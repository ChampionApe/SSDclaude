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

## 2026-10-09 (evening) — the online appendix on a branch in its own worktree

While another session drafts the paper on `main`, the online appendix is rebuilt on branch `oa-revision` in the worktree
`../SSDclaude-oa` (`.venv` a junction to the main checkout's), so neither session's commits interleave with the other's.
The only shared file is the generated `writing/Paper/onlineAppendix.tex`, which defines every key the paper cites.
Plan, decisions and status: `notes/plan_onlineAppendix.md` (untracked in the main checkout); module logs: python/paper,
python/US. Headless Chrome (`--headless=new --virtual-time-budget`) checks the OJS pages when the desktop session is
locked and the browser extension's tab is hidden.

## 2026-10-09 (night) — the online appendix merged, published, and the unused outputs retired

On RKB's go `oa-revision` went into `main` by fast-forward (`ea52b8e`). The idle paper session had uncommitted edits
in four files the branch changes: all its uncommitted work was first stored as a stash ("paper session's uncommitted
work at 58b53fb"), then three-way merged and left uncommitted on the new HEAD. `_escPairs`'s same-reading baseline
and its README line carry over; its edits to code the branch retired (`_escTable`, the old site registry) and the
retired tables' rebuilt files live only in that stash. D5 done: 94 outputs down to 35 (python/paper log). The site
was published from the clean worktree (gh-pages `e3810ba`); worktree and branch removed, run logs kept in `logs/oa`.
The plan is archived (`archive/notes/plan_onlineAppendix.md`); open: TODO W13 (the paper's pointers to the site), C12.
Bash-tool heredocs collapse a double backslash to one: edit scripts with TeX in them go through a file written by Write.

## 2026-10-23 — the AI review reconciled and the response planned

The review of 2026-10-22 (`coarse-output/`) was read critically and reconciled comment by comment with RKB:
`archive/notes/reviewResponse_2026-10/paper_reviewResponse.md` holds the agreed actions A1–A14 and the detailed comments at their first-pass
verdicts; `archive/notes/reviewResponse_2026-10/plan_reviewResponse.md` turns them into agent packages, with a checkpoint before any writing (TODO
W16). Found on the way: the U.S. design target is pension-only (39.2/49.2; PaG 2021 has 49.6) while τ includes
Medicare, against the text (decided: pensions only in all three countries, Medicare in the OA); appendix B.1 prints
the young term with 1+β; ν_t is UN WPP 2024 total population growth, not census data. An agent assembled the
29-country inputs (`data/oecd29*.csv` by `python/paper/oecd29Data.py`, `notes/data_oecd29.md`). Python run with
`-I` ignores PYTHONIOENCODING: Greek letters print with `-X utf8`.

## 2026-10-24 to 2026-10-26 — the review response carried out (W16 closed)

Phases 1–3 of the plan of 2026-10-23: code and runs C0–C7, theory notes T1–T3, the writing W1–W9 and verification V
(numbers audit, referee pass, 15 fixes, `runTests.py --all` 35/35), commits `f3a15a4`, `cd81410`, `6bb36ec`, `d5f0ef6`.
Decided with RKB on 2026-10-26: A13 as the strategic term in the OA only; France's ν at PaG 2021's retirement-age gaps
(1.5/1), rerun as C7, which moved the French leisure rows and left one design-layer fallback state, now stated; section
7.1's wording kept. The workbooks' `Readme` sheets were deleted, their content in `data/README.md`. Both Overleaf
projects pushed and the OA published from `d5f0ef6`. Everything is in `archive/notes/reviewResponse_2026-10/`
(`archive/INDEX.md`); left open: TODO C13 (the A13 split), D3, W17. Findings #20–21.

## 2026-10-27 — the paper by object (C14, R6, R7, W18–W21, V)

Decided with RKB in the morning: one laboratory, the U.S., with France and the UK as donor data plus the deep test;
section 6 ends with the 26-country test of spending at the observed designs without the cost, section 7 holds the
deep test (7.3) and the design test (7.4); the cross-section transports ε (λ_i = ε Π_i/R_i, `sizePiR`), β common with
the common-return bracket beside, both turnouts run; the UK as host retired (R7, D3 closed). Plan and ledger in
`archive/notes/byObject_2026-10/`. Checkpoint 1: ε, common β and U.S. turnout as the main variant, the inequality verdict
conditional on the turnout profile, the deep test under both transports (a third of the UK's distance and little of
France's under ε, a quarter of each under λ). Runs 3 h 19 min, every row one equilibrium; new exhibits
`OECD26_Spending`, `OECD26_Robustness`, `OECD26_Reconcile`, `USFRCalibration`; `runESC.mergeWrite` rereads csvs
round-trip exact. Overleaf pulled before the writing (RKB's abstract and introduction edits kept) and pushed after V
(numbers audit and referee pass by two reviewers, their fixes in). Symbol rule: the transported parameter is
`\varepsilon`, never the universal pension's `\epsilon` (style guide §4). Lesson: tex edits never through the Bash
tool's sed or heredocs, which mangle backslashes (a `\v` became a vertical tab); scripts written with Write instead.
Commits e14e556, 8267f10; `runTests.py --all` 35/35 in 3068 s; the online appendix published from 8267f10 (gh-pages 4281a38). Open: RKB's Overleaf review (the Conde-Ruiz sentence's new place in the
introduction, the ε letter), W17, C13, C12, D2, W14.
