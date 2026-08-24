r""" Stake decomposition for the endogenous-theta exploration: who gains and who loses, and through which
channel, from a marginal increase in NEXT period's theta_{t+1} at the calibration year -- the "leaded
choice" of writing/Paper/Appendix/EndogenousSystemCharacteristics.tex, evaluated on the calibrated models
WITHOUT implementing a theta-solver.

Run:  .venv\Scripts\python.exe python\US\thetaStakes.py                      # US at rho = 0.5, 1, 2
      ... --rho 1 --country US FR UK                                          # LOG, all three countries
      ... --theta 0 0.5 1 --delta 0.05 --permanent                            # see below

The leaded-choice objective at t (probabilistic voting, same weights as the tau problem, base.FOC):

    dW_t/dθ_{t+1} = Σ_i γ_{t-1,i} ω p_{t-1} μ_{t-1,i} dυ_{2,t}^i/dθ_{t+1} + ν_t Σ_i γ_{t,i} μ_{t,i} dυ_{1,t}^i/dθ_{t+1}

with υ_{1,t}^i = (1+β_i)ln(tilde-c_{1,t}^i) + β_i ln R_{t+1} (LOG) or (1+B_{t+1}^i)(tilde-c_{1,t}^i)^{1-1/ρ}/(1-1/ρ)
(CRRA), and υ_{2,t}^i = ln c_{2,t}^i or (c_{2,t}^i)^{1-1/ρ}/(1-1/ρ) (docs model_PEE.tex). Every derivative
is a finite difference of the model's own equilibrium objects across two solves with θ_{t+1} = θ1 ± δ on
a createCopyFromt0(t0) seeded from the baseline state, in two readings:

    NOTE this is deliberately NOT shocks.py's convention any more. shocks.py now builds new equilibrium
    paths (the change over the whole horizon, own steady state) because the counterfactual tables compare
    countries. This file asks a different question -- what one electorate's marginal stake in the NEXT
    period's design is, at the state it actually inherits -- and that stake is by construction local and
    unanticipated: the savings entering t are sunk, and perturbing them along with θ would be measuring
    a different derivative. The copy convention is the right one here and should stay.

    ee     tau held at the baseline path           -> the direct (economic-equilibrium) channels
    full   tau_{t+1}, ... re-optimised politically  -> adds the "size" channel, dτ_{t+1}/dθ_{t+1}

tau_t itself is pinned at the baseline in both readings (envelope theorem: it is chosen optimally at t,
so its response to θ_{t+1} is second order for W_t; under LOG it does not respond at all).

Channels reported (all in utils per unit θ_{t+1}, weighted into W_t):
    old_h        retirees, via h_t: c_{2,t}^i ∝ h_t^{1-α} for every i, so this is (1-α)dln(h_t)/dθ_{t+1}
                 times the bloc's marginal-utility weight (ee reading)
    old_size     retirees, the τ_{t+1}-response feeding back on h_t (full - ee)
    young_resplit  young, the re-split of their OWN future benefit pot at fixed aggregates: the pot
                 (1-α)/α·(p/κ)·τ_{t+1}·s_t is fixed given s_t, and dPV_i/dθ_{t+1} = pot·(hηRatio_i - 1), which
                 sums to zero over types -- so this is pure redistribution among the young, negative in
                 utils because the losers (poor) have the higher marginal utility of wealth. Analytic,
                 d ln(tilde-c_1^i) = pot·(hηRatio_i-1)/((1+B^i)·tilde-c_1^i) (lifetime wealth W_i = (1+B^i)c̃_1^i).
                 NB under GHH the proportional half of this enters through h_t (the Bismarckian return is
                 part of the effective wage), so do not read dln(h_t) as a separate efficiency gain.
    young_aggregate  young, everything else in the ee reading: the genuine GE/efficiency part (h_t, s_t,
                 R_{t+1}, B_{t+1}, Γ_s)
    young_size   young, the τ_{t+1} response (full - ee)
    seq_old      REFERENCE: the sequential choice's retiree redistribution stake dW_t/dθ_t (closed form
                 via Base.c2i, everything else fixed) -- the force every proposal has to beat
Plus dτ_{t+1}/dθ_{t+1}, dln h_t, dln s_t, dln R_{t+1} (ee and full), and two distance-to-interior metrics:
ratio = -old_total/young_total (interior needs ≈1) and omegaNeeded = ω·ratio^{-1}... i.e. the retiree
weight at which the leaded FOC would be zero.

--permanent sets θ_{t+1} = θ_{t+2} = ... = θ1 instead of θ_{t+1} alone (the "permanent choice" reading).

THE WEDGE (appendix ESC, "Marginal costs of raising redistributive, public funds"): benefits are scaled by
f(θ), f' > 0, which enters every period-t object exactly where τ_{t+1} does (Γs, Θh, si_s, c1i, tildec1i --
"f(θ) in front of the (1-α)/α part"), while τ_t as the current tax is untouched. Two things are reported
for it, both in the ee reading (τ pinned -- the premise of the B+A hybrid, that the wedge neutralises the
τ_{t+1} response; re-optimising τ under the wedge would need f inside policy.py's FOC and is NOT done here):
    G_old, G_young, G   dW_t/dln f_{t+1}: the political value of scaling the young's future benefit pot by
                        1% at fixed θ_{t+1} (young gain through lifetime wealth, retirees through h_t)
    epsNeeded           the semi-elasticity f'(θ)/f(θ) at which the ee FOC is zero: -total_ee/G
    pNeeded_phi*        the p of f(θ) = φ+(1-φ)θ^p delivering that semi-elasticity at this θ, for
                        φ = 0.25/0.5/0.75 (NaN at θ=0, where the form is degenerate)
    seq_G, seq_epsNeeded, seq_pNeeded_phi50   the same for the SEQUENTIAL choice dW_t/dθ_t (retirees
                        only) -- this is the appendix's own calibration of p (0.41 at φ = 0.5), so a check
--wedge PHI P additionally runs the ee reading WITH f(θ) = (φ+(1-φ)θ^p)/(φ+(1-φ)θ_base^p) installed along
the whole path (normalised so the baseline is untouched), i.e. the exact ee FOC under that wedge rather
than its linearisation. The full reading is skipped in that mode (see above).
Writes results/diagnostics/thetaStakes{,CommonX}{,Permanent}{,Wedge}.csv, one row per (country, rho, theta1).
"""
import os, sys, argparse, time
from contextlib import contextmanager
import numpy as np, pandas as pd
from scipy import optimize

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
sys.path.insert(0, HERE)
os.chdir(HERE)

