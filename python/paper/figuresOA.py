r""" Figure builders for the online appendix (notes/brief_onlineAppendix_2026-10-06.md, section 2.3). House
style from figures.py (_panel, SERIES, INK) and figuresUS.RHOCOLOURS; drawn at the measure (5.91 in).

Each writes results/paper/Figs/<name>.{pdf,png,svg} and <name>.marks.json through figures._save. Every data
point is its own artist, tagged with figures.markId, and its mark names the table and row that print it;
the text of a mark is the cell of that row (tablesOA's formatters), with tex escapes removed. Lines are drawn
untagged beneath the points.
"""
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import config as C
import datasets as D
import tablesOA as T
from tablesUS import COUNTRYNAME
from figures import SERIES, INK, _panel, _save, markId
from figuresUS import RHOCOLOURS

MARKERS = ('o', 's', '^')
SURFACE = '#fcfcfb'
WIDTH = 5.91                       # \linewidth of the paper, in inches


def _plain(text):
    """ A tex cell as a mark's text: escapes and math shifts removed ('15.06\\%' -> '15.06%'). """
    return text.replace('\\%', '%').replace('$', '')


def _point(ax, x, y, gid, colour, marker = 'o', ms = 3.6, z = 4):
    """ One tagged data mark, a Line2D of its own so that the svg carries its id exactly once. """
    (pt,) = ax.plot([x], [y], linestyle = 'none', marker = marker, markersize = ms, color = colour,
                    markeredgecolor = SURFACE, markeredgewidth = 0.5, zorder = z)
    pt.set_gid(gid)
    return pt


def _mark(gid, label, series, panel, value, text, table, row):
    return {'id': gid, 'label': label, 'series': series, 'panel': panel, 'value': float(value),
            'text': text, 'table': table, 'row': row}


def _style(ax, title, ylabel = '', xlabel = None):
    _panel(ax, title, ylabel, titlesize = 8.5, labelsize = 7)
    ax.yaxis.label.set_fontsize(7.5)
    if xlabel:
        ax.set_xlabel(xlabel, color = INK['secondary'], fontsize = 7.5)


def _key(handles, labels, ax, **kw):
    leg = ax.legend(handles, labels, frameon = False, fontsize = 7, labelcolor = INK['secondary'], **kw)
    return leg


# ---------------------------------------------------------------------------------------------------
# The calibrations across rho
# ---------------------------------------------------------------------------------------------------
def _rhoPanel(ax, xs, ys, gids, colour, marker, highlight = None):
    """ A line through (xs, ys), untagged, and one tagged point per value. `highlight`: the x drawn in ink
    (the paper's rho). """
    ax.plot(xs, ys, color = colour, linewidth = 1.2, zorder = 3)
    for x, y, gid in zip(xs, ys, gids):
        ink = highlight is not None and np.isclose(x, highlight)
        _point(ax, x, y, gid, INK['primary'] if ink else colour, marker, ms = 4.2 if ink else 3.4,
               z = 5 if ink else 4)


ARGPANELS = [('β',  r'Discount factor $\beta$',             'Discount factor β',             '',               1.),
             ('ω',  r'Political weight of the old $\omega$', 'Political weight of the old ω', '',               1.),
             ('sr', 'Savings rate, % of GDP',               'Savings rate {year}, % of GDP', '',               100.),
             ('ι',  r'Informal savings ratio $\iota$',       'Informal savings ratio ι',      '',               1.),
             ('η0', r'Productivity $\eta_0$',                'Informal productivity η0',      '',               1.),
             ('X0', r'Taste for leisure $X_0$',              'Informal taste for leisure X0', '',               1.)]
ARGASCII = {'β': 'beta', 'ω': 'omega', 'sr': 'sr', 'ι': 'iota', 'η0': 'eta0', 'X0': 'X0'}    # mark-id parts


def argRhoGrid(commonX = None):
    r""" The Argentine calibration across the rho grid (results/calibration/informalSavings_rhoGrid*): beta,
    omega, the savings rate and the informal savings ratio of the calibration year, eta_0 and X_0, one panel
    each against rho, the paper's rho in ink. Marks link to ARG_RhoGridTable's `rho@<rho>` rows. The common X,
    which the vector-X sweep does not record, is in the table only, so the two twins draw the same panels. """
    commonX = C.ARG['commonX'] if commonX is None else commonX
    sfx = C.variantSuffix(commonX, 'ARG')
    name, table = 'ARG_RhoGrid' + sfx, 'ARG_RhoGridTable' + sfx
    g = T.argRhoGrid(commonX)
    fmt = {c: f for c, _, f in T.ARGRHOCOLS}
    year = C.calendar()['year0']
    ρ1 = C.ARG['ρBaseline']
    fig, axes = plt.subplots(2, 3, figsize = (WIDTH, 3.9), constrained_layout = True, sharex = True)
    marks = []
    for k, (ax, (col, title, plainTitle, ylabel, scale)) in enumerate(zip(axes.ravel(), ARGPANELS)):
        _style(ax, title.format(year = year), ylabel, '$\\rho$' if k >= 3 else None)
        xs, ys = g['ρ'].values.astype(float), scale*g[col].values.astype(float)
        gids = [markId(name, ARGASCII[col], 'rho' + C.num(x, 1)) for x in xs]
        _rhoPanel(ax, xs, ys, gids, SERIES[0], 'o', highlight = ρ1)
        for x, v, gid in zip(xs, g[col].values.astype(float), gids):
            marks.append(_mark(gid, 'ρ = ' + C.num(x, 1), '', plainTitle.format(year = year), scale*v,
                               _plain(fmt[col](v)), table, 'rho@' + T._rhoKey(x)))
    dot = lambda c, ms: Line2D([], [], linestyle = 'none', marker = 'o', markersize = ms, color = c,
                               markeredgecolor = SURFACE, markeredgewidth = 0.5)
    fig.legend([dot(SERIES[0], 3.4), dot(INK['primary'], 4.2)],
               ['calibration at each $\\rho$', '$\\rho = ' + C.num(ρ1, 0) + '$, the paper\'s specification'],
               loc = 'outside lower center', ncol = 2, frameon = False, fontsize = 7, labelcolor = INK['secondary'])
    return _save(fig, name, marks)


