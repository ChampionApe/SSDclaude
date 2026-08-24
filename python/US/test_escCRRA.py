r""" LeadedCRRA against the one benchmark it has: its own LOG limit.

Run:  .venv\Scripts\python.exe python\US\test_escCRRA.py          (~4 min -- a SLOW suite)

`LeadedCRRA` cannot be checked against a closed form, and its path iteration makes an assumption
(`stateSensitivity`) that `LeadedLOG` does not. What it CAN be held to is continuity: as rho -> 1 the CRRA
model becomes the LOG model, so the leaded choice must converge on `LeadedLOG`'s answer, and at a
first-order rate in (rho - 1) since nothing here is kinked at rho = 1.

That is a real test rather than a formality. The two solvers share the objective's weights and nothing
else: LOG maximises a closed-form W_t on a state grid via a backward recursion in theta alone; CRRA
re-solves the whole politico-economic equilibrium at each candidate design and iterates on the path. They
reach the same number from different directions or one of them is wrong.

Also checked: the state-independence that the path iteration relies on, measured at rho != 1 rather than
inferred from the LOG proof.

SLOW, and registered as such in python/runTests.py: each rho costs a (beta, omega) recalibration plus a
grid of full CRRA equilibrium solves.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from modelESC import ModelESC

from gridsearch.testing import check, report

WEDGE = {'spec': 'scale', 'phi': 0.5, 'p': 0.4022}      # the LOG-calibrated wedge, held fixed across rho
GS_LOG = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}
GS_CRRA = GS_LOG | {'ns': 150}


def build(ρ):
    m = ModelESC(pars = testmod.pars | {'ρ': float(ρ), 'β': 0.76, 'ω': 1.45}, wedge = WEDGE,
                 **testmod.kwargs)
    m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
    m.LOG.initGS(GS_LOG)
    m.CRRA.initGS(GS_CRRA)
    m.calibrate()
    return m


# ---- the LOG anchor
mLOG = build(1.0)
θStar = float(mLOG.db['θ'].xs(mLOG.t0Year))
chLOG = mLOG.leadedChoiceAtT0(mLOG.ESC.solveBackward())
check('the LOG leaded choice reproduces theta* at the calibrated wedge (the anchor)',
      abs(chLOG - θStar) < 2e-3, '-> choice={:.6f} vs theta*={:.6f}'.format(chLOG, θStar))

# ---- the limit
ρs = (1.10, 1.05, 1.02)
gaps, slopes = [], []
for ρ in ρs:
    m = build(ρ)
    ch = m.leadedChoiceAtT0_CRRA()
    gaps.append(ch - chLOG)
    slopes.append((ch - chLOG)/(ρ - 1))
    check('rho={:.2f}: the CRRA choice is finite and interior'.format(ρ), 0. < ch < 1.,
          '-> choice={:.6f}  gap to LOG={:+.6f}'.format(ch, ch - chLOG))

check('the gap to the LOG choice shrinks monotonically as rho -> 1',
      all(abs(gaps[i+1]) < abs(gaps[i]) for i in range(len(gaps)-1)),
      '-> gaps={}'.format(', '.join('{:+.5f}'.format(g) for g in gaps)))

# First order in (rho-1): the ratio gap/(rho-1) should settle rather than drift. The candidate grid is
# coarse under CRRA (13 nodes + parabolic refinement), so the tolerance is the grid's, not the solver's.
spread = max(slopes) - min(slopes)
check('...at a first-order rate -- gap/(rho-1) settles', spread < 0.12,
      '-> slopes={} (spread {:.4f})'.format(', '.join('{:.4f}'.format(s) for s in slopes), spread))

# ---- the assumption the path iteration makes, measured away from rho = 1
#
# This MUST be evaluated at rho=2's OWN calibrated wedge, not at the LOG one. A higher EIS needs far less
# wedge (0.090 against 0.408), so WEDGE at rho=2 puts the choice on the theta=1 corner -- where both
# perturbations return 1.0 and the slope is exactly zero for a reason that has nothing to do with state
# dependence. The first version of this test did that and passed vacuously; the interiority check below is
# what makes the measurement mean something.
#
# The constant tracks the csv and has to be refreshed with it: it was 0.0856 under the old calibration
# target (the choice MADE at t0) and is 0.0901 under the current one (the design in FORCE at t0, since
# 2026-08-24). Nothing here asserts the value -- the checks are about solver agreement -- so a stale
# number would not fail, it would quietly stop testing what the comment says it tests.
P_CRRA2 = 0.0901          # results/esc/escCalibrationCRRA.csv, rho=2, scale, phi=0.5
m2 = ModelESC(pars = testmod.pars | {'ρ': 2.0, 'β': 0.76, 'ω': 1.45},
              wedge = WEDGE | {'p': P_CRRA2}, **testmod.kwargs)
m2.db['dates'], m2.db['workweek'] = testmod.dates, testmod.workweek
m2.LOG.initGS(GS_LOG); m2.CRRA.initGS(GS_CRRA)
m2.calibrate()
θc = np.full(m2.T, float(m2.db['θ'].xs(m2.t0Year)))
ch2 = m2.leadedChoiceAtT0_CRRA()
check('rho=2 at its own calibrated wedge gives an INTERIOR choice (so the next check is not vacuous)',
      0.02 < ch2 < 0.98, '-> choice={:.6f} at p={}'.format(ch2, P_CRRA2))
sens = m2.ESCC.stateSensitivity(θc, pos = m2.db['t0'])
check('at rho=2 the leaded choice is still near-independent of the inherited design',
      abs(sens['slope']) < 0.05,
      '-> d(theta_t+2)/d(theta_t+1)={:+.4f} (exactly 0 under LOG); choices {:.4f}/{:.4f}'.format(
          sens['slope'], sens['choiceLo'], sens['choiceHi']))

# ---- the TRUE solver (LeadedCRRA2D): the 2-D backward recursion the path iteration approximates
#
# Two checks, each against something already trusted rather than against itself.
from policyESC import Interp2D

# (a) Interp2D is exact on a bilinear surface, extrapolates along s, clamps along theta.
sg, tg = np.linspace(0.1, 0.4, 7), np.linspace(0., 1., 5)
plane = 2.0*sg[:, None] - 0.5*tg[None, :] + 0.3
f = Interp2D(sg, tg, plane)
qs, qt = np.array([0.13, 0.31, 0.5]), np.array([0.11, 0.77, 0.4])   # last s is OUTSIDE the grid
check('Interp2D reproduces a bilinear surface exactly, extrapolating along s',
      np.allclose(f(qs, qt), 2.0*qs - 0.5*qt + 0.3, atol = 1e-12),
      '-> max|diff|={:.2e}'.format(float(np.max(np.abs(f(qs, qt) - (2.0*qs - 0.5*qt + 0.3))))))
check('Interp2D clamps along theta (queries at the ends of the unit interval)',
      np.allclose(f(0.2, -0.1), f(0.2, 0.0)) and np.allclose(f(0.2, 1.1), f(0.2, 1.0)))

# (b) Pinned everywhere, the 2-D recursion IS the exogenous-theta solver on a redundant grid: force
# theta = theta* at every position and the simulated tau path must land on solvePEE_CRRA's. This checks
# the state fixed point, the FOC assembly, the selection and both interpolants -- everything except the
# W/argmax layer -- against the production solver.
base2 = m2.solvePEE_CRRA()
θStar2 = float(m2.db['θ'].xs(m2.t0Year))
s0b = float(base2['report']['s_'].iloc[0])
solsPin = m2.ESCC2.solvePolicies(θStar2, pinPos = m2.T)      # every period pinned
θP, τP, _, _, _ = m2.ESCC2.simulate(solsPin, θStar2, s0b, pinPos = m2.T)
dτ = float(np.max(np.abs(τP.values - base2['τ'].values)))
check('pinned everywhere, the 2-D recursion reproduces the exogenous CRRA tax path',
      dτ < 5e-3, '-> max|dtau| = {:.2e} (state-grid + theta-interpolation level)'.format(dτ))

# (c) The choice itself, against the path iteration at the calibrated wedge -- the two reach theta_{t0+1}
# by entirely different routes (a 2-D policy recursion vs repeated full-path solves), and at rho=2 the
# measured state slope is ~0.01, so they must agree to grid accuracy. Run at the SOLVE grid (ns=50),
# where the measured choice is 0.7433 against ns=150's 0.7430 -- the s-grid is not what the accuracy
# hangs on; the theta-STATE grid is (7 nodes gave 0.723), so nθ stays at the default 13
# (RESEARCH_LOG 2026-08-24).
m2.CRRA.initGS(GS_LOG | {'ns': 50})
out2D = m2.solveLeaded2D(pinAtT0 = True)
ch2D = m2.leadedChoiceAtT0_2D(out = out2D)
m2.CRRA.initGS(GS_CRRA)
check('the 2-D choice at t0 agrees with the path iteration to grid accuracy',
      abs(ch2D - ch2) < 2.5e-2, '-> 2-D={:.5f} vs path={:.5f} (diff {:+.4f})'.format(
          ch2D, ch2, ch2D - ch2))
check('...and its tau_t0 still hits the calibration target',
      abs(out2D['targetDrift']['τ']) < 5e-4,
      '-> tau drift {:+.2e}, R drift {:+.2e}'.format(out2D['targetDrift']['τ'],
                                                     out2D['targetDrift']['R']))

report()
