r""" Unexpected universalisation of the pension system at the calibration date t0, run at each rho that
has a calibrated solution. Not a test -- an experiment script.

Run:  .venv\Scripts\python.exe python\InformalSavings\shockUniversal.py --rho 1.0
A bare invocation is the headline experiment: rule='match' against refType=1, every rho in the csv that
has a pickled instance. The other readings are reached through --rule/--refType/--scale.

The experiment (docs §9's model-copy mechanism, README "Model copies for shock experiments"):

  1. Solve the baseline PEE over the full horizon at the calibrated parameters, with db's own eps.
  2. Read the state (s_{t0-1}, iota_{t0-1}) entering t0 off that solved path (stateAtT0).
  3. Build the model copy whose horizon starts at t0 (createCopyFromt0). The copy's agents solve their
     whole problem knowing only the reformed system, which is what makes the reform UNEXPECTED: the
     baseline path that produced the seed state was solved under the old eps and is not revised.
  4. Replace eps on the copy by the universal value and re-solve the PEE from the seed state.

UNIVERSAL has two readings, both supported (--rule; see universalEps). Both are read off
eq:governmentBudget, where the level bbar_t and the aggregate h_{t-1} are common to b^0 and b^i and so
cancel -- which is what makes either reform a pure parameter change with no equilibrium object in it:

    b_t^0 = eps_t h_{t-1} bbar_t,   b_t^i = [theta_t h_{t-1,i} eta_{t-1,i} + (1-theta_t) h_{t-1}] bbar_t

  'match'  b_t^0 = b_t^{j}:  eps_t = theta_t hetaRatio_{t-1,j} + (1-theta_t)      (--refType j, default 1)
  'flat'   the non-contributive component only:  eps_t = 1 - theta_t

theta is NOT touched under either: universality is about who is covered (eps), not about how contributive
the formal benefit is (theta). The two readings BRACKET the reform rather than differing in degree, and
on the Argentina calibration they fall on opposite sides of the status quo (eps = 0.337): 'match' raises
it to 0.546 (+62%), 'flat' cuts it to 0.161 (-52%), and every response flips sign accordingly. The
calibrated eps is 0.7 (a coverage rate) times the relative benefit of type j=2 times an early-retirement
discount (see model.getEps), which is why 'match' against j=1 is a rise despite equalising to the LOWEST
formal type. --refType and --scale run the intermediate readings; neither changes the mechanism.

TWO THINGS THE COPY NEEDS BEYOND A NEW eps ARRAY, both from README "Known limitations":
  - eps must be written into db, not only passed to solvePEE_*. kappa_t(eps_{t+1}) is consumed everywhere
    through a CACHED db['kappa'] rather than through the explicit kappa(eps1, t), so a call that passed a
    new eps while leaving db alone would solve the reform's household problem against the baseline's
    government budget. installEps writes both, in that order.
  - db['kappa[t-1]'] at the copy's first period must be rebuilt from the NEW eps_{t0}. _sliceDb restricts
    rather than recomputes, so the copy inherits the baseline's genuine kappa_{t0-1} there -- correct
    under no shock, stale under this one, since bbar_{t0} = nu w h tau/(h_{t0-1} kappa_{t0-1}) is what
    pays the reformed benefit to the generation already old at t0. (On the current calibration p/gamma0
    are constant and eps^U is flat, so this value coincides with what addLeadAndLags' boundary clamp
    would give; it stops coinciding the moment either varies over t.)

--control re-solves the copy with eps UNCHANGED and checks it reproduces the baseline's own tail. That is
test_createCopyFromt0.py's round trip, run here as a precondition rather than as a test: it validates the
seed state, the slicing and the re-solve on THIS rho's instance before any reform number is read off.
"""
import os, sys, argparse, pickle, time
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
os.chdir(HERE)                                  # test.py resolves data/ relative to the repo root

