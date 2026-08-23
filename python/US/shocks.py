r""" The US counterfactuals: pension design (theta), ageing, and French characteristics.

Machinery only -- runShocksUS.py is the driver. Every experiment is an UNANTICIPATED, PERMANENT change
dated at the calibration year t0 (2020), run on createCopyFromt0(t0) seeded from the baseline's own state,
and reported in two readings:

    Full effect            the shocked model, tau re-optimised politically   solvePEE_*
    Economic equilibrium   the shocked model, tau held at the BASELINE path  EE_*_solve

The decomposition is the point of the tables (writing/Paper/Tables/US_PensChars.tex, US_Ageing.tex): for
theta the two effects work against each other on savings, for ageing the EE-only tax path is fixed by
construction so its whole content is the capital-deepening channel.

REPORTING CONVENTIONS -- all three matter, and none is arbitrary.

  * The savings rate reported in the paper is s/(w*h), savings over gross LABOUR income, not Base's
    savingsRate = s/Y. They differ by exactly (1-alpha): the baseline calibration gives s/Y = 0.153737
    and 0.153737/0.7 = 0.219624, against the paper's 21.96%. srPaper() does that division in one place.

  * The workweek is reported RELATIVE to the baseline and rescaled to the observed one:
    workweek = workweek_data * hbar/hbar_baseline. Under vector X the LEVEL of hbar is not identified
    (docs eq:us:model:hoursUnit), so an absolute hbar is meaningless -- hbar*84 is 31.54 at the baseline,
    not the 39.39 the data say. Only the ratio is a result. This is the same rule modelFR.ModelFR builds
    its hours target from, applied to reporting instead of to calibration.

  * db['dates'] is STALE on a copy -- it keeps the full original calendar against a shorter, renumbered
    horizon (see test_createCopyFromt0.py). Never label a copy's periods with it. Everything here is
    reported at the copy's period 0, which IS the baseline's t0, and the calendar is carried explicitly.

THE FRENCH COUNTERFACTUALS. Three separate experiments, and the paper's own table pins what each means:

  * Income distribution: France's eta_i with X_i held at the US values -- see shockIncomeDistribution for
    why that particular combination, and why the obvious alternatives are all the same experiment as each
    other. France's income groups are cut at US percentiles precisely so that gamma_i lines up and the
    swap is like-for-like (Quant.tex).
  * Leisure preferences: a PURE SCALE on X_i, matching France's population-weighted mean X. It is
    rescaleX, i.e. eq:us:model:scaleInvariance, so tau, the savings rate and R cannot move at all and only
    the workweek does. US_OtherShocks.tex confirms this exactly -- its leisure row carries the baseline's
    own 14.43% and 21.96% and moves the workweek 39.39 -> 34.72. Anything else would be a different
    experiment, and a version of this table where the leisure row DID move taxes is commented out beside
    the live one.
  * Voting: France's mu_i. Only the PROFILE matters: FOC is linear in mu through both omega1i and omega2i,
    so a common scale cancels out of z_t = 0. US mu rises steeply across income (0.474/0.629/0.765),
    France's is nearly flat (0.810/0.857/0.852).
"""
import numpy as np, pandas as pd


# ---------------------------------------------------------------- reporting

def srPaper(sr, α):
    """ s/(w*h) from Base.savingsRate's s/Y. See the module docstring. """
    return sr/(1-α)


def readout(m, τ, report, workweekData, hbarRef, pos = 0):
    """ The three reported quantities at a copy's period `pos` (= the baseline's t0).

    hbarRef is the BASELINE's hbar, the reference the workweek is expressed against; pass the baseline's
    own to make its row come out at workweekData exactly. """
    t = m.db['t'][pos]
    α = float(m.db['α'].xs(t))
    hbar = float(m.B.avgHours(report['h'].xs(t), t))
    sr = float(m.B.savingsRate(report['s'].xs(t), report['s_'].xs(t), report['h'].xs(t), t))
    return {'τ': float(np.asarray(τ)[pos] if not hasattr(τ, 'xs') else τ.xs(t)),
            'sr': srPaper(sr, α), 'srOverY': sr,
            'workweek': workweekData * hbar/hbarRef,
            'hbar': hbar, 'h': float(report['h'].xs(t)), 'R': float(report['R'].xs(t))}


