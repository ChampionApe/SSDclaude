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
  C  The U.S. drivers' --theta. calibrateRhoGrid.thetaRun: θ0, the variant's calibration/; results/calibration/
     refused. runESC without a variant: results/calibration's sweep, the workbook's θ, the fine grids;
     setTheta: every U.S. model at θ0 seeded off the variant's sweep, France and the UK at their FRA and GBR rows
     against that sweep, root/esc, the coarse grid; other stages, results/esc/, a missing sweep, a calibration at
     another θ0 refused. runShocksUS.thetaRun: the variant's sweep at every rho asked for, root/shocks/, France's θ0;
     results/shocks/ refused; the host model carries θ0.
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
  G  The drivers' defaults, guards, paths and exit codes: runOECD26's --turnout and --omegaRule are config's, 'cps' and
     --coarse are refused into results/oecd26/, countryInputs takes the turnout; the retired Medicare reading, ESC stages
     and dead helpers are gone; a relative --out, --pkldir or --root is the caller's; runShocksUS.writeRows merges
     atomically; runESC.main exits 1 after a survived failure; readCalibratedP, c5Numbers.escRows and
     runHorizon.escLambda read converged rows only; runTauTheta.selfCheck raises.
  X  The ξ drivers: runShocksXi and runESCxi need --theta --main, the workbook ξ runs first, the rows at another θ0 are
     replaced, the self-check reads the rows at the run's θ.
  T  Without --theta calibrateRhoGrid{,EU}, runShocksUS, runESC, runESCcrra, runTauTheta and stationaryApproxESC refuse
     to write into results/ (oecd26.indexTheta); --theta index runs the workbook's θ there, an output outside results/
     runs without it.
  Z  The sweeps resume a row only at the run's settings (calibrateRhoGrid.staleSettings/resumeAt): another n, ns (CRRA
     rows), smoothKnots or interpKind, and for France and the UK another retAge or U.S. reference β (βUS), is re-solved;
     a row without retAge/βUS is resumed unchecked; the published sweeps of results/calibration/ resume whole at
     config.US's settings. End to end at ρ = 1 (LOG, n = 51) into temporary csvs.
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
θUSindex = oecd26.countryInputs('USA', 'cps')['θ']
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
inpUS = oecd26.countryInputs('USA', 'cps')
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
        raises(lambda: CRG.thetaRun('fixC', True), SystemExit)]
