# Research log — US

Model-specific session log. Structure/design conventions live in this folder's `README.md` (check there
first — this log is for history and open decisions, not current state).

## 2026-08-21 — documentation, written before any code

`writing/US/` (namespace `us`, exogenous `θ`): `model*.tex` + `num*.tex`, following `informalAnalytical`'s
file split. The model is that one with the informal type removed, so most of the tex is a copy with the
`j=0` terms deleted and `κ_t` collapsed to `p_t`.

Two results came out of writing the derivation rather than out of running anything, and both changed the
code that followed:

- **The LOG first-order condition decouples across time**, `z_t = z_t(τ_t)` (`eq:PEELOG:decoupling`). In
  the informal models the old informal household's indirect utility depends on the *level* of `Θ_{h,t}`,
  which carries `τ_{t+1}` through `Γ_{s,t}`; that is the only such term, so removing the household leaves
  every term a function of `τ_t` alone. The PEE path is `T` independent scalar problems with a diagonal
  Jacobian. Verified exactly (`max|dz_t| = 0`) in `test_ee.py`, with a control check so it is not vacuous.
- **There are two invariances, not one.** With `y^η = η^{1+ξ}/X^ξ` and `y^x = (η/X)^ξ`, every aggregate
  uses `y^η` alone. Scale (`λ`: `y^η → λy^η`) moves levels; hours unit (`μ`: `y^x → μy^x` at fixed `y^η`)
  moves `h_i` and the workweek `h̄` and **nothing else, including aggregate `h`**.

**A normalisation I got wrong first.** The first draft of the common-`X` variant moved the normalisation
off `Γ_h = 1` and onto `∑γ_iη_i = 1`, on the reasoning that the hours target identifies the scale. It does
not — it identifies the hours *unit*. Both variants normalise `Γ_h = 1`, exactly as the Argentina models
do; they differ only in whether `μ` is left arbitrary (vector `X_i`) or pinned by average hours (common
`X`). Aggregate `h` cannot serve as that target, because `h` does not respond to `μ` at all.

**A typo in both parent docs, left unfixed there.** `writing/informalAnalytical/model_setup.tex:108` and
`writing/informalSavings/model_setup.tex:102` write the labour-supply FOC's pension term as
`θ_{t+1}·b̄_{t+1}`, undiscounted, while the savings equation on the next line discounts. It should be
`θ_{t+1}·b̄_{t+1}/(R_{t+1}/p_t)`; the equilibrium expression in each file already implies exactly that. It
is confined to that one line in each and nothing downstream inherits it. The US doc has it right.

**`θ = 2 − 1/RR` is the idea, not the computation.** That closed form holds only if the income groups sit
at exactly half-mean and mean. They sit at `z^η = (0.507, 1.001)`, and the difference matters: the general
formula gives 0.738 (the paper's number), the idealised one 0.745. `getθ` uses the general one.

## 2026-08-21 (cont'd) — code

`base.py`/`policy.py`/`model.py` copied from `informalAnalytical` and adjusted, per the
self-contained-per-module convention.

- **The `j=0` slot stays, with `γ_0 = 0`** — the workbook's own `Readme` sheet says the data are laid out
  that way. Its terms are computed and multiplied by zero. Synthetic `η_0`/`X_0` must stay **finite**:
  `0·NaN` is `NaN` and would poison the whole FOC. `test_ee.py` perturbs the slot to check it is inert.
- **`getEps` raises if `γ_0 > 0`.** `db['Ushare0']` (0.287, the universal share of US transfers) is not
  the Argentina models' `ε`, and with zero mass nothing distinguishes them; the guard is there so the
  platform-work extension cannot inherit a plausible-looking number that was never derived.
- **Calibration is 2-D**, `(β, ω)` against `R_{t0}` and `τ_{t0}`. The savings rate is still reported —
  0.1537, untargeted and plausible — but is no longer a target.

**The `Γs` bracket: a constant that was safe by parameter values, not by construction.**
`steadyState_CRRA_solve` inherited a fixed bracket `(1e-6, 0.75)`. `Θ_h`'s denominator vanishes at
`Base.ΓsCap = Γ_h·α·κ/((1-α)·p·θ·τ)`, which scales with `α/(1-α)` — 0.75 for Argentina against 0.43 here —
and with `κ/p`, above one there and exactly one here. At US parameters the cap falls to ≈0.58 as `τ→1`,
below the constant, and `steadyStatePEE_CRRA` searches `τ` across all of `[l,u]`, so CRRA died on a NaN
with a message pointing at the solver rather than at the bracket. `steadyState_CRRA_bounds` now ties the
bracket to the model. `test_crra.py` asserts the bracket *tracks the cap* rather than that any number
works — retuning the constant would only move the `τ` at which it reappears. Same shape as
`notes/crossCuttingFindings.md` #7.

**Validation.** The vector-`X` calibration reproduces the *commented-out* column of
`writing/Paper/Tables/USUKFRCalibration.tex`: `θ` 0.7382 vs 0.74, `ω` 1.4536 vs 1.45, `η_H/η_L` 3.733 vs
3.73, `γ`-weighted mean `X` 10.88 vs 10.9. The first three are scale-invariant and are the real evidence;
the `X` match is at the eigenvector routine's own arbitrary normalisation, so it says the two codebases
call the same eigensolver, not that they agree about economics. The **live** column (`θ` 0.83, `ω` 1.42,
`X` 3.4, `η_H/η_L` 4.32) is a different vintage and is not reproduced — and since `θ` is closed-form in
`RR` and `z^η` with no model object entering, that gap has to be input data, not solver behaviour.

**Open, for whoever writes the paper table.** Its `X` row is labelled *"Target: Avg. workweek"*, but under
vector `X` the workweek is not a target and `X`'s level is arbitrary — yet the commented values match
vector `X`. An `X` actually calibrated to the workweek is ≈4.15 (vector `X` with the target imposed) or
4.03 (common `X`), not 10.9.

## 2026-08-21 (cont'd) — the ρ sweep, and the policy smoother's knots

Added `calibratePoint`/`calibrateGrid` (ported from `InformalSavings`, minus the `ι` state and the
occupancy diagnostic) and `calibrateRhoGrid.py`. `ns`, `interpKind` and `smoothKnots` became first-class
grid settings so a sweep can refine them through `initGS` in one place.

**`notes/crossCuttingFindings.md` #4 ended with "`informalAnalytical` … has not been checked for this."
This sweep is that check, and it found #5, not #4.** The policy smoother was using FITPACK's adaptive knot
count — chosen from the data, so it flips as a parameter moves and puts jumps in a residual that is about
to be differentiated. Measured at ρ=0.5, the hardest point, over `ns ∈ {50,75,100,150}`:

| smoother | β across ns |
|---|---|
| adaptive | 1.4347, 1.4395, 1.4391, 1.4369 — a 0.3%-wide band, **no trend** |
| pinned (`smoothKnots=4`) | 1.4698, 1.4420, 1.4375, 1.4354 — **monotone**; then 1.4354 / 1.4353 / 1.4355 at ns = 200/250/300 |

Two things worth carrying forward:

- **Judge by the trend, not the spread.** The converging sequence has the *wider* range, so a
  spread-of-answers metric ranks it worse. That is how this was nearly dismissed.
- **The adaptive smoother was masking the error, not avoiding it.** It put every `ns` inside one band, so
  refinement could never reveal that `ns=50` is 2.4% off. A band with no trend is not a small error bar;
  it is the absence of information.

**#4's own fix was tested and not adopted.** `cubic` at pinned knots reproduces linear's behaviour while
failing to converge in 2 of 8 cells — #4's overshoot caution. `pchip` *is* affordable here (all
interpolants are 1-D; the 1400× cost that blocked it in `InformalSavings` is a 2-D problem) and agrees
with linear at ns=150 — 1.43527 vs 1.43536, inside linear's own settled band, so a genuine independent
confirmation of the value — but fails at ns=50 and 75, which a march cannot afford. Settled on **linear +
pinned knots**, `ns=150` for calibration and `ns=50` for a plain solve.

