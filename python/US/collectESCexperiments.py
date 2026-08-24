r""" Collect the endogenous-theta counterfactual runs across rho into one table.

Run:  .venv\Scripts\python.exe python\US\collectESCexperiments.py

Inputs (results/esc/): escShocks.csv (rho = 1, LOG, runESC.py) and escShocksCRRA.csv (rho != 1, CRRA,
runESCcrra.py --stage shocks). Writes results/esc/escExperiments.csv (long form, one row per
(rho, spec, scenario, reading)) and prints a per-spec pivot at t0 (2020): the design in force
(theta_t0) and the tax/savings outcomes there, chosen vs pinned. Reported at t0 because every scenario
is a new equilibrium path whose political choice binds from the first period, so 2020's design is an
outcome rather than an inherited datum (runESC.py's shocks-stage docstring). The paper pipeline's
stage (ii) declares this script (python/paper/runShocksUS.py) and stage (iii) reads only its output, so
a change to the merge belongs here, not in the pipeline.
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
ESC = os.path.join(REPO, 'results', 'esc')

log = pd.read_csv(os.path.join(ESC, 'escShocks.csv'))
log['ρ'], log['preferences'] = 1.0, 'LOG'
crra = pd.read_csv(os.path.join(ESC, 'escShocksCRRA.csv'))
crra['preferences'] = 'CRRA'
d = pd.concat([log, crra], ignore_index = True)
d = d[[c for c in ('ρ', 'preferences', 'spec', 'phi', 'p', 'scenario', 'θpinned',
                   'θ_tm1', 'θ_t0', 'θ_t1', 'τ_t0', 'sr_t0', 'ww_t0', 'τ_t1', 'sr_t1', 'ww_t1')
       if c in d.columns]]
d = d.sort_values(['spec', 'ρ', 'scenario', 'θpinned']).reset_index(drop = True)
out = os.path.join(ESC, 'escExperiments.csv')
d.to_csv(out, index = False)
print(f'-> {os.path.relpath(out, REPO)}  ({len(d)} rows)\n')

order = ['baseline', 'mild', 'acute', 'frIncome', 'frLeisure', 'frVoting', 'frBoth',
         'frAll', 'France']
for spec in ('scale', 'flat'):
    ds = d[d['spec'] == spec]
    if ds.empty:
        continue
    print('=' * 100)
    print(f'spec = {spec}, phi = 0.5   (theta_t0 = design in force at 2020; tau/sr at 2020)')
    print('=' * 100)
    for pin, lab in ((False, 'theta CHOSEN'), (True, 'theta PINNED at its exogenous value')):
        sub = ds[ds['θpinned'] == pin]
        if sub.empty:
            continue
        piv = sub.pivot_table(index = 'scenario', columns = 'ρ',
                              values = ['θ_t0', 'τ_t0', 'sr_t0'], aggfunc = 'first')
        piv = piv.reindex([s for s in order if s in piv.index])
        print(f'\n--- {lab} ---')
        print(piv.round(4).to_string())
    print()
