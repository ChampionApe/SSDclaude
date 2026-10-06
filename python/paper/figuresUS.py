r""" Figure builders for the US/France/UK arm. figures.py is the Argentina arm and owns the house style;
this module imports it rather than restating it, so the two arms stay one visual family.

Style rules that apply here specifically:
  * The counterfactuals are a CATEGORICAL set, not a continuous parameter, so they get the categorical
    pair -- never THETA_RAMP, which is reserved for a parameter that varies continuously.
  * The baseline is a reference line, not a series: it is drawn in ink, not in a series colour, so it
    cannot be mistaken for one of the scenarios being compared against it.
  * Every panel plots the DEVIATION from the baseline, never the level. The levels differ by a few
    points on a 14% base and a 39-hour base, which a level axis compresses into indistinguishable bars;
    the deviation is also the only thing the workweek column means, since under vector X the level of
    hbar is not identified and only its ratio to the baseline is a result. The one exception is the
    pension design in the ESC figure, where the corners 0 and 1 are meaningful and the level is read.
  * Savings are reported over GDP, s/Y, in both figures -- the shock csv's `srOverY`, and in the ESC
    figure (1 - alpha) times the csv's s/(wh), since wh = (1 - alpha) Y. alpha is read from the
    calibration summary, never typed.
  * NOT config.pct anywhere in here. It escapes the percent sign for tex and matplotlib renders the
    backslash literally, so a legend built with it reads "14.4\%". Anything drawn INTO a figure needs
    plain formatting; config.pct is for tex cells only.
"""
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

import config as C
import datasets as D
from figures import SERIES, INK, LW, _panel, _save, markId, mark, signed, plain
from tables import rowKey
from tablesUS import ROWKEY


# The rows of the overview, in the order the paper's discussion moves in: pension design, then ageing (the
# two it identifies as the main determinants), then France's characteristics in UKUS_French's order.
# Reading the finished figure top-to-bottom should reproduce that ranking, so the order is fixed here
# rather than sorted by effect size: a figure whose ordering changes with the data cannot be referred to
# in prose. Each row is (row label, [(csv scenario, mark label), ...], shock family, how a second scenario
# is drawn). A row with two scenarios is one bar per rho (_barPanel): 'tone' draws both from the baseline,
# the FIRST in the series colour and the second in its light tone (theta = 0 and theta = 1, on either side
# of the US design); 'line' draws the first as the bar and marks the second by a line across it (mild
# ageing inside acute ageing). The figure carries no key for either: the paper's note explains them. The
# composite rows (all three French characteristics, France's own path) are the tables' business.
OVERVIEW = [('Pension design',       [(r'$\theta = 0$', r'$\theta = 0$'), (r'$\theta = 1$', r'$\theta = 1$')],
             'design', 'tone'),
            ('Ageing',               [('Acute ageing', 'Acute ageing'), ('Mild ageing', 'Mild ageing')], 'ageing',
             'line'),
            ('French income distr.', [('Income distribution', 'French income distr.')], 'french', None),
            ('French voting',        [('Voting', 'French voting')], 'french', None),
            ('French leisure',       [('Leisure preferences', 'French leisure')], 'french', None)]

# The light tone of a 'tone' bar: the series colour at this share over the surface, which keeps the
# lightest of the three (orange) at about 2:1 against the surface, the floor at which it still reads as a
# mark in print. Opaque rather than an alpha, so the shorter tone drawn over the longer keeps its colour.
TINT, SURFACE = 0.6, '#ffffff'
# The width of a 'line' mark, in points. It is drawn in the surface colour where it falls inside its bar,
# and in the series colour where it does not, so it never vanishes against the surface.
MARKLW = 2.0
# A row every one of whose bars rounds to zero at the paper's precision (one decimal, style guide §3) says
# so in words: an empty bar group reads as a missing run. Only the leisure rows of the tax and savings
# panels qualify.
ZEROROW = 0.05

# The three reported quantities, as (csv column, panel title, axis label, how to scale a deviation).
# tau and srOverY are fractions on the csv and are read in percentage points; the workweek is already
# in hours (normalised inside the experiment script against that rho's own baseline) and its deviation
# is in hours. Do NOT re-derive the workweek from hbar here -- see tablesUS.py.
PANELS = [('τ',        'Equilibrium tax rate', 'Percentage points',        100.),
          ('srOverY',  'Savings over GDP',     'Percentage points of GDP', 100.),
          ('workweek', 'Average workweek',     'Hours per week',           1.)]

# Colours for the three rho values: the categorical pair plus one ink shade -- three is one more than
# the validated pair carries, so the extra slot is deliberately NEUTRAL rather than a third hue guessed
# by eye. Fixed order, never cycled.
RHOCOLOURS = [SERIES[0], SERIES[1], INK['secondary']]

# A mark's id part and the unit its text carries, per plotted column (figures.signed). None: a level of
# theta, printed to three decimals.
MARKUNIT = {'τ': ('tau', 'p.p.'), 'srOverY': ('sr', 'p.p. of GDP'), 'workweek': ('ww', 'hours'),
            'θ_t0': ('theta', None), 'τ_t0': ('tau', 'p.p.'), 'sr_t0': ('sr', 'p.p. of GDP'),
            'ww_t0': ('ww', 'hours')}
# The CRRA table printing each shock family of OVERVIEW at every rho of config.US['ρTable'], after the
# host's name (_shockTable).
CRRATABLE = {'design': '_CRRA_PensChars', 'ageing': '_CRRA_Ageing', 'french': '_CRRA_OtherShocks'}


def _rhoPart(ρ):
    return 'rho{:.1f}'.format(ρ)


def _markText(v, unit):
    return '{:.3f}'.format(v) if unit is None else signed(v, unit = unit)


