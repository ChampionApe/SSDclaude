r""" policy.py's CRRA class -- the politico-economic equilibrium with two endogenous states.

Run:  .venv\Scripts\python.exe python\InformalSavings\test_peeCRRA.py

Four things are checked, in increasing order of how much machinery they exercise:

  1. The exact collapse at rho=1. Base.B's exponent makes B_T^i the primitive beta_i regardless of
     (s_,h), and every level factor c^{1-1/rho} becomes c^0=1, so CRRA.solveTerminal is then *literally*
     LOG.solveTerminal at every state: state-independent in s_{T-1} and equal to the LOG solve to machine
     precision. This is a closed-form identity, not a numerical coincidence, and it is why solveTerminal
     is deliberately not guarded against rho=1.
  2. z_T and z_t against the PRIMITIVES at rho != 1. W_t is rebuilt from indirect utilities
     (level^{1-1/rho}/(1-1/rho), with (1+B) folded into the young levels as eq:hatc1 prescribes) and
     differentiated in tau_t with the two predetermined ratios held fixed. At t<T the two states are
     re-solved EXACTLY at each perturbed tau by nested brentq, so the check sees the continuation channel.
  3. The unnesting of eq:iotaOfTauS. Both residuals must vanish at the reported (s_t, iota_t), and --
     the load-bearing claim -- iota_t(tau,s) must not depend on s_{t-1}, which is what makes solving it
     first exact rather than an approximation.
  4. The reachable set and the feasibility mask: the mask must be 2-dimensional (never a function of
     iota_{t-1}), and no period may hand its successor a state outside the grids.
"""
import os, sys
import numpy as np
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod

m = testmod.mLOG
LOG, CRRA, B, BG = m.LOG, m.CRRA, m.B, m.BG
tIdx = m.db['t']
θpath, εpath = m.db['θ'].values, m.db['eps'].values
t = tIdx[-1]
pos = tIdx.get_loc(t)
tLag = tIdx[pos - 1]
θ, ε = θpath[pos], εpath[pos]

from gridsearch.testing import check, report


# ---- 0. grid structure -------------------------------------------------------------------------------
check("GS['PEE'] carries both state/candidate pairs, all unset",
      set(CRRA.GS['PEE']['stateGrids']) == {'ι_', 's_'}
      and set(CRRA.GS['PEE']['solGrids']) == {'τ', 'ι', 's'}
      and all(CRRA.GS['PEE']['stateGrids'][k] is None for k in ('ι_', 's_')))
check("CRRA's τ grid is LOG's (initGS extends, not replaces)",
      np.array_equal(CRRA.GS['PEE']['solGrids']['τ'], LOG.GS['PEE']['solGrids']['τ']))

# ---- 1. exact collapse to LOG at ρ=1 -----------------------------------------------------------------
τGrid = CRRA.GS['PEE']['solGrids']['τ']
ιGrid = LOG.defaultIotaGrid(θ, ε, t)                      # LOG's, so both classes solve on one grid
sGrid = CRRA.defaultSGrid(θ, t)
solT_LOG = LOG.solveTerminal(θ, ε, t = t, ιGrid = ιGrid)
solT_1 = CRRA.solveTerminal(θ, ε, t = t, ιGrid = ιGrid, sGrid = sGrid)
τ1 = solT_1['τ'].values                                   # (Ms, Nι)
check('at ρ=1 CRRA terminal τ_T is state-independent in s_{T-1}',
      np.allclose(τ1, τ1[[0], :], atol = 1e-12),
      '-> max spread over s_={:.2e}'.format(np.abs(τ1 - τ1[[0], :]).max()))
check('at ρ=1 CRRA terminal τ_T equals LOG terminal τ_T at every state',
      np.allclose(τ1, solT_LOG['τ'].values[None, :], atol = 1e-12),
      '-> max|diff|={:.2e}'.format(np.abs(τ1 - solT_LOG['τ'].values[None, :]).max()))
try:
    CRRA._requireCRRA(t)
    check('at ρ=1 _requireCRRA raises', False)
except ValueError as e:
    check('at ρ=1 _requireCRRA raises, naming the LOG class', 'LOG' in str(e))

