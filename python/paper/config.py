r""" Paths, the Argentina specification, and the unit conversions shared by all three pipeline stages.

This module imports nothing from the model. Stage (iii) must stay able to rebuild every table and figure
from `results/` alone, in seconds and without unpickling a model instance -- see README.md.
"""
import os, functools
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))

DATA      = os.path.join(REPO, 'data')
RESULTS   = os.path.join(REPO, 'results')
CALIBDIR  = os.path.join(RESULTS, 'calibration')
INSTDIR   = os.path.join(CALIBDIR, 'instances')
SHOCKDIR  = os.path.join(RESULTS, 'shocks')
SWEEPDIR  = os.path.join(RESULTS, 'sweeps')
ESCDIR    = os.path.join(RESULTS, 'esc')
NUMDIR    = os.path.join(RESULTS, 'numerical')      # pre-publication numerical checks (stationary vs
                                                    # date-specific policy functions), no paper output
PAPERDIR  = os.path.join(RESULTS, 'paper')          # stage (iii) writes here first
PAPERTEX  = os.path.join(REPO, 'writing', 'Paper')  # ... then copies here unless --no-copy

MODELDIR  = os.path.join(REPO, 'python', 'InformalSavings')
USDIR     = os.path.join(REPO, 'python', 'US')
PYTHON    = os.path.join(REPO, '.venv', 'Scripts', 'python.exe')

# ---------------------------------------------------------------------------------------------------
# The Argentina specification: what the paper's numbers are, as a declaration rather than as CLI history.
# Stages (i) and (ii) pass these to the experiment scripts; changing a paper number starts here.
# ---------------------------------------------------------------------------------------------------
ARG = {
    'workbook':   'ArgentinaTest.xlsx',
    'ρGrid':      [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0],
    'ρAnchor':    1.0,      # the sole LOG point; calibrateGrid marches outward from it
    'ρBaseline':  1.0,      # the paper's headline specification
    'ρTable':     [0.5, 1.0, 2.0],   # rows the funcOfRho table prints uncommented; the rest are
                                     # emitted commented. Matches US['ρTable'], so both arms of the
                                     # paper show the same three points of their rho grids
    'rule':       'match',  # b^0 = b^refType
    'refType':    1,
    # The anchor's starting (beta, omega, eta0, X0). The march seeds every other point from its history,
    # but the anchor starts from test.py's defaults (beta = 0.6, omega = 2), and at alpha = 0.35 those put
    # the informal steady state outside the net-saver region, so the iota state grid is degenerate before
    # the root takes a step. This is the vector-X solution at rho = 1 for alpha = 0.35, K/Y = 3.23 and the
    # GDP-based tax target (model.taxTarget, tau0 = 0.1181), z_0 relative to the formal average
    # (test_calibrationGrid.py, 2026-10-23); retune it if the capital share, the spending share, the K/Y
    # target or the household-survey targets move.
    'anchorGuess': {'β': 0.668641, 'ω': 1.496254, 'η0': 0.285587, 'X0': 0.373999},
    # Grid settings. calibrateRhoGrid.py gives BOTH solvers interpKind/smoothKnots and only the grid
    # SIZES to CRRA; LOG keeps its own documented nι=50. Anything re-solving a calibrated instance must
    # mirror that split or it solves under a different interpolant than it was fitted under
    # (archive/notes/informalSavings_resolvedIssues.md). loadCalibrated() enforces it; do not bypass.
    'gridSettings': {'interpKind': 'cubic', 'smoothKnots': 4, 'nι': 45, 'ns': 45},
    # WHICH CALIBRATION VARIANT THE ARGENTINA OUTPUTS LEAD WITH (as US['commonX']). False: vector X_i
    # from relative income and relative hours; True: one scalar X across the formal types pinned by the
    # formal workweek, relative formal hours a prediction. X enters no aggregate, so tau, K/Y, the
    # savings rate and every counterfactual coincide across the two to solver precision (measured at
    # <= 4e-12 over the whole rho grid, archive/notes/argentina_commonX_vs_vectorX.md); what differs is the
    # calibration table (eta_i, X_i, eta_0, X_0) and the relative-hours diagnostic. The headline outputs
    # read this; their twins pass commonX = not this.
    # Common X, matching the OECD arm: it identifies one leisure parameter
    # rather than four, puts the workweek level on a target, and turns relative formal hours into a
    # prediction to be checked against the survey.
    'commonX': True,
}


