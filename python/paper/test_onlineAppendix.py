r""" Checks of the online appendix: its generator (onlineAppendix.py), the table converter (texTable.py) and the
datasets of its interactive figures (siteData.py), the last against the paper's own figures.

Run:  .venv\Scripts\python.exe python\paper\test_onlineAppendix.py      (pytest collects the same test_ functions)

Reads results/paper, writing/Paper and writing/OnlineAppendix; writes nothing (the generator itself is not run).
"""
import os, re, sys, glob, html, json

import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as C
import texTable as TT
import onlineAppendix as OA

TABLES = sorted(glob.glob(os.path.join(C.PAPERDIR, 'Tables', '*.tex')))
TOL = 1e-6


def _data(name):
    return pd.read_csv(os.path.join(C.PAPERDIR, 'Data', name + '.csv'))


def _marks(name):
    with open(os.path.join(C.PAPERDIR, 'Figs', name + '.marks.json'), encoding = 'utf-8') as f:
        return {m['id']: m['value'] for m in json.load(f)['marks']}


def test_every_table_converts():
    r""" Every built table parses in strict mode (no macro outside the converter's vocabulary), every body row
    fills the table's width, its row keys are unique and are exactly its `% row:` comments, and the HTML carries
    no TeX outside math. """
    assert TABLES, 'no built tables in results/paper/Tables'
    for f in TABLES:
        name = os.path.basename(f)[:-4]
        tex = OA.read(f)
        t = TT.parse(tex)
        h = t.html(TT.Context(strict = True))
        for r in t.body:
            if r.kind != 'group':
                assert sum(c.span for c in r.cells) == t.ncols, (name, [c.tex for c in r.cells])
        live = [l for l in tex.split('\n') if not l.lstrip().startswith('%')]
        assert len(t.keys) == sum('% row:' in l for l in live), name
        outside = re.sub(r'<span class="math inline">.*?</span>', '', h)
        assert not re.search(r'\\[A-Za-z]+', html.unescape(re.sub('<[^>]+>', '', outside))), name


def test_print_copy_resolves_every_reference():
    r""" A table's print copy (for the PDF edition) holds no \ref, \eqref or \oa: each became text. """
    for f in TABLES:
        out = TT.printTex(OA.read(f), lambda label, eq = False: 'X', lambda key: 'OA.0')
        assert not re.search(r'\\(ref|eqref|oa)\s*\{', out), os.path.basename(f)


def test_converter_vocabulary():
    ctx = TT.Context(strict = True)
    assert TT.inline(r'$-0.09$ p.p.', ctx) == '\u22120.09 p.p.'
    assert TT.inline(r'France\textquotesingle s', ctx) == 'France\u2019s'
    assert '\\(\\boldsymbol{\\theta}\\)' in TT.inline(r'$\bm{\theta}$', ctx)
    assert TT.inline(r'1960--2020', ctx) == '1960\u20132020'
    refs = TT.Context(ref = lambda label, eq = False: '[{}|{}]'.format(label, eq))
    assert TT.inline(r'eq.\ \eqref{eq:x}', refs) == '[eq:x|word]'
    assert TT.inline(r'of \eqref{eq:x}', refs) == 'of [eq:x|True]'
    try:
        TT.inline(r'\unknownmacro{a}', ctx)
        raise AssertionError('strict mode let an unknown macro through')
    except TT.UnknownMacro:
        pass
    assert OA.collapseRuns('tables 5 of the paper, 6 of the paper and 7 of the paper') == 'tables 5, 6 and 7 of the paper'


def test_pages_keys_and_registry():
    r""" Every page of _quarto.yml exists and opens with a keyed heading; keys and section codes are unique; every
    retired key points at a live one; every exhibit a page includes is registered, and every registered one is
    included on exactly one page; every registered output is one build.py builds, of the matching kind. """
    pgs = OA.pages()
    assert len(pgs) == len(OA.pageFiles()) >= 20
    keys, codes, seen = {}, [], []
    for p in pgs:
        assert os.path.exists(os.path.join(OA.SITE, p['file'])), p['file']
        assert p['key'], '{} has no keyed level-1 heading'.format(p['file'])
        for k in p['keys']:
            assert k not in keys, 'key {} on {} and {}'.format(k, keys.get(k), p['file'])
            keys[k] = p['file']
        if p['code']:
            codes.append(p['code'])
        seen += p['exhibits']
    assert len(codes) == len(set(codes)), codes
    for old, new in OA.OLDKEYS.items():
        assert new in keys, (old, new)
    assert len(seen) == len(set(seen)), 'an exhibit is included on two pages'
    assert set(seen) == set(OA.EXHIBITS), set(seen) ^ set(OA.EXHIBITS)
    import build
    for i, ex in OA.EXHIBITS.items():
        assert ex.output in build.OUTPUTS, (i, ex.output)
        assert build.OUTPUTS[ex.output][0] == {'explorer': 'data'}.get(ex.kind, ex.kind), i


def test_paper_macros_cover_the_paper():
    r""" writing/Paper/onlineAppendix.tex defines every \oa key the paper uses. """
    defined = set(re.findall(r'\\oadef\{([^}]*)\}', OA.read(OA.MACROS)))
    for d in ('Sections', 'Appendix'):
        for f in glob.glob(os.path.join(C.PAPERTEX, d, '*.tex')):
            for k in re.findall(r'\\oa\{([^}]*)\}', OA.uncomment(OA.read(f))):
                assert k in defined, (os.path.basename(f), k)


