r""" The stage (iii) builders of the cross-country test (tablesOECD26, figuresOECD26) and their readers
(datasets.oecd26*), on synthetic results/oecd26 csvs written to a temporary directory.

Run:  .venv\Scripts\python.exe python\paper\test_oecd26.py      (seconds; pytest collects the same test_ functions)

The synthetic model makes every relation exact, so its slopes are known: layer 1's spending is 10 + 4 (growth - 1)
+ 6 gini and its index 0.9 + b (growth - 1) on the design chosen (shifted by 0.1 on the design in force), b = -0.3
at the paper's variant and another value at each other (spec, betaRule); layer 2 matches the data's spending. The
variants share one set of csvs, as runOECD26.py writes them, so a reader that mixed them would read the wrong b.
The deep test's csvs (usCalibrationSummary, escCalibration{,Costs}, escCountry{,Costs}, escCornerSlope) are
synthetic too, for OECD26_Reconcile and US_ESC_Country. Reads data/oecdFigure1.csv and data/oecd26_sample.csv; writes
only to the temporary directory.
"""
import os, sys, json, tempfile, shutil

import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as C
import datasets as D
import tablesOECD26 as T
import figuresOECD26 as F
import tablesUS as TU
import texTable as TT

TMP = tempfile.mkdtemp(prefix = 'oecd26paper_')
D.OECD26DIR = os.path.join(TMP, 'oecd26')
C.PAPERDIR = os.path.join(TMP, 'paper')
C.ESCDIR = os.path.join(TMP, 'esc')
FIG = D.oecdFigure1Data()
SMP = D.oecd26Sample()
V = C.US['oecd26']
KEY = {'phi': C.US['esc']['phi'], 'commonX': C.US['commonX']}
_SW = D.usSweep('US')
BETA = float(_SW.loc[np.isclose(_SW['ρ'], 1.0), 'β'].iloc[0])     # the U.S. calibration's, which the reader requires
# (spec, betaRule) -> layer 1's index-on-growth slope; the paper's variant is -0.3
SLOPE = {(V['spec'], V['betaRule']): -0.3, ('size', 'common'): -0.2, ('size', 'commonR'): -0.1,
         ('sizePiR', 'commonR'): -0.05}
P = {'size': 10.5, 'sizePiR': 20.8, 'none': np.nan}