# ---- switch the model to ρ != 1 ----------------------------------------------------------------------
ρ = 1.15
m.db.update(m.adjPar('ρ', ρ))
p = 1 - 1/ρ
sGrid = CRRA.defaultSGrid(θ, t)
ιGrid = CRRA.defaultIotaGrid(θ, ε, t)
_gs = CRRA.GS['PEE']['gridSettings']
_sAnchor = m.steadyState_CRRA_solve(_gs['sAnchorτ'], θ, t = t)['s']
check('defaultSGrid: 0 < l_s and both bounds are multiples of s*(sAnchorτ)',
      sGrid[0] > 0 and np.isclose(sGrid[-1], _gs['pads'][1]*_sAnchor)
      and np.isclose(sGrid[0], max(_gs['δs'], _gs['pads'][0]*_sAnchor)),
      '-> [{:.4f}, {:.4f}] = ({}, {})·{:.4f}, n={}'.format(
          sGrid[0], sGrid[-1], _gs['pads'][0], _gs['pads'][1], _sAnchor, sGrid.size))
# The anchor is NOT s*(0): measured across ρ, s*(0) is perfectly ANTI-correlated with the reachable set's
# upper edge (it falls 83% while the box rises 20%), so no constant pad on it can track the box. That is
# the property the retune turned on, so pin it rather than only the resulting numbers.
check('defaultSGrid: s*(0) is a much larger, ρ-sensitive quantity -- the rejected anchor',
      m.steadyState_CRRA_solve(0.0, θ, t = t)['s'] > 2*_sAnchor,
      '-> s*(0)={:.4f} vs s*({})={:.4f}'.format(
          m.steadyState_CRRA_solve(0.0, θ, t = t)['s'], _gs['sAnchorτ'], _sAnchor))
check('defaultIotaGrid (CRRA steady state): 0 < l_ι, capped above',
      ιGrid[0] > 0 and ιGrid[-1] <= CRRA.GS['PEE']['gridSettings']['capι'],
      '-> [{:.4f}, {:.4f}], n={}'.format(ιGrid[0], ιGrid[-1], ιGrid.size))

# ---- 2a. z_T against the primitives at ρ≠1 -----------------------------------------------------------
def politicalObjective_T(τ, s_, ι_, siRatio_):
    """ W_T from the primitives: υ_{1,T}^i = (c̃_1^i)^{1-1/ρ}/(1-1/ρ), υ_{2,T}^j = (c_2^j)^{1-1/ρ}/(1-1/ρ).
    The informal young's term carries no τ_T at all. siRatio_ and ι_ are held fixed, as the policy maker
    does. """
    h = B.h(B.ΘhTerminal(τ, t), s_, t)
    zi = np.zeros(m.ni)
    u = lambda c: c**p/p
    old = (B.get('γi[t-1]', t)*B.ω2i(t)*u(B.c2i(h, s_, τ, θ, siRatio_, t))).sum() \
          + B.get('γ0[t-1]', t)*B.ω20(t)*u(B.c20(h, s_, ε, τ, ι_, t))
    young = (B.get('γi', t)*B.ω1i(t)*u(B.tildec1i(h, zi, 0.0, 0.0, 0.0, t))).sum()
    return old + B.get('ν', t)*young

solT = CRRA.solveTerminal(θ, ε, t = t, ιGrid = ιGrid, sGrid = sGrid)
hFD = 1e-6
for τ0, s0, ι0 in [(0.10, 0.005, 0.05), (0.30, 0.020, 0.30), (0.55, 0.030, 1.20)]:
    d = CRRA.stateGrid_T(np.atleast_1d(τ0), np.atleast_1d(s0), θ, t, tLag)
    zbar = CRRA.zbar_T(d, θ, t)
    from gridsearch import CartesianGrid
    g1 = CartesianGrid(τ = np.atleast_1d(τ0), s_ = np.atleast_1d(s0))
    zk = float(CRRA._zStateCRRA(zbar, d, ε, np.atleast_1d(ι0), t, g1)[0, 0, 0])
    fd = (politicalObjective_T(τ0 + hFD, s0, ι0, d['si_s_'][0])
          - politicalObjective_T(τ0 - hFD, s0, ι0, d['si_s_'][0])) / (2*hFD)
    check('z_T = dW_T/dτ_T from primitives at (τ={:.2f}, s_={:.3f}, ι_={:.2f})'.format(τ0, s0, ι0),
          np.isclose(zk, fd, rtol = 1e-5),
          '-> z={:+.6e}, fd={:+.6e}'.format(zk, fd))

