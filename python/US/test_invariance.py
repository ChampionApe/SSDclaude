r""" The two invariances the US calibration rests on (docs eq:scaleInvariance, eq:hoursUnit).

Run:  .venv\Scripts\python.exe python\US\test_invariance.py

eta_i and X_i enter the model only through two combinations, y^eta = eta^(1+xi)/X^xi and
y^x = (eta/X)^xi, and almost everything uses y^eta alone. That leaves exactly two free rescalings:

  scale (lambda)   y^eta -> lambda*y^eta, so Gamma_h -> lambda*Gamma_h.
                   Levels (h, s, c, Y) scale; R, w, tau, ratios and the savings rate do not.
                   Normalised away by Gamma_h = 1 in BOTH calibration variants.

  hours unit (mu)  y^x -> mu*y^x holding y^eta fixed.
                   Individual hours h_i and the workweek hbar scale; EVERYTHING else -- including the
                   aggregate h -- does not. This is the one the commonX variant pins with data.

Conflating the two is the live risk: it is why h_t cannot serve as the average-hours target (h_t does not
respond to mu at all), and why a level of h is meaningless under the vector-X variant. Both are checked
here rather than asserted, because both are claims about the whole solved path, not about one formula.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelUS

from gridsearch.testing import check, report


def newModel(commonX = False, **over):
    return ModelUS(pars = testmod.pars | over, commonX = commonX, **testmod.kwargs)


def rescale(m, λ = 1., μ = 1.):
    """ Apply the scale (lambda) and/or hours-unit (mu) rescaling to a model in place.
    lambda: X -> lambda^(-1/xi) X.        mu: eta -> eta/mu, X -> mu^(-(1+xi)/xi) X. """
    ξ = m.db['ξ'].values.reshape(m.T, 1)
    m.db.update(m.adjPar('ηj', m.db['ηj'].values/μ))
    m.db.update(m.adjPar('Xj', m.db['Xj'].values * λ**(-1/ξ) * μ**(-(1+ξ)/ξ)))
    m.updateAuxPars()
    return m


def solved(m):
    out = m.solvePEE_LOG()
    rep, t0 = out['report'], m.db['t0']
    V = {k: v.values for k, v in rep.items()}
    return {'τ': out['τ'].values, 'h': V['h'], 's': V['s'], 'R': V['R'], 'w': V['w'],
            'hi': V['hi'], 'si_s': V['si_s'], 'c1i': V['c1i'],
            'hbar': m.B.avgHours(V['h'][t0], m.db['t'][t0]),
            'sr': m.B.savingsRate(V['s'][t0], V['s_'][t0], V['h'][t0], m.db['t'][t0]),
            'θ': np.asarray(m.db['θ']), 'Γh': np.asarray(m.db['Γh'])}


def cmp(name, a, b, factor = 1., tol = 1e-9):
    d = np.max(np.abs(np.asarray(a, dtype = float)*factor - np.asarray(b, dtype = float)))
    scale = max(np.max(np.abs(np.asarray(b, dtype = float))), 1e-300)
    return check(name, d/scale < tol, '-> max rel diff={:.2e}'.format(d/scale))


base = solved(newModel())

# ---- 1. scale invariance
λ = 2.5
sc = solved(rescale(newModel(), λ = λ))
cmp('[lambda] Gamma_h scales by lambda', base['Γh'], sc['Γh'], factor = λ)
cmp('[lambda] h scales by lambda', base['h'], sc['h'], factor = λ)
cmp('[lambda] s scales by lambda', base['s'], sc['s'], factor = λ)
cmp('[lambda] c_1^i scales by lambda', base['c1i'], sc['c1i'], factor = λ)
cmp('[lambda] hbar scales by lambda', base['hbar'], sc['hbar'], factor = λ)
cmp('[lambda] tau is unchanged', base['τ'], sc['τ'])
cmp('[lambda] R is unchanged', base['R'], sc['R'])
cmp('[lambda] w is unchanged', base['w'], sc['w'])
cmp('[lambda] s_i/s is unchanged', base['si_s'], sc['si_s'])
cmp('[lambda] the savings rate is unchanged', base['sr'], sc['sr'])
cmp('[lambda] theta is unchanged', base['θ'], sc['θ'])

# ---- 2. hours-unit invariance
μ = 1.8
hu = solved(rescale(newModel(), μ = μ))
cmp('[mu] h_i scales by mu', base['hi'], hu['hi'], factor = μ)
cmp('[mu] hbar scales by mu', base['hbar'], hu['hbar'], factor = μ)
cmp('[mu] Gamma_h is unchanged', base['Γh'], hu['Γh'])
cmp('[mu] the AGGREGATE h is unchanged', base['h'], hu['h'])
cmp('[mu] s is unchanged', base['s'], hu['s'])
cmp('[mu] tau is unchanged', base['τ'], hu['τ'])
cmp('[mu] R is unchanged', base['R'], hu['R'])
cmp('[mu] the savings rate is unchanged', base['sr'], hu['sr'])
cmp('[mu] theta is unchanged', base['θ'], hu['θ'])
# The two are genuinely different transformations, not one dressed twice: lambda moves h, mu does not.
check('lambda and mu are independent (lambda moves h, mu does not)',
      not np.isclose(sc['h'][0], base['h'][0], rtol = 1e-6) and np.isclose(hu['h'][0], base['h'][0], rtol = 1e-12))

# ---- 3. commonX: Gamma_h = 1 for any X, and X is exactly the hours unit
mc = newModel(commonX = True)
t0 = mc.db['t'][mc.db['t0']]
check('[commonX] X is common across types', np.allclose(mc.db['Xi'].values, mc.db['Xi'].values[:, :1]))
check('[commonX] Gamma_h == 1 at the reference X', np.isclose(mc.B.Γh(t0), 1, rtol = 1e-12),
      '-> Gamma_h={:.12f}'.format(mc.B.Γh(t0)))
for X in (0.3, 4.2):
    mX = newModel(commonX = True)
    mX.initProductivity_commonX(X = X)
    mX.updateAuxPars()
    check('[commonX] Gamma_h == 1 also at X={}'.format(X), np.isclose(mX.B.Γh(t0), 1, rtol = 1e-12),
          '-> Gamma_h={:.12f}'.format(mX.B.Γh(t0)))
# Relative hours become a prediction: h_i/h proportional to (z^eta_i)^(xi/(1+xi)).
ξ = mc.db['ξ'].xs(t0)
zη = mc.zηiNormalized()
pred = zη**(ξ/(1+ξ))
cmp('[commonX] h_i/h proportional to (z^eta)^(xi/(1+xi))',
    mc.B.hRatio(t0)/mc.B.hRatio(t0)[0], pred/pred[0])

# solveCommonX is a closed form, so applying it must hit the target in ONE step, with no re-solve.
solC = solved(mc)
X = mc.solveCommonX(solC['h'][mc.db['t0']])
mc.initProductivity_commonX(X = X)
mc.updateAuxPars()
after = solved(mc)
check('[commonX] solveCommonX hits the average-hours target in one step',
      np.isclose(after['hbar'], mc.db['h0'], rtol = 1e-10),
      '-> hbar={:.6f} vs target {:.6f} (X={:.4f})'.format(after['hbar'], mc.db['h0'], X))
cmp('[commonX] applying X leaves tau untouched (block-recursive)', solC['τ'], after['τ'])
cmp('[commonX] applying X leaves R untouched (block-recursive)', solC['R'], after['R'])
cmp('[commonX] applying X leaves the AGGREGATE h untouched', solC['h'], after['h'])
cmp('[commonX] applying X leaves theta untouched', solC['θ'], after['θ'])

report()