**Results.** Both variants, `ρ ∈ [0.5, 2.0]` step 0.1, 16/16 each, ~4.5 min, residuals ≤ 6.6e-12.
`results/calibration/US_rhoGrid{,CommonX}.csv` + per-point pickles + logs. `β` falls 1.4354 → 0.5563, `ω`
2.3156 → 1.1934, the untargeted savings rate 0.1591 → 0.1485. Three checks fell out of running both
variants: `β`/`ω`/`sr`/`h` agree across variants to ~1e-13 at every `ρ` (block-recursivity confirmed end to
end, not just at the calibration year); `R` and `τ` are constant down both csvs; and `h̄` is pinned at
machine precision under common `X` while drifting 1.0e-3 under vector `X`.

**How to read `verifyResidual`.** The `ρ=1` row is uninformative — LOG has no inner state grid and
`solveVectorized` does not touch the `τ` grid, so it comes back equal to the residual by construction. On
CRRA rows it *overstates* the uncertainty: ~7e-4 at ρ=0.5 across every `ns` from 100 to 300, while `β`
itself is settled to 1e-4. It measures how far the residual moves under a 1.5× grid change at fixed
parameters, which does not vanish because the parameters converged. A level across points, not an error bar.

## Open (as of 2026-08-21 — superseded by the 2026-08-22 entry below; read that list instead)

- ~~**Shock/counterfactual experiments are untouched.**~~ Done 2026-08-22, with `test_createCopyFromt0.py`.
- ~~**`python/paper/` is not wired to this module.**~~ Done 2026-08-22; 12 outputs wired.
- **`η_H/η_L` differs between the calibration variants** (3.733 vs 3.080) — still open. Not a units
  artifact (the ratio is `μ`-invariant) but a real consequence of the identification. Common `X`
  over-predicts the hours gradient by 21.2% (1.401 against 1.156 in the data), which is the price of the
  restriction and the diagnostic `model_calibration.tex` says to report.
- ~~Only the US is calibrated; France and the UK need their own workbooks.~~ Both landed 2026-08-22 and
  are calibrated and swept. France's `θ = 1` needed no code — `getθ` returns exactly 1 at `RR0 = 1`.

## 2026-08-22 — France/UK (`ModelFR`), the counterfactuals, and the paper pipeline

A long session. Four things, in order.

### 1. `ModelFR(ModelUS)` — the France/UK calibration protocol

Only the calibration methods differ, as the paper states (`Quant.tex`): β is **imposed** at the US value
at the same ρ (so the `R` target goes with it, and `eq:calibration` collapses to a 1-D root over ω against
`τ_{t0}`), and average hours are targeted in **both** variants at `h̄_FR = h̄_US·ww_FR/ww_US`.

The structural fact that made this small: **proportional `X_i` scaling *is* the documented scale
invariance.** `test_invariance.py`'s `rescale(λ)` already applies exactly `X → λ^{-1/ξ}X` at fixed η. So λ
is block-recursive to the ω root — τ, R, w, θ, `s_i/s` and the savings rate are pointwise invariant —
closed-form `λ = h̄*/h̄`, applied *after* the root exactly like `commonX`'s `X`. Three hooks opened in
`model.py` (`hbarTarget`, `_calResidual`, `_calPostRoot`) so each override changes one thing in one place;
the existing suites were unaffected.