# ---------------------------------------------------------------- the shocks

def shockTheta(mt0, value):
    """ theta_t = `value` for every period of the copy. Returns the installed path.

    db['θ'] is written (rather than only passed to the solver) because solvePEE_*'s theta=None default,
    Base.ΓsCap and the CRRA steady-state bracket all read it from db, and leaving them on the calibrated
    theta while the solver used a shocked one would be silently inconsistent.

    DO NOT call updateAuxPars after this. theta is in paramsFromFuncs, so updateAuxPars recomputes it
    from getTheta -- i.e. from the replacement-rate data -- and would put the calibrated theta straight
    back, undoing the shock while every other number still looked reasonable. That is exactly how this
    first ran: theta = 0 and theta = 1 both returned the baseline to every digit. Nothing else in
    paramsFromFuncs (Gamma_h, eps, kappa) depends on theta, so nothing needs refreshing here. """
    mt0.db.update(mt0.adjPar('θ', float(value)))
    return mt0.db['θ'].values.copy()


def shockAgeing(mt0, kind):
    """ 'mild': nu_t -> (1+nu_t)/2.   'acute': nu_t -> 1.   Both from the copy's first period onward,
    which IS 2020 onward -- the copy has no earlier period, so "from 2020 and onward" (US_Ageing.tex's
    own note) is enforced by construction rather than by a date filter. """
    ν = mt0.db['ν'].values.astype(float)
    new = (1+ν)/2 if kind == 'mild' else np.ones_like(ν)
    mt0.db.update(mt0.adjPar('ν', new))
    mt0.updateAuxPars()
    return new


def shockIncomeDistribution(mt0, ηFR, pinTheta = False, θPin = None):
    """ France's productivity vector eta_i, with X_i HELD at the US values. That combination is the
    experiment, and which combination it is matters: it reproduces US_OtherShocks.tex's income row exactly
    (tau 13.28%, savings rate 22.75%), where the alternatives do not.

    Why the alternatives collapse. Under vector X the eigenvector identification makes y^eta proportional
    to z^eta, and every aggregate uses y^eta alone (docs eq:us:model:scaleInvariance) -- so "swap z^eta and
    re-derive eta and X" and "take France's whole (eta, X) pair" are the SAME experiment, both giving
    tau = 13.79%. Only holding X_i fixed while eta moves is a different one, because then
    y^eta_i = eta_i^{1+xi}/X_i^xi is no longer proportional to either country's z^eta.

    That also makes the decomposition in US_OtherShocks.tex coherent: eta carries "income distribution",
    the LEVEL of X carries "leisure preferences" (shockLeisure), and the two do not overlap. Changing both
    at once would just be the France calibration.

    THETA MOVES WITH ETA, AND IT MOVES A LOT. theta is in paramsFromFuncs, so updateAuxPars re-derives it
    from getTheta -- i.e. it holds the OECD replacement-rate RATIO db['RR0'] fixed and lets theta adjust to
    the new income distribution. It falls from 0.738 to 0.495: under France's flatter distribution the same
    observed replacement-rate ratio implies a much less Bismarckian system. This is NOT incidental to the
    result -- pinning theta at the US value instead gives tau = 12.83% against 13.28%. Re-deriving is what
    reproduces US_OtherShocks.tex, so it is the default, but the counterfactual then bundles a pension-design
    change with the inequality change and should be read that way. pinTheta = True holds theta at `θPin`
    for the alternative reading.

    eta_0 (the zero-mass slot) is kept at the US value -- it is multiplied by gamma_0 = 0, but must stay
    finite. """
    ηj = np.hstack([mt0.db['ηj'].values[0, 0], np.asarray(ηFR, dtype = float)])
    mt0.db.update(mt0.adjPar('ηj', ηj))
    mt0.updateAuxPars()   # Gamma_h and theta are both functions of eta/X
    if pinTheta:
        mt0.db.update(mt0.adjPar('θ', float(θPin)))   # after updateAuxPars -- see shockTheta
    return float(mt0.db['θ'].xs(mt0.db['t'][0]))


