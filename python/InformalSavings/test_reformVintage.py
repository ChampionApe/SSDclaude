r""" The reform period of a model copy, the GDP concept of the tax target, and the epsPre0 variant.

Run:  .venv\Scripts\python.exe python\InformalSavings\test_reformVintage.py      (~1-2 min)

  1-3. eq:shockState: the generation old at t0 saved at t0-1 under the baseline's system, so on a reform
       copy it enters with the baseline path's formal savings shares s_{t0-1,i}/s_{t0-1}, ι_{t0-1} and
       h_{t0-1} (stateAtT0's seed). The t0 tax condition holds the shares there, at every candidate tax
       and state, and the consistency step (shares consistent with each candidate) applies from t0+1 on,
       at the copy's own vintage. EE_report reports t0's c2i/c20/bbar off the same lags. LOG, then CRRA
       on small grids.
  4.   model.taxTarget: pension spending over GDP, GDP = formal plus informal output. The closed form,
       and the identity it rests on, checked on a solved path where the η_0/X_0 targets are met.
  5.   ModelInformalSavings(epsPre0=True): ε = 0 before the reform, a reform from zero, the pickle flag
       and shockUniversal.loadCalibrated's guard.
  6.   shockUniversal.frame's formal-benefit readouts against eq:governmentBudget's average.

Parameters near the ρ = 1 vector-X calibration (results/calibration/informalSavings_rhoGrid.csv of
2026-10-07, rounded): the reform's t0 tax is interior there, which test.py's defaults do not guarantee.
"""
import os, sys, pickle, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import ModelInformalSavings
import shockUniversal as su

from gridsearch.testing import check, report

NEAR = {'β': 0.6495, 'ω': 1.4501, 'η0': 0.2883, 'X0': 0.3753}
NEAR_CRRA = {'β': 0.5057, 'ω': 1.2979, 'η0': 0.2884, 'X0': 0.3764}     # the ρ = 1.5 row, rounded
CRRA_GRID = {'nι': 12, 'ns': 12, 'interpKind': 'cubic', 'smoothKnots': 4}


def model(pars, ρ = 1.0, **kwargs):
    m = ModelInformalSavings(pars = testmod.pars | {'ρ': ρ}, **testmod.kwargs, **kwargs)
    m._calSetPars(pars)
    return m


def attempt(fn):
    """ fn() or the exception it raised: a check on an API the code may not have prints FAIL, not a crash. """
    try:
        return fn()
    except Exception as e:                       # noqa: BLE001 -- reported through the check's detail
        return e


def maxAbs(a, b):
    return float(np.max(np.abs(np.asarray(a, dtype = float) - np.asarray(b, dtype = float))))


def reformCopy(m, solve, seed, t0):
    """ The headline reform on a copy (shockUniversal's steps 3-4): eps^U under 'match', refType 1. """
    mt0 = m.createCopyFromt0(t0)
    su.installEps(mt0, su.universalEps(mt0))
    return mt0, getattr(mt0, solve)(**seed)


