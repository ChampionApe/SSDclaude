r""" Is the LOG/CRRA solver boundary at rho=1 a discontinuity in the model, or in the method?

Run:  .venv\Scripts\python.exe python\InformalSavings\diagnoseLogCrraBoundary.py --test limit
      ... --test limit    the rho->1 limit of the CRRA solve against LOG, at FIXED parameters
      ... --test refine   whether that gap is grid error (shrinks with n) or a method gap (plateaus)
      ... --test cal      smoothness of the calibrated parameters across a fine grid straddling rho=1
      ... --test path     smoothness of the solved PEE path across the same grid
      ... --test shock    smoothness of the universalisation response across the same grid

Motivation: plotUniversalShock.py --period 1 shows Delta-tau dipping at exactly rho=1.0->1.1 (6.09% ->
5.72%) with both flanking segments smooth. rho=1 is the module's ONLY LOG point (model._calPreferences
returns 'LOG' iff rho==1 exactly); every other point is CRRA. A feature sitting exactly on that boundary
is a solver-transition artifact until shown otherwise -- README, "Results: the universalisation shock".

RESOLVED 2026-08-20 -- this script is kept as the measurement that found it, and as the control that
would catch a recurrence. calibrateRhoGrid.py now gives interpKind to BOTH solvers; before that it keyed
it on 'CRRA', so the LOG anchor ran on its class default 'linear' and crossing rho=1 changed the method
AND the grid AND the interpolant at once. Any test that does not hold the last two fixed measures their
sum and attributes it to the first. Hence --mode:

    common      both solvers on identical settings (default). Isolates the METHOD.
    production  LOG on its own class defaults, nι=50 and interpKind='linear' -- the PRE-FIX
                configuration. No longer what the sweep does; retained because it is what reproduces the
                artifact, and a mode that can only ever return "fine" is not a control.

The difference between the two modes was the part of the boundary jump that was a settings choice rather
than a property of the two recursions. It was ~98% of it.

WHAT A CLEAN RESULT LOOKS LIKE. CRRA at rho=1±δ and LOG at rho=1 solve the same economics in the limit
δ->0 (the CRRA class refuses rho=1 outright -- every term of eq:PEEcrraTerms carries a (·)^{1-1/ρ} and
hatc1's exponent 1/(1-1/ρ) diverges -- so the limit is a test, not a fallback; policy.CRRA's own class
docstring says so). So gap(δ) = |x_CRRA(1±δ) - x_LOG(1)| should go to ZERO with δ, linearly, from both
sides. Three failure shapes, distinguishable only by running the ladder:

    gap -> 0          continuous. Any dip at the boundary is elsewhere (calibration, or the shock).
    gap -> C > 0      a genuine method gap of size C. C is the size of the artifact, and the thing to
                      report it against is the tau-grid spacing, per this repo's convention.
    gap grows as δ->0 the CRRA discretization degrades approaching its own singular parameterization.
                      This would put the LEAST accurate CRRA points immediately beside the exact LOG
                      one, which is the shape that produces a dip at the boundary and nowhere else.

A note on one mechanism that is NOT the explanation, checked before writing this so it is not re-derived:
in B = β^ρ(R/p)^{ρ-1} the entire R-dependence carries a factor (ρ-1), which cancels exactly against the
1/(1-1/ρ) in lnhatc1i = log1p(B)/(1-1/ρ) + log(tildec1i). So neither float64 cancellation nor the
continuation interpolants' error is amplified as rho->1; both stay O(1). The large ADDITIVE offset
log1p(β_i)/(1-1/ρ) (~80 at rho=1.01) differences out of dln(ĉ)/dτ and costs ~1e-12 at these rho.
"""
import os, sys, argparse, pickle, time
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
os.chdir(HERE)

from model import ModelInformalSavings

CALDIR   = os.path.join(REPO, 'results', 'calibration')
FINECSV  = os.path.join(CALDIR, 'informalSavings_rhoFine.csv')
FINEPKL  = os.path.join(CALDIR, 'instancesFine')
BASEPKL  = os.path.join(CALDIR, 'instances')
OUTDIR   = os.path.join(REPO, 'results', 'boundary')

