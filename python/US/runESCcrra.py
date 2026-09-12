r""" Endogenous system characteristics under CRRA: calibrate the wedge at rho != 1, solve the design path,
and run the ageing counterfactual.

Run:  .venv\Scripts\python.exe python\US\runESCcrra.py                       # rho = 2, both specs, phi=.5
      ... --rho 2.0 0.5  --spec scale  --phi 0.5  --commonX
      ... --stage calib path shocks sens
      ... --exact --stage calib path shocks --ns 150                        # the published method

TWO METHODS, one `method` column. Every row written here carries method = 'exact' or 'path', and the
column is part of every merge key, so the two vintages coexist in one csv and the paper pipeline selects
by it (python/paper/datasets.py, config.US['esc']['exact']).

  --exact   LeadedCRRA2D through ModelESC.solveLeaded2D: backward-solved policy functions over the
            two-dimensional state (s_{t-1}, theta_t), no held-fixed future. The PUBLISHED method for the
            CRRA ESC leg. One full recursion per calibration trial and per chosen-design reading
            (~6 min at ns = 150, ~95 s at ns = 50; the two grids agree to 3e-5 in the design, the
            theta-state grid is what the accuracy hangs on -- test_escCRRA.py). The wedge calibration
            therefore SCANS on the coarse grid (--nsScan) and refines the bracketed root on --ns, so it
            needs no warm start from the path iteration; a path p on file only narrows the scanned
            bracket to half..double of it.
  default   LeadedCRRA's path iteration, the development stand-in certified against the exact recursion
            to ~0.01 in the design (test_escCRRA.py). No paper output reads it.

Why this is a separate driver from runESC.py: under CRRA nothing about the leaded choice is cheap. The tau
FOC depends on s_{t-1}, so there is no static tauPolicy(theta); W_t is not additively separable, so the
choice depends on both states; and every candidate design costs a full solvePEE_CRRA (~3 s) instead of a
closed form. The path iteration budgets:

    calibrate p     ~70 s per trial value  (a 35 s recalibration of (beta, omega) + 13 candidate solves)
    the design path ~2 min per iteration
    each shock      one path solve per reading

STAGES
  calib   p such that the equilibrium design IN FORCE at t0 reproduces theta*, per (rho, spec, phi) --
          ModelESC.leadedDesignAtT0_CRRA (path) or leadedDesignAtT0_2D (exact), the design chosen one
          period BEFORE 2020, which is what the tables read. The bracket is scanned an order of magnitude
          BELOW the LOG one: at rho = 2 the LOG-calibrated p = 0.41 already puts the choice at the
          theta = 1 corner (a higher EIS needs far less wedge to reach an interior choice).
  path    the design path at the calibrated p, plus targetDrift.
  sens    stateSensitivity -- d(theta_{t+2})/d(theta_{t+1}), the quantity the path iteration assumes is
          zero. It IS zero under LOG (proved and measured); this reports what it is under CRRA. Any path
          result should be read next to this number. Not run under --exact (nothing is assumed there).
  shocks  counterfactuals, theta pinned vs chosen, each a NEW EQUILIBRIUM PATH (shocked parameters over
          the whole horizon, own steady state, the choice binding from the first period) and REPORTED AT
          t0. Default scenario set: acute ageing plus the French characteristics -- income distribution,
          leisure, voting, their income+voting combination and all three at once -- the same set
          runESC.py's LOG stage runs, selectable via --scenarios, plus France's own calibrated path as
          the endpoint row. The French data are frenchData's (runShocksUS.py), calibrated at the SAME rho
          under CRRA, computed once per rho and shared across specs.
  permanent   the permanent choice traced in rho (stagePermanentCRRA), escPermanentCRRA.csv.
  sequential  the COSTLESS sequential FOC of eq:esc:seqFOC (ModelESC.sequentialFOC) on the solved
              no-wedge baseline at every dated period, escSequentialCRRA.csv: its sign over theta in
              [0,1] is the "three timings, one corner" claim under CRRA (the LOG case is test_esc.py's).
"""
import os, sys, argparse, time
import numpy as np, pandas as pd
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)

import test as testmod
import shocks as sh
from modelESC import ModelESC
from runESC import SHOCKS_ESC, mergeWrite, buildEU, readout as escReadout
from runShocksUS import frenchData

