r""" The cross-country test's loader and driver (oecd26.py, runOECD26.py); the two calibrations of the cost parameter
are test_oecd26Anchor.py's (slow).

Run:  .venv\Scripts\python.exe python\US\test_oecd26.py        (~2 min)

  L  The loader reproduces data/oecd29*.csv for the 29: ν over DATES against oecd29_population.csv (wpp2024, with
     the 1960 and 2110 copies), γ_i, y_i and Ṽ against the distribution file and oecd29.csv's *_usPct, I against
     bbIndex, θ = clip(2 - 1/I), τ0 = spending/(1 - α), μ (cps: the U.S. workbook; cses: mu*_usPct, and NoTurnout
     for Luxembourg); on the built model hηRatio = y_i, Vtilde and θ on every date, θ surviving updateAuxPars,
     setWedge and calibrate (#9) and differing from getθ on the group means; the U.S. ν is the U.S. workbook's.
  S  data/oecd26_sample.csv is A4's rule on data/oecd29.csv: 26 kept; Mexico, Turkey and Korea dropped.
  C  At θ ≡ 1 the log tax is archive/notes/reviewResponse_2026-10/theory_closedForm.md eq (1.4) at every date and each country's ν, all 29, with
     the cost installed (it vanishes with its τ-derivative at θ = 1); the corner τ = 0 included (Mexico, Turkey).
  R  At the inputs of the published run of 2026-10-03 (the workbooks before review-2026-10) and its λ = 8.643207,
     the code path reproduces that run's ω of the U.S. (β imposed at that calibration's value) and of appendix
     G.1's UK and France; the designs in force in 2020 are pinned at today's LeadedLOG (PUB's comment).
  B  The log tax's gradient solve evaluates the condition only below the grid's u < 1 (policy.LOG._upper): from a warm
     start past τ = 1 it returns the cold start's equilibrium; Turkey's layer-2 row under CSES, seeded at the anchor
     of 2026-10-25, calibrates to the ω of the run of 2026-10-24; on cold solves, where no iterate reaches the bound,
     the tax is bitwise the one under u = 1 (one process, crossCuttingFindings #1).
  D  The layers at coarse grids in a temporary directory against an anchor row at a given λ: three countries
     through both layers (the U.S., Australia at the clip θ = 0, Italy at θ = 1), the U.S. rows against the
     anchor, reuse of rows under an unchanged key, recomputation under force or a moved anchor, refusal of a
     stale anchor row, and Luxembourg's 'noTurnout' row under cses.
  P  results/oecd26/, once complete, was computed at the U.S. calibration of now: each anchor row keyed on today's
     β and U.S. inputs at the fine grid, each layer row against that anchor and keyed on today's inputs, one tax
     equilibrium and no fallback per row. Skipped with a NOTE while the files are absent or partial (a run in
     progress writes them row by row). R's β are the 2026-10-03 run's by design; nothing else is.
  U  Every solve above records one tax equilibrium and no fallback: under log the tax is unique
     (archive/notes/reviewResponse_2026-10/theory_uniqueness.md), so a count above one is a defect.
"""
import os, sys, time, tempfile, shutil
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
import oecd26
import runOECD26 as R
from model import ModelUS
from gridsearch.testing import check, report

tic = time.time()
counts = []                       # (label, multiplicity summary) of every solve, for U
main, dist, smp = oecd26.readData()
pop = pd.read_csv(oecd26.FILES['pop'])
β, ωSeed, βSource = oecd26.usBeta()
US_CUTS = np.array([0.582266, 0.757993])

