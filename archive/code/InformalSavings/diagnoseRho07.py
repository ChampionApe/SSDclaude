r""" Diagnostics for the unresolved calibration pocket at rho ~ 0.7-0.775 (README, "Results: the rho sweep").

Run:  .venv\Scripts\python.exe python\InformalSavings\diagnoseRho07.py [--test 1|2|both] [--rho 0.6 0.7875]

Both tests run off the pickled instances in results/calibration/instances/, i.e. at points that ACTUALLY
CONVERGED, which is what separates them from the diagnostics already on the ladder. The rho=0.7 finite-
difference probe recorded in the research log was taken at an off-root point (residual 4.4e-3) and the log
flags that caveat itself; the flanking points rho=0.6 and rho=0.7875 are converged, so the same measurement
there is comparable to the rho=1.1 one that produced _calOuterKwargs.

Test 1 -- outer Jacobian conditioning at converged flanking points. Forward-difference Jacobian of
eq:calibration's residual at several steps h. Reports per-column stability across h (the rho=1.1 symptom:
one corrupted column) and the condition number (the "ill-conditioned intersection" hypothesis: two residual
rows whose zero-contours are near-parallel would amplify grid noise into large parameter displacement while
leaving max|residual| small). Cost ~4 PEE solves per step per point.

Test 2 -- where the solved path sits inside the state grids. The iota grid's bounds (pad_iota, cap_iota)
and the s grid's (pad_s) were tuned at rho=1 on the Argentina calibration and have no standing elsewhere;
if the path at the pocket's flanks sits in a sparse stretch of either grid, the fix is node placement
rather than node count. Cost ~1 PEE solve per point.
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
# The sweep's own CRRA settings. calibration_residual does NOT install these (calibratePoint does), so a
# diagnostic that forgets them silently measures a different problem at the PEE default 30x30/linear.
GRIDSETTINGS = {'nι': 45, 'ns': 45, 'interpKind': 'cubic'}
# Pinned to the ADAPTIVE smoother, explicitly. This script's measurements were all taken against it, and
# test 4 exists to compare it with the fixed-knot branch -- so it must not follow policy.py's default,
# which became smoothKnots=4 on 2026-08-19. Overridden by --smoothKnots.
SMOOTHKNOTS = None
PARS = ('β', 'ω', 'η0', 'X0')
ROWS = ('sr', 'tau', 'eta0', 'X0')


def loadPoint(ρ):
    """ Pickled instance + the converged unbounded x from the csv. Returns (model, x, row). """
    path = os.path.join(PKLDIR, 'rho_{:.4f}.pkl'.format(ρ))
    with open(path, 'rb') as f:
        m = pickle.load(f)
    df = pd.read_csv(CSV)
    row = df.loc[(df['ρ']-ρ).abs().idxmin()]
    x = np.array([row['x{}'.format(i)] for i in range(4)], dtype = float)
    m.CRRA.initGS(GRIDSETTINGS | {'smoothKnots': SMOOTHKNOTS})   # explicit: None IS the adaptive request
    return m, x, row


def jacobian(m, x, h):
    """ Forward-difference Jacobian of calibration_residual, relative step h (scipy's `eps` convention).
    Column j = d(residual)/d(x_j). """
    f0 = m.calibration_residual(x, 'CRRA')
    J = np.empty((len(f0), len(x)))
    for j in range(len(x)):
        xp = x.copy()
        step = h*max(abs(x[j]), 1.0)
        xp[j] += step
        J[:, j] = (m.calibration_residual(xp, 'CRRA')-f0)/step
    return f0, J


def rowAngle(a, b):
    """ Angle between two residual rows in parameter space. Near 0 or 180 deg = near-parallel zero
    contours = an intersection that amplifies grid noise into parameter displacement. """
    c = (a @ b)/(np.linalg.norm(a)*np.linalg.norm(b))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def test1(ρ, steps):
    print('\n' + '='*78)
    print('TEST 1  outer Jacobian at the CONVERGED point rho={}'.format(ρ))
    print('='*78)
    m, x, row = loadPoint(ρ)
    print('csv: residual={:.2e} verify={:.2e} nfev={} beta={:.6f} omega={:.6f} eta0={:.6f} X0={:.6f}'.format(
        row['residual'], row['verifyResidual'], row['nfev'], row['β'], row['ω'], row['η0'], row['X0']))
    print('x   = ' + np.array2string(x, precision = 6))
    Js = {}
    for h in steps:
        t0 = time.time()
        f0, J = jacobian(m, x, h)
        Js[h] = J
        print('\nh={:.0e}   max|residual| at x = {:.3e}   ({:.0f}s)'.format(
            h, np.max(np.abs(f0)), time.time()-t0))
        print('   J (rows = residuals, cols = d/d' + ', d/d'.join(PARS) + ')')
        for i, r in enumerate(J):
            print('     {:<5}{}'.format(ROWS[i], np.array2string(r, precision = 4)))
        sv = np.linalg.svd(J, compute_uv = False)
        print('   cond(J) = {:.4g}   singular values = {}'.format(sv[0]/sv[-1],
                                                                  np.array2string(sv, precision = 3)))
        sub = J[:2, :2]                       # the 2-D (beta,omega) problem a fixed-eta0/X0 calibration faces
        svs = np.linalg.svd(sub, compute_uv = False)
        print('   cond(J[sr,tau x beta,omega]) = {:.4g}   angle(sr,tau rows) = {:.2f} deg'.format(
            svs[0]/svs[-1], rowAngle(sub[0], sub[1])))
    print('\ncolumn stability across h (||column|| relative to its value at the middle step):')
    ref = Js[steps[len(steps)//2]]
    print('   {:<10}'.format('h') + ''.join('{:>14}'.format('d/d'+p) for p in PARS))
    for h in steps:
        rel = [np.linalg.norm(Js[h][:, j])/np.linalg.norm(ref[:, j]) for j in range(4)]
        print('   {:<10.0e}'.format(h) + ''.join('{:>14.4f}'.format(v) for v in rel))
    return Js


def occupancy(name, grid, path):
    """ How much of a state grid the solved path actually uses, and at what local resolution. """
    lo, hi = grid[0], grid[-1]
    pmin, pmax = np.min(path), np.max(path)
    cells = np.diff(grid)
    idx = np.clip(np.searchsorted(grid, path)-1, 0, len(grid)-2)
    print('\n  {}: grid [{:.5f}, {:.5f}], {} nodes, cells {:.2e}..{:.2e}'.format(
        name, lo, hi, len(grid), cells.min(), cells.max()))
    print('    path range [{:.5f}, {:.5f}]  ->  {:.1f}% of the grid span'.format(
        pmin, pmax, 100*(pmax-pmin)/(hi-lo)))
    print('    cell width where the path lives: {:.2e}..{:.2e}  (= {:.1f}x..{:.1f}x the narrowest cell)'.format(
        cells[idx].min(), cells[idx].max(), cells[idx].min()/cells.min(), cells[idx].max()/cells.min()))
    print('    nodes strictly inside the path range: {} of {}'.format(
        int(((grid > pmin) & (grid < pmax)).sum()), len(grid)))
    print('    distance to bounds: {:.1f} cells below, {:.1f} cells above'.format(
        (pmin-lo)/cells[0], (hi-pmax)/cells[-1]))


def reachableFrom(sols, sGrid, ιGrid, sBox, ιBox):
    """ Is the region the path occupies close to invariant under the state transition? Restrict the state
    grid to [sBox]x[ιBox] and report the (s_t,ι_t) the recursion maps that block into, per period and
    unioned (docs eq:reachable, recorded by CRRA.report_t).

    This is the number that decides whether the grid bounds can be narrowed: the reachable set computed
    over the WHOLE grid is wide by construction (far-out states map far out), so it answers nothing. What
    matters is whether states near the path stay near the path. """
    si = (sGrid >= sBox[0]) & (sGrid <= sBox[1])
    ιi = (ιGrid >= ιBox[0]) & (ιGrid <= ιBox[1])
    print('\n  reachable set from the {}x{} block of S x S_0 covering the path:'.format(si.sum(), ιi.sum()))
    sAll, ιAll = [], []
    for t, d in sorted(sols.items()):
        r = d.get('reachable')
        if r is None:
            continue
        s = np.asarray(r['s'])[np.ix_(si, ιi)]
        ι = np.asarray(r['ι'])[np.ix_(si, ιi)]
        ok = np.asarray(r['inGrid'])[np.ix_(si, ιi)]
        sAll.append(s[ok]); ιAll.append(ι[ok])
        print('    t={:<3} s in [{:.5f}, {:.5f}]   iota in [{:.5f}, {:.5f}]   ({} of {} in grid)'.format(
            t, np.nanmin(s), np.nanmax(s), np.nanmin(ι), np.nanmax(ι), int(ok.sum()), ok.size))
    if sAll:
        s, ι = np.concatenate(sAll), np.concatenate(ιAll)
        print('    union   s in [{:.5f}, {:.5f}]   iota in [{:.5f}, {:.5f}]'.format(
            np.nanmin(s), np.nanmax(s), np.nanmin(ι), np.nanmax(ι)))


def test2(ρ):
    print('\n' + '='*78)
    print('TEST 2  where the solved path sits inside the state grids, rho={}'.format(ρ))
    print('='*78)
    m, x, row = loadPoint(ρ)
    θ, ε = m.db['θ'].values, m.db['eps'].values
    tT = m.db['t'][-1]
    ιGrid = m.CRRA.defaultIotaGrid(θ[-1], ε[-1], t = tT)
    sGrid = m.CRRA.defaultSGrid(θ[-1], t = tT)
    t0 = time.time()
    out = m.solvePEE_CRRA()
    rep = out['report']
    print('solved in {:.0f}s'.format(time.time()-t0))
    # s_ is the state ENTERING each period; s itself ends at the structural s_T=0 (README, "Reporting
    # domains"), which is not a visited state and would drag the measured range to the grid's floor.
    ιPath, sPath = rep['ι'].values, rep['s_'].values
    occupancy('iota (S_0)', ιGrid, ιPath)
    occupancy('s    (S)  ', sGrid, sPath)
    reachableFrom(out['sols'], sGrid, ιGrid,
                  (0.5*np.min(sPath), 2.0*np.max(sPath)), (0.5*np.min(ιPath), 2.0*np.max(ιPath)))
    return out


def test3(ρ, j = 0, span = 2e-4, n = 41):
    """ Scan the outer residual along one coordinate of x at fine spacing, looking for JUMPS.

    Test 1 finds the beta column of the Jacobian at rho=0.7875 disagreeing by ~22% at the calibration's
    configured step eps=1e-4 while h=1e-5 and h=1e-3 agree with each other. A step that is an outlier on
    BOTH sides is the signature of a discontinuity sitting inside [x, x+1e-4] but outside [x, x+1e-5]:
    a jump J contributes J/h to the measured slope, so it dominates at the step that first straddles it
    and is diluted tenfold at the next decade up. This measures J directly.

    J matters because it is a floor: if the residual surface has jumps of size J, no solver drives
    |residual| below J, and the pocket's plateau at 3.3e-6 is explained rather than merely described. """
    print('\n' + '='*78)
    print('TEST 3  residual scan along x[{}] ({}), rho={}'.format(j, PARS[j], ρ))
    print('='*78)
    m, x, row = loadPoint(ρ)
    offsets = np.linspace(0.0, span, n)
    print('{:>12} {:>14} {:>14} {:>14} {:>14}'.format('offset', *ROWS))
    vals = []
    for o in offsets:
        xp = x.copy(); xp[j] += o
        r = m.calibration_residual(xp, 'CRRA')
        vals.append(r)
        print('{:>12.3e} {:>14.6e} {:>14.6e} {:>14.6e} {:>14.6e}'.format(o, *r))
    v = np.array(vals)
    d = np.diff(v, axis = 0)
    step = offsets[1]-offsets[0]
    print('\nlargest successive changes per row (a smooth residual gives ~slope*step uniformly):')
    for i, name in enumerate(ROWS):
        k = int(np.argmax(np.abs(d[:, i])))
        med = np.median(np.abs(d[:, i]))
        print('  {:<5} median |delta| = {:.3e}   max |delta| = {:.3e} at offset {:.3e}  '
              '(ratio {:.1f}x)'.format(name, med, abs(d[k, i]), offsets[k+1], abs(d[k, i])/med
                                       if med else np.inf))
    print('\nstep between nodes = {:.3e}'.format(step))
    return offsets, v


def diagnostics(m, x, j, offset, solveKwargs = None):
    """ Every discrete quantity the CRRA solve makes a choice about, at x + offset·e_j. These are the
    candidates for the jump's source: a feasibility node flipping, selectMax landing on a different
    tau-node, a root count changing, or a state leaving the grid. """
    xp = x.copy(); xp[j] += offset
    d = m.calibration_report(m._calFromX(xp), 'CRRA', solveKwargs)
    pee = d['PEE']
    out = {'targets': np.array([d['KY'], d['τ'], d['η0'], d['X0']]),
           'initNRoots': None if pee['init'] is None else int(pee['init']['nRoots']),
           'initS': None if pee['init'] is None else float(pee['init']['s']),
           'initI': None if pee['init'] is None else float(pee['init']['ι']),
           'pathTau': pee['path']['τ'].values.copy(), 'periods': {}}
    for t, r in sorted(pee['sols'].items()):
        e = {}
        for k in ('feasible', 'atBound', 'outOfGrid'):
            if k in r:
                e[k] = int(np.sum(np.asarray(r[k], dtype = bool)))
        for k in ('nMax', 'nRootsS', 'nRootsι', 'nRootsSolS', 'nRootsSolι'):
            if k in r:
                v = np.asarray(r[k], dtype = float)
                e[k+'.sum'] = float(np.nansum(v))
                e[k+'.ne1'] = int(np.nansum(v != 1))
        e['tau'] = np.asarray(r['τ'], dtype = float)
        out['periods'][t] = e
    return out


def test4(ρ, j = 0, offsets = (8.0e-5, 8.5e-5), smooth = None):
    """ What discrete choice changes across the dominant jump. Test 3 locates it between two adjacent
    scan nodes; this re-solves at both and diffs every selection/feasibility/root-count diagnostic the
    recursion records, per period. Whichever changes exactly there is the mechanism -- and it decides
    whether retuning the state grids is the fix or an irrelevance. """
    print('\n' + '='*78)
    print('TEST 4  what switches across the jump, rho={}, along x[{}] ({})'.format(ρ, j, PARS[j]))
    print('='*78)
    m, x, row = loadPoint(ρ)
    sk = None if smooth is None else {'backwardKwargs': {'smooth': smooth}}
    A = diagnostics(m, x, j, offsets[0], sk)
    B = diagnostics(m, x, j, offsets[1], sk)
    print('offsets {:.3e} -> {:.3e}   smooth={}'.format(offsets[0], offsets[1],
                                                        'default' if smooth is None else smooth))
    print('targets     {}'.format(np.array2string(A['targets'], precision = 8)))
    print('         -> {}'.format(np.array2string(B['targets'], precision = 8)))
    print('         d= {}'.format(np.array2string(B['targets']-A['targets'], precision = 3)))
    for k in ('initNRoots', 'initS', 'initI'):
        flag = '  <-- CHANGED' if A[k] != B[k] else ''
        print('{:<12} {} -> {}{}'.format(k, A[k], B[k], flag))
    dτ = B['pathTau']-A['pathTau']
    print('walked tau  max|delta| = {:.3e} at period {}'.format(np.max(np.abs(dτ)), int(np.argmax(np.abs(dτ)))))
    print('            per period: ' + np.array2string(dτ, precision = 3))
    print('\nper-period discrete diagnostics (only entries that CHANGED are shown):')
    anyChange = False
    for t in A['periods']:
        a, b = A['periods'][t], B['periods'][t]
        msgs = ['{}: {} -> {}'.format(k, a[k], b[k]) for k in a
                if k != 'tau' and a[k] != b[k]]
        dt = b['tau']-a['tau']
        nCell = int(np.sum(np.abs(dt) > 1e-12))
        msgs.append('tau grid: {} of {} cells moved, max|delta| = {:.3e}'.format(nCell, dt.size, np.max(np.abs(dt))))
        if len(msgs) > 1 or nCell:
            anyChange = True
        print('  t={:<3} {}'.format(t, '; '.join(msgs)))
    if not anyChange:
        print('  (nothing discrete changed -- the jump is not a selection/feasibility switch)')
    return A, B


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', default = 'both', choices = ('1', '2', '3', '4', 'both'))
    p.add_argument('--offsets', type = float, nargs = 2, default = [8.0e-5, 8.5e-5])
    p.add_argument('--smooth', type = float, default = None, help = 'override solveBackward smooth (0 = off)')
    p.add_argument('--smoothKnots', type = int, default = None, help = 'fixed-knot policy smoother: knot every m-th node')
    p.add_argument('--rho', type = float, nargs = '+', default = [0.6, 0.7875])
    p.add_argument('--steps', type = float, nargs = '+', default = [1e-5, 1e-4, 1e-3])
    a = p.parse_args()
    SMOOTHKNOTS = a.smoothKnots
    for ρ in a.rho:
        if a.test in ('2', 'both'):
            test2(ρ)
        if a.test in ('1', 'both'):
            test1(ρ, a.steps)
        if a.test == '3':
            test3(ρ)
        if a.test == '4':
            test4(ρ, offsets = tuple(a.offsets), smooth = a.smooth)
