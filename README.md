# SSDclaude

Code repository for *Social Security Design and Its Political Support* (2026). See `CLAUDE.md` for project
conventions; this file is a map. **`REPLICATION.md`** walks a reader from every table and figure of the
paper to the data, the script and the command that produce it.

## Layout

**`data/`**: raw and processed inputs (not results). `ArgentinaTest.xlsx`, `USMain_test.xlsx`,
`FRMain.xlsx`, `UKMain.xlsx` (the last also regrouped at US percentiles), plus `argentina_*.csv`, the
calibration targets `python/paper/dataTargets.py` derives from the Penn World Table, and `oecdFigure1*.csv`
behind figure 1. Each file's source, vintage and reader: `data/README.md`.

**`python/`**: three model variants, a shared numerical package, and the paper pipeline. Each subfolder
has a `README.md` (purpose, files, how to run, invariants, status, open items) and a terse `RESEARCH_LOG.md`.

| | |
|---|---|
| `informalAnalytical/` | the analytical (log-preference) informal-sector model and **ancestor** of the other two; shared conventions documented there |
| `InformalSavings/` | the variant where the informal type saves. Calibrated to Argentina, targeting its capital-output ratio |
| `US/` | `informalAnalytical` without the informal type, for the US, France and the UK. Also the endogenous-`θ` work |
| `gridsearch/` | bounded-root reparameterisation, 1-D root selection, Cartesian grids, gridded interpolation, an anchored parameter march, and `testing.py`, the shared PASS/FAIL harness |
| `paper/` | the three-stage pipeline that builds `writing/Paper`'s tables and figures, and the online appendix, from `results/` |
| `runTests.py` | the repo-wide runner: 24 fast suites (~7 min), `--all` adds the five slow ones (~1 h), `--list`, `-k <pattern>` |

**`results/`**: solved output. `calibration/` holds the parameter sweeps and one pickled instance per point,
each sweep with its own pickle directory (`instances/` for Argentina, `instancesUS*`, `instances{FR,UK,UKUS}*`);
`shocks/` the counterfactual paths; `sweeps/` the `(ε, θ)` comparative statics; `esc/` the endogenous-`θ`
runs; `numerical/` the stationary-policy checks; `paper/` the built tables and figures. Superseded runs go in a
subdirectory, never beside the live ones (`notes/crossCuttingFindings.md` #8).

**`writing/`**: `main.tex` plus one subfolder per model variant with `model*.tex` (model and equilibrium)
and `num*.tex` (numerical solution), written as self-contained technical notes; `US/model_esc.tex`/
`num_esc.tex` cover the endogenous `θ`. Tex labels are cited from docstrings, so follow any rename
through the `.py` files. **`writing/Paper/`** is the current draft, compiled locally by the user; a
generated `.tex` there carries a `%% GENERATED` banner and must not be hand-edited. `writing/overleaf.py`
moves the draft to and from Overleaf (`push`/`pull` by git; its docstring is the manual).
**`writing/OnlineAppendix/`** is the online appendix, a Quarto book built from `results/` by
`python/paper/build.py --site`, published at https://championape.github.io/SSDclaude (its `README.md`).

**`notes/`**: the live working notes.

| | |
|---|---|
| `TODO.md` | the one open list |
| `paper_styleGuide.md` | the paper's register: voice, units, terminology, LaTeX conventions |
| `paper_costLiterature.md` | the literature behind section 7's cost of redistribution, and how the paper motivates it |
| `crossCuttingFindings.md` | nineteen lessons cited by number from code and READMEs. Read #3–#5 before diagnosing a stalled outer solver, #7 before keying a fix to one solver, #9 before writing a parameter the model derives, #13 before resuming any sweep, #15 before spending a normalisation, #18 before ranking candidates |

**`archive/`**: history, indexed in `archive/INDEX.md`, which opens with the paper's decisions by theme and
where each is argued: the session logs to 2026-10-07, closed notes, plans and agent briefs, retired
diagnostics (`archive/code/`), superseded results (`archive/results/`), the long-form findings and the pre-cut
READMEs. `.rgignore` keeps it out of default searches; read it by path when a live file points there.

**`logs/`** (gitignored): detached-run scripts and their logs. `finalRun1002/` (both arms, 2026-10-03) and
`finalRunC8/` (the Argentine arm, 2026-10-07) are the runs behind the committed results.

**`RESEARCH_LOG.md`**: cross-cutting session log; module logs live under `python/<module>/`.
**`pyenv.md`**: required packages and versions.

## Traps when running the pipeline on Windows

- `PYTHONUTF8=1` for every pipeline run: the scripts print Greek letters and crash on the first print under
  the cp1252 console.
- PowerShell `*>` redirection writes UTF-16; route python output through `cmd /c "... > log 2>&1"`.
- A `tail -F` on a log that a PowerShell script appends to makes every later `Add-Content` fail silently;
  poll with `grep -q` in an `until` loop instead (finding #14).
- Workbooks under `data/` are edited in Excel (COM from PowerShell works) or written as literal values, never
  through openpyxl: it drops the cached formula values, pandas then reads NaN and every steady state fails.

## Status

All three model variants solve, calibrate and run their counterfactuals, and all 82 outputs are wired end to
end (`python/paper/build.py --list`): 15 in the paper, the rest in the online appendix. The endogenous-`θ`
layer (leaded and permanent timings, LOG and CRRA) is implemented and calibrated; only the *sequential* timing
is not. Every count in the committed results reads one equilibrium and no fallback. Open items:
`notes/TODO.md` and the module READMEs.
