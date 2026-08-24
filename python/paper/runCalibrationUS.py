r""" Stage (i) of the paper pipeline, US/France/UK arm: produce the calibration the rich-OECD numbers
rest on. The Argentina arm is runCalibration.py; the two are separate entry points because they delegate
to different sweep scripts, and share config.py and results/paper/.

Run:  .venv\Scripts\python.exe python\paper\runCalibrationUS.py       check what exists, solve what does not
      ... --force                                                      re-solve every point
      ... --summaryOnly                                                skip solving; just rebuild the summary
      ... --commonX                                                    also sweep the common-X variant
      ... --dry                                                        print the commands and exit

Two things happen, and only the first is expensive:

  1. The rho sweeps. Delegated to python/US/calibrateRhoGrid.py (the US, which calibrates beta and omega
     against R and tau) and python/US/calibrateRhoGridEU.py (France, the UK, and the UK regrouped at US
     percentiles, which IMPOSE the US beta at the same rho and calibrate omega alone). This file is the
     DECLARATION of what the paper calibrates, not a second implementation of it. ~4.5 min per country
     per variant; all four are resumable and return already-solved rho from their own csv, so a re-run
     with nothing to do costs seconds.

     ORDER MATTERS HERE, unlike in the Argentina arm. calibrateRhoGridEU.py reads the US sweep csv for
     beta and hbar at each rho and refuses to interpolate, so the US sweep must be complete over the
     grid before any European sweep starts. That dependency is enforced, not just documented.

  2. The endogenous-theta (app:ESC) wedge calibrations: p per (rho, spec) such that the leaded choice
     at 2020 reproduces the observed design, at config.US['esc']'s phi. Delegated to python/US/runESC.py
     (LOG, rho = 1 -- also produces the no-wedge corner row) and python/US/runESCcrra.py (CRRA, the other
     rho in the esc table grid). EXPENSIVE where missing (~25-30 min per CRRA (rho, spec): each trial
     value of p recalibrates (beta, omega) and runs 13 candidate equilibrium solves), which is why the
     check is per-(rho, spec) and the drivers merge into their csvs rather than overwriting them.

  3. The summary, results/paper/usCalibrationSummary.csv -- one row per country. Stage (iii) builds the
     calibration and household-heterogeneity tables from this file rather than from a pickled instance,
     so that stage stays a pure csv -> tex step with no model import (README.md). It is the only place
     in this arm that opens a pickle.

WHY THE SUMMARY IS NOT JUST THE SWEEP CSVS: they carry the calibrated scalars (beta, omega, lambda, X)
but not the per-type vectors eta_i, X_i, gamma_i, mu_i, nor theta -- and those are the whole of the two
household-heterogeneity tables and three rows of USUKFRCalibration. They live on the instance.
"""
import os, sys, argparse, subprocess, pickle, datetime, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

SWEEPS = ('US',) + C.US['countries'][1:] + C.US['extraSweeps']    # US first -- see the docstring


def sweepCmd(country, commonX = False, force = False):
    """ The command that produces `country`'s sweep csv, at config.US's grid and settings. """
    g, ρ = C.US['gridSettings'], C.US['ρGrid']
    step = round(ρ[1] - ρ[0], 10)
    common = ['--lo', str(min(ρ)), '--hi', str(max(ρ)), '--step', str(step),
              '--anchor', str(C.US['ρAnchor']), '--n', str(g['n']), '--ns', str(g['ns']),
              '--verify', str(g['verify']), '--verifyN', str(g['verifyN']),
              '--interpKind', g['interpKind'], '--smoothKnots', str(g['smoothKnots'])]
    if country == 'US':
        cmd = [C.PYTHON, os.path.join(C.USDIR, 'calibrateRhoGrid.py')] + common
    else:
        base = 'UK' if country in ('UK', 'UKUS') else country
        cmd = ([C.PYTHON, os.path.join(C.USDIR, 'calibrateRhoGridEU.py'), '--country', base]
               + (['--grouping', 'US'] if country == 'UKUS' else []) + common)
    return cmd + (['--commonX'] if commonX else []) + (['--force'] if force else [])


def missing(country, commonX = False):
    """ rho in the paper's grid that `country`'s sweep csv does not already carry. """
    path = C.usSweepCsv(country, commonX)
    if not os.path.exists(path):
        return list(C.US['ρGrid'])
    df = pd.read_csv(path)
    have = set(np.round(df.loc[np.isfinite(pd.to_numeric(df['residual'], errors = 'coerce')), 'ρ'], 6))
    return [ρ for ρ in C.US['ρGrid'] if round(ρ, 6) not in have]


