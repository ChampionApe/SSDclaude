# Research log — gridsearch

Package-specific session log. For repo-wide/structural decisions, see the root `RESEARCH_LOG.md`.

## 2026-08-04 — `robustRoot.py`
`boundedResidual(f, l, u, a0, a1)` wraps an FOC function into an unconstrained residual safe for a
gradient-based root-finder to search over all of `ℝ`. Model-agnostic by design (plain callable in/out, no
`db`/`base.py` dependency). Verified against the doc's own worked examples — interior root and both
boundary/corner cases. First consumed by `informalAnalytical.policy.LOG.solveVectorized`.

## 2026-08-05 — `roots1d.py`
1-D root/extremum detection on a grid, model-agnostic. Three design decisions worth recording:
- **Two families, one implementation.** Root and maximum detection differ only in the cell mask
  (`f[i]*f[i+1] < 0` vs. `f[i] > 0 > f[i+1]`), so there is one detector plus named wrappers.
- **Exact zeros are load-bearing, not measure-zero.** Under `robustRoot`, `h = z + |z|` is *identically
  zero* at `τ̃ = l - 1/a₀` whenever `z(l) < 0` — a corner solution is an exact zero at an outer node,
  invisible to a sign-change test. (This also explains the extra `1e-4` in `inspiration/auxFunctions.py`'s
  `defaultGrid_`, which nudges the node past the root so a sign change appears; `roots1d` handles zeros
  directly instead.) A first version of the sign-run rule still dropped zeros at the **first/last** node —
  nothing on one side to bracket them — caught by testing, fixed with one-sided classification.
- **Multiplicity by maximising, not root-finding.** The trapezoid rule integrates a piecewise-linear
  function *exactly*, so `objectiveProfile` is the exact antiderivative of the same interpolant whose zeros
  `allRoots` finds. Its global maximiser therefore lies in `{l, u} ∪ {downward crossings}`, making the
  selection rule a definition rather than a heuristic — and subsuming the corner check, since endpoints
  compete on the same footing.

## 2026-08-05 (cont'd) — ND grids, and vectorizing the crossing detection
Groundwork for `CRRA`'s terminal-period solve, which searches over `τ` at every point of a savings grid.

- **`cartesian.py` (`CartesianGrid`): numpy, not the inspiration's `pd.MultiIndex` + `unstack`.** The
  inspiration needed a MultiIndex because it recovered the 2-D shape from grids of unknown provenance. Built
  here in C-order, the flat layout is fixed by construction — `reshape` inverts it exactly, with no sorting,
  no label lookups, and no dependence on `unstack`'s level ordering (which the inspiration's
  `.unstack(level=solName).values.T` quietly relies on).
- **Vectorizing `_matrixCrossings` was measured twice, and the first attempt was wrong.** The rule looks
  sequential in one place — "pair each node with the last *nonzero* node before it" — which vectorizes with
  `np.maximum.accumulate` over row indices. But the first version allocated ~15 full `(M,N)` temporaries and
  was **2.5× slower than the loop** at large N: the arithmetic is elementwise either way, the memory traffic
  is not. Fix: crossings are sparse, so gather and interpolate only at `np.nonzero(ok)` and compact via a
  `lexsort` over the crossings alone. 4–8× in the intended range (`M~10²`, `N~10²`); the loop wins again
  past ~5·10⁶ elements, a crossover documented in the docstring rather than left to be rediscovered.
- `_columnCrossings` is retained as the **test oracle**, not deleted — the two must agree exactly, and the
  column-at-a-time form is the plain statement of the rule. 1200 randomized cases, inputs quantized on
  purpose so zero runs, boundary zeros and all-zero columns actually occur rather than being hoped for.
