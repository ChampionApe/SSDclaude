r""" Loaders for everything stage (iii) reads. The only module that knows the results/ file layout and
column names, so a schema change is a one-file edit rather than a hunt through the builders.

Nothing here imports the model. A loader whose input is missing raises MissingInput, which build.py
turns into a skipped output and a line in the report -- an unrun experiment must never look like a
built table.
"""
import os, re, glob, json
import numpy as np, pandas as pd

import config as C

SCENARIOS = {'reform': 'universal_{rule}_rho{ρ:.4f}.csv',   # full effect, taxes re-optimised
             'ee':     'eeOnly_{rule}_rho{ρ:.4f}.csv'}      # taxes held at the baseline path


class MissingInput(Exception):
    """ A required results/ file does not exist. Carries the paths so the report can name them. """
    def __init__(self, paths):
        self.paths = [paths] if isinstance(paths, str) else list(paths)
        super().__init__('missing input(s): '
                         + ', '.join(os.path.relpath(p, C.REPO) for p in self.paths))


def _need(path):
    if not os.path.exists(path):
        raise MissingInput(path)
    return path


def calibrationSummary():
    """ The one-row record runCalibration.py writes. Vector entries are JSON in the csv and come back
    as lists of float. """
    df = pd.read_csv(_need(os.path.join(C.PAPERDIR, 'calibrationSummary.csv')))
    rec = df.iloc[0].to_dict()
    for k in ('ν', 'ηi', 'Xi', 'γi'):
        if isinstance(rec.get(k), str):
            rec[k] = json.loads(rec[k])
    return rec


def rhoGrid():
    """ The calibration sweep, one row per rho, deduplicated on rho keeping the last (the file is
    appended to across resumed marches). """
    df = pd.read_csv(_need(os.path.join(C.CALIBDIR, 'informalSavings_rhoGrid.csv')))
    return df.drop_duplicates('ρ', keep = 'last').sort_values('ρ').reset_index(drop = True)


def shockPath(ρ, scenario = 'reform', rule = None):
    """ One rho's full response path, indexed on the model's own t with t0 first. """
    rule = rule or C.ARG['rule']
    return pd.read_csv(_need(os.path.join(C.SHOCKDIR, SCENARIOS[scenario].format(ρ = ρ, rule = rule))),
                       index_col = 0)


def shockAtPeriod(period = 0, scenario = 'reform', rule = None, ρGrid = None):
    """ One row per rho, at `period` periods after t0 (0 = the impact period, the paper's year 2010).

    The row is taken POSITIONALLY (iloc), not by label: each csv is already indexed on the model's own
    t starting at t0, so period is an offset into that. Every rho in the grid must be present -- a
    partial sweep is raised on rather than silently plotted as a shorter curve. """
    ρGrid = C.ARG['ρGrid'] if ρGrid is None else ρGrid
    rule = rule or C.ARG['rule']
    paths = {ρ: os.path.join(C.SHOCKDIR, SCENARIOS[scenario].format(ρ = ρ, rule = rule)) for ρ in ρGrid}
    lack = [p for p in paths.values() if not os.path.exists(p)]
    if lack:
        raise MissingInput(lack)
    rows = []
    for ρ, p in paths.items():
        df = pd.read_csv(p, index_col = 0)
        if period >= len(df):
            raise MissingInput(p + ' (has {} periods, need offset {})'.format(len(df), period))
        r = df.iloc[period].to_dict()
        r['ρ'] = ρ
        rows.append(r)
    return pd.DataFrame(rows).sort_values('ρ').reset_index(drop = True)


def epsThetaGrid(ρ = None):
    """ The Cartesian (eps, theta) grid at the calibration year, one row per pair.

    Checked to be a COMPLETE rectangle before it is returned. figures.argLogFourInOne pivots this into
    an eps x theta matrix and fills between adjacent theta columns; a missing pair becomes a NaN in the
    matrix and fill_between drops that span silently, so a partially-resumed sweep would render as a
    figure with holes rather than as an error. """
    ρ = C.ARG['ρBaseline'] if ρ is None else ρ
    path = _need(os.path.join(C.SWEEPDIR, 'epsThetaGrid_rho{:.4f}.csv'.format(ρ)))
    df = pd.read_csv(path)
    nε, nθ = df['eps'].nunique(), df['theta'].nunique()
    if len(df) != nε * nθ:
        raise MissingInput('{} (incomplete grid: {} rows for {} eps x {} theta)'.format(
            path, len(df), nε, nθ))
    return df


# ---------------------------------------------------------------------------------------------------
# Derived quantities the csvs do not carry
# ---------------------------------------------------------------------------------------------------
def savingsRate(s, s_, h, α, ν):
    """ Eq (calibration): s_t / ((s_{t-1}/nu_t)^alpha h_t^(1-alpha)). The same expression as
    base.py's Base.savingsRate, restated here so stage (iii) needs no model import -- if that
    equation ever changes, both must move. """
    return s / ((s_/ν)**α * h**(1-α))


