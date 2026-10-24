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

## 2026-10-23 — C0 of the review response: candidate counts in every PEE solve (branch `review-2026-10`)

The counts now come with the solve's return value into the driver rows: `calibratePoint`'s record (every US, UK,
France sweep), `shocks.runOne` (full effect; `runShocksUS.effectRows`, also used by `runShocksXi.py`), the
permanent timing (`solvePermanent`, `policy.mergeMultiplicity` over the candidates and the chosen path),
`runESCcrra.stageSequential`, and the design layer on `stationaryApproxESC` rows. Still -1: the 'ee' rows,
failed cost calibrations, and the tax columns of the exact CRRA root layer (its tax step `frozenTaxPass`
counts nothing; the design columns carry it). τ_2020 of a ρ = 1 calibration point and of acute ageing bitwise
old vs new in one process; the permanent timing jitters ~1e-14 between identical runs. `test_counts.py`.
No csv rewritten: the counts land on C1's reruns.

## 2026-10-23 — C1 of the review response: pension-only recalibration, Medicare reading, Π-inclusive cost

Workbooks at pensions only (U.S. τ0 0.105229, θ* 0.7278): stages (i), (ii) and `--prepub` rerun (`logs/C1/`) after a
self-check (HEAD's targets give the θ = 1 tax 0.122797 and λ 8.643207356 bitwise). New: `getθ` scales θ by 1 − `Ushare0`,
`test.reading(M)` puts Medicare in τ0 and θ (`--medicare`, sweep/shocks `USMedicare`); spec `'sizePiR'` (λ·Π_t/R_t, π
solved to the path's own, `ModelESC._ΠRFixedPoint`, calibrate's outer π loop); `calibrateWedge` brackets across a failed
scan node; `collectESCexperiments.py --costs`. Found: at ρ = 2 the ns = 50 CRRA tax solve jumps by ~1e-5 in τ at some
(β, ω, λ), which stops the (β, ω) root and 2-cycles the π iteration (damped, accepted below 2e-4); 'sizePiR' scans at
ns = 150. LOG λ 11.564, 'sizePiR' 20.839; the closed-form θ = 1 tax holds to 6e-13. Numbers: `notes/ledger_C1.md`.

## 2026-10-23 — C3 of the review response, phase 1: the cross-country test's code (branch `review-2026-10`)

`oecd26.py`: `ModelOECD(ModelESC)` from `data/oecd29*.csv` (groups at the U.S. percentiles, θ = 2 − 1/I clipped
and re-derived at every refresh, #9; WPP ν; figure 1.1's cash spending; β of the no-cost U.S. sweep imposed, as in
G.1; ω alone calibrated). `runOECD26.py`: anchor (the U.S., ω and λ), layer 1 (the anchor's ω, λ), layer 2 (own ω),
turnout cps/cses; rows reused only under an equal inputs hash, layers tied to the anchor's (#13). Self-check: at
the 2026-10-03 inputs the code path gives λ = 8.643207 (1e-10) and G.1's UK and France rows (1e-14); the tax at
θ ≡ 1 is `notes/theory_closedForm.md` (1.4) for all 29 (1e-10, τ = 0 corners included). `test_oecd26.py`,
`test_oecd26Anchor.py`; builders in `python/paper/{tables,figures}OECD26.py`. No results: runs in phase 2.

## 2026-10-24 — C3, phase 2: the cross-country test run (branch `review-2026-10`)

`runOECD26.py` at C1's pension-only U.S. calibration (β 0.655483), fine grids, cps and cses, the 29, one process
(`logs/C3/runOECD26.log`, 18 min) -> `results/oecd26/`: anchor λ 11.218 (cps) and 13.575 (cses); every row one
equilibrium, no fallback; eq (1.4) at θ ≡ 1 to 2.6e-11. Stage (ii) runs it (`runShocksUS.py` entry `oecd26`, always:
the rows' keys decide). `datasets.oecd26Anchor` refuses an anchor at another U.S. β or on the coarse grid;
`test_oecd26.py` P checks `results/oecd26/` against today's β and inputs and skips while the files are partial (a
run writes them row by row). Built `OECD26_Layer1`, `OECD26_Slopes`, `OECD26_Omega`. Numbers: `notes/ledger_C3.md`.

## 2026-10-24 — C5 of the review response: the smaller U.S. numbers (branch `review-2026-10`)

`c5Numbers.py` (no model code changed; self-check reproduces τ_2020, the θ = 1 tax and θ_2020 at λ = 11.564 bitwise)
-> `results/numerical/C5_*.csv`, numbers and paper lines in `notes/ledger_C5.md`. C.1's critical turnout ratio
11.5 / 3.4 / 1.84 at ρ = 0.5 / 1 / 2 against 1.61; the ranking at every ρ of the sweep (U.S. counterfactuals at
ρ 0.6–1.9 by `runShocksUS.py --out`); #7, #22 (λ ≈ εΠ/R: 52–209× at ρ = 1), index units; #5's split through the
Π-inclusive slot at a fixed π (log, and exact 2-D CRRA at ρ = 0.5, 2, ~1 h each): the cost's linearity in τ is
Beveridgean at every ρ, 83% of the ρ = 0.5 response, not all of it. Found: `LeadedLOG`'s 41-node table of the
anticipated tax function biases θ_2020 by −0.005 (0.7278 vs 0.7324 converged; finding #19); responses move ≤ 0.0025.

## 2026-10-24 — C4 of the review response (A6): horizon, terminal condition, FOC residuals
New `runHorizon.py` (not wired). Self-checks: the 2200 rows give the sweep's τ_2020 and `escPath{,CRRA}.csv`'s θ_2020,
τ_2020 (≤ 3.6e-12). From T = 2200 to 2140, 2290 or the steady-state terminal condition (40 periods appended, policy
stationary at 2200 to 1e-15): τ_2020 ≤ 0.0012 p.p., chosen θ_2020 ≤ 6e-5 (exact 2-D, ρ = 0.5, 2); LOG rows identical
at every date to 2110. Residuals |τ_FOC − τ̂| off the grid, as solved: ≤ 3.2e-4 p.p. on the path at `ns` = 150;
at 50 the path residual (6.9e-4 in τ) exceeds the jumps a scan over ω finds (2.3e-4). Against converged τ-derivatives
the path residual is 0.17 / 0.37 p.p. (ρ = 0.5 / 2): `CRRA.focParts_t` smooths along τ with s = 1e-4 (#7; open, model
code); at the calibrated parameters the θ 1 → 0 tax gap moves 9.34 → 8.96 and 2.12 → 1.99 p.p.; recalibrating under
converged derivatives stalls (residual 2e-3). Numbers `notes/ledger_C4.md`, logs `logs/C4/`.
