r""" The cross-country test of section 7's model (python/US/runOECD26.py, results/oecd26/): the panel data shared
with figuresOECD26, the slopes of figure 1.1's relations in the data and in the model (all five, OECD26_Slopes; the
two of section 6's spending test at the observed designs without the cost, spendingSlopes), the calibrated political
weights (OECD26_Omega), the five slopes under each measure of the design (OECD26_ThetaVariants), the predicted against
the observed design (thetaFit, figuresOECD26's OECD26_ThetaFit*), and appendix H's stylized readings (OECD26_Stylized,
results/oecd26_stylized/).

THE DESIGN'S MEASURE (`theta`, config.US['theta'] by default): the data side's index is I = 1/(2 - θ) of that variant
of data/oecd26_theta.csv and its spending the variant's, on its countries (datasets.oecd26SampleOf: inSample and a
finite θ); the model's rows are the variant's (datasets.oecd26Dir). `theta` 'paper' is figure 1.1's index on
data/oecd26_sample.csv's sample26, with the 'index' rows of results/oecd26/.

Every builder takes
  turnout  'cses' (each economy at its own CSES propensities to vote; Luxembourg has none and drops out of data and
           model alike) | 'cps' (every economy at the U.S. CPS propensities) | 'pooled' (the stylized reading of
           results/oecd26_stylized/ only: the U.S. at its CSES profile, AUS, BEL, LUX flat, the rest the mean profile);
  sample   '26', the sample of the design's measure (above);
  reading  'inForce' (the design in force in 2020 on the freely simulated path, chosen in 1990: the reading of the
           cost parameter's target) | 'chosen' (the design chosen in 2020 at the observed design, in force from 2050);
  spec     the cost transported from the U.S. anchor: 'sizePiR' (λ_n = ε Π_n/R_n for country n, the anchor's ε in
           the csvs' `p`), 'size' (the anchor's λ) | 'none' (no cost; the model then reads no design);
  betaRule 'common' (the anchor's β in every country) | 'commonR' (each country's β set so that its 2020 return is
           the anchor's);
  spending the model's spending: 'chosen' (100 τInForce (1 - α), the 2020 tax on the path whose design in force is the
           chosen one, = spending2020 τInForce/τ2020; reading 'inForce' and a cost only) | 'observed' (spending2020, the
           tax at the observed design, which layer 2's ω matches by construction);
each None for the paper's variant, PAPER, which is config.US['oecd26']'s (sample '26', spending its
`spendingReading`; under spec 'none' spending is 'observed'). An output's name and label carry the parts that differ
from the paper's variant (`suffix`). The model's design enters every regression on the index's scale, I = 1/(2 - θ),
the inverse of the loader's θ = 2 - 1/I; spending is 100 τ (1 - α), % of GDP, the inverse of the calibration's τ0. Both
sides of every slope use figure 1.1's regressors (OECD population growth 2020/1990, the WIID Gini) and the same
countries.
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
# Section 6's spending test (spendingSlopes, figuresOECD26.oecd26Spending) and the relations of the index
# (OECD26_Stylized), each a subset of RELATIONS.
SPENDING = (('spending', 'growth'), ('spending', 'gini'))
INDEXRELATIONS = (('spending', 'index'), ('index', 'growth'), ('index', 'gini'))
READINGS = {'chosen': 'θChosen', 'inForce': 'θInForce'}
SPENDINGS = ('chosen', 'observed')
TURNOUTS = ('cses', 'cps', 'pooled')
VARIANT = ('turnout', 'sample', 'reading', 'spec', 'betaRule', 'spending')          # suffix's order
PAPER = ({k: C.US['oecd26'][k] for k in ('turnout', 'reading', 'spec', 'betaRule')}
         | {'sample': '26', 'spending': C.US['oecd26']['spendingReading']})
YTEX = {'spending': 'Pension spending', 'index': 'Bismarckian index'}
XTEX = {'growth': 'population growth', 'gini': 'the Gini', 'index': 'the Bismarckian index'}
# What a caption adds for a cost, β rule, turnout or spending other than the paper's.
SPECCAPTION = {'size': r'the U.S.\ $\lambda$ in every country',
               'sizePiR': r'the U.S.\ $\varepsilon$ in every country, $\lambda_n = \varepsilon\,\Pi_n/R_n$',
               'none': 'without the cost'}
BETACAPTION = {'common': r'the U.S.\ $\beta$ in every country',
               'commonR': r'each country\textquotesingle s $\beta$ set to the U.S.\ 2020 return'}
TURNOUTCAPTION = {'cses': 'each country at its own turnout', 'cps': r'every country at the U.S.\ turnout',
                  'pooled': 'the pooled turnout'}
SPENDINGCAPTION = {'chosen': 'spending at the chosen designs', 'observed': 'spending at the observed designs'}
# The notes' sentence on the propensities to vote by income group.
TURNOUTNOTE = {'cses': r'Turnout: each country\textquotesingle s own propensities to vote by income group, from the CSES.',
               'cps': r'Turnout: the U.S.\ propensities to vote by income group, from the CPS, in every country.'}


def compulsoryText(theta = None):
    """ 'Belgium and Luxembourg, which enforce compulsory voting, flat': the compulsory-voting countries of the θ
    variant's sample (datasets.compulsoryVoting), '' where it has none. """
    c = D.compulsoryVoting(theta)
    return '' if not c else _names(c) + (', which enforces' if len(c) == 1 else ', which enforce') \
        + ' compulsory voting, flat'


