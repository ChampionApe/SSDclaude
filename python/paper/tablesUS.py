r""" Table builders for the US/France/UK arm. tables.py is the Argentina arm; the two are separate
modules for the same reason runCalibration.py and runCalibrationUS.py are.

Each function returns the complete tex body of one file in writing/Paper/Tables/, reproducing the
STRUCTURE of the hand-written table it replaces (tabularx with Y columns, the same caption, label and
rules), so the paper's \ref{}s keep resolving and a diff shows moved numbers rather than a re-layout.

EVERY US BUILDER TAKES `commonX`, DEFAULTING TO THE HEADLINE VARIANT (config.US['commonX']). The same
builder therefore produces the paper's table and its robustness twin, and config.variantSuffix keeps the
headline's name, filename and \label exactly as the draft cites them while the twin's carry its own
variant. Do not fork a builder to make a twin -- the point of the pair is that the two differ only in
which calibration they read.

THREE CONVENTIONS, each of which a builder could silently get wrong:

  * `Savings rate` is s/Y, savings relative to GDP -- the same quantity as the Argentina tables. The US
    shock csv carries it as `srOverY` (datasets.US_SR); its `sr` column is s/(w h) and is not read. The
    ESC csvs carry only s/(w h) and go through datasets.escSavingsOverY, which is exact (w h = (1-alpha) Y).
  * A counterfactual's savings rate is reported as the CHANGE against that rho's own baseline, in
    percentage points (config.pp); only baseline rows carry a level. The baseline savings rate is a
    prediction that moves with rho (beta is identified by R), so a scenario at rho differenced against
    the rho = 1 baseline is not an effect. (The leisure row, a pure scale that cannot move savings, was
    the check -- 0.00 at every rho -- while it was printed; it is still in the csv.) Tax rates and
    workweeks stay as levels.
  * `Avg. workweek` is normalised against each rho's OWN baseline, inside the experiment script. Under
    vector X the level of hbar is not identified, so there is no expression that converts it to hours;
    the observed workweek is a reference point, not a unit. Stage (iii) therefore reads `workweek`
    straight out of the csv and must never re-derive it from hbar.
"""
import os
import numpy as np

import config as C
import datasets as D
from tables import BANNER, LQ, RQ, SRNOTE, notesBlock, rowKey, keyed

# The row-key block of each shock-csv scenario (tables.rowKey); figuresUS names its marks' rows with it.
ROWKEY = {'Baseline': 'baseline', r'$\theta = 0$': 'theta0', r'$\theta = 1$': 'theta1',
          'Mild ageing': 'mild', 'Acute ageing': 'acute', 'Income distribution': 'income',
          'Leisure preferences': 'leisure', 'Voting': 'voting', 'All French characteristics': 'frall',
          'France (own calibration)': 'france'}


def _xwrap(name, src, caption, label, colspec, header, body, note = None, width = r'.9\textwidth'):
    """ One threeparttable around a tabularx, matching the hand-written US tables' layout. `header` is a
    list of cells for one row, or a pre-formatted string when a table needs more than one header row
    (escCalibrationTable's grouped columns).

    `width`: the four-column shock tables sit at .9\\textwidth. The six-column ESC tables need the full
    measure -- at .9 each Y column is 2.2cm and the headers break mid-word. """
    tn = notesBlock(note)
    head = header if isinstance(header, str) else ' & '.join(header)
    return (BANNER.format(name = name, src = src)
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{' + caption + '}\n\\label{' + label + '}\n'
            + '\\renewcommand{\\arraystretch}{1.25}\n'
            + '\\begin{tabularx}{' + width + '}{' + colspec + '}\n\\toprule\n'
            + head + ' \\\\\n\\midrule \n'
            + body + '\n\\bottomrule\n\\end{tabularx}\n' + tn
            + '\\end{threeparttable}\n\\end{table}\n')


def _cells(r, base = None):
    """ The three reported quantities of one shock row, formatted. With `base` (that rho's baseline
    row) the savings rate is the change against it in p.p.; without, it is the level. """
    sr = C.pct(r[D.US_SR]) if base is None else C.pp(r[D.US_SR] - base[D.US_SR])
    return [C.pct(r['τ']), sr, C.num(r['workweek'])]


def _shockRows(df, ρ, scenarios, baselineLabel):
    """ The 'Full effect' / 'Economic equilibrium effect' block shared by US_PensChars and US_Ageing. """
    b = D.usBaseline(df, ρ)
    line = lambda lab, r, base = None: ' & '.join([lab] + _cells(r, base)) + r' \\'
    out = [keyed(line(baselineLabel, b) + '[1.25ex]', 'baseline')]
    for effect, head in (('full', 'Full effect:'), ('ee', 'Economic equilibrium effect:')):
        out.append(r'\multicolumn{4}{l}{\textit{' + head + r'}} \\\hline')
        block = [[line(lab, D.usShockRow(df, ρ, scen, effect), b), rowKey(ROWKEY[scen], effect = effect)]
                 for lab, scen in scenarios]
        block[-1][0] += '[1.25ex]'
        out += [keyed(l, k) for l, k in block]
    return '\n'.join(out)


SHOCKHEAD = [r'\textbf{Scenario}', r'\textbf{Tax rate}', r'\textbf{Savings rate}',
             r'\textbf{Avg. workweek}']


