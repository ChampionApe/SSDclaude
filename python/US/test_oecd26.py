r""" The cross-country test's loader and driver (oecd26.py, runOECD26.py); the two calibrations of the cost parameter
are test_oecd26Anchor.py's (slow).

Run:  .venv\Scripts\python.exe python\US\test_oecd26.py        (~4.5 min)

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
  N  Spec 'none', coarse: the anchor calibrates ω to τ0 and reads no design (p, θChosen, θInForce, fStar, f0 NaN,
     status 'ok'); at θ_c = 1 (France, Austria) layer 1's τ_2020 is eq (1.4) at ν_2020.
  Q  betaRule 'commonR', coarse, at D's anchor: layer 1's R_2020 is the anchor's (the U.S. recovers the anchor's β),
     layer 2's two residuals vanish; the β-common settings carry no betaRule (their keys are unchanged).
  Π  Spec 'sizePiR', coarse: each row's π fixed points converged (ΠRgap < ΠR_TOL), λEff2020 = p·ΠR2020, and the
     readouts are each solve's own: τ_2020 and ΠR2020 a fresh solvePEE_LOG's, θInForce and τInForce a fresh
     solveLeaded(pinAtT0 = False)'s; layer 2 matches spending.
  K  runESC.usWedgeRow (the country stage's U.S.-cost row), the UK at coarse design grids: under 'sizePiR' the
     choice is a fresh free path's at its own π, the tax and ΠR the pinned path's; under 'size' the choice is the
     earlier sequence's (policies solved first, then leadedDesignAtT0 on them) bitwise.
  M  results/oecd26/'s csvs copied to a temporary directory: a run under 'size', 'common' at the fine grid reuses
     every row, whether or not the csv has the betaRule column; a forced recompute of GBR's layer-1 cps row writes
     the column ('common' on every row) and reproduces τ_2020 and θInForce to 1e-10, the other rows unchanged.
     Skipped with a NOTE while results/oecd26/ is absent, partial or not current (P says which).
  P  results/oecd26/, once complete, was computed at the U.S. calibration of now: per spec, each anchor row keyed on
     today's β and U.S. inputs at the fine grid; per spec and β rule, each layer row against that anchor and keyed
     on today's inputs, one tax equilibrium and no fallback per row. A variant whose rows are absent or partial (a
     run in progress writes them row by row) is skipped with a NOTE. R's β are the 2026-10-03 run's by design;
     nothing else is.
  U  Every solve above records one tax equilibrium and no fallback: under log the tax is unique
     (archive/notes/reviewResponse_2026-10/theory_uniqueness.md), so a count above one is a defect.
"""
import os, sys, time, tempfile, shutil, filecmp
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
import oecd26
import runOECD26 as R
import runESC
from model import ModelUS
from modelESC import ΠR_TOL
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
a = {'turnout': 'cps', 'spec': cfg['spec'], 'phi': R.PHI, 'commonX': R.COMMONX, 'betaRule': 'common', 'iso3': 'USA',
     'status': 'ok', 'β': β, 'ω': float(cal['pars']['ω']), 'p': 10., 'τData': inpUS['τ0'], 'θData': inpUS['θ'],
     'inputsKey': R.anchorKey(inpUS, β, cfg), 'grid': cfg['grid']}
RA = float(cal['report']['R'])                     # the anchor's R_2020 (the θ-pinned path's), Q's target
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

MULT = ('nEqMax', 'nCandMax', 'nFallback')

# ==== N: no cost ==============================================================================================
tmpN = tempfile.mkdtemp(prefix = 'oecd26N_')
cfgN = R.settings(coarse = True, spec = 'none')
aN = R.stageAnchor('cps', tmpN, cfgN, (β, ωSeed, βSource))
counts.append(('N anchor', {k: aN[k] for k in MULT}))
check("N: the 'none' anchor calibrates ω to τ0 and reads no design (p, θChosen, θInForce, fStar, f0 NaN), status ok",
      aN['status'] == 'ok' and abs(aN['τResidual']) < 1e-8 and cfgN['bracket'] is None
      and all(np.isnan(float(aN[k])) for k in ('p', 'θChosen', 'θInForce', 'τInForce', 'fStar', 'f0', 'τPinGap',
                                                'ΠR2020', 'λEff2020')),
      'ω {:.6f}, τ_2020 - τ0 {:.1e}'.format(aN['ω'], aN['τResidual']))