import test as testmod
import testEU
from model import ModelUS
from runShocksUS import usRow

OUTDIR = os.path.join(REPO, 'results', 'diagnostics')


# ---------------------------------------------------------------- models

def buildUS(ρ, commonX = False, n = 101, ns = 150, smoothKnots = 4, interpKind = 'linear'):
    """ The calibrated US model at this rho, installed from the sweep csv exactly as runShocksUS does. """
    row = usRow(ρ, commonX)
    preferences = 'LOG' if ρ == 1 else 'CRRA'
    m = ModelUS(pars = testmod.pars | {'ρ': float(ρ), 'β': float(row['β']), 'ω': float(row['ω'])},
                commonX = commonX, **testmod.kwargs)
    m.db['dates'] = testmod.dates
    wp = {'smoothKnots': smoothKnots or None, 'interpKind': interpKind}
    getattr(m, preferences).initGS(({'n': n, 'ns': ns} if preferences == 'CRRA' else {'n': n}) | wp)
    if commonX:
        m.initProductivity_commonX(X = float(row['X']))
        m.updateAuxPars()
    return m, preferences


def buildEU(country, grouping = None, commonX = False):
    """ France/UK at rho = 1 (LOG), calibrated on the spot (a 1-D root in omega -- seconds). """
    m = testEU.model(country, grouping = grouping, commonX = commonX)
    m.calibrate()
    return m, 'LOG'


# ---------------------------------------------------------------- one evaluation

