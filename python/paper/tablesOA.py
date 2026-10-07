r""" Table builders for the online appendix (writing/OnlineAppendix; archive/notes/brief_onlineAppendix_2026-10-06.md,
section 2.3). Each returns the complete tex body of one file in results/paper/Tables/, which is not copied
into writing/Paper. Layout as tablesUS: tables.BANNER and tablesUS._xwrap, label `table:OA:<Name>` (plus
config.variantSuffix on a twin), a note in the house form.

Every body row ends with ` % row: <key>`, the last thing on its line; block titles, sub-headers and rules
carry none (brief section 2.2). `_body` refuses a duplicate key.

Units are the paper tables': savings over GDP throughout (the ESC csvs carry s/(w h) and go through
datasets.escSavingsOverY), tax and savings rates in percent to two decimals, their changes in p.p.
(config.pp), the design theta to three decimals. The cell formatters a figure reuses for its marks' text
(ARGRHOCOLS, OECDRHOCOLS, the ESC path cells) live here, so a mark and its table row print the same string.
"""
import os, re
import numpy as np

import config as C
import datasets as D
import oecdFigure1 as F1
from tables import LQ, RQ
from tablesUS import _xwrap, COUNTRYNAME


# ---------------------------------------------------------------------------------------------------
# Shared pieces
# ---------------------------------------------------------------------------------------------------
def _row(cells, key, tail = ''):
    r""" One body row: the cells, the row end and any spacing `tail`, then the key comment last. """
    return ' & '.join(cells) + r' \\' + tail + ' % row: ' + key


def _title(text, ncol):
    r""" A block title spanning the table: no key. """
    return r'\multicolumn{' + str(ncol) + r'}{l}{\textit{' + text + r'}} \\'


def _body(lines):
    """ The joined body, refusing a duplicate row key; a block gap on the last row is dropped. """
    keys = [l.split(' % row: ')[1] for l in lines if ' % row: ' in l]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        raise ValueError('duplicate row keys: {}'.format(dup))
    lines = list(lines)
    lines[-1] = lines[-1].replace(r' \\[.5em] % row: ', r' \\ % row: ')
    return '\n'.join(lines)


def _signed(x, digits = 2):
    """ A change as a signed math-mode number, unsigned when it rounds to zero (as config.pp). """
    v = round(float(x), digits)
    return C.num(0., digits) if v == 0 else '${:+.{d}f}$'.format(v, d = digits)


def _dash(x, fmt):
    """ `fmt(x)`, or '--' for a value the csv does not hold (NaN). """
    return '--' if x is None or x != x else fmt(x)


def _rhoKey(ρ):
    return C.num(float(ρ), 1)


def _tex(s):
    r""" Plain text from a csv into a tex cell: the special characters escaped, straight double quotes as
    tex quotes, apostrophes as \textquotesingle (the house form). """
    s = str(s)
    out = []
    for ch in s:
        out.append({'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
                    '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
                    '|': r'$|$', '<': r'$<$', '>': r'$>$', "'": r'\textquotesingle{}'}.get(ch, ch))
    s = ''.join(out)
    return re.sub(r'"([^"]*)"', LQ + r'\1' + RQ, s)


def _keyOf(s):
    """ An ASCII row key from a name: lowercase, runs of anything outside [a-z0-9] as one '_'. """
    return re.sub(r'[^a-z0-9]+', '_', str(s).lower()).strip('_')


def _fileKey(name):
    """ A file name's row key, its extension dropped: 'US_shocks.csv' -> 'us_shocks'. """
    return _keyOf(os.path.splitext(name)[0])


def _label(name):
    return 'table:OA:' + name


# ---------------------------------------------------------------------------------------------------
# Figure 1's data (data.qmd)
# ---------------------------------------------------------------------------------------------------
ROLES = ('spending', 'growth', 'index', 'gini')                 # oecdFigure1's variable roles, in order
ROLEFMT = {'spending': lambda v: C.num(v, 1), 'growth': lambda v: C.num(v, 3),
           'index': lambda v: C.num(v, 3), 'gini': lambda v: C.num(v, 3)}


def oecdCountries():
    r""" Figure 1's cross-section, one row per country: the four variables oecdFigure1.PLOT draws, each
    followed by the year it is read at where that varies by country (data/oecdFigure1.csv). Rows keyed on
    lowercase ISO3; the economies sections 6-7 calibrate (oecdFigure1.HIGHLIGHT) set in bold. """
    df = D.oecdFigure1Data()
    cols = []                                         # (header, csv column, formatter)
    for role in ROLES:
        c = F1.PLOT[role]
        cols.append((r'\textbf{' + _tex(_varLabel(role, c)) + '}', c, ROLEFMT[role]))
        if c + '_year' in df.columns:
            cols.append((r'\textbf{Year}', c + '_year', lambda v: str(int(round(float(v))))))
    lines = []
    for iso, r in df.iterrows():
        name = _tex(r['country'])
        if iso in F1.HIGHLIGHT:
            name = r'\textbf{' + name + '}'
        lines.append(_row([name] + [_dash(r[c], f) for _, c, f in cols], _keyOf(iso)))
    note = (r'\textit{Note:} The ' + str(len(df)) + r' OECD members plotted in figure '
            r'\ref{fig:US:OECDdata}. Each variable is read in ' + str(F1.YEAR)
            + r' or the nearest year within ' + str(F1.WINDOW) + r' years of it (the year columns); population '
            r'growth is the population of ' + str(F1.YEAR) + r' over that of ' + str(F1.BASE) + r'. Sources in '
            r'table \ref{' + _label('OECD_Sources') + r'}. In bold the economies the paper calibrates.')
    return _xwrap('OECD_Countries', 'data/oecdFigure1.csv', r'The cross-section of figure \ref{fig:US:OECDdata}, by country',
                  _label('OECD_Countries'), 'l' + 'Y'*len(cols), ['\\textbf{Country}'] + [h for h, _, _ in cols],
                  _body(lines), note, width = r'\textwidth')


