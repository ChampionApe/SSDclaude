r""" CRRA.solveTerminal (policy.py) -- the terminal-period CRRA politico-economic equilibrium.

Run:  .venv\Scripts\python.exe python\informalAnalytical\test_crraTerminal.py

The sharpest available check is not approximate: at rho=1, Base.B's rho_c=1 makes Bi collapse to the
primitive beta_i regardless of (s_, h) (Rp**0=1), and every consumption-level weight c^{1-1/rho} collapses
to c^0=1 -- so CRRA's terminal FOC is then *exactly* LOG's terminal FOC, state-independent, at every s_ in
the grid. This is a closed-form identity (see policy.py's CRRA class docstring), not a numerical
coincidence, so the two solves are expected to agree to machine precision, not just to grid tolerance.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from gridsearch import CartesianGrid
from model import ModelInformalAnalytical

m = testmod.mLOG                      # rho=1 calibration
CRRA, LOG = m.CRRA, m.LOG
th, eps = m.db['θ'].values, m.db['eps'].values
tIdx = m.db['t']
t = tIdx[-1]
pos = tIdx.get_loc(t)
tLag = tIdx[pos - 1]

from gridsearch.testing import check, report

# ---- 0. self.GS structure: symmetric between LOG and CRRA, correctly wired
check("LOG.GS['PEE']['stateGrids'] is None (LOG's political FOC has no state)",
      LOG.GS['PEE']['stateGrids'] is None)
check("LOG.GS['PEE']['solGrids']['τ'] matches its own gridSettings",
      np.allclose(LOG.GS['PEE']['solGrids']['τ'][[0, -1]],
                  [LOG.GS['PEE']['gridSettings']['l'], LOG.GS['PEE']['gridSettings']['u']]))
check("CRRA.GS['PEE']['stateGrids'] exists with 's_' unset (extends, not replaces, LOG's entry)",
      set(CRRA.GS['PEE']['stateGrids']) == {'s_'})
check("CRRA.GS['PEE']['solGrids']['τ'] present too (inherited from LOG.initGS)",
      'τ' in CRRA.GS['PEE']['solGrids'])

# ---- 1. exact collapse to LOG at rho=1, at every state simultaneously
dLOG = LOG.solveBackward_t(t, th[pos], eps[pos], tLag, terminal = True)
tauLOG = dLOG['τ']

sGrid = CRRA.defaultSGrid(th[pos], t, n = 25)
CRRA.GS['PEE']['stateGrids']['s_'] = sGrid   # fix the state grid explicitly -- see solveTerminal's docstring
res = CRRA.solveTerminal(th[pos], eps[pos], t = t)
check('CRRA terminal tau is state-independent at rho=1',
      np.allclose(res['τ'].values, res['τ'].values[0], atol = 1e-10),
      '-> range={:.2e}'.format(res['τ'].values.max() - res['τ'].values.min()))
check('CRRA terminal tau == LOG terminal tau at rho=1',
      np.allclose(res['τ'].values, tauLOG, atol = 1e-4),
      '-> CRRA={:.6f} vs LOG={:.6f}'.format(res['τ'].values[0], tauLOG))
check('no corner solutions selected', not res['atBound'].any())
check('no multiplicity', (res['nMax'] <= 1).all())

# ---- 2. sanity at genuine rho != 1: state dependence is the whole point of the CRRA terminal problem
# (Bi = Base.B(s_, h, tLag) genuinely depends on the state, unlike LOG's primitive beta_i)
m2 = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 2.0}, **testmod.kwargs)
CRRA2 = m2.CRRA
th2, eps2 = m2.db['θ'].values, m2.db['eps'].values
t2 = m2.db['t'][-1]
check("a fresh CRRA instance starts with stateGrids['s_'] unset (None)",
      CRRA2.GS['PEE']['stateGrids']['s_'] is None)

# without an explicit override, solveTerminal computes a fresh defaultSGrid internally and does NOT
# cache it back into self.GS (see the header comment on self.GS -- avoiding exactly this staleness risk)
resAuto = CRRA2.solveTerminal(th2[pos], eps2[pos], t = t2)
check("solveTerminal works with no override set (auto defaultSGrid)",
      np.all(np.isfinite(resAuto['τ'].values)))
check("solveTerminal does NOT cache the computed default back into self.GS",
      CRRA2.GS['PEE']['stateGrids']['s_'] is None)

sGrid2 = CRRA2.defaultSGrid(th2[pos], t2, n = 25)
CRRA2.GS['PEE']['stateGrids']['s_'] = sGrid2
res2 = CRRA2.solveTerminal(th2[pos], eps2[pos], t = t2)
check("explicit override actually determines the state grid used",
      np.array_equal(res2['s_'], sGrid2))
spread = res2['τ'].values.max() - res2['τ'].values.min()
check('rho!=1: tau genuinely varies with state', spread > 1e-4, '-> range={:.2e}'.format(spread))
check('rho!=1: tau values stay in [0,1] and finite',
      np.all(np.isfinite(res2['τ'].values)) and np.all((res2['τ'].values >= 0) & (res2['τ'].values <= 1)))

# ---- 3. stateGrid_T/focGrid_T produce finite values directly (not just after selectMaxND smooths things
# over) -- catches a bad formula before it hides behind the grid search
tIdx2 = m2.db['t']
tLag2 = tIdx2[tIdx2.get_loc(t2) - 1]
gr = CartesianGrid(τ = np.array([0.1, 0.3]), s_ = sGrid2[:3])
d = CRRA2.stateGrid_T(gr.flat['τ'], gr.flat['s_'], th2[pos], eps2[pos], t2, tLag2)
z = CRRA2.focGrid_T(d, th2[pos], eps2[pos], t2)
check('stateGrid_T/focGrid_T finite off the grid search path', np.all(np.isfinite(z)))

# ---- 4. report_T: full solution dict (not just the bare grid-search result) and the tau/h policy
# functions -- the "local functions evaluable along the PEE path" report_T exists to build
for k in ('Θh', 'h', 'Bi', 'Γs_', 'si_s_', 'tc1i', 'c2i', 'tc20', 'τPolicy', 'hPolicy'):
    check("solveTerminal's report includes '{}'".format(k), k in res2)

check('τPolicy is exact AT the grid nodes it was built from',
      np.allclose(res2['τPolicy'](sGrid2), res2['τ'].values, atol = 1e-12))
check('hPolicy is exact AT the grid nodes it was built from',
      np.allclose(res2['hPolicy'](sGrid2), res2['h'].values, atol = 1e-12))

# an off-grid (interior) point: linear interpolation between its two bracketing nodes
sMid = 0.5*(sGrid2[10] + sGrid2[11])
tauMid_expected = 0.5*(res2['τ'].values[10] + res2['τ'].values[11])
check('τPolicy interpolates linearly between nodes',
      np.isclose(res2['τPolicy'](sMid), tauMid_expected, atol = 1e-10))

# extrapolation: a candidate state below/above the grid must return a finite, non-clamped value (not the
# boundary node's value repeated) -- exactly the t<T recursion's use case (see report_T's docstring)
sBelow, sAbove = sGrid2[0] - 0.1*(sGrid2[-1] - sGrid2[0]), sGrid2[-1] + 0.1*(sGrid2[-1] - sGrid2[0])
check('τPolicy extrapolates below the grid (finite, not clamped to the boundary node)',
      np.isfinite(res2['τPolicy'](sBelow)) and not np.isclose(res2['τPolicy'](sBelow), res2['τ'].values[0]))
check('τPolicy extrapolates above the grid (finite, not clamped to the boundary node)',
      np.isfinite(res2['τPolicy'](sAbove)) and not np.isclose(res2['τPolicy'](sAbove), res2['τ'].values[-1]))

# report_T is genuinely reusable standalone (not just as solveTerminal's tail call): re-running it on the
# already-solved (sGrid2, tau) pair must reproduce res2 exactly -- stateGrid_T is shape-agnostic about
# where tau came from (see report_T's docstring), so this is a real identity, not a tautology
reportAgain = CRRA2.report_T(sGrid2, res2['τ'].values, th2[pos], eps2[pos], t2, tLag2)
check('report_T re-run on its own output reproduces it exactly',
      np.array_equal(reportAgain['h'].values, res2['h'].values) and
      np.array_equal(reportAgain['Θh'], res2['Θh']))

report()