def stateGridCRRA(m, t0):
    """ The s-grid solveBackward would build on a copy from t0 at the BASELINE theta -- computed once and
    passed to every perturbed solve, so the interpolation noise does not move with theta. """
    mt = m.createCopyFromt0(t0)
    gs = mt.CRRA.GS['PEE']
    if gs['stateGrids']['s_'] is not None:
        return np.asarray(gs['stateGrids']['s_'])
    θ = mt.db['θ'].values.astype(float)
    return mt.CRRA.defaultSGrid(θ[-1], mt.db['t'][-1], n = gs['gridSettings']['ns'])


@contextmanager
def leadWedge(mt, τ, fθ):
    """ While active, mt.leadSym(τ) -- for THIS τ array object -- returns lead(f(θ)·τ) instead of lead(τ).
    EE_LOG_solve, EE_CRRA_residual/_solve and EE_report all build τ_{t+1} through exactly that call and pass
    the same array object through, so the wedge lands on every lead position and on no current-tax position.
    Identity-based on purpose (a value match could hit a policy-solver's own τ arrays); asserts the patch was
    hit so a refactor that stops routing τ1 through leadSym fails loudly instead of silently dropping f. """
    orig, hits = mt.leadSym, []
    def patched(x, *a, **k):
        if x is τ:
            hits.append(1)
            return orig(fθ*τ, *a, **k)
        return orig(x, *a, **k)
    mt.leadSym = patched
    try:
        yield
    finally:
        del mt.leadSym
        assert hits, 'leadWedge: the EE path never called leadSym(τ) -- the wedge was not applied'


def fWedge(θ, φ, p, θBase):
    """ f(θ) = (φ+(1-φ)θ^p)/(φ+(1-φ)θBase^p): the appendix's form, normalised so the baseline is untouched. """
    return (φ + (1-φ)*np.asarray(θ, float)**p)/(φ + (1-φ)*θBase**p)


def fSemiElasticity(θ, φ, p):
    """ f'(θ)/f(θ) for f = φ+(1-φ)θ^p. """
    return (1-φ)*p*θ**(p-1)/(φ + (1-φ)*θ**p)


def pNeeded(θ, φ, eps):
    """ The SMALLER p at which f'(θ)/f(θ) = eps for f = φ+(1-φ)θ^p (for θ<1 the semi-elasticity is hump-shaped
    in p, so every reachable eps has two solutions; the appendix's p=0.41 is the small one). NaN if θ=0,
    eps<=0, or eps above the hump. """
    if not (θ > 0 and eps > 0):
        return np.nan
    grid = np.linspace(1e-6, 50., 5001)
    vals = fSemiElasticity(θ, φ, grid)
    pmax = grid[np.argmax(vals)]
    g = lambda p: fSemiElasticity(θ, φ, p) - eps
    if g(pmax) < 0:
        return np.nan
    return optimize.brentq(g, 1e-6, pmax)


def evaluate(m, base, preferences, θ1, reading, permanent = False, sGrid = None, fθ = None, fScale1 = 1.):
    """ Solve the copy-from-t0 with θ_{t0+1} = θ1 (or θ_{t0+1}, ... = θ1 if permanent) in the given reading.
    Returns (copy, τ path, EE report). tau_0 (= t0) is the baseline's in both readings.
    fθ: callable θ -> f(θ) installing the wedge on the EE solve (ee reading only -- see module docstring);
    fScale1 additionally scales f at the copy's period 1 (the lead seen from t0), which is how G is measured. """
    t0 = m.db['t'][m.db['t0']]
    seed = m.stateAtT0(base['report'], t0)
    τBase = base['τ'].loc[t0:].values.astype(float)
    mt = m.createCopyFromt0(t0)
    θ = mt.db['θ'].values.astype(float).copy()
    if permanent:
        θ[1:] = θ1
    else:
        θ[1] = θ1
    mt.db.update(mt.adjPar('θ', θ))  # db['θ'] is read by ΓsCap and the CRRA brackets -- keep consistent
    ε = mt.db['eps'].values.astype(float)
    f = np.ones_like(θ) if fθ is None else np.asarray(fθ(θ), float).copy()
    f[1] *= fScale1
    if reading == 'ee':
        τ = τBase.copy()
        if not np.allclose(f, 1.):
            with leadWedge(mt, τ, f):
                sol = getattr(mt, f'EE_{preferences}_solve')(τ, θ, ε, **seed)
                report = mt.EE_report(sol, τ, θ, ε, seed['s0'])
            return mt, τ, report
    elif not np.allclose(f, 1.):
        raise ValueError('the wedge is only implemented for the ee reading (f is not in the policy FOC)')
    elif preferences == 'LOG':
        τ = mt.solvePEE_LOG(θ = θ, ε = ε, **seed)['τ'].values.astype(float).copy()
        τ[0] = τBase[0]
    else:
        full = mt.solvePEE_CRRA(θ = θ, ε = ε, backwardKwargs = {'sGrid': sGrid}, **seed)
        τ = full['τ'].values.astype(float).copy()
        τ[0] = τBase[0]
    sol = getattr(mt, f'EE_{preferences}_solve')(τ, θ, ε, **seed)
    report = mt.EE_report(sol, τ, θ, ε, seed['s0'])
    return mt, τ, report


