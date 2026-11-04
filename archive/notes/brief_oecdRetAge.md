# Brief: retirement-age corrections and Luxembourg in the own-turnout cross-section (2026-11-02)

**RKB, 2026-11-02.** The main version is θ variant C, each country's own turnout (CSES), layer 1 at the average ω
(`--omegaRule mean`, the mean of the layer-2 ω's). Two things are tested now: a retirement-age correction of the
population ratio ν, starting with the effective exit age, and Luxembourg at a flat turnout profile against
Luxembourg left out. Exploration only: no change to `python/paper/config.py`, `writing/` or `results/oecd26/`. Hold
the full tests. The paper text and the heavy robustness runs come on Tuesday night.

## 1. Data
The OECD average effective age of labour-market exit, **men**, for the 29 countries of `data/oecd29.csv`, in the
latest year around 2020.
- **Source:** OECD Pensions at a Glance 2021 (or the OECD's "average effective age of retirement" series behind it).
  Record the exact table/series and the year.
- **Output:** `data/oecd29_exitAge.csv` (iso3, exitAge_men, year, source), plus a row in `data/README.md` in the
  style of the others.

## 2. Code (`python/US/oecd26.py`, `python/US/runOECD26.py`)
- **`--retAge none|exit|nra`**, default `none`, so every row on disk keeps its inputsKey.
  - ν is replaced by ν(30 − g)/(30 + ν g), France's formula of appendix F (`data/README.md`, `FRMain.xlsx`).
  - g = A_US − A_c in years. Under `exit`, A is the effective exit age, the same at every date. Under `nra`, A is
    `nra_current_men` for 1990 and 2020 and `nra_future_men` for 2050 and 2080.
  - The U.S. gap is 0, so the anchor is unchanged.
  - Add a key column `retAge`, with legacy value `none` for the rows already on disk.
  - Check: under `nra`, France's 2020 ν is 1.039, appendix F's 1.04.
- **Turnout `'csesFlat'`:** each country's own CSES profile; a country in `oecd26.COMPULSORY` without CSES
  (Luxembourg) gets a flat profile. The anchor is the cses anchor (the U.S. at its own CSES profile).

## 3. Runs
- **Settings:** θ C, spec sizePiR, betaRule common, `--inSample`. Outdir `results/oecd26_retage/`, with
  `--usSweep results/calibration/US_rhoGridCommonX.csv` as in `logs/oecdVariants/run.sh`.
- **Reuse:** don't recompute rows on disk. The cses anchor and layer 2 are in `results/oecd26/`. Luxembourg's flat
  rows at today's ν are in `results/oecd26_stylized/` (turnout pooled, the same inputs and anchor).
- **The runs**, all with layer 1 at `--omegaRule mean`:
  - **R5:** `retAge none`, turnout `csesFlat`. Layer 2 needs only Luxembourg's row; layer 1 runs at the new ω̄, which
    includes Luxembourg.
  - **R6:** `retAge exit`, turnouts `cses` and `csesFlat`. Layer 2 for 21 countries, then layer 1 at each ω̄.
- **How to run:** detached, script and log in `logs/oecdRetAge/`, with expected times (about 20 min per layer 1 and
  25 min per layer 2).

## 4. Comparison
`logs/variantCompare/summary_retAge.md` compares four combinations: {retAge none, exit} × {Luxembourg out, flat}, at
ω̄. For each give:
- n and ω̄;
- the slopes of layers 1 and 2 against the data (spending on growth, spending on the index at the chosen design,
  index on growth, index on Gini);
- the correlation of predicted with observed θ, U.S. left out;
- the mean θ and spending, model against data.

The regressors are figure 1.1's (population 2020/1990), in data and model alike. The data side changes only with the
sample.

## 5. Checks and report
- **Checks:**
  - the defaults reproduce today's inputsKeys;
  - the anchor is unchanged;
  - France's ν under `nra` is 1.039;
  - every row is ok with nEqMax 1;
  - `python/US/test_oecd26.py` passes.
- **Logs:** an entry in `python/US/RESEARCH_LOG.md` (at most 6 lines). No commit.
- **Report, briefly:**
  - the exit ages and gaps (table);
  - the code changes;
  - the comparison table with 3–4 sentences reading it;
  - the run times;
  - anything odd.
