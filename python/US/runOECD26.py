r""" The cross-country test of section 7's model: the log model with the 'size' cost (Eq esc:AB) built from each OECD
country's data (oecd26.py), its predicted 2020 tax and design set against figure 1.1's relations.

Run:  .venv\Scripts\python.exe python\US\runOECD26.py                       every stage, both turnout readings
      ... --stage anchor layer1 layer2
      ... --turnout cps cses
      ... --countries USA GBR FRA                                           a subset (default: the 29)
      ... --force                                                           recompute rows already on disk
      ... --outdir DIR                                                      default results/oecd26
      ... --coarse                                                          small grids, for a quick check

Three stages, one csv each in --outdir, rows merged on their keys (runESC.mergeWrite); ρ = 1, common X.

  anchor  anchor.csv, one row per turnout reading: the U.S. at the OECD inputs, β imposed (oecd26.usBeta), ω
          calibrated against τ_2020 at the observed design and λ to eq esc:calibration, the design in force in
          2020 on the freely simulated path (ModelESC.calibrateWedge; the leaded choice is alg esc:leaded of
          writing/US/num_esc.tex).
  layer1  layer1.csv: every country at the anchor's β, ω and λ, entering 2020 with its observed design θ_c.
  layer2  layer2.csv: every country's ω calibrated to its own τ_2020 at θ_c, at the anchor's β and λ.

`turnout` 'cps' gives every economy the U.S. CPS propensities to vote; 'cses' each its own CSES turnout, the
anchor included (each reading has its own anchor). Luxembourg has no CSES election: its 'cses' rows carry
status 'noTurnout'. Every row carries `sample26` from the data step (python/paper/oecd26Sample.py).

Readouts per row (`readouts`), all at 2020 (t0):
  τ2020, spending2020   τPolicy_2020(θ_c) and 100·τ2020·(1-α), % of GDP (the inverse of τ0's construction)
  θChosen, indexChosen  θPolicy_2020(θ_c): the design chosen in 2020, in force in 2050; I = 1/(2-θ)
  θInForce, indexInForce, τInForce   the design in force in 2020 on the freely simulated path (chosen in 1990;
                        appendix G.1's reading and λ's target), and the 2020 tax under it
  R2020, Vtilde, fStar, f0   the return on the θ-pinned path, Eq esc:Vtilde, f(θ_c, τ2020), f(0, τ2020)
  closedFormGap, closedFormCorners   oecd26.closedFormCheck: the tax at θ ≡ 1 against eq (1.4) at each date's ν
  nEqMax, nCandMax, nFallback   the tax rule's counts over the design recursion and the pinned solve
                        (policy.multiplicityColumns); under log the tax is unique, so nEqMax > 1 is a defect

Resumable: a row on disk is reused when its `inputsKey` (oecd26.inputsKey over the stage, the country's inputs,
β, the anchor's ω and λ and the grid settings) equals the current one and its status is 'ok'; --force
recomputes. A layer refuses an anchor row whose key does not match the current U.S. inputs and β: rerun the
anchor stage after any recalibration of the U.S. (crossCuttingFindings #13).
"""
import os, sys, argparse, time, json
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)

import oecd26
from runESC import mergeWrite, _keyOf, _keyCell
from modelESC import WEDGE_BRACKET
from policy import multiplicityColumns, mergeMultiplicity

OUTDIR = os.path.join(REPO, 'results', 'oecd26')
# The paper's cost and variant (python/paper/config.py: US['esc']['spec'], US['esc']['phi'], US['commonX']).
SPEC, PHI, COMMONX = 'size', 0.5, True
KEYANCHOR = ['turnout', 'spec', 'phi', 'commonX']
KEYLAYER = ['turnout', 'spec', 'phi', 'commonX', 'iso3']
STAGES = ('anchor', 'layer1', 'layer2')
SETTINGS = {'fine':   {'n': 101, 'nθ': 41, 'nθCand': 121, 'nScan': 12},
            'coarse': {'n': 51, 'nθ': 21, 'nθCand': 41, 'nScan': 6}}


