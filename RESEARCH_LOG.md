# Research log

Cross-cutting/structural session log. For model-specific work, see `python/<module>/RESEARCH_LOG.md`.

## 2026-07-10 — repo conventions established
- Reviewed `CLAUDE.md`, `informalAnalytical`'s three `.py` files, and the tex documentation (then a single
  `writing/informalAnalytical_docs.tex`, since split into `writing/informalAnalytical/`).
- **The documentation convention this repo runs on:** each `python/<module>/` folder gets its own
  `README.md` (purpose, file map, implementation status) and `RESEARCH_LOG.md` (module-specific session
  log); this root log is reserved for cross-cutting/structural sessions. Written into `CLAUDE.md`, and the
  root `README.md` expanded into a repo map.

## 2026-08-05 — logging cadence, and a docstring-density convention
- **Log cadence.** `RESEARCH_LOG.md`/`README.md` updates happen once, at the end of a working session when
  the user signals it — not after every interaction. The prior per-interaction habit had gotten noisy.
- **Docstring density (`CLAUDE.md`).** Keep equation cross-references, shape conventions and genuine
  gotchas; cut narration of design history, rejected alternatives and inspiration comparisons — that
  belongs here. Applied as a sweep across `informalAnalytical`'s three files; `gridsearch/*.py` was already
  at that density. Verified behavior-neutral via the full suite before and after.
- Two workflow habits saved as feedback memories rather than `CLAUDE.md`, since they are about how I work
  rather than project convention: write verification checks directly into the real test file instead of a
  throwaway scratchpad first; prefer `Grep` + a narrow `Read` over re-reading a whole large file.

## 2026-08-06 — the same sweep, one session later
Applied at the end of the calibration-implementation session (work itself in
`python/informalAnalytical/RESEARCH_LOG.md`). Trimmed the new `model.py` §8/`base.py` §10 docstrings to the
house density; condensed `informalAnalytical/RESEARCH_LOG.md`'s older entries (~190 → ~65 lines) to fact +
gotcha. **Kept every bug and trap** (the `β>1` cap, the overflow fix, the non-integer-index fix) — those are
exactly what a future session would otherwise silently re-trigger. That split is the template for every
condensation since, this one included.

## 2026-08-10 — a copied bug, and the test class that would have caught it
A latent bug in `base.py`'s `hRatio` was found in `InformalSavings` and turned out to be present in
`informalAnalytical` too, because the file had been copied. Details in the two module logs; the
cross-cutting points:
- **Copying a module copies its blind spots.** `InformalSavings` inherited both the bug and the absence of
  the test that would have exposed it. When a new module starts as a copy, the *tests* it does not have are
  as inherited as the code it does.
- **Both test suites targeted the FOC/policy machinery only.** Nothing asserted the model's own primitive
  conditions — that reported consumption equals income minus savings, that the PAYG budget balances, that
  `∑γ_iη_ih_i = h`. Those identities are cheap, independent of the solution method, and caught in one run
  what four test files and a working calibration had not. Each module now has a `test_ee.py`; `US` should
  get one **before** it gets a solver.
- **Naming as a correctness concern.** The bug was possible because a method's name and docstring described
  a different quantity than its body computed, and five call sites split three-to-two on which they wanted.
  The fix was to name both quantities and let the call sites say which they mean.

Also: `InformalSavings`' economic equilibrium implemented and `writing/informalSavings/`'s numerical
sections written. That doc set is now self-contained — it no longer refers to the analytical variant — so
the two model documents read independently, which is the convention to hold to for `US` as well.

## 2026-08-10 (cont'd) — the docs are downstream of the code, and the loop needs closing explicitly
`InformalSavings.policy` was implemented from `num_peeLOG.tex`/`num_peeCRRA.tex` as the spec. Six of the
specs' numerical prescriptions turned out wrong or incomplete once measured; the `.tex` files were edited at
the end of the session to state what the code does.

**Derivations transfer; numerical folklore does not.** Every structural result the docs derived — the state
dropping out of the LOG fixed point, the rank-one decomposition, the exact unnesting of the two CRRA states
— held exactly and shaped the implementation. What failed on contact was the *numerical* advice layered on
top: grid bounds read off a steady state, a smoothing recommendation applied to the wrong object, a
refinement rule that made things worse. Expect that split: write the second kind provisionally and measure
it before believing it.

**Deviations need somewhere to live between discovery and reconciliation.** They accumulated as
`notes/informalSavings_numericalDeviations.md`, recording per item what the doc said, what the code does,
and the measurement justifying the difference. That made the eventual `.tex` edit mechanical — no number
had to be re-derived. Worth repeating for `US`: a deviations note per model, folded into the docs at the end
of a session rather than in the middle of one.

**A mistake worth not repeating.** One deviation was written up with a confidently wrong mechanism, caught
only because putting it into the paper prompted an isolated measurement. The original data had already
contradicted the story — the error was non-monotone in the refinement — and had been read past, because the
story was plausible and the measurement had two variables moving at once. **A mechanism claimed in the
paper needs a measurement that varies one thing, and a non-monotonicity is a fact to explain, never noise
to average over.** This is the class of error a reader cannot catch: the prose looks reasonable and the
number attached to it is real.

## 2026-08-10 (cont'd) — reuse that is silently approximation
`InformalSavings`' path solve was implemented. Three points generalise.

