r""" Measure where the state grids should sit, across solved calibrations.

Run:  .venv\Scripts\python.exe python\InformalSavings\measureGrids.py [--rho 0.5 0.7875 1.5 2.0] [--log]

Feeds the OFFLINE retune of the grid rule (policy.py's grid-placement diagnostics say why it must stay
offline). Answers the two questions a single-point measurement cannot:

  1. How much does the reachable box move with rho? If it barely moves, measuring once -- on the cheap LOG
     calibration at the start of any workflow -- is enough to set constants for a whole sweep.
  2. Does the LOG box BOUND the CRRA one? The current lower pad (0.25) is documented as right for LOG,
     whose solved iota_t undershoots its own steady-state minimum. If LOG's box is the wider of the two,
     LOG-derived constants are conservative for CRRA -- safe, but leaving resolution unused.

Also prints, per point, what the CURRENT rule produces against what the box implies, which is the table
the new constants get read off.
"""
import os, sys, argparse, pickle, time
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
os.chdir(HERE)

CSV    = os.path.join(REPO, 'results', 'calibration', 'informalSavings_rhoGrid.csv')
PKLDIR = os.path.join(REPO, 'results', 'calibration', 'instances')
GRIDSETTINGS = {'nι': 45, 'ns': 45, 'interpKind': 'cubic'}
# Candidate anchors for the s rule: s*(tau) at these tau. tau0=0.125 is the calibration's own target, so
# it is the natural candidate -- but it is a candidate, not the answer, which is why several are tried.
ANCHOR_TAUS = (0.0, 0.05, 0.125, 0.2, 0.3, 0.4)


def legacyGrids(m, policy, θ, ε, t):
    """ The grid rule as it stood before the 2026-08-19 retune, installed through initGS' override slots
    so the two rules can be compared on one code path. l_ι = max(δι, 0.25·min ι*), u_ι = min(1.25·max ι*,
    2.0); s linear on [1e-4, 1.25·s*(0)]. """
    settings = policy.GS['PEE']['gridSettings']
    τGrid = policy.GS['PEE']['solGrids']['τ']
    if isinstance(policy, type(m.CRRA)) and hasattr(policy, 'defaultSGrid'):
        ι = []
        for τ in np.linspace(τGrid[0], τGrid[-1], 21):
            try:
                ss = m.steadyState_CRRA_solve(τ, θ, t = t)
            except (ValueError, RuntimeError):
                continue
            ι.append(m.B.s0_s(m.B.B0SteadyState(ss['Γs'], τ, θ, t), ss['Θs'], τ, ε, t))
        ι = np.asarray(ι)
        sMax = m.steadyState_CRRA_solve(0.0, θ, t = t)['s']
        sGrid = np.linspace(1e-4, 1.25*sMax, settings['ns'])
    else:
        Θs = m.steadyState_LOG_solve(τGrid, θ, t = t)['Θs']
        ι = m.B.s0_s(m.B.get('β0', t), Θs, τGrid, ε, t)
        sGrid = None
    lo = max(settings['δι'], 0.25*np.min(ι))
    hi = min(1.25*np.max(ι), 2.0)
    return np.geomspace(lo, hi, settings['nι']), sGrid


