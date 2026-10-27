r""" The cross-country test of section 7's model: the log model with a cost of Eq esc:AB, or none, built from each
OECD country's data (oecd26.py), its predicted 2020 tax and design set against figure 1.1's relations.

Run:  .venv\Scripts\python.exe python\US\runOECD26.py                       every stage, both turnout readings
      ... --stage anchor layer1 layer2
      ... --turnout cps cses
      ... --spec size sizePiR none                                          the costs (default: the paper's)
      ... --betaRule common commonR                                         the β rules (default: the paper's)
      ... --countries USA GBR FRA                                           a subset (default: the 29)
      ... --force                                                           recompute rows already on disk
      ... --outdir DIR                                                      default results/oecd26
      ... --coarse                                                          small grids, for a quick check

The defaults of --spec and --betaRule are python/paper/config.py's US['oecd26'] (`paperVariant`). Three stages, one
csv each in --outdir, rows merged on their keys (runESC.mergeWrite); ρ = 1, common X. Every (spec, betaRule) asked
for runs in turn, the anchor once per spec and turnout.

  anchor  anchor.csv, one row per spec and turnout reading: the U.S. at the OECD inputs, β imposed (oecd26.usBeta),
          ω calibrated against τ_2020 at the observed design and the cost parameter to eq esc:calibration, the
          design in force in 2020 on the freely simulated path (ModelESC.calibrateWedge; the leaded choice is alg
          esc:leaded of writing/US/num_esc.tex). Its betaRule is always 'common'.
  layer1  layer1.csv: every country at the anchor's ω and cost parameter, entering 2020 with its observed design
          θ_c; β the anchor's ('common') or calibrated alone to the anchor's R2020 ('commonR').
  layer2  layer2.csv: every country's ω calibrated to its own τ_2020 at θ_c, at the anchor's cost parameter; β the
          anchor's ('common'), or (β, ω) calibrated to (the anchor's R2020, the country's τ_2020) ('commonR').

`spec`, the cost: 'size' (Eq esc:AB, `p` = λ), 'sizePiR' (λ·Π_t/R_t: the anchor's λ in `p`, each country's own
π = Π/R, every solve iterating π to its own path's, modelESC), 'none' (no cost: the anchor calibrates ω alone,
and no row reads a design: p, θChosen, θInForce, τInForce, fStar, f0 are NaN and the status 'ok'; a costless
design choice is the corner of proposition 4). `phi` is the dummy 0.5 under every spec.

`turnout` 'cps' gives every economy the U.S. CPS propensities to vote; 'cses' each its own CSES turnout, the
anchor included (each reading has its own anchor). Luxembourg has no CSES election: its 'cses' rows carry
status 'noTurnout'. Every row carries `sample26` from the data step (python/paper/oecd26Sample.py).

Readouts per row (`readouts`), all at 2020 (t0):
  τ2020, spending2020   the 2020 tax at θ_c and 100·τ2020·(1-α), % of GDP (the inverse of τ0's construction):
                        τPolicy_2020(θ_c) under 'size', the θ-pinned path's (solvePEE_LOG) under 'sizePiR', 'none'
  θChosen, indexChosen  θPolicy_2020(θ_c): the design chosen in 2020, in force in 2050; I = 1/(2-θ)
  θInForce, indexInForce, τInForce   the design in force in 2020 on the freely simulated path (chosen in 1990;
                        appendix G.1's reading and λ's target), and the 2020 tax under it
  R2020, Vtilde, fStar, f0   the return on the θ-pinned path, Eq esc:Vtilde, f(θ_c, τ2020), f(0, τ2020)
  τPinGap               |the pinned path's τ_2020 - τPolicy_2020(θ_c)|: rounding under 'size'; under 'sizePiR' the
                        effect of the two paths' different π; NaN under 'none'
  ΠR2020, λEff2020, ΠRgap   'sizePiR' only: π_2020 on the θ-pinned path, p·ΠR2020 (the cost parameter the country
                        faces in 2020), the larger of the two fixed points' last max|Δπ| (below modelESC.ΠR_TOL).
                        NaN under 'size' and 'none', as on the rows written before these columns
  closedFormGap, closedFormCorners   oecd26.closedFormCheck: the tax at θ ≡ 1 against eq (1.4) at each date's ν
  nEqMax, nCandMax, nFallback   the tax rule's counts over the design recursion and the pinned solve
                        (policy.multiplicityColumns); under log the tax is unique, so nEqMax > 1 is a defect
Under 'sizePiR' the free-path readouts (θChosen, θInForce, τInForce) are solveLeaded(pinAtT0 = False)'s at its own
fixed point in π and the pinned ones (τ2020, R2020, fStar, f0, ΠR2020) solvePEE_LOG()'s at its own; each iterates
to its own path's π, so neither solve's π serves the other. A 'commonR' layer row's `β` is the country's calibrated
β, `βAnchor` and `RTarget` the anchor's β and R2020.

Resumable: rows are keyed on (turnout, spec, phi, commonX, betaRule[, iso3]); a csv written before the betaRule
column is read as betaRule 'common', and rewritten so before the next merge (`migrate`). A row on disk is reused
when its `inputsKey` (oecd26.inputsKey over the stage, the country's inputs, β, the anchor's ω and cost parameter,
under 'commonR' the anchor's R2020, and the settings: grids, spec, bracket, and betaRule unless 'common') equals
the current one and its status is 'ok'; --force recomputes. A layer refuses an anchor row whose key does not match
the current U.S. inputs and β: rerun the anchor stage after any recalibration of the U.S. (crossCuttingFindings
#13).
"""
import os, sys, argparse, time, json, importlib.util
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
CWD = os.getcwd()                 # where a relative --outdir points: runESC's import changes the directory to HERE
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)

