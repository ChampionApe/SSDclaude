r""" Endogenous system characteristics, A+B: run the leaded choice of theta under the deadweight wedge and
write everything the appendix needs.

Run:  .venv\Scripts\python.exe python\US\runESC.py                     # every stage
      ... --stage calib                        the wedge calibration table alone
      ... --stage path                         the endogenous design path
      ... --stage shocks                       the counterfactuals
      ... --stage country                      France and the UK
      ... --spec scale flat  --phi 0.25 0.5 0.75

Four stages, each writing its own csv under results/esc/:

  calib    for every (spec, phi): p such that the equilibrium design IN FORCE at 2020 is the observed one
           (ModelESC.leadedDesignAtT0), with (beta, omega) recalibrated inside. Plus the no-wedge row,
           which is the corner the whole exercise is trying to escape.
  path     the equilibrium path of theta_t under the calibrated wedge, with the choice binding from the
           first period -- the ageing prediction, and the closest thing the model has to figure 1.1's
           cross-section.
  shocks   the counterfactuals of shocks.py (ageing, French income distribution / leisure / voting, and
           all three at once), plus a France reference row, each run twice: theta PINNED at the shocked
           model's exogenous design, and theta chosen. Every one is a NEW EQUILIBRIUM PATH -- the shocked
           parameters hold over the whole horizon, the economy starts at its own steady state, the
           political choice binds from the first period -- and is REPORTED AT t0 (2020). t0+1 is written
           too, but the tables read t0: because theta_{t0} is now an equilibrium outcome rather than a
           pinned datum, 2020 already carries the design response.
  country  France and the UK under (i) the US-calibrated wedge and (ii) their own. (i) asks whether one
           common technology of redistribution puts the three countries in the observed order; (ii) is the
           appendix's own convention (a separately calibrated p per country).

Everything is LOG (rho = 1). The CRRA case needs a two-dimensional (s, theta) state and is not this file.
"""
import os, sys, argparse, time, json
import numpy as np, pandas as pd
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)

import test as testmod
import testEU
import shocks as sh
from modelESC import ModelESC
from modelFR import ModelFR

OUTDIR = os.path.join(REPO, 'results', 'esc')
GS = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}


def mergeWrite(path, rows, key):
    """ Write `rows` to csv `path`, PRESERVING rows on disk whose `key` combination this run did not
    produce. The stage loops write after every point, and the paper pipeline re-runs exactly the missing
    (spec, phi) or (rho, spec, phi) combinations -- a plain to_csv would clobber everything else in the
    file on such a partial run. NaN keys (the no-wedge row's phi) are compared as equal. """
    df = pd.DataFrame(rows)
    if os.path.exists(path) and len(df):
        old = pd.read_csv(path)
        fill = lambda d: pd.MultiIndex.from_frame(d[key].astype(object).fillna('__na__').astype(str))
        df = pd.concat([old[~fill(old).isin(fill(df))], df], ignore_index = True)
    df.to_csv(path, index = False)


class ModelESCFR(ModelESC, ModelFR):
    """ France/UK under the wedge. ModelESC first in the MRO so its __init__ strips `wedge` before
    ModelFR's strips `usRef`; calibrate() then resolves to ModelFR's (beta imposed from the US, omega the
    only searched parameter) and getθ to ModelESC's wedge-aware one. """


# ---------------------------------------------------------------- builders

def buildUS(wedge = None, ρ = 1.0, nθ = 41, nθCand = 121):
    row = pd.read_csv(os.path.join(REPO, 'results', 'calibration', 'US_rhoGrid.csv'))
    row = row.loc[(row['ρ'] - ρ).abs() < 1e-9].iloc[-1]
    m = ModelESC(pars = testmod.pars | {'ρ': float(ρ), 'β': float(row['β']), 'ω': float(row['ω'])},
                 wedge = wedge, nθ = nθ, nθCand = nθCand, **testmod.kwargs)
    m.db['dates'] = testmod.dates
    m.db['workweek'] = testmod.workweek
    m.LOG.initGS(GS)
    return m


