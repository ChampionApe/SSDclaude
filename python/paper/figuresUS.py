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
from matplotlib.lines import Line2D

import config as C
import datasets as D
from figures import SERIES, INK, LW, _panel, _save


# The order the paper's discussion moves in: pension design first, then ageing (the two it identifies as
# the main determinants), then the three French characteristics. Reading the finished figure
# top-to-bottom should reproduce that ranking, so the order is fixed here rather than sorted by effect
# size: a figure whose ordering changes with the data cannot be referred to in prose. The composite
# rows (all three French characteristics, France's own path) are the tables' business, not this figure's.
SCENARIOS = [(r'$\theta = 0$',        r'$\theta = 0$',        'design'),
             (r'$\theta = 1$',        r'$\theta = 1$',        'design'),
             ('Acute ageing',         'Acute ageing',         'ageing'),
             ('Mild ageing',          'Mild ageing',          'ageing'),
             ('French voting',        'Voting',               'french'),
             ('French income distr.', 'Income distribution',  'french'),
             ('French leisure',       'Leisure preferences',  'french')]

# The three reported quantities, as (csv column, panel title, axis label, how to scale a deviation).
# tau and srOverY are fractions on the csv and are read in percentage points; the workweek is already
# in hours (normalised inside the experiment script against that rho's own baseline) and its deviation
# is in hours. Do NOT re-derive the workweek from hbar here -- see tablesUS.py.
PANELS = [('τ',        'Equilibrium tax rate',    'Change in $\\tau$ (percentage points)',      100.),
          ('srOverY',  'Savings over GDP',        'Change in $s/Y$ (percentage points of GDP)', 100.),
          ('workweek', 'Average workweek',        'Change in average hours worked per week',    1.)]

# Colours for the three rho values: the categorical pair plus one ink shade -- three is one more than
# the validated pair carries, so the extra slot is deliberately NEUTRAL rather than a third hue guessed
# by eye. Fixed order, never cycled.
RHOCOLOURS = [SERIES[0], SERIES[1], INK['secondary']]


def _barPanel(ax, title, xlabel, labels, series, colours):
    r""" One horizontal grouped-bar panel: `series` is a list of (label, values) over `labels`, drawn as
    one bar per series within each scenario group. """
    y = np.arange(len(labels))
    height = 0.8/len(series)
    # _panel FIRST: it sets tick_params, which would otherwise recolour the scenario labels to the muted
    # ink meant for numeric ticks. These are the figure's row headings and belong in primary ink.
    _panel(ax, title, '')
    for k, (lab, vals) in enumerate(series):
        off = (k - (len(series)-1)/2)*height
        ax.barh(y + off, vals, height = height, color = colours[k], label = lab,
                edgecolor = 'none', zorder = 3)
    ax.axvline(0, color = INK['primary'], linewidth = 1.0, zorder = 4)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize = 9, color = INK['primary'])
    ax.set_xlabel(xlabel, color = INK['secondary'], fontsize = 8.5)
    ax.grid(axis = 'y', visible = False)


def _topDown(axes):
    """ Put the first scenario at the TOP, once for the whole row of panels.

    NOT inside the per-panel helpers: these axes are created with sharey=True, so they are one y-axis
    wearing several faces and every invert_yaxis() call flips it again. Called per panel it reverses
    the scenario order on any EVEN number of panels and leaves it alone on any odd number. Invert once,
    on one axis, and the count stops mattering. """
    axes[0].invert_yaxis()


def _figLegend(fig, handles, labels, note, bottom = 0.09):
    """ One legend for the whole figure, below the panels, plus a one-line note on the baseline the
    deviations are measured from. Figure-level rather than per-panel: the series mean the same thing
    in every panel, so repeating the key would be redundant. """
    fig.tight_layout(rect = (0, bottom, 1, 1))
    fig.legend(handles, labels, loc = 'lower center', ncol = len(handles), frameon = False,
               fontsize = 9, bbox_to_anchor = (0.5, 0.035))
    fig.text(0.5, 0.005, note, ha = 'center', va = 'bottom', fontsize = 8, color = INK['secondary'])


