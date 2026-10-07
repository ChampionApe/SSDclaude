r""" The frozen-state design-choice layers for the CRRA leaded design (writing/US/num_esc.tex): LeadedCRRA2D's
root layer (designRule 'root', alg esc:crra2D), policyESCpilot's first-order-condition layer (alg
esc:crra2Dfoc), the split of LeadedCRRA2D.solveBackward_t2D they plug into, and the design counts through
the solver and runESCcrra.py's rows.

Run:  .venv\Scripts\python.exe python\US\test_designChoicePilot.py        (~2 min)

Setup as test_frozenSelection.py section 5: rho = 2, the 'size' wedge at lambda = 1.728, 5 design-state
nodes, 13 candidate designs, 25 savings nodes, the terminal period and the last choosing period.
  T1  sharesFrom(aOf(.)) is base.si_s at a common discount factor (eq:esc:aDef); aOf refuses otherwise.
  T2  under designRule 'legacy' (the layer pinned periods run) solveBackward_t2D reproduces four reference
      numbers of its period dict, to 1e-12 across processes (crossCuttingFindings #1).
  T3  both layers run the period: equilibria and fallbacks per state, and how far apart they land.
  T4  the frozen tax pass at the shares of the tax rule's own selection returns that selection.
  T5  the design derivative of the FOC layer against a central difference of the re-solved state.
  T6  the one-shot deviation check (eq:esc:stateEq:design) at every state, both layers.
  T8  the frozen pass's crossing next to the maximising node is roots1d's nearest root of the column.
  T9  the secant closing of eq:esc:aResidual lands on the bisection closing.
  T10 a recursion's multiplicity carries the tax and the design counts; -1 for the design under 'legacy'.
  T11 runESCcrra.py's row builders carry designRule, Ma and both sets of counts; mergeWrite takes the new
      columns against a csv without them.
"""
import os, sys, time, tempfile
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from modelESC import ModelESC
from gridsearch import roots1d
from policy import SUMMARY_NAMES, DESIGN_NAMES
from policyESC import LeadedCRRA2D, aOf, sharesFrom, frozenTaxPass, _alongτ, _cellCrossing
from policyESCpilot import resolveAt, deviationCheck, designSlopeAt, consistentTax, LeadedCRRA2DFOC

from gridsearch.testing import check, report

PARS = testmod.pars | {'ρ': 1.0, 'β': 0.7606187875476447, 'ω': 1.4536273947550569}
GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}
# T2's reference numbers of the legacy layer's period dict (fresh process)
REF_T2 = {'θNext': 111.47111977586651, 'τStar3': 395.12541942719207, 'τ00': 0.14243079889653795, 'nEqτ': 1625}


tic = time.time()
m = ModelESC(pars = PARS | {'ρ': 2.0}, wedge = {'spec': 'size', 'phi': 0.5, 'p': 1.728}, nθ2D = 5, nθCand2D = 13,
             **testmod.kwargs)
m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
m.LOG.initGS(GS)
BG, tIdx = m.BG, m.db['t']
E = LeadedCRRA2D(m, nθ = 5, nθCand = 13, designRule = 'legacy')
R = LeadedCRRA2D(m, nθ = 5, nθCand = 13)                      # the production default: root, Ma 5, secant
F = LeadedCRRA2DFOC(m, nθ = 5, nθCand = 13)
E.GS = R.GS = F.GS = m.CRRA.GS
check('the production defaults: ModelESC.ESCC2 and LeadedCRRA2D run the root layer at Ma = 5, secant closing',
      (m.ESCC2.designRule, m.ESCC2.Ma, R.designRule, R.Ma, R.aClose) == ('root', 5, 'root', 5, 'secant'),
      f'-> ESCC2 {m.ESCC2.designRule}/{m.ESCC2.Ma}, LeadedCRRA2D() {R.designRule}/{R.Ma}/{R.aClose}')
θStar = float(m.db['θ'].xs(m.t0Year))
ε = m.db['eps'].values.astype(float)
sGrid = E.defaultSGrid(θStar, tIdx[-1], n = 25)
solT = E.solveTerminal2D(ε[-1], sGrid, tIdx[-1], tIdx[-2])
t, tLag, t1 = tIdx[-2], tIdx[-3], tIdx[-1]
args = (solT, t, tLag, t1, ε[-2], ε[-1], sGrid, sGrid, E.θCand, True)