OECDPANELS = [('β',  r'Discount factor $\beta$ (all three)', 'Discount factor β',            '',               1.),
              ('ω',  r'Political weight of the old $\omega$', 'Political weight of the old ω', '',               1.),
              ('X',  r'Taste for leisure $X$',               'Taste for leisure X',           '',               1.),
              ('R',  r'Interest factor $R$, 30 years',       'Interest factor R, 30 years',   '',               1.),
              ('sr', 'Savings rate, % of GDP',               'Savings rate {year}, % of GDP', '',               100.)]
ASCII = {'β': 'beta', 'ω': 'omega', 'X': 'X', 'R': 'R', 'sr': 'sr'}


def oecdRhoGrid(commonX = None):
    r""" The U.S., UK and French calibrations across the rho grid (results/calibration/{US,UK,FR}_rhoGrid*):
    beta (calibrated for the U.S. and imposed on the other two, so drawn once), omega, the common X, the
    30-year interest factor R and the savings rate of the calibration year, one panel each against rho, a
    series per country, the paper's rho in ink. Under vector X the sweeps record no X and its panel is left
    out. Marks link to OECD_RhoGridTable's `<iso3>@<rho>` rows. """
    commonX = C.US['commonX'] if commonX is None else commonX
    sfx = C.variantSuffix(commonX)
    name, table = 'OECD_RhoGrid' + sfx, 'OECD_RhoGridTable' + sfx
    sw = T.oecdSweeps(commonX)
    fmt = {c: f for c, _, f in T.OECDRHOCOLS}
    year = C.usCalendar()['year0']
    ρ1 = C.US['ρBaseline']
    panels = [p for p in OECDPANELS if commonX or p[0] != 'X']
    fig, axes = plt.subplots(2, 3, figsize = (WIDTH, 4.1), constrained_layout = True, sharex = True)
    slots = axes.ravel()
    marks = []
    colours = dict(zip([c for c, _ in T.OECDHOSTS], (SERIES[0], SERIES[1], INK['secondary'])))
    markers = dict(zip([c for c, _ in T.OECDHOSTS], MARKERS))
    for k, (ax, (col, title, plainTitle, ylabel, scale)) in enumerate(zip(slots, panels)):
        # an axis gets the rho label where no panel sits below it
        below = k >= 3 or k + 3 >= len(panels)
        _style(ax, title.format(year = year), ylabel, '$\\rho$' if below else None)
        ax.tick_params(labelbottom = below)
        hosts = T.OECDHOSTS[:1] if col == 'β' else T.OECDHOSTS
        for c, key in hosts:
            g = sw[c]
            xs, vs = g['ρ'].values.astype(float), g[col].values.astype(float)
            gids = [markId(name, ASCII[col], key, 'rho' + C.num(x, 1)) for x in xs]
            _rhoPanel(ax, xs, scale*vs, gids, colours[c], markers[c], highlight = ρ1)
            for x, v, gid in zip(xs, vs, gids):
                marks.append(_mark(gid, 'ρ = ' + C.num(x, 1), COUNTRYNAME[c], plainTitle.format(year = year),
                                   scale*v, _plain(fmt[col](v)), table, key + '@' + T._rhoKey(x)))
    for ax in slots[len(panels):]:
        ax.axis('off')
    handles = [Line2D([], [], color = colours[c], marker = markers[c], markersize = 3.4, linewidth = 1.2,
                      markeredgecolor = SURFACE, markeredgewidth = 0.5) for c, _ in T.OECDHOSTS]
    handles.append(Line2D([], [], linestyle = 'none', marker = 'o', markersize = 4.2, color = INK['primary'],
                          markeredgecolor = SURFACE, markeredgewidth = 0.5))
    _key(handles, [COUNTRYNAME[c] for c, _ in T.OECDHOSTS] + ['$\\rho = ' + C.num(ρ1, 0) + '$, the paper\'s'],
         slots[len(panels)], loc = 'center')
    return _save(fig, name, marks)


