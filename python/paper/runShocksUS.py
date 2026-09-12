r""" Stage (ii) of the paper pipeline, US/France/UK arm: run the counterfactuals the rich-OECD tables and
figure are read off. Nothing is calibrated here -- every experiment reads (beta, omega) from the sweep
csvs, so stage (i) (runCalibrationUS.py) must have run first.

Run:  .venv\Scripts\python.exe python\paper\runShocksUS.py               the MAIN part: whatever is missing
      ... --prepub                                                       the PRE-PUBLICATION part only
      ... --all                                                          both parts
      ... --only shocks                                                  one experiment
      ... --list                                                         what exists, what is missing
      ... --force                                                        re-run even where output exists
      ... --dry                                                          print the commands and exit

As in the Argentina arm, each entry declares WHAT the paper needs and which script produces it;
python/US/runShocksUS.py is the implementation and keeps its own CLI. This file records the settings the
published numbers were produced at.

TWO PARTS. `part = 'main'` is what a routine rebuild runs: the exogenous-theta shocks in both variants and
the LOG leg of the endogenous-theta appendix, all cheap. `part = 'prepub'` holds the heavy runs whose
results move only when the model does, run once before submission: the exact CRRA ESC leg (the published
method, config.US['esc']['exact']) and the timing checks of TODO R3. The merge (`escExperiments`) belongs
to both. The two parts are selected on the command line, never mixed by default, so that a development
rebuild can never turn into an overnight solve.

ONE SCRIPT PRODUCES ALL THREE TABLES' WORTH OF ROWS. python/US/runShocksUS.py writes one long csv --
one row per (rho, family, scenario, effect) -- covering the theta, ageing and French-characteristic
families at every rho in config.US['ρTable']. That is why the whole set costs one entry here rather than
three: the families share a baseline solve per rho, and splitting them would re-solve it three times.

Cost of the main part: ~30 s for the exogenous shocks, a few minutes for the LOG ESC leg. Every experiment
there is cheap because none of them calibrates -- the expensive outer root already ran in stage (i). The
`freeTheta` entry is a second reading of the French income-distribution counterfactual (theta re-derived
from RR0 rather than held at the US design); see python/US/shocks.shockIncomeDistribution for why that
choice is not incidental.
"""
import os, sys, argparse, subprocess
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding = 'utf-8')

RHOFLAGS = ['--rho'] + [str(r) for r in C.US['ρTable']]
G = C.US['gridSettings']
GRIDFLAGS = ['--n', str(G['n']), '--ns', str(G['ns']),
             '--interpKind', G['interpKind'], '--smoothKnots', str(G['smoothKnots'])]
# The ESC leg runs under the headline calibration variant only. It is the most expensive stage in the
# pipeline, and unlike the exogenous-theta shocks -- where both variants are cheap and both are built --
# a second variant here would double a multi-hour run for an appendix the paper does not read twice.
ESCVARIANT = ['--commonX'] if C.US['commonX'] else []
ESC = C.US['esc']
ESCSPEC = ['--spec', ESC['spec'], '--phi', str(ESC['phi'])]
ESCRHO = [str(r) for r in ESC['ρTable'] if r != C.US['ρAnchor']]


def _hasExactRows(path, ρs = None):
    """ Output check for the exact CRRA leg: the csv exists AND carries method = 'exact' rows at every rho
    the tables print, under the headline variant. The file's mere existence says nothing -- the path
    iteration's rows live in the same csv under method = 'path'. """
    if not os.path.exists(path):
        return False
    df = pd.read_csv(path)
    if 'method' not in df.columns:
        return False
    df = df[df['method'].fillna('path') == 'exact']
    if 'commonX' in df.columns:
        df = df[df['commonX'].fillna(False).astype(bool) == bool(C.US['commonX'])]
    have = set(round(float(r), 6) for r in df['ρ'])
    return all(round(float(r), 6) in have for r in (ρs or [float(r) for r in ESCRHO]))