# The tables' name of a variable where it is not oecdFigure1.LABEL's: the index is the ratio of replacement
# rates, not the calibrated theta of the models.
VARLABEL = {'index': 'Bismarckian--Beveridgean index'}
EPS = re.compile(r'\bEPS\b|eps_')


def _varLabel(role, column):
    return VARLABEL.get(role, F1.LABEL[column])


def _withoutEPS(note):
    """ A sources note without its sentences on the figure's previous version (the EPS and its eps_* readings),
    which data/README.md documents. """
    return ' '.join(s for s in re.split(r'(?<=\.)\s+(?=[A-Z])', str(note)) if not EPS.search(s))


def _plottedColumns():
    """ The csv columns figure 1 draws. """
    return set(F1.PLOT.values())


def oecdSources():
    r""" The sources of figure 1's data, one row per entry of data/oecdFigure1_sources.csv: the columns it
    sources, provider and dataset with vintage and retrieval date, the series, the years and the note. The
    entries whose columns figure 1 draws come first. URLs are in the csv, not printed. Rows keyed on the
    entry's first column. """
    src = D.oecdFigure1Sources()
    src = src[[not all(c.strip().startswith('eps_') for c in s.split(',')) for s in src['column']]]
    plotted = _plottedColumns()
    first = lambda s: s.split(',')[0].strip()
    drawn = [any(c.strip() in plotted for c in s.split(',')) for s in src['column']]
    blocks = [('Plotted in the figure of the paper', src[drawn]),
              ('Further concepts in data/oecdFigure1.csv', src[[not d for d in drawn]])]
    lines = []
    for title, sub in blocks:
        if sub.empty:
            continue
        lines.append(_title(_tex(title), 4))
        for _, r in sub.iterrows():
            source = '; '.join(_tex(x) for x in (r['provider'] + ': ' + r['dataset'], r['vintage'],
                                                  ('retrieved ' + r['retrieved']) if r['retrieved'] else '') if x)
            series = _tex(r['series']) + ('. Years: ' + _tex(r['years']) if r['years'] else '')
            lines.append(_row([_tex(r['column']), source, series, _tex(_withoutEPS(r['note'])) or '--'],
                              _keyOf(first(r['column']))))
    note = (r'\textit{Note:} The columns are those of data/oecdFigure1.csv; data/oecdFigure1\_sources.csv '
            r'carries the URL of every source.')
    rag = r'>{\raggedright\arraybackslash}'
    text = _xwrap('OECD_Sources', 'data/oecdFigure1_sources.csv', r'The sources of figure \ref{fig:US:OECDdata}',
                  _label('OECD_Sources'), rag + 'p{3.8cm}' + (rag + 'X')*3,
                  [r'\textbf{Columns}', r'\textbf{Source}', r'\textbf{Series and years}', r'\textbf{Note}'],
                  _body(lines), note, width = r'\textwidth')
    return text.replace('\\centering\n', '\\centering\n\\footnotesize\n', 1)


def oecdCorrelations():
    r""" The pairwise correlations of figure 1's variables in the concepts it plots (results/paper/
    oecdCorrelations.csv, written by the OECDdata build, variant 'named' = oecdFigure1.NAMED): n, Pearson's r
    and Spearman's rank correlation with their p-values. The csv's other concept sets, those of the figure's
    previous version, are not printed (data/README.md). Rows keyed `named_<x role>_<y role>`. """
    if F1.PLOT != F1.NAMED:
        raise ValueError('OECD_Correlations prints the named concepts, and figure 1 no longer plots them')
    df = D.oecdCorrelations()
    sub = df[df['variant'] == 'named']
    if sub.empty:
        raise D.MissingInput('results/paper/oecdCorrelations.csv (variant named)')
    role = {v: k for k, v in F1.NAMED.items()}
    label = lambda c: _tex(_varLabel(role[c], c))
    p = lambda v: r'$<0.001$' if float(v) < 0.0005 else C.num(float(v), 3)
    lines = [_row([label(r['x']) + ' and ' + label(r['y']), str(int(r['n'])),
                   '$' + C.num(float(r['pearson']), 2) + '$', p(r['pearson_p']),
                   '$' + C.num(float(r['spearman']), 2) + '$', p(r['spearman_p'])],
                  'named_' + role[r['x']] + '_' + role[r['y']]) for _, r in sub.iterrows()]
    note = (r'\textit{Note:} The concepts plotted in figure \ref{fig:US:OECDdata}. Pairwise complete '
            r'observations; the $p$-values are those of the two-sided tests of zero correlation. Variables as in '
            r'table \ref{' + _label('OECD_Countries') + r'} and their sources in table \ref{'
            + _label('OECD_Sources') + '}.')
    return _xwrap('OECD_Correlations', 'results/paper/oecdCorrelations.csv', r'Correlations in the cross-section of figure \ref{fig:US:OECDdata}',
                  _label('OECD_Correlations'), r'>{\raggedright\arraybackslash}p{6.4cm}YYYYY',
                  [r'\textbf{Variables}', '$n$', r'\textbf{Pearson} $r$', '$p$', r'\textbf{Spearman}', '$p$'],
                  _body(lines), note, width = r'\textwidth')


