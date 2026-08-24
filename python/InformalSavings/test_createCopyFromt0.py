r""" createCopyFromt0 must reproduce the tail of the baseline path when there is no actual shock, and
must leave db/T/tFirst/x0/db['t0'] self-consistent for a genuinely shorter, renumbered horizon. Also
covers stateAtT0's ι reporting asymmetry (ι is reported as ι_t, t=0..T-2, not lagged like s_).

Run:  .venv\Scripts\python.exe python\informalSavings\test_createCopyFromt0.py
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod

m = testmod.mLOG

from gridsearch.testing import check, report

# ---- 1. _sliceDb: covered once, in informalAnalytical/test_createCopyFromt0.py
# The helper is byte-identical in all three modules (it is module-level and shared verbatim), so the
# synthetic-db checks are run there rather than three times over the same code. What IS per-module is
# everything below: createCopyFromt0 wires this class's own attributes, and stateAtT0 differs by model.

# ---- 2. createCopyFromt0: structural consistency on the real calibrated instance
T = len(m.db['t'])
calPos = m.db['t0']
t0Pos = T // 2
t0 = m.db['t'][t0Pos]
mt0 = m.createCopyFromt0(t0)

check('mt0 is independent of m', mt0.db is not m.db)
check('mt0.db shared across its own B/BG/BT/LOG/CRRA', mt0.db is mt0.B.db is mt0.LOG.db is mt0.CRRA.db)
check('mt0.T == T - t0Pos', mt0.T == T - t0Pos)
check("mt0.db['t'] renumbered to 0-based", list(mt0.db['t']) == list(range(T - t0Pos)))
check('tFirst reset to 0 on B/BG/BT', mt0.B.tFirst == 0 and mt0.BG.tFirst == 0 and mt0.BT.tFirst == 0)
check('LOG/CRRA T refreshed', mt0.LOG.T == mt0.T and mt0.CRRA.T == mt0.T)
check('warm-start caches cleared', mt0.x0 == {} and mt0.LOG.x0 == {} and mt0.CRRA.x0 == {})
expectedT0 = (calPos - t0Pos) if calPos >= t0Pos else None
check("db['t0'] shifted/None correctly", mt0.db['t0'] == expectedT0,
      f'-> got {mt0.db["t0"]!r}, expected {expectedT0!r}')
for k in ('α', 'ν', 'ξ', 'ρ', 'ω', 'χR', 'βi', 'γi'):
    check(f"db[{k!r}] index matches new db['t']", list(mt0.db[k].index) == list(mt0.db['t']))

# db['t0'] "still valid" branch, checked in isolation (slice exactly at the calibration year itself)
mtKeep = m.createCopyFromt0(m.db['t'][calPos])
check("db['t0'] == 0 when sliced exactly at the calibration year", mtKeep.db['t0'] == 0)
try:
    m.createCopyFromt0(m.db['t'][-1] + 1)
    check('t0 outside db[t] raises ValueError', False)
except ValueError:
    check('t0 outside db[t] raises ValueError', True)

# ---- 3. behavioral round trip: no actual shock -> the copy reproduces the baseline's own tail
base = m.solvePEE_LOG()
seed = m.stateAtT0(base['report'], t0, init = base['init'])
check('stateAtT0 returns s0 and ι0', set(seed) == {'s0', 'ι0'})
shocked = mt0.solvePEE_LOG(**seed)

dS0 = abs(base['report']['s'].xs(t0) - shocked['report']['s'].xs(0))
dH0 = abs(base['report']['h'].xs(t0) - shocked['report']['h'].xs(0))
check('report[s] at t0 matches baseline (no shock)', dS0 < 1e-6, f'-> |diff|={dS0:.2e}')
check('report[h] at t0 matches baseline (no shock)', dH0 < 1e-6, f'-> |diff|={dH0:.2e}')

tailOffset = min(2, mt0.T - 2)  # stay inside txE's domain (length T-1) for the ι check below
tailOrig, tailNew = m.db['t'][t0Pos + tailOffset], mt0.db['t'][tailOffset]
dSTail = abs(base['report']['s'].xs(tailOrig) - shocked['report']['s'].xs(tailNew))
dHTail = abs(base['report']['h'].xs(tailOrig) - shocked['report']['h'].xs(tailNew))
dITail = abs(base['report']['ι'].xs(tailOrig) - shocked['report']['ι'].xs(tailNew))
check('report[s] later in the tail matches baseline (no shock)', dSTail < 1e-6, f'-> |diff|={dSTail:.2e}')
check('report[h] later in the tail matches baseline (no shock)', dHTail < 1e-6, f'-> |diff|={dHTail:.2e}')
check('report[ι] later in the tail matches baseline (no shock)', dITail < 1e-6, f'-> |diff|={dITail:.2e}')

# ---- 4. stateAtT0's ι asymmetry: at t0 == db['t'][0], ι0 must come from init['ι'] verbatim, NOT
# report['ι'].xs(t0-1) (which would be out of range / a different period's value on another instance --
# the exact footgun stateAtT0 exists to avoid). A sentinel init value confirms the branch actually fires.
sentinel = -0.12345
seedFirst = m.stateAtT0(base['report'], m.db['t'][0], init = {'ι': sentinel})
check("stateAtT0 at t0==db['t'][0] returns init['ι'] verbatim", seedFirst['ι0'] == sentinel)
seedInterior = m.stateAtT0(base['report'], t0, init = {'ι': sentinel})
check('stateAtT0 at an interior t0 ignores init and reads report[ι].xs(t0-1)',
      seedInterior['ι0'] != sentinel and np.isclose(seedInterior['ι0'], base['report']['ι'].xs(m.db['t'][t0Pos - 1])))

# ---- 5. LOG.solveRobust actually runs on the copy (warm-start caches genuinely cleared, not stale-shaped)
sols = mt0.LOG.solveBackward(mt0.db['θ'].values, mt0.db['eps'].values)
check('LOG.solveBackward runs on the copy without error', len(sols) == mt0.T)

report()
