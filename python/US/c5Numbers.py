r""" Numbers for the review response (package C5): the U.S. block at the pension-only calibration, read off the
calibrated csvs and, where a number needs a solve, the same builders and solvers the paper's drivers use.

Run:  .venv\Scripts\python.exe python\US\c5Numbers.py <command> [--rho ...]

  selfcheck   the calibrated U.S. reproduced from its csv rows: the 2020 tax and the theta = 1 counterfactual at
              rho = 1 (runShocksUS's path) and the design in force in 2020 at the calibrated lambda (runESC's).
  a1          prop:esc:corner's condition under CRRA-GHH (app:esc:corner): the sign of
              sum_i gamma_i mu_i (y_i - 1) D_i^{-1/rho} over theta_t in [0, 1], D_i of eq:esc:corner:c2 with the
              inherited shares of eq:si_s (B_t for beta), at the calibrated equilibrium at every date. The
              critical turnout-weight ratio mu_H/mu_L at which the Beveridgean corner first fails, for weights
              mu_i = y_i^k and mu_i = (mu_i^CPS)^m, and the pairwise bound (D_H/D_L)^{1/rho} at theta_t = 0.
              -> C5_criticalTurnout.csv
  a9          every counterfactual of figure 6.1 (tax rate, full effect, p.p.) at every rho on file, ranked by
              size: results/shocks/{US,UK,UKUS}_shocksCommonX.csv and C5_US_shocksRhoGridCommonX.csv (the
              U.S. at the other rho of the sweep, runShocksUS.py --out). -> C5_ranking.csv
  loss        the share of revenue lost, 1 - f of eq:esc:budget, at theta* and below it, at each rho's calibrated
              cost (the paper's and the Pi-inclusive one), the 2020 tax held and, under log, re-solved
              (T_2020(theta)); and its derivative in theta at theta*. -> C5_marginalLoss.csv
  lambda      lambda against participation and taxable-income elasticities: lambda ~ eps Pi_t/R_t (the
              Harberger share of eq:esc:Vtilde's loss with the wedge eq:esc:implicitTax discounted at R_t), Pi
              and R in 2020 on each rho's no-cost baseline; the implied eps and the multiples of the 0.1-0.4
              range. -> C5_lambdaElasticity.csv
  index       design changes in index units, I = 1/(2 - theta), the ratio of replacement rates at mean and half
              mean earnings under eq:model:governmentBudget. -> C5_indexUnits.csv
  design      eq:esc:leadFOC under log at the 1990 electorate's choice of theta_2020 (prop:esc:separability:
              the choice maximises B_t(theta_{t+1}) alone), for the U.S. and France's income distribution, with
              the anticipated tax function T_{t+1} solved at every candidate: dB/dtheta_{t+1} at the U.S. choice
              by route (the design at a given loss share and tax; the loss share's dependence on the design,
              eq:esc:ftheta; the anticipated tax's response, T'_{t+1}) and by bloc (the retirees' labor stake;
              the young's hours; the young's pension and earnings, the bracket of tilde-c_{1,t}^i; R_{t+1}); the
              solver's design at finer design grids (nθ); and the design chosen when the cost keeps the U.S. size
              of the system (X1) or also its dispersion (X2), and the U.S. under the French dispersion in the
              cost (X3), through the Pi-inclusive slot at a fixed pi_t (tau^US_t/tau_t, times
              Vtilde_US/Vtilde_FR). -> C5_designDecomp.csv
  designCRRA  X1 and X2 under CRRA with the exact 2-D recursion (alg esc:crra2D) at --rho.
              -> C5_designDecompCRRA_rho<rho>.csv
  a13         tau_2020 against inherited capital s_2019 (the CRRA policy function of 2020, alg:CRRA:grid) at
              each rho. -> C5_taxPolicyState.csv
  strategic   the strategic term of the 2020 choice, dtau_2050/ds_2020 * ds_2020/dtau_2020 (the slope of the
              2050 policy function times the economic equilibrium's savings response). -> C5_strategicTerm.csv

Nothing here writes a csv the paper reads; every output is results/numerical/C5_*.csv.
"""
import os, sys, argparse, time, json
import numpy as np, pandas as pd
from copy import deepcopy
from scipy import optimize

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)

import test as testmod
import shocks as sh
from modelESC import ModelESC
from policyESC import LeadedBase
from runShocksUS import hostRow
import runShocksUS
import runESC
import runESCcrra

OUTDIR = os.path.join(REPO, 'results', 'numerical')
SHK = os.path.join(REPO, 'results', 'shocks')
ESC = os.path.join(REPO, 'results', 'esc')
RHOS = (0.5, 1.0, 2.0)
GS = {'n': 101, 'ns': 150, 'smoothKnots': 4, 'interpKind': 'linear'}   # runShocksUS / runESCcrra defaults
NCAND2D = 41                                                          # config.US['esc']['nCand2D']
THETA_STAR = 0.727757                                                 # the observed U.S. design (escCalibration)
EPS = (0.1, 0.25, 0.4)                     # Chetty et al. (2011), Saez, Slemrod and Giertz (2012); 0.25 extensive


def out(name):
    os.makedirs(OUTDIR, exist_ok = True)
    return os.path.join(OUTDIR, name)


def prefs(ρ):
    return 'LOG' if ρ == 1 else 'CRRA'


def usModel(ρ, cls = ModelESC):
    """ The no-cost U.S. at rho, common X, rebuilt from its sweep row as runShocksUS.hostModel does (ModelESC
    with no wedge is ModelUS exactly; it adds sequentialFOC). """
    row = hostRow(ρ, True, 'US')
    m = cls(pars = testmod.reading(None) | {'ρ': float(ρ), 'β': float(row['β']), 'ω': float(row['ω'])},
            commonX = True, **testmod.kwargs)
    m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
    gs = GS if ρ != 1 else {k: v for k, v in GS.items() if k != 'ns'}
    getattr(m, prefs(ρ)).initGS(gs)
    m.initProductivity_commonX(X = float(row['X']))
    m.updateAuxPars()
    return m, row


