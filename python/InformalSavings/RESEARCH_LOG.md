# Research log — InformalSavings

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md`, indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to look. A
lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-09-11 — the informal targets were mis-scaled; recalibrated

`X0` looked low (0.413 against formal `X_i` of 15–25). Two defects, both in the `η0/X0` step (also in
`informalAnalytical`). (i) `eq:calibration:eta0/X0` read `h_t` as average formal hours, true only under
`∑γ_i(η_i/X_i)^ξ = 1`; scipy's unit-norm eigenvector gave 0.499, so informal hours solved at 1.90× the
formal average against a target of 0.95. Fixed as a normalisation (`addEigenVectors`, docs
`eq:calibration:yNorm`); equilibrium-neutral to 9 digits, same `η0/X0`, formal `X_i` now 0.74–1.24.
(ii) `test.py` divided `z_j` by the unweighted mean over all five groups; now the γ-weighted formal mean
(`eq:calibration:z`). This one moves results: ρ-grid, shocks, `(ε,θ)` grid re-run (`--force`), ρ=1 reform
effect +0.99 → +1.25 p.p. (a third → almost half of the 1.8% of GDP). `test_calibration.py` now checks
informal hours and income on the solved path. Finding #12.