check('C: calibrateRhoGrid --theta: θ0 the variant\'s U.S. θ, csv and pickles under the variant\'s calibration/; '
      'results/calibration/ and a variant without a U.S. θ refused',
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
eRef = [raises(lambda: runESC.setTheta('fixA', root, ['calib', 'nosuch']), SystemExit),
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
        raises(lambda: RS.thetaRun('fixA', 'results', True, [1.0]), SystemExit)]
mS = RS.hostModel(1.0, True, RS.hostRow(1.0, True, 'US', sOut[1]), {'n': 51}, θ0 = sOut[0])
check("C: runShocksUS --theta: θ0, the variant's sweep (every rho asked for) and root/shocks/; results/shocks/ "
      "refused; the host model carries θ0 on every date",
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
      argvExit(runESCcrra, '--theta', 'C', '--exact', '--stage', 'sequential')]
check("M: runShocksXi, stationaryApprox, stationaryApproxESC take --theta with --main only and for config.US['theta']; "
      "runESCcrra refuses a variant's sequential stage", all(eX), ' | '.join(str(x) for x in eX))

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

# ==== G: defaults, guards, paths and exit codes of the drivers ==================================================
import argparse
import runShocksXi, runESCxi, runTauTheta, stationaryApprox, stationaryApproxESC, runESCcrra
from runESCcrra import readCalibratedP
tmpG = os.path.join(tmp, 'G')
os.makedirs(tmpG)
runESC.THETA.update(saved)


class Stop(Exception):
    pass


def defaultsOf(mod, *argv):
    """ The namespace mod.main() parses from argv; main stops there, nothing runs. """
    orig, box = argparse.ArgumentParser.parse_args, {}

    def grab(self, args = None, namespace = None):
        box['a'] = orig(self, list(argv), namespace)
        raise Stop

    argparse.ArgumentParser.parse_args = grab
    try:
        mod.main()
    except Stop:
        pass
    finally:
        argparse.ArgumentParser.parse_args = orig
    return box['a']


def until(mod, name, argv, stub = None, run = None, **others):
    """ (run or mod).main() on argv with mod.<name> replaced by `stub` (by default a stub that records its arguments and
    raises Stop), mod.<others> by theirs, oecd26.usBeta by one returning the U.S. β: {'args': what the default stub
    was called with, 'exit': the text of a SystemExit}. """
    got, saved_ = {}, {k: getattr(mod, k) for k in (name, *others)}

    def stop(*args, **kw):
        got['args'] = args
        raise Stop

    ub, old = oecd26.usBeta, sys.argv
    setattr(mod, name, stub or stop)
    for k, v in others.items():
        setattr(mod, k, v)
    oecd26.usBeta = lambda *a, **k: (β, ωSeed, 'stub')
    sys.argv = ['x.py'] + list(argv)
    try:
        (run or mod).main()
    except Stop:
        pass
    except SystemExit as e:
        got['exit'] = str(e) or 'exit'
    finally:
        sys.argv, oecd26.usBeta = old, ub
        for k, v in saved_.items():
            setattr(mod, k, v)
    return got


vOE = R.paperVariant()
dG = defaultsOf(R)
gA = until(R, 'stageAnchor', ['--stage', 'anchor', '--outdir', tmpG])
gL = until(R, 'stageLayer', ['--stage', 'layer1', '--outdir', tmpG], anchorRow = lambda *a: {'status': 'ok'})
check("G: runOECD26's --turnout and --omegaRule default to config.US['oecd26'] ('csesFlat', 'mean'), the stages get them",
      dG.turnout == [vOE['turnout']] == ['csesFlat'] and dG.omegaRule == vOE['omegaRule'] == 'mean'
      and gA['args'][0] == 'csesFlat' and gL['args'][7] == 'mean', '{} {}'.format(dG.turnout, dG.omegaRule))
gC, gCo = until(R, 'stageAnchor', ['--turnout', 'cps']), until(R, 'stageAnchor', ['--turnout', 'cps', '--outdir', tmpG])
gK, gKo = until(R, 'stageAnchor', ['--coarse']), until(R, 'stageAnchor', ['--coarse', '--outdir', tmpG])
gKm = until(R, 'stageAnchor', ['--theta', mainV, '--main', '--coarse'])
gP = until(R, 'stageAnchor', ['--turnout', 'cses', 'csesFlat'])
check("G: runOECD26 refuses turnout 'cps' and --coarse into results/oecd26/ (also under --main), allows them into another "
      "--outdir, and the paper's turnouts into results/oecd26/",
      'cps' in gC.get('exit', '') and 'args' not in gC and gCo.get('args', [None])[0] == 'cps'
      and '--coarse' in gK.get('exit', '') and 'args' not in gK and 'args' in gKo
      and '--coarse' in gKm.get('exit', '') and 'args' not in gKm and gP.get('args', [None])[0] == 'cses',
      ' | '.join(str(x.get('exit')) for x in (gC, gK, gKm)))
eT = [raises(lambda: oecd26.countryInputs('GBR'), TypeError),
      raises(lambda: oecd26.inputsFrom('X', 'X', [1.]*9, [.3]*3, [1.]*3, [1.]*3, 1., .5), TypeError)]
check("G: oecd26.countryInputs and inputsFrom take the turnout explicitly (no 'cps' default); one dict for the anchor "
      "and twin turnouts", all(eT) and R.ANCHORTURNOUT == {'csesFlat': 'cses'} and not hasattr(R, 'TWIN')
      and not hasattr(oecd26, 'isStandard'), ' | '.join(str(x) for x in eT))
check('G: the Medicare reading, the unwired ESC stages, the dead readers and helpers are gone',
      not any((hasattr(testmod, 'reading'), hasattr(runESC, 'stagePermanent'), hasattr(runESC, 'stageFig1'),
               hasattr(runESCcrra, 'stagePermanentCRRA'), hasattr(testEU, 'retAgeFR'), hasattr(testEU, 'frenchNu'),
               hasattr(RS, 'usRow'), hasattr(runESC, 'json'))))
dE, dC = defaultsOf(runESC), defaultsOf(runESCcrra)
eS = [raises(lambda: defaultsOf(runESC, '--stage', 'fig1'), SystemExit),
      raises(lambda: defaultsOf(runESC, '--stage', 'permanent'), SystemExit),
      raises(lambda: defaultsOf(runESCcrra, '--stage', 'sens'), SystemExit),
      raises(lambda: defaultsOf(runESCcrra, '--stage', 'permanent'), SystemExit)]
check("G: runESC's default stages are calib path shocks country, runESCcrra's calib path shocks; fig1, permanent and sens "
      "are no choice", dE.stage == ['calib', 'path', 'shocks', 'country'] and dC.stage == ['calib', 'path', 'shocks']
      and all(eS), ' | '.join(str(x) for x in eS))
ρSt = oecd26.paperConfig().US['ρStationary']
check("G: stationaryApprox's default --rho is config.US['ρStationary'], and the drivers' literals of the design grid "
      "are config.US['esc']['nCand2D']", list(defaultsOf(stationaryApprox).rho) == list(ρSt) == [0.5, 2.0]
      and c5Numbers.NCAND2D == runHorizon.N_CAND_2D == oecd26.paperConfig().US['esc']['nCand2D'])

# relative --out, --pkldir, --root: the caller's working directory's, absolute before the drivers change directory
rel = ['rel/o.csv', 'rel/p', 'rel/r']
absOf = lambda mod, x: os.path.abspath(os.path.join(mod.CWD, x))
gCRG = until(CRG, 'thetaRun', ['--theta', 'fixA', '--out', rel[0], '--pkldir', rel[1], '--root', rel[2]])['args']
gCEU = until(CEU, 'thetaRun', ['--theta', 'fixA', '--out', rel[0], '--pkldir', rel[1], '--root', rel[2]])['args']
gRS = until(RS, 'thetaRun', ['--theta', 'fixA', '--root', rel[2]])['args']
gRE = until(runESC, 'setTheta', ['--theta', 'fixA', '--root', rel[2]])['args']
gRC = until(runESCcrra, 'setThetaCRRA', ['--theta', 'fixA', '--root', rel[2]])['args'][0]
gTT = until(runESC, 'setTheta', ['--theta', 'fixA', '--root', rel[2]], run = runTauTheta)['args']
check("G: a relative --out, --pkldir or --root is absolute against the caller's directory in calibrateRhoGrid{,EU}, "
      "runShocksUS, runESC, runESCcrra and runTauTheta",
      gCRG[2:5] == tuple(absOf(CRG, x) for x in rel) and gCEU[3:6] == tuple(absOf(CEU, x) for x in rel)
      and gRS[1] == absOf(RS, rel[2]) and gRE[1] == absOf(runESC, rel[2]) and gRC.root == absOf(runESCcrra, rel[2])
      and gTT[1] == absOf(runTauTheta, rel[2]), str(gCRG[2:5]))

# the merge of runShocksUS: a subset keeps the other rows, another θ is dropped, a failed rename leaves the file
fw = os.path.join(tmpG, 'shocks.csv')
tagC = {'thetaSource': 'C', 'θ0': 0.544496}
mk = lambda ρ, τ, tag = tagC: {'ρ': ρ, 'family': 'ageing', 'scenario': 'Acute', 'effect': 'full', 'τ': τ} | tag
pd.DataFrame([mk(0.5, .1), mk(1.0, .2), mk(2.0, .3)]).to_csv(fw, index = False)
RS.writeRows(fw, [mk(1.0, 9.)], tagC)
d1 = pd.read_csv(fw).sort_values('ρ')
before = open(fw, 'rb').read()
osReplace = os.replace
os.replace = lambda *a: (_ for _ in ()).throw(OSError('rename'))
try:
    eW = raises(lambda: RS.writeRows(fw, [mk(0.5, 7.)], tagC), OSError)
finally:
    os.replace = osReplace
untouched = open(fw, 'rb').read() == before and not os.path.exists(fw + '.tmp')
tag5 = {'thetaSource': 'C', 'θ0': 0.5}
RS.writeRows(fw, [mk(1.0, 5., tag5)], tag5)
d2 = pd.read_csv(fw)
check("G: runShocksUS.writeRows replaces the rows of its own (ρ, family, scenario, effect) and keeps the others; a "
      "failing rename leaves the file as it was; the rows at another θ0 are dropped",
      list(d1['ρ']) == [0.5, 1.0, 2.0] and list(d1['τ']) == [.1, 9., .3] and bool(eW) and untouched
      and list(d2['τ']) == [5.] and list(d2['θ0']) == [0.5], str(list(d1['τ'])))

# the exit code of a run that survived a failure; the exact CRRA cost read from file
runESC.FAILURES.clear()
stageCorner0, argv0 = runESC.stageCorner, sys.argv
try:
    sys.argv = ['x.py', '--stage', 'corner', '--spec', 'size', '--phi', '0.5', '--commonX', '--theta', 'index']
    runESC.stageCorner = lambda *a, **k: runESC.noteFailure('corner', ValueError('boom'))
    rcFail = runESC.main()
    nFail = len(runESC.FAILURES)
    runESC.FAILURES.clear()
    runESC.stageCorner = lambda *a, **k: None
    rcOK = runESC.main()
finally:
    runESC.stageCorner, sys.argv = stageCorner0, argv0
    runESC.FAILURES.clear()
check('G: runESC.main exits 1 when a stage noted a failure it survived, 0 otherwise', (rcFail, nFail, rcOK) == (1, 1, 0),
      str((rcFail, nFail, rcOK)))
fcr = os.path.join(tmpG, 'escCalibrationCRRA.csv')
crra = lambda ρ, m_, p_, ok: {'ρ': ρ, 'spec': 'size', 'phi': 0.5, 'commonX': True, 'method': m_, 'p': p_, 'converged': ok,
                              'β': .6, 'ω': 1.2}
pd.DataFrame([crra(2.0, 'exact', 4.0, True), crra(2.0, 'exact', 9.0, False), crra(0.5, 'path', 1.5, True),
              crra(0.5, 'path', 8.0, False)]).to_csv(fcr, index = False)
rc = [readCalibratedP(fcr, 2.0, 'size', 0.5, True, 'exact'), readCalibratedP(fcr, 0.5, 'size', 0.5, True, 'exact'),
      readCalibratedP(fcr, 0.5, 'size', 0.5, True, 'exact', fallback = True), readCalibratedP(fcr, 0.5, 'size', 0.5, True, 'path')]
escDir0, build0 = stationaryApproxESC.ESCDIR, runESCcrra.buildUS
stationaryApproxESC.ESCDIR = tmpG
runESCcrra.buildUS = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('built'))
try:
    eRef = raises(lambda: stationaryApproxESC.runCRRA(0.5, 'size', 0.5, True, 50, 21), KeyError)
    eBuilt = raises(lambda: stationaryApproxESC.runCRRA(0.5, 'size', 0.5, True, 50, 21, allowPathP = True), RuntimeError)