def argVariantTag(commonX = False):
    """ The file-name suffix of the Argentina variant's results: '' (vector X) or '_commonX'. """
    return '_commonX' if commonX else ''


def argSweepCsv(commonX = False):
    return os.path.join(CALIBDIR, 'informalSavings_rhoGrid' + ('CommonX' if commonX else '') + '.csv')


def argInstanceDir(commonX = False):
    return os.path.join(CALIBDIR, 'instances' + ('CommonX' if commonX else ''))


def argShockTemplate(scenario, rule = None, commonX = False):
    """ The shock csv name template of one scenario ('reform' | 'ee' | 'flat'), with {ρ} left open. """
    rule = rule or ARG['rule']
    stem = {'reform': 'universal_' + rule, 'ee': 'eeOnly_' + rule, 'flat': 'universal_flat'}[scenario]
    return stem + '_rho{ρ:.4f}' + argVariantTag(commonX) + '.csv'


def argEpsThetaCsv(ρ, commonX = False):
    return os.path.join(SWEEPDIR, 'epsThetaGrid_rho{:.4f}{}.csv'.format(ρ, argVariantTag(commonX)))

# ---------------------------------------------------------------------------------------------------
# Calendar and units
# ---------------------------------------------------------------------------------------------------
# The pickled instances do NOT carry db['dates'] or db['workweek'] -- test.py sets them on its own
# mLOG, and calibratePoint pickles an instance that never saw them. Both are re-read from the workbook.


@functools.lru_cache(maxsize = None)
def calendar():
    """ {model t index: calendar year} and the calibration year's index, from the workbook.
    Mirrors test.py's construction: the population sheet's dates, extended by t_ss=3 further 30-year
    steps. Only the dated part is returned -- the steady-state tail has no calendar meaning. """
    wb = pd.read_excel(os.path.join(DATA, ARG['workbook']), sheet_name = None, header = None)
    dft = pd.DataFrame(wb['population'].values)
    dates = pd.DataFrame(dft.iloc[1:, ].values, columns = dft.iloc[0, :]).set_index('t').index
    dfc = pd.DataFrame(wb['calibration'].values)
    dfc = pd.Series(dfc.iloc[1, :].values, index = dfc.iloc[0, :].values)
    τ0, y = argTaxTarget(wb)
    return {'dates': {i: int(d) for i, d in enumerate(dates)},
            't0': int(list(dates).index(dfc['Calibration year'])),
            'year0': int(dfc['Calibration year']),
            'workweek': float(dfc['Average workweek']),
            # Derived as in test.py (model.taxTarget), never a literal tax rate.
            'τ0': τ0, 'yInformal': y,
            'α': float(dfc['Capital income share']),
            'spending': float(dfc['Pension spending']),
            's0': float(dfc['Savings rate'])}


def argTaxTarget(wb):
    """ (tau0, y) from the workbook `wb` (pd.read_excel's dict of sheets): eq (calibration:tau)'s target, pension
    spending over GDP with GDP formal plus informal output and y the informal share of GDP. The closed form of
    python/InformalSavings/model.py's taxTarget, restated because this module imports nothing from the model,
    on test.py's inputs: a = gamma_0 z_0^eta (1-alpha), z_0^eta the informal income over the population-weighted
    formal mean, tau0 = spending (1+a)/((1-alpha) + spending a), y = a(1-tau0)/(1+a(1-tau0)).
    datasets.calibrationSummary checks tau0 against the calibrated tax. """
    dfc = pd.DataFrame(wb['calibration'].values)
    dfc = pd.Series(dfc.iloc[1, :].values, index = dfc.iloc[0, :].values)
    dfj = pd.DataFrame(wb['heterogeneity'].values)
    dfj = pd.DataFrame(dfj.iloc[1:, ].values, columns = dfj.iloc[0, :])
    γ, inc = dfj['Population shares'].values.astype(float), dfj['Income'].values.astype(float)
    z0η = inc[0]/np.average(inc[1:], weights = γ[1:])
    S, α = float(dfc['Pension spending']), float(dfc['Capital income share'])
    a = γ[0]*z0η*(1-α)
    τ0 = S*(1+a)/((1-α) + S*a)
    return τ0, a*(1-τ0)/(1 + a*(1-τ0))


