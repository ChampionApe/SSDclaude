r""" Stage (ii) of the paper pipeline: run the experiments whose output the paper's tables and figures
are read off. Nothing is calibrated here -- every experiment starts from a pickled calibrated instance,
so stage (i) must have run first.

Run:  .venv\Scripts\python.exe python\paper\runShocks.py                 run whatever is missing
      ... --only universal                                              one experiment
      ... --list                                                        what exists, what is missing
      ... --force                                                       re-run even where output exists
      ... --dry                                                         print the commands and exit

Each entry of EXPERIMENTS declares WHAT the paper needs and which script produces it. The scripts are
the implementations and keep their own CLIs; this file is the record of the settings the published
numbers were produced at, so that reproducing them is a run rather than an archaeology.

Cost, cold, on the 16-point rho grid: `universal` ~2.5 h (a full backward PEE recursion per rho),
`flat` ~10 min (anchor only), `eeOnly` ~minutes (taxes are exogenous, so it is one EE solve per rho and
no policy recursion), `epsThetaGrid` ~5 min (378 points). Every entry is skipped when its output already
exists, so a re-run with nothing to do costs seconds.
"""
import os, sys, argparse, subprocess, glob
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

for _s in (sys.stdout, sys.stderr):             # --dry prints GRIDFLAGS, which carry '--nι'
    _s.reconfigure(encoding = 'utf-8')

G = C.ARG['gridSettings']
GRIDFLAGS = ['--interpKind', G['interpKind'], '--smoothKnots', str(G['smoothKnots']),
             '--nι', str(G['nι']), '--ns', str(G['ns'])]


def _rhoFiles(dirname, template, ρGrid):
    return {ρ: os.path.join(dirname, template.format(ρ = ρ)) for ρ in ρGrid}


EXPERIMENTS = {
    # The headline reform: b^0 = b^1 at t0, taxes re-optimised politically. Tables funcOfRho and the
    # "Full effect" row of ArgentinaUniversal, and figure ARG_CRRA_LOG.
    'universal': {
        'script':  'shockUniversal.py',
        'args':    ['--rule', C.ARG['rule'], '--refType', str(C.ARG['refType'])] + GRIDFLAGS,
        'outputs': lambda: _rhoFiles(C.SHOCKDIR, 'universal_%s_rho{ρ:.4f}.csv' % C.ARG['rule'],
                                     C.ARG['ρGrid']),
        'note':    'full effect, all rho',
    },
    # The other reading of "universal" (eps = 1-theta, the non-contributive component only). It falls on
    # the OTHER side of the status quo, so the two bracket the reform rather than differing in degree.
    # Anchor only -- extending it to the whole grid is an open item (InformalSavings/README.md).
    'flat': {
        'script':  'shockUniversal.py',
        'args':    ['--rule', 'flat'] + GRIDFLAGS,
        'rho':     [C.ARG['ρAnchor']],
        'outputs': lambda: _rhoFiles(C.SHOCKDIR, 'universal_flat_rho{ρ:.4f}.csv', [C.ARG['ρAnchor']]),
        'note':    'bracketing reading, anchor only',
    },
    # The same reform with taxes held at the baseline path: the "Economic Equilibrium" row of
    # ArgentinaUniversal, which is what separates the pure equilibrium response from the policy response.
    'eeOnly': {
        'script':  'shockEEOnly.py',
        'args':    ['--rule', C.ARG['rule'], '--refType', str(C.ARG['refType'])] + GRIDFLAGS,
        'outputs': lambda: _rhoFiles(C.SHOCKDIR, 'eeOnly_%s_rho{ρ:.4f}.csv' % C.ARG['rule'],
                                     C.ARG['ρGrid']),
        'note':    'economic-equilibrium effect only (taxes fixed)',
    },
    # Comparative statics in the two system characteristics at the baseline rho, on a full CARTESIAN
    # (eps, theta) grid: one curve in eps per theta, which is what figure ARG_LOG_FourInOne shades.
    # eps does NOT track theta here -- the two are independent axes by construction (see the script).
    'epsThetaGrid': {
        'script':  'sweepEpsThetaGrid.py',
        'args':    ['--rho', str(C.ARG['ρBaseline'])] + GRIDFLAGS,
        'outputs': lambda: {'sweep': os.path.join(C.SWEEPDIR, 'epsThetaGrid_rho{:.4f}.csv'
                                                  .format(C.ARG['ρBaseline']))},
        'note':    'tau/sr/h/iota over the eps x theta plane',
    },
}


def status(name):
    """ (script exists, {key: path} present, {key: path} missing) for one experiment. """
    e = EXPERIMENTS[name]
    have, lack = {}, {}
    for k, path in e['outputs']().items():
        (have if os.path.exists(path) else lack)[k] = path
    return os.path.exists(os.path.join(C.MODELDIR, e['script'])), have, lack


def command(name, ρ = None):
    e = EXPERIMENTS[name]
    cmd = [C.PYTHON, os.path.join(C.MODELDIR, e['script'])] + list(e['args'])
    ρ = ρ if ρ is not None else e.get('rho')
    if ρ:
        cmd += ['--rho'] + [str(v) for v in ρ] if isinstance(ρ, (list, tuple)) else ['--rho', str(ρ)]
    return cmd


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
            print('{:<13} {:<48} script:{}  have {}/{}'.format(
                name, EXPERIMENTS[name]['note'], 'yes' if ok else 'MISSING',
                len(have), len(have)+len(lack)))
            if a.dry and ok:
                print('    ' + ' '.join(command(name)))
            if lack and not a.dry:
                keys = sorted(lack, key = str)
                print('    missing: ' + ', '.join(str(k) for k in keys[:8])
                      + (' ...' if len(keys) > 8 else ''))
        return

    for name in a.only:
        ok, have, lack = status(name)
        if not ok:
            print('SKIP {}: {} does not exist yet.'.format(name, EXPERIMENTS[name]['script']))
            continue
        if not lack and not a.force:
            print('SKIP {}: all {} output(s) present.'.format(name, len(have)))
            continue
        # The scripts are individually resumable and skip what they already have, so the whole set is
        # handed over rather than only the missing keys -- one process, one warm-started march.
        cmd = command(name, list(lack) if (lack and not a.force
                                           and all(isinstance(k, float) for k in lack)) else None)
        print('\n' + '='*94 + '\n{}: {}\n  {}\n'.format(name, EXPERIMENTS[name]['note'], ' '.join(cmd))
              + '='*94)
        r = subprocess.run(cmd, cwd = C.REPO)
        if r.returncode:
            raise SystemExit('{} exited {}'.format(EXPERIMENTS[name]['script'], r.returncode))


if __name__ == '__main__':
    main()