OUTDIR = os.path.join(REPO, 'results', 'esc')
GSC = {'n': 101, 'ns': 150, 'smoothKnots': 4, 'interpKind': 'linear'}

# Row-identity keys, rho-indexed counterparts of runESC's. commonX is in all three -- see mergeWrite.
# method too: an exact row and a path row answer the same question by different solvers and must not
# overwrite each other (the pipeline selects by method).
KEYCAL = ['ρ', 'spec', 'phi', 'commonX', 'method']
KEYPATH = ['ρ', 'spec', 'phi', 'commonX', 'method', 'pos']
KEYSHK = ['ρ', 'spec', 'phi', 'commonX', 'method', 'scenario', 'θpinned']


def buildUS(ρ, wedge = None, nθCandCRRA = 13, commonX = False, gs = None, nθCand2D = 21):
    """ runESC.buildUS's CRRA counterpart: (beta, omega) seeded from the matching variant's sweep, the
    calibration itself redone by the caller. gs: the CRRA grid settings (GSC by default); LeadedCRRA2D
    borrows them at solve time, so --ns reaches the exact solver through here. nθCand2D: the exact
    recursion's candidate grid for θ_{t+1} -- the objective is flat near its maximum (~1e-5 in W over
    ±0.01 in θ at the frVoting choice), so the grid sets the resolution of the reported design. """
    gs = GSC if gs is None else gs
    row = pd.read_csv(os.path.join(REPO, 'results', 'calibration',
                                   'US_rhoGridCommonX.csv' if commonX else 'US_rhoGrid.csv'))
    row = row.loc[(row['ρ'] - ρ).abs() < 1e-9].iloc[-1]
    m = ModelESC(pars = testmod.pars | {'ρ': float(ρ), 'β': float(row['β']), 'ω': float(row['ω'])},
                 wedge = wedge, nθCandCRRA = nθCandCRRA, nθCand2D = nθCand2D, commonX = commonX,
                 **testmod.kwargs)
    m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
    m.CRRA.initGS(gs)
    m.LOG.initGS({k: v for k, v in gs.items() if k != 'ns'})
    return m


def franceRowCRRA(m, ρ, spec, phi, p, hbarRef, commonX = False, gs = None):
    """ runESC.franceRow at rho != 1: France's own calibrated equilibrium at 2020 under the same wedge,
    exogenous theta, in escShocksCRRA's row schema. See runESC.franceRow for what the row means and why
    its workweek is a target rather than a prediction. Exogenous theta, so the row is method-free; the
    caller stamps the method it is filed under. """
    mFR = buildEU('FR', {'spec': spec, 'phi': phi, 'p': p}, ρ = ρ, commonX = commonX)
    mFR.CRRA.initGS(GSC if gs is None else gs)
    mFR.calibrate(preferences = 'CRRA')
    pos = mFR.db['t0']
    out = mFR.solvePEE_CRRA()
    ww = float(m.db['workweek'])
    r0 = escReadout(mFR, out['τ'], out['report'], hbarRef, pos, workweekData = ww)
    r1 = escReadout(mFR, out['τ'], out['report'], hbarRef, pos+1, workweekData = ww)
    θ = mFR.db['θ'].values.astype(float)
    return {'ρ': ρ, 'spec': spec, 'phi': phi, 'commonX': commonX, 'p': p, 'scenario': 'France',
            'θpinned': True,
            'θ_tm1': float(θ[pos-1]), 'θ_t0': float(θ[pos]), 'θ_t1': float(θ[pos+1]),
            'τ_t0': r0['τ'], 'sr_t0': r0['sr'], 'ww_t0': r0['workweek'],
            'τ_t1': r1['τ'], 'sr_t1': r1['sr'], 'ww_t1': r1['workweek']}


