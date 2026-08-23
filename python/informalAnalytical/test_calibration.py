r""" model.py's calibrate -- the nested fixed point over (beta, omega, eta0, X0) (docs eq:calibration).

Run:  .venv\Scripts\python.exe python\informalAnalytical\test_calibration.py

What is checked:

  1. Bounded<->unbounded reparameterization round-trips.
  2. LOG calibration converges and hits all four eq:calibration targets at db['t0'].
  3. Idempotent: re-running from the converged point does not move the parameters.
  4. Failure restores db (forced via tol=0).
  5. beta is not capped at 1 -- guards against reintroducing that bound (see model.py's _calBounds).
  6. CRRA calibrates at one rho just below and one just above 1, landing near the LOG parameters. Only
     these two easy points -- rho ~ 0.5/~2 wait for a later, more robust test.
  7. Parameter rewriting mid-calibration does not interact with base.py's cacheParams().
"""
import os, sys
from contextlib import contextmanager
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelInformalAnalytical
from base import Base

from gridsearch.testing import check, report

def newModel(**over):
    return ModelInformalAnalytical(pars = testmod.pars | over, **testmod.kwargs)

# ---- 1. reparameterization round-trip
m = newModel(ρ = 1)
pars0 = m.calibrationPars
back = m._calFromX(m._calToX(pars0))
check('_calToX/_calFromX round-trip', all(np.isclose(back[k], pars0[k], rtol = 1e-12) for k in m._calPars))
check('_calFromX maps any real to a strictly positive parameter',
      all(v > 0 for v in m._calFromX(np.array([-40., 0., 12., 3.])).values()))

# ---- 2. LOG calibration hits all four targets
cal = m.calibrate(preferences = 'LOG')
t0 = m.db['t'][m.db['t0']]
check('calibrate returns the expected keys', set(cal) == {'pars', 'x', 'residual', 'report', 'scipyRes'})
check('all four residuals below tol', np.max(np.abs(cal['residual'])) < 1e-8,
      '-> max|residual|={:.2e}'.format(np.max(np.abs(cal['residual']))))
rep = cal['report']
check('savings-rate target hit at t0', np.isclose(rep['sr'], m.db['s0'], rtol = 1e-7),
      '-> sr={:.6f} vs target {:.6f}'.format(rep['sr'], m.db['s0']))
check('tax-rate target hit at t0', np.isclose(rep['τ'], m.db['τ0'], rtol = 1e-7),
      '-> τ={:.6f} vs target {:.6f}'.format(rep['τ'], m.db['τ0']))
check('eta0 self-consistent with Theta_h(t0)', np.isclose(rep['η0'], cal['pars']['η0'], rtol = 1e-7),
      '-> implied={:.6f}, held={:.6f}'.format(rep['η0'], cal['pars']['η0']))
check('X0 self-consistent with Theta_h(t0)', np.isclose(rep['X0'], cal['pars']['X0'], rtol = 1e-7),
      '-> implied={:.6f}, held={:.6f}'.format(rep['X0'], cal['pars']['X0']))
check('db holds the converged parameters afterwards',
      all(np.isclose(m.calibrationPars[k], cal['pars'][k], rtol = 1e-10) for k in m._calPars),
      '-> ' + ', '.join('{}={:.5f}'.format(k, cal['pars'][k]) for k in m._calPars))

# Theta_h recovered from the solved path must reproduce the h it came from (Base.ΘhFromH is an inverse).
solved = rep['PEE']['report']
check('ΘhFromH inverts Base.h exactly',
      np.isclose(m.B.h(rep['Θh'], solved['s_'].xs(t0), t0), solved['h'].xs(t0), rtol = 1e-12))

# ---- 3. idempotence
cal2 = m.calibrate(preferences = 'LOG')
check('re-calibrating from the converged point does not move the parameters',
      all(np.isclose(cal2['pars'][k], cal['pars'][k], rtol = 1e-6) for k in m._calPars),
      '-> max rel move={:.2e}'.format(max(abs(cal2['pars'][k]/cal['pars'][k]-1) for k in m._calPars)))

# ---- 4. failure restores db
before = dict(m.calibrationPars)
epsBefore = m.db['eps'].values.copy()
raised = False
try:
    m.calibrate(preferences = 'LOG', tol = 0.0)   # unreachable tolerance -> _checkConverged raises
except RuntimeError:
    raised = True