import oecd26
from runESC import mergeWrite, _keyOf, _keyCell
from modelESC import WEDGE_BRACKET
from policy import multiplicityColumns, mergeMultiplicity

OUTDIR = os.path.join(REPO, 'results', 'oecd26')
PAPERCONFIG = os.path.join(REPO, 'python', 'paper', 'config.py')
SPECS = ('size', 'sizePiR', 'none')
BETARULES = oecd26.BETARULES
# phi: the dummy key of the proportional costs (python/paper/config.py US['esc']['phi']); common X, the paper's.
PHI, COMMONX = 0.5, True
KEYANCHOR = ['turnout', 'spec', 'phi', 'commonX', 'betaRule']
KEYLAYER = KEYANCHOR + ['iso3']
# The value of a key column in a csv written before the column existed (migrate, _onDisk).
LEGACY = {'betaRule': 'common'}
STAGES = ('anchor', 'layer1', 'layer2')
SETTINGS = {'fine':   {'n': 101, 'nθ': 41, 'nθCand': 121, 'nScan': 12},
            'coarse': {'n': 51, 'nθ': 21, 'nθCand': 41, 'nScan': 6}}
DESIGN = ('θChosen', 'indexChosen', 'atBoundChosen', 'θStateSpread', 'θInForce', 'indexInForce', 'τInForce')


def paperVariant():
    """ python/paper/config.py's US['oecd26'], the paper's variant, read from the file (the CLI's defaults). """
    sp = importlib.util.spec_from_file_location('_paperConfig', PAPERCONFIG)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.US['oecd26']


def settings(coarse = False, spec = 'size', betaRule = 'common'):
    """ The settings of a run: the LOG tax grid (n nodes, oecd26.GS otherwise), the design state grid and candidates
    of LeadedLOG, the cost scan and its bracket (ModelESC.WEDGE_BRACKET; None under 'none'), spec and phi, and
    betaRule when it is not 'common' (the β-common rows keep the keys they had before the rule). Part of every
    row's key. """
    s = dict(SETTINGS['coarse' if coarse else 'fine'])
    s |= {'grid': 'coarse' if coarse else 'fine', 'bracket': None if spec == 'none' else list(WEDGE_BRACKET[spec]),
          'spec': spec, 'phi': PHI}
    return s if betaRule == 'common' else s | {'betaRule': betaRule}


def anchorSettings(cfg):
    """ The settings of a run's anchor: cfg without betaRule (the anchor is always 'common'). """
    return {k: v for k, v in cfg.items() if k != 'betaRule'}


