# Research log — US

Model-specific session log. Current state, conventions and traps are in this folder's `README.md` — check
there first; this log is history and open decisions. Recurring findings are cited by number from
`notes/crossCuttingFindings.md`.

## 2026-08-21 — documentation, written before any code

`writing/US/` (namespace `us`, exogenous `θ`). The model is `informalAnalytical` with the informal type
removed, so most of the tex is a copy with the `j=0` terms deleted and `κ_t` collapsed to `p_t`. **Two
results came out of writing the derivation rather than out of running anything**, and both shaped the code
that followed: the LOG first-order condition decouples across time, and `η`/`X` carry *two* independent
invariances rather than one. Both are in the README.

**A normalisation I got wrong first.** The first draft of the common-`X` variant moved the normalisation
off `Γ_h = 1` and onto `∑γ_iη_i = 1`, reasoning that the hours target identifies the scale. It does not —
it identifies the hours *unit*. Both variants normalise `Γ_h = 1`; they differ only in whether `μ` is left
arbitrary or pinned by average hours. Aggregate `h` cannot serve as that target, because it does not
respond to `μ` at all.

**A typo in both parent docs, left unfixed there.** `writing/{informalAnalytical,informalSavings}/
model_setup.tex` write the labour-supply FOC's pension term undiscounted, while the savings equation on
the next line discounts. It should carry `/(R_{t+1}/p_t)`; the equilibrium expression in each file already
implies exactly that. Confined to one line in each, nothing downstream inherits it, and the US doc has it
right.