def _shockTable(host, fam, scenario, ρ, sfx):
    r""" (table, row key) of the table printing `scenario` of family `fam` on `host` at `ρ`: the host's CRRA
    table of the family, which prints every scenario of OVERVIEW and FRENCH at every rho. """
    return host + CRRATABLE[fam] + sfx, rowKey(ROWKEY[scenario], ρ)


def _tint(colour):
    """ The light tone of `colour`: TINT of it over the surface, as an opaque rgb. """
    return tuple(TINT*np.array(mcolors.to_rgb(colour)) + (1 - TINT)*np.array(mcolors.to_rgb(SURFACE)))


def _barPanel(ax, title, xlabel, labels, series, colours, gids = None, kinds = None):
    r""" One horizontal grouped-bar panel: `series` is a list of (label, values) over `labels`, drawn as
    one bar per series within each scenario group. `gids[k][j]` tags series k's bar for label j.

    `kinds[j]` (OVERVIEW's last field) makes row j's values pairs, with `gids[k][j]` a pair too. 'tone':
    two scenarios in one bar, both measured from the baseline, the first in the series colour and the
    second in its light tone (_tint); the longer is drawn first, so where the two lie on the same side of
    zero the shorter stays visible over it, parted by a surface gap where it ends, and on opposite sides
    the zero line parts them. 'line': the first is the bar and the second a line across it (MARKLW). A row
    whose bars all round to zero (ZEROROW) is labelled 'unchanged'. """
    y = np.arange(len(labels))
    height = 0.8/len(series)
    kinds = kinds or [None]*len(labels)
    # _panel FIRST: it sets tick_params, which would otherwise recolour the scenario labels to the muted
    # ink meant for numeric ticks. These are the figure's row headings and belong in primary ink.
    _panel(ax, title, '', titlesize = 12, labelsize = 10)
    for k, (lab, vals) in enumerate(series):
        yk = y + (k - (len(series)-1)/2)*height
        for j, (v, kind) in enumerate(zip(vals, kinds)):
            g = gids[k][j] if gids else None
            if kind == 'tone':
                tones = list(zip(v, (colours[k], _tint(colours[k])), g or (None, None)))
            elif kind == 'line':
                tones = [(v[0], colours[k], g[0] if g else None)]
            else:
                tones = [(v, colours[k], g)]
            for x, c, gid in sorted(tones, key = lambda t: -abs(t[0])):
                # One legend entry per series, from its first row's full tone.
                key = lab if j == 0 and c is colours[k] else '_nolegend_'
                patch = ax.barh(yk[j], x, height = height, color = c, edgecolor = 'none', zorder = 3,
                                label = key).patches[0]
                if gid:
                    patch.set_gid(gid)
            if kind == 'tone' and v[0]*v[1] > 0:
                inner = np.sign(v[0])*min(abs(v[0]), abs(v[1]))
                ax.vlines(inner, yk[j] - height/2, yk[j] + height/2, colors = SURFACE, linewidth = 1.2,
                          zorder = 3.5)
            elif kind == 'line':
                inside = v[0]*v[1] > 0 and abs(v[1]) < abs(v[0])
                line, = ax.plot([v[1], v[1]], [yk[j] - height/2, yk[j] + height/2], linewidth = MARKLW,
                                color = SURFACE if inside else colours[k], solid_capstyle = 'butt',
                                zorder = 3.6)
                if g:
                    line.set_gid(g[1])
    for j in range(len(labels)):
        row = [x for _, vals in series for x in (vals[j] if isinstance(vals[j], tuple) else (vals[j],))]
        if all(abs(x) < ZEROROW for x in row):
            ax.annotate('unchanged', xy = (0, y[j]), xytext = (5, 0), textcoords = 'offset points',
                        ha = 'left', va = 'center', fontsize = 10, style = 'italic', color = INK['muted'])
    ax.axvline(0, color = INK['primary'], linewidth = 1.0, zorder = 4)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize = 11, color = INK['primary'])
    ax.set_xlabel(xlabel, color = INK['secondary'], fontsize = 10)
    ax.grid(axis = 'y', visible = False)


def _topDown(axes):
    """ Put the first scenario at the TOP, once for the whole row of panels.

    NOT inside the per-panel helpers: these axes are created with sharey=True, so they are one y-axis
    wearing several faces and every invert_yaxis() call flips it again. Called per panel it reverses
    the scenario order on any EVEN number of panels and leaves it alone on any odd number. Invert once,
    on one axis, and the count stops mattering. """
    axes[0].invert_yaxis()


def _figLegend(fig, handles, labels, bottom = 0.075, ncol = None):
    r""" One legend for the whole figure, below the panels. Figure-level rather than per-panel: the
    series mean the same thing in every panel, so repeating the key would be redundant.

    The baseline the deviations are measured from is NOT drawn here: it is a \tablenotes under the
    \includegraphics in the paper, which keeps its levels out of a second place they would have to be
    kept in step (they are printed in the tables) and leaves the panels the height. """
    # ncol: a five-entry key does not fit one row at this width and is clipped at both ends rather than
    # shrunk, so the caller that has one wraps it.
    fig.tight_layout(rect = (0, bottom, 1, 1))
    fig.legend(handles, labels, loc = 'lower center', ncol = ncol or len(handles), frameon = False,
               fontsize = 11, bbox_to_anchor = (0.5, 0.01))


