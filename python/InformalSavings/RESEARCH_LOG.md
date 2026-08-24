# Research log — InformalSavings

Model-specific session log. For repo-wide/structural decisions, see the root `RESEARCH_LOG.md`.

## 2026-08-10 — economic equilibrium implemented; numerical PEE section written

`base.py`/`model.py`/`policy.py` started as copies of `informalAnalytical` with the type-0 pieces stripped.

**Decisions taken (with the user).** The informal return scaler is `χR`, a 1-D parameter over `t`; the
copied `α0`/`χ` are dropped. `χ^R` carries a **period** index — the docs' `χ^R_t` in `ι_t` and `χ^R_{t-1}`
in `c_{2,t}^0` were typos; verified with `χ^R_t = 1+0.1t` (`ι` matches the corrected form to 1.4e-17,
differs from the old text by 2.5e-3), so the convention is tested, not assumed. `l_ι > 0` strictly, which
puts `dυ_{2,t}^0/dτ_t`'s pole at `ι_{t-1} = -A_tτ_t` outside the evaluation region for every `τ_t` — no
masking of the state dimension needed, and out-of-grid `ι_t` is reported infeasible, never clipped. The
savings-rate calibration target stays **formal-only**, so `ι` is a diagnostic rather than something fitted.
`χ^R` is not calibrated — fixed outside the loop, and `χ^R=1` is a knife-edge, not a neutral default.

**Why the EE needed no change.** Informal savings never enter the formal capital stock, so
`Γs`/`Θh`/`Θs`/`s`/`h`/`si_s`/`κ`/`bbar` are untouched and `ι_t` is a closed-form read-off of the solved
core rather than part of any root problem. Confirmed: `EE_CRRA_solve` at `ρ=1` reproduces `EE_LOG_solve`
bitwise for `s`/`h`.

**Trap, inherited with the copied file.** The `hRatio` bug — see the root log and `informalAnalytical`'s
entry of the same date. Found here, by `test_ee.py`'s primitive-budget checks. The two ratios are now
`hRatio` (`h_i/h`) and `hηRatio` (`h_iη_i/h`).

**Docs.** `num_peeLOG.tex` rewritten (the copy still described a stateless recursion), `num_peeCRRA.tex`,
`num_peePath.tex`, `num_calibration.tex` written; `A_t`/`R^0`/`B^0` added to `num.tex`'s auxiliary block;
`χ^R` indices corrected across the model sections.

## 2026-08-10 (cont'd) — `policy.py` implemented (LOG and CRRA), and the docs reconciled to it

`LOG` solves the backward recursion over `ι_{t-1}`, `CRRA` over `(s_{t-1}, ι_{t-1})`. `base.py` §9 grew the
marginal-utility layer: `dlnc2i_dτ` ported unchanged, `dlnc20_dτ` new and simpler (`eq:dv20` takes the
state directly instead of `Θh`), the two terminal closed forms, and the `eq:v1LOG` profiles with the
`lnRleadΘ`/`tildec10Θ` coefficient functions that make them expressible without `s_{t-1}`.

**The three doc results were the design, and all three held.** The `ι_t` fixed point is free of the
predetermined state, so the LOG state approximation stays 1-D; the rank-one decomposition reduces the whole
state grid to a broadcast (checked against a pointwise evaluation of the full product, 1.8e-12); the CRRA
unnesting is exact (checked against a nested `brentq`). The only thing `gridsearch` needed was a 2-D
interpolant.

**What the primitive-rebuild test standard bought.** The sharpest checks reconstruct the political
objective `W_t` from primitives and finite-difference it rather than comparing against our own output.
Machine precision at `t=T`, ~1e-3 absolute at `t<T` — and the test asserts the *implied τ error* against
the grid spacing rather than a magic tolerance, since what matters is that the grid, not the
differentiation, limits the answer.

**Four numerical findings, each of which changed the docs** (full tables:
`notes/informalSavings_numericalDeviations.md` items 1–4):
- *Differentiate in `ln(1-τ_t)`.* Every profile carries a `ln(1-τ_t)` term, so `dy/dτ` diverges like
  `1/(1-τ_t)`. Against a known closed form: ~1e-2 relative near `u` in raw `τ`, ~1e-15 in `x`.
- *Smoothing belongs to the policy, not the derivative.* A smoothing budget on the differentiation spline
  is 3–10× worse than an interpolating one. A smoothed policy must also be clipped back into `[l,u]`.
- *The steady-state range is the wrong reference for `𝒮_0`.* It diverges above (`u_ι ~ 1e4` as `τ→1`) and
  understates below (`ι_t` reaches 0.031 against a steady-state minimum of 0.094). The lower bound was the
  one that mattered: with the doc's factor, 188 of 450 selections were pinned to the feasibility edge.
- *Align `𝒮_0'`, refine `𝒮'`.*

**A methodological note worth keeping.** The `𝒮_0'` finding was first written up with a mechanism that was
**wrong** ("the residual is piecewise linear in `ι_t`"), caught only because writing it into the paper
prompted an isolated measurement. The residual has no curvature of its own — `ι_t` enters only through the
continuation interpolants, so *their* kinks are the error, alignment removes them and refinement creates
more straddling cells. The tell was in the original data (the error was non-monotone in the node count) and
had been read past. A confounded measurement plus a plausible story is exactly what survives review.

## 2026-08-10 (cont'd) — the path solve; two traps, one in each direction

`model.py` §6-7 and `policy.py`'s `approximatePEE` complete the chain from policy functions to a reported
equilibrium. Solved path: `τ_1 = 0.145` (LOG), `0.153` (`ρ=1.15`), no period at a corner, no state off-grid.

