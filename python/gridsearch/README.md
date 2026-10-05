# gridsearch

Homemade package for solving politico-economic equilibria without closed-form solutions via grid search
and root-finding. Shared across the model variants; it never sees a model's `db`. Installed editable from
`python/pyproject.toml` (`pyenv.md`).

## Files

**`robustRoot.py`**: the bounded-root reparameterisation (`num_robustroot.tex`, `eq:root`). Wraps an FOC
`f` meaningful only on `[l,u]` into an unconstrained residual; `f` is only evaluated at `clip(τ,l,u)`.

**`roots1d.py`**: root and extremum detection on a grid (`alg:LOG:gridsearch`), for `f` of shape `(M,)`
or `(M,N)` on one sorted grid.
- `allRoots`/`firstRoot` (`kind='any'`) for root problems; `allMax`/`firstMax` (downward crossings) when
  `f` is the derivative of an objective. `allRoots` returns `(Kmax, N)` NaN-padded.
- Exact zeros are handled at any `tol` via a sign-run rule; a `robustRoot` corner is an identically zero
  outer node. `tol` defaults to 0.
- `selectMaxFrozen`/`selectMaxFrozenND` is the selection rule (`num_robustroot.tex`, `eq:candidates`,
  `eq:equilibriumTest`): candidates are the feasible endpoints and every crossing of the consistent FOC;
  the caller's callback returns the objective along the grid at each candidate's frozen predetermined
  state (in the US solvers the FOC re-evaluated at frozen shares, integrated by `cumtrapzColumns`, plus
  the retirees' level at the anchor node); a candidate is an equilibrium if it maximises its own
  objective (value within `rtol`; a crossing also when its nearest node attains the maximum, or, if its
  quadratic stencil touches an infeasible node, the maximising node is within one cell; an endpoint on
  value alone); passing candidates within one cell of each other are one equilibrium, represented by the
  crossing; among equilibria the highest own objective wins. Returns `x`, `atBound`, `nMax`, `nCand`,
  `nEq`, `nEqRaw`, `nMerged`, `fallback`, `W`. `selectMax` is the
  earlier integral criterion (`objectiveProfile`), kept as the fallback where no candidate passes and
  for callers not yet wired (the informal models). `interpAlong` and `_quadAt` are its helpers. **Pass
  the interior grid only.**
- Vectorised across columns (`np.maximum.accumulate`); `_columnCrossings` is the readable rule and the
  test oracle. Ragged columns are grouped by NaN pattern (`np.unique(..., axis=1)`), 1–2 patterns per 900
  columns in practice.

**`cartesian.py`**: `CartesianGrid`, the product of named 1-D grids and the flat↔ND mapping, C-order so
`reshape` inverts it exactly.

**`interp.py`**: `griddedInterp1D`/`griddedInterp2D` (callable interpolants that **extrapolate rather than
clamp**; 2-D evaluates elementwise on paired coordinates), `griddedSmooth1D`/`griddedGradient1D`
(smoothing-spline denoise and derivative sharing one fit; NaN passes through per column).
- `knots=None` lets FITPACK choose the knot count from the data, which flips as the data moves (finding
  #5); an int pins knots at every `m`-th valid node, making the fit a linear map of `y`. Pass an int
  wherever the output is differentiated or feeds a root problem. Default stays `None` so old results
  reproduce.
- `kind`: `'linear'` (historical default), `'cubic'`, `'pchip'`. The non-linear kinds are what made
  `InformalSavings`' CRRA calibration solvable away from `ρ=1`. Prefer `'pchip'` in 1-D; in 2-D
  `RegularGridInterpolator` rebuilds it per call (~1400× slower), so `'cubic'` there.
- NaN survives the non-linear kinds by nearest-valid fill for the fit and a mask on evaluation. **Do not
  simplify the mask away**: an infeasible region must return non-finite. Both interpolants guard
  non-finite coordinates. A point exactly on a node is assigned to the left interval.
- `griddedGradient1D`'s `s` is an absolute bound: normalise per column. Differentiate in the coordinate
  that makes a singular factor affine (`ln(1-τ)`). A root against interpolant output inherits kinks at the
  nodes: refine candidate grids in whole multiples, or not at all.

**`continuation.py`**: `marchGrid(grid, solve, …)` solves an expensive problem at every value of a
parameter grid, warm-starting from the solves already done. Anchored and bidirectional; extrapolates in
the parameter value (not the index) through the last `degree+1` solves, from an unbounded coordinate where
the caller has one; on failure retries the un-extrapolated previous point, then inserts and keeps an
intermediate value. Failures are recorded, not raised; `onPoint` fires per attempt.

**`testing.py`**: the shared PASS/FAIL harness (`check`/`report`, plus a UTF-8 reconfigure of
stdout/stderr on import). Lives here because `gridsearch` is the only importable package.

## Tests

`test_roots1d.py` (`roots1d`, `cartesian`, the vectorised-vs-oracle sweep, `robustRoot`'s corner
encoding), `test_interp.py` (all of `interp`, centred on the NaN semantics), `test_continuation.py`
(against fake solves, so it tests warm-start quality and failure recovery).

## Status

All five modules implemented, tested, and consumed end to end by all three model variants and the
`calibrateGrid` marches. `griddedInterp2D` was the only addition the two-state case needed. All three models' solvers run `selectMaxFrozen` (the US on 2026-10-02, the informal models the same evening); the
one-cell form is restricted to candidates next to an infeasible cell and passing candidates within a cell merge
(`RESEARCH_LOG.md`, 2026-10-02 evening).

**Deliberately not built**: a `SolveGrid`-style class with traversal order, per-state warm starts, window
refinement and index maps (the prior implementation, at `c958031^:python/InformalSavings/inspiration/`).
Evaluating the whole Cartesian grid in one vectorised pass removes the loop those address, and FOC
evaluation cost is flat in grid size. What the precompute-once principle did justify is `cacheParams()`
in the models. Pre-cut long version: `archive/readmes/gridsearch_README_2026-09-11.md`.