# ---------------------------------------------------------------------------------------------------
# Argentina (argentina.qmd)
# ---------------------------------------------------------------------------------------------------
def argPeriods(commonX = None):
    """ The reform path's dated periods at the baseline rho, terminal period excluded (s_T = 0): a list of
    (offset from t0, year). Years past the workbook's dated part continue its period length. """
    cal = C.calendar()
    years = [cal['dates'][k] for k in sorted(cal['dates'])]
    step = years[1] - years[0]
    n = len(D.shockPath(C.ARG['ρBaseline'], 'reform', commonX = commonX)) - 1
    return [(k, cal['year0'] + step*k) for k in range(n)]


def argentinaReformPath(commonX = None):
    r""" The reform of table \ref{table:Argentina:Universal} (full effect) at the baseline rho along its path:
    the tax rate, savings over GDP and the average workweek per period, pre-reform (the path without the
    reform) against reform. Levels throughout, as ArgentinaUniversal. The terminal period is not printed (its
    savings are zero by construction). Rows keyed `y<year>@<rho>`. """
    commonX = C.ARG['commonX'] if commonX is None else commonX
    sfx = C.variantSuffix(commonX, 'ARG')
    ρ = C.ARG['ρBaseline']
    path = D.shockPath(ρ, 'reform', commonX = commonX)
    srB = D.savingsRatePath(ρ, 'base', commonX = commonX)
    srR = D.savingsRatePath(ρ, 'reform', commonX = commonX)
    hRef = D.baselineHours(ρ, commonX = commonX)
    lines = []
    for k, year in argPeriods(commonX):
        r = path.iloc[k]
        lines.append(_row([str(year), C.pct(r['τ_base']), C.pct(r['τ_reform']),
                           C.pct(srB.iloc[k]), C.pct(srR.iloc[k]),
                           C.num(C.workweekHours(r['h_base'], hRef)), C.num(C.workweekHours(r['h_reform'], hRef))],
                          'y{}@{}'.format(year, _rhoKey(ρ))))
    sub = r'\textbf{Pre-reform} & \textbf{Reform}'
    header = (r' & \multicolumn{2}{c}{\textbf{Tax rate}} & \multicolumn{2}{c}{\textbf{Savings rate}} & '
              r'\multicolumn{2}{c}{\textbf{Avg. workweek (hours)}} \\' + '\n'
              r'\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}' + '\n'
              r'\textbf{Year} & ' + ' & '.join([sub]*3))
    note = (r'\textit{Note:} The reform of table \ref{table:Argentina:Universal' + sfx + r'}, with taxes '
            r'determined by the politico-economic equilibrium, at $\rho = ' + C.num(ρ, 0) + r'$. The '
            r'pre-reform columns are the equilibrium path without the reform. The savings rate is savings '
            r'relative to GDP. The workweek is normalised so that the pre-reform path reads the observed average '
            r'workweek in ' + str(C.calendar()['year0']) + r'. The terminal period of the finite horizon, where '
            r'savings are zero, is not shown.' + C.variantNote(commonX, arm = 'ARG'))
    return _xwrap('ArgentinaReformPath' + sfx,
                  'results/shocks/universal_match_rho%.4f%s.csv' % (ρ, C.argVariantTag(commonX)),
                  'Pension system reform along the path, Argentina' + C.variantCaption(commonX, 'ARG'),
                  _label('ArgentinaReformPath' + sfx), 'lYYYYYY', header, _body(lines), note)


# (csv column, header, formatter) of the Argentine calibration across rho. ARG_RhoGrid's marks print with
# the same formatters, so a hovered value reads as its table cell.
ARGRHOCOLS = [('β',  r'$\beta$',    lambda v: C.num(v, 3)),
              ('ω',  r'$\omega$',   lambda v: C.num(v, 3)),
              ('η0', r'$\eta_0$',   lambda v: C.num(v, 3)),
              ('X0', r'$X_0$',      lambda v: C.num(v, 3)),
              ('X',  r'$X$',        lambda v: C.num(v, 2)),
              ('sr', r'\textbf{Savings rate}', lambda v: C.pct(v)),
              ('ι',  r'$\iota$',    lambda v: C.num(v, 3))]


def argRhoGrid(commonX = None):
    """ The Argentine calibration sweep of one variant over config.ARG['ρGrid'], raising if a rho is missing. """
    g = D.rhoGrid(commonX)
    return _onGrid(g, C.ARG['ρGrid'], C.argSweepCsv(C.ARG['commonX'] if commonX is None else commonX))


def _onGrid(g, grid, path):
    """ The rows of sweep `g` at the rhos of `grid`, raising MissingInput naming `path` if one is absent. """
    miss = [ρ for ρ in grid if not np.isclose(g['ρ'], ρ).any()]
    if miss:
        raise D.MissingInput('{} (ρ = {})'.format(path, miss))
    return g[g['ρ'].apply(lambda r: any(np.isclose(r, v) for v in grid))].reset_index(drop = True)