def turnoutNote(turnout, theta = None):
    """ The notes' sentence on the propensities to vote by income group under `turnout`. """
    if turnout != 'pooled':
        return TURNOUTNOTE[turnout]
    comp = compulsoryText(theta)
    return (r'Turnout: the U.S.\ at its own CSES propensities to vote; ' + (comp + '; ' if comp else '')
            + r'every other country at the mean CSES profile of the countries that vote voluntarily.')
COSTSYMBOL = {'size': r'$\lambda$', 'sizePiR': r'$\varepsilon$'}                # the anchor's `p`
# The design's measure as the notes state it: config.US['theta']'s (config.THETADEF), and the index on figure 1.1's
# scale.
MEASURENOTE = r'$\theta$, ' + C.THETADEF + r', and $I = 1/(2-\theta)$, the Bismarckian index.'


def variant(turnout = None, sample = None, reading = None, spec = None, betaRule = None, spending = None):
    """ The variant as a dict over VARIANT, PAPER's value where None; spending 'observed' under spec 'none', which
    chooses no design. """
    v = dict(zip(VARIANT, (turnout, sample, reading, spec, betaRule, spending)))
    v = {k: PAPER[k] if v[k] is None else v[k] for k in VARIANT}
    if spending is None and v['spec'] == 'none':
        v['spending'] = 'observed'
    return v


def suffix(turnout = None, sample = None, reading = None, spec = None, betaRule = None, spending = None):
    r""" '' for the paper's variant (PAPER); otherwise the parts that differ, e.g. '_cps', '_size_commonR'.
    Appended to an output's name and \label. Under spec 'none' the spending reading is not a part. """
    v = variant(turnout, sample, reading, spec, betaRule, spending)
    return ''.join('_' + v[k] for k in VARIANT if v[k] != PAPER[k] and not (k == 'spending' and v['spec'] == 'none'))


def variantCaption(turnout = None, sample = None, reading = None, spec = None, betaRule = None, spending = None):
    """ What a caption adds for a variant other than the paper's: '' for the paper's own. """
    v = variant(turnout, sample, reading, spec, betaRule, spending)
    parts = ([r'every country of figure \ref{fig:US:OECDdata}'] if v['sample'] != PAPER['sample'] else []) \
        + ([TURNOUTCAPTION[v['turnout']]] if v['turnout'] != PAPER['turnout'] else []) \
        + (['the design chosen in 2020'] if v['reading'] != PAPER['reading'] else []) \
        + ([SPECCAPTION[v['spec']]] if v['spec'] != PAPER['spec'] else []) \
        + ([BETACAPTION[v['betaRule']]] if v['betaRule'] != PAPER['betaRule'] else []) \
        + ([SPENDINGCAPTION[v['spending']]] if v['spending'] != PAPER['spending'] and v['spec'] != 'none' else [])
    return ''.join(', ' + p for p in parts)


def _check(v):
    if (v['turnout'] not in TURNOUTS or v['sample'] != '26' or v['reading'] not in READINGS
            or v['spec'] not in SPECCAPTION or v['betaRule'] not in BETACAPTION or v['spending'] not in SPENDINGS):
        raise ValueError('turnout cses|cps|pooled, sample 26, reading chosen|inForce, spec size|sizePiR|none, betaRule '
                         'common|commonR, spending chosen|observed; got {}'.format(v))
    if v['spending'] == 'chosen' and (v['reading'] != 'inForce' or v['spec'] == 'none'):
        raise ValueError("spending 'chosen' is the tax on the path of the design in force in 2020: reading 'inForce' "
                         "and a cost only; got {}".format(v))


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