def escRows():
    """ The paper's cost calibration at each rho: (lambda, beta, omega) of 'size' and lambda of 'sizePiR', common
    X, at the pension-only theta* (LOG: escCalibration{,Costs}.csv; CRRA: the exact rows of
    escCalibrationCRRA{,Costs}.csv). """
    rows = {}
    c = pd.read_csv(os.path.join(ESC, 'escCalibration.csv'))
    cc = pd.read_csv(os.path.join(ESC, 'escCalibrationCosts.csv'))
    s = c[(c.spec == 'size') & c.commonX.astype(bool)].iloc[-1]
    q = cc[(cc.spec == 'sizePiR') & cc.commonX.astype(bool)].iloc[-1]
    rows[1.0] = {'λ': float(s.p), 'β': float(s['β']), 'ω': float(s['ω']), 'τ0': float(s['τ0']),
                 'Vtilde': float(s.Vtilde), 'θStar': float(s['θStar']), 'λΠR': float(q.p), 'ΠR': float(q['ΠR'])}
    c = pd.read_csv(os.path.join(ESC, 'escCalibrationCRRA.csv'))
    cc = pd.read_csv(os.path.join(ESC, 'escCalibrationCRRACosts.csv'))
    for ρ in (0.5, 2.0):
        s = c[(c['ρ'] == ρ) & (c.spec == 'size') & (c.method == 'exact') & c.commonX.astype(bool)
              & np.isclose(c['θStar'], THETA_STAR, atol = 1e-6)].iloc[-1]
        q = cc[(cc['ρ'] == ρ) & (cc.spec == 'sizePiR') & (cc.method == 'exact')].iloc[-1]
        rows[ρ] = {'λ': float(s.p), 'β': float(s['β']), 'ω': float(s['ω']), 'τ0': float(s['τ0']),
                   'Vtilde': float(s.Vtilde), 'θStar': float(s['θStar']), 'λΠR': float(q.p), 'ΠR': float(q['ΠR'])}
    return rows


def escModel(ρ, wedge):
    """ The U.S. under a cost at rho, (beta, omega, X) recalibrated with the cost installed: runESC.buildUS
    (log) or runESCcrra.buildUS (CRRA, the exact recursion's settings), then calibrate(), as the drivers'
    path and shocks stages do. """
    if ρ == 1:
        m = runESC.buildUS(wedge, ρ = 1.0, commonX = True)
    else:
        m = runESCcrra.buildUS(ρ, wedge, commonX = True, gs = GS, nθCand2D = NCAND2D)
    m.calibrate()
    return m


# ------------------------------------------------------------------------------------------------ selfcheck
def selfcheck(a):
    """ Two headline numbers from their own code paths: tau_2020 and the theta = 1 tax at rho = 1
    (US_shocksCommonX.csv), and theta_2020 = theta* at the calibrated lambda (escCalibration.csv). """
    shk = pd.read_csv(os.path.join(SHK, 'US_shocksCommonX.csv'))
    ref = shk[(shk['ρ'] == 1.0)]
    m, row = usModel(1.0)
    base = m.solvePEE_LOG()
    t0 = m.t0Year
    τ0 = float(base['τ'].xs(t0))
    mt, _ = sh.shockedCopy(m, 'theta1', None)
    τθ1 = float(mt.solvePEE_LOG()['τ'].xs(t0))
    τ0Ref = float(ref[ref.family == 'baseline']['τ'].iloc[0])
    τθ1Ref = float(ref[(ref.scenario == '$\\theta = 1$') & (ref.effect == 'full')]['τ'].iloc[0])
    print(f'rho=1 tau_2020 {τ0:.10f} vs csv {τ0Ref:.10f} (diff {τ0-τ0Ref:+.1e}); theta=1 tax {τθ1:.10f} vs csv '
          f'{τθ1Ref:.10f} (diff {τθ1-τθ1Ref:+.1e})')
    e = escRows()[1.0]
    tic = time.time()
    mE = escModel(1.0, {'spec': 'size', 'phi': 0.5, 'p': e['λ']})
    θ2020 = mE.leadedDesignAtT0()
    print(f"rho=1 lambda {e['λ']:.6f}: beta {mE.simpleβinv():.6f} vs {e['β']:.6f}, omega "
          f"{float(mE.db['ω'].xs(mE.t0Year)):.6f} vs {e['ω']:.6f}; theta_2020 {θ2020:.8f} vs theta* "
          f"{float(mE.db['θ'].xs(mE.t0Year)):.8f} ({time.time()-tic:.0f}s)")
    ok = (abs(τ0 - τ0Ref) < 1e-9 and abs(τθ1 - τθ1Ref) < 1e-9 and abs(θ2020 - THETA_STAR) < 1e-5
          and abs(mE.simpleβinv() - e['β']) < 1e-6)
    print('SELFCHECK', 'OK' if ok else 'FAILED')
    return 0 if ok else 1


# ------------------------------------------------------------------------------------------------ A1
def _sumAt(D, y, γ, μ, ρ):
    """ sum_i gamma_i mu_i (y_i - 1) D_i^{-1/rho} for D (nθ, ni): the sign of eq:esc:seqFOC under CRRA. """
    return ((γ*μ*(y - 1))[None, :]*D**(-1/ρ)).sum(axis = 1)


def _critical(D, y, γ, w, ρ, hi = 20.):
    """ The smallest k >= 0 with max_theta sum_i gamma_i w_i^k (y_i - 1) D_i^{-1/rho} >= 0 (bisection; the sum
    rises in k once w increases with income). NaN if none below `hi`. """
    f = lambda k: float(np.max(_sumAt(D, y, γ, w**k, ρ)))
    if f(0.) >= 0:
        return 0.
    if f(hi) < 0:
        return np.nan
    lo, up = 0., hi
    for _ in range(80):
        mid = 0.5*(lo + up)
        lo, up = (mid, up) if f(mid) < 0 else (lo, mid)
    return up