def stagePermanentCRRA(ρs, specs, phis, out, wedgeP = None, nCand = 21, commonX = False):
    """ The permanent choice under CRRA, traced in rho.

    This is where the permanent timing turns out to be fragile in a way the appendix does not report. With
    no wedge the objective is essentially MONOTONE in theta, so the choice is always a corner -- and WHICH
    corner flips inside the paper's own rho range: theta = 0 for rho <~ 1.3 (the appendix's result, found
    at rho = 1) and theta = 1 above it. The gaps W(0) - W(1) are recorded so the flatness is visible rather
    than inferred from the argmax alone.

    theta_perm is the anticipated vote's fixed point (modelESC.solvePermanent's default); the unanticipated
    reading is recorded beside it. Every row here is a corner, where the two cannot differ -- which is
    exactly the case finding #10 warns about, so the column is kept to make that visible."""
    rows = []
    for ρ in ρs:
        for spec in specs:
            for phi in phis:
                w = None if wedgeP is None else {'spec': spec, 'phi': phi, 'p': wedgeP}
                for label, wedge in (('none', None), ('calibrated', w)):
                    if wedge is None and label == 'calibrated':
                        continue
                    try:
                        m = buildUS(ρ, wedge, nθCandCRRA = 13, commonX = commonX)
                        m.ESCPC.nθCand = nCand
                        m.ESCPC.θCand = np.linspace(0., 1., nCand)
                        m.calibrate()
                        pref = 'LOG' if ρ == 1.0 else 'CRRA'
                        tic = time.time()
                        r = m.solvePermanent(pref, verbose = False)
                        W = np.asarray(r['W'], dtype = float)
                        W = W - np.nanmax(W)
                        rows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'commonX': commonX,
                                     'wedge': label,
                                     'p': np.nan if wedge is None else wedge['p'],
                                     'θStar': float(m.db['θ'].xs(m.t0Year)), 'θPerm': r['θ'],
                                     'atBound': r['atBound'], 'W0gap': W[0], 'W1gap': W[-1],
                                     'converged': r['converged'],
                                     'θPermIncumbent': r['θIncumbent'],
                                     'τAtChoice': r['τAtChoice']})
                        print('  rho={:<5} {:<6} wedge={:<11} θ_perm={:.4f}  corner={:<5} '
                              'W(0)-max={:+.5f} W(1)-max={:+.5f}  [{:.0f}s]'.format(
                                  ρ, spec, label, r['θ'], str(r['atBound']), W[0], W[-1], time.time()-tic))
                    except Exception as e:
                        print('  rho={} {} {} FAILED {}: {}'.format(ρ, spec, label, type(e).__name__, e))
                    pd.DataFrame(rows).to_csv(out, index = False)
    return pd.DataFrame(rows)


def stageSequential(ρs, out, commonX = False, gs = None, nθ = 201):
    """ The costless sequential FOC on the solved no-wedge baseline at every non-terminal dated period
    (position 0 has no predetermined ratio). One row per (rho, pos): the largest and smallest value over
    the theta grid and whether it is negative throughout -- the corner claim is `negative` at every row. """
    rows, θg = [], np.linspace(0., 1., nθ)
    for ρ in ρs:
        m = buildUS(ρ, None, commonX = commonX, gs = gs)
        m.calibrate()
        sol = m.solvePEE_LOG() if ρ == 1.0 else m.solvePEE_CRRA()
        dates = m.db['dates']
        for pos in range(1, len(m.db['t']) - 1):
            foc = m.sequentialFOC(θg, sol, pos = pos)
            k = int(np.argmax(foc))
            rows.append({'ρ': ρ, 'commonX': commonX, 'pos': pos,
                         'date': dates[pos] if pos < len(dates) else np.nan,
                         'τ': float(np.asarray(sol['τ'])[pos]),
                         'focMax': float(foc[k]), 'θAtMax': float(θg[k]), 'focMin': float(np.min(foc)),
                         'negative': bool(np.all(foc < 0.))})
            print('  rho={:<4} pos={} ({}): max FOC {:+.4e} at θ={:.3f}, min {:+.4e}  -> {}'.format(
                ρ, pos, rows[-1]['date'], foc[k], θg[k], np.min(foc),
                'negative throughout' if rows[-1]['negative'] else 'NOT NEGATIVE'))
        mergeWrite(out, rows, ['ρ', 'commonX', 'pos'])
    return pd.DataFrame(rows)


