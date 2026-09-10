# Research log

Cross-cutting/structural session log. Model-specific work is in `python/<module>/RESEARCH_LOG.md`;
findings that recurred across modules are stated once in `notes/crossCuttingFindings.md` and cited here by
number rather than restated.

## 2026-07-10 — repo conventions established

Each `python/<module>/` gets its own `README.md` (purpose, file map, status) and `RESEARCH_LOG.md`; this
root log is reserved for cross-cutting sessions. Written into `CLAUDE.md`, with the root `README.md` as a
repo map.

## 2026-08-05 — log cadence and docstring density

**Log cadence**: `RESEARCH_LOG.md`/`README.md` updates happen once, at the end of a working session when
the user signals it, not after every interaction. **Docstring density** (`CLAUDE.md`): keep equation
cross-references, shape conventions and genuine gotchas; cut design history, rejected alternatives and
comparisons to the prior implementation — those belong here.

## 2026-08-06 — the condensation template

Condensed `informalAnalytical/RESEARCH_LOG.md` (~190 → ~65 lines) to fact + gotcha, **keeping every bug
and trap** — those are exactly what a future session would otherwise silently re-trigger. That split is
the template for every condensation since.

## 2026-08-10 — a copied bug, and the test class that would have caught it

A latent bug in `base.py`'s `hRatio` was found in `InformalSavings` and turned out to be present in
`informalAnalytical` too, because the file had been copied.

- **Copying a module copies its blind spots.** `InformalSavings` inherited both the bug and the absence of
  the test that would have exposed it. When a new module starts as a copy, the *tests* it does not have
  are as inherited as the code it does.
- **Both suites targeted the FOC/policy machinery only.** Nothing asserted the model's own primitive
  conditions — that consumption equals income minus savings, that the PAYG budget balances, that
  `∑γ_iη_ih_i = h`. Those identities are cheap, independent of the solution method, and caught in one run
  what four test files and a working calibration had not. Each module now has a `test_ee.py`.
- **Naming as a correctness concern.** The bug was possible because a method's name and docstring
  described a different quantity than its body computed, and five call sites split three-to-two on which
  they wanted. The fix was to name both quantities and let the call sites say which they mean.

## 2026-08-10 (cont'd) — the docs are downstream of the code

`InformalSavings.policy` was implemented from the `num_pee*.tex` specs. Six of the specs' numerical
prescriptions turned out wrong or incomplete once measured, and the `.tex` files were edited to state what
the code does.

**Derivations transfer; numerical folklore does not.** Every structural result the docs derived held
exactly and shaped the implementation. What failed on contact was the *numerical* advice layered on top:
grid bounds read off a steady state, a smoothing recommendation applied to the wrong object, a refinement
rule that made things worse. Expect that split — write the second kind provisionally and measure it before
believing it. Deviations accumulate in a per-model note between discovery and reconciliation, which is
what makes the eventual `.tex` edit mechanical.

**A mistake worth not repeating.** One deviation was written up with a confidently wrong mechanism, caught
only because putting it into the paper prompted an isolated measurement. The original data had already
contradicted the story — the error was non-monotone in the refinement — and had been read past, because
the story was plausible and the measurement had two variables moving at once. **A mechanism claimed in the
paper needs a measurement that varies one thing, and a non-monotonicity is a fact to explain, never noise
to average over.**

## 2026-08-10 (cont'd) — reuse that is silently approximation