def test_reform_paths_are_figure_5_2():
    r""" ARG_ReformPaths: the reform's change in 2010 and 2040 at every rho is the point of the paper's figure
    (ARG_CRRA_LOG), in its units. """
    df, marks = _data('ARG_ReformPaths'), _marks('ARG_CRRA_LOG')
    part = {'tau': 'tau', 'sr': 'sr', 'workweek': 'ww', 'iota': 'iota'}
    n = 0
    for ρ in C.ARG['ρGrid']:
        for v, p in part.items():
            for year, run in ((2010, 'short'), (2040, 'long')):
                r = df[np.isclose(df['rho'], ρ) & (df['year'] == year) & (df['variable'] == v)].iloc[0]
                change = (r['reform'] - r['pre']) * (100 if v == 'iota' else 1)
                assert abs(change - marks['ARG_CRRA_LOG--{}--{}--rho{:.1f}'.format(p, run, ρ)]) < TOL, (ρ, v, year)
                n += 1
    assert n == 16*8


def test_counterfactuals_are_figure_6_1():
    r""" OECD_Counterfactuals: on the U.S. under the paper's calibration, every bar of the paper's figure
    (US_overview) is the dataset's change. """
    df = _data('OECD_Counterfactuals')
    df = df[(df['source'] == 'main') & (df['host'] == 'US') & (df['calibration'] == 'commonX') & (df['effect'] == 'full')]
    out = {'tau': 'tau', 'sr': 'sr', 'ww': 'workweek'}
    marks = _marks('US_overview')
    for mid, value in marks.items():
        _, scen, rho, part = mid.split('--')
        r = df[(df['scenario'] == scen) & np.isclose(df['rho'], float(rho[3:])) & (df['outcome'] == out[part])]
        assert len(r) == 1 and abs(float(r['change'].iloc[0]) - value) < TOL, mid
    assert len(marks) > 40


def test_esc_counterfactuals_are_figure_7_1():
    r""" ESC_Counterfactuals: the paper's figure (US_ESC_overview) at the design levels and at the chosen readings,
    which both conventions for the pinned reading's baseline share. """
    df = _data('ESC_Counterfactuals')
    df = df[(df['source'] == 'main') & (df['host'] == 'US') & (df['spec'] == C.US['esc']['spec'])]
    key = {'acute': 'acute', 'frIncome': 'income', 'frVoting': 'voting', 'frLeisure': 'leisure'}
    out = {'theta': 'theta', 'tau': 'tau', 'sr': 'sr', 'ww': 'workweek'}
    n = 0
    for mid, value in _marks('US_ESC_overview').items():
        _, scen, rho, part, reading = mid.split('--')
        if part != 'theta' and reading != 'chosen':
            continue
        r = df[(df['scenario'] == key[scen]) & np.isclose(df['rho'], float(rho[3:])) & (df['outcome'] == out[part])
               & (df['reading'] == reading)]
        col = 'level' if part == 'theta' else 'change'
        assert len(r) == 1 and abs(float(r[col].iloc[0]) - value) < TOL, mid
        n += 1
    assert n >= 40, n


def test_esc_paths_are_figure_G1():
    r""" ESC_Paths: the U.S. path at rho = 1 is the paper's path figure (US_ESC_Path), year by year. """
    df = _data('ESC_Paths')
    df = df[(df['source'] == 'main') & (df['country'] == 'US') & (df['wedgeFrom'] == 'US')
            & (df['spec'] == C.US['esc']['spec']) & np.isclose(df['rho'], 1.0)]
    n = 0
    for mid, value in _marks('US_ESC_Path').items():
        _, var, reading, year = mid.split('--')
        r = df[(df['variable'] == var) & (df['year'] == int(year))]
        if r.empty:                                   # the figure runs past the site's last dated year
            continue
        assert abs(float(r['chosen' if reading == 'data' else reading].iloc[0]) - value) < TOL, mid
        n += 1
    assert n >= 10, n


def test_datasets_are_complete():
    r""" Every host, calibration, rho and scenario the pages draw is in the datasets, and the only missing values
    are the pinned workweek of the CRRA paths, which escPathCRRA.csv does not store. """
    o = _data('OECD_Counterfactuals')
    m = o[o['source'] == 'main']
    assert set(m['host']) == {'US', 'UK', 'UKUS', 'USMedicare'} and set(m['calibration']) == {'commonX', 'vectorX'}
    for h in ('US', 'UK', 'UKUS', 'USMedicare'):
        sub = m[(m['host'] == h) & (m['effect'] == 'full')]
        for ρ in (0.5, 1.0, 2.0):
            have = set(sub[np.isclose(sub['rho'], ρ)]['scenario'])
            assert {'theta0', 'theta1', 'mild', 'acute', 'income', 'voting', 'leisure'} <= have, (h, ρ)
    assert sorted(o[o['source'] == 'xi']['xi'].unique()) == [0.2, 0.3, 0.4]
    e = _data('ESC_Counterfactuals')
    for h in ('US', 'UK'):
        for ρ in (0.5, 1.0, 2.0):
            have = set(e[(e['host'] == h) & (e['source'] == 'main') & np.isclose(e['rho'], ρ)]['scenario'])
            assert {'acute', 'income', 'voting', 'leisure'} <= have, (h, ρ)
    assert not o.isna().any().any() and not e.isna().any().any()
    p = _data('ESC_Paths')
    nan = p[p.isna().any(axis = 1)]
    assert set(nan['variable']) <= {'workweek'} and not np.isclose(nan['rho'], 1.0).any()
    assert set(p[p['source'] == 'host']['country']) == {'UK', 'FR'}


if __name__ == '__main__':
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print('ok    ' + name)
            except AssertionError as e:
                fails += 1
                print('FAIL  {}: {}'.format(name, e))
    print('{} failed'.format(fails))
    sys.exit(1 if fails else 0)