# The CRRA calibration's settings (README, "The CRRA calibration's two settings"). In --mode common these
# are imposed on LOG as well; nothing here is a per-solver choice.
CRRAGS = {'nι': 45, 'ns': 45, 'interpKind': 'cubic', 'smoothKnots': 4}
# The PRE-FIX LOG configuration: smoothKnots only, so nι=50 and 'linear' survive from
# policy.LOG._gridSettings. calibrateRhoGrid.py now also passes interpKind, so this is no longer what a
# sweep gives LOG -- it is the control that reproduces the artifact.
LOGGS  = {'smoothKnots': 4}


def settingsFor(preferences, mode):
    """ Grid settings for one solver under one mode. 'common' hands both solvers CRRAGS -- LOG ignores
    'ns' (it has no savings state) and uses nι/interpKind/smoothKnots exactly as CRRA does. """
    if mode == 'common':
        return dict(CRRAGS)
    return dict(CRRAGS) if preferences == 'CRRA' else dict(LOGGS)


def loadInstance(ρ, pkldir):
    with open(os.path.join(pkldir, 'rho_{:.4f}.pkl'.format(ρ)), 'rb') as f:
        return pickle.load(f)


def solveAt(m, ρ, mode, gsOverride = None):
    """ Install rho on m and solve the PEE with whichever solver rho selects, at m's CURRENT calibrated
    parameters. Returns (preferences, out, settings). db is left holding rho -- callers that care must
    reinstall their own.

    The parameters are deliberately not re-calibrated: this is the experiment that separates the solver
    from the calibration, so (β,ω,η0,X0) must be the same numbers on both sides of the boundary. """
    m.db.update(m.adjPar('ρ', float(ρ)))
    preferences = m._calPreferences()
    settings = settingsFor(preferences, mode) | (gsOverride or {})
    policy = getattr(m, preferences)
    policy.initGS(settings)
    out = getattr(m, f'solvePEE_{preferences}')()
    return preferences, out, settings


def summarise(m, out):
    """ The handful of scalars a boundary comparison is read on, plus the whole tau path for max-norms.
    t0 is the calibration year; t0+1 is where the shock's dip appears. iota reports on txE (README,
    "Reporting domains") so it is one period shorter than tau -- read positionally off db['t']. """
    t = list(m.db['t'])
    t0 = m.db['t'][m.db['t0']]
    rep, τ = out['report'], out['τ']
    d = {'τ': np.asarray(τ, dtype = float),
         'τ_t0': float(τ.xs(t0)), 'τ_t0p1': float(τ.xs(t[t.index(t0)+1])),
         's_t0': float(rep['s'].xs(t0)), 'h_t0': float(rep['h'].xs(t0)),
         'ι_t0': float(rep['ι'].xs(t0))}
    return d


# ----------------------------------------------------------------------------------------------------
def testLimit(args):
    """ Test 1. The rho->1 limit at FIXED parameters.

    Everything is held at the calibrated rho=1 instance's own (β,ω,η0,X0). Only rho moves, and with it
    the solver. Under a continuous method the CRRA answer converges to the LOG one from both sides. """
    m = loadInstance(1.0, args.pkldir)
    x0 = m._calToX(m.calibrationPars)
    print('parameters held fixed at the rho=1 calibration: ' +
          '  '.join('{}={:.6f}'.format(k, v) for k, v in m.calibrationPars.items()))
    print('mode={}  (LOG settings {}, CRRA settings {})\n'.format(
        args.mode, settingsFor('LOG', args.mode), settingsFor('CRRA', args.mode)))

    tStart = time.time()
    prefL, outL, gsL = solveAt(m, 1.0, args.mode)
    base = summarise(m, outL)
    τGrid = m.LOG.GS['PEE']['solGrids']['τ']
    spacing = float(np.diff(τGrid).mean())
    print('LOG at rho=1 ({:.0f}s):  τ(t0)={:.8f}  τ(t0+1)={:.8f}  ι(t0)={:.8f}  s(t0)={:.8f}'.format(
        time.time()-tStart, base['τ_t0'], base['τ_t0p1'], base['ι_t0'], base['s_t0']))
    print('τ-grid spacing = {:.3e}  (the unit any gap should be read in)\n'.format(spacing))

    rows = []
    for δ in args.deltas:
        for sgn in (-1, +1):
            ρ = 1 + sgn*δ
            # _calSetPars is re-applied every time: adjPar('ρ') alone does not touch (β,ω,η0,X0), but a
            # previous CRRA solve leaves db's warm-start caches and auxiliary parameters at its own point.
            m._calSetPars(m._calFromX(x0))
            t1 = time.time()
            try:
                pref, out, gs = solveAt(m, ρ, args.mode)
                s = summarise(m, out)
                rows.append({'ρ': ρ, 'δ': sgn*δ, 'pref': pref, 'ok': True, 'time': time.time()-t1,
                             'dτ_t0': s['τ_t0']-base['τ_t0'], 'dτ_t0p1': s['τ_t0p1']-base['τ_t0p1'],
                             'dι_t0': s['ι_t0']-base['ι_t0'], 'ds_t0': s['s_t0']-base['s_t0'],
                             'maxdτ': float(np.max(np.abs(s['τ']-base['τ'])))})
                print('  rho={:<7.4f} {:<5} {:>5.0f}s  Δτ(t0)={:+.3e}  Δτ(t0+1)={:+.3e}  '
                      'Δι(t0)={:+.3e}  Δs(t0)={:+.3e}  max|Δτ|={:.3e}'.format(
                          ρ, pref, rows[-1]['time'], rows[-1]['dτ_t0'], rows[-1]['dτ_t0p1'],
                          rows[-1]['dι_t0'], rows[-1]['ds_t0'], rows[-1]['maxdτ']))
            except Exception as e:
                rows.append({'ρ': ρ, 'δ': sgn*δ, 'pref': 'FAIL', 'ok': False,
                             'time': time.time()-t1, 'error': '{}: {}'.format(type(e).__name__, e)[:160]})
                print('  rho={:<7.4f} FAILED  {}'.format(ρ, rows[-1]['error']))

    df = pd.DataFrame(rows).sort_values('δ')
    _write(df, 'limit_{}.csv'.format(args.mode))

    _limitReading(df, spacing)
    return df


