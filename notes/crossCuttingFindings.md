# Cross-cutting findings

Findings that recurred across modules. Recorded once here; other files link to a number rather than
restate it. Each entry is the statement, the tell, and the habit. Long-form versions of the ones that
came with a full investigation are in `notes/archive/`.

## 1. Bitwise reproducibility holds within a process, not across processes

A fresh interpreter reproduces an unchanged solve only to ~1e-13 (464 of 611 arrays differed in
`InformalSavings`); within one process it is bitwise identical. numpy's SIMD dispatch varies with array
size and alignment.

**Habit.** An old-vs-new comparison for a refactor must run both implementations **in the same process** —
monkeypatch the pre-change functions in and compare there. A saved baseline compared across runs asserts
only ~1e-13, which is too loose to catch a subtly wrong reuse, and far too loose for a refactor that
changes array sizes. Check the reference path's call counts too, to confirm it was exercised.

## 2. A clip that manufactures a bracket also manufactures a root

Every bounded policy here is evaluated as `clip(τ(·), l, u)`. A fixed point closed through one is
bracketed on `[l,u]` for free — and has an *exact* root at whichever endpoint the extrapolated policy
overshoots, which `brentq` returns in preference to the interior one.

**Tell.** The returned root sits exactly on a bound and the state it implies is far outside the grid.
Whether it fires is luck: at `ρ=1.15` `InformalSavings.initialStatePEE` overshot `u` and trapped; at
`ρ=1` it undershot `l` and the LOG case "worked", supplying false confidence in an untested path.

**Habit.** Scan the interior grid with the out-of-grid region masked to NaN, take the lowest surviving
sign change, bracket inside that cell, and report multiplicity rather than resolving it silently. **Do
not simplify this back to a bare bracketed solve on `[l,u]`.**

## 3. "Converged" and "small residual" can both be true at the wrong answer

A nested solve (outer root over parameters, inner grid search over a state) absorbs the inner solve's
discretization error into the outer parameters. Nothing errors; `success` and a tight tolerance are both
consistent with the wrong answer.

**The diagnostic.** Hold the outer-converged parameters fixed, refine the inner grid, read the trend:

| residual under refinement | meaning |
|---|---|
| decays | the coarse grid was fine |
| plateaus | the refined problem is well resolved and its root is genuinely elsewhere — the outer answer is *wrong*, not imprecise |
| grows | not grid-converged at any resolution tried; the error is not resolution (see #4, #5) |

Measured: `InformalSavings`' CRRA calibration plateaued at `6.6e-4 → 3.13e-3 → 3.14e-3` on a 30×30 inner
grid (~1% displacement in `β`) and decayed `1e-12 → 1.0e-4 → 4.4e-5` at 45×45. Hence the CRRA
*calibration* uses a finer inner grid than the CRRA *solve* — the two defaults are deliberately not
unified.

**The same signature one level up.** Before an outer point converges, a plateau shows as *resistance to
warm-starting*: `ρ=0.775` was retried from starts 100× closer and landed on the same 3.3e-6 residual
every time. A closer start buying nothing is the same tell as a refinement that does not decay.

## 4. When refinement does not help, suspect the interpolant, not the grid

A policy stored as a **piecewise-linear** interpolant makes the outer objective continuous but only
piecewise `C¹`, with kinks at every cell boundary. Refining moves the kinks closer together without
removing them, so a Newton-type outer solver stalls at any resolution.

**The fix is the interpolation kind, not the node count.** At `ρ=1.1`, linear → cubic took the outer solve
from stalling near `3e-5` after 60+ evaluations to `1.3e-11` in 12. The located parameters differed by
0.016% in `β` — the linear answer was never badly displaced, the solver just could not descend to it.

Three cautions:
- **Comparing schemes at a fixed point is not a comparison.** Evaluating B at A's converged point measures
  how far B's root has moved. Re-solve under each scheme and compare *refinement behaviour*.
- **Monotone (PCHIP) is the principled choice and may be unaffordable.** Plain cubic can overshoot where a
  policy is flat at a bound. `RegularGridInterpolator` rebuilds pchip splines on every call (~1400× slower
  than linear), so 2-D use needs a precomputed bicubic-Hermite evaluator nobody has written.
- **On the `informalAnalytical`/`US` lineage, check #5 first.** Swept over `ρ`, `US`' calibration was
  fixed by pinning the smoother's knots, not by the interpolant kind; `cubic` failed to converge in 2 of 8
  measured cells and `pchip` failed on coarse grids.

**Judge by the trend, not the spread.** A converging sequence spans a *wider* range than a jittering band,
so ranking settings by spread-of-answers prefers the broken one. A band with no trend is the absence of
information, not a small error bar — the adaptive smoother's 0.3% band hid a coarsest grid 2.4% off.

## 5. A discrete choice inside a differentiated residual is a discontinuity

Third cause with #3/#4's presentation, and the one invisible to both refinement and a better interpolant:
somewhere inside the inner solve a **library routine chooses an integer from the data** — adaptive knot
counts, adaptive quadrature orders, an `argmax` over candidates, a root-count branch. It flips as a
parameter moves and the residual jumps by `J`; a root falling inside a jump does not exist in the
discretized problem, so `|residual|` cannot go below `J`.

Measured: `UnivariateSpline(s=…)`'s FITPACK knot count put ~3.5e-6 jumps in a residual with a 1e-6
tolerance and made one `ρ` uncalibratable across six attempts. Fixed-knot `LSQUnivariateSpline`
(`gridsearch.interp`'s `knots`) removed every jump; the point solved in 11 evaluations.

**How to tell it apart, cheaply.** Fine-scan the residual along one parameter *at a converged point* and
compare successive differences to their median: smooth curvature gives a flat ratio, this gives isolated
spikes. Two corollaries: a finite-difference step that disagrees with both a smaller and a larger one is
straddling a jump (a jump contributes `J/h`), and aggregate counters will not find it — diff the
*per-period* arrays and find where a perturbation stops propagating smoothly.

**The design rule.** Anything inside a residual that will be differentiated should be a **linear map of
its input** for fixed structure, or its structural choice pinned from outside. This is also the argument
against auto-tuning grids or bounds from a previous run: that makes the residual depend on solve history.

## 6. Settings adopted as defences against an undiagnosed defect must be re-derived, not inherited

While a defect is present, every workaround setting *is* justified by measurement. The measurements are
not wrong — the attribution is: they report the defect as a property of the thing measured. Fixing the
defect invalidates the reason for every such setting while leaving it in place, documented as if it still
applied.

Measured: `InformalSavings`' two defences against the smoother's jumps fell differently once re-derived —
the per-solver finite-difference step was removed outright, the doubled inner grid survived on an argument
an order of magnitude weaker than the one that established it. Neither outcome was predictable, which is
the reason to re-derive rather than reason about it.

**What to re-derive.** Anything whose written justification cites a *symptom* ("column X was corrupted",
"the sequence plateaued") rather than a *mechanism* ("the profile diverges like 1/(1-τ), so differentiate
in log"). Recording the measurement behind each setting, not just its value, is what makes this list
findable.

**Two traps in the re-derivation.** Measure at converged points (#5). And check that a summary statistic
can come out both ways on the data it will see — a classifier that fired on every row because the ladder
included the calibration's own grid invites reading the label instead of the numbers.

## 7. A fix keyed to where a defect was found, rather than to where it applies

A defect diagnosed in one configuration and fixed *there* — keyed to the solver, branch, or parameter
range where it surfaced — persists in every other configuration that shares it, now in a codebase that
reads as though the problem is solved. The *diagnostic* usually gets keyed the same way, so the
configuration still carrying the defect is also the one exempt from the check that would catch it.

Measured: `interpKind='cubic'` (#4) was keyed to `'CRRA'`. LOG kept `'linear'`, so `ρ=1` — the single LOG
point of every sweep — ran the interpolant the module had concluded was inadequate, jittering 2.4e-3 in
`τ(t0+1)` against 2.5e-5 under cubic. The calibration fitted four parameters to one realisation of that
jitter and the shock response inherited a +10.6%-of-scale displacement, read for a session as a
LOG-vs-CRRA "solver-transition artifact". The `verify` refinement check was keyed identically, so every
LOG row of every sweep carried `verifyResidual = NaN`.

**Why it is hard to see.** The defective configuration is internally consistent: it converges, its
residual is *tighter* than the fixed configuration's (1.6e-11 vs 1.1e-9), and it hits its targets exactly.
A tight residual at a jittered answer is the solver descending precisely onto the wrong number.

**The habit.** When keying a fix to a configuration, write down what the key is *for*. A **resolution**
choice legitimately differs per solver; a **well-posedness** choice — is this object even converged? —
cannot, and keying it is a bug. Repair at the **call site that keyed it**, not by changing the class
default: the default has other consumers, and tests written against it are evidence about the default,
not about the bug.

**A diagnostic that generalises.** To test whether a boundary between two methods is real, calibrate a
fine grid straddling it and ask whether the odd point lies on the curve the others trace. Second
differences make it unambiguous without a fit: one displaced point reads `[+d, −2d, +d]` exactly. Subtract
the trend before reading a gap — use the central average `½[x(1+δ)+x(1−δ)] − x(1)`.

**A weaker cousin: a constant that was never keyed to anything.** `US` inherited a hard-coded CRRA steady
state bracket `(1e-6, 0.75)`. The feasibility limit it stands in for, `Γ_h·α·κ/((1-α)·p·θ·τ)`, scales with
`α/(1-α)` and `κ/p` — above 0.75 everywhere at Argentina's parameters, ≈0.58 at the US's, where the solver
died on a NaN while reporting a solver problem. **When a copied module changes a structural parameter,
every hard-coded bound in it is a hypothesis that needs re-testing.** Derive the bound from the model;
retuning the number only moves the parameter value at which it reappears, and the test to write asserts
that the bound *tracks* the model quantity.

**The same constant failed again, in the opposite direction.** The fix was `min(0.75, 0.99·Γs_cap)`, but
`Γs_cap` carries `θτ` in its denominator, so at **`θ = 0` it is infinite** and the `min` reverts to the
bare constant. That configuration became reachable only when the counterfactuals started at their own
steady state. Two further lessons: **a bound derived from the model is only derived where the derivation
is finite** — check the degenerate limits — and **a change of experimental convention is a change of the
input distribution to every solver downstream**. The repair pattern: expand the bracket geometrically, and
only when the default has already failed, so it can never alter a call that worked.

## 8. A superseded file left beside the live ones is an input to anything that globs

Backups, variants and dated copies in the same directory as the data they supersede are not inert. Any
reader that discovers inputs by pattern picks them up, and the extra rows are usually *well formed*,
because the same code produced them. It is worst when the reader takes the record's **key from the file's
contents** rather than its name — then the superseded row sorts into the right place and renaming no
longer protects you.

Measured: `universal_match_rho1.0000_preInterpFix.csv` was backed up in place minutes before its live
twin was regenerated. `plotUniversalShock.py` globs `universal_<rule>_rho*.csv` and reads `ρ` from each
file's own column, so the figure showed the pre-fix anchor (6.089%) beside the post-fix one (5.488%) while
purporting to show one series — and was published before anyone noticed.

**The habit.**
- **Superseded runs go in a subdirectory**, never beside the live ones. A non-recursive glob then cannot
  reach them, whatever they are called.
- **Match the filename pattern exactly** — `rho<number>.csv`, anchored — and say out loud what was skipped.
- **A duplicate key is an error, not something to resolve.** Averaging, first-wins and last-wins all hide
  it. Raise, and name both files.
- Same defect, other clothes: a column present in a schema is not evidence it is populated, and a default
  filename correct when written is not evidence it still is. **A pipeline trusting the shape of its inputs
  instead of their provenance.**

## 9. A derived parameter silently undoes any experiment that sets it

When a model recomputes parameters from data whenever the deep parameters move (`paramsFromFuncs` here),
every one is a trap for a counterfactual that sets it directly: write the value, call the refresh, and the
refresh puts the calibrated value back. Nothing raises, and the run is internally consistent — it solved
the baseline again.

**What makes it hard to catch is that the null result is plausible.** A counterfactual returning the
baseline reads as "this characteristic does not matter", which is the kind of conclusion these experiments
exist to produce. Measured: `shocks.shockTheta` set `db['θ']` then called `updateAuxPars()` for tidiness;
both `θ = 0` and `θ = 1` returned the calibrated path to every printed digit.

The same refresh is *required* two functions away — `shockIncomeDistribution` changes `η`, and `Γ_h` and
`θ` are genuine functions of `η`, so there it moves `θ` from 0.738 to 0.495, a real part of the experiment.
The rule is not "never refresh"; the refresh's inputs decide.

**The habit.** Know which parameters are derived before writing one, and set it *after* the refresh. **A
counterfactual that returns the baseline exactly is a failed run until proven otherwise** — polar cases
are the cheap check, since `θ = 0` and `θ = 1` must not agree with each other whatever they do relative to
the baseline. Distinguish "derived from data the shock changed" from "derived from data it did not"; both
look like the same line of code.

## 10. A corner makes any sensitivity check vacuous

A test measuring how much *A* moves when *B* is perturbed proves nothing if *A* sits at a boundary: the
answer is zero for a reason unrelated to the mechanism under test.

Measured: `test_escCRRA.py` perturbed `θ_{t+1}` and re-optimised `θ_{t+2}`, reporting `+0.0000` and
passing, while the production run at the same ρ reported `−0.0092`. The test reused the *LOG-calibrated*
`p = 0.402`; at ρ = 2 that puts the choice on the `θ = 1` corner, where both perturbations return 1.0. At
ρ = 2's own calibrated `p = 0.086` it gets `−0.0092` and agrees.

**Why it is easy to miss.** The vacuous result is *more* reassuring than the real one. A test whose
failure mode is "returns an even better number than expected" will not be re-examined.

**The habit.** Assert interiority in front of any derivative check (`0.02 < x < 0.98`). Reuse of a
calibrated parameter across a regime change is the usual cause — `p` under LOG is not `p` under CRRA, a
higher EIS needs 4.7× less of it. And **when a test and a production run disagree about the same quantity,
the test is the suspect**, even when the test shows the tidier number.

## 11. Maximising over a policy that also enters a predetermined state

`base.dlnc2i_dτ`'s docstring forbids taking `dln(c_2)/dτ` numerically off a solution grid: the policy
maker treats `s_{t-1,i}/s_{t-1}` as predetermined, the ratio moves along such a grid, and a grid
derivative folds in a channel that does not belong in the FOC. That warning was written for τ and applies
verbatim to any other instrument reaching the same state.

The **leaded** choice of θ is safe — `θ_{t+1}` does not appear in the date-`t-1` savings ratio. The
**permanent** choice is not: θ enters through `θ_{t0}`, and a grid maximisation that recomputes the ratio
per candidate credits the electorate with internalising a state it takes as given. Savings made at `t0-1`
are sunk when the vote happens. The readings are not close — **θ = 0.775 pinned against 0.910 moving** at
`p = 0.4`. Second, independent tell: the ratio depends on `τ_{t0}` too, while the τ it is paired with
solves `z = 0`, which is *built* holding the ratio fixed.

The asymmetry is the danger: the same objective, maximised over a different argument, is correct in one
case and wrong in the other, so copying the leaded implementation carries the bug.

### 11b. Pinning is one decision; *what value* to pin at is a second one

The first version pinned at the **incumbent** design's ratio, on the grounds that this makes the
experiment an unanticipated reform. But the experiment is not unanticipated: households arrive at `t0`
knowing a design will be chosen, so savings made at `t0-1` were made against the design that *wins*.
Rational expectations make it a fixed point, `θ* = argmax_θ W(θ ; siRatio(θ*))`; the incumbent is the seed.

**What made this survive review.** The two readings coincide *exactly* wherever the chosen design
reproduces the incumbent one — precisely the condition the wedge calibration targets. Every calibrated
number was right and `p` unchanged; the error shows only away from the calibration (0.775 vs 0.773 at
`p = 0.4`, 0.542 vs 0.549 at `p = 0.25`).

**The habit.** Before grid-maximising over an instrument, list the predetermined states it appears in; if
non-empty, pin them and pass them in as an **argument, not a recomputation**. Then ask *separately* what
the pinned value is — pinning answers "does the electorate internalise this?", the timing answers "what
did the agents who set this state believe?". A closed-form FOC hides both questions (it holds the state
fixed automatically); moving to a grid search changes what is held constant, and that change must be
deliberate. Test the convention away from the point where it is a no-op (#10), and report all readings
once — the gaps are the measure of how much the convention matters.

## 12. A calibration target has units on both sides, and only one side is in the code

The Argentina calibration targeted a savings rate of 18.4% and returned a 30-year discount factor of
1.212. The period is 30 years with full depreciation, so `s_t/Y_t` is `K_{t+1}/Y_t` — a stock over a
period's flow. The datum was an *annual* national-accounts saving flow, a larger object, because an annual
gross flow also replaces capital depreciating *within* the window. The target asked for about half again
the capital Argentina has, and β absorbed it.

**Why it survived years of review**, each part generalisable:
- **The convention lived only in prose.** "A period is 30 years" appeared in the documentation and nowhere
  in the code, so no test could check it. It is now a parameter (`yearsPerPeriod`) the target equation
  carries explicitly.
- **The neighbouring target was converted correctly** (7.1% of GDP ÷ (1-α) = 0.125), which made the
  calibration look internally careful.
- **Both readings were plausible numbers.** A units error between two plausible quantities has no symptom
  except the parameter it lands in.
- **The provenance was one sentence, in the paper, and wrong** — sector, denominator and comparability all
  incorrect, with no series id, vintage or window in the workbook.

**What to do.** Beside every calibration target record the series, the window, when it was retrieved, and
**the units of both sides of the equation**. Where the datum is derived rather than typed, let a script
derive it and write that record itself, including the readings it did *not* adopt
(`python/paper/dataTargets.py`).

**The tell.** A target whose model side is a ratio of two objects at *different time aggregations* — a
stock over a flow, a per-period quantity over a per-year one. Convert the model's moment into the data's
units by hand, once, and see whether the number is one anybody would have written down.