def buildEU(country, wedge = None, grouping = None, nθ = 41, nθCand = 121, ρ = 1.0):
    pars, kwargs, dates, workweek = testEU.load(country, grouping = grouping)
    pars.update({'ρ': float(ρ), 'ω': 2.})
    m = ModelESCFR(pars = pars, wedge = wedge, usRef = testEU.usReference(), nθ = nθ,
                   nθCand = nθCand, **kwargs)
    m.db['dates'], m.db['workweek'], m.db['country'] = dates, workweek, country + (grouping or '')
    m.LOG.initGS(GS)
    return m


# ---------------------------------------------------------------- reporting

def readout(m, τ, report, hbarRef, pos, workweekData = None):
    """ shocks.readout at one position of the path.

    workweekData defaults to the model's own datum, which is right for every US-based counterfactual. It
    must be passed explicitly for a NON-US model (franceRow): the workweek is reported as
    workweekData * hbar/hbarRef with hbarRef the US baseline's, so pairing France's hbar with France's own
    datum would scale the ratio twice and put its row at ~31.9 instead of 35.4. """
    return sh.readout(m, τ, report,
                      float(m.db['workweek'] if workweekData is None else workweekData),
                      hbarRef, pos = pos)


def baselineRefs(m):
    """ The exogenous-theta baseline on the SAME model (same wedge, same calibration): its hbar at t0 is
    the workweek's reference point, and its (tau, sr, workweek) the row every endogenous number is read
    against. """
    base = m.solvePEE_LOG()
    t0 = m.t0Year
    hbarRef = float(m.B.avgHours(base['report']['h'].xs(t0), t0))
    return base, hbarRef


# ---------------------------------------------------------------- stage: calibration

def stageCalib(specs, phis, out, ρ = 1.0):
    rows = []
    m = buildUS(None, ρ = ρ)
    m.calibrate()
    t0 = m.t0Year
    sols = m.ESC.solveBackward()
    rows.append({'spec': 'none', 'phi': np.nan, 'p': np.nan, 'converged': True,
                 'θStar': float(m.db['θ'].xs(t0)), 'choice': m.leadedDesignAtT0(sols),
                 'β': m.simpleβinv(), 'ω': float(m.db['ω'].xs(t0)), 'τDrift': np.nan, 'RDrift': np.nan})
    print('no wedge: θ*={θStar:.4f} -> choice {choice:.4f}'.format(**rows[-1]))
    mergeWrite(out, rows, ['spec', 'phi'])

    for spec in specs:
        for phi in phis:
            tic = time.time()
            print(f'\n[{spec}, φ={phi}] calibrating p ...')
            m = buildUS({'spec': spec, 'phi': phi, 'p': 1.0}, ρ = ρ)
            try:
                rec = m.calibrateWedge(spec = spec, phi = phi)
            except Exception as e:
                print(f'  FAILED: {type(e).__name__}: {e}')
                rows.append({'spec': spec, 'phi': phi, 'p': np.nan, 'converged': False})
                mergeWrite(out, rows, ['spec', 'phi']); continue
            r = {'spec': spec, 'phi': phi, 'p': rec['p'], 'converged': rec['converged'],
                 'θStar': rec['θ'], 'residual': rec['residual'],
                 'β': m.simpleβinv(), 'ω': float(m.db['ω'].xs(m.t0Year))}
            if rec['converged']:
                led = m.solveLeaded(pinAtT0 = False)
                # 'choice' is the calibration's own target read back off the solved path: the design in
                # FORCE at t0, not the one chosen there. At a converged p it equals θ* to `residual`.
                r |= {'τDrift': led['targetDrift']['τ'], 'RDrift': led['targetDrift']['R'],
                      'choice': float(led['θ'].iloc[m.db['t0']]),
                      'choiceAtT0': float(led['θ'].iloc[m.db['t0']+1])}
            rows.append(r)
            print('  -> p={p}  θ*={θStar:.4f}  β={β:.4f} ω={ω:.4f}  ({:.0f}s)'.format(time.time()-tic, **r))
            mergeWrite(out, rows, ['spec', 'phi'])
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- stage: the design path

