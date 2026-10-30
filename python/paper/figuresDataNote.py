r""" The technical note's data part (writing/data/): three descriptive figures of the OECD cross-section's θ and
τ variants. Reads data/oecd26_theta.csv only (written by oecd26Theta.py); writes writing/data/figs/*.pdf. Not
wired into build.py: the note is not the paper, and no result enters.

Run:  .venv\Scripts\python.exe -I python\paper\figuresDataNote.py
      -> writing/data/figs/dataThetaVariants.pdf, dataTauVariants.pdf, dataThetaPaperA.pdf; prints the numbers
         the note's text quotes

θ is NaN in the csv where A's slope is negative (AUS, DNK, ISL: a public pension tested against the private one);
the figures draw those at the axis edge with a marker of their own, never at a filled value.
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figures import plt, SERIES, INK, _panel        # house style; importing reads no file

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
CSV = os.path.join(REPO, 'data', 'oecd26_theta.csv')
OUT = os.path.join(REPO, 'writing', 'data', 'figs')
EDGE = -0.08                                         # where a negative A slope is drawn
OFFSET = {'POL': (-14, 3), 'ITA': (4, 0), 'FIN': (4, -6), 'HUN': (4, 1), 'LUX': (-14, 2), 'NOR': (3, -6)}


def load():
    d = pd.read_csv(CSV)
    w = d.pivot(index = 'iso3', columns = 'variant', values = 'theta')
    raw = d.pivot(index = 'iso3', columns = 'variant', values = 'thetaRaw')
    a = d[d.variant == 'A'].set_index('iso3')
    w['Araw'] = raw['A']
    w['tauA'] = 100*a['tau']
    w['tauB'] = 100*d[d.variant == 'B'].set_index('iso3')['tau']
    w['privShare'] = a['privShare']
    w['inC'] = d[d.variant == 'C'].set_index('iso3')['inSample'].astype(bool)
    return w


def _save(fig, name):
    os.makedirs(OUT, exist_ok = True)
    fig.savefig(os.path.join(OUT, name + '.pdf'), metadata = {'CreationDate': None, 'ModDate': None})
    plt.close(fig)


def _legend(ax, handles, labels, **kw):
    ax.legend(handles, labels, frameon = False, fontsize = 7, labelcolor = INK['secondary'], **kw)


def thetaVariants(w):
    """ (i) θ by country under paper, A and B, sorted by A's raw slope; C's dropped countries in muted ink. """
    w = w.sort_values('Araw')
    y = np.arange(len(w))
    fig, ax = plt.subplots(figsize = (5.91, 3.7), constrained_layout = True)
    _panel(ax, '', '', labelsize = 7)
    ax.grid(True, axis = 'y', color = INK['grid'], linewidth = 0.5)
    mk = dict(linestyle = 'none', markersize = 4.2, markeredgewidth = 0.8)
    hp, = ax.plot(w['paper'], y, marker = 's', color = INK['muted'], markerfacecolor = 'none', **mk)
    hb, = ax.plot(w['B'], y, marker = 'D', color = SERIES[1], markerfacecolor = 'none', **mk)
    ha, = ax.plot(w['A'], y, marker = 'o', color = SERIES[0], markeredgecolor = '#fcfcfb',
                  **{**mk, 'markeredgewidth': 0.5})
    neg = w['A'].isna()
    hn, = ax.plot(np.full(neg.sum(), EDGE), y[neg.to_numpy()], marker = '<', color = SERIES[0], **mk)
    ax.set_yticks(y)
    ax.set_yticklabels([iso + ('' if inC else '*') for iso, inC in zip(w.index, w['inC'])])
    for t, inC in zip(ax.get_yticklabels(), w['inC']):
        t.set_color(INK['primary'] if inC else INK['muted'])
    ax.set_xlim(EDGE - 0.04, 1.04)
    ax.set_ylim(-0.7, len(w) - 0.3)
    ax.set_xlabel(r'$\theta$', color = INK['secondary'], fontsize = 8)
    fig.legend([hp, ha, hn, hb], ['paper (figure 1.1)', 'A, public tier', 'A < 0', 'B, all mandatory'],
               loc = 'outside lower center', ncol = 4, frameon = False, fontsize = 7, labelcolor = INK['secondary'],
               title = '* not in C', title_fontsize = 7)
    _save(fig, 'dataThetaVariants')


def tauVariants(w):
    """ (ii) τ by country: the public system (A, C) and its addition in B, labelled with the private share. """
    w = w.sort_values('tauB')
    y = np.arange(len(w))
    fig, ax = plt.subplots(figsize = (5.91, 3.7), constrained_layout = True)
    _panel(ax, '', '', labelsize = 7)
    ax.grid(False, axis = 'y')
    hA = ax.barh(y, w['tauA'], height = 0.7, color = SERIES[0], edgecolor = 'none')
    hB = ax.barh(y, w['tauB'] - w['tauA'], left = w['tauA'], height = 0.7, color = SERIES[1], edgecolor = 'none')
    for yi, (tb, ps) in enumerate(zip(w['tauB'], w['privShare'])):
        if ps >= 0.005:
            ax.text(tb + 0.3, yi, '{:.0f}%'.format(100*ps), va = 'center', fontsize = 6.5, color = INK['secondary'])
    ax.set_yticks(y)
    ax.set_yticklabels(w.index)
    for t, inC in zip(ax.get_yticklabels(), w['inC']):
        t.set_color(INK['primary'] if inC else INK['muted'])
    ax.set_ylim(-0.7, len(w) - 0.3)
    ax.set_xlim(0, 28)
    ax.set_xlabel(r'$\tau$, % of labour income', color = INK['secondary'], fontsize = 8)
    _legend(ax, [hA, hB], ['public (paper, A, C)', 'added in B (label: private share of B)'], loc = 'lower right')
    _save(fig, 'dataTauVariants')


def thetaPaperA(w):
    """ (iii) A's θ against the paper's, with the 45° line; countries not in C hollow, A < 0 at the bottom edge. """
    fig, ax = plt.subplots(figsize = (4.0, 3.5), constrained_layout = True)
    _panel(ax, '', '', labelsize = 7)
    ax.plot([0, 1], [0, 1], color = INK['muted'], linewidth = 0.8, linestyle = '--', zorder = 1)
    for iso, r in w.iterrows():
        yv = r['A'] if np.isfinite(r['A']) else EDGE
        filled = bool(r['inC'])
        ax.plot(r['paper'], yv, linestyle = 'none', marker = 'o' if np.isfinite(r['A']) else 'v', markersize = 4.2,
                color = SERIES[0], markerfacecolor = SERIES[0] if filled else 'none',
                markeredgecolor = '#fcfcfb' if filled else SERIES[0], markeredgewidth = 0.5 if filled else 0.8,
                zorder = 3)
        ax.annotate(iso, (r['paper'], yv), xytext = OFFSET.get(iso, (3, 2)), textcoords = 'offset points', fontsize = 5.5,
                    color = INK['secondary'])
    ax.set_xlim(-0.05, 1.1)
    ax.set_ylim(EDGE - 0.05, 1.1)
    ax.set_xlabel(r'$\theta$, paper (figure 1.1)', color = INK['secondary'], fontsize = 8)
    ax.set_ylabel(r'$\theta$, A', color = INK['secondary'], fontsize = 8)
    h1 = plt.Line2D([], [], linestyle = 'none', marker = 'o', color = SERIES[0], markeredgecolor = '#fcfcfb')
    h2 = plt.Line2D([], [], linestyle = 'none', marker = 'o', color = SERIES[0], markerfacecolor = 'none')
    h3 = plt.Line2D([], [], linestyle = 'none', marker = 'v', color = SERIES[0], markerfacecolor = 'none')
    _legend(ax, [h1, h2, h3], ['in C', 'not in C', 'A < 0'], loc = 'upper left')
    _save(fig, 'dataThetaPaperA')


def numbers(w):
    """ The numbers the note quotes, printed for checking against the text. """
    f = w[np.isfinite(w['A'])]
    print('paper theta = 1:', list(w.index[w['paper'] >= 0.9995]), ' = 0:', list(w.index[w['paper'] <= 5e-4]))
    print('A theta >= .99:', list(f.index[f['A'] >= 0.99]), ' <= .01:', list(f.index[f['A'] <= 0.01]),
          ' NaN:', list(w.index[w['A'].isna()]))
    print('mean paper {:.3f}, mean A {:.3f} (23 with A), mean paper on same {:.3f}; corr {:.3f}'.format(
        w['paper'].mean(), f['A'].mean(), f['paper'].mean(), np.corrcoef(f['paper'], f['A'])[0, 1]))
    print('paper - A: max {} {:.3f}; A > paper: {}'.format(
        (f['paper'] - f['A']).idxmax(), (f['paper'] - f['A']).max(), list(f.index[f['A'] > f['paper'] + 1e-3])))
    print('C sample', int(w['inC'].sum()), 'dropped', list(w.index[~w['inC']]))
    print(w[['paper', 'A', 'A2pt', 'B', 'tauA', 'tauB', 'privShare']].round(3).sort_values('A').to_string())
    print('tauA range {:.1f} ({}) to {:.1f} ({})'.format(w['tauA'].min(), w['tauA'].idxmin(), w['tauA'].max(),
                                                         w['tauA'].idxmax()))


def main():
    w = load()
    thetaVariants(w)
    tauVariants(w)
    thetaPaperA(w)
    numbers(w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
