r""" The cross-country test of section 7's model (python/US/runOECD26.py, results/oecd26/): the panel data shared
with figuresOECD26, the slopes of figure 1.1's relations in the data and in the model (all five, OECD26_Slopes; the
two of section 6's spending test at the observed designs without the cost, spendingSlopes), the calibrated political
weights (OECD26_Omega), appendix H's design slopes under the other costs, beta rules and turnouts
(OECD26_Robustness), and the U.S., the UK and France measured as in the deep test and as in the cross-section
(OECD26_Reconcile).

Every builder takes
  turnout  'cps' (every economy at the U.S. CPS propensities to vote) | 'cses' (each its own; Luxembourg has none
           and drops out of data and model alike);
  sample   '26' (data/oecd26_sample.csv's sample26) | '29' (figure 1.1's countries);
  reading  'inForce' (the design in force in 2020 on the freely simulated path, chosen in 1990: the reading of the
           cost parameter's target and of appendix G.1) | 'chosen' (the design chosen in 2020 at the observed
           design, in force from 2050);
  spec     the cost transported from the U.S. anchor: 'sizePiR' (λ_n = ε Π_n/R_n for country n, the anchor's ε in
           the csvs' `p`),
           'size' (the anchor's λ) | 'none' (no cost; the model then reads no design);
  betaRule 'common' (the anchor's β in every country) | 'commonR' (each country's β set so that its 2020 return is
           the anchor's);
each None for the paper's variant, PAPER, which is config.US['oecd26']'s (sample '26'). An output's name and label
carry the parts that differ from the paper's variant (`suffix`). The model's design enters every regression on the
index's scale, I = 1/(2 - θ), the inverse of the loader's θ = 2 - 1/I; spending is 100 τ (1 - α), % of GDP, the
inverse of the calibration's τ0. Both sides of every slope use figure 1.1's regressors (OECD population growth
2020/1990, the WIID Gini) and the same countries.
"""
import os
import numpy as np, pandas as pd

import config as C
import datasets as D
import oecdFigure1 as F1
from tables import rowKey, keyed
from tablesUS import _xwrap

# Figure 1.1's panels in its order, (y role, x role); the x role 'index' is the design on the index scale.
RELATIONS = (('spending', 'growth'), ('spending', 'gini'), ('spending', 'index'),
             ('index', 'growth'), ('index', 'gini'))
# Section 6's spending test (spendingSlopes, figuresOECD26.oecd26Spending) and appendix H's robustness table
# (oecd26Robustness), each a subset of RELATIONS.
SPENDING = (('spending', 'growth'), ('spending', 'gini'))
ROBUST = (('index', 'growth'), ('index', 'gini'), ('spending', 'index'))
READINGS = {'chosen': 'θChosen', 'inForce': 'θInForce'}
VARIANT = ('turnout', 'sample', 'reading', 'spec', 'betaRule')          # suffix's order
PAPER = {k: C.US['oecd26'][k] for k in ('turnout', 'reading', 'spec', 'betaRule')} | {'sample': '26'}
YTEX = {'spending': 'Pension spending', 'index': 'Bismarckian index'}
XTEX = {'growth': 'population growth', 'gini': 'the Gini', 'index': 'the Bismarckian index'}
# What a caption adds for a cost or β rule other than the paper's.
SPECCAPTION = {'size': r'the U.S.\ $\lambda$ in every country',
               'sizePiR': r'the U.S.\ $\varepsilon$ in every country, $\lambda_n = \varepsilon\,\Pi_n/R_n$',
               'none': 'without the cost'}
BETACAPTION = {'common': r'the U.S.\ $\beta$ in every country',
               'commonR': r'each country\textquotesingle s $\beta$ set to the U.S.\ 2020 return'}
COSTSYMBOL = {'size': r'$\lambda$', 'sizePiR': r'$\varepsilon$'}                # the anchor's `p`


def variant(turnout = None, sample = None, reading = None, spec = None, betaRule = None):
    """ The variant as a dict over VARIANT, PAPER's value where None. """
    v = dict(zip(VARIANT, (turnout, sample, reading, spec, betaRule)))
    return {k: PAPER[k] if v[k] is None else v[k] for k in VARIANT}


