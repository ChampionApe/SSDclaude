# US

US model variant, for the rich OECD economies — the US, France and the UK. Structurally it is
`informalAnalytical` with the informal household type removed: `J` formal types only, so `γ_0 = 0`, `ε`
and the informal factor prices disappear, and the government-budget coefficient collapses to `κ_t = p_t`.
Pension design is one-dimensional (`θ`). Derivation in `writing/US/` (`model*.tex` = model/equilibrium,
`num*.tex` = numerical solution); docstrings cite its labels by short name (`eq:calibration:Xsolve`, …).

## Files

| | |
|---|---|
| `base.py`, `policy.py`, `model.py` | copied from `informalAnalytical` and adjusted, per the self-contained-per-module convention |
| `modelFR.py` | `ModelFR(ModelUS)` — the France/UK calibration protocol |
| `shocks.py` | the counterfactual machinery |
| `policyESC.py`, `modelESC.py` | endogenous `θ`: `LeadedLOG`, `LeadedCRRA`, `LeadedCRRA2D`, `PermanentLOG/CRRA`, `ModelESC` |
| `thetaStakes.py` | the diagnostic that preceded them — who gains and loses from a marginal change in `θ_{t+1}`, without solving for `θ`. It established that the leaded choice needs a wedge |
| `test.py`, `testEU.py` | workbook loaders: `USMain_test.xlsx`; `FRMain.xlsx` / `UKMain.xlsx` via `testEU.model('FR'|'UK'[, grouping='US'])` |

Eight test suites, all fast (~55 s), registered in `python/runTests.py`.

## Running it

```
python\US\calibrateRhoGrid.py   [--commonX]                  # US sweep, rho 0.5..2.0 step 0.1, ~4.5 min
python\US\calibrateRhoGridEU.py --country FR|UK [--grouping US] [--commonX]
python\US\runShocksUS.py        [--commonX] [--family theta] [--rho 1]
python\US\runESC.py | runESCcrra.py                          # endogenous theta
python\US\collectESCexperiments.py                           # merge -> results/esc/escExperiments.csv
```

All sweeps write their csv after *every* point and resume from it; per-point pickles are a cache.
`python/paper/` drives all of this for the paper's numbers — see `python/paper/README.md`.

Four things about the drivers that are not obvious:

- **Instance directories must not be shared.** Pickle filenames are the `ρ` alone, so the US sweep writes
  `instancesUS/`, separate from the Argentina sweep's `instances/`.
- **The EU sweeps require the US sweep to be complete first.** `USReference` matches `ρ` exactly and
  refuses to interpolate, which is also why `--maxHalvings` defaults to **0** there: step-halving would
  insert `ρ` that have no US row.
- **Pass the EU sweeps the csv of the *same* variant.** `h̄` differs between vector `X` and common `X` by
  construction, and it is `h̄` that carries the reference.
- **The ESC drivers merge into their csvs rather than overwriting** (`runESC.mergeWrite`), so a run over
  one `(ρ, spec)` preserves the rest of the file. `runESCcrra.py --bracket` must span every ρ it is asked
  to run: the required wedge falls an order of magnitude across the sweep (`p` = 0.965 / 0.408 / 0.090 at
  ρ = 0.5 / 1 / 2 under `scale`), so a bracket chosen at ρ = 2 sits entirely below the root at ρ = 0.5.

## Invariants the code depends on

**The zero-mass slot.** The informal type `j=0` is kept in every array — the data are laid out that way —
with `γ_0 = 0`, so its terms are computed and multiplied by zero. Synthetic `η_0`/`X_0` must therefore
stay **finite**: `0·NaN` is `NaN`, which would poison the political FOC (`test_ee.py` perturbs the slot to
check it is inert). `getEps` **raises** if `γ_0 > 0`.

**The LOG first-order condition decouples across time** (`eq:us:model:PEELOG:decoupling`): with no
informal household every term in `z_t` is a function of `τ_t` alone, so the LOG PEE path is `T`
independent scalar problems. Verified exactly in `test_ee.py`. The backward solver is still correct — the
recursion is simply vacuous — so this is an available optimisation, not one the code takes. Not true under
CRRA.

