# Research log — US

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_US.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-09 (evening) — runs for the online appendix (branch `oa-revision`)

`runShocksUS.py --host UKUS` run in both variants (results/shocks/UKUS_shocks*.csv). New `runShocksXi.py`: the US
counterfactuals at ξ = 0.2, 0.3, 0.4 (LOG, common X), the US and France recalibrated at each ξ, France against a US
reference built from the ξ-calibrated US; ξ = 0.3 reproduces `US_shocksCommonX.csv` to 7e-12. `runESC.py`: stage
`pathHost` (France and the UK under the US λ and their own, `escPathHost.csv`) and `--scenarios`; both ESC drivers run
France's own row with a French scenario only; `HOST_SCENARIOS` and `config.US['esc']['uk']['scenarios']` add acute
ageing, run on the UK in LOG and exact CRRA (~7 min per ρ). Every published row unchanged; `test_esc.py` 85/85.
