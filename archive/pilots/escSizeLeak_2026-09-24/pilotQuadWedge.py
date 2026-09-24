r""" PILOT (scratchpad only, nothing in the repo is modified): the leaded choice of theta at rho = 1 under a
deadweight cost that scales with the redistribution actually performed, instead of the paper's f(theta)
= phi + (1-phi) theta^p, which burns a fixed share of revenue at a given theta whatever the income
distribution.

    'quad'      f(theta) = exp( -1/2 * p * V * (1-theta)^2 ),   V = sum_i gamma_i (y_i - 1)^2,
                y_i = eta_i^(1+xi)/X_i^xi / Gamma_h  (relative labour income, the model's hηRatio)
    'quadSize'  the same with p replaced by p * scale, scale = tau_bar(scenario)/tau_bar(US): the leak per
                unit of redistribution rises with the size of the system (a first pass at a cost that is
                convex in the implicit tax, without putting tau inside f).

Both are proportional (A = f theta, B = f (1-theta)), so f cancels from the replacement-rate ratio and
theta* = 0.738 is unchanged; p is calibrated exactly as in runESC.stageCalib (design in force at 2020 =
observed), with (beta, omega) recalibrated inside. Counterfactuals are runESC.leadedNewPath, i.e. the
paper's own construction (new equilibrium path, own steady state, choice binding from the first period).
"""
import os, sys, time, json
US = r'C:\Users\sxj477\documents\github\SSDclaude\python\US'
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, US)
import numpy as np, pandas as pd
from copy import deepcopy
import base as B
import runESC as R

sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)


def Vof(db):
    """ Between-type variance of relative labour income at t0, from the raw db (works for Base, BaseGrid
    and BaseTime alike, whose self(k, t) conventions differ). """
    t0 = db['t0']
    γ = db['γi'].iloc[t0].values.astype(float)
    η = db['ηi'].iloc[t0].values.astype(float)
    X = db['Xi'].iloc[t0].values.astype(float)
    ξ = float(db['ξ'].iloc[t0])
    a = η**(1+ξ)/X**ξ
    y = a/(γ*a).sum()
    return float((γ*(y-1)**2).sum())


_orig = B.Base.fWedge
def fWedge(self, θ):
    spec = self.db.get('wedgeSpec')
    if spec in ('quad', 'quadSize'):
        p = float(self.db['wedgeP'])
        scale = float(self.db.get('wedgeScale', 1.0)) if spec == 'quadSize' else 1.0
        V = Vof(self.db)
        return np.exp(-0.5*p*scale*V*(1-np.asarray(θ, dtype = float))**2)
    return _orig(self, θ)
B.Base.fWedge = fWedge