def seedSavings(ρ, rule = None, tol = 1e-6):
    """ s_{t0-1}, the savings level entering the reform year. Common to every scenario, because the
    reform is unanticipated: the seed state is the baseline's in all of them.

    No shock csv carries it -- it is a state, not a row -- so it is recovered two ways and they check
    each other:

      * from the eeOnly csv's `s__base`, which reports the seed directly, when that file exists;
      * by inverting eq (calibration) at t0, where the baseline savings rate is a CALIBRATION TARGET
        and so is known exactly: sr = s/((s_/nu)^alpha h^(1-alpha)) solved for s_. The achieved sr is
        read off the sweep csv rather than assumed to be 0.184, so this stays exact at the solver's own
        precision rather than at the target's.

    The inversion is what keeps every figure buildable before the eeOnly experiment has been run; the
    agreement check is what keeps it honest once it has. """
    ref  = shockPath(ρ, 'reform', rule)
    grid = rhoGrid()
    row  = grid.loc[np.isclose(grid['ρ'], ρ)]
    if row.empty:
        raise MissingInput('rho={} absent from informalSavings_rhoGrid.csv'.format(ρ))
    cal  = calibrationSummary()
    α, ν = cal['α'], np.asarray(cal['ν'], dtype = float)[C.calendar()['t0']]
    sr, s, h = float(row['sr'].iloc[-1]), float(ref['s_base'].iloc[0]), float(ref['h_base'].iloc[0])
    inverted = ν * (s / (sr * h**(1-α)))**(1/α)

    path = os.path.join(C.SHOCKDIR, SCENARIOS['ee'].format(ρ = ρ, rule = rule or C.ARG['rule']))
    if os.path.exists(path):
        reported = float(pd.read_csv(path, index_col = 0)['s__base'].iloc[0])
        if abs(reported/inverted - 1) > tol:
            raise ValueError('seed savings disagree at rho={}: eeOnly csv {!r} vs eq(calibration) '
                             'inversion {!r} ({:.2e} relative). One of the two runs is stale.'
                             .format(ρ, reported, inverted, abs(reported/inverted - 1)))
        return reported
    return inverted


def baselineHours(ρ, rule = None):
    """ The calibrated baseline's aggregate hours at t0, for this rho: the reference point that
    config.workweekHours normalises against. Per rho, because each rho is separately calibrated and h is
    not one of the four targets -- so its level differs across the grid even though tau and the savings
    rate do not. Normalising each rho against its own baseline is what makes the pre-reform workweek
    42.54 everywhere and the reform rows comparable. """
    return float(shockPath(ρ, 'reform', rule)['h_base'].iloc[0])


def savingsRatePath(ρ, which = 'reform', rule = None):
    """ The savings rate over the whole reported path. `which` is a column suffix: 'base', 'reform'
    (shockUniversal's csv) or 'ee' (shockEEOnly's).

    The lag is the previous row of the same path, except at t0 where it is the seed state -- see
    seedSavings. The terminal period is NaN by construction (s_T = 0), and is left NaN rather than
    zero-filled: a zero there would plot as a real collapse. """
    df   = shockPath(ρ, 'ee' if which == 'ee' else 'reform', rule)
    cal  = calibrationSummary()
    α, ν = cal['α'], np.asarray(cal['ν'], dtype = float)
    t0i  = C.calendar()['t0']
    s = df['s_' + which].values.astype(float)
    h = df['h_' + which].values.astype(float)
    s_ = np.concatenate([[seedSavings(ρ, rule)], s[:-1]])
    with np.errstate(divide = 'ignore', invalid = 'ignore'):
        sr = savingsRate(s, s_, h, α, ν[t0i:t0i+len(s)])
    sr[s <= 0] = np.nan                       # terminal period: s_T = 0 is degenerate, not a datum
    return pd.Series(sr, index = df.index)


def reformSavingsRate(ρ, period = 0, rule = None):
    """ The savings rate on the full-effect path at `period` periods after t0. """
    return float(savingsRatePath(ρ, 'reform', rule).iloc[period])


# ---------------------------------------------------------------------------------------------------
# US / France / UK
# ---------------------------------------------------------------------------------------------------

def usCalibrationSummary(commonX = False):
    """ runCalibrationUS.py's one-row-per-country record, keyed by country. Vector entries are JSON in
    the csv and come back as lists of float. """
    df = pd.read_csv(_need(os.path.join(C.PAPERDIR, 'usCalibrationSummary.csv')))
    df = df[df['commonX'].astype(bool) == bool(commonX)]
    if df.empty:
        raise MissingInput(os.path.join(C.PAPERDIR, 'usCalibrationSummary.csv'))
    out = {}
    for rec in df.to_dict('records'):
        for k in ('ηi', 'Xi', 'γi', 'μi', 'ν'):
            if isinstance(rec.get(k), str):
                rec[k] = json.loads(rec[k])
        out[rec['country']] = rec
    return out


