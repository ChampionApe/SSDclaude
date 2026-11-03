r""" θ from a variant of data/oecd26_theta.csv: the cross-country loader and driver (oecd26.py, runOECD26.py), the
U.S. design imposed as db['θ0'] (model.py ModelUS.θOverride/getθ, modelESC.py) and the U.S. drivers' --theta
(calibrateRhoGrid.py, runESC.py), on a temporary fixture of the file (data/ is not read for it).

Run:  .venv\Scripts\python.exe python\US\test_oecd26Theta.py        (~1 min)

  I  thetaSource 'index' is the default: countryInputs with and without it agree on every value for the 29 and both
     turnouts, the dict records 'index', and the settings and the anchor key carry no thetaSource (test_oecd26.py P
     pins the keys of results/oecd26/ against today's).
  F  Under a variant θ reaches ModelOECD.getθ and db['θ'] on every date within 1e-12 (the fixture's U.S., θ = 0 and
     θ = 1); θRaw is the file's θ, never 'clipped'; I = 1/(2 - θ).
  E  A NaN θ, a θ outside [0, 1] or a missing row raises NoTheta; an unknown variant, a duplicate row or a variant
     named 'index' raises ValueError.
  K  The inputsKey (anchor and layer) differs between sources, also where the two give the same θ (the label alone).
  O  runOECD26: the default outdir follows the variant; main refuses results/oecd26/ under a variant, an unknown
     variant and --inSample without one; --inSample keeps the variant's inSample countries and the U.S.
  W  stageLayer under a variant: 'noTheta' rows for a NaN, a missing and an out-of-range θ, keyed on the variant;
     stageAnchor exits where the variant has no U.S. θ; a csv without thetaSource reads and migrates as 'index'.
  B  usBeta under a variant: the variant's sweep is required, its row must carry the variant and θ0 = the variant's
     U.S. θ; the source names both and enters the anchor key (not under 'index').
  U  ModelUS.getθ without db['θ0'] (or with NaN) is the RR0 closed form bit for bit; with it θ = θ0 on every date,
     through updateAuxPars and the common-X calibration at ρ = 1, which still hits R, τ and hours; θ0 outside [0, 1]
     raises. ModelESC returns θ0 under 'size' (runESC.buildUS) and refuses it under 'flat'; ModelOECD refuses it.
  C  The U.S. drivers' --theta. calibrateRhoGrid.thetaRun: θ0, the variant's calibration/; results/calibration/,
     --medicare refused. runESC without a variant: results/calibration's sweep, the workbook's θ, the fine grids;
     setTheta: every U.S. model at θ0 seeded off the variant's sweep, France and the UK at their FRA and GBR rows
     against that sweep, root/esc, the coarse grid; other stages, results/esc/, a missing sweep, a calibration at
     another θ0 refused. runShocksUS.thetaRun: the variant's sweep at every rho asked for, root/shocks/, France's θ0;
     --medicare, --freeTheta and results/shocks/ refused; the host model carries θ0.
  S  τ0 under a variant is the file's `spending` over the labour share (a fixture variant at another spending); for
     the variants of oecd26.SPENDINGASFIGURE a spending other than figure 1.1's raises; on data/oecd26_theta.csv
     paper, A, A2pt and C equal figure 1.1's pensionSpending (data/oecd29.csv, data/oecdFigure1.csv) to 1e-9.
  M  --main: oecd26.thetaRoot is results/ for config.US['theta'] and refuses any other variant; calibrateRhoGrid,
     calibrateRhoGridEU, runESC, runShocksUS and runOECD26 write the standard paths under it and keep refusing them
     without it; the CRRA, ξ and stationary drivers take --theta with --main only.
  R  France and the UK at θ0: testEU.model's θ0 is db['θ'] on every date and survives France's ω calibration at the
     U.S. cuts (LOG, ρ = 1), which still hits τ0; without it θ is the workbook's (1 for France) bit for bit.
     calibrateRhoGridEU.thetaRun: the country's θ0, the variant's U.S. sweep (refused at another θ0), the csv under
     root/calibration/. runESC.checkCalib reads only the rows a stage reads; runESCcrra.readCalibratedP keeps only
     the variant's rows; runESCcrra.buildUS and stationaryApprox.build carry θ0.
  N  c5Numbers and runHorizon take --theta with --main only, for config.US['theta']; their row filter (_at) keeps the
     variant's rows at θ0 (the rows without thetaSource without one); under C c5Numbers.usModel and runHorizon.build
     carry θ0 and runESC.THETA is installed; runHorizon.mergeWrite and c5Numbers._mergeExperiments drop the rows at
     another θ (a csv holds one θ), replace a key and tag their rows.
"""
import os, sys, time, tempfile, shutil
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
import oecd26
import runOECD26 as R
import runESC
import calibrateRhoGrid as CRG
import runShocksUS as RS
from model import ModelUS
from modelESC import ModelESC
from gridsearch.testing import check, report

