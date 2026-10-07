# Style guide for the paper draft (`writing/Paper`)

The register of the paper: how its sections are written, so that new text blends in. The technical notes
under `writing/<model>/` follow their own conventions and are not covered.

## 1. Voice and register

- **First person plural, present tense.** "We calibrate", "we find", "the model predicts", "table X
  shows". Past tense only for history (Argentina's reforms, what earlier papers did).
- **Plain academic register.** Claims stated directly, mechanisms explained in one or two sentences,
   no flourishes. No meta-commentary and no second clause that restates the first for emphasis.
- **Dashes.** The older sections use none. Allow at most one `---` per paragraph, for a genuine aside;
  otherwise start a new sentence.
- **Hedging is calibrated, not defensive.** "about", "roughly", "a bit less than", "consistent with",
  "in line with", "suggests". Do not hedge model results that are exact ("the tax rate increases by
  6.2 p.p."); do hedge the mapping to data ("consistent with available evidence").
- **No narration of the research process.** The paper never says what was tried and abandoned in the
  main text; alternatives not pursued go in a footnote, stated as a choice with its cost (see the
  footnote on the placement of the deadweight wedge, or on holding θ fixed in the inequality
  counterfactual). Development history stays in the logs and `archive/`.

## 2. Paragraph and section anatomy

**Headings.** `\section` and `\subsection` only for the paper's skeleton; inside a section use
`\smalltitle{Name.}` — bold run-in heading, sentence case, ending in a period. The endogenous-θ section
is the one section that uses `\subsection` within itself; that is acceptable there because it has
three distinct parts, but do not add further subsections elsewhere.

## 3. Numbers, units and precision

These rules are indicative, adjust if the context warrants it:

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

- Every savings-rate number is savings over GDP. Never "of labor income".
- Quote at most two or three numbers per sentence.
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
  (no periods), "France". "Argentina".
- **Named scenarios** are italicised on first use, `{\it mild ageing}`, `{\it acute ageing}`, then
  bare. The draft mixes `{\it }` and `\emph{}`; either is fine, do not convert existing ones.
- **Counterfactual labels** used in tables and text alike: pension design (θ), ageing, income
  distribution, leisure preferences, voting patterns.
- **"Exogenous θ" / "endogenous θ"**, or "θ pinned" / "θ chosen", for the two readings in the
  endogenous-design section.
- **Endogenous-design cost vocabulary**: "the deadweight cost of redistribution" or "the
  cost"; λ is "the cost parameter"; $1-f$ is "the share of revenue lost"; $\tilde V$ is "the dispersion
   of relative incomes"; "the size of the system" is the tax rate. The derivation is one paragraph in
    `sec:esc`; the technical note has the rest, and the paper refers to it as "the technical documentation".
- **Pending numbers** are written with the sentence structure in place and the number as
  `\todo{CRRA: <what>}`, specific enough to be filled without re-reading the section. Inside a footnote
  or a table note use `\todo[inline]{...}` (a margin note is not allowed there). `grep -rn "CRRA:"
  writing/Paper` lists what is left.

## 5. LaTeX conventions

- **Cross-references in running text are lowercase**: "section \ref{...}", "table \ref{...}",
  "figure \ref{...}", "appendix \ref{...}", "proposition \ref{...}", "equation \eqref{...}" or
  just "\eqref{...}". Capitalised only at the start of a sentence ("Table \ref{...} shows").
- **Label prefixes**: `sec:`, `eq:`, `prop:`, `def:`, `table:`, `fig:`, `app:`, with a
  colon-separated path (`table:US:pensChars`, `fig:US_ESC:overview`, `eq:esc:budget`). Table and
  figure labels are set by `python/paper` and must not be changed in the tex.
- **Citations**: biblatex. `\textcite{key}` as a sentence element, `\parencite{key}` for
  parenthetical, `\parencite[e.g.][]{a,b}` for a list with a prefix. Every reference in the draft
  goes through biblatex; no author-year is written as plain text. The style is `authoryear`, not
  `authoryear-comp`, so a multi-key cite repeats a repeated author's name rather than sharing it
  across years.
- **Footnotes** carry data sources, institutional detail, alternative choices not pursued, and
  connections to the literature that would interrupt the argument. They are full sentences. Use them
  freely; the draft averages one or two per paragraph in the calibration passages.
- **Tables and figures**: Place figures/tables on its own line after discussing paragraph, but adjust
   placement if it does not fit well on the page. Figures: `\caption` above `\includegraphics`,
   `\label` after the caption, `[!htb]`, width `\linewidth` (or `0.7\linewidth` for a single panel);
   notes via `threeparttable` + `\tablenotes` in `\footnotesize`, opening "\textit{Note:}". End the
   `\includegraphics` line with `\par`: `tablenotes[flushleft]` zeroes `\leftskip`/`\rightskip` before
   its own `\par`, so without it the graphic's paragraph is set flush left and `\centering` is lost.
- **Table and figure notes**. A single note is `\begin{tablenotes}[flushleft]` + `\item[]`,
  set as a paragraph with no list indent; the list form with `\item` is only for notes carrying labelled
  markers keyed to cells (`US_Ageing`'s a/b). A note carries what the main text does not — it never
  restates the section's own description of the exercise — and where several tables share a preamble,
  one anchors it and the rest say "the cost specification and the units are those of table X"
  (`tablesUS.ESCANCHOR`). Figure notes live in the `.tex` beside the `\includegraphics`, not drawn
  inside the PDF, and cite a table for baseline levels rather than repeating the numbers.
- **Rules.** Booktabs everywhere: `\toprule`/`\midrule`/`\bottomrule`, no vertical rules and no
  full-width `\hline`. The one exception, deliberate and confined to the two calibration tables
  `table:US:Calib{,_vectorX}`, is a hairline at 25% black on each side of the three country columns,
  which separates the values from the prose column (2026-09-15, RKB's call). It rules out
  `\addlinespace` in those tables: a `\vrule` in the column spec is drawn per row and a gap breaks it.
  The household-heterogeneity tables still carry the old `|`-and-`\hline` design and are the last ones
  that do.
- **The calibration variant is not printed.** The paper is the common-`X` calibration throughout, so no
  caption or note names it; only a vector-`X_i` twin in the online appendix says what it is
  (`config.variantNote`, `variantCaption`). The alternative is pointed at once per arm: Argentina in a
  footnote to its calibration paragraph (`app:EPH:vectorX`, a stub in the Argentine calibration appendix
  that sends the reader on to `\oa{arg-calibration}`), the rich economies in their calibration appendix
  (`app:US`, pointing at `\oa{oecd-vectorx}`). Sections 6 and 7 carry no pointer.
- **The online appendix** is cited with `\oa{key}`, which prints "online appendix" linked to the key's
  page, so the text reads "the \oa{esc-uk}"; never "Online Appendix OA.4.3" (`\oanum{key}` gives the number
  where one is needed), and never inside a caption or heading, since it is a link. The keys are the
  anchors of `writing/OnlineAppendix/*.qmd`, written to `writing/Paper/onlineAppendix.tex` by
  `build.py --site`; `writing/checkPaper.py` fails on an unknown key.
- **Equations**: `align` (unnumbered `align*` for one-off calibration formulas), `subequations` with
  a shared label for a block of definitions; inline `$...$` for symbols. Multi-letter functions in
  `\mathrm{}` (`\mathrm{LE_{men}}`), calligraphic for objective functions ($\mathcal{W}_t$).
- **Control spaces** after abbreviations: `i.e.\ `, `e.g.\ `, `vs.\ `, `U.S.\ ` mid-sentence,
  `p.p.\ of GDP`.
- **Comments** intended for a later session use `%%` and a grep-able tag (`%% TODO-ARG035:`). Remove
  the tag when the item is done; do not leave narrative comments in finished text.
- Do not hand-edit anything carrying the `%% GENERATED` banner.

## 6. A short checklist before committing a section

1. Every number in prose matches the table or figure next to it, in the paper's units.
2. No dashes doing the work of a sentence break; no sentence commenting on the paper's own prose.
3. Vocabulary from §4 only; no synonyms invented for θ, ε, or the equilibrium concepts.
4. Cross-references lowercase in running text; citations through biblatex.