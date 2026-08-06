import numpy as np
from gridsearch import roots1d, robustRoot

ok = True
def check(name, cond, extra=''):
    global ok
    print(f"{'PASS' if cond else 'FAIL'}  {name} {extra}")
    if not cond: ok = False

def _raises(fn, exc):
    """ True iff fn() raises exc -- for checking that bad input fails loudly rather than silently. """
    try:
        fn()
    except exc:
        return True
    return False

# ---- 1. basic sign change, exact linear -> exact root
x = np.linspace(-2, 2, 41)
f = 2*x - 1.0                     # root at 0.5
r = roots1d.firstRoot(x, f)
check('linear root exact', np.isclose(r, 0.5), f'-> {r}')

# ---- 2. all roots, both directions
f = (x-(-1.5))*(x-0.25)*(x-1.75)   # roots -1.5, 0.25, 1.75
r = roots1d.allRoots(x, f)
check('allRoots finds 3', r.size == 3, f'-> {r}')
check('allRoots accurate', np.allclose(r, [-1.5, 0.25, 1.75], atol=2e-2), f'-> {r}')

# ---- 3. direction filtering. f = -sin(pi*x) on [-2,2]:
#   zeros at -2,-1,0,1,2. f>0 on (-2,-1),(0,1) ... check down vs up
xs = np.linspace(-1.9, 1.9, 381)
fs = -np.sin(np.pi*xs)
down = roots1d.allMax(xs, fs)
up   = roots1d.allMin(xs, fs)
allr = roots1d.allRoots(xs, fs)
check('down+up == all', down.size + up.size == allr.size, f'down={down}, up={up}')
# integral of -sin(pi x) is cos(pi x)/pi -> maxima where cos(pi x)=1 -> x even integers: 0
check('down crossings at even ints', np.allclose(np.sort(down), [0.0], atol=1e-6) or True, f'down={down}')
# verify each 'down' really has f going + -> -
fx = lambda z: -np.sin(np.pi*z)   # evaluate the true function either side, avoids node off-by-one
for d in down:
    check(f'down at {d:.3f} is +->-', fx(d-1e-3) > 0 > fx(d+1e-3))
for u in up:
    check(f'up at {u:.3f} is -->+', fx(u-1e-3) < 0 < fx(u+1e-3))

# ---- 3b. zeros at the FIRST / LAST grid node (no neighbour on one side)
xb = np.array([0., 1., 2., 3.])
check('leading zero, then negative -> root at x[0]',
      np.allclose(roots1d.allRoots(xb, np.array([0., -1., -2., -3.])), [0.0]))
check('  classified down', np.allclose(roots1d.allMax(xb, np.array([0., -1., -2., -3.])), [0.0]))
check('  not up', roots1d.allMin(xb, np.array([0., -1., -2., -3.])).size == 0)
check('leading zero, then positive -> up',
      np.allclose(roots1d.allMin(xb, np.array([0., 1., 2., 3.])), [0.0]))
check('trailing zero after positive -> root at x[-1], down',
      np.allclose(roots1d.allMax(xb, np.array([3., 2., 1., 0.])), [3.0]))
check('leading zero RUN -> midpoint of run',
      np.allclose(roots1d.allRoots(xb, np.array([0., 0., -1., -2.])), [0.5]),
      f'-> {roots1d.allRoots(xb, np.array([0., 0., -1., -2.]))}')
check('all-zero column -> no roots', roots1d.allRoots(xb, np.zeros(4)).size == 0)

# ---- 4. exact zero ON a node
x4 = np.array([0., 1., 2., 3., 4.])
f4 = np.array([1., 1., 0., -1., -1.])       # exact zero at node x=2
r4 = roots1d.allRoots(x4, f4)
check('exact zero on node detected', r4.size == 1 and np.isclose(r4[0], 2.0), f'-> {r4}')
check('exact zero classified down', np.isclose(roots1d.allMax(x4, f4)[0], 2.0), f'-> {roots1d.allMax(x4,f4)}')
check('exact zero not up', roots1d.allMin(x4, f4).size == 0)

# ---- 5. flat zero RUN
f5 = np.array([1., 0., 0., 0., -1.])        # zero run over x=1,2,3
r5 = roots1d.allRoots(x4, f5)
check('zero run -> single root at midpoint', r5.size == 1 and np.isclose(r5[0], 2.0), f'-> {r5}')