rowsN = {r['iso3']: r for r in R.stageLayer('layer1', 'cps', ['FRA', 'AUT'], tmpN, aN, cfgN)}
gapN = {}
for iso, r in rowsN.items():
    inp = oecd26.countryInputs(iso)
    gapN[iso] = abs(r['τ2020'] - oecd26.closedFormTax(inp['α'], β, inp['ξ'], aN['ω'],
                                                      inp['ν'][oecd26.DATES.get_loc(oecd26.T0YEAR)]))
    counts.append(('N layer1 ' + iso, {k: r[k] for k in MULT}))
check("N: at θ_c = 1 (FRA, AUT) layer 1's τ_2020 without the cost is eq (1.4) at ν_2020, and no design is read",
      all(rowsN[c]['θData'] == 1. and np.isnan(rowsN[c]['θInForce']) for c in ('FRA', 'AUT'))
      and max(gapN.values()) < 1e-8, ', '.join('{} |Δτ| {:.1e}'.format(c, g) for c, g in gapN.items()))

# ==== Q: β set to the anchor's 2020 return ====================================================================
tmpQ = tempfile.mkdtemp(prefix = 'oecd26Q_')
cfgQ = R.settings(coarse = True, betaRule = 'commonR')
aQ = a | {'R2020': RA}
q1 = {r['iso3']: r for r in R.stageLayer('layer1', 'cps', ['USA', 'GBR'], tmpQ, aQ, cfgQ)}
q2 = R.stageLayer('layer2', 'cps', ['GBR'], tmpQ, aQ, cfgQ)[0]
for r in list(q1.values()) + [q2]:
    counts.append(('Q {} {}'.format(r['layer'], r['iso3']), {k: r[k] for k in MULT}))
check("Q: under 'commonR' layer 1's R_2020 is the anchor's at the anchor's ω (USA, GBR); the U.S. recovers the "
      "anchor's β", all(r['status'] == 'ok' and abs(r['R2020'] - RA) < 1e-8 and r['ω'] == a['ω'] and r['βAnchor'] == β
                        and r['RTarget'] == RA for r in q1.values()) and abs(q1['USA']['β'] - β) < 1e-8,
      'R_2020 - R_US: {}; β: USA {:.10f} (anchor {:.10f}), GBR {:.6f}'.format(
          ', '.join('{} {:.1e}'.format(c, r['R2020'] - RA) for c, r in q1.items()), q1['USA']['β'], β, q1['GBR']['β']))
check("Q: under 'commonR' layer 2's two residuals vanish (GBR: R_2020/R_US - 1, τ_2020 - τ0)",
      q2['status'] == 'ok' and abs(q2['R2020']/RA - 1) < 1e-8 and abs(q2['τ2020'] - q2['τData']) < 1e-8
      and q2['calResidual'] < 1e-8,
      'R {:.1e}, τ {:.1e}; β {:.6f}, ω {:.6f}'.format(q2['R2020']/RA - 1, q2['τ2020'] - q2['τData'], q2['β'], q2['ω']))
check("Q: the β-common settings carry no betaRule (their rows keep their keys); a 'commonR' row has a key of its own",
      'betaRule' not in R.settings() and 'betaRule' not in cfg and q1['USA']['inputsKey'] != l1['USA']['inputsKey'])

# ==== Π: the Π-inclusive cost =================================================================================
tmpP = tempfile.mkdtemp(prefix = 'oecd26P_')
cfgP = R.settings(coarse = True, spec = 'sizePiR')
aP = a | {'spec': 'sizePiR', 'p': 20.}
p1 = R.stageLayer('layer1', 'cps', ['GBR'], tmpP, aP, cfgP)[0]
p2 = R.stageLayer('layer2', 'cps', ['GBR'], tmpP, aP, cfgP)[0]
for r in (p1, p2):
    counts.append(('Π {} GBR'.format(r['layer']), {k: r[k] for k in MULT}))