**A clip that manufactures a bracket also manufactures a root** — `notes/crossCuttingFindings.md` #2.
Applies wherever a fixed point is closed through a bounded policy, in `US` as much as here.

**"Reuse" and "approximation" can be the same line of code.** Two bugs this session were mirror images: a
bound reused as a bracket, and a solved policy surface reused as a state transition. In both cases the
reused object was genuinely already computed, genuinely correct, genuinely the right type — and using it
still replaced an exact evaluation with an approximate one. The tell in both was that the *doc* named a
different object than the code reached for. **When a later section consumes an earlier section's output,
check whether the derivation asked for that output or for something the output happens to be interpolable
into.**

**A luck-dependent bug is a reason to test both cases first.** The bracket bug was invisible under LOG and
fatal under CRRA, differing only in the sign of an extrapolation. The log case was implemented first,
"worked", and supplied false confidence. Where two preference cases share a code path, exercise the harder
one before trusting the easier one — the copied-module blind spot above, one level down.

## 2026-08-11 — two cross-cutting lessons from the `InformalSavings` calibration
Session work is in `python/InformalSavings/RESEARCH_LOG.md` and `python/gridsearch/RESEARCH_LOG.md`. Two
things generalise and are written up in `notes/crossCuttingFindings.md` (#1 bitwise reproducibility, #3
converged-but-wrong nested solves) rather than here. Both belong to the same family as the 2026-08-10
entries: **the failure mode of a nested numerical method is almost never a loud one, and the test that
finds it is usually a comparison the method itself does not make.**

## 2026-08-11 (cont'd) — documentation sweep: write a repeated finding once
User asked for a repo-wide pass: strip comments/docstrings that only restate a README/RESEARCH_LOG, and
where a finding had been written out in full more than once, write it once and reference it.