def argRhoGridTable(commonX = None):
    r""" The Argentine calibration at every rho of the grid (results/calibration/informalSavings_rhoGrid*):
    beta, omega, eta_0, X_0, the common X (the vector-X sweep records none: '--'), and the two untargeted
    moments of the calibration year, the savings rate over GDP and the informal savings ratio iota. Rows
    keyed `rho@<rho>`. The targets (K/Y and tau) are common to every row and go into the note, read from the
    csv and checked to be common. """
    commonX = C.ARG['commonX'] if commonX is None else commonX
    sfx = C.variantSuffix(commonX, 'ARG')
    g = argRhoGrid(commonX)
    for col in ('KY', 'τ'):
        if np.ptp(g[col].astype(float)) > 1e-6:
            raise ValueError('{} differs across rho in the Argentine sweep (spread {:.2e}); it is a target'
                             .format(col, np.ptp(g[col].astype(float))))
    lines = [_row([C.num(r['ρ'], 1)] + [_dash(r[c], f) for c, _, f in ARGRHOCOLS], 'rho@' + _rhoKey(r['ρ']))
             for _, r in g.iterrows()]
    year = C.calendar()['year0']
    note = (r'\textit{Note:} Each $\rho$ is calibrated to the same targets, a capital--output ratio of $'
            + C.num(float(g['KY'].iloc[0]), 2) + r'$ and a tax rate of ' + C.pct(float(g['τ'].iloc[0])) + r' in '
            + str(year) + r'; the calibration at $\rho = ' + C.num(C.ARG['ρBaseline'], 0) + r'$ is table '
            r'\ref{table:Arg:Calib' + sfx + r'}. The savings rate (savings relative to GDP) and the informal '
            r'savings ratio $\iota = s^0/s$ are those of ' + str(year) + r', predictions rather than targets.'
            + ('' if commonX else r' The vector-$X_i$ calibration has no common $X$.')
            + C.variantNote(commonX, arm = 'ARG'))
    return _xwrap('ARG_RhoGridTable' + sfx, os.path.relpath(C.argSweepCsv(commonX), C.REPO).replace(os.sep, '/'),
                  r'The calibration across $\rho$, Argentina' + C.variantCaption(commonX, 'ARG'),
                  _label('ARG_RhoGridTable' + sfx), 'Y'*(1 + len(ARGRHOCOLS)),
                  [r'\textbf{CRRA} ($\rho$)'] + [h for _, h, _ in ARGRHOCOLS], _body(lines), note,
                  width = r'\textwidth')


# ---------------------------------------------------------------------------------------------------
# The rich economies with the design given (oecd.qmd)
# ---------------------------------------------------------------------------------------------------
OECDHOSTS = (('US', 'usa'), ('UK', 'gbr'), ('FR', 'fra'))      # (sweep key, row-key block), the paper's order
OECDRHOCOLS = [('β',  r'$\beta$',  lambda v: C.num(v, 3)),
               ('ω',  r'$\omega$', lambda v: C.num(v, 3)),
               ('X',  r'$X$',      lambda v: C.num(v, 2)),
               ('R',  r'$R$',      lambda v: C.num(v, 3)),
               ('sr', r'\textbf{Savings rate}', lambda v: C.pct(v))]


def oecdSweeps(commonX = None):
    """ {country: its calibration sweep over config.US['ρGrid']} for the U.S., the UK and France, raising if a
    rho is missing from any. """
    cx = C.US['commonX'] if commonX is None else commonX
    return {c: _onGrid(D.usSweep(c, cx), C.US['ρGrid'], C.usSweepCsv(c, cx)) for c, _ in OECDHOSTS}


def oecdRhoGridTable(commonX = None):
    r""" The U.S., UK and French calibrations at every rho of the grid (results/calibration/{US,UK,FR}_rhoGrid*),
    one block per country: beta, omega, the common X (the vector-X sweeps record none: '--'), the 30-year
    gross interest factor R and the savings rate over GDP in the calibration year. Rows keyed
    `<iso3>@<rho>`. """
    commonX = C.US['commonX'] if commonX is None else commonX
    sfx = C.variantSuffix(commonX)
    sw = oecdSweeps(commonX)
    lines = []
    for c, key in OECDHOSTS:
        lines.append(_title(COUNTRYNAME[c], 1 + len(OECDRHOCOLS)))
        for _, r in sw[c].iterrows():
            lines.append(_row([C.num(r['ρ'], 1)] + [_dash(r[k], f) for k, _, f in OECDRHOCOLS],
                              key + '@' + _rhoKey(r['ρ'])))
        lines[-1] = lines[-1].replace(r' \\ % row:', r' \\[.5em] % row:')
    year = C.usCalendar()['year0']
    note = (r'\textit{Note:} $\beta$ is calibrated for the U.S., to its interest factor $R$, and imposed on the '
            r'UK and France at the same $\rho$; their $R$ is a prediction. $\omega$ is calibrated to each '
            r'country\textquotesingle s tax rate in ' + str(year) + r'. '
            + (r'$X$ is pinned by the U.S.\ average workweek and by average hours relative to the U.S. ' if commonX
               else r'The vector-$X_i$ calibration has no common $X$. ')
            + r'The savings rate is savings relative to GDP in ' + str(year) + r', a prediction. The calibration '
            r'at $\rho = ' + C.num(C.US['ρBaseline'], 0) + r'$ is table \ref{table:US:Calib' + sfx + '}.'
            + C.variantNote(commonX))
    return _xwrap('OECD_RhoGridTable' + sfx, 'results/calibration/{US,UK,FR}_rhoGrid%s.csv' % ('CommonX' if commonX else ''),
                  r'The calibration across $\rho$: the U.S., the UK and France' + C.variantCaption(commonX),
                  _label('OECD_RhoGridTable' + sfx), 'Y'*(1 + len(OECDRHOCOLS)),
                  [r'\textbf{CRRA} ($\rho$)'] + [h for _, h, _ in OECDRHOCOLS], _body(lines), note)