def a1(a):
    rows = []
    θg = np.linspace(0., 1., 2001)
    shk = pd.read_csv(os.path.join(SHK, 'US_shocksCommonX.csv'))
    for ρ in a.rho:
        tic = time.time()
        m, row = usModel(ρ)
        base = getattr(m, f'solvePEE_{prefs(ρ)}')()
        rep, B = base['report'], m.B
        τθ0 = float(shk[(shk['ρ'] == ρ) & (shk.scenario == '$\\theta = 0$') & (shk.effect == 'full')]['τ'].iloc[0])
        tIdx = m.db['t']
        for pos in range(1, len(tIdx) - 1):
            t, tLag = tIdx[pos], tIdx[pos-1]
            with B.cacheParams():
                α, p_, κ_ = float(B.get('α', t)), float(B.get('p[t-1]', t)), float(B.get('κ[t-1]', t))
                y = np.asarray(B.hηRatio(t, lag = '[t-1]'), dtype = float).ravel()
                γ = np.asarray(B.get('γi[t-1]', t), dtype = float).ravel()
                μ = np.asarray(B.get('μi[t-1]', t), dtype = float).ravel()
            si_ = rep['si_s'].xs(tLag).values.astype(float)
            τt = float(np.asarray(base['τ'])[pos])
            for τLabel, τUse in (('calibrated', τt), ('theta0', τθ0)):
                if τLabel == 'theta0' and pos != m.db['t0']:
                    continue
                coef = (1-α)/α*p_*τUse/κ_
                D = si_[None, :] + coef*(θg[:, None]*y[None, :] + (1 - θg[:, None]))
                S = _sumAt(D, y, γ, μ, ρ)
                iL, iH = int(np.argmin(y)), int(np.argmax(y))
                k = _critical(D, y, γ, y, ρ)
                mm = _critical(D, y, γ, μ, ρ)
                rows.append({'ρ': ρ, 'date': int(testmod.dates[pos]), 'pos': pos, 'tax': τLabel, 'τ': τUse,
                             'yL': y[iL], 'yM': float(np.median(y)), 'yH': y[iH], 'μL': μ[iL], 'μH': μ[iH],
                             'turnoutRatio': μ[iH]/μ[iL],
                             'cRatioθ0': D[0, iH]/D[0, iL], 'cRatioθStar': float(np.interp(THETA_STAR, θg, D[:, iH]/D[:, iL])),
                             'pairBoundθ0': (D[0, iH]/D[0, iL])**(1/ρ),
                             'maxSumObserved': float(S.max()), 'negativeEverywhere': bool(np.all(S < 0)),
                             'kCrit': k, 'ratioCrit_yk': (y[iH]/y[iL])**k if np.isfinite(k) else np.nan,
                             'mCrit': mm, 'ratioCrit_μm': (μ[iH]/μ[iL])**mm if np.isfinite(mm) else np.nan})
        # cross-check: the sum is ModelESC.sequentialFOC up to a positive factor at t0 (observed turnout)
        pos = m.db['t0']
        foc = m.sequentialFOC(θg[::100], base, pos = pos)
        r0 = [r for r in rows if r['ρ'] == ρ and r['pos'] == pos and r['tax'] == 'calibrated'][0]
        print(f"rho={ρ}: 2020 tau {r0['τ']:.6f}; y {r0['yL']:.4f}/{r0['yM']:.4f}/{r0['yH']:.4f}; turnout ratio "
              f"{r0['turnoutRatio']:.3f}; c_H/c_L at theta=0 {r0['cRatioθ0']:.4f}; critical ratio (y^k) "
              f"{r0['ratioCrit_yk']:.4f} (k={r0['kCrit']:.4f}), (mu^m) {r0['ratioCrit_μm']:.4f} (m={r0['mCrit']:.4f}); "
              f"pairwise bound {r0['pairBoundθ0']:.4f}; seqFOC<0 everywhere: {bool(np.all(foc < 0))}  "
              f"[{time.time()-tic:.0f}s]")
    df = pd.DataFrame(rows)
    df.to_csv(out('C5_criticalTurnout.csv'), index = False)
    print('->', os.path.relpath(out('C5_criticalTurnout.csv'), REPO))
    return 0


# ------------------------------------------------------------------------------------------------ A9
EFFECTS = [('acute ageing', 'Acute ageing'), ('mild ageing', 'Mild ageing'), ('design (θ 1→0)', None),
           ('θ = 0', '$\\theta = 0$'), ('θ = 1', '$\\theta = 1$'), ('income distribution', 'Income distribution'),
           ('voting', 'Voting'), ('leisure', 'Leisure preferences'), ('all French', 'All French characteristics')]
RANKED = ('ageing', 'design (θ 1→0)', 'income distribution', 'voting', 'leisure')


def a9(a):
    srcs = [('US', 'US_shocksCommonX.csv'), ('UK', 'UK_shocksCommonX.csv'), ('UKUS', 'UKUS_shocksCommonX.csv')]
    frames = []
    for host, f in srcs:
        d = pd.read_csv(os.path.join(SHK, f)).assign(host = host, source = 'results/shocks/' + f)
        frames.append(d)
    grid = out('C5_US_shocksRhoGridCommonX.csv')
    if os.path.exists(grid):
        g = pd.read_csv(grid).assign(host = 'US', source = 'results/numerical/C5_US_shocksRhoGridCommonX.csv')
        have = set(frames[0]['ρ'].round(6))
        frames.append(g[~g['ρ'].round(6).isin(have)])
        both = g[g['ρ'].round(6).isin(have)]
        if len(both):    # the grid run's rows at a rho also on file must reproduce it
            ref = frames[0].set_index(['ρ', 'scenario', 'effect'])['τ']
            chk = both.set_index(['ρ', 'scenario', 'effect'])['τ']
            print('grid run vs US_shocksCommonX.csv at shared rho: max|dtau| = {:.1e}'.format(
                float((chk - ref.reindex(chk.index)).abs().max())))
    d = pd.concat(frames, ignore_index = True)
    rows = []
    for (host, ρ), g in d.groupby(['host', 'ρ']):
        full = g[g.effect.isin(['full', 'baseline'])].set_index('scenario')['τ']
        b = float(full['Baseline'])
        eff = {}
        for name, scen in EFFECTS:
            if name == 'design (θ 1→0)':
                eff[name] = full['$\\theta = 0$'] - full['$\\theta = 1$']
            elif scen in full:
                eff[name] = full[scen] - b
        for ageing in ('acute ageing', 'mild ageing'):
            sizes = {k: abs(eff[ageing] if k == 'ageing' else eff[k]) for k in RANKED}
            order = sorted(sizes, key = lambda k: -sizes[k])
            for name, v in eff.items():
                key = 'ageing' if name == ageing else name
                rows.append({'host': host, 'ρ': ρ, 'ageingScenario': ageing.split()[0], 'effect': name,
                             'dτ_pp': 100*v, 'absdτ_pp': 100*abs(v),
                             'rank': order.index(key) + 1 if key in order else np.nan,
                             'baselineτ': b, 'source': g['source'].iloc[0]})
    df = pd.DataFrame(rows)
    df.to_csv(out('C5_ranking.csv'), index = False)
    acute = df[df.ageingScenario == 'acute']
    tab = acute.pivot_table(index = ['host', 'ρ'], columns = 'effect', values = 'dτ_pp')
    with pd.option_context('display.width', 250, 'display.max_columns', 20):
        print(tab.round(2).to_string())
    viol = []
    for (host, ρ), g in acute.groupby(['host', 'ρ']):
        r = g.set_index('effect')['rank']
        if not (r['acute ageing'] == 1 and r['design (θ 1→0)'] == 2):
            viol.append((host, ρ, dict(r.dropna().astype(int))))
    print('rho where "ageing first, design second" (acute) fails:', viol or 'none')
    print('->', os.path.relpath(out('C5_ranking.csv'), REPO))
    return 0


# ------------------------------------------------------------------------------------------------ #7
def _f(λπ, τ, V, θ):
    return np.exp(-0.5*λπ*τ*V*(1 - np.asarray(θ, dtype = float))**2)