inpG = oecd26.countryInputs('GBR')
m2 = R._build(inpG, β, a['ω'], 20., cfgP)
pin2 = m2.solvePEE_LOG()
t0 = m2.t0Year
m3 = R._build(inpG, β, a['ω'], 20., cfgP)
led3 = m3.solveLeaded(pinAtT0 = False)
dev = {'τ2020': abs(p1['τ2020'] - float(pin2['τ'].xs(t0))), 'ΠR2020': abs(p1['ΠR2020'] - float(m2.db['wedgeΠR'].xs(t0))),
       'θInForce': abs(p1['θInForce'] - float(led3['θ'].xs(t0))), 'τInForce': abs(p1['τInForce'] - float(led3['τ'].xs(t0)))}
check("Π: under 'sizePiR' each row's π fixed points converged (ΠRgap < ΠR_TOL) and λEff2020 = p·ΠR2020 (GBR, both layers)",
      all(r['status'] == 'ok' and r['ΠRgap'] < ΠR_TOL and abs(r['λEff2020'] - 20.*r['ΠR2020']) < 1e-12 for r in (p1, p2)),
      'ΠRgap {:.1e}, {:.1e}; ΠR2020 {:.6f}, λEff2020 {:.4f}'.format(p1['ΠRgap'], p2['ΠRgap'], p1['ΠR2020'], p1['λEff2020']))
check("Π: layer 1's τ_2020 and ΠR2020 are a fresh solvePEE_LOG's, θInForce and τInForce a fresh "
      "solveLeaded(pinAtT0 = False)'s, each at its own π", max(dev.values()) < 1e-9,
      ', '.join('{} {:.1e}'.format(k, v) for k, v in dev.items()) + '; τPinGap {:.1e}'.format(p1['τPinGap']))
check("Π: layer 2 under 'sizePiR' matches spending (GBR)", abs(p2['τ2020'] - p2['τData']) < 1e-8,
      'τ_2020 - τ0 {:.1e}, ω {:.6f}'.format(p2['τ2020'] - p2['τData'], p2['ω']))

# ==== K: the country stage's U.S.-cost row ====================================================================
def ukModel(spec, p):
    m = runESC.buildEU('UK', {'spec': spec, 'phi': 0.5, 'p': p}, commonX = True, nθ = 21, nθCand = 41)
    m.calibrate()
    return m


rowK = runESC.usWedgeRow(ukModel('sizePiR', 20.), 'sizePiR', 0.5, True, 'UK', 20.)
mK = ukModel('sizePiR', 20.)
ledK = mK.solveLeaded(pinAtT0 = False)
pinK = mK.solvePEE_LOG()
tK = mK.t0Year
devK = {'choice': abs(rowK['choice'] - float(ledK['θ'].xs(tK))), 'τ': abs(rowK['τ'] - float(pinK['τ'].xs(tK))),
        'ΠR': abs(rowK['ΠR'] - float(mK.db['wedgeΠR'].xs(tK)))}
counts.append(('K UK sizePiR', {k: rowK[k] for k in MULT}))
check("K: the country stage's U.S.-cost row under 'sizePiR' (UK): the choice is a fresh free path's at its own π, "
      "τ and ΠR the θ*-pinned path's", max(devK.values()) < 1e-9,
      ', '.join('{} {:.1e}'.format(k, v) for k, v in devK.items()) + '; choice {:.6f}, ΠR {:.6f}'.format(
          rowK['choice'], rowK['ΠR']))
rowS = runESC.usWedgeRow(ukModel('size', 10.), 'size', 0.5, True, 'UK', 10.)
mS = ukModel('size', 10.)
solsS = mS.ESC.solveBackward()
multS = runESC.multiplicityColumns(mS.ESC.lastMultiplicity)
chS = mS.leadedDesignAtT0(solsS)
check("K: under 'size' the row's choice and counts are the earlier sequence's bitwise (policies solved, then "
      "leadedDesignAtT0 on them)", rowS['choice'] == chS and all(rowS[k] == v for k, v in multS.items()),
      'choice {!r} and {!r}'.format(rowS['choice'], chS))

# ==== P: the results on disk are current ======================================================================
def production():
    """ results/oecd26's three csvs, betaRule 'common' where the column is absent or blank (runOECD26.LEGACY), or
    None while a file is absent. """
    try:
        f = {n: pd.read_csv(os.path.join(R.OUTDIR, n + '.csv'), dtype = {'inputsKey': str, 'anchorKey': str},
                            float_precision = 'round_trip') for n in ('anchor', 'layer1', 'layer2')}
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError):
        return None
    for d in f.values():
        d['betaRule'] = d['betaRule'].fillna('common') if 'betaRule' in d.columns else 'common'
    return f