def _rowsPresent(df, ρs, scenarios, effect = 'full'):
    r""" The subset of `scenarios` for which every rho has a row: a scenario the run did not produce
    should drop out of the figure rather than take the whole build down with it, and a scenario missing
    at SOME rho is dropped too -- a bar group with a hole in it reads as a zero. """
    out = []
    for entry in scenarios:
        try:
            for ρ in ρs:
                D.usShockRow(df, ρ, entry[1], effect)
        except D.MissingInput:
            continue
        out.append(entry)
    return out


def usOverview(commonX = None):
    r""" Figure \ref{fig:US:overview}: every single-characteristic counterfactual's effect on the tax
    rate, savings over GDP and the average workweek, in deviations from the baseline, at each rho in
    config.US['rhoTable'].

    Read as: which characteristics move each outcome, and does that ranking survive the IES. Ageing and
    pension design should dominate the tax panel and the three French characteristics should be visibly
    minor there -- while the workweek panel inverts that, since leisure preferences are a pure change of
    the hours unit and move hours alone. Putting the three panels side by side on a SHARED scenario axis
    is what makes that inversion readable.
    """
    commonX = C.US['commonX'] if commonX is None else commonX
    df = D.usShocks(commonX = commonX)
    ρs = C.US['ρTable']
    scen = _rowsPresent(df, ρs, SCENARIOS)
    labels = [lab for lab, _, _ in scen]
    colours = RHOCOLOURS[:len(ρs)]

    fig, axes = plt.subplots(1, len(PANELS), figsize = (10.6, 0.42*len(labels) + 2.6), sharey = True)
    for ax, (col, title, xlabel, scale) in zip(axes, PANELS):
        series = []
        for ρ in ρs:
            base = D.usBaseline(df, ρ)[col]
            series.append((r'$\rho = ' + C.num(ρ, 1) + '$',
                           [scale*(D.usShockRow(df, ρ, s, 'full')[col] - base) for _, s, _ in scen]))
        _barPanel(ax, title, xlabel, labels, series, colours)
    _topDown(axes)
    b = D.usBaseline(df, C.US['ρBaseline'])
    handles, labs = axes[0].get_legend_handles_labels()
    _figLegend(fig, handles, labs,
               'Deviations from the calibrated US baseline, which at $\\rho = {}$ is a tax rate of '
               '{:.1f}%, savings of {:.1f}% of GDP and a {:.1f}-hour week. Savings are relative to '
               'GDP, $s/Y$.'.format(C.num(C.US['ρBaseline'], 1), 100*b['τ'], 100*b['srOverY'],
                                    b['workweek']))
    return _save(fig, 'US_overview' + C.variantSuffix(commonX))


# ---------------------------------------------------------------------------------------------------
# Endogenous system characteristics (app:ESC)
# ---------------------------------------------------------------------------------------------------
# The counterfactual set the appendix runs, in the same order as the main-text figure where the two
# overlap. 'mild' is absent: runESCcrra.py's scenario set does not include it, so it exists at rho = 1
# only and a row of it would be a hole at two thirds of the grid. 'frBoth' has no main-text
# counterpart: it is the pair whose two halves move the DESIGN in opposite directions, which is why the
# appendix runs it. 'frAll' is left out: by scale invariance it carries the same design, tax and
# savings as 'frBoth' and differs only in hours, which this figure does not report.
ESCSCENARIOS = [('Acute ageing',            'acute'),
                ('French voting',           'frVoting'),
                ('French income distr.',    'frIncome'),
                ('French leisure',          'frLeisure'),
                ('Income distr.\n+ voting', 'frBoth')]


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


def _dumbbellPanel(ax, title, xlabel, labels, pairs, colours, ref = 0., extraRefs = ()):
    r""" One horizontal dumbbell panel. `pairs` is a list over series (rho values) of
    (label, [(x_pinned, x_chosen) per scenario]); each pair is drawn as an open marker at the pinned
    reading, a filled marker at the chosen one and a connector in the series colour, so the DISTANCE
    between the two readings -- the design response -- is the mark itself rather than a gap the reader
    has to measure between a bar end and a marker. `ref` is the ink reference line (0 for a deviation
    panel, the US design for the level panel); `extraRefs` are muted lines (the corners of theta). """
    y = np.arange(len(labels))
    off = np.linspace(-0.27, 0.27, len(pairs)) if len(pairs) > 1 else [0.]
    _panel(ax, title, '')
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
        ax.scatter(x0, yy, s = 34, facecolors = 'white', edgecolors = colours[k], linewidths = 1.4,
                   zorder = 5)
        ax.scatter(x1, yy, s = 34, facecolors = colours[k], edgecolors = 'white', linewidths = 0.8,
                   zorder = 6)
    for yk in y[:-1]:
        ax.axhline(yk + 0.5, color = INK['grid'], linewidth = 0.8, zorder = 1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize = 9, color = INK['primary'])
    ax.set_xlabel(xlabel, color = INK['secondary'], fontsize = 8.5)
    ax.grid(axis = 'y', visible = False)


