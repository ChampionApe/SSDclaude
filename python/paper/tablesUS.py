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
    """ One threeparttable around a tabularx, matching the hand-written US tables' layout. `header` is a
    list of cells for one row, or a pre-formatted string when a table needs more than one header row
    (escCalibrationTable's grouped columns). """
    tn = ('\\begin{tablenotes}\n\\footnotesize\n' + note + '\n\\end{tablenotes}\n') if note else ''
    head = header if isinstance(header, str) else ' & '.join(header)
    return (BANNER.format(name = name, src = src)
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{' + caption + '}\n\\label{' + label + '}\n'
            + '\\renewcommand{\\arraystretch}{1.25}\n'
            + '\\begin{tabularx}{.9\\textwidth}{' + colspec + '}\n\\toprule\n'
            + head + ' \\\\\n\\midrule \n'
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
    note = (r'\item Each scenario is a separate equilibrium path: the demography holds throughout and '
            r'the economy starts from its own steady state, so the capital stock brought into '
            + str(year0) + r' is the counterfactual one rather than the baseline\textquotesingle s.' '\n'
            r'\item[a] The ' + LQ + 'mild ageing' + RQ + r' scenario refers to the case with $\nu_t$ set '
            r'at $(1+\nu_t^{base})/2$ throughout.' '\n'
            r'\item[b] The ' + LQ + 'acute ageing' + RQ + r' scenario refers to $\nu_t = 1$ throughout.')
    return _xwrap('US_Ageing', 'results/shocks/US_shocks.csv',
                  'The effect of ageing in US -- {}'.format(year0),
                  'table:US:ageing', 'p{3cm}YYY', SHOCKHEAD, body, note)


def usOtherShocks():
    r""" Table \ref{table:US:otherShocks}: French income distribution, leisure preferences and voting
    imposed on the US model, at the baseline rho.

    Full effect only, following the paper, which reports that the two effects are not informative apart
    for these three -- they work in the same direction and are quantitatively minor. The
    economic-equilibrium rows ARE in results/shocks/US_shocks.csv if that judgement is revisited.

    Two rows beyond the paper's original three: all three characteristics at once, and France's own
    calibrated path. Together they say how far the observable characteristics take the US towards France
    and how much is left for the political weight -- the comparison the new-path convention exists to
    make (python/US/runShocksUS.franceReference). """
    ρ = C.US['ρBaseline']
    df = D.usShocks()
    rows = [' & '.join(['Baseline'] + _cells(D.usBaseline(df, ρ))) + r' \\']
    for lab in ('Income distribution', 'Leisure preferences', 'Voting'):
        rows.append(' & '.join([lab] + _cells(D.usShockRow(df, ρ, lab, 'full'))) + r' \\')
    rows.append(' & '.join(['All three'] + _cells(D.usShockRow(df, ρ, 'All French characteristics',
                                                               'full'))) + r' \\[.5em]\hline\\[-.75em]')
    rows.append(' & '.join(['France (own calibration)']
                           + _cells(D.usShockRow(df, ρ, 'France (own calibration)', 'full'))) + r' \\')
    note = (r'\item $\rho = ' + C.num(ρ, 1) + r'$, full effect. Each row is a separate equilibrium path: '
            r'the borrowed characteristics hold throughout and the economy starts from its own steady '
            r'state, so the row describes a country that has always had this mix rather than the US hit '
            r'by a surprise in 2020. Leisure preferences rescales every '
            r'$X_i$ to France\textquotesingle s population-weighted mean $X$, which is a pure change of the hours '
            r'unit, so the tax and savings rates stay exactly at baseline and only hours move. Income '
            r'distribution replaces $\eta_i$ with France\textquotesingle s while holding $X_i$; $\theta$ is then '
            r're-derived from the unchanged replacement-rate ratio and falls, so this row bundles a '
            r'pension-design change with the inequality change (see python/US/shocks.py). The last row '
            r'is France\textquotesingle s own calibrated path, which carries its own $\omega$ as well as '
            r'its own characteristics; its workweek is a calibration target, not a prediction.')
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
            r'imposed on the other two.')
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


def _escCells(r):
    """ The design in force at t0 and the three t0 outcomes of one escExperiments row. """
    return [C.num(r['θ_t0']), C.pct(r['τ_t0']), C.pct(r['sr_t0']), C.num(r['ww_t0'])]