# ---------------------------------------------------------------------------------------------------
# The endogenous design (esc.qmd)
# ---------------------------------------------------------------------------------------------------
def escXiValues():
    """ (the workbook xi, [the other xi with a converged calibration]) of escXiRobustness.csv. The workbook
    xi is the US calibration's, read from the summary. """
    ξ0 = float(D.usCalibrationSummary()['US']['ξ'])
    xi = D.escXi()
    cal = xi[(xi['kind'] == 'calibration') & xi['converged'].astype(str).isin(['True', 'true', '1', '1.0'])]
    others = sorted(float(x) for x in cal['xi'].unique() if not np.isclose(float(x), ξ0))
    return ξ0, others


def escXiPath(ξ):
    """ The baseline path at Frisch elasticity `xi` (rho = 1), the columns of datasets.escPath. """
    xi = D.escXi()
    df = xi[np.isclose(xi['xi'].astype(float), ξ) & (xi['kind'] == 'path')]
    if df.empty:
        raise D.MissingInput('results/esc/escXiRobustness.csv (path, ξ = {})'.format(ξ))
    return df.sort_values('pos').reset_index(drop = True)


def escPathSpecs():
    r""" The specifications ESC_Path and ESC_PathTable print, in order: [(block title, path frame, key
    suffix, series label, rho, xi)], the rhos of config.US['esc']['ρTable'] at the workbook xi, then the
    other xi at the baseline rho. Refuses a workbook-xi path in escXiRobustness.csv that does not reproduce
    escPath.csv (a stale row, crossCuttingFindings #13). """
    ξ0, others = escXiValues()
    ρ1 = C.US['ρBaseline']
    base = D.escPath(ρ1)
    try:
        own = escXiPath(ξ0)
    except D.MissingInput:
        own = None
    if own is not None:
        for c in ('θ', 'τ', 'τExo'):
            if len(own) != len(base) or np.max(np.abs(own[c].values - base[c].values)) > 1e-8:
                raise ValueError('escXiRobustness.csv at the workbook ξ = {} does not reproduce escPath.csv ({}); '
                                 're-run python/US/runESCxi.py'.format(ξ0, c))
    out = []
    for ρ in C.US['esc']['ρTable']:
        out.append((r'$\rho = ' + C.num(ρ, 1) + '$', D.escPath(ρ), '@' + _rhoKey(ρ),
                    r'$\rho = ' + C.num(ρ, 1) + '$', ρ, ξ0))
    for ξ in others:
        out.append((r'$\rho = ' + C.num(ρ1, 1) + r'$, $\xi = ' + C.num(ξ, 1) + '$', escXiPath(ξ),
                    'xi' + C.num(ξ, 1) + '@' + _rhoKey(ρ1), r'$\xi = ' + C.num(ξ, 1) + '$', ρ1, ξ))
    return out


def escPathKey(year, suffix):
    """ ESC_PathTable's row key for `year` in the specification whose key suffix is `suffix` ('@1.0',
    'xi0.2@1.0'): 'y2050@1.0', 'y2050xi0.2@1.0'. """
    return 'y{}{}'.format(int(year), suffix)


def escPathCells(r):
    """ ESC_PathTable's cells for one path row: the design chosen, the tax chosen and pinned, their
    difference. ESC_Path's marks print the first and the last. """
    return [C.num(r['θ'], 3), C.pct(r['τ']), C.pct(r['τExo']), C.pp(r['τ'] - r['τExo'])]


def escPathTable():
    r""" The design and the tax along the baseline path, chosen against pinned: per specification (each rho of
    config.US['esc']['ρTable'] at the workbook xi, the other xi at rho = 1) and date, the design in force with
    the choice binding from the first period, the tax on that path, the tax with the design held at theta*
    throughout, and their difference. results/esc/escPath.csv (rho = 1), escPathCRRA.csv (the published
    method), escXiRobustness.csv. Rows keyed `y<year>@<rho>` and `y<year>xi<xi>@<rho>`. """
    specs = escPathSpecs()
    θstar = float(D.escCalibration()[(C.US['ρBaseline'], C.US['esc']['spec'])]['θStar'])
    lines = []
    for title, df, suffix, _, _, _ in specs:
        lines.append(_title(title, 5))
        for _, r in df.iterrows():
            lines.append(_row([str(int(r['date']))] + escPathCells(r), escPathKey(r['date'], suffix)))
        lines[-1] = lines[-1].replace(r' \\ % row:', r' \\[.5em] % row:')
    ξ0 = specs[0][5]
    note = (r'\textit{Note:} Chosen: the design is chosen one period in advance from the first period on, '
            r'at the cost parameter calibrated for each specification (table \ref{table:US_ESC:calibration} and '
            r'table \ref{' + _label('ESC_Xi') + r'}); its first value is the initial condition. Pinned: the same '
            r'model with the design held at $\theta^{\ast} = ' + C.num(θstar, 3) + r'$ throughout. The '
            r'$\rho$ blocks are at $\xi = ' + C.num(ξ0, 1) + r'$, and $\rho \neq 1$ is solved by the exact '
            r'two-dimensional recursion. The last period shown precedes the terminal period of the finite '
            r'horizon.')
    return _xwrap('ESC_PathTable', 'results/esc/escPath.csv, escPathCRRA.csv, escXiRobustness.csv',
                  'The design and the tax along the baseline path, chosen and pinned', _label('ESC_PathTable'),
                  'YYYYY', [r'\textbf{Year}', r'$\theta_t$ \textbf{chosen}', r'\textbf{Tax rate, chosen}',
                            r'\textbf{Tax rate, pinned}', r'\textbf{Difference}'], _body(lines), note)