# ---------------------------------------------------------------------------------------------------
def usPensChars(commonX = None):
    r""" Table \ref{table:US:pensChars}: theta = 0 and theta = 1 in the US, both effects, at the
    baseline rho. """
    commonX = C.US['commonX'] if commonX is None else commonX
    ρ = C.US['ρBaseline']
    df = D.usShocks(commonX = commonX)
    θ0 = D.usCalibrationSummary(commonX)['US']['θ']
    body = _shockRows(df, ρ, [(r'$\theta = 0$', r'$\theta = 0$'), (r'$\theta = 1$', r'$\theta = 1$')],
                      r'$\theta = ' + C.num(θ0) + '$')
    note = (r'\item \textit{Note:} $\rho = ' + C.num(ρ, 1) + r'$. The economic-equilibrium rows hold $\tau$ at the '
            r'baseline path, so they isolate the response of savings and hours to $\theta$ alone; the '
            r'full rows re-optimise $\tau$ politically.' + SRNOTE + C.variantNote(commonX))
    return _xwrap('US_PensChars' + C.variantSuffix(commonX), df.attrs['source'],
                  r'The effect of pension design ($\theta$) in US -- {}{}'.format(
                      C.usCalendar()['year0'], C.variantCaption(commonX)),
                  'table:US:pensChars' + C.variantSuffix(commonX), 'p{3cm}YYY', SHOCKHEAD, body, note)


def usAgeing(commonX = None):
    r""" Table \ref{table:US:ageing}: mild and acute ageing, both effects, at the baseline rho.

    Ageing touches neither eta nor X, so every number here is common to the two calibration variants
    (they agree to ~1e-13); the twin exists so the appendix set is complete, not because it moves. """
    commonX = C.US['commonX'] if commonX is None else commonX
    ρ = C.US['ρBaseline']
    year0 = C.usCalendar()['year0']
    df = D.usShocks(commonX = commonX)
    body = _shockRows(df, ρ,
                      [(r'Mild ageing\tnote{a}', 'Mild ageing'),
                       (r'Acute ageing\tnote{b}', 'Acute ageing')], 'Baseline')
    note = (r'\item \textit{Note:} Each scenario is a separate equilibrium path.' + SRNOTE + '\n'
            r'\item[a] The ' + LQ + 'mild ageing' + RQ + r' scenario refers to the case with $\nu_t$ set '
            r'at $(1+\nu_t^{base})/2$ throughout.' '\n'
            r'\item[b] The ' + LQ + 'acute ageing' + RQ + r' scenario refers to $\nu_t = 1$ throughout.'
            + C.variantNote(commonX))
    return _xwrap('US_Ageing' + C.variantSuffix(commonX), df.attrs['source'],
                  'The effect of ageing in US -- {}{}'.format(year0, C.variantCaption(commonX)),
                  'table:US:ageing' + C.variantSuffix(commonX), 'p{3cm}YYY', SHOCKHEAD, body, note)


HOSTNAME = {'US': 'US', 'UK': 'the UK'}    # as the captions and notes name the host economy


def _otherShocks(commonX = None, host = 'US'):
    r""" Table \ref{table:US:otherShocks} (host 'US') and \ref{table:UK:otherShocks} (host 'UK'): the
    French characteristics imposed on the host model, at the baseline rho.

    Full effect only, following the paper, which reports that the two effects are not informative apart
    for these -- they work in the same direction and are quantitatively minor. The economic-equilibrium
    rows ARE in the shock csv if that judgement is revisited.

    Four single-characteristic and composite rows: income distribution, leisure preferences (a pure
    rescaling of X_i, so it moves hours and nothing else -- printed again since 2026-09-22), voting, and
    all three at once; then France's own calibrated path. The last two say how far the observable
    characteristics take the host towards France and how much is left for the political weight -- the
    comparison the new-path convention exists to make (python/US/runShocksUS.franceReference).

    This is the table the calibration variant moves most: income distribution is defined through eta,
    which is exactly what the variant re-interprets. The UK table reads the UK-host csv, where France's
    groups are cut at the UK's own income cuts (config.US['ukHost']). """
    commonX = C.US['commonX'] if commonX is None else commonX
    ρ = C.US['ρBaseline']
    df = D.usShocks(commonX = commonX, host = host)
    b = D.usBaseline(df, ρ)
    name = HOSTNAME[host]
    theName = name if name.startswith('the ') else 'the ' + name      # 'the US', 'the UK'
    rows = [keyed(' & '.join(['Baseline'] + _cells(b)) + r' \\', 'baseline')]
    for lab in ('Income distribution', 'Leisure preferences', 'Voting'):
        rows.append(keyed(' & '.join([lab] + _cells(D.usShockRow(df, ρ, lab, 'full'), b)) + r' \\',
                          ROWKEY[lab]))
    rows.append(keyed(' & '.join(['All French characteristics']
                                 + _cells(D.usShockRow(df, ρ, 'All French characteristics', 'full'), b))
                      + r' \\[.5em]\hline\\[-.75em]', ROWKEY['All French characteristics']))
    rows.append(keyed(' & '.join(['France (own calibration)']
                                 + _cells(D.usShockRow(df, ρ, 'France (own calibration)', 'full'), b)) + r' \\',
                      ROWKEY['France (own calibration)']))
    design = (r' pension design is the separate counterfactual of Table~\ref{table:US:pensChars}.'
              if host == 'US' else '.')
    note = (r'\item \textit{Note:} $\rho = ' + C.num(ρ, 1) + r'$, full effect. Each row is a separate equilibrium path: '
            r'the borrowed characteristics hold throughout and the economy starts from its own steady '
            r'state, so the row describes a country that has always had this mix rather than ' + name
            + r' hit by a surprise in 2020. Income '
            r'distribution replaces $\eta_i$ with France\textquotesingle s while holding $X_i$ \emph{and} '
            r'holding $\theta$ at ' + theName + r' design, so it is a change in inequality alone'
            + (';' if host == 'US' else '') + design
            + r' Leisure preferences rescales every $X_i$ to France\textquotesingle s population-weighted '
            r'mean $X$ at the productivity level of the income row; it is a pure rescaling of the hours '
            r'unit and moves hours and nothing else. All French characteristics '
            r'imposes France\textquotesingle s $\eta_i$, level of $X_i$ and voting weights $\mu_i$ at once. '
            r'The last row is France\textquotesingle s own calibrated path, its savings rate reported as '
            r'the distance from ' + theName + r' baseline.'
            + (r' France\textquotesingle s income groups are cut at the UK\textquotesingle s own income '
               r'percentiles here (table \ref{table:a_US:CalibFRUK}).' if host == 'UK' else '')
            + C.variantNote(commonX))
    return _xwrap(host + '_OtherShocks' + C.variantSuffix(commonX), df.attrs['source'],
                  'French income distribution, leisure preferences and voting patterns in ' + name
                  + C.variantCaption(commonX),
                  'table:' + host + ':otherShocks' + C.variantSuffix(commonX), 'lYYY', SHOCKHEAD,
                  '\n'.join(rows), note)


