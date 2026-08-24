# US

US model variant (see project overview in root `CLAUDE.md`). Used for the rich OECD economies — the US,
France, and the UK. Structurally it is `informalAnalytical` with the informal household type removed: `J`
formal types only, so `γ_0 = 0`, `ε` and the informal factor prices (`w^0`, `R^0`, `χ`) disappear, and the
government-budget coefficient collapses to `κ_t = p_t`. Pension design is one-dimensional (`θ` only, and
exogenous). Full derivation in `writing/US/` (`model*.tex` = model/equilibrium definitions, `num*.tex` =
numerical solution); docstrings reference its labels by short name (`eq:calibration:Xsolve`, …).

## Files
`base.py` / `policy.py` / `model.py` — copied from `informalAnalytical` and adjusted, per the repo's
self-contained-per-module convention. `modelFR.py` adds `ModelFR(ModelUS)`, the France/UK calibration
protocol (below). `shocks.py` holds the counterfactual machinery. `policyESC.py`/`modelESC.py` add the
endogenous-`θ` layer (`LeadedLOG`, `LeadedCRRA`, `ModelESC`); `thetaStakes.py` is the diagnostic that
preceded them, decomposing who gains and loses from a marginal change in `θ_{t+1}` without solving for `θ`
at all — it is what established that the leaded choice needs a wedge before any solver was written.
`test.py` loads `data/USMain_test.xlsx`; `testEU.py` loads `data/FRMain.xlsx` and `data/UKMain.xlsx`
(`testEU.model('FR')`, `testEU.model('UK')`, `testEU.model('UK', grouping='US')`). Eight test suites, all
fast (~55 s total), registered in `python/runTests.py`. Drivers: `calibrateRhoGrid.py` (US),
`calibrateRhoGridEU.py` (FR/UK), `runShocksUS.py` (all counterfactuals), `runESC.py` / `runESCcrra.py`
(endogenous `θ`), `collectESCexperiments.py` (merges the two ESC shock csvs into
`results/esc/escExperiments.csv`, the file the paper pipeline reads). The ESC drivers **merge into
their csvs rather than overwriting** (`runESC.mergeWrite`), so a run over one `(ρ, spec)` preserves the
rest of the file — which is what lets `python/paper/` re-run exactly the missing combinations.

## The ρ sweep

```
.venv\Scripts\python.exe python\US\calibrateRhoGrid.py                 # rho 0.5..2.0, step 0.1
.venv\Scripts\python.exe python\US\calibrateRhoGrid.py --commonX       # the common-X variant
```

Anchored at `ρ=1` (the only value where the LOG solver applies, so the only point needing no warm start)
and marched outward in both directions via `gridsearch.continuation.marchGrid`, each point seeded from its
neighbours in the **unbounded** coordinate where extrapolation cannot step `β` or `ω` across zero. Writes
`results/calibration/US_rhoGrid.csv` after *every* point and is resumable: a rerun reads the csv back and
returns cached points without re-solving, so a resumed march is no worse warm-started than an
uninterrupted one. Per-point pickled instances go to `results/calibration/instancesUS/` — **a separate
directory from the Argentina sweep's `instances/`**, whose filenames are the `ρ` alone, so pointing both
at one directory would silently overwrite wherever the grids share a value.

Only `β` and `ω` are searched. `θ` is closed-form from the replacement-rate ratio and does not depend on
`ρ`; under `--commonX`, `X` is recovered after the root rather than inside it. `R` and `τ` are targets and
must be constant down the csv — a column that is supposed to be constant is the cheapest available check
that a point converged to the *right* thing rather than merely converged.

## The zero-mass slot

The informal type `j=0` is kept in every array — the data are laid out that way (see the workbook's
`Readme` sheet) — but has `γ_0 = 0`. Its terms are computed and then multiplied by zero. Two consequences
the code depends on:

- Synthetic `η_0`/`X_0` must stay **finite**. `0·NaN` is `NaN`, which would poison the whole political
  FOC. `test_ee.py` checks the slot is genuinely inert by perturbing it.
- `getEps` **raises** if `γ_0 > 0`. `db['Ushare0']` (the universal share of US transfers, 0.287) is not
  the Argentina models' `ε`, and the platform-work extension would need a properly derived one.

## Two things the docs establish that the code must respect

**The LOG first-order condition decouples across time** (`eq:us:model:PEELOG:decoupling`). With no informal
household, every term in `z_t` is a function of `τ_t` alone — the old informal household's indirect utility
was the only channel through which the *level* of `Θ_{h,t}`, and hence `τ_{t+1}`, entered. So the LOG PEE
path is `T` independent scalar problems, not a backward recursion. Verified exactly (`max|dz_t| = 0`) in
`test_ee.py`. The existing backward solver is still *correct* — the recursion is simply vacuous — so this
is an available optimisation, not something the code currently exploits. Does **not** carry over to CRRA.