def _build(inp, β, ω, λ, cfg, R0 = None, calibrateω = True):
    spec = cfg['spec']
    return oecd26.build(inp, β, ω, None if spec == 'none' else λ, spec = spec, phi = cfg['phi'],
                        gs = oecd26.GS | {'n': cfg['n']}, nθ = cfg['nθ'], nθCand = cfg['nθCand'],
                        betaRule = cfg.get('betaRule', 'common'), R0 = R0, calibrateω = calibrateω)


def readouts(m):
    """ The 2020 readouts of a solved country (module docstring), with the merged counts. The spec is the model's
    (db['wedgeSpec']; None reads as 'none'). """
    t0 = m.t0Year
    spec = m.db.get('wedgeSpec')
    θD = float(m.db['θ'].xs(t0))
    mult, gaps = [], []
    design, τLed = dict.fromkeys(DESIGN, np.nan), np.nan
    if spec is not None:
        if spec == 'sizePiR':
            led = m.solveLeaded(pinAtT0 = False)            # the free path at its own fixed point in π
            sols, θIn, τIn = led['sols'], float(led['θ'].xs(t0)), float(led['τ'].xs(t0))
            mult.append(led['multiplicity'])
            gaps.append(led['ΠRgap'])
            τLed = m.ESC.τAt(t0, θD)                         # at that path's π, which db now holds
        else:
            sols = m.ESC.solveBackward()
            mult.append(m.ESC.lastMultiplicity)
            τLed = m.ESC.τAt(t0, θD)
            θIn = m.leadedDesignAtT0(sols)
            τIn = m.ESC.τAt(t0, θIn)
        θChosen = m.ESC.choiceAt(sols, t0, θD)
        k = int(np.argmin(np.abs(sols[t0]['θGrid'] - θD)))
        design = {'θChosen': θChosen, 'indexChosen': float(oecd26.indexFromTheta(θChosen)),
                  'atBoundChosen': bool(sols[t0]['atBoundθ'][k]), 'θStateSpread': float(sols[t0]['stateSpread']),
                  'θInForce': θIn, 'indexInForce': float(oecd26.indexFromTheta(θIn)), 'τInForce': τIn}
    pin = m.solvePEE_LOG()                                  # θ ≡ θ_c over the horizon; under 'sizePiR' at its own π
    mult.append(pin.get('multiplicity'))
    τPin = float(pin['τ'].xs(t0))
    τ = τPin if spec in (None, 'sizePiR') else τLed
    pir = dict.fromkeys(('ΠR2020', 'λEff2020', 'ΠRgap'), np.nan)
    if spec == 'sizePiR':
        gaps.append(pin['ΠRgap'])
        π = float(m.db['wedgeΠR'].xs(t0))                  # the pinned path's π_2020
        pir = {'ΠR2020': π, 'λEff2020': float(m.db['wedgeP'])*π, 'ΠRgap': float(max(gaps))}
    α = float(m.db['α'].xs(t0))
    lag = '[t-1]' if spec == 'sizePiR' else ''              # f(θ_2020, τ_2020) carries π_2020
    with m.B.cacheParams():
        V = float(m.B.Vtilde(t0))
        fStar, f0 = ((np.nan, np.nan) if spec is None else
                     (float(m.B.fWedge(θD, τ, t0, lag)), float(m.B.fWedge(0., τ, t0, lag))))
    gap, corners = oecd26.closedFormCheck(m)
    return ({'ν2020': float(m.db['ν'].xs(t0)), 'Vtilde': V, 'θData': θD, 'τ2020': τ, 'spending2020': 100*τ*(1 - α)}
            | design | {'τPinGap': abs(τPin - τLed), 'R2020': float(pin['report']['R'].xs(t0)), 'fStar': fStar,
                         'f0': f0} | pir
            | {'closedFormGap': gap, 'closedFormCorners': corners} | multiplicityColumns(mergeMultiplicity(mult)))


