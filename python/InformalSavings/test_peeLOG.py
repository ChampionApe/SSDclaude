r""" LOG.solveTerminal (policy.py) -- the terminal-period politico-economic equilibrium with a state.

Run:  .venv\Scripts\python.exe python\InformalSavings\test_peeLOG.py

Three things are worth testing here, and none of them is a regression check against our own output:

  1. z_T against the PRIMITIVES. The political objective W_T is rebuilt from indirect utilities evaluated
     with base.py's consumption functions -- ln(c̃_{1,T}^j) for the young, ln(c_{2,T}^j) for the old, the
     same weights FOC applies -- and differentiated numerically in τ_T with s_{T-1,i}/s_{T-1} and ι_{T-1}
     held fixed, as the policy maker does. z_T must reproduce that. This is what makes the closed forms
     (dv1iTerminal_dτ_LOG, dlnc2i_dτ, dlnc20_dτ) checkable rather than merely asserted.
  2. eq:zdecomposition, numerically. The rank-one broadcast is the design's load-bearing shortcut, so the
     (M,M_ι) matrix it assembles is compared against z_T evaluated pointwise over the full Cartesian
     product through base.py's dlnc20_dτ. They must agree to machine precision.
  3. Structure. At ε=0 the state term vanishes identically (A_T=0), so τ_T(ι_{T-1}) must be EXACTLY flat --
     a closed-form identity, not a numerical coincidence. And by eq:logsep, z_T must not depend on s_{T-1}
     at all, which the primitive-side rebuild can check directly since it does use a savings level.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from gridsearch import CartesianGrid, griddedInterp1D

m = testmod.mLOG                      # ρ=1 calibration
LOG = m.LOG
B, BG = m.B, m.BG
θpath, εpath = m.db['θ'].values, m.db['eps'].values
tIdx = m.db['t']
t = tIdx[-1]
pos = tIdx.get_loc(t)
tLag = tIdx[pos - 1]
θ, ε = θpath[pos], εpath[pos]

from gridsearch.testing import check, report


# ---- 0. self.GS structure -------------------------------------------------------------------------
check("GS['PEE']['solGrids']['τ'] matches its own gridSettings",
      np.allclose(LOG.GS['PEE']['solGrids']['τ'][[0, -1]],
                  [LOG.GS['PEE']['gridSettings']['l'], LOG.GS['PEE']['gridSettings']['u']]))
check("GS['PEE'] carries both ι slots, unset (𝒮_0 as a state, 𝒮_0' as candidates)",
      set(LOG.GS['PEE']['stateGrids']) == {'ι_'} and LOG.GS['PEE']['stateGrids']['ι_'] is None
      and LOG.GS['PEE']['solGrids']['ι'] is None)

# ---- 1. the default state grid --------------------------------------------------------------------
ιGrid = LOG.defaultIotaGrid(θ, ε, t)
τGrid = LOG.GS['PEE']['solGrids']['τ']
ιStar = B.s0_s(B.get('β0', t), m.steadyState_LOG_solve(τGrid, θ, t = t)['Θs'], τGrid, ε, t)
pad = LOG.GS['PEE']['gridSettings']['padι']
check('defaultIotaGrid: l_ι > 0 strictly (keeps dv20 pole off the grid)', ιGrid[0] > 0,
      '-> l_ι={:.3e}'.format(ιGrid[0]))
check('defaultIotaGrid: BOTH bounds are multiples of min_τ ι*(τ)',
      np.isclose(ιGrid[0], max(LOG.GS['PEE']['gridSettings']['δι'], pad[0]*ιStar.min()))
      and np.isclose(ιGrid[-1], min(pad[1]*ιStar.min(), LOG.GS['PEE']['gridSettings']['capι'])),
      '-> [{:.4f}, {:.4f}] = ({}, {})·{:.4f}'.format(ιGrid[0], ιGrid[-1], pad[0], pad[1], ιStar.min()))
# Anchoring the top on the minimum rather than the maximum is the whole point: max_τ ι*(τ) diverges as
# τ→1, so a rule written on it has no finite content and the real bound was whatever capι was set to --
# an absolute number that would not survive a change of data. capι stays as a backstop, and on this
# calibration it must be inert, or the rule is back to being decided by an arbitrary constant.
check('defaultIotaGrid: max_τ ι*(τ) diverges, which is why it is not the anchor',
      ιStar.max() > 100*ιStar.min(), '-> min {:.4f} vs max {:.3e}'.format(ιStar.min(), ιStar.max()))
check('defaultIotaGrid: capι is a backstop, not the operative bound',
      ιGrid[-1] < LOG.GS['PEE']['gridSettings']['capι'],
      '-> u_ι={:.4f} against cap {}'.format(ιGrid[-1], LOG.GS['PEE']['gridSettings']['capι']))
check('defaultIotaGrid: strictly increasing', np.all(np.diff(ιGrid) > 0),
      '-> [{:.3e}, {:.3e}], n={}'.format(ιGrid[0], ιGrid[-1], ιGrid.size))

# ---- 2. z_T against the primitives -----------------------------------------------------------------
# W_T rebuilt from indirect utilities. siRatio_ and ι_ are arguments, NOT recomputed inside: the policy
# maker takes both as predetermined, so the finite difference below must hold them fixed while τ_T moves.
def politicalObjective(τ, s_, ι_, siRatio_):
    """ W_T = ω Σ_j γ_{T-1,j}p_{T-1,j}μ_{T-1,j}ln(c_{2,T}^j) + ν_T Σ_j γ_{T,j}μ_{T,j}ln(c̃_{1,T}^j),
    with the terminal collapse B_{T+1}=0, Γ_{s,T}=0, τ_{T+1}=0 (docs eq:TerminalEE). """
    Θh = B.ΘhTerminal(τ, t)
    h = B.h(Θh, s_, t)
    zi = np.zeros(m.ni)
    tc1i = B.tildec1i(h, zi, 0.0, 0.0, 0.0, t)
    tc10 = B.tildec10(s_, 0.0, 0.0, 0.0, 0.0, t)
    c2i = B.c2i(h, s_, τ, θ, siRatio_, t)
    c20 = B.c20(h, s_, ε, τ, ι_, t)
    old = (B.get('γi[t-1]', t)*B.ω2i(t)*np.log(c2i)).sum() + B.get('γ0[t-1]', t)*B.ω20(t)*np.log(c20)
    young = (B.get('γi', t)*B.ω1i(t)*np.log(tc1i)).sum() + B.get('γ0', t)*B.ω10(t)*np.log(tc10)
    return old + B.get('ν', t)*young

def zPolicy(τ, ι_):
    """ z_T(τ_T, ι_{T-1}) through policy.py's own path, at scalar (τ, ι_). Returns (z, si_s_ used). """
    d = LOG.stateGrid_T(np.atleast_1d(float(τ)), θ, t, tLag)
    z = LOG._zState(LOG.zbar_T(d, θ, t), np.atleast_1d(float(τ)), ε, np.atleast_1d(float(ι_)), t)
    return float(z[0, 0]), d['si_s_'][0]