# ---------------------------------------------------------------------------------------------------
# The US/France/UK specification. Same role as ARG above: a declaration of what the paper's rich-OECD
# numbers are, not a second implementation. See python/US/README.md for the model and the protocol.
# ---------------------------------------------------------------------------------------------------
US = {
    'countries':  ('US', 'FR', 'UK'),        # the columns of USUKFRCalibration, in the paper's order
    'workbooks':  {'US': 'USMain_test.xlsx', 'FR': 'FRMain.xlsx', 'UK': 'UKMain.xlsx'},
    'ρGrid':      [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0],
    'ρAnchor':    1.0,                        # the sole LOG point, and the sweeps' march anchor
    'ρBaseline':  1.0,                        # the headline specification: the LOG tables
    'ρTable':     [0.5, 1.0, 2.0],            # the rows the CRRA tables print
    # READINGS of the U.S. workbook that are a switch rather than a sheet: name -> the driver flags of
    # python/US/calibrateRhoGrid.py and runShocksUS.py. 'USMedicare' is the online appendix's 'transfers to
    # the old': Medicare spending, 2.9% of GDP (MedPAC 2020 Data Book, data/README.md; the workbook's
    # pre-2026-10-23 value), added to pension spending in tau0 and paid as a flat benefit, so theta =
    # (1 - m) theta_P with m = 2.9/(7.366 + 2.9) (python/US/test.reading). Swept and shocked like the US,
    # with France referenced to it; usCalendar derives its tau0 from the workbook's.
    'readings': {'USMedicare': {'medicare': 0.029}},
    # WHICH CALIBRATION VARIANT THE PAPER LEADS WITH. True = the common scalar X of the docs' variant B,
    # where the hours unit is a calibration target and relative hours become a prediction; False = the
    # vector X_i of variant A, where relative hours are data and the LEVEL of hbar is not identified.
    # beta, omega, tau, R, the savings rate and aggregate h are the SAME under both (block recursivity,
    # measured to ~1e-13 down the sweeps) -- what the choice changes is eta, X, and therefore every
    # counterfactual defined THROUGH eta or X: the French income-distribution and leisure rows.
    # The headline tables and figures read this; their vector-X twins pass commonX = not this.
    'commonX': True,
    # gradKnotSpacing is recorded, not forwarded (python/US/policy.CRRA's default): the distance in tau between
    # the knots of the least-squares cubic in ln(1 - tau) the CRRA tau-derivatives are taken from. Appendix
    # D's residual table (tablesHorizon.numResiduals) prints it.
    'gridSettings': {'interpKind': 'linear', 'smoothKnots': 4, 'n': 101, 'ns': 150,
                     'verify': 225, 'verifyN': 151, 'gradKnotSpacing': 0.04},
    # --- Endogenous system characteristics (sec:esc): the leaded choice of theta under a deadweight
    # cost on the pension system (python/US/base.py fWedge, writing/US/model_esc.tex). Every spec is
    # PROPORTIONAL -- the cost scales the whole benefit and cancels from the replacement-rate ratio, so
    # theta* stays the data's own -- and its one parameter is calibrated per rho so the design IN FORCE in
    # 2020 on a freely simulated path is the observed one (ModelESC.leadedDesignAtT0,
    # results/esc/escCalibration{,CRRA}.csv). The counterfactual tables report at t0: every scenario is a
    # new equilibrium path whose political choice binds from the first period, so 2020's design is an
    # outcome and already carries the response. The ESC leg runs under the headline variant, US['commonX'].
    #   'size'  (the paper's): f(theta, tau) = exp(-1/2 lambda tau Vtilde (1-theta)^2), a deadweight cost
    #           quadratic in the implicit tax the flat component levies on each type, scaled by the size of
    #           the system; Vtilde = sum_i gamma_i (y_i-1)^2/y_i. Nothing is lost when nothing is
    #           redistributed. lambda lives in the csvs' `p` column (the paper prints it as lambda).
    #   'scale' (the previous wedge, the online appendix's second cost specification): f(theta) =
    #           phi + (1-phi) theta^p, the cost attached to the design label rather than to the transfer.
    #   'flat'  (only the flat component carries the cost) runs only in the permanent stage's comparison
    #           rows of escPermanent.csv, which no output prints.
    # The rho points of the pre-publication stationary-vs-date-specific check (runShocksUS.py 'stationary';
    # rho = 1 is exact by the LOG decoupling and is not run). sec:numerical's footnote quotes the maximal gap
    # over these points.
    'ρStationary': [0.5, 0.7, 1.3, 1.5, 2.0],
    'esc': {
        'spec':           'size',      # the paper's cost specification
        'comparisonSpec': 'scale',     # the previous wedge, the online appendix's second cost (page C3)
        # phi is a DUMMY KEY under 'size': f does not use it, but every ESC csv is merge-keyed on
        # (spec, phi, commonX) and the readers (runESC.pickCalib, datasets.escRow/escCalibration) filter on
        # it, so the 'size' rows are written and read at 0.5. Under 'scale' it is the imposed floor f(0).
        'phi':            0.5,
        'ρTable':         [0.5, 1.0, 2.0],
        # The scan bracket of the EXACT CRRA calibration (runESCcrra.py --bracket), per spec and rho: the
        # required parameter falls steeply in rho, so one bracket cannot serve both. A rho absent from a
        # spec's dict leaves the bracket to runESCcrra.py's own default for that spec; a rho present with
        # None is a PLACEHOLDER and stage (i) refuses to run it (config.escBracket). 'scale' keeps the
        # child's default (its wide scan narrowed around a path-iteration p on file). 'size': set from the
        # LOG lambda after WP4 -- [lambda/20, 3 lambda] at rho = 2, [lambda/3, 5 lambda] at rho = 0.5.
        # 'sizePiR' (costVariants) the same way from its own LOG lambda; 'scale' from its LOG p, [p, 6p] at
        # rho = 0.5 and [p/20, p] at rho = 2 (the exact p was 2.3 and 0.21 times the LOG one on 2026-09-24).
        # Set 2026-10-23 from the LOG calibration at the pension-only workbook: lambda 11.563954 ('size'),
        # p 0.414608 ('scale'), lambda 20.838898 ('sizePiR').
        # 'scale' at rho = 2: narrowed to the sign change of the 2026-10-23 scan, whose node 0.0687 does not solve
        # on the ns = 50 grid, and brentq to 1e-6 (xtol): p is ~0.09 there, so 2e-5 left the design 1.8e-4 off.
        'bracket':        {'scale':   {0.5: (0.4146, 2.488), 2.0: (0.0377, 0.1251)},
                           'size':    {0.5: (3.855, 57.82), 2.0: (0.5782, 34.69)},
                           # 'sizePiR': lambda_size,CRRA/pi_2020 within a factor of 1.4 (the LOG ratio is
                           # 0.999), scanned at ns2D (costVariants' nsScan: the ns = 50 tax solve has jumps of
                           # ~1e-5 in tau at rho = 2 that stop the (beta, omega) root and the pi iteration)
                           'sizePiR': {0.5: (30.0, 70.0), 2.0: (3.2, 8.0)}},
        # brentq's xtol on the cost parameter where runESCcrra.py's default (2e-5) is too coarse, per spec and rho.
        'xtol':           {'scale': {2.0: 1e-6}},
        # THE PUBLISHED CRRA METHOD. True: every CRRA ESC output is built from rows with method = 'exact'
        # (LeadedCRRA2D, python/US/runESCcrra.py --exact, the pre-publication part of stages (i)/(ii))
        # and a missing exact row is MissingInput -- never a fallback to the path iteration's rows, which
        # stay on disk under method = 'path' as the cross-check they are. False builds from the path rows.
        'exact':     True,
        'ns2D':      150,      # savings-state grid of the exact recursion (its choice is insensitive to it)
        'nsScan':    50,       # the coarse grid the wedge calibration SCANS on before refining at ns2D
        # The candidate grid for θ_{t+1}. The objective is flat near its maximum (1e-5 in W over ±0.01 in
        # θ at the frVoting choice, rho = 2), so this grid sets the resolution of the printed design: 13
        # nodes gave 0.285, 21 gave 0.273 (2026-09-11).
        'nCand2D':   41,
        # The design layer of the exact recursion (runESCcrra.py --designRule/--Ma): algorithm esc:crra2D of
        # writing/US/num_esc.tex, the root in a, adopted on the pilot (python/US/RESEARCH_LOG.md, 2026-10-02).
        'designRule': 'root',
        'Ma':         5,
        # The pre-publication timing checks: the permanent choice traced in rho under CRRA.
        'ρPermanentCRRA': [1.1, 1.2, 1.3, 1.4, 1.5, 2.0],
        # The UK's OWN cost parameter per rho (the deep test, UK_ESC_Calibration), calibrated as the US one is:
        # LOG from escCountry.csv ('own'), CRRA by the exact recursion into escCalibrationCRRAUK.csv (stage (i)
        # --prepub, runESCcrra.py --host UK --stage calib). Brackets set from coarse probes (2026-09-29): the
        # UK's design is 0.23/0.57 at lambda 1.45/3.0 (rho = 2) and 0.46/0.71 at 12/25 (rho = 0.5). nsScan 0 at
        # rho = 0.5 scans at ns2D: the UK's (beta-imposed) calibration does not converge on the ns = 50 grid
        # there. Rescaled 2026-10-23 by the UK's LOG lambda at the pension-only workbooks (7.786 against 7.264)
        # and widened: the exact lambda was 2.08 and 0.38 times the LOG one.
        'uk': {'bracket':   {0.5: (11.5, 30.0), 2.0: (1.4, 5.5)},
               'nsScan':    {0.5: 0, 2.0: 50},
               'nScan':     4},
        # THE COST VARIANTS OF SECTION 7 (A8 of archive/notes/reviewResponse_2026-10/paper_reviewResponse.md): the ageing counterfactuals
        # under the paper's cost, the cost on the design (comparisonSpec) and the Pi-inclusive cost 'sizePiR'
        # (python/US/modelESC.py: lambda*Pi_t/R_t, the factor the paper's cost absorbs into lambda, solved to
        # the path's own Pi_t/R_t), at every rho of ρTable, both readings. 'sizePiR' is calibrated like the
        # paper's cost and runs, with mild ageing under the other two at rho != 1, into the `tag`ged csvs
        # (escCalibration{,CRRA}Costs, escPath{,CRRA}Costs, escShocks{,CRRA}Costs; mild ageing under the
        # other two costs at rho != 1 in escShocksCRRACostsMild, its own file so the two runs never write one
        # csv at once); collectESCexperiments.py --costs merges them with the paper's csvs into
        # escAgeingCosts.csv.
        'costVariants': {'spec': 'sizePiR', 'tag': 'Costs', 'scenarios': ['baseline', 'mild', 'acute'],
                         'mildSpecs': ['size', 'scale'], 'mildTag': 'CostsMild',
                         # the exact CRRA calibration: three scan nodes on the narrow bracket, on the ns2D grid,
                         # brentq to 1e-3 in lambda (~1e-5 in the design); each node is two to three recursions
                         'nScan': 3, 'nsScan': 0, 'xtol': 1e-3},
        # escExperiments.csv scenario keys -> the labels the appendix tables print.
        # 'frLeisure' is run and merged but no longer printed (dropped from the paper 2026-09-11).
        'scenarios': {'acute': 'Acute ageing', 'frIncome': 'Income distribution',
                      'frVoting': 'Voting', 'frAll': 'All French characteristics'},
    },
    # THE CROSS-COUNTRY TEST (python/US/runOECD26.py, results/oecd26/), the one place its paper variant lives:
    # the builders (tablesOECD26.PAPER, figuresOECD26) and the readers (datasets.oecd26*) default to it, and
    # runOECD26.py's --spec/--betaRule defaults are read from here.
    #   spec      the cost transported from the U.S. anchor: 'sizePiR' (lambda_i = epsilon Pi_i/R_i, epsilon
    #             the U.S. one), 'size' (lambda itself), 'none' (no cost)
    #   betaRule  'common' (the U.S. beta in every country) | 'commonR' (each country's beta set so that its
    #             2020 return is the U.S. anchor's)
    #   turnout   'cps' (the U.S. CPS propensities in every country) | 'cses' (each country's own)
    #   reading   the model's design: 'inForce' (in force in 2020, chosen in 1990) | 'chosen' (chosen in 2020)
    #   spendingSpec  the cost of section 6's spending test at the observed designs
    # `variants`: the runs stage (ii)'s entry 'oecd26' makes, one runOECD26.py command each, in this order (an
    # anchor before the layers that read it); rows already current are reused, so a rerun costs seconds.
    'oecd26': {
        'spec': 'sizePiR', 'betaRule': 'common', 'turnout': 'cps', 'reading': 'inForce', 'spendingSpec': 'none',
        'variants': [
            {'spec': ['size', 'sizePiR'], 'betaRule': ['common'], 'turnout': ['cps', 'cses'],
             'stage': ['anchor', 'layer1', 'layer2']},
            {'spec': ['none'], 'betaRule': ['common'], 'turnout': ['cps', 'cses'],
             'stage': ['anchor', 'layer1', 'layer2']},
            {'spec': ['size', 'sizePiR'], 'betaRule': ['commonR'], 'turnout': ['cps', 'cses'],
             'stage': ['layer1', 'layer2']},
        ],
    },
}

