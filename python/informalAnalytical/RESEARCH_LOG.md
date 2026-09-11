# Research log — informalAnalytical

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md`, indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to look. A
lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-09-11 — informal targets: hours normalisation and formal-mean denominators

Same two fixes as `InformalSavings` (its log, same date): `addEigenVectors` imposes `∑γ_i(η_i/X_i)^ξ = 1`
(`eq:calibration:yNorm`) and `test.py` builds `z_j` against the γ-weighted formal mean
(`eq:calibration:z`). `test_calibration.py` checks informal hours and income on the solved path; LOG
calibration now β=0.671, ω=1.486, η0=0.288, X0=0.376. No paper output reads this model.
