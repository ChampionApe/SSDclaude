r""" The stage (iii) builders of the cross-country test (tablesOECD26, figuresOECD26) and their readers
(datasets.oecd26*), on synthetic results/oecd26 csvs written to a temporary directory.

Run:  .venv\Scripts\python.exe python\paper\test_oecd26.py      (seconds; pytest collects the same test_ functions)

The synthetic model makes every relation exact, so its slopes are known: layer 1's spending at the observed design is
10 + 4 (growth - 1) + 6 gini and its index 0.9 + b (growth - 1) on the design chosen (shifted by 0.1 on the design in
force), b = -0.3 at the paper's variant and another value at each other (spec, betaRule) and each other measure of the
design (thetaSource); layer 2 matches the data's spending at the observed design; in both layers the spending at the
chosen design (τInForce/τ2020 times spending2020) is 5 + 10 I of the design in force. Layer rows carry omegaRule
(layer 1 at config's 'mean', with ωMean, or 'anchor'; layer 2 'anchor') and retAge (config's 'nra' or a population
variant), and the paper's turnout 'csesFlat' stands on the 'cses' anchor (datasets.ANCHORTURNOUT). The variants share
one set of csvs, as runOECD26.py writes them, so a reader that mixed them would read the wrong b. The data side is config.US['theta']'s measure of
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
OMEGAMEAN = 1.2                                               # layer 1's ω under omegaRule 'mean' (the anchor's is 1.23)


def _slope(spec, betaRule, theta):
    return SLOPETHETA[theta] if theta != THETA and theta in SLOPETHETA else SLOPE.get((spec, betaRule), -0.3)


def synthetic(turnout = None, anchorKey = 'h000000000001', drop = (), lux = False, β = None, grid = 'fine',
              spec = None, betaRule = None, legacy = False, theta = None, omegaRule = None, retAge = None, b = None,
              layers = (1, 2)):
    """ anchor.csv and layer{1,2}.csv for `turnout`, `spec`, `betaRule`, layer 1's `omegaRule` and `retAge`
    (config.US['oecd26']'s where None) and the measure `theta` (config.US['theta'] by default; 'index' for figure 1.1's
    index) in datasets.oecd26Dir(theta), every country but `drop`, replacing the rows of the same reading (the
    anchor's: its turnout datasets.ANCHORTURNOUT's, its β rule always 'common'); a data variant also gets its U.S.
    sweep (oecd26_theta_<V>/calibration/). Layer 1's rows carry `omegaRule` (under 'mean' ω and ωMean OMEGAMEAN),
    layer 2's 'anchor'; `layers` the layers written. `lux` writes Luxembourg as 'noTurnout'; `legacy` writes no
    betaRule column, as the csvs before it. Under 'none' the anchor has no cost parameter and no row a design. `b`
    layer 1's index-on-growth slope (_slope's where None). """
    turnout = V['turnout'] if turnout is None else turnout
    theta = THETA if theta is None else theta
    root = D.oecd26Dir(theta)
    os.makedirs(root, exist_ok = True)
    spec = V['spec'] if spec is None else spec
    betaRule = V['betaRule'] if betaRule is None else betaRule
    omegaRule = V['omegaRule'] if omegaRule is None else omegaRule
    retAge = V['retAge'] if retAge is None else retAge
    aTurnout = D.ANCHORTURNOUT.get(turnout, turnout)
    β = BETA if β is None else β
    if theta not in (THETA, 'index'):
        os.makedirs(os.path.join(root, 'calibration'), exist_ok = True)
        pd.DataFrame([{'ρ': 1.0, 'β': BETA, 'residual': 1e-12, 'thetaSource': theta, 'θ0': C.theta0('US', theta)}]) \
            .to_csv(os.path.join(root, 'calibration', 'US_rhoGridCommonX.csv'), index = False)
    key = KEY | {'spec': spec, 'betaRule': betaRule, 'thetaSource': theta}
    g, gi = FIG['popGrowth'].astype(float), FIG['gini'].astype(float)
    b = _slope(spec, betaRule, theta) if b is None else b
    idx = 0.9 + b*(g - 1)
    idxUS = 0.9 + _slope(spec, 'common', theta)*(g['USA'] - 1)
    index = FIG['bbIndex'] if theta == 'index' else D.thetaVariant(theta)['index'].reindex(FIG.index)
    a = pd.DataFrame([key | {'betaRule': 'common', 'turnout': aTurnout, 'iso3': 'USA', 'status': 'ok', 'β': β,
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
        for layer in layers:
            extra = {'omegaRule': omegaRule if layer == 1 else 'anchor', 'retAge': retAge}
            if layer == 1 and omegaRule == 'mean':
                extra |= {'ωMean': OMEGAMEAN, 'nMean': len(FIG)}
            if lux and c == 'LUX':
                rows[layer].append(base | {'status': 'noTurnout'} | extra)
                continue
            sp = 10 + 4*(g[c] - 1) + 6*gi[c] if layer == 1 else float(FIG.at[c, 'pensionSpending'])
            design = ({'θChosen': np.nan, 'θInForce': np.nan, 'τInForce': np.nan} if spec == 'none' else
                      {'θChosen': 2 - 1/idx[c], 'θInForce': 2 - 1/(idx[c] - 0.1), 'τInForce': chosen(idx[c] - 0.1)/70})
            ω = (OMEGAMEAN if omegaRule == 'mean' else 1.23) if layer == 1 else 1 + 0.01*sp
            rows[layer].append(base | {'status': 'ok', 'ω': ω,
                                       'ν2020': g[c], 'Vtilde': 0.2, 'spendingData': FIG.at[c, 'pensionSpending'],
                                       'indexData': index[c], 'θData': 2 - 1/index[c], 'spending2020': sp, 'τ2020': sp/70}
                               | design | extra)
    for name, df in (('anchor', a), ('layer1', pd.DataFrame(rows[1])), ('layer2', pd.DataFrame(rows[2]))):
        if df.empty:
            continue
        old = os.path.join(root, name + '.csv')
        rule = 'common' if name == 'anchor' else betaRule
        if legacy:
            df = df.drop(columns = 'betaRule')
        if os.path.exists(old):
            prev = pd.read_csv(old, dtype = {'inputsKey': str, 'anchorKey': str})
            prule = prev['betaRule'].fillna('common') if 'betaRule' in prev.columns else 'common'
            same = ((prev['turnout'] == (aTurnout if name == 'anchor' else turnout)) & (prev['spec'] == spec)
                    & (prule == rule) & (prev['thetaSource'] == theta))
            if name != 'anchor':
                prevRule = prev['omegaRule'].fillna('anchor') if 'omegaRule' in prev.columns else 'anchor'
                prevAge = prev['retAge'].fillna('none') if 'retAge' in prev.columns else 'none'
                same &= (prevRule == (omegaRule if name == 'layer1' else 'anchor')) & (prevAge == retAge)
            df = pd.concat([prev[~same], df], ignore_index = True)
        df.to_csv(old, index = False)


def chosen(index):
    """ The synthetic spending at the chosen design (% of GDP) at the index of the design in force. """
    return 5 + 10*index


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
    # the paper's turnout has no anchor row of its own: it stands on the cses anchor, and Luxembourg is in the panel
    assert V['turnout'] == 'csesFlat' and set(pd.read_csv(D.oecd26Path(0))['turnout']) == {'cses'}
    assert D.oecd26Anchor()['turnout'] == 'cses' and 'LUX' in T.panelData(1).index
    assert set(m['omegaRule']) == {V['omegaRule']} and set(m['retAge']) == {V['retAge']}
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
    assert V['spendingReading'] == 'chosen'
    for k in (('spending', 'growth'), ('spending', 'gini')):
        assert not s.loc[k, 'targeted2']                                          # at the chosen design
    for k in (1, 2):                                                              # 5 + 10 I, exact in both layers
        assert abs(s.loc[('spending', 'index'), 'layer{}'.format(k)]['slope'] - 10) < 1e-10, k
    so = T.slopes(spending = 'observed').set_index(['y', 'x'])
    for k in (('spending', 'growth'), ('spending', 'gini')):
        assert so.loc[k, 'targeted2']
        assert abs(so.loc[k, 'layer2']['slope'] - so.loc[k, 'data']['slope']) < 1e-10
    p, po = T.panelData(1), T.panelData(1, spending = 'observed')
    assert np.allclose(p['spendingModel'], chosen(p['indexModel']), atol = 1e-12)
    assert np.allclose(po['spendingModel'], p['spendingObserved'], atol = 0)
    assert _raises(lambda: T.panelData(1, reading = 'chosen', spending = 'chosen'), ValueError)
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
    assert T.suffix() == '' and T.suffix(spec = 'size') == '_size' and T.suffix(spending = 'observed') == '_observed'
    assert T.suffix(turnout = 'cses', spec = 'none', betaRule = 'commonR') == '_cses_none_commonR'
    assert V['turnout'] == 'csesFlat' and T.suffix(turnout = 'cses') == '_cses'
    assert ((T.suffix(retAge = 'none'), T.suffix(retAge = 'exit'), T.suffix(omegaRule = 'anchor'), T.suffix(theta = 'B'))
            == ('_nuNone', '_nuExit', '_omegaUS', '_thetaB'))
    assert T.variantCaption() == '' and T.TURNOUTCAPTION['cses'] in T.variantCaption(turnout = 'cses')
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
    # the paper's note points to appendix G.1 for θ; a variant's note states MEASURENOTE in full
    assert r'\ref{app:oecd26:data}' in T.oecd26Omega() and 'clipped' not in T.oecd26Omega() and C.THETADEF in T.MEASURENOTE
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
    never asked for, and the figure's note gives the sample, the anchor and the turnout but not the slopes, which
    section 6's text quotes (notes/paper_styleGuide.md, "What a note holds"). """
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
            assert T._cell(s.loc[k, side]) not in note, (k, side)
    a = D.oecd26Anchor(spec = 'none')                    # the sample, the anchor's β, layer 1's mean ω, the turnout
    assert ('{} countries'.format(len(SAMPLE)) in note and r'$\beta = ' + C.num(a['β'], 2) + '$' in note
            and 'mean of the second layer' in note and C.num(OMEGAMEAN, 2) in note
            and T.TURNOUTNOTE[V['turnout']] in note and r'\varepsilon' not in note)
    marks = json.load(open([q for q in paths if q.endswith('.marks.json')][0], encoding = 'utf-8'))['marks']
    assert len(marks) == 2*(2*len(SAMPLE) + 2)


