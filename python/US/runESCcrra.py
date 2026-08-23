r""" Endogenous system characteristics under CRRA: calibrate the wedge at rho != 1, solve the design path,
and run the ageing counterfactual.

Run:  .venv\Scripts\python.exe python\US\runESCcrra.py                       # rho = 2, both specs, phi=.5
      ... --rho 2.0 0.5  --spec scale flat  --phi 0.5
      ... --stage calib path shocks sens

Why this is a separate driver from runESC.py: under CRRA nothing about the leaded choice is cheap. The tau
FOC depends on s_{t-1}, so there is no static tauPolicy(theta); W_t is not additively separable, so the
choice depends on both states; and every candidate design costs a full solvePEE_CRRA (~3 s) instead of a
closed form. LeadedCRRA therefore iterates on the PATH and this file budgets for it:

    calibrate p     ~70 s per trial value  (a 35 s recalibration of (beta, omega) + 13 candidate solves)
    the design path ~2 min per iteration
    each shock      one path solve per reading

STAGES
  calib   p such that the leaded choice at t0 reproduces theta*, per (rho, spec, phi). The bracket is
          scanned an order of magnitude BELOW the LOG one: at rho = 2 the LOG-calibrated p = 0.402 already
          puts the choice at the theta = 1 corner, which is the same ordering the stake decomposition
          found (a higher EIS needs far less wedge to reach an interior choice).
  path    the full path iteration at the calibrated p, plus targetDrift.
  sens    stateSensitivity -- d(theta_{t+2})/d(theta_{t+1}), the quantity the path iteration assumes is
          zero. It IS zero under LOG (proved and measured); this reports what it is under CRRA. Any path
          result should be read next to this number.
  shocks  ageing (mild, acute), theta pinned vs chosen, reported at t0 and t0+1.
"""
import os, sys, argparse, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)

import test as testmod
import shocks as sh
from modelESC import ModelESC

OUTDIR = os.path.join(REPO, 'results', 'esc')
GSC = {'n': 101, 'ns': 150, 'smoothKnots': 4, 'interpKind': 'linear'}


def buildUS(ρ, wedge = None, nθCandCRRA = 13):
    row = pd.read_csv(os.path.join(REPO, 'results', 'calibration', 'US_rhoGrid.csv'))
    row = row.loc[(row['ρ'] - ρ).abs() < 1e-9].iloc[-1]
    m = ModelESC(pars = testmod.pars | {'ρ': float(ρ), 'β': float(row['β']), 'ω': float(row['ω'])},
                 wedge = wedge, nθCandCRRA = nθCandCRRA, **testmod.kwargs)
    m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
    m.CRRA.initGS(GSC)
    m.LOG.initGS({k: v for k, v in GSC.items() if k != 'ns'})
    return m


