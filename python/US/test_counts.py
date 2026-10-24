r""" The candidate counts of every politico-economic solve, carried into the csv row its driver writes: the tax
rule's (nEqMax, nCandMax, nFallback; writing/US/num_robustroot.tex, eq:equilibriumTest) and the root design
layer's of the exact CRRA recursion (nEqθMax, nBrθMax, nFallbackθ; num_esc.tex, alg esc:crra2D), as
policy.multiplicityColumns writes them. A row records a count where it is non-negative; -1 is a solve that
selected no tax.

Run:  .venv\Scripts\python.exe python\US\test_counts.py        (~1 min)

  C1  a calibration point at rho = 1 (LOG): calibratePoint's record carries the counts of the PEE solve at the
      calibrated parameters, for the US (calibrateRhoGrid.toRow) and France (ModelFR, calibrateRhoGridEU.toRow).
  C2  a shock (acute ageing, rho = 1): shocks.runOne returns the full-effect solve's counts, and
      runShocksUS.effectRows writes them on the 'full' row and -1 on the 'ee' row (taxes held).
  C3  the permanent timing, LOG (rho = 1, the 'size' cost) and CRRA (rho = 2, three candidate designs):
      solvePermanent's 'multiplicity' covers every candidate's tax selections and the equilibrium at the
      choice; PermanentLOG.τPath returns its taxes bitwise unchanged with or without the counts.
  C4  the sequential stage (runESCcrra.stageSequential at rho = 1): every row carries the baseline solve's counts.
  C5  stationaryApproxESC's rows: the design-layer counts of a 2-D recursion (rho = 2, the last choosing period),
      and -1 for the design under LOG, whose design is a grid argmax.
"""
import os, sys, time, tempfile
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
import testEU
import shocks as sh
from model import ModelUS
from modelESC import ModelESC
from policy import multiplicityColumns, mergeMultiplicity, SUMMARY_NAMES
from policyESC import LeadedCRRA2D
import calibrateRhoGrid, calibrateRhoGridEU, runShocksUS, runESCcrra, stationaryApproxESC

from gridsearch.testing import check, report

GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}
PARS = testmod.pars | {'ρ': 1.0, 'β': 0.655483014875856, 'ω': 1.2308601504079868}
TAX = ('nEqMax', 'nCandMax', 'nFallback')
DESIGN = ('nEqθMax', 'nBrθMax', 'nFallbackθ')


def counted(row, cols = TAX):
    """ The row records the counts: every column present, an integer, non-negative, at least one equilibrium
    and one candidate. """
    v = [row.get(c, -1) for c in cols]
    return all(np.isfinite(x) and x >= 0 for x in v) and v[0] >= 1 and v[1] >= 1


def show(row, cols = TAX + DESIGN):
    return ', '.join(f'{c} {row[c]}' for c in cols if c in row)


tic = time.time()

# ==== C1: a calibration point, the US and France ==========================================================
m = ModelUS(pars = testmod.pars | {'ρ': 1.0}, commonX = True, **testmod.kwargs)
rec = m.calibratePoint(1.0, gridSettings = {'LOG': GS, 'CRRA': GS | {'ns': 50}})
row = calibrateRhoGrid.toRow(rec, 1.0, 'test')
check("C1 US: calibratePoint's record carries the PEE solve's counts and toRow writes them",
      isinstance(rec.get('multiplicity'), dict) and counted(row)
      and all(row[c] == rec['multiplicity'][c] for c in TAX), f'-> {show(row)}')
mFR = testEU.model('FR', commonX = True, ρ = 1.0)
recFR = mFR.calibratePoint(1.0, par = 'ρ', gridSettings = {'LOG': GS, 'CRRA': GS | {'ns': 50}})
rowFR = calibrateRhoGridEU.toRow(recFR, 1.0, 'test')
check("C1 France (ModelFR): the record carries the counts of the re-solve at the calibrated point; toRow writes them",
      counted(rowFR), f'-> {show(rowFR)}')

# ==== C2: a shock's full and economic-equilibrium rows ====================================================
m.db['dates'] = testmod.dates
t0 = m.db['t'][m.db['t0']]
base = m.solvePEE_LOG()
hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
r = sh.runOne(m, base, 'acute', {}, 'LOG', float(testmod.workweek), hbarRef)
rows = runShocksUS.effectRows(r, {'ρ': 1.0, 'preferences': 'LOG', 'family': 'ageing', 'scenario': r['label']})
full, ee = rows
check("C2: shocks.runOne returns the full-effect solve's counts; effectRows writes them on the 'full' row",
      full['effect'] == 'full' and counted(full) and full['τ'] == r['full']['τ'], f'-> full: {show(full)}')
check("C2: the 'ee' row (taxes held at the baseline path) writes -1",
      ee['effect'] == 'ee' and all(ee[c] == -1 for c in TAX) and ee['τ'] == r['ee']['τ'], f'-> ee: {show(ee)}')

