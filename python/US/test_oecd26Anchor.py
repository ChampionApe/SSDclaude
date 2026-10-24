r""" The calibration of the cost parameter in the cross-country test (oecd26.py, runOECD26.py), the slow half of
test_oecd26.py.

Run:  .venv\Scripts\python.exe python\US\test_oecd26Anchor.py        (~5 min)

  R  At the inputs of the published run of 2026-10-03 (the U.S. workbook before review-2026-10), ModelOECD with β
     imposed at that calibration's value reproduces its λ = 8.643207 and ω (escCalibration.csv, 'size', LOG):
     λ is calibrated to eq esc:calibration by ModelESC.calibrateWedge on a narrow bracket.
  A  runOECD26.stageAnchor at coarse grids on the OECD inputs: λ and ω calibrated, the design in force in 2020 on
     the datum, τ_2020 on the target, one tax equilibrium; the U.S. layer-1 row at the anchor reproduces the
     anchor's readouts.
"""
import os, sys, time, tempfile, shutil
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import oecd26
import runOECD26 as R
from gridsearch.testing import check, report

tic = time.time()
# data/USMain_test.xlsx as of the run of 2026-10-03: ν (1960..2080), γ, income, turnout, τ0, θ*; and its results
NU = [1.405486131972424, 1.405486131972424, 1.339667762739423, 1.1219986438186136, 1.0688804499803877]
Γ, INC, MU = [0.5822660721626665, 0.17572652815988363, 0.24200739967744997], [37116., 73299., 160208.], [0.474, 0.629, 0.765]
TAU0, THETA = 0.1442857142857143, 0.7382263650417814
LAMBDA, BETA, OMEGA = 8.64320735564998, 0.7585347063319889, 1.507771142663732

# ==== R ========================================================================================================
y = np.asarray(INC)/np.sum(np.asarray(Γ)*np.asarray(INC))
inp = oecd26.inputsFrom('US', 'US', NU + [NU[-1]]*(1 + oecd26.T_SS), Γ, y, MU, 100*TAU0*0.7, 1/(2 - THETA))
m = oecd26.build(inp, BETA, 1.45, None)
rec = m.calibrateWedge(spec = 'size', phi = 0.5, bracket = (8.0, 9.5), nScan = 3, verbose = False)
ω = float(m.db['ω'].iloc[2])
mult = m.ESC.lastMultiplicity
check("R: λ and ω reproduce escCalibration.csv's 'size' row at its inputs, β imposed",
      rec['converged'] and abs(rec['p'] - LAMBDA) < 1e-6 and abs(ω - OMEGA) < 1e-8,
      'λ {:.9f} (published {:.9f}), ω {:.10f} (published {:.10f}), design residual {:.1e}'.format(
          rec['p'], LAMBDA, ω, OMEGA, rec['residual']))
check('R: one tax equilibrium, no fallback', mult['nEqMax'] == 1 and mult['nFallback'] == 0, str(mult))

# ==== A ========================================================================================================
tmp = tempfile.mkdtemp(prefix = 'oecd26_')
cfg = R.settings(coarse = True) | {'bracket': [3., 40.], 'nScan': 4}
ref = oecd26.usBeta()
a = R.stageAnchor('cps', tmp, cfg, ref)
check('A: anchor: λ and ω calibrated, the design in force in 2020 is the datum, τ_2020 the target',
      a['status'] == 'ok' and abs(a['designResidual']) < 1e-5 and abs(a['τResidual']) < 1e-8
      and abs(a['θInForce'] - a['θData']) < 1e-5 and a['nEqMax'] == 1 and a['nFallback'] == 0,
      'λ {:.4f} ω {:.4f}; θ {:.4f} in force {:.4f}; chosen {:.4f}'.format(a['p'], a['ω'], a['θData'],
                                                                        a['θInForce'], a['θChosen']))
d = pd.read_csv(os.path.join(tmp, 'anchor.csv'))
check('A: one anchor row on disk, accepted by anchorRow', len(d) == 1 and R.anchorRow('cps', tmp, cfg, ref)['p'] == a['p'])
l1 = R.stageLayer('layer1', 'cps', ['USA'], tmp, a, cfg)[0]
check("A: the U.S. layer-1 row at the anchor reproduces the anchor's readouts",
      all(abs(l1[k] - a[k]) < 1e-9 for k in ('τ2020', 'θInForce', 'θChosen', 'R2020', 'Vtilde')),
      ', '.join('{} {:.1e}'.format(k, abs(l1[k] - a[k])) for k in ('τ2020', 'θInForce', 'θChosen', 'R2020')))

shutil.rmtree(tmp, ignore_errors = True)
print('\n({:.0f}s)'.format(time.time() - tic))
report()
