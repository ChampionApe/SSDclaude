r""" Run the US counterfactuals at one or more rho and write the three paper tables' worth of numbers.

Run:  .venv\Scripts\python.exe python\US\runShocksUS.py                      # rho = 0.5, 1, 2
      ... --rho 1                                the LOG case alone
      ... --family theta                         one family (theta | ageing | french | all)
      ... --commonX                              the common-X calibration variant

Three families. Each scenario is a NEW EQUILIBRIUM PATH -- the shocked parameters hold over the whole
1960-2200 horizon and the economy starts at its own steady state, not the US's -- read at 2020, and
reported as a full effect (tau re-optimised) and an economic-equilibrium-only effect (tau held at the
baseline path):

    theta    theta = 0 and theta = 1                              -> writing/Paper/Tables/US_PensChars.tex
    ageing   mild (nu -> (1+nu)/2) and acute (nu -> 1), throughout -> US_Ageing.tex
    french   France's income distribution, leisure preferences, voting, and all three at once
                                                                  -> US_OtherShocks.tex

Plus a FRANCE reference row (--noFrance to skip): France's own calibrated path, read at its own 2020 with
the US workweek reference, so the French-characteristics rows can be read against the country they are
borrowed from. That row is the point of the new-path convention -- an unanticipated 2020 reform is not
commensurable with a country's own equilibrium path, a counterfactual country that has always had these
characteristics is. Note the France row's WORKWEEK is a calibration target (ModelFR targets hours
relative to the US), not a prediction; only its tau and savings rate are results.

See shocks.py for what each shock does and for the reporting conventions (savings rate is s/(w*h), the
workweek is expressed relative to the US baseline, and everything is read at db['t0']). The French
characteristics are read from data/FRMain.xlsx via testEU.py -- France's income groups are cut at US
percentiles precisely so that these swaps are well defined.

The calibration at each rho comes from the US sweep csv (results/calibration/US_rhoGrid{,CommonX}.csv),
so this script never re-runs the outer root: it installs (beta, omega) and solves. That also means every
rho asked for must already be in the sweep.

Writes results/shocks/US_shocks{,CommonX}.csv -- one row per (rho, family, scenario, effect).
"""
import os, sys, argparse, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)

import test as testmod
import testEU
import shocks as sh
from model import ModelUS

OUTDIR = os.path.join(REPO, 'results', 'shocks')

FAMILIES = {'theta': ('theta0', 'theta1'), 'ageing': ('mild', 'acute'),
            'french': ('frIncome', 'frLeisure', 'frVoting', 'frAll')}


def usRow(ρ, commonX):
    """ The US sweep's calibrated row at this rho. """
    csv = os.path.join(REPO, 'results', 'calibration',
                       'US_rhoGridCommonX.csv' if commonX else 'US_rhoGrid.csv')
    df = pd.read_csv(csv)
    hit = df.loc[(df['ρ'] - ρ).abs() < 1e-9]
    if hit.empty:
        raise KeyError(f'No US calibration at ρ={ρ} in {csv}. Run calibrateRhoGrid.py there first.')
    return hit.iloc[-1]