France's `θ = 1` needed **no code**: `getθ` returns exactly 1 at `RR0 = 1` for any grouping, which is why
France's groups may be cut at US percentiles.

**`test_fr.py` needs no country data.** Fed the US workbook with the US's own β and a workweek ratio of 1,
the protocol becomes an identity: `ω_FR = ω_US`, `λ = 1`, and **`R` lands on `R0` although nothing targets
it** — that last one says the two-target US root and the one-target FR root found the same point, which is
what "impose β from the US" has to mean.

**A real bug the test caught: λ was an increment, not a level.** `rescaleX` multiplies the `X_i` already in
db, so a repeated `calibrate` — or the next point of a march, which reuses one instance — reported the
small step from the previous solution rather than the total rescaling (λ = 0.893 then 1.000 then 1.000).
Every other column was right either way, because the target is absolute and the rescaling reaches it from
wherever it starts. That is what made it worth pinning: **the wrong λ is plausible and lands everything
else on target.** `calibrate` now resets productivity to the `Γ_h = 1` baseline first, so `λ = Γ_h` exactly.

Note this bug only existed *because* `Γ_h` is not arbitrary here. Under `ModelUS` it is a free
normalisation; under `ModelFR` the hours target pins it, so it is data-determined and its level matters.
I had described it as arbitrary and was corrected — worth recording, since the correction is what made the
λ bug findable.

### 2. The sweeps

`calibrateRhoGridEU.py`, mirroring the US driver with three differences: a 1-D search vector (one `x0`
column, β a *recorded* column); every visited ρ must exist in the US sweep csv, validated **before** the
march since `USReference` refuses to interpolate; and `--maxHalvings` defaults to 0, because step-halving
would insert intermediate ρ with no US row. `usRefFromCsv` became a `USReference` class rather than a
closure so a swept instance pickles.

All six sweeps (FR/UK/UKUS × two variants) solved 16/16, residuals ≤ 1.4e-14. **β reproduces the US sweep
exactly (0.0e+00) in all six.** ω agrees across variants (block recursivity). τ is constant to 1e-14 under
common `X` and 1e-4 under vector `X` — the difference is precisely the rescaling drift, since only vector
`X` carries a rescaling.

