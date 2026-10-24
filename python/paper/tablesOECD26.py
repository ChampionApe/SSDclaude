r""" The cross-country test of section 7's model (python/US/runOECD26.py, results/oecd26/): the panel data shared
with figuresOECD26, the slopes of figure 1.1's relations in the data and in the model, and the calibrated
political weights.

Every builder takes
  turnout  'cps' (every economy at the U.S. CPS propensities to vote, the paper's) | 'cses' (each its own,
           the online appendix's; Luxembourg has none and drops out of data and model alike);
  sample   '26' (data/oecd26_sample.csv's sample26, the paper's) | '29' (figure 1.1's countries);
  reading  'chosen' (the design chosen in 2020 at the observed design, in force in 2050) | 'inForce' (the
           design in force in 2020 on the freely simulated path, appendix G.1's reading).
The model's design enters every regression on the index's scale, I = 1/(2 - θ), the inverse of the loader's
θ = 2 - 1/I; spending is 100 τ (1 - α), % of GDP, the inverse of the calibration's τ0. Both sides of every
slope use figure 1.1's regressors (OECD population growth 2020/1990, the WIID Gini) and the same countries.
"""
import numpy as np, pandas as pd

import config as C
import datasets as D
import oecdFigure1 as F1
from tables import rowKey
from tablesUS import _xwrap

# Figure 1.1's panels in its order, (y role, x role); the x role 'index' is the design on the index scale.
RELATIONS = (('spending', 'growth'), ('spending', 'gini'), ('spending', 'index'),
             ('index', 'growth'), ('index', 'gini'))
READINGS = {'chosen': 'θChosen', 'inForce': 'θInForce'}
YTEX = {'spending': 'Pension spending', 'index': 'Bismarckian index'}
XTEX = {'growth': 'population growth', 'gini': 'the Gini', 'index': 'the Bismarckian index'}


def suffix(turnout = 'cps', sample = '26', reading = 'chosen'):
    r""" '' for the paper's variant; otherwise the parts that differ, e.g. '_cses_29'. Appended to an output's
    name and \label. """
    return ('' if turnout == 'cps' else '_' + turnout) + ('' if sample == '26' else '_' + sample) \
        + ('' if reading == 'chosen' else '_' + reading)


def _check(turnout, sample, reading):
    if turnout not in ('cps', 'cses') or sample not in ('26', '29') or reading not in READINGS:
        raise ValueError('turnout cps|cses, sample 26|29, reading chosen|inForce; got {!r}, {!r}, {!r}'
                         .format(turnout, sample, reading))


def panelData(layer, turnout = 'cps', sample = '26', reading = 'chosen'):
    r""" One row per country of the sample with a model row: figure 1.1's x variables (`growth`, `gini`), the
    data's `spendingData`, `indexData`, and the model's `spendingModel`, `θModel`, `indexModel` = 1/(2 - θ),
    from layer `layer` (1 | 2). Countries whose model row is 'noTurnout' (cses) are dropped from both sides and
    listed in `.attrs['dropped']`; a sample country with no row is MissingInput, a failed row an error. """
    _check(turnout, sample, reading)
    fig = D.oecdFigure1Data()
    smp = D.oecd26Sample()
    model = D.oecd26Layer(layer, turnout)
    isos = [c for c in fig.index if sample == '29' or bool(smp.at[c, 'sample26'])]
    lack = [c for c in isos if c not in model.index]
    if lack:
        raise D.MissingInput('{} (layer {}, {}: no row for {})'.format(D.oecd26Path(layer), layer, turnout,
                                                                       ', '.join(lack)))
    m = model.loc[isos]
    bad = m.index[~m['status'].isin(['ok', 'noTurnout'])]
    if len(bad):
        raise ValueError('layer {} ({}): failed rows for {}'.format(layer, turnout, ', '.join(bad)))
    moved = [c for c in isos if bool(m.at[c, 'sample26']) != bool(smp.at[c, 'sample26'])]
    if moved:
        raise ValueError('layer {} ({}): sample26 differs from data/oecd26_sample.csv for {}: rerun the layer'
                         .format(layer, turnout, ', '.join(moved)))
    dropped = list(m.index[m['status'] == 'noTurnout'])
    keep = [c for c in isos if c not in dropped]
    θ = m.loc[keep, READINGS[reading]].astype(float)
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


def slopes(turnout = 'cps', sample = '26', reading = 'chosen'):
    """ One row per relation of RELATIONS: OLS of the data and of layers 1 and 2 (`data`, `layer1`, `layer2`,
    each an ols dict), on the countries both layers cover. Layer 2 matches spending by construction, so its
    spending-on-regressor rows are flagged `targeted2`. """
    p1, p2 = panelData(1, turnout, sample, reading), panelData(2, turnout, sample, reading)
    common = p1.index.intersection(p2.index)
    p1, p2 = p1.loc[common], p2.loc[common]
    rows = []
    for yRole, xRole in RELATIONS:
        rows.append({'y': yRole, 'x': xRole, 'data': ols(*_xy(p1, yRole, xRole, 'Data')),
                     'layer1': ols(*_xy(p1, yRole, xRole, 'Model')), 'layer2': ols(*_xy(p2, yRole, xRole, 'Model')),
                     'targeted2': yRole == 'spending' and xRole != 'index'})
    out = pd.DataFrame(rows)
    out.attrs.update({'n': len(common), 'dropped': p1.attrs['dropped']})
    return out