# ---- 3. the state approximation and its unnesting ----------------------------------------------------
posR = pos - 1
tR, tR1, tRLag = tIdx[posR], tIdx[posR + 1], tIdx[posR - 1]
θR, θR1, εR, εR1 = θpath[posR], θpath[posR + 1], εpath[posR], εpath[posR + 1]

def iotaExact(τ, s):
    """ ι_t(τ_t,s_t) to solver tolerance -- eq:iotaOfTauS, which involves neither predetermined state. """
    def f(ι):
        d = CRRA.stateApprox_t(np.atleast_1d(float(τ)), np.atleast_1d(float(s)),
                               np.atleast_1d(float(ι)), tR, θR1, solT)
        return float(BG.s0_s(d['B01'], d['Θs'], d['τ1'], εR1, tR)[0] - ι)
    return optimize.brentq(f, ιGrid[0], ιGrid[-1], xtol = 1e-15, rtol = 8.9e-16)

def sExact(τ, s_):
    """ s_t(τ_t,s_{t-1}) -- eq:stateResidual:s, with ι_t eliminated first. Nested brentq: the exact
    version of the two 1-D grid searches, used to check them. """
    ν, σ = BG.get('ν', tR), BG.power_s(tR)
    def f(s):
        ι = iotaExact(τ, s)
        d = CRRA.stateApprox_t(np.atleast_1d(float(τ)), np.atleast_1d(float(s)),
                               np.atleast_1d(ι), tR, θR1, solT)
        return float(d['Θs'][0]) * (s_/ν)**σ - s
    return optimize.brentq(f, sGrid[0], sGrid[-1], xtol = 1e-16, rtol = 8.9e-16)

sCandGrid = CRRA.defaultSCandGrid(sGrid)
sSol, ιSol, nRootsS, nRootsι = CRRA.solveStateApprox_t(τGrid, sGrid, sCandGrid, ιGrid, tR, θR1, εR1, solT)
feas = ~np.isnan(sSol) & ~np.isnan(ιSol)
check('step 1 locates both states on most of 𝒯×𝒮',
      feas.sum(axis = 0).min() >= 2,
      '-> feasible τ per s_: min {} of {}'.format(int(feas.sum(axis = 0).min()), τGrid.size))
check('the state roots are single-valued where they exist',
      set(np.unique(nRootsS[feas])) <= {1} and set(np.unique(nRootsι[feas])) <= {1})

# The unnesting claim: iota_t depends on (tau, s) but NOT on which s_{t-1} produced that s.
ιA = iotaExact(0.30, 0.02)
check('ι_t(τ_t,s_t) is a function of (τ_t,s_t) alone -- no s_{t-1} enters eq:stateResidual:iota',
      np.isclose(ιA, iotaExact(0.30, 0.02)) and 's_' not in CRRA.stateApprox_t.__code__.co_varnames)

# The second factorisation, which _iotaOfTauS evaluates the block once per (s_t,ι_t) pair on the strength
# of: tau_t reaches eq:stateApprox ONLY through Theta_h. If a future edit routes tau into any of these
# five, _iotaOfTauS would silently return the value belonging to whichever tau happened to come first --
# so this is checked bitwise, not to a tolerance, and over the extremes of 𝒯 rather than nearby points.
sProbe = np.linspace(sGrid[0], sGrid[-1], 9)
ιProbe = np.linspace(ιGrid[0], ιGrid[-1], 9)
blk = CRRA._stateApproxSI(sProbe, ιProbe, tR, θR1, solT)
τFree = all(np.array_equal(np.asarray(CRRA.stateApprox_t(np.full_like(sProbe, τv), sProbe, ιProbe,
                                                        tR, θR1, solT)[k]), np.asarray(blk[k]))
            for τv in (τGrid[0], 0.5, τGrid[-1]) for k in ('τ1', 'h1', 'B1', 'B01', 'Γs'))
check('_stateApproxSI is bitwise independent of τ_t -- the factorisation _iotaOfTauS relies on',
      τFree, '-> τ1/h1/B1/B01/Γs identical at τ={:.4f}, 0.5, {:.4f}'.format(τGrid[0], τGrid[-1]))

