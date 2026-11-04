r""" The model core's guards, and the CRRA permanent timing's path (notes/codeReview_triage.md, 2026-11-04).
Each check fails on the code before the change it pins.

Run:  .venv\Scripts\python.exe python\US\test_coreGuards.py        (~30 s)

  G1  solvePermanent('CRRA'): the equilibrium at the chosen design is solvePEE_CRRA's own (sol, report),
      every candidate starts from its own steady-state seed, and permanentChoiceAtT0('CRRA') passes no s0.
  G2  adjPar takes no `t`.
  G3  a candidate design whose solve fails (policyESC.SOLVE_FAILURES) is dropped and counted; any other
      exception propagates: _leadedGridChoice_CRRA, LeadedCRRA.solvePath and stateSensitivity,
      PermanentCRRA._grid.
  G4  LeadedCRRA2D.s0FixedPoint's iteration fallback raises unless it converges on the state grid.
  G5  LOG.solveVectorized caches its warm start only once the convergence check has passed.
  G6  sequentialFOC (the costless Eq esc:seqFOC) refuses an installed wedge.
  G7  EE_CRRA_solve builds the LOG fallback x0 only when no x0 is cached.
  G8  calibratePoint without gridSettings keeps the installed settings; _calVerify refines and restores them.
  G9  addEigenVectors is the closed form y = z/(γ·z) of Eq (calibration:etai/Xi)'s rank-one eigenproblem,
      within 1e-14 of scipy's eigs.
  G10 one zero-mass guard (policy.requireZeroMass) behind LOG's and the leaded solvers'.
  G11 the dead definitions are gone.
  G12 κ_t = p_t + ε_{t+1}γ_{t,0}p_t^0 (Eq governmentBudget:bbar), checked at a time-varying γ_0.
  G13 'sizePiR' at acceptance (_ΠRFixedPoint, calibrate): db keeps the π the returned solve was solved at, the
      record carries the path's π (ΠRpath) and ΠRgap = max|ΠRpath - db's π|.
"""
import os, sys, time, types, inspect
import numpy as np
import pandas as pd
import scipy.sparse.linalg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
import base, policy, policyESC, shocks
from model import ModelUS
from modelESC import ModelESC
from policyESC import LeadedCRRA2D, LeadedBase

from gridsearch.testing import check, report

GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}
PARS = testmod.pars | {'ρ': 1.0, 'β': 0.655483014875856, 'ω': 1.2308601504079868}


def raises(f, exc):
    """ f() raises exc (and nothing else). """
    try:
        f()
    except exc:
        return True
    except Exception:
        return False
    return False


tic = time.time()

# ==== G1: the CRRA permanent timing's path ================================================================
mC = ModelESC(pars = PARS | {'ρ': 2.0}, nθCandPerm = 3, **testmod.kwargs)
mC.CRRA.initGS(GS | {'ns': 25})
ε = mC.db['eps'].values.astype(float)
perm = mC.solvePermanent('CRRA', verbose = False)
ref = mC.solvePEE_CRRA(θ = perm['θPath'], ε = ε)
same = lambda a, b: np.array_equal(np.asarray(a, dtype = float), np.asarray(b, dtype = float))
check("G1 solvePermanent('CRRA') reports solvePEE_CRRA's own equilibrium at the chosen design (τ, s_, R)",
      same(perm['τ'], ref['τ']) and same(perm['report']['s_'], ref['report']['s_'])
      and same(perm['report']['R'], ref['report']['R']),
      f"-> θ_perm {perm['θ']:.4f}; s_ at position 0 {float(perm['report']['s_'].iloc[0]):.6f} "
      f"against {float(ref['report']['s_'].iloc[0]):.6f}")
