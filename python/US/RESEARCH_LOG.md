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
oecd26 32, onlineAppendix 10, all pass. Numbers and the paper lines that moved: `archive/notes/reviewResponse_2026-10/ledger_C7.md`.

## 2026-10-26 — V, documentation items (branch `review-2026-10`)
README cut to 100 lines; the pre-cut file is `archive/readmes/US_README_2026-10-26.md` (`archive/INDEX.md`). Technical note:
num_esc's permanent timing at `test_escTiming.py`'s pins (p = 0.4: 0.753 pinned, 0.870 moving, 0.7525 incumbent; p = 0.25:
0.517 / 0.523), the flat-only variant's leaded calibration and the path iteration dated as last run 2026-10-03 at θ* = 0.738
(path rows unchanged since, checked against f3a15a4~1), model_calibration's θ 0.728 against 0.735 (z = 0.507, 1.0005).
`REPLICATION.md` maps section 5's informal-retiree spending (1.053 / 1.968% of GDP: S·γ0 b0/(γ0 b0 + biAvg) from the
`universal_match` csvs) and `c5Numbers.py strategic`; `data/README.md` the Argentine ν copies. `oecd29Data.py`'s two
French notes rerun offline from `logs/oecd29_raw/`: only the `note` columns of `oecd29_{population,sources}.csv` moved.
`NUM_Residuals` already described the least-squares cubic; rebuilt identical. build 51, --site, --map (table unchanged), checkPaper OK.

## 2026-10-27 — C14: the cross-section driver's variants (branch `review-2026-10`, `notes/plan_byObject.md` C14)
`runOECD26.py --spec size|sizePiR|none --betaRule common|commonR` (each in turn; defaults read from `config.US['oecd26']`).
`betaRule` is in both keys and in `inputsKey` only when not 'common', so the on-disk rows keep theirs; a csv without the
column reads and is migrated as 'common' (`migrate`). `ModelOECD(betaRule, calibrateω)`: 'commonR' sets β to the anchor's
R2020 (layer 1; with ω to τ0 in layer 2). Under 'sizePiR' `readouts` reads the design off `solveLeaded`'s own π fixed point
and τ2020/R2020 off `solvePEE_LOG`'s, plus `ΠR2020`, `λEff2020`, `ΠRgap`; 'none' reads no design. `runESC.usWedgeRow`: the
country stage's U.S.-cost row, which raised under 'sizePiR'. GBR's rows bitwise old vs new code; fine-grid row times (GBR)
sizePiR 47.8/42.4 s, commonR 9.5/8.6 s (layers 1/2). python/paper: `config.US['oecd26']`, readers and OECD26 builders take
spec/betaRule, stage (ii)'s `oecd26` runs its `variants`, `escCountry('sizePiR')` reads escCountryCosts.csv. test_oecd26
45/45 (N, Q, Π, K, M new), paper test_oecd26 9/9, test_oecd26Anchor 5/5, fast suites 29/29. Logs `logs/C14/`.

