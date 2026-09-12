# Cross-cutting findings

Findings that recurred across modules, written once and cited by number from code and READMEs. Each entry
is the statement, the tell and the habit. The long-form versions, with the measurements behind each, are
in `archive/findings_longform.md` under the same numbers. **Do not renumber.**

## 1. Bitwise reproducibility holds within a process, not across processes

A fresh interpreter reproduces an unchanged solve only to ~1e-13 (numpy's SIMD dispatch varies with array
size and alignment); within one process it is bitwise.

**Habit.** An old-vs-new comparison for a refactor runs both implementations in the same process
(monkeypatch the old functions in). A baseline saved across runs asserts only ~1e-13, too loose to catch a
subtly wrong reuse. Check the reference path's call counts too, to confirm it was exercised.

## 2. A clip that manufactures a bracket also manufactures a root

Every bounded policy is evaluated as `clip(τ(·), l, u)`, so a fixed point closed through it has an exact
root at whichever endpoint the extrapolated policy overshoots, and `brentq` returns that in preference to
the interior one.

**Tell.** The root sits exactly on a bound and the implied state is far outside the grid. Whether it fires
is luck: LOG undershot `l` and "worked", `ρ=1.15` overshot `u` and trapped.

**Habit.** Scan the interior grid with out-of-grid values masked to NaN, take the lowest surviving sign
change, bracket inside that cell, report multiplicity. Never simplify back to a bare bracketed solve on
`[l,u]` (`InformalSavings.initialStatePEE`).

## 3. "Converged" and "small residual" can both be true at the wrong answer

A nested solve (outer root over parameters, inner grid search over a state) absorbs the inner
discretisation error into the outer parameters; `success` and a tight tolerance are both consistent with
the wrong answer.

