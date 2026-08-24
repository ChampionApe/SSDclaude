r""" interp.py -- the interpolants, with emphasis on the NaN semantics the non-linear kinds had to preserve.

Run:  .venv\Scripts\python.exe python\gridsearch\test_interp.py

The point of the file: 'linear' propagates NaN out of an infeasible cell for free, and the CRRA path
solve's `strict` check relies on that (a path through such a cell must go non-finite *without* leaving the
rectangle). 'pchip'/'cubic' cannot be constructed over NaN at all, so they fill and mask instead -- and the
masked result has to reproduce linear's NaN pattern exactly, or an infeasible region starts returning
plausible-looking policy.
"""
import numpy as np
from gridsearch import interp
from gridsearch.interp import griddedInterp1D, griddedInterp2D

from gridsearch.testing import check, report

# ---- 1. the linear path is unchanged ------------------------------------------------------------------
x = np.linspace(0, 1, 6)
y = 2*x + 1
f = griddedInterp1D(x, y)
check('1D linear is exact on a linear function', np.allclose(f([0.13, 0.77]), 2*np.array([0.13, 0.77])+1))
check('1D linear extrapolates rather than clamping',
      np.isclose(f(1.5), 4.0) and np.isclose(f(-0.5), 0.0), f'-> {f(1.5)}, {f(-0.5)}')
check('1D accepts unsorted nodes', np.allclose(griddedInterp1D(x[::-1], y[::-1])(0.4), f(0.4)))

X, Y = np.meshgrid(np.linspace(0, 1, 5), np.linspace(0, 2, 7), indexing = 'ij')
Z = 3*X - Y
g = griddedInterp2D(np.linspace(0, 1, 5), np.linspace(0, 2, 7), Z)
check('2D linear is exact on a bilinear function',
      np.allclose(g([0.2, 0.8], [1.4, 0.3]), 3*np.array([0.2, 0.8]) - np.array([1.4, 0.3])))
check('2D linear extrapolates past the rectangle', np.isclose(g(1.5, 2.5), 3*1.5-2.5), f'-> {g(1.5,2.5)}')
check('2D evaluates elementwise on paired coordinates, not on an outer product',
      np.shape(g([0.2, 0.8], [1.4, 0.3])) == (2,))

# ---- 2. pchip/cubic reproduce the linear NaN pattern --------------------------------------------------
# The reference is linear's own output, compared AWAY FROM THE NODES. On a node exactly, interp1d and
# RegularGridInterpolator assign the point to the left-hand interval, so a *valid* node bordering an
# invalid cell reads the NaN and returns NaN. That is an interval-lookup artifact, not a property worth
# reproducing: the masked kinds return the node's own value there, which is checked separately below.
xs = np.linspace(0, 1, 11)
ys = np.sin(3*xs)
ys[4] = np.nan                                            # one infeasible node
probe = np.linspace(-0.17, 1.23, 71)                      # offset so no probe point lands on a node
check('the 1D probe avoids the nodes (else the comparison below tests the lookup convention)',
      not np.any(np.isclose(probe[:, None], xs[None, :], atol = 1e-12)))
ref = np.isnan(griddedInterp1D(xs, ys, 'linear')(probe))
check('the 1D reference actually has NaN to reproduce', 0 < ref.sum() < len(probe),
      f'-> {ref.sum()} NaN of {len(probe)}')
for kind in ('pchip', 'cubic'):
    got = np.isnan(griddedInterp1D(xs, ys, kind)(probe))
    check(f'1D {kind} reproduces linear\'s NaN pattern off the nodes',
          np.array_equal(got, ref), f'-> {got.sum()} vs {ref.sum()} NaN of {len(probe)}')

zs = np.add.outer(np.sin(3*np.linspace(0, 1, 9)), np.cos(np.linspace(0, 2, 8)))
zs[3, 5] = np.nan
ax, ay = np.linspace(0, 1, 9), np.linspace(0, 2, 8)
px, py = np.meshgrid(np.linspace(0.013, 0.987, 37), np.linspace(0.017, 1.983, 33), indexing = 'ij')
ref2 = np.isnan(griddedInterp2D(ax, ay, zs, 'linear')(px, py))
check('the 2D reference actually has NaN to reproduce (the test would be vacuous otherwise)',
      0 < ref2.sum() < ref2.size, f'-> {ref2.sum()} NaN of {ref2.size}')
