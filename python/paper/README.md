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

- The US arm's stages (i)/(ii) have two parts. `main` (the default) is a routine rebuild: sweeps, the LOG
  wedge, the exogenous shocks in both variants, the LOG ESC leg. `prepub` (`--prepub`; `--all` for both)
  is run once before submission: the exact CRRA wedge and ESC leg (`runESCcrra.py --exact`, the published
  method, `config.US['esc']['exact']`), the φ-robustness wedges and the R3 timing checks; ~3.5 h.
- Every stage skips work whose output exists; `--force` overrides, `--list` reports, `--dry` prints the
  delegated commands. The ESC merge entry always runs. **`--force` whenever anything upstream moved, a recalibration above all**: the
  calibration sweeps and `sweepEpsThetaGrid.py` resume from their own csv keyed on the parameter point
  alone (finding #13). It is forwarded to the child only where the child resumes.
- Stage (iii) imports no model code and unpickles nothing, so a rebuild is seconds and can never turn into
  a solve. An output whose inputs are missing is reported and skipped (`datasets.MissingInput`), never
  partially written.
- Stages (i)/(ii) are declarations: the model folders' scripts do the work, and `config.py` records the
  settings the published numbers were produced at. **Change a paper number there first.**
- Both arms carry two calibration variants; `config.US['commonX']` and `config.ARG['commonX']` (both
  True since 2026-09-12) name each headline. Every US and Argentina builder takes `commonX`: the plain
  name and tex label are the headline, the `_vectorX`/`_commonX` twin follows (`config.variantSuffix(commonX, arm)`,
  `build._variants`). Argentina's variant lives in its own sweep csv, instance directory and suffixed
  shock/sweep csvs (`config.argSweepCsv`, `argInstanceDir`, `argShockTemplate`); `runCalibration.py` /
  `runShocks.py --commonX` add it. The ESC leg runs under the US headline only.
- Stage (0) is the only network access (Penn World Table via FRED); it writes a calibration *input* to
  `data/` and skips existing output, so the committed csv means no other stage touches the network.

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications, calendars, unit conversions; imports nothing from the models |
| `datasets.py` | the only module that knows the `results/` layout and column names, both arms |
| `tables.py`, `figures.py` | Argentina builders, one function per output; `figures` owns the house style |
| `tablesUS.py`, `figuresUS.py` | US/France/UK builders |
| `build.py` | stage (iii): the output registry for both arms, and the copy into `writing/Paper` |
| `dataTargets.py` | stage (0) |

## Outputs wired (39)

| Paper file | Built from |
|---|---|
| `Tables/ArgentinaCalibration.tex` | `results/paper/calibrationSummary.csv` |
| `Tables/ArgentinaUniversal.tex` | `eeOnly_match_rho1.0000.csv` + `universal_match_rho1.0000.csv` |
| `Tables/Argentina_funcOfRho.tex` | `universal_match_rho*.csv` |
| `Figs/ARG_LOG_FourInOne.pdf` | `results/sweeps/epsThetaGrid_rho1.0000.csv` |
| `Figs/ARG_CRRA_LOG.pdf` | `universal_match_rho*.csv` |
| `Tables/USUKFRCalibration.tex`, `Tables/{US,FR,UK}_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` |
| `Tables/US_{PensChars,Ageing,OtherShocks}.tex` | `US_shocksCommonX.csv`, ρ = 1 |
| `Tables/US_CRRA_{PensChars,Ageing,OtherShocks}.tex` | `US_shocksCommonX.csv`, ρ ∈ {0.5, 1, 2} |
| `Figs/US_overview.pdf` | `US_shocksCommonX.csv`, all ρ; three panels |
| `Tables/US_ESC_Calibration.tex` | `results/esc/escCalibration{,CRRA}.csv` (CRRA rows: `method` = exact) |
| `Tables/US_ESC_{Ageing,IncomeDistr,Voting,FrenchAll}.tex` | `results/esc/escExperiments.csv`, ρ ∈ {0.5, 1, 2}, CRRA rows at `method` = exact |
| `Tables/UK_ESC_Calibration.tex` | `results/esc/escCountry.csv`, ρ = 1 only |
| `Figs/US_ESC_overview.pdf` | `escExperiments.csv`, 2×2 dumbbells (open = `θ` pinned, filled = chosen) |

Every US and Argentina table and figure is registered twice (headline and `_vectorX`, both arms leading
with common X since 2026-09-12); the ESC outputs headline only. Only `ArgentinaCalibration_vectorX` is
`\input` in the paper -- the other Argentina twins are built but print the same numbers as the headline.
The French leisure row is no longer printed (2026-09-11) but still runs, sits in every csv and inside
`frAll`. Every US counterfactual is a new equilibrium path read at 2020 (`python/US/shocks.py`,
`writing/US/num_esc.tex`); the French tables carry the all-three row and France's own path, which fails by
construction under the `flat` spec.

## Traps

One line each; measurements in `archive/readmes/paper_README_2026-09-11.md`.

- A pinned `θ` does not survive a composite shock on its own (#9); the composites re-install it.
- `build.py` backs up a hand-written file once, to `results/paper/superseded/` (deleted 2026-08-24;
  originals at `bfba998:`). Re-runs detect their own `%% GENERATED` banner.
- The workweek is a normalisation: `config.workweekHours(h, hRef)` = `42.54·h/hRef`, per ρ. Never
  `h·7·12`.
- The pre-reform savings rate is per ρ in both arms; difference against that ρ's own baseline.
  `Argentina_funcOfRho` prints one shared pre-reform row (τ, workweek; savings cell `--`) and raises if the
  pre-reform τ is not common.
- The Argentina ρ march is seeded at its anchor (`config.ARG['anchorGuess']` → `--x0`); retune if α or the
  K/Y target moves.
- `datasets.seedSavings` derives `s_{t0-1}` two ways and raises if they disagree. Keep the guard.
- Vectors go through the summary csv as JSON (numpy 2's `np.float64(…)` repr was once scraped as 64.0).
- The long-run figure period must clear `T` (`figures.argCrraLog` refuses); the default `t0+1` is where the
  short- and long-run savings series nearly coincide, a real feature of the path.
- `datasets.epsThetaGrid` requires a complete rectangle AND exactly one `statusQuo` row matching
  `calibrationSummary` (#13).
- Colours: the categorical blue/orange pair in fixed order; `figures.THETA_RAMP` for a continuous
  parameter. Do not substitute by eye.

US arm:

- Stage (i) is order-dependent: the full US sweep before any EU sweep (`runCalibrationUS.py` enforces).
- One savings unit, `s/Y`, everywhere: `datasets.US_SR` = `srOverY`; the ESC csvs are converted by
  `(1-α)` with α from the summary csv (`escSavingsOverY`). Counterfactual tables print the change against
  that ρ's own baseline (`config.pp`, `tables.SRNOTE`); the ESC tables against the *endogenous* baseline.
- `workweek` in the shock csv is already in hours; do not re-derive it from `hbar`.
- A `createCopyFromt0` copy's `db['dates']` is stale; `config.usCalendar()` reads the workbook instead.
- `config.pct` escapes `%` for tex; never into a figure.
- The income-distribution row holds `θ` (the `freeTheta` entry keeps the other reading).
- The CRRA ESC csvs hold two vintages side by side, `method` = exact (published) and path (the
  cross-check); `datasets.escMethod` selects and never falls back. An exact row missing is `MissingInput`.
- A detached pipeline log must not be held open while it runs (`crossCuttingFindings.md` #14).
- The two variants check each other: baseline, `θ`, ageing and voting come back identical (≤5e-15),
  income distribution and all-three differ, leisure differs in the workweek only.