def objects(m, report, τ, preferences, pos = 0):
    """ The utility-relevant objects at the copy's period `pos` (= t0): indirect utilities, their level
    factors (dυ/dln c), and the aggregates the channels are read off. """
    t, t1 = m.db['t'][pos], m.db['t'][pos+1]
    c1 = report['tildec1i'].xs(t).values.astype(float)
    c2 = report['c2i'].xs(t).values.astype(float)
    B = report['B'].xs(t).values.astype(float)
    R1 = float(report['R'].xs(t1))
    β = m.B.get('βi', t)
    if preferences == 'LOG':
        v1, v2 = (1+β)*np.log(c1) + β*np.log(R1), np.log(c2)
        lev1, lev2 = (1+β), np.ones_like(c2)
    else:
        p = 1 - 1/float(m.B.get('ρ', t))
        v1, v2 = (1+B)*c1**p/p, c2**p/p
        lev1, lev2 = (1+B)*c1**p, c2**p
    α, ξ, pt, κ = (float(m.B.get(k, t)) for k in ('α', 'ξ', 'p', 'κ'))
    Γs = float(report['Γs'].xs(t))
    θ1 = float(m.db['θ'].xs(t1))
    bracket = m.B.auxProd(t)/(1+ξ) + Γs*(1-α)/α*pt*float(τ[pos+1])*(1-θ1)/κ   # tildec1i's type-specific factor
    return {'v1': v1, 'v2': v2, 'lev1': lev1, 'lev2': lev2, 'c1': c1, 'c2': c2, 'B': B, 'R1': R1,
            'h': float(report['h'].xs(t)), 's': float(report['s'].xs(t)), 'Γs': Γs,
            'τ1': float(τ[pos+1]), 'θ1': θ1, 'bracket': bracket, 'α': α, 'ξ': ξ, 'p': pt, 'κ': κ}


def weights(m, pos = 0):
    """ W_t's bloc weights at the copy's period pos: old_i = γ_{t-1,i}·ω·p_{t-1}·μ_{t-1,i}, young_i = ν_t·γ_{t,i}·μ_{t,i}
    -- exactly base.FOC's combination. """
    t = m.db['t'][pos]
    old = m.B.get('γi[t-1]', t) * m.B.ω2i(t)
    young = float(m.B.get('ν', t)) * m.B.get('γi', t) * m.B.ω1i(t)
    return old, young


# ---------------------------------------------------------------- the decomposition