tic = time.time()
tmp = tempfile.mkdtemp(prefix = 'oecd26Theta_')
FIX = os.path.join(tmp, 'oecd26_theta.csv')
data = oecd26.readData()
β, ωSeed, βSource = oecd26.usBeta()
θUSindex = oecd26.countryInputs('USA')['θ']
rows = ([('USA', 'fixA', 0.54, False), ('GBR', 'fixA', 0.18, True), ('CAN', 'fixA', 0.32, True),
         ('AUS', 'fixA', np.nan, False), ('FRA', 'fixA', 1.0, True), ('IRL', 'fixA', 0.0, True),
         ('ITA', 'fixA', 1.2, True)]                                   # NZL: no row under fixA
        + [('USA', 'fixB', θUSindex, True), ('GBR', 'fixB', 0.30, True), ('FRA', 'fixB', 0.7, True)]
        + [('USA', 'fixC', np.nan, True), ('GBR', 'fixC', 0.30, True)]
        + [('USA', 'C', 0.544496, True), ('FRA', 'C', 0.82188, True), ('GBR', 'C', 0.181208, True)])
SPEND = data[0]['pensionSpending']
fixture = pd.DataFrame(rows, columns = ['iso3', 'variant', 'theta', 'inSample'])
fixture['spending'] = [9.0 if (i, v) == ('GBR', 'fixB') else float(SPEND[i]) for i, v in zip(fixture['iso3'],
                                                                                           fixture['variant'])]
fixture.to_csv(FIX, index = False)
oecd26.FILES['theta'] = FIX
FIXTHETA = {(i, v): t for i, v, t, _ in rows}


def raises(f, exc):
    try:
        f()
    except exc as e:
        return str(e) or type(e).__name__
    except Exception as e:
        return False
    return False


# ==== I: 'index' unchanged ====================================================================================
same, recorded = True, True
for t in oecd26.TURNOUT:
    for iso in oecd26.countries():
        try:
            a, b = oecd26.countryInputs(iso, t, data), oecd26.countryInputs(iso, t, data, 'index')
        except oecd26.NoTurnout:
            continue
        same &= a.keys() == b.keys() and all(np.array_equal(a[k], b[k]) if isinstance(a[k], np.ndarray)
                                             else a[k] == b[k] for k in a)
        recorded &= a['thetaSource'] == 'index'
inpUS = oecd26.countryInputs('USA')
cfgI = R.settings(coarse = True)
check("I: countryInputs' default is thetaSource 'index' (every value, 29 countries, both turnouts) and records it",
      same and recorded)
check("I: under 'index' the settings carry no thetaSource and the anchor key ignores a βSource",
      all('thetaSource' not in R.settings(c, s, r) for c in (False, True) for s in R.SPECS for r in R.BETARULES)
      and R.anchorKey(inpUS, β, cfgI) == R.anchorKey(inpUS, β, cfgI, 'any source')
      == oecd26.inputsKey('anchor', oecd26.modelInputs(inpUS), β, R.anchorSettings(cfgI)))

# ==== F: θ reaches getθ =======================================================================================
dev, flags = {}, []
for iso in ('USA', 'GBR', 'FRA', 'IRL'):
    inp = oecd26.countryInputs(iso, 'cps', data, 'fixA')
    m = oecd26.build(inp, β, ωSeed, 10.)
    θf = FIXTHETA[(iso, 'fixA')]
    dev[iso] = max(abs(m.getθ() - θf), float(np.max(np.abs(m.db['θ'].values - θf))), abs(inp['θ'] - θf))
    flags.append(inp['θRaw'] == θf and not R._dataColumns(inp)['θClipped'] and inp['thetaSource'] == 'fixA'
                 and inp['index'] == float(oecd26.indexFromTheta(θf)) and m.db['RR0'] == inp['index'])
check('F: the variant\'s θ reaches ModelOECD.getθ and db[\'θ\'] on every date within 1e-12 (USA 0.54, GBR 0.18, '
      'FRA 1, IRL 0)', max(dev.values()) < 1e-12 and all(flags),
      ', '.join('{} {:.1e}'.format(k, v) for k, v in dev.items()))

# ==== E: errors ===============================================================================================
eNaN = raises(lambda: oecd26.countryInputs('AUS', 'cps', data, 'fixA'), oecd26.NoTheta)
eOut = raises(lambda: oecd26.countryInputs('ITA', 'cps', data, 'fixA'), oecd26.NoTheta)
eMiss = raises(lambda: oecd26.countryInputs('NZL', 'cps', data, 'fixA'), oecd26.NoTheta)
check('E: a NaN θ (AUS), θ = 1.2 (ITA) and a missing row (NZL) raise NoTheta', bool(eNaN and eOut and eMiss),
      '{} | {}'.format(eNaN, eMiss))
eVar = raises(lambda: oecd26.countryInputs('GBR', 'cps', data, 'nosuch'), ValueError)
bad = os.path.join(tmp, 'bad.csv')
pd.DataFrame([('GBR', 'fixA', 0.1, True), ('GBR', 'fixA', 0.2, True)],
             columns = ['iso3', 'variant', 'theta', 'inSample']).to_csv(bad, index = False)
eDup = raises(lambda: oecd26.thetaFromFile('GBR', 'fixA', bad), ValueError)
pd.DataFrame([('GBR', 'index', 0.1, True)], columns = ['iso3', 'variant', 'theta', 'inSample']).to_csv(bad, index = False)
eIdx = raises(lambda: oecd26.thetaFromFile('GBR', 'index', bad), ValueError)
check("E: an unknown variant, a duplicate (iso3, variant) and a variant named 'index' raise ValueError, not NoTheta",
      bool(eVar and eDup and eIdx) and not isinstance(eVar, oecd26.NoTheta), eDup)