def loss(a):
    rows = []
    e = escRows()
    T2020 = {}
    mE = escModel(1.0, {'spec': 'size', 'phi': 0.5, 'p': e[1.0]['λ']})
    t0 = mE.t0Year
    for θ in (THETA_STAR - 0.2, THETA_STAR - 0.1, THETA_STAR - 0.05, THETA_STAR, 0.):
        T2020[round(θ, 6)] = mE.ESC.τAt(t0, θ)          # T_2020(theta): the tax at the design in force
    for ρ in RHOS:
        r = e[ρ]
        for spec, λπ in (('size', r['λ']), ('sizePiR', r['λΠR']*r['ΠR'])):
            τ0, V, θs = r['τ0'], r['Vtilde'], r['θStar']
            base = {'ρ': ρ, 'spec': spec, 'λ': r['λ'] if spec == 'size' else r['λΠR'],
                    'π': 1. if spec == 'size' else r['ΠR'], 'τ0': τ0, 'Vtilde': V, 'θStar': θs}
            dθ = -_f(λπ, τ0, V, θs)*λπ*τ0*V*(1 - θs)          # d(1-f)/dtheta at theta*, tau held
            for dθd in (0., -0.05, -0.1, -0.2):
                θ = θs + dθd
                rows.append(base | {'Δθ': dθd, 'θ': θ, 'taxHeld': True, 'τ': τ0,
                                    'loss': 1 - _f(λπ, τ0, V, θ), 'lossθ0': 1 - _f(λπ, τ0, V, 0.),
                                    'dLoss_dθ_atθStar': dθ})
                if ρ == 1 and spec == 'size':
                    τθ = T2020[round(θ, 6)]
                    rows.append(base | {'Δθ': dθd, 'θ': θ, 'taxHeld': False, 'τ': τθ,
                                        'loss': 1 - _f(λπ, τθ, V, θ), 'lossθ0': 1 - _f(λπ, T2020[0.], V, 0.),
                                        'dLoss_dθ_atθStar': np.nan})
    df = pd.DataFrame(rows)
    df.to_csv(out('C5_marginalLoss.csv'), index = False)
    with pd.option_context('display.width', 250, 'display.max_columns', 20):
        print(df[['ρ', 'spec', 'λ', 'Δθ', 'taxHeld', 'τ', 'loss', 'dLoss_dθ_atθStar']].round(5).to_string())
    print('->', os.path.relpath(out('C5_marginalLoss.csv'), REPO))
    return 0


# ------------------------------------------------------------------------------------------------ #22
def ΠRAt(m, report, pos):
    """ Pi_t = nu_t w_t h_t/(w_{t-1} h_{t-1}) and R_t on a solved path at position pos >= 1. """
    t = m.db['t'][pos]
    w, h = report['w'].values.astype(float), report['h'].values.astype(float)
    Π = float(m.db['ν'].xs(t))*w[pos]*h[pos]/(w[pos-1]*h[pos-1])
    return Π, float(report['R'].values[pos])


def lam(a):
    rows = []
    e = escRows()
    for ρ in RHOS:
        m, _ = usModel(ρ)
        base = getattr(m, f'solvePEE_{prefs(ρ)}')()
        pos = m.db['t0']
        Π, R = ΠRAt(m, base['report'], pos)
        path = [ΠRAt(m, base['report'], p) for p in range(1, len(m.db['t']) - 1)]
        r = e[ρ]
        π = Π/R
        row = {'ρ': ρ, 'Π2020': Π, 'R2020': R, 'πBaseline2020': π, 'πSizePiR2020': r['ΠR'],
               'λ': r['λ'], 'λΠR': r['λΠR'], 'λΠR·π': r['λΠR']*r['ΠR'],
               'εImplied_paperΠ': r['λ']/Π, 'εImplied_ΠR': r['λ']/π, 'εImplied_ΠRcost': r['λΠR'],
               'πPath': json.dumps({int(testmod.dates[p]): round(x[0]/x[1], 5) for p, x in
                                    zip(range(1, len(m.db['t']) - 1), path)})}
        for ε in EPS:
            row[f'λ_ε{ε}_paperΠ'] = ε*Π
            row[f'λ_ε{ε}_ΠR'] = ε*π
            row[f'multiple_ε{ε}_paperΠ'] = r['λ']/(ε*Π)
            row[f'multiple_ε{ε}_ΠR'] = r['λ']/(ε*π)
            row[f'multiple_ε{ε}_ΠRcost'] = r['λΠR']/ε
        rows.append(row)
        print(f"rho={ρ}: Pi_2020 {Π:.4f} R_2020 {R:.4f} pi {π:.4f} (sizePiR path {r['ΠR']:.4f}); lambda "
              f"{r['λ']:.3f} -> eps {r['λ']/π:.2f} (paper's mapping {r['λ']/Π:.2f}); Pi-incl. lambda {r['λΠR']:.3f}; "
              f"multiples of 0.1-0.4: {r['λ']/(0.4*π):.0f}-{r['λ']/(0.1*π):.0f} (paper's {r['λ']/(0.4*Π):.0f}-"
              f"{r['λ']/(0.1*Π):.0f})")
    df = pd.DataFrame(rows)
    df.to_csv(out('C5_lambdaElasticity.csv'), index = False)
    print('->', os.path.relpath(out('C5_lambdaElasticity.csv'), REPO))
    return 0


# ------------------------------------------------------------------------------------------------ #13
def I(θ):
    return 1/(2 - np.asarray(θ, dtype = float))