def escXi():
    r""" The endogenous design at other Frisch elasticities (log preferences, results/esc/escXiRobustness.csv):
    per xi the calibrated cost parameter lambda, the design in force in the three periods after 2020 on the
    baseline path, and acute ageing at 2020 with the design pinned at theta* and chosen (the design chosen,
    and the tax rate under each reading). Rows keyed `xi<xi>`. The workbook xi's acute-ageing rows are
    checked against escExperiments.csv (US_ESC_Ageing at rho = 1) and a mismatch raises. """
    ξ0, others = escXiValues()
    xi = D.escXi()
    t0 = C.usCalendar()['year0']
    acute = D.escExperiments()
    lines, years = [], None
    for ξ in sorted([ξ0] + others):
        sub = xi[np.isclose(xi['xi'].astype(float), ξ)]
        cal = sub[sub['kind'] == 'calibration']
        if cal.empty:
            raise D.MissingInput('results/esc/escXiRobustness.csv (calibration, ξ = {})'.format(ξ))
        path = escXiPath(ξ)
        after = path[path['date'] > t0].sort_values('date').head(3)
        if years is None:
            years = [int(y) for y in after['date']]
        elif [int(y) for y in after['date']] != years:
            raise ValueError('escXiRobustness.csv: the path dates differ across ξ')
        get = lambda kind: sub[sub['kind'] == kind]
        pin, cho = get('acute pinned'), get('acute chosen')
        if pin.empty or cho.empty:
            raise D.MissingInput('results/esc/escXiRobustness.csv (acute ageing, ξ = {})'.format(ξ))
        pin, cho = pin.iloc[0], cho.iloc[0]
        if np.isclose(ξ, ξ0):
            for reading, row in ((True, pin), (False, cho)):
                pub = D.escRow(acute, C.US['ρBaseline'], C.US['esc']['spec'], 'acute', reading)
                if abs(pub['θ_t0'] - row['θ']) > 1e-8 or abs(pub['τ_t0'] - row['τ']) > 1e-8:
                    raise ValueError('escXiRobustness.csv at the workbook ξ does not reproduce escExperiments.csv '
                                     '(acute, pinned={}); re-run python/US/runESCxi.py'.format(reading))
        lines.append(_row([C.num(ξ, 1), C.num(float(cal.iloc[0]['p']), 3)]
                          + [C.num(v, 3) for v in after['θ']]
                          + [C.num(cho['θ'], 3), C.pct(pin['τ']), C.pct(cho['τ'])], 'xi' + C.num(ξ, 1)))
    header = (r' & & \multicolumn{3}{c}{\textbf{Design on the baseline path}} & '
              r'\multicolumn{3}{c}{\textbf{Acute ageing, ' + str(t0) + r'}} \\' + '\n'
              r'\cmidrule(lr){3-5}\cmidrule(lr){6-8}' + '\n'
              r'$\xi$ & $\lambda$ & ' + ' & '.join(r'$\theta_{' + str(y) + '}$' for y in years)
              + r' & $\theta$ \textbf{chosen} & \textbf{Tax, pinned} & \textbf{Tax, chosen}')
    θstar = float(D.escCalibration()[(C.US['ρBaseline'], C.US['esc']['spec'])]['θStar'])
    note = (r'\textit{Note:} Log preferences ($\rho = 1$). At each Frisch elasticity $\xi$ the model is '
            r'recalibrated, $(\beta, \omega, X)$ to their targets and $\lambda$ so that the design in force in '
            + str(t0) + r' is $\theta^{\ast} = ' + C.num(θstar, 3) + r'$. The design columns follow the '
            r'baseline path of table \ref{' + _label('ESC_PathTable') + r'}. Acute ageing sets $\nu_t = 1$ '
            r'throughout, a new equilibrium path read at ' + str(t0) + r', with the design pinned at '
            r'$\theta^{\ast}$ or chosen; at $\xi = ' + C.num(ξ0, 1) + r'$ it is the row of table '
            r'\ref{table:US_ESC:ageing} at $\rho = 1$.')
    return _xwrap('ESC_Xi', 'results/esc/escXiRobustness.csv', r'The endogenous design across the Frisch elasticity $\xi$',
                  _label('ESC_Xi'), 'Y'*8, header, _body(lines), note, width = r'\textwidth')


