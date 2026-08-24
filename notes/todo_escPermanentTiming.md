# TODO — finish the endogenous-θ permanent timing (paused 2026-08-24)

> **Status update, later on 2026-08-24:** items 3 and 4 are DONE — the research-log entries are written
> (root `RESEARCH_LOG.md` "(cont. 2)" and `python/US/RESEARCH_LOG.md` "Addendum 2"), and
> `python/runTests.py` has run clean twice (22/22). Items 1 and 2 (the `PermanentCRRA` smoke + ρ trace,
> and regenerating `results/esc/escPermanent{,CRRA}.csv`) are still open — both csvs remain the
> pre-timing-change vintage. Everything below is kept as written for the run instructions and the
> reference numbers.

## Context in one paragraph
The permanent choice of `θ` pinned `s_{t0-1,i}/s_{t0-1}` at the **incumbent** design, justified in the docs
as an "unanticipated permanent reform". That is the wrong timing: the vote at `t0` is anticipated, so the
savings made at `t0-1` were made against the design that *wins*, and the equilibrium is the fixed point
`θ* = argmax_θ W(θ ; siRatio(θ*))`. Pinning itself stays right (savings are sunk at the vote, and a moving
ratio would break the concentration result); only the value pinned at was wrong. Full write-up in
`notes/crossCuttingFindings.md` #11/#11b and `writing/US/num_esc.tex` §ESC:permanent.

## State of the tree — safe to leave, but not finished
- **Code changed and working**: `python/US/policyESC.py` (`PermanentLOG.siRatioAt`/`solveFixedPoint`,
  `PermanentCRRA._grid`/`W`/`solveFixedPoint`, `τPath` takes a path), `python/US/modelESC.py`
  (`θPathPermanent`, `solvePermanent(pinning=…)`, `permanentChoiceAtT0`), `runESC.py`, `runESCcrra.py`.
- **`python/US/test_esc.py` passes 34/34.** Nothing else in the repo imports the changed classes, so other
  work in the repo is unaffected.
- **Docs done**: `writing/US/model_esc.tex`, `writing/US/num_esc.tex`, `notes/crossCuttingFindings.md`,
  `python/US/README.md`.
- **Verified**: the calibrated wedge is unchanged — `p = 0.375032266276` under both readings, identical to
  12 digits, because the calibration target *is* the fixed-point condition. Calibration now takes 37 s.

## What is left, in priority order

### 1. `PermanentCRRA` has never been executed  ← the only real risk here
It was restructured substantially (candidate solves cached in `_grid`, `W` signature changed, new
`solveFixedPoint`) and **no test covers it** — `test_escCRRA.py` has no reference to the class. Smoke it at
one ρ before trusting anything CRRA:

```
.venv\Scripts\python.exe python\US\runESCcrra.py --stage permanent --rho 2.0 --spec scale --phi 0.5
```
~4 min (the recorded log shows 230–260 s per row). Expect `θ_perm = 1.0000, corner=True` at ρ=2 with no
wedge, matching `results/esc/escPermanentCRRA.csv`'s existing ρ=2 row. Every row in that file is a corner,
where the two pinnings *cannot* differ — which is finding #10's trap, so the smoke run confirms the code
runs, not that the timing change works under CRRA.

Then the full ρ trace to regenerate the csv with the new columns (~25–30 min):
```
.venv\Scripts\python.exe python\US\runESCcrra.py --stage permanent --rho 1.1 1.2 1.3 1.4 1.5 2.0
```

### 2. `results/esc/escPermanent.csv` is stale
The run was killed mid-scan, so the live file is the pre-session one: `θPerm` there is the
*incumbent-pinned* reading and the new `converged`/`θPermIncumbent` columns are missing. A stale result
file beside live code is finding #8.

```
.venv\Scripts\python.exe python\US\runESC.py --stage permanent --spec scale flat --phi 0.25 0.5 0.75
```
~10–15 min. Checks on the output: `p` for (`scale`, φ=0.5) must come back **0.37503226627596936**, and on
every calibrated row `θPerm ≈ θPermIncumbent ≈ θStar` (they coincide by construction at the calibration
point). Also delete `results/esc/runESCpermanent.log` from the killed run, or let the new one overwrite it.

### 3. Research log entries
Not yet written. Root `RESEARCH_LOG.md` for the cross-cutting part (#11b: pinning and *what value to pin
at* are two decisions, and the second was invisible because it is a no-op exactly at the calibration
point). `python/US/RESEARCH_LOG.md` for the model-specific part. Note that its 2026-08-23 entry (line ~387)
still carries the old "unanticipated permanent reform" justification — correct it in the new entry rather
than editing the dated one.

### 4. `python/runTests.py`
Not re-run end to end since the change (~75 s). Only `test_esc.py` was run, and it passes.

## Numbers worth having on hand when checking the reruns
| | fixed point | incumbent pinning | moving (wrong) |
|---|---|---|---|
| `p = 0.4` (test_esc's wedge) | 0.775076 | 0.773380 | 0.9096 |
| `p = 0.375` (permanent's own calibration) | 0.738226 | 0.738226 | 0.8694 |
| `p = 0.25` | 0.541576 | 0.549211 | 0.652294 |

The middle row is the calibration point, where the first two columns must agree exactly. The other rows are
where the timing actually bites.
