r""" US model structure: what removing the informal household actually buys, and that it is really gone.

Run:  .venv\Scripts\python.exe python\US\test_ee.py

The US model keeps the j=0 slot in every array (the data are laid out that way) but gives it zero mass.
That makes three doc claims testable rather than assumed:

  1. kappa_t collapses to p_t (docs eq:governmentBudget:bbar).
  2. The informal block is genuinely inert -- perturbing eta_0/X_0 must not move any aggregate. If it
     did, gamma_0=0 would not be doing what the docs say it does.
  3. The LOG first-order condition decouples across time, z_t = z_t(tau_t) (docs
     eq:PEELOG:decoupling). This is the property that turns the PEE path into T independent scalar
     problems, and it holds ONLY because the old informal household -- the one term carrying the level
     of Theta_h, hence tau_{t+1} -- has been zeroed out.

Plus the usual aggregation/budget identities, which are what catch an h_i/h vs h_i*eta_i/h mix-up.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelUS

from gridsearch.testing import check, report

m = testmod.mLOG
T, ni = m.T, m.ni
t0 = m.db['t'][m.db['t0']]
τ = np.full(T, m.db['τ0'])
θ, ε = m.db['θ'].values, m.db['eps'].values
tFirst = m.B.tFirst
xE = slice(0, T-1)


def close(a, b, tol = 1e-10):
    d = np.max(np.abs(np.asarray(a, dtype = float) - np.asarray(b, dtype = float)))
    return d, d < tol


# ---- 1. the data really are the US layout: a zero-mass informal slot
check('gamma_0 == 0 in every period', np.all(m.db['γ0'].values == 0),
      '-> max={:.3e}'.format(np.max(m.db['γ0'].values)))
check('formal shares sum to one', np.isclose(m.db['γi'].values.sum(axis = 1), 1).all())
check('nj = ni + 1 (three income groups plus the inert slot)', (m.nj, m.ni) == (4, 3))

# ---- 2. kappa collapses to p (docs: the informal-sector coefficient is gone)
d, c = close(m.db['κ'].values, m.db['p'].values)
check('kappa_t == p_t', c, '-> max|diff|={:.2e}'.format(d))

# ---- 3. theta from the replacement-rate ratio reproduces the paper's calibration
zη = (m.B.auxProd(t0)/m.B.Γh(t0))            # = eta_i^(1+xi)/(X_i^xi Gamma_h) = z^eta_i
i1, i2 = m.db['RRGroups']
check('z^eta at the RR groups sits at half-mean and mean',
      np.isclose(zη[i1-1], 0.5, atol = 0.02) and np.isclose(zη[i2-1], 1.0, atol = 0.02),
      '-> z1={:.4f}, z2={:.4f}'.format(zη[i1-1], zη[i2-1]))
check('theta matches the paper (0.738)', np.isclose(m.db['θ'].xs(t0), 0.738, atol = 5e-4),
      '-> theta={:.5f}'.format(m.db['θ'].xs(t0)))
# The idealised closed form theta = 2 - 1/RR is close but NOT what we use -- the group cuts land near,
# not on, half-mean/mean. Guards against someone "simplifying" getTheta to the two-line version.
check('theta differs from the idealised 2-1/RR, as the docs warn',
      not np.isclose(m.db['θ'].xs(t0), 2-1/m.db['RR0'], atol = 1e-3),
      '-> general={:.5f} vs idealised={:.5f}'.format(m.db['θ'].xs(t0), 2-1/m.db['RR0']))

# ---- 4. the economic equilibrium solves and satisfies its primitive identities
s0 = m.steadyState_LOG_solve(τ[tFirst], θ[tFirst], t = tFirst)['s']
sol = m.EE_LOG_solve(τ, θ, ε, s0)
V = {k: v.values for k, v in m.EE_report(sol, τ, θ, ε, s0).items()}
check('EE report is finite everywhere', all(np.all(np.isfinite(v)) for v in V.values()))

γi, ηi = m.db['γi'].values, m.db['ηi'].values
d, c = close((γi*ηi*V['hi']).sum(axis = 1), V['h'])
check('sum_i gamma_i eta_i h_i == h (aggregation)', c, '-> max|diff|={:.2e}'.format(d))

# PAYG balance, eq (governmentBudget): contributions == benefits, with gamma_0 = 0 there is no
# informal claim on the budget at all.
ν, p_, γi_ = m.db['ν'].values, m.db['p[t-1]'].values, m.db['γi[t-1]'].values
lhs = ν*V['w']*τ*V['h']
rhs = p_*(γi_*V['bi']).sum(axis = 1)
d, c = close(lhs[1:], rhs[1:])
check('PAYG budget balances (contributions == benefits)', c, '-> max|diff|={:.2e}'.format(d))

# avgHours is the unweighted average and must differ from the productivity-weighted aggregate.
hbar = m.B.avgHours(V['h'][m.db['t0']], t0)
d, c = close(hbar, (γi[m.db['t0']]*V['hi'][m.db['t0']]).sum())
check('avgHours == sum_i gamma_i h_i', c, '-> max|diff|={:.2e}'.format(d))
check('avgHours is NOT the aggregate h (they are different objects)',
      not np.isclose(hbar, V['h'][m.db['t0']], rtol = 1e-3),
      '-> hbar={:.5f} vs h={:.5f}'.format(hbar, V['h'][m.db['t0']]))

# ---- 5. the informal block is inert
mAlt = ModelUS(pars = testmod.pars, **testmod.kwargs)
for k in ('ηj', 'Xj'):
    df = mAlt.db[k].copy()
    df[df.columns[0]] = df[df.columns[0]]*3.7      # move the zero-mass type, nothing else
    mAlt.db.update(mAlt.adjPar(k, df.values))
mAlt.updateAuxPars()
solAlt = mAlt.EE_LOG_solve(τ, θ, mAlt.db['eps'].values, s0)
d, c = close(np.concatenate([sol['s'], sol['h']]), np.concatenate([solAlt['s'], solAlt['h']]))
check('perturbing eta_0/X_0 leaves the EE untouched', c, '-> max|diff|={:.2e}'.format(d))
pol, polAlt = m.solvePEE_LOG(), mAlt.solvePEE_LOG()
d, c = close(pol['τ'].values, polAlt['τ'].values, tol = 1e-8)
check('perturbing eta_0/X_0 leaves the PEE tax path untouched', c, '-> max|diff|={:.2e}'.format(d))

# ---- 6. the LOG first-order condition decouples across time: z_t = z_t(tau_t)
τtilde = pol['τ'].values.copy()
z0 = m.LOG.focVectorized(m.LOG.stateVectorized(τtilde, θ, ε))
check('z_t is ~zero along the solved path (sanity)', np.max(np.abs(z0)) < 1e-6,
      '-> max|z|={:.2e}'.format(np.max(np.abs(z0))))
worst = 0.
for tPert in range(1, T):                      # perturb tau_{t+1} only, look at z_t
    τpert = τtilde.copy()
    τpert[tPert] += 0.05
    zPert = m.LOG.focVectorized(m.LOG.stateVectorized(τpert, θ, ε))
    worst = max(worst, np.max(np.abs(zPert[:tPert] - z0[:tPert])))
check('z_t is unchanged by any tau_{t+1}, ..., tau_T (decoupling)', worst < 1e-12,
      '-> max|dz_t|={:.2e}'.format(worst))
# Control: the same perturbation must move z at the period it belongs to, or the test above is vacuous.
τpert = τtilde.copy()
τpert[tFirst] += 0.05
zPert = m.LOG.focVectorized(m.LOG.stateVectorized(τpert, θ, ε))
check('control: perturbing tau_t does move z_t', abs(zPert[tFirst] - z0[tFirst]) > 1e-6,
      '-> |dz|={:.3e}'.format(abs(zPert[tFirst] - z0[tFirst])))

report()
