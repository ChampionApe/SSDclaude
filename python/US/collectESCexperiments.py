r""" Collect the endogenous-theta counterfactual runs across rho into one table.

Run:  .venv\Scripts\python.exe python\US\collectESCexperiments.py

Inputs (results/esc/): escShocks.csv (rho = 1, LOG, runESC.py) and escShocksCRRA.csv (rho != 1, CRRA,
runESCcrra.py --stage shocks). Writes results/esc/escExperiments.csv (long form, one row per
(rho, spec, method, scenario, reading)) and prints a per-spec pivot at t0 (2020): the design in force
(theta_t0) and the tax/savings outcomes there, chosen vs pinned. Reported at t0 because every scenario
is a new equilibrium path whose political choice binds from the first period, so 2020's design is an
outcome rather than an inherited datum (runESC.py's shocks-stage docstring). The paper pipeline's
stage (ii) declares this script (python/paper/runShocksUS.py) and stage (iii) reads only its output, so
a change to the merge belongs here, not in the pipeline.

`method` says which solver produced a CRRA row: 'exact' (LeadedCRRA2D, the published method) or 'path'
(the path iteration). LOG rows are stamped 'exact' -- the LOG backward recursion is the exact solution
-- and a CRRA row written before the column existed is a path-iteration row. Both vintages are carried
through; python/paper/datasets.escRow selects by config.US['esc']['exact'].
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
ESC = os.path.join(REPO, 'results', 'esc')

COLUMNS = ('ρ', 'preferences', 'spec', 'phi', 'commonX', 'method', 'p', 'scenario', 'θpinned',
           'θ_tm1', 'θ_t0', 'θ_t1', 'τ_t0', 'sr_t0', 'ww_t0', 'τ_t1', 'sr_t1', 'ww_t1')


def merge(log, crra):
    """ The merged long table from the LOG frame (escShocks.csv) and the CRRA frame (escShocksCRRA.csv).
    Pure: no file access, so test_esc.py can drive it on toy frames. """
    log = log.copy()
    crra = crra.copy()
    log['ρ'], log['preferences'] = 1.0, 'LOG'
    log['method'] = 'exact'
    crra['preferences'] = 'CRRA'
    if 'method' not in crra.columns:
        crra['method'] = 'path'
    crra['method'] = crra['method'].fillna('path')
    d = pd.concat([log, crra], ignore_index = True)
    # commonX identifies the calibration variant the row was produced under and is carried through to
    # the merged csv, where datasets.escExperiments filters on it. A row written before the column
    # existed is a vector-X row (the variant everything ran under then), so that is what a missing value
    # means.
    if 'commonX' not in d.columns:
        d['commonX'] = False
    d['commonX'] = d['commonX'].fillna(False).astype(bool)
    d = d[[c for c in COLUMNS if c in d.columns]]
    return d.sort_values(['commonX', 'method', 'spec', 'ρ', 'scenario', 'θpinned']).reset_index(drop = True)


def main():
    sys.stdout.reconfigure(encoding = 'utf-8', line_buffering = True)
    d = merge(pd.read_csv(os.path.join(ESC, 'escShocks.csv')),
              pd.read_csv(os.path.join(ESC, 'escShocksCRRA.csv')))
    out = os.path.join(ESC, 'escExperiments.csv')
    d.to_csv(out, index = False)
    print(f'-> {os.path.relpath(out, REPO)}  ({len(d)} rows)\n')

    order = ['baseline', 'mild', 'acute', 'frIncome', 'frLeisure', 'frVoting', 'frBoth',
             'frAll', 'France']
    for cx in sorted(d['commonX'].unique()):
        for method in sorted(d['method'].unique()):
            for spec in sorted(d.loc[d['commonX'] == cx, 'spec'].unique()):
                ds = d[(d['spec'] == spec) & (d['commonX'] == cx) & (d['method'] == method)]
                if ds.empty:
                    continue
                print('=' * 100)
                print('spec = {}, phi = 0.5, {}, method = {}   (theta_t0 = design in force at 2020; '
                      'tau/sr at 2020)'.format(spec, 'common X' if cx else 'vector X', method))
                print('=' * 100)
                for pin, lab in ((False, 'theta CHOSEN'), (True, 'theta PINNED at its exogenous value')):
                    sub = ds[ds['θpinned'] == pin]
                    if sub.empty:
                        continue
                    piv = sub.pivot_table(index = 'scenario', columns = 'ρ',
                                          values = ['θ_t0', 'τ_t0', 'sr_t0'], aggfunc = 'first')
                    piv = piv.reindex([s for s in order if s in piv.index])
                    print('\n--- {} ---'.format(lab))
                    print(piv.round(4).to_string())
                print()


if __name__ == '__main__':
    main()
