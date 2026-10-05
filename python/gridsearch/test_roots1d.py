import numpy as np
from gridsearch import roots1d, robustRoot

from gridsearch.testing import check, report

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
fx = lambda z: -np.sin(np.pi*z)   # the true function, evaluated either side: avoids a node off-by-one
check('every down crossing really goes + -> -', all(fx(d-1e-3) > 0 > fx(d+1e-3) for d in down), f'down={down}')
check('every up crossing really goes - -> +', all(fx(u-1e-3) < 0 < fx(u+1e-3) for u in up), f'up={up}')

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

# ---- 21. selectMax groups ragged columns by feasibility pattern (a speed optimisation that must not
# change a single answer). The reference is the obvious per-column loop: build a matrix with many
# columns but only a handful of distinct NaN patterns -- the case a policy grid search produces, where
# feasibility depends on some state coordinates and not others -- and require agreement bitwise.
rng = np.random.default_rng(20260811)
xr = np.linspace(0., 1., 61)
N, nPat = 240, 4
patterns = []
for p in range(nPat):
    mask = np.zeros(xr.size, dtype = bool)          # True = infeasible
    mask[:2 + 5*p] = True                           # a leading infeasible run of varying length
    if p == nPat - 1:
        mask[-4:] = True                            # one pattern infeasible at BOTH ends
    patterns.append(mask)
assign = rng.integers(0, nPat, N)
Fr = np.empty((xr.size, N))
for j in range(N):
    Fr[:, j] = 1.5 - 3*xr + 0.4*rng.standard_normal(1) + 0.3*np.sin(6*xr + j)
Fr[:, rng.permutation(N)[:20]] = np.abs(Fr[:, rng.permutation(N)[:20]])   # some columns never cross
for j in range(N):
    Fr[patterns[assign[j]], j] = np.nan
Fr[:, :6] = np.where(np.isnan(Fr[:, :6]), 1.0, Fr[:, :6])                 # a few fully clean columns

selG = roots1d.selectMax(xr, Fr)
refG = {'x': np.full(N, np.nan), 'nMax': np.zeros(N, dtype = int), 'atBound': np.zeros(N, dtype = bool)}
for j in range(N):
    okj = ~np.isnan(Fr[:, j])
    if okj.sum() < 2:
        continue
    s1 = roots1d.selectMax(xr[okj], Fr[okj, j])
    refG['x'][j], refG['nMax'][j], refG['atBound'][j] = s1['x'], s1['nMax'], s1['atBound']
xSame = (selG['x'] == refG['x']) | (np.isnan(selG['x']) & np.isnan(refG['x']))
check('selectMax: pattern-grouped ragged columns match the per-column loop bitwise',
      xSame.all() and np.array_equal(selG['nMax'], refG['nMax'])
      and np.array_equal(selG['atBound'], refG['atBound']),
      f'-> {N} columns, {len({m.tobytes() for m in np.isnan(Fr).T})} distinct patterns, '
      f'{int((~xSame).sum())} mismatches')
# every column distinct: the grouping must degenerate to the per-column case, not silently merge
Fd = Fr.copy()
for j in range(N):
    Fd[2 + (j % (xr.size - 8)), j] = np.nan          # give each column its own extra hole
selD = roots1d.selectMax(xr, Fd)
refD = np.full(N, np.nan)
for j in range(N):
    okj = ~np.isnan(Fd[:, j])
    if okj.sum() >= 2:
        refD[j] = roots1d.selectMax(xr[okj], Fd[okj, j])['x']
dSame = (selD['x'] == refD) | (np.isnan(selD['x']) & np.isnan(refD))
check('selectMax: all-distinct patterns still match the per-column loop bitwise', dSame.all(),
      f'-> {len({m.tobytes() for m in np.isnan(Fd).T})} distinct patterns over {N} columns')

# ---- 9. selectMaxFrozen: candidates tested and ranked at their own frozen predetermined state.
# A synthetic political problem W(τ; a) = φ(τ) + c·τ·a with the predetermined state a = a(τ) = τ in
# equilibrium. The consistent FOC is z(τ) = φ'(τ) + c·τ; the objective at a candidate's frozen state is
# W_c(τ) = φ(τ) + c·τ_c·τ. φ has two humps near 0.3 and 0.7 of heights tuned through a tilt ε so that
# (num_robustroot.tex): with λ ≡ -Δφ/(c·Δτ²) in (0.5, 0.7) both crossings are equilibria, payoff
# dominance picks the upper one and the integral criterion picks the lower; with λ in (0.7, 1) only the
# lower is an equilibrium and both rules pick it.
xg = np.linspace(0.02, 0.98, 97)
c0 = 0.01