# ==== K: the keys =============================================================================================
inpA, inpB = oecd26.countryInputs('USA', 'cps', data, 'fixA'), oecd26.countryInputs('USA', 'cps', data, 'fixB')
cfgA, cfgB = R.settings(coarse = True, thetaSource = 'fixA'), R.settings(coarse = True, thetaSource = 'fixB')
kI, kA, kB = (R.anchorKey(inpUS, β, cfgI), R.anchorKey(inpA, β, cfgA, βSource), R.anchorKey(inpB, β, cfgB, βSource))
lay = lambda inp, cfg: oecd26.inputsKey('layer1', oecd26.modelInputs(inp), β, 1.3, 10., cfg)
check('K: the anchor and layer keys differ between sources, also where the U.S. θ is the same (fixB: the index\'s)',
      len({kI, kA, kB}) == 3 and len({lay(inpUS, cfgI), lay(inpA, cfgA), lay(inpB, cfgB)}) == 3
      and abs(inpB['θ'] - inpUS['θ']) < 1e-15, 'U.S. θ index {:.15f}, fixB {:.15f}'.format(inpUS['θ'], inpB['θ']))

# ==== O: the outdir and the country selection =================================================================
def mainExit(*argv):
    old = sys.argv
    sys.argv = ['runOECD26.py'] + list(argv)
    try:
        R.main()
        return False
    except SystemExit as e:
        return str(e)
    finally:
        sys.argv = old


check("O: the default outdir is results/oecd26 under 'index', results/oecd26_theta_<variant> otherwise",
      R.defaultOutdir() == R.OUTDIR == os.path.join(R.REPO, 'results', 'oecd26')
      and R.defaultOutdir('fixA') == os.path.join(R.REPO, 'results', 'oecd26_theta_fixA') == oecd26.thetaDir('fixA'))
mO = [mainExit('--theta', 'fixA', '--outdir', R.OUTDIR), mainExit('--theta', 'nosuch'), mainExit('--inSample')]
check('O: main refuses results/oecd26 under a variant, an unknown variant, and --inSample without a variant',
      all(mO), ' | '.join(str(x) for x in mO))
sel = R.selectCountries(None, 'fixA', True)
check('O: --inSample keeps the variant\'s inSample countries in oecd29.csv\'s order, and the U.S. (inSample False)',
      sel == [c for c in oecd26.countries() if c in {'USA', 'GBR', 'CAN', 'FRA', 'IRL', 'ITA'}]
      and R.selectCountries(['GBR', 'AUS'], 'fixA', True) == ['GBR'] and R.selectCountries(['AUS']) == ['AUS'],
      str(sel))

# ==== W: the driver's rows ====================================================================================
tmpW = os.path.join(tmp, 'W')
os.makedirs(tmpW)
fake = {'β': β, 'ω': 1.3, 'p': 10., 'inputsKey': 'hfake', 'R2020': np.nan}
w = R.stageLayer('layer1', 'cps', ['AUS', 'NZL', 'ITA'], tmpW, fake, cfgA)
dW = pd.read_csv(os.path.join(tmpW, 'layer1.csv'))
check("W: under a variant a NaN, missing or out-of-range θ gives a 'noTheta' row keyed on the variant, no solve",
      [r['status'] for r in w] == ['noTheta']*3 and set(dW['thetaSource']) == {'fixA'} and len(dW) == 3
      and (dW['nEqMax'] == -1).all())
eUS = raises(lambda: R.stageAnchor('cps', tmpW, R.settings(coarse = True, thetaSource = 'fixC'), (β, ωSeed, βSource)),
             SystemExit)
check('W: stageAnchor exits where the variant has no U.S. θ', bool(eUS), eUS)
leg = os.path.join(tmpW, 'anchor.csv')
pd.DataFrame([{'turnout': 'cps', 'spec': 'size', 'phi': R.PHI, 'commonX': R.COMMONX, 'betaRule': 'common',
               'status': 'ok', 'inputsKey': 'hold'}]).to_csv(leg, index = False)
hitI = R._onDisk(leg, R.KEYANCHOR, ['cps', 'size', R.PHI, R.COMMONX, 'common', 'index'])
hitA = R._onDisk(leg, R.KEYANCHOR, ['cps', 'size', R.PHI, R.COMMONX, 'common', 'fixA'])
R.migrate(leg)
check("W: a csv without thetaSource reads as 'index' (not as a variant) and migrates to the column at 'index'",
      hitI is not None and hitI['inputsKey'] == 'hold' and hitA is None
      and list(pd.read_csv(leg)['thetaSource']) == ['index'])

# ==== B: the variant's U.S. sweep =============================================================================
root = os.path.join(tmp, 'B')
eNo = raises(lambda: oecd26.usBeta(oecd26.sweepPath(root), thetaSource = 'fixA'), FileNotFoundError)
os.makedirs(os.path.dirname(oecd26.sweepPath(root)))
def sweep(θ0, ts = 'fixA'):
    pd.DataFrame([{'ρ': 1.0, 'residual': 1e-12, 'β': 0.6, 'ω': 1.2, 'X': 1.0, 'hbar': 0.4, 'commit': 'abc', 'timestamp': 'now',
                   'thetaSource': ts, 'θ0': θ0}]).to_csv(oecd26.sweepPath(root), index = False)
