# InformalSavings

Overlapping generations with `J+1` household types where type 0 ("informal") **saves** through an informal
vehicle rather than being hand-to-mouth. Informal savings earn `R_t^0 = R_t·χ_t^R` and stay **out of the
formal capital stock**. Derivation in `writing/informalSavings/` (`model*.tex` = model/equilibrium,
`num*.tex` = numerical solution); tex labels like `eq:auxiliary:s0_s` are cited throughout the docstrings.

## The one structural consequence that drives everything

`ι_t ≡ s_{t,0}/s_t` (`eq:auxiliary:s0_s`) depends on `τ_t` through `Θ_{s,t}`. Unlike `s_{t,i}/s_t`, which
reduces to a closed form in `τ_{t+1}` alone, `ι_{t-1}` is **an endogenous state of the political problem**.
So:

- **The economic equilibrium is unchanged.** `Γs`, `Θh`, `Θs`, `s`, `h`, `si_s`, `κ`, `bbar` all sum over
  `i>0` only and never see `s_{t,0}`. `ι_t` is a closed-form read-off of the solved core, **not** part of
  any root problem — `EE_*_solve`/`steadyState_*` needed no change.
- **The politico-economic equilibrium changes completely.** Even under LOG there is now a state, so the
  triangular `z_t = z_t(τ_t, τ_{t+1})` structure is gone and with it the whole-path simultaneous solve.

## Timing convention

Docs run `t=1,…,T` with `t=0` a pre-determined state; code has `db['t']` defaulting to `0,…,T-1`.

| Docs | Code |
|---|---|
| `t=0` (pre-determined) | the `s0` function argument (state *before* `db['t'][0]`) |
| `t=1` (first active period) | `db['t'][0]` = `Base.tFirst` |
| `t=T` (terminal) | `db['t'][-1]` |

Two db entries share names with the above by coincidence: `db['s0']` is the savings **rate** at the
baseline year (reported; it identified `β` until 2026-08-24, when `db['KY0']`, the capital-output ratio,
replaced it as the target), and `db['t0']` is the *index* of the calibration baseline year.

## Files

| | |
|---|---|
| `base.py` | `Base`/`BaseGrid`/`BaseTime` — the economic-equilibrium equations, each method named after its tex label. Scalar / grid-valued / vectorized over `t` |
| `model.py` | `ModelInformalSavings`: db scaffolding (§0-2), EE solve given a policy path (§3), steady state (§4), initial state (§5), calibration (§8, grid §8.1) |
| `policy.py` | `LOG` / `CRRA` — the full backward recursion, over `ι_{t-1}` and over `(s_{t-1}, ι_{t-1})` |
| `test.py` | loads `data/ArgentinaTest.xlsx` and builds the real Argentina instance. A bare `ModelInformalSavings()` has identical household types and gives `NaN`/`inf` `θ`/`κ`/`ε` — expected |

**Experiment scripts** (not tests): `calibrateRhoGrid.py` (the ρ sweep), `retargetCalibration.py`
(parameters as a function of ONE calibration target), `shockUniversal.py` (the unanticipated
universalisation, `num_shock.tex`), `shockEEOnly.py` (the same reform with taxes held at the baseline
path), `sweepEpsThetaGrid.py` (the cartesian `(ε, θ)` comparative statics behind the paper's
`ARG_LOG_FourInOne`), `plotUniversalShock.py`, `plotBoundary.py`.

**Measurement/diagnostic scripts** (not tests, kept because the chains are worth re-running rather than
re-deriving): `measureGrids.py` (reachable box, occupancy, `atBound`, anchor comparison — feeds the grid
rule; `--legacy` reproduces the pre-2026-08-19 rule on one code path), `measureOuterSettings.py` (the
outer Jacobian across finite-difference steps, a real calibration at each candidate step, and the inner
grid ladder), `diagnoseRho07.py` (the four diagnostics that located the residual discontinuity),
`diagnoseLogCrraBoundary.py` (the ρ=1 boundary; `--mode common|production` is the point of it — any
measurement that does not hold `nι`/`interpKind` fixed across the boundary measures their sum and
attributes it to the recursion).

**Test suites**: `test_ee.py` (36 checks, rebuilding every consumption level from the primitive
FOCs/budgets), `test_peeLOG.py` (52), `test_peeCRRA.py` (35), `test_peePath.py` (41),
`test_createCopyFromt0.py` (36), plus the slow `test_calibration.py` (~12 min) and
`test_calibrationGrid.py` (~45 min). Each is a standalone script printing one PASS/FAIL line per
assertion via `gridsearch/testing.py`; run them individually or through `python/runTests.py`.