def stagePath(specs, phis, calib, out, ρ = 1.0):
    rows = []
    for spec in specs:
        for phi in phis:
            hit = calib[(calib['spec'] == spec) & (calib['phi'] == phi) & calib['converged']]
            if hit.empty:
                continue
            p = float(hit.iloc[0]['p'])
            m = buildUS({'spec': spec, 'phi': phi, 'p': p}, ρ = ρ)
            m.calibrate()
            base, hbarRef = baselineRefs(m)
            led = m.solveLeaded(pinAtT0 = False)
            dates = m.db['dates']
            for pos, t in enumerate(m.db['t']):
                if pos + 1 >= len(m.db['t']):
                    break
                r = readout(m, led['τ'], led['report'], hbarRef, pos)
                rb = readout(m, base['τ'], base['report'], hbarRef, pos)
                rows.append({'spec': spec, 'phi': phi, 'p': p, 'pos': pos,
                             'date': dates[pos] if pos < len(dates) else np.nan,
                             'ν': float(m.db['ν'].xs(t)),
                             'θ': float(led['θ'].xs(t)), 'τ': r['τ'], 'sr': r['sr'],
                             'workweek': r['workweek'], 'R': r['R'],
                             'τExo': rb['τ'], 'srExo': rb['sr'], 'workweekExo': rb['workweek']})
            pd.DataFrame(rows).to_csv(out, index = False)
            print('[{}, φ={}] θ path: {}'.format(spec, phi,
                  '  '.join('{:.3f}'.format(x) for x in led['θ'].values[:8])))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- stage: counterfactuals

def leadedNewPath(m, hbarRef, apply = None, data = None, pin = False):
    """ One counterfactual as a NEW EQUILIBRIUM PATH: the shocked parameters hold over the whole horizon,
    the economy starts at its own steady state, and everything is read at t0 (2020). shocks.shockedCopy
    is the same construction on the exogenous-theta side.

    pin=True holds theta at the shocked model's own exogenous design for the whole horizon -- the
    exogenous-theta reading. pin=False lets the political choice bind from the first period the horizon
    allows, so theta_{t0} is itself an equilibrium outcome rather than an inherited datum. That is what
    makes a table at 2020 informative: under the old copy-from-t0 convention theta was pinned as history
    through 2020 and the two readings agreed there by construction, so the tables had to be read at 2050.

    Returns readouts at t0 and t0+1 (t0 is what the tables print; t0+1 is kept because the design path's
    drift is the ageing prediction) plus the design at t0-1, t0, t0+1. """
    pos = m.db['t0']
    mt = deepcopy(m)
    # as shocks.shockedCopy: the warm starts hold the BASELINE's solution, so clearing them is what keeps
    # each experiment independent of which one ran before it.
    mt.x0, mt.LOG.x0, mt.CRRA.x0 = {}, {}, {}
    if apply is not None:
        apply(mt, data)
    ε = mt.db['eps'].values.astype(float)
    if pin:
        θ = mt.db['θ'].values.astype(float)
        pol = mt.solvePEE_LOG(θ = θ, ε = ε)
        τ, report, θPath = pol['τ'], pol['report'], pd.Series(θ, index = mt.db['t'])
    else:
        led = mt.solveLeaded(pinAtT0 = False)
        τ, report, θPath = led['τ'], led['report'], led['θ']
    return {'t0': readout(mt, τ, report, hbarRef, pos), 't1': readout(mt, τ, report, hbarRef, pos+1),
            'θ_': float(θPath.iloc[pos-1]), 'θ0': float(θPath.iloc[pos]),
            'θ1': float(θPath.iloc[pos+1]), 'm': mt}


