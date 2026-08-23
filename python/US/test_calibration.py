r""" model.py's calibrate -- the nested fixed point over (beta, omega) (docs eq:calibration).

Run:  .venv\Scripts\python.exe python\US\test_calibration.py

Two targets here, not the Argentina models' four: the informal eta_0/X_0 are gone with the type that had
a mass, and the savings-rate target is replaced by the 30-year interest rate R_{t0}. The savings rate is
still reported, just not targeted.

What is checked:

  1. Bounded<->unbounded reparameterization round-trips.
  2. LOG calibration (vector X) converges and hits both targets at db['t0'].
  3. db holds the converged parameters afterwards, and re-running does not move them.
  4. commonX calibration hits a THIRD target, average hours, without a third search dimension: X is
     recovered in closed form after the root and the re-solve reproduces the same (R, tau). The point of
     the check is that this is an identity, not a numerical coincidence.
  5. Failure restores db (forced via tol=0).
  6. beta is not capped at 1 -- guards against reintroducing that bound (see model.py's _calBounds).
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelUS

from gridsearch.testing import check, report


def newModel(commonX = False, **over):
    return ModelUS(pars = testmod.pars | over, commonX = commonX, **testmod.kwargs)


# ---- 1. reparameterization round-trip
m = newModel()
pars0 = m.calibrationPars
back = m._calFromX(m._calToX(pars0))
check('_calToX/_calFromX round-trip', all(np.isclose(back[k], pars0[k], rtol = 1e-12) for k in m._calPars))
check('_calFromX maps any real to a strictly positive parameter',
      all(v > 0 for v in m._calFromX(np.array([-40., 12.])).values()))
check('calibration searches over (beta, omega) only', m._calPars == ('β', 'ω'))

# ---- 2. LOG calibration, vector X
cal = m.calibrate(preferences = 'LOG')
t0 = m.db['t'][m.db['t0']]
rep = cal['report']
check('calibrate returns the expected keys', set(cal) == {'pars', 'x', 'residual', 'report', 'scipyRes'})
check('both residuals below tol', np.max(np.abs(cal['residual'])) < 1e-8,
      '-> max|residual|={:.2e}'.format(np.max(np.abs(cal['residual']))))
check('interest-rate target hit at t0', np.isclose(rep['R'], m.db['R0'], rtol = 1e-7),
      '-> R={:.6f} vs target {:.6f}'.format(rep['R'], m.db['R0']))
check('tax-rate target hit at t0', np.isclose(rep['τ'], m.db['τ0'], rtol = 1e-7),
      '-> tau={:.6f} vs target {:.6f}'.format(rep['τ'], m.db['τ0']))
check('db holds the converged parameters afterwards',
      all(np.isclose(m.calibrationPars[k], cal['pars'][k], rtol = 1e-10) for k in m._calPars),
      '-> ' + ', '.join('{}={:.5f}'.format(k, cal['pars'][k]) for k in m._calPars))
check('the savings rate is reported but NOT targeted (it is free to land anywhere)',
      np.isfinite(rep['sr']), '-> savings rate={:.4f}'.format(rep['sr']))

# ---- 3. idempotence
cal2 = m.calibrate(preferences = 'LOG')
check('re-calibrating from the converged point does not move the parameters',
      all(np.isclose(cal2['pars'][k], cal['pars'][k], rtol = 1e-6) for k in m._calPars),
      '-> ' + ', '.join('{}: {:.6f} -> {:.6f}'.format(k, cal['pars'][k], cal2['pars'][k]) for k in m._calPars))

# ---- 4. commonX: a third target, but no third dimension
mc = newModel(commonX = True)
calc = mc.calibrate(preferences = 'LOG')
repc = calc['report']
check('[commonX] interest-rate target hit', np.isclose(repc['R'], mc.db['R0'], rtol = 1e-7),
      '-> R={:.6f}'.format(repc['R']))
check('[commonX] tax-rate target hit', np.isclose(repc['τ'], mc.db['τ0'], rtol = 1e-7),
      '-> tau={:.6f}'.format(repc['τ']))
check('[commonX] average-hours target hit', np.isclose(repc['hbar'], mc.db['h0'], rtol = 1e-7),
      '-> hbar={:.6f} vs target {:.6f}'.format(repc['hbar'], mc.db['h0']))
check('[commonX] X is reported alongside (beta, omega)', 'X' in calc['pars'],
      '-> X={:.5f}'.format(calc['pars'].get('X', np.nan)))
check('[commonX] the search itself stayed 2-dimensional', len(calc['x']) == 2)
check('[commonX] db ends up with a genuinely common X',
      np.allclose(mc.db['Xi'].values, mc.db['Xi'].values[:, :1]))
check('[commonX] Gamma_h is still 1 after X is applied', np.isclose(mc.B.Γh(t0), 1, rtol = 1e-10),
      '-> Gamma_h={:.12f}'.format(mc.B.Γh(t0)))
# The workweek target is only meaningful because hbar has a level here. Under vector X it does not:
# the two calibrations should agree on tau and R while disagreeing on hbar.
check('[commonX] vector-X and common-X agree on tau (policy ignores the hours unit)',
      np.isclose(repc['τ'], rep['τ'], rtol = 1e-6),
      '-> {:.6f} vs {:.6f}'.format(repc['τ'], rep['τ']))
check('[commonX] but the two disagree on hbar, which only common-X pins',
      not np.isclose(repc['hbar'], rep['hbar'], rtol = 1e-3),
      '-> commonX={:.5f} vs vectorX={:.5f}'.format(repc['hbar'], rep['hbar']))

# ---- 5. failure restores db
def dbSignature(mm):
    return (mm.simpleβinv(), float(mm.db['ω'].xs(t0)), float(np.asarray(mm.db['Γh'])[0]))

sig = dbSignature(m)
try:
    m.calibrate(preferences = 'LOG', tol = 0.)     # unreachable tolerance -> _checkConverged raises
    check('forced failure raises', False)
except RuntimeError:
    check('forced failure raises', True)
check('db is restored after a failed calibration', np.allclose(dbSignature(m), sig, rtol = 1e-12),
      '-> {} vs {}'.format(dbSignature(m), sig))

# ---- 6. beta is not capped at 1
check('beta has no upper bound in _calBounds', all(np.isinf(u) for (l, u) in m._calBounds.values()))
check('_calFromX can return beta > 1', m._calFromX(np.array([1.0, 0.]))['β'] > 1,
      '-> beta={:.4f}'.format(m._calFromX(np.array([1.0, 0.]))['β']))

# ---- 7. commonX without the hours target must fail loudly rather than silently skip it
mNoH = ModelUS(pars = {k: v for k, v in testmod.pars.items() if k != 'h0'},
               commonX = True, **testmod.kwargs)
try:
    mNoH.calibrate(preferences = 'LOG')
    check('commonX without db[h0] raises', False)
except KeyError:
    check('commonX without db[h0] raises', True)

report()