Two things the sweeps do that will bite: **a re-run under changed settings silently returns the old rows**
unless given a new `--out` or `--force` (they resume from their own csv), and `--out` is relative to this
directory, since the scripts `chdir` so `test.py` finds `data/`.

## Conventions and traps

- **`hRatio` vs `hηRatio` (`base.py` §0).** Two ratios differing by a factor `η_{t,i}`:
  `hRatio = h_{t,i}/h_t = (η/X)^ξ/Γh` and `hηRatio = h_{t,i}η_{t,i}/h_t = auxProd/Γh`. `hi`/`bi` need the
  first; `si_s`'s third term, `c2i` and `dlnc2i_dτ` need the second. Conflating them was a real bug, live
  in both modules. Sanity checks: `∑γ_iη_i·hRatio_i = 1` and `∑γ_i·hηRatio_i = 1`.
- **`χ^R` carries a *period* index, not a generation index.** `R_t^0` is the return earned between `t-1`
  and `t`, so `ι_t`/`c10`/`tildec10` use `χ^R_{t+1}` (they discount `b_{t+1}^0`) while `c20`/`dv20` use
  `χ^R_t`. Verified with a time-varying `χ^R`, so it is not an untested convention.
- **Reporting domains.** `Γs`/`B`/`B0`/`si_s`/`ι` report at length `T-1` (`db['txE']` — all genuinely
  undefined at `T`, where `s_T=0` makes both ratios `0/0`); everything else is length `T`. `_wrapVars`
  looks each name up in `_t2vars`/`_txE2vars`; a name in neither raises.
- **Explicit vs db-sourced.** Primitives (`α, ξ, ν, γ, η, X, β, p, κ, χR, Γh, …`) are read from db.
  Anything solve- or policy-dependent — `τ`, `θ`/`ε`, `s`/`h`, `B`/`B0`, `ι` — is always an explicit
  argument.
- **`cacheParams()` is opt-in and block-scoped** (~6.5× per evaluation, flat in grid size). Deliberately
  not always-on: `model.py` rewrites whole db symbols during calibration, and a surviving cache would
  return stale parameters *silently*.