def stageShocks(specs, phis, calib, out, ρ = 1.0):
    rows = []
    for spec in specs:
        for phi in phis:
            hit = calib[(calib['spec'] == spec) & (calib['phi'] == phi) & calib['converged']]
            if hit.empty:
                continue
            p = float(hit.iloc[0]['p'])
            m = buildUS({'spec': spec, 'phi': phi, 'p': p}, ρ = ρ)
            m.calibrate()
            _, hbarRef = baselineRefs(m)
            data = frenchData(m)
            print(f'\n[{spec}, φ={phi}, p={p:.4f}] counterfactuals')
            for name in ESC_SCENARIOS:
                apply, d = (None, None) if name == 'baseline' else (SHOCKS_ESC[name][1], data)
                for pin in (True, False):
                    tic = time.time()
                    try:
                        r = leadedNewPath(m, hbarRef, apply, d, pin = pin)
                    except Exception as e:
                        print(f'  {name:<10} pin={pin}: FAILED {type(e).__name__}: {e}')
                        continue
                    rows.append({'spec': spec, 'phi': phi, 'p': p, 'scenario': name,
                                 'θpinned': pin, 'θ_tm1': r['θ_'], 'θ_t0': r['θ0'], 'θ_t1': r['θ1'],
                                 'τ_t0': r['t0']['τ'], 'sr_t0': r['t0']['sr'], 'ww_t0': r['t0']['workweek'],
                                 'τ_t1': r['t1']['τ'], 'sr_t1': r['t1']['sr'], 'ww_t1': r['t1']['workweek']})
                    print('  {:<10} pin={:<5} θ_t0={:.4f}  τ_t0={:.4f} sr_t0={:.4f} ww_t0={:.2f}'
                          '  (θ_t1={:.4f}, {:.0f}s)'
                          .format(name, str(pin), r['θ0'], r['t0']['τ'], r['t0']['sr'],
                                  r['t0']['workweek'], r['θ1'], time.time()-tic))
                    mergeWrite(out, rows, ['spec', 'phi', 'scenario', 'θpinned'])

            # France's own calibrated path under the same wedge -- the endpoint the French-characteristics
            # rows are read against. Exogenous theta only: France's design is a datum here, and a leaded
            # France would be a different exercise (that is stageCountry's question).
            try:
                f = franceRow(m, spec, phi, p, hbarRef, ρ = ρ)
                rows.append(f)
                print('  {:<10} pin={:<5} θ_t0={:.4f}  τ_t0={:.4f} sr_t0={:.4f} ww_t0={:.2f}'
                      .format('France', 'True', f['θ_t0'], f['τ_t0'], f['sr_t0'], f['ww_t0']))
                mergeWrite(out, rows, ['spec', 'phi', 'scenario', 'θpinned'])
            except Exception as e:
                print(f'  France     FAILED {type(e).__name__}: {e}')
    return pd.DataFrame(rows)


def franceRow(m, spec, phi, p, hbarRef, ρ = 1.0):
    """ France's own calibrated equilibrium at 2020 under the same wedge, in escShocks' row schema.

    Not a shock on the US model: France carries its own eta, X, mu, nu AND its own calibrated omega, so
    what separates it from the all-French-characteristics row is precisely what the observable
    characteristics do not explain. The workweek is on the US scale (hbarRef, and the US datum passed
    explicitly to readout) and is ModelFR's own hours target, so that cell reproduces the datum rather
    than predicting it. """
    mFR = buildEU('FR', {'spec': spec, 'phi': phi, 'p': p}, ρ = ρ)
    mFR.calibrate()
    pos = mFR.db['t0']
    out = mFR.solvePEE_LOG()
    ww = float(m.db['workweek'])
    r0 = readout(mFR, out['τ'], out['report'], hbarRef, pos, workweekData = ww)
    r1 = readout(mFR, out['τ'], out['report'], hbarRef, pos+1, workweekData = ww)
    θ = mFR.db['θ'].values.astype(float)
    return {'spec': spec, 'phi': phi, 'p': p, 'scenario': 'France', 'θpinned': True,
            'θ_tm1': float(θ[pos-1]), 'θ_t0': float(θ[pos]), 'θ_t1': float(θ[pos+1]),
            'τ_t0': r0['τ'], 'sr_t0': r0['sr'], 'ww_t0': r0['workweek'],
            'τ_t1': r1['τ'], 'sr_t1': r1['sr'], 'ww_t1': r1['workweek']}


# France's income distribution AND its voting profile together. Neither shocks.py nor the paper runs the
# pair, and the pair is what the cross-section actually confronts: the two move in OPPOSITE directions for
# the design (more equality pushes theta up, a flatter voting profile pushes it down), so whether the model
# implies a theta-inequality relation at all depends on their net effect -- which is the question figure 1.1
# poses. Applied in the order income-then-voting; shockIncomeDistribution re-derives theta from RR0 and
# shockVoting does not touch eta, so the two commute.
SHOCKS_ESC = dict(sh.SHOCKS) | {
    'frBoth': ('Income distribution + voting',
               lambda mt0, d: (sh.SHOCKS['frIncome'][1](mt0, d), sh.SHOCKS['frVoting'][1](mt0, d))),
}

