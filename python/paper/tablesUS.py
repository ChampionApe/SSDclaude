r""" Table builders for the US/France/UK arm. tables.py is the Argentina arm; the two are separate
modules for the same reason runCalibration.py and runCalibrationUS.py are.

Each function returns the complete tex body of one file in writing/Paper/Tables/, reproducing the
STRUCTURE of the hand-written table it replaces (tabularx with Y columns, the same caption, label and
rules), so the paper's \ref{}s keep resolving and a diff shows moved numbers rather than a re-layout.

TWO CONVENTIONS CARRIED FROM python/US, both of which a builder could silently get wrong:

  * `Savings rate` is s/(w*h) -- savings over gross labour income -- not Base.savingsRate's s/Y. They
    differ by exactly (1-alpha), and the experiment csv already carries the paper's version. Do not
    divide again here.
  * `Avg. workweek` is normalised against each rho's OWN baseline, inside the experiment script. Under
    vector X the level of hbar is not identified, so there is no expression that converts it to hours;
    the observed workweek is a reference point, not a unit. Stage (iii) therefore reads `workweek`
    straight out of the csv and must never re-derive it from hbar.
"""
import numpy as np

import config as C
import datasets as D
from tables import BANNER, LQ, RQ


def _xwrap(name, src, caption, label, colspec, header, body, note = None):
    """ One threeparttable around a tabularx, matching the hand-written US tables' layout. """
    tn = ('\\begin{tablenotes}\n\\footnotesize\n' + note + '\n\\end{tablenotes}\n') if note else ''
    return (BANNER.format(name = name, src = src)
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{' + caption + '}\n\\label{' + label + '}\n'
            + '\\renewcommand{\\arraystretch}{1.25}\n'
            + '\\begin{tabularx}{.9\\textwidth}{' + colspec + '}\n\\toprule\n'
            + ' & '.join(header) + ' \\\\\n\\midrule \n'
            + body + '\n\\bottomrule\n\\end{tabularx}\n' + tn
            + '\\end{threeparttable}\n\\end{table}\n')


def _cells(r):
    """ The three reported quantities of one shock row, already formatted. """
    return [C.pct(r['τ']), C.pct(r['sr']), C.num(r['workweek'])]


def _shockRows(df, ρ, scenarios, baselineLabel):
    """ The 'Full effect' / 'Economic equilibrium effect' block shared by US_PensChars and US_Ageing. """
    line = lambda lab, r: ' & '.join([lab] + _cells(r)) + r' \\'
    out = [line(baselineLabel, D.usBaseline(df, ρ)) + '[1.25ex]']
    for effect, head in (('full', 'Full effect:'), ('ee', 'Economic equilibrium effect:')):
        out.append(r'\multicolumn{4}{l}{\textit{' + head + r'}} \\\hline')
        for lab, scen in scenarios:
            out.append(line(lab, D.usShockRow(df, ρ, scen, effect)))
        out[-1] += '[1.25ex]'
    return '\n'.join(out)


SHOCKHEAD = [r'\textbf{Scenario}', r'\textbf{Tax rate}', r'\textbf{Savings rate}',
             r'\textbf{Avg. workweek}']


# ---------------------------------------------------------------------------------------------------
def usPensChars():
    r""" Table \ref{table:US:pensChars}: theta = 0 and theta = 1 in the US, both effects, at the
    baseline rho. """
    ρ = C.US['ρBaseline']
    df = D.usShocks()
    θ0 = D.usCalibrationSummary()['US']['θ']
    body = _shockRows(df, ρ, [(r'$\theta = 0$', r'$\theta = 0$'), (r'$\theta = 1$', r'$\theta = 1$')],
                      r'$\theta = ' + C.num(θ0) + '$')
    note = (r'\item $\rho = ' + C.num(ρ, 1) + r'$. The economic-equilibrium rows hold $\tau$ at the '
            r'baseline path, so they isolate the response of savings and hours to $\theta$ alone; the '
            r'full rows re-optimise $\tau$ politically.')
    return _xwrap('US_PensChars', 'results/shocks/US_shocks.csv',
                  r'The effect of pension design ($\theta$) in US -- {}'.format(C.usCalendar()['year0']),
                  'table:US:pensChars', 'p{3cm}YYY', SHOCKHEAD, body, note)


def usAgeing():
    r""" Table \ref{table:US:ageing}: mild and acute ageing, both effects, at the baseline rho. """
    ρ = C.US['ρBaseline']
    year0 = C.usCalendar()['year0']
    body = _shockRows(D.usShocks(), ρ,
                      [(r'Mild ageing\tnote{a}', 'Mild ageing'),
                       (r'Acute ageing\tnote{b}', 'Acute ageing')], 'Baseline')
    note = (r'\item[a] The ' + LQ + 'mild ageing' + RQ + r' scenario refers to the case with $\nu_t$ set '
            r'at $(1+\nu_t^{base})/2$ from ' + str(year0) + ' and onward.\n'
            r'\item[b] The ' + LQ + 'acute ageing' + RQ + r' scenario refers to $\nu_t = 1$ from '
            + str(year0) + ' and onward.')
    return _xwrap('US_Ageing', 'results/shocks/US_shocks.csv',
                  'The effect of ageing in US -- {}'.format(year0),
                  'table:US:ageing', 'p{3cm}YYY', SHOCKHEAD, body, note)