def escTiming():
    r""" The three timings of the design choice without the cost (writing/US/model_esc.tex, Three timings;
    writing/US/num_esc.tex, The permanent choice):

      * chosen with the tax (sequential), rho of escSequentialCRRA.csv: the largest value over theta in [0, 1]
        and over the dated periods of the costless first order condition eq:esc:seqFOC on the baseline path.
        Negative at every node and date means the corner theta = 0, which is then printed as the choice.
      * one period in advance (leaded), log preferences: the design in force at t0 (escPermanent.csv,
        spec 'none', θLeaded).
      * once and for all (permanent): the design chosen and the tax at it, under log preferences
        (escPermanent.csv, spec 'none') and under CRRA at the rho of escPermanentCRRA.csv (wedge 'none').

    The csvs' other columns are not printed: W0gap/W1gap and nTurning are not defined in the technical
    documentation, and the previous cost forms' rows of escPermanent.csv concern a timing the paper does not
    use with a cost. Rows keyed `sequential@<rho>`, `leaded@<rho>`, `permanent@<rho>`. """
    seq = D.escSequentialCRRA()
    perm = D.escPermanent()
    permC = D.escPermanentCRRA()
    none = perm[perm['spec'] == 'none']
    if none.empty:
        raise D.MissingInput('results/esc/escPermanent.csv (the costless row, spec none)')
    none = none.iloc[-1]
    permC = permC[permC['wedge'] == 'none'].sort_values('ρ')
    ρLOG = C.US['ρAnchor']
    year0 = C.usCalendar()['year0']
    isTrue = lambda s: s.astype(str).isin(['True', 'true', '1', '1.0'])
    sci = lambda v: '$' + '{:.3g}'.format(float(v)) + '$'
    gap = r'[.5em]'
    lines = []
    for k, (ρ, sub) in enumerate(seq.groupby('ρ')):
        neg = bool(isTrue(sub['negative']).all())
        lines.append(_row(['With the tax' if k == 0 else '', C.num(ρ, 1), C.num(0., 3) if neg else '--', '--',
                           sci(sub['focMax'].max())], 'sequential@' + _rhoKey(ρ)))
    lines[-1] = lines[-1].replace(r' \\ % row:', r' \\' + gap + ' % row:')
    lines.append(_row(['One period in advance', C.num(ρLOG, 1), C.num(float(none['θLeaded']), 3), '--', '--'],
                      'leaded@' + _rhoKey(ρLOG), gap))
    rows = [(ρLOG, none)] + [(float(r['ρ']), r) for _, r in permC.iterrows()]
    for k, (ρ, r) in enumerate(rows):
        lines.append(_row(['Once and for all' if k == 0 else '', C.num(ρ, 1), C.num(float(r['θPerm']), 3),
                           C.pct(float(r['τAtChoice'])), '--'], 'permanent@' + _rhoKey(ρ)))
    same = all(abs(float(r['θPerm']) - float(r['θPermIncumbent'])) < 1e-9 for _, r in rows)
    dates = sorted(int(d) for d in seq['date'].unique())
    note = (r'\textit{Note:} No cost of redistribution; $\rho = ' + C.num(ρLOG, 0) + r'$ is log preferences. '
            r'With the tax: the largest value of the marginal effect of the design on the political objective, '
            r'equation \eqref{eq:esc:seqFOC}, over a grid of $\theta_t$ on $[0,1]$ and the dates ' + str(dates[0]) + '--'
            + str(dates[-1]) + r' of the baseline path'
            + (r'; it is negative everywhere, so the choice is the corner $\theta_t = 0$ at every date. '
               if bool(isTrue(seq['negative']).all()) else '. ')
            + r'Its scale is that of the objective, which differs across $\rho$; the log case is checked in the '
              r'regression suite of the code. '
            + r'One period in advance: the design in force in ' + str(year0) + r' on the path where the choice '
            r'binds from the first period. Once and for all: the design chosen in ' + str(year0) + r', with the '
            r'savings of the period before made in anticipation of the vote, and the tax rate at that design.'
            + (r' Pinning the savings ratio at the incumbent design instead, an unanticipated vote, gives the same '
               r'design in every row.' if same else ''))
    return _xwrap('ESC_Timing', 'results/esc/escPermanent.csv, escPermanentCRRA.csv, escSequentialCRRA.csv',
                  'The timing of the design choice without a cost', _label('ESC_Timing'), 'lYYYY',
                  [r'\textbf{Timing}', r'\textbf{CRRA} ($\rho$)', r'$\theta$ \textbf{chosen}',
                   r'\textbf{Tax rate}', r'\textbf{Largest} $\partial \mathcal{W}_t/\partial\theta_t$'],
                  _body(lines), note)


# ---------------------------------------------------------------------------------------------------
# Numerical checks (numerical.qmd)
# ---------------------------------------------------------------------------------------------------
def _stationaryBlocks():
    """ [(arm title, [(row label, key block, frame, gap column, formatter)])] of NUM_Stationary, each frame
    cut to the dated periods before the terminal one. """
    def cut(df):
        last = df.groupby('ρ')['t'].transform('max')
        return df[df['t'] < last]
    us, esc, arg = (cut(D.stationaryApprox(w)) for w in ('US', 'US_ESC', 'ARG'))
    pp = lambda v: _signed(v, 2)
    th = lambda v: _signed(v, 3)
    return [('United States', [('Tax rate, design given (p.p.)', 'us', us, 'gap_pp', pp),
                               ('Tax rate, design chosen (p.p.)', 'esctax', esc, 'gapτ_pp', pp),
                               (r'Design chosen ($\theta$)', 'escdesign', esc, 'gapθ', th)]),
            ('Argentina', [('Tax rate (p.p.)', 'arg', arg, 'gap_pp', pp)])]


