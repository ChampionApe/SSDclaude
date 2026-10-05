# Brief: the equilibrium test's one-cell clause, restricted and merged (2026-10-02)

For the `model-coder` agent. One change to the shared package, `python/gridsearch/roots1d.py`
(`selectMaxFrozen`, and `selectMaxFrozenND` through it), with its tests, then every suite that runs
through it. Nothing under `results/` or `writing/` changes; the solvers in `python/US/`,
`python/informalAnalytical/` and `python/InformalSavings/` are not edited (their counts flow from the
package as they are), except where a test of theirs pins a behaviour this change corrects.

## 1. The defect

`selectMaxFrozen` (eq:equilibriumTest of `writing/*/num_robustroot.tex`) accepts a candidate as an
equilibrium if its own frozen objective is maximised at it within `rtol`, **or** if the node maximising
that objective lies within one cell of it (`near`). The second form was meant for an interior crossing
next to an infeasible node, where `_quadAt` can only interpolate linearly and understates the
candidate's value. It is applied to every candidate, corners included. On the Argentine headline
instances (`python/InformalSavings`, common X, $\rho = 1, 2, 0.5$) a lower corner next to a crossing
within about 1.5 cells then passes although its own profile is maximised at the adjacent node, the
payoff-dominance ranking compares the two at different frozen states and picks the corner, the walked
tax jumps by up to a cell, and the calibrated CRRA point no longer survives grid refinement
(`InformalSavings/test_calibration.py`: residual $1.5\times10^{-3}$ at $60\times60$ against
$8.6\times10^{-12}$ on its own grid; $1.1\times10^{-5}$ under `'legacy'`). Report and diagnostics:
`python/InformalSavings/RESEARCH_LOG.md` (2026-10-02), `logs/informalFrozen/diagProd_rho*.log`,
`classifyEq_rho*.log`, `IS_test_calibration_final.log`. The same clause let a corner design pass in
the US pilot (`test_designChoicePilot.py`, T3 foc). Finding #5 (a resolution-dependent jump inside a
differentiated residual), #18.

## 2. The change, in `selectMaxFrozen`

1. **The one-cell clause applies only where the value test cannot be read precisely**: an interior
   candidate whose three-node stencil in `_quadAt` contains a non-finite node (the linear fallback).
   Corners, feasible-edge endpoints and interior candidates with a full stencil pass the value test
   alone, `Wc >= Wmax - slack`. Make `_quadAt` expose the fallback (a second return, or a helper
   `_stencilFallback(x, W, cand)` that `selectMaxFrozen` calls).
2. **Candidates closer than one cell are one equilibrium at the grid's resolution.** After the test,
   per column, cluster the passing candidates by `|x_i - x_j| <= 1.001 * cell` (transitively). A
   cluster is represented by its interior crossing, since that is located at sub-grid precision and
   moves continuously with the data, with the highest own objective if it has several; a corner in a
   cluster with an interior crossing is dropped; a cluster of corners alone keeps the corner. `nEq`
   counts clusters. Add to the output `nEqRaw` (passing candidates before merging) and `nMerged`
   (candidates absorbed), scalars when the input was 1-d, and carry them through
   `selectMaxFrozenND`. The selection among clusters is unchanged (`select`), as is the fallback.
3. Docstring: say what the code does now (the two forms and when each applies, the merge and its
   reason); the history goes to `python/gridsearch/RESEARCH_LOG.md`, at most ten lines; one line in
   `python/gridsearch/README.md` where the rule is described.

## 3. Tests (`python/gridsearch/test_roots1d.py`, extend the frozen section)

- **R1** A column whose consistent condition crosses downward 1.5 cells above the lower corner, with a
  frozen-objective factory under which the corner's own profile has its maximum at the adjacent node
  (above the corner's value by more than the slack) and the crossing's own profile is maximised at the
  crossing: before the change both pass (`nEq == 2`, the corner selected); after, `nEq == 1`,
  `nEqRaw == 1`, the crossing selected, `atBound` False. Build it from `_frozenFactory`'s pattern.
- **R2** The feature kept: an interior crossing whose stencil touches an infeasible (NaN) node, whose
  linear reading falls below the node maximum by more than the slack, still passes through the clause;
  `nEq == 1`.
- **R3** Two interior crossings within one cell of each other, both passing: `nEqRaw == 2`,
  `nMerged == 1`, `nEq == 1`, the one with the higher own objective selected.
- **R4** The existing tilt test (two well-separated equilibria, `nEq == 2`, payoff dominance) is
  unchanged, and `selectMaxFrozenND` returns the two new keys in `stateShape`.
- Then the suites that run through the rule, quoting the totals: the fast registry
  (`python\runTests.py`), `InformalSavings/test_calibration.py` (the two failing checks of
  `logs/informalFrozen/IS_test_calibration_final.log` must pass; quote their lines), and the two slow
  US suites `US/test_escCRRA.py` and `US/test_escTiming.py` (their pinned numbers must not move; say so).
  A suite elsewhere that pins the old behaviour (a count that included a clause-passing corner) is
  adjusted with the old and new values quoted.

## 4. Measurement

Re-run the diagnostics behind the InformalSavings report at $\rho = 1, 2, 0.5$ (the scripts behind
`diagProd_rho*.log`, or their equivalent): the number of states with `nEq == 2` before and after, the
maximum move of the walked tax against `'legacy'`, and the recalibrated $\beta$ at $\rho = 1$
(`'legacy'` 0.650578, the clause 0.650178). Expected: the near-corner states resolve to the crossing,
`nEq == 1` everywhere or nearly, and the moves against `'legacy'` fall to the crossing's own location
error. Report whatever is measured.

## 5. Report

As the agent definition says: files and functions; the verdict lines of R1 to R4 and the suite totals
verbatim; the diagnostics before and after; the log entry.

## 6. Two counterparts in `python/US/policy.py` (`CRRA.objectiveFrozen`), same change

The informal wiring found two edge cases in the frozen objective that the US template shares and did
not touch (`python/InformalSavings/RESEARCH_LOG.md`, 2026-10-02, "departures"): (a) a candidate sitting
on a node at the upper end of the feasible sub-grid, next to an infeasible cell, gets NaN hours from
`interpAlong` and so a NaN objective, which removes it from the candidate set; read the hours at the
node for a candidate that sits on one. (b) At $\rho = 1$ the retirees' level `c2k**p/p` is undefined
(terminal period only; `_requireCRRA` refuses `t < T`); use `ln c` there, as the informal modules do.
Apply both to `US.CRRA.objectiveFrozen`, add one check each to `python/US/test_frozenSelection.py`
(section 2 or 5: an upper-end candidate next to an infeasible cell is finite; the terminal frozen
objective at $\rho = 1$ is finite and its derivative equals $z_T$), and run that suite. `test_esc.py`'s
pinned numbers must not move (quote the suite total).