def lagChecks(tag, m, mt0, base, shock, seed, tPrev):
    """ Sections 1-3's checks shared by LOG and CRRA: the t0 shares are the baseline's, t0+1's are the
    consistent ones at the copy's vintage, and EE_report's first-period lags are the seed's. """
    xBase = base['report']['si_s'].xs(tPrev).values
    inh = seed.get('inherited') or {}
    check(tag + ': stateAtT0 carries the baseline shares s_{t0-1,i}/s_{t0-1} and h_{t0-1}',
          np.array_equal(inh.get('si_s', np.nan), xBase) and inh.get('h') == base['report']['h'].xs(tPrev))

    s0 = np.asarray(shock['sols'][0]['si_s_'])
    check(tag + ': the t0 tax condition holds the baseline shares at every state (reform copy)',
          maxAbs(s0.reshape(-1, len(xBase)), np.broadcast_to(xBase, s0.reshape(-1, len(xBase)).shape)) == 0,
          '-> max|Δ| = {:.2e}'.format(maxAbs(s0.reshape(-1, len(xBase)),
                                               np.broadcast_to(xBase, s0.reshape(-1, len(xBase)).shape))))

    # t0+1: the consistency step at the copy's vintage 0 (new eps in κ_{t0}), at the selected taxes.
    s1 = shock['sols'][1]
    τ1 = np.asarray(s1['τ'], dtype = float)
    if 'B' in s1 and np.ndim(s1['B']) == 3:     # CRRA: B_{t0+1}^i of the generation old at t0+1
        B = np.asarray(s1['B'], dtype = float).reshape(-1, len(xBase))
    else:
        B = mt0.BG.get('βi', 0)
    Γ = mt0.BG.Γs(B, τ1.reshape(-1), mt0.db['θ'].values[1], 0)
    want = mt0.BG.si_s(B, τ1.reshape(-1), mt0.db['θ'].values[1], Γ, 0)
    got = np.asarray(s1['si_s_'], dtype = float).reshape(-1, len(xBase))
    ok = np.isfinite(got).all(axis = 1)
    check(tag + ': t0+1 rebuilds the shares consistently at the copy\'s vintage (the new eps)',
          ok.any() and maxAbs(got[ok], want[ok]) < 1e-13 and np.ptp(got[ok][:, 0]) > 0,
          '-> max|Δ| = {:.2e}, spread over states {:.2e}'.format(maxAbs(got[ok], want[ok]), np.ptp(got[ok][:, 0])))

    # EE_report's first period: c2i at the inherited shares, c20 at ι0, bbar at the inherited h_{t0-1}.
    rep, B0 = shock['report'], mt0.B
    τ, θ, ε = float(shock['τ'].iloc[0]), mt0.db['θ'].values[0], mt0.db['eps'].values[0]
    h, w, s0v = rep['h'].xs(0), rep['w'].xs(0), float(seed['s0'])
    c2i = B0.c2i(h, s0v, τ, θ, xBase, t = 0)
    c20 = B0.c20(h, s0v, ε, τ, seed['ι0'], t = 0)
    bbar = B0.bbar(τ, w, h, inh.get('h', np.nan), t = 0)
    dev = [maxAbs(rep['c2i'].xs(0)/c2i, 1), abs(rep['c20'].xs(0)/c20 - 1), abs(rep['bbar'].xs(0)/bbar - 1)]
    check(tag + ': EE_report\'s t0 lags are the seed\'s (c2i at the baseline shares, c20 at ι0, bbar at h_{t0-1})',
          max(dev) < 1e-13, '-> relative |Δ| c2i {:.1e}, c20 {:.1e}, bbar {:.1e}'.format(*dev))
    return xBase


# ---- 1. LOG: the baseline, its seed, the reform copy --------------------------------------------------
m = model(NEAR)
t0, tPrev = m.db['t'][m.db['t0']], m.db['t'][m.db['t0'] - 1]
base = m.solvePEE_LOG()
seed = m.stateAtT0(base['report'], t0, init = base['init'])
mt0, shock = reformCopy(m, 'solvePEE_LOG', seed, t0)
check('LOG reform: the 2010 tax is interior (so the share convention can move it)',
      0.02 < float(shock['τ'].iloc[0]) < 0.98 and not shock['path']['atBound'][0],
      '-> τ_t0 = {:.6f}'.format(float(shock['τ'].iloc[0])))
xBase = lagChecks('LOG', m, mt0, base, shock, seed, tPrev)

# The convention is not a no-op here (#10): the shares the copy's own vintage implies at t0 -- the
# consistency step under the new eps -- differ from the inherited ones at the reform's own t0 tax.
τR = np.atleast_1d(float(shock['τ'].iloc[0]))
Γc = mt0.BG.Γs(mt0.BG.get('βi', 0), τR, mt0.db['θ'].values[0], 0)
xCopy = mt0.BG.si_s(mt0.BG.get('βi', 0), τR, mt0.db['θ'].values[0], Γc, 0)[0]
check('LOG: the new-eps consistent shares at t0 differ from the inherited ones',
      maxAbs(xCopy, xBase) > 1e-4, '-> max|Δ| = {:.2e}'.format(maxAbs(xCopy, xBase)))