h = 1e-6
for τ0 in (0.05, 0.25, 0.60):
    for ι0 in (0.08, 1.0, 25.0):
        for s_ in (0.5, 4.0):
            z, siRatio_ = zPolicy(τ0, ι0)
            fd = (politicalObjective(τ0 + h, s_, ι0, siRatio_)
                  - politicalObjective(τ0 - h, s_, ι0, siRatio_)) / (2*h)
            check('z_T = dW_T/dτ_T from primitives at (τ={:.2f}, ι_={:5.2f}, s_={:.1f})'.format(τ0, ι0, s_),
                  np.isclose(z, fd, rtol = 1e-6),
                  '-> z={:+.6e}, fd={:+.6e}'.format(z, fd))

# By eq:logsep the FOC cannot depend on the savings level; the block above already re-used one z for two
# s_ values, so agreement there IS the invariance -- restated here as its own line for visibility.
zA = (politicalObjective(0.3 + h, 0.5, 1.0, zPolicy(0.3, 1.0)[1])
      - politicalObjective(0.3 - h, 0.5, 1.0, zPolicy(0.3, 1.0)[1])) / (2*h)
zB = (politicalObjective(0.3 + h, 50.0, 1.0, zPolicy(0.3, 1.0)[1])
      - politicalObjective(0.3 - h, 50.0, 1.0, zPolicy(0.3, 1.0)[1])) / (2*h)
