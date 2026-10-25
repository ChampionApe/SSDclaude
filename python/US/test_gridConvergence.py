r""" Grid convergence of the CRRA tax condition's τ-derivatives, of the log design choice's anticipated tax and of
the exact CRRA design recursion's θ-state grid.

Run:  .venv\Scripts\python.exe python\US\test_gridConvergence.py        (~1.5 min)

  D  CRRA._gradProfile (docs alg:CRRA:grid, step 3): the τ-derivatives are the least-squares cubic in ln(1-τ) with
     knots gradKnotSpacing apart in τ, so refining the tax grid puts more nodes under each knot. At a calibrated
     ρ = 0.5 (common X, CAL05), ns = 50: the knots follow the grid (D1); at the state
     the 2020 path enters with, the 2020 continuation held, dln h/dτ near the root and the root of the period's
     condition agree between 101 and 401 tax nodes (D2, D3); a whole solve's 2020 tax and θ 1 -> 0 gap agree
     between the two grids (D4). Under log preferences the CRRA derivatives are never called (D5).
     runHorizon's converged reference is the same derivative on the 8-fold tax grid, knots held (D6).
  L  LeadedLOG at the log calibration of the paper's cost (λ = 11.563954, 'size', common X, (β, ω, X)
     recalibrated): the design in force in 2020 is the maximiser of W_1990 with the anticipated tax T_2020(θ')
     solved at every θ' -- the zero of dW/dθ' by central differences, located by brentq, independently of the
     solver's candidate grid -- to 1e-5 (L1); it does not depend on the design-state grid (21 against 41 nodes,
     L2); the anticipated tax the recursion reads at its candidates is the polished policy (τAt, L3), and its
     selections are counted (L4).
  C  LeadedCRRA2D (alg esc:crra2D): the last choosing period's design, its continuation on the default 13 θ nodes
     (Interp2D, cubic along θ) against the continuation on 97, every state (C1; the whole recursion's θ_2020 at the
     calibration: python/US/RESEARCH_LOG.md, 2026-10-24); the default grid and interpolant (C2).
"""
import os, sys, time
import numpy as np
from copy import deepcopy
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
import shocks as sh
from model import ModelUS
from modelESC import ModelESC
from policyESC import LeadedLOG
from gridsearch import CartesianGrid
from gridsearch.testing import check, report

tic = time.time()
# the calibrated common-X U.S. at rho = 0.5 (results/calibration/US_rhoGridCommonX.csv as of f3a15a4): beta, omega, X
CAL05 = (1.0599983263028827, 1.674480497033504, 4.177466626733653)
GS = {'n': 101, 'ns': 50, 'smoothKnots': 4, 'interpKind': 'linear'}
TOL_ROOT, TOL_DLNH, TOL_TAX, TOL_GAP = 2e-5, 2e-3, 5e-5, 5e-5     # D3, D2 (relative), D4 (level of tau)


def crra(n, ρ = 0.5, cal = CAL05):
    β, ω, X = cal
    m = ModelUS(pars = testmod.pars | {'ρ': ρ, 'β': β, 'ω': ω}, commonX = True, **testmod.kwargs)
    m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
    m.CRRA.initGS(GS | {'n': n})
    m.initProductivity_commonX(X = X)
    m.updateAuxPars()
    return m


# ==== D: the CRRA tax condition's tau-derivatives ===============================================================
m = crra(101)
out = m.solvePEE_CRRA()
sols, tIdx = out['sols'], m.db['t']
θ, ε = m.db['θ'].values.astype(float), m.db['eps'].values.astype(float)
sGrid = sols[tIdx[0]]['τ'].index.values.astype(float)
τ101 = m.CRRA.GS['PEE']['solGrids']['τ'].copy()
τ401 = np.linspace(τ101[0], τ101[-1], 401)
knots = {n: getattr(m.CRRA, '_gradKnots', lambda g: None)(g) for n, g in ((101, τ101), (401, τ401))}
check('D1: the derivatives\' knots follow the tax grid, gradKnotSpacing apart in tau (4 nodes per knot at n = 101, '
      '16 at 401)', knots == {101: 4, 401: 16}, f'-> {knots}')

