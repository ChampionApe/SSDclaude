# paper

The pipeline that turns solved models into the tables and figures in `writing/Paper`. It is not a model:
it owns no economics, and every number it emits is read off `results/`.

## Three stages, run in order

There are **two model arms** — Argentina (`python/InformalSavings/`) and the rich OECD economies
(`python/US/`) — with separate stage (i)/(ii) entry points, because they delegate to different experiment
scripts. They share `config.py`, `results/`, and one stage (iii).

| Stage | Argentina | US / France / UK | Writes | Cost (cold, ARG / US) |
|---|---|---|---|---|
| (i) calibration | `runCalibration.py` | `runCalibrationUS.py` | `results/calibration/`, `results/paper/*Summary.csv` | ~75 min / ~20 min |
| (ii) experiments | `runShocks.py` | `runShocksUS.py` | `results/shocks/`, `results/sweeps/` | ~2.5 h / ~30 s |
| (iii) build | `build.py` | `build.py` | `results/paper/{Tables,Figs}`, then `writing/Paper` | seconds |

```
.venv\Scripts\python.exe python\paper\runCalibration.py      .venv\Scripts\python.exe python\paper\runCalibrationUS.py
.venv\Scripts\python.exe python\paper\runShocks.py           .venv\Scripts\python.exe python\paper\runShocksUS.py
.venv\Scripts\python.exe python\paper\build.py
```

Every stage **skips work whose output already exists**, so the sequence above is safe to re-run: it costs
seconds when nothing has changed and only pays for what is genuinely missing. `--force` overrides,
`--list` reports without doing anything, `--dry` prints the commands stage (i)/(ii) would delegate.

## The separation that makes this worth having

**Stage (iii) imports no model code and unpickles nothing.** It reads csv, writes tex and pdf. That is
what makes it re-runnable after every edit to a caption or a rounding rule, and it is why the expensive
stages are separate entry points rather than a `--refresh` flag: a full paper rebuild can never silently
turn into a 2.5-hour solve.

The corollary is that **an output whose inputs are missing is reported and skipped, never partially
written**. An experiment that has not been run must not be able to look like a table that has.

Stages (i) and (ii) are *declarations*, not implementations. The experiment scripts under
`python/InformalSavings/` and `python/US/` keep their own CLIs and do the work; these four files record
the settings the published numbers were produced at, so reproducing them is a run rather than an
archaeology. `config.py` is where a paper number's specification actually starts.

## Files
- `config.py` — paths, the `ARG` and `US` specifications (ρ grids, reform rule, grid settings), both
  calendars, and the unit conversions. Imports nothing from the model. Change a paper number here first.
- `datasets.py` — the only module that knows the `results/` file layout and column names, for both arms.
  Raises `MissingInput`, which `build.py` turns into a skipped output.
- `tables.py` / `figures.py` — the Argentina builders. One function per paper output.
- `tablesUS.py` / `figuresUS.py` — the US/France/UK builders. `figuresUS` imports the house style from
  `figures` rather than restating it, so the two arms stay one visual family.
- `build.py` — stage (iii): the output registry for both arms, and the copy into `writing/Paper`.

## Outputs currently wired

| Paper file | Built from |
|---|---|
| `Tables/ArgentinaCalibration.tex` | `results/paper/calibrationSummary.csv` |
| `Tables/ArgentinaUniversal.tex` | `eeOnly_match_rho1.0000.csv` + `universal_match_rho1.0000.csv` |
| `Tables/Argentina_funcOfRho.tex` | `universal_match_rho*.csv` |
| `Figs/ARG_LOG_FourInOne.pdf` | `results/sweeps/epsThetaGrid_rho1.0000.csv` |
| `Figs/ARG_CRRA_LOG.pdf` | `universal_match_rho*.csv` |
| **US / France / UK** | |
| `Tables/USUKFRCalibration.tex` | `results/paper/usCalibrationSummary.csv` |
| `Tables/{US,FR,UK}_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` |
| `Tables/US_PensChars.tex` | `US_shocks.csv`, ρ = 1 |
| `Tables/US_Ageing.tex` | `US_shocks.csv`, ρ = 1 |
| `Tables/US_OtherShocks.tex` | `US_shocks.csv`, ρ = 1 |
| `Tables/US_CRRA_{PensChars,Ageing,OtherShocks}.tex` | `US_shocks.csv`, ρ ∈ {0.5, 1, 2} |
| `Figs/US_taxOverview.pdf` | `US_shocks.csv`, all ρ |
| `Figs/USX_taxOverview.pdf` | `US_shocksCommonX.csv`, all ρ |

Not wired: everything under `writing/Paper/Appendix/EndogenousSystemCharacteristics.tex`, which needs
endogenous `θ`.

**The common-`X` shock run is a check as much as an output.** θ, ageing and voting must come back
*identical* to the vector-`X` run — none of them touches `η` or `X`, and `β`/`ω`/`h` agree across variants
— while income distribution and leisure must differ, since those two are *defined* through `η` and `X`,
whose meaning is exactly what the variant changes. Measured: the first group agrees to ≤ 4e-15 in τ and
sr, the second differs by up to 7.9e-3 in τ and 1.48 hours in the workweek. A common-`X` run that matched
on all seven would mean the variant was not being applied.

## Traps
- **`writing/Paper` is not tracked by git.** The first time a generated file would overwrite a
  hand-written one, `build.py` copies the original to `results/paper/superseded/` and says so. That
  backup is the only recovery path, so do not delete that directory until the paper's numbers have been
  read and accepted. Re-runs detect their own banner and do not re-back-up (which would otherwise
  overwrite the true original with a generated one on the second run).