def _dataColumns(inp):
    return {'iso3': inp['iso3'], 'country': inp['country'], 'sample26': inp['sample26'],
            'spendingData': inp['spending'], 'τData': inp['τ0'], 'indexData': inp['index'],
            'θRaw': inp['θRaw'], 'θClipped': bool(inp['θRaw'] != inp['θ'])}


def _read(path):
    """ csv `path` with floats read round-trip exact: pandas' default parser misses the written value by an ulp in
    about one case in six, and an anchor read back must be the anchor that was computed. """
    return pd.read_csv(path, dtype = {'inputsKey': str, 'anchorKey': str}, float_precision = 'round_trip')


def _onDisk(path, key, values):
    """ The row of csv `path` whose `key` columns equal `values` (canonical strings, runESC._keyOf), or None. A key
    column the csv lacks reads as its LEGACY value. """
    if not os.path.exists(path):
        return None
    d = _read(path)
    for k, v in LEGACY.items():
        if k in key and k not in d.columns:
            d[k] = v
    if any(k not in d.columns for k in key):
        return None
    hit = d[_keyOf(d, key).isin(pd.MultiIndex.from_arrays([[_keyCell(v)] for v in values]))]
    if len(hit) > 1:
        raise ValueError('{}: {} rows on the key {}'.format(path, len(hit), dict(zip(key, values))))
    return None if hit.empty else hit.iloc[0].to_dict()


def migrate(path):
    """ Rewrite csv `path` with the key columns it was written without, at their LEGACY values (betaRule 'common',
    the one rule before the column), so that mergeWrite matches its rows to the current keys rather than keeping
    them beside recomputed twins. No-op when the file is absent or has every column. """
    if not os.path.exists(path):
        return
    d = _read(path)
    lack = {k: v for k, v in LEGACY.items() if k not in d.columns}
    if lack:
        d.assign(**lack).to_csv(path, index = False)


def _write(path, rows, key):
    migrate(path)
    mergeWrite(path, rows, key)


def anchorKey(inp, β, cfg):
    return oecd26.inputsKey('anchor', oecd26.modelInputs(inp), β, anchorSettings(cfg))


# ---------------------------------------------------------------- stage: the anchor
def stageAnchor(turnout, outdir, cfg, ref, force = False):
    """ The U.S. at the OECD inputs under cfg's spec: ω and the cost parameter calibrated (ω alone under 'none'), β
    imposed; cfg's betaRule is ignored (anchorSettings). `ref`: oecd26.usBeta()'s (β, ω seed, source), read once
    per run so that every stage of a run imposes one β. Returns the anchor row (dict). """
    cfg = anchorSettings(cfg)
    spec = cfg['spec']
    path = os.path.join(outdir, 'anchor.csv')
    inp = oecd26.countryInputs('USA', turnout)
    β, ωSeed, βSource = ref
    key = anchorKey(inp, β, cfg)
    keyVals = [turnout, spec, PHI, COMMONX, 'common']
    old = _onDisk(path, KEYANCHOR, keyVals)
    if not force and old is not None and old.get('inputsKey') == key and old.get('status') == 'ok':
        print('[anchor {} {}] on disk: ω={:.6f} p={:.6f}'.format(spec, turnout, old['ω'], old['p']))
        return old
    tic = time.time()
    m = _build(inp, β, ωSeed, None, cfg)
    row = dict(zip(KEYANCHOR, keyVals)) | _dataColumns(inp) | {'β': β, 'βSource': βSource}
    try:
        if spec == 'none':
            m.calibrate()
            rec = {'converged': True, 'p': np.nan, 'residual': np.nan, 'scan': [], 'message': 'no cost: ω calibrated'}
        else:
            rec = m.calibrateWedge(spec = spec, phi = PHI, bracket = tuple(cfg['bracket']), nScan = cfg['nScan'])
    except Exception as e:
        rec = {'converged': False, 'p': np.nan, 'residual': np.nan, 'scan': [],
               'message': '{}: {}'.format(type(e).__name__, e)}
    row |= {'p': rec['p'], 'designResidual': rec['residual'], 'converged': bool(rec['converged']),
            'message': rec.get('message', ''), 'scan': json.dumps(rec.get('scan', []))}
    if rec['converged']:
        t0 = m.t0Year
        row |= {'ω': float(m.db['ω'].xs(t0)), 'status': 'ok'} | readouts(m)
        row['τResidual'] = row['τ2020'] - inp['τ0']
    else:
        row |= {'ω': np.nan, 'status': 'failed'} | multiplicityColumns(None)
    row |= {'inputsKey': key, 'grid': cfg['grid'], 'time': time.time() - tic}
    os.makedirs(outdir, exist_ok = True)
    _write(path, [row], KEYANCHOR)
    if row['status'] == 'ok':
        print('[anchor {} {}] ω={:.6f} p={:.6f}  θ={:.4f} -> in force {:.4f}, chosen {:.4f}  τ={:.4f}  R={:.4f}  '
              '({:.0f}s)'.format(spec, turnout, row['ω'], row['p'], row['θData'], row['θInForce'], row['θChosen'],
                                 row['τ2020'], row['R2020'], row['time']))
    else:
        print('[anchor {} {}] FAILED: {}'.format(spec, turnout, row['message']))
    return row


