# The `ρ≈0.7` calibration pocket: diagnosis and fix (2026-08-19)

`ρ=0.7` was the one point of the `ρ ∈ [0.5, 2.0]` sweep that never calibrated. Six attempts across four
escalating strategies failed (README history, module log 2026-08-12), all plateauing near `3.3e-6` against
a `1e-6` tolerance. It now solves in **11 evaluations, first attempt, no step-halving**.

This note records the diagnosis, because the *conclusion the earlier session drew was correct and its
attribution was wrong*, and because the measurement chain is worth being able to re-run rather than
re-derive. The transferable lesson is `crossCuttingFindings.md` #5.

## The cause

`policy.py`'s policy smoother — `_smooth2D` (CRRA) and `solveBackward_t` (LOG) — called
`gridsearch.interp.griddedSmooth1D`, which used `scipy.interpolate.UnivariateSpline(s=1e-5)`. With a
smoothing factor, FITPACK's `curfit` **chooses the number and placement of interior knots** to meet the
residual bound. That count is an integer chosen *from the data*, so it flips discontinuously as a model
parameter moves, and the fitted policy jumps with it.

The calibration finite-differences a residual that contains that solve. So the jumps appear as
discontinuities in the outer residual, and where a root falls inside one, **it does not exist in the
discretized problem** — no warm start, step size, or grid refinement can reach it.

## The measurement chain

All of it is in `python/InformalSavings/diagnoseRho07.py` (tests 1–4), run off the pickled instances in
`results/calibration/instances/`, i.e. at points that actually converged. This matters: the earlier
session's finite-difference probe was taken at an *off-root* point (residual 4.4e-3) and the module log
flags that caveat itself.

1. **Jacobian conditioning at the converged flanking points `ρ=0.6`, `ρ=0.7875`** — `cond(J)` is 15–18
   against 11.0 at `ρ=1.1`. Benign. Rules out an ill-conditioned intersection. The `(β,ω)` sub-block is
   much better conditioned (5.4–6.2, rows 23–27° from anti-parallel).
2. **Column stability across step sizes.** At `ρ=0.7875` the `β` column disagrees by ~22% at the
   configured `eps=1e-4` while `h=1e-5` and `h=1e-3` agree with each other to 3%. A step anomalous on
   *both* sides is not truncation error and not noise — it is a discontinuity straddled by one step and
   diluted tenfold by the next decade up.
3. **A 41-point residual scan along `β`** confirms it directly: the residual rises in exactly uniform
   steps of `6.3410e-07` punctuated by five jumps, all four residual rows jumping at the **same offsets**
   (a single discrete event, not per-target noise). The dominant one at offset `8.5e-5` is `~3.5e-6` —
   the size of the plateau. Summing the jumps inside `[0, 1e-4]` predicts a measured slope of `0.1041`
   against a true `0.1268`; test 1 measured `0.1041`.
4. **What switches.** Re-solving either side of the jump and diffing every discrete diagnostic the
   recursion records: **no** feasibility count, root count, `selectMax` count or `nRoots` changed. The
   `τ` policy grids moved identically in the jump step and a control step for `t=9…t=3`, then diverged
   **only at `t=2`** (9.49e-04 against 1.07e-06, 886×) — which is the first period, going backward, that
   carries infeasible cells, and therefore the first whose smoothing spline is fitted on a masked node
   set. Setting `smooth=0` collapsed the divergence 327×.

## The fix

`gridsearch.interp.griddedSmooth1D(..., knots=m)` fits `LSQUnivariateSpline` with interior knots at every
`m`-th **valid** node. Knots then depend only on the node positions and the validity mask, never on the
values, so at a fixed mask the smoother is a **linear map** of its input and its output moves continuously
with any parameter. Placing them on valid nodes satisfies Schoenberg–Whitney per column, which fixed
positions in grid coordinates would not once a column carries NaNs. It is also ~2.4× faster, since FITPACK
no longer iterates over knot counts.

Exposed as the `smoothKnots` grid setting, defaulting to `None` (the adaptive spline), so existing results
are reproduced bitwise until the switch is thrown.

**Effect at the jump step** (offset 8.0e-5 → 8.5e-5, `ρ=0.7875`):

| | t=2 policy | t=0 policy | walked τ | residual Δ (`sr`) |
|---|---|---|---|---|
| adaptive, *control* step | 1.071e-06 | 3.628e-06 | 7.08e-07 | +6.337e-07 |
| adaptive, *jump* step | 9.493e-04 | 3.221e-03 | 3.150e-04 | −1.972e-06 |
| `smooth=0`, jump step | 2.907e-06 | 6.788e-06 | 1.688e-06 | +6.885e-07 |
| **`smoothKnots=4`, jump step** | **1.009e-06** | **1.477e-06** | **7.661e-07** | **+6.312e-07** |

The fixed-knot smoother at the *jump* step is indistinguishable from the adaptive one at a *normal* step,
and tighter than no smoothing at all — the expected signature of keeping the denoise and dropping the
discrete choice. Re-running the full 41-point scan: **five jumps → zero**, largest excess `−8.0e-10`
(0.1% of the median step) against `−2.607e-06` (411%).

## Two provocations that find nothing