sweep(0.6)
eθ = raises(lambda: oecd26.usBeta(oecd26.sweepPath(root), thetaSource = 'fixA'), ValueError)
sweep(0.54, 'fixB')
eTs = raises(lambda: oecd26.usBeta(oecd26.sweepPath(root), thetaSource = 'fixA'), ValueError)
sweep(0.54)
bA = oecd26.usBeta(oecd26.sweepPath(root), thetaSource = 'fixA')
check('B: under a variant usBeta refuses a missing sweep and a row at another θ0 or variant, and accepts its own',
      bool(eNo and eθ and eTs) and bA[:2] == (0.6, 1.2) and 'theta=fixA θ0=0.54' in bA[2], '{} | {}'.format(eNo, bA[2]))
check('B: under a variant the anchor key moves with the sweep\'s source, and anchorKey requires one',
      R.anchorKey(inpA, β, cfgA, bA[2]) != R.anchorKey(inpA, β, cfgA, bA[2] + ' later')
      and bool(raises(lambda: R.anchorKey(inpA, β, cfgA), ValueError)))

# ==== U: ModelUS's θ0 =========================================================================================
def closedForm(m):
    """ ModelUS.getθ's RR0 route, eq calibration:theta, written out. """
    i, ii = m.db['RRGroups']
    ξ = m.db['ξ'].xs(m.db['t0'])
    h1 = (m.db['Γh']*m.db['Xi'][i]**ξ/m.db['ηi'][i]**(1+ξ)).xs(m.db['t0'])
    h2 = (m.db['Γh']*m.db['Xi'][ii]**ξ/m.db['ηi'][ii]**(1+ξ)).xs(m.db['t0'])
    return (1 - m.db['Ushare0'])*(m.db['RR0']*h1 - h2)/(1 - h2 - m.db['RR0']*(1 - h1))


new = lambda **over: ModelUS(pars = testmod.pars | {'ρ': 1.} | over, commonX = True, **testmod.kwargs)
m0, mN = new(), new(θ0 = np.nan)
check("U: without db['θ0'], or with it NaN, getθ is the RR0 closed form bit for bit (the workbook's U.S.)",
      m0.getθ() == closedForm(m0) == mN.getθ() and np.array_equal(m0.db['θ'].values, mN.db['θ'].values)
      and testmod.mLOG.getθ() == closedForm(testmod.mLOG), 'θ {!r}'.format(m0.getθ()))
θ0 = FIXTHETA[('USA', 'fixA')]
mT = new(θ0 = θ0)
θs = [mT.getθ(), float(np.max(np.abs(mT.db['θ'].values - θ0)))]
mT.updateAuxPars()
cal = mT.calibrate(preferences = 'LOG')
rep = cal['report']
devT = float(np.max(np.abs(mT.db['θ'].values - θ0)))
check("U: with db['θ0'] getθ is θ0 and db['θ'] holds it on every date through updateAuxPars and the common-X "
      "calibration at ρ = 1, which hits R, τ and hours", θs[0] == θ0 and θs[1] == 0. and devT < 1e-12
      and np.isclose(rep['R'], mT.db['R0'], rtol = 1e-7) and np.isclose(rep['τ'], mT.db['τ0'], rtol = 1e-7)
      and np.isclose(rep['hbar'], mT.db['h0'], rtol = 1e-7),
      'max |θ - θ0| {:.1e}; β {:.6f} ω {:.6f} (index: θ {:.4f})'.format(devT, cal['pars']['β'], cal['pars']['ω'],
                                                                         m0.getθ()))
check("U: db['θ0'] outside [0, 1] raises", bool(raises(lambda: new(θ0 = 1.3), ValueError)))
mE = runESC.buildUS({'spec': 'size', 'phi': 0.5, 'p': 10.}, commonX = True, θ0 = θ0)
mE.setWedge(p = 5.)
eFlat = raises(lambda: ModelESC(pars = testmod.pars | {'θ0': θ0}, wedge = {'spec': 'flat', 'phi': 0.5, 'p': 1.},
                                **testmod.kwargs), NotImplementedError)
mO26 = oecd26.build(inpUS, β, ωSeed, 10.)
mO26.db['θ0'] = 0.5
eOECD = raises(mO26.updateAuxPars, ValueError)
check("U: ModelESC returns θ0 under 'size' (runESC.buildUS, through setWedge) and refuses it under 'flat'; ModelOECD "
      "refuses it (its θ is RR0's)", float(np.max(np.abs(mE.db['θ'].values - θ0))) == 0. and bool(eFlat)
      and bool(eOECD), '{} | {}'.format(eFlat, eOECD))