def suffix(turnout = None, sample = None, reading = None, spec = None, betaRule = None):
    r""" '' for the paper's variant (PAPER); otherwise the parts that differ, e.g. '_cses_29', '_size_commonR'.
    Appended to an output's name and \label. """
    v = variant(turnout, sample, reading, spec, betaRule)
    return ''.join('_' + v[k] for k in VARIANT if v[k] != PAPER[k])


def variantCaption(turnout = None, sample = None, reading = None, spec = None, betaRule = None):
    """ What a caption adds for a variant other than the paper's: '' for the paper's own. """
    v = variant(turnout, sample, reading, spec, betaRule)
    parts = ([r'every country of figure \ref{fig:US:OECDdata}'] if v['sample'] != PAPER['sample'] else []) \
        + (['each country at its own turnout'] if v['turnout'] != PAPER['turnout'] else []) \
        + (['the design chosen in 2020'] if v['reading'] != PAPER['reading'] else []) \
        + ([SPECCAPTION[v['spec']]] if v['spec'] != PAPER['spec'] else []) \
        + ([BETACAPTION[v['betaRule']]] if v['betaRule'] != PAPER['betaRule'] else [])
    return ''.join(', ' + p for p in parts)


def _check(v):
    if (v['turnout'] not in ('cps', 'cses') or v['sample'] not in ('26', '29') or v['reading'] not in READINGS
            or v['spec'] not in SPECCAPTION or v['betaRule'] not in BETACAPTION):
        raise ValueError('turnout cps|cses, sample 26|29, reading chosen|inForce, spec size|sizePiR|none, betaRule '
                         'common|commonR; got {}'.format(v))


def panelData(layer, turnout = None, sample = None, reading = None, spec = None, betaRule = None):
    r""" One row per country of the sample with a model row: figure 1.1's x variables (`growth`, `gini`), the
    data's `spendingData`, `indexData`, and the model's `spendingModel`, `θModel`, `indexModel` = 1/(2 - θ),
    from layer `layer` (1 | 2). Countries whose model row is 'noTurnout' (cses) are dropped from both sides and
    listed in `.attrs['dropped']`; a sample country with no row is MissingInput, a failed row an error. """
    v = variant(turnout, sample, reading, spec, betaRule)
    _check(v)
    fig = D.oecdFigure1Data()
    smp = D.oecd26Sample()
    model = D.oecd26Layer(layer, v['turnout'], v['spec'], v['betaRule'])
    isos = [c for c in fig.index if v['sample'] == '29' or bool(smp.at[c, 'sample26'])]
    lack = [c for c in isos if c not in model.index]
    if lack:
        raise D.MissingInput('{} (layer {}, {} {} {}: no row for {})'.format(
            D.oecd26Path(layer), layer, v['turnout'], v['spec'], v['betaRule'], ', '.join(lack)))
    m = model.loc[isos]
    bad = m.index[~m['status'].isin(['ok', 'noTurnout'])]
    if len(bad):
        raise ValueError('layer {} ({}): failed rows for {}'.format(layer, v['turnout'], ', '.join(bad)))
    moved = [c for c in isos if bool(m.at[c, 'sample26']) != bool(smp.at[c, 'sample26'])]
    if moved:
        raise ValueError('layer {} ({}): sample26 differs from data/oecd26_sample.csv for {}: rerun the layer'
                         .format(layer, v['turnout'], ', '.join(moved)))
    dropped = list(m.index[m['status'] == 'noTurnout'])
    keep = [c for c in isos if c not in dropped]
    θ = m.loc[keep, READINGS[v['reading']]].astype(float)
    out = pd.DataFrame({'country': fig.loc[keep, 'country'],
                        'growth': fig.loc[keep, F1.NAMED['growth']].astype(float),
                        'gini': fig.loc[keep, F1.NAMED['gini']].astype(float),
                        'spendingData': fig.loc[keep, F1.NAMED['spending']].astype(float),
                        'indexData': fig.loc[keep, F1.NAMED['index']].astype(float),
                        'spendingModel': m.loc[keep, 'spending2020'].astype(float),
                        'θModel': θ, 'indexModel': 1/(2 - θ)}, index = pd.Index(keep, name = 'iso3'))
    out.attrs['dropped'] = dropped
    return out


