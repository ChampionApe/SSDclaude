# The paper's presentation: emphasis, cuts, additions (2026-09-30)

Review note for RKB and MGE, written after a full read of the draft on branch `esc-sizeLeak` (Overleaf in
sync: `pull paper --dry-run` reported 64 files unchanged). §1 is the diagnosis and the thesis I recommend;
§2 the decisions that change what the edit does; §3 the section-by-section recommendation, each with a
target length and the contents in order; §4 what is missing; §5 what to cut or move; §6 inconsistencies to
fix whatever is decided; §7 the order of work. Numbers quoted here are the draft's own (tables are the
source). `notes/paper_styleGuide.md` remains the register; nothing here overrides it.

## 1. Diagnosis

Main text 17.5k words, appendices 8.4k, 45 generated tables, 9 figures. At 12pt and one-and-a-half spacing
that is roughly 50 pages of main text before tables, which is above what most field journals take
(10--12k words is the usual expectation; check the target journal's limit before fixing the numbers below).

| Section | Words | Share of main text |
|---|---|---|
| 1 Introduction | 2,250 | 13% |
| 2 Model | 1,665 | 9% |
| 3 Log-GHH preferences | 1,506 | 9% |
| 4 Numerical methods | 1,535 | 9% |
| 5 Argentina | 1,797 | 10% |
| 6 Rich OECD countries | 3,230 | 18% |
| 7 Endogenous design | 4,854 | 28% |
| 8 Conclusion | 695 | 4% |
| Appendices A--G | 8,410 | -- |

**What the draft contains.** Three layers of results, which do form one arc:

1. *Analytical.* With log-GHH preferences the politico-economic equilibrium is in closed form despite
   heterogeneity and a two-dimensional design; taxes are lower under Bismarckian benefits and higher under
   universal pensions once the share of households outside the contributive system is large (proposition 2).
2. *Quantitative, design given.* Argentina's coverage expansion (the model accounts for about half of the
   observed rise in spending, and the sign of the savings response matches Ruffo); the U.S., France and the
   UK (ageing first, the earnings link second, income inequality and voting patterns minor).
3. *Design chosen.* Without a cost of redistribution the electorate never picks an interior design. With a
   Harberger cost of the flat component that rises with the size of the system, calibrated on the U.S.
   design alone, ageing makes the chosen design more Bismarckian, inequality moves it little, and one
   parameter orders the UK, the U.S. and France as observed.