for kind in ('pchip', 'cubic'):
    got2 = np.isnan(griddedInterp2D(ax, ay, zs, kind)(px, py))
    check(f'2D {kind} reproduces linear\'s NaN pattern off the nodes',
          np.array_equal(got2, ref2), f'-> {got2.sum()} vs {ref2.sum()} NaN')

# The node convention itself, stated rather than inherited: a valid node next to an invalid cell keeps its
# own value under the masked kinds, where linear reports NaN.
check("linear reports NaN at a VALID node bordering an invalid cell (the lookup artifact)",
      np.isnan(griddedInterp1D(xs, ys, 'linear')(xs[5])))
check("the masked kinds return that node's own value instead",
      np.isclose(griddedInterp1D(xs, ys, 'pchip')(xs[5]), ys[5]),
      '-> {:.6f} vs y[5]={:.6f}'.format(float(griddedInterp1D(xs, ys, 'pchip')(xs[5])), ys[5]))

# The whole point of the exercise: pchip must be CONSTRUCTIBLE over a NaN-carrying surface, which is what
# failed before (PchipInterpolator raises "`y` must contain only finite values").
check('2D pchip is constructible over a surface carrying NaN at infeasible nodes',
      np.isfinite(griddedInterp2D(ax, ay, zs, 'pchip')(0.05, 0.1)))
check('the filled values never leak: a point inside the invalid cell is NaN, not a plausible number',
      np.isnan(griddedInterp2D(ax, ay, zs, 'pchip')(ax[3], ay[5])))

# ---- 2b. a non-finite COORDINATE must return NaN, not raise -------------------------------------------
# The callers evaluate policies at candidate states that can themselves be NaN (an infeasible candidate).
# 'linear' returns NaN for those on its own. The spline methods build their splines lazily per axis at
# call time, so a NaN coordinate makes axis 0 return NaN and axis 1 then RAISES while constructing a
# spline over it -- which is what broke the first attempt at using pchip in the CRRA recursion.
for kind in ('linear', 'pchip', 'cubic'):
    got = griddedInterp1D(xs, np.sin(3*xs), kind)(np.array([0.15, np.nan, 0.65]))
    check(f'1D {kind} returns NaN for a NaN coordinate rather than raising',
          np.isnan(got[1]) and np.isfinite(got[0]) and np.isfinite(got[2]), f'-> {got}')
    got2 = griddedInterp2D(ax, ay, np.add.outer(ax, ay), kind)(
        np.array([0.2, np.nan, 0.6]), np.array([1.0, 1.0, np.nan]))
    check(f'2D {kind} returns NaN for a NaN coordinate rather than raising',
          np.isnan(got2[1]) and np.isnan(got2[2]) and np.isfinite(got2[0]), f'-> {got2}')

# ---- 3. pchip is smoother than linear, and does not overshoot -----------------------------------------
# The motivation for the whole change: remove the kinks of the piecewise-linear form. Measure the second
# difference (a proxy for the kinks) and check pchip is genuinely smoother on a curved function.
xc = np.linspace(0, 2*np.pi, 15)
yc = np.sin(xc)
fine = np.linspace(0.1, 2*np.pi-0.1, 400)
d2 = {k: np.abs(np.diff(griddedInterp1D(xc, yc, k)(fine), 2)).max() for k in ('linear', 'pchip', 'cubic')}
check('1D pchip is smoother than linear (smaller max second difference)',
      d2['pchip'] < d2['linear'], '-> linear {:.3e}, pchip {:.3e}, cubic {:.3e}'.format(
          d2['linear'], d2['pchip'], d2['cubic']))
check('1D pchip is exact on the nodes it interpolates',
      np.allclose(griddedInterp1D(xc, yc, 'pchip')(xc), yc))

# Monotonicity is why pchip rather than cubic: a policy flat at a bound must not be overshot, which is the
# documented failure of smoothing a cornered profile.
step = np.array([0., 0., 0., 0., 1., 2., 3., 3., 3.])
xstep = np.arange(len(step), dtype = float)
fineS = np.linspace(0, len(step)-1, 400)
vals = {k: griddedInterp1D(xstep, step, k)(fineS) for k in ('pchip', 'cubic')}
check('1D pchip does not overshoot a profile that is flat at a corner',
      vals['pchip'].min() >= step.min()-1e-12 and vals['pchip'].max() <= step.max()+1e-12,
      '-> pchip range [{:.4f}, {:.4f}]'.format(vals['pchip'].min(), vals['pchip'].max()))