def ols(x, y):
    """ Least squares of y on a constant and x: slope, its classical standard error, intercept, Pearson's r
    and n. """
    x, y = np.asarray(x, dtype = float), np.asarray(y, dtype = float)
    n = len(x)
    xc = x - x.mean()
    b = float(np.sum(xc*(y - y.mean()))/np.sum(xc**2))
    a = float(y.mean() - b*x.mean())
    e = y - a - b*x
    se = float(np.sqrt(np.sum(e**2)/(n - 2)/np.sum(xc**2)))
    return {'slope': b, 'se': se, 'intercept': a, 'r': float(np.corrcoef(x, y)[0, 1]), 'n': n}


def _xy(p, yRole, xRole, side):
    """ (x, y) of one relation on `side` 'Data' | 'Model': the regressors are the data's, except the index,
    which is each side's own. """
    y = p[yRole + side]
    x = p[xRole + side] if xRole == 'index' else p[xRole]
    return x, y


def slopes(turnout = None, sample = None, reading = None, spec = None, betaRule = None, relations = RELATIONS,
           layers = (1, 2)):
    """ One row per relation of `relations` (RELATIONS by default): OLS of the data and of each layer of `layers`
    (`data`, `layer1`, `layer2`, each an ols dict, None for a layer not asked for), on the countries every layer
    asked for covers. Layer 2 matches spending by construction, so its spending-on-regressor rows are flagged
    `targeted2`. Under spec 'none' no row has a design: ask for the spending relations only (SPENDING). """
    ps = {k: panelData(k, turnout, sample, reading, spec, betaRule) for k in layers}
    common = ps[layers[0]].index
    for k in layers[1:]:
        common = common.intersection(ps[k].index)
    ps = {k: p.loc[common] for k, p in ps.items()}
    first = ps[layers[0]]
    rows = []
    for yRole, xRole in relations:
        rows.append({'y': yRole, 'x': xRole, 'data': ols(*_xy(first, yRole, xRole, 'Data'))}
                    | {'layer{}'.format(k): ols(*_xy(ps[k], yRole, xRole, 'Model')) if k in ps else None
                       for k in (1, 2)}
                    | {'targeted2': yRole == 'spending' and xRole != 'index'})
    out = pd.DataFrame(rows)
    out.attrs.update({'n': len(common), 'dropped': first.attrs['dropped']})
    return out


def spendingSlopes(turnout = None, sample = None):
    """ Section 6's spending test: the two relations of SPENDING in the data and in layer 1 at config.US['oecd26']'s
    spendingSpec (no cost: no design is read) and the β rule 'common', at the observed designs. """
    return slopes(turnout, sample, None, C.US['oecd26']['spendingSpec'], 'common', relations = SPENDING,
                  layers = (1,))


def _cell(o, digits = 2):
    return '$' + C.num(o['slope'], digits) + '$ $(' + C.num(o['se'], digits) + ')$'


def _layersText(a, v):
    r""" The note's sentence on what the layers share with the anchor `a` and what layer 2 calibrates, at the
    variant `v`. """
    items = ([r'$\beta = ' + C.num(float(a['β']), 3) + '$'] if v['betaRule'] == 'common' else []) \
        + [r'$\omega = ' + C.num(float(a['ω']), 3) + '$'] \
        + ([COSTSYMBOL[v['spec']][:-1] + ' = ' + C.num(float(a['p']), 3) + '$'] if v['spec'] in COSTSYMBOL else [])
    shared = items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]
    tail = {'size': '', 'none': ', without the cost',
            'sizePiR': r', each at its cost $\lambda_n = \varepsilon\,\Pi_{n,2020}/R_{n,2020}$'}[v['spec']] \
        + (r', with the $\beta$ that sets its 2020 return to the U.S.\ one' if v['betaRule'] == 'commonR' else '')
    calibrated = r'$\omega$' if v['betaRule'] == 'common' else r'$\beta$ and $\omega$'
    return (r'Layer 1: every country at the U.S.\ ' + shared + tail + '; layer 2: ' + calibrated
            + r' calibrated to each country\textquotesingle s spending'
            + (r' and the U.S.\ 2020 return' if v['betaRule'] == 'commonR' else '') + ', which it then matches.')