EXPERIMENTS = {
    # Every family, every rho in the table grid, both readings (full effect and economic-equilibrium-only).
    # The VECTOR-X variant: with config.US['commonX'] = True this is the appendix's robustness twin, and
    # 'shocksCommonX' below carries the headline tables and figure. Both are built either way -- they cost
    # 30 s each and the pair is a check on itself (see 'shocksCommonX').
    'shocks': {
        'part':    'main',
        'script':  'runShocksUS.py',
        'args':    RHOFLAGS + GRIDFLAGS,
        'outputs': lambda: [os.path.join(C.SHOCKDIR, 'US_shocks.csv')],
        'note':    'theta / ageing / French, all rho, both effects',
    },
    # The same set under the common-X calibration variant -- the HEADLINE one. Cheap and worth
    # having as a check as much as an output: theta, ageing and voting must come back IDENTICAL to the
    # vector-X run (they touch neither eta nor X, and beta/omega/h agree across variants), while income
    # distribution and leisure must differ -- those two are defined through eta and X, whose meaning is
    # exactly what the variant changes. A commonX run that matched on all seven would mean the variant
    # was not being applied.
    'shocksCommonX': {
        'part':    'main',
        'script':  'runShocksUS.py',
        'args':    RHOFLAGS + GRIDFLAGS + ['--commonX'],
        'outputs': lambda: [os.path.join(C.SHOCKDIR, 'US_shocksCommonX.csv')],
        'note':    'the same set under common X',
    },
    # The alternative reading of the income-distribution counterfactual: theta RE-DERIVED from RR0 under
    # France's eta instead of held at the US design. Not wired to a paper output; kept because the
    # difference (tau 13.28% against the reported 12.83% at rho=1, vector X) is a modelling choice the
    # table does not show, and re-deriving it later from memory is what this pipeline exists to avoid.
    'freeTheta': {
        'part':    'main',
        'script':  'runShocksUS.py',
        'args':    RHOFLAGS + GRIDFLAGS + ['--commonX', '--freeTheta', '--family', 'french',
                                           '--out', os.path.join(C.SHOCKDIR, 'US_shocks_freeTheta.csv')],
        'outputs': lambda: [os.path.join(C.SHOCKDIR, 'US_shocks_freeTheta.csv')],
        'note':    'French income distribution with theta re-derived',
    },
    # --- Endogenous system characteristics (app:ESC), the LOG leg (rho = 1). Requires the LOG wedge
    # calibration from stage (i) (runCalibrationUS.py's escMissing step). All cheap.
    # The equilibrium design path under the calibrated wedge: the 0.738 -> 0.748 -> 0.773 drift the
    # text quotes (results/esc/escPath.csv).
    'escPath': {
        'part':    'main',
        'script':  'runESC.py',
        'args':    ['--stage', 'path'] + ESCSPEC + ESCVARIANT,
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escPath.csv')],
        'note':    'endogenous-theta design path, LOG (rho = 1)',
    },
    # The counterfactuals on the LEADED-choice model at the calibrated wedge, each run twice (theta
    # pinned at the calibrated design vs chosen).
    'escShocks': {
        'part':    'main',
        'script':  'runESC.py',
        'args':    ['--stage', 'shocks'] + ESCSPEC + ESCVARIANT,
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escShocks.csv')],
        'note':    'endogenous-theta counterfactuals, LOG (rho = 1)',
    },
    # France and the UK under the US wedge and under their own (Tables/UK_ESC_Calibration.tex).
    'escCountry': {
        'part':    'main',
        'script':  'runESC.py',
        'args':    ['--stage', 'country'] + ESCSPEC + ESCVARIANT,
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escCountry.csv')],
        'note':    'France and the UK under the ESC wedge, LOG (rho = 1)',
    },
    # The timing checks of TODO R3. Permanent: the anticipated-vote fixed point under LOG at three phi and
    # both specs (its reference numbers are also test_esc.py's), and under CRRA traced in rho (a corner
    # at every rho, which is what the trace shows). Sequential: the costless FOC of eq:esc:seqFOC on the
    # solved baseline at rho = 0.5 and 2 -- negative on all of [0,1] is the "three timings, one corner"
    # claim; the LOG case is test_esc.py's.
    'escPermanent': {
        'part':    'prepub',
        'script':  'runESC.py',
        'args':    ['--stage', 'permanent', '--spec', 'scale', 'flat', '--phi', '0.25', '0.5', '0.75']
                   + ESCVARIANT,
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escPermanent.csv')],
        'note':    'permanent timing, LOG: own-p calibration at three phi, both specs (~15 min)',
    },
    'escPermanentCRRA': {
        'part':    'prepub',
        'script':  'runESCcrra.py',
        'args':    ['--stage', 'permanent', '--rho'] + [str(r) for r in ESC['ρPermanentCRRA']]
                   + ESCSPEC + ESCVARIANT,
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escPermanentCRRA.csv')],
        'note':    'permanent timing, CRRA, traced in rho (~30 min)',
    },
    'escSequentialCRRA': {
        'part':    'prepub',
        'script':  'runESCcrra.py',
        'args':    ['--stage', 'sequential', '--rho'] + ESCRHO + ESCVARIANT,
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escSequentialCRRA.csv')],
        'note':    'sequential timing, CRRA: the costless FOC over theta (~2 min)',
    },
    # --- PRE-PUBLICATION. The CRRA leg by the EXACT 2-D recursion (LeadedCRRA2D), the published method:
    # the design path and the counterfactuals at the exact-calibrated p from stage (i) --prepub. One full
    # recursion per chosen-design reading, ~6 min each at ns = 150; ~1.5 h for the two rho. Rows carry
    # method = 'exact' and sit beside the path iteration's rows (method = 'path'), which no paper output
    # reads (config.US['esc']['exact']); the output check therefore looks for exact rows, not the file.
    'escShocksCRRA': {
        'part':    'prepub',
        'script':  'runESCcrra.py',
        'args':    (['--exact', '--stage', 'path', 'shocks', '--rho'] + ESCRHO + ESCSPEC
                    + ['--ns', str(ESC['ns2D']), '--nsScan', str(ESC['nsScan']),
                       '--nCand2D', str(ESC['nCand2D'])] + ESCVARIANT),
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escShocksCRRA.csv'),
                            os.path.join(C.ESCDIR, 'escPathCRRA.csv')],
        'complete': lambda: all(_hasExactRows(os.path.join(C.ESCDIR, f))
                                for f in ('escShocksCRRA.csv', 'escPathCRRA.csv')),
        'note':    'endogenous-theta path and counterfactuals, CRRA, EXACT 2-D recursion',
    },
    # The merge stage (iii) reads. Listed last so a run rebuilds it after the producers, in BOTH parts,
    # and NEVER skipped ('always'): it costs a second, and a merge left over from before a producer ran
    # is exactly the stale-but-present output that blocked the build on 2026-09-11.
    'escExperiments': {
        'part':    'both',
        'always':  True,
        'script':  'collectESCexperiments.py',
        'args':    [],
        'outputs': lambda: [os.path.join(C.ESCDIR, 'escExperiments.csv')],
        'note':    'merge the LOG and CRRA legs into one long table',
    },
}