finally:
    stationaryApproxESC.ESCDIR, runESCcrra.buildUS = escDir0, build0
check("G: readCalibratedP reads converged rows only (exact 4.0, not the failed 9.0; path 1.5, not 8.0) and falls back to "
      "the path p only on request; stationaryApproxESC refuses the path p unless --allowPathP",
      rc[0] == (4.0, 'exact') and np.isnan(rc[1][0]) and rc[1][1] is None and rc[2] == (1.5, 'path') and rc[3] == (1.5, 'path')
      and bool(eRef) and bool(eBuilt), '{} | {}'.format(rc, eRef))
# the converged filter of the readers of the cost calibration
fl = lambda f_, rows_: pd.DataFrame(rows_).to_csv(os.path.join(tmpG, f_), index = False)
cal = lambda p_, ok, **kw: {'spec': 'size', 'phi': 0.5, 'commonX': True, 'p': p_, 'converged': ok, 'β': .6, 'ω': 1.2,
                            'τ0': .1, 'Vtilde': .3, 'θStar': c5Numbers.THETA_WORKBOOK} | kw
pir = lambda p_, ok, **kw: {'spec': 'sizePiR', 'phi': 0.5, 'commonX': True, 'p': p_, 'converged': ok, 'ΠR': .9} | kw
fl('escCalibration.csv', [cal(8., True), cal(99., False)])
fl('escCalibrationCosts.csv', [pir(7., True), pir(77., False)])
fl('escCalibrationCRRA.csv', [cal(4., True, ρ = r_, method = 'exact') for r_ in (0.5, 2.0)]
   + [cal(44., False, ρ = r_, method = 'exact') for r_ in (0.5, 2.0)])