check('dW_T/dτ_T is invariant to s_{T-1} (eq:logsep)', np.isclose(zA, zB, rtol = 1e-6),
      '-> {:+.6e} vs {:+.6e}'.format(zA, zB))

# ---- 3. eq:zdecomposition: the rank-one broadcast vs. the full product ------------------------------
sol = LOG.solveTerminal(θ, ε, t = t, ιGrid = ιGrid)
g = CartesianGrid(τ = τGrid, ι_ = ιGrid)
dFull = LOG.stateGrid_T(g.flat['τ'], θ, t, tLag)
zFull = BG.FOC(BG.dv1iTerminal_dτ_LOG(g.flat['τ'], t), np.zeros(g.size),
               BG.dlnc2i_dτ(dFull['dlnh'], g.flat['τ'], θ, dFull['si_s_'], t),
               BG.dlnc20_dτ(dFull['dlnh'], g.flat['τ'], ε, g.flat['ι_'], t), t)
check('eq:zdecomposition -- rank-one broadcast == pointwise z_T over 𝒯×𝒮_0',
      np.allclose(sol['z'], zFull.reshape(g.shape), rtol = 1e-12, atol = 1e-12),
      '-> max|diff|={:.3e}'.format(np.abs(sol['z'] - zFull.reshape(g.shape)).max()))

# ---- 4. the solved policy function ------------------------------------------------------------------
τSol = sol['τ'].values
check('solveTerminal reports τ_T over 𝒮_0 with matching shapes',
      τSol.shape == ιGrid.shape and sol['z'].shape == (τGrid.size, ιGrid.size)
      and np.allclose(sol['τ'].index.values, ιGrid))
check('selected τ_T lies inside [l,u]', np.all((τSol >= τGrid[0]) & (τSol <= τGrid[-1])),
      '-> τ ∈ [{:.4f}, {:.4f}]'.format(τSol.min(), τSol.max()))
interior = ~np.asarray(sol['atBound'])
zAtSol = np.array([np.interp(τSol[j], τGrid, sol['z'][:, j]) for j in range(ιGrid.size)])
check('z_T ≈ 0 at every interior selection (grid-resolution accuracy)',
      (not interior.any()) or np.max(np.abs(zAtSol[interior])) < 1e-6,
      '-> {} interior, max|z|={:.3e}'.format(int(interior.sum()),
                                             np.max(np.abs(zAtSol[interior])) if interior.any() else 0.0))
check('τPolicy/ΘhPolicy reproduce the solution at the nodes',
      np.allclose(sol['τPolicy'](ιGrid), τSol)
      and np.allclose(sol['ΘhPolicy'](ιGrid), B.ΘhTerminal(τSol, t)))
check('τ_T(ι_{T-1}) is decreasing in the state (more own savings -> less pension demanded)',
      np.all(np.diff(τSol) <= 1e-12),
      '-> τ(l_ι)={:.4f}, τ(u_ι)={:.4f}'.format(τSol[0], τSol[-1]))

# ---- 5. ε=0: the state term vanishes identically ----------------------------------------------------
sol0 = LOG.solveTerminal(θ, 0.0, t = t, ιGrid = ιGrid)
check('at ε=0 the FOC has no state term, so τ_T(ι_{T-1}) is exactly flat',
      np.allclose(sol0['τ'].values, sol0['τ'].values[0], atol = 0, rtol = 0),
      '-> range={:.3e}'.format(sol0['τ'].values.max() - sol0['τ'].values.min()))
