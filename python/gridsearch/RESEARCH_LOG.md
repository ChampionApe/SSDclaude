# Research log — gridsearch

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_gridsearch.md`, indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to look. A
lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-02 (evening) — the equilibrium test's one-cell form restricted, candidates within a cell merged

`selectMaxFrozen` passed any candidate whose own objective peaked within one cell, corners included: on the Argentine
headline instances a lower corner 1.5 cells below a crossing passed, out-ranked it at its own frozen state, and the switch
broke the CRRA calibration's grid refinement (#5; InformalSavings log, 2026-10-02). Now an endpoint passes on value alone;
a crossing on value, when its nearest node attains the maximum, or, if its stencil touches an infeasible node
(`_stencilFallback`), when the maximising node is within one cell. Passing candidates within 1.001 cells are one
equilibrium represented by the crossing (`_clusterRepresentatives`; `nEqRaw`, `nMerged`). The nearest-node form is not
in the brief: without it, crossings within 0.02 cells of a node fell back (1/6/77 headline states at rho = 1/2/0.5).
Headline: nEq = 2 at 27/63/563 states -> 0, no fallback, every policy equal to 'legacy' bitwise; rho = 1 beta 0.6505784.
`test_roots1d.py` 9i-9n, 89 checks; brief `notes/brief_equilibriumTestCell_2026-10-02.md`, `logs/equilibriumTestCell/`.

## 2026-10-02 — selection among tax candidates at frozen predetermined states

`roots1d.selectMaxFrozen`/`selectMaxFrozenND` replace the integral criterion as the rule; `selectMax` stays as
the fallback. Candidates are the feasible endpoints and every crossing of the consistent FOC; each is tested and
ranked on the caller's objective at that candidate's frozen state (the test passes on value, rtol 1e-9, or when
the maximising node is within one cell, which carries candidates next to infeasible cells); `nCand`, `nEq`,
`fallback` and the own objective `W` are returned. Helpers `interpAlong`, `cumtrapzColumns`, `_quadAt`. The
callback must be consistent with the FOC: the US solvers integrate the FOC re-evaluated at frozen shares, since
raw CRRA utility levels put the maximum a few cells from the crossing (140 spurious failures at rho = 2 before
the change). `test_roots1d.py` section 9: a synthetic two-equilibrium case where the rules disagree (payoff
dominance picks the upper crossing, the integral the lower), the fixed-state identity with `selectMax`, the
fallback, a corner equilibrium, the ND wrapper; 80 checks pass. Finding #18.
