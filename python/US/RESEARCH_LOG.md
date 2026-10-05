# Research log — US

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_US.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-03 — the final run's US arm read (C6 closed)

`logs/finalRun1002/US_stage{1,2}.log`, 19:57 → 09:50; the four exact CRRA costs took 1.7–2.3 h each under `designRule
= 'root'`, `Ma = 5`. Exact λ against the earlier layer: US 18.242 → 18.267 (ρ = 0.5), 1.728 → 1.724 (ρ = 2); UK
15.089 → 15.117, 2.786 → 2.777; scan brackets unchanged. Design counts 1/1/0 (`nEqθMax`, `nBrθMax`, `nFallbackθ`) at
every chosen row of the five CRRA esc files; tax counts nEq = 1, no fallback wherever counted (−1 on the calibration
grids, the EE-only files and pinned rows). Designs moved ≤ 1.3e-3 (French voting, ρ = 2; ≤ 4e-4 at ρ = 0.5; UK
≤ 3e-4), taxes ≤ 7e-5, workweek ≤ 1.2e-3 h, design path ≤ 6e-4, stationary misplacement 0.042/0.059 and the placebo
unchanged at the printed precision; exact-vs-path gaps 0.031 (ρ = 0.5) and 0.061/0.090 (ρ = 2). LOG rows within 1e-11
(#1). `escPermanentCRRA.csv` aligns on no key after its label change (read by no output). `num_esc.tex` checks list
filled (items 8–11, 15, 17, 18); README status updated; `compareResults.py` listed in `python/paper/README.md`.

## 2026-10-02 (evening) — the equilibrium test's cell clause, and two edge cases of the frozen objective

`roots1d.selectMaxFrozen` (gridsearch log, same date): the one-cell form of eq:equilibriumTest now applies only to a
crossing whose stencil touches an infeasible cell, a crossing also passes when its nearest node attains its own
objective's maximum, and passing candidates within a cell merge into one equilibrium (`nEqRaw`, `nMerged`). Found on
the Argentine instances (TODO C7); the US checks are unchanged. `CRRA.objectiveFrozen`: hours read at the node for a
candidate sitting on one (an upper feasible end next to an infeasible cell no longer drops out), and `ln c` as the
retirees' level at ρ = 1 (the terminal period now selects instead of falling back; τ bitwise). `test_frozenSelection.py`
33 checks. The final run of both arms restarted after it (`logs/finalRun1002/`).

## 2026-10-02 (production) — the root layer is LeadedCRRA2D's design layer (C6)

`designRule = 'root'` (alg esc:crra2D, `_chooseRoot`) is the default; `'legacy'` (`_chooseLegacy`) stays for comparisons and pinned periods. `aOf`, `sharesFrom`, `frozenTaxPass` and helpers moved to `policyESC` (module level); `LeadedCRRA2DRoot` removed, the FOC layer stays in `policyESCpilot`.
Cost: `Ma = 5`, a bracketed secant (`_closeSecant`, Illinois + bisection safeguard; `aClose = 'bisection'` kept for T9), the cell-local crossing `_cellCrossing`. One period ρ=2 baseline ns=150 nCand=41: 458 → 126 frozen passes, 0.477 → 0.400 s per pass, root/legacy tChoose 5.46 → 1.06; θ' equals the pilot's to 1.4e-12 (bitwise in one process at Ma 9, bisection). `logs/designChoiceProduction/`.
Counts: `LeadedCRRA2D.multiplicity` (tax + design, `policy.DESIGN_NAMES`, -1 = not counted) from `solvePolicies`/`solveLeaded2D`; `runESCcrra.py --designRule/--Ma`, its rows carry both and six counts (`solverColumns`); the other drivers the tax counts (`policy.multiplicityColumns`); `config.US['esc']` designRule/Ma forwarded by both paper stages. `test_designChoicePilot.py` T8–T11 (22 checks); `test_frozenSelection.py` §5 now runs `'legacy'`.
M7/M8 (ρ=2 French voting, ns=50, `pilotDesignChoice.py --item M78`): resolveAt instead of the grid reading moves θ' by 2.6e-6 at (s0, θ*) (6.5e-3 at worst over states); nθ2D 21 vs 13 by 6.3e-4. Nothing in `results/` re-run.

## 2026-10-02 (pilot) — the two frozen-state design layers for the CRRA leaded choice, measured (C6)

`LeadedCRRA2D.solveBackward_t2D` is now `_periodCore` + `_choose` + `_handBack` (the unsplit period dict bitwise in one process; `tCore`/`tChoose` added). `policyESCpilot.py`: `LeadedCRRA2DRoot` (alg esc:crra2D, bisection of eq:esc:aResidual) and `LeadedCRRA2DFOC` (alg esc:crra2Dfoc, `selectMaxFrozen` on z^θ) override `_choose` only, sharing `frozenTaxPass`, `aOf`/`sharesFrom` (eq:esc:aDef, common βi asserted), `resolveAt`, `deviationCheck`; `test_designChoicePilot.py`, 13 checks. Measurements: `pilotDesignChoice.py`, `logs/pilotDesignChoice/pilotDesignChoice.csv`.
Root: one closed bracket and no fallback at every state of every run, deviation gain ≤ 0. Design in force at t0 0.7385/0.3366/0.7334 (ρ=2 baseline, ρ=2 French voting, ρ=0.5) against the earlier layer's 0.7383/0.3347/0.7364, and equal to it to 2e-6 at ρ=1.05. 5–9× the earlier layer's choice cost (23 min per recursion at ns=50 under load).
FOC: 0.8–1.5× the cost, and the least sensitive to the candidate grid (0.002 between 41 and 81 against 0.006 for root). But its fixed-knot θ' spline misses the young's slope by 18–23% (M4), its deviation gains reach 1.6e-5 relative, and its t0 design is off root by up to 0.023 (0.7152 at ρ=2). Not wired into any driver; nothing in `results/` re-run.

## 2026-10-02 (later) — tax candidates tested and ranked at frozen savings shares (C7)

RKB's point on `num_robustroot.tex`: the integral of the consistent z_t along the tax grid moves the shares with
it, so it ranked candidates at different predetermined states and said nothing about multiplicity. Now every
candidate (both corners, every crossing) is tested and ranked on z_t re-evaluated at its own frozen shares and
integrated (`roots1d.selectMaxFrozen`; `LOG.objectiveFrozen`, `CRRA.objectiveFrozen`, with `focParts_t`/
`zAtShares` splitting the splines from the retirees' term so `focGrid_t` is bitwise what it was); the four US
solvers report `nCand`/`nEq`/`fallback` per state and `multiplicity` in `solvePEE_*`/`solveLeaded*`;
`solveRobust(check = True)` runs the full-grid pass on every log solve (+19 ms, 1.0 s per calibration) and keeps
the gradient solution bitwise when it is the selected equilibrium. Raw CRRA utility levels are NOT the right
frozen objective (the FOC carries smoothed derivatives; 140 spurious test failures at ρ = 2 before switching to
the integrated condition). `test_frozenSelection.py` (31 checks): the frozen objective's τ-derivative equals z_t
to 1e-6 (log) and 1e-9 (CRRA T); bitwise the earlier criterion wherever one equilibrium exists; one equilibrium at
every state, no fallback, at ρ = 1, 2, 0.5, in the leaded log recursion and one 2-D ESC period. Fast registry:
23 of 23 suites pass in 309 s (`logs/fastSuites_frozenSelection_1002.log`), `test_esc.py`'s pinned numbers
included. Nothing in `results/` re-run; checklist `notes/todo_finalRun_2026-10-02.md`.

## 2026-10-02 — the CRRA design choice moves a predetermined state (found by reading, nothing run)

While section 4 of the paper was being drafted: `LeadedCRRA2D._econAt` (policyESC.py 603–605) evaluates every
candidate θ_{t+1} with s_{t-1,i}/s_{t-1} recomputed at the candidate's own τ* and h_t, through B_t(R_t) under
ρ ≠ 1, so the design comparison includes a channel the electorate does not control. The tax FOC holds the ratio
fixed correctly; LOG is immune (B = β, and the tax does not see θ_{t+1}). The path iteration and `PermanentCRRA`
(level of past savings) share the class. Size unmeasured; RKB wants a new algorithm, designed in a fresh session:
`notes/esc_crraDesignChoiceProblem.md`, TODO C6. num_esc.tex line 8 states the opposite and is fixed with it.

## 2026-09-30 — Frisch-elasticity robustness of the endogenous design (`runESCxi.py`)

New driver, LOG under 'size' and common X: per ξ the model is rebuilt with ξ in the workbook parameters (`buildUSxi` swaps it
into `testmod.pars` around `runESC.buildUS`, since η_i derive from it in the constructor), λ calibrated by `calibrateWedge`
with (β, ω, X) recalibrated at every trial, then runESC's path and acute-ageing code. θ* and Ṽ are ξ-free (asserted; gap
1.1e-16). Self-check at ξ = 0.3: λ, path and acute rows equal to the published ones bitwise. ξ = 0.2/0.3/0.4: λ = 8.736/
8.643/8.547, one sign change each, no corner; design 2050/2080/2110 0.798/0.805/0.809, 0.797/0.804/0.809, 0.796/0.804/0.809;
tax 2110 0.212/0.209/0.206; acute ageing chosen 0.825/0.825/0.826 (τ 2020 pinned 0.229/0.225/0.221, chosen 0.232/0.228/
0.224); R drift 2.0/2.9/3.7e-3 (the headline's fixed-point caveat). `results/esc/escXiRobustness.csv`, `logs/escXi.log`, 7.6 min.

## 2026-09-29 — the UK as ESC host (`--host UK`)

`runESC.py --stage shocks --host UK` and `runESCcrra.py --exact --host UK` run the French scenarios on the
UK at its OWN λ (LOG from `escCountry.csv`; CRRA calibrated into `escCalibrationCRRAUK.csv`), France cut at
the UK's groups; `buildEU` seeds ω and passes ModelESC options, `runESCcrra.buildHost`, `frenchData`/
`franceRow` take the grouping, rows carry `host`, UK files carry it in their names; `collectESCexperiments.py
--host UK` -> `escExperimentsUK.csv`. UK λ = 15.089, 7.264, 2.786 at ρ = 0.5, 1, 2 (US 18.242, 8.643, 1.728);
every free baseline re-elects 0.5597. Trap: at ρ = 0.5 the UK's β-imposed calibration does not converge on
the ns = 50 scan grid (7.5e-4), so that ρ scans at 150 (~35 min per trial, 5 h in all). `test_esc.py` S15.

## 2026-09-24 — the `'size'` wedge f(θ, τ) (WP2 and WP4 of `archive/notes/plan_escSizeLeak.md`)

`Base.fWedge/wedgeA/wedgeB(θ, τ, t, lag)` gain the spec `'size'`; `Vtilde(t, lag)` memoised and zero-mass
masked; `dlnfWedge_dτ`; τ passed at every call site (same-date pairs); `dlnc2i_dτ` × (1+τ∂τ ln f); `model.py`'s
`EE_report` passes τ to `bi`. `calibrateWedge` brackets per spec (`WEDGE_BRACKET`), λ in `wedgeP`. Every
`runESC.py` stage merges its csv (per-stage keys; a bool/NaN key-string defect that duplicated rows fixed);
calibration rows carry `Vtilde`, `fStar`, `f0`, `τ0`. `test_esc.py` 9–14: λ = 0 bitwise the no-wedge model,
the retirees' τ-derivative against a finite difference to 2.6e-10, Ṽ invariances to 1e-16, `'scale'` p =
0.4076119851 reproduced (~235 s now). Results, common X: λ = 8.643 (LOG; Ṽ 0.436, f(θ*) 0.982, f(0) 0.762,
R drift 2.9e-3), 18.24 (ρ 0.5) and 1.728 (ρ 2) exact, one sign change per scan (a coarse-grid inner failure at
one node each, skipped as designed); the two ρ ran in parallel through `--tag` (`logs/runEscSizeCrra0924.ps1`).
S4 fired: the path iteration (λ = 20.31, 1.917) separates from the exact choice by 0.031 (French voting, ρ 0.5) and 0.063/0.091 (voting, joint, ρ 2); 81 candidates move the exact choice ≤ 0.006, and at the exact λ the path iteration picks 0.717 at baseline, so it is the method's approximation, not the grid (`archive/pilots/escSizeLeak_S4_2026-09-25/`). Stationary check under `'size'` (`results/numerical/US_ESC_stationaryApprox.csv`): the ν-frozen policy misplaces the design in force by up to 0.053 (LOG), 0.042 (ρ 0.5) and 0.059 (ρ 2), against 0.005/0.016 under `'scale'`: the design now answers to the size of the system, which the frozen ν mis-states most at 2020–2050.

## 2026-09-22 — a UK host for the French-characteristics shocks

`runShocksUS.py --host US|UK|UKUS`: the host is rebuilt from its sweep row (`hostModel`; on a ModelFR
`setUSRef` for β, then X or `rescaleX(λ)`), asserted to reproduce the sweep's own τ (not the workbook
target: under CRRA the vector-X rescaling drift of `hoursDriftTol` sits in the recorded τ). The one model
change: `shocks.ηLevel` preserves the host's Γ_h instead of resetting it to 1 -- on a calibrated vector-X
ModelFR Γ_h = λ, and the old assertion would have undone the UK's hours calibration (`test_eu.py`, 4 new
checks). `testEU.load` takes any sheet suffix and names a missing sheet; `calibrateRhoGridEU.py --country FR
--grouping UK` sweeps `FRUK` (16/16 both variants, ω identical to France's US-cut value). On the UK, France's
income distribution *raises* τ (+0.3 p.p., France the more unequal at the UK's cuts) under common X and
lowers it (−0.5) under vector X. `logs/ukusSmoke0922.log`, `frukSweep0922.log`, `ukShocks0922.log`,
`frFix0922.log`, `escCrraFrFix0922.log` (the exact CRRA leg re-run after the hours fix, ~1.5 h).

## 2026-09-12 (night) — stationary vs date-specific policy functions (prepub check)

`stationaryApprox.py`: the exact CRRA recursion against a policy function solved with ν frozen at each
date's value (40-period recursion, first period read, convergence checked over the visited states -- the
bottom of the s grid never settles, ~1e-4, and is excluded), walked along the projected path from the exact
initial state; plus the steady-state PEE tax τ*(ν_t) and one long-run function. At ρ ∈ {0.5, 0.7, 1.3,
1.5, 2}: the date-by-date stationary walk misses the exact tax by ≤ 0.17 p.p. (2020), the steady-state
comparison by ≤ 0.20 p.p., the sign flipping at ρ = 1 (exact by the decoupling); one long-run function is
6–8 p.p. off before 2050. The terminal period is 3.5–9.7 p.p. too high, the one before ≤ 0.26 p.p.
`stationaryApproxESC.py`: the same for the leaded design under the wedge, LOG (`ESC.solveBackward` on the
frozen copy) and exact 2-D CRRA (`ESCC2.solvePolicies` on the baseline's s grid, ~5 min each): the design
in force is misplaced by ≤ 0.005 (LOG) and ≤ 0.016 (CRRA, 1990 at ρ = 2, where the frozen recursion itself
only settles to 0.015 -- the flat objective); the tax by ≤ 0.21 p.p. `results/numerical/US_*.csv`,
`logs/*Stationary*0912.log`; wired as prepub entries of `python/paper/runShocksUS.py`.

## 2026-09-12 — one hours unit across countries (C4)

`addEigenVectors` now scales both eigenvectors to γ·y = 1, so the vector-X hours unit
μ = ∑γ_i y^x_i is 1 everywhere instead of scipy's unit-norm value (US 0.5593, FR 0.5590, UK 0.5770) --
the same normalisation the Argentina models impose. It is the eq (hoursUnit) rescaling, so only h̄ and
h_i move: the re-swept vector-X grids reproduce β, ω, R, τ, sr and h to ≤1.6e-13 at every ρ, h̄ scales by
1/μ_US (ratio 1.788), and the μ_c/μ_US that ModelFR's Γ_h rescaling used to hide in X̄_c/X̄_US now sits in
λ where it belongs (UK λ 0.8367 → 0.8632 at ρ = 1, the 3% TODO C4 named; FR 0.8934 → 0.8930). Docs:
`writing/US/model_calibration.tex` (both normalisations now stated, and the h̄-comparability remark).
`test_ee.py`'s h̄ ≠ h check was degenerate under μ = 1 and became the two aggregation identities plus
h̄/h = μ, with the commonX instance (μ = 0.963) as the non-normalised control. Sweeps:
`logs/usVectorX0912.log`, ~20 min; the ESC leg runs under common X and was not touched.

## 2026-09-11 — Exact CRRA ESC solver published; timing checks as tests and stages

`runESCcrra.py --exact` runs the wedge calibration, design path and counterfactuals through `solveLeaded2D`
(`ModelESC.leadedDesignAtT0_2D`, `calibrateWedge` preferences `CRRA2D`, scan at `--nsScan` 50 then refine
at `--ns` 150, 41 candidates); rows carry `method` = exact|path, in every merge key. Exact p: 0.935 (ρ 0.5),
0.0855 (ρ 2). The path iteration stays as the cross-check only. STOP 3 of `notes/plan_2026-09-11.md`
(frVoting θ 0.285 path vs 0.273 exact at ρ = 2) was the candidate grid on a flat objective (W differs by
1e-5 over ±0.01 in θ; 13/21/41/81 candidates give 0.285/0.273/0.263/0.262), not state dependence (slope
−0.001). New: `ModelESC.sequentialFOC` (costless seqFOC on a solved path; negative on [0,1] at every dated
period, ρ = 0.5, 1, 2), `--stage sequential`, `test_escTiming.py` (slow: TODO R3's permanent reference
numbers; "p = 0.375" is the calibrated 0.375032). `PermanentCRRA` ran for the first time: corner θ = 0 for
ρ ≤ 1.3, θ = 1 for ρ ≥ 1.4 (`escPermanentCRRA.csv`). `test_esc.py` now ~80–100 s (sections 10, 13, 14).
