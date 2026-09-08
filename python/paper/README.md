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
| (i) calibration | `runCalibration.py` | `runCalibrationUS.py` | `results/calibration/`, `results/paper/*Summary.csv` | ~3.2 h / ~20 min |
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/` | ~50 min / ~30 s |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |

Every stage **skips work whose output already exists**, so running them in order is safe: it costs seconds
when nothing has changed and only pays for what is genuinely missing. `--force` overrides, `--list`
reports without doing anything, `--dry` prints the commands stage (i)/(ii) would delegate.

**Skipping answers "nothing changed"; `--force` answers "the inputs moved". Only the second is a
judgement.** Three of the delegated scripts resume from their own csv — the calibration sweeps and
`sweepEpsThetaGrid.py` — and they key on the parameter point, never on what produced it. A resumed run
therefore returns rows solved under an earlier calibration, or earlier grid settings, without a word, and
nothing downstream can tell from the row that it did. **So `--force` whenever anything upstream moved: a
recalibration above all**, since the sweeps load a pickled instance and no column records which one. It is
forwarded to the child only where the child resumes; elsewhere it just defeats this file's own skip.
Failing to do this after the K/Y retarget is what put 378 stale rows in the `(ε, θ)` grid and a
discontinuity in `ARG_LOG_FourInOne` (2026-08-25 log entry); `datasets.epsThetaGrid` now refuses that csv
rather than plotting it.

**The US arm carries TWO calibration variants, and `config.US['commonX']` says which one leads.** Common
`X` is the headline: the taste for leisure is one number across income groups, its level pinned by
targeting the observed workweek, and relative hours become a prediction. Vector `X_i` is the robustness
twin. Every US builder takes `commonX` and defaults to the headline, so one builder produces both — the
headline keeps the plain name, filename and tex `\label` the draft already cites, and the twin's carry
their own variant (`config.variantSuffix`). `build.OUTPUTS` registers the pair through `_variants`.
Flipping the config flag therefore swaps what is in the paper's tables without renaming one of them.
The two share `β`, `ω`, `τ`, `R`, the savings rate and aggregate `h` exactly; what differs is anything
defined *through* `η` or `X` — the French income-distribution and leisure rows, and nothing else. The
ESC leg runs under the headline variant only: it is the most expensive stage in the pipeline and a
second variant would double a multi-hour run for an appendix nobody reads twice.

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

## Outputs wired (34)

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
| `Figs/US_overview.pdf` | `US_shocksCommonX.csv`, all ρ — τ, savings and hours in one three-panel figure |
| `Tables/US_ESC_Calibration.tex` | `results/esc/escCalibration{,CRRA}.csv` |
| `Tables/US_ESC_{Ageing,IncomeDistr,Leisure,Voting,FrenchAll}.tex` | `results/esc/escExperiments.csv`, ρ ∈ {0.5, 1, 2} |
| `Figs/US_ESC_overview.pdf` | `escExperiments.csv` — dumbbells: open marker = `θ` pinned, filled = chosen, per (scenario, ρ) |

Every US table and figure above is registered **twice**, once per calibration variant: the plain name is
the headline and `<name>_vectorX` the appendix twin. The ESC outputs are the exception (headline only).

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

- **A pinned `θ` does not survive a composite shock on its own.** `θ` is in `paramsFromFuncs`, so every
  `updateAuxPars` re-derives it and the LAST one wins: in `frAll` and `frBoth` the income shock's pin is
  followed by `shockVoting`'s refresh, which recomputes `θ` from *France's* `η`. Both composites
  re-install it explicitly, and `test_esc.py` pins that they do. The single-characteristic rows never see
  this, which is exactly why the defect read as a plausible 0.55 rather than as a failure
  (`crossCuttingFindings.md` #9).
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
- **The pre-reform savings rate is per rho, not a shared row — in both arms.** Neither arm targets it any
  more (Argentina identifies β by K/Y, the US by R), so it is a prediction that moves with ρ, and a table
  that differences against the ρ = 1 level misstates the effect at every other ρ, sign included.
  The three `US_CRRA_*` tables print a baseline row per ρ and difference against it; `Argentina_funcOfRho`
  prints ONE shared pre-reform row (τ and the workweek, which are common by construction; the savings
  cell is `--`) and still differences every post-reform row against its own ρ's baseline path
  (2026-09-08). The builder raises if the pre-reform τ is not common across ρ.
- **The Argentina ρ march must be seeded at its anchor.** `config.ARG['anchorGuess']` is forwarded as
  `calibrateRhoGrid.py --x0`; without it the anchor starts from the workbook defaults, at which the `ι`
  state grid is degenerate under α = 0.35. Retune it if the capital share or the K/Y target moves.
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
- **`datasets.epsThetaGrid` checks the grid is finished AND that it is about the current calibration** —
  two different failures, because `sweepEpsThetaGrid.py` is resumable. *Finished*: a complete `ε × θ`
  rectangle, since `figures.argLogFourInOne` pivots it into a matrix and `fill_between` drops a NaN span
  **silently**. *Current*: **exactly one `statusQuo` row, matching `calibrationSummary`**. A resumed sweep
  across a recalibration ADDS the new calibrated column and keeps the old rows, which is still a perfect
  rectangle — so the shape check cannot see it, and the tell is the second `statusQuo` row. The
  calibration match is the check that matters: a *wholly* stale csv has exactly one such row. This was
  live — 378 of 392 rows survived the K/Y retarget and put a 3.7 p.p. notch in the published figure.
  `crossCuttingFindings.md` #13.
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
- **One savings-rate unit, `s/Y`, in every table and figure of both arms (2026-09-08).** The US shock csv
  carries both `sr` = `s/(w·h)` and `srOverY` = `s/Y`; stage (iii) reads `datasets.US_SR` (= `srOverY`)
  and never `sr`. The ESC csvs carry only `s/(w·h)`, and `datasets.escSavingsOverY` converts by the exact
  factor `(1-α)` with `α` read from `usCalibrationSummary.csv` and cross-checked against the workbook —
  never a bare 0.30. Every counterfactual table prints the savings rate as the **change against that ρ's
  own baseline** (`config.pp`), the baseline row as a level, and the note says so (`tables.SRNOTE`); the
  leisure row must read `0.00 p.p.` at every ρ, which is the check that the differencing is against the
  right baseline. The ESC tables difference against the *endogenous* baseline, so their exogenous leisure
  rows carry the 0.01–0.02 p.p. gap between the two baselines rather than an effect.
- **`workweek` in the US shock csv is already in hours**, normalised inside the experiment script
  against *that ρ's own* baseline. Re-deriving it in stage (iii) from `hbar` would be wrong twice over.
- **A shock copy's `db['dates']` is stale, not absent.** `createCopyFromt0` leaves the full original
  calendar on a shorter, renumbered horizon, so nothing here reads it — `config.usCalendar()` goes back to
  the workbook instead.
- **`config.pct` escapes the percent sign for tex, so it must never go into a figure.** matplotlib renders
  the backslash literally and the legend read `14.4\%`. Anything drawn *into* a figure needs plain
  formatting.
- **The income-distribution counterfactual HOLDS `θ` at the US design.** Swapping `η_i` would otherwise
  re-derive it from the unchanged replacement-rate ratio and take it to 0.495, bundling a pension-design
  change into a counterfactual about inequality — and pension design is the separate `theta` family in
  the same table set. Pinning is therefore the default; `runShocksUS.py`'s `freeTheta` entry keeps the
  re-deriving reading on disk (τ 13.79% against the reported 13.21% at ρ = 1, common X).
- **The two variants check each other.** Run the same shock set under both and compare row by row:
  baseline, θ, ageing and voting must come back *identical* (measured ≤ 5e-15 in τ and sr — this is the
  block-recursivity claim end to end), while income distribution and all-three must **differ** (4.9e-3
  and 5.1e-3 in τ), since those are defined through `η`. A run matching everywhere would mean the variant
  was not being applied.
  **Leisure is the one that must differ in the WORKWEEK and not in τ**: it is a pure scale, so τ and the
  savings rate are pinned at baseline in *both* variants (they agree to 2.3e-5, the solver's own
  tolerance) and the whole variant effect lands on hours — 34.74 against 33.24, because `Xbar_FR/Xbar_US`
  is 1.520 under vector `X` and 1.761 under common `X`. Checking that row in τ would report a pass on a
  quantity that cannot move.
