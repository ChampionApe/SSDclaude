# Runbook: re-running Argentina on the capital-output target

Opened 2026-08-24. The calibration target is now `db['KY0'] = 3.2313` — Argentina's capital-output ratio
in 2010, the calibration year, where the rest of `eq:calibration` is measured too (PWT 11.0, see
`python/paper/dataTargets.py`; `--target window` selects the 1980–2010 mean of 3.6606 instead, and both
readings are written to `data/argentina_calibrationTargets.csv` every run). It replaces the savings-rate
target `db['s0'] = 0.184`; `notes/argentina_savingsTargetAudit.md` is the argument.

> **EXECUTED 2026-08-24. Every step below is done; nothing here is outstanding.** Kept as the record of
> what was run and in what order, and because the verification commands are the ones to re-use the next
> time the target moves. Outcomes are in "What actually happened" at the end; the numbers themselves live
> in `python/InformalSavings/README.md` and the research logs.

**The code is migrated, the numbers are not.** *(As written, before the run.)* Everything in `results/`
was fitted to the old target, and every paper number downstream of it is stale-but-internally-consistent.
This file is the execution plan for the pass that fixes that. Total machine time ≈ **6-7 hours**, almost
all of it in steps 3 and 4, which is why it is a night job. The US/France/UK arm is untouched by all of
this and must **not** be re-run.

---

## Expected landing point

Measured at ρ=1 by `python/InformalSavings/retargetCalibration.py`
(`results/calibration/informalSavings_KYGrid.csv`):

| | old target (sr = 0.184) | new target (K/Y = 3.2313) |
|---|---|---|
| β | 1.2120 | **0.8076** |
| ω | 2.6414 | 2.3278 |
| K/Y implied | 4.005 | 3.231 |
| savings rate delivered | 0.1840 | 0.1472 |
| $R$ over 30y (annualised) | 3.221 (3.98%/yr) | 3.992 (4.72%/yr) |

β crosses 1 at K/Y ≈ 3.64, so the 2010 reading clears it with room; the thirty-year mean (3.6606) would
have left β at 1.0126. The low-ρ end is the open question — at the old target β was 4.28 at ρ=0.5 and the
CRRA re-target was never completed, so what it becomes is unknown until step 3.

## 1. Before starting

```
git status --short results/calibration results/shocks results/sweeps results/paper
.venv\Scripts\python.exe python\paper\dataTargets.py
```

The first command must show the Argentina csvs **clean** — `informalSavings_rhoGrid.csv`,
`results/shocks/*`, `results/sweeps/*` and `calibrationSummary.csv` unmodified against HEAD. That is what
makes the old sr-target numbers recoverable after step 3 overwrites them, and it is why no commit is
needed first: git already holds them. If any of those files is dirty, commit or stash it before going on,
because step 3 destroys the working copy. (The working tree carries unrelated in-progress work on the
US/ESC side; do not sweep that into a commit about this change.)

The second command must print `capitalOutputRatio = 3.2313  (year reading)` and exit without
refetching. If it refetches,
`data/argentina_calibrationTargets.csv` is missing and something upstream is wrong — stop.

Confirm the target actually reached the model:

```
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'python/InformalSavings'); import os; os.chdir('python/InformalSavings'); import test; print(test.mLOG.db['KY0'], test.mLOG.db['yearsPerPeriod'])"
```
→ `3.2313 30`

## 2. Two code changes that are inputs to the run, not consequences of it

Both are deliberately still undone, because on the *old* csvs they break the build. Make them now, before
step 3, so the rebuild in step 6 lands on the first try.

**2a. `python/paper/runCalibration.py`, in `summarise()`** — add `'KY'` to the tuple of columns copied
out of the sweep csv:
```python
for k in ('β', 'ω', 'KY', 'sr', 'τ', 'ι', 'residual', 'verifyResidual', 'commit', 'timestamp'):
```
and add `'KY'` to the print list at the bottom of `main()` beside `'sr'`.