fl('escCalibrationCRRACosts.csv', [pir(3., True, ρ = r_, method = 'exact') for r_ in (0.5, 2.0)]
   + [pir(33., False, ρ = r_, method = 'exact') for r_ in (0.5, 2.0)])
esc0, escH0 = c5Numbers.ESC, runHorizon.ESCDIR
c5Numbers.ESC = runHorizon.ESCDIR = tmpG
try:
    e5 = c5Numbers.escRows()
    lH = [float(runHorizon.escLambda(1.0, 'LOG')['p']), float(runHorizon.escLambda(2.0, 'exact')['p'])]
finally:
    c5Numbers.ESC, runHorizon.ESCDIR = esc0, escH0
check("G: c5Numbers.escRows and runHorizon.escLambda read converged calibration rows only",
      [e5[r_]['λ'] for r_ in (1.0, 0.5, 2.0)] == [8., 4., 4.] and [e5[r_]['λΠR'] for r_ in (1.0, 0.5, 2.0)] == [7., 3., 3.]
      and lH == [8., 4.], '{} {}'.format({k: v['λ'] for k, v in e5.items()}, lH))

# ==== X: the ξ drivers ========================================================================================
XIC = 0.544496
tagXi = {'thetaSource': 'C', 'θ0': XIC, 'grid': 'fine'}
eXi = []
for mod, name in ((runShocksXi, 'runXi'), (runESCxi, 'θStarAt')):
    for argv in ([], ['--theta', 'C'], ['--main']):
        eXi.append(until(mod, name, argv).get('exit', 'ran'))