def _rowsPresent(df, ρs, rows, effect = 'full'):
    r""" The subset of `rows` for which every rho has each of the row's scenarios (entry[1]: one csv
    scenario, or OVERVIEW's list of (scenario, label)): a scenario the run did not produce should drop out
    of the figure rather than take the whole build down with it, and a scenario missing at SOME rho is
    dropped too -- a bar group with a hole in it reads as a zero. """
    out = []
    for entry in rows:
        names = [entry[1]] if isinstance(entry[1], str) else [s for s, _ in entry[1]]
        try:
            for ρ in ρs:
                for s in names:
                    D.usShockRow(df, ρ, s, effect)
        except D.MissingInput:
            continue
        out.append(entry)
    return out


def usOverview(commonX = None):
    r""" Figure \ref{fig:US:overview}: every single-characteristic counterfactual's effect on the tax
    rate, savings over GDP and the average workweek, in deviations from the baseline, at each rho in
    config.US['rhoTable'].

    Read as: which characteristics move each outcome, and does that ranking survive the IES. Ageing and
    pension design should dominate the tax panel and the French characteristics should be visibly minor
    there, while leisure preferences move the workweek alone. Putting the three panels side by side on a
    SHARED scenario axis is what makes the rankings comparable.

    The design and ageing rows are two scenarios each, one bar per rho (OVERVIEW, _barPanel): theta = 0
    and theta = 1 in two tones on either side of the baseline, so the bar's length is the whole effect of
    the design, and acute ageing as the bar with mild ageing a line across it. The legend keys rho only;
    the paper's figure note explains the two rows.
    """
    commonX = C.US['commonX'] if commonX is None else commonX
    sfx = C.variantSuffix(commonX)
    name, marks = 'US_overview' + sfx, []
    df = D.usShocks(commonX = commonX)
    ρs = C.US['ρTable']
    rows = _rowsPresent(df, ρs, OVERVIEW)
    labels = [lab for lab, _, _, _ in rows]
    kinds = [kind for _, _, _, kind in rows]
    colours = RHOCOLOURS[:len(ρs)]

    fig, axes = plt.subplots(1, len(PANELS), figsize = (8.4, 0.46*len(labels) + 2.2), sharey = True)
    for ax, (col, title, xlabel, scale) in zip(axes, PANELS):
        part, unit = MARKUNIT[col]
        series, gids = [], []
        for ρ in ρs:
            base = D.usBaseline(df, ρ)[col]
            vals, ids = [], []
            for _, scen, fam, _ in rows:
                vs = [scale*(D.usShockRow(df, ρ, s, 'full')[col] - base) for s, _ in scen]
                gs = [markId(name, ROWKEY[s], _rhoPart(ρ), part) for s, _ in scen]
                for (s, lab), v, g in zip(scen, vs, gs):
                    tab, rk = _shockTable('US', fam, s, ρ, sfx)
                    marks.append(mark(g, plain(lab), v, _markText(v, unit),
                                      series = 'ρ = ' + C.num(ρ, 1), panel = title, table = tab, row = rk))
                vals.append(tuple(vs) if len(vs) > 1 else vs[0])
                ids.append(tuple(gs) if len(gs) > 1 else gs[0])
            series.append((r'$\rho = ' + C.num(ρ, 1) + '$', vals))
            gids.append(ids)
        _barPanel(ax, title, xlabel, labels, series, colours, gids, kinds)
    _topDown(axes)
    handles, labs = axes[0].get_legend_handles_labels()
    _figLegend(fig, handles, labs)
    return _save(fig, name, marks)


# ---------------------------------------------------------------------------------------------------
# Endogenous system characteristics (app:ESC)
# ---------------------------------------------------------------------------------------------------
# The counterfactual set the appendix runs, in the same order as the main-text figure where the two
# overlap. 'mild' is absent: runESCcrra.py's scenario set does not include it, so it exists at rho = 1
# only and a row of it would be a hole at two thirds of the grid. The composite, 'French characteristics',
# is 'frBoth' (France's income distribution and voting patterns at once), the pair whose two halves move the
# DESIGN in opposite directions. By scale invariance it carries the design, tax and savings of 'frAll', the
# tables' all-French row, which also imposes France's level of X and so differs in hours alone (the leisure
# rescaling; 'frLeisure' is run but not drawn).
ESCSCENARIOS = [('Acute ageing',           'acute'),
                ('French voting',          'frVoting'),
                ('French income distr.',   'frIncome'),
                ('French characteristics', 'frBoth')]
# The table printing each ESC scenario, per host; 'frBoth' through the all-French rows.
ESCTABLE = {'US': {'acute': 'US_ESC_Ageing', 'frIncome': 'US_ESC_IncomeDistr', 'frVoting': 'US_ESC_Voting',
                   'frBoth': 'US_ESC_FrenchAll'},
            'UK': {'frIncome': 'UK_ESC_IncomeDistr', 'frVoting': 'UK_ESC_Voting', 'frBoth': 'UK_ESC_FrenchAll'}}
# (scenario, column) a mark must not link to its ESCTABLE row, and the tooltip that says why.
ESCUNPRINTED = {('frBoth', 'ww_t0'): ' (no table prints this workweek: the all-French rows also impose '
                                     "France's level of X)"}
NOTABLE = ' (no table prints this value)'


def _capitalShare():
    """ The US capital income share alpha, from the calibration summary. Needed to turn the ESC csv's
    s/(wh) into s/Y = (1 - alpha) s/(wh); the shock csv carries srOverY itself, this one does not. """
    rec = D.usCalibrationSummary()['US']
    if 'α' not in rec or rec['α'] != rec['α']:
        raise D.MissingInput('α for the US in results/paper/usCalibrationSummary.csv')
    return float(rec['α'])


def _escRowsPresent(df, spec, ρs, scenarios):
    """ The subset of `scenarios` carrying BOTH readings at every rho -- same contract as _rowsPresent:
    the LOG and CRRA ESC drivers have their own scenario lists, so a scenario can legitimately exist at
    rho = 1 and nowhere else. """
    out = []
    for entry in scenarios:
        try:
            for ρ in ρs:
                for pinned in (True, False):
                    D.escRow(df, ρ, spec, entry[1], pinned)
        except D.MissingInput:
            continue
        out.append(entry)
    return out