- **`inspiration/gridsearch`'s `SolveGrid` reviewed and deliberately mostly not ported** (traversal order,
  `ΔL`/`ΔU` refinement, NaN-filling/smoothing, `np.ix_` index maps). Reasoning in the README: refinement and
  per-state warm starts exist to avoid evaluating the full grid state-by-state, but a FOC evaluation is
  dominated by per-call db overhead and is **flat in grid size**, so the full vectorized grid is nearly free
  and there is no per-state loop left to warm-start. The precompute-once principle was still right — it
  pointed at per-*year* model parameters (`base.py`'s `cacheParams()`), not at grid index maps.
- **`interp.py` (`griddedInterp1D`)**: a thin `interp1d(..., fill_value='extrapolate')` wrapper, chosen over
  porting the inspiration's hand-rolled `CustomLinInterp` since scipy already does exactly that, and matches
  what the inspiration itself settled on.

## 2026-08-05 (cont'd) — `griddedSmooth1D`/`griddedGradient1D`; `selectMax` handles NaN
Both landed once `informalAnalytical`'s CRRA `t<T` recursion gave them real callers (numerical `dh/dτ` in
the FOC; denoising the selected `τ_t(s_{t-1})` before interpolating). They share one `UnivariateSpline` fit
(`_splineAlongAxis0`); NaN is dropped per column — real infeasible cells, not padding — rather than
poisoning the fit. `roots1d.selectMax` now accepts NaN in `f`, so each state maximises over its own feasible
sub-grid, needed because a `t<T` `(τ,s_)` cell can leave the state grid at extreme `τ`.

## 2026-08-10 — `griddedInterp2D`, and two traps that only appear once an interpolant feeds a root-finder

`InformalSavings.policy`'s CRRA class needed continuation policies over *two* states, so `interp.py` gained
`griddedInterp2D` (`RegularGridInterpolator`, linear, extrapolating). One design choice worth recording: it
evaluates **elementwise on paired coordinates**, not on their outer product. The caller always has one
candidate `(s,ι)` per point — a vector of pairs, not a grid to cross — and returning the product would have
made every call site reshape around a shape it never wanted.

That was the *only* addition the two-state problem required. `robustRoot`, `roots1d`, `cartesian` and the
rest of `interp` transferred unchanged from the one-state case, which is the first real evidence that this
package's interfaces sit at the right level of generality rather than having been fitted to
`informalAnalytical`.

**Two traps, both found downstream in `InformalSavings` and both now in this package's README**, because
they are properties of these functions rather than of that model:

1. *`griddedGradient1D`'s `s` is an absolute residual bound*, so one default cannot serve profiles of
   different magnitude — callers should normalise per column before fitting. And where the differentiated
   function has a known singular factor, fit in the coordinate that makes it affine: in `InformalSavings`
   every profile carried a `ln(1-τ)` term, and differentiating in `x = ln(1-τ)` rather than `τ` was worth
   ~13 orders of magnitude. Neither is something `griddedGradient1D` can do for the caller, so both belong
   in its documentation.
2. *A root located against interpolated output inherits kinks at the interpolant's own nodes.* A candidate
   grid that straddles those breakpoints is **worse than a coarser one that aligns with them**, and
   refining without aligning makes it worse rather than better — the measured error was non-monotone in
   the node count (2.3e-7 aligned, ~2e-5 at twice the nodes unaligned, back to 3.5e-7 at eight times).
   This is a general fact about `allRoots` consuming `griddedInterp*` output, so it is worth knowing here
   and not only where it was found. Note the contrast that makes it precise: it bites only when the
   residual has little curvature of its own. Where the residual is genuinely nonlinear in the searched
   variable, that curvature dominates and ordinary refinement is what pays.

No code change to `roots1d` followed — the fix is in how callers choose grids, not in the crossing logic.

## 2026-08-11 - `selectMax` groups ragged columns by feasibility pattern

`selectMax` had a vectorized path for NaN-free columns and a per-column Python loop for the rest, on the
reasoning that each ragged column must be maximised over its own feasible sub-grid. Measured in
`InformalSavings`' CRRA recursion, that split was the worst possible one for the actual data: **all 900
state columns were ragged, so the fast path never fired once**, yet there were only **1-2 distinct NaN
patterns per period** among them. The loop was therefore running 900 times to do 1-2 columns' worth of
distinct work, and `selectMaxND` was 18% of the whole backward recursion.