def usOtherShocks():
    r""" Table \ref{table:US:otherShocks}: French income distribution, leisure preferences and voting
    imposed on the US model, at the baseline rho.

    Full effect only, following the paper, which reports that the two effects are not informative apart
    for these three -- they work in the same direction and are quantitatively minor. The
    economic-equilibrium rows ARE in results/shocks/US_shocks.csv if that judgement is revisited. """
    ρ = C.US['ρBaseline']
    df = D.usShocks()
    rows = [' & '.join(['Baseline'] + _cells(D.usBaseline(df, ρ))) + r' \\']
    for lab in ('Income distribution', 'Leisure preferences', 'Voting'):
        rows.append(' & '.join([lab] + _cells(D.usShockRow(df, ρ, lab, 'full'))) + r' \\')
    note = (r'\item $\rho = ' + C.num(ρ, 1) + r'$, full effect. Leisure preferences rescales every '
            r'$X_i$ to France''s population-weighted mean $X$, which is a pure change of the hours '
            r'unit, so the tax and savings rates stay exactly at baseline and only hours move. Income '
            r'distribution replaces $\eta_i$ with France''s while holding $X_i$; $\theta$ is then '
            r're-derived from the unchanged replacement-rate ratio and falls, so this row bundles a '
            r'pension-design change with the inequality change (see python/US/shocks.py).')
    return _xwrap('US_OtherShocks', 'results/shocks/US_shocks.csv',
                  'French income distribution, leisure preferences, and voting patterns in US',
                  'table:US:otherShocks', 'lYYY', SHOCKHEAD, '\n'.join(rows), note)


# ---------------------------------------------------------------------------------------------------
def _crraTable(name, caption, label, scenarios):
    """ A rho-stacked table: one group of rows per scenario, the scenario name printed against the
    middle rho, over config.US['rhoTable']. Full effect only -- the decomposition is the LOG tables' job.
    """
    df = D.usShocks()
    ρs = C.US['ρTable']
    mid = len(ρs)//2
    b = D.usBaseline(df, C.US['ρBaseline'])
    out = [' & '.join(['Baseline', ''] + _cells(b)) + r' \\[.5em]\hline\\[-.75em]']
    for lab, scen in scenarios:
        for k, ρ in enumerate(ρs):
            r = D.usShockRow(df, ρ, scen, 'full')
            out.append(' & '.join([lab if k == mid else '', C.num(ρ, 1)] + _cells(r))
                       + r' \\' + (r'[.5em]\hline\\[-.75em]' if k == len(ρs)-1 else ''))
    note = (r'\item The baseline row is at $\rho = ' + C.num(C.US['ρBaseline'], 1)
            + r'$, the log case, where the calibration targets are hit exactly. Every $\rho$ is '
            r'separately calibrated (results/calibration/US\_rhoGrid.csv) and its workweek is '
            r'normalised against its own baseline, so the columns are comparable down the table.')
    return _xwrap(name, 'results/shocks/US_shocks.csv', caption, label, 'YYYYY',
                  [r'\textbf{Scenario}', r'\textbf{CRRA} ($\rho$)', r'\textbf{Tax rate}',
                   r'\textbf{Savings rate}', r'\textbf{Avg. workweek}'], '\n'.join(out), note)


def usCrraPensChars():
    r""" Table \ref{table:US:CRRA:pensChars}. """
    return _crraTable('US_CRRA_PensChars',
                      r'Does CRRA matter for the effect of pension design ($\theta$) in US -- {}'
                      .format(C.usCalendar()['year0']), 'table:US:CRRA:pensChars',
                      [(r'$\theta = 0$', r'$\theta = 0$'), (r'$\theta = 1$', r'$\theta = 1$')])


def usCrraAgeing():
    r""" Table \ref{table:US:CRRA:ageing}. """
    return _crraTable('US_CRRA_Ageing',
                      'Does CRRA matter for the effect of ageing in US -- {}'
                      .format(C.usCalendar()['year0']), 'table:US:CRRA:ageing',
                      [('Mild ageing', 'Mild ageing'), ('Acute ageing', 'Acute ageing')])


def usCrraOtherShocks():
    r""" Table \ref{table:US:CRRA:otherShocks}. """
    return _crraTable('US_CRRA_OtherShocks',
                      'Does CRRA matter for French characteristics imposed on the US -- {}'
                      .format(C.usCalendar()['year0']), 'table:US:CRRA:otherShocks',
                      [('Income distribution', 'Income distribution'),
                       ('Leisure preferences', 'Leisure preferences'), ('Voting', 'Voting')])


# ---------------------------------------------------------------------------------------------------
COUNTRYNAME = {'US': 'US', 'UK': 'UK', 'FR': 'France'}