- **Differentiate along `ln(1-τ_t)`, not `τ_t`** (`policy.py`'s `_gradProfile`). Every profile carries a
  `ln(1-τ_t)` term, so `dy/dτ` diverges like `1/(1-τ_t)`: a raw-`τ` fit is off by ~1e-2 near the top of
  `𝒯` against ~1e-15 in `x`. Do not simplify this back to a direct `griddedGradient1D(τGrid, …)`.
- **Smoothing the *derivative* hurts** (3–10× worse than an interpolating spline); the doc's smoothing
  advice applies to `τ_t(ι_{t-1})` before interpolation, a different object. **And a smoothed policy must
  be clipped back into `[l,u]`** — a spline through a profile flat at a corner undershoots it. Smoothing
  is a denoise, not a re-optimisation.
- **`interpKind` and `smoothKnots` go to BOTH solvers; only the grid sizes are keyed.** Both are
  well-posedness choices, and keying either by solver is a bug: at `'linear'` the LOG solve does not
  converge in `nι` at all, and since `τ(t0)` is a calibration *target* the parameters get fitted to one
  realisation of that jitter. `nι` legitimately differs (LOG 50, CRRA 45) — that one **is** a resolution
  choice. The same rule reaches `shockUniversal.py`, which must re-solve a calibrated instance on the
  interpolant it was calibrated at. `crossCuttingFindings.md` #7.
- **The policy smoother's knots must be pinned (`smoothKnots`, default 4), not chosen from the data** —
  FITPACK's adaptive knot count flips as a parameter moves, putting ~3.5e-6 jumps in the outer residual,
  which is what made ρ≈0.7 uncalibratable. **The default flip created an override trap**: `initGS` merges
  the caller's dict *over* the defaults, so passing `smoothKnots=None` now *disables* pinned knots. A
  caller threading an optional argument must omit the key when it has nothing to say — two callers were
  inverted by the flip, in opposite directions. `notes/informalSavings_resolvedIssues.md`.
- **The state grids anchor on `min_τ ι*(τ)` and `s*(0.3)`, not on `max_τ ι*(τ)` and `s*(0)`.** `ι*`
  diverges as `τ→1`, so a rule on its maximum had no finite content and `capι` was silently the real
  bound; `s*(0)` is *perfectly* anti-correlated with the reachable set across ρ. `padι[0]` must not be
  raised further without re-measuring `atBound` — deviations note item 4.
- **Do not auto-tune the grids from a previous run.** `initGS`' state slots are override-only by design: a
  grid learned from run *n* makes the outer residual depend on solve history — the smoother's knot flips
  relocated. Measure with `reachableBox`/`gridOccupancy` and retune the *rule* offline.
- **A clip that manufactures a bracket also manufactures a root** (`model.py`'s `initialStatePEE`). Do not
  simplify it back to a bracketed solve on `[l,u]`. `crossCuttingFindings.md` #2.
- **A superseded result file left beside the live ones is an input to anything that globs** — three
  instances in this module alone. Superseded runs go in a subdirectory; readers match the filename pattern
  exactly and treat a duplicate key as an error, never as something to average.
  `crossCuttingFindings.md` #8.
- **`τ_t` reaches `eq:stateApprox` only through `Θ_{h,t}`** (`policy.py`'s `_stateApproxSI`), so
  `_iotaOfTauS` evaluates the continuation objects once per distinct `(s_t,ι_t)` **pair** rather than per
  `(τ_t,s_t,ι_t)` triple — a 900× reduction in `report_t` and the difference between a 64 s and a 5.7 s
  CRRA solve. Exact, not an approximation; `test_peeCRRA.py` asserts the independence **bitwise**. Do not
  fold `_stateApproxSI` back into `stateApprox_t`, and do not soften `np.unique`'s exact grouping to a
  tolerance.
- **The forward walk re-solves the state transitions; it does not interpolate them** (`approximatePEE`'s
  `exact=True`). `eq:forwardSim` means that literally. Reading them off `ιPolicy`/`sPolicy` interpolates a
  composition the re-solve evaluates directly, costs ~2 orders of magnitude, and under LOG discards
  structural result 1 below.
- **The CRRA calibration's settings are not the PEE solve's**: `interpKind='cubic'` (at `'linear'` it does
  not converge at all away from ρ=1) and `nι=ns=45` set explicitly before `calibrate`. The outer
  finite-difference step is **scipy's own, for both solvers** (`_calOuterKwargs` is empty). Numbers in
  `notes/informalSavings_numericalDeviations.md` items 11–13; general diagnostics in
  `crossCuttingFindings.md` #3–#4.

## The three structural results the docs derive

All exploited. Kept because they are what the code would silently lose if someone "simplified" it — and
one has already been lost once and restored.

1. **LOG: the `ι_t` fixed point is a function of `τ_t` alone** — `ι_{t-1}` appears nowhere in it, because
   `B^i=β_i` makes `Γ_{s,t}` a function of `τ_{t+1}` only. So the state approximation is 1-D over
   `𝒯×𝒮_0'`, not repeated per state.
2. **LOG: `ι_{t-1}` enters `z_t` through one additive rank-one term** (`eq:zdecomposition`), so the whole
   state grid costs a broadcast. Carry `Θ_{h,t+1}(ι_t)`, **not** `h_{t+1}` — the level also depends on
   `s_t` and so is not a function of the state.
3. **CRRA: the two states unnest into two 1-D roots** — `ι_t(τ_t,s_t)` first (its residual sees neither
   predetermined state), then `s_t` given `s_{t-1}`. Exact, not an approximation.

Also from the docs: `l_ι > 0` strictly (it puts `dv20`'s pole outside the grid); grid searches use the
interior grid `𝒯`, not the extended `𝒯̃`; and `dlnc2i_dτ` must stay closed-form, while `dlnc20_dτ` *may*
be gridded because `ι_{t-1}` is a grid coordinate rather than a function of `τ_t`.

## Model copies for shock experiments (`createCopyFromt0`)

Same mechanism as `informalAnalytical` (module-level `_sliceDb`, shared verbatim — see that README for the
design). One addition, since this module has a second state:

**`stateAtT0(report, t0, init)` returns `{'s0', 'ι0'}`, and the two states are asymmetric.** `s_` is
reported lagged, so `report['s_'].xs(t0)` is exactly the state entering `t0`; but `ι` is reported on the
`txE` domain as `ι_t`, **not** lagged, so the state entering `t0` is `report['ι'].xs(t0-1)` — *except* at
`t0 == db['t'][0]`, where `t0-1` has no entry at all and the value is the model's own initial-state proxy
`init['ι']`. Pass the `'init'` dict `solvePEE_*` already returns rather than recomputing it. Getting this
branch wrong reads either an out-of-range index or, on another instance, a different period's `ι`;
`test_createCopyFromt0.py` pins it with a sentinel.

## Status

Done and verified: db/parameter scaffolding and simple calibration (§0-2); EE solve given a policy (§3),
steady state (§4), initial state (§5); `policy.py`'s `LOG` and `CRRA` classes over their respective states;
the path solve (§6-7); calibration (§8) and calibration over a parameter grid (§8.1); grid-placement
diagnostics; model copies for shock experiments; and the universalisation experiment, run across the full
ρ grid for `match` (`flat` only at ρ=1).

`calibrate`'s `tol` defaults to `1e-6`, deliberately looser than the inner solves (EE 1e-8, steady state
1e-11): those are exact root problems, this one reads its targets off a grid-searched path. ~1e-4 in the
parameters is the outer answer's floor, which is what that `tol` should be read against — do not relax it
much further.

Results (the ρ sweep, the shock, the decomposition, the `(ε,θ)` grid, and the anchor's history):
`notes/archive/informalSavings_results.md`. Departures from the `num_*.tex` specs, with the measurement
behind each: `notes/informalSavings_numericalDeviations.md` — read it before editing those specs.

## Open items

- **`EE_report` uses proxy lagged objects at a model copy's first period**, which contaminates
  `shockUniversal.py`'s `d_c20` at `t0`. `EE_report` backs its first period's lagged objects out of
  `initialState_solve` rather than taking them as arguments; on the *full* model that is right, on a
  **copy** it is not, since the true `ι_{t0-1}`/`h_{t0-1}` are the baseline's and `stateAtT0` already knows
  them. `c20` at `t0` is off by **+5.3–5.7% of level** under both solvers, and `bbar` by +0.01–0.13% under
  CRRA only. `b0`/`bi` are clean (`h_{t-1}` cancels against `bbar`), and everything from `t0+1` on is
  clean — so τ/`s`/`h`/`ι`, the paper's three Argentina tables and both figures are unaffected. The
  no-shock control does not catch it, because `shockEEOnly.py` deliberately mirrors the same convention so
  the two rows stay differenceable. **Fix**: let `EE_report` take the lagged state instead of calling
  `initialState_solve` — a `model.py` change plus a ~2.5 h re-run. Until then the consumption columns
  should not be quoted.
- **`test_calibrationGrid.py`'s pinned anchor was updated without running the suite** (2026-08-20, at the
  user's request). The pair is backed by two direct calibrations and agrees with the fine grid's
  CRRA-extrapolated prediction to 1.2e-5, but agreement with a prediction is not the suite passing. Run
  `python/runTests.py -k calibrationGrid` (~45 min) before treating it as verified.
- **`κ`'s db-cache staleness under a varying `ε` is live, not latent.** The explicit `κ(ε1, t)` exists but
  every consumer reads a cached `db['κ']`, so any path that changes `ε` must rewrite `db['κ']` with it —
  `shockUniversal.installEps` is the one that does. Nothing detects the omission: a mutually inconsistent
  `(ε,κ)` violates no equilibrium condition.
- **The low-ρ tail of the sweep is converged but not resolved** (`verifyResidual` 1.2e-3 at ρ=0.5), and
  β > 1 below ρ≈0.85 — a result about the low-EIS end rather than a numerical problem
  (`notes/argentina_calibrationTarget.md`).
- `initialState_solve` returns `s` from the **CRRA** steady state in both preference cases, while
  `initialStatePEE`/`EE_LOG_solve` take `s_0` from `steadyState_LOG_solve` under LOG. At ρ=1 the two agree
  to 1e-11 but not bitwise. Deliberate — it keeps each solver's `s_0` default consistent with itself — and
  it is why `init['s']` is not used under LOG.
- `lnRleadΘ` reads `α`/`power_h` at `t` though both are `t+1` objects exactly. Follows `Rlead`'s own
  convention; immaterial unless `α`/`ξ` vary over `t`.
- Not planned: a `χ^R` sensitivity sweep (`calibrateGrid` would do it with `par='χR'`) despite `χ^R=1`
  being a knife-edge; reducing the four-parameter outer root to two, which would also be far better
  conditioned (5.4–6.2 against 15–18) and make a residual *map* affordable; and the `flat` universalisation
  reading at every ρ rather than only the anchor.