**"Reuse" and "approximation" can be the same line of code.** Two bugs were mirror images: a bound reused
as a bracket (#2), and a solved policy surface reused as a state transition. In both the reused object was
genuinely already computed, correct, and the right type — and using it still replaced an exact evaluation
with an approximate one. The tell in both was that the *doc* named a different object than the code
reached for. **When a later section consumes an earlier section's output, check whether the derivation
asked for that output or for something the output happens to be interpolable into.**

**A luck-dependent bug is a reason to test both cases first.** The bracket bug was invisible under LOG and
fatal under CRRA, differing only in the sign of an extrapolation. The log case was implemented first,
"worked", and supplied false confidence.

## 2026-08-11 — nested solves, and writing a repeated finding once

Two findings went into `notes/crossCuttingFindings.md` (#1 bitwise reproducibility, #3 converged-but-wrong
nested solves) rather than here. Both belong to the same family as the 2026-08-10 entries: **the failure
mode of a nested numerical method is almost never a loud one, and the test that finds it is usually a
comparison the method itself does not make.**

A repo-wide pass then established the rule that produced that note: where a finding had been written out
in full more than once (root log, a module log, that module's README), write it once and reference it.
Section-header block comments that restated their own README became one-line pointers. **Left untouched**:
per-method docstrings, and the long docstrings that are the working rationale for a non-obvious choice
sitting on the method that implements it — those are the "genuine gotcha" `CLAUDE.md` says to keep close
to the code.

**Where the parameter-march helper lives.** Calibrating across a grid needs logic all three variants want,
but the model modules are deliberately self-contained duplicates. The split: the model-agnostic part is
`gridsearch/continuation.py`, which never touches a `db`; each model gets a thin `calibrateGrid` adapter.
First module in `gridsearch` about *sequencing* grid searches rather than performing one — it stretches
the package's stated purpose, and the justification is that the alternative was three copies.

**A methodological point, repo-wide.** Two interpolation schemes cannot be compared by evaluating both at
a fixed point one of them converged to — that measures how far the other's root has moved, and it made the
better scheme look worse on the first attempt. Compare by re-solving under each and comparing refinement
behaviour. Same for grids, tolerances, and any setting that moves the located solution.

## 2026-08-19 — a third cause for "the outer solver stalls", and a Windows output trap

**#5** joins #3 and #4: a **library routine choosing an integer from the data** inside the residual. It is
recorded as cross-cutting because the diagnostic recipe is model-agnostic, and because it generalises into
a design rule the whole repo follows — anything inside a differentiated residual should be a linear map of
its input for fixed structure, or have its structural choice pinned from outside. That rule is also the
argument against auto-tuning grids or bounds from a previous run.

**A Windows trap that cost two aborted runs.** Test files and sweep scripts print Greek parameter names.
When stdout is a console this is fine; when it is a pipe or a log file, Python on Windows defaults to the
ANSI codepage and the first `β` raises `UnicodeEncodeError`. In `calibrateRhoGrid.py` it surfaced as
`marchGrid` reporting "the anchor value 1.0 failed to solve" — a genuine-looking numerical failure with a
clerical cause. Closed at source 2026-08-20.

## 2026-08-19 (cont'd) — re-deriving what was built on a defect; a shock-experiment pattern

**#6**, the companion to #5: two settings adopted against the smoother's jumps were re-derived and did not
fall the same way — one removed outright, the other kept on an argument an order of magnitude weaker. That
asymmetry is the finding, and it argues for something the whole repo does: recording the *measurement*
behind each setting, not only its value. Without that, the list of things to re-derive cannot be
reconstructed.

**A shock-experiment pattern that generalises.** Baseline solve → read the state entering `t0` → build the
model copy → change the parameter → re-solve from that state. Two lessons not specific to `ε`:

- **Changing a parameter is not the same as passing it.** Aggregates derived from a parameter and cached
  in `db` are read by every equation as givens, so a call that passes a new path but leaves the cache
  alone solves a mutually inconsistent model *without violating any equilibrium condition*. Nothing
  detects it.
- **Restriction is not recomputation at the boundary.** `_sliceDb` restricts lagged entries, so the copy
  inherits genuine pre-`t0` values — correct under no shock, stale under one, wherever a lagged object
  depends on the changed parameter.

Also worth carrying: write an experiment with **two readings of the same reform** when the definition is a
modelling choice rather than a datum. Here "universal" admitted two, and they bracketed the status quo
rather than differing in degree, so every response reversed sign. One reading would have looked like a
result.

## 2026-08-19 (cont'd) / 2026-08-20 — a fix keyed to where a defect was found

`InformalSavings`' `ρ=1` boundary artifact was #4 recurring where nobody looked, and became **#7**. Two
parts generalise beyond it:

**A tighter residual can be the wrong answer, more precisely located.** The defective configuration
converged *better* than the fixed one and hit its targets exactly, because a target was being fitted at
one realisation of a jittering solve. No local diagnostic separates those. What did was computing the same
object a second way and reading the two as a **series** — a fine grid straddling the boundary, and second
differences, which for one displaced point read `[+d, −2d, +d]` exactly, reproduced on two grids ten-fold
apart in spacing. Worth reaching for whenever two methods meet at a parameter value, which here is every
`ρ=1`.

**Ask what a change can reach before re-running the pipeline.** A full 16-point sweep was launched and the
user stopped it with the right question: if the fix only changed what is passed to the LOG solver, why
re-solve the CRRA points? Solver selection is `ρ==1` exactly, so one row's residual function changed; the
rest keep their own, and a warm start moves the path to a root rather than the root — verified at 8 CRRA
points, which returned the published parameters to 6 significant figures. **30 s against ~2.5 h.** The
machinery to exploit a small blast radius existed and went unused because the blast radius was never
estimated.

**#8** came from a backup taken in place that became a datapoint in a published figure. *Also worth
carrying*: the figure and the prose beside it disagreed, and only the figure was wrong, because the
analysis behind the prose had excluded the stale file explicitly while the plotter had not. Two readers of
the same directory with different filters is a standing invitation to that. One loader, one filter.

## 2026-08-20 (cont'd) — a shared test harness and a repo-wide runner

All 16 test files re-declared the same six-line `check()` block with formatting drift, and **none
reconfigured stdout**, so the cp1252 trap recorded the day before was live in every one of them. Both
problems have one fix: `gridsearch/testing.py`, which provides `check`/`report` and reconfigures the
streams on import. Verified under `PYTHONLEGACYWINDOWSSTDIO=1` with output redirected — the exact
condition that used to break — rather than only under a console. It lives in `gridsearch` because that is
the only importable package.

*Worth carrying:* the trap had been correctly diagnosed, written into two READMEs and this log, given a
workaround, and left in place. The workaround is what kept it alive — it made every individual encounter
cheap enough not to fix, while the cost of forgetting it stayed a whole aborted run. **A documented
workaround for a one-line fix is a decision to keep paying, and should be re-read as one.**

`python/runTests.py` registers every suite, classifies fast/slow by wall time, and runs each as a
**subprocess** — the model suites mutate their instance's `db` and would collide in one process. *A defect
it surfaced immediately*: `test_roots1d.py` printed its verdict but never called `sys.exit`, so it had
always exited 0. Nothing had ever checked, which is why it survived. Check counts were also stale in three
READMEs; `report()` now prints them, so the number in a README can be read off a run instead of maintained.

## 2026-08-21 — a paper pipeline, and a normalisation mistaken for a result

`python/paper/` was built to generate `writing/Paper`'s tables and figures. It is the repo's fifth
`python/` folder and the first that is neither a model nor a numerical package.

**Three stages, separate entry points.** The load-bearing part is that **stage (iii) imports no model code
and unpickles nothing** — it reads csv, writes tex and pdf, and takes seconds. That is what makes it safe
to re-run after every caption edit, and why the expensive stages are separate commands rather than a
`--refresh` flag: a paper rebuild can never silently become a 2.5-hour solve. The corollary, enforced
rather than hoped for: **an output whose inputs are missing is reported and skipped, never partially
written.** Stages (i) and (ii) are *declarations* — their value is that the settings the published numbers
were produced at are a file rather than shell history.

**A free normalisation reported as a result — the session's real mistake.** The paper reports an average
workweek; the model's aggregate `h` has no scale. Converting with `h·(7·12)` inverts how the
*pre-determined* period's hours enter as a model *input*; it is not a scale the solved `h_t` inherits. What
makes this worth recording is not the wrong formula but what it produced: the baseline came out at 44.22
instead of 42.54, and `h` varied across `ρ` where `τ` and the savings rate did not — and I wrote that
spread into a table note and a README as a *finding*, with a plausible mechanism. It was an artifact of
dividing by a constant instead of by each `ρ`'s own baseline. **A quantity with no scale cannot have a
cross-run spread that means anything; that the explanation was available is what made it convincing.** The
guard is now structural: `config.workweekHours(h, hRef)` takes the reference as a required argument.

*Related, stated by the user:* the paper's current numbers come from a different codebase. Differences
against it are two code generations being compared, not errors being corrected. I had called them "stale"
more than once.

**Two independent routes to one number, and the disagreement they caught.** `datasets.seedSavings`
recovers `s_{t0-1}` two ways and raises if they disagree. It fired immediately, on my own bug: vector
fields were being written to csv as a python repr, and under numpy 2 the repr of a list of `np.float64`
is `np.float64(1.64…)`, out of whose literal text a number-scraping reader mines a spurious `64.0`. *Worth
carrying:* the check was written for a stale-experiment scenario and caught a serialisation defect
instead — a cross-check pays out in the case it was not designed for, which is the argument for writing it.

**Parallel agents against a fixed output contract.** The two missing experiments were built concurrently.
What made that work was fixing the csv schemas before either started, and scoping each agent to a new file
so no shared file had two writers — READMEs and logs explicitly excluded and written afterwards from their
reports. The one contract gap surfaced while writing the builders and was patched by messaging the running
agent rather than by a follow-up pass.

## 2026-08-21 — a module documented before it was coded

`US` went from empty to documented, implemented, tested and swept in one session.

**Docs first is worth repeating.** Every other module here was documented after the fact. This one was
derived in tex before any code existed, and two structural results fell out of the derivation rather than
out of debugging: removing the informal household makes the LOG first-order condition decouple across time
(so the PEE path is `T` independent scalar problems), and `η`/`X` carry *two* independent invariances
rather than one. Neither would plausibly have been noticed by porting the parent module and running it —
it works either way, just with a vacuous recursion and an unexamined normalisation.

**The two-invariance distinction closes the loop on the previous entry's mistake.** With
`y^η = η^{1+ξ}/X^ξ` and `y^x = (η/X)^ξ`, every aggregate uses `y^η` alone, so the model has a *scale* and,
separately, an *hours unit* that moves individual hours and the workweek and nothing else. A workweek is
comparable only to the unweighted average `h̄`, and `h` cannot pin the hours unit even in principle,
because it does not respond to it. The general rule: **before treating a level as a result, find the
transformations the model is invariant under and check which one it moves under.** There can be more than
one, and they need not act on the same objects.

**#4's closing question is answered, and the answer was #5.** The check finally happened on `US` (same
lineage as `informalAnalytical`), and the binding defect was the adaptive knot count, not the interpolant
kind. Two transferable lessons went into the note: judge a refinement study by the **trend, not the
spread** (the converging setting had the *wider* range and was nearly dismissed for it), and **a band with
no trend is the absence of information, not a small error bar**.

**A constant that was safe by parameter values rather than by construction** (now part of #7): the CRRA
steady state's hard-coded bracket was correct once, silently, and travelled with a file copy. **When a
copied module changes a structural parameter, every hard-coded bound in it is a hypothesis that needs
re-testing.**

## 2026-08-22 — a second pipeline arm

**`python/paper/` now has two model arms**, split by *delegation target* rather than by model: the two
arms hand off to experiment scripts with different CLIs, and those files exist to record the settings the
published numbers were produced at. A single entry point carrying both flag vocabularies would have made
that record harder to read, which is the one thing it must not be. Stage (iii) stays shared because it is
model-agnostic by construction.

**#9**: a derived parameter silently undoes any experiment that sets it. What makes it worth a numbered
finding is that **the null result is plausible** — a counterfactual that comes back at the baseline reads
as "this characteristic does not matter", which is exactly the kind of conclusion these experiments exist
to produce.

**A convention that had to be recovered rather than read off.** The paper's "savings rate" is `s/(w·h)`,
not `Base.savingsRate`'s `s/Y`; they differ by exactly `(1-α)`. Nothing in the code or docs said so — it
was found by noticing that `0.15374/0.7 = 0.21962` against the table's 21.96%. **Where a published number
and a computed one differ by a clean factor, check the definition before checking the model.**

**Correction to the `US` README**: I had described the level of `Γ_h` as arbitrary. It is a
*normalisation* under `ModelUS`, and under `ModelFR` the hours target pins it, so it is data-determined
there. In neither case is it irrelevant — it sets the level of `h`, `s`, `c`, `Y`. The distinction earned
its keep immediately: the λ-is-an-increment bug in `ModelFR.calibrate` was findable only because `Γ_h`'s
level is a result worth checking.

**Data**: `FRMain.xlsx` and `UKMain.xlsx` carry no `30y interest` column, so `testEU.load` sets
`db['R0'] = NaN` deliberately rather than leaving the US default in place. Same shape as `getEps` raising
on `γ_0 > 0`: **a plausible-looking inherited number is worse than an absent one.**

## 2026-08-24 — endogenous `θ`

Substance in `python/US/RESEARCH_LOG.md`. Cross-cutting:

**#10** (a corner makes any sensitivity check vacuous) and **#11** (maximising over a policy that also
enters a predetermined state), later extended by **#11b** (pinning is one decision; *what value* to pin at
is a second one). All three are the same species as #3–#9: not bugs in an algorithm, but ways for a
defensible-looking number to be the wrong number. #11b's specific lesson: **a decision that is a no-op at
the calibration point is a decision no calibration check can catch** — it has to be found by asking what
the timing *means*.