def oecd26Slopes(turnout = None, sample = None, reading = None, spec = None, betaRule = None):
    r""" The slopes of figure 1.1's relations: the data on the sample, the model with the U.S. political weight
    and cost (layer 1) and with each country's own political weight (layer 2). """
    v = variant(turnout, sample, reading, spec, betaRule)
    s = slopes(**v)
    a = D.oecd26Anchor(v['turnout'], v['spec'])
    body = []
    for _, r in s.iterrows():
        label = YTEX[r['y']] + ' on ' + XTEX[r['x']]
        cells = [label, _cell(r['data']), _cell(r['layer1']),
                 r'\textit{targeted}' if r['targeted2'] else _cell(r['layer2'])]
        body.append(' & '.join(cells) + r' \\ % row: ' + rowKey(r['y'] + '_' + r['x']))
    target = (r' (for the U.S.\ its observed design, the target of ' + COSTSYMBOL[v['spec']] + ')'
              if v['spec'] in COSTSYMBOL else '')
    design = (r'the design chosen in 2020, which binds from 2050' if v['reading'] == 'chosen' else
              r'the design in force in 2020 on the freely simulated path, chosen in 1990' + target)
    dropped = s.attrs['dropped']
    note = (r'\textit{Note:} Least-squares slopes with standard errors in parentheses, ' + str(s.attrs['n'])
            + ' countries' + (' (without ' + ', '.join(dropped) + ', which has no turnout data)' if dropped else '')
            + r'. The regressors are those of figure \ref{fig:US:OECDdata} in data and model alike; the model\textquotesingle s '
            r'index is $1/(2-\theta)$ of ' + design + r', and its spending is $\tau(1-\alpha)$ at the observed '
            r'design. ' + _layersText(a, v)
            + (r' Turnout: each country\textquotesingle s own.' if v['turnout'] == 'cses' else ''))
    sfx = suffix(**v)
    return _xwrap('OECD26_Slopes' + sfx,
                  'results/oecd26/layer1.csv, layer2.csv, anchor.csv; data/oecdFigure1.csv, oecd26_sample.csv',
                  r'Figure \ref{fig:US:OECDdata}\textquotesingle s relations in the data and in the model'
                  + variantCaption(**v),
                  'table:OECD26:slopes' + sfx, 'lYYY',
                  [r'\textbf{Relation}', r'\textbf{Data}', r'\textbf{Layer 1}', r'\textbf{Layer 2}'],
                  '\n'.join(body), note, width = r'\textwidth')


