r""" The economic equilibrium must satisfy the model's own primitive conditions, not just its closed forms.

Run:  .venv\Scripts\python.exe python\InformalSavings\test_ee.py

Every closed form in base.py §4-§7 is a *reduction* of the primitive optimality/budget conditions in
eq (formalOpt)/(informalOpt)/(formalBudget)/(informalBudget)/(governmentBudget). `primitiveChecks` rebuilds
the primitive side independently -- individual savings from the household FOC, consumption from the raw
budget, the government's balanced budget from the benefit formulas -- and requires the closed forms to
reproduce it. That is what catches an algebra slip in the reduction (in particular the new informal-savings
objects R0/B0/s0_s/c10/tildec10/c20), which self-consistency among the closed forms cannot.

It is run at ρ=1 (LOG) and at ρ≠1 (CRRA): only the latter exercises B_{t+1}^0's dependence on the informal
return, since ρ=1 collapses it to the primitive β_0 regardless of R^0.
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
p, p0 = m.db['p'].values, m.db['p0'].values
ηi, η0, X0 = m.db['ηi'].values, m.db['η0'].values, m.db['X0'].values
xE = slice(0, T-1)

from gridsearch.testing import check, report

def close(a, b, tol = 1e-10):
    d = np.max(np.abs(np.asarray(a, dtype = float) - np.asarray(b, dtype = float)))
    return d, d < tol


def primitiveChecks(V, init, s0, tag, tol = 1e-10):
    """ Rebuild every consumption level and the government budget from primitives and compare. V: the
    _wrapVars-style report as raw ndarrays; init: initialState_solve's dict; s0: the pre-horizon state. """
    B0v = V['B0']

    # informal savings from eq (informalOpt), then ι = s_{t,0}/s_t
    income0 = V['w0'][xE]*η0[xE]*V['h0'][xE] - X0[xE]*ξ[xE]/(1+ξ[xE])*V['h0'][xE]**((1+ξ[xE])/ξ[xE])
    pensionPV0 = V['b0'][1:]/(V['R0'][1:]/p0[xE])
    s0i = B0v/(1+B0v)*income0 - pensionPV0/(1+B0v)
    d, c = close(s0i/V['s'][xE], V['ι'], tol)
    check(f'[{tag}] ι == s_{{t,0}}/s_t rebuilt from the informal FOC', c, f'max|diff|={d:.2e}')

    # informal budgets, eq (informalBudget)
    s0i_full = np.append(s0i, 0.)                      # s_{T,0}=0: no period T+1 to save into
    d, c = close(V['w0']*η0*V['h0'] - s0i_full, V['c10'], tol)
    check(f'[{tag}] c_1^0 == w0*η0*h0 - s_{{t,0}}', c, f'max|diff|={d:.2e}')
    d, c = close(V['c10'] - X0*ξ/(1+ξ)*V['h0']**((1+ξ)/ξ), V['tildec10'], tol)
    check(f'[{tag}] tilde-c_1^0 == c_1^0 - GHH disutility term', c, f'max|diff|={d:.2e}')
    s0i_lag = np.append(init['ι']*s0, s0i)             # s_{t-1,0}; t=0's comes from the initial state
    d, c = close(s0i_lag*V['R0']/p0_ + V['b0'], V['c20'], tol)
    check(f'[{tag}] c_2^0 == s_{{t-1,0}}*R^0/p_{{t-1,0}} + b^0', c, f'max|diff|={d:.2e}')
    check(f'[{tag}] tilde-c_2^0 == c_2^0 (informal old supply no labour)',
          np.array_equal(V['tildec20'], V['c20']))

    # formal budgets, eq (formalBudget) -- regression: informal savings must not touch the formal block
    si_full = np.vstack([V['si_s']*V['s'][xE, None], np.zeros((1, ni))])
    d, c = close(V['w'][:, None]*(1-τ)[:, None]*V['hi']*ηi - si_full, V['c1i'], tol)
    check(f'[{tag}] c_1^i == w(1-τ)h_i η_i - s_{{t,i}}', c, f'max|diff|={d:.2e}')
    si_lag = np.vstack([(init['si_s']*s0)[None, :], si_full[:-1]])
    d, c = close(si_lag*(V['R']/p_)[:, None] + V['bi'], V['c2i'], tol)
    check(f'[{tag}] c_2^i == s_{{t-1,i}}*R/p_{{t-1}} + b^i', c, f'max|diff|={d:.2e}')

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


# =====================================================================================
# 1. LOG (ρ=1)
# =====================================================================================
s0 = m.steadyState_LOG_solve(τ[tFirst], θ[tFirst], t = tFirst)['s']
sol = m.EE_LOG_solve(τ, θ, ε, s0 = s0)
rep = m.EE_report(sol, τ, θ, ε, s0)
init = m.initialState_solve(τ[tFirst], θ[tFirst], ε[tFirst])
V = {k: v.values for k, v in rep.items()}