**A structural result that changes how the docs read.** Under log preferences the political objective is
additively separable, `W_t = A(τ_t, θ_t) + B(θ_{t+1})`, so the leaded choice of `θ` has **no state at
all** — not a weak dependence on the inherited design, an exactly zero one, measured across the whole
state grid. The appendix sets that problem up with `θ_t` as a state; it is one for the tax and not for the
design. Documented as a proposition rather than left as a numerical curiosity, because it is what makes
the solver a sequence problem instead of a recursion.

**A csv-write convention.** Incremental drivers must **merge into shared csvs, not overwrite them**: a
plain `to_csv` after each run clobbers every row the current run did not produce. The sweep scripts never
had this problem because they own resume logic per csv. Generally: *any script that writes a csv other
invocations of itself also write must read it back first.*

**A session-tooling trap**: appending python through a quoted bash heredoc halved every `\` — fatal where
a raw string then ended in a lone backslash, and silent where `\hline` became a still-parseable one inside
emitted tex. Emit code containing backslashes through Write/Edit, never through a heredoc.

## 2026-08-24 — a calibration target's units

The Argentina arm targeted a savings rate of 18.4% and calibrated β = 1.212 at ρ=1. The answer was not in
the solver, the denominator, or the datum's sector coverage, but in its **time dimension** — full detail in
`notes/argentina_calibrationTarget.md`, transferable form in **#12**.

**What let it survive** is the generalisable part. The 30-year convention existed only in the
documentation; no line of code mentioned it, so nothing in the model could be inconsistent with it and no
test could see it. The neighbouring target had been converted correctly, which made the calibration look
internally careful, and both readings were plausible numbers — 18.4% of output is a plausible saving rate
and the implied K/Y of 4.0 a plausible capital-output ratio; they simply were not the same claim.
**A convention that lives only in prose is a convention the code cannot be checked against**;
`yearsPerPeriod` is now a model parameter for that reason. The replacement target is derived by a script
that writes the value, its window, its source and its retrieval date into `data/`, and the alternative
reading beside it — so the next person sees not only what was targeted but what was passed over.

## 2026-08-24 — repository cleanup

A pass over every README, research log, note, result file and test suite, at the user's request, to cut
each to essentials. No numerical behaviour changed; the full fast suite and `build.py` were run before and
after.

**What was deleted, and the policy behind it.** Superseded results (pickles, sweeps, the pre-new-path
convention csvs), resolved diagnostics whose findings are recorded in `notes/`, all 36 run logs, and the
two vendored `inspiration/` copies of the prior implementation. The policy the user set was *git history
is the archive* — which is only true if the deletions are committed, so everything was first captured in
one snapshot commit (`bfba998`) and deleted after it. Two directories were the **only** copy of something
outside git before that commit (`results/paper/superseded/`, the hand-written paper tables `build.py` had
replaced), and the commit that removes them names where to recover them.

**Documentation was cut roughly in half** (READMEs 173 KB → 74 KB, notes 2048 → 925 lines), with the
long-form measurements demoted to `notes/archive/` rather than dropped. The rule applied throughout: a
README states purpose, file map and status plus the traps that will cost a run if forgotten; a measurement
that cost a solve goes to a note; narration of how the code came to be goes nowhere.

*A defect the deletions surfaced, which is #8 in the other direction:* `measureOuterSettings.py` defaulted
its `--csv` to a superseded sweep. Removing that file turned a silent staleness into a loud failure, which
is the argument for deleting superseded files rather than filing them — a stale default that still
resolves is worse than one that does not.

## 2026-08-25 — a published figure built from two calibrations

Structural because the lesson is not about the `(ε,θ)` sweep. `crossCuttingFindings.md` gains **#13: a
resumable producer is keyed on the question, not on what answered it.** A script that skips points already
on disk is resumable within one setup and a silent mixer across a change in what produced the rows —
the key is the parameter point, and nothing in the row records the calibration behind it. The K/Y retarget
moved the calibrated `ε`, the sweep was re-run without `--force`, and 378 of the resulting 392 rows were
bit-identical to the pre-retarget file. `ARG_LOG_FourInOne` then showed one column of the current economy
inside a surface of the old one. Detail in `python/paper/` and `python/InformalSavings/RESEARCH_LOG.md`.

**Three repo-wide habits come out of it**, all in #13. A shape check answers "is it finished", never "is it
about the current question" — staleness here *added* a column, so the rectangle check passed. Every
resumable output should carry a row that must agree with the current inputs, and the loader should check
it; the distinguished point already in the grid usually serves for free. And **a flag that only defeats the
caller's own bookkeeping is worse than no flag** — `runShocks.py --force` was never forwarded to the child,
so following the documented remedy would have produced the same stale file with more confidence in it.

**The audit that would have caught it earlier is cheap and was not being run**: diff `results/paper/` against
`writing/Paper/` after any change to a calibration. It also isolates hand edits to the draft from line-ending
rewrites, which `git status` cannot separate — used that way in the same session to reconcile three
hand-edited tables back into `config.py`/`tables.py`/`tablesUS.py`.

## 2026-08-25 — the num docs rebuilt as public technical notes

All three `writing/<model>/num*.tex` sets were restructured for the repository going public, one pattern
per model: `num.tex` opens with a three-pillar strategy overview (FOC-as-root plus the closed-form
`s_{t-1,i}/s_{t-1}` reduction that keeps the savings distribution out of the state space; grids robust to
corners and multiplicity that reuse their evaluations for the objective and the numerical gradients; the
structure each variant exploits — LOG triangularity/decoupling, the CRRA broadcast, the ESC
objective-on-grid) and cites the GitHub URL. The generic machinery is stated once per model in
`num_robustroot.tex` ("Robust policy search with bounds"), where `eq:root` is now written on general
`[l,u]` (matching what `gridsearch/robustRoot.py` implements) and
`eq:extendedGrid`/`eq:objectiveProfile`/`eq:candidates` moved in from `num_peeLOG.tex` — label *names*
unchanged, so every docstring cross-reference survives without touching a `.py`. The planning inventory
behind the cut is `notes/numAppendix_analytical_planning.md`.

**The writing rule applied: docs hold no memory.** Final state only — the measured tuning chronicles
(InformalSavings' ι-grid bounds, the calibration step-size and grid-displacement tables) were compressed
to the design rules they justified (default √ε finite-difference step with the fixed-knot smoother as its
stated precondition; cubic continuation surfaces under CRRA; the decay-vs-plateau refinement check behind
the 45×45 inner grids), with the journeys remaining in `notes/informalSavings_*` and the module logs.
Kept in full, per the user: every ESC methodological innovation (objective evaluated on the design grid so
corners are observed rather than inferred, the pinned-ratio discipline, scan-not-bracket for a
corner-flat residual) and the correctness gotchas (closed-form-only derivatives, the ρ→1 overflow
identities, corner-as-exact-zero, residual-not-success-flag).

**Defects fixed in passing.** `\Eqref` was used in `US/num_esc.tex` but defined nowhere in the preamble —
replaced, no uses remain; `US/num_esc.tex` referenced `\refeq:esc:auxiliary:si` where the label lives
under the model prefix (`\refmodeleq:`) — a latent dangling reference; and
`informalAnalytical/num_calibration.tex` now defines `calibration:KY/:tau/:sr`, which `base.py`/`model.py`
docstrings already cited but the tex never labeled.

**A checker gotcha worth keeping.** The quick bash/grep label check silently failed to extract
`\refmodeleq:` references and reported all-clear on a comparison it never made. The prefix-aware Python
checker (label prefixes normalized per file kind, model↔num cross-references included) is the one that
counts; it verified all three doc sets with zero dangling references.

## 2026-08-27 — a pinned parameter is pinned by the LAST refresh, not the last one you can see

Structural because the lesson is not about `θ`. `crossCuttingFindings.md` **#9 gains its second instance**,
and it is the one the finding's own habit does not catch. #9's rule was "set a derived parameter *after*
the refresh that would recompute it". `shocks.shockIncomeDistribution` does exactly that. Then
`shockFrenchAll` calls `shockVoting` two lines later, whose own `updateAuxPars` re-derives `θ` from the
`η` now in db — France's. The pin was undone in the composite rows and nowhere else: the
single-characteristic row is correct precisely because nothing runs after it.

**So the rule extends: a derived parameter is pinned by the last refresh in the whole sequence, not by the
last one in the function you are reading.** Composing two individually correct shocks is not itself
correct, and the composite is where nobody looks — `frAll` came back on `θ = 0.551` where 0.738 was asked
for, with τ, savings and hours all plausible. It was caught by reading the run's printed output against
what had been requested, not by a test; the test exists now, and covers each composite as well as each
single shock.

**A second habit out of the same session, about checks rather than about code.** The US arm's two
calibration variants are supposed to check each other: run the same shock set under both, and quantities
the variant cannot touch must agree while quantities defined through `η` or `X` must differ. The check as
written asked the *leisure* row to differ **in τ** — and leisure is a pure scale, so τ cannot move under
either variant. It agreed to 2.3e-5 and would have gone on reporting a pass through any breakage of the
thing it was meant to police; the row's whole variant content is in the workweek (34.74 against 33.24).
**A check keyed to a quantity that cannot move is not a weak check, it is not a check** — and it reads as
one of the strongest, because it never fails.

Detail in `python/US/RESEARCH_LOG.md` (the pin, and the ESC leg's common-X variant) and
`python/paper/RESEARCH_LOG.md` (common `X` as the headline calibration, one builder per variant pair, and
a `sharey` axis inversion that was correct only by panel-count parity).

## 2026-09-08 — the baseline savings rate is a prediction, not a row; and a zip round trip to Overleaf

**A pre-reform row taken from the ρ = 1 calibration is wrong at every other ρ, in both arms.** Neither
arm targets the savings rate any more: Argentina identifies β by K/Y (since the 2026-08-24 retarget) and
the US by the interest rate, so the 2010/2020 savings rate is an equilibrium outcome that moves with ρ —
15.3% → 14.1% across the Argentina grid, 22.7% → 21.2% across the US one (paper units). The tax rate is a
target and the workweek a per-ρ normalisation, so those two columns *are* common; the savings rate only
looked like a third. `Argentina_funcOfRho` printed one pre-reform row from the calibration summary and
thereby showed the reform *raising* savings at ρ = 0.5 (15.27% against 14.72%), contradicting the figure
beside it, which differences each ρ against its own baseline (−0.07 p.p.). Fixed: a pre/post pair per ρ,
the pre-reform row read off that ρ's baseline path. **The three US CRRA tables carry the same defect and
are not yet fixed**: read against their single ρ = 1 baseline, the savings effect appears to grow with ρ
in every scenario; against each ρ's own baseline it mostly shrinks, and for θ = 0, θ = 1 and the leisure
row the sign flips (leisure is a pure scale and cannot move savings, yet the table implies ±0.8 p.p.).
The ESC tables and both overview figures were already per-ρ. Detail and numbers in
`python/paper/RESEARCH_LOG.md`.

**Why Argentina's β exceeds the US's, and why α ∈ [0.30, 0.43] is on the table.** In
`python/InformalSavings/RESEARCH_LOG.md` and `notes/argentina_alphaSensitivity.md`.

**`writing/overleaf.py`: export/import by zip, no git sync.** `export note|paper` zips the sources with
`main.tex` at the root for Overleaf's *Upload Project*; `import note|paper <zip> [--dry-run] [--all]`
brings *Download Source* back. Import never deletes, writes only text sources unless `--all` (so an old
zip cannot roll back pipeline-built figures), and refuses to overwrite anything carrying the
`%% GENERATED` banner — an online edit to a generated table is reported so the change goes to its source.
Export first resolves every `\input`/`\subimport`/`\includegraphics`/`\addbibresource` against the zip
contents *case-sensitively* and refuses on a miss. That check found three references that compile here
and would fail on Overleaf's Linux: `\input{Packages.tex}` for `packages.tex` in the note, and
`\addbibresource{references.bib}` for `References.bib` in both preambles. All three now match the files.
`writing/exports/` is gitignored. The Overleaf side stays manual by design.

## 2026-09-08 — the paper rebuilt as four sections, α = 0.35 launched, and two constants that were data

**Decisions, from the user.** Argentina's capital share moves from Frankema's economy-wide 0.43 to a
formal-sector 0.35 net of mixed income (Gollin), K/Y kept at 3.23; every table in both arms reports the
savings rate as s/Y and as a change against that ρ's own baseline; the two overview figures lose their
composite rows and the ESC figure becomes a dumbbell chart; and the "Quantitative Analysis" section is
replaced by four — numerical methods, Argentina, rich OECD, endogenous design. The plan and the state of
each item are in `notes/todo_paperRewrite.md`, which is the entry point for the writing sessions.

**Two constants that turned out to be statements about the data, not about the model.** The α change
killed the ρ march twice before it ran. First the `ι` state grid was degenerate at the anchor: the grid is
built from the steady state at the parameters the residual is *first* evaluated at, and the anchor's
only source of those was the workbook default `β = 0.6, ω = 2`. Second the first CRRA point died on the
inherited bracket `(1e-6, 0.75)` for `Γs` — the constant the US module had replaced with a derived cap on
2026-08-21, on the reasoning that it was "safe at Argentina's parameters". It was, at α = 0.43. Both are
now inputs (`config.ARG['anchorGuess']`, `steadyState_CRRA_bounds` in both Argentina modules);
`crossCuttingFindings.md` #7 gains the instance. The habit: a bound justified by the current parameter
values is re-tested by every change to the data, and the module that "does not have the problem" is the
one to check first when the data moves.

**A tooling trap that read as a model failure.** Editing the workbook with openpyxl dropped the cached
values of its formula cells, so pandas read θ, ε and three population cells as NaN and the first symptom
was a degenerate state grid deep in the solver. Edit workbooks through Excel; `logs/` (gitignored) now
holds the detached-run scripts and their logs, and `PYTHONUTF8=1` is required for any pipeline run.

**Restructure without rewriting.** The old section was sliced, not edited: the Argentina and OECD
sections are the old subsections promoted, the ESC appendix is the new `sec:esc` verbatim apart from the
figure paragraph and the s/Y numbers, and `Sections/Numerical.tex` is an outline plus the two surviving
paragraphs. Every place that still quotes an α = 0.43 magnitude carries a `%% TODO-ARG035` comment for the
Argentina session to grep. One real defect found by the reference checker: the CRRA
pension-characteristics table was input twice, in the main text and in the appendix.

## 2026-09-08 (writing) — a style guide, the numerical section, the OECD pass, and two checks that changed the record

The first writing session of the rewrite (`notes/todo_paperRewrite.md` is the plan; this entry is what it
did and what it learnt). Working method agreed with RKB and kept: lay out the options before writing
anything, then write.

**A style guide before any prose.** `notes/paper_styleGuide.md` synthesises the draft's own conventions
(voice, paragraph anatomy, units and precision, terminology, LaTeX habits) so new text blends in. The
draft carried two registers — the plain textbook register of the older sections and a more rhetorical
one in the September additions (dashes, "in disguise", meta-commentary on the paper's own claims) — and
the guide picks the plain one as the target. It also records that the introduction's two-argument
parencite form is not valid biblatex.

**The numerical section, and what it does not claim.** Written as a compact section from the three
`num*.tex` sets: six run-in headings, the candidate-set rule and the additive decomposition of the
first-order condition in the informal savings ratio as its only displays, the generic nested-fixed-point
calibration and the ρ march (targets stay in the application sections), one forwarding sentence to the
endogenous-design section. Decision with RKB: no methodological contribution is claimed; the state-space
reduction is an economic result already in section 3, the objective reconstruction is a device, and the
rank-one / exact-unnesting structure is model-specific exploitation. The endogenous-θ solution was judged
an extension of the same machinery (direct objective evaluation on a design grid because the corner is
the question; separability and concentration are economics; the CRRA recursion is the tax recursion with
one more state) and stays in `sec:esc`.

**A literature claim that was wrong, caught by RKB.** The first draft said the numerical
politico-economic literature uses backward induction on a state grid. Checked against the papers' own
text: Krusell–Ríos-Rull (1999) compute a stationary policy function as a fixed point by linear-quadratic
approximation; Song (2011) does the same by Chebyshev projection for CRRA; Gonzalez-Eiras–Niepelt (2008)
have the closed form and only footnote a numerical CRRA check, and both they and Song use finite-horizon
backward induction as a proof device (uniqueness "in the limit of finite-horizon economies"). The section
now states the difference: we compute a sequence of date-specific policy functions, which is that
finite-horizon-limit equilibrium, selected by the terminal condition where a stationary fixed point can be
multiple (Forni 2005), with the demographic transition entering directly. A difference, not a
contribution. `KrusellRR99a1` added to the bib.

**The OECD pass.** The draft's US/UK/FR tables were stale copies (savings as levels over labour income);
the rebuilt ones and the three US figures were copied across, and every number in the section re-read
against them — all held, one overstatement softened ("an order of magnitude" → "several times"; the
inequality/ageing ratio is 3–7). Rearranged so the CRRA robustness has its own heading and the
interpretation paragraphs close the section on the hand-off to `sec:esc`; the IES paragraph duplicated
from the Argentina section became a cross-reference. The vector-X appendix argued the wrong direction
(France's income distribution as a *smaller* change while quoting a *larger* tax effect); fixed.

**Two things a reader caught that the pipeline could not.** "See the note above" in the Argentina
calibration pointed at a tex comment; the capital-share paragraph is now written (formal-sector share,
Gollin's mixed-income argument, the (0.43−y)/(1−y) bracket 0.30–0.40 with 0.35 taken, a footnote on why
K/Y stays at 3.23). And the tax target: spending over formal output is τ(1−α), so the 12.5% literal was
0.071/0.57 and belonged to α = 0.43; at 0.35 it is 10.9%. The experiments session took it from there
(the workbook now carries spending, τ₀ is derived — finding #9 again) and relaunched. Every "% of GDP"
conversion in the Argentina prose uses 0.65 from now on.

**Table 3.** `Argentina_funcOfRho` now prints one shared pre-reform row (τ, workweek; savings `--`) and
"Change in savings rate" against each ρ's own baseline, with a guard that the pre-reform τ is common.

**Overleaf.** Two zips exported during the session; RKB edits online from here, so further exports are on
request, and the import script's dry run is the way changes come back.

## 2026-09-08 (evening) — a converted datum is a stale datum: the tax target moved with α

RKB caught it after the first α = 0.35 sweep was running: the workbook's tax target 0.125 was 7.1% of
GDP converted at α = 0.43, since spending over formal output is τ(1−α). Under α = 0.35 the target is
0.109, and ω had been calibrated to a number that no longer meant what it said. The run was killed and
relaunched with the datum stored (spending share) and the target derived in the loaders; β moved a
further 0.686 → 0.651, ω 1.616 → 1.527, R and the informal parameters not at all. Finding #12 gains the
instance — the neighbouring target that #12 had praised for being converted *correctly* was the one
that went stale, because the conversion's input was baked into the cell. Store the datum, derive the
target.

**The pass, end to end.** Calibration 16/16 in 3.2 h (the low-ρ tail takes ~17 min a point), shocks
50 min (the README had said 2.5 h), tests all green after the anchor re-pin, build copied into the draft
and the Argentina prose re-read against it (`python/paper/RESEARCH_LOG.md`). The plan note
`notes/todo_paperRewrite.md` now has items 1–4 closed except the endogenous-θ writing pass; the
introduction's three `XXX` author notes and the two Frankema checks are RKB's.

## 2026-09-08 (late) — Overleaf by git after all

Uploading a zip into an existing Overleaf project does not extract it, so every zip export meant a new
project. The DeiC instance has the Git integration, and `writing/overleaf.py` gains `push`/`pull`: a
clone of the project under the gitignored `exports/`, `push` copies the export's file set over it
(same reference check, deletions propagated), `pull` applies the zip import's rules to the clone. This
repository's own history is never involved. Three things the stand-in test (a local bare repo) forced:
a first push knows nothing of the online history, so it refuses if any online text source differs and
asks for a `pull --dry-run` and then `--force` once; the clone runs with `core.autocrlf=false` and all
comparisons normalise line endings, since Windows git's checkout otherwise reported the whole project
as changed on every pull; and a pulled file keeps the local file's ending style. Tested: co-author edit
detected, pulled, overwritten with `--force`, second push a no-op. The real first push is RKB's, from a
terminal so the credential manager can take the token.

## 2026-09-10 — first pull from Overleaf by git; RKB's table edits moved into the builders

**The pull.** `overleaf.py pull paper` brought back RKB's online pass on eight prose files (the
endogenous-theta section drops the sequential/leaded vocabulary for contemporaneous / one period in
advance; the Argentina savings effect reads 1.8% rather than 1.9%; a deadweight-cost sentence gained
13% / 1.5% of raised funds at rho = 0.5 / 2). Eight generated tables had also been edited online and were
refused by the banner check, as designed. Their edits went into the builders instead: shorter notes,
every US table now says "Common-X calibration: see the note to Table X" and only the calibration table
spells the variant out (`config.variantNote(commonX, full)`), and the ESC calibration table gained a
computed f(theta*) column (RKB had typed 0.986 at rho = 2; the value is 0.9865, printed 0.987). Kept
against the online version, on RKB's instruction: `tablenotes` rather than a plain italic Note, and no
manual spacing in header cells. The biblatex switch to `authoryear-comp` was reverted. Two literal
backspace bytes in `config.py` (a heredoc had eaten `\b` in `\bar h` and `\beta`) would have printed
"ar h" and "eta" in the vector-X appendix tables; fixed.

**Paper edits.** The technical documentation is now a bib entry (`BergGE26doc`, @online, URL in the
note field because the paper sets `url = false`) cited in the numerical section and the ESC section's
opening footnote. The calibration table's omega row prints the three tax targets as
`tau^{US} = 14.4%` etc. instead of "Social security tax rates".

**Endogenous-theta section, the co-author's three questions.** "The forward-looking channel the data
narrative is about", "the fixed point moves with it", "static in the design state" and "a cheaper path
iteration" were all compressions of `num_esc.tex`; rewritten in plain terms. Two errors found on the
way: RKB's online edit had turned "provably independent" into "probably independent", and "the tables
below use the most accurate method" was wrong — the CRRA tables come from the path iteration, certified
against the exact 2-D recursion, not from the recursion. Now stated as such.

**Exact-solver question.** Assessed from the recorded timings (~12 min per 2-D solve at ns = 150, ~3x
less at ns = 50; the path iteration 2 min per sweep, the p scan 15–17 min per rho): an everything-exact
CRRA leg is ~1.5–5 h of compute plus half a day for an `--exact` branch the driver does not have, and
changes the design by ~0.002 against a method resolution of ±0.01. Decision: do it once for the final
version, opt-in, not in the default pipeline. Logged as item 7 of `notes/todo_paperRewrite.md`, with
Argentina under common X as item 6. The composite French shocks (income + voting, all three) are
flagged for a cut but deferred: the section's closing paragraphs rest on income + voting.

**Common X against vector X.** `notes/us_commonX_vs_vectorX.md`: the two variants agree to 1e-6 on
every US counterfactual that does not touch eta or X, and differ on two. Income distribution: the
political choice responds to eta^{1+xi}/X^xi, and under vector X the US X_i rise with income (8.0 to
18.5), so holding them while importing France's flatter eta compounds the compression (composite
top/bottom 2.5 against 2.9 under common X) — a larger tax cut and a smaller hours rise. Leisure:
Xbar_FR/Xbar_US is 1.76 under common X and 1.52 under vector X because the vector X_i also carry each
country's relative-hours profile; both overshoot the observed 4.0-hour gap (6.2 and 4.7 h at rho = 1).
Recommendation, argued in the note: common X stays the headline (relative hours are a prediction, the
inequality counterfactual isolates eta, one parameter one target), vector X stays the appendix twin.

**Overleaf.** First push by git, `--force` once as the docstring foresees; RKB's three newer eps figures
were copied local first so the push could not delete or roll them back. Overleaf matches the folder.
