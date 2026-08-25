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
