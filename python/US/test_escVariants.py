r""" The linear and linear-quadratic cost specs (Base.fWedge, Eq esc:AB; Ṽ of Eq esc:Vtilde and M = Base.Mabs),
the threshold calibration (ModelESC.calibrateWedgeCorner) and the driver pieces of the joint one
(runESC.kappaRoot, calibrateJoint on stub models, kappaOf, kappaColumn, wedgeReadout's Mabs;
collectESCexperiments' kappa column).

Run:  .venv\Scripts\python.exe python\US\test_escVariants.py          (~2.5 min)

    'sizeL'    f = exp(-λ τ M (1-θ))                     M = Σ_i γ_i |y_i-1|
    'sizeLQ'   f = exp(-λ τ (1-θ)[κ M + ½ Ṽ (1-θ)])
    'sizeLQV'  f = exp(-λ τ Ṽ (1-θ)[κ + ½(1-θ)])         κ = 0 is 'size', f = exp(-½ λ τ Ṽ (1-θ)²) (test_esc.py)

Checks 1-8 are notes/brief_escVariants_code_2026-10-08.md's as amended by brief_escVariants_code2; M1-M4 pin
Mabs, D1-D5 the driver. The test model is test_esc.py's (US, ρ = 1, vector X): Ṽ = 0.4357, M = 0.5746. On
it the 'sizeL' design at t0 is 0.476 at λ = 1.5 and the corner θ = 1 from λ ≈ 1.95 on, and the calibration
of (β, ω) fails at λ = 50, so check 7 brackets the threshold with λ = 1.5 and 8.
"""
import os, sys
from types import SimpleNamespace
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
import modelESC
from modelESC import ModelESC, CORNER_TOL

from gridsearch.testing import check, report

GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}
PARS = testmod.pars | {'ρ': 1.0, 'β': 0.7606187875476447, 'ω': 1.4536273947550569}
LAMBDA_SIZE = 8.643207      # test_esc.py's calibrated 'size' λ on this model ("lambda=8.643207")
λL, λLQ, κLQ = 2.3, 4.4, 0.25


def build(wedge):
    m = ModelESC(pars = PARS, wedge = wedge, **testmod.kwargs)
    m.db['dates'] = testmod.dates
    m.db['workweek'] = testmod.workweek
    m.LOG.initGS(GS)
    return m


def onGrid(fun, θg, τg, t):
    """ fun(θ, τ, t) stacked over τg, each a vector over θg: (len(τg), len(θg)). """
    return np.array([np.broadcast_to(np.asarray(fun(θg, τ, t), dtype = float), θg.shape) for τ in τg])


θg = np.linspace(0., 1., 11)
τg = np.array([0.05, 0.14, 0.3, 0.9])
WEDGES = {'sizeL': {'spec': 'sizeL', 'phi': 0.5, 'p': λL},
          'sizeLQ': {'spec': 'sizeLQ', 'phi': 0.5, 'p': λLQ, 'kappa': κLQ},
          'sizeLQV': {'spec': 'sizeLQV', 'phi': 0.5, 'p': λLQ, 'kappa': κLQ}}
models = {s: build(w) for s, w in WEDGES.items()}
t0 = models['sizeL'].t0Year
V0, M0 = float(models['sizeL'].B.Vtilde(t0)), float(models['sizeL'].B.Mabs(t0))

# ---- M1-M4. Mabs = Σ_i γ_i |y_i-1|: its definition, the two invariances, the degenerate distribution, the
# zero-mass guard, BaseTime
mT0 = models['sizeL']
γM, yM = np.asarray(mT0.B.get('γi', t0), dtype = float), np.asarray(mT0.B.hηRatio(t0), dtype = float)
check('M1. Mabs equals sum_i gamma_i |y_i - 1| on the test model (printed beside Vtilde)',
      abs(M0 - float((γM*np.abs(yM - 1)).sum())) < 1e-15 and M0 > 0,
      '-> M={:.6f} Vtilde={:.6f} M/Vtilde={:.4f}'.format(M0, V0, M0/V0))