# ==== L: the loader ===========================================================================================
dev = {k: 0. for k in ('ν', 'γ', 'y', 'V', 'I', 'τ0', 'hη', 'Vm')}
θok, μok = True, True
for iso in oecd26.countries():
    inp = oecd26.countryInputs(iso)
    p = pop[(pop['iso3'] == iso) & (pop['definition'] == 'wpp2024')].set_index('period')['nu']
    want = np.array([p[1960], p[1990], p[2020], p[2050], p[2080], p[2110]] + [p[2110]]*oecd26.T_SS)
    dev['ν'] = max(dev['ν'], np.max(np.abs(inp['ν'] - want)))
    dev['γ'] = max(dev['γ'], np.max(np.abs(inp['γ'] - np.diff(np.r_[0., US_CUTS, 1.]))))
    dev['y'] = max(dev['y'], np.max(np.abs(inp['y'] - main.loc[iso, ['y1_usPct', 'y2_usPct', 'y3_usPct']].to_numpy(float))))
    dev['V'] = max(dev['V'], abs(inp['Vtilde'] - main.at[iso, 'Vtilde_usPct']))
    dev['I'] = max(dev['I'], abs(inp['index'] - main.at[iso, 'bbIndex']))
    dev['τ0'] = max(dev['τ0'], abs(inp['τ0'] - main.at[iso, 'pensionSpending']/100/0.7))
    θok &= inp['θ'] == float(np.clip(2 - main.at[iso, 'grr050_men']/main.at[iso, 'grr100_men'], 0, 1)) or \
        abs(inp['θ'] - float(np.clip(2 - main.at[iso, 'grr050_men']/main.at[iso, 'grr100_men'], 0, 1))) < 1e-15
    μok &= np.array_equal(inp['μ'], np.asarray(testmod.pars['μj'], dtype = float)[1:])
    m = oecd26.build(inp, β, ωSeed, 10.)
    t0 = m.t0Year
    dev['hη'] = max(dev['hη'], np.max(np.abs(np.asarray(m.B.hηRatio(t0), dtype = float) - inp['y'])))
    dev['Vm'] = max(dev['Vm'], abs(float(m.B.Vtilde(t0)) - inp['Vtilde']))
    θok &= bool(np.all(m.db['θ'].values == inp['θ']))
check('L: ν over DATES is oecd29_population.csv wpp2024 with its 1960/2110 copies, steady state at 2110 (29 countries)',
      dev['ν'] < 1e-12, 'max |Δ| {:.1e}'.format(dev['ν']))
check('L: γ_i are the U.S. percentile groups; y_i and Ṽ are oecd29.csv *_usPct', dev['γ'] < 1e-12 and dev['y'] < 1e-12
      and dev['V'] < 1e-7, 'max |Δ| γ {:.1e} y {:.1e} Ṽ {:.1e}'.format(dev['γ'], dev['y'], dev['V']))
check('L: I = grr100/grr050 is bbIndex to its rounding; θ = clip(2 - 1/I) on inputs and on every date of the model',
      dev['I'] < 5e-5 and θok, 'max |I - bbIndex| {:.1e}'.format(dev['I']))
check('L: τ0 = spending/100/(1 - α); μ is the U.S. workbook\'s CPS turnout (cps)', dev['τ0'] < 1e-15 and μok)
check('L: on the model hηRatio = y_i and Base.Vtilde = Ṽ (common X, Γ_h = 1)', dev['hη'] < 1e-7 and dev['Vm'] < 1e-7,
      'max |Δ| {:.1e}, {:.1e}'.format(dev['hη'], dev['Vm']))
ν = np.asarray(testmod.pars['ν'], dtype = float)
check("L: the U.S. ν is the U.S. workbook's (WPP 2024, to the workbook's rounding)",
      np.max(np.abs(oecd26.countryInputs('USA')['ν'] - ν)) < 5e-7,
      'max |Δ| {:.1e}'.format(np.max(np.abs(oecd26.countryInputs('USA')['ν'] - ν))))
cs = oecd26.countryInputs('GBR', 'cses')
check('L: cses turnout is oecd29.csv mu*_usPct', np.array_equal(cs['μ'], main.loc['GBR', ['mu1_usPct', 'mu2_usPct', 'mu3_usPct']].to_numpy(float)))
try:
    oecd26.countryInputs('LUX', 'cses')
    check('L: Luxembourg under cses raises NoTurnout', False)
except oecd26.NoTurnout:
    check('L: Luxembourg under cses raises NoTurnout', True)

inp = oecd26.countryInputs('GBR')
m = oecd26.build(inp, β, ωSeed, 10.)
θs = [float(m.db['θ'].iloc[2])]
m.updateAuxPars(); θs.append(float(m.db['θ'].iloc[2]))
m.setWedge(p = 3.); θs.append(float(m.db['θ'].iloc[2]))
cal = m.calibrate(); θs.append(float(m.db['θ'].iloc[2]))
counts.append(('L calibrate GBR', cal['report']['PEE']['multiplicity']))
θGroups = ModelUS.getθ(m)
check('L: θ survives updateAuxPars, setWedge and calibrate (#9), and is not getθ on the group means',
      max(θs) - min(θs) == 0 and abs(θGroups - θs[0]) > 1e-3 and abs(cal['report']['τ'] - inp['τ0']) < 1e-8,
      'θ {:.6f}, getθ on the groups {:.6f}'.format(θs[0], θGroups))