check('cubic DOES overshoot it -- which is why pchip is the default recommendation, not cubic',
      vals['cubic'].min() < step.min()-1e-6 or vals['cubic'].max() > step.max()+1e-6,
      '-> cubic range [{:.4f}, {:.4f}] vs data [{:.1f}, {:.1f}]'.format(
          vals['cubic'].min(), vals['cubic'].max(), step.min(), step.max()))

# ---- 4. trailing axes and edge cases ------------------------------------------------------------------
yt = np.stack([np.sin(3*xs), np.cos(3*xs)], axis = -1)    # (M, 2)
yt[4, 0] = np.nan                                          # invalid in ONE trailing entry only
ft = griddedInterp1D(xs, yt, 'pchip')
check('a node invalid in any trailing entry invalidates the whole node',
      np.isnan(ft(xs[4])).all(), f'-> {ft(xs[4])}')
check('trailing axes pass through with the right shape', np.shape(ft([0.1, 0.2])) == (2, 2))
check('an all-valid surface returns the bare interpolant (no mask overhead)',
      not np.isnan(griddedInterp2D(ax, ay, np.ones((9, 8)), 'pchip')(0.5, 1.0)))

# ---- 5. griddedSmooth1D's knots: the adaptive branch is discontinuous, the fixed one is not -----------
# Why this matters beyond smoothing quality: InformalSavings' policy smoother feeds a calibration whose
# outer residual is finite-differenced in a model parameter. UnivariateSpline picks its knot COUNT from
# the data, so that count flips as the parameter moves and the fitted profile jumps with it -- measured
# in that model as ~3.5e-6 jumps in the outer residual, the size of an unresolved calibration's plateau.
from gridsearch.interp import griddedSmooth1D

from scipy import interpolate as _interp

xs5 = np.linspace(0.0, 1.0, 45)
rng = np.random.default_rng(0)
noise = 1e-4*rng.standard_normal(xs5.size)          # the kinks a real profile carries
# The perturbation has to change the profile's SHAPE, not just its level: FITPACK's knot count is driven
# by the residual against the smoothing bound, and a constant offset (or a pure rescaling) leaves that
# unchanged, so it provokes no flip at all. A frequency shift is the cheap stand-in for what a model
# parameter does to a solved policy.
prof = lambda o: np.sin(4*(1+o)*xs5) + 0.3*xs5**2 + noise

# The mechanism, asserted directly rather than through a tuned threshold: over the same sweep the
# adaptive branch changes its knot count repeatedly and the fixed branch cannot.
sweep = np.linspace(0.0, 1.0, 201)
nAdaptive = [len(_interp.UnivariateSpline(xs5, prof(o), s = 1e-5, k = 3).get_knots()) for o in sweep]
flips = int(np.sum(np.diff(nAdaptive) != 0))
check('the adaptive branch re-chooses its knot count as the data changes shape',
      flips > 0 and len(set(nAdaptive)) > 1,
      f'-> {len(set(nAdaptive))} distinct counts {sorted(set(nAdaptive))}, {flips} flips')
check('the fixed branch cannot: its knots depend on the nodes and the mask, never on the values',
      len({len(interp._fixedKnots(xs5, 3, 4)) for o in sweep}) == 1,
      f'-> {len(interp._fixedKnots(xs5, 3, 4))} interior knots throughout')

# The symptom, measured in a window bracketing one flip: the largest pointwise change between successive
# profiles against the median one. Over a WIDE sweep the genuine change in the profile dominates and both
# branches read ~1.2 -- the jump is only visible where the flip is the biggest thing happening.
def jumpRatio(knots, lo = 0.030, hi = 0.045, n = 60):
    offs = np.linspace(lo, hi, n)
    V = np.array([griddedSmooth1D(xs5, prof(o), s = 1e-5, knots = knots) for o in offs])
    d = np.max(np.abs(np.diff(V, axis = 0)), axis = 1)
    return np.max(d)/np.median(d)

adaptiveJump, fixedJump = jumpRatio(None), jumpRatio(4)
check('fixed knots move continuously across a window where the adaptive count flips',
      fixedJump < 1.1, f'-> max/median pointwise step = {fixedJump:.2f}')