k = int(np.flatnonzero(np.isclose(perm['cache']['θ'], 0.5))[0])
cand = mC.solvePEE_CRRA(θ = np.full(mC.T, 0.5), ε = ε)
check('G1 every candidate starts from its own steady-state seed (τ_t0 at θ = 0.5 as a fresh solvePEE_CRRA)',
      perm['cache']['τ'][k] == float(cand['τ'].xs(mC.t0Year)),
      f"-> {perm['cache']['τ'][k]:.10f} against {float(cand['τ'].xs(mC.t0Year)):.10f}")
calls = []
mC.ESCPC.solve = lambda *a, **kw: calls.append(kw) or {'θ': 0.5}
mC.permanentChoiceAtT0('CRRA', base = ref)
del mC.ESCPC.solve
check("G1 permanentChoiceAtT0('CRRA') passes no s0 (s_{t0-1} is not the state before position 0)",
      len(calls) == 1 and calls[0].get('s0') is None, f'-> kwargs {calls}')

# ==== G2: adjPar has no t ==================================================================================
m = ModelUS(pars = PARS, commonX = True, **testmod.kwargs)
check('G2 adjPar takes no t (the in-place path is gone)',
      't' not in inspect.signature(m.adjPar).parameters and raises(lambda: m.adjPar('ω', 1.3, t = 2), TypeError))

# ==== G3: failed candidate solves dropped and counted, other exceptions propagate ===========================
mE = ModelESC(pars = PARS, **testmod.kwargs)
E, T, t0 = mE.ESCC, mE.T, int(mE.db['t0'])
bad = float(E.θCand[4])
def fakeSolve(exc):
    def solve(θTry, s0 = None, **kw):
        if np.any(np.asarray(θTry) == bad):
            raise exc('a fake failure')
        return np.asarray(θTry, dtype = float)
    return solve
E.W = lambda out, pos: -(out[pos+1] - 0.62)**2
E.solveθPath = fakeSolve(RuntimeError)
ch = mE.leadedChoiceAtT0_CRRA()
fails = getattr(mE, 'lastGridChoiceFailures', None)
check('G3 _leadedGridChoice_CRRA drops a candidate whose solve fails and records it',
      abs(ch - 0.62) < 1e-12 and fails is not None and len(fails) == 1 and fails[0][0] == bad,
      f'-> choice {ch:.12f}; failures {fails}')
E.solveθPath = fakeSolve(KeyError)
check('G3 _leadedGridChoice_CRRA lets any other exception through', raises(mE.leadedChoiceAtT0_CRRA, KeyError))
E.solveθPath = fakeSolve(ValueError)
rec = E.solvePath(0.5, pinPos = T-3, maxIter = 1, verbose = False)
check('G3 LeadedCRRA.solvePath counts the failed candidate solves',
      rec.get('nFailed') == 2 and abs(rec['θ'].values[-1] - 0.62) < 1e-12,
      f"-> nFailed {rec.get('nFailed')}, θ_T {rec['θ'].values[-1]:.12f}")
E.solveθPath = fakeSolve(KeyError)
check('G3 LeadedCRRA.solvePath lets any other exception through',
      raises(lambda: E.solvePath(0.5, pinPos = T-3, maxIter = 1, verbose = False), KeyError))
E.solveθPath = fakeSolve(ArithmeticError)
sens = E.stateSensitivity(np.full(T, 0.5), pos = t0)
check('G3 stateSensitivity counts the failed candidate solves', sens.get('nFailed') == 2 and sens['slope'] == 0.,
      f"-> nFailed {sens.get('nFailed')}, slope {sens['slope']}")
E.solveθPath = fakeSolve(TypeError)
check('G3 stateSensitivity lets any other exception through',
      raises(lambda: E.stateSensitivity(np.full(T, 0.5), pos = t0), TypeError))
P = mC.ESCPC
θBefore = mC.db['θ'].values.copy()
def fakePEE(exc):
    def solve(θ = None, ε = None, s0 = None, **kw):
        if float(θ[0]) == 0.5:
            raise exc('a fake failure')
        return ref
    return solve