def index(a):
    rows = []

    def add(item, ρ, θ0, θ1, source, reading = ''):
        rows.append({'item': item, 'ρ': ρ, 'reading': reading, 'θ0': θ0, 'θ1': θ1, 'Δθ': θ1 - θ0,
                     'I0': float(I(θ0)), 'I1': float(I(θ1)), 'ΔI': float(I(θ1) - I(θ0)),
                     'ΔI_firstOrder': float(I(θ0)**2*(θ1 - θ0)), 'source': source})

    add('observed U.S. design (level)', np.nan, THETA_STAR, THETA_STAR, 'results/esc/escCalibration.csv')
    add('Beveridgean corner vs U.S.', np.nan, THETA_STAR, 0., 'definition')
    add('Bismarckian corner vs U.S.', np.nan, THETA_STAR, 1., 'definition')
    add('theta 1 -> 0 (section 6)', np.nan, 1., 0., 'definition')
    # the design path, theta chosen (escPath LOG, escPathCRRA exact)
    p = pd.read_csv(os.path.join(ESC, 'escPath.csv'))
    p = p[(p.spec == 'size') & p.commonX.astype(bool)].set_index('date')['θ']
    pc = pd.read_csv(os.path.join(ESC, 'escPathCRRA.csv'))
    for ρ in RHOS:
        s = p if ρ == 1 else pc[(pc['ρ'] == ρ) & (pc.spec == 'size') & (pc.method == 'exact')].set_index('date')['θ']
        src = 'results/esc/escPath.csv' if ρ == 1 else 'results/esc/escPathCRRA.csv'
        for d in (2050, 2080, 2110):
            add(f'design path 2020 -> {d}', ρ, float(s[2020]), float(s[d]), src)
    # figure 7.1 and the A8 costs: theta_2020 chosen, against the chosen baseline of the same rho
    x = pd.read_csv(os.path.join(ESC, 'escExperiments.csv'))
    x = x[(x.spec == 'size') & x.commonX.astype(bool) & ((x.preferences == 'LOG') | (x.method == 'exact'))
          & ~x['θpinned'].astype(bool)]
    for ρ in RHOS:
        g = x[x['ρ'] == ρ].set_index('scenario')['θ_t0']
        for scen in ('acute', 'mild', 'frIncome', 'frVoting', 'frLeisure', 'frBoth', 'frAll'):
            if scen in g:
                add(f'{scen} (figure 7.1)', ρ, float(g['baseline']), float(g[scen]), 'results/esc/escExperiments.csv',
                    'chosen')
    c = pd.read_csv(os.path.join(ESC, 'escAgeingCosts.csv'))
    c = c[~c['θpinned'].astype(bool)]
    for _, r in c.iterrows():
        if r['scenario'] in ('mild', 'acute'):
            add(f"{r['scenario']} ageing, cost {r['spec']}", float(r['ρ']), float(r['θ_t0'] - r['dθ_t0']),
                float(r['θ_t0']), 'results/esc/escAgeingCosts.csv', 'chosen')
    # the UK and France under the U.S. lambda (appendix G.1), against their observed designs and the U.S.
    k = pd.read_csv(os.path.join(ESC, 'escCountry.csv'))
    k = k[(k.spec == 'size') & k.commonX.astype(bool) & (k.wedgeFrom == 'US')]
    for _, r in k.iterrows():
        add(f"{r['country']} under the U.S. lambda vs observed", 1.0, float(r['θStar']), float(r['choice']),
            'results/esc/escCountry.csv', 'chosen')
        add(f"{r['country']} under the U.S. lambda vs U.S. design", 1.0, THETA_STAR, float(r['choice']),
            'results/esc/escCountry.csv', 'chosen')
    # data: figure 1.1's index, the U.S. and the UK observed, and the cross-section's range
    f1 = pd.read_csv(os.path.join(REPO, 'data', 'oecdFigure1.csv')).set_index('iso3')['bbIndex']
    for iso in ('USA', 'GBR', 'FRA'):
        if iso in f1:
            θd = 2 - 1/float(f1[iso])
            add(f'{iso} figure 1.1 index (theta = 2 - 1/I)', np.nan, θd, θd, 'data/oecdFigure1.csv', 'data')
    add('figure 1.1 range (29 countries)', np.nan, max(0., 2 - 1/float(f1.min())), min(1., 2 - 1/float(f1.max())),
        'data/oecdFigure1.csv', 'data')
    df = pd.DataFrame(rows)
    df.to_csv(out('C5_indexUnits.csv'), index = False)
    with pd.option_context('display.width', 250, 'display.max_columns', 20, 'display.max_rows', 200):
        print(df[['item', 'ρ', 'θ0', 'θ1', 'Δθ', 'I0', 'I1', 'ΔI']].round(4).to_string())
    print('->', os.path.relpath(out('C5_indexUnits.csv'), REPO))
    return 0


# ------------------------------------------------------------------------------------------------ #5
class _FrozenF:
    """ Inside the block, f(theta_{t+1}, tau_{t+1}) of the young at the date `t` (lag '', eq:esc:AB) is
    evaluated at (θf, τf) wherever an argument is given, while the benefit formula keeps its own theta and
    tau: the derivative of W_t in theta_{t+1} then splits by route. Instance attribute on BG only. """
    def __init__(self, BG, t):
        self.BG, self.t, self.θf, self.τf = BG, t, None, None

    def __enter__(self):
        orig = type(self.BG).fWedge.__get__(self.BG)
        def fWedge(θ, τ = None, t = None, lag = ''):
            if lag == '' and t == self.t:
                θ = θ if self.θf is None else np.broadcast_to(self.θf, np.shape(θ))
                τ = τ if self.τf is None else np.broadcast_to(self.τf, np.shape(τ))
            return orig(θ, τ, t, lag)
        self.BG.fWedge = fWedge
        return self

    def __exit__(self, *exc):
        del self.BG.fWedge


def _pieces(mm, ctx, θ1, τ1, frozen = None):
    """ The theta_{t+1}-dependent part of W_t (eq:LOG:PolObj) at the electorate ctx['t'], in four pieces:
    the retirees' (1-alpha) ln h_t (their stake in labor supply), the young's (1+beta)(1+xi)/xi ln h_t (their
    hours), the young's (1+beta) ln of the bracket of tilde-c_{1,t}^i (own earnings and the pension), and the
    young's beta ln R_{t+1}. θ1, τ1: (M,). frozen: (θf, τf) for f's arguments or None. Returns {piece: (M,)}. """
    E, BG = mm.ESC, mm.BG
    t, tLag, t1 = ctx['t'], ctx['tLag'], ctx['t1']
    M = θ1.size
    cont = {'τ1': τ1, 'θ2': np.full(M, ctx['θ2']), 'τ2': np.full(M, ctx['τ2']), 'terminal1': False}
    with BG.cacheParams(), _FrozenF(BG, t) as fz:
        if frozen is not None:
            fz.θf, fz.τf = frozen
        W, parts = E.objective(t, tLag, t1, np.full(M, ctx['τt']), np.full(M, ctx['θt']), θ1, cont)
        old, young = E.weights(t)
        α, ξ = float(BG.get('α', t)), float(BG.get('ξ', t))
        β = np.asarray(BG.get('βi', t), dtype = float)
        lnh = np.log(parts['h'])
        tc1 = BG.tildec1i(parts['h'], β, τ1, θ1, parts['Γs'], t)
        hTerm = (1+ξ)/ξ*lnh[:, None]
        bracket = np.log(tc1) - hTerm                       # ln bracket - ln((1+B)Gamma_h^{(1+xi)/xi}), a constant
    return {'old: labor stake': float(np.sum(old))*(1-α)*lnh,
            'young: hours': (young*(1+β)*hTerm).sum(axis = -1),
            'young: pension and earnings': (young*(1+β)*bracket).sum(axis = -1),
            'young: R_{t+1}': (young*β*np.log(parts['R1'])[:, None]).sum(axis = -1),
            'W': W}


def _taxFn(mm, ctx):
    """ T_{t+1}(theta_{t+1}), the anticipated tax function of the next period, solved (not interpolated). """
    return lambda θ: mm.ESC.τOfθ(ctx['t1'], np.atleast_1d(np.asarray(θ, dtype = float)), ctx['t'],
                                 terminal = False)[0]


def _context(mm, sols, θPath, τPath):
    """ The 1990 electorate (position t0 - 1), which chooses theta_2020: its date and the continuation. """
    tIdx = mm.db['t']
    pos = mm.db['t0'] - 1
    t, tLag, t1, t2 = tIdx[pos], tIdx[pos-1], tIdx[pos+1], tIdx[pos+2]
    θ2 = float(np.interp(0.5, sols[t1]['θGrid'], sols[t1]['θNext']))           # state-free under log
    τ2 = float(np.interp(θ2, sols[t2]['θGrid'], sols[t2]['τ']))
    return {'t': t, 'tLag': tLag, 't1': t1, 'pos': pos, 'θt': float(θPath.iloc[pos]),
            'τt': float(τPath.iloc[pos]), 'θ2': θ2, 'τ2': τ2}