check('the adaptive branch jumps there (this is the bug being switched off)',
      adaptiveJump > 1.5*fixedJump, f'-> adaptive {adaptiveJump:.2f} vs fixed {fixedJump:.2f}')

base = prof(0.0) - noise

# Linearity is the property that buys the continuity, so test it directly rather than only its symptom.
a, b = base, np.cos(6*xs5)
lhs = griddedSmooth1D(xs5, 2.0*a - 3.0*b, s = 1e-5, knots = 4)
rhs = 2.0*griddedSmooth1D(xs5, a, s = 1e-5, knots = 4) - 3.0*griddedSmooth1D(xs5, b, s = 1e-5, knots = 4)
check('fixed knots make the fit a LINEAR map of the data', np.allclose(lhs, rhs, atol = 1e-12),
      f'-> max|delta| = {np.max(np.abs(lhs-rhs)):.2e}')
check('the adaptive branch is not linear in the data',
      not np.allclose(griddedSmooth1D(xs5, 2.0*a-3.0*b, s = 1e-5),
                      2.0*griddedSmooth1D(xs5, a, s = 1e-5)-3.0*griddedSmooth1D(xs5, b, s = 1e-5)))

# It must still smooth: closer to the truth than the noisy input, and no worse than the adaptive fit.
err = lambda y: np.max(np.abs(y-base))
check('fixed knots still denoise (closer to the clean profile than the noisy input)',
      err(griddedSmooth1D(xs5, base+noise, s = 1e-5, knots = 4)) < err(base+noise),
      '-> {:.2e} vs {:.2e}'.format(err(griddedSmooth1D(xs5, base+noise, s = 1e-5, knots = 4)),
                                   err(base+noise)))

# NaN semantics carry over: infeasible cells stay NaN and knots land on VALID nodes, so Schoenberg-Whitney
# holds per column rather than only for a full one.
yn = np.stack([base+noise, base+noise], axis = -1)
yn[10:18, 1] = np.nan
sm = griddedSmooth1D(xs5, yn, s = 1e-5, knots = 4)
check('NaNs pass through the fixed-knot branch unchanged', np.isnan(sm[10:18, 1]).all())
check('a masked column is still fitted on its surviving nodes', np.isfinite(sm[:10, 1]).all()
      and np.isfinite(sm[18:, 1]).all())
check('a column too short for interior knots still fits (degree-k least squares, no raise)',
      np.isfinite(griddedSmooth1D(np.linspace(0, 1, 6), np.linspace(0, 1, 6)**2,
                                  s = 1e-5, knots = 4)).all())
check('default (knots=None) reproduces the adaptive fit bitwise -- existing results are untouched',
      np.array_equal(griddedSmooth1D(xs5, base+noise, s = 1e-5),
                     griddedSmooth1D(xs5, base+noise, s = 1e-5, knots = None)))

# ---- 6. griddedGradient1D: exact where the spline can be, and NaN exactly where the input was ---------
from gridsearch import griddedGradient1D
xq = np.linspace(0., 2., 81)
yq = 3*xq**2 - 2*xq + 1                      # derivative 6x-2, exactly representable by a cubic spline
check('exact on a quadratic', np.allclose(griddedGradient1D(xq, yq, s=0.0), 6*xq - 2, atol=1e-8))
gq2 = griddedGradient1D(xq, np.column_stack([yq, -yq]), s=0.0)
check('a trailing axis is differentiated column by column',
      gq2.shape == (81, 2) and np.allclose(gq2[:, 0], 6*xq - 2, atol=1e-8)
      and np.allclose(gq2[:, 1], -(6*xq - 2), atol=1e-8))
yNan = yq.copy(); yNan[[10, 11, 60]] = np.nan
gNan = griddedGradient1D(xq, yNan, s=0.0)
check('NaN comes back exactly where the input had it, and nowhere else',
      np.array_equal(np.isnan(gNan), np.isnan(yNan)))
check('the surviving points are still accurate (a NaN does not poison the fit)',
      np.allclose(gNan[~np.isnan(gNan)], (6*xq - 2)[~np.isnan(yNan)], atol=1e-6))
check('too few valid points -> all NaN rather than a bogus low-order fit',
      np.all(np.isnan(griddedGradient1D(xq, np.where(np.arange(81) < 3, yq, np.nan), s=0.0))))

report()