# ---- 2. the no-shock control: with the lags inherited, t0's reported c2i/c20/bbar reproduce the baseline.
# Only to the t0 tax's grid resolution, not to 1e-10: the baseline locates the root of z_t at shares
# consistent with each candidate, the copy at the baseline's realised shares -- one root in exact
# arithmetic, two linear interpolations on 𝒯 (9e-6 in τ here). The steady-state proxies EE_report used
# before put c20 5% off.
mc = m.createCopyFromt0(t0)
ctrl = mc.solvePEE_LOG(**seed)
dev = {k: abs(float(np.max(np.abs(np.asarray(ctrl['report'][k].xs(0)) / np.asarray(base['report'][k].xs(t0)) - 1))))
       for k in ('c2i', 'c20', 'bbar')}
dτ = abs(float(ctrl['τ'].iloc[0]) - float(base['τ'].xs(t0)))
check('LOG control (eps unchanged): the t0 tax, and c2i, c20, bbar relative, reproduce the baseline',
      dτ < 3e-5 and max(dev.values()) < 3e-4,
      '-> |Δτ| {:.1e}; '.format(dτ) + ', '.join('{} {:.1e}'.format(k, v) for k, v in dev.items()))

# ---- 3. CRRA on small grids: the same, with s_{t-1} a state and B_t^i in the shares --------------------
mC = model(NEAR_CRRA, ρ = 1.5)
mC.CRRA.initGS(CRRA_GRID)
baseC = mC.solvePEE_CRRA()
seedC = mC.stateAtT0(baseC['report'], t0, init = baseC['init'])
mt0C, shockC = reformCopy(mC, 'solvePEE_CRRA', seedC, t0)
lagChecks('CRRA', mC, mt0C, baseC, shockC, seedC, tPrev)

# ---- 4. the tax target: spending over GDP, GDP formal plus informal output ----------------------------
S, α, γ0, z0 = 0.071, 0.35, 0.47, 0.30
τ0, y = ModelInformalSavings.taxTarget(S, α, γ0, z0)
check('taxTarget: τ_0(1-α)(1-y) = spending and y = a(1-τ_0)/(1+a(1-τ_0))',
      abs(τ0*(1-α)*(1-y) - S) < 1e-15 and abs(y - γ0*z0*(1-α)*(1-τ0)/(1+γ0*z0*(1-α)*(1-τ0))) < 1e-15,
      '-> τ_0 = {:.6f}, y = {:.6f}'.format(τ0, y))
check('taxTarget without informal output is spending/(1-α)',
      ModelInformalSavings.taxTarget(S, α, 0.0, z0) == (S/(1-α), 0.0))
p = testmod.pars
check("test.py's τ0 is taxTarget on the workbook's spending, α, γ_0 and z_0^η",
      (p['τ0'], p['yInformal0']) == ModelInformalSavings.taxTarget(p['pensionSpending0'], p['α'], p['γj'][0],
                                                                    p['zηj'][0]),
      '-> τ0 = {:.6f}, y = {:.6f}'.format(p['τ0'], p['yInformal0']))

# On the solved path: with η_0/X_0 at the values eq:calibration:eta0/X0 imply at t0, the model's own
# informal share of GDP (base.outputInformal/outputFormal) is the closed form at the solved tax.
rep = base['report']
h, s_, τb = rep['h'].xs(t0), rep['s_'].xs(t0), float(base['τ'].xs(t0))
Θh = m.B.ΘhFromH(h, s_, t0)
η0 = float(m.B.calibrationη0(Θh, τb, t0))
mY = model(NEAR | {'η0': η0, 'X0': float(m.B.calibrationX0(η0, Θh, t0))})
Yf, Y0 = mY.B.outputFormal(s_, h, t0), mY.B.outputInformal(s_, t0)
a = mY.db['γ0'].xs(t0) * mY.db['zη0'].xs(t0) * (1-mY.db['α'].xs(t0))
yClosed = a*(1-τb)/(1+a*(1-τb))
check('on the solved path at the η_0/X_0 targets, Y0/(Y+Y0) is the closed-form y at the solved tax',
      abs(Y0/(Yf+Y0) - yClosed) < 1e-12, '-> model {:.10f}, closed form {:.10f}'.format(Y0/(Yf+Y0), yClosed))
