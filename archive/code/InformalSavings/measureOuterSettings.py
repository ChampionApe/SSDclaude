r""" Re-measure the two CRRA calibration settings that predate smoothKnots and the retuned grid rule
(README, "The CRRA calibration's three settings"): the outer finite-difference step `eps`
(deviations note item 11) and the inner grid size nι=ns=45 (item 12). Not a test -- a measurement script.

Run:  .venv\Scripts\python.exe python\InformalSavings\measureOuterSettings.py --test all

Both settings were established under the ADAPTIVE-knot smoother and the OLD grid rule, i.e. against an
outer residual that had ~3.5e-6 jumps in it (notes/informalSavings_resolvedIssues.md). Item 13's step and
item 12's grid are each a defence against a symptom that the two 2026-08-19 changes may have removed at
source, so both numbers are re-derived here rather than carried:

  --test jac   mechanism. Forward-difference Jacobian of eq:calibration's residual across steps h, at the
               CONVERGED points of the retuned partial sweep. Item 13's finding was one corrupted column
               (η0 at 5x its resolved value at scipy's default step); this asks whether that column is
               still corrupted now that the residual is continuous. Cost ~4 residual evaluations per step
               per rho (~2.5 min at 45x45).

  --test eps   decision. Calibrate at each candidate eps from a COMMON start (the LOG anchor's x at
               rho=1), which is what item 13 did and what makes nfev comparable. A Jacobian table says
               which step is accurate; only this says which one the Newton search survives. Cost ~1
               calibration per (rho, eps) -- ~6 min each when it converges, considerably more when it
               does not.

  --test grid  decision. Calibrate at each inner grid size, then re-evaluate the outer residual at the
               converged parameters on a ladder of finer grids. Item 12's diagnostic: the number DECAYS
               if the answer is grid-converged and PLATEAUS if the root is displaced, and it was the
               plateau at 30x30 -- not the size of the residual -- that established 45x45. Also reports
               the parameter distance from the 45x45 answer, since a displaced root is displaced in the
               parameters, not in the residual. Cost ~1 calibration + 3 evaluations per grid size.

All three run at interpKind='cubic' and smoothKnots=4, i.e. the settings the next sweep will use.
"""
import os, sys, argparse, pickle, time
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
os.chdir(HERE)                                  # test.py resolves data/ relative to the repo root

# The live sweep. A diagnostic run is only comparable to points carrying the same solver settings, so if
# this is ever pointed at another csv, check it was solved at BASE below (crossCuttingFindings #8: a
# default filename that was correct when written is not evidence it still is).
CSV    = os.path.join(REPO, 'results', 'calibration', 'informalSavings_rhoGrid.csv')
PKLDIR = os.path.join(REPO, 'results', 'calibration', 'instances')
PARS = ('β', 'ω', 'η0', 'X0')
ROWS = ('sr', 'τ', 'η0', 'X0')
BASE = {'interpKind': 'cubic', 'smoothKnots': 4}


def csvRow(ρ):
    df = pd.read_csv(CSV)
    row = df.loc[(df['ρ']-ρ).abs().idxmin()]
    return row, np.array([row['x{}'.format(i)] for i in range(4)], dtype = float)


def gridSettings(n):
    return BASE | {'nι': n, 'ns': n}


def loadPoint(ρ, n = 45):
    """ Pickled instance (db at ITS OWN converged parameters) + the converged unbounded x. """
    with open(os.path.join(PKLDIR, 'rho_{:.4f}.pkl'.format(ρ)), 'rb') as f:
        m = pickle.load(f)
    row, x = csvRow(ρ)
    m.CRRA.initGS(gridSettings(n))
    return m, x, row


def freshModel(ρ):
    """ A model built from test.py's own parameters at this rho -- no state carried from any solve. """
    import test as testmod
    from model import ModelInformalSavings
    return ModelInformalSavings(pars = testmod.pars | {'ρ': float(ρ)}, **testmod.kwargs)


def jacobian(m, x, h):
    """ Forward-difference Jacobian of calibration_residual at relative step h (scipy's `eps`
    convention: hybr's actual step is h*max(|x_j|,1)). Column j = d(residual)/d(x_j). """
    f0 = m.calibration_residual(x, 'CRRA')
    J = np.empty((len(f0), len(x)))
    for j in range(len(x)):
        xp = x.copy()
        step = h*max(abs(x[j]), 1.0)
        xp[j] += step
        J[:, j] = (m.calibration_residual(xp, 'CRRA')-f0)/step
    return f0, J