def settings(coarse = False):
    """ The grid settings of a run: the LOG tax grid (n nodes, oecd26.GS otherwise), the design state grid and
    candidates of LeadedLOG, the λ scan and its bracket (ModelESC.WEDGE_BRACKET). Part of every row's key. """
    s = dict(SETTINGS['coarse' if coarse else 'fine'])
    return s | {'grid': 'coarse' if coarse else 'fine', 'bracket': list(WEDGE_BRACKET[SPEC]), 'spec': SPEC, 'phi': PHI}


def _build(inp, β, ω, λ, cfg):
    return oecd26.build(inp, β, ω, λ, spec = SPEC, phi = PHI, gs = oecd26.GS | {'n': cfg['n']},
                        nθ = cfg['nθ'], nθCand = cfg['nθCand'])


def readouts(m):
    """ The 2020 readouts of a solved country (module docstring), with the merged counts. """
    t0 = m.t0Year
    sols = m.ESC.solveBackward()
    multESC = m.ESC.lastMultiplicity
    θD = float(m.db['θ'].xs(t0))
    τ = m.ESC.τAt(t0, θD)
    θChosen = m.ESC.choiceAt(sols, t0, θD)
    k = int(np.argmin(np.abs(sols[t0]['θGrid'] - θD)))
    θIn = m.leadedDesignAtT0(sols)
    τIn = m.ESC.τAt(t0, θIn)
    pin = m.solvePEE_LOG()                                  # θ ≡ θ_c over the horizon
    τPin = float(pin['τ'].xs(t0))
    gap, corners = oecd26.closedFormCheck(m)
    α = float(m.db['α'].xs(t0))
    with m.B.cacheParams():
        V, fStar, f0 = (float(m.B.Vtilde(t0)), float(m.B.fWedge(θD, τ, t0)), float(m.B.fWedge(0., τ, t0)))
    mult = mergeMultiplicity([multESC, pin.get('multiplicity')])
    return {'ν2020': float(m.db['ν'].xs(t0)), 'Vtilde': V, 'θData': θD, 'τ2020': τ, 'spending2020': 100*τ*(1 - α),
            'θChosen': θChosen, 'indexChosen': float(oecd26.indexFromTheta(θChosen)),
            'atBoundChosen': bool(sols[t0]['atBoundθ'][k]), 'θStateSpread': float(sols[t0]['stateSpread']),
            'θInForce': θIn, 'indexInForce': float(oecd26.indexFromTheta(θIn)), 'τInForce': τIn,
            'τPinGap': abs(τPin - τ), 'R2020': float(pin['report']['R'].xs(t0)), 'fStar': fStar, 'f0': f0,
            'closedFormGap': gap, 'closedFormCorners': corners} | multiplicityColumns(mult)


def _dataColumns(inp):
    return {'iso3': inp['iso3'], 'country': inp['country'], 'sample26': inp['sample26'],
            'spendingData': inp['spending'], 'τData': inp['τ0'], 'indexData': inp['index'],
            'θRaw': inp['θRaw'], 'θClipped': bool(inp['θRaw'] != inp['θ'])}


def _onDisk(path, key, values):
    """ The row of csv `path` whose `key` columns equal `values` (canonical strings, runESC._keyOf), or None.
    Floats are read round-trip exact: pandas' default parser misses the written value by an ulp in about one
    case in six, and an anchor read back must be the anchor that was computed. """
    if not os.path.exists(path):
        return None
    d = pd.read_csv(path, dtype = {'inputsKey': str, 'anchorKey': str}, float_precision = 'round_trip')
    if any(k not in d.columns for k in key):
        return None
    hit = d[_keyOf(d, key).isin(pd.MultiIndex.from_arrays([[_keyCell(v)] for v in values]))]
    if len(hit) > 1:
        raise ValueError('{}: {} rows on the key {}'.format(path, len(hit), dict(zip(key, values))))
    return None if hit.empty else hit.iloc[0].to_dict()


