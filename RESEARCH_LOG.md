# Research log (cross-cutting)

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_root.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-07 (evening) — the repo cut to the paper as it stands: notes, logs, tests and context

On RKB's instruction, what served the path rather than the paper left the live tree. `notes/` keeps four files (the
TODO, the style guide, the findings, `paper_costLiterature.md`); sixteen closed notes, plans and briefs went to
`archive/notes/`, four 2026-08-23 tex/bib leftovers were deleted. Every session-log entry to this date (67, six logs)
moved to `archive/sessionLogs/`, and `archive/INDEX.md` now opens with the paper's decisions by theme. Retired
diagnostics went to `archive/code/`, superseded results to `archive/results/`; `logs/` keeps `finalRun1002/` and
`finalRunC8/`. The traps moved to the root README, D1's data caveats to `data/README.md`, the `\oa{key}` rule to the
style guide; READMEs, `CLAUDE.md`, the agent definitions and code comments repointed. Tests: `US/test_createCopyFromt0.py`
archived (nothing calls the US model copies), T2's pre-split copy cut, `test_eu.py`'s FRUK check asserts the sheets
load, `paper/test_onlineAppendix.py` registered; the permanent-timing and FOC-layer checks stay (the technical note
quotes them). Fast suites 22 of 24; the two `informalAnalytical` failures date from C8's `8e85632` (TODO C9).
