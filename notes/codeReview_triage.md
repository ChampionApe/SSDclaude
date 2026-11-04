# Code review triage (2026-11-04; brief `notes/brief_codeDocReview.md`, step 2)

## Outcome (step 2 done, nothing committed)
RKB: cubic NaN check first; retire Medicare/freeTheta, the unwired ESC stages, the orphan results/paper files; fix the
xi drivers (rerun later); apply NUM_Selection; leave the stage-0 drafts. Applied in four passes (P1 US core, P2 US
drivers, P3 paper, P4 InformalSavings/gridsearch/informalAnalytical; module logs of 2026-11-04 hold the detail).
- Cubic NaN (R4#3): 0 NaN nodes in every published ARG surface (all rho, reforms, sweep, appendix D); masking fixed,
  re-solve bitwise equal. US runs 'linear' throughout.
- Moved outputs: NUM_Selection(+Files) counts (US experiments 2->3 files, 108->162 rows, 60->90 counted; ESC 12->13
  files), the `_thetaA/B` Source banners, REPLICATION.md map Reads (workbooks now listed; 20 rows). writing/Paper
  identical (PDF dates aside). Vector-X calibration (not headline) moves <=1.7e-15 relative (closed-form eigenvector).
- Lead: readers escPermanent/escPermanentCRRA/escSequentialCRRA and their csvs removed; pipeline entry `escXi`
  (runESCxi --theta C --main, after escExperiments) added, 0/1 until run; `runShocksXi` (shocksXi) also needs a rerun
  at C; build.py stdout UTF-8 (a new siteData note printed theta into a cp1252 log and crashed the build).
- Open, not applied: sizePiR pi at acceptance (R1#4, <=2e-4 after a stall); resume keys on settings (R2#7); mandatory
  --theta (R2#11); objectiveFrozen's per-candidate anchor (R4#6); the pinTheta=False branch of
  shocks.shockIncomeDistribution/shockFrenchAll/runESC.shockIncomeAndVoting has no driver caller since freeTheta
  went (test_esc.py:351-362 still exercises it); stage-0 drafts undocumented in REPLICATION.md.
- Open (found by the note writer): kappa's factor (1+γ_{t,0})/(1+γ_{t+1,0}) (InformalSavings base.py:180, US base.py:261,
  and the note's eq:governmentBudget:bbar) may be inverted against the budget as written, and n_t means formal young in
  eq:aggregateStates but all young at model_setup:87. Inert in every published run (γ0 constant at 0.4706 in ARG,
  0 in the US; no experiment varies it); needs a derivation before γ0 ever moves over time.

Four reports (R1 US core, R2 US drivers, R3 paper, R4 InformalSavings/gridsearch/informalAnalytical), ~80 findings.
Lead-verified: R1#1-3, R2#2 (all 19 ESC calibration rows converged), R3#7, R3#16. No formula bug found in either
model core (R1, R4 checked the cited labels). Baseline: build reproduces HEAD (PDF dates aside).

## A. Would move a result -- RKB decides
| # | Finding | Moves |
|---|---|---|
| R4#3 | `gridsearch/interp.py` 'cubic'/'pchip' fill NaN nodes (linear masks them); every published ARG instance runs 'cubic', and CRRA `report_t` interpolates surfaces with NaN nodes | ARG CRRA numbers *if* a published surface has NaN nodes in a used stencil -- unchecked |
| R3#6 | `datasets.selectionCsvs` omits `US_shocksXiCommonX.csv`, `escXiRobustness.csv` | NUM_Selection file/row counts (site); verdict unchanged |
| R1#4 | `sizePiR`: db keeps the new path's pi at acceptance, `calibrate` keeps piIn | <=2e-4 in PiR2020/lambdaEff after a damped stall only |
| R1#1-2 | CRRA permanent choice starts the path from s_{t0-1} at position 0; reports at the wrong s0 | `escPermanentCRRA.csv` (unwired, unread) -- moot if the stage is retired (D) |

## B. Bugs with no published number
R1#3=R4#1 `adjDf_ti` `k.loc` (dead `t=` path, all three models: delete it). R4#2 `initialStatePEE` nRoots double-counts
a zero at a node. R2#1 `runESCxi` has no `--theta`: `escXiRobustness.csv` is index-theta, so the site's xi blocks
are silently empty (fix or retire). R3#1 `compareResults` keys too short (rows collapse). R3#2 `--map` under-reports
cached workbook reads (`lru_cache`). R3#3 `%% Source:` banners of the `_thetaA/B` outputs name `results/oecd26/`.
R3#7 the Argentina commands in README/REPLICATION lack `--commonX` (headline). R4#16 `runHorizon.fresh` ignores
`m.commonX`. R4#5 `_calVerify` drops `solveKwargs`. R1#9 `sequentialFOC` mixes costless/wedged terms (raise on wedge).

## C. Guards (no output change)
R2: #2 `converged` filter in `readCalibratedP`/`escLambda`/`escRows`; #3 failures exit nonzero, row-count
`complete` hooks; #4 atomic csv write in `runShocksUS`; #5 'cps' defaults -> paper's (`countryInputs` turnout
required); #6 refuse `--coarse` into `results/oecd26/`; #8 refuse path-p under `--exact`; #9 `runTauTheta.selfCheck`
raises; #12 `stationaryApprox --rho` default; #13 relative `--out` vs `os.chdir`. R1: #5 narrow `except Exception`
and count failures; #6 `s0FixedPoint` fallback check; #7 `calibratePoint` keeps installed grid settings; #8 cache
x0 only on success; #10 lazy fallback x0. R3: #8 PAPER rows of `OECD26_Variants` raise, not `--`; #9 overview
figures raise on a missing headline row; #10 NaN-safe siteData checks; #11 `StaleInput` in `--list`/build; #12
`_noDuplicates` instead of last-wins; #14 `usAlpha` raises. R4#4 `smooth` is a switch, say so.

## D. Retirements -- RKB approves
Medicare and `--freeTheta` (calibrateRhoGrid, runShocksUS, test.reading, testEU, tests); unwired ESC stages
(`runESC.stagePermanent`, `stageFig1`, `runESCcrra.stagePermanentCRRA`, `sens`; `stageCorner` only if the corner
sentence does not need `escCornerSlope.csv`) with their readers and Oct-25 csvs; `runESCxi`+`runShocksXi` if not fixed;
21 orphan generated files in `results/paper` (git rm); 'cps' and 'A2pt' names; stage-0 drafts
(`oecd26Theta` makes the paper's measure: document it in REPLICATION; the SchemesA/B/Topups/PensionTiers/
figuresDataNote drafts: document or archive).

## E. Cleanup (no output change)
Dead defs/imports (leads list, confirmed); history-narrating and wrong docstrings (R1#12-16, R2#18, R3#19-20,
R4#8-10, 13-15); duplicated helpers (R1#19, R2#17); `addEigenVectors` closed form (R1#18, ~1e-16); `CRRA._rootS`
dead branch; README count 51 -> 59.