# The order the shocks stage runs and the tables read. 'frAll' (shocks.shockFrenchAll) is the far end of
# the "mostly US, partly France" scale and franceRow is its endpoint; 'frBoth' stays because it isolates
# the two characteristics that move the DESIGN in opposite directions.
ESC_SCENARIOS = ('baseline', 'mild', 'acute', 'frIncome', 'frLeisure', 'frVoting', 'frBoth', 'frAll')


def frenchData(m):
    """ France's characteristics in the form shocks.py wants (runShocksUS.frenchData, LOG only). """
    parsFR, kwFR, datesFR, wwFR = testEU.load('FR')
    mFR = ModelFR(pars = parsFR | {'ρ': 1., 'ω': 2.}, usRef = testEU.usReference(), **kwFR)
    mFR.db['dates'], mFR.db['workweek'] = datesFR, wwFR
    mFR.LOG.initGS(GS)
    mFR.calibrate()
    t0FR, t0US = mFR.db['t'][mFR.db['t0']], m.t0Year
    XbarFR = float((mFR.db['γi'].xs(t0FR)*mFR.db['Xi'].xs(t0FR)).sum())
    XbarUS = float((m.db['γi'].xs(t0US)*m.db['Xi'].xs(t0US)).sum())
    # muFR is the WORKBOOK's mu_j -- nj entries, including the zero-mass slot -- because shockVoting
    # installs it through adjPar('μj'). Passing the ni-length mu_i instead raises a shape error, which is
    # how this was caught. eta is the other way round: shockIncomeDistribution takes eta_i.
    return {'ηFR': mFR.db['ηi'].xs(t0FR).values.astype(float),
            'μFR': parsFR['μj'],
            'xbarRatio': XbarFR/XbarUS, 'pinTheta': False,
            'θUS': float(m.db['θ'].xs(t0US))}


# ---------------------------------------------------------------- stage: France and the UK

def stageCountry(specs, phis, calib, out):
    rows = []
    for spec in specs:
        for phi in phis:
            hit = calib[(calib['spec'] == spec) & (calib['phi'] == phi) & calib['converged']]
            if hit.empty:
                continue
            pUS = float(hit.iloc[0]['p'])
            for country, grouping in (('FR', None), ('UK', None), ('UK', 'US')):
                label = country + (grouping or '')
                # (i) the US-calibrated wedge, imposed
                try:
                    m = buildEU(country, {'spec': spec, 'phi': phi, 'p': pUS}, grouping = grouping)
                    m.calibrate()
                    t0 = m.t0Year
                    sols = m.ESC.solveBackward()
                    θStar = float(m.db['θ'].xs(t0))
                    ch = m.leadedDesignAtT0(sols)
                    rows.append({'spec': spec, 'phi': phi, 'country': label, 'wedgeFrom': 'US',
                                 'p': pUS, 'θStar': θStar, 'choice': ch,
                                 'ω': float(m.db['ω'].xs(t0)), 'τ': float(m.solvePEE_LOG()['τ'].xs(t0))})
                    print('[{}, φ={}] {:<5} US wedge p={:.4f}: θ*={:.4f} -> choice {:.4f}'
                          .format(spec, phi, label, pUS, θStar, ch))
                except Exception as e:
                    print(f'  {label} US-wedge FAILED {type(e).__name__}: {e}')
                # (ii) its own calibrated p
                try:
                    m = buildEU(country, {'spec': spec, 'phi': phi, 'p': pUS}, grouping = grouping)
                    rec = m.calibrateWedge(spec = spec, phi = phi, verbose = False)
                    rows.append({'spec': spec, 'phi': phi, 'country': label, 'wedgeFrom': 'own',
                                 'p': rec['p'], 'θStar': rec['θ'], 'choice': rec['θ'] + rec['residual'],
                                 'converged': rec['converged'],
                                 'ω': float(m.db['ω'].xs(m.t0Year))})
                    print('[{}, φ={}] {:<5} own wedge: p={} θ*={:.4f} ({})'
                          .format(spec, phi, label, rec['p'], rec['θ'], rec['message']))
                except Exception as e:
                    print(f'  {label} own-wedge FAILED {type(e).__name__}: {e}')
                pd.DataFrame(rows).to_csv(out, index = False)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- stage: the permanent choice

