# Research log (cross-cutting)

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_root.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-09-11 — context reset

The repo's markdown context had grown to ~400 KB. All six session logs, `notes/archive/`, the 2026-08-25
numerical-appendix planning note and `paper/figs_inspiration.md` moved to a root `archive/` (`git mv`),
with `archive/INDEX.md` listing every log entry by date and title. `.rgignore` keeps `archive/` out of
default searches. `notes/crossCuttingFindings.md` was cut to statement/tell/habit per finding, same
numbers (long form with measurements: `archive/findings_longform.md`); the six READMEs were cut to
orientation, each under ~100 lines, with the pre-cut versions in `archive/readmes/`. `CLAUDE.md` now
carries the size caps. Live paths cited from code (`crossCuttingFindings`, the three InformalSavings
notes, `TODO.md`) did not move; two code comments citing the old root log were repointed. The archived
logs sit in `archive/sessionLogs/`, not `archive/logs/`: `.gitignore`'s `logs/` rule matches any directory
of that name, which both untracks it and hides it from ripgrep.

## 2026-09-11 — the agent plan executed: exact CRRA ESC solver, two-part pipeline, variant twins in both arms

`notes/plan_2026-09-11.md` (deleted at the end of the day, per its own rule) ran end to end: C1, C2, R1, R3,
R4, W1–W3, then C3 and R2. Structural: (i) the US stages (i)/(ii) have a `main` and a `--prepub` part, and
the exact 2-D recursion is the published CRRA ESC method with a `method` column keyed into every CRRA csv
(`python/paper/RESEARCH_LOG.md`); (ii) both arms now carry two calibration variants with headline/twin
outputs (`config.US['commonX']` = True, `config.ARG['commonX']` = False) — for Argentina the variants print
identical results and differ only in the calibration table (`notes/argentina_commonX_vs_vectorX.md`,
decision W2); (iii) finding #14 (a `tail -F` on a pipeline log breaks the ps1's own `Add-Content`). Per-model
detail in the three module logs of the same date; open items for RKB in `notes/TODO.md` (W1, W2, W2b, W4, C4).