def usOtherShocks(commonX = None):
    r""" Table \ref{table:US:otherShocks}. """
    return _otherShocks(commonX, host = 'US')


def ukOtherShocks(commonX = None):
    r""" Table \ref{table:UK:otherShocks}: the same exercise with the UK as host (config.US['ukHost']). """
    return _otherShocks(commonX, host = C.US['ukHost'])


# ---------------------------------------------------------------------------------------------------
def _crraTable(name, caption, label, scenarios, commonX = None, host = 'US'):
    """ A rho-stacked table over config.US['rhoTable'], laid out like the ESC tables: a baseline group
    with one row per rho (levels), then one group per scenario whose savings cell is the change against
    THAT rho's baseline. The group name is printed against the middle rho. Full effect only -- the
    decomposition is the LOG tables' job.

    One baseline per rho, not one shared row: tau and the workweek are common across rho (a target and a
    normalisation), the savings rate is not -- beta is identified by R, so the baseline savings rate is
    a prediction that falls with rho. Differencing every rho against the rho = 1 level reversed the sign
    of the theta rows at rho = 2 and put +-0.8 p.p. on the (then printed) leisure row, which cannot move
    savings. """
    commonX = C.US['commonX'] if commonX is None else commonX
    df = D.usShocks(commonX = commonX, host = host)
    ρs = C.US['ρTable']
    mid = len(ρs)//2
    groups = [('Baseline', None)] + list(scenarios)
    out = []
    for lab, scen in groups:
        for k, ρ in enumerate(ρs):
            b = D.usBaseline(df, ρ)
            cells = _cells(b) if scen is None else _cells(D.usShockRow(df, ρ, scen, 'full'), b)
            out.append(keyed(' & '.join([lab if k == mid else '', C.num(ρ, 1)] + cells)
                             + r' \\' + (r'[.5em]\hline\\[-.75em]' if k == len(ρs)-1 else ''),
                             rowKey('baseline' if scen is None else ROWKEY[scen], ρ)))
    note = (r'\item \textit{Note:} Every $\rho$ is separately calibrated. Every scenario row reports the '
            r'change in the savings rate against the baseline at the same $\rho$, in percentage points.'
            + C.variantNote(commonX))
    return _xwrap(name + C.variantSuffix(commonX), df.attrs['source'],
                  caption + C.variantCaption(commonX), label + C.variantSuffix(commonX), 'YYYYY',
                  [r'\textbf{Scenario}', r'\textbf{CRRA} ($\rho$)', r'\textbf{Tax rate}',
                   r'\textbf{Savings rate}', r'\textbf{Avg. workweek}'], '\n'.join(out), note)


def usCrraPensChars(commonX = None):
    r""" Table \ref{table:US:CRRA:pensChars}. """
    return _crraTable('US_CRRA_PensChars',
                      r'Does CRRA matter for the effect of pension design ($\theta$) in US -- {}'
                      .format(C.usCalendar()['year0']), 'table:US:CRRA:pensChars',
                      [(r'$\theta = 0$', r'$\theta = 0$'), (r'$\theta = 1$', r'$\theta = 1$')],
                      commonX = commonX)


def usCrraAgeing(commonX = None):
    r""" Table \ref{table:US:CRRA:ageing}. """
    return _crraTable('US_CRRA_Ageing',
                      'Does CRRA matter for the effect of ageing in US -- {}'
                      .format(C.usCalendar()['year0']), 'table:US:CRRA:ageing',
                      [('Mild ageing', 'Mild ageing'), ('Acute ageing', 'Acute ageing')],
                      commonX = commonX)


def usCrraOtherShocks(commonX = None):
    r""" Table \ref{table:US:CRRA:otherShocks}. """
    return _crraTable('US_CRRA_OtherShocks',
                      'Does CRRA matter for French characteristics imposed on the US -- {}'
                      .format(C.usCalendar()['year0']), 'table:US:CRRA:otherShocks',
                      [('Income distribution', 'Income distribution'), ('Voting', 'Voting')],
                      commonX = commonX)


