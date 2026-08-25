# Research log — InformalSavings

Model-specific session log. Repo-wide decisions are in the root `RESEARCH_LOG.md`; recurring findings are
cited by number from `notes/crossCuttingFindings.md`.

## 2026-08-10 — economic equilibrium; the numerical PEE sections written

`base.py`/`model.py`/`policy.py` started as copies of `informalAnalytical` with the type-0 pieces stripped.

**Decisions taken with the user.** The informal return scaler is `χR`, a 1-D parameter over `t`; the copied
`α0`/`χ` are dropped. `χ^R` carries a **period** index — the docs' `χ^R_t` in `ι_t` and `χ^R_{t-1}` in
`c_{2,t}^0` were typos; verified with `χ^R_t = 1+0.1t` (`ι` matches the corrected form to 1.4e-17, differs
from the old text by 2.5e-3), so the convention is tested, not assumed. `l_ι > 0` strictly, which puts
`dυ_{2,t}^0/dτ_t`'s pole outside the evaluation region for every `τ_t` — no masking of the state dimension
needed, and an out-of-grid `ι_t` is reported infeasible, never clipped. The calibration target stays
**formal-only**, so `ι` is a diagnostic rather than something fitted. `χ^R` is not calibrated, and
`χ^R = 1` is a knife-edge, not a neutral default.

**Why the EE needed no change.** Informal savings never enter the formal capital stock, so
`Γs`/`Θh`/`Θs`/`s`/`h`/`si_s`/`κ`/`bbar` are untouched and `ι_t` is a closed-form read-off of the solved
core. Confirmed: `EE_CRRA_solve` at `ρ=1` reproduces `EE_LOG_solve` bitwise for `s`/`h`.

**Trap inherited with the copied file**: the `hRatio`/`hηRatio` bug, found here by `test_ee.py`'s
primitive-budget checks. See the root log.

## 2026-08-10 (cont'd) — `policy.py` (LOG and CRRA), and the docs reconciled to it

**The three doc results were the design, and all three held.** The `ι_t` fixed point is free of the
predetermined state, so the LOG state approximation stays 1-D; the rank-one decomposition reduces the whole
state grid to a broadcast (checked against a pointwise evaluation of the full product, 1.8e-12); the CRRA
unnesting is exact (checked against a nested `brentq`). The only thing `gridsearch` needed was a 2-D
interpolant.

**What the primitive-rebuild test standard bought.** The sharpest checks reconstruct `W_t` from primitives
and finite-difference it rather than comparing against our own output. Machine precision at `t=T`, ~1e-3
absolute at `t<T` — and the test asserts the *implied τ error* against the grid spacing rather than a magic
tolerance, since what matters is that the grid, not the differentiation, limits the answer.

Four numerical findings changed the docs (deviations items 1–4): differentiate in `ln(1-τ_t)`; smoothing
belongs to the policy, not the derivative; the steady-state range is the wrong reference for `𝒮_0`; align
`𝒮_0'`, refine `𝒮'`.

**A methodological note worth keeping.** The `𝒮_0'` finding was first written up with a mechanism that was
**wrong** ("the residual is piecewise linear in `ι_t`"), caught only because writing it into the paper
prompted an isolated measurement. The tell was in the original data — the error was non-monotone in the
node count — and had been read past. A confounded measurement plus a plausible story is exactly what
survives review.

## 2026-08-10 (cont'd) — the path solve; two traps, one in each direction

Solved path: `τ_1 = 0.145` (LOG), `0.153` (`ρ=1.15`), no period at a corner, no state off-grid.

