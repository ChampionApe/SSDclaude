r""" The US counterfactuals of runShocksUS.py (the design, ageing and France's characteristics, the design
given) at other Frisch elasticities: log preferences (rho = 1), the common-X calibration, the US and France
recalibrated at each xi.

Run:  .venv\Scripts\python.exe python\US\runShocksXi.py                 # xi = 0.3 (the check), then 0.2, 0.4
      ... --xi 0.2 0.4                                                   # without the check

xi is the workbook's 'Labor supply elasticity' (0.3), replaced in the parameters both models are built from;
the workbooks are never written. It has to reach the constructors: eta_i and X_i are derived from db['xi'] there
(Eq calibration:etaCommonX), so writing db['xi'] on a built model would leave them at the workbook xi. Per xi:

  1. the US calibrated as stage (i) does at rho = 1 (beta, omega against R and tau; X against the workweek), seeded
     from the published sweep row;
  2. France calibrated against THIS US model -- ModelFR imposes the US beta and targets hours relative to the US
     hbar, so its reference (modelFR.USReference) is built from step 1 rather than read off the published sweep,
     which holds the workbook-xi US;
  3. every scenario of runShocksUS.FAMILIES, both readings, and France's own path (runShocksUS's row schema).

With the workbook xi first in --xi, its rows are checked against results/shocks/US_shocksCommonX.csv at rho = 1
(CHECK_TOL) and a mismatch stops the run before any other xi: rows from a code path that does not reproduce
the published ones are not comparable with them.

Writes results/shocks/US_shocksXiCommonX.csv: runShocksUS.py's columns plus 'ξ', one block per xi.
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
from policy import multiplicityColumns
from model import ModelUS
from modelFR import ModelFR, USReference
from runShocksUS import FAMILIES, hostRow, effectRows

OUT = os.path.join(REPO, 'results', 'shocks', 'US_shocksXiCommonX.csv')
XI0 = float(testmod.pars['ξ'])        # the workbook's value
CHECK_TOL = 1e-7                      # tau and s/Y as fractions, the workweek in hours
GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}


def _assertXi(m, ξ, who):
    if not np.allclose(m.db['ξ'].values.astype(float), ξ, rtol = 0, atol = 0):
        raise RuntimeError(f'{who}: db[ξ] is not {ξ} at every date.')


def usModel(ξ):
    """ The US at xi, calibrated (common X, LOG), seeded from the published rho = 1 sweep row. """
    row = hostRow(1.0, True, 'US')
    m = ModelUS(pars = testmod.pars | {'ρ': 1.0, 'ξ': float(ξ), 'β': float(row['β']), 'ω': float(row['ω'])},
                commonX = True, **testmod.kwargs)
    m.db['dates'] = testmod.dates
    m.LOG.initGS(GS)
    _assertXi(m, ξ, 'usModel')
    m.calibrate(preferences = 'LOG')
    return m


def usReferenceOf(m):
    """ modelFR.USReference at rho = 1 from the calibrated US model m: its beta and its hbar in 2020 (the
    sweep's 'hbar' column, Model.calibration_report), and the US workbook's h0. """
    t0 = m.db['t'][m.db['t0']]
    out = m.solvePEE_LOG()
    hbar = float(m.B.avgHours(out['report']['h'].xs(t0), t0))
    return USReference({1.0: {'β': float(m.simpleβinv()), 'hbar': hbar}}, testmod.pars['h0'])


def franceModel(ξ, ref):
    """ France (its own groups, the US percentiles) at xi, calibrated against the reference `ref`. """
    pars, kwargs, dates, workweek = testEU.load('FR')
    mFR = ModelFR(pars = pars | {'ρ': 1.0, 'ω': 2.0, 'ξ': float(ξ)}, commonX = True, usRef = ref, **kwargs)
    mFR.db['dates'], mFR.db['workweek'], mFR.db['country'] = dates, workweek, 'FR'
    mFR.LOG.initGS(GS)
    _assertXi(mFR, ξ, 'franceModel')
    mFR.calibrate(preferences = 'LOG')
    return mFR


def frenchData(m, mFR):
    """ runShocksUS.frenchData on a France already calibrated at the host's xi. """
    t0FR, t0 = mFR.db['t'][mFR.db['t0']], m.db['t'][m.db['t0']]
    XbarFR = float((mFR.db['γi'].xs(t0FR).values.astype(float) * mFR.db['Xi'].xs(t0FR).values.astype(float)).sum())
    XbarUS = float((m.db['γi'].xs(t0).values.astype(float) * m.db['Xi'].xs(t0).values.astype(float)).sum())
    ηFR = mFR.db['ηi'].xs(t0FR).values.astype(float)
    parsFR = testEU.load('FR')[0]
    return {'ηFR': ηFR, 'μFR': parsFR['μj'], 'ηScale': sh.ηLevel(m, ηFR), 'xbarRatio': XbarFR/XbarUS,
            'XbarFR': XbarFR, 'XbarUS': XbarUS, 'θUS': float(m.db['θ'].xs(t0)), 'pinTheta': True}


def runXi(ξ, workweek):
    tic = time.time()
    m = usModel(ξ)
    t0 = m.db['t'][m.db['t0']]
    base = m.solvePEE_LOG()
    hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
    b = sh.readout(m, base['τ'], base['report'], workweek, hbarRef, pos = m.db['t0'])
    Xbar = float((m.db['γi'].xs(t0).values.astype(float) * m.db['Xi'].xs(t0).values.astype(float)).sum())
    print('\nξ={:<4} US calibrated: β={:.6f} ω={:.6f} X={:.6f}; baseline tau={:.4f} s/Y={:.4f} ww={:.2f}  ({:.0f}s)'
          .format(ξ, float(m.simpleβinv()), float(m.db['ω'].xs(t0)), Xbar, b['τ'], b['srOverY'], b['workweek'],
                  time.time()-tic))
    rows = [{'ξ': ξ, 'ρ': 1.0, 'preferences': 'LOG', 'family': 'baseline', 'scenario': 'Baseline',
             'effect': 'baseline', **b} | multiplicityColumns(base.get('multiplicity'))]
    mFR = franceModel(ξ, usReferenceOf(m))
    data = frenchData(m, mFR)
    print('  France at ξ={}: ω={:.6f}, Xbar_FR/Xbar_US={:.4f}'.format(ξ, float(mFR.db['ω'].xs(mFR.db['t'][mFR.db['t0']])),
                                                                     data['xbarRatio']))
    famOf = {n: f for f, ns in FAMILIES.items() for n in ns}
    for name in sum((list(ns) for ns in FAMILIES.values()), []):
        tic = time.time()
        r = sh.runOne(m, base, name, data, 'LOG', workweek, hbarRef)
        rows += effectRows(r, {'ξ': ξ, 'ρ': 1.0, 'preferences': 'LOG', 'family': famOf[name],
                               'scenario': r['label']})
        print('  {:<14} full: tau={:.4f} ww={:.2f}   EE-only: tau={:.4f} ww={:.2f}   {:.0f}s'.format(
            name, r['full']['τ'], r['full']['workweek'], r['ee']['τ'], r['ee']['workweek'], time.time()-tic))
    out = mFR.solvePEE_LOG()
    f = sh.readout(mFR, out['τ'], out['report'], workweek, hbarRef, pos = mFR.db['t0'])
    tFR = mFR.db['t'][mFR.db['t0']]
    rows.append({'ξ': ξ, 'ρ': 1.0, 'preferences': 'LOG', 'family': 'french', 'scenario': 'France (own calibration)',
                 'effect': 'full', **f, 'θ': float(mFR.db['θ'].xs(tFR)), 'ω': float(mFR.db['ω'].xs(tFR))}
                | multiplicityColumns(out.get('multiplicity')))
    return pd.DataFrame(rows)


def check(df):
    """ The workbook-xi rows against the published common-X shocks at rho = 1. """
    pub = pd.read_csv(os.path.join(REPO, 'results', 'shocks', 'US_shocksCommonX.csv'))
    pub = pub[np.isclose(pub['ρ'], 1.0)]
    worst = 0.
    for _, r in df.iterrows():
        hit = pub[(pub['scenario'] == r['scenario']) & (pub['effect'] == r['effect'])]
        if len(hit) != 1:
            raise RuntimeError(f"check: {len(hit)} published rows for ({r['scenario']}, {r['effect']})")
        for c in ('τ', 'srOverY', 'workweek'):
            worst = max(worst, abs(float(hit[c].iloc[0]) - float(r[c])))
    if worst > CHECK_TOL:
        raise RuntimeError(f'check: the workbook-ξ rows differ from US_shocksCommonX.csv by {worst:.2e}')
    print(f'  check against US_shocksCommonX.csv at ρ = 1: max |gap| {worst:.1e} (tol {CHECK_TOL:.0e})')


def main():
    p = argparse.ArgumentParser(description = 'US counterfactuals at other Frisch elasticities (LOG, common X).')
    p.add_argument('--xi', type = float, nargs = '*', default = [XI0, 0.2, 0.4])
    p.add_argument('--out', default = OUT)
    a = p.parse_args()
    workweek = float(testmod.workweek)
    have = pd.read_csv(a.out) if os.path.exists(a.out) else pd.DataFrame()
    for ξ in a.xi:
        df = runXi(ξ, workweek)
        if np.isclose(ξ, XI0):
            check(df)
        if len(have):
            have = have[~np.isclose(have['ξ'].astype(float), ξ)]
        have = pd.concat([have, df], ignore_index = True)
        have.to_csv(a.out, index = False)
    print('\n-> {}'.format(os.path.relpath(a.out, REPO)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
