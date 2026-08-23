# InformalSavings `policy.py` ↔ `num_pee*.tex` — reconciliation record

**Status: reconciled 2026-08-11** — items 1–8 with the `policy.py` implementation, items 9–10 with the
path solve, items 11–14 with the calibration. `num_calibration.tex` has been updated for 11–14. This file
is the record of what moved and the measurements behind it, so the numbers do not have to be re-derived if
either side is revisited. Everything here is reproduced by `python/InformalSavings/test_peeLOG.py` /
`test_peeCRRA.py` / `test_peePath.py` / `test_calibration.py` / `test_calibrationGrid.py` and
`python/gridsearch/test_interp.py`, on the Argentina calibration.

Items 1–9 and 11–14 are cases where the **code deviated from the doc and the doc was (or must be)
corrected**. Item 10 is the one case so far in the other direction: the doc was right and the code was
changed to match it.

**Items 13–14 partly overturn 11–12** and are the more important pair: item 11's step-size conclusion is
LOG-only, and item 12's "the inner grid is at fault" is at most half the story — the *kind* of
continuation interpolant matters more. Read 11–12 only together with 13–14.

Each item lists where the code implements it and where the doc now states it.

---

## 1. Numerical derivatives are taken in `x = ln(1-τ_t)`, not in `τ_t`

*Code*: `policy.py` `LOG._gradProfile` (CRRA inherits it). *Doc*: `num_peeLOG.tex`, new subsection "The
coordinate the numerical derivatives are taken in"; `num_peeCRRA.tex` "Which derivatives may be taken on
the grid" now refers to it.

Every profile carries a `ln(1-τ_t)` term through `Θ_{h,t} ∝ ((1-α)(1-τ_t))^{ξ/(1+αξ)}`, so `dy/dτ`
diverges like `1/(1-τ_t)`. Measured against the closed form available when the continuation policy is held
fixed:

| coordinate | max rel. error near `u` | interior |
|---|---|---|
| `τ` | 9e-1 | 2e-2 |
| `ln(1-τ)` | 1e-15 | 1e-15 |

## 2. Candidate grids: align `𝒮_0'`, refine `𝒮'` — the two roots fail differently

*Code*: `CRRA.defaultSCandGrid` (4× geometric `𝒮'`); `𝒮_0'` defaults to `𝒮_0` in both `solveBackward`s.
*Doc*: `num_peeLOG.tex` Grids ¶ (the `ι` side, with the mechanism), `num_peeCRRA.tex` Grids ¶ (the contrast).

**This was initially written up with the wrong mechanism** — as "the residual is piecewise linear in `ι_t`"
— and corrected after isolating it. The residual is *not* piecewise linear; the real point is that it has
no curvature of its own worth speaking of, because `ι_t` reaches it **only** through the continuation
interpolants, whose breakpoints sit at `𝒮_0`'s nodes. A candidate cell that *straddles* a breakpoint is one
the locating secant cannot represent, and refining without aligning creates such cells rather than removing
them. Hence the error is non-monotone in the number of candidate nodes:

| `𝒮_0'` (relative error in the located `ι_t`) | k=1 | k=2 | k=4 | k=8 |
|---|---|---|---|---|
| superset of `𝒮_0` | 2.3e-7 | 5.4e-8 | 1.4e-8 | 3.5e-9 |
| non-aligned, same size | 2.3e-7 | 1.9e-5 | 1.8e-5 | 3.5e-7 |

The `s` root is the opposite case: `B_{t+1}(s_t,h_{t+1})` is genuinely nonlinear in `s_t` and swamps the
same kinks, so alignment is irrelevant (superset and non-aligned agree within 20% at every size) and
refinement pays. Relative error in the located `s_t` across the state grid: **2.3e-2** at `𝒮'=𝒮`,
**4.5e-4** at 4× uniform, **7.2e-5** at 4× geometric — geometric because `s_t` spans a factor of ~20 while
a uniform `𝒮'` puts constant-width cells at the bottom of that range.

## 3. Smoothing: the policy, not the derivative — and clip it

