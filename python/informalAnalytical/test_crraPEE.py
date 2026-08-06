r""" model.py's solvePEE_CRRA -- end-to-end CRRA politico-economic equilibrium.

Run:  .venv\Scripts\python.exe python\informalAnalytical\test_crraPEE.py

Three things to check, corresponding to the three genuinely new pieces added on top of
policy.py's CRRA.solveBackward (already tested in test_crraBackward.py):

  1. steadyStatePEE_CRRA is a genuine fixed point: tau* = clip(tauPolicy_tFirst(steadyState(tau*)['s'])).
  2. approximatePEE reproduces report_t's own gridded data exactly when walked from a grid node --
     it is a forward *read* of already-computed data, not a new solve, so this must be exact.
  3. solvePEE_CRRA's warm start changes only performance, never the answer: EE_CRRA_solve is re-solved
     exactly regardless of x0, so warmStart=True/False must converge to the same equilibrium.

Plus a continuity sanity check: as rho -> 1, solvePEE_CRRA should land close to solvePEE_LOG (rho=1).
Not exact -- the mechanisms differ entirely (grid interpolation + exact re-solve vs. closed form) -- but
close, since the underlying economics is continuous in rho.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelInformalAnalytical

ok = True
def check(name, cond, extra = ''):
    global ok
    print(('PASS' if cond else 'FAIL') + '  ' + name + ' ' + extra)
    if not cond:
        ok = False

m = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 1.5}, **testmod.kwargs)
th, eps = m.db['θ'].values, m.db['eps'].values
tFirst = m.B.tFirst
posT = m.db['t'].get_loc(m.db['t'][-1])
sG = m.CRRA.defaultSGrid(th[posT], m.db['t'][-1], n = 25)
sols = m.CRRA.solveBackward(th, eps, sGrid = sG)

# ---- 1. steadyStatePEE_CRRA: genuine fixed point
ss = m.steadyStatePEE_CRRA(sols, th)
l, u = m.CRRA.GS['PEE']['gridSettings']['l'], m.CRRA.GS['PEE']['gridSettings']['u']
tauImplied = float(np.clip(sols[tFirst]['τPolicy'](ss['s']), l, u))
ssCheck = m.steadyState_CRRA_solve(tauImplied, th[tFirst], t = tFirst)
check('steadyStatePEE_CRRA fixed point: steadyState(clip(τPolicy(s*)))[s] == s*',
      np.isclose(ssCheck['s'], ss['s'], rtol = 1e-6),
      '-> s*={:.6f}, round-trip={:.6f}'.format(ss['s'], ssCheck['s']))

# ---- 2. approximatePEE: exact reproduction of report_t's own data at a grid node
node = sG[10]
path = m.CRRA.approximatePEE(sols, node)
t0 = m.db['t'][0]
check('approximatePEE τ[0] == report_t τPolicy at that state, exactly',
      np.isclose(path['τ'].values[0], np.clip(sols[t0]['τPolicy'](node), l, u), atol = 1e-12))
check('approximatePEE Γs[0]/h[0]/s[0] match report_t data at the node, exactly',
      np.isclose(path['Γs'][0], sols[t0]['ΓsPolicy'](node), atol = 1e-12) and
      np.isclose(path['h'][0], sols[t0]['hPolicy'](node), atol = 1e-12) and
      np.isclose(path['s'][0], sols[t0]['sPolicy'](node), atol = 1e-12))

# ---- 3. solvePEE_CRRA end to end, with and without the warm start
sol1 = m.solvePEE_CRRA(θ = th, ε = eps, warmStart = True)
m.x0.pop('EE_CRRA', None)
sol2 = m.solvePEE_CRRA(θ = th, ε = eps, warmStart = False)
check('solvePEE_CRRA returns the expected keys', set(sol1) == {'sols', 'τ', 'sol', 'report'})
s1v, s2v = sol1['report']['s'].values, sol2['report']['s'].values
check('warmStart True/False converge to the SAME exact equilibrium',
      np.allclose(s1v, s2v, rtol = 1e-6, atol = 1e-10),
      '-> max abs diff={:.2e}'.format(np.max(np.abs(s1v - s2v))))
check('τ path finite and in [0,1]',
      np.all(np.isfinite(sol1['τ'].values)) and np.all((sol1['τ'].values >= 0) & (sol1['τ'].values <= 1)),
      '-> range [{:.4f}, {:.4f}]'.format(sol1['τ'].values.min(), sol1['τ'].values.max()))
check('report s/h finite',
      np.all(np.isfinite(sol1['report']['s'].values)) and np.all(np.isfinite(sol1['report']['h'].values)))

# ---- 4. continuity against LOG as rho -> 1
mNear1 = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 1.02}, **testmod.kwargs)
solCRRA = mNear1.solvePEE_CRRA(θ = mNear1.db['θ'].values, ε = mNear1.db['eps'].values)
mLOG = ModelInformalAnalytical(pars = testmod.pars | {'ρ': 1.0}, **testmod.kwargs)
solLOG = mLOG.solvePEE_LOG()
diff = np.abs(solCRRA['τ'].values - solLOG['policy']['τ'].values)
check('ρ=1.02 CRRA PEE is close to LOG (ρ=1) PEE', diff.max() < 0.05,
      '-> max|diff|={:.4f}'.format(diff.max()))

print()
print('ALL PASS' if ok else 'SOME FAILURES')
sys.exit(0 if ok else 1)
