r""" Calibrate the informalSavings model across a grid of CRRA parameter values.

Run:  .venv\Scripts\python.exe python\InformalSavings\calibrateRhoGrid.py [options]
      ... --lo 0.5 --hi 2.0 --step 0.1        the default sweep
      ... --lo 0.5 --hi 2.0 --step 0.25       a coarse pass first
      ... --force                             re-solve points already in the csv

The march is anchored at rho=1, where the LOG solver applies and no warm start is needed, and walks
outward in both directions (gridsearch.continuation.marchGrid). Each calibration costs ~26 PEE solves at
~21 s each, so the sweep is measured in hours and is built to survive being interrupted:

  * results/calibration/informalSavings_rhoGrid.csv is the record, rewritten after *every* point. A run
    started over reads it back, and any rho already present is returned from it without re-solving --
    which also means those points still seed the extrapolation, so a resumed march is no worse warm-started
    than an uninterrupted one.
  * results/calibration/instances/*.pkl is a cache, not the record: one pickled model per point (~62 kB),
    holding the converged db. Reconstructing the same thing from the csv costs one _calSetPars and one
    solve, so nothing is lost if these are deleted -- they exist to make a solved point cheap to open
    interactively. Full solutions (policy functions) are deliberately NOT stored: CRRA's are not
    pickleable at all (gridsearch.interp's griddedInterp2D returns a closure) and they regenerate in ~21 s.

The inner grid defaults to nι=ns=45, which is NOT the PEE solve's default and must not be reduced -- see
README, "The CRRA calibration needs a finer inner grid than the CRRA solve". Whether 45 is still enough
far from rho=1 has never been tested, which is what --verify exists to answer: it re-evaluates the outer
residual at the converged parameters on a finer grid and stores it beside the point. A point whose
verifyResidual is not small is converged but not resolved, and should not be read as a result.
"""
import os, sys, argparse, pickle, subprocess, datetime
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))

# A point takes minutes and the sweep takes hours, so progress has to appear as it happens rather than
# when the process exits. Whenever stdout is a pipe or a log file it is block-buffered by default, which
# hides the entire run; set here rather than relying on the caller remembering `python -u`.
# encoding too, not only buffering: every progress line carries Greek parameter names, and when
# stdout is a pipe or a log file it defaults to the ANSI codepage on Windows -- which raises
# UnicodeEncodeError on the first point and takes the whole march down with it.
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)                                        # test.py reads data/ relative to its own location

import test as testmod
from model import ModelInformalSavings
from gridsearch import continuation

OUTDIR = os.path.join(REPO, 'results', 'calibration')
CSV    = os.path.join(OUTDIR, 'informalSavings_rhoGrid.csv')
PKLDIR = os.path.join(OUTDIR, 'instances')

# Ordered so the csv reads as: what was solved, what it cost, whether to believe it, then the answer.
COLUMNS = ['ρ', 'preferences', 'requested', 'residual', 'verifyResidual', 'occupancyι', 'occupancys',
           'β', 'ω', 'η0', 'X0',
           'KY', 'sr', 'τ', 'ι', 'nRoots', 'nfev', 'time', 'nι', 'ns', 'nτ', 'x0', 'x1', 'x2', 'x3',
           'commit', 'timestamp']
# occupancy* sit beside verifyResidual because they answer the same kind of question and neither is
# asserted: verifyResidual catches a point that is converged but not resolved, occupancy catches a state
# grid whose nodes are mostly somewhere the dynamics never go. A grid that is too NARROW announces itself
# (states outside it are reported infeasible, never clipped); one that is too WIDE is silent, and this is
# the column that makes it visible. toRow reindexes to this list, so a record key absent here is dropped.


def gitCommit():
    """ Short hash of the code that produced a row -- the sweep outlives several edits of the solver. """
    try:
        return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd = REPO, capture_output = True,
                              text = True, timeout = 10).stdout.strip() or 'unknown'
    except Exception:
        return 'unknown'


