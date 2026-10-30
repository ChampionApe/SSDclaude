# Brief: the OECD cross-section with θ from a variant file (2026-10-30)

**Problem.** `python/US/oecd26.py` takes every country's design from figure 1.1's index, θ = 2 − 1/I, with
I = grr100_men/grr050_men (`countryInputs` → `inputsFrom` → `index`, and `ModelOECD.getθ` = `thetaFromIndex(db['RR0'])`).
O5 of the 2026-10-29 review (`notes/thetaTau_alternatives.md`) replaces it with alternative measures, one value of θ per
country and variant. These come from a new stage (0) file, `data/oecd26_theta.csv`, with columns
`iso3, variant, theta, inSample` (one row per country × variant; `theta` in [0, 1] or NaN where it is not defined).
The file is written separately and does not exist yet. Spending (τ0) and every other input stay as they are.

**Change.**
- `oecd26.countryInputs(iso3, turnout, data, thetaSource = 'index')`.
  - With 'index', nothing changes, bit for bit.
  - With a variant name, θ is read from the file and the model's datum is set so that `getθ` returns that θ:
    `index` = 1/(2 − θ), so RR0 and `thetaFromIndex` stay consistent. `θRaw` = θ.
  - A NaN or out-of-range θ, or a missing row, raises a clear error (like `NoTurnout`); the drivers skip such a
    country and print a line.
  - Record `thetaSource` in the inputs dict.
- `runOECD26.py --theta VARIANT` (default 'index').
  - It enters every row (a `thetaSource` column) and `inputsKey`, so a row computed on one θ is never reused for
    another.
  - Anchor rows are also keyed on it: the U.S. anchor's θ changes with the variant, and with it the calibrated ω
    and cost parameter.
  - With `--theta` other than 'index' and no `--outdir`, the default outdir is `results/oecd26_theta_<variant>/`, so
    the paper's `results/oecd26/` is never touched.
  - `--countries` already selects a subset; also add `--inSample`, which keeps the countries with `inSample` True for
    the variant, the U.S. always included.
  - Old csvs without the column read as 'index' (the `LEGACY` mechanism).
- `python/US/README.md`, the module docstrings and `python/US/RESEARCH_LOG.md` updated in the house style
  (CLAUDE.md: spec, not history).

**Checks that must pass.**
- `test_oecd26.py` and `test_oecd26Anchor.py` as before, so 'index' is unchanged.
- A new test with a temporary variant file (a fixture, not `data/`):
  - θ reaches `ModelOECD.getθ` within 1e-12;
  - a NaN row raises;
  - the inputsKey differs between sources;
  - the default outdir follows the variant.
- One `--coarse` smoke run on USA plus two countries with the fixture, written under `logs/` (gitignored), to
  confirm the anchor and layer 1 run end to end.

Do not run the full set, and do not touch `results/oecd26/`, `writing/` or `python/paper/`.

## Extension: the U.S. calibration at a given θ

RKB, 2026-10-30, on top of the above. In the test run the U.S. is re-measured with the new θ in its own calibrations as
well (sections 6–7), not kept at 0.728.

1. A θ override for the U.S. model.
   - `ModelUS.getθ` (python/US/model.py:323) returns `db['θ0']` when that key is present and finite, and otherwise
     derives θ from RR0/RRGroups, unchanged bit for bit.
   - Check that ModelESC's wedge-aware getθ and ModelOECD.getθ honour it consistently, or that ModelOECD keeps its own
     route; say which.
   - Where the override value comes from: the U.S. row of data/oecd26_theta.csv for the chosen variant, so the U.S.
     carries the same number in sections 6–7 and in the cross-section's anchor.
2. calibrateRhoGrid.py: `--theta VARIANT`, which installs θ0 from that file. It writes to its own csv and pickle
   directory (e.g. results/oecd26_theta_<variant>/calibration/US_rhoGridCommonX.csv), never results/calibration/. Only
   ρ = 1, common X, is needed for the test, so the run accepts `--lo 1 --hi 1`.
3. runESC.py --stage calib: the same `--theta VARIANT`, with its own output directory under
   results/oecd26_theta_<variant>/esc/, and β/ω recalibrated inside as now. It should yield λ, ε and ω at the new θ for
   the paper's spec ('size', commonX), log only.
4. runOECD26.py --theta VARIANT: usBeta reads the variant's own U.S. sweep csv from item 2, not results/calibration/.
   It refuses, with a clear message, if that csv is missing. The anchor key records the sweep it used
   (crossCuttingFindings #13).

Tests: the 'index' / no-θ0 defaults unchanged bit for bit (the existing U.S. and ESC calibration tests that apply), and
θ0 reaching getθ within 1e-12. The smoke run at --coarse with the fixture should exercise the chain end to end: the
U.S. calibration at θ0, the ESC calib, the anchor, then layer 1 on two countries. Still no full runs.

## Extension 2: the counterfactuals at a given θ

RKB, 2026-10-30. Besides the calibrations, the test run also re-runs the U.S. counterfactuals of sections 6–7 at the
new θ, ρ = 1 only. The same `--theta VARIANT` (θ0 from data/oecd26_theta.csv's U.S. row, outputs under
results/oecd26_theta_<variant>/, read from that variant's calibration csv, never from results/calibration/ or
results/esc/) is added to:

(a) runShocksUS.py --rho 1 --commonX (the families theta, ageing, french, the France reference row). France keeps its
    own calibration; the U.S. baseline and every U.S.-based scenario take θ0. The income-distribution scenario holds θ
    at the U.S. θ0.
(b) runESC.py's stages path, shocks and country (and corner if it is cheap) under the paper's spec ('size', commonX),
    at the variant's calibrated λ, ε and ω from item 3.

Same tests: defaults unchanged bit for bit, plus one --coarse smoke run of each new entry point. Still no full runs:
report the exact commands for the full test run (calibration → ESC calib → shocks → ESC path/shocks/country → OECD
anchor, layer 1 and layer 2 with --spec sizePiR --betaRule common --turnout cps cses --inSample), in the order they
must run.
