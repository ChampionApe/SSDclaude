# Brief: the root-in-$a$ design layer becomes the production CRRA design solver (2026-10-02)

For the `model-coder` agent. Follows `notes/brief_designChoicePilot_2026-10-02.md` and its report
(`python/US/RESEARCH_LOG.md`, entry "2026-10-02 (pilot)"; tables in `logs/pilotDesignChoice/report.txt`).
The decision, taken on those measurements: the root layer (algorithm `esc:crra2D` of
`writing/US/num_esc.tex`) is the production design layer of `LeadedCRRA2D`; the first-order-condition
layer stays in the sandbox module as the documented alternative. One change in four parts: (1) the root
layer moves into `LeadedCRRA2D` with its cost cut, (2) the design counts travel through the solvers and
the drivers, (3) the tests are re-pinned and the slow US suites run once, (4) two one-off measurements.
Nothing under `results/` or `writing/` changes; `python/paper/config.py` and the two paper stage scripts
are touched only where named below.

## 1. Read first

The pilot brief and report; `writing/US/num_esc.tex` (the CRRA subsubsection: `eq:esc:aDef`,
`eq:esc:stateEq`, `eq:esc:aResidual`, algorithm `esc:crra2D`); `python/US/policyESC.py` and
`python/US/policyESCpilot.py` as they stand after the pilot; `python/US/policy.py`
(`multiplicitySummary`); `python/US/modelESC.py` (`solveLeaded2D`, `leadedDesignAtT0_2D`);
`python/US/runESCcrra.py`; `python/paper/config.py` (the `esc` block) and `python/paper/runShocksUS.py`,
`runCalibrationUS.py` (how they call `runESCcrra.py`); `notes/crossCuttingFindings.md` #1, #5, #13, #14.

## 2. Part 1: the root layer in `LeadedCRRA2D`, at the earlier layer's cost

Move `aOf`, `sharesFrom`, `frozenTaxPass` and their helpers (`_alongτ`, `_interpRows`, `_argmaxRows`,
`_young`) from `policyESCpilot.py` into `policyESC.py` (module level, or methods of `LeadedCRRA2D`;
your call, named in the report). `LeadedCRRA2D` gains `designRule` (`'root'`, the default; `'legacy'`, the
earlier layer, kept for comparisons) and the root settings `Ma` (default 5), `aTolBracket` (1e-9),
`aTolResidual` (1e-6); `_choose` dispatches on `designRule`. `policyESCpilot.py` imports the helpers
from `policyESC` (no duplicated code); `LeadedCRRA2DRoot` becomes a thin subclass that only sets
`designRule = 'root'` (or is removed, with `pilotDesignChoice.py` and the test updated to use
`LeadedCRRA2D(designRule = 'root')`); `LeadedCRRA2DFOC` stays as it is.

Three cost changes, each measured (report the time per frozen pass and the passes per period before
and after, one period at $\rho = 2$, baseline, `ns = 150`, `nCand = 41`, `nθ2D = 13`):

- **(a) The closing step.** Replace the bisection of each bracket by a bracketed secant with a bisection
  safeguard (Illinois or Brent-style, vectorised over the open brackets as the bisection is now: one
  frozen pass per iteration for every state with an open bracket). $r(a)$ is close to linear, so four to
  six iterations should reach `aTolBracket`. Keep the jump test exactly: a bracket that shrinks below
  `aTolBracket` with $|r| >$ `aTolResidual` is a jump, not a root. Report the mean and maximum number of
  iterations per state.
- **(b) `Ma = 5`** by default (the tabulation of $r$ on $\mathcal A$ is the multiplicity detector and the
  pilot found one bracket at every state of every run); the range extension of one cell at each end
  stays. Settings remain settable from the driver.
- **(c) The crossing in `frozenTaxPass`.** Replace `_allRootsRagged` over every interior column by the
  cell-local crossing: at the maximising node $j$ of the integrated profile, $\hat z$ changes sign in
  the cell $[j-1, j]$ or $[j, j+1]$; take the linear crossing in the cell where it does (the nearer one
  if both), the node itself where neither does (a tangential maximum). Vectorised over columns, no
  grouping by NaN pattern. Test T8 shows it equals the pilot's location where the nearest root is unique.
  Also cache the young's grid objective (`_young`) in `core` once per period instead of per pass, and
  profile one pass (`cProfile`, the top ten cumulative entries pasted in the report) before and after.

Target: `tChoose` under `designRule = 'root'` at most twice `tChoose` under `'legacy'`, measured back to
back in one process on the setting above, twice, the smaller ratio reported. If the target is not
reached, report the profile and what remains; do not change the algorithm beyond (a) to (c).

## 3. Part 2: the counts through the solvers and the drivers