def _focRoutes(mm, ctx, θ0, T, δ = 1e-4):
    """ dW_t/dtheta_{t+1} at θ0 by central differences, total and by route, each split into _pieces:
    'design' (benefit formula's theta, f and tau_{t+1} held), 'cost' (f's theta argument alone, eq:esc:ftheta),
    'tax' (tau_{t+1} = T(theta) everywhere, f's tau included). T: the tax function used. """
    θpm = np.array([θ0 + δ, θ0 - δ])
    τ0 = float(T(θ0)[0])
    τpm = T(θpm)
    runs = {'total': (θpm, τpm, None),
            'design': (θpm, np.full(2, τ0), (θ0, τ0)),
            'cost': (np.full(2, θ0), np.full(2, τ0), None),           # f's theta varies: see below
            'tax': (np.full(2, θ0), τpm, None)}
    res = {}
    for route, (θ1, τ1, fr) in runs.items():
        if route == 'cost':
            P = {k: np.empty(2) for k in ('old: labor stake', 'young: hours', 'young: pension and earnings',
                                          'young: R_{t+1}', 'W')}
            for j in range(2):
                pj = _pieces(mm, ctx, θ1[j:j+1], τ1[j:j+1], frozen = (θpm[j], τ0))
                for k in P:
                    P[k][j] = pj[k][0]
        else:
            P = _pieces(mm, ctx, θ1, τ1, frozen = fr)
        res[route] = {k: float((v[0] - v[1])/(2*δ)) for k, v in P.items()}
    return res, τ0


def _argmaxW(mm, ctx, T, n = 121):
    """ The design the electorate at ctx chooses for t+1 when it anticipates the tax function T: argmax of W_t
    over theta_{t+1} on n nodes with the solvers' parabolic refinement (LeadedBase._argmax), then the zero of
    dW_t/dtheta_{t+1} next to it. """
    θg = np.linspace(0., 1., n)
    W = _pieces(mm, ctx, θg, T(θg))['W']
    θ0, atBound = LeadedBase._argmax(θg, W)
    if atBound:
        return θ0
    g = lambda θ: _focRoutes(mm, ctx, θ, T)[0]['total']['W']
    h = θg[1] - θg[0]
    lo, hi = max(θ0 - 2*h, 1e-6), min(θ0 + 2*h, 1 - 1e-6)
    return float(optimize.brentq(g, lo, hi, xtol = 1e-10)) if g(lo)*g(hi) < 0 else θ0


def _withCost(m, spec, scale, τTarget, solve, passes, tol):
    """ The model m (deepcopied) under 'sizePiR' at a FIXED pi_t (ModelESC._ΠRfrozen): pi_t = scale *
    tau^target_t / tau_t, so that lambda pi_t tau_t Vtilde = lambda scale tau^target_t Vtilde on the solved path,
    iterated `passes` times or until max |pi tau - scale tau^target|/(scale tau^target) < tol. τTarget None:
    pi = scale. solve(mX) -> {'θ', 'τ'}. Returns (solve's return, pi, gap, passes run). """
    mX = deepcopy(m)
    mX.x0, mX.LOG.x0, mX.CRRA.x0 = {}, {}, {}
    mX.setWedge(spec = spec, update = False)          # update = False: theta stays pinned (#9)
    mX._ΠRfrozen = True
    π = np.full(mX.T, float(scale))
    target = None if τTarget is None else scale*np.asarray(τTarget, dtype = float)
    k, gap, rec = 0, np.nan, None
    while k < passes:
        if target is not None:          # the tax of the last solve, or the caller's guess before the first
            π = target/np.asarray(rec['τ'] if rec is not None else m._c5TauGuess, dtype = float)
        mX.setΠR(π)
        rec = solve(mX)
        k += 1
        if target is None:
            gap = 0.
            break
        # the gap over every period but the terminal one, whose U.S. tax a CRRA caller only extrapolates
        τ = np.asarray(rec['τ'], dtype = float)
        gap = float(np.max(np.abs(π[:-1]*τ[:-1] - target[:-1])/target[:-1]))
        print(f'      pass {k}: theta_2020 {float(rec["θ"].iloc[mX.db["t0"]]):.6f}, max rel. gap in pi*tau {gap:.2e}')
        if gap < tol:
            break
    return rec, π, gap, k