# ---------------------------------------------------------------------------------------------------
# The endogenous design's baseline path
# ---------------------------------------------------------------------------------------------------
def escPath():
    r""" The design and the tax along the baseline path, chosen against pinned (tablesOA.escPathSpecs:
    escPath.csv, escPathCRRA.csv at the published method, escXiRobustness.csv). Columns: across rho at the
    workbook xi, and across xi at rho = 1 (whose workbook-xi series is the rho = 1 path of the left column,
    in the same colour). Rows: the design in force, as a level with theta* as the ink reference, and the tax
    chosen minus pinned in p.p. Marks link to ESC_PathTable's rows. """
    name, table = 'ESC_Path', 'ESC_PathTable'
    specs = T.escPathSpecs()
    ξ0, ρ1 = specs[0][5], C.US['ρBaseline']
    θstar = float(D.escCalibration()[(ρ1, C.US['esc']['spec'])]['θStar'])
    left = [s for s in specs if np.isclose(s[5], ξ0)]
    base = [s for s in left if np.isclose(s[4], ρ1)][0]
    right = sorted([(base[0], base[1], base[2], r'$\xi = ' + C.num(ξ0, 1) + '$', ρ1, ξ0)]
                   + [s for s in specs if not np.isclose(s[5], ξ0)], key = lambda s: s[5])
    colLeft = {id(s): (RHOCOLOURS[k], MARKERS[k]) for k, s in enumerate(left)}
    # the workbook-xi series on the right is the rho = 1 path on the left: same colour and marker
    refStyle = colLeft[id(base)]
    others = iter([(RHOCOLOURS[k], MARKERS[k]) for k in range(3) if (RHOCOLOURS[k], MARKERS[k]) != refStyle])
    colRight = {id(s): (refStyle if np.isclose(s[5], ξ0) else next(others)) for s in right}

    fig, axes = plt.subplots(2, 2, figsize = (WIDTH, 4.6), constrained_layout = True, sharex = True)
    panels = [('theta', r'Design in force $\theta_t$', 'Design in force θ_t', '', ),
              ('dtau', 'Tax rate, chosen minus pinned', 'Tax rate, chosen minus pinned', 'percentage points')]
    marks = []
    columns = ((left, colLeft, r'across $\rho$ ($\xi = ' + C.num(ξ0, 1) + '$)', 'rho'),
               (right, colRight, r'across $\xi$ ($\rho = ' + C.num(ρ1, 0) + '$)', 'xi'))
    for j, (specList, styles, by, tag) in enumerate(columns):
        for i, (pid, title, plainTitle, ylabel) in enumerate(panels):
            ax = axes[i, j]
            # the top panel names what its column varies, so the two columns read apart without the key
            _style(ax, title + (', ' + by if i == 0 else ''), ylabel if j == 0 else '', 'year' if i == 1 else None)
            ax.axhline(θstar if pid == 'theta' else 0., color = INK['primary'], linewidth = 0.9, zorder = 2)
            for s in specList:
                _, df, suffix, series, ρ, ξ = s
                colour, marker = styles[id(s)]
                xs = df['date'].values.astype(int)
                vs = (df['θ'].values.astype(float) if pid == 'theta'
                      else 100.*(df['τ'].values.astype(float) - df['τExo'].values.astype(float)))
                ax.plot(xs, vs, color = colour, linewidth = 1.2, zorder = 3)
                sid = (tag + C.num(ρ, 1)) if tag == 'rho' else (tag + C.num(ξ, 1))
                for (_, r), x, v in zip(df.iterrows(), xs, vs):
                    gid = markId(name, pid, sid, x)
                    _point(ax, x, v, gid, colour, marker)
                    cells = T.escPathCells(r)
                    marks.append(_mark(gid, str(x), _plain(series).replace('\\rho', 'ρ').replace('\\xi', 'ξ'),
                                       plainTitle, v, _plain(cells[0] if pid == 'theta' else cells[3]),
                                       table, T.escPathKey(x, suffix)))
        handles = [Line2D([], [], color = styles[id(s)][0], marker = styles[id(s)][1], markersize = 3.6,
                          linewidth = 1.2, markeredgecolor = SURFACE, markeredgewidth = 0.5) for s in specList]
        # The ink reference is labelled where it runs (theta* in the design panel; zero in the tax panel is
        # the pinned reading by the panel's title), so the key holds the three series alone and stays narrow
        # enough for the tax panel's upper left, which is empty in both columns until the gap opens after 2020.
        axes[0, j].annotate(r'pinned, $\theta^{\ast} = ' + C.num(θstar, 3) + '$', xy = (1., θstar),
                            xycoords = ('axes fraction', 'data'), xytext = (-2, 2), textcoords = 'offset points',
                            ha = 'right', va = 'bottom', fontsize = 7, color = INK['secondary'])
        leg = axes[1, j].legend(handles, [s[3] for s in specList], loc = 'upper left', fontsize = 7,
                                labelcolor = INK['secondary'], frameon = False)
        leg.set_zorder(6)
    return _save(fig, name, marks)