def oecd26Omega(turnout = None, sample = None, reading = None, spec = None, betaRule = None):
    r""" Layer 2 by country: the inputs that differ across countries (workers per retiree in 2020, the dispersion
    of relative incomes, spending, the index and the design it implies), the calibrated political weight and the
    design predicted at the U.S. cost, in the order of figure 1.1's footnote. """
    v = variant(turnout, sample, reading, spec, betaRule)
    _check(v)
    p = panelData(2, **v)
    m = D.oecd26Layer(2, v['turnout'], v['spec'], v['betaRule']).loc[p.index]
    a = D.oecd26Anchor(v['turnout'], v['spec'])
    smp = D.oecd26Sample()
    outside = [c for c in p.index if not bool(smp.at[c, 'sample26'])]
    body = []
    for c in p.index:
        r = m.loc[c]
        tag = r'$^{\ast}$' if c == 'USA' else r'$^{\dagger}$' if c in outside else ''
        cells = [str(p.at[c, 'country']) + tag, C.num(float(r['ν2020']), 2),
                 C.num(float(r['Vtilde']), 3), C.num(float(r['spendingData']), 1), C.num(float(r['indexData']), 3),
                 C.num(float(r['θData']), 3), C.num(float(r['ω']), 3), C.num(float(p.at[c, 'θModel']), 3),
                 C.num(float(p.at[c, 'indexModel']), 3)]
        body.append(' & '.join(cells) + r' \\ % row: ' + c.lower())
    design = ('chosen in 2020, in force from 2050' if v['reading'] == 'chosen' else
              'in force in 2020 on the freely simulated path, chosen in 1990')
    head, join = ((r'$\omega$ is calibrated to spending at $\beta = ' + C.num(float(a['β']), 3) + '$', ' and ')
                  if v['betaRule'] == 'common' else
                  (r'$\beta$ and $\omega$ are calibrated to the U.S.\ 2020 return and to spending', ' at '))
    cost = {'size': join + r'the U.S.\ $\lambda = ' + C.num(float(a['p']), 3) + '$',
            'sizePiR': join + r'the U.S.\ $\varepsilon = ' + C.num(float(a['p']), 3)
                       + r'$, $\lambda_n = \varepsilon\,\Pi_{n,2020}/R_{n,2020}$',
            'none': ', without the cost'}[v['spec']]
    anchor = (r' $^{\ast}$The U.S.\ is the anchor, where ' + COSTSYMBOL[v['spec']] + ' is calibrated.'
              if v['spec'] in COSTSYMBOL else r' $^{\ast}$The U.S.\ is the anchor.')
    note = (r'\textit{Note:} $\nu_{2020}$, workers per retiree; $\tilde V$, the dispersion of relative incomes at '
            r'the U.S.\ income percentiles; spending in \% of GDP; $I$, the Bismarckian index, and $\theta = 2 - 1/I$ '
            r'clipped to $[0,1]$. ' + head + cost + r'; the last two columns are the '
            r'model\textquotesingle s design, ' + design + r', and its index.' + anchor
            + (r' $^{\dagger}$Outside the paper\textquotesingle s sample: informal employment above '
               + '{:g}'.format(float(smp['informalMax'].iloc[0])) + r'\% of employment.' if outside else '')
            + (r' Turnout: each country\textquotesingle s own.' if v['turnout'] == 'cses' else ''))
    # two header rows, the data's columns and the model's under a spanner each, so that nine columns fit
    header = (r' & \multicolumn{5}{c}{\textbf{Data}} & \multicolumn{3}{c}{\textbf{Model, layer 2}} \\' + '\n'
              + r'\cmidrule(lr){2-6}\cmidrule(lr){7-9}' + '\n'
              + r'\textbf{Country} & $\nu_{2020}$ & $\tilde V$ & spending & $I$ & $\theta$ & $\omega$ & $\theta$ & $I$')
    sfx = suffix(**v)
    return _xwrap('OECD26_Omega' + sfx, 'results/oecd26/layer2.csv, anchor.csv; data/oecdFigure1.csv, oecd26_sample.csv',
                  r'The countries of the cross-country test, each calibrated to its pension spending'
                  + variantCaption(**v),
                  'table:OECD26:omega' + sfx, 'l' + 'Y'*8, header,
                  '\n'.join(body), note, width = r'\textwidth', size = r'\footnotesize\setlength{\tabcolsep}{3pt}')



# ---------------------------------------------------------------------------------------------------
# Appendix H: the robustness of the design relations across the cost transported, the β rule and turnout, and the
# U.S., the UK and France measured as in the deep test and as in the cross-section.
ROBUSTVARIANTS = (('size', 'common'), ('size', 'commonR'), ('sizePiR', 'common'), ('sizePiR', 'commonR'))
VARIANTTEX = {('size', 'common'): r'$\lambda$, common $\beta$', ('size', 'commonR'): r'$\lambda$, common $R$',
              ('sizePiR', 'common'): r'$\varepsilon$, common $\beta$',
              ('sizePiR', 'commonR'): r'$\varepsilon$, common $R$'}
TURNOUTTEX = {'cps': r'U.S.\ turnout', 'cses': r'Own turnout'}
SHORT = {('index', 'growth'): 'Index on growth', ('index', 'gini'): 'Index on the Gini',
         ('spending', 'index'): 'Spending on the index'}


def _variantSlopes(turnout, sample, reading, spec, betaRule):
    """ slopes() of ROBUST at one variant, or None when its rows are missing or stale (MissingInput, StaleInput):
    a variant not run, or run against another anchor, prints `--`, never a stale value. Anything else raises. """
    try:
        return slopes(turnout, sample, reading, spec, betaRule, relations = ROBUST)
    except (D.MissingInput, D.StaleInput):
        return None


