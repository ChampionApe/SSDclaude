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

ok = True
def check(name, cond, extra = ''):
    global ok
    print(('PASS' if cond else 'FAIL') + '  ' + name + ' ' + extra)
    if not cond:
        ok = False

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

print()
print('ALL PASS' if ok else 'SOME FAILURES')
sys.exit(0 if ok else 1)
