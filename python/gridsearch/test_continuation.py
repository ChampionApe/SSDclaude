r""" continuation.py -- the anchored parameter march (marchGrid) and its extrapolation.

Run:  .venv\Scripts\python.exe python\gridsearch\test_continuation.py

The solves here are fake by construction: each `solve` records the starting point it was handed, so the
checks are about the *quality of the warm start* and the *recovery from failure*, which is the whole
content of the module. A real solve would hide both behind its own convergence.
"""
import numpy as np
from gridsearch import continuation
from gridsearch.continuation import marchGrid, extrapolateX

from gridsearch.testing import check, report

def _raises(fn, exc):
    try:
        fn()
    except exc:
        return True
    return False

# ---- 1. extrapolateX: exactness, degree fallback, and the near-duplicate node guard ------------------
# The polynomial through the last degree+1 points must be reproduced exactly, componentwise, since that
# is the only claim the docstring makes. A linear path is reproduced by degree 1; a quadratic one is not.
hist = [(0.5, np.array([1.0, -2.0])), (0.6, np.array([1.2, -2.4]))]      # x = (2v, -4v)
x0, src = extrapolateX(hist, 0.7, degree = 1)
check('degree-1 extrapolation is exact on a linear path',
      np.allclose(x0, [1.4, -2.8]) and src == 'extrap', f'-> {x0}')
check('extrapolation runs backwards too (the left half of the march)',
      np.allclose(extrapolateX(hist, 0.4, degree = 1)[0], [0.8, -1.6]))
quad = [(1.0, np.array([1.0])), (2.0, np.array([4.0])), (3.0, np.array([9.0]))]   # x = v^2
check('degree 2 is exact on a quadratic path where degree 1 is not',
      np.allclose(extrapolateX(quad, 4.0, degree = 2)[0], 16.0)
      and not np.allclose(extrapolateX(quad, 4.0, degree = 1)[0], 16.0),
      '-> deg2={:.4f}, deg1={:.4f}'.format(float(extrapolateX(quad, 4.0, 2)[0][0]),
                                           float(extrapolateX(quad, 4.0, 1)[0][0])))
single = extrapolateX(hist[:1], 0.7, degree = 1)
check('a single prior solve degrades to carry, not to an error',
      single[1] == 'carry' and np.allclose(single[0], hist[0][1]), f'-> {single[0]}')
check('empty history returns no starting point', extrapolateX([], 0.7)[0] is None)
# Step-halving can place two nodes arbitrarily close; the Vandermonde system is then singular and the
# extrapolation must decline rather than return garbage.
close = [(0.5, np.array([1.0])), (0.5 + 1e-14, np.array([1.0]))]
check('near-duplicate nodes fall back to carry instead of solving a singular system',
      extrapolateX(close, 0.7, degree = 1)[1] == 'carry')

# ---- 2. visit order: anchored and bidirectional ------------------------------------------------------
grid = np.arange(0.5, 2.01, 0.5)                      # 0.5 1.0 1.5 2.0
seen = []
def solveOK(v, x0):
    seen.append(v)
    return {'x': np.array([2*v])}
out = marchGrid(grid, solveOK, anchor = 1.0)
check('the anchor is solved first', seen[0] == 1.0, f'-> order {seen}')
check('the march runs outward in both directions from the anchor',
      seen == [1.0, 1.5, 2.0, 0.5], f'-> order {seen}')
check('every requested value is solved', sorted(r['value'] for r in out['records']) == sorted(grid))
check('no failures on a solvable grid', out['failures'] == [])
check('history is returned sorted by value',
      [p[0] for p in out['history']] == sorted(p[0] for p in out['history']))
seen.clear()
marchGrid(grid, solveOK)
check('anchor=None is a plain left-to-right pass', seen == [0.5, 1.0, 1.5, 2.0], f'-> order {seen}')
check('a non-increasing grid is rejected rather than silently sorted',
      _raises(lambda: marchGrid([1.0, 0.5], solveOK), ValueError))

# ---- 3. the two directions must not share a history --------------------------------------------------
# Extrapolating leftward from points collected on the right would step the wrong way. Anchor at 1.0 on a
# path x = 10*v: the first left point (0.5) must be seeded from the anchor alone, i.e. by 'carry'.
starts = {}
def solveLinear(v, x0):
    starts[v] = np.asarray(x0, dtype = float).copy()
    return {'x': np.array([10.0*v])}
marchGrid(np.array([0.5, 0.75, 1.0, 1.25, 1.5]), solveLinear, anchor = 1.0)
check('the first point of each direction is seeded by carry from the anchor',
      np.allclose(starts[1.25], 10.0) and np.allclose(starts[0.75], 10.0),
      '-> right {:.3f}, left {:.3f}'.format(float(starts[1.25][0]), float(starts[0.75][0])))
check('the second point of each direction is extrapolated, and exactly so on a linear path',
      np.allclose(starts[1.5], 15.0) and np.allclose(starts[0.5], 5.0),
      '-> right {:.3f} (want 15), left {:.3f} (want 5)'.format(float(starts[1.5][0]),
                                                               float(starts[0.5][0])))

# ---- 4. x0 for the anchor, and a failing anchor -------------------------------------------------------
starts.clear()
marchGrid(grid, solveLinear, x0 = np.array([99.0]), anchor = 1.0)
check("the caller's x0 seeds the anchor and nothing else", np.allclose(starts[1.0], 99.0))
check('a failing anchor raises -- the march has no starting point',
      _raises(lambda: marchGrid(grid, lambda v, x0: (_ for _ in ()).throw(RuntimeError('no')),
                                anchor = 1.0), RuntimeError))