**Two invariances, easily conflated.** With `y^η_i ≡ η_i^{1+ξ}/X_i^ξ` and `y^x_i ≡ (η_i/X_i)^ξ`, every
aggregate uses `y^η` alone and `y^x` appears only in `h_i/h`. *Scale* (`y^η → λy^η`) scales `h`, `s`, `c`,
`Y` and leaves `R`, `w`, `τ` and every ratio alone — normalised away by `Γ_h = 1`. *Hours unit*
(`y^x → μy^x` at fixed `y^η`) scales `h_i` and the workweek `h̄ ≡ ∑γ_i h_i` and leaves **everything
else**, aggregate `h` included, unchanged. Both checked to machine precision in `test_invariance.py`.

> **`h̄` is the only object comparable to an observed workweek, and under vector `X` its level is
> meaningless.** Report it against a reference point; never compare it across calibrations as a level.
> Aggregate `h` is pinned by `Γ_h = 1` but is in efficiency units and cannot serve as the target instead.

## Calibration

`R_{t_0}` replaces the savings rate (still reported, not targeted), the informal `η_0`/`X_0` are gone, and
`θ` is closed-form from the OECD replacement-rate ratio. Both variants normalise `Γ_h = 1` and differ only
in how the hours unit is fixed.

| Variant | `commonX` | `X` | Hours data used as | Outer loop | Targets |
|---|---|---|---|---|---|
| A | `False` (default) | vector `X_i` | relative hours (eigenvector system) | `β`, `ω` | `R_{t_0}`, `τ_{t_0}` |
| B | `True` | common scalar `X` | level of average hours | `β`, `ω` | `R_{t_0}`, `τ_{t_0}`, `h̄_{t_0}` |

Under B, `Γ_h = 1` holds for **any** `X`, so `X` is not a third search dimension: `calibrate` solves the
2×2 system and `solveCommonX` returns `X` in one closed-form step (`verifyCommonX=True` asserts the
re-solve reproduces `(R, τ)`, since that is an identity, not an approximation). Relative hours become a
*prediction* there, worth reporting against the observed profile.

**`zηiNormalized` is load-bearing.** `test.py` divides income by its *unweighted* mean; the model's `z^η`
is relative to the *population-weighted* average. Variant A never notices (its eigenvector system is
scale-free); variant B inverts `z^η` directly and would silently mis-scale `η`.

**Settings**: linear interpolant, pinned knots (`smoothKnots=4`), `ns=150` for calibration (`ns=50` stays
the *solve* default — the outer root is far more demanding of the inner grid than one PEE solve). The
smoother's adaptive knot count is a discrete choice inside a differentiated residual and must not come
back. `steadyState_CRRA_bounds` ties the `Γs` bracket to `Base.ΓsCap` rather than to the inherited
constant `(1e-6, 0.75)`, and expands geometrically when the default has already failed — `ΓsCap` is
infinite at `θ = 0`, so it cannot be the only guard. `test_crra.py` asserts the bracket *tracks* the cap.
See `crossCuttingFindings.md` #7 and `notes/archive/us_measurements.md` §1.

**Sweep health checks**: `R` and `τ` are targets and must be constant down the csv; `β`, `ω`, `sr`, `h`
must agree across the two variants (~1e-13, the block-recursivity claim end to end); `h̄` is pinned at
machine precision under `--commonX` and drifts ~1e-3 under vector `X`.

## France and the UK (`modelFR.py`)

Same model, two protocol differences: **`β` is imposed at the US value at the same `ρ`** (so the root
collapses to 1-D over `ω` against `τ_{t0}`, and `R` becomes a prediction), and **average hours are
targeted in both variants, relative to the US** — `h̄_FR = h̄_US·workweek_FR/workweek_US`, the only hours
target with meaning under vector `X`.

The hours target is hit by moving **every `X_i` by the same proportion** (`rescaleX`), i.e. by the scale
invariance. Hence: **`Γ_h = 1` no longer holds on a calibrated `ModelFR`** — it ends at `λ`, which costs
nothing but makes an assertion of `Γ_h = 1` wrong on this class; and **`λ` is closed-form and applied
*after* the root**, asserted by the `verify` drift check rather than assumed.

**`calibrate` resets productivity to the `Γ_h = 1` baseline before the root**, which is what makes `λ` a
level rather than an increment — `rescaleX` multiplies the `X_i` already in db, so without the reset a
second `calibrate`, or the next point of a march, reports the step from the previous solution. Every other
column is right either way, which is what makes the wrong `λ` plausible and worth pinning in `test_fr.py`.

France's `θ = 1` needs **no code** (`getθ` returns exactly 1 when the workbook's `RR0 = 1`, for any income
grouping), which is why France's groups may be cut at US percentiles and why `ModelFR` serves the UK
unchanged.

