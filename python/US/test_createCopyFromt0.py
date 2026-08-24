r""" createCopyFromt0 on the US model.

No longer what the counterfactual tables run on -- shocks.py builds new equilibrium paths over the full
horizon (shocks.shockedCopy) since 2026-08-24. Still live and still worth pinning: thetaStakes.py uses it
for the marginal-stake decomposition, where an unanticipated local perturbation is the right object, and
the other two model modules' shock scripts are built on it.

Run:  .venv\Scripts\python.exe python\US\test_createCopyFromt0.py

Inherited from informalAnalytical and, until now, untested here (the module README said so). The contract
is the same: the copy must reproduce the tail of the baseline path when there is no actual shock, and must
leave db/T/tFirst/x0/db['t0'] self-consistent for a genuinely shorter, RENUMBERED horizon. This suite is
that module's, ported, plus two checks specific to this module:

  * The zero-mass informal slot must survive the slice. gamma_0 = 0 is what makes the j=0 terms inert, and
    a copy that lost it would solve a different model without saying so.
  * db['dates'] is STALE on a copy, and that is a trap worth pinning. test.py stores the calendar years
    there, and it looks like the one db entry that would let a copy report calendar-labelled results. It
    is not: `dates = datesLog.union(...)` returns an Index whose name pandas drops to None, so _sliceDb --
    which keys off `v.name == 't'` -- never touches it. The copy therefore carries the FULL original
    calendar against a horizon that starts at t0 and is shorter, so labelling a copy's periods with
    db['dates'] silently mislabels every one of them. Shock code must carry its own calendar.
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import test as testmod
from model import _sliceDb

m = testmod.mLOG

from gridsearch.testing import check, report

# ---- 1. _sliceDb on synthetic db entries: restricted AND renumbered to 0-based
t = pd.Index(range(6), name = 't')
j = pd.Index(range(3), name = 'j')
db = {
    't': t,
    'txE': pd.Index(range(5), name = 't'),
    'j': j,
    'tj': pd.MultiIndex.from_product([t, j]),
    'x': pd.Series(np.arange(10.0, 16.0), index = t),
    'x[t-1]': pd.Series(np.arange(9.0, 15.0), index = t),
    'df': pd.DataFrame(np.arange(12).reshape(6, 2), index = t, columns = [0, 1]),
    'scalar': 3.14,
    'typeOnly': pd.Series([1., 2., 3.], index = j),
}
_sliceDb(db, 3)
check('t sliced+renumbered', list(db['t']) == [0, 1, 2])
check('txE sliced+renumbered', list(db['txE']) == [0, 1])
check('tj level renumbered', sorted(db['tj'].get_level_values('t').unique()) == [0, 1, 2])
check('x sliced+renumbered (values preserved, not recomputed)',
      list(db['x'].index) == [0, 1, 2] and list(db['x'].values) == [13.0, 14.0, 15.0])
check('x[t-1] sliced+renumbered (its own already-lagged values, untouched)',
      list(db['x[t-1]'].values) == [12.0, 13.0, 14.0])
check('df sliced+renumbered', list(db['df'].index) == [0, 1, 2])
check('scalar untouched', db['scalar'] == 3.14)
check('type-only (j-indexed) series untouched',
      list(db['typeOnly'].index) == [0, 1, 2] and list(db['typeOnly'].values) == [1., 2., 3.])
check('j index (non-t) untouched', list(db['j']) == [0, 1, 2])

# ---- 2. createCopyFromt0: structural consistency on the real instance
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
for k in ('α', 'ν', 'ξ', 'ρ', 'ω', 'βi', 'γi'):
    check(f"db[{k!r}] index matches new db['t']", list(mt0.db[k].index) == list(mt0.db['t']))

mtKeep = m.createCopyFromt0(m.db['t'][calPos])
check("db['t0'] == 0 when sliced exactly at the calibration year", mtKeep.db['t0'] == 0)
try:
    m.createCopyFromt0(m.db['t'][-1] + 1)
    check('t0 outside db[t] raises ValueError', False)
except ValueError:
    check('t0 outside db[t] raises ValueError', True)

# ---- 2b. US-specific: the zero-mass slot, and what happens to db['dates']
check('the zero-mass informal slot survives the slice (gamma_0 still 0 everywhere)',
      float(np.max(mt0.db['γ0'])) == 0.,
      '-> max gamma_0={:.1e}'.format(float(np.max(mt0.db['γ0']))))
check('eta_0/X_0 stay finite on the copy (0*NaN would poison the FOC)',
      np.isfinite(mt0.db['ηj'].values.astype(float)).all()
      and np.isfinite(mt0.db['Xj'].values.astype(float)).all())
check("db['dates'] is STALE on a copy -- full length, original calendar, not sliced",
      len(mtKeep.db['dates']) == T and list(mtKeep.db['dates']) == list(m.db['dates']),
      '-> len(dates)={} vs len(t)={}, dates={}...'.format(
          len(mtKeep.db['dates']), len(mtKeep.db['t']), list(mtKeep.db['dates'])[:3]))
check("...and the reason is that db['dates'] has no name, so _sliceDb never sees it",
      m.db['dates'].name is None,
      '-> Index.union() drops the name; testmod.dates comes from datesLog.union(...)')

# ---- 3. behavioural round trip: no actual shock -> the copy reproduces the baseline's own tail
base = m.solvePEE_LOG()
seed = m.stateAtT0(base['report'], t0)
shocked = mt0.solvePEE_LOG(**seed)

for name, key in (('s', 's'), ('h', 'h'), ('R', 'R')):
    d0 = abs(base['report'][key].xs(t0) - shocked['report'][key].xs(0))
    check(f'report[{name}] at t0 matches baseline (no shock)', d0 < 1e-6, f'-> |diff|={d0:.2e}')
dTau0 = abs(base['τ'].xs(t0) - shocked['τ'].xs(0))
check('tau at t0 matches baseline (no shock)', dTau0 < 1e-6, f'-> |diff|={dTau0:.2e}')

tailOffset = min(2, mt0.T - 1)
tailOrig, tailNew = m.db['t'][t0Pos + tailOffset], mt0.db['t'][tailOffset]
for name, key in (('s', 's'), ('h', 'h')):
    dTail = abs(base['report'][key].xs(tailOrig) - shocked['report'][key].xs(tailNew))
    check(f'report[{name}] later in the tail matches baseline (no shock)', dTail < 1e-6,
          f'-> |diff|={dTail:.2e}')

# ---- 4. LOG.solveRobust runs on the copy (caches genuinely cleared, not stale-shaped)
polShocked = mt0.LOG.solveRobust(mt0.db['θ'].values, mt0.db['eps'].values)
check('LOG.solveRobust runs on the copy without error', 'τ' in polShocked)

report()