def _frozenFactory(φ, c):
    def frozen(cand):
        K, Nc = cand.shape
        W = np.full((K, xg.size, Nc), np.nan)
        for k in range(K):
            for j in range(Nc):
                if np.isfinite(cand[k, j]):
                    W[k, :, j] = φ(xg) + c*cand[k, j]*xg
        return W
    return frozen

def _bruteEquilibria(φ, dφ, c, roots, fine = np.linspace(0.02, 0.98, 9601)):
    """ Oracle: which crossings are global maxima of their own frozen objective, and their own values.
    Each grid-located crossing is first refined to the exact zero of the continuous z = φ' + c·τ, so that
    its own value is an exact local maximum of W_c and the fine-grid maximum (which undershoots a true
    maximum by at most ½|φ''|(Δ/2)² ≈ 4e-10) can be compared at 1e-9. """
    from scipy import optimize
    eq, val, ref = [], [], []
    for r in roots:
        zc = lambda τ: dφ(τ) + c*τ
        a, b = r - 0.02, r + 0.02
        r = optimize.brentq(zc, a, b) if zc(a)*zc(b) < 0 else r
        Wr = φ(fine) + c*r*fine
        own = φ(r) + c*r*r
        eq.append(own >= Wr.max() - 1e-9)
        val.append(own)
        ref.append(r)
    return np.array(eq), np.array(val), np.array(ref)

def _case(eps):
    φ = lambda τ: -((τ - 0.3)**2)*((τ - 0.7)**2) + eps*(τ - 0.5)
    dφ = lambda τ: -2*(τ - 0.3)*(τ - 0.7)**2 - 2*(τ - 0.3)**2*(τ - 0.7) + eps
    z = dφ(xg) + c0*xg
    roots = roots1d.allRoots(xg, z, kind = 'any')
    down = roots1d.allMax(xg, z)
    return φ, dφ, z, roots, down

# 9a. the state does not move: identical to selectMax (both pick the true maximum, and nEq == 1)
φa, dφa, za, _, _ = _case(-0.0030)
zFixed = dφa(xg)                                           # a ≡ 0: z is the derivative of φ itself
selFixed = roots1d.selectMaxFrozen(xg, zFixed, _frozenFactory(φa, 0.0))
selL = roots1d.selectMax(xg, zFixed)
check('selectMaxFrozen: fixed state -> same x as selectMax', selFixed['x'] == selL['x'],
      f"-> frozen {selFixed['x']:.6f}, legacy {selL['x']:.6f}")
check('selectMaxFrozen: fixed state -> exactly one equilibrium among the candidates',
      selFixed['nEq'] == 1 and selFixed['nCand'] == selL['nMax'] + 2 + (roots1d.allMin(xg, zFixed).size)
      and not selFixed['fallback'], f"-> nCand={selFixed['nCand']}, nEq={selFixed['nEq']}, nMax={selFixed['nMax']}")

# 9b. the discriminating case: two equilibria, the rules disagree, the frozen rule is the oracle's.
# With humps at 0.3 and 0.7 the algebra gives λ = -ε/c: both crossings are equilibria for λ in (0.3, 0.7),
# payoff dominance picks the upper for λ < 1 and the integral criterion for λ < 0.5 only.
found = None
for eps in np.linspace(-0.0068, -0.0052, 17):
    φb, dφb, zb, rootsB, downB = _case(eps)
    if downB.size != 2:
        continue
    eqB, valB, refB = _bruteEquilibria(φb, dφb, c0, downB)
    legacyPick = roots1d.selectMax(xg, zb)['x']
    if eqB.all() and np.isclose(legacyPick, downB[0], atol = 2e-2) and valB[1] > valB[0]:
        found = (eps, φb, dφb, zb, downB, valB)
        break
check('selectMaxFrozen test case: a tilt exists at which both crossings are equilibria and the rules disagree',
      found is not None, '' if found is None else f'-> eps={found[0]:.5f}, crossings {found[4]}')
