# InformalSavings

Overlapping generations with `J+1` household types where type 0 ("informal") **saves** through an informal
vehicle earning `R_t^0 = R_t·χ_t^R`, outside the formal capital stock. Derivation in
`writing/informalSavings/` (`model*.tex`, `num*.tex`); docstrings cite tex labels by name. Shared
conventions are in `python/informalAnalytical/README.md`.

**The one structural consequence.** `ι_t ≡ s_{t,0}/s_t` (`eq:auxiliary:s0_s`) depends on `τ_t`, so
`ι_{t-1}` is an endogenous state of the political problem. The economic equilibrium is unchanged (every
core object sums over `i>0`; `ι_t` is a closed-form read-off, not part of any root); the
politico-economic equilibrium changes completely (even LOG has a state; no whole-path simultaneous solve).

## Timing and data conventions

Docs run `t=1,…,T` with `t=0` pre-determined; code has `db['t']` = `0,…,T-1`, so docs `t=0` is the `s0`
argument, docs `t=1` is `db['t'][0]` = `Base.tFirst`. Name collisions: `db['s0']` is the baseline savings
**rate** (reported; `db['KY0']`, the capital-output ratio, is the `β` target since 2026-08-24), `db['t0']`
is the *index* of the baseline year.

**The tax target is derived, not read**: the workbook carries pension spending over GDP (0.071) and
`test.py` sets `db['τ0'] = spending/(1-α)`. A literal rate went stale with α once (finding #12).

## Files

| | |
|---|---|
| `base.py` | `Base`/`BaseGrid`/`BaseTime`, the EE equations, one method per tex label |
| `model.py` | `ModelInformalSavings`: db scaffolding (§0-2), EE solve (§3), steady state (§4), initial state (§5), calibration (§8, grid §8.1) |
| `policy.py` | `LOG`/`CRRA`, the backward recursion over `ι_{t-1}` and over `(s_{t-1}, ι_{t-1})` |
| `test.py` | loads `data/ArgentinaTest.xlsx`; a bare `ModelInformalSavings()` gives NaN/inf `θ`/`κ`/`ε`, expected |
| experiments | `calibrateRhoGrid.py` (`--x0 β ω η0 X0` seeds the anchor; required at α = 0.35), `retargetCalibration.py`, `shockUniversal.py`, `shockEEOnly.py`, `sweepEpsThetaGrid.py`, `plotUniversalShock.py`, `plotBoundary.py` |
| diagnostics | `measureGrids.py`, `measureOuterSettings.py`, `diagnoseRho07.py`, `diagnoseLogCrraBoundary.py` (`--mode common|production` is the point of it) |
| tests | `test_ee.py`, `test_peeLOG.py`, `test_peeCRRA.py`, `test_peePath.py`, `test_createCopyFromt0.py`; slow: `test_calibration.py` (~12 min), `test_calibrationGrid.py` (~45 min) |

Sweeps resume from their own csv keyed on the parameter point alone: a re-run after a recalibration
silently returns old rows unless given `--force` or a new `--out` (#13). `--out` is relative to this
directory (the scripts `chdir` so `test.py` finds `data/`).

## Conventions and traps

One line each; the measurement behind each is in `archive/readmes/InformalSavings_README_2026-09-11.md`
and `notes/informalSavings_numericalDeviations.md`.

- `hRatio = h_{t,i}/h_t` vs `hηRatio = h_{t,i}η_{t,i}/h_t`: `hi`/`bi` need the first, `si_s`'s third
  term, `c2i`, `dlnc2i_dτ` the second. Checks: `∑γ_iη_i·hRatio_i = 1`, `∑γ_i·hηRatio_i = 1`.
- `χ^R` carries a *period* index: `ι_t`/`c10`/`tildec10` use `χ^R_{t+1}`, `c20`/`dv20` use `χ^R_t`.
- `Γs`/`B`/`B0`/`si_s`/`ι` report on `db['txE']` (length `T-1`); everything else length `T`.
- Two calibration variants (`ModelInformalSavings(commonX=...)`, `calibrateRhoGrid.py --commonX`, own csv
  and `instancesCommonX/`). Vector X (default): `Γ_h = 1` and `∑γ_i(η_i/X_i)^ξ = 1`, relative hours as
  data. Common X: one scalar `X`, `η_i` closed-form from income with `Γ_h = 1`, `X` solved after the root
  from the FORMAL workweek `db['h0']` (block-recursive, as the US arm); relative formal hours are a
  prediction (`predictedRelativeHours`). The informal targets `calibrationη0/X0` carry the hours-unit
  ratio `M = ∑γ_i(η_i/X_i)^ξ/Γ_h` (`Base.hoursUnitRatio`, 1 under vector X), and the data `z_j` are
  relative to the γ-weighted formal mean. `X` enters no aggregate, so β, ω, τ, K/Y and every shock
  coincide across variants to 1e-13; only `(η_i, X_i, η_0, X_0)` differ. `test_calibration.py` §6.
- Primitives are read from db; anything solve- or policy-dependent (`τ`, `θ`/`ε`, `s`/`h`, `B`, `ι`) is an
  explicit argument. `cacheParams()` is opt-in and block-scoped.
- Differentiate along `ln(1-τ_t)`, not `τ_t` (`policy.py`'s `_gradProfile`); do not simplify back.
- Smooth the policy, not the derivative; clip a smoothed policy back into `[l,u]`.
- `interpKind` and `smoothKnots` go to BOTH solvers (well-posedness choices, #7); only `nι` is keyed
  (LOG 50, CRRA 45). `shockUniversal.py` must re-solve on the interpolant it was calibrated at.
- Knots are pinned (`smoothKnots=4`, #5). `initGS` merges the caller's dict over the defaults, so passing
  `smoothKnots=None` *disables* pinning: omit the key when you have nothing to say.
- State grids anchor on `min_τ ι*(τ)` and `s*(0.3)`; do not raise `padι[0]` without re-measuring
  `atBound`; never auto-tune grids from a previous run.
- `initialStatePEE`'s masked grid scan must not become a bracketed solve on `[l,u]` (#2).
- `_stateApproxSI` evaluates continuation objects once per distinct `(s_t, ι_t)` pair (exact, 900× cheaper;
  asserted bitwise in `test_peeCRRA.py`). Do not fold it back or soften `np.unique`.
- The forward walk re-solves the state transitions (`approximatePEE(exact=True)`), it does not
  interpolate them.
- The CRRA calibration sets `interpKind='cubic'` and `nι=ns=45` explicitly; the outer finite-difference
  step is scipy's own for both solvers.
- `steadyState_CRRA_bounds` derives the bracket from `Base.ΓsCap` with geometric expansion (#7).
- `calibrate`'s `tol=1e-6` is deliberately looser than the inner solves; ~1e-4 in the parameters is the
  floor.

**Three structural results the code exploits** (would be lost by "simplifying"): under LOG the `ι_t`
fixed point depends on `τ_t` alone (1-D state approximation); under LOG `ι_{t-1}` enters `z_t` through one
rank-one term (`eq:zdecomposition`; carry `Θ_{h,t+1}(ι_t)`, not `h_{t+1}`); under CRRA the two states
unnest into two 1-D roots. Also: `l_ι > 0` strictly; grid searches use the interior grid; `dlnc2i_dτ`
stays closed-form.

**`createCopyFromt0`**: as `informalAnalytical`, plus `stateAtT0` returns `{'s0', 'ι0'}` where `ι` is
reported unlagged on `txE`, so the state entering `t0` is `report['ι'].xs(t0-1)`, or `init['ι']` when
`t0 == db['t'][0]`. Pinned in `test_createCopyFromt0.py`.

## Status

Done and verified: scaffolding and calibration (§0-2, §8, §8.1), EE solve, steady state, initial state,
`LOG` and `CRRA` policies, the path solve (§6-7), grid diagnostics, model copies, the universalisation
experiment across the ρ grid (`match`; `flat` at ρ=1 only), and the `(ε, θ)` grid. Results:
`archive/notes/informalSavings_results.md`. Departures from the `num_*.tex` specs:
`notes/informalSavings_numericalDeviations.md`, read before editing those specs.

## Open items

- `EE_report` backs its first period's lagged objects out of `initialState_solve`, which is wrong on a
  model *copy* (`c20` at `t0` off by +5.3–5.7%, `bbar` by ≤0.13% under CRRA; everything from `t0+1` on and
  the paper's Argentina outputs unaffected). Fix: let it take the lagged state. Do not quote the
  consumption columns until then.
- `κ`'s cached `db['κ']` goes stale under a varying `ε`; `shockUniversal.installEps` rewrites it, nothing
  detects an omission.
- The low-ρ tail is converged but not resolved (`verifyResidual` 1.2e-3 at ρ=0.5), and β > 1 below ρ≈0.85
  (`notes/argentina_calibrationTarget.md`).
- `initialState_solve` returns the CRRA steady-state `s` in both cases (agrees with LOG to 1e-11, not
  bitwise); deliberate.
- `lnRleadΘ` reads `α`/`power_h` at `t` though they are `t+1` objects; immaterial unless they vary.
- Not planned: a `χ^R` sweep; reducing the outer root from four parameters to two; `flat` at every ρ.
- `informalAnalytical`'s `calibrationη0/X0` still assume `M = 1` (no common-X variant there); mirror the
  `hoursUnitRatio` factor if that model ever gets one.