pos = 2                                                   # 2020; its continuation is the solved 2050 policy
t, t1, tLag = tIdx[pos], tIdx[pos+1], tIdx[pos-1]
s_ = float(out['report']['s_'].values[pos])
x = np.array([0.999*s_, s_, 1.001*s_])


def periodAt(τGrid):
    """ The period's z_t parts and its selected tax at the states x, on τGrid, the continuation held. """
    m.CRRA.GS['PEE']['solGrids']['τ'] = τGrid
    try:
        sSol, _ = m.CRRA.solveStateApprox_t(τGrid, sGrid, x, t, θ[pos+1], sols[t1])
        g = CartesianGrid(τ = τGrid, s_ = x)
        d = m.CRRA.stateGrid_t(g.flat['τ'], sSol.reshape(-1), g.flat['s_'], t, tLag, t1, θ[pos], θ[pos+1],
                               ε[pos], ε[pos+1], sols[t1])
        dlnh = g.reshape(m.CRRA.focParts_t(d, g, t, ε[pos])['dlnh'])[:, 1]
        root = float(m.CRRA.solveBackward_t(sols[t1], t, tLag, t1, θ[pos], θ[pos+1], ε[pos], ε[pos+1], x, sGrid,
                                            smooth = 0)['τ'].values[1])
    finally:
        m.CRRA.GS['PEE']['solGrids']['τ'] = τ101
    return dlnh, root


dlnh101, root101 = periodAt(τ101)
dlnh401, root401 = periodAt(τ401)
near = np.abs(τ101 - root101) <= 0.05                   # nodes of the 101-grid within 0.05 of the root
dd = float(np.max(np.abs(dlnh101[near] - dlnh401[::4][near]))/np.max(np.abs(dlnh101[near])))
check(f'D2: dln h_2020/dτ at the path state, nodes within 0.05 of the root, 101 against 401 tax nodes, to '
      f'{TOL_DLNH:.0e} relative', dd <= TOL_DLNH, f'-> {dd:.2e}')
check(f'D3: the root of the 2020 condition at the path state (continuation held), 101 against 401 tax nodes, to '
      f'{TOL_ROOT:.0e}', abs(root401 - root101) <= TOL_ROOT,
      f'-> {root101:.8f} vs {root401:.8f} ({root401 - root101:+.2e})')

whole = {}
for n in (101, 401):
    mn = crra(n)
    r = {}
    for scen in ('baseline', 'theta0', 'theta1'):
        mt = mn if scen == 'baseline' else sh.shockedCopy(mn, scen, {})[0]
        r[scen] = float(mt.solvePEE_CRRA()['τ'].values[pos])
    whole[n] = (r['baseline'], r['theta0'] - r['theta1'])
dτ, dgap = whole[401][0] - whole[101][0], whole[401][1] - whole[101][1]
check(f'D4: whole solves, 101 against 401 tax nodes: the 2020 tax to {TOL_TAX:.0e} and the θ 1 -> 0 gap to '
      f'{TOL_GAP:.0e}', abs(dτ) <= TOL_TAX and abs(dgap) <= TOL_GAP,
      f'-> tau_2020 {whole[101][0]:.7f} / {whole[401][0]:.7f} ({dτ:+.1e}), gap {whole[101][1]:.7f} / '
      f'{whole[401][1]:.7f} ({dgap:+.1e})')

mL = ModelUS(pars = testmod.pars | {'ρ': 1.0, 'β': 0.655483014875856, 'ω': 1.2308601504079868}, commonX = True,
             **testmod.kwargs)
