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

## 2026-09-11 (evening) — common-X calibration variant (TODO C3)

`ModelInformalSavings(commonX=True)`: formal `η_i = (z^η_i)^{1/(1+ξ)} X^{ξ/(1+ξ)}`, `X_i = X` (Γ_h = 1 for any
X), the four-parameter root at X = 1, then `X` closed-form from the formal workweek `db['h0']` and the
equilibrium re-solved (`_calPostRoot`, identity checked). The informal targets `calibrationη0/X0` gain the
hours-unit ratio `M = ∑γ_i(η_i/X_i)^ξ/Γ_h` (`Base.hoursUnitRatio`; exactly 1 under vector X, so nothing
moved there). `calibrateRhoGrid.py --commonX` writes `informalSavings_rhoGridCommonX.csv` and
`instancesCommonX/`; `verifyResidual` is now evaluated at the final parameters (the root's x is at X = 1).
Anchor ρ = 1: β, ω, K/Y, τ, ι equal the vector-X ones to 1e-13, X = 1.937, η0 0.288 → 0.344, X0 0.375 → 0.804;
the ρ = 1 universal/eeOnly shocks reproduce the vector-X csvs to 1e-12. Docs: `model_calibration.tex`
(eq calibration:M, the common-X paragraph), `num_calibration.tex`. `test_calibration.py` §6 (slow).
