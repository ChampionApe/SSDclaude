# paper

The pipeline that turns solved models into the tables and figures in `writing/Paper`. It is not a model:
it owns no economics, and every number it emits is read off `results/`.

## Three stages, run in order

Two model arms — Argentina (`python/InformalSavings/`) and the rich OECD economies (`python/US/`) — with
separate stage (i)/(ii) entry points, because they delegate to different experiment scripts. They share
`config.py`, `results/`, and one stage (iii).

| Stage | Argentina | US / France / UK | Writes | Cost (cold, ARG / US) |
|---|---|---|---|---|
| (0) data targets | `dataTargets.py` | — | `data/argentina_*.csv` | seconds |
| (i) calibration | `runCalibration.py` | `runCalibrationUS.py` | `results/calibration/`, `results/paper/*Summary.csv` | ~2 h / ~20 min |
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/` | ~2.5 h / ~30 s |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |

Every stage **skips work whose output already exists**, so running them in order is safe: it costs seconds
when nothing has changed and only pays for what is genuinely missing. `--force` overrides, `--list`
reports without doing anything, `--dry` prints the commands stage (i)/(ii) would delegate.

**Stage (iii) imports no model code and unpickles nothing.** It reads csv, writes tex and pdf. That is
what makes it re-runnable after every caption or rounding change, and it is why the expensive stages are
separate entry points rather than a `--refresh` flag: a paper rebuild can never silently turn into a
2.5-hour solve. The corollary is that **an output whose inputs are missing is reported and skipped, never
partially written** — an experiment that has not been run must not be able to look like a table that has.

Stages (i) and (ii) are *declarations*, not implementations: the experiment scripts under the model
folders keep their own CLIs and do the work, and these four files record the settings the published
numbers were produced at. `config.py` is where a paper number's specification actually starts.

## Files

| | |
|---|---|
| `config.py` | paths, the `ARG` and `US` specifications (ρ grids, reform rule, grid settings), both calendars, the unit conversions. Imports nothing from the model — **change a paper number here first** |
| `datasets.py` | the only module that knows the `results/` file layout and column names, for both arms. Raises `MissingInput`, which `build.py` turns into a skipped output |
| `tables.py`, `figures.py` | the Argentina builders, one function per paper output |
| `tablesUS.py`, `figuresUS.py` | the US/France/UK builders. `figuresUS` imports the house style from `figures` rather than restating it, so the two arms stay one visual family |
| `build.py` | stage (iii): the output registry for both arms, and the copy into `writing/Paper` |
| `dataTargets.py` | **stage (0), and the only part of the pipeline that touches the network** |

`dataTargets.py` derives Argentina's capital-output target from the Penn World Table (via FRED) and writes
it to `data/`, not `results/`: it is a calibration *input*, on the same footing as the workbook. It exists
because that target is a reading of an external series at a chosen year, not a number anyone typed. It
writes both the year and the window-mean reading every run and names only one `capitalOutputRatio`
(`--target` chooses); like every other stage it skips existing output, so the committed csv means no other
stage ever needs the network.

## Outputs wired (23)

| Paper file | Built from |
|---|---|
| `Tables/ArgentinaCalibration.tex` | `results/paper/calibrationSummary.csv` |
| `Tables/ArgentinaUniversal.tex` | `eeOnly_match_rho1.0000.csv` + `universal_match_rho1.0000.csv` |
| `Tables/Argentina_funcOfRho.tex` | `universal_match_rho*.csv` |
| `Figs/ARG_LOG_FourInOne.pdf` | `results/sweeps/epsThetaGrid_rho1.0000.csv` |
| `Figs/ARG_CRRA_LOG.pdf` | `universal_match_rho*.csv` |
| `Tables/USUKFRCalibration.tex`, `Tables/{US,FR,UK}_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` |
| `Tables/US_{PensChars,Ageing,OtherShocks}.tex` | `US_shocks.csv`, ρ = 1 |
| `Tables/US_CRRA_{PensChars,Ageing,OtherShocks}.tex` | `US_shocks.csv`, ρ ∈ {0.5, 1, 2} |
| `Figs/US_taxOverview.pdf` / `Figs/USX_taxOverview.pdf` | `US_shocks.csv` / `US_shocksCommonX.csv`, all ρ |
| `Tables/US_ESC_Calibration.tex` | `results/esc/escCalibration{,CRRA}.csv` |
| `Tables/US_ESC_{Ageing,IncomeDistr,Leisure,Voting,FrenchAll}.tex` | `results/esc/escExperiments.csv`, ρ ∈ {0.5, 1, 2} |

Nothing in `writing/Paper` remains unwired.

**The ESC leg runs through all three stages.** Stage (i) checks the wedge calibrations per (ρ, spec) at
`config.US['esc']`'s φ and delegates the missing ones to `python/US/runESC.py` (LOG) / `runESCcrra.py`
(CRRA) — expensive where missing (~25–30 min per CRRA combination). Stage (ii) declares the counterfactual
runs and the merge whose csv is all stage (iii) reads. The ESC drivers **merge into their csvs rather than
overwriting**, so the pipeline can re-run exactly a missing (ρ, spec); the other experiment scripts own
their whole csv and do not need this.

**Every US counterfactual is a new equilibrium path read at 2020** — the ESC appendix and the main-text
tables alike. The changed characteristics hold over the whole horizon, the economy starts at its own
steady state, and in the endogenous-θ runs the political choice binds from the first period, so θ_2020 is
an outcome rather than an inherited datum. `python/US/shocks.py` and `writing/US/num_esc.tex` carry the
reasoning. Two consequences here: the wedge calibration moved one period back with the reporting, so
**every** `escCalibration{,CRRA}.csv` point had to be recomputed, not just the experiments; and the French
tables carry two extra rows (all three French characteristics at once, and France's own calibrated path,
which is not a counterfactual on the US model and whose workweek is a calibration target rather than a
prediction). Under the `flat` spec the France row fails by construction — its `(θ, p)` inversion is not
identified at France's θ = 1 corner — and the headline `scale` spec carries it.

## Traps

- **`build.py` backs up a hand-written file the first time it overwrites one**, to
  `results/paper/superseded/`. Re-runs detect their own `%% GENERATED` banner and do not re-back-up, which
  would otherwise overwrite the true original with a generated one on the second run. That directory was
  deleted in the 2026-08-24 cleanup once the numbers were accepted; the originals are at
  `bfba998:results/paper/superseded/`.
- **Aggregate hours have no scale, so the workweek is a normalisation — not a conversion.** The observed
  42.54 hours is the *reference point*: the calibrated baseline's `h` at the calibration year **is** 42.54
  hours by definition, per ρ, and every other `h` is reported as `42.54 · h/hRef`.
  `config.workweekHours(h, hRef)` requires that reference explicitly for this reason.
  **Do not use `h · 7 · 12`.** That inverts how the *pre-determined* period's hours enter as a model
  input — not a scale the solved `h_t` inherits. Using it to report made the baseline read 44.22 instead
  of 42.54 and manufactured a 43.80–44.57 spread across ρ out of a free normalisation, which then looked
  like a result worth noting in the table.
- **The savings rate needs a state, not a row.** `s_{t0-1}` is the seed entering the reform year and no
  shock csv can carry it as a datum. `datasets.seedSavings` gets it two ways — from `shockEEOnly.py`'s
  `s__base`, and by inverting eq (calibration) at `t0`, where the baseline savings rate is a target and so
  is known — and **raises if they disagree**. That guard has already caught one real defect; keep it.
- **Vectors go through the summary csv as JSON.** Under numpy 2 the repr of a list of `np.float64` is
  `np.float64(1.64…)`, and a number-scraping reader mines a spurious `64.0` out of the literal text
  `float64`. This was a live bug, not a hypothetical one.
- **The long-run figure period must clear the terminal period**, where `s_T = 0` makes the savings rate
  and `ι` degenerate rather than small. `figures.argCrraLog` refuses a `longRun` that lands on or past it.
  The default is `t0+1` (2040), chosen for legibility — at `t0+3` the four curves separated more but the
  figure read worse. **The savings-rate panel is what that costs**: at `t0+1` the short- and long-run
  series converge and cross near ρ≈0.9, with a largest gap of 0.024 p.p. on an axis spanning 0.19 p.p.
  That is a real feature of the path (the savings-rate effect is essentially at its long-run value by
  2040), not a plotting artifact — but it is why that panel no longer shows a short/long contrast.
- **`datasets.epsThetaGrid` requires a complete rectangle.** `figures.argLogFourInOne` pivots the grid into
  an `ε × θ` matrix and fills between adjacent `θ` columns; a missing pair becomes a NaN and
  `fill_between` drops that span **silently**. Since `sweepEpsThetaGrid.py` is resumable, a partially
  finished sweep is a reachable state.
- **Figure colours**: a two-hue **categorical** pair (blue then orange, worst-case CVD ΔE 24.7) in fixed
  order, never cycled, for series identity. A **continuous** parameter gets `figures.THETA_RAMP` instead —
  one hue light→dark plus a colourbar, never a rainbow and never the categorical pair. Its middle step is
  the categorical blue, so the two kinds of figure stay one family; its lightest step is the ordinal floor
  against a light surface, so the palest curve survives print. Do not substitute by eye.

### Specific to the US/France/UK arm

- **Stage (i) is ORDER-DEPENDENT here, and is not in the Argentina arm.** France and the UK impose the US
  `β` at the same ρ, read out of `US_rhoGrid.csv`, which `USReference` matches exactly and refuses to
  interpolate. So the US sweep must be complete over the whole grid before any European sweep starts;
  `runCalibrationUS.py` enforces that rather than relying on loop order, since a partial US sweep would
  otherwise fail one point at a time in the middle of a march.
- **Two columns of the US shock csv are already converted and must not be converted again.** `sr` is
  `s/(w·h)`, the paper's savings rate; and `workweek` is already in hours, normalised inside the
  experiment script against *that ρ's own* baseline. Re-deriving the workweek in stage (iii) from `hbar`
  would be wrong twice over.
- **A shock copy's `db['dates']` is stale, not absent.** `createCopyFromt0` leaves the full original
  calendar on a shorter, renumbered horizon, so nothing here reads it — `config.usCalendar()` goes back to
  the workbook instead.
- **`config.pct` escapes the percent sign for tex, so it must never go into a figure.** matplotlib renders
  the backslash literally and the legend read `14.4\%`. Anything drawn *into* a figure needs plain
  formatting.
- **The income-distribution counterfactual moves `θ`** (0.738 → 0.495), because swapping `η_i` re-derives
  it from the unchanged replacement-rate ratio. That is what reproduces the paper, so it is the default,
  but the row therefore bundles a pension-design change with the inequality change. `runShocksUS.py`'s
  `pinTheta` entry keeps the alternative reading on disk.
- **The common-`X` shock run is a check as much as an output.** θ, ageing and voting must come back
  *identical* to the vector-`X` run (measured: ≤ 4e-15 in τ and sr) while income distribution and leisure
  must differ (up to 7.9e-3 in τ), since those two are *defined* through `η` and `X`. A common-`X` run
  matching on all seven would mean the variant was not being applied.
