r""" model.py's calibratePoint/calibrateGrid (§8.1) -- the continuation march over a parameter grid.

Run:  .venv\Scripts\python.exe python\InformalSavings\test_calibrationGrid.py

gridsearch/test_continuation.py already covers the march's logic against fake solves (visit order,
extrapolation, the retry ladder, step-halving). What is checked here is only what that cannot see: that
the adapter installs the parameter and picks the solver, that a real calibration still hits eq:calibration
at every point of the grid, and that the warm start is worth what it costs.

Slow (~20 min): three real calibrations on the resolved 45x45 inner grid, plus a refined verification at
each. The 45x45 is not the PEE default; it is kept here so this file exercises the settings the sweep
actually runs at, not because 30x30 fails -- since smoothKnots the two agree to ~2e-4 in the parameters
(deviations item 17, which retracted item 12's displaced-root finding). Reducing it would make this a
test of a configuration nothing else uses.
"""
import os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelInformalSavings

from gridsearch.testing import check, report

def newModel(**over):
    return ModelInformalSavings(pars = testmod.pars | over, **testmod.kwargs)

# Grid SIZES are keyed by solver -- a resolution choice, and 45x45 on LOG would move it off its own
# documented default. interpKind and smoothKnots are given to BOTH, matching calibrateRhoGrid.py: they are
# well-posedness rather than resolution choices, so keying either by solver is a bug
# (crossCuttingFindings #7; measurements in deviations note items 12-13).
GRIDS  = {'CRRA': {'nι': 45, 'ns': 45, 'interpKind': 'cubic', 'smoothKnots': 4},
          'LOG': {'smoothKnots': 4, 'interpKind': 'cubic'}}
VERIFY = {'CRRA': {'nι': 60, 'ns': 60, 'interpKind': 'cubic'}, 'LOG': {'nι': 75}}

# ---- 1. calibratePoint: parameter installation and solver selection ----------------------------------
m = newModel(ρ = 1)
t0 = m.db['t'][m.db['t0']]
check('_calPreferences selects LOG at rho=1', m._calPreferences() == 'LOG')
m.db.update(m.adjPar('ρ', 1.3))
check('_calPreferences selects CRRA once rho moves off 1', m._calPreferences() == 'CRRA',
      '-> rho={:.2f}'.format(float(m.db['ρ'].xs(t0))))
m.db.update(m.adjPar('ρ', 1))
# BOTH solvers run at scipy's default outer step (deviations note item 11). The hook is kept, so this
# asserts the dict is EMPTY rather than absent: a reintroduced per-solver step should have to restate its
# own measurement.
check('neither solver overrides scipy\'s outer FD step', m._calOuterKwargs == {})

tStart = time.time()
anchor = m.calibratePoint(1.0, gridSettings = GRIDS, verify = VERIFY)
print('   (anchor calibrated in {:.1f}s)'.format(time.time()-tStart))
check('calibratePoint writes the parameter it was given into db',
      np.isclose(float(m.db['ρ'].xs(t0)), 1.0))
check('calibratePoint returns a flat record carrying x and the four parameters',
      {'ρ', 'x', 'residual', 'preferences', 'β', 'ω', 'η0', 'X0'} <= set(anchor))
check('the anchor used the LOG solver', anchor['preferences'] == 'LOG')
check('the anchor converged', anchor['residual'] < 1e-6, '-> max|res|={:.2e}'.format(anchor['residual']))
check("the record's x is the unbounded image of the record's parameters",
      all(np.isclose(m._calFromX(anchor['x'])[k], anchor[k], rtol = 1e-10) for k in m._calPars),
      '-> ' + ', '.join('{}={:.5f}'.format(k, anchor[k]) for k in m._calPars))
# This reference moves whenever a solver-side setting or the calibration target moves, and is UPDATED
# rather than loosened -- the point of the check is that the anchor lands where the README says it does.
# The history of moves, and the fine-grid extrapolation that independently confirms one of them, are in
# notes/archive/informalSavings_results.md.
check('the anchor reproduces the LOG calibration documented in the README',
      np.isclose(anchor['β'], 0.807610, rtol = 1e-4) and np.isclose(anchor['ω'], 2.327810, rtol = 1e-4),
      '-> β={:.6f}, ω={:.6f}'.format(anchor['β'], anchor['ω']))
check('the inner grid actually used is recorded with the point',
      anchor['gridSettings']['nι'] == 50,
      '-> nι={} (LOG keeps its own default, not the CRRA calibration grid)'.format(
          anchor['gridSettings']['nι']))
check('keyed gridSettings leave the solver that was not named at its defaults',
      m._calGridSettings({'CRRA': GRIDS['CRRA']}, 'LOG') is None
      and m._calGridSettings(GRIDS, 'CRRA') == GRIDS['CRRA'])
check('a flat gridSettings dict still applies to whichever solver runs',
      m._calGridSettings({'nι': 45}, 'LOG') == {'nι': 45})

# _calVerify must leave the working grid installed, or every subsequent point would silently solve on the
# refined one -- and the sweep's timings and its results would both quietly stop meaning what they say.
check('the refined verification restores the working grid afterwards',
      m.LOG.GS['PEE']['gridSettings']['nι'] == 50,
      '-> nι={}'.format(m.LOG.GS['PEE']['gridSettings']['nι']))
check('the verification residual is recorded and finite',
      np.isfinite(anchor['verifyResidual']),
      '-> max|res| at 60x60 = {:.2e} (vs {:.2e} on its own grid)'.format(
          anchor['verifyResidual'], anchor['residual']))

