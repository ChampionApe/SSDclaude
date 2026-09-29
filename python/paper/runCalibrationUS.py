r""" Stage (i) of the paper pipeline, US/France/UK arm: produce the calibration the rich-OECD numbers
rest on. The Argentina arm is runCalibration.py; the two are separate entry points because they delegate
to different sweep scripts, and share config.py and results/paper/.

Run:  .venv\Scripts\python.exe python\paper\runCalibrationUS.py       the MAIN part: check what exists, solve what does not
      ... --prepub                                                     the PRE-PUBLICATION part only (the exact CRRA wedge, the phi runs)
      ... --all                                                        both parts
      ... --force                                                      re-solve every point
      ... --summaryOnly                                                skip solving; just rebuild the summary
      ... --commonX                                                    also sweep the common-X variant
      ... --dry                                                        print the commands and exit

TWO PARTS, as runShocksUS.py: the main part is the sweeps, the LOG wedge calibration and the summary; the
pre-publication part is the EXACT CRRA wedge calibration (runESCcrra.py --exact, the published method,
~1.2 h per rho from scratch) and the phi-robustness wedge calibrations under LOG (the phi footnote).

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

  2. The endogenous-theta (sec:esc) cost calibrations: the cost parameter per (rho, spec) such that the
     leaded choice at 2020 reproduces the observed design, at config.US['esc']'s phi. Delegated to
     python/US/runESC.py (LOG, rho = 1 -- the paper's spec AND the comparison spec, also the no-wedge
     corner row) and python/US/runESCcrra.py (CRRA, the other rho in the esc table grid, the paper's spec
     only, with config.escBracket's scan bracket per rho). EXPENSIVE where missing (~45 min per CRRA
     (rho, spec): each trial value recalibrates (beta, omega) and runs the exact recursion), which is why
     the check is per-(rho, spec) and the drivers merge into their csvs rather than overwriting them.

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
        # A regrouped country is its workbook plus the grouping suffix: 'UKUS', 'FRUK' (config.usCalendar).
        base, grouping = country[:2], country[2:]
        cmd = ([C.PYTHON, os.path.join(C.USDIR, 'calibrateRhoGridEU.py'), '--country', base]
               + (['--grouping', grouping] if grouping else []) + common)
    return cmd + (['--commonX'] if commonX else []) + (['--force'] if force else [])


def missing(country, commonX = False):
    """ rho in the paper's grid that `country`'s sweep csv does not already carry. """
    path = C.usSweepCsv(country, commonX)
    if not os.path.exists(path):
        return list(C.US['ρGrid'])
    df = pd.read_csv(path)
    have = set(np.round(df.loc[np.isfinite(pd.to_numeric(df['residual'], errors = 'coerce')), 'ρ'], 6))
    return [ρ for ρ in C.US['ρGrid'] if round(ρ, 6) not in have]


PHIROBUST = [0.25, 0.75]      # the phi footnote in sec:esc: LOG wedge calibrations at phi != esc['phi']


def _escLogRows(phis):
    """ {(spec, phi)} of converged LOG wedge calibrations on file, under the headline variant. """
    path = os.path.join(C.ESCDIR, 'escCalibration.csv')
    if not os.path.exists(path):
        return set()
    df = pd.read_csv(path)
    ok = df[df['converged'].astype(bool)]
    if 'commonX' in ok.columns:
        ok = ok[ok['commonX'].astype(bool) == bool(C.US['commonX'])]
    return {(s, round(float(p), 6)) for s, p in zip(ok['spec'], pd.to_numeric(ok['phi'], errors = 'coerce'))
            if p == p}


def escMissing(part = 'main', force = False, strict = True):
    """ The ESC cost-calibration commands whose rows results/esc does not already carry (converged, at
    config.US['esc']'s phi, headline variant). One command per missing combination -- the drivers merge
    into their csvs (runESC.mergeWrite), so partial re-runs are safe.

    'main': the LOG calibrations at esc['phi'] under the paper's spec and the comparison spec (about 80 s
    each; also the no-wedge row). 'prepub': the EXACT CRRA calibrations at every rho the ESC tables print
    under the paper's spec (method = 'exact' rows -- the path iteration's rows in the same csv do not
    count), one command per rho with its own scan bracket from config.escBracket, and the LOG
    calibrations at PHIROBUST. `force` lists them all. A placeholder bracket raises unless `strict` is
    False (the --dry listing), which prints it as `--bracket <unset> <unset>` instead. """
    esc = C.US['esc']
    spec, phi = esc['spec'], esc['phi']
    specsL = [spec] + ([esc['comparisonSpec']] if esc.get('comparisonSpec') else [])
    # The ESC leg runs under the headline calibration variant only -- see paper/runShocksUS.ESCVARIANT.
    variant = ['--commonX'] if C.US['commonX'] else []
    cmds = []
    haveL = set() if force else _escLogRows([phi] + PHIROBUST)
    lackL = [s for s in specsL if (s, round(phi, 6)) not in haveL]
    if part in ('main', 'all') and lackL:
        cmds.append([C.PYTHON, os.path.join(C.USDIR, 'runESC.py'), '--stage', 'calib',
                     '--spec'] + lackL + ['--phi', str(phi)] + variant)
    if part in ('prepub', 'all'):
        pathC = os.path.join(C.ESCDIR, 'escCalibrationCRRA.csv')
        haveC = set()
        if os.path.exists(pathC) and not force:
            df = pd.read_csv(pathC)
            if 'method' not in df.columns:
                df['method'] = 'path'
            ok = df[df['converged'].astype(bool) & np.isclose(df['phi'], phi)
                    & (df['method'].fillna('path') == 'exact')]
            if 'commonX' in ok.columns:
                ok = ok[ok['commonX'].astype(bool) == bool(C.US['commonX'])]
            haveC = {(round(float(r), 6), s) for r, s in zip(ok['ρ'], ok['spec'])}
        lackρ = [ρ for ρ in esc['ρTable'] if ρ != C.US['ρAnchor'] and (round(ρ, 6), spec) not in haveC]
        exact = [C.PYTHON, os.path.join(C.USDIR, 'runESCcrra.py'), '--exact', '--stage', 'calib']
        opts = ['--spec', spec, '--phi', str(phi), '--ns', str(esc['ns2D']),
                '--nsScan', str(esc['nsScan']), '--nCand2D', str(esc['nCand2D'])] + variant
        # A rho with its own bracket gets its own command (the bracket is one pair); the rest share one
        # command and runESCcrra.py's own default scan for the spec.
        brackets = {}
        for ρ in lackρ:
            try:
                brackets[ρ] = C.escBracket(ρ, spec)
            except ValueError:
                if strict:
                    raise
                brackets[ρ] = ('<unset>', '<unset>')
        shared = [ρ for ρ in lackρ if brackets[ρ] is None]
        if shared:
            cmds.append(exact + ['--rho'] + [str(r) for r in shared] + opts)
        for ρ in lackρ:
            if brackets[ρ] is not None:
                cmds.append(exact + ['--rho', str(ρ), '--bracket'] + [str(b) for b in brackets[ρ]] + opts)
        # The UK's own exact CRRA cost (appendix app:UKUS), one command per missing rho, its bracket and
        # scan grid from esc['uk'].
        uk = esc['uk']
        pathUK = os.path.join(C.ESCDIR, 'escCalibrationCRRAUK.csv')
        haveUK = set()
        if os.path.exists(pathUK) and not force:
            df = pd.read_csv(pathUK)
            ok = df[df['converged'].astype(bool) & (df['method'] == 'exact') & (df['spec'] == spec)
                    & (df['commonX'].astype(bool) == bool(C.US['commonX']))]
            haveUK = {round(float(r), 6) for r in ok['ρ']}
        for ρ in esc['ρTable']:
            if ρ == C.US['ρAnchor'] or round(ρ, 6) in haveUK:
                continue
            cmds.append([C.PYTHON, os.path.join(C.USDIR, 'runESCcrra.py'), '--exact', '--host', 'UK',
                         '--stage', 'calib', '--rho', str(ρ), '--bracket']
                        + [str(b) for b in uk['bracket'][ρ]]
                        + ['--nScan', str(uk['nScan']), '--spec', spec, '--phi', str(phi),
                           '--ns', str(esc['ns2D']), '--nsScan', str(uk['nsScan'][ρ]),
                           '--nCand2D', str(esc['nCand2D'])] + variant)
        # phi is a parameter of f only under 'scale'/'flat'; under 'size' it is a dummy key and a
        # run at another phi would reproduce the esc['phi'] calibration under a different key.
        lackφ = [p for p in PHIROBUST if spec in ('scale', 'flat') and (spec, round(p, 6)) not in haveL]
        if lackφ:
            cmds.append([C.PYTHON, os.path.join(C.USDIR, 'runESC.py'), '--stage', 'calib',
                         '--spec', spec, '--phi'] + [str(p) for p in lackφ] + variant)
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
    p.add_argument('--commonX', action = 'store_true',
                   help = 'also SWEEP the common-X variant. The summary always covers both variants -- '
                          'the paper builds a headline table and its twin from them and summarising is '
                          'only an unpickle -- so this flag is about the expensive step alone.')
    p.add_argument('--dry', action = 'store_true', help = 'print the sweep commands and exit')
    p.add_argument('--rho', type = float, default = None, help = 'summarise a rho other than the baseline')
    p.add_argument('--prepub', action = 'store_true',
                   help = 'the pre-publication part only: the exact CRRA wedge and the phi runs, no sweeps')
    p.add_argument('--all', dest = 'all_', action = 'store_true', help = 'both parts')
    a = p.parse_args()
    part = 'all' if a.all_ else ('prepub' if a.prepub else 'main')

    variants = [False] + ([True] if a.commonX else [])
    if a.dry:
        if part != 'prepub':
            for cx in variants:
                for c in SWEEPS:
                    print(' '.join(sweepCmd(c, cx, a.force)))
        for cmd in escMissing(part, a.force, strict = False):
            print(' '.join(cmd))
        return

    if not a.summaryOnly and part != 'prepub':
        for cx in variants:
            for c in SWEEPS:
                todo = C.US['ρGrid'] if a.force else missing(c, cx)
                label = c + (' (common X)' if cx else '')
                if not todo:
                    print('{:<14} all {} rho already solved.'.format(label, len(C.US['ρGrid'])))
                    continue
                if not C.usHasSheets(c):
                    print('{:<14} SKIPPED: the workbook has no calibration sheet for this regrouping yet.'
                          .format(label))
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

    if not a.summaryOnly:
        # --- the ESC cost calibrations (sec:esc). Per-(rho, spec, method) check, so a complete
        # results/esc costs nothing here; a missing exact CRRA rho costs ~45 min (pre-publication part).
        # A placeholder bracket (config.escBracket) raises here, before any command runs.
        cmds = escMissing(part, a.force)
        if not cmds:
            print('ESC cost ({}): every combination already calibrated.'.format(part))
        for cmd in cmds:
            print('\nESC cost: ' + ' '.join(cmd))
            r = subprocess.run(cmd, cwd = C.REPO)
            if r.returncode:
                raise SystemExit('ESC calibration exited {}'.format(r.returncode))

    # Both variants, always: the paper's headline outputs read one and their robustness twins the
    # other, so a summary carrying only one of them blocks half the build (config.US['commonX']).
    # A regrouping whose sweep does not exist yet (no workbook sheets) is left out of the summary rather
    # than failing it; its tables report MissingInput in stage (iii).
    recs = [summarise(c, a.rho, cx) for cx in (False, True) for c in SWEEPS
            if os.path.exists(C.usSweepCsv(c, cx))]
    os.makedirs(C.PAPERDIR, exist_ok = True)
    out = os.path.join(C.PAPERDIR, 'usCalibrationSummary.csv')
    pd.DataFrame(recs).to_csv(out, index = False)
    print('\nwritten: ' + os.path.relpath(out, C.REPO))
    # Printed for the variant the paper leads with. beta, omega and theta are common to both by block
    # recursivity; Xbar and the eta ratio are not, which is the whole content of the variant.
    print('  the {} calibration (config.US[\'commonX\'] = {})'.format(
        'common-X' if C.US['commonX'] else 'vector-X', C.US['commonX']))
    print('  {:<8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}'.format(
        'country', 'θ', 'ω', 'β', 'Xbar', 'ηH/ηL', 'ν2020'))
    for r in recs:
        if bool(r['commonX']) != bool(C.US['commonX']):
            continue
        print('  {:<8} {:8.4f} {:8.4f} {:8.4f} {:8.2f} {:8.3f} {:8.3f}'.format(
            r['country'], r['θ'], r['ω'], r['β'], r['Xbar'], r['ηHηL'], r['ν2020']))


if __name__ == '__main__':
    main()