def frenchData(m, ρ, preferences, gs = None, commonX = False):
    """ France's characteristics, in the form the shocks want, plus the US quantities they are relative to.

    zetaFR and muFR are data and do not depend on rho. xbarRatio does: France's X_i carry the calibrated
    hours-unit level lambda, which moves across rho (0.8835 -> 0.9020 over the sweep), so France is
    calibrated at the SAME rho -- and the SAME calibration variant -- as the US model being shocked,
    rather than once at rho = 1 under vector X.

    zetaFR is France's relative income on ITS OWN groups -- which are the US percentiles, so gamma matches
    the US vector type by type and the swap is a like-for-like replacement. xbarRatio is the ratio of
    population-weighted mean X_i, France's calibrated value over the US's: the row the paper's calibration
    table reports as `X`, and the only thing a pure scale can be matched on.
    """
    parsFR, kwargsFR, _, _ = testEU.load('FR')
    # commonX must match the US model being shocked. Under commonX, France's X_i is a single scalar and
    # its eta_i inverts z^eta directly, so both characteristics differ from the vector-X calibration --
    # taking them from the wrong variant would impose a France that does not exist in this run's units.
    mFR = testEU.model('FR', ρ = float(ρ), commonX = commonX)
    if gs:
        getattr(mFR, preferences).initGS(gs)
    mFR.calibrate(preferences = preferences)
    t0FR = mFR.db['t'][mFR.db['t0']]
    γFR = mFR.db['γi'].xs(t0FR).values.astype(float)
    XbarFR = float((γFR * mFR.db['Xi'].xs(t0FR).values.astype(float)).sum())

    t0 = m.db['t'][m.db['t0']]
    γUS = m.db['γi'].xs(t0).values.astype(float)
    XbarUS = float((γUS * m.db['Xi'].xs(t0).values.astype(float)).sum())
    # gamma is not bit-identical across the two workbooks -- the same nominal percentile cuts land on
    # slightly different shares in CPS and LIS -- so this reports the gap rather than asserting equality.
    return {'ηFR': mFR.db['ηi'].xs(t0FR).values.astype(float), 'μFR': parsFR['μj'],
            'xbarRatio': XbarFR/XbarUS, 'XbarFR': XbarFR, 'XbarUS': XbarUS,
            'γgap': float(np.max(np.abs(γFR - γUS))),
            'θUS': float(m.db['θ'].xs(t0))}


def franceReference(ρ, preferences, gs = None, commonX = False, workweekData = None, hbarRef = None):
    """ France's own calibrated equilibrium at 2020, in the same three columns the US rows carry.

    The endpoint of the "mostly US, partly France" scale: US_OtherShocks reads its French-characteristics
    rows against this. It is NOT a shock on the US model -- France has its own eta, X, mu, nu AND its own
    calibrated omega (ModelFR imposes the US beta and searches omega alone), so the gap between the
    all-characteristics row and this one is exactly what the observable characteristics fail to explain.

    hbarRef is the US baseline's hbar and workweekData the US workbook's own workweek, so the reported
    number is France's hours on the US scale. That is the comparable object under vector X, where the
    LEVEL of hbar is not identified -- and it is also ModelFR's own hours target, so this cell reproduces
    France's observed workweek by construction rather than predicting it. Say so wherever it is printed.
    """
    mFR = testEU.model('FR', ρ = float(ρ), commonX = commonX)
    if gs:
        getattr(mFR, preferences).initGS(gs)
    mFR.calibrate(preferences = preferences)
    out = getattr(mFR, f'solvePEE_{preferences}')()
    r = sh.readout(mFR, out['τ'], out['report'], workweekData, hbarRef, pos = mFR.db['t0'])
    r['θ'] = float(mFR.db['θ'].xs(mFR.db['t'][mFR.db['t0']]))
    r['ω'] = float(mFR.db['ω'].xs(mFR.db['t'][mFR.db['t0']]))
    return r