def testJac(ρ, steps, n):
    print('\n' + '='*90)
    print('JAC   outer Jacobian at the converged rho={}, {}x{}, {}'.format(ρ, n, n, BASE))
    print('='*90)
    m, x, row = loadPoint(ρ, n)
    print('csv: residual={:.2e} verify={:.2e} nfev={} β={:.6f} ω={:.6f} η0={:.6f} X0={:.6f}'.format(
        row['residual'], row['verifyResidual'], row['nfev'], row['β'], row['ω'], row['η0'], row['X0']))
    Js = {}
    for h in steps:
        t0 = time.time()
        f0, J = jacobian(m, x, h)
        Js[h] = J
        print('\nh={:.2e}   max|residual| at x = {:.3e}   ({:.0f}s)'.format(h, np.max(np.abs(f0)),
                                                                           time.time()-t0))
        for i, r in enumerate(J):
            print('   {:<4}{}'.format(ROWS[i], np.array2string(r, precision = 4)))
        sv = np.linalg.svd(J, compute_uv = False)
        print('   cond(J) = {:.4g}'.format(sv[0]/sv[-1]))
    # Item 13's decisive display: a column that is a property of the residual is flat across h; a column
    # corrupted by a jump straddled at one step stands out against its neighbours.
    print('\ncolumn norms relative to the middle step (flat = the step is not the lever):')
    ref = Js[steps[len(steps)//2]]
    print('   {:<11}'.format('h') + ''.join('{:>13}'.format('d/d'+p) for p in PARS) + '{:>13}'.format('cond'))
    for h in steps:
        rel = [np.linalg.norm(Js[h][:, j])/np.linalg.norm(ref[:, j]) for j in range(4)]
        sv = np.linalg.svd(Js[h], compute_uv = False)
        print('   {:<11.2e}'.format(h) + ''.join('{:>13.4f}'.format(v) for v in rel)
              + '{:>13.4g}'.format(sv[0]/sv[-1]))
    return Js


def calibrateAt(ρ, x0, n, calKwargs):
    """ One CRRA calibration at rho on an n x n inner grid. Returns (model, record) with record['ok']. """
    m = freshModel(ρ)
    m.CRRA.initGS(gridSettings(n))
    t0 = time.time()
    try:
        cal = m.calibrate(preferences = 'CRRA', x0 = x0, **calKwargs)
        rec = {'ok': True, 'time': time.time()-t0, 'nfev': int(cal['scipyRes'].nfev),
               'residual': float(np.max(np.abs(cal['residual']))), 'x': cal['x'],
               'pars': {k: float(v) for k, v in cal['pars'].items()}}
    except Exception as e:
        rec = {'ok': False, 'time': time.time()-t0, 'error': str(e)[:160]}
    return m, rec


def parDist(pars, row):
    """ Max relative distance of a calibrated parameter vector from the reference csv row. """
    return max(abs(pars[k]/float(row[k])-1) for k in PARS)


def testEps(ρ, epsList, n):
    print('\n' + '='*90)
    print('EPS   calibrate at rho={} from the LOG anchor, {}x{}, {}'.format(ρ, n, n, BASE))
    print('='*90)
    ref, _ = csvRow(ρ)
    _, xStart = csvRow(1.0)                     # the common start: the LOG anchor's converged x
    print('start x (LOG anchor at rho=1) = ' + np.array2string(xStart, precision = 6))
    print('reference (retuned sweep):      β={:.6f} ω={:.6f} η0={:.6f} X0={:.6f}  nfev={}'.format(
        ref['β'], ref['ω'], ref['η0'], ref['X0'], ref['nfev']))
    out = {}
    for eps in epsList:
        kw = {} if eps is None else {'options': {'eps': float(eps)}}
        _, rec = calibrateAt(ρ, xStart, n, kw)
        out[eps] = rec
        label = 'scipy default' if eps is None else '{:.0e}'.format(eps)
        if rec['ok']:
            print('  eps={:<14} OK    max|res|={:.2e}  nfev={:<4} {:>5.0f}s   '
                  'β={:.6f} ω={:.6f} η0={:.6f} X0={:.6f}   Δpar vs ref = {:.2e}'.format(
                      label, rec['residual'], rec['nfev'], rec['time'], rec['pars']['β'],
                      rec['pars']['ω'], rec['pars']['η0'], rec['pars']['X0'], parDist(rec['pars'], ref)))
        else:
            print('  eps={:<14} FAIL  {:>5.0f}s   {}'.format(label, rec['time'], rec['error']))
    return out


def testGrid(ρ, nList, ladder, calKwargs):
    print('\n' + '='*90)
    print('GRID  calibrate at rho={} on each inner grid, then refine at fixed parameters. {}'.format(
        ρ, BASE))
    print('      calKwargs = {}'.format(calKwargs))
    print('='*90)
    ref, _ = csvRow(ρ)
    _, xStart = csvRow(1.0)
    out = {}
    for n in nList:
        m, rec = calibrateAt(ρ, xStart, n, calKwargs)
        if not rec['ok']:
            print('  n={:<4} FAIL  {:>5.0f}s   {}'.format(n, rec['time'], rec['error']))
            out[n] = rec
            continue
        print('  n={:<4} OK    max|res|={:.2e}  nfev={:<4} {:>5.0f}s   '
              'β={:.6f} ω={:.6f}   Δpar vs 45x45 ref = {:.2e}'.format(
                  n, rec['residual'], rec['nfev'], rec['time'], rec['pars']['β'], rec['pars']['ω'],
                  parDist(rec['pars'], ref)))
        # The refinement ladder is the diagnostic, not the residual at the calibration's own grid: a
        # displaced root has a small residual on the grid that displaced it.
        trend = []
        for k in ladder:
            m.CRRA.initGS(gridSettings(k))
            try:
                trend.append(float(np.max(np.abs(m.calibration_residual(rec['x'], 'CRRA')))))
            except Exception:
                trend.append(np.nan)
        m.CRRA.initGS(gridSettings(n))
        rec['trend'] = trend
        # Summarise the rungs OFF this calibration's own grid only. The rung at n is ~1e-12 by
        # construction (it is the grid the root was found on), so including it makes every ladder "rise"
        # at its first step and any shape classifier fire on every row -- which is what the first version
        # of this script did. What discriminates is the LEVEL the off-grid rungs sit at, compared across
        # n: item 12's displaced 30x30 sat at 3.1e-3 against 45x45's 1e-4.
        off = [v for k, v in zip(ladder, trend) if k != n]
        rec['offGrid'] = off
        print('       refined at {}: {}   -> off-own-grid {:.1e}..{:.1e} (median {:.1e})'.format(
            ' / '.join(str(k) for k in ladder),
            ' / '.join('{:.2e}'.format(v) for v in trend),
            min(off), max(off), float(np.median(off))))
        out[n] = rec
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', default = 'all', choices = ('jac', 'eps', 'grid', 'all'))
    p.add_argument('--rho', type = float, nargs = '+', default = [0.7, 0.9])
    p.add_argument('--steps', type = float, nargs = '+',
                   default = [1.49e-8, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2])
    p.add_argument('--eps', type = float, nargs = '+', default = [1e-4, 1e-3],
                   help = 'candidate outer steps; scipy\'s default is added as None')
    p.add_argument('--n', type = int, default = 45, help = 'inner grid for --test jac/eps')
    p.add_argument('--nGrid', type = int, nargs = '+', default = [30, 45, 60])
    p.add_argument('--ladder', type = int, nargs = '+', default = [45, 60, 75])
    p.add_argument('--gridEps', default = 'default',
                   help = "outer step used by --test grid, set from what --test eps concludes; "
                          "'default' leaves scipy's own step, which is what that test settled on")
    a = p.parse_args()
    for ρ in a.rho:
        if a.test in ('jac', 'all'):
            testJac(ρ, a.steps, a.n)
        if a.test in ('eps', 'all'):
            testEps(ρ, [None] + list(a.eps), a.n)
        if a.test in ('grid', 'all'):
            testGrid(ρ, a.nGrid, a.ladder,
                     {} if a.gridEps == 'default' else {'options': {'eps': float(a.gridEps)}})
