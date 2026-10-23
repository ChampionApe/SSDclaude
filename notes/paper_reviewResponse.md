# Response to the AI review of 2026-10-22

The review is `coarse-output/coarse_review_22102026.md` (the second file there is an identical copy): eleven
overall comments, here O1–O11, and 25 detailed ones, 1–25. All were reconciled with RKB on 2026-10-23;
`notes/plan_reviewResponse.md` carries them out. Nothing is implemented yet.

## Agreed actions (implement after reconciliation)

**A1 (O1, agreed 2026-10-23).** No separate responsiveness ψ_i: it would enter where μ_i does and is not
identified apart from it, and the threshold is already in C.1.
- C.1, after the threshold $\mu_i/\mu_j < c_i/c_j$: one sentence that μ_i is the political weight of type i,
  turnout its observable part, and that a responsiveness differing across types (the swing-voter density of
  probabilistic voting) would enter in the same place; then the critical ratio at the 2020 U.S. calibration: the
  corner survives until the weight of the high-income group is about 3.2 times that of the low-income one, twice
  the observed turnout ratio (1.61). Computed for proposition C.1's timing (design chosen with the tax), log,
  τ = 0.144, α = 0.3, β = 0.76, retirees' savings formed under θ* = 0.738, weights μ_i = y_i^k on the CPS groups:
  first overturned at k = 0.8 (ratio 3.22); retirees' consumption ratio high/low at θ = 0 is 3.16. The number
  needs a reproducible source when implemented (the check was a scratch script). Section 7's timing would need a
  model run.
- Introduction: one sentence that the data rejecting Conde-Ruiz and Profeta is not evidence for this model, since
  their prediction comes from coalitions under majority voting, which probabilistic voting rules out.
- λ keeps "political" among the costs it stands for (RKB, 2026-10-23): no model captures every political force,
  saying so is no weakness, and the paper already goes further than the related literature.

**A2 (O5's U.S. target, agreed 2026-10-23).** Pensions only, in all three countries, as the main calibration: the
U.S. tax rate from pension spending alone (7.2% of GDP: τ = 10.3%, not 14.4%) and θ* from *Pensions at a Glance
2021*'s 39.2/49.6 (0.728 at the model's groups, not 0.738). Medicare in τ and θ as a flat benefit (θ* = 0.519,
below the UK's 0.560) goes to the online appendix as the "transfers to the old" reading. Rewrite section 6's
"Fourth, ..." and appendix F's Medicare sentences; the U.S. block reruns from stage (i) and λ is recalibrated,
with section 7 and appendix G (G.1's "the UK's system is smaller" flips). Open: one spending concept throughout,
figure 1.1's cash (U.S. 7.37, UK 7.84, France 14.44, against the workbooks' 7.2, 8.27, 14.88).

**A3 (income source, agreed 2026-10-23).** Sections 6–7 keep the microdata groupings: for the U.S. the CPS covers
part-time and part-year men, gives group means and hours directly and shares its survey with the turnout data,
where the OECD series is full-time only, three percentiles and a fitted lognormal ($\tilde V$ 0.365 against 0.436).
The cross-country exercise uses the OECD earnings deciles of men in full-time work, 2019, for every country, the
three included, so that it reports them at both sources. Optional, with D3: recount the UK on a recent
Understanding Society wave (the BHPS is 2006–07; the OECD series has the UK's $\tilde V$ fall from 0.227 to 0.192
by 2019).

**A4 (sample, agreed 2026-10-23).** The cross-country exercise runs without informality on 26 countries: Mexico,
Turkey and Korea dropped by one rule, ILO informal employment above 25% (56, 31 and 29%; next come the UK, 20%,
the Czech Republic, 17%, and the Netherlands, 14%, where the measure mostly reflects self-employment those systems
cover), with Korea's young system (1988) and Turkey's retirement age of 52 as further reasons. Figure 1.1 stays at
29 with a note; the model is compared with data slopes recomputed on the 26 (they move little, below); the 29 go
to the online appendix.

**A5 (O2, agreed 2026-10-23).** Proposition 2 reworded only slightly: θ and inequality at the stationary fixed
point, where retirees' savings shares are consistent with the design, for $J$ types; the $\nu_t$ condition
($\sum_{i>0}\gamma_i\mathcal E^i_{2,t}>0$ at the optimum) in the statement; ε's condition (B.5) stated at the
inherited distribution. Appendix B.1's proof rewritten, succinct and with every step explicit: the first-order
condition; the derivative in θ at consistent shares (weight $y_i/c_i^2$, Chebyshev); inequality for $J$ types by
pairwise transfers; the $\nu_t$ condition. With it, B.1's young term (the code's $1+\beta\alpha(1+\xi)/(1+\alpha\xi)$,
not $1+\beta$) and the stray $\tau_t$. The θ step is checked (scratch check of 2026-10-23); the inequality step at
consistent shares is still to be derived.

