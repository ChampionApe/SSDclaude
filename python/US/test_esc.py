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

report()