def anchorRow(turnout, outdir, cfg, ref):
    """ The anchor row of `turnout` and cfg's spec on disk, refused unless it is 'ok' and keyed on the current U.S.
    inputs, the β of `ref` (oecd26.usBeta()) and the settings. """
    cfg = anchorSettings(cfg)
    path = os.path.join(outdir, 'anchor.csv')
    row = _onDisk(path, KEYANCHOR, [turnout, cfg['spec'], PHI, COMMONX, 'common'])
    if row is None or row.get('status') != 'ok':
        raise SystemExit('no calibrated {} anchor for turnout {!r} in {}: run --stage anchor'.format(
            cfg['spec'], turnout, path))
    if row['inputsKey'] != anchorKey(oecd26.countryInputs('USA', turnout), ref[0], cfg):
        raise SystemExit('the {} anchor row for turnout {!r} in {} was computed at other inputs, β or settings: '
                         'rerun --stage anchor (with --force)'.format(cfg['spec'], turnout, path))
    return row


# ---------------------------------------------------------------- stages: the two layers
def stageLayer(layer, turnout, isos, outdir, anchor, cfg, force = False):
    """ layer 'layer1' (the anchor's ω) or 'layer2' (ω calibrated per country), for the countries `isos`, at cfg's
    spec and betaRule; `anchor` is the anchor row of cfg's spec and `turnout`. """
    spec, rule = cfg['spec'], cfg.get('betaRule', 'common')
    path = os.path.join(outdir, layer + '.csv')
    data = oecd26.readData()
    β, ωA, λA = float(anchor['β']), float(anchor['ω']), float(anchor['p'])
    RA = float(anchor['R2020']) if rule == 'commonR' else None
    rows = []
    for iso in isos:
        keyVals = [turnout, spec, PHI, COMMONX, rule, iso]
        base = dict(zip(KEYLAYER, keyVals)) | {'layer': layer, 'β': β, 'ωAnchor': ωA, 'p': λA,
                                               'anchorKey': anchor['inputsKey'], 'grid': cfg['grid']}
        if rule == 'commonR':
            base |= {'βAnchor': β, 'RTarget': RA}
        try:
            inp = oecd26.countryInputs(iso, turnout, data)
        except oecd26.NoTurnout as e:
            rows.append(base | {'country': data[0].at[iso, 'country'], 'sample26': bool(data[2].at[iso, 'sample26']),
                                'status': 'noTurnout', 'message': str(e)} | multiplicityColumns(None))
            _write(path, rows, KEYLAYER)
            print('[{} {} {} {}] {:<4} no CSES turnout: skipped'.format(layer, spec, rule, turnout, iso))
            continue
        key = oecd26.inputsKey(layer, oecd26.modelInputs(inp), β, ωA, λA, cfg, *([RA] if rule == 'commonR' else []))
        old = _onDisk(path, KEYLAYER, keyVals)
        if not force and old is not None and old.get('inputsKey') == key and old.get('status') == 'ok':
            continue
        tic = time.time()
        row = base | _dataColumns(inp) | {'inputsKey': key}
        try:
            m = _build(inp, β, ωA, λA, cfg, R0 = RA, calibrateω = layer == 'layer2')
            ω, βi, conv, res = ωA, β, True, 0.
            if m._calPars:                                  # layer 2, or β under 'commonR'
                cal = m.calibrate()
                ω, βi = float(cal['pars'].get('ω', ωA)), float(cal['pars'].get('β', β))
                res = float(np.max(np.abs(cal['residual'])))
            row |= ({'ω': ω, 'converged': conv, 'calResidual': res, 'status': 'ok', 'message': ''}
                    | ({'β': βi} if rule == 'commonR' else {}) | readouts(m))
        except Exception as e:
            row |= {'ω': np.nan, 'converged': False, 'status': 'failed',
                    'message': '{}: {}'.format(type(e).__name__, e)} | multiplicityColumns(None)
        row['time'] = time.time() - tic
        rows.append(row)
        _write(path, rows, KEYLAYER)
        if row['status'] == 'ok':
            flag = '' if row['nEqMax'] == 1 and row['nFallback'] == 0 else \
                '  COUNTS nEqMax={} nFallback={}'.format(row['nEqMax'], row['nFallback'])
            print('[{} {} {} {}] {:<4} ω={:.4f}{}  θ={:.3f} -> chosen {:.3f} (in force {:.3f})  τ={:.4f} (data {:.4f})'
                  '  ({:.1f}s){}'.format(layer, spec, rule, turnout, iso, ω,
                                         '  β={:.6f}'.format(row['β']) if rule == 'commonR' else '', row['θData'],
                                         row['θChosen'], row['θInForce'], row['τ2020'], row['τData'], row['time'],
                                         flag))
        else:
            print('[{} {} {} {}] {:<4} FAILED: {}'.format(layer, spec, rule, turnout, iso, row['message']))
    return rows


