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
quotes them). OA.2 and OA.3 cite appendices E and F; site republished (gh-pages `3d60368`). C9 closed: the two
`informalAnalytical` failures since C8 were a solver stopping rule, fixed in that module (its log); fast suites 24 of 24.

## 2026-10-08 (afternoon, evening) — the endogenous-design rewrite as an autonomous multi-agent run

RKB asked for a detailed plan from his sketch (`notes/plan_endogenousDesign.md` §A-B) and its autonomous
execution with agents on Opus and Fable. The plan (§C) ran in phases with gates: a Fable theorist derived the
variants and the Bismarckian-corner condition (`notes/esc_variants.md`), an Opus coder implemented the specs
and tests, Opus runners and builders produced the rows and exhibits, Fable writers took section 7 and appendix
C, Opus writers appendix G and the surrounding text, a Fable referee and an Opus numbers audit reviewed, a Fable
pass applied the findings and cut appendix C back with the propositions moved to the technical note (RKB's
instruction after reading it on Overleaf). Three new agent types on Fable at max (`model-theorist`,
`paper-writer-lead`, `paper-reviewer-lead`); the older types did not load this session, so those roles ran as
`general-purpose` with the model and effort set per call. Gate 1 changed a decision on the theorist's result
(the M weight on the linear term) and a run finding changed the paper's inequality claim; both are recorded in
the plan's §C.1 for RKB's review, with the plan's status paragraph listing his calls. Local commits by path at
every phase, no push to GitHub, Overleaf or the site. The precision item of the leaded recursion (TODO C11) and
the CRRA leg for the preferred cost (R6) are the open code items; the briefs and reviews are in `archive/notes/`.