def oecd26Robustness(sample = None, reading = None):
    r""" The slopes of the design relations (ROBUST) in layers 1 and 2 under each cost transported (the U.S. λ, or
    its ε with λ_n = ε Π_n/R_n) and β rule (ROBUSTVARIANTS), one panel per turnout, the data's slopes on top of each
    panel. A variant whose rows are missing or stale prints `--`. The data's slopes are the same in every variant
    of a turnout (one set of countries), which is checked. """
    v = variant(sample = sample, reading = reading)
    _check(v)
    ncol = 1 + 2*len(ROBUST)
    body, counts = [], {}
    for turnout in TURNOUTTEX:
        res = {sb: _variantSlopes(turnout, v['sample'], v['reading'], *sb) for sb in ROBUSTVARIANTS}
        got = [r for r in res.values() if r is not None]
        data = None
        if got:
            data = got[0].set_index(['y', 'x'])['data']
            for r in got[1:]:
                other = r.set_index(['y', 'x'])['data']
                if any(abs(other[k]['slope'] - data[k]['slope']) > 1e-12 or other[k]['n'] != data[k]['n']
                       for k in ROBUST):
                    raise ValueError('OECD26_Robustness: the data slopes differ across the variants of turnout {}'
                                     .format(turnout))
            counts[turnout] = (got[0].attrs['n'], got[0].attrs['dropped'])
        title = TURNOUTTEX[turnout] + ('' if data is None else ', {} countries'.format(counts[turnout][0]))
        body.append(r'\multicolumn{%d}{l}{\textit{%s}} \\' % (ncol, title))
        cells = [r'\multicolumn{2}{c}{' + ('--' if data is None else _cell(data[k])) + '}' for k in ROBUST]
        body.append(keyed(' & '.join(['Data'] + cells) + r' \\', turnout + '_data'))
        for sb in ROBUSTVARIANTS:
            r = res[sb]
            paper = (turnout, sb[0], sb[1]) == (PAPER['turnout'], PAPER['spec'], PAPER['betaRule'])
            if r is None:
                cells = ['--']*(2*len(ROBUST))
            else:
                t = r.set_index(['y', 'x'])
                cells = [_cell(t.loc[k, 'layer{}'.format(L)]) for k in ROBUST for L in (1, 2)]
            body.append(keyed(' & '.join([VARIANTTEX[sb] + (r'$^{\ast}$' if paper else '')] + cells) + r' \\',
                              '_'.join((turnout,) + sb)))
    design = ('the design chosen in 2020' if v['reading'] == 'chosen' else
              'the design in force in 2020 on the freely simulated path, chosen in 1990')
    names = D.oecdFigure1Data()['country']
    dropped = [names[c] for c in sorted({c for n, d in counts.values() for c in d})]
    note = (r'\textit{Note:} Least-squares slopes with standard errors in parentheses; the regressors are those of '
            r'figure \ref{fig:US:OECDdata}, the model\textquotesingle s index is $1/(2-\theta)$ of ' + design
            + r', and its spending is $\tau(1-\alpha)$ at the observed design. Rows: the cost parameter carried from '
            r'the U.S.\ anchor to every country, its $\lambda$ or its $\varepsilon$ with '
            r'$\lambda_n = \varepsilon\,\Pi_{n,2020}/R_{n,2020}$, and $\beta$, the U.S.\ value in every country '
            r'(common $\beta$) or set so that each country\textquotesingle s 2020 return is the U.S.\ one (common '
            r'$R$, with $\beta$ and $\omega$ calibrated together in layer 2). Own turnout: every '
            r'country\textquotesingle s propensities to vote from the CSES, the U.S.\ anchor recalibrated at its '
            r'own CSES profile' + (' (' + ', '.join(dropped) + ', with no CSES election, left out)' if dropped else '')
            + r'. $^{\ast}$The paper\textquotesingle s specification. --: not computed.')
    header = (' & ' + ' & '.join(r'\multicolumn{2}{c}{\textbf{' + SHORT[k] + '}}' for k in ROBUST) + r' \\' + '\n'
              + ''.join(r'\cmidrule(lr){%d-%d}' % (2 + 2*i, 3 + 2*i) for i in range(len(ROBUST))) + '\n'
              + r'\textbf{Cost, rule} & ' + ' & '.join(['Layer 1', 'Layer 2']*len(ROBUST)))
    sfx = suffix(sample = sample, reading = reading)
    return _xwrap('OECD26_Robustness' + sfx,
                  'results/oecd26/layer1.csv, layer2.csv, anchor.csv; data/oecdFigure1.csv, oecd26_sample.csv',
                  r'The design relations under other maintained assumptions' + variantCaption(sample = sample,
                                                                                              reading = reading),
                  'table:OECD26:robustness' + sfx, 'l' + 'Y'*(2*len(ROBUST)), header, '\n'.join(body), note,
                  width = r'\textwidth', size = r'\footnotesize\setlength{\tabcolsep}{3pt}')