def sequentialStake(m, base, preferences, δ = 1e-3):
    """ The sequential choice's retiree stake dW_t/dθ_t at t0 -- a pure re-split of a fixed pot, so only
    c_{2,t}^i moves (Base.c2i with θ_t ± δ, everything else fixed). Also returned per type. """
    t0Pos = m.db['t0']
    t0, tm1 = m.db['t'][t0Pos], m.db['t'][t0Pos-1]
    rep, τ = base['report'], float(base['τ'].xs(t0))
    h, s_ = float(rep['h'].xs(t0)), float(rep['s_'].xs(t0))
    siRatio_ = rep['si_s'].xs(tm1).values.astype(float)
    θ = float(m.db['θ'].xs(t0))
    lo, hi = max(0., θ-δ), min(1., θ+δ)
    c2 = {x: m.B.c2i(h, s_, τ, x, siRatio_, t = t0) for x in (lo, hi)}
    if preferences == 'LOG':
        v2 = {x: np.log(c) for x, c in c2.items()}
    else:
        p = 1 - 1/float(m.B.get('ρ', t0))
        v2 = {x: c**p/p for x, c in c2.items()}
    dv2 = (v2[hi]-v2[lo])/(hi-lo)
    old = m.B.get('γi[t-1]', t0) * m.B.ω2i(t0)
    # G for the sequential choice: scaling the retirees' own benefits (τ_t -> (1±ε)τ_t in c2i, θ_t fixed)
    ε = 1e-3
    c2s = {x: m.B.c2i(h, s_, x*τ, θ, siRatio_, t = t0) for x in (1-ε, 1+ε)}
    if preferences == 'LOG':
        v2s = {x: np.log(c) for x, c in c2s.items()}
    else:
        v2s = {x: c**p/p for x, c in c2s.items()}
    G = float((old*(v2s[1+ε]-v2s[1-ε])).sum()/(np.log(1+ε)-np.log(1-ε)))
    seq = float((old*dv2).sum())
    eps = -seq/G if G != 0 else np.nan
    return {'seq_old': seq, 'seq_G': G, 'seq_epsNeeded': eps,
            'seq_pNeeded_phi50': pNeeded(θ, 0.5, eps)}, old*dv2


def stakesAt(m, base, preferences, θ1, δ, permanent = False, sGrid = None, verbose = True, fθ = None,
             εG = 1e-2):
    """ The full decomposition at θ_{t+1} = θ1 (central difference ±δ, one-sided at the corners). With a
    wedge fθ only the ee reading is run (see module docstring); G is measured by scaling f at period 1 by
    (1±εG) at θ1 itself. """
    lo, hi = max(0., θ1-δ), min(1., θ1+δ)
    step = hi - lo
    out = {'θ1': θ1, 'δ': δ, 'permanent': permanent, 'θlo': lo, 'θhi': hi, 'wedge': fθ is not None}
    readings = ('ee',) if fθ is not None else ('ee', 'full')
    U = {}
    for reading in readings:
        for x in (lo, hi):
            tic = time.time()
            mt, τ, rep = evaluate(m, base, preferences, x, reading, permanent, sGrid, fθ = fθ)
            U[reading, x] = objects(mt, rep, τ, preferences)
            if verbose:
                print('    {:<4} θ1={:.4f}: τ1={:.5f} h={:.5f} s={:.5f} R1={:.4f}  ({:.1f}s)'.format(
                    reading, x, U[reading, x]['τ1'], U[reading, x]['h'], U[reading, x]['s'],
                    U[reading, x]['R1'], time.time()-tic))
    old, young = weights(mt)
    out['oldWeight'], out['youngWeight'] = float(old.sum()), float(young.sum())

    def d(reading, key, log = False):
        a, b = U[reading, lo][key], U[reading, hi][key]
        return ((np.log(b)-np.log(a)) if log else (b-a))/step

    for reading in readings:
        out[f'old_{reading}'] = float((old*d(reading, 'v2')).sum())
        out[f'young_{reading}'] = float((young*d(reading, 'v1')).sum())
        out[f'dlnh_{reading}'] = d(reading, 'h', log = True)
        out[f'dlns_{reading}'] = d(reading, 's', log = True)
        out[f'dlnR1_{reading}'] = d(reading, 'R1', log = True)
        out[f'dτ1_{reading}'] = d(reading, 'τ1')
    # young by type (who among the young is for and against), full reading if available
    dv1 = d(readings[-1], 'v1')
    for i, w in enumerate(young):
        out[f'young_{readings[-1]}_i{i}'] = float(w*dv1[i])

    # channels inside the ee reading: the re-split at fixed aggregates (analytic, at the lo/hi average
    # of the ee objects) and the aggregate/GE remainder
    avg = lambda k: 0.5*(U['ee', lo][k] + U['ee', hi][k])
    o = U['ee', lo]
    pot = (1-o['α'])/o['α']*o['p']/o['κ']*avg('τ1')*avg('s')
    hηRatio = mt.B.hηRatio(mt.db['t'][0])
    dlnc1Resplit = pot*(hηRatio-1)/((1+avg('B'))*avg('c1'))
    out['young_resplit'] = float((young*avg('lev1')*dlnc1Resplit).sum())
    for i, w in enumerate(young):
        out[f'young_resplit_i{i}'] = float(w*avg('lev1')[i]*dlnc1Resplit[i])
    out['young_aggregate'] = out['young_ee'] - out['young_resplit']
    out['old_h'] = out['old_ee']
    out['total_ee'] = out['old_ee'] + out['young_ee']
    out['ratio_ee'] = -out['old_ee']/out['young_ee'] if out['young_ee'] != 0 else np.nan
    t0 = m.db['t'][m.db['t0']]
    ω = float(m.db['ω'].xs(t0))
    out['ω'] = ω
    if 'full' in readings:
        out['young_size'] = out['young_full'] - out['young_ee']
        out['old_size'] = out['old_full'] - out['old_ee']
        out['total_full'] = out['old_full'] + out['young_full']
        out['ratio'] = -out['old_full']/out['young_full'] if out['young_full'] != 0 else np.nan
        out['ωNeeded'] = ω/out['ratio'] if (out['ratio'] > 0) else np.nan
    else:
        for k in ('young_size', 'old_size', 'total_full', 'ratio', 'ωNeeded', 'old_full', 'young_full',
                  'dlnh_full', 'dlns_full', 'dlnR1_full', 'dτ1_full'):
            out[k] = np.nan

    # G: the political value of scaling the young's future benefit pot, dW_t/dln f_{t+1} at θ1 (ee)
    V = {}
    for sc in (1-εG, 1+εG):
        mt, τ, rep = evaluate(m, base, preferences, θ1, 'ee', permanent, sGrid, fθ = fθ, fScale1 = sc)
        V[sc] = objects(mt, rep, τ, preferences)
    dlnf = np.log(1+εG) - np.log(1-εG)
    out['G_old'] = float((old*(V[1+εG]['v2']-V[1-εG]['v2'])).sum()/dlnf)
    out['G_young'] = float((young*(V[1+εG]['v1']-V[1-εG]['v1'])).sum()/dlnf)
    out['G'] = out['G_old'] + out['G_young']
    out['epsNeeded'] = -out['total_ee']/out['G'] if out['G'] != 0 else np.nan
    for φ in (0.25, 0.5, 0.75):
        out[f'pNeeded_phi{int(φ*100)}'] = pNeeded(θ1, φ, out['epsNeeded'])
    return out


