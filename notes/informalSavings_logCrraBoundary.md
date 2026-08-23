# The LOG/CRRA boundary at `ρ=1`: an interpolant change wearing a solver change's clothes

Status: **diagnosed, and FIXED on 2026-08-20.** `calibrateRhoGrid.py` now gives `interpKind` to both
solvers and keys `verify` on `'LOG'` as well; `shockUniversal.py` re-solves LOG on the interpolant it was
calibrated at; `test_calibrationGrid.py`'s pinned anchor is updated. The `ρ` sweep and the universalisation
shock were re-run. The pre-fix series is kept as `informalSavings_rhoGrid_preInterpFix.csv` (+
`instances_preInterpFix/`). See "What was changed" at the bottom.

**One-line summary (of the defect, now fixed):** `calibrateRhoGrid.py` keyed its grid settings by solver
and gave the LOG anchor only `smoothKnots`, so `ρ=1` was the sole point in every sweep solved on
**piecewise-linear** continuation interpolants — an answer that does not converge in `nι` but jitters by
~2.4e-3 in `τ(t0+1)`. The calibration then fitted `(β,ω,η0,X0)` to hit `τ(t0)=0.125` at one realisation of
that jitter, displacing the anchor's parameters off the CRRA curve, and the universalisation response at
`t0+1` inherited a **+10.6%** displacement. It was never the LOG/CRRA recursions disagreeing: those agree
to 0.2% of a grid cell.

Companion to `notes/crossCuttingFindings.md` #4 (piecewise-linear interpolants limiting an outer solve)
and #5/#6 (settings adopted against a defect, and how such findings age). This is #4 recurring in a place
nobody looked: not in the CRRA calibration that motivated the original finding, but in the **LOG anchor
that was left behind when the fix was applied**.

## The symptom

`plotUniversalShock.py --period 1` showed `Δτ` dipping at exactly `ρ=1.0→1.1` (6.09% → 5.72%), with both
flanking segments smooth, and the impact period showing nothing. `ρ=1` is the module's only LOG point
(`model._calPreferences` returns `'LOG'` iff `ρ==1` exactly), so the feature sat precisely on the solver
boundary. The README recorded it as a candidate solver-transition artifact and listed the standard
diagnostic (refine the CRRA point at `ρ=1.1`) as not yet run.

That diagnostic would not have found it. The problem is not on the CRRA side.

## The confound that had to come out first

Before the fix, crossing `ρ=1` in `calibrateRhoGrid.py` changed **four things at once**, because the grid
settings were keyed by solver and the LOG anchor was given only `smoothKnots`:

| | LOG (`ρ=1`) | CRRA (every other `ρ`) | after the fix |
|---|---|---|---|
| recursion | 1-D state `ι_{t-1}` | 2-D state `(s_{t-1}, ι_{t-1})` | unchanged — genuinely differs |
| `nι` | 50 (class default) | 45 | unchanged — a resolution choice, may differ |
| `interpKind` | **`'linear'`** (class default) | **`'cubic'`** | **`'cubic'` for both** |
| `smoothKnots` | 4 | 4 | unchanged |

Any measurement that does not hold the middle two fixed attributes their sum to the first.
`diagnoseLogCrraBoundary.py` therefore runs every test in two modes: `common` (both solvers on the CRRA
settings, isolating the method) and `production` (LOG on its pre-fix class defaults — retained as the
control that reproduces the artifact).

## The measurements

All at **fixed** calibrated parameters unless stated; `--test limit`, `--test settings`, `--test cal`,
`--test path`, `--test shock`. Raw output in `results/boundary/`.

**1. The two recursions agree in the limit, to 0.2% of a grid cell.** CRRA at `ρ=1±δ` against LOG at
`ρ=1`. The raw gap is linear in `δ` and antisymmetric — that is the true economic slope `dτ/dρ`, not a
solver artifact, and reading it as one would have been the easy mistake. The discriminating statistic is
the central average, which cancels the linear term:

    D(δ) = ½[x(1+δ) + x(1-δ)] − x_LOG(1)   →   ½x''δ² + C

`D(δ)` falls like `δ²` at large `δ` (successive ratios ≈4) and then **plateaus** (ratios ≈1.00), so `C≠0`
and the fit `D = C + aδ²` holds across the whole ladder to ~10%. Under **common** settings
`C = +1.6e-5` in `τ(t0)` and `+2.1e-5` in `τ(t0+1)` — 0.0016 and 0.0021 `τ`-grid cells, far below the
module's documented ~1e-3 floor for `z_t`. **The recursions are fine.**

