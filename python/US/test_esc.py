r""" Endogenous system characteristics: the wedge (base.py's wedgeA/wedgeB) and the leaded choice of theta
(policyESC.LeadedLOG, modelESC.ModelESC).

Run:  .venv\Scripts\python.exe python\US\test_esc.py

Five things are worth pinning, and they are the five that would silently produce a plausible wrong answer:

  1. NO WEDGE IS THE IDENTITY. ModelESC with spec=None must reproduce ModelUS to machine precision, and
     so must spec='scale'/'flat' at phi=1 (f == 1). Without this every ESC result is measured against a
     baseline that has quietly moved.
  2. THE WEDGE IS THE APPENDIX'S. Gamma_s, Theta_h and s_i/s under 'scale' are checked against the
     appendix's own closed forms (app:ESC, "Marginal costs of raising redistributive, public funds"),
     evaluated independently here rather than by re-running the code under test.
  3. z_t DOES NOT SEE theta_{t+1}. LeadedLOG.z passes (tau, theta) as placeholders for
     (tau_{t+1}, theta_{t+1}) on the grounds that they reach the FOC only through the zero-mass informal
     household. Driven over the whole unit square, z_t must not move -- otherwise tau_t and theta_{t+1}
     are not separable and the entire recursion is ill-posed.
  4. THE CHOICE IS INVARIANT TO s_{t-1}. The recursion evaluates the objective at s_{t-1} = 1 because
     ln(s_{t-1}) enters W_t additively. Checked by re-maximising at a different s.
  5. tau FROM THE RECURSION IS tau FROM solvePEE_LOG. The leaded solver reaches the tax through its own
     grid+polish path; at a fixed theta it must land on what the production solver gives.

Two more since the counterfactuals became new equilibrium paths read at 2020 (sections 9 and 10):

  6. THE CALIBRATION TARGETS THE DESIGN IN FORCE AT t0, not the choice made there. theta_t is a state
     chosen at t-1, so those are different numbers; swapping them moves every appendix table by ~0.01 in
     theta and leaves everything looking reasonable.
  7. A SHOCKED MODEL IS THE FULL HORIZON. shocks.shockedCopy must keep the calendar and db['t0'], and the
     shock must reach the first period -- a copy that renumbered periods would report the wrong year.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelUS
from modelESC import ModelESC

from gridsearch.testing import check, report

GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}
PARS = testmod.pars | {'ρ': 1.0, 'β': 0.7606187875476447, 'ω': 1.4536273947550569}


def build(cls, wedge = None):
    kw = {'wedge': wedge} if cls is ModelESC else {}
    m = cls(pars = PARS, **kw, **testmod.kwargs)
    m.db['dates'] = testmod.dates
    m.db['workweek'] = testmod.workweek
    m.LOG.initGS(GS)
    return m


def close(a, b, tol = 1e-10):
    d = np.max(np.abs(np.asarray(a, dtype = float) - np.asarray(b, dtype = float)))
    return d, d < tol


mUS = build(ModelUS)
solUS = mUS.solvePEE_LOG()
t0 = mUS.db['t'][mUS.db['t0']]

# ---- 1. no wedge is the identity
for label, wedge in (('spec=None', None),
                     ('spec=scale, phi=1', {'spec': 'scale', 'phi': 1.0, 'p': 0.4}),
                     ('spec=flat, phi=1', {'spec': 'flat', 'phi': 1.0, 'p': 0.4})):
    m = build(ModelESC, wedge)
    sol = m.solvePEE_LOG()
    dτ, okτ = close(sol['τ'].values, solUS['τ'].values, 1e-14)
    ds, oks = close(sol['report']['s'].values, solUS['report']['s'].values, 1e-14)
    dθ, okθ = close(m.db['θ'].values, mUS.db['θ'].values, 1e-14)
    check(f'{label} reproduces ModelUS (tau, s, theta)', okτ and oks and okθ,
          '-> max|dtau|={:.1e} max|ds|={:.1e} max|dtheta|={:.1e}'.format(dτ, ds, dθ))

# f(theta) itself
mW = build(ModelESC, {'spec': 'scale', 'phi': 0.5, 'p': 0.4})
θq = np.array([0., 0.25, 0.5, 0.7382, 1.])
fq = mW.B.fWedge(θq)
check('f(theta) = phi + (1-phi)theta^p, increasing, f(0)=phi, f(1)=1',
      np.allclose(fq, 0.5 + 0.5*θq**0.4) and np.all(np.diff(fq) > 0)
      and np.isclose(fq[0], 0.5) and np.isclose(fq[-1], 1.),
      '-> f={}'.format(np.round(fq, 4)))
check("'scale': A+B = f(theta), 'flat': A = theta",
      np.allclose(mW.B.wedgeA(θq) + mW.B.wedgeB(θq), fq)
      and np.allclose(build(ModelESC, {'spec': 'flat', 'phi': .5, 'p': .4}).B.wedgeA(θq), θq))

# ---- 2. the wedge is the appendix's closed forms (app:ESC), evaluated independently
# Gamma_s = (1/(1+xi)) Gamma_h beta / (1 + beta + (1-alpha)/alpha tau f(theta)(1 + theta beta))
# Theta_h denominator: Gamma_h - (1-alpha)/alpha f(theta) tau theta Gamma_s
# s_i/s = y_i/Gamma_h + (1-alpha)/alpha f(theta) tau (1-theta)/(1+beta) (y_i/Gamma_h - 1)
B = mW.B
α, ξ = float(B.get('α', t0)), float(B.get('ξ', t0))
Γh = float(B.Γh(t0))
βi = B.get('βi', t0)
β = float(βi[0])
check('the calibration used for the closed forms has a common beta_i', np.allclose(βi, β))
τx, θx = 0.17, 0.62
f = float(0.5 + 0.5*θx**0.4)
ΓsCode = float(B.Γs(βi, τx, θx, t0))
ΓsDoc = (1/(1+ξ)) * Γh*β / (1 + β + (1-α)/α*τx*f*(1 + θx*β))
d, ok = close(ΓsCode, ΓsDoc, 1e-12)
check('Gamma_s matches app:ESC with f(theta)', ok, '-> code={:.10f} doc={:.10f} diff={:.1e}'.format(ΓsCode, ΓsDoc, d))

ΘhCode = float(B.Θh(τx, τx, θx, ΓsCode, t0))
ΘhDoc = Γh**((1+ξ)/(1+α*ξ)) * ((1-α)*(1-τx)/(Γh - (1-α)/α*f*τx*θx*ΓsCode))**(ξ/(1+α*ξ))
d, ok = close(ΘhCode, ΘhDoc, 1e-12)
check('Theta_h matches app:ESC with f(theta)', ok, '-> code={:.10f} doc={:.10f} diff={:.1e}'.format(ΘhCode, ΘhDoc, d))

siCode = B.si_s(βi, τx, θx, ΓsCode, t0)
y = B.auxProd(t0)/Γh
siDoc = y + (1-α)/α*f*τx*(1-θx)/(1+β)*(y - 1)
d, ok = close(siCode, siDoc, 1e-12)
check('s_i/s matches app:ESC with f(theta)', ok, '-> max|diff|={:.1e}'.format(d))

# and that the wedge is NOT silently in the current tax: b^i uses A/B, bbar stays gross
bbarCode = float(B.bbar(τx, 1.3, 0.66, 0.65, t0))
check('bbar is gross of the wedge (nu w h tau / (h_ kappa_))',
      np.isclose(bbarCode, float(B.get('ν', t0))*1.3*0.66*τx/(0.65*float(B.get('κ[t-1]', t0)))))

# ---- 3. z_t does not see theta_{t+1} (what LeadedLOG.z's placeholder rests on)
tLag = mW.db['t'][mW.db['t0']-1]
worst = 0.
zRef = None
for τ1 in (0.05, 0.5, 0.9):
    for θ1 in (0.0, 0.5, 1.0):
        d = mW.LOG.stateGrid(np.array([τx]), t0, np.array([θx]), tLag, False, τ1 = τ1, θ1 = θ1)
        z = float(mW.LOG.focGrid(d, t0, np.array([θx]), float(mW.db['eps'].xs(t0)), False)[0])
        zRef = z if zRef is None else zRef
        worst = max(worst, abs(z - zRef))
check('z_t is unchanged over the whole (tau_1, theta_1) square (zero-mass slot)', worst < 1e-14,
      '-> max|dz|={:.2e}'.format(worst))
check('the placeholder z() agrees with an explicit (tau_1, theta_1)',
      abs(float(mW.ESC.z(t0, τx, θx, tLag, False)[0]) - zRef) < 1e-14)

# ---- 4/5. the recursion: tau against solvePEE_LOG, and invariance to s_{t-1}
sols = mW.ESC.solveBackward()
θStar = float(mW.db['θ'].xs(t0))
solW = mW.solvePEE_LOG()                       # same model, theta exogenous at theta*
d, ok = close(mW.ESC.τAt(t0, θStar), float(solW['τ'].xs(t0)), 1e-8)
check('tau from the leaded recursion == tau from solvePEE_LOG at theta*', ok,
      '-> recursion={:.10f} solver={:.10f} diff={:.1e}'.format(mW.ESC.τAt(t0, θStar), float(solW['τ'].xs(t0)), d))

# the whole tau policy, not just one node
dd = max(abs(mW.ESC.τAt(t, θStar) - float(solW['τ'].xs(t))) for t in mW.db['t'][:-1])
check('...and at every non-terminal period', dd < 1e-8, '-> max|diff|={:.2e}'.format(dd))

# s-invariance of the CHOICE: re-maximise the objective at a different s_{t-1}
tIdx = mW.db['t']
pos = tIdx.get_loc(t0)
t1 = tIdx[pos+1]
τt = np.full(mW.ESC.nθCand, mW.ESC.τAt(t0, θStar))
θt = np.full(mW.ESC.nθCand, θStar)
s1 = sols[t1]
cont = {'τ1': np.interp(mW.ESC.θCand, s1['θGrid'], s1['τ']),
        'θ2': np.interp(mW.ESC.θCand, s1['θGrid'], s1['θNext']),
        'terminal1': False}
s2 = sols[tIdx[pos+2]]
cont['τ2'] = np.interp(cont['θ2'], s2['θGrid'], s2['τ'])
arg = {}
for sLag in (1.0, 0.037, 12.5):
    W, _ = mW.ESC.objective(t0, tIdx[pos-1], t1, τt, θt, mW.ESC.θCand, cont, s_ = sLag)
    arg[sLag] = mW.ESC._argmax(mW.ESC.θCand, W)[0]
spread = max(arg.values()) - min(arg.values())
check('the leaded choice is invariant to s_{t-1} (appendix normalisation)', spread < 1e-12,
      '-> argmax at s=1/0.037/12.5: {} (spread {:.1e})'.format(
          ', '.join('{:.6f}'.format(v) for v in arg.values()), spread))

# ---- 6. the corner the wedge is meant to escape, and that it does escape it
mNo = build(ModelESC, None)
mNo.calibrate()
solsNo = mNo.ESC.solveBackward()
chNo = mNo.leadedChoiceAtT0(solsNo)
check('WITHOUT a wedge the leaded choice is the corner theta = 0 (app:ESC)', chNo == 0.,
      '-> choice={:.6f}'.format(chNo))
check('...at every state, not just at theta*', np.all(solsNo[t0]['θNext'] == 0.),
      '-> max={:.3e}'.format(np.max(solsNo[t0]['θNext'])))

mW.calibrate()
solsW = mW.ESC.solveBackward()
chW = mW.leadedChoiceAtT0(solsW)
check('WITH the wedge (phi=.5, p=.4) the choice is interior', 0. < chW < 1.,
      '-> choice={:.6f}'.format(chW))

# ---- 7. theta identification: 'scale' leaves it alone, 'flat' moves it, both invert the same datum
for spec, moves in (('scale', False), ('flat', True)):
    m = build(ModelESC, {'spec': spec, 'phi': 0.5, 'p': 1.6})
    θs = float(m.db['θ'].xs(t0))
    θ0 = float(mUS.db['θ'].xs(t0))
    A, Bc = m.B.wedgeA(θs), m.B.wedgeB(θs)
    ratio = Bc/A
    check(f"'{spec}': B/A reproduces the data ratio (1-theta_nowedge)/theta_nowedge",
          np.isclose(ratio, (1-θ0)/θ0, rtol = 1e-9),
          '-> B/A={:.8f} data={:.8f} theta={:.4f}'.format(ratio, (1-θ0)/θ0, θs))
    check(f"'{spec}': theta {'moves with' if moves else 'is unchanged by'} p",
          (abs(θs - θ0) > 1e-3) == moves, '-> theta={:.4f} vs {:.4f}'.format(θs, θ0))

# ---- 8. the PERMANENT choice (PermanentLOG)
mNo.calibrate()
permNo = mNo.solvePermanent('LOG')
check('WITHOUT a wedge the PERMANENT choice is also a corner (app:ESC)', permNo['atBound'],
      '-> theta={:.6f}, turning points={}'.format(permNo['θ'], permNo['nTurning']))
check('...and at rho=1 it is the theta=0 corner specifically', permNo['θ'] == 0.,
      '-> theta={:.6f}'.format(permNo['θ']))

permW = mW.solvePermanent('LOG')
check('WITH the wedge the permanent choice is interior', 0. < permW['θ'] < 1.,
      '-> theta={:.6f} (leaded gives {:.6f})'.format(permW['θ'], chW))
check('the anticipated-vote fixed point converges', permW['converged'],
      '-> iterates {}'.format(np.round(permW['iterates'], 6)))

# tau at the chosen design must be the ORDINARY PEE tax there -- that is the concentration argument the
# solver rests on (dW/dtau = 0 is the same first-order condition, so the 2-D grid the appendix proposes
# collapses to this 1-D one). If it ever stops holding, PermanentLOG.solve is solving the wrong problem.
τConc = mW.ESCP.τAt(mW.t0Year, permW['θ'])
check('tau at the permanent choice == tauPolicy(theta) (the concentration argument)',
      abs(τConc - permW['τAtChoice']) < 1e-6,
      '-> concentrated={:.8f} solver={:.8f}'.format(τConc, permW['τAtChoice']))

# The predetermined ratio must be PINNED, not recomputed per candidate. This is not a nicety: the two
# readings differ by ~0.13 in theta at the calibrated wedge.
check('pinning s_{t-1,i}/s_{t-1} matters, so the convention is load-bearing',
      abs(permW['θMoving'] - permW['θ']) > 1e-3,
      '-> pinned={:.4f} vs moving={:.4f}'.format(permW['θ'], permW['θMoving']))
siPin = mW.predeterminedSiRatio()
check('the pinned ratio is the baseline equilibrium value at t0-1, and sums correctly',
      siPin.shape == (mW.ni,) and abs(float((mW.B.get('γi', t0)*siPin).sum()) - 1.) < 1e-9,
      '-> sum(gamma_i * si_s) = {:.12f}'.format(float((mW.B.get('γi', t0)*siPin).sum())))

# ---- 9. the anticipated vote: which value the ratio is pinned AT
# siRatioAt's closed form must reproduce the solved equilibrium's own si_s at t0-1. That is what makes the
# fixed point a scalar problem -- eq (EE:si_s) at vintage t0-1 depends on DATE-t0 policy alone, so the
# kinked design path (incumbent before t0, chosen from t0) needs no separate solve to evaluate.
siClosed = mW.ESCP.siRatioAt(t0, float(mW.db['θ'].xs(t0)))
check('siRatioAt(incumbent) == the solved baseline si_s at t0-1',
      float(np.max(np.abs(siClosed - siPin))) < 1e-12,
      '-> max|diff| = {:.3e}'.format(float(np.max(np.abs(siClosed - siPin)))))

# The two pinnings coincide EXACTLY wherever the choice reproduces the incumbent design -- which is what
# calibrateWedge targets, so the calibrated p is common to both readings. The content of that claim is the
# identity just checked, applied at the root. Here the fixed point is verified against its own equation
# rather than against the loop that produced it.
reFP = mW.ESCP.solve(t0, mW.ESCP.siRatioAt(t0, permW['θ']))['θ']
check('the fixed point satisfies its own equation when re-solved at its ratio',
      abs(reFP - permW['θ']) < 1e-8, '-> re-solved={:.9f} reported={:.9f}'.format(reFP, permW['θ']))

# Away from a calibrated wedge the two pinnings must SEPARATE, or the timing is untested.
mOff = build(ModelESC, {'spec': 'scale', 'phi': 0.5, 'p': 0.25})
mOff.calibrate()
permOff = mOff.solvePermanent('LOG')
check('away from the calibrated wedge the choice leaves the incumbent design', 
      abs(permOff['θ'] - float(mOff.db['θ'].xs(t0))) > 1e-2,
      '-> chosen={:.6f} incumbent={:.6f}'.format(permOff['θ'], float(mOff.db['θ'].xs(t0))))
check('...and there the two pinnings separate, so the timing is load-bearing',
      0. < permOff['θ'] < 1. and abs(permOff['θ'] - permOff['θIncumbent']) > 1e-4,
      '-> fixedPoint={:.6f} incumbent={:.6f} moving={:.6f}'.format(
          permOff['θ'], permOff['θIncumbent'], permOff['θMoving']))

# The reported path is the reform the timing describes: exogenous before t0, chosen from t0 on.
θPath = permOff['θPath']
check('the reported design path is kinked at t0, not constant at the choice',
      np.allclose(θPath[:mOff.db['t0']], float(mOff.db['θ'].xs(t0)))
      and np.allclose(θPath[mOff.db['t0']:], permOff['θ']),
      '-> before t0={:.6f} from t0={:.6f}'.format(θPath[0], θPath[mOff.db['t0']]))

# ---- 10. leadedDesignAtT0: the object the counterfactual tables read and the wedge calibrates on
# theta_t is a STATE chosen at t-1, so the design in force in 2020 is thetaPolicy_{1990}, not the choice
# made in 2020. The two are different numbers and the calibration targets the first; a regression that
# quietly swapped them would move every appendix table by ~0.01 in theta and leave everything looking
# reasonable, which is exactly what this pins.
pos0 = mW.db['t0']
design = mW.leadedDesignAtT0(solsW)
θFree, _ = mW.ESC.simulate(solsW, float(mW.db['θ'].xs(t0)), tPin = None)
check('leadedDesignAtT0 is the freely simulated path at t0', abs(design - θFree.iloc[pos0]) < 1e-14,
      '-> {:.8f} vs {:.8f}'.format(design, θFree.iloc[pos0]))
check('...and it is NOT the choice made at t0 (they differ by a period of nu_t)',
      abs(design - chW) > 1e-3, '-> design_t0={:.6f} choice_at_t0={:.6f}'.format(design, chW))
# Under LOG the policy has no state, so the design at t0 is thetaPolicy_{t0-1} evaluated anywhere.
tPrev = mW.db['t'][pos0-1]
check('...and under LOG it equals thetaPolicy_{t0-1} at any inherited design',
      max(abs(design - mW.ESC.choiceAt(solsW, tPrev, x)) for x in (0.05, 0.5, 0.95)) < 1e-12,
      '-> spread over inherited theta < 1e-12 (LOG has no state; see leadedDesignAtT0)')

# At the CALIBRATED wedge the design at t0 must land on theta* -- that is what calibrateWedge solves for,
# and it is what puts the baseline row of every counterfactual table on the observed design.
mCal = build(ModelESC, {'spec': 'scale', 'phi': 0.5, 'p': 1.0})
rec = mCal.calibrateWedge(spec = 'scale', phi = 0.5, verbose = False)
led = mCal.solveLeaded(pinAtT0 = False)
check('at the calibrated p the FREE path reproduces theta* at t0', rec['converged']
      and abs(float(led['θ'].iloc[mCal.db['t0']]) - float(mCal.db['θ'].xs(t0))) < 1e-4,
      '-> p={:.6f} theta_t0={:.6f} theta*={:.6f}'.format(
          rec['p'], float(led['θ'].iloc[mCal.db['t0']]), float(mCal.db['θ'].xs(t0))))
check('...and the tax target is still hit there', abs(led['targetDrift']['τ']) < 1e-6,
      '-> tauDrift={:.2e} RDrift={:.2e}'.format(led['targetDrift']['τ'], led['targetDrift']['R']))

# ---- 11. the new-path convention: a shocked model is the full horizon, not a copy from t0
# shockedCopy must leave the horizon, the calendar and t0's POSITION alone -- the readout sits at
# db['t0'], so a copy that renumbered periods would silently report the wrong year.
import shocks as sh                                                                  # noqa: E402
mBase = build(ModelESC, {'spec': 'scale', 'phi': 0.5, 'p': 0.4})
mBase.calibrate()
mShk, _ = sh.shockedCopy(mBase, 'acute', None)
check('shockedCopy keeps the full horizon and the calibration position',
      len(mShk.db['t']) == len(mBase.db['t']) and mShk.db['t0'] == mBase.db['t0']
      and list(mShk.db['dates']) == list(mBase.db['dates']),
      '-> T={} t0={} dates[0]={}'.format(len(mShk.db['t']), mShk.db['t0'], list(mShk.db['dates'])[0]))
check('...and the shock reaches the FIRST period, not only t0 onward',
      float(mShk.db['ν'].xs(mShk.db['t'][0])) == 1.0,
      '-> nu[0]={:.4f} (baseline {:.4f})'.format(float(mShk.db['ν'].xs(mShk.db['t'][0])),
                                                 float(mBase.db['ν'].xs(mBase.db['t'][0]))))
check('...and the warm-start caches are cleared, so experiments do not depend on run order',
      mShk.x0 == {} and mShk.LOG.x0 == {} and mShk.CRRA.x0 == {})
# The unshocked new path IS the baseline: same parameters, same own-steady-state start.
noShock, _ = sh.shockedCopy(mBase, 'frLeisure', {'xbarRatio': 1.0})
# 1e-8, not machine precision: rescaleX(1) still runs updateAuxPars, which re-derives theta from eta/X
# and reintroduces the inversion's own error. The point is that the construction adds nothing, not that
# a no-op round trip is bit-exact.
dτ = float(np.max(np.abs(noShock.solvePEE_LOG()['τ'].values - mBase.solvePEE_LOG()['τ'].values)))
check('a null shock on a new path reproduces the baseline path', dτ < 1e-8,
      '-> max|dtau|={:.2e}'.format(dτ))

report()
