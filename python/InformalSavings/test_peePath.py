r""" model.py's path solve -- the initial-state fixed point, the forward walk, and the exact re-solve.

Run:  .venv\Scripts\python.exe python\InformalSavings\test_peePath.py

Covers docs eq:initialFixedPoint / eq:forwardSim / §PEEpath. What is checked, in the order the path
solve performs it:

  1. The initial fixed point. The residual must vanish at the reported tau_1, the reported state must be
     the one initialState_solve gives at that tau_1, and -- the trap the scan exists for -- the solve
     must NOT return the degenerate root at the upper bracket end, where the extrapolated policy clips
     to u and makes the residual identically zero.
  2. The walk. tau_1 off the walk must equal the fixed point's own tau_1, since the walk evaluates the
     same policy function at the same state; and the state EE_report treats as pre-determined must be
     the state the walk started from.
  3. The containment guards. A path started outside the state grids must raise, and strict=False must
     return the same path flagged instead.
  4. The docs' grid diagnostic: the simulated iota against the iota of the exact re-solve. This is a
     resolution measurement, not a correctness one -- it sees an error the first order condition
     residual structurally cannot, since that residual is evaluated ON the grid.

Not covered here: a rebuild of the path from the primitives. The exact re-solve is EE_LOG_solve /
EE_CRRA_solve, whose own primitive checks live in test_ee.py.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod

m = testmod.mLOG
tIdx = m.db['t']
θpath, εpath = m.db['θ'].values, m.db['eps'].values
tFirst = m.B.tFirst

from gridsearch.testing import check, report


# ---- 1. LOG: the initial fixed point -----------------------------------------------------------------
solsLOG = m.LOG.solveBackward(θpath, εpath)
initLOG = m.initialStatePEE(solsLOG, θpath, εpath, 'LOG')
l = m.LOG.GS['PEE']['gridSettings']['l']
u = m.LOG.GS['PEE']['gridSettings']['u']

check('LOG initial fixed point residual vanishes',
      abs(initLOG['residual']) < 1e-10, '-> |resid|={:.2e}'.format(abs(initLOG['residual'])))
check('LOG initial τ_1 is interior, not the degenerate upper root',
      l + 1e-8 < initLOG['τ'] < u - 1e-8, '-> τ_1={:.6f} (u={:.4f})'.format(initLOG['τ'], u))
check('LOG initial τ_1 reproduces itself through the period-1 policy function',
      np.isclose(initLOG['τ'], float(solsLOG[tFirst]['τPolicy'](initLOG['ι'])), atol = 1e-10))
check('LOG initial ι_0 is §5-consistent at the converged τ_1',
      np.isclose(initLOG['ι'],
                 m.initialState_solve(initLOG['τ'], θpath[tFirst], εpath[tFirst], t = tFirst)['ι'],
                 rtol = 1e-12))
check('LOG initial ι_0 lies inside 𝒮_0',
      solsLOG[tFirst]['ι_'][0] <= initLOG['ι'] <= solsLOG[tFirst]['ι_'][-1],
      '-> ι_0={:.5f}'.format(initLOG['ι']))

# Half of the trap the grid scan exists for: at τ=u the steady state degenerates -- formal savings
# collapse, so ι_0 = s_0^0/s_0 diverges -- and the state leaves 𝒮_0 entirely, which is what the scan's
# NaN mask keys off. The other half (the residual there being identically zero) is a CRRA phenomenon
# here; see the CRRA section.
ιAtU = m.initialState_solve(u, θpath[tFirst], εpath[tFirst], t = tFirst)['ι']
check('LOG the top of 𝒯 implies a state outside 𝒮_0, and is masked rather than searched',
      ιAtU > solsLOG[tFirst]['ι_'][-1],
      '-> ι_0(u)={:.3e} vs u_ι={:.3f}'.format(ιAtU, solsLOG[tFirst]['ι_'][-1]))


# ---- 2. LOG: the walk --------------------------------------------------------------------------------
outLOG = m.solvePEE_LOG()
pathLOG, repLOG = outLOG['path'], outLOG['report']

check('LOG walk returns one τ per period', outLOG['τ'].index.equals(tIdx))
check('LOG walked τ_1 equals the fixed point τ_1',
      np.isclose(outLOG['τ'].values[tFirst], initLOG['τ'], atol = 1e-12),
      '-> |diff|={:.2e}'.format(abs(outLOG['τ'].values[tFirst] - initLOG['τ'])))
check('LOG walked states stay inside 𝒮_0', bool(pathLOG['inGrid'].all()))
check('LOG no period pins to a corner of 𝒯', not pathLOG['atBound'].any(),
      '-> at bound: {}'.format(list(tIdx[pathLOG['atBound']])))
check('LOG walk starts from the state EE_report treats as pre-determined',
      np.isclose(pathLOG['ι_'][0], initLOG['ι'], rtol = 1e-12))
check('LOG ι_t reports over db[txE]', len(pathLOG['ι']) == len(m.db['txE']))
check('LOG entering states are the lagged generated ones',
      np.allclose(pathLOG['ι_'][1:], pathLOG['ι']))


# ---- 3. LOG: the containment guards ------------------------------------------------------------------
ιGrid = solsLOG[tFirst]['ι_']
try:
    m.LOG.approximatePEE(solsLOG, θpath, εpath, 10*ιGrid[-1])
    check('a path started outside 𝒮_0 raises', False)
except RuntimeError as e:
    check('a path started outside 𝒮_0 raises', True)
    check('...and the message names 𝒮_0 rather than clipping silently', '𝒮_0' in str(e))
flagged = m.LOG.approximatePEE(solsLOG, θpath, εpath, 10*ιGrid[-1], strict = False)
check('strict=False returns the same path flagged instead of raising',
      (not flagged['inGrid'][0]) and len(flagged['τ']) == len(tIdx))


# ---- 4. LOG: the grid diagnostic ---------------------------------------------------------------------
# Docs §PEEpath: the simulated ι against the ι of the exact re-solve. A visible gap means 𝒮_0 is too
# coarse for the dynamics. Asserted against the state grid's own spacing rather than a magic tolerance --
# what matters is that the walk resolves the state to well inside a grid cell.
gapLOG = np.max(np.abs(pathLOG['ι'] - repLOG['ι'].values))
cellLOG = np.max(np.diff(ιGrid[(ιGrid >= pathLOG['ι'].min()) & (ιGrid <= pathLOG['ι'].max())]))
check('LOG simulated ι agrees with the exact re-solve to well inside a 𝒮_0 cell',
      gapLOG < 0.1*cellLOG,
      '-> max|gap|={:.2e} vs cell {:.2e} ({:.1%} of a cell)'.format(gapLOG, cellLOG, gapLOG/cellLOG))
check('LOG exact re-solve is the reported one, not the simulation',
      not np.array_equal(pathLOG['ι'], repLOG['ι'].values))

# The transition itself: docs eq:forwardSim writes ι_t = ι_t(τ_t), and under LOG the predetermined state
# drops out of that fixed point entirely -- so re-solving it at the walked τ_t is both exact-given-τ and
# free of ι_{t-1}, while ιPolicy interpolates the composition over ι_{t-1}. The two must agree at the
# nodes of 𝒮_0 and may differ between them; the gap is 𝒮_0's own contribution to the path error.
interpLOG = m.LOG.approximatePEE(solsLOG, θpath, εpath, initLOG['ι'], exact = False)
check('LOG re-solved and interpolated transitions agree to within the state grid',
      np.max(np.abs(interpLOG['ι'] - pathLOG['ι'])) < np.max(np.diff(ιGrid)),
      '-> max|diff|={:.2e}'.format(np.max(np.abs(interpLOG['ι'] - pathLOG['ι']))))
check('LOG re-solving the transition beats interpolating it against the exact re-solve',
      np.max(np.abs(pathLOG['ι'] - repLOG['ι'].values))
      <= np.max(np.abs(interpLOG['ι'] - repLOG['ι'].values)),
      '-> exact {:.2e} vs interpolated {:.2e}'.format(
          np.max(np.abs(pathLOG['ι'] - repLOG['ι'].values)),
          np.max(np.abs(interpLOG['ι'] - repLOG['ι'].values))))


# ---- switch the model to ρ != 1 ----------------------------------------------------------------------
ρ = 1.15
m.db.update(m.adjPar('ρ', ρ))

outCRRA = m.solvePEE_CRRA()
pathC, repC, solsC = outCRRA['path'], outCRRA['report'], outCRRA['sols']
initC = m.initialStatePEE(solsC, θpath, εpath, 'CRRA')

check('CRRA initial fixed point residual vanishes',
      abs(initC['residual']) < 1e-10, '-> |resid|={:.2e}'.format(abs(initC['residual'])))
check('CRRA initial τ_1 is interior, not the degenerate upper root',
      l + 1e-8 < initC['τ'] < u - 1e-8, '-> τ_1={:.6f}'.format(initC['τ']))
check('CRRA initial τ_1 reproduces itself through the period-1 policy function',
      np.isclose(initC['τ'], float(solsC[tFirst]['τPolicy'](initC['s'], initC['ι'])), atol = 1e-10))
check('CRRA initial state lies inside 𝒮×𝒮_0',
      solsC[tFirst]['s_'][0] <= initC['s'] <= solsC[tFirst]['s_'][-1]
      and solsC[tFirst]['ι_'][0] <= initC['ι'] <= solsC[tFirst]['ι_'][-1],
      '-> (s_0,ι_0)=({:.5f}, {:.5f})'.format(initC['s'], initC['ι']))
check('CRRA walked τ_1 equals the fixed point τ_1',
      np.isclose(outCRRA['τ'].values[tFirst], initC['τ'], atol = 1e-12))

# The trap in full, and the reason initialStatePEE scans before it brackets. At τ=u the implied state has
# left 𝒮×𝒮_0 by orders of magnitude, so τPolicy is extrapolating; here it comes back ABOVE u, clips to
# u, and the residual u - u is EXACTLY zero. brentq on [l,u] accepts that bracket and returns the
# endpoint -- the degenerate steady state -- without ever looking inside. Which way this falls is luck:
# the same evaluation under LOG extrapolates to a negative tax, clips to l, and leaves residual(u)≈1.
initAtU = m.initialState_solve(u, θpath[tFirst], εpath[tFirst], t = tFirst)
τAtU = float(solsC[tFirst]['τPolicy'](initAtU['s'], initAtU['ι']))
check('CRRA at τ=u the implied state has left 𝒮_0 by orders of magnitude',
      initAtU['ι'] > 100*solsC[tFirst]['ι_'][-1],
      '-> ι_0(u)={:.3e} against u_ι={:.4f}'.format(initAtU['ι'], solsC[tFirst]['ι_'][-1]))
# WHICH WAY the extrapolation falls is luck, and the 2026-08-19 grid retune flipped it: on the wider grid
# τPolicy(u) came back ABOVE u, clipped to u, and made residual(u) exactly 0 -- a root brentq would have
# accepted. On the narrower grid it extrapolates to a large NEGATIVE tax, clips to l, and leaves
# residual(u)≈u-l instead. Both are the same defect, so assert the defect and not the coin toss: the
# policy is being evaluated far outside its own grid, so whatever the clip returns carries no information
# about a root, and a bracketed solve on [l,u] cannot tell the two cases apart.
check('CRRA τPolicy(u) is a meaningless extrapolation, not a policy value (why the scan is not optional)',
      not (l <= τAtU <= u),
      '-> extrapolated τPolicy={:.3f}, outside 𝒯=[{:.4f}, {:.4f}]'.format(τAtU, l, u))
check('CRRA the clipped residual at u is degenerate -- pinned to an endpoint either way',
      np.isclose(np.clip(τAtU, l, u), l) or np.isclose(np.clip(τAtU, l, u), u),
      '-> clips to {:.4f}, residual(u)={:.4f}'.format(np.clip(τAtU, l, u), u - np.clip(τAtU, l, u)))
check('CRRA the located root is not that endpoint',
      initC['τ'] < 0.5*u, '-> τ_1={:.6f}'.format(initC['τ']))

check('CRRA walked states stay inside 𝒮×𝒮_0', bool(pathC['inGrid'].all()))
check('CRRA walked states stay inside the previous period\'s reachable set 𝒫_t',
      bool(pathC['inReach'].all()))
check('CRRA no period pins to a corner of 𝒯', not pathC['atBound'].any(),
      '-> at bound: {}'.format(list(tIdx[pathC['atBound']])))
check('CRRA entering states are the lagged generated ones',
      np.allclose(pathC['s_'][1:], pathC['s']) and np.allclose(pathC['ι_'][1:], pathC['ι']))

# The warm start must be the simulated (Γs,h,s) in EE_CRRA_residual's own layout, not a reordering.
x0 = np.concatenate([pathC['Γs'], pathC['h'], pathC['s']])
ns = m.ns['EE_CRRA']
check('CRRA warm start unstacks back into the simulated (Γs,h,s)',
      np.allclose(ns(x0, 'Γs'), pathC['Γs']) and np.allclose(ns(x0, 'h'), pathC['h'])
      and np.allclose(ns(x0, 's'), pathC['s']))
check('CRRA warm start is finite everywhere', bool(np.isfinite(x0).all()))

# Same diagnostic as the log case, for both states.
sGrid, ιGridC = solsC[tFirst]['s_'], solsC[tFirst]['ι_']
gapS = np.max(np.abs(pathC['s'] - repC['s'].values[:-1]))
cellS = np.max(np.diff(sGrid))
gapI = np.max(np.abs(pathC['ι'] - repC['ι'].values))
cellI = np.max(np.diff(ιGridC[(ιGridC >= pathC['ι'].min()) & (ιGridC <= pathC['ι'].max())]))
check('CRRA simulated s agrees with the exact re-solve to well inside a 𝒮 cell',
      gapS < 0.1*cellS,
      '-> max|gap|={:.2e} vs cell {:.2e} ({:.1%} of a cell)'.format(gapS, cellS, gapS/cellS))
check('CRRA simulated ι agrees with the exact re-solve to well inside a 𝒮_0 cell',
      gapI < 0.1*cellI,
      '-> max|gap|={:.2e} vs cell {:.2e} ({:.1%} of a cell)'.format(gapI, cellI, gapI/cellI))

interpC = m.CRRA.approximatePEE(solsC, θpath, εpath, initC['s'], initC['ι'], exact = False)
check('CRRA re-solved and interpolated transitions agree to within the state grids',
      np.max(np.abs(interpC['s'] - pathC['s'])) < np.max(np.diff(sGrid))
      and np.max(np.abs(interpC['ι'] - pathC['ι'])) < np.max(np.diff(ιGridC)),
      '-> max|Δs|={:.2e}, max|Δι|={:.2e}'.format(np.max(np.abs(interpC['s'] - pathC['s'])),
                                                 np.max(np.abs(interpC['ι'] - pathC['ι']))))
check('CRRA re-solving the transitions beats interpolating them against the exact re-solve',
      gapS <= np.max(np.abs(interpC['s'] - repC['s'].values[:-1]))
      and gapI <= np.max(np.abs(interpC['ι'] - repC['ι'].values)),
      '-> s: exact {:.2e} vs interpolated {:.2e} | ι: exact {:.2e} vs interpolated {:.2e}'.format(
          gapS, np.max(np.abs(interpC['s'] - repC['s'].values[:-1])),
          gapI, np.max(np.abs(interpC['ι'] - repC['ι'].values))))

# Both solvers return the keys §8's calibration drives them through.
for name, out in (('LOG', outLOG), ('CRRA', outCRRA)):
    check(f'solvePEE_{name} returns the keys calibration_report reads',
          {'τ', 'sol', 'report'} <= set(out)
          and {'h', 's', 's_'} <= set(out['report']))

report()