check('at ε=0 z_T is exactly state-independent',
      np.allclose(sol0['z'], sol0['z'][:, [0]], atol = 0, rtol = 0))


# ====================================================================================================
#   t < T: the backward recursion
# ====================================================================================================
posR = pos - 1                        # the period solved against a t+1 continuation
tR, tR1 = tIdx[posR], tIdx[posR + 1]
tRLag = tIdx[posR - 1]
θR, θR1, εR, εR1 = θpath[posR], θpath[posR + 1], εpath[posR], εpath[posR + 1]

# ---- 6. the numerical derivatives, isolated against a closed form -----------------------------------
# Hold the continuation policy CONSTANT in the state. τ_{t+1} is then constant along τ_t, so the whole
# eq:v1LOG profile collapses to the analytical LOG derivative that this model does NOT have in general:
#     dυ_{1,t}^i/dτ_t = -(1+ξ)/((1+αξ)(1-τ_t))·(1+β_{t,i}·power_s),   dln(Θ_{h,t})/dτ_t = -ξ/((1+αξ)(1-τ_t)).
# (Both follow from ln(c̃_1) and ln(R_{t+1}) being affine in ln(1-τ_t) at fixed τ_{t+1}.) Any error in
# v1iProfile_LOG, lnRleadΘ or _gradProfile shows up here, with nothing else in the way.
flatGrid = np.linspace(0.05, 0.95, 7)
solpConst = {'τPolicy': griddedInterp1D(flatGrid, np.full(flatGrid.size, 0.30)),
             'ΘhPolicy': griddedInterp1D(flatGrid, np.full(flatGrid.size, 1.0))}
dConst = LOG.stateGrid_t(τGrid, np.full(τGrid.size, 0.5), tR, tRLag, θR, θR1, εR1, solpConst)
βi, powerS, ξ, α = BG.get('βi', tR), BG.power_s(tR), BG.get('ξ', tR), BG.get('α', tR)
dv1iExact = (-1/(1-τGrid))[:, None] * (1+ξ)/(1+α*ξ) * (1 + βi*powerS)
dlnhExact = -1/(1-τGrid) * ξ/(1+α*ξ)
dv1iNum = LOG._gradProfile(τGrid, dConst['v1i'], 1e-6)
dlnhNum = LOG._gradProfile(τGrid, np.log(dConst['Θh']), 1e-6)
check('numerical dυ_{1,t}^i/dτ_t matches its closed form at fixed τ_{t+1}',
      np.allclose(dv1iNum, dv1iExact, rtol = 1e-8),
      '-> max rel={:.3e}'.format(np.abs(dv1iNum/dv1iExact - 1).max()))
check('numerical dln(Θ_{h,t})/dτ_t matches its closed form',
      np.allclose(dlnhNum, dlnhExact, rtol = 1e-8),
      '-> max rel={:.3e}'.format(np.abs(dlnhNum/dlnhExact - 1).max()))

# ---- 7. the state fixed point ------------------------------------------------------------------------
ιCandFine = np.geomspace(ιGrid[0], ιGrid[-1], 2000)
ιOfτ, nRoots = LOG.solveStateApprox_t(τGrid, ιCandFine, tR, θR1, εR1, sol)
feas = ~np.isnan(ιOfτ)
dChk = LOG.stateApprox_t(τGrid[feas], ιOfτ[feas], tR, θR1, sol)
resid = LOG._residualIota(dChk, ιOfτ[feas], tR, εR1)
check('eq:stateResidualLOG vanishes at the located ι_t(τ_t)', np.max(np.abs(resid)) < 1e-6,
      '-> {} of {} nodes feasible, max|residual|={:.3e}'.format(int(feas.sum()), τGrid.size,
                                                               np.max(np.abs(resid))))
check('the feasibility mask is contiguous in τ (infeasibility comes from ι_t leaving 𝒮_0\', not noise)',
      np.all(np.diff(np.flatnonzero(feas)) == 1))