# ==== C: the U.S. drivers' --theta ============================================================================
cOut = CRG.thetaRun('fixA', True)
cSub = os.path.join(oecd26.thetaDir('fixA'), 'calibration')
cRef = [raises(lambda: CRG.thetaRun('fixA', True, out = os.path.join(CRG.OUTDIR, 'US_rhoGridCommonX.csv')), SystemExit),
        raises(lambda: CRG.thetaRun('fixA', True, medicare = 0.029), SystemExit),
        raises(lambda: CRG.thetaRun('fixC', True), SystemExit)]
check('C: calibrateRhoGrid --theta: θ0 the variant\'s U.S. θ, csv and pickles under the variant\'s calibration/; '
      'results/calibration/, --medicare and a variant without a U.S. θ refused',
      cOut == (θ0, os.path.join(cSub, 'US_rhoGridCommonX.csv'), os.path.join(cSub, 'instancesUSCommonX'))
      and all(cRef) and not os.path.exists(oecd26.thetaDir('fixA')), ' | '.join(str(x) for x in cRef))
mD = runESC.buildUS({'spec': 'size', 'phi': 0.5, 'p': 10.}, commonX = True)
check("C: runESC without a variant: results/calibration's sweep, the workbook's θ (RR0), the fine grids",
      runESC.usSweep(True) == os.path.join(runESC.REPO, 'results', 'calibration', 'US_rhoGridCommonX.csv')
      and runESC.thetaColumns() == {} and mD.ESC.nθ == 41 and mD.getθ() == closedForm(mD)
      and runESC.setTheta() == runESC.OUTDIR and runESC.THETA['θ0'] is None)
saved = dict(runESC.THETA)
try:
    outE = runESC.setTheta('fixA', root, ['calib', 'path', 'shocks', 'country', 'corner'], coarse = True)
    mV, mF = runESC.buildUS({'spec': 'size', 'phi': 0.5, 'p': 10.}, commonX = True), runESC.buildEU('FR', None, commonX = True)
    cal0 = pd.DataFrame([{'spec': 'size', 'phi': 0.5} | runESC.thetaColumns()])
    okV = (outE == os.path.join(root, 'esc') and float(np.max(np.abs(mV.db['θ'].values - θ0))) == 0.
           and mV.simpleβinv() == 0.6 and mV.ESC.nθ == 21 and mF.usRefSource(1.0)['β'] == 0.6 and mF.getθ() == 1.
           and runESC.checkCalib(cal0, 'x') is cal0)
    eCal = raises(lambda: runESC.checkCalib(cal0.assign(θ0 = 0.6), 'x'), SystemExit)
finally:
    runESC.THETA.update(saved)
eRef = [raises(lambda: runESC.setTheta('fixA', root, ['calib', 'fig1']), SystemExit),
        raises(lambda: runESC.setTheta('fixA', 'results'), SystemExit),
        raises(lambda: runESC.setTheta('fixA', os.path.join(tmp, 'none')), SystemExit),
        raises(lambda: runESC.setTheta(None, coarse = True), SystemExit), eCal]
check("C: runESC --theta: every U.S. model at θ0 seeded off the variant's sweep, France at its own θ against that "
      "sweep's β, root/esc, the coarse grid; other stages, results/esc/, a missing sweep, --coarse alone and a "
      "calibration at another θ0 refused", okV and all(eRef) and runESC.THETA == saved,
      ' | '.join(str(x) for x in eRef))
sOut = RS.thetaRun('fixA', root, True, [1.0])
sOutFR = sOut[3]
sOut = sOut[:3]
sRef = [raises(lambda: RS.thetaRun('fixA', root, True, [0.5, 1.0]), SystemExit),
        raises(lambda: RS.thetaRun('fixA', root, True, [1.0], medicare = 0.029), SystemExit),
        raises(lambda: RS.thetaRun('fixA', root, True, [1.0], freeTheta = True), SystemExit),
        raises(lambda: RS.thetaRun('fixA', 'results', True, [1.0]), SystemExit)]
mS = RS.hostModel(1.0, True, RS.hostRow(1.0, True, 'US', sOut[1]), {'n': 51}, θ0 = sOut[0])
check("C: runShocksUS --theta: θ0, the variant's sweep (every rho asked for) and root/shocks/; --medicare, "
      "--freeTheta and results/shocks/ refused; the host model carries θ0 on every date",
      sOut == (θ0, os.path.join(root, 'calibration'), os.path.join(root, 'shocks', 'US_shocksCommonX.csv'))
      and all(sRef) and float(np.max(np.abs(mS.db['θ'].values - θ0))) == 0. and mS.simpleβinv() == 0.6
      and sOutFR == FIXTHETA[('FRA', 'fixA')], ' | '.join(str(x) for x in sRef))

# ==== S: τ0 from the file's spending ==========================================================================
α = float(testmod.pars['α'])
gI, gB = oecd26.countryInputs('GBR', 'cps', data), oecd26.countryInputs('GBR', 'cps', data, 'fixB')
gA = oecd26.countryInputs('GBR', 'cps', data, 'fixA')
check("S: under a variant τ0 is the file's spending/100/(1 - α) (GBR fixB 9.0 against figure 1.1's 7.836); a "
      "variant at figure 1.1's spending gives the index's τ0 bit for bit",
      gB['τ0'] == 9.0/100/(1 - α) and gB['spending'] == 9.0 and gA['τ0'] == gI['τ0'] and gI['spending'] == 7.836,
      'τ0 index {!r}, fixB {!r}'.format(gI['τ0'], gB['τ0']))