def _escPairs(name, df, spec, ρs, scen, col, title, scale, level, host = 'US', idHost = ()):
    r""" One dumbbell panel's data: `pairs` for _dumbbellPanel (both readings against the ENDOGENOUS
    baseline at each rho, or the level for `level`), their `gids` and the `marks`, each linked to the
    pinned/chosen row of the host's ESC table (ESCTABLE). `idHost`: extra id parts naming the host. """
    part, unit = MARKUNIT[col]
    pairs, gids, marks = [], [], []
    for ρ in ρs:
        base = 0. if level else float(D.escRow(df, ρ, spec, 'baseline', False)[col])
        vals = [(scale*(float(D.escRow(df, ρ, spec, s, True)[col]) - base),
                 scale*(float(D.escRow(df, ρ, spec, s, False)[col]) - base))
                for _, s in scen]
        pairs.append((r'$\rho = ' + C.num(ρ, 1) + '$', vals))
        gids.append([])
        for (lab, s), pv in zip(scen, vals):
            tab = None if (s, col) in ESCUNPRINTED else ESCTABLE[host].get(s)
            ids = [markId(name, *idHost, s, _rhoPart(ρ), part, reading) for reading in ('pinned', 'chosen')]
            gids[-1].append(ids)
            marks += [mark(g, plain(lab) + ('' if tab else ESCUNPRINTED.get((s, col), NOTABLE)), v,
                           _markText(v, unit),
                           series = 'ρ = {}, θ {}'.format(C.num(ρ, 1), reading), panel = title,
                           table = tab, row = rowKey(reading, ρ) if tab else None)
                      for g, v, reading in zip(ids, pv, ('pinned', 'chosen'))]
    return pairs, gids, marks


def _dumbbellPanel(ax, title, xlabel, labels, pairs, colours, ref = 0., extraRefs = (), gids = None):
    r""" One horizontal dumbbell panel. `pairs` is a list over series (rho values) of
    (label, [(x_pinned, x_chosen) per scenario]); each pair is drawn as an open marker at the pinned
    reading, a filled marker at the chosen one and a connector in the series colour, so the DISTANCE
    between the two readings -- the design response -- is the mark itself rather than a gap the reader
    has to measure between a bar end and a marker. `ref` is the ink reference line (0 for a deviation
    panel, the US design for the level panel); `extraRefs` are muted lines (the corners of theta).
    `gids[k][j]`: the (pinned, chosen) ids of series k's pair for scenario j. """
    y = np.arange(len(labels))
    off = np.linspace(-0.27, 0.27, len(pairs)) if len(pairs) > 1 else [0.]
    _panel(ax, title, '', titlesize = 12, labelsize = 10)
    ax.axvline(ref, color = INK['primary'], linewidth = 1.0, zorder = 2)
    for x in extraRefs:
        ax.axvline(x, color = INK['muted'], linewidth = 0.8, zorder = 2)
    for k, (_, vals) in enumerate(pairs):
        yy = y + off[k]
        x0 = [v[0] for v in vals]
        x1 = [v[1] for v in vals]
        for a, b, yk in zip(x0, x1, yy):
            ax.plot([a, b], [yk, yk], color = colours[k], linewidth = 1.8, zorder = 3,
                    solid_capstyle = 'round')
        # One scatter per point, so each marker carries its own gid: same z-order and draw order as one
        # scatter per reading, so not a pixel moves.
        for j, (a, yk) in enumerate(zip(x0, yy)):
            sc = ax.scatter([a], [yk], s = 34, facecolors = 'white', edgecolors = colours[k],
                            linewidths = 1.4, zorder = 5)
            if gids:
                sc.set_gid(gids[k][j][0])
        for j, (b, yk) in enumerate(zip(x1, yy)):
            sc = ax.scatter([b], [yk], s = 34, facecolors = colours[k], edgecolors = 'white',
                            linewidths = 0.8, zorder = 6)
            if gids:
                sc.set_gid(gids[k][j][1])
    for yk in y[:-1]:
        ax.axhline(yk + 0.5, color = INK['grid'], linewidth = 0.8, zorder = 1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize = 11, color = INK['primary'])
    ax.set_xlabel(xlabel, color = INK['secondary'], fontsize = 10)
    ax.grid(axis = 'y', visible = False)


