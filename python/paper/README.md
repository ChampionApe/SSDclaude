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
| (i) calibration | `runCalibration.py` | `runCalibrationUS.py` | `results/calibration/`, `results/paper/*Summary.csv` | ~3.2 h / ~20 min |
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/`, `results/esc/`, `results/oecd26/` | ~50 min / ~30 s (+ESC) |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |
| online appendix | `build.py --site`, then `quarto render writing/OnlineAppendix` | the same | `writing/OnlineAppendix/{_generated,_book,_variables.yml}`, `writing/Paper/onlineAppendix.tex` | ~1 min |

- Stage (ii) has `main` (the default) and `prepub` (`--prepub`; `--all` for both), the second run once before
  submission: the exact CRRA ESC leg (~3 h), the timing checks (~3.5 h), the stationary-vs-date-specific checks.
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
  'size', `comparisonSpec` 'scale'; under 'size' `phi` is a dummy key and `p` holds λ), the Π-inclusive cost
  `'sizePiR'` (`esc['costVariants']`, its `--tag Costs` csvs, `escAgeingCosts.csv`; the deep test under it,
  `escCountryCosts`), the Medicare reading (`readings`, the site's B5).
- **The cross-country test** (A14, C14, R6): stage (ii)'s entry `oecd26` runs `python/US/runOECD26.py` once per
  variant of `config.US['oecd26']['variants']` (seconds when the rows are current: keyed on their inputs and the U.S.
  β, #13). The paper's variant (`spec` 'sizePiR', the U.S. ε, printed `\varepsilon`, never the universal pension's
  `\epsilon`; β 'common'; turnout 'cps'; the design in force in 2020) and section 6's `spendingSpec` ('none') live in
  `config.US['oecd26']` alone; builders default to it, one at another variant carries it in its suffix (`_size`,
  `_commonR`, `_cses`, `_29`). `datasets.oecd26Anchor`/`oecd26Layer` raise `StaleInput` on an anchor of another U.S.
  β or grid, or a row of another anchor; `OECD26_Robustness` and `OECD26_Reconcile` print `--` there, never a value.
- **Argentina's GDP** is formal plus informal output, `Y + Y0` (#3): `datasets` reads savings and spending over it
  (`savingsRatePath`, `spendingPath`) and `config.argTaxTarget` checks the calibrated τ. Not wired: the pre-reform
  ε = 0 calibration and `reformDiagnostics.py` (`REPLICATION.md` §3).
- Not wired, commands in `REPLICATION.md` §3: C5's smaller U.S. numbers (`python/US/c5Numbers.py` ->
  `results/numerical/C5_*.csv`; the site's `US_TaxState`, `US_Strategic` read two) and C4's appendix D checks
  (`runHorizon.py` -> `results/numerical/`; `NUM_Horizon`, `NUM_Residuals`, `NUM_HorizonPaths` read them).

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications, calendars, unit conversions; imports nothing from the models |
| `datasets.py` | the only module that knows the `results/` layout and column names, both arms |
| `tables.py`, `figures.py` | Argentina builders, one function per output; `figures` owns the house style |
| `tablesUS.py`, `figuresUS.py` | US/France/UK builders: the calibration (`USUKFRCalibration`; `USFRCalibration`, the U.S. and France), section 7's `US_ESC_Calibration`, `US_ESC_overview`, appendix G's deep test `US_ESC_Country` (the UK and France under the U.S. λ and ε, with each one's Π/R; the note's U.S. ratio checked to make ε and λ one cost), `UK_ESC_Calibration` |
| `build.py` | stage (iii): the output registry for both arms, the copy into `writing/Paper` (not for `ONLINE_ONLY`; a figure's `_note.tex` beside its pdf) |
| `tablesOA.py`, `figuresOA.py` | the online appendix's own exhibits; `figuresOA.escPathPaper` is the paper's `US_ESC_Path` |
| `siteData.py` | the datasets of the site's interactive figures (kind `data`), each checked against the file it duplicates |
| `onlineAppendix.py`, `texTable.py` | `build.py --site`: the exhibits' registry (`EXHIBITS`), their blocks, the datasets, `_variables.yml`, the `\oa` macros (retired keys aliased); `test_onlineAppendix.py` checks them |
| `compareResults.py` | every changed csv under `results/` against a commit, rows aligned on the file's keys (writes nothing) |
| `dataTargets.py`, `oecdFigure1.py` | stage (0) |
| `oecd29Data.py`, `oecd26Sample.py` | stage (0), not wired: the 29 countries' inputs (`data/oecd29*.csv`, `notes/data_oecd29.md`); the sample rule (`data/oecd26_sample.csv`) |
| `tablesHorizon.py` | appendix D: `NUM_Horizon` (`NUM_HorizonPaths` on the site), `NUM_Residuals`; the counts are `tablesOA.numSelection` |
| `tablesOECD26.py`, `figuresOECD26.py` | the cross-country test (`results/oecd26/`): section 6's spending at the observed designs without the cost (`OECD26_Spending`, its note with the slopes), layer 1 beside the data (`OECD26_Layer1`), the five slopes (`OECD26_Slopes`), the `ω`'s (`OECD26_Omega`), appendix H's design slopes under λ/ε × common β/R × turnout (`OECD26_Robustness`) and the U.S., the UK and France measured both ways (`OECD26_Reconcile`). `test_oecd26.py` checks them on synthetic csvs |

## Outputs wired (55)

Every generated `.tex` carries a `%% Source:` banner; `--list` reports what is buildable now. Every table row ends
in a `% row: <key>` comment (`tables.rowKey`) and every figure writes `.svg` and `.marks.json` (`figures._save`),
which tie the site's datasets to the paper's figures. The paper inputs 23 outputs; the online appendix's 38 exhibits
read 33 outputs, of which the 31 `ONLINE_ONLY` (the `data` outputs, the `OECD26_*_29`, `_cses` and `_size`
variants, `OECD_Medicare`, `US_TaxState`, `US_Strategic`, `NUM_HorizonPaths`, `NUM_Selection`, `NUM_SelectionFiles`)
are never copied into `writing/Paper`; appendix D states the counts in words (2026-10-28). The 59 outputs retired on 2026-10-09 went with their builders, and so did the UK-host three of
2026-10-27 (`FRUK_`/`UKUS_householdheterogeneity`, `OECD_Regroupings`; their last builds archived).

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