mD = build(WEDGES['sizeL'])               # rescaled here, made degenerate in check 4, given a zero-mass type in M3
mD.db.update(mD.adjPar('Xj', mD.db['Xj'].values*2.5)); mD.updateAuxPars()
M1 = float(mD.B.Mabs(t0))
mD.db.update(mD.adjPar('ηj', mD.db['ηj'].values*1.7)); mD.updateAuxPars()
M2 = float(mD.B.Mabs(t0))
check('M2. Mabs is invariant to a common rescaling of X_i (x2.5) and of eta_i (x1.7)',
      abs(M1 - M0) < 1e-13 and abs(M2 - M0) < 1e-13, '-> residuals {:.1e}, {:.1e}'.format(M1 - M0, M2 - M0))
MT = np.asarray(mT0.BT.Mabs(), dtype = float)
MB = np.array([float(mT0.B.Mabs(t)) for t in mT0.db['t']])
lagM = max(abs(float(mT0.B.Mabs(mT0.db['t'][k], lag = '[t-1]')) - MB[k-1]) for k in range(1, mT0.T))
check("M4. Mabs on BaseTime is (T,) and matches Base year by year; lag=[t-1] is the previous year's vintage",
      MT.shape == (mT0.T,) and np.max(np.abs(MT - MB)) < 1e-15 and lagM < 1e-15)

# ---- 1. λ = 0 is the no-wedge model: f == 1, A = θ, B = 1-θ, ∂_τ ln f = 0 (λ toggled in the db; θ does not
# depend on λ under the size specs, so no refresh)
for spec in WEDGES:
    m = models[spec]
    m.setWedge(p = 0., update = False)
    B = m.B
    f = onGrid(B.fWedge, θg, τg, t0)
    A, Bc = onGrid(B.wedgeA, θg, τg, t0), onGrid(B.wedgeB, θg, τg, t0)
    d = onGrid(B.dlnfWedge_dτ, θg, τg, t0)
    m.setWedge(p = WEDGES[spec]['p'], update = False)
    check(f"1. '{spec}' at lambda = 0: f == 1, A == theta, B == 1-theta, dln f/dtau == 0 on the (theta, tau) grid",
          np.all(f == 1.) and np.all(A == θg) and np.all(Bc == 1-θg) and np.all(d == 0.),
          '-> max|f-1|={:.1e} max|A-theta|={:.1e} max|dlnf|={:.1e}'.format(
              np.max(np.abs(f-1)), np.max(np.abs(A-θg)), np.max(np.abs(d))))

# ---- 2. 'sizeLQ' and 'sizeLQV' at κ = 0 ARE 'size', bitwise: one instance, the spec toggled in its db
# (instances differ at ~1e-15 in η_i/X_i, test_esc.py S9, so the bitwise claim is about the code path); and
# the two LQ forms differ by the factor M/Ṽ in the linear term of ln f
m2 = build({'spec': 'size', 'phi': 0.5, 'p': LAMBDA_SIZE})
lagFun = lambda θ, τ, t: m2.B.fWedge(θ, τ, t, '[t-1]')
fQ, dQ, fQlag = onGrid(m2.B.fWedge, θg, τg, t0), onGrid(m2.B.dlnfWedge_dτ, θg, τg, t0), onGrid(lagFun, θg, τg, t0)
same, lin = {}, {}
for spec in ('sizeLQ', 'sizeLQV'):
    m2.setWedge(spec = spec, kappa = 0., update = False)
    same[spec] = (np.array_equal(fQ, onGrid(m2.B.fWedge, θg, τg, t0))
                  and np.array_equal(dQ, onGrid(m2.B.dlnfWedge_dτ, θg, τg, t0))
                  and np.array_equal(fQlag, onGrid(lagFun, θg, τg, t0)))
    m2.setWedge(kappa = κLQ, update = False)
    lin[spec] = np.log(onGrid(m2.B.fWedge, θg, τg, t0)) - np.log(fQ)        # the linear term of ln f
check("2. 'sizeLQ' and 'sizeLQV' at kappa = 0 equal 'size' BITWISE in fWedge (both vintages) and dlnfWedge_dtau",
      same['sizeLQ'] and same['sizeLQV'], '-> {}'.format(same))