# ==== T1: the one-parameter family of the inherited shares ============================================
rng = np.random.default_rng(20261002)
worst = 0.
with BG.cacheParams():
    for _ in range(20):
        b, τ, θ = rng.uniform(0.2, 3.0), rng.uniform(0.01, 0.6), rng.uniform(0., 1.)
        B = np.full(m.ni, b)
        D = sharesFrom(BG, aOf(BG, B, τ, θ, tLag), tLag)
        S = BG.si_s(B, τ, θ, BG.Γs(B, τ, θ, tLag), tLag)
        worst = max(worst, float(np.max(np.abs(D - S))))
check('T1: sharesFrom(aOf(B, τ, θ)) equals base.si_s at a common B, twenty random draws, size wedge',
      worst <= 1e-13, f'-> max|ΔD| = {worst:.2e}')


class _UnequalβBG:
    """ BG with βi differing across types; everything else from the model. """
    def __getattr__(self, k):
        return getattr(BG, k)

    def get(self, k, t = None):
        return np.array([0.70, 0.76, 0.80]) if k == 'βi' else BG.get(k, t)


try:
    aOf(_UnequalβBG(), np.full(m.ni, 1.), 0.2, 0.5, tLag)
    raised = False
except ValueError:
    raised = True
check('T1: aOf raises when βi differs across types', raised)

# ==== T2: the legacy layer's period, against its reference numbers ======================================
new = E.solveBackward_t2D(*args)
check('T2: the period dict carries tCore and tChoose, and the five interpolants',
      all(k in new for k in ('tCore', 'tChoose', 'τPolicy', 'hPolicy', 'sPolicy', 'ΓsPolicy', 'θPolicy')),
      f"-> tCore {new.get('tCore', np.nan):.2f}s, tChoose {new.get('tChoose', np.nan):.2f}s")
nums = {'θNext': float(np.nansum(new['θNext'])), 'τStar3': float(np.nansum(new['τStar3'])),
        'τ00': float(new['τ'][0, 0]), 'nEqτ': int(new['nEqτ'].sum())}
ok = all(abs(nums[k] - REF_T2[k]) <= 1e-12*max(1., abs(REF_T2[k])) for k in REF_T2)
check("T2: designRule 'legacy' reproduces the four reference numbers, to 1e-12 relative (across processes, #1)", ok,
      '-> ' + ', '.join(f'{k} {nums[k]!r} (recorded {REF_T2[k]!r})' for k in REF_T2))

# ==== T3: both layers run the period =====================================================================
perR = R.solveBackward_t2D(*args)
perF = F.solveBackward_t2D(*args)
cellθ, cellτ = float(E.θCand[1] - E.θCand[0]), float(np.diff(E.GS['PEE']['solGrids']['τ']).max())
check('T3 root: one closed bracket at every state, no fallback',
      (perR['nEqθ'] == 1).all() and (perR['nBrθ'] == 1).all() and not perR['fallbackθ'].any(),
      f"-> nEqθ {np.unique(perR['nEqθ'])}, nBrθ max {perR['nBrθ'].max()}, fallback {int(perR['fallbackθ'].sum())}, "
      f"max|r(a*)| {np.nanmax(np.abs(perR['rStar'])):.1e}, {perR['nPass']} frozen passes, closing iterations per "
      f"state mean {perR['nIterθ'].mean():.2f} max {perR['nIterθ'].max()}")
n2 = int((perF['nEqθ'] > 1).sum())
cornerSel = int(perF['atBoundθ'].sum())
check('T3 foc: at least one equilibrium at every state, none selected at a corner, no fallback',
      (perF['nEqθ'] >= 1).all() and not perF['fallbackθ'].any() and cornerSel == 0,
      f"-> nEqθ {np.unique(perF['nEqθ'])}; {n2}/{perF['nEqθ'].size} states with two: the corner θ'=1 passes "
      f"selectMaxFrozen's one-cell clause when the interior maximum is the node next to it (13 candidates); "
      f"nCandθ max {perF['nCandθ'].max()}, {perF['nPass']} frozen passes")
dθ = float(np.nanmax(np.abs(perR['θNext'] - perF['θNext'])))
dτ = float(np.nanmax(np.abs(perR['τChosen'] - perF['τChosen'])))
check('T3: root and foc within one candidate cell in θ and one τ cell in τ, every state',
      dθ <= cellθ and dτ <= cellτ, f'-> max|Δθ| {dθ:.4f} (cell {cellθ:.4f}), max|Δτ| {dτ:.2e} (cell {cellτ:.4f})')
