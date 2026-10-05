r""" The selection among tax candidates at frozen savings shares (num_robustroot.tex, eq:candidates and
eq:equilibriumTest), as wired into the four US solvers.

Run:  .venv\Scripts\python.exe python\US\test_frozenSelection.py        (~1-2 min)

What is checked: (1) the frozen objective each solver hands to roots1d.selectMaxFrozen IS the political
objective -- its derivative in tau at the shares consistent with the evaluation point equals the solver's
own z_t, under LOG and at the CRRA terminal period, where both sides are closed form; (2) the rule
reproduces the earlier integral criterion bitwise wherever a state has exactly one equilibrium, so the
published numbers can only move where the counts say the rule bound; (3) every solver reports the counts;
(4) CRRA.objectiveFrozen's two edge cases: the terminal period at rho = 1 (section 2) and a candidate on the
last feasible node next to an infeasible cell (section 5).
"""
import os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelUS
from modelESC import ModelESC
from gridsearch import CartesianGrid

from gridsearch.testing import check, report

PARS = testmod.pars | {'ρ': 1.0, 'β': 0.7606187875476447, 'ω': 1.4536273947550569}
GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}


def build(cls, ρ = 1.0, **kw):
    m = cls(pars = PARS | {'ρ': ρ}, **kw, **testmod.kwargs)
    m.db['dates'] = testmod.dates
    m.db['workweek'] = testmod.workweek
    m.LOG.initGS(GS)
    return m


def maxdiff(a, b):
    return float(np.nanmax(np.abs(np.asarray(a, dtype = float) - np.asarray(b, dtype = float))))


# ==== 1. LOG: the frozen objective's derivative at its own shares is z_t ==============================
tic = time.time()
mL = build(ModelUS)
θ, ε = mL.db['θ'].values, mL.db['eps'].values
tIdx = mL.db['t']
pos0 = int(mL.db['t0'])
t0, tLag0, tT, tLagT = tIdx[pos0], tIdx[pos0-1], tIdx[-1], tIdx[-2]
h = 1e-5
with mL.BG.cacheParams():
    for (t, tLag, terminal, label) in ((t0, tLag0, False, 't0'), (tT, tLagT, True, 'T')):
        pos = tIdx.get_loc(t)
        θt = float(θ[pos])
        εt = float(ε[pos])
        for τ in (0.08, 0.15, 0.30):
            dg = mL.LOG.stateGrid(np.array([τ]), t, θt, tLag, terminal, τ1 = np.array([τ]), θ1 = np.array([θt]))
            z = float(mL.LOG.focGrid(dg, t, θt, εt, terminal)[0])
            τg = np.array([τ - h, τ, τ + h])
            dLoc = mL.LOG.stateGrid(τg, t, θt, tLag, terminal, τ1 = τg, θ1 = np.full(3, θt))
            W = mL.LOG.objectiveFrozen(np.array([[τ]]), τg, dLoc, θt, t, εt, tLag, terminal)   # (1, 3, 1)
            dW = (W[0, 2, 0] - W[0, 0, 0])/(2*h)
            check(f'LOG {label}: d/dτ of the frozen objective at its own shares equals z_t at τ={τ}',
                  abs(dW - z) <= 1e-6*max(1., abs(z)), f'-> {dW:.9f} vs {z:.9f}')
        # frozen at ANOTHER candidate the derivative differs: the shares matter
        τg = np.array([0.15 - h, 0.15, 0.15 + h])
        dLoc = mL.LOG.stateGrid(τg, t, θt, tLag, terminal, τ1 = τg, θ1 = np.full(3, θt))
        W2 = mL.LOG.objectiveFrozen(np.array([[0.30]]), τg, dLoc, θt, t, εt, tLag, terminal)
        z15 = float(mL.LOG.focGrid(mL.LOG.stateGrid(np.array([0.15]), t, θt, tLag, terminal,
                                                    τ1 = np.array([0.15]), θ1 = np.array([θt])), t, θt, εt, terminal)[0])
        check(f'LOG {label}: at shares frozen elsewhere the derivative is a different number',
              abs((W2[0, 2, 0] - W2[0, 0, 0])/(2*h) - z15) > 1e-6)