interior = θg < 1
ratio = lin['sizeLQ'][:, interior]/lin['sizeLQV'][:, interior]
check("...and at kappa = 0.25 their linear terms of ln f differ by the factor M/Vtilde on the grid (and are not 0)",
      np.max(np.abs(ratio/(M0/V0) - 1)) < 1e-12 and np.max(np.abs(lin['sizeLQV'])) > 1e-2
      and np.all(lin['sizeLQ'][:, ~interior] == 0.),
      '-> ratio in [{:.10f}, {:.10f}], M/Vtilde={:.10f}'.format(ratio.min(), ratio.max(), M0/V0))

# ---- 3. ∂_τ ln f = ln f/τ (ln f is linear in τ) and = a central finite difference of ln fWedge in τ
for spec, m in models.items():
    B = m.B
    lnf = np.log(onGrid(B.fWedge, θg, τg, t0))
    ana = onGrid(B.dlnfWedge_dτ, θg, τg, t0)
    ident = float(np.max(np.abs(ana - lnf/τg[:, None])))
    h = 1e-6
    fd = (np.log(onGrid(B.fWedge, θg, τg + h, t0)) - np.log(onGrid(B.fWedge, θg, τg - h, t0)))/(2*h)
    errFD = float(np.max(np.abs(ana - fd)))
    check(f"3. '{spec}': dlnfWedge_dtau == ln f/tau and == the central FD of ln f in tau to 1e-8",
          ident < 1e-12 and errFD < 1e-8 and np.max(np.abs(ana)) > 0.1,
          '-> identity {:.1e}, FD {:.1e} (max|dlnf/dtau|={:.3f})'.format(ident, errFD, np.max(np.abs(ana))))

# ---- 4. f = 1 at θ = 1 for every τ, and f = 1 everywhere when Ṽ = M = 0 (finding #17; test_esc.py S13's
# degenerate distribution: every y_i = 1, set through adjPar without updateAuxPars)
τwide = np.array([0.01, 0.14, 0.5, 0.99, 3.])
mD.db.update(mD.adjPar('ηj', np.ones(mD.nj)))
mD.db.update(mD.adjPar('Xj', np.ones(mD.nj)))
for spec, w in WEDGES.items():
    m = models[spec]
    f1 = np.array([float(m.B.fWedge(1., τ, t0)) for τ in τwide])
    mD.setWedge(spec = spec, p = w['p'], kappa = w.get('kappa', 0.), update = False)
    Vdeg, Mdeg = float(mD.B.Vtilde(t0)), float(mD.B.Mabs(t0))
    fDeg = onGrid(mD.B.fWedge, θg, τg, t0)
    check(f"4. '{spec}': f == 1 at theta = 1 for every tau, and f == 1 for every (theta, tau) when Vtilde = M = 0",
          np.all(f1 == 1.) and Vdeg < 1e-28 and Mdeg < 1e-14 and np.max(np.abs(fDeg - 1.)) < 1e-15,
          '-> f(1, tau)={} Vtilde={:.1e} M={:.1e} max|f-1|={:.1e}'.format(
              np.unique(f1), Vdeg, Mdeg, np.max(np.abs(fDeg - 1.))))

# ---- M3. the zero-mass guard: i-type 1 given γ = 0 (γj as test_esc.py S13) and a NaN y_i there (hηRatio
# replaced on the instance): Mabs is finite and the live types' sum
mD.db.update(mD.adjPar('γj', np.array([0., 0., 0.5, 0.5])))
γG = np.asarray(mD.B.get('γi', t0), dtype = float)
dead = np.flatnonzero(γG == 0)
yG = np.array([np.nan, 0.6, 1.4])
mD.B.hηRatio = lambda t = None, lag = '': yG
MG = float(mD.B.Mabs(t0))
del mD.B.hηRatio
MHand = float(sum(γG[i]*abs(yG[i] - 1) for i in range(len(γG)) if γG[i] > 0))
check("M3. a NaN y_i in a zero-mass slot is masked out of Mabs (finite, and the live types' sum)",
      list(dead) == [0] and np.isfinite(MG) and abs(MG - MHand) < 1e-15,
      '-> M={:.10f} by hand={:.10f}'.format(MG, MHand))