def design(a):
    """ #5 under log (rho = 1). """
    rows = []
    e = escRows()[1.0]
    m = escModel(1.0, {'spec': 'size', 'phi': 0.5, 'p': e['λ']})
    data = runESC.frenchData(m, commonX = True)
    mFR = deepcopy(m)
    mFR.x0, mFR.LOG.x0, mFR.CRRA.x0 = {}, {}, {}
    runESC.SHOCKS_ESC['frIncome'][1](mFR, data)
    t0 = m.t0Year
    led = {k: mm.solveLeaded(pinAtT0 = False) for k, mm in (('US', m), ('FR', mFR))}
    V = {k: float(mm.B.Vtilde(t0)) for k, mm in (('US', m), ('FR', mFR))}
    csv = pd.read_csv(os.path.join(ESC, 'escExperiments.csv'))
    csv = csv[(csv.spec == 'size') & (csv.preferences == 'LOG') & ~csv['θpinned'].astype(bool)].set_index('scenario')
    for k, sc in (('US', 'baseline'), ('FR', 'frIncome')):
        print(f"{k}: theta_2020 {float(led[k]['θ'].xs(t0)):.6f} (csv {float(csv.loc[sc, 'θ_t0']):.6f}), tau_2020 "
              f"{float(led[k]['τ'].xs(t0)):.6f}, Vtilde {V[k]:.4f}")
    ctx = {k: _context(mm, led[k]['sols'], led[k]['θ'], led[k]['τ']) for k, mm in (('US', m), ('FR', mFR))}
    T = {k: _taxFn(mm, ctx[k]) for k, mm in (('US', m), ('FR', mFR))}

    # --- the choice with the anticipated tax function solved at every candidate rather than read off the
    # solver's piecewise-linear table over its 41-node design grid (LeadedLOG.solveBackward's τPolicy1)
    θHat = {k: _argmaxW(mm, ctx[k], T[k]) for k, mm in (('US', m), ('FR', mFR))}
    for k in θHat:
        rows.append({'kind': 'choice', 'ρ': 1.0, 'case': f'{k}, tax function solved at each candidate',
                     'experiment': f'{k}exactT', 'θ2020': θHat[k]})
    print(f"  theta_2020 with T solved at each candidate: U.S. {θHat['US']:.6f}, FR {θHat['FR']:.6f} "
          f"(response {θHat['FR']-θHat['US']:+.6f})")

    # --- the design condition at that U.S. choice, by route and bloc, for the U.S. and France's distribution
    for label, econ in (('US', 'US'), ('FR', 'FR')):
        mm = m if econ == 'US' else mFR
        res, τ1 = _focRoutes(mm, ctx[econ], θHat['US'], T[econ])
        for route, pc in res.items():
            for piece, v in pc.items():
                rows.append({'kind': 'foc', 'ρ': 1.0, 'case': label, 'route': route, 'piece': piece, 'value': v,
                             'θ1': θHat['US'], 'τ1': τ1, 'Vtilde': V[econ]})
        s = sum(res[r]['W'] for r in ('design', 'cost', 'tax'))
        print(f"  {label:<4} at theta {θHat['US']:.5f}: tau_2020 {τ1:.5f}  dW/dtheta total {res['total']['W']:+.6f} "
              f"(routes sum {s:+.6f}): design {res['design']['W']:+.6f}, cost {res['cost']['W']:+.6f}, "
              f"tax {res['tax']['W']:+.6f}")
        for piece in ('old: labor stake', 'young: hours', 'young: pension and earnings', 'young: R_{t+1}'):
            print('      {:<30} '.format(piece) + '  '.join(f'{r} {res[r][piece]:+.6f}' for r in res))

    # --- the solver's design grid: theta_2020 of the U.S. and France at finer tables (nθ), same lambda
    for nθ in (41, 81, 161, 321):
        mn = runESC.buildUS({'spec': 'size', 'phi': 0.5, 'p': e['λ']}, ρ = 1.0, nθ = nθ, commonX = True)
        mn.calibrate()
        mnFR = deepcopy(mn)
        mnFR.x0, mnFR.LOG.x0, mnFR.CRRA.x0 = {}, {}, {}
        runESC.SHOCKS_ESC['frIncome'][1](mnFR, data)
        θn = {k: mm.leadedDesignAtT0() for k, mm in (('US', mn), ('FR', mnFR))}
        rows.append({'kind': 'grid', 'ρ': 1.0, 'case': f'design grid nθ = {nθ}', 'experiment': f'nθ{nθ}',
                     'θ2020': θn['US'], 'θ2020FR': θn['FR']})
        print(f"  nθ = {nθ:>3}: theta_2020 U.S. {θn['US']:.6f}, FR {θn['FR']:.6f} (response {θn['FR']-θn['US']:+.6f})")

    # --- the design chosen under the cost re-scaled through the Pi-inclusive slot (equilibria)
    solveL = lambda mX: mX.solveLeaded(pinAtT0 = False)
    τUS = led['US']['τ'].values.astype(float)
    mFR._c5TauGuess = led['FR']['τ'].values.astype(float)
    m._c5TauGuess = τUS
    exps = [('US', m, 'baseline', 1., None, 'U.S.'),
            ('FR', mFR, 'frIncome', 1., None, 'FR (pi = 1, reproduces frIncome)'),
            ('X1', mFR, 'frIncome', 1., τUS, 'FR, cost at the U.S. size (pi = tau^US/tau)'),
            ('X2', mFR, 'frIncome', V['US']/V['FR'], τUS, 'FR, cost at the U.S. size and dispersion'),
            ('X3', m, 'baseline', V['FR']/V['US'], None, 'U.S., cost at the French dispersion')]
    for key, mm, sc, scale, τT, label in exps:
        rec, π, gap, k = _withCost(mm, 'sizePiR', scale, τT, solveL, passes = 30, tol = 1e-10)
        θ0, τ0 = float(rec['θ'].xs(t0)), float(rec['τ'].xs(t0))
        rows.append({'kind': 'choice', 'ρ': 1.0, 'case': label, 'experiment': key, 'θ2020': θ0, 'τ2020': τ0,
                     'π2020': float(π[m.db['t0']]), 'gap': gap, 'passes': k, 'θ2050': float(rec['θ'].iloc[m.db['t0']+1])})
        print(f'  {label:<48} theta_2020 {θ0:.6f}  tau_2020 {τ0:.6f}  pi_2020 {π[m.db["t0"]]:.5f}  ({k} passes)')
    pd.DataFrame(rows).to_csv(out('C5_designDecomp.csv'), index = False)
    print('->', os.path.relpath(out('C5_designDecomp.csv'), REPO))
    return 0


def designCRRA(a):
    """ #5 under CRRA (exact 2-D recursion): the design chosen in 2020 under France's income distribution when
    the cost keeps the U.S. size of the system (X1) and also its dispersion (X2), as in `design`. """
    for ρ in a.rho:
        rows = []
        e = escRows()[ρ]
        tic = time.time()
        m = escModel(ρ, {'spec': 'size', 'phi': 0.5, 'p': e['λ']})
        print(f'rho={ρ}: calibrated (beta {m.simpleβinv():.6f} vs {e["β"]:.6f}, omega '
              f'{float(m.db["ω"].xs(m.t0Year)):.6f} vs {e["ω"]:.6f})  [{time.time()-tic:.0f}s]')
        data = runShocksUS.frenchData(m, ρ, 'CRRA', gs = GS, commonX = True)
        mFR, _ = sh.shockedCopy(m, 'frIncome', data, runESC.SHOCKS_ESC)
        t0, pos0 = m.t0Year, m.db['t0']
        V = {'US': float(m.B.Vtilde(t0)), 'FR': float(mFR.B.Vtilde(t0))}
        # the U.S. free path's tax (escPathCRRA, exact) and a first guess for France's: its pinned path scaled
        # to the free 2020 value on file (escExperiments)
        pc = pd.read_csv(os.path.join(ESC, 'escPathCRRA.csv'))
        pc = pc[(pc['ρ'] == ρ) & (pc.spec == 'size') & (pc.method == 'exact')].sort_values('pos')
        τUS = np.append(pc['τ'].values.astype(float), pc['τ'].values[-1])          # terminal: last ratio
        x = pd.read_csv(os.path.join(ESC, 'escExperiments.csv'))
        x = x[(x['ρ'] == ρ) & (x.spec == 'size') & (x.method == 'exact')].set_index(['scenario', 'θpinned'])
        pinUS = m.solvePEE_CRRA()['τ'].values.astype(float)
        pinFR = mFR.solvePEE_CRRA()['τ'].values.astype(float)
        τUS = τUS if len(τUS) == m.T else pinUS*τUS[pos0]/pinUS[pos0]
        mFR._c5TauGuess = pinFR*float(x.loc[('frIncome', False), 'τ_t0'])/pinFR[pos0]
        print(f'  Vtilde US {V["US"]:.4f} FR {V["FR"]:.4f}; tau_2020 US free {τUS[pos0]:.6f}, FR guess '
              f'{mFR._c5TauGuess[pos0]:.6f}  [{time.time()-tic:.0f}s]')
        solve2D = lambda mX: mX.solveLeaded2D(pinAtT0 = False)
        for key, scale, label in (('X1', 1., 'FR, cost at the U.S. size (pi = tau^US/tau)'),
                                  ('X2', V['US']/V['FR'], 'FR, cost at the U.S. size and dispersion')):
            if a.only and key not in a.only:
                continue
            tic = time.time()
            rec, π, gap, k = _withCost(mFR, 'sizePiR', scale, τUS, solve2D, passes = a.passes, tol = 2e-3)
            θ0, τ0 = float(rec['θ'].iloc[pos0]), float(rec['τ'].iloc[pos0])
            mult = rec.get('multiplicity') or {}
            rows.append({'kind': 'choice', 'ρ': ρ, 'case': label, 'experiment': key, 'θ2020': θ0, 'τ2020': τ0,
                         'π2020': float(π[pos0]), 'gap': gap, 'passes': k,
                         'θ2050': float(rec['θ'].iloc[pos0+1]), 'nEqθMax': mult.get('nEqθMax'),
                         'nFallbackθ': mult.get('nFallbackθ')})
            print(f'  {label:<48} theta_2020 {θ0:.6f}  tau_2020 {τ0:.6f}  pi_2020 {π[pos0]:.5f}  ({k} passes, '
                  f'{time.time()-tic:.0f}s)')
            _mergeExperiments(rows, out(f'C5_designDecompCRRA_rho{ρ:g}.csv'))
    return 0