def synthetic(turnout = 'cps', anchorKey = 'h000000000001', drop = (), lux = False, β = None, grid = 'fine',
              spec = None, betaRule = None, legacy = False):
    """ anchor.csv and layer{1,2}.csv for `turnout`, `spec` and `betaRule` (config.US['oecd26']'s where None) in
    D.OECD26DIR, every country but `drop`, replacing the rows of the same turnout, spec and β rule (the anchor's
    always 'common'); `lux` writes Luxembourg as 'noTurnout'; `legacy` writes no betaRule column, as the csvs before
    it. Under 'none' the anchor has no cost parameter and no row a design. """
    os.makedirs(D.OECD26DIR, exist_ok = True)
    spec = V['spec'] if spec is None else spec
    betaRule = V['betaRule'] if betaRule is None else betaRule
    β = BETA if β is None else β
    key = KEY | {'spec': spec, 'betaRule': betaRule}
    g, gi = FIG['popGrowth'].astype(float), FIG['gini'].astype(float)
    idx = 0.9 + SLOPE.get((spec, betaRule), -0.3)*(g - 1)
    idxUS = 0.9 + SLOPE.get((spec, 'common'), -0.3)*(g['USA'] - 1)
    a = pd.DataFrame([key | {'betaRule': 'common', 'turnout': turnout, 'iso3': 'USA', 'status': 'ok', 'β': β,
                             'ω': 1.23, 'p': P[spec], 'inputsKey': anchorKey, 'grid': grid, 'θData': 0.5,
                             'ν2020': g['USA'], 'Vtilde': 0.2,
                             'θInForce': np.nan if spec == 'none' else 2 - 1/(idxUS - 0.1)}])
    rows = {1: [], 2: []}
    for c in FIG.index:
        if c in drop:
            continue
        base = key | {'turnout': turnout, 'iso3': c, 'country': FIG.at[c, 'country'],
                      'sample26': bool(SMP.at[c, 'sample26']), 'anchorKey': anchorKey, 'grid': grid,
                      'β': β, 'ωAnchor': 1.23, 'p': P[spec]}
        for layer in (1, 2):
            if lux and c == 'LUX':
                rows[layer].append(base | {'status': 'noTurnout'})
                continue
            sp = 10 + 4*(g[c] - 1) + 6*gi[c] if layer == 1 else float(FIG.at[c, 'pensionSpending'])
            design = ({'θChosen': np.nan, 'θInForce': np.nan} if spec == 'none' else
                      {'θChosen': 2 - 1/idx[c], 'θInForce': 2 - 1/(idx[c] - 0.1)})
            rows[layer].append(base | {'status': 'ok', 'ω': 1.23 if layer == 1 else 1 + 0.01*sp,
                                       'ν2020': g[c], 'Vtilde': 0.2, 'spendingData': FIG.at[c, 'pensionSpending'],
                                       'indexData': FIG.at[c, 'bbIndex'], 'θData': 0.5, 'spending2020': sp} | design)
    for name, df in (('anchor', a), ('layer1', pd.DataFrame(rows[1])), ('layer2', pd.DataFrame(rows[2]))):
        old = os.path.join(D.OECD26DIR, name + '.csv')
        rule = 'common' if name == 'anchor' else betaRule
        if legacy:
            df = df.drop(columns = 'betaRule')
        if os.path.exists(old):
            prev = pd.read_csv(old, dtype = {'inputsKey': str, 'anchorKey': str})
            prule = prev['betaRule'].fillna('common') if 'betaRule' in prev.columns else 'common'
            same = (prev['turnout'] == turnout) & (prev['spec'] == spec) & (prule == rule)
            df = pd.concat([prev[~same], df], ignore_index = True)
        df.to_csv(old, index = False)


def fresh():
    shutil.rmtree(D.OECD26DIR, ignore_errors = True)


def _ols(x, y):
    b, a = np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)
    return b


def test_readers_and_sample():
    synthetic()
    m = D.oecd26Layer(1)
    assert len(m) == 29 and D.oecd26Anchor()['p'] == P[V['spec']]
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
    d.loc[(d['iso3'] == 'GBR') & (d['spec'] == V['spec']), 'anchorKey'] = 'h0000000000ff'
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


def test_variants_select_and_never_mix():
    """ Both specs and both β rules in one set of csvs: each reader call returns its own variant's 29 rows and
    slope, the default call config.US['oecd26']'s, and the anchor of a spec is its 'common' row. """
    fresh()
    for spec, rule in SLOPE:
        synthetic(spec = spec, betaRule = rule)
    assert len(pd.read_csv(D.oecd26Path(1))) == 29*len(SLOPE) and len(pd.read_csv(D.oecd26Path(0))) == 2
    for (spec, rule), b in SLOPE.items():
        kw = {} if (spec, rule) == (V['spec'], V['betaRule']) else {'spec': spec, 'betaRule': rule}
        lay = D.oecd26Layer(1, **kw)
        assert len(lay) == 29 and set(lay['spec']) == {spec} and set(lay['betaRule']) == {rule}, (spec, rule)
        s = T.slopes(**kw).set_index(['y', 'x'])
        assert abs(s.loc[('index', 'growth'), 'layer1']['slope'] - b) < 1e-10, (spec, rule)
    assert D.oecd26Anchor()['p'] == P[V['spec']] and D.oecd26Anchor(spec = 'size')['p'] == P['size']
    assert D.oecd26Anchor(spec = 'sizePiR')['betaRule'] == 'common'