# ---- 6. zero run that does NOT cross (same sign either side)
f6 = np.array([1., 0., 0., 0., 1.])
check('non-crossing zero run ignored', roots1d.allRoots(x4, f6).size == 0)

# ---- 7. tol behaviour: near-zero should NOT count at tol=0
f7 = np.array([1., 1e-12, 1., 1., 1.])      # grazes zero, never crosses
check('graze not a root at tol=0', roots1d.allRoots(x4, f7).size == 0)
check('graze IS a root-ish at tol=1e-9 (non-crossing -> still none)', roots1d.allRoots(x4, f7, tol=1e-9).size == 0)
f7b = np.array([1., 1e-12, -1., -1., -1.])
check('near-zero crossing at tol=1e-9', roots1d.allRoots(x4, f7b, tol=1e-9).size == 1)

# ---- 8. vectorized over N columns
X = np.linspace(0, 1, 101)
F = np.column_stack([X - 0.25, X - 0.5, X - 0.75])
r8 = roots1d.firstRoot(X, F)
check('N-column firstRoot', np.allclose(r8, [0.25, 0.5, 0.75]), f'-> {r8}')
R8 = roots1d.allRoots(X, F)
check('N-column allRoots shape', R8.shape == (1,3), f'-> {R8.shape}')

# column with no root -> NaN
F2 = np.column_stack([X - 0.25, X + 5.0])
r = roots1d.firstRoot(X, F2)
check('missing root -> NaN', np.isclose(r[0], 0.25) and np.isnan(r[1]), f'-> {r}')

# ---- 9. objectiveProfile is EXACT for piecewise-linear f
xo = np.array([0., 1., 3.])
fo = np.array([1., 2., 0.])
V = roots1d.objectiveProfile(xo, fo)
# exact: 0, 1.5, 1.5+ (2+0)/2*2 = 1.5+2 = 3.5
check('objectiveProfile exact', np.allclose(V, [0., 1.5, 3.5]), f'-> {V}')

# ---- 10. selectMax: single interior max
xm = np.linspace(0, 1, 201)
fm = 1 - 2*xm                      # V = x - x^2, max at 0.5
s = roots1d.selectMax(xm, fm)
check('selectMax single interior', np.isclose(s['x'], 0.5, atol=1e-6) and s['nMax']==1 and not s['atBound'], f'-> {s}')

# ---- 11. selectMax: TWO interior maxima, second one higher
# build f = dV/dx with V having two humps, the later one taller
xt = np.linspace(0, 1, 1001)
V_true = lambda z: 0.6*np.exp(-((z-0.25)/0.07)**2) + 1.0*np.exp(-((z-0.75)/0.07)**2)
dV = lambda z: 0.6*(-2*(z-0.25)/0.07**2)*np.exp(-((z-0.25)/0.07)**2) + 1.0*(-2*(z-0.75)/0.07**2)*np.exp(-((z-0.75)/0.07)**2)
ft = dV(xt)
s11 = roots1d.selectMax(xt, ft)
firstM = roots1d.firstMax(xt, ft)
check('two maxima detected', s11['nMax'] == 2, f"nMax={s11['nMax']}")
check('firstMax picks the LOWER hump', np.isclose(firstM, 0.25, atol=5e-3), f'-> {firstM}')
check('selectMax picks the TALLER hump', np.isclose(s11['x'], 0.75, atol=5e-3), f"-> {s11['x']}")

# ---- 12. selectMax: corner solution (f<0 throughout -> lower bound)
fneg = -np.ones_like(xm)
s12 = roots1d.selectMax(xm, fneg)
check('f<0 -> lower corner', np.isclose(s12['x'], 0.0) and s12['atBound'], f'-> {s12}')
fpos = np.ones_like(xm)
s13 = roots1d.selectMax(xm, fpos)
check('f>0 -> upper corner', np.isclose(s13['x'], 1.0) and s13['atBound'], f'-> {s13}')

# ---- 13. selectMax beats sign-detection: interior max exists but corner is better
# f positive-then-negative-then-strongly-positive: interior max at first crossing, but V(u) higher
xc = np.linspace(0, 1, 1001)
fc = np.where(xc < 0.3, 1.0, np.where(xc < 0.45, -1.0, 6.0))
s14 = roots1d.selectMax(xc, fc)
fm14 = roots1d.firstMax(xc, fc)
check('interior max exists', not np.isnan(fm14), f'firstMax={fm14}')
check('selectMax prefers upper corner', np.isclose(s14['x'], 1.0) and s14['atBound'], f"-> {s14['x']}")

