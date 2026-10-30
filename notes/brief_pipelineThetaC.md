# Brief: the paper pipeline on θ variant C, with a reduced run list (2026-10-30)

RKB's decisions of 2026-10-30. **θ variant C** (`notes/thetaTau_alternatives.md`, `data/oecd26_theta.csv`) becomes the
paper's main measure for the U.S., the UK, France and the OECD cross-section. The U.S. and OECD runs are cut to the
list below. The earlier `--theta` work is in `notes/brief_oecd26ThetaSource.md` (with its two extensions) and
`python/US/README.md`; the test run of C is in `results/oecd26_theta_C/`, compared in `notes/thetaC_comparison.md`.
Scope is the U.S. and OECD arms only: Argentina (`ARG`, `runCalibration.py`, `runShocks.py`) is unchanged.

## 1. Model code (python/US)
- **The UK and France take their θ from the variant file** wherever `--theta V` is given: the FRA and GBR rows
  (C: 0.8216 and 0.1806), installed as `θ0` like the U.S. one. This covers:
  - `calibrateRhoGridEU.py` (FR and UK sweeps);
  - `runESC.py` stages country, pathHost and corner;
  - `runShocksUS.py`'s France reference row, and the French counterfactuals' source calibration.

  France in section 6 is calibrated at the U.S. income percentiles. The new θ is a slope over earnings multiples and
  does not depend on the grouping, so France at the U.S. cuts takes θ0 = 0.8216 directly and its ω is recalibrated
  there. That is the auxiliary step: a recalibration at the imposed θ, not a re-derivation of θ. The income-
  distribution counterfactual still holds θ at the U.S. θ0. Check every place where `modelFR`/`testEU` derived θ
  from RR0 or assumed θ = 1, among them the deep test's corner argument (`escCornerSlope`) and the `closedForm`
  checks at θ ≡ 1. Make each one either take θ0 or say why it is unaffected.
- **τ from the file.** Under a variant, `oecd26.countryInputs` takes τ0 from the file's `spending` column. Assert
  that for the variants paper, A, A2pt and C it equals figure 1.1's `pensionSpending` to 1e-9. B's column is public
  plus mandatory and quasi-mandatory private spending. The 'index' default stays bit for bit.
- **Writing the standard result paths.** The guard that refuses variant output in
  `results/{oecd26,calibration,esc,shocks}` stays, except for the pipeline's main variant: allow it when an explicit
  `--main` flag is given and V equals `config.US['theta']`. The robustness variants keep writing to
  `results/oecd26_theta_<V>/`.

## 2. The pipeline (python/paper)
- `config.US['theta'] = 'C'`. Every U.S., UK, France, ESC and OECD command of stages (i) and (ii) carries
  `--theta C --main`.
- **ρ grid** = [0.5, 1, 2] for every U.S. arm: the U.S., FR and UK sweeps, the shocks, the exact CRRA ESC, and
  `ρTable`. The stationary check's `ρStationary` is cut to the non-log points of the new grid, [0.5, 2.0];
  `ρPermanentCRRA` goes with the runs dropped below.

**Kept (RKB):**