τLog = mL.solvePEE_LOG()['τ'].values.copy()
calls = []
orig = mL.CRRA.focParts_t
mL.CRRA.focParts_t = lambda *a, **k: calls.append(1) or orig(*a, **k)
mL.LOG.x0 = {}                                            # the same cold start as the first solve
τLog2 = mL.solvePEE_LOG()['τ'].values
check('D5: under log preferences the tax path never reaches the CRRA derivatives (0 calls) and is bitwise unchanged',
      not calls and np.array_equal(τLog, τLog2), f'-> calls {len(calls)}, max|dτ| {np.max(np.abs(τLog - τLog2)):.1e}')

import policy                                                                       # noqa: E402
import runHorizon                                                                   # noqa: E402
gg, τ0 = policy.griddedGradient1D, m.CRRA.GS['PEE']['solGrids']['τ'].copy()
with runHorizon.referenceDerivatives(m, 8):
    τR = m.CRRA.GS['PEE']['solGrids']['τ'].copy()
    kR, ggR = getattr(m.CRRA, '_gradKnots', lambda g: None)(τR), policy.griddedGradient1D
check("D6: runHorizon.referenceDerivatives is the production derivative on the tax grid refined 8-fold (801 nodes, "
      "knots still gradKnotSpacing apart: 32 nodes per knot), and restores the grid",
      τR.size == 801 and kR == 32 and ggR is gg and np.array_equal(m.CRRA.GS['PEE']['solGrids']['τ'], τ0),
      f'-> {τR.size} nodes, {kR} nodes per knot, derivative {"unchanged" if ggR is gg else "replaced"}')

# ==== L: the log design choice's anticipated tax ================================================================
LAMBDA = 11.563953547546632                   # results/esc/escCalibration.csv: 'size', common X (as of f3a15a4)


def esc(nθ = 41):
    mE = ModelESC(pars = testmod.pars | {'ρ': 1.0, 'β': 0.655483014875856, 'ω': 1.2308601504079868},
                  wedge = {'spec': 'size', 'phi': 0.5, 'p': LAMBDA}, nθ = nθ, commonX = True, **testmod.kwargs)
    mE.db['dates'], mE.db['workweek'] = testmod.dates, testmod.workweek
    mE.LOG.initGS({'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'})
    return mE


mE = esc()
mE.calibrate()
solsE = mE.ESC.solveBackward()
θ2020 = mE.leadedDesignAtT0(solsE)
led = mE.solveLeaded(pinAtT0 = False, sols = solsE)
tIdx = mE.db['t']
pv = mE.db['t0'] - 1                                           # 1990 chooses the design in force in 2020
t, tLag, t1, t2 = tIdx[pv], tIdx[pv-1], tIdx[pv+1], tIdx[pv+2]
θt, τt = float(led['θ'].iloc[pv]), float(led['τ'].iloc[pv])
θ2 = float(np.interp(0.5, solsE[t1]['θGrid'], solsE[t1]['θNext']))      # the choice at t+1 has no state under log
τ2 = float(mE.ESC.τOfθ(t2, np.array([θ2]), t1, terminal = (t2 == tIdx[-1]))[0][0])


def W(θ1):
    """ W_1990 at candidate designs θ1, the anticipated tax T_2020 solved at each. """
    θ1 = np.atleast_1d(np.asarray(θ1, dtype = float))
    M = θ1.size
    τ1 = mE.ESC.τOfθ(t1, θ1, t, terminal = False)[0]
    cont = {'τ1': τ1, 'θ2': np.full(M, θ2), 'τ2': np.full(M, τ2), 'terminal1': False}
    return mE.ESC.objective(t, tLag, t1, np.full(M, τt), np.full(M, θt), θ1, cont)[0]


δ = 1e-4
dW = lambda q: float(np.diff(W(np.array([q - δ, q + δ])))[0]/(2*δ))
θRef = optimize.brentq(dW, θ2020 - 0.02, θ2020 + 0.02, xtol = 1e-10)
check('L1: the design in force in 2020 at the log calibration is the maximiser of W_1990 with T_2020 solved at '
      'every candidate, to 1e-5', abs(θ2020 - θRef) <= 1e-5,
      f'-> solver {θ2020:.7f}, reference {θRef:.7f} ({θ2020 - θRef:+.1e}); θ* {float(mE.db["θ"].xs(mE.t0Year)):.7f}')