# ==== S: the sample ===========================================================================================
s = pd.read_csv(oecd26.FILES['sample'], index_col = 'iso3')
inf = pd.to_numeric(main['informal'], errors = 'coerce')
check('S: oecd26_sample.csv lists the 29 in oecd29.csv\'s order; 26 kept, MEX, TUR, KOR dropped',
      list(s.index) == oecd26.countries() and int(s['sample26'].sum()) == 26
      and set(s.index[~s['sample26']]) == {'MEX', 'TUR', 'KOR'})
check('S: sample26 is informal employment <= 25% or no series', bool((s['sample26'] == ~(inf > 25)).all()))
check('S: the loader carries sample26', all(oecd26.countryInputs(c)['sample26'] == bool(s.at[c, 'sample26'])
                                           for c in ('USA', 'MEX', 'KOR', 'GBR')))

# ==== C: the closed form at θ ≡ 1 =============================================================================
gaps, corners = {}, {}
for iso in oecd26.countries():
    m = oecd26.build(oecd26.countryInputs(iso), β, 1.3, 10.)
    gaps[iso], corners[iso] = oecd26.closedFormCheck(m)
worst = max(gaps, key = gaps.get)
check('C: at θ ≡ 1 the tax is eq (1.4) at every date and each country\'s ν, terminal β -> 0 (29 countries, λ = 10)',
      gaps[worst] < 1e-8, 'max |Δτ| {:.1e} ({}); dates at the lower corner: {}'.format(
          gaps[worst], worst, {k: v for k, v in corners.items() if v} or 'none'))

# ==== R: the published numbers at the published inputs ========================================================
def rel(income, γ):
    income, γ = np.asarray(income, float), np.asarray(γ, float)
    return income/np.sum(γ*income)


HEAD = {   # data/{US,UK,FR}Main*.xlsx as of the run of 2026-10-03: ν (1960..2110), γ, income, turnout, τ0, θ*
    'US': ([1.405486131972424, 1.405486131972424, 1.339667762739423, 1.1219986438186136, 1.0688804499803877],
           [0.5822660721626665, 0.17572652815988363, 0.24200739967744997], [37116., 73299., 160208.],
           [0.474, 0.629, 0.765], 0.1442857142857143, 0.7382263650417814),
    'UK': ([1.0919194313105167, 1.0919194313105167, 1.1740347147676515, 1.1210481688022833, 1.0059806887999434],
           [0.2916324856439705, 0.581214109926169, 0.12715340442986053], [14087., 28201., 60319.],
           [0.6064477, 0.6993464, 0.7352941], 0.11857142857142859, 0.5597455420580428),
    'FR': ([1.0262988524061831, 1.0262988524061831, 0.9668838626647813, 0.9037438499264058, 0.8705914625994323],
           [0.5820540935672515, 0.17598684210526316, 0.24195906432748537], [25112., 39361., 73767.],
           [0.8097, 0.8567, 0.8518], 0.21285714285714286, 1.0)}
# ω: the run of 2026-10-03; the designs in force in 2020 (θUS and the second entries): today's LeadedLOG at that
# run's λ, which reads the anticipated tax solved at every candidate (that run's 41-node table gave 0.7382263651
# -- the datum, on which its λ was calibrated --, 0.6246139324, 0.7489380486)
PUB = {'λ': 8.64320735564998, 'βUS': 0.7585347063319889, 'ωUS': 1.507771142663732, 'βSweep': 0.7606187875474915,
       'θUS': 0.7377083813119105,
       'UK': (1.2168885576097583, 0.6241113041731652), 'FR': (1.4180571029150613, 0.7475506558049251)}


def headInputs(k):
    nu, γ, inc, μ, τ0, θ = HEAD[k]
    return oecd26.inputsFrom(k, k, nu + [nu[-1]]*(1 + oecd26.T_SS), γ, rel(inc, γ), μ, 100*τ0*0.7, 1/(2 - θ))


