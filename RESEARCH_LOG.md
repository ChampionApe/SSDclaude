# Research log

Cross-cutting/structural session log. For model-specific work, see `python/<module>/RESEARCH_LOG.md`.

## 2026-07-10
- Reviewed existing structure: `CLAUDE.md`, `informalAnalytical` code (`base.py`, `model.py`, `policy.py`), and `writing/informalAnalytical_docs.tex`. Found `model.py` has parameter/database scaffolding and partial calibration implemented, but `policy.py` (politico-economic equilibrium solve) is an empty stub, and the doc's numerical §PEELOG/§PEE/§Calibration sections are unwritten.
- Agreed on documentation conventions: each `python/<module>/` folder gets its own `README.md` (purpose, file map, implementation status) and `RESEARCH_LOG.md` (module-specific session log), kept up to date as code changes. Root `RESEARCH_LOG.md` is reserved for cross-cutting/structural sessions like this one.
- Updated `CLAUDE.md` to document these conventions. Expanded root `README.md` into a repo map.
- Created `README.md` + `RESEARCH_LOG.md` for `informalAnalytical` (with real implementation-status notes), `InformalSavings`, `US`, and `gridsearch` (placeholders — no code yet in the latter three beyond `gridsearch/__init__.py`).
- Next: start implementing the economic equilibrium solve for `informalAnalytical` (§EE numerical part of the docs — `Γs`, `Θh`, `Θs`, aggregate `s_t`/`h_t`), then the `policy.py` `LOG`/`CRRA` solve. `pyenv.md` is still empty and should be populated with actual package versions once we run the code.

## 2026-08-05
- Updated `CLAUDE.md`'s logging convention: `RESEARCH_LOG.md`/`README.md` updates now happen once, at the end of a working session (when the user signals it), not after every interaction — the prior per-interaction habit had gotten noisy (see this date's `informalAnalytical`/`gridsearch` logs for the last instance of it, consolidated into single entries after the fact).

## 2026-08-05 (cont'd) — session-usage reduction
User flagged the session was burning through usage faster than before and asked for durable fixes ahead
of starting a fresh session.
- Added a docstring-density convention to `CLAUDE.md`: keep equation cross-references/shape conventions/
  genuine gotchas; cut narration of design history, rejected alternatives, and inspiration comparisons
  (that belongs in `RESEARCH_LOG.md`). Applied it as a sweep across `informalAnalytical/base.py`/
  `policy.py`/`model.py` (the accumulated bloat from this session) — `gridsearch/*.py` was already at this
  density. Verified behavior-neutral via the full test suite before/after.
- Two workflow habits saved as feedback memories (not `CLAUDE.md`, since they're about how *I* work, not
  a project convention): stop writing a throwaway scratchpad diagnostic and then separately promoting the
  same checks into a real test once a verification pattern is established — write directly into the real
  test file; prefer `Grep` + narrow `Read` over re-reading a whole large file for one method.

## 2026-08-06 — session-usage reduction, round 2
Same ask as 2026-08-05, applied at end of the calibration-implementation session (see
`python/informalAnalytical/RESEARCH_LOG.md`'s 2026-08-06 entry for the actual work).
- Trimmed the new `model.py` §8/`base.py` §10 docstrings down to the house density; condensed
  `informalAnalytical/RESEARCH_LOG.md`'s older entries (~190 → ~65 lines) to fact + gotcha, dropping
  verification narration and inspiration-file comparisons — kept every bug/trap (the β>1 cap, the
  overflow fix, the non-integer-index fix) since those are exactly what a future session would otherwise
  silently re-trigger.