def anchorKey(inp, β, cfg):
    return oecd26.inputsKey('anchor', oecd26.modelInputs(inp), β, cfg)


# ---------------------------------------------------------------- stage: the anchor
def stageAnchor(turnout, outdir, cfg, ref, force = False):
    """ The U.S. at the OECD inputs: ω and λ calibrated, β imposed. `ref`: oecd26.usBeta()'s (β, ω seed,
    source), read once per run so that every stage of a run imposes one β. Returns the anchor row (dict). """
    path = os.path.join(outdir, 'anchor.csv')
    inp = oecd26.countryInputs('USA', turnout)
    β, ωSeed, βSource = ref
    key = anchorKey(inp, β, cfg)
    keyVals = [turnout, SPEC, PHI, COMMONX]
    old = _onDisk(path, KEYANCHOR, keyVals)
    if not force and old is not None and old.get('inputsKey') == key and old.get('status') == 'ok':
        print('[anchor {}] on disk: ω={:.6f} λ={:.6f}'.format(turnout, old['ω'], old['p']))
        return old
    tic = time.time()
    m = _build(inp, β, ωSeed, None, cfg)
    row = dict(zip(KEYANCHOR, keyVals)) | _dataColumns(inp) | {'β': β, 'βSource': βSource}
    try:
        rec = m.calibrateWedge(spec = SPEC, phi = PHI, bracket = tuple(cfg['bracket']), nScan = cfg['nScan'])
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
    mergeWrite(path, [row], KEYANCHOR)
    if row['status'] == 'ok':
        print('[anchor {}] ω={:.6f} λ={:.6f}  θ={:.4f} -> in force {:.4f}, chosen {:.4f}  τ={:.4f}  R={:.4f}  '
              '({:.0f}s)'.format(turnout, row['ω'], row['p'], row['θData'], row['θInForce'], row['θChosen'],
                                 row['τ2020'], row['R2020'], row['time']))
    else:
        print('[anchor {}] FAILED: {}'.format(turnout, row['message']))
    return row


def anchorRow(turnout, outdir, cfg, ref):
    """ The anchor row of `turnout` on disk, refused unless it is 'ok' and keyed on the current U.S. inputs, the
    β of `ref` (oecd26.usBeta()) and the settings. """
    path = os.path.join(outdir, 'anchor.csv')
    row = _onDisk(path, KEYANCHOR, [turnout, SPEC, PHI, COMMONX])
    if row is None or row.get('status') != 'ok':
        raise SystemExit('no calibrated anchor for turnout {!r} in {}: run --stage anchor'.format(turnout, path))
    if row['inputsKey'] != anchorKey(oecd26.countryInputs('USA', turnout), ref[0], cfg):
        raise SystemExit('the anchor row for turnout {!r} in {} was computed at other inputs, β or settings: '
                         'rerun --stage anchor (with --force)'.format(turnout, path))
    return row