def escOverview():
    r""" Figure \ref{fig:US_ESC:overview}: what each counterfactual does when the pension design is
    chosen politically, against what it does at a fixed design -- as dumbbells from the pinned reading
    (open marker) to the chosen one (filled marker), one per (scenario, rho).

    Four panels in a 2 x 2 grid. The design itself first, as a LEVEL: every dumbbell there starts at
    the US design, so its length is the design response and the muted lines at 0 and 1 are the corners
    the text refers to. Then the tax rate, savings over GDP and the average workweek as deviations from
    the endogenous-theta baseline, so the pinned end is the main-text reading and the dumbbell is what
    endogenising the design adds. A dumbbell that collapses to a dot IS the finding for that row (ageing
    in the tax panel).

    2 x 2 rather than one row of four: at \linewidth a row of four narrow panels shrinks the type below
    legibility and squeezes the tax panel's 12-point range into an inch. The grid keeps every panel at
    half the width, and the scenario labels are repeated on the left of each row so a panel can be read
    without tracing back across the page. All four share one scenario axis (sharey), so inverting it
    once (_topDown) puts the first scenario at the top everywhere.

    The workweek is in hours, normalised against that rho's own baseline inside the ESC driver (the
    csv's ww_t0), for the reason tablesUS.py gives: under vector X the level of hbar is not identified,
    so stage (iii) never re-derives it.

    Every row is a new equilibrium path whose political choice binds from the first period, so the
    design in force in 2020 is itself an outcome. All panels are read at 2020.
    """
    df = D.escExperiments()
    spec, ρs = C.US['esc']['spec'], C.US['esc']['ρTable']
    α = _capitalShare()
    colours = RHOCOLOURS[:len(ρs)]
    scen = _escRowsPresent(df, spec, ρs, ESCSCENARIOS)
    labels = [lab for lab, _ in scen]
    θstar = float(D.escRow(df, C.US['ρBaseline'], spec, 'baseline', False)['θ_t0'])

    # (column, title, axis label, deviation scale, is a level). sr_t0 is s/(wh); (1 - alpha) turns it
    # into s/Y before the percentage-point scaling.
    panels = [('θ_t0',  'Pension design in 2020', '$\\theta$ in force', 1., True),
              ('τ_t0',  'Equilibrium tax rate', 'Percentage points', 100., False),
              ('sr_t0', 'Savings over GDP', 'Percentage points of GDP', 100.*(1 - α), False),
              ('ww_t0', 'Average workweek', 'Hours per week', 1., False)]

    fig, grid = plt.subplots(2, 2, figsize = (8.0, 2*(0.5*len(labels) + 1.35) + 0.9), sharey = True)
    axes = grid.ravel()
    marks = []
    for ax, (col, title, xlabel, scale, level) in zip(axes, panels):
        # Both readings are measured against the ENDOGENOUS baseline, so the two are on one scale and
        # the dumbbell length is the design response and nothing else. Reading the pinned rows against a
        # pinned baseline instead would fold the baseline's own design response into it.
        pairs, gids, mk = _escPairs('US_ESC_overview', df, spec, ρs, scen, col, title, scale, level)
        marks += mk
        _dumbbellPanel(ax, title, xlabel, labels, pairs, colours,
                       ref = θstar if level else 0., extraRefs = (0., 1.) if level else (), gids = gids)
    axes[0].set_xlim(-0.04, 1.06)
    _topDown(axes)
    # sharey hides the inner columns' tick labels; the second ROW's left panel keeps its own, which is
    # what lets the lower panels be read without tracing back up the page.
    for ax in grid[:, 0]:
        ax.tick_params(axis = 'y', labelleft = True)

    handles = [Line2D([], [], color = c, linewidth = 1.8, label = r'$\rho = ' + C.num(ρ, 1) + '$')
               for c, ρ in zip(colours, ρs)]
    handles += [Line2D([], [], marker = 'o', linestyle = 'none', markerfacecolor = 'white',
                       markeredgecolor = INK['primary'], markersize = 6,
                       label = '$\\theta$ pinned at the U.S. design'),
                Line2D([], [], marker = 'o', linestyle = 'none', markerfacecolor = INK['primary'],
                       markeredgecolor = 'white', markersize = 6,
                       label = '$\\theta$ chosen by the electorate')]
    _figLegend(fig, handles, [h.get_label() for h in handles], bottom = 0.12, ncol = 2)
    return _save(fig, 'US_ESC_overview', marks)


# ---------------------------------------------------------------------------------------------------
# France's characteristics on two hosts, the US and the UK (appendix app:UKUS). One row of panels per
# host on shared axes per column, so the two hosts are compared by position rather than across figures.
# ---------------------------------------------------------------------------------------------------
HOSTS = [('US', 'U.S.'), ('UK', 'UK')]    # (host key, row label)
FRENCH = [('French income distr.', 'Income distribution'),
          ('French voting',        'Voting'),
          ('French leisure',       'Leisure preferences'),
          ('French characteristics', 'All French characteristics')]


def _hostRowLabel(ax, text):
    """ The host's name, set above the row's first panel and left of its title. """
    ax.annotate(text, xy = (0, 1), xycoords = 'axes fraction', xytext = (0, 24), textcoords = 'offset points',
                fontsize = 13, fontweight = 'bold', color = INK['primary'], ha = 'left', va = 'bottom')


def ukusFrench(commonX = None):
    r""" Figure \ref{fig:UKUS:french}: France's characteristics imposed on the US and on the UK at a given
    pension design, in deviations from each host's own baseline, at each rho. Rows are hosts; columns the
    tax rate, savings over GDP and the workweek, sharing each column's axis. Every scenario must be present
    at every rho for both hosts (_rowsPresent), since a hole would read as a zero. """
    commonX = C.US['commonX'] if commonX is None else commonX
    sfx = C.variantSuffix(commonX)
    name, marks = 'UKUS_French' + sfx, []
    ρs = C.US['ρTable']
    dfs = {h: D.usShocks(commonX = commonX, host = h) for h, _ in HOSTS}
    scen = [s for s in FRENCH if all(s in _rowsPresent(dfs[h], ρs, FRENCH) for h, _ in HOSTS)]
    if not scen:
        raise D.MissingInput('the French scenarios in results/shocks/{US,UK}_shocks*.csv')
    labels = [lab for lab, _ in scen]
    colours = RHOCOLOURS[:len(ρs)]
    fig, grid = plt.subplots(len(HOSTS), len(PANELS), figsize = (8.4, 2*(0.46*len(labels) + 1.5) + 0.8),
                             sharey = True, sharex = 'col')
    for i, (row, (h, hostLabel)) in enumerate(zip(grid, HOSTS)):
        df = dfs[h]
        for ax, (col, title, xlabel, scale) in zip(row, PANELS):
            part, unit = MARKUNIT[col]
            series, gids = [], []
            for ρ in ρs:
                base = D.usBaseline(df, ρ)[col]
                vals = [scale*(D.usShockRow(df, ρ, s, 'full')[col] - base) for _, s in scen]
                series.append((r'$\rho = ' + C.num(ρ, 1) + '$', vals))
                gids.append([markId(name, h, ROWKEY[s], _rhoPart(ρ), part) for _, s in scen])
                for (lab, s), v, g in zip(scen, vals, gids[-1]):
                    tab, rk = _shockTable(h, 'french', s, ρ, sfx)
                    marks.append(mark(g, plain(lab), v,
                                      _markText(v, unit), series = 'ρ = ' + C.num(ρ, 1),
                                      panel = hostLabel + ': ' + title, table = tab, row = rk))
            _barPanel(ax, title, xlabel if i == len(HOSTS) - 1 else '', labels, series, colours, gids)
        _hostRowLabel(row[0], hostLabel)
    _topDown(grid.ravel())
    for ax in grid[:, 0]:
        ax.tick_params(axis = 'y', labelleft = True)
    handles, labs = grid[0, 0].get_legend_handles_labels()
    _figLegend(fig, handles, labs, bottom = 0.06)
    return _save(fig, name, marks)


