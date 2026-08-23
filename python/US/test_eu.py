r""" The France and UK workbooks, end to end through ModelFR (testEU.py + modelFR.py).

Run:  .venv\Scripts\python.exe python\US\test_eu.py

test_fr.py checks the PROTOCOL against a US reference and needs no country data. This suite checks that
the actual workbooks load and calibrate, and it deliberately pins almost no numbers -- the workbooks are
still being assembled, and a suite that hard-codes their contents would fail on every data revision for
no reason. What it asserts instead are the things that must hold whatever the data say:

  * theta = 1 for France, EXACTLY, straight out of RR0 = 1 -- no code imposes it.
  * db['R0'] is NaN, and ModelUS.calibrate therefore REFUSES to run on these workbooks rather than
    quietly targeting the US interest rate that ModelUS's defaults would otherwise supply.
  * beta is the US sweep's value at that rho, held exactly through the search.
  * hbar lands on hbarTarget(), and Gamma_h ends at lambda rather than 1.
  * the UK's own income groups and its US-percentile regrouping are NOT interchangeable.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import testEU
import test as testmod
from model import ModelUS

from gridsearch.testing import check, report

CASES = (('FR', None), ('UK', None), ('UK', 'US'))
usRef = testEU.usReference()

for country, grouping in CASES:
    tag = country + (grouping or '')
    m = testEU.model(country, grouping = grouping)
    t0 = m.db['t'][m.db['t0']]

    check('[{}] workbook loads with 3 formal types plus the zero-mass slot'.format(tag),
          m.nj == 4 and float(np.max(m.db['γ0'])) == 0.)
    check('[{}] the synthetic j=0 slot is finite, not NaN'.format(tag),
          np.isfinite(m.db['ηj'].xs(t0).values.astype(float)).all()
          and np.isfinite(m.db['Xj'].xs(t0).values.astype(float)).all())
    check('[{}] R0 is NaN -- there is no interest-rate target for these countries'.format(tag),
          np.isnan(m.db['R0']))

    cal = m.calibrate(preferences = 'LOG')
    rep = cal['report']
    check('[{}] calibration converges'.format(tag), np.max(np.abs(cal['residual'])) < 1e-8,
          '-> max|residual|={:.2e}'.format(np.max(np.abs(cal['residual']))))
    check('[{}] the tax target is hit'.format(tag), np.isclose(rep['τ'], m.db['τ0'], rtol = 1e-7),
          '-> tau={:.8f} vs target {:.8f}'.format(rep['τ'], m.db['τ0']))
    check('[{}] beta is the US sweep value at rho=1, held exactly'.format(tag),
          np.isclose(m.simpleβinv(), usRef(1.0)['β'], rtol = 1e-12),
          '-> beta={:.8f}'.format(m.simpleβinv()))
    check('[{}] average hours land on the US-referenced target'.format(tag),
          np.isclose(rep['hbar'], m.hbarTarget(), rtol = 1e-9),
          '-> hbar={:.8f} vs target {:.8f}'.format(rep['hbar'], m.hbarTarget()))
    check('[{}] Gamma_h ends at lambda, not 1 -- the normalisation is given up'.format(tag),
          np.allclose(np.asarray(m.db['Γh'], dtype = float), cal['pars']['λ'], rtol = 1e-9),
          '-> Gamma_h={:.6f}, lambda={:.6f}'.format(float(np.max(m.db['Γh'])), cal['pars']['λ']))
    check('[{}] the hours drift is recorded and is machine precision under LOG'.format(tag),
          rep['hoursDrift'] < 1e-8, '-> hoursDrift={:.2e}'.format(rep['hoursDrift']))
    check('[{}] the savings rate is reported and finite (never targeted here)'.format(tag),
          np.isfinite(rep['sr']), '-> sr={:.4f}, R (a prediction)={:.4f}'.format(rep['sr'], rep['R']))

    if country == 'FR':
        check('[FR] theta = 1 exactly, from RR0 = 1 -- nothing in code imposes it',
              np.isclose(float(m.db['θ'].xs(t0)), 1., rtol = 1e-14),
              '-> theta={:.14f}, RR0={:.6f}'.format(float(m.db['θ'].xs(t0)), m.db['RR0']))

# ---- ModelUS must refuse these workbooks rather than import its own R0 default.
# Checked on the residual rather than by running calibrate: a cold-start ModelUS on France's parameters
# fails for an unrelated reason (an infeasible Gamma_s bracket at beta=0.6), which would make a
# raises-anything test pass for the wrong reason and tell us nothing about R0.
parsFR, kwargsFR, _, _ = testEU.load('FR')
mUS = ModelUS(pars = parsFR | {'ρ': 1., 'ω': 2., 'β': .6}, **kwargsFR)
resid = mUS._calResidual({'R': 2.443, 'τ': float(mUS.db['τ0'])})
check('ModelUS residual on a France workbook is NaN in the R entry, not a US default',
      np.isnan(resid[0]) and resid[1] == 0., '-> residual={}'.format(resid))
try:
    mUS._checkConverged(resid, name = 'test')
    check('and _checkConverged rejects it rather than reading NaN as converged', False)
except RuntimeError:
    check('and _checkConverged rejects it rather than reading NaN as converged', True)

# ---- the UK's two groupings are different models, not two views of one
mUK, mUKus = testEU.model('UK'), testEU.model('UK', grouping = 'US')
tUK = mUK.db['t'][mUK.db['t0']]
check('[UK] the two groupings carry different replacement-rate ratios',
      not np.isclose(mUK.db['RR0'], mUKus.db['RR0'], rtol = 1e-3),
      '-> RR0={:.6f} (own groups) vs {:.6f} (US percentiles)'.format(mUK.db['RR0'], mUKus.db['RR0']))
check('[UK] and therefore different theta -- they are not interchangeable',
      not np.isclose(float(mUK.db['θ'].xs(tUK)), float(mUKus.db['θ'].xs(tUK)), rtol = 1e-3),
      '-> theta={:.6f} vs {:.6f}'.format(float(mUK.db['θ'].xs(tUK)), float(mUKus.db['θ'].xs(tUK))))
check('[UK] the US regrouping reproduces the US population shares',
      np.allclose(mUKus.db['γi'].xs(tUK).values.astype(float),
                  testmod.pars['γj'][1:], rtol = 1e-6),
      '-> {}'.format(np.round(mUKus.db['γi'].xs(tUK).values.astype(float), 6)))

report()
