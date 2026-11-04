r""" base.py's cacheParams() must change speed and nothing else.

Run:  .venv\Scripts\python.exe python\informalAnalytical\test_cacheParams.py

The cache exists because ~43% of a political-FOC grid evaluation is pandas db lookups (flat in grid
size -- pure per-call overhead), but it carries a real hazard: model.py rewrites whole db symbols during
calibration, and a cache that outlived such a write would return stale parameters *silently*. The
block-scoped design is what rules that out, so the checks below are mostly about scope and invalidation,
not about speed.
"""
import os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod

m = testmod.mLOG
LOG, BG = m.LOG, m.BG
th, eps = m.db['θ'].values, m.db['eps'].values
t, tLag = m.db['t'][5], m.db['t'][4]
g = np.linspace(1e-4, 1 - 1e-4, 101)

from gridsearch.testing import check, report

def foc():
    return LOG.focGrid(LOG.stateGrid(g, t, th[5], tLag, False, 0.15, th[6]), t, th[5], eps[5], False)

# ---- 1. the cache changes nothing about the numbers
zPlain = foc()
with BG.cacheParams():
    zCached = foc()
    zCached2 = foc()                      # second call inside the block is the one that hits the cache
check('cached FOC == uncached FOC (bitwise)', np.array_equal(zPlain, zCached))
check('repeat call inside block identical', np.array_equal(zCached, zCached2))
check('cache cleared on exit', BG._cache is None)
check('uncached again after block', np.array_equal(foc(), zPlain))

# ---- 2. two years inside ONE block must not collide (keys carry the resolved year).
# Pick years whose parameters actually differ: only nu varies with t in this calibration, and it is flat
# from index 5 on, so 2 vs 5 is the meaningful pair. Two years sharing every parameter would make this
# check vacuous -- it would pass even against a cache that ignored the year entirely.
iA, iB = 2, 5
run = lambda i: LOG.focGrid(
    LOG.stateGrid(g, m.db['t'][i], th[i], m.db['t'][i-1], False, 0.15, th[i+1]),
    m.db['t'][i], th[i], eps[i], False)
with BG.cacheParams():
    zA, zB = run(iA), run(iB)
zA_ref, zB_ref = run(iA), run(iB)
check('two years in one block: year A correct', np.array_equal(zA, zA_ref))
check('two years in one block: year B correct', np.array_equal(zB, zB_ref))
check('the two years genuinely differ (nu {:.3f} vs {:.3f})'.format(
          m.db['ν'].values[iA], m.db['ν'].values[iB]), not np.array_equal(zA_ref, zB_ref))

# ---- 3. nesting: an inner block reuses the outer cache, only the outermost exit clears
with BG.cacheParams():
    with BG.cacheParams():
        check('nested block reuses cache', BG._cache is not None)
    check('inner exit does NOT clear', BG._cache is not None)
check('outer exit clears', BG._cache is None)

# ---- 4. no stale reads: a db write outside a block is visible immediately
before = BG.get('α', t)
m.db['α'].loc[t] = float(before) * 1.5
check('db write visible outside a block', np.isclose(BG.get('α', t), before * 1.5))
m.db['α'].loc[t] = before
check('restored', np.isclose(BG.get('α', t), before))

# ---- 5. end to end. solveVectorized warm-starts from self.x0['vectorized'] and overwrites it on
# success, so a second run would start from the first run's answer and converge to a slightly different
# point within tolerance -- nothing to do with caching. Clear it so both runs solve the same problem.
def freshSolve():
    m.LOG.x0.pop('vectorized', None)
    m.x0.clear()
    return m.solvePEE_LOG(solver = 'Vectorized')

solA = freshSolve()
with BG.cacheParams(), m.BT.cacheParams(), m.B.cacheParams():
    solB = freshSolve()
