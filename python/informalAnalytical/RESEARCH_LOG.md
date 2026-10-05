# Research log — informalAnalytical

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md`, indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to look. A
lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-02 — tax candidates tested and ranked at frozen savings shares (finding #18)

`notes/brief_informalFrozenSelection_2026-10-02.md`, on the US pattern: `roots1d.selectMax(ND)` → `selectMaxFrozen(ND)` via
`LOG.objectiveFrozen`/`_select`/`_selectND` (`selection`, a class attribute; `'legacy'` = the integral rule) and
`CRRA.objectiveFrozen`, with `focGrid_t` split into `focParts_t` + `zAtShares` (bitwise the old formula, Σz
-3009.6235507679557). Two departures from the US code: the retirees' level is ln c at ρ = 1 (`_retireeLevel`; c^p/p
gave nEq = 0 at every state of the ρ = 1 terminal collapse), and a candidate on a node reads the hours there
(`_interpAtCand`; `interpAlong`'s 0·NaN lost every upper corner next to an infeasible cell, 20 of 20 states).
`solveRobust(check=True)`: full-grid pass on every solve, +30 ms; gradient solution kept bitwise. Counts in
`solvePEE_*`/`approximatePEE`. Quick-test models: one equilibrium everywhere, every τ bitwise the old rule (LOG Στ
3.359229625878843). Checks: test_cacheParams §7, test_crraTerminal §5, test_crraBackward §7, test_crraPEE. No paper output reads this model.

## 2026-09-11 — informal targets: hours normalisation and formal-mean denominators

Same two fixes as `InformalSavings` (its log, same date): `addEigenVectors` imposes `∑γ_i(η_i/X_i)^ξ = 1`
(`eq:calibration:yNorm`) and `test.py` builds `z_j` against the γ-weighted formal mean
(`eq:calibration:z`). `test_calibration.py` checks informal hours and income on the solved path; LOG
calibration now β=0.671, ω=1.486, η0=0.288, X0=0.376. No paper output reads this model.
