r""" The cross-country test of section 7's model (python/US/runOECD26.py, results/oecd26/): the panel data shared
with figuresOECD26, the slopes of figure 1.1's relations in the data and in the model (all five, OECD26_Slopes; the
two of section 6's spending test at the observed designs without the cost, spendingSlopes), the calibrated political
weights (OECD26_Omega), and the five slopes under each measure of the design (OECD26_ThetaVariants).

THE DESIGN'S MEASURE (`theta`, config.US['theta'] by default): the data side's index is I = 1/(2 - θ) of that variant
of data/oecd26_theta.csv and its spending the variant's, on its countries (datasets.oecd26SampleOf: inSample and a
finite θ); the model's rows are the variant's (datasets.oecd26Dir). `theta` 'paper' is figure 1.1's index on
data/oecd26_sample.csv's sample26, with the 'index' rows of results/oecd26/.

Every builder takes
  turnout  'cps' (every economy at the U.S. CPS propensities to vote) | 'cses' (each its own; Luxembourg has none
           and drops out of data and model alike);
  sample   '26', the sample of the design's measure (above);
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
import os, re
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
# The design's measure as the notes state it: config.US['theta']'s, θ the slope of public pension benefits on
# earnings (notes/thetaTau_alternatives.md, variant C), and the index on figure 1.1's scale.
MEASURENOTE = (r'$\theta$, the least-squares slope of the public pension on earnings at 0.5, 1 and 2 times average '
               r'earnings, times one minus the share of spending on minimum top-ups and tested benefits, and '
               r'$I = 1/(2-\theta)$, the Bismarckian index.')


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
    if (v['turnout'] not in ('cps', 'cses') or v['sample'] != '26' or v['reading'] not in READINGS
            or v['spec'] not in SPECCAPTION or v['betaRule'] not in BETACAPTION):
        raise ValueError('turnout cps|cses, sample 26, reading chosen|inForce, spec size|sizePiR|none, betaRule '
                         'common|commonR; got {}'.format(v))


def dataSide(theta = None):
    """ (countries, index, spending) of the data side under the design's measure `theta` (module docstring): figure
    1.1's order, I and spending (% of GDP) as Series on ISO3. """
    theta = C.US['theta'] if theta is None else theta
    fig = D.oecdFigure1Data()
    if theta == 'paper':
        smp = D.oecd26Sample()
        return ([c for c in fig.index if bool(smp.at[c, 'sample26'])], fig[F1.NAMED['index']].astype(float),
                fig[F1.NAMED['spending']].astype(float))
    t = D.thetaVariant(theta)
    return D.oecd26SampleOf(theta), t['index'].astype(float), t['spending'].astype(float)


def panelData(layer, turnout = None, sample = None, reading = None, spec = None, betaRule = None, theta = None):
    r""" One row per country of the sample with a model row: figure 1.1's x variables (`growth`, `gini`), the
    data's `spendingData`, `indexData` under the design's measure `theta` (dataSide), and the model's `spendingModel`,
    `θModel`, `indexModel` = 1/(2 - θ), from layer `layer` (1 | 2) of that measure. Countries whose model row is
    'noTurnout' (cses) are dropped from both sides and listed in `.attrs['dropped']`; a sample country with no row is
    MissingInput, a failed row an error. """
    v = variant(turnout, sample, reading, spec, betaRule)
    _check(v)
    theta = C.US['theta'] if theta is None else theta
    fig = D.oecdFigure1Data()
    smp = D.oecd26Sample()
    model = D.oecd26Layer(layer, v['turnout'], v['spec'], v['betaRule'], 'index' if theta == 'paper' else theta)
    isos, index, spending = dataSide(theta)
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
                        'spendingData': spending.loc[keep], 'indexData': index.loc[keep],
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
           layers = (1, 2), theta = None):
    """ One row per relation of `relations` (RELATIONS by default): OLS of the data and of each layer of `layers`
    (`data`, `layer1`, `layer2`, each an ols dict, None for a layer not asked for), on the countries every layer
    asked for covers, under the design's measure `theta` (panelData). Layer 2 matches spending by construction, so its
    spending-on-regressor rows are flagged `targeted2`. Under spec 'none' no row has a design: ask for the spending
    relations only (SPENDING). """
    ps = {k: panelData(k, turnout, sample, reading, spec, betaRule, theta) for k in layers}
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


def _cell(o, digits = 2, stack = False):
    r""" A slope and its standard error; `stack` puts the error on a line of its own (\newline), so that every cell of
    a narrow column breaks alike. """
    return '$' + C.num(o['slope'], digits) + '$' + (r'\newline' if stack else ' ') + '$(' + C.num(o['se'], digits) + ')$'