check('ι_t(τ_t) is single-valued on the feasible set', set(np.unique(nRoots[feas])) <= {1},
      '-> root counts {}'.format(sorted(set(np.unique(nRoots)))))

# ---- 8. z_t against the primitives, continuation channel included -----------------------------------
# The same rebuild as §2, one period earlier, where nothing is closed form: υ_{1,t}^j now carries
# ln(R_{t+1}) and both depend on τ_t through τ^{t+1}(ι_t(τ_t)). ι_t is re-solved EXACTLY at each τ (brentq
# on eq:stateResidualLOG) rather than read off any grid, so this checks the derivative, not the root.
from scipy import optimize

def iotaExact(τ):
    """ ι_t(τ_t) to solver tolerance, for the finite difference below. """
    def f(ι):
        d = LOG.stateApprox_t(np.atleast_1d(float(τ)), np.atleast_1d(float(ι)), tR, θR1, sol)
        return float(LOG._residualIota(d, np.atleast_1d(float(ι)), tR, εR1)[0])
    return optimize.brentq(f, ιGrid[0], ιGrid[-1], xtol = 1e-14, rtol = 8.9e-16)

def politicalObjective_t(τ, s_, ι_, siRatio_):
    """ W_t at an actual savings level, from the primitives: υ_{1,t}^j = (1+β)ln(c̃_1^j)+β ln(R_{t+1}^j)
    (the remaining β ln(β/p) terms carry no policy and drop out of the derivative), υ_{2,t}^j = ln(c_2^j).
    ι_{t-1} and s_{t-1,i}/s_{t-1} are held fixed, as the policy maker does. """
    ι = iotaExact(τ)
    d = LOG.stateApprox_t(np.atleast_1d(float(τ)), np.atleast_1d(ι), tR, θR1, sol)
    Θh, Θs, Θh1, τ1, Γs = (float(np.ravel(d[k])[0]) for k in ('Θh', 'Θs', 'Θh1', 'τ1', 'Γs'))
    h, s = B.h(Θh, s_, tR), B.s(Θs, s_, tR)
    R1 = B.Rlead(s, B.h(Θh1, s, tR1), tR)
    βi_t, β0_t = B.get('βi', tR), B.get('β0', tR)
    v1i = (1+βi_t)*np.log(B.tildec1i(h, βi_t, τ1, θR1, Γs, tR)) + βi_t*np.log(R1)
    v10 = (1+β0_t)*np.log(B.tildec10(s_, s, β0_t, τ1, εR1, tR)) \
          + β0_t*np.log(R1*B.get('χR[t+1]', tR))
    c2i = B.c2i(h, s_, τ, θR, siRatio_, tR)
    c20 = B.c20(h, s_, εR, τ, ι_, tR)
    old = (B.get('γi[t-1]', tR)*B.ω2i(tR)*np.log(c2i)).sum() + B.get('γ0[t-1]', tR)*B.ω20(tR)*np.log(c20)
    young = (B.get('γi', tR)*B.ω1i(tR)*v1i).sum() + B.get('γ0', tR)*B.ω10(tR)*v10
    return old + B.get('ν', tR)*young

# Tolerance. Unlike §2 this cannot hold to machine precision: the young terms are spline derivatives of
# profiles that inherit kinks from the piecewise-linear continuation interpolant, and ~2e-3 absolute is the
# floor (interpolating the continuation policy cubically halves it, measured, and leaves the ranking of
# candidates unchanged). A fixed rtol would be the wrong criterion since z_t crosses zero on this grid, so
# the check is on what the error actually costs: the τ it moves the located root by, |Δz|/|dz/dτ|, against
# the τ-grid spacing. The grid, not the differentiation, has to be what limits the solved policy.
dR = LOG.stateGrid_t(τGrid, ιOfτ, tR, tRLag, θR, θR1, εR1, sol)
zbarR = LOG.zbar_t(dR, θR, tR)
hFD = 1e-5
for k, ι0 in [(20, 0.5), (40, 0.5), (40, 1.5), (60, 0.5)]:
    τ0 = τGrid[k]
    zProfile = LOG._zState(zbarR, τGrid, εR, np.atleast_1d(ι0), tR)[:, 0]
    zk = float(zProfile[k])
    fd = (politicalObjective_t(τ0 + hFD, 2.0, ι0, dR['si_s_'][k])
          - politicalObjective_t(τ0 - hFD, 2.0, ι0, dR['si_s_'][k])) / (2*hFD)
    implied = abs(zk - fd)/abs(np.gradient(zProfile, τGrid)[k])
    check('z_t = dW_t/dτ_t from primitives at (τ={:.3f}, ι_={:.1f}), continuation channel included'
          .format(τ0, ι0), implied < 0.1*float(np.diff(τGrid).max()),
          '-> abs={:.1e}, implied τ error={:.1e} vs τ cell={:.1e}'.format(
              abs(zk - fd), implied, float(np.diff(τGrid).max())))