# The three economies of the deep test: usCalibrationSummary's key, the cross-section's ISO3, the label.
RECONCILE = (('US', 'USA', r'U.S.'), ('UK', 'GBR', 'UK'), ('FR', 'FRA', 'France'))
RECONCILESPECS = ('none', 'size', 'sizePiR')


def _anchorAndLayer2(turnout, spec):
    """ (anchor, layer 2) of the cross-section at `turnout`, `spec` and the β rule 'common', or (None, None) when
    either is missing or stale. """
    try:
        return D.oecd26Anchor(turnout, spec), D.oecd26Layer(2, turnout, spec, 'common')
    except (D.MissingInput, D.StaleInput):
        return None, None


def oecd26Reconcile(turnout = None, reading = None):
    r""" The U.S., the UK and France measured twice: as in the deep test (each country's own calibration, the U.S. in
    section 6 and the UK and France in appendix F, usCalibrationSummary.csv: θ*, ν_2020 and ω without the cost; the
    test of the UK and France,
    escCountry{,Costs}.csv, and the U.S. cost calibrations, escCalibration{,Costs}.csv: Ṽ, ω and the design chosen
    at the U.S. λ and ε) and as in the cross-section (results/oecd26: the anchor for the U.S., layer 2 at the β rule
    'common' for the UK and France, at `turnout`, under no cost, λ and ε). The U.S.'s chosen design is the one its
    cost is calibrated to re-elect (the deep test's θ*) and the anchor's. `--` where a quantity is not on file. """
    v = variant(turnout = turnout, reading = reading)
    _check(v)
    col = READINGS[v['reading']]
    summ = D.usCalibrationSummary()
    lack = [c for c, _, _ in RECONCILE if c not in summ]
    if lack:
        raise D.MissingInput(os.path.join(C.PAPERDIR, 'usCalibrationSummary.csv') + ' (no {} row)'.format(lack))
    esc = {}
    for spec in ('size', 'sizePiR'):
        try:
            cal, cty = D.escCalibrationLOG(spec), D.escCountry(spec = spec)
        except D.MissingInput:
            continue
        if abs(float(cal['θStar']) - float(summ['US']['θ'])) > 1e-6:
            raise ValueError('OECD26_Reconcile: the {} cost calibration has θ* {} where usCalibrationSummary.csv has '
                             '{}: a stale calibration'.format(spec, cal['θStar'], summ['US']['θ']))
        us = cty[cty['wedgeFrom'] == 'US'].set_index('country')
        esc[spec] = {'US': {'Vtilde': cal['Vtilde'], 'ω': cal['ω'], 'chosen': cal['θStar']}}
        for c in ('UK', 'FR'):
            if c in us.index:
                r = us.loc[c]
                esc[spec][c] = {'Vtilde': r['Vtilde'], 'ω': r['ω'], 'chosen': r['choice']}
    cross = {spec: _anchorAndLayer2(v['turnout'], spec) for spec in RECONCILESPECS}

    def deep(c, q, spec = None):
        """ The deep test's `q` of country `c`: from usCalibrationSummary.csv (θ, ν2020; ω without the cost) or
        from the cost calibration and the country test of `spec` (any spec on file for Ṽ, which is data). """
        if q in ('θ', 'ν2020'):
            return float(summ[c][q])
        if spec == 'none':
            return float(summ[c]['ω'])
        for s in ([spec] if spec else ['size', 'sizePiR']):
            x = esc.get(s, {}).get(c, {}).get(q, np.nan)
            if x == x:
                return float(x)
        return None

    def crossCell(iso, q, spec = None):
        """ The cross-section's `q` of `iso`: the anchor's for the U.S., layer 2's otherwise, under `spec` (the
        first on file of the paper's, 'size', 'none' for the data columns, the same under every spec). """
        for s in ([spec] if spec else [v['spec'], 'size', 'none']):
            a, lay = cross[s]
            if a is None:
                continue
            r = a if iso == 'USA' else (lay.loc[iso].to_dict() if iso in lay.index else {})
            x = r.get(q, np.nan)
            if x == x:
                return float(x)
        return None

    rows = [('theta', r'$\theta$ observed', 3, lambda c: deep(c, 'θ'), lambda i: crossCell(i, 'θData')),
            ('vtilde', r'$\tilde V$', 3, lambda c: deep(c, 'Vtilde'), lambda i: crossCell(i, 'Vtilde')),
            ('nu', r'$\nu_{2020}$', 2, lambda c: deep(c, 'ν2020'), lambda i: crossCell(i, 'ν2020')),
            ('omega_none', r'$\omega$, no cost', 3, lambda c: deep(c, 'ω', 'none'),
             lambda i: crossCell(i, 'ω', 'none'))]
    for spec, sym in (('size', r'\lambda'), ('sizePiR', r'\varepsilon')):
        rows += [('omega_' + spec, r'$\omega$, U.S.\ $' + sym + '$', 3,
                  lambda c, s = spec: deep(c, 'ω', s), lambda i, s = spec: crossCell(i, 'ω', s)),
                 ('chosen_' + spec, r'$\theta$ chosen, U.S.\ $' + sym + '$', 3,
                  lambda c, s = spec: deep(c, 'chosen', s), lambda i, s = spec: crossCell(i, col, s))]
    fmt = lambda x, d: '--' if x is None else C.num(x, d)
    body = [keyed(' & '.join([label] + [fmt(fd(c), d) for c, _, _ in RECONCILE]
                             + [fmt(fc(i), d) for _, i, _ in RECONCILE]) + r' \\', key)
            for key, label, d, fd, fc in rows]
    n = len(RECONCILE)
    header = (r' & \multicolumn{%d}{c}{\textbf{Deep test}} & \multicolumn{%d}{c}{\textbf{Cross-section}} \\' % (n, n)
              + '\n' + r'\cmidrule(lr){2-%d}\cmidrule(lr){%d-%d}' % (1 + n, 2 + n, 1 + 2*n) + '\n'
              + ' & '.join([''] + [r'\textbf{' + name + '}' for _, _, name in RECONCILE]*2))
    design = ('chosen in 2020' if v['reading'] == 'chosen' else 'in force in 2020, chosen in 1990,')
    note = (r'\textit{Note:} Deep test: each country\textquotesingle s own calibration, the U.S.\ in section '
            r'\ref{sec:oecd} and the UK and France in appendix \ref{app:US} ($\theta$, $\nu_{2020}$ and $\omega$ '
            r'without the cost), and $\tilde V$, $\omega$ and the design chosen at the U.S.\ $\lambda$ and '
            r'$\varepsilon$ from the test of table \ref{table:US_ESC:country}; for the U.S.\ from the calibration of '
            r'its cost, which re-elects its observed design. Cross-section: the OECD '
            r'data of appendix \ref{app:oecd26}, the U.S.\ anchor and the second layer, $\omega$ calibrated to each '
            r'country\textquotesingle s spending at the U.S.\ $\beta$ and cost parameter'
            + (r', each country at its own turnout' if v['turnout'] == 'cses' else '')
            + r'. The design chosen is the one ' + design + r' on the freely simulated path; under $\varepsilon$, '
            r'$\lambda_n = \varepsilon\,\Pi_{n,2020}/R_{n,2020}$. --: not computed.')
    sfx = suffix(turnout = turnout, reading = reading)
    return _xwrap('OECD26_Reconcile' + sfx,
                  'results/paper/usCalibrationSummary.csv; results/esc/escCalibration{,Costs}.csv, '
                  'escCountry{,Costs}.csv; results/oecd26/anchor.csv, layer2.csv',
                  r'The U.S., the UK and France in the deep test and in the cross-section'
                  + variantCaption(turnout = turnout, reading = reading),
                  'table:OECD26:reconcile' + sfx, 'l' + 'Y'*(2*n), header, '\n'.join(body), note,
                  width = r'\textwidth')
