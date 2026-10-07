# Common X versus vector X_i in the Argentina calibration

Written 2026-09-11. Compares the two calibration variants of the Argentina model (`python/InformalSavings`,
`commonX = True | False`) on the calibration sweep, the reform experiments and the (ε, θ) grid, and argues
which variant the main text should carry. The companion note for the OECD arm is
`notes/us_commonX_vs_vectorX.md`; the code and docs are in `python/InformalSavings/RESEARCH_LOG.md`
(2026-09-11 evening) and `writing/informalSavings/model_calibration.tex` (the common-X paragraph).

## The two variants

Both fit the same aggregates: the capital-output ratio (3.23, identifying β), the pension tax (10.9% of
formal labour income, identifying ω), the income shares of the four formal quartiles, and the informal
household's income and hours relative to the formal average (identifying η_0 and X_0). They differ in how
the formal taste for leisure is identified.

- **Vector X_i** (the draft's numbers). One leisure parameter per formal quartile, identified from each
  quartile's observed hours in the EPH. Relative hours are data; the level of hours is not identified and
  the workweek is reported only against the baseline. Both normalisations of the documentation's
  eq. (calibration:yNorm) are imposed: Γ_h = 1 and ∑γ_i(η_i/X_i)^ξ = 1, the second being what lets the
  informal hours target be stated against the aggregate h_t.
- **Common X.** One leisure parameter shared by the four formal quartiles, its level pinned by the observed
  average formal workweek of 42.5 hours (as a share of discretionary time). η_i follow from the income
  shares alone, Γ_h = 1 holds for any X, and relative formal hours become a prediction. The second
  normalisation is not imposed; the informal targets carry the hours-unit ratio M = ∑γ_i(η_i/X_i)^ξ/Γ_h
  instead (0.84 here; exactly 1 under vector X). The informal η_0 and X_0 stay calibrated parameters under
  both variants.

The calibrated objects at ρ = 1:

| | η_i (quartiles 1 to 4) | X_i | η_0 | X_0 | relative formal hours |
|---|---|---|---|---|---|
| Vector X_i | 0.51, 0.72, 0.95, 1.69 | 0.74, 0.77, 0.88, 1.24 | 0.288 | 0.375 | data: 0.89, 0.98, 1.02, 1.10 |
| Common X | 0.64, 0.90, 1.14, 1.87 | 1.94 | 0.344 | 0.804 | predicted: 0.86, 0.95, 1.02, 1.18 |

β, ω, the capital-output ratio, the tax rate, the savings rate and the informal savings ratio ι are
identical across the two variants to 4e-12 at every ρ of the grid (0.5 to 2.0), and so is the
grid-refinement residual of each point. The informal parameters differ by the M factors exactly
(η_0/M and X_0·M^{-1-1/ξ}) and, as under vector X, barely move across ρ (η_0 0.343 to 0.344, X_0 0.803
to 0.805); X itself sits at 1.92 to 1.94.

## Where the results agree: everywhere

Every experiment the paper prints gives the same answer under both variants, to solver precision:

| Output | Largest difference, any ρ, any column |
|---|---|
| Reform paths, full effect (`universal_match_rho*`) | 4e-12 |
| Reform paths, taxes held (`eeOnly_match_rho*`) | 4e-12 |
| Flat reading at ρ = 1 (`universal_flat_rho1`) | 4e-12 |
| (ε, θ) grid at ρ = 1, 378 points, τ, s/Y, hours, ι | 3e-13 |

So `ArgentinaUniversal`, `Argentina_funcOfRho`, `ARG_LOG_FourInOne` and `ARG_CRRA_LOG` print the same
numbers under either variant: the 1.25 p.p. tax increase, the 0.3 p.p. of GDP savings drop, the 0.15-hour
workweek change, the 16 to 17% fall in informal savings.

## Why the Argentina arm cannot tell the variants apart, when the US arm can

X enters no aggregate. The formal composite η_i^{1+ξ}/X_i^ξ equals z_i^η under both variants, the
aggregate h_t is in efficiency units and does not respond to the hours unit, and the informal household
contributes through η_0^{1+ξ}/X_0^ξ, which the M factors leave unchanged. The calibration is therefore
block-recursive: X is solved after the four-parameter root and moves nothing the root saw.

In the US arm two counterfactuals are defined *through* η or X (France's income distribution imported at
the US X_i, and France's level of X), and those are where the variants separate. The Argentina arm has no
such experiment: the reform moves ε, the grid moves ε and θ, and CRRA moves ρ, none of which touches
η_i or X_i. The only place the variant shows is the calibration table and the sentence that explains
how X is identified.

## Where they differ: the calibration table and its reading

- **What is data and what is a prediction.** Under vector X the four relative hours are inputs and the
  X_i profile (0.74 to 1.24, rising with income) is the residual that makes them hold. Under common X
  the hours profile is a prediction, 0.86, 0.95, 1.02, 1.18 against 0.89, 0.98, 1.02, 1.10 in the data:
  the right ordering and the right middle, with the top quartile overshot by 8% and the bottom undershot
  by 4%, because the model makes hours rise with income at elasticity ξ/(1+ξ) = 0.23 and the EPH profile
  is flatter.
- **The level of hours.** Under common X the 42.5-hour workweek is a calibration target, hit exactly;
  under vector X it is a normalisation of the printed workweek and carries no content. This is the same
  distinction the OECD section already explains for the US.
- **The informal parameters.** Under common X, X_0 = 0.80 against the formal X = 1.94, so the informal
  household's disutility of labour is 41% of the formal one; under vector X, X_0 = 0.375 against formal
  X_i of 0.74 to 1.24, a ratio of 30 to 50%. Same reading, different units. Neither number is quoted in
  the text.
- **One caveat to confirm.** The workbook's "Average workweek" (42.54 hours) is read as the average over
  *formal* workers, because every other hours datum in the calibration is relative to the formal
  average (`data/ArgentinaTest.xlsx`, `test.py`). If the figure is an all-worker average, the common-X
  target should be that instead (the informal type then enters the target with its weight γ_0 = 0.32),
  which changes X but, by the same block recursion, nothing else.

## Conclusion: common X for the main text, vector X_i for the appendix

The quantitative case is empty here, so the decision is about the paper's identification story, and on
that count common X is the better choice, for three reasons.

1. **One identification across the two arms.** The OECD section leads with common X and explains why
   (relative hours as a prediction tested against data, the workweek as the one hours target). Carrying
   vector X_i for Argentina would ask the reader to follow a second convention for the same object, with
   a normalisation, ∑γ_i(η_i/X_i)^ξ = 1, that exists only to make the informal target well defined and
   has no counterpart in the US text.
2. **The informal targets read more naturally.** Under common X the informal hours and income targets are
   stated against average formal hours, which is what the EPH ratios are, with the hours unit carried
   explicitly through M; under vector X the same statement leans on the second normalisation being in
   force, which is the assumption that produced the 2026-09-11 mis-scaling of η_0 and X_0.
3. **It costs nothing.** No number in the Argentina results moves, so the change is confined to the
   calibration paragraph (the identification of X, the workweek target, the relative-hours check) and
   the calibration table (X in place of X_i; η_i, η_0 and X_0 at their common-X values). The vector-X
   twin goes to the appendix next to the OECD twins, with one sentence saying the results are identical
   by construction, which is itself a useful statement about the model.

The one argument for keeping vector X_i is that the Argentina hours data by quartile are then used
rather than predicted, and the prediction misses the top quartile by 8%. That is worth reporting (the
common-X table's note already prints predicted against observed), but it is a check the model passes
reasonably rather than a reason to identify four parameters from four numbers and leave the hours level
free.

What it takes: set `config.ARG['commonX'] = True`, run `build.py --only ArgentinaCalibration
ArgentinaCalibration_vectorX ArgentinaUniversal ...` (every `Argentina*`/`ARG_*` name), rewrite the
identification paragraph of `Sections/Argentina.tex` (the sentences from "Because only relative income
and hours are observed" to the normalisation), and register the `_vectorX` twins in the appendix.
