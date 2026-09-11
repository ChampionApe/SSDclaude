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
