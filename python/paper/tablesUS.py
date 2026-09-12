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
import numpy as np

import config as C
import datasets as D
from tables import BANNER, LQ, RQ, SRNOTE


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


def _cells(r, base = None):
    """ The three reported quantities of one shock row, formatted. With `base` (that rho's baseline
    row) the savings rate is the change against it in p.p.; without, it is the level. """
    sr = C.pct(r[D.US_SR]) if base is None else C.pp(r[D.US_SR] - base[D.US_SR])
    return [C.pct(r['τ']), sr, C.num(r['workweek'])]


def _shockRows(df, ρ, scenarios, baselineLabel):
    """ The 'Full effect' / 'Economic equilibrium effect' block shared by US_PensChars and US_Ageing. """
    b = D.usBaseline(df, ρ)
    line = lambda lab, r, base = None: ' & '.join([lab] + _cells(r, base)) + r' \\'
    out = [line(baselineLabel, b) + '[1.25ex]']
    for effect, head in (('full', 'Full effect:'), ('ee', 'Economic equilibrium effect:')):
        out.append(r'\multicolumn{4}{l}{\textit{' + head + r'}} \\\hline')
        for lab, scen in scenarios:
            out.append(line(lab, D.usShockRow(df, ρ, scen, effect), b))
        out[-1] += '[1.25ex]'
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


def usOtherShocks(commonX = None):
    r""" Table \ref{table:US:otherShocks}: French income distribution and voting imposed on the US model,
    at the baseline rho.

    Full effect only, following the paper, which reports that the two effects are not informative apart
    for these -- they work in the same direction and are quantitatively minor. The economic-equilibrium
    rows ARE in results/shocks/US_shocks.csv if that judgement is revisited.

    The leisure-preference row (a pure rescaling of X_i, moving hours alone) is no longer printed
    anywhere in the paper -- dropped 2026-09-11 as uninformative. The experiment still runs and its rows
    stay in the csv; only the readers changed. It is still INSIDE the all-characteristics row, which
    needs France's level of X to land on France's own (eta, X).

    Two rows beyond the single characteristics: all French characteristics at once, and France's own
    calibrated path. Together they say how far the observable characteristics take the US towards France
    and how much is left for the political weight -- the comparison the new-path convention exists to
    make (python/US/runShocksUS.franceReference).

    This is the table the calibration variant moves most: income distribution is defined through eta,
    which is exactly what the variant re-interprets. """
    commonX = C.US['commonX'] if commonX is None else commonX
    ρ = C.US['ρBaseline']
    df = D.usShocks(commonX = commonX)
    b = D.usBaseline(df, ρ)
    rows = [' & '.join(['Baseline'] + _cells(b)) + r' \\']
    for lab in ('Income distribution', 'Voting'):
        rows.append(' & '.join([lab] + _cells(D.usShockRow(df, ρ, lab, 'full'), b)) + r' \\')
    rows.append(' & '.join(['All French characteristics']
                           + _cells(D.usShockRow(df, ρ, 'All French characteristics', 'full'), b))
                + r' \\[.5em]\hline\\[-.75em]')
    rows.append(' & '.join(['France (own calibration)']
                           + _cells(D.usShockRow(df, ρ, 'France (own calibration)', 'full'), b)) + r' \\')
    note = (r'\item \textit{Note:} $\rho = ' + C.num(ρ, 1) + r'$, full effect. Each row is a separate equilibrium path: '
            r'the borrowed characteristics hold throughout and the economy starts from its own steady '
            r'state, so the row describes a country that has always had this mix rather than the US hit '
            r'by a surprise in 2020. Income '
            r'distribution replaces $\eta_i$ with France\textquotesingle s while holding $X_i$ \emph{and} '
            r'holding $\theta$ at the US design, so it is a change in inequality alone; pension design is '
            r'the separate counterfactual of Table~\ref{table:US:pensChars}. All French characteristics '
            r'imposes France\textquotesingle s $\eta_i$, voting weights $\mu_i$ and level of $X_i$ at once; '
            r'the last, a pure rescaling of the hours unit, moves hours and nothing else. The last row '
            r'is France\textquotesingle s own calibrated path, its savings rate reported as the distance '
            r'from the US baseline.' + C.variantNote(commonX))
    return _xwrap('US_OtherShocks' + C.variantSuffix(commonX), df.attrs['source'],
                  'French income distribution and voting patterns in US'
                  + C.variantCaption(commonX),
                  'table:US:otherShocks' + C.variantSuffix(commonX), 'lYYY', SHOCKHEAD,
                  '\n'.join(rows), note)


