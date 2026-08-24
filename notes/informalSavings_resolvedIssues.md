# InformalSavings: two resolved calibration defects

Both are fixed and their transferable lessons are `crossCuttingFindings.md` #5 (the ρ≈0.7 pocket) and
#4/#7 (the ρ=1 boundary). Kept for the measurements — they are what a re-run would otherwise have to
re-derive — and because the settings they justify are still live. Full investigations, including the raw
diagnostic output that lived in `results/boundary/`, are at `c958031^`
(`notes/informalSavings_rho07_resolved.md`, `notes/informalSavings_logCrraBoundary.md`).

---

## 1. The `ρ≈0.7` pocket: an adaptive knot count inside a differentiated residual (fixed 2026-08-19)

`ρ=0.7` was the one point of the sweep that never calibrated — six attempts across four escalating
strategies, all plateauing near `3.3e-6` against a `1e-6` tolerance. It now solves in **11 evaluations,
first attempt, no step-halving**.

**Cause.** The policy smoother called `griddedSmooth1D` with `UnivariateSpline(s=1e-5)`, whose FITPACK
`curfit` chooses the number and placement of interior knots to meet a residual bound. That count is an
integer chosen *from the data*: it flips as a parameter moves, the fitted policy jumps, and the
calibration finite-differences a residual containing that solve. Where a root falls inside a jump it does
not exist in the discretized problem, and no warm start, step size or refinement reaches it.

**The diagnosis is re-runnable**: `python/InformalSavings/diagnoseRho07.py` (tests 1–4), off the pickled
instances in `results/calibration/instances/` — i.e. at points that actually converged, which matters,
since the earlier session's probe was taken off-root. What it found:

- `cond(J)` 15–18 at the flanking points against 11.0 at ρ=1.1 — benign, so not an ill-conditioned
  intersection.
- At ρ=0.7875 the `β` column disagrees by ~22% at the configured `eps=1e-4` while `h=1e-5` and `h=1e-3`
  agree to 3%. **A step anomalous on both sides is a straddled discontinuity, not truncation error.**
- A 41-point residual scan along `β`: uniform steps of `6.341e-07` punctuated by five jumps, all four
  residual rows jumping at the *same* offsets — a single discrete event. The dominant jump is ~3.5e-6,
  the size of the plateau.
- No feasibility count, root count or `selectMax` count changed across the jump. The `τ` policy grids
  diverged **only at `t=2`** (9.49e-04 against 1.07e-06, 886×) — the first period going backward that
  carries infeasible cells, hence the first whose smoothing spline is fitted on a masked node set.

**Fix.** `griddedSmooth1D(..., knots=m)` fits `LSQUnivariateSpline` with interior knots at every `m`-th
**valid** node. Knots then depend only on node positions and the validity mask, never on the values, so at
a fixed mask the smoother is a **linear map** of its input. Placing them on valid nodes satisfies
Schoenberg–Whitney per column, which fixed positions in grid coordinates would not once a column carries
NaNs. It is ~2.4× faster too. Exposed as `smoothKnots`, defaulting to `None` so old results reproduce
bitwise. Re-running the 41-point scan: **five jumps → zero**, largest excess −8.0e-10 (0.1% of the median
step) against −2.607e-06 (411%).