if found is not None:
    eps, φb, dφb, zb, downB, valB = found
    selF = roots1d.selectMaxFrozen(xg, zb, _frozenFactory(φb, c0))
    selL = roots1d.selectMax(xg, zb)
    check('selectMaxFrozen: both crossings pass the equilibrium test', selF['nEq'] == 2 and not selF['fallback'],
          f"-> nEq={selF['nEq']}, nCand={selF['nCand']}")
    check('selectMaxFrozen: payoff dominance picks the upper equilibrium', np.isclose(selF['x'], downB[1], atol = 2e-2),
          f"-> frozen {selF['x']:.5f}, oracle {downB[1]:.5f}")
    check('selectMax (legacy) picks the lower one here, so the test discriminates', np.isclose(selL['x'], downB[0], atol = 2e-2),
          f"-> legacy {selL['x']:.5f}")
    # the own value inherits the crossing's O(h²) location error at FIRST order, through the state the
    # candidate pins (dW_c(τ_c)/dτ_c = c·τ_c here), so it ranks well-separated candidates and no more
    check("selectMaxFrozen: the selected equilibrium's own objective matches the oracle to the crossing's location error",
          np.isclose(selF['W'], valB[1], rtol = 1e-3, atol = 1e-8), f"-> {selF['W']:.8f} vs {valB[1]:.8f}")
    selLow = roots1d.selectMaxFrozen(xg, zb, _frozenFactory(φb, c0), select = 'lowest')
    check("selectMaxFrozen: select = 'lowest' picks the lower equilibrium", np.isclose(selLow['x'], downB[0], atol = 2e-2))
    # 9c. a steeper tilt (λ ≈ 0.85): only the lower crossing survives at its own state; both rules agree
    φc, dφc, zc, rootsC, downC = _case(eps - 0.0025)
    if downC.size == 2:
        eqC, valC, refC = _bruteEquilibria(φc, dφc, c0, downC)
        selFc = roots1d.selectMaxFrozen(xg, zc, _frozenFactory(φc, c0))
        check('selectMaxFrozen: with the upper crossing not an equilibrium at its own state, nEq == 1 and the lower is chosen',
              selFc['nEq'] == int(eqC.sum()) == 1 and np.isclose(selFc['x'], downC[int(np.argmax(eqC))], atol = 2e-2),
              f"-> oracle eq={eqC}, nEq={selFc['nEq']}, x={selFc['x']:.5f}")
    # 9d. matrix input: the same column twice plus a NaN-headed copy -> identical per-column answers
    Zm = np.stack([zb, zb, zb], axis = 1)
    Zm[:5, 2] = np.nan
    def frozenM(cand):
        W = _frozenFactory(φb, c0)(cand)
        W[:, :5, 2] = np.nan
        return W
    selM = roots1d.selectMaxFrozen(xg, Zm, frozenM)
    check('selectMaxFrozen: matrix columns reproduce the scalar call and survive a NaN head',
          np.allclose(selM['x'], selF['x']) and np.array_equal(selM['nEq'], [2, 2, 2]),
          f"-> x={selM['x']}, nEq={selM['nEq']}, fallback={selM['fallback']}")

# 9e. no candidate is an equilibrium at its own state: fallback to the legacy choice, flagged.
# W(τ; a) = (c/2)(τ - a)², a(τ) = 2τ - 0.5: z = c(τ - a(τ)) = -c(τ - 0.5), a downward crossing at 0.5
# that is a MINIMUM of its own frozen objective; neither corner is a best response at its own a either.
cF = 2.0
zF = -cF*(xg - 0.5)
def frozenF(cand):
    K, Nc = cand.shape
    W = np.full((K, xg.size, Nc), np.nan)
    for k in range(K):
        for j in range(Nc):
            if np.isfinite(cand[k, j]):
                a = 2*cand[k, j] - 0.5
                W[k, :, j] = 0.5*cF*(xg - a)**2
    return W
selN = roots1d.selectMaxFrozen(xg, zF, frozenF)
selNL = roots1d.selectMax(xg, zF)
check('selectMaxFrozen: no equilibrium -> fallback flagged and the legacy choice returned',
      selN['fallback'] and selN['nEq'] == 0 and selN['nCand'] == 3 and selN['x'] == selNL['x'] and np.isnan(selN['W']),
      f"-> nCand={selN['nCand']}, nEq={selN['nEq']}, x={selN['x']:.4f} (legacy {selNL['x']:.4f})")

