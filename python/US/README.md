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
| `test.py`, `testEU.py` | workbook loaders: `USMain_test.xlsx`; `FRMain.xlsx`/`UKMain.xlsx` via `testEU.model('FR'|'UK'[, grouping='US'])` |
| `calibrateRhoGrid.py`, `calibrateRhoGridEU.py`, `runShocksUS.py`, `runESC.py`, `runESCcrra.py`, `collectESCexperiments.py` | drivers |

Eight fast test suites (~55 s), registered in `python/runTests.py`.

## Running it

```
python\US\calibrateRhoGrid.py   [--commonX]                  # US sweep, rho 0.5..2.0 step 0.1, ~4.5 min
python\US\calibrateRhoGridEU.py --country FR|UK [--grouping US] [--commonX]
python\US\runShocksUS.py        [--commonX] [--family theta] [--rho 1]
python\US\runESC.py | runESCcrra.py    [--commonX]           # endogenous theta
python\US\collectESCexperiments.py                           # merge -> results/esc/escExperiments.csv
```

Sweeps write their csv after every point and resume from it; `python/paper/` drives all of this. Instance
directories are per sweep (pickle names are the `ρ` alone). EU sweeps need the complete US sweep of the
*same variant* first (`USReference` matches `ρ` exactly; `--maxHalvings` defaults to 0 there). ESC drivers
merge into their csvs (`runESC.mergeWrite`); `runESCcrra.py --bracket` must span every `ρ` asked for, since
`p` falls from 0.965 to 0.090 across `ρ` = 0.5..2.

## Invariants the code depends on

- **Zero-mass slot.** Type 0 stays in every array with `γ_0 = 0`; synthetic `η_0`/`X_0` must be finite
  (`0·NaN` poisons the FOC; `test_ee.py` perturbs the slot). `getEps` raises if `γ_0 > 0`.
- **The LOG FOC decouples across `t`** (`eq:us:model:PEELOG:decoupling`); the backward solver is still
  used. Not true under CRRA.
- **Two invariances**: scale (`y^η → λy^η`, normalised away by `Γ_h = 1`) and hours unit (`y^x → μy^x`,
  moves only `h_i` and `h̄`). `test_invariance.py`. **`h̄` is the only object comparable to an observed
  workweek, and under vector `X` its level is meaningless**: report it against a reference, never as a
  level across calibrations.

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

## Endogenous `θ`

- The leaded choice under the `f(θ)` deadweight wedge. Measured in `test_esc.py`: `z_t` depends on
  `(τ_t, θ_t)` alone, so `τ_t = τPolicy_t(θ_t)`; under LOG the choice has no state and is invariant to
  `s_{t-1}`. Both fail under CRRA (`LeadedCRRA` solves the path, reports `stateSensitivity`).
- Runs under the variant `config.US['commonX']` names; `commonX` is part of every merge key (#13). The
  `flat` spec is implemented but not run for the paper.
- Calibration target: the design *in force* in 2020 (`leadedDesignAtT0`); `p` = 0.4076 at `ρ` = 1,
  `scale`, φ = 0.5. `p` and the chosen design are bit-identical across the calibration variants; only
  exogenous rows that swap `η` move (`notes/esc_experiments_acrossRho.md`).
- `LeadedCRRA2D` is the exact 2-D recursion certifying the path iteration to ±0.01; pinned periods
  collapse the candidate grid inside the recursion; the θ-state grid matters (13 nodes), the `s` grid does
  not. ~70 s per period at `ns=150`.
- Permanent timing: the joint `(τ_{t0}, θ)` choice concentrates to a 1-D search; the savings ratio is
  pinned at the fixed point `θ*` (`solveFixedPoint`, default), not at the incumbent (#11/#11b).

## Status

Implemented and tested: EE, LOG and CRRA PEE, both calibration variants, `ModelFR`, ρ sweeps for all four
calibrations in both variants, three counterfactual families in both readings, the endogenous-`θ` leaded
choice (LOG, CRRA path iteration, exact 2-D) and permanent timing, and the `python/paper/` wiring.
Structural ESC corners: France and the UK-at-US-percentiles have no own-wedge calibration (the observed
design is the `θ = 1` corner); the UK's own `p` = 0.185 against the US's 0.408.

**Open**: the *sequential* ESC timing is unimplemented; `PermanentCRRA` has never been executed
(`notes/TODO.md`, items 10–11); the workweek column's full-effect gap against the paper (~2%,
unattributed, not the initial condition); the UK's `X_i` sit 1.108× the paper's (the `λ` normalisation).