check('ι reports on txE (length T-1)', len(V['ι']) == T-1 and rep['ι'].index.equals(m.db['txE']))
check('B0 reports on txE (length T-1)', len(V['B0']) == T-1)
check('c10/c20 report on t (length T)', len(V['c10']) == T and len(V['c20']) == T)
check('no NaN/inf anywhere in the report',
      all(np.all(np.isfinite(v)) for v in V.values()),
      str({k for k, v in V.items() if not np.all(np.isfinite(v))}))
check('ρ=1: B0 == β0 exactly', np.array_equal(V['B0'], m.db['β0'].values[:-1]))

primitiveChecks(V, init, s0, 'LOG')

# terminal period: informal young neither save nor receive a discounted pension
auxProd0 = η0**(1+ξ)/X0**ξ
d, c = close(V['c10'][-1], auxProd0[-1]*V['w0'][-1]**(1+ξ[-1]))
check('c_{1,T}^0 collapses to eq (TerminalEE)', c, f'|diff|={d:.2e}')
d, c = close(V['tildec10'][-1], V['c10'][-1]/(1+ξ[-1]))
check('tilde-c_{1,T}^0 == c_{1,T}^0/(1+ξ)', c, f'|diff|={d:.2e}')

# the EE core is untouched by informal savings: CRRA at ρ=1 must reproduce LOG exactly
solC = m.EE_CRRA_solve(τ, θ, ε, s0 = s0, tol = 1e-9)
d, c = close(solC['s'].values, sol['s'].values, 1e-8)
check('EE_CRRA_solve == EE_LOG_solve at ρ=1 (s)', c, f'max|diff|={d:.2e}')
d, c = close(m.EE_report(solC, τ, θ, ε, s0)['ι'].values, V['ι'], 1e-8)
check('EE_CRRA report == EE_LOG report at ρ=1 (ι)', c, f'max|diff|={d:.2e}')

# starting from the steady state at a constant policy the path is a fixed point, for as long as the
# exogenous parameters stay at their tFirst values (ν moves over t in the Argentina data).
nSS = int(np.argmax(ν != ν[0])) if np.any(ν != ν[0]) else T-1
d, c = close(sol['s'].values[:nSS], np.full(nSS, s0), 1e-9)
check('constant policy from s* keeps s_t = s* while ν is constant', c, f'nSS={nSS}, max|diff|={d:.2e}')
d, c = close(V['ι'], np.full(T-1, init['ι']), 1e-9)
check('ι_t equals the initial-state ι_{-1} along that path', c, f'max|diff|={d:.2e}')

# ι depends on τ_t (through Θ_{s,t}) -- the property that makes it a political state. si_s, by contrast,
# is a function of τ_{t+1} alone and must NOT move when only τ_t does.
τAlt = τ.copy(); τAlt[4] = τ[4] + 0.05
repAlt = m.EE_report(m.EE_LOG_solve(τAlt, θ, ε, s0 = s0), τAlt, θ, ε, s0)
check('ι_4 responds to τ_4', abs(repAlt['ι'].values[4] - V['ι'][4]) > 1e-6,
      f"Δι={repAlt['ι'].values[4]-V['ι'][4]:.3e}")
check('si_s_4 does not respond to τ_4 (function of τ_5 only)',
      np.allclose(repAlt['si_s'].values[4], V['si_s'][4], atol = 1e-12))

# =====================================================================================
# 2. CRRA (ρ≠1) -- the only case where B^0 genuinely depends on the informal return R^0
# =====================================================================================
ρCRRA = 1.15
snapshot = dict(m.db)
try:
    m.db.update(m.adjPar('ρ', ρCRRA))
    s0C = m.steadyState_CRRA_solve(τ[tFirst], θ[tFirst], t = tFirst)['s']
    solC = m.EE_CRRA_solve(τ, θ, ε, s0 = s0C, tol = 1e-9)
    repC = m.EE_report(solC, τ, θ, ε, s0C)
    initC = m.initialState_solve(τ[tFirst], θ[tFirst], ε[tFirst])
    VC = {k: v.values for k, v in repC.items()}

    check(f'ρ={ρCRRA}: B0 differs from β0 (informal return enters)',
          not np.allclose(VC['B0'], m.db['β0'].values[:-1], atol = 1e-8),
          f"max|B0-β0|={np.max(np.abs(VC['B0']-m.db['β0'].values[:-1])):.2e}")
    d, c = close(VC['B0'], m.db['β0'].values[:-1]**ρCRRA * (VC['R0'][1:]/p0[xE])**(ρCRRA-1))
    check(f'ρ={ρCRRA}: B0 == β0^ρ (R^0/p0)^(ρ-1)', c, f'max|diff|={d:.2e}')
    d, c = close(VC['R0'], VC['R']*m.db['χR'].values)
    check(f'ρ={ρCRRA}: R0 == R·χR', c, f'max|diff|={d:.2e}')
    primitiveChecks(VC, initC, s0C, f'ρ={ρCRRA}', tol = 1e-9)
finally:
    m.db.clear(); m.db.update(snapshot); m.x0.pop('EE_CRRA', None)

report()
