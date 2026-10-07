# InformalSavings `policy.py` ↔ `num_*.tex` — reconciliation record

Where the code departs from the docs, what the doc now says, and the measurement behind each. Kept so the
numbers do not have to be re-derived if either side is revisited; everything here is reproduced by the
module's test suites and `gridsearch/test_interp.py`, on the Argentina calibration.

**Renumbered 2026-08-24** into current state: the retracted and superseded items (old 4, 13, and the
original readings of 11/12) were folded into the items that replaced them. Old numbering is at
`c958031^`. Old → new: 1–3 unchanged, 4→4 (rewritten), 5–10 unchanged, 11+13+17(step)→11,
12+17(grid)→12, 14→13, 15→3, 16→4.

---

## 1. Numerical derivatives are taken in `x = ln(1-τ_t)`, not in `τ_t`

*Code*: `policy.py` `LOG._gradProfile` (CRRA inherits). *Doc*: `num_peeLOG.tex`, "The coordinate the
numerical derivatives are taken in".

Every profile carries a `ln(1-τ_t)` term through `Θ_{h,t} ∝ ((1-α)(1-τ_t))^{ξ/(1+αξ)}`, so `dy/dτ`
diverges like `1/(1-τ_t)`. Against the closed form available when the continuation policy is held fixed:

| coordinate | max rel. error near `u` | interior |
|---|---|---|
| `τ` | 9e-1 | 2e-2 |
| `ln(1-τ)` | 1e-15 | 1e-15 |

## 2. Candidate grids: align `𝒮_0'`, refine `𝒮'` — the two roots fail differently

*Code*: `CRRA.defaultSCandGrid` (4× geometric `𝒮'`); `𝒮_0'` defaults to `𝒮_0`. *Doc*: `num_peeLOG.tex` /
`num_peeCRRA.tex` Grids ¶.

`ι_t` reaches the residual **only** through the continuation interpolants, whose breakpoints sit at
`𝒮_0`'s nodes, so a candidate cell that *straddles* a breakpoint is one the locating secant cannot
represent. Refining without aligning creates such cells rather than removing them, and the error is
non-monotone in the candidate count:

| `𝒮_0'` (rel. error in located `ι_t`) | k=1 | k=2 | k=4 | k=8 |
|---|---|---|---|---|
| superset of `𝒮_0` | 2.3e-7 | 5.4e-8 | 1.4e-8 | 3.5e-9 |
| non-aligned, same size | 2.3e-7 | 1.9e-5 | 1.8e-5 | 3.5e-7 |

The `s` root is the opposite case: `B_{t+1}(s_t,h_{t+1})` is genuinely nonlinear in `s_t` and swamps the
same kinks, so alignment is irrelevant and refinement pays — 2.3e-2 at `𝒮'=𝒮`, 4.5e-4 at 4× uniform,
7.2e-5 at 4× geometric (geometric because `s_t` spans a factor of ~20).

## 3. Smoothing: the policy, not the derivative; clip it; pin the knots

*Code*: `sGrad = 0.0`; smoothing retained for `τ_t(·)` with `smoothKnots` (default **4**), threaded into
`LOG.solveBackward_t` and `CRRA._smooth2D`; clip in both. *Doc*: `num_peeLOG.tex` alg step 4;
`num_peeCRRA.tex` "Numerical stability". Not a deviation any more.

Three separate facts:
- A smoothing budget on the *differentiation* spline is 3–10× worse than an interpolating one — after item
  1 there is nothing left to denoise.
- A smoother run through a policy that is flat at a corner undershoots it, and the reported `τ_t` leaves
  `[l,u]` by ~1e-3 unless clipped.
- **The knot count must be pinned.** `UnivariateSpline(s=…)` lets FITPACK choose it from the data; that
  integer flips as a parameter moves, putting ~3.5e-6 discontinuities in the calibration's outer residual
  and making one `ρ` uncalibratable. `LSQUnivariateSpline` with knots at every `m`-th valid node makes the
  smoother a linear map of its input, is ~2.4× faster, and satisfies Schoenberg–Whitney per column even
  where the column carries NaNs. Full diagnosis: `notes/informalSavings_resolvedIssues.md` §1;
  transferable form: `crossCuttingFindings.md` #5.

**The trap the default flip created**: `initGS` merges over the defaults, so an explicit
`smoothKnots=None` now *disables* pinned knots. A caller with nothing to say must omit the key.