## 2026-10-30 — O5: θ from a variant file, and the U.S. at a given θ (`notes/brief_oecd26ThetaSource.md`, both extensions)
`oecd26.countryInputs(thetaSource)`: 'index' unchanged; a variant reads `data/oecd26_theta.csv` (iso3, variant, theta, inSample), RR0 = 1/(2-θ), NoTheta -> 'noTheta' rows. `runOECD26 --theta V [--inSample]`: thetaSource in both keys (LEGACY 'index'), in inputsKey only when not 'index', the anchor's adding the variant's U.S. sweep source.
`ModelUS.getθ` returns `db['θ0']` when finite (`θOverride`); ModelESC passes it through except under 'flat', ModelOECD refuses it (keeps RR0). `--theta V` in calibrateRhoGrid (rows carry thetaSource, θ0; usBeta checks them), runESC (calib, path, shocks, country, corner; module context `THETA`; France and the UK referenced to the variant's sweep) and runShocksUS, all under `results/oecd26_theta_V/`, `results/{calibration,esc,shocks,oecd26}/` refused.
Index path against the unchanged code: 708 keys, 57 data-column rows, 58 input dicts identical; `test_oecd26` P on results/oecd26/ passes. Tests: test_oecd26Theta 22/22 (new), fast suites 30/30. Coarse smoke on a fixture (USA 0.54, GBR 0.18, CAN 0.32), `logs/thetaSource/smoke/`: U.S. β 0.651382, ω 1.17330 at θ0; ESC calib λ 6.1739, ε 11.1288; sizePiR anchor ω 1.268065, ε 10.65569, θInForce USA 0.5400, GBR 0.6737, CAN 0.5811. The real data/oecd26_theta.csv (written meanwhile) parses: variants paper, A, A2pt, B, C.

## 2026-10-30 — θ variant C against the paper at ρ = 1 (`notes/thetaC_comparison.md`)
Read-only, no solve: `logs/thetaC/compare.py` reads both sides with python/paper's readers and builders (results paths patched
to `results/oecd26_theta_C/`; data side I = 1/(2 − θ_C) on the 21), `tables.py`, `checks.py` -> `logs/thetaC/compare_out.json`.
Self-check: five builders rebuild `writing/Paper/Tables` byte for byte; figures 6.1/7.1's ρ = 1 marks exact; appendix H's 17/25.
Found: λ 11.345 -> 6.247, ε 20.445 -> 11.260 (anchor 20.01 -> 10.78); the θ = 0 workweek gap 1.7 -> 1.3 h; design responses to
ageing ×1.6; the UK chooses 0.472, below the U.S. 0.544, against its workbook 0.560 (G.1's ordering fails: the UK and France keep
workbook θ in the deep test, C has 0.181, 0.822); on the same 21 the index–growth slope steepens (L1 −0.23 -> −0.31), spending–index
flattens (39.8 -> 28.9); layer-2 side count 13/20 against a base of 12. No failed row: the p = 200/400 inner failures are top scan
nodes. Not run under C: `none`, the ε country stage, CRRA, appendix H's other variants.

## 2026-10-30 — θ variant C as the paper's measure: the drivers (`notes/brief_pipelineThetaC.md`)
`--theta V` now puts France and the UK at their FRA/GBR rows too (`oecd26.countryθ0`; `buildEU`, both `frenchData`,
`franceReference`, `testEU.model(θ0)`), with ω recalibrated at the U.S. cuts; new in `calibrateRhoGridEU` and `runESCcrra`
(calib/path/shocks), `pathHost` a variant stage, `checkCalib` checks only the rows a stage reads. `--main` (V =
`config.US['theta']`, `oecd26.thetaRoot`) writes the standard `results/` paths; `runShocksXi`, `stationaryApprox{,ESC}` take
`--theta C --main` only; `--rhos` in both sweeps; under a variant τ0 is the file's `spending` (= figure 1.1's for paper/A/A2pt/C,
asserted to 1e-9); `collectESCexperiments --theta`; the corner stage skips a ρ it cannot calibrate. Index path bitwise: FR/UK ω at
ρ = 1 (1.4457073912138274, 1.1028388390028443) and GBR τ0 identical before and after. test_oecd26Theta 32/32, fast suites 30/30. Coarse smoke
(`logs/pipelineThetaC/smoke/`): France at θ0 0.82188 ω 1.39230, own λ 13.594 (U.S. λ 6.247 makes it choose 0.645); UK at 0.181208
ω 1.04162, own λ 3.628, chooses 0.493; the corner stage's UK row at λ = 100 fails to calibrate.

