r""" The economic equilibrium must satisfy the model's own primitive conditions, not just its closed forms.

Run:  .venv\Scripts\python.exe python\informalAnalytical\test_ee.py

Every closed form in base.py §4-§7 is a *reduction* of the primitive optimality/budget conditions in
eq (formalOpt)/(formalBudget)/(informalBudget)/(governmentBudget). The checks below rebuild the primitive
side independently -- individual savings from the household FOC, consumption from the raw budget, the
government's balanced budget from the benefit formulas -- and require the closed forms to reproduce it.

Written after `hi`/`bi` were found to carry a spurious η_{t,i} factor (hRatio was h_iη_i/h, not h_i/h):
`∑_i γ_i η_i h_i == h` and the PAYG balance below are exactly the identities that catch that class of bug,
and neither was covered by the pre-existing tests, which all target the FOC/policy machinery instead.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod

m = testmod.mLOG
T, ni = m.T, m.ni
τ = np.full(T, m.db['τ0'])
θ, ε = m.db['θ'].values, m.db['eps'].values
tFirst = m.B.tFirst

α, ξ, ν = m.db['α'].values, m.db['ξ'].values, m.db['ν'].values
γi, γ0 = m.db['γi'].values, m.db['γ0'].values
γi_, γ0_ = m.db['γi[t-1]'].values, m.db['γ0[t-1]'].values
p_, p0_ = m.db['p[t-1]'].values, m.db['p0[t-1]'].values
ηi, η0, X0 = m.db['ηi'].values, m.db['η0'].values, m.db['X0'].values
η0_, X0_, χ_ = m.db['η0[t-1]'].values, m.db['X0[t-1]'].values, m.db['χ[t-1]'].values
xE = slice(0, T-1)

from gridsearch.testing import check, report

def close(a, b, tol = 1e-10):
    d = np.max(np.abs(np.asarray(a, dtype = float) - np.asarray(b, dtype = float)))
    return d, d < tol


def primitiveChecks(V, init, s0, tag, tol = 1e-10):
    """ Rebuild every consumption level and the government budget from primitives and compare. V: the
    _wrapVars-style report as raw ndarrays; init: initialState_solve's dict; s0: the pre-horizon state. """
    # formal budgets, eq (formalBudget)
    si_full = np.vstack([V['si_s']*V['s'][xE, None], np.zeros((1, ni))])
    d, c = close(V['w'][:, None]*(1-τ)[:, None]*V['hi']*ηi - si_full, V['c1i'], tol)
    check(f'[{tag}] c_1^i == w(1-τ)h_i η_i - s_{{t,i}}', c, f'max|diff|={d:.2e}')
    si_lag = np.vstack([(init['si_s']*s0)[None, :], si_full[:-1]])
    d, c = close(si_lag*(V['R']/p_)[:, None] + V['bi'], V['c2i'], tol)
    check(f'[{tag}] c_2^i == s_{{t-1,i}}*R/p_{{t-1}} + b^i', c, f'max|diff|={d:.2e}')

    # informal budgets, eq (informalBudget) -- hand-to-mouth in this model variant, both when young and
    # when old (the old-age endowment is modelled as labour supply at productivity χ_{t-1}η_{t-1,0}).
    h10 = (η0*V['w0']/X0)**ξ
    d, c = close(V['w0']*η0*h10, V['c10'], tol)
    check(f'[{tag}] c_1^0 == w0*η0*h_1^0 (hand-to-mouth)', c, f'max|diff|={d:.2e}')
    d, c = close(V['c10'] - X0*ξ/(1+ξ)*h10**((1+ξ)/ξ), V['tildec10'], tol)
    check(f'[{tag}] tilde-c_1^0 == c_1^0 - GHH disutility term', c, f'max|diff|={d:.2e}')
    h20 = (χ_*η0_*V['w0']/X0_)**ξ
    d, c = close(V['w0']*χ_*η0_*h20 + V['b0'], V['c20'], tol)
    check(f'[{tag}] c_2^0 == w0*χ_{{t-1}}*η_{{t-1,0}}*h_2^0 + b^0', c, f'max|diff|={d:.2e}')
    d, c = close(V['c20'] - X0_*ξ/(1+ξ)*h20**((1+ξ)/ξ), V['tildec20'], tol)
    check(f'[{tag}] tilde-c_2^0 == c_2^0 - GHH disutility term', c, f'max|diff|={d:.2e}')

    # PAYG balance, eq (governmentBudget) -- ties κ/bbar/bi/b0 together. t=0 pays the pre-horizon generation.
    contrib = ν*V['w']*V['h']*τ/(1+γ0)
    payout = ((γi_*p_[:, None]*V['bi']).sum(axis = 1) + γ0_*p0_*V['b0'])/(1+γ0_)
    d, c = close(contrib[1:], payout[1:], tol)
    check(f'[{tag}] PAYG budget balances at every t>0', c, f'max|diff|={d:.2e}')

    # aggregation identities the closed forms must respect
    d, c = close((γi*ηi*V['hi']).sum(axis = 1), V['h'], tol)
    check(f'[{tag}] ∑_i γ_i η_i h_i == h', c, f'max|diff|={d:.2e}')
    d, c = close((γi[xE]*V['si_s']).sum(axis = 1), np.ones(T-1), tol)
    check(f'[{tag}] ∑_i γ_i (s_i/s) == 1', c, f'max|diff|={d:.2e}')


# ---- base.py's two ratios must be what their names say
hR, hηR = m.BT.hRatio(), m.BT.hηRatio()
d, c = close((γi*ηi*hR).sum(axis = 1), np.ones(T))
check('hRatio: ∑_i γ_i η_i (h_i/h) == 1', c, f'max|diff|={d:.2e}')
d, c = close((γi*hηR).sum(axis = 1), np.ones(T))
check('hηRatio: ∑_i γ_i (h_i η_i/h) == 1', c, f'max|diff|={d:.2e}')
d, c = close(hηR, hR*ηi)
check('hηRatio == hRatio * η_i', c, f'max|diff|={d:.2e}')

# =====================================================================================
# LOG (ρ=1)
# =====================================================================================
s0 = m.steadyState_LOG_solve(τ[tFirst], θ[tFirst], t = tFirst)['s']
sol = m.EE_LOG_solve(τ, θ, ε, s0 = s0)
rep = m.EE_report(sol, τ, θ, ε, s0)
init = m.initialState_solve(τ[tFirst], θ[tFirst])
V = {k: v.values for k, v in rep.items()}

check('no NaN/inf anywhere in the report',
      all(np.all(np.isfinite(v)) for v in V.values()),
      str({k for k, v in V.items() if not np.all(np.isfinite(v))}))
primitiveChecks(V, init, s0, 'LOG')

# =====================================================================================
# CRRA (ρ≠1) -- same identities off the LOG knife-edge
# =====================================================================================
ρCRRA = 1.15
snapshot = dict(m.db)
try:
    m.db.update(m.adjPar('ρ', ρCRRA))
    s0C = m.steadyState_CRRA_solve(τ[tFirst], θ[tFirst], t = tFirst)['s']
    solC = m.EE_CRRA_solve(τ, θ, ε, s0 = s0C, tol = 1e-9)
    repC = m.EE_report(solC, τ, θ, ε, s0C)
    initC = m.initialState_solve(τ[tFirst], θ[tFirst])
    primitiveChecks({k: v.values for k, v in repC.items()}, initC, s0C, f'ρ={ρCRRA}', tol = 1e-9)
finally:
    m.db.clear(); m.db.update(snapshot); m.x0.pop('EE_CRRA', None)

report()