# ==== C3: the permanent timing, LOG and CRRA ===============================================================
mP = ModelESC(pars = PARS, wedge = {'spec': 'size', 'phi': 0.5, 'p': 11.564}, **testmod.kwargs)
mP.db['dates'], mP.db['workweek'] = testmod.dates, testmod.workweek
mP.LOG.initGS(GS)
perm = mP.solvePermanent('LOG')
colsP = multiplicityColumns(perm.get('multiplicity'))
check("C3 LOG: solvePermanent's 'multiplicity' carries the counts of the choice's selections and the chosen path",
      counted(colsP), f"-> θ_perm {perm['θ']:.6f}; {show(colsP)}")
θPath = mP.θPathPermanent(perm['θ'])
τPlain = mP.ESCP.τPath(θPath)
τWith, multPath = mP.ESCP.τPath(θPath, withMultiplicity = True)
τAt = np.array([mP.ESCP.τAt(t, θPath[k]) for k, t in enumerate(mP.db['t'])])
check('C3 LOG: τPath gives the same taxes bitwise with and without its counts, and τAt\'s at every period',
      np.array_equal(τPlain, τWith) and np.array_equal(τPlain, τAt) and multPath['nEqMax'] >= 1,
      f"-> max|Δτ| {float(np.max(np.abs(τPlain - τAt))):.1e}; τPath counts nEqMax {multPath['nEqMax']}")
choice = mP.ESCP.solveFixedPoint(mP.t0Year, float(mP.db['θ'].xs(mP.t0Year)))['multiplicity']
want = mergeMultiplicity([choice, multPath])
check("C3 LOG: the row's counts merge the choice's (t0, t0+1, t0+2 at every candidate) and the chosen path's",
      all(perm['multiplicity'][k] == want[k] for k in SUMMARY_NAMES[:4]),
      f"-> choice nCandMax {choice['nCandMax']}, path nCandMax {multPath['nCandMax']}")

mC = ModelESC(pars = PARS | {'ρ': 2.0}, nθCandPerm = 3, **testmod.kwargs)
mC.db['dates'], mC.db['workweek'] = testmod.dates, testmod.workweek
mC.CRRA.initGS(GS | {'ns': 25})
permC = mC.solvePermanent('CRRA', verbose = False)
colsC = multiplicityColumns(permC.get('multiplicity'))
nOk = int(permC['cache']['ok'].sum())
check("C3 CRRA: solvePermanent's 'multiplicity' carries every candidate's solve and the equilibrium at the choice",
      counted(colsC) and nOk == 3 and all(s is not None for s in permC['cache']['mult']),
      f"-> θ_perm {permC['θ']:.4f} of {nOk} candidates; {show(colsC)}")

# ==== C4: the sequential stage's rows ======================================================================
with tempfile.TemporaryDirectory() as tmp:
    f = os.path.join(tmp, 'escSequentialCRRA.csv')
    runESCcrra.stageSequential([1.0], f, commonX = True, nθ = 21)
    seq = pd.read_csv(f)
check('C4: every row of the sequential stage carries the baseline solve\'s counts',
      len(seq) > 0 and all(counted(rw) for rw in seq.to_dict('records')),
      f"-> {len(seq)} rows; {show(seq.iloc[0].to_dict(), TAX)}")

# ==== C5: stationaryApproxESC's rows, the 2-D recursion's design layer and LOG =============================
m2 = ModelESC(pars = PARS | {'ρ': 2.0}, wedge = {'spec': 'size', 'phi': 0.5, 'p': 1.728}, nθ2D = 5, nθCand2D = 13,
              **testmod.kwargs)
m2.db['dates'], m2.db['workweek'] = testmod.dates, testmod.workweek
m2.LOG.initGS(GS)
R = m2.ESCC2
R.GS = m2.CRRA.GS
tIdx, T = m2.db['t'], m2.T
ε = m2.db['eps'].values.astype(float)
sGrid = R.defaultSGrid(float(m2.db['θ'].xs(m2.t0Year)), tIdx[-1], n = 25)
solT = R.solveTerminal2D(ε[-1], sGrid, tIdx[-1], tIdx[-2])
per = R.solveBackward_t2D(solT, tIdx[-2], tIdx[-3], tIdx[-1], ε[-2], ε[-1], sGrid, sGrid, R.θCand, True)
mult2D = LeadedCRRA2D.multiplicity({tIdx[-2]: per, tIdx[-1]: solT})


def statRows(ρ, method, mm, mult):
    ν = mm.db['ν'].values.astype(float)
    z = np.zeros(mm.T)
    conv = {np.round(v, 12): (0., 0.) for v in ν}
    return stationaryApproxESC.rows(ρ, method, mm, ν, z, z, z, z, z, z, z, z, conv, mult)


rows2D = statRows(2.0, 'CRRA2D', m2, mult2D)
check("C5 CRRA2D: every stationaryApproxESC row carries the 2-D recursion's design-layer counts",
      len(rows2D) == T and all(counted(rw, DESIGN) for rw in rows2D)
      and all(rw[c] == mult2D[c] for rw in rows2D for c in DESIGN), f'-> {show(rows2D[0])}')
mP.ESC.solveBackward()
rowsL = statRows(1.0, 'LOG', mP, mP.ESC.lastMultiplicity)
check('C5 LOG: the tax counts of the leaded LOG recursion, -1 for the design layer it does not have',
      all(counted(rw) and all(rw[c] == -1 for c in DESIGN) for rw in rowsL), f'-> {show(rowsL[0])}')
print(f'    [{time.time()-tic:.1f}s]')

report()