**There are two distinct invariances, and they are easy to conflate.** Writing `y^η_i ≡ η_i^{1+ξ}/X_i^ξ`
and `y^x_i ≡ (η_i/X_i)^ξ`, every aggregate uses `y^η` alone; `y^x` appears only in `h_i/h`.

- *Scale* (`eq:us:model:scaleInvariance`): `y^η_i → λ y^η_i`, so `Γ_h → λΓ_h`. Scales `h`, `s`, `c`, `Y`;
  leaves `R`, `w`, `τ`, `h_i/h`, `s_i/s`, savings rate unchanged. Requires `s_0` at the model's own steady
  state, not imposed. **Normalised away by `Γ_h = 1` in both variants.**
- *Hours unit* (`eq:us:model:hoursUnit`): `y^x_i → μ y^x_i` holding `y^η` fixed, i.e. `η_i → η_i/μ`,
  `X_i → μ^{-(1+ξ)/ξ} X_i`. Scales `h_i` and the workweek `h̄ ≡ ∑γ_i h_i` by `μ`; leaves **everything
  else**, including aggregate `h`, unchanged.

Both are checked to machine precision in `test_invariance.py`. The practical upshot: `h̄` is the only
object comparable to an observed workweek, and under variant A its level is meaningless — report it
against a reference point, never compare across calibrations as a level (see the root `RESEARCH_LOG.md`
on exactly this mistake). Aggregate `h` is pinned by `Γ_h = 1` but is in efficiency units and is **not**
what a workweek is comparable to, which is why it cannot serve as the target in `h̄`'s place.

## Calibration

Targets differ from the Argentina models: `R_{t_0}` replaces the savings rate (which is still reported,
just not targeted), the informal `η_0`/`X_0` are gone, and `θ` comes from the OECD replacement-rate ratio
in closed form. Both variants normalise `Γ_h = 1` and differ only in how the hours unit `μ` is fixed.

| Variant | `commonX` | `X` | Hours data used as | `μ` fixed by | Outer loop | Targets |
|---|---|---|---|---|---|---|
| A | `False` (default) | vector `X_i` | relative hours `z^x_i` (eigenvector system) | nothing — left arbitrary | `β`, `ω` | `R_{t_0}`, `τ_{t_0}` |
| B | `True` | common scalar `X` | level of average hours | the `h̄_{t_0}` target | `β`, `ω` | `R_{t_0}`, `τ_{t_0}`, `h̄_{t_0}` |

In variant B, `η_i = (z^η_i)^{1/(1+ξ)} X^{ξ/(1+ξ)}` and `Γ_h = 1` holds for **any** `X` (because
`∑γ_i z^η_i = 1` by construction), so `X` is not a third search dimension — it enters no aggregate at all.
`calibrate` solves the `2×2` system, then `solveCommonX` returns `X` in one closed-form step and the
re-solve reproduces the same `(R, τ)`; `verifyCommonX=True` asserts that, since it is an identity rather
than an approximation. Relative hours become a *prediction* there, `h_i/h ∝ (z^η_i)^{ξ/(1+ξ)}` — worth
reporting against observed `z^x_i` as a diagnostic.

Note `zηiNormalized`: `test.py` divides income by its *unweighted* mean, but the model's `z^η` is relative
to the *population-weighted* average. Variant A never notices (the eigenvector system is scale-free);
variant B inverts `z^η` directly and would silently mis-scale `η` without it.

## The policy smoother's knots (the second bug inherited from Argentina)

`notes/crossCuttingFindings.md` #4 ends with *"`informalAnalytical` uses the same piecewise-linear
interpolants and has not been checked for this."* This module is that vintage, and the ρ sweep is where
the check finally happened. It found #5, not #4.

The policy smoother used `griddedSmooth1D` with FITPACK's **adaptive** knot count, chosen from the data,
so it flips discontinuously as a parameter moves and puts jumps in a residual that is about to be
differentiated. Measured at ρ=0.5 (the hardest point of the sweep), over `ns ∈ {50,75,100,150}`:

| smoother | β across ns | verdict |
|---|---|---|
| adaptive | 1.4347, 1.4395, 1.4391, 1.4369 | a 0.3%-wide **band with no trend** — refinement tells you nothing |
| pinned (`smoothKnots=4`) | 1.4698, 1.4420, 1.4375, 1.4354 | **monotone**, and settles: 1.4354 / 1.4354 / 1.4353 / 1.4355 at ns = 150/200/250/300 |

**Judge by the trend, not the spread.** The converging sequence has the *wider* range, so a
spread-of-answers metric ranks it worse — backwards, and worth remembering, because that is how this was
nearly missed. The adaptive smoother was not avoiding the ns=50 error, only masking it.