def test_variants_table_population_and_measures():
    """ OECD26_Variants: panel A the paper's ν and config's population variants in RETAGEORDER over one data row, each
    with its own layer slopes (index on growth: the reading's b); panel B config.US['theta'] then the data variants, each
    with its own data side (the variant's 1/(2 - θ) on its countries); a measure whose anchor is of another U.S.
    calibration prints `--`; the star on the paper's rows only; the table converts. """
    fresh()
    synthetic()
    synthetic(retAge = 'none', b = -0.15)
    synthetic(retAge = 'exit', b = -0.45)
    synthetic('cses', lux = True, retAge = 'none', b = -0.17)  # the uncorrected ν without Luxembourg
    synthetic(theta = 'A')
    synthetic(theta = 'B', β = BETA*(1 + 1e-6))                 # B's anchor off its own sweep: stale
    assert T.MEASURES == (THETA, 'A', 'B') and T.populationRows() == ['none', 'nra', 'exit']
    tex = T.oecd26Variants()
    assert '--only OECD26_Variants\n' in tex and r'\label{table:OECD26:variants}' in tex
    rows = _table(tex)
    keys = (['population_data'] + ['population_{}_{}'.format(r, s) for r in ('none', 'nra', 'exit')
                                   for s in ('layer1', 'layer2')]
            + ['population_none_cses_{}'.format(s) for s in ('data', 'layer1', 'layer2')]
            + ['measure_{}_{}'.format(m, s) for m in (THETA, 'A', 'B') for s in ('data', 'layer1', 'layer2')])
    assert list(rows) == keys
    noLux = [c for c in SAMPLE if c != 'LUX']
    assert rows['population_none_cses_layer1'][2 + list(T.RELATIONS).index(('index', 'growth'))] == \
        T._cell({'slope': -0.17, 'se': 0.}, stack = True)
    assert rows['population_none_cses_data'][2 + list(T.RELATIONS).index(('index', 'growth'))] == \
        T._cell(T.ols(FIG.loc[noLux, 'popGrowth'], TV.loc[noLux, 'index']), stack = True)
    assert rows['population_none_cses_data'][0] == 'Uncorrected, without Luxembourg'
    cell = lambda b: T._cell({'slope': b, 'se': 0.}, stack = True)
    ig = 2 + list(T.RELATIONS).index(('index', 'growth'))
    for r, b in (('none', -0.15), ('nra', -0.3), ('exit', -0.45)):
        for side in ('layer1', 'layer2'):
            assert rows['population_{}_{}'.format(r, side)][ig] == cell(b), (r, side)
    assert rows['population_data'][ig] == T._cell(T.ols(FIG.loc[SAMPLE, 'popGrowth'], TV.loc[SAMPLE, 'index']), stack = True)
    tA, sA = D.thetaVariant('A'), D.oecd26SampleOf('A')
    assert rows['measure_A_data'][ig] == T._cell(T.ols(FIG.loc[sA, 'popGrowth'], tA.loc[sA, 'index']), stack = True)
    assert rows['measure_A_layer1'][ig] == cell(SLOPETHETA['A']) and rows['measure_B_data'][2:] == ['--']*5
    assert rows['measure_{}_data'.format(THETA)][2:] == rows['population_data'][2:]
    assert rows['population_nra_layer1'][0].endswith(r'$^{\ast}$') and rows['population_none_layer1'][0] == 'Uncorrected'
    assert rows['measure_{}_data'.format(THETA)][0].endswith(r'$^{\ast}$') and not rows['measure_A_data'][0].endswith('$')
    assert ' --: not computed.' in tex and r'\ref{fig:OECD26:layer1}' in tex