# ---------------------------------------------------------------------------------------------------
def _crraTable(name, caption, label, scenarios, commonX = None):
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
    df = D.usShocks(commonX = commonX)
    ρs = C.US['ρTable']
    mid = len(ρs)//2
    groups = [('Baseline', None)] + list(scenarios)
    out = []
    for lab, scen in groups:
        for k, ρ in enumerate(ρs):
            b = D.usBaseline(df, ρ)
            cells = _cells(b) if scen is None else _cells(D.usShockRow(df, ρ, scen, 'full'), b)
            out.append(' & '.join([lab if k == mid else '', C.num(ρ, 1)] + cells)
                       + r' \\' + (r'[.5em]\hline\\[-.75em]' if k == len(ρs)-1 else ''))
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


# ---------------------------------------------------------------------------------------------------
COUNTRYNAME = {'US': 'US', 'UK': 'UK', 'FR': 'France'}


def usukfrCalibration(commonX = None):
    r""" Table \ref{table:US:Calib}: the headline calibration for the three countries.

    `X` is the POPULATION-WEIGHTED MEAN of X_i -- the only summary of a vector whose level IS the hours
    unit, and the one the leisure counterfactual is matched on. beta is added as a row the hand-written
    table omitted: it is imposed on France and the UK from the US calibration at the same rho, so
    printing it makes that visible rather than implicit. """
    commonX = C.US['commonX'] if commonX is None else commonX
    c = D.usCalibrationSummary(commonX)
    cols = [k for k in ('US', 'UK', 'FR') if k in c]     # the hand-written column order
    year0 = C.usCalendar()['year0']

    def row(label, fn, target):
        return ' & '.join([label] + [fn(c[k]) for k in cols] + [target]) + r' \\'

    rows = [
        row(r'$\theta$', lambda r: C.num(r['θ']), 'Replacement rate dispersion'),
        row(r'$\omega$', lambda r: C.num(r['ω']),
            ', '.join(r'$\tau^{' + k + '} = ' + C.pct(c[k]['τ0'], 1) + '$' for k in cols)),
        row(r'$\beta$',  lambda r: C.num(r['β']), 'US: 30y interest rate; imposed on UK/FR'),
        # Two decimals: with the hours unit normalised to μ = 1 (model.addEigenVectors), the vector-X
        # X_i and their mean sit on an O(1) scale where one decimal is two significant figures.
        row('$X$',       lambda r: C.num(r['Xbar'], 2), 'Avg.\\ workweek'),
        row(r'$\nu_{%d}$' % year0, lambda r: C.num(r['ν2020']),
            '30-year gross population growth rates'),
        row(r'$\eta_{H}/\eta_L$', lambda r: C.num(r['ηHηL']),
            'Relative productivity of high (H) to low (L) income groups'),
    ]
    header = ([r'\multicolumn{1}{c|}{\textbf{Parameter}}']
              + [r'\textbf{' + COUNTRYNAME[k] + '}' for k in cols] + [r'\textbf{Target}'])
    # The one note that spells the variant out; every other US table points here (config.variantNote).
    note = (r'\item \textit{Note:} $\rho = ' + C.num(C.US['ρBaseline'], 1) + r'$. $X$ is the '
            r'population-weighted mean of $X_i$; its level is the hours unit, pinned for France and the '
            r'UK by targeting average hours relative to the US rather than in levels. $\beta$ is '
            r'calibrated for the US and imposed on the other two.' + C.variantNote(commonX, full = True))
    return (BANNER.format(name = 'USUKFRCalibration' + C.variantSuffix(commonX),
                          src = 'results/paper/usCalibrationSummary.csv')
            + '\\begin{table}[!htb]\n\\centering\n\\begin{threeparttable}\n'
            + '\\caption{Calibration, US, UK, and France' + C.variantCaption(commonX) + '}\n'
            + '\\label{table:US:Calib' + C.variantSuffix(commonX) + '}\n'
            + '\\renewcommand{\\arraystretch}{1.25}\n'
            + '\\begin{tabularx}{\\textwidth}{Y|' + 'Y'*len(cols) + '|p{6cm}}\n\\hline\n'
            + '& \\multicolumn{%d}{c|}{\\textbf{Country}} & \\\\ \\cline{2-%d}\n' % (len(cols), len(cols)+1)
            + ' & '.join(header) + ' \\\\ \\hline\n'
            + '\n'.join(rows) + '\n\\hline\n\\end{tabularx}\n'
            + '\\begin{tablenotes}\n\\footnotesize\n' + note + '\n\\end{tablenotes}\n'
            + '\\end{threeparttable}\n\\end{table}\n')


