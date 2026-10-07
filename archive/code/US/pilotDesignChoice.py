r""" Measurements of the frozen-state design-choice layers against each other and against the legacy layer:
items M1 to M6 of notes/brief_designChoicePilot_2026-10-02.md, M7 and M8 of
notes/brief_designChoiceProduction_2026-10-02.md. 'root' is LeadedCRRA2D(designRule = 'root') at its
defaults (Ma = 5, secant closing; the M1-M6 rows on file were measured at Ma = 9 with bisection), 'legacy'
designRule = 'legacy', 'foc' policyESCpilot.LeadedCRRA2DFOC.

Run (each item group is its own process; every group writes logs/pilotDesignChoice/rows_<tag>.csv and
one .npz of per-state policies per run):

    python\US\pilotDesignChoice.py --item M1 --rho 2.0            # one period at ns = 150, + M6 checks
    python\US\pilotDesignChoice.py --item M2 --rho 2.0 --scenarios baseline frVoting
    python\US\pilotDesignChoice.py --item M34                      # nCand and derivative sensitivity
    python\US\pilotDesignChoice.py --item M5                       # rho -> 1 at lambda = 8.643
    python\US\pilotDesignChoice.py --item M78                      # grid reading; design-state grid
    python\US\pilotDesignChoice.py --report                        # merge into pilotDesignChoice.csv, print

Model: runESCcrra.buildUS under the 'size' wedge at the exact calibrated lambda of
results/esc/escCalibrationCRRA.csv (common X), (beta, omega) recalibrated; the French-voting point is
runESCcrra's shocks stage (frenchData, then shocks.shockedCopy 'frVoting'). Every period chooses.
Rows: M, rho, scenario, nCand, ns, nθ, knotsθ, rule, period, item, value, seconds.
"""
import os, sys, glob, time, argparse
import numpy as np, pandas as pd
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)

OUT = os.path.join(REPO, 'logs', 'pilotDesignChoice')
LAMBDA = {2.0: 1.7282425096969982, 0.5: 18.242097713421508}
LAMBDA_LOG = 8.643
COLS = ['M', 'ρ', 'scenario', 'nCand', 'ns', 'nθ', 'knotsθ', 'rule', 'period', 'item', 'value', 'seconds']
RULES = ('legacy', 'root', 'foc')
PAIRS = (('legacy', 'root'), ('legacy', 'foc'), ('root', 'foc'))


class Rows:
    """ The rows of one process, rewritten to its own csv after every addition. """

    def __init__(self, tag):
        self.path = os.path.join(OUT, f'rows_{tag}.csv')
        self.rows = []

    def add(self, M, ρ, scenario, nCand, ns, nθ, knotsθ, rule, period, item, value, seconds = np.nan):
        self.rows.append(dict(zip(COLS, (M, ρ, scenario, nCand, ns, nθ, knotsθ, rule, period, item,
                                         float(value), float(seconds)))))
        pd.DataFrame(self.rows, columns = COLS).to_csv(self.path, index = False)


def calibratedλ(ρ):
    """ λ of the exact 'size' common-X row at ρ (read-only), checked against the brief's value. """
    df = pd.read_csv(os.path.join(REPO, 'results', 'esc', 'escCalibrationCRRA.csv'))
    hit = df[(df['method'] == 'exact') & (df['spec'] == 'size') & (df['commonX'].astype(str) == 'True')
             & ((df['ρ'] - ρ).abs() < 1e-9)]
    λ = float(hit['p'].iloc[-1])
    if abs(λ - LAMBDA[ρ]) > 1e-12:
        raise ValueError(f'λ on file at ρ={ρ} is {λ!r}, the brief quotes {LAMBDA[ρ]!r}.')
    return λ


_BASE = {}