CSV    = os.path.join(REPO, 'results', 'calibration', 'informalSavings_rhoGrid.csv')
PKLDIR = os.path.join(REPO, 'results', 'calibration', 'instances')
OUTDIR = os.path.join(REPO, 'results', 'shocks')
# Series compared baseline vs reform. Aggregates and prices first, then the two type-0 consumption
# levels, which are what the reform is about.
SERIES = ('τ', 's', 'h', 'ι', 'R', 'w', 'bbar', 'b0', 'bi', 'c10', 'c20')


def relBenefit(m, refType = 1):
    """ b_t^{refType}/(h_{t-1} bbar_t) = theta_t hetaRatio_{t-1,refType} + (1-theta_t), i.e. eq
    :governmentBudget's formal benefit stripped of the level it shares with b^0. Parameters only. """
    θ = m.db['θ'].values
    col = list(m.db['i']).index(refType)        # db['i'] is labelled 1..J; hηRatio is positional
    return θ*np.asarray(m.BT.hηRatio(lag = '[t-1]'))[:, col] + (1-θ)


def universalEps(m, rule = 'match', refType = 1, scale = 1.0):
    """ eps^U_t over m's whole horizon, under one of the two readings of "universal". Both are parameter
    expressions (theta, eta, X, xi): bbar_t and h_{t-1} are common to b^0 and b^i and cancel, so neither
    reading needs a solved equilibrium.

    'match': b_t^0 = b_t^{refType} -- type 0 receives the WHOLE benefit of a formal type, contributive
        component included, as if it had that type's earnings history.
    'flat':  eps_t = 1 - theta_t -- type 0 receives only the NON-CONTRIBUTIVE component, the part of
        eq:governmentBudget that is proportional to aggregate h_{t-1} and independent of any own earnings
        history. This is universal coverage of the flat pillar rather than of the whole system, and on the
        Argentina calibration it is a benefit CUT for type 0, not a rise: theta=0.839 puts eps at 0.161
        against the calibrated 0.337. The two readings therefore bracket the reform rather than differing
        in degree, which is why the sign of every response flips between them. """
    if rule == 'match':
        return scale * relBenefit(m, refType)
    elif rule == 'flat':
        return scale * (1 - m.db['θ'].values)
    raise ValueError("rule must be 'match' or 'flat', got {!r}".format(rule))


def installEps(m, ε):
    """ Write an eps path into db and refresh everything derived from it. Order matters: aux_κ reads
    db['eps[t+1]'], so eps must land first. See the module docstring for why db['κ[t-1]'] at position 0
    is then overwritten rather than left to addLeadAndLags' boundary clamp. """
    m.db.update(m.adjPar('eps', np.asarray(ε, dtype = float)))
    ll = m.addLeadAndLags('κ', m.aux_κ)
    p_, γ0_, p0_ = (float(m.db[k].iloc[0]) for k in ('p[t-1]', 'γ0[t-1]', 'p0[t-1]'))
    γ0 = float(m.db['γ0'].iloc[0])
    ll['κ[t-1]'].iloc[0] = (p_ + float(m.db['eps'].iloc[0])*γ0_*p0_) * (1+γ0_)/(1+γ0)
    m.db.update(ll)


def solvePEE(m, preferences, **kwargs):
    return (m.solvePEE_LOG(**kwargs) if preferences == 'LOG' else m.solvePEE_CRRA(**kwargs))


def loadCalibrated(ρ, settings, commonSettings = False, pkldir = None):
    """ The pickled instance at its own converged parameters, with the grid settings installed on the
    solver that rho selects. The pickle is the calibrated solution -- nothing is recalibrated here.

    An instance MUST be re-solved on the settings it was calibrated at. calibrateRhoGrid.py gives both
    solvers interpKind/smoothKnots and only the grid SIZES to CRRA, so that split is mirrored here: LOG
    gets interpKind/smoothKnots and keeps its own nι=50. Solving a calibrated instance under a different
    interpolant than it was fitted under is precisely the defect this split exists to prevent -- it moved
    the rho=1 anchor off the curve its CRRA neighbours trace and put a +10.6%-of-scale spike in the
    t0+1 response (notes/informalSavings_resolvedIssues.md).

    commonSettings: give LOG the grid sizes too. Diagnostic only -- use it when comparing the two
    recursions with every setting held identical, not for a run whose instances were calibrated without it.

    pkldir: override the instance directory (a diagnostic sweep writes its own). """
    path = os.path.join(pkldir or PKLDIR, 'rho_{:.4f}.pkl'.format(ρ))
    with open(path, 'rb') as f:
        m = pickle.load(f)
    preferences = m._calPreferences()
    if preferences == 'CRRA' or commonSettings:
        getattr(m, preferences).initGS(settings)
    else:
        m.LOG.initGS({k: settings[k] for k in ('interpKind', 'smoothKnots') if k in settings})
    return m, preferences