for τ0 in (0.15, 0.35, 0.55):
    k = int(np.argmin(abs(τGrid - τ0)))
    for j in (5, 20):
        if not feas[k, j]:
            continue
        check('grid roots match exact nested brentq at (τ={:.2f}, s_={:.4f})'.format(τGrid[k], sGrid[j]),
              np.isclose(sSol[k, j], sExact(τGrid[k], sGrid[j]), rtol = 1e-3)
              and np.isclose(ιSol[k, j], iotaExact(τGrid[k], sSol[k, j]), rtol = 1e-3),
              '-> s_t: {:.6e} vs {:.6e}; ι_t: {:.6e} vs {:.6e}'.format(
                  sSol[k, j], sExact(τGrid[k], sGrid[j]), ιSol[k, j], iotaExact(τGrid[k], sSol[k, j])))

# ---- 2b. z_t against the primitives at t<T -----------------------------------------------------------
def politicalObjective_t(τ, s_, ι_, siRatio_):
    """ W_t from the primitives, with both states re-solved exactly at this τ. The young levels carry
    (1+B_{t+1}^j) as eq:hatc1 prescribes -- (ĉ)^{1-1/ρ} = (1+B)(c̃)^{1-1/ρ} -- so the discount factor's own
    τ_t-dependence through s_t is inside the differentiated object, not held fixed beside it. """
    s = sExact(τ, s_)
    ι = iotaExact(τ, s)
    d = CRRA.stateApprox_t(np.atleast_1d(float(τ)), np.atleast_1d(s), np.atleast_1d(ι), tR, θR1, solT)
    d = {k: np.asarray(v)[0] for k, v in d.items()}
    h = B.h(d['Θh'], s_, tR)
    u = lambda c: c**p/p
    v1i = (1 + d['B1']) * u(B.tildec1i(h, d['B1'], d['τ1'], θR1, d['Γs'], tR))
    v10 = (1 + d['B01']) * u(B.tildec10(s_, s, d['B01'], d['τ1'], εR1, tR))
    old = (B.get('γi[t-1]', tR)*B.ω2i(tR)*u(B.c2i(h, s_, τ, θR, siRatio_, tR))).sum() \
          + B.get('γ0[t-1]', tR)*B.ω20(tR)*u(B.c20(h, s_, εR, τ, ι_, tR))
    young = (B.get('γi', tR)*B.ω1i(tR)*v1i).sum() + B.get('γ0', tR)*B.ω10(tR)*v10
    return old + B.get('ν', tR)*young

from gridsearch import CartesianGrid
g2 = CartesianGrid(τ = τGrid, s_ = sGrid)
dR = CRRA.stateGrid_t(g2.flat['τ'], sSol.reshape(-1), ιSol.reshape(-1), g2.flat['s_'],
                      tR, tRLag, θR, θR1, εR1, solT)
zbarR = CRRA.zbar_t(dR, g2, θR, tR)
hFD = 1e-6
for k, j, ι0 in [(30, 10, 0.05), (45, 20, 0.30), (60, 10, 1.00)]:
    τ0, s_0 = τGrid[k], sGrid[j]
    zProfile = CRRA._zStateCRRA(zbarR, dR, εR, np.atleast_1d(ι0), tR, g2)[:, j, 0]
    siRatio_ = g2.reshape(dR['si_s_'])[k, j]
    fd = (politicalObjective_t(τ0 + hFD, s_0, ι0, siRatio_)
          - politicalObjective_t(τ0 - hFD, s_0, ι0, siRatio_)) / (2*hFD)
    implied = abs(zProfile[k] - fd)/abs(np.gradient(zProfile, τGrid)[k])
    check('z_t = dW_t/dτ_t from primitives at (τ={:.2f}, s_={:.4f}, ι_={:.2f})'.format(τ0, s_0, ι0),
          implied < 0.1*float(np.diff(τGrid).max()),
          '-> z={:+.4e}, fd={:+.4e}, implied τ error={:.1e} vs τ cell={:.1e}'.format(
              zProfile[k], fd, implied, float(np.diff(τGrid).max())))