# 9f. a corner equilibrium: z < 0 throughout, and the frozen objective at the lower corner's own state
# is decreasing -> l is the unique equilibrium, atBound
zC = -1.0 - xg
frozenC = lambda cand: np.where(np.isfinite(cand)[:, None, :], -(xg[None, :, None]*(1 + cand[:, None, :])), np.nan)
selC = roots1d.selectMaxFrozen(xg, zC, frozenC)
check('selectMaxFrozen: corner equilibrium returned as a corner', selC['atBound'] and selC['x'] == xg[0]
      and selC['nEq'] == 1 and selC['nCand'] == 2, f"-> x={selC['x']}, nEq={selC['nEq']}")

# 9g. the ND wrapper: two states through CartesianGrid, τ first (the fixed-state case of 9a)
from gridsearch import CartesianGrid
gND = CartesianGrid(τ = xg, s = np.array([0., 1.]))
zND = np.stack([zFixed]*2, axis = 1).reshape(-1)                                 # (M*2,) C-order, τ first
selND = roots1d.selectMaxFrozenND(gND, zND, 'τ', _frozenFactory(φa, 0.0))
check('selectMaxFrozenND: state-shaped output, both columns equal to the 1-d call',
      selND['x'].shape == (2,) and np.allclose(selND['x'], selFixed['x']) and selND['nEq'].shape == (2,)
      and np.array_equal(selND['nEq'], [1, 1]), f"-> x={selND['x']}, nEq={selND['nEq']}")
check('selectMaxFrozenND: nEqRaw and nMerged come back in the state shape, nEqRaw - nMerged == nEq',
      'nEqRaw' in selND and 'nMerged' in selND and selND['nEqRaw'].shape == (2,) and selND['nMerged'].shape == (2,)
      and np.array_equal(selND['nEqRaw'] - selND['nMerged'], selND['nEq']),
      f"-> nEqRaw={selND.get('nEqRaw')}, nMerged={selND.get('nMerged')}")

# 9h. interpAlong and _quadAt: exact on a quadratic, NaN-safe
Yq = (xg**2)[:, None] * np.array([[1.0, 2.0]])
cq = np.array([[0.1, np.nan], [0.5, 0.7]])
qa = roots1d._quadAt(xg, np.stack([Yq, Yq]), cq)
check('_quadAt reproduces a quadratic exactly and passes NaN through',
      np.allclose(qa[np.isfinite(cq)], (cq**2 * np.array([[1.0, 2.0]]))[np.isfinite(cq)]) and np.isnan(qa[0, 1]))
la = roots1d.interpAlong(xg, xg[:, None]*np.array([[1.0, -1.0]]), cq)
check('interpAlong is exact on a linear profile and passes NaN through',
      np.allclose(la[np.isfinite(cq)], (cq*np.array([[1.0, -1.0]]))[np.isfinite(cq)]) and np.isnan(la[0, 1]))

# ---- 9i-9l. The one-cell form of the test and the merge (eq:equilibriumTest). The node maximising a
# candidate's own objective within one cell passes it only where its value cannot be read precisely: an
# interior crossing whose three-node stencil touches an infeasible node (_quadAt's linear fallback).
# Passing candidates within one cell of each other are one equilibrium, represented by the crossing.
cell = xg[1] - xg[0]

# 9i (R1). A lower corner 1.5 cells below a crossing. W(τ; a) = φ(τ) + c·τ·a - G·a, φ = -(τ - m)²/2:
# z = m - (1 - c)τ crosses down at m/(1 - c) = x[0] + 1.5 cells; the corner's own objective peaks at
# m + c·x[0], nearest the adjacent node; the crossing's peaks at the crossing. The level -G·a ranks the
# corner's own value first, so a rule that let the corner pass (a one-cell form at a corner) selects it.
cR, mR, GR = 0.4, 0.021, 0.1
φR = lambda τ: -0.5*(τ - mR)**2
zR = mR - (1 - cR)*xg
frozenR = lambda cand: _frozenFactory(φR, cR)(cand) - GR*cand[:, None, :]
xR = mR/(1 - cR)
W0R = frozenR(np.array([[xg[0]]]))[0, :, 0]                      # the corner's own objective
check('9i premise: the corner\'s own objective peaks at the adjacent node, above the corner by more than the '
      'slack, and the crossing sits 1.5 cells above the corner',
      int(np.argmax(W0R)) == 1 and W0R[1] - W0R[0] > 1e-6 and np.isclose(xR, xg[0] + 1.5*cell, atol = 1e-12),
      f'-> argmax node {int(np.argmax(W0R))}, gain {W0R[1] - W0R[0]:.2e}, crossing {xR:.6f}')
