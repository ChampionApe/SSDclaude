""" Interpolation, smoothing and differentiation of gridded data.

Three jobs, all model-agnostic like the rest of this package:

  griddedInterp1D   -- a callable interpolant, e.g. a solved policy tau(s)/h(s) to be evaluated later at
                       an arbitrary candidate state, not only at the nodes the grid search visited.
  griddedSmooth1D   -- denoise a solved profile before interpolating it.
  griddedGradient1D -- a derivative along a grid axis, where no closed form exists.

The latter two are built on a *smoothing* spline rather than finite differences, deliberately and
following the precedent this replaces: their inputs are themselves outputs of interpolated policy
functions, so they carry small kinks that plain differencing would amplify into the derivative. The
smoothing factor is what controls that, and it is exposed rather than fixed.
"""
import numpy as np
from scipy import interpolate


def griddedInterp1D(x, y, kind = 'linear'):
    """ x: (M,) grid nodes -- sorted here defensively, since only the axis a search runs over (roots1d's
    own precondition) is guaranteed sorted, not every state axis a grid happens to carry. y: (M,) or
    (M, ...) values at those nodes; trailing axes (e.g. a per-household-type quantity) pass through
    unchanged. kind: passed to scipy.interpolate.interp1d -- 'linear' matches what this package's callers
    settled on (piecewise-linear, no curvature between nodes); pass 'quadratic'/'cubic' for a smoother
    continuation if one is ever wanted.

    Returns a callable f(xNew) -> yNew that extrapolates *linearly* past [min(x), max(x)] rather than
    raising or clamping to the boundary value. This matters concretely: a candidate state produced by an
    outer root-solve (e.g. an endogenous continuation state implied by a candidate policy) is not
    guaranteed to land inside the grid this interpolant was built from, and clamping would silently
    misrepresent the policy at exactly the states where the boundary is actually informative. """
    order = np.argsort(x)
    return interpolate.interp1d(np.asarray(x)[order], np.asarray(y)[order], kind = kind, axis = 0,
                                bounds_error = False, fill_value = 'extrapolate')


def _splineAlongAxis0(x, y, s, k, derivative):
    """ Fit a smoothing spline in x along axis 0 of y, once per trailing index, and evaluate either it or
    its derivative back at x. Shared by griddedSmooth1D/griddedGradient1D so the two differ only in that
    final choice.

    NaNs are dropped per column rather than poisoning the fit. This is not defensive padding: the callers'
    grids carry genuinely infeasible cells (a candidate state for which no economic equilibrium exists),
    and the honest treatment is to fit the surviving points and return NaN where the input was NaN --
    matching the precedent's own dropna handling. A column with too few valid points to support degree k
    is returned as all-NaN rather than silently fitted at a lower degree. """
    x = np.asarray(x, dtype = float)
    y = np.asarray(y, dtype = float)
    if y.shape[:1] != x.shape:
        raise ValueError(f"y's first axis {y.shape[:1]} must match x {x.shape}.")
    order = np.argsort(x)
    xs = x[order]
    flat = y[order].reshape(len(xs), -1)
    out = np.full(flat.shape, np.nan)
    for j in range(flat.shape[1]):
        col = flat[:, j]
        ok = ~np.isnan(col)
        if ok.sum() <= k:                       # UnivariateSpline needs > k points
            continue
        sp = interpolate.UnivariateSpline(xs[ok], col[ok], s = s, k = k)
        out[ok, j] = (sp.derivative() if derivative else sp)(xs[ok])
    inv = np.argsort(order)                     # undo the sort applied above
    return out.reshape(y.shape)[inv]


def griddedSmooth1D(x, y, s = 1e-5, k = 3):
    """ Smoothing spline through gridded (x, y), evaluated back at x. y may be (M,) or (M, ...); each
    trailing index is smoothed independently along axis 0. NaNs pass through as NaN (see
    _splineAlongAxis0). s: smoothing factor -- larger smooths harder; 0 would interpolate exactly. """
    return _splineAlongAxis0(x, y, s, k, derivative = False)


def griddedGradient1D(x, y, s = 1e-4, k = 3):
    """ dy/dx along a grid axis, as the derivative of a smoothing spline through (x, y). y may be (M,) or
    (M, ...) -- e.g. (M, ni) for a per-household-type quantity -- with each trailing index differentiated
    independently along axis 0. NaNs pass through as NaN (see _splineAlongAxis0).

    Use where no closed form exists. Where one does, prefer it: a grid derivative silently includes every
    channel that varies along the grid, which is not always what a first-order condition wants (see
    base.py's dlnc2i_dτ for a case where that distinction is load-bearing rather than cosmetic). """
    return _splineAlongAxis0(x, y, s, k, derivative = True)
