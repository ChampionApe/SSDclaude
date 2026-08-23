r""" Stage (ii) of the paper pipeline, US/France/UK arm: run the counterfactuals the rich-OECD tables and
figure are read off. Nothing is calibrated here -- every experiment reads (beta, omega) from the sweep
csvs, so stage (i) (runCalibrationUS.py) must have run first.

Run:  .venv\Scripts\python.exe python\paper\runShocksUS.py               run whatever is missing
      ... --only shocks                                                  one experiment
      ... --list                                                         what exists, what is missing
      ... --force                                                        re-run even where output exists
      ... --dry                                                          print the commands and exit

As in the Argentina arm, each entry declares WHAT the paper needs and which script produces it;
python/US/runShocksUS.py is the implementation and keeps its own CLI. This file records the settings the
published numbers were produced at.

ONE SCRIPT PRODUCES ALL THREE TABLES' WORTH OF ROWS. python/US/runShocksUS.py writes one long csv --
one row per (rho, family, scenario, effect) -- covering the theta, ageing and French-characteristic
families at every rho in config.US['ρTable']. That is why the whole set costs one entry here rather than
three: the families share a baseline solve per rho, and splitting them would re-solve it three times.

Cost: ~30 s for the whole thing. Every experiment here is cheap because none of them calibrates -- the
expensive outer root already ran in stage (i). The `pinTheta` entry is a second reading of the French
income-distribution counterfactual (theta held at the US value rather than re-derived from RR0); see
python/US/shocks.shockIncomeDistribution for why that choice is not incidental.
"""
import os, sys, argparse, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding = 'utf-8')

RHOFLAGS = ['--rho'] + [str(r) for r in C.US['ρTable']]
G = C.US['gridSettings']
GRIDFLAGS = ['--n', str(G['n']), '--ns', str(G['ns']),
             '--interpKind', G['interpKind'], '--smoothKnots', str(G['smoothKnots'])]

EXPERIMENTS = {
    # Every family, every rho in the table grid, both readings (full effect and economic-equilibrium-only).
    # Feeds US_PensChars, US_Ageing, US_OtherShocks and their CRRA counterparts, plus US_taxOverview.
    'shocks': {
        'script':  'runShocksUS.py',
        'args':    RHOFLAGS + GRIDFLAGS,
        'outputs': lambda: [os.path.join(C.SHOCKDIR, 'US_shocks.csv')],
        'note':    'theta / ageing / French, all rho, both effects',
    },
    # The same set under the common-X calibration variant, for Figs/USX_taxOverview. Cheap and worth
    # having as a check as much as an output: theta, ageing and voting must come back IDENTICAL to the
    # vector-X run (they touch neither eta nor X, and beta/omega/h agree across variants), while income
    # distribution and leisure must differ -- those two are defined through eta and X, whose meaning is
    # exactly what the variant changes. A commonX run that matched on all seven would mean the variant
    # was not being applied.
    'shocksCommonX': {
        'script':  'runShocksUS.py',
        'args':    RHOFLAGS + GRIDFLAGS + ['--commonX'],
        'outputs': lambda: [os.path.join(C.SHOCKDIR, 'US_shocksCommonX.csv')],
        'note':    'the same set under common X',
    },
    # The alternative reading of the income-distribution counterfactual. Not wired to a paper output;
    # kept because the difference (tau 12.83% against 13.28% at rho=1) is a modelling choice the table
    # does not show, and re-deriving it later from memory is exactly what this pipeline exists to avoid.
    'pinTheta': {
        'script':  'runShocksUS.py',
        'args':    RHOFLAGS + GRIDFLAGS + ['--pinTheta', '--family', 'french',
                                           '--out', os.path.join(C.SHOCKDIR, 'US_shocks_pinTheta.csv')],
        'outputs': lambda: [os.path.join(C.SHOCKDIR, 'US_shocks_pinTheta.csv')],
        'note':    'French income distribution with theta pinned',
    },
}


def status(name):
    e = EXPERIMENTS[name]
    script = os.path.join(C.USDIR, e['script'])
    outs = e['outputs']()
    have = [p for p in outs if os.path.exists(p)]
    return os.path.exists(script), have, [p for p in outs if p not in have]


def command(name):
    e = EXPERIMENTS[name]
    return [C.PYTHON, os.path.join(C.USDIR, e['script'])] + list(e['args'])


def main():
    p = argparse.ArgumentParser(description = __doc__.split('\n')[1])
    p.add_argument('--only', nargs = '+', choices = list(EXPERIMENTS), default = list(EXPERIMENTS))
    p.add_argument('--list', action = 'store_true', help = 'report what exists and exit')
    p.add_argument('--force', action = 'store_true', help = 're-run even where output already exists')
    p.add_argument('--dry', action = 'store_true', help = 'print commands and exit')
    a = p.parse_args()

    if a.list or a.dry:
        for name in a.only:
            ok, have, lack = status(name)
            print('{:<10} {:<48} script:{}  have {}/{}'.format(
                name, EXPERIMENTS[name]['note'], 'yes' if ok else 'MISSING',
                len(have), len(have)+len(lack)))
            if a.dry and ok:
                print('    ' + ' '.join(command(name)))
        return

    for name in a.only:
        ok, have, lack = status(name)
        if not ok:
            print('SKIP {}: {} does not exist yet.'.format(name, EXPERIMENTS[name]['script']))
            continue
        if not lack and not a.force:
            print('SKIP {}: all {} output(s) present.'.format(name, len(have)))
            continue
        cmd = command(name)
        print('\n' + '='*94 + '\n{}: {}\n  {}\n'.format(name, EXPERIMENTS[name]['note'], ' '.join(cmd))
              + '='*94)
        r = subprocess.run(cmd, cwd = C.REPO)
        if r.returncode:
            raise SystemExit('{} exited {}'.format(EXPERIMENTS[name]['script'], r.returncode))


if __name__ == '__main__':
    main()
