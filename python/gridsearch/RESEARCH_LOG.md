# Research log — gridsearch

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_gridsearch.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-11-04 — code review P4: the masked kinds return NaN exactly where 'linear' does
- `interp._maskedCall` now masks with the linear interpolant of 0/NaN at the nodes, so `'cubic'`/`'pchip'` are NaN on
  a valid node whose lookup interval has an invalid corner and when extrapolated from such an edge cell; the old
  linearly interpolated 0/1 mask passed both. Values near an invalid node still depend on the fill (docstrings).
- Measured first (in-memory PEE solves of the pickled instances, nothing written): no published cubic surface has a
  NaN node (the 16 common-X instances and their ε = 0 twins, baseline and reform, the (ε,θ) sweep, 'flat', the
  nι = ns = 60 refinement, appendix D's horizons), so no published evaluation reached the mask; ρ = 1 and 2 re-solve
  bitwise old vs new in one process. `test_interp.py` +4 checks (8 vs 21 and 12 vs 40 NaN on the old code).
- `griddedSmooth1D`: with `knots` an int, `s` is ignored (said so). `roots1d.firstMin` removed (no caller).
