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
    'ρTable':     [0.8, 1.0, 2.0],   # rows the funcOfRho table prints uncommented
    'rule':       'match',  # b^0 = b^refType
    'refType':    1,
    # Grid settings. calibrateRhoGrid.py gives BOTH solvers interpKind/smoothKnots and only the grid
    # SIZES to CRRA; LOG keeps its own documented nι=50. Anything re-solving a calibrated instance must
    # mirror that split or it solves under a different interpolant than it was fitted under
    # (notes/informalSavings_resolvedIssues.md). loadCalibrated() enforces it; do not bypass.
    'gridSettings': {'interpKind': 'cubic', 'smoothKnots': 4, 'nι': 45, 'ns': 45},
}

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
    return {'dates': {i: int(d) for i, d in enumerate(dates)},
            't0': int(list(dates).index(dfc['Calibration year'])),
            'year0': int(dfc['Calibration year']),
            'workweek': float(dfc['Average workweek']),
            'τ0': float(dfc['Pension tax']),
            's0': float(dfc['Savings rate'])}


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
    # 'UKUS' is the UK workbook regrouped at US income percentiles -- a separate calibration, kept for
    # counterfactual comparability and NOT interchangeable with 'UK' (different RR0, so different theta).
    # It is calibrated and swept, but no paper table reads it yet.
    'extraSweeps': ('UKUS',),
    'gridSettings': {'interpKind': 'linear', 'smoothKnots': 4, 'n': 101, 'ns': 150,
                     'verify': 225, 'verifyN': 151},
    # --- Endogenous system characteristics (app:ESC): the leaded choice of theta under a deadweight
    # wedge on redistributive funds. 'spec' is the paper's headline cost formulation (the wedge scales
    # the whole benefit; f cancels from the replacement-rate ratio, so theta* stays the data's own);
    # 'altSpec' is the benefit-side variant, calibrated and run everywhere as robustness. phi is
    # imposed, p is calibrated per (rho, spec) so the design IN FORCE in 2020 on a freely simulated path
    # is the observed one (ModelESC.leadedDesignAtT0, results/esc/escCalibration{,CRRA}.csv). The
    # counterfactual tables report at t0: every scenario is a new equilibrium path whose political choice
    # binds from the first period, so 2020's design is an outcome and already carries the response.
    # (The superseded convention -- an unanticipated 2020 reform with the design pinned through 2020 --
    # had to report t0+1; results/esc/preNewPath/ holds those csvs.)
    'esc': {
        'spec':      'scale',
        'altSpec':   'flat',
        'phi':       0.5,
        'ρTable':    [0.5, 1.0, 2.0],
        # escExperiments.csv scenario keys -> the labels the appendix tables print.
        'scenarios': {'acute': 'Acute ageing', 'frIncome': 'Income distribution',
                      'frLeisure': 'Leisure preferences', 'frVoting': 'Voting',
                      'frAll': 'All French characteristics'},
    },
}

# Which sweep csv belongs to which country and calibration variant. The US is calibrated on its own
# (calibrateRhoGrid.py); FR/UK/UKUS impose the US beta and are swept by calibrateRhoGridEU.py.
def usSweepCsv(country, commonX = False):
    tag = ('US_rhoGrid' if country == 'US' else country + '_rhoGrid') + ('CommonX' if commonX else '')
    return os.path.join(CALIBDIR, tag + '.csv')


def usInstanceDir(country, commonX = False):
    return os.path.join(CALIBDIR, 'instances' + ('US' if country == 'US' else country)
                        + ('CommonX' if commonX else ''))


@functools.lru_cache(maxsize = None)
def usCalendar(country = 'US'):
    """ {model t index: calendar year}, the calibration year, and the observed workweek, from `country`'s
    workbook. Mirrors python/US/test.py and testEU.py: the population sheet's dates extended by t_ss = 3
    further 30-year steps, of which only the dated part is returned.

    Read from the workbook rather than from a pickled instance for the same reason ARG's calendar is:
    calibratePoint pickles an instance that never saw db['dates']. On a shock COPY db['dates'] is worse
    than absent -- it is present and stale (python/US/test_createCopyFromt0.py), which is the other
    reason nothing in this pipeline reads it.

    The UK workbook carries a second calibration sheet for its US-percentile regrouping; `country`
    'UKUS' selects it. """
    base, sheet = (country[:2], 'calibrationUS') if country == 'UKUS' else (country, 'calibration')
    wb = pd.read_excel(os.path.join(DATA, US['workbooks'][base]), sheet_name = None, header = None)
    dft = pd.DataFrame(wb['population'].values)
    dates = pd.DataFrame(dft.iloc[1:, ].values, columns = dft.iloc[0, :]).set_index('t').index
    dfc = pd.DataFrame(wb[sheet].values)
    dfc = pd.Series(dfc.iloc[1, :].values, index = dfc.iloc[0, :].values)
    return {'dates': {i: int(d) for i, d in enumerate(dates)},
            't0': int(list(dates).index(dfc['Calibration year'])),
            'year0': int(dfc['Calibration year']),
            'workweek': float(dfc['Average workweek']),
            'τ0': float(dfc['Pension tax']),
            'RR0': float(dfc['Replacement rate'])}


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


def num(x, digits = 2):
    return '{:.{d}f}'.format(x, d = digits)


def vec(x, digits = 1):
    """ [1.03, 1.45] -> '[1.0, 1.5]', the form the calibration table already uses. """
    return '[' + ', '.join('{:.{d}f}'.format(v, d = digits) for v in x) + ']'
