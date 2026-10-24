r""" The stage (iii) builders of the cross-country test (tablesOECD26, figuresOECD26) and their readers
(datasets.oecd26*), on synthetic results/oecd26 csvs written to a temporary directory.

Run:  .venv\Scripts\python.exe python\paper\test_oecd26.py      (seconds; pytest collects the same test_ functions)

The synthetic model makes every relation exact, so its slopes are known: layer 1's spending is 10 + 4 (growth - 1)
+ 6 gini and its index 0.9 - 0.3 (growth - 1) on the design chosen (0.8 on the design in force); layer 2 matches
the data's spending. Reads data/oecdFigure1.csv and data/oecd26_sample.csv; writes only to the temporary directory.
"""
import os, sys, json, tempfile, shutil

import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as C
import datasets as D
import tablesOECD26 as T
import figuresOECD26 as F
import texTable as TT

TMP = tempfile.mkdtemp(prefix = 'oecd26paper_')
D.OECD26DIR = os.path.join(TMP, 'oecd26')
C.PAPERDIR = os.path.join(TMP, 'paper')
FIG = D.oecdFigure1Data()
SMP = D.oecd26Sample()
KEY = {'spec': C.US['esc']['spec'], 'phi': C.US['esc']['phi'], 'commonX': C.US['commonX']}
_SW = D.usSweep('US')
BETA = float(_SW.loc[np.isclose(_SW['ρ'], 1.0), 'β'].iloc[0])     # the U.S. calibration's, which the reader requires


def synthetic(turnout = 'cps', anchorKey = 'h000000000001', drop = (), lux = False, β = None, grid = 'fine'):
    """ anchor.csv and layer{1,2}.csv for `turnout` in D.OECD26DIR, every country but `drop`; `lux` writes
    Luxembourg as 'noTurnout'. """
    os.makedirs(D.OECD26DIR, exist_ok = True)
    β = BETA if β is None else β
    a = pd.DataFrame([KEY | {'turnout': turnout, 'iso3': 'USA', 'status': 'ok', 'β': β, 'ω': 1.23, 'p': 10.5,
                             'inputsKey': anchorKey, 'grid': grid}])
    g, gi = FIG['popGrowth'].astype(float), FIG['gini'].astype(float)
    idx = 0.9 - 0.3*(g - 1)
    rows = {1: [], 2: []}
    for c in FIG.index:
        if c in drop:
            continue
        base = KEY | {'turnout': turnout, 'iso3': c, 'country': FIG.at[c, 'country'],
                      'sample26': bool(SMP.at[c, 'sample26']), 'anchorKey': anchorKey, 'grid': grid,
                      'β': β, 'ωAnchor': 1.23, 'p': 10.5}
        for layer in (1, 2):
            if lux and c == 'LUX':
                rows[layer].append(base | {'status': 'noTurnout'})
                continue
            sp = 10 + 4*(g[c] - 1) + 6*gi[c] if layer == 1 else float(FIG.at[c, 'pensionSpending'])
            rows[layer].append(base | {'status': 'ok', 'ω': 1.23 if layer == 1 else 1 + 0.01*sp,
                                       'ν2020': g[c], 'Vtilde': 0.2, 'spendingData': FIG.at[c, 'pensionSpending'],
                                       'indexData': FIG.at[c, 'bbIndex'], 'θData': 0.5, 'spending2020': sp,
                                       'θChosen': 2 - 1/idx[c], 'θInForce': 2 - 1/(idx[c] - 0.1)})
    for name, df in (('anchor', a), ('layer1', pd.DataFrame(rows[1])), ('layer2', pd.DataFrame(rows[2]))):
        old = os.path.join(D.OECD26DIR, name + '.csv')
        if os.path.exists(old):
            prev = pd.read_csv(old, dtype = {'inputsKey': str, 'anchorKey': str})
            df = pd.concat([prev[prev['turnout'] != turnout], df], ignore_index = True)
        df.to_csv(old, index = False)


def _ols(x, y):
    b, a = np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)
    return b


def test_readers_and_sample():
    synthetic()
    m = D.oecd26Layer(1)
    assert len(m) == 29 and D.oecd26Anchor()['p'] == 10.5
    assert int(SMP['sample26'].sum()) == 26 and set(SMP.index[~SMP['sample26']]) == {'MEX', 'TUR', 'KOR'}
    p = T.panelData(1)
    assert len(p) == 26 and 'MEX' not in p.index and p.attrs['dropped'] == []
    assert np.allclose(p['indexModel'], 1/(2 - p['θModel']), atol = 1e-15)


