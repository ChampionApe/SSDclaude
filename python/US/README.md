# US

`informalAnalytical` with the informal type removed (`γ_0 = 0`, no `ε`, `κ_t = p_t`, design is the scalar
`θ`), for the US, France and the UK. Derivation in `writing/US/` (`model*.tex`, `num*.tex`;
`model_esc.tex`/`num_esc.tex` for the endogenous `θ`). Shared conventions are documented in
`python/informalAnalytical/README.md`. Measurements and the pre-cut long version of this file:
`archive/readmes/US_README_2026-09-11.md`, `archive/notes/us_measurements.md`.

## Files

| | |
|---|---|
| `base.py`, `policy.py`, `model.py` | copied from `informalAnalytical` and adjusted |
| `modelFR.py` | `ModelFR(ModelUS)`, the France/UK calibration protocol |
| `shocks.py` | counterfactual machinery: `shockedCopy`, one function per scenario |
| `policyESC.py`, `modelESC.py` | endogenous `θ`: `LeadedLOG`, `LeadedCRRA`, `LeadedCRRA2D` (design layer `designRule = 'root'`, alg `esc:crra2D`; `'legacy'` the earlier one), `PermanentLOG/CRRA`, `ModelESC` |
| `policyESCpilot.py` | sandbox: the first-order-condition design layer (`LeadedCRRA2DFOC`, alg `esc:crra2Dfoc`, not adopted: finding #19) and the checks `test_designChoicePilot.py` runs; the pilot's driver is `archive/code/US/pilotDesignChoice.py` |
| `test.py`, `testEU.py` | workbook loaders: `USMain_test.xlsx`; `FRMain.xlsx`/`UKMain.xlsx` via `testEU.model('FR'|'UK'[, grouping])` -- a grouping is a sheet suffix: `('UK', 'US')` the UK at US percentiles, `('FR', 'UK')` France at the UK's cuts. `test.reading(M)`: the US with Medicare spending M in `τ0` and as a flat share of `θ` (the online appendix's 'transfers to the old'; sweep `USMedicare`) |
| `calibrateRhoGrid.py`, `calibrateRhoGridEU.py`, `runShocksUS.py`, `runESC.py`, `runESCcrra.py`, `runESCxi.py`, `collectESCexperiments.py` | drivers |
| `oecd26.py`, `runOECD26.py` | the cross-country test: `ModelOECD(ModelESC)` built from `data/oecd29*.csv` (groups at the U.S. percentiles, `θ = 2 - 1/I` clipped, WPP `ν`, figure 1.1's cash spending, `β` of the no-cost U.S. sweep imposed, `ω` alone calibrated); the driver's anchor (the U.S. at these inputs, `ω` and `λ` calibrated), layer 1 (every country at the anchor's `ω`, `λ`) and layer 2 (`ω` per country), turnout `cps`/`cses`, rows keyed on an inputs hash -> `results/oecd26/` |
| `stationaryApprox.py`, `stationaryApproxESC.py` | prepub checks: a stationary policy function (ν frozen at each date's value) against the exact date-specific one along the demographic path, for taxes (CRRA) and for the endogenous design (LOG, exact 2-D CRRA); `results/numerical/` |
| `runHorizon.py` | appendix D, not wired: the calibrated economy at T = 2140, 2200, 2290 and under the steady-state terminal condition (design given and chosen), the tax rule's FOC residuals off the grid, a jump scan, and whole solves under converged τ-derivatives; `results/numerical/US_{horizon,horizonDesign,residuals,jumps,derivativeScheme}.csv` |
| `c5Numbers.py` | the review response's smaller numbers (package C5): C.1's critical turnout ratio, the ranking of the counterfactuals across ρ, the marginal loss, λ against elasticities, index units, the design condition's response to inequality, τ_2020(s_2019); `results/numerical/C5_*.csv`, no paper output |

Ten fast test suites (~6.5 min; `test_esc.py` alone ~235 s, both cost specs; `test_designChoicePilot.py`, the
CRRA design layer; `test_frozenSelection.py`, the tax-candidate selection; `test_counts.py`, the counts in every
driver's rows; `test_oecd26.py`, the cross-country loader and layers, ~2 min) and three slow ones
(`test_escTiming.py`, the permanent timing's reference numbers, ~75 s; `test_escCRRA.py`, ~7 min;
`test_oecd26Anchor.py`, the cross-country anchor, ~5 min), registered in `python/runTests.py`.

## Running it

```
python\US\calibrateRhoGrid.py   [--commonX]                  # US sweep, rho 0.5..2.0 step 0.1, ~4.5 min
python\US\calibrateRhoGridEU.py --country FR|UK [--grouping US|UK] [--commonX]   # UK --grouping US = UKUS, FR --grouping UK = FRUK
python\US\runShocksUS.py        [--commonX] [--family theta] [--rho 1] [--host US|UK|UKUS]
python\US\runESC.py | runESCcrra.py    [--commonX]           # endogenous theta
python\US\collectESCexperiments.py                           # merge -> results/esc/escExperiments.csv
python\US\runESC.py --stage shocks --host UK | runESCcrra.py --exact --host UK   # acute ageing and French shocks on the UK, own λ
python\US\collectESCexperiments.py --host UK                 # -> escExperimentsUK.csv
python\US\runESC.py --stage pathHost --spec size --phi 0.5 --commonX   # the design path of France and the UK -> escPathHost.csv
python\US\runShocksXi.py [--xi 0.2 0.4]                      # the US shocks at other ξ (LOG, common X) -> US_shocksXiCommonX.csv
python\US\calibrateRhoGrid.py --medicare 0.029 | runShocksUS.py --medicare 0.029   # the Medicare reading -> USMedicare_*
python\US\runESC.py --stage calib path shocks --spec sizePiR --tag Costs --scenarios baseline mild acute --commonX
python\US\collectESCexperiments.py --costs                   # ageing under the three costs -> escAgeingCosts.csv
python\US\runOECD26.py [--stage anchor layer1 layer2] [--turnout cps cses] [--coarse]   # the cross-country test -> results/oecd26/
python\US\c5Numbers.py selfcheck|a1|a9|loss|lambda|index|design|a13 ; designCRRA --rho 0.5   # -> results/numerical/C5_*.csv
```

`--scenarios` limits the ESC shocks stage of either driver to some scenarios (the rows of the others on disk are
kept); France's own row runs with a French scenario only. `runShocksXi.py` recalibrates the US and France at each
ξ and checks its workbook-ξ rows against `US_shocksCommonX.csv` before any other ξ.

`python/paper/` drives all of this. Sweeps write their csv after every point and resume from it; instance
directories are per sweep (pickle names are the `ρ` alone); EU sweeps need the complete US sweep of the *same
variant* first. `--host` picks the economy the characteristics are imposed on (`UK`: its own calibration with
France cut at its groups, sweep `FRUK`; `UKUS`: the UK at US percentiles), rebuilt from its sweep row and
asserted to reproduce the workbook tax. ESC drivers merge into their csvs in every stage (`runESC.mergeWrite`,
keyed on `spec`, `phi`, `commonX` and the row's identifiers); `runESCcrra.py --bracket` is per `ρ` and spec,
`--tag` writes a separate csv so two `ρ` can run in parallel.

## Invariants the code depends on

- **`Ushare0` scales `θ`**: `θ = (1 - Ushare0)·θ_P` (`getθ`), the flat share of transfers to the old outside the
  pension formula; 0 in every workbook, Medicare's share in `test.reading`. It is also the inert `ε` (`getEps`).
- **Zero-mass slot.** Type 0 stays in every array with `γ_0 = 0`; synthetic `η_0`/`X_0` must be finite
  (`0·NaN` poisons the FOC; `test_ee.py` perturbs the slot). `getEps` raises if `γ_0 > 0`.
- **The LOG FOC decouples across `t`** (`eq:us:model:PEELOG:decoupling`); the backward solver is still
  used. Not true under CRRA.
- **Tax candidates are compared at frozen shares** (`num_robustroot.tex`, `roots1d.selectMaxFrozen`, finding
  #18). Every candidate (both corners, every crossing) is tested and ranked on `z_t` re-evaluated at its own
  frozen shares and integrated (`LOG.objectiveFrozen`, `CRRA.objectiveFrozen`; `CRRA.focParts_t`/`zAtShares`
  split the splines from the retirees' term). Every solver reports `nCand`/`nEq`/`fallback` per state and a
  `multiplicity` summary (`policy.multiplicitySummary`) that every driver row writes (`multiplicityColumns`;
  -1 where no tax is selected: the 'ee' readings, the root design layer's tax step);
  `LOG.solveRobust(check = True)` runs the full-grid pass on every solve; `selection = 'legacy'` reinstates
  the integral criterion for comparisons.
- **The CRRA design is chosen at frozen savings shares** (`num_esc.tex` alg `esc:crra2D`, findings #11, #18).
  `LeadedCRRA2D._chooseRoot` values every candidate design, and the tax it is paired with, at one scalar `a`
  (the one-parameter family of shares, `aOf`/`sharesFrom`), and closes `a` by a root of `eq:esc:aResidual` on
  a 5-node grid with an Illinois secant. Counts `nEqθ`/`nBrθ`/`fallbackθ` per state; the drivers write them
  as non-key columns. `'legacy'` valued each candidate at its own consistent shares and stays for comparisons.
- **Two invariances**: scale (`y^η → λy^η`, normalised away by `Γ_h = 1`) and hours unit (`y^x → μy^x`,
  moves only `h_i` and `h̄`). `test_invariance.py`. Both normalisations are spent in `addEigenVectors`:
  `Γ_h = 1` and `μ = ∑γ_i y^x_i = 1` (so `h̄ = h` under vector `X`, a coincidence of units, not an identity:
  finding #15). **`h̄` is the only object comparable to an observed workweek, and under vector `X` its level
  is still not data**: report it against a reference.

## Calibration

`R_{t_0}` replaces the savings rate as a target, `θ` is closed-form from the replacement-rate ratio, and
the two variants differ only in how the hours unit is fixed. Variant A (`commonX=False`, default): vector
`X_i` from relative hours (eigenvector system), outer loop `β, ω` against `R_{t_0}, τ_{t_0}`. Variant B
(`commonX=True`, the paper's): one scalar `X` pinned by the level of average hours, `X` closed-form after the
2×2 root (`solveCommonX`, `verifyCommonX`); relative hours become a prediction. `zηiNormalized` is
load-bearing under B.

Settings: linear interpolant, `smoothKnots=4` (pinned, never adaptive: finding #5), `ns=150` for
calibration against 50 for a solve. `steadyState_CRRA_bounds` ties the bracket to `Base.ΓsCap` with
geometric expansion (#7); `test_crra.py` asserts it tracks the cap. Health checks: `R`, `τ` constant down
the csv; `β`, `ω`, `sr`, `h` agree across variants to ~1e-13; `h̄` pinned under `--commonX`.

**France and the UK (`modelFR.py`).** `β` is imposed at the US value at the same `ρ` (1-D root over `ω`;
`R` becomes a prediction) and average hours are targeted relative to the US by a common rescaling of every
`X_i` (`rescaleX`), so **`Γ_h` ends at `λ`, not 1**, on a calibrated `ModelFR`; `calibrate` resets to the
`Γ_h = 1` baseline first so `λ` is a level (`test_fr.py`). France's `θ = 1` needs no code (`getθ` returns
1 when `RR0 = 1`); the UK's US-percentile regrouping is not interchangeable with its own (`θ` 0.560 vs
0.543). `testEU.load` sets `db['R0'] = NaN` so a stray `ModelUS.calibrate` fails loudly. Under CRRA the
rescaling drifts because `defaultSGrid` floors the state grid at an absolute `1e-4` (must stay absolute);
`report['hoursDrift']` is asserted at `1e-8`/`1e-3`.

## Counterfactuals (`shocks.py`, `runShocksUS.py`)

Every experiment is a new equilibrium path over the whole horizon from its own steady state, read at
`db['t0']` = 2020, built by `shockedCopy` (deepcopy, warm starts cleared); reported as full effect and as
economic-equilibrium effect (`τ` held at the baseline path). Families: `theta` (`θ` = 0, 1), `ageing`
(mild, acute), `french` (income distribution `η`, leisure `X`, voting `μ`, all three), and France's own
calibration (`--noFrance` skips).

- The csv carries `sr` = `s/(w·h)` and `srOverY` = `s/Y`; the paper prints `s/Y`. The workweek is
  normalised against that `ρ`'s own baseline. `db['dates']` is valid on these copies.
- `η` carries income distribution, the level of `X` leisure, `μ` voting (profile only). The income row
  carries France's `η` *profile* at the US productivity *level* (`shocks.ηLevel` rescales so `Γ_h = 1` at
  the US `X`), the leisure row the compensating scale, so the two compose to `frAll`. `test_esc.py`.
- The income row HOLDS `θ` at the US design (`--freeTheta` keeps the re-deriving reading). Composites
  re-install the pin at the end because the last `updateAuxPars` wins (#9; asserted in `test_esc.py`).
- `shocks.ηLevel` preserves the HOST's `Γ_h`, which is 1 on `ModelUS` but `λ` on a calibrated vector-X
  `ModelFR`; resetting it to 1 would undo the UK's hours calibration (`test_eu.py`).

## Endogenous `θ`

- The leaded choice under a deadweight cost on benefits, `Base.fWedge(θ, τ, t, lag)` with three specs
  (`writing/US/model_esc.tex`, Eq `esc:AB`). **`'size'` is the paper's**: `f = exp(-½ λ τ Ṽ (1-θ)²)`, the
  Harberger loss of the flat component's implicit taxes, `Ṽ = Σ γ_i (y_i-1)²/y_i` (`Base.Vtilde`, zero-mass
  slot masked), `λ` in the `wedgeP` slot and the csv column `p`, `φ` a dummy key. `'scale'`
  (`f = φ+(1-φ)θ^p`) is the earlier wedge and the online appendix's comparison arm; `'sizePiR'` is `'size'`
  with `λ·π_t`, `π_t = Π_t/R_t` of `f`'s date (`Base.wedgeΠR`: lag `'[t-1]'` reads `π_t`, lag `''` `π_{t+1}`),
  the Π-inclusive cost of section 7's cost variants: `ModelESC._ΠRFixedPoint` solves `π` to the path's own
  (households and voters take it as given); only `solvePEE_*`, `solveLeaded`, `leadedDesignAtT0` and
  `solveLeaded2D` iterate it, the other solvers refuse the spec; `'flat'` runs only in
  the permanent stage's comparison rows, which no output prints. `f` takes the τ of the same date as its θ,
  so every call site passes it, and `dlnc2i_dτ`
  carries `(1 + τ ∂_τ ln f)` (Eq `esc:dlnc2i`). Measured in `test_esc.py`: `z_t` depends on `(τ_t, θ_t)`
  alone, so `τ_t = τPolicy_t(θ_t)`; under LOG the choice has no state and is invariant to `s_{t-1}`. Both
  fail under CRRA (`LeadedCRRA` solves the path, reports `stateSensitivity`).
- Runs under the variant `config.US['commonX']` names; `commonX` and `spec` are part of every merge key,
  in every stage of `runESC.py` and `runESCcrra.py` (#13), so the two specs' rows coexist in one csv.
- Calibration target: the design *in force* in 2020 (`leadedDesignAtT0`), by a log-grid scan of the cost
  parameter for one sign change (`WEDGE_BRACKET` per spec) then a bracketed root. At `ρ` = 1: `λ` = 11.564
  under `'size'` (`Ṽ_US` = 0.436, `f(θ*)` = 0.981, `f(0)` = 0.767), `p` = 0.4146 under `'scale'`.
- `LeadedCRRA2D` is the exact 2-D recursion and the PUBLISHED CRRA method (`runESCcrra.py --exact`,
  `method` = exact rows; the path iteration's rows stay under `method` = path as the cross-check). Pinned
  periods collapse the candidate grid inside the recursion; the θ-state grid matters (13 nodes), the `s`
  grid does not (50 vs 150: 3e-5 in θ); the objective is flat near its maximum, so the candidate grid
  sets the third decimal of the design (41 nodes, `config.US['esc']['nCand2D']`). ~40 s per period at
  `ns=150`; the cost calibration scans at `ns=50` and refines at 150.
- `ModelESC.sequentialFOC`: the costless sequential FOC on a solved path (`test_esc.py` at ρ = 1,
  `runESCcrra.py --stage sequential` under CRRA). Negative on [0,1] at every dated period.
- Permanent timing: the joint `(τ_{t0}, θ)` choice concentrates to a 1-D search; the savings ratio is
  pinned at the fixed point `θ*` (`solveFixedPoint`, default), not at the incumbent (#11/#11b).
- **Frisch robustness** (`runESCxi.py`, LOG, common X): recalibrated at ξ = 0.2/0.3/0.4 (β, ω, X, λ; θ* and
  `Ṽ` ξ-free, asserted); `results/esc/escXiRobustness.csv`, ξ = 0.3 reproduces the published rows bitwise.

## Status

Implemented and tested: EE, LOG and CRRA PEE, both calibration variants, `ModelFR`, ρ sweeps for all four
calibrations in both variants, three counterfactual families in both readings, the endogenous-`θ` leaded
choice (LOG, CRRA path iteration, exact 2-D) and permanent timing, the Π-inclusive cost and the Medicare
reading, and the `python/paper/` wiring. The results are the pension-only run of 2026-10-23 (C1 of the review
response, `logs/C1/`, numbers in `notes/ledger_C1.md`; the run of 2026-10-03 is HEAD's).

- Under `'size'` the UK (own `λ` = 7.79 against the US's 11.56 under LOG) and the UK at US percentiles (7.05) have own
  calibrations; France has none, its observed `θ = 1` being out of reach of a cost quadratic in the
  redistribution performed. As ESC host (`--host UK`, CRRA into `escCalibrationCRRAUK.csv`) the UK's exact
  calibration scans at `ns` = 150 at `ρ` = 0.5, where `ns` = 50 does not converge. Its data caveats: `data/README.md`.
- At ρ = 2 (and for some λ at 0.5) the `ns` = 50 CRRA tax solve jumps by ~1e-5 in τ, which can stop the (β, ω) root
  at a scan node; `calibrateWedge` then brackets between the finite neighbours, and `'sizePiR'` scans at `ns` = 150.
- Appendix D (`runHorizon.py`, `notes/ledger_C4.md`): from T = 2200 to 2140, 2290 or the steady-state terminal condition
  τ_2020 moves ≤ 0.0012 p.p. and the chosen θ_2020 ≤ 6e-5 (LOG rows identical); a scan over ω ± 0.1% at `ns` = 50
  jumps by up to 2e-4 in τ_2020 (none at 150), inside that grid's path residual (6.9e-4).
- Open: the CRRA tax condition's τ-derivatives are not converged. `CRRA.focParts_t` fits `griddedGradient1D` along τ
  at its default s = 1e-4 (adaptive knots, 101 nodes), where `InformalSavings._gradProfile` uses ln(1−τ) and s = 0
  (#7): against converged derivatives the root on the path moves 0.17 (ρ = 0.5) and 0.37 p.p. (ρ = 2), and at the
  calibrated parameters the θ = 0 − θ = 1 tax gap is 8.96 / 1.99 p.p. against 9.34 / 2.12. `LeadedCRRA2D` inherits it.
- `PermanentCRRA` puts the costless permanent choice at θ = 1 for every ρ ≥ 1.1 (θ = 0 under LOG; 2026-10-03: θ = 0
  up to ρ = 1.3) (`escPermanentCRRA.csv`, the online appendix's `ESC_Timing`).
- The path iteration (`method = 'path'`) values each candidate on its own re-solved path, an approximation
  reported as such (`num_esc.tex`).
- The cross-country test (`oecd26.py`, `runOECD26.py`, stage (ii) entry `oecd26`): run 2026-10-24 at the pension-only
  U.S. calibration (β = 0.6555), fine grids, both turnout readings, the 29 (`results/oecd26/`, `logs/C3/`, 18 min):
  anchor `λ` = 11.22 (cps) and 13.58 (cses); one equilibrium and no fallback in every row; numbers in
  `notes/ledger_C3.md`. At the inputs of the run of 2026-10-03 the code reproduces that run's `λ` and G.1's rows.
- Open: `LeadedLOG` reads the anticipated tax function T_{t+1}(θ) off a linear table on its 41-node design grid, which
  biases the log design choice by about −0.005 at the calibration (θ_2020 0.7278 against 0.7324 with T solved at every
  candidate, 0.7323 at 321 nodes; finding #19); the exact CRRA recursion's 13-node θ-state grid is unmeasured
  (`notes/ledger_C5.md`, 2026-10-24).
