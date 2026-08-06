# SSDclaude
Code repository for *Social Security Design and Its Political Support* (2026).

See `CLAUDE.md` for full project conventions. This file is just a map of the repo.

## Layout
- `data/` — raw and processed data (not results).
- `python/` — model code, one subfolder per model variant plus a shared numerical utility package. Each subfolder has its own `README.md` (purpose, files, implementation status) and `RESEARCH_LOG.md` (model-specific session log).
    - `informalAnalytical/` — analytical (log-preference, closed-form) informal-sector model. Furthest along.
    - `InformalSavings/` — informal savings model variant. Not started.
    - `US/` — US model variant. Not started.
    - `gridsearch/` — homemade numerical package for gridsearch-based solving. Has one generic module (`robustRoot`, bounded-root reparameterization) so far.
- `results/` — output tables, figures, model instances, and solution databases.
- `notes/` — smaller tasks and working notes.
- `writing/` — tex/markdown documentation, one doc per model variant (e.g. `informalAnalytical_docs.tex`).
- `RESEARCH_LOG.md` — cross-cutting/structural session log (repo organization, decisions spanning modules). Model-specific logs live under `python/<module>/`.
- `pyenv.md` — required python packages and versions.

The final output is a research paper in Overleaf: https://da.overleaf.com/project/6a4b74c7259adae491b45669.
