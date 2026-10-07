# Social Security Design and Its Political Support (2026)

## Project overview
The project develops an overlapping generations model with heterogeneous households and endogenous policy of the pension system and design. 

The final output from the project is a research paper in Overleaf that can be accessed here: https://da.overleaf.com/project/6a86b4569416ca8062f0b899. The technical note (`writing/main.tex` and the model folders) is a separate Overleaf project: https://da.overleaf.com/project/6a4b74c7259adae491b45669. Both are synced with `writing/overleaf.py`.

## Structure
The project is self-contained in the current repository. Subfolders:
- `data/` - raw and processed data (not results).
- `results` - output tables, figures, and model instances and solution databases.
- `notes` - use this for smaller tasks and working notes. Only what is live stays here (the open list, the style guide, the findings, a brief or problem note while its work is open); when the work closes, the note moves to `archive/notes/` with a line in `archive/INDEX.md`.
- `archive` - history: session logs to 2026-10-07, closed notes, plans and briefs, retired diagnostics and superseded results, long-form findings, pre-cut READMEs. Indexed in `archive/INDEX.md`, which opens with the paper's decisions by theme; excluded from default searches by `.rgignore`. Do not read it unless a live file points there or you are stuck on something the index names, and never restate its content into a live file.
- `logs` (gitignored) - detached-run scripts and their logs.
- `writing` - use this to generate tex and markdown files like model documentation. 
- `writing/Paper` - contains copy of latest draft of the final paper.
- `writing/OnlineAppendix` - the online appendix (Quarto), built from `results/` by `python/paper/build.py --site`.

 

### Model structure (informalAnalytical, informalSavings, US)
The three models are similar, but the code and documentation is self-contained. For each model, we have:
* A tex documentation folder `writing/x/` with x being the model version, pulled into `writing/main.tex` by `\subimport`. Inside it, `model*.tex` define the model and its equilibria, `num*.tex` the numerical solution — split one file per section (see `writing/informalSavings/num.tex` for the pattern). Equations carry `\refeq:` labels that the `.py` docstrings reference by name, so a label rename has to be followed through the code.
* A `python/<module>/README.md` describing the module's purpose, file map, and current implementation status (what's solved vs. still a stub). Update this whenever the status changes materially — it's the fastest way for us (or a future session) to know what's actually working without re-reading all the code.
* A `python/<module>/RESEARCH_LOG.md` for session entries specific to that model (or to the gridsearch package).

### Paper outputs
Every table and figure in `writing/Paper` that comes from a model is produced by `python/paper/`, in three
stages: (i) `runCalibration.py`, (ii) `runShocks.py`, (iii) `build.py`. Stage (iii) reads only `results/`
— it imports no model code and unpickles nothing — so a paper rebuild costs seconds and can never turn
into a solve. Do not hand-edit a generated `.tex` in `writing/Paper`: it carries a `%% GENERATED` banner
and the next build overwrites it. Change the number at its source (`python/paper/config.py`, or the
experiment that produced the csv) and rebuild. See `python/paper/README.md`.

A referee must be able to trace every table, figure and data input of the paper from the GitHub repo:
`REPLICATION.md` (root) is that map and `data/README.md` sources every input file. `build.py --map`
regenerates the output table in `REPLICATION.md`; the hand-written parts and `data/README.md` are
updated whenever a data file, a stage or a figure outside the pipeline is added or changed.


## Key conventions
- After a full working session, before the user shuts down the session (not during every interaction), append a short entry to the relevant log: the root `RESEARCH_LOG.md` for cross-cutting/structural work (repo organization, conventions, decisions spanning modules), or `python/<module>/RESEARCH_LOG.md` for work specific to one model (informalAnalytical, InformalSavings, US) or the gridsearch package.
- Context budget, so the docs stay cheap to read: a `README.md` stays under ~100 lines and holds orientation only (purpose, file map, how to run, invariants as one-liners, status, open items). A log entry is at most ~10 lines: what changed, why, where to look. A lesson that recurs goes to `notes/crossCuttingFindings.md` once, as statement/tell/habit, cited by number; its numbering is referenced from code and must not change. Anything longer (measurements, investigations, superseded plans) goes to `archive/` with a pointer from the live file.
- Keep a list of python packages including specific versions required for running the code updated in `pyenv.md`. 
- Keep each `python/<module>/README.md` current (see Model structure above).
- Docstrings/comments in `.py` files: keep only what a future session needs to *use or modify* the code correctly — the equation/doc cross-reference (e.g. `Eq (auxiliary:Gammas)`), shape conventions where non-obvious (e.g. `(M,)` vs `(M,ni)`), and genuine gotchas (why an argument must be explicit rather than read from db, a numerical trap like an overflow band that must not be reintroduced, why NaN must not be zero-filled). Do not narrate design history, debugging process, alternatives considered and rejected, or comparisons to a prior/inspiration implementation — that belongs in `RESEARCH_LOG.md`, not inline. If a docstring reads like a chronicle of how the code came to be rather than a spec of what it does now, trim it.