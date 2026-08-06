# Research log — gridsearch

Package-specific session log. For repo-wide/structural decisions, see the root `RESEARCH_LOG.md`.

## 2026-08-04
- Added `robustRoot.py` (the "Robust root finding with bounds" transform, `eq:root`): `boundedResidual(f,
  l, u, a0, a1)` wraps an FOC function into an unconstrained residual safe for a gradient-based root-finder
  to search over all of `ℝ`. Model-agnostic by design (plain callable in/out, no `db`/`base.py` dependency).
  Verified against the doc's own worked examples (interior root, both boundary/corner cases).
- Now consumed by `informalAnalytical.policy.LOG.solveVectorized` — see that module's `RESEARCH_LOG.md`.

## 2026-08-05
- Added `roots1d.py` — 1D root/extremum detection on a grid, built for `alg:gridsearch` but model-agnostic.
  See README for the API. Three design decisions worth recording:
  - **Two families, one implementation.** Root detection and maximum detection differ only in the cell
    mask (`f[i]*f[i+1] < 0` vs. `f[i] > 0 > f[i+1]`), so there's one detector plus named wrappers, same
    split as `base.py`'s preference-agnostic `FOC` vs. its `_LOG` marginal utilities.
  - **Exact zeros are load-bearing, not measure-zero.** Working through the `robustRoot` algebra:
    `h = z - |z|·penalty` evaluates to `z + |z|`, *identically zero*, at `τ̃ = l - 1/a₀` whenever `z(l) < 0`.
    So a corner solution is an exact zero at an outer node, invisible to a sign-change test. This also
    explains the extra `1e-4` in `inspiration/auxFunctions.py`'s `defaultGrid_` — it nudges the node just
    past the root so a sign change does appear. `roots1d` handles zeros directly rather than depending on
    that offset. A first version of the sign-run rule still dropped zeros at the *first/last* grid node
    (nothing on one side to bracket them) — caught by testing, fixed with one-sided classification.
  - **Multiplicity by maximising, not root-finding.** The trapezoid rule integrates a piecewise-linear
    function *exactly*, so `objectiveProfile` is the exact antiderivative of the same interpolant whose
    zeros `allRoots` finds. Its global maximiser therefore lies in `{l, u} ∪ {downward crossings}`, making
    the selection rule a definition rather than a heuristic — and it subsumes the corner check, since
    endpoints compete on the same footing. Verified synthetically: on a two-humped objective `firstMax`
    returns the lower hump and `selectMax` the taller; with an interior maximum present but a corner
    higher, `selectMax` correctly prefers the corner.
- Consumed by `informalAnalytical.policy.LOG.solveBackward`/`solveRobust`. Vectorized over N functions
  sharing one grid specifically so `CRRA`'s grid-of-states solve can reuse it unchanged.

## 2026-08-05 (cont'd) — ND grids, and vectorizing the crossing detection
Groundwork for `CRRA`'s terminal-period solve, which searches over `τ` at every point of a savings-state
grid. See `informalAnalytical/RESEARCH_LOG.md` for the model-side half of this session.

- Added `cartesian.py` (`CartesianGrid`). **Chose numpy over the inspiration's `pd.MultiIndex` + `unstack`
  route**: the reason the inspiration needed a MultiIndex is that it recovered the 2D shape from grids of
  unknown provenance. When the product is built here in C-order, the flat layout is fixed by construction —
  `reshape` inverts it exactly, with no sorting, no label lookups, and no dependence on `unstack`'s level
  ordering (which the inspiration's `.unstack(level=solName).values.T` quietly relies on). Labels remain
  available for reporting; the solve path is plain ndarrays.
- Vectorized the crossing detection across columns (`_matrixCrossings`) and added `selectMaxND`.
  - The rule looks sequential in one place — "pair each node with the last *nonzero* node before it", whose
    reach varies by column and position. It vectorizes with `np.maximum.accumulate` over row indices,
    carrying forward the most recent nonzero node.
  - **Measured twice, and the first attempt was wrong.** The initial version allocated ~15 full `(M,N)`
    temporaries and was *2.5x slower than the loop* at large N — the arithmetic is elementwise either way,
    but the memory traffic is not. Replacing the argsort compaction with a cumsum-scatter helped only
    marginally, which located the real cost. Fix: crossings are sparse, so do the gathers and interpolation
    only at `np.nonzero(ok)` and compact via a `lexsort` over the crossings alone. Result 4–8x in the
    intended range (`M~10²`, `N~10²`). The loop still wins past ~5·10⁶ elements; that crossover is
    documented in the docstring rather than left for someone to rediscover.
  - `_columnCrossings` retained as the **test oracle**, not deleted: the two must agree exactly, and the
    column-at-a-time form is the one that reads as a plain statement of the rule. Checked on 1200
    randomized cases (400 inputs × 3 kinds), with inputs quantized on purpose so zero runs, boundary zeros
    and all-zero columns actually occur rather than being hoped for.
- **Reviewed `inspiration/gridsearch`'s `SolveGrid` on request** and deliberately did not port most of it —
  traversal order, `ΔL`/`ΔU` refinement, NaN-filling/smoothing, `np.ix_` index maps. Reasoning recorded in
  the README: refinement and per-state warm starts exist to avoid evaluating the full grid state-by-state,
  but profiling showed a FOC evaluation is dominated by per-call db overhead and is **flat in grid size**,
  so the full vectorized grid is nearly free and there is no per-state loop left to warm-start. The
  precompute-once principle was still right — it just pointed at per-*year* model parameters
  (`base.py`'s `cacheParams()`), not at grid index maps.
- Added `interp.py` (`griddedInterp1D`) once `informalAnalytical`'s CRRA terminal solve needed policy
  functions τ(s)/h(s) evaluable off the grid: a thin `scipy.interpolate.interp1d(..., fill_value=
  'extrapolate')` wrapper, chosen over porting the inspiration's hand-rolled `CustomLinInterp`/
  `_linInterp` since scipy already does exactly that (piecewise-linear, linear extrapolation — matching
  what the inspiration itself settled on; its `PchipInterpolator` alternative sits commented out there).
  `griddedSmoothND`/`griddedGradientND` (the inspiration's `_smooth1D`/`_griddedGradient1D`/`2D`) were
  scoped to live here too, when built — no caller yet, since the terminal period is closed-form.

## 2026-08-05 (cont'd) — griddedSmooth1D/griddedGradient1D built; selectMax handles NaN
Both landed once `informalAnalytical`'s CRRA `t<T` recursion gave them real callers (numerical `dh/dτ` in
the FOC; denoising the selected `τ_t(s_{t-1})` before interpolating). Share one `UnivariateSpline` fit
(`_splineAlongAxis0`); NaN dropped per-column (real infeasible cells, not padding) rather than poisoning
the fit. Also extended `roots1d.selectMax` to accept NaN in `f`: each state now maximises over its own
feasible sub-grid (a fast path when no column has NaN, a per-column fallback otherwise) rather than
requiring full feasibility — needed since a `t<T` `(τ,s_)` cell can leave the state grid at extreme `τ`.
Tested directly in `test_roots1d.py` (node-exactness, trailing-axis handling, NaN-passthrough for the
spline functions; masked-column/fully-infeasible/no-manufactured-crossing cases for `selectMax`).

Docstring density swept down repo-wide this session (see `informalAnalytical/RESEARCH_LOG.md`) — this
package's files were already at the target density (equation refs + invariants, no narration) and needed
no changes.