def _cell(o, digits = 2):
    return '$' + C.num(o['slope'], digits) + '$ $(' + C.num(o['se'], digits) + ')$'


def oecd26Slopes(turnout = 'cps', sample = '26', reading = 'chosen'):
    r""" The slopes of figure 1.1's relations: the data on the sample, the model with the U.S. political weight
    and cost (layer 1) and with each country's own political weight (layer 2). """
    s = slopes(turnout, sample, reading)
    a = D.oecd26Anchor(turnout)
    body = []
    for _, r in s.iterrows():
        label = YTEX[r['y']] + ' on ' + XTEX[r['x']]
        cells = [label, _cell(r['data']), _cell(r['layer1']),
                 r'\textit{targeted}' if r['targeted2'] else _cell(r['layer2'])]
        body.append(' & '.join(cells) + r' \\ % row: ' + rowKey(r['y'] + '_' + r['x']))
    design = (r'the design chosen in 2020, which binds from 2050' if reading == 'chosen' else
              r'the design in force in 2020 on the freely simulated path')
    dropped = s.attrs['dropped']
    note = (r'\textit{Note:} Least-squares slopes with standard errors in parentheses, ' + str(s.attrs['n'])
            + ' countries' + (' (without ' + ', '.join(dropped) + ', which has no turnout data)' if dropped else '')
            + r'. The regressors are those of figure \ref{fig:US:OECDdata} in data and model alike; the model\textquotesingle s '
            r'index is $1/(2-\theta)$ of ' + design + r', and its spending is $\tau(1-\alpha)$ at the observed '
            r'design. Layer 1: every country at the U.S.\ $\beta = ' + C.num(float(a['β']), 3) + r'$, $\omega = '
            + C.num(float(a['ω']), 3) + r'$ and $\lambda = ' + C.num(float(a['p']), 3) + r'$; layer 2: $\omega$ '
            r'calibrated to each country\textquotesingle s spending, which it then matches.'
            + (r' Turnout: each country\textquotesingle s own.' if turnout == 'cses' else ''))
    name = 'OECD26_Slopes' + suffix(turnout, sample, reading)
    return _xwrap(name, 'results/oecd26/layer1.csv, layer2.csv, anchor.csv; data/oecdFigure1.csv, oecd26_sample.csv',
                  r'Figure \ref{fig:US:OECDdata}\textquotesingle s relations in the data and in the model',
                  'table:OECD26:slopes' + suffix(turnout, sample, reading), 'lYYY',
                  [r'\textbf{Relation}', r'\textbf{Data}', r'\textbf{Layer 1}', r'\textbf{Layer 2}'],
                  '\n'.join(body), note, width = r'\textwidth')


def oecd26Omega(turnout = 'cps', sample = '26', reading = 'chosen'):
    r""" Layer 2 by country: the inputs that differ across countries (workers per retiree in 2020, the dispersion
    of relative incomes, spending, the index and the design it implies), the calibrated political weight and the
    design predicted at the U.S. cost, in the order of figure 1.1's footnote. """
    _check(turnout, sample, reading)
    p = panelData(2, turnout, sample, reading)
    m = D.oecd26Layer(2, turnout).loc[p.index]
    a = D.oecd26Anchor(turnout)
    body = []
    for c in p.index:
        r = m.loc[c]
        cells = [str(p.at[c, 'country']) + (r'$^{\ast}$' if c == 'USA' else ''), C.num(float(r['ν2020']), 2),
                 C.num(float(r['Vtilde']), 3), C.num(float(r['spendingData']), 1), C.num(float(r['indexData']), 3),
                 C.num(float(r['θData']), 3), C.num(float(r['ω']), 3), C.num(float(p.at[c, 'θModel']), 3),
                 C.num(float(p.at[c, 'indexModel']), 3)]
        body.append(' & '.join(cells) + r' \\ % row: ' + c.lower())
    design = 'chosen in 2020' if reading == 'chosen' else 'in force in 2020'
    note = (r'\textit{Note:} $\nu_{2020}$, workers per retiree; $\tilde V$, the dispersion of relative incomes at '
            r'the U.S.\ income percentiles; spending in \% of GDP; $I$, the Bismarckian index, and $\theta = 2 - 1/I$ '
            r'clipped to $[0,1]$. $\omega$ is calibrated to spending at $\beta = ' + C.num(float(a['β']), 3)
            + r'$ and the U.S.\ $\lambda = ' + C.num(float(a['p']), 3) + r'$; the last two columns are the design '
            + design + r' and its index. $^{\ast}$The U.S.\ is the anchor, where $\lambda$ is calibrated.'
            + (r' Turnout: each country\textquotesingle s own.' if turnout == 'cses' else ''))
    header = [r'\textbf{Country}', r'$\nu_{2020}$', r'$\tilde V$', r'\textbf{Spending}', '$I$', r'$\theta$',
              r'$\omega$', r'$\theta$ \textbf{chosen}', r'$I$ \textbf{chosen}']
    name = 'OECD26_Omega' + suffix(turnout, sample, reading)
    return _xwrap(name, 'results/oecd26/layer2.csv, anchor.csv; data/oecdFigure1.csv, oecd26_sample.csv',
                  r'The countries of the cross-country test, each calibrated to its pension spending',
                  'table:OECD26:omega' + suffix(turnout, sample, reading), 'l' + 'Y'*(len(header) - 1), header,
                  '\n'.join(body), note, width = r'\textwidth', size = r'\footnotesize')