# ---- 5. the marginal cost at the corner: ∂ln f/∂θ at θ = 1 is λτM ('sizeL'), λτMκ ('sizeLQ'), λτṼκ ('sizeLQV')
WANT5 = {'sizeL': (λL*M0, 'lambda tau M'), 'sizeLQ': (λLQ*M0*κLQ, 'lambda tau M kappa'),
         'sizeLQV': (λLQ*V0*κLQ, 'lambda tau Vtilde kappa')}
for spec, m in models.items():
    h = 1e-5
    fd = np.array([(np.log(float(m.B.fWedge(1.+h, τ, t0))) - np.log(float(m.B.fWedge(1.-h, τ, t0))))/(2*h)
                   for τ in τg])
    want = WANT5[spec][0]*τg
    err = float(np.max(np.abs(fd/want - 1)))
    check(f"5. '{spec}': dln f/dtheta at theta = 1 (central FD) == {WANT5[spec][1]}",
          err < 1e-7 and np.all(want > 0), '-> max rel err={:.1e}; at tau=0.14: {:.6f}'.format(err, fd[1]))

# ---- 6. dln c_2^i/dτ equals its central finite difference at FIXED s_{t-1,i}/s_{t-1} and h (test_esc.py S10)
for spec, m in models.items():
    sol = m.solvePEE_LOG()
    rep, B = sol['report'], m.B
    tPrev = m.db['t'][m.db['t0']-1]
    h0, s_0 = float(rep['h'].xs(t0)), float(rep['s_'].xs(t0))
    si_ = rep['si_s'].xs(tPrev).values.astype(float)
    θStar = float(m.db['θ'].xs(t0))
    α = float(B.get('α', t0))
    A0 = (1-α)/α*float(B.get('p[t-1]', t0))/float(B.get('κ[t-1]', t0))
    worstFD, worstFactor = 0., np.inf
    for θp, τp in ((θStar, float(sol['τ'].xs(t0))), (0.3, 0.25), (0.9, 0.08)):
        ana = np.asarray(B.dlnc2i_dτ(0., τp, θp, si_, t0), dtype = float)
        eps = 1e-5
        lnc = lambda τ: np.log(np.asarray(B.c2i(h0, s_0, τ, θp, si_, t0), dtype = float))
        fd = (lnc(τp + eps) - lnc(τp - eps))/(2*eps)
        worstFD = max(worstFD, float(np.max(np.abs(ana - fd))/np.max(np.abs(ana))))
        br = (np.asarray(B.wedgeA(θp, τp, t0, '[t-1]'))*B.hηRatio(t0, lag = '[t-1]')
              + np.asarray(B.wedgeB(θp, τp, t0, '[t-1]')))
        naive = A0*br/(si_ + A0*τp*br)                   # without the (1 + τ ∂_τ ln f) factor
        worstFactor = min(worstFactor, float(np.max(np.abs(ana - naive))/np.max(np.abs(ana))))
    check(f"6. '{spec}': dlnc2i_dtau == the central FD of ln c2i at fixed s_(t-1,i)/s_(t-1) (1e-8 relative, three points)",
          worstFD < 1e-8, '-> max rel err={:.2e}'.format(worstFD))
    check(f"...and the (1 + tau dln f/dtau) factor is load-bearing under '{spec}'", worstFactor > 1e-3,
          '-> smallest rel change from dropping it={:.2e}'.format(worstFactor))

