r""" The permanent timing's reference numbers (notes/TODO.md R3), LOG. A SLOW suite (~75 s).

Run:  .venv\Scripts\python.exe python\US\test_escTiming.py

PermanentLOG at (scale, phi = 0.5) and three p: the anticipated-vote fixed point, the incumbent pinning
and the moving ratio, plus the permanent timing's own calibrated p. A change to PermanentLOG, to the
pinning convention or to the calibration protocol that left everything "looking reasonable" would move
these at the sixth digit. The cheap structural checks on the same objects (concentration, pinning,
kinked path, the sequential FOC's sign) stay in test_esc.py.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from modelESC import ModelESC

from gridsearch.testing import check, report

GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}
PARS = testmod.pars | {'ρ': 1.0, 'β': 0.7606187875476447, 'ω': 1.4536273947550569}


def build(wedge):
    m = ModelESC(pars = PARS, wedge = wedge, **testmod.kwargs)
    m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
    m.LOG.initGS(GS)
    return m


PCAL = 0.37503226627596936          # the permanent timing's own calibrated p (scale, phi = 0.5)
# fixed point / incumbent pinning / moving ratio. TODO's "p = 0.375" row is the calibrated p, where the
# fixed point IS theta* by construction (p = 0.375 exactly gives 0.738178).
PERMREF = {0.4:   (0.775076, 0.773380, 0.9096),
           PCAL:  (0.738226, 0.738226, 0.8694),
           0.25:  (0.541576, 0.549211, 0.652294)}
for pRef, (fp, inc, mov) in PERMREF.items():
    mR = build({'spec': 'scale', 'phi': 0.5, 'p': pRef})
    mR.calibrate()
    rR = mR.solvePermanent('LOG')
    check('permanent timing at p={:.6g}: fixed point / incumbent / moving reproduce the reference'.format(pRef),
          abs(rR['θ'] - fp) < 2e-6 and abs(rR['θIncumbent'] - inc) < 2e-6
          and abs(rR['θMoving'] - mov) < (6e-5 if pRef != 0.25 else 2e-6),
          '-> {:.6f} / {:.6f} / {:.6f} vs {} / {} / {}'.format(
              rR['θ'], rR['θIncumbent'], rR['θMoving'], fp, inc, mov))

mPC = build({'spec': 'scale', 'phi': 0.5, 'p': 0.4})
recPC = mPC.calibrateWedge(spec = 'scale', phi = 0.5, preferences = 'permLOG', verbose = False)
check('the permanent timing\'s own calibrated p reproduces 0.37503226627596936',
      recPC['converged'] and abs(recPC['p'] - PCAL) < 2e-6,
      '-> p={:.14f} (residual {:+.1e})'.format(recPC['p'], recPC['residual']))

report()
