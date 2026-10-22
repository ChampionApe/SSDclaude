r""" Table builders for the US/France/UK arm. tables.py is the Argentina arm; the two are separate
modules for the same reason runCalibration.py and runCalibrationUS.py are.

Each function returns the complete tex body of one file in writing/Paper/Tables/, reproducing the
STRUCTURE of the hand-written table it replaces (tabularx with Y columns, the same caption, label and
rules), so the paper's \ref{}s keep resolving and a diff shows moved numbers rather than a re-layout.

Every US builder takes `commonX`, defaulting to the headline variant (config.US['commonX']), which is the
only one build.py registers; config.variantSuffix names the other variant's file and \label, so the
headline's stay exactly as the draft cites them.

THREE CONVENTIONS of stage (iii), for every builder that reads the experiment csvs (figuresUS, siteData):

  * `Savings rate` is s/Y, savings relative to GDP -- the same quantity as the Argentina tables. The US
    shock csv carries it as `srOverY` (datasets.US_SR); its `sr` column is s/(w h) and is not read. The
    ESC csvs carry only s/(w h) and go through datasets.escSavingsOverY, which is exact (w h = (1-alpha) Y).
  * A counterfactual's savings rate is reported as the CHANGE against that rho's own baseline, in
    percentage points (config.pp); only baseline rows carry a level. The baseline savings rate is a
    prediction that moves with rho (beta is identified by R), so a scenario at rho differenced against
    the rho = 1 baseline is not an effect. (The leisure row, a pure scale that cannot move savings, is
    the check: 0.00 at every rho.) Tax rates and workweeks stay as levels.
  * `Avg. workweek` is normalised against each rho's OWN baseline, inside the experiment script. Under
    vector X the level of hbar is not identified, so there is no expression that converts it to hours;
    the observed workweek is a reference point, not a unit. Stage (iii) therefore reads `workweek`
    straight out of the csv and must never re-derive it from hbar.
"""
import os
import numpy as np

import config as C
import datasets as D
from tables import BANNER, LQ, RQ, notesBlock, rowKey, keyed

# The short key of each shock-csv scenario: figuresUS's mark ids and siteData's scenario column.
ROWKEY = {'Baseline': 'baseline', r'$\theta = 0$': 'theta0', r'$\theta = 1$': 'theta1',
          'Mild ageing': 'mild', 'Acute ageing': 'acute', 'Income distribution': 'income',
          'Leisure preferences': 'leisure', 'Voting': 'voting', 'All French characteristics': 'frall',
          'France (own calibration)': 'france'}


def _xwrap(name, src, caption, label, colspec, header, body, note = None, width = r'.9\textwidth', size = None):
    """ One threeparttable around a tabularx, matching the hand-written US tables' layout. `header` is a
    list of cells for one row, or a pre-formatted string when a table needs more than one header row.

    `width`: the four-column shock tables sit at .9\\textwidth. The six-column ESC tables need the full
    measure -- at .9 each Y column is 2.2cm and the headers break mid-word. `size` (a font-size command,
    e.g. r'\\footnotesize') sets the tabular's type, not the caption's or the notes'; None leaves it at the
    paper's. """
    tn = notesBlock(note)
    head = header if isinstance(header, str) else ' & '.join(header)
    return (BANNER.format(name = name, src = src)
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{' + caption + '}\n\\label{' + label + '}\n'
            + '\\renewcommand{\\arraystretch}{1.25}\n'
            + ('' if size is None else size + '\n')
            + '\\begin{tabularx}{' + width + '}{' + colspec + '}\n\\toprule\n'
            + head + ' \\\\\n\\midrule \n'
            + body + '\n\\bottomrule\n\\end{tabularx}\n' + tn
            + '\\end{threeparttable}\n\\end{table}\n')


# ---------------------------------------------------------------------------------------------------
# LaTeX: column headers, captions, block titles. figuresOA draws the US, UK and FR entries as plain text.
COUNTRYNAME = {'US': 'U.S.', 'UK': 'UK', 'FR': 'France', 'FRUK': 'France, UK income groups',
               'UKUS': r'UK, U.S.\ income groups'}
CAPTIONNAME = dict(COUNTRYNAME, US = 'the U.S.')    # "Household heterogeneity -- the U.S."