# ---- 2. calibrateGrid over a three-point grid --------------------------------------------------------
# Small but genuine: the anchor plus one point either side, so both directions of the march run and each
# has to hand a CRRA solve a starting point produced by the LOG one.
grid = np.array([0.9, 1.0, 1.1])
written = []
def trace(r):
    """ Also the progress readout: each point is minutes long, so a silent march is indistinguishable
    from a hung one. """
    written.append(r)
    print('   rho={:<5} {}'.format(round(r['value'], 4),
          'ok, {:.0f}s, nfev={}'.format(r['result']['time'], r['result']['nfev']) if r['ok']
          else 'attempt failed ({}): {}'.format(r['x0Source'], r['error'][:80])))

m2 = newModel(ρ = 1)
tStart = time.time()
out = m2.calibrateGrid(grid, anchor = 1.0, gridSettings = GRIDS, verify = VERIFY, onPoint = trace)
elapsed = time.time()-tStart
print('   (3-point march in {:.1f}s)'.format(elapsed))

recs = [r for r in out['records'] if r['ok']]
byRho = {round(r['result']['ρ'], 4): r['result'] for r in recs}
check('every requested rho is calibrated', out['failures'] == [] and set(byRho) == {0.9, 1.0, 1.1},
      '-> solved {}'.format(sorted(byRho)))
check('the anchor is solved first and with LOG; the flanks with CRRA',
      recs[0]['result']['ρ'] == 1.0 and byRho[1.0]['preferences'] == 'LOG'
      and byRho[0.9]['preferences'] == byRho[1.1]['preferences'] == 'CRRA')
check('onPoint fired once per attempted point', len(written) == len(out['records']))
check('the march returns a history usable as a warm start for a later, finer sweep',
      len(out['history']) == 3 and all(len(x) == len(m2._calPars) for _, x in out['history']))

# ---- 3. eq:calibration is actually satisfied at every point of the grid ------------------------------
# The whole point of a calibration sweep: at each rho the four targets must still be hit, so what varies
# across the grid is the parameters, not the fit.
for ρ, r in sorted(byRho.items()):
    check('rho={}: all four residuals below tol'.format(ρ), r['residual'] < 1e-6,
          '-> max|res|={:.2e} in {:.0f}s, nfev={}'.format(r['residual'], r['time'], r['nfev']))
    check('rho={}: capital-output and tax targets hit at t0'.format(ρ),
          np.isclose(r['KY'], m2.db['KY0'], rtol = 1e-5) and np.isclose(r['τ'], m2.db['τ0'], rtol = 1e-5),
          '-> K/Y={:.6f} (target {:.6f}), τ={:.6f} (target {:.6f})'.format(
              r['KY'], m2.db['KY0'], r['τ'], m2.db['τ0']))
    check('rho={}: iota at t0 is a genuine savings ratio in (0,1)'.format(ρ), 0 < r['ι'] < 1,
          '-> ι={:.6f}'.format(r['ι']))
    check('rho={}: the initial fixed point is a single crossing'.format(ρ), r['nRoots'] == 1,
          '-> nRoots={}'.format(r['nRoots']))
    check('rho={}: the calibrated point survives inner-grid refinement'.format(ρ),
          np.isfinite(r['verifyResidual']) and r['verifyResidual'] < 1e-3,
          '-> max|res| at 60x60 = {:.2e}'.format(r['verifyResidual']))

# The parameters must genuinely move with rho -- otherwise the sweep is producing three copies of one
# answer and every check above would pass on a march that ignored its own parameter.
spread = {k: max(byRho[ρ][k] for ρ in byRho)/min(byRho[ρ][k] for ρ in byRho) - 1 for k in m2._calPars}
check('the calibrated parameters move with rho', max(spread.values()) > 1e-3,
      '-> ' + ', '.join('{} spread {:.2%}'.format(k, v) for k, v in spread.items()))
check('beta is monotone in rho over this range (a smooth path is what extrapolation assumes)',
      (byRho[0.9]['β'] - byRho[1.0]['β'])*(byRho[1.0]['β'] - byRho[1.1]['β']) > 0,
      '-> β = ' + ', '.join('{:.5f}'.format(byRho[ρ]['β']) for ρ in sorted(byRho)))

# ---- 4. the warm start has to be worth its complexity ------------------------------------------------
# A cold CRRA calibration from the LOG parameters, against the same point reached by the march. Both
# start from the same db state; the difference is only the starting point handed to the outer root.
mCold = newModel(ρ = 1.1)
mCold._calSetPars({k: anchor[k] for k in mCold._calPars})
mCold.CRRA.initGS(GRIDS['CRRA'])
tStart = time.time()
cold = mCold.calibrate(preferences = 'CRRA')
coldTime, coldFev = time.time()-tStart, int(cold['scipyRes'].nfev)
warm = byRho[1.1]
check('the warm-started march reaches the same calibrated point as a cold solve',
      all(np.isclose(cold['pars'][k], warm[k], rtol = 1e-3) for k in mCold._calPars),
      '-> ' + ', '.join('{}: cold {:.5f} vs warm {:.5f}'.format(k, cold['pars'][k], warm[k])
                        for k in mCold._calPars))
check('the warm start costs no more residual evaluations than a cold one',
      warm['nfev'] <= coldFev,
      '-> nfev warm {} ({:.0f}s) vs cold {} ({:.0f}s)'.format(warm['nfev'], warm['time'],
                                                              coldFev, coldTime))

report()