mC.solvePEE_CRRA = fakePEE(RuntimeError)
cache = P._grid(mC.t0Year, P.θCand, verbose = False)
check('G3 PermanentCRRA._grid keeps a failed candidate as ok = False, with its error and the count',
      cache.get('nFailed') == 1 and list(cache['ok']) == [True, False, True]
      and str(cache.get('errors', [None]*3)[1]).startswith('RuntimeError'),
      f"-> nFailed {cache.get('nFailed')}, errors {cache.get('errors')}")
mC.solvePEE_CRRA = fakePEE(KeyError)
check('G3 PermanentCRRA._grid lets any other exception through',
      raises(lambda: P._grid(mC.t0Year, P.θCand, verbose = False), KeyError))
del mC.solvePEE_CRRA
check("G3 PermanentCRRA._grid restores db['θ'] after a propagated exception",
      np.array_equal(mC.db['θ'].values, θBefore))

# ==== G4: s0FixedPoint's fallback ==========================================================================
fake = types.SimpleNamespace(db = {'t': pd.Index([0, 1])})
grid = np.linspace(0.1, 1., 10)
sols = lambda f: {0: {'sPolicy': f, 'sGrid': grid}}
s0 = lambda f: LeadedCRRA2D.s0FixedPoint(fake, sols(f), 0.5)
sIn = s0(lambda s, θ: np.where((s <= 0.1) | (s >= 1.), np.nan, 0.5 + 0.5*(s - 0.5)))
check('G4 s0FixedPoint: without a bracket the iteration converging on the grid is returned', abs(sIn - 0.5) < 1e-11,
      f'-> {sIn!r}')
check('G4 s0FixedPoint raises where the iteration converges off the grid (s* = 2 on [0.1, 1])',
      raises(lambda: s0(lambda s, θ: 2. + 0.5*(s - 2.)), RuntimeError))
check('G4 s0FixedPoint raises where the iteration does not converge',
      raises(lambda: s0(lambda s, θ: 2.*s + 0.1), RuntimeError))
check('G4 s0FixedPoint: a bracketed fixed point is brentq\'s',
      abs(s0(lambda s, θ: 0.3 + 0.4*s) - 0.5) < 1e-12)

# ==== G5: the gradient solve's warm start ==================================================================
m.LOG.initGS(GS)
θ, εL = m.db['θ'].values, m.db['eps'].values
m.LOG.x0.clear()
failed = raises(lambda: m.LOG.solveVectorized(θ, εL, tol = -1.), RuntimeError)
check('G5 a gradient solve that fails its convergence check raises and caches no warm start',
      failed and 'vectorized' not in m.LOG.x0, f'-> cache keys {list(m.LOG.x0)}')
fast = m.LOG.solveVectorized(θ, εL)
cached = policy.robustRoot.clip(m.LOG.x0.get('vectorized', np.full(m.T, np.nan)), 0, m.LOG._upper(None))
check('G5 a converged one caches its τ̃', np.array_equal(cached, fast['τ'].values))

# ==== G6: sequentialFOC is costless ========================================================================
mW = ModelESC(pars = PARS, wedge = {'spec': 'size', 'phi': 0.5, 'p': 6.247}, commonX = True, **testmod.kwargs)
mW.LOG.initGS(GS)
outW = mW.solvePEE_LOG()
check('G6 sequentialFOC refuses an installed wedge',
      raises(lambda: mW.sequentialFOC(np.linspace(0., 1., 5), outW), NotImplementedError))

