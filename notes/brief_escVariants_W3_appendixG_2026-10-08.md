# Brief W3: appendix G, the endogenous design's additional results (new file), and `main.tex`

For the `paper-writer` agent. Your files: the new `writing/Paper/Appendix/EndogenousDesignDetails.tex`,
`writing/Paper/main.tex` (one line) and `writing/Paper/Appendix/Robustness.tex` (only if a sentence refers
to its own letter). W1 is rewriting section 7, W2 appendix C, W4 the introduction, abstract, conclusion and
technical note; cite their labels (§3), do not wait for them. Plan: `notes/plan_endogenousDesign.md` §B
(RKB's outline: G.1 calibration details, G.2 the counterfactuals not in the main text, G.3 the role of
$\rho$) and §C.1 decisions 4 to 6.

## 1. The file

`main.tex`: insert `\input{Appendix/EndogenousDesignDetails}` immediately before
`\input{Appendix/Robustness}`, so the new appendix is G and the robustness map becomes H (its label
`app:robustness` is unchanged and every reference is by label).

`Appendix/EndogenousDesignDetails.tex`, opening like the other appendices
(`\section{Endogenous design: additional results}\label{app:escDetails}\setcounter{equation}{0}`, then
one orienting sentence), 900 to 1,300 words in all, with:

**G.1 `\subsection{Calibration across variants and countries}\label{app:escDetails:calibration}`.**
Table `table:US_ESC:variantsCountry` (`Tables/US_ESC_VariantsCountry.tex`): per variant, the UK, France and
the UK regrouped at the U.S. income percentiles under the U.S. parameters and with their own; the
alternative pinning of the linear-quadratic cost on the U.S. and France (what France's corner takes, and
where it puts the UK); France's design under the $\tilde V$-weighted linear term if the table's note or a
row carries it. Take from section 7.2's current text (`Sections/EndogenousTheta.tex` as of the start of
your task, before W1 overwrites it: read it first and copy what you need) the sentences on the UK at the
U.S. cuts (its re-read design 0.543, $\tilde V$ 0.065, the choice moving little) and on what separates the
UK from France (size, not dispersion), updated to the table. One footnote on the regrouping's caveat
(`data/README.md`'s UK note: a linear fit of the UK survey to the U.S. cuts; TODO D3 says the exact
regrouping would give $\tilde V \geq 0.10$) as a choice with its cost.

**G.2 `\subsection{Counterfactuals across variants}\label{app:escDetails:counterfactuals}`.** Table
`table:US_ESC:variantsShocks` (`Tables/US_ESC_VariantsShocks.tex`): every scenario of the endogenous-design
exercise per variant, with the savings rate and the workweek, mild ageing, the composite of France's
income distribution and voting patterns, all French characteristics and France's own path. Read it in
three or four sentences per block of findings: what the savings rate and workweek do when the design is
chosen (the current online text of `US_ESC_Ageing` and the others in `python/paper/onlineAppendix.py`
says what the quadratic cost does; check it against the new table before reusing a sentence); the
composite and the all-French rows (voting prevails); the linear cost's corners; the UK as host in one
sentence with `\oa{esc-uk}`.

**G.3 `\subsection{The role of the intertemporal elasticity}\label{app:escDetails:rho}`.** Tables
`table:US_ESC:calibration` (`Tables/US_ESC_Calibration.tex`: the quadratic cost's parameter per $\rho$) and
`table:US_ESC:summary` (`Tables/US_ESC_Summary.tex`: the counterfactuals per $\rho$), both `\input` here.
Content from the current section 7's closing paragraph (its text as of the start of your task) expanded to
two or three paragraphs: the cost parameter falls steeply in $\rho$ and why; the ageing response is stable
across $\rho$; the responses to inequality and voting patterns are not, with the $\rho = 2$ numbers; the
UK's own cost across $\rho$ (`\oa{esc-uk}`); the Frisch elasticity in one sentence (`\oa{esc-path}`) and
the timing of the choice in one (`\oa{esc-timing}`); a closing sentence that the linear and
linear-quadratic costs are computed at $\rho = 1$ and that the quadratic cost is the $\rho$ comparison's.

## 2. Numbers

From the tables named above, in the paper's units (`notes/paper_styleGuide.md` §3); every number checked
against its cell; `\todo{...}` where a table lacks one. The table environments are generated: `\input`
them, never edit them.

## 3. Labels

Yours, new: `app:escDetails`, `app:escDetails:calibration`, `app:escDetails:counterfactuals`,
`app:escDetails:rho`. Cited: `sec:esc`, `sec:esc:cost`, `sec:esc:calibration`, `sec:esc:results` (section
7), `app:esc`, `app:esc:cost`, `prop:esc:bismarckCorner` (appendix C), `table:US:Calib`,
`table:a_US:CalibFRUK`, `fig:US:OECDdata`, `app:robustness`, the generated `table:US_ESC:variantsCountry`,
`table:US_ESC:variantsShocks`, `table:US_ESC:calibration`, `table:US_ESC:summary`,
`table:US_ESC:variants`, `table:US_ESC:results`; `\oa{esc-variants}`, `\oa{esc-us}`, `\oa{esc-uk}`,
`\oa{esc-path}`, `\oa{esc-timing}`, `\oa{esc-scale}`. Register: `notes/paper_styleGuide.md`; the exemplar
for an appendix of results is `Appendix/CalibrationOECD.tex`. Run `writing/checkPaper.py` before
reporting; a label of W1's or W2's not yet defined is theirs, say so rather than defining it.
