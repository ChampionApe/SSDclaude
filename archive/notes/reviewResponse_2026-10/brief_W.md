# Brief W: phase 3 of the review response (W1–W9), shared by every writing package

Phase 3 of `notes/plan_reviewResponse.md` (W16). Branch `review-2026-10`, from cd81410: all numbers are final (C1–C6
committed, checkpoint 2 passed, defaults confirmed by RKB 2026-10-25). Started 2026-10-25 on RKB's go.

## Read first

- `notes/plan_reviewResponse.md`: Principles, and your row of the Writing table.
- `notes/paper_reviewResponse.md`: the full text of every action (A1–A14) and comment (#1–#25, W15) your row names.
  These are the decisions; do not reopen them.
- `notes/paper_styleGuide.md`, which every sentence follows.
- The ledgers `notes/ledger_C1.md` … `ledger_C6.md`. Each prose number has its old and new value there, with
  file:line. **C6 is the final word**: where C1–C5 and C6 disagree, C6's value stands. `ledger_C6.md` §2–§4 lists
  the sentences that no longer hold.
- The theory notes `notes/theory_prop2.md` (T1), `theory_uniqueness.md` (T2) and `theory_closedForm.md` (T3),
  where your actions cite them.

## Rules

1. **Minimal writing** (principle 2). Update the numbers and the sentences your actions name. Rewrite a paragraph
   only where its claim changes (a sign, a ranking, an ordering, a threshold) or the content is new.
2. **Numbers in prose** come from the generated tables and figures (`writing/Paper/Tables`, `Figs`) or the csvs
   the ledgers cite, at the ledger's precision. Never edit a generated `.tex` (it has a `%% GENERATED` banner). If a
   table's note or content is wrong, report it: it is fixed at its source in `python/paper`.
3. **Your files only** (the table below). If a fix is needed in another package's file, report it and do not
   make it. Only W1 edits `References.bib`: other packages report the entries they need (key, full reference) and
   cite the key; W1 adds them. Only W6 edits `main.tex` (the new appendix's `\input`).
4. **Labels**: keep existing `\label`s. A new label follows the file's pattern; report it, so cross-references
   from other files can be added.
5. **Compiling**: do not compile in `writing/Paper` itself (agents run in parallel). Copy the folder to
   `logs/W<n>/build/` and run latexmk there; report new warnings (undefined references, overfull boxes) from your
   files. `writing/checkPaper.py` may be run on the real folder (it is read-only).
6. Do not commit. Do not push to Overleaf.

## File sets

| | Files (under `writing/Paper` unless stated) |
|---|---|
| W1 | `abstract.tex`, `Sections/Introduction.tex`, `Sections/Conclusion.tex`, `References.bib` |
| W2 | `Sections/Model.tex`, `Sections/Numerical.tex` |
| W3 | `Sections/Log.tex`, `Appendix/PoliticoEconomicEquilibrium.tex` (appendix B), `Appendix/EconomicEquilibrium.tex` if B's proofs need it |
| W4 | `Sections/Argentina.tex`, `Appendix/HouseholdSurveyArg.tex` (appendix E) |
| W5 | `Sections/OECD.tex`, `Appendix/CalibrationOECD.tex` (appendix F) |
| W6 | `Sections/EndogenousTheta.tex`, `Appendix/EndogenousDesignResults.tex` (appendix G), a new `Appendix/OECD26.tex`, `main.tex` |
| W7 | `Appendix/EndogenousDesign.tex` (appendix C) |
| W8 | `Appendix/TerminalStates.tex` (appendix D); also the technical note's `writing/US/num_esc.tex` and `num_robustroot.tex` and any other `writing/US/num*.tex` that describe the U.S. solver C6 changed |
| W9 | `writing/OnlineAppendix/*.qmd`, `python/paper/*` (builders, `config.py`), results through the builders only |

W8, the technical note: describe the solver as C6 left it (`python/US/RESEARCH_LOG.md`, entries of 2026-10-24
and 2026-10-25; `notes/brief_C6.md`):
- the τ-derivatives are a least-squares cubic in ln(1−τ) with knots 0.04 apart;
- `LeadedLOG` solves the anticipated tax at every candidate;
- `LeadedCRRA2D` is Catmull-Rom along θ at 13 nodes, clipped to bounds;
- the log tax solve's upper bound is u < 1.

Keep the equation labels the `.py` docstrings cite (CLAUDE.md).

W9 also owns the generated `NUM_Residuals` note in `python/paper/tablesHorizon.py`, which still says
"smoothing spline". It then runs `build.py`, `--site` and `--map`, and checks `test_onlineAppendix.py`.

## Report (your final message)

- What changed, as file:line with one line each. Mark every claim that changed (old → new).
- Each action and comment in your row: done, how, and where; or not done and why.
- Things for other packages: a bib entry, a label, a fix in someone else's file, a wrong generated note.
- The checks: latexmk in your copy (new warnings), and `checkPaper`.
- Open questions for RKB, if any; keep them few.