`interpKind` is exposed but **`cubic` is not adopted**: at pinned knots it reproduces linear's behaviour
almost exactly while failing to converge in 2 of 8 measured cells (#4's own overshoot caution). `pchip` —
which the 1-D case here can afford, unlike `InformalSavings`' 2-D interpolants — agrees with linear at
ns=150 (1.43527 vs 1.43536, inside linear's own settled band, so a useful independent confirmation of the
value) but fails at ns=50 and 75, which a march cannot afford. So: **linear interpolant, pinned knots,
ns=150 for calibration** (`ns=50` remains the *solve* default; the outer root is far more demanding of the
inner grid than a single PEE solve).

## The Γs bracket (a real bug inherited from Argentina)

`steadyState_CRRA_solve` used a constant bracket `(1e-6, 0.75)`. That is safe at Argentina parameters by
*parameter values, not by construction*: `Θ_h`'s denominator vanishes at `Base.ΓsCap = Γ_h·α·κ/((1-α)·p·θ·τ)`,
which scales with `α/(1-α)` (0.75 there vs 0.43 here) and `κ/p` (>1 there, exactly 1 here). At US
parameters the cap falls to ≈0.58 as `τ→1`, i.e. **below** 0.75, and `steadyStatePEE_CRRA` searches `τ`
across all of `[l,u]` — so `brentq` evaluated a NaN and raised a message pointing at the solver rather
than at the infeasible bracket. `steadyState_CRRA_bounds` now ties the bracket to the model. Retuning the
constant would only move the `τ` at which the trap reappears; `test_crra.py` therefore asserts that the
bracket *tracks the cap*, not that some particular number works.

## Validation against the paper

The variant-A calibration reproduces the *superseded* (commented-out) column of
`writing/Paper/Tables/USUKFRCalibration.tex` closely: `θ = 0.7382` vs 0.74, `ω = 1.4536` vs 1.45,
`η_H/η_L = 3.733` vs 3.73, and the population-weighted mean of `X_i` = 10.88 vs 10.9. The live column
(`θ = 0.83`, `ω = 1.42`, `X = 3.4`, `η_H/η_L = 4.32`) is a different vintage and is **not** reproduced —
consistent with the root `RESEARCH_LOG.md`'s note that the paper's current numbers come from a different
codebase.

## France and the UK: `ModelFR` (`modelFR.py`)

Same model, different calibration protocol — the two differences the paper states (`Quant.tex`, §Social
Security in Rich OECD Countries):

1. **`β` is imposed at the US value at the same `ρ`**, not searched, and the `R` target goes with it.
   `eq:calibration` collapses from a 2-D root over `(β, ω)` to a **1-D root over `ω` against `τ_{t0}`**;
   `R` is still reported, now as a prediction.
2. **Average hours are targeted in *both* variants**, and relative to the US:
   `h̄_FR = h̄_US · workweek_FR/workweek_US`. That is the only hours target with meaning under vector `X`,
   where the level of `h̄` is arbitrary — it is the README's "report `h̄` against a reference point" rule
   turned into the calibration itself. Under `--commonX` it is not a new target: `h̄_US = h0_US` exactly
   there, so it reduces to the observed `workweek_FR` variant B already uses.

Under vector `X` the target is hit by moving **every `X_i` by the same proportion** (`ModelUS.rescaleX`),
which is exactly the scale invariance `eq:us:model:scaleInvariance`. Two consequences:

- **`Γ_h = 1` no longer holds on a calibrated `ModelFR`** — it ends at `λ`. `initProductivity_vectorX`
  still imposes it; the post-root rescaling gives it up. Nothing reads `Γ_h` as a target and every
  reported ratio is invariant to it, so this costs nothing — but an assertion that `Γ_h = 1` is wrong on
  this class.
- **`λ` is block-recursive to the `ω` root**, exactly as `commonX`'s `X` is: the scale invariance leaves
  `τ`, `R`, `w`, `θ`, `s_i/s` and the savings rate pointwise unchanged. So `λ` is closed-form
  (`λ = target/h̄`) and applied *after* the root, never inside it. Asserted by the `verify` drift check,
  not assumed.

France's `θ = 1` needs **no code**: `getθ` returns exactly 1 when the workbook's `RR0 = 1`, for any income
grouping — which is why France's groups may be cut at US percentiles. So `ModelFR` serves the UK unchanged;
only the workbook differs.

Wiring (`modelFR.py`): `usRef` is a dict `{'β','hbar','h0'}` or a callable of `ρ` returning one;
`usRefFromCsv(path, h0US)` builds a `USReference` (a class, not a closure, so a swept instance pickles)
from `results/calibration/US_rhoGrid{,CommonX}.csv`. Pass the csv of the *same* variant — `h̄` differs
between vector `X` and common `X` by construction, and it is `h̄` that carries the reference. A march over
`ρ` requires the callable form and refuses a fixed dict, since `β` and `h̄_US` both move with `ρ`.

**`calibrate` resets productivity to the `Γ_h = 1` baseline before the root**, which is what makes `λ` a
*level* rather than an increment. `rescaleX` multiplies the `X_i` already in db, so without the reset a
second `calibrate` — or the next point of a march, which reuses one instance — reports the small step from
the previous solution instead of the total rescaling. Every other column is right either way (the target
is absolute, so the rescaling lands on it from wherever it starts), which is exactly what made this worth
pinning in `test_fr.py`: the wrong `λ` is plausible. With the reset, `λ = Γ_h` exactly.

### The ρ sweep for FR/UK

```
.venv\Scripts\python.exe python\US\calibrateRhoGridEU.py --country FR
.venv\Scripts\python.exe python\US\calibrateRhoGridEU.py --country UK
.venv\Scripts\python.exe python\US\calibrateRhoGridEU.py --country UK --grouping US
                                                          ... --commonX      # the common-X variant
```

Same march as the US sweep (resume-from-csv, pickle-is-a-cache, `--verify`), with three differences:

- **The search is 1-D**, so the csv has one `x0` column, and `β` is a *recorded* column rather than a
  solved one — it must reproduce the US sweep's `β` at every point, which is the cheapest available check
  that the reference was wired up right.
- **Every visited `ρ` must exist in the US sweep csv.** `USReference` matches exactly and refuses to
  interpolate. The grid is validated against the reference *before* the march starts. This is also why
  `--maxHalvings` defaults to **0** here and not the US sweep's 2: step-halving would insert intermediate
  `ρ` (0.55, 0.65, …) that have no US row. If a point resists, run the US sweep on the finer grid first.
- **Two extra columns**: `λ` (the calibrated hours-unit level under vector `X`; absent under `--commonX`,
  where `X` plays that role) and `hoursDrift`.

**`test_fr.py` needs no France workbook.** Fed the US workbook with the US's own `β` and a workweek ratio
of 1, the whole protocol becomes an identity that can be checked exactly: `ω_FR = ω_US`, `λ = 1`, and
**`R` lands on `R0` although nothing targets it** (verified at `ρ = 1` under LOG and at `ρ = 0.9, 1.3`
under CRRA against the real sweep csv, residuals ≤ 1.4e-15). That last one is the sharp check — it says
the two-target US root and the one-target FR root found the same point, which is what "impose `β` from the
US" has to mean. The rest of the suite drives the workweek ratio and `β` off their reference values and
checks each moves exactly what it should: `λ = r`, `h̄` and `h` and `h_i` scale by `r`, `Γ_h = r`, every
`X_i` moves by `r^{-1/ξ}`, `η_i` untouched, and `ω`/`τ`/`R`/`sr`/`θ` do not move at all.

### The workbooks (`testEU.py`)

`data/FRMain.xlsx` and `data/UKMain.xlsx`, same sheet layout as the US with two differences that are the
protocol showing up in the data:

- **No `30y interest` column** — `R` is not a target, so the number was never collected. `testEU.load`
  sets `db['R0'] = NaN` rather than leaving `ModelUS`'s default 2.443 in place, so a stray
  `ModelUS.calibrate` on one of these workbooks fails loudly instead of quietly targeting the US rate
  (`_checkConverged`'s `not (maxResid <= tol)` already rejects NaN — that is what makes this work).
- France's `Worker-to-retiree` is **adjusted for the lower retirement age** (2.5 years below the US/UK in
  2020, narrowing to 2 by 2050) and differs from the raw census ratio beside it. The UK's is not adjusted.

The UK workbook also carries `heterogeneityUS`/`calibrationUS`: the same UK data **regrouped at US income
percentiles** (cumulative shares 0.5823/0.7580/1), for counterfactuals that need the two countries' groups
to line up. The UK's own calibration uses its own half-mean/mean cuts. The two are **not interchangeable** —
`RR0` is 0.694 against 0.868, so `θ` is 0.560 against 0.543.

### Results at ρ = 1 (LOG)

| | `ω` | `β` (imposed) | `θ` | `λ` | `τ` | `R` (predicted) | `sr` | `η_H/η_L` |
|---|---|---|---|---|---|---|---|---|
| US | 1.4536 | 0.7606 | 0.7382 | — | 0.1443 | 2.4430 | 0.1537 | 3.733 |
| FR | 1.4181 | 0.7606 | **1.0000** | 0.8934 | 0.2129 | 2.0865 | 0.1344 | 2.438 |
| UK | 1.1637 | 0.7606 | 0.5597 | 0.8367 | 0.1186 | 2.0404 | 0.1720 | 3.868 |
| UK (US groups) | 1.2263 | 0.7606 | 0.5427 | 0.8435 | 0.1186 | 2.0403 | 0.1720 | 1.714 |

**France reproduces `writing/Paper/Tables/FR_householdheterogeneity.tex` to every printed digit** —
`X_i = 15.107, 16.778, 19.792` against the table's 15.1, 16.8, 19.8; `η_i = 1.214, 1.757, 2.959` against
1.2, 1.76, 2.96; population-weighted mean `X` 16.53 against `USUKFRCalibration.tex`'s superseded 16.6;
`ω = 1.4181` against 1.42; `θ = 1.00`. That is a validation of the **hours target specifically**: France's
`X_i` level is pinned by nothing except `h̄_FR = h̄_US·workweek_FR/workweek_US`, so landing on the paper's
values is evidence the rule is the one the original codebase used. Same vintage story as the US — the
superseded (commented-out) column is reproduced, the live one is not.

**The UK reproduces `η_i` exactly (0.924, 1.697, 3.574 vs 0.92, 1.70, 3.57) but its `X_i` are uniformly
1.108× the table's** (12.97, 17.84, 35.72 vs 11.7, 16.1, 32.3 — the factor is 1.1082/1.1079/1.1059, i.e.
one common scale). Since `η` matches and the `X` discrepancy is a single proportional factor, the
difference is **purely the `λ` degree of freedom** — the economics is identical, only the hours
normalisation differs, and the paper's UK used a slightly different one. Worth resolving before the table
is regenerated. Note also that the paper's own two tables disagree about the UK: `η_H/η_L` is 3.88 from
`UK_householdheterogeneity.tex` but 2.73/2.85 in `USUKFRCalibration.tex`. This code gives 3.868, siding
with the household table.