prod = production()
current = {}                      # ('anchor', spec) or (layer, spec, betaRule) -> complete and keyed on now
nC = len(oecd26.countries())
if prod is None:
    print('NOTE  P skipped: results/oecd26/ is absent (runOECD26.py writes it row by row)')
else:
    data, an = oecd26.readData(), prod['anchor']
    for spec in sorted(set(an['spec'])):
        aS = an[an['spec'] == spec]
        if sorted(aS['turnout']) != sorted(oecd26.TURNOUT):
            print('NOTE  P skipped for {}: anchor rows for {} only'.format(spec, sorted(aS['turnout'])))
            continue
        keyA = {t: R.anchorKey(oecd26.countryInputs('USA', t, data), β, R.settings(spec = spec)) for t in oecd26.TURNOUT}
        current[('anchor', spec)] = (set(aS['status']) == {'ok'} and set(aS['betaRule']) == {'common'}
                                     and all(aS.loc[aS['turnout'] == t, 'inputsKey'].iloc[0] == k for t, k in keyA.items()))
        check('P: results/oecd26/anchor.csv, {}: one ok anchor per turnout, keyed on the U.S. β and inputs of now, '
              'fine grid'.format(spec), current[('anchor', spec)], 'β {} on disk, {} now'.format(sorted(set(aS['β'])), β))
        par = {t: (float(r['β']), float(r['ω']), float(r['p'])) for t, r in aS.set_index('turnout').iterrows()}
        RAn = {t: float(r['R2020']) for t, r in aS.set_index('turnout').iterrows()}
        for layer in ('layer1', 'layer2'):
            dl = prod[layer]
            for rule in sorted(set(dl.loc[dl['spec'] == spec, 'betaRule'])):
                d = dl[(dl['spec'] == spec) & (dl['betaRule'] == rule)]
                if any((d['turnout'] == t).sum() != nC for t in oecd26.TURNOUT):
                    print('NOTE  P skipped for {} {} {}: {} rows, {} per turnout when complete'.format(
                        layer, spec, rule, len(d), nC))
                    continue
                ok = d[d['status'] == 'ok']
                fineL = R.settings(spec = spec, betaRule = rule)
                cur = [oecd26.inputsKey(layer, oecd26.modelInputs(oecd26.countryInputs(r['iso3'], r['turnout'], data)),
                                        *par[r['turnout']], fineL, *([RAn[r['turnout']]] if rule == 'commonR' else []))
                       for _, r in ok.iterrows()]
                current[(layer, spec, rule)] = (
                    set(d['status']) <= {'ok', 'noTurnout'} and set(d.loc[d['status'] == 'noTurnout', 'iso3']) <= {'LUX'}
                    and bool((d['anchorKey'] == d['turnout'].map(dict(zip(aS['turnout'], aS['inputsKey'])))).all())
                    and list(ok['inputsKey']) == cur and bool((ok['nEqMax'] == 1).all() and (ok['nFallback'] == 0).all()))
                check('P: {}, {}, {}: 29 rows per turnout, each computed against the anchor on disk and keyed on the '
                      'inputs of now; one tax equilibrium and no fallback in every ok row'.format(layer, spec, rule),
                      current[(layer, spec, rule)],
                      '{} ok, {} noTurnout'.format(len(ok), int((d['status'] == 'noTurnout').sum())))

# ==== M: the rows on disk are reused under betaRule 'common' ==================================================
if not all(current.get(k) for k in (('anchor', 'size'), ('layer1', 'size', 'common'), ('layer2', 'size', 'common'))):
    print("NOTE  M skipped: results/oecd26/ has no complete and current 'size'/'common' rows (P)")