## 4. Both `𝒮_0` bounds anchor on `min_τ ι*(τ)`; `𝒮` anchors on `s*(0.3)`

*Code*: `padι = (0.45, 3.7)`, `pads = (0.45, 3.65)`, `sAnchorτ = 0.3`; `capι = 2.0` as an inert backstop.
*Doc*: `num_peeLOG.tex` / `num_peeCRRA.tex` Grids ¶. Not a deviation any more.

Anchoring the `ι` top on `max_τ ι*(τ)` gave the rule no finite content — `ι*` diverges to 25 484 at
τ=0.9999 because the *denominator* (formal savings) collapses — so the operative bound was the absolute
`capι`, a constant that would not survive a change of data. Measured across ρ ∈ [0.5, 2.0] under LOG,
`min_τ ι*(τ)` is constant to 0.045% and the reachable set sits at 0.539–0.557× / 2.89–3.07× it. For `𝒮`,
`s*(0)` is *perfectly* anti-correlated with the reachable upper edge (−1.000), so no constant pad on it
can track; `s*(0.3)` is ρ-stable to 1.5% while still moving with the calibrated data. Occupancy 49–52% →
78–80% (`ι`) and 40%/80% → 62%/76% (`s`).

**The lower bound still binds and must not be padded further without re-measuring `atBound`.** The
steady-state range understates `ι_t`'s dynamic range (0.031 against a steady-state minimum of 0.094). At
the doc's old 0.75 factor, `l_ι = 0.228` left 29 of 101 `𝒯` nodes infeasible for a purely numerical reason
and pinned the selection to the feasibility edge at most states (188 corner selections of 450). `l_ι` is
0.137 here and corner selections *fell*. Watch corner selections, not feasible-node counts.

## 5. `ρ=1` is refused by the recursion, not by the terminal solve

*Code*: `CRRA.solveBackward`/`solveBackward_t` guard; `CRRA.solveTerminal` deliberately does not.
*Doc*: `num_peeCRRA.tex` "Numerical stability".

The terminal period never forms `ĉ_1`, so at `ρ=1` it coincides *exactly* with `LOG.solveTerminal`
(equal to 5.6e-17). That identity is the sharpest test of the CRRA class.

## 6. Step 4 of the CRRA algorithm is the memory bottleneck

*Code*: `CRRA._iotaOfTauS`'s `chunk`. *Doc*: `num_peeCRRA.tex` "Numerical stability", `alg:CRRA:grid`.

Its largest intermediate is `|𝒮|·|𝒮_0|·|𝒮'|·|𝒮_0'|` — the one object scaling with all four grids at once,
so it grows as the fourth power of a uniform refinement. The algorithm's "cost is calls, not gridpoints"
remark holds for steps 1–3 only.

## 7. Feasibility condition 3 is tested on all four levels

*Code*: `CRRA._positiveLevels`. *Doc*: `num_peeCRRA.tex` feasibility item 3. The doc's argument that only
`c_{2,t}^i` can fail is retained; testing all four is cheaper than relying on it and catches a fractional
power of a negative base at its source.

## 8. Accuracy statements now in the docs

LOG `t<T`: `z_t` is accurate to ~1e-3 *absolute*, floored by the continuation interpolant's kinks, which
displaces the located tax by ~4e-4 — a small fraction of a `𝒯` cell, so the grid rather than the
differentiation is binding. Both cases: `z_T` matches a finite difference of the political objective
rebuilt from the **primitives** to machine precision.

## 9. The initial fixed point is a grid scan, not a bracketed root

*Code*: `model.py` `initialStatePEE`. *Doc*: `num_peePath.tex`, "The bracket is guaranteed, and that is
the problem". The doc previously called `eq:initialFixedPoint` "a scalar problem" with "clean, known
bounds `[l,u]`", which reads as — and was first implemented as — one `brentq` on `[l,u]`.

That returns the wrong root. The residual is `τ - clip(τ¹(·), l, u)`, and the clip that makes `[l,u]` a
guaranteed bracket also creates an *exact* root at whichever end the extrapolated policy overshoots:

| | `ι_0(u)` | `𝒮_0` upper | extrapolated `τ¹` | residual at `u` |
|---|---|---|---|---|
| CRRA (`ρ=1.15`) | 5.5e3 | 2.0 | **8.32** → clips to `u` | **0** |
| LOG (`ρ=1`) | 6.9e3 | 2.0 | −0.70 → clips to `l` | 0.9998 |