def escMissing():
    """ The ESC wedge-calibration commands whose (rho, spec) rows results/esc does not already carry
    (converged, at config.US['esc']'s phi). One command per missing combination -- the drivers merge
    into their csvs (runESC.mergeWrite), so partial re-runs are safe. """
    esc = C.US['esc']
    specs = [esc['spec'], esc['altSpec']]
    phi = esc['phi']
    cmds = []
    pathL = os.path.join(C.ESCDIR, 'escCalibration.csv')
    haveL = set()
    if os.path.exists(pathL):
        df = pd.read_csv(pathL)
        ok = df[df['converged'].astype(bool)
                & np.isclose(pd.to_numeric(df['phi'], errors = 'coerce'), phi)]
        haveL = set(ok['spec'])
    lackL = [s for s in specs if s not in haveL]
    if lackL:
        cmds.append([C.PYTHON, os.path.join(C.USDIR, 'runESC.py'), '--stage', 'calib',
                     '--spec'] + lackL + ['--phi', str(phi)])
    pathC = os.path.join(C.ESCDIR, 'escCalibrationCRRA.csv')
    haveC = set()
    if os.path.exists(pathC):
        df = pd.read_csv(pathC)
        ok = df[df['converged'].astype(bool) & np.isclose(df['phi'], phi)]
        haveC = {(round(float(r), 6), s) for r, s in zip(ok['ρ'], ok['spec'])}
    for ρ in [r for r in esc['ρTable'] if r != C.US['ρAnchor']]:
        for s in specs:
            if (round(ρ, 6), s) not in haveC:
                cmds.append([C.PYTHON, os.path.join(C.USDIR, 'runESCcrra.py'), '--stage', 'calib',
                             '--rho', str(ρ), '--spec', s, '--phi', str(phi)])
    return cmds


def summarise(country, ρ = None, commonX = False):
    """ One country's calibration at `rho`, as one flat record.

    Unpickling needs ModelUS/ModelFR importable and the workbook path resolvable, which is why this
    chdir's into python/US exactly as the experiment scripts do. Held to this one function so nothing
    else in the pipeline inherits the requirement.
    """
    ρ = C.US['ρBaseline'] if ρ is None else ρ
    cwd = os.getcwd()
    sys.path.insert(0, C.USDIR)
    os.chdir(C.USDIR)
    try:
        with open(os.path.join(C.usInstanceDir(country, commonX), 'rho_{:.4f}.pkl'.format(ρ)), 'rb') as f:
            m = pickle.load(f)
        t0 = m.db['t'][m.db['t0']]
        atT0 = lambda k: float(m.db[k].xs(t0)) if hasattr(m.db[k], 'xs') else float(np.asarray(m.db[k])[0])
        # Vectors go through the csv as JSON, not as a python repr -- see runCalibration.summarise for
        # the numpy-2 'np.float64(...)' reading that made this a live bug rather than a hypothetical one.
        vec = lambda a: json.dumps([float(v) for v in np.asarray(a, dtype = float).ravel()])
        ηi = m.db['ηi'].xs(t0).values.astype(float)
        Xi = m.db['Xi'].xs(t0).values.astype(float)
        γi = m.db['γi'].xs(t0).values.astype(float)
        μi = m.db['μi'].xs(t0).values.astype(float)
        νt = m.db['ν'].values.astype(float)
        rec = {'country': country, 'ρ': ρ, 'commonX': bool(commonX),
               'preferences': m._calPreferences(), 't0': int(m.db['t0']), 'T': int(m.T),
               'θ': atT0('θ'), 'α': atT0('α'), 'ξ': atT0('ξ'), 'Γh': atT0('Γh'),
               'ν2020': float(νt[m.db['t0']]),
               # The population-weighted mean X_i is the row USUKFRCalibration reports as `X`, and the
               # only summary of X_i a pure scale can be matched on (python/US/shocks.shockLeisure).
               'Xbar': float((γi*Xi).sum()),
               'ηHηL': float(ηi[-1]/ηi[0]),
               'ηi': vec(ηi), 'Xi': vec(Xi), 'γi': vec(γi), 'μi': vec(μi), 'ν': vec(νt)}
    finally:
        os.chdir(cwd)
        sys.path.remove(C.USDIR)

    # beta/omega/lambda come from the sweep csv, not the pickle: the csv is the record of the calibration
    # and is what every other paper number is read against, so the table must not be able to disagree
    # with it. theta is on the instance only -- it is derived, not searched.
    df = pd.read_csv(C.usSweepCsv(country, commonX))
    row = df.loc[np.isclose(df['ρ'], ρ)]
    if row.empty:
        raise SystemExit('rho={} is not in {} -- run the sweep first.'
                         .format(ρ, os.path.relpath(C.usSweepCsv(country, commonX), C.REPO)))
    row = row.iloc[-1]
    for k in ('β', 'ω', 'λ', 'X', 'R', 'τ', 'sr', 'h', 'hbar', 'residual', 'verifyResidual',
              'hoursDrift', 'commit', 'timestamp'):
        rec[k] = row[k] if k in row.index else np.nan
    # The workweek and the tax target are inputs, and tau is a target: a mismatch here means the pickle
    # and the csv row came from different runs, or that the workbook moved under the sweep.
    cal = C.usCalendar(country)
    rec['workweek'] = cal['workweek']
    rec['τ0'] = cal['τ0']
    if not np.isclose(float(rec['τ']), cal['τ0'], atol = 1e-3):
        raise SystemExit('{}: solved tau={} but the workbook targets {}. Sweep and workbook disagree.'
                         .format(country, rec['τ'], cal['τ0']))
    rec['builtAt'] = datetime.datetime.now().replace(microsecond = 0).isoformat()
    return rec