def modelAt(ρ, scenario, ns, nCand):
    """ The calibrated US model under the size wedge at ρ's exact λ, or its French-voting copy. The
    calibrated baseline is built once per (ρ, ns, nCand) in a process. """
    from runESCcrra import buildUS, GSC
    from runShocksUS import frenchData
    from runESC import SHOCKS_ESC
    import shocks as sh
    gs = GSC | {'ns': ns}
    if (ρ, ns, nCand) not in _BASE:
        tic = time.time()
        m = buildUS(ρ, wedge = {'spec': 'size', 'phi': 0.5, 'p': calibratedλ(ρ)}, commonX = True, gs = gs,
                    nθCand2D = nCand)
        m.calibrate()
        _BASE[(ρ, ns, nCand)] = m
        print(f'  calibrated ρ={ρ} ns={ns} [{time.time()-tic:.0f}s]')
    m = _BASE[(ρ, ns, nCand)]
    if scenario == 'baseline':
        return m
    tic = time.time()
    frData = frenchData(m, ρ, 'CRRA', gs = gs, commonX = True)
    mt, _ = sh.shockedCopy(m, scenario, frData, SHOCKS_ESC)
    print(f'  {scenario} copy at ρ={ρ} [{time.time()-tic:.0f}s]')
    return mt


def layer(rule, m, nθ, nCand, knots = None):
    from policyESC import LeadedCRRA2D
    from policyESCpilot import LeadedCRRA2DFOC
    L = {'legacy': lambda: LeadedCRRA2D(m, nθ = nθ, nθCand = nCand, designRule = 'legacy'),
         'root': lambda: LeadedCRRA2D(m, nθ = nθ, nθCand = nCand, designRule = 'root'),
         'foc': lambda: LeadedCRRA2DFOC(m, nθ = nθ, nθCand = nCand, smoothKnotsθ = knots)}[rule]()
    L.GS = m.CRRA.GS
    return L


def onePeriod(m, nθ, nCand, ns, rules = RULES, knots = None):
    """ The terminal period, then one _periodCore at the last choosing period and each layer's _choose on
    it (test_frozenSelection.py section 5). Returns (core, {rule: choice dict}, {rule: seconds}, tCore). """
    Ls = {r: layer(r, m, nθ, nCand, knots) for r in rules}
    E = Ls[rules[0]]
    tIdx = m.db['t']
    θStar = float(m.db['θ'].xs(m.t0Year))
    ε = m.db['eps'].values.astype(float)
    sGrid = E.defaultSGrid(θStar, tIdx[-1], n = ns)
    solT = E.solveTerminal2D(ε[-1], sGrid, tIdx[-1], tIdx[-2])
    tic = time.perf_counter()
    core = E._periodCore(solT, tIdx[-2], tIdx[-3], tIdx[-1], ε[-2], ε[-1], sGrid, sGrid, E.θCand)
    tCore = time.perf_counter() - tic
    chs, sec = {}, {}
    for r, L in Ls.items():
        tic = time.perf_counter()
        chs[r] = L._choose(core, L.θCand, True)
        sec[r] = time.perf_counter() - tic
        print(f'    {r:<6} choose [{sec[r]:.1f}s]')
    return core, chs, sec, tCore, Ls


def maxAbs(a, b):
    with np.errstate(invalid = 'ignore'):
        return float(np.nanmax(np.abs(np.asarray(a, dtype = float) - np.asarray(b, dtype = float))))


def saveNpz(name, chs, extra = None):
    arrs = {}
    for r, ch in chs.items():
        for k in ('θNext', 'τSel', 'aStar', 'nEqθ', 'nBrθ', 'nCandθ', 'fallbackθ', 'atBoundθ'):
            if k in ch:
                arrs[f'{r}_{k}'] = np.asarray(ch[k])
    np.savez(os.path.join(OUT, name + '.npz'), **arrs, **(extra or {}))