def usukfrCalibration():
    r""" Table \ref{table:US:Calib}: the headline calibration for the three countries.

    `X` is the POPULATION-WEIGHTED MEAN of X_i -- the only summary of a vector whose level IS the hours
    unit, and the one the leisure counterfactual is matched on. beta is added as a row the hand-written
    table omitted: it is imposed on France and the UK from the US calibration at the same rho, so
    printing it makes that visible rather than implicit. """
    c = D.usCalibrationSummary()
    cols = [k for k in ('US', 'UK', 'FR') if k in c]     # the hand-written column order
    year0 = C.usCalendar()['year0']

    def row(label, fn, target):
        return ' & '.join([label] + [fn(c[k]) for k in cols] + [target]) + r' \\'

    rows = [
        row(r'$\theta$', lambda r: C.num(r['θ']), 'Replacement rate dispersion'),
        row(r'$\omega$', lambda r: C.num(r['ω']), 'Social security tax rates'),
        row(r'$\beta$',  lambda r: C.num(r['β']), 'US: 30y interest rate; imposed on UK/FR'),
        row('$X$',       lambda r: C.num(r['Xbar'], 1), 'Avg.\\ workweek'),
        row(r'$\nu_{%d}$' % year0, lambda r: C.num(r['ν2020']),
            '30-year gross population growth rates'),
        row(r'$\eta_{H}/\eta_L$', lambda r: C.num(r['ηHηL']),
            'Relative productivity of high (H) to low (L) income groups'),
    ]
    header = ([r'\multicolumn{1}{c|}{\textbf{Parameter}}']
              + [r'\textbf{' + COUNTRYNAME[k] + '}' for k in cols] + [r'\textbf{Target}'])
    note = (r'\item $\rho = ' + C.num(C.US['ρBaseline'], 1) + r'$. $X$ is the population-weighted mean '
            r'of $X_i$; its level is the hours unit, pinned for France and the UK by targeting average '
            r'hours relative to the US rather than in levels. $\beta$ is calibrated for the US and '
            r'imposed on the other two, which is why $\omega$ is their only searched parameter.')
    return (BANNER.format(name = 'USUKFRCalibration', src = 'results/paper/usCalibrationSummary.csv')
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{Calibration, US, UK, and France}\n\\label{table:US:Calib}\n'
            + '\\renewcommand{\\arraystretch}{1.25}\n'
            + '\\begin{tabularx}{\\textwidth}{Y|' + 'Y'*len(cols) + '|p{6cm}}\n\\hline\n'
            + '& \\multicolumn{%d}{c|}{\\textbf{Country}} & \\\\ \\cline{2-%d}\n' % (len(cols), len(cols)+1)
            + ' & '.join(header) + ' \\\\ \\hline\n'
            + '\n'.join(rows) + '\n\\hline\n\\end{tabularx}\n'
            + '\\begin{tablenotes}\n\\footnotesize\n' + note + '\n\\end{tablenotes}\n'
            + '\\end{threeparttable}\n\\end{table}\n')


def _householdHeterogeneity(country, name, label):
    r""" One country's per-group table: gamma_i, X_i, eta_i, mu_i. """
    c = D.usCalibrationSummary()[country]
    spec = [(r'$\gamma_i$', 'γi', 2, 'Income percentiles.'),
            ('$X_i$',       'Xi', 1, 'Hours worked.'),
            (r'$\eta_i$',   'ηi', 2, 'Income distribution.'),
            (r'$\mu_i$',    'μi', 2, 'Voting propensity.')]
    rows = [' & '.join([lab] + [C.num(v, d) for v in c[key]] + [target]) + r' \\'
            for lab, key, d, target in spec]
    return (BANNER.format(name = name, src = 'results/paper/usCalibrationSummary.csv')
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{Household heterogeneity -- ' + COUNTRYNAME[country] + '}\n'
            + '\\label{' + label + '}\n\\renewcommand{\\arraystretch}{1.5}\n'
            + '\\begin{tabularx}{\\textwidth}{Y|YYY|p{5cm}}\n\\hline\n'
            + '& \\multicolumn{3}{c|}{\\textbf{Income group}} & \\\\ \\cline{2-4}\n'
            + ' & '.join([r'\multicolumn{1}{c|}{\textbf{Parameter}}',
                          r'\textbf{Low}', r'\textbf{Medium}', r'\textbf{High}', r'\textbf{Target}'])
            + ' \\\\ \\hline\n' + '\n'.join(rows) + '\n\\hline\n\\end{tabularx}\n'
            + '\\end{threeparttable}\n\\end{table}\n')


def usHouseholdHeterogeneity():
    return _householdHeterogeneity('US', 'US_householdheterogeneity', 'table:a_US:CalibUS')


def frHouseholdHeterogeneity():
    return _householdHeterogeneity('FR', 'FR_householdheterogeneity', 'table:a_US:CalibFR')


def ukHouseholdHeterogeneity():
    return _householdHeterogeneity('UK', 'UK_householdheterogeneity', 'table:a_US:CalibUK')