### How exactly the rescaling can hold under CRRA (and why the s-grid floor stays absolute)

Under LOG the rescaling is exact — the drift check comes back at 2e-16. Under CRRA it does not, and the
reason is `policy.py`'s `defaultSGrid`: it floors the state grid at an **absolute `1e-4`** while its upper
bound `1.25·sMax` moves with the model. Rescaling `X` therefore changes where the floor sits relative to
the grid, and the solution moves slightly. Measured on the US workbook at ρ=0.8, rescaling by λ=0.89:

| `ns` | 50 | 150 | 300 | 600 |
|---|---|---|---|---|
| `\|Δτ\|` | 9.6e-5 | 1.30e-4 | 1.37e-4 | 1.40e-4 |

It **plateaus rather than shrinking**, which locates the cause in the bound rather than in resolution — a
diagnostic run with a floor of `1e-4·sMax` instead gives 7e-16 at every `ns`, confirming it.

**The floor stays absolute, and that diagnostic is not a proposed change.** `s_{T-1} = 0` makes
`Rlead`/`Bi`/`si_s` undefined and every model here can reach exact zero, so keeping the search off that
region is plain numerical stability and must not be made to depend on the model's own scale. The
consequence to record is just that the rescaling holds numerically only down to the floor's size relative
to `sMax` — with `sMax ≈ 0.37` and λ ∈ [0.83, 0.90] across FR/UK, `1e-4` is ~0.03% of the grid's span and
the resulting drift is ≤ 2.5e-4, comfortably inside the CRRA solver's own error level (`verifyResidual` is
~6e-4 across the US sweep). It would stop being negligible only at a calibration whose `sMax` fell by an
order of magnitude, which is the condition to check before trusting it elsewhere.

