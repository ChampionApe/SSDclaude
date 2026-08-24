# US: measurements and validation against the paper

Demoted from `python/US/README.md` so it can stay a file map and a status. Everything here is a
measurement that cost a solve, or a statement about which of the paper's printed columns this code
reproduces. Nothing here is needed to *use* the module.

## 1. The policy smoother's knots

`notes/crossCuttingFindings.md` #4 ended with *"`informalAnalytical` uses the same piecewise-linear
interpolants and has not been checked for this."* This module is that vintage, and the ρ sweep is where
the check happened. It found #5, not #4.

The smoother used `griddedSmooth1D` with FITPACK's **adaptive** knot count, chosen from the data, so it
flips discontinuously as a parameter moves and puts jumps in a residual about to be differentiated.
Measured at ρ=0.5 (the hardest point of the sweep), over `ns ∈ {50,75,100,150}`:

| smoother | β across ns | verdict |
|---|---|---|
| adaptive | 1.4347, 1.4395, 1.4391, 1.4369 | a 0.3%-wide **band with no trend** — refinement tells you nothing |
| pinned (`smoothKnots=4`) | 1.4698, 1.4420, 1.4375, 1.4354 | **monotone**, and settles: 1.4354 / 1.4354 / 1.4353 / 1.4355 at ns = 150/200/250/300 |

**Judge by the trend, not the spread.** The converging sequence has the *wider* range, so a
spread-of-answers metric ranks it worse — which is how this was nearly missed.

`interpKind` is exposed but **`cubic` is not adopted**: at pinned knots it reproduces linear's behaviour
almost exactly while failing to converge in 2 of 8 measured cells. `pchip` — affordable here, unlike
`InformalSavings`' 2-D interpolants — agrees with linear at ns=150 (1.43527 vs 1.43536, inside linear's
own settled band, so a useful independent confirmation of the value) but fails at ns=50 and 75, which a
march cannot afford.

**The absolute s-grid floor, measured.** Adopting a proportional floor instead would move the calibrated
`β` by −9.3e-03 (0.65%) at ρ=0.5 and by ≤1.1e-04 at ρ = 0.8, 1.5, 2.0 — i.e. it would also require
re-running `US_rhoGrid*.csv`. That ρ=0.5 is that sensitive to the lower bound is itself worth knowing: it
is the same point the knot investigation found hardest.

## 2. Results at ρ = 1 (LOG)

| | `ω` | `β` (imposed) | `θ` | `λ` | `τ` | `R` (predicted) | `sr` | `η_H/η_L` |
|---|---|---|---|---|---|---|---|---|
| US | 1.4536 | 0.7606 | 0.7382 | — | 0.1443 | 2.4430 | 0.1537 | 3.733 |
| FR | 1.4181 | 0.7606 | **1.0000** | 0.8934 | 0.2129 | 2.0865 | 0.1344 | 2.438 |
| UK | 1.1637 | 0.7606 | 0.5597 | 0.8367 | 0.1186 | 2.0404 | 0.1720 | 3.868 |
| UK (US groups) | 1.2263 | 0.7606 | 0.5427 | 0.8435 | 0.1186 | 2.0403 | 0.1720 | 1.714 |

## 3. Validation against the paper's calibration tables

**The variant-A US calibration reproduces the *superseded* (commented-out) column of
`USUKFRCalibration.tex` closely**: `θ = 0.7382` vs 0.74, `ω = 1.4536` vs 1.45, `η_H/η_L = 3.733` vs 3.73,
population-weighted mean `X_i` = 10.88 vs 10.9. The live column (`θ = 0.83`, `ω = 1.42`, `X = 3.4`,
`η_H/η_L = 4.32`) is a different vintage and is **not** reproduced — consistent with the paper's current
numbers coming from a different codebase.

**France reproduces `FR_householdheterogeneity.tex` to every printed digit** — `X_i = 15.107, 16.778,
19.792` against 15.1, 16.8, 19.8; `η_i = 1.214, 1.757, 2.959` against 1.2, 1.76, 2.96; weighted mean `X`
16.53 against 16.6; `ω = 1.4181` against 1.42; `θ = 1.00`. That is a validation of the **hours target
specifically**: France's `X_i` level is pinned by nothing except `h̄_FR = h̄_US·workweek_FR/workweek_US`,
so landing on the paper's values is evidence the rule is the one the original codebase used.