**`θ = 2 − 1/RR` is the idea, not the computation.** That closed form holds only if the income groups sit
at exactly half-mean and mean. They sit at `z^η = (0.507, 1.001)`, and the difference matters: the general
formula gives 0.738 (the paper's number), the idealised one 0.745. `getθ` uses the general one.

## 2026-08-21 (cont'd) — code, and the ρ sweep

`base.py`/`policy.py`/`model.py` copied from `informalAnalytical` and adjusted. The zero-mass `j=0` slot,
`getEps`'s guard and the `Γs` bracket are all in the README; the bracket is #7's shape — a constant that
was **safe by parameter values rather than by construction** and travelled with a file copy.

**The sweep is the check `crossCuttingFindings.md` #4 asked for, and it found #5, not #4.** The policy
smoother was using FITPACK's adaptive knot count. Measurements are in `notes/archive/us_measurements.md`
§1; two things worth carrying forward: **judge by the trend, not the spread** (the converging sequence has
the *wider* range, which is how this was nearly dismissed), and **the adaptive smoother was masking the
error, not avoiding it** — a band with no trend is not a small error bar, it is the absence of information.
#4's own fix was tested and **not** adopted.

**How to read `verifyResidual`.** The `ρ=1` row is uninformative — LOG has no inner state grid and
`solveVectorized` does not touch the `τ` grid, so it comes back equal to the residual by construction. On
CRRA rows it *overstates* the uncertainty: ~7e-4 at ρ=0.5 across every `ns` from 100 to 300, while `β`
itself is settled to 1e-4. It measures how far the residual moves under a 1.5× grid change at fixed
parameters, which does not vanish because the parameters converged. **A level across points, not an error
bar.**

**Validation.** The vector-`X` calibration reproduces the *commented-out* column of
`USUKFRCalibration.tex`. The first three matched quantities are scale-invariant and are the real evidence;
the `X` match is at the eigenvector routine's own arbitrary normalisation, so it says the two codebases
call the same eigensolver, not that they agree about economics. The **live** column is a different vintage
and is not reproduced — and since `θ` is closed-form in `RR` and `z^η` with no model object entering, that
gap has to be input data, not solver behaviour.

**Open, for whoever writes the paper table.** Its `X` row is labelled *"Target: Avg. workweek"*, but under
vector `X` the workweek is not a target and `X`'s level is arbitrary — yet the commented values match
vector `X`. An `X` actually calibrated to the workweek is ≈4.15 (vector `X` with the target imposed) or
4.03 (common `X`), not 10.9.

**Still open from this session**: `η_H/η_L` differs between the calibration variants (3.733 vs 3.080). Not
a units artifact — the ratio is `μ`-invariant — but a real consequence of the identification. Common `X`
over-predicts the hours gradient by 21.2%, which is the price of the restriction and the diagnostic
`model_calibration.tex` says to report.

## 2026-08-22 — France/UK (`ModelFR`), the counterfactuals, and the paper pipeline

### `ModelFR` and the sweeps

**The structural fact that made this small: proportional `X_i` scaling *is* the documented scale
invariance.** `test_invariance.py`'s `rescale(λ)` already applies exactly that transformation, so λ is
block-recursive to the ω root and is closed-form, applied *after* it. Three hooks opened in `model.py`
(`hbarTarget`, `_calResidual`, `_calPostRoot`) so each override changes one thing in one place.

**A real bug the test caught: λ was an increment, not a level.** `rescaleX` multiplies the `X_i` already in
db, so a repeated `calibrate` — or the next point of a march, which reuses one instance — reported the step
from the previous solution rather than the total (λ = 0.893 then 1.000 then 1.000). Every other column was
right either way, because the target is absolute and the rescaling reaches it from wherever it starts. That
is what made it worth pinning: **the wrong λ is plausible and lands everything else on target.**

Note this bug only existed *because* `Γ_h` is not arbitrary here. Under `ModelUS` it is a free
normalisation; under `ModelFR` the hours target pins it. I had described it as arbitrary and was corrected
— worth recording, since the correction is what made the λ bug findable.

All six sweeps (FR/UK/UKUS × two variants) solved 16/16, residuals ≤ 1.4e-14, and **β reproduces the US
sweep exactly (0.0e+00) in all six**. τ is constant to 1e-14 under common `X` and 1e-4 under vector `X` —
precisely the rescaling drift, since only vector `X` carries a rescaling. The CRRA rescaling's
absolute-s-grid-floor story is in the README.

### The counterfactuals

**τ and the savings rate reproduce the paper exactly on all 14 rows at ρ=1.** Three conventions had to be
*recovered* to get there — the savings rate is `s/(w·h)`, the workweek is a per-ρ normalisation, and
`db['dates']` is stale on a copy — each now documented where it is applied.

**Two findings inside the French rows.** The income row moves `θ` 0.738 → 0.495, so it bundles a
pension-design change with the inequality change. And **`shockTheta` first returned the baseline for both
polar cases** — `updateAuxPars` re-derived θ straight back. Now #9, because the null result reads as a
conclusion rather than as a bug.

The one thing that did *not* reproduce: the workweek column on full-effect rows (0.4–2.5% off; exact on the
ageing EE rows). τ and sr are hours-unit-invariant and match everywhere, so the gap is in the conversion,
not the equilibrium.

### The pipeline

`python/paper/` gained a second arm. Contracts verified rather than assumed: stages (i)/(ii) skip what
exists, stage (iii) is idempotent and does not re-back-up, and with `US_shocks.csv` removed the seven
shock-derived outputs report BLOCKED while the four calibration-derived ones stay OK.

Also caught: `config.pct` escapes the percent for tex, so a figure legend rendered a literal backslash.

### Open from this session

- The workweek full-effect gap against the paper.
- The UK's `X_i` are uniformly 1.108× the paper's while `η_i` matches exactly — purely the λ degree of
  freedom. Relatedly, the paper's own two UK tables disagree: `UK_householdheterogeneity` implies
  `η_H/η_L = 3.88`, `USUKFRCalibration` says 2.73/2.85. This code gives 3.868.
- The live `US_CRRA_Ageing.tex` disagrees with the live `US_Ageing.tex` at ρ=1 for the same scenario
  (16.33% vs 18.45% for mild ageing). This code gives 18.45%, siding with the LOG table, and reproduces
  the CRRA table's ρ=0.5 row exactly. Mixed vintages within one table.

## 2026-08-23 — endogenous `θ`: the leaded choice under a deadweight wedge

The appendix reports that the sequential, leaded and permanent choices of `θ` all corner at `θ = 0`, and
that only the deadweight-wedge formulation is interior. This session implemented **the leaded choice with
the wedge** — the combination the appendix never runs.

**The whole wedge is one substitution.** `θ → A(θ)`, `(1-θ) → B(θ)` in `Γs`, `Θh`, `si_s`, `c1i`,
`tildec1i`, `c2i`, `dlnc2i_dτ`, `ΓsCap`, `BSteadyState` — because in *every* equilibrium object `θ_{t+1}`
appears only multiplying `(1-α)/α·τ_{t+1}`. `bbar` stays gross; the lost share is implicit in `A+B < 1`.
Two specs: `scale` (`A = fθ`, `B = f(1-θ)`, the appendix's live one) and `flat` (`A = θ`, the commented
variant).

**Three structural findings, all measured rather than assumed** — `z_t` depends on `(τ_t, θ_t)` alone;
under LOG the leaded choice has **no state at all**; the choice is invariant to `s_{t-1}`. Details in the
README. The appendix treats `θ_t` as a state under this timing; under LOG it is not one.

**The wedge escapes the corner and calibrates to the appendix's own number.** `scale`/φ=0.5 gives
**p = 0.402 against the appendix's 0.41** from the *sequential* calibration — the two timings need almost
the same wedge. `flat` is the better-behaved spec: `scale` reaches the `θ=1` corner by p≈0.7, so its
calibrated point sits close to a boundary in p-space, while `flat` stays interior across the whole scanned
range (but there θ is jointly identified with p, and `getθ` becomes a scalar root).

### What it predicts — and where it fails

**Ageing raises `θ`, as figure 1.1 and the paper's conjecture say.** Along the calibrated path the chosen
design rises 0.738 → 0.754 → 0.764.

**But the magnitudes are the wrong way round.** Sweeping one axis at a time: `ν` from 1.55 → 0.95 moves
the chosen θ 0.723 → 0.780, while inequality from `η_H/η_L` 3.73 → 2.44 moves it 0.738 → **1.000**. At
France's inequality the model picks θ = 1.00, which is exactly France's observed design — but it gets there
through **inequality**, and moving `ν` from the US's 1.34 to France's 0.97 buys only +0.05 of the +0.26
US→France gap. **Figure 1.1 reports the opposite ranking**: a clear cross-country relation of θ with
population growth and none with the Gini. So the mechanism reproduces the CondeRuizP07-style prediction
that the paper's own introduction says the data reject. French voting patterns push the other way, so the
offsetting story is real but does not rescue the ranking.

**Cross-country, one common wedge does not order the three countries.** At the US-calibrated p, France
chooses θ = 1.00 (data 1.00 ✓) and the UK chooses θ = 1.00 (data 0.56 ✗); matching the UK needs
p = 0.186 against 0.402. France's own p has no interior solution — its choice is at the corner for every p
in the bracket, which `calibrateWedge` reports rather than papering over.

**This is the substantive obstacle, and it is not numerical.** Any mechanism whose force is within-cohort
redistribution will tie θ to inequality; matching figure 1.1 needs one whose primary driver is the age
structure.

## 2026-08-23 (cont.) — CRRA, and the permanent choice

**`LeadedCRRA`** iterates on the equilibrium *path*, re-solving the whole PEE at every candidate design —
which is also what makes the envelope logic right, since τ_t is re-optimised at each candidate. Its one
assumption, that the choice at t+1 does not respond to the design it inherits, is **measured**:
`dθ_{t+2}/dθ_{t+1} = −0.009`. Validated against its own limit: as ρ → 1 the CRRA choice converges on
`LeadedLOG`'s at a clean first-order rate (gap/(ρ−1) = 0.90, 0.90, 0.94 at ρ = 1.10/1.05/1.02) — two
solvers sharing only the objective's weights, agreeing where they must.

**A higher EIS needs 4.7× less wedge** to reach an interior design — the factor `thetaStakes.py`'s
decomposition predicted from an entirely separate calculation — and roughly **doubles the ageing
response**. ρ = 2 helps the mechanism on both counts without changing the inequality-vs-ageing verdict.

*A test that passed for the wrong reason*, now #10: the first state-sensitivity check used the
LOG-calibrated wedge at ρ = 2, which sits on the θ=1 corner, so both perturbations return 1.0 and the slope
is trivially zero.

**The permanent choice** is cheaper than the appendix's recipe in two ways, neither obvious from the
write-up (which proposes a 2-D grid): the joint choice **concentrates** to a 1-D maximisation, and once θ
is fixed forever there is no recursion. **The one thing that must not be got wrong** is pinning
`s_{t0-1,i}/s_{t0-1}` — 0.773 pinned against 0.910 moving, at the same wedge (#11).

**The required wedge is essentially timing-invariant** (~0.375–0.41 across sequential, leaded and
permanent), and at a common wedge the two implemented timings deliver designs within ~0.04 of each other.
**The timing is second order; the wedge is what does the work.** Worth saying in the appendix, which
presents the timings as alternatives with qualitatively different outcomes — they differ only in the
*absence* of a wedge.

**The permanent timing is fragile in ρ, and the appendix does not report this.** With no wedge the
permanent objective is essentially monotone in θ, so the choice is always a corner — and *which* corner
flips inside the paper's own ρ range:

| ρ | 1.1 | 1.2 | 1.3 | 1.4 | 1.5 | 2.0 |
|---|---|---|---|---|---|---|
| θ permanent | 0 | 0 | 0 | **1** | **1** | **1** |
| W(1) − W(0) | −0.0065 | −0.0026 | −0.0005 | +0.0007 | +0.0014 | +0.0024 |

The appendix reports the θ = 0 corner because it works at ρ = 1. Above ρ ≈ 1.35 the sign reverses: with a
high EIS the young's resistance to taxation is low, so the dominant channel is the future path of τ and
capital — permanently higher θ means permanently lower τ and more capital — and that beats the
redistribution motive. The objective is nearly flat between the corners near the flip (5e-4), so this is a
near-tie rather than a sharp switch. **Consequence for the wedge**: at ρ = 2 the permanent choice is
already at θ = 1 *without* one, and a wedge penalising Beveridgean design pushes it further that way, so
under permanent + CRRA the wedge cannot deliver an interior solution at all. It makes the permanent
specification unattractive as the paper's headline, since its qualitative result depends on a parameter the
paper treats as robustness. **A decision, still open.**

## 2026-08-24 — the true leaded CRRA solution (`LeadedCRRA2D`)

Computes the Markov object the path iteration approximates, by one direct backward pass. Design decisions
worth recording:

- It **subclasses `policy.CRRA` and overrides exactly one method** plus the assembly around it, so the two
  solvers cannot drift apart. The `θ_t` axis is not carried through the big grid: `θ_t` enters only the
  current old's `dv2i` term, so the expensive numerical τ-derivatives are computed once per period.
- **Pinning lives in the recursion, not the simulation.** Under CRRA `τ_t` responds to `θ_{t+1}`, so
  periods where the design is history must be solved with the candidate set collapsed to the inherited
  design — the LOG habit of pinning only in `simulate()` would evaluate τ off the pinned continuation.
  This is also what makes the pinned-everywhere recursion collapse exactly to the exogenous-θ solver,
  which became a check against production code.
- The planned warm start from the approximation was **not needed**: a direct recursion has no seed. **The
  approximation's role inverted** — it is the cheap method being *certified*, not the certifier.

The W objective is flat enough near its maximum that *either* method pins the design only to ±0.01 —
consistent with the stake decomposition's finding that the design stakes are second-order — and they agree
within that band, so the path iteration is certified for the tables. The grid sensitivities are the useful
surprise: the s-grid is immaterial, but the θ-**state** grid is not.

**The wedge falls steeply in the EIS** — p = 0.95 / 0.40 / 0.086 at ρ = 0.5 / 1 / 2 under `scale`. The
counterfactuals across ρ × spec are in `notes/esc_experiments_acrossRho.md`; the headline is that whether
"French characteristics" raise or lower the Bismarckian index is an **EIS question**, since income
distribution and voting pull in opposite directions and which wins depends on ρ.

## 2026-08-24 — every US counterfactual becomes a new equilibrium path, read at 2020

**Decision, from the user**: a row should describe a country that has *always* had its mix of
characteristics, so that it is commensurable with France's own calibrated path. That comparison is the
point; a 2020 surprise is not comparable with an equilibrium. Applied to both the exogenous-θ main-text
tables and the endogenous-θ appendix.

**Measured before deciding, and it made the change cheap.** At ρ = 1 the convention moves the workweek
column and nothing else — τ and the savings rate agree to every printed digit across all seven scenarios,
because under LOG/Cobb-Douglas both are rate objects independent of the inherited capital stock. The
main-text tables are ρ = 1, so their headline numbers did not move at all. This does not survive to CRRA.

**It also resolved a standing discrepancy.** The leisure row is a pure `rescaleX`, and the scale invariance
requires `s_0` at the model's own steady state — which an unanticipated shock cannot have. It used to give
35.10 against the paper's 34.72; the new path gives 34.74.

**The wedge calibration had to move one period back with the reporting.** `θ_t` is a state chosen at
`t-1`, so the design in force in 2020 is `θPolicy_1990`. On the old target the freely simulated path came
back at **0.727** against the observed 0.738 — a 1.1pp miss in the baseline row of every comparison table.
`p` moves 0.40220 → **0.40761** under `scale`, φ = 0.5, ρ = 1.

**The design response at 2020 is monotone in ρ**: acute ageing takes θ from 0.738 to 0.766 / 0.778 / 0.846,
French voting drives it to 0.662 / 0.533 / 0.285, and the French income distribution corners at θ = 1 at
every ρ. Same ordering as the calibrated cost itself — a higher elasticity strengthens the young's
forward-looking stake, so the same characteristic change moves the political outcome further and less
friction is needed to hold the choice off the corner.

**One real bug fell out** (#7): with `s0` no longer seeded, `solvePEE_CRRA` reaches `steadyStatePEE_CRRA`,
and at `θ = 0` — now over the whole horizon — `ΓsCap` is infinite, so the bound reverted to the bare
constant. Latent for as long as the old convention kept θ = 0 away from that solver.

**Two further defects, both of the same kind — a registry or an interval correct only for the case it was
written against.** `shocks.shockedCopy` looked names up in `shocks.SHOCKS`, but `frBoth` lives only in
`runESC.SHOCKS_ESC`, so every `frBoth` row failed `KeyError` at ρ = 2; `shockedCopy` now takes an optional
registry. And `runESCcrra`'s `--bracket` defaulted to an interval tuned at ρ = 2 that sits entirely below
the ρ = 0.5 root — both specs reported "no sign change", the scan doing exactly what the corner guard is
for. Worth noting the previous vintage of that csv had ρ = 0.5 rows, so someone had passed a wider bracket
by hand and **the default had been wrong the whole time.**

The backfill gave a free check nothing was asserting: `frAll` and `frBoth` differ only by the leisure
scale, a pure `rescaleX`, so they must agree on design and tax and differ only in hours. At ρ = 2 both give
θ = 0.70676 and τ = 14.45% with workweeks 36.04 and 40.47 — the scale invariance holding through the
endogenous-θ layer under CRRA.

**The grid-refinement study behind the ±0.01 flatness claim was NOT re-run** at the new wedge. It is a
property of the discretisation rather than of `p`, and both the tex and the README now say so instead of
implying it was measured at the current value.

**Addendum — the permanent timing's second decision.** The 2026-08-23 entry justified pinning
`s_{t0-1,i}/s_{t0-1}` at the incumbent design as an "unanticipated permanent reform"; that justification is
corrected here rather than by editing the dated entry. The vote at `t0` is anticipated, so the equilibrium
is the fixed point `θ* = argmax W(θ; siRatio(θ*))` — `solveFixedPoint`, now the default. Pinning itself
stays right; only the value pinned at was wrong, and it is a no-op exactly at the calibration point, which
is why every calibrated `p` is common to both readings and only counterfactuals separate them (#11b).
Still open: `PermanentCRRA` has never been executed since its restructuring —
`notes/todo_escPermanentTiming.md`.

## 2026-08-25 — num docs restructured (detail in the root log)

`writing/US/num*.tex` rewritten as final-state technical notes; `num_esc.tex` keeps every methodological
innovation and loses only the backwards-looking framing (the "previously used" counterfactual convention
is now a neutral comparison of the two constructions). Two latent defects fixed there: `\Eqref` (a macro
defined nowhere in the preamble) and `\refeq:esc:auxiliary:si` (wrong prefix — the label lives in
`model_esc.tex` under `\refmodeleq:`). `eq:extendedGrid`/`eq:objectiveProfile`/`eq:candidates` now live in
`num_robustroot.tex`. `num_ee.tex`/`num_calibration.tex` untouched; all code-cited labels preserved.


## 2026-08-27 — the income-distribution counterfactual holds θ, and a pin that did not hold

**Decision, from the user**: the French income-distribution row should change the income distribution and
nothing else. `θ` is identified from the ratio of replacement rates at mean and half-mean income, so
France's flatter `η` implies a much less Bismarckian system through the *same* observed ratio — 0.738 →
0.495. Letting that happen puts a pension-design change inside a counterfactual about inequality, when
pension design is the separate `theta` family in the same table set. `shockIncomeDistribution` now pins by
default (`--freeTheta` keeps the re-deriving reading on disk), and the ESC exogenous-θ rows inherit it.

`θPin` defaults to the model's own design read *before* the swap rather than to a value the caller passes.
The caller had one — `frenchData['θUS']` — but a default that depends on the caller supplying the right
number is a default that can be wrong quietly; reading it off the object being shocked cannot be.

**The pin did not survive the composite rows, and that is finding #9 in a form the existing habit misses.**
#9's rule was "set a derived parameter *after* the refresh". `shockIncomeDistribution` does exactly that —
and then `shockFrenchAll` calls `shockVoting`, whose own `updateAuxPars` re-derives `θ` from the η now in
db, which is France's. `frAll` and `frBoth` came back on **θ = 0.551** with every other column plausible;
`frIncome`, where nothing runs afterwards, was correct. The rule extends: **a derived parameter is pinned
by the last refresh in the whole sequence, not by the last one in the function you are reading.** Both
composites re-install it at the end, `test_esc.py` asserts the pin survives each of `frIncome`/`frAll`/
`frBoth` *and* that `pinTheta=False` still re-derives, and `frBoth` became a named function instead of a
tuple-of-lambdas so it has somewhere to say so. Caught by reading the run's own output rather than by a
test — the pinned rows printing 0.5506 where 0.7382 was asked for.

## 2026-08-27 — the ESC leg gains the common-X variant, and loses the flat spec

`runESC.py`/`runESCcrra.py` take `--commonX`, threaded into `buildUS` and `buildEU`. Two things had to
agree that are easy to miss: `usReference` must be read off the *same* variant's sweep (it carries
`h̄_US`, and `h̄` differs between the variants by construction), and `frenchData` must build France under
the same variant, since under common X France's `η` inverts `z^η` directly and its `X` is a scalar.

**`commonX` is a column and part of every merge key.** These csvs are resumable and their rows do not
otherwise record what produced them, so without it a common-X run would overwrite the vector-X rows, or
leave them to be read as current — #13. `datasets.escCalibration`/`escRow` filter on it. Two guards were
needed rather than one: `bool(nan)` is **True**, so a blank cell would file an untagged row under common
X, the one variant it certainly is not; and `mergeWrite` adds a key column missing from the file on disk
as NaN, so a pre-column csv keeps its rows instead of raising.

**The calibrated wedge is invariant to the variant, bit for bit**: `p` = 0.964818 at ρ = 0.5 and 0.407612
at ρ = 1 under both. Block recursivity reaching through the endogenous-θ layer — the leaded choice sees
`η`/`X` only through the normalised aggregate.

**And so is the chosen design, measured rather than inferred.** Comparing the LOG counterfactuals under
the two variants scenario by scenario: baseline, mild and acute ageing, voting and leisure agree to
**≤ 1.2e-12 in θ and 1.2e-14 in τ**, in the *endogenous* reading as well as the pinned one. That settles
two things at once — the ±0.01 certification of the path iteration against the 2-D solver was measured
under vector `X` and carries over, and the appendix's ageing, voting and leisure results are literally the
same numbers under either identification.

**Only the scenarios that swap `η` move, and `frIncome` alone hides it.** Under vector `X` the swap holds
`X_i` fixed, so `y^η_i = η_i^{1+ξ}/X_i^ξ` is not proportional to either country's `z^η`; under common `X`
it is proportional to `η_i^{1+ξ}`. Different `y^η` distributions, hence a genuinely different experiment —
the same 13.21% against 12.83% the exogenous-θ table shows. `frIncome` reads as identical (1.000 both)
only because it corners; `frBoth` and `frAll` are interior at 0.9718 against 1.000 and show it. A corner
masking a real difference is #10's shape: the invariance had to be read off the scenarios that are not at
one.

The `flat` (redistributive-only) cost spec is still implemented and runnable but is no longer run for the
paper — the user's call. It is a second formulation of the same assumption and it doubled the most
expensive stage in the pipeline.

## 2026-09-08 — a forced failure that did not fail

`test_calibration.py`'s "forced failure raises" check called `calibrate(tol = 0.)` and expected
`_checkConverged` to raise. Under the full runner it passed silently once: a warm-started root landed on a
residual of exactly 0.0, and `0.0 <= 0.0` is converged. Standalone it raised every time. The check now
uses `tol = -1.`, which no finite residual satisfies — a "forced" failure has to be forced by construction,
not by a tolerance the solver can happen to meet (`crossCuttingFindings.md` #1 on cross-process bitwise
differences is the likely reason it showed up only under the runner).

## 2026-09-11 — the income-distribution shock carried France's productivity level, not just its profile

RKB asked for a review of how the "French income distribution" counterfactual is implemented and whether
a normalisation had been forgotten. One had, and it is worth stating precisely because it is invisible in
every column except hours. The model is invariant to the joint scale (η, X) → (cη, cX), which is what
Γ_h = 1 normalises away; but η → cη at *fixed* X is not a normalisation, since hours depend on η_i/X_i,
so it moves h_i and h̄ by c^ξ while leaving τ, s/Y and R exactly alone (eq:us:model:hoursUnit). France's
calibrated η_i carries the level that Γ_h = 1 fixes at *France's* X. Under common X that is
η_FR = z^{1/(1+ξ)} X_FR^{ξ/(1+ξ)}, a factor (X_FR/X_US)^{ξ/(1+ξ)} = 1.14 above the US level at ρ = 1 —
France's leisure preference showing up as a productivity advantage. Swapped in raw, `shockIncomeDistribution`
left Γ_h at 1.185 on the shocked model and put the income row's workweek 4% too high (41.97 against 40.36
hours full effect, 41.68 against 40.08 EE-only); τ, sr and R agreed to every printed digit between the two
readings, which is why nothing had flagged it. Under vector X the raw level comes from the unit-norm
eigenvector `eigs` returns and happened to land at Γ_h = 0.998, so the appendix numbers move by 0.04%; that
was luck, not a property.

The fix (option 1 of two put to RKB; option 2 was to keep the numbers and state the convention): new
`shocks.ηLevel(m, ηFR)` returns c = Γ_h(η_FR, X_US)^{-1/(1+ξ)}, evaluated before the swap so it reads the
US X_i; `shockIncomeDistribution` installs c·η_FR (zero-mass slot included), asserts Γ_h = 1 afterwards
and returns c instead of θ. `shockLeisure(mt0, xbarRatio, ηScale = 1.)` rescales X by ηScale·xbarRatio,
so France's X is expressed on the same scale the income row fixed and the two rows still compose to
France's own (η, X) up to the joint scale: `frAll` and France's own row are unchanged in every column
(35.29/35.18 h common X, 35.91/35.70 vector X), only the split between the two single-characteristic rows
moved — leisure goes from 33.24 to 34.57 hours under common X. `shockFrenchAll` feeds the income step's c
to the leisure step; both `frenchData` functions (runShocksUS, runESC) carry `ηScale`, so `runESCcrra` and
`frBoth` inherit it. A residual convention remains: "same productivity level" could mean ∑γ_i η_i fixed
rather than Γ_h = 1, worth 0.5% on the workweek against the 4% at stake. Three new checks in `test_esc.py`
(c·η_FR installed and returned; Γ_h = 1 with c ≠ 1; frAll's X_i/X_US = c·xbarRatio); all 22 suites pass.

Also measured on the way, and recorded in the README: under vector X the row does not impose France's
income profile at all. With X_i held at the US values the implied relative income is
[0.659, 1, 1.635] against France's [0.638, 1, 1.874] and the US's [0.506, 1, 2.186] — more compressed at
the top than France, because France's top group works relatively longer hours and that enters through
X_i. Under common X the row's profile is France's exactly. The docstring already said the fixed-X swap is
the experiment reproducing the paper; the appendix label "income distribution" is looser there.

**Not rerun.** The sweeps wait on another session's Argentina job; every US shock and ESC result file is
now stale for the frIncome/frLeisure/frBoth/frAll rows (`notes/TODO.md` item 1). The leisure shock itself
is no longer printed in the paper (paper log), but it still runs and stays in every csv.

# Entries 2026-09-11 to 2026-10-07

Moved verbatim from the live log on 2026-10-07, oldest first. Run logs under `logs/` that these entries cite were deleted the same day, except `logs/finalRun1002/` and `logs/finalRunC8/`.

## 2026-09-11 — Exact CRRA ESC solver published; timing checks as tests and stages

`runESCcrra.py --exact` runs the wedge calibration, design path and counterfactuals through `solveLeaded2D`
(`ModelESC.leadedDesignAtT0_2D`, `calibrateWedge` preferences `CRRA2D`, scan at `--nsScan` 50 then refine
at `--ns` 150, 41 candidates); rows carry `method` = exact|path, in every merge key. Exact p: 0.935 (ρ 0.5),
0.0855 (ρ 2). The path iteration stays as the cross-check only. STOP 3 of `notes/plan_2026-09-11.md`
(frVoting θ 0.285 path vs 0.273 exact at ρ = 2) was the candidate grid on a flat objective (W differs by
1e-5 over ±0.01 in θ; 13/21/41/81 candidates give 0.285/0.273/0.263/0.262), not state dependence (slope
−0.001). New: `ModelESC.sequentialFOC` (costless seqFOC on a solved path; negative on [0,1] at every dated
period, ρ = 0.5, 1, 2), `--stage sequential`, `test_escTiming.py` (slow: TODO R3's permanent reference
numbers; "p = 0.375" is the calibrated 0.375032). `PermanentCRRA` ran for the first time: corner θ = 0 for
ρ ≤ 1.3, θ = 1 for ρ ≥ 1.4 (`escPermanentCRRA.csv`). `test_esc.py` now ~80–100 s (sections 10, 13, 14).

## 2026-09-12 — one hours unit across countries (C4)

`addEigenVectors` now scales both eigenvectors to γ·y = 1, so the vector-X hours unit
μ = ∑γ_i y^x_i is 1 everywhere instead of scipy's unit-norm value (US 0.5593, FR 0.5590, UK 0.5770) --
the same normalisation the Argentina models impose. It is the eq (hoursUnit) rescaling, so only h̄ and
h_i move: the re-swept vector-X grids reproduce β, ω, R, τ, sr and h to ≤1.6e-13 at every ρ, h̄ scales by
1/μ_US (ratio 1.788), and the μ_c/μ_US that ModelFR's Γ_h rescaling used to hide in X̄_c/X̄_US now sits in
λ where it belongs (UK λ 0.8367 → 0.8632 at ρ = 1, the 3% TODO C4 named; FR 0.8934 → 0.8930). Docs:
`writing/US/model_calibration.tex` (both normalisations now stated, and the h̄-comparability remark).
`test_ee.py`'s h̄ ≠ h check was degenerate under μ = 1 and became the two aggregation identities plus
h̄/h = μ, with the commonX instance (μ = 0.963) as the non-normalised control. Sweeps:
`logs/usVectorX0912.log`, ~20 min; the ESC leg runs under common X and was not touched.

## 2026-09-12 (night) — stationary vs date-specific policy functions (prepub check)

`stationaryApprox.py`: the exact CRRA recursion against a policy function solved with ν frozen at each
date's value (40-period recursion, first period read, convergence checked over the visited states -- the
bottom of the s grid never settles, ~1e-4, and is excluded), walked along the projected path from the exact
initial state; plus the steady-state PEE tax τ*(ν_t) and one long-run function. At ρ ∈ {0.5, 0.7, 1.3,
1.5, 2}: the date-by-date stationary walk misses the exact tax by ≤ 0.17 p.p. (2020), the steady-state
comparison by ≤ 0.20 p.p., the sign flipping at ρ = 1 (exact by the decoupling); one long-run function is
6–8 p.p. off before 2050. The terminal period is 3.5–9.7 p.p. too high, the one before ≤ 0.26 p.p.
`stationaryApproxESC.py`: the same for the leaded design under the wedge, LOG (`ESC.solveBackward` on the
frozen copy) and exact 2-D CRRA (`ESCC2.solvePolicies` on the baseline's s grid, ~5 min each): the design
in force is misplaced by ≤ 0.005 (LOG) and ≤ 0.016 (CRRA, 1990 at ρ = 2, where the frozen recursion itself
only settles to 0.015 -- the flat objective); the tax by ≤ 0.21 p.p. `results/numerical/US_*.csv`,
`logs/*Stationary*0912.log`; wired as prepub entries of `python/paper/runShocksUS.py`.

## 2026-09-22 — a UK host for the French-characteristics shocks

`runShocksUS.py --host US|UK|UKUS`: the host is rebuilt from its sweep row (`hostModel`; on a ModelFR
`setUSRef` for β, then X or `rescaleX(λ)`), asserted to reproduce the sweep's own τ (not the workbook
target: under CRRA the vector-X rescaling drift of `hoursDriftTol` sits in the recorded τ). The one model
change: `shocks.ηLevel` preserves the host's Γ_h instead of resetting it to 1 -- on a calibrated vector-X
ModelFR Γ_h = λ, and the old assertion would have undone the UK's hours calibration (`test_eu.py`, 4 new
checks). `testEU.load` takes any sheet suffix and names a missing sheet; `calibrateRhoGridEU.py --country FR
--grouping UK` sweeps `FRUK` (16/16 both variants, ω identical to France's US-cut value). On the UK, France's
income distribution *raises* τ (+0.3 p.p., France the more unequal at the UK's cuts) under common X and
lowers it (−0.5) under vector X. `logs/ukusSmoke0922.log`, `frukSweep0922.log`, `ukShocks0922.log`,
`frFix0922.log`, `escCrraFrFix0922.log` (the exact CRRA leg re-run after the hours fix, ~1.5 h).

## 2026-09-24 — the `'size'` wedge f(θ, τ) (WP2 and WP4 of `archive/notes/plan_escSizeLeak.md`)

`Base.fWedge/wedgeA/wedgeB(θ, τ, t, lag)` gain the spec `'size'`; `Vtilde(t, lag)` memoised and zero-mass
masked; `dlnfWedge_dτ`; τ passed at every call site (same-date pairs); `dlnc2i_dτ` × (1+τ∂τ ln f); `model.py`'s
`EE_report` passes τ to `bi`. `calibrateWedge` brackets per spec (`WEDGE_BRACKET`), λ in `wedgeP`. Every
`runESC.py` stage merges its csv (per-stage keys; a bool/NaN key-string defect that duplicated rows fixed);
calibration rows carry `Vtilde`, `fStar`, `f0`, `τ0`. `test_esc.py` 9–14: λ = 0 bitwise the no-wedge model,
the retirees' τ-derivative against a finite difference to 2.6e-10, Ṽ invariances to 1e-16, `'scale'` p =
0.4076119851 reproduced (~235 s now). Results, common X: λ = 8.643 (LOG; Ṽ 0.436, f(θ*) 0.982, f(0) 0.762,
R drift 2.9e-3), 18.24 (ρ 0.5) and 1.728 (ρ 2) exact, one sign change per scan (a coarse-grid inner failure at
one node each, skipped as designed); the two ρ ran in parallel through `--tag` (`logs/runEscSizeCrra0924.ps1`).
S4 fired: the path iteration (λ = 20.31, 1.917) separates from the exact choice by 0.031 (French voting, ρ 0.5) and 0.063/0.091 (voting, joint, ρ 2); 81 candidates move the exact choice ≤ 0.006, and at the exact λ the path iteration picks 0.717 at baseline, so it is the method's approximation, not the grid (`archive/pilots/escSizeLeak_S4_2026-09-25/`). Stationary check under `'size'` (`results/numerical/US_ESC_stationaryApprox.csv`): the ν-frozen policy misplaces the design in force by up to 0.053 (LOG), 0.042 (ρ 0.5) and 0.059 (ρ 2), against 0.005/0.016 under `'scale'`: the design now answers to the size of the system, which the frozen ν mis-states most at 2020–2050.

## 2026-09-29 — the UK as ESC host (`--host UK`)

`runESC.py --stage shocks --host UK` and `runESCcrra.py --exact --host UK` run the French scenarios on the
UK at its OWN λ (LOG from `escCountry.csv`; CRRA calibrated into `escCalibrationCRRAUK.csv`), France cut at
the UK's groups; `buildEU` seeds ω and passes ModelESC options, `runESCcrra.buildHost`, `frenchData`/
`franceRow` take the grouping, rows carry `host`, UK files carry it in their names; `collectESCexperiments.py
--host UK` -> `escExperimentsUK.csv`. UK λ = 15.089, 7.264, 2.786 at ρ = 0.5, 1, 2 (US 18.242, 8.643, 1.728);
every free baseline re-elects 0.5597. Trap: at ρ = 0.5 the UK's β-imposed calibration does not converge on
the ns = 50 scan grid (7.5e-4), so that ρ scans at 150 (~35 min per trial, 5 h in all). `test_esc.py` S15.

## 2026-09-30 — Frisch-elasticity robustness of the endogenous design (`runESCxi.py`)

New driver, LOG under 'size' and common X: per ξ the model is rebuilt with ξ in the workbook parameters (`buildUSxi` swaps it
into `testmod.pars` around `runESC.buildUS`, since η_i derive from it in the constructor), λ calibrated by `calibrateWedge`
with (β, ω, X) recalibrated at every trial, then runESC's path and acute-ageing code. θ* and Ṽ are ξ-free (asserted; gap
1.1e-16). Self-check at ξ = 0.3: λ, path and acute rows equal to the published ones bitwise. ξ = 0.2/0.3/0.4: λ = 8.736/
8.643/8.547, one sign change each, no corner; design 2050/2080/2110 0.798/0.805/0.809, 0.797/0.804/0.809, 0.796/0.804/0.809;
tax 2110 0.212/0.209/0.206; acute ageing chosen 0.825/0.825/0.826 (τ 2020 pinned 0.229/0.225/0.221, chosen 0.232/0.228/
0.224); R drift 2.0/2.9/3.7e-3 (the headline's fixed-point caveat). `results/esc/escXiRobustness.csv`, `logs/escXi.log`, 7.6 min.

## 2026-10-02 — the CRRA design choice moves a predetermined state (found by reading, nothing run)

While section 4 of the paper was being drafted: `LeadedCRRA2D._econAt` (policyESC.py 603–605) evaluates every
candidate θ_{t+1} with s_{t-1,i}/s_{t-1} recomputed at the candidate's own τ* and h_t, through B_t(R_t) under
ρ ≠ 1, so the design comparison includes a channel the electorate does not control. The tax FOC holds the ratio
fixed correctly; LOG is immune (B = β, and the tax does not see θ_{t+1}). The path iteration and `PermanentCRRA`
(level of past savings) share the class. Size unmeasured; RKB wants a new algorithm, designed in a fresh session:
`notes/esc_crraDesignChoiceProblem.md`, TODO C6. num_esc.tex line 8 states the opposite and is fixed with it.

## 2026-10-02 (later) — tax candidates tested and ranked at frozen savings shares (C7)

RKB's point on `num_robustroot.tex`: the integral of the consistent z_t along the tax grid moves the shares with
it, so it ranked candidates at different predetermined states and said nothing about multiplicity. Now every
candidate (both corners, every crossing) is tested and ranked on z_t re-evaluated at its own frozen shares and
integrated (`roots1d.selectMaxFrozen`; `LOG.objectiveFrozen`, `CRRA.objectiveFrozen`, with `focParts_t`/
`zAtShares` splitting the splines from the retirees' term so `focGrid_t` is bitwise what it was); the four US
solvers report `nCand`/`nEq`/`fallback` per state and `multiplicity` in `solvePEE_*`/`solveLeaded*`;
`solveRobust(check = True)` runs the full-grid pass on every log solve (+19 ms, 1.0 s per calibration) and keeps
the gradient solution bitwise when it is the selected equilibrium. Raw CRRA utility levels are NOT the right
frozen objective (the FOC carries smoothed derivatives; 140 spurious test failures at ρ = 2 before switching to
the integrated condition). `test_frozenSelection.py` (31 checks): the frozen objective's τ-derivative equals z_t
to 1e-6 (log) and 1e-9 (CRRA T); bitwise the earlier criterion wherever one equilibrium exists; one equilibrium at
every state, no fallback, at ρ = 1, 2, 0.5, in the leaded log recursion and one 2-D ESC period. Fast registry:
23 of 23 suites pass in 309 s (`logs/fastSuites_frozenSelection_1002.log`), `test_esc.py`'s pinned numbers
included. Nothing in `results/` re-run; checklist `notes/todo_finalRun_2026-10-02.md`.

## 2026-10-02 (pilot) — the two frozen-state design layers for the CRRA leaded choice, measured (C6)

`LeadedCRRA2D.solveBackward_t2D` is now `_periodCore` + `_choose` + `_handBack` (the unsplit period dict bitwise in one process; `tCore`/`tChoose` added). `policyESCpilot.py`: `LeadedCRRA2DRoot` (alg esc:crra2D, bisection of eq:esc:aResidual) and `LeadedCRRA2DFOC` (alg esc:crra2Dfoc, `selectMaxFrozen` on z^θ) override `_choose` only, sharing `frozenTaxPass`, `aOf`/`sharesFrom` (eq:esc:aDef, common βi asserted), `resolveAt`, `deviationCheck`; `test_designChoicePilot.py`, 13 checks. Measurements: `pilotDesignChoice.py`, `logs/pilotDesignChoice/pilotDesignChoice.csv`.
Root: one closed bracket and no fallback at every state of every run, deviation gain ≤ 0. Design in force at t0 0.7385/0.3366/0.7334 (ρ=2 baseline, ρ=2 French voting, ρ=0.5) against the earlier layer's 0.7383/0.3347/0.7364, and equal to it to 2e-6 at ρ=1.05. 5–9× the earlier layer's choice cost (23 min per recursion at ns=50 under load).
FOC: 0.8–1.5× the cost, and the least sensitive to the candidate grid (0.002 between 41 and 81 against 0.006 for root). But its fixed-knot θ' spline misses the young's slope by 18–23% (M4), its deviation gains reach 1.6e-5 relative, and its t0 design is off root by up to 0.023 (0.7152 at ρ=2). Not wired into any driver; nothing in `results/` re-run.

## 2026-10-02 (production) — the root layer is LeadedCRRA2D's design layer (C6)

`designRule = 'root'` (alg esc:crra2D, `_chooseRoot`) is the default; `'legacy'` (`_chooseLegacy`) stays for comparisons and pinned periods. `aOf`, `sharesFrom`, `frozenTaxPass` and helpers moved to `policyESC` (module level); `LeadedCRRA2DRoot` removed, the FOC layer stays in `policyESCpilot`.
Cost: `Ma = 5`, a bracketed secant (`_closeSecant`, Illinois + bisection safeguard; `aClose = 'bisection'` kept for T9), the cell-local crossing `_cellCrossing`. One period ρ=2 baseline ns=150 nCand=41: 458 → 126 frozen passes, 0.477 → 0.400 s per pass, root/legacy tChoose 5.46 → 1.06; θ' equals the pilot's to 1.4e-12 (bitwise in one process at Ma 9, bisection). `logs/designChoiceProduction/`.
Counts: `LeadedCRRA2D.multiplicity` (tax + design, `policy.DESIGN_NAMES`, -1 = not counted) from `solvePolicies`/`solveLeaded2D`; `runESCcrra.py --designRule/--Ma`, its rows carry both and six counts (`solverColumns`); the other drivers the tax counts (`policy.multiplicityColumns`); `config.US['esc']` designRule/Ma forwarded by both paper stages. `test_designChoicePilot.py` T8–T11 (22 checks); `test_frozenSelection.py` §5 now runs `'legacy'`.
M7/M8 (ρ=2 French voting, ns=50, `pilotDesignChoice.py --item M78`): resolveAt instead of the grid reading moves θ' by 2.6e-6 at (s0, θ*) (6.5e-3 at worst over states); nθ2D 21 vs 13 by 6.3e-4. Nothing in `results/` re-run.

## 2026-10-02 (evening) — the equilibrium test's cell clause, and two edge cases of the frozen objective

`roots1d.selectMaxFrozen` (gridsearch log, same date): the one-cell form of eq:equilibriumTest now applies only to a
crossing whose stencil touches an infeasible cell, a crossing also passes when its nearest node attains its own
objective's maximum, and passing candidates within a cell merge into one equilibrium (`nEqRaw`, `nMerged`). Found on
the Argentine instances (TODO C7); the US checks are unchanged. `CRRA.objectiveFrozen`: hours read at the node for a
candidate sitting on one (an upper feasible end next to an infeasible cell no longer drops out), and `ln c` as the
retirees' level at ρ = 1 (the terminal period now selects instead of falling back; τ bitwise). `test_frozenSelection.py`
33 checks. The final run of both arms restarted after it (`logs/finalRun1002/`).

## 2026-10-03 — the final run's US arm read (C6 closed)

`logs/finalRun1002/US_stage{1,2}.log`, 19:57 → 09:50; the four exact CRRA costs took 1.7–2.3 h each under `designRule
= 'root'`, `Ma = 5`. Exact λ against the earlier layer: US 18.242 → 18.267 (ρ = 0.5), 1.728 → 1.724 (ρ = 2); UK
15.089 → 15.117, 2.786 → 2.777; scan brackets unchanged. Design counts 1/1/0 (`nEqθMax`, `nBrθMax`, `nFallbackθ`) at
every chosen row of the five CRRA esc files; tax counts nEq = 1, no fallback wherever counted (−1 on the calibration
grids, the EE-only files and pinned rows). Designs moved ≤ 1.3e-3 (French voting, ρ = 2; ≤ 4e-4 at ρ = 0.5; UK
≤ 3e-4), taxes ≤ 7e-5, workweek ≤ 1.2e-3 h, design path ≤ 6e-4, stationary misplacement 0.042/0.059 and the placebo
unchanged at the printed precision; exact-vs-path gaps 0.031 (ρ = 0.5) and 0.061/0.090 (ρ = 2). LOG rows within 1e-11
(#1). `escPermanentCRRA.csv` aligns on no key after its label change (read by no output). `num_esc.tex` checks list
filled (items 8–11, 15, 17, 18); README status updated; `compareResults.py` listed in `python/paper/README.md`.