else:
    tmpM = tempfile.mkdtemp(prefix = 'oecd26M_')
    for n in ('anchor', 'layer1', 'layer2'):
        shutil.copy(os.path.join(R.OUTDIR, n + '.csv'), os.path.join(tmpM, n + '.csv'))
    hadColumn = 'betaRule' in pd.read_csv(os.path.join(R.OUTDIR, 'layer1.csv'), nrows = 1).columns
    fineS, refNow = R.settings(), (β, ωSeed, βSource)
    def change(old, new, skip = None):
        """ The largest relative change of a value of `old`'s rows in `new` (rows matched on KEYLAYER, those `skip`
        selects left out), the 'time' column ignored; inf where a row, a column, a NaN or a non-float cell differs. """
        if skip is not None:
            old, new = old[~skip(old)], new[~skip(new)]
        o, n_ = old.set_index(R.KEYLAYER).sort_index(), new.set_index(R.KEYLAYER).sort_index()
        if not (o.index.equals(n_.index) and set(o.columns) <= set(n_.columns)):
            return np.inf
        rel = 0.
        for c in o.columns.drop('time', errors = 'ignore'):
            x, y = o[c], n_[c]
            if pd.api.types.is_float_dtype(x) and pd.api.types.is_float_dtype(y):
                x, y = x.values, y.values
                fin = np.isfinite(x)
                rel = max(rel, np.inf if not np.array_equal(fin, np.isfinite(y)) else
                          float(np.max(np.abs(y[fin] - x[fin])/np.maximum(np.abs(x[fin]), 1e-300), initial = 0.)))
            elif not (x.fillna('').astype(str) == y.fillna('').astype(str)).all():
                rel = np.inf
        return rel

    readM = lambda n: pd.read_csv(os.path.join(tmpM, n + '.csv'), dtype = {'inputsKey': str, 'anchorKey': str},
                                  float_precision = 'round_trip')
    old = production()
    anchorsM = {t: R.stageAnchor(t, tmpM, fineS, refNow) for t in oecd26.TURNOUT}
    solved = [r for layer in ('layer1', 'layer2') for t in oecd26.TURNOUT
              for r in R.stageLayer(layer, t, oecd26.countries(), tmpM, anchorsM[t], fineS) if r['status'] != 'noTurnout']
    new = {n: readM(n) for n in ('layer1', 'layer2')}
    relM = max(change(old[n], new[n]) for n in new)
    check("M: a 'size'/'common' run at the fine grid on results/oecd26/'s rows ({} betaRule column) solves no row and "
          "leaves anchor.csv as it was; the layer files, rewritten for Luxembourg's 'noTurnout' rows, carry betaRule "
          "('common' where they had none) on unchanged rows".format('with a' if hadColumn else 'no'),
          not solved and filecmp.cmp(os.path.join(tmpM, 'anchor.csv'), os.path.join(R.OUTDIR, 'anchor.csv'),
                                     shallow = False)
          and all(d['betaRule'].notna().all() and (hadColumn or set(d['betaRule']) == {'common'}) for d in new.values())
          and relM < 1e-13, '{} rows solved; layer rows: max relative change {:.1e}'.format(len(solved), relM))
    sel = lambda d: (d['iso3'] == 'GBR') & (d['turnout'] == 'cps') & (d['spec'] == 'size') & (d['betaRule'] == 'common')
    disk = old['layer1'][sel(old['layer1'])].iloc[0]
    forced = R.stageLayer('layer1', 'cps', ['GBR'], tmpM, anchorsM['cps'], fineS, force = True)[0]
    devG = {k: abs(forced[k] - float(disk[k])) for k in ('τ2020', 'θInForce')}
    rel = change(old['layer1'], readM('layer1'), sel)
    check("M: a forced recompute of GBR (layer 1, 'size', 'common', cps) reproduces the row on disk's τ_2020 and "
          "θInForce to 1e-10, the other rows unchanged", max(devG.values()) < 1e-10 and rel < 1e-13,
          'τ_2020 {:.1e}, θInForce {:.1e}; other rows: max relative change {:.1e}'.format(
              devG['τ2020'], devG['θInForce'], rel))
    check('M: after the rewrite every row is reused again',
          R.stageLayer('layer1', 'cps', oecd26.countries(), tmpM, anchorsM['cps'], fineS) == [])
    shutil.rmtree(tmpM, ignore_errors = True)
for d in (tmpN, tmpQ, tmpP):
    shutil.rmtree(d, ignore_errors = True)

# ==== U: uniqueness ===========================================================================================
bad = [(k, c) for k, c in counts if not (c and c['nEqMax'] == 1 and c['nFallback'] == 0)]
check('U: every solve records one tax equilibrium and no fallback ({} solves)'.format(len(counts)), not bad,
      str(bad[:3]) if bad else '')

shutil.rmtree(tmp, ignore_errors = True)
print('\n({:.0f}s)'.format(time.time() - tic))
report()
