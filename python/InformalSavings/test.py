import os, pandas as pd, numpy as np, scipy
from model import ModelInformalSavings
from symMaps import SimpleSys

# Read in data from excel: C:\Users\sxj477\Documents\GitHub\SSDclaude\data\ArgentinaTest.xlsx
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'ArgentinaTest.xlsx')
wb = pd.read_excel(PATH, sheet_name = None, header = None)
t_ss  = 3 # number of periods in steady state

# Read population sheet:
dft = pd.DataFrame(wb['population'].values)
dft = pd.DataFrame(dft.iloc[1:,].values, columns = dft.iloc[0,:]).set_index('t')
datesLog = dft.index
νLog = dft['Worker-to-retiree'].values.astype(float)
TLog = len(datesLog)
dates = datesLog.union(pd.Index([datesLog[-1]+30*i for i in range(1, t_ss+1)]))

# Read heterogeneity sheet:
dfj = pd.DataFrame(wb['heterogeneity'].values)
dfj = pd.DataFrame(dfj.iloc[1:,].values, columns = dfj.iloc[0,:])

# Read calibration sheet:
dfc = pd.DataFrame(wb['calibration'].values)
dfc = pd.Series(dfc.iloc[1,:].values, index = dfc.iloc[0,:].values)
workweek = dfc['Average workweek']

# Create objects to parse to model initialization:
kwargs = {'T': TLog+t_ss, 'nj':dfj.shape[0]}
pars = {'α': dfc['Capital income share'], 'ξ': dfc['Labor supply elasticity'], 'ν': np.hstack([νLog, np.full(kwargs['T']-TLog, νLog[-1])]),
        'τ0': dfc['Pension tax'], 'RR0': dfc['Replacement rate'], 'RRGroups': tuple(eval(dfc['Replacement rate groups'])), 't0': dates.get_loc(dfc['Calibration year']),
        'γj': dfj['Population shares'].values.astype(float), 
        'μj': dfj['Voting shares'].values.astype(float), 
        'Xj': 1,
        'zxj': (dfj['Hours'].values/(dfj['Hours'].values.mean())).astype(float), 
        'zηj': (dfj['Income'].values/(dfj['Income'].values.mean())).astype(float)}
pars['h0'] = workweek / (7*12) # estimate of share of time spend on labor
pars['s0'] = dfc['Savings rate']   # reported only; the target that identifies beta is KY0 below

# The capital-output target does NOT live in the workbook: it is a window mean over an external series,
# so python/paper/dataTargets.py derives it and this csv is the record (target, window, source, date).
# The workbook's 'Savings rate' is what it superseded -- notes/argentina_savingsTargetAudit.md.
TARGETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data',
                       'argentina_calibrationTargets.csv')
pars['KY0'] = float(pd.read_csv(TARGETS).set_index('target').loc['capitalOutputRatio', 'value'])



# Initialize LOG model with some parameter values:
pars.update({'ρ': 1, 'ω': 2, 'β': .6})
mLOG = ModelInformalSavings(pars = pars, **kwargs)
mLOG.db['dates'] = dates
mLOG.db['workweek'] = workweek

