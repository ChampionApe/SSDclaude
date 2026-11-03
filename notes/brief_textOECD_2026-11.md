# Brief: the text pass after the switch to θ variant C and RKB's decisions of 2026-11-02

Every writer follows `notes/paper_styleGuide.md` and works on its own file set.
- **Numbers.** Take them only from generated outputs (tables and figure notes in `writing/Paper`, marks in
  `results/paper/Figs/*.marks.json`) or the csvs they name; never from memory or an older draft.
- **Generated files.** Never hand-edit a generated `.tex` (banner `%% GENERATED`).
- **No compiling.** Do not run latexmk; I compile at the end and send back any errors.
- **History.** The paper never narrates what changed or was tried.
- **Report.** What you changed (file:line), every number you introduced with its source, and what you left open.

## RKB's decisions (2026-11-02)
- **D1. Section 7's motivation is review point O3.**
  - Section 6 confirms that ageing drives pension spending and inequality does not. But its theory says that at a
    given demography a more Bismarckian design lowers the tax (proposition LOG:PEE; 6.7 p.p. from corner to corner
    at ρ = 1, figure 6.1). Figure 1.1 shows spending rising with the index, and the index rising as population
    growth falls.
  - Section 7 resolves this. Under the deadweight cost the tax is hump-shaped in θ at a given demography: below the
    electorate's preferred design a more Bismarckian design raises the tax, since less revenue is lost; above it
    the design lowers the tax, as without the cost. And ageing raises both τ and θ.
  - The sentence "although at a given demography a more Bismarckian design lowers the tax" goes.
- **D2. The cross-section's main specification** is θ variant C, each country's own propensities to vote (CSES),
  and layer 1 at the U.S. anchor's ω. It has 20 countries: figure 1.1's 21 less Luxembourg, which has no CSES survey.
  The anchor is the U.S. measured like every other country (OECD earnings data, CSES turnout).
  - Two stylized readings are robustness, in appendix H. One sets every country at the average political weight;
    it moves levels, not the cross-section. The other pools the turnout (the U.S. at its own profile, Australia,
    Belgium and Luxembourg flat, the rest at the voluntary average); it matches own turnout on the same 20 countries,
    and Luxembourg is the outlier in layer 1.
  - The source for both is `logs/variantCompare/summary_2026-11.md`, and the paper's table `OECD26_Stylized`.
- **D3.** Design A (`OECD26_ThetaFit`, predicted against observed θ) goes in section 7.3; design E
  (`OECD26_ThetaFitGrid`) in appendix H.
- **D4.** The θ measure gets one sentence in the introduction and a paragraph in appendix H.1. θ is the
  earnings-linked share of the least-squares line through the public pension at 0.5, 1 and 2 times average earnings
  (Pensions at a Glance 2021, men, 2020 rules), times one minus the share of public spending on minimum top-ups and
  tested benefits.
  - The sample is 21 countries: informal employment below 25% of employment, and one public pay-as-you-go system
    paying the bulk of benefits. Figure 1.1's note states the rule.
  - U.S. 0.544, France 0.822, UK 0.181.
- **D5.** The robustness of the measure covers C, A and B only, in appendix H (`OECD26_ThetaVariants`).
- **D6.** Appendix H.5 (measured twice) goes. Appendix F.3 (the UK's calibration) and appendix G (the UK and France
  calibrated in full; the design along the path) move to the online appendix: `\oa{oecd-uk}`, `\oa{esc-countries}`,
  `\oa{esc-paths}`.

## Stale numbers
The switch to variant C changed every model number. The audit is `notes/staleNumbers_2026-11-02.md`: stale values,
claims that no longer hold, and numbers that are correct. Fix each item in your files from the sources it names.

**Pending reruns, leave unchanged:**
- the 70/30 footnote (`EndogenousTheta.tex:29`);
- the three-step decomposition footnote (`EndogenousTheta.tex:60`) and the attribution to "the third force" (keep
  the sentence's other claims correct);
- appendix C's critical turnout ratios (`EndogenousDesign.tex:43`) and πPath (`:70`);
- appendix D's numbers (`TerminalStates.tex:40–48`).

**Dropped runs:**
- The timing checks and the permanent choice: claim only the variant-C check (the costless choice one period ahead
  under log preferences is the Beveridgean corner) and the analytical result (proposition esc:corner). Drop the
  permanent-choice footnote.
- Medicare: drop the sentences and pointers.

## Writers and file sets
**W-a (lead): `Sections/OECD.tex`, `Sections/EndogenousTheta.tex`.**
- **Phase 1.**
  - Fix all stale numbers and claims in section 6 up to the cross-section, and in 7.1–7.2.
  - Write the O3 framing: the end of section 6 states the puzzle; section 7's opening says the section resolves it.
  - Replace references to appendix G (`app:escResults*`, "the UK and France calibrated in full") with `\oa{}` pointers.
- **Phase 2** (after the pipeline report): rewrite section 6's cross-section paragraph and section 7.3 at own
  turnout.
  - Section 6: 20 countries, figure 6.2's slopes from its note.
  - Section 7.3:
    - the anchor's values;
    - figure 7.2 and table 5, with spending now at the chosen design;
    - the tax against a pinned design (O3's resolution, from the pipeline's T7 figure note);
    - design A with r, RMSE and the compression: the model's designs spread a third to a half as much as the observed;
    - inequality and turnout: at own turnout neither spending nor the index moves with the Gini, as in the data; at
      the U.S. propensities to vote the index falls with the Gini and the design is barely predicted;
    - pointers to appendix H.
  - Remove the corner explanation ("two countries at the Beveridgean corner and six at the Bismarckian one").

**W-b: `Sections/Introduction.tex`, `abstract.tex`, `Conclusion.tex`.** Runs after W-a, so that it summarises
W-a's final text.
- Figure 1.1's description: D4's sentence and 21 countries.
- The cross-section claims at own turnout, and the stale numbers and claims in the audit.
- Remove the deep test and "six of the 26 countries".

**W-c: `Appendix/OECD26.tex`.** After the pipeline report.
- **H.1:** the sample (21; 20 in the test) and D4's paragraph.
- **H.2:** the U.S. at these data, the anchor at OECD earnings and CSES turnout.
- **H.3:** layer 2, `OECD26_Omega`.
- **H.4:** the measures (`OECD26_ThetaVariants`), the turnouts (`OECD26_ThetaFitGrid`) and the stylized readings
  (`OECD26_Stylized`).
- **H.5** deleted, with the `\input` lines of `OECD26_Robustness` and `OECD26_Reconcile`.

**W-d: `Appendix/CalibrationOECD.tex`, `Appendix/EndogenousDesign.tex`, `Appendix/PoliticoEconomicEquilibrium.tex`,
`Appendix/EconomicEquilibrium.tex`, `Appendix/TerminalStates.tex` and `main.tex`.**
- The stale numbers and claims in the audit, except the pending items.
- Remove F.3 (the UK) and the UK from F's title and text; F's table keeps `table:US:Calib` (the U.S. and France).
- Remove the `\input` of `Appendix/EndogenousDesignResults` from `main.tex`.
- Replace references to appendix G with `\oa{esc-countries}` or `\oa{esc-paths}`.

**W-e: `writing/OnlineAppendix`.** After the pipeline report.
- Prose for the new pages B6 `oecd-uk` (from F.3) and C7 `esc-countries` (from G.1), and G.2's prose in C1
  `esc-paths`, following `writing/OnlineAppendix/README.md` (no typed numbers).
- Check that C6 `esc-oecd26` and D1 `data` match D2 and D4.
