# Research log — informalAnalytical

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-07 (evening) — the vectorized LOG solve restarts on a near miss; section 5's footnote pinned (TODO C9)

Since C8's inputs (γ₀ = 0.4706, first-quartile ε) the quick-test model's `solveVectorized` stopped at max|z| = 1.5e-8
against the 1e-8 gate: scipy's `hybr` stops on a step tolerance (`xtol`), not on the residual, so `test_cacheParams.py`
and `test_crraBackward.py`, which call the vectorized solver directly, failed; `solveRobust` had recovered through its
grid fallback. `LOG.solveVectorized` now restarts `optimize.root` once from its own solution when the gate is missed
(9e-16 here, τ moving by 1.2e-9); a solve that meets the gate is never restarted, so every passing solve is bitwise
unchanged. `test_calibration.py` §8 pins the paper's section 5 footnote: on the calibrated ρ = 1 model the reform (ε
0.210 → 0.547 from 2010, rule 'match', κ rebuilt) raises the 2010 tax from 10.92% to 16.38%. `getEps`'s docstring
cites `app:EPH` (also in InformalSavings). `US/policy.py`'s `solveVectorized` has the same default and passes; unchanged.

## 2026-11-04 — code review P4: dead code only
The adjPar family's `t` (with `adjDf_ti`'s broken `k.loc` branch), `Base.power_p`, `getXi`, `aux_p`, `LOG.style` and
`LOG.kwargs` removed, and unused imports (`Lead`, `interpolate`, test.py's `scipy`/`SimpleSys`, test_crraBackward's
`roots1d`); `ω2i`'s docstring. `LOG.x0` stays: it is `solveVectorized`'s warm start. Pinned in `test_ee.py`.

## 2026-11-04 — κ without the (1+γ₀) factor
`Base.κ` = p_t + ε_{t+1}γ_{t,0}p_{t,0}: n_t and ν_t count formal young, as in InformalSavings (derivation in its log of today).
`test_ee.py`: the PAYG check is now per formal young, and a last section moves γ₀ over t (the budget misses by 7.0e-4 on the
old κ). The workbook's γ₀ is constant, so the factor was exactly 1 and no output moves. `objectiveFrozen` (LOG and CRRA) keeps
the per-candidate anchor that InformalSavings replaced (README, open items).

## 2026-11-04 — `objectiveFrozen`'s common anchor (port of InformalSavings' fix of today)
`LOG/CRRA.objectiveFrozen` take the consistent z and anchor every candidate at its column's first finite node of z
(`policy._firstFinite`, `_anchoredAt`); a candidate not finite there is NaN in that column. Toy: `test_cacheParams.py` §8 (4 FAIL on the old code).
Old vs new in one process (`logs/iaFrozen_oldNew.log`): solves at ρ = 1, 1.5, 2, 0.5 bitwise equal, all 31 LOG and 34 CRRA calls
bitwise, no column masked. Fresh models are not bitwise reproducible in one process (`addEigenVectors`' ARPACK start), so compare deep copies.

## 2026-11-04 — addEigenVectors in closed form
`model.addEigenVectors`: y = z/(γ·z) (z·γᵀ has rank one) replaces ARPACK `eigs`, whose random start made two builds of one model
differ by ~1e-16; on the ARG workbook instance ARPACK and the closed form agree to 3.3e-16 (as python/US since P1).