def panelData(layer, turnout = None, sample = None, reading = None, spec = None, betaRule = None, theta = None,
              spending = None, omegaRule = 'anchor', root = None):
    r""" One row per country of the sample with a model row: figure 1.1's x variables (`growth`, `gini`), the
    data's `spendingData`, `indexData` and `θData` = 2 - 1/I under the design's measure `theta` (dataSide), and the
    model's `spendingModel` (at the variant's spending reading), `spendingObserved` (spending2020), `θModel`,
    `indexModel` = 1/(2 - θ), from layer `layer` (1 | 2) of that measure; layer 1 at `omegaRule` ('anchor' | 'mean'),
    both from datasets.oecd26Dir(theta, root). Countries whose model row is 'noTurnout' (cses) are dropped from both
    sides and listed in `.attrs['dropped']`; a sample country with no row is MissingInput, a failed row an error. """
    v = variant(turnout, sample, reading, spec, betaRule, spending)
    _check(v)
    theta = C.US['theta'] if theta is None else theta
    fig = D.oecdFigure1Data()
    smp = D.oecd26Sample()
    model = D.oecd26Layer(layer, v['turnout'], v['spec'], v['betaRule'], 'index' if theta == 'paper' else theta,
                          root, omegaRule if layer == 1 else 'anchor')
    isos, index, spend = dataSide(theta)
    lack = [c for c in isos if c not in model.index]
    if lack:
        raise D.MissingInput('{} (layer {}, {} {} {}: no row for {})'.format(
            D.oecd26Path(layer, None if theta == 'paper' else theta, root), layer, v['turnout'], v['spec'],
            v['betaRule'], ', '.join(lack)))
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
    observed = m.loc[keep, 'spending2020'].astype(float)
    model = (observed if v['spending'] == 'observed' else
             observed*m.loc[keep, 'τInForce'].astype(float)/m.loc[keep, 'τ2020'].astype(float))
    out = pd.DataFrame({'country': fig.loc[keep, 'country'],
                        'growth': fig.loc[keep, F1.NAMED['growth']].astype(float),
                        'gini': fig.loc[keep, F1.NAMED['gini']].astype(float),
                        'spendingData': spend.loc[keep], 'indexData': index.loc[keep],
                        'θData': 2 - 1/index.loc[keep],
                        'spendingModel': model, 'spendingObserved': observed,
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
           layers = (1, 2), theta = None, spending = None, omegaRule = 'anchor', root = None, keep = None):
    """ One row per relation of `relations` (RELATIONS by default): OLS of the data and of each layer of `layers`
    (`data`, `layer1`, `layer2`, each an ols dict, None for a layer not asked for), on the countries every layer
    asked for covers (and among `keep`, if given), under the design's measure `theta` (panelData; layer 1 at
    `omegaRule`, both from `root`). Layer 2 matches spending at the observed design by construction, so under spending
    'observed' its spending-on-regressor rows are flagged `targeted2`. Under spec 'none' no row has a design: ask for
    the spending relations only (SPENDING). """
    ps = {k: panelData(k, turnout, sample, reading, spec, betaRule, theta, spending, omegaRule, root) for k in layers}
    common = ps[layers[0]].index
    for k in layers[1:]:
        common = common.intersection(ps[k].index)
    if keep is not None:
        common = common.intersection(pd.Index(keep))
    ps = {k: p.loc[common] for k, p in ps.items()}
    first = ps[layers[0]]
    obs = variant(turnout, sample, reading, spec, betaRule, spending)['spending'] == 'observed'
    rows = []
    for yRole, xRole in relations:
        rows.append({'y': yRole, 'x': xRole, 'data': ols(*_xy(first, yRole, xRole, 'Data'))}
                    | {'layer{}'.format(k): ols(*_xy(ps[k], yRole, xRole, 'Model')) if k in ps else None
                       for k in (1, 2)}
                    | {'targeted2': obs and yRole == 'spending' and xRole != 'index'})
    out = pd.DataFrame(rows)
    out.attrs.update({'n': len(common), 'dropped': first.attrs['dropped'], 'countries': list(common)})
    return out


def spendingSlopes(turnout = None, sample = None):
    """ Section 6's spending test: the two relations of SPENDING in the data and in layer 1 at config.US['oecd26']'s
    spendingSpec (no cost: no design is read) and the β rule 'common', at the observed designs. """
    return slopes(turnout, sample, None, C.US['oecd26']['spendingSpec'], 'common', relations = SPENDING,
                  layers = (1,), spending = 'observed')


def thetaFit(layer, turnout = None, units = 'theta', omegaRule = 'anchor', root = None):
    """ The predicted against the observed design of layer `layer` at the paper's variant but `turnout`, from `root`
    (results/oecd26/ by default; datasets.oecd26StylizedDir() for 'pooled'): `panel` (panelData) and, over the countries
    other than the U.S. (the anchor, on the 45-degree line by construction), Pearson's `r` of model on data, `rmse` of
    the model's prediction, `rmseMean` that of predicting every country at the sample mean, `sdModel` and `sdData` the
    standard deviations (population, ddof 0: sdData equals rmseMean) of predicted and observed, and `fit` (ols of model
    on data). `units` 'theta' (θ) or 'index' (I = 1/(2 - θ)). `n` counts the U.S. in, `nStat` out. """
    p = panelData(layer, turnout, omegaRule = omegaRule, root = root)
    col = {'theta': ('θData', 'θModel'), 'index': ('indexData', 'indexModel')}[units]
    h = p.drop(index = 'USA')
    x, y = h[col[0]].to_numpy(float), h[col[1]].to_numpy(float)
    return {'panel': p, 'x': p[col[0]], 'y': p[col[1]], 'n': len(p), 'nStat': len(h),
            'r': float(np.corrcoef(x, y)[0, 1]), 'rmse': float(np.sqrt(np.mean((y - x)**2))),
            'rmseMean': float(np.sqrt(np.mean((x - x.mean())**2))), 'sdData': float(np.std(x)), 'sdModel': float(np.std(y)),
            'fit': ols(x, y), 'dropped': p.attrs['dropped']}


def _cell(o, digits = 2, stack = False):
    r""" A slope and its standard error; `stack` puts the error on a line of its own (\newline), so that every cell of
    a narrow column breaks alike. """
    return '$' + C.num(o['slope'], digits) + '$' + (r'\newline' if stack else ' ') + '$(' + C.num(o['se'], digits) + ')$'


def _dashNote(body):
    r""" The note's key to `--`, only when a cell of `body` (rows of a table) prints one. """
    return ' --: not computed.' if any(re.search(r'(&\s*--\s*(&|\\\\))|\{--\}', b) for b in body) else ''


def _names(isos):
    """ ISO3 codes as figure 1.1's country names, joined by commas and 'and'. """
    names = [str(D.oecdFigure1Data().at[c, 'country']) for c in isos]
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]