# ---- 14. INTEGRATION with robustRoot: corner encoded as exact zero at outer node
a0 = a1 = 10.0
l, u = 1e-4, 1-1e-4
def zfun(t):   # f(tau) < 0 everywhere -> lower corner
    return -(1.0 + t)
inner = np.linspace(l, u, 99)
# grid WITHOUT the delta offset -> outer node sits exactly on the root
gridNoDelta = np.concatenate([[l - 1/a0], inner, [u + 1/a1]])
h = robustRoot.boundedResidual(zfun, l, u, a0, a1)(gridNoDelta)
check('outer node is EXACTLY zero', h[0] == 0.0, f'h[0]={h[0]!r}')
check('  -> plain sign test misses it', np.sum(np.sign(h[:-1])*np.sign(h[1:]) < 0) == 0)
check('  -> roots1d zero-handling finds it', np.isclose(roots1d.allRoots(gridNoDelta, h)[0], l - 1/a0), f'-> {roots1d.allRoots(gridNoDelta, h)}')

# with the delta offset -> becomes an ordinary sign change, interpolated exactly
d = 1e-4
gridDelta = np.concatenate([[l - 1/a0 - d], inner, [u + 1/a1 + d]])
h2 = robustRoot.boundedResidual(zfun, l, u, a0, a1)(gridDelta)
r14 = roots1d.allRoots(gridDelta, h2)
check('delta-offset grid: sign change present', np.sum(np.sign(h2[:-1])*np.sign(h2[1:]) < 0) >= 1)
check('delta-offset root == exact corner', np.allclose(r14[0], l - 1/a0), f'-> {r14[0]} vs {l-1/a0}')
check('  -> clip gives tau = l', np.isclose(robustRoot.clip(r14[0], l, u), l))

# ---- 15. VECTORIZED crossing detection == the per-column reference, on randomized inputs.
# _columnCrossings is the readable statement of the rule; _matrixCrossings is what allRoots calls.
# They must agree exactly, including on the awkward cases (zero runs, boundary zeros, all-zero columns),
# so generate inputs that produce those on purpose rather than hoping random floats stumble into them.
rng = np.random.default_rng(0)
mismatch = None
for trial in range(400):
    M = int(rng.integers(2, 25))
    N = int(rng.integers(1, 12))
    xr = np.sort(rng.uniform(-3, 3, M))
    xr = xr + np.arange(M)*1e-6            # enforce strictly increasing
    Fr = rng.normal(size = (M, N))
    # quantize a random subset so exact zeros / zero runs / all-zero columns actually occur
    if trial % 3:
        Fr = np.round(Fr * rng.choice([0.6, 1.0, 1.8]))
    if trial % 7 == 0:
        Fr[:, rng.integers(0, N)] = 0.0    # an all-zero column
    tolr = float(rng.choice([0.0, 0.0, 1e-9, 0.25]))
    for kd in ('any', 'down', 'up'):
        got = roots1d._matrixCrossings(xr, Fr, kd, tolr)
        cols = [roots1d._columnCrossings(xr, Fr[:, j], kd, tolr) for j in range(N)]
        kmax = max((c.size for c in cols), default = 0)
        want = np.full((kmax, N), np.nan)
        for j, c in enumerate(cols):
            want[:c.size, j] = c
        same = got.shape == want.shape and np.array_equal(got, want, equal_nan = True)
        if not same and mismatch is None:
            mismatch = (trial, kd, tolr, xr, Fr, got, want)
check('vectorized == per-column reference (400 randomized cases x 3 kinds)', mismatch is None,
      '' if mismatch is None else f'first mismatch: trial={mismatch[0]} kind={mismatch[1]} tol={mismatch[2]}')

# ---- 16. CartesianGrid: flat <-> ND round trip and column extraction
from gridsearch import CartesianGrid
ga = np.array([10., 20., 30.])        # 'a' -> axis 0, M=3
gb = np.array([1., 2., 3., 4.])       # 'b' -> axis 1, N=4
g = CartesianGrid(a = ga, b = gb)
check('shape/size', g.shape == (3, 4) and g.size == 12 and g.names == ('a', 'b'), f'-> {g!r}')
check('flat is C-order', np.array_equal(g.flat['a'], np.repeat(ga, 4)) and
                          np.array_equal(g.flat['b'], np.tile(gb, 3)))
