r""" Workbook loaders for the France and UK variants -- the ModelFR counterpart of test.py.

    import testEU
    m = testEU.model('FR')                 # France
    m = testEU.model('UK')                 # UK, its own income groups
    m = testEU.model('UK', grouping = 'US')  # UK, regrouped at US income percentiles

Same sheet layout as data/USMain_test.xlsx with two differences, both of which are the calibration
protocol showing up in the data (see modelFR.py):

  * There is NO '30y interest' column. R is not a target for these countries -- beta is imposed from the
    US -- so the number was never collected. db['R0'] is set to NaN rather than left at ModelUS's default
    2.443: nothing in ModelFR reads it, and a stray ModelUS.calibrate on one of these workbooks must fail
    loudly rather than quietly target the US interest rate.
  * The population sheet's 'Worker-to-retiree' is the column the model uses. France's is adjusted for its
    lower retirement age (2.5 years below the US/UK in 2020, narrowing to 2 by 2050) and so differs from
    the raw census ratio in the neighbouring column; the UK's does not need the adjustment.

France's 'Replacement rate' is 1, and getTheta (getθ) returns exactly 1 at RR0 = 1 for ANY income
grouping -- which is why France's groups can be cut at US percentiles. Nothing imposes theta = 1 in code.

The UK workbook carries a second pair of sheets, 'heterogeneityUS'/'calibrationUS', holding the same UK
data regrouped at the US income percentiles (cumulative population shares 0.5823/0.7580/1). Those are for
counterfactuals that need the two countries' groups to line up; the UK's OWN calibration uses its own
half-mean/mean cuts, which is what grouping = 'UK' (the default) selects. The two carry different
replacement-rate ratios (0.694 vs 0.868) and so different theta -- they are not interchangeable.
"""
import os
import numpy as np, pandas as pd

DIR = os.path.dirname(os.path.abspath(__file__))
PATHS = {'FR': os.path.join(DIR, '..', '..', 'data', 'FRMain.xlsx'),
         'UK': os.path.join(DIR, '..', '..', 'data', 'UKMain.xlsx')}
t_ss = 3   # number of periods in steady state, as in test.py


def load(country, grouping = None, t_ss = t_ss):
    """ Read a workbook into (pars, kwargs, dates, workweek), in the form ModelFR's __init__ wants.
    grouping selects the sheet pair: None/'' the workbook's own, 'US' the '...US' pair (UK only). """
    suffix = grouping or ''
    wb = pd.read_excel(PATHS[country], sheet_name = None, header = None)

    def sheet(name):
        d = pd.DataFrame(wb[name].values)
        return pd.DataFrame(d.iloc[1:, ].values, columns = d.iloc[0, :])

    dft = sheet('population').set_index('t')
    datesLog = dft.index
    νLog = dft['Worker-to-retiree'].values.astype(float)
    TLog = len(datesLog)
    dates = datesLog.union(pd.Index([datesLog[-1]+30*i for i in range(1, t_ss+1)]))

    dfj = sheet('heterogeneity'+suffix)
    dfc = sheet('calibration'+suffix)
    dfc = pd.Series(dfc.iloc[0, :].values, index = dfc.columns)
    workweek = dfc['Average workweek']

    kwargs = {'T': TLog+t_ss, 'nj': dfj.shape[0]}
    pars = {'α': dfc['Capital income share'], 'ξ': dfc['Labor supply elasticity'],
            'ν': np.hstack([νLog, np.full(kwargs['T']-TLog, νLog[-1])]),
            'τ0': dfc['Pension tax'], 'RR0': dfc['Replacement rate'],
            'RRGroups': tuple(eval(str(dfc['Replacement rate groups']))),
            't0': dates.get_loc(dfc['Calibration year']),
            'γj': dfj['Population shares'].values.astype(float),
            'μj': dfj['Voting shares'].values.astype(float),
            'Xj': 1,
            'zxj': (dfj['Hours'].values/(dfj['Hours'].values.mean())).astype(float),
            'zηj': (dfj['Income'].values/(dfj['Income'].values.mean())).astype(float)}
    pars['h0'] = workweek / (7*12)      # share of time spent working -- the SAME unit as the US's h0,
                                        # which is what makes the h̄ ratio in ModelFR.hbarTarget meaningful
    pars['Ushare0'] = dfc['Universal share']
    pars['R0'] = np.nan                 # not a target here, and not in the workbook -- see the docstring
    return pars, kwargs, dates, workweek


def usReference(commonX = False, h0US = None):
    """ ModelFR's US reference as a callable of rho, read off the US rho sweep. h0US defaults to the US
    workbook's own average-hours input, loaded from test.py. """
    from modelFR import usRefFromCsv
    if h0US is None:
        import test as testmod
        h0US = testmod.pars['h0']
    csv = os.path.join(DIR, '..', '..', 'results', 'calibration',
                       'US_rhoGridCommonX.csv' if commonX else 'US_rhoGrid.csv')
    return usRefFromCsv(csv, h0US = h0US)


def model(country, grouping = None, commonX = False, ρ = 1., ω = 2., **over):
    """ A ready ModelFR on `country`'s workbook, with the US reference wired to the sweep of the matching
    variant. beta is NOT set here: setUSRef installs it from the reference at db's rho when calibrate runs.
    """
    from modelFR import ModelFR
    pars, kwargs, dates, workweek = load(country, grouping = grouping)
    pars.update({'ρ': ρ, 'ω': ω})
    m = ModelFR(pars = pars | over, commonX = commonX,
                usRef = usReference(commonX = commonX), **kwargs)
    m.db['dates'], m.db['workweek'], m.db['country'] = dates, workweek, country+(grouping or '')
    return m