def escBracket(ρ, spec = None):
    """ The exact CRRA calibration's scan bracket at `rho` under `spec` (US['esc']['spec'] by default):
    (lo, hi) to pass as runESCcrra.py --bracket, or None to leave the child its own default. Raises on a
    placeholder (rho listed with None) so an unset bracket stops stage (i) before a 45-minute scan. """
    spec = US['esc']['spec'] if spec is None else spec
    table = US['esc']['bracket'].get(spec, {})
    hit = [table[k] for k in table if np.isclose(float(k), ρ)]
    if not hit:
        return None
    if hit[0] is None:
        raise ValueError("config.US['esc']['bracket'][{!r}][{}] is a placeholder: set it from the LOG "
                         "calibration before running the exact CRRA calibration".format(spec, ρ))
    lo, hi = hit[0]
    return float(lo), float(hi)


# Which sweep csv belongs to which country and calibration variant. The US is calibrated on its own
# (calibrateRhoGrid.py); FR/UK impose the US beta and are swept by calibrateRhoGridEU.py.
def usSweepCsv(country, commonX = False):
    tag = ('US_rhoGrid' if country == 'US' else country + '_rhoGrid') + ('CommonX' if commonX else '')
    return os.path.join(CALIBDIR, tag + '.csv')


def usInstanceDir(country, commonX = False):
    return os.path.join(CALIBDIR, 'instances' + ('US' if country == 'US' else country)
                        + ('CommonX' if commonX else ''))