def main():
    tic0 = time.time()
    res = {'spec': 'quad', 'phi': 0.5}
    # ---------------------------------------------------------------- 1. calibrate p on the US
    m = R.buildUS({'spec': 'quad', 'phi': 0.5, 'p': 1.0}, ρ = 1.0, commonX = True)
    print('V_US =', round(Vof(m.db), 4))
    print('\n[quad] calibrating p ...')
    rec = m.calibrateWedge(spec = 'quad', phi = 0.5, bracket = (0.2, 60.0), nScan = 12)
    print('  ->', {k: rec[k] for k in ('p', 'residual', 'converged', 'θ', 'message')}, f'({time.time()-tic0:.0f}s)')
    res['calib'] = {k: (float(rec[k]) if k in ('p', 'residual', 'θ') else rec[k]) for k in ('p', 'residual', 'converged', 'θ', 'message')}
    res['calib']['scan'] = rec['scan']
    if not rec['converged']:
        json.dump(res, open(os.path.join(OUT, 'pilotQuad.json'), 'w'), indent = 1, default = str)
        return
    p = float(rec['p'])
    t0 = m.t0Year
    θq = np.linspace(0, 1, 11)
    print('  f(θ) on [0,1] at the US V:', np.round(m.B.fWedge(θq), 3))
    res['fUS'] = dict(zip(map(str, np.round(θq, 1)), np.round(m.B.fWedge(θq), 4).tolist()))
    res['calib'] |= {'β': float(m.simpleβinv()), 'ω': float(m.db['ω'].xs(t0))}

    # ---------------------------------------------------------------- 2. the design path (baseline)
    led = m.solveLeaded(pinAtT0 = False)
    res['path'] = {str(int(d)): float(v) for d, v in zip(m.db['dates'], np.asarray(led['θ']))}
    print('  design path:', {k: round(v, 4) for k, v in res['path'].items()})

    # ---------------------------------------------------------------- 3. counterfactuals, quad
    _, hbarRef = R.baselineRefs(m)
    data = R.frenchData(m, commonX = True)
    τUS = None
    rows = []
    for name in R.ESC_SCENARIOS:
        apply, d = (None, None) if name == 'baseline' else (R.SHOCKS_ESC[name][1], data)
        for pin in (True, False):
            tic = time.time()
            try:
                r = R.leadedNewPath(m, hbarRef, apply, d, pin = pin)
            except Exception as e:
                print(f'  {name:<10} pin={pin}: FAILED {type(e).__name__}: {e}'); continue
            V = Vof(r['m'].db)
            rows.append({'spec': 'quad', 'scenario': name, 'θpinned': pin, 'V': V, 'scale': 1.0,
                         'θ_t0': r['θ0'], 'θ_t1': r['θ1'], 'τ_t0': r['t0']['τ'], 'sr_t0': r['t0']['sr'],
                         'ww_t0': r['t0']['workweek']})
            if name == 'baseline' and pin:
                τUS = r['t0']['τ']
            print('  quad     {:<10} pin={:<5} V={:.3f} θ_t0={:.4f} τ_t0={:.4f} sr={:.4f} ww={:.2f} ({:.0f}s)'
                  .format(name, str(pin), V, r['θ0'], r['t0']['τ'], r['t0']['sr'], r['t0']['workweek'], time.time()-tic))
        pd.DataFrame(rows).to_csv(os.path.join(OUT, 'pilotQuad_shocks.csv'), index = False)

    # ---------------------------------------------------------------- 4. counterfactuals, quadSize
    # scale = pinned tau_t0 of the scenario / pinned tau_t0 of the US baseline, both under 'quad'.
    pinned = {r['scenario']: r['τ_t0'] for r in rows if r['θpinned']}
    for name in R.ESC_SCENARIOS:
        if name not in pinned:
            continue
        scale = pinned[name]/τUS
        apply, d = (None, None) if name == 'baseline' else (R.SHOCKS_ESC[name][1], data)
        m2 = deepcopy(m)
        m2.db['wedgeSpec'], m2.db['wedgeScale'] = 'quadSize', scale
        tic = time.time()
        try:
            r = R.leadedNewPath(m2, hbarRef, apply, d, pin = False)
        except Exception as e:
            print(f'  {name:<10} quadSize: FAILED {type(e).__name__}: {e}'); continue
        rows.append({'spec': 'quadSize', 'scenario': name, 'θpinned': False, 'V': Vof(r['m'].db), 'scale': scale,
                     'θ_t0': r['θ0'], 'θ_t1': r['θ1'], 'τ_t0': r['t0']['τ'], 'sr_t0': r['t0']['sr'],
                     'ww_t0': r['t0']['workweek']})
        print('  quadSize {:<10} scale={:.3f} θ_t0={:.4f} τ_t0={:.4f} sr={:.4f} ww={:.2f} ({:.0f}s)'
              .format(name, scale, r['θ0'], r['t0']['τ'], r['t0']['sr'], r['t0']['workweek'], time.time()-tic))
        pd.DataFrame(rows).to_csv(os.path.join(OUT, 'pilotQuad_shocks.csv'), index = False)

    # ---------------------------------------------------------------- 5. the UK and France with the US p
    crows = []
    # the size of each system relative to the US's: the observed 2020 tax targets (workbooks; the same
    # numbers as results/paper/usCalibrationSummary.csv, column τ0)
    τObs = {'US': 0.1442857142857143, 'UK': 0.1185714285714286, 'FR': 0.2128571428571429}
    for country, grouping in (('UK', None), ('FR', None), ('UK', 'US')):
        label = country + (grouping or '')
        for spec in ('quad', 'quadSize'):
            tic = time.time()
            try:
                mEU = R.buildEU(country, {'spec': spec, 'phi': 0.5, 'p': p}, grouping = grouping, commonX = True)
                if spec == 'quadSize':
                    mEU.db['wedgeScale'] = τObs[country]/τObs['US']
                mEU.calibrate()
                tEU = mEU.t0Year
                τEU = float(mEU.solvePEE_LOG()['τ'].xs(tEU))
                sols = mEU.ESC.solveBackward()
                ch = mEU.leadedDesignAtT0(sols)
                crows.append({'spec': spec, 'country': label, 'p': p, 'scale': (τEU/τUS if spec == 'quadSize' else 1.0),
                              'V': Vof(mEU.db), 'θStar': float(mEU.db['θ'].xs(tEU)), 'choice': float(ch),
                              'ω': float(mEU.db['ω'].xs(tEU)), 'τ': τEU})
                print('  {:<8} {:<5} V={:.3f} scale={:.3f} θ*={:.4f} -> choice {:.4f}  τ={:.4f} ω={:.3f} ({:.0f}s)'
                      .format(spec, label, crows[-1]['V'], crows[-1]['scale'], crows[-1]['θStar'], ch, τEU, crows[-1]['ω'], time.time()-tic))
            except Exception as e:
                print(f'  {label} {spec} FAILED {type(e).__name__}: {e}')
            pd.DataFrame(crows).to_csv(os.path.join(OUT, 'pilotQuad_country.csv'), index = False)

    # ---------------------------------------------------------------- 6. the UK's own p under quad
    try:
        tic = time.time()
        mUK = R.buildEU('UK', {'spec': 'quad', 'phi': 0.5, 'p': p}, commonX = True)
        recUK = mUK.calibrateWedge(spec = 'quad', phi = 0.5, bracket = (0.2, 60.0), nScan = 10, verbose = False)
        res['UKown'] = {k: (float(recUK[k]) if k in ('p', 'residual', 'θ') else recUK[k]) for k in ('p', 'residual', 'converged', 'θ', 'message')}
        print('  UK own p under quad:', res['UKown'], f'({time.time()-tic:.0f}s)')
    except Exception as e:
        print(f'  UK own-p FAILED {type(e).__name__}: {e}')

    json.dump(res, open(os.path.join(OUT, 'pilotQuad.json'), 'w'), indent = 1, default = str)
    print(f'\ndone in {time.time()-tic0:.0f}s')


if __name__ == '__main__':
    main()