**What the framing says.** The introduction calls tractability "our main theoretical contribution" (¶6) and
reaches the design choice in ¶10 as an afterthought ("Given the large effects we find ... we next
endogenize"). Figure 1, whose two facts the paper ends up explaining, appears in ¶13 inside the discussion
of Conde-Ruiz and Profeta. The conclusion puts the design result last, after the limitations. Meanwhile
section 7 is 28% of the main text and reads as a technical note: per-ρ number runs in every paragraph, a
"Solution" paragraph, a paragraph of instructions on how to read the tables, a 150-word footnote on
calibration variants.

**The thesis I recommend.** The title is right and can stay. The paper's one sentence: *pension design
shapes the political support for pensions, and political support in turn shapes the design; with the size of
the system as the link, ageing accounts for both the size and the earnings-relatedness of pensions across
rich countries, and inequality for neither.* The arc, in the order the paper should tell it:

> figure 1 (two facts) → model → design shapes taxes (proposition 2) → by how much (Argentina, then the
> three rich economies) → taxes shape design (section 7) → figure 1 answered.

Argentina stays: it is the paper's one validation against an observed reform and the one use of the ε
dimension. It is framed as such, and compressed.

## 2. Decisions that change what the edit does

| | Decision | Recommendation |
|---|---|---|
| D1 | Reposition around the arc above, or tighten in place | Reposition. The results already support it; only the abstract, introduction, section openings and conclusion change their emphasis. |
| D2 | Length target | Main text ≈ 12k words (from 17.5k); appendices in the paper ≈ 5k, the rest in an online appendix. |
| D3 | An online appendix | Yes: the vector-X twins (D.5, F.2), the UK endogenous-design tables (G.2), the scale-wedge table (F.3). The technical note already holds derivations and algorithms. |
| D4 | Additions that cost work (§4) | (a) the equal-weights corner proposition: a proof, no run; (b) ξ robustness for the chosen design: one run; (c) a spending--design panel in figure 1: MGE's data; (d) mild-ageing rows in `US_ESC_Ageing`: a builder change. Recommend (a) and (c); (b) and (d) if time allows. |
| D5 | Argentina: keep compressed, or split into a separate paper | Keep. Splitting orphans the ε half of proposition 2 and the informal-savings machinery of sections 2--4. If a length limit binds hard, Argentina (section 5, appendix D, the informal-savings parts of 2--4) is the separable piece. |
| D6 | The cross-country test moves up to follow the calibration of λ | Yes. It is the identification check on the one free parameter and should be read before any counterfactual. |

## 3. Section by section

Targets are for the main text; "contents" is the order the section should run in.

### Abstract (253 → ≤ 180 words)

Lead with the question, then one sentence per result in the arc's order. Drop "our analysis aligns with
existing results on ..." (it spends a sentence on what is not new) and split the 60-word last sentence.
A candidate, to fix the emphasis rather than the wording:

> Pension systems differ in whether benefits require a contribution record and in how closely they follow
> past earnings. Both features shape who supports the system and therefore its size. We study them in an
> overlapping generations model with capital, heterogeneous households, an informal sector and
> probabilistic voting over the payroll tax. With logarithmic GHH preferences the politico-economic
> equilibrium is in closed form: taxes are higher when benefits are flat and, when the share of households
> outside the contributive system is large, when pensions are universal. Calibrated to Argentina, the model
> accounts for about half of the rise in pension spending after the 2005--2010 expansion of coverage.
> Calibrated to the U.S., France and the UK, ageing is the main determinant of pension spending, the
> earnings link the second, and income inequality and voting patterns minor. We then let the electorate
> choose the earnings link. Without a cost of redistribution the choice is a corner; with a deadweight cost
> of flat benefits that rises with the size of the system, calibrated to the U.S., ageing makes benefits
> more earnings-related, inequality moves the design little, and a single cost parameter orders the designs
> of the UK, the U.S. and France as observed.

### 1 Introduction (2,250 → ≈ 1,700 words)

Contents, with word budgets:

1. *Motivation* (150). Pensions are large; systems differ on two dimensions; design is a political outcome.
   Merge ¶1--2 and cut the duplicate sentence ("A political-economy perspective is therefore critical ..." /
   "Understanding this politico-economic equilibrium is therefore essential ...").
2. *The facts* (200). Figure 1 moved here. Across the OECD, pension spending and the Bismarckian index both
   rise as population growth falls; neither is related to the Gini coefficient. Conde-Ruiz and Profeta
   predict the opposite for inequality. The paper's question follows: can one political process deliver
   the size and the design, and their relation to ageing but not to inequality?
3. *The model* (150). ¶3--4 merged. Informal households in two sentences: they carry the coverage dimension
   and the Argentine application. The platform-work motivation (¶5) goes to one sentence in the conclusion;
   the paper never delivers it.
4. *Result 1, analytical* (120). ¶6 reframed: not "tractability is the contribution" but what the closed form
   shows: taxes lower under Bismarckian benefits, higher under universal pensions once the eligible share is
   large.
5. *Result 2, design given* (170). Argentina as validation (half of the observed increase, savings and hours
   fall modestly, consistent with Ruffo); then the ranking for the rich economies. ¶7 tightened.
6. *Result 3, design chosen* (300, two paragraphs). (a) The corner: the flat component is a pure transfer
   within a cohort, so an electorate with concave preferences wants either all of it or none; every timing
   of the choice gives a corner at U.S. inequality. (b) The cost and its three predictions, with the size of
   the system as the mechanism; one sentence tying each prediction to figure 1. ¶10 rewritten in the plain
   register (it currently has one 70-word sentence).
7. *CRRA* (80). ¶8 cut to three sentences: results robust to the IES except that a higher IES dampens the
   effect of the earnings link on taxes, and why.
8. *Literature* (350). ¶11 and ¶13 merged, in three blocks: the politico-economic equilibrium literature
   (present); the design literature (Casamatta, Cremer and Pestieau 2000; Conde-Ruiz and Profeta 2007;
   Koethenbuerger, Poutvaara and Profeta 2008; add the ones in §4.5); informality and pensions (one or two
   references). The TODO-W1 sentence resolves here.
9. *Roadmap* (100).

Cut ¶9 ("These results yield several contributions"): generic, and its third claim (growth and inequality)
is not delivered.

### 2 The model (1,665 → ≈ 1,450 words)

Keep the structure; it is the paper's skeleton and reads well. Specific points:
- 2.1: "We consider both finite and infinite horizon economies" belongs in section 4 (the paper reports the
  finite-horizon solution).
- 2.3: the "analytical model / numerical model" naming is not used later (the paper says hand-to-mouth vs
  informal savers); drop it and state the two cases where they are used (section 3).
- Informal prices: "proportional to formal sector's factor prices" while the Argentina calibration sets the
  same return on savings for both types. State the constants once (here or in 5's calibration) so the two
  agree.
- The PEE definition is standard and can stay as is; the note after it (fixed point in the infinite
  horizon) can go with the horizon sentence to section 4.

### 3 Logarithmic-GHH preferences (1,506 → ≈ 1,300 words)

Keep both propositions and their discussion; they are the analytical core. Changes:
- Fix the opening: "When performing quantitative analysis, we use the more general CRRA utility" is wrong
  for sections 5--7, where log is the benchmark and CRRA the robustness.
- Proposition 1 part v and the paragraph on informal savings comparative statics can be halved; the
  state-variable paragraph at the end (the informal savings ratio as a state) moves to section 4, where the
  state space is discussed.
- Proposition 2 says "increasing in income inequality". Say which statistic: the model's inequality is the
  between-type dispersion of relative labour income (the same object as Ṽ in section 7), and it is not the
  Gini of figure 1. This one sentence pre-empts a referee's objection to the reading of figure 1.
- Optional, cheap: after proposition 2, state whether Argentina's γ₀ = 0.32 lies above the threshold γ̄₀ of
  its own calibration, so the theory and section 5 connect (section 5's footnote currently says only
  "consistent with proposition 2 if γ₀ > γ̄₀").

### 4 Numerical methods (1,535 → ≈ 600 words)

The technical note exists and the paper cites it; this section only has to say what is computed and why it
is not a steady-state exercise. Contents:
1. One paragraph: date-specific Markov policy functions by backward induction, why the stationary
   approximation is not enough here (three cases: CRRA, informal savers, chosen design), the accuracy
   numbers in a footnote of two sentences (0.2--0.3 p.p. on taxes, up to 0.05 on the design).
2. One paragraph: the state space is at most two scalars and why (proposition 1 iii); the FOC solved on a
   grid with corners and interior roots ranked by the reconstructed objective (no displayed candidate set).
3. One paragraph: path and calibration as a nested fixed point, with the targets left to sections 5--6.
4. Two sentences absorbed from section 7's "Solution" paragraph: under log the chosen design is a
   one-dimensional search at each date; under CRRA a two-dimensional recursion on (s, θ).
The literature argument (Krusell et al., Forni, Song, Galasso) stays as one sentence.

### 5 Argentina (1,797 → ≈ 1,300 words)

Reframe the opening: this is the one experiment in the paper in which the design actually changed, so the
model's prediction is compared with an observed outcome before the model is used for counterfactuals.
Contents:
1. The reform and the data fact (one paragraph, keep figure 2).
2. Calibration (compress to two paragraphs plus the table). Either report the ξ ∈ [0.2, 0.4] robustness the
   text promises, or cut the promise.
3. The reform (keep the table and the paragraph; it is the headline).
4. The ε--θ figure: keep the figure, halve the paragraph (the "always had it" vs impact distinction is the
   useful sentence).
5. CRRA: one paragraph. Keep the table (small) and move the figure to the appendix, or the reverse; not both
   in the main text. The IES-evidence footnote shortened. The "ρ ∈ [1, 2] more plausible" argument stays
   here and is cross-referenced from section 7 rather than repeated.

### 6 Rich OECD countries (3,230 → ≈ 2,300 words)

Contents:
1. Opening (one paragraph): what the section does and the preview. Cut the platform-work paragraph; "We take
   the first of these applications" then goes too.
2. Calibration (compress by a third). The vector-X paragraph (150 words) becomes a two-sentence footnote,
   which is what the style guide's one-pointer rule asks for. Keep the France retirement-age footnote.
3. Pension design and ageing: keep both tables in the main text (they are the two main determinants) and
   the paragraphs as they are.
4. French characteristics: the table stays in appendix G; the discussion shrinks to one paragraph (the two
   headline numbers, the leisure placebo in one sentence, the UK-host sentence).
5. The overview figure and its paragraph: keep; it is the section's summary.
6. CRRA: one paragraph plus the pointer. The mechanism (why a higher IES dampens the effect of θ) is given
   here once and not again in appendix F.1, which currently repeats it.
7. Interpretation (what ω and X absorb): keep, shorter.
8. Closing: the return to figure 1 and the hand-off to section 7. Keep.
Delete the two commented-out paragraphs (Prescott/Alesina hours discussion) from the source.

### 7 Endogenous pension design (4,854 → ≈ 2,800 words)

The headline section, to be rewritten so it reads as a paper section. Proposed structure:

- *Opening* (150). What the section does, one-sentence preview, the pointer to the technical documentation.
  Not a full preview of every result; the introduction does that.
- *7.1 Costless redistribution: a corner* (500). The contemporaneous FOC displayed (it carries the
  intuition) and, if D4(a) is taken, stated as a proposition (§4.2). The advance timing in one paragraph
  with its FOC; the permanent timing in three sentences or a footnote. The "common lesson" sentence is the
  subsection's last.
- *7.2 A deadweight cost of redistribution* (900). The budget with f; the three arguments; the
  tax-component reading (Summers, Disney, Kumler et al.) in one paragraph; the Harberger derivation in three
  sentences; the A/B substitution in two; the magnitude of λ against elasticities kept, shorter, framed up
  front as: λ is a reduced form and the cross-country test is its discipline. The timing choice in three
  sentences. Keep the mechanism ∂A + ∂B = f_θ ≥ 0 (it is what makes the interior possible); drop equation
  (esc:leadFOCcost) to the technical note.
- *7.3 Calibration and a cross-country test* (500). The calibration equation and table
  `US_ESC_Calibration`; then, moved up from the end, the cross-country test with table `US_ESC_Country` in
  the main text: one parameter, three countries, the ordering reproduced, the UK's own λ, France's corner
  out of reach and why (the C5 sentence). Fix "within 16%" (§6).
- *7.4 Ageing, inequality and voting patterns* (750). Two sentences on the baseline drift (0.738 to 0.81 by
  2110 at ρ = 1, the tax from 14.4% to 20.9%); the overview figure; one paragraph per counterfactual quoting
  ρ = 1 in the text and the range across ρ in one clause; the composite in three sentences.
- Cut: the "Solution" paragraph (to section 4); the reading-instructions paragraph ("Baseline path") to two
  sentences plus a table note; the common-X footnote to one sentence; "the placebo the construction implies".

### 8 Conclusion (695 → ≈ 450 words)

Contents: (1) what the paper does, three sentences; (2) the findings in the arc's order, the design result
as the climax rather than after the limitations, in fewer words than section 7's opening; (3) limitations
and future work: no risk (BergGEwp), France's corner (a linear term, or the formality margin of the
Argentine model), platform work in one sentence. Fix the units (§6).

### Appendices (8.4k → ≈ 5k in the paper; the rest online)

| Appendix | Recommendation |
|---|---|
| A--C proofs, PEE derivations, terminal states | Keep. Check whether B.3 (CRRA with informal savings) is needed in the paper or only in the technical note. |
| D Argentina calibration | Cut the three paragraphs on the EPH's rotation design to one; keep the pension-system formulas. D.5 (vector-X) online. |
| E OECD heterogeneity tables | Keep the three countries; E.4--E.5 (regroupings) online, or keep only if the UK exercise stays in the paper. |
| F U.S. robustness | Keep F.1 (CRRA) without repeating section 6's mechanism. F.2 (vector-X, 11 tables and a figure) online. F.3: keep `US_ESC_Ageing`; the scale-wedge table online, and if kept, its text rewritten as a specification comparison, not "an earlier draft". |
| G UK vs U.S. | Keep G.1 (host independence with the design given) with the figure and one table per host. G.2 (endogenous design on the UK, three tables) online; its message, that the design response stays in the design, fits in one sentence of section 7.4. |

The online appendix needs a second root file in `writing/Paper` (sharing `Packages.tex` and `Tables/`);
check that `overleaf.py export` accepts a second root before relying on it.

## 4. What is missing

1. **The size--design relation in the data.** The mechanism of section 7 is that a larger system is
   costlier to keep flat, so spending and the Bismarckian index should co-move across countries. Figure 1
   shows both against population growth and the Gini, not against each other. Add a panel (or replace one
   Gini panel) and put the correlation coefficients in the footnote. Also: the footnote says 29 countries
   and the figure shows about 20 markers; check which are missing and say so.
2. **The corner as a proposition.** With equal propensities to vote, the contemporaneous FOC (esc:seqFOC)
   is a weighted sum of (y_i − 1), which averages to zero, against 1/D_i, where D_i is increasing in y_i
   (relative savings are linear in y_i with positive slope, proposition 1 iii, and the second term rises
   with y_i for θ ≥ 0). By Chebyshev's sum inequality the sum is negative for every θ ∈ [0, 1], every ω, ν
   and τ: the contemporaneous choice is the Beveridgean corner for any parameters, and only voting weights
   that rise with income can overturn it. Proof to verify, but it turns a numerical statement into a
   result and makes the quantitative role of μ_i explicit. The advance timing stays quantitative.
3. **Frisch elasticity in section 7.** The design channel runs through hours, and "for reasonable labor
   supply elasticities" is asserted. One row (ξ = 0.2, 0.4) for the baseline chosen design and the
   acute-ageing response at ρ = 1 would close it. Needs a run.
4. **A time-series check.** The model predicts the design drifts Bismarckian along the demographic
   transition. The notional defined-contribution reforms of the 1990s (Sweden, Italy, Latvia, Poland) and
   Germany's points reform tightened the earnings link in fast-ageing countries; one sentence with a
   reference (Holzmann and Palmer 2006, to check) would give the prediction an empirical anchor.
5. **References the design literature will expect.** Tabellini (2000, SJE, "A positive theory of social
   security"): within-cohort redistribution sustains pensions through a coalition of the old and the poor
   young, which is exactly the force behind the corner in 7.1. Galasso and Profeta (2002, EJPE) survey.
   Cremer, De Donder, Maldonado and Pestieau (2007, JPubE): voting over the type and the generosity of a
   pension system. Bethencourt and Galasso (2008, JPubE) on health and pensions as political complements,
   since the U.S. calibration adds Medicare. Galasso and Profeta (2004, Economic Policy) on ageing and the
   political sustainability of designs. For informality and pensions, Levy (2008). All to check before
   adding.
6. **What "inequality" is in the model.** One sentence in 7.4 that the model's inequality is the dispersion
   of relative labour income across the three groups at the chosen income cuts, so figure 1's Gini is a
   different object (the notes behind the branch make this point; the paper does not yet).

## 5. What to cut or move (summary)

- Section 4's literature argument and accuracy footnote → technical note (already there); section 7's
  "Solution" paragraph → section 4.
- Platform work: three appearances → one sentence in the conclusion.
- The vector-X calibration: one footnote per arm (style guide rule) and the twin tables online.
- Section 7: reading instructions, the common-X footnote, equation (esc:leadFOCcost), per-ρ number runs,
  the scale-wedge history.
- Appendix D's survey description; appendix F.1's repeated mechanism.
- Two commented-out paragraphs in `OECD.tex`; the `TODO-W1` tag in the introduction.

## 6. Inconsistencies to fix whatever is decided

1. "Within 16%" (section 7 and the conclusion): true at ρ = 1 (7.264 vs 8.643); at ρ = 2 the UK's own λ is
   61% above the U.S. one (2.786 vs 1.728), as appendix G.2 says. TODO W7(b).
2. France's LIS survey year is stated nowhere; section 6 implies 2019. TODO W7(a).
3. Section 3's opening sentence on CRRA in the quantitative analysis (§3 above).
4. Equation (esc:seqFOC) is displayed with "≤ 0 for θ ∈ [0, 1]" and the text says the sign is a quantitative
   matter. Display the derivative; state the sign in the text (or as the proposition of §4.2).
5. Conclusion: labour supply falls "about 0.3%" where section 5 gives 0.15 hours a week; savings "0.3 p.p.
   of GDP" matches. Argentina's "1.25 p.p." breaks the one-decimal rule of the style guide.
6. Introduction: coverage "91% of retirees by 2010"; section 5: "almost universal". Use one number in both.
7. Figure 1's footnote: 29 countries vs about 20 markers (§4.1).
8. Section 6's footnote: a U.S. Gini of 0.59 is a market-income figure; say which series and concept.
9. Section 7 cites mild ageing at ρ = 1 (0.784) from table `US_ESC_Ageing`, which carries only the
   acute-ageing rows. Either add the rows (D4(d)) or cite the csv-free sentence without the table.
10. Section 2 vs section 5 on informal prices (§3, model).
11. Section 6 opening: "We take the first of these applications" reads oddly once the paragraph before it
    is cut.

## 7. Order of work

1. RKB (with MGE): D1--D6 and the length target.
2. Section 7 first: it is the largest cut and the headline, and everything else is written against it.
3. Section 4 (cut), then the introduction and abstract (written against the final section 7).
4. Sections 6, 5, 3, 2, in that order; then the conclusion.
5. Appendices last: the moves are `\input` edits plus the online-appendix root; no number changes.
6. Runs needed only for the optional additions: ξ robustness (§4.3), mild-ageing rows (§6.9), figure 1's
   panel (MGE's data). The proposition (§4.2) needs no run.

Every table and figure stays generated; prose numbers are checked against the table next to them at each
step (style guide §7).



## DECISIONS (RKB, 26-09-30)
D1. Reposition.
D2. No specific length target yet.
D3. Yes to online appendices. We can decide the split later.
D4. Yes to (a), (b), and (c).
D5. Keep compressed.
D6. Agreed.

## 8. Work plan (2026-09-30, after the decisions; supersedes §7)

Five working sessions, each closed by a review gate. The main session writes the pieces where one voice
matters (section 7, then the abstract, introduction and conclusion) and orchestrates the rest. Agents run
in parallel worktrees, one file set each, and are of two kinds: *forks*, which inherit this session's
reading of the draft, the plan and, from gate 1 on, the accepted section 7 with RKB's comments, so their
prose blends; and *fresh* agents, for work where the paper context is ballast (a compute run, reference
checks) or where independence is the point (the referee pass, the number audit). Fresh sessions use this
section as their entry point.

### Ground rules

- One branch, `paper-rewrite`. `esc-sizeLeak` is 23 commits ahead of `main` and `main` has not moved, so
  it fast-forwards; RKB's call at gate 0 whether to merge first (recommended: the Overleaf copy already
  *is* the branch) or to open `paper-rewrite` off `esc-sizeLeak`.
- Every agent touches only the files its brief names, and the briefs of one session are disjoint.
  **Worktree isolation is conditional** (2026-09-30): a subagent worktree is cut from `origin/HEAD` unless
  `.claude/settings.json` carries `{"worktree": {"baseRef": "head"}}`, and `main` is ahead of `origin`,
  so without that line a worktree would check out the paper as it was before the size-leak branch. RKB
  added the line on 2026-09-30 (the auto-mode classifier had refused it from the session), so agents run
  in worktrees and commit there, and the main session merges after the gate. Should the file ever be
  missing, agents work in the main checkout, commit nothing, and the main session commits per file after
  the gate; the per-file diff is the review object either way. A worktree holds committed files only: `results/` is tracked and present,
  `.venv/` is not, so agents call the repo's interpreter by absolute path. Generated tables and their labels
  are never edited; a number that must change goes through `python/paper`.
- Pending numbers are written as `\todo{...}` per the style guide, listed in the agent's report, and
  cleared before the final gate. Every agent's report has one shape: word count before and after, what
  moved where, which tables each quoted number was checked against, what is unresolved, what it ran.
- `writing/checkPaper.py` (built in session 1, ~50 lines): every `\ref`/`\eqref` target exists, every
  cite key is in the bib, word count per section, the `\todo`/`%% TODO` list, `---` count per paragraph,
  a control-byte scan. Run by every agent before it reports and by the main session at every gate.
- RKB compiles locally at each gate; Overleaf is pushed at gates 3 and 5 only (pull first). MGE is asked
  to keep online edits to comments until gate 3, or to say which sections he edits.
- `pull paper --dry-run` at the start of every session.
- **Models and effort (RKB, 2026-09-30).** Every agent runs on Opus 5.5 at xhigh or max effort, through
  the project agent definitions in `.claude/agents/`: `paper-writer` (max; prose, proofs, appendix
  restructuring), `paper-reviewer` (max; read-only audits), `paper-compute` (xhigh; runs and builders),
  `paper-data` (xhigh; data collection with web access). A fork runs on the parent session's model and
  ignores a model override, so a fork is used only when the session itself is on Opus 5.5; otherwise the
  same work goes to a `paper-writer` whose brief names the files a fork would have inherited: this note,
  `notes/paper_styleGuide.md`, `CLAUDE.md`, the draft, and from gate 1 the accepted section 7 as the
  exemplar of the voice. Briefs are written so that either kind can do the job. The frontmatter pins
  `model: claude-opus-5-5` (the `opus` alias moves) and `effort`, which overrides the session's level; a
  per-call `model` argument would override the pin, so none is passed. The agents folder is new, so the
  session is restarted once before the first spawn.

### Gate 0 (RKB, before session 1)

1. The branch: done 2026-09-30. `main` fast-forwarded to `77ba943` (the whole of `esc-sizeLeak`) and
   `paper-rewrite` opened from it; P1 in `notes/TODO.md` closes with it.
2. MGE is not a dependency. The figure 1 data work is agent A4 (session 1, below), which also settles
   France's LIS survey year (W7a) from the workbook; he reads at gates 3 and 5 and gets one line with the
   Overleaf push at gate 3, including the request to keep online edits to comments while a section is
   under rewrite.

### Session 1: section 7, and three independent pieces

Main session: rewrites section 7 per §3 (four subsections, labels fixed now so later sessions can point at
them: `sec:esc:corner`, `sec:esc:cost`, `sec:esc:calibration`, `sec:esc:results`), with two placeholders:
`%% TODO-PROP3` where the proposition is stated and `\todo{xi: ...}` where the ξ result goes. Since D4(d)
is not taken, the mild-ageing number (0.784) leaves the text unless RKB asks for the builder change. Builds
`checkPaper.py`. Spawned at the start of the session, in parallel:

| Agent | Kind | Brief | Stop condition |
|---|---|---|---|
| A4 figure 1 data | `paper-data`, worktree | Rebuild figure 1 from its sources, which footnote 5 of the introduction names: pension spending (% of GDP), population growth as population 2020 over 1990, and the Bismarckian--Beveridgean index as the ratio of OECD replacement rates at mean and at half-mean income, all OECD; the Gini coefficient from the World Income Inequality Database; the 29 countries listed there; 2020 or the nearest year, recorded per country. Deliverables: (i) `data/oecdFigure1.xlsx` (or csv) with one row per country, every column sourced (series, table, vintage, year used) in a Readme sheet, as `FRMain.xlsx` does; (ii) a stage (0) script in `python/paper/` on the `dataTargets.py` pattern, the only stage with network access, that reads the saved data and writes the figure in the house style of `python/paper/figures.py` to `results/paper/Figs/OECDdata.pdf`, registered in `build.py`, with a fifth panel, spending against the index, or a 2×3 layout; (iii) `results/paper/oecdCorrelations.csv`: pairwise Pearson and Spearman correlations with n per pair; (iv) a report: which of the 29 countries lack which variable (the footnote says 29, the figure shows about 20 markers), the WIID series and income concept behind the U.S. value of 0.59, whether the re-collected data reproduce the current `Figs/OECDdata.eps` point by point, France's LIS survey year from the Readme sheet of `data/FRMain.xlsx`, and the footnote rewritten to state the sources exactly. The existing EPS and the `\includegraphics` line stay untouched: the switch is a gate 1 decision. | A source that no longer serves the series (report the replacement, do not substitute silently); re-collected data that do not reproduce the EPS (report both, e.g. gross vs net replacement rates, men vs both sexes, rather than choose); a country with no 2020 value within two years is reported as missing, not interpolated. |
| A1 corner proposition | `paper-writer`, worktree | Verify the Chebyshev argument of §4.2 against appendix B's expressions (relative savings linear in $y_i$ with non-negative slope; $\sum_i\gamma_i(y_i-1)=0$). Write the proposition and proof as a new subsection of `Appendix/PoliticoEconomicEquilibrium.tex` and return a five-line statement for 7.1. Sanity check, reported not published: the sign of (esc:seqFOC) with equal $\mu_i$ on a θ grid at the 2020 U.S. calibration, through `python/US/thetaStakes.py` or the model directly. | The proof fails: report where, and 7.1 stays a quantitative statement. |
| A2 ξ robustness | `paper-compute`, worktree | At ρ = 1 (LOG), ξ = 0.2 and 0.4: recalibrate (β, ω) from the workbook model (ξ is a workbook parameter, `python/US/test.py`), calibrate λ so the 2020 design is 0.738 (θ* is read off relative incomes and does not depend on ξ; assert it), report the baseline chosen design and its drift (2050, 2080, 2110), the tax path, and acute ageing pinned and chosen. A standalone driver in `python/US/` on the `runESC.py` pattern writing `results/esc/escXiRobustness.csv`; nothing headline is touched. Self-check first: at ξ = 0.3 the driver must reproduce λ = 8.643, the drift 0.797/0.804/0.809 and acute ageing 0.825. Log entry in `python/US/RESEARCH_LOG.md`, README status line. Budget half a day of compute in the background. | The λ bracket fails at a ξ (report the scan); a corner at some ξ is a result, not a failure. |
| A3 references | `paper-data` | Verify with web search the candidates of §4.5 (Tabellini 2000; Galasso and Profeta 2002, 2004; Cremer, De Donder, Maldonado and Pestieau 2007; Bethencourt and Galasso 2008; Holzmann and Palmer 2006; Levy 2008): exact titles, journals, volumes, pages. Add biblatex entries to `writing/Paper/References.bib` in the file's own style and return two lines per paper on the result relevant to us, for the introduction and 7.1. No citations inserted. | A reference that cannot be verified is reported, not added. |

**Gate 1 (RKB, end of session 1 or the next morning).** Read section 7 compiled. What to check: the
four-part structure and the placement of the cross-country test; the voice, since this draft is the
exemplar every later writer is pointed at; that every number quoted stands in a table beside it. Then A1's
proof (with MGE if he wants to see it), A2's numbers for sanity, A3's entries, and A4: whether the rebuilt
figure replaces the EPS, which panel layout, and the footnote. Sign-off merges the four worktrees; no
Overleaf push yet unless MGE wants section 7 early. *Session 1 done 2026-09-30: the four reports and the
checklist are condensed in `notes/paper_gate1.md`, whose DECISIONS block is where RKB records the gate 1
calls; the paper was pushed to Overleaf for the read at RKB's request, and the agents ran in the main checkout
(no worktrees; see the note's §6).*

### Session 2: the four independent cuts, in parallel

Four `paper-writer` agents spawned after gate 1 (forks if the session is on Opus 5.5), one worktree and
one section file each, every brief naming the accepted section 7 as the exemplar. Interfaces are fixed in
the briefs so nothing is duplicated or lost: B1 receives, B4 deletes.

| Agent | Brief |
|---|---|
| B1 section 4 | To ≈ 600 words per §3. Receives section 7's two sentences on the design solution (1-D search under log, 2-D recursion on (s, θ) under CRRA), section 2's horizon sentence and section 3's closing paragraph on the informal savings state. |
| B2 section 6 | To ≈ 2,300 per §3. Deletes the two commented-out paragraphs; the vector-X paragraph to a two-sentence footnote; CRRA to one paragraph, and it names the sentence appendix F.1 must then lose (done in session 4). The closing hand-off cites `sec:esc:corner`. |
| B3 section 5 | To ≈ 1,300 per §3. The ξ ∈ [0.2, 0.4] promise is cut (no Argentina run is commissioned). The CRRA table stays; the figure environment moves to the end of `Appendix/HouseholdSurveyArg.tex`, label unchanged. |
| B4 sections 2–3 | The edits of §3: the CRRA sentence, the "analytical/numerical" naming, the horizon sentence and the state paragraph deleted (B1 has them), the inequality-statistic sentence after proposition 2, the informal-price constants stated once. Optional: γ̄₀ for Argentina's calibration, only if appendix B's threshold is explicit and computable from `results/`; otherwise say so. |

Main session meanwhile: folds A1's statement into 7.1 and A2's result into 7.4 or a footnote; first-line
review of the four diffs (style guide §7 checklist, cross-references, numbers) before RKB sees them.

**Gate 2 (RKB).** The four diffs, or the compiled sections 2--6. A lighter review: cuts, not new claims.
Sign-off merges.

### Session 3: the framing (main session, no forks)

Abstract, introduction and conclusion written by one hand against the final sections 3--7, with A3's
references and A4's figure and footnote; the `TODO-W1` tag resolves here. Then one `paper-reviewer`:

| Agent | Brief |
|---|---|
| C1 referee pass | Read the tex of the whole draft without this session's priors. Return: every claim in the abstract and introduction not delivered by a section; every number in prose that does not match the table or figure beside it; terminology that drifts from the style guide's §4; the three places a referee would push hardest. Report only. |

**Gate 3 (RKB, then MGE).** The highest-value review: abstract, introduction, conclusion, and C1's list.
Push to Overleaf for MGE (pull first); his edits come back through `pull` and are applied on the branch.

### Session 4: appendices and the online split

D3's split is decided at this gate. Two `paper-writer` agents:

| Agent | Brief |
|---|---|
| D1 online root | `\newif\ifonline` in `main.tex`, an `online.tex` wrapper that sets it and inputs `main`, the online sections behind the switch; confirm `overleaf.py export paper` accepts the second root (inspect the zip) and fix `overleaf.py` if it does not. |
| D2 appendices | Per §3's table: appendix D's survey description to one paragraph, F.1 without section 6's repeated mechanism, G restructured, the scale-wedge text as a specification comparison if kept. Every label kept; `\FloatBarrier` before every (sub)section as now. |

Main session: the §6 inconsistencies not yet folded into section work (the LIS year, the Gini concept and
the country count come from A4's report).

**Gate 4 (RKB).** Compile both roots; every appendix reference from the main text resolves; the split.

### Session 5: consistency and close-out

| Agent | Brief |
|---|---|
| E1 number audit | `paper-reviewer`: section by section, every number, sign and unit in prose against the table or figure beside it (style guide §3). Report only. |

Main session: fixes from E1, `checkPaper.py` clean with no `\todo` left, the final Overleaf push (both
projects if the proposition or the ξ run touched the technical note), then the housekeeping: `notes/TODO.md`
(W7 closed, P1 resolved, C5 stays), the root `RESEARCH_LOG.md` entry, README status lines where outputs
changed, and this file to `archive/notes/` with a pointer from the log.

**Gate 5 (RKB, then MGE).** The final read; merge `paper-rewrite` into `main`.

### Timeline and risks

Five sessions and five turnarounds; gates 1, 2 and 4 can be same-day, and nothing waits on MGE: his read
at gate 3 runs alongside session 4. About two weeks of calendar time. Risks: (S1) the proposition fails,
at no cost to the text; (S2) the ξ run overruns or fails to bracket, and becomes a one-line footnote or is
dropped; (S3) MGE edits online sections under rewrite, and the pull conflicts are merged by hand at the
gate; (S4) once D2 is set, the draft is still long, and the second pass goes to sections 6 and 7, not to 2
and 3; (S5) A4's re-collected data do not reproduce MGE's figure, in which case gate 1 decides which
concept the paper uses and the footnote says so. Not recommended: parallel agents for the abstract,
introduction and conclusion (one hand), or agents for the one-line fixes of §6 (done inline during the
section work).