def test_slopes_exact_and_data():
    synthetic()
    s = T.slopes().set_index(['y', 'x'])
    keep = SMP.index[SMP['sample26']]
    f = FIG.loc[keep]
    want = {('spending', 'growth'): _ols(f['popGrowth'], f['pensionSpending']),
            ('spending', 'gini'): _ols(f['gini'], f['pensionSpending']),
            ('spending', 'index'): _ols(f['bbIndex'], f['pensionSpending']),
            ('index', 'growth'): _ols(f['popGrowth'], f['bbIndex']),
            ('index', 'gini'): _ols(f['gini'], f['bbIndex'])}
    for k, b in want.items():
        assert abs(s.loc[k, 'data']['slope'] - b) < 1e-10, k
        assert s.loc[k, 'data']['n'] == 26
    assert abs(s.loc[('index', 'growth'), 'layer1']['slope'] + 0.3) < 1e-10      # exact by construction
    assert s.loc[('index', 'growth'), 'layer1']['se'] < 1e-10
    for k in (('spending', 'growth'), ('spending', 'gini')):
        assert s.loc[k, 'targeted2']
        assert abs(s.loc[k, 'layer2']['slope'] - s.loc[k, 'data']['slope']) < 1e-10
    s2 = T.slopes(reading = 'inForce').set_index(['y', 'x'])
    assert abs(s2.loc[('index', 'growth'), 'layer1']['slope'] + 0.3) < 1e-10      # the in-force index is shifted


def test_cses_drops_luxembourg_and_29():
    synthetic('cses', lux = True)
    p = T.panelData(1, turnout = 'cses')
    assert 'LUX' not in p.index and p.attrs['dropped'] == ['LUX'] and len(p) == 25
    assert T.slopes(turnout = 'cses').attrs['n'] == 25
    synthetic()
    assert len(T.panelData(2, sample = '29')) == 29


def test_stale_and_missing():
    synthetic()
    d = pd.read_csv(D.oecd26Path(1), dtype = {'inputsKey': str, 'anchorKey': str})
    d.loc[d['iso3'] == 'GBR', 'anchorKey'] = 'h0000000000ff'
    d.to_csv(D.oecd26Path(1), index = False)
    try:
        D.oecd26Layer(1)
        raise AssertionError('a row of another anchor was read')
    except ValueError as e:
        assert 'GBR' in str(e)
    synthetic(drop = ('ITA',))
    try:
        T.panelData(1)
        raise AssertionError('a missing sample country passed')
    except D.MissingInput as e:
        assert 'ITA' in str(e)
    synthetic(drop = ('MEX',))
    assert len(T.panelData(1)) == 26                     # outside the sample: not needed
    for kw in ({'β': BETA*(1 + 1e-6)}, {'grid': 'coarse'}):   # an anchor of an earlier U.S. calibration, a coarse run
        synthetic(**kw)
        try:
            D.oecd26Anchor()
            raise AssertionError('a stale anchor was read: {}'.format(kw))
        except ValueError as e:
            assert 'rerun python/US/runOECD26.py' in str(e)


def test_builders_write_and_convert():
    synthetic()
    for fn, name in ((T.oecd26Slopes, 'OECD26_Slopes'), (T.oecd26Omega, 'OECD26_Omega')):
        tex = fn()
        assert tex.startswith('%% GENERATED') and 'results/oecd26/' in tex.splitlines()[2]
        t = TT.parse(tex)
        t.html(TT.Context(strict = True))
        keys = [l.split('% row: ')[1] for l in tex.splitlines() if '% row: ' in l]
        assert len(keys) == len(set(keys)) and len(keys) == (5 if name == 'OECD26_Slopes' else 26), name
    paths = F.oecd26Figure(1)
    with open([q for q in paths if q.endswith('.marks.json')][0], encoding = 'utf-8') as f:
        marks = json.load(f)['marks']
    assert len(marks) == 5*(2*26 + 2)
    line = [m for m in marks if m['id'].endswith('index_growth--model--fit')][0]
    assert abs(line['value'] + 0.3) < 1e-10 and line['row'] == 'index_growth'
    assert len(json.load(open([q for q in F.oecd26Figure(2) if q.endswith('.marks.json')][0],
                              encoding = 'utf-8'))['marks']) == 2*(2*26 + 2)


if __name__ == '__main__':
    from gridsearch.testing import check, report
    for name, fn in [(k, v) for k, v in dict(globals()).items() if k.startswith('test_') and callable(v)]:
        try:
            fn()
            check(name, True)
        except Exception as e:
            check(name, False, '{}: {}'.format(type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors = True)
    report()