**The workbooks** differ from the US in two ways that are the protocol showing up in the data: no
`30y interest` column, so `testEU.load` sets `db['R0'] = NaN` rather than leaving the US default in place
— a stray `ModelUS.calibrate` then fails loudly instead of quietly targeting the US rate; and France's
`Worker-to-retiree` is adjusted for the lower retirement age. The UK workbook also carries
`heterogeneityUS`/`calibrationUS` — the same data regrouped at US income percentiles, for counterfactuals
needing the groups to line up. The two are **not interchangeable**: `RR0` 0.694 against 0.868, so `θ` is
0.560 against 0.543.

**`test_fr.py` needs no France workbook.** Fed the US workbook with the US's own `β` and a workweek ratio
of 1, the protocol becomes an identity: `ω_FR = ω_US`, `λ = 1`, and **`R` lands on `R0` although nothing
targets it** (≤ 1.4e-15) — the sharp check that the two-target US root and the one-target FR root find the
same point.

**The rescaling is exact under LOG (2e-16) and not under CRRA**, because `defaultSGrid` floors the state
grid at an **absolute `1e-4`** while its upper bound moves with the model. The drift plateaus rather than
shrinking under refinement, locating the cause in the bound rather than in resolution. The floor stays
absolute — `s_{T-1} = 0` makes `Rlead`/`Bi`/`si_s` undefined and every model here can reach exact zero, so
that guard must not depend on the model's own scale. `ModelFR` therefore *records* the drift as
`report['hoursDrift']` and asserts at `{'LOG': 1e-8, 'CRRA': 1e-3}`: loose enough for the measured
artifact, tight enough to catch an `η`/`X` leaking into an aggregate, which would be O(1). It stops being
negligible only at a calibration whose `sMax` falls by an order of magnitude.

## Counterfactuals (`shocks.py`, `runShocksUS.py`)

Every experiment is a **new equilibrium path**: the changed parameters hold over the whole 1960–2200
horizon, the economy starts at its **own steady state**, and the readout is at `db['t0']` = 2020. A row is
a country that has *always* had this mix of characteristics — not the US surprised in 2020 — which is what
makes the rows commensurable with France's own calibrated path, carried as the table's endpoint.
`shocks.shockedCopy` is the construction: `deepcopy` (not `createCopyFromt0`), warm starts cleared so
experiments do not depend on run order. Each is reported twice: **full effect** (τ re-optimised) and
**economic-equilibrium effect** (τ held at the baseline path — seconds, since there is no political
problem; its `s0` is the shocked model's own steady state at the baseline's first-period tax).

| Family | Scenarios |
|---|---|
| `theta` | `θ = 0`, `θ = 1` |
| `ageing` | mild (`ν → (1+ν)/2`), acute (`ν → 1`), throughout |
| `french` | France's income distribution (`η`), leisure preferences (`X`), voting (`μ`), all three at once |
| — | France, own calibration (`--noFrance` to skip) |

**Three reporting conventions, none arbitrary.** The paper's **savings rate is `s/(w·h)`**, not
`Base.savingsRate`'s `s/Y` — they differ by exactly `(1-α)`, and without this the baseline row misses by a
third. The **workweek is normalised against that ρ's own baseline**, since under vector `X` the level of
`h̄` is not identified and only the ratio is a result. **Everything is read at `db['t0']`**; the new-path
models keep the baseline's calendar, so `db['dates']` is valid on them — which was *not* true of the
`createCopyFromt0` copies these experiments used to run on (`Index.union` drops the name, so `_sliceDb`
never sliced it; still pinned in `test_createCopyFromt0.py`, since `thetaStakes.py` uses that machinery).

**What the French rows mean.** Under vector `X` the eigenvector identification makes `y^η ∝ z^η` and every
aggregate uses `y^η` alone, so "swap `z^η` and re-derive" and "take France's whole `(η, X)` pair" are the
**same experiment**; only holding `X_i` fixed while `η` moves is different, and that is the one
reproducing the paper. So `η` carries income distribution, the *level* of `X` carries leisure preferences,
and they do not overlap. Leisure is then a pure scale, which is why its row leaves τ and the savings rate
exactly at baseline. Voting swaps `μ`, and only its *profile* matters — the FOC is linear in `μ`.