# ---- 7. the corner is reached under 'sizeL', and calibrateWedgeCorner brackets it
mC = build({'spec': 'sizeL', 'phi': 0.5, 'p': 1.5})
recC = mC.calibrateWedgeCorner('sizeL', phi = 0.5, bracket = (1.5, 8.), nScan = 3, tol = 1e-2, verbose = False)
sC = recC['scan']
dAtThreshold = mC.leadedDesignAtT0()                    # the model is left calibrated at the threshold
check("7. 'sizeL': the design at t0 is interior at lambda = 1.5 and the corner at lambda = 8 (the scan's end nodes)",
      abs(sC[0]['p'] - 1.5) < 1e-12 and abs(sC[-1]['p'] - 8.) < 1e-12 and 0.02 < sC[0]['design'] < 0.98
      and sC[-1]['design'] >= 1 - CORNER_TOL, '-> designs {}'.format([round(s['design'], 6) for s in sC]))
check('...calibrateWedgeCorner: a converged threshold between them, the design there exactly 1.0 and just below it '
      "interior and > 0.9, db['wedgeP'] at the threshold",
      recC['converged'] and 1.5 < recC['p'] < 8. and dAtThreshold == 1.0
      and 0.9 < recC['choiceBelow'] < 1 - CORNER_TOL and mC.db['wedgeP'] == recC['p'] and recC['θ'] == 1.0,
      '-> threshold lambda={:.4f} design there {!r} choiceBelow={:.6f} wedgeP={:.4f}'.format(
          recC['p'], dAtThreshold, recC['choiceBelow'], mC.db['wedgeP']))

# ---- 7b. calibrateWedgeCorner's scan, bisection and failure branches on a toy design(λ): wedgeResidual is
# replaced on the instance (the corner from λ = 2.5, a failing node where asked), so no model is solved
mT = models['sizeL']
θT = float(mT.db['θ'].xs(t0))
toyCalls, failAt = [], set()
def toyResidual(p, spec, phi, calKwargs = None, preferences = 'LOG', kappa = None):
    toyCalls.append(float(p))
    if any(abs(p - q) < 1e-12 for q in failAt):
        raise RuntimeError('toy failure')
    return (1. if p >= 2.5 else 0.7 + 0.1*p) - θT
mT.wedgeResidual = toyResidual
rT = mT.calibrateWedgeCorner('sizeL', bracket = (1., 8.), nScan = 4, tol = 1e-3, verbose = False)
lastT = toyCalls[-1]
failAt.add(float(np.exp(np.linspace(0., np.log(8.), 4))[1]))         # the second node, 2.0: no bracketing pair
rTf = mT.calibrateWedgeCorner('sizeL', bracket = (1., 8.), nScan = 4, verbose = False)
failAt.clear()
rTl = mT.calibrateWedgeCorner('sizeL', bracket = (3., 9.), nScan = 3, verbose = False)
rTn = mT.calibrateWedgeCorner('sizeL', bracket = (0.5, 2.), nScan = 3, verbose = False)
del mT.wedgeResidual
check('7b. calibrateWedgeCorner on a toy design: the threshold 2.5 to relative 1e-3, the last evaluation at it, '
      'choiceBelow the design at the lower end',
      rT['converged'] and 2.5 <= rT['p'] <= 2.5*(1 + 1e-3) and abs(rT['choiceBelow'] - (0.7 + 0.25)) < 1e-3
      and rT['message'] == 'threshold' and lastT == rT['p'],
      '-> threshold={:.6f} choiceBelow={:.6f} last evaluation at {:.6f}'.format(rT['p'], rT['choiceBelow'], lastT))
check('...no bracketing pair after a failed node, the corner at the first node and no corner: converged = False, '
      'p NaN, and the message says which',
      all(not r['converged'] and np.isnan(r['p']) for r in (rTf, rTl, rTn))
      and np.isnan(rTf['scan'][1]['design']) and 'failed node' in rTf['message']
      and 'below the bracket' in rTl['message'] and 'no corner' in rTn['message'],
      '-> {} | {} | {}'.format(rTf['message'], rTl['message'], rTn['message']))