So `ModelFR` **records** the drift as `report['hoursDrift']` (and in a sweep record) rather than asserting
it away, and asserts at `hoursDriftTol = {'LOG': 1e-8, 'CRRA': 1e-3}` — loose enough to pass the measured
artifact, tight enough to still catch what the check is for, which is an `η`/`X` leaking into an aggregate
and would be O(1).

For the record, since the diagnostic invites the question: adopting a proportional floor would move the
calibrated `β` by −9.3e-03 (0.65%) at ρ=0.5 and by ≤1.1e-04 at ρ = 0.8, 1.5, 2.0, i.e. it would also
require re-running `results/calibration/US_rhoGrid*.csv`. That the ρ=0.5 answer is that sensitive to the
lower bound is itself worth knowing — it is the same point the knot investigation above found hardest.

## Sweep results (2026-08-21)

Both variants solved 16/16 over `ρ ∈ [0.5, 2.0]` step 0.1, ~4.5 min each; every residual ≤ 6.6e-12,
`verifyResidual` ≤ 9.5e-4. `results/calibration/US_rhoGrid{,CommonX}.csv` plus per-point pickles and the
run logs beside them.

`β` falls monotonically 1.4354 → 0.5563 and `ω` 2.3156 → 1.1934 across the grid; the untargeted savings
rate drifts gently 0.1591 → 0.1485. Three checks fell out of running both variants:

- **`β`, `ω`, `sr`, `h` agree across variants to ~1e-13 at every ρ.** That is the block-recursivity claim
  (`eq:calibration:Xsolve`) confirmed end to end, not just at the calibration year.
- **`R` and `τ` are constant down both csvs** (spreads 1.9e-11 / 3.0e-12) — they are targets, so any drift
  would mean a point converged to the wrong thing.
- **`h̄` is pinned to the target at machine precision under `--commonX` and drifts (1.0e-3) under vector
  `X`** — exactly the documented distinction: only the common-`X` variant gives the workweek a level.

## Counterfactuals (`shocks.py`, `runShocksUS.py`)

```
.venv\Scripts\python.exe python\US\runShocksUS.py                # rho 0.5, 1, 2; all three families
.venv\Scripts\python.exe python\US\runShocksUS.py --commonX      # the common-X variant
.venv\Scripts\python.exe python\US\runShocksUS.py --family theta --rho 1
```