def test_legacy_rows_read_as_common():
    """ Rows written before the betaRule column (or blank in it) are 'common' rows; no 'commonR' row is made up. """
    fresh()
    synthetic(spec = 'size', betaRule = 'common', legacy = True)
    assert 'betaRule' not in pd.read_csv(D.oecd26Path(1)).columns
    assert len(D.oecd26Layer(1, spec = 'size', betaRule = 'common')) == 29
    try:
        T.panelData(1, spec = 'size', betaRule = 'commonR')
        raise AssertionError("a 'commonR' panel was read off legacy rows")
    except D.MissingInput:
        pass
    synthetic(spec = 'sizePiR', betaRule = 'common')                        # adds the column, blank on the old rows
    assert pd.read_csv(D.oecd26Path(1))['betaRule'].isna().sum() == 29
    s = T.slopes(spec = 'size', betaRule = 'common').set_index(['y', 'x'])
    assert abs(s.loc[('index', 'growth'), 'layer1']['slope'] - SLOPE[('size', 'common')]) < 1e-10
    assert len(D.oecd26Layer(1, spec = 'sizePiR', betaRule = 'common')) == 29


def test_none_anchor_without_cost():
    """ A 'none' anchor has no cost parameter (p NaN) and its layers no design; the reader takes it, and the
    spending panel is complete. """
    synthetic(spec = 'none', betaRule = 'common')
    a = D.oecd26Anchor(spec = 'none')
    assert np.isnan(float(a['p'])) and a['spec'] == 'none'
    p = T.panelData(1, spec = 'none')
    assert len(p) == 26 and np.isfinite(p['spendingModel']).all() and p['θModel'].isna().all()


def test_variant_suffix_and_caption():
    """ OECD26_Slopes at a non-default variant carries the variant in its name, label and caption. """
    synthetic(spec = 'size', betaRule = 'commonR')
    assert T.suffix() == '' and T.suffix(spec = 'size') == '_size'
    assert T.suffix(turnout = 'cses', spec = 'none', betaRule = 'commonR') == '_cses_none_commonR'
    assert T.variantCaption() == ''
    tex = T.oecd26Slopes(spec = 'size', betaRule = 'commonR')
    assert '--only OECD26_Slopes_size_commonR\n' in tex and r'\label{table:OECD26:slopes_size_commonR}' in tex
    assert T.SPECCAPTION['size'] in tex and T.BETACAPTION['commonR'] in tex
    assert r'$\beta$ and $\omega$ calibrated' in tex and r'$\lambda = 10.50$' in tex
    TT.parse(tex).html(TT.Context(strict = True))
    paths = F.oecd26Figure(1, spec = 'size', betaRule = 'commonR')
    assert any(os.path.basename(q).startswith('OECD26_Layer1_size_commonR.') for q in paths)


def test_builders_write_and_convert():
    synthetic()
    for fn, name in ((T.oecd26Slopes, 'OECD26_Slopes'), (T.oecd26Omega, 'OECD26_Omega')):
        tex = fn()
        assert tex.startswith('%% GENERATED') and 'results/oecd26/' in tex.splitlines()[2]
        assert '--only ' + name + '\n' in tex                  # the paper's variant: the registered name
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


def _table(tex):
    """ The body rows of a built table as {row key: [cells]}, after a strict HTML conversion. """
    t = TT.parse(tex)
    t.html(TT.Context(strict = True))
    rows = {}
    for line in tex.splitlines():
        if '% row: ' in line:
            body, key = line.split('% row: ')
            rows[key.strip()] = [c.strip() for c in body.rstrip().rstrip('\\').split(' & ')]
    return rows