check("X: runShocksXi and runESCxi need --theta and --main both (the rows are the paper's measure)",
      all('--theta' in x and 'PASSED' not in x for x in eXi), ' | '.join(eXi[:2]))
seen = []
fout = os.path.join(tmpG, 'xi.csv')
until(runShocksXi, 'runXi', ['--theta', mainV, '--main', '--xi', '0.2', '0.4', '0.3', '--out', fout],
      stub = lambda ξ, ww: (seen.append(ξ), (_ for _ in ()).throw(Stop()))[0])
check("X: runShocksXi runs the workbook ξ first, whatever the order of --xi", seen == [runShocksXi.XI0], str(seen))
pd.DataFrame([{'ξ': 0.2, 'x': 0., 'thetaSource': 'C', 'θ0': 0.5}, {'ξ': 0.4, 'x': 1., 'thetaSource': 'C', 'θ0': 0.5},
              {'ξ': 0.4, 'x': 2., 'thetaSource': 'C', 'θ0': XIC}, {'ξ': 0.25, 'x': 3., 'thetaSource': np.nan, 'θ0': np.nan}]
             ).to_csv(fout, index = False)
newXi = lambda ξ, ww: pd.DataFrame([{'ξ': ξ, 'x': 9., 'thetaSource': 'C', 'θ0': XIC}])
until(runShocksXi, 'runXi', ['--theta', mainV, '--main', '--xi', '0.2', '--out', fout], stub = newXi)
dXi = pd.read_csv(fout).sort_values('ξ')
check("X: runShocksXi replaces the rows of its ξ, keeps the others at the variant's θ0 and drops the rows at another θ0 "
      "or none", list(dXi['ξ']) == [0.2, 0.4] and list(dXi['x']) == [9., 2.] and set(dXi['θ0']) == {XIC},
      str(dict(zip(dXi['ξ'], dXi['x']))))
# runESCxi: the rows read and kept at the run's θ
saved2 = dict(runESC.THETA)
runESC.THETA.update({'variant': 'C', 'θ0': XIC, 'grid': 'fine'})
pubc = {'spec': 'size', 'phi': 0.5, 'commonX': True, 'converged': True}
cvals = dict(p = 6., θStar = .54, β = .65, ω = 1.2, X = 4., Vtilde = .3, fStar = .9, f0 = .7, choice = .54)
decoy = lambda r_: r_ | {'thetaSource': 'fixA', 'θ0': 0.5}
mine = lambda r_: r_ | tagXi
fl('pubCal.csv', [decoy(pubc | {k: v + 1 for k, v in cvals.items()}), mine(pubc | cvals)])
fl('pubPath.csv', [decoy({'spec': 'size', 'phi': 0.5, 'commonX': True, 'pos': k, 'date': 1960 + 30*k, 'θ': .1, 'τ': .1})
                   for k in (2, 3, 4, 5)] + [mine({'spec': 'size', 'phi': 0.5, 'commonX': True, 'pos': k,
                                                   'date': 1960 + 30*k, 'θ': .5, 'τ': .2}) for k in (2, 3, 4, 5)])
expr = lambda pin, th: {'ρ': 1.0, 'preferences': 'LOG', 'spec': 'size', 'phi': 0.5, 'commonX': True, 'scenario': 'acute',
                        'θpinned': pin, 'θ_t0': th, 'τ_t0': .3}
fl('pubExp.csv', [decoy(expr(p_, 0.)) for p_ in (True, False)] + [mine(expr(p_, .5)) for p_ in (True, False)])
xiRow = lambda kind, pos, **kw: {'xi': runESCxi.XI0, 'spec': 'size', 'phi': 0.5, 'commonX': True, 'kind': kind, 'pos': pos,
                                 'date': 1960 + 30*pos, 'p': 6.} | kw
xiRows = ([xiRow('calibration', 2, **(cvals | {'converged': True}))]
          + [xiRow('path', k, θ = .5, τ = .2) for k in (2, 3, 4, 5)]
          + [xiRow('acute ' + w, 2, θ = .5, τ = .3) for w in ('pinned', 'chosen')])
fx = os.path.join(tmpG, 'xiRob.csv')
pd.DataFrame([decoy(xiRow('calibration', 2, **{k: v + 5 for k, v in cvals.items()}))] + [mine(r_) for r_ in xiRows]
             ).to_csv(fx, index = False)