## 2026-11-02 — Two more readings of the cross-section on θ variant C (`notes/brief_oecdVariants.md`, exploration)
`runOECD26.py --omegaRule mean`: layer 1 at ω̄, the mean of the run's current ok layer-2 ω's, β and ε the anchor's (`meanOmega`;
key column `omegaRule`, LEGACY 'anchor', in inputsKey only when not 'anchor'). `--turnout pooled` (`oecd26.TURNOUTS`, no default): U.S.
own CSES, `COMPULSORY` (AUS, BEL, LUX) flat, the rest `pooledProfile` over the θ source's voluntary non-U.S. sample (C: 18, (1, 1.047,
1.076)). `--usSweep` puts another outdir on the main sweep; both readings are refused in results/oecd26/. Under the defaults every row
there is reused without a solve (10 anchors, 734 rows); GBR's C/cses layer-1 row recomputes bitwise; μ against 0.9μ ≤ 1.4e-12.
Runs (`logs/oecdVariants/run.sh`, 53 min) -> `results/oecd26_explore/`: pooled anchor = C/cses anchor bitwise, ω̄ 1.30556 (R1, 20) and
1.32566 (R3, 21), every row ok, nEqMax 1. `logs/variantCompare/summary_2026-11.md`: ω̄ lifts θ 0.023 and spending 0.74 p.p., mean
spending meets the data, correlations unchanged, slopes worse; pooled = cses on the common 20, Luxembourg (θ 0.016 at the anchor's ω)
costs layer 1's Pearson on 21. test_oecd26 45/45 (X new), paper test_oecd26 12/12, fast suites 30/30.

## 2026-11-02 — C5 numbers and appendix D's U.S. checks at θ variant C (`notes/staleNumbers_2026-11-02.md`)
`c5Numbers.py`, `runHorizon.py --theta C --main` (config.US['theta'] only): θ0 0.544496 on every U.S. model (runESC.setTheta for the
ESC builders, France at FRA), every csv read kept at C (`_at`), rows tagged thetaSource/θ0, a merge drops rows of another θ (one θ per
csv; runHorizon's under a lock file, so the per-ρ/terminal design lanes share US_horizonDesign.csv). No CRRA 'sizePiR' row at C: `loss`,
`lambda` leave it NaN; `a9` reads ρ 0.5/1/2 only (C5_US_shocksRhoGridCommonX.csv is pre-C, unread). Self-check: τ_2020, θ = 1 tax at
ρ = 1 to 7e-17/4e-17, θ_2020 0.544496 at λ 6.246973; horizon self-checks 5.9e-13 (log), 2.4e-13/2.0e-11 (CRRA design). Run
`logs/c5rerun/run.sh` (7 lanes, 2 h 04 min) and `run_X2rho05.sh` (X2 at ρ = 0.5 to 4 passes: 2 left a π·τ gap 2.5e-2, θ 0.742928 ->
0.744085). Split 69/31; steps +0.200/−0.216/−0.045, +0.239/−0.188/−0.039, +0.371/−0.062/−0.007; X3 −0.278; critical ratios
12.2/3.50/1.87 (1.80 from 2080), corner condition at every date and ρ. Not rerun: `jumps` (unread). test_oecd26Theta 33/33 (N new), fast 30/30.

## 2026-11-02 — Retirement-age correction of ν and Luxembourg flat (`notes/brief_oecdRetAge.md`, exploration)
`--retAge none|exit|nra` (`oecd26.retAgeGaps`, `retAgeNu`: ν(30 − g)/(30 + ν g), its mirror (30ν − g)/(30 + g) for g < 0 as `oecd29Data.nraRule`; exit ages `data/oecd29_exitAge.csv`, PaG 2021 fig. 6.14); key column `retAge` (LEGACY 'none', inputsKey only when not 'none'), the anchor unchanged (U.S. gap 0). Turnout `csesFlat`: the cses anchor (`ANCHORTURNOUT`), rows equal to cses copied (`_twin`, `copiedFrom`).
Runs `logs/oecdRetAge/run.sh` -> `results/oecd26_retage/` (36 min; the mirror rerun 23 min): every row ok, nEqMax 1; defaults reproduce all 273 C keys on disk; FRA ν under nra 1.039. `logs/variantCompare/summary_retAge.md`: exit lowers ω̄ (1.306 -> 1.177) and makes Luxembourg harmless (L1 Pearson with LUX 0.362 -> 0.683; without 0.735 -> 0.688); layer 2 unchanged.
One-sided rule (as the brief) put NZL (ν 1.98) at τ = 0: `summary_retAge_oneSided.md`. test_oecd26 50/50 (Y new).

## 2026-11-04 — Code review, fix pass P1: the model core (`notes/codeReview_triage.md`)
CRRA permanent timing (unwired): candidates start from their own steady-state seed (s_{t0-1} was passed as the state
before position 0), the chosen design's equilibrium is `solvePEE_CRRA`'s own sol/report (was re-solved and reported at
s0 = s_0). Guards: the candidate-design loops drop only `policyESC.SOLVE_FAILURES` and count them, other errors propagate;
`s0FixedPoint`'s fallback must converge on the grid; `solveVectorized` caches x0 only after its check; `sequentialFOC`
refuses a wedge; `calibratePoint(gridSettings = None)` keeps the installed settings. `addEigenVectors` in closed form
z/(γ·z): HEAD's ARPACK gave 5 distinct yη over 6 instances in one process (2.2e-16). Removed adjPar's dead `t`, power_p,
aux_p, getXi, shocks.solveBaseline, LOG.style/kwargs; docstrings cut to spec. HEAD vs new in one process
(`logs/reviewP1/oldnew.log`): LOG, CRRA, calibration point, leaded LOG, permanent LOG, 2-D, θ = 0 shock bitwise; vector X
≤ 1.7e-15. `test_coreGuards.py` 27/27 (23 fail on HEAD); US fast 14/14, test_escTiming, test_escCRRA pass.

## 2026-11-04 — Code review follow-up: κ, sizePiR at acceptance, pinTheta, resume keys, --theta (`notes/codeReview_triage.md`)
`Base.κ` = p_t + ε_{t+1}γ_{t,0}p_t^0 (factor (1+γ_{t,0})/(1+γ_{t+1,0}) dropped): one common-X calibration at θ C, ρ = 1, and a
CRRA solve bitwise against the old κ in one process (β 0.6514784090237656). `sizePiR` at acceptance: db keeps the π solved
at (as `calibrate`), records add `ΠRpath`; old vs new on ITA's main-spec layer-1 row: ΠR2020 3.1e-14, λEff2020 4.0e-13, rest
≤ 5.8e-15; escCalibrationCosts' tail ΠR 6.5e-14 (`logs/fixPassUS_2026-11-04/piAcceptance.log`); bound on the 331 published C
rows: max ΠRgap 9.9e-11. pinTheta removed (`shockIncomeDistribution(mt0, ηFR, *, θPin)`). Sweeps resume a row only at the
run's n, ns (CRRA), smoothKnots, interpKind and, for FR/UK, new columns retAge, βUS (`staleSettings`/`resumeAt`; older rows
resumed with a notice); an index run refuses a csv with variant rows. Without --theta the drivers refuse results/
(`oecd26.indexTheta`; `--theta index`). runCalibrationUS: nothing missing or stale, 0 ESC commands; runShocksUS --list all
had. test_coreGuards 30/30 (G12-G13 new), test_oecd26Theta 56/56 (T, Z new), US fast 14/14.

## 2026-11-04 — --theta mandatory for the last four drivers (`notes/codeReview_triage.md`, "Still open")
stationaryApprox, runHorizon and c5Numbers (every command but `selfcheck`, which writes nothing) refuse results/ without --theta
(`oecd26.indexTheta`; `--theta index` the workbook's θ), collectESCexperiments refuses results/esc/ (`--theta index` keeps the rows
without thetaSource); `--theta C --main` unchanged. stationaryApprox writes through `writeRows` (merge on (ρ, t), `runESC.writeCsv`,
rows at another θ dropped): the published csv rewritten with its own ρ = 0.5 rows is byte-identical; collect's `--theta C` and
`--costs --theta C` on a copy of results/ reproduce escExperiments.csv (64 rows) and escAgeingCosts.csv (24) byte for byte.