def usShockCsv(host = 'US', commonX = False):
    """ python/US/runShocksUS.py's long csv for `host` ('US' | 'USMedicare', the reading) and variant. """
    return os.path.join(SHOCKDIR, host + '_shocks' + ('CommonX' if commonX else '') + '.csv')


@functools.lru_cache(maxsize = None)
def usCalendar(country = 'US'):
    """ {model t index: calendar year}, the calibration year, and the observed workweek, from `country`'s
    workbook. Mirrors python/US/test.py and testEU.py: the population sheet's dates extended by t_ss = 3
    further 30-year steps, of which only the dated part is returned.

    Read from the workbook rather than from a pickled instance for the same reason ARG's calendar is:
    calibratePoint pickles an instance that never saw db['dates']. On a shock COPY db['dates'] is worse
    than absent -- it is present and stale (python/US/test_createCopyFromt0.py), which is the other
    reason nothing in this pipeline reads it.

    A reading (US['readings']) is the US workbook with tau0 derived as python/US/test.reading derives it. """
    if country in US['readings']:
        cal = dict(usCalendar('US'))
        S, M = cal['τ0']*(1 - cal['α']), US['readings'][country]['medicare']
        return cal | {'τ0': (S + M)/(1 - cal['α']), 'Ushare': M/(S + M)}
    wb = pd.read_excel(os.path.join(DATA, US['workbooks'][country]), sheet_name = None, header = None)
    dft = pd.DataFrame(wb['population'].values)
    dates = pd.DataFrame(dft.iloc[1:, ].values, columns = dft.iloc[0, :]).set_index('t').index
    dfc = pd.DataFrame(wb['calibration'].values)
    dfc = pd.Series(dfc.iloc[1, :].values, index = dfc.iloc[0, :].values)
    return {'dates': {i: int(d) for i, d in enumerate(dates)},
            't0': int(list(dates).index(dfc['Calibration year'])),
            'year0': int(dfc['Calibration year']),
            'workweek': float(dfc['Average workweek']),
            'τ0': float(dfc['Pension tax']),
            'RR0': float(dfc['Replacement rate']),
            'α': float(dfc['Capital income share'])}