# ---- 9. the full recursion ---------------------------------------------------------------------------
sols = LOG.solveBackward(θpath, εpath, ιGrid = ιGrid, ιCandGrid = ιCandFine)
check('solveBackward returns one solution per period', set(sols) == set(tIdx))
check('every period reports a policy over the same 𝒮_0',
      all(np.allclose(s['τ'].index.values, ιGrid) for s in sols.values()))
check('no period reports a solved ι_t outside 𝒮_0 (never clipped, docs §PEELOG)',
      all(not np.any(s['outOfGrid']) for k, s in sols.items() if k != tIdx[-1]))
check('no NaN in any solved policy function',
      all(not np.isnan(s['τ'].values).any() for s in sols.values()))
# Decreasing in the state: strictly across the grid, and locally to within the τ-grid's own resolution.
# The local qualifier is not a hedge -- over most of 𝒮_0 the selection sits on a corner, where τ_t(ι_{t-1})
# is flat and the smoothing spline of step 4 wiggles it by ~1e-3, well inside one τ cell.
dτCell = float(np.diff(τGrid).max())
check('τ_t(ι_{t-1}) falls from l_ι to u_ι at every t',
      all(s['τ'].values[0] > s['τ'].values[-1] for s in sols.values()))
check('τ_t(ι_{t-1}) has no local increase above the τ-grid spacing',
      all(np.diff(s['τ'].values).max() <= dτCell for s in sols.values()),
      '-> max local increase={:.2e} vs one τ cell={:.2e}'.format(
          max(np.diff(s['τ'].values).max() for s in sols.values()), dτCell))

# The recursion's own state transition must be consistent with the fixed point it came from.
sR = sols[tR]
dTrans = LOG.stateApprox_t(sR['τ'].values, sR['ι'].values, tR, θR1, sols[tR1])
check('reported ι_t solves eq:stateResidualLOG at the SELECTED τ_t(ι_{t-1})',
      np.max(np.abs(LOG._residualIota(dTrans, sR['ι'].values, tR, εR1))) < 1e-6,
      '-> max|residual|={:.3e}'.format(np.max(np.abs(LOG._residualIota(dTrans, sR['ι'].values, tR, εR1)))))
check('ιPolicy reproduces the solved transition at the nodes', np.allclose(sR['ιPolicy'](ιGrid), sR['ι'].values))

# ---- 10. ε=0 kills the state everywhere --------------------------------------------------------------
sols0 = LOG.solveBackward(θpath, np.zeros_like(εpath), ιGrid = ιGrid, ιCandGrid = ιCandFine)
# atol=1e-12 rather than 0: z_t is exactly state-independent here (checked at T in §5), and selectMax
# therefore returns identical taxes, but step 4's smoothing spline perturbs a constant profile by ~1e-16.
check('at ε≡0 every period\'s τ_t(ι_{t-1}) is flat (A_t=0 removes the only state channel)',
      all(np.allclose(s['τ'].values, s['τ'].values[0], atol = 1e-12, rtol = 0) for s in sols0.values()),
      '-> max range={:.3e}'.format(max(s['τ'].values.max() - s['τ'].values.min() for s in sols0.values())))

report()