def usukfrCalibration(commonX = None):
    r""" Table \ref{table:US:Calib}: the headline calibration for the three countries.

    `X` is the POPULATION-WEIGHTED MEAN of X_i -- the only summary of a vector whose level IS the hours
    unit, and the one the leisure counterfactual is matched on. The lower panel holds the parameters the
    three countries share, each in one cell across the country columns: beta, calibrated on the US and
    imposed on France and the UK at the same rho, and rho, xi and alpha, imposed. A value that differs
    across the countries raises rather than printing one of them. """
    commonX = C.US['commonX'] if commonX is None else commonX
    c = D.usCalibrationSummary(commonX)
    cols = [k for k in ('US', 'UK', 'FR') if k in c]     # the hand-written column order
    year0 = C.usCalendar()['year0']
    # Booktabs horizontals, plus the one deviation: a hairline at 25% black on each side of the value
    # block, which is what separates the numbers from the prose column now that there is no spanner.
    # No \addlinespace with it -- the rules are drawn per row, so a gap between rows breaks them into
    # dashes; \arraystretch carries the air instead. A merged cell carries the right-hand rule in its
    # own spec, since \multicolumn replaces the spec of the columns it spans.
    rule = '!{\\color{black!25}\\vrule width 0.5pt}'

    # Parameter, the three values, then what identifies them. The values are the table's content and sit
    # in the middle under one spanner rule, which is what separates them from the prose column; the
    # identifying phrase is a gloss and closes the row.
    def row(key, label, target, fn):
        return keyed(' & '.join([label] + [fn(c[k]) for k in cols] + [target]) + r' \\', key)

    def shared(key, label, target, col, fmt = C.num):
        v = [float(c[k][col]) for k in cols]
        if not np.allclose(v, v[0], rtol = 0, atol = 1e-12):
            raise ValueError('{} is not common to {}: {}'.format(col, cols, v))
        cell = r'\multicolumn{%d}{c%s}{%s}' % (len(cols), rule, fmt(v[0]))
        return keyed(' & '.join([label, cell, target]) + r' \\', key)

    rows = [
        row('theta', r'$\theta$', 'Replacement rate dispersion', lambda r: C.num(r['θ'])),
        row('omega', r'$\omega$',
            ', '.join(r'$\tau^{' + k + '} = ' + C.pct(c[k]['τ0'], 1) + '$' for k in cols),
            lambda r: C.num(r['ω'])),
        # Two decimals: with the hours unit normalised to μ = 1 (model.addEigenVectors), the vector-X
        # X_i and their mean sit on an O(1) scale where one decimal is two significant figures.
        row('X', '$X$', 'Average workweek', lambda r: C.num(r['Xbar'], 2)),
        row('nu', r'$\nu_{%d}$' % year0, '30-year gross population growth',
            lambda r: C.num(r['ν2020'])),
        row('etaratio', r'$\eta_{H}/\eta_L$', 'Relative productivity, high to low income',
            lambda r: C.num(r['ηHηL'])),
        r'\midrule',
        # Not "imposed on the other two" as well: the note says so, and the cell then fits one line.
        shared('beta', r'$\beta$', '30-year interest rate (U.S.)', 'β'),
        shared('rho', r'$\rho$', 'Log-GHH preferences', 'ρ', fmt = '{:g}'.format),
        shared('xi', r'$\xi$', 'Frisch elasticity of labor supply', 'ξ'),
        shared('alpha', r'$\alpha$', 'Capital income share', 'α'),
    ]
    header = ([r'\textbf{Parameter}'] + [r'\textbf{' + COUNTRYNAME[k] + '}' for k in cols]
              + [r'\textbf{Identified by}'])
    # The one note that spells the variant out; every other US table points here (config.variantNote).
    note = (r'\item \textit{Note:} $X$ is the '
            r'population-weighted mean of $X_i$; its level is the hours unit, pinned for France and the '
            r'UK by targeting average hours relative to the U.S.\ rather than in levels. The lower panel is '
            r'common to the three countries; $\beta$ is calibrated for the U.S.\ and imposed on the other two.'
            + C.variantNote(commonX, full = True))
    return (BANNER.format(name = 'USUKFRCalibration' + C.variantSuffix(commonX),
                          src = 'results/paper/usCalibrationSummary.csv')
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{Calibration, the U.S., the UK and France' + C.variantCaption(commonX) + '}\n'
            + '\\label{table:US:Calib' + C.variantSuffix(commonX) + '}\n'
            + '\\renewcommand{\\arraystretch}{1.3}\n'
            + '\\begin{tabularx}{\\textwidth}{l' + rule + 'C{1.4cm}'*len(cols) + rule
            + '>{\\raggedright\\arraybackslash}X}\n\\toprule\n'
            + ' & '.join(header) + ' \\\\ \\midrule\n'
            + '\n'.join(rows) + '\n\\bottomrule\n\\end{tabularx}\n'
            + notesBlock(note)
            + '\\end{threeparttable}\n\\end{table}\n')