def sampleText(n, dropped):
    """ '20 countries (without Luxembourg, which has no CSES survey)' or '21 countries'. """
    return '{} countries'.format(n) + (' (without {}, which {} no CSES survey)'.format(
        _names(dropped), 'has' if len(dropped) == 1 else 'have') if dropped else '')


def _shared(a, v):
    """ The anchor's parameters every layer-1 country takes, as tex items: β (common rule), ω, the cost parameter. """
    return (([r'$\beta = ' + C.num(float(a['β']), 2) + '$'] if v['betaRule'] == 'common' else [])
            + [r'$\omega = ' + C.num(float(a['ω']), 2) + '$']
            + ([COSTSYMBOL[v['spec']][:-1] + ' = ' + C.num(float(a['p']), 2) + '$'] if v['spec'] in COSTSYMBOL else []))


def _and(items):
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def _layersText(a, v, matches = True, layers = (1, 2), ω = None):
    r""" The note's sentence on what the layers share with the anchor `a` and what layer 2 calibrates, at the
    variant `v`; `matches` adds that layer 2 then matches spending (at the observed design under spending 'chosen');
    `layers` the layers the output shows; `ω` a layer-1 ω other than the anchor's (omegaRule 'mean'). """
    items = _shared(a, v)
    if ω is not None:
        items = [r'$\omega = ' + C.num(ω, 2) + r'$, the mean of layer 2\textquotesingle s' if i.startswith(r'$\omega')
                 else i for i in items]
    tail = {'size': '', 'none': ', without the cost',
            'sizePiR': r', each at its cost $\lambda_{n,t} = \varepsilon\,\Pi_{n,t}/R_{n,t}$'}[v['spec']] \
        + (r', with the $\beta$ that sets its 2020 return to the U.S.\ one' if v['betaRule'] == 'commonR' else '')
    calibrated = r'$\omega$' if v['betaRule'] == 'common' else r'$\beta$ and $\omega$'
    one = r'Layer 1: every country at the U.S.\ ' + _and(items) + tail
    two = ('layer 2: ' + calibrated + r' calibrated to each country\textquotesingle s spending'
           + (r' at its observed design' if v['spending'] == 'chosen' else '')
           + (r' and the U.S.\ 2020 return' if v['betaRule'] == 'commonR' else '')
           + (', which it then matches' if matches and v['spending'] == 'observed' else ''))
    if layers == (1,):
        return one + '.'
    return one + '; ' + two + '.'