# ==== G7: EE_CRRA_solve's fallback x0 is lazy ==============================================================
m2 = ModelUS(pars = PARS | {'ρ': 2.0}, commonX = True, **testmod.kwargs)
τc, θc, εc = np.full(m2.T, float(m2.db['τ0'])), m2.db['θ'].values, m2.db['eps'].values
real = m2.defaultX0_EE_CRRA
built = []
m2.defaultX0_EE_CRRA = lambda *a: built.append(1) or real(*a)
m2.EE_CRRA_solve(τc, θc, εc)
nFirst = len(built)
m2.EE_CRRA_solve(τc, θc, εc)
check('G7 EE_CRRA_solve builds the LOG fallback x0 only without a cached one', nFirst == 1 and len(built) == 1,
      f'-> built {nFirst} on the cold call, {len(built) - nFirst} on the cached one')

# ==== G8: calibratePoint keeps the installed grid settings ================================================
mG = ModelUS(pars = PARS, commonX = True, **testmod.kwargs)
mG.LOG.initGS({'n': 51, 'Δl': 7})
seen = []
mG.calibrate = lambda **kw: {'report': {'R': 1., 'τ': .1, 'sr': .2, 'h': .3, 'hbar': .3, 'PEE': {}},
                             'residual': np.zeros(2), 'x': np.zeros(2), 'scipyRes': None,
                             'pars': {'β': .6, 'ω': 1.}}
mG.calibration_residual = lambda x, prefs, solveKwargs = None: seen.append(
    dict(mG.LOG.GS['PEE']['gridSettings'])) or np.zeros(2)
recG = mG.calibratePoint(1.0, verify = {'n': 201})
after = mG.LOG.GS['PEE']['gridSettings']
check('G8 calibratePoint without gridSettings keeps the installed ones',
      recG['gridSettings']['n'] == 51 and recG['gridSettings']['Δl'] == 7, f"-> {recG['gridSettings']}")
check('G8 _calVerify refines the installed settings and restores them',
      len(seen) == 1 and seen[0]['n'] == 201 and seen[0]['Δl'] == 7 and after['n'] == 51 and after['Δl'] == 7,
      f'-> during {seen}, after {after}')

# ==== G9: the eigenvectors in closed form ==================================================================
mV = ModelUS(pars = testmod.pars | {'ρ': 1.0}, commonX = False, **testmod.kwargs)
tV = mV.db['t0']
γ = mV.db['γi'].xs(tV).values
for y, z in (('yx', 'zxi'), ('yη', 'zηi')):
    zz = mV.db[z].xs(tV).values.astype(float)
    _, vec = scipy.sparse.linalg.eigs(zz.reshape(-1, 1)*γ.reshape(1, -1), k = 1)
    ye = np.abs(np.real(vec)).ravel()
    ye = ye/(γ*ye).sum()
    got = np.asarray(mV.db[y], dtype = float)
    d = float(np.max(np.abs(got/ye - 1)))
    check(f'G9 {y} is z/(γ·z) exactly and within 1e-14 of scipy eigs', np.array_equal(got, zz/(γ*zz).sum()) and d <= 1e-14,
          f'-> max rel diff to eigs {d:.1e}')

# ==== G10: one zero-mass guard ============================================================================
mZ = ModelESC(pars = PARS, **testmod.kwargs)
mZ.db['γ0'] = mZ.db['γ0'] + 0.1
helper = getattr(policy, 'requireZeroMass', None)
check('G10 LOG and the leaded solvers raise through policy.requireZeroMass when γ0 > 0',
      helper is not None and raises(lambda: helper(mZ.db, 'test'), NotImplementedError)
      and raises(mZ.LOG._requireZeroMass, NotImplementedError) and raises(mZ.ESC._requireZeroMass, NotImplementedError)
      and 'requireZeroMass(' in inspect.getsource(policy.LOG._requireZeroMass)
      and 'requireZeroMass(' in inspect.getsource(LeadedBase._requireZeroMass))

