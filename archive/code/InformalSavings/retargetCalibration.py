r""" Recalibrate the Argentina (informalSavings) model across a grid of values for ONE 0-D target.

Run:  .venv\Scripts\python.exe python\InformalSavings\retargetCalibration.py [--par KY0] [--targets ...]

Context: `notes/argentina_calibrationTarget.md`, which is what moved the target from the savings rate
(`s0`) to the capital-output ratio (`KY0`). `--par` names the db key that moves; everything else is held,
including rho, which `--rho` fixes and which also selects the calibrated instance the march starts from
(`results/calibration/instances/rho_*.pkl` -- `calibrateRhoGrid.py` writes them). Each point is one
calibration warm started from the previous one, so order `--targets` with the instance's own value first.

`--par s0` reproduces the audit note's table only on the code as of 2026-08-24: `s0` is reported but no
longer targeted, so on this code every point of such a march returns the same calibration.

At rho != 1 the solver is CRRA and its inner grid must be the calibration's, not the PEE solve's (README,
"The CRRA calibration needs a finer inner grid than the CRRA solve") -- hence --niota/--ns and the two
well-posedness settings (interpKind, smoothKnots), defaulted to calibrateRhoGrid.py's.

Beyond (beta, omega, eta0, X0) each row records both aggregate readings of the same equilibrium: the
targeted K/Y and the savings rate s_t/Y_t that the paper's tables report. They are different objects --
K/Y prices the predetermined stock, sr the flow into it -- and the second is not implied by the first
without the period's capital growth, which is why both are recorded rather than converted.
"""
import os, sys, argparse, pickle, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)                                   # test.py reads data/ relative to its own location

OUT = os.path.join(REPO, 'results', 'calibration', 'informalSavings_KYGrid.csv')
PKLDIR = os.path.join(REPO, 'results', 'calibration', 'instances')
COLUMNS = ['par', 'target', 'ρ', 'preferences', 'β', 'ω', 'η0', 'X0', 'KY', 'sr', 'τ', 'ι',
           's', 's_', 'h', 'R30', 'Rann', 'residual', 'time']


def diagnostics(m, report):
    """ The solved path at db['t0'] and the return it implies. R = alpha*Y_t/K_t with K_t = s_{t-1}/nu_t
    (eq:factorPrices); Rann is its annual equivalent, i.e. the 30-year R spread over the period. """
    t0 = m.db['t'][m.db['t0']]
    rep = report['PEE']['report']
    s, s_, h = (float(rep[k].xs(t0)) for k in ('s', 's_', 'h'))
    α, ν = float(m.B.get('α', t0)), float(m.B.get('ν', t0))
    K = s_/ν
    R = α * K**α * h**(1-α) / K
    return {'s': s, 's_': s_, 'h': h, 'R30': R, 'Rann': R**(1/m.db['yearsPerPeriod']),
            'ι': float(rep['ι'].xs(m.db['txE'][m.db['t0']]))}


def loadInstance(ρ):
    """ A calibrated instance, with any 0-D parameter added since it was pickled filled in from the class
    defaults. The pickles predate KY0/yearsPerPeriod and carry a db that has neither. """
    m = pickle.load(open(os.path.join(PKLDIR, 'rho_{:.4f}.pkl'.format(ρ)), 'rb'))
    for k, v in m.default0DParams.items():
        m.db.setdefault(k, v)
    return m


def main():
    p = argparse.ArgumentParser(description = __doc__,
                                formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--par', default = 'KY0', help = 'the 0-D db key that moves along the march')
    p.add_argument('--targets', nargs = '*', type = float,
                   default = [3.2313, 3.4, 3.6606, 3.1, 3.0, 2.8, 2.6])
    p.add_argument('--rho', type = float, default = 1.0)
    p.add_argument('--niota', dest = 'nι', type = int, default = 45)
    p.add_argument('--ns', type = int, default = 45)
    p.add_argument('--interpKind', default = 'cubic', choices = ('linear', 'cubic', 'pchip'))
    p.add_argument('--smoothKnots', type = int, default = 4)
    p.add_argument('--out', default = OUT, help = 'relative paths resolve against the REPO root, not the '
                   'cwd -- this script chdirs to its own directory so test.py finds data/')
    args = p.parse_args()
    args.out = args.out if os.path.isabs(args.out) else os.path.join(REPO, args.out)

    rows = []
    m = loadInstance(args.rho)
    preferences = m._calPreferences()
    if preferences == 'CRRA':
        getattr(m, preferences).initGS({'nι': args.nι, 'ns': args.ns, 'interpKind': args.interpKind,
                                        'smoothKnots': args.smoothKnots or None})
    for target in args.targets:
        t = time.time()
        m.db[args.par] = float(target)
        cal = m.calibrate()                    # warm start: m.x0['calibration'] from the previous point
        d = diagnostics(m, cal['report'])
        row = {'par': args.par, 'target': target, 'ρ': args.rho, 'preferences': preferences,
               **{k: float(v) for k, v in cal['pars'].items()},
               'KY': float(cal['report']['KY']), 'sr': float(cal['report']['sr']),
               'τ': float(cal['report']['τ']), **d,
               'residual': float(np.max(np.abs(cal['residual']))), 'time': time.time()-t}
        rows.append({c: row.get(c) for c in COLUMNS})
        print('{}={:.4f}: β={:.4f} ω={:.4f} K/Y={:.3f} sr={:.4f} R={:.3f} ({:.4f}/yr) |res|={:.1e} '
              '[{:.0f}s]'.format(args.par, target, row['β'], row['ω'], row['KY'], row['sr'], row['R30'],
                                 row['Rann'], row['residual'], row['time']))
        pd.DataFrame(rows, columns = COLUMNS).to_csv(args.out, index = False)


if __name__ == '__main__':
    main()