def test_spending_slopes_exact_and_note():
    """ OECD26_Spending at spendingSpec ('none', no design on any row): the two spending slopes of layer 1 and of the
    data are the least-squares slopes of the synthetic numbers on the 26, the index relations are never asked for, and
    the figure's note carries both pairs as the table cells print them. """
    assert V['spendingSpec'] == 'none'
    fresh()
    synthetic(spec = 'none', betaRule = 'common')
    s = T.spendingSlopes().set_index(['y', 'x'])
    assert list(s.index) == list(T.SPENDING) and s['layer2'].isna().all()
    keep = SMP.index[SMP['sample26']]
    f = FIG.loc[keep]
    model = 10 + 4*(f['popGrowth'].astype(float) - 1) + 6*f['gini'].astype(float)
    for (y, x), col in ((('spending', 'growth'), 'popGrowth'), (('spending', 'gini'), 'gini')):
        assert abs(s.loc[(y, x), 'data']['slope'] - _ols(f[col], f['pensionSpending'])) < 1e-10
        assert abs(s.loc[(y, x), 'layer1']['slope'] - _ols(f[col], model)) < 1e-10
        assert s.loc[(y, x), 'layer1']['n'] == 26
    paths = F.oecd26Spending()
    note = open([q for q in paths if q.endswith('OECD26_Spending_note.tex')][0], encoding = 'utf-8').read()
    assert note.startswith('%% GENERATED') and '--only OECD26_Spending\n' in note
    for k in T.SPENDING:
        for side in ('data', 'layer1'):
            assert T._cell(s.loc[k, side]) in note, (k, side)
    assert r'\omega' not in note and 'countries' not in note           # the sample and anchor are section 6's
    marks = json.load(open([q for q in paths if q.endswith('.marks.json')][0], encoding = 'utf-8'))['marks']
    assert len(marks) == 2*(2*26 + 2)


def test_robustness_dashes_missing_and_stale():
    """ OECD26_Robustness: a variant with rows prints its slopes (index on growth, layer 1: the variant's b); a
    variant never run, and one whose rows were computed against another anchor, print `--`, never a value; the data
    row is on top of each turnout panel. """
    fresh()
    for spec, rule in (('size', 'common'), ('sizePiR', 'common'), ('size', 'commonR')):
        synthetic(spec = spec, betaRule = rule)
    synthetic('cses', lux = True, spec = 'sizePiR', betaRule = 'common')
    d = pd.read_csv(D.oecd26Path(1), dtype = {'inputsKey': str, 'anchorKey': str})
    stale = (d['spec'] == 'size') & (d['betaRule'] == 'commonR') & (d['iso3'] == 'GBR')
    d.loc[stale, 'anchorKey'] = 'h0000000000ff'
    d.to_csv(D.oecd26Path(1), index = False)
    tex = T.oecd26Robustness()
    assert '--only OECD26_Robustness\n' in tex and r'\label{table:OECD26:robustness}' in tex
    rows = _table(tex)
    assert list(rows)[:5] == ['cps_data', 'cps_size_common', 'cps_size_commonR', 'cps_sizePiR_common',
                              'cps_sizePiR_commonR']
    for key, b in (('cps_size_common', -0.2), ('cps_sizePiR_common', -0.3), ('cses_sizePiR_common', -0.3)):
        assert rows[key][1] == T._cell({'slope': b, 'se': 0.}), (key, rows[key][1])
    for key in ('cps_size_commonR', 'cps_sizePiR_commonR', 'cses_size_common', 'cses_size_commonR',
                'cses_sizePiR_commonR'):
        assert rows[key][1:] == ['--']*6, (key, rows[key])
    assert rows['cps_sizePiR_common'][0].endswith(r'$^{\ast}$')                  # the paper's variant only
    assert not rows['cses_sizePiR_common'][0].endswith(r'$^{\ast}$')
    keep = SMP.index[SMP['sample26']]
    f = FIG.loc[keep]
    assert rows['cps_data'][1] == r'\multicolumn{2}{c}{' + T._cell(T.ols(f['popGrowth'], f['bbIndex'])) + '}'
    assert 'Own turnout, 25 countries' in tex and 'Luxembourg, with no CSES election, left out' in tex
    assert r'$\varepsilon$, common $\beta$' in tex and r'\epsilon' not in tex   # ε, never the universal pension's ϵ


