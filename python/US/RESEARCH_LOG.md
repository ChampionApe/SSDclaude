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
ns = 150. LOG λ 11.564, 'sizePiR' 20.839; the closed-form θ = 1 tax holds to 6e-13. Numbers: `archive/notes/reviewResponse_2026-10/ledger_C1.md`.

## 2026-10-23 — C3 of the review response, phase 1: the cross-country test's code (branch `review-2026-10`)

`oecd26.py`: `ModelOECD(ModelESC)` from `data/oecd29*.csv` (groups at the U.S. percentiles, θ = 2 − 1/I clipped
and re-derived at every refresh, #9; WPP ν; figure 1.1's cash spending; β of the no-cost U.S. sweep imposed, as in
G.1; ω alone calibrated). `runOECD26.py`: anchor (the U.S., ω and λ), layer 1 (the anchor's ω, λ), layer 2 (own ω),
turnout cps/cses; rows reused only under an equal inputs hash, layers tied to the anchor's (#13). Self-check: at
the 2026-10-03 inputs the code path gives λ = 8.643207 (1e-10) and G.1's UK and France rows (1e-14); the tax at
θ ≡ 1 is `archive/notes/reviewResponse_2026-10/theory_closedForm.md` (1.4) for all 29 (1e-10, τ = 0 corners included). `test_oecd26.py`,
`test_oecd26Anchor.py`; builders in `python/paper/{tables,figures}OECD26.py`. No results: runs in phase 2.

## 2026-10-24 — C3, phase 2: the cross-country test run (branch `review-2026-10`)

`runOECD26.py` at C1's pension-only U.S. calibration (β 0.655483), fine grids, cps and cses, the 29, one process
(`logs/C3/runOECD26.log`, 18 min) -> `results/oecd26/`: anchor λ 11.218 (cps) and 13.575 (cses); every row one
equilibrium, no fallback; eq (1.4) at θ ≡ 1 to 2.6e-11. Stage (ii) runs it (`runShocksUS.py` entry `oecd26`, always:
the rows' keys decide). `datasets.oecd26Anchor` refuses an anchor at another U.S. β or on the coarse grid;
`test_oecd26.py` P checks `results/oecd26/` against today's β and inputs and skips while the files are partial (a
run writes them row by row). Built `OECD26_Layer1`, `OECD26_Slopes`, `OECD26_Omega`. Numbers: `archive/notes/reviewResponse_2026-10/ledger_C3.md`.

## 2026-10-24 — C5 of the review response: the smaller U.S. numbers (branch `review-2026-10`)

`c5Numbers.py` (no model code changed; self-check reproduces τ_2020, the θ = 1 tax and θ_2020 at λ = 11.564 bitwise)
-> `results/numerical/C5_*.csv`, numbers and paper lines in `archive/notes/reviewResponse_2026-10/ledger_C5.md`. C.1's critical turnout ratio
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
converged derivatives stalls (residual 2e-3). Numbers `archive/notes/reviewResponse_2026-10/ledger_C4.md`, logs `logs/C4/`.

## 2026-10-24 — C6 of the review response: τ-derivatives and design grids (branch `review-2026-10`)
`CRRA._gradProfile` (alg:CRRA:grid step 3; `LeadedCRRA2D` inherits it): a least-squares cubic in ln(1−τ), knots
`gradKnotSpacing` = 0.04 apart in τ, for the smoothing spline in τ (s = 1e-4, adaptive). At the calibrated ρ = 0.5 / 2
(ns 150) τ_2020 and the θ 1→0 gap move ≤ 1.8e-5 / 1.3e-4 from 101 to 801 tax nodes (10.461%, 9.13 p.p.; 10.400%, 2.01;
published 10.523%, 9.34 / 2.12). C4's interpolating spline does not converge in n (10.43, 10.38, 10.62, 10.73%): each
kink where s_t(τ) crosses a node of 𝒮 enters the root, compounding back through the policies' slope in s. Calibrations
converge (1e-13), LOG bitwise. `LeadedLOG.taxes_t` solves T_{t+1} at every candidate, `_argmaxCubic` refines: θ_2020 at
λ = 11.564 0.73242 (0.72776), the continuous maximiser to 4e-7; λ 11.345. `LeadedCRRA2D`'s policies are Catmull-Rom
along θ (`Interp2D`) at 13 nodes: θ_2020 7.0e-4 / 6.4e-4 from the linear 97-node value at ρ = 0.5 / 2 (linear at 13:
0.011 / 0.013; PCHIP would flatten the anticipated tax's turning point), ~1.15× the linear cost. `runHorizon`'s
reference is the production derivative on 801 tax nodes. `test_gridConvergence.py`; logs `logs/C6/`; no csv rewritten.

## 2026-10-25 — C6 reruns: stages (i)/(ii) main and prepub, C4's and C5's runs on C6's code (branch `review-2026-10`)
Self-check first: the ρ = 1 counterfactuals reproduce `US_shocksCommonX.csv` exactly. 80 jobs under a 5-process cap
(`logs/C6runs/`, `gen_jobs.py` → `jobs.tsv`, `scheduler.ps1`), 10.9 h, all converged. λ (`size`) is 25.082 / 11.345 /
2.643 at ρ = 0.5 / 1 / 2 (was 23.691 / 11.564 / 2.459), the UK's own 16.694 / 7.740 / 3.103. θ 1→0 is 9.13 / 6.61 / 1.99 p.p.
No rank changes; the design-layer fallback and the ns = 50 jumps are gone; converged residuals are 0.003 p.p.
Crossed: 1 − f(θ*) 4.17% at ρ = 0.5 (the text: "no more than 4%"); the UK's λ is a third below the U.S. at ρ ≤ 1, 17.4% above at 2.
Steady-state horizon at ρ = 0.5: +0.027 p.p. in τ_2020. Failed: `runOECD26` layer 2, CSES, Turkey (τ → 1 at ω = 1e-6),
so `test_oecd26.py` P fails, 28/29 fast suites; `test_escCRRA` 13/13 with P_CRRA2 0.0916 → 0.0942. `archive/notes/reviewResponse_2026-10/ledger_C6.md`.

## 2026-10-25 — C6 §3: the log tax's gradient solve kept below τ = 1 (branch `review-2026-10`)
Turkey's layer-2 CSES row failed because `LOG.solveVectorized` clipped τ̃ to [0, 1]. The ω root's first step (1.2873 → 1.5302)
sent the warm-started τ̃_1960 past 1, where `initialState_solve`'s Γs bracket (1e-6) sees 1/(1 − τ) = ∞. The ValueError
bypasses `solveRobust`'s RuntimeError fallback. The LOG code is f3a15a4's; C6 only moved the cses anchor's ω seed
(1.287743 → 1.287315): f3a15a4's code fails at the new seed and C6's passes at the old. Fix: eq:root's u is the grid's,
1 − 1e-4 (`LOG._upper`, #7's cousin; `informalAnalytical/policy.py` keeps u = 1). Replayed with `--force` to scratch,
only TUR's layer-2 solves (cps, cses) passed u (`HOOK` lines in `logs/C6/oecd26_replay_R*.log`); TUR cses reran,
ω = 1.5265055645 as on 2026-10-24. The resume write rewrote the other rows at ≤ 2e-14 relative (`runESC.mergeWrite`
rereads with pandas' default parser). `test_oecd26.py` B; logs `logs/C6/tur_*.log`.

## 2026-10-26 — C7: France's ν at PaG 2021's retirement-age gap (branch `review-2026-10`)
RKB's `FRMain.xlsx` `population!D` (gap 1.5/1 years): every run that reads France's ν rerun (`logs/C7/`, 37 jobs, 2.3 h;
self-check: escCountry's France row bitwise on HEAD's ν). France ω 1.346 → 1.446 at ρ = 1 (ν_2020 0.97 → 1.04, X 6.90 →
6.64, R 2.265 → 2.432); its design under the U.S. λ 0.7954 → 0.7953, corner slope still negative and λ-free. Found: the
French leisure counterfactual is not ν-free, since France's X is pinned by hours at a ν-dependent wage: workweek +0.32 h at
ρ = 1, rates unchanged; income and voting rows unchanged (η_FR moves by one factor). One design-layer fallback appeared
(escShocksCRRA, ρ = 0.5, cost on the design, frLeisure chosen). oecd26 recomputed nothing. Tests eu 40, esc 91, counts 11,
oecd26 32, onlineAppendix 10, all pass. Numbers and the paper lines that moved: `notes/ledger_C7.md`.
