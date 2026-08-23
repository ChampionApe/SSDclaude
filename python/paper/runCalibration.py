r""" Stage (i) of the paper pipeline: produce the calibration the paper's numbers rest on.

Run:  .venv\Scripts\python.exe python\paper\runCalibration.py            check what exists, solve what does not
      ... --force                                                        re-solve every point
      ... --summaryOnly                                                  skip solving; just rebuild the summary
      ... --dry                                                          print the command and exit

Two things happen here, and only the first is expensive:

  1. The rho sweep. Delegated to python/InformalSavings/calibrateRhoGrid.py at config.ARG's grid and
     settings -- this file is the DECLARATION of what the paper calibrates, not a second implementation
     of it. ~75 minutes cold for the 16 points; the sweep is resumable and returns already-solved rho
     from its own csv, so a re-run with nothing to do costs seconds.

  2. The summary, results/paper/calibrationSummary.csv. Stage (iii) builds the calibration TABLE from
     this file rather than from a pickled instance, so that stage stays a pure csv -> tex step that
     needs no model import (README.md). It is the one point in the pipeline that opens a pickle.

WHY THE SUMMARY IS NOT JUST THE SWEEP CSV: informalSavings_rhoGrid.csv carries the four CALIBRATED
parameters (beta, omega, eta0, X0) but not the ones that are fixed or derived -- eps, theta, gamma0,
alpha, xi, nu, eta_i, X_i -- and those are half of the paper's calibration table. They live on the
instance, which is where this reads them from.
"""
import os, sys, argparse, subprocess, pickle, datetime, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C


def sweepCmd(force = False):
    g = C.ARG['gridSettings']
    ρ = C.ARG['ρGrid']
    step = round(ρ[1] - ρ[0], 10)
    cmd = [C.PYTHON, os.path.join(C.MODELDIR, 'calibrateRhoGrid.py'),
           '--lo', str(min(ρ)), '--hi', str(max(ρ)), '--step', str(step),
           '--anchor', str(C.ARG['ρAnchor']),
           '--nι', str(g['nι']), '--ns', str(g['ns']),
           '--interpKind', g['interpKind'], '--smoothKnots', str(g['smoothKnots'])]
    return cmd + (['--force'] if force else [])


def missing():
    """ rho in the paper's grid that the sweep csv does not already carry. """
    path = os.path.join(C.CALIBDIR, 'informalSavings_rhoGrid.csv')
    if not os.path.exists(path):
        return list(C.ARG['ρGrid'])
    have = set(np.round(pd.read_csv(path)['ρ'].values, 6))
    return [ρ for ρ in C.ARG['ρGrid'] if round(ρ, 6) not in have]


def summarise(ρ = None):
    """ The calibration table's content, at the paper's baseline rho, as one flat record.

    Unpickling needs ModelInformalSavings importable and test.py's data path resolvable, which is why
    this chdir's into the model directory exactly as the experiment scripts do. Held to this one
    function so that nothing else in the pipeline inherits the requirement.
    """
    ρ = C.ARG['ρBaseline'] if ρ is None else ρ
    cwd = os.getcwd()
    sys.path.insert(0, C.MODELDIR)
    os.chdir(C.MODELDIR)
    try:
        with open(os.path.join(C.INSTDIR, 'rho_{:.4f}.pkl'.format(ρ)), 'rb') as f:
            m = pickle.load(f)
        t0 = m.db['t0']
        first = lambda k: float(np.asarray(m.db[k])[0]) if np.ndim(m.db[k]) else float(m.db[k])
        atT0  = lambda k: float(m.db[k].xs(m.db['t'][t0])) if hasattr(m.db[k], 'xs') else first(k)
        # Vectors go through the csv as JSON, not as a python repr: under numpy 2 the repr of a list of
        # np.float64 is 'np.float64(1.64...)', whose literal text a number-scraping reader mines a
        # spurious 64.0 out of. json.dumps of plain floats has no such reading.
        vec = lambda a: json.dumps([float(v) for v in np.asarray(a, dtype = float).ravel()])
        rec = {'ρ': ρ, 'preferences': m._calPreferences(), 't0': t0, 'T': m.T,
               'ε': atT0('eps'), 'θ': atT0('θ'), 'γ0': atT0('γ0'),
               'α': atT0('α'), 'ξ': atT0('ξ'), 'η0': atT0('η0'), 'X0': atT0('X0'),
               'ν': vec(m.db['ν'].values),
               'ηi': vec(m.db['ηi'].xs(m.db['t'][t0])),
               'Xi': vec(m.db['Xi'].xs(m.db['t'][t0])),
               'γi': vec(m.db['γi'].xs(m.db['t'][t0]))}
    finally:
        os.chdir(cwd)
        sys.path.remove(C.MODELDIR)

    # beta/omega come from the sweep csv, not the pickle: the csv is the record of the calibration and
    # is what every other paper number is read against, so the table must not be able to disagree with it.
    df = pd.read_csv(os.path.join(C.CALIBDIR, 'informalSavings_rhoGrid.csv'))
    row = df.loc[np.isclose(df['ρ'], ρ)]
    if row.empty:
        raise SystemExit('rho={} is not in informalSavings_rhoGrid.csv -- run the sweep first.'.format(ρ))
    row = row.iloc[-1]
    for k in ('β', 'ω', 'sr', 'τ', 'ι', 'residual', 'verifyResidual', 'commit', 'timestamp'):
        rec[k] = row[k]
    # eta0/X0 are calibrated AND on the instance; they must agree, and a mismatch means the pickle and
    # the csv row came from different runs.
    for k in ('η0', 'X0'):
        if not np.isclose(rec[k], row[k], rtol = 1e-8):
            raise SystemExit('{}: instance {!r} != csv {!r}. Pickle and csv row are from different runs.'
                             .format(k, rec[k], row[k]))
    rec['builtAt'] = datetime.datetime.now().replace(microsecond = 0).isoformat()
    return rec


def main():
    p = argparse.ArgumentParser(description = __doc__.split('\n')[1])
    p.add_argument('--force', action = 'store_true', help = 're-solve every point, not only the missing')
    p.add_argument('--summaryOnly', action = 'store_true', help = 'rebuild the summary from what exists')
    p.add_argument('--dry', action = 'store_true', help = 'print the sweep command and exit')
    p.add_argument('--rho', type = float, default = None, help = 'summarise a rho other than the baseline')
    a = p.parse_args()

    cmd = sweepCmd(a.force)
    if a.dry:
        print(' '.join(cmd))
        return

    if not a.summaryOnly:
        todo = C.ARG['ρGrid'] if a.force else missing()
        if todo:
            print('calibrating {} point(s): {}'.format(len(todo), todo))
            print('  ' + ' '.join(cmd))
            r = subprocess.run(cmd, cwd = C.REPO)
            if r.returncode:
                raise SystemExit('calibrateRhoGrid.py exited {}'.format(r.returncode))
        else:
            print('all {} rho already solved; nothing to calibrate.'.format(len(C.ARG['ρGrid'])))

    rec = summarise(a.rho)
    os.makedirs(C.PAPERDIR, exist_ok = True)
    out = os.path.join(C.PAPERDIR, 'calibrationSummary.csv')
    pd.DataFrame([rec]).to_csv(out, index = False)
    print('\nwritten: ' + os.path.relpath(out, C.REPO))
    for k in ('ρ', 'β', 'ω', 'η0', 'X0', 'ε', 'θ', 'sr', 'τ', 'residual'):
        print('  {:<6} {}'.format(k, rec[k]))


if __name__ == '__main__':
    main()