selR = roots1d.selectMaxFrozen(xg, zR, frozenR)
check('selectMaxFrozen: a corner whose own objective peaks at the adjacent node fails; the crossing 1.5 cells '
      'away is the one equilibrium',
      selR['nEq'] == 1 and selR.get('nEqRaw') == 1 and selR.get('nMerged') == 0 and not selR['atBound']
      and not selR['fallback'] and np.isclose(selR['x'], xR, atol = 1e-12),
      f"-> nEq={selR['nEq']}, nEqRaw={selR.get('nEqRaw')}, x={selR['x']:.6f} (crossing {xR:.6f}), atBound={selR['atBound']}")

# 9j (R2). The one-cell form kept where it belongs: nodes below 0.07 infeasible, c = -2, the crossing at
# 0.073, 0.3 cells above the first feasible node, so its stencil (nodes 4-6) touches a NaN node and its
# value is read linearly, below the node maximum. The first feasible node's own objective peaks at 0.079,
# nearest the next node, so that endpoint fails.
cJ, mJ = -2.0, 0.219
φJ = lambda τ: -0.5*(τ - mJ)**2
holeJ = xg < 0.0695
zJ = np.where(holeJ, np.nan, mJ - (1 - cJ)*xg)
def frozenJ(cand):
    W = _frozenFactory(φJ, cJ)(cand)
    W[:, holeJ, :] = np.nan
    return W
xJ = mJ/(1 - cJ)
WJ = frozenJ(np.array([[xJ]]))
linJ = float(roots1d._quadAt(xg, WJ, np.array([[xJ]]))[0, 0])
check('9j premise: the crossing\'s stencil touches the infeasible node, and its linear reading falls below its '
      'own node maximum (one cell away) by more than the slack',
      roots1d._stencilFallback(xg, WJ, np.array([[xJ]]))[0, 0] and np.nanmax(WJ) - linJ > 1e-6
      and abs(xg[np.nanargmax(WJ[0, :, 0])] - xJ) <= cell,
      f'-> shortfall {np.nanmax(WJ) - linJ:.2e}, maximising node {xg[np.nanargmax(WJ[0, :, 0])]:.3f}')
selJ = roots1d.selectMaxFrozen(xg, zJ, frozenJ)
check('selectMaxFrozen: an interior crossing next to an infeasible node passes on the one-cell form; the '
      'endpoint beside it does not',
      selJ['nEq'] == 1 and selJ.get('nEqRaw') == 1 and not selJ['atBound'] and not selJ['fallback']
      and np.isclose(selJ['x'], xJ, atol = 1e-12),
      f"-> nEq={selJ['nEq']}, nEqRaw={selJ.get('nEqRaw')}, x={selJ['x']:.6f} (crossing {xJ:.6f})")

# 9k (R3). Two crossings 2/3 of a cell apart, both equilibria. f = 1 except -0.5 at x = 0.51: down at
# 0.5067, up at 0.5133. W(τ; a) = F(τ) - c(a)(τ - a)²/2 + G·a with F = ∫f is consistent with f for any
# c(a) (∂W/∂τ at a = τ is f): c = 1e4 near the pair peaks each crossing's own objective sharply at
# itself, c = -1e4 at the endpoints makes theirs convex, so they fail. G = 1 ranks the upper crossing's
# own value first, so the representative is chosen by value, not by order.
fP = np.ones_like(xg)
fP[49] = -0.5
FP = roots1d.cumtrapzColumns(xg, fP[:, None])[:, 0]
def frozenP(cand):
    K, Nc = cand.shape
    W = np.full((K, xg.size, Nc), np.nan)
    for k in range(K):
        for j in range(Nc):
            a = cand[k, j]
            if np.isfinite(a):
                c = 1e4 if abs(a - 0.51) < 0.05 else -1e4
                W[k, :, j] = FP - 0.5*c*(xg - a)**2 + 1.0*a
    return W
rootsP = roots1d.allRoots(xg, fP)
selP = roots1d.selectMaxFrozen(xg, fP, frozenP)
check('selectMaxFrozen: two crossings within one cell, both passing, are one equilibrium represented by the '
      'one with the higher own objective',
      rootsP.size == 2 and rootsP[1] - rootsP[0] < cell and selP['nCand'] == 4 and selP.get('nEqRaw') == 2
      and selP.get('nMerged') == 1 and selP['nEq'] == 1 and np.isclose(selP['x'], rootsP[1], atol = 1e-12)
      and not selP['atBound'] and not selP['fallback'],
      f"-> crossings {rootsP}, nEqRaw={selP.get('nEqRaw')}, nMerged={selP.get('nMerged')}, nEq={selP['nEq']}, x={selP['x']:.6f}")