- `LeadedCRRA2D.solvePolicies` sets `self.lastMultiplicity` from both the tax keys
  (`nEqτ`, `nCandτ`, `fallbackτ`) and the design keys (`nEqθ`, `nBrθ`, `fallbackθ`); `multiplicitySummary`
  takes a prefix or returns the design counts under their own names (`nEqθMax`, `nBrθMax`,
  `nStatesMultipleθ`, `nFallbackθ`), so a csv row can carry both sets. Under `'legacy'` the design keys
  are absent and the summary says so (`-1`), as the tax keys do under the legacy tax rule.
- `modelESC.ModelESC.__init__` takes `designRule` and `Ma` and passes them to `LeadedCRRA2D`;
  `solveLeaded2D` and `leadedDesignAtT0_2D` return the combined `multiplicity`.
- `runESCcrra.py`: `--designRule {root,legacy}` (default `root`) and `--Ma` (default 5) reach
  `buildUS`/`buildHost`; every row it writes (calibration, path, shocks, the UK host files) carries
  `designRule`, `Ma`, and the counts `nEqMax`, `nCandMax`, `nFallback` (tax) and `nEqθMax`, `nBrθMax`,
  `nFallbackθ` (design) as **non-key** columns (the merge keys of `KEYCAL`/`KEYPATH`/`KEYSHK` stay as
  they are, finding #13; `mergeWrite` must accept rows with the new columns against a csv without them).
- The other US drivers write the tax counts `nEqMax`, `nCandMax`, `nFallback` from the `multiplicity`
  their solves return, as non-key columns: `calibrateRhoGrid.py`, `calibrateRhoGridEU.py`,
  `runShocksUS.py` (python/US), `runESC.py`, `runESCxi.py`, `stationaryApprox.py`,
  `stationaryApproxESC.py`. Where a solve returns no `multiplicity` (say which), write `-1`.
- `python/paper/config.py`, the `esc` block: `designRule: 'root'`, `Ma: 5`, with a two-line comment
  naming algorithm `esc:crra2D` and the pilot; `python/paper/runShocksUS.py` and `runCalibrationUS.py`
  forward them to `runESCcrra.py` as flags wherever they build its command.
- The readers in `python/paper/datasets.py` must not break on the new columns (they select columns by
  name; confirm with `build.py --list` and one `build.py --only US_ESC_Calibration` on the committed
  csvs, which carry no such columns yet: both must still succeed).

## 4. Part 3: tests

- `test_designChoicePilot.py` adapted to the production class; add **T8** (the cell-local crossing
  against `_allRootsRagged`'s nearest root on the pilot setup, equal to 1e-12 where that root is
  unique, and the count of columns where it is not), **T9** (the secant closing against the bisection
  closing: $a^\ast$ to 1e-9 and the same `nEqθ` at every state of the pilot setup), **T10**
  (`multiplicitySummary` returns both sets of keys from a `solvePolicies` run on the pilot setup;
  `-1` for the design keys under `'legacy'`), **T11** (the driver row builders of `runESCcrra.py`
  produce the new columns from a `solveLeaded2D` output: call the row-building code on the pilot
  setup's output, or on a synthetic `out` dict if the builders are not factored, and say which).
- `test_esc.py`, `test_escCRRA.py`, `test_escTiming.py`: every pinned number that involves the 2-D
  CRRA design moves with the layer (the pilot measured 2e-4 to 3e-3 at $t_0$). Re-pin them, and quote
  in the report each old and new value side by side with the setting; numbers that pin LOG, the
  permanent timing or the path iteration must not move (say so for each suite).
- Run the fast registry (`python\runTests.py`) and the two slow US suites once
  (`test_escTiming.py` ~75 s, `test_escCRRA.py` ~7 min): verdict lines verbatim.

## 5. Part 4: two one-off measurements (append to `pilotDesignChoice.py`, items M7 and M8)

- **M7, the grid reading against the re-solve.** One period, $\rho = 2$, French voting, `ns = 50`,
  `nCand = 41`: the root layer as is (the design value read from the grid) against the root layer with
  $\mathcal V_t$ at the final $a^\ast$ re-evaluated by `resolveAt` for the selection only (one extra
  pass): the maximum over states of $|\Delta\theta|$, and the value at the state nearest
  $(s_0, \theta^\ast)$ with $s_0$ from `s0FixedPoint` of a legacy recursion at that setting. This says
  whether the grid reading tilts the choice.
- **M8, the design-state grid at the path.** The same setting, `nθ2D` 13 against 21: the root layer's
  design at the state nearest $(s_0,\theta^\ast)$, not the maximum over states. If it moves by more
  than 0.005, say so prominently: the config's `nθ2D` is then raised in the final run.

## 6. Report

As the agent definition says, plus: the before/after pass times and pass counts and the ratio of part
1; the profile excerpt; the re-pinned numbers side by side; M7 and M8; the log entry (one, at most ten
lines, in `python/US/RESEARCH_LOG.md`). `python/US/README.md` is updated by the main session.