pub0 = dict(runESCxi.PUBLISHED)
runESCxi.PUBLISHED.update({'calib': os.path.join(tmpG, 'pubCal.csv'), 'path': os.path.join(tmpG, 'pubPath.csv'),
                           'experiments': os.path.join(tmpG, 'pubExp.csv')})
try:
    okSelf = runESCxi.selfCheck(fx, True)
    ids = runESCxi._ids(0.2, True, 'path', 2, 1990, 6.)
    runESCxi.write(fx, [mine(xiRow('acute chosen', 2, θ = .6, τ = .4))])
    dW = pd.read_csv(fx)
finally:
    runESCxi.PUBLISHED.update(pub0)
    runESC.THETA.update(saved2)
check("X: runESCxi's self-check reads the published and its own rows at the run's θ only (a decoy row of another θ0 first "
      "in each file), the rows it writes carry thetaSource, θ0, grid and the rows at another θ0 are dropped on a write",
      okSelf and set(dW['thetaSource']) == {'C'} and set(dW['θ0']) == {XIC} and len(dW) == len(xiRows)
      and runESC.THETA == saved and ids['thetaSource'] == 'C' and ids['θ0'] == XIC and ids['grid'] == 'fine',
      '{} rows'.format(len(dW)))

# runTauTheta: the self-check raises when it cannot compare or the gap is above its tolerance
sys.path.insert(0, os.path.join(runTauTheta.R.REPO, 'python', 'paper'))
import config as PC
fshk = os.path.join(runTauTheta.R.REPO, 'results', 'shocks', 'US_shocksCommonX.csv')
shk = PC.atTheta(pd.read_csv(fshk)) if os.path.exists(fshk) else pd.DataFrame()
refT = shk[np.isclose(shk['ρ'], 1.0) & (shk['effect'] == 'full') & (shk['scenario'] == r'$\theta = 0$')] if len(shk) else shk
eNaN = raises(lambda: runTauTheta.selfCheck(pd.DataFrame({'spec': [], 'θpin': [], 'τ': []}), tmpG, True), RuntimeError)
if len(refT):
    τ0T = float(refT['τ'].iloc[0])
    gOK = runTauTheta.selfCheck(pd.DataFrame([{'spec': 'none', 'θpin': 0., 'τ': τ0T}]), tmpG, True)
    eBad = raises(lambda: runTauTheta.selfCheck(pd.DataFrame([{'spec': 'none', 'θpin': 0., 'τ': τ0T + 1e-3}]), tmpG, True),
                  RuntimeError)
    check("G: runTauTheta.selfCheck raises when nothing could be compared (NaN) or the gap in τ is above 1e-6, and "
          "returns a gap of 0 against the published row", bool(eNaN) and 'NaN' in str(eNaN) and bool(eBad) and gOK == 0.,
          '{} | {}'.format(eNaN, eBad))
else:
    print("NOTE  the runTauTheta self-check against results/shocks/ skipped: no row at config.US['theta']")

# ==== T: --theta is required for results/ ====================================================================
tmpT = os.path.join(tmp, 'T')
os.makedirs(tmpT)
oT = lambda *x: os.path.join(tmpT, *x)
ns_ = lambda **kw: argparse.Namespace(**({'theta': None, 'root': None, 'main': False} | kw))
tCRG = [until(CRG, 'readDone', []), until(CRG, 'readDone', ['--theta', 'index']),
        until(CRG, 'readDone', ['--out', oT('us.csv'), '--pkldir', oT('pu')]), until(CRG, 'readDone', ['--out', oT('us.csv')])]
tCEU = [until(CEU, 'readDone', ['--rhos', '0.5', '1', '2']), until(CEU, 'readDone', ['--rhos', '0.5', '1', '2', '--theta', 'index']),
        until(CEU, 'readDone', ['--rhos', '0.5', '1', '2', '--out', oT('fr.csv'), '--pkldir', oT('pf')])]
tRS = [until(RS, 'hostRow', []), until(RS, 'hostRow', ['--theta', 'index']), until(RS, 'hostRow', ['--out', oT('s.csv')])]
tRE = [until(runESC, 'setTheta', []), until(runESC, 'setTheta', ['--theta', 'index'])]
tTT = [until(runESC, 'setTheta', [], run = runTauTheta), until(runESC, 'setTheta', ['--theta', 'index'], run = runTauTheta)]
tSA = [until(stationaryApproxESC, 'runLOG', ['--rho', '1']),
       until(stationaryApproxESC, 'runLOG', ['--rho', '1', '--theta', 'index']),
       until(stationaryApproxESC, 'runLOG', ['--rho', '1', '--out', oT('sa.csv')])]