- **Aggregate hours have no scale, so the workweek is a normalisation — not a conversion.** `h`'s level
  is not pinned by anything in the model. The observed 42.54 hours is the *reference point*: the
  calibrated baseline's `h` at the calibration year **is** 42.54 hours by definition, per ρ, and every
  other `h` is reported as `42.54 · h/hRef`. `config.workweekHours(h, hRef)` requires that reference
  explicitly for this reason; `datasets.baselineHours(ρ)` supplies it. A shock is then read as the change
  in hours the normalisation implies.
  **Do not use `h · 7 · 12`.** That inverts `test.py`'s `h0 = workweek/(7·12)`, which is how the
  *pre-determined* period's hours enter as a model input — not a scale the solved `h_t` inherits. Using
  it to report made the baseline read 44.22 instead of 42.54 and manufactured a 43.80–44.57 spread across
  ρ out of a free normalisation, which then looked like a result worth noting in the table. It was not.
  Anchoring each ρ to its own baseline is also what makes `Argentina_funcOfRho`'s single pre-reform row
  correct rather than merely convenient.
- **The savings rate needs a state, not a row.** `s_{t0-1}` is the seed entering the reform year and no
  shock csv can carry it as a datum. `datasets.seedSavings` gets it two ways — from `shockEEOnly.py`'s
  `s__base`, and by inverting eq (calibration) at `t0`, where the baseline savings rate is a target and
  so is known — and **raises if they disagree**. That guard has already caught one real defect; keep it.
- **Vectors go through the summary csv as JSON.** Under numpy 2 the repr of a list of `np.float64` is
  `np.float64(1.64…)`, and a number-scraping reader mines a spurious `64.0` out of the literal text
  `float64`. This was a live bug, not a hypothetical one.
- **The long-run figure period must clear the terminal period**, where `s_T = 0` makes the savings rate
  and `ι` degenerate rather than small. `figures.argCrraLog` refuses a `longRun` that lands on or past
  it; the period before it already carries the terminal boundary's influence. The default is `t0+1`
  (year 2040), chosen for legibility — at `t0+3` the four curves separated more, but the figure read
  worse. **The savings-rate panel is the one this costs**: at `t0+1` the short- and long-run series
  converge and cross near `ρ≈0.9`, with a largest gap of 0.024 p.p. on an axis spanning 0.19 p.p. That
  is a real feature of the path (the savings-rate effect is essentially at its long-run value by 2040),
  not a plotting artifact — but it is why that panel no longer shows a short/long contrast.
- **`datasets.epsThetaGrid` requires a complete rectangle.** `figures.argLogFourInOne` pivots the grid
  into an `ε × θ` matrix and fills between adjacent `θ` columns; a missing pair becomes a NaN and
  `fill_between` drops that span **silently**. Since `sweepEpsThetaGrid.py` is resumable, a partially
  finished sweep is a reachable state, and without the check it would render as a figure with holes
  rather than as a skipped output.
- Figure colours: two-hue **categorical** pair (blue then orange, worst-case CVD ΔE 24.7) in fixed order,
  never cycled, for series identity. A **continuous** parameter gets `figures.THETA_RAMP` instead — one
  hue light→dark plus a colourbar, never a rainbow and never the categorical pair. Its middle step is the
  categorical blue, so the two kinds of figure stay one family; its lightest step is the ordinal floor
  against a light surface, so the palest curve survives print. Do not substitute by eye.

## Traps specific to the US/France/UK arm
- **Stage (i) is ORDER-DEPENDENT here, and it is not in the Argentina arm.** France and the UK impose the
  US `β` at the same `ρ`, read out of `US_rhoGrid.csv`, which `USReference` matches exactly and refuses
  to interpolate. So the US sweep must be complete over the whole grid before any European sweep starts.
  `runCalibrationUS.py` enforces that rather than relying on loop order — a partial US sweep would
  otherwise fail one point at a time in the middle of a march.
- **Two columns of the US shock csv are already converted and must not be converted again.** `sr` is
  `s/(w·h)`, the paper's savings rate, which is `Base.savingsRate`'s `s/Y` divided by `(1-α)`; and
  `workweek` is already in hours, normalised inside the experiment script against *that ρ's own*
  baseline. Re-deriving the workweek in stage (iii) from `hbar` would be wrong twice over — `hbar` has no
  identified level under vector `X`, and each ρ needs its own reference. Same trap as the Argentina arm's
  `workweekHours`, one layer earlier.
- **`config.pct` escapes the percent sign for tex, so it must never go into a figure.** matplotlib
  renders the backslash literally and the legend read `14.4\%`. Caught in `US_taxOverview`; anything
  drawn *into* a figure needs plain formatting.
- **A shock copy's `db['dates']` is stale, not absent.** `createCopyFromt0` leaves the full original
  calendar on a shorter, renumbered horizon (`python/US/test_createCopyFromt0.py`), so nothing here reads
  it — `config.usCalendar()` goes back to the workbook instead.
- **The income-distribution counterfactual moves `θ`.** Swapping `η_i` re-derives `θ` from the unchanged
  replacement-rate ratio, 0.738 → 0.495. That is what reproduces the paper, so it is the default, but the
  row therefore bundles a pension-design change with the inequality change. `runShocksUS.py`'s `pinTheta`
  entry keeps the alternative reading (τ = 12.83% against 13.28%) on disk rather than in memory.