def main():
    p = argparse.ArgumentParser(description = 'US counterfactuals: theta, ageing, French characteristics.')
    p.add_argument('--rho', type = float, nargs = '*', default = [0.5, 1.0, 2.0])
    p.add_argument('--family', default = 'all', choices = ('all', 'theta', 'ageing', 'french'))
    p.add_argument('--commonX', action = 'store_true')
    p.add_argument('--n', type = int, default = 101)
    p.add_argument('--ns', type = int, default = 150)
    p.add_argument('--smoothKnots', type = int, default = 4)
    p.add_argument('--interpKind', default = 'linear')
    p.add_argument('--pinTheta', action = 'store_true',
                   help = "hold theta at the US value in the income-distribution counterfactual instead "
                          "of re-deriving it from RR0 (which is what reproduces the paper). See "
                          "shocks.shockIncomeDistribution.")
    p.add_argument('--noFrance', action = 'store_true',
                   help = "skip France's own calibrated path, the reference row the French-characteristics "
                          'counterfactuals are read against. See franceReference.')
    p.add_argument('--out', default = None)
    a = p.parse_args()

    names = sum((list(FAMILIES[f]) for f in (FAMILIES if a.family == 'all' else [a.family])), [])
    famOf = {n: f for f, ns in FAMILIES.items() for n in ns}
    out = a.out or os.path.join(OUTDIR, 'US_shocks' + ('CommonX' if a.commonX else '') + '.csv')
    os.makedirs(OUTDIR, exist_ok = True)

    workweek = float(testmod.workweek)
    rows = []
    print('scenarios: {}'.format(', '.join(names)))
    print('workweek (data, {}): {:.5f}'.format(testmod.dfc['Calibration year'], workweek))

    for ρ in a.rho:
        row = usRow(ρ, a.commonX)
        preferences = 'LOG' if ρ == 1 else 'CRRA'
        m = ModelUS(pars = testmod.pars | {'ρ': float(ρ), 'β': float(row['β']), 'ω': float(row['ω'])},
                    commonX = a.commonX, **testmod.kwargs)
        m.db['dates'] = testmod.dates
        wp = {'smoothKnots': a.smoothKnots or None, 'interpKind': a.interpKind}
        getattr(m, preferences).initGS(({'n': a.n, 'ns': a.ns} if preferences == 'CRRA'
                                        else {'n': a.n}) | wp)
        if a.commonX:
            m.initProductivity_commonX(X = float(row['X']))
            m.updateAuxPars()

        t0 = m.db['t'][m.db['t0']]
        tic = time.time()
        base = m.solvePEE_LOG() if preferences == 'LOG' else m.solvePEE_CRRA()
        hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
        b = sh.readout(m, base['τ'], base['report'], workweek, hbarRef, pos = m.db['t0'])
        print('\nrho={:<4} {:<4} baseline: tau={:.4f}  sr={:.4f}  workweek={:.2f}  theta={:.4f}'
              '   ({:.0f}s to solve)'.format(ρ, preferences, b['τ'], b['sr'], b['workweek'],
                                             float(m.db['θ'].xs(t0)), time.time()-tic))
        # The calibration is a fixed point of these numbers, so they are also a check on the reinstall:
        # tau must equal the target and the workweek must be the data value by construction of hbarRef.
        rows.append({'ρ': ρ, 'preferences': preferences, 'family': 'baseline', 'scenario': 'Baseline',
                     'effect': 'baseline', **b})

        gsFR = ({'n': a.n, 'ns': a.ns} if preferences == 'CRRA' else {'n': a.n}) | wp
        data = (frenchData(m, ρ, preferences, gsFR, a.commonX)
                if any(famOf[n] == 'french' for n in names) else {})
        if data:
            data['pinTheta'] = a.pinTheta
        if data:
            print('  French: Xbar_FR/Xbar_US={:.4f} ({:.2f} vs {:.2f}), max|gamma_FR-gamma_US|={:.1e}'
                  .format(data['xbarRatio'], data['XbarFR'], data['XbarUS'], data['γgap']))

        for name in names:
            tic = time.time()
            r = sh.runOne(m, base, name, data, preferences, workweek, hbarRef)
            for eff in ('full', 'ee'):
                rows.append({'ρ': ρ, 'preferences': preferences, 'family': famOf[name],
                             'scenario': r['label'], 'effect': eff, **r[eff]})
            print('  {:<22} full: tau={:.4f} sr={:.4f} ww={:.2f}   |   EE-only: tau={:.4f} sr={:.4f} '
                  'ww={:.2f}   {:.0f}s'.format(
                      name, r['full']['τ'], r['full']['sr'], r['full']['workweek'],
                      r['ee']['τ'], r['ee']['sr'], r['ee']['workweek'], time.time()-tic))
            pd.DataFrame(rows).to_csv(out, index = False)

        if not a.noFrance:
            tic = time.time()
            try:
                f = franceReference(ρ, preferences, gsFR, a.commonX, workweek, hbarRef)
                rows.append({'ρ': ρ, 'preferences': preferences, 'family': 'french',
                             'scenario': 'France (own calibration)', 'effect': 'full', **f})
                print('  {:<22} full: tau={:.4f} sr={:.4f} ww={:.2f}   |   theta={:.4f} omega={:.4f}'
                      '   {:.0f}s'.format('France', f['τ'], f['sr'], f['workweek'], f['θ'], f['ω'],
                                          time.time()-tic))
            except Exception as e:
                print(f'  France reference FAILED {type(e).__name__}: {e}')
            pd.DataFrame(rows).to_csv(out, index = False)

    pd.DataFrame(rows).to_csv(out, index = False)
    print('\n-> {}'.format(os.path.relpath(out, REPO)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