def readCalibratedP(fCal, ρ, spec, phi, commonX, method):
    """ The calibrated p for this (rho, spec, phi, variant) from the csv, at `method` if such a row exists.
    An exact run with no exact row yet falls back to the path-iteration p with a printed warning -- the
    two agree to ~0.01 in the design, so it is a serviceable stand-in for a smoke run, not for the paper
    (the pipeline runs calib first). NaN when nothing matches. """
    if not os.path.exists(fCal):
        return np.nan, None
    hit = pd.read_csv(fCal)
    hit = hit[(hit['ρ'] == ρ) & (hit['spec'] == spec) & (hit['phi'] == phi)]
    if 'commonX' in hit.columns:
        hit = hit[hit['commonX'].astype(bool) == bool(commonX)]
    if 'method' not in hit.columns:
        hit = hit.assign(method = 'path')
    hit['method'] = hit['method'].fillna('path')
    own = hit[hit['method'] == method]
    if not own.empty:
        return float(own.iloc[-1]['p']), method
    if method == 'exact' and not hit.empty:
        return float(hit.iloc[-1]['p']), str(hit.iloc[-1]['method'])
    return np.nan, None


def pathRowsFrom(m, led, base, ρ, spec, phi, pCal, commonX, method):
    """ escPathCRRA rows from a solved design path (solveLeadedCRRA or solveLeaded2D return). """
    t0 = m.t0Year
    hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
    dates = m.db['dates']
    rows = []
    for pos, t in enumerate(m.db['t'][:-1]):
        r = sh.readout(m, led['out']['τ'] if 'out' in led else led['τ'],
                       led['out']['report'] if 'out' in led else led['report'],
                       float(m.db['workweek']), hbarRef, pos = pos)
        rb = sh.readout(m, base['τ'], base['report'], float(m.db['workweek']), hbarRef, pos = pos)
        rows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'commonX': commonX, 'method': method,
                     'p': pCal, 'pos': pos,
                     'date': dates[pos] if pos < len(dates) else np.nan,
                     'ν': float(m.db['ν'].xs(t)), 'θ': float(led['θ'].xs(t)),
                     'τ': r['τ'], 'sr': r['sr'], 'workweek': r['workweek'],
                     'τExo': rb['τ'], 'srExo': rb['sr'],
                     'converged': led.get('converged', True), 'step': led.get('step', np.nan),
                     'τDrift': led['targetDrift']['τ'], 'RDrift': led['targetDrift']['R']})
    return rows