**Consolidation.** Three findings had each been written out in full three times (root log, a module's
RESEARCH_LOG, that module's README): bitwise reproducibility holding within a process but not across; a
clip manufacturing a bracket and therefore a spurious root; and a nested solve reporting convergence at a
displaced answer, diagnosed by refining the inner grid at fixed outer parameters. `notes/crossCuttingFindings.md`
now holds the general statement plus the concrete numbers for each, and the prior write-ups point at it.
The `ln(1-τ)`-differentiation and interpolant-kink traps were checked for the same pattern but turned out
already correctly layered (gridsearch/README states the general function behaviour once; the module README
states the current convention; the module log points at the deviations note for the numbers) — left alone.

**Docstring trims.** Several section-header block comments in both models' `base.py`/`model.py`/`policy.py`
restated their own README almost verbatim; each is now a one-line pointer plus whatever implementation-only
detail was not there. **Left untouched:** per-method docstrings (equation refs and shapes, not reproduced
anywhere else), and the handful of long docstrings that are the working rationale for a non-obvious choice
sitting on the method that implements it — those are the "genuine gotcha" `CLAUDE.md` says to keep close to
the code, not narration. Verified behavior-neutral (comment-only diffs, suites unchanged).

## 2026-08-11 (cont'd) — `gridsearch` gains a sequencing module
Substance in `python/gridsearch/RESEARCH_LOG.md` and `python/InformalSavings/RESEARCH_LOG.md`.

**Where the parameter-march helper lives.** Calibrating across a grid needs logic (visit order, warm-start
extrapolation, failure recovery) all three model variants will want. Since the model modules are
deliberately self-contained duplicates, the split is: the model-agnostic part is
`gridsearch/continuation.py`, which never touches a `db`; each model gets a thin `calibrateGrid` adapter
that knows what a calibration is. This is the first module in `gridsearch` about *sequencing* grid searches
rather than performing one — it stretches the package's stated purpose slightly, and the justification is
that the alternative was three copies.

**A trap that will recur in the other variants.** `InformalSavings` found its CRRA calibration limited by
the *kind* of its continuation interpolants (piecewise-linear kinks leaving the outer residual only
piecewise `C¹`), not by grid resolution. The diagnostic is the refinement trend at a converged point:
**shrinking means grid-limited, growing means the answer is not grid-converged at all.** That extends
`notes/crossCuttingFindings.md` #3 to catch a *solver* that cannot descend, with the interpolant rather
than the grid as the fix. `informalAnalytical` uses the same piecewise-linear interpolants and has never
been checked for this.

**A methodological point worth stating once, repo-wide.** Two interpolation schemes cannot be compared by
evaluating both at a fixed point that one of them converged to — that measures how far the other scheme's
root has moved, not which scheme is better, and it made the better scheme look worse on the first attempt.
Compare by re-solving under each and comparing refinement behaviour. Same for grids, tolerances, and any
other setting that moves the located solution.

## 2026-08-19 — a third cause for "the outer solver stalls", and a Windows output trap

**`crossCuttingFindings.md` gains #5.** Findings #3 and #4 already described an outer solve that plateaus
while every inner solve looks fine, with two different causes (a displaced answer; a piecewise-linear
interpolant). `InformalSavings` turned up a third with the same presentation and a different fix again: a
**library routine choosing an integer from the data** inside the residual — here `UnivariateSpline`'s
FITPACK knot count, but equally adaptive quadrature, an `argmax` over candidates, or a root-count branch.
The residual then has jumps, and a root falling inside one does not exist in the discretized problem, so no
warm start, step size or refinement reaches it.

Recorded there rather than in the module because the diagnostic recipe is model-agnostic — scan the
residual finely at a *converged* point and look at successive differences against their median; a
finite-difference step that disagrees with both a smaller and a larger one is straddling a jump; aggregate
counters will not find it, per-period array diffs will. And because it generalises into a design rule the
whole repo should follow: anything inside a differentiated residual should be a linear map of its input for
fixed structure, or have its structural choice pinned from outside. That rule is also the argument against
auto-tuning grids or bounds from a previous run — it makes the residual depend on solve history, which is
the same defect wearing different clothes.

Details in `notes/informalSavings_rho07_resolved.md`; `informalAnalytical` shares `gridsearch.interp` and
has **not** been checked for this (same status as #4).

**A Windows trap that cost two aborted runs.** Every module's test files and sweep scripts print Greek
parameter names. When stdout is a console this is fine; when it is a pipe or a log file, Python on Windows
defaults to the ANSI codepage and the first `β` raises `UnicodeEncodeError`. In `calibrateRhoGrid.py` this
surfaced as `marchGrid` reporting "the anchor value 1.0 failed to solve" — a genuine-looking numerical
failure with a purely clerical cause. Fixed there by reconfiguring encoding alongside the line buffering it
already set. The test files still had it at the time of writing — **closed 2026-08-20**, see that entry.

## 2026-08-19 (cont'd) — re-deriving what was built on a defect; and a shock-experiment pattern

**`crossCuttingFindings.md` gains #6**, the companion to #5. Having found the smoother's knot flips, the
follow-on question was what had been adopted to work around them. Two settings in `InformalSavings` had
been, both correctly measured at the time and both citing a *symptom* rather than a mechanism in their
justification. Re-derived, they did not fall the same way: one was removed outright, the other survived
with an argument an order of magnitude weaker than the one that established it. That asymmetry is the
finding — it is not predictable from the original measurement, so the settings have to be re-derived
rather than reasoned about, and the practical test for which ones are at risk is whether their recorded
justification names a symptom or a mechanism.

Recorded there rather than in the module because it is a maintenance rule about how findings age, not a
numerical one, and because it argues for something the whole repo does: recording the *measurement* behind
each setting, not only its value. Without that, the list of things to re-derive cannot be reconstructed.
#6 also picks up a diagnostic-design point worth generalising — a summary statistic that cannot come out
both ways on the data it will see is worse than no statistic, since it invites reading the label instead
of the numbers.

**A shock-experiment pattern that generalises past this model.** `InformalSavings` gained an unanticipated
reform experiment (`shockUniversal.py`): baseline solve → read the state entering `t0` → build the model
copy restricted to `t0..T` → change the policy parameter → re-solve from that state. The mechanism
(`createCopyFromt0`/`stateAtT0`) is shared verbatim with `informalAnalytical`, so the experiment layer will
transfer too. Two lessons from building it that are not specific to `ε`:

- **Changing a parameter is not the same as passing it.** Aggregates derived from a parameter and cached
  in `db` — here `κ(ε_{t+1})` — are read by every equation as givens, so a call that passes a new path but
  leaves the cache alone solves a mutually inconsistent model *without violating any equilibrium
  condition*. Nothing detects it. Any experiment that varies a parameter has to rewrite the derived cache
  with it, and both modules' `paramsFromFuncs` machinery makes this easy to forget rather than easy to do.
- **Restriction is not recomputation at the boundary.** `_sliceDb` restricts lagged entries, so the copy
  inherits genuine pre-`t0` values — correct under no shock, stale under one, wherever a lagged object
  depends on the changed parameter. Both modules' copies have this shape.

Also worth carrying: an experiment is best written with **two readings of the same reform** when the
definition is a modelling choice rather than a datum. Here "universal" admitted two, and they turned out
to bracket the status quo rather than differing in degree, so every response reversed sign. One reading
would have looked like a result.

## 2026-08-19 (cont'd) — a fix applied where a defect was found rather than where it applied

`InformalSavings`' `ρ=1` boundary artifact turned out to be `crossCuttingFindings.md` #4 recurring in the
one place nobody looked. Module detail is in `python/InformalSavings/RESEARCH_LOG.md`; the full chain is
`notes/informalSavings_logCrraBoundary.md`. Recorded repo-wide as **#7** because two parts generalise.

**Keying a fix by configuration leaves the configurations that did not surface it.** `interpKind='cubic'`
was adopted against #4 and keyed to `'CRRA'`, since that is where the calibration had stalled. LOG kept
`'linear'`, so the single LOG point of every sweep ran the interpolant the module had already concluded
was inadequate — and the `verify` refinement check was keyed the same way, so that point is also the only
one with `verifyResidual = NaN`. The configuration still carrying the defect was the one exempt from the
check for it. The distinction to write down when keying anything: a **resolution** choice may legitimately
differ per solver, a **well-posedness** choice may not. This repo had already drawn exactly that line for
`smoothKnots` and then keyed `interpKind`, which is the same kind of choice, anyway.

**A tighter residual can be the wrong answer, more precisely located.** The defective configuration
converged *better* than the fixed one (1.6e-11 against 1.1e-9) and hit its calibration targets exactly,
because a target was being fitted at one realisation of a jittering solve. No local diagnostic separates
those. What did was computing the same object a second way and reading the two as a **series**: a fine
grid straddling the boundary, and second differences, which for one displaced point read `[+d, −2d, +d]`
exactly — reproduced on two grids ten-fold apart in spacing. Worth reaching for whenever two methods meet
at a parameter value, which in this repo is every `ρ=1`.

Also carried into #7: subtract the trend before reading a gap between two methods. The raw difference is
dominated by the true slope in the parameter and looks like a large artifact; the central average
`½[x(1+δ)+x(1−δ)] − x(1)` cancels it and is what actually exposes the jump.

## 2026-08-20 — the boundary fix kept; scoping a re-run to what a change can reach

`InformalSavings`' `ρ=1` interpolant fix was applied (module log and
`notes/informalSavings_logCrraBoundary.md` have the substance). Two process points generalise, and a third
finding was added to `notes/crossCuttingFindings.md`.

**Repair a keying mistake where it was keyed.** The obvious fix — correct `policy.LOG._gridSettings`'
`interpKind` default — is wrong here, because `CRRA` *inherits* that key, so it moves both solvers'
defaults and trips two suites whose assertions were themselves measured under the old value. The defect
was introduced at a call site that keyed a well-posedness setting by solver, and that call site is where it
belongs. Generally: the default may have other consumers, and tests written against it are evidence about
the default, not about the bug. Recorded as part of #7.

**Ask what a change can reach before re-running the pipeline.** A full 16-point sweep was launched to
refresh the results and the user stopped it with the right question: if the fix only changed what is passed
to the LOG solver, why re-solve the CRRA points? It did not need to. The solver selection is `ρ==1`
exactly, so exactly one row's residual function changed; the rest keep their own, and a warm start moves
the path to a root rather than the root — verified at 8 CRRA points, which returned the published
parameters to 6 significant figures. `calibrateRhoGrid.py`'s resume path already supported the targeted
patch (drop the row, re-run without `--force`): **30 s against ~2.5 h**, one row of sixteen changed. The
machinery to exploit a small blast radius existed and went unused because the blast radius was never
estimated. Worth doing explicitly whenever an expensive pipeline is re-run after a fix.

**`crossCuttingFindings.md` gains #8**, from a backup taken in place that became a datapoint: a superseded
CSV left beside the live ones matched a plotter's glob and, because the loader read the key from the file's
own column rather than its name, contributed a well-formed extra point that was published in a figure. It
is the third instance of one shape in this repo — with a stale default filename and a declared-but-unfilled
schema column — and the common defect is a **pipeline trusting the shape of its inputs rather than their
provenance**. The habit is a subdirectory for superseded runs, anchored filename matching, and a duplicate
key raising rather than being resolved silently.

*Also worth carrying*: the figure and the prose beside it disagreed, and only the figure was wrong, because
the analysis behind the prose had excluded the stale file explicitly while the plotter had not. Two readers
of the same directory with different filters is a standing invitation to that. One loader, one filter.

## 2026-08-20 (cont'd) — documentation and test-scaffolding cleanup

User asked for a consolidation pass over the READMEs, research logs, tests, and the loose log files that
had accumulated at the repo root. Docs-and-scaffolding only; no numerical behaviour was changed, and the
14 fast suites plus both `test_calibration.py` suites were run before and after.

**A shared test harness, which closed a trap the repo had documented and then lived with.** All 16 test
files re-declared the same six-line `ok`/`check()` block, with formatting drift between them and four
different final-verdict spellings — and **none reconfigured stdout**, so the cp1252 trap recorded in this
log on 2026-08-19 was live in every one of them. Both problems have one fix:
`gridsearch/testing.py` provides `check`/`report`/`utf8Stdout` and reconfigures the streams on import.
Verified under `PYTHONLEGACYWINDOWSSTDIO=1` with output redirected — the exact condition that used to
break — rather than only under a console.

It lives in `gridsearch` because that is the only importable package (`pyproject.toml` declares
`packages = ["gridsearch"]`; the model folders carry `__init__.py` but are not packages). It is not
re-exported by `__init__.py` and is not part of the numerical API. The alternative — a `python/testkit.py`
the model tests reach by parent-directory `sys.path` surgery — was worse for a module every test imports.

*Worth carrying:* the trap had been correctly diagnosed, written into two READMEs and this log, given a
workaround (`PYTHONIOENCODING=utf-8`), and left in place with the note "worth fixing at the source if
anyone touches them". The workaround is what kept it alive: it made every individual encounter cheap
enough not to fix, while the cost of forgetting it stayed a whole aborted run. **A documented workaround
for a one-line fix is a decision to keep paying, and it should be re-read as one.**

**`python/runTests.py`.** No way to run the suites as a set existed; each was launched by hand from a path
in a README. The runner registers all 17, classifies them fast/slow by wall time (14 fast, ~70 s total;
three slow, ~1 h), and runs each as a **subprocess** — the model suites mutate their instance's `db` and
snapshot/restore it in a `finally`, so they would collide in one process. `--list`/`-k`/`--all` select.
The classification is wall time, not importance: the slow three are the ones that actually pin the
published parameters.

*A defect the runner surfaced immediately:* `gridsearch/test_roots1d.py` printed its verdict but never
called `sys.exit`, so it had always exited 0 — a failing run would have reported success to anything
checking the exit code. Nothing had ever checked, which is why it survived. Uniform `report()` fixes it
everywhere at once.

**Check counts were stale in three READMEs**, by one to two each (e.g. `test_peeLOG.py` documented as 51
and running 52). They had been counted by hand or by grepping call sites, and loop-expanded assertions do
not match either. `report()` now prints `(n passed, m failed)`, so the number in a README is a quantity
that can be read off a run instead of maintained.

**Condensation, on the 2026-08-06 template** (fact + gotcha; keep every bug, trap and measurement; drop
verification narration and process chronology). Root log 320 → 277 lines, `InformalSavings` 756 → 606,
`gridsearch` 246 → 218. `informalAnalytical`'s was already condensed in 2026-08-06 and was left alone.
Two entries needed more than compression because they had been **overtaken**: 2026-08-12's `ρ=0.7`
diagnosis, whose conclusion 2026-08-19 overturned, now says so in its heading and keeps only what
survives — the ladder's negative results, and the two habits that produced the misattribution (a probe run
at an off-root point, and a recorded caveat that was not acted on). A superseded entry that does not
announce itself is worse than a long one.

