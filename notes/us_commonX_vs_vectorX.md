# Common X versus vector X_i in the US counterfactuals

Written 2026-09-10. Compares the two calibration variants of the US model on the full shock set
(`results/shocks/US_shocksCommonX.csv` against `results/shocks/US_shocks.csv`), at ρ ∈ {0.5, 1, 2},
and argues which variant the main text should carry.

## The two variants

Both fit the same US aggregates: the tax rate, the interest rate, the average workweek, and the income
shares of the three groups. They differ in how the taste for leisure is identified.

- **Vector X_i.** One leisure parameter per income group, identified from each group's observed hours.
  Relative hours are data; the level of hours is not separately identified and only its ratio to the
  baseline is reported. Productivities η_i follow from incomes and observed hours.
- **Common X.** One leisure parameter shared by all groups, its level pinned by the observed average
  workweek. Relative hours across groups are then a prediction of the model, and η_i are re-identified
  from incomes given those predicted hours.

The calibrated objects at ρ = 1:

| | η_i (low, mid, high) | X_i | Xbar |
|---|---|---|---|
| US, vector X_i | 0.96, 1.70, 3.58 | 8.0, 9.9, 18.5 | 10.9 |
| US, common X | 0.82, 1.38, 2.52 | 4.0 | 4.0 |
| FR, vector X_i | 1.21, 1.76, 2.96 | 15.1, 16.8, 19.8 | 16.5 |
| FR, common X | 1.11, 1.57, 2.55 | 7.1 | 7.1 |

β, ω, τ, R and the savings rate are identical across the two variants to about 1e-13: they are pinned
by aggregates, and the group structure enters them only through sums that both variants match.

## Where the counterfactuals agree

Every counterfactual that leaves η_i and X_i untouched gives the same answer under both variants, to
solver precision (below 1e-6 in τ, the savings rate and hours): the baseline, θ = 0, θ = 1, mild and
acute ageing, French voting weights, and France's own calibrated path. This holds at every ρ and for both
the economic-equilibrium and the full-effect readings. It is the block-recursivity property end to end.

## Where they differ

Two counterfactuals are defined through η or X, and both differ in the same direction at every ρ.
Full effect, levels; savings rate is s/Y.

**Income distribution** (France's η_i, US X_i held, θ held at the US design):

| ρ | τ common | τ vector | gap | s/Y common | s/Y vector | hours common | hours vector | gap |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 12.9% | 12.4% | 0.5 p.p. | 16.7% | 17.0% | 42.3 | 41.1 | 1.2 h |
| 1.0 | 13.2% | 12.8% | 0.4 p.p. | 15.8% | 16.0% | 42.0 | 40.8 | 1.1 h |
| 2.0 | 13.7% | 13.4% | 0.2 p.p. | 15.0% | 15.1% | 41.7 | 40.7 | 1.0 h |

Against the common baseline (τ = 14.4%, hours 39.4), the vector-X reading is the larger tax cut and
the smaller rise in hours.

**Leisure preferences** (every X_i rescaled by Xbar_FR / Xbar_US):

| ρ | hours common | hours vector | gap |
|---|---|---|---|
| 0.5 | 32.8 | 34.4 | 1.6 h |
| 1.0 | 33.2 | 34.7 | 1.5 h |
| 2.0 | 33.7 | 35.1 | 1.4 h |

Taxes and the savings rate do not move in either variant (a pure rescaling of X is a change of the
hours unit). The observed French workweek is 35.4 hours, 4.0 below the US.

**All three French characteristics** is the sum of the two: at ρ = 1, τ = 13.9% (common) against 13.4%
(vector), hours 35.3 against 35.9.

## Why

**Income distribution.** The political choice responds to the composite
η_i^{1+ξ} / X_i^ξ, which is what enters the tax first-order condition, not to η_i alone. Under vector
X the calibrated US X_i rise steeply with income (8.0 to 18.5), because high earners work fewer hours
than their productivity alone would imply and X_i absorbs that. The counterfactual holds those X_i and
imports France's flatter η_i, so the two compressions compound. Under common X there is no X gradient
to compound with. Top-to-bottom ratio of the composite at ρ = 1:

| | US baseline | French η imported |
|---|---|---|
| Common X | 4.3 | 2.9 |
| Vector X_i | 4.3 | 2.5 |

The baselines coincide by construction (both fit the same US data); the vector-X counterfactual is the
flatter economy, hence the larger tax cut and the smaller hours response.

**Leisure.** The rescaling factor is the ratio of the two countries' mean X, and that ratio is a
calibration outcome: 1.76 under common X, 1.52 under vector X. Under common X the level of X is pinned by
the average workweek alone, so the ratio is the entire hours gap read as a taste difference. Under
vector X the X_i also carry each country's relative-hours profile, and France's is much flatter (15.1 to
19.8 against 8.0 to 18.5), which pulls the two means closer. Both variants overshoot the observed 4.0-hour
gap: common X by 6.2 hours at ρ = 1, vector X by 4.7.

## Conclusion: common X for the main text, vector X_i for the appendix

The current setup (`config.US['commonX'] = True`) is the right one, for three reasons.

1. **Common X tests the model where vector X fits it.** Under common X the relative hours of the three
   groups are a prediction, checked against data in the household-heterogeneity tables. Under vector X
   they are inputs, and the X gradient that results (a top group with more than twice the taste for
   leisure of the bottom group) is a residual that makes the hours data hold rather than an estimate of
   anything. A counterfactual that holds that residual fixed while changing η_i carries it into the
   answer.
2. **The inequality counterfactual is cleaner under common X.** It isolates the income distribution:
   the composite that the political choice responds to moves because η moves, and for no other reason.
   Under vector X part of the measured effect is the interaction with a leisure gradient that was itself
   identified from US hours. Common X is also the more conservative reading (a 1.2 p.p. tax cut against
   1.6 at ρ = 1), which is the safer one to build the section's argument on.
3. **Identification is one parameter, one target.** Common X is pinned by the workweek; vector X uses
   three hours observations for three parameters and leaves the level of hours unidentified, which is
   why the appendix twin can only report hours relative to its baseline.

The one row where vector X does better is leisure: its 4.7-hour overshoot of the observed gap is
closer than common X's 6.2. That is not a point in its favour for the main text, because it comes from
the same fitted X_i profile, and the paper does not lean on the leisure counterfactual as a quantitative
account of the hours gap; the text already says the model overshoots. It is, however, exactly what the
appendix twin is for: it shows that the sign and rough size of every effect survive the other
identification, that the tax and savings results are identical wherever η and X are not involved, and
that the two rows that move do so for a reason the reader can follow.

So: keep common X as the headline, keep the vector-X twin in the appendix with the paragraph that
explains the two rows that differ, and do not print both in the main text. If the paper ever wanted to
use the leisure counterfactual as a quantitative explanation of the US-France hours gap, that would be
the case for revisiting the choice.
