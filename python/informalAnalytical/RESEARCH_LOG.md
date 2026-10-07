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