# ---- 4. the full recursion, feasibility and reachability ---------------------------------------------
sols = CRRA.solveBackward(θpath, εpath, sGrid = sGrid, ιGrid = ιGrid)
check('solveBackward returns one solution per period', set(sols) == set(tIdx))
check('every period reports τ_t over the same 𝒮×𝒮_0',
      all(s['τ'].shape == (len(sGrid), len(ιGrid)) for s in sols.values()))
check('no NaN in any solved policy function',
      all(not np.isnan(s['τ'].values).any() for s in sols.values()))
check('every selected τ_t lies inside [l,u] (smoothing may not leave the admissible set)',
      all((s['τ'].values >= CRRA.GS['PEE']['gridSettings']['l']).all()
          and (s['τ'].values <= CRRA.GS['PEE']['gridSettings']['u']).all() for s in sols.values()),
      '-> min={:.4f}, max={:.4f}'.format(min(s['τ'].values.min() for s in sols.values()),
                                         max(s['τ'].values.max() for s in sols.values())))
check('the feasibility mask is 2-dimensional, on 𝒯×𝒮 only (never a function of ι_{t-1})',
      all(s['feasible'].shape == (τGrid.size, len(sGrid)) for k, s in sols.items() if k != t))
check('no period hands its successor a state outside 𝒮×𝒮_0 (eq:reachable)',
      all(not np.any(s['outOfGrid']) for k, s in sols.items() if k != t),
      '-> {} pairs outside'.format(sum(int(np.sum(s['outOfGrid'])) for k, s in sols.items() if k != t)))

# The reported states must solve the residuals they came from, at the SELECTED taxes -- and to the
# accuracy the grids can deliver, which is not the same thing for the two roots. Both are checked against
# refinement rather than against a fixed tolerance, since that is what distinguishes "grid-limited" from
# "wrong": the ι root is exact by construction (its residual is piecewise linear once 𝒮_0' is aligned with
# 𝒮_0), while the s root converges with |𝒮'| because B_{t+1}(s_t,h_{t+1}) is nonlinear in s_t.
def residualsAt(rep, sCand):
    τSel = rep['τ'].values.reshape(-1)
    sSel, ιSel = rep['s'].values.reshape(-1), rep['ι'].values.reshape(-1)
    s_Sel = np.repeat(sGrid, len(ιGrid))
    d = CRRA.stateApprox_t(τSel, sSel, ιSel, tR, θR1, solT)
    rι = BG.s0_s(d['B01'], d['Θs'], d['τ1'], εR1, tR) - ιSel
    rs = d['Θs']*((s_Sel/BG.get('ν', tR))**BG.power_s(tR)) - sSel
    return np.nanmax(np.abs(rι)), np.nanmax(np.abs(rs/sSel))

sR = sols[tR]
rι, rs = residualsAt(sR, sCandGrid)
check('reported ι_t solves eq:stateResidual:iota at the selected τ_t, essentially exactly',
      rι < 1e-6, '-> max|residual|={:.2e}'.format(rι))
check('reported s_t solves eq:stateResidual:s at the selected τ_t to grid accuracy',
      rs < 5e-4, '-> max relative residual={:.2e}'.format(rs))

fine = CRRA.solveBackward_t(sols[tR1], tR, tRLag, θR, θR1, εR, εR1, sGrid, ιGrid,
                            np.geomspace(sGrid[0], sGrid[-1], 4*len(sCandGrid)), ιGrid)
rιF, rsF = residualsAt(fine, None)
check("the s_t residual is grid-limited, not a bug: refining 𝒮' 4x shrinks it",
      rsF < rs/2, '-> {:.2e} -> {:.2e} on a 4x finer 𝒮\''.format(rs, rsF))
check("the ι_t residual does not depend on 𝒮' at all (it is not the binding grid)",
      np.isclose(rι, rιF, rtol = 0.5), '-> {:.2e} vs {:.2e}'.format(rι, rιF))
check('the policy interpolants reproduce the solution at the nodes',
      np.allclose(sR['τPolicy'](*np.meshgrid(sGrid, ιGrid, indexing = 'ij')), sR['τ'].values)
      and np.allclose(sR['sPolicy'](*np.meshgrid(sGrid, ιGrid, indexing = 'ij')), sR['s'].values))

report()
