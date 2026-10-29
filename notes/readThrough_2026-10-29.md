# Read-through of the draft, 2026-10-29 (W22)

This is the full read-through after RKB's Overleaf edits of 2026-10-28/29, done by three read-only reviewers
(sections 1–5, sections 6–8, appendices A–H). The reviewers checked numbers against the csvs under `results/`
and `data/`; anything not stated below matched at its printed precision.
- Part 1 lists the decisions for RKB, each with a recommended change.
- Part 2 lists simple fixes, to be applied once RKB agrees.
- Part 3 lists fixes to generated tables, made in `python/paper`.

Already applied today (before the read-through):
- Table 4 gained a β column, with λ, β and ω at two decimals.
- Table 5: the standard errors are stacked under the slopes, and the note is trimmed.
- The abstract and the conclusion were shortened.
- Small fixes in the new §6 and §7 text.
- Figure 7's note now defines the model's index.

## 1. Decisions for RKB (most important first)

**D1. Which cost parameter is structural, λ or ε.**
- §7.2, G.2 and table 6 hold λ constant along the U.S. path (escPath, spec `size`).
- §7.3, G.1 and H transport ε, so that λ_{n,t} = ε Π_{n,t}/R_{n,t} varies with the date (`sizePiR`).
- Appendix C.2's footnote (EndogenousDesign.tex:70) says Π/R is absorbed into λ "which is calibrated rather than derived". That argues against the paper's own cross-section specification.
- §7.3's footnote presents the transport as notation ("we write λ_US,t = ε Π/R"). Under ε, the cost falls with ageing: the U.S. Π/R goes from 0.555 (2020) to 0.467 (2110), and older countries face a lower λ. This is part of why the index responds less to growth (−0.23 against −0.28 under λ, table 15).
- The cut §7.2 paragraph was the only place that explained this. A referee will ask why λ is constant in 7.2 and date-varying in 7.3.
- *Recommend:*
  - Keep λ constant for the U.S. results and ε for the cross-section.
  - Rewrite C.2's footnote: "Π/R falls as the population ages, from 0.55 in 2020 to 0.46 in 2110 along the U.S. path. The U.S. results of section 7.2 absorb it into a constant λ; to carry the cost across countries, section 7.3 and appendices G.1 and H keep it, λ_{n,t} = ε Π_{n,t}/R_{n,t}."
  - Add one clause to §7.3: "…which at the U.S. ratio of 2020 is the λ of table 4 and falls as a population ages; appendix H repeats the test with the U.S. λ in every country."

**D2. The cross-section's U.S. anchor is recalibrated, and §6–7 no longer say so.**
- Four sets of U.S. values appear:
  - Table 3: ω = 1.23, from the CPS household groups, no cost.
  - Table 4: ω = 1.28, λ = 11.34 at ρ = 1, so ε = 20.445 (also in G.1 and table 12).
  - Table 5: ω = 1.294, ε = 20.014, β = 0.655. This is the U.S. measured from the OECD earnings data, as every other country is: θ = 0.735, Ṽ = 0.333, and its λ_2020 is 11.108.
  - Figure 6.2's test: ω = 1.259, which is printed only in a cell of table 16.
- Only H.2 explains the recalibration, and today's cut removed §6's footnote on ω.
- *Recommend:*
  - Restore a one-line footnote in §6: "the political weight that reproduces U.S. spending with the U.S. design and income distribution measured as for every other country, 1.259, differs slightly from table 3's."
  - Add one sentence to §7.3: "every synthetic country takes the political weight and the cost parameter of the U.S. measured from the same OECD data (appendix H), which differ slightly from those of table 4."
  - Add 1.259 to H.2.

