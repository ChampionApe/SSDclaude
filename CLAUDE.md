# Social Security Design and Its Political Support (2026)

## Project overview
The project develops an overlapping generations model with heterogeneous households and endogenous policy of the pension system and design. 

The final output from the project is a research paper in Overleaf that can be accessed here: https://da.overleaf.com/project/6a4b74c7259adae491b45669. 

## Structure
The project is self-contained in the current repository. Subfolders:
- `data/` - raw and processed data (not results).
- `python/` - python files.
- `results` - output tables, figures, and model instances and solution databases.
- `notes` - use this for smaller tasks and working notes. 
- `writing` - use this to generate tex and markdown files like model documentation. 
- `writing/Paper` - contains copy of latest draft of the final paper.

The `python/` folder organizes the code in five folders: Three of them implement different variations of the economic model (informalAnalytical, informalSavings, US), the fourth includes a small homemade package to use to solve tricky numerical problems using gridsearches (to be developed), and the fifth (`paper`) is the pipeline that turns solved models into the tables and figures in `writing/Paper`. 

### Model structure
The three models are similar, but the code and documentation is self-contained. For each model, we have:
* A tex documentation folder `writing/x/` with x being the model version, pulled into `writing/main.tex` by `\subimport`. Inside it, `model*.tex` define the model and its equilibria, `num*.tex` the numerical solution — split one file per section (see `writing/informalSavings/num.tex` for the pattern). Equations carry `\refeq:` labels that the `.py` docstrings reference by name, so a label rename has to be followed through the code.
* Three .py files that are linked:
    * `base.py` includes base classes that defines all the relevant functions from the documentation.
    * `policy.py` includes classes that implement the identification of sequences of policy functions.
    * `model.py` defines the parent class with database structure. Draws on `base.py` and `policy.py` classes directly.
* A `python/<module>/README.md` describing the module's purpose, file map, and current implementation status (what's solved vs. still a stub). Update this whenever the status changes materially — it's the fastest way for us (or a future session) to know what's actually working without re-reading all the code.
* A `python/<module>/RESEARCH_LOG.md` for session entries specific to that model (or to the gridsearch package).

### Paper outputs
Every table and figure in `writing/Paper` that comes from a model is produced by `python/paper/`, in three
stages: (i) `runCalibration.py`, (ii) `runShocks.py`, (iii) `build.py`. Stage (iii) reads only `results/`
— it imports no model code and unpickles nothing — so a paper rebuild costs seconds and can never turn
into a solve. Do not hand-edit a generated `.tex` in `writing/Paper`: it carries a `%% GENERATED` banner
and the next build overwrites it. Change the number at its source (`python/paper/config.py`, or the
experiment that produced the csv) and rebuild. See `python/paper/README.md`.


## Key conventions
- Language: Mainly Python.
- Writing: Do not waste energy on compiling tex files; add as local tex file under `writing` and let the user compile locally. 
- After a full working session, before the user shuts down the session (not during every interaction), append a short entry to the relevant log: the root `RESEARCH_LOG.md` for cross-cutting/structural work (repo organization, conventions, decisions spanning modules), or `python/<module>/RESEARCH_LOG.md` for work specific to one model (informalAnalytical, InformalSavings, US) or the gridsearch package.
- Keep a list of python packages including specific versions required for running the code updated in `pyenv.md`. 
- Keep each `python/<module>/README.md` current (see Model structure above).
- Docstrings/comments in `.py` files: keep only what a future session needs to *use or modify* the code correctly — the equation/doc cross-reference (e.g. `Eq (auxiliary:Gammas)`), shape conventions where non-obvious (e.g. `(M,)` vs `(M,ni)`), and genuine gotchas (why an argument must be explicit rather than read from db, a numerical trap like an overflow band that must not be reintroduced, why NaN must not be zero-filled). Do not narrate design history, debugging process, alternatives considered and rejected, or comparisons to a prior/inspiration implementation — that belongs in `RESEARCH_LOG.md`, not inline. If a docstring reads like a chronicle of how the code came to be rather than a spec of what it does now, trim it.