Worth recording, since a test that fails to provoke the bug reads like a bug that is not there:
- A **constant offset** or a pure rescaling of the data provokes no knot flip at all — FITPACK's count is
  driven by the residual against the smoothing bound, which both leave unchanged. The perturbation must
  change the profile's *shape*.
- Over a **wide** parameter sweep the genuine change in the profile dominates and the adaptive and fixed
  branches both read ~1.2 on a max/median jump ratio. The jump is only visible in a window where the flip
  is the biggest thing happening (1.94 against 1.01 there).

`gridsearch/test_interp.py` §5 therefore asserts the *mechanism* — 6 distinct knot counts and 11 flips for
the adaptive branch where the fixed branch holds 10 knots throughout, and linearity in the data to 1.78e-15
— rather than a tuned threshold.

## What the earlier session got right, and what it got wrong

Right: that the plateau was **not** displacement and not a bad warm start; that a 100×-closer start buying
nothing is the decisive signature. Wrong: attributing that signature to grid resolution. The planned next
step — refining `nι=ns=60` at `ρ=0.775` — would have cost ~30 minutes and, on the evidence here, would not
have closed it, because the obstacle was a discontinuity rather than a resolution limit.

The `eps=1e-4` outer step is *also* implicated but is not the fix: it is the uniquely bad step at this
point (the big jump sits inside `[x, x+1e-4]` and outside `[x, x+1e-5]`), so it corrupts the Jacobian, but
a larger step only dilutes the jump — it cannot create a root that the discretization removed. `eps=1e-3`
remains worth adopting on its own merits; `1e-5` is a lottery, since it usually straddles no jump but pays
35% of the slope when it does.

## The grid retune, measured the same way

Separate change, same session, different problem: the smoother made the residual *continuous*, the grids
made it *resolved*. Driven by `policy.reachableBox`/`gridOccupancy` (post-processing, no solve) and
`python/InformalSavings/measureGrids.py`.

**Findings.** Across `ρ ∈ [0.5, 2.0]` and under LOG, `min_τ ι*(τ)` is constant to **0.045%**, and the
reachable box sits at `0.539–0.557×` and `2.89–3.07×` it — so both `ι` bounds are stable multiples of the
*minimum*, and measuring once on the cheap LOG calibration suffices for a whole sweep. For `s`, the
incumbent anchor `s*(0)` is **perfectly anti-correlated** with the box's upper edge (−1.000: it falls 83%
across `ρ` while the box rises 20%), so no constant pad on it can track; `s*(τ_0)` still drifts 77%;
`s*(0.3)` is `ρ`-stable to 1.5% while remaining a solved function of the calibrated parameters.

**Rule change.** `padι: (0.25, 1.25)` on `(min, max)` → `(0.45, 3.7)` on `(min, min)`; `pads: 1.25` on
`s*(0)` → `(0.45, 3.65)` on `s*(0.3)` with `sAnchorτ=0.3`. Anchoring the `ι` top on the minimum is what
retires `capι` as the *operative* bound — `max_τ ι*(τ)` diverges (25 484 at `τ=0.9999`), so the rule
written on it had no finite content and the real bound was an absolute constant that would not survive a
change of data. `capι=2.0` survives as an inert backstop.

**Effect.** `ι` occupancy 49–52% → 78–80%; `s` occupancy 40%/80% → 62%/76%; `outOfGrid` 0 throughout.

**One tension, resolved by evidence.** Feasible `τ`-nodes fell 81% → 66%, i.e. ~34 of 101 infeasible,
*past* the 29/101 the deviations note flags as the symptom that made the doc's 0.75 pad unusable. The harm
it names did not follow: corner selections **fell** (988 → 45 at `ρ=2.0`, 36 → 17 under LOG) and the
calibration converged in the same evaluation count to the same answer (`β` −0.047%, `ω` −0.071%). The
reason is that the loss has a different source: `l_ι` moved only 0.076 → 0.137, still below the 0.228 that
caused the documented problem, so the lost nodes come from the *upper* bound (2.0 → 1.13) — high-`τ` nodes
whose implied `ι_t` the equilibrium never visits. `minFeasible=2` never fired.

## End-to-end result

`calibrateRhoGrid.py --lo 0.7 --hi 1.0 --step 0.1 --anchor 1.0 --smoothKnots 4`, both changes active:

| ρ | residual | nfev | verify (orig. sweep) | verify (smoother only) | verify (both) |
|---|---|---|---|---|---|
| 0.9 | 3.92e-12 | 12 | 6.5e-05 | 1.19e-04 | **3.29e-05** |
| 0.8 | 4.14e-12 | 11 | 3.8e-05 | 1.58e-04 | **4.48e-05** |
| 0.7 | 5.96e-12 | 11 | *never solved* | 3.10e-04 | **3.95e-05** |

The smoother alone left `verifyResidual` rising monotonically toward the hard region — the symptom that
region was still the least resolved. With the retune it is **flat** and better than the original sweep
everywhere. `dlnβ/dρ` = −2.259 / −1.756 / −1.406 across the three intervals, continuing the monotone
steepening of the original series (−2.254 / −1.752 / −1.402), so the answer is on the trend and not merely
converged.