# ---- 7c. after a scan that ends far above the bracket, the refinement starts from the warm starts of the
# bracket's left node: a toy wedgeResidual that raises when self.x0['calibration'] (here log λ) is more than a
# factor 4 from λ, and then poisons a solver warm start (LOG.x0) so that every later call fails until all warm
# starts are restored -- what the real (β, ω) calibration does from λ = 26.7 at λ = 1.2 on the US model under
# 'sizeL' (a failed attempt leaves LOG.x0 where it failed; restoring x0['calibration'] alone is not enough)
mW = models['sizeL']
warmSave = mW._warmStart()
θW = float(mW.db['θ'].xs(t0))
def warmToy(kind):
    def toy(p, spec, phi, calKwargs = None, preferences = 'LOG', kappa = None):
        x = mW.x0.get('calibration')
        if mW.LOG.x0.get('toy') == 'poisoned' or (x is not None and abs(np.log(p) - float(np.ravel(x)[0])) > np.log(4.)):
            mW.LOG.x0['toy'] = 'poisoned'
            raise RuntimeError('toy: the warm start is too far or poisoned')
        mW.x0['calibration'], mW.LOG.x0['toy'] = np.array([np.log(p)]), 'ok'
        return np.log(p/2.) if kind == 'sign' else (1. if p >= 2.5 else 0.9) - θW
    return toy
warmRec = {}
for kind in ('sign', 'corner'):
    mW.x0.pop('calibration', None)
    mW.LOG.x0.pop('toy', None)
    mW.wedgeResidual = warmToy(kind)
    try:
        warmRec[kind] = (mW.calibrateWedge('sizeL', bracket = (1., 30.), nScan = 4, verbose = False) if kind == 'sign'
                         else mW.calibrateWedgeCorner('sizeL', bracket = (1., 30.), nScan = 4, verbose = False))
    except Exception as e:
        warmRec[kind] = {'converged': False, 'p': np.nan, 'message': f'{type(e).__name__}: {e}'}
    del mW.wedgeResidual
mW._restoreWarmStart(warmSave)
check("7c. a refinement after a far scan starts from the left node's warm starts: calibrateWedge (retried) finds "
      'the root 2, calibrateWedgeCorner the threshold 2.5',
      warmRec['sign']['converged'] and abs(warmRec['sign']['p'] - 2.) < 1e-6
      and warmRec['corner']['converged'] and 2.5 <= warmRec['corner']['p'] <= 2.5*(1 + 1e-3),
      '-> root {:.6f} ({}), threshold {:.6f} ({})'.format(warmRec['sign']['p'], warmRec['sign']['message'],
                                                         warmRec['corner']['p'], warmRec['corner']['message']))

# ---- 8. the interior kind under 'sizeLQ' at a fixed κ: κ reaches the model through calibrateWedge
mQ = build({'spec': 'sizeLQ', 'phi': 0.5, 'p': 4., 'kappa': 0.})
recQ = mQ.calibrateWedge(spec = 'sizeLQ', phi = 0.5, kappa = κLQ, bracket = (3.3, 4.5), nScan = 6, verbose = False)
vQ = np.array([s['residual'] for s in recQ['scan']])
okQ = np.isfinite(vQ)
nSignQ = sum(1 for k in range(len(vQ)-1) if okQ[k] and okQ[k+1] and vQ[k]*vQ[k+1] < 0)
check("8. calibrateWedge('sizeLQ', kappa = 0.25) converges with one sign change and lambda below the 'size' one",
      recQ['converged'] and nSignQ == 1 and recQ['p'] < LAMBDA_SIZE and mQ.db['wedgeKappa'] == κLQ
      and recQ['wedge']['kappa'] == κLQ,
      '-> lambda={:.6f} residual={:.1e} (size: {}); {} sign change(s), residual {:+.4f} -> {:+.4f}'.format(
          recQ['p'], recQ['residual'], LAMBDA_SIZE, nSignQ, vQ[okQ][0], vQ[okQ][-1]))