So the CRRA path started from `s_0 = 2e-11`, `ι_0 = 5.5e3`. **Which way this falls is luck** — the two
cases differ only in the sign of the extrapolation. Instead: evaluate the residual on `𝒯`, return NaN
wherever the implied `(s_0,ι_0)` leaves the state grids, take the lowest sign change among survivors, and
`brentq` inside that one cell; report multiplicity (`nRoots`) rather than resolving it silently.
Transferable form: `crossCuttingFindings.md` #2.

## 10. The forward walk re-solves the state transitions — *the code moved, not the doc*

*Code*: `LOG.approximatePEE` / `CRRA.approximatePEE`, `exact = True` (default). *Doc*: `num_peePath.tex`
"Forward simulation" — `eq:forwardSim` is meant literally.

The first implementation read the transitions off the `sPolicy`/`ιPolicy` interpolants over the
*predetermined* state, i.e. interpolated a composition the doc evaluates directly. Max absolute
discrepancy over the path:

| | re-solved | interpolated |
|---|---|---|
| LOG `ι` | 1.2e-8 | 4.7e-6 |
| CRRA `s` | 1.1e-7 | 6.6e-6 |
| CRRA `ι` | 4.7e-7 | 9.9e-6 |

Two orders of magnitude for one scalar root per **period**, against the one per **node** the backward
recursion has already paid. Under LOG there is a second reason: `ι_t` is a function of `τ_t` alone, and
interpolating `ι_t` over `ι_{t-1}` discards exactly that. The interpolated walk survives as `exact=False`.

*The one deviation in this direction*: a derivation the implementation quietly weakened, because
interpolating something already computed looks like reuse rather than approximation. Worth checking for
specifically when a later section consumes an earlier section's output.

## 11. The outer finite-difference step: scipy's default, both preference cases

*Code*: `model.py` `calibrate`; `_calOuterKwargs` is **empty**. *Doc*: `num_calibration.tex`, "The outer
residual is only piecewise smooth" — the LOG/CRRA split it used to carry should be removed.
*Test*: `test_calibration.py` §5, `test_calibrationGrid.py` (`_calOuterKwargs == {}`).
*Script*: `measureOuterSettings.py --test jac|eps`.

The doc predicted that the step "must be large enough that the induced movement of the state clears a
grid cell" and that `√(machine eps)` "will return noise". The opposite holds: the difference quotient is
flat across six orders of magnitude and it is the **large** steps that misbehave. `τ_t` is located by
interpolation *inside* a cell of `𝒯` and the policy interpolants are piecewise linear in the state, so a
small step stays on one linear piece and returns that piece's slope — which is what Newton wants.

A CRRA-only `eps=1e-4` override was carried for a while on the strength of one corrupted Jacobian column
(`η0` at 5.13 against a resolved 0.99). That was the adaptive smoother's residual jumps being straddled at
that step, not a property of the CRRA residual. Re-measured at `smoothKnots=4`:

| ‖`η0` column‖ rel. to `h=1e-4` | 1.49e-8 | 1e-6 | 1e-5 | 1e-4 | 1e-3 | 1e-2 |
|---|---|---|---|---|---|---|
| ρ=0.9 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9995 | 0.9952 |
| ρ=0.7 | 1.0001 | 1.0000 | 1.0000 | 1.0000 | 0.9996 | 0.9956 |

Flat to 0.01%, and calibrating from a common start gives the same evaluation count and parameters to
3.7e-10 at every step, with scipy's default reaching the tightest residual of the three. The override was
removed rather than retuned. Transferable form: `crossCuttingFindings.md` #6.

## 12. The CRRA calibration keeps a finer inner grid than the PEE solve

*Code*: not defaulted — `CRRA.initGS({'nι': 45, 'ns': 45})` before `calibrate`. *Doc*:
`num_calibration.tex` "Order of work, and a check". *Test*: `test_calibration.py` §8.