The fix is to group by pattern (`np.unique(..., axis=1)`) rather than by "clean vs ragged": columns sharing
a NaN pattern share the sub-grid `x[ok]`, so one vectorized call serves the group. Per column the answer is
bitwise what a single-column call returns, because `allRoots` routes 1-column and many-column inputs
through the same `_matrixCrossings` and every step of it is column-independent -- so this is a grouping,
not an approximation. `test_roots1d.py` gained two checks against the per-column loop as oracle: one with
few distinct patterns (240 columns, 5 patterns) and one with all patterns distinct (144 of 240), the second
to confirm the grouping degenerates correctly rather than silently merging columns.

*Generalisable point, and the reason this sat unnoticed:* the original split was written around a plausible
guess about the data ("most columns will be clean"). The truth was the opposite in both directions -- none
were clean, and almost none were distinct. Feasibility in a grid search typically depends on some state
coordinates and not others, which makes near-duplicate masks the norm rather than the exception; a
per-column fallback should group before it loops.

## 2026-08-11 — `continuation.py`; `interp.py` gains interpolation kinds and NaN handling

Both additions were driven by `InformalSavings`' calibration across a grid of `rho`, but both are
model-agnostic and neither imports anything from a model module.

**`continuation.py` — `marchGrid`.** A calibration costs ~26 politico-economic solves, so a grid of them
has to be bought one warm start at a time. Three design decisions worth recording, all of which came from
the shape of the caller's problem rather than from generality for its own sake:
- **Anchored and bidirectional, not a sweep.** The caller's problem is only well-posed at one interior
  point (`rho=1`, where the cheaper LOG solver applies and no warm start is needed), so a left-to-right
  pass has nowhere to start. `anchor` names the first value; the grid is walked outward both ways, each
  direction carrying its own history. `test_continuation.py` pins that the two directions do *not* share
  a history — extrapolating leftward from points collected on the right steps the wrong way.
- **Extrapolate in the parameter value, not the grid index**, and in the caller's *unbounded* coordinate.
  The first because step-halving inserts off-grid values, after which index spacing is meaningless. The
  second because extrapolating a positivity-constrained parameter in levels can step across its bound,
  giving a starting point that is invalid rather than merely poor. Nodes are centred on the target before
  the Vandermonde solve, so the answer is the constant term and the system stays conditioned even when
  halving has put two nodes close together (there is an explicit fallback below 1e-12 separation).
- **A retry ladder before step-halving.** `extrap`, then the un-extrapolated previous point, then an
  inserted intermediate. The middle rung is not redundant: extrapolating across a kink overshoots, and the
  previous point is then both closer and much cheaper than another solve. Intermediates are kept in the
  history so the retry extrapolates from closer in.

Two bugs the tests caught, both in the first version: an empty history produced no candidate at all, so
the anchor was never attempted (fixed by passing `x0=None` through and letting `solve` use its own
default); and near-duplicate nodes, which step-halving creates by construction, hit a singular Vandermonde.

*A measured caveat on the whole idea.* Once the caller's interpolants were made `C^1` (below), the
extrapolation stopped paying for itself at the step sizes actually used: a warm-started calibration and a
cold one both converge in 12 evaluations to identical parameters at `Delta rho = 0.1`. The machinery earns
its place in robustness at larger steps and in surviving a failed point, not in speed. Worth knowing before
anyone extends it.

**`interp.py` — `kind`, and NaN.** The kind of interpolant turned out to be the binding constraint on
`InformalSavings`' CRRA calibration, not the resolution of the grids (item 13 of
`notes/informalSavings_numericalDeviations.md` has the numbers). Making non-linear kinds usable needed two
distinct fixes, and the second is the interesting one:
1. The spline methods refuse to be *constructed* over the NaN a policy surface carries at its infeasible
   nodes. Invalid nodes are filled from their nearest valid neighbour for the fit and masked back to NaN on
   evaluation. The mask is load-bearing rather than tidy: `linear` propagates NaN out of an infeasible cell
   for free, and the caller's containment check relies on a path through such a cell going non-finite
   *without* leaving the rectangle — fill without mask converts that signal into a plausible number.
