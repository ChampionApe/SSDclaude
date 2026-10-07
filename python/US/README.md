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
| `test.py`, `testEU.py` | workbook loaders: `USMain_test.xlsx`; `FRMain.xlsx`/`UKMain.xlsx` via `testEU.model('FR'|'UK'[, grouping])` -- a grouping is a sheet suffix: `('UK', 'US')` the UK at US percentiles, `('FR', 'UK')` France at the UK's cuts |
| `calibrateRhoGrid.py`, `calibrateRhoGridEU.py`, `runShocksUS.py`, `runESC.py`, `runESCcrra.py`, `runESCxi.py`, `collectESCexperiments.py` | drivers |
| `stationaryApprox.py`, `stationaryApproxESC.py` | prepub checks: a stationary policy function (ν frozen at each date's value) against the exact date-specific one along the demographic path, for taxes (CRRA) and for the endogenous design (LOG, exact 2-D CRRA); `results/numerical/` |

Nine fast test suites (~6 min; `test_esc.py` alone ~235 s, both cost specs; `test_designChoicePilot.py`, the
CRRA design layer; `test_frozenSelection.py`, the tax-candidate selection) and two slow ones
(`test_escTiming.py`, the permanent timing's reference numbers, ~75 s; `test_escCRRA.py`, ~7 min),
registered in `python/runTests.py`.

## Running it

```
python\US\calibrateRhoGrid.py   [--commonX]                  # US sweep, rho 0.5..2.0 step 0.1, ~4.5 min
python\US\calibrateRhoGridEU.py --country FR|UK [--grouping US|UK] [--commonX]   # UK --grouping US = UKUS, FR --grouping UK = FRUK
python\US\runShocksUS.py        [--commonX] [--family theta] [--rho 1] [--host US|UK|UKUS]
python\US\runESC.py | runESCcrra.py    [--commonX]           # endogenous theta
python\US\collectESCexperiments.py                           # merge -> results/esc/escExperiments.csv
python\US\runESC.py --stage shocks --host UK | runESCcrra.py --exact --host UK   # French shocks on the UK, own λ
python\US\collectESCexperiments.py --host UK                 # -> escExperimentsUK.csv
```

`python/paper/` drives all of this. Sweeps write their csv after every point and resume from it; instance
directories are per sweep (pickle names are the `ρ` alone); EU sweeps need the complete US sweep of the *same
variant* first. `--host` picks the economy the characteristics are imposed on (`UK`: its own calibration with
France cut at its groups, sweep `FRUK`; `UKUS`: the UK at US percentiles), rebuilt from its sweep row and
asserted to reproduce the workbook tax. ESC drivers merge into their csvs in every stage (`runESC.mergeWrite`,
keyed on `spec`, `phi`, `commonX` and the row's identifiers); `runESCcrra.py --bracket` is per `ρ` and spec,
`--tag` writes a separate csv so two `ρ` can run in parallel.

## Invariants the code depends on

- **Zero-mass slot.** Type 0 stays in every array with `γ_0 = 0`; synthetic `η_0`/`X_0` must be finite
  (`0·NaN` poisons the FOC; `test_ee.py` perturbs the slot). `getEps` raises if `γ_0 > 0`.
- **The LOG FOC decouples across `t`** (`eq:us:model:PEELOG:decoupling`); the backward solver is still
  used. Not true under CRRA.
- **Tax candidates are compared at frozen shares** (`num_robustroot.tex`, `roots1d.selectMaxFrozen`, finding
  #18). Every candidate (both corners, every crossing) is tested and ranked on `z_t` re-evaluated at its own
  frozen shares and integrated (`LOG.objectiveFrozen`, `CRRA.objectiveFrozen`; `CRRA.focParts_t`/`zAtShares`
  split the splines from the retirees' term). Every solver reports `nCand`/`nEq`/`fallback` per state and a
  `multiplicity` summary (`policy.multiplicitySummary`); `LOG.solveRobust(check = True)` runs the full-grid
  pass on every solve; `selection = 'legacy'` reinstates the integral criterion for comparisons.
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
  (`f = φ+(1-φ)θ^p`) is the earlier wedge and the online appendix's comparison arm; `'flat'` runs only in
  the permanent stage's comparison rows, which no output prints. `f` takes the τ of the same date as its θ,
  so every call site passes it, and `dlnc2i_dτ`
  carries `(1 + τ ∂_τ ln f)` (Eq `esc:dlnc2i`). Measured in `test_esc.py`: `z_t` depends on `(τ_t, θ_t)`
  alone, so `τ_t = τPolicy_t(θ_t)`; under LOG the choice has no state and is invariant to `s_{t-1}`. Both
  fail under CRRA (`LeadedCRRA` solves the path, reports `stateSensitivity`).
- Runs under the variant `config.US['commonX']` names; `commonX` and `spec` are part of every merge key,
  in every stage of `runESC.py` and `runESCcrra.py` (#13), so the two specs' rows coexist in one csv.
- Calibration target: the design *in force* in 2020 (`leadedDesignAtT0`), by a log-grid scan of the cost
  parameter for one sign change (`WEDGE_BRACKET` per spec) then a bracketed root. At `ρ` = 1: `λ` = 8.643
  under `'size'` (`Ṽ_US` = 0.436, `f(θ*)` = 0.982, `f(0)` = 0.762), `p` = 0.4076 under `'scale'`.
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
choice (LOG, CRRA path iteration, exact 2-D) and permanent timing, and the `python/paper/` wiring. The
committed results are the final run of 2026-10-03 (`logs/finalRun1002/`, read in
`archive/notes/todo_finalRun_2026-10-02.md`): one equilibrium and no fallback at every counted state.

- Under `'size'` the UK (own `λ` = 7.26 against the US's 8.64) and the UK at US percentiles (6.52) have own
  calibrations; France has none, its observed `θ = 1` being out of reach of a cost quadratic in the
  redistribution performed. As ESC host (`--host UK`, CRRA into `escCalibrationCRRAUK.csv`) the UK's exact
  calibration scans at `ns` = 150 at `ρ` = 0.5, where `ns` = 50 does not converge. Its data caveats: `data/README.md`.
- `PermanentCRRA` puts the costless permanent choice at θ = 0 for ρ ≤ 1.3 and θ = 1 for ρ ≥ 1.4
  (`escPermanentCRRA.csv`, the online appendix's `ESC_Timing`).
- The path iteration (`method = 'path'`) values each candidate on its own re-solved path, an approximation
  reported as such (`num_esc.tex`).
