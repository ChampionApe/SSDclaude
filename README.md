# SSDclaude

Code repository for *Social Security Design and Its Political Support* (2026). See `CLAUDE.md` for project
conventions; this file is a map.

## Layout

**`data/`** — raw and processed inputs (not results). `ArgentinaTest.xlsx`, `USMain_test.xlsx`,
`FRMain.xlsx`, `UKMain.xlsx` (the last also carries a US-percentile regrouping of the UK data, for
counterfactual comparability), plus `argentina_*.csv`, the calibration targets
`python/paper/dataTargets.py` derives from the Penn World Table.

**`python/`** — three model variants, a shared numerical package, and the paper pipeline. Each subfolder
has its own `README.md` (purpose, files, status) and `RESEARCH_LOG.md`.

| | |
|---|---|
| `informalAnalytical/` | the analytical (log-preference) informal-sector model, and the **ancestor** of the other two — the shared conventions are documented there |
| `InformalSavings/` | the variant where the informal type saves rather than being hand-to-mouth. Calibrated to Argentina, targeting its capital-output ratio |
| `US/` | `informalAnalytical` without the informal type (`γ_0 = 0`), for the US, France and the UK. Also carries the endogenous-`θ` work |
| `gridsearch/` | bounded-root reparameterization, 1-D root selection, Cartesian grids, gridded interpolation/smoothing/differentiation, and an anchored parameter march. Also `testing.py`, the shared PASS/FAIL harness — it lives here because `gridsearch` is the only importable package |
| `paper/` | the three-stage pipeline that builds `writing/Paper`'s tables and figures from `results/` |
| `runTests.py` | the repo-wide runner: 22 fast suites (~160 s), `--all` adds the four slow suites (~1 h), `--list`, `-k <pattern>`. Every suite also runs on its own |

**`results/`** — solved output. `calibration/` holds the parameter sweeps and one pickled instance per
solved point, each sweep with its **own** pickle directory since the filenames are the `ρ` alone
(`instances/` for Argentina, `instancesUS*`, `instances{FR,UK,UKUS}*`); `shocks/` the counterfactual paths,
full-effect and economic-equilibrium-only; `sweeps/` the cartesian `(ε, θ)` comparative statics; `esc/` the
endogenous-`θ` runs; `paper/` the built tables and figures. Superseded runs go in a subdirectory, never
beside the live ones — `notes/crossCuttingFindings.md` #8.

**`notes/`** — working notes, and where longer findings live so the READMEs can stay short.

| | |
|---|---|
| `crossCuttingFindings.md` | thirteen findings that recurred across modules, written once and cited by number. Read #3–#5 before diagnosing any outer solver that stalls (and note #4: on the `informalAnalytical`/`US` lineage check #5's knot count first), #6 after fixing one, #7 before keying a fix or a diagnostic to one solver/branch/range — or before trusting a hard-coded bound in a module that began as a copy, #9 before writing a parameter the model also derives from data, #10 before trusting a sensitivity check whose subject might sit on a boundary, #11 before grid-maximising over an instrument that also enters a predetermined state, #12 before adopting a calibration target, and #13 before resuming any sweep, or after changing anything one has already been run under |
| `informalSavings_numericalDeviations.md` | where `InformalSavings`' code departs from the `num_*.tex` specs, with the measurement behind each |
| `informalSavings_resolvedIssues.md` | two resolved calibration defects and the still-live settings they justify |
| `argentina_calibrationTarget.md` | why the calibration targets K/Y rather than the savings rate, and the map from target to `β` |
| `esc_experiments_acrossRho.md` | the endogenous-`θ` counterfactuals across `ρ ∈ {0.5, 1, 2}` |
| `todo_escPermanentTiming.md` | the one piece of open ESC work |
| `archive/` | measurements and results demoted out of the module READMEs |

**`writing/`** 
* Tex documentation: `main.tex` plus one subfolder per model variant, each with
`model*.tex` (model and equilibrium definitions) and `num*.tex` (numerical solution).
* `US/model_esc.tex` / `num_esc.tex` document the endogenous choice of `θ`.
* The `num*.tex` sets are written as self-contained, final-state technical notes for the public repo: strategy overview and repo URL in
`num.tex`, the shared grid-search machinery stated once per model in `num_robustroot.tex`
(`eq:extendedGrid`/`eq:objectiveProfile`/`eq:candidates` are defined there, not in `num_peeLOG.tex`), and
no development history — that stays in `notes/` and the logs.
* Docstring-cited labels were preserved throughout the 2026-08-25 restructure; keep them stable, or follow a rename through the `.py` files.
* **`writing/Paper/`** holds the current draft. Compiled locally by the user, not by agents; do not hand-edit a generated `.tex` there — it carries a `%% GENERATED` banner and the next `build.py` overwrites it.

**`RESEARCH_LOG.md`** — cross-cutting session log (repo organization, decisions spanning modules).
Model-specific logs live under `python/<module>/`. **`pyenv.md`** — required packages and versions.

## Status

All three model variants solve, calibrate and run their counterfactuals, and all 23 paper outputs are
wired end to end. The endogenous-`θ` layer (leaded and permanent timings, LOG and CRRA) is implemented and
calibrated; only the *sequential* timing is not. Per-module detail and open items are in the module
READMEs.