def _deepTest(costs = True, ratioUS = 11.345/20.445):
    """ Synthetic deep-test csvs in C.PAPERDIR and C.ESCDIR: the three calibrations, the U.S. cost under 'size' and
    'sizePiR' (θ* the U.S. θ; under 'sizePiR' its Π/R `ratioUS`, at which ε·Π/R is the U.S. λ), the UK and France
    under each (choices 0.69/0.795 and 0.67/0.74; the UK's own parameter 7.7 and 14.0, France none; under 'sizePiR'
    Π/R 0.529 and 0.432 on the U.S.-parameter rows), France's corner slope. `costs` False leaves the 'sizePiR' csvs
    out. """
    os.makedirs(C.PAPERDIR, exist_ok = True)
    os.makedirs(C.ESCDIR, exist_ok = True)
    for f in ('escCalibrationCosts.csv', 'escCountryCosts.csv'):
        if os.path.exists(os.path.join(C.ESCDIR, f)):
            os.remove(os.path.join(C.ESCDIR, f))
    pd.DataFrame([{'country': c, 'ρ': 1.0, 'commonX': True, 'θ': θ, 'ν2020': ν, 'ω': ω}
                  for c, θ, ν, ω in (('US', 0.7278, 1.34, 1.231), ('UK', 0.5597, 1.17, 1.103),
                                     ('FR', 1.0, 1.04, 1.446))]).to_csv(
        os.path.join(C.PAPERDIR, 'usCalibrationSummary.csv'), index = False)
    common = {'phi': 0.5, 'commonX': True}
    for spec, tag, p, ω, chosen, own in (('size', '', 11.345, 1.25, (0.69, 0.795), 7.7),
                                         ('sizePiR', 'Costs', 20.445, 1.28, (0.67, 0.74), 14.0)):
        if tag and not costs:
            continue
        ratio = lambda r: {'ΠR': r} if tag else {}                    # the 'size' csvs carry no ratio
        pd.DataFrame([common | {'spec': spec, 'p': p, 'converged': True, 'θStar': 0.7278, 'choice': 0.7278,
                                'β': 0.655, 'ω': ω, 'Vtilde': 0.436} | ratio(ratioUS)]).to_csv(
            os.path.join(C.ESCDIR, 'escCalibration' + tag + '.csv'), index = False)
        rows = []
        for c, θ, V, ch, r in (('UK', 0.5597, 0.223, chosen[0], 0.529), ('FR', 1.0, 0.218, chosen[1], 0.432),
                               ('UKUS', 0.5427, 0.065, 0.70, 0.527)):
            rows += [common | {'spec': spec, 'country': c, 'wedgeFrom': 'US', 'p': p, 'θStar': θ, 'choice': ch,
                               'ω': ω + 0.01, 'Vtilde': V} | ratio(r),
                     common | {'spec': spec, 'country': c, 'wedgeFrom': 'own', 'p': own if c != 'FR' else np.nan,
                               'θStar': θ, 'choice': θ, 'converged': c != 'FR', 'ω': ω, 'Vtilde': V}
                     | ratio(np.nan if c == 'FR' else r - 0.001)]
        pd.DataFrame(rows).to_csv(os.path.join(C.ESCDIR, 'escCountry' + tag + '.csv'), index = False)
    pd.DataFrame([common | {'spec': 'size', 'country': 'FR', 'λ': lam, 'vote': 1, 'slope': -0.1, 'τ1Corner': 0.2}
                  for lam in (0.0, 11.345)]).to_csv(os.path.join(C.ESCDIR, 'escCornerSlope.csv'), index = False)