def numStationary():
    r""" Stationary against date-specific policy functions (results/numerical/*_stationaryApprox*.csv): the
    path walked by a time-invariant policy function solved at each date's own nu_t, minus the paper's
    date-specific solution, by date and rho. The tax in p.p. (the U.S. with the design given, under CRRA; the
    U.S. with the design chosen, log and CRRA; Argentina, log and CRRA) and the chosen design in units of
    theta. The terminal period is not printed. Rows keyed `<block>@<rho>`. The csvs' other columns (the gap
    at the exact path's states, the steady-state and long-run comparisons) are not printed: the technical
    documentation does not define them. """
    blocks = _stationaryBlocks()
    ncol = 2 + max(len(sorted(df['date'].unique())) for _, rows in blocks for _, _, df, _, _ in rows)
    lines = []
    for arm, rows in blocks:
        dates = sorted(int(d) for d in rows[0][2]['date'].unique())
        for _, _, df, _, _ in rows:
            if sorted(int(d) for d in df['date'].unique()) != dates:
                raise ValueError('NUM_Stationary: the {} blocks have different dates'.format(arm))
        lines.append(r'\multicolumn{2}{l}{\textit{' + arm + r'}} & ' + ' & '.join(str(d) for d in dates)
                     + ' &'*(ncol - 2 - len(dates)) + r' \\')
        lines.append(r'\cmidrule(lr){3-' + str(2 + len(dates)) + '}')
        for label, block, df, col, fmt in rows:
            for k, (ρ, sub) in enumerate(df.groupby('ρ')):
                sub = sub.set_index('date')
                cells = [label if k == 0 else '', C.num(ρ, 1)] + [fmt(sub.loc[d, col]) for d in dates]
                cells += [''] * (ncol - len(cells))
                lines.append(_row(cells, block + '@' + _rhoKey(ρ)))
            lines[-1] = lines[-1].replace(r' \\ % row:', r' \\[.5em] % row:')
    note = (r'\textit{Note:} Each cell is the policy on the path walked by time-invariant policy functions, '
            r'each solved at its own date' + "'" + r's $\nu_t$ and applied from the same initial state, minus '
            r'the date-specific policy of the paper' + "'" + r's solution: the tax rate in percentage points, '
            r'the chosen design in units of $\theta$. Under log preferences ($\rho = 1$) with the design given '
            r'the two coincide and the U.S.\ block has no row. The design chosen is at the paper' + "'" + r's cost '
            r'specification. The terminal period of the finite horizon is not shown; the last period shown '
            r'carries the date-specific solution\textquotesingle s approach to it (appendix \ref{app:T}) rather '
            r'than the demographic transition.')
    return _xwrap('NUM_Stationary', 'results/numerical/{US,US_ESC}_stationaryApprox.csv, ARG_stationaryApprox'
                  + C.argVariantTag(C.ARG['commonX']) + '.csv',
                  'Stationary against date-specific policy functions', _label('NUM_Stationary'),
                  r'>{\raggedright\arraybackslash}p{2.6cm}' + 'Y'*(ncol - 1),
                  r'\textbf{Policy} & $\rho$ & \multicolumn{' + str(ncol - 2)
                  + r'}{c}{\textbf{Stationary minus date-specific}}', _body(lines), note, width = r'\textwidth')


def numSelection():
    r""" The equilibrium counts per results csv behind the outputs (datasets.selectionCsvs): rows, rows that
    record counts, and over those the largest number of equilibria, the largest number of candidates and the
    total of fallbacks; first for the tax rule of writing/US/num_robustroot.tex (nEqMax, nCandMax,
    nFallback), then for the design layer of the exact CRRA recursion of writing/US/num_esc.tex (nEqθMax,
    nBrθMax, nFallbackθ), whose candidates are brackets. A csv that records no count of a layer prints '--'
    in its statistics; the design block lists only the csvs that record that layer. Rows keyed
    `<layer>_<file>`. """
    entries = D.selectionCsvs()
    stats = {(lab, layer): D.countSummary(ps, layer) for _, lab, ps in entries for layer in ('tax', 'design')}
    num = lambda v: '--' if v is None else str(v)
    fname = lambda lab, n: _tex(lab) + ('' if n == 1 else r' (' + str(n) + ' files)')
    lines = []
    for arm, title in (('ARG', 'Tax rule: Argentina'), ('US', 'Tax rule: the U.S., the UK and France')):
        lines.append(_title(title, 6))
        for a, lab, ps in entries:
            if a != arm:
                continue
            s = stats[(lab, 'tax')]
            lines.append(_row([fname(lab, s['files']), str(s['rows']), str(s['counted']), num(s['eqMax']),
                               num(s['candMax']), num(s['fallbacks'])], 'tax_' + _fileKey(lab)))
    lines[-1] = lines[-1].replace(r' \\ % row:', r' \\[.5em] % row:')
    lines.append(_title('Design layer of the exact CRRA recursion: brackets as candidates', 6))
    for a, lab, ps in entries:
        s = stats[(lab, 'design')]
        if s['counted'] == 0:
            continue
        lines.append(_row([fname(lab, s['files']), str(s['rows']), str(s['counted']), num(s['eqMax']),
                           num(s['candMax']), num(s['fallbacks'])], 'design_' + _fileKey(lab)))
    note = (r'\textit{Note:} Per csv, the rows, the rows that record the counts, and over those the largest '
            r'number of equilibria at any state and period, the largest number of candidates and the total number '
            r'of states at which the solver fell back. The tax rule is the selection of the technical '
            r'documentation, which falls back on the tax that maximizes its integral criterion where no '
            r'candidate passes the equilibrium test; a solve that does not select a tax (the '
            r'economic-equilibrium paths, with taxes held at the baseline path) or did not record its counts '
            r'leaves them out. The design layer is that of the exact recursion under CRRA preferences, which '
            r'compares the candidate designs with the retirees\textquotesingle{} savings shares held fixed and '
            r'then makes the shares consistent: its candidates are the brackets of that consistency residual, and '
            r'where none closes to an equilibrium it falls back on comparing each design at its own consistent '
            r'shares. escExperiments.csv and escExperimentsUK.csv, which the endogenous-design exhibits read, '
            r'merge the escShocks* files, whose counts are the rows above.')
    return _xwrap('NUM_Selection', 'results/{calibration,shocks,sweeps,esc,numerical}/*.csv',
                  'Equilibrium counts in the results the exhibits read', _label('NUM_Selection'),
                  r'>{\raggedright\arraybackslash}p{5.4cm}YYYYY',
                  [r'\textbf{File}', r'\textbf{Rows}', r'\textbf{Counted}', r'\textbf{Equilibria, max}',
                   r'\textbf{Candidates, max}', r'\textbf{Fallbacks}'], _body(lines), note, width = r'\textwidth')
