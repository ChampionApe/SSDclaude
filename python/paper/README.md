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

- Stage (ii) has two parts in both arms. `main` (the default) is a routine rebuild: sweeps, the exogenous
  shocks in both variants, the LOG ESC leg. `prepub` (`--prepub`; `--all` for both) is run once before
  submission: the exact CRRA ESC leg (`runESCcrra.py --exact`, the published method,
  `config.US['esc']['exact']`, ~3 h for two ρ in parallel), the R3 timing checks (~3.5 h), and the
  **stationary-vs-date-specific policy checks** behind `sec:numerical`'s literature paragraph (US taxes
  under CRRA, the endogenous design under LOG and exact CRRA, ~1 h; Argentina through `runShocks.py
  --prepub`, ~10 min). Those write `results/numerical/`, which no paper output reads.
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
- **The UK exercise** (2026-09-22): `config.US['ukHost']` names the host of the second French-characteristics
  arm; stage (i) sweeps `FRUK`, stage (ii) runs `runShocksUS.py --host UK` under a `requires` guard, stage
  (iii) builds `UK_OtherShocks`, `UK_CRRA_OtherShocks`, `FRUK_householdheterogeneity` (+ twins).
  Since 2026-09-29 also under the chosen design, at the UK's own λ (`config.US['esc']['uk']`): stage (i)
  `--prepub` calibrates it under CRRA, stage (ii) runs `escShocksUK` (LOG), `escShocksCRRAUK` (prepub) and
  the `escExperimentsUK` merge, stage (iii) builds `UK_ESC_{IncomeDistr,Voting,FrenchAll}` and the two
  US-vs-UK figures `UKUS_French` (+ twin), `UKUS_ESC_French`; `UKUS_householdheterogeneity` documents the
  UK at US income groups.
- **The ESC cost specification** (2026-09-24, `notes/plan_escSizeLeak.md`): `config.US['esc']['spec'] =
  'size'` is the paper's, `comparisonSpec = 'scale'` the previous wedge, kept as one appendix table
  (`US_ESC_ScaleWedge`). `phi` is a dummy key under `'size'` (every ESC csv is keyed on it); the `p` column
  holds λ, printed as $\lambda$. Stage (i) calibrates both specs under LOG and the paper's spec under CRRA,
  with a per-(spec, ρ) scan bracket from `config.escBracket` (the `'size'` brackets were set from the LOG
  λ = 8.643); the φ-robustness runs exist only for a spec whose `f` reads φ. Stage (ii)'s LOG entries run
  `--spec size scale` so the comparison arm is rebuilt with the paper's; the CRRA and stationary entries run
  the paper's spec. `US_ESC_Country` (the UK, France and the UK at US cuts under the US λ, and their own)
  replaces `UK_ESC_Calibration`, whose builder stays callable.

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications, calendars, unit conversions; imports nothing from the models |
| `datasets.py` | the only module that knows the `results/` layout and column names, both arms |
| `tables.py`, `figures.py` | Argentina builders, one function per output; `figures` owns the house style |
| `tablesUS.py`, `figuresUS.py` | US/France/UK builders |
| `build.py` | stage (iii): the output registry for both arms, and the copy into `writing/Paper` |
| `dataTargets.py` | stage (0) |

## Outputs wired (54)

Each built file names its own input: every generated `.tex` and its `.pdf` sibling carry a
`%% Source:` banner with the csv it was read from, and `--list` reports what is buildable now. The
registry itself is `build.py`'s table -- that, not this file, is the list of 54.

Every US and Argentina table and figure is registered twice (headline and `_vectorX`); the ESC outputs
headline only. Only `ArgentinaCalibration_vectorX` is `\input` in the paper. Since 2026-09-29 the OECD
appendix is three files: `Appendix/CalibrationOECD.tex` (`app:US`, the five heterogeneity tables),
`US.tex` (`app:USrob`: CRRA, every `_vectorX` twin, `US_ESC_Ageing` + `US_ESC_ScaleWedge`) and
`UKvsUS.tex` (`app:UKUS`: the French-characteristics tables, US and UK, pinned then chosen design, with
`US_ESC_Country`); the main text keeps the discussion. Every US counterfactual is a new
equilibrium path read at 2020 (`python/US/shocks.py`, `writing/US/num_esc.tex`); the French tables carry the
all-three row and France's own path.

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
