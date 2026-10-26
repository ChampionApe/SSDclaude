# Brief C0: candidate counts in every politico-economic solve (A6)

Package C0 of `notes/plan_reviewResponse.md` (W16). Agent: model-coder. Branch `review-2026-10`.

## Problem

Appendix D and the online appendix's `NUM_Selection` (`python/paper/tablesOA.numSelection`, built from
`datasets.selectionCsvs`/`countSummary`) report the tax rule's candidate counts (`nEqMax`, `nCandMax`,
`nFallback`; `writing/US/num_robustroot.tex`, eq:equilibriumTest) per results csv. The columns exist
everywhere (`python/US/policy.multiplicityColumns`), but many politico-economic solves write `-1` or NaN
because the solve's counts are not passed through. Today's table (`results/paper/Tables/NUM_Selection.tex`),
rows counted of rows:

| csv | counted | where the counts are lost |
|---|---|---|
| `results/calibration/{US,UK,FR}_rhoGrid{,CommonX}.csv` | 0 of 16 each | `calibrateRhoGrid.toRow`/`calibrateRhoGridEU`: `calibratePoint`'s record carries no `multiplicity` (the US/UK/French calibration paths, `python/US/model.py` `calibrate`) |
| `results/shocks/{US,UK}_shocks{,CommonX}.csv` | 6 of 54 | `runShocksUS.main` writes `multiplicityColumns(None)` for every scenario row; `shocks.runOne` drops the `'full'` solve's `multiplicity` |
| `results/esc/escCountry.csv` | 9 of 12 | find out which rows and why |
| `results/esc/escShocksCRRA{,UK}.csv`, `escCalibrationCRRA{,UK}.csv`, `escPathCRRA.csv` | 16 of 120, 16 of 30, 0 of 8, 0 of 2, 0 of 48 (tax layer) | the CRRA ESC driver (`runESCcrra.py`, `policyESC.py`); NaN rows may be rows written before the columns or the `path` method rows |
| `results/esc/escPermanent{,CRRA}.csv`, `escSequentialCRRA.csv`, `escXiRobustness.csv` | 0 | the permanent timing returns none (runESC.py:106); check whether a selection is run there at all |
| `results/numerical/US_ESC_stationaryApprox.csv` | 9 of 27 | find out |

Argentina (`python/InformalSavings`) already records counts on every PEE csv (rhoGrid, `universal_match_*`,
`epsThetaGrid`, `ARG_stationaryApprox`). The `eeOnly_*` rows and the shocks' `'ee'` rows are
economic-equilibrium solves with taxes held at the baseline path: they select no tax and stay `-1` by design.

## What to do

1. Pass the counts through every politico-economic solve whose csv rows the paper or the online appendix
   read, U.S. block (U.S., UK, France, the UK hosts `UK`, `UKUS`, `FRUK`) and ESC (LOG and CRRA, exact
   method; the design layer `nEqθMax`, `nBrθMax`, `nFallbackθ` where the exact CRRA recursion runs): the
   calibration record of `calibratePoint`, `shocks.runOne`'s `'full'` solve and `runShocksUS`'s rows, the
   CRRA ESC rows, `franceReference`, the stationary-approximation rows. Where a solve genuinely runs no tax
   selection (an economic equilibrium, a timing that fixes the tax), leave `-1` and list it in the report
   with the reason.
2. Changing the numbers is not allowed: τ, θ and every reported quantity must be bitwise unchanged. The change
   only carries existing `sel['nCand']`, `sel['nEq']`, `sel['fallback']` outward.
3. The 26-country driver of C3 will reuse `python/US`'s solve and row helpers; make the counts come with
   the solve's return value (as `solvePEE_*`'s `'multiplicity'` already does), not as a per-driver patch.
4. Tests (script style, `gridsearch/testing.py`): for each code path you change, a small solve whose row
   carries non-negative counts and fails without the change: a U.S. LOG calibration point, a shock's
   `'full'` row, a CRRA ESC row. Register them in `python/runTests.py` if they are fast, otherwise run them
   and quote the output.
5. Reference number: before the change, record the 2020 τ of one U.S. LOG calibration point and of one
   shock's `'full'` solve (e.g. ageing at ρ = 1) from the unchanged code; after, report them bitwise.

## Files

May touch: `python/US/{model.py, modelFR.py, modelESC.py, policy.py, policyESC.py, shocks.py, runShocksUS.py,
runESC.py, runESCcrra.py, runShocksXi.py, calibrateRhoGrid.py, calibrateRhoGridEU.py, stationaryApprox*.py}`,
new or existing test files in `python/US/`, `python/runTests.py`, `python/US/RESEARCH_LOG.md`, and
`python/US/README.md` if a status line changes. Not `python/InformalSavings`, `python/paper`, `results/`,
`writing/`. If `python/gridsearch` seems to need a change, stop and report instead.

## Done when

- Every fast suite passes (`python\runTests.py`), and the US suites you touched pass.
- Stage (iii) on the current `results/` is unchanged: `python/paper/build.py` runs and `git status
  results/paper writing/Paper` shows no change (re-check out any PDF that differs by bytes alone,
  per `python/paper/README.md`'s traps).
- The reference τ's are bitwise equal.
- The report lists, per csv of the table above, whether its rows will now record counts on the next
  rerun (C1 reruns stages (i) and (ii) for the U.S. block and ESC), and which rows stay `-1` and why.