def run(m, preferences, θs, δ, permanent, label, verbose = True, wedge = None):
    """ All theta levels for one calibrated model. wedge: None or (φ, p) -- see module docstring. """
    t0 = m.db['t'][m.db['t0']]
    tic = time.time()
    base = getattr(m, f'solvePEE_{preferences}')()
    sGrid = stateGridCRRA(m, t0) if preferences == 'CRRA' else None
    θBase = float(m.db['θ'].xs(t0))
    seq, seqByType = sequentialStake(m, base, preferences)
    fθ = None if wedge is None else (lambda θ: fWedge(θ, wedge[0], wedge[1], θBase))
    print('\n{}: {} baseline τ={:.4f} θ={:.4f} ω={:.4f} ν={:.3f}  seq dW/dθ_t (old) = {:+.4f}, G = {:+.4f}, '
          'eps needed = {:.3f} -> p(φ=.5) = {:.3f}   ({:.0f}s){}'.format(
              label, preferences, float(base['τ'].xs(t0)), θBase, float(m.db['ω'].xs(t0)),
              float(m.db['ν'].xs(t0)), seq['seq_old'], seq['seq_G'], seq['seq_epsNeeded'],
              seq['seq_pNeeded_phi50'], time.time()-tic,
              '' if wedge is None else '   [wedge φ={}, p={}: ee reading only]'.format(*wedge)))
    rows = []
    for θ1 in θs:
        θ1 = θBase if θ1 == 'base' else float(θ1)
        print('  θ_{{t+1}} = {:.4f}'.format(θ1))
        r = stakesAt(m, base, preferences, θ1, δ, permanent, sGrid, verbose = verbose, fθ = fθ)
        r |= {'label': label, 'preferences': preferences, 'θBase': θBase, **seq,
              'τBase': float(base['τ'].xs(t0)), 'ν': float(m.db['ν'].xs(t0)),
              'wedgePhi': np.nan if wedge is None else wedge[0], 'wedgeP': np.nan if wedge is None else wedge[1]}
        for i, v in enumerate(seqByType):
            r[f'seq_old_i{i}'] = float(v)
        rows.append(r)
        print('    old: h={old_h:+.4f} size={old_size:+.4f} | young: resplit={young_resplit:+.4f} '
              'aggregate={young_aggregate:+.4f} size={young_size:+.4f} | total ee={total_ee:+.4f} full={total_full:+.4f}  '
              'ratio ee={ratio_ee:.3f} full={ratio:.3f}  ωNeeded={ωNeeded:.2f} | dτ1={dτ1_full:+.4f} '
              'dlnh(ee)={dlnh_ee:+.4f}'.format(**r))
        print('    wedge: G old={G_old:+.4f} young={G_young:+.4f} -> eps needed={epsNeeded:.3f}  '
              'p(φ=.25/.5/.75)={pNeeded_phi25:.3f}/{pNeeded_phi50:.3f}/{pNeeded_phi75:.3f}'.format(**r))
    return rows


