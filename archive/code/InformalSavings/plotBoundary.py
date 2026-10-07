r""" The LOG/CRRA boundary artifact, before and after: one figure per response series.

Run:  .venv\Scripts\python.exe python\InformalSavings\plotBoundary.py
      ... --series d_τ_t0p1        default; the period the artifact is largest in
      ... --series d_τ_t0

Reads diagnoseLogCrraBoundary.py --test shock's output for both modes
(results/boundary/shock_<rule>_<mode>.csv) and overlays them against ρ. The point of the figure is the
single displaced anchor: under `production` settings the ρ=1 point sits off the line its four CRRA
neighbours trace, and under `common` settings it does not. Everything else about the two series is the
same experiment.

Writes results/boundary/<series>_vs_rho_<rule>.{png,pdf}. Not a test.
"""
import os, sys, argparse
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUTDIR = os.path.join(REPO, 'results', 'boundary')

LABEL = {'d_τ_t0': r'$\Delta\tau$ at $t_0$', 'd_τ_t0p1': r'$\Delta\tau$ at $t_0+1$',
         'd_s_t0': r'$\Delta s$ at $t_0$', 'd_s_t0p1': r'$\Delta s$ at $t_0+1$',
         'd_ι_t0': r'$\Delta\iota$ at $t_0$', 'd_ι_t0p1': r'$\Delta\iota$ at $t_0+1$'}


def anchorFit(x, y, anchor = 1.0, deg = 3):
    """ Deg-3 fit through every point but the anchor, evaluated at the anchor: what the CRRA points say
    the ρ=1 value should be. With four flanking points the cubic interpolates them, so the gap to the
    plotted anchor is the honest extrapolation of the CRRA series onto its own hole. """
    m = ~np.isclose(x, anchor)
    return float(np.polyval(np.polyfit(x[m], y[m], min(deg, m.sum()-1)), anchor))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--series', default = 'd_τ_t0p1')
    p.add_argument('--rule', default = 'match')
    p.add_argument('--anchor', type = float, default = 1.0)
    a = p.parse_args()

    fig, ax = plt.subplots(figsize = (7.2, 4.6))
    styles = {'production': ('tab:red', 'o', 'shipped: LOG on linear interpolants'),
              'common':     ('tab:blue', 's', 'fixed: LOG on cubic, as CRRA')}
    for mode, (c, mk, lab) in styles.items():
        path = os.path.join(OUTDIR, 'shock_{}_{}.csv'.format(a.rule, mode))
        if not os.path.exists(path):
            print('missing (skipped): ' + os.path.relpath(path, REPO))
            continue
        d = pd.read_csv(path).sort_values('ρ')
        x, y = d['ρ'].values.astype(float), d[a.series].values.astype(float)*100
        ax.plot(x, y, mk+'-', color = c, label = lab, ms = 6, lw = 1.4)
        pred = anchorFit(x, y, a.anchor)
        act = float(y[np.isclose(x, a.anchor)][0])
        ax.plot([a.anchor], [pred], 'x', color = c, ms = 9, mew = 2)
        ax.annotate('', xy = (a.anchor, act), xytext = (a.anchor, pred),
                    arrowprops = dict(arrowstyle = '<->', color = c, lw = 1.1))
        ax.text(a.anchor + 0.0015, 0.5*(act+pred), '{:+.2f} pp'.format(act-pred),
                color = c, fontsize = 9, va = 'center')
        print('{:<11} anchor={:.4f}  CRRA-fit={:.4f}  displacement={:+.4f} pp'.format(
            mode, act, pred, act-pred))

    ax.axvline(a.anchor, color = '0.75', lw = 0.8, ls = ':', zorder = 0)
    ax.set_xlabel(r'$\rho$   (the LOG solver is used at $\rho=1$ only)')
    ax.set_ylabel(LABEL.get(a.series, a.series) + '  (%)')
    ax.set_title('Universalisation response across the LOG/CRRA boundary\n'
                 '× marks where the four CRRA points say the anchor should be', fontsize = 10)
    ax.legend(fontsize = 9, frameon = False)
    ax.grid(alpha = 0.25, lw = 0.6)
    fig.tight_layout()
    os.makedirs(OUTDIR, exist_ok = True)
    stem = os.path.join(OUTDIR, '{}_vs_rho_{}'.format(a.series.replace('τ', 'tau').replace('ι', 'iota'),
                                                      a.rule))
    for ext in ('png', 'pdf'):
        fig.savefig(stem + '.' + ext, dpi = 160)
    print('written: ' + os.path.relpath(stem + '.png', REPO))


if __name__ == '__main__':
    main()