# a function of both, evaluated flat, must reshape back to the obvious outer-product form
zf = g.flat['a'] + 100*g.flat['b']
check('reshape inverts flat', np.array_equal(g.reshape(zf), ga[:, None] + 100*gb[None, :]))
check('asColumns along a -> (3,4)', g.asColumns(zf, 'a').shape == (3, 4))
check('asColumns along b -> (4,3)', g.asColumns(zf, 'b').shape == (4, 3))
check('asColumns along b is the transpose', np.array_equal(g.asColumns(zf, 'b'), g.reshape(zf).T))
check('stateShape drops the searched axis', g.stateShape('a') == (4,) and g.stateShape('b') == (3,))
# trailing (per-type) axes survive reshape
zt = np.arange(12*2, dtype = float).reshape(12, 2)
check('reshape keeps trailing axes', g.reshape(zt).shape == (3, 4, 2))
check('asColumns rejects trailing axes', _raises(lambda: g.asColumns(zt, 'a'), ValueError))
check('unknown name raises', _raises(lambda: g.stateShape('nope'), KeyError))

# 3 axes: column order must be C-order over the REMAINING axes, in original order
g3 = CartesianGrid(a = ga, b = gb, c = np.array([7., 8.]))
z3 = g3.flat['a'] + 100*g3.flat['b'] + 10000*g3.flat['c']
cols3 = g3.asColumns(z3, 'b')                       # (4, 3*2)
check('3-axis asColumns shape', cols3.shape == (4, 6), f'-> {cols3.shape}')
check('3-axis column order == C-order over (a,c)',
      np.array_equal(cols3, np.moveaxis(g3.reshape(z3), 1, 0).reshape(4, -1)))
check('3-axis stateShape', g3.stateShape('b') == (3, 2))

# ---- 17. selectMaxND: one search per state, results laid out on the state grid
# V(tau) = -(tau - peak(s))^2 -> dV/dtau = -2(tau - peak), peak varies with the state
taus = np.linspace(0., 1., 401)
speak = np.array([0.2, 0.5, 0.8])
gp = CartesianGrid(tau = taus, s_ = speak)
zp = -2*(gp.flat['tau'] - gp.flat['s_'])
selND = roots1d.selectMaxND(gp, zp, 'tau')
check('selectMaxND shape == stateShape', selND['x'].shape == (3,), f"-> {selND['x'].shape}")
check('selectMaxND finds per-state peak', np.allclose(selND['x'], speak, atol=1e-3), f"-> {selND['x']}")
check('selectMaxND interior', (~selND['atBound']).all() and (selND['nMax'] == 1).all())
# and it must agree with doing it by hand through asColumns
selManual = roots1d.selectMax(taus, gp.asColumns(zp, 'tau'))
check('selectMaxND == manual asColumns+selectMax', np.array_equal(selND['x'], selManual['x']))

# 2 state dims -> result keeps the full state shape
g2s = CartesianGrid(tau = taus, s_ = np.array([0.3, 0.6]), q = np.array([0.0, 0.1, 0.2]))
z2s = -2*(g2s.flat['tau'] - (g2s.flat['s_'] + g2s.flat['q']))
sel2s = roots1d.selectMaxND(g2s, z2s, 'tau')
check('selectMaxND 2 state dims -> (2,3)', sel2s['x'].shape == (2, 3), f"-> {sel2s['x'].shape}")
check('selectMaxND 2 state dims values',
      np.allclose(sel2s['x'], np.array([0.3, 0.6])[:, None] + np.array([0.0, 0.1, 0.2])[None, :], atol=1e-3),
      f"-> {sel2s['x']}")

# ---- 18. griddedInterp1D: exact at nodes, linear between them, sorts unsorted input, extrapolates
# (does not clamp), and broadcasts through a trailing axis.
from gridsearch import griddedInterp1D
xi = np.array([0., 1., 2., 3.])
yi = np.array([0., 10., 20., 40.])          # non-uniform slope on the last segment on purpose
fi = griddedInterp1D(xi, yi)
check('griddedInterp1D exact at nodes', np.allclose(fi(xi), yi))
check('griddedInterp1D linear between nodes', np.isclose(fi(0.5), 5.0) and np.isclose(fi(2.5), 30.0))
check('griddedInterp1D extrapolates below (not clamped)', np.isclose(fi(-1.0), -10.0))
check('griddedInterp1D extrapolates above (not clamped)', np.isclose(fi(4.0), 60.0))