**READMEs.** `InformalSavings/README.md`'s two "Results:" sections had grown into full narrative
duplicates of this log and the notes files; trimmed to the live file, the headline numbers, the
superseded-file list, and pointers (561 → 527 lines, with the `Δτ` dip moved from "open" to resolved).
Repeated per-file boilerplate ("Exits nonzero on failure", printed 16 times across three READMEs) is now
one sentence at the top of each Files section. Stale paths fixed repo-wide: `writing/informalAnalytical_docs.tex`
had been split into `writing/informalAnalytical/` but was still cited in `gridsearch/README.md` (×2),
`informalAnalytical/README.md`, `informalAnalytical/base.py` and this log; `US/README.md` pointed at a
`writing/US_docs.tex` that will never exist.

**Four loose `.txt` run logs deleted from the repo root** (`jac_rho07_log.txt`, `rho07_attempt_log.txt`,
`results_sweep_log*.txt`) — raw stdout from the superseded 2026-08-12 `ρ=0.7` failure, referenced by
nothing, and fully superseded by `notes/informalSavings_rho07_resolved.md`. The root `README.md` now says
run logs belong in `results/`, which is where every log written since 2026-08-19 already goes.

## 2026-08-21 — a paper pipeline: three stages, and a normalisation mistaken for a result

