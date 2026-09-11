# Research log — gridsearch

Package-specific session log. Current behaviour is in this folder's `README.md`; repo-wide decisions are in
the root `RESEARCH_LOG.md`.

## 2026-08-04 — `robustRoot.py`

`boundedResidual` wraps an FOC into an unconstrained residual safe to search over all of `ℝ`.
Model-agnostic by design (plain callable in/out, no `db` dependency). Verified against the doc's worked
examples — interior root and both corner cases.

## 2026-08-05 — `roots1d.py`

Three design decisions worth recording:

- **Two families, one implementation.** Root and maximum detection differ only in the cell mask, so there
  is one detector plus named wrappers.
- **Exact zeros are load-bearing, not measure-zero.** Under `robustRoot`, `h = z + |z|` is *identically*
  zero at an outer node whenever `z(l) < 0` — a corner solution is an exact zero, invisible to a sign-change
  test. A first version of the sign-run rule still dropped zeros at the **first/last** node, with nothing on
  one side to bracket them; caught by testing, fixed with one-sided classification.
- **Multiplicity by maximising, not root-finding.** The trapezoid rule integrates a piecewise-linear
  function *exactly*, so `objectiveProfile` is the exact antiderivative of the same interpolant whose zeros
  `allRoots` finds. Its global maximiser therefore lies in `{l, u} ∪ {downward crossings}`, which makes the
  selection rule a definition rather than a heuristic — and subsumes the corner check, since endpoints
  compete on the same footing.

## 2026-08-05 (cont'd) — ND grids, and vectorizing the crossing detection

**`CartesianGrid`: numpy, not a `pd.MultiIndex` + `unstack`.** A MultiIndex is needed only when the 2-D
shape has to be recovered from grids of unknown provenance. Built here in C-order, the flat layout is fixed
by construction and `reshape` inverts it exactly.

**Vectorizing `_matrixCrossings` was measured twice, and the first attempt was wrong.** The rule looks
sequential in one place, which vectorizes with `np.maximum.accumulate` over row indices — but the first
version allocated ~15 full `(M,N)` temporaries and was **2.5× slower than the loop** at large N: the
arithmetic is elementwise either way, the memory traffic is not. Fix: crossings are sparse, so gather and
interpolate only at `np.nonzero(ok)` and compact via a `lexsort` over the crossings alone. 4–8× in the
intended range; the loop wins again past ~5·10⁶ elements, a crossover documented in the docstring rather
than left to be rediscovered. `_columnCrossings` is retained as the **test oracle**, not deleted, against
1200 randomized cases whose inputs are quantized on purpose so zero runs and boundary zeros actually occur
rather than being hoped for.