**Two provocations that find nothing**, worth knowing before writing a test for this: a constant offset or
a pure rescaling provokes no knot flip at all (FITPACK's count is driven by the residual against the
smoothing bound, which both leave unchanged — the perturbation must change the profile's *shape*); and
over a *wide* parameter sweep the genuine change in the profile dominates, so adaptive and fixed branches
both read ~1.2 on a max/median jump ratio. `gridsearch/test_interp.py` §5 therefore asserts the
*mechanism* — 6 distinct knot counts and 11 flips for the adaptive branch where the fixed branch holds 10
throughout, plus linearity in the data to 1.78e-15 — rather than a tuned threshold.

### The grid retune that came with it (live configuration)

Separate change, same session: the smoother made the residual *continuous*, the grids made it *resolved*.
Measured by `policy.reachableBox`/`gridOccupancy` and `measureGrids.py`, no solve required.

Across ρ ∈ [0.5, 2.0] under LOG, `min_τ ι*(τ)` is constant to **0.045%** and the reachable box sits at
0.539–0.557× and 2.89–3.07× it — both `ι` bounds are stable multiples of the *minimum*, so measuring once
on the cheap LOG calibration suffices for a whole sweep. For `s`, the incumbent anchor `s*(0)` is
perfectly anti-correlated with the box's upper edge (−1.000), so no constant pad on it can track;
`s*(0.3)` is ρ-stable to 1.5% while remaining a solved function of the calibrated parameters.

| | old | new |
|---|---|---|
| `padι` | `(0.25, 1.25)` on `(min, max)` | `(0.45, 3.7)` on `(min, min)` |
| `pads` | `1.25` on `s*(0)` | `(0.45, 3.65)` on `s*(0.3)`, `sAnchorτ=0.3` |

Anchoring the `ι` top on the *minimum* is what retires `capι` as the operative bound: `max_τ ι*(τ)`
diverges (25 484 at τ=0.9999), so the rule written on it had no finite content and the real bound was an
absolute constant that would not survive a change of data. `capι=2.0` survives as an inert backstop.
Effect: `ι` occupancy 49–52% → 78–80%, `s` occupancy 40%/80% → 62%/76%, `outOfGrid` 0 throughout.

**One tension, resolved by evidence.** Feasible τ-nodes fell 81% → 66%, past the 29/101 the deviations
note flags as the symptom that made the doc's 0.75 pad unusable — but the harm it names did not follow:
corner selections *fell* (988 → 45 at ρ=2.0) and the calibration converged in the same evaluation count to
the same answer (β −0.047%, ω −0.071%). The loss has a different source: `l_ι` moved only 0.076 → 0.137,
still below the 0.228 that caused the documented problem, so the lost nodes come from the *upper* bound
— high-τ nodes whose implied `ι_t` the equilibrium never visits.

**End-to-end**, both changes active:

| ρ | residual | nfev | verify (orig. sweep) | verify (smoother only) | verify (both) |
|---|---|---|---|---|---|
| 0.9 | 3.92e-12 | 12 | 6.5e-05 | 1.19e-04 | **3.29e-05** |
| 0.8 | 4.14e-12 | 11 | 3.8e-05 | 1.58e-04 | **4.48e-05** |
| 0.7 | 5.96e-12 | 11 | *never solved* | 3.10e-04 | **3.95e-05** |

The smoother alone left `verifyResidual` rising toward the hard region; with the retune it is flat and
better than the original sweep everywhere. `dlnβ/dρ` continues the original series' monotone steepening
(−2.259/−1.756/−1.406 against −2.254/−1.752/−1.402), so the answer is on the trend, not merely converged.

---

## 2. The `ρ=1` LOG/CRRA boundary: an interpolant change wearing a solver change's clothes (fixed 2026-08-20)

**The defect.** `calibrateRhoGrid.py` keyed its grid settings by solver and gave the LOG anchor only
`smoothKnots`, so `ρ=1` was the sole point in every sweep solved on **piecewise-linear** continuation
interpolants. The calibration then fitted `(β,ω,η0,X0)` to hit `τ(t0)=0.125` at one realisation of that
jitter, displacing the anchor off the CRRA curve, and the universalisation response at `t0+1` inherited a
**+10.6%** displacement — read for a session as a LOG-vs-CRRA "solver-transition artifact".

**The recursions were never the problem.** CRRA at ρ=1±δ against LOG at ρ=1, read through the central
average `D(δ) = ½[x(1+δ)+x(1−δ)] − x_LOG(1)` (which cancels the true economic slope — reading the raw gap
instead was the easy mistake): under common settings `C = +1.6e-5` in `τ(t0)`, 0.0016 of a τ-grid cell.
Under production settings the same `C` is 40–63× larger, and since CRRA's settings are identical in both
modes the whole difference is the LOG answer moving:

| change at fixed parameters | Δτ(t0) | Δτ(t0+1) |
|---|---|---|
| `nι` 50→45 at `cubic` | −1.2e-5 | −2.3e-5 |
| `linear`→`cubic` at `nι=50` | **+6.30e-4** | **+1.33e-3** |
| `nι` 45→60→90 at `cubic` | flat to 1e-5 | flat to 2e-5 |

**`interpKind` carries all of it; `nι` is already converged.** The linear LOG solve does not converge in
`nι` — it *oscillates*, spread 2.4e-3 in `τ(t0+1)` against cubic's 2.5e-5 over `nι ∈ [45,120]`, 95×.
There is no `nι` at which it is right, which is why refinement was never going to help. The
`0.12500000` at `nι=50` is not convergence: `τ(t0)` is a calibration target.

Second differences over a fine ρ grid locate the displacement exactly — one displaced point reads
`[+d, −2d, +d]`, which `η0` (d=9.3e-6) and `X0` (d=1.02e-4) give to two significant figures, reproduced
independently by the coarse sweep at ten-fold different spacing to 6%. For scale, `X0`'s entire range
across ρ ∈ [0.5,2.0] is 1.02e-3, so the anchor's displacement is ~11% of that parameter's whole economic
variation. Recalibrating the anchor on cubic lands `β`, `η0`, `X0` on the CRRA-fit prediction to 5–6
significant figures, and leaves the CRRA points bit-identical — bounding the blast radius to the anchor
row alone.

**The fix was at the call site that keyed it**, not at the class default: `CRRA._gridSettings` inherits
`interpKind` from `LOG`, so flipping it there moves both defaults and trips two suites whose assertions
were themselves measured at `'linear'` (`test_peeCRRA`'s bound-overshoot tolerance, and `test_peePath`'s
"re-solving beats interpolating", which stops holding once the interpolant is `C¹` — that penalty was
largely a linear artifact). So: give both solvers `interpKind`, keep grid sizes per-solver. The `verify`
refinement check was keyed the same way and now covers LOG too, reporting 5.73e-6 at the anchor — a number
that had been `NaN` in every sweep ever run.