# ==== G11: dead definitions =================================================================================
gone = {'Base.power_p': hasattr(base.Base, 'power_p'), 'ModelUS.aux_p': hasattr(ModelUS, 'aux_p'),
        'ModelUS.getXi': hasattr(ModelUS, 'getXi'), 'shocks.solveBaseline': hasattr(shocks, 'solveBaseline'),
        'LOG.style': hasattr(m.LOG, 'style'), 'LOG.kwargs': hasattr(m.LOG, 'kwargs'),
        'LeadedLOG.kwargs': hasattr(mE.ESC, 'kwargs'), 'LeadedCRRA.kwargs': hasattr(mE.ESCC, 'kwargs'),
        'PermanentCRRA.kwargs': hasattr(mE.ESCPC, 'kwargs')}
check('G11 the dead definitions are gone', not any(gone.values()), f'-> still there: {[k for k, v in gone.items() if v]}')

# ==== G12: κ_t = p_t + ε_{t+1}γ_{t,0}p_t^0 ===================================================================
mK = ModelUS(pars = PARS, **testmod.kwargs)
tK = mK.db['t']
γK = pd.Series(np.linspace(0.1, 0.4, len(tK)), index = tK)
mK.db.update({'γ0': γK, 'γ0[t+1]': γK.shift(-1).fillna(0.5), 'γ0[t-1]': γK.shift(1).fillna(0.05)})
ε1 = np.linspace(0.2, 0.3, len(tK))
p, p0 = mK.db['p'].values.astype(float), mK.db['p0'].values.astype(float)
κK = np.asarray(mK.BT.κ(ε1), dtype = float)
check('G12 κ_t = p_t + ε_{t+1}γ_{t,0}p_t^0 with a time-varying γ_0 (no (1+γ_{t,0})/(1+γ_{t+1,0}) factor), and = p at γ_0 = 0',
      np.array_equal(κK, p + ε1*γK.values*p0) and np.array_equal(m.db['κ'].values.astype(float), m.db['p'].values.astype(float)),
      f'-> κ[0] {κK[0]:.6f} against p[0] + ε γ0 p0 {p[0] + ε1[0]*γK.values[0]*p0[0]:.6f}')

# ==== G13: 'sizePiR' at acceptance: db keeps the π solved at, the record the path's ===========================
mP = ModelESC(pars = PARS, wedge = {'spec': 'sizePiR', 'phi': 0.5, 'p': 11.26}, commonX = True, **testmod.kwargs)
mP.LOG.initGS(GS)
outP = mP.solvePEE_LOG()
πdb = mP.db['wedgeΠR'].values.astype(float)
πP = outP.get('ΠRpath')
πRe = mP.ΠRPath(outP['report'], outP['τ'].values, mP.db['θ'].values)
check("G13 solvePEE_LOG under 'sizePiR': the record's ΠRpath is ΠRPath of the returned path, db keeps the π it was "
      "solved at (ΠRgap = max|ΠRpath - db's π| exactly, a warm start equal to ΠRpath)",
      πP is not None and float(np.max(np.abs(πP - πRe))) < 1e-14 and outP['ΠRgap'] == float(np.max(np.abs(πP - πdb)))
      and outP['ΠRgap'] < 1e-10 and np.array_equal(mP._ΠRstart['solvePEE_LOG'], πP),
      f"-> {outP['ΠRiter']} iterations, gap {outP['ΠRgap']:.1e}, π_2020 {πdb[mP.db['t0']]:.6f}")
calP = mP.calibrate()
πdbC = mP.db['wedgeΠR'].values.astype(float)
check("G13 calibrate under 'sizePiR': the same record (ΠRpath, ΠRgap = max|ΠRpath - db's π|), db and the warm start "
      "at the π the calibration was solved at", calP.get('ΠRpath') is not None
      and calP['ΠRgap'] == float(np.max(np.abs(calP['ΠRpath'] - πdbC))) and np.array_equal(mP._ΠRstart['calibrate'], πdbC),
      f"-> {calP['ΠRiter']} iterations, gap {calP['ΠRgap']:.1e}")

print(f'[{time.time() - tic:.0f}s]')
report()
