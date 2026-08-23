r""" modelFR.ModelFR -- the US-referenced calibration (see modelFR.py's docstring).

Run:  .venv\Scripts\python.exe python\US\test_fr.py

There is no France workbook yet, and this suite deliberately does not need one. It calibrates ModelFR on
the US workbook against the US model's OWN calibration, where the whole protocol reduces to an identity
that can be checked exactly:

    imposed beta = beta_US  and  workweek ratio = 1   ==>   omega_FR = omega_US, lambda = 1,
                                                            and R lands on R0 without being targeted.

That last one is the sharp test. R is dropped from the residual, so nothing in the 1-D root pushes it
anywhere; recovering R0 to 1e-9 says the two-target US root and the one-target FR root found the same
point, which is what "impose beta from the US" is supposed to mean.

The rest of the suite drives the two things that identity holds fixed -- the workweek ratio, and beta --
off their reference values, and checks that each moves exactly what it should and nothing else.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelUS
from modelFR import ModelFR

from gridsearch.testing import check, report


def newUS(commonX = False, **over):
    return ModelUS(pars = testmod.pars | over, commonX = commonX, **testmod.kwargs)


def newFR(usRef = None, commonX = False, **over):
    return ModelFR(pars = testmod.pars | over, commonX = commonX, usRef = usRef, **testmod.kwargs)


def refFrom(cal):
    """ The US reference {beta, hbar, h0} from a finished ModelUS.calibrate. h0 is the US model's own
    average-hours input, which is testmod.pars['h0'] for both variants. """
    return {'β': cal['pars']['β'], 'hbar': cal['report']['hbar'], 'h0': testmod.pars['h0']}


# ---- 0. the search is one-dimensional
check('ModelFR searches over omega only', ModelFR._calPars == ('ω',),
      '-> {}'.format(ModelFR._calPars))
check('ModelFR carries its own bounds (not inherited from the 2-D US ones)',
      set(ModelFR._calBounds) == {'ω'}, '-> {}'.format(sorted(ModelFR._calBounds)))
check('the residual has one entry, and it is the tax target',
      len(ModelFR._calResidual(newFR(), {'τ': 0.2, 'R': 1.})) == 1)

# ---- 1. the reference identity, vector X
usA = newUS()
calUS = usA.calibrate(preferences = 'LOG')
refA = refFrom(calUS)

frA = newFR(usRef = refA)
calFR = frA.calibrate(preferences = 'LOG')
repFR, repUS = calFR['report'], calUS['report']

check('FR calibration converges', np.max(np.abs(calFR['residual'])) < 1e-8,
      '-> max|residual|={:.2e}'.format(np.max(np.abs(calFR['residual']))))
check('tax target hit', np.isclose(repFR['τ'], frA.db['τ0'], rtol = 1e-7),
      '-> tau={:.8f} vs target {:.8f}'.format(repFR['τ'], frA.db['τ0']))
check('omega reproduces the US value', np.isclose(calFR['pars']['ω'], calUS['pars']['ω'], rtol = 1e-7),
      '-> omega_FR={:.8f} vs omega_US={:.8f}'.format(calFR['pars']['ω'], calUS['pars']['ω']))
check('lambda is 1 at a workweek ratio of 1', np.isclose(calFR['pars']['λ'], 1., rtol = 1e-9),
      '-> lambda={:.12f}'.format(calFR['pars']['λ']))
check('R lands on R0 although it is NOT a target here',
      np.isclose(repFR['R'], frA.db['R0'], rtol = 1e-7),
      '-> R={:.8f} vs the untargeted R0={:.8f}'.format(repFR['R'], frA.db['R0']))
check('beta is the imposed value, unmoved by the search',
      np.isclose(frA.simpleβinv(), refA['β'], rtol = 1e-12),
      '-> beta={:.10f} vs imposed {:.10f}'.format(frA.simpleβinv(), refA['β']))
check('calibrate records the imposed beta in pars (it is not in _calPars)',
      np.isclose(calFR['pars']['β'], refA['β'], rtol = 1e-12))
check('the savings rate matches the US, being invariant to everything that differs',
      np.isclose(repFR['sr'], repUS['sr'], rtol = 1e-7),
      '-> sr={:.8f} vs {:.8f}'.format(repFR['sr'], repUS['sr']))
check('Gamma_h is still 1 when lambda is 1',
      np.isclose(float(np.max(frA.db['Γh'])), 1., rtol = 1e-9),
      '-> Gamma_h={:.12f}'.format(float(np.max(frA.db['Γh']))))

# ---- 2. a workweek ratio != 1: what the X rescaling moves, and what it must not
r = 1.25
frR = newFR(usRef = refA | {'hbar': refA['hbar']*r})
calR = frR.calibrate(preferences = 'LOG')
repR = calR['report']
t0 = frR.db['t'][frR.db['t0']]
ξ = float(frR.db['ξ'].xs(t0))

check('[ratio] lambda equals the workweek ratio', np.isclose(calR['pars']['λ'], r, rtol = 1e-9),
      '-> lambda={:.10f} vs r={:.10f}'.format(calR['pars']['λ'], r))
check('[ratio] average hours hit the referenced target',
      np.isclose(repR['hbar'], refA['hbar']*r, rtol = 1e-9),
      '-> hbar={:.8f} vs target {:.8f}'.format(repR['hbar'], refA['hbar']*r))
check('[ratio] hbar scales by exactly r relative to the ratio-1 calibration',
      np.isclose(repR['hbar'], repFR['hbar']*r, rtol = 1e-9))
check('[ratio] omega does not move -- the rescaling is block-recursive to the root',
      np.isclose(calR['pars']['ω'], calFR['pars']['ω'], rtol = 1e-9),
      '-> omega={:.10f} vs {:.10f}'.format(calR['pars']['ω'], calFR['pars']['ω']))
check('[ratio] tau does not move', np.isclose(repR['τ'], repFR['τ'], rtol = 1e-9))
check('[ratio] R does not move', np.isclose(repR['R'], repFR['R'], rtol = 1e-9))
check('[ratio] the savings rate does not move', np.isclose(repR['sr'], repFR['sr'], rtol = 1e-9))
check('[ratio] theta does not move', np.isclose(float(frR.db['θ'].xs(t0)), float(frA.db['θ'].xs(t0)), rtol = 1e-9))
check('[ratio] aggregate h DOES scale by r -- this is the scale invariance, not the hours unit',
      np.isclose(repR['h'], repFR['h']*r, rtol = 1e-9),
      '-> h={:.8f} vs {:.8f}'.format(repR['h'], repFR['h']*r))
check('[ratio] Gamma_h = lambda, i.e. the Gamma_h = 1 normalisation is given up',
      np.allclose(np.asarray(frR.db['Γh'], dtype = float), r, rtol = 1e-9),
      '-> Gamma_h={:.10f} vs lambda={:.10f}'.format(float(np.max(frR.db['Γh'])), r))
check('[ratio] every X_i moves by the same factor lambda^(-1/xi)',
      np.allclose(frR.db['Xi'].xs(t0).values.astype(float),
                  frA.db['Xi'].xs(t0).values.astype(float) * r**(-1/ξ), rtol = 1e-9),
      '-> X_i={} vs {}'.format(np.round(frR.db['Xi'].xs(t0).values.astype(float), 5),
                               np.round(frA.db['Xi'].xs(t0).values.astype(float) * r**(-1/ξ), 5)))
check('[ratio] eta_i is untouched by the rescaling',
      np.allclose(frR.db['ηi'].xs(t0).values.astype(float),
                  frA.db['ηi'].xs(t0).values.astype(float), rtol = 1e-12))
hiOf = lambda rep: rep['PEE']['report']['hi'].xs(t0).values.astype(float)
check('[ratio] individual hours h_i scale by r, like every other level',
      np.allclose(hiOf(repR), hiOf(repFR)*r, rtol = 1e-9),
      '-> h_i={} vs {}'.format(np.round(hiOf(repR), 5), np.round(hiOf(repFR)*r, 5)))
check('[ratio] relative hours h_i/h are therefore unchanged',
      np.allclose(hiOf(repR)/repR['h'], hiOf(repFR)/repFR['h'], rtol = 1e-9))

# ---- 2b. lambda is a LEVEL, not an increment
# rescaleX multiplies the X_i already in db, so without the reset in calibrate a repeated call -- or the
# next point of a march, which reuses one instance -- reports the small step from the previous solution
# instead of the total rescaling. The equilibrium is right either way, which is exactly what makes this
# worth pinning: the wrong lambda is plausible and lands every other column on target.
again = frR.calibrate(preferences = 'LOG')
check('[repeat] lambda is unchanged by re-calibrating (not collapsed to ~1)',
      np.isclose(again['pars']['λ'], calR['pars']['λ'], rtol = 1e-9),
      '-> lambda={:.10f} vs {:.10f} on the first call'.format(again['pars']['λ'], calR['pars']['λ']))
check('[repeat] lambda equals Gamma_h, i.e. the total rescaling from the Gamma_h = 1 baseline',
      np.isclose(again['pars']['λ'], float(np.max(frR.db['Γh'])), rtol = 1e-9),
      '-> lambda={:.10f}, Gamma_h={:.10f}'.format(again['pars']['λ'], float(np.max(frR.db['Γh']))))
check('[repeat] omega is unchanged too', np.isclose(again['pars']['ω'], calR['pars']['ω'], rtol = 1e-9))
check('[repeat] average hours still land on the target',
      np.isclose(again['report']['hbar'], frR.hbarTarget(), rtol = 1e-9))
check('[repeat] X_i are unchanged -- the reset re-derives them, it does not drift them',
      np.allclose(frR.db['Xi'].xs(t0).values.astype(float),
                  frA.db['Xi'].xs(t0).values.astype(float) * r**(-1/ξ), rtol = 1e-9))

# ---- 3. beta really is imposed, not searched
frB = newFR(usRef = refA | {'β': refA['β']*1.1})
calB = frB.calibrate(preferences = 'LOG')
check('[beta] a different imposed beta is held exactly',
      np.isclose(frB.simpleβinv(), refA['β']*1.1, rtol = 1e-12),
      '-> beta={:.10f} vs imposed {:.10f}'.format(frB.simpleβinv(), refA['β']*1.1))
check('[beta] the tax target is still hit',
      np.isclose(calB['report']['τ'], frB.db['τ0'], rtol = 1e-7))
check('[beta] R misses R0, as it must once it is not a target',
      not np.isclose(calB['report']['R'], frB.db['R0'], rtol = 1e-3),
      '-> R={:.6f} vs R0={:.6f}'.format(calB['report']['R'], frB.db['R0']))
check('[beta] omega had to move to keep the tax target',
      not np.isclose(calB['pars']['ω'], calFR['pars']['ω'], rtol = 1e-3),
      '-> omega={:.6f} vs {:.6f}'.format(calB['pars']['ω'], calFR['pars']['ω']))

# ---- 4. commonX: the referenced target reduces to the observed workweek
usX = newUS(commonX = True)
calUSX = usX.calibrate(preferences = 'LOG')
refX = refFrom(calUSX)
check('[commonX] hbar_US equals h0_US there, so the reference ratio is the raw workweek',
      np.isclose(refX['hbar'], testmod.pars['h0'], rtol = 1e-9),
      '-> hbar_US={:.10f} vs h0={:.10f}'.format(refX['hbar'], testmod.pars['h0']))

frX = newFR(usRef = refX, commonX = True)
calFRX = frX.calibrate(preferences = 'LOG')
check('[commonX] FR calibration converges', np.max(np.abs(calFRX['residual'])) < 1e-8)
check('[commonX] omega reproduces the US value',
      np.isclose(calFRX['pars']['ω'], calUSX['pars']['ω'], rtol = 1e-7),
      '-> omega={:.8f} vs {:.8f}'.format(calFRX['pars']['ω'], calUSX['pars']['ω']))
check('[commonX] X reproduces the US value',
      np.isclose(calFRX['pars']['X'], calUSX['pars']['X'], rtol = 1e-7),
      '-> X={:.8f} vs {:.8f}'.format(calFRX['pars']['X'], calUSX['pars']['X']))
check('[commonX] no lambda -- X carries the hours unit there, no rescaling is applied',
      'λ' not in calFRX['pars'])
check('[commonX] average hours hit the target',
      np.isclose(calFRX['report']['hbar'], frX.hbarTarget(), rtol = 1e-9))

frXr = newFR(usRef = refX | {'hbar': refX['hbar']*r}, commonX = True)
calFRXr = frXr.calibrate(preferences = 'LOG')
check('[commonX] a workweek ratio r moves X by r^((1+xi)/xi), not by lambda^(-1/xi)',
      np.isclose(calFRXr['pars']['X'], calFRX['pars']['X'] * r**(-(1+ξ)/ξ), rtol = 1e-8),
      '-> X={:.8f} vs {:.8f}'.format(calFRXr['pars']['X'], calFRX['pars']['X'] * r**(-(1+ξ)/ξ)))
check('[commonX] omega still does not move', np.isclose(calFRXr['pars']['ω'], calFRX['pars']['ω'], rtol = 1e-9))

# ---- 5. the guards
try:
    newFR().calibrate(preferences = 'LOG')
    check('calibrate without a US reference raises', False)
except ValueError as e:
    check('calibrate without a US reference raises', 'US reference' in str(e))

try:
    newFR(usRef = refA).calibratePoint(0.9, par = 'ρ')
    check('marching over rho with a FIXED reference raises', False)
except TypeError as e:
    check('marching over rho with a FIXED reference raises', 'callable' in str(e))

try:
    newFR(usRef = {'β': 0.7, 'hbar': 0.3}).calibrate(preferences = 'LOG')
    check('an incomplete US reference raises', False)
except KeyError as e:
    check('an incomplete US reference raises', 'h0' in str(e))

# ---- 6. a rho march takes beta and hbar from the reference at each rho
usRefByRho = {1.0: refA, 0.9: refA | {'β': refA['β']*0.95, 'hbar': refA['hbar']*1.05}}
frM = newFR(usRef = lambda ρ: usRefByRho[ρ])
rec = frM.calibratePoint(1.0, par = 'ρ')   # preferences follow db['rho'] -- LOG at 1.0
check('[march] calibratePoint installs the reference beta at that rho',
      np.isclose(rec['β'], refA['β'], rtol = 1e-12), '-> beta={:.10f}'.format(rec['β']))
check('[march] the record carries lambda, so a sweep csv writes it down',
      np.isclose(rec['λ'], 1., rtol = 1e-9))
check('[march] the record reproduces the US omega', np.isclose(rec['ω'], calUS['pars']['ω'], rtol = 1e-7))
frM.setUSRef(**usRefByRho[0.9])
check('[march] setUSRef at a different rho installs that beta',
      np.isclose(frM.simpleβinv(), refA['β']*0.95, rtol = 1e-12))
check('[march] and moves the hours target with it',
      np.isclose(frM.hbarTarget(), refA['hbar']*1.05, rtol = 1e-12))
check('[march] the reference table the callable returns is NOT mutated by override',
      usRefByRho[1.0] == refA and np.isclose(usRefByRho[0.9]['β'], refA['β']*0.95, rtol = 1e-12),
      '-> a shared dict edited in place would import one rho\'s beta at every later point')

report()