def _householdHeterogeneity(country, name, label, commonX = None):
    r""" One country's per-group table: gamma_i, X_i, eta_i, mu_i.

    Under the common-X calibration the X_i row is one number repeated, and the hours row is a prediction
    rather than the target it is under vector X -- so the `Target` column is variant-dependent. """
    commonX = C.US['commonX'] if commonX is None else commonX
    summary = D.usCalibrationSummary(commonX)
    if country not in summary:
        raise D.MissingInput(os.path.join(C.PAPERDIR, 'usCalibrationSummary.csv') + ' (no {} row)'.format(country))
    c = summary[country]
    spec = [(r'$\gamma_i$', 'γi', 2, 'Income percentiles.', 'gamma'),
            ('$X_i$',       'Xi', 2, 'Average hours worked.' if commonX else 'Hours worked.', 'X'),
            (r'$\eta_i$',   'ηi', 2, 'Income distribution.', 'eta'),
            (r'$\mu_i$',    'μi', 2, 'Voting propensity.', 'mu')]
    rows = [keyed(' & '.join([lab] + [C.num(v, d) for v in c[key]] + [target]) + r' \\', rk)
            for lab, key, d, target, rk in spec]
    return (BANNER.format(name = name + C.variantSuffix(commonX),
                          src = 'results/paper/usCalibrationSummary.csv')
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{Household heterogeneity -- ' + CAPTIONNAME[country]
            + C.variantCaption(commonX) + '}\n'
            + '\\label{' + label + C.variantSuffix(commonX) + '}\n'
            + '\\renewcommand{\\arraystretch}{1.5}\n'
            + '\\begin{tabularx}{\\textwidth}{Y|YYY|p{5cm}}\n\\hline\n'
            + '& \\multicolumn{3}{c|}{\\textbf{Income group}} & \\\\ \\cline{2-4}\n'
            + ' & '.join([r'\multicolumn{1}{c|}{\textbf{Parameter}}',
                          r'\textbf{Low}', r'\textbf{Medium}', r'\textbf{High}', r'\textbf{Target}'])
            + ' \\\\ \\hline\n' + '\n'.join(rows) + '\n\\hline\n\\end{tabularx}\n'
            + '\\end{threeparttable}\n\\end{table}\n')


def usHouseholdHeterogeneity(commonX = None):
    return _householdHeterogeneity('US', 'US_householdheterogeneity', 'table:a_US:CalibUS', commonX)


def frHouseholdHeterogeneity(commonX = None):
    return _householdHeterogeneity('FR', 'FR_householdheterogeneity', 'table:a_US:CalibFR', commonX)


def ukHouseholdHeterogeneity(commonX = None):
    return _householdHeterogeneity('UK', 'UK_householdheterogeneity', 'table:a_US:CalibUK', commonX)


def frukHouseholdHeterogeneity(commonX = None):
    """ France regrouped at the UK's income cuts -- the France the UK exercise borrows from. """
    return _householdHeterogeneity('FRUK', 'FRUK_householdheterogeneity', 'table:a_US:CalibFRUK', commonX)


def ukusHouseholdHeterogeneity(commonX = None):
    """ The UK regrouped at US income percentiles -- the third row of US_ESC_Country. Its group means are
    a linear fit of the UK's own, not a microdata recount (data/UKMain.xlsx, sheet heterogeneityUS). """
    return _householdHeterogeneity('UKUS', 'UKUS_householdheterogeneity', 'table:a_US:CalibUKUS', commonX)


# ---------------------------------------------------------------------------------------------------
# Endogenous system characteristics (section sec:esc, appendix app:escResults): the cost calibration of
# the U.S. and the UK and the cross-country test.
# ---------------------------------------------------------------------------------------------------
def _wedgeSymbol(spec = None):
    """ The calibrated cost parameter's symbol under `spec` (config.US['esc']['spec'] by default): lambda
    under 'size', p under 'scale'. Both live in the csvs' `p` column. """
    spec = C.US['esc']['spec'] if spec is None else spec
    return r'\lambda' if spec == 'size' else 'p'


def _costRows(recs, spec):
    """ The rows of a cost-calibration table, {rho: record} -> (body, thetaStar, Vtilde): rho, the cost
    parameter, omega and the shares of revenue lost at the observed design and at theta = 0
    (datasets.escWedge), in percent at one decimal. theta* and Vtilde are the same at every rho -- the cost
    cancels from the replacement-rate ratio, and Vtilde is a function of relative incomes alone -- so the
    note prints them once; a row that disagrees is an error in the csvs, not a cell to print. """
    rows, θs, Vs = [], [], []
    for ρ in sorted(recs):
        r = recs[ρ]
        w = D.escWedge(r, spec)
        θs.append(float(r['θStar']))
        Vs.append(w['Vtilde'])
        rows.append(keyed(' & '.join([C.num(ρ, 1), C.num(float(r['p']), 3), C.num(float(r['ω']), 2),
                                      C.pct(1 - w['fStar'], 1), C.pct(1 - w['f0'], 1)]) + r' \\',
                          rowKey('rho', ρ)))
    if max(θs) - min(θs) > 1e-6 or (None not in Vs and max(Vs) - min(Vs) > 1e-6):
        raise ValueError('theta* or Vtilde differs across rho in the cost calibration: {} {}'.format(θs, Vs))
    return '\n'.join(rows), θs[0], (None if None in Vs else Vs[0])


def _costHeader(spec):
    return [r'$\rho$', '$' + _wedgeSymbol(spec) + '$', r'$\omega$', r'$1 - f(\theta^{\ast})$', '$1 - f(0)$']


def escCalibrationTable(spec = None):
    r""" Table \ref{table:US_ESC:calibration} (section sec:esc): the calibrated cost parameter per rho (lambda
    under 'size', p under 'scale'), omega recalibrated with it, and the shares of revenue lost in 2020 at the
    observed design and at theta = 0, both at the 2020 tax rate. `spec` defaults to the paper's
    (config.US['esc']['spec']); passing the comparison spec exercises the builder on its rows. """
    spec = C.US['esc']['spec'] if spec is None else spec
    cal = D.escCalibration()
    recs = {}
    for ρ in C.US['esc']['ρTable']:
        if (ρ, spec) not in cal:
            raise D.MissingInput('escCalibration ({}, {})'.format(ρ, spec))
        recs[ρ] = cal[(ρ, spec)]
    body, θ, V = _costRows(recs, spec)
    if spec == 'size':
        form = (r'The cost is that of equation \eqref{eq:esc:budget}, with $\theta^{\ast} = ' + C.num(θ, 3)
                + r'$ and $\tilde V = ' + C.num(V, 3) + r'$ at every $\rho$')
    else:
        form = (r'The cost is $f(\theta) = \phi + (1-\phi)\theta^{p}$ with $\phi = ' + C.num(C.US['esc']['phi'], 1)
                + r'$ imposed, and $\theta^{\ast} = ' + C.num(θ, 3) + r'$ at every $\rho$')
    note = (r'\textit{Note:} ' + form + r'. $1 - f(\theta^{\ast})$ and $1 - f(0)$ are the shares of revenue lost '
            r'in 2020 at the observed design and at a flat benefit, both at the 2020 tax rate. $\beta$ and '
            r'$\omega$ are recalibrated with $' + _wedgeSymbol(spec) + r'$.' + C.variantNote(C.US['commonX']))
    return _xwrap('US_ESC_Calibration', 'results/esc/escCalibration{,CRRA}.csv',
                  'The calibrated cost of redistribution for the U.S.',
                  'table:US_ESC:calibration', 'YYYYY', _costHeader(spec), body, note, width = r'.8\textwidth')


# escCountry.csv's economy keys, in the order the table prints them, their labels and row keys.
COUNTRYROWS = (('UK', 'UK', 'gbr'), ('FR', 'France', 'fra'), ('UKUS', r'UK at U.S.\ income groups', 'ukus'))


def escCountryTable(spec = None):
    r""" Table \ref{table:US_ESC:country}: the cross-country test of the cost specification. One row per
    economy -- the UK, France, and the UK regrouped at US income percentiles -- with its observed design,
    the design its electorate chooses under the US-calibrated parameter, and the parameter at which it
    re-elects its own design (`--` where no finite value does: France's observed design is the corner
    theta = 1). Vtilde is printed when the csv carries it (rows written since the 'size' spec). rho = 1
    (LOG) only: the country stage has no CRRA counterpart. """
    spec = C.US['esc']['spec'] if spec is None else spec
    df = D.escCountry(spec = spec)
    sym = _wedgeSymbol(spec)
    us = df[df['wedgeFrom'] == 'US']
    hasV = 'Vtilde' in df.columns and bool(us['Vtilde'].notna().any())
    rows = []
    for key, name, rk in COUNTRYROWS:
        u = us[us['country'] == key]
        if u.empty:
            raise D.MissingInput('escCountry ({}, US {}, {}, phi={})'
                                 .format(key, sym, spec, C.US['esc']['phi']))
        u = u.iloc[-1]
        own = df[(df['country'] == key) & (df['wedgeFrom'] == 'own')]
        cells = [name, C.num(float(u['θStar']), 3), C.num(float(u['choice']), 3),
                 '--' if own.empty else C.num(float(own.iloc[-1]['p']), 3)]
        if hasV:
            cells.append('--' if u['Vtilde'] != u['Vtilde'] else C.num(float(u['Vtilde']), 3))
        rows.append(keyed(' & '.join(cells) + r' \\', rk))
    pUS = float(us.iloc[-1]['p'])
    # \mbox: in the narrow Y column the header otherwise breaks as "ob-served"
    header = [r'\textbf{Economy}', r'$\theta^{\ast}$ \mbox{\textbf{observed}}',
              r'$\theta$ \textbf{chosen, U.S.} $' + sym + '$', r'\textbf{Own} $' + sym + '$'] \
             + ([r'$\tilde V$'] if hasV else [])
    if spec == 'size':
        gap = r' No finite $\lambda$ makes France re-elect its observed design: it is the corner $\theta = 1$.'
    else:
        gap = (r' No finite $p$ makes France re-elect its observed design, the corner $\theta = 1$.')
    note = (r'\textit{Note:} Each economy is its own calibration at $\rho = 1$ with U.S.\ $' + sym + ' = '
            + C.num(pUS, 3) + '$. ' + LQ + 'Chosen' + RQ
            + r' is the design in 2020 on the economy\textquotesingle s own freely simulated path under the '
            r'U.S.\ parameter, to be read against the observed one; ' + LQ + 'own' + RQ + r' is the value at '
            r'which that path re-elects the observed design.' + gap + C.variantNote(C.US['commonX']))
    return _xwrap('US_ESC_Country', 'results/esc/escCountry.csv',
                  r'The UK and France under the U.S.\ cost of redistribution',
                  'table:US_ESC:country', 'l' + 'Y'*(len(header) - 1), header, '\n'.join(rows), note,
                  width = r'\textwidth')


def ukEscCalibrationTable(spec = None):
    r""" Table \ref{table:UK_ESC:calibration} (appendix app:escResults:calibration): the UK's own calibrated
    cost per rho at its own income groups (datasets.escCalibrationHost: rho = 1 from escCountry.csv, the
    other rho from escCalibrationCRRAUK.csv), in the layout of escCalibrationTable. beta is the US value
    without the cost at each rho, imposed as in section 6; omega is recalibrated with the cost parameter. """
    spec = C.US['esc']['spec'] if spec is None else spec
    cal = D.escCalibrationHost('UK', spec = spec)
    recs = {}
    for ρ in C.US['esc']['ρTable']:
        if ρ not in cal:
            raise D.MissingInput("the UK's own cost calibration at rho = {} ({})".format(ρ, spec))
        recs[ρ] = cal[ρ]
    body, θ, V = _costRows(recs, spec)
    sym = _wedgeSymbol(spec)
    note = (r'\textit{Note:} As table \ref{table:US_ESC:calibration}, for the UK at its own income groups, where '
            r'$\theta^{\ast} = ' + C.num(θ, 3) + '$' + ('' if V is None else r' and $\tilde V = ' + C.num(V, 3) + '$')
            + r' at every $\rho$; $' + sym + r'$ is the value at which the UK electorate re-elects its observed '
            r'design. $\beta$ is the U.S.\ value of the calibration without the cost, imposed as in section '
            r'\ref{sec:oecd}, and $\omega$ is recalibrated with $' + sym + r'$.' + C.variantNote(C.US['commonX']))
    return _xwrap('UK_ESC_Calibration', 'results/esc/escCountry.csv, escCalibrationCRRAUK.csv',
                  'The calibrated cost of redistribution in the UK',
                  'table:UK_ESC:calibration', 'YYYYY', _costHeader(spec), body, note, width = r'.8\textwidth')