dθL = float(np.nanmax(np.abs(perR['θNext'] - new['θNext'])))
print(f'      [root against the legacy layer: max|Δθ| {dθL:.4f}]')

# ==== T4: the frozen tax pass ties to the tax rule ========================================================
core = E._periodCore(*args[:-1])
g, d = core['g'], core['d']
τGrid = g.values('τ')
nτ, ns_, nθ1 = g.shape
tax = consistentTax(E, core, E.θCand)
wC, wI = 0., 0.
nC, nI = 0, 0
with BG.cacheParams():
    for it, θt in enumerate(E.θGrid):
        τs = tax['τStar'][it]
        hs = _alongτ(τGrid, d['h'].reshape(nτ, -1), τs.reshape(-1))
        a = aOf(BG, BG.B(np.repeat(sGrid, nθ1), hs, tLag), τs.reshape(-1), float(θt), tLag).reshape(ns_, nθ1)
        τh = frozenTaxPass(E, core, float(θt), a)['τ']
        one = tax['nEqτ'][it] == 1
        cor, inn = one & tax['atBoundτ'][it], one & ~tax['atBoundτ'][it]
        if cor.any():
            wC, nC = max(wC, float(np.max(np.abs(τh - τs)[cor]))), nC + int(cor.sum())
        if inn.any():
            wI, nI = max(wI, float(np.max(np.abs(τh - τs)[inn]))), nI + int(inn.sum())
check('T4: the frozen pass at a = a_t(τ*, h_t(τ*)) returns the tax rule\'s interior τ* to (Δτ)²/4 '
      '(corner τ* to 1e-10 where there are any)', nI > 0 and wI <= 0.25*cellτ**2 and wC <= 1e-10,
      f'-> interior: max|τ̂ - τ*| {wI:.2e} over {nI} cells ((Δτ)²/4 = {0.25*cellτ**2:.1e}; the frozen crossing and '
      f'the consistent one differ at second order where a_t is nonlinear in τ within a cell); '
      f'corners: {wC:.1e} over {nC} cells')

# ==== T5: the design derivative against a central difference of the re-solved state =====================
it = int(np.argmin(np.abs(E.θGrid - 0.5)))
young = F.weights(t)[1]
θq, h = 0.45, 0.0125
rels, asyms = [], []
for js in (6, 12, 18):
    iτ = int(np.argmin(np.abs(τGrid - perR['τChosen'][it, js])))
    dlnc, _ = designSlopeAt(F, core, iτ, js, θq)
    pts = resolveAt(F, core, τGrid[iτ], sGrid[js], E.θGrid[it], np.array([θq - h, θq, θq + h]), 1.)
    spline = float((young*pts['hatc1iPow'][1]*dlnc).sum())
    Wy = pts['Wy']
    fd = (Wy[2] - Wy[0])/(2*h)
    rels.append((spline - fd)/abs(fd))
    asyms.append(((Wy[2] - Wy[1])/h - (Wy[1] - Wy[0])/h)/abs(fd))
check("T5: the spline ∂θ' of the young's term at θ'=0.45 within 25% of resolveAt's central difference (h=0.0125), three states",
      max(abs(r) for r in rels) <= 0.25,
      '-> (spline-fd)/|fd| ' + ', '.join(f'{r:+.3f}' for r in rels)
      + '; forward-backward asymmetry (fwd-bwd)/|fd| ' + ', '.join(f'{x:+.3f}' for x in asyms))
gridSlope = F._designDerivatives(core)['dv1i_dθ'].reshape(nτ, ns_, nθ1, -1)
iτ = int(np.argmin(np.abs(τGrid - perR['τChosen'][it, 12])))
at6 = designSlopeAt(F, core, iτ, 12, E.θCand[6])[0]
nodeSlope = gridSlope[iτ, 12, 6]/g.reshape(d['hatc1iPow'])[iτ, 12, 6]
check('T5: designSlopeAt at a node is the gridded fixed-knot derivative the FOC layer uses',
      np.max(np.abs(at6 - nodeSlope)) <= 1e-12, f'-> max diff {np.max(np.abs(at6 - nodeSlope)):.1e}')