**2. Under production settings the same `C` is 40–63× larger** (`+6.3e-4` and `+1.33e-3`, i.e. 0.063 and
0.133 cells). CRRA's settings are *identical* in the two modes, so the whole difference is the LOG answer
moving. Decomposing it with cheap (~1 s) LOG solves:

| change at fixed parameters | Δτ(t0) | Δτ(t0+1) |
|---|---|---|
| `nι` 50→45 at `cubic` | −1.2e-5 | −2.3e-5 |
| `linear`→`cubic` at `nι=50` | **+6.30e-4** | **+1.33e-3** |
| `nι` 45→60→90 at `cubic` | flat to 1e-5 | flat to 2e-5 |

`nι` is irrelevant and already converged. **`interpKind` carries all of it.**

**3. The LOG solve on linear interpolants is not grid-converged — it jitters.** `τ(t0)` across
`nι ∈ {30,40,45,50,60,75,90,120,160}`:

    linear:  0.126147 0.126693 0.125959 0.125000 0.125925 0.125260 0.125262 0.125624 0.126199
    cubic:   0.125621 0.125610 0.125618 0.125630 0.125621 0.125628 0.125627 0.125640 0.126053

Over `nι ∈ [45,120]` the spread is 9.6e-4 (linear) against 2.2e-5 (cubic) in `τ(t0)`, and 2.4e-3 against
2.5e-5 in `τ(t0+1)` — **95×**. The linear series has no trend; it oscillates. There is no `nι` at which it
is right, which is why refinement was never going to help and why the planned CRRA-side refinement would
have closed nothing.

The `0.12500000` at `nι=50` is not convergence. `τ(t0)=0.125` is one of `eq:calibration`'s four **targets**,
so the calibration drove `(β,ω,η0,X0)` until it was hit *at that one setting* — i.e. the parameters were
fitted to one realisation of the jitter. (The cubic `nι=160` entry, 0.126053, is a genuine outlier against
its own series and is not explained here; flagged below.)

**4. So the discontinuity is already in the calibration.** Second differences over the fine grid identify
it exactly: for a series where only the middle point is displaced by `d`, they read `[+d, −2d, +d]`.

| | second differences | reading |
|---|---|---|
| `η0` | +9.29e-6, **−1.85e-5**, +9.30e-6 | exactly `[+d,−2d,+d]`, `d=9.3e-6` |
| `X0` | +1.02e-4, **−2.03e-4**, +1.02e-4 | exactly `[+d,−2d,+d]`, `d=1.02e-4` |
| `β` | −5.1e-4, **+2.57e-3**, −5.6e-4 | same shape plus genuine curvature |
| `ω` | +4.7e-3, **−7.0e-3**, +4.6e-3 | same |
| `τ`, `sr` | ~1e-13 | calibration **targets** — pinned, cannot jump |