**The UK reproduces `η_i` exactly (0.924, 1.697, 3.574 vs 0.92, 1.70, 3.57) but its `X_i` are uniformly
1.108× the table's** (12.97, 17.84, 35.72 vs 11.7, 16.1, 32.3; the factor is 1.1082/1.1079/1.1059, one
common scale). Since `η` matches and the discrepancy is a single proportional factor, the difference is
**purely the `λ` degree of freedom** — identical economics, different hours normalisation. Note the
paper's own two tables disagree about the UK: `η_H/η_L` is 3.88 in `UK_householdheterogeneity.tex` but
2.73/2.85 in `USUKFRCalibration.tex`. This code gives 3.868, siding with the household table.

## 4. Validation of the counterfactuals (ρ = 1)

**τ and the savings rate reproduce the paper exactly on all 14 rows** of `US_PensChars`, `US_Ageing` and
`US_OtherShocks`, including the baseline (14.43% / 21.96% / 39.39). The new-path convention leaves both
untouched at ρ = 1, so that agreement survived the rewrite.

**What the new-path convention cost, measured at ρ = 1: the workweek column and nothing else.** τ and the
savings rate come out identical to every printed digit under both conventions on all seven scenarios —
under LOG/Cobb-Douglas both are rate objects independent of the inherited capital stock, while the *level*
of hours responds to the wage and hence to `k_2020`. This does **not** survive to CRRA, where τ responds
to the state, so the ρ ∈ {0.5, 2} rows do move.

**The workweek column improved, and the reason identifies what the old gap was.** The leisure row is the
diagnostic case: the scale invariance requires `s_0` at the model's own steady state, which an
unanticipated shock cannot have, so the pure-scale answer was unreachable under the old convention. It
gave 35.10 against the paper's 34.72; the new path gives **34.74**. The remaining full-effect rows still
differ by up to ~2%, unattributed — but now known not to be the initial condition.

**The comparison the change is for** (ρ = 1, full effect):

| | τ | savings rate | workweek | θ |
|---|---|---|---|---|
| US baseline | 14.43% | 21.96% | 39.39 | 0.738 |
| + all three French characteristics | 14.30% | 22.22% | 35.49 | 0.495 |
| France, own calibration | 21.29% | 19.19% | 35.44 | 1.000 |

The characteristics reproduce France's workweek almost exactly and close essentially **none** of the 7pp
tax gap; what is left is France's own `ω` and its `θ = 1` corner. France's workweek cell is `ModelFR`'s
calibration target, not a prediction — say so wherever it is printed.

**The French counterfactuals' equivalences, measured.** "Swap `z^η` and re-derive" and "take France's
whole `(η, X)` pair" both give τ = 13.79%; holding `X_i` fixed while `η` moves gives 13.28%, which is the
one reproducing the paper. Pinning `θ` instead of re-deriving it gives 12.83%.

## 5. The endogenous-θ tables at 2020

`scale`, φ = 0.5, ρ = 1, exogenous θ → endogenous θ: acute ageing 0.738 → 0.778, mild 0.738 → 0.752,
French voting 0.738 → 0.533, and the French income distribution — and every scenario containing it — goes
to the **θ = 1 corner**. That is a result, not a failure: under France's flatter distribution the
electorate wants a fully Bismarckian system, which is where France's own observed design sits. France's
own row (τ 21.29%, θ = 1) is carried beside them under `scale`; under `flat` it fails by construction,
because that spec's joint `(θ, p)` inversion is not identified at `θ = 1`.

The cross-ρ version of this table, and the findings the paper's ESC appendix presents, are in
`notes/esc_experiments_acrossRho.md`.

`LeadedCRRA2D` validation (`test_escCRRA.py`, `writing/US/num_esc.tex` §CRRA): pinned everywhere it
reproduces the exogenous solver's tax path to 3.2e-5; at ρ=2's calibrated wedge (p=0.0901) the choice at
t0 is 0.759 vs the path iteration's 0.761, with τ still on target (drifts 3.2e-4 in τ, 3.1e-4 in R).

The permanent timing's two pinnings separate only away from the calibration: 0.775 vs 0.773 at p=0.4,
0.542 vs 0.549 at p=0.25.

## 6. The common-`X` shock run is a check as much as an output

θ, ageing and voting must come back *identical* to the vector-`X` run — none of them touches `η` or `X`,
and `β`/`ω`/`h` agree across variants — while income distribution and leisure must differ, since those two
are *defined* through `η` and `X`. Measured: the first group agrees to ≤ 4e-15 in τ and sr, the second
differs by up to 7.9e-3 in τ and 1.48 hours in the workweek. A common-`X` run that matched on all seven
would mean the variant was not being applied.