# ---------------------------------------------------------------------------------------------- M1 + M6
def itemM1(rows, ρ, scenarios, ns = 150, nCand = 41, nθ = 13):
    from policyESCpilot import deviationCheck, resolveAt
    for scenario in scenarios:
        print(f'\n=== M1 ρ={ρ} {scenario} ns={ns} nCand={nCand} ===')
        m = modelAt(ρ, scenario, ns, nCand)
        core, chs, sec, tCore, Ls = onePeriod(m, nθ, nCand, ns)
        period = int(core['t'])
        key = dict(M = 'M1', ρ = ρ, scenario = scenario, nCand = nCand, ns = ns, nθ = nθ, knotsθ = 4,
                   period = period)
        rows.add(**key, rule = 'core', item = 'tCore', value = tCore, seconds = tCore)
        for r, ch in chs.items():
            rows.add(**key, rule = r, item = 'tChoose', value = sec[r], seconds = sec[r])
            if 'nEqθ' in ch:
                rows.add(**key, rule = r, item = 'nEqθ max', value = ch['nEqθ'].max())
                rows.add(**key, rule = r, item = 'states nEqθ != 1', value = (ch['nEqθ'] != 1).sum())
                rows.add(**key, rule = r, item = 'fallbackθ', value = ch['fallbackθ'].sum())
                nb = ch['nBrθ'] if 'nBrθ' in ch else ch['nCandθ']
                rows.add(**key, rule = r, item = 'nBrθ|nCandθ max', value = nb.max())
                rows.add(**key, rule = r, item = 'frozen passes', value = ch['nPass'])
            if (np.asarray(ch['nEqτ']) >= 0).any():
                rows.add(**key, rule = r, item = 'nEqτ max', value = ch['nEqτ'].max())
                rows.add(**key, rule = r, item = 'cells nEqτ > 1', value = (ch['nEqτ'] > 1).sum())
                rows.add(**key, rule = r, item = 'fallbackτ', value = ch['fallbackτ'].sum())
        for a, b in PAIRS:
            rows.add(**key, rule = f'{a}-{b}', item = 'max|Δθ|', value = maxAbs(chs[a]['θNext'], chs[b]['θNext']))
            rows.add(**key, rule = f'{a}-{b}', item = 'max|Δτ|', value = maxAbs(chs[a]['τSel'], chs[b]['τSel']))
        # M6: the deviation check and the re-solve at the selected policy, every state
        sGrid = core['sGrid']
        for r in ('root', 'foc'):
            ch, L = chs[r], Ls[r]
            tic = time.perf_counter()
            gain, rel, dAbs, dRel = [], [], [], []
            for it, θt in enumerate(L.θGrid):
                dc = deviationCheck(L, core, float(θt), ch['aStar'][it], ch['θNext'][it])
                ra = resolveAt(L, core, ch['τSel'][it], sGrid, float(θt), ch['θNext'][it], ch['aStar'][it])
                gain.append(dc['gain']); rel.append(dc['rel'])
                dAbs.append(np.abs(ra['W'] - dc['V'])); dRel.append(np.abs(ra['W'] - dc['V'])/np.abs(dc['V']))
            s = time.perf_counter() - tic
            k6 = key | {'M': 'M6'}
            rows.add(**k6, rule = r, item = 'deviation gain max', value = np.nanmax(gain), seconds = s)
            rows.add(**k6, rule = r, item = 'deviation gain max rel', value = np.nanmax(rel))
            rows.add(**k6, rule = r, item = 'resolveAt-grid max abs', value = np.nanmax(dAbs))
            rows.add(**k6, rule = r, item = 'resolveAt-grid max rel', value = np.nanmax(dRel))
            print(f'    M6 {r}: gain {np.nanmax(gain):.2e} (rel {np.nanmax(rel):.2e}), '
                  f'resolveAt {np.nanmax(dAbs):.2e} (rel {np.nanmax(dRel):.2e})')
        saveNpz(f'M1_{scenario}_rho{ρ}_ns{ns}_nc{nCand}', chs, {'sGrid': sGrid, 'θGrid': Ls['legacy'].θGrid})