def _householdHeterogeneity(country, name, label, commonX = None):
    r""" One country's per-group table: gamma_i, X_i, eta_i, mu_i.

    Under the common-X calibration the X_i row is one number repeated, and the hours row is a prediction
    rather than the target it is under vector X -- so the `Target` column is variant-dependent. """
    commonX = C.US['commonX'] if commonX is None else commonX
    c = D.usCalibrationSummary(commonX)[country]
    spec = [(r'$\gamma_i$', 'γi', 2, 'Income percentiles.'),
            ('$X_i$',       'Xi', 2, 'Average hours worked.' if commonX else 'Hours worked.'),
            (r'$\eta_i$',   'ηi', 2, 'Income distribution.'),
            (r'$\mu_i$',    'μi', 2, 'Voting propensity.')]
    rows = [' & '.join([lab] + [C.num(v, d) for v in c[key]] + [target]) + r' \\'
            for lab, key, d, target in spec]
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
    reported as the change against it in p.p. """
    sr = D.escSavingsOverY(r['sr_t0'])
    srCell = C.pct(sr) if base is None else C.pp(sr - D.escSavingsOverY(base['sr_t0']))
    return [C.num(r['θ_t0']), C.pct(r['τ_t0']), srCell, C.num(r['ww_t0'])]


def _escTable(name, scenarioKey, caption, label, extraNote = '', france = False):
    """ Rows grouped by reading, one row per rho within each. The savings change in every non-baseline
    row is against the printed baseline of the same rho -- the endogenous-theta reading, which is also
    what figuresUS.escOverview differences against. """
    df = D.escExperiments()
    spec, ρs = C.US['esc']['spec'], C.US['esc']['ρTable']
    # The ESC leg runs under the headline calibration variant only -- there is no twin to select here,
    # and escRow filters on it so a stale vector-X row cannot be read in its place.
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
            base = None if scen == 'baseline' else D.escRow(df, ρ, spec, 'baseline', False)
            out.append(' & '.join([lab if k == mid else '', C.num(ρ, 1)] + _escCells(r, base))
                       + r' \\' + ('[.5em]\\hline\\\\[-.75em]' if k == len(ρs)-1 else ''))
    note = (r'\item \textit{Note:} Deadweight-cost specification: the proportional cost $f(\theta)$ with $\phi = '
            + C.num(C.US['esc']['phi'], 1) + r'$ and $p$ calibrated per $\rho$ '
            r'(Table~\ref{table:US_ESC:calibration}). Every counterfactual is a separate equilibrium path: '
            r'the changed parameters hold throughout, the economy starts from its own steady state, and '
            r'the political choice binds from the first period of the horizon, so the design in force in '
            r'2020 is itself an outcome rather than an inherited datum. All rows are read at 2020. '
            r'$\theta$ (2020) is the design in force there; in the exogenous rows it is the US design, '
            r'held fixed so that the counterfactual is about the changed characteristic alone. Each '
            r'$\rho$ is separately calibrated and its workweek normalised against its own baseline. '
            r'The savings rate is savings relative to GDP; the baseline rows report its level and every '
            r'other row the change against the baseline at the same $\rho$, in percentage points.'
            + extraNote + C.variantNote(C.US['commonX']))
    if france:
        note += (r' The France row is not a counterfactual on the US model: France carries its own '
                 r'characteristics \emph{and} its own calibrated $\omega$, so the distance between it '
                 r'and the endogenous row is what the observable characteristics do not explain. Its '
                 r"workweek is France's own calibration target, not a prediction, and its savings rate "
                 r'is likewise the distance from the US baseline.')
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
                     r' The exogenous rows hold $\theta$ at the US design, so they are the change in '
                     r'inequality alone; the endogenous rows let the electorate choose the design under '
                     r'the French income distribution, and the gap between the two is what endogenising '
                     r'the design adds.', france = True)


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
    r""" Table \ref{table:US_ESC:calibration}: the calibrated cost parameter p per rho, with the design
    theta* the electorate re-elects.

    The proportional cost is the only formulation reported. Under it f cancels from the replacement-rate
    ratio, so theta* is the data's own 0.738 at every rho and the table's second column is a check that
    it did: a theta* that moved with rho would mean the wedge had leaked into the design identification.
    """
    cal = D.escCalibration()
    ρs, spec, φ = C.US['esc']['ρTable'], C.US['esc']['spec'], C.US['esc']['phi']
    rows = []
    for ρ in ρs:
        if (ρ, spec) not in cal:
            raise D.MissingInput('escCalibration ({}, {})'.format(ρ, spec))
        r = cal[(ρ, spec)]
        p, θ = float(r['p']), float(r['θStar'])
        # f(theta*) = phi + (1-phi) theta*^p: the share of redistributive funds that reaches households
        # at the chosen design, so 1 - f is the deadweight cost the text quotes.
        rows.append(' & '.join([C.num(ρ, 1), C.num(p, 3), C.num(θ, 3), C.num(φ + (1-φ)*θ**p, 3)])
                    + r' \\')
    header = ' & '.join([r'\textbf{CRRA} ($\rho$)', '$p$', r'$\theta^{\ast}$', r'$f(\theta^{\ast})$'])
    note = (r'\item \textit{Note:} $f(\theta) = \phi + (1-\phi)\theta^{p}$ with $\phi = ' + C.num(φ, 1)
            + r'$ imposed; $p$ is calibrated so the $\theta$ choice is the observed one, with '
            r'$(\beta, \omega)$ recalibrated at each trial value. The cost is proportional, so the wedge '
            r'cancels from the replacement-rate ratio. Without the cost the choice would be in the corner '
            r'$\theta = 0$ for every $\rho$.' + C.variantNote(C.US['commonX']))
    return _xwrap('US_ESC_Calibration', 'results/esc/escCalibration{,CRRA}.csv',
                  'The calibrated cost of redistributive funds',
                  'table:US_ESC:calibration', 'YYYY', header, '\n'.join(rows), note)


def ukEscCalibrationTable():
    r""" Table \ref{table:UK_ESC:calibration}: escCalibrationTable's layout for the UK -- the wedge p
    calibrated so that the UK electorate re-elects the UK's own observed design theta*.

    rho = 1 only: the country stage (python/US/runESC.stageCountry) runs under LOG and has no CRRA
    counterpart yet, so the table prints whatever rho the csv carries rather than config's rhoTable, and
    the note says so. The US-wedge reading -- the UK's choice with the US's p imposed -- is in the same
    csv and goes into the note as the comparison the number is for: the UK needs a smaller wedge than
    the US to re-elect a less Bismarckian system, and with the US wedge its electorate corners at
    theta = 1. France has no own-wedge row (its observed design IS the corner, so there is no root) and
    is not printed. """
    df = D.escCountry()
    spec, φ = C.US['esc']['spec'], C.US['esc']['phi']
    own = df[(df['country'] == 'UK') & (df['wedgeFrom'] == 'own')]
    us = df[(df['country'] == 'UK') & (df['wedgeFrom'] == 'US')]
    if own.empty:
        raise D.MissingInput('escCountry (UK, own wedge, {}, phi={})'.format(spec, φ))
    rows = []
    for r in own.to_dict('records'):
        p, θ = float(r['p']), float(r['θStar'])
        rows.append(' & '.join([C.num(float(r['ρ']), 1), C.num(p, 3), C.num(θ, 3),
                                C.num(φ + (1-φ)*θ**p, 3)]) + r' \\')
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