d = np.max(np.abs(solA['policy']['τ'].values - solB['policy']['τ'].values))
check('solvePEE_LOG tau bitwise identical under caching', d == 0.0, '-> max|diff|={:.2e}'.format(d))
for k in ('s', 'h', 'Γs'):
    d = np.max(np.abs(solA['report'][k].values - solB['report'][k].values))
    check('  report[{}] bitwise identical'.format(k), d == 0.0, '-> max|diff|={:.2e}'.format(d))

# ---- 6. the two independent LOG solvers still agree (guards the wiring in policy.py, which now runs
# both inside cache blocks). 1.3e-05 at n=101 is the grid resolution, matching the README.
tauV = freshSolve()['policy']['τ'].values
m.LOG.x0.pop('vectorized', None)
tauB = m.LOG.solveBackward(th, eps)['τ'].values
dSolvers = np.max(np.abs(tauV - tauB))
check('solveVectorized == solveBackward to grid resolution', dSolvers < 5e-5,
      '-> max|diff|={:.2e}'.format(dSolvers))

# ---- 7. LOG: the selection among tax candidates at frozen savings shares (num_robustroot.tex,
# eq:candidates/eq:equilibriumTest; policy.LOG.objectiveFrozen). The frozen objective's τ-derivative at the
# shares consistent with the evaluation point is the solver's own z_t (closed form); the rule reproduces the
# integral criterion bitwise wherever one equilibrium exists; the counts reach every solve output.
tIdx = m.db['t']
pos0 = int(m.db['t0'])
hFD = 1e-5
with BG.cacheParams():
    for (tt, tl, terminal, label) in ((tIdx[pos0], tIdx[pos0 - 1], False, 't0'), (tIdx[-1], tIdx[-2], True, 'T')):
        pp = tIdx.get_loc(tt)
        θt, εt = float(th[pp]), float(eps[pp])
        τ1c = 0.2                                     # a fixed continuation τ_{t+1}; ignored at T
        for τc in (0.08, 0.15, 0.30):
            z = float(LOG.focGrid(LOG.stateGrid(np.array([τc]), tt, θt, tl, terminal, τ1c, θt), tt, θt, εt, terminal)[0])
            τg = np.array([τc - hFD, τc, τc + hFD])
            dg = LOG.stateGrid(τg, tt, θt, tl, terminal, τ1c, θt)
            W = LOG.objectiveFrozen(np.array([[τc]]), τg, dg, LOG.focGrid(dg, tt, θt, εt, terminal),
                                    θt, tt, εt, tl, terminal)
            dW = (W[0, 2, 0] - W[0, 0, 0])/(2*hFD)
            check(f'LOG {label}: dW/dτ of the frozen objective at its own shares equals z_t at τ={τc}',
                  abs(dW - z) <= 1e-6*max(1., abs(z)), f'-> {dW:.9f} vs {z:.9f}')
        τg = np.array([0.15 - hFD, 0.15, 0.15 + hFD])
        dg = LOG.stateGrid(τg, tt, θt, tl, terminal, τ1c, θt)
        W2 = LOG.objectiveFrozen(np.array([[0.30]]), τg, dg, LOG.focGrid(dg, tt, θt, εt, terminal),
                                 θt, tt, εt, tl, terminal)
        z15 = float(LOG.focGrid(LOG.stateGrid(np.array([0.15]), tt, θt, tl, terminal, τ1c, θt), tt, θt, εt, terminal)[0])
        check(f'LOG {label}: at shares frozen at another candidate the derivative is a different number',
              abs((W2[0, 2, 0] - W2[0, 0, 0])/(2*hFD) - z15) > 1e-6,
              '-> {:.6f} vs z_t {:.6f}'.format((W2[0, 2, 0] - W2[0, 0, 0])/(2*hFD), z15))