ESCFRENCH = [('French income distr.',    'frIncome'),
             ('French voting',           'frVoting'),
             ('French characteristics', 'frBoth')]


def ukusEscFrench():
    r""" Figure \ref{fig:UKUS:escFrench}: France's characteristics on the US and on the UK when the design
    is chosen, each host at its own cost parameter. Rows are hosts; the design in force in 2020 as a level
    (the reference line is the host's own observed design) and the tax rate as a deviation from the
    host's endogenous-theta baseline, as dumbbells from the pinned reading to the chosen one
    (escOverview's encoding). 'frAll' is left out for the reason ESCSCENARIOS gives. """
    spec, ρs = C.US['esc']['spec'], C.US['esc']['ρTable']
    colours = RHOCOLOURS[:len(ρs)]
    dfs = {h: D.escExperiments(h) for h, _ in HOSTS}
    scen = [s for s in ESCFRENCH if all(s in _escRowsPresent(dfs[h], spec, ρs, ESCFRENCH) for h, _ in HOSTS)]
    if not scen:
        raise D.MissingInput('the French scenarios at every rho in results/esc/escExperiments{,UK}.csv')
    labels = [lab for lab, _ in scen]
    panels = [('θ_t0', 'Pension design in 2020', '$\\theta$ in force', 1., True),
              ('τ_t0', 'Equilibrium tax rate', 'Percentage points', 100., False)]
    fig, grid = plt.subplots(len(HOSTS), len(panels), figsize = (8.0, 2*(0.5*len(labels) + 1.4) + 0.9),
                             sharey = True, sharex = 'col')
    marks = []
    for i, (row, (h, hostLabel)) in enumerate(zip(grid, HOSTS)):
        df = dfs[h]
        θstar = float(D.escRow(df, C.US['ρBaseline'], spec, 'baseline', False)['θ_t0'])
        for ax, (col, title, xlabel, scale, level) in zip(row, panels):
            pairs, gids, mk = _escPairs('UKUS_ESC_French', df, spec, ρs, scen, col, hostLabel + ': ' + title,
                                        scale, level, host = h, idHost = (h,))
            marks += mk
            _dumbbellPanel(ax, title, xlabel if i == len(HOSTS) - 1 else '', labels, pairs, colours,
                           ref = θstar if level else 0., extraRefs = (0., 1.) if level else (), gids = gids)
        row[0].set_xlim(-0.04, 1.06)
        _hostRowLabel(row[0], hostLabel)
    _topDown(grid.ravel())
    for ax in grid[:, 0]:
        ax.tick_params(axis = 'y', labelleft = True)
    handles = [Line2D([], [], color = c, linewidth = 1.8, label = r'$\rho = ' + C.num(ρ, 1) + '$')
               for c, ρ in zip(colours, ρs)]
    handles += [Line2D([], [], marker = 'o', linestyle = 'none', markerfacecolor = 'white',
                       markeredgecolor = INK['primary'], markersize = 6,
                       label = "$\\theta$ pinned at the host's design"),
                Line2D([], [], marker = 'o', linestyle = 'none', markerfacecolor = INK['primary'],
                       markeredgecolor = 'white', markersize = 6,
                       label = '$\\theta$ chosen by the electorate')]
    _figLegend(fig, handles, [h.get_label() for h in handles], bottom = 0.12, ncol = 2)
    return _save(fig, 'UKUS_ESC_French', marks)


# ---------------------------------------------------------------------------------------------------
# The robustness map (appendix app:robustness, the online appendix's front page)
# ---------------------------------------------------------------------------------------------------
# Design given: (id part, panel title). 'theta' is tau(theta = 0) - tau(theta = 1); the others are the
# change against the host's own baseline at the same rho.
MAPGIVEN = [('theta', r'$\theta = 0$ against $\theta = 1$'), ('acute', 'Acute ageing'),
            ('income', 'French income distr.'), ('voting', 'French voting')]
MAPGIVENSCEN = {'acute': 'Acute ageing', 'income': 'Income distribution', 'voting': 'Voting'}
MAPGIVENTABLE = {'US': {'theta': 'US_CRRA_PensChars', 'acute': 'US_CRRA_Ageing',
                        'income': 'US_CRRA_OtherShocks', 'voting': 'US_CRRA_OtherShocks'},
                 'UK': {'theta': 'UK_CRRA_PensChars', 'acute': 'UK_CRRA_Ageing',
                        'income': 'UK_CRRA_OtherShocks', 'voting': 'UK_CRRA_OtherShocks'}}