def main():
    p = argparse.ArgumentParser(description = __doc__.split('\n')[1])
    p.add_argument('--force', action = 'store_true', help = 're-solve every point, not only the missing')
    p.add_argument('--summaryOnly', action = 'store_true', help = 'rebuild the summary from what exists')
    p.add_argument('--commonX', action = 'store_true', help = 'also sweep/summarise the common-X variant')
    p.add_argument('--dry', action = 'store_true', help = 'print the sweep commands and exit')
    p.add_argument('--rho', type = float, default = None, help = 'summarise a rho other than the baseline')
    a = p.parse_args()

    variants = [False] + ([True] if a.commonX else [])
    if a.dry:
        for cx in variants:
            for c in SWEEPS:
                print(' '.join(sweepCmd(c, cx, a.force)))
        for cmd in escMissing():
            print(' '.join(cmd))
        return

    if not a.summaryOnly:
        for cx in variants:
            for c in SWEEPS:
                todo = C.US['ρGrid'] if a.force else missing(c, cx)
                label = c + (' (common X)' if cx else '')
                if not todo:
                    print('{:<14} all {} rho already solved.'.format(label, len(C.US['ρGrid'])))
                    continue
                # The US sweep is the reference every European one reads beta and hbar from, and
                # calibrateRhoGridEU refuses to interpolate it -- so an incomplete US sweep must stop the
                # run here rather than fail per-point halfway through a march.
                if c != 'US' and missing('US', cx):
                    raise SystemExit('The US sweep is incomplete at {}; France/UK impose its beta and '
                                     'cannot be swept first.'.format(missing('US', cx)))
                print('\n{}: calibrating {} point(s)'.format(label, len(todo)))
                cmd = sweepCmd(c, cx, a.force)
                print('  ' + ' '.join(cmd))
                r = subprocess.run(cmd, cwd = C.REPO)
                if r.returncode:
                    raise SystemExit('sweep for {} exited {}'.format(label, r.returncode))

        # --- the ESC wedge calibrations (app:ESC). Per-(rho, spec) check, so a complete results/esc
        # costs nothing here; a missing CRRA combination costs ~25-30 min.
        cmds = escMissing()
        if not cmds:
            print('ESC wedge:      all (rho, spec) combinations already calibrated.')
        for cmd in cmds:
            print('\nESC wedge: ' + ' '.join(cmd))
            r = subprocess.run(cmd, cwd = C.REPO)
            if r.returncode:
                raise SystemExit('ESC calibration exited {}'.format(r.returncode))

    recs = [summarise(c, a.rho, cx) for cx in variants for c in SWEEPS]
    os.makedirs(C.PAPERDIR, exist_ok = True)
    out = os.path.join(C.PAPERDIR, 'usCalibrationSummary.csv')
    pd.DataFrame(recs).to_csv(out, index = False)
    print('\nwritten: ' + os.path.relpath(out, C.REPO))
    print('  {:<8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}'.format(
        'country', 'θ', 'ω', 'β', 'Xbar', 'ηH/ηL', 'ν2020'))
    for r in recs:
        if r['commonX']:
            continue
        print('  {:<8} {:8.4f} {:8.4f} {:8.4f} {:8.2f} {:8.3f} {:8.3f}'.format(
            r['country'], r['θ'], r['ω'], r['β'], r['Xbar'], r['ηHηL'], r['ν2020']))


if __name__ == '__main__':
    main()
