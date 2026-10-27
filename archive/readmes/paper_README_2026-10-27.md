# paper

The pipeline that turns solved models into `writing/Paper`'s tables and figures and the online appendix. It
owns no economics; every number it emits is read off `results/`.

## Three stages, run in order

Two arms, Argentina (`python/InformalSavings/`) and the OECD economies (`python/US/`), with separate stage
(i)/(ii) entry points; they share `config.py`, `results/` and stage (iii).

| Stage | Argentina | US / France / UK | Writes | Cost (cold, ARG / US) |
|---|---|---|---|---|
| (0) data targets | `dataTargets.py` | `oecdFigure1.py` (figure 1) | `data/argentina_*.csv`, `data/oecdFigure1*.csv` | seconds |
| (i) calibration | `runCalibration.py` | `runCalibrationUS.py` | `results/calibration/`, `results/paper/*Summary.csv` | ~3.2 h / ~20 min |
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/`, `results/esc/`, `results/oecd26/` | ~50 min / ~30 s (+ESC) |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |
| online appendix | `build.py --site`, then `quarto render writing/OnlineAppendix` | the same | `writing/OnlineAppendix/{_generated,_book,_variables.yml}`, `writing/Paper/onlineAppendix.tex` | ~1 min |

- Stage (ii) has two parts in both arms: `main` (the default: sweeps, the exogenous shocks in both variants,
  the LOG ESC leg) and `prepub` (`--prepub`; `--all` for both), run once before submission: the exact CRRA ESC
  leg (`runESCcrra.py --exact`, the published method, ~3 h for two ρ in parallel), the timing checks (~3.5 h),
  and the stationary-vs-date-specific checks behind section 4's accuracy footnote (~1 h US, ~10 min
  Argentina), which write `results/numerical/` for the online appendix's `NUM_Stationary` alone.
- Every stage skips work whose output exists; `--force` overrides, `--list` reports, `--dry` prints the
  delegated commands. The ESC merge entry always runs. **`--force` whenever anything upstream moved, a
  recalibration above all**: the calibration sweeps and `sweepEpsThetaGrid.py` resume from their own csv
  keyed on the parameter point alone (finding #13). It is forwarded to the child only where the child resumes.
- Stage (iii) imports no model code and unpickles nothing, so a rebuild is seconds and can never turn into
  a solve. An output whose inputs are missing is reported and skipped (`datasets.MissingInput`), never
  partially written.
- Stages (i)/(ii) are declarations: the model folders' scripts do the work, and `config.py` records the
  settings the published numbers were produced at. **Change a paper number there first.**
- Both arms carry two calibration variants, `config.US['commonX']` and `config.ARG['commonX']` (both True)
  naming the headline. Every builder takes `commonX` (the headline by default) and `build.py` registers the
  headline only; the vector-X calibration reaches the online appendix through its own tables and datasets.
  Argentina's variant has its own sweep csv, instance directory and suffixed shock/sweep csvs
  (`runCalibration.py`/`runShocks.py --commonX`). The ESC leg runs under the US headline only.
- Stage (0) is the only network access (Penn World Table via FRED; OECD, PaG 2021, World Bank, WIID and WID for
  figure 1); it writes inputs to `data/` and skips existing output. `oecdFigure1.PLOT = NAMED` plots the
  concepts figure 1's note names.
- **`--map`** rewrites the output table of `REPLICATION.md`: one row per registered output with the files it
  reads (traced through pandas at build time, not declared) and the tex files that input it.
- **The UK as host** (`config.US['ukHost']`, the UK's own λ in `config.US['esc']['uk']`): stage (i) sweeps
  `FRUK` and, with `--prepub`, calibrates the UK's λ under CRRA; stage (ii) runs `runShocksUS.py --host UK`
  and `--host UKUS` (the UK at US income groups), `escShocksUK`, `escShocksCRRAUK` (prepub; both with acute
  ageing since 2026-10-09) and the `escExperimentsUK` merge; outputs `UK_*`, `FRUK_*`, `UKUS_*` and the site's
  counterfactuals.
- **The online appendix's runs** (2026-10-09): `shocksXi` (`python/US/runShocksXi.py`: the US counterfactuals at
  ξ = 0.2, 0.3, 0.4, LOG, common X, the US and France recalibrated at each ξ; its ξ = 0.3 block is checked against
  `US_shocksCommonX.csv`) and `escPathHost` (`runESC.py --stage pathHost`: the design path of France and the UK
  under the US λ and their own). The site's datasets (`siteData.py`) read them.
- **The ESC cost**: `config.US['esc']['spec'] = 'size'` is the paper's, `comparisonSpec = 'scale'` the earlier
  wedge, the online appendix's second cost (C3); under `'size'` `phi` is a dummy key and the `p` column holds λ.
  Stage (i) calibrates both under LOG and under the exact CRRA recursion (`config.escBracket`, set from the LOG
  parameter); stage (ii) runs both, the stationary check the paper's only.
- **Section 7's cost variants** (`config.US['esc']['costVariants']`, A8): the Π-inclusive cost `'sizePiR'`
  (λ·Π_t/R_t, `python/US/modelESC.py`) calibrated and run like the paper's into `--tag Costs` csvs
  (`escCalibration{,CRRA}Costs`, `escPath{,CRRA}Costs`, `escShocks{,CRRA}Costs`, the last also mild ageing under
  the two other costs at ρ ≠ 1); `escAgeingCosts` merges mild and acute ageing under the three costs into
  `results/esc/escAgeingCosts.csv`. No output reads it yet.
- **The Medicare reading** (`config.US['readings']`, the online appendix's 'transfers to the old'): stage (i)
  sweeps `USMedicare` (the U.S. with Medicare in τ0 and as a flat share of θ) beside the U.S. and summarises it;
  stage (ii) runs its counterfactuals (`shocksMedicare*`, France referenced to it). The site's B5 reads them
  (`OECD_Medicare`, host `USMedicare` of `OECD_Counterfactuals`).
- **The cross-country test** (A14, C14): stage (ii)'s entry `oecd26` runs `python/US/runOECD26.py` once per variant of
  `config.US['oecd26']['variants']` every time (seconds when the rows are current: they are keyed on their inputs
  and the U.S. β, #13) into `results/oecd26/`; stage (0)'s `oecd26Sample.py` sets the sample. The paper's variant
  (the cost transported, `spec`; the β rule; turnout; the design reading) lives in `config.US['oecd26']` alone:
  the readers (`datasets.oecd26*`) and the builders (`tablesOECD26.PAPER`) default to it, and a builder at another
  variant carries it in its suffix (`_size`, `_commonR`, `_cses`, `_29`). `datasets.oecd26Anchor` refuses an anchor
  solved at another U.S. β or on the coarse grid, and `oecd26Layer` a row of another anchor. Until the rows of the
  configured spec exist the registered `OECD26_*` outputs are `MissingInput`; the site's C6 shows all 29 and CSES turnout.
- **Argentina's GDP** is formal plus informal output, `Y + Y0` in the shock and sweep csvs (#3, 2026-10-23):
  `datasets` reads savings over GDP as s/(Y+Y0) (`savingsRatePath`; the sweeps' `srGDP` as `sr`, their formal-output
  rate as `srFormal`), spending as τ(1-α)Y/(Y+Y0) (`spendingPath`) and table 2's formal benefits from `d_biAvg`
  (`formalBenefitChange`); `config.argTaxTarget` restates `model.taxTarget` and `calibrationSummary` checks the
  calibrated τ against it. Not wired: the pre-reform ε = 0 calibration and its reform (`--epsPre0`,
  `informalSavings_rhoGridCommonXEpsPre0.csv`, `*_commonX_epsPre0.csv`) and `python/InformalSavings/
  reformDiagnostics.py` (`results/shocks/ARG_reform{FOC,B5,HouseholdSavings,Refine}_commonX.csv`); commands in
  `REPLICATION.md` §3.
- **The review's smaller U.S. numbers** (package C5, not wired): `python/US/c5Numbers.py` and a `runShocksUS.py
  --out` run at every ρ of the sweep write `results/numerical/C5_*.csv` (C.1's critical turnout ratio, the ranking of
  the counterfactuals, the marginal loss, λ against elasticities, index units, the design's response to inequality,
  τ_2020(s_2019), the strategic term); only the site's `US_TaxState` and `US_Strategic` read them. Commands in `REPLICATION.md` §3, numbers in
  `archive/notes/reviewResponse_2026-10/ledger_C5.md`.
- **Appendix D's checks** (package C4, not wired): `python/{US,InformalSavings}/runHorizon.py` re-solve the calibrated
  economies at other horizons and under the steady-state terminal condition, and take the tax rule's first-order-condition
  residuals off the grid, into `results/numerical/` (`{US,ARG}_horizon*`, `*_residuals*`, `US_jumps`, `US_derivativeScheme`);
  `NUM_Horizon`, `NUM_Residuals` and the site's `NUM_HorizonPaths` read them. Commands in `REPLICATION.md` §3,
  numbers in `archive/notes/reviewResponse_2026-10/ledger_C4.md` and `ledger_C6.md` §5.

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications, calendars, unit conversions; imports nothing from the models |
| `datasets.py` | the only module that knows the `results/` layout and column names, both arms |
| `tables.py`, `figures.py` | Argentina builders, one function per output; `figures` owns the house style |
| `tablesUS.py`, `figuresUS.py` | US/France/UK builders, including section 7's `escCalibrationTable` (`US_ESC_Calibration`) and `escOverview` (`US_ESC_overview`), appendix G.1's `ukEscCalibrationTable` (`UK_ESC_Calibration`) and `escCountryTable` (`US_ESC_Country`) |
| `build.py` | stage (iii): the output registry for both arms, and the copy into `writing/Paper` (not for `ONLINE_ONLY`) |
| `tablesOA.py`, `figuresOA.py` | the online appendix's own exhibits: figure 1's data, the calibrations across ρ and under the two treatments of leisure, the regroupings, the two costs, the timing of the design choice, the numerical checks; `figuresOA.escPathPaper` is the paper's path figure (`US_ESC_Path`) |
| `siteData.py` | the datasets of the online appendix's interactive figures (kind `data`, `results/paper/Data/*.csv`): Argentina's reform paths, the design-given and the design-chosen counterfactuals, the endogenous-design paths; each in the paper's units and checked against the file it duplicates |
| `onlineAppendix.py`, `texTable.py` | `build.py --site`: the registry of the online appendix's exhibits (`EXHIBITS`), their blocks (tables as HTML, figures as svg, an interactive figure's caption and note), the datasets, the palette, `_variables.yml` and the `\oa` macros with the retired keys aliased; reads `results/paper` and the paper's tex only. `test_onlineAppendix.py` checks them and ties each dataset to the paper's figure (a fast suite of `python/runTests.py`) |
| `compareResults.py` | reading a run: every changed csv under `results/` against a commit, rows aligned on the file's keys, the largest difference per column and the columns added (writes nothing) |
| `dataTargets.py`, `oecdFigure1.py` | stage (0) |
| `oecd29Data.py` | stage (0), not wired: the 29 countries' $\nu_t$, income groups and secondary inputs for calibrating the log model to each (`data/oecd29*.csv`, `notes/data_oecd29.md`) |
| `oecd26Sample.py` | stage (0), not wired, no network: the sample of the cross-country test, informal employment above 25% dropped (`data/oecd26_sample.csv`); the rule lives here only |
| `tablesHorizon.py` | appendix D: the horizon and terminal condition (`NUM_Horizon`, and date by date for the site, `NUM_HorizonPaths`), the residuals off the grid (`NUM_Residuals`); its counts table is `tablesOA.numSelection` (`NUM_Selection`, grouped by solve; file by file on the site, `NUM_SelectionFiles`) |
| `tablesOECD26.py`, `figuresOECD26.py` | the cross-country test (`results/oecd26/`, `python/US/runOECD26.py`): figure 1.1's relations with the model's layer 1 beside the data (`OECD26_Layer1`; layer 2 by argument), the slopes of data and both layers (`OECD26_Slopes`), the calibrated `ω`'s (`OECD26_Omega`); the turnout, sample and design reading of the online appendix's variants by argument. `test_oecd26.py` checks them on synthetic csvs |

## Outputs wired (51)

Every generated `.tex` carries a `%% Source:` banner with the csv it was read from; `--list` reports what is
buildable now. Every table row ends in a `% row: <key>` comment (`tables.rowKey`) and every figure also writes
`.svg` and `.marks.json` (`figures._save`, `figures.mark`): the site shows the svg, and `test_onlineAppendix.py`
reads the marks to tie each dataset of the site to the paper's figure. The paper inputs 21 outputs (the
calibration and household tables, `ArgentinaUniversal`, `ARG_CRRA_LOG`, `US_overview`, `US_ESC_Calibration`,
`US_ESC_overview`, `OECDdata`, appendix G's `UK_ESC_Calibration`, `US_ESC_Country` and `US_ESC_Path`, the
cross-country test's `OECD26_*` at the design in force in 2020, and appendix D's `NUM_Horizon`, `NUM_Residuals`
and `NUM_Selection`, the counts grouped by solve); the online appendix's 41 exhibits (`onlineAppendix.EXHIBITS`)
read 33 outputs, of which the 28 `ONLINE_ONLY` (the four `data` outputs among them, the `OECD26_*_29` and
`_cses` variants, `OECD_Medicare`, `US_TaxState`, `US_Strategic`, `NUM_HorizonPaths`, `NUM_SelectionFiles`) are never copied into
`writing/Paper`. The 59 outputs neither input nor shown (the
`_vectorX` twins, the counterfactual and ESC tables, the ρ-grid, path and ξ tables) were retired with their
builders on 2026-10-09. Every US counterfactual is a new equilibrium path read at 2020 (`python/US/shocks.py`).

## Traps

One line each; measurements in `archive/readmes/paper_README_2026-09-11.md`.

- A pinned `θ` does not survive a composite shock on its own (#9); the composites re-install it.
- `build.py` backs up a hand-written file once, to `results/paper/superseded/`; re-runs detect their banner.
- The workweek is a normalisation: `config.workweekHours(h, hRef)` = `42.54·h/hRef`, per ρ. Never `h·7·12`.
- The pre-reform savings rate is per ρ in both arms; difference against that ρ's own baseline.
- The Argentina ρ march is seeded at its anchor (`config.ARG['anchorGuess']` → `--x0`); retune if α or the
  K/Y target moves.
- `datasets.seedSavings` derives `s_{t0-1}` two ways and raises if they disagree. Keep the guard.
- Vectors go through the summary csv as JSON (numpy 2's `np.float64(…)` repr was once scraped as 64.0).
- The long-run figure period must clear `T` (`figures.argCrraLog` refuses).
- `datasets.epsThetaGrid` requires a complete rectangle AND exactly one `statusQuo` row matching
  `calibrationSummary` (#13).
- Colours: the categorical blue/orange pair in fixed order; `figures.THETA_RAMP` for a continuous parameter.
- A figure's type is set at `figsize`, read at a `\linewidth` of 5.91 in; size the figure near the measure
  and pass `titlesize`/`labelsize` to `figures._panel`; check the rendered page, not the png.
- A `% row:` key is the LAST thing on its line (`tables.keyed`); a tagged mark is one artist (a scatter
  collection carries one gid for all its points), and `_save` raises if an id is not exactly once in the svg.
- `--map` and `--list` re-save every figure and the PDFs carry a creation date: `git checkout` the ones that
  differ by bytes alone.
- The online appendix's PDF edition (not built now) must render with `pdf-engine: pdflatex` and
  `latex-auto-install: false`: a failed LuaLaTeX run once made Quarto update the machine's TeX Live.

US arm:

- Stage (i) is order-dependent: the full US sweep before any EU sweep (`runCalibrationUS.py` enforces).
- One savings unit, `s/Y`, everywhere: `datasets.US_SR` = `srOverY`; the ESC csvs are converted by
  `(1-α)` (`escSavingsOverY`). A counterfactual is the change against that ρ's own baseline; an ESC
  reading (figure 7.1, `siteData`) against the baseline of the *same reading*, θ pinned or chosen (one common baseline
  would put the gap between the two into every pinned reading).
- `workweek` in the shock csv is already in hours; `config.pct` escapes `%` for tex, never into a figure.
- A `createCopyFromt0` copy's `db['dates']` is stale; `config.usCalendar()` reads the workbook instead.
- The income-distribution row holds `θ` (the `freeTheta` entry keeps the other reading).
- The CRRA ESC csvs hold `method` = exact (published) and path (the cross-check) side by side;
  `datasets.escMethod` selects and never falls back. An exact row missing is `MissingInput`.
- An ESC calibration row without `Vtilde`, `fStar`, `f0`, `τ0` predates `'size'`; `datasets.escWedge` then
  computes the two `f` from the `'scale'` form and refuses any other spec.
- The two variants check each other: baseline, `θ`, ageing and voting come back identical (≤5e-15),
  income distribution and all-three differ, leisure differs in the workweek only.