def shockLeisure(mt0, xbarRatio):
    """ France's leisure preferences: scale every X_i by xbarRatio = Xbar_FR/Xbar_US (population-weighted
    means), i.e. rescaleX(lambda) with lambda = xbarRatio**(-xi).

    A pure scale, so tau/sr/R cannot move -- see the module docstring. Returns lambda. """
    ξ = float(mt0.db['ξ'].xs(mt0.db['t'][0]))
    λ = float(xbarRatio)**(-ξ)
    mt0.rescaleX(λ)
    return λ


def shockVoting(mt0, μFR):
    """ France's voting profile. Only relative mu matters (the FOC is linear in it), so the level of the
    supplied vector is irrelevant; it is installed as given. """
    mt0.db.update(mt0.adjPar('μj', np.asarray(μFR, dtype = float)))
    mt0.updateAuxPars()


SHOCKS = {
    'theta0':   ('$\\theta = 0$',          lambda mt0, d: shockTheta(mt0, 0.)),
    'theta1':   ('$\\theta = 1$',          lambda mt0, d: shockTheta(mt0, 1.)),
    'mild':     ('Mild ageing',            lambda mt0, d: shockAgeing(mt0, 'mild')),
    'acute':    ('Acute ageing',           lambda mt0, d: shockAgeing(mt0, 'acute')),
    'frIncome': ('Income distribution',    lambda mt0, d: shockIncomeDistribution(mt0, d['ηFR'], d.get('pinTheta', False), d.get('θUS'))),
    'frLeisure':('Leisure preferences',    lambda mt0, d: shockLeisure(mt0, d['xbarRatio'])),
    'frVoting': ('Voting',                 lambda mt0, d: shockVoting(mt0, d['μFR'])),
}


# ---------------------------------------------------------------- running one experiment

def solveBaseline(m, preferences):
    """ The calibrated model's own PEE path over the full horizon, plus the readout at t0. """
    out = getattr(m, f'solvePEE_{preferences}')()
    return out


def runOne(m, base, name, data, preferences, workweekData, hbarRef, solveKwargs = None):
    """ One shock, both readings, on a fresh copy each time.

    Returns {'full': readout, 'ee': readout, 'extra': ...}. The two readings share one copy-and-shock
    step, so they differ ONLY in whether tau is re-optimised -- which is what makes the decomposition a
    decomposition rather than two loosely related runs.

    The EE-only reading holds tau at the BASELINE path over the copy's horizon (sliced off the front, so
    position 0 is t0), and solves the economic equilibrium alone: no political problem, no backward
    recursion, no state grid. Seconds, against a full PEE solve.
    """
    t0Pos = m.db['t0']
    t0 = m.db['t'][t0Pos]
    seed = m.stateAtT0(base['report'], t0)
    label, apply = SHOCKS[name]
    τBase = base['τ'].loc[t0:].values.astype(float)
    out = {'label': label}

    # --- full effect
    mFull = m.createCopyFromt0(t0)
    extra = apply(mFull, data)
    full = getattr(mFull, f'solvePEE_{preferences}')(**seed, **(solveKwargs or {}))
    out['full'] = readout(mFull, full['τ'], full['report'], workweekData, hbarRef)
    out['extra'] = extra if np.isscalar(extra) else None

    # --- economic-equilibrium-only: same shock, baseline taxes
    # EE_*_solve returns {'s','h','Γs','B'} only; EE_report expands that into the equilibrium objects
    # readout needs ('s_' and 'R' among them). theta/eps come from the SHOCKED copy's db -- for the theta
    # experiments that is the whole shock, so reading them off the baseline here would silently undo it.
    mEE = m.createCopyFromt0(t0)
    apply(mEE, data)
    θEE, εEE = mEE.db['θ'].values.astype(float), mEE.db['eps'].values.astype(float)
    sol = getattr(mEE, f'EE_{preferences}_solve')(τBase, θEE, εEE, **seed)
    ee = mEE.EE_report(sol, τBase, θEE, εEE, seed['s0'])
    out['ee'] = readout(mEE, τBase, ee, workweekData, hbarRef)
    return out