badC = os.path.join(tmp, 'badC.csv')
fixture.assign(spending = np.where(fixture['variant'] == 'C', fixture['spending'] + 1e-6, fixture['spending'])) \
    .to_csv(badC, index = False)
oecd26.FILES['theta'] = badC
eSp = raises(lambda: oecd26.countryInputs('GBR', 'cps', data, 'C'), ValueError)
okB = oecd26.countryInputs('GBR', 'cps', data, 'fixB')['spending'] == 9.0
oecd26.FILES['theta'] = FIX
real = oecd26.readTheta(os.path.join(oecd26.DATA, 'oecd26_theta.csv'))
fig1 = pd.read_csv(os.path.join(oecd26.DATA, 'oecdFigure1.csv'), index_col = 'iso3')['pensionSpending']
devS = {v: float(np.max(np.abs(real.loc[real['variant'] == v, 'spending'].values
                               - np.c_[SPEND.loc[real.loc[real['variant'] == v, 'iso3']].values,
                                       fig1.loc[real.loc[real['variant'] == v, 'iso3']].values].T)))
        for v in oecd26.SPENDINGASFIGURE}
check("S: for a variant of SPENDINGASFIGURE ('C') a spending 1e-6 off figure 1.1's raises, for another (fixB) it "
      "does not; data/oecd26_theta.csv's paper, A, A2pt and C equal pensionSpending (oecd29.csv and oecdFigure1.csv)",
      bool(eSp) and okB and max(devS.values()) <= 1e-9 and set(devS) == {'paper', 'A', 'A2pt', 'C'},
      ', '.join('{} {:.1e}'.format(k, v) for k, v in devS.items()))

# ==== M: --main ===============================================================================================
mainV = oecd26.paperTheta()
eMain = [raises(lambda: oecd26.thetaRoot('fixA', main = True), ValueError),
         raises(lambda: oecd26.thetaRoot('index', main = True), ValueError)]
check("M: config.US['theta'] is 'C'; thetaRoot is results/ for it under --main and the variant's directory without, "
      "and refuses --main for another variant or 'index'",
      mainV == 'C' and oecd26.thetaRoot('C', True) == oecd26.RESULTS and oecd26.thetaRoot('C') == oecd26.thetaDir('C')
      and all(eMain), ' | '.join(str(x) for x in eMain))
cM = CRG.thetaRun('C', True, main = True)
cMv = CRG.thetaRun('C', False, main = True)
cMe = [raises(lambda: CRG.thetaRun('fixA', True, main = True), SystemExit),
       raises(lambda: CRG.thetaRun('C', True, root = 'logs', main = True), SystemExit),
       raises(lambda: CRG.thetaRun('C', True), SystemExit) is False]
check("M: calibrateRhoGrid --theta C --main writes results/calibration/US_rhoGrid{CommonX}.csv and instancesUS*; "
      "--main for another variant or with --root refused; without --main C goes to its own directory",
      cM == (0.544496, os.path.join(CRG.OUTDIR, 'US_rhoGridCommonX.csv'), os.path.join(CRG.OUTDIR, 'instancesUSCommonX'))
      and cMv[1] == os.path.join(CRG.OUTDIR, 'US_rhoGrid.csv') and all(cMe), ' | '.join(str(x) for x in cMe))
mOm = [mainExit('--theta', 'fixA', '--main'), mainExit('--main'), mainExit('--theta', 'C', '--main', '--outdir', tmp)]
check("M: runOECD26 --main refuses another variant than config.US['theta'], no variant and --outdir", all(mOm),
      ' | '.join(str(x) for x in mOm))
eE = [raises(lambda: runESC.setTheta('fixA', None, ['calib'], main = True), SystemExit),
      raises(lambda: runESC.setTheta(None, main = True), SystemExit),
      raises(lambda: runESC.setTheta('C', root, ['calib'], main = True), SystemExit),
      raises(lambda: RS.thetaRun('fixA', None, True, [1.0], main = True), SystemExit)]
check("M: runESC.setTheta and runShocksUS.thetaRun refuse --main for another variant, alone, or with --root",
      all(eE) and runESC.THETA == saved, ' | '.join(str(x) for x in eE))
import runESCcrra, runShocksXi, stationaryApprox, stationaryApproxESC

def argvExit(mod, *argv):
    old = sys.argv
    sys.argv = ['x.py'] + list(argv)
    try:
        mod.main()
        return False
    except SystemExit as e:
        return str(e) or 'exit'
    finally:
        sys.argv = old
        runESC.THETA.update(saved)
eX = [argvExit(runShocksXi, '--theta', 'C'), argvExit(stationaryApprox, '--theta', 'C'),
      argvExit(stationaryApproxESC, '--main'), argvExit(runShocksXi, '--theta', 'fixA', '--main'),
      argvExit(runESCcrra, '--theta', 'C', '--exact', '--stage', 'permanent')]
check("M: runShocksXi, stationaryApprox, stationaryApproxESC take --theta with --main only and for config.US['theta']; "
      "runESCcrra refuses a variant's permanent stage", all(eX), ' | '.join(str(x) for x in eX))

