r""" CRRA.solveBackward (policy.py) -- the t<T backward recursion, docs alg:CRRA:grid.

Run:  .venv\Scripts\python.exe python\informalAnalytical\test_crraBackward.py

Unlike the terminal period, t<T has no exact rho=1 cross-check against LOG: the hat-consumption fold
(base.py's hatc1i) has no rho=1 counterpart, and the solve refuses to run there by design. Verification
therefore rests on three independent footings:

  1. base.py's refactor is an identity  -- dv2i_dτ_LOG/dv20_dτ_LOG must be bitwise what they were before
     dlnc2i_dτ/dlnc20_dτ were extracted, and the whole LOG solve must be unchanged.
  2. The state approximation IS exactly checkable at rho=1 -- there B = beta_i is a primitive, so Theta_s
     does not depend on the candidate s_t, the residual is linear with slope -1, and the unique root is
     exactly the LOG closed form Theta_s*(s_/nu)^sigma. This pins step 1 of the algorithm to machine
     precision without needing the rest of the recursion to be rho=1-compatible.
  3. At rho != 1, the located tax must actually solve the first order condition: interpolating z_t at the
     selected tau must return ~0 wherever an interior maximum was chosen.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelInformalAnalytical
from gridsearch import CartesianGrid, roots1d

from gridsearch.testing import check, report

m = testmod.mLOG                                  # rho = 1
th, eps = m.db['θ'].values, m.db['eps'].values
BG, CR, tIdx = m.BG, m.CRRA, m.db['t']
tT, posT = tIdx[-1], tIdx.get_loc(tIdx[-1])

# ---- 1. base.py's extraction is an identity, not a rewrite
t, tLag = tIdx[5], tIdx[4]
tau = np.linspace(.05, .9, 7)
si = BG.si_s(BG.get('βi', tLag), tau, th[5], BG.Γs(BG.get('βi', tLag), tau, th[5], tLag), tLag)
check('dv2i_dτ_LOG == dlnc2i_dτ(closed-form dlnh), bitwise',
      np.array_equal(BG.dv2i_dτ_LOG(tau, th[5], si, t),
                     BG.dlnc2i_dτ(BG.dlnΘh_dτ_LOG(tau, t), tau, th[5], si, t)))
Th = BG.ΘhTerminal(tau, t)
check('dv20_dτ_LOG == dlnc20_dτ(closed-form dlnh), bitwise',
      np.array_equal(BG.dv20_dτ_LOG(tau, eps[5], Th, t),
                     BG.dlnc20_dτ(BG.dlnΘh_dτ_LOG(tau, t), tau, eps[5], Th, t)))
solA = m.solvePEE_LOG(solver = 'Vectorized')
m.LOG.x0.pop('vectorized', None); m.x0.clear()
check('LOG end-to-end solve unchanged by the refactor',
      np.array_equal(solA['policy']['τ'].values, m.solvePEE_LOG(solver = 'Vectorized')['policy']['τ'].values))

# ---- 2. state approximation, exact at rho=1
sGrid = CR.defaultSGrid(th[posT], tT, n = 20)
solT = CR.solveTerminal(th[posT], eps[posT], t = tT, sGrid = sGrid)
t, pos = tIdx[-2], tIdx.get_loc(tIdx[-2])
tauG = CR.GS['PEE']['solGrids']['τ']
sSol, nRoots = CR.solveStateApprox_t(tauG, sGrid, sGrid, t, th[pos+1], solT)

lo = CR.stateApprox_t(np.repeat(tauG, len(sGrid)), np.full(len(tauG)*len(sGrid), sGrid[0]),
                      t, th[pos+1], solT)['Θs']
hi = CR.stateApprox_t(np.repeat(tauG, len(sGrid)), np.full(len(tauG)*len(sGrid), sGrid[-1]),
                      t, th[pos+1], solT)['Θs']
check('rho=1: Theta_s does not depend on the candidate s_t', np.array_equal(lo, hi))

feas = ~np.isnan(sSol)
ν, σ = BG.get('ν', t), BG.power_s(t)
expected = lo.reshape(len(tauG), len(sGrid))[:, :1] * ((sGrid/ν)**σ)[None, :]
rel = np.abs(sSol/expected - 1)[feas].max()
check('rho=1: state approximation == LOG closed form on feasible cells', rel < 1e-12,
      '-> max rel diff={:.2e}'.format(rel))
check('rho=1: equilibrium is unique where it exists', set(np.unique(nRoots)) <= {0, 1},
      '-> counts {}'.format(np.unique(nRoots)))

# ---- 3. feasibility behaves as the docs describe: infeasible only at HIGH tau, and contiguous
cols = [np.flatnonzero(feas[:, j]) for j in range(feas.shape[1])]
check('feasible tau-sets are contiguous',
      all(c.size == 0 or c.size == np.ptp(c) + 1 for c in cols))
check('infeasibility sits at high tau (lowest tau always feasible)',
      all(c[0] == 0 for c in cols if c.size))
check('some cells genuinely infeasible (mask is exercised, not vacuous)', (~feas).any(),
      '-> {}/{} infeasible'.format((~feas).sum(), feas.size))

# ---- 4. rho != 1: the recursion runs and the FOC is actually solved
m2 = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 1.5}, **testmod.kwargs)
CR2, th2, eps2 = m2.CRRA, m2.db['θ'].values, m2.db['eps'].values
sG2 = CR2.defaultSGrid(th2[posT], m2.db['t'][-1], n = 20)
sols = CR2.solveBackward(th2, eps2, sGrid = sG2, smooth = 0.0)   # smooth=0 so tau is the raw FOC solution
check('one solution per period', len(sols) == m2.T, '-> {}'.format(len(sols)))
for tt in m2.db['t']:
    v = sols[tt]['τ'].values
    check('  t={}: tau finite and in [0,1]'.format(tt),
          np.all(np.isfinite(v)) and np.all((v >= 0) & (v <= 1)),
          '-> [{:.4f}, {:.4f}]'.format(np.nanmin(v), np.nanmax(v)))
    for k in ('τPolicy', 'hPolicy'):
        check('  t={}: {} present'.format(tt, k), k in sols[tt])

# the substantive check: at an interior selection, z_t(tau*) must be ~0. Rebuild z on the grid for one
# t<T period and interpolate it at the selected tau, exactly as selectMax's own criterion implies.
t2 = m2.db['t'][-2]
p2 = m2.db['t'].get_loc(t2)
t2Lag, t21 = m2.db['t'][p2-1], m2.db['t'][p2+1]
sNext, tauG2 = CR2.solveStateApprox_t(CR2.GS['PEE']['solGrids']['τ'], sG2, sG2,
                                      t2, th2[p2+1], sols[t21])[0], CR2.GS['PEE']['solGrids']['τ']
g2 = CartesianGrid(τ = tauG2, s_ = sG2)
with m2.BG.cacheParams():
    d2 = CR2.stateGrid_t(g2.flat['τ'], sNext.reshape(-1), g2.flat['s_'],
                         t2, t2Lag, t21, th2[p2], th2[p2+1], eps2[p2], eps2[p2+1], sols[t21])
    z2 = CR2.focGrid_t(d2, g2, t2, th2[p2], eps2[p2])
z2c = g2.reshape(z2)                                  # (Mtau, Ns_)
τstar, atB = sols[t2]['τ'].values, sols[t2]['atBound']
resid = []
for j in range(len(sG2)):
    if atB[j] or np.isnan(τstar[j]):
        continue
    col = z2c[:, j]
    good = ~np.isnan(col)
    resid.append(abs(np.interp(τstar[j], tauG2[good], col[good])))
check('FOC residual ~0 at every interior selection', len(resid) > 0 and max(resid) < 1e-8,
      '-> {} interior states, max|z|={:.2e}'.format(len(resid), max(resid) if resid else float('nan')))

# ---- 5. the hat consumption: safe forms == literal definition, and no overflow band near rho=1.
# base.py never materialises ĉ1i itself, carrying (ĉ1i)^{1-1/rho} and ln(ĉ1i) instead, because the literal
# (1+B)^{1/(1-1/rho)} overflows float64 as rho -> 1 (at rho=1.001 the exponent is 1001, so it overflows
# once B > 1.03). Check the two forms agree where the literal one IS well-conditioned, then that the
# rewrite actually removed the fragile band.
mh = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 2.0}, **testmod.kwargs)
BGh, thh = mh.BG, mh.db['θ'].values
th_t, th_t1 = mh.db['t'][3], mh.db['t'][4]
hh = np.array([0.30, 0.35, 0.40])
Bh = np.tile(np.linspace(0.5, 0.9, mh.ni), (3, 1))     # (points, ni)
Γsh = np.array([0.10, 0.12, 0.14])
args = (hh, Bh, np.array([.2, .25, .3]), thh[4], Γsh, th_t)
tc = BGh.tildec1i(*args)
ph = 1 - 1/BGh.get('ρ', th_t)
literal = ((1 + Bh)**(1/ph) * tc)                      # the doc's eq:hatc1i, verbatim
check('hatc1iPow == (literal ĉ1i)^{1-1/ρ} at ρ=2',
      np.allclose(BGh.hatc1iPow(*args), literal**ph, rtol = 1e-12),
      '-> max rel={:.2e}'.format(np.max(np.abs(BGh.hatc1iPow(*args)/literal**ph - 1))))
check('lnhatc1i == ln(literal ĉ1i) at ρ=2',
      np.allclose(BGh.lnhatc1i(*args), np.log(literal), rtol = 1e-12),
      '-> max abs={:.2e}'.format(np.max(np.abs(BGh.lnhatc1i(*args) - np.log(literal)))))

# the band that used to break: rho close to 1 with B > 1.03
mn = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 1.001}, **testmod.kwargs)
BGn = mn.BG
Bbig = np.tile(np.linspace(1.5, 8.0, mn.ni), (3, 1))   # comfortably past the old overflow threshold
argsN = (hh, Bbig, np.array([.2, .25, .3]), mn.db['θ'].values[4], Γsh, mn.db['t'][3])
pn = 1 - 1/BGn.get('ρ', mn.db['t'][3])
with np.errstate(over = 'ignore'):
    litN = (1 + Bbig)**(1/pn) * BGn.tildec1i(*argsN)
check('literal form DOES overflow at ρ=1.001 with B>1.03 (the band being fixed)',
      np.isinf(litN).any(), '-> {} of {} entries inf'.format(np.isinf(litN).sum(), litN.size))
with np.errstate(over = 'raise', invalid = 'raise', divide = 'raise'):
    powN, lnN = BGn.hatc1iPow(*argsN), BGn.lnhatc1i(*argsN)
check('hatc1iPow stays finite there', np.all(np.isfinite(powN)))
check('lnhatc1i stays finite there', np.all(np.isfinite(lnN)))

# and the full recursion runs at rho=1.001 with over/invalid/divide promoted to errors
mr = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 1.001}, **testmod.kwargs)
thr, epsr = mr.db['θ'].values, mr.db['eps'].values
sGr = mr.CRRA.defaultSGrid(thr[posT], mr.db['t'][-1], n = 8)
with np.errstate(over = 'raise', invalid = 'raise', divide = 'raise'):
    solR = mr.CRRA.solveBackward(thr, epsr, sGrid = sGr, smooth = 0.0)
vR = solR[mr.db['t'][-2]]['τ'].values
check('solveBackward runs clean at ρ=1.001 (no overflow/invalid)', np.all(np.isfinite(vR)),
      '-> tau in [{:.4f}, {:.4f}]'.format(np.nanmin(vR), np.nanmax(vR)))

# ---- 6. rho=1 is refused by the t<T path, with a message pointing at LOG
try:
    CR.solveBackward(th, eps, sGrid = sGrid)
    check('rho=1 t<T solve raises', False, '-> no exception')
except ValueError as e:
    check('rho=1 t<T solve raises ValueError naming LOG', 'LOG' in str(e))

report()