# ---- D1. runESC.kappaOf / kappaColumn: NaN or absent -> 0.0 into a model; NaN out of every spec but KAPPA_SPECS
import runESC                                                                        # noqa: E402
import collectESCexperiments as coll                                                 # noqa: E402
rowsK = pd.DataFrame([{'spec': 'size', 'kappa': np.nan}, {'spec': 'sizeLQ', 'kappa': 0.25}])
m2.setWedge(spec = 'size', update = False)              # kappa 0.25 still in its db, unread under 'size'
check('D1. kappaOf: NaN and a missing column read as 0.0, a value as itself; kappaColumn NaN except sizeLQ/sizeLQV',
      runESC.kappaOf(rowsK.iloc[0]) == 0. and runESC.kappaOf(rowsK.iloc[1]) == 0.25
      and runESC.kappaOf(pd.Series({'p': 1.})) == 0. and runESC.kappaOf({'kappa': None}) == 0.
      and np.isnan(runESC.kappaColumn(models['sizeL'])) and runESC.kappaColumn(models['sizeLQ']) == κLQ
      and runESC.kappaColumn(models['sizeLQV']) == κLQ and np.isnan(runESC.kappaColumn(m2)))

# ---- D2. runESC.kappaRoot, calibrateJoint's outer root, on toy functions of κ
calls = []
def gSign(k):
    calls.append(k)
    return 0.3 - 0.5*k                                  # root at 0.6
rS = runESC.kappaRoot(gSign, 'sign', verbose = False)
check("D2. kappaRoot 'sign': the first sign change of the scan, then brentq to 1e-3; no kappa evaluated twice",
      rS['converged'] and abs(rS['kappa'] - 0.6) < 1e-3 and len(calls) == len(set(calls)),
      '-> kappa={:.6f} after {} evaluations'.format(rS['kappa'], len(calls)))
rC = runESC.kappaRoot(lambda k: 1. if k >= 0.8 else 0.8 + 0.2*k, 'corner', verbose = False)   # corner from 0.8
check("...'corner': the smallest kappa found at the corner, within 1e-3 above the threshold",
      rC['converged'] and 0.8 <= rC['kappa'] <= 0.8 + 1e-3 and rC['message'] == 'threshold',
      '-> kappa={:.6f}'.format(rC['kappa']))
def gFail(k):
    if k == 0.25:
        raise RuntimeError('toy failure')
    return 0.3 - 0.5*k
rF = runESC.kappaRoot(gFail, 'sign', verbose = False)
rN = runESC.kappaRoot(lambda k: 0.5, 'sign', verbose = False)
r1 = runESC.kappaRoot(lambda k: 1., 'corner', verbose = False)
r0 = runESC.kappaRoot(lambda k: 0.5, 'corner', verbose = False)
check('...a failed scan node is a NaN datum; no sign change, a corner at the first kappa and no corner are '
      'converged = False with kappa NaN',
      rF['converged'] and np.isnan(rF['scan'][1][1]) and abs(rF['kappa'] - 0.6) < 1e-3
      and all(not r['converged'] and np.isnan(r['kappa']) for r in (rN, r1, r0)),
      '-> {} | {} | {}'.format(rN['message'], r1['message'], r0['message']))

# ---- D3. collectESCexperiments.merge carries kappa (NaN where a frame has none)
logF = pd.DataFrame([{'spec': 'sizeLQ', 'phi': 0.5, 'commonX': True, 'p': 4.4, 'kappa': 0.25,
                      'scenario': 'baseline', 'θpinned': False, 'θ_t0': 0.74}])
crraF = pd.DataFrame([{'ρ': 2.0, 'spec': 'size', 'phi': 0.5, 'commonX': True, 'method': 'exact', 'p': 1.7,
                       'scenario': 'baseline', 'θpinned': False, 'θ_t0': 0.75}])
mg = coll.merge(logF, crraF)
check('D3. collectESCexperiments.merge carries kappa: 0.25 on the sizeLQ row, NaN on the row without the column',
      'kappa' in mg.columns and float(mg.loc[mg['spec'] == 'sizeLQ', 'kappa'].iloc[0]) == 0.25
      and mg.loc[mg['spec'] == 'size', 'kappa'].isna().all(), '-> columns {}'.format(list(mg.columns)))

# ---- D4. wedgeReadout (and every row carrying Vtilde) writes Mabs, the economy's M at t0
wr = runESC.wedgeReadout(models['sizeL'], 0.14)
check('D4. wedgeReadout writes Mabs == Base.Mabs(t0) beside Vtilde; runESC.dispersion gives the same two',
      wr['Mabs'] == M0 and wr['Vtilde'] == V0 and runESC.dispersion(models['sizeL']) == {'Vtilde': V0, 'Mabs': M0},
      '-> {}'.format({k: round(v, 6) for k, v in wr.items()}))