**2b. `python/paper/tables.py`, `argentinaCalibration()`, the β row** — the target column currently reads
`Private savings rate of X%`, which is wrong on the concept, wrong on the sector and wrong on the
denominator. Replace with the capital-output ratio:
```python
[r'$\beta$', '$' + C.num(c['β']) + '$', 'Capital--output ratio of $' + C.num(c['KY'], 2) + '$'],
```
Nothing else in `tables.py` needs touching: the savings rate stays in `ArgentinaUniversal` and
`Argentina_funcOfRho` as a *reported* quantity, which it still is.

**No change needed** in `python/paper/datasets.py`. `seedSavings` inverts eq (calibration) at `t0` for
`s_{t0-1}`, but it reads the *achieved* `sr` off the sweep csv rather than assuming the target — its
docstring says so. It and its cross-check against `shockEEOnly.py`'s `s__base` survive untouched.

## 3. Stage (i): recalibrate the ρ grid — ~2 h

```
.venv\Scripts\python.exe python\paper\runCalibration.py --force
```

`--force` is **required**, not optional: `calibrateRhoGrid.py` resumes from its own csv and would
otherwise hand back all 16 old rows without solving anything. Writes
`results/calibration/informalSavings_rhoGrid.csv`, 16 pickles under `instances/`, and
`results/paper/calibrationSummary.csv`.

Timing, measured on the 2026-08-24 run: the LOG anchor takes 26 s and each CRRA point 430-530 s, so the
grid is ~2 h rather than the ~75 min the README quotes. The README's figure predates `--verify`, which
re-solves every point on a 60x60 grid on top of the calibration itself.

Verify before going on:

```
.venv\Scripts\python.exe -c "import pandas as pd; d=pd.read_csv('results/calibration/informalSavings_rhoGrid.csv'); print(d[['ρ','β','ω','KY','sr','τ','ι','residual','verifyResidual','occupancyι','occupancys']].to_string(index=False))"
```