**How exactly the rescaling can hold under CRRA.** Exact under LOG (2e-16); not under CRRA, because
`defaultSGrid` floors the state grid at an absolute `1e-4` while `1.25·sMax` moves with the model.
Measured at ρ=0.8 over λ=0.89: |Δτ| = 9.6e-5 / 1.30e-4 / 1.37e-4 / 1.40e-4 at ns = 50/150/300/600 — it
**plateaus**, which locates the cause in the bound rather than in resolution; a diagnostic floor of
`1e-4·sMax` gives 7e-16 at every ns. **The floor stays absolute** — every model can reach exact zero, so
that region must simply not be searched, and the floor must not depend on the model's scale. The cost is
bounded (≤ 2.5e-4, inside the solver's own ~6e-4 `verifyResidual`) and is *recorded* as `hoursDrift`
rather than asserted away. For the record: a proportional floor would move β by 0.65% at ρ=0.5 and require
re-running the US sweep.

### 3. The counterfactuals

`shocks.py` + `runShocksUS.py`. θ ∈ {0,1}, mild/acute ageing, and France's η/X/μ, at ρ ∈ {0.5, 1, 2}, each
as a full effect and an economic-equilibrium-only effect, on `createCopyFromt0(t0)` — which got its own
test suite here first (37 checks; the no-shock round trip reproduces the baseline tail to ~1e-12).

**τ and the savings rate reproduce the paper exactly on all 14 rows at ρ=1.** Three conventions had to be
recovered to get there, and each is now documented where it is applied:

- The paper's savings rate is **`s/(w·h)`**, not `s/Y`; they differ by `(1-α)`.
- The workweek is normalised against the baseline per ρ; `h̄` has no identified level.
- `db['dates']` is **stale on a copy** — full original calendar on a shorter, renumbered horizon, because
  `Index.union` drops the name so `_sliceDb` never sees it.

**What the French counterfactuals mean.** Under vector `X`, `y^η ∝ z^η` and every aggregate uses `y^η`
alone, so "swap `z^η` and re-derive" and "take France's whole `(η, X)`" are the *same* experiment (τ =
13.79%). Only holding `X_i` fixed while η moves is different — and it reproduces the paper (13.28% /
22.75%). That makes the decomposition coherent: η carries income distribution, the level of `X` carries
leisure. Leisure is then a pure scale, which is why the paper's row has τ and sr exactly at baseline.

**Two findings inside that.** The income row moves `θ` 0.738 → 0.495 (`updateAuxPars` re-derives it holding
`RR0` fixed), so it bundles a pension-design change with the inequality change; `--pinTheta` keeps the
alternative (12.83%) on disk. And **`shockTheta` first returned the baseline for both polar cases** —
`updateAuxPars` re-derived θ straight back. Now `notes/crossCuttingFindings.md` #9, because the null result
reads as a conclusion rather than as a bug.

The one thing that did *not* reproduce: the workweek column on full-effect rows (0.4–2.5% off; exact on
the ageing EE rows). τ and sr are hours-unit-invariant and match everywhere, so the gap is in the
conversion, not the equilibrium. Unattributed. For the leisure row the cause *is* known — 34.74 is the
pure-scale answer, 35.10 is what an inherited `s_{t0-1}` gives, and the scale invariance requires `s_0` at
the model's own steady state, which an unanticipated shock cannot have.

### 4. The pipeline

`python/paper/` gained a second arm: `runCalibrationUS.py`, `runShocksUS.py`, `tablesUS.py`,
`figuresUS.py`, a `US` spec in `config.py`, and 12 new entries in `build.py`'s registry. 17 outputs build
in ~5 s. Contracts verified rather than assumed: stages (i)/(ii) skip what exists, stage (iii) is
idempotent and does not re-back-up, and with `US_shocks.csv` removed the seven shock-derived outputs
report BLOCKED while the four calibration-derived ones stay OK.

**Stage (i) is order-dependent here and is not in the Argentina arm** — FR/UK read the US β and refuse to
interpolate, so `runCalibrationUS.py` enforces that the US sweep is complete before any European one
starts, rather than trusting loop order.

The common-`X` shock run is a **check** as much as an output: θ, ageing and voting must come back identical
to vector `X` (they touch neither η nor `X`), while income distribution and leisure must differ.
Measured: ≤ 4e-15 for the first group, up to 7.9e-3 in τ and 1.48 hours for the second.

Also caught: `config.pct` escapes the percent for tex, so the figure legend rendered a literal backslash.
Anything drawn *into* a figure needs plain formatting.

### Open

- **Endogenous `θ`** — the next piece of work, deliberately deferred.
- The workweek full-effect gap against the paper.
- The UK's `X_i` are uniformly 1.108× the paper's while `η_i` matches exactly — purely the λ degree of
  freedom. Relatedly, the paper's own two UK tables disagree: `UK_householdheterogeneity` implies
  `η_H/η_L = 3.88`, `USUKFRCalibration` says 2.73/2.85. This code gives 3.868.
- The live `US_CRRA_Ageing.tex` disagrees with the live `US_Ageing.tex` at ρ=1 for the same scenario
  (16.33% vs 18.45% for mild ageing). This code gives 18.45%, siding with the LOG table; the ρ=0.5 row of
  the CRRA table (18.62%/23.47%) it reproduces exactly. Mixed vintages within one table.

## 2026-08-23 — endogenous `θ`: the leaded choice under a deadweight wedge (A+B)

The appendix (`writing/Paper/Appendix/EndogenousSystemCharacteristics.tex`) reports that the sequential,
leaded and permanent choices of `θ` all corner at `θ = 0`, and that only the deadweight-wedge formulation
is interior. This session implemented the **leaded choice with the wedge** — the combination the appendix
never runs — and measured what it delivers.

### What was built

`base.py` gained two hooks, `wedgeA(θ)`/`wedgeB(θ)`, and nothing else changed there. The whole wedge is the
substitution `θ → A(θ)`, `(1-θ) → B(θ)` in `Γs`, `Θh`, `si_s`, `c1i`, `tildec1i`, `c2i`, `dlnc2i_dτ`,
`ΓsCap`, `BSteadyState` — because in *every* equilibrium object `θ_{t+1}` appears only multiplying
`(1-α)/α·τ_{t+1}`. `bbar` stays gross; the lost share is implicit in `A+B < 1`. Two specs:

| | `A(θ)` | `B(θ)` | |
|---|---|---|---|
| `scale` | `f(θ)θ` | `f(θ)(1-θ)` | the appendix's live spec |
| `flat` | `θ` | `f(θ)(1-θ)` | MGE's commented variant |

`policyESC.py` (`LeadedLOG`, `LeadedCRRA`), `modelESC.py` (`ModelESC`), `test_esc.py` (22 checks, in
`runTests.py`), drivers `runESC.py` / `runESCcrra.py`, results in `results/esc/`.

### Three structural findings, all measured rather than assumed

1. **`z_t` depends on `(τ_t, θ_t)` alone**, wedge or no wedge: `θ_{t+1}` reaches the FOC only through
   `Θ_{h,t}` → `dv20`, whose weight is `γ_0 = 0`. So `τ_t = τPolicy_t(θ_t)` is a *static* scalar problem and
   the two choices at `t` are separable. This is what makes the LOG leaded solve cheap.
2. **Under LOG the leaded choice has no state at all.** `θPolicy_t(θ_t)` comes back constant across the
   whole `[0,1]` state grid, to machine precision, at every period. `ln h_t`, `ln c̃_{1,t}^i` and
   `ln R_{t+1}` are each *additively* separable in `τ_t` and `θ_{t+1}`, so `W_t = A(τ_t) + B(θ_{t+1})`, and
   `θ_t` reaches `W_t` only through `τ_t`. The appendix treats `θ_t` as a state under this timing; under
   LOG it is not one.
3. The choice is invariant to `s_{t-1}` (the appendix's own normalisation), verified numerically.

### The wedge does escape the corner, and calibrates to the appendix's own number

Without a wedge the leaded choice is `θ = 0` at every state — the appendix's result, reproduced
independently. With it, `θPolicy_{t0}(θ*) = θ*` calibrates cleanly (residual 4.9e-8) at

| spec | φ=0.25 | φ=0.5 | φ=0.75 |
|---|---|---|---|
| `scale` | 0.257 | **0.402** | 0.942 |
| `flat` | 0.438 | 0.702 | 1.854 |

`scale`/φ=0.5 gives **p = 0.402 against the appendix's 0.41** from the *sequential* calibration — the two
timings need almost the same wedge. The nested calibration's own approximation (β,ω calibrated at
exogenous `θ`) is verified by `targetDrift`: 9e-15 in τ, 2.6e-9 in R.

`flat` is the better-behaved spec: `scale` reaches the `θ=1` corner by p≈0.7, so its calibrated point sits
close to a boundary in p-space, while `flat` stays interior across the whole scanned range. Under `flat`,
θ is jointly identified with p (f does not cancel in the replacement-rate ratio) and `getθ` becomes a
scalar root — `θ* = 0.716` at φ=0.5 rather than 0.738.

### What it predicts — and where it fails

**Ageing raises `θ`, as figure 1.1 and the paper's own conjecture say.** Along the calibrated path
(`scale`, φ=0.5) `ν` falls 1.34 → 1.07 and the chosen design rises 0.738 → 0.754 → 0.764. Acute ageing
dated 2020 moves the 2050 design to 0.775.

**But the magnitudes are the wrong way round.** Sweeping one axis at a time (`stageFig1`):

| axis | range | `θ` chosen |
|---|---|---|
| `ν` (population growth) | 1.55 → 0.95 | 0.723 → 0.780 |
| inequality (`η` spread) | `η_H/η_L` 3.73 → 2.44 | 0.738 → **1.000** |

At France's `η_H/η_L = 2.44` the model picks `θ = 1.00`, which is exactly France's observed design — but it
gets there through **inequality**, and moving `ν` from the US's 1.34 to France's 0.97 buys only +0.05 of the
+0.26 US→France gap. Figure 1.1 reports the opposite ranking: a clear cross-country relation of `θ` with
population growth and **none** with the Gini.

So the mechanism reproduces the CondeRuizP07-style prediction that the paper's own introduction says the
data reject. French voting patterns push the other way (`θ` → 0.536 alone; the two together give 1.000
under `scale`, 0.828 under `flat`), so the offsetting story is real but does not rescue the ranking.

**Cross-country, one common wedge does not order the three countries.** With the US-calibrated p = 0.402:
France chooses `θ = 1.00` (data 1.00 ✓), the UK chooses `θ = 1.00` (data 0.56 ✗). Matching the UK needs its
own, much smaller wedge (p = 0.186 vs 0.402). France's own p has no interior solution — its choice is at the
corner for every p in the bracket, which `calibrateWedge` reports rather than papering over.

### Open

- The inequality-vs-ageing magnitude problem above is the substantive obstacle, not a numerical one.
  Any mechanism whose force is within-cohort redistribution will tie `θ` to inequality; matching figure 1.1
  needs one whose primary driver is the age structure.
- The UK under a common wedge.
- CRRA: see the next entry / `results/esc/*CRRA*`.

## 2026-08-23 (cont.) — CRRA, and the permanent choice

### CRRA (`LeadedCRRA`, ρ = 2)

None of the LOG simplifications survive CRRA, so the solver iterates on the equilibrium **path**,
re-solving the whole PEE at every candidate design (which is also what makes the envelope logic right: τ_t
is re-optimised at each candidate). Its one assumption — that the choice at t+1 does not respond to the
design it inherits — is measured, not asserted: `dθ_{t+2}/dθ_{t+1} = −0.009` (`scale`), `−0.004` (`flat`).
Under LOG it is exactly zero, so the shortcut is sound at ρ = 2.

Validated against its own limit: as ρ → 1 the CRRA choice converges on `LeadedLOG`'s at a clean
first-order rate — gaps 0.0903 / 0.0448 / 0.0188 at ρ = 1.10 / 1.05 / 1.02, so gap/(ρ−1) = 0.90, 0.90,
0.94. Two solvers sharing only the objective's weights, agreeing where they must. Pinned in
`test_escCRRA.py` (slow suite).

| | LOG (ρ=1) | CRRA (ρ=2) |
|---|---|---|
| calibrated p (`scale`, φ=0.5) | 0.402 | **0.086** |
| θ chosen, 2080 | 0.7535 | 0.7834 |
| acute ageing → θ at t₀+1 | 0.7747 | **0.8149** |

A higher EIS needs **4.7× less wedge** to reach an interior design — the factor the `thetaStakes.py`
decomposition predicted from an entirely separate calculation — and roughly **doubles the ageing
response**. ρ = 2 helps the mechanism on both counts without changing the inequality-vs-ageing verdict.

*A test that passed for the wrong reason.* The first version of `test_escCRRA.py`'s state-sensitivity
check used the LOG-calibrated wedge at ρ = 2, which sits on the θ=1 corner — both perturbations return
1.0 and the slope is trivially zero. It now runs at ρ = 2's own p behind an explicit interiority
assertion. Worth remembering as a pattern: a *corner* makes any sensitivity check vacuous.

### The permanent choice (`PermanentLOG`, `PermanentCRRA`)

Two things make this cheaper than the appendix's recipe, and neither is obvious from the write-up (which
proposes a two-dimensional grid over `(τ_{t0}, θ)`):

