# paper

The pipeline that turns solved models into `writing/Paper`'s tables and figures. It owns no economics;
every number it emits is read off `results/`.

## Three stages, run in order

Two arms, Argentina (`python/InformalSavings/`) and the OECD economies (`python/US/`), with separate stage
(i)/(ii) entry points; they share `config.py`, `results/` and stage (iii).

| Stage | Argentina | US / France / UK | Writes | Cost (cold, ARG / US) |
|---|---|---|---|---|
| (0) data targets | `dataTargets.py` | — | `data/argentina_*.csv` | seconds |
| (i) calibration | `runCalibration.py` | `runCalibrationUS.py` | `results/calibration/`, `results/paper/*Summary.csv` | ~3.2 h / ~20 min |
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/`, `results/esc/` | ~50 min / ~30 s (+ESC) |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |
| online appendix | `build.py --site`, then `quarto render writing/OnlineAppendix` | the same | `writing/OnlineAppendix/{_generated,_book}`, `writing/Paper/onlineAppendix.tex` | ~1 min |

- Stage (ii) has two parts in both arms. `main` (the default) is a routine rebuild: sweeps, the exogenous
  shocks in both variants, the LOG ESC leg. `prepub` (`--prepub`; `--all` for both) is run once before
  submission: the exact CRRA ESC leg (`runESCcrra.py --exact`, the published method,
  `config.US['esc']['exact']`, ~3 h for two ρ in parallel), the R3 timing checks (~3.5 h), and the
  **stationary-vs-date-specific policy checks** behind `sec:numerical`'s literature paragraph (US taxes
  under CRRA, the endogenous design under LOG and exact CRRA, ~1 h; Argentina through `runShocks.py
  --prepub`, ~10 min). Those write `results/numerical/`, which only the online appendix reads (`NUM_Stationary`).
- Every stage skips work whose output exists; `--force` overrides, `--list` reports, `--dry` prints the
  delegated commands. The ESC merge entry always runs. **`--force` whenever anything upstream moved, a
  recalibration above all**: the calibration sweeps and `sweepEpsThetaGrid.py` resume from their own csv
  keyed on the parameter point alone (finding #13). It is forwarded to the child only where the child resumes.
- Stage (iii) imports no model code and unpickles nothing, so a rebuild is seconds and can never turn into
  a solve. An output whose inputs are missing is reported and skipped (`datasets.MissingInput`), never
  partially written.
- Stages (i)/(ii) are declarations: the model folders' scripts do the work, and `config.py` records the
  settings the published numbers were produced at. **Change a paper number there first.**
- Both arms carry two calibration variants; `config.US['commonX']` and `config.ARG['commonX']` (both
  True since 2026-09-12) name each headline. Every US and Argentina builder takes `commonX`: the plain
  name and tex label are the headline, the `_vectorX`/`_commonX` twin follows (`config.variantSuffix`,
  `build._variants`). Argentina's variant lives in its own sweep csv, instance directory and suffixed
  shock/sweep csvs; `runCalibration.py` / `runShocks.py --commonX` add it. The ESC leg runs under the US
  headline only. **Only a vector-X table names its calibration** (`config.variantNote`, empty under common
  X): the paper is the common-X calibration throughout and says so nowhere.
- Stage (0) is the only network access (Penn World Table via FRED); it writes a calibration *input* to
  `data/` and skips existing output, so the committed csv means no other stage touches the network.
- **Figure 1** (2026-09-30): a second stage (0) script, `oecdFigure1.py`, writes
  `data/oecdFigure1{,_sources}.csv` (OECD, PaG 2021, World Bank, WIID, WID); the entry `OECDdata` builds
  `Figs/OECDdata.pdf` and `oecdCorrelations.csv` from that csv alone. The paper inputs the PDF;
  `oecdFigure1.PLOT = NAMED` picks the sourced concepts (gate 1 call, 2026-09-30).
- **`--map`** rewrites the output table of `REPLICATION.md`, the referee-facing map: one row per registered
  output with the files it reads (traced through pandas at build time, not declared) and the tex files that
  input it. Run it after adding or renaming an output.
- **The UK as host** (`config.US['ukHost']`, the UK's own λ in `config.US['esc']['uk']`): stage (i) sweeps
  `FRUK` and, with `--prepub`, calibrates the UK's λ under CRRA; stage (ii) runs `runShocksUS.py --host UK`,
  `escShocksUK`, `escShocksCRRAUK` (prepub) and the `escExperimentsUK` merge; outputs `UK_*`, `FRUK_*`, `UKUS_*`.
- **The ESC cost** (`archive/notes/plan_escSizeLeak.md`): `config.US['esc']['spec'] = 'size'` is the paper's,
  `comparisonSpec = 'scale'` the cost on the design, which `US_ESC_ScaleWedge` sets beside it. `phi` is a dummy
  key under `'size'`; the `p` column holds λ. Stage (i) calibrates both under LOG and the paper's under CRRA
  (brackets `config.escBracket`); stage (ii)'s LOG entries run `--spec size scale`, the CRRA and stationary
  ones the paper's. `US_ESC_Country` holds the UK, France and the UK at US cuts under the US λ, and their own.

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications, calendars, unit conversions; imports nothing from the models |
| `datasets.py` | the only module that knows the `results/` layout and column names, both arms |
| `tables.py`, `figures.py` | Argentina builders, one function per output; `figures` owns the house style |
| `tablesUS.py`, `figuresUS.py` | US/France/UK builders |
| `build.py` | stage (iii): the output registry for both arms, and the copy into `writing/Paper` (not for `ONLINE_ONLY`) |
| `tablesOA.py`, `figuresOA.py` | the online appendix's own exhibits: figure 1's data, the calibrations across ρ, the endogenous design's path, ξ and timing, the numerical checks |
| `onlineAppendix.py`, `texTable.py` | `build.py --site`: the registry of the online appendix's sections and exhibits, the generated tables as HTML, the print edition's copies with every reference resolved, the `\oa` macros; reads `results/paper` and the paper's tex only. `test_onlineAppendix.py` checks them |
| `compareResults.py` | reading a run: every changed csv under `results/` against a commit, rows aligned on the file's keys, the largest difference per column and the columns added (writes nothing) |
| `dataTargets.py` | stage (0) |

## Outputs wired (81)

Each built file names its own input: every generated `.tex` carries a `%% Source:` banner with the csv it
was read from, and `--list` reports what is buildable now. The registry is `build.py`'s table; `--map` writes
which tex file inputs each output into `REPLICATION.md`. Every US and Argentina output is registered twice
(headline and `_vectorX`), the ESC outputs headline only. Every table row ends in a `% row: <key>` comment
(`tables.rowKey`) and every figure also writes `.svg` and `.marks.json` (`figures._save`, `figures.mark`): the
online appendix's handles from a mark to the table row that prints it. The 25 `ONLINE_ONLY` outputs are built
into `results/paper` and never copied into `writing/Paper`. Since 2026-10-06 the paper inputs the headline
tables its sections and appendices A–H cite (`RobustnessMap` in appendix H); the twins, the UK's CRRA and
endogenous-design tables and the scale-wedge comparison are the online appendix's (`notes/paper_onlineAppendix.md`).
Every US counterfactual is a new equilibrium path read at 2020 (`python/US/shocks.py`, `writing/US/num_esc.tex`).

## Traps

One line each; measurements in `archive/readmes/paper_README_2026-09-11.md`.

- A pinned `θ` does not survive a composite shock on its own (#9); the composites re-install it.
- `build.py` backs up a hand-written file once, to `results/paper/superseded/`. Re-runs detect their own
  `%% GENERATED` banner.
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
- A `% row:` key is the LAST thing on its line: several builders append `[1.25ex]` or `\hline` to a row after
  building it, and a comment placed before them swallows the spacing.
- A tagged mark is one artist (a scatter collection carries one gid for all its points); ids are ASCII and
  `_save` raises if one is not exactly once in the svg.
- The online appendix renders with `pdf-engine: pdflatex` and `latex-auto-install: false` (`_quarto.yml`): a
  failed LuaLaTeX run once made Quarto run `tlmgr update --all` on the machine's TeX Live (2026-10-06).
  Render HTML and PDF together; `quarto render --to pdf` alone empties `_book` of the HTML.

US arm:

- Stage (i) is order-dependent: the full US sweep before any EU sweep (`runCalibrationUS.py` enforces).
- One savings unit, `s/Y`, everywhere: `datasets.US_SR` = `srOverY`; the ESC csvs are converted by
  `(1-α)` (`escSavingsOverY`). Counterfactual tables print the change against that ρ's own baseline; the
  ESC tables against the *endogenous* baseline.
- `workweek` in the shock csv is already in hours; `config.pct` escapes `%` for tex, never into a figure.
- A `createCopyFromt0` copy's `db['dates']` is stale; `config.usCalendar()` reads the workbook instead.
- The income-distribution row holds `θ` (the `freeTheta` entry keeps the other reading).
- The CRRA ESC csvs hold two vintages side by side, `method` = exact (published) and path (the
  cross-check); `datasets.escMethod` selects and never falls back. An exact row missing is `MissingInput`.
- The ESC calibration csvs carry `Vtilde`, `fStar`, `f0`, `τ0` since 2026-09-24; a row from before lacks
  them, and `datasets.escWedge` then computes the two `f` from the `'scale'` form and refuses any other spec.
- A detached pipeline log must not be held open while it runs (#14).
- The two variants check each other: baseline, `θ`, ageing and voting come back identical (≤5e-15),
  income distribution and all-three differ, leisure differs in the workweek only.