**The income-distribution row moves `θ`,** 0.738 → 0.495: `updateAuxPars` re-derives it holding the
replacement-rate *ratio* fixed, so France's flatter distribution implies a much less Bismarckian system.
Not incidental — pinning `θ` instead gives τ = 12.83% against 13.28%. Re-deriving reproduces the paper and
is the default; `--pinTheta` keeps the alternative on disk.

> **A trap that cost a full run** (`crossCuttingFindings.md` #9): `θ` is in `paramsFromFuncs`, so calling
> `updateAuxPars` after setting it re-derives it and silently undoes the shock. Both `θ = 0` and `θ = 1`
> first returned the baseline to every digit — a null result reading as "pension design does not matter".

## Endogenous `θ`

The *leaded* choice under the `f(θ)` deadweight wedge — appendix `EndogenousSystemCharacteristics.tex`'s
"A+B" combination, which the appendix itself never runs. Documented in `writing/US/model_esc.tex` (the
cost, the three timings, the two propositions the solvers rest on) and `num_esc.tex` (algorithms,
calibration, checks).

**Three properties the code relies on, all *measured* in `test_esc.py`, not assumed**: `z_t` depends on
`(τ_t, θ_t)` alone, so `τ_t = τPolicy_t(θ_t)` is static and the two choices at `t` are separable; under
LOG the leaded choice has **no state at all**, because `W_t = A(τ_t) + B(θ_{t+1})` in logs; and the choice
is invariant to `s_{t-1}`. All three fail under CRRA, which is why `LeadedCRRA` solves the path and
reports `stateSensitivity`.

**The calibration target is the design *in force* in 2020** — `θPolicy_1990`, not the choice made in 2020,
since `θ_t` is a state chosen at `t-1`. `calibrateWedge` targets `leadedDesignAtT0`, which is what puts
the baseline row on the observed 0.738 (the old target came back at 0.727). `p` = 0.4076 under `scale`,
φ = 0.5, ρ = 1. The counterfactuals are new paths read at 2020 with the choice binding from the first
period, so `θ_2020` is an equilibrium outcome.

**`LeadedCRRA2D` is the honest Markov object** the path iteration approximates — backward iteration over
the 2-D state `(s_{t-1}, θ_t)`, one direct pass, no warm start. **Pinned periods collapse the candidate
grid to the inherited design *inside* the recursion**, since under CRRA `τ_t` responds to `θ_{t+1}` and
simulation-time pinning alone would be wrong (the LOG shortcut does not carry over). It certifies the
cheap path iteration for the tables. Grid requirements are properties of the grids, not of `p`: the `s`
grid is immaterial, the θ-*state* grid is not (7 nodes misplace the choice by 0.02; the default 13
suffice). ~70 s/period at ns=150.

**The permanent timing**, three things worth knowing before using it. Its joint `(τ_{t0}, θ)` choice
**concentrates** — `dW/dτ = 0` is the ordinary τ FOC at `θ_t = θ`, so the appendix's 2-D grid collapses to
a 1-D search (checked in `test_esc.py`). `s_{t0-1,i}/s_{t0-1}` **must be pinned** while maximising, since
θ enters it there in a way it never does in the leaded problem; letting it move gives 0.910 instead of
0.775. And **what it is pinned at is the timing's answer, not the incumbent's**: the vote is anticipated,
so the equilibrium is the fixed point `θ* = argmax W(θ ; siRatio(θ*))` (`solveFixedPoint`, the default).
The two coincide exactly wherever the choice reproduces the incumbent design — which is what
`calibrateWedge` targets — so every calibrated `p` is common to both.
`crossCuttingFindings.md` #11/#11b.

## Status

Implemented and tested: economic equilibrium, LOG and CRRA PEE, both calibration variants, `ModelFR`'s
France/UK protocol, ρ sweeps for all four calibrations in both variants (16/16 each), all three
counterfactual families in both readings, the endogenous-`θ` leaded choice under LOG and CRRA (path
iteration and exact 2-D solver) and the permanent timing, and the `python/paper/` wiring.

Measurements, ρ=1 results tables and validation against the paper's printed columns:
`notes/archive/us_measurements.md`.

**Open**: the *sequential* ESC timing is unimplemented; `PermanentCRRA` has never been executed
(`notes/todo_escPermanentTiming.md`); the workweek column's full-effect gap against the paper (~2%,
unattributed, but known not to be the initial condition); and the UK's `X_i` sitting uniformly 1.108× the
paper's, which is purely the `λ` normalisation.
