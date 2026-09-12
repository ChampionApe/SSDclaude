# Research log — US

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_US.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

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
