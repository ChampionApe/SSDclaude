r""" Run the repo's test suites and print one verdict.

    .venv\Scripts\python.exe python\runTests.py              # the fast suites (~4 min)
    .venv\Scripts\python.exe python\runTests.py --all        # fast + slow (~1 h)
    .venv\Scripts\python.exe python\runTests.py --slow       # the slow ones only
    .venv\Scripts\python.exe python\runTests.py -k pee       # only suites whose path matches 'pee'
    .venv\Scripts\python.exe python\runTests.py --list       # show the registry and exit

Each suite is a standalone script that prints PASS/FAIL lines and exits nonzero on failure (see
`gridsearch/testing.py`), so they are run as subprocesses rather than imported: a suite mutates its
model instance's db, and several would collide in one process. Per-suite output is echoed only on
failure -- pass `--verbose` to see it always.

SLOW is a wall-time classification, not an importance one. The slow suites run real calibrations and are
the ones that actually pin the published parameters; run `--all` before trusting a change to `model.py`
§8, `policy.py`'s grid settings, or `gridsearch/interp.py`.
"""
import argparse, os, subprocess, sys, time

from gridsearch.testing import utf8Stdout

utf8Stdout()    # the suite notes below contain Greek; see gridsearch/testing.py

ROOT = os.path.dirname(os.path.abspath(__file__))

# (path relative to python/, slow?, one-line note)
SUITES = [
    ('gridsearch/test_roots1d.py',                False, 'crossings, CartesianGrid, selectMax'),
    ('gridsearch/test_interp.py',                 False, 'interpolation kinds, NaN semantics, fixed knots'),
    ('gridsearch/test_continuation.py',           False, 'marchGrid warm starts and failure recovery'),
    ('informalAnalytical/test_ee.py',             False, 'economic equilibrium vs primitives'),
    ('informalAnalytical/test_cacheParams.py',    False, 'the per-year db cache'),
    ('informalAnalytical/test_crraTerminal.py',   False, 'CRRA terminal period'),
    ('informalAnalytical/test_crraBackward.py',   False, 'CRRA t<T recursion'),
    ('informalAnalytical/test_crraPEE.py',        False, 'CRRA end-to-end PEE'),
    ('informalAnalytical/test_createCopyFromt0.py', False, 'model copies for shock experiments'),
    ('InformalSavings/test_ee.py',                False, 'economic equilibrium vs primitives'),
    ('InformalSavings/test_peeLOG.py',            False, 'LOG backward recursion over ι'),
    ('InformalSavings/test_peeCRRA.py',           False, 'CRRA recursion over (s, ι)'),
    ('InformalSavings/test_peePath.py',           False, 'initial fixed point + forward walk'),
    ('InformalSavings/test_createCopyFromt0.py',  False, 'model copies, both states'),
    ('US/test_ee.py',                             False, 'zero-mass informal slot, κ=p, FOC decoupling'),
    ('US/test_invariance.py',                     False, 'the scale (λ) and hours-unit (μ) invariances'),
    ('US/test_crra.py',                           False, 'Γs bracket vs the Θh feasibility cap'),
    ('US/test_calibration.py',                    False, '~6 s: (β,ω) against R/τ, plus commonX'),
    ('US/test_fr.py',                             False, '~20 s: ModelFR -- imposed β, US-referenced h̄'),
    ('US/test_eu.py',                             False, 'the FR/UK workbooks end to end through ModelFR'),
    ('US/test_createCopyFromt0.py',               False, 'model copies from t0 -- the shock machinery'),
    ('US/test_esc.py',                            False, '~12 s: the θ wedge, leaded and permanent choices'),
    ('informalAnalytical/test_calibration.py',    True,  'nested-fixed-point calibration'),
    ('InformalSavings/test_calibration.py',       True,  '~12 min: four LOG calibrations and one CRRA'),
    ('InformalSavings/test_calibrationGrid.py',   True,  '~45 min: three real calibrations over a ρ grid'),
    ('US/test_escCRRA.py',                        True,  '~7 min: LeadedCRRA vs its LOG limit; the 2-D solver vs both'),
]


def run(rel, verbose):
    path = os.path.join(ROOT, rel)
    t0 = time.time()
    p = subprocess.run([sys.executable, path], capture_output = True, text = True,
                       encoding = 'utf-8', errors = 'replace')
    dt = time.time() - t0
    good = p.returncode == 0
    print('{}  {:<44} {:>7.1f}s'.format('pass' if good else 'FAIL', rel, dt))
    if verbose or not good:
        for line in (p.stdout or '').splitlines():
            if verbose or line.startswith('FAIL') or line.startswith('Traceback'):
                print('       | ' + line)
        for line in (p.stderr or '').splitlines()[-20:]:
            print('       ! ' + line)
    return good, dt


def main():
    ap = argparse.ArgumentParser(description = __doc__,
                                 formatter_class = argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--all',  action = 'store_true', help = 'include the slow suites')
    ap.add_argument('--slow', action = 'store_true', help = 'run only the slow suites')
    ap.add_argument('-k', dest = 'pattern', default = None, help = 'substring filter on the suite path')
    ap.add_argument('--list', action = 'store_true', help = 'print the registry and exit')
    ap.add_argument('--verbose', action = 'store_true', help = 'echo every suite\'s output')
    a = ap.parse_args()

    if a.list:
        for rel, slow, note in SUITES:
            print('{:<6} {:<44} {}'.format('SLOW' if slow else 'fast', rel, note))
        return 0

    sel = [s for s in SUITES if (s[1] if a.slow else (a.all or not s[1]))]
    if a.pattern:
        sel = [s for s in sel if a.pattern in s[0]]
    if not sel:
        print('no suites selected'); return 1

    print('running {} suite{}\n'.format(len(sel), '' if len(sel) == 1 else 's'))
    results = [(rel, ) + run(rel, a.verbose) for rel, _, _ in sel]
    bad = [rel for rel, good, _ in results if not good]
    print('\n{} of {} suites passed in {:.0f}s'.format(len(results) - len(bad), len(results),
                                                       sum(dt for _, _, dt in results)))
    if bad:
        print('failed: ' + ', '.join(bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
