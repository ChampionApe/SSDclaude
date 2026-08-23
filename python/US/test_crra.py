r""" The CRRA steady-state bracket, and CRRA continuity into the LOG limit.

Run:  .venv\Scripts\python.exe python\US\test_crra.py

The Argentina models bracket the Gamma_s search at a constant (1e-6, 0.75). That is safe there by
parameter values, not by construction: the Theta_h denominator vanishes at Base.GammaSCap, which scales
with alpha/(1-alpha) and kappa/p. At US parameters (alpha = 0.30, kappa = p) the cap falls below 0.75
once tau is high enough, and steadyStatePEE_CRRA searches tau across the whole of [l,u] -- so the
constant bracket makes brentq evaluate a NaN and raise a message pointing at the solver rather than at
the infeasible bracket. model.py's steadyState_CRRA_bounds ties the bracket to the model instead.

The regression guard below is deliberately phrased as "the OLD constant would have failed": retuning the
constant would only move the tau at which the trap reappears, so the test has to assert that the bracket
tracks the model, not that some particular number works.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelUS

from gridsearch.testing import check, report

m = ModelUS(pars = testmod.pars | {'ρ': 1.1}, **testmod.kwargs)
θ = m.db['θ'].values
tFirst, t0 = m.B.tFirst, m.db['t'][m.db['t0']]
θ0 = θ[m.db['t0']]

# ---- 1. GammaSCap is exactly where the Theta_h denominator vanishes
α, p, κ, Γh = m.B.get('α', t0), m.B.get('p', t0), m.B.get('κ', t0), m.B.Γh(t0)
for τ in (0.1, 0.5, 0.9):
    cap = m.B.ΓsCap(τ, θ0, t0)
    denom = Γh - (1-α)/α * p*θ0*τ/κ * cap
    check('GammaSCap zeroes the Theta_h denominator at tau={}'.format(τ), abs(denom) < 1e-12,
          '-> cap={:.4f}, denom={:.2e}'.format(cap, denom))
check('GammaSCap is infinite when theta*tau = 0', np.isinf(m.B.ΓsCap(0., θ0, t0)))

# ---- 2. the bracket tracks the model, and the old constant would have failed
capHigh = m.B.ΓsCap(1.0, θ0, t0)
check('the cap falls below the Argentina constant 0.75 at high tau', capHigh < 0.75,
      '-> cap(tau=1)={:.4f}'.format(capHigh))
lo, hi = m.steadyState_CRRA_bounds(1.0, θ0, t0)
check('steadyState_CRRA_bounds stays strictly inside the cap', hi < capHigh,
      '-> upper={:.4f} vs cap={:.4f}'.format(hi, capHigh))
check('steadyState_CRRA_bounds leaves the constant alone where it is safe',
      np.isclose(m.steadyState_CRRA_bounds(0.1, θ0, t0)[1], 0.75),
      '-> upper at tau=0.1: {:.4f}'.format(m.steadyState_CRRA_bounds(0.1, θ0, t0)[1]))
# Regression guard: the residual at the old constant really is NaN, i.e. the trap was real.
check('the OLD constant bracket evaluates to NaN at high tau (the trap this fixes)',
      np.isnan(m.steadyState_CRRA_residual(0.75, 1.0, θ0, tFirst)))

# ---- 3. the steady state solves across the whole tau range the PEE search visits
bad = [τ for τ in np.linspace(0., 0.99, 34)
       if not np.isfinite(m.steadyState_CRRA_solve(τ, θ0, t = tFirst)['s'])]
check('steadyState_CRRA_solve returns a finite s for every tau in [0, 0.99]', not bad,
      '-> failures at {}'.format(bad[:5]))

# ---- 4. solvePEE_CRRA runs on both sides of rho = 1
for ρ in (0.9, 1.1):
    mρ = ModelUS(pars = testmod.pars | {'ρ': ρ}, **testmod.kwargs)
    out = mρ.solvePEE_CRRA()
    check('solvePEE_CRRA solves at rho={}'.format(ρ),
          np.all(np.isfinite(out['τ'].values)) and np.all(np.isfinite(out['report']['s'].values)),
          '-> tau(t0)={:.6f}'.format(out['τ'].xs(t0)))

# ---- 5. the well-posedness grid settings are pinned and actually reach the solve
gs = m.CRRA.GS['PEE']['gridSettings']
check('the policy smoother pins its knots by default', gs['smoothKnots'] == 4,
      '-> smoothKnots={}'.format(gs['smoothKnots']))
check('an interpolant kind is recorded rather than left implicit', gs['interpKind'] in ('linear', 'cubic', 'pchip'),
      '-> interpKind={!r}'.format(gs['interpKind']))
check('ns is a grid setting, so a sweep can refine it through initGS', 'ns' in gs, '-> ns={}'.format(gs['ns']))
mOv = ModelUS(pars = testmod.pars | {'ρ': 1.1}, **testmod.kwargs)
mOv.CRRA.initGS({'smoothKnots': None, 'ns': 33})
check('initGS overrides reach the settings dict',
      mOv.CRRA.GS['PEE']['gridSettings']['smoothKnots'] is None
      and mOv.CRRA.GS['PEE']['gridSettings']['ns'] == 33)
# The adaptive smoother must produce a DIFFERENT answer -- otherwise the setting is not wired through and
# the measurement behind the default (policy.py's _gridSettings) would be describing a no-op.
τPinned = m.solvePEE_CRRA()['τ'].values
mAd = ModelUS(pars = testmod.pars | {'ρ': 1.1}, **testmod.kwargs)
mAd.CRRA.initGS({'smoothKnots': None})
τAdaptive = mAd.solvePEE_CRRA()['τ'].values
check('smoothKnots is wired through (pinned vs adaptive differ)',
      not np.allclose(τPinned, τAdaptive, rtol = 1e-12, atol = 1e-14),
      '-> max|dtau|={:.2e}'.format(np.max(np.abs(τPinned-τAdaptive))))

# ---- 6. continuity: as rho -> 1 the CRRA path approaches the LOG one
mLog = ModelUS(pars = testmod.pars | {'ρ': 1}, **testmod.kwargs)
τLog = mLog.solvePEE_LOG()['τ'].values
mNear = ModelUS(pars = testmod.pars | {'ρ': 1+1e-3}, **testmod.kwargs)
τNear = mNear.solvePEE_CRRA()['τ'].values
gap = np.max(np.abs(τNear - τLog))
check('CRRA at rho=1.001 lands close to the LOG path', gap < 5e-3,
      '-> max|dtau|={:.2e}'.format(gap))

report()
