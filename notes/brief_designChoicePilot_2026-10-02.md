# Brief: pilot of the two frozen-state design-choice algorithms for the CRRA leaded choice (2026-10-02)

For the `model-coder` agent. One change: implement the two choice layers that `writing/US/num_esc.tex`
states for the CRRA leaded choice as sandbox subclasses of `LeadedCRRA2D` sharing its step 1, measure
them against each other and against the current choice layer, and report. Nothing in the pipeline,
`results/` or `writing/` changes. The decision which layer becomes the production solver is taken by
the main session on the measurements, afterwards.

## 1. Context to read first

- `notes/esc_crraDesignChoiceProblem.md`: the defect (the current layer values each candidate design at
  its own consistent savings shares; the electorate cannot move them).
- `writing/US/num_esc.tex`, subsubsection *CRRA preferences*: the equilibrium at a state
  (`eq:esc:aDef`, `eq:esc:stateEq`), algorithm `esc:crra2D` (direct evaluation, root in $a$),
  algorithm `esc:crra2Dfoc` (first order condition, `eq:esc:designEnvelope`, `eq:esc:designFOC`,
  `eq:esc:designProfile`). `writing/US/num_robustroot.tex`: the selection rule both layers reuse.
- `python/US/README.md`, the top two entries of `python/US/RESEARCH_LOG.md`,
  `notes/crossCuttingFindings.md` #4, #5, #11, #14, #18.
- Code: `python/US/policyESC.py` (`LeadedBase._argmax`, `LeadedCRRA2D`: `_solveStateGrid`, `_econCore`,
  `_focParts`, `_zAtθ`, `_econAt`, `solveBackward_t2D`, `solvePolicies`); `python/US/policy.py`
  (`CRRA.objectiveFrozen`, `focParts_t`, `zAtShares`, `_selectND`, `multiplicitySummary`);
  `python/gridsearch/roots1d.py` (`selectMaxFrozen`, `selectMaxFrozenND`, `interpAlong`,
  `cumtrapzColumns`, `_quadAt`, `_allRootsRagged`, `allRoots`); `python/gridsearch/interp.py`
  (`griddedGradient1D`, `griddedSmooth1D`); `python/US/base.py` (`si_s`, `Γs`, `B`, `c2i`, `hηRatio`,
  `wedgeB`, `politicalWeights`, `FOC`); `python/US/test_frozenSelection.py` section 5 (the one-period
  2-D setup the tests reuse); `python/US/runESCcrra.py` (`buildUS`, `GSC`, the shocks stage).

## 2. The objects