def stagePermanent(specs, phis, out, ρ = 1.0, θCand = None):
    """ The PERMANENT choice of theta (app:ESC), calibrated in its own right and compared with the leaded
    one at the same wedge.

    Three rows per (spec, phi): the no-wedge case (which the appendix reports as a corner and which this
    reproduces), the leaded-calibrated wedge evaluated under the permanent timing, and the permanent
    timing's OWN calibrated p. The last is the number that belongs beside the appendix's 0.41.

    Three readings of the predetermined ratio are recorded per row (modelESC.solvePermanent's `pinning`).
    theta_perm is the anticipated vote's fixed point; theta_permIncumbent is the unanticipated reform, which
    coincides with it wherever the choice reproduces the incumbent design -- so the two agree by
    construction on the calibrated rows and separate only elsewhere. theta_permMovingSi is the WRONG object
    under either timing, kept because the gap is ~0.13 in theta and belongs on the record."""
    rows = []
    for spec in specs:
        for phi in phis:
            # (a) no wedge
            m = buildUS(None, ρ = ρ)
            m.calibrate()
            r = m.solvePermanent('LOG', θCand = θCand)
            rows.append({'spec': 'none', 'phi': np.nan, 'p': np.nan, 'source': 'none',
                         'θStar': float(m.db['θ'].xs(m.t0Year)), 'θPerm': r['θ'],
                         'atBound': r['atBound'], 'nTurning': r['nTurning'],
                         'converged': r['converged'], 'θPermIncumbent': r['θIncumbent'],
                         'θPermMovingSi': r['θMoving'],
                         'θLeaded': m.leadedDesignAtT0(m.ESC.solveBackward()),
                         'τAtChoice': r['τAtChoice']})
            print('[{}, φ={}] no wedge: θ_perm={:.4f} (corner={}, turns={})'.format(
                spec, phi, r['θ'], r['atBound'], r['nTurning']))

            # (b) the permanent timing's own calibrated p
            m = buildUS({'spec': spec, 'phi': phi, 'p': 0.4}, ρ = ρ)
            try:
                rec = m.calibrateWedge(spec = spec, phi = phi, preferences = 'permLOG', verbose = False)
            except Exception as e:
                print('  own-p calibration FAILED {}: {}'.format(type(e).__name__, e))
                rec = {'converged': False, 'p': np.nan, 'message': str(e)}
            if rec['converged']:
                r = m.solvePermanent('LOG', θCand = θCand)
                rows.append({'spec': spec, 'phi': phi, 'p': rec['p'], 'source': 'permanent',
                             'θStar': rec['θ'], 'θPerm': r['θ'], 'atBound': r['atBound'],
                             'nTurning': r['nTurning'], 'converged': r['converged'],
                             'θPermIncumbent': r['θIncumbent'], 'θPermMovingSi': r['θMoving'],
                             'θLeaded': m.leadedDesignAtT0(m.ESC.solveBackward()),
                             'τAtChoice': r['τAtChoice']})
                print('  own p={:.4f}: θ_perm={:.4f} (target {:.4f}), leaded at the same wedge={:.4f}'.format(
                    rec['p'], r['θ'], rec['θ'], rows[-1]['θLeaded']))
            pd.DataFrame(rows).to_csv(out, index = False)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- stage: the model's figure 1.1