def _limitReading(df, spacing):
    """ The discriminating statistic, and why the raw gap is not it.

    x_CRRA(1±δ) - x_LOG(1) is dominated by the TRUE economic slope dx/dρ, which is nonzero: it comes out
    linear in δ and antisymmetric in its sign, and says nothing about the solvers. The central average

        D(δ) = ½[x(1+δ) + x(1-δ)] - x_LOG(1)

    cancels that linear term. What is left is ½x''δ² + C, where C is any jump between the CRRA limit at
    rho->1 and the LOG value AT rho=1 -- i.e. exactly the boundary artifact. So:

        D(δ) -> 0 like δ² (successive ratios ~4 when δ halves)   =>  continuous; C is zero.
        D(δ) -> C ≠ 0     (successive ratios ~1)                 =>  a method gap of size C.

    Reported against the τ-grid spacing, since a jump well under one cell cannot be what moves a located
    policy. Richardson-extrapolating the two smallest δ under the δ² model gives the cleanest estimate of
    C: C ≈ [4D(δ/2) - D(δ)]/3. """
    ok = df[df['ok']]
    cols = [('dτ_t0', 'τ(t0)'), ('dτ_t0p1', 'τ(t0+1)'), ('dι_t0', 'ι(t0)'), ('ds_t0', 's(t0)')]
    δs = sorted({abs(v) for v in ok['δ']}, reverse = True)
    δs = [d for d in δs if ((ok['δ'] == d).any() and (ok['δ'] == -d).any())]
    if len(δs) < 2:
        print('\n(need both signs at >=2 δ for the central statistic)')
        return
    print('\ncentral average D(δ) = ½[x(1+δ)+x(1-δ)] - x_LOG(1)  -- the linear trend is cancelled, so a '
          'nonzero\nlimit as δ->0 IS the boundary jump.  ratios ~4 per halving => δ² => continuous.')
    for key, name in cols:
        D = [0.5*(float(ok.loc[ok['δ'] == d, key].iloc[0]) + float(ok.loc[ok['δ'] == -d, key].iloc[0]))
             for d in δs]
        print('  {:<9} '.format(name) + '  '.join('δ={:g}:{:+.2e}'.format(d, v) for d, v in zip(δs, D)))
        ratios = [D[i]/D[i+1] if D[i+1] else np.nan for i in range(len(D)-1)]
        print('  {:<9} ratios: '.format('') + '  '.join('{:.2f}'.format(r) for r in ratios))
        C = (4*D[-1] - D[-2])/3
        print('  {:<9} Richardson C (δ²-model, two smallest δ) = {:+.3e}'.format('', C) +
              ('   = {:.4f} τ-grid cells'.format(abs(C)/spacing) if key.startswith('dτ') else ''))