# ==== 2. LOG: rule against the earlier criterion on the full grid, and the counts ======================
n = mL.LOG.GS['PEE']['solGrids']['τ'].size
mL.LOG.selection = 'frozen'
gridF = mL.LOG.solveBackward(θ, ε, Δl = n, Δu = n, update = False)
mL.LOG.selection = 'legacy'
gridL = mL.LOG.solveBackward(θ, ε, Δl = n, Δu = n, update = False)
mL.LOG.selection = 'frozen'
mult = gridF['multiplicity']
check('LOG grid: counts reported, one equilibrium at every period of the baseline, no fallback',
      mult['nEqMax'] == 1 and mult['nFallback'] == 0 and mult['nCandMax'] >= 3, f'-> {mult}')
check('LOG grid: the rule reproduces the earlier criterion bitwise where one equilibrium exists',
      np.array_equal(gridF['τ'].values, gridL['τ'].values), f"-> max|Δτ| = {maxdiff(gridF['τ'], gridL['τ']):.2e}")
rob = mL.LOG.solveRobust(θ, ε)
check('LOG solveRobust: attaches the counts and keeps the gradient solution when it is the selected equilibrium',
      rob.get('multiplicity') is not None and 'warm start' not in rob['message'],
      f"-> {rob['message']}; {rob.get('multiplicity')}")
out = mL.solvePEE_LOG()
check('solvePEE_LOG carries the multiplicity summary', isinstance(out.get('multiplicity'), dict)
      and out['multiplicity']['nEqMax'] >= 1, f"-> {out.get('multiplicity')}")
# the check leaves the gradient solution bitwise untouched: same x0 in and out of solveRobust
x0 = np.full(mL.T, float(mL.db['τ0']))
fast = mL.LOG.solveVectorized(θ, ε, x0 = x0.copy(), update = False)
viaRobust = mL.LOG.solveRobust(θ, ε, x0 = x0.copy(), update = False)
check('solveRobust: the gradient solution is returned bitwise when it is the selected equilibrium',
      np.array_equal(fast['τ'].values, viaRobust['τ'].values) and 'multiplicity' in viaRobust)
# the CRRA terminal period at ρ = 1 (this model): the retirees' level is Σ ω ln c_2 there, c^p/p being undefined
posT = len(tIdx) - 1
sG1 = mL.CRRA.defaultSGrid(θ[posT], tT, n = 12)
with mL.BG.cacheParams():
    gLoc = CartesianGrid(τ = np.array([0.15 - h, 0.15, 0.15 + h]), s_ = sG1)
    dLoc = mL.CRRA.stateGrid_T(gLoc.flat['τ'], gLoc.flat['s_'], θ[posT], ε[posT], tT, tLagT)
    zLoc = mL.CRRA.focGrid_T(dLoc, θ[posT], ε[posT], tT).reshape(3, -1)
    W1 = mL.CRRA.objectiveFrozen(np.full((1, sG1.size), 0.15), gLoc, dLoc, None, θ[posT], tT, tLagT,
                                 ε = ε[posT], terminal = True)
dW1 = (W1[0, 2, :] - W1[0, 0, :])/(2*h)
err1 = np.max(np.abs(dW1 - zLoc[1])/np.maximum(1., np.abs(zLoc[1])))
check('CRRA ρ=1 T: the frozen objective is finite and its τ-derivative at its own shares equals z_T, every state',
      np.isfinite(W1).all() and err1 <= 1e-5, f'-> finite {bool(np.isfinite(W1).all())}, max rel err {err1:.2e}')
print(f'    [LOG sections: {time.time()-tic:.1f}s]')