m21 = deepcopy(mE)
m21.ESC = LeadedLOG(m21, nθ = 21, nθCand = mE.ESC.nθCand)
θ21 = m21.leadedDesignAtT0()
check('L2: ...and does not depend on the design-state grid (21 against 41 nodes) to 1e-9', abs(θ21 - θ2020) <= 1e-9,
      f'-> {θ21:.10f} vs {θ2020:.10f}')

τCand = solsE[t1].get('τCand')
js = np.arange(0, mE.ESC.nθCand, 20)
gapC = (np.inf if τCand is None else
        max(abs(float(τCand[j]) - mE.ESC.τAt(t1, float(mE.ESC.θCand[j]))) for j in js))
check('L3: the anticipated tax the recursion reads at its candidates is the polished policy (τAt), to 1e-12',
      gapC <= 1e-12, f'-> max|dτ| {gapC:.1e} at {js.size} candidates')
mult = mE.ESC.lastMultiplicity
check('L4: the candidates\' tax selections are counted: one equilibrium, no fallback',
      'nEqτCand' in solsE[t1] and mult['nEqMax'] == 1 and mult['nFallback'] == 0, f'-> {mult}')

# ==== C: the exact CRRA design recursion's θ-state grid ========================================================
from policyESC import LeadedCRRA2D                                                 # noqa: E402
m2 = ModelESC(pars = testmod.pars | {'ρ': 2.0, 'β': 0.655483014875856, 'ω': 1.2308601504079868},
              wedge = {'spec': 'size', 'phi': 0.5, 'p': 1.728}, **testmod.kwargs)
m2.db['dates'], m2.db['workweek'] = testmod.dates, testmod.workweek
m2.LOG.initGS({'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'})
m2.CRRA.initGS({'n': 101, 'ns': 25, 'smoothKnots': 4, 'interpKind': 'linear'})
E13, E97 = LeadedCRRA2D(m2, nθ = 13, nθCand = 41), LeadedCRRA2D(m2, nθ = 97, nθCand = 41)
E13.GS = E97.GS = m2.CRRA.GS
tIdx2 = m2.db['t']
ε2 = m2.db['eps'].values.astype(float)
sG2 = E13.defaultSGrid(float(m2.db['θ'].xs(m2.t0Year)), tIdx2[-1], n = 25)
args2 = (tIdx2[-2], tIdx2[-3], tIdx2[-1], ε2[-2], ε2[-1], sG2, sG2, E13.θCand, True)
per = {k: E13.solveBackward_t2D(e.solveTerminal2D(ε2[-1], sG2, tIdx2[-1], tIdx2[-2]), *args2)['θNext']
       for k, e in (('13', E13), ('97', E97))}
dθ = float(np.nanmax(np.abs(per['13'] - per['97'])))
check("C1: the last choosing period's design with its continuation on 13 θ nodes is the one with it on 97, to 1e-3, "
      "at every state (ρ = 2, λ = 1.728, ns = 25, 41 candidates)", dθ <= 1e-3,
      f"-> max|Δθ'| {dθ:.2e}; θ' {np.nanmin(per['97']):.4f}..{np.nanmax(per['97']):.4f}")
E = ModelESC(pars = testmod.pars | {'ρ': 2.0}, **testmod.kwargs).ESCC2
check("C2: the default θ-state grid is 13 nodes with the cubic θ-interpolant",
      E.nθ == 13 and getattr(E, 'θInterp', 'linear') == 'cubic', f"-> {E.nθ} nodes, {getattr(E, 'θInterp', 'linear')}")

print(f'({time.time() - tic:.0f}s)')
report()