**Trap 1: a clip that manufactures a bracket also manufactures a root** (`notes/crossCuttingFindings.md`
#2). The first CRRA path started from `s_0 = 2e-11` because `ι_0` reached ~5e3 against `u_ι=2` and the
extrapolated policy clipped back to `u`, making the residual exactly zero. LOG was fine only by luck (the
same extrapolation undershoots `l` instead). Fixed by scanning `𝒯` with the out-of-grid region masked to
NaN, taking the lowest surviving sign change, and bracketing inside that cell.

**Trap 2, running the other way: the code quietly weakened a derivation.** `eq:forwardSim` writes the
transitions as `ι_t(τ_t)` / `s_t(τ_t,s_{t-1})` — re-solved at the walked tax. The first implementation read
them off the `ιPolicy`/`sPolicy` interpolants, which agree at the nodes and differ between them. Re-solving
is ~2 orders better (LOG `ι`: 1.2e-8 vs 4.7e-6; CRRA `s`: 1.1e-7 vs 6.6e-6) and costs one scalar root per
*period* against one per *node*. Under LOG it also preserves the structural result that `ι_t` is a function
of `τ_t` alone. Now `exact=True` by default; `exact=False` is kept because it is what measures the
difference.

The two traps are the same mistake in mirror image: reuse that is silently approximation — a bound reused
as a bracket, a solved surface reused as a transition.

**Also.** `report_t` records the candidate grids (`ιCand`, `sCand`) so the path solve re-solves on the grid
its period actually used; `ΓsPolicy` added for the CRRA warm start. `num_peePath.tex` gained the bracket
subsection, the literal reading of `eq:forwardSim`, what containment in `𝒫_t` can actually be tested (a
bounding box contains it, so failure is conclusive and success is not), and the CRRA-only NaN channel — a
path can go undefined without leaving `𝒮×𝒮_0`, because a 2-D interpolant cannot be restricted to its
feasible nodes the way the 1-D ones can.

## 2026-08-11 — the CRRA solve made ~11× faster; the calibration run for the first time

**Two exact redundancies removed.** `solvePEE_CRRA` 64 s → 5.7 s, `solvePEE_LOG` 3.1 s → 0.49 s.
- *`τ_t` reaches `eq:stateApprox` only through `Θ_h`.* `τ_{t+1}`, `h_{t+1}`, `B`, `B0`, `Γ_s` and the two
  interpolant calls behind them do not take `τ_t` — the argument lists say so. Both hot callers pass a
  `(τ,s)` Cartesian product, so `report_t` evaluated 3.2M rows where 3 600 are distinct: a 900× redundancy.
  Split into `_stateApproxSI`, evaluated once per distinct `(s_t, ι_t)` pair.
- *`selectMax` looped over 900 state columns when there were 1–2 distinct feasibility patterns.* Its
  vectorized fast path only fired on NaN-free columns, and every column was ragged — but CRRA feasibility
  is built on `(τ, s_)` and is near-constant in `ι_`. Now grouped by pattern.

**A negative result that dictated how the refactor was verified.** "Output identical bitwise against a
saved baseline" is unsound here — `notes/crossCuttingFindings.md` #1 has why, and the pattern that works
instead. Done that way: 561 arrays bitwise identical, with the reference implementation's call counts
checked to confirm it was genuinely exercised.

**The calibration converged on the first run.** LOG, 26 evaluations / 16 s to `max|residual| = 2e-10`:
`β=1.212188, ω=2.638654, η0=0.325548, X0=0.408116`, `ι(t0) = 0.3618` — inside `(0,1)` and inside its own
state grid, the docs' closing check. (Superseded twice since; the current pair and the history of moves are
in the README's calibration entry.) CRRA at `ρ=1.02` warm-started from it lands within 2.5% on every
parameter, the docs' cross-check and a real one since the two solvers share no code path.

**Two findings that changed `num_calibration.tex`** (deviations items 11–12; both later revisited by item
17 — read them as the baseline, not as current advice):
- *The doc's "main numerical hazard" does not occur, and its remedy is backwards.* It predicts a
  `√(machine eps)` Jacobian step "will return noise". Measured, the difference quotient is flat from
  `h=1e-9` to `1e-5` (≤9e-5 relative on all four columns) and only moves at `1e-3` and above. The mechanism
  is in the doc's own preceding paragraph: the policy interpolants are piecewise linear in the state, so a
  small step stays on one linear piece and returns its slope, while a large step averages across kinks.
- *For CRRA the hazard is real, but it is the grid, not the step* — `notes/crossCuttingFindings.md` #3.
  Both of the usual reassurances (solver success, small residual) were true at the wrong answer, and only
  refining the inner grid at fixed parameters told the two cases apart.

**Deliberately not done then:** the CRRA default grid stayed `30×30`. At fixed parameters the solved path
barely moves with resolution (`τ(t0)` 0.12727 at `30×30` vs 0.12879 from `45×45` on; `ι(t0)` within 0.2%).
Worth knowing for figures: the path's **first two periods** wobble ~3e-3 at every resolution tested and do
not settle monotonically, while `τ(t0)` converges cleanly — they are the least-resolved part of the path.

**Doc re-check (completed, nothing outstanding).** A label audit fixed three dangling citations inherited
from the copy (`eq:w0`→`eq:factorPrices0`, `eq:fast`→`eq:focbounded`, `eq:hatc1i`→`eq:hatc1`) and, on the
doc side, two omitted arguments (`θ_{t+1}` in `eq:auxiliary:Gammas`, `ε_{t+1}` in `eq:auxiliary:s0_s`),
stray `t` subscripts in `eq:auxiliary:ThetahT`, and `Γ_{h,t}` written transposed in 26 places. Not
re-checked: `model_setup.tex` in full, the formal block of `model_competitiveequilibrium.tex`,
`model_finitehorizon.tex`, `num_robustroot.tex`.

## 2026-08-11 (cont'd) — calibration across a grid of `ρ`

**What was built.** `gridsearch/continuation.py` (`marchGrid`) holds the model-agnostic part and is
documented in that package's log. Here: `model.py` §8.1's `calibratePoint`/`calibrateGrid`/
`_calGridSettings`/`_calVerify`, the resumable `calibrateRhoGrid.py`, and `test_calibrationGrid.py`.

**Storage: data, not pickles — decided on evidence.** The model instance pickles unchanged (62 kB, and a
round-trip reproduces the residual exactly). But `sols` does not: the LOG policy functions pickle (554 kB),
the **CRRA ones do not at all**, because `gridsearch.griddedInterp2D` returns a closure. So the record of a
calibration is a CSV row — reconstructing a solved model from it costs one `_calSetPars` and one ~25 s
solve against ~10 min to re-calibrate, and a CSV survives code changes a pickle does not. Pickled instances
are a cache; `sols` is not stored.

**Three findings.**
1. *The CRRA outer finite-difference step.* A `ρ=1.1` calibration ran 20+ minutes without converging. The
   `η0` column of the outer Jacobian came out at `5.13` at scipy's default step against `0.99` at `h=1e-4`,
   while `β` (0.132) and `X0` (0.996) were stable at every step — one corrupted column spoiling the Newton
   direction. `_calOuterKwargs` set `options={'eps': 1e-4}` for CRRA. **Retracted 2026-08-19** (item 17):
   the corrupted column was `smoothKnots`' residual jumps being straddled at that step, not a property of
   the CRRA residual.
2. *The interpolants, which were the real cause.* With the step "fixed" the search still stalled near
   `3e-5`, and refining the inner grid made the residual *grow* (`3.3e-5 → 1.5e-4 → 2.9e-4` at 45/60/75) —
   the item-12 diagnostic returning the wrong sign. The cause is the *kind* of continuation interpolant:
   piecewise-linear surfaces make the outer residual only piecewise `C¹`, and refinement moves the kinks
   closer together without removing them. With cubic, the same calibration reaches `1.33e-11` in **12**
   evaluations and the refinement trend reverses. The parameters differ by 0.016% in `β`, so the linear
   answer was never badly displaced — the solver simply could not descend to it. `interpKind` became a
   `_gridSettings` entry, defaulting to `linear` so existing results were unchanged (the default is still
   `linear`; both solvers are now handed `cubic` explicitly — see the README's Conventions and #7). Item 14.
3. *`η0` and `X0` are barely unknowns.* The Jacobian at `ρ=1.1` is diagonal-dominant in exactly those two
   rows (`-0.80`, `-1.00`, negligible off-diagonals), and across a three-point march they move **0.00% and
   0.02%** against 29%/22% for `β`/`ω`. The four-parameter root could be reduced to two. **Deliberately not
   done** (the user's call): an efficiency change, not a fix, since the 4-D system is well-conditioned
   (condition number 11.0, row correlations ≤ 0.81). Related: the residual *scaling*'s stated justification
   was stale — it claimed `η0 ~ 0.2, X0 ~ 2.6`, but calibrated `X0` is 0.408 and 2.6 is `ω`'s value. All
   four targets are `O(0.1–0.5)`, so relative-versus-level scaling is close to immaterial.

**Two process notes.** I twice reported a conclusion a proper measurement then overturned — that the
residual was *bitwise* flat and the Jacobian identically zero (a trace printed `x` at 4 decimals, hiding a
1.5e-8 perturbation), and that the four equations were near-collinear (condition number 11). Both were
plausible from partial evidence, both wrong, and the measurement was cheap in each case. Separately: a
40-minute run with fully buffered output is indistinguishable from a hung one — `calibrateRhoGrid.py` sets
`line_buffering=True`, and long runs should be started with `python -u`.

## 2026-08-12 — `createCopyFromt0`: model copies for shock experiments

`model.py`'s `createCopyFromt0`/`stateAtT0`: solve the baseline PEE over the full horizon, copy the model
with its horizon restricted to `t≥t0` and renumbered to start at 0, re-solve seeded from the baseline's own
state at `t0`. `_sliceDb` is shared verbatim with `informalAnalytical`, whose README/log documents the
mechanism once (renumbering vs. restriction, in-place `db` mutation, the `db['t0']` shift/`None` rule).

**The one addition specific to this module: `stateAtT0` carries a second, asymmetric state.** `s_` reports
lagged, so `report['s_'].xs(t0)` is directly the state entering `t0` — but `ι` reports on the `txE` domain
as `ι_t` (unlagged), so the state entering `t0` is `report['ι'].xs(t0-1)`, **except** at `t0 == db['t'][0]`
where `t0-1` has no entry and the value must come from `init['ι']`. Getting this wrong passes a
same-instance smoke test and fails only on a genuine shock, so `test_createCopyFromt0.py` pins the branch
with a sentinel `init['ι']` that must appear verbatim only at `t0 == db['t'][0]`.

**Session note.** Implemented in the prior session; the README/log update was missed before that session
ended and was filled in from the code and tests on disk rather than from conversation history.

## 2026-08-12 (cont'd) — the `ρ` sweep run; `ρ=0.7` resists (attribution later found wrong)

First full run of `calibrateRhoGrid.py --lo 0.5 --hi 2.0 --step 0.1`. 15 of 16 points solved cleanly;
`ρ=0.7` did not, across six attempts and four strategies. **This entry's conclusion was wrong** — see
2026-08-19 below and `notes/informalSavings_resolvedIssues.md`. Kept for the two parts that survive.

*What the ladder actually ruled out.* The march's own extrapolation/carry/step-halving; a warm start
interpolated from the solved `ρ=0.6`/`0.8` neighbours (residual there 4.4e-3, component-wise bracketed,
`nRoots=1` — an unremarkable surface, so "the starting points were bad" is out); and a step-size probe
showing every column except `X0` unstable across `h ∈ [1e-6, 1e-2]`, so no step size fixes it. With
`maxHalvings=4`, `ρ=0.7875` solved cleanly but `ρ=0.78125` took **37 evaluations / 1359 s**, and a retry of
`ρ=0.775` warm-started from 0.00625 away landed at 3.3e-6 — statistically identical to attempts started
100× further out. A closer start bought nothing.

*The misreading, worth keeping as an example.* That plateau-under-improving-start was read as
grid-limited (`notes/crossCuttingFindings.md` #3) and the planned next step was refining to `nι=ns=60`. The
signature was read correctly; the attribution was wrong, and the planned refinement would have cost half an
hour and closed nothing. Two contributing habits: the step-size probe was run at an **off-root** point
(residual 4.4e-3) while the `ρ=1.1` measurement it was compared against was taken at a converged one, and
its own caveat was recorded but not acted on.

*A cost note worth keeping.* A **failed** calibration attempt in this pocket averaged ~26 minutes (scipy
iterates far longer before declaring non-convergence than it does to converge) against ~6 minutes for a
success elsewhere on the grid. A stuck point costs much more to diagnose than a solving one costs to
compute.

## 2026-08-19 — `ρ=0.7` solved: a discrete choice inside a differentiated residual

`ρ=0.7` — the one point of the sweep that never calibrated, after six attempts across four strategies —
now solves in **11 evaluations, first attempt, no step-halving**, `residual` 5.96e-12. Two independent
changes, addressing two different problems.

**The cause was not what the previous session concluded.** Its reading was that the plateau under an
improving warm start meant grid-limited, and the planned next step was refining `nι=ns=60` at `ρ=0.775`.
The signature was read correctly; the attribution was wrong. `gridsearch.interp.griddedSmooth1D` used
`UnivariateSpline(s=1e-5)`, and FITPACK chooses its knot *count* from the data — an integer that flips as a
parameter moves. That put ~3.5e-6 jumps in the calibration's outer residual, against a 1e-6 tolerance, so
where a root fell inside a jump it **did not exist in the discretized problem** and no warm start could
reach it. The planned refinement would have cost half an hour and closed nothing.

Full measurement chain, the two provocations that fail to find the bug, and the numbers:
`notes/informalSavings_resolvedIssues.md`. Transferable form: `notes/crossCuttingFindings.md` #5, which is
where the diagnostic recipe belongs — it is not specific to this model or to splines.

**Two process notes worth keeping.**
- *Run diagnostics at converged points.* The previous session's finite-difference probe was taken at an
  off-root point and its own log flags the caveat; re-running it at the two converged flanking points
  removed the caveat and, more usefully, produced the column-stability table that pointed straight at the
  jump. The pickled instances made this cheap — this is what they are for.
- *Aggregate counters did not find it.* Feasibility totals, root counts and `selectMax` counts were all
  unchanged across the jump. What found it was diffing the **per-period** policy arrays against a control
  step and noticing the divergence begins exactly at `t=2` — the first period, going backward, carrying
  infeasible cells, hence the first whose smoothing spline is fitted on a masked node set.

**The grid retune, and why it is deliberately not automatic.** Separate change: the smoother made the
residual continuous, the grids made it *resolved*. `padι` now anchors **both** `𝒮_0` bounds on
`min_τ ι*(τ)` and `𝒮` anchors on `s*(0.3)`; occupancy 49–52% → 78–80% (`ι`), `verifyResidual` across
`ρ ∈ [0.7,0.9]` from a rising 1.2–3.1e-4 to a flat 3.3–4.5e-5. Deviations note item 16 has the anchors and
their spreads; the discarded candidates are as informative as the chosen ones (`s*(0)` is *perfectly*
anti-correlated with the reachable set, `s*(τ_0)` — the obvious guess — drifts 77%).

The user proposed the workflow: solve LOG with defaults, measure, add margin, update the constants
offline. Measurement confirmed it works — `min_τ ι*(τ)` is constant to 0.045% across `ρ` and under LOG, so
one cheap LOG calibration sets constants for a whole sweep. The one thing argued *against* was closing the
loop automatically: a grid learned from the previous run makes the outer residual depend on solve history,
which is the same defect as the knot flips wearing different clothes. `initGS`' own docstring had already
made that call for a related reason. So: `reachableBox`/`gridOccupancy` measure and `calibratePoint`
records `occupancy*`, but nothing acts.

**A tension resolved by evidence rather than by argument.** The retune drops feasible `τ`-nodes from 81% to
66% — past the 29/101 that deviations item 4 names as the symptom which made the doc's 0.75 pad unusable.
The harm did not follow: corner selections *fell* (988 → 45 at `ρ=2.0`), and the LOG calibration converged
in 25 evaluations against 26 to within 0.05% in `β`. The loss comes from the *upper* bound, not the lower
one, which is still below the level that caused the documented failure.

**Verified.** All five module suites pass (36/52/35/41/36). Three checks needed updating: two asserted the
old grid rule; the third, `test_peePath`'s spurious-root trap, **flipped direction** — on the wider grid
`τPolicy(u)` extrapolated above `u` and made `residual(u)` exactly 0, on the narrower one it extrapolates
to −1456 and clips to `l`. The test's own comment had already said which way it falls is luck, so it now
asserts the defect (the policy is evaluated far outside its grid, so the clipped residual is degenerate
either way) rather than the coin toss. End-to-end: `ρ ∈ {1.0, 0.9, 0.8, 0.7}` all solve, `dlnβ/dρ` matching
the original series to three digits.

**Next.** Re-run the full `ρ ∈ [0.5, 2.0]` sweep with `--smoothKnots 4` and the retuned rule — it
supersedes the current CSV, which the README now flags as predating both changes. Then `eps=1e-3` for the
CRRA outer step (hygiene, not a fix — it corrupts the Jacobian but cannot create a removed root), and
re-measuring whether `45×45` is still needed now that the residual is continuous and the grids are placed.

## 2026-08-19 (cont'd) — the settings adopted against the knot flips, re-derived; and the universalisation shock

Follow-on from the entry above. Having found that the outer residual's discontinuities were a smoother
artefact, the question was what else had been built on top of that defect. Two settings had: the CRRA
outer finite-difference step (`_calOuterKwargs`, deviations item 13) and the CRRA inner grid `nι=ns=45`
(item 12). Both were re-derived rather than inherited (`measureOuterSettings.py`). **They did not fall the
same way**, which is the entry's point — the numbers are in deviations item 17.

**The step is gone.** Item 13's whole content was one Jacobian column (`η0`) reading 5.13 against a
resolved 0.99 at scipy's default step. Re-measured at the converged `ρ=0.7`/`ρ=0.9` points, every column
is flat to 0.01% from `1.5e-8` through `1e-4`; calibrating from a common start, all three candidate steps
take the same number of evaluations to the same parameters, and the **default reaches the tightest final
residual**. So `eps=1e-3` — which the `rho07_resolved` note recommended adopting "on its own merits" — is
marginally worse, and the override is removed rather than retuned. `_calOuterKwargs` is kept as an empty
dict: the per-solver hook is the right place for the next such finding, and an empty one records that the
LOG/CRRA split was retracted on evidence rather than never considered.

**The grid stays, on a much weaker argument.** Item 12's `30×30` was *displaced* — `β` off ~1%, ladder
plateauing at 3.1e-3. That does not reproduce: `n ∈ {30,45,60}` now agree to 1.5–3.8e-4, which is less
than either of that day's two solver changes moved the LOG anchor. What survives is that `30×30`'s
refinement rungs run 2–3× above `45×45`'s at `ρ=0.7` and are indistinguishable at `ρ=0.9`; since the sweep
runs to `ρ=0.5`, further into that region, `45×45` is kept — at 4× the cost, and as the first thing to
revisit if the budget binds. Incidentally settled: `n=60` buys nothing over 45, so **~1e-4 in the
parameters is the floor of what the outer answer is determined to**, which is the scale `calibrate`'s
`tol` should be read against. LOG independently shows the same floor (5.7e-4 refined at `nι=75`).

*Process note.* The `--test grid` ladder's first version printed a shape classifier that fired on every
row, because the ladder starts at the calibration's own grid where the residual is ~1e-12 by construction.
A diagnostic whose verdict is constant across all inputs is worse than none — it invites reading the label
instead of the numbers. Fixed to summarise only the rungs off the calibration's own grid.

**`smoothKnots` now applies to LOG too.** The sweep keyed it on `'CRRA'` only, so the `ρ=1` anchor — whose
`x` seeds the entire march — was the one point solved under a different residual from all the others.
Pinning its knots costs nothing (26 nfev against 25), tightens the residual 33× (1.5e-11 against 5.2e-10)
and moves the answer to **`β=1.210923, ω=2.645212, η0=0.325559, X0=0.408241`**, i.e. −0.057%/+0.32%. That
is the largest of the three solver-side moves this answer has made, and `test_calibrationGrid.py` pins the
new pair with all three references kept in its comment. Consequence for results: the `_retuned` partial
CSV is superseded rather than merely incomplete, since its anchor predates this.

**The universalisation shock** (`shockUniversal.py`, docs `num_shock.tex`). Unanticipated reform at `t0`:
baseline solve → `stateAtT0` → `createCopyFromt0` → new `ε` → re-solve from that state, with the seed state
the only channel from the pre- to the post-reform world. Two readings, both parameter-only since `b̄_t` and
`h_{t-1}` cancel between `b^0` and `b^i`: `b^0=b^j` and `ε=1-θ`. They turned out to *bracket* the status
quo rather than differing in degree (0.546 and 0.161 against 0.337), so every response reverses sign — a
better outcome than two variants of the same direction, and worth keeping both.

Two implementation points that were not obvious from the model code. `ε` must be written into **db**, not
merely passed to `solvePEE_*`: `κ_t(ε_{t+1})` is consumed everywhere through a cached `db['κ']`, and a
mutually inconsistent `(ε,κ)` pair violates no equilibrium condition, so the error would have been silent
and plausible. And `db['κ[t-1]']` at the copy's first period has to be rebuilt from the *new* `ε_{t0}` —
`_sliceDb` restricts rather than recomputes, and `b̄_{t0}` is what pays the reformed benefit to the
generation already old at `t0`. Both are currently invisible (`p`/`γ0` constant, `ε^U` flat, so the
inherited, reformed and boundary-clamped values coincide) and stop being so the moment either varies.
The README's `κ`-staleness caveat is therefore no longer latent, and now names the pattern to copy.

**Test-suite addendum (same session).** All seven suites now pass — 36/52/35/41/36 (the fast five),
36 (`test_calibration`), 37 (`test_calibrationGrid`). The two slow ones had **not** been run since before
the 2026-08-19 grid retune; the entry above this one says "all five module suites pass", and that was
literally true and easy to misread as complete coverage. `test_calibration.py` §8 was already failing when
this session started, and the natural suspect — `_calOuterKwargs` being emptied — was wrong. The measured
disambiguation at `ρ=1.02`, warm-started from LOG:

| §8's settings | max\|res\| | nfev | time |
|---|---|---|---|
| linear + adaptive, scipy's default step | 2.02e-07 | 32 | 1881 s |
| linear + adaptive, `eps=1e-4` (**the pre-change default**) | 2.21e-07 | 30 | 2028 s |
| cubic + `smoothKnots=4`, scipy's default step | **1.71e-12** | 11 | 263 s |

The middle row is the point: the configuration exactly as it stood before the change fails too, and by the
same margin. So the step was never what carried this check, which *strengthens* item 17 rather than
qualifying it — and it is `crossCuttingFindings.md` #5 restated, since neither step reaches a root the
discretization removed (~30 evaluations of cycling either way). §8 now runs at the settings the CRRA
calibration is documented to need, and carries the table so it is not re-derived.

Two smaller things found while fixing it. `initGS()` with **no argument** resets `interpKind` and
`smoothKnots`, not just the grid sizes, so §8's "coarsen back to the default" comparison had been varying
three things at once; held properly fixed, `30×30` is 1.2× `60×60` at `ρ=1.02` rather than the 2.8× that
confound produced — most of that gap was the smoother. And item 12's `>10×` assertion has been replaced by
a direction check with the ratio reported, plus the condition under which `45×45` should simply be dropped.

*The lesson to carry, which is #6's in miniature:* a suite that is too slow to run every session will be
left behind by a change made in a session that did not run it, and the failure then surfaces later
attached to the wrong cause. The fast/slow split is real, but "all suites pass" needs to name which.

**`smoothKnots` default flipped `None` → `4`** (end of session, at the user's call). The argument for
`None` was bitwise reproducibility of pre-retune results; those are all superseded, every calibration path
was already overriding it, and the configuration that still reached the adaptive branch by default was the
one that silently failed for a session. All seven suites pass under the new default — 36/52/35/41/36/36/37
— and the fast five are unchanged by it, since they assert against grid spacing and primitive rebuilds
rather than stored numbers.

*The part worth remembering is the flip's collateral*, not the flip. `initGS` merges the caller's dict
**over** the class defaults, so `smoothKnots=None` stopped meaning "no opinion" and started meaning
"disable pinning". Two callers threaded an optional argument through and were inverted in **opposite**
directions: `calibrateRhoGrid.py` passed its `None` default straight in, so an unflagged sweep would have
selected the adaptive smoother — silently, and in the one script where it matters most; `diagnoseRho07.py`
omitted the key instead, so it would have inherited `4` and quietly changed the baseline of the
adaptive-vs-fixed comparison its test 4 exists to make. Both are now explicit. General form: flipping a
default is not a local edit when callers pass the old default value as their own "unset" sentinel, and the
two failure directions look nothing alike from the call site.

## 2026-08-19 (cont'd) — the `ρ` sweep re-run at the retuned settings; the shock across the full grid

Two of the README's open items closed this session: the `ρ ∈ [0.5, 2.0]` sweep re-run at the settings the
day's earlier entries settled on, then the universalisation shock extended from the single `ρ=1` anchor to
every point of it.

**The sweep: clean on the first try.** `calibrateRhoGrid.py --force` (defaults already matched the settled
settings — `smoothKnots=4`, `interpKind='cubic'`, `nι=ns=45`, scipy's own outer step), all 16 points, first
attempt, **no step-halving anywhere** — including `ρ=0.7`, which cost six failed attempts across four
strategies in the original 2026-08-12 sweep. Total wall time ≈75 min against the ≈6h the module docstring
had budgeted for a sweep still fighting the discontinuity; the budget was written before the fix and is now
stale by roughly the size of the fix itself. `residual` ≤ 3.1e-11 throughout, `verifyResidual` ≤ 1.5e-4,
`nRoots=1` at every point — the cleanest run this sweep has had.

**A schema/row-builder mismatch, caught by reading the output rather than by a test.** The first run's CSV
had `occupancyι`/`occupancys` blank at every point, despite `COLUMNS` declaring them and the README stating
`calibratePoint` "records `occupancy*` on every point." Reproduced directly against a pickled instance
(`rho_1.1000.pkl`) with the underlying computation left untouched: `_calOccupancy` returns real numbers
(71%/80% at `ρ=1.1`, consistent with the retune's documented 78–80%). The break was one level up —
`calibrateRhoGrid.py`'s `toRow` builds the CSV row by picking a fixed tuple of keys off `calibratePoint`'s
record, and that tuple never included the two occupancy keys, so they were computed, discarded, and written
as blank on every point since the columns were added. Fixed (`toRow` now includes them) and the sweep
re-run to backfill — parameters and residuals are bitwise unrelated to the fix (same warm-started resolve),
only the two new columns differ from the first run.

*Worth naming as its own trap, distinct from the smoother/grid findings above*: a column present in
`COLUMNS` is not evidence it is populated. The two places that would have caught it faster — a test
asserting `verifyResidual`/`occupancy*` are non-null for a fresh sweep row, or printing the occupancy
numbers in the script's own per-point progress line the way `β`/`ω`/`η0`/`X0` already are — neither exists
yet. Not fixed this session; worth doing before the next sweep if occupancy is meant to be read routinely
rather than recovered by hand when someone asks.

**A second latent trap, same shape, caught while wiring up the shock experiment next.** `shockUniversal.py`
still defaulted `--csv` to `informalSavings_rhoGrid_fixedKnots_retuned.csv` — correct when that file was
the newest series, silently wrong now that a fresher one supersedes it. A bare invocation would have walked
every `ρ` in a superseded CSV against pickled instances the fresh sweep had *already overwritten* in place
(same filenames, `rho_{ρ:.4f}.pkl`), so the failure mode was not "wrong file, obvious," but a CSV whose own
recorded parameters no longer matched the instances it was pointing readers at — the same silent
mismatch shape as `κ`-staleness under a varying `ε` (README, "Known limitations"), one layer up. Caught
before running by reading the module docstring's own note that a re-run under changed settings needs a new
`--out` or `--force`, and asking the same question of every other script with a CSV default. Fixed by
pointing the default at the canonical `informalSavings_rhoGrid.csv`; run this session with `--csv` passed
explicitly regardless, since the default fix had not landed yet when the run started.

**The shock, across all 16 points.** `match` (`b^0=b^1`) run at every `ρ`, LOG at the anchor and CRRA
elsewhere, loading the fresh sweep's pickled instances. The reform identity `b^0/b^{refType} = target`
holds to ≤3.3e-16 at every point — the strongest form of the check the docstring describes, since it now
confirms `installEps`'s `db['κ']`/`db['κ[t-1]']` rewrite stays internally consistent across a `ρ` range
sixteen times wider than what it had been exercised on. Full numbers in the README's "Results" section.

**One genuine finding: two of the four response series are not monotone in `ρ`.** `Δι` and the two
consumption responses (`Δc^{1,0}`, `Δc^{2,0}`) move monotonically across the whole grid, matching the
intuition that a bigger income effect at low `ρ` (curvature) would predict. `Δτ` and `Δs` do not — both
rise from `ρ=0.5`, turn over around `ρ≈1.3` (`Δτ` peaking at 7.75%), and fall back toward `ρ=2.0` (6.62%).
The `ρ=1`-only result from earlier today could not have shown this: `ρ=1` sits close to the peak rather
than on either monotone limb, so a single point reads as "large and roughly typical" when it is neither.
Not investigated mechanically this session — the political mechanism (`τ`'s own FOC weighs the now-larger
`c^{2,0}` gain against the formal types' loss, with weights that themselves shift with `ρ`) is the natural
place to look, but the hump is reported as a fact of the solved path here, not yet explained.

**Not done.** `flat` across the full grid (only the `ρ=1` anchor exists for it — see README Open); the
`χ^R` sensitivity sweep; the occupancy-visibility gap named above.

## 2026-08-19 (cont'd) — plotting the shock response against `ρ`; a candidate solver-boundary artifact

Added `plotUniversalShock.py` (new file this session; `matplotlib` installed into `.venv`, logged in
`pyenv.md`) to plot one response series from `shockUniversal.py`'s per-`ρ` CSVs against `ρ`. First built
for the impact period (`Δτ`, `--period 0` default), matching the hump already written up above:
`results/shocks/delta_tau_vs_rho_match_t0.png`, rising from `ρ=0.5` to a peak near `ρ≈1.3` (7.75%) and
falling back to 6.62% by `ρ=2.0`.

**Generalised to `--period`, a positional row offset from `t0`**, since each shock CSV is already indexed
on the model's own `t` starting at `t0` (`shockUniversal.py`'s `b.join(r, ...)`), and asked to plot `t0+1`
next. Output naming picked up the period (`..._t0.png`/`..._t1.png`); the original impact-only filename
without a period suffix was deleted rather than kept alongside, so only the new convention exists on disk.

**The `t0+1` plot surfaced something the impact-period one does not show.** Same hump shape overall (peak
≈6.0% near `ρ≈1.4-1.5`), but with a small dip exactly at `ρ=1.0→1.1` (6.09% → 5.72%) that both flanking
segments — `ρ≤1.0` and `ρ≥1.1` — do not have; each side on its own is smooth. `ρ=1.0` is the module's one
LOG point, `ρ≥1.1` all CRRA, so the dip sits precisely on the solver boundary the sweep itself changes
methods at. Read as a candidate solver-transition artifact, not an economic kink, on the strength of that
coincidence alone — but not checked against a refined CRRA grid at `ρ=1.1`, which is the standard diagnostic
this repo already has for "is a kink real or grid-limited" (`notes/crossCuttingFindings.md` #3/#5). Recorded
in the README's Open list rather than chased further this session.

## 2026-08-19 (cont'd) — the `ρ=1` boundary: not the solvers, the interpolant the LOG anchor was left on

The `Δτ` dip at `ρ=1.0→1.1` in the `t0+1` shock response (README Open, previous entry) is diagnosed. It is
**not** a LOG-vs-CRRA solver-transition artifact, and the diagnostic the README proposed — refining the
CRRA grid at `ρ=1.1` — would have found nothing: measured, that moves `Δτ` by ~6e-5, about 100× less than
the displacement it was meant to explain.

Full chain, all numbers, and the recommended one-line fix: `notes/informalSavings_resolvedIssues.md`.
Transferable form: `notes/crossCuttingFindings.md` #7. Headlines:

**The two recursions agree; the settings do not.** Crossing `ρ=1` changes four things at once, because
`calibrateRhoGrid.py` keys grid settings by solver and hands LOG only `smoothKnots`: the recursion, `nι`
(50→45), and `interpKind` (`'linear'`→`'cubic'`). Holding the last two fixed, the CRRA limit as `ρ→1`
differs from LOG by 1.6e-5 in `τ(t0)` — **0.0016 τ-grid cells**. Leaving them at production values it is
6.3e-4, 40× larger; `nι` accounts for ~2% of that and `interpKind` for the rest.

**The LOG answer on linear interpolants does not converge — it jitters.** `τ(t0)` across
`nι ∈ [45,120]` spans 9.6e-4 with no trend, against 2.2e-5 under cubic; `τ(t0+1)` 2.4e-3 against 2.5e-5,
a factor 95. The `0.12500000` at `nι=50` is not convergence — `τ(t0)=0.125` is a *calibration target*, so
the parameters were fitted to one realisation of the jitter, at one setting.

**Which is why the discontinuity is in the calibration, not only the path.** On a fine grid
`ρ ∈ {0.98,...,1.02}` (new: `informalSavings_rhoFine.csv`), second differences read `[+d, −2d, +d]`
exactly for `η0` (`d=9.3e-6`) and `X0` (`d=1.02e-4`) — the signature of a single displaced point. The
published coarse sweep reproduces both independently (+9.9e-6, +1.08e-4), two measurements ten-fold apart
in spacing agreeing to 6%. `τ` and `sr` are pinned at ~1e-13 because they are targets, which is exactly
why `t0` looked cleaner than `t0+1`.

**Recalibrating the anchor on cubic removes it.** `β`/`η0`/`X0` land on the CRRA-neighbours' prediction to
5–6 significant figures; the shock's `d_τ(t0+1)` displacement falls from **+10.6% of scale to −0.002%**
(4700×) and the series becomes monotone through `ρ=1`. The CRRA rows are unaffected — identical `β`/`ω` at
`ρ=1.01`/`1.02` under both modes, since a warm start does not move a root — so the blast radius is the
anchor row of each sweep and `universal_*_rho1.0000.csv`.

**The fix is NOT the class default.** `CRRA._gridSettings` inherits `interpKind` from `LOG` (its override
dict does not carry the key), so flipping LOG's default flips CRRA's too. Tried and reverted: it fails
`test_peeCRRA` (cubic's overshoot at a bound, which `policy.py`'s own docstring predicts, pushes
`eq:stateResidual:iota` from <1e-6 to 1.75e-6 at the coarse 30×30 default) and `test_peePath` (with cubic,
interpolating a transition is no longer worse than re-solving it — so structural result 10's *test* stops
holding, which is itself worth knowing: that penalty is largely a linear-interpolant artifact). The
surgical fix is one line in `calibrateRhoGrid.py` — give LOG `interpKind` as CRRA already gets it, keeping
`nι=50`. Measured, that cuts the anchor displacement ~90× on every parameter at no cost (25 nfev vs 26).

**And the check that would have caught it was keyed the same way.** `verify` is `{'CRRA': ...}`, so every
LOG row of every sweep has `verifyResidual = NaN`. The one point on the unconverged interpolant is the one
point with no refinement check.

**New files.** `diagnoseLogCrraBoundary.py` (six selectable tests, `--mode common|production` to separate
method from settings), `plotBoundary.py`. `calibrateRhoGrid.py` gained `--pkldir` and `--common`;
`shockUniversal.py` gained `--pkldir` and `--commonSettings`. All additive — the fast five suites pass
unchanged (36/52/35/41/36).

**A measurement note worth carrying.** The raw gap `x_CRRA(1±δ) − x_LOG(1)` is linear in `δ` and
antisymmetric, because it is dominated by the true slope `dτ/dρ`; reading it as a solver artifact was the
easy mistake and it is what the first ladder looked like. The statistic that answers the question is the
central average `½[x(1+δ)+x(1−δ)] − x_LOG(1)`, which cancels the trend and leaves `½x''δ² + C`: it decays
like `δ²` (ratios ≈4) then plateaus at `C`, and `C` is the jump.

**Not done** *(as of this entry — the fix was applied the next day; see the 2026-08-20 entry below).* The
fix is not applied — it moves the published `ρ=1` calibration
(`β=1.210923, ω=2.645212` → `β=1.211968, ω=2.641368`) and `test_calibrationGrid.py` pins the old pair.
Also open: one cubic outlier at `nι=160` (`τ(t0)=0.126053` against a series flat at 0.12562), the only
datum inconsistent with "cubic is converged"; and whether `'pchip'` should replace `'cubic'` for both
solvers, since it is the monotone `C¹` option that would not have tripped `test_peeCRRA` and was rejected
on speed rather than accuracy.

## 2026-08-20 — the boundary fix applied; a one-row patch instead of a sweep; a backup that became a datapoint

Follow-on from the previous entry, at the user's call to keep the fix. Diagnosis and all measurements are
in `notes/informalSavings_resolvedIssues.md`; this entry is what changed and what it cost.

**The fix, at the call site rather than the class default.** `calibrateRhoGrid.py` now passes `interpKind`
to **both** solvers (`logGS = {'smoothKnots': knots, 'interpKind': args.interpKind}`); the grid sizes stay
per-solver, since `nι` genuinely is a resolution choice and LOG's answer is already converged in it at
`'cubic'`. `verify` is keyed on `'LOG'` too (`--verifyLOG`, default 75). `shockUniversal.py` re-solves LOG
on the `interpKind`/`smoothKnots` it was *calibrated* at — without that, the shock would re-solve a
calibrated instance under a different interpolant than it was fitted under, the same defect one layer down.

`policy.LOG._gridSettings`' class default was deliberately **not** touched: `CRRA._gridSettings` inherits
the key, so flipping it moves both solvers' defaults and trips `test_peeCRRA` (cubic's overshoot at a
bound) and `test_peePath` (whose "re-solving beats interpolating" assertion stops holding once the
interpolant is `C¹`). A defect introduced by keying is repaired by un-keying it where it was keyed.

**New anchor: `β=1.211968, ω=2.641368, η0=0.325550, X0=0.408138`**, `verifyResidual = 5.7e-6` where every
LOG row of every prior sweep carried `NaN`. The residual is *looser* than before (1.0e-9 against 1.5e-11)
and that is not a regression — the old tight residual was the solver converging precisely onto a jittering
answer. This is the only entry in the anchor's history with an independent check: the fine grid's four
CRRA points predict `β=1.211956, ω=2.641327` by extrapolation onto their own gap, and this lands on it to
1.2e-5 where the previous anchor missed by 1.03e-3.

**Result.** `d_τ(t0+1)` at `ρ = 0.9, 1.0, 1.1` goes `5.157% → 6.089% → 5.722%` to
`5.157% → 5.488% → 5.722%` — monotone, kink gone. Anchor deviation from a fit through its neighbours:
`+0.567 pp → −0.034 pp`. Impact period `7.512% → 7.223%`.

**A full re-sweep was started and abandoned, correctly.** The user asked why the whole grid needed
re-running when the fix only changed what is passed to the LOG solver. It did not.
`_calPreferences` selects LOG at `ρ==1` exactly, so the fix changes the residual function at **one** point
of the grid; the other 15 keep their own residual, and a warm start moves the path to a root, not the
root. That was already verified at 8 CRRA points (4 on the fine grid under both configurations, 4 in the
abandoned sweep — `ρ=1.1` returned `β=1.080742, ω=2.417306`, the published values to 6 significant
figures). The patch was then done through the script's **own resume path** — drop the `ρ=1` row, re-run
without `--force`, cached rows return from the CSV untouched — in **30 s against ~2.5 h**. Exactly one row
of `informalSavings_rhoGrid.csv` differs from the pre-fix series, confirmed column by column. Same
reasoning for the shock: only `--rho 1.0` was re-run, since no other instance changed.

*The general point*: before re-running an expensive pipeline after a change, ask which of its outputs the
change can actually reach. Here the blast radius was one row out of sixteen and the machinery to exploit
that already existed, unused.

**A backup that became a datapoint.** The user noticed the regenerated `t0+1` figure appeared to have two
gridpoints at `ρ=1`. It did. `universal_match_rho1.0000_preInterpFix.csv` — the backup taken minutes
earlier — matched `plotUniversalShock.py`'s `universal_<rule>_rho*.csv` glob, and since `loadAtPeriod`
reads `ρ` from the file's **own column** rather than the filename, the pre-fix anchor came through as a
well-formed extra point and was plotted beside the post-fix one. The numbers quoted in text were right
(that analysis filtered `preInterpFix` explicitly); the figure was wrong. Fixed both ways: superseded runs
moved to `results/shocks/preInterpFix/`, and the loader now requires an exact filename match, reports what
it skips, and **raises on a duplicate `ρ`** naming both files. Third instance of this shape in this module
(after the stale `--csv` default and the unpopulated `occupancy*` columns) — now written once as
`notes/crossCuttingFindings.md` #8 and referenced from the README rather than restated.

**Test status, stated precisely.** The fast five pass against the fixed code (`test_ee`, `test_peeLOG`,
`test_peeCRRA`, `test_peePath`, `test_createCopyFromt0`). `test_calibrationGrid.py` has its `GRIDS['LOG']`
and pinned anchor updated but **was not run** — started, then stopped at the user's request. Its pin is
therefore backed by two direct calibrations and the CRRA extrapolation, not by the suite. Run it before
treating it as verified; that is recorded in the README's Known limitations too.

**Files.** `results/calibration/informalSavings_rhoGrid_preInterpFix.csv` + `instances_preInterpFix/` and
`results/shocks/preInterpFix/` hold the superseded series. `results/boundary/` holds the diagnostic output
and the before/after figure.

## 2026-08-21 — two experiments the paper needed, and a proxy state the control run found

Run as part of building `python/paper/` (root log). Both experiments were built by parallel agents
against a fixed output contract; the contract, not the code, was what had to be got right first.

**`shockEEOnly.py` — the economic-equilibrium-only reform.** The paper's reform table decomposes into
three rows and only two existed: baseline, and the full effect with taxes re-optimised. The middle row
holds `τ` at the baseline path and moves `ε` alone, which is what separates the pure equilibrium response
from the policy response. It is **not** a second shock experiment — with taxes exogenous there is no
backward recursion at all, just one `EE_*_solve` per `ρ`, so all 16 points cost under a minute against
~2.5 h for `shockUniversal.py`. The baseline `τ` path is read off `shockUniversal.py`'s own csv rather
than re-solved; that shortcut is **bitwise** exact, but only under
`pd.read_csv(..., float_precision='round_trip')` — the default C parser is ~1 ulp off, which is enough to
make a bitwise check fail and look like a real disagreement.

The decomposition at `ρ=1`: savings rate `18.400% → 18.532%` (economic equilibrium) `→ 18.222%` (full
effect). **The pure equilibrium effect is positive and the full effect negative**, at every `ρ` on the
grid; labour supply moves the same way in both, with the equilibrium part about a third of the total.

**A proxy state that the no-shock control found, and that is live in the existing results.** `EE_report`
backs its first period's lagged objects out of `initialState_solve` rather than taking them as arguments.
On the full model that is right. On a **copy** from `createCopyFromt0` it is not: the true
`ι_{t0-1}`/`h_{t0-1}` entering `t0` are the baseline's, and `stateAtT0` already knows them. Since every
shock experiment compares a full-model baseline against a copy, the proxy enters the *difference*:
`c20` at `t0` is off by **+5.3–5.7% of level** under both solvers, and `bbar` by +0.01–0.13% under CRRA
only (under LOG the proxy `Γ_{s,t-1}` is exact, so it is 1e-17 there). `b0`/`bi` are clean — `h_{t-1}`
cancels against `bbar`. Everything from `t0+1` on, and `τ`/`s`/`h`/`ι` throughout, is clean.
**So the README's `Δc^{2,0} = +11.31%` headline is roughly half artifact**, while the paper's three tables
and both figures — which read only `τ`, `s`, `h`, `ι` — are unaffected. Recorded in Known limitations with
the fix (let `EE_report` take the lagged state; a `model.py` change plus a ~2.5 h re-run), not applied.

*Worth carrying:* **the control run was a precondition, not a test, and it is what found this.** It is
cheap (one extra `EE_*_solve`, and it doubles as the CRRA warm start) and it asks the one question no
residual can: does the machinery reproduce the baseline when the shock is removed? A defect of this shape
— a mutually consistent but wrong lagged state — violates no equilibrium condition and so is invisible to
every convergence check in the repo. Same family as the `κ` staleness already in Known limitations: an
object that enters as *given* cannot be caught by checking the equations it enters.

**`sweepEpsTheta.py` — comparative statics in the two system characteristics.** *(Superseded 2026-08-21:
the file and its csv were deleted and replaced by `sweepEpsThetaGrid.py` — see that entry. What survives
here is the `installEps`/`κ` reasoning below, which the grid script inherited unchanged.)* Behind the
paper's four-panel figure. Deliberately **not** a recalibration: `β`/`ω`/`η0`/`X0` stay pinned and one
characteristic moves at a time, so the status-quo row reproduces the calibrated point (`τ` to 5.6e-11,
savings rate to 1.9e-11) and both sweeps pass through it. 33 points at ~1.1 s each.

Two decisions the file records. `ε` is installed only through `shockUniversal.installEps` — the `κ`
staleness makes any other route silently wrong. And **`--epsTracksTheta` defaults off**: `model.getEps`
makes `ε` a decreasing function of `θ`, so letting `ε` track would superimpose a reversed `ε` sweep onto
the `θ` panel and destroy the independence the two panels are read with. Both `eps` and `theta` are
recorded on every row so the two readings can never be confused after the fact.

**The `ε=ε^U` sweep row is not the universalisation shock, and should not be expected to match**: at
`ρ=1`, `τ` is +9.88% against the shock's +7.22%. The sweep re-solves the whole horizon under the new `ε`,
so the state entering `t0` has itself adjusted (`s_` −3.2%); the shock is unanticipated and seeds from the
pre-reform state. `c20` shows the largest gap (−6.1%) because the generation already old at `t0` is
exactly the one whose savings the shock leaves at their pre-reform level.

**One documented claim the sweep contradicts.** `writing/Paper/Sections/Quant.tex` says the effects are
nonlinear in `ε` "in all cases, with the marginal effect decreasing with `ε`". That holds for `τ`, the
savings rate and `h`. It does **not** hold for `ι`, whose marginal effect grows monotonically in
magnitude across the whole grid (−0.053 → −0.085). The level signs all agree. Reported to the user rather
than tuned; the fix is a word in the paper (the three flow variables, not "all cases"), not in the code.

**Neither script has a test file.** They are experiment scripts in the same class as `shockUniversal.py`
and `calibrateRhoGrid.py`, and like those they are covered indirectly — the status-quo/no-shock rows are
self-checks that fail loudly. `runTests.py`'s registry is unchanged at 17 suites.

## 2026-08-21 — `sweepEpsThetaGrid.py`, and the cross sweep retired

`sweepEpsTheta.py` swept `ε` and `θ` **one at a time** through the calibrated `ρ=1` instance — a cross
through the calibrated point. The paper figure it fed wanted the whole surface, so it was replaced by
`sweepEpsThetaGrid.py`, a cartesian product grid. 27 `ε` × 14 `θ` = 378 points, 4m52s, `nRoots == 1`
everywhere, status-quo row reproducing the calibration to 5.6e-11 in `τ` and 1.9e-11 in the savings rate.
Figure-side work is in `python/paper/RESEARCH_LOG.md`.

**`ε` must not track `θ` here, and the reason is different from the old script's.** `sweepEpsTheta.py`
offered `--epsTracksTheta` and defaulted it off because letting `model.getEps` follow `θ` would have
superimposed a reversed `ε` sweep on the `θ` *panel*, destroying the independence the two panels were
read with — a presentation argument. On a product grid the argument is structural: following the chain
would make `ε` a function of `θ`, collapsing the grid onto a curve, and there would be no `θ`-family of
`ε`-curves for the figure to exist at all. So the flag is not offered rather than defaulted off. Same
conclusion, and it is worth keeping the two reasons distinct — the presentation one could be argued with;
this one cannot.

**Installation order is safe in both directions, and the script asserts it anyway.** `installTheta`
touches only `db['θ']` (plus lead/lag via `adjPar`); `installEps` rewrites `db['eps']` and the cached
`db['kappa']`, and `aux_κ` reads `db['eps[t+1]']` and nothing else. So neither can clobber the other.
`solvePoint` still asserts the `(ε, θ)` sitting in `db` is the pair asked for, because the failure mode
this guards is silent: a mutually inconsistent `(ε, κ)` violates no equilibrium condition, so a wrong
install produces a plausible number rather than an exception.

**Cost of a product grid was the thing worth measuring first.** At ~1.1 s per point a full grid is
minutes, not hours — cheap enough that the cross sweep's whole reason for existing (avoiding the product)
had lapsed. That was not obvious before checking the `time` column of the existing csv; the assumption
that "a 2-D sweep is expensive" is what had kept the figure a cross.

**`sweepEpsTheta.py` and `results/sweeps/epsTheta_rho1.0000.csv` deleted.** Before deleting, the grid was
checked against the cross sweep along both calibrated lines: max abs difference **8.3e-17** over
`τ, sr, h, ι, s, s_, c10, c20` at shared `ε`, **9.7e-17** at shared `θ`. That is 1-ulp agreement between
two independently written installation paths — the real content of the check, recorded here because the
file it ran against is gone. The three helpers the grid script had imported from it (`installTheta`,
`atT0`, `buildGrid`) were inlined first; `installTheta` lost its now-meaningless `tracksEps` argument in
the move. Both deleted files were untracked, so this is not recoverable from git.

## 2026-08-24 — why the calibrated β exceeds 1, and the ranked fixes (analysis only)

The ρ sweep's β is above 1 for every ρ below ~1.15 (1.21 at ρ = 1, 4.28 at ρ = 0.5). Diagnosis and a
ranked list of fixes are in `notes/argentina_calibrationTarget.md`; the short version: the 18.4% savings
datum is targeted as s/Y while the labor share is only 1−α = 0.57, so the young must save 32% of gross
labor income — half again what the US arm delivers with β = 0.76 — and β is the only free parameter
left to do it. The past calibration that targeted savings/labor-income imposed roughly half the saving
(s/Y ≈ 0.105) and that is the whole reason it produced β < 1. Recommended: re-target as s/(wh) behind
a flag (consistent with the s/(wh) convention `shocks.srPaper` already uses for the paper's tables),
then audit what the 18.4% actually measures — the model's s is the young cohort's net retirement
saving, not national-accounts gross saving. No recalibration was run.

## 2026-08-24 (cont.) — the audit ran, and it corrects the entry above

`notes/argentina_calibrationTarget.md` carried out the previous entry's "then audit the datum" step,
and the outcome supersedes that entry's recommendation. What changed: the 18.4% is a World Bank gross
national-accounts saving rate (nearest current-vintage series 17.0–17.7%; the exact number is
unrecoverable post-rebasing, and the workbook records no series id); the household-vs-national sector
argument does NOT apply, because households own the whole capital stock here; and the re-denomination
fix (target s/(wh)) is retired — the τ target was already converted into the model's denominator, so
the denominators were consistent all along, and the s/(wh) reading implies a capital–output ratio below
anything measured. The real defect is the TIME dimension: with 30-year periods and full depreciation
the model's moment is `s_t/Y_t = K_{t+1}/Y_t`, a stock over 30 years of output, while the datum is an
annual flow — a different and larger object. Revised recommendation: set the target so the implied
capital–output ratio matches PWT (`s0 ≈ 0.15`), giving β = 0.81–0.97 at ρ = 1 with no new datum needed;
β crosses 1 at K/Y ≈ 3.68, which is the US arm's own implied ratio.


## 2026-08-24 (cont.) — the target moved, and everything downstream was re-run

The previous entry's recommendation was implemented, with one change of reading. `db['KY0']` replaces
`db['s0']` as the moment that identifies β, through a new `Base.capitalOutputRatio` (`eq:calibration:KY`)
in both Argentina variants, and `yearsPerPeriod = 30` is now a model parameter rather than a convention
living only in the documentation — that convention being exactly what the error turned on. The residual
is formed once, in `_calResidual`, with K/Y relative and τ level (K/Y is O(3.2) against τ's O(0.125), so
a level gap there would swamp the tax target); the savings rate is still computed and reported, because
the paper's tables quote it.

**The datum is the calibration year, not a window mean.** The audit measured against 1994-2007 (3.5752);
the value adopted is 2010 alone, **3.2313**, on the grounds that every other target in eq:calibration —
the tax rate, the replacement-rate ratio, the coverage share, the household survey — is measured at or
around 2010, and Argentina's K/Y moves too much over the preceding decades (4.28 in 1990, 3.17 in 2007,
mostly through the denominator) for an average to describe the same economy. It also matters for the
question that opened all this: β crosses 1 at K/Y ≈ 3.64, so the 30-year mean (3.6606) would have left
β at 1.0126 while 2010 gives 0.8076. `python/paper/dataTargets.py` derives both readings from PWT 11.0
every run and names only one of them `capitalOutputRatio`; `--target` chooses which.

**Full re-run, ~4 h of machine time**, all 16 ρ: sweep, universalisation (both readings), the
economic-equilibrium-only decomposition, the (ε,θ) grid, the paper rebuild, and `runTests.py --all`.
Results in this README's "Results" sections. The three findings worth keeping:

1. **β crosses 1 between ρ=0.8 and ρ=0.9**, against ρ≈1.15 before. The whole curve is ≈0.65× its old
   self at every ρ, so the retarget shrank the β>1 region rather than removing it — ρ<0.85 still
   calibrates above 1. That is a statement about the low-EIS end, not about the target.
2. **The ρ≈0.7 pocket is gone.** Under the savings-rate target ρ ∈ [0.7, 0.775] would not converge and
   needed `diagnoseRho07.py`; here ρ=0.7 solves in 12 evaluations at a 4.5e-14 residual. Not separated
   from the different β it lands on, so not claimed as a fix.
3. **verifyResidual degrades down the low-ρ tail** — 6e-6 at ρ=1, 4.9e-4 at ρ=0.6, 1.2e-3 at ρ=0.5. The
   bottom two rows are converged but not resolved and should be read as indicative. Open.

Two test failures came out of the re-run, both stale references rather than defects. `test_calibrationGrid`
pins the anchor's (β,ω) against the README and was updated, as its own comment prescribes. More
interesting: `informalAnalytical/test_calibration.py` failed to converge *from its shipped starting
guess* — β=0.6, tuned for the old target — walking into a region where the whole-path policy solve
returns a NaN τ and the steady-state brentq then dies at its own lower bracket. From every start in
[0.7, 1.0] it converges to the same root (β=0.84424, ω=2.19679), so the guess moved to 0.85 and the root
is not in doubt. Worth recording as a limitation of that variant: its outer search has no globalization,
so a start far from the root fails rather than converging slowly. The InformalSavings arm took the same
change from the same guess without complaint.