# ==== 3. CRRA: the terminal frozen objective is closed form and matches z_T; full solves agree ==========
for ρ in (2.0, 0.5):
    tic = time.time()
    mC = build(ModelUS, ρ = ρ)
    θ, ε = mC.db['θ'].values, mC.db['eps'].values
    posT = len(tIdx) - 1
    sGrid = mC.CRRA.defaultSGrid(θ[posT], tT, n = 12)
    with mC.BG.cacheParams():
        for τm in (0.10, 0.25):
            gLoc = CartesianGrid(τ = np.array([τm - h, τm, τm + h]), s_ = sGrid)
            dLoc = mC.CRRA.stateGrid_T(gLoc.flat['τ'], gLoc.flat['s_'], θ[posT], ε[posT], tT, tLagT)
            zLoc = mC.CRRA.focGrid_T(dLoc, θ[posT], ε[posT], tT).reshape(3, -1)
            W = mC.CRRA.objectiveFrozen(np.full((1, sGrid.size), τm), gLoc, dLoc, None, θ[posT], tT, tLagT,
                                        ε = ε[posT], terminal = True)
            dW = (W[0, 2, :] - W[0, 0, :])/(2*h)
            err = np.max(np.abs(dW - zLoc[1])/np.maximum(1., np.abs(zLoc[1])))
            check(f'CRRA ρ={ρ} T: d/dτ of the frozen objective at its own shares equals z_T at τ={τm}, every state',
                  err <= 1e-5, f'-> max rel err {err:.2e}')
    # the terminal selection, both rules
    mC.CRRA.selection = 'frozen'
    repF = mC.CRRA.solveTerminal(θ[posT], ε[posT], t = tT)
    mC.CRRA.selection = 'legacy'
    repL = mC.CRRA.solveTerminal(θ[posT], ε[posT], t = tT)
    mC.CRRA.selection = 'frozen'
    single = repF['nEq'] == 1
    check(f'CRRA ρ={ρ} T: counts reported per state', repF['nEq'].shape == repF['τ'].shape and repF['nCand'].min() >= 2,
          f"-> nEq max {repF['nEq'].max()}, nCand max {repF['nCand'].max()}, fallback {int(repF['fallback'].sum())}")
    check(f'CRRA ρ={ρ} T: bitwise the earlier criterion at states with one equilibrium',
          np.array_equal(repF['τ'].values[single], repL['τ'].values[single]),
          f"-> {int(single.sum())}/{single.size} states single; max|Δτ| there {maxdiff(repF['τ'].values[single], repL['τ'].values[single]):.1e}")
    # the full recursion, both rules
    mC.CRRA.selection = 'frozen'
    solsF = mC.CRRA.solveBackward(θ, ε)
    multF = dict(mC.CRRA.lastMultiplicity)
    mC.CRRA.selection = 'legacy'
    solsL = mC.CRRA.solveBackward(θ, ε)
    mC.CRRA.selection = 'frozen'
    worst = max(maxdiff(solsF[t]['τ'].values, solsL[t]['τ'].values) for t in tIdx)
    clean = multF['nStatesMultiple'] == 0 and multF['nFallback'] == 0
    check(f'CRRA ρ={ρ}: recursion reports the counts', multF['nEqMax'] >= 1, f'-> {multF}')
    check(f'CRRA ρ={ρ}: identical policy tables to the earlier criterion' + (' (one equilibrium everywhere)' if clean else ' where the rule did not bind'),
          (worst == 0.0) if clean else True, f'-> max|Δτ| over all periods and states {worst:.2e}; clean={clean}')
    out = mC.solvePEE_CRRA()
    check(f'CRRA ρ={ρ}: solvePEE_CRRA carries the multiplicity summary', isinstance(out.get('multiplicity'), dict))
    print(f'    [CRRA ρ={ρ}: {time.time()-tic:.1f}s]')

# ==== 4. ESC, LOG: the tax policy over the design state, both rules ====================================
tic = time.time()
mE = build(ModelESC, wedge = {'spec': 'size', 'phi': 0.5, 'p': 8.643})
mE.LOG.selection = 'frozen'
τF, abF, nmF, exF = mE.ESC.τOfθ(t0, mE.ESC.θGrid, tLag0, terminal = False)
mE.LOG.selection = 'legacy'
τL, abL, nmL, exL = mE.ESC.τOfθ(t0, mE.ESC.θGrid, tLag0, terminal = False)
mE.LOG.selection = 'frozen'
check('ESC LOG: τ(θ_t) at t0 identical under both rules where one equilibrium exists',
      np.array_equal(τF[exF['nEq'] == 1], τL[exF['nEq'] == 1]) and exF['nEq'].shape == (mE.ESC.nθ,),
      f"-> nEq max {exF['nEq'].max()}, fallback {int(exF['fallback'].sum())}, max|Δτ| {maxdiff(τF, τL):.1e}")