m = oecd26.build(headInputs('US'), PUB['βUS'], 1.45, PUB['λ'])
cal = m.calibrate()
θIn = m.leadedDesignAtT0(m.ESC.solveBackward())
counts.append(('R U.S.', m.ESC.lastMultiplicity))
check("R: U.S. at the published inputs and λ, β imposed: ω is escCalibration.csv's and the design in force in 2020 "
      "today's", abs(cal['pars']['ω'] - PUB['ωUS']) < 1e-9 and abs(θIn - PUB['θUS']) < 1e-7,
      'ω {:.10f} (published {:.10f}), design {:.10f} ({:.10f}; θ* {:.10f})'.format(
          cal['pars']['ω'], PUB['ωUS'], θIn, PUB['θUS'], HEAD['US'][5]))
for k in ('UK', 'FR'):
    m = oecd26.build(headInputs(k), PUB['βSweep'], 1.3, PUB['λ'])
    cal = m.calibrate()
    sols = m.ESC.solveBackward()
    θIn = m.leadedDesignAtT0(sols)
    counts.append(('R ' + k, m.ESC.lastMultiplicity))
    check("R: {} at the published inputs under the U.S. λ: ω reproduces escCountry.csv, the design in force in 2020 "
          "is today's".format(k), abs(cal['pars']['ω'] - PUB[k][0]) < 1e-9 and abs(θIn - PUB[k][1]) < 1e-9,
          'ω {:.10f} (published {:.10f}), θ {:.10f} ({:.10f})'.format(cal['pars']['ω'], PUB[k][0], θIn, PUB[k][1]))

# ==== B: the gradient solve's upper bound =====================================================================
fine = R.settings()
inpUS = oecd26.countryInputs('USA')
ref = R._build(inpUS, β, ωSeed, 10., fine).solvePEE_LOG()['τ'].values.astype(float)
dev, err = 0., ''
for x0 in (np.r_[1.5, ref[1:]], np.full(len(ref), 3.)):
    m = R._build(inpUS, β, ωSeed, 10., fine)
    m.LOG.x0['vectorized'] = x0                       # the warm start a previous solve leaves behind
    try:
        out = m.solvePEE_LOG()
        counts.append(('B warm start past 1', out['multiplicity']))
        dev = max(dev, float(np.max(np.abs(out['τ'].values.astype(float) - ref))))
    except Exception as e:
        dev, err = np.inf, '{}: {}'.format(type(e).__name__, e)
check("B: from a warm start past τ = 1 (the first date; every date at 3) the log tax solve returns the cold start's "
      "equilibrium", dev < 1e-9, err or 'max |Δτ| {:.1e}'.format(dev))
# runOECD26's layer 2, CSES, Turkey (θ = 1, so λ does not enter): β of results/calibration at 2026-10-25, ω seeded at
# results/oecd26/anchor.csv's cses row of that day, where the ω root's first step sent the tax past 1; the ω of
# layer2.csv's row of 2026-10-24, seeded at that day's anchor
TUR = {'β': 0.655483014875856, 'ωSeed': 1.287314893152347, 'λ': 13.44349660231993, 'ω': 1.5265055644780803}
m = R._build(oecd26.countryInputs('TUR', 'cses'), TUR['β'], TUR['ωSeed'], TUR['λ'], fine)
try:
    cal = m.calibrate()
    counts.append(('B TUR cses', cal['report']['PEE']['multiplicity']))
    ok = abs(cal['pars']['ω'] - TUR['ω']) < 1e-9 and abs(cal['report']['τ'] - m.db['τ0']) < 1e-8
    msg = 'ω {:.10f}, minus 2026-10-24\'s {:.1e}; τ_2020 - τ0 {:.1e}'.format(
        cal['pars']['ω'], cal['pars']['ω'] - TUR['ω'], cal['report']['τ'] - m.db['τ0'])
except Exception as e:
    ok, msg = False, '{}: {}'.format(type(e).__name__, e)
check("B: Turkey's layer-2 row under CSES, ω seeded at the anchor of 2026-10-25, calibrates to the ω of 2026-10-24",
      ok, msg)
same = []
for iso in ('USA', 'AUS', 'ITA', 'TUR'):
    inp = oecd26.countryInputs(iso)
    a, b = R._build(inp, β, ωSeed, 10., fine), R._build(inp, β, ωSeed, 10., fine)
    θc, εc = a.db['θ'].values, a.db['eps'].values
    same.append(np.array_equal(a.LOG.solveRobust(θc, εc, u = 1.)['τ'].values, b.LOG.solveRobust(θc, εc)['τ'].values))
