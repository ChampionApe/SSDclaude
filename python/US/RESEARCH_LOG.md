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