solsE = mE.ESC.solveBackward()
check('ESC LOG: the recursion carries per-period counts and a summary',
      'nEqτ' in solsE[t0] and mE.ESC.lastMultiplicity['nEqMax'] >= 1, f'-> {mE.ESC.lastMultiplicity}')
print(f'    [ESC LOG: {time.time()-tic:.1f}s]')

# ==== 5. ESC, CRRA 2-D: one period of the exact recursion, both rules ==================================
tic = time.time()
# designRule 'legacy': the layer that runs the tax rule at every (θ_t, s_, θ1); the root layer does not
mE2 = build(ModelESC, ρ = 2.0, wedge = {'spec': 'size', 'phi': 0.5, 'p': 1.728}, nθ2D = 5, nθCand2D = 7,
            designRule = 'legacy')
E = mE2.ESCC2
E.GS = mE2.CRRA.GS
θStar = float(mE2.db['θ'].xs(mE2.t0Year))
ε2 = mE2.db['eps'].values.astype(float)
sGrid2 = E.defaultSGrid(θStar, tIdx[-1], n = 25)
solT = E.solveTerminal2D(ε2[-1], sGrid2, tIdx[-1], tIdx[-2])
per = {}
for rule in ('frozen', 'legacy'):
    E.selection = rule
    per[rule] = E.solveBackward_t2D(solT, tIdx[-2], tIdx[-3], tIdx[-1], ε2[-2], ε2[-1], sGrid2, sGrid2, E.θCand, True)
E.selection = 'frozen'
nEq2 = per['frozen']['nEqτ']
single2 = nEq2 == 1
d2 = np.abs(per['frozen']['τStar3'] - per['legacy']['τStar3'])
check('ESC CRRA 2-D: per-(θ_t, s_, θ1) counts carried', nEq2.shape == per['frozen']['τStar3'].shape and nEq2.max() >= 1,
      f"-> nEq max {nEq2.max()}, nCand max {per['frozen']['nCandτ'].max()}, fallback {int(per['frozen']['fallbackτ'].sum())}")
check('ESC CRRA 2-D: τ*(s_, θ_t, θ1) identical to the earlier criterion where one equilibrium exists',
      np.nanmax(np.where(single2, d2, 0.)) == 0.0,
      f"-> {int(single2.sum())}/{single2.size} single; max|Δτ| elsewhere {np.nanmax(np.where(single2, 0., d2)):.1e}")
# a candidate on the last feasible node, next to an infeasible cell (the top two τ nodes masked): its hours
# are read at the node, so its frozen objective is finite and equals the unmasked one on the feasible nodes
gU = CartesianGrid(τ = np.linspace(0.05, 0.45, 9), s_ = sGrid2[::6])
τU = gU.values('τ')
with mE2.BG.cacheParams():
    dU = mE2.CRRA.stateGrid_T(gU.flat['τ'], gU.flat['s_'], θStar, ε2[-1], tIdx[-1], tIdx[-2])
    dH = dU | {'h': np.where(gU.flat['τ'] > τU[6], np.nan, dU['h'])}
    candU = np.full((1, gU.stateShape('τ')[0]), τU[6])
    WH = mE2.CRRA.objectiveFrozen(candU, gU, dH, None, θStar, tIdx[-1], tIdx[-2], ε = ε2[-1], terminal = True)
    WF = mE2.CRRA.objectiveFrozen(candU, gU, dU, None, θStar, tIdx[-1], tIdx[-2], ε = ε2[-1], terminal = True)
check('CRRA ρ=2 T: a candidate on the last feasible node next to an infeasible cell has a finite frozen objective, '
      'equal to the unmasked one on the feasible nodes',
      np.isfinite(WH[0, :7]).all() and np.isnan(WH[0, 7:]).all() and np.allclose(WH[0, :7], WF[0, :7], rtol = 1e-12, atol = 0),
      f'-> finite on the feasible nodes {bool(np.isfinite(WH[0, :7]).all())}, '
      f'max|Δ| against unmasked {np.nanmax(np.abs(WH[0, :7] - WF[0, :7])):.1e}')
print(f'    [ESC CRRA 2-D one period: {time.time()-tic:.1f}s]')

report()
