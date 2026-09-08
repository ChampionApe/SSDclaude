# Style guide for the paper draft (`writing/Paper`)

Synthesized from the current draft on 2026-09-08, for the rewrite sessions. It describes how the
existing sections are written so new text blends in, and picks one register where the draft currently
has two. The technical notes under `writing/<model>/` follow their own conventions and are not covered.

## 1. Voice and register

- **First person plural, present tense.** "We calibrate", "we find", "the model predicts", "table X
  shows". Past tense only for history (Argentina's reforms, what earlier papers did).
- **Plain academic register.** The target is the register of the model, log-preference and Argentina
  sections: claims stated directly, mechanisms explained in one or two sentences, no flourishes.
  The sections written in September 2026 (endogenous θ, the later OECD paragraphs) drift toward a
  more rhetorical register — dashes mid-sentence, "in disguise", "the exercise's placebo", "a negative
  result worth stating plainly", "which is the tension the introduction's cross-section poses". Tone
  these down when they are revisited: keep the content, drop the meta-commentary and the second clause
  that restates the first for emphasis.
- **Dashes.** The older sections use none. Allow at most one `---` per paragraph, for a genuine aside;
  otherwise start a new sentence.
- **Hedging is calibrated, not defensive.** "about", "roughly", "a bit less than", "consistent with",
  "in line with", "suggests". Do not hedge model results that are exact ("the tax rate increases by
  6.2 p.p."); do hedge the mapping to data ("consistent with available evidence").
- **No narration of the research process.** The paper never says what was tried and abandoned in the
  main text; alternatives not pursued go in a footnote, stated as a choice with its cost (see the
  footnote on the placement of the deadweight wedge, or on holding θ fixed in the inequality
  counterfactual). Development history stays in `notes/` and the logs.

## 2. Paragraph and section anatomy

**Sentence order inside a results paragraph** is stable across the draft and should be kept:

1. What the exercise is (one sentence; name the table or figure).
2. The headline number(s), signed and in the paper's units.
3. The mechanism, typically one sentence opening "The reason for this is that", "This happens
   because", or "Since ... have a higher marginal utility ...".
4. Optionally, a comparison to the literature or to the other countries, or a footnote.

**A quantitative section** (Argentina, OECD, endogenous θ) follows this order:

1. Opening paragraphs: why the case matters, what data fact is to be explained, and a one-sentence
   preview of the finding ("We show that ... ageing is the most significant with pension
   characteristics being the second most important factor").
2. `\smalltitle{Calibration.}` — targets, sources, and every identifying assumption, in prose.
   Parameter-by-parameter, ending with the calibration table `\input`.
3. One `\smalltitle{...}` per experiment or experiment family, each ending with its table `\input`
   immediately after the paragraph that discusses it.
4. `\smalltitle{The effect of the intertemporal elasticity of substitution.}` — the CRRA robustness,
   after the log-preference results, never mixed into them.
5. A closing interpretation paragraph (what the parameters absorb, what the model is and is not).

**Section openings** state what the section does and preview the result; they do not summarise the
paper. **Section closings** hand off to the next section with one sentence ("Section \ref{sec:esc}
takes up that question by letting the electorate choose θ as well as τ").

**Headings.** `\section` and `\subsection` only for the paper's skeleton; inside a section use
`\smalltitle{Name.}` — bold run-in heading, sentence case, ending in a period. The endogenous-θ section
is the one section that uses `\subsection` within itself; that is acceptable there because it has
three distinct parts, but do not add further subsections elsewhere.

## 3. Numbers, units and precision

| Quantity | Unit and precision | Examples in draft |
|---|---|---|
| Tax rate changes | percentage points, one decimal, "p.p." | "about 6.2 p.p.", "by 8.7 p.p." |
| Tax rate levels | percent, one decimal | "13.2\%", "τ_{2010}=0.125" (level as a parameter) |
| Savings rate | changes in p.p. of GDP, one decimal; levels in \% | "1.6 p.p.\ of GDP", "the baseline's 15.4\%" |
| Pension spending | \% of GDP, one decimal | "1.9\% of GDP" |
| Hours | weekly hours, one decimal | "about 6.2 hours per week", "at most 0.7 hours" |
| Bismarckian index θ | three decimals | "0.738", "0.972" |
| Other parameters | as in the table | "$\xi=0.30$", "$K/Y = 3.23$" |
| Solver tolerances | scientific | "$6\times10^{-4}$" (rare; mostly for the technical notes) |

- Every savings-rate number is savings over GDP (convention of 2026-09-08). Never "of labor income".
- A number in prose must match the table it sits next to; the table is the source. Counterfactual
  rows are changes against the same ρ's own baseline.
- Quote at most two or three numbers per sentence; a run of numbers across ρ is written as a list
  in one sentence ("from $0.738$ to $0.766$, $0.778$ and $0.846$ at $\rho = 0.5, 1, 2$").
- Signs in words: "increases by", "a drop of", "would reduce". Avoid "+1.4 p.p." in prose.

## 4. Terminology and notation

- **Pension design vocabulary**, defined once in the model section and then used bare: *contributive*
  vs *universal* (the ε dimension); *Bismarckian* vs *Beveridgean* (the θ dimension). "More
  Bismarckian" means higher θ; "the Bismarckian corner" is θ = 1, "the Beveridgean corner" θ = 0.
  "Earnings-related" and "flat" benefits are the plain-language equivalents and may alternate.
- **Households**: "formal" and "informal" households; "informal or displaced" only in the
  introduction. Household types are indexed $i$ or $j$; the informal type is $0$.
- **Equilibria**: "economic equilibrium" (competitive, taxes given) and "politico-economic
  equilibrium" (PEE). Write out the words in the paper; "PEE" only after being defined and mostly in
  the numerical section.
- **Preferences**: "log-GHH preferences" for the analytical case; "CRRA preferences" or "general CRRA
  preferences" for the extension; ρ is read as the intertemporal elasticity of substitution and
  written "IES" after first definition. ξ is the Frisch elasticity.
- **Fixed symbols**: τ tax rate, θ Bismarckian index, ε universal-pension level, γ₀ informal share,
  ν_t workers per retiree, ω political weight of the old, μ_i propensity to vote, X_i taste for
  leisure, η_i productivity, β discount factor, α capital share, s savings, h hours.
- **Timing**: model periods are thirty years; calendar years name periods ("2010", "2020", "2040").
- **Country names**: "the U.S." (with periods, used adjectivally as "U.S.\ inequality"), "the UK"
  (no periods), "France". "Argentina", "Argentine" as adjective for the survey.
- **Named scenarios** are italicised on first use, `{\it mild ageing}`, `{\it acute ageing}`, then
  bare. The draft mixes `{\it }` and `\emph{}`; either is fine, do not convert existing ones.
- **Counterfactual labels** used in tables and text alike: pension characteristics (θ), ageing, income
  distribution, leisure preferences, voting patterns, "French characteristics" for the composite.
- **"Exogenous θ" / "endogenous θ"**, or "θ pinned" / "θ chosen", for the two readings in the
  endogenous-design section.

## 5. LaTeX conventions

- **Cross-references in running text are lowercase**: "section \ref{...}", "table \ref{...}",
  "figure \ref{...}", "appendix \ref{...}", "proposition \ref{...}", "equation \eqref{...}" or
  just "\eqref{...}". Capitalised only at the start of a sentence ("Table \ref{...} shows").
- **Label prefixes**: `sec:`, `eq:`, `prop:`, `def:`, `table:`, `fig:`, `app:`, with a
  colon-separated path (`table:US:pensChars`, `fig:US_ESC:overview`, `eq:esc:budget`). Table and
  figure labels are set by `python/paper` and must not be changed in the tex.
- **Citations**: biblatex. `\textcite{key}` as a sentence element, `\parencite{key}` for
  parenthetical, `\parencite[e.g.][]{a,b}` for a list with a prefix. The introduction's
  `\parencite{a,b}{e.g.}` is not biblatex syntax (the second brace group prints as text after the
  citation); fix it when that paragraph is touched. Two references are still written
  as plain text ("Gonzalez-Eiras and Niepelt (2008)", "Song (2011)") in `Log.tex`; convert to
  `\textcite` when that section is touched.
- **Footnotes** carry data sources, institutional detail, alternative choices not pursued, and
  connections to the literature that would interrupt the argument. They are full sentences. Use them
  freely; the draft averages one or two per paragraph in the calibration passages.
- **Tables and figures**: `\input{Tables/Name}` on its own line after the discussing paragraph.
  Figures: `\caption` above `\includegraphics`, `\label` after the caption, `[!htb]`, width
  `\linewidth` (or `0.7\linewidth` for a single panel); notes via `threeparttable` +
  `\tablenotes` in `\footnotesize`, opening "\textit{Note:}".
- **Equations**: `align` (unnumbered `align*` for one-off calibration formulas), `subequations` with
  a shared label for a block of definitions; inline `$...$` for symbols. Multi-letter functions in
  `\mathrm{}` (`\mathrm{LE_{men}}`), calligraphic for objective functions ($\mathcal{W}_t$).
- **Control spaces** after abbreviations: `i.e.\ `, `e.g.\ `, `vs.\ `, `U.S.\ ` mid-sentence,
  `p.p.\ of GDP`.
- **Comments** intended for a later session use `%%` and a grep-able tag (`%% TODO-ARG035:`). Remove
  the tag when the item is done; do not leave narrative comments in finished text.
- Do not hand-edit anything carrying the `%% GENERATED` banner.

## 6. What the introduction and conclusion promise

Any new result paragraph must be traceable to one of the claims already made in the introduction
(paragraphs 6–9) and echoed in the conclusion. If the rewrite changes a magnitude or a sign, change
it in all three places: the abstract, the introduction, and the conclusion. `grep -rn TODO-ARG035
writing/Paper` lists the places currently known to be out of sync.

## 7. A short checklist before committing a section

1. Every number in prose matches the table or figure next to it, in the paper's units.
2. Each results paragraph names its table or figure and gives a mechanism.
3. No dashes doing the work of a sentence break; no sentence commenting on the paper's own prose.
4. Vocabulary from §4 only; no synonyms invented for θ, ε, or the equilibrium concepts.
5. Cross-references lowercase in running text; citations through biblatex.
6. The section opens by saying what it does and closes by handing off to the next one.
