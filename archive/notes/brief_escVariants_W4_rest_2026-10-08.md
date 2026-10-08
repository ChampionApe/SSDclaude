# Brief W4: the introduction, abstract and conclusion sentences on the cost; the technical note

For the `paper-writer` agent. Your files: `writing/Paper/Sections/Introduction.tex`,
`writing/Paper/abstract.tex`, `writing/Paper/Sections/Conclusion.tex`, `writing/US/model_esc.tex`,
`writing/US/num_esc.tex`, `notes/paper_costLiterature.md` and `notes/TODO.md` (one item). W1 is rewriting
section 7, W2 appendix C, W3 appendix G; cite their labels, do not wait for them. Plan:
`notes/plan_endogenousDesign.md` §C.1 (decisions 1 to 5 as amended at gate 1); the economics
`notes/esc_variants.md` §7 (the $M$ weight) and §4-§5.

## 1. The paper (small, surgical edits)

- `Sections/Introduction.tex`, the paragraph beginning "An interior design requires flat benefits to be
  more expensive": the cost is now a leak with a constant part and a part rising with the load, scaled by
  the size of the system; three variants; the preferred one has two parameters, pinned by the U.S. and the
  UK designs, France the test; the ordering of the UK, the U.S. and France holds under every variant;
  France's corner requires a linear term the UK's design rules out (read the numbers in
  `Tables/US_ESC_Variants.tex` before writing; `\todo{}` if it is not built yet). Same length as now. The
  footnote of the preceding paragraph (TODO W11: "We also explore different ways...", research narration,
  claims runs at other labor supply elasticities the online appendix does not show) is rewritten as a
  statement of what appendix C.1 and `\oa{esc-timing}` show: the three timings each give a corner without
  the cost, at each intertemporal elasticity. Close W11 in `notes/TODO.md` (delete the item) when done.
- `abstract.tex`, the last sentence ("...a single cost parameter orders the designs of the UK, the U.S.\
  and France as observed"): the cost calibrated to the U.S. and the UK orders the three designs as observed
  under every variant; keep the ageing and inequality claims; same length.
- `Sections/Conclusion.tex`: the sentence of the first results paragraph on "the single cost parameter
  orders the designs ... the UK's own cost is within 17\%" updated to the variants; the limitations
  paragraph's second limitation ("the cost specification cannot deliver France's fully Bismarckian system
  ... a linear term ... would allow it") rewritten: a linear term lets an electorate choose the corner, but
  the linear term that France's corner needs puts the UK far below its design, so the three designs are not
  consistent with one cost of this family, and a formality margin remains the structural candidate.

## 2. The technical note (`writing/US/`, a separate Overleaf project; same conventions as the file)

- `model_esc.tex`, the `\emph{Specification.}` paragraph: the general form with the $M$ weight on the
  linear term and $\tilde V$ on the quadratic, the three paper variants and the record spec `'sizeLQV'`
  ($\tilde V$ on both), the properties (keep the ones there; add the first unit's marginal cost
  $\lambda_1\tau_t M$ and that $\ln f$ stays linear in $\tau_t$), the $\tau$-scaling as the choice with the
  literal leak's cost, one sentence each; the `\emph{Dates.}` paragraph gains $M$'s vintage beside
  $\tilde V$'s. Keep `\refeq:esc:AB`; give the general form `\refeq:esc:fGeneral` and $M$ `\refeq:esc:Mabs`.
  Where the paragraph names "a linear term ... we do not introduce one", replace.
- `num_esc.tex`, "Calibrating the cost": two paragraphs after "Why the residual is scanned and not
  bracketed": the threshold calibration (a log-grid scan for the first cost at which the design in force at
  $t_0$ is the corner, then bisection in $\log\lambda$ on the corner indicator, to a relative $10^{-3}$;
  `ModelESC.calibrateWedgeCorner`), and the joint calibration of $(\lambda,\kappa)$ (for each shape the
  U.S. scale by the existing scan and root, the second economy's design under the pair read off its own
  freely simulated path, a root in the shape on that design minus the observed one, or a bisection on the
  corner indicator when the second economy is France; `runESC.calibrateJoint`). Read the code's
  docstrings (`python/US/modelESC.py`, `runESC.py`, the top entry of `python/US/RESEARCH_LOG.md`) and write
  what it does now, nothing about how it came to be.
- `notes/paper_costLiterature.md` §4 (one short paragraph dated 2026-10-08: the variants, the $M$ weight,
  the finding that the UK and France cannot be reconciled at one pair) and §5 (unchanged citations; say
  the variants cite nothing new).

## 3. Rules

`notes/paper_styleGuide.md` for the paper files; the technical note's own register for `writing/US/`
(third person, `\refeq:`/`\cref` labels, `\emph{}` run-ins). Every number from a generated table or from
`notes/esc_variants.md` §7 with its equation number; `\todo{}` otherwise. Write with Write/Edit, no
heredocs; run `writing/checkPaper.py` for the paper files (the technical note is not checked by it; scan
your files for control bytes). Labels cited from the others: `sec:esc`, `sec:esc:calibration`, `app:esc`,
`app:esc:corner`, `app:esc:cost`, `prop:esc:bismarckCorner`, `app:escDetails`, `table:US_ESC:variants`;
`\oa{esc-timing}`, `\oa{esc-variants}`. Report in at most 20 lines, the TODO change included.
