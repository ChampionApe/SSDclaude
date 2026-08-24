# Cross-cutting findings

Findings that recurred across module sessions and were previously written out in full in more than one
place (root `RESEARCH_LOG.md` and a module's own README/`RESEARCH_LOG.md`). Recorded once here; other
files should link to the relevant section below rather than restate it.

## 1. Bitwise reproducibility holds within a process, not across processes

Re-running an unchanged solve in a fresh interpreter differs from its own saved baseline by up to ~1e-13
(measured: 464 of 611 recorded arrays in `InformalSavings`), because numpy's SIMD dispatch varies with
array size and memory alignment. Within one process it is bitwise identical (0 of 546/561 checked, in two
separate measurements).

**Consequence for every module here**: an old-vs-new comparison for a refactor must run both
implementations **in the same process** to assert bitwise identity — a saved `.npz`/baseline compared
across runs can only ever assert ~1e-13, which is too loose to catch a subtly wrong reuse, and is
*especially* too loose for a refactor that changes array sizes (that legitimately shifts last bits on its
own). The pattern that works: paste the pre-change functions verbatim into a scratch module, monkeypatch
them in, run both in one process, compare — and check the reference path's own call counts to confirm it
was actually exercised. Used this way in `InformalSavings`' CRRA speed refactor (561 arrays, bitwise
identical, 2026-08-11).

## 2. A clip that manufactures a bracket also manufactures a root

Every bounded policy function in this project is evaluated as `clip(τ(·), l, u)`. Closing any fixed point
through one gives a residual that is bracketed on `[l,u]` for free — and therefore also has an *exact*
root at whichever endpoint the extrapolated policy overshoots, which a bracketed solver (e.g. `brentq`)
will return in preference to the interior one. This is a property of the clip, not of any one model, so it
should be checked wherever a fixed point is closed through a bounded policy.

**Concrete instance**: `InformalSavings.model.initialStatePEE`'s `eq:initialFixedPoint` residual
`τ - clip(τ¹(·), l, u)`. At `τ=u` the steady state degenerates, the implied `ι_0` leaves the state grid by
three orders of magnitude, and the extrapolated policy clips back to `u` — residual exactly zero, and a
bare `brentq` on `[l,u]` returns that degenerate endpoint. Whether the trap fires is luck, not structure:
at `ρ=1.15` the extrapolation overshoots `u` and the trap fires; at `ρ=1` (LOG) it undershoots `l` instead
and there is no spurious root — so the LOG case "worked" first and supplied false confidence in an
untested code path. Fixed by scanning the interior grid with the out-of-grid region masked to `NaN`,
taking the lowest surviving sign change, and bracketing only inside that cell — multiplicity reported
rather than resolved silently. **Do not simplify this back to a bare bracketed solve on `[l,u]`.**

## 3. "Converged" and "small residual" can both be true at the wrong answer

A nested numerical solve (outer root over parameters, inner solve/grid search over a state) can report
success with a small residual while sitting at a point displaced from the true answer, because the inner
solve's own discretization error gets silently absorbed into the outer parameters. Nothing errors; scipy's
`success` flag and a tight outer tolerance are both consistent with the wrong answer.

**The diagnostic, general to every nested solve in this repo**: hold the outer-converged parameters fixed,
refine the inner grid, and ask whether the residual decays or plateaus. A plateau means the refined
problem is already well resolved and its root is genuinely elsewhere — the outer answer is wrong, not
imprecise. A decaying residual means the coarse grid was fine. One extra evaluation, and no amount of
tightening the outer tolerance is a substitute for it.