def test_layer1_omega_rules_never_mix():
    """ Layer 1 at the mean ω (the paper's) and at the U.S. ω side by side in one csv: each reader call returns its own
    rule's rows and slope, layer 2 one reading under either; a layer-1 rule asked of layer 2 is an error; the paper's
    notes give layer 1's mean ω, the U.S.-ω variant's the anchor's. """
    fresh()
    synthetic()
    synthetic(omegaRule = 'anchor', b = -0.2, layers = (1,))
    for rule, b in (('mean', -0.3), ('anchor', -0.2)):
        s = T.slopes(omegaRule = rule).set_index(['y', 'x'])
        assert abs(s.loc[('index', 'growth'), 'layer1']['slope'] - b) < 1e-10, rule
        assert abs(s.loc[('index', 'growth'), 'layer2']['slope'] + 0.3) < 1e-10, rule
    assert _raises(lambda: D.oecd26Layer(2, omegaRule = 'mean'), ValueError)
    assert len(D.oecd26Layer(1, omegaRule = 'anchor')) == 29 and len(D.oecd26Layer(1)) == 29
    assert T.layer1Omega(T.variant()) == OMEGAMEAN and T.layer1Omega(T.variant(omegaRule = 'anchor')) is None
    tex = T.oecd26Slopes(omegaRule = 'anchor')
    assert '--only OECD26_Slopes_omegaUS\n' in tex and r'$\omega = 1.23$' in tex and 'mean of layer 2' not in tex
    assert 'Model and layers as in figure' in T.oecd26Slopes()
    note = open([q for q in F.oecd26Figure(1) if q.endswith('_note.tex')][0], encoding = 'utf-8').read()
    assert 'mean of the second layer' in note and C.num(OMEGAMEAN, 2) in note