nτ = LOG.GS['PEE']['solGrids']['τ'].size
LOG.selection = 'frozen'
gridF = LOG.solveBackward(th, eps, Δl = nτ, Δu = nτ, update = False)
winF = LOG.solveBackward(th, eps, update = False)
LOG.selection = 'legacy'
gridL = LOG.solveBackward(th, eps, Δl = nτ, Δu = nτ, update = False)
winL = LOG.solveBackward(th, eps, update = False)
LOG.selection = 'frozen'
mult = gridF['multiplicity']
nEqT = np.array([d['nEq'] for d in gridF['diagnostics'].values()])
single = nEqT == 1
check('LOG full grid: counts reported at every period; one equilibrium everywhere, no fallback',
      mult['nEqMax'] == 1 and mult['nFallback'] == 0 and mult['nCandMax'] >= 3 and single.all(), f'-> {mult}')
check('LOG full grid: the rule reproduces the integral criterion bitwise where one equilibrium exists',
      np.array_equal(gridF['τ'].values[single], gridL['τ'].values[single]),
      '-> τ sum {!r} (frozen) vs {!r} (legacy); τ_T={!r}, τ_t0={!r}'.format(
          float(gridF['τ'].sum()), float(gridL['τ'].sum()), float(gridF['τ'].iloc[-1]), float(gridF['τ'].iloc[pos0])))
check('LOG refinement window: same, bitwise', np.array_equal(winF['τ'].values, winL['τ'].values)
      and winL['multiplicity']['nEqMax'] == 0, '-> legacy counts {}'.format(winL['multiplicity']))
x0 = np.full(m.T, float(m.db['τ0']))
fast = LOG.solveVectorized(th, eps, x0 = x0.copy(), update = False)
rob = LOG.solveRobust(th, eps, x0 = x0.copy(), update = False)
check('solveRobust (check=True): the gradient solution is returned bitwise when it is the selected equilibrium',
      np.array_equal(fast['τ'].values, rob['τ'].values) and 'warm start' not in rob['message'],
      f"-> {rob['message']}")
check('solveRobust (check=True) attaches the counts of the full-grid pass',
      rob.get('multiplicity') == mult, f"-> {rob.get('multiplicity')}")
check('solveRobust(check=False) is the gradient solve alone, without counts',
      'multiplicity' not in LOG.solveRobust(th, eps, x0 = x0.copy(), update = False, check = False))
m.LOG.x0.pop('vectorized', None)
out = m.solvePEE_LOG()
check('solvePEE_LOG carries the multiplicity summary', isinstance(out.get('multiplicity'), dict)
      and out['multiplicity']['nEqMax'] == 1, f"-> {out.get('multiplicity')}")
check("solvePEE_LOG(solver='Vectorized') reports no counts (None)",
      m.solvePEE_LOG(solver = 'Vectorized')['multiplicity'] is None)

# ---- 8. the frozen objectives share one anchor per column (toy; LOG and CRRA objectiveFrozen)
# Every candidate's W drops the column-common levels (the young's, the informal retirees') at one node, which
# must be the same node for every candidate or the dropped constants differ and so does the ranking. Toy, one
# formal type: frozen share D(τ_c) = 0.2 - 0.5τ_c, retirees' consumption c = D + τ, column-common part -τ²/2,
# so W(τ; D) = -τ²/2 + u(D + τ), u = ln (LOG, ρ = 1) or c^p/p with p = 1/2 (CRRA, ρ = 2), and the condition is
# NaN where c <= 0. The candidate τ_c = 0.6 has D = -0.1, so it is infeasible below τ = 0.1. Column 0 is
# feasible from τ = 0 (its anchor), where that candidate has no level and must be NaN; column 1 is feasible
# from τ = 0.3, where both candidates are, and both must be the exact W up to one constant, τ_anchor²/2.
import policy as policyMod
from gridsearch import CartesianGrid