Every experiment is a **new equilibrium path** (2026-08-24): the changed parameters hold over the whole
1960–2200 horizon, the economy starts at its **own steady state** (`solvePEE_*`'s `s0` default), and the
readout is at `db['t0']` = 2020. A row is a country that has *always* had this mix of characteristics —
mostly US, partly France — not the US surprised in 2020. That is what makes the rows commensurable with
France's own calibrated path, which the table now carries as its endpoint (`franceReference`).
`shocks.shockedCopy` is the construction: `deepcopy` (not `createCopyFromt0`), warm starts cleared so
experiments do not depend on run order.

Each is reported twice: **full effect** (τ re-optimised, `solvePEE_*`) and **economic-equilibrium effect**
(τ held at the baseline path, `EE_*_solve` — no political problem, so seconds; its `s0` is the shocked
model's own steady state at the baseline's first-period tax, since there is no policy function to read a
tax off). Three families plus the reference row:

| Family | Scenarios |
|---|---|
| `theta` | `θ = 0`, `θ = 1` |
| `ageing` | mild (`ν → (1+ν)/2` throughout), acute (`ν → 1` throughout) |
| `french` | France's income distribution (`η`), leisure preferences (`X`), voting (`μ`), **all three at once** (`frAll`) |
| — | **France, own calibration** (`franceReference`, `--noFrance` to skip) |

**What the convention costs, measured at ρ = 1: the workweek column and nothing else.** τ and the savings
rate come out identical to every printed digit under both conventions, on all seven scenarios. Under
LOG/Cobb-Douglas both are rate objects independent of the inherited capital stock, while the *level* of
hours responds to the wage and hence to `k_2020`. This does **not** survive to CRRA — τ responds to the
state there, so the ρ ∈ {0.5, 2} rows do move. The superseded csvs are in `results/shocks/preNewPath/`.

**The comparison the change is for** (ρ = 1, full effect):

| | τ | savings rate | workweek | θ |
|---|---|---|---|---|
| US baseline | 14.43% | 21.96% | 39.39 | 0.738 |
| + all three French characteristics | 14.30% | 22.22% | 35.49 | 0.495 |
| France, own calibration | 21.29% | 19.19% | 35.44 | 1.000 |

The characteristics reproduce France's workweek almost exactly and close essentially **none** of the 7pp
tax gap; what is left over is France's own `ω` and its `θ = 1` corner. Note France's workweek cell is
`ModelFR`'s calibration target, not a prediction — say so wherever it is printed.

**Three reporting conventions, none of them arbitrary.**

- The paper's **savings rate is `s/(w·h)`** — savings over gross *labour* income — not `Base.savingsRate`'s
  `s/Y`. They differ by exactly `(1-α)`: the baseline gives `s/Y = 0.15374`, and `0.15374/0.7 = 0.21962`
  against the paper's 21.96%. Without this the baseline row misses by a third.
- The **workweek is normalised against the baseline**, `workweek_data · h̄/h̄_base`, per ρ. Under vector `X`
  the level of `h̄` is not identified, so there is no expression that converts it — `h̄·84` is 31.54 at the
  baseline, not 39.39. Only the ratio is a result.
- **Everything is read at `db['t0']`**, the calibration year's position in the full horizon (2 = 2020).
  The new-path models keep the baseline's calendar, so `db['dates']` is valid on them — that was *not*
  true of the `createCopyFromt0` copies these experiments used to run on, where `Index.union` drops the
  name so `_sliceDb` never sliced it (still pinned in `test_createCopyFromt0.py`, since `thetaStakes.py`
  and the other modules still use that machinery).

**What the French counterfactuals mean, and why the obvious alternatives collapse.** Under vector `X` the
eigenvector identification makes `y^η ∝ z^η`, and every aggregate uses `y^η` alone — so *"swap `z^η` and
re-derive"* and *"take France's whole `(η, X)` pair"* are the **same experiment** (both τ = 13.79%). Only
holding `X_i` fixed while `η` moves is different, and that is the one reproducing the paper (13.28%). So
the decomposition is coherent: `η` carries income distribution, the *level* of `X` carries leisure
preferences, and they do not overlap. Leisure is then a **pure scale** (`rescaleX`), which is why its row
leaves τ and the savings rate exactly at baseline. Voting swaps `μ`, and only its *profile* matters — the
FOC is linear in `μ`, so a common scale cancels out of `z_t = 0`.

**The income-distribution row moves `θ`,** from 0.738 to 0.495: `updateAuxPars` re-derives it holding the
OECD replacement-rate *ratio* fixed, so France's flatter distribution implies a much less Bismarckian
system. Not incidental — pinning `θ` gives τ = 12.83% against 13.28%. Re-deriving reproduces the paper and
is the default; `--pinTheta` runs the alternative.

### Validation against the paper (ρ = 1)

**τ and the savings rate reproduce the paper exactly on all 14 rows** of `US_PensChars`, `US_Ageing` and
`US_OtherShocks` — including the baseline (14.43% / 21.96% / 39.39) — and the new-path convention leaves
both untouched at ρ = 1, so that agreement is unchanged by the rewrite.

**The workweek column improved, and the reason identifies what the old gap was.** The leisure row is the
diagnostic case: the scale invariance requires `s_0` at the model's own steady state, which an
unanticipated shock cannot have, so the pure-scale answer was unreachable under the old convention. It
gave 35.10 against the paper's 34.72; the new path gives **34.74**. The remaining full-effect rows still
differ from the paper by up to ~2%, and that residual is still unattributed — but it is now known not to
be the initial condition.

**A trap that cost a full run** (`notes/crossCuttingFindings.md` #9): `θ` is in `paramsFromFuncs`, so
calling `updateAuxPars` after setting it re-derives it from the replacement-rate data and silently undoes
the shock. Both `θ = 0` and `θ = 1` first returned the baseline to every digit — a null result that reads
as "pension design does not matter" rather than as a bug.

## The paper pipeline

`python/paper/` builds every US/FR/UK table and figure from `results/`, in the same three stages as the
Argentina arm: `runCalibrationUS.py`, `runShocksUS.py`, `build.py`. Stage (i) is **order-dependent** here —
France and the UK read the US `β` out of `US_rhoGrid.csv` and refuse to interpolate, so the US sweep must
be complete first, which `runCalibrationUS.py` enforces. See `python/paper/README.md`.

## Implementation status
Documentation complete (`writing/US/`, exogenous `θ`). Code: economic equilibrium, LOG and CRRA PEE, both
calibration variants, `ModelFR`'s France/UK protocol, ρ sweeps for all four calibrations in both variants
(16/16 points each), `createCopyFromt0`, all three counterfactual families in both readings, and the
`python/paper/` pipeline — all working and tested. France reproduces the paper's household table exactly;
the UK up to one common factor on `X_i`. The shock tables reproduce the paper's τ and savings rate on
every row.

**Endogenous `θ`** (2026-08-23): the *leaded* choice under the `f(θ)` deadweight wedge — appendix
`EndogenousSystemCharacteristics.tex`'s "A+B" combination, which the appendix itself never runs — is
implemented and calibrated. `base.py`'s `wedgeA`/`wedgeB`, `policyESC.py` (`LeadedLOG` complete,
`LeadedCRRA` path-iteration), `modelESC.py` (`ModelESC`), `test_esc.py`, drivers `runESC.py` /
`runESCcrra.py`, results in `results/esc/`. Documented in `writing/US/model_esc.tex` (the cost, the three
timings, and the two propositions the solvers rest on) and `writing/US/num_esc.tex` (the algorithms, the
calibration, and the checks). See `RESEARCH_LOG.md` for the findings; the short version is
that the wedge does escape the `θ = 0` corner and calibrates to p = 0.402 (against the appendix's 0.41
from the sequential timing), ageing moves the design the right way, but the model ties `θ` far more
tightly to inequality than figure 1.1's cross-section does.

Three properties the code relies on, all *measured* in `test_esc.py`, not assumed: `z_t` depends on
`(τ_t, θ_t)` alone (so `τ_t = τPolicy_t(θ_t)` is static and the two choices at `t` are separable); under
LOG the leaded choice has **no state at all** — `θPolicy_t` is constant across the whole `θ` grid, because
`W_t = A(τ_t) + B(θ_{t+1})` in logs; and the choice is invariant to `s_{t-1}`. All three fail under CRRA,
which is why `LeadedCRRA` solves the path and reports `stateSensitivity`.

**The counterfactuals are new paths read at 2020, and the wedge target moved with them** (2026-08-24).
`runESC.leadedNewPath` / `runESCcrra`'s shocks stage build the same object `shocks.shockedCopy` does — the
change over the whole horizon, own steady state — and let the political choice bind from the first period
(`solveLeaded(pinAtT0=False)`, `solveLeadedCRRA(pinAtT0=False)`), so `θ_2020` is an equilibrium outcome and
the tables read t0 rather than t0+1.

That forced the calibration target one period back. `θ_t` is a state chosen at `t-1`, so the design *in
force* in 2020 is `θPolicy_1990`, not the choice made in 2020; `calibrateWedge` now targets the first
(`ModelESC.leadedDesignAtT0` / `leadedDesignAtT0_CRRA`) so the baseline row sits on the observed 0.738. On
the old target the free path came back at **0.727** — a 0.011 miss, small but enough to make every
comparison in a 2020 table read against a number the model did not hit. `p` moves 0.4022 → **0.4076**
under `scale`, φ = 0.5, ρ = 1 (0.7022 → 0.7086 under `flat`); τ and R still land on their targets
(drifts 2e-10 and 5e-4). Under LOG the two objects coincide only if the policy function is time-invariant,
which `ν_t` prevents; `leadedChoiceAtT0` is kept for the pinned reading and for the separability checks.
Superseded csvs: `results/esc/preNewPath/`.

**The CRRA driver's `--bracket` must span every ρ it is asked to run.** The required cost falls an order
of magnitude across the sweep — `p` = 0.965 / 0.408 / 0.090 at ρ = 0.5 / 1 / 2 under `scale`, 1.461 /
0.709 / 0.178 under `flat` — so the old default `[0.01, 0.6]`, chosen at ρ = 2, sits entirely *below* the
root at ρ = 0.5 and the scan correctly reports no crossing instead of converging on its own endpoint.
That default only ever worked because whoever ran ρ = 0.5 passed a wider bracket by hand. Now `[0.01, 3.0]`
with `nScan` 14, which spans all three.

**What the tables now show at 2020** (`scale`, φ = 0.5, ρ = 1, exogenous θ → endogenous θ): acute ageing
0.738 → 0.778, mild 0.738 → 0.752, French voting 0.738 → 0.533, and the French income distribution — and
every scenario containing it, `frBoth` and `frAll` — goes to the **θ = 1 corner**. That last one is a
result, not a failure: under France's flatter distribution the electorate wants a fully Bismarckian
system, which is where France's own observed design sits. France's own row (τ 21.29%, θ = 1) is carried
beside them under `scale`; under `flat` it fails by construction, because that spec's joint `(θ, p)`
inversion is not identified at `θ = 1` — the corner is reported, not worked around.

**A bracket bug the convention exposed** (`model.steadyState_CRRA_bounds`). With `s0` no longer seeded
from the baseline, `solvePEE_CRRA` calls `steadyStatePEE_CRRA`, which searches τ over the whole of
`[l, u]`. At `θ = 0` — the `θ = 0` counterfactual, now over the whole horizon — `Base.ΓsCap` is infinite,
so nothing tied the upper end of the `Γs` bracket to the model and the hard-coded 0.75 was simply too low
at ρ = 2: the residual was negative at *both* ends and brentq raised a bracket error. The bound now
expands geometrically, and only when the default bracket has already failed, so it cannot change a call
that worked. `notes/crossCuttingFindings.md` #7.

**The true CRRA solution** (2026-08-24): `LeadedCRRA2D` (`policyESC.py`) computes the honest Markov
object the path iteration approximates — backward iteration over the 2-D state `(s_{t-1}, θ_t)` with
2-D continuation policy interpolants (`Interp2D`), one direct backward pass, no warm start needed. It
subclasses `policy.CRRA` and overrides only the continuation-evaluation step; pinned periods collapse
the candidate grid to the inherited design *inside the recursion* (under CRRA `τ_t` responds to
`θ_{t+1}`, so simulation-time pinning alone would be wrong — the LOG shortcut does not carry over).
Wrappers: `ModelESC.solveLeaded2D` / `leadedChoiceAtT0_2D`. Validation (`test_escCRRA.py`, and
`writing/US/num_esc.tex` §CRRA): pinned everywhere it reproduces the exogenous solver's tax path to
3.2e-5; at ρ=2's calibrated wedge (p=0.0901) the choice at t0 is 0.759 vs the path iteration's 0.761 —
a 0.002 gap — with τ still on target (drifts 3.2e-4 in τ, 3.1e-4 in R). The W objective is flat enough
that either method pins the design only to ±0.01, and they agree well within that band, so the cheap
path iteration is certified for the tables. Grid requirements measured, not guessed — and they are
properties of the grids, not of `p`, so they carry across the recalibration: the `s` grid is immaterial
(4e-4 from ns=50→150), the θ-*state* grid is not (7 nodes misplace the choice by 0.02; the default 13
suffice). Cost: ~70 s/period at ns=150, ~12 s at ns=50.

Three things about the permanent timing are worth knowing before using it. Its joint `(τ_{t0}, θ)` choice
**concentrates** — `dW/dτ = 0` is the ordinary τ FOC at `θ_t = θ`, so the appendix's two-dimensional grid
collapses to a one-dimensional search, and `τ*(θ) = τPolicy(θ)` is checked in `test_esc.py`.
`s_{t0-1,i}/s_{t0-1}` **must be pinned** while maximising: θ enters it there (through `θ_{t0}`) in a way it
never does in the leaded problem, savings are sunk when the vote is taken, and letting it move gives 0.910
instead of 0.775 (and would break the concentration result, since the ratio also depends on `τ_{t0}` while
`z = 0` is built holding it fixed). And **what it is pinned at is the timing's answer, not the
incumbent's**: the vote is anticipated, so the savings made at `t0-1` were made against the design that
wins, and the equilibrium is the fixed point `θ* = argmax W(θ ; siRatio(θ*))` — `solveFixedPoint`, the
default in `solvePermanent`. The incumbent pinning (an unanticipated reform) is kept as a diagnostic and is
the seed. The two **coincide exactly wherever the choice reproduces the incumbent design**, which is what
`calibrateWedge` targets, so every calibrated `p` is common to both and only the counterfactuals separate
them: 0.775 vs 0.773 at p=0.4, 0.542 vs 0.549 at p=0.25. See `notes/crossCuttingFindings.md` #11/#11b.
Only the *sequential* timing is still unimplemented.

Open smaller items: the workweek column's full-effect gap against the paper (above), and the UK's `X_i`
scale.
