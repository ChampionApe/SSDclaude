# TODO — finish the endogenous-θ permanent timing (open since 2026-08-24)

**What changed.** The permanent choice of `θ` pinned `s_{t0-1,i}/s_{t0-1}` at the **incumbent** design.
Pinning is right (savings are sunk at the vote, and a moving ratio breaks the concentration result); the
*value* was wrong — the vote at `t0` is anticipated, so the equilibrium is the fixed point
`θ* = argmax_θ W(θ ; siRatio(θ*))`. Code, docs and `test_esc.py` (34/34) are done; the calibrated wedge is
unchanged to 12 digits (`p = 0.375032266276`) because the calibration target *is* the fixed-point
condition. See `crossCuttingFindings.md` #11b and `writing/US/num_esc.tex` §ESC:permanent.

## What is left

**1. `PermanentCRRA` has never been executed** — the only real risk here. It was restructured
substantially (candidate solves cached in `_grid`, new `W` signature and `solveFixedPoint`) and no test
covers it. Smoke it at one ρ first (~4 min):

```
.venv\Scripts\python.exe python\US\runESCcrra.py --stage permanent --rho 2.0 --spec scale --phi 0.5
```

Expect `θ_perm = 1.0000, corner=True`. Every row of the old CRRA file was a corner, where the two pinnings
*cannot* differ (finding #10's trap), so this confirms the code runs, not that the timing change works
under CRRA. Then the full trace (~25–30 min):
`runESCcrra.py --stage permanent --rho 1.1 1.2 1.3 1.4 1.5 2.0`.

**2. Regenerate `results/esc/escPermanent{,CRRA}.csv`.** Both were the pre-timing-change vintage —
`θPerm` was the incumbent-pinned reading and the `converged`/`θPermIncumbent` columns were missing — so
they were deleted rather than left beside live code (finding #8); they are at `c958031^` if needed.
Nothing in `python/paper/` reads them. To rebuild (~10–15 min):

```
.venv\Scripts\python.exe python\US\runESC.py --stage permanent --spec scale flat --phi 0.25 0.5 0.75
```

Checks on the output: `p` for (`scale`, φ=0.5) must come back **0.37503226627596936**, and on every
calibrated row `θPerm ≈ θPermIncumbent ≈ θStar` (they coincide by construction at the calibration point).

## Reference numbers for the reruns

| | fixed point | incumbent pinning | moving (wrong) |
|---|---|---|---|
| `p = 0.4` (test_esc's wedge) | 0.775076 | 0.773380 | 0.9096 |
| `p = 0.375` (permanent's own calibration) | 0.738226 | 0.738226 | 0.8694 |
| `p = 0.25` | 0.541576 | 0.549211 | 0.652294 |

The middle row is the calibration point, where the first two columns must agree exactly. The others are
where the timing actually bites.