def test_theta_fit_statistics_and_figures():
    """ tablesOECD26.thetaFit: r, RMSE and the RMSE at the mean over the countries other than the U.S., in θ and in
    index units, as computed here; OECD26_ThetaFit and appendix G's OECD26_ThetaFitPopulation and _Measure write their
    marks (every dot, line and statistic); the notes point to figure 7.2, leave the statistics to the panels and, at the
    mean ω, put the U.S. on the 45-degree line in layer 2 only. """
    fresh()
    synthetic()
    for r in C.US['oecd26']['populationVariants']:
        synthetic(retAge = r)
    for m in C.US['oecd26']['thetaVariants']:
        synthetic(theta = m)
    for units, cols in (('theta', ('θData', 'θModel')), ('index', ('indexData', 'indexModel'))):
        f = T.thetaFit(1, units = units)
        h = T.panelData(1).drop(index = 'USA')
        x, y = h[cols[0]].values, h[cols[1]].values
        assert abs(f['r'] - np.corrcoef(x, y)[0, 1]) < 1e-12 and f['nStat'] == len(h) == f['n'] - 1
        assert abs(f['rmse'] - np.sqrt(np.mean((y - x)**2))) < 1e-12
        assert abs(f['rmseMean'] - np.std(x)) < 1e-12 and abs(f['sdData'] - f['rmseMean']) < 1e-12
        assert abs(f['sdModel'] - np.std(y)) < 1e-12
    paths = F.oecd26ThetaFit()
    marks = json.load(open([q for q in paths if q.endswith('.marks.json')][0], encoding = 'utf-8'))['marks']
    n = len(SAMPLE)
    assert len(marks) == 2*(n + 2)
    note = open([q for q in paths if q.endswith('_note.tex')][0], encoding = 'utf-8').read()
    f1 = T.thetaFit(1)
    assert 'RMSE {}'.format(C.num(f1['rmse'], 2)) not in note and '$r = ' not in note
    assert 'other {} countries'.format(f1['nStat']) in note and r'\ref{fig:OECD26:layer1}' in note
    assert V['omegaRule'] == 'mean' and 'in the second layer it lies on the' in note
    for kind, ns in (('population', [n]*3), ('measure', [len(D.oecd26SampleOf(m)) for m in T.MEASURES])):
        paths = F.oecd26ThetaFitRows(kind)
        assert any(os.path.basename(q) == 'OECD26_ThetaFit{}.pdf'.format(kind.capitalize()) for q in paths), kind
        marks = json.load(open([q for q in paths if q.endswith('.marks.json')][0], encoding = 'utf-8'))['marks']
        assert len(marks) == sum(2*(k + 2) for k in ns), kind


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


