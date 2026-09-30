# Research log — US

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_US.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

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
