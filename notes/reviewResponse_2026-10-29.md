# Response to the AI review of 2026-10-29

The review is `coarse-output/coarse_review_29102026.md` (coarse 1.9.6, Opus 5.5, high): twelve overall comments,
here O1–O12, and 19 detailed ones, 1–19; recommendation major revision. The run was on a flattened TeX of
`fa0335f` (OpenRouter had no credit for the PDF), so the reviewer saw no reference list and its appendix numbers
("appendix 19", "34") are off; its `\label` names are right. First-pass verdicts below come from two read-only
checks against the draft and the W16 response (`archive/notes/reviewResponse_2026-10/paper_reviewResponse.md`,
A1–A14). **Nothing is decided or implemented.** Cost tags: (a) text only, (b) print a number already in
`results/`, (c) new computation.

## Found while checking (not, or not quite, in the review)

- **Under the cost the tax is not monotone in θ in the cross-section.** In layer 1 (`results/oecd26/layer1.csv`,
  specs `size` and `sizePiR`) the tax at the chosen design `τInForce` exceeds the tax at the observed one `τ2020` in
  24–26 of 26 countries, whichever way the design moves: in the 11–16 countries chosen more Bismarckian than
  observed (Australia θ 0 → 0.69, τ 5.2 → 6.8%; Ireland 0 → 0.71, 6.2 → 8.7%), tax and θ rise together. The loss
  term $1+\ln f$ outweighs the marginal-utility term at low dispersion. Section 7.3's "at a given demography a more
  Bismarckian design lowers the tax" (`Sections/EndogenousTheta.tex:80`) holds without the cost, not with it.
- **W16 decisions not in the draft:** A8 (ageing response under the Π-inclusive and design-level costs in section
  7; only in OA C3), A10 (the sentence that ε is never chosen), A1's introduction sentence on Conde-Ruiz–Profeta
  (TODO W20), W6's marginal-loss figures (a design 0.1 flatter loses 7.7/3.5/0.8%, `C5_marginalLoss.csv`), and
  W16 #1's turnout check of B.1's condition at the U.S. calibration.
- **Appendix E's footnote is false** (`Appendix/HouseholdSurveyArg.tex:24`): it says every target is "measured"
  at the calibration year; the survey is 2006 H2, the coverage share 2004, spending 2000–01 (flagged in W4, unchanged).
