# Python environment

Virtual environment lives in `.venv/` at the repo root (not committed — see `.gitignore`). Created with:
```
python -m venv .venv
.venv\Scripts\python.exe -m pip install numpy pandas scipy symMaps
.venv\Scripts\python.exe -m pip install -e python
```
The last line installs the homemade `gridsearch` package (`python/gridsearch/`, declared by `python/pyproject.toml`) in editable mode — `import gridsearch` then works from any file/cwd with no `sys.path` manipulation, and edits to `gridsearch/*.py` take effect immediately (editable install = a path mapping, not a copy). `pyproject.toml` explicitly lists `packages = ["gridsearch"]` rather than relying on auto-discovery, since `python/` also holds `informalAnalytical`/`InformalSavings`/`US`, which carry stray `__init__.py` files but aren't meant to be imported as packages.

Python: 3.14.6 (`C:\Python314\python.exe`)

## Packages (pinned, from `pip freeze` on 2026-07-10)
- numpy==2.5.1
- pandas==3.0.3
- scipy==1.18.0
- symMaps==0.0.4 — Rasmus/ChampionApe's symbolic-index-mapping package (https://github.com/ChampionApe/symMaps). Provides `SimpleSys`, `Lag`, `Lead`. Pulls in `pyDbs` as a dependency.
- pyDbs==0.1.8 — dependency of symMaps (`adj`, `adjMultiIndex`, `Broadcast`, `Gpy*`, `SimpleDB`, `cartesianProductIndex`). Note: this is a *different* API than the old pyDbs version the code was originally written against (that version had `SymMaps`/`adj` at top level with a `getShift` method) — see `RESEARCH_LOG.md` 2026-07-10 entry.
- openpyxl==3.1.5 — pulled in by pyDbs; used for reading `data/*.xlsx` calibration inputs (see `informalAnalytical/test.py`).
- python-dateutil==2.9.0.post0, six==1.17.0, tzdata==2026.3, et_xmlfile==2.0.0 — transitive dependencies (pandas/openpyxl).
- gridsearch==0.0.1 — this repo's own homemade package (`python/gridsearch/`), editable-installed from `python/pyproject.toml` (added 2026-08-05).

## Setup from scratch
```
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install numpy pandas scipy symMaps
.venv\Scripts\python.exe -m pip install -e python
```