**The prior implementation's `SolveGrid` was reviewed and deliberately mostly not ported** — reasoning in
the README. The precompute-once principle was still right; it pointed at per-*year* model parameters
(`base.py`'s `cacheParams()`), not at grid index maps.

## 2026-08-05 (cont'd) — smoothing and gradients; `selectMax` handles NaN

`griddedSmooth1D`/`griddedGradient1D` landed once the CRRA `t<T` recursion gave them real callers. They
share one spline fit; NaN is dropped per column — real infeasible cells, not padding — rather than
poisoning it. `selectMax` now accepts NaN so each state maximises over its own feasible sub-grid.

## 2026-08-10 — `griddedInterp2D`, and two traps that appear once an interpolant feeds a root-finder

`griddedInterp2D` evaluates **elementwise on paired coordinates**, not on their outer product: the caller
always has one candidate `(s,ι)` per point, and returning the product would make every call site reshape
around a shape it never wanted.

**That was the *only* addition the two-state problem required.** Everything else transferred unchanged from
the one-state case — the first real evidence that this package's interfaces sit at the right level of
generality rather than having been fitted to `informalAnalytical`.

**Two traps, both found downstream but both properties of these functions** (now in the README): the
smoothing bound is *absolute*, so callers must normalise per column and should differentiate in whatever
coordinate makes a known singular factor affine; and a root located against interpolated output inherits
kinks at the interpolant's own nodes, so a candidate grid that straddles them is **worse than a coarser one
that aligns with them**. The measured error was non-monotone in the node count. The contrast that makes it
precise: it bites only when the residual has little curvature of its own — where the residual is genuinely
nonlinear in the searched variable, that curvature dominates and ordinary refinement is what pays. No code
change followed; the fix is in how callers choose grids.

## 2026-08-11 — `selectMax` groups ragged columns by feasibility pattern

`selectMax` had a vectorized path for NaN-free columns and a per-column loop for the rest. Measured in
`InformalSavings`' CRRA recursion, that split was the worst possible one for the actual data: **all 900
state columns were ragged, so the fast path never fired once**, yet there were only **1–2 distinct NaN
patterns** among them. The loop ran 900 times to do 1–2 columns' worth of distinct work, and `selectMaxND`
was 18% of the whole backward recursion. Grouping by pattern is a grouping, not an approximation — per
column the answer is bitwise what a single-column call returns.

*Generalisable point, and the reason this sat unnoticed:* the original split was written around a plausible
guess about the data ("most columns will be clean"). The truth was the opposite in both directions — none
were clean, and almost none were distinct. Feasibility in a grid search typically depends on some state
coordinates and not others, which makes near-duplicate masks the norm. **A per-column fallback should group
before it loops.**

## 2026-08-11 — `continuation.py`; `interp.py` gains kinds and NaN handling

**`marchGrid`.** Three design decisions, all from the shape of the caller's problem rather than generality
for its own sake — anchored and bidirectional, extrapolation in the parameter value and in the caller's
*unbounded* coordinate, and a retry ladder before step-halving. The README states them. Two bugs the tests
caught, both in the first version: an empty history produced no candidate at all, so the anchor was never
attempted; and near-duplicate nodes, which step-halving creates by construction, hit a singular Vandermonde.

*A measured caveat on the whole idea.* Once the caller's interpolants were made `C¹`, the extrapolation
stopped paying for itself at the step sizes actually used — warm and cold both converge in 12 evaluations to
identical parameters at Δρ = 0.1. **The machinery earns its place in robustness at larger steps and in
surviving a failed point, not in speed.** Worth knowing before anyone extends it.

**`interp.py` — `kind`, and NaN.** The kind of interpolant turned out to be the binding constraint on
`InformalSavings`' CRRA calibration, not the resolution of the grids. Making non-linear kinds usable needed
two fixes, and the second is the interesting one: the spline methods refuse to be *constructed* over NaN
(so invalid nodes are filled for the fit and masked back on evaluation — the mask is load-bearing, since
the caller's containment check relies on a path through an infeasible cell going non-finite *without*
leaving the rectangle); and `RegularGridInterpolator` builds spline methods **lazily, per axis, at call
time**, so a non-finite evaluation *coordinate* makes axis 0 return NaN and axis 1 then raise. That second
one is invisible in any test that only feeds finite coordinates, and it is what broke the first attempt at
using pchip inside the recursion.

**`pchip` is right in principle and unusable in 2-D at present** — 844 ms per 3600-point evaluation against
0.59 ms for linear, because `RegularGridInterpolator` rebuilds its splines on every call. That 1400×
penalty took a CRRA solve from 5.7 s to over 10 min.

*Generalisable point.* Comparing interpolation schemes by evaluating them at a fixed point found under one
of them is not a comparison — it measures how far the other scheme's root has moved. The first version of
this comparison did exactly that and made `cubic` look worse.

## 2026-08-19 — `griddedSmooth1D` gains fixed knots, because adaptive ones are a discontinuity

FITPACK's `curfit` chooses its knot count from the data — an **integer**, so it flips as the data moves and
the fitted profile jumps with it. Harmless for a one-off denoise, severe for this package's actual callers,
which sit inside solves whose output is finite-differenced with respect to a model parameter (#5).

`knots=m` fits `LSQUnivariateSpline` with interior knots at every `m`-th **valid** node. Two properties do
the work: the knots depend only on node positions and the validity mask, never on the values, so the
smoother is a **linear map** of its input — asserted directly (linear to 1.78e-15), not only through its
symptom; and placing them on *valid* nodes satisfies Schoenberg–Whitney per column, which fixed positions in
grid coordinates would not. Also 2.4× faster, since the knot-count iteration is gone.

**Testing this is harder than it looks, and the two failed attempts are the useful part.** A constant offset
provokes no knot flip at all — FITPACK's count is driven by the residual against the smoothing bound, which
a constant shift and a pure rescaling both leave unchanged, so the perturbation has to change the profile's
*shape*. And over a wide parameter sweep the genuine change in the profile dominates, so both branches read
~1.2 on a max/median jump ratio; the jump is visible only in a window where the flip is the biggest thing
happening. The test therefore asserts the **mechanism** — 6 distinct knot counts and 11 flips for adaptive
where fixed holds 10 knots throughout — rather than a threshold tuned until it passed.

`griddedGradient1D` takes `knots` too, for symmetry, but needs nothing: its callers pass `s=0`, and an
interpolating spline's knots *are* the data points, so they already do not depend on the values.