def specText(a, v, matches = True, layers = (1, 2)):
    r""" The notes' account of the model, its layers and the turnout. The paper's variant points to figure 7.2
    (`OECD26_Layer1`), whose note and section 7.3 define them (notes/paper_styleGuide.md, "What a note holds"); a
    variant states them in full, since they differ from figure 7.2's. """
    if suffix(**v) == '':
        return r'Model and layers as in figure \ref{fig:OECD26:layer1}.'
    return modelText(v) + ' ' + _layersText(a, v, matches, layers) + ' ' + turnoutNote(v['turnout'])


def modelText(v):
    r""" The note's sentence on what the model's index and spending are at the variant `v`. """
    design = ('chosen in 2020, which binds from 2050' if v['reading'] == 'chosen' else
              'in force in 2020, chosen in 1990')
    spend = (r'in 2020 on the path of the design it chooses' if v['spending'] == 'chosen' else
             r'in 2020 at the observed design')
    return (r'The model\textquotesingle s index is $1/(2-\theta)$ of the design ' + design
            + r', and its spending $\tau(1-\alpha)$ ' + spend + '.')


def oecd26Slopes(turnout = None, sample = None, reading = None, spec = None, betaRule = None, spending = None):
    r""" The slopes of figure 1.1's relations: the data on the sample, the model with the U.S. political weight
    and cost (layer 1) and with each country's own political weight (layer 2). """
    v = variant(turnout, sample, reading, spec, betaRule, spending)
    s = slopes(**v)
    a = D.oecd26Anchor(v['turnout'], v['spec'])
    body = []
    for _, r in s.iterrows():
        label = YTEX[r['y']] + ' on ' + XTEX[r['x']]
        cells = [label, _cell(r['data'], stack = True), _cell(r['layer1'], stack = True),
                 r'\textit{targeted}' if r['targeted2'] else _cell(r['layer2'], stack = True)]
        body.append(' & '.join(cells) + r' \\ % row: ' + rowKey(r['y'] + '_' + r['x']))
    note = (r'\textit{Note:} Least-squares slopes, standard errors in parentheses, ' + '{} countries. '.format(s.attrs['n'])
            + specText(a, v))
    sfx = suffix(**v)
    return _xwrap('OECD26_Slopes' + sfx,
                  'results/oecd26/layer1.csv, layer2.csv, anchor.csv; data/oecdFigure1.csv, oecd26_theta.csv',
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
    head, join = ((r'$\omega$ is calibrated to spending at the observed design at $\beta = ' + C.num(float(a['β']), 2)
                   + '$', ' and ') if v['betaRule'] == 'common' else
                  (r'$\beta$ and $\omega$ are calibrated to the U.S.\ 2020 return and to spending at the observed '
                   r'design', ' at '))
    cost = {'size': join + r'the U.S.\ $\lambda = ' + C.num(float(a['p']), 2) + '$',
            'sizePiR': join + r'the U.S.\ $\varepsilon = ' + C.num(float(a['p']), 2)
                       + r'$, $\lambda_{n,t} = \varepsilon\,\Pi_{n,t}/R_{n,t}$',
            'none': ', without the cost'}[v['spec']]
    anchor = (r' $^{\ast}$The U.S.\ is the anchor, where $\omega$ and ' + COSTSYMBOL[v['spec']] + ' are calibrated.'
              if v['spec'] in COSTSYMBOL else r' $^{\ast}$The U.S.\ is the anchor.')
    dagger = (r' $^{\dagger}$Outside the paper\textquotesingle s sample: informal employment above '
              + '{:g}'.format(float(smp['informalMax'].iloc[0])) + r'\% of employment.' if outside else '')
    if suffix(**v) == '':
        note = (r'\textit{Note:} ' + '{} countries'.format(len(p)) + r'. $\nu_{2020}$, workers per retiree; '
                r'$\tilde V$, the dispersion of relative incomes at the U.S.\ income percentiles; spending in \% of '
                r'GDP; $\theta$ and $I = 1/(2-\theta)$ as in appendix \ref{app:oecd26:data}. $\omega$ is calibrated to '
                r'spending at the observed design (layer 2, figure \ref{fig:OECD26:layer1}); the last two columns are '
                r'the model\textquotesingle s design for 2020, chosen in 1990, and its index. $^{\ast}$The anchor, '
                r'where $\omega$ and $\varepsilon$ are calibrated.' + dagger)
    else:
        note = (r'\textit{Note:} ' + sampleText(len(p), p.attrs['dropped']) + r'. $\nu_{2020}$, workers per retiree; '
                r'$\tilde V$, the dispersion of relative incomes at the U.S.\ income percentiles; spending in \% of GDP; '
                + MEASURENOTE + ' ' + head + cost + r'; the last two columns are the model\textquotesingle s design, '
                + design + r', and its index.' + anchor + dagger + ' ' + turnoutNote(v['turnout']))
    # two header rows, the data's columns and the model's under a spanner each, so that nine columns fit
    header = (r' & \multicolumn{5}{c}{\textbf{Data}} & \multicolumn{3}{c}{\textbf{Model, layer 2}} \\' + '\n'
              + r'\cmidrule(lr){2-6}\cmidrule(lr){7-9}' + '\n'
              + r'\textbf{Country} & $\nu_{2020}$ & $\tilde V$ & spending & $I$ & $\theta$ & $\omega$ & $\theta$ & $I$')
    sfx = suffix(**v)
    return _xwrap('OECD26_Omega' + sfx, 'results/oecd26/layer2.csv, anchor.csv; data/oecdFigure1.csv, oecd26_theta.csv',
                  r'The countries of the cross-country test, each calibrated to its pension spending'
                  + variantCaption(**v),
                  'table:OECD26:omega' + sfx, 'l' + 'Y'*8, header,
                  '\n'.join(body), note, width = r'\textwidth', size = r'\footnotesize\setlength{\tabcolsep}{3pt}')



# ---------------------------------------------------------------------------------------------------
# The five slopes under each measure of the design (OECD26_ThetaVariants): config.US['theta'] (the paper's) and the
# robustness variants of data/oecd26_theta.csv (config.US['oecd26']['thetaVariants']), at both turnouts.
MEASURES = (C.US['theta'],) + tuple(v for v in C.US['oecd26']['thetaVariants'] if v != C.US['theta'])
MEASURETEX = {'paper': r'Figure \ref{fig:US:OECDdata}\textquotesingle s index', 'A2pt': 'A, two points'}
TURNOUTTEX = {'cps': r'U.S.\ turnout', 'cses': r'Own turnout'}


def _measureSlopes(measure, turnout):
    """ slopes() of RELATIONS at the paper's variant of the cross-section under `measure` (MEASURES), or None while its
    rows are missing or stale (MissingInput, StaleInput): `--`, never a stale value. Anything else raises. """
    try:
        return slopes(turnout, theta = measure)
    except (D.MissingInput, D.StaleInput):
        return None


def oecd26ThetaVariants():
    r""" The slopes of figure 1.1's relations (OECD26_Slopes's five) in the data and in layers 1 and 2 under each
    measure of the design (MEASURES, the paper's first): the variants of data/oecd26_theta.csv, each on its own
    in-sample countries, the data's index 1/(2 - θ) of the variant and its spending; config.US['theta']'s from
    results/oecd26/, the others from results/oecd26_theta_<V>/ (stage (ii)'s oecd26Variants). One panel per turnout,
    the model's spending at the paper's reading. A measure whose rows are missing or stale prints `--`. """
    ncol = 1 + 3*len(TURNOUTTEX)
    res = {(m, t): _measureSlopes(m, t) for m in MEASURES for t in TURNOUTTEX}
    body = []
    for yRole, xRole in RELATIONS:
        body.append(r'\multicolumn{%d}{l}{\textit{%s}} \\' % (ncol, YTEX[yRole] + ' on ' + XTEX[xRole]))
        for m in MEASURES:
            cells = [MEASURETEX.get(m, m) + (r'$^{\ast}$' if m == C.US['theta'] else '')]
            for t in TURNOUTTEX:
                r = res[(m, t)]
                if r is None:
                    cells += ['--']*3
                    continue
                row = r.set_index(['y', 'x']).loc[(yRole, xRole)]
                cells += [_cell(row['data']), _cell(row['layer1']),
                          r'\textit{targeted}' if row['targeted2'] else _cell(row['layer2'])]
            body.append(keyed(' & '.join(cells) + r' \\', '_'.join((yRole, xRole, m))))
    ns = ', '.join('{} {}'.format(MEASURETEX.get(m, m), '/'.join(str(res[(m, t)].attrs['n']) if res[(m, t)] is not None
                                                                  else '--' for t in TURNOUTTEX))
                   for m in MEASURES if any(res[(m, t)] is not None for t in TURNOUTTEX))
    v = variant()
    note = (r'\textit{Note:} Least-squares slopes, standard errors in parentheses. Each measure of $\theta$ (appendix '
            r'\ref{app:oecd26:data}) is its own cross-section, the data and the model calibrated to them, on its '
            r'countries' + (r' at U.S.\ and at own turnout: ' + ns if ns else '')
            + r'. U.S.\ turnout: the CPS propensities to vote in every country; own turnout: each '
            r'country\textquotesingle s CSES propensities, the anchor recalibrated at its own. ' + specText(None, v)
            + r' $^{\ast}$The paper\textquotesingle s measure; at own turnout, table \ref{table:OECD26:slopes}.'
            + _dashNote(body))
    header = (' & ' + ' & '.join(r'\multicolumn{3}{c}{\textbf{' + TURNOUTTEX[t] + '}}' for t in TURNOUTTEX) + r' \\'
              + '\n' + ''.join(r'\cmidrule(lr){%d-%d}' % (2 + 3*i, 4 + 3*i) for i in range(len(TURNOUTTEX))) + '\n'
              + r'\textbf{Measure} & ' + ' & '.join(['Data', 'Layer 1', 'Layer 2']*len(TURNOUTTEX)))
    return _xwrap('OECD26_ThetaVariants',
                  'results/oecd26/, results/oecd26_theta_<V>/ layer1.csv, layer2.csv, anchor.csv; data/oecd26_theta.csv, '
                  'oecdFigure1.csv',
                  r'Figure \ref{fig:US:OECDdata}\textquotesingle s relations under each measure of the design',
                  'table:OECD26:thetaVariants', 'l' + 'Y'*(3*len(TURNOUTTEX)), header, '\n'.join(body), note,
                  width = r'\textwidth', size = r'\footnotesize\setlength{\tabcolsep}{3pt}')


# ---------------------------------------------------------------------------------------------------
# Appendix H's stylized readings (OECD26_Stylized): the paper's variant at own turnout (results/oecd26/), layer 1 at the
# mean layer-2 ω, and the pooled turnout with either ω (results/oecd26_stylized/, stage (ii)'s oecd26Stylized).
# Panels, each on the sample of its first reading: (key, [(row key, label, turnout, omegaRule, from the stylized
# directory?, on the panel's countries only?)]).
STYLIZED = (
    ('own', [('cses', r'Own turnout$^{\ast}$', 'cses', 'anchor', False, False),
             ('cses_mean', r'Own turnout, average $\omega$', 'cses', 'mean', True, False),
             ('pooled_own', r'Pooled turnout, these countries', 'pooled', 'anchor', True, True)]),
    ('pooled', [('pooled', r'Pooled turnout', 'pooled', 'anchor', True, False),
                ('pooled_mean', r'Pooled turnout, average $\omega$', 'pooled', 'mean', True, False)]),
)


def stylizedReading(turnout, omegaRule = 'anchor', stylized = False, keep = None):
    """ One reading of OECD26_Stylized: the slopes of INDEXRELATIONS (data, layers 1 and 2) on the countries both layers
    cover (and among `keep`), and over those other than the U.S. the correlation of model and data θ, the mean θ and
    the mean spending of data and both layers (the model's at the paper's spending reading); `ω` layer 1's ω. """
    root = D.oecd26StylizedDir() if stylized else None
    s = slopes(turnout, relations = INDEXRELATIONS, omegaRule = omegaRule, root = root, keep = keep)
    common = s.attrs['countries']
    ps = {k: panelData(k, turnout, omegaRule = omegaRule if k == 1 else 'anchor', root = root).loc[common]
          for k in (1, 2)}
    h = {k: p.drop(index = 'USA') for k, p in ps.items()}
    lay1 = D.oecd26Layer(1, turnout, root = root, omegaRule = omegaRule)
    ω = float(lay1.loc[[c for c in common if c != 'USA'], 'ω'].astype(float).unique()[0])
    out = {'slopes': s.set_index(['y', 'x']), 'n': len(common), 'dropped': s.attrs['dropped'], 'ω': ω,
           'countries': common,
           'θMeanData': float(h[1]['θData'].mean()), 'spendMeanData': float(h[1]['spendingData'].mean())}
    for k in (1, 2):
        out['r{}'.format(k)] = float(np.corrcoef(h[k]['θData'], h[k]['θModel'])[0, 1])
        out['θMean{}'.format(k)] = float(h[k]['θModel'].mean())
        out['spendMean{}'.format(k)] = float(h[k]['spendingModel'].mean())
    return out


def oecd26Stylized():
    r""" Appendix H's stylized readings of the cross-section beside the paper's (STYLIZED): per sample a data row, then
    per reading the slopes of the index relations in layers 1 and 2, the correlation of the predicted with the observed
    θ, and the mean θ and spending, the U.S. left out of the last three. Rows keyed `data_<panel>` and the readings'
    keys. """
    a = D.oecd26Anchor()
    span = lambda txt: r'\multicolumn{2}{c}{' + txt + '}'
    blank = span('')
    body, ωs = [], {}
    for panel, rows in STYLIZED:
        res = {}
        for key, label, turnout, rule, sty, restrict in rows:
            res[key] = stylizedReading(turnout, rule, sty, keep = res[rows[0][0]]['countries'] if restrict else None)
            if rule == 'mean':
                ωs[panel] = res[key]['ω']
        first = res[rows[0][0]]
        title = sampleText(first['n'], first['dropped'])
        body.append(r'\multicolumn{14}{l}{\textit{' + title[0].upper() + title[1:] + '}} \\\\')
        d = first['slopes']
        cells = ['Data', str(first['n'])] + [span(_cell(d.loc[k, 'data'])) for k in INDEXRELATIONS] \
            + [blank, span(C.num(first['θMeanData'], 3)), span(C.num(first['spendMeanData'], 2))]
        body.append(keyed(' & '.join(cells) + r' \\', 'data_' + panel))
        for key, label, turnout, rule, sty, restrict in rows:
            r = res[key]
            cells = [label, str(r['n'])]
            for k in INDEXRELATIONS:
                cells += [_cell(r['slopes'].loc[k, 'layer1'], stack = True), _cell(r['slopes'].loc[k, 'layer2'], stack = True)]
            cells += [C.num(r['r1'], 2), C.num(r['r2'], 2), C.num(r['θMean1'], 3), C.num(r['θMean2'], 3),
                      C.num(r['spendMean1'], 2), C.num(r['spendMean2'], 2)]
            body.append(keyed(' & '.join(cells) + r' \\', key))
    v = variant()
    note = (r'\textit{Note:} The test of table \ref{table:OECD26:slopes} under the two readings of appendix '
            r'\ref{app:oecd26:readings}: every country at the mean of layer 2\textquotesingle s $\omega$ ('
            + ' and '.join('{} at {}'.format(C.num(ωs[p], 2), {'own': 'own', 'pooled': 'pooled'}[p])
                           for p in ('own', 'pooled') if p in ωs)
            + r' turnout, against the anchor\textquotesingle s ' + C.num(float(a['ω']), 2) + r'), and pooled turnout; '
            r'\textit{pooled turnout, these countries} is the pooled reading on the countries of own turnout. Slopes: '
            r'least squares, standard errors in parentheses, the U.S.\ included; correlations and means: without the '
            r'U.S. Spending in \% of GDP. ' + specText(a, v) + r' $^{\ast}$The paper\textquotesingle s specification.')
    rel = {('spending', 'index'): r'Spending on $I$', ('index', 'growth'): r'$I$ on growth',
           ('index', 'gini'): r'$I$ on the Gini'}
    groups = [rel[k] for k in INDEXRELATIONS] + [r'Corr.\ $\theta$', r'Mean $\theta$', 'Mean spending']
    header = (' & & ' + ' & '.join(r'\multicolumn{2}{c}{' + g + '}' for g in groups) + r' \\' + '\n'
              + ''.join(r'\cmidrule(lr){%d-%d}' % (3 + 2*i, 4 + 2*i) for i in range(len(groups))) + '\n'
              + r'\textbf{Reading} & $n$ & ' + ' & '.join(['L1', 'L2']*len(groups)))
    return _xwrap('OECD26_Stylized',
                  'results/oecd26/, results/oecd26_stylized/ layer1.csv, layer2.csv, anchor.csv; data/oecd26_theta.csv, '
                  'oecdFigure1.csv',
                  r'The cross-country test under stylized readings of turnout and the political weight',
                  'table:OECD26:stylized', r'>{\raggedright\arraybackslash}p{2.3cm}c' + 'Y'*(2*len(groups)), header,
                  '\n'.join(body), note, width = r'\textwidth',
                  size = r'\scriptsize\setlength{\tabcolsep}{2pt}')