def stagePermanentCRRA(ρs, specs, phis, out, wedgeP = None, nCand = 21):
    """ The permanent choice under CRRA, traced in rho.

    This is where the permanent timing turns out to be fragile in a way the appendix does not report. With
    no wedge the objective is essentially MONOTONE in theta, so the choice is always a corner -- and WHICH
    corner flips inside the paper's own rho range: theta = 0 for rho <~ 1.3 (the appendix's result, found
    at rho = 1) and theta = 1 above it. The gaps W(0) - W(1) are recorded so the flatness is visible rather
    than inferred from the argmax alone. """
    rows = []
    for ρ in ρs:
        for spec in specs:
            for phi in phis:
                w = None if wedgeP is None else {'spec': spec, 'phi': phi, 'p': wedgeP}
                for label, wedge in (('none', None), ('calibrated', w)):
                    if wedge is None and label == 'calibrated':
                        continue
                    try:
                        m = buildUS(ρ, wedge, nθCandCRRA = 13)
                        m.ESCPC.nθCand = nCand
                        m.ESCPC.θCand = np.linspace(0., 1., nCand)
                        m.calibrate()
                        pref = 'LOG' if ρ == 1.0 else 'CRRA'
                        tic = time.time()
                        r = m.solvePermanent(pref, verbose = False)
                        W = np.asarray(r['W'], dtype = float)
                        W = W - np.nanmax(W)
                        rows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'wedge': label,
                                     'p': np.nan if wedge is None else wedge['p'],
                                     'θStar': float(m.db['θ'].xs(m.t0Year)), 'θPerm': r['θ'],
                                     'atBound': r['atBound'], 'W0gap': W[0], 'W1gap': W[-1],
                                     'τAtChoice': r['τAtChoice']})
                        print('  rho={:<5} {:<6} wedge={:<11} θ_perm={:.4f}  corner={:<5} '
                              'W(0)-max={:+.5f} W(1)-max={:+.5f}  [{:.0f}s]'.format(
                                  ρ, spec, label, r['θ'], str(r['atBound']), W[0], W[-1], time.time()-tic))
                    except Exception as e:
                        print('  rho={} {} {} FAILED {}: {}'.format(ρ, spec, label, type(e).__name__, e))
                    pd.DataFrame(rows).to_csv(out, index = False)
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser(description = 'Endogenous theta under CRRA.')
    p.add_argument('--rho', type = float, nargs = '*', default = [2.0])
    p.add_argument('--spec', nargs = '*', default = ['scale', 'flat'])
    p.add_argument('--phi', type = float, nargs = '*', default = [0.5])
    p.add_argument('--stage', nargs = '*', default = ['calib', 'path', 'sens', 'shocks'],
                   help = "add 'permanent' for the permanent-choice trace in rho")
    p.add_argument('--bracket', type = float, nargs = 2, default = [0.01, 0.6])
    p.add_argument('--nScan', type = int, default = 10)
    p.add_argument('--nCand', type = int, default = 13)
    p.add_argument('--maxIter', type = int, default = 4)
    p.add_argument('--tag', default = '')
    a = p.parse_args()
    os.makedirs(OUTDIR, exist_ok = True)
    fCal = os.path.join(OUTDIR, f'escCalibrationCRRA{a.tag}.csv')
    fPath = os.path.join(OUTDIR, f'escPathCRRA{a.tag}.csv')
    fShk = os.path.join(OUTDIR, f'escShocksCRRA{a.tag}.csv')

    if 'permanent' in a.stage:
        print('=== the permanent choice under CRRA, traced in rho ===')
        stagePermanentCRRA(a.rho, a.spec, a.phi, os.path.join(OUTDIR, f'escPermanentCRRA{a.tag}.csv'))
        if a.stage == ['permanent']:
            print()
            print('-> {}'.format(os.path.relpath(OUTDIR, REPO)))
            return 0

    calRows, pathRows, shkRows = [], [], []
    for ρ in a.rho:
        for spec in a.spec:
            for phi in a.phi:
                tag = f'rho={ρ}, {spec}, phi={phi}'
                # ---------------------------------------------------- calibrate p
                pCal = np.nan
                if 'calib' in a.stage:
                    tic = time.time()
                    print(f'\n=== [{tag}] calibrating p under CRRA ===')
                    m = buildUS(ρ, {'spec': spec, 'phi': phi, 'p': 0.2}, nθCandCRRA = a.nCand)
                    try:
                        rec = m.calibrateWedge(spec = spec, phi = phi, preferences = 'CRRA',
                                               bracket = tuple(a.bracket), nScan = a.nScan)
                        pCal = rec['p']
                        calRows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'p': rec['p'],
                                        'converged': rec['converged'], 'θStar': rec['θ'],
                                        'residual': rec['residual'], 'message': rec['message'],
                                        'β': m.simpleβinv(), 'ω': float(m.db['ω'].xs(m.t0Year)),
                                        'seconds': time.time()-tic})
                        print('  -> p={}  ({})  [{:.0f}s]'.format(rec['p'], rec['message'], time.time()-tic))
                    except Exception as e:
                        print(f'  FAILED {type(e).__name__}: {e}')
                        calRows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'p': np.nan,
                                        'converged': False, 'message': f'{type(e).__name__}: {e}'})
                    pd.DataFrame(calRows).to_csv(fCal, index = False)
                else:
                    hit = pd.read_csv(fCal)
                    hit = hit[(hit['ρ'] == ρ) & (hit['spec'] == spec) & (hit['phi'] == phi)]
                    pCal = float(hit.iloc[0]['p']) if not hit.empty else np.nan
                if not np.isfinite(pCal):
                    print(f'  [{tag}] no calibrated p -- skipping the remaining stages.')
                    continue

                # ---------------------------------------------------- the design path
                m = buildUS(ρ, {'spec': spec, 'phi': phi, 'p': pCal}, nθCandCRRA = a.nCand)
                m.calibrate()
                t0 = m.t0Year
                θStar = float(m.db['θ'].xs(t0))
                if 'path' in a.stage:
                    tic = time.time()
                    print(f'\n=== [{tag}] design path (p={pCal:.4f}, θ*={θStar:.4f}) ===')
                    try:
                        led = m.solveLeadedCRRA(maxIter = a.maxIter)
                        base = m.solvePEE_CRRA()
                        hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
                        dates = m.db['dates']
                        for pos, t in enumerate(m.db['t'][:-1]):
                            r = sh.readout(m, led['out']['τ'], led['out']['report'],
                                           float(m.db['workweek']), hbarRef, pos = pos)
                            rb = sh.readout(m, base['τ'], base['report'],
                                            float(m.db['workweek']), hbarRef, pos = pos)
                            pathRows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'p': pCal, 'pos': pos,
                                             'date': dates[pos] if pos < len(dates) else np.nan,
                                             'ν': float(m.db['ν'].xs(t)), 'θ': float(led['θ'].xs(t)),
                                             'τ': r['τ'], 'sr': r['sr'], 'workweek': r['workweek'],
                                             'τExo': rb['τ'], 'srExo': rb['sr'],
                                             'converged': led['converged'], 'step': led['step'],
                                             'τDrift': led['targetDrift']['τ'],
                                             'RDrift': led['targetDrift']['R']})
                        print('  θ path: {}   (converged={}, {:.0f}s)'.format(
                            '  '.join('{:.4f}'.format(x) for x in led['θ'].values[:7]),
                            led['converged'], time.time()-tic))
                        pd.DataFrame(pathRows).to_csv(fPath, index = False)
                    except Exception as e:
                        print(f'  path FAILED {type(e).__name__}: {e}')

                # ---------------------------------------------------- the assumption, measured
                if 'sens' in a.stage:
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
                        pd.DataFrame(calRows).to_csv(fCal, index = False)
                    except Exception as e:
                        print(f'  sens FAILED {type(e).__name__}: {e}')

                # ---------------------------------------------------- counterfactuals
                if 'shocks' in a.stage:
                    base = m.solvePEE_CRRA()
                    hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
                    seed = m.stateAtT0(base['report'], t0)
                    for name in ('baseline', 'mild', 'acute'):
                        for pin in (True, False):
                            tic = time.time()
                            try:
                                mt = m.createCopyFromt0(t0)
                                if name != 'baseline':
                                    sh.SHOCKS[name][1](mt, None)
                                if pin:
                                    θp = mt.db['θ'].values.astype(float)
                                    o = mt.solvePEE_CRRA(θ = θp, ε = mt.db['eps'].values.astype(float),
                                                         **seed)
                                    θPath, out = pd.Series(θp, index = mt.db['t']), o
                                else:
                                    rec = mt.solveLeadedCRRA(s0 = seed['s0'], maxIter = a.maxIter,
                                                             verbose = False)
                                    θPath, out = rec['θ'], rec['out']
                                r0 = sh.readout(mt, out['τ'], out['report'], float(mt.db['workweek']),
                                                hbarRef, pos = 0)
                                r1 = sh.readout(mt, out['τ'], out['report'], float(mt.db['workweek']),
                                                hbarRef, pos = 1)
                                shkRows.append({'ρ': ρ, 'spec': spec, 'phi': phi, 'p': pCal,
                                                'scenario': name, 'θpinned': pin,
                                                'θ_t0': float(θPath.iloc[0]), 'θ_t1': float(θPath.iloc[1]),
                                                'θ_t2': float(θPath.iloc[2]),
                                                'τ_t0': r0['τ'], 'sr_t0': r0['sr'], 'ww_t0': r0['workweek'],
                                                'τ_t1': r1['τ'], 'sr_t1': r1['sr'], 'ww_t1': r1['workweek']})
                                print('  {:<9} pin={:<5} θ_t1={:.4f}  τ_t0={:.4f} τ_t1={:.4f} sr_t1={:.4f}'
                                      '  [{:.0f}s]'.format(name, str(pin), float(θPath.iloc[1]),
                                                           r0['τ'], r1['τ'], r1['sr'], time.time()-tic))
                                pd.DataFrame(shkRows).to_csv(fShk, index = False)
                            except Exception as e:
                                print(f'  {name} pin={pin} FAILED {type(e).__name__}: {e}')
    print('\n-> {}'.format(os.path.relpath(OUTDIR, REPO)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