check('B: on cold solves the tax is bitwise the one under u = 1 (USA, AUS, ITA, TUR, one process)', all(same),
      '{} of {} bitwise'.format(sum(same), len(same)))

# ==== D: the driver ===========================================================================================
tmp = tempfile.mkdtemp(prefix = 'oecd26_')
cfg = R.settings(coarse = True)
inpUS = oecd26.countryInputs('USA')
m = R._build(inpUS, β, ωSeed, 10., cfg)
cal = m.calibrate()
a = {'turnout': 'cps', 'spec': R.SPEC, 'phi': R.PHI, 'commonX': R.COMMONX, 'iso3': 'USA', 'status': 'ok', 'β': β,
     'ω': float(cal['pars']['ω']), 'p': 10., 'τData': inpUS['τ0'], 'θData': inpUS['θ'],
     'inputsKey': R.anchorKey(inpUS, β, cfg), 'grid': cfg['grid']}
R.mergeWrite(os.path.join(tmp, 'anchor.csv'), [a], R.KEYANCHOR)
counts.append(('D anchor at λ = 10', cal['report']['PEE']['multiplicity']))
ref = (β, ωSeed, βSource)
check('D: an anchor row at λ = 10 with the current key is accepted', R.anchorRow('cps', tmp, cfg, ref)['ω'] == a['ω'])
isos = ['USA', 'AUS', 'ITA']
l1 = {r['iso3']: r for r in R.stageLayer('layer1', 'cps', isos, tmp, a, cfg)}
l2 = {r['iso3']: r for r in R.stageLayer('layer2', 'cps', isos, tmp, a, cfg)}
cols = ['τ2020', 'spending2020', 'θChosen', 'indexChosen', 'θInForce', 'τInForce', 'closedFormGap', 'nEqMax',
        'nCandMax', 'nFallback', 'sample26', 'inputsKey', 'θClipped']
d1, d2 = pd.read_csv(os.path.join(tmp, 'layer1.csv')), pd.read_csv(os.path.join(tmp, 'layer2.csv'))
check("D: layer rows on disk, one per country, every readout column, status ok, the anchor's key",
      len(d1) == 3 and len(d2) == 3 and all(c in d1.columns and c in d2.columns for c in cols)
      and set(d1['status']) == {'ok'} and set(d2['status']) == {'ok'}
      and set(d1['anchorKey']) == {a['inputsKey']} == set(d2['anchorKey']))
check("D: the U.S. layer rows reproduce the anchor's τ_2020 (layer 1) and ω (layer 2)",
      abs(l1['USA']['τ2020'] - a['τData']) < 1e-8 and abs(l2['USA']['ω'] - a['ω']) < 1e-7
      and abs(l2['USA']['θChosen'] - l1['USA']['θChosen']) < 1e-10)
check('D: layer 2 matches each country\'s spending; θ clipped at 0 (AUS) and 1 (ITA); I = 1/(2 - θ)',
      all(abs(l2[c]['τ2020'] - l2[c]['τData']) < 1e-8 for c in isos) and l1['AUS']['θClipped']
      and l1['AUS']['θData'] == 0. and l1['ITA']['θData'] == 1. and not l1['ITA']['θClipped']
      and all(abs(r['indexChosen'] - 1/(2 - r['θChosen'])) < 1e-15 for r in list(l1.values()) + list(l2.values())))
check('D: the closed form holds on every row (θ ≡ 1 at the row\'s ω)',
      max(r['closedFormGap'] for r in list(l1.values()) + list(l2.values())) < 1e-8)
for r in list(l1.values()) + list(l2.values()):
    counts.append(('D {} {}'.format(r.get('layer', 'anchor'), r['iso3']), {k: r[k] for k in ('nEqMax', 'nCandMax', 'nFallback')}))
before = d1.copy()
again = R.stageLayer('layer1', 'cps', isos, tmp, R.anchorRow('cps', tmp, cfg, ref), cfg)
check('D: a rerun under the same key reuses every row (nothing recomputed, file unchanged)',
      again == [] and pd.read_csv(os.path.join(tmp, 'layer1.csv')).equals(before))