def test_reconcile_both_specs():
    """ OECD26_Reconcile: the deep test's cells read the calibrations and the country test of each spec, the U.S.'s
    chosen design its θ*; the cross-section's the anchor (U.S.) and layer 2 of each spec at 'common', the chosen
    design of λ and ε each its own spec's (the synthetic b differs); a spec not on file is `--`. """
    fresh()
    for spec in ('none', 'size', 'sizePiR'):
        synthetic(spec = spec, betaRule = 'common')
    _deepTest()
    tex = T.oecd26Reconcile()
    assert '--only OECD26_Reconcile\n' in tex and r'\label{table:OECD26:reconcile}' in tex
    assert r'$\theta$ chosen, U.S.\ $\varepsilon$' in tex and r'\epsilon' not in tex
    assert r'the U.S.\ in section \ref{sec:oecd} and the UK and France in appendix \ref{app:US}' in tex
    rows = _table(tex)
    assert list(rows) == ['theta', 'vtilde', 'nu', 'omega_none', 'omega_size', 'chosen_size', 'omega_sizePiR',
                          'chosen_sizePiR']
    g = FIG['popGrowth'].astype(float)
    inForce = lambda spec, c: C.num(2 - 1/(0.9 + SLOPE[(spec, 'common')]*(g[c] - 1) - 0.1), 3)
    assert rows['theta'][1:] == ['0.728', '0.560', '1.000', '0.500', '0.500', '0.500']
    assert rows['nu'][1:4] == ['1.34', '1.17', '1.04'] and rows['nu'][5] == C.num(g['GBR'], 2)
    assert rows['vtilde'][1:4] == ['0.436', '0.223', '0.218']
    assert rows['omega_none'][1:4] == ['1.231', '1.103', '1.446'] and rows['omega_none'][4] == '1.230'
    assert rows['chosen_size'][1:4] == ['0.728', '0.690', '0.795']
    assert rows['chosen_sizePiR'][1:4] == ['0.728', '0.670', '0.740']
    for spec in ('size', 'sizePiR'):
        assert rows['chosen_' + spec][4:] == [inForce(spec, c) for c in ('USA', 'GBR', 'FRA')], spec
    assert inForce('size', 'GBR') != inForce('sizePiR', 'GBR')
    _deepTest(costs = False)
    shutil.rmtree(D.OECD26DIR)
    synthetic(spec = 'size', betaRule = 'common')
    rows = _table(T.oecd26Reconcile())
    assert rows['chosen_sizePiR'][1:] == ['--']*6 and rows['omega_none'][4:] == ['--']*3
    assert rows['chosen_size'][2:4] == ['0.690', '0.795'] and rows['theta'][4:] == ['0.500']*3


def test_country_table_both_transports():
    """ US_ESC_Country: the UK and France (not the UK at U.S. income groups), each with its Π/R under the U.S. ε and
    the design chosen and its own parameter under the U.S. λ and ε; France's own `--` under both, its corner sentence
    once; the note's U.S. ratio, at which ε and λ must be one cost (a ratio that breaks it raises). """
    _deepTest()
    tex = TU.escCountryTable()
    rows = _table(tex)
    assert list(rows) == ['gbr', 'fra']
    assert rows['gbr'][1:] == ['0.560', '0.223', '0.529', '0.690', '7.70', '0.670', '14.00']
    assert rows['fra'][1:] == ['1.000', '0.218', '0.432', '0.795', '--', '0.740', '--']
    assert tex.count('Bismarckian corner') == 1 and r'$\varepsilon = 20.45$' in tex and r'$\lambda = 11.35$' in tex
    assert r'\epsilon' not in tex and r'$\lambda_{n,t} = \varepsilon\,\Pi_{n,t}/R_{n,t}$' in tex
    assert r'the U.S.\ ratio is $0.555$, at which the U.S.\ $\varepsilon$ and $\lambda$ are the same cost' in tex
    assert _table(TU.escCountryTable(specs = ('size',)))['gbr'][1:] == ['0.560', '0.223', '0.690', '7.70']
    _deepTest(ratioUS = 0.6)
    try:
        TU.escCountryTable()
        raise AssertionError('a U.S. ratio at which ε·Π/R is not λ must raise')
    except ValueError:
        pass
    _deepTest()


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