# ==== R: France and the UK at θ0 ==============================================================================
import testEU
mF0, mU0 = testEU.model('FR', commonX = True), testEU.model('UK', commonX = True)
mFθ = testEU.model('FR', commonX = True, θ0 = 0.7)
θFR0 = [float(np.max(np.abs(mFθ.db['θ'].values - 0.7)))]
mFθ.LOG.initGS({'n': 51, 'smoothKnots': 4, 'interpKind': 'linear'})
repF = mFθ.calibrate(preferences = 'LOG')['report']
θFR0.append(float(np.max(np.abs(mFθ.db['θ'].values - 0.7))))
check("R: testEU.model's θ0 is France's θ on every date before and after its ω calibration at the U.S. cuts (LOG, "
      "ρ = 1, n = 51), which hits τ0; without θ0 France's θ is 1 and the UK's the RR0 closed form, bit for bit",
      θFR0 == [0., 0.] and np.isclose(repF['τ'], mFθ.db['τ0'], rtol = 1e-7) and mF0.getθ() == 1.
      and float(mF0.db['θ'].values.min()) == 1. and mU0.getθ() == closedForm(mU0),
      'France at θ0 0.7: ω {:.6f}'.format(float(mFθ.db['ω'].xs(mFθ.db['t'][mFθ.db['t0']]))))
import calibrateRhoGridEU as CEU
eu = CEU.thetaRun('fixA', 'UK', True, root = root, rhos = [1.0])
euE = [raises(lambda: CEU.thetaRun('fixA', 'FR', True, root = root, rhos = [0.5]),
              SystemExit),
       raises(lambda: CEU.thetaRun('fixB', 'FR', True, root = root, rhos = [1.0]),
              SystemExit),
       raises(lambda: CEU.thetaRun('fixA', 'FR', True, out = os.path.join(CEU.OUTDIR, 'FR_rhoGridCommonX.csv'),
                                   root = root, rhos = [1.0]), SystemExit),
       raises(lambda: CEU.thetaRun('fixA', 'FR', True, rhos = [1.0], main = True), SystemExit)]
check("R: calibrateRhoGridEU --theta: the UK's θ0 (GBR), csv and pickles under root/calibration/, the variant's U.S. "
      "sweep; a rho it lacks, a sweep at another θ0, results/calibration/ and --main for another variant refused",
      eu == (0.18, os.path.join(root, 'calibration', 'UK_rhoGridCommonX.csv'),
             os.path.join(root, 'calibration', 'instancesUKCommonX'), oecd26.sweepPath(root)) and all(euE),
      ' | '.join(str(x) for x in euE))
try:
    runESC.setTheta('fixA', root, ['pathHost', 'country', 'corner'], coarse = True)
    mFA, mUA = runESC.buildEU('FR', None, commonX = True), runESC.buildEU('UK', None, commonX = True)
    okEU = mFA.getθ() == 1.0 and float(np.max(np.abs(mUA.db['θ'].values - 0.18))) == 0.
    tc = runESC.thetaColumns()
    calR = pd.DataFrame([{'spec': 'size', 'phi': 0.5, 'commonX': True} | tc,
                         {'spec': 'scale', 'phi': 0.25, 'commonX': True, 'thetaSource': np.nan, 'θ0': np.nan},
                         {'spec': 'size', 'phi': 0.5, 'commonX': False, 'thetaSource': np.nan, 'θ0': np.nan}])
    okR = runESC.checkCalib(calR, 'x', ['size'], [0.5], True) is calR
    eR = [raises(lambda: runESC.checkCalib(calR, 'x', ['size', 'scale'], [0.5, 0.25], True), SystemExit),
          raises(lambda: runESC.checkCalib(calR, 'x'), SystemExit)]
    fc = os.path.join(tmp, 'crra.csv')
    pd.DataFrame([{'ρ': 2.0, 'spec': 'size', 'phi': 0.5, 'commonX': True, 'method': 'exact', 'p': 4.0} | tc,
                  {'ρ': 2.0, 'spec': 'size', 'phi': 0.5, 'commonX': True, 'method': 'exact', 'p': 3.0}]
                 ).to_csv(fc, index = False)
    pV = runESCcrra.readCalibratedP(fc, 2.0, 'size', 0.5, True, 'exact')
    mC = runESCcrra.buildUS(1.0, None, commonX = True, gs = {'n': 51, 'ns': 50, 'smoothKnots': 4, 'interpKind': 'linear'})
    okC = float(np.max(np.abs(mC.db['θ'].values - θ0))) == 0. and mC.simpleβinv() == 0.6
finally:
    runESC.THETA.update(saved)
pI = runESCcrra.readCalibratedP(fc, 2.0, 'size', 0.5, True, 'exact')
stationaryApprox.THETA.update({'variant': 'C', 'θ0': 0.544496})
try:
    mSt = stationaryApprox.build({'β': 0.6, 'ω': 1.2, 'X': 4.0}, 2.0, True, {'n': 51, 'ns': 50, 'smoothKnots': 4,
                                                                           'interpKind': 'linear'})
finally:
    stationaryApprox.THETA.update({'variant': None, 'θ0': None})