def main():
    p = argparse.ArgumentParser(description = 'Stake decomposition for the leaded choice of theta_{t+1}.')
    p.add_argument('--rho', type = float, nargs = '*', default = [0.5, 1.0, 2.0])
    p.add_argument('--country', nargs = '*', default = ['US'], choices = ('US', 'FR', 'UK', 'UKUS'))
    p.add_argument('--theta', nargs = '*', default = ['0', '0.5', 'base', '1'],
                   help = "theta_{t+1} levels; 'base' = the calibrated theta")
    p.add_argument('--delta', type = float, default = None,
                   help = 'finite-difference half-step (default 1e-3 under LOG, 0.05 under CRRA)')
    p.add_argument('--permanent', action = 'store_true')
    p.add_argument('--wedge', type = float, nargs = 2, metavar = ('PHI', 'P'), default = None,
                   help = 'install f(θ)=φ+(1-φ)θ^p (normalised at the baseline θ) on the ee reading')
    p.add_argument('--commonX', action = 'store_true')
    p.add_argument('--n', type = int, default = 101)
    p.add_argument('--ns', type = int, default = 150)
    p.add_argument('--smoothKnots', type = int, default = 4)
    p.add_argument('--interpKind', default = 'linear')
    p.add_argument('--quiet', action = 'store_true')
    p.add_argument('--out', default = None)
    a = p.parse_args()
    os.makedirs(OUTDIR, exist_ok = True)
    out = a.out or os.path.join(OUTDIR, 'thetaStakes' + ('CommonX' if a.commonX else '')
                                + ('Permanent' if a.permanent else '') + ('Wedge' if a.wedge else '') + '.csv')
    rows = []
    for ρ in a.rho:
        for c in a.country:
            if c == 'US':
                m, pref = buildUS(ρ, a.commonX, a.n, a.ns, a.smoothKnots, a.interpKind)
            else:
                if ρ != 1:
                    print(f'\n{c} at ρ={ρ}: skipped (FR/UK are run at LOG only here).')
                    continue
                m, pref = buildEU('UK' if c == 'UKUS' else c, grouping = 'US' if c == 'UKUS' else None,
                                  commonX = a.commonX)
            δ = a.delta if a.delta is not None else (1e-3 if pref == 'LOG' else 0.05)
            rs = run(m, pref, a.theta, δ, a.permanent, f'{c} ρ={ρ}', verbose = not a.quiet,
                     wedge = tuple(a.wedge) if a.wedge else None)
            for r in rs:
                r |= {'country': c, 'ρ': ρ}
            rows += rs
            pd.DataFrame(rows).to_csv(out, index = False)
    pd.DataFrame(rows).to_csv(out, index = False)
    print('\n-> {}'.format(os.path.relpath(out, REPO)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