**A6 (O3, agreed 2026-10-23).** The appendix carries it, the main text points to it. Appendix: log-HtM uniqueness
stated and proved (at consistent shares the retirees' term falls in τ); the candidate count recorded in every solve
and reported (now on no U.S., UK or French calibration path and on 6 of 54 `US_shocks` rows, OA D2); a table of 2020
and 2050 outcomes at $T$ = 2140, 2200, 2290 and under appendix D's steady-state terminal condition, for CRRA and
informal savings; first-order-condition residuals off the grid. Main text: section 4's Gonzalez-Eiras–Niepelt
sentence reworded (their uniqueness does not carry over; log-HtM proved, the rest checked numerically), footnote 12
updated.

**A7 (O4, agreed 2026-10-23).** Rerun the Argentine reform with pre-reform ε = 0 (γ₀ counts the elderly without a
pension); report the change in formal benefits in table 2 (+3.4% in 2010, against "financed by cuts"); name the
compared objects (71% total against total, 62% for the newly covered); a sentence each on the 2005 spending base,
the 2008 nationalization and the period length; the 1.8% presented as one moment among several.

**A8 (O5's cost, agreed 2026-10-23).** The ageing response under the Π-inclusive cost and under the design-level
cost moves into the main text (section 7). No linear term for now: revisit it if the 26-country test looks off
(six of the 26 sit at θ = 1, which no finite λ reaches).

**A9 (O7, agreed 2026-10-23).** Qualify the ranking in the abstract and the conclusion (at ρ = 2 the voting effect,
1.69 p.p., exceeds the design effect, 1.48; numbers to redo after A2); fix the conclusion's "changes only the size
of the earnings-link effect"; say that Gonzalez-Rozada and Ruffo's sign excludes only ρ near 0.5; GHH named as a
limitation, no non-GHH run.

**A10 (O8, agreed 2026-10-23).** No grid over ε. What remains is one sentence on the scope: section 7 chooses θ,
and ε enters only as the Argentine reform.

**A11 (O9, agreed 2026-10-23).** The $J = 1$ closed form, checked against Gonzalez-Eiras and Niepelt (2008), in a
footnote or appendix B, not in section 3; no $J = 2$ figure.

**A12 (O10, agreed 2026-10-23).** Both sides of (B.5) at the Argentine calibration, with $\sigma^0_t$ and
$\sigma^i_t$, in the appendix only; no negative case.

**A13 (O11, agreed 2026-10-23).** Online appendix, low priority: $\tau_{2020}$ against the inherited capital at
ρ = 0.5, 1, 2 for the U.S., and the 2020 tax split into the choice of a voter who ignores the state-to-policy
feedback and the full Markov choice.

**A14 (O6, agreed 2026-10-23).** The 26-country test. Anchor
on the U.S. measured as the others are (OECD
deciles at the U.S. percentiles, figure 1.1's spending and index, θ = 2 − 1/I, WPP ν), turnout and the other
parameters at the U.S. values. (1) Main text: each country's ν path, income distribution and inherited design at the
U.S. ω and λ; the predicted 2020 tax and the design chosen in 2020, regressed on growth and the Gini as in figure
1.1 (θ converted by $I = 1/(2-\theta)$), slopes beside the data's. (2) Appendix: ω calibrated to each country's
spending, the design predicted at the U.S. λ (G.1's test on 25 countries), the ω's reported. (3) OA: each country's
own turnout; all 29. Defaults: U.S. percentiles everywhere, plain WPP ν, 2019 distributions, figure 1.1's cash
spending. Placed at the end of section 7 (layer 1), in an appendix (layer 2 and the data) and in the OA.

## Data for the 29-country log calibration (O6)

Assembled 2026-10-23: `notes/data_oecd29.md` (sources, validation, seven decisions for us), `data/oecd29*.csv`,
`python/paper/oecd29Data.py` (not wired into the build). The ν method is found: total population growth over thirty
years, UN WPP 2024 medium variant, reproduces every workbook value to 4e-7 (the paper's "census data" is this).
Main open choice: the income distribution source (recommended: OECD earnings deciles of men in full-time work,
which reproduces the UK's grouping and understates the U.S. and French dispersion).
Figure 1.1's correlations at 29 / without MEX and TUR / also without KOR: spending–growth −.58/−.56/−.58,
index–growth −.39/−.49/−.49, spending–index .63/.67/.67, spending–Gini −.08/.12/.15, index–Gini .18/.17/.18; only
the sign of the flat spending–Gini relation depends on the sample.

## Found while checking (not in the review)

- **The U.S. design target is pension-only.** `USMain_test.xlsx`'s replacement-rate ratio 0.796748 is 39.2/49.2
  to six digits; *Pensions at a Glance 2021* has 39.2/49.6 (0.790), so a transcription slip or an older edition,
  and no Medicare, against section 6 and appendix F ("Medicare enters the calibration of θ"); τ includes it
  (7.2 + 2.9% of GDP). Medicare as a flat benefit gives θ* = (1 − 2.9/10.1) × 0.728 = 0.519, exact under the benefit
  formula. Resolved by A2.
- B.1's young term is printed with $(1+\beta)$; the code (`python/informalAnalytical/base.py`, `dv1i_dτ_LOG`) has
  $1+\beta\alpha(1+\xi)/(1+\alpha\xi)$, which is right (the printed form drops the rise in $R_{t+1}$).
- B.1's $\partial\mathcal E^m_{2,t}/\partial\theta$ carries a stray $\tau_t$ (a common factor, harmless).
- The log-HtM tax is unique: with savings shares consistent with the tax, the retirees' term still falls in τ.
- Under the design-level cost (OA C3), France's income distribution takes the U.S. design to θ = 1 at every ρ.

## Detailed comments (agreed at the first-pass verdicts, 2026-10-23)

W15 goes with #19 (and #5's decomposition with it); #13's index units are for the headline numbers only.

| | Verdict | Action |
|---|---|---|
| 1 sign of θ | right about B.1, wrong fix | as O2 |
| 2 Ruffo | agree | their estimate (difference-in-differences, households) in its own units; rework the choice of ρ |
| 3 GDP vs formal output | agree | one GDP concept in target and outcome |
| 4 distribution at the reform | partly | formal shares at the reform date are rebuilt under the new ε (`policy.py`, `tLag = tFirst` on the copy): fix, rerun |
| 5 inequality and design | mostly agree | decompose the design condition (with W15); candidate channel: τ falls, the cost is linear in τ |
| 6 reporting margin | agree | narrow C.2 to participation and formality |
| 7 marginal loss | agree | add it (ρ = 0.5: 3.9% to 7.3% for Δθ = −0.1) |
| 8 threshold under CRRA | agree | $(c_i/c_j)^{1/\rho}$ in C.1 |
| 9 Bismarckian corner | agree | section 7.1's wording into C.2 |
| 10 φ in (B.5) | agree, negligible | fix B.1's sentence |
| 11 monotonicity (C.9) | agree | "near the calibrated design" |
| 12 $\bar b_t$ | agree | relabel at (8) |
| 13 θ vs the index | agree | state $I = 1/(2-\theta)$; design changes in index units |
| 14 leisure row | wrong | none |
| 15 informal wages | agree | reword section 2.2 |
| 16 fixed anticipated tax | partly | add the qualifier; the numerical check is moot |
| 17 timing | partly | editorial, section 7.1 |
| 18 mild ageing | mostly disagree | at most make the framing explicit |
| 19 low-IES reversal | agree (= W15) | fix "dampened"; the threshold; check the ρ ≤ 0.6 resolution first |
| 20 loss timing | agree | a footnote |
| 21 Harberger | agree | "revenue-equivalent excess burden" |
| 22 λ mapping | agree | λ ≈ εΠ/R; recompute the multiples |
| 23 French voting | partly | one sentence |
| 24 GE&N attribution | agree | Song only; hand-to-mouth qualifier |
| 25 γ₀, ν | agree on γ₀ | define both in section 2.1 |