def _dashNote(body):
    r""" The note's key to `--`, only when a cell of `body` (rows of a table) prints one. """
    return ' --: not computed.' if any(re.search(r'(&\s*--\s*(&|\\\\))|\{--\}', b) for b in body) else ''


def _layersText(a, v, matches = True):
    r""" The note's sentence on what the layers share with the anchor `a` and what layer 2 calibrates, at the
    variant `v`; `matches` adds that layer 2 then matches spending. """
    items = ([r'$\beta = ' + C.num(float(a['β']), 2) + '$'] if v['betaRule'] == 'common' else []) \
        + [r'$\omega = ' + C.num(float(a['ω']), 2) + '$'] \
        + ([COSTSYMBOL[v['spec']][:-1] + ' = ' + C.num(float(a['p']), 2) + '$'] if v['spec'] in COSTSYMBOL else [])
    shared = items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]
    tail = {'size': '', 'none': ', without the cost',
            'sizePiR': r', each at its cost $\lambda_{n,t} = \varepsilon\,\Pi_{n,t}/R_{n,t}$'}[v['spec']] \
        + (r', with the $\beta$ that sets its 2020 return to the U.S.\ one' if v['betaRule'] == 'commonR' else '')
    calibrated = r'$\omega$' if v['betaRule'] == 'common' else r'$\beta$ and $\omega$'
    return (r'Layer 1: every country at the U.S.\ ' + shared + tail + '; layer 2: ' + calibrated
            + r' calibrated to each country\textquotesingle s spending'
            + (r' and the U.S.\ 2020 return' if v['betaRule'] == 'commonR' else '')
            + (', which it then matches.' if matches else '.'))