**D3. Precision of λ, ε and β across tables and prose (a consequence of today's two-decimal table 4).**
- Table 4 prints λ = 11.34 and β = 0.65 at ρ = 1.
- Table 13 (UK, "as table 4") prints 16.694, 7.740 and 3.103.
- Table 12, G.1, G.2 and H quote 11.345, 20.445, 7.740, 14.655 and 20.014.
- β reads as 0.66 (tables 3 and 8), 0.655 (H and the notes to tables 5 and 14) and 0.65 (table 4). The values are 0.6555 without the cost and 0.6549 with it, so the 0.66/0.65 pair is a rounding straddle that reads as a misprint.
- *Recommend:* two decimals throughout, matching RKB's call for table 4:
  - λ/ε in table 13 and in table 12's notes.
  - The prose of G and H: 11.34, 20.44, 7.74, 14.66, 20.01.
  - β at 0.65/0.66 wherever it is quoted.
- Alternatively, table 4's β at three decimals alone (1.058 / 0.655 / 0.517) removes the straddle.

**D4. β > 1 at ρ = 0.5 (table 4: 1.06 per thirty-year period, 1.063 without the cost).**
- It is the first β at ρ ≠ 1 that the paper prints, and only online appendix page B1 comments on it.
- *Recommend:* add to table 4's note: "At ρ = 0.5 the β that matches the U.S. interest rate exceeds one, with or without the cost."

**D5. The abstract's claims.**
- "Taxes … higher when pensions are universal": proposition 2 and the introduction call the effect of ϵ ambiguous, and at ρ = 0.5 Argentina's tax falls.
  - *Recommend:* "Taxes are lower when benefits are earnings-related, and a universal pension raises them when informal retirees are poorer than formal ones."
- "an interior choice requires redistribution … to be costly": C.1 allows an interior design if turnout rises steeply with income, and the introduction carries that qualifier.
  - *Recommend:* "…requires redistribution through pensions to be costly unless the rich vote much more often than the poor", or leave it as a simplification acceptable in an abstract.

**D6. "Ageing first, the earnings link second" depends on the scenario and the measure.**
- The ranking holds for acute ageing measured against the design corner to corner. At ρ = 0.5 it is a near tie (9.3 vs 9.1).
- Against mild ageing (4.0 p.p.), the design ranks first.
- At ρ = 2, the design's 2.0 p.p. corner to corner beats France's voting profile (1.8) only on that measure: from the baseline, the θ = 0 bar is 1.2 p.p.
- *Recommend:*
  - State "measured from corner to corner" once in §6.
  - Write "ageing to a constant population" in the abstract and conclusion, or drop "at every IES we consider" from the conclusion.

**D7. Argentina's informal savings (Argentina.tex:34, RKB's new sentence).**
- The sentence: "informal households lower savings by 6 p.p. against that of formal ones".
- The 6 is ι, informal savings relative to the average formal household's, which falls from 32.8% to 26.9% in 2010. ι is defined only in figure 5.2's note, two paragraphs later.
- Read as savings rates, the gap falls 5.4 p.p., and those rates are over disposable labour income, which §3 of the style guide rules out.
- *Recommend:* "This is consistent with the model, in which the reform lowers an informal household's savings from 33% to 27% of the average formal household's in 2010."

**D8. Argentina's "savings rate" counts formal savings only.**
- The cells of table 2 and §5's "−0.4 p.p. of GDP" are formal savings over formal plus informal output. The notes say only "savings relative to GDP".
- Including informal savings gives −0.8 p.p. Under that definition, the economic-equilibrium row's rise, which §5 explains, disappears.
- *Recommend:* keep the definition, since it is the capital stock, and say so: "the savings of formal households, which form the capital stock, relative to GDP". This goes in table 2's note (tables.py:138), figure 5.2's note and §5:32.

**D9. Appendix E points to a comparison §5 no longer makes.**
- HouseholdSurveyArg.tex:36 says "section 5 compares the prediction with the survey" (hours by quartile). The online appendix page arg-leisure says the same.
- *Recommend:* point to the online appendix instead: "and the \oa{arg-leisure} compares the prediction with the survey". Then drop "as section … notes" in arg-leisure.qmd.

**D10. Numerical.tex:3, "immaterial in the equilibrium of proposition 2, which carries no state".**
- With a universal pension, the continuation policy enters the tax condition; proposition 3 makes the claim only without informal households.
- *Recommend:* "immaterial under log-GHH preferences without informal households (proposition 3), but not with a universal pension, under CRRA preferences or with informal savers".

**D11. Optional notation clashes.**
- y is the informal share of GDP (E) and also relative income y_i (B, C, 7.1).
- φ appears in the 'scale' cost (C.2) and as φ_t (B).
- a_i, b_i appear in the Chebyshev step (C).
- *Recommend:* rename E's informal share, e.g. to s_0 or y^0, and leave the rest alone.

## 2. Simple fixes (apply on agreement)

