r""" Figure builders for the US/France/UK arm. figures.py is the Argentina arm and owns the house style;
this module imports it rather than restating it, so the two arms stay one visual family.

Style rules that apply here specifically:
  * The counterfactuals are a CATEGORICAL set, not a continuous parameter, so they get the categorical
    pair -- never THETA_RAMP, which is reserved for a parameter that varies continuously.
  * The baseline is a reference line, not a series: it is drawn in ink, not in a series colour, so it
    cannot be mistaken for one of the scenarios being compared against it.
"""
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import config as C
import datasets as D
from figures import SERIES, INK, LW, _panel, _save


# The order the paper's discussion moves in: pension design first, then ageing (the two it identifies as
# the main determinants), then the three French characteristics (the minor ones). Reading the finished
# figure top-to-bottom should reproduce that ranking, so the order is fixed here rather than sorted by
# effect size -- a figure whose ordering changes with the data cannot be referred to in prose.
SCENARIOS = [(r'$\theta = 0$',        r'$\theta = 0$',        'design'),
             (r'$\theta = 1$',        r'$\theta = 1$',        'design'),
             ('Acute ageing',         'Acute ageing',         'ageing'),
             ('Mild ageing',          'Mild ageing',          'ageing'),
             ('French voting',        'Voting',               'french'),
             ('French income distr.', 'Income distribution',  'french'),
             ('French leisure',       'Leisure preferences',  'french')]


def usTaxOverview(commonX = False):
    r""" Figure \ref{fig:US:taxOverview}: every counterfactual's effect on the politico-economic tax
    rate, in percentage points from the baseline, at each rho in config.US['rhoTable'].

    Read as: which characteristics move taxes, and does that ranking survive the IES. Ageing and pension
    design should dominate; the three French characteristics should be visibly minor. Plotting the
    DEVIATION rather than the level is what makes that comparison legible -- the levels differ by a few
    points on a 14% base, which a level axis compresses into indistinguishable bars.
    """
    df = D.usShocks(commonX = commonX)
    ρs = C.US['ρTable']
    labels = [lab for lab, _, _ in SCENARIOS]
    y = np.arange(len(SCENARIOS))
    height = 0.8/len(ρs)

    fig, ax = plt.subplots(figsize = (7.6, 4.6))
    _panel(ax, 'Effect of each counterfactual on the equilibrium tax rate'
               + (' (common $X$)' if commonX else ''), '')
    # One bar group per scenario, one bar per rho. Categorical pair plus one ink shade for the third
    # rho -- three is one more than the validated pair carries, so the extra slot is deliberately
    # NEUTRAL rather than a third hue guessed by eye.
    colours = [SERIES[0], SERIES[1], INK['secondary']][:len(ρs)]
    for k, ρ in enumerate(ρs):
        base = D.usBaseline(df, ρ)['τ']
        vals = [100*(D.usShockRow(df, ρ, scen, 'full')['τ'] - base) for _, scen, _ in SCENARIOS]
        ax.barh(y + (k - (len(ρs)-1)/2)*height, vals, height = height,
                color = colours[k], label = r'$\rho = ' + C.num(ρ, 1) + '$',
                edgecolor = 'none', zorder = 3)
    ax.axvline(0, color = INK['primary'], linewidth = 1.0, zorder = 4)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize = 9, color = INK['primary'])
    ax.invert_yaxis()
    ax.set_xlabel('Change in the equilibrium tax rate (percentage points)',
                  color = INK['secondary'], fontsize = 9)
    ax.grid(axis = 'y', visible = False)
    # NOT config.pct here. It escapes the percent sign for tex, and matplotlib renders the backslash
    # literally, so the legend read "14.4\%". Anything drawn INTO a figure needs the unescaped form;
    # config.pct is for tex cells only.
    b1 = D.usBaseline(df, C.US['ρBaseline'])['τ']
    ax.legend(frameon = False, fontsize = 8, loc = 'lower right',
              title = 'baseline $\\tau$ = {:.1f}% at $\\rho={}$'.format(
                  100*b1, C.num(C.US['ρBaseline'], 1)),
              title_fontsize = 8)
    fig.tight_layout()
    return _save(fig, 'US_taxOverview' if not commonX else 'USX_taxOverview')
