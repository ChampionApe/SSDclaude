# Research log — InformalSavings

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-23 — C2 code (W16, `archive/notes/reviewResponse_2026-10/brief_C2.md`): the reform period's lags, the GDP target, ε = 0
- #4: a copy's first period rebuilt the retirees' formal shares per candidate tax at its own vintage (new ε in
  κ_{t0}; under CRRA also ν_{t0+1} in B), and `EE_report` took t0's lags from `initialState_solve` (c20 up to 5.7% off).
  `stateAtT0` now returns `inherited` (s_{t0-1,i}/s_{t0-1}, h_{t0-1}); `solvePEE_*(inherited=)` holds the shares in
  the t0 tax condition (`policy` `si_s0`), consistency from t0+1; `EE_report(lagged=)`. ρ = 1 common X: τ_2010
  0.130021 → 0.129974 (Δτ 2.0790 → 2.0744 pp); the no-shock control now 1.6e-6 at t0 (two grid roots, not 1e-10).
- #3: GDP = formal + informal output (w⁰η₀h₀); `taxTarget` gives τ0 = 0.1181, y = 0.0753 (was 0.071/0.65 = 0.1092).
- A7: `epsPre0` switch (`--epsPre0` on calibrateRhoGrid/shockUniversal); shock csvs carry bi1..biJ, biAvg, Y, Y0.
- `test_reformVintage.py` (7 FAIL and a crash on the old code); test_calibrationGrid's anchor now β 0.668641, ω
  1.496254. Stage (i)/(ii) not rerun: the Argentina results are stale.

## 2026-10-23/24 — C2 runs: stage (i)/(ii) on the C2 code, the ε = 0 variant, the reform's diagnostics
- Self-check: the committed ρ = 1 instance reproduced the coder's Δτ 2.074358 p.p. Both variants re-swept (`--force`,
  common X first; 5.4 h and 2.9 h on a loaded machine), stage (ii) main and the stationary check; `logs/C2runs/`.
- Headline ρ = 1: τ₀ 0.1181, β 0.669, ω 1.496; 2010 Δτ +1.95 p.p. (was 2.08), spending +1.17% of GDP (65% of 1.8%),
  savings −0.36 p.p. of GDP, formal benefits +1.46% (−12.70% at fixed taxes). ε = 0 variant: Δτ +4.20 p.p.
- New `reformDiagnostics.py` (`ARG_reform{FOC,B5,HouseholdSavings,Refine}_commonX.csv`); `sweepEpsThetaGrid.py`
  writes `srGDP`, `Y`, `Y0`. The tax response turns negative between ρ = 0.6 and 0.5, grid-resolved.
- Numbers, sources and the paper's sentences: `archive/notes/reviewResponse_2026-10/ledger_C2.md`.

## 2026-10-24 — C4 (W16, A6): horizon, terminal condition and first-order-condition residuals
- New `runHorizon.py` (not wired): the common-X instances at T = 2130/2190/2280 and under the steady-state terminal
  condition (40 periods appended; the 2190 policy stationary to 8e-7), baseline and universal reform; `resize` equals a
  fresh build at every T. Self-check: the 2190 rows give `universal_match_rho*_commonX.csv`'s τ_2010 to 8e-17.
- 2010 tax within 0.005 p.p. across horizons; the reform's 2010 response at ρ = 1 is 1.950 p.p. (2130: 1.942; 2280 and
  steady state: 1.950), the largest move −0.420 → −0.390 p.p. at ρ = 0.5, T = 2130.
- Residuals |τ_FOC − τ̂| off the grid: ≤ 0.008 p.p. on the path (0.014 on a 4× tax grid); every off-grid state ≤ 0.003
  (ρ = 1) and 0.015 p.p. (ρ = 2); at ρ = 0.5 the 2-D smoothing departs ≤ 0.35 p.p. from the raw selection at
  1920–2010 states away from the path. Numbers `archive/notes/reviewResponse_2026-10/ledger_C4.md`, log `logs/C4/ARG.log`.
