r""" Plot a response series from the universalisation shock (shockUniversal.py) against rho, at a chosen
number of periods after t0. Not a test.

Run:  .venv\Scripts\python.exe python\InformalSavings\plotUniversalShock.py [--series d_τ] [--rule match]
      ... --period 1        one period after the reform, instead of the impact period (default 0)
"""
import os, sys, argparse, glob, re
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from gridsearch.testing import utf8Stdout

utf8Stdout()    # --help and the duplicate-ρ error carry Greek; see gridsearch/testing.py

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
INDIR = os.path.join(REPO, 'results', 'shocks')
OUTDIR = INDIR

LABELS = {'d_τ': 'Δτ (change in the tax rate)', 'd_s': 'Δs', 'd_ι': 'Δι',
          'd_c10': 'Δc¹,⁰', 'd_c20': 'Δc²,⁰'}


def loadAtPeriod(rule, period):
    """ {ρ: row at t0+period} across results/shocks/universal_{rule}_rho<number>.csv. Rows are already
    indexed on the model's own t (b.index[:len(shock)] in shockUniversal.py), t0 first, so this is a plain
    positional offset -- iloc[period], not a lookup by label.

    The filename must match the rho pattern EXACTLY, and duplicate rho is a hard error rather than a
    silently doubled point. A glob of 'rho*' also matches anything appended after the number -- a backup,
    a variant, a dated copy -- and since rho is then read from the file's own column the extra row looks
    entirely legitimate on the plot. That is not hypothetical: a 'universal_match_rho1.0000_preInterpFix'
    backup left in this directory put the pre-fix and post-fix anchors on one figure as two points at
    rho=1. Keep superseded runs in a subdirectory (preInterpFix/), not beside the live ones. """
    pattern = re.compile(r'universal_{}_rho-?\d+\.\d+\.csv$'.format(re.escape(rule)))
    rows, seen = [], {}
    for f in sorted(glob.glob(os.path.join(INDIR, 'universal_{}_rho*.csv'.format(rule)))):
        if not pattern.fullmatch(os.path.basename(f)):
            print('  skipped (not a plain rho file): ' + os.path.basename(f))
            continue
        df = pd.read_csv(f, index_col = 0)
        if period < len(df):
            ρ = round(float(df['ρ'].iloc[0]), 6)
            if ρ in seen:
                raise ValueError('two files give rho={}: {} and {}. Move the superseded one out of {}.'
                                 .format(ρ, seen[ρ], os.path.basename(f), INDIR))
            seen[ρ] = os.path.basename(f)
            rows.append(df.iloc[period])
    return pd.DataFrame(rows).sort_values('ρ').reset_index(drop = True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--series', default = 'd_τ')
    p.add_argument('--rule', default = 'match', choices = ('match', 'flat'))
    p.add_argument('--period', type = int, default = 0, help = 'periods after t0; 0 = impact period')
    p.add_argument('--out', default = None, help = 'basename (no extension); default from --series/--rule')
    a = p.parse_args()

    df = loadAtPeriod(a.rule, a.period)
    if a.series not in df:
        sys.exit('no column {!r} in the loaded rows; have {}'.format(a.series, list(df.columns)))

    fig, ax = plt.subplots(figsize = (6.5, 4.2), constrained_layout = True)
    ax.plot(df['ρ'], 100*df[a.series], color = '#2a78d6', linewidth = 2, marker = 'o', markersize = 5,
             solid_capstyle = 'round')
    ax.axhline(0, color = '#e1e0d9', linewidth = 1, zorder = 0)
    ax.set_xlabel('ρ (CRRA curvature)', color = '#52514e')
    ax.set_ylabel(LABELS.get(a.series, a.series) + '  (%)', color = '#52514e')
    when = 'impact period (t₀)' if a.period == 0 else 't₀+{}'.format(a.period)
    ax.set_title('Universal pension reform ({} rule)\nresponse at {}'.format(a.rule, when),
                 color = '#0b0b0b', fontsize = 11, loc = 'left')
    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)
    for spine in ('left', 'bottom'):
        ax.spines[spine].set_color('#898781')
    ax.tick_params(colors = '#898781')
    ax.grid(True, color = '#e1e0d9', linewidth = 0.8)
    ax.set_axisbelow(True)

    base = a.out or 'delta_{}_vs_rho_{}_t{}'.format(
        a.series.replace('d_', '').replace('τ', 'tau').replace('ι', 'iota'), a.rule, a.period)
    for ext in ('png', 'pdf'):
        path = os.path.join(OUTDIR, base + '.' + ext)
        fig.savefig(path, dpi = 300)
        print('written: ' + os.path.relpath(path, REPO))


if __name__ == '__main__':
    main()
