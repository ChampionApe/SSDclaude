# Brief R1: referee pass on the endogenous-design rewrite (section 7, appendices C and G)

For the `paper-reviewer-lead` agent (read-only). The rewrite's plan is `notes/plan_endogenousDesign.md`
§B (RKB's outline, binding in its order) and §C.1 (the session's decisions); the economics is
`notes/esc_variants.md` (§7 the version under the $M$ weight, the paper's; §1-§6 the derivation). Read
the plan, then the three files as a referee would, then the note only to check a derivation step.

## 1. Files

- `writing/Paper/Sections/EndogenousTheta.tex` (section 7), with `Tables/US_ESC_Variants.tex`,
  `Tables/US_ESC_Results.tex` and `Figs/US_ESC_Path.pdf` (its marks: `results/paper/Figs/US_ESC_Path.marks.json`).
- `writing/Paper/Appendix/EndogenousDesign.tex` (appendix C).
- `writing/Paper/Appendix/EndogenousDesignDetails.tex` (appendix G), with `Tables/US_ESC_VariantsCountry.tex`,
  `Tables/US_ESC_VariantsShocks.tex`, `Tables/US_ESC_Calibration.tex`, `Tables/US_ESC_Summary.tex`.
- For consistency only: the cost sentences of `Sections/Introduction.tex`, `abstract.tex` and
  `Sections/Conclusion.tex`.

## 2. What to check, in order of cost to the paper

1. **Claims delivered.** Every claim section 7 makes about a variant, a calibration or a counterfactual
   is in a table or figure the section cites, with the number as printed; every "appendix C shows" is
   shown there; every "appendix G reports" is reported there.
2. **The derivations.** Appendix C.2's general form and its properties (nothing lost at $\theta_t = 1$
   and at $M = \tilde V = 0$; the share lost rising in $\tau_t$; $\partial\ln f/\partial\tau_t = \ln f/\tau_t$;
   the first unit's marginal cost $\lambda_1\tau_t M$); proposition `prop:esc:bismarckCorner` and its proof,
   step by step in the paper's notation (`eq:esc:leadFOC`, `eq:esc:auxiliary`, the young's consumption,
   the return), the sign and order-$\tau_{t+1}$ claims; the generalised design condition in C.3; that the
   weight of each term is what its derivation gives and the $\tau_t$-scaling of the linear term is owned
   as a choice with its cost.
3. **The economics as told.** Section 7.1 follows RKB's order (diagnosis; the implicit tax and the
   intensive margin the model has; the literature in its four blocks; the variants). Does the leaky-bucket
   reading of the linear and quadratic terms hold together; is the "France's corner is what the UK's design
   rules out" reading supported by the variants table; is the linear cost presented as the limit and not as a
   peer; is the $\rho$ paragraph honest that the other variants are computed at $\rho = 1$.
4. **Style** (`notes/paper_styleGuide.md`): vocabulary of §4 (no new synonyms for $\theta$, the cost, the
   readings), numbers per §3, cross-references lowercase, at most one `---` per paragraph, no narration of
   the research process, footnotes as full sentences, the section's own notation matching the older
   sections ($\partial f/\partial x$, dated symbols, "the inherited design").
5. **Placement, not length.** RKB has set no target length (2026-10-08: cuts come later if needed), so
   length is not a finding. What is: material in the main text that belongs in an appendix or the online
   appendix by the paper's own convention (derivations, solver detail, robustness), and material in
   appendix C whose absence a referee would not notice (say which passages, for RKB's later call, in the
   separate list of §3).

## 3. Report

Findings ranked by cost with a referee, each with `file:line`, the claim as written, the evidence and the
fix in one sentence; then the three places a referee would push hardest and why; then, separately and not
as findings, the cut list for appendix C that the plan's phase W5 will execute (RKB wants it close to its
pre-rewrite length, with propositions 4 and 5 and their proofs in the technical documentation only): which
sentences of C.2's specification and corner paragraphs the paper must keep for section 7's claims to be
supported, and which can go to the technical note with the propositions, with the lines. At most 60 lines.