# ---- 5. failure recovery: the retry ladder, then step-halving -----------------------------------------
# A solver that only converges when handed a starting point within `reach` of the answer. With reach
# small enough that a full grid step overshoots, the march must insert intermediate values to arrive.
def stiff(reach, log = None):
    def solve(v, x0):
        target = np.array([np.exp(v)])              # a genuinely curved path, so degree-1 overshoots
        if log is not None:
            log.append(v)
        if x0 is None:                              # the anchor, with nothing to extrapolate from
            return {'x': target}
        if abs(float(np.asarray(x0)[0]) - float(target[0])) > reach:
            raise RuntimeError(f'no convergence at {v} from {float(np.asarray(x0)[0]):.4f}')
        return {'x': target}
    return solve

g = np.arange(1.0, 3.01, 0.5)
out = marchGrid(g, stiff(0.35), anchor = 1.0, maxHalvings = 4)
solvedReq = sorted(r['value'] for r in out['records'] if r['ok'] and r['requested'])
inserted = [r['value'] for r in out['records'] if r['ok'] and not r['requested']]
check('step-halving carries the march through values a direct step cannot reach',
      solvedReq == sorted(g), f'-> solved {solvedReq}')
check('intermediate values were genuinely needed and are flagged requested=False',
      len(inserted) > 0 and all(v not in list(g) for v in inserted), f'-> inserted {inserted}')
check('intermediate solves are kept in the history, not discarded',
      all(any(np.isclose(p[0], v) for p in out['history']) for v in inserted))
check('halvings are counted in the record',
      max(r['halvings'] for r in out['records']) > 0,
      '-> max halvings {}'.format(max(r['halvings'] for r in out['records'])))

# The retry ladder: 'carry' must be tried after 'extrap' fails, before any halving. A solver accepting
# only the previous x *exactly* must therefore get through the whole grid with no intermediates at all.
# The returned path has to vary with v, or extrapolation would coincide with carry and never be rejected.
# Anchored at the leftmost value so the march is one-directional -- this fake solver carries state between
# calls, which a bidirectional march would (correctly) invalidate when it returns to the anchor.
last = {}
def carryOnly(v, x0):
    if x0 is not None and not np.allclose(np.asarray(x0), last['x']):
        raise RuntimeError('only the carried point is accepted')
    last['x'] = np.array([10.0*v])
    return {'x': last['x']}
out = marchGrid(np.arange(0.5, 2.51, 0.5), carryOnly, anchor = 0.5)
solvedReq = sorted(r['value'] for r in out['records'] if r['ok'])
check("'carry' is tried after 'extrap' fails, and rescues the point without halving",
      len(solvedReq) == 5 and all(r['halvings'] == 0 for r in out['records']),
      '-> sources {}'.format([r['x0Source'] for r in out['records']]))
check('the extrapolated start was genuinely rejected first, so carry is doing the work',
      any(not r['ok'] and r['x0Source'] == 'extrap' for r in out['records'])
      and all(r['x0Source'] in ('default', 'carry') for r in out['records'] if r['ok']))

# ---- 6. a genuinely unsolvable value is recorded, and the sweep continues past it ---------------------
def failsAt(bad):
    def solve(v, x0):
        if np.isclose(v, bad):
            raise RuntimeError(f'unsolvable at {v}')
        return {'x': np.array([2*v])}
    return solve

out = marchGrid(np.arange(0.5, 2.51, 0.5), failsAt(1.5), anchor = 1.0, maxHalvings = 1)
check('an unsolvable value is recorded as a failure rather than raised',
      any(np.isclose(r['value'], 1.5) for r in out['failures']))
check('the march continues past a failed value by default',
      any(np.isclose(r['value'], 2.0) and r['ok'] for r in out['records'])
      and any(np.isclose(r['value'], 2.5) and r['ok'] for r in out['records']),
      '-> solved {}'.format(sorted(r['value'] for r in out['records'] if r['ok'])))
out = marchGrid(np.arange(0.5, 2.51, 0.5), failsAt(1.5), anchor = 1.0, maxHalvings = 1, stopOnFail = True)
check('stopOnFail abandons the failing direction but not the other one',
      not any(np.isclose(r['value'], 2.0) and r['ok'] for r in out['records'])
      and any(np.isclose(r['value'], 0.5) and r['ok'] for r in out['records']),
      '-> solved {}'.format(sorted(r['value'] for r in out['records'] if r['ok'])))
check('minStep stops halving from chasing an unsolvable point forever',
      len(marchGrid(np.array([1.0, 1.5]), failsAt(1.5), anchor = 1.0,
                    maxHalvings = 50, minStep = 1e-3)['records']) < 40,
      '-> {} attempts'.format(len(marchGrid(np.array([1.0, 1.5]), failsAt(1.5), anchor = 1.0,
                                            maxHalvings = 50, minStep = 1e-3)['records'])))

# ---- 7. onPoint fires for every attempt, in visit order ----------------------------------------------
# This is the persistence hook, so what matters is that nothing is silently skipped -- a point written
# nowhere is a point re-solved on the next run.
fired = []
out = marchGrid(np.arange(0.5, 2.51, 0.5), failsAt(1.5), anchor = 1.0, maxHalvings = 1,
                onPoint = lambda r: fired.append((r['value'], r['ok'])))
check('onPoint fires once per attempt, successes and failures alike',
      len(fired) == len(out['records'])
      and [f[0] for f in fired] == [r['value'] for r in out['records']])
check('onPoint sees failures too, not just the points worth keeping',
      any(not f[1] for f in fired))

report()
