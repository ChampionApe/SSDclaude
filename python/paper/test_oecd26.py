r""" The stage (iii) builders of the cross-country test (tablesOECD26, figuresOECD26) and their readers
(datasets.oecd26*), on synthetic results/oecd26 csvs written to a temporary directory.

Run:  .venv\Scripts\python.exe python\paper\test_oecd26.py      (seconds; pytest collects the same test_ functions)

The synthetic model makes every relation exact, so its slopes are known: layer 1's spending is 10 + 4 (growth - 1)
+ 6 gini and its index 0.9 + b (growth - 1) on the design chosen (shifted by 0.1 on the design in force), b = -0.3
at the paper's variant and another value at each other (spec, betaRule) and each other measure of the design
(thetaSource); layer 2 matches the data's spending. The variants share one set of csvs, as runOECD26.py writes them,
so a reader that mixed them would read the wrong b. The data side is config.US['theta']'s measure of
data/oecd26_theta.csv (its in-sample countries, I = 1/(2 - θ), its spending), or figure 1.1's index on the paper's
26 for the measure 'paper'. The deep test's csv (escCountry, escCornerSlope) is synthetic too, for US_ESC_Country.
Reads data/oecdFigure1.csv, data/oecd26_sample.csv and data/oecd26_theta.csv; writes only to the temporary directory.
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
C.RESULTS = TMP                                               # the robustness variants' results/oecd26_theta_<V>/
FIG = D.oecdFigure1Data()
SMP = D.oecd26Sample()
V = C.US['oecd26']
THETA = C.US['theta']
TV = D.thetaVariant()
SAMPLE = D.oecd26SampleOf()
KEY = {'phi': C.US['esc']['phi'], 'commonX': C.US['commonX']}
BETA = 0.651382                                               # the synthetic U.S. calibration's, which the reader requires
_SW = pd.DataFrame([{'ρ': 1.0, 'β': BETA, 'residual': 1e-12, 'thetaSource': THETA, 'θ0': C.theta0()}])
D.usSweep = lambda country, commonX = None: _SW
# (spec, betaRule) -> layer 1's index-on-growth slope; the paper's variant is -0.3
SLOPE = {(V['spec'], V['betaRule']): -0.3, ('size', 'common'): -0.2, ('size', 'commonR'): -0.1,
         ('sizePiR', 'commonR'): -0.05}
# another measure of the design -> its slope at the paper's variant
SLOPETHETA = {'index': -0.4, 'A': -0.25, 'B': -0.35}
P = {'size': 10.5, 'sizePiR': 20.8, 'none': np.nan}


def _slope(spec, betaRule, theta):
    return SLOPETHETA[theta] if theta != THETA and theta in SLOPETHETA else SLOPE.get((spec, betaRule), -0.3)


def synthetic(turnout = 'cps', anchorKey = 'h000000000001', drop = (), lux = False, β = None, grid = 'fine',
              spec = None, betaRule = None, legacy = False, theta = None):
    """ anchor.csv and layer{1,2}.csv for `turnout`, `spec`, `betaRule` (config.US['oecd26']'s where None) and the
    measure `theta` (config.US['theta'] by default; 'index' for figure 1.1's index) in datasets.oecd26Dir(theta),
    every country but `drop`, replacing the rows of the same turnout, spec, β rule (the anchor's always 'common') and
    thetaSource; a robustness measure also gets its U.S. sweep (oecd26_theta_<V>/calibration/). `lux` writes
    Luxembourg as 'noTurnout'; `legacy` writes no betaRule column, as the csvs before it. Under 'none' the anchor has
    no cost parameter and no row a design. """
    theta = THETA if theta is None else theta
    root = D.oecd26Dir(theta)
    os.makedirs(root, exist_ok = True)
    spec = V['spec'] if spec is None else spec
    betaRule = V['betaRule'] if betaRule is None else betaRule
    β = BETA if β is None else β
    if theta not in (THETA, 'index'):
        os.makedirs(os.path.join(root, 'calibration'), exist_ok = True)
        pd.DataFrame([{'ρ': 1.0, 'β': BETA, 'residual': 1e-12, 'thetaSource': theta, 'θ0': C.theta0('US', theta)}]) \
            .to_csv(os.path.join(root, 'calibration', 'US_rhoGridCommonX.csv'), index = False)
    key = KEY | {'spec': spec, 'betaRule': betaRule, 'thetaSource': theta}
    g, gi = FIG['popGrowth'].astype(float), FIG['gini'].astype(float)
    b = _slope(spec, betaRule, theta)
    idx = 0.9 + b*(g - 1)
    idxUS = 0.9 + _slope(spec, 'common', theta)*(g['USA'] - 1)
    index = FIG['bbIndex'] if theta == 'index' else D.thetaVariant(theta)['index'].reindex(FIG.index)
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
                                       'indexData': index[c], 'θData': 0.5, 'spending2020': sp} | design)
    for name, df in (('anchor', a), ('layer1', pd.DataFrame(rows[1])), ('layer2', pd.DataFrame(rows[2]))):
        old = os.path.join(root, name + '.csv')
        rule = 'common' if name == 'anchor' else betaRule
        if legacy:
            df = df.drop(columns = 'betaRule')
        if os.path.exists(old):
            prev = pd.read_csv(old, dtype = {'inputsKey': str, 'anchorKey': str})
            prule = prev['betaRule'].fillna('common') if 'betaRule' in prev.columns else 'common'
            same = ((prev['turnout'] == turnout) & (prev['spec'] == spec) & (prule == rule)
                    & (prev['thetaSource'] == theta))
            df = pd.concat([prev[~same], df], ignore_index = True)
        df.to_csv(old, index = False)


def fresh():
    shutil.rmtree(D.OECD26DIR, ignore_errors = True)
    for v in C.US['oecd26']['thetaVariants']:
        shutil.rmtree(D.oecd26Dir(v), ignore_errors = True)


def _ols(x, y):
    b, a = np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)
    return b


def _raises(f, exc):
    try:
        f()
    except exc as e:
        return str(e) or type(e).__name__
    return False


def test_readers_and_sample():
    """ The reader keeps the main measure's rows; the panel is that measure's in-sample countries (21 under C: the
    26 without AUS, DNK, ISL, NLD, CHE), with the data's index 1/(2 - θ) of the file and its spending. """
    fresh()
    synthetic()
    m = D.oecd26Layer(1)
    assert len(m) == 29 and D.oecd26Anchor()['p'] == P[V['spec']]
    assert int(SMP['sample26'].sum()) == 26 and set(SMP.index[~SMP['sample26']]) == {'MEX', 'TUR', 'KOR'}
    p = T.panelData(1)
    assert list(p.index) == SAMPLE and len(p) == int(TV['sample'].sum()) and p.attrs['dropped'] == []
    if THETA == 'C':
        assert len(p) == 21 and not {'AUS', 'DNK', 'ISL', 'NLD', 'CHE', 'MEX'} & set(p.index)
    assert np.allclose(p['indexData'], 1/(2 - TV.loc[p.index, 'theta']), atol = 1e-15)
    assert np.allclose(p['spendingData'], TV.loc[p.index, 'spending'], atol = 1e-12)
    assert np.allclose(p['indexModel'], 1/(2 - p['θModel']), atol = 1e-15)


def test_slopes_exact_and_data():
    fresh()
    synthetic()
    s = T.slopes().set_index(['y', 'x'])
    f, t = FIG.loc[SAMPLE], TV.loc[SAMPLE]
    want = {('spending', 'growth'): _ols(f['popGrowth'], t['spending']),
            ('spending', 'gini'): _ols(f['gini'], t['spending']),
            ('spending', 'index'): _ols(t['index'], t['spending']),
            ('index', 'growth'): _ols(f['popGrowth'], t['index']),
            ('index', 'gini'): _ols(f['gini'], t['index'])}
    for k, b in want.items():
        assert abs(s.loc[k, 'data']['slope'] - b) < 1e-10, k
        assert s.loc[k, 'data']['n'] == len(SAMPLE)
    assert abs(s.loc[('index', 'growth'), 'layer1']['slope'] + 0.3) < 1e-10      # exact by construction
    assert s.loc[('index', 'growth'), 'layer1']['se'] < 1e-10
    for k in (('spending', 'growth'), ('spending', 'gini')):
        assert s.loc[k, 'targeted2']
    s2 = T.slopes(reading = 'inForce').set_index(['y', 'x'])
    assert abs(s2.loc[('index', 'growth'), 'layer1']['slope'] + 0.3) < 1e-10      # the in-force index is shifted


def test_cses_drops_luxembourg_and_no_29():
    fresh()
    synthetic('cses', lux = True)
    p = T.panelData(1, turnout = 'cses')
    assert 'LUX' not in p.index and p.attrs['dropped'] == ['LUX'] and len(p) == len(SAMPLE) - 1
    assert T.slopes(turnout = 'cses').attrs['n'] == len(SAMPLE) - 1
    synthetic()
    assert _raises(lambda: T.panelData(2, sample = '29'), ValueError)             # the 29 are no sample any more


def test_stale_and_missing():
    fresh()
    synthetic()
    d = pd.read_csv(D.oecd26Path(1), dtype = {'inputsKey': str, 'anchorKey': str})
    d.loc[(d['iso3'] == 'GBR') & (d['spec'] == V['spec']), 'anchorKey'] = 'h0000000000ff'
    d.to_csv(D.oecd26Path(1), index = False)
    e = _raises(lambda: D.oecd26Layer(1), ValueError)
    assert e and 'GBR' in e
    synthetic(drop = ('ITA',))
    e = _raises(lambda: T.panelData(1), D.MissingInput)
    assert e and 'ITA' in e
    synthetic(drop = ('MEX', 'AUS'))
    assert len(T.panelData(1)) == len(SAMPLE)                # outside the measure's sample: not needed
    for kw in ({'β': BETA*(1 + 1e-6)}, {'grid': 'coarse'}):   # an anchor of an earlier U.S. calibration, a coarse run
        synthetic(**kw)
        e = _raises(lambda: D.oecd26Anchor(), ValueError)
        assert e and 'rerun python/US/runOECD26.py' in e, kw
    fresh()
    synthetic(theta = 'index')                               # rows of another measure only: never read as the main
    assert _raises(lambda: D.oecd26Layer(1), D.MissingInput) and len(T.panelData(1, theta = 'paper')) == 26


def test_variants_select_and_never_mix():
    """ Both specs, both β rules and two measures of the design in one set of csvs: each reader call returns its own
    variant's 29 rows and slope, the default call config.US['oecd26']'s at config.US['theta'], and the anchor of a
    spec is its 'common' row. """
    fresh()
    for spec, rule in SLOPE:
        synthetic(spec = spec, betaRule = rule)
    synthetic(theta = 'index')
    assert len(pd.read_csv(D.oecd26Path(1))) == 29*(len(SLOPE) + 1) and len(pd.read_csv(D.oecd26Path(0))) == 3
    for (spec, rule), b in SLOPE.items():
        kw = {} if (spec, rule) == (V['spec'], V['betaRule']) else {'spec': spec, 'betaRule': rule}
        lay = D.oecd26Layer(1, **kw)
        assert len(lay) == 29 and set(lay['spec']) == {spec} and set(lay['betaRule']) == {rule}, (spec, rule)
        assert set(lay['thetaSource']) == {THETA}
        s = T.slopes(**kw).set_index(['y', 'x'])
        assert abs(s.loc[('index', 'growth'), 'layer1']['slope'] - b) < 1e-10, (spec, rule)
    s = T.slopes(theta = 'paper').set_index(['y', 'x'])
    assert abs(s.loc[('index', 'growth'), 'layer1']['slope'] - SLOPETHETA['index']) < 1e-10
    assert D.oecd26Anchor()['p'] == P[V['spec']] and D.oecd26Anchor(spec = 'size')['p'] == P['size']
    assert D.oecd26Anchor(spec = 'sizePiR')['betaRule'] == 'common'


def test_legacy_rows_read_as_common():
    """ Rows written before the betaRule column (or blank in it) are 'common' rows; no 'commonR' row is made up. """
    fresh()
    synthetic(spec = 'size', betaRule = 'common', legacy = True)
    assert 'betaRule' not in pd.read_csv(D.oecd26Path(1)).columns
    assert len(D.oecd26Layer(1, spec = 'size', betaRule = 'common')) == 29
    assert _raises(lambda: T.panelData(1, spec = 'size', betaRule = 'commonR'), D.MissingInput)
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
    assert len(p) == len(SAMPLE) and np.isfinite(p['spendingModel']).all() and p['θModel'].isna().all()


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
    fresh()
    synthetic()
    n = len(SAMPLE)
    for fn, name in ((T.oecd26Slopes, 'OECD26_Slopes'), (T.oecd26Omega, 'OECD26_Omega')):
        tex = fn()
        assert tex.startswith('%% GENERATED') and 'results/oecd26/' in tex.splitlines()[2]
        assert '--only ' + name + '\n' in tex                  # the paper's variant: the registered name
        t = TT.parse(tex)
        t.html(TT.Context(strict = True))
        keys = [l.split('% row: ')[1] for l in tex.splitlines() if '% row: ' in l]
        assert len(keys) == len(set(keys)) and len(keys) == (5 if name == 'OECD26_Slopes' else n), name
    assert T.MEASURENOTE in T.oecd26Omega() and 'clipped' not in T.oecd26Omega()
    paths = F.oecd26Figure(1)
    with open([q for q in paths if q.endswith('.marks.json')][0], encoding = 'utf-8') as f:
        marks = json.load(f)['marks']
    assert len(marks) == 5*(2*n + 2)
    line = [m for m in marks if m['id'].endswith('index_growth--model--fit')][0]
    assert abs(line['value'] + 0.3) < 1e-10 and line['row'] == 'index_growth'
    assert len(json.load(open([q for q in F.oecd26Figure(2) if q.endswith('.marks.json')][0],
                              encoding = 'utf-8'))['marks']) == 2*(2*n + 2)


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
    data are the least-squares slopes of the synthetic numbers on the measure's countries, the index relations are
    never asked for, and the figure's note carries both pairs as the table cells print them. """
    assert V['spendingSpec'] == 'none'
    fresh()
    synthetic(spec = 'none', betaRule = 'common')
    s = T.spendingSlopes().set_index(['y', 'x'])
    assert list(s.index) == list(T.SPENDING) and s['layer2'].isna().all()
    f, t = FIG.loc[SAMPLE], TV.loc[SAMPLE]
    model = 10 + 4*(f['popGrowth'].astype(float) - 1) + 6*f['gini'].astype(float)
    for (y, x), col in ((('spending', 'growth'), 'popGrowth'), (('spending', 'gini'), 'gini')):
        assert abs(s.loc[(y, x), 'data']['slope'] - _ols(f[col], t['spending'])) < 1e-10
        assert abs(s.loc[(y, x), 'layer1']['slope'] - _ols(f[col], model)) < 1e-10
        assert s.loc[(y, x), 'layer1']['n'] == len(SAMPLE)
    paths = F.oecd26Spending()
    note = open([q for q in paths if q.endswith('OECD26_Spending_note.tex')][0], encoding = 'utf-8').read()
    assert note.startswith('%% GENERATED') and '--only OECD26_Spending\n' in note
    for k in T.SPENDING:
        for side in ('data', 'layer1'):
            assert T._cell(s.loc[k, side]) in note, (k, side)
    assert r'\omega' not in note and 'countries' not in note           # the sample and anchor are section 6's
    marks = json.load(open([q for q in paths if q.endswith('.marks.json')][0], encoding = 'utf-8'))['marks']
    assert len(marks) == 2*(2*len(SAMPLE) + 2)


def test_theta_variants_measures_and_dashes():
    """ OECD26_ThetaVariants: each measure of the design prints its own slopes (index on growth, layer 1: the measure's
    b) and its own data side (figure 1.1's index on the 26 for 'paper', the variant's 1/(2 - θ) on its countries
    otherwise); a measure never run, and one whose anchor is of another U.S. calibration, print `--`; the star is on
    config.US['theta']'s row only. """
    fresh()
    synthetic()
    synthetic(theta = 'index')
    synthetic(theta = 'A')
    synthetic(theta = 'B', β = BETA*(1 + 1e-6))                 # B's anchor off its own sweep: stale
    tex = T.oecd26ThetaVariants()
    assert '--only OECD26_ThetaVariants\n' in tex and r'\label{table:OECD26:thetaVariants}' in tex
    rows = _table(tex)
    assert len(rows) == 5*len(T.MEASURES)
    cell = lambda b: T._cell({'slope': b, 'se': 0.})
    for m, b in (('paper', SLOPETHETA['index']), (THETA, -0.3), ('A', SLOPETHETA['A'])):
        assert rows['index_growth_' + m][2] == cell(b), (m, rows['index_growth_' + m])
        assert rows['index_growth_' + m][4:] == ['--']*3                          # no cses rows written
    for m in ('A2pt', 'B'):
        assert rows['index_growth_' + m][1:] == ['--']*6, m
    keep26 = SMP.index[SMP['sample26']]
    assert rows['index_growth_paper'][1] == T._cell(T.ols(FIG.loc[keep26, 'popGrowth'], FIG.loc[keep26, 'bbIndex']))
    tA = D.thetaVariant('A')
    sA = D.oecd26SampleOf('A')
    assert rows['index_growth_A'][1] == T._cell(T.ols(FIG.loc[sA, 'popGrowth'], tA.loc[sA, 'index']))
    assert rows['index_growth_' + THETA][0].endswith(r'$^{\ast}$') and not rows['index_growth_A'][0].endswith('$')
    assert r'\epsilon' not in tex and ' --: not computed.' in tex


def _deepTest(θFR = 0.82188, ownFR = 13.59, corner = False):
    """ Synthetic escCountry.csv in C.ESCDIR at the main measure (thetaSource, θ0 the U.S.'s): the UK (θ* 0.181, its own
    λ 3.63) and France (θ* `θFR`, its own λ `ownFR`, None for no converged one) under the U.S. λ 6.247; with `corner`
    France's corner slope (escCornerSlope.csv). A copy of every row at thetaSource 'index' beside them, at other
    numbers, which no reader may take. """
    os.makedirs(C.ESCDIR, exist_ok = True)
    for f in ('escCornerSlope.csv',):
        if os.path.exists(os.path.join(C.ESCDIR, f)):
            os.remove(os.path.join(C.ESCDIR, f))
    common = {'phi': 0.5, 'commonX': True, 'spec': 'size'}
    θ = {'thetaSource': THETA, 'θ0': C.theta0()}
    rows = []
    for c, θs, V_, ch, own in (('UK', 0.181208, 0.223, 0.493, 3.63), ('FR', θFR, 0.218, 0.645, ownFR)):
        rows += [common | θ | {'country': c, 'wedgeFrom': 'US', 'p': 6.247, 'θStar': θs, 'choice': ch, 'ω': 1.2,
                                'Vtilde': V_},
                 common | θ | {'country': c, 'wedgeFrom': 'own', 'p': np.nan if own is None else own, 'θStar': θs,
                                'choice': θs, 'converged': own is not None, 'ω': 1.2, 'Vtilde': V_}]
    stale = [r | {'thetaSource': 'index', 'θ0': np.nan, 'p': 11.345, 'choice': 0.7} for r in rows]
    pd.DataFrame(rows + stale).to_csv(os.path.join(C.ESCDIR, 'escCountry.csv'), index = False)
    if corner:
        pd.DataFrame([common | θ | {'country': 'FR', 'λ': lam, 'vote': 1, 'slope': -0.1, 'τ1Corner': 0.2}
                      for lam in (0.0, 6.247)]).to_csv(os.path.join(C.ESCDIR, 'escCornerSlope.csv'), index = False)


def test_country_table_lambda_and_france():
    """ US_ESC_Country under the U.S. λ: the UK and France at the main measure's rows (the 'index' copies never read);
    France at its interior design prints its own λ and no corner sentence, without reading escCornerSlope.csv;
    France at the corner θ = 1 with no own λ prints `--` and the corner sentence, which reads the corner slopes; an
    own λ at the corner raises. """
    _deepTest()
    tex = TU.escCountryTable()
    rows = _table(tex)
    assert list(rows) == ['gbr', 'fra']
    assert rows['gbr'][1:] == ['0.181', '0.223', '0.493', '3.63']
    assert rows['fra'][1:] == ['0.822', '0.218', '0.645', '13.59']
    assert 'Bismarckian corner' not in tex and r'$\lambda = 6.25$' in tex and 'escCornerSlope' not in tex
    assert r'\varepsilon' not in tex
    _deepTest(θFR = 1.0, ownFR = None, corner = True)
    tex = TU.escCountryTable()
    assert _table(tex)['fra'][1:] == ['1.000', '0.218', '0.645', '--'] and tex.count('Bismarckian corner') == 1
    _deepTest(θFR = 1.0, ownFR = 13.59, corner = True)
    assert _raises(lambda: TU.escCountryTable(), ValueError)
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
