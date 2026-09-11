# Research log — paper

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_paper.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-09-11 — Argentina rebuilt after the informal-target fix

Stages (i)–(iii) re-run for Argentina (`InformalSavings` log, same date, for the fix). `anchorGuess`
retuned; `ArgentinaCalibration` prints `η_i`/`X_i` to two decimals (the rescaled `X_i` are 0.74–1.24).
Only the five Argentina outputs were copied into `writing/Paper` (`build.py --only`): a US ESC run was in
flight. Prose updated to the new numbers in `Argentina.tex`, and the headline "a third" became "almost
half" in the abstract, introduction and conclusion. This is the vector-X Argentina; TODO W2 still decides
it against common X.