*Code*: `sGrad = 0.0` defaults; `smooth = 1e-5` retained for `τ_t(·)`; clip in `LOG.solveBackward_t` and
`CRRA._smooth2D`. *Doc*: `num_peeLOG.tex` alg step 4; `num_peeCRRA.tex` "Numerical stability".

A smoothing budget of 1e-6 (in units of the profile's own variance) on the *differentiation* spline is
3–10× worse than an interpolating one: after change 1 there is nothing left to denoise. Separately, a
smoother run through a policy that is flat at a corner over part of the state grid undershoots it, and the
reported `τ_t` leaves `[l,u]` by ~1e-3 unless clipped.

Implementation detail with no doc counterpart: the budget is applied **per column, scale-free** (each
profile normalised by its own standard deviation), since `UnivariateSpline`'s `s` is an absolute bound.

**Superseded in part, 2026-08-19 (item 15).** The *policy* smoothing survives; how its knots are chosen
does not. `smoothKnots` now pins them, and the smoothing budget `s` is unused on that branch.

## 4. `𝒮_0` bounds: cap above, pad generously below, space logarithmically

**Superseded 2026-08-19 — see item 16.** Both bounds are now multiples of `min_τ ι*(τ)` and `capι` is an
inert backstop. The reasoning below is kept because it is what item 16 had to overturn, and because its
"below" bullet names a failure mode that must not be reintroduced by padding further.

*Code (until 2026-08-19)*: `LOG.defaultIotaGrid` (`capι = 2.0`, `padι = (0.25, 1.25)`, `spacingι = 'log'`).
*Doc*: `num_peeLOG.tex` Grids ¶, rewritten with both reasons and the display of the bound formula.

- **Above**: `ι*(τ) → ∞` as `τ→1` because the *denominator* (formal savings) collapses. Uncapped the rule
  gives `u_ι ≈ 8.6e3` while paths live at `ι ≈ 0.1`.
- **Below**: the steady-state range *understates* `ι_t`'s dynamic range — 0.031 against a steady-state
  minimum of 0.094. With the doc's old 0.75 factor, 29 of 101 nodes of `𝒯` are infeasible for a purely
  numerical reason and the selection is pinned to the feasibility edge at most states (188 corner
  selections of 450, against 71 with 0.25). The solved path is unchanged to three decimals either way,
  which is what identifies it as a grid artefact.

## 5. `ρ=1` is refused by the recursion, not by the terminal solve

*Code*: `CRRA.solveBackward`/`solveBackward_t` guard; `CRRA.solveTerminal` deliberately does not.
*Doc*: `num_peeCRRA.tex` "Numerical stability", first bullet.

The terminal period never forms `ĉ_1`, so at `ρ=1` it coincides *exactly* with `LOG.solveTerminal`
(state-independent in `s_{T-1}`, equal to 5.6e-17). That identity is the sharpest test of the CRRA class.

## 6. Step 4 of the CRRA algorithm is the memory bottleneck

*Code*: `CRRA._iotaOfTauS`'s `chunk` argument. *Doc*: `num_peeCRRA.tex` "Numerical stability" (new bullet)
and the closing remark of `alg:CRRA:grid`.

Its largest intermediate is `|𝒮|·|𝒮_0|·|𝒮'|·|𝒮_0'|` — the one object scaling with all four grids at once,
so it grows as the fourth power of a uniform refinement. The algorithm's "cost is calls, not gridpoints"
remark holds for steps 1–3 only.

## 7. Feasibility condition 3 is tested on all four levels

*Code*: `CRRA._positiveLevels`. *Doc*: `num_peeCRRA.tex` feasibility item 3, closing sentence. The doc's
argument that only `c_{2,t}^i` can fail is retained; testing all four is cheaper than relying on it and
catches a fractional power of a negative base at its source.

## 8. Accuracy statements now in the docs

- LOG `t<T`: `z_t` is accurate to ~1e-3 *absolute*, floored by the continuation interpolant's kinks
  (cubic interpolation halves it and leaves the candidate ranking unchanged). That displaces the located
  tax by ~4e-4, a small fraction of a `𝒯` cell — the grid, not the differentiation, is the binding
  constraint. Stated at the end of `num_peeLOG.tex`'s new coordinate subsection.
- Both cases: `z_T` matches a finite difference of the political objective rebuilt from the **primitives**
  to machine precision.

## 9. The initial fixed point is a grid scan, not a bracketed root

*Code*: `model.py`'s `initialStatePEE`. *Doc*: `num_peePath.tex`, new subsection "The bracket is
guaranteed, and that is the problem". The doc previously called `eq:initialFixedPoint` "a scalar problem"
with "clean, known bounds `[l,u]`" — which reads as, and was first implemented as, one `brentq` on
`[l,u]`.

That implementation returns the wrong root. The residual is `τ - clip(τ¹(·), l, u)`, and the clip is what
makes `[l,u]` a guaranteed bracket — but it also creates an *exact* root at whichever end the extrapolated
policy overshoots. At `τ = u` the steady state degenerates (formal savings collapse, so `ι_0 = s_0^0/s_0`
diverges) and the state is far outside the grids the policy functions were solved on, so `τ¹` is
extrapolating there. On the Argentina calibration:

| | `ι_0(u)` | `𝒮_0` upper | extrapolated `τ¹` | residual at `u` |
|---|---|---|---|---|
| CRRA (`ρ=1.15`) | 5.5e3 | 2.0 | **8.32** → clips to `u` | **0** |
| LOG (`ρ=1`) | 6.9e3 | 2.0 | −0.70 → clips to `l` | 0.9998 |

`brentq` accepts a bracket whose endpoint value is zero and returns that endpoint, so the CRRA path
started from `s_0 = 2e-11`, `ι_0 = 5.5e3` and every subsequent state was extrapolated. **Which way this
falls is luck** — the two cases differ only in the sign of the extrapolation, and the LOG case happened to
be fine. A `[l,u]` bracket is therefore not safe here even though it is guaranteed.

What the code does instead: evaluate the residual on `𝒯`, return `NaN` wherever the implied `(s_0,ι_0)`
leaves the state grids (so the extrapolated region cannot produce a root at all), take the lowest sign
change among the surviving nodes, and `brentq` inside that one cell. Multiplicity is reported (`nRoots`)
rather than silently resolved. On this calibration the masked residual is monotone with a single crossing:
`τ_1 = 0.1453` (LOG), `0.1534` (CRRA).

*Generalisable point, and the reason this is worth a doc paragraph rather than a code comment*: a clip that
manufactures a bracket also manufactures a root. Every bounded policy function in this project is clipped
the same way, so the same trap is available anywhere a fixed point is closed through one.

## 10. The forward walk re-solves the state transitions — *the code moved, not the doc*

*Code*: `LOG.approximatePEE` / `CRRA.approximatePEE`, `exact = True` (default). *Doc*: `num_peePath.tex`
"Forward simulation", expanded to say that `eq:forwardSim` is meant literally; `num_peeLOG.tex` /
`num_peeCRRA.tex` step 4 now note that the state interpolants exist only for the cheaper variant.

`eq:forwardSim` writes the transitions as functions of the tax — `ι_t(τ_t)` (log), `s_t(τ_t,s_{t-1})` then
`ι_t(τ_t,s_t)` (CRRA). The first implementation instead read them off the `sPolicy`/`ιPolicy` interpolants
that `report_t` builds over the *predetermined* state. The two agree at the nodes of `𝒮`/`𝒮_0` and differ
between them, so this was an interpolation of a composition the doc's version evaluates directly.

Measured against the exact re-solve, maximum absolute discrepancy over the path:

| | re-solved | interpolated |
|---|---|---|
| LOG `ι` | 1.2e-8 | 4.7e-6 |
| CRRA `s` | 1.1e-7 | 6.6e-6 |
| CRRA `ι` | 4.7e-7 | 9.9e-6 |

Two orders of magnitude for one scalar root per **period** — against the one per **node** the backward
recursion has already paid, so the cost is not measurable in the solve as a whole. Under LOG there is a
second reason beyond accuracy: `ι_t` is a function of `τ_t` alone (result 1 of the README's list), and
interpolating `ι_t` over `ι_{t-1}` discards exactly that. The interpolated walk is kept as `exact=False`,
which is what produces the table above.

*Generalisable point*: the deviations in items 1–9 were all numerical folklore in the docs failing on
contact. This one is the opposite — a derivation in the doc that the implementation quietly weakened,
because interpolating something already computed looks like reuse rather than approximation. Worth
checking for specifically when a later section consumes an earlier section's output.

## 11. The outer finite-difference step: the doc's predicted failure does not occur

*Code*: `model.py` `calibrate` (scipy `hybr` at its default step; no `options={'eps': …}`).
*Doc*: `num_calibration.tex`, "The outer residual is only piecewise smooth" — **needs correcting**.
*Test*: `test_calibration.py` §5.

The doc predicts that the outer Jacobian's step "must be large enough that the induced movement of the
state clears a grid cell", and that a `√(machine eps)` step "will be far below that and will return
noise". Measured at the converged LOG point, the difference quotient is *flat* across six orders of
magnitude of step size, and it is the **large** steps that misbehave:

| step `h` | 1e-9 | 1.49e-8 (`hybr` default) | 1e-5 | 1e-3 | 1e-2 |
|---|---|---|---|---|---|
| `d(res_τ)/d(x_β)` | −0.1352 | −0.1352 | −0.1352 | −0.1096 | −0.1287 |
| `d(res_τ)/d(x_ω)` | +0.3698 | +0.3698 | +0.3697 | +0.3826 | +0.3837 |

Agreement between `h=1e-9` and the default step is 9e-5 relative or better on all four columns. The
mechanism the doc missed is in its own text one paragraph earlier: `τ_t` is located by interpolation
*inside* a cell of `𝒯`, and the policy interpolants are piecewise linear in the state, so a small step
stays on **one linear piece** and returns that piece's slope — which is exactly what Newton wants. A large
step averages across kinks and is *less* accurate. The hazard is real but intermittent (a step straddling
a kink, an `argmax` switching), not a systematic noise floor, and the remedy the doc prescribes makes it
worse. The LOG calibration converges from `test.py`'s starting parameters in 26 evaluations to 2e-10 at
the default step.

## 12. The CRRA calibration needs a finer inner grid than the PEE solve — item 11's hazard, relocated

> **Superseded in part by item 17 (2026-08-19).** The grid size is retained; the *reason* below — a
> displaced root at `30×30` — no longer reproduces once the residual is continuous. Kept because the
> measurements are the baseline item 17 is read against.

*Code*: not defaulted — `CRRA.initGS({'nι': 45, 'ns': 45})` before `calibrate`.
*Doc*: `num_calibration.tex` "Order of work, and a check" — **needs a paragraph**.
*Test*: `test_calibration.py` §8.

Item 11 clears the doc's worry for LOG; for CRRA the same worry is justified, but the object at fault is
the **grid**, not the step. At the PEE default `30×30` the outer root converges (scipy reports success) to
a *displaced* point. Holding those parameters fixed and refining only the inner grid:

| grid `(nι, ns, nsCandMult)` | (30,30,4) | (30,30,8) | (45,45,4) | (60,60,4) | (60,60,8) |
|---|---|---|---|---|---|
| max abs. outer residual | 6.6e-4 | 7.6e-4 | 3.13e-3 | 3.14e-3 | 3.14e-3 |

A **plateau**, not a decay — the refined problem is well resolved and its root is simply somewhere else,
so `30×30`'s answer is wrong rather than imprecise. Calibrating at `45×45` gives the healthy pattern:

| evaluated at | 45×45 (its own) | 60×60 | 75×75 |
|---|---|---|---|
| max abs. outer residual | 1.0e-12 | 1.0e-4 | 4.4e-5 |

Decreasing, so the answer is grid-converged to ~1e-4. The LOG side needs no such treatment: at its
default `nι=50` the residual under refinement already shrinks (3.1e-4 at 75, 6.6e-5 at 100).

The two grids are *not* unified into one default deliberately: `30×30` is what `test_peeCRRA.py` and
`test_peePath.py` assert their grid-spacing tolerances against, and the PEE solve itself is unaffected —
it is the outer root's sensitivity to a displaced inner solution that needs the resolution. Raising the
default would be a separate, test-affecting change.

*Generalisable point*: "scipy reports success" and "the residual is small" were both true at the wrong
answer. What distinguished it was refining the thing the residual is computed *through* and watching
whether the number decays or plateaus — a test that costs one extra evaluation and that no tolerance on
the outer solve could have replaced.

---

## 13. The outer finite-difference step, revisited: item 11 does not carry over to CRRA

> **Retracted by item 17 (2026-08-19).** The corrupted `η0` column below was the adaptive smoother's
> residual jumps being straddled at that step, not a property of the CRRA residual. `_calOuterKwargs` is
> now empty and item 11's rule covers both preference cases. Kept for the measurement and the reasoning.

*Code*: `model.py` `_calOuterKwargs` (applied in `calibrate`). *Doc*: `num_calibration.tex`, "The outer
residual is only piecewise smooth", now split by preference case.

Item 11 measured the outer Jacobian **at the converged LOG calibration** and found the difference quotient
flat from `h=1e-9` to `1e-5`, concluding that scipy's default `sqrt(eps)` step is correct and that the
doc's original "clear a grid cell" prescription was harmful. That measurement stands *for LOG*. It does
**not** generalise: measured at `ρ=1.1`, `45×45`, from the LOG parameters, the columns are

| step `h` | 1.49e-8 (default) | 1e-6 | 1e-5 | 1e-4 | 1e-3 | 1e-2 |
|---|---|---|---|---|---|---|
| `β` | 0.132 | 0.132 | 0.131 | 0.138 | 0.137 | 0.136 |
| `ω` | 0.386 | 0.451 | 0.350 | 0.398 | 0.387 | 0.399 |
| **`η0`** | **5.126** | 0.551 | 0.905 | **0.988** | **0.999** | 0.916 |
| `X0` | 0.996 | 0.996 | 0.996 | 0.997 | 0.992 | 0.990 |

`β` and `X0` are stable at every step; `ω` wobbles ±13%; `η0` is **5× its resolved value at the default
step**. One corrupted column is enough to derail the Newton direction — the search then cycles for 60+
evaluations without converging. `_calOuterKwargs` therefore sets `options={'eps': 1e-4}` for CRRA only
(hybr scales it as `sqrt(eps)·|x|`, so the effective step is `1e-2·|x|`), and leaves LOG at scipy's
default, which is what item 11 and `test_calibration.py` §5 pin.

*Generalisable point*: a step-size measurement taken at one converged point of one preference case is not
a property of the residual. Both conclusions are correct in their own regime, and the doc now says so.

---

## 14. Piecewise-linear continuation interpolants are what actually breaks the CRRA calibration

*Code*: `gridsearch/interp.py` (`kind` argument, NaN handling), `policy.py` `_gridSettings['interpKind']`.
*Doc*: `num_calibration.tex`, "Where the hazard does bite".

Item 12 attributed the CRRA calibration's trouble to the resolution of the inner state grids. That is at
most half of it. The deeper cause is the *kind* of interpolant: `τ^t(·,·)` piecewise linear in the state
makes the outer residual surface only piecewise `C¹`, and Newton cannot descend it. Measured at `ρ=1.1`,
`45×45`, with the item-13 step:

| `interpKind` | outer solve | residual at the converged `x`, `45 / 60 / 75` |
|---|---|---|
| `linear` | **never converges** — stalls ~3e-5 after 60+ evaluations | 3.27e-5 → 1.52e-4 → 2.93e-4 — **growing** |
| `cubic` | **1.33e-11 in 12 evaluations** | 1.33e-11 → 1.69e-4 → 5.06e-5 — **shrinking** |

So `linear` is not grid-converged at `ρ=1.1` (the refinement trend is the wrong sign — item 12's own
diagnostic, failing), while `cubic` shows the decaying pattern item 12 calls healthy. The calibrated
parameters differ by only 0.016% in `β` and 0.11% in `ω`, so `linear` was **not badly displaced** — it
simply could not drive the residual down. `interpKind='cubic'` is now required for the CRRA calibration,
recorded per point in the grid settings rather than fixed at the call sites.

**`pchip` is the theoretically right choice and is not usable at present.** It is monotone and `C¹`, so
unlike `cubic` it cannot overshoot a policy that is flat at a bound (measured on a cornered profile:
`cubic` returns `[-0.088, 3.105]` on data spanning `[0, 3]`; `pchip` stays inside). But
`scipy.interpolate.RegularGridInterpolator` rebuilds its pchip splines **on every call**, giving 844 ms
per 3 600-point evaluation against 0.59 ms for `linear` and 1.02 ms for `cubic` — a 1400× penalty that
takes a CRRA solve from 5.7 s to over 10 min. Using it would need a precomputed bicubic-Hermite
evaluator. Until then `cubic`'s overshoot is unguarded on `h`/`s`/`ι`/`Γs` (`τ` is clipped already, item 3).

Two NaN traps were fixed to make any non-linear kind usable at all, both in `gridsearch/interp.py`:
1. A policy surface carries NaN at infeasible nodes and the spline methods refuse to be **constructed**
   over them. Invalid nodes are filled from their nearest valid neighbour for the fit and masked back to
   NaN on evaluation, reproducing `linear`'s NaN propagation exactly (verified off-node against `linear`).
   The mask is load-bearing: `approximatePEE`'s `strict` check relies on a path through an infeasible cell
   going non-finite *without* leaving the rectangle.
2. `RegularGridInterpolator` builds spline methods **lazily, per axis, at call time**, so a non-finite
   *evaluation coordinate* makes axis 0 return NaN and axis 1 then raises while building a spline over it.
   `linear` tolerates NaN coordinates for free; the spline kinds need an explicit guard.

One caveat on the masking: `interp1d`/`RGI` assign a point sitting exactly on a node to the left-hand
interval, so a *valid* node bordering an invalid cell reads the NaN and returns NaN. The masked kinds
return the node's own value there instead. That is a lookup artifact rather than a semantic difference,
and `test_interp.py` states it explicitly rather than inheriting it.

## 15. The policy smoother's knots must be pinned, not chosen from the data

*Code*: `gridsearch.interp.griddedSmooth1D(..., knots)`; `smoothKnots` in `_gridSettings`, threaded into
`LOG.solveBackward_t` and `CRRA._smooth2D`. *Doc*: **updated 2026-08-19** — `num_peeLOG.tex` alg step 4 now states the requirement and why
(a smoother that selects its own knot count puts a discrete choice inside a function the calibration
differentiates); `num_peeCRRA.tex` "Numerical stability" cross-references it. Not a deviation any more.

`UnivariateSpline(s=…)` lets FITPACK choose the knot COUNT from the data. That integer flips as a model
parameter moves, putting ~3.5e-6 discontinuities in the calibration's outer residual — the size of the
`ρ≈0.7` plateau, and the reason no warm start could close it. `LSQUnivariateSpline` with knots at every
`m`-th valid node makes the smoother a linear map of its input (hence continuous in the parameters), is
~2.4× faster, and satisfies Schoenberg–Whitney per column even where the column carries NaNs.

**Default flipped `None` → `4` on 2026-08-19**, after `test_calibration.py` §8 was found to have spent a
session failing precisely because it reached the adaptive branch by default (item 17's addendum). The
bitwise-reproducibility argument for `None` had expired — every result it protected is superseded, and
every calibration path was already overriding it. Note the trap the flip creates: `initGS` merges over the
defaults, so an explicit `smoothKnots=None` now *disables* pinned knots. Two callers were inverted by it in
opposite directions and both are now explicit; a caller with nothing to say must omit the key.

Full diagnosis, including the four measurements that located it and the two provocations that do *not*
find it: `notes/informalSavings_rho07_resolved.md`. Transferable form: `crossCuttingFindings.md` #5.

## 16. Both `𝒮_0` bounds anchor on `min_τ ι*(τ)`; `𝒮` anchors on `s*(0.3)`

*Code*: `padι = (0.45, 3.7)`, `pads = (0.45, 3.65)`, `sAnchorτ = 0.3`; `capι = 2.0` retained as a backstop.
*Doc*: **updated 2026-08-19** — `num_peeLOG.tex` Grids ¶ carries the new bound formula, the argument for
anchoring on the minimum, and the caution that corner selections rather than feasible-node counts are the
quantity to watch; `num_peeCRRA.tex` Grids ¶ carries the `s^*(0)` anti-correlation and the interior anchor.
Not a deviation any more.

Supersedes item 4. Anchoring the `ι` top on `max_τ ι*(τ)` gave the rule no finite content (`ι*` diverges
to 25 484 at `τ=0.9999`), so the operative bound was the absolute `capι` — a constant that would not
survive a change of data. Measured across `ρ ∈ [0.5, 2.0]` and under LOG, `min_τ ι*(τ)` is constant to
0.045% and the reachable set sits at `0.539–0.557×` / `2.89–3.07×` it. For `𝒮`, `s*(0)` is *perfectly*
anti-correlated with the reachable upper edge (−1.000), so no constant pad on it can track; `s*(τ_0)`
drifts 77%; `s*(0.3)` is `ρ`-stable to 1.5% while still moving with the calibrated data.

Occupancy 49–52% → 78–80% (`ι`) and 40%/80% → 62%/76% (`s`); `verifyResidual` across `ρ ∈ [0.7, 0.9]`
fell to a flat 3.3–4.5e-5 from a rising 1.2–3.1e-4. Item 4's "below" bullet still binds: `l_ι` is 0.137
here, below the 0.228 that caused its documented feasibility failure, and corner selections *fell*. Do not
raise `padι[0]` further without re-measuring `atBound`.

---

## 17. The outer step and the inner grid, re-measured after `smoothKnots`: item 13 retracted, item 12 halved

*Code*: `model.py` `_calOuterKwargs` is now **empty**; `nι=ns=45` **retained** for the CRRA calibration.
*Doc*: `num_calibration.tex`, "The outer residual is only piecewise smooth" — the LOG/CRRA split it
carries per item 13 **should be removed**; the one rule (scipy's default step) now covers both.
*Test*: `test_calibrationGrid.py` (`_calOuterKwargs == {}`).
*Script*: `measureOuterSettings.py` (`--test jac|eps|grid`).

Items 12 and 13 were both established against a residual that had ~3.5e-6 jumps in it (item 15), and both
are defences against symptoms that could have been the jumps rather than the causes they were attributed
to. Re-measured at the converged `ρ=0.7` and `ρ=0.9` points of the retuned partial sweep, at
`interpKind='cubic'`, `smoothKnots=4` and the item-16 grid rule.

**The step: item 13 does not survive.** Its whole content was one corrupted Jacobian column (`η0` at 5.13
against a resolved 0.99 at scipy's default step). That column is now flat:

| ‖column‖ rel. to `h=1e-4` | 1.49e-8 | 1e-6 | 1e-5 | 1e-4 | 1e-3 | 1e-2 |
|---|---|---|---|---|---|---|
| `η0`, `ρ=0.9` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9995 | 0.9952 |
| `η0`, `ρ=0.7` | 1.0001 | 1.0000 | 1.0000 | 1.0000 | 0.9996 | 0.9956 |

Flat to 0.01% over four orders of magnitude, and only the *largest* step loses anything — which is item
11's LOG finding, now holding for CRRA as well. Calibrating from a common start (the `ρ=1` LOG anchor's
`x`) confirms it decides nothing:

| | scipy default | `eps=1e-4` | `eps=1e-3` |
|---|---|---|---|
| `ρ=0.9` | 12 nfev, **3.57e-12** | 12 nfev, 3.90e-12 | 12 nfev, 6.95e-12 |
| `ρ=0.7` | 14 nfev, **8.60e-12** | 14 nfev, 8.62e-12 | 13 nfev, 2.82e-10 |

Same evaluation count, same parameters to 3.7e-10, and scipy's default reaches the tightest residual of
the three. `eps=1e-3` — which `rho07_resolved.md` recommended adopting "on its own merits" — is in fact
marginally *worse*, so the override is removed rather than retuned. Items 11 and 13 collapse into one
rule, and the doc's split by preference case should go with them.

**The grid: item 12's mechanism is gone, its conclusion survives on much weaker grounds.** Item 12
established `45×45` because `30×30` converged to a *displaced* root — `β` off by ~1%, and the ladder
(refining at fixed parameters) plateauing at 3.1e-3. Neither symptom reproduces:

| ρ | n | nfev | time | Δpar vs 45×45 | ladder off its own grid |
|---|---|---|---|---|---|
| 0.9 | 30 | 12 | **102 s** | 1.5e-4 | 1.1e-5 … 4.3e-5 |
| 0.9 | 45 | 12 | 439 s | — | 1.1e-5 … 3.3e-5 |
| 0.9 | 60 | 12 | 1184 s | 9.4e-5 | 2.2e-5 … 3.3e-5 |
| 0.7 | 30 | 14 | **119 s** | 3.8e-4 | 7.1e-5 … 1.1e-4 |
| 0.7 | 45 | 14 | 432 s | — | 2.3e-5 … 4.0e-5 |
| 0.7 | 60 | 14 | 1201 s | 1.0e-4 | 1.8e-5 … 4.2e-5 |

The displacement is down from ~1% to 1.5–3.8e-4, i.e. *smaller than the two solver changes made the same
day* (the grid retune moved the LOG anchor 0.047%/0.071%, pinned knots a further 0.057%/0.32%). So item
12's diagnosis — "`30×30`'s answer is wrong rather than imprecise" — was itself a reading of the
discontinuity, the same misattribution the `ρ=0.7` pocket produced.

What survives is a genuine but modest resolution effect, and only at the hard end of the `ρ` range: at
`ρ=0.7` the `n=30` rungs run a consistent 2–3× above `n=45`'s, where at `ρ=0.9` the two are
indistinguishable. `n=60` buys nothing over `n=45` on either (same rung level; its parameters differ from
`n=45`'s by 1.0e-4, the same order as the spread among all three), so **~1e-4 in the parameters is the
outer answer's floor and refining past 45 does not penetrate it** — which is also the number `calibrate`'s
`tol` should be read against.

A third point, added when `test_calibration.py` §8 was brought onto these settings: at `ρ=1.02`, holding
the smoother and interpolant fixed and varying *only* the grid, `30×30` is **1.2×** `60×60` — against 1.0×
at `ρ=0.9` and 2–3× at `ρ=0.7`. The resolution effect therefore grows monotonically with distance from
`ρ=1`, which is the sharpest available statement of what the finer grid buys. (§8's own earlier 2.8×
compared `initGS()` with no argument against `45×45`, which resets `interpKind` and `smoothKnots` as well
— three things varying at once, and most of that gap was the smoother, not the grid.)

`45×45` is therefore **kept**, but for a different reason than item 12 gave, and a weaker one: not
"`30×30` is wrong" but "`30×30` is ~3× coarser at `ρ=0.7`, and the sweep runs to `ρ=0.5`, further into the
region where that gap opened." The 4× cost saving is real (roughly 90 min against 6 h for a 16-point
sweep) and is what should be re-examined first if the sweep budget ever binds — the evidence against
`30×30` is now a factor of three on a 1e-4 quantity, not a correctness argument.

*Generalisable point*: two settings adopted as defences against one undiagnosed defect will both look
justified for as long as the defect is present, and neither measurement is wrong at the time it is taken.
When the defect is finally found, every such setting has to be re-derived rather than inherited — and they
will not all fall the same way. One was removed here; the other was kept with its justification rewritten.

---

## Left in the code, with no doc counterpart (by design)

- `base.py`'s `lnRleadΘ` reads `α` and `power_h` at `t` though both are `t+1` objects exactly. Follows
  `Rlead`'s existing convention; immaterial unless `α`/`ξ` vary over `t`.
- `gridsearch.griddedInterp2D` — extrapolating, evaluated on paired coordinates — added for the CRRA
  continuation surfaces; `kind`/NaN handling added with item 14.
- `gridsearch/continuation.py` (`marchGrid`) — the anchored parameter march used by `model.py`'s
  `calibrateGrid`. Purely numerical scaffolding for solving a *sequence* of calibrations; it has no
  counterpart in the docs because it changes no equation.