The original argument — that `30×30` converged to a *displaced* root, `β` off by ~1% with the refinement
ladder plateauing at 3.1e-3 — was itself a reading of the smoother's discontinuity and does not reproduce.
What survives is a genuine but modest resolution effect that **grows with distance from `ρ=1`**: `n=30`'s
refinement ladder runs 1.0× `n=60`'s at ρ=0.9, 1.2× at ρ=1.02 and 2–3× at ρ=0.7. Parameter displacement
against `45×45` is 1.5e-4 (ρ=0.9) and 3.8e-4 (ρ=0.7) — smaller than the two solver changes made the same
day moved the LOG anchor. `n=60` buys nothing over `n=45` (parameters differ by 1.0e-4, the same order as
the spread among all three), so **~1e-4 in the parameters is the outer answer's floor**, and that is the
number `calibrate`'s `tol` should be read against.

`45×45` is therefore kept on weaker grounds than it was adopted on: not "`30×30` is wrong" but "`30×30` is
~3× coarser at ρ=0.7 and the sweep runs to ρ=0.5". The 4× cost is real — roughly 90 min against 6 h for a
16-point sweep — and is what to re-examine first if the sweep budget binds. The two grids are deliberately
not unified: `30×30` is what `test_peeCRRA.py`/`test_peePath.py` assert their spacing tolerances against.

## 13. Continuation interpolants must not be piecewise linear (CRRA calibration)

*Code*: `gridsearch/interp.py` (`kind`, NaN handling); `policy.py` `_gridSettings['interpKind']`.
*Doc*: `num_calibration.tex`, "Where the hazard does bite".

`τ^t(·,·)` piecewise linear in the state makes the outer residual surface only piecewise `C¹`, and Newton
cannot descend it. At ρ=1.1, 45×45:

| `interpKind` | outer solve | residual at the converged `x`, 45 / 60 / 75 |
|---|---|---|
| `linear` | **never converges** — stalls ~3e-5 after 60+ evaluations | 3.27e-5 → 1.52e-4 → 2.93e-4 — **growing** |
| `cubic` | **1.33e-11 in 12 evaluations** | 1.33e-11 → 1.69e-4 → 5.06e-5 — **shrinking** |

The calibrated parameters differ by 0.016% in `β`, so `linear` was not badly displaced — it simply could
not drive the residual down. **`interpKind` must be given to both solvers, not keyed to CRRA**; keying it
is what produced the `ρ=1` anchor defect (`informalSavings_resolvedIssues.md` §2,
`crossCuttingFindings.md` #7).

**`pchip` is the theoretically right choice and is not usable in 2-D.** Monotone and `C¹`, so unlike
`cubic` it cannot overshoot a policy flat at a bound (measured: `cubic` returns `[-0.088, 3.105]` on data
spanning `[0,3]`). But `RegularGridInterpolator` rebuilds its pchip splines **on every call** — 844 ms per
3600-point evaluation against 0.59 ms for `linear` and 1.02 ms for `cubic`, taking a CRRA solve from 5.7 s
to over 10 min. Until a precomputed bicubic-Hermite evaluator exists, `cubic`'s overshoot is unguarded on
`h`/`s`/`ι`/`Γs` (`τ` is clipped already, item 3).

Two NaN traps in `gridsearch/interp.py` that any non-linear kind needs:
1. Spline methods refuse to be **constructed** over NaN. Invalid nodes are filled from their nearest valid
   neighbour for the fit and masked back to NaN on evaluation. The mask is load-bearing:
   `approximatePEE`'s `strict` check relies on a path through an infeasible cell going non-finite
   *without* leaving the rectangle.
2. `RegularGridInterpolator` builds spline methods **lazily, per axis, at call time**, so a non-finite
   evaluation *coordinate* makes axis 0 return NaN and axis 1 then raises while building a spline over it.
   `linear` tolerates NaN coordinates for free; the spline kinds need an explicit guard.

One caveat on the masking: `interp1d`/`RGI` assign a point exactly on a node to the left-hand interval, so
a *valid* node bordering an invalid cell reads the NaN and returns NaN. The masked kinds return the node's
own value there. A lookup artifact, stated explicitly in `test_interp.py` rather than inherited.

---

## Left in the code, with no doc counterpart (by design)

- `base.py`'s `lnRleadΘ` reads `α` and `power_h` at `t` though both are `t+1` objects exactly. Follows
  `Rlead`'s convention; immaterial unless `α`/`ξ` vary over `t`.
- `gridsearch.griddedInterp2D` — extrapolating, evaluated on paired coordinates — for the CRRA
  continuation surfaces.
- `gridsearch/continuation.py` (`marchGrid`) — the anchored parameter march behind `calibrateGrid`. Purely
  numerical scaffolding; it changes no equation.