# ----------------------------------------------------------------------------------------------------
def testRefine(args):
    """ Test 2. Is the limit gap grid error or a method gap?

    At a fixed small δ, refine the CRRA inner grid and re-measure the gap against the same LOG answer.
    Shrinking => grid-limited, and the fix is resolution. Flat => the two recursions genuinely disagree at
    this rho, and resolution will not close it. This is notes/crossCuttingFindings.md #3's diagnostic
    applied to a solver difference rather than to one solver's own convergence. """
    m = loadInstance(1.0, args.pkldir)
    x0 = m._calToX(m.calibrationPars)
    _, outL, _ = solveAt(m, 1.0, args.mode)
    base = summarise(m, outL)
    print('LOG at rho=1:  τ(t0)={:.8f}  τ(t0+1)={:.8f}\n'.format(base['τ_t0'], base['τ_t0p1']))

    rows = []
    for δ in args.deltas:
        for n in args.ns:
            ρ = 1 + δ
            m._calSetPars(m._calFromX(x0))
            t1 = time.time()
            try:
                pref, out, gs = solveAt(m, ρ, args.mode, gsOverride = {'nι': n, 'ns': n})
                s = summarise(m, out)
                rows.append({'ρ': ρ, 'δ': δ, 'n': n, 'ok': True, 'time': time.time()-t1,
                             'dτ_t0': s['τ_t0']-base['τ_t0'], 'dτ_t0p1': s['τ_t0p1']-base['τ_t0p1'],
                             'dι_t0': s['ι_t0']-base['ι_t0'],
                             'maxdτ': float(np.max(np.abs(s['τ']-base['τ'])))})
                print('  rho={:<7.4f} n={:<3} {:>5.0f}s  Δτ(t0)={:+.3e}  Δτ(t0+1)={:+.3e}  '
                      'max|Δτ|={:.3e}'.format(ρ, n, rows[-1]['time'], rows[-1]['dτ_t0'],
                                              rows[-1]['dτ_t0p1'], rows[-1]['maxdτ']))
            except Exception as e:
                print('  rho={:<7.4f} n={:<3} FAILED  {}'.format(ρ, n, str(e)[:120]))
    df = pd.DataFrame(rows)
    _write(df, 'refine_{}.csv'.format(args.mode))
    return df


# ----------------------------------------------------------------------------------------------------
def _smoothness(df, xcol, cols, anchor = 1.0):
    """ Does the anchor row lie on the curve the other rows trace?

    For each column: fit a polynomial through every point EXCEPT the anchor, evaluate at the anchor, and
    report the anchor's deviation from it. The anchor is the one LOG point, so this asks whether the LOG
    answer is where the CRRA points say it should be -- which is the whole question, and it cannot be
    asked by looking at differences alone (a smooth series and a series with one displaced point have
    similar first differences; they differ in whether the displaced point is predictable from the rest).

    Degree is len(others)-1 capped at 3: with four flanking points a cubic interpolates them exactly, so
    the reported deviation is the honest extrapolation error of the CRRA series onto its own gap. """
    x = df[xcol].values.astype(float)
    isAnchor = np.isclose(x, anchor)
    if not isAnchor.any():
        print('  (no anchor row at {}={})'.format(xcol, anchor))
        return {}
    out = {}
    for c in cols:
        y = df[c].values.astype(float)
        ok = np.isfinite(y)
        xo, yo = x[ok & ~isAnchor], y[ok & ~isAnchor]
        if len(xo) < 2:
            continue
        deg = min(3, len(xo)-1)
        pred = float(np.polyval(np.polyfit(xo, yo, deg), anchor))
        act = float(y[isAnchor][0])
        scale = float(np.max(np.abs(yo))) or 1.0
        out[c] = {'actual': act, 'predicted': pred, 'dev': act-pred, 'relDev': (act-pred)/scale}
        print('    {:<10} LOG={:+.8f}  CRRA-fit predicts {:+.8f}  dev={:+.3e}  ({:+.3f}% of scale, '
              'deg {})'.format(c, act, pred, act-pred, 100*(act-pred)/scale, deg))
    return out