class _ToyBG:
    def __init__(self, ρ): self.ρ = ρ
    def get(self, k, t = None): return self.ρ if k == 'ρ' else np.ones(1)
    def B(self, s_, h, t = None): return np.ones_like(s_)
    def Γs(self, B, τ1, θ1, t = None): return np.ones_like(τ1)
    def si_s(self, B, τ1, θ1, Γs, t = None): return (0.2 - 0.5*np.asarray(τ1))[:, None]
    def c2i(self, h, s_, τ, θ, si_s_, t = None): return si_s_ + np.asarray(τ, dtype = float).reshape(-1, 1)

class _Toy:
    ni = 1
    def __init__(self, ρ): self.BG, self.p = _ToyBG(ρ), 1 - 1/ρ
    def _oldFormalWeights(self, t): return np.ones(1)
    def _zFrozen(self, τ, si_s_):
        c = si_s_[:, 0] + τ
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            return -τ + np.where(c > 0, c**(self.p - 1), np.nan)
    def focGrid(self, d, t, θ, ε, terminal): return self._zFrozen(d['τ'], d['si_s_'])      # LOG's callee
    def zAtShares(self, d, parts, θ, si_s_, t): return self._zFrozen(d['τ'], si_s_)       # CRRA's at t < T

τT = np.linspace(0., 1., 2001)
candT = np.array([[0.2, 0.2], [0.6, 0.6]])
lowT = τT < 0.3
for name, ρT in (('LOG', 1.), ('CRRA', 2.)):
    toy, p = _Toy(ρT), 1 - 1/ρT
    u = np.log if p == 0 else (lambda c: c**p/p)
    zT = np.column_stack([-τT + (0.2 + 0.5*τT)**(p - 1)]*2)                     # consistent: c = 0.2 + 0.5τ
    zT[lowT, 1] = np.nan
    if name == 'LOG':
        WT = policyMod.LOG.objectiveFrozen(toy, candT, τT, {'τ': np.repeat(τT, 2)}, zT, 0., 0, 0., 0, False)
    else:
        gT = CartesianGrid(τ = τT, s_ = np.array([1., 2.]))
        dT = {'τ': gT.flat['τ'], 'h': np.ones(gT.flat['τ'].size), 's_': gT.flat['s_']}
        WT = policyMod.CRRA.objectiveFrozen(toy, candT, gT, dT, {}, zT.reshape(-1), 0., 0, 0)
    with np.errstate(divide = 'ignore', invalid = 'ignore'):
        exact = [-τT**2/2 + u(0.2 - 0.5*c + τT) for c in candT[:, 0]]
    gap = max(np.max(np.abs(WT[0, :, 0] - exact[0])),
              *(np.max(np.abs(WT[k, ~lowT, 1] - exact[k][~lowT] - τT[~lowT][0]**2/2)) for k in range(2)))
    check(f'toy, {name}: a candidate infeasible at its column\'s anchor is NaN in that column, the other is not',
          np.isnan(WT[1, :, 0]).all() and np.isfinite(WT[0, :, 0]).all(),
          '-> finite nodes of τ_c = 0.6 in column 0: {}'.format(int(np.isfinite(WT[1, :, 0]).sum())))
    check(f'toy, {name}: candidates feasible at the anchor are the exact W(τ; D) up to one constant per column',
          gap < 1e-5 and np.isnan(WT[:, lowT, 1]).all(), '-> max |W - W_exact - τ_anchor²/2| {:.1e}'.format(gap))

# ---- speed (reported, not asserted -- timings are machine-dependent)
def timeit(fn, r = 100):
    fn()
    s = time.perf_counter()
    for _ in range(r):
        fn()
    return (time.perf_counter() - s) / r * 1e6

def cachedLoop():
    with BG.cacheParams():
        for _ in range(10):
            foc()

tPlain, tCached = timeit(foc), timeit(cachedLoop, r = 20) / 10
print('\nper FOC evaluation:  uncached {:7.1f} us   cached {:7.1f} us   speedup {:.1f}x'.format(
    tPlain, tCached, tPlain / tCached))

report()
