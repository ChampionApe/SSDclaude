# paper

The pipeline that turns solved models into `writing/Paper`'s tables and figures and the online appendix. It
owns no economics; every number it emits is read off `results/`. The long version of this file, with every
arm's runs described: `archive/readmes/paper_README_2026-10-27.md` (and `_2026-09-11.md`).

## Three stages, run in order

Two arms, Argentina (`python/InformalSavings/`) and the OECD economies (`python/US/`), with separate stage
(i)/(ii) entry points; they share `config.py`, `results/` and stage (iii).

| Stage | Argentina | US / France / UK | Writes | Cost (cold, ARG / US) |
|---|---|---|---|---|
| (0) data targets | `dataTargets.py` | `oecdFigure1.py` (figure 1) | `data/argentina_*.csv`, `data/oecdFigure1*.csv` | seconds |
| (i) calibration | `runCalibration.py` | `runCalibrationUS.py --commonX` | `results/calibration/`, `results/paper/*Summary.csv` | ~3.2 h / ~45 min |
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/`, `results/esc/`, `results/oecd26/`, `results/oecd26_theta_<V>/` | ~50 min / ~2 h (+3 h variants, +1.5 h stylized) |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |
| online appendix | `build.py --site`, then `quarto render writing/OnlineAppendix` | the same | `writing/OnlineAppendix/{_generated,_book,_variables.yml}`, `writing/Paper/onlineAppendix.tex` | ~1 min |

- Stages (i)/(ii) have `main` and `prepub` (`--prepub`; `--all` for both): the exact CRRA cost calibrations (~5-6.5 h,
  `--lanes`), the CRRA ESC leg and the stationary checks (~2 h). `--keepGoing` passes a failed part;
  `logs/overnight_2026-10-30/run.sh` runs (i)-(iii) in their order of dependence.
- **The design's measure** is `config.US['theta']` ('C' of `data/oecd26_theta.csv`): every U.S. arm command carries
  `--theta C --main` (`config.thetaFlags`); every reader keeps the rows at it (`config.atTheta`, `datasets._readUS`),
  and an output counts only there. The U.S. ρ grid is 0.5, 1, 2 (`--rhos`).
- Every stage skips work whose output exists; `--force` overrides, `--list` reports, `--dry` prints the delegated
  commands. **`--force` whenever anything upstream moved, a recalibration above all** (#13); it is forwarded to the
  child only where the child resumes.
- Stage (iii) imports no model code and unpickles nothing; an output whose inputs are missing is reported and
  skipped (`datasets.MissingInput`), never partially written. Stages (i)/(ii) are declarations: `config.py` records
  the settings the published numbers were produced at. **Change a paper number there first.**
- Both arms carry two calibration variants, `config.US['commonX']`/`config.ARG['commonX']` (both True) naming the
  headline; `build.py` registers the headline only. The ESC leg runs under the US headline only.
- Stage (0) is the only network access (it writes `data/` and skips existing output). **`--map`** rewrites
  `REPLICATION.md`'s output table: one row per registered output, its inputs traced through pandas at build time.
- The US arm's further runs, each a stage (i)/(ii) entry of `config.US`: `shocksXi` and `escPathHost` (the site's;
  the UK as a second host, retired 2026-10-27, is in `archive/results/ukHost_2026-10/`), the ESC cost (`esc['spec']`
  'size', `comparisonSpec` 'scale' under log only; under 'size' `phi` is a dummy key and `p` holds λ), the Π-inclusive
  cost `'sizePiR'` (`esc['costVariants']`: LOG calibration, acute ageing, `escAgeingCosts.csv`), the tax against a
  pinned design (`escTauTheta`, `python/US/runTauTheta.py`, `config.US['tauTheta']`, seconds). Dropped 2026-10-30:
  Medicare, `freeTheta`, the timing checks, the deep test under ε, the other costs under CRRA.
- **The cross-country test** (A14, C14, R6; `archive/notes/brief_retAgeChoice.md`): stage (ii)'s entry `oecd26` runs
  `python/US/runOECD26.py --inSample` per variant of `config.US['oecd26']['variants']` and per retAge of it (rows keyed
  on inputs and the U.S. β, #13) on the measure's 21 countries, data side I = 1/(2 - θ): the paper's specification
  with and without the cost, appendix G's population variants (ν uncorrected, at the exit age) and C5's readings
  (Luxembourg left out, layer 1 at the U.S. ω); `oecd26Variants` the data variants A, B (`config.THETANAMES`) into
  `results/oecd26_theta_<V>/`. The paper's variant (ε, printed `\varepsilon`; β 'common'; own turnout with Luxembourg
  flat, `csesFlat`, on the `cses` anchor; layer 1 at the mean layer-2 ω, `omegaRule`; ν at the statutory correction,
  `retAge` 'nra'; design in force in 2020; section 7's spending at the chosen design, `spendingReading`) and section
  6's `spendingSpec` live in `config.US['oecd26']`; another carries its suffix (`_cses`, `_omegaUS`, `_nuNone`,
  `_thetaA`). Stale anchors or rows raise `StaleInput`. France's own ν is `config.US['retAgeFR']`'s (`testEU.load`;
  `'nra'`, appendix F). Retired: the cps rows (unread); the pooled turnout and A2pt in `archive/results/`.
- **Argentina's GDP** is formal plus informal output, `Y + Y0` (#3): `datasets` reads savings and spending over it
  (`savingsRatePath`, `spendingPath`) and `config.argTaxTarget` checks the calibrated τ. Not wired: the pre-reform
  ε = 0 calibration and `reformDiagnostics.py` (`REPLICATION.md` §3).
- Not wired, commands in `REPLICATION.md` §3, both with `--theta C --main`: C5's smaller U.S. numbers
  (`python/US/c5Numbers.py` -> `results/numerical/C5_*.csv`; the site's `US_TaxState`, `US_Strategic` read two) and
  C4's appendix D checks (`runHorizon.py` -> `results/numerical/`; `NUM_Horizon`, `NUM_Residuals`,
  `NUM_HorizonPaths` read them). Their U.S. readers keep thetaSource C only (`datasets._readUS`).

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications, calendars, unit conversions; imports nothing from the models |
| `datasets.py` | the only module that knows the `results/` layout and column names, both arms |
| `tables.py`, `figures.py` | Argentina builders, one function per output; `figures` owns the house style |
| `tablesUS.py`, `figuresUS.py` | US/France/UK builders: the calibration (`USFRCalibration`, the paper's; `OECD_Calibration`, the three, the site's), section 7's `US_ESC_Calibration`, `US_ESC_overview`, the site's deep test `US_ESC_Country` (the UK and France under the U.S. λ, each at its θ0 with its own λ where one exists; the corner sentence only for France at θ = 1), `UK_ESC_Calibration` |
| `build.py` | stage (iii): the output registry for both arms, the copy into `writing/Paper` (not for `ONLINE_ONLY`; a figure's `_note.tex` beside its pdf) |
| `tablesOA.py`, `figuresOA.py` | the online appendix's own exhibits, `US_ESC_Path` and `US_ESC_TauTheta` (its note generated) among them |
| `siteData.py` | the datasets of the site's interactive figures (kind `data`), each checked against the file it duplicates |
| `onlineAppendix.py`, `texTable.py` | `build.py --site`: the exhibits' registry (`EXHIBITS`), their blocks, the datasets, `_variables.yml`, the `\oa` macros (retired keys aliased); `test_onlineAppendix.py` checks them |
| `compareResults.py` | every changed csv under `results/` against a commit, rows aligned on the file's keys (writes nothing) |
| `dataTargets.py`, `oecdFigure1.py` | stage (0) |
| `oecd29Data.py`, `oecd26Sample.py`, `oecd26PensionTiers.py` | stage (0), not wired: the 29 countries' inputs (`data/oecd29*.csv`, `notes/data_oecd29.md`); the sample rule (`data/oecd26_sample.csv`); pension tiers and their financing, draft (`data/oecd26_pensionTiers_harmonised.csv`, `notes/data_thetaTau.md`) |
| `oecd26SchemesA.py`, `oecd26SchemesB.py`, `oecd26Topups.py` | stage (0), not wired, drafts: scheme rules by country (`data/oecd26_pensionSchemes_A.csv`, `_B.csv`; no network, hand-read values typed in); top-up spending and the share s (`data/oecd26_topups.csv`, `notes/data_thetaTau.md` §G; checks every typed value against its raw file's text) |
| `figuresDataNote.py` | not wired: the technical note's data part, three figures of the θ/τ variants from `data/oecd26_theta.csv` alone into `writing/data/figs/` |
| `tablesHorizon.py` | appendix D: `NUM_Horizon` (`NUM_HorizonPaths` on the site), `NUM_Residuals`; the counts are `tablesOA.numSelection` |
| `tablesOECD26.py`, `figuresOECD26.py` | the cross-country test (`results/oecd26/`, the measure's data side `tablesOECD26.dataSide`): section 6's spending at the observed designs without the cost (`OECD26_Spending`), layer 1 beside the data (`OECD26_Layer1`), the five slopes (`OECD26_Slopes`), the `ω`'s (`OECD26_Omega`), predicted against observed θ (`OECD26_ThetaFit`; `thetaFit`'s r and RMSE without the U.S.), appendix G's `OECD26_Variants` (population and data variants) and `OECD26_ThetaFitPopulation`, `OECD26_ThetaFitMeasure`, C5's exhibits by suffix; the index version `OECD26_ThetaFitIndex` is built, not input. Every figure writes `<name>_note.tex` with its numbers. `test_oecd26.py` checks them on synthetic csvs |

## Outputs wired (51)

Every generated `.tex` carries a `%% Source:` banner; `--list` reports what is buildable now. Every table row ends
in a `% row: <key>` comment (`tables.rowKey`) and every figure writes `.svg` and `.marks.json` (`figures._save`),
which tie the site's datasets to the paper's figures. Of the 22 outputs copied into `writing/Paper` the paper inputs 20
(not `ARG_LOG_FourInOne` and the index version `OECD26_ThetaFitIndex`); the online appendix's 43 exhibits read
39 outputs, 37 of them `ONLINE_ONLY` (never copied), appendix F.3's and G's among them since 2026-11-02;
`onlineAppendix.RETIRED` holds the 10 exhibits whose runs were dropped on 2026-10-30, which the pages still include (a
notice is written in their place). Figure 1.1 (`OECDdata`) plots the measure's index on its countries and writes
`OECDdata_note.tex`; every note that defines θ says it as `config.THETADEF`. Removed 2026-10-30 with their runs:
`OECD26_Robustness`, `OECD26_Reconcile`, `ESC_Timing`, `ESC_CostCalibration`, `OECD_Medicare`,
`OECD26_{Layer1,Slopes,Omega}_{29,size}`; 2026-11-02 `USUKFRCalibration` (a duplicate of `USFRCalibration`).

## Traps

One line each; measurements in the archived READMEs.

- A pinned `θ` does not survive a composite shock on its own (#9); the composites re-install it.
- `build.py` backs up a hand-written file once, to `results/paper/superseded/`; re-runs detect their banner.
- The workweek is a normalisation: `config.workweekHours(h, hRef)` = `42.54·h/hRef`, per ρ. Never `h·7·12`.
- The pre-reform savings rate is per ρ in both arms; difference against that ρ's own baseline.
- The Argentina ρ march is seeded at its anchor (`config.ARG['anchorGuess']`); retune if α or K/Y moves.
- `datasets.seedSavings` derives `s_{t0-1}` two ways and raises if they disagree; vectors go through the summary
  csv as JSON; `datasets.epsThetaGrid` requires one `statusQuo` row matching `calibrationSummary` (#13).
- Colours: the blue/orange pair in fixed order, `figures.THETA_RAMP` for a continuous parameter; a figure is sized
  at the 5.91 in measure; a `% row:` key is the LAST thing on its line; `_save` raises on a mark id not once in
  the svg; `--map`/`--list` re-save figures whose PDFs differ by creation date alone (`git checkout` them).
- The site's PDF edition (not built) must render with `pdf-engine: pdflatex`, `latex-auto-install: false`.
- US arm: the full US sweep before any EU sweep; one savings unit, `s/Y` (`datasets.US_SR`, the ESC csvs by
  `(1-α)`); an ESC reading against the baseline of the same reading; `workweek` in the shock csv is in hours;
  `config.usCalendar()` reads the workbook, not a copy's stale `db['dates']`.
- The CRRA ESC csvs hold `method` exact (published) and path side by side; `datasets.escMethod` never falls back.
- An ESC calibration row without `Vtilde`, `fStar`, `f0`, `τ0` predates `'size'` (`datasets.escWedge`).
- The two calibration variants check each other: baseline, `θ`, ageing and voting identical (≤5e-15).