def _mergeExperiments(rows, path):
    """ One file per rho (two rho run as two processes): this run's experiments replace their rows on disk. """
    df = pd.DataFrame(rows)
    if os.path.exists(path):
        old = pd.read_csv(path)
        df = pd.concat([old[~old['experiment'].isin(df['experiment'])], df], ignore_index = True)
    df.to_csv(path, index = False)
    print('->', os.path.relpath(path, REPO))


# ------------------------------------------------------------------------------------------------ A13
def a13(a):
    """ tau_2020(s_2019): the 2020 policy function of the CRRA politico-economic equilibrium (design given,
    alg:CRRA:grid) at inherited capital between half and one and a half times the equilibrium s_2019; under
    log the tax does not depend on the state (prop:LOG:PEE). """
    rows = []
    for ρ in a.rho:
        m, _ = usModel(ρ)
        base = getattr(m, f'solvePEE_{prefs(ρ)}')()
        t0 = m.t0Year
        s0 = float(base['report']['s_'].xs(t0))
        τ0 = float(base['τ'].xs(t0))
        for x in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.3, 1.4, 1.5):
            if ρ == 1:
                τ = τ0
            else:
                sol = base['sols'][t0]
                g = np.asarray(sol['τ'].index, dtype = float)
                τ = float(sol['τPolicy'](x*s0)) if g.min() <= x*s0 <= g.max() else np.nan
            rows.append({'ρ': ρ, 's_2019/s*': x, 's_2019': x*s0, 'τ2020': τ, 'τ2020Equilibrium': τ0})
        r = pd.DataFrame([w for w in rows if w['ρ'] == ρ]).set_index('s_2019/s*')['τ2020']
        el = (np.log(r[1.05]) - np.log(r[0.95]))/(np.log(1.05) - np.log(0.95))
        print(f'rho={ρ}: tau_2020 {τ0:.6f} at s_2019 {s0:.6f}; at 0.5/1.5 s*: {r[0.5]:.6f}/{r[1.5]:.6f}; '
              f'elasticity d ln tau/d ln s {el:+.4f}')
    pd.DataFrame(rows).to_csv(out('C5_taxPolicyState.csv'), index = False)
    print('->', os.path.relpath(out('C5_taxPolicyState.csv'), REPO))
    return 0


def strategic(a, δ = 0.005):
    """ The strategic term of the 2020 electorate's choice, dtau_2050/ds_2020 * ds_2020/dtau_2020 at the
    equilibrium path: ds/dtau from eq:stateResidual at s_2019 given the continuation (stateApprox_t, central
    difference +-δ in tau_2020), dtau/ds the slope of the 2050 policy function (central, +-1% of s_2020).
    Zero under log (prop:LOG:PEE). """
    rows = []
    for ρ in a.rho:
        if ρ == 1:
            rows.append({'ρ': ρ, 'dsdτ': np.nan, 'dτ1ds': 0.0, 'strategic': 0.0, 'elasticity τ1,s': 0.0, 'elasticity τ1,τ': 0.0})
            continue
        m, _ = usModel(ρ)
        base = m.solvePEE_CRRA()
        tIdx, t0 = m.db['t'], m.t0Year
        t1 = tIdx[tIdx.get_loc(t0) + 1]
        θ1 = float(m.db['θ'].xs(t1))
        s_ = float(base['report']['s_'].xs(t0))
        sEq = float(base['report']['s_'].xs(t1))
        τ0, τ1 = float(base['τ'].xs(t0)), float(base['τ'].xs(t1))
        CR, solp = m.CRRA, base['sols'][t1]
        sC = np.asarray(base['sols'][t0]['τ'].index, dtype = float)
        sC = np.linspace(sC.min(), sC.max(), 4001)

        def sOf(τ):
            Θs = CR.stateApprox_t(np.full_like(sC, τ), sC, t0, θ1, solp)['Θs']
            return float(CR._rootS(Θs[:, None], sC, np.array([s_]), t0)[0][0])
        sAt = sOf(τ0)
        dsdτ = (sOf(τ0 + δ) - sOf(τ0 - δ))/(2*δ)
        dτ1ds = (float(solp['τPolicy'](1.01*sAt)) - float(solp['τPolicy'](0.99*sAt)))/(0.02*sAt)
        rows.append({'ρ': ρ, 'τ_t0': τ0, 'τ_t1': τ1, 's_t0': sAt, 's_t0 path': sEq,
                     'dsdτ': dsdτ, 'dτ1ds': dτ1ds, 'strategic': dτ1ds*dsdτ,
                     'elasticity s,τ': dsdτ*τ0/sAt, 'elasticity τ1,s': dτ1ds*sAt/τ1,
                     'elasticity τ1,τ': dτ1ds*dsdτ*τ0/τ1})
        r = rows[-1]
        print(f"rho={ρ}: s_{t0} {sAt:.6f} (path {sEq:.6f}); ds/dtau {dsdτ:+.5f} (el {r['elasticity s,τ']:+.3f}); "
              f"dtau_{t1}/ds {dτ1ds:+.5f} (el {r['elasticity τ1,s']:+.3f}); strategic dtau_{t1}/dtau_{t0} "
              f"{r['strategic']:+.5f}")
    pd.DataFrame(rows).to_csv(out('C5_strategicTerm.csv'), index = False)
    print('->', os.path.relpath(out('C5_strategicTerm.csv'), REPO))
    return 0


COMMANDS = {'selfcheck': selfcheck, 'a1': a1, 'a9': a9, 'loss': loss, 'lambda': lam, 'index': index,
            'design': design, 'designCRRA': designCRRA, 'a13': a13, 'strategic': strategic}


def main():
    p = argparse.ArgumentParser(description = 'C5 numbers (see the module docstring).')
    p.add_argument('command', choices = tuple(COMMANDS))
    p.add_argument('--rho', type = float, nargs = '*', default = list(RHOS))
    p.add_argument('--passes', type = int, default = 2, help = 'designCRRA: solves per experiment at most')
    p.add_argument('--only', nargs = '*', default = None, help = 'designCRRA: experiments to run (X1 X2)')
    a = p.parse_args()
    tic = time.time()
    rc = COMMANDS[a.command](a)
    print(f'[{a.command}: {time.time()-tic:.0f}s]')
    return rc


if __name__ == '__main__':
    sys.exit(main())
