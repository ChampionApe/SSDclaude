# gridsearch

Homemade package for solving tricky numerical problems — politico-economic equilibria without closed-form
solutions — via gridsearch and root-finding. Shared across the model variants; it never sees a model's
`db`, which is what keeps it reusable.

## Files

**`robustRoot.py`** — the bounded-root reparameterization (`num_robustroot.tex`, `eq:root`). Wraps a
first-order-condition `f` that is only meaningful on `[l,u]` into an unconstrained residual a
gradient-based solver can search over all of `ℝ` without ever calling `f` outside its domain. `f` is only
evaluated at `clip(τ,l,u)`; recover the bounded policy from a solved `τ̃` the same way. Verified against
the doc's worked examples, reproducing its analytical roots `τ̃=1+1/a1`, `τ̃=-1/a0` exactly.

**`roots1d.py`** — root and extremum detection on a grid (`alg:LOG:gridsearch`). Takes a sorted grid `x`
`(M,)` and values `f` `(M,)` or `(M,N)` — N independent functions on the *same* grid — and locates where
the piecewise-linear interpolant crosses zero.

- **Two families, differing only in which crossings count.** `allRoots`/`firstRoot` (`kind='any'`) for
  genuine root problems; `allMax`/`firstMax` (downward crossings) when `f` is the derivative of an
  objective and only maxima are admissible — e.g. the political FOC, where an upward crossing is a local
  *minimum*. `allRoots` returns `(Kmax, N)` NaN-padded so a ragged result stays usable downstream.
- **Exact zeros are always handled**, at any `tol`, via a sign-run rule. Not an edge case: under
  `robustRoot` a corner solution is encoded as an *identically* zero value at an outer node
  (`h = z + |z| = 0` when `z < 0`), which `f[i]*f[i+1] < 0` cannot see. `tol` defaults to `0` — a nonzero
  default would report spurious roots wherever `f` grazes zero without crossing.
- **Multiplicity.** `objectiveProfile` is the cumulative trapezoid, which is the integral of the *same*
  piecewise-linear interpolant used to locate crossings — exactly, not approximately. `selectMax` then
  maximises over `{x[0], x[-1]} ∪ {downward crossings}`, so endpoints compete with interior maxima on the
  same footing, and returns `nMax` and `atBound`. **Pass the interior grid only**: outside `[l,u]` the
  penalised residual is an artificial construction, not `dV/dτ`, so integrating it is meaningless.
