# SSDclaude

Code repository for *Social Security Design and Its Political Support* (2026). See `CLAUDE.md` for project
conventions; this file is a map.

## Layout

**`data/`**: raw and processed inputs (not results). `ArgentinaTest.xlsx`, `USMain_test.xlsx`,
`FRMain.xlsx`, `UKMain.xlsx` (the last also regrouped at US percentiles), plus `argentina_*.csv`, the
calibration targets `python/paper/dataTargets.py` derives from the Penn World Table.

**`python/`**: three model variants, a shared numerical package, and the paper pipeline. Each subfolder
has a `README.md` (purpose, files, how to run, invariants, status, open items) and a terse `RESEARCH_LOG.md`.

| | |
|---|---|
| `informalAnalytical/` | the analytical (log-preference) informal-sector model and **ancestor** of the other two; shared conventions documented there |
| `InformalSavings/` | the variant where the informal type saves. Calibrated to Argentina, targeting its capital-output ratio |
| `US/` | `informalAnalytical` without the informal type, for the US, France and the UK. Also the endogenous-`θ` work |
| `gridsearch/` | bounded-root reparameterisation, 1-D root selection, Cartesian grids, gridded interpolation, an anchored parameter march, and `testing.py`, the shared PASS/FAIL harness |
| `paper/` | the three-stage pipeline that builds `writing/Paper`'s tables and figures from `results/` |
| `runTests.py` | the repo-wide runner: 22 fast suites (~160 s), `--all` adds the four slow ones (~1 h), `--list`, `-k <pattern>` |

**`results/`**: solved output. `calibration/` holds the parameter sweeps and one pickled instance per point,
each sweep with its own pickle directory (`instances/` for Argentina, `instancesUS*`, `instances{FR,UK,UKUS}*`);
`shocks/` the counterfactual paths; `sweeps/` the `(ε, θ)` comparative statics; `esc/` the endogenous-`θ`
runs; `paper/` the built tables and figures. Superseded runs go in a subdirectory, never beside the live
ones (`notes/crossCuttingFindings.md` #8).

**`notes/`**: the live working notes.

| | |
|---|---|
| `crossCuttingFindings.md` | thirteen findings cited by number from code and READMEs. Read #3–#5 before diagnosing a stalled outer solver, #7 before keying a fix to one solver, #9 before writing a parameter the model derives, #13 before resuming any sweep |
| `TODO.md` | the one open list. Closed work is in the logs, not here |
| `informalSavings_numericalDeviations.md` | where `InformalSavings` departs from the `num_*.tex` specs, with the measurement behind each |
| `informalSavings_resolvedIssues.md` | two resolved calibration defects and the live settings they justify |
| `argentina_calibrationTarget.md`, `argentina_alphaSensitivity.md` | why the calibration targets K/Y, and what α does to β |
| `esc_experiments_acrossRho.md`, `us_commonX_vs_vectorX.md` | result write-ups behind two paper decisions |
| `paper_styleGuide.md` | voice, units and LaTeX conventions of the paper draft |

**`archive/`**: history, frozen 2026-09-11 and indexed in `archive/INDEX.md`: the session logs to that
date, the long-form findings with their measurements, the pre-cut READMEs, closed to-do files and
demoted result notes. `.rgignore` keeps it out of default searches; read it by path when a live file
points there.

**`writing/`**: `main.tex` plus one subfolder per model variant with `model*.tex` (model and equilibrium)
and `num*.tex` (numerical solution), written as self-contained technical notes; `US/model_esc.tex`/
`num_esc.tex` cover the endogenous `θ`. Tex labels are cited from docstrings, so follow any rename
through the `.py` files. **`writing/Paper/`** is the current draft, compiled locally by the user; a
generated `.tex` there carries a `%% GENERATED` banner and must not be hand-edited. `writing/overleaf.py`
moves the draft to and from Overleaf (`push`/`pull` by git; its docstring is the manual).

**`logs/`** (gitignored): detached-run scripts and their logs. Python output there needs `PYTHONUTF8=1`,
and workbooks under `data/` must be edited through Excel, not openpyxl (`notes/TODO.md`, "Traps").

**`RESEARCH_LOG.md`**: cross-cutting session log; module logs live under `python/<module>/`.
**`pyenv.md`**: required packages and versions.

## Status

All three model variants solve, calibrate and run their counterfactuals, and all 34 paper outputs are
wired end to end. The endogenous-`θ` layer (leaded and permanent timings, LOG and CRRA) is implemented
and calibrated; only the *sequential* timing is not. Open items: `notes/TODO.md` and the module READMEs.