**Concrete instance**: `InformalSavings`' CRRA calibration (§8) at the PEE solve's default `30×30` inner
grid: the outer 4-D root converges, reports success, and lands on a point where holding parameters fixed
and refining the inner grid gives `6.6e-4 → 3.13e-3 → 3.14e-3` (plateau at ~1% displacement in `β`). At
`45×45` the same refinement gives `1e-12 → 1.0e-4 → 4.4e-5` (healthy decay). Fix: the CRRA *calibration*
uses a finer inner grid (`nι=ns=45`) than the CRRA *solve* itself needs (`30×30` is fine for the PEE solve
alone, and is what `test_peeCRRA.py`/`test_peePath.py` assert their spacing tolerances against — the two
defaults are deliberately not unified).

**A third outcome, added 2026-08-11: the residual can *grow* under refinement.** The rule above has two
cases; there is a worse one. At `ρ=1.1` with piecewise-linear interpolants the same diagnostic gives
`3.3e-5 → 1.5e-4 → 2.9e-4` — monotonically increasing, meaning the model's computed targets are still
moving at the finest grid tried and the answer is not grid-converged at *any* of them. Refining further
does not help, because the error is not resolution: see #4.

**A fourth variant, added 2026-08-12: the plateau shows up as resistance to warm-starting, not just to
refinement.** The diagnostic above holds the *outer* parameters fixed and refines the inner grid. The same
signature appears one level up, before an outer point has even converged: in `InformalSavings`' `ρ` sweep,
`ρ=0.775` was attempted three times with progressively closer warm starts (from `ρ=0.8`, then `ρ=0.7875`,
then `ρ=0.78125` — a final gap of 0.00625) and landed at the same ~3.3–3.7e-6 residual every time. A
start 100× closer bought nothing, which is the same tell as a refinement that does not decay: the point is
not merely hard to reach, it is sitting at what `45×45` can resolve. A neighbouring point in the same
pocket (`ρ=0.78125`) needed 37 evaluations against the sweep's usual ~10–13, a second independent symptom
of the same limit. Full detail: `InformalSavings/RESEARCH_LOG.md`, 2026-08-12.

---

## 4. When refinement does not help, suspect the interpolant, not the grid

