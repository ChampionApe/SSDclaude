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
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/`, `results/esc/` | ~50 min / ~30 s (+ESC) |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |
| online appendix | `build.py --site`, then `quarto render writing/OnlineAppendix` | the same | `writing/OnlineAppendix/{_generated,_book}`, `writing/Paper/onlineAppendix.tex` | ~1 min |

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
  naming the headline. Every US and Argentina builder takes `commonX`: the plain name and tex label are the
  headline, the `_vectorX` twin follows (`config.variantSuffix`, `build._variants`); only the twin names its
  calibration (`config.variantNote`). Argentina's variant has its own sweep csv, instance directory and
  suffixed shock/sweep csvs (`runCalibration.py`/`runShocks.py --commonX`). The ESC leg runs under the US
  headline only.
- Stage (0) is the only network access (Penn World Table via FRED; OECD, PaG 2021, World Bank, WIID and WID for
  figure 1); it writes inputs to `data/` and skips existing output. `oecdFigure1.PLOT = NAMED` plots the
  concepts figure 1's note names.
- **`--map`** rewrites the output table of `REPLICATION.md`: one row per registered output with the files it
  reads (traced through pandas at build time, not declared) and the tex files that input it.
- **The UK as host** (`config.US['ukHost']`, the UK's own λ in `config.US['esc']['uk']`): stage (i) sweeps
  `FRUK` and, with `--prepub`, calibrates the UK's λ under CRRA; stage (ii) runs `runShocksUS.py --host UK`,
  `escShocksUK`, `escShocksCRRAUK` (prepub) and the `escExperimentsUK` merge; outputs `UK_*`, `FRUK_*`, `UKUS_*`.
- **The ESC cost**: `config.US['esc']['spec'] = 'size'` is the paper's, `comparisonSpec = 'scale'` the earlier
  wedge that `US_ESC_ScaleWedge` sets beside it; under `'size'` `phi` is a dummy key and the `p` column holds λ.
  Stage (i) calibrates both under LOG and the paper's under CRRA (`config.escBracket`); stage (ii)'s LOG
  entries run both specs, the CRRA and stationary ones the paper's.

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications, calendars, unit conversions; imports nothing from the models |
| `datasets.py` | the only module that knows the `results/` layout and column names, both arms |
| `tables.py`, `figures.py` | Argentina builders, one function per output; `figures` owns the house style |
| `tablesUS.py`, `figuresUS.py` | US/France/UK builders, including `escSummary` (`US_ESC_Summary`) and `robustnessMap` (appendix G) |
| `build.py` | stage (iii): the output registry for both arms, and the copy into `writing/Paper` (not for `ONLINE_ONLY`) |
| `tablesOA.py`, `figuresOA.py` | the online appendix's own exhibits: figure 1's data, the calibrations across ρ, the endogenous design's path, ξ and timing, the numerical checks |
| `onlineAppendix.py`, `texTable.py` | `build.py --site`: the registry of the online appendix's sections and exhibits (each with its `text`), the generated tables as HTML, the print edition, the `\oa` macros; reads `results/paper` and the paper's tex only. `test_onlineAppendix.py` checks them (a fast suite of `python/runTests.py`) |
| `compareResults.py` | reading a run: every changed csv under `results/` against a commit, rows aligned on the file's keys, the largest difference per column and the columns added (writes nothing) |
| `dataTargets.py`, `oecdFigure1.py` | stage (0) |

## Outputs wired (82)

Every generated `.tex` carries a `%% Source:` banner with the csv it was read from; `--list` reports what is
buildable now. Every US and Argentina output is registered twice (headline and `_vectorX`), the ESC outputs
once. Every table row ends in a `% row: <key>` comment (`tables.rowKey`) and every figure also writes `.svg` and
`.marks.json` (`figures._save`, `figures.mark`), the online appendix's handles from a mark to its table row.
The paper inputs 15 outputs (the calibration and household tables, `ArgentinaUniversal`, `ARG_CRRA_LOG`,
`US_overview`, `US_ESC_Calibration`, `US_ESC_Country`, `US_ESC_overview`, `US_ESC_Summary`, `OECDdata`,
`RobustnessMap`); everything else is the online appendix's, the 25 `ONLINE_ONLY` outputs never copied into
`writing/Paper`. Every US counterfactual is a new equilibrium path read at 2020 (`python/US/shocks.py`).

## Traps

One line each; measurements in `archive/readmes/paper_README_2026-09-11.md`.

- A pinned `θ` does not survive a composite shock on its own (#9); the composites re-install it.
- `build.py` backs up a hand-written file once, to `results/paper/superseded/`; re-runs detect their banner.
- The workweek is a normalisation: `config.workweekHours(h, hRef)` = `42.54·h/hRef`, per ρ. Never `h·7·12`.
- The pre-reform savings rate is per ρ in both arms; difference against that ρ's own baseline.
  `Argentina_funcOfRho` raises if the pre-reform τ is not common.
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
- `--map` re-saves every figure and the PDFs carry a creation date: `git checkout` the ~17 that differ by bytes.
- The online appendix renders with `pdf-engine: pdflatex` and `latex-auto-install: false`: a failed LuaLaTeX
  run once made Quarto update the machine's TeX Live. Render HTML and PDF together; `--to pdf` alone empties
  `_book` of the HTML.

US arm:

- Stage (i) is order-dependent: the full US sweep before any EU sweep (`runCalibrationUS.py` enforces).
- One savings unit, `s/Y`, everywhere: `datasets.US_SR` = `srOverY`; the ESC csvs are converted by
  `(1-α)` (`escSavingsOverY`). Counterfactual tables print the change against that ρ's own baseline; the
  ESC tables against the *endogenous* baseline.
- `workweek` in the shock csv is already in hours; `config.pct` escapes `%` for tex, never into a figure.
- A `createCopyFromt0` copy's `db['dates']` is stale; `config.usCalendar()` reads the workbook instead.
- The income-distribution row holds `θ` (the `freeTheta` entry keeps the other reading).
- The CRRA ESC csvs hold `method` = exact (published) and path (the cross-check) side by side;
  `datasets.escMethod` selects and never falls back. An exact row missing is `MissingInput`.
- An ESC calibration row without `Vtilde`, `fStar`, `f0`, `τ0` predates `'size'`; `datasets.escWedge` then
  computes the two `f` from the `'scale'` form and refuses any other spec.
- The two variants check each other: baseline, `θ`, ageing and voting come back identical (≤5e-15),
  income distribution and all-three differ, leisure differs in the workweek only.