2. `RegularGridInterpolator` builds spline methods **lazily, per axis, at call time**. So a non-finite
   *evaluation coordinate* — which the callers do produce — makes axis 0 return NaN and axis 1 then raise
   while constructing a spline over it. This is invisible in any test that only feeds finite coordinates,
   and it is what broke the first attempt at using pchip inside the recursion.

**`pchip` is right in principle and unusable in 2-D at present.** It is monotone and `C^1`, so unlike
`cubic` it cannot overshoot a policy flat at a bound (measured: `cubic` returns `[-0.088, 3.105]` on data
spanning `[0,3]`; `pchip` stays inside). But `RegularGridInterpolator` rebuilds its pchip splines on every
call: **844 ms per 3600-point evaluation, against 0.59 ms for `linear` and 1.02 ms for `cubic`**. That
1400x penalty took a CRRA solve from 5.7 s to over 10 min. Using it needs a precomputed bicubic-Hermite
evaluator; `cubic` is what the calibration runs on until someone writes one.

*Generalisable point.* Comparing interpolation schemes by evaluating them at a fixed point found under one
of them is not a comparison — it measures how far the other scheme's root has moved, not which is better.
The first version of this comparison did exactly that and made `cubic` look worse. Schemes have to be
compared by re-solving under each and looking at the refinement trend of each answer.

## 2026-08-19 — `griddedSmooth1D` gains fixed knots, because adaptive ones are a discontinuity

`interp.py`'s smoothing pass used `scipy.interpolate.UnivariateSpline(s=…)`. With a smoothing factor,
FITPACK's `curfit` chooses the number and placement of interior knots to meet the residual bound — and
that count is an **integer chosen from the data**, so it flips as the data moves and the fitted profile
jumps with it.

That is harmless for a one-off denoise and severe for this package's actual callers, which sit inside
solves whose output is finite-differenced with respect to a model parameter. In `InformalSavings` it put
~3.5e-6 discontinuities in a calibration residual with a 1e-6 tolerance, which made one `ρ` uncalibratable
across six attempts and was misdiagnosed for a session as a grid-resolution limit. Full chain:
`notes/informalSavings_resolvedIssues.md`; the transferable version is `notes/crossCuttingFindings.md` #5.

**The change.** `knots=None` (default) keeps the adaptive spline and reproduces every prior result bitwise.
`knots=m` fits `LSQUnivariateSpline` with interior knots at every `m`-th **valid** node. Two properties do
the work:
- The knots depend only on node positions and the validity mask, never on the values, so at a fixed mask
  the smoother is a **linear map** of its input — which is what makes its output continuous in whatever
  parameter produced the input. Asserted directly (`test_interp.py` §5, linear to 1.78e-15), not only
  through its symptom.
- Placing them on *valid* nodes satisfies Schoenberg–Whitney per column. Fixed positions in grid
  coordinates would not: a column carrying NaNs can leave a knot interval empty and `LSQUnivariateSpline`
  raises. Columns too short for interior knots fall back to a single degree-`k` least-squares fit, still
  linear in `y`.

Also 2.4× faster (1.45 ms against 3.46 ms per 45-column pass), since the knot-count iteration is gone.

**Testing this is harder than it looks, and the two failed attempts are the useful part.** A constant
offset provokes no knot flip at all — FITPACK's count is driven by the residual against the smoothing
bound, which a constant shift (and a pure rescaling) leaves unchanged; the perturbation has to change the
profile's *shape*. And over a wide parameter sweep the genuine change in the profile dominates, so
adaptive and fixed branches both read ~1.2 on a max/median jump ratio; the jump is visible only in a window
where the flip is the biggest thing happening (1.94 against 1.01). §5 therefore asserts the **mechanism** —
6 distinct knot counts and 11 flips for adaptive where fixed holds 10 knots throughout — rather than a
threshold tuned until it passed.

**Verified.** `test_interp.py` 41 checks (11 new), `test_roots1d.py` 79, `test_continuation.py` 29, plus
all five `InformalSavings` suites at the unchanged default.

`griddedGradient1D` takes `knots` too, for symmetry, but needs nothing: its callers pass `s=0`, and an
interpolating spline's knots *are* the data points, so they already do not depend on the values.