1. **The joint choice concentrates.** `dW/dτ = 0` is the ordinary τ first-order condition evaluated at
   `θ_t = θ` — the permanent choice adds nothing to it, since θ is not a function of τ. So `τ*(θ) =
   τPolicy_{t0}(θ)`, already available, and what remains is a **one-dimensional** maximisation over θ.
   Verified in `test_esc.py`: τ at the chosen design equals `τPolicy(θ)` to 1e-6.
2. **τ_t for t > t₀ is the ordinary PEE at constant θ.** Once θ is fixed forever there is no recursion.

**The one thing that must not be got wrong.** `s_{t0-1,i}/s_{t0-1}` is predetermined, and here θ enters it
(through θ_{t0}) in a way it never does in the leaded problem. Maximising W while letting it move with the
candidate folds in a channel the policy maker takes as given — the same error `dlnc2i_dτ`'s docstring
forbids for τ. **It is not a small difference: 0.773 pinned against 0.910 moving**, at the same wedge. The
pinned reading is the default and is also what makes this the "unanticipated permanent reform" the
appendix describes; the other is exposed as a diagnostic and recorded in the output.

**Results.** Without a wedge the permanent choice corners at θ = 0 — the appendix's finding, reproduced.
With one it is interior, and the calibrated wedge is close to the other two timings:

| timing | p (`scale`, φ=0.5) | p (`flat`, φ=0.5) |
|---|---|---|
| sequential (the appendix's own) | 0.41 | — |
| leaded | 0.402 | 0.702 |
| **permanent** | **0.375** | **0.664** |

So **the required wedge is essentially timing-invariant** (~0.375–0.41), and at a common wedge the two
implemented timings deliver designs within ~0.04 of each other. The timing is second order; the wedge is
what does the work. That is worth saying in the appendix, which currently presents the timings as
alternatives with qualitatively different outcomes — they differ only in the *absence* of a wedge.

### The permanent timing is fragile in ρ, and the appendix does not report this

With no wedge the permanent objective is essentially **monotone** in θ (`nTurning = 0`), so the choice is
always a corner — and *which* corner flips inside the paper's own ρ range:

| ρ | 1.1 | 1.2 | 1.3 | 1.4 | 1.5 | 2.0 |
|---|---|---|---|---|---|---|
| θ permanent | 0 | 0 | 0 | **1** | **1** | **1** |
| W(1) − W(0) | −0.0065 | −0.0026 | −0.0005 | +0.0007 | +0.0014 | +0.0024 |

The appendix reports the θ = 0 corner because it works at ρ = 1. Above ρ ≈ 1.35 the sign reverses: with a
high EIS the young's resistance to taxation is low (the paper's own `Quant.tex` makes this point), so the
permanent choice's dominant channel is the future path of τ and capital — permanently higher θ means
permanently lower τ and more capital — and that beats the redistribution motive. Note the objective is
nearly flat between the corners near the flip (gaps of 5e-4), so this is a near-tie, not a sharp switch.

**Consequence for the wedge:** at ρ = 2 the permanent choice is already at θ = 1 *without* a wedge, and a
wedge that penalises Beveridgean design pushes it further that way. So under permanent + CRRA the wedge
cannot deliver an interior solution at all — the binding problem there is the opposite corner, and would
need something that penalises *Bismarckian* design instead.

### Open

- Sequential timing still not implemented (only its FOC appears in the appendix; the leaded and permanent
  solvers here would make it a small addition).
- The ρ-flip above deserves a decision: it makes the permanent specification unattractive as the paper's
  headline, since its qualitative result depends on a parameter the paper treats as robustness.

## 2026-08-24 — the true leaded CRRA solution (`LeadedCRRA2D`), and the counterfactuals across ρ

**The 2-D solver.** `policyESC.LeadedCRRA2D` computes the Markov object `LeadedCRRA`'s path iteration
approximates: policy functions `τ_t(s_{t-1}, θ_t)` and `θPolicy_t(s_{t-1}, θ_t)` by one direct backward
pass — terminal condition plus recursion, no warm start, no convergence tolerance. Design decisions
worth recording:

- It **subclasses `policy.CRRA` and overrides exactly one method** (`stateApprox_t`, the continuation
  evaluation) plus the assembly around it. The state fixed point, FOC assembly and selection are the
  parent's own, so the two solvers cannot drift apart. The `θ_t` axis is not carried through the big
  grid: `θ_t` enters only the current old's `dv2i` term, so the expensive numerical τ-derivatives are
  computed once per period and only that one term is rebuilt per `θ_t` node.
- **Pinning lives in the recursion, not the simulation.** Under CRRA `τ_t` responds to `θ_{t+1}`, so
  periods where the design is history (t ≤ t0) must be solved with the candidate set collapsed to the
  inherited design — the LOG habit of pinning only in `simulate()` would evaluate τ off the pinned
  continuation. This is also what makes the pinned-everywhere recursion collapse exactly to the
  exogenous-θ solver, which became check (b) in `test_escCRRA.py` (max|Δτ| < 5e-3 against
  `solvePEE_CRRA`, testing everything except the choice layer against production code).
- The planned warm start from the approximation was **not needed**: a direct recursion has no seed.
  The approximation's role inverted — it is the cheap method being *certified*, not the certifier.

**What the validation found (ρ = 2, calibrated wedge p = 0.0856, scale φ = 0.5).** The choice at t0 is
0.743–0.746 across grid refinements vs the path iteration's 0.738; long-run design 0.79–0.81 vs 0.795;
τ agrees to 2e-4 throughout. The W objective is flat enough near its maximum that *either* method pins
the design only to ±0.01 — consistent with the stake decomposition's finding that the design stakes
are second-order — and they agree within that band, so the path iteration is certified for the tables.
The grid sensitivities are the useful surprise: the s-grid is immaterial (choice moves 4e-4 from
ns=50→150; the choice is *nearly* state-independent in s even under CRRA), but the θ-STATE grid is not
(7 nodes misplace the choice by 0.02, 13 suffice). Cost ~70 s/period at ns=150, ~12 s at ns=50 —
cheaper per solve than one path iteration, but the path iteration is still cheaper inside shock loops
because copies shorten the horizon. Documented in `writing/US/num_esc.tex` (alg:esc:crra2D).

**Wedge calibrations at ρ = 0.5** (both specs, φ = 0.5, ~26/32 min): p = 0.9484 (scale, θ* = 0.7382),
p = 1.4447 (flat, θ* = 0.6911). With ρ = 2's 0.0856/0.169 and LOG's 0.402/0.702 this completes a clean
monotone picture: the wedge needed for an interior re-election of the observed design falls steeply in
the EIS. Merged into `results/esc/escCalibrationCRRA.csv`.