check('an unreachable tol raises rather than returning silently', raised)
check('db parameters restored after a failed calibration',
      all(np.isclose(m.calibrationPars[k], before[k], rtol = 1e-14) for k in m._calPars))
check('db auxiliary parameters (eps) restored too', np.allclose(m.db['eps'].values, epsBefore, rtol = 1e-14))

# ---- 5. beta is not capped at 1 (the bound that made the first version stall)
check('calibrated beta exceeds 1 on this calibration', cal['pars']['β'] > 1,
      '-> β={:.5f}'.format(cal['pars']['β']))
check('no _calBounds entry caps a parameter from above',
      all(np.isinf(u) for _, u in m._calBounds.values()))

# ---- 6. CRRA either side of rho=1, fully warm-started from the *calibrated* LOG model.
# Warm start means both halves: _calSetPars installs LOG's converged (β,ω,η0,X0) into the fresh instance's
# db (so the auxiliary parameters and the very first PEE solve start from the LOG equilibrium), and
# x0=cal['x'] starts the outer root finder at the same point. Without the first half the instance would
# start from test.py's raw guesses (η0=0.20, X0=2.57) even though x0 describes the calibrated ones.
#
# Deliberately only two points, both close to 1, where CRRA should essentially reproduce LOG. Harder
# values (rho ~ 0.5, ~2) are left for a later, more robust test once the solve is tweaked for them.
for ρ in (0.98, 1.02):
    mC = newModel(ρ = ρ)
    mC._calSetPars(cal['pars'])
    calC = mC.calibrate(preferences = 'CRRA', x0 = cal['x'])
    check('CRRA (ρ={}) calibration converges'.format(ρ), np.max(np.abs(calC['residual'])) < 1e-8,
          '-> max|residual|={:.2e}'.format(np.max(np.abs(calC['residual']))))
    check('CRRA (ρ={}) parameters land near the LOG ones'.format(ρ),
          max(abs(calC['pars'][k]/cal['pars'][k]-1) for k in m._calPars) < 0.05,
          '-> ' + ', '.join('{}={:.5f} ({:+.2%})'.format(k, calC['pars'][k], calC['pars'][k]/cal['pars'][k]-1)
                            for k in m._calPars))

# ---- 7. calibrate's parameter rewriting vs. base.py's cacheParams()
# Every cacheParams() block lives inside policy.py's solve methods, i.e. strictly *after* _calSetPars has
# finished writing to db -- so no db write ever happens while a cache is live. Checked rather than
# reasoned, since a stale cache corrupts results silently, which is exactly what the cache was made
# opt-in to avoid.
@contextmanager
def noCache(self):
    yield self

mNo = newModel(ρ = 1)
_orig = Base.cacheParams
Base.cacheParams = noCache
try:
    calNoCache = mNo.calibrate(preferences = 'LOG')
finally:
    Base.cacheParams = _orig
# Agreement to solver tolerance, not bitwise: a root find amplifies last-bit differences into visibly
# different (equally valid) converged points, so bitwise identity is the wrong granularity here.
# test_cacheParams.py checks bitwise identity where it belongs -- a single FOC evaluation.
gap = max(abs(calNoCache['pars'][k]/cal['pars'][k]-1) for k in m._calPars)
check('calibrate agrees with caching disabled', gap < 1e-6,
      '-> max rel diff={:.2e}; real cache staleness would show up here as a gross mismatch'.format(gap))

mF = newModel(ρ = 1)
try:
    mF.calibrate(preferences = 'LOG', tol = 0.0)   # forced failure -> db restore in an except handler
except RuntimeError:
    pass
check('no cache left live after a calibration, including a failed one',
      mF.B._cache is None and mF.BG._cache is None and mF.BT._cache is None,
      '-> cacheParams\' finally unwinds before calibrate\'s db restore runs')

# A cache that survived a db write would be visible as a *changed answer* when the same solve is repeated
# inside one block after parameters move. Drive that directly: solve, rewrite parameters, solve again.
mC = newModel(ρ = 1)
first = mC.calibration_report(mC.calibrationPars, 'LOG')['τ']
bumped = dict(mC.calibrationPars); bumped['β'] = bumped['β']*1.10
second = mC.calibration_report(bumped, 'LOG')['τ']
check('a parameter rewrite between solves genuinely changes the answer (no stale reads)',
      not np.isclose(first, second, rtol = 1e-8),
      '-> τ(t0) {:.6f} -> {:.6f} after β +10%'.format(first, second))


report()
