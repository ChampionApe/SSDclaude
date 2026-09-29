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
| `policyESC.py`, `modelESC.py` | endogenous `θ`: `LeadedLOG`, `LeadedCRRA`, `LeadedCRRA2D`, `PermanentLOG/CRRA`, `ModelESC` |
| `thetaStakes.py` | diagnostic: who gains from a marginal change in `θ_{t+1}`; showed the leaded choice needs a wedge |
| `test.py`, `testEU.py` | workbook loaders: `USMain_test.xlsx`; `FRMain.xlsx`/`UKMain.xlsx` via `testEU.model('FR'|'UK'[, grouping])` -- a grouping is a sheet suffix: `('UK', 'US')` the UK at US percentiles, `('FR', 'UK')` France at the UK's cuts (sheets `heterogeneityUK`/`calibrationUK`) |
| `calibrateRhoGrid.py`, `calibrateRhoGridEU.py`, `runShocksUS.py`, `runESC.py`, `runESCcrra.py`, `collectESCexperiments.py` | drivers |
| `stationaryApprox.py`, `stationaryApproxESC.py` | prepub checks: a stationary policy function (ν frozen at each date's value) against the exact date-specific one along the demographic path, for taxes (CRRA) and for the endogenous design (LOG, exact 2-D CRRA); `results/numerical/` |

Eight fast test suites (~5 min; `test_esc.py` alone ~235 s, both cost specs) and two slow ones
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

Sweeps write their csv after every point and resume from it; `python/paper/` drives all of this. Instance
directories are per sweep (pickle names are the `ρ` alone). `runShocksUS.py --host` picks the economy the
characteristics are imposed on: `US` (default), `UK` (the UK's own calibration, France cut at the UK's groups,
sweep `FRUK`) or `UKUS` (the UK at US percentiles, France as is); the host is rebuilt from its sweep row
(`hostModel`) and its baseline must reproduce the workbook tax, which the script asserts. EU sweeps need the complete US sweep of the
*same variant* first (`USReference` matches `ρ` exactly; `--maxHalvings` defaults to 0 there). ESC drivers
merge into their csvs in every stage (`runESC.mergeWrite`, keyed on `spec`, `phi`, `commonX` and the row's
own identifiers); `runESCcrra.py --bracket` is per `ρ` and per spec, because the calibrated cost falls
steeply in `ρ` (`config.US['esc']['bracket']` records the paper's; `runESCcrra.py --tag` writes to a
separate csv, used to run two `ρ` in parallel without racing on one file).

## Invariants the code depends on

- **Zero-mass slot.** Type 0 stays in every array with `γ_0 = 0`; synthetic `η_0`/`X_0` must be finite
  (`0·NaN` poisons the FOC; `test_ee.py` perturbs the slot). `getEps` raises if `γ_0 > 0`.
- **The LOG FOC decouples across `t`** (`eq:us:model:PEELOG:decoupling`); the backward solver is still
  used. Not true under CRRA.
- **Two invariances**: scale (`y^η → λy^η`, normalised away by `Γ_h = 1`) and hours unit (`y^x → μy^x`,
  moves only `h_i` and `h̄`). `test_invariance.py`. Both normalisations are spent in
  `addEigenVectors`: `Γ_h = 1` and `μ = ∑γ_i y^x_i = 1`, the latter since 2026-09-12 (so `h̄ = h` under
  vector `X` -- a coincidence of units, not an identity: finding #15 -- and one hours unit per country). **`h̄` is the only object comparable to an observed
  workweek, and under vector `X` its level is still not data**: report it against a reference.

## Calibration

`R_{t_0}` replaces the savings rate as a target, `θ` is closed-form from the replacement-rate ratio, and
the two variants differ only in how the hours unit is fixed. Variant A (`commonX=False`, default): vector
`X_i` from relative hours (eigenvector system), outer loop `β, ω` against `R_{t_0}, τ_{t_0}`. Variant B
(`commonX=True`): one scalar `X` pinned by the level of average hours, `X` closed-form after the 2×2 root
(`solveCommonX`, `verifyCommonX`); relative hours become a prediction. `zηiNormalized` is load-bearing
under B.

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
  (`writing/US/model_esc.tex`, Eq `esc:AB`). **`'size'` is the paper's** (2026-09-24): `f = exp(-½ λ τ Ṽ
  (1-θ)²)`, the Harberger loss of the flat component's implicit taxes, `Ṽ = Σ γ_i (y_i-1)²/y_i`
  (`Base.Vtilde`, zero-mass slot masked), `λ` in the `wedgeP` slot and the csv column `p`, `φ` a dummy key.
  `'scale'` (`f = φ+(1-φ)θ^p`) is the previous wedge and the appendix comparison arm; `'flat'` is
  implemented but not run. `f` takes the τ of the same date as its θ, so every call site passes it, and
  `dlnc2i_dτ` carries `(1 + τ ∂_τ ln f)` (Eq `esc:dlnc2i`); under the other specs τ is ignored and those
  paths are bit-identical to before. Measured in `test_esc.py`: `z_t` depends on `(τ_t, θ_t)` alone, so
  `τ_t = τPolicy_t(θ_t)`; under LOG the choice has no state and is invariant to `s_{t-1}`. Both fail under
  CRRA (`LeadedCRRA` solves the path, reports `stateSensitivity`).
- Runs under the variant `config.US['commonX']` names; `commonX` and `spec` are part of every merge key,
  in every stage of `runESC.py` and `runESCcrra.py` (#13), so the two specs' rows coexist in one csv.
- Calibration target: the design *in force* in 2020 (`leadedDesignAtT0`), by a log-grid scan of the cost
  parameter for one sign change (`WEDGE_BRACKET` per spec) then a bracketed root. At `ρ` = 1: `λ` = 8.643
  under `'size'` (`Ṽ_US` = 0.436, `f(θ*)` = 0.982, `f(0)` = 0.762), `p` = 0.4076 under `'scale'`. The
  calibrated parameter and the chosen design are bit-identical across the calibration variants; only
  exogenous rows that swap `η` move (`notes/esc_experiments_acrossRho.md`).
- `LeadedCRRA2D` is the exact 2-D recursion and the PUBLISHED CRRA method (`runESCcrra.py --exact`,
  `method` = exact rows; the path iteration's rows stay under `method` = path as the cross-check). Pinned
  periods collapse the candidate grid inside the recursion; the θ-state grid matters (13 nodes), the `s`
  grid does not (50 vs 150: 3e-5 in θ); the objective is flat near its maximum, so the candidate grid
  sets the third decimal of the design (41 nodes, `config.US['esc']['nCand2D']`). ~40 s per period at
  `ns=150`; the wedge calibration scans at `ns=50` and refines at 150.
- `ModelESC.sequentialFOC`: the costless sequential FOC on a solved path (`test_esc.py` at ρ = 1,
  `runESCcrra.py --stage sequential` under CRRA). Negative on [0,1] at every dated period.
- Permanent timing: the joint `(τ_{t0}, θ)` choice concentrates to a 1-D search; the savings ratio is
  pinned at the fixed point `θ*` (`solveFixedPoint`, default), not at the incumbent (#11/#11b).

## Status

Implemented and tested: EE, LOG and CRRA PEE, both calibration variants, `ModelFR`, ρ sweeps for all four
calibrations in both variants, three counterfactual families in both readings, the endogenous-`θ` leaded
choice (LOG, CRRA path iteration, exact 2-D) and permanent timing, and the `python/paper/` wiring.
Under `'size'` the UK (own `λ` = 7.26 against the US's 8.64) and the UK-at-US-percentiles (6.52) have
own calibrations; France has none, by construction: its observed design is the `θ = 1` corner, and under a
cost quadratic in the redistribution performed the first unit of redistribution is free at the margin, so
no finite `λ` places the choice there (`results/esc/escCountry.csv`). **The UK as ESC host**
(2026-09-29): `--host UK` in both ESC drivers runs the French scenarios on the UK at its OWN `λ` (LOG from
`escCountry.csv`; CRRA calibrated by the exact recursion into `escCalibrationCRRAUK.csv`), France cut at
the UK's groups; every UK file carries the host in its name. At `ρ` = 0.5 the UK's exact calibration must
scan at `ns` = 150: its β-imposed calibration does not converge on the `ns` = 50 grid there.

**Open**: `PermanentCRRA` (run 2026-09-11, `results/esc/escPermanentCRRA.csv`) puts the costless permanent
choice at θ = 0 for ρ ≤ 1.3 and at θ = 1 for ρ ≥ 1.4 -- the paper's wording is RKB's (`notes/TODO.md`
W2b). **The UK exercise** (2026-09-22): the French-characteristics shocks run on the UK's own calibration with
France cut at the UK's groups (`--host UK`, sweep `FRUK`, `results/shocks/UK_shocks{,CommonX}.csv`); the
data caveats (France's voting at those cuts is an overlap approximation; a likely hours typo in France's
own sheet) are `notes/TODO.md` D1.
