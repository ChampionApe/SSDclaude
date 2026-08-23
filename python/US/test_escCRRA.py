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
# wedge (0.086 against 0.402), so WEDGE at rho=2 puts the choice on the theta=1 corner -- where both
# perturbations return 1.0 and the slope is exactly zero for a reason that has nothing to do with state
# dependence. The first version of this test did that and passed vacuously; the interiority check below is
# what makes the measurement mean something.
P_CRRA2 = 0.0856          # results/esc/escCalibrationCRRA.csv, rho=2, scale, phi=0.5
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

report()