eRC = raises(lambda: runESCcrra.setThetaCRRA(ns_()), SystemExit)
nI = ns_(theta = 'index')
okRC = runESCcrra.setThetaCRRA(nI) == runESCcrra.OUTDIR and nI.theta is None
refused = lambda g: 'without --theta' in g.get('exit', '') and 'args' not in g
ran = lambda g: 'args' in g and 'exit' not in g
check("T: without --theta every U.S. driver that writes results/ refuses it (calibrateRhoGrid{,EU} also for the default "
      "--pkldir), --theta index runs there at the workbook's θ, an --out (and --pkldir) outside results/ runs without it",
      all(refused(g) for g in (tCRG[0], tCRG[3], tCEU[0], tRS[0], tRE[0], tTT[0], tSA[0])) and bool(eRC)
      and all(ran(g) for g in (tCRG[1], tCRG[2], tCEU[1], tCEU[2], tRS[1], tRS[2], tRE[1], tTT[1], tSA[1], tSA[2]))
      and tRE[1]['args'][0] is None and tTT[1]['args'][0] is None and okRC and runESC.THETA == saved,
      ' | '.join(str(g.get('exit'))[:90] for g in (tCRG[0], tRE[0])))
tMix = [until(CRG, 'resumeAt', ['--theta', 'index', '--commonX']),
        until(CRG, 'resumeAt', ['--country', 'FR', '--rhos', '0.5', '1', '2', '--theta', 'index', '--commonX'], run = CEU)]
check("T: --theta index does not resume a sweep csv holding a variant's rows (the published US and FR sweeps, at C)",
      all('not the index θ' in g.get('exit', '') and 'args' not in g for g in tMix), tMix[0].get('exit', '')[-90:])
iT = [oecd26.indexTheta('index', [oecd26.RESULTS], 'x'), oecd26.indexTheta('C', [oecd26.RESULTS], 'x'),
      oecd26.indexTheta(None, [tmpT, None], 'x'), raises(lambda: oecd26.indexTheta(None, [oT('a'), CRG.OUTDIR], 'x'), SystemExit)]
check("T: oecd26.indexTheta maps 'index' to None, keeps a variant, passes None outside results/ and refuses it inside",
      iT[:3] == [None, 'C', None] and bool(iT[3]), str(iT[3]))

# ==== Z: the sweeps resume at their settings ==================================================================
gsC = oecd26.paperConfig().US['gridSettings']
wantUS = {'n': gsC['n'], 'ns': gsC['ns'], 'smoothKnots': gsC['smoothKnots'], 'interpKind': gsC['interpKind']}
row_ = lambda ρ, pref, **kw: {'ρ': ρ, 'preferences': pref, 'residual': 1e-12, 'n': 101, 'ns': 150 if pref == 'CRRA' else 50,
                              'smoothKnots': 4, 'interpKind': 'linear', 'x0': 0.} | kw
dZ = pd.DataFrame([row_(0.5, 'CRRA'), row_(1.0, 'LOG'), row_(2.0, 'CRRA', ns = 100), row_(1.5, 'CRRA', n = np.nan),
                   row_(0.6, 'CRRA', smoothKnots = np.nan), row_(0.7, 'CRRA', interpKind = 'cubic'),
                   row_(0.8, 'CRRA', residual = np.nan, n = 51), row_(3.0, 'CRRA', n = 51)])
gridZ = [0.5, 0.6, 0.7, 0.8, 1.0, 1.5, 2.0]
stZ, oldZ = CRG.staleSettings(dZ, wantUS, gridZ)
doneZ = {0.5: 1, 0.6: 1, 0.7: 1, 1.0: 1, 1.5: 1, 2.0: 1}
CRG.resumeAt(doneZ, dZ, wantUS, gridZ)
wantEU = wantUS | {'retAge': 'nra', 'βUS': lambda ρ: 0.65 + ρ}
dZE = pd.DataFrame([row_(0.5, 'CRRA', retAge = 'nra', βUS = 1.15), row_(1.0, 'LOG', retAge = np.nan, βUS = np.nan),
                    row_(2.0, 'CRRA', retAge = 'exit', βUS = 2.65), row_(1.5, 'CRRA', retAge = 'nra', βUS = 2.15 + 1e-9)])