def test_paper_rows_and_data_columns_are_never_stale():
    """ A stale row of the paper's own variant (the starred rows of OECD26_Variants) raises where a variant's prints
    `--`; layer 2's copy of the data side that is not data/oecd26_theta.csv's is StaleInput in OECD26_Omega. """
    fresh()
    synthetic(β = BETA*(1 + 1e-6))                                 # the paper's anchor off the U.S. sweep
    assert _raises(lambda: T.oecd26Variants(), D.StaleInput)
    fresh()
    synthetic()
    d = pd.read_csv(D.oecd26Path(2), dtype = {'inputsKey': str, 'anchorKey': str})
    d['spendingData'] += 0.01
    d.to_csv(D.oecd26Path(2), index = False)
    e = _raises(lambda: T.oecd26Omega(), D.StaleInput)
    assert e and 'data columns of layer 2' in e


def test_correlations_and_capital_share_are_tied_to_their_sources():
    """ OECD_Correlations refuses an oecdCorrelations.csv that is not the current figure's (StaleInput); the capital
    share has no fallback to the workbook (MissingInput without the summary). """
    import tablesOA as OA, oecdFigure1 as F1
    cur = F1.figureCorrelations(F1.plotted())
    old, D.OECDCORR = D.OECDCORR, os.path.join(TMP, 'oecdCorrelations.csv')
    try:
        cur.to_csv(D.OECDCORR, index = False)
        assert 'row: named_spending_growth' in OA.oecdCorrelations()
        bad = cur.copy()
        bad.loc[0, 'n'] -= 1
        bad.to_csv(D.OECDCORR, index = False)
        assert _raises(lambda: OA.oecdCorrelations(), D.StaleInput)
    finally:
        D.OECDCORR = old
    D.usAlpha.cache_clear()
    assert _raises(lambda: D.usAlpha(), D.MissingInput)


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