def oecd26Slopes(turnout = None, sample = None, reading = None, spec = None, betaRule = None):
    r""" The slopes of figure 1.1's relations: the data on the sample, the model with the U.S. political weight
    and cost (layer 1) and with each country's own political weight (layer 2). """
    v = variant(turnout, sample, reading, spec, betaRule)
    s = slopes(**v)
    a = D.oecd26Anchor(v['turnout'], v['spec'])
    body = []
    for _, r in s.iterrows():
        label = YTEX[r['y']] + ' on ' + XTEX[r['x']]
        cells = [label, _cell(r['data'], stack = True), _cell(r['layer1'], stack = True),
                 r'\textit{targeted}' if r['targeted2'] else _cell(r['layer2'], stack = True)]
        body.append(' & '.join(cells) + r' \\ % row: ' + rowKey(r['y'] + '_' + r['x']))
    design = (r' The model\textquotesingle s index is that of the design chosen in 2020, which binds from 2050.'
              if v['reading'] == 'chosen' else '')
    dropped = s.attrs['dropped']
    note = (r'\textit{Note:} Least-squares slopes with standard errors in parentheses, ' + str(s.attrs['n'])
            + ' countries' + (' (without ' + ', '.join(dropped) + ', which has no turnout data)' if dropped else '')
            + r'. The regressors are those of figure \ref{fig:US:OECDdata} in data and model alike.' + design + ' '
            + _layersText(a, v, matches = False)
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
    head, join = ((r'$\omega$ is calibrated to spending at $\beta = ' + C.num(float(a['β']), 2) + '$', ' and ')
                  if v['betaRule'] == 'common' else
                  (r'$\beta$ and $\omega$ are calibrated to the U.S.\ 2020 return and to spending', ' at '))
    cost = {'size': join + r'the U.S.\ $\lambda = ' + C.num(float(a['p']), 2) + '$',
            'sizePiR': join + r'the U.S.\ $\varepsilon = ' + C.num(float(a['p']), 2)
                       + r'$, $\lambda_{n,t} = \varepsilon\,\Pi_{n,t}/R_{n,t}$',
            'none': ', without the cost'}[v['spec']]
    anchor = (r' $^{\ast}$The U.S.\ is the anchor, where ' + COSTSYMBOL[v['spec']] + ' is calibrated.'
              if v['spec'] in COSTSYMBOL else r' $^{\ast}$The U.S.\ is the anchor.')
    note = (r'\textit{Note:} $\nu_{2020}$, workers per retiree; $\tilde V$, the dispersion of relative incomes at '
            r'the U.S.\ income percentiles; spending in \% of GDP; ' + MEASURENOTE + ' ' + head + cost + r'; the last two columns are the '
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
# The five slopes under each measure of the design (OECD26_ThetaVariants): the paper's index and the variants of
# data/oecd26_theta.csv, at both turnouts.
MEASURES = ('paper', 'A', 'A2pt', 'B', 'C')
MEASURETEX = {'paper': r'Figure \ref{fig:US:OECDdata}\textquotesingle s index', 'A': 'A', 'A2pt': 'A, two points',
              'B': 'B', 'C': 'C'}
TURNOUTTEX = {'cps': r'U.S.\ turnout', 'cses': r'Own turnout'}


def _measureSlopes(measure, turnout):
    """ slopes() of RELATIONS at the paper's variant of the cross-section under `measure` (MEASURES; 'paper' the rows of
    figure 1.1's index), or None while its rows are missing or stale (MissingInput, StaleInput): `--`, never a stale
    value. Anything else raises. """
    try:
        return slopes(turnout, theta = measure)
    except (D.MissingInput, D.StaleInput):
        return None


def oecd26ThetaVariants():
    r""" The slopes of figure 1.1's relations (OECD26_Slopes's five) in the data and in layers 1 and 2 under each
    measure of the design (MEASURES): figure 1.1's index (results/oecd26/, thetaSource 'index', on the paper's
    sample of data/oecd26_sample.csv) and the variants of data/oecd26_theta.csv, each on its own in-sample countries,
    the data's index 1/(2 - θ) of the variant and its spending; config.US['theta']'s from results/oecd26/, the others
    from results/oecd26_theta_<V>/ (stage (ii)'s oecd26Variants). One panel per turnout. A measure whose rows are
    missing or stale prints `--`. """
    ncol = 1 + 3*len(TURNOUTTEX)
    res = {(m, t): _measureSlopes(m, t) for m in MEASURES for t in TURNOUTTEX}
    body = []
    for yRole, xRole in RELATIONS:
        body.append(r'\multicolumn{%d}{l}{\textit{%s}} \\' % (ncol, YTEX[yRole] + ' on ' + XTEX[xRole]))
        for m in MEASURES:
            cells = [MEASURETEX[m] + (r'$^{\ast}$' if m == C.US['theta'] else '')]
            for t in TURNOUTTEX:
                r = res[(m, t)]
                if r is None:
                    cells += ['--']*3
                    continue
                row = r.set_index(['y', 'x']).loc[(yRole, xRole)]
                cells += [_cell(row['data']), _cell(row['layer1']),
                          r'\textit{targeted}' if row['targeted2'] else _cell(row['layer2'])]
            body.append(keyed(' & '.join(cells) + r' \\', '_'.join((yRole, xRole, m))))
    ns = ', '.join('{} {}'.format(MEASURETEX[m] if m != 'paper' else 'the index', res[(m, 'cps')].attrs['n'])
                   for m in MEASURES if res[(m, 'cps')] is not None)
    note = (r'\textit{Note:} Least-squares slopes with standard errors in parentheses, the regressors those of figure '
            r'\ref{fig:US:OECDdata}. Each measure of the design $\theta$ is its own cross-section: the data\textquotesingle s '
            r'index $1/(2-\theta)$ and spending under it, on its countries'
            + (r' (at U.S.\ turnout: ' + ns + ')' if ns else '')
            + r', and the model calibrated to them, the U.S.\ anchor included. Layer 1: every country at its '
            r'anchor\textquotesingle s $\beta$, $\omega$ and $\varepsilon$, at its cost '
            r'$\lambda_{n,t} = \varepsilon\,\Pi_{n,t}/R_{n,t}$; layer 2: $\omega$ calibrated to each '
            r'country\textquotesingle s spending. Own turnout: every country\textquotesingle s CSES propensities to '
            r'vote, the anchor recalibrated at its own. $^{\ast}$The paper\textquotesingle s measure.' + _dashNote(body))
    header = (' & ' + ' & '.join(r'\multicolumn{3}{c}{\textbf{' + TURNOUTTEX[t] + '}}' for t in TURNOUTTEX) + r' \\'
              + '\n' + ''.join(r'\cmidrule(lr){%d-%d}' % (2 + 3*i, 4 + 3*i) for i in range(len(TURNOUTTEX))) + '\n'
              + r'\textbf{Measure} & ' + ' & '.join(['Data', 'Layer 1', 'Layer 2']*len(TURNOUTTEX)))
    return _xwrap('OECD26_ThetaVariants',
                  'results/oecd26/, results/oecd26_theta_<V>/ layer1.csv, layer2.csv, anchor.csv; data/oecd26_theta.csv, '
                  'oecdFigure1.csv, oecd26_sample.csv',
                  r'Figure \ref{fig:US:OECDdata}\textquotesingle s relations under each measure of the design',
                  'table:OECD26:thetaVariants', 'l' + 'Y'*(3*len(TURNOUTTEX)), header, '\n'.join(body), note,
                  width = r'\textwidth', size = r'\footnotesize\setlength{\tabcolsep}{3pt}')