stZE, oldZE = CRG.staleSettings(dZE, wantEU, [0.5, 1.0, 1.5, 2.0], ('retAge', 'βUS'))
check("Z: staleSettings: another ns on a CRRA row (not on a LOG one), smoothKnots (NaN is the adaptive None), interpKind, "
      "retAge or βUS is stale; a row without the grid or without retAge/βUS predates them; failed rows and rhos off the "
      "grid are not read; resumeAt drops the stale rows from the resume cache",
      stZ == {2.0: ['ns'], 0.6: ['smoothKnots'], 0.7: ['interpKind']} and oldZ == [1.5] and sorted(doneZ) == [0.5, 1.0, 1.5]
      and stZE == {2.0: ['retAge'], 1.5: ['βUS']} and oldZE == [1.0], '{} {} | {} {}'.format(stZ, oldZ, stZE, oldZE))
pubZ, pubOld = {}, {}
for cx in (False, True):
    refZ = testEU.usReference(commonX = cx)
    for c in ('US', 'FR', 'UK'):
        f = os.path.join(CRG.OUTDIR, c + '_rhoGrid' + ('CommonX' if cx else '') + '.csv')
        w = wantUS if c == 'US' else wantUS | {'retAge': testEU.retAgeHost(c), 'βUS': lambda ρ, r = refZ: float(r(ρ)['β'])}
        st, od = CRG.staleSettings(pd.read_csv(f), w, oecd26.paperConfig().US['ρGrid'], () if c == 'US' else CEU.INPUTCOLUMNS)
        pubZ[os.path.basename(f)], pubOld[os.path.basename(f)] = st, len(od)
check("Z: the published sweeps of results/calibration/ (US, FR, UK, both variants) resume whole at config.US's grid "
      "settings: no stale row; France's and the UK's rows predate retAge/βUS and are resumed unchecked",
      all(v == {} for v in pubZ.values()) and all(pubOld[k] == (0 if k.startswith('US') else 3) for k in pubOld),
      str(pubOld))


def sweep(mod, csv, *extra):
    """ mod.main() at ρ = 1 (LOG), n = 51, no verify, the workbook's θ, into `csv` and its pickle directory. """
    old = sys.argv
    sys.argv = ['x.py', '--rhos', '1', '--n', '51', '--verify', '0', '--theta', 'index', '--out', csv,
                '--pkldir', csv + '.pkl'] + list(extra)
    try:
        return mod.main()
    finally:
        sys.argv = old


fUS, fFR = oT('US_z.csv'), oT('FR_z.csv')
rcZ = [sweep(CRG, fUS)]
z1 = pd.read_csv(fUS)
z1.assign(n = 101).to_csv(fUS, index = False)
rcZ.append(sweep(CRG, fUS))
z2 = pd.read_csv(fUS)
rcZ.append(sweep(CRG, fUS))
z3 = pd.read_csv(fUS)
check("Z: calibrateRhoGrid end to end: a row recorded at another n is re-solved at the run's, a row at the run's is "
      "resumed (timestamp kept)", rcZ == [0, 0, 0] and list(z2['n']) == [51] and z2['timestamp'].iloc[0] == z3['timestamp'].iloc[0]
      and z2['β'].iloc[0] == z1['β'].iloc[0], 'β {!r}'.format(z1['β'].iloc[0]))
rcE = [sweep(CEU, fFR, '--country', 'FR')]
e1 = pd.read_csv(fFR)
βref = float(testEU.usReference(commonX = False)(1.0)['β'])
e1.assign(retAge = 'exit', timestamp = 'x').to_csv(fFR, index = False)
rcE.append(sweep(CEU, fFR, '--country', 'FR'))
e2 = pd.read_csv(fFR)
e2.assign(retAge = np.nan, βUS = np.nan).to_csv(fFR, index = False)
rcE.append(sweep(CEU, fFR, '--country', 'FR'))
e3 = pd.read_csv(fFR)
check("Z: calibrateRhoGridEU end to end: a new row records retAge (testEU.retAgeHost) and βUS (the U.S. reference β, = its "
      "β); a row at another retAge is re-solved; a row without retAge/βUS is resumed unchecked",
      rcE == [0, 0, 0] and e1['retAge'].iloc[0] == testEU.retAgeHost('FR') and e1['βUS'].iloc[0] == βref == e1['β'].iloc[0]
      and e2['retAge'].iloc[0] == testEU.retAgeHost('FR') and e2['timestamp'].iloc[0] != 'x'
      and pd.isna(e3['retAge'].iloc[0]) and e3['timestamp'].iloc[0] == e2['timestamp'].iloc[0],
      'βUS {!r}, retAge {}'.format(e1['βUS'].iloc[0], e1['retAge'].iloc[0]))

shutil.rmtree(tmp, ignore_errors = True)
print('\n({:.0f}s)'.format(time.time() - tic))
report()