- **Vectorized across columns**, including the apparently sequential part of the rule ("pair each node with
  the last *nonzero* node before it"), which goes through `np.maximum.accumulate` on row indices. 4–8×
  faster than looping in the intended range (`M ~ 10²`, `N ~ 10²`); the loop wins again past ~5·10⁶
  elements, where cache locality beats fewer Python calls. `_columnCrossings` is retained as the readable
  statement of the rule and as the **test oracle** — the two are checked for exact agreement on 1200
  randomized cases.
- **Ragged columns are grouped by feasibility pattern, not looped over.** Columns sharing a NaN pattern
  share the sub-grid, so `np.unique(..., axis=1)` groups them and one vectorized call serves each group.
  Patterns are far from all-distinct in practice: measured in `InformalSavings`' CRRA recursion, **1–2
  distinct patterns across 900 columns** per period — all ragged, so the all-feasible fast path never
  fired and the loop ran 900 times where 1–2 calls suffice.

**`cartesian.py`** — `CartesianGrid`, the product of named 1-D grids and the flat↔ND mapping, so a grid
search evaluates the model's equations **once** on flat vectors covering every (choice, state) combination
and then looks along the choice axis alone. Numpy only: built in C-order, the flat layout is fixed by
construction, so `reshape` inverts it exactly — no sorting, no label lookups, no dependence on a
MultiIndex `unstack`'s level ordering. Nothing requires the choice axis to be first.

**`interp.py`** — four jobs on gridded data. `griddedInterp1D`/`griddedInterp2D` give a callable
interpolant over one or two states; both **extrapolate rather than clamp**, since a candidate state from
an outer root-solve need not land inside the grid, and the 2-D one evaluates **elementwise on paired
coordinates** rather than on their outer product. `griddedSmooth1D`/`griddedGradient1D` are a
smoothing-spline denoise pass and a derivative along a grid axis, sharing one fit; NaN passes through per
column rather than poisoning it.

- **`knots` decides whether the result is continuous in the data.** `None` keeps `UnivariateSpline(s=s)`,
  which lets FITPACK choose the knot *count* from the data — an integer that flips as the data moves, so
  the fitted profile jumps. An int `m` pins interior knots at every `m`-th valid node
  (`LSQUnivariateSpline`), making the fit a **linear map** of `y`, hence continuous, and ~2.4× faster.
  Pass an int wherever the output is differentiated with respect to a model parameter or feeds a root
  problem in one: the adaptive branch's knot flips read as genuine discontinuities there, and cost
  `InformalSavings` an uncalibratable parameter value until it was found
  (`notes/informalSavings_resolvedIssues.md`, `crossCuttingFindings.md` #5). Default stays `None` so
  existing results reproduce bitwise.
- **`kind` is load-bearing, not cosmetic.** `'linear'` is the historical default and the only kind with no
  NaN handling to do. `'cubic'`/`'pchip'` remove the piecewise-linear kinks, which is what made
  `InformalSavings`' CRRA *calibration* solvable away from `ρ=1` at all. Prefer `'pchip'` on principle
  (monotone, `C¹`, cannot overshoot a policy flat at a bound, where `'cubic'` returns `[-0.088, 3.105]` on
  data spanning `[0,3]`) — but **`RegularGridInterpolator` rebuilds its pchip splines on every call**,
  844 ms per 3600-point evaluation against 0.59 ms for `'linear'` and 1.02 ms for `'cubic'`. In 2-D that
  1400× penalty rules it out until someone writes a precomputed bicubic-Hermite evaluator; in 1-D it is
  cheap.
- **NaN survives the non-linear kinds.** Invalid nodes are filled from their nearest valid neighbour for
  the fit and masked back to NaN on evaluation, reproducing `'linear'`'s NaN pattern off the nodes. **Do
  not "simplify" the mask away** — the fill is scaffolding for the fit, and without the mask an infeasible
  region returns a plausible-looking number instead of the non-finite value the caller's containment check
  is watching for. `RegularGridInterpolator` also builds spline methods lazily *per axis at call time*, so
  a non-finite evaluation *coordinate* makes axis 0 return NaN and axis 1 then raise; both interpolants
  guard their coordinates. One inherited quirk is stated rather than reproduced: a point exactly on a node
  is assigned to the left-hand interval, so `'linear'` returns NaN at a *valid* node bordering an invalid
  cell where the masked kinds return the node's own value.
- **Two traps that only show up once these feed a root-finder.** `griddedGradient1D`'s `s` is an
  **absolute** sum-of-squared-residuals bound, so one default cannot serve profiles of different
  magnitude — normalise per column before fitting; and where the underlying function has a known singular
  factor, differentiate in the coordinate that makes it affine (`ln(1-τ)` there, worth ~13 orders of
  magnitude). Second, a root located against interpolant output inherits **kinks at the interpolant's own
  nodes**, so a candidate grid that straddles them is worse than a coarser one that aligns with them —
  refine only in whole multiples, or not at all.

**`continuation.py`** — `marchGrid(grid, solve, …)`: solve an expensive, ill-conditioned problem at every
value of a parameter grid, using the solves already done to start the next. Three properties the callers
depend on, all asserted in `test_continuation.py`:

- **Anchored and bidirectional.** `anchor` names the value solved first; the grid is walked outward from
  it in both directions, each carrying its own history. Not a convenience — a problem well-posed at only
  one interior point (`ρ=1`, where a cheaper solver applies) has nowhere else to start.
- **Extrapolation in the parameter value, not the grid index**, through the last `degree+1` solves,
  componentwise, with nodes centred on the target so the Vandermonde stays conditioned. Index spacing
  stops being meaningful the first time step-halving inserts an off-grid value. Start from an
  **unbounded** coordinate wherever the caller has one: extrapolating a constrained parameter in levels
  can step across its bound, giving a start that is invalid rather than merely poor.
- **A retry ladder, then step-halving.** On failure: the un-extrapolated previous point first
  (extrapolating across a kink overshoots, and the previous point is closer *and* cheaper than halving),
  then an intermediate value inserted between the last success and the target, solved and *kept* so the
  retry extrapolates from closer in. Failures are recorded, not raised — a sweep long enough to need this
  is too long to discard over one bad value — and `onPoint` fires per attempt so the caller can persist as
  it goes.

**`testing.py`** — the shared PASS/FAIL harness every `test_*.py` in the repo imports (`check`/`report`,
plus a UTF-8 reconfigure of stdout/stderr on import: the model tests print Greek, and Windows defaults a
redirected stream to the ANSI codepage, which used to turn a passing suite into a `UnicodeEncodeError`).
It lives here because `gridsearch` is the only importable package — the model folders are not packages —
and is not part of the numerical API.

## Tests

`test_roots1d.py` covers `roots1d` and `cartesian` — including the vectorized-vs-oracle sweep and
`robustRoot`'s corner encoding end to end. `test_interp.py` owns **all** of `interp`, concentrated on the
NaN semantics the non-linear kinds had to preserve. `test_continuation.py` runs against deliberately
*fake* solves, so its checks are about warm-start quality and failure recovery, which a real solve would
hide behind its own convergence. Counts are printed by `report()` rather than maintained here.

## Status

All five modules implemented and tested, and consumed end to end by all three model variants —
`informalAnalytical.policy`, `InformalSavings.policy`'s `LOG` and `CRRA` (terminal period and the `t<T`
recursion over one and two endogenous states), `US.policy` and `US.policyESC`, and the `calibrateGrid`
marches. `griddedInterp2D` is the only addition the two-state case needed; everything else transferred
unchanged, which is the evidence that the interfaces are at the right level of generality.

`continuation.py` is the one module here that is not about a single grid search but about *sequencing*
many of them. It lives in this package because it never touches a `db`, and because the three model
variants would otherwise each grow their own copy.

## Deliberately not built

A `SolveGrid`-style class that precomputes index maps and avoids evaluating the full grid — the design the
prior implementation used (at `c958031^:python/InformalSavings/inspiration/`). Most of it addresses a cost
this design removes:

- **Traversal order and per-state warm starts** exist because that code solved state-by-state in a Python
  loop. Evaluating the whole Cartesian grid in one vectorized pass removes the loop, so there is nothing
  to warm-start.
- **Window refinement** exists to avoid evaluating the full grid, but a FOC evaluation's cost is dominated
  by per-call db overhead and is **flat in grid size** (`M=101` and `M=501` both ~1.8 ms). Refining
  optimises a non-problem here.
- **Index maps for `np.ix_` subsetting** — `reshape` on a self-built C-order product is free.

What the precompute-once principle *did* justify is a cache of per-**year** db parameters
(`base.py`'s `cacheParams()`). That is the repeated cost, and it is a model concern rather than a grid one.