def testCal(args):
    """ Test 3. Are the CALIBRATED PARAMETERS continuous across the boundary?

    Reads the fine sweep's csv. If the LOG anchor sits off the curve its four CRRA neighbours trace, the
    discontinuity is already in the calibration and everything downstream inherits it. """
    df = pd.read_csv(args.csv).sort_values('ρ')
    print(df[['ρ', 'preferences', 'residual', 'verifyResidual', 'β', 'ω', 'η0', 'X0', 'τ', 'ι', 'sr',
              'nfev', 'time']].to_string(index = False))
    print('\nis the LOG anchor on the curve its CRRA neighbours trace?')
    _smoothness(df, 'ρ', ['β', 'ω', 'η0', 'X0', 'τ', 'ι', 'sr'], anchor = args.anchor)
    print('\nsecond differences (uniform ρ-step, so a clean series has these ~O(step^2) and of one sign):')
    for c in ['β', 'ω', 'η0', 'X0', 'τ', 'ι']:
        v = df[c].values.astype(float)
        print('    {:<4} '.format(c) + '  '.join('{:+.3e}'.format(d) for d in np.diff(v, 2)))
    return df


# ----------------------------------------------------------------------------------------------------
def testPath(args):
    """ Test 4. Is the solved PEE PATH continuous across the boundary, at each point's own calibration?

    Test 3 can pass while this fails: the calibration targets four scalars at t0, and a path can be
    displaced away from them while still hitting them. This re-solves each calibrated instance and reads
    the path objects the shock experiment is actually differenced against. """
    df = pd.read_csv(args.csv).sort_values('ρ')
    rows = []
    for ρ in df['ρ'].values:
        m = loadInstance(float(ρ), args.pkldir)
        t1 = time.time()
        pref, out, gs = solveAt(m, float(ρ), args.mode)
        s = summarise(m, out)
        rows.append({'ρ': float(ρ), 'pref': pref, 'time': time.time()-t1,
                     **{k: v for k, v in s.items() if k != 'τ'}})
        print('  rho={:<7.4f} {:<5} {:>5.0f}s  τ(t0)={:.8f}  τ(t0+1)={:.8f}  ι(t0)={:.8f}  '
              's(t0)={:.8f}'.format(ρ, pref, rows[-1]['time'], s['τ_t0'], s['τ_t0p1'], s['ι_t0'],
                                    s['s_t0']))
    out = pd.DataFrame(rows)
    _write(out, 'path_{}.csv'.format(args.mode))
    print('\nis the LOG anchor on the curve its CRRA neighbours trace?')
    _smoothness(out, 'ρ', ['τ_t0', 'τ_t0p1', 'ι_t0', 's_t0', 'h_t0'], anchor = args.anchor)
    return out


# ----------------------------------------------------------------------------------------------------
def testShock(args):
    """ Test 5. Is the universalisation RESPONSE continuous across the boundary?

    The object the dip was seen in. Reuses shockUniversal.runShock unchanged so this measures the shipped
    experiment rather than a re-implementation of it; only the instance directory is redirected. """
    import shockUniversal as su
    df = pd.read_csv(args.csv).sort_values('ρ')
    rows = []
    for ρ in df['ρ'].values:
        ρ = float(ρ)
        settings = settingsFor('CRRA', args.mode)
        d = su.runShock(ρ, settings, args.rule, args.refType, 1.0, False,
                        'boundary_{}_universal_{{rule}}_rho{{ρ:.4f}}.csv'.format(args.mode),
                        commonSettings = (args.mode == 'common'), pkldir = args.pkldir)
        r = {'ρ': ρ}
        for k in ('d_τ', 'd_s', 'd_ι', 'd_c10', 'd_c20'):
            if k in d:
                r[k+'_t0'] = float(d[k].iloc[0])
                r[k+'_t0p1'] = float(d[k].iloc[1])
        r['τ_base_t0'] = float(d['τ_base'].iloc[0])
        r['τ_reform_t0'] = float(d['τ_reform'].iloc[0])
        rows.append(r)
    out = pd.DataFrame(rows)
    _write(out, 'shock_{}_{}.csv'.format(args.rule, args.mode))
    print('\n' + out.to_string(index = False))
    print('\nis the LOG anchor on the curve its CRRA neighbours trace?')
    _smoothness(out, 'ρ', [c for c in out.columns if c != 'ρ'], anchor = args.anchor)
    return out