def measure(ρ, preferences, legacy = False):
    """ Solve at a pickled calibration and report the reachable box, the grids, and the occupancy. """
    with open(os.path.join(PKLDIR, 'rho_{:.4f}.pkl'.format(ρ)), 'rb') as f:
        m = pickle.load(f)
    policy = getattr(m, preferences)
    if preferences == 'CRRA':
        policy.initGS(GRIDSETTINGS)
    else:
        policy.initGS()
    if legacy:
        ιG, sG = legacyGrids(m, policy, m.db['θ'].values[-1], m.db['eps'].values[-1], m.db['t'][-1])
        policy.GS['PEE']['stateGrids']['ι_'] = ιG
        if sG is not None:
            policy.GS['PEE']['stateGrids']['s_'] = sG
    t0 = time.time()
    pee = getattr(m, f'solvePEE_{preferences}')()
    rep = pee['report']
    seed = {}
    for name, key in (('ι', 'ι'), ('s', 's_')):
        if key in rep:
            v = np.asarray(rep[key], dtype = float)
            v = v[np.isfinite(v) & (v > 0)]
            if v.size:
                seed[name] = (0.5*v.min(), 2.0*v.max())
    box = policy.reachableBox(pee['sols'], seed = seed)
    occ = policy.gridOccupancy(pee['sols'], box)
    print('\nrho={} ({}, {:.0f}s)'.format(ρ, preferences, time.time()-t0))
    for name, o in sorted(occ.items()):
        print('  {:<2} grid [{:.5f}, {:.5f}]  box [{:.5f}, {:.5f}]  -> {} of {} nodes ({:.1%})'.format(
            name, o['grid'][0], o['grid'][1], o['box'][0], o['box'][1], o['nodes'], o['n'], o['frac']))
    # The risk the reachable box CANNOT see: raising l_ι shrinks the candidate range 𝒮_0', so τ-nodes
    # whose implied ι_t falls below it become infeasible and the selection is pinned to the feasibility
    # edge instead of the first order condition. This is the documented failure of the doc's original 0.75
    # pad (README, defaultIotaGrid) and is what decides whether the retune went too far.
    feas = atB = tot = oog = 0
    for t, d in sorted(pee['sols'].items()):
        if 'feasible' in d:
            f = np.asarray(d['feasible'], dtype = bool)
            feas += int(f.sum()); tot += int(f.size)
        if 'atBound' in d:
            atB += int(np.asarray(d['atBound'], dtype = bool).sum())
        if 'outOfGrid' in d:
            oog += int(np.nansum(np.asarray(d['outOfGrid'], dtype = bool)))
    print('     feasible {}/{} ({:.1%})   atBound {}   outOfGrid {}'.format(
        feas, tot, feas/tot if tot else np.nan, atB, oog))
    rec = {'feasible': feas, 'feasTot': tot, 'atBound': atB, 'outOfGrid': oog,
           'ρ': ρ, 'preferences': preferences,
           **{f'{k}_{a}': v for k, o in occ.items()
              for a, v in (('gridLo', o['grid'][0]), ('gridHi', o['grid'][1]),
                           ('boxLo', o['box'][0]), ('boxHi', o['box'][1]),
                           ('nodes', o['nodes']), ('frac', o['frac']))}}
    # Candidate anchors for the s rule. s*(0) is what the rule uses today and is known to drift against
    # the box (2.2x across rho); these are the alternatives, evaluated at the same solved parameters so
    # the ratio spread is the whole comparison.
    if preferences == 'CRRA':
        tT = m.db['t'][-1]
        θ = m.db['θ'].values
        for τa in ANCHOR_TAUS:
            try:
                rec[f'sStar_{τa:.3f}'] = float(m.steadyState_CRRA_solve(τa, θ[-1], t = tT)['s'])
            except Exception:
                rec[f'sStar_{τa:.3f}'] = np.nan
    return rec


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--rho', type = float, nargs = '+', default = [0.5, 0.7875, 1.2, 2.0])
    p.add_argument('--log', action = 'store_true', help = 'also measure the LOG solver at rho=1')
    p.add_argument('--legacy', action = 'store_true', help = 'use the pre-2026-08-19 grid rule instead')
    a = p.parse_args()
    rows = [measure(ρ, 'CRRA', a.legacy) for ρ in a.rho]
    if a.log:
        rows.append(measure(1.0, 'LOG', a.legacy))
    df = pd.DataFrame(rows)
    print('\n' + '='*100)
    print(df.to_string(index = False))
    # Which anchor makes the s rule stable: the winner is the tau whose boxHi/s*(tau) varies least across
    # rho, since that is the ratio a single constant has to stand in for.
    cols = [c for c in df.columns if c.startswith('sStar_')]
    if cols and 's_boxHi' in df:
        c = df[df['preferences'] == 'CRRA'].dropna(subset = ['s_boxHi'])
        print('\ns-anchor comparison (spread of the ratio across rho -- SMALLER IS BETTER):')
        print('  {:<12} {:>12} {:>12} {:>12}'.format('anchor', 'boxHi/anchor', 'spread', 'boxLo/anchor'))
        best = None
        for col in cols:
            r = (c['s_boxHi']/c[col]).values
            rl = (c['s_boxLo']/c[col]).values
            if not np.all(np.isfinite(r)):
                continue
            spread = r.max()/r.min()-1
            print('  s*({:<8}) {:>12} {:>11.1%} {:>12}'.format(col.split('_')[1],
                  '{:.3f}-{:.3f}'.format(r.min(), r.max()), spread,
                  '{:.3f}-{:.3f}'.format(rl.min(), rl.max())))
            if best is None or spread < best[1]:
                best = (col, spread, r, rl)
        if best:
            print('  -> best anchor: s*({}) with {:.1%} spread; '
                  'pads would be ~{:.2f} (hi) and ~{:.2f} (lo) before margin'.format(
                      best[0].split('_')[1], best[1], best[2].max(), best[3].min()))

    for name in ('ι', 's'):
        lo, hi = f'{name}_boxLo', f'{name}_boxHi'
        if lo in df:
            d = df.dropna(subset = [lo])
            c = d[d['preferences'] == 'CRRA']
            print('\n{}: CRRA box lo in [{:.5f}, {:.5f}] (spread {:.1%}), hi in [{:.5f}, {:.5f}] '
                  '(spread {:.1%})'.format(name, c[lo].min(), c[lo].max(), c[lo].max()/c[lo].min()-1,
                                           c[hi].min(), c[hi].max(), c[hi].max()/c[hi].min()-1))
            g = d[d['preferences'] == 'LOG']
            if len(g):
                print('   LOG box [{:.5f}, {:.5f}] -- {} the CRRA range'.format(
                    g[lo].iloc[0], g[hi].iloc[0],
                    'BOUNDS' if (g[lo].iloc[0] <= c[lo].min() and g[hi].iloc[0] >= c[hi].max())
                    else 'does NOT bound'))
