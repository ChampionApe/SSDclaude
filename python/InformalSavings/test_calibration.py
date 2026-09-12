r""" model.py's calibrate -- the nested fixed point over (beta, omega, eta0, X0) (docs eq:calibration).

Run:  .venv\Scripts\python.exe python\informalSavings\test_calibration.py

What is checked:

  1. Bounded<->unbounded reparameterization round-trips; _calSetPars writes where it claims to.
  2. calibration_report's four target quantities against a rebuild from the solved path's primitives.
  3. LOG calibration converges and hits all four eq:calibration targets at db['t0'].
  4. The doc's step 2: the state grids are rebuilt at every residual evaluation, never carried over.
  5. The doc's main numerical hazard -- the outer finite-difference step. Measured, not assumed; the
     measurement does NOT reproduce the doc's prediction, so it is pinned here (see the note at 5).
  6. Idempotence, and db restoration after a failed calibration.
  7. The closing check of docs num_calibration: iota at t0 lands inside the unit interval and inside the
     state grid the policy functions were actually solved on.
  8. CRRA at one rho just above 1, warm-started from the LOG solution, landing near the LOG parameters --
     a genuine cross-check, since the two solvers share no code path.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelInformalSavings

from gridsearch.testing import check, report

def newModel(**over):
    return ModelInformalSavings(pars = testmod.pars | over, **testmod.kwargs)

m = newModel(ρ = 1)
t0 = m.db['t'][m.db['t0']]

# ---- 1. reparameterization and parameter installation -------------------------------------------------
pars0 = m.calibrationPars
back = m._calFromX(m._calToX(pars0))
check('_calToX/_calFromX round-trip', all(np.isclose(back[k], pars0[k], rtol = 1e-12) for k in m._calPars))
check('_calFromX maps any real to a strictly positive parameter',
      all(v > 0 for v in m._calFromX(np.array([-40., 0., 12., 3.])).values()))

# _calSetPars must move column 0 of the FULL ηj/Xj frames, not just db['η0']/db['X0'] -- a stale column 0
# would leave Γh (and so every equilibrium object) describing the previous trial point.
trial = dict(pars0); trial['η0'], trial['X0'], trial['β'] = 0.31, 0.44, 0.9
epsBefore, κBefore = m.db['eps'].values.copy(), m.db['κ'].values.copy()
ΓhBefore, prod0Before = m.B.Γh(t0), m.B.auxProd0(t0)
m._calSetPars(trial)
check('_calSetPars writes eta0/X0 into column 0 of the ηj/Xj frames',
      np.isclose(m.db['ηj'].xs(t0).iloc[0], 0.31) and np.isclose(m.db['Xj'].xs(t0).iloc[0], 0.44)
      and np.isclose(m.db['η0'].xs(t0), 0.31) and np.isclose(m.db['X0'].xs(t0), 0.44))
check('_calSetPars refreshes the auxiliary parameters beta reaches (eps, then kappa)',
      not np.allclose(m.db['eps'].values, epsBefore) and not np.allclose(m.db['κ'].values, κBefore),
      '-> eps {:.6f} -> {:.6f}'.format(float(epsBefore[0]), float(m.db['eps'].values[0])))
# eta0/X0 must reach the equilibrium through auxProd0 = eta0^(1+xi)/X0^xi -- by eq:auxiliary:s0_s the
# quantity iota_t is proportional to it -- and must NOT reach Gamma_h, which sums over the FORMAL types
# only. The pair of checks is the point: the first says the write lands, the second that it does not leak
# into the formal aggregate, which is what a careless write to the shared ηj/Xj frames would do.
check('_calSetPars moves auxProd0, the channel eta0/X0 reach iota through',
      not np.isclose(m.B.auxProd0(t0), prod0Before),
      '-> auxProd0 {:.6f} -> {:.6f}'.format(float(prod0Before), float(m.B.auxProd0(t0))))
check('_calSetPars leaves Gamma_h untouched (it sums over i>0, not the informal type)',
      np.isclose(m.B.Γh(t0), ΓhBefore, rtol = 1e-14), '-> Γh={:.6f}'.format(float(ΓhBefore)))
m._calSetPars(pars0)

# ---- 2. the four target quantities against a primitive rebuild ----------------------------------------
# calibration_report reads sr/tau/eta0/X0 off Base helpers. Rebuild each from the solved path directly, so
# the test does not merely re-run the same expression it is checking.
rep = m.calibration_report(pars0, 'LOG')
solved = rep['PEE']['report']
h, s, s_ = solved['h'].xs(t0), solved['s'].xs(t0), solved['s_'].xs(t0)
α, ξ, ν, Γh = m.B.get('α', t0), m.B.get('ξ', t0), m.B.get('ν', t0), m.B.Γh(t0)
srManual = s / ((s_/ν)**α * h**(1-α))
check('savings rate == eq:calibration:sr rebuilt from the solved (s, s_, h)',
      np.isclose(rep['sr'], srManual, rtol = 1e-14),
      '-> {:.10f} vs {:.10f}'.format(rep['sr'], srManual))
# The targeted moment. Rebuilt the long way -- through Y and the return -- rather than through
# capitalOutputRatio's own (K/h)^(1-alpha) shortcut, so the test can see an error in that algebra. The
# yearsPerPeriod factor is the whole point of the target: without it K/Y is a thirtieth of the data's.
KYmanual = m.db['yearsPerPeriod'] * (s_/ν) / ((s_/ν)**α * h**(1-α))
check('capital-output ratio == eq:calibration:KY rebuilt from K_t and Y_t',
      np.isclose(rep['KY'], KYmanual, rtol = 1e-14),
      '-> {:.10f} vs {:.10f}'.format(rep['KY'], KYmanual))
check('capital-output ratio == yearsPerPeriod*alpha/R at t0 (the US arm target, rescaled)',
      np.isclose(rep['KY'], m.db['yearsPerPeriod']*α/(α*(s_/ν)**(α-1)*h**(1-α)), rtol = 1e-13))
check('Theta_h from ΘhFromH inverts Base.h exactly',
      np.isclose(m.B.h(rep['Θh'], s_, t0), h, rtol = 1e-13),
      '-> h {:.10f} vs {:.10f}'.format(float(m.B.h(rep['Θh'], s_, t0)), float(h)))
zη0, zx0 = m.B.get('zη0', t0), m.B.get('zx0', t0)
inner = ((1-α)/Γh**α)**(1/(1+α*ξ))
M = float(m.B.hoursUnitRatio(t0))          # average formal hours / h_t: 1 under vector X
η0Manual = (zη0/zx0) * (1-α)*(1-rep['τ']) / (M * rep['Θh']**α * inner)
X0Manual = η0Manual * inner / (rep['Θh']*zx0*M)**(1/ξ)
check('implied eta0 == eq:calibration:eta0 rebuilt from primitives',
      np.isclose(rep['η0'], η0Manual, rtol = 1e-14), '-> {:.10f} vs {:.10f}'.format(rep['η0'], η0Manual))
check('implied X0 == eq:calibration:X0 rebuilt from primitives',
      np.isclose(rep['X0'], X0Manual, rtol = 1e-14), '-> {:.10f} vs {:.10f}'.format(rep['X0'], X0Manual))
check('the tax target is read at db[t0], not at the first active period',
      np.isclose(rep['τ'], rep['PEE']['τ'].xs(t0)) and m.db['t0'] != 0,
      '-> τ(t0)={:.6f} vs τ(tFirst)={:.6f}'.format(rep['τ'], rep['PEE']['τ'].iloc[0]))

# ---- 3. LOG calibration hits all four targets ---------------------------------------------------------
cal = m.calibrate(preferences = 'LOG')
check('calibrate returns the expected keys', set(cal) == {'pars', 'x', 'residual', 'report', 'scipyRes'})
check('all four residuals below tol', np.max(np.abs(cal['residual'])) < 1e-8,
      '-> max|residual|={:.2e}'.format(np.max(np.abs(cal['residual']))))
calRep = cal['report']
check('capital-output target hit at t0', np.isclose(calRep['KY'], m.db['KY0'], rtol = 1e-7),
      '-> K/Y={:.6f} vs target {:.6f}'.format(calRep['KY'], m.db['KY0']))
check('tax-rate target hit at t0', np.isclose(calRep['τ'], m.db['τ0'], rtol = 1e-7),
      '-> τ={:.6f} vs target {:.6f}'.format(calRep['τ'], m.db['τ0']))
check('eta0 self-consistent with Theta_h(t0)', np.isclose(calRep['η0'], cal['pars']['η0'], rtol = 1e-7),
      '-> implied={:.6f}, held={:.6f}'.format(calRep['η0'], cal['pars']['η0']))
check('X0 self-consistent with Theta_h(t0)', np.isclose(calRep['X0'], cal['pars']['X0'], rtol = 1e-7),
      '-> implied={:.6f}, held={:.6f}'.format(calRep['X0'], cal['pars']['X0']))
# What the two self-consistency conditions are FOR, read off the solved path rather than off the formulas:
# informal hours and income relative to the average formal household equal the data. Checks 'X0 self-
# consistent' above pass even when eq (calibration:X0) is derived under the wrong hours unit, which is
# why this one is needed -- and it needs both the γ·y^x = 1 normalization and a data z_0 whose denominator
# is the formal average (eq calibration:z).
γiT0, ηiT0, XiT0 = m.db['γi'].xs(t0).values, m.db['ηi'].xs(t0).values, m.db['Xi'].xs(t0).values
check('eq calibration:yNorm: Γ_h = 1 and ∑γ_i(η_i/X_i)^ξ = 1 at t0',
      np.isclose(m.B.Γh(t0), 1, rtol = 1e-12) and np.isclose((γiT0*(ηiT0/XiT0)**ξ).sum(), 1, rtol = 1e-12))
check('eq calibration:z: the data z_i average to one over the formal types',
      np.isclose((γiT0*m.db['zxi'].xs(t0).values).sum(), 1, rtol = 1e-12)
      and np.isclose((γiT0*m.db['zηi'].xs(t0).values).sum(), 1, rtol = 1e-12))
sol = calRep['PEE']['report']
hiC, h0C = sol['hi'].xs(t0).values, float(sol['h0'].xs(t0))
wC, w0C = float(sol['w'].xs(t0)), float(sol['w0'].xs(t0))
relHours  = h0C/(γiT0*hiC).sum()
relIncome = w0C*cal['pars']['η0']*h0C/(wC*(1-calRep['τ'])*(γiT0*ηiT0*hiC).sum())
check('solved informal hours / average formal hours == z_0^x', np.isclose(relHours, zx0, rtol = 1e-7),
      '-> {:.6f} vs {:.6f}'.format(relHours, zx0))
check('solved informal income / average formal income == z_0^η', np.isclose(relIncome, zη0, rtol = 1e-7),
      '-> {:.6f} vs {:.6f}'.format(relIncome, zη0))
check('db holds the converged parameters afterwards',
      all(np.isclose(m.calibrationPars[k], cal['pars'][k], rtol = 1e-10) for k in m._calPars),
      '-> ' + ', '.join('{}={:.5f}'.format(k, cal['pars'][k]) for k in m._calPars))
# No _calPars entry may be bounded from above: the search has to be able to cross 1 in beta, in either
# direction. It used to land above 1 on this calibration and that was taken as the evidence; under the
# capital-output target it lands below, so only the bound structure is asserted -- beta's value is
# reported, not required.
check('no _calBounds entry caps a parameter from above (beta must be free to cross 1)',
      all(np.isinf(u) for _, u in m._calBounds.values()),
      '-> β={:.5f}'.format(cal['pars']['β']))

# ---- 4. the doc's step 2: state grids rebuilt at every residual evaluation ----------------------------
# The bounds of 𝒮_0 come from the steady-state map iota*(tau), which moves with (beta, eta0, X0). Reuse
# across the search would place the equilibrium outside its own grid and surface as an infeasibility or a
# corner rather than as an error. The mechanism is that the override slots stay None so each solve
# re-derives its default; check the mechanism AND its consequence.
slots = m.LOG.GS['PEE']
check('no state grid is cached back into the override slots by a solve',
      slots['stateGrids']['ι_'] is None and slots['solGrids']['ι'] is None)
tT = m.db['t'][-1]                                # defaultIotaGrid takes ONE year's θ/ε, not the path
gridA = m.LOG.defaultIotaGrid(m.db['θ'].values[-1], m.db['eps'].values[-1], tT)
bumped = dict(cal['pars']); bumped['η0'] = bumped['η0']*1.20
m._calSetPars(bumped)
gridB = m.LOG.defaultIotaGrid(m.db['θ'].values[-1], m.db['eps'].values[-1], tT)
m._calSetPars(cal['pars'])
check('the state grid genuinely moves with eta0, so rebuilding is not a formality',
      not np.allclose(gridA, gridB),
      '-> 𝒮_0 = [{:.4f}, {:.4f}] -> [{:.4f}, {:.4f}] on eta0 +20%'.format(
          gridA[0], gridA[-1], gridB[0], gridB[-1]))

# ---- 5. the outer finite-difference step --------------------------------------------------------------
# The doc predicted that a sqrt(machine eps) step "will return noise". It does not: the difference
# quotient is flat to ~4 decimals from 1e-9 to 1e-5 and it is the LARGE steps that wobble, because tau_t
# is located by interpolation inside a cell of the tax grid and a small step stays on one linear piece.
# Measurements: deviations note item 11. Pinned here so the finding is not quietly lost.
x0 = cal['x']
r0 = m.calibration_residual(x0, 'LOG')
def slope(k, h):
    xp = x0.copy(); xp[k] += h
    return (m.calibration_residual(xp, 'LOG') - r0)/h
for k, name in enumerate(m._calPars):
    small, deflt = slope(k, 1e-9), slope(k, np.sqrt(np.finfo(float).eps))
    scale = max(np.max(np.abs(small)), 1e-12)
    check('outer Jacobian column for {} is stable at the default step (not noise)'.format(name),
          np.max(np.abs(small - deflt))/scale < 1e-3 and np.max(np.abs(deflt)) > 1e-3,
          '-> max|Δslope|/|slope| = {:.2e} between h=1e-9 and h=sqrt(eps)'.format(
              float(np.max(np.abs(small - deflt))/scale)))

# ---- 6. idempotence and db restoration ----------------------------------------------------------------
cal2 = m.calibrate(preferences = 'LOG')
check('re-calibrating from the converged point does not move the parameters',
      all(np.isclose(cal2['pars'][k], cal['pars'][k], rtol = 1e-6) for k in m._calPars),
      '-> max rel move={:.2e}'.format(max(abs(cal2['pars'][k]/cal['pars'][k]-1) for k in m._calPars)))

before = dict(m.calibrationPars)
epsBefore = m.db['eps'].values.copy()
raised = False
try:
    m.calibrate(preferences = 'LOG', tol = 0.0)   # unreachable tolerance -> _checkConverged raises
except RuntimeError:
    raised = True
check('an unreachable tol raises rather than returning silently', raised)
check('db parameters restored after a failed calibration',
      all(np.isclose(m.calibrationPars[k], before[k], rtol = 1e-14) for k in m._calPars))
check('db auxiliary parameters (eps) restored too', np.allclose(m.db['eps'].values, epsBefore, rtol = 1e-14))

# ---- 7. the closing check of docs num_calibration -----------------------------------------------------
# Nothing was fitted to iota, so it is a diagnostic rather than a target -- but the whole grid
# construction rests on l_iota > 0, which a calibrated value outside the unit interval would contradict.
ιt0 = float(calRep['PEE']['report']['ι'].xs(t0))
ιGrid = calRep['PEE']['sols'][m.db['t'][-1]]['ι_']
check('calibrated iota at t0 is a genuine savings ratio in (0,1)', 0 < ιt0 < 1, '-> ι={:.6f}'.format(ιt0))
check('calibrated iota at t0 lies inside the state grid the policies were solved on',
      ιGrid[0] <= ιt0 <= ιGrid[-1],
      '-> ι={:.6f} in 𝒮_0 = [{:.4f}, {:.4f}]'.format(ιt0, ιGrid[0], ιGrid[-1]))
init = calRep['PEE']['init']
check('the initial fixed point is a single crossing at the calibrated parameters',
      init is not None and init['nRoots'] == 1,
      '-> nRoots={}, τ_1={:.6f}, residual={:.2e}'.format(init['nRoots'], init['τ'], init['residual']))

# ---- 8. CRRA just above rho=1, warm-started from LOG --------------------------------------------------
# The two solvers share no code path, so agreement near rho=1 tests both. Warm start means both halves:
# the converged LOG parameters installed in db, and x0 starting the outer root at the same point.
#
# NONE OF THESE SETTINGS ARE THE PEE SOLVE'S DEFAULTS. What carries the check is smoothKnots + cubic:
# un-pinned knots FAIL here at any outer step, ~30 evaluations of cycling apiece (crossCuttingFindings #5).
# 45x45 is retained on much weaker grounds than it was adopted on -- deviations note items 11-13 have the
# measurements and the two readings they retired.
ρC = 1.02
CRRAGRID = {'nι': 45, 'ns': 45, 'interpKind': 'cubic', 'smoothKnots': 4}
mC = newModel(ρ = ρC)
mC._calSetPars(cal['pars'])
mC.CRRA.initGS(CRRAGRID)
calC = mC.calibrate(preferences = 'CRRA', x0 = cal['x'])
check('CRRA (ρ={}) calibration converges on the resolved grid'.format(ρC),
      np.max(np.abs(calC['residual'])) < 1e-8,
      '-> max|residual|={:.2e}'.format(np.max(np.abs(calC['residual']))))
gap = max(abs(calC['pars'][k]/cal['pars'][k]-1) for k in m._calPars)
check('CRRA (ρ={}) parameters land near the LOG ones'.format(ρC), gap < 0.05,
      '-> ' + ', '.join('{}={:.5f} ({:+.2%})'.format(k, calC['pars'][k], calC['pars'][k]/cal['pars'][k]-1)
                        for k in m._calPars))

# The answer must be a property of the model, not of the grid it was found on. Vary ONLY the grid:
# initGS() with no argument would reset interpKind and smoothKnots too, which is a different experiment.
mC.CRRA.initGS(CRRAGRID | {'nι': 60, 'ns': 60})
rFine = np.max(np.abs(mC.calibration_residual(calC['x'], 'CRRA')))
mC.CRRA.initGS(CRRAGRID | {'nι': 30, 'ns': 30})
rCoarse = np.max(np.abs(mC.calibration_residual(calC['x'], 'CRRA')))
mC.CRRA.initGS(CRRAGRID)
check('the calibrated CRRA point survives grid refinement', rFine < 1e-3,
      '-> max|residual| at 60x60 = {:.2e} (vs {:.2e} on its own 45x45 grid)'.format(
          rFine, np.max(np.abs(calC['residual']))))
# Only the DIRECTION is checked -- the coarse grid must be genuinely worse, i.e. 45x45 is not an arbitrary
# pick -- with the ratio reported rather than bounded. If this ever inverts, 45x45 has no justification
# left and should be dropped.
check('coarsening the inner grid to the PEE default degrades the residual', rCoarse > rFine,
      '-> max|residual| at 30x30 = {:.2e}, {:.1f}x the 60x60 value'.format(rCoarse, rCoarse/rFine))

# ---- 6. the common-X variant: same equilibrium, the hours unit pinned by the workweek ------------------
# X enters no aggregate (eta_i^{1+xi}/X^xi = z^eta_i for any X), so the four-parameter root and the
# equilibrium must coincide with the vector-X calibration's; what moves is (eta_0, X_0) through the
# hours-unit ratio M, and the level of formal hours, which now hits db['h0']. The informal z checks are
# the same as under vector X, which is what the M factor in calibrationη0/X0 is for.
mX = ModelInformalSavings(pars = testmod.pars | {'ρ': 1.0}, commonX = True, **testmod.kwargs)
mX._calSetPars({'β': cal['pars']['β'], 'ω': cal['pars']['ω'], 'η0': cal['pars']['η0'], 'X0': cal['pars']['X0']})
mX.LOG.initGS(dict(m.LOG.GS['PEE']['gridSettings']))       # the vector-X model's own grid
calX = mX.calibrate(preferences = 'LOG')
repX = calX['report']
check('common X: the root converges', np.max(np.abs(calX['residual'])) < 1e-8,
      '-> max|residual|={:.2e}'.format(np.max(np.abs(calX['residual']))))
check('common X: beta, omega, K/Y, tau and iota coincide with the vector-X calibration (X enters no aggregate)',
      all(np.isclose(calX['pars'][k], cal['pars'][k], rtol = 1e-8) for k in ('β', 'ω'))
      and np.isclose(repX['KY'], calRep['KY'], rtol = 1e-8) and np.isclose(repX['τ'], calRep['τ'], atol = 1e-10)
      and np.isclose(float(repX['PEE']['report']['ι'].xs(t0)), float(calRep['PEE']['report']['ι'].xs(t0)), rtol = 1e-8),
      '-> β {:.10f} vs {:.10f}, ω {:.10f} vs {:.10f}'.format(calX['pars']['β'], cal['pars']['β'],
                                                          calX['pars']['ω'], cal['pars']['ω']))
check('common X: average formal hours at t0 hit the workweek target db[h0]',
      np.isclose(repX['hbar'], mX.hbarTarget(), rtol = 1e-8),
      '-> hbar={:.6f} target={:.6f}, X={:.4f}'.format(repX['hbar'], mX.hbarTarget(), calX['pars']['X']))
γX, ηX, XX = mX.db['γi'].xs(t0).values, mX.db['ηi'].xs(t0).values, mX.db['Xi'].xs(t0).values
MX = float(mX.B.hoursUnitRatio(t0))
check('common X: Γ_h = 1 still, X_i common, and the second normalisation is NOT imposed (M != 1)',
      np.isclose(mX.B.Γh(t0), 1, rtol = 1e-12) and np.allclose(XX, XX[0]) and abs(MX - 1) > 1e-3,
      '-> M={:.6f}'.format(MX))
check('common X: eta_0/X_0 differ from the vector-X ones by the M factors',
      np.isclose(calX['pars']['η0'], cal['pars']['η0']/MX, rtol = 1e-6)
      and np.isclose(calX['pars']['X0'], cal['pars']['X0']*MX**(-1-1/ξ), rtol = 1e-6),
      '-> η0 {:.6f} vs {:.6f}/M, X0 {:.6f} vs {:.6f}·M^(-1-1/ξ)'.format(
          calX['pars']['η0'], cal['pars']['η0'], calX['pars']['X0'], cal['pars']['X0']))
solX = repX['PEE']['report']
hiX, h0X = solX['hi'].xs(t0).values, float(solX['h0'].xs(t0))
wX, w0X = float(solX['w'].xs(t0)), float(solX['w0'].xs(t0))
check('common X: solved informal hours / average formal hours == z_0^x',
      np.isclose(h0X/(γX*hiX).sum(), zx0, rtol = 1e-7), '-> {:.6f} vs {:.6f}'.format(h0X/(γX*hiX).sum(), zx0))
check('common X: solved informal income / average formal income == z_0^η',
      np.isclose(w0X*calX['pars']['η0']*h0X/(wX*(1-repX['τ'])*(γX*ηX*hiX).sum()), zη0, rtol = 1e-7))
check('common X: relative formal hours are a prediction, rising with income',
      np.all(np.diff(mX.predictedRelativeHours()) > 0)
      and np.isclose((γX*mX.predictedRelativeHours()).sum(), 1, rtol = 1e-12),
      '-> predicted {} vs data {}'.format(np.round(mX.predictedRelativeHours(), 3),
                                          np.round(mX.db['zxi'].xs(t0).values, 3)))

report()