def toRow(rec, requested, commit):
    """ calibratePoint's record -> one flat csv row. """
    g = rec['gridSettings']
    row = {k: rec.get(k) for k in ('ρ', 'preferences', 'residual', 'verifyResidual', 'occupancyι',
                                   'occupancys', 'β', 'ω', 'η0', 'X0', 'KY', 'sr', 'τ', 'ι', 'nRoots',
                                   'nfev', 'time')}
    row |= {'requested': requested, 'nι': g.get('nι'), 'ns': g.get('ns'), 'nτ': g.get('n'),
            'commit': commit, 'timestamp': datetime.datetime.now().isoformat(timespec = 'seconds')}
    row |= {f'x{i}': v for i, v in enumerate(rec['x'])}
    return row


def readDone(path):
    """ {rho: x} for the points already solved, as the resume cache. Keyed on the rounded value so a
    grid rebuilt from the same --lo/--step matches it exactly rather than by floating-point luck. """
    if not os.path.exists(path):
        return {}, pd.DataFrame(columns = COLUMNS)
    df = pd.read_csv(path)
    done = {round(float(r['ρ']), 6): np.array([r[f'x{i}'] for i in range(4)], dtype = float)
            for _, r in df.iterrows() if np.isfinite(r.get('residual', np.nan))}
    return done, df