`writing/Paper`'s tables and figures had been hand-maintained while the code moved underneath them. The
session built `python/paper/` to generate them. **This is the repo's fifth `python/` folder and the first
that is neither a model nor a numerical package**, so `CLAUDE.md`'s "four folders" sentence and the root
`README.md` map both changed; `CLAUDE.md` gained a "Paper outputs" subsection stating the three stages and
the rule that a generated `.tex` is never hand-edited.

**The three stages, and why they are separate entry points.** `runCalibration.py` → `runShocks.py` →
`build.py`. The split was the user's, and the load-bearing part of it is that **stage (iii) imports no
model code and unpickles nothing** — it reads csv, writes tex and pdf, and takes seconds. That is what
makes it safe to re-run after every edit to a caption or a rounding rule, and it is why the expensive
stages are separate commands rather than a `--refresh` flag on the builder: a paper rebuild can never
silently become a 2.5-hour solve. Every stage skips work whose output exists, so the sequence is
idempotent and costs seconds when nothing changed.

The corollary, enforced rather than hoped for: **an output whose inputs are missing is reported and
skipped, never partially written.** An experiment that has not been run must not be able to look like a
table that has. `datasets.MissingInput` is the one mechanism; `build.py --list` reports buildability
without doing anything.

Stages (i) and (ii) are *declarations*, not implementations — the experiment scripts keep their own CLIs
and do the work. Their value is that the settings the published numbers were produced at are now a file
(`config.py`) rather than shell history.

**A free normalisation reported as a result — the session's real mistake.** The paper reports an average
workweek; the model's aggregate `h` has no scale. I converted with `h·(7·12)`, inverting `test.py`'s
`pars['h0'] = workweek/(7·12)`. But that is how the **pre-determined** period's hours enter as a model
*input*; it is not a scale the solved `h_t` inherits. The correct treatment is a **normalisation against a
reference point**: the calibrated baseline's `h` at the calibration year *is* the observed 42.54 hours, per
`ρ`, and every other `h` reports as `42.54·h/hRef`.