forced = R.stageLayer('layer1', 'cps', ['AUS'], tmp, a, cfg, force = True)
moved = R.stageLayer('layer1', 'cps', ['AUS'], tmp, a | {'ω': a['ω'] + 0.01}, cfg)
check('D: force recomputes; a moved anchor ω changes the key and recomputes',
      len(forced) == 1 and len(moved) == 1 and moved[0]['ωAnchor'] == a['ω'] + 0.01
      and moved[0]['inputsKey'] != forced[0]['inputsKey'])
an = pd.read_csv(os.path.join(tmp, 'anchor.csv'))
an.loc[0, 'inputsKey'] = 'stale'
an.to_csv(os.path.join(tmp, 'anchor.csv'), index = False)
try:
    R.anchorRow('cps', tmp, cfg, ref)
    check('D: an anchor row computed at other inputs is refused', False)
except SystemExit:
    check('D: an anchor row computed at other inputs is refused', True)
lux = R.stageLayer('layer1', 'cses', ['LUX'], tmp, a, cfg)
check("D: Luxembourg under cses gets a 'noTurnout' row", len(lux) == 1 and lux[0]['status'] == 'noTurnout'
      and lux[0]['nEqMax'] == -1)

# ==== P: the results on disk are current ======================================================================
def production():
    """ results/oecd26's three csvs, or None while they are absent or partial: runOECD26.py writes them row by row
    (both turnout readings' anchors, 29 rows per reading in each layer when complete), and a reader running beside
    it sees a partial file. """
    try:
        f = {n: pd.read_csv(os.path.join(R.OUTDIR, n + '.csv'), dtype = {'inputsKey': str, 'anchorKey': str},
                            float_precision = 'round_trip') for n in ('anchor', 'layer1', 'layer2')}
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError):
        return None
    n = len(oecd26.countries())*len(oecd26.TURNOUT)
    full = (sorted(f['anchor']['turnout']) == sorted(oecd26.TURNOUT) and len(f['layer1']) == n == len(f['layer2']))
    return f if full else None


prod = production()
if prod is None:
    print('NOTE  P skipped: results/oecd26/ is absent or partial (runOECD26.py writes it row by row); run this suite '
          'again once the run has finished')
else:
    an, fine, data = prod['anchor'], R.settings(), oecd26.readData()
    rd = lambda layer: prod[layer]
    keyA = {t: R.anchorKey(oecd26.countryInputs('USA', t, data), β, fine) for t in oecd26.TURNOUT}
    check('P: results/oecd26/anchor.csv holds one ok anchor per turnout, keyed on the U.S. β and inputs of now, '
          'fine grid', sorted(an['turnout']) == sorted(oecd26.TURNOUT) and set(an['status']) == {'ok'}
          and all(an.loc[an['turnout'] == t, 'inputsKey'].iloc[0] == k for t, k in keyA.items()),
          'β {} on disk, {} now'.format(sorted(set(an['β'])), β))
    for layer in ('layer1', 'layer2'):
        d = rd(layer)
        ok = d[d['status'] == 'ok']
        par = {t: (float(r['β']), float(r['ω']), float(r['p'])) for t, r in an.set_index('turnout').iterrows()}
        cur = [oecd26.inputsKey(layer, oecd26.modelInputs(oecd26.countryInputs(r['iso3'], r['turnout'], data)),
                                *par[r['turnout']], fine) for _, r in ok.iterrows()]
        check('P: {}: 29 rows per turnout, each computed against the anchor on disk and keyed on the inputs of now; '
              'one tax equilibrium and no fallback in every ok row'.format(layer),
              set(d['status']) <= {'ok', 'noTurnout'}
              and set(d.loc[d['status'] == 'noTurnout', 'iso3']) <= {'LUX'}
              and bool((d['anchorKey'] == d['turnout'].map(dict(zip(an['turnout'], an['inputsKey'])))).all())
              and list(ok['inputsKey']) == cur and bool((ok['nEqMax'] == 1).all() and (ok['nFallback'] == 0).all()),
              '{} ok, {} noTurnout'.format(len(ok), int((d['status'] == 'noTurnout').sum())))

# ==== U: uniqueness ===========================================================================================
bad = [(k, c) for k, c in counts if not (c and c['nEqMax'] == 1 and c['nFallback'] == 0)]
check('U: every solve records one tax equilibrium and no fallback ({} solves)'.format(len(counts)), not bad,
      str(bad[:3]) if bad else '')

shutil.rmtree(tmp, ignore_errors = True)
print('\n({:.0f}s)'.format(time.time() - tic))
report()
