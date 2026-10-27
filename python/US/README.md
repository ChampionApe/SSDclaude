# US

`informalAnalytical` with the informal type removed (`γ_0 = 0`, no `ε`, `κ_t = p_t`, design is the scalar `θ`),
for the US, France and the UK, with the endogenous design of section 7 and the cross-country test. Derivation in
`writing/US/` (`model*.tex`, `num*.tex`; `model_esc.tex`/`num_esc.tex` for the endogenous `θ`); shared conventions
in `python/informalAnalytical/README.md`. The long version of this file, with the calibration, counterfactual and
endogenous-design details and every status measurement: `archive/readmes/US_README_2026-10-26.md`.

## Files

| | |
|---|---|
| `base.py`, `policy.py`, `model.py` | copied from `informalAnalytical` and adjusted |
| `modelFR.py` | `ModelFR(ModelUS)`, the France/UK calibration protocol |
| `shocks.py` | counterfactuals: `shockedCopy`, one function per scenario |
| `policyESC.py`, `modelESC.py` | endogenous `θ`: `LeadedLOG`, `LeadedCRRA`, `LeadedCRRA2D` (the published CRRA solver, `designRule = 'root'`, alg `esc:crra2D`), `PermanentLOG/CRRA`, `ModelESC` |
| `policyESCpilot.py` | sandbox: the first-order-condition design layer (`esc:crra2Dfoc`, not adopted: finding #19), run by `test_designChoicePilot.py` |
| `test.py`, `testEU.py` | workbook loaders: `USMain_test.xlsx`; `testEU.model('FR'\|'UK')` (each workbook's own sheets; the regrouped pairs are not read); `test.reading(M)`, the Medicare reading |
| `calibrateRhoGrid.py`, `calibrateRhoGridEU.py`, `runShocksUS.py`, `runShocksXi.py`, `runESC.py`, `runESCcrra.py`, `runESCxi.py`, `collectESCexperiments.py` | drivers |
| `oecd26.py`, `runOECD26.py` | the cross-country test: `ModelOECD(ModelESC)` from `data/oecd29*.csv`; anchor, layer 1 (anchor's `ω`, cost), layer 2 (own `ω`), turnout `cps`/`cses`, cost `size`/`sizePiR`/`none`, β `common`/`commonR` (set to the anchor's `R2020`), rows keyed on an inputs hash -> `results/oecd26/` |
| `stationaryApprox.py`, `stationaryApproxESC.py` | prepub: stationary against date-specific policy functions (taxes; the design) -> `results/numerical/` |
| `runHorizon.py` | appendix D, not wired: other horizons and the steady-state terminal condition, FOC residuals off the grid, a jump scan, converged τ-derivatives -> `results/numerical/US_{horizon,horizonDesign,residuals,jumps,derivativeScheme}.csv` |
| `c5Numbers.py` | the review response's smaller numbers -> `results/numerical/C5_*.csv` (`US_TaxState` and `US_Strategic` read two) |

Tests, registered in `python/runTests.py`: twelve fast suites (`test_ee`, `test_invariance`, `test_crra`,
`test_calibration`, `test_fr`, `test_eu`, `test_esc`, `test_frozenSelection`, `test_designChoicePilot`, `test_counts`,
`test_oecd26`, `test_gridConvergence`) and three slow ones (`test_escTiming`, `test_escCRRA`, `test_oecd26Anchor`).

## Running it

```
python\US\calibrateRhoGrid.py [--commonX] [--medicare 0.029] ; calibrateRhoGridEU.py --country FR|UK [--commonX]
python\US\runShocksUS.py [--commonX] [--family theta] [--rho 1] [--medicare 0.029] ; runShocksXi.py [--xi 0.2 0.4]
python\US\runESC.py | runESCcrra.py --exact [--commonX]   # LOG | exact CRRA; --host UK --stage calib: the UK's own cost
python\US\runESC.py --stage pathHost|corner --spec size --phi 0.5 --commonX     # escPathHost.csv | escCornerSlope.csv
python\US\runESC.py --stage calib path shocks --spec sizePiR --tag Costs --scenarios baseline mild acute --commonX
python\US\collectESCexperiments.py [--costs]                                   # -> escExperiments.csv | escAgeingCosts.csv
python\US\runOECD26.py [--stage ...] [--turnout cps cses] [--spec size sizePiR none] [--betaRule common commonR] [--coarse]
python\US\c5Numbers.py selfcheck|a1|a9|loss|lambda|index|design|a13|strategic ; designCRRA --rho 0.5
```

`python/paper/` drives all of this (`REPLICATION.md` §3 for the runs it does not). Sweeps resume from their own csv
(finding #13: `--force` after a recalibration); EU sweeps need the complete US sweep of the same variant first.
ESC drivers merge into their csvs (`runESC.mergeWrite`, keyed on `spec`, `phi`, `commonX` and the row's ids).

## Invariants the code depends on

- **`Ushare0` scales `θ`**: `θ = (1 - Ushare0)·θ_P` (`getθ`); 0 in every workbook, Medicare's share in `test.reading`.
- **Zero-mass slot.** Type 0 stays in every array with `γ_0 = 0`; synthetic `η_0`/`X_0` must be finite (`0·NaN`).
- **The LOG FOC decouples across `t`** (`eq:us:model:PEELOG:decoupling`); not true under CRRA.
- **The log tax's gradient solve stays below τ = 1** (`LOG._upper`, `u` = 1 − 1e-4; `test_oecd26.py` B).
- **Tax candidates are compared at frozen shares** (`num_robustroot.tex`, finding #18); every solver reports
  `nCand`/`nEq`/`fallback` and every driver row writes `multiplicityColumns` (−1 where no tax is selected).
- **The CRRA design is chosen at frozen savings shares** (alg `esc:crra2D`, findings #11, #18): one scalar `a`,
  closed by a root of `eq:esc:aResidual`; counts `nEqθ`/`nBrθ`/`fallbackθ` per state.
- **Two invariances** (scale, hours unit; `test_invariance.py`), both normalised in `addEigenVectors`: `Γ_h = 1`,
  `μ = 1`, so `h̄ = h` under vector `X` by units, not identity (finding #15). `h̄` is reported against a reference.
- **Calibration**: `R_{t_0}` replaces the savings rate, `θ` is closed-form from the replacement-rate ratio
  (`eq:calibration:theta`); variant B (`commonX=True`, the paper's) pins one scalar `X` by average hours
  (`solveCommonX`; `zηiNormalized` is load-bearing there).
- **Grid settings** pinned, never adaptive (#5): linear interpolant, `smoothKnots=4`, `ns=150` (50 for a cost
  scan), `gradKnotSpacing=0.04` (`CRRA._gradProfile`, least-squares cubic in ln(1−τ); #7, #20); the CRRA
  steady-state bracket tracks `Base.ΓsCap` (#7, `test_crra.py`).
- **France and the UK** (`modelFR.py`): `β` imposed at the US value, hours targeted by `rescaleX`, so `Γ_h` ends at
  `λ`, not 1; `testEU.load` sets `R0 = NaN` so a stray `ModelUS.calibrate` fails; `defaultSGrid`'s 1e-4 floor
  must stay absolute (`report['hoursDrift']` is asserted).
- **Counterfactuals** are new equilibrium paths from their own steady state, read at 2020; the income row holds
  `θ`, composites re-install the pin (#9); `shocks.ηLevel` preserves the host's `Γ_h`.
- **The ESC cost**: `'size'` (the paper's, `f = exp(-½ λ τ Ṽ (1-θ)²)`, `λ` in the `wedgeP` slot and column `p`),
  `'scale'` (the earlier wedge, comparison arm), `'sizePiR'` (`ε·Π_t/R_t`, ε in `p`; only `solvePEE_*` and the leaded
  solvers iterate `π`, the others refuse it; a driver reads each object off the solve that iterated to it:
  `runOECD26.readouts`, `runESC.usWedgeRow`); `f` takes the τ of its own date; `commonX` and `spec` are in every
  merge key (#13).
- **The cross-country csvs** are keyed on (turnout, spec, phi, commonX, betaRule[, iso3]); the anchor is always
  `'common'`; a csv without `betaRule` is read, and migrated at its next write, as `'common'` (`runOECD26.migrate`).
- **`LeadedCRRA2D`**: 13 θ-state nodes with Catmull-Rom policies along θ (`Interp2D`; linear is 0.011 off, #19), 41
  candidates (`config.US['esc']['nCand2D']`), which set the design's third decimal; the `s` grid does not.
- **Permanent timing** pins the savings ratio at the fixed point `θ*`, not at the incumbent (#11/#11b).

## Status

Implemented and tested: EE, LOG and CRRA PEE, both calibration variants, `ModelFR`, ρ sweeps of the US, its Medicare
reading, France and the UK in both variants, three counterfactual families in both readings, the endogenous `θ` (LOG
leaded, exact 2-D CRRA, path iteration, permanent timing), the Π-inclusive cost, the cross-country test (its `sizePiR`,
`none` and `commonR` variants run 2026-10-27, R6), appendix D's checks and the `python/paper/` wiring. The UK as a
second host retired 2026-10-27 (R7, `archive/results/ukHost_2026-10/`); it keeps its sweep, own cost and deep-test rows.

The results are C6's reruns of 2026-10-25 on the pension-only calibration of 2026-10-23 (C1), under the converged
CRRA τ-derivatives and design grids (`test_gridConvergence.py`); every row that reads France's `ν` is C7's rerun of
2026-10-26 (`logs/C7/`). Numbers, old → new: `archive/notes/reviewResponse_2026-10/ledger_C{1..7}.md`. At ρ = 1: `θ*` =
0.7278, `λ` = 11.345 (`'size'`; 25.082 and 2.643 at ρ = 0.5 and 2), the UK's own 7.74; France has no interior crossing.

## Open

- The path iteration (`method = path`) and the flat-only variant's leaded calibration were last run on 2026-10-03
  at the earlier calibration (`θ*` = 0.738); they are cross-checks no exhibit prints (`num_esc.tex`, checks).
- One design-layer fallback state: `escShocksCRRA.csv`, ρ = 0.5, `'scale'`, French leisure, design chosen.
- A13's myopic/Markov split needs a new model function (deferred; TODO C13).
- Data caveats of the UK and France: `data/README.md`.