What makes this worth recording is not the wrong formula but what it produced. The baseline came out at
44.22 instead of 42.54, and `h` varied across `ρ` where `τ` and the savings rate did not — and I wrote
that spread into a table note and into a README as a *finding* ("h is not a calibration target, so it
differs across ρ"), complete with a plausible mechanism. It was an artifact of dividing by a constant
instead of by each `ρ`'s own baseline. **A quantity with no scale cannot have a cross-run spread that
means anything; that the explanation was available is what made it convincing.** The guard now is
structural: `config.workweekHours(h, hRef)` takes the reference as a required argument, so the conversion
cannot be written without naming what it is relative to.

*Related, and stated by the user:* the paper's current numbers come from a different codebase. Differences
against it are two code generations being compared, not errors being corrected — the question they raise
is which version the paper reports, not a defect to chase. I had called them "stale" more than once.

**Two independent routes to one number, and the disagreement they caught.** The savings rate needs
`s_{t0-1}`, a *state* entering the reform year that no shock csv carries as a row. `datasets.seedSavings`
recovers it two ways — from the new `shockEEOnly.py`'s `s__base`, and by inverting eq (calibration) at
`t0`, where the baseline savings rate is a target and so is known — and raises if they disagree. It fired
immediately, on **my** bug: `runCalibration.py` was writing vector fields to csv as a python repr, and
under numpy 2 the repr of a list of `np.float64` is `np.float64(1.64…)`, out of whose literal text a
number-scraping reader mines a spurious `64.0`. Now JSON on both sides. *Worth carrying:* the check was
written for a stale-experiment scenario and caught a serialisation defect instead — a cross-check pays out
in the case it was not designed for, which is the argument for writing it at all.

**Parallel agents against a fixed output contract.** The two missing experiments were built concurrently
(model-specific findings in `python/InformalSavings/RESEARCH_LOG.md`, including a proxy-state defect one
of them found in the *existing* results). What made that work was fixing the csv schemas before either
started, and scoping each agent to a new file so no shared file had two writers — READMEs and logs
explicitly excluded and written afterwards from their reports. The one contract gap (`s_{t0-1}` had no
home in any schema) surfaced while writing the builders and was patched by messaging the running agent
rather than by a follow-up pass.

**`writing/Paper` is not tracked by git**, so overwriting a hand-written table is unrecoverable. `build.py`
copies any file lacking its `%% GENERATED` banner to `results/paper/superseded/` before the first
overwrite, and detects its own banner afterwards so a second run cannot overwrite the true original with a
generated one. Same principle as `notes/crossCuttingFindings.md` #8, applied to a directory git is not
watching.

**Status.** Five Argentina outputs wired and built (three tables, two figures). The 14 US/UK/FR tables and
two figures cannot start until `python/US/` exists; `build.py` only ever writes files in its own registry,
so the hand-written versions are untouched.

## 2026-08-21 — a module documented before it was coded; and an open question in the findings note, closed

The `US` module went from empty to documented, implemented, tested and swept in one session (module log:
`python/US/RESEARCH_LOG.md`). Four points are cross-cutting rather than about that model.

**Docs first is worth repeating.** Every other module here was documented after the fact. This one was
derived in tex before any code existed, and two structural results fell out of the derivation rather than
out of debugging: that removing the informal household makes the LOG first-order condition decouple across
time (so the PEE path is `T` independent scalar problems, not a backward recursion), and that `η`/`X` carry
*two* independent invariances rather than one. Both then shaped the code and became tests. Neither would
plausibly have been noticed by porting the parent module and running it — it works either way, just with a
vacuous recursion and an unexamined normalisation.

**The two-invariance distinction closes the loop on the previous entry's mistake.** That entry records
reporting an artifact of a free normalisation as a finding, and fixing it by requiring a reference point.
The reason the level of `h` was slippery is now precise: with `y^η = η^{1+ξ}/X^ξ` and `y^x = (η/X)^ξ`,
every aggregate uses `y^η` alone, so the model has a *scale* (moves levels) and, separately, an *hours
unit* (moves individual hours and the workweek and nothing else, aggregate `h` included). A workweek is
comparable only to the unweighted average `h̄`, never to the productivity-weighted aggregate `h` — and
`h` cannot be used to pin the hours unit even in principle, because it does not respond to it. The general
rule: **before treating a level as a result, find the transformations the model is invariant under and
check which one it moves under.** There can be more than one, and they need not act on the same objects.

**`notes/crossCuttingFindings.md` #4's closing sentence is now answered, and the answer was #5.** That
note ended "`informalAnalytical` uses the same piecewise-linear interpolants and has not been checked for
this." The check finally happened, on `US` (same lineage), and the binding defect was #5's adaptive knot
count, not #4's interpolant kind. #4's own fix was tested and **not** adopted: `cubic` fails to converge in
2 of 8 measured cells, and `pchip` — affordable here, since every interpolant in this module is 1-D and the
1400× cost that blocked it is a 2-D problem — agrees with linear once resolved but fails on coarse grids.
Note updated in place. Two transferable lessons:

- **Judge a refinement study by the trend, not the spread.** The converging setting had the *wider* range
  of answers (a monotone sequence spans more than a jittering band does), so a spread-of-answers metric
  ranked it worse and nearly got it dismissed. This sharpens #3: the diagnostic is the *shape* of the
  sequence, and "small spread" is not evidence of anything.
- **A band with no trend is the absence of information, not a small error bar.** The adaptive smoother was
  not avoiding the coarse-grid error, it was masking it — every node count landed inside one 0.3% band, so
  refinement could never reveal that the coarsest was 2.4% off.

**A constant that was safe by parameter values rather than by construction.** The CRRA steady state
inherited a hard-coded search bracket `(1e-6, 0.75)`. The feasibility limit it stands in for scales with
`α/(1-α)` and `κ/p`, both of which move between modules; at US parameters the limit drops below the
constant and the solver died on a NaN, reporting a solver problem rather than an infeasible interval. This
is #7's shape with a twist worth naming separately: #7 is about a fix keyed to where a defect was *found*,
whereas here the constant was never keyed to anything — it was correct once, silently, and travelled with
a file copy. **When a copied module changes a structural parameter, every hard-coded bound in it is a
hypothesis that needs re-testing**, and the fix is to derive the bound from the model rather than to retune
the number, which would only move the point at which it reappears.

## 2026-08-22 — the US/France/UK arm reaches the paper; a second pipeline arm

Structural, repo-level notes from the session. The model-specific record is in
`python/US/RESEARCH_LOG.md`; the pipeline's is in `python/paper/RESEARCH_LOG.md`.

**`python/paper/` now has two model arms.** Argentina and US/France/UK have separate stage (i) and (ii)
entry points (`runCalibration.py`/`runCalibrationUS.py`, `runShocks.py`/`runShocksUS.py`) and share
`config.py`, `results/`, and one stage (iii) (`build.py`). The split is by *delegation target*, not by
model: the two arms hand off to experiment scripts with different CLIs, and those files exist to record
the settings the published numbers were produced at. A single entry point carrying both flag vocabularies
would have made that record harder to read, which is the one thing it must not be. Stage (iii) stays
shared because it is model-agnostic by construction — it reads csv and writes tex, imports no model code
and unpickles nothing. 17 outputs, ~5 s.

**A new cross-cutting finding, #9: a derived parameter silently undoes any experiment that sets it.**
`shocks.shockTheta` wrote `db['θ']` and then called `updateAuxPars()`, which re-derives everything in
`paramsFromFuncs` — including `θ` — from the replacement-rate data. Both `θ = 0` and `θ = 1` returned the
calibrated path to every printed digit. What makes this class worth a numbered finding is that **the null
result is plausible**: a counterfactual that comes back at the baseline reads as "this characteristic does
not matter", which is exactly the kind of conclusion these experiments exist to produce. The absence of an
effect is not self-evidently a bug the way a NaN is. The habit that catches it is cheap — assert that two
*polar* scenarios differ from each other, not just from the baseline.

**A convention that had to be recovered rather than read off.** The paper's "savings rate" is `s/(w·h)`,
savings over gross labour income, not `Base.savingsRate`'s `s/Y`; they differ by exactly `(1-α)`. Nothing
in the code or the docs said so — it was found by noticing that `0.15374/0.7 = 0.21962` against the
table's 21.96%. Recorded in `python/US/shocks.py` and both READMEs. Worth flagging as a repo-level habit:
where a published number and a computed one differ by a clean factor, check the definition before
checking the model.

**Correction to something I had written in the `US` README.** I described the level of `Γ_h` as arbitrary.
It is not. It is a *normalisation* under `ModelUS`, where nothing pins the level of hours; under
`ModelFR` the hours target pins it, so it comes out data-determined. And in neither case is it irrelevant
— it sets the level of `h`, `s`, `c`, `Y`, and is unidentified only jointly with TFP, which `base.py`
normalises to `A = 1`. The distinction earned its keep immediately: the λ-is-an-increment bug in
`ModelFR.calibrate` was findable only because `Γ_h`'s level is a result worth checking.

**Data.** `data/` gained `FRMain.xlsx` and `UKMain.xlsx`. Neither carries a `30y interest` column — `R` is
not a target for those countries — so `testEU.load` sets `db['R0'] = NaN` deliberately rather than leaving
`ModelUS`'s default 2.443 in place, and `_checkConverged`'s `not (maxResid <= tol)` makes a stray
`ModelUS.calibrate` on one of those workbooks fail loudly instead of quietly targeting the US rate. Same
shape as `getEps` raising on `γ_0 > 0`: a plausible-looking inherited number is worse than an absent one.

**Test count.** 21 fast suites (~75 s), up from 19: `US/test_fr.py` (the `ModelFR` protocol, data-free by
construction), `US/test_eu.py` (the FR/UK workbooks end to end) and `US/test_createCopyFromt0.py` (the
shock machinery, which the `US` README had flagged as inherited-and-untested).

## 2026-08-24 — endogenous `θ`: what belongs here rather than in the module log

The substance of this work is `US`-specific and lives in `python/US/RESEARCH_LOG.md`. Three things are
cross-cutting enough to record at the root.

**Two new entries in `notes/crossCuttingFindings.md`.** #10, *a corner makes any sensitivity check
vacuous* — a test measuring `dθ_{t+2}/dθ_{t+1}` passed with `+0.0000` because the parameter it reused put
the choice on a boundary, while the production run at the same `ρ` gave `−0.0092`; the vacuous answer was
the more reassuring one, which is why it survived review. And #11, *maximising over a policy that also
enters a predetermined state* — `base.dlnc2i_dτ`'s existing warning, written for `τ`, turns out to apply
verbatim to any instrument reaching the same state, and the permanent choice of `θ` is one. Worth 0.14 in
the answer.

Both are the same species as #3–#9: not bugs in an algorithm, but ways for a defensible-looking number to
be the wrong number.

**A structural result that changes how the docs should read.** Under log preferences the political
objective is additively separable, `W_t = A(τ_t, θ_t) + B(θ_{t+1})`, so the leaded choice of `θ` has **no
state at all** — not a weak dependence on the inherited design, an exactly zero one, measured across the
whole state grid. The appendix sets that problem up with `θ_t` as a state; it is one for the tax and not
for the design. Documented as a proposition in `writing/US/model_esc.tex` rather than left as a numerical
curiosity, because it is what makes the solver a sequence problem instead of a recursion.

**Documentation convention held.** The new material split model-side (`writing/US/model_esc.tex`: the cost,
the three timings, two propositions) from numerical (`writing/US/num_esc.tex`: algorithms, calibration,
verification), matching every other section of the module rather than accumulating in one file. Equation
labels follow the `\refeq:esc:*` pattern and the `.py` docstrings reference them by name, so the usual
rename discipline applies.

**Test count.** 22 fast suites (~75 s) plus a new slow one: `US/test_esc.py` (28 checks — the wedge against
the appendix's own closed forms, the three structural properties, both timings) and `US/test_escCRRA.py`
(slow, ~4 min: the CRRA solver against its log limit).

## 2026-08-24 (cont.) — the ESC leg reaches the paper; a csv-write convention; a tooling trap

The day's substance is in the module logs (`python/US/RESEARCH_LOG.md`: the exact 2-D CRRA solver and
the counterfactuals across ρ; `python/paper/RESEARCH_LOG.md`: the pipeline wiring and the appendix
rewrite). Three things are structural enough for the root.

**Endogenous θ now runs through all three pipeline stages**, spanning `python/US` (drivers +
`collectESCexperiments.py`), `python/paper` (declarations in stages i/ii, five builders in stage iii),
and `writing/Paper` (the rewritten `Appendix/EndogenousSystemCharacteristics.tex` plus five generated
`US_ESC_*` tables). Nothing in `writing/Paper` remains unwired. The appendix defers derivations to the
`writing/` docs — which formalizes what those docs are for: they are the "online technical
documentation" the paper will cite, so their sections need to stay publishable, not just internal.

**A convention worth naming: incremental drivers must merge into shared csvs, not overwrite them.**
The ESC drivers write one csv from several independent (ρ, spec) runs; a plain `to_csv` after each run
clobbers every row the current run did not produce, which is what forced this session's tagged-file
workaround before `runESC.mergeWrite` (dedupe on the key columns, NaN keys compared equal) replaced it.
The Argentina and US sweep scripts never had this problem because they own resume logic per csv — the
rule generalises as: *any script that writes a csv other invocations of itself also write must read it
back first.*

**A session-tooling trap**: appending python through a quoted bash heredoc halved every `\` — fatal
where a raw string then ended in a lone backslash, and silent where `\hline` became a still-parseable
`\hline` inside emitted tex. Caught only because the syntax error fired first. Emit code that contains
backslashes through Write/Edit, never through a heredoc.

## 2026-08-24 (cont. 2) — the permanent timing's second decision (the entry `notes/todo_escPermanentTiming.md` was owed)

Finding #11 said: do not let a predetermined state move with the instrument being maximised. The
permanent-θ work surfaced a sequel worth its own statement, now `crossCuttingFindings.md` #11b:
**pinning is one decision; *what value* to pin at is a second one, and it can be invisible.** The
predetermined savings ratio was first pinned at the *incumbent* design — justified as an "unanticipated
permanent reform" — but the vote is anticipated: households save at `t0-1` against the design that
*wins*, so the right object is the fixed point `θ* = argmax W(θ; siRatio(θ*))`. What made the wrong
value survive review is that the two readings coincide exactly wherever the choice reproduces the
incumbent design — which is precisely what the wedge calibration targets — so every calibrated number
was identical under both (p to 12 digits) and only the counterfactuals separate them (0.775 vs 0.773 at
p=0.4; 0.542 vs 0.549 at p=0.25). A decision that is a no-op at the calibration point is a decision no
calibration check can catch; it has to be found by asking what the timing *means*, which is the
generalisable lesson.


## 2026-08-24 — a calibration target's units, and where that class of error hides

The Argentina arm targeted a savings rate of 18.4% and calibrated β = 1.212 at ρ=1, which is what
prompted the question. The answer turned out not to be in the solver, the denominator, or the sector
coverage of the datum, but in its **time dimension**, and the generalisable part is where that error was
able to hide.

The model's period is 30 years with capital fully depreciating between periods. So `Y_t` is thirty years
of output, `s_t` is the end-of-period capital *stock*, and the moment `s_t/Y_t` is a stock-to-flow ratio
— `K_{t+1}/Y_t` — not an annual saving rate. An annual national-accounts saving rate is a different and
larger object, because it also replaces the capital that depreciates *inside* the thirty-year window,
which a one-purchase-per-period convention does not have. Feeding one into the other asked the model to
hold about half again as much capital as Argentina has, and β is what gave.

**What let it survive.** The 30-year convention existed only in the documentation; no line of code
mentioned it, so nothing in the model could be inconsistent with it and no test could see it. The
neighbouring target had been converted correctly (pension spending 7.1% of GDP ÷ (1-α) = 0.125), which
made the calibration look internally careful, and the resulting number was not absurd — 18.4% of output
is a plausible saving rate, and the implied K/Y of 4.0 is a plausible capital-output ratio; they simply
were not the same claim. Two plausible readings of one number, and nothing in the repo recording which
was meant. **A convention that lives only in prose is a convention the code cannot be checked against**;
`yearsPerPeriod` is now a model parameter for that reason, and `eq:calibration:KY` carries it explicitly.

Transferable, and now `crossCuttingFindings.md` #12: **for every calibration target, write down the
units of both sides and where the datum came from, in the repo, next to the number.** The workbook
carried `Savings rate = 0.184` with no series id, no vintage and no window; the paper's one-sentence
description of it turned out to be wrong on three counts (private, per-capita, and comparable to the
model's moment). The replacement target is derived by a script (`python/paper/dataTargets.py`) that
writes the value, its window, its source and its retrieval date into `data/`, and writes the alternative
reading beside it — so the next person can see not only what was targeted but what was passed over.