**Sections 1–5**
- Introduction:
  - :27 the timing footnote calls one period ahead "alternative", but it is the paper's timing. → "The corner survives the timing of section 7: at the U.S. calibration the electorate also picks the Beveridgean corner when it chooses the design one period ahead of the benefits it governs, and a permanent choice of the design, an exercise outside the Markov equilibria we study, delivers a corner as well (\oa{esc-timing})."
  - :27 "with the U.S. cost parameter as well" → "at the U.S. cost of redistribution". The countries share ε, not λ.
  - :24 "but with observed design, demography and income distribution representing the OECD figures" → "each with the observed design, demography and income distribution of one of the countries in figure 1".
  - :24 "This predicts" → "The model predicts".
  - :24 "Implementing this reform in our calibrated model accounts for" → "In the calibrated model the reform accounts for".
  - :24 footnote ", see section 6." → " (section 6)."
  - :15 "(Bismarckian--Beveridgean index)" → "(Bismarckian index)".
  - :5 "half mean" → "half-mean".
  - :33 the appendix list → add "the UK and France calibrated in full and the robustness of the cross-country test".
- Abstract keywords in sentence case: "Social security, labor supply, politico-economic equilibrium, heterogeneous agents."
- Model:
  - :16 "normalized such that Σγ_iη_i = 1" is not the normalization used (E normalizes Γ_h = 1). → "and η_i is their labor productivity."
  - Definition 1: :123 τ^{+1}_t(z_{t+1}); :140 τ^{+1}_T(·) = ∅; :147 "τ*_ι = τ^{+1}_{ι−1}(z_ι) for all ι ≥ t"; :142 a space before "for all".
  - Grammar:
    - :3 "and are thus not subject to"
    - :32 "their factor prices"
    - :37 "by a function"
    - :90 "with the lowest productivity"
    - :106 "age-related"
  - :111 heading → `\smalltitle{Economic equilibrium.}`.
  - The labels `6d` and `Argentina` lack the §5 prefix; a stray comment sits at :96.
- Log:
  - :56 β ln(c̃^0_{2,t+1}): the tilde is missing.
  - :66 add a comma before "and relative labor supply".
  - :29 "τ_{t+1} and θ".
- Numerical:
  - :3 T = 2200 is the rich economies' horizon. → "T, 2200 for the rich economies and 2190 for Argentina".
  - :3 footnote "roughly 0.2 p.p., up to 0.3 for Argentina" holds only before the period preceding T: D2.1 shows −0.65 for Argentina at ρ = 0.5 in 2160. → "by up to about 0.2 p.p. before the period that precedes T, and by up to 0.3 p.p. in the Argentine calibration …".
  - :5 "evaluate it at the one consistent distribution"; "add to the state space the ratio …".
- Argentina:
  - :3 "was reformed, tying".
  - :17 cut the meta sentence "The following outlines…" and the footnote that repeats it. → "Appendix E holds the data, the identifying formulas and the sources of the calibration, and the \oa{arg} shows how the design (ϵ, θ) shapes equilibrium outcomes and how other calibrations affect the results."
  - :23 "of the household survey (EPH, appendix E)".
  - :21 "reports the parameters".
  - :21 θ at three decimals, 0.839.
- Not verifiable from the repo: Argentina.tex:3 says "2.7 million added, from about 3 to 5 million".

**Sections 6–8**
- §6:26 the workweek number mixes reference points: tax and savings are corner to corner, the 1.7 hours runs from the baseline. → "…and shortens the workweek by 2.4 hours, 1.7 of them between the observed design and the Beveridgean corner." This keeps §7.1's "1.7 hours (section 6)" valid.
- §7.3, "layer" is never defined. → "The test has two layers. In the first, we solve … In the second, each country's political weight …".
- §7.3 footnote: ε enters unnamed. → "…with ε the elasticity of the Harberger loss in appendix C.2, and let country n face …".
- §7.2:35 needs the index mapping, which now comes after it. → "the design implied by the index of figure 1, θ = 2 − 1/I, exceeds …".
- Appendix H:8 "the inverse of the mapping in section 7.3" → "which inverts the model's index I = 1/(2−θ)".
- Conclusion:
  - :5 add proposition 2's condition: "…with ageing and, when propensities to vote are equal, with income inequality…".
  - :7 "at the U.S. political weight and propensities to vote more unequal countries…". The relation is significant in layer 1 only.
  - :5 "the 2005--2010 expansion of coverage".
  - :9 the referent of "through which" is wrong. → "…, while both the hours responses and the retirees' stake in an earnings-related design work through labor supply".