# ---------------------------------------------------------------------------------------------------
# The two US calibration variants, as they appear in an output's identity and in its table note.
#
# The variant US['commonX'] names is the HEADLINE: its outputs keep the plain names and tex labels the
# paper already \ref{}s, so switching which variant leads never renames the outputs the draft cites --
# it changes what they contain. The other variant is the robustness twin, and its name and label carry
# ITS OWN variant rather than the word "alternative", so a file on disk says what is in it.
#
# The printed note is keyed on commonX, not on which variant leads: the paper's tables and figures are
# the common-X calibration and say nothing about it, and only a vector-X table names itself.
# ---------------------------------------------------------------------------------------------------
def isLead(commonX, arm = 'US'):
    """ Is `commonX` the headline variant of `arm` ('US' | 'ARG')? """
    return bool(commonX) == bool((US if arm == 'US' else ARG)['commonX'])


def variantSuffix(commonX, arm = 'US'):
    r""" '' for the headline variant, '_commonX'/'_vectorX' for the twin. Appended to an output's name,
    its tex filename and its \label. """
    return '' if isLead(commonX, arm) else ('_commonX' if commonX else '_vectorX')


def variantCaption(commonX, arm = 'US'):
    """ The caption tail that marks a twin. Empty for the headline -- its caption is the paper's own. """
    return '' if isLead(commonX, arm) else (r' (common $X$ calibration)' if commonX
                                            else r' (vector $X_i$ calibration)')