- **Section 7.1 overclaims the costless lead-timing corner** (`EndogenousTheta.tex:5`, "at every IES we check …
  one period ahead"): on file only under log (`results/esc/escPermanent.csv`, spec `none`); no `none` spec in
  `runESCcrra`.

## Overall comments

**O1 Ageing → Bismarckian partly from the cost's τ-linearity.** Premise right (two forces at
`EndogenousTheta.tex:57`, inequality decomposed at :60, ageing not; λ 12–205× external evidence at
`Appendix/EndogenousDesign.tex:72`; six of 26 at θ = 1; France unreachable). Defence available: the τ-linearity of
the share is the Harberger one (loss ∝ τ², revenue ∝ τ), not a free choice. Repeats W16 A8, whose trigger ("six of
the 26 at θ = 1") is now met. *Rec.:* (b) put OA C3's numbers into 7.2 (acute ageing raises θ₂₀₂₀ by 0.109 at the
paper's λ, 0.074 under ε transport, 0.035 under the design-level cost at ρ = 1; `results/esc/escAgeingCosts.csv`);
(c, cheap under log) the reviewer's step, loss share held at the U.S. path then freed, via `c5Numbers._withCost`.
**For RKB:** the linear term (new code in `python/US/base.py`) — A8 said revisit if the test looked off.

**O2 Corner proved for a timing set aside; λ vs a weight gradient.** Half wrong: the introduction's "we prove"
(`Introduction.tex:27`) is the simultaneous timing, which prop:esc:corner proves. The real overclaim is 7.1 (above).
Threshold numbers right (3.4 vs 1.61), and C.1 already says the threshold bounds turnout × responsiveness (A1, done).
Non-identification of λ and the weight gradient is valid in principle. *Rec.:* (a) 7.1 "under log" for the lead
timing (or (c) run it at ρ = 0.5, 2 with no cost); (c, one log calibration) the $k$ in $\mu_i = y_i^k$ at which the
lead-timing choice at λ = 0 equals θ*, one number in C.1. Decline the cross-section under that closure (as A1).

**O3 Spending–index relation mixes two counterfactuals.** Right; the notes say so (`EndogenousTheta.tex:75`,
`Tables/OECD26_Robustness.tex:33`). Spending at the chosen design is on disk (`τInForce`). With the finding above,
switching would *raise* the model's slope (42–58 against 16.3). *Rec.:* (b) report the chosen-design reading
(column switch in `tablesOECD26.panelData`) and partial slopes conditional on ν, data and model; (a) qualify :80.

**O4 Validation thin and moves with measurement.** All numbers check. The preferred specification is already
marked. New: the base rate for "same side as the U.S." is 14 of 25 (always predict above), so 17 of 25 is weak; by
hand Pearson ≈ 0.59, Spearman ≈ 0.5, RMSE ≈ 0.29 against 0.30 for the mean and ≈ 0.26 for θ on ν. Repeats A14's
scope. *Rec.:* (b) r and Spearman from `layer2.csv`/`layer1.csv`, base rate beside 17/25; report the RMSE and say
why it loses (compressed range, corners unreachable); (a) one sentence in 7.3 justifying ε transport and U.S.
turnout before appendix H's variants. **For RKB:** whether to print the RMSE.

**O5 The index may not measure the model's θ.** Right: PaG 2021 table 4.1's mandatory series includes mandatory or
quasi-mandatory private tiers for NL, DK, SE, CH, AUS, ISL, NO; the Netherlands' 0.951 cannot be the AOW. Under log
layer 1's chosen design does not depend on the observed one, so its index–growth slope is untouched; data slopes,
layer-1 spending, layer 2 and the side counts change. New. *Rec.:* (b, small builder change) slopes without the
private-tier countries (`tablesOECD26.py:81` takes 26|29 only); better (c) a public-only index from PaG's
public/private breakdown (paper-data to check it reports 0.5 and 1.0 AW by scheme) and a log rerun (~10 s a solve).
**For RKB:** subsample only, or the public index.

**O6 Design history and demographic measurement.** Right (stateless design under log; ν is total population
growth; France's correction only in the deep test). Nit: θ₂₀₂₀ depends on ν₂₀₂₀ too, through T₂₀₂₀. New. *Rec.:*
(a) path dependence among the conclusion's limitations; (c, cheap) an old-age-dependency ν from WPP 2024
(`oecd29Data.py`), one row in table H.2. Decline the CRRA inherited-design extension.

**O7 Argentina: consistency, not accounting.** Numbers check; A7 done. Reviewer error: τ is the equivalent rate
(spending over formal labor income), so the 2008 nationalization enters through spending, as the footnote says;
the Ruffo comparison is already qualitative. Left: "accounts for about three fifths" (`Introduction.tex:24`,
`Conclusion.tex:5`) outruns section 5. *Rec.:* (a) "is consistent with / matches" in both, one clause on the
equivalent rate; (c, minutes) the reform at α = 0.24, 0.384, 0.40, ρ = 1 (with detailed #8).

**O8 GHH drives the retirees' stake.** Right, and repeats A9 (limitation named, no non-GHH run: done). A non-GHH
run is a new solver (the tax gains a state, the design loses separability). *Rec.:* decline; (a) at most one
sentence saying why.

**O9 Coverage never chosen.** Right; repeats A10, whose sentence is missing. The one-shot comparison of $\mathcal
W_{2010}$ at ε = 0.21 and ε^U is cheap (`InformalSavings/policy.py:262`) but likely favours ε^U and reopens "why not
earlier". *Rec.:* (a) write A10's sentence; decline the computation.

**O10 No decomposition of predicted variation by source.** Right, new, cheap and probably favourable: layer 1 at
ν ≈ 1.02–1.05 spans spending 11.0–12.3% across θ 0.34–1, against 2.9–14.2% across ν. *Rec.:* (c) 3 × 26 log
solves through `runOECD26._build`, one input at its U.S. value each time; variance shares of predicted τ and θ.

**O11 No majority-voting benchmark.** Partly: dependence on propensities is shown in-model (H, robustness
table); the contrast with CRP is asserted. *Rec.:* (a) A1's introduction sentence plus "the model does not nest
majority voting"; decline the median-voter run (two-dimensional policy, no Condorcet winner without CRP's
structure).

**O12 No analytical comparative static for the design.** Right, new, and one result is cheap: under log ν_t enters
eq:esc:leadFOC only through the young's bloc, $-(\omega/\nu_t)$ times the retirees', so at an interior optimum
with the second-order condition $d\theta^*_{t+1}/d\nu_t < 0$ whenever the retirees' bloc is positive: the first
force is structural and needs no λ. *Rec.:* (a) one paragraph in C.4 (paper-writer-lead to check the derivation);
the second force and $\tilde V$ stated as numerical.

## Detailed comments

| | Verdict | Action |
|---|---|---|
| 1 cost moves with current τ | agree | (a) C.3: dependence on current τ is part of the reduced form; reword the 7.8 vs 8.7 footnote (`EndogenousTheta.tex:41`), which also mixes in ω's recalibration. (c) f at anticipated τ, recalibrate λ, redo acute ageing — **for RKB** |
| 2 Ṽ scaling and residence-based tiers | agree | (a) state the forfeiture assumption at `EndogenousDesign.tex:58`; one sentence on AOW/NZ/DK flat tiers. Only the dispersion force depends on it |
| 3 France's 1990 gap | partly | right on 1990 (≈5 years, ν₁₉₉₀ 1.10 → 0.85), wrong on 2050. (a) say the 1990 gap is held at 2020's; (c) rerun the deep test — **for RKB** |
| 4 CRRA state space | partly | no contradiction (the paragraph has the design given); (a) extend the footnote as proposed anyway |
| 5 roadmap HtM qualifier | agree | (a) `Introduction.tex:33` |
| 6 which U.S. cost travels | agree | (b) footnote at `EndogenousTheta.tex:64`: λ = 11.11 at ε = 20.01 (11.34 and 20.44 at the CPS groups) |
| 7 Argentina's θ mapping | partly | arithmetic right (0.838 vs 0.816), explanation backwards (spread 2.11, wider). (a) one sentence; loosen `Argentina.tex:21` |
| 8 α vs y⁰ | partly | (a) 0.35 a compromise implying informal income ≈ 12% of GDP against the model's 7.5%; drop "same footing" |
| 9 ageing without the ε caveat | partly | (a) add the qualifier at `Introduction.tex:29`; the Argentine relevance is wrong (informal savers there) |
| 10 Bismarckian lowers τ, turnout | partly | reviewer's check uses the wrong consumption; at consistent shares μy/D² falls with income on all of [0,1] (high/low 0.37–0.51). (a) clause at `Introduction.tex:22`, `OECD.tex:26`; (c, no solve) the weights in B.1 from a script. See also the cost finding above |
| 11 order of the ρ = 0.5 steps | agree | (a) "the three forces nearly offset each other" |
| 12 "small to modest" loss | agree | (b) name the calibration; print the θ = 0.5 losses (13.4/6.3/1.5%) or W6's marginal figures |
| 13 implicit tax of the benchmark | partly | algebra right, omitted size term 38% of revenue at ε = 20.44. RKB cut the common-wedge clause on 2026-10-26 — **for RKB**: restore with this caveat? |
| 14 Gini slope sign | partly | (a) the bivariate slope does not isolate the channel; (c, no solve) partial slopes, with O3 |
| 15 IES and the savings channel | partly | B₂₀₂₀ is 0.660/0.655/0.653 across ρ (β recalibrated), so curvature, as written, is the channel. (a) "by the logic of" the proposition; optional clause with B |
| 16 2006 survey for 2010 | agree | (a) assign the moments to the 2010 period and correct the false footnote; 2010 EPH only if wanted (data outside the repo) |
| 17 EPH formality rule | agree | (a) the self-employed, the urban frame, the age cut; needs RKB's original data work — **for RKB** |
| 18 duration factor | agree, minor | (a) the factor is a lower bound; recomputing needs the life-table regression (not in the repo) |
| 19 Medicare vs UK | partly | (a) drop "below the UK's 0.560" in appendix F and OA B5; recast so comparability is the stated reason |

17 of 19 close with text; #1, #3, #10, #14 can be answered with computation instead of acknowledged.

## For RKB

1. O1: the linear-plus-quadratic cost (A8's condition met), and whether the reviewer's freed-τ decomposition runs.
2. O3 and the cost finding: which spending reading the test reports, and how 7.3 states the tax–design relation.
3. O4: print the RMSE beside the correlations?
4. O5: drop the private-tier countries, or rebuild a public-only index.
5. O10 and O6: the variance decomposition and the old-age-dependency ν (both cheap log runs).
6. Detailed #1, #3, #13, #17.
7. Declines: O8 non-GHH, O9 the ε choice, O11 the median voter, O6's CRRA history extension.
