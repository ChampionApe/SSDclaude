r""" Figure 1.1's panels with the model beside the data (python/US/runOECD26.py, results/oecd26/): the data's
countries and fitted line in the first series colour, the model's in the second, one panel per relation of
tablesOECD26.RELATIONS. Layer 1 draws all five panels; layer 2 matches spending by construction and draws the
two panels of the index. The arguments (turnout, sample, reading) are tablesOECD26's.
"""
import numpy as np

import config as C
import oecdFigure1 as F1
from figures import plt, SERIES, INK, _panel, _save, markId, mark
from tablesOECD26 import RELATIONS, panelData, ols, suffix, _xy

MARKFMT = dict(F1.MARKFMT)
AXIS = {'spending': (0, 20), 'index': (0.44, 1.07)}


def oecd26Figure(layer = 1, turnout = 'cps', sample = '26', reading = 'inForce'):
    r""" OECD26_Layer1 (layer 1) or its layer-2 counterpart OECD26_Layer2: 2x3 as figure 1.1, the legend in
    the sixth cell (layer 1), or 1x3 with the index panels (layer 2). Every dot and line is a mark; a dot is
    linked to its country's row of OECD26_Omega (lowercase ISO3), a line carries its slope. """
    p = panelData(layer, turnout, sample, reading)
    sfx = suffix(turnout, sample, reading)
    name = 'OECD26_Layer{}'.format(layer) + sfx
    cells = ([(0, 0, 'spending', 'growth'), (0, 1, 'spending', 'gini'), (0, 2, 'spending', 'index'),
              (1, 0, 'index', 'growth'), (1, 1, 'index', 'gini')] if layer == 1 else
             [(0, 0, 'index', 'growth'), (0, 1, 'index', 'gini')])
    rows = 2 if layer == 1 else 1
    fig, axes = plt.subplots(rows, 3, figsize = (5.91, 3.9 if layer == 1 else 2.15), constrained_layout = True,
                             squeeze = False)
    marks = []
    for r, c, yv, xv in cells:
        if (yv, xv) not in RELATIONS:
            raise ValueError('{}: ({}, {}) is not one of tablesOECD26.RELATIONS'.format(name, yv, xv))
        ax = axes[r, c]
        _panel(ax, '', '', titlesize = 8, labelsize = 7)
        (xn, xf), (yn, yf) = MARKFMT[xv], MARKFMT[yv]
        for side, colour, z in (('Data', SERIES[0], 3), ('Model', SERIES[1], 4)):
            x, y = _xy(p, yv, xv, side)
            for iso in p.index:
                pt, = ax.plot(x[iso], y[iso], linestyle = 'none', marker = 'o' if side == 'Data' else 'D',
                              markersize = 3.6, color = colour, markeredgecolor = '#fcfcfb',
                              markeredgewidth = 0.5, zorder = z)
                pt.set_gid(markId(name, yv + '_' + xv, side.lower(), iso.lower()))
                marks.append(mark(pt.get_gid(), p.at[iso, 'country'], y[iso],
                                  '{}: {}; {}: {}'.format(xn, xf.format(x[iso]), yn, yf.format(y[iso])),
                                  series = side.lower(), panel = '{} against {}'.format(yn, xn),
                                  table = 'OECD26_Omega' + sfx if layer == 2 else None,
                                  row = iso.lower() if layer == 2 else None))
            o = ols(x, y)
            xs = np.linspace(float(x.min()), float(x.max()), 2)
            ln, = ax.plot(xs, o['intercept'] + o['slope']*xs, color = colour, linewidth = 1.2, zorder = z - 1)
            ln.set_gid(markId(name, yv + '_' + xv, side.lower(), 'fit'))
            marks.append(mark(ln.get_gid(), 'fitted line', o['slope'],
                              'slope {:.2f} (s.e. {:.2f})'.format(o['slope'], o['se']), series = side.lower(),
                              panel = '{} against {}'.format(yn, xn), table = 'OECD26_Slopes' + sfx,
                              row = yv + '_' + xv))
        if c == 0:
            ax.set_ylabel(F1.LABEL[F1.NAMED[yv]], color = INK['secondary'], fontsize = 7.5)
        if r == rows - 1 or (layer == 1 and c == 2):
            ax.set_xlabel(F1.LABEL[F1.NAMED[xv]], color = INK['secondary'], fontsize = 7.5)
        if yv == 'index':
            ax.set_ylim(*AXIS['index'])
        else:
            ax.set_ylim(0, max(AXIS['spending'][1], float(np.nanmax(p[['spendingData', 'spendingModel']].values)) + 1))
        if xv == 'index':
            ax.set_xlim(*AXIS['index'])
    legendAx = axes[rows - 1, 2]
    legendAx.axis('off')
    dot = lambda colour, marker: plt.Line2D([], [], linestyle = '-', linewidth = 1.2, marker = marker,
                                            markersize = 3.6, color = colour, markeredgecolor = '#fcfcfb',
                                            markeredgewidth = 0.5)
    n = len(p)
    leg = legendAx.legend([dot(SERIES[0], 'o'), dot(SERIES[1], 'D')],
                          ['data', 'model, layer {}'.format(layer)], loc = 'center', frameon = False, fontsize = 7,
                          labelcolor = INK['secondary'], title = '{} countries, fitted lines'.format(n),
                          title_fontsize = 7)
    leg.get_title().set_color(INK['secondary'])
    return _save(fig, name, marks)