def usShocks(pinTheta = False, commonX = False):
    """ python/US/runShocksUS.py's long csv: one row per (rho, family, scenario, effect).

    `effect` is 'baseline' | 'full' | 'ee'. tau and sr are fractions; `workweek` is already in hours,
    normalised against that rho's own baseline inside the experiment script -- stage (iii) must NOT
    re-derive it from hbar, which has no scale under vector X (see python/US/shocks.py). """
    name = ('US_shocks_pinTheta.csv' if pinTheta
            else 'US_shocksCommonX.csv' if commonX else 'US_shocks.csv')
    return pd.read_csv(_need(os.path.join(C.SHOCKDIR, name)))


def usShockRow(df, ρ, scenario, effect):
    """ One (rho, scenario, effect) row, raising rather than returning an empty frame -- a silently
    missing scenario would render as a blank table cell instead of a skipped output. """
    hit = df[(np.isclose(df['ρ'], ρ)) & (df['scenario'] == scenario) & (df['effect'] == effect)]
    if hit.empty:
        raise MissingInput('{} (ρ={}, {}, {}) in results/shocks/US_shocks.csv'
                           .format(scenario, ρ, scenario, effect))
    return hit.iloc[-1]


def usBaseline(df, ρ):
    return usShockRow(df, ρ, 'Baseline', 'baseline')


def usSweep(country, commonX = False):
    """ One country's calibration sweep, deduplicated on rho keeping the last. """
    df = pd.read_csv(_need(C.usSweepCsv(country, commonX)))
    return df.drop_duplicates('ρ', keep = 'last').sort_values('ρ').reset_index(drop = True)


# ---------------------------------------------------------------------------------------------------
# Endogenous system characteristics (results/esc/)
# ---------------------------------------------------------------------------------------------------
def escCalibration():
    """ The calibrated deadweight wedge, {(rho, spec): record} with p, thetaStar, beta, omega.

    Two files because two solvers produced them: escCalibration.csv is the LOG case (rho = 1; also
    carries the no-wedge row under spec 'none', keyed here as (1.0, 'none')), escCalibrationCRRA.csv the
    CRRA rows with their own rho column. Only converged rows at config.US['esc']['phi'] are returned --
    an unconverged calibration must surface as a missing key, not as a NaN cell. """
    phi = C.US['esc']['phi']
    out = {}
    log = pd.read_csv(_need(os.path.join(C.ESCDIR, 'escCalibration.csv')))
    for rec in log.to_dict('records'):
        if rec['spec'] == 'none':
            out[(1.0, 'none')] = rec
        elif bool(rec['converged']) and np.isclose(float(rec['phi']), phi):
            out[(1.0, rec['spec'])] = rec
    crra = pd.read_csv(_need(os.path.join(C.ESCDIR, 'escCalibrationCRRA.csv')))
    for rec in crra.to_dict('records'):
        if bool(rec['converged']) and np.isclose(float(rec['phi']), phi):
            out[(float(rec['ρ']), rec['spec'])] = rec
    return out


def escExperiments():
    """ collectESCexperiments.py's merged long csv: one row per (rho, spec, scenario, reading), with the
    design, tax, savings rate and workweek at t0 AND t0+1. `θpinned` True is the exogenous-theta reading
    (design held at the shocked model's own exogenous value), False the endogenous one.

    The t0 columns are what the tables read. Every scenario is a NEW EQUILIBRIUM PATH -- the shocked
    parameters hold over the whole horizon and the political choice binds from the first period -- so
    theta_{t0} is an equilibrium outcome and 2020 already carries the design response. (Under the
    superseded copy-from-2020 convention it did not, and the tables read t0+1.) The scenario 'France' is France's own calibrated path, not a shock on the US
    model, and carries only the pinned reading. """
    return pd.read_csv(_need(os.path.join(C.ESCDIR, 'escExperiments.csv')))


def escRow(df, ρ, spec, scenario, pinned):
    """ One (rho, spec, scenario, reading) row, raising rather than returning an empty frame -- same
    contract as usShockRow. """
    hit = df[np.isclose(df['ρ'], ρ) & (df['spec'] == spec) & (df['scenario'] == scenario)
             & (df['θpinned'].astype(bool) == bool(pinned))
             & np.isclose(df['phi'], C.US['esc']['phi'])]
    if hit.empty:
        raise MissingInput('{} (ρ={}, {}, pinned={}) in results/esc/escExperiments.csv'
                           .format(scenario, ρ, spec, pinned))
    return hit.iloc[-1]