# Design chosen: (escExperiments scenario, panel title), and the specification rows, (kind, key, label):
# a host at the paper's cost, the U.S. at the comparison cost, the Frisch elasticity at rho = 1.
MAPCHOSEN = [('acute', 'Acute ageing'), ('frIncome', 'French income distr.'), ('frVoting', 'French voting')]
MAPSPECS = [('host', 'US', 'U.S.'), ('scale', 'US', 'U.S., cost on\nthe design'), ('host', 'UK', 'UK'),
            ('xi', 0.2, r'U.S., $\xi = 0.2$'), ('xi', 0.4, r'U.S., $\xi = 0.4$')]
XIROW = 'xi{:.1f}'       # ESC_Xi's row key of one Frisch elasticity (tablesOA)
MAPMS, MAPRING = 4.6, 9.5


def _mapGiven(host, commonX, ρ, part):
    """ (change in the tax rate in p.p., table, row) of one design-given marker. """
    df = D.usShocks(commonX = commonX, host = host)
    tau = lambda s, e = 'full': float(D.usShockRow(df, ρ, s, e)['τ'])
    if part == 'theta':
        v, block = tau(r'$\theta = 0$') - tau(r'$\theta = 1$'), 'theta0'
    else:
        v, block = tau(MAPGIVENSCEN[part]) - tau('Baseline', 'baseline'), ROWKEY[MAPGIVENSCEN[part]]
    return 100*v, MAPGIVENTABLE[host][part] + C.variantSuffix(commonX), rowKey(block, ρ)


def _mapChosen(kind, key, ρ, scen):
    """ (change in the design in force in 2020 against the same specification's baseline, table, row) of
    one design-chosen marker. """
    spec = C.US['esc']['spec']
    if kind == 'xi':
        xi = D.escXi()
        xi = xi[np.isclose(xi['xi'], key)]
        year0 = C.usCalendar()['year0']
        base = xi[(xi['kind'] == 'path') & (xi['date'] == year0)]
        cho = xi[xi['kind'] == 'acute chosen']
        if base.empty or cho.empty:
            raise D.MissingInput('the baseline in {} and acute chosen at xi = {} in results/esc/escXiRobustness.csv'
                                 .format(year0, key))
        return float(cho['θ'].iloc[0]) - float(base['θ'].iloc[0]), 'ESC_Xi', XIROW.format(key)
    host, spec = (key, spec) if kind == 'host' else ('US', C.US['esc']['comparisonSpec'])
    df = D.escExperiments(host)
    v = float(D.escRow(df, ρ, spec, scen, False)['θ_t0']) - float(D.escRow(df, ρ, spec, 'baseline', False)['θ_t0'])
    if kind == 'scale':
        return v, 'US_ESC_ScaleWedge', rowKey('scale', ρ)
    return v, ESCTABLE[host][scen], rowKey('chosen', ρ)


def _mapRun(kind, key, scen):
    """ Does the specification row exist for this scenario by design? The UK's chosen-design runs are
    France's characteristics (config.US['esc']['uk']['scenarios']); the xi check is acute ageing alone. A
    run that should exist and does not is MissingInput, never a blank. """
    if kind == 'host' and key == 'UK':
        return scen in C.US['esc']['uk']['scenarios']
    if kind == 'xi':
        return scen == 'acute'
    return True


def _mapRows(groups, gap = 0.18):
    """ Row-group layout from the top: per group of n slots (one per rho, or one), its slot positions,
    its centre and the boundary below it. A three-slot group is one unit high, a one-slot group 0.45. """
    out, top = [], 0.
    for n in groups:
        h = 1.0 if n > 1 else 0.45
        slots = [top + h/2] if n == 1 else list(top + h/2 + 0.3*(np.arange(n) - (n - 1)/2))
        out.append((slots, top + h/2, top + h + gap/2))
        top += h + gap
    return out, top - gap


def _mapPanel(ax, title, labels, rows, extent, size = 7):
    """ House axes for one map panel: rows top-down, zero as the reference, groups ruled apart. """
    _panel(ax, title, '', titlesize = 8, labelsize = size - 0.5)
    ax.axvline(0, color = INK['primary'], linewidth = 0.8, zorder = 2)
    for _, _, edge in rows[:-1]:
        ax.axhline(edge, color = INK['grid'], linewidth = 0.8, zorder = 1)
    ax.set_yticks([c for _, c, _ in rows])
    ax.set_yticklabels(labels, fontsize = size, color = INK['primary'])
    ax.set_ylim(extent + 0.12, -0.12)
    ax.grid(axis = 'y', visible = False)
    ax.xaxis.set_major_locator(MaxNLocator(4))


def _mapEmpty(ax, y, text):
    ax.text(0.5, y, text, transform = ax.get_yaxis_transform(), ha = 'center', va = 'center',
            fontsize = 6.5, style = 'italic', color = INK['muted'])