# ---- D5. calibrateJoint on stub models (runESC.buildUS/buildEU replaced): λ_US(κ) = 2.26/(κ + 0.262) is the
# inner calibration; under pin 'FR' France's design in force at t0 is the corner when λκ >= 1 (the root
# κ = 0.262/1.26), under pin 'UK' the UK's design is θ* + 0.3 - λκ (root λκ = 0.3, κ = 0.0786/1.96)
lamUS = lambda k: 2.26/(k + 0.262)
log = {'inner': [], 'design': []}
class StubUS:
    def calibrateWedge(self, spec, phi, bracket = None, nScan = 12, kappa = None, verbose = True, **kw):
        lam = lamUS(kappa)
        ok = bracket[0] <= lam <= bracket[1]
        log['inner'].append((float(kappa), tuple(bracket), ok))
        return {'converged': ok, 'p': lam if ok else np.nan, 'message': 'stub', 'residual': 0., 'θ': 0.738}
class StubEU:
    def __init__(self, pin, wedge):
        self.pin, self.w, self.t0Year = pin, wedge, 2020
        self.db = {'θ': pd.Series([1.0 if pin == 'FR' else 0.56], index = [2020])}
        self.ESC = SimpleNamespace(solveBackward = lambda: 'sols')
    def calibrate(self):
        pass
    def leadedDesignAtT0(self, sols):
        log['design'].append(self.w['spec'])
        x = self.w['p']*self.w['kappa']
        return (1.0 if x >= 1. else 0.9) if self.pin == 'FR' else 0.56 + 0.3 - x
buildUS0, buildEU0 = runESC.buildUS, runESC.buildEU
runESC.buildUS = lambda wedge, **kw: StubUS()
runESC.buildEU = lambda pin, wedge, **kw: StubEU(pin, wedge)
try:
    jFR = runESC.calibrateJoint('FR', 0.5, verbose = False)
    innerFR = list(log['inner'])
    jUK = runESC.calibrateJoint('UK', 0.5, verbose = False, spec = 'sizeLQV')
finally:
    runESC.buildUS, runESC.buildEU = buildUS0, buildEU0
full = modelESC.WEDGE_BRACKET['sizeLQ']
check("D5. calibrateJoint 'FR' on stubs: the smallest kappa at which France's design in force at t0 is the corner "
      '(within 1e-3), the US model left at that kappa, θPin = 1',
      jFR['converged'] and 0.262/1.26 <= jFR['kappa'] <= 0.262/1.26 + 1e-3 and jFR['θPin'] == 1.0
      and innerFR[-1][0] == jFR['kappa'] and abs(jFR['rec']['p'] - lamUS(jFR['kappa'])) < 1e-12
      and max(runESC.KAPPA_GRID) > 1. and runESC.CORNER_TOL == CORNER_TOL,
      '-> kappa={:.6f} lambda={:.6f}'.format(jFR['kappa'], jFR['rec']['p']))
check("...'UK' under 'sizeLQV': the root of the UK design minus its θ* to 1e-3; the inner bracket is the full one "
      'first, narrowed after, and every pinned design is read by leadedDesignAtT0 under the spec asked',
      jUK['converged'] and abs(jUK['kappa'] - 0.0786/1.96) < 1e-3
      and abs(jUK['θPin'] - (0.86 - lamUS(jUK['kappa'])*jUK['kappa'])) < 1e-12
      and innerFR[0][1] == full and all(b != full for _, b, ok in innerFR[1:] if ok)
      and set(log['design']) == {'sizeLQ', 'sizeLQV'},
      '-> kappa={:.6f} θPin={:.6f}; {} inner calls under FR, brackets {}'.format(
          jUK['kappa'], jUK['θPin'], len(innerFR), [tuple(round(x, 3) for x in b) for _, b, _ in innerFR[:3]]))

report()