# ---------------------------------------------------------------------------------------------- M2
def itemM2(rows, ρ, scenarios, ns = 50, nCand = 41, nθ = 13):
    from policy import multiplicitySummary
    for scenario in scenarios:
        print(f'\n=== M2 ρ={ρ} {scenario} ns={ns} nCand={nCand} ===')
        m0 = modelAt(ρ, scenario, ns, nCand)
        tabs = {}
        for r in RULES:
            m = deepcopy(m0)
            m.ESCC2 = layer(r, m, nθ, nCand)
            tic = time.time()
            out = m.solveLeaded2D(pinAtT0 = False, verbose = True)
            sec = time.time() - tic
            t0 = m.t0Year
            key = dict(M = 'M2', ρ = ρ, scenario = scenario, nCand = nCand, ns = ns, nθ = nθ, knotsθ = 4, rule = r)
            rows.add(**key, period = int(t0), item = 'θ_t0 (in force)', value = float(out['θ'].xs(t0)), seconds = sec)
            rows.add(**key, period = int(t0), item = 'θ_t1', value = float(out['θ'].iloc[int(m.db['t0'])+1]))
            rows.add(**key, period = int(t0), item = 'τ_t0', value = float(out['τ'].xs(t0)))
            rows.add(**key, period = int(t0), item = 'targetDrift R', value = out['targetDrift']['R'])
            rows.add(**key, period = int(t0), item = 'targetDrift τ', value = out['targetDrift']['τ'])
            sols = out['sols']
            per = [t for t in sols if not sols[t].get('terminal') and sols[t].get('choose')]
            rows.add(**key, period = -1, item = 'Σ tCore', value = sum(sols[t]['tCore'] for t in per))
            rows.add(**key, period = -1, item = 'Σ tChoose', value = sum(sols[t]['tChoose'] for t in per))
            mt = out['multiplicity']
            for k in ('nEqMax', 'nCandMax', 'nStatesMultiple', 'nFallback'):
                rows.add(**key, period = -1, item = f'τ {k}', value = mt[k])
            if r != 'legacy':
                mθ = multiplicitySummary(sols, keys = ('nEqθ', 'nBrθ' if r == 'root' else 'nCandθ', 'fallbackθ'))
                for k in ('nEqMax', 'nCandMax', 'nStatesMultiple', 'nFallback'):
                    rows.add(**key, period = -1, item = f'θ {k}', value = mθ[k])
                print(f'    {r} θ multiplicity {mθ}')
            tabs[r] = {t: np.asarray(sols[t]['θNext']) for t in per}
            print(f'  {r}: θ_t0={float(out["θ"].xs(t0)):.4f} τ_t0={float(out["τ"].xs(t0)):.4f} '
                  f'drift={out["targetDrift"]} [{sec:.0f}s]')
            np.savez(os.path.join(OUT, f'M2_{scenario}_rho{ρ}_{r}.npz'),
                     **{f'θNext_t{t}': v for t, v in tabs[r].items()},
                     θ = out['θ'].values, τ = out['τ'].values)
        for a, b in PAIRS:
            for t in tabs[a]:
                rows.add(M = 'M2', ρ = ρ, scenario = scenario, nCand = nCand, ns = ns, nθ = nθ, knotsθ = 4,
                         rule = f'{a}-{b}', period = int(t), item = 'max|Δθ|', value = maxAbs(tabs[a][t], tabs[b][t]))