- every `KY` = 3.2313 to ~1e-5, every `τ` = 0.125 to ~1e-5 — these are the targets and a miss is a failure
- `residual` < 1e-6 everywhere; `verifyResidual` ≲ 1e-4 (README, "a point that is converged but not
  resolved"). A point an order of magnitude above the rest is the one to look at, not the whole column.
- β monotone decreasing in ρ, ω likewise; ι ∈ (0,1)
- 16 rows, and `commit`/`timestamp` all from tonight — a stale row means `--force` did not take.

## 4. Stage (ii): re-run the experiments — ~3 h

```
.venv\Scripts\python.exe python\paper\runShocks.py --list      # everything should read "exists" (stale)
.venv\Scripts\python.exe python\paper\runShocks.py --force
```

Again `--force`: `shockUniversal.py`, `shockEEOnly.py` and `sweepEpsThetaGrid.py` are each resumable on
their own csv and will silently return the old rows without it. Cost: `universal` ~2.5 h (a full backward
PEE recursion per ρ), `flat` ~10 min, `eeOnly` ~minutes, `epsThetaGrid` ~5 min.

Verify:
- `runShocks.py --list` reports every output present
- the status-quo row of `results/sweeps/epsThetaGrid_rho1.0000.csv` reproduces the calibration: `τ` to
  ~1e-10 and the savings rate to the sweep csv's own `sr`. That row is the sweep's self-check.
- `shockEEOnly.py --control` runs as part of the entry; it is what caught the `EE_report` proxy defect
  and it doubles as the CRRA warm start. Do not skip it.

## 5. Tests — ~1 h

```
.venv\Scripts\python.exe python\runTests.py --all
```

All 26 suites must pass. Already verified against the migrated code at K/Y = 3.5752 — the fast 22, plus
`InformalSavings/test_calibration.py` (38 checks) and `informalAnalytical/test_calibration.py` (22) —
but they run their own cold calibrations, so re-run them at 3.2313. `InformalSavings/test_calibrationGrid.py`
(~45 min) has **not** been run since the migration; it is the one with real risk of surfacing something,
and it is independent of steps 3–4.

If `test_calibration.py` fails on `beta is not capped at 1`, read the message: the check now asserts only
that no `_calBounds` entry has a finite upper bound, and reports β. β's *value* is no longer an assertion.

## 6. Stage (iii): rebuild the paper — seconds

```
.venv\Scripts\python.exe python\paper\build.py --list
.venv\Scripts\python.exe python\paper\build.py
```

Rebuilds `ArgentinaCalibration`, `ArgentinaUniversal`, `Argentina_funcOfRho`, `ARG_LOG_FourInOne`,
`ARG_CRRA_LOG` (and the untouched US outputs, which must come back byte-identical apart from the
build timestamp — if a US table moves, something in stage (i) leaked across arms).

Check in the output:
- `Tables/ArgentinaCalibration.tex`: β ≈ 0.81 against target text "Capital–output ratio of 3.23"
- `Tables/ArgentinaUniversal.tex` and `Argentina_funcOfRho.tex`: the pre-reform savings-rate row is now
  ≈ 14.7%, not 18.40%. That is the most visible single consequence of the whole change.

## 7. Hand-written numbers in the paper that the rebuild does NOT touch

These are prose in `writing/Paper/Sections/Quant.tex` and must be re-read against the new tables. All of
them are Argentina; none of the US paragraphs are affected.

- line 57: "increases tax rates by about 3.1 p.p.", "a drop of less than one p.p. in the savings rate",
  "average weekly labor supply drops by about 0.4 hours", "their savings rate drops 23\%"
- line 94 and the surrounding ε/θ discussion: the *signs* and monotonicity should survive (they are
  properties of the model, not of β), but any magnitude quoted there needs checking
- line 73's table note "The savings rate is defined as savings relative to GDP" is still true and stays

Also re-read `writing/informalSavings/num_calibration.tex`, the *Residual* paragraph: it quotes
η0 = 0.326 and X0 = 0.408 "at the calibrated point". Both move (0.3258/0.4113 at 3.5752, and again at 3.2313).

## 8. Documentation, after the numbers land

- `python/paper/README.md` — `dataTargets.py` is a fourth entry point and appears in neither the stage
  table nor the Files list. It is stage (0): it writes to `data/`, not `results/`, and it is the only
  part of the pipeline that needs the network.
- `python/InformalSavings/README.md` — "Results: the ρ sweep", "Results: the universalisation shock" and
  "Results: the reform decomposed" all quote numbers from the old calibration, and the β > 1 discussion
  is superseded. Update the file map too: `retargetCalibration.py` is new.
- `RESEARCH_LOG.md` (root, cross-cutting: the target change spans two model modules and the paper) and
  `python/InformalSavings/RESEARCH_LOG.md` (the sweep's new numbers).
- `notes/argentina_betaCalibration.md` and `notes/argentina_savingsTargetAudit.md` are the *record* of
  how this was decided. Leave their tables alone — they document a state the code is no longer in, and
  say so.
- `data/ArgentinaTest.xlsx` still carries `Savings rate = 0.184`, read into `db['s0']` and reported but
  not targeted. Either add a `Readme` sheet saying so (the US/FR/UK workbooks have one, this one does
  not) or drop the column once nothing reads it.

## 9. If β lands above 1 across a wide stretch of the ρ grid

That is a result, not a bug, and it is the question this whole exercise was opened on. β here is a
**30-year** discount factor and the old-age weight in the model is β·p with p < 1, so β slightly above 1
is admissible in an OLG model in a way it is not in an infinite-horizon one. What no annualisation
argument rescues is a large β at the low-ρ end (4.28 at ρ=0.5 under the old target). If that survives,
the options are in `notes/argentina_betaCalibration.md` §"Possible fixes" — and the honest reading is
that the target was never the whole story at low ρ.

Do not respond to it by moving the window to make β behave. The window is a data choice and has to be
defensible on its own; `results/calibration/informalSavings_KYGrid.csv` is there to make the
β(K/Y) trade-off explicit rather than to be shopped.

## 10. One-line summary of the run

```
git commit                                                     # save the old numbers
edit runCalibration.summarise + tables.argentinaCalibration     # step 2
.venv\Scripts\python.exe python\paper\runCalibration.py --force   # ~2 h
.venv\Scripts\python.exe python\paper\runShocks.py --force        # ~3 h
.venv\Scripts\python.exe python\runTests.py --all                 # ~1 h
.venv\Scripts\python.exe python\paper\build.py                    # seconds
```


---

## What actually happened (2026-08-24)

Ran in the order above, in ≈3 h of machine time rather than the 6-7 estimated — stage (ii) came in at ~40
min against ~3 h, because a shock point is one PEE solve where a calibration point is a 25-evaluation
root search.

| Step | Outcome |
|---|---|
| 1 | Argentina results confirmed clean against HEAD; no commit needed, and the tree's unrelated US/ESC work stayed out of one |
| 2 | `summarise()` + `tables.argentinaCalibration` edited before the run, as prescribed |
| 3 | **16/16, no step-halving, ~2 h.** `KY` = 3.2313 to 1.6e-10, `τ` = 0.125 to 3.6e-10 everywhere |
| 4 | All four experiments, 16 ρ each; status-quo row reproduces the calibration to 0.0e+00 |
| 5 | 26/26, after two fixes — see below |
| 6 | Built; Argentina outputs all moved, US outputs moved only in the workweek column (this tree's own ageing change, not Argentina) |
| 7 | `Quant.tex`'s Argentina paragraph rewritten |
| 8 | Both READMEs, all three research logs, `crossCuttingFindings.md` #12 |

**The three results.** β = 0.8076 at ρ=1 (was 1.2120) and **crosses 1 between ρ=0.8 and 0.9** rather than
at ρ≈1.15 — the curve is ≈0.65× its old self at every ρ, so the retarget shrank the β>1 region without
closing it, and §9's warning stands for ρ<0.85. The **ρ≈0.7 pocket is gone** (12 evaluations, 4.5e-14,
where it used to need four strategies and fail). **`verifyResidual` degrades down the low-ρ tail** —
1.2e-3 at ρ=0.5, 4.9e-4 at ρ=0.6 — so those two rows are converged but not resolved; refining that tail
is the one thing this pass leaves open.

**The two test failures, both stale references rather than defects.** `test_calibrationGrid` pins the
anchor's (β,ω) against the README and was updated, as its own comment prescribes.
`informalAnalytical/test_calibration.py` failed to converge *from its shipped starting guess* of β=0.6 —
tuned for the old target — walking into a region where the whole-path policy solve returns a NaN τ and
the steady-state `brentq` then dies at its own lower bracket. Every start in [0.7, 1.0] reaches the same
root (β=0.84424, ω=2.19679), so the guess moved to 0.85. That variant's outer search has no
globalization; `InformalSavings` took the same change from the same guess without complaint.

**One claim in the paper changed, not just its numbers.** The reform now accounts for +0.82 p.p. of GDP
of the observed 1.9% rise in pension spending — a little over two fifths, where the text said "almost the
entirety". Rewritten in `Quant.tex`, and flagged as the author's to settle. Note that sentence was
already inconsistent with the *old* generated table (+0.90 p.p. → 0.51% of GDP): its "3.1 p.p." matches
neither calibration and predates both. A check that did land: τ × (1−α) = 7.12% of GDP against the 7.1%
ANSES datum the τ target was built from.

**Still open, and both are decisions rather than tasks.** β > 1 for ρ < 0.85 (options in
`notes/argentina_betaCalibration.md`); and whether the US tables that `build.py` wrote into
`writing/Paper` from this tree's in-progress ESC work should stay — `git checkout` on
`writing/Paper/Tables/US_*.tex` and `results/paper/Tables/US_*.tex` reverts them, and `build.py --only`
the Argentina targets avoids repeating it.