# ==== T6: the one-shot deviation check at every state, both layers ======================================
for name, L, per in (('root', R, perR), ('foc', F, perF)):
    rel, gain = [], []
    for k, θt in enumerate(E.θGrid):
        dc = deviationCheck(L, core, float(θt), per['aStar'][k], per['θNext'][:, k])
        rel.append(dc['rel']); gain.append(dc['gain'])
    rmax, gmax = float(np.nanmax(rel)), float(np.nanmax(gain))
    if name == 'root':
        check('T6 root: no candidate design beats the chosen one at its a* by more than 1e-6 relative',
              rmax <= 1e-6, f'-> max gain {gmax:.2e}, relative {rmax:.2e}')
    else:
        check('T6 foc: the deviation gain at a_c* is below 1e-3 relative (regression bound)', rmax <= 1e-3,
              f'-> max gain {gmax:.2e}, relative {rmax:.2e}; the brief\'s 1e-6 '
              + ('holds' if rmax <= 1e-6 else 'does NOT hold at 13 candidates'))

# ==== T8: the cell-local crossing is roots1d's nearest root ================================================
# At each θ_t node and the root layer's own a* per state: z_t at the frozen shares, the maximising node of
# its integrated profile, and the crossing next to it (_cellCrossing) against every root of the column
# (roots1d._allRootsRagged) and the one nearest the node, as the pilot's pass took it.
parts, t_ = core['parts'], core['t']
worst, nOne, nMany, nManyDiff, nInner, tied = 0., 0, 0, 0, 0, True
for k, θt in enumerate(E.θGrid):
    a = np.where(np.isfinite(perR['aStar'][k]), perR['aStar'][k], 1.)
    aF = np.broadcast_to(a[None, :, None], (nτ, ns_, nθ1)).reshape(-1)
    with BG.cacheParams(), np.errstate(divide = 'ignore', invalid = 'ignore'):
        z = np.asarray(R.zAtShares(d, parts, float(θt), sharesFrom(BG, aF, tLag), t_), dtype = float).reshape(nτ, -1)
    P = roots1d.cumtrapzColumns(τGrid, z)
    fin = np.isfinite(z)
    usable = fin.sum(axis = 0) >= 2
    first = np.where(usable, fin.argmax(axis = 0), 0)
    last = np.where(usable, nτ - 1 - fin[::-1].argmax(axis = 0), 0)
    jmax = np.argmax(np.where(fin, P, -np.inf), axis = 0)
    inner = np.flatnonzero(usable & (jmax != first) & (jmax != last))
    cellX = _cellCrossing(τGrid, z, jmax[inner], inner)
    roots = roots1d._allRootsRagged(τGrid, z[:, inner], 0.0)
    nR = np.isfinite(roots).sum(axis = 0)
    node = τGrid[jmax[inner]]
    dist = np.where(np.isfinite(roots), np.abs(roots - node[None, :]), np.inf)
    near = roots[np.argmin(dist, axis = 0), np.arange(inner.size)] if roots.shape[0] else np.full(inner.size, np.nan)
    near = np.where(np.isfinite(near), near, node)
    one = nR == 1
    if one.any():
        worst = max(worst, float(np.max(np.abs(cellX - near)[one])))
    nOne, nMany, nInner = nOne + int(one.sum()), nMany + int((~one).sum()), nInner + inner.size
    nManyDiff += int(((~one) & (cellX != near)).sum())
    tied &= np.array_equal(frozenTaxPass(R, core, float(θt), a)['τ'].reshape(-1)[inner], cellX)
check("T8: the crossing next to the profile's maximising node equals roots1d's nearest root to 1e-12 where the column has one root",
      nOne > 0 and worst <= 1e-12,
      f'-> max|Δτ̂| {worst:.1e} over {nOne} of {nInner} interior columns (5 θ_t at a*); {nMany} columns with '
      f'another root count, {nManyDiff} of them with a different location')
check('T8: frozenTaxPass returns exactly that crossing on the interior columns', tied)

# ==== T9: the secant closing against the bisection closing ===============================================
RB = LeadedCRRA2D(m, nθ = 5, nθCand = 13, aClose = 'bisection')
RB.GS = m.CRRA.GS
chS = R._choose(core, R.θCand, True)
chB = RB._choose(core, RB.θCand, True)
dA = float(np.nanmax(np.abs(chS['aStar'] - chB['aStar'])))
dθ9 = float(np.nanmax(np.abs(chS['θNext'] - chB['θNext'])))
br = chS['nBrθ'] > 0
check('T9: the secant closing lands on the bisection closing, a* to 1e-9 and the same nEqθ at every state',
      dA <= 1e-9 and np.array_equal(chS['nEqθ'], chB['nEqθ']),
      f"-> max|Δa*| {dA:.1e}, max|Δθ'| {dθ9:.1e}; iterations per state secant mean {chS['nIterθ'][br].mean():.2f} "
      f"max {chS['nIterθ'].max()}, bisection mean {chB['nIterθ'][br].mean():.2f} max {chB['nIterθ'].max()}; "
      f"frozen passes {chS['nPass']} against {chB['nPass']}")