def selected(prepub = False, all_ = False):
    """ The entry names of the requested part(s), in declaration order. """
    parts = {'main', 'prepub', 'both'} if all_ else ({'prepub', 'both'} if prepub else {'main', 'both'})
    return [n for n, e in EXPERIMENTS.items() if e['part'] in parts]


def status(name):
    e = EXPERIMENTS[name]
    script = os.path.join(C.USDIR, e['script'])
    outs = e['outputs']()
    have = [p for p in outs if os.path.exists(p)]
    lack = [p for p in outs if p not in have]
    if not lack and 'complete' in e and not e['complete']():
        lack = [p + ' (no exact rows)' for p in outs]
    if e.get('always'):
        lack = lack or [p + ' (always re-run)' for p in outs]
    return os.path.exists(script), have, lack


def command(name):
    e = EXPERIMENTS[name]
    return [C.PYTHON, os.path.join(C.USDIR, e['script'])] + list(e['args'])


def main():
    p = argparse.ArgumentParser(description = __doc__.split('\n')[1])
    p.add_argument('--only', nargs = '+', choices = list(EXPERIMENTS), default = None,
                   help = 'a subset, regardless of part')
    p.add_argument('--prepub', action = 'store_true', help = 'the pre-publication part instead of the main one')
    p.add_argument('--all', dest = 'all_', action = 'store_true', help = 'both parts')
    p.add_argument('--list', action = 'store_true', help = 'report what exists and exit')
    p.add_argument('--force', action = 'store_true', help = 're-run even where output already exists')
    p.add_argument('--dry', action = 'store_true', help = 'print commands and exit')
    a = p.parse_args()
    names = a.only if a.only else selected(a.prepub, a.all_)

    if a.list or a.dry:
        for name in names:
            ok, have, lack = status(name)
            n = len(EXPERIMENTS[name]['outputs']())
            print('{:<7} {:<18} {:<66} script:{}  have {}/{}{}'.format(
                EXPERIMENTS[name]['part'], name, EXPERIMENTS[name]['note'], 'yes' if ok else 'MISSING',
                n - len(lack), n, '  (no exact rows yet)' if any('no exact' in l for l in lack) else ''))
            if a.dry and ok:
                print('    ' + ' '.join(command(name)))
        return

    for name in names:
        ok, have, lack = status(name)
        if not ok:
            print('SKIP {}: {} does not exist yet.'.format(name, EXPERIMENTS[name]['script']))
            continue
        if not lack and not a.force:
            print('SKIP {}: all {} output(s) present.'.format(name, len(have)))
            continue
        cmd = command(name)
        print('\n' + '='*94 + '\n{} [{}]: {}\n  {}\n'.format(name, EXPERIMENTS[name]['part'],
                                                             EXPERIMENTS[name]['note'], ' '.join(cmd))
              + '='*94)
        r = subprocess.run(cmd, cwd = C.REPO)
        if r.returncode:
            raise SystemExit('{} exited {}'.format(EXPERIMENTS[name]['script'], r.returncode))


if __name__ == '__main__':
    main()