def _escTable(name, scenarioKey, caption, label, extraNote = '', france = False):
    df = D.escExperiments()
    spec, ρs = C.US['esc']['spec'], C.US['esc']['ρTable']
    mid = len(ρs)//2
    readings = [('Baseline', 'baseline', False),
                (r'Exogenous $\theta$', scenarioKey, True),
                (r'Endogenous $\theta$', scenarioKey, False)]
    if france:
        readings.append(('France', 'France', True))
    out = []
    for lab, scen, pinned in readings:
        for k, ρ in enumerate(ρs):
            r = D.escRow(df, ρ, spec, scen, pinned)
            out.append(' & '.join([lab if k == mid else '', C.num(ρ, 1)] + _escCells(r))
                       + r' \\' + ('[.5em]\\hline\\\\[-.75em]' if k == len(ρs)-1 else ''))
    note = (r'\item Deadweight-cost specification: the proportional cost $f(\theta)$ with $\phi = '
            + C.num(C.US['esc']['phi'], 1) + r'$ and $p$ calibrated per $\rho$ '
            r'(\cref{table:US_ESC:calibration}). Every counterfactual is a separate equilibrium path: '
            r'the changed parameters hold throughout, the economy starts from its own steady state, and '
            r'the political choice binds from the first period of the horizon, so the design in force in '
            r'2020 is itself an outcome rather than an inherited datum. All rows are read at 2020. '
            r'$\theta$ (2020) is the design in force there; in the exogenous rows it is the value the '
            r'replacement-rate data imply under the changed characteristics. Each $\rho$ is separately '
            r'calibrated and its workweek normalised against its own baseline.' + extraNote)
    if france:
        note += (r' The France row is not a counterfactual on the US model: France carries its own '
                 r'characteristics \emph{and} its own calibrated $\omega$, so the distance between it '
                 r'and the endogenous row is what the observable characteristics do not explain. Its '
                 r"workweek is France's own calibration target, not a prediction.")
    return _xwrap(name, 'results/esc/escExperiments.csv', caption, label, 'p{2.6cm}YYYYY',
                  ESCHEAD, '\n'.join(out), note)


def escAgeing():
    r""" Table \ref{table:US_ESC:ageing}. """
    return _escTable('US_ESC_Ageing', 'acute',
                     'Endogenous design and ' + LQ + 'acute ageing' + RQ + ' in US',
                     'table:US_ESC:ageing',
                     r' The ' + LQ + 'acute ageing' + RQ + r' scenario sets $\nu_t = 1$ throughout, so '
                     r'the counterfactual economy is one whose demography has always been stationary '
                     r'rather than the US surprised by ageing in 2020.')


def escIncomeDistr():
    r""" Table \ref{table:US_ESC:incomeDistr}. """
    return _escTable('US_ESC_IncomeDistr', 'frIncome',
                     'Endogenous design and the French income distribution in US',
                     'table:US_ESC:incomeDistr',
                     r' In the exogenous rows $\theta$ is re-derived from the unchanged replacement-rate '
                     r'ratio under the French $\eta_i$ (0.50 against the US 0.74), so that row bundles a '
                     r'design change with the change in inequality; the endogenous rows let the '
                     r'electorate choose instead.', france = True)


def escLeisure():
    r""" Table \ref{table:US_ESC:leisure}. """
    return _escTable('US_ESC_Leisure', 'frLeisure',
                     'Endogenous design and French leisure preferences in US',
                     'table:US_ESC:leisure', france = True)


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


def escCalibrationTable():
    r""" Table \ref{table:US_ESC:calibration}: the calibrated cost parameter p per (rho, spec), with the
    design theta* the electorate re-elects. Under the proportional cost f cancels from the
    replacement-rate ratio, so theta* is the data's 0.738 at every rho; under the benefit-side variant
    theta and p are jointly identified and theta* moves with rho. """
    cal = D.escCalibration()
    ρs = C.US['esc']['ρTable']
    spec, alt = C.US['esc']['spec'], C.US['esc']['altSpec']
    rows = []
    for ρ in ρs:
        cells = [C.num(ρ, 1)]
        for s in (spec, alt):
            if (ρ, s) not in cal:
                raise D.MissingInput('escCalibration ({}, {})'.format(ρ, s))
            r = cal[(ρ, s)]
            cells += [C.num(float(r['p']), 3), C.num(float(r['θStar']), 3)]
        rows.append(' & '.join(cells) + r' \\')
    header = (' & \\multicolumn{2}{c}{\\textbf{Proportional cost}} & '
              '\\multicolumn{2}{c}{\\textbf{Redistributive-only cost}} \\\\\n'
              '\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n'
              + ' & '.join([r'\textbf{CRRA} ($\rho$)', '$p$', r'$\theta^{\ast}$',
                            '$p$', r'$\theta^{\ast}$']))
    note = (r'\item $f(\theta) = \phi + (1-\phi)\theta^{p}$ with $\phi = ' + C.num(C.US['esc']['phi'], 1)
            + r'$ imposed; $p$ is calibrated so the design \emph{in force} in 2020 --- on a path where the '
            r'political choice binds from the first period --- is the observed one, '
            r'with $(\beta, \omega)$ recalibrated at each trial value. Under the proportional cost the '
            r"wedge cancels from the replacement-rate ratio, so $\theta^{\ast}$ is the data's own at "
            r'every $\rho$; under the redistributive-only cost $\theta^{\ast}$ and $p$ are jointly '
            r'identified. Without the cost the choice corners at $\theta = 0$ at every $\rho$.')
    return _xwrap('US_ESC_Calibration', 'results/esc/escCalibration{,CRRA}.csv',
                  'The calibrated cost of redistributive funds',
                  'table:US_ESC:calibration', 'YYYYY', header, '\n'.join(rows), note)