def variantNote(commonX, full = False, arm = 'US'):
    r""" One sentence naming the calibration variant, appended to a VECTOR-X table's note.

    Empty under common X, which is what the paper is: every table and figure in the main text is the
    common-X calibration, so none of them says so, and only the vector-X twins in the appendices carry a
    label. The vector-X calibration table (`full = True`) spells the variant out; every other vector-X
    table names it and points at that table's note. """
    if commonX:
        return ''
    calib = r'table:US:Calib' if arm == 'US' else r'table:Arg:Calib'
    if not full:
        return (r' Vector-$X_i$ calibration: see the note to '
                r'table~\ref{' + calib + variantSuffix(commonX, arm) + '}.')
    return (r' Vector-$X_i$ calibration: $X_i$ is identified from relative hours, which are data here, '
            r'and the level of $\bar h$ is then not identified --- only its ratio to the baseline is. '
            r'$\beta$, $\omega$, the tax rate and the savings rate are common to the two variants; what '
            r'differs is anything defined through $\eta$ or $X$.')


def workweekHours(h, hRef):
    """ Aggregate hours h_t -> an average workweek in hours, by NORMALISATION against `hRef`.

    `h` has no well-defined scale in the model, so no expression converts it to hours on its own. The
    observed average workweek is a REFERENCE POINT instead: the calibrated model's hours at the
    calibration year are defined to be `workweek` hours, and any other h is reported as
    `workweek * h/hRef`. Pass the calibrated baseline's own h at t0 as `hRef` -- per rho, since each rho
    is separately calibrated. The baseline then reads 42.54 at every rho by construction, and a shocked
    h is read as the change in hours it implies.

    NOT `h * 7 * 12`. That inverts test.py's `h0 = workweek/(7*12)`, which is how the PRE-DETERMINED
    period's hours are fed in as a model input; it is not a scale the solved h_t inherits, and using it
    to report makes the baseline miss 42.54 and manufactures a spread across rho out of a free
    normalisation. """
    return calendar()['workweek'] * np.asarray(h, dtype = float) / hRef


def pct(x, digits = 2):
    r""" 0.1256 -> '12.56\%'. The escaped percent is what goes into a tex cell. """
    return r'{:.{d}f}\%'.format(100*x, d = digits)


def pp(x, digits = 2):
    r""" A CHANGE in a rate, 0.0014 -> '$+0.14$ p.p.', -0.0158 -> '$-1.58$ p.p.'. Math mode so the
    minus is a minus rather than a hyphen. A change that rounds to zero prints unsigned ('0.00 p.p.')
    rather than as '-0.00': the sign of a solver residual is not a result. """
    v = round(100*x, digits)
    if v == 0:
        return '{:.{d}f} p.p.'.format(0., d = digits)
    return '${:+.{d}f}$ p.p.'.format(v, d = digits)


def num(x, digits = 2):
    return '{:.{d}f}'.format(x, d = digits)


def vec(x, digits = 1):
    """ [1.03, 1.45] -> '[1.0, 1.5]', the form the calibration table already uses. """
    return '[' + ', '.join('{:.{d}f}'.format(v, d = digits) for v in x) + ']'