# 9l. A corner and a crossing within one cell, both passing: the corner is dropped even though its own
# value is the higher. 9j's infeasible head with c = 0 and the crossing at 0.073: the endpoint at 0.07 is
# its own objective's maximising node (it passes on value), the crossing passes on the one-cell form.
mK = 0.073
zK = np.where(holeJ, np.nan, mK - xg)
def frozenK(cand):
    W = _frozenFactory(lambda τ: -0.5*(τ - mK)**2, 0.0)(cand)
    W[:, holeJ, :] = np.nan
    return W
selK = roots1d.selectMaxFrozen(xg, zK, frozenK)
WK = frozenK(np.array([[0.07]]))[0, :, 0]
check('selectMaxFrozen: a corner within one cell of a passing crossing is absorbed by it, whatever their own '
      'values', selK.get('nEqRaw') == 2 and selK.get('nMerged') == 1 and selK['nEq'] == 1 and not selK['atBound']
      and np.isclose(selK['x'], mK, atol = 1e-12) and np.nanmax(WK) > selK['W'],
      f"-> nEqRaw={selK.get('nEqRaw')}, nEq={selK['nEq']}, x={selK['x']:.6f}, own value {selK['W']:.3e} below the "
      f"corner's {np.nanmax(WK):.3e}")

# 9m. The node form: a crossing with a full stencil, a thousandth of a cell below node 50, whose own
# objective -(τ - P(a))²/2 peaks a hundredth of a cell above it, beyond the node -- the second-order gap
# between a crossing located on f's interpolant and its frozen objective's discrete peak, which the headline
# instances show at crossings within 0.02 cells of a node. P(a) = c + 0.01·cell + (a - c)/2 puts the
# endpoints' own peaks far inside, so they fail. The node beats the crossing's exact value by several slacks.
def _peakFactory(c0, off):
    P = lambda a: c0 + off + 0.5*(a - c0)
    def frozen(cand):
        K, Nc = cand.shape
        W = np.full((K, xg.size, Nc), np.nan)
        for k in range(K):
            for j in range(Nc):
                if np.isfinite(cand[k, j]):
                    W[k, :, j] = -0.5*(xg - P(cand[k, j]))**2
        return W
    return frozen
cM = xg[50] - 0.001*cell
selM = roots1d.selectMaxFrozen(xg, cM - xg, _peakFactory(cM, 0.01*cell))
WM = _peakFactory(cM, 0.01*cell)(np.array([[cM]]))[0, :, 0]
gapM = (WM.max() - (-0.5*(0.01*cell)**2))/(1e-9*(abs(WM.max()) + WM.max() - WM.min()))
check('selectMaxFrozen: a crossing a hair below a node whose own objective peaks just beyond that node passes '
      '(its nearest node attains the maximum)',
      int(np.argmax(WM)) == 50 and gapM > 2 and selM['nEq'] == 1 and selM.get('nEqRaw') == 1
      and not selM['fallback'] and not selM['atBound'] and np.isclose(selM['x'], cM, atol = 1e-12),
      f"-> node beats the crossing's value by {gapM:.1f}x the slack; nEq={selM['nEq']}, fallback={selM['fallback']}, "
      f"x={selM['x']:.6f}")

# 9n. ... but not when the peak is beyond the farther node of its cell: crossing 0.2 cells above node 50,
# own peak 0.7 cells above it, so the maximising node is node 51, 0.8 cells away -- within the one-cell form
# that full-stencil crossings do not get. No candidate passes; the column falls back, flagged.
cN = xg[50] + 0.2*cell
selN2 = roots1d.selectMaxFrozen(xg, cN - xg, _peakFactory(cN, 0.7*cell))
check('selectMaxFrozen: a full-stencil crossing whose own objective peaks at the farther node of its cell is not '
      'an equilibrium', selN2.get('nEqRaw') == 0 and selN2['nEq'] == 0 and selN2['fallback'],
      f"-> nEqRaw={selN2.get('nEqRaw')}, nEq={selN2['nEq']}, fallback={selN2['fallback']}")

report()