| row | what | runs |
|---|---|---|
| 1 | U.S. sweep, vector X | ρ = 0.5, 1, 2 (RKB, 2026-10-30, second round) |
| 2 | U.S. sweep, common X | ρ = 0.5, 1, 2 |
| 3 | FR and UK sweeps | ρ = 0.5, 1, 2 |
| 4 | ESC LOG calibration | paper's cost and the comparison cost |
| 5 | Π-inclusive cost calibration | LOG, needed by 14 |
| 6 | exact CRRA ESC calibration | paper's cost only, plus the UK's own |
| 8 | `shocks` (vector X) | ρ = 0.5, 1, 2 (RKB, second round) |
| 9 | `shocksCommonX` | ρ = 0.5, 1, 2 |
| 12 | `shocksXi` | LOG, cheap; unconfirmed, listed for RKB |
| 13 | `escPath`, `escShocks` | |
| 14 | `escCosts` and the `escAgeingCosts` merge | acute ageing only |
| 15 | `escCountry`, `escPathHost` | the UK and France at their C designs |
| 16 | `oecd26` | `sizePiR` × common β × {cps, cses} × {anchor, layer1, layer2}; `none` × common β × {cps, cses} × {anchor, layer1, layer2} (figure 6.2's spending test) |
| 18 | `escShocksCRRA` | only |
| 19 | `stationary`, `stationaryESC` | ρStationary = [0.5, 2.0] (RKB, second round) |
| 20 | `escExperiments` merge | |

Rows 1 and 8 carry `--theta C --main` like their common-X twins.

**Dropped (RKB, or following the suggestion RKB accepted):**
- 7: the LOG calibrations at the other φ (PHIROBUST)
- 10: `shocksMedicare`, `shocksMedicareCommonX` and the USMedicare sweeps
- 11: `freeTheta`
- 14: the rest of the cost comparison (the path and mild ageing in `escCosts`, all of `escCountryCosts`)
- 17: `escPermanent`, `escPermanentCRRA`, `escSequentialCRRA`
- 18: the rest of the CRRA ESC (`escShocksCRRAcomparison`, `escShocksCRRACosts`, `escShocksCRRAMild`)
- 6: the exact CRRA calibrations for the comparison cost and the cost variant

Remove each one from the drivers' declarations rather than leaving it skipped. Keep the scripts themselves.

- **Robustness variants**: a stage (ii) entry `oecd26Variants`. For V in A, A2pt, B: `calibrateRhoGrid.py --commonX
  --lo 1 --hi 1 --theta V`, then `runOECD26.py --theta V --inSample --spec sizePiR --betaRule common --turnout cps cses
  --stage anchor layer1 layer2`, both into `results/oecd26_theta_<V>/`.
- **Builders** (`tablesOECD26`, `figuresOECD26`, `datasets`):
  - **Data side.** The cross-section's data relations use I = 1/(2 − θ_C) on the in-sample countries, with the
    sample taken from the file.
  - **New table, `OECD26_ThetaVariants`.** Table 5's five slopes under paper, A, A2pt, B and C, at both turnouts.
    It is built by build.py but not yet `\input` anywhere; RKB places it.
  - **Dropped outputs.** Every builder output that read a dropped run is removed from build.py, with a list in your
    report of the paper and online-appendix outputs and quoted numbers that disappear.
  - **Figure 1.1 on the new measure** (RKB, second round). The OECD data figure (`oecdFigure1.figure`, output
    `OECDdata`) plots the Bismarckian index I = 1/(2 − θ_C) from `data/oecd26_theta.csv` on variant C's in-sample
    countries (21); the spending, population-growth and Gini panels stay on the same countries. Its generated
    note/caption states the measure and the sample. The report lists the paper sentences that quote figure 1.1's
    sample or numbers (e.g. "29 countries", the introduction's slopes) for a later text pass; they are not edited.
- Update `REPLICATION.md` (`build.py --map`), `python/paper/README.md`, `python/US/README.md` and the module logs.
  Do not hand-edit any generated `.tex` in `writing/Paper`.

## 3. Checks
- The 'index' / no-θ0 defaults are bit for bit.
- `python/runTests.py` passes in full.
- `python/paper/test_oecd26.py` and `test_onlineAppendix.py`, and `writing/checkPaper.py`, are adapted to the
  reduced set and pass.
- `build.py --dry` (or `--list`) shows every remaining output with a source.
- One `--coarse` smoke run of the new FR/UK θ0 route.
- No full runs: the overnight run is a separate step.

## 4. The overnight script (write it, do not start it)
`logs/overnight_2026-10-30/run.sh`, in this order:
1. Snapshot `results/{calibration,esc,shocks,oecd26,paper}` to `logs/results_snapshot_preC_2026-10-30/`.
2. `runCalibrationUS.py --all`.
3. `runShocksUS.py --all`.
4. The `oecd26Variants` entry.
5. `build.py` and `build.py --site`.

Each step logs to its own file plus a status line with its timing, and a failure stops only the steps that depend
on it. Give the expected time of each step.