**Counterfactuals across ρ ∈ {0.5, 1, 2} × {scale, flat}** (acute ageing, French income distribution,
leisure, voting, and income+voting): ρ = 1 was already on disk (`escShocks.csv`, 2026-08-23);
the CRRA legs run via `runESCcrra.py --stage shocks` with the French scenarios newly wired in
(`SHOCKS_ESC` + `runShocksUS.frenchData` at the same ρ under CRRA, cached per ρ). Each leg writes its
own tagged `escShocksCRRA_exp*.csv` so concurrent runs cannot clobber one another (finding #8);
`collectESCexperiments.py` merges everything into `results/esc/escExperiments.csv` and prints the
per-spec pivots. Re-run the collector after any leg finishes — it is idempotent.

At ρ = 1 the pattern worth flagging: under `scale` the French income distribution drives the *chosen*
design to the θ = 1 corner (data-implied θ* is 0.495 — the electorate un-does the flattening entirely),
French voting weights pull it down to 0.536, and the two together still corner at 1 — the design
responds to inequality far more strongly than the cross-section does, now visible in the
counterfactuals themselves and not only in the fig-1.1 trace.

**Addendum (end of session): all legs finished.** 12/12 (ρ, spec) × scenario × reading combinations on
disk; merged table `results/esc/escExperiments.csv`, findings written up in
`notes/esc_experiments_acrossRho.md`. The cross-ρ headlines: acute ageing moves the chosen design
Bismarckian at every EIS (+0.04 at ρ=0.5 to +0.08 at ρ=2, scale); the French income distribution
corners the choice at θ=1 at *every* ρ under scale (data-implied θ* is 0.495) and erases most of the
pinned reading's savings-rate gain; the French voting profile is the one experiment whose strength is
sharply ρ-dependent (−0.07/−0.20/−0.46 across ρ), so the income+voting net effect flips from the θ=1
corner at ρ≤1 to interior 0.69 at ρ=2 — whether "French characteristics" raise or lower the
Bismarckian index is an EIS question. Leisure is a placebo at every ρ, as scale invariance requires.

**Addendum (pipeline session, same day).** Three module-side changes made for the paper pipeline (the
pipeline story itself is in `python/paper/RESEARCH_LOG.md`): (i) `runESC.mergeWrite`, used by both ESC
drivers' calib/path/shocks writes, so a run over one `(ρ, spec)` no longer clobbers the rest of a
shared csv — the defect behind this morning's tagged-file workaround; (ii) the tagged
`escShocksCRRA_exp*` csvs consolidated into one canonical `escShocksCRRA.csv` (80-row merge with the
pre-session mild/acute rows, deduped preferring the new runs; inputs preserved under
`results/esc/superseded/`); (iii) `collectESCexperiments.py` now reads exactly
`escShocks.csv` + `escShocksCRRA.csv` and is declared as the paper pipeline's `escExperiments` stage —
its output is the only file stage (iii) reads for the four experiment tables.

**Addendum 2 — the permanent-timing log entry `notes/todo_escPermanentTiming.md` item 3 asked for.**
The 2026-08-23 entry below justified pinning `s_{t0-1,i}/s_{t0-1}` at the incumbent design as an
"unanticipated permanent reform"; that justification is corrected here rather than by editing the dated
entry. The vote at `t0` is anticipated, so the savings made at `t0-1` were made against the design that
wins, and the equilibrium is the fixed point `θ* = argmax W(θ; siRatio(θ*))` — `solveFixedPoint`, now
`solvePermanent`'s default, with the incumbent pinning kept as the diagnostic and seed. Pinning itself
stays right (savings are sunk at the vote; a moving ratio breaks the concentration result); only the
value pinned at was wrong, and it is a no-op exactly at the calibration point, which is why every
calibrated `p` is common to both readings (0.375032266276 to 12 digits) and only counterfactuals
separate them. Full story: `notes/crossCuttingFindings.md` #11/#11b, `writing/US/num_esc.tex`
§ESC:permanent, root `RESEARCH_LOG.md` (cont. 2). Still open from that todo: `PermanentCRRA` has never
been executed since its restructuring, and `results/esc/escPermanent{,CRRA}.csv` are the
pre-timing-change vintage (`θPerm` there is the incumbent-pinned reading; the `converged`/
`θPermIncumbent` columns are missing) — regenerate via `runESC.py --stage permanent` /
`runESCcrra.py --stage permanent` before using any permanent-timing number.

## 2026-08-24 — every US counterfactual becomes a new equilibrium path, read at 2020

Decision, from the user: the US counterfactuals should not be unanticipated shocks. A row should describe
a country that has *always* had its mix of characteristics — mostly US, partly France — so that it is
commensurable with France's own calibrated path. That comparison is the point; a 2020 surprise is not
comparable with an equilibrium. Applied to both arms, the exogenous-θ main-text tables and the
endogenous-θ appendix, and the appendix tables now report at 2020 rather than 2050.

**What replaced what.** `shocks.shockedCopy` (`deepcopy`, warm starts cleared) instead of
`createCopyFromt0(t0)` seeded with `stateAtT0`; the changed parameters over the whole 1960–2200 horizon
instead of from 2020 on; the economy's own steady state instead of the baseline's savings; the readout at
`db['t0']` instead of the copy's renumbered position 0. `createCopyFromt0` itself stays — `thetaStakes.py`
wants exactly the local unanticipated perturbation, and the other two modules build on it.

**Measured before deciding, and it made the change cheap.** At ρ = 1 the convention moves the workweek
column and nothing else: τ and the savings rate agree to every printed digit across all seven scenarios.
Under LOG/Cobb-Douglas both are rate objects independent of the inherited capital stock, while the level
of hours responds to the wage and so to `k_2020`. The main-text tables are ρ = 1, so their headline
numbers did not move at all. This does not survive to CRRA and the ρ ∈ {0.5, 2} rows do move.

**It also resolved a standing discrepancy.** The leisure row is a pure `rescaleX`, and the scale
invariance requires `s_0` at the model's own steady state — which an unanticipated shock cannot have. It
used to give 35.10 against the paper's 34.72; the new path gives 34.74. The remaining full-effect workweek
gaps (up to ~2%) are still unattributed but are now known *not* to be the initial condition.

**The wedge calibration had to move one period back with the reporting.** `θ_t` is a state chosen at
`t-1`, so the design in force in 2020 is `θPolicy_1990`, not the choice made in 2020, and only the first
is what a 2020 table reads. On the old target (`θPolicy_{t0}(θ*) = θ*`) the freely simulated path came
back at **0.727** against the observed 0.738 — a 1.1pp miss in the baseline row of every comparison table.
`calibrateWedge` now targets `ModelESC.leadedDesignAtT0` (LOG) / `leadedDesignAtT0_CRRA` (CRRA, the same
13-candidate approximation relocated one slot). `p` moves 0.40220 → **0.40761** under `scale`, φ = 0.5,
ρ = 1; τ and R still land on target (drifts 2e-10, 5e-4). Under LOG the retarget is free of any fixed
point in the design's own history, because `prop:esc:separability` makes the policy state-free.

**What the 2020 tables now say** (`scale`, φ = 0.5, ρ = 1; exogenous θ → endogenous θ): acute ageing
0.738 → 0.778, mild 0.738 → 0.752, French voting 0.738 → 0.533, and the French income distribution — with
everything containing it — goes to the **θ = 1 corner**. The corner is a result: under France's flatter
distribution the electorate wants a fully Bismarckian system, which is where France's observed design
sits. France's own path is carried as the endpoint row under `scale`; under `flat` it fails by
construction, since that spec's joint `(θ, p)` inversion is not identified at `θ = 1`.

**The comparison the whole change is for** (ρ = 1, full effect, exogenous θ):

| | τ | savings rate | workweek | θ |
|---|---|---|---|---|
| US baseline | 14.43% | 21.96% | 39.39 | 0.738 |
| + all three French characteristics | 14.30% | 22.22% | 35.49 | 0.495 |
| France, own calibration | 21.29% | 19.19% | 35.44 | 1.000 |

The characteristics reproduce France's workweek almost exactly and close essentially none of the 7pp tax
gap. What is left over is France's own `ω` and its `θ = 1` design — a sharper statement than the previous
tables could make, and the reason the France row and the `frAll` row were added.

**One real bug fell out** (`model.steadyState_CRRA_bounds`, `notes/crossCuttingFindings.md` #7). With
`s0` no longer seeded, `solvePEE_CRRA` calls `steadyStatePEE_CRRA`, which searches τ over all of `[l, u]`.
At `θ = 0` — the θ = 0 counterfactual, now over the whole horizon — `ΓsCap` is infinite, so the
`min(0.75, 0.99·ΓsCap)` bound reverted to the bare constant, and at ρ = 2 the root sits above it. The
bound now expands geometrically, and only when the default has already failed to bracket, so it cannot
change a call that worked. Latent for as long as the old convention kept θ = 0 away from that solver.

Superseded results: `results/{shocks,esc}/preNewPath/`. Docs: `writing/US/num_esc.tex`
§ESC:counterfactuals (new) and §ESC:calibration (retargeted).

**Addendum — the CRRA re-run, and two defects it exposed.** All six wedge calibrations were recomputed
under the new target. `p` rises by 1.5–2% uniformly: 0.9484 → **0.9648**, 0.4022 → **0.4076**, 0.0856 →
**0.0901** under `scale` at ρ = 0.5, 1, 2, and 1.4447 → **1.4609**, 0.7022 → **0.7086**, 0.1692 →
**0.1775** under `flat`. The design response at 2020 turns out **monotone in ρ**: acute ageing takes θ
from 0.738 to 0.766 / 0.778 / 0.846, French voting drives it to 0.662 / 0.533 / 0.285, and the French
income distribution corners at θ = 1 at every ρ. Same ordering as the calibrated cost itself — a higher
elasticity strengthens the young's forward-looking stake, so the same characteristic change moves the
political outcome further and less friction is needed to hold the choice off the corner.

Two defects, both mine, both of the same kind — a registry or an interval that was correct only for the
case it was written against:

1. `shocks.shockedCopy` looked names up in `shocks.SHOCKS`, but `frBoth` lives only in
   `runESC.SHOCKS_ESC`. The old CRRA code called `SHOCKS_ESC[name][1]` directly; routing it through the
   new helper lost the registry and every `frBoth` row failed `KeyError` at ρ = 2. `shockedCopy` now
   takes an optional `registry`. Backfilled. The LOG driver was never affected — it passes the apply
   function in.
2. `runESCcrra`'s `--bracket` defaulted to `[0.01, 0.6]`, tuned at ρ = 2, and the ρ = 0.5 root is near
   1.0. Both specs reported "no sign change" — the scan doing exactly what `calibrateWedge`'s corner
   guard is for, rather than returning an endpoint. Default widened to `[0.01, 3.0]`, `nScan` 10 → 14.
   Worth noting the previous vintage of this csv had ρ = 0.5 rows, so someone had passed a wider bracket
   by hand and the default had been wrong the whole time.

The backfill gave a free check nothing was asserting: `frAll` and `frBoth` differ only by the leisure
scale, which is a pure `rescaleX`, so they must agree on design and tax and differ only in hours. At
ρ = 2 both give θ = 0.70676 and τ = 14.45%, with workweeks 36.04 and 40.47 — the scale invariance
holding through the endogenous-θ layer under CRRA.

Docs refreshed against the new runs: `writing/US/num_esc.tex` §The calibrated cost across ρ (all six
`p`), §CRRA (the 2-D-vs-path comparison re-measured at p = 0.0901: 0.759 vs 0.761, pinned reproduction
3.2e-5, drifts 3.2e-4/3.1e-4) and §scanned-not-bracketed (the interval must span every ρ). The
grid-refinement study behind the ±0.01 flatness claim was NOT re-run — it is a property of the
discretisation rather than of `p`, and both the tex and the README now say so instead of implying it was
measured at the current wedge.