# ---------------------------------------------------------------- stages: the two layers
def stageLayer(layer, turnout, isos, outdir, anchor, cfg, force = False):
    """ layer 'layer1' (the anchor's ω) or 'layer2' (ω calibrated per country), for the countries `isos`. """
    path = os.path.join(outdir, layer + '.csv')
    data = oecd26.readData()
    β, ωA, λA = float(anchor['β']), float(anchor['ω']), float(anchor['p'])
    rows = []
    for iso in isos:
        keyVals = [turnout, SPEC, PHI, COMMONX, iso]
        base = dict(zip(KEYLAYER, keyVals)) | {'layer': layer, 'β': β, 'ωAnchor': ωA, 'p': λA,
                                               'anchorKey': anchor['inputsKey'], 'grid': cfg['grid']}
        try:
            inp = oecd26.countryInputs(iso, turnout, data)
        except oecd26.NoTurnout as e:
            rows.append(base | {'country': data[0].at[iso, 'country'], 'sample26': bool(data[2].at[iso, 'sample26']),
                                'status': 'noTurnout', 'message': str(e)} | multiplicityColumns(None))
            mergeWrite(path, rows, KEYLAYER)
            print('[{} {}] {:<4} no CSES turnout: skipped'.format(layer, turnout, iso))
            continue
        key = oecd26.inputsKey(layer, oecd26.modelInputs(inp), β, ωA, λA, cfg)
        old = _onDisk(path, KEYLAYER, keyVals)
        if not force and old is not None and old.get('inputsKey') == key and old.get('status') == 'ok':
            continue
        tic = time.time()
        row = base | _dataColumns(inp) | {'inputsKey': key}
        try:
            m = _build(inp, β, ωA, λA, cfg)
            ω, conv, res = ωA, True, 0.
            if layer == 'layer2':
                cal = m.calibrate()
                ω, res = float(cal['pars']['ω']), float(np.max(np.abs(cal['residual'])))
            row |= {'ω': ω, 'converged': conv, 'calResidual': res, 'status': 'ok', 'message': ''} | readouts(m)
        except Exception as e:
            row |= {'ω': np.nan, 'converged': False, 'status': 'failed',
                    'message': '{}: {}'.format(type(e).__name__, e)} | multiplicityColumns(None)
        row['time'] = time.time() - tic
        rows.append(row)
        mergeWrite(path, rows, KEYLAYER)
        if row['status'] == 'ok':
            flag = '' if row['nEqMax'] == 1 and row['nFallback'] == 0 else \
                '  COUNTS nEqMax={} nFallback={}'.format(row['nEqMax'], row['nFallback'])
            print('[{} {}] {:<4} ω={:.4f}  θ={:.3f} -> chosen {:.3f} (in force {:.3f})  τ={:.4f} (data {:.4f})'
                  '  ({:.1f}s){}'.format(layer, turnout, iso, ω, row['θData'], row['θChosen'], row['θInForce'],
                                         row['τ2020'], row['τData'], row['time'], flag))
        else:
            print('[{} {}] {:<4} FAILED: {}'.format(layer, turnout, iso, row['message']))
    return rows


def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--stage', nargs = '*', default = list(STAGES), choices = STAGES)
    p.add_argument('--turnout', nargs = '*', default = list(oecd26.TURNOUT), choices = oecd26.TURNOUT)
    p.add_argument('--countries', nargs = '*', default = None, help = 'ISO3 codes (default: the 29)')
    p.add_argument('--force', action = 'store_true', help = 'recompute rows already on disk')
    p.add_argument('--outdir', default = OUTDIR)
    p.add_argument('--coarse', action = 'store_true', help = 'small grids (SETTINGS["coarse"]), for a quick check')
    a = p.parse_args()
    cfg = settings(a.coarse)
    isos = a.countries or oecd26.countries()
    unknown = set(isos) - set(oecd26.countries())
    if unknown:
        raise SystemExit('not in data/oecd29.csv: {}'.format(sorted(unknown)))
    os.makedirs(a.outdir, exist_ok = True)
    tic = time.time()
    ref = oecd26.usBeta()
    print('β = {:.6f} from {}'.format(ref[0], ref[2]))
    for turnout in a.turnout:
        anchor = stageAnchor(turnout, a.outdir, cfg, ref, a.force) if 'anchor' in a.stage else None
        for layer in ('layer1', 'layer2'):
            if layer in a.stage:
                anchor = anchor if anchor is not None and anchor.get('status') == 'ok' else \
                    anchorRow(turnout, a.outdir, cfg, ref)
                stageLayer(layer, turnout, isos, a.outdir, anchor, cfg, a.force)
    print('\n-> {}  ({:.0f}s)'.format(os.path.relpath(a.outdir, REPO), time.time() - tic))
    return 0


if __name__ == '__main__':
    sys.exit(main())