**Trap 1 (#2)**: the first CRRA path started from `s_0 = 2e-11` because `ι_0` reached ~5e3 against
`u_ι = 2` and the extrapolated policy clipped back to `u`, making the residual exactly zero. LOG was fine
only by luck — the same extrapolation undershoots `l`.

**Trap 2, running the other way: the code quietly weakened a derivation.** `eq:forwardSim` writes the
transitions as re-solved at the walked tax; the first implementation read them off the interpolants, which
agree at the nodes and differ between them. Re-solving is ~2 orders better and costs one scalar root per
*period* against one per *node*. Under LOG it also preserves the structural result that `ι_t` is a function
of `τ_t` alone.

The two traps are the same mistake in mirror image: **reuse that is silently approximation** — a bound
reused as a bracket, a solved surface reused as a transition.

Also: `num_peePath.tex` gained what containment in `𝒫_t` can actually be tested (a bounding box contains
it, so failure is conclusive and success is not), and the CRRA-only NaN channel — a path can go undefined
without leaving `𝒮×𝒮_0`, because a 2-D interpolant cannot be restricted to its feasible nodes the way the
1-D ones can.

## 2026-08-11 — the CRRA solve ~11× faster; the calibration run for the first time

**Two exact redundancies removed.** `solvePEE_CRRA` 64 s → 5.7 s, `solvePEE_LOG` 3.1 s → 0.49 s.
`τ_t` reaches `eq:stateApprox` only through `Θ_h`, and both hot callers pass a `(τ,s)` Cartesian product,
so `report_t` evaluated 3.2M rows where 3 600 are distinct — a 900× redundancy, now `_stateApproxSI`. And
`selectMax` looped over 900 state columns when there were 1–2 distinct feasibility patterns: its vectorized
fast path only fired on NaN-free columns, and every column was ragged.

**A negative result that dictated how the refactor was verified** (#1): "identical bitwise against a saved
baseline" is unsound across processes. Done in-process instead: 561 arrays bitwise identical, with the
reference implementation's call counts checked to confirm it was genuinely exercised.

**The calibration converged on the first run** — LOG, 26 evaluations / 16 s to `max|residual| = 2e-10`,
with `ι(t0) = 0.3618` inside `(0,1)` and inside its own state grid, the docs' closing check. (Parameters
superseded twice since; history in `notes/archive/informalSavings_results.md`.)

**Deliberately not done then:** the CRRA default grid stayed `30×30`. Worth knowing for figures: the path's
**first two periods** wobble ~3e-3 at every resolution tested and do not settle monotonically, while
`τ(t0)` converges cleanly — they are the least-resolved part of the path.

A label audit fixed three dangling citations inherited from the copy and, on the doc side, two omitted
arguments, stray `t` subscripts, and `Γ_{h,t}` written transposed in 26 places. **Not re-checked**:
`model_setup.tex` in full, the formal block of `model_competitiveequilibrium.tex`,
`model_finitehorizon.tex`, `num_robustroot.tex`.

## 2026-08-11 (cont'd) — calibration across a grid of `ρ`

**Storage: data, not pickles — decided on evidence.** The model instance pickles unchanged (62 kB, and a
round-trip reproduces the residual exactly). But `sols` does not: the LOG policy functions pickle (554 kB),
the **CRRA ones do not at all**, because `griddedInterp2D` returns a closure. So the record of a
calibration is a csv row — reconstructing a solved model from it costs one `_calSetPars` and one ~25 s
solve against ~10 min to re-calibrate, and a csv survives code changes a pickle does not. Pickled instances
are a cache; `sols` is not stored.

**`η0` and `X0` are barely unknowns.** The Jacobian at `ρ=1.1` is diagonal-dominant in exactly those two
rows, and across a three-point march they move **0.00% and 0.02%** against 29%/22% for `β`/`ω`. The
four-parameter root could be reduced to two — **deliberately not done** (the user's call): an efficiency
change, not a fix, since the 4-D system is well conditioned. Related: the residual *scaling*'s stated
justification was stale, claiming `X0 ~ 2.6` when calibrated `X0` is 0.408 and 2.6 is `ω`'s value.

**Two findings that changed `num_calibration.tex`**, both later revisited — read deviations items 11–12 as
current, not the original readings. The doc's "main numerical hazard" (a `√(machine eps)` Jacobian step
returning noise) does not occur and its remedy is backwards; and for CRRA the hazard is real but it is the
grid, not the step (#3). A CRRA-only `eps=1e-4` override was adopted on the strength of one corrupted `η0`
Jacobian column (5.13 against a resolved 0.99) and **retracted 2026-08-19** — that column was the
smoother's residual jumps being straddled at that step.

**Two process notes.** I twice reported a conclusion a proper measurement then overturned — that the
residual was *bitwise* flat and the Jacobian identically zero (a trace printed `x` at 4 decimals, hiding a
1.5e-8 perturbation), and that the four equations were near-collinear. Both were plausible from partial
evidence, both wrong, and the measurement was cheap in each case. Separately: a 40-minute run with fully
buffered output is indistinguishable from a hung one — start long runs with `python -u`.

## 2026-08-12 — `createCopyFromt0`, and the second asymmetric state

`_sliceDb` is shared verbatim with `informalAnalytical`, whose README documents the mechanism. The one
addition here is that **`stateAtT0` carries a second state and the two are asymmetric**: `s_` reports
lagged, `ι` reports unlagged on the `txE` domain, so the state entering `t0` is `report['ι'].xs(t0-1)`
except at `t0 == db['t'][0]`, where it must come from `init['ι']`. Getting this wrong passes a
same-instance smoke test and fails only on a genuine shock, so `test_createCopyFromt0.py` pins the branch
with a sentinel.

## 2026-08-12 (cont'd) — the `ρ` sweep; `ρ=0.7` resists (attribution later found wrong)

15 of 16 points solved; `ρ=0.7` did not, across six attempts and four strategies. **This entry's
conclusion was wrong** — see 2026-08-19. Three parts survive.

*What the ladder ruled out*: the march's own extrapolation/carry/step-halving; a warm start interpolated
from the solved neighbours (an unremarkable surface, so "the starting points were bad" is out); and a
step-size probe showing every column except `X0` unstable, so no step size fixes it. `ρ=0.78125` took **37
evaluations / 1359 s**, and a retry of `ρ=0.775` warm-started from 0.00625 away landed at 3.3e-6 —
identical to attempts started 100× further out. **A closer start bought nothing.**

*The misreading, worth keeping as an example.* That plateau was read as grid-limited (#3) and the planned
next step was refining to `nι=ns=60`, which would have cost half an hour and closed nothing. Two
contributing habits: the step-size probe was run at an **off-root** point while the measurement it was
compared against was taken at a converged one, and its own caveat was recorded but not acted on.

*A cost note.* A **failed** attempt in this pocket averaged ~26 minutes — scipy iterates far longer before
declaring non-convergence than it does to converge — against ~6 minutes for a success elsewhere. A stuck
point costs much more to diagnose than a solving one costs to compute.

## 2026-08-19 — `ρ=0.7` solved: a discrete choice inside a differentiated residual

Now solves in **11 evaluations, first attempt, no step-halving**, residual 5.96e-12. Two independent
changes: `griddedSmooth1D`'s adaptive knot count pinned (#5), and the state-grid rule retuned. Full chain
and the measurements: `notes/informalSavings_resolvedIssues.md` §1; the settings themselves are in the
README's Conventions.

The re-derivation of what had been adopted *against* the jumps (#6) removed the outer-step override
outright and kept `45×45` on an argument an order of magnitude weaker than the one that established it.

## 2026-08-19 (cont'd) — the sweep re-run; the shock across the full grid

The retuned sweep and the universalisation experiment across all 16 ρ; numbers in
`notes/archive/informalSavings_results.md`. Two things from building the shock:

**Changing a parameter is not the same as passing it.** `κ(ε_{t+1})` is cached in `db` and read by every
equation as a given, so `installEps` must rewrite both. A mutually inconsistent `(ε, κ)` violates no
equilibrium condition, so nothing raises.

**Two readings of one reform.** "Universal" admitted two definitions (`b^0=b^1`, and `ε = 1-θ`), and they
turned out to **bracket** the status quo rather than differ in degree — every response reverses sign.
Either reading alone would have looked like a result.

## 2026-08-19 (cont'd) / 2026-08-20 — the `ρ=1` boundary, and a one-row patch

The `Δτ` dip at `ρ=1.0→1.1` was **not** the two recursions disagreeing — they agree to 0.0016 of a τ-grid
cell. It was the LOG anchor being the one point in every sweep solved on piecewise-linear interpolants
(#7). Full chain: `notes/informalSavings_resolvedIssues.md` §2.

**A one-row patch instead of a sweep.** Solver selection is `ρ==1` exactly, so exactly one row's residual
function changed; a warm start moves the path to a root rather than the root, verified at 8 CRRA points
which returned the published parameters to 6 significant figures. Done through the script's own resume path
in **30 s against ~2.5 h**.

**A backup that became a datapoint** (#8, third instance in this module): a backup taken in place matched
`plotUniversalShock.py`'s glob, and since the loader reads `ρ` from the file's own column, the pre-fix
anchor came through as a well-formed extra point and was plotted. The prose beside the figure was right,
because that analysis filtered the backup explicitly. Fixed both ways: superseded runs to a subdirectory,
and the loader now requires an exact filename match and **raises on a duplicate `ρ`** naming both files.

**Test status, stated precisely.** `test_calibrationGrid.py` has its pinned anchor updated but **was not
run** — started, then stopped at the user's request. Still open.

## 2026-08-21 — two experiments the paper needed, and a proxy state the control run found

Both built by parallel agents against a fixed output contract; the contract, not the code, was what had to
be got right first.

**`shockEEOnly.py`** holds `τ` at the baseline path and moves `ε` alone. It is **not** a second shock
experiment — with taxes exogenous there is no backward recursion at all, so all 16 points cost under a
minute against ~2.5 h. The baseline `τ` path is read off `shockUniversal.py`'s csv rather than re-solved;
that shortcut is **bitwise** exact, but only under `float_precision='round_trip'` — the default C parser is
~1 ulp off, which is enough to make a bitwise check fail and look like a real disagreement.

**A proxy state that the no-shock control found, and that is live in the existing results.** `EE_report`
backs its first period's lagged objects out of `initialState_solve` rather than taking them as arguments;
on a **copy** that is wrong, and since every shock compares a full-model baseline against a copy, the proxy
enters the *difference*. Details and blast radius in the README's Open items.

*Worth carrying:* **the control run was a precondition, not a test, and it is what found this.** It is
cheap and it asks the one question no residual can — does the machinery reproduce the baseline when the
shock is removed? A mutually consistent but wrong lagged state violates no equilibrium condition and so is
invisible to every convergence check in the repo. Same family as the `κ` staleness: **an object that enters
as *given* cannot be caught by checking the equations it enters.**

## 2026-08-21 — `sweepEpsThetaGrid.py`, and the cross sweep retired

The one-at-a-time cross sweep was replaced by a cartesian product grid, since the paper's figure wants the
whole surface. **Cost was the thing worth measuring first**: at ~1.1 s per point a full grid is minutes,
not hours — cheap enough that the cross sweep's whole reason for existing had lapsed. That was not obvious
before checking the `time` column of the existing csv.

**`ε` must not track `θ` here, and the reason is different from the old script's.** The cross sweep
defaulted the flag off because letting `ε` follow `θ` would superimpose a reversed `ε` sweep on the `θ`
*panel* — a presentation argument. On a product grid the argument is structural: following the chain
collapses the grid onto a curve, and there is no `θ`-family for the figure to exist at all. So the flag is
not offered rather than defaulted off. Worth keeping the two reasons distinct — the presentation one could
be argued with; this one cannot.

**One documented claim the sweep contradicts.** `Quant.tex` says the marginal effect decreases with `ε`
"in all cases". That holds for `τ`, the savings rate and `h`; it does **not** hold for `ι`, whose marginal
effect grows monotonically across the whole grid. Reported rather than tuned — the fix is a word in the
paper, not in the code.

## 2026-08-24 — the calibration target moved to K/Y, and everything downstream was re-run

Two analysis passes preceded the change and the second corrected the first; both are now consolidated in
`notes/argentina_calibrationTarget.md`, and the transferable form is #12. The short version: the defect was
the datum's **time dimension**, not its denominator or its sector coverage.

`db['KY0'] = 3.2313` replaces `db['s0']` as the moment identifying β, through `Base.capitalOutputRatio`
(`eq:calibration:KY`), and **`yearsPerPeriod = 30` is now a model parameter** rather than a convention
living only in the documentation — that convention being exactly what the error turned on. The residual is
formed once, in `_calResidual`, with K/Y **relative** and τ **level**: K/Y is O(3.2) against τ's O(0.125),
so a level gap there would swamp the tax target. The savings rate is still computed and reported, because
the paper's tables quote it.

**The datum is the calibration year, not a window mean** — every other target in `eq:calibration` is
measured at or around 2010, and Argentina's K/Y moves too much over the preceding decades for an average to
describe the same economy. It also decides the question that opened all this: β crosses 1 at K/Y ≈ 3.64, so
the 30-year mean would have left β at 1.0126 where 2010 gives 0.8076.

**Full re-run, ~4 h**, all 16 ρ: sweep, both universalisation readings, the EE-only decomposition, the
(ε,θ) grid, the paper rebuild, and `runTests.py --all`. Three findings, detail in
`notes/archive/informalSavings_results.md`: β crosses 1 between ρ=0.8 and 0.9 rather than at ρ≈1.15 (the
curve is ≈0.65× its old self everywhere, so the retarget shrank the β>1 region rather than removing it);
the ρ≈0.7 pocket is gone, though not separated from the different β it lands on; and `verifyResidual`
degrades down the low-ρ tail, leaving those rows converged but not resolved.

**Two test failures, both stale references rather than defects.** `test_calibrationGrid` pins the anchor
against the README and was updated, as its own comment prescribes. More interesting:
`informalAnalytical/test_calibration.py` failed to converge *from its shipped starting guess* of β=0.6,
tuned for the old target, walking into a region where the path solve returns a NaN τ and the steady-state
`brentq` dies at its own lower bracket. Every start in [0.7, 1.0] reaches the same root, so the guess moved
to 0.85. **Worth recording as a limitation of that variant**: its outer search has no globalization, so a
start far from the root fails rather than converging slowly. This arm took the same change from the same
guess without complaint.

## 2026-08-24 (cont.) — cleanup

The module's two "Results:" README sections moved to `notes/archive/informalSavings_results.md`, the
`ρ≈0.7` and `ρ=1` investigation notes merged into `notes/informalSavings_resolvedIssues.md`, and the
deviations note renumbered into current state (the retracted items folded into the ones that replaced
them). Superseded sweeps, their pickles and all run logs were deleted — recoverable at `bfba998`. That
turned up one live defect: `measureOuterSettings.py` still defaulted its `--csv` to a superseded file,
which is #8 in the other direction. **A stale default that still resolves is worse than one that does not.**

## 2026-08-25 — the (ε,θ) grid re-solved at the current calibration

The 2026-08-24 retarget entry above says the full re-run included "the (ε,θ) grid". It did not: the sweep
resumes on `(ε, θ)` and was re-run **without** `--force`, so it added the new calibrated ε column and kept
378 rows solved at the old β. Re-solved here — 378 points, 27 ε × 14 θ, `nRoots = 1` everywhere, and the
status-quo row reproduces the calibrated baseline exactly (τ = 0.125, sr = 0.147247, h = 0.499316,
ι = 0.364964). The mechanism and the guards added downstream are in `python/paper/RESEARCH_LOG.md` and
generalised as `crossCuttingFindings.md` #13.

**Cost: ~2.4 s per point, not the ~0.65 s the old csv's `time` column recorded.** The estimate had been
read off rows solved at the previous calibration, so the sweep is ~15 min rather than the ~5 documented in
`python/paper/`. Worth noting as a fact about the current β rather than a regression: the timings were
stale in exactly the way the rows were.

**The `ι` exception survives the retarget, and is sharper than first recorded.** `Quant.tex` claims the
marginal effect of ε decreases "in all cases"; on the fresh grid it holds for τ, the savings rate and h,
and fails for ι, whose `|∂ι/∂ε|` *grows* by a factor of three across the grid — 0.036 to 0.108 at the
calibrated θ, monotonically in 11 of 14 θ columns, the other three flattening near the upper edge rather
than turning over. Every other documented claim checks out on the new numbers, including "almost linear in
θ" for h: its θ-slope moves 8% from θ=0.5 to θ=1, against 23% for τ and 43% for the savings rate.

**RESOLVED the same day, and not by a carve-out.** The user rewrote the paragraph rather than exempting ι
from it: the "marginal effect decreasing with ε in all cases" sentence is gone, and with it the only claim
the sweep contradicted. This closes the item opened 2026-08-21. The replacement makes four claims, all
re-checked against the fresh grid and holding **strictly at every grid point** — τ up in ε and down in θ;
savings and labour down in ε, up in θ, largest effect at low ε (|slope| 0.035→0.009 for sr, 0.042→0.019
for h); ι down in *both* ε and θ; and formal savings falling in ε too, so `s^0 = ι·s` drops by more than ι
alone shows. That last one is new and worth the arithmetic: across the ε range at the calibrated θ,
ι −14.2% and s −15.9% compound to s^0 −27.9%.

*Worth keeping:* the sweep's contribution here was not the correction but the **claim that could not be
made before** — that ι falls in θ as well as in ε, which is a statement about the whole surface. The cross
sweep the grid replaced could not have supported it.

**One thing the re-run changed for the reader.** The figure's reform move (ε: 0.305 → ε^U = 0.546 along the
calibrated-θ curve) is now +1.89 p.p. in τ, against the +1.44 p.p. in Table `ArgentinaUniversal`. The two
are different objects — the sweep puts the reformed system in place over the whole horizon and lets the
initial state be re-derived under it, while `shockUniversal.py` is unanticipated at t0 onto the baseline's
inherited state — but before the re-run the stale diamond read +1.24 p.p., so the figure *understated* the
table and now *overstates* it. The text quotes "about 1.4 p.p." next to the figure. Open, in the paper.

## 2026-08-25 — num docs restructured (detail in the root log)

`writing/informalSavings/num*.tex` rewritten as final-state technical notes. The selection rule
(`eq:objectiveProfile`/`eq:candidates`) moved from `num_peeLOG.tex` into `num_robustroot.tex`; the ι-grid
bounds discussion and the calibration step-size/grid-displacement measurements were compressed to the
design rules they justified — the journeys stay in `notes/informalSavings_*` and this log.
`num_ee.tex`/`num_shock.tex` essentially unchanged. Every label cited by `policy.py`/`model.py`/tests is
preserved.