The anchor is displaced off the curve its four CRRA neighbours trace by −0.083% (`β`), +0.144% (`ω`),
+9.3e-6 (`η0`), +1.02e-4 (`X0`). The published coarse sweep (`Δρ=0.1`) reproduces the two flat ones
independently at +9.9e-6 and +1.08e-4 — two measurements at ten-fold different grid spacing agreeing to
6%. For scale, `X0`'s **entire** range across `ρ ∈ [0.5,2.0]` is 1.02e-3, so the anchor's displacement is
~11% of the whole economic variation of that parameter. (`β`/`ω`'s deviations on the coarse grid, +1.2%
and +0.8%, are dominated by polynomial fit error across a window where `β` falls 2.08→0.85; the fine
grid's numbers are the reliable ones.)

**5. Recalibrating the anchor on cubic removes the displacement.**

| | CRRA-fit prediction at `ρ=1` | production LOG (`linear`) | common LOG (`cubic`) |
|---|---|---|---|
| `β` | 1.211956 | 1.210923 | **1.211956** |
| `ω` | 2.641327 | 2.645212 | 2.641440 |
| `η0` | 0.3255500 | 0.3255592 | **0.3255500** |
| `X0` | 0.4081390 | 0.4082406 | **0.4081400** |

`β`, `η0`, `X0` land on the predicted values to 5–6 significant figures; `ω`'s residual displacement falls
35×. The CRRA points are **unchanged** between the two modes (`ρ=1.01`: `β=1.19691, ω=2.61603` in both),
confirming that the warm start does not move a root and bounding the blast radius to the anchor row alone.

**6. The shock response inherits it.** `d_τ(t0+1)` across the fine grid, production settings:

    ρ:      0.98      0.99      1.00(LOG)  1.01      1.02
    d_τ:    0.05445   0.05475   0.06089    0.05530   0.05556

The four CRRA points trace a smooth rising line; the LOG point sits +5.87e-3 above it, **+10.6% of scale**.
`d_s(t0+1)` is displaced −11.8% of scale, `d_τ(t0)` +3.8%. The `ρ=1` value 6.089% reproduces the README's
6.09% exactly, so this is the same feature: the anchor is a **spike**, and `ρ=1.0→1.1` reads as a dip only
because the anchor is too high.

`τ(t0)` is pinned at 0.125 at every point, which is why the impact period looked cleaner than `t0+1`: the
one object the calibration controls exactly is the one the impact plot is closest to.

**7. Recalibrating the whole fine grid with the anchor on cubic removes it everywhere.** Independently
calibrated series, `--mode common` throughout (`informalSavings_rhoFineCommon.csv`):

| anchor displacement | production | common | reduction |
|---|---|---|---|
| `β` | −1.03e-3 | −7.3e-6 | 142× |
| `ω` | +3.88e-3 | +1.10e-4 | 35× |
| `η0` | +9.26e-6 | +6.7e-8 | 137× |
| `X0` | +1.02e-4 | +7.4e-7 | 138× |
| `d_τ(t0)` | +3.8% of scale | −0.027% | 140× |
| `d_τ(t0+1)` | **+10.6% of scale** | **−0.002%** | **4700×** |
| `d_s(t0+1)` | −11.8% of scale | +0.034% | 350× |

`β`'s second differences go from `[−5.1e-4, +2.6e-3, −5.6e-4]` — alternating, the displaced-point
signature — to `[+5.19e-4, +5.16e-4, +4.70e-4]`: same sign and near-constant, i.e. a smooth convex series.
`d_τ(t0+1)` becomes `0.054450, 0.054745, 0.055024, 0.055296, 0.055562`, monotone through the anchor.
Figure: `results/boundary/d_tau_t0p1_vs_rho_match.png` (`plotBoundary.py`).

**8. The CRRA side is not the problem, which the README's proposed diagnostic would have shown.** The open
item suggested refining the CRRA grid at `ρ=1.1` to test whether the dip shrinks. Done (`--test refine`):
across `n ∈ {30,45,60}`, `Δτ` moves by ~6e-5 at `ρ=1.1` and ~2.6e-5 at `ρ=1.01` — roughly 100× *smaller*
than the boundary displacement it was meant to explain. The diagnostic was well chosen for a
grid-resolution artifact and this is not one; it is on the other side of the boundary.

## Why this was invisible

- The anchor's own convergence diagnostics all pass. `residual` = 1.6e-11, `nfev` = 26, and `verifyResidual`
  — the check designed to catch "converged but not resolved" — is **`NaN` at the LOG point**, because
  `calibrateRhoGrid.py` keys `verify` on `'CRRA'` only. The one point running the unconverged interpolant
  is the one point with no refinement check.
- `crossCuttingFindings.md` #4 established that piecewise-linear continuation interpolants limit an outer
  solve, and `interpKind='cubic'` was adopted — but keyed to CRRA, since that is where the failure had
  appeared. LOG kept `'linear'` as a class default nobody revisited. The finding was applied where it was
  found rather than where it applied.
- Every published LOG result is *internally* consistent: the calibration hits its targets at its own
  settings. Nothing is detectably wrong until a second solver computes the same object a different way.

## The fix is NOT the class default — `interpKind` is shared

The obvious change, `policy.LOG._gridSettings`'s `interpKind` `'linear'` → `'cubic'`, is **wrong**.
`CRRA._gridSettings` returns `super()._gridSettings | {...}` and that override dict does **not** carry
`interpKind`, so the setting is inherited: flipping LOG's default flips CRRA's too. Tried and reverted
(`policy.py` restored and checksum-verified); it fails two suites, and both failures are informative
rather than incidental:

- `test_peeCRRA`: `eq:stateResidual:iota`'s residual at the selected `τ_t` goes `<1e-6` → `1.75e-6`. This
  is at CRRA's *coarse* `30×30` default, and it is plain cubic's documented weakness — `policy.py`'s own
  `interpKind` docstring says cubic **overshoots where a policy is flat at a bound**, which is why
  `'pchip'` is described there as better in principle. Cubic is not uniformly better.
- `test_peePath`: the assertion that re-solving a transition beats interpolating it (`exact <=
  interpolated`, the module's structural result 10 / "trap 2") stops holding — under cubic the two are
  equal to three significant figures for LOG's `ι`, and interpolated is marginally *better* for CRRA's.
  Not a defect: that test's premise was measured at `'linear'`, where the interpolant's kinks are the
  error. It does mean the "reuse is silently approximation" penalty is largely an artifact of the linear
  interpolant.

## What was changed (2026-08-20)

1. **`calibrateRhoGrid.py` passes `interpKind` to the LOG solver, as it already did for CRRA** — i.e.
   `'LOG': {'smoothKnots': knots, 'interpKind': args.interpKind}`. One line, no class default moved, and
   LOG keeps its own `nι=50`. Measured against the CRRA neighbours' prediction, this
   cuts the anchor's displacement by **~90× on every parameter**:

   | | CRRA-fit predicts | production (`nι=50, linear`) | this fix (`nι=50, cubic`) |
   |---|---|---|---|
   | `β` | 1.211956 | 1.210923 (−1.03e-3) | 1.211968 (+1.2e-5) |
   | `ω` | 2.641327 | 2.645212 (+3.88e-3) | 2.641368 (+4.1e-5) |
   | `η0` | 0.3255500 | 0.3255592 (+9.3e-6) | 0.3255499 (−1e-7) |
   | `X0` | 0.4081390 | 0.4082406 (+1.02e-4) | 0.4081379 (−1.1e-6) |

   Cost: nothing (25 nfev against 26, ~18 s). The final residual is looser — 1.06e-9 against 1.57e-11 —
   but still three orders under `calibrate`'s `tol=1e-6`, and the tight residual at `'linear'` was the
   solver converging precisely onto a jittered answer, which is exactly the trap.
2. **`calibrateRhoGrid.py` keys `verify` on `'LOG'` too** (`--verifyLOG`, default `nι=75`, LOG's
   established refinement rung at 1.5× its working 50). A refinement check that skips the anchor cannot
   catch the anchor, and that is why the defect survived: every LOG row of every prior sweep carried
   `verifyResidual = NaN`. It now reports — **5.73e-6** at the anchor, comfortably resolved.
3. **`shockUniversal.py` re-solves LOG on `interpKind`/`smoothKnots` as calibrated**, keeping the grid
   sizes CRRA-only. Without this the shock would re-solve a calibrated instance under a *different*
   interpolant than it was fitted under — the same defect one layer down. `--commonSettings` is now
   diagnostic-only (it adds the grid sizes).
4. **`test_calibrationGrid.py`**: `GRIDS['LOG']` gains `interpKind`, and the pinned anchor moves to
   `β=1.211968, ω=2.641368`. That reference has an independent check no earlier one had — the four CRRA
   points of the fine grid predict `β=1.211956, ω=2.641327` by extrapolation onto their own gap, so it is
   not merely "what the solver returns".
5. The documented calibration is now
   **`β=1.211968, ω=2.641368, η0=0.325550, X0=0.408138`** (from `β=1.210923, ω=2.645212, η0=0.325559,
   X0=0.408241`). The `ρ` sweep and the shock were re-run; the pre-fix series is kept as
   `informalSavings_rhoGrid_preInterpFix.csv`.

## Still open

- The cubic `nι=160` outlier in measurement 3 (0.126053 against a series flat at 0.12562). Far outside the
  sweep's operating range, but the one datum inconsistent with "cubic is converged"; it should be
  explained rather than left.
- `'pchip'` instead of `'cubic'` for both solvers. It is the monotone `C¹` option that would not have
  tripped `test_peeCRRA`'s overshoot, and the recorded reason it was rejected is speed (1400× slower in
  `RegularGridInterpolator`), not accuracy.
- `policy.LOG._gridSettings` still *defaults* to `'linear'`, and `CRRA` still inherits that key. Every
  calibration path now overrides it, so the default is only what a bare `LOG()`/`CRRA()` gets — which is
  what `test_peeCRRA`/`test_peePath` exercise, and both were measured at `'linear'`. Flipping the class
  default is a separate decision with its own test updates (see above); it is not required by this fix.

## `informalAnalytical`: exposed in principle, not in practice — yet

Checked while fixing this. It is **not** currently affected, and the reason is worth recording so the
check is not redone: it has no `interpKind`/`smoothKnots` settings at all (those were added to
`InformalSavings`' `policy.py` after the two modules diverged), so all six of its continuation
interpolants are bare `griddedInterp1D(...)` calls taking `gridsearch.interp`'s own `kind='linear'`
default. More to the point, it has no §8.1 — no `calibratePoint`/`calibrateGrid`, and no `ρ` sweep on
disk — so there is no march across a LOG/CRRA boundary for an anchor to be displaced *in*.

That makes this a pre-emptive note rather than a live defect: **the moment `informalAnalytical` gains a
parameter sweep spanning `ρ=1`, it inherits this exactly**, and with no `interpKind` argument to key
correctly it will inherit it in the harder-to-see form — a hardcoded default rather than a visible
setting. The cheap check before that happens is measurement 3 above: solve at fixed parameters across a
ladder of state-grid sizes and see whether the answer converges or jitters.