def main():
    p = argparse.ArgumentParser(description = 'Calibrate informalSavings across a grid of rho.')
    p.add_argument('--lo', type = float, default = 0.5)
    p.add_argument('--hi', type = float, default = 2.0)
    p.add_argument('--step', type = float, default = 0.1)
    p.add_argument('--anchor', type = float, default = 1.0)
    p.add_argument('--nι', '--niota', dest = 'nι', type = int, default = 45)
    p.add_argument('--ns', type = int, default = 45)
    p.add_argument('--verify', type = int, default = 60, help = 'refined nι=ns for the resolution check; 0 to skip')
    p.add_argument('--verifyLOG', type = int, default = 75,
                   help = "refined nι for the LOG anchor's resolution check (its working nι is 50)")
    # Default 4, matching policy.py's own since 2026-08-19. It must NOT be None here: initGS merges this
    # dict over the class defaults, so a None would explicitly select the adaptive smoother rather than
    # request the default -- the exact inversion the flip introduced. 0 is the way back to adaptive.
    p.add_argument('--smoothKnots', type = int, default = 4,
                   help = 'fixed-knot policy smoother: interior knot every m-th node. 0 selects the '
                          'adaptive smoother, which re-chooses its knot COUNT from the data and makes the '
                          'outer residual discontinuous -- only for reproducing pre-2026-08-19 results.')
    p.add_argument('--interpKind', default = 'cubic', choices = ('linear', 'cubic', 'pchip'),
                   help = "continuation interpolant, BOTH solvers; 'linear' does not converge away "
                          "from rho=1 under CRRA, and does not converge in nι at all under LOG")
    p.add_argument('--degree', type = int, default = 1, help = 'extrapolation degree for the warm start')
    p.add_argument('--maxHalvings', type = int, default = 2)
    # Now that interpKind is shared, crossing rho=1 changes the solver, the state dimension and nι
    # (50->45) -- but no longer the interpolant, which was carrying ~98% of the jump. --common
    # additionally matches the grid SIZES. That is a diagnostic, not a fix: nι accounts for ~2% of the
    # boundary gap and the LOG answer is already converged in it at 'cubic' (flat to 1e-5 across
    # nι in {45,60,90}). Use it to isolate the two recursions from every setting at once.
    p.add_argument('--common', action = 'store_true',
                   help = 'also give the LOG anchor the CRRA grid SIZES, so nothing but the recursion '
                          'changes at rho=1 (diagnostic; interpKind is already shared)')
    p.add_argument('--force', action = 'store_true', help = 're-solve points already present in the csv')
    p.add_argument('--out', default = CSV)
    # A sweep written to a non-default --out must also get its own --pkldir, or it silently overwrites the
    # canonical sweep's instances wherever the two grids share a value (the filename is the rho alone).
    # That matters even when the settings agree: the code is bitwise reproducible within a process but not
    # across them, so the overwrite is not a no-op and shockUniversal.py reads these by name.
    p.add_argument('--pkldir', default = PKLDIR, help = 'where the per-point pickled instances go')
    args = p.parse_args()

    pkldir = args.pkldir
    os.makedirs(OUTDIR, exist_ok = True)
    os.makedirs(pkldir, exist_ok = True)
    grid = np.round(np.arange(args.lo, args.hi + 0.5*args.step, args.step), 6)
    commit = gitCommit()
    # Keyed by solver: the grid sizes and interpKind are the CRRA calibration's, and the LOG anchor keeps
    # its own defaults (nι=50, 'linear') rather than being silently moved onto them. interpKind='cubic' is
    # required rather than preferred -- at 'linear' the CRRA calibration away from rho=1 does not converge
    # and its answer is not grid-converged; see the module docstring of test_calibrationGrid.py.
    #
    # smoothKnots is the one setting BOTH solvers get. It is not a resolution choice but a well-posedness
    # one -- the adaptive spline's knot count is chosen from the data and flips discontinuously as a
    # parameter moves, putting jumps in the outer residual (README, "The policy smoother's knots must be
    # pinned"). Leaving the anchor on the adaptive smoother would solve rho=1 under a different residual
    # from every other point, and since the anchor's x is the warm start the whole march is seeded from,
    # that difference propagates. Measured at rho=1: same nfev (26 vs 25), a 33x tighter residual
    # (1.5e-11 vs 5.2e-10), and beta/omega move -0.057%/+0.32%.
    knots = args.smoothKnots if args.smoothKnots else None      # 0 -> the adaptive branch
    crraGS = {'nι': args.nι, 'ns': args.ns, 'interpKind': args.interpKind, 'smoothKnots': knots}
    # interpKind is given to BOTH solvers (2026-08-20). It is not a resolution choice but a
    # well-posedness one, the same argument as smoothKnots above: at 'linear' the LOG solve does not
    # converge in nι, it JITTERS -- tau(t0) spans 9.6e-4 across nι in [45,120] with no trend, against
    # 2.2e-5 at 'cubic', and tau(t0+1) 2.4e-3 against 2.5e-5. Since tau(t0) is a calibration target the
    # four parameters were being fitted to one realisation of that jitter at one nι, displacing the rho=1
    # anchor off the curve its CRRA neighbours trace and putting a +10.6%-of-scale spike in the
    # universalisation response at t0+1. It was keyed on CRRA only because that is where
    # crossCuttingFindings #4 surfaced -- see #7, and notes/informalSavings_resolvedIssues.md for the
    # full chain. nι stays per-solver: THAT one is a resolution choice and legitimately differs.
    logGS = {'smoothKnots': knots, 'interpKind': args.interpKind}
    gridSettings = {'CRRA': crraGS, 'LOG': dict(crraGS) if args.common else logGS}
    # LOG is keyed here too (2026-08-20). It was CRRA-only, so every LOG row of every sweep carried
    # verifyResidual=NaN -- the one point running the unconverged interpolant was also the one point with
    # no resolution check, which is why the defect above survived. 75 is LOG's established refinement
    # rung (1.5x its nι=50), matching test_calibrationGrid.py's VERIFY.
    verify = ({'CRRA': {'nι': args.verify, 'ns': args.verify, 'interpKind': args.interpKind},
               'LOG': {'nι': args.verifyLOG}}
              if args.verify else None)

    done, df = ({}, pd.DataFrame(columns = COLUMNS)) if args.force else readDone(args.out)
    # Keyed by rho, not a list: marchGrid reports one record per *attempt*, so a point that fails on the
    # extrapolated start and succeeds on the carried one arrives twice, and a resumed run revisits values
    # already in the csv. Keying makes every write idempotent and lets a success overwrite an earlier
    # failure at the same rho.
    rows = {} if args.force else {round(float(r['ρ']), 6): r for r in df.to_dict('records')}
    print('grid: {} points, {} to {} step {}'.format(len(grid), grid[0], grid[-1], args.step))
    print('anchor rho={}, inner grid {}x{}, verify at {}/{}, smoothKnots={}, interpKind={} (both '
          'solvers), LOG grid {}'.format(
              args.anchor, args.nι, args.ns, args.verify or 'off', args.verifyLOG,
              knots or 'adaptive', args.interpKind, 'CRRA sizes' if args.common else 'own nι=50'))
    if done:
        print('resuming: {} of {} points already in {}'.format(
            sum(round(float(v), 6) in done for v in grid), len(grid), os.path.relpath(args.out, REPO)))

    m = ModelInformalSavings(pars = testmod.pars | {'ρ': float(args.anchor)}, **testmod.kwargs)

    def write():
        (pd.DataFrame(list(rows.values())).reindex(columns = COLUMNS).sort_values('ρ')
           .to_csv(args.out, index = False))

    def solve(ρ, x0):
        """ marchGrid's callback. A point already in the csv is returned from it -- not re-solved, but
        still installed into db, so the next point's *inner* warm start is not left at a stale parameter
        point while its outer one is up to date. """
        key = round(float(ρ), 6)
        if key in done:
            x = done[key]
            m.db.update(m.adjPar('ρ', float(ρ)))
            m._calSetPars(m._calFromX(x))
            print('  rho={:<6} cached'.format(key))
            return {'x': x, 'cached': True}
        rec = m.calibratePoint(ρ, x0 = x0, gridSettings = gridSettings, verify = verify)
        print('  rho={:<6} {:<4} max|res|={:.2e}  verify={:.2e}  nfev={:<3} {:.0f}s  '
              'β={:.5f} ω={:.5f} η0={:.5f} X0={:.5f}'.format(
                  key, rec['preferences'], rec['residual'], rec.get('verifyResidual', np.nan),
                  rec['nfev'], rec['time'], rec['β'], rec['ω'], rec['η0'], rec['X0']))
        return rec

    def onPoint(r):
        """ Persist after every successful point. Failures are only *reported* here -- a failed attempt
        does not mean a failed point, since the march still has the carried start and step-halving to try,
        so which values genuinely failed is not known until the march returns. """
        key = round(float(r['value']), 6)
        if not r['ok']:
            print('  rho={:<6} attempt failed ({}): {}'.format(key, r['x0Source'], r['error'][:100]))
            return
        if r['result'].get('cached'):
            return
        rows[key] = toRow(r['result'], r['requested'], commit)
        write()
        with open(os.path.join(pkldir, 'rho_{:.4f}.pkl'.format(r['value'])), 'wb') as f:
            pickle.dump(m, f)

    out = continuation.marchGrid(grid, solve, anchor = args.anchor, degree = args.degree,
                                 maxHalvings = args.maxHalvings, onPoint = onPoint)

    # A failed *attempt* is not a failed point -- the retry ladder and step-halving may have rescued it.
    # Only values with no successful record anywhere are written as failures.
    solvedValues = {round(float(r['value']), 6) for r in out['records'] if r['ok']}
    hardFails = [r for r in out['failures'] if round(float(r['value']), 6) not in solvedValues]
    for r in hardFails:
        rows[round(float(r['value']), 6)] = {
            'ρ': round(float(r['value']), 6), 'requested': r['requested'], 'commit': commit,
            'residual': np.nan, 'preferences': 'FAILED: ' + r['error'][:120],
            'timestamp': datetime.datetime.now().isoformat(timespec = 'seconds')}
    write()

    solved = [r for r in out['records'] if r['ok']]
    print('\n{} solved ({} requested, {} inserted by step-halving), {} failed'.format(
        len(solved), sum(r['requested'] for r in solved), sum(not r['requested'] for r in solved),
        len(hardFails)))
    print('csv: ' + os.path.relpath(args.out, REPO))
    if hardFails:
        print('failed at rho: ' + ', '.join('{:.4f}'.format(r['value']) for r in hardFails))
    final = pd.DataFrame(list(rows.values())).reindex(columns = COLUMNS).sort_values('ρ')
    bad = final[final['verifyResidual'] > 1e-3]
    if len(bad):
        print('\nWARNING: {} point(s) converged but did not survive grid refinement -- do not read these '
              'as results, re-run them with a larger --nι/--ns:'.format(len(bad)))
        print(bad[['ρ', 'residual', 'verifyResidual']].to_string(index = False))
    return 0 if not hardFails else 1


if __name__ == '__main__':
    sys.exit(main())