def frame(report, refType = 1, names = SERIES, τ = None):
    """ Named series out of an EE_report (plus tau, which the report does not carry), aligned on the
    reporting index each one uses -- ι/Γs live on txE and are one period shorter (README, "Reporting
    domains"), so this must be a join rather than a column stack. Type-indexed entries (bi) are reduced
    to the reform's reference type, so the reported b^i is the one b^0 is being equalised to. """
    cols = {} if τ is None else {'τ': pd.Series(np.asarray(τ), index = report['s'].index)}
    for k in names:
        if k in report:
            v = report[k]
            cols[k] = v if isinstance(v, pd.Series) else v.loc[:, refType]
    return pd.DataFrame(cols)


def runShock(ρ, settings, rule, refType, scale, control, out, commonSettings = False, pkldir = None):
    print('\n' + '='*94)
    print('rho={}   universal pensions at t0: rule={} ({})   scale={}'.format(
        ρ, rule, 'b^0 = b^{}'.format(refType) if rule == 'match' else 'eps = 1-theta', scale))
    print('='*94)
    m, preferences = loadCalibrated(ρ, settings, commonSettings, pkldir)
    t0 = m.db['t'][m.db['t0']]
    print('{} solver, T={}, t0 = db index {} (calibration year), grid {}'.format(
        preferences, m.T, t0,
        settings if (preferences == 'CRRA' or commonSettings)
        else {k: settings[k] for k in ('interpKind', 'smoothKnots') if k in settings}))

    tStart = time.time()
    base = solvePEE(m, preferences)
    seed = m.stateAtT0(base['report'], t0, init = base['init'])
    print('baseline solved ({:.0f}s).  state entering t0:  s={:.6f}  ι={:.6f}'.format(
        time.time()-tStart, seed['s0'], seed['ι0']))

    if control:
        mc, _ = loadCalibrated(ρ, settings, commonSettings, pkldir)
        mc = mc.createCopyFromt0(t0)
        ctrl = solvePEE(mc, preferences, **seed)
        dev = {k: float(np.max(np.abs(np.asarray(ctrl['report'][k])
                                      - np.asarray(base['report'][k].loc[t0:]))))
               for k in ('s', 'h', 'ι')}
        print('control (copy, eps unchanged) reproduces the baseline tail:  ' +
              '  '.join('max|Δ{}|={:.2e}'.format(k, v) for k, v in dev.items()))

    mt0 = m.createCopyFromt0(t0)
    εOld = float(m.db['eps'].iloc[0])
    εU = universalEps(mt0, rule = rule, refType = refType, scale = scale)
    installEps(mt0, εU)
    print('eps: {:.6f} -> {:.6f} ({:+.1f}%)   kappa: {:.6f} -> {:.6f}'.format(
        εOld, εU[0], 100*(εU[0]/εOld-1), float(m.db['κ'].iloc[0]), float(mt0.db['κ'].iloc[0])))

    tStart = time.time()
    shock = solvePEE(mt0, preferences, **seed)
    # The reform's defining identity, read off the SOLVED path via the model's own bi/b0 rather than off
    # the formula that produced eps^U: b^0/b^{ref} must equal the ratio the installed eps implies. Under
    # 'match' that target is exactly 1; under 'flat' it is (1-theta)/relBenefit. This is what catches a
    # refType read against the wrong column (db['i'] is labelled 1..J while hηRatio is positional), and
    # it fails just as loudly if installEps left db['kappa'] or db['eps[t+1]'] out of step.
    target = εU/relBenefit(mt0, refType)
    ratio = np.asarray(shock['report']['b0'])/np.asarray(shock['report']['bi'].loc[:, refType])
    print('reform solved ({:.0f}s).  b^0/b^{} on the reformed path = {:.6f}, target {:.6f} '
          '(max|dev| {:.2e})'.format(time.time()-tStart, refType, ratio[0], target[0],
                                     np.max(np.abs(ratio-target))))

    # Both frames are on the copy's 0-based index; shift the reform's back onto the baseline's calendar.
    b = frame(base['report'], refType, τ = base['τ']).loc[t0:]
    r = frame(shock['report'], refType, τ = shock['τ']).set_index(b.index[:len(shock['report']['s'])])
    df = b.join(r, lsuffix = '_base', rsuffix = '_reform')
    for k in SERIES:
        if k+'_base' in df:
            df['d_'+k] = df[k+'_reform']/df[k+'_base'] - 1
    df.insert(0, 'ρ', ρ)
    df.index.name = 't'

    show = ['τ_base', 'τ_reform', 'd_τ', 'd_s', 'd_h', 'd_ι', 'd_c10', 'd_c20']
    print('\nrelative change (reform/baseline - 1), tau in levels:')
    print(df[[c for c in show if c in df]].to_string(float_format = lambda v: '{:9.5f}'.format(v)))

    if out:
        os.makedirs(OUTDIR, exist_ok = True)
        path = os.path.join(OUTDIR, out.format(ρ = ρ, rule = rule))
        df.to_csv(path)
        print('\nwritten: ' + os.path.relpath(path, REPO))
    return df


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--rho', type = float, nargs = '+', default = None,
                   help = 'default: every rho in --csv that has a pickled instance')
    p.add_argument('--csv', default = CSV)
    p.add_argument('--rule', default = 'match', choices = ('match', 'flat'),
                   help = "'match' (default): b^0 = b^refType, the whole benefit.  'flat': eps = "
                          "1-theta, the non-contributive component only -- see universalEps")
    p.add_argument('--refType', type = int, default = 1,
                   help = "formal type j that b^0 matches under 'match', and the denominator of the "
                          "reported b^0/b^j under either rule")
    p.add_argument('--scale', type = float, default = 1.0, help = 'multiplier on eps^U (1 = exact equality)')
    p.add_argument('--control', action = 'store_true', help = 'also run the no-shock round trip first')
    p.add_argument('--nι', '--niota', dest = 'nι', type = int, default = 45)
    p.add_argument('--ns', type = int, default = 45)
    p.add_argument('--interpKind', default = 'cubic', choices = ('linear', 'cubic', 'pchip'))
    p.add_argument('--smoothKnots', type = int, default = 4)
    p.add_argument('--commonSettings', action = 'store_true',
                   help = 'also give LOG the grid SIZES (--nι/--ns). Diagnostic only -- interpKind and '
                          'smoothKnots already go to both solvers, matching calibrateRhoGrid.py')
    p.add_argument('--pkldir', default = PKLDIR, help = 'directory of pickled calibrated instances')
    p.add_argument('--out', default = 'universal_{rule}_rho{ρ:.4f}.csv', help = "'' to skip writing")
    a = p.parse_args()
    settings = {'nι': a.nι, 'ns': a.ns, 'interpKind': a.interpKind, 'smoothKnots': a.smoothKnots}
    ρs = a.rho
    if ρs is None:
        df = pd.read_csv(a.csv)
        ρs = [float(v) for v in df['ρ']
              if os.path.exists(os.path.join(a.pkldir, 'rho_{:.4f}.pkl'.format(float(v))))]
    for ρ in ρs:
        runShock(ρ, settings, a.rule, a.refType, a.scale, a.control, a.out, a.commonSettings, a.pkldir)