def robustnessMap():
    r""" Figure \ref{fig:robustness}: every headline result against the host's own baseline at the same
    rho, one marker per specification, in two blocks of small multiples. Design given: the change in the
    tax rate (p.p.) under theta = 0 against theta = 1, acute ageing and France's income distribution and
    voting patterns, rows the U.S. and the UK as hosts. Design chosen: the change in the design in force in
    2020 under acute ageing and France's income distribution and voting patterns, rows the U.S. at the
    paper's cost, at the comparison cost (config.US['esc']['comparisonSpec']), the UK at its own cost, and
    the U.S. at xi = 0.2, 0.4 (rho = 1). rho by colour (RHOCOLOURS), the calibration variant by marker
    (filled circle the headline, open diamond the twin, so where the two agree the circle sits inside the
    diamond), the paper's own reading (U.S., headline variant, rho = 1, the paper's cost) ringed in ink.
    Every marker is a mark linked to the table row that prints it; a specification that is not run (or a
    host MAPGIVENTABLE has no table for) is said so in its cell. The xi markers read datasets.escXi and link to ESC_Xi rows
    XIROW. Sized at the 5.91in measure. """
    ρs = C.US['ρTable']
    colour = dict(zip(ρs, RHOCOLOURS))
    head = C.US['commonX']
    variants = [(head, 'o', True), (not head, 'D', False)]       # (commonX, marker, filled)
    varName = lambda cx: 'common X' if cx else 'vector Xᵢ'
    paperρ = C.US['ρBaseline']
    name, marks = 'RobustnessMap', []

    givenRows, givenExt = _mapRows([len(ρs)]*len(HOSTS))
    chosenRows, chosenExt = _mapRows([1 if kind == 'xi' else len(ρs) for kind, _, _ in MAPSPECS])
    unit = 0.36                                                   # inches per row unit
    hGiven, hChosen = givenExt*unit + 0.75, chosenExt*unit + 0.75
    fig = plt.figure(figsize = (5.91, hGiven + hChosen + 0.55), layout = 'constrained')
    sfGiven, sfChosen = fig.subfigures(2, 1, height_ratios = [hGiven, hChosen + 0.55])
    for sf, text in ((sfGiven, 'Design given: change in the tax rate, percentage points'),
                     (sfChosen, r'Design chosen: change in the design $\theta$ in force in 2020')):
        sf.suptitle(text, x = 0.01, ha = 'left', fontsize = 9, color = INK['primary'])

    def point(ax, x, y, c, marker, filled, gid, ring):
        if ring:
            ax.plot(x, y, linestyle = 'none', marker = 'o', markersize = MAPRING, markerfacecolor = 'none',
                    markeredgecolor = INK['primary'], markeredgewidth = 0.9, zorder = 6)
        kw = (dict(markerfacecolor = c, markeredgecolor = '#fcfcfb', markeredgewidth = 0.5, markersize = MAPMS)
              if filled else
              dict(markerfacecolor = 'none', markeredgecolor = c, markeredgewidth = 1.0, markersize = MAPMS + 1.6))
        pt, = ax.plot(x, y, linestyle = 'none', marker = marker, zorder = 4 if filled else 3, **kw)
        pt.set_gid(gid)

    axes = sfGiven.subplots(1, len(MAPGIVEN), sharey = True)
    for ax, (part, title) in zip(axes, MAPGIVEN):
        _mapPanel(ax, title, [lab for _, lab in HOSTS], givenRows, givenExt)
        for (h, hostLabel), (slots, centre, _) in zip(HOSTS, givenRows):
            if part not in MAPGIVENTABLE[h]:
                _mapEmpty(ax, centre, 'not reported')
                continue
            for ρ, y in zip(ρs, slots):
                for cx, marker, filled in variants:
                    v, tab, rk = _mapGiven(h, cx, ρ, part)
                    gid = markId(name, 'given', part, h, 'commonX' if cx else 'vectorX', _rhoPart(ρ))
                    point(ax, v, y, colour[ρ], marker, filled, gid,
                          ring = h == 'US' and cx == head and np.isclose(ρ, paperρ))
                    marks.append(mark(gid, hostLabel, v, signed(v, unit = 'p.p.'),
                                      series = 'ρ = {}, {}'.format(C.num(ρ, 1), varName(cx)),
                                      panel = 'Design given: ' + plain(title), table = tab, row = rk))

    axes = sfChosen.subplots(1, len(MAPCHOSEN), sharey = True)
    for ax, (scen, title) in zip(axes, MAPCHOSEN):
        _mapPanel(ax, title, [lab for _, _, lab in MAPSPECS], chosenRows, chosenExt)
        for (kind, key, lab), (slots, centre, _) in zip(MAPSPECS, chosenRows):
            if not _mapRun(kind, key, scen):
                _mapEmpty(ax, centre, 'not run')
                continue
            for ρ, y in zip([paperρ] if kind == 'xi' else ρs, slots):
                v, tab, rk = _mapChosen(kind, key, ρ, scen)
                gid = markId(name, 'chosen', scen, kind, key, _rhoPart(ρ))
                point(ax, v, y, colour[ρ], 'o', True, gid,
                      ring = kind == 'host' and key == 'US' and np.isclose(ρ, paperρ))
                marks.append(mark(gid, plain(lab), v, signed(v, digits = 3),
                                  series = 'ρ = ' + C.num(ρ, 1), panel = 'Design chosen: ' + plain(title),
                                  table = tab, row = rk))

    # The headline variant is the paper's and goes unnamed (config.variantNote); only the twin's open
    # diamond is keyed. A filled grey key for it would read as rho = 2.
    ink = lambda **kw: Line2D([], [], linestyle = 'none', **kw)
    handles = ([ink(marker = 'o', markersize = MAPMS, markerfacecolor = colour[ρ], markeredgecolor = '#fcfcfb',
                    markeredgewidth = 0.5) for ρ in ρs]
               + [ink(marker = 'D', markersize = MAPMS + 1.6, markerfacecolor = 'none',
                      markeredgecolor = INK['secondary'], markeredgewidth = 1.0),
                  ink(marker = 'o', markersize = MAPRING, markerfacecolor = 'none',
                      markeredgecolor = INK['primary'], markeredgewidth = 0.9)])
    labels = ([r'$\rho = ' + C.num(ρ, 1) + '$' for ρ in ρs]
              + [r'vector $X_i$ calibration', "the paper's reading"])
    sfChosen.legend(handles, labels, loc = 'outside lower center', ncol = len(handles), frameon = False,
                    fontsize = 7, labelcolor = INK['secondary'], columnspacing = 1.4, handletextpad = 0.3)
    return _save(fig, name, marks)