def main():
    v = paperVariant()
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--stage', nargs = '*', default = list(STAGES), choices = STAGES)
    p.add_argument('--turnout', nargs = '*', default = list(oecd26.TURNOUT), choices = oecd26.TURNOUT)
    p.add_argument('--spec', nargs = '*', default = [v['spec']], choices = SPECS,
                   help = "the costs, each in turn (default: config.US['oecd26']['spec'])")
    p.add_argument('--betaRule', nargs = '*', default = [v['betaRule']], choices = BETARULES,
                   help = "the β rules of the layers, each in turn (default: config.US['oecd26']['betaRule'])")
    p.add_argument('--countries', nargs = '*', default = None, help = 'ISO3 codes (default: the 29)')
    p.add_argument('--force', action = 'store_true', help = 'recompute rows already on disk')
    p.add_argument('--outdir', default = OUTDIR)
    p.add_argument('--coarse', action = 'store_true', help = 'small grids (SETTINGS["coarse"]), for a quick check')
    a = p.parse_args()
    a.outdir = os.path.abspath(os.path.join(CWD, a.outdir))
    isos = a.countries or oecd26.countries()
    unknown = set(isos) - set(oecd26.countries())
    if unknown:
        raise SystemExit('not in data/oecd29.csv: {}'.format(sorted(unknown)))
    os.makedirs(a.outdir, exist_ok = True)
    tic = time.time()
    ref = oecd26.usBeta()
    print('β = {:.6f} from {}'.format(ref[0], ref[2]))
    for spec in a.spec:
        cfgA = settings(a.coarse, spec)
        for turnout in a.turnout:
            anchor = stageAnchor(turnout, a.outdir, cfgA, ref, a.force) if 'anchor' in a.stage else None
            for rule in a.betaRule:
                cfg = settings(a.coarse, spec, rule)
                for layer in ('layer1', 'layer2'):
                    if layer in a.stage:
                        anchor = anchor if anchor is not None and anchor.get('status') == 'ok' else \
                            anchorRow(turnout, a.outdir, cfgA, ref)
                        stageLayer(layer, turnout, isos, a.outdir, anchor, cfg, a.force)
    print('\n-> {}  ({:.0f}s)'.format(os.path.relpath(a.outdir, REPO), time.time() - tic))
    return 0


if __name__ == '__main__':
    sys.exit(main())