def testSettings(args):
    """ Test 6. Which of the two settings changes carries the production-mode boundary jump?

    --test limit measured C = (CRRA limit at rho->1) - (LOG at rho=1) as 1.6e-5 under common settings and
    6.3e-4 under production ones. CRRA's own settings are IDENTICAL in the two modes, so the whole 40x
    difference must be the LOG answer moving between nι=50/'linear' (its class defaults, which the sweep
    leaves it on) and nι=45/'cubic' (what the sweep gives CRRA). That is directly measurable, and cheap:
    a LOG solve is ~1 s, so the 2x2 costs nothing.

    Reported as deviations from the production LOG point, since that is the one every published
    calibration was solved at. """
    m = loadInstance(1.0, args.pkldir)
    print('parameters held fixed at: ' +
          '  '.join('{}={:.6f}'.format(k, v) for k, v in m.calibrationPars.items()) + '\n')
    combos = [('production (nι=50, linear)', {'nι': 50, 'interpKind': 'linear', 'smoothKnots': 4}),
              ('nι=50, cubic',               {'nι': 50, 'interpKind': 'cubic',  'smoothKnots': 4}),
              ('nι=45, linear',              {'nι': 45, 'interpKind': 'linear', 'smoothKnots': 4}),
              ('common (nι=45, cubic)',      {'nι': 45, 'interpKind': 'cubic',  'smoothKnots': 4}),
              ('nι=60, cubic',               {'nι': 60, 'interpKind': 'cubic',  'smoothKnots': 4}),
              ('nι=90, cubic',               {'nι': 90, 'interpKind': 'cubic',  'smoothKnots': 4})]
    rows = []
    for name, gs in combos:
        m.db.update(m.adjPar('ρ', 1.0))
        m.LOG.initGS(gs)
        out = m.solvePEE_LOG()
        s = summarise(m, out)
        rows.append({'settings': name, **{k: v for k, v in s.items() if k != 'τ'}})
        print('  LOG {:<28} τ(t0)={:.8f}  τ(t0+1)={:.8f}  ι(t0)={:.8f}  s(t0)={:.8f}'.format(
            name, s['τ_t0'], s['τ_t0p1'], s['ι_t0'], s['s_t0']))
    df = pd.DataFrame(rows)
    ref = df.iloc[0]
    print('\ndeviation from the production LOG point (this is what the CRRA side is compared against):')
    for _, r in df.iloc[1:].iterrows():
        print('  {:<28} Δτ(t0)={:+.3e}  Δτ(t0+1)={:+.3e}  Δι(t0)={:+.3e}'.format(
            r['settings'], r['τ_t0']-ref['τ_t0'], r['τ_t0p1']-ref['τ_t0p1'], r['ι_t0']-ref['ι_t0']))
    print('\nThe production-vs-common gap in --test limit was Δτ(t0) ≈ -6.2e-4, Δτ(t0+1) ≈ -1.3e-3.\n'
          'Whichever row above reproduces that is the setting that carries the boundary jump.')
    _write(df, 'settings.csv')
    return df


def _write(df, name):
    os.makedirs(OUTDIR, exist_ok = True)
    path = os.path.join(OUTDIR, name)
    df.to_csv(path, index = False)
    print('\nwritten: ' + os.path.relpath(path, REPO))


TESTS = {'limit': testLimit, 'refine': testRefine, 'settings': testSettings, 'cal': testCal,
         'path': testPath, 'shock': testShock}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description = __doc__.split('\n')[0])
    p.add_argument('--test', required = True, choices = list(TESTS) + ['all'])
    p.add_argument('--mode', default = 'common', choices = ('common', 'production'),
                   help = "'common': both solvers on identical grid settings, isolating the method. "
                          "'production': LOG on its pre-fix class defaults (nι=50, linear).")
    p.add_argument('--deltas', type = float, nargs = '+',
                   default = [0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002],
                   help = 'the |rho-1| ladder for --test limit/refine')
    p.add_argument('--ns', type = int, nargs = '+', default = [30, 45, 60, 75],
                   help = 'inner grid sizes for --test refine')
    p.add_argument('--csv', default = FINECSV)
    p.add_argument('--pkldir', default = FINEPKL)
    p.add_argument('--anchor', type = float, default = 1.0)
    p.add_argument('--rule', default = 'match', choices = ('match', 'flat'))
    p.add_argument('--refType', type = int, default = 1)
    a = p.parse_args()
    for name in (list(TESTS) if a.test == 'all' else [a.test]):
        print('\n' + '='*100 + '\n{}   (mode={})\n'.format(TESTS[name].__doc__.strip().split('\n')[0],
                                                            a.mode) + '='*100)
        TESTS[name](a)