def escOverview():
    r""" Figure \ref{fig:US_ESC:overview}: what each counterfactual does when the pension design is
    chosen politically, against what it does at a fixed design -- as dumbbells from the pinned reading
    (open marker) to the chosen one (filled marker), one per (scenario, rho).

    Three panels. The design itself first, as a LEVEL: every dumbbell there starts at the US design,
    so its length is the design response and the muted lines at 0 and 1 are the corners the text refers
    to. Then the tax rate and savings over GDP as deviations from the endogenous-theta baseline, so the
    pinned end is the main-text reading and the dumbbell is what endogenising the design adds. A
    dumbbell that collapses to a dot IS the finding for that row (ageing, leisure).

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
    panels = [('θ_t0',  'Pension design in 2020',
               '$\\theta$ in force (0 = Beveridgean, 1 = Bismarckian)', 1., True),
              ('τ_t0',  'Equilibrium tax rate', 'Change in $\\tau$ (percentage points)', 100., False),
              ('sr_t0', 'Savings over GDP', 'Change in $s/Y$ (percentage points of GDP)',
               100.*(1 - α), False)]

    fig, axes = plt.subplots(1, len(panels), figsize = (9.6, 0.75*len(labels) + 2.3), sharey = True)
    for ax, (col, title, xlabel, scale, level) in zip(axes, panels):
        pairs = []
        for ρ in ρs:
            # Both readings are measured against the ENDOGENOUS baseline, so the two are on one scale
            # and the dumbbell length is the design response and nothing else. Reading the pinned rows
            # against a pinned baseline instead would fold the baseline's own design response into it.
            base = 0. if level else float(D.escRow(df, ρ, spec, 'baseline', False)[col])
            pairs.append((r'$\rho = ' + C.num(ρ, 1) + '$',
                          [(scale*(float(D.escRow(df, ρ, spec, s, True)[col]) - base),
                            scale*(float(D.escRow(df, ρ, spec, s, False)[col]) - base))
                           for _, s in scen]))
        _dumbbellPanel(ax, title, xlabel, labels, pairs, colours,
                       ref = θstar if level else 0., extraRefs = (0., 1.) if level else ())
    axes[0].set_xlim(-0.04, 1.06)
    _topDown(axes)

    handles = [Line2D([], [], color = c, linewidth = 1.8, label = r'$\rho = ' + C.num(ρ, 1) + '$')
               for c, ρ in zip(colours, ρs)]
    handles += [Line2D([], [], marker = 'o', linestyle = 'none', markerfacecolor = 'white',
                       markeredgecolor = INK['primary'], markersize = 6,
                       label = '$\\theta$ pinned at the US design'),
                Line2D([], [], marker = 'o', linestyle = 'none', markerfacecolor = INK['primary'],
                       markeredgecolor = 'white', markersize = 6,
                       label = '$\\theta$ chosen by the electorate')]
    ρ0 = C.US['ρBaseline']
    b = D.escRow(df, ρ0, spec, 'baseline', False)
    _figLegend(fig, handles, [h.get_label() for h in handles],
               'Deviations from the endogenous-$\\theta$ baseline, which at $\\rho = {}$ chooses '
               '$\\theta = {:.3f}$, a tax rate of {:.1f}% and savings of {:.1f}% of GDP. Savings are '
               'relative to GDP, $s/Y$.'.format(C.num(ρ0, 1), θstar, 100*float(b['τ_t0']),
                                                100*(1 - α)*float(b['sr_t0'])),
               bottom = 0.1)
    return _save(fig, 'US_ESC_overview')