# ---------------------------------------------------------------------------------------------- M3 + M4
def itemM34(rows, ρ = 2.0, scenario = 'frVoting', ns = 50):
    from policyESCpilot import resolveAt, designSlopeAt
    print(f'\n=== M3/M4 ρ={ρ} {scenario} ns={ns} ===')
    m = modelAt(ρ, scenario, ns, 41)
    θStar = float(m.db['θ'].xs(m.t0Year))
    # M3: the candidate grid
    res, cores = {}, {}
    for nCand in (13, 21, 41, 81):
        print(f'  M3 nCand={nCand}')
        core, chs, sec, tCore, Ls = onePeriod(m, 13, nCand, ns)
        res[nCand], cores[nCand] = chs, (core, Ls)
        sGrid, θGrid = core['sGrid'], Ls['legacy'].θGrid
        js, it = int(np.argmin(np.abs(sGrid - 0.5*(sGrid[0] + sGrid[-1])))), int(np.argmin(np.abs(θGrid - θStar)))
        for r, ch in chs.items():
            rows.add('M3', ρ, scenario, nCand, ns, 13, 4, r, int(core['t']), 'θ at (s mid, θ*)',
                     ch['θNext'][it, js], sec[r])
        rows.add('M3', ρ, scenario, nCand, ns, 13, 4, 'state', int(core['t']), 's_ at the state', sGrid[js])
        rows.add('M3', ρ, scenario, nCand, ns, 13, 4, 'state', int(core['t']), 'θ_t at the state', θGrid[it])
        saveNpz(f'M3_{scenario}_rho{ρ}_ns{ns}_nc{nCand}', chs)
    for nCand in (13, 21, 41):
        for r in RULES:
            rows.add('M3', ρ, scenario, nCand, ns, 13, 4, r, int(cores[nCand][0]['t']), 'max|θ(nCand)-θ(81)|',
                     maxAbs(res[nCand][r]['θNext'], res[81][r]['θNext']))
    # M4 (i): the design-state grid, 13 against 21 nodes, at the common θ_t nodes
    print('  M4 nθ2D = 21')
    core21, chs21, sec21, tCore21, Ls21 = onePeriod(m, 21, 41, ns)
    θ13, θ21 = cores[41][1]['legacy'].θGrid, Ls21['legacy'].θGrid
    i13 = [int(np.argmin(np.abs(θ13 - v))) for v in θ21 if np.min(np.abs(θ13 - v)) < 1e-12]
    i21 = [int(np.argmin(np.abs(θ21 - θ13[i]))) for i in i13]
    for r in RULES:
        rows.add('M4', ρ, scenario, 41, ns, 21, 4, r, int(core21['t']), 'max|θ(nθ=21)-θ(nθ=13)| common θ_t',
                 maxAbs(chs21[r]['θNext'][i21], res[41][r]['θNext'][i13]), sec21[r])
    saveNpz(f'M4_{scenario}_rho{ρ}_ns{ns}_nth21', chs21)
    # M4 (ii): the knots of the design derivative, 4 against 8
    core, Ls = cores[41]
    F8 = layer('foc', m, 13, 41, knots = 8)
    tic = time.perf_counter()
    ch8 = F8._choose(core, F8.θCand, True)
    s8 = time.perf_counter() - tic
    rows.add('M4', ρ, scenario, 41, ns, 13, 8, 'foc', int(core['t']), 'max|θ(knots=8)-θ(knots=4)|',
             maxAbs(ch8['θNext'], res[41]['foc']['θNext']), s8)
    rows.add('M4', ρ, scenario, 41, ns, 13, 8, 'root-foc', int(core['t']), 'max|Δθ|',
             maxAbs(ch8['θNext'], res[41]['root']['θNext']))
    rows.add('M4', ρ, scenario, 41, ns, 13, 8, 'foc', int(core['t']), 'states nEqθ != 1', (ch8['nEqθ'] != 1).sum())
    saveNpz(f'M4_{scenario}_rho{ρ}_ns{ns}_knots8', {'foc8': ch8})
    # M4 (iii): the spline slope of the young's term at θ' = 0.45 against a central difference of resolveAt
    g = core['g']
    τGrid = g.values('τ')
    sGrid, θGrid = core['sGrid'], Ls['legacy'].θGrid
    it = int(np.argmin(np.abs(θGrid - θStar)))
    E = Ls['legacy']
    young = E.weights(core['t'])[1]
    q = float(1 - 1/m.BG.get('ρ', core['t']))
    θq, h = 0.45, 0.0125
    for n, js in enumerate((len(sGrid)//4, len(sGrid)//2, (3*len(sGrid))//4)):
        iτ = int(np.argmin(np.abs(τGrid - res[41]['root']['τSel'][it, js])))
        dlnc, _ = designSlopeAt(E, core, iτ, js, θq)
        pts = resolveAt(E, core, τGrid[iτ], sGrid[js], θGrid[it], np.array([θq - h, θq, θq + h]), 1.)
        spline = float((young*pts['hatc1iPow'][1]*dlnc).sum())
        Wy = pts['Wy']
        fd = (Wy[2] - Wy[0])/(2*h)
        fwd, bwd = (Wy[2] - Wy[1])/h, (Wy[1] - Wy[0])/h
        lab = f'state {n+1} (s_={sGrid[js]:.4g}, τ={τGrid[iτ]:.4f})'
        rows.add('M4', ρ, scenario, 41, ns, 13, 4, lab, int(core['t']), 'spline slope', spline)
        rows.add('M4', ρ, scenario, 41, ns, 13, 4, lab, int(core['t']), 'central difference', fd)
        rows.add('M4', ρ, scenario, 41, ns, 13, 4, lab, int(core['t']), '(spline-fd)/|fd|', (spline - fd)/abs(fd))
        rows.add('M4', ρ, scenario, 41, ns, 13, 4, lab, int(core['t']), '(fwd-bwd)/|fd|', (fwd - bwd)/abs(fd))
        print(f'    M4 FD {lab}: spline {spline:.6e} fd {fd:.6e} rel {(spline-fd)/abs(fd):+.3f} '
              f'asym {(fwd-bwd)/abs(fd):+.3f}')


# ---------------------------------------------------------------------------------------------- M5
def itemM5(rows, ρs = (1.10, 1.05, 1.02), ns = 50, nCand = 41, rules = ('root', 'foc', 'legacy')):
    import test as testmod
    from modelESC import ModelESC
    GSL = {'n': 101, 'smoothKnots': 4, 'interpKind': 'linear'}

    def build(ρ):
        m = ModelESC(pars = testmod.pars | {'ρ': float(ρ), 'β': 0.76, 'ω': 1.45},
                     wedge = {'spec': 'size', 'phi': 0.5, 'p': LAMBDA_LOG}, commonX = True,
                     nθCand2D = nCand, **testmod.kwargs)
        m.db['dates'], m.db['workweek'] = testmod.dates, testmod.workweek
        m.LOG.initGS(GSL)
        m.CRRA.initGS(GSL | {'ns': ns})
        m.calibrate()
        return m
    print('\n=== M5: the LOG anchor ===')
    mL = build(1.0)
    θLOG = mL.leadedDesignAtT0()
    rows.add('M5', 1.0, 'baseline', nCand, ns, 13, 4, 'LeadedLOG', int(mL.t0Year), 'θ_t0 (in force)', θLOG)
    print(f'  LOG θ_t0 = {θLOG:.6f}')
    for ρ in ρs:
        print(f'\n=== M5 ρ={ρ} ===')
        m0 = build(ρ)
        for r in rules:
            m = deepcopy(m0)
            m.ESCC2 = layer(r, m, 13, nCand)
            tic = time.time()
            out = m.solveLeaded2D(pinAtT0 = False)
            sec = time.time() - tic
            θ0 = float(out['θ'].xs(m.t0Year))
            key = dict(M = 'M5', ρ = ρ, scenario = 'baseline', nCand = nCand, ns = ns, nθ = 13, knotsθ = 4,
                       rule = r, period = int(m.t0Year))
            rows.add(**key, item = 'θ_t0 (in force)', value = θ0, seconds = sec)
            rows.add(**key, item = 'gap to LOG', value = θ0 - θLOG)
            rows.add(**key, item = 'gap/(ρ-1)', value = (θ0 - θLOG)/(ρ - 1))
            print(f'  {r}: θ_t0={θ0:.6f} gap={θ0-θLOG:+.6f} ratio={(θ0-θLOG)/(ρ-1):+.4f} [{sec:.0f}s]')


# ---------------------------------------------------------------------------------------------- M7 + M8
_S0 = {}


def s0Legacy(ρ, scenario, ns, nCand):
    """ s0 of a legacy recursion at the setting, every period choosing (ModelESC.solveLeaded2D's s0, i.e.
    s0FixedPoint at θ*), and its seconds; cached per process. """
    key = (ρ, scenario, ns, nCand)
    if key not in _S0:
        m = deepcopy(modelAt(ρ, scenario, ns, nCand))
        m.ESCC2 = layer('legacy', m, 13, nCand)
        tic = time.time()
        out = m.solveLeaded2D(pinAtT0 = False)
        _S0[key] = (float(out['s0']), time.time() - tic)
        print(f'  legacy recursion: s0 = {_S0[key][0]:.6f} [{_S0[key][1]:.0f}s]')
    return _S0[key]


def stateNear(sGrid, θGrid, s0, θStar):
    """ (s_ index, θ_t index) of the grid state nearest (s0, θ*). """
    return int(np.argmin(np.abs(np.asarray(sGrid) - s0))), int(np.argmin(np.abs(np.asarray(θGrid) - θStar)))


def itemM7(rows, ρ = 2.0, scenario = 'frVoting', ns = 50, nCand = 41, nθ = 13):
    """ The grid reading of V against the re-solve: the root layer's design (V(θ'; a*) read from the grid)
    against the design selected at the same a* from V re-evaluated off the grid by resolveAt at (τ̂(θ'; a*),
    θ') -- one extra frozen pass per θ_t for τ̂, the selection only, a* not re-solved. """
    from policyESCpilot import resolveAt
    from policyESC import frozenTaxPass, _argmaxRows
    print(f'\n=== M7 ρ={ρ} {scenario} ns={ns} nCand={nCand} ===')
    m = modelAt(ρ, scenario, ns, nCand)
    θStar = float(m.db['θ'].xs(m.t0Year))
    s0, secS0 = s0Legacy(ρ, scenario, ns, nCand)
    core, chs, sec, tCore, Ls = onePeriod(m, nθ, nCand, ns, rules = ('root',))
    R, ch = Ls['root'], chs['root']
    x = np.asarray(core['θ1Grid'], dtype = float)
    sGrid = core['sGrid']
    ns_, nθ1 = len(sGrid), len(x)
    θre = np.full((nθ, ns_), np.nan)
    tic = time.perf_counter()
    for it, θt in enumerate(R.θGrid):
        ok = np.isfinite(ch['aStar'][it])
        a = np.where(ok, ch['aStar'][it], 1.)
        fp = frozenTaxPass(R, core, float(θt), a)
        ra = resolveAt(R, core, fp['τ'].reshape(-1), np.repeat(sGrid, nθ1), float(θt), np.tile(x, ns_),
                       np.repeat(a, nθ1))
        V = np.asarray(ra['W'], dtype = float).reshape(ns_, nθ1)
        V[~ok] = np.nan
        θre[it] = _argmaxRows(x, V)[0]
    s = time.perf_counter() - tic
    js, it0 = stateNear(sGrid, R.θGrid, s0, θStar)
    dθ = θre - ch['θNext']
    key = dict(M = 'M7', ρ = ρ, scenario = scenario, nCand = nCand, ns = ns, nθ = nθ, knotsθ = 4,
               period = int(core['t']))
    rows.add(**key, rule = 'root', item = 'max|θ(grid V)-θ(resolveAt V)|', value = np.nanmax(np.abs(dθ)), seconds = s)
    rows.add(**key, rule = 'root', item = 'θ(grid V) at (s0, θ*)', value = ch['θNext'][it0, js], seconds = sec['root'])
    rows.add(**key, rule = 'root', item = 'θ(resolveAt V) at (s0, θ*)', value = θre[it0, js])
    rows.add(**key, rule = 'root', item = 'θ(resolveAt V)-θ(grid V) at (s0, θ*)', value = dθ[it0, js])
    rows.add(**key, rule = 'state', item = 's0 (legacy recursion)', value = s0, seconds = secS0)
    rows.add(**key, rule = 'state', item = 's_ at the state', value = sGrid[js])
    rows.add(**key, rule = 'state', item = 'θ_t at the state', value = R.θGrid[it0])
    print(f'  M7: max|Δθ| {np.nanmax(np.abs(dθ)):.2e}; at (s_={sGrid[js]:.4g}, θ_t={R.θGrid[it0]:.4f}): grid '
          f'{ch["θNext"][it0, js]:.6f}, resolveAt {θre[it0, js]:.6f}, Δ {dθ[it0, js]:+.2e} [{s:.0f}s]')


def itemM8(rows, ρ = 2.0, scenario = 'frVoting', ns = 50, nCand = 41):
    """ The design-state grid at the path: the root layer's design at the grid state nearest (s0, θ*) with
    nθ2D = 13 against 21 (θ* = 0.7383 is nearest 0.75 on both grids). """
    print(f'\n=== M8 ρ={ρ} {scenario} ns={ns} nCand={nCand} ===')
    m = modelAt(ρ, scenario, ns, nCand)
    θStar = float(m.db['θ'].xs(m.t0Year))
    s0, _ = s0Legacy(ρ, scenario, ns, nCand)
    at = {}
    for nθ in (13, 21):
        core, chs, sec, tCore, Ls = onePeriod(m, nθ, nCand, ns, rules = ('root',))
        θG, sGrid = Ls['root'].θGrid, core['sGrid']
        js, it0 = stateNear(sGrid, θG, s0, θStar)
        at[nθ] = float(chs['root']['θNext'][it0, js])
        key = dict(M = 'M8', ρ = ρ, scenario = scenario, nCand = nCand, ns = ns, nθ = nθ, knotsθ = 4,
                   period = int(core['t']))
        rows.add(**key, rule = 'root', item = 'θ at (s0, θ*)', value = at[nθ], seconds = sec['root'])
        rows.add(**key, rule = 'state', item = 's_ at the state', value = sGrid[js])
        rows.add(**key, rule = 'state', item = 'θ_t at the state', value = θG[it0])
        print(f'  M8 nθ2D={nθ}: θ at (s_={sGrid[js]:.4g}, θ_t={θG[it0]:.4f}) = {at[nθ]:.6f}')
    d = at[21] - at[13]
    rows.add(M = 'M8', ρ = ρ, scenario = scenario, nCand = nCand, ns = ns, nθ = 21, knotsθ = 4, rule = 'root',
             period = int(core['t']), item = 'θ(nθ=21)-θ(nθ=13) at (s0, θ*)', value = d)
    print(f'  M8: θ(nθ=21) - θ(nθ=13) = {d:+.6f}' + ('   ** MORE THAN 0.005 **' if abs(d) > 0.005 else ''))


# ---------------------------------------------------------------------------------------------- report
def report():
    files = sorted(glob.glob(os.path.join(OUT, 'rows_*.csv')))
    if not files:
        print('no rows_*.csv under', OUT)
        return
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index = True)
    df.to_csv(os.path.join(OUT, 'pilotDesignChoice.csv'), index = False)
    print(f'{len(df)} rows from {len(files)} files -> logs/pilotDesignChoice/pilotDesignChoice.csv')
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    pd.set_option('display.max_rows', 500)
    fmt = lambda v: '' if pd.isna(v) else (f'{v:.0f}' if float(v).is_integer() and abs(v) < 1e6 else f'{v:.4g}')
    for M in sorted(df['M'].unique()):
        d = df[df['M'] == M]
        idx = ['ρ', 'scenario', 'nCand', 'ns', 'nθ', 'knotsθ', 'period', 'item']
        print(f'\n===== {M} =====')
        tab = d.pivot_table(index = idx, columns = 'rule', values = 'value', aggfunc = 'last', dropna = False)
        tab = tab.dropna(how = 'all')
        print(tab.map(fmt).to_string())
        sec = d.dropna(subset = ['seconds']).pivot_table(index = ['ρ', 'scenario', 'nCand', 'nθ', 'knotsθ', 'item'],
                                                           columns = 'rule', values = 'seconds', aggfunc = 'last')
        if not sec.empty:
            print(f'-- seconds ({M})')
            print(sec.map(lambda v: '' if pd.isna(v) else f'{v:.1f}').to_string())


def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--item', choices = ['M1', 'M2', 'M34', 'M5', 'M7', 'M8', 'M78'])
    p.add_argument('--rho', type = float, default = 2.0)
    p.add_argument('--scenarios', nargs = '+', default = ['baseline', 'frVoting'])
    p.add_argument('--tag', default = None, help = 'rows file suffix (default: item and rho)')
    p.add_argument('--ns', type = int, default = None, help = 'override the state grid of M1/M2 (smoke runs)')
    p.add_argument('--nCand', type = int, default = None, help = 'override the candidate grid of M1/M2 (smoke runs)')
    p.add_argument('--report', action = 'store_true')
    a = p.parse_args()
    os.makedirs(OUT, exist_ok = True)
    if a.report:
        report()
        return 0
    tag = a.tag or f'{a.item}_rho{a.rho}_{"_".join(a.scenarios)}'
    rows = Rows(tag)
    tic = time.time()
    over = {k: v for k, v in (('ns', a.ns), ('nCand', a.nCand)) if v is not None}
    if a.item == 'M1':
        itemM1(rows, a.rho, a.scenarios, **over)
    elif a.item == 'M2':
        itemM2(rows, a.rho, a.scenarios, **over)
    elif a.item == 'M34':
        itemM34(rows)
    elif a.item == 'M5':
        itemM5(rows)
    elif a.item in ('M7', 'M78'):
        itemM7(rows, a.rho)
    if a.item in ('M8', 'M78'):
        itemM8(rows, a.rho)
    print(f'\nDONE {tag} [{time.time()-tic:.0f}s] -> {os.path.relpath(rows.path, REPO)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