check("R: under setTheta France and the UK take the FRA and GBR rows (fixA 1, 0.18) in runESC.buildEU and pathHost "
      "is a variant stage; checkCalib reads only the rows asked for (a legacy row of another spec or commonX passes, "
      "one asked for refuses); runESCcrra.readCalibratedP keeps the variant's row (4.0, not the index's 3.0, which it "
      "reads without a variant), runESCcrra.buildUS and stationaryApprox.build carry θ0",
      okEU and okR and all(eR) and pV == (4.0, 'exact') and pI == (3.0, 'exact') and okC
      and float(np.max(np.abs(mSt.db['θ'].values - 0.544496))) == 0.,
      'variant p {}, index p {}; {}'.format(pV, pI, ' | '.join(str(x) for x in eR)))

# ==== N: c5Numbers and runHorizon under --theta ===============================================================
import c5Numbers, runHorizon
c5Saved, hzSaved = dict(c5Numbers.THETA), dict(runHorizon.THETA)


def argvExitN(mod, *argv):
    old = sys.argv
    sys.argv = ['x.py'] + list(argv)
    try:
        mod.main()
        return False
    except SystemExit as e:
        return str(e) or 'exit'
    finally:
        sys.argv = old
        runESC.THETA.update(saved)
        c5Numbers.THETA.update(c5Saved)
        runHorizon.THETA.update(hzSaved)


eN = [argvExitN(c5Numbers, 'a1', '--theta', 'C'), argvExitN(c5Numbers, 'a1', '--main'),
      argvExitN(c5Numbers, 'a1', '--theta', 'fixA', '--main'), argvExitN(runHorizon, '--stage', 'log', '--theta', 'C'),
      argvExitN(runHorizon, '--stage', 'log', '--theta', 'fixA', '--main')]
frame = pd.DataFrame({'k': [1, 2, 3, 4], 'thetaSource': ['C', 'C', np.nan, 'index'],
                      'θ0': [0.544496, 0.5, np.nan, np.nan]})
noVariant = [list(c5Numbers._at(frame)['k']), list(runHorizon._at(frame)['k'])]
try:
    c5Numbers.setTheta('C', True)
    hzN = runHorizon.setTheta('C', True)
    atC = [list(c5Numbers._at(frame)['k']), list(runHorizon._at(frame)['k'])]
    mN, _ = c5Numbers.usModel(1.0)
    mH = runHorizon.build(2.0, 0.6, 1.2, 4.0, runHorizon.BASE_TSS)
    θN = [float(np.max(np.abs(m.db['θ'].values - 0.544496))) for m in (mN, mH)]
    okEsc = runESC.THETA['variant'] == 'C' and runESC.THETA['θ0'] == 0.544496 and runESC.THETA['main']
    fm = os.path.join(tmp, 'merge.csv')
    pd.DataFrame([{'ρ': 0.5, 'date': 2020, 'τ': 1.}, {'ρ': 2.0, 'date': 2020, 'τ': 2.}]).to_csv(fm, index = False)
    runHorizon.mergeWrite(fm, [{'ρ': 0.5, 'date': 2020, 'τ': 3.} | runHorizon._tag()], ['ρ', 'date'])
    runHorizon.mergeWrite(fm, [{'ρ': 2.0, 'date': 2020, 'τ': 4.} | runHorizon._tag()], ['ρ', 'date'])
    runHorizon.mergeWrite(fm, [{'ρ': 0.5, 'date': 2020, 'τ': 5.} | runHorizon._tag()], ['ρ', 'date'])
    mg = pd.read_csv(fm).sort_values('ρ')
    okMerge = (list(mg['τ']) == [5., 4.] and set(mg['thetaSource']) == {'C'} and not os.path.exists(fm + '.lock'))
    fx = os.path.join(tmp, 'C5_x.csv')
    pd.DataFrame([{'experiment': 'X1', 'θ2020': 0.7}, {'experiment': 'X2', 'θ2020': 0.8}]).to_csv(fx, index = False)
    c5Numbers._mergeExperiments([{'experiment': 'X1', 'θ2020': 0.5}], fx)
    mx = pd.read_csv(fx)
    okX = list(mx['experiment']) == ['X1'] and list(mx['thetaSource']) == ['C'] and list(mx['θ0']) == [0.544496]
finally:
    runESC.THETA.update(saved)
    c5Numbers.THETA.update(c5Saved)
    runHorizon.THETA.update(hzSaved)
check("N: c5Numbers and runHorizon take --theta with --main only and for config.US['theta']; _at keeps the run's θ "
      "(C at θ0, or the rows without thetaSource without a variant); under C usModel and runHorizon.build impose θ0 on "
      "every date, runESC.THETA is installed; runHorizon.mergeWrite drops the rows at another θ, replaces a key, "
      "leaves no lock; c5Numbers._mergeExperiments drops the other θ's rows and tags its own",
      all(eN) and noVariant == [[3, 4], [3, 4]] and atC == [[1], [1]] and θN == [0., 0.] and okEsc and okMerge
      and okX and hzN is None and c5Numbers.THETA == c5Saved and runHorizon.THETA == hzSaved,
      ' | '.join(str(x) for x in eN))

shutil.rmtree(tmp, ignore_errors = True)
print('\n({:.0f}s)'.format(time.time() - tic))
report()