check("EE_report's Y/Y0 are base.outputFormal/outputInformal on the path",
      abs(rep['Y'].xs(t0)/m.B.outputFormal(s_, h, t0) - 1) < 1e-14
      and abs(rep['Y0'].xs(t0)/m.B.outputInformal(s_, t0) - 1) < 1e-14)

# ---- 5. epsPre0 ---------------------------------------------------------------------------------------
m0 = model(NEAR, epsPre0 = True)
check('epsPre0: ε = 0 at every t, and κ = p (no informal pension in the budget)',
      np.all(m0.db['eps'].values == 0) and np.allclose(m0.db['κ'].values, m0.db['p'].values, rtol = 1e-14))
base0 = m0.solvePEE_LOG()
check('epsPre0: the baseline PEE solves, b^0 = 0 on its path, the t0 tax interior',
      np.all(base0['report']['b0'].values == 0) and 0.02 < float(base0['τ'].xs(t0)) < 0.98,
      '-> τ_t0 = {:.6f}'.format(float(base0['τ'].xs(t0))))
seed0 = m0.stateAtT0(base0['report'], t0, init = base0['init'])
mt00, shock0 = reformCopy(m0, 'solvePEE_LOG', seed0, t0)
ratio = shock0['report']['b0'].values/shock0['report']['bi'].loc[:, 1].values
check('epsPre0: the reform from zero solves with b^0 = b^1 on the reformed path, and raises the t0 tax',
      maxAbs(ratio, 1) < 1e-12 and float(shock0['τ'].iloc[0]) > float(base0['τ'].xs(t0)),
      '-> max|b0/b1-1| = {:.1e}, τ_t0 {:.6f} -> {:.6f}'.format(maxAbs(ratio, 1), float(base0['τ'].xs(t0)),
                                                               float(shock0['τ'].iloc[0])))
st = dict(m.__dict__)
st.pop('epsPre0', None)
mOld = ModelInformalSavings.__new__(ModelInformalSavings)
mOld.__setstate__(st)
check('epsPre0 survives a pickle; an instance pickled without it reads False',
      pickle.loads(pickle.dumps(m0)).epsPre0 is True and mOld.epsPre0 is False)
with tempfile.TemporaryDirectory() as d:
    with open(os.path.join(d, 'rho_1.0000.pkl'), 'wb') as f:
        pickle.dump(m, f)
    r = attempt(lambda: su.loadCalibrated(1.0, {}, pkldir = d, epsPre0 = True))
    check('shockUniversal.loadCalibrated refuses an instance of the other eps variant', isinstance(r, ValueError),
          '-> {!r}'.format(r)[:120])

# ---- 6. the formal-benefit readouts --------------------------------------------------------------------
f = su.frame(rep, m = m)
idx = rep['h'].index[1:]
avg = rep['h'].shift(1).loc[idx] * rep['bbar'].loc[idx]
check("frame's biAvg = Σ_i γ_{t-1,i} b_t^i equals h_{t-1}·bbar_t (eq:governmentBudget)",
      maxAbs(f['biAvg'].loc[idx]/avg, 1) < 1e-13, '-> max rel |Δ| = {:.1e}'.format(maxAbs(f['biAvg'].loc[idx]/avg, 1)))
check("frame carries b^i for every formal type", all('bi{}'.format(j) in f for j in m.db['i'])
      and maxAbs(f['bi1'], rep['bi'].loc[:, 1]) == 0)

report()