# ==== T10: the counts of a recursion, tax and design =====================================================
pin = int(m.db['t0'])           # pinned periods run the legacy layer, so the tax rule counts there
solsR = R.solvePolicies(θStar, pinPos = pin, sGrid = sGrid)
multR = dict(R.lastMultiplicity)
solsL = E.solvePolicies(θStar, pinPos = pin, sGrid = sGrid)
multL = dict(E.lastMultiplicity)
keys = set(SUMMARY_NAMES) | set(DESIGN_NAMES)
check("T10 root: solvePolicies' multiplicity carries both sets: the tax rule's (pinned periods) and the design layer's",
      keys <= set(multR) and multR['nEqMax'] >= 1 and multR['nEqθMax'] == 1 and multR['nBrθMax'] == 1
      and multR['nFallbackθ'] == 0 and multR['nStatesMultipleθ'] == 0,
      '-> ' + ', '.join(f'{k} {multR[k]}' for k in ('nEqMax', 'nCandMax', 'nFallback', 'nEqθMax', 'nBrθMax',
                                                    'nStatesMultipleθ', 'nFallbackθ')))
check("T10 legacy: the design counts are -1 (not counted), the tax counts are there",
      all(multL[k] == -1 for k in DESIGN_NAMES[:4]) and multL['nEqMax'] >= 1,
      '-> ' + ', '.join(f'{k} {multL[k]}' for k in ('nEqMax', 'nCandMax', 'nFallback', 'nEqθMax', 'nBrθMax',
                                                    'nStatesMultipleθ', 'nFallbackθ')))

# ==== T11: runESCcrra.py's rows ===============================================================================
# pathRowsFrom on the solveLeaded2D output of the T10 root recursion (base = the same output: the
# exogenous columns are not under test); the calibration and shock rows are built inline in runESCcrra.main
# from solverColumns(multiplicityOf(.)), checked here on the same output.
import runESCcrra
out = m.solveLeaded2D(pinAtT0 = True, sols = solsR)
rowsP = runESCcrra.pathRowsFrom(m, out, out, 2.0, 'size', 0.5, 1.728, False, 'exact', designRule = 'root', Ma = 5)
want = {'designRule': 'root', 'Ma': 5} | {k: multR[k] for k in ('nEqMax', 'nCandMax', 'nFallback', 'nEqθMax',
                                                               'nBrθMax', 'nFallbackθ')}
inline = runESCcrra.solverColumns('root', 5, runESCcrra.multiplicityOf(out))
check('T11: every path row carries designRule, Ma and the six counts of the recursion; solverColumns(multiplicityOf) '
      'gives the same columns for the inline rows',
      len(rowsP) > 0 and all({k: r[k] for k in want} == want for r in rowsP) and inline == want,
      f'-> {len(rowsP)} rows, {want}')
check('T11: a solve that counted nothing writes -1', set(runESCcrra.solverColumns('legacy', 5, None).values())
      - {'legacy', 5} == {-1})
with tempfile.TemporaryDirectory() as tmp:
    f = os.path.join(tmp, 'escPathCRRA.csv')
    old = pd.DataFrame([{k: r[k] for k in r if k not in want} | {'ρ': 0.5} for r in rowsP])
    old.to_csv(f, index = False)
    runESCcrra.mergeWrite(f, rowsP, runESCcrra.KEYPATH)
    back = pd.read_csv(f)
    newRows, oldRows = back[np.isclose(back['ρ'], 2.0)], back[np.isclose(back['ρ'], 0.5)]
check('T11: mergeWrite takes rows with the new columns against a csv without them (old rows kept, NaN there)',
      len(oldRows) == len(rowsP) and len(newRows) == len(rowsP) and oldRows['nEqθMax'].isna().all()
      and (newRows['nEqθMax'] == want['nEqθMax']).all() and (newRows['designRule'] == 'root').all(),
      f'-> {len(back)} rows back: {len(oldRows)} old, {len(newRows)} new')
print(f'    [{time.time()-tic:.1f}s]')

report()