def ukCrraPensChars(commonX = None):
    r""" Table \ref{table:UK:CRRA:pensChars} (online appendix): theta = 0 and theta = 1 on the UK host. """
    return _crraTable('UK_CRRA_PensChars',
                      r'Does CRRA matter for the effect of pension design ($\theta$) in the UK -- {}'
                      .format(C.usCalendar('UK')['year0']), 'table:UK:CRRA:pensChars',
                      [(r'$\theta = 0$', r'$\theta = 0$'), (r'$\theta = 1$', r'$\theta = 1$')],
                      commonX = commonX, host = C.US['ukHost'])


def ukCrraAgeing(commonX = None):
    r""" Table \ref{table:UK:CRRA:ageing} (online appendix): mild and acute ageing on the UK host. """
    return _crraTable('UK_CRRA_Ageing',
                      'Does CRRA matter for the effect of ageing in the UK -- {}'
                      .format(C.usCalendar('UK')['year0']), 'table:UK:CRRA:ageing',
                      [('Mild ageing', 'Mild ageing'), ('Acute ageing', 'Acute ageing')],
                      commonX = commonX, host = C.US['ukHost'])


def ukCrraOtherShocks(commonX = None):
    r""" Table \ref{table:UK:CRRA:otherShocks}: the UK-host counterpart. """
    return _crraTable('UK_CRRA_OtherShocks',
                      'Does CRRA matter for French characteristics imposed on the UK -- {}'
                      .format(C.usCalendar('UK')['year0']), 'table:UK:CRRA:otherShocks',
                      [('Income distribution', 'Income distribution'), ('Voting', 'Voting')],
                      commonX = commonX, host = C.US['ukHost'])