**Diagnostic.** Hold the outer parameters fixed, refine the inner grid, read the trend: decays, the coarse
grid was fine; plateaus, the outer answer is wrong rather than imprecise; grows, not a resolution problem
at all (#4, #5). Before convergence the same signature is resistance to warm-starting: a 100× closer start
buying nothing. This is why `InformalSavings`' CRRA *calibration* uses a finer inner grid than its CRRA
*solve*.

## 4. When refinement does not help, suspect the interpolant, not the grid

A piecewise-linear policy interpolant leaves kinks at every cell boundary; refining moves them closer
without removing them, so a Newton-type outer solver stalls at any resolution. The fix is the interpolation
kind (`cubic`/`pchip`), not the node count.

**Cautions.** Comparing schemes at a fixed point measures how far the root moved, not which is right:
re-solve under each and compare refinement behaviour. PCHIP is the principled choice but
`RegularGridInterpolator` rebuilds it per call (~1400× slower), so 2-D use is unaffordable. On the
`informalAnalytical`/`US` lineage check #5 first: there the fix was pinned smoother knots, and `cubic` did
not converge everywhere. Judge by the trend, not the spread: a jittering band is narrower than a
converging sequence and once hid a coarsest grid 2.4% off.

## 5. A discrete choice inside a differentiated residual is a discontinuity

Somewhere inside the inner solve a library routine chooses an integer from the data (an adaptive knot
count, a quadrature order, an `argmax`, a root-count branch). It flips as a parameter moves, the residual
jumps by `J`, and no root inside a jump exists, so `|residual|` cannot go below `J`. Invisible to
refinement and to a better interpolant.

**Tell.** Fine-scan the residual along one parameter at a converged point and compare successive
differences to their median: isolated spikes. A finite-difference step that disagrees with both a smaller
and a larger one is straddling a jump. Diff per-period arrays, not aggregate counters.

**Rule.** Anything inside a residual that will be differentiated is a linear map of its input for fixed
structure, or has its structural choice pinned from outside (`gridsearch.interp`'s `knots`). The same
argument forbids auto-tuning grids or bounds from a previous run.

## 6. Settings adopted as defences against an undiagnosed defect must be re-derived, not inherited

While a defect is present every workaround is justified by measurement; fixing the defect invalidates the
reason and leaves the setting in place, documented as if it still applied. Re-derived, `InformalSavings`'
two defences fell differently (one removed, one kept on a weaker argument), which is why to re-derive
rather than reason about it.

**What to re-derive.** Anything whose justification cites a symptom ("column X was corrupted") rather than
a mechanism ("the profile diverges like `1/(1-τ)`, so differentiate in log"). Record the measurement behind
each setting, not only its value. Measure at converged points (#5).

## 7. A fix keyed to where a defect was found, rather than to where it applies

A defect fixed only in the solver, branch or range where it surfaced persists everywhere else that shares
it, in a codebase that reads as solved; the diagnostic is usually keyed the same way, so the still-defective
configuration is also exempt from the check. The defective configuration converges, hits its targets, and
often has the *tighter* residual.

**Habit.** Write down what a key is *for*. A resolution choice may differ per solver; a well-posedness
choice (is this object converged?) cannot, and keying it is a bug. Repair at the call site that keyed it,
not at the class default.

**The cousin: a constant never keyed to anything.** A hard-coded bound inherited by a copied module is a
hypothesis about that module's parameters. The CRRA steady-state bracket `(1e-6, 0.75)` failed in `US`
(cap ≈ 0.58 there) and again in the ancestors when α moved to 0.35. Derive the bound from the model, check
its degenerate limits (`ΓsCap` is infinite at `θ = 0`), expand geometrically only after the default has
failed, and test that the bound *tracks* the model quantity. The same holds for a starting guess: the ρ
march's anchor guess is a declared input (`--x0`, `config.ARG['anchorGuess']`).

**Diagnostic for a suspected method boundary.** Calibrate a fine grid straddling it; one displaced point
reads `[+d, −2d, +d]` in second differences.

## 8. A superseded file left beside the live ones is an input to anything that globs

Backups and dated copies in the directory they supersede are picked up by any pattern-based reader, and the
extra rows are well formed because the same code produced them. Worst when the key is read from the file's
contents: then renaming does not protect you.

**Habit.** Superseded runs go in a subdirectory. Match the filename pattern exactly and say what was
skipped. A duplicate key is an error, never resolved by averaging or first/last-wins. A column present in a
schema is not evidence it is populated.

## 9. A derived parameter silently undoes any experiment that sets it

When parameters are recomputed from data on every refresh (`paramsFromFuncs`), a counterfactual that
writes one and then refreshes gets the calibrated value back, and the run solves the baseline again. The
null result is plausible ("design does not matter").

**Extension.** A derived parameter is pinned by the LAST refresh in the whole call sequence, not the last
one in the function you are reading: a composite shock's later step re-derived a `θ` an earlier step had
pinned (`US/shocks.py`, only in the composite rows).

**Habit.** Know which parameters are derived before writing one; set it after the last refresh; re-install
pins at the end of composites and test that they survive. A counterfactual returning the baseline exactly
is a failed run until proven otherwise; polar cases (`θ = 0` against `θ = 1`) are the cheap check. The
refresh itself may be required (a changed `η` really does move `Γ_h`); only the value installed after it is
the choice.

## 10. A corner makes any sensitivity check vacuous

A check of how much *A* moves when *B* is perturbed proves nothing if *A* sits on a bound: the answer is
zero for an unrelated reason, and it is *more* reassuring than the real one. Usual cause: a calibrated
parameter reused across a regime change (`p` under LOG put the CRRA choice on the `θ = 1` corner).

**Habit.** Assert interiority in front of any derivative check (`0.02 < x < 0.98`). When a test and a
production run disagree about the same quantity, the test is the suspect, even when it shows the tidier
number.

## 11. Maximising over a policy that also enters a predetermined state

`dlnc2i_dτ` must not be read numerically off a solution grid because the policy maker treats
`s_{t-1,i}/s_{t-1}` as predetermined; the same holds for any instrument reaching that state. The *leaded*
`θ` choice is safe (`θ_{t+1}` is not in the date-`t-1` ratio); the *permanent* choice is not, and a grid
maximisation that recomputes the ratio per candidate credits the electorate with internalising a sunk
state (0.910 moving against 0.775 pinned at `p = 0.4`). Copying the leaded implementation carries the bug.

### 11b. Pinning is one decision; *what value* to pin at is a second one

Pinning at the incumbent's ratio makes the reform unanticipated, but households save at `t0-1` knowing a
design will be chosen, so the equilibrium is the fixed point `θ* = argmax_θ W(θ ; siRatio(θ*))`, the
incumbent only the seed. The two coincide exactly where the chosen design reproduces the incumbent, which
is what the wedge calibration targets, so every calibrated number was right and the error showed only away
from the calibration.

**Habit.** Before grid-maximising over an instrument, list the predetermined states it enters, pin them,
and pass them as an argument rather than a recomputation; then ask separately what the pinned value is.
Test the convention away from the point where it is a no-op (#10).

## 12. A calibration target has units on both sides, and only one side is in the code

Argentina's savings-rate target was an annual flow set against a 30-year-period stock-over-flow model
moment, and β absorbed the factor (1.212). It survived because the period length lived only in prose (now
`yearsPerPeriod`), both readings were plausible numbers, and the provenance was one wrong sentence. The
correctly converted neighbour became the next instance: a *converted* datum stored in the workbook stayed
at the old α when α moved (0.125 at α = 0.43 is 0.109 at 0.35). Store the datum, derive the target in the
loader. A third instance had no aggregate footprint at all: informal hours were targeted against formal
*clock* hours, the derivation used the productivity-weighted `h_t`, and the two agree only under a
normalisation the code did not impose (`X0` 20× off, every τ and β unchanged; 2026-09-11).

**Habit.** Beside every target record series, window, retrieval date and the units of both sides; let a
script derive it (`python/paper/dataTargets.py`). Tell: a target whose model side is a ratio at different
time aggregations. Convert the model moment into the data's units by hand once and ask whether anyone
would have written that number down. Test a target on the solved path (the model's own ratio against the
datum), not by re-evaluating the formula that defines it: a self-consistency check passes a wrong derivation.

## 13. A resumable producer is keyed on the question, not on what answered it

A script that skips points already on disk is resumable within one setup and a silent mixer across a
recalibration: the key is the parameter point and no column records the calibration behind the row
(`sweepEpsThetaGrid.py` kept 378 of 392 rows across the K/Y retarget; the published figure showed one
fresh column inside an old surface).

**Why guards miss it.** A shape check answers "is it finished", never "is it about the current question";
the rows are individually correct equilibria of a different economy; the only tell was semantic (two
`statusQuo` rows); and `--force` was not forwarded to the child that owned the skip.

**Habit.** Give every resumable output a row that must agree with the current inputs and make the loader
check it (exactly one `statusQuo`, matching the calibration record). `--force` must reach the process that
owns the skip. Document the invalidating *event* (a recalibration), not only the invalidating setting.
Tell: a skip key that is a strict subset of what the rows depend on.

## 14. A log held open by a reader is a log the writer cannot append to

**Statement.** On Windows, Git's `tail -F` opens a file without write sharing, so a PowerShell
`Add-Content` to that file fails with "being used by another process"; inside a `.ps1` the error is
non-terminating, the script runs on, and the pipeline log ends up with its first line only while every
stage silently completes (twice on 2026-09-11: `logs/argPipeline0911.log`, `logs/usPipeline0911.log`).

**Tell.** A pipeline log frozen at `START`/`WAITING` while the per-stage logs keep growing; no `exit`
lines, no `DONE`; the stage logs' mtimes are the only record.

**Habit.** Never hold a pipeline log open: watch it with `until grep -q DONE log; do sleep 30; done`
(open, read, close), never with `tail -F` or a Monitor built on it. When the log is frozen, read the
stage logs and their mtimes before concluding anything about the run.

## 15. Spending a normalisation makes distinct objects coincide numerically

**Statement.** A free normalisation fixes units, not meaning. Imposing the hours unit
`mu = sum_i gamma_i y^x_i = 1` in the US calibration (2026-09-12, TODO C4) moved no equilibrium object at
all, but made the average workweek `hbar` equal the aggregate `h` at every date, since `gamma_i` does not
vary with `t`. The two stay different objects -- one unweighted, one productivity-weighted -- and the
`test_ee.py` check asserting they differ was right to fail.

**Tell.** A test that asserts two quantities are *unequal*, or a comment that separates them by example,
starts failing after a change that touches nothing else; the ratio between them is exactly the constant
just normalised.

**Habit.** When spending a normalisation, grep for the objects it relates and rewrite any "these differ"
check as the identity that defines their ratio (`hbar/h = mu`), with a non-normalised instance as the
control -- an equality that holds by convention is worth asserting, an inequality that holds by accident
is not. Never let other code read the new coincidence as an invariant.