State $(s_{t-1},\theta_t)$ on $\mathcal S\times\Theta$; policy $(\tau_t,\theta')$ on
$\mathcal T\times\Theta'$; $t$, $t_{lag}$, $t_1$ as in `solveBackward_t2D`.

**The frozen scalar.** With a common discount factor the inherited shares are
$D_i(a) = 1 + a\,(y_i - 1)$, $y_i$ = `hηRatio(t, lag = '[t-1]')`, and the consistent value at
$(\tau, h_t)$ given $\theta_t$ is, from the terms of `base.si_s` at vintage $t-1$,
$$a_t(\tau, h_t;\theta_t) = 1 + \frac{1-\alpha}{\alpha}\,\frac{p_{t-1}\,\tau}{\kappa_{t-1}}\;
\frac{\mathrm{wedgeB}(\theta_t,\tau,t,\text{'[t-1]'})}{1 + B_t}, \qquad B_t = \mathtt{B}(s_{t-1}, h_t, t_{lag}),$$
the parameters at vintage $t-1$ (`get('p', tLag)`, `get('κ', tLag)`, `get('α', tLag)`). Derive it from
`si_s`'s own three terms rather than from this line, and let the test (T1) say they agree. Assert a common
`βi` at `tLag` wherever `aOf` is called (raise otherwise).

**The objective at a frozen $a$.** With $q = 1 - 1/\rho$ and `old, young = weights(t)` (the
`LeadedBase` weights, i.e. `politicalWeights`),
$$\mathcal W_t(\tau,\theta';a) = \sum_i \mathrm{young}_i\,\mathrm{hatc1iPow}_i(\tau,\theta')/q
 + \sum_i \mathrm{old}_i\,c_{2,t}^i\big(h_t(\tau,\theta'), s_{t-1}, \tau, \theta_t, D(a)\big)^{q}/q,$$
exactly `_econAt`'s assembly with the shares replaced by $D(a)$. On the grid of step 1 the young's term
is `d['hatc1iPow']` and the retirees' term is closed form, so $\mathcal W_t(\cdot,\cdot;a)$ on the whole
$(\tau,\theta')$ grid of a state costs no state solve.

**The equilibrium at a state** (`eq:esc:stateEq`): $(\hat\tau,\hat\theta', a)$ with
$\hat\tau = \arg\max_\tau \mathcal W_t(\tau,\hat\theta';a)$,
$\hat\theta' = \arg\max_{\theta'} \mathcal V_t(\theta';a)$ where
$\mathcal V_t(\theta';a) = \max_\tau \mathcal W_t(\tau,\theta';a)$, and
$a = a_t(\hat\tau, h_t(\hat\tau,\hat\theta');\theta_t)$.

**The frozen tax pass** (shared by both layers; `frozenTaxPass(core, θt, a)`). For one $\theta_t$ and an
$a$ that may vary per $s_{t-1}$ (constant along $\tau$ and $\theta'$): `zAtShares(d, parts, θt, D(a), t)`
on the grid; the profile `cumtrapzColumns` along $\tau$ per $(s_{t-1},\theta')$ column (feasible
sub-grid as everywhere); $\hat\tau(\theta';a)$ = the corner if the profile's maximum is at an end node,
else the crossing of the piecewise-linear interpolant of that frozen $z_t$ nearest the maximising node
(`allRoots` / `_allRootsRagged` on the column, pick the root nearest the node); no equilibrium test
(nothing moves along the grid at a frozen $a$). $\mathcal V_t(\theta';a)$ = $\mathcal W_t(\cdot,\theta';a)$
on the grid read at $\hat\tau$ by `_quadAt` (node value at a corner). Also return $h_t$ and $B_t$ at
$\hat\tau$ (`interpAlong` along $\tau$) and the young's level at $\hat\tau$. Shapes: `(ns_, nθ1)` per
$\theta_t$.

## 3. Layer A, root in $a$ (algorithm `esc:crra2D`): `LeadedCRRA2DRoot`

Per $\theta_t\in\Theta$ (the loop `solveBackward_t2D` already has), vectorised over $s_{t-1}$:

1. The range: $a_t$ of §2 at every grid node $(\tau, s_{t-1},\theta')$ from `d['B']`, `d['τ']`, $\theta_t$;
   per $s_{t-1}$ its min and max over $(\tau,\theta')$, extended by one cell of the grid below;
   $\mathcal A$ = `Ma` equally spaced nodes (setting, default 9).
2. For each $a\in\mathcal A$: `frozenTaxPass` → $\hat\tau(\theta';a)$, $\mathcal V_t(\theta';a)$;
   $\hat\theta'(a)$ by `_argmax` over $\Theta'$ (parabola when interior, corner as corner);
   $\hat\tau(a)$ = `np.interp` of $\hat\tau(\cdot;a)$ along $\Theta'$ at $\hat\theta'(a)$, $h_t$ likewise;
   $r(a) = a - a_t(\hat\tau(a), h_t;\theta_t)$.
3. Every sign change of $r$ on $\mathcal A$ (per $s_{t-1}$) is a bracket. Close each by bisection
   (re-running step 2 at the trial $a$, all states with an open bracket at once) until the bracket is
   narrower than `aTolBracket = 1e-9`; it is a root if $|r| \le$ `aTolResidual = 1e-6` there, otherwise a
   jump (discard, count as a discarded bracket). Several roots: select the one with the highest
   $\mathcal V_t(\hat\theta'(a);a)$ (payoff dominance). None: `fallbackθ = True` and the legacy layer's
   answer for that state.
4. Report per state: `nBrθ` (brackets), `nEqθ` (closed), `fallbackθ`, `aStar`, and keep the $\tau$
   counts of step 2 of the legacy layer where it runs.

Hand-back as the legacy layer (`_handBack`), with $\theta_{\text{next}} = \hat\theta'(a^\ast)$ and
$\tau_{\text{sel}} = \hat\tau(a^\ast)$.

## 4. Layer B, first order condition (algorithm `esc:crra2Dfoc`): `LeadedCRRA2DFOC`

1. Derivatives along $\Theta'$: `griddedGradient1D(θ1Grid, ·, knots = smoothKnotsθ)` of
   $\ln h_t$ and of `lnhatc1i` on the step-1 grid (move the `θ1` axis first; the grid is
   `CartesianGrid(τ, s_, θ1)`). `smoothKnotsθ`: setting, default the grid's `smoothKnots`; `dv1i_dθ =
   hatc1iPow · ∂ lnhatc1i/∂θ'`. These do not depend on $\theta_t$ or $a$: once per period.
2. The consistent tax at each design: the legacy step 3 unchanged, `_selectND` with the
   `objectiveFrozen` callback → $\tau^\ast(\theta_t, s_{t-1},\theta')$ and its counts. Then
   $a(\theta') = a_t(\tau^\ast, h_t(\tau^\ast,\theta');\theta_t)$ with $h_t$ and $B_t$ interpolated
   along $\tau$ at $\tau^\ast$.
3. The design condition on $\Theta'$ per $(\theta_t,s_{t-1})$:
   $z^\theta(\theta') = \sum_i \mathrm{young}_i\,\mathrm{dv1i\_d\theta}_i\big|_{\tau^\ast}
   + \sum_i \mathrm{old}_i\,(c_{2,t}^i)^{q}\,(1-\alpha)\,\partial_{\theta'}\ln h_t\big|_{\tau^\ast}$,
   the young's part interpolated along $\tau$ at $\tau^\ast$ (`interpAlong`), $c_{2,t}^i$ at $D(a(\theta'))$.
4. `selectMaxFrozen(θ1Grid, zθ, frozen, rtol = 1e-9)` with `zθ` of shape `(nθ1, ns_)` per $\theta_t$ and
   the callback, for `cand (K, ns_)`: $a_c$ = `np.interp` of $a(\theta')$ along $\Theta'$ at the candidate
   (NaN-padded); `frozenTaxPass` at $a_c$ → $\hat\tau(\theta';a_c)$ for every $\theta'$; the integrand
   $\partial_{\theta'}\mathcal W_t(\hat\tau(\theta';a_c),\theta';a_c)$ = the young's `dv1i_dθ` at
   $\hat\tau(\theta';a_c)$ plus the retirees' term at $a_c$ and $\hat\tau(\theta';a_c)$;
   `W[k] = cumtrapzColumns(θ1Grid, integrand) + level`, where `level` is the full
   $\mathcal W_t(\hat\tau(0;a_c), 0; a_c)$ (young's and retirees' both, read from the grid at
   $\hat\tau(0;a_c)$): unlike the tax test, the young's level at $\theta'=0$ moves with $a_c$ through
   $\hat\tau(0;a_c)$, and the payoff-dominance ranking needs it. Returns the selected design, `nCandθ`,
   `nEqθ`, `fallbackθ`, `W`.
5. The tax at the selected design: $\hat\tau(\cdot;a_{c^\ast})$ of the selected candidate's frozen pass,
   `np.interp` along $\Theta'$ at the selected design. Fallback: the legacy answer.

Hand-back as the legacy layer.

## 5. Files

1. `python/US/policyESC.py`. Refactor `LeadedCRRA2D.solveBackward_t2D` into `_periodCore(sol1, t, tLag,
   t1, ε, ε1, sGrid, sCand, θ1Grid)` (the grid, `_solveStateGrid`, `_econCore`, `_focParts`; returns a
   dict with `g, s, nRoots, d, parts` and the arguments), `_choose(core, θ1Grid, choose)` (the current
   step 3 to step 4: the $\theta_t$ loop with `_selectND`, `_econAt` at $\tau^\ast$, `_argmax`; returns
   `τStar, atBoundτ, nEqτ, nCandτ, fallbackτ, W, θNext, atBoundθ, τSel`) and `_handBack(core, θNext,
   τSel, choose, extra)` (smoothing with pinned knots, the final `_econAt`, the tables and interpolants,
   the period dict; `extra` is merged into the dict). `solveBackward_t2D` composes the three and returns
   the same dict **bitwise** (T2). Subclasses override `_choose` only. Time the two parts into the period
   dict as `tCore`, `tChoose`.
2. New `python/US/policyESCpilot.py`: `aOf(BG, B, τ, θt, tLag)`, `sharesFrom(BG, a, t)`,
   `frozenTaxPass(...)`, `resolveAt(...)` (the state re-solved at an off-grid $(\tau, s_{t-1},\theta')$
   and $\mathcal W_t$ assembled at a given $a$, `_econAt` with the shares replaced: the check of the grid
   reading), `deviationCheck(...)` (at a state's selected $(\hat\theta', a^\ast)$: the maximum over
   $\Theta'$ of $\mathcal V_t(\theta';a^\ast) - \mathcal V_t(\hat\theta';a^\ast)$ from a frozen pass),
   `class LeadedCRRA2DRoot(LeadedCRRA2D)`, `class LeadedCRRA2DFOC(LeadedCRRA2D)`, each with the
   settings of §3 and §4 as constructor keywords and the per-state counts in the period dict under the
   names above. Docstrings name the equation labels (`eq:esc:aDef`, `eq:esc:stateEq`,
   `eq:esc:aResidual`, `eq:esc:designFOC`, `eq:esc:designProfile`).
3. New `python/US/pilotDesignChoice.py`: the measurement driver of §6. Outputs under
   `logs/pilotDesignChoice/` (create it): one csv of rows (one per measurement, with `ρ, scenario,
   nCand, ns, nθ, knotsθ, rule, period, item, value, seconds`), per-run `.npz` of the per-state policies,
   and the console log. `--report` prints the comparison tables from the csv.
4. New `python/US/test_designChoicePilot.py` (fast, under two minutes, `gridsearch.testing`'s
   `check`/`report`), registered in `python/runTests.py` as a fast suite.
5. `python/US/RESEARCH_LOG.md`: one entry, at most ten lines.

Not to touch: `runESCcrra.py`, `modelESC.py`, `python/paper/`, `results/`, `writing/`. The pilot
drives a full recursion by replacing the solver instance, `m.ESCC2 = LeadedCRRA2DRoot(m, nθ = 13, nθCand
= nCand, ...)`, before `m.solveLeaded2D(pinAtT0 = False)`; `solvePolicies` borrows `m.CRRA.GS` as now.

## 6. Measurements

Model: `runESCcrra.buildUS(ρ, wedge = {'spec': 'size', 'phi': 0.5, 'p': λ}, commonX = True, gs = GSC |
{'ns': ns}, nθCand2D = nCand)` with $\lambda$ read from `results/esc/escCalibrationCRRA.csv` (rows
`method == 'exact'`, `spec == 'size'`, `commonX`): 1.7282425096969982 at $\rho = 2$ and
18.242097713421508 at $\rho = 0.5$. The French-voting point: `frenchData(m, ρ, 'CRRA', gs = gs, commonX
= True)` then `sh.shockedCopy(m, 'frVoting', frData, SHOCKS_ESC)`, as the shocks stage of
`runESCcrra.py` does. `nθ2D = 13` unless varied. Every period chooses (`pinAtT0 = False`). Run long
items in the background through `cmd /c "... > logs\pilotDesignChoice\<name>.log 2>&1"` and monitor
the file (finding #14). Compute budget about three hours in all; if a full recursion at `ns = 50`
exceeds twenty minutes, keep M2 to $\rho = 2$ and say so.

- **M1, one period at the published resolution** (`ns = 150`, `nCand = 41`): for $\rho\in\{2, 0.5\}$ and
  the baseline and French-voting models, the terminal period and the last choosing period (as
  `test_frozenSelection.py` section 5), one `_periodCore` and the three layers on it. Record per state
  $\theta_{\text{next}}$ and $\tau$ for each layer; the maxima over states of $|\Delta\theta|$ and
  $|\Delta\tau|$ for legacy–root, legacy–foc, root–foc; the counts (`nEqθ`, `nBrθ`/`nCandθ`,
  `fallbackθ`, and the $\tau$ counts); `tCore` and `tChoose` per layer; and the two checks of M6.
- **M2, full recursions** (`ns = 50`, `nCand = 41`): $\rho = 2$ baseline and French voting, $\rho = 0.5$
  baseline; the three layers. Record the design in force at $t_0$, $\tau_{t_0}$ and `targetDrift` from
  `solveLeaded2D`, the per-period maxima over states of $|\Delta\theta|$ between layers, the
  multiplicity summaries, total seconds.
- **M3, candidate-grid sensitivity** (one period, `ns = 50`, $\rho = 2$, French voting):
  `nCand ∈ {13, 21, 41, 81}`, three layers; the choice at the state nearest $(s_0, \theta^\ast)$ ($s_0$
  from `s0FixedPoint` of a legacy recursion, or the middle of `sGrid` if that is simpler, said in the
  report) and the maximum over states of $|\theta(\text{nCand}) - \theta(81)|$ per layer.
- **M4, the derivative of layer B** (one period, `ns = 50`, $\rho = 2$, French voting, `nCand = 41`):
  `nθ2D` 13 against 21 (root and foc); `smoothKnotsθ` 4 against 8 (foc); and at three interior states
  the spline $\partial_{\theta'}$ of the young's term at $\theta' = 0.45$ against a central finite
  difference of `resolveAt`'s young's term with $h = 0.0125$ (the design-state nodes sit at multiples
  of $1/12$, so $0.45$ is between nodes): report the relative difference and the finite difference's
  own asymmetry (forward against backward) as the kink size.
- **M5, continuity, if the budget allows** (`ns = 50`, `nCand = 41`, baseline, $\lambda = 8.643$ held
  fixed as `test_escCRRA.py` does): $\rho\in\{1.10, 1.05, 1.02\}$, root and foc, the choice at $t_0$
  against `LeadedLOG`'s at the same $\lambda$; the ratio gap/($\rho - 1$).
- **M6, the two checks on both layers**, inside M1 at every state: `deviationCheck` (expected at most
  the parabola's resolution, report the maximum) and `resolveAt` against the grid reading of
  $\mathcal V_t$ at the selected policy (report the maximum absolute and relative difference).

## 7. Checks that must pass (`test_designChoicePilot.py`)

Setup as `test_frozenSelection.py` section 5: `ModelESC` at $\rho = 2$, `wedge = {'spec': 'size',
'phi': 0.5, 'p': 1.728}`, `nθ2D = 5`, `nθCand2D = 13`, `sGrid` of 25 nodes, the terminal period and the
last choosing period.

- **T1** `sharesFrom(aOf(B, τ, θ))` equals `si_s(B, τ, θ, Γs(B, τ, θ), tLag)` to `1e-13` at twenty
  random $(B, \tau, \theta)$ under the `'size'` wedge; `aOf` raises when `βi` differs across types.
- **T2** The refactored `LeadedCRRA2D` reproduces the pre-refactor period dict bitwise: before touching
  `policyESC.py`, record from the setup `float(np.nansum(per['θNext']))`,
  `float(np.nansum(per['τStar3']))`, `float(per['τ'][0, 0])` and `int(per['nEqτ'].sum())` and quote them
  in the report; after, the test asserts equality.
- **T3** Root and foc each run the period; every state has `nEqθ == 1` and no `fallbackθ`; the maxima
  over states of $|\Delta\theta|$ (root–foc) and $|\Delta\tau|$ are reported and asserted at most one
  candidate cell and one $\tau$ cell respectively.
- **T4** The frozen tax pass ties to the tax rule: at each $(\theta_t, s_{t-1},\theta')$ of the legacy
  layer with `nEqτ == 1`, the pass at $a = a_t(\tau^\ast, h_t(\tau^\ast))$ returns $\hat\tau = \tau^\ast$
  to `1e-10`.
- **T5** Layer B's derivative: the spline $\partial_{\theta'}$ of the young's term against the central
  finite difference of `resolveAt` at three interior states, $\theta' = 0.45$ (between the nodes of a
  5-node $\Theta$ too: $0.25, 0.5$), $h = 0.0125$: report the relative difference; assert within $25\%$,
  and report the finite difference's forward–backward asymmetry next to it.
- **T6** `deviationCheck` at the selected policy of every state, both layers: assert at most `1e-6`
  relative to $|\mathcal V_t|$; report the maximum.
- The fast registry stays green: `python\runTests.py`.

## 8. Report

As the agent definition says, plus: the M1 to M6 tables pasted from `--report`, the reference numbers
of T2 before and after, and the settings each number was produced at. Numerical claims come from a
test line or a run you made, quoted. If a measurement did not run, say which and why.