- "IES" for ρ throughout §7. "Elasticity" currently means both ρ and the participation elasticities in one sentence (:35, also :5, :60).
- Typos:
  - §7:5 footnote, the second "also"
  - :9 "lowers labor force participation"
  - :27 "…nothing: at θ_t = 1, and when all incomes are equal, since …"
  - :55 "towards flatter benefits"
  - :80 "the signs of the three relations"
  - :85 "keep their sign at either" (one variant is insignificant)
- §6:
  - :28 "the latter close to the rise of about 3.6 p.p. in U.S. spending that \textcite{mkvss08} find for a similar fall in population growth"
  - :13 "The three panels report the effects on …"
  - :2 footnote: drop "under the alternative treatment of the taste for leisure" (style guide §5)

**Appendices**
- Algebra:
  - B:132–133 and :171: the CRRA and informal-savings FOCs sum γ_i without μ_i. Insert μ_i.
  - A:96: in c̃^0_{1,t} for informal savers, the bracket needs dividing by 1 + B^0_{t+1}, as at A:90 and B:154.
  - B:105 φ_t = 0.971 → 0.972 at τ = 13.76%, unless it includes a strategic term.
  - H:11 "θ = 0.735, the inverse of its index, 39.2/49.6" → "the one implied by its index I = 39.2/49.6 = 0.790".
- G.1:6 "in the two forms of section 7.3", but 7.3 now gives only ε. → "in two forms: … the U.S. λ = 11.34 (table 12)". The ε it quotes (20.445) is the CPS-group anchor, while the cross-section's is 20.014; say so (D2).
- H:
  - :14 add France's dispersion (0.150 vs 0.218) to what differs.
  - :19 "−0.10 … at the U.S. propensities to vote".
  - :3 cite appendix D for the candidate counts, not section 4.
  - :6 "(ILOSTAT, 2018--2020)" is a plain-text source; move it to a footnote or a bib entry.
  - CSES: spell out once, in F.
- E:24 the Gollin-adjusted shares are in appendix F, not section 6.
- C:51 "The online appendix reports … (\oa{esc-timing})" prints "online appendix" twice. → "The \oa{esc-timing} reports …".
- G:3 mentions "the path of the design along the projected U.S. demography" that the main text never reports.
- F: name the CPS November supplement as the turnout source.
- Sentence-final "U.S." before a capital needs `U.S.\@`: G:6, G:12, H:14.
- Grammar:
  - A:1 heading "Economic equilibrium"
  - A:45 comma → period
  - A:110 "in the form"
  - A:149 "This is the negative of the term above."
  - A:158 "For savings"
  - B: θ subscripts at :138, :145, :181 and :187; :150 missing period; :164 "equilibrium derivative"
  - C:43 "along the calibrated equilibrium path"
  - D:45 "Among the results only the online appendix reports,"
  - G:20 "the path after 2020"
- PDF links: 84 "duplicate destination" warnings, from appendix equation and page anchors. Appendix equation links can land on the wrong target. → add `\renewcommand{\theHequation}{\thesection.\arabic{equation}}` after main.tex:41, or load hyperref with `hypertexnames=false`. Also check that G's footnote at :20 prints ("Hfootnote.49 does not exist").

## 3. Generated tables (fix in python/paper, rebuild)

- Table 5's note, and the notes of the Omega, Robustness and Reconcile tables: λ_n = ε Π_{n,2020}/R_{n,2020} → λ_{n,t} = ε Π_{n,t}/R_{n,t}, as the text and the solver have it (tablesOECD26.py:189).
- US_ESC_Country: the header overruns by 8pt. Use `\footnotesize\setlength{\tabcolsep}{3pt}` as in OECD26_Omega.
- OECD26_Robustness and OECD26_Reconcile notes end with "--: not computed." although neither table has a "--" cell. Print it only when one appears.
- Tables 3 and 8 print θ at two decimals (0.73, 0.56, 1.00); style guide §3 asks for three.
- UK_householdheterogeneity caption: "-- the UK".
- Figure 6.2's legend "model, no cost" names §7's cost one section early. → "model".
- The prose numbers in the footnotes at §7:29 and §7:60 come from `results/numerical/C5_designDecomp*.csv`, which REPLICATION.md lists as read by nothing. Add those rows to REPLICATION.md.
- The style guide §4 still cites "sections 7.3, 7.4", and §2 describes section 7 as two parts; update both.