# ---------------------------------------------------------------------------------------------------
COUNTRYNAME = {'US': 'US', 'UK': 'UK', 'FR': 'France', 'FRUK': 'France, UK income groups',
               'UKUS': 'UK, US income groups'}


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
        shared('beta', r'$\beta$', '30-year interest rate (US)', 'β'),
        shared('rho', r'$\rho$', 'Log-GHH preferences', 'ρ', fmt = '{:g}'.format),
        shared('xi', r'$\xi$', 'Frisch elasticity of labor supply', 'ξ'),
        shared('alpha', r'$\alpha$', 'Capital income share', 'α'),
    ]
    header = ([r'\textbf{Parameter}'] + [r'\textbf{' + COUNTRYNAME[k] + '}' for k in cols]
              + [r'\textbf{Identified by}'])
    # The one note that spells the variant out; every other US table points here (config.variantNote).
    note = (r'\item \textit{Note:} $X$ is the '
            r'population-weighted mean of $X_i$; its level is the hours unit, pinned for France and the '
            r'UK by targeting average hours relative to the US rather than in levels. The lower panel is '
            r'common to the three countries; $\beta$ is calibrated for the US and imposed on the other two.'
            + C.variantNote(commonX, full = True))
    return (BANNER.format(name = 'USUKFRCalibration' + C.variantSuffix(commonX),
                          src = 'results/paper/usCalibrationSummary.csv')
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{Calibration, US, UK, and France' + C.variantCaption(commonX) + '}\n'
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
            + '\\caption{Household heterogeneity -- ' + COUNTRYNAME[country]
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
# Endogenous system characteristics (app:ESC). All four experiment tables share one builder: rows
# grouped by rho, four readings per group -- the endogenous-theta baseline, the counterfactual with
# theta PINNED at its exogenous value, the counterfactual with theta CHOSEN, and (in the French tables)
# France's own calibrated path as the endpoint. Reported at t0 (2020): every counterfactual is a new
# equilibrium path whose political choice binds from the first period, so the design in force in 2020
# is itself an outcome (python/US/runESC.py's shocks stage).
# ---------------------------------------------------------------------------------------------------
ESCHEAD = [r'\textbf{Scenario}', r'\textbf{CRRA} ($\rho$)', r'$\bm{\theta}$ \textbf{(2020)}',
           r'\textbf{Tax rate}', r'\textbf{Savings rate}', r'\textbf{Avg. workweek}']


def _escCells(r, base = None):
    """ The design in force at t0 and the three t0 outcomes of one escExperiments row. The csv's
    savings rate is s/(w h) and is converted to s/Y here; with `base` (that rho's baseline row) it is
    reported as the change against it in p.p. The design prints to three decimals (style guide §3). """
    sr = D.escSavingsOverY(r['sr_t0'])
    srCell = C.pct(sr) if base is None else C.pp(sr - D.escSavingsOverY(base['sr_t0']))
    return [C.num(r['θ_t0'], 3), C.pct(r['τ_t0']), srCell, C.num(r['ww_t0'])]


ESCANCHOR = 'table:US_ESC:ageing'    # the first ESC table; the other three refer to its note


def _wedgeSymbol(spec = None):
    """ The calibrated cost parameter's symbol under `spec` (config.US['esc']['spec'] by default): lambda
    under 'size', p under 'scale'. Both live in the csvs' `p` column. """
    spec = C.US['esc']['spec'] if spec is None else spec
    return r'\lambda' if spec == 'size' else 'p'


def _costSentence(spec = None):
    """ The one sentence a table note spends on the cost specification under `spec`, pointing at the
    calibration table for the parameter. """
    spec = C.US['esc']['spec'] if spec is None else spec
    if spec == 'size':
        return (r'The deadweight cost $f(\theta_t, \tau_t)$ of \eqref{eq:esc:budget} is quadratic in the '
                r'implicit tax the flat component levies and scaled by the size of the system, '
                r'$f = \exp\{-\tfrac12 \lambda \tau_t \tilde V (1-\theta_t)^2\}$, with $\lambda$ '
                r'calibrated per $\rho$ (table \ref{table:US_ESC:calibration}).')
    return (r'The proportional deadweight cost $f(\theta) = \phi + (1-\phi)\theta^{p}$ of '
            r'\eqref{eq:esc:budget}, with $\phi = ' + C.num(C.US['esc']['phi'], 1) + r'$ imposed and $p$ '
            r'calibrated per $\rho$ (table \ref{table:US_ESC:calibration}).')


def _escTable(name, scenarioKey, caption, label, extraNote = '', france = False, anchor = False, host = 'US'):
    """ Rows grouped by reading, one row per rho within each. The savings change in every non-baseline
    row is against the printed baseline of the same rho -- the endogenous-theta reading, which is also
    what figuresUS.escOverview differences against. host 'UK': the UK-host runs at the UK's own cost
    parameter (escExperimentsUK.csv); `anchor` then means the UK anchor, UKANCHOR, which prints the UK's
    lambda per rho. Row keys `baseline|pinned|chosen|france@<rho>`. """
    df = D.escExperiments(host)
    spec, ρs = C.US['esc']['spec'], C.US['esc']['ρTable']
    # The ESC leg runs under the headline calibration variant only -- there is no twin to select here,
    # and escRow filters on it so a stale vector-X row cannot be read in its place.
    mid = len(ρs)//2
    # (label, scenario, pinned, row-key block)
    readings = [('Baseline', 'baseline', False, 'baseline'),
                (r'Exogenous $\theta$', scenarioKey, True, 'pinned'),
                (r'Endogenous $\theta$', scenarioKey, False, 'chosen')]
    if france:
        readings.append(('France', 'France', True, 'france'))
    out = []
    for lab, scen, pinned, block in readings:
        for k, ρ in enumerate(ρs):
            r = D.escRow(df, ρ, spec, scen, pinned)
            base = None if scen == 'baseline' else D.escRow(df, ρ, spec, 'baseline', False)
            out.append(keyed(' & '.join([lab if k == mid else '', C.num(ρ, 1)] + _escCells(r, base))
                             + r' \\' + ('[.5em]\\hline\\\\[-.75em]' if k == len(ρs)-1 else ''),
                             rowKey(block, ρ)))
    # Section sec:esc already states what every one of these tables is -- separate equilibrium paths,
    # read at 2020, pinned against chosen design -- so the note carries only what the text does not: the
    # cost specification and the units. ESCANCHOR spells those out once; the other three point at it.
    if anchor and host == 'US':
        note = (r'\textit{Note:} ' + _costSentence(spec) + r' Each $\rho$ is separately calibrated and its '
                r'workweek normalised against its own baseline. The savings rate is savings relative to '
                r'GDP; the baseline rows report its level and every other row the change against the '
                r'baseline at the same $\rho$, in percentage points.')
    elif anchor:
        cal = D.escCalibrationHost(host, spec = spec)
        miss = [ρ for ρ in ρs if ρ not in cal]
        if miss:
            raise D.MissingInput('the {} own cost calibration at ρ = {} (escCountry.csv, escCalibrationCRRA{}.csv)'
                                 .format(host, miss, host))
        sym = _wedgeSymbol(spec)
        note = (r'\textit{Note:} The cost specification and the units are those of table \ref{' + ESCANCHOR
                + r'}, at the UK\textquotesingle s own cost parameter, calibrated per $\rho$ so that the UK '
                r'electorate re-elects its observed design $\theta^{\ast} = '
                + C.num(float(cal[C.US['ρBaseline']]['θStar']), 3) + r'$: $' + sym + ' = '
                + ', '.join(C.num(float(cal[ρ]['p']), 3) for ρ in ρs) + r'$ at $\rho = '
                + ', '.join(C.num(ρ, 1) for ρ in ρs) + r'$, with $\beta$ imposed from the US and $\omega$ '
                r'recalibrated at each trial value. France\textquotesingle s income groups are cut at the '
                r'UK\textquotesingle s own income percentiles (table \ref{table:a_US:CalibFRUK}).')
    else:
        note = (r'\textit{Note:} The cost specification' + ('' if host == 'US' else ', the cost parameter')
                + r' and the units are those of table \ref{' + (ESCANCHOR if host == 'US' else UKANCHOR)
                + r'}.')
    note += extraNote + C.variantNote(C.US['commonX'])
    if france:
        hostName = HOSTNAME[host] if HOSTNAME[host].startswith('the ') else 'the ' + HOSTNAME[host]
        note += (r" The France row is France's own calibrated path rather than a counterfactual on "
                 + hostName + r' model: it carries France\textquotesingle s own $\omega$ as well as its '
                 r'characteristics, and its workweek is a calibration target rather than a prediction.')
    return _xwrap(name, df.attrs['source'], caption, label, 'p{2.6cm}YYYYY',
                  ESCHEAD, '\n'.join(out), note, width = r'\textwidth')


def escAgeing():
    r""" Table \ref{table:US_ESC:ageing}. """
    return _escTable('US_ESC_Ageing', 'acute',
                     'Endogenous design and ' + LQ + 'acute ageing' + RQ + ' in US',
                     'table:US_ESC:ageing',
                     r' The ' + LQ + 'acute ageing' + RQ + r' scenario sets $\nu_t = 1$ throughout.',
                     anchor = True)


def escIncomeDistr():
    r""" Table \ref{table:US_ESC:incomeDistr}. """
    return _escTable('US_ESC_IncomeDistr', 'frIncome',
                     'Endogenous design and the French income distribution in US',
                     'table:US_ESC:incomeDistr', france = True)


def escVoting():
    r""" Table \ref{table:US_ESC:voting}. """
    return _escTable('US_ESC_Voting', 'frVoting',
                     'Endogenous design and French voting patterns in US',
                     'table:US_ESC:voting', france = True)


def escFrenchAll():
    r""" Table \ref{table:US_ESC:frenchAll}: all three French characteristics at once, against France.

    The table the new-path convention is for. The single-characteristic tables ask what one borrowed
    feature does; this one asks how far the observable characteristics take the US towards France, and
    the France row says how much is left over for the political weight and the design. """
    return _escTable('US_ESC_FrenchAll', 'frAll',
                     'Endogenous design and all French characteristics in US',
                     'table:US_ESC:frenchAll',
                     r' The scenario replaces the US $\eta_i$, the level of $X_i$ and the voting weights '
                     r'$\mu_i$ with France\textquotesingle s simultaneously.', france = True)


# The UK counterparts (appendix app:UKUS): France's characteristics on the UK at the UK's OWN cost
# parameter, France cut at the UK's income groups. The first carries the UK's lambda per rho.
UKANCHOR = 'table:UK_ESC:incomeDistr'


def ukEscIncomeDistr():
    r""" Table \ref{table:UK_ESC:incomeDistr}. """
    return _escTable('UK_ESC_IncomeDistr', 'frIncome',
                     'Endogenous design and the French income distribution in the UK',
                     UKANCHOR, france = True, anchor = True, host = 'UK')


def ukEscVoting():
    r""" Table \ref{table:UK_ESC:voting}. """
    return _escTable('UK_ESC_Voting', 'frVoting', 'Endogenous design and French voting patterns in the UK',
                     'table:UK_ESC:voting', france = True, host = 'UK')


def ukEscFrenchAll():
    r""" Table \ref{table:UK_ESC:frenchAll}. """
    return _escTable('UK_ESC_FrenchAll', 'frAll', 'Endogenous design and all French characteristics in the UK',
                     'table:UK_ESC:frenchAll',
                     r' The scenario replaces the UK $\eta_i$, the level of $X_i$ and the voting weights '
                     r'$\mu_i$ with France\textquotesingle s simultaneously.', france = True, host = 'UK')


def escCalibrationTable(spec = None):
    r""" Table \ref{table:US_ESC:calibration}: the calibrated cost parameter per rho (lambda under 'size',
    p under 'scale'), the design theta* the electorate re-elects, the share of revenue that reaches
    households at that design and at theta = 0 (datasets.escWedge), and Vtilde.

    theta* is the data's own 0.738 at every rho because the cost is proportional and cancels from the
    replacement-rate ratio; the column is the check that it did. `spec` defaults to the paper's
    (config.US['esc']['spec']); passing the comparison spec exercises the builder on its rows. """
    spec = C.US['esc']['spec'] if spec is None else spec
    cal = D.escCalibration()
    sym = _wedgeSymbol(spec)
    rows = []
    for ρ in C.US['esc']['ρTable']:
        if (ρ, spec) not in cal:
            raise D.MissingInput('escCalibration ({}, {})'.format(ρ, spec))
        r = cal[(ρ, spec)]
        w = D.escWedge(r, spec)
        rows.append(keyed(' & '.join([C.num(ρ, 1), C.num(float(r['p']), 3), C.num(float(r['θStar']), 3),
                                      C.num(w['fStar'], 3), C.num(w['f0'], 3),
                                      '--' if w['Vtilde'] is None else C.num(w['Vtilde'], 3)]) + r' \\',
                          rowKey('rho', ρ)))
    header = ' & '.join([r'\textbf{CRRA} ($\rho$)', '$' + sym + '$', r'$\theta^{\ast}$',
                         r'$f(\theta^{\ast})$', '$f(0)$', r'$\tilde V$'])
    if spec == 'size':
        form = (r'$f(\theta, \tau) = \exp\{-\tfrac12 \lambda \tau \tilde V (1-\theta)^2\}$ with '
                r'$\tilde V = \sum_i \gamma_i (y_i - 1)^2 / y_i$ the dispersion of relative labour '
                r'incomes; $f(\theta^{\ast})$ and $f(0)$ are read at the 2020 tax rate, so $1 - f$ is the '
                r'share of revenue lost at the observed design and at a flat benefit')
    else:
        form = (r'$f(\theta) = \phi + (1-\phi)\theta^{p}$ with $\phi = ' + C.num(C.US['esc']['phi'], 1)
                + r'$ imposed, so $f(0) = \phi$')
    note = (r'\textit{Note:} ' + form + r'; $' + sym + r'$ is calibrated so the design in force in 2020 '
            r'is the observed one, with $(\beta, \omega)$ recalibrated at each trial value. The cost is '
            r'proportional, so it cancels from the replacement-rate ratio and $\theta^{\ast}$ is the '
            r'data\textquotesingle s own. Without the cost the choice would be in the corner $\theta = 0$ '
            r'for every $\rho$.' + C.variantNote(C.US['commonX']))
    return _xwrap('US_ESC_Calibration', 'results/esc/escCalibration{,CRRA}.csv',
                  'The calibrated cost of redistributive funds',
                  'table:US_ESC:calibration', 'YYYYYY', header, '\n'.join(rows), note)


# escCountry.csv's economy keys, in the order the table prints them, their labels and row keys.
COUNTRYROWS = (('UK', 'UK', 'gbr'), ('FR', 'France', 'fra'), ('UKUS', 'UK at US income groups', 'ukus'))


def escCountryTable(spec = None):
    r""" Table \ref{table:US_ESC:country}: the cross-country test of the cost specification. One row per
    economy -- the UK, France, and the UK regrouped at US income percentiles -- with its observed design
    and 2020 tax rate, the design its electorate chooses under the US-calibrated parameter, and the
    parameter at which it re-elects its own design (`--` where no finite value does: France's observed
    design is the corner theta = 1). Vtilde is printed when the csv carries it (rows written since the
    'size' spec). rho = 1 (LOG) only: the country stage has no CRRA counterpart. """
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
        cells = [name, C.num(float(u['θStar']), 3), C.pct(float(u['τ']), 1), C.num(float(u['choice']), 3),
                 '--' if own.empty else C.num(float(own.iloc[-1]['p']), 3)]
        if hasV:
            cells.append('--' if u['Vtilde'] != u['Vtilde'] else C.num(float(u['Vtilde']), 3))
        rows.append(keyed(' & '.join(cells) + r' \\', rk))
    pUS = float(us.iloc[-1]['p'])
    header = [r'\textbf{Economy}', r'$\theta^{\ast}$ \textbf{observed}', r'\textbf{Tax rate}',
              r'$\theta$ \textbf{chosen, US} $' + sym + '$', r'\textbf{Own} $' + sym + '$'] \
             + ([r'$\tilde V$'] if hasV else [])
    if spec == 'size':
        gap = (r' No finite $\lambda$ makes France re-elect its observed design: it is the corner '
               r'$\theta = 1$, and under a cost quadratic in the redistribution performed the first unit '
               r'of redistribution is free at the margin.')
    else:
        gap = (r' No finite $p$ makes France re-elect its observed design, the corner $\theta = 1$.')
    note = (r'\textit{Note:} ' + _costSentence(spec) + r' Each economy is its own calibration at $\rho = 1$ '
            r'($\beta$ imposed from the US, $\omega$ its own; table \ref{table:US:Calib}); the UK at US '
            r'income groups is the UK workbook regrouped at the US income percentiles. ' + LQ + 'Chosen' + RQ
            + r' is the design in force in 2020 on the economy\textquotesingle s own freely simulated path '
            r'under the US parameter $' + sym + ' = ' + C.num(pUS, 3) + r'$, to be read against the observed '
            r'one; ' + LQ + 'own' + RQ + r' is the value at which that path re-elects the observed design, '
            r'with $\omega$ recalibrated at each trial value.' + gap + C.variantNote(C.US['commonX']))
    return _xwrap('US_ESC_Country', 'results/esc/escCountry.csv',
                  'The UK and France under the US cost of redistribution',
                  'table:US_ESC:country', 'l' + 'Y'*(len(header) - 1), header, '\n'.join(rows), note,
                  width = r'\textwidth')


# The chosen-design columns of US_ESC_ScaleWedge: (escExperiments scenario, header).
SPECCOLUMNS = [('acute', 'Acute ageing'), ('frIncome', 'French income distribution'),
               ('frVoting', 'French voting patterns')]
SPECROWS = {'size': 'redistribution', 'scale': 'the design'}    # how the table names each cost spec


def escScaleWedge():
    r""" Table \ref{table:US_ESC:scaleWedge}: the paper's cost specification (config.US['esc']['spec'],
    'size') against the comparison spec ('scale', comparisonSpec), one block of rows per spec: the
    calibrated parameter per rho, the design it re-elects, the share of revenue reaching households at that
    design and at theta = 0 (datasets.escWedge), and the design chosen in 2020 under acute ageing and
    France's income distribution and voting patterns (SPECCOLUMNS).

    Rows: every rho of config.US['esc']['ρTable'] whose calibration and three chosen readings are on file at
    the published method; rho = 1 (LOG) is required for both specs, the CRRA rows are printed when present.
    Row keys `size@<rho>`, `scale@<rho>`. """
    specs = [C.US['esc']['spec'], C.US['esc']['comparisonSpec']]
    cal = D.escCalibration()
    df = D.escExperiments()
    ρs = C.US['esc']['ρTable']
    blocks = []
    for spec in specs:
        rows = []
        for ρ in ρs:
            try:
                r = cal[(ρ, spec)]
                chosen = [float(D.escRow(df, ρ, spec, s, False)['θ_t0']) for s, _ in SPECCOLUMNS]
            except (KeyError, D.MissingInput):
                if ρ == C.US['ρAnchor']:
                    raise D.MissingInput('escCalibration and escExperiments (ρ={}, {}, {})'
                                         .format(ρ, spec, ', '.join(s for s, _ in SPECCOLUMNS)))
                continue
            w = D.escWedge(r, spec)
            rows.append([ρ, [C.num(ρ, 1), C.num(float(r['p']), 3), C.num(float(r['θStar']), 3),
                             C.num(w['fStar'], 3), C.num(w['f0'], 3)] + [C.num(θ, 3) for θ in chosen]])
        mid = len(rows)//2
        blocks.append('\n'.join(keyed(' & '.join([SPECROWS[spec] if k == mid else ''] + cells) + r' \\',
                                      rowKey(spec, ρ)) for k, (ρ, cells) in enumerate(rows)))
    header = (r' & & \multicolumn{4}{c}{\textbf{Calibration}} & '
              r'\multicolumn{3}{c}{$\theta$ \textbf{chosen (2020)}} \\' + '\n'
              r'\cmidrule(lr){3-6}\cmidrule(lr){7-9}' + '\n'
              r'\textbf{Cost on} & \textbf{CRRA} ($\rho$) & $\lambda$, $p$ & $\theta^{\ast}$ & '
              r'$f(\theta^{\ast})$ & $f(0)$ & ' + ' & '.join(r'\textbf{' + h + '}' for _, h in SPECCOLUMNS))
    note = (r'\textit{Note:} Two specifications of the deadweight cost $f$ of \eqref{eq:esc:budget}, each '
            r'with one parameter calibrated per $\rho$ so that the design in force in 2020 is the observed '
            r'$\theta^{\ast}$, with $(\beta, \omega)$ recalibrated at each trial value. The cost on '
            r'redistribution is that of table \ref{table:US_ESC:calibration}, $f(\theta, \tau) = '
            r'\exp\{-\tfrac12 \lambda \tau \tilde V (1-\theta)^2\}$: quadratic in the implicit tax the flat '
            r'component levies and scaled by the size of the system, so nothing is lost when nothing is '
            r'redistributed. The cost on the design is $f(\theta) = \phi + (1-\phi)\theta^{p}$ with $\phi = '
            + C.num(C.US['esc']['phi'], 1) + r'$ imposed: a flat benefit forfeits a share $1 - \phi$ of '
            r'revenue whatever it redistributes. $f(\theta^{\ast})$ and $f(0)$ are the shares of revenue '
            r'that reach households at the observed design and at a flat benefit; the cost on '
            r'redistribution is read at the 2020 tax rate. The last three columns are the design in force in 2020 '
            r'when the electorate chooses it; under the cost on redistribution they are the '
            r'endogenous-$\theta$ rows of tables \ref{table:US_ESC:ageing}, \ref{table:US_ESC:incomeDistr} '
            r'and \ref{table:US_ESC:voting}.' + C.variantNote(C.US['commonX']))
    return _xwrap('US_ESC_ScaleWedge', 'results/esc/escCalibration{,CRRA}.csv, escExperiments.csv',
                  'Two specifications of the deadweight cost: calibration and the chosen design',
                  'table:US_ESC:scaleWedge', 'lcYYYYYYY', header, '\n\\midrule\n'.join(blocks), note,
                  width = r'\textwidth')


def ukEscCalibrationTable(spec = None):
    r""" Table \ref{table:UK_ESC:calibration}: the UK-only predecessor of escCountryTable, in
    escCalibrationTable's previous layout -- the wedge p calibrated so that the UK electorate re-elects
    the UK's own observed design theta*, under the 'scale' form f = phi + (1-phi) theta^p. Not registered
    in build.py since 2026-09-24; kept callable on the comparison spec's rows
    (config.US['esc']['comparisonSpec'], the default here).

    rho = 1 only: the country stage (python/US/runESC.stageCountry) runs under LOG and has no CRRA
    counterpart, so the table prints whatever rho the csv carries rather than config's rhoTable, and
    the note says so. The US-wedge reading -- the UK's choice with the US's p imposed -- goes into the
    note. France has no own-wedge row (its observed design IS the corner) and is not printed. """
    spec = C.US['esc']['comparisonSpec'] if spec is None else spec
    df = D.escCountry(spec = spec)
    φ = C.US['esc']['phi']
    own = df[(df['country'] == 'UK') & (df['wedgeFrom'] == 'own')]
    us = df[(df['country'] == 'UK') & (df['wedgeFrom'] == 'US')]
    if own.empty:
        raise D.MissingInput('escCountry (UK, own wedge, {}, phi={})'.format(spec, φ))
    rows = []
    for r in own.to_dict('records'):
        p, θ = float(r['p']), float(r['θStar'])
        rows.append(keyed(' & '.join([C.num(float(r['ρ']), 1), C.num(p, 3), C.num(θ, 3),
                                      C.num(φ + (1-φ)*θ**p, 3)]) + r' \\', rowKey('rho', float(r['ρ']))))
    header = ' & '.join([r'\textbf{CRRA} ($\rho$)', '$p$', r'$\theta^{\ast}$', r'$f(\theta^{\ast})$'])
    usNote = ''
    if not us.empty:
        u = us.iloc[-1]
        usNote = (r' With the US wedge imposed instead ($p = ' + C.num(float(u['p']), 3)
                  + r'$, Table~\ref{table:US_ESC:calibration}) the UK electorate\textquotesingle s choice is '
                  r'$\theta = ' + C.num(float(u['choice']), 3) + '$.')
    note = (r'\item \textit{Note:} As Table~\ref{table:US_ESC:calibration}, for the UK model: '
            r'$f(\theta) = \phi + (1-\phi)\theta^{p}$ with $\phi = ' + C.num(φ, 1) + r'$ imposed, $\beta$ '
            r'imposed from the US calibration at the same $\rho$, and $p$ calibrated so that the UK '
            r'electorate re-elects the UK\textquotesingle s observed design $\theta^{\ast}$, with $\omega$ '
            r'recalibrated at each trial value. Only $\rho = 1$ has been run for the UK.' + usNote
            + C.variantNote(C.US['commonX']))
    return _xwrap('UK_ESC_Calibration', 'results/esc/escCountry.csv',
                  'The calibrated cost of redistributive funds in the UK',
                  'table:UK_ESC:calibration', 'YYYY', header, '\n'.join(rows), note)
