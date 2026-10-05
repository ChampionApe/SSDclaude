# Brief: the frozen-share selection among tax candidates in the two informal models (2026-10-02)

For the `model-coder` agent. One change in two modules: the selection among tax candidates in
`python/informalAnalytical/policy.py` and `python/InformalSavings/policy.py` moves from
`roots1d.selectMax`/`selectMaxND` (candidates ranked by the integral of the consistent condition) to
`roots1d.selectMaxFrozen`/`selectMaxFrozenND` (every candidate tested and ranked at its own frozen
shares), exactly as the US module did on 2026-10-02 (finding #18). The counts travel into the solve
outputs and the Argentine drivers' csv rows. Nothing under `results/` or `writing/` changes. Another
agent is working in `python/US/` and `python/paper/` at the same time: do not touch those folders or
`python/runTests.py` (extend the existing suites, add none).

## 1. Read first

`writing/informalSavings/num_robustroot.tex` and `writing/informalAnalytical/num_robustroot.tex`
(*Selecting among several roots*: `eq:candidates`, `eq:objectiveProfile`, `eq:equilibriumTest`, the
selection and the fallback) and the paragraph *Root problems that are not maximisations* (the ι fixed
point is a root, not a maximisation: neither the test nor the selection applies to it).
`python/gridsearch/roots1d.py` (`selectMaxFrozen`, `selectMaxFrozenND`, `interpAlong`,
`cumtrapzColumns`): the rule and the callback contract. The US wiring as the template:
`python/US/policy.py` (`LOG.objectiveFrozen`, `LOG._select`, `LOG._selectND`, `LOG.solveRobust`,
`CRRA.objectiveFrozen`, `CRRA.focParts_t`, `CRRA.zAtShares`, `multiplicitySummary`), `python/US/model.py`
(where `multiplicity` enters the solve outputs), `python/US/test_frozenSelection.py` (the quick-test
pattern), the 2026-10-02 (later) entry of `python/US/RESEARCH_LOG.md`. Each module's `README.md` and
`RESEARCH_LOG.md`; `notes/crossCuttingFindings.md` #4, #10, #13, #18.

## 2. What is frozen, and what is not

- **The formal retirees' shares** $s_{t-1,i}/s_{t-1}$ (`d['si_s_']`, `base.si_s` at vintage $t-1$) are
  the predetermined state that $z_t$ substitutes consistently with each node of $\mathcal T$. Under LOG
  they are a function of the candidate's tax and $\theta_t$ alone ($B = \beta$); under CRRA also of the
  hours at the candidate's tax through $B_t(s_{t-1}, h_t)$, with $h_t$ interpolated linearly along
  $\tau$ at the candidate (`interpAlong`), as `US.CRRA.objectiveFrozen` does. Freeze them per candidate.
- **The informal state** $\iota_{t-1}$ (InformalSavings) and the level $s_{t-1}$ (CRRA) are grid states:
  constant along $\mathcal T$ within a column, so already frozen. The ι fixed point along $\tau$
  (`solveStateApprop_t`, `_rootIota`, `_iotaOfTauS`) is a root problem and stays as it is.
- **The informal retirees' and the young's terms** of $z_t$ do not involve the formal shares; they are
  the same at every candidate of a column and are reused, not recomputed.

**The frozen objective** of a candidate $c$ in a column: $z_t$ re-evaluated along the column with the
formal shares frozen at $D_c$, integrated by `cumtrapzColumns` from the first feasible node, plus the
formal retirees' level at that node at $D_c$ (`Σ old_i · υ_2^i` with `c2i` at $D_c$; under LOG `ln c2i`,
under CRRA `c2i^q/q`, the political weights of `base.politicalWeights` or the module's equivalent). The
young's and the informal retirees' levels at the first node are common to the column and drop out. The
callback must integrate the condition with its numerical derivatives (CRRA `t < T`), not raw utility
levels (finding #18, #4). Shapes: `cand (K, N)` in, `W (K, M, N)` out, NaN where infeasible, as
`selectMaxFrozen`'s docstring says.

## 3. Files and functions

**`python/informalAnalytical/policy.py`**
- `LOG.focGrid(d, t, θ, ε, terminal)` already takes the shares from `d['si_s_']`: add
  `LOG.objectiveFrozen(cand, τGrid, d, θ, t, ε, tLag, terminal)` on the US pattern without the zero-mass
  guard (the informal old's term `dv20_dτ_LOG` is in `focGrid` and carries no shares), `LOG._select` /
  `LOG._selectND` with the `selection` attribute (`'frozen'` default, `'legacy'` the earlier criterion
  with counts `-1`), and wire `solveBackward_t` (the windowed grid `g`: the callback runs on the window;
  pass `Δl = Δu = n` for the full count where the US does) and `solveRobust` (`check = True` as the US:
  the full-grid pass on every solve, the gradient solution kept bitwise when it is the selected
  equilibrium; report the cost per solve).
- `CRRA.focGrid_t(d, g, t, θ, ε)` computes the splines inline: split it into `focParts_t(d, g, t, ε)`
  (every numerical τ-derivative, `dv1i`, `dv10`, `dv20`, `dlnh`, `p`) and `zAtShares(d, parts, θ, si_s_,
  t)` (the formal retirees' term rebuilt at given shares) so that `focGrid_t` is `zAtShares` at
  `d['si_s_']`, **bitwise** what it was; add `CRRA.objectiveFrozen` (terminal through `focGrid_T` with
  the shares replaced, `t < T` through `zAtShares`) and wire `solveTerminal` and `solveBackward_t`
  through `_selectND`.

**`python/InformalSavings/policy.py`**
- LOG: `zbar_T(d, θ, t)` / `zbar_t(d, θ, t, s)` hold the τ-only part including the formal retirees'
  term; `_zState` adds the ι part per column. Add `zbarAtShares(d, θ, t, si_s_, parts)` (or the split
  that fits: the numerical derivatives `_gradProfile` computed once, the retirees' term rebuilt at given
  shares, with the shares now per column, shape `(M·M_ι, ni)` after broadcasting) so that the frozen
  objective is `_zState(zbarAtShares(…), τGrid, ε, ιGrid, t)` integrated along τ per column, plus the
  formal retirees' level; `objectiveFrozen`, `_select`, `selection`, and the wiring of `solveTerminal`
  and `solveBackward_t` (the feasibility mask and `minFeasible` as they are).
- CRRA: the same with the 3-D grid `g3` and `selectMaxFrozenND` along `'τ'`; the shares frozen at the
  candidate's tax and the hours there; `_positiveLevels` as it is (a NaN cell stays NaN in the callback).
- The `multiplicity` summary (`nEqMax`, `nStatesMultiple`, `nFallback`, `nCandMax`; copy
  `US.policy.multiplicitySummary` into the module or import it if the modules share nothing yet, say
  which) into every solve output that the drivers write from (`model.py`'s `solvePEE_*`-equivalents and
  `approximatePEE`), and the Argentine drivers write `nEqMax`, `nCandMax`, `nFallback` as **non-key**
  columns (finding #13) into their csvs: the calibration sweep(s) and the shock/sweep scripts that
  `python/paper/runCalibration.py` and `runShocks.py` call (find them from those two files, read-only;
  list them in the report). `-1` where a solve returns no summary, and say where.

## 4. Checks that must pass (extend the existing suites; no new suite)

Both modules, on their existing quick-test models (`test_peeLOG.py`, `test_peeCRRA.py` in
InformalSavings; `test_crraTerminal.py`, `test_crraBackward.py`, `test_crraPEE.py` and the LOG suite in
informalAnalytical), the US `test_frozenSelection.py` pattern:

- **F1** The τ-derivative of the frozen objective at the shares consistent with the evaluation point
  equals the solver's own $z_t$: to `1e-6` under LOG (closed form) and at the CRRA terminal period, at
  three taxes and two states (ι, and $s_{t-1}$ under CRRA).
- **F2** Bitwise the earlier criterion wherever a state has exactly one equilibrium (`nEq == 1`): the
  selected τ equal, and `nEq.max()`, `fallback.sum()` reported. Record, before any change, one
  reference number per solver (the sum of the selected τ over the state grid at the terminal period and
  at one `t < T`) and quote it against the changed path.
- **F3** The CRRA split: `focGrid_t` after the split equals the pre-split `focGrid_t` bitwise on the
  quick-test grid (record the sum of $z$ before the change).
- **F4** Every solve output carries the counts; `solveRobust(check = True)` returns the gradient
  solution bitwise where it is the selected equilibrium (informalAnalytical LOG).
- **F5** The ι fixed point is untouched: `solveStateApprox_t`'s outputs bitwise before and after.
- The fast registry stays green (`python\runTests.py`; the other agent may be running it too, so run
  it once at the end and quote the totals), and `InformalSavings/test_calibration.py` once (~15 min).

## 5. Report

As the agent definition says: files and functions; the verdict lines; the reference numbers before
and after; the cost of the full-grid check per solve; what was not done and why; one log entry per
module (`python/informalAnalytical/RESEARCH_LOG.md`, `python/InformalSavings/RESEARCH_LOG.md`, at most
ten lines each). The READMEs and the technical note are updated by the main session.