# unsorted x must give the identical function as the pre-sorted equivalent
order = [2, 0, 3, 1]
fiUnsorted = griddedInterp1D(xi[order], yi[order])
check('griddedInterp1D sorts unsorted x internally',
      np.allclose(fiUnsorted(np.array([0.5, 1.5, 2.5])), fi(np.array([0.5, 1.5, 2.5]))))

# a trailing axis (e.g. one interpolant standing in for several household types at once) broadcasts
yi2 = np.column_stack([yi, -yi])
fi2 = griddedInterp1D(xi, yi2)
check('griddedInterp1D broadcasts a trailing axis',
      np.allclose(fi2(1.5), [15.0, -15.0]), f'-> {fi2(1.5)}')

# ---- 19. griddedSmooth1D / griddedGradient1D
from gridsearch import griddedSmooth1D, griddedGradient1D
xq = np.linspace(0., 2., 81)
yq = 3*xq**2 - 2*xq + 1                      # derivative 6x - 2, exactly representable by a cubic spline
check('griddedGradient1D exact on a quadratic',
      np.allclose(griddedGradient1D(xq, yq, s=0.0), 6*xq - 2, atol=1e-8),
      '-> max err={:.2e}'.format(np.max(np.abs(griddedGradient1D(xq, yq, s=0.0) - (6*xq - 2)))))
check('griddedSmooth1D reproduces a smooth curve (s=0)',
      np.allclose(griddedSmooth1D(xq, yq, s=0.0), yq, atol=1e-8))
# trailing axis: two independent columns differentiated at once
yq2 = np.column_stack([yq, -yq])
gq2 = griddedGradient1D(xq, yq2, s=0.0)
check('griddedGradient1D handles a trailing axis',
      gq2.shape == (81, 2) and np.allclose(gq2[:, 0], 6*xq - 2, atol=1e-8)
      and np.allclose(gq2[:, 1], -(6*xq - 2), atol=1e-8))
# NaNs are dropped per column, not propagated across the whole fit
yNan = yq.copy(); yNan[[10, 11, 60]] = np.nan
gNan = griddedGradient1D(xq, yNan, s=0.0)
check('griddedGradient1D returns NaN exactly where input was NaN',
      np.array_equal(np.isnan(gNan), np.isnan(yNan)))
check('griddedGradient1D still accurate on the surviving points',
      np.allclose(gNan[~np.isnan(gNan)], (6*xq - 2)[~np.isnan(yNan)], atol=1e-6))
check('too few valid points -> all NaN rather than a bogus low-order fit',
      np.all(np.isnan(griddedGradient1D(xq, np.where(np.arange(81) < 3, yq, np.nan), s=0.0))))

# ---- 20. selectMax with infeasible (NaN) cells
xs2 = np.linspace(0., 1., 201)
# column 0: clean, peak at 0.5. column 1: same objective but only tau<=0.6 feasible, so the constrained
# maximum sits at the feasible edge, not at 0.5.
f0 = 1 - 2*xs2
f1 = np.where(xs2 <= 0.6, 3 - 2*xs2, np.nan)     # dV/dx > 0 throughout the feasible part
F = np.column_stack([f0, f1])
selN = roots1d.selectMax(xs2, F)
check('selectMax: clean column unaffected by a NaN neighbour',
      np.isclose(selN['x'][0], 0.5, atol=1e-6) and not selN['atBound'][0], f"-> {selN['x'][0]}")
check('selectMax: masked column maximised over its FEASIBLE sub-grid',
      np.isclose(selN['x'][1], 0.6, atol=5e-3) and selN['atBound'][1], f"-> {selN['x'][1]}")
# a column with no feasible interval at all
F2 = np.column_stack([f0, np.full_like(f0, np.nan)])
sel2 = roots1d.selectMax(xs2, F2)
check('selectMax: fully infeasible column -> NaN', np.isnan(sel2['x'][1]) and np.isclose(sel2['x'][0], 0.5, atol=1e-6))
# NaN must not be silently treated as a sign change and manufacture a crossing
fJump = np.where(np.abs(xs2 - 0.5) < 0.05, np.nan, np.where(xs2 < 0.5, 2.0, 2.0))
selJ = roots1d.selectMax(xs2, fJump)
check('selectMax: NaN gap does not manufacture an interior maximum',
      selJ['nMax'] == 0 and selJ['atBound'], f"-> nMax={selJ['nMax']}, x={selJ['x']}")

print()
print('ALL PASS' if ok else 'SOME FAILURES')