A grid search whose policy is stored as a **piecewise-linear** interpolant produces an outer objective that
is continuous but only piecewise `C¹`, with kinks at every cell boundary. Refining the grid moves the kinks
closer together without removing them, so a Newton-type outer solver keeps hitting them at any resolution.
The symptom is a solver that stalls at a residual far above its tolerance while each individual inner solve
looks fine, and (per #3) a refinement trend with the wrong sign.

**The fix is the interpolation kind, not the node count.** In `InformalSavings`' CRRA calibration at
`ρ=1.1`, switching the continuation interpolants from linear to cubic took the outer solve from *stalling
near `3e-5` after 60+ evaluations* to **`1.3e-11` in 12 evaluations**, and reversed the refinement trend to
`1.3e-11 → 1.7e-4 → 5.1e-5`. The located parameters differed by only 0.016% in `β` — so the linear answer
was never badly displaced; the solver simply could not descend to it. This is a different failure from #3
and needs a different fix, though the two present almost identically.

Two cautions, both learned the expensive way:
- **Comparing schemes at a fixed point is not a comparison.** Evaluating scheme B at the point scheme A
  converged to measures how far B's root has moved, not which scheme is better — done that way, cubic looks
  *worse* than linear. Re-solve under each scheme and compare the refinement behaviour of each answer.
- **Monotone (PCHIP) is the principled choice and may be unaffordable.** A plain cubic can overshoot where
  a policy is flat at a bound (`[-0.088, 3.105]` on data spanning `[0,3]` in a measured case), which
  matters for any quantity not independently clipped. But `scipy`'s `RegularGridInterpolator` rebuilds
  pchip splines on every call — 1400× slower than linear — so using it in 2-D needs a precomputed
  bicubic-Hermite evaluator that nobody has written yet.

**Checked on the `informalAnalytical` lineage (2026-08-21), and the binding defect there was #5, not #4.**
`US` (a copy of that module) was swept over `ρ` and its calibration would not resolve; pinning the
smoother's knots fixed it, while the interpolant kind did not. `cubic` failed to converge in 2 of 8
measured `(ρ, ns)` cells — the overshoot caution above — and `pchip`, which **is** affordable in that
module because every interpolant there is 1-D, agreed with linear once resolved but failed on coarse
grids. So: check #5 first on this lineage, and treat the interpolant kind as the second hypothesis rather
than the first. Details in `python/US/RESEARCH_LOG.md`.

Two refinements to the diagnostic itself, learned there:
- **Judge by the trend, not the spread.** A converging sequence spans a *wider* range than a jittering
  band does, so ranking settings by spread-of-answers prefers the broken one. The signal is the shape of
  the sequence (see #3), never its width.
- **A band with no trend is the absence of information, not a small error bar.** The adaptive smoother put
  every node count inside one 0.3% band, which looked like a converged answer with a modest uncertainty
  and was actually refinement telling you nothing — the coarsest grid in that band was 2.4% off.

## 5. A discrete choice inside a differentiated residual is a discontinuity

#3 and #4 both describe an outer solver that stalls while every inner solve looks fine. There is a third
cause with the same presentation, and it is the one that is invisible to refinement *and* to a better
interpolant: somewhere inside the inner solve, a **library routine chooses an integer from the data**.
Adaptive knot counts, adaptive quadrature orders, `argmax` over a candidate set, a root-count branch, an
active-set choice — any of them flips as a parameter moves, and the residual jumps.

Once the residual has jumps of size `J`, a root can fall *inside* one, in which case it does not exist in
the discretized problem and `|residual|` cannot be driven below `J`. That is why the diagnostic signature
is **a plateau that does not improve under a better warm start** — #3's signature — but the fix is neither
#3's resolution nor #4's interpolant kind.

**The measured instance.** `InformalSavings`' policy smoother used `UnivariateSpline(s=…)`, whose FITPACK
knot count is chosen from the data. That put ~3.5e-6 jumps in a calibration residual with a 1e-6 tolerance
and made one `ρ` uncalibratable across six attempts. Replacing it with a fixed-knot `LSQUnivariateSpline`
(`gridsearch.interp`'s `knots`) removed every jump and the point solved in 11 evaluations.
Full chain: `notes/informalSavings_rho07_resolved.md`.

**How to tell it apart from #3/#4, cheaply.** Take a fine scan of the residual along one parameter, at a
*converged* point, and look at successive differences against their median. Smooth curvature gives a flat
ratio; this gives isolated spikes. Two corollaries worth knowing before running it:
- **The step size that looks worst is diagnostic.** A finite-difference step that disagrees with both a
  smaller and a larger one is straddling a jump — a jump `J` contributes `J/h`, dominating at the step that
  first spans it and diluting tenfold a decade up. A step anomalous on *both* sides is not truncation error.
- **Aggregate counters will not find it.** Feasibility totals, root counts and selection counts can all be
  unchanged across the jump. Diff the *per-period* solution arrays instead and find the period where a
  perturbation stops propagating smoothly.

**The design rule that follows.** Anything inside a residual that will be differentiated should be a
**linear map of its input** for fixed structure, or its structural choice should be pinned from outside.
This is also the argument against auto-tuning grids or bounds from a previous run: it makes the residual
depend on solve history, which is this bug wearing different clothes.

---

## 6. Settings adopted as defences against an undiagnosed defect must be re-derived, not inherited

Companion to #5, and the step most likely to be skipped after a bug like it is found. While a defect is
present, every setting adopted to work around it *is* justified by measurement — the measurements are not
wrong, and re-reading them will not reveal anything. What is wrong is the attribution: the measurement
reports the defect as a property of the thing being measured. Fixing the defect therefore silently
invalidates the *reason* for every such setting, while leaving the settings in place and their
documentation reading as if it still applied.

**The measured instance.** `InformalSavings` had two settings adopted against the smoother's residual
jumps: a per-solver finite-difference step (a Jacobian column read 5× its resolved value at scipy's
default) and a doubled inner grid (the coarse grid appeared to converge to a *displaced* root). Both were
correctly measured and both were re-derived once the jumps were gone. They did not fall the same way — the
step was removed outright, while the grid survived on an argument an order of magnitude weaker than the
one that had established it (deviations note item 17). Neither outcome was predictable from the original
measurement, which is the reason to re-derive rather than reason about it.

**What to re-derive, and how to find the list.** Anything whose written justification cites a symptom
rather than a mechanism — "column X was corrupted", "the sequence plateaued", "it did not converge". A
setting justified by a mechanism ("the profile diverges like 1/(1-τ), so differentiate in log") is not at
risk. In practice the list is short and the note that records the settings is where it lives, which is an
argument for recording the measurement behind each setting rather than only its value.

**Two traps in the re-derivation itself.**
- *Measure at converged points.* This is #5's process note and it recurs: a diagnostic taken off-root
  cannot distinguish a defect in the residual from being in the wrong place.
- *A diagnostic whose verdict never varies is worse than none.* The grid re-measurement's first version
  classified the refinement ladder's shape including the rung at the calibration's own grid, where the
  residual is ~1e-12 by construction — so every ladder "rose" and the label fired on every row. It invites
  reading the label instead of the numbers. Check that a summary statistic can actually come out both ways
  on the data it will see.

## 7. A fix keyed to where a defect was found, rather than to where it applies

**General statement.** When a defect is diagnosed in one configuration and the fix is applied *there* —
keyed to the solver, the branch, the parameter range where it happened to surface — every other
configuration that shares the defect keeps it, and now keeps it in a codebase that reads as though the
problem is solved. The written record makes this worse rather than better: it says the finding was
understood and acted on, so the natural next question ("does this apply anywhere else?") looks answered.

The companion failure is that the *diagnostic* usually gets keyed the same way, so the configuration still
carrying the defect is also the one exempt from the check that would catch it.

**The measured instance.** `InformalSavings` established (#4) that piecewise-linear continuation
interpolants leave an outer residual only piecewise `C¹` and stall the calibration, and adopted
`interpKind='cubic'`. It was keyed to `'CRRA'`, because that is where the stall had appeared. The LOG
solver kept `'linear'` as a class default nobody revisited — so `ρ=1`, the single LOG point of every
sweep, was the one point solved on the interpolant the module had already concluded was inadequate. Its
answer does not converge in `nι`; it jitters by 2.4e-3 in `τ(t0+1)` against 2.5e-5 under cubic. The
calibration then fitted its four parameters to hit `τ(t0)=0.125` at one realisation of that jitter, and
the universalisation response at `t0+1` inherited a displacement of **+10.6% of scale** — read for a
session as a candidate LOG-vs-CRRA "solver-transition artifact". The two recursions in fact agree to
0.2% of a grid cell. Full chain: `notes/informalSavings_logCrraBoundary.md`.

The `verify` refinement check was keyed the same way: `{'CRRA': ...}`, so **every LOG row of every sweep
carries `verifyResidual = NaN`**. The one point running the unconverged interpolant is the one point with
no resolution check.

**Why it was hard to see.** The defective configuration is internally consistent — it converges, its
residual is *tighter* than the fixed configuration's (1.6e-11 against 1.1e-9), and it hits its calibration
targets exactly. A tight residual at a jittered answer is the solver descending precisely onto the wrong
number, and nothing local can tell the two apart. It becomes visible only when a second method computes
the same object and the two are compared as a *series*, which is what a fine grid straddling the boundary
buys.

**The habit.** When a fix is keyed to a configuration, write down what the key is *for*. Two keys look
identical in code and are opposites in kind: a **resolution** choice legitimately differs per solver (the
CRRA calibration needs a finer grid than LOG), while a **well-posedness** choice — is this object even
converged? — cannot, and keying it is a bug. `InformalSavings` had already drawn exactly this distinction
for `smoothKnots`, which is applied to both solvers for stated well-posedness reasons; `interpKind` is the
same kind of choice and was keyed anyway.

**Fixed 2026-08-20**, and the shape of the fix is part of the finding. The repair was *not* to correct the
class default — `CRRA._gridSettings` inherits `interpKind` from `LOG`, so flipping it there moves both
solvers' defaults and trips two suites whose assertions were themselves measured at `'linear'`
(`test_peeCRRA`'s bound-overshoot tolerance, and `test_peePath`'s "re-solving beats interpolating", which
stops holding once the interpolant is `C¹` — worth knowing on its own: that penalty was largely a linear
artifact). The repair was at the **call site that keyed it**, which is also where the mistake was: give
both solvers `interpKind`, keep the grid sizes per-solver. A defect introduced by keying is usually
repaired by un-keying it there, not by changing what it was keyed away from — the default may have other
consumers, and the tests written against it are evidence about the default, not about the bug.

The companion repair matters as much: the `verify` refinement check was keyed the same way and now covers
LOG too. It reports 5.73e-6 at the anchor — a number that had been `NaN` in every sweep ever run.

**A diagnostic that generalises.** To test whether a boundary between two methods is real, calibrate a
*fine* grid straddling it and ask whether the odd point out lies on the curve the others trace — fit
through everything except it and extrapolate in. Second differences make the answer unambiguous without a
fit: a series with one displaced point reads `[+d, −2d, +d]` exactly, which is what `η0` and `X0` gave to
two significant figures on two grids ten-fold apart in spacing. And subtract the trend before reading a
gap: the raw difference between the two methods is dominated by the true slope in the parameter, so the
statistic has to be the central average `½[x(1+δ)+x(1−δ)] − x(1)`, which cancels it and leaves the jump.

**A weaker cousin: a constant that was never keyed to anything.** (`US`, 2026-08-21.) The CRRA steady
state carried a hard-coded search bracket `(1e-6, 0.75)`. The feasibility limit it stands in for —
`Γ_h·α·κ/((1-α)·p·θ·τ)`, where `Θ_h`'s denominator vanishes — scales with `α/(1-α)` and `κ/p`, both of
which differ between modules. At `α = 0.43` with a positive informal mass the limit sits above 0.75 for
every `τ`; at `α = 0.30` with `κ = p` it falls to ≈0.58, and the solver died on a NaN while reporting a
solver problem rather than an infeasible interval. Unlike the cases above, the constant was not keyed to
the configuration where a defect surfaced — it was correct once, silently, and travelled with a file copy.
**When a copied module changes a structural parameter, every hard-coded bound in it is a hypothesis that
needs re-testing.** Fix by deriving the bound from the model, not by retuning the number: retuning only
moves the parameter value at which it reappears, and a test written against the new number would assert
the wrong thing. The test to write asserts that the bound *tracks* the model quantity.

## 8. A superseded file left beside the live ones is an input to anything that globs

**General statement.** Backups, variants and dated copies kept in the same directory as the data they
supersede are not inert. Any reader that discovers its inputs by pattern — a glob, a directory listing, a
"load everything matching" helper — will pick them up, and the resulting extra rows are usually *well
formed*, because they were produced by the same code that produced the live ones. Nothing looks broken.
The plot simply has a point that should not be there, or a series is silently doubled, or a mean is taken
over two vintages of the same experiment.

The failure is worst when the reader takes the record's **key from the file's contents** rather than from
its name. Then the superseded row carries a legitimate key, sorts into the right place, and is
indistinguishable from a real observation. Renaming the file no longer protects you; only excluding it does.

**The measured instance.** `InformalSavings` backed up `universal_match_rho1.0000.csv` as
`universal_match_rho1.0000_preInterpFix.csv` in place, minutes before regenerating it.
`plotUniversalShock.py` globs `universal_<rule>_rho*.csv` and reads `ρ` from each file's own `ρ` column, so
the backup contributed a second, perfectly well-formed point at `ρ=1` — the pre-fix anchor (6.089%) plotted
beside the post-fix one (5.488%). The figure showed a before/after comparison while purporting to show a
single series, and it was published before anyone noticed. The prose alongside it was correct, because that
analysis had filtered the backup out explicitly; the two disagreed and only the figure was wrong.

This is the third instance of the same shape in one module, which is why it is here rather than in a module
note. The other two: `shockUniversal.py`'s `--csv` default still naming a sweep a fresher one had
superseded (so it would have walked a stale CSV against instances already overwritten in place); and
`COLUMNS` declaring `occupancyι`/`occupancys` that the row-builder never copied out of the record, writing
blanks for every point across several sweeps.

**The habit.**
- **Superseded runs go in a subdirectory**, never beside the live ones (`results/shocks/preInterpFix/`,
  `results/calibration/instances_preInterpFix/`). A non-recursive glob then cannot reach them, whatever
  they are called.
- **Match the filename pattern exactly** — `rho<number>.csv`, anchored — rather than `rho*`, and say out
  loud what was skipped.
- **A duplicate key is an error, not something to resolve.** Averaging, first-wins and last-wins all hide
  it. Raise, and name both files: the ambiguity is real and the reader cannot know which vintage is wanted.
- Corollary already recorded under #7's companion: a column present in a schema is not evidence it is
  populated, and a default filename that was correct when written is not evidence it still is. All three
  are the same defect — **a pipeline trusting the shape of its inputs instead of their provenance.**

## 9. A derived parameter silently undoes any experiment that sets it

**General statement.** When a model keeps a list of parameters that are *recomputed from data* whenever
the deep parameters move — `paramsFromFuncs` here — every one of them is a trap for a counterfactual that
wants to set it directly. Write the value, call the refresh, and the refresh puts the calibrated value
back. Nothing raises; nothing is NaN; the run completes and every other number in it is internally
consistent, because the model really did solve — it just solved the baseline again.

What makes this hard to catch is that the *null result is plausible*. A counterfactual that returns the
baseline reads as "this characteristic does not matter", which is exactly the kind of conclusion these
experiments exist to produce. The absence of an effect is not evidence of a bug the way a NaN is.

**The measured instance.** `python/US/shocks.shockTheta` set `db['θ']` and then called `updateAuxPars()`
for tidiness. `θ` is in `paramsFromFuncs`, so `updateAuxPars` re-derived it through `getθ` from the
replacement-rate data. Both `θ = 0` and `θ = 1` returned the calibrated `θ = 0.7382` path — τ, the savings
rate and the workweek all came back at the baseline to every printed digit. Two polar pension systems
producing identical equilibria is not subtle once stated, but on screen it was three tidy rows of numbers.

The same refresh is *required* two functions away: `shockIncomeDistribution` changes `η`, and `Γ_h` and
`θ` are both genuine functions of `η`, so there it must be called — and it moves `θ` from 0.738 to 0.495,
which is a real part of that experiment rather than a side effect to suppress. So the rule is not "never
refresh"; it is that the refresh's inputs decide.

**The habit.**
- **Know which parameters are derived before writing one.** If it is on the recompute list, set it *after*
  the refresh, and say so where it is set.
- **A counterfactual that returns the baseline exactly is a failed run until proven otherwise.** Polar
  cases are the cheap check: `θ = 0` and `θ = 1` must not agree with each other, whatever they do relative
  to the baseline. An assertion that two scenarios *differ* costs nothing and catches this whole class.
- **Distinguish "derived from data that the shock changed" from "derived from data it did not."** The
  first must be refreshed and the change reported; the second must be left alone. Both look like the same
  line of code.

## 10. A corner makes any sensitivity check vacuous

Found in `US/test_escCRRA.py`, but the shape is general: a test that measures how much *A* moves when *B*
is perturbed proves nothing if *A* sits at a boundary, because the answer is zero for a reason that has
nothing to do with the mechanism under test.

The concrete case. `LeadedCRRA` iterates on the design path holding `θ_{t+2}` fixed while `θ_{t+1}` varies,
which is exact only if the choice at `t+1` ignores the design it inherits. That assumption is worth a test,
so the suite perturbs `θ_{t+1}` and re-optimises `θ_{t+2}`. It reported `dθ_{t+2}/dθ_{t+1} = +0.0000` and
passed — while the production run, at the same ρ, reported `−0.0092`.

The difference was the wedge parameter. The test reused the *LOG-calibrated* `p = 0.402`; at ρ = 2 that
puts the choice on the `θ = 1` corner, where both perturbations return exactly 1.0 and the slope is
identically zero. The test was measuring the boundary, not the model. It now runs at ρ = 2's own calibrated
`p = 0.086` — and gets `−0.0092`, agreeing with the production run.

**Why this is easy to miss.** The vacuous result is *more* reassuring than the real one: 0.0000 looks like
a clean pass, `−0.0092` looks like something to think about. A test whose failure mode is "returns an even
better number than expected" will not be re-examined.

**The habit.**
- **Assert interiority before measuring a derivative.** One line, in front of the check that needs it:
  `check('the choice is interior, so the next check is not vacuous', 0.02 < x < 0.98)`. Without it, the
  sensitivity check silently degrades into a boundary check.
- **Reuse of a calibrated parameter across a regime change is the usual cause.** `p` calibrated under LOG
  is not `p` under CRRA — a higher EIS needs 4.7× less of it — and a parameter carried across without
  recalibration will often land on a boundary rather than merely being slightly off.
- **When a test and a production run disagree about the same quantity, the test is the suspect**, even
  when the test is the one showing the tidier number.


## 11. Maximising over a policy that also enters a predetermined state

`base.dlnc2i_dτ`'s docstring already forbids taking `dln(c_2)/dτ` numerically off a solution grid: the
policy maker treats `s_{t-1,i}/s_{t-1}` as predetermined, the ratio moves along such a grid, and a grid
derivative therefore folds in a channel that does not belong in the first order condition. That warning was
written for τ. It applies verbatim to any *other* instrument that reaches the same state, and the
endogenous-θ work found one.

The leaded choice of θ is safe: `θ_{t+1}` does not appear in the date-`t-1` savings ratio, so maximising
the objective over it on a grid is legitimate. The **permanent** choice is not: there θ enters through
`θ_{t0}`, and a grid maximisation that recomputes the ratio at each candidate credits the electorate with
internalising a state it takes as given. The two readings are not close — **θ = 0.773 pinned against 0.910
moving**, at the same wedge — so this is a modelling error large enough to change conclusions, not a
numerical nicety.

The asymmetry is what makes it dangerous: the same objective function, maximised over a different argument,
is correct in one case and wrong in the other. The leaded implementation established the pattern, and
copying it to the permanent case would have carried the bug.

**The habit.**
- **Before grid-maximising an objective over an instrument, list the predetermined states the instrument
  appears in.** If the list is non-empty, pin them and pass them in explicitly — an argument, not a
  recomputation. `PermanentLOG.solve` takes `siRatio_` as a required argument for exactly this reason.
- **A closed-form FOC hides the question; a grid maximisation exposes it.** Differentiating analytically
  holds the state fixed automatically, because you simply do not differentiate it. Moving from a FOC to a
  grid search silently changes what is being held constant, and that change has to be made deliberately.
- **Report both readings once.** The gap is the measure of how much the convention matters; recording it
  is cheaper than re-deriving it the next time someone asks.