def main():
    p = argparse.ArgumentParser(description = 'Endogenous theta under CRRA.')
    p.add_argument('--rho', type = float, nargs = '*', default = [2.0])
    p.add_argument('--spec', nargs = '*', default = ['scale'])
    p.add_argument('--commonX', action = 'store_true',
                   help = 'the common-X calibration variant (the paper leads with it). Written as a '
                          'column and part of the merge key -- see runESC.mergeWrite.')
    p.add_argument('--phi', type = float, nargs = '*', default = [0.5])
    p.add_argument('--stage', nargs = '*', default = ['calib', 'path', 'sens', 'shocks'],
                   help = "add 'permanent' for the permanent-choice trace in rho, 'sequential' for the "
                          "costless sequential FOC")
    p.add_argument('--scenarios', nargs = '*',
                   default = ['baseline', 'acute', 'frIncome', 'frLeisure', 'frVoting', 'frBoth', 'frAll'],
                   help = 'shock stage scenarios; any key of runESC.SHOCKS_ESC plus "baseline"')
    p.add_argument('--exact', action = 'store_true',
                   help = 'solve the leaded choice with the exact 2-D recursion (LeadedCRRA2D) instead of '
                          'the path iteration; rows are written with method = "exact"')
    p.add_argument('--ns', type = int, default = GSC['ns'],
                   help = 'the CRRA savings-state grid (default {}); the 2-D recursion borrows it, and '
                          '50 is ~4x faster at no measurable cost in the choice'.format(GSC['ns']))
    p.add_argument('--nsScan', type = int, default = 50,
                   help = 'under --exact, the grid the wedge calibration SCANS on before refining at '
                          '--ns (the warm start; 0 = scan at --ns too)')
    p.add_argument('--nCand2D', type = int, default = 21,
                   help = 'under --exact, the candidate grid for θ_{t+1} (see buildUS)')
    # ONE bracket cannot serve every rho. The required cost falls steeply in the intertemporal
    # elasticity -- p is about 0.95, 0.41, 0.09 at rho = 0.5, 1, 2 -- so the old default [0.01, 0.6],
    # chosen for rho = 2, sits entirely BELOW the root at rho = 0.5 and the scan correctly reports no
    # crossing rather than returning a number. Spanning all three costs only scan nodes, so the default
    # spans them and nScan rises to keep the resolution per decade roughly what it was. Under --exact the
    # default is half..double the path iteration's p instead (readCalibratedP), each node being a full
    # recursion.
    p.add_argument('--bracket', type = float, nargs = 2, default = None)
    p.add_argument('--nScan', type = int, default = None, help = 'default 14 (path), 4 (exact)')
    p.add_argument('--xtol', type = float, default = None,
                   help = 'brentq tolerance on p; default 1e-6 (path), 2e-5 (exact)')
    p.add_argument('--nCand', type = int, default = 13)
    p.add_argument('--maxIter', type = int, default = 4)
    p.add_argument('--tag', default = '')
    a = p.parse_args()
    os.makedirs(OUTDIR, exist_ok = True)
    fCal = os.path.join(OUTDIR, f'escCalibrationCRRA{a.tag}.csv')
    fPath = os.path.join(OUTDIR, f'escPathCRRA{a.tag}.csv')
    fShk = os.path.join(OUTDIR, f'escShocksCRRA{a.tag}.csv')
    method = 'exact' if a.exact else 'path'
    gs = GSC | {'ns': a.ns}
    nScan = a.nScan if a.nScan is not None else (6 if a.exact else 14)
    xtol = a.xtol if a.xtol is not None else (2e-5 if a.exact else 1e-6)
    gsScan = gs | {'ns': a.nsScan} if (a.exact and a.nsScan > 0) else gs
    print('method = {}, ns = {}{}'.format(method, a.ns, f', scan at ns = {a.nsScan}' if a.exact else ''))

    if 'permanent' in a.stage:
        print('=== the permanent choice under CRRA, traced in rho ===')
        stagePermanentCRRA(a.rho, a.spec, a.phi, os.path.join(OUTDIR, f'escPermanentCRRA{a.tag}.csv'),
                           commonX = a.commonX)
    if 'sequential' in a.stage:
        print('=== the costless sequential FOC on the no-wedge baseline ===')
        stageSequential(a.rho, os.path.join(OUTDIR, f'escSequentialCRRA{a.tag}.csv'),
                        commonX = a.commonX, gs = gs)
    if set(a.stage) <= {'permanent', 'sequential'}:
        print()
        print('-> {}'.format(os.path.relpath(OUTDIR, REPO)))
        return 0

    calRows, pathRows, shkRows = [], [], []
    frDataCache = {}
    for ρ in a.rho:
        for spec in a.spec:
            for phi in a.phi:
                tag = f'rho={ρ}, {spec}, phi={phi}'
                # ---------------------------------------------------- calibrate p
                pCal = np.nan
                if 'calib' in a.stage:
                    tic = time.time()
                    print(f'\n=== [{tag}] calibrating p under CRRA ({method}) ===')
                    bracket, nScanHere = a.bracket, nScan
                    if bracket is None:
                        bracket = (0.01, 3.0)
                        if a.exact:
                            # a path-iteration p on file narrows the scan; without one the wide bracket
                            # is scanned on the coarse grid, which is what --nsScan is for
                            pRef, from_ = readCalibratedP(fCal, ρ, spec, phi, a.commonX, 'path')
                            if np.isfinite(pRef):
                                bracket, nScanHere = (0.5*pRef, 2.0*pRef), min(nScan, 4)
                                print('  bracket {:.4f}..{:.4f} around the {} p = {:.4f}'.format(
                                    *bracket, from_, pRef))
                            else:
                                nScanHere = max(nScan, 14)
                                print('  no path-iteration p on file: full bracket, nScan = {}'
                                      .format(nScanHere))
                    m = buildUS(ρ, {'spec': spec, 'phi': phi, 'p': 0.2}, nθCandCRRA = a.nCand,
                                commonX = a.commonX, gs = gs, nθCand2D = a.nCand2D)
                    try:
                        rec = m.calibrateWedge(spec = spec, phi = phi,
                                               preferences = 'CRRA2D' if a.exact else 'CRRA',
                                               bracket = tuple(bracket), nScan = nScanHere, xtol = xtol,
                                               beforeScan = lambda: m.CRRA.initGS(gsScan),
                                               beforeRefine = lambda: m.CRRA.initGS(gs))
                        pCal = rec['p']
                        calRows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'commonX': a.commonX,
                                        'method': method, 'p': rec['p'],
                                        'converged': rec['converged'], 'θStar': rec['θ'],
                                        'residual': rec['residual'], 'message': rec['message'],
                                        'β': m.simpleβinv(), 'ω': float(m.db['ω'].xs(m.t0Year)),
                                        'ns': a.ns, 'nsScan': a.nsScan if a.exact else np.nan,
                                        'nCand2D': a.nCand2D if a.exact else np.nan,
                                        'nScan': len(rec['scan']),
                                        'seconds': time.time()-tic})
                        print('  -> p={}  ({})  [{:.0f}s]'.format(rec['p'], rec['message'], time.time()-tic))
                    except Exception as e:
                        print(f'  FAILED {type(e).__name__}: {e}')
                        calRows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'commonX': a.commonX,
                                        'method': method, 'p': np.nan,
                                        'converged': False, 'message': f'{type(e).__name__}: {e}'})
                    mergeWrite(fCal, calRows, KEYCAL)
                else:
                    # a --tag run without its own calibration reads the untagged one (smoke runs)
                    for fc in (fCal, os.path.join(OUTDIR, 'escCalibrationCRRA.csv')):
                        pCal, from_ = readCalibratedP(fc, ρ, spec, phi, a.commonX, method)
                        if np.isfinite(pCal):
                            break
                    if np.isfinite(pCal) and from_ != method:
                        print(f'  [{tag}] WARNING: no {method} calibration on file; using the {from_} '
                              f'p = {pCal:.6f} as a stand-in.')
                if not np.isfinite(pCal):
                    print(f'  [{tag}] no calibrated p -- skipping the remaining stages.')
                    continue

                # ---------------------------------------------------- the design path
                m = buildUS(ρ, {'spec': spec, 'phi': phi, 'p': pCal}, nθCandCRRA = a.nCand,
                            commonX = a.commonX, gs = gs, nθCand2D = a.nCand2D)
                m.calibrate()
                t0 = m.t0Year
                θStar = float(m.db['θ'].xs(t0))
                base = m.solvePEE_CRRA()
                hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
                ledBase = None          # the free path on the calibrated model: shared by path and shocks
                if 'path' in a.stage:
                    tic = time.time()
                    print(f'\n=== [{tag}] design path (p={pCal:.4f}, θ*={θStar:.4f}, {method}) ===')
                    try:
                        # pinAtT0 explicitly, not by default: the reported path is the free one, so that
                        # theta_{t0} is the equilibrium design the shocks stage and the tables read.
                        ledBase = (m.solveLeaded2D(pinAtT0 = False, verbose = True) if a.exact
                                   else m.solveLeadedCRRA(maxIter = a.maxIter, pinAtT0 = False))
                        pathRows += pathRowsFrom(m, ledBase, base, ρ, spec, phi, pCal, a.commonX, method)
                        print('  θ path: {}   (converged={}, {:.0f}s)'.format(
                            '  '.join('{:.4f}'.format(x) for x in ledBase['θ'].values[:7]),
                            ledBase.get('converged', True), time.time()-tic))
                        mergeWrite(fPath, pathRows, KEYPATH)
                    except Exception as e:
                        print(f'  path FAILED {type(e).__name__}: {e}')
                        ledBase = None

                # ---------------------------------------------------- the assumption, measured
                if 'sens' in a.stage and a.exact:
                    print('  sens: not applicable under --exact (the 2-D recursion assumes nothing '
                          'about the inherited design).')
                elif 'sens' in a.stage:
                    tic = time.time()
                    try:
                        θc = np.full(m.T, θStar)
                        sens = m.ESCC.stateSensitivity(θc, pos = m.db['t0'])
                        print('  stateSensitivity d(θ_t+2)/d(θ_t+1) = {:+.4f}  '
                              '(choice {:.4f} at θ={:.3f} vs {:.4f} at θ={:.3f})  [{:.0f}s]'.format(
                                  sens['slope'], sens['choiceLo'], sens['θLo'],
                                  sens['choiceHi'], sens['θHi'], time.time()-tic))
                        for r in calRows:
                            if (r['ρ'], r['spec'], r['phi']) == (ρ, spec, phi):
                                r['stateSlope'] = sens['slope']
                        if calRows:
                            mergeWrite(fCal, calRows, KEYCAL)
                    except Exception as e:
                        print(f'  sens FAILED {type(e).__name__}: {e}')

                # ---------------------------------------------------- counterfactuals
                if 'shocks' in a.stage:
                    pos0 = m.db['t0']
                    frData = None
                    if any(n.startswith('fr') for n in a.scenarios):
                        if ρ not in frDataCache:
                            print('  calibrating France at rho={} for the French scenarios ...'.format(ρ))
                            frDataCache[ρ] = frenchData(m, ρ, 'CRRA', gs = gs, commonX = a.commonX)
                        frData = frDataCache[ρ]
                    for name in a.scenarios:
                        for pin in (True, False):
                            tic = time.time()
                            try:
                                # New equilibrium path, as runESC.leadedNewPath: the shock holds over the
                                # whole horizon, the economy starts at its own steady state (no s0 seed),
                                # and the design is chosen from the first period when pin is False.
                                mt, _ = sh.shockedCopy(m, name, frData, SHOCKS_ESC) \
                                        if name != 'baseline' else (deepcopy(m), None)
                                if name == 'baseline':
                                    mt.x0, mt.LOG.x0, mt.CRRA.x0 = {}, {}, {}
                                if pin:
                                    θp = mt.db['θ'].values.astype(float)
                                    o = mt.solvePEE_CRRA(θ = θp, ε = mt.db['eps'].values.astype(float))
                                    θPath, out = pd.Series(θp, index = mt.db['t']), o
                                elif name == 'baseline' and ledBase is not None:
                                    θPath = ledBase['θ']          # the path stage already solved it
                                    out = ledBase['out'] if 'out' in ledBase else ledBase
                                elif a.exact:
                                    rec = mt.solveLeaded2D(pinAtT0 = False)
                                    θPath, out = rec['θ'], rec
                                else:
                                    rec = mt.solveLeadedCRRA(maxIter = a.maxIter, verbose = False,
                                                             pinAtT0 = False)
                                    θPath, out = rec['θ'], rec['out']
                                r0 = sh.readout(mt, out['τ'], out['report'], float(mt.db['workweek']),
                                                hbarRef, pos = pos0)
                                r1 = sh.readout(mt, out['τ'], out['report'], float(mt.db['workweek']),
                                                hbarRef, pos = pos0+1)
                                shkRows.append({'ρ': ρ, 'spec': spec, 'phi': phi,
                                                'commonX': a.commonX, 'method': method, 'p': pCal,
                                                'scenario': name, 'θpinned': pin,
                                                'θ_tm1': float(θPath.iloc[pos0-1]),
                                                'θ_t0': float(θPath.iloc[pos0]),
                                                'θ_t1': float(θPath.iloc[pos0+1]),
                                                'τ_t0': r0['τ'], 'sr_t0': r0['sr'], 'ww_t0': r0['workweek'],
                                                'τ_t1': r1['τ'], 'sr_t1': r1['sr'], 'ww_t1': r1['workweek']})
                                print('  {:<9} pin={:<5} θ_t0={:.4f}  τ_t0={:.4f} sr_t0={:.4f} '
                                      'ww_t0={:.2f}  (θ_t1={:.4f}, {:.0f}s)'.format(
                                          name, str(pin), float(θPath.iloc[pos0]), r0['τ'], r0['sr'],
                                          r0['workweek'], float(θPath.iloc[pos0+1]), time.time()-tic))
                                mergeWrite(fShk, shkRows, KEYSHK)
                            except Exception as e:
                                print(f'  {name} pin={pin} FAILED {type(e).__name__}: {e}')

                    # France's own calibrated path at this rho -- the endpoint the French-characteristics
                    # rows are read against (runESC.franceRow's CRRA counterpart, exogenous theta).
                    try:
                        tic = time.time()
                        f = franceRowCRRA(m, ρ, spec, phi, pCal, hbarRef, commonX = a.commonX, gs = gs)
                        f['method'] = method
                        shkRows.append(f)
                        print('  {:<9} pin={:<5} θ_t0={:.4f}  τ_t0={:.4f} sr_t0={:.4f} ww_t0={:.2f}'
                              '  [{:.0f}s]'.format('France', 'True', f['θ_t0'], f['τ_t0'], f['sr_t0'],
                                                   f['ww_t0'], time.time()-tic))
                        mergeWrite(fShk, shkRows, KEYSHK)
                    except Exception as e:
                        print(f'  France FAILED {type(e).__name__}: {e}')
    print('\n-> {}'.format(os.path.relpath(OUTDIR, REPO)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