def stageFig1(specs, phis, calib, out, ρ = 1.0):
    """ The model's own cross-section: the chosen design and the equilibrium tax as functions of population
    growth and of income inequality, one axis at a time.

    Figure 1.1 plots pension spending and the Bismarckian index against population growth and against the
    Gini across twenty OECD countries, and reports a clear relation with the first and none with the second.
    This traces the model's counterpart by re-solving the leaded equilibrium on a grid of nu (holding
    everything else at the US calibration) and on a grid of inequality (scaling the SPREAD of eta_i around
    its population-weighted mean, so mean productivity is held fixed and only dispersion moves).

    theta reported is the CHOICE at t0 -- the design the electorate picks given the shocked environment,
    which is what the cross-section of designs corresponds to. """
    rows = []
    for spec in specs:
        for phi in phis:
            hit = calib[(calib['spec'] == spec) & (calib['phi'] == phi) & calib['converged']]
            if hit.empty:
                continue
            p = float(hit.iloc[0]['p'])
            base = buildUS({'spec': spec, 'phi': phi, 'p': p}, ρ = ρ)
            base.calibrate()
            t0 = base.t0Year
            pars0 = {'β': base.simpleβinv(), 'ω': float(base.db['ω'].xs(t0))}
            ν0 = float(base.db['ν'].xs(t0))
            η0 = base.db['ηi'].xs(t0).values.astype(float)
            γ0 = base.db['γi'].xs(t0).values.astype(float)
            ηBar = float((γ0*η0).sum())

            for axis, values in (('nu', np.linspace(0.95, 1.55, 13)),
                                 ('inequality', np.linspace(0.5, 1.3, 9))):
                for v in values:
                    m = buildUS({'spec': spec, 'phi': phi, 'p': p}, ρ = ρ)
                    m.db.update(m.adjPar('β', pars0['β']))
                    m.db.update(m.adjPar('ω', pars0['ω']))
                    if axis == 'nu':
                        m.db.update(m.adjPar('ν', float(v)))
                    else:
                        ηNew = ηBar + v*(η0 - ηBar)          # scale the spread, hold the mean
                        m.db.update(m.adjPar('ηj', np.append(m.db['η0'].xs(t0), ηNew)))
                    m.updateAuxPars()
                    try:
                        sols = m.ESC.solveBackward()
                        θStar = float(m.db['θ'].xs(t0))
                        ch = m.leadedDesignAtT0(sols)
                        rows.append({'spec': spec, 'phi': phi, 'p': p, 'axis': axis, 'value': float(v),
                                     'ν': float(m.db['ν'].xs(t0)), 'θData': θStar, 'θChoice': ch,
                                     'τ': m.ESC.τAt(t0, θStar),
                                     'τAtChoice': m.ESC.τAt(t0, ch),
                                     'ηRatio': float(m.db['ηi'].xs(t0).values[-1]/m.db['ηi'].xs(t0).values[0])})
                    except Exception as e:
                        print(f'  {axis}={v:.3f} FAILED {type(e).__name__}: {e}')
                    pd.DataFrame(rows).to_csv(out, index = False)
                d = pd.DataFrame(rows)
                d = d[(d.spec == spec) & (d.phi == phi) & (d.axis == axis)]
                print('[{}, φ={}] {:<11}: θ choice {:.3f} -> {:.3f} over {} = {:.2f} -> {:.2f}'.format(
                    spec, phi, axis, d['θChoice'].iloc[0], d['θChoice'].iloc[-1], axis,
                    d['value'].iloc[0], d['value'].iloc[-1]))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description = 'Endogenous theta: leaded choice under the deadweight wedge.')
    p.add_argument('--stage', nargs = '*', default = ['calib', 'path', 'shocks', 'country', 'fig1',
                                                     'permanent'],
                   choices = ('calib', 'path', 'shocks', 'country', 'fig1', 'permanent'))
    p.add_argument('--spec', nargs = '*', default = ['scale', 'flat'])
    p.add_argument('--phi', type = float, nargs = '*', default = [0.5, 0.25, 0.75])
    p.add_argument('--rho', type = float, default = 1.0)
    p.add_argument('--tag', default = '')
    a = p.parse_args()
    os.makedirs(OUTDIR, exist_ok = True)
    f = lambda n: os.path.join(OUTDIR, f'{n}{a.tag}.csv')

    calib = None
    if 'calib' in a.stage:
        calib = stageCalib(a.spec, a.phi, f('escCalibration'), ρ = a.rho)
    else:
        calib = pd.read_csv(f('escCalibration'))
    if 'path' in a.stage:
        stagePath(a.spec, a.phi, calib, f('escPath'), ρ = a.rho)
    if 'shocks' in a.stage:
        stageShocks(a.spec, a.phi, calib, f('escShocks'), ρ = a.rho)
    if 'country' in a.stage:
        stageCountry(a.spec, a.phi, calib, f('escCountry'))
    if 'fig1' in a.stage:
        stageFig1(a.spec, a.phi, calib, f('escFig1'), ρ = a.rho)
    if 'permanent' in a.stage:
        stagePermanent(a.spec, a.phi, f('escPermanent'), ρ = a.rho)
    print('\n-> {}'.format(os.path.relpath(OUTDIR, REPO)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
