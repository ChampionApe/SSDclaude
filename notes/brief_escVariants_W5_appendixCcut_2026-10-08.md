# Brief W5: appendix C cut back, the propositions to the technical note

For the `paper-writer-lead` agent. RKB read the rewritten appendix C on Overleaf (2026-10-08) and wants it
much shorter, closer to the version before the rewrite, with propositions 4 (the Bismarckian corner,
`prop:esc:bismarckCorner`, new) and 5 (`prop:esc:separability`, which the appendix had before) in the
technical documentation only. Plan: `notes/plan_endogenousDesign.md` §C.2 "Phase W5". The referee's report
(R1, the session hands it to you) lists which sentences of C.2 section 7 needs and which can go.

## 1. Files

- `writing/Paper/Appendix/EndogenousDesign.tex`: the cut.
- `writing/US/model_esc.tex`: receives the two propositions with their proofs and the paragraphs that
  belong with them, in the technical note's register (third person, `\refeq:`/`\cref`, `\emph{}` run-ins;
  its labels are `\refeq:esc:...`, and it already has `prop:esc:separability` and `prop:esc:substitution`
  as plain `\label`s: add `prop:esc:bismarckCorner` there the same way, and the equation
  `\refeq:esc:cornerFOC`). W4 edited this file earlier today (the specification, the magnitude, the
  sequential condition); build on its text.
- The references: `writing/Paper/Sections/Numerical.tex` (one `\ref{prop:esc:separability}` in its design
  paragraph) and `writing/Paper/Sections/EndogenousTheta.tex` (`prop:esc:separability` and
  `prop:esc:bismarckCorner`, wherever the rewritten section cites them): each becomes a reference to the
  appendix subsection that states the result in words (`app:esc:log`, `app:esc:cost`) with "the technical
  documentation \parencite{BergGE26doc}" named once where the proof is. Touch nothing else in those files.
- The pre-rewrite appendix C is `git show eefb460~1:writing/Paper/Appendix/EndogenousDesign.tex`; use it as
  the length and register reference (3,038 words).

## 2. What appendix C keeps, by subsection

**C.1** unchanged. **C.2**: "The implicit tax", "Which margin", "The Harberger loss" unchanged; the
specification paragraph kept but tightened to: the amount carried (`eq:esc:Mabs`), the general form
(`eq:esc:fGeneral`) with the three variants and the scale-and-shape writing, the three properties in one
sentence each, the $\tau_t$ choice in its footnote, the two closing sentences on the alternatives; then
one paragraph "The Bismarckian corner" in words, no proposition environment: at the corner the cost enters
the design's slope through $\lambda_1\tau_{t+1}M$ alone, so the corner is chosen once $\lambda_1$ exceeds a
threshold that is proportional to $1/\tau_{t+1}$, rises when the distribution is compressed (the common
part of the obstacle does not shrink with it) and when the voting profile flattens, and falls with ageing;
the derivation and the closed form are in the technical documentation. The magnitude paragraph as W2 left
it. **C.3** as W2 left it (the general design condition stays; it is one line). **C.4**: the statement of
separability in two sentences (the objective is additively separable; the design chosen at $t$ depends on
neither the inherited design nor savings; the tax depends on the inherited design alone), what section 4
uses, and the sentence on CRRA; the proposition and the proof go to the technical note.

Target: at or below 3,000 words for the appendix. Nothing section 7 cites may disappear: run
`writing/checkPaper.py` (labels `prop:esc:bismarckCorner` and `prop:esc:separability` must then be defined
nowhere in the paper and cited nowhere), latexmk on the paper (clean, no undefined references), and
latexmk on the technical note (`writing/main.tex`; it has one pre-existing error in
`US/model_setup.tex` line 40, "Extra alignment tab", which is not yours; no new error and no undefined
reference of yours).

## 3. Report

Words before and after for the appendix; what moved to the technical note and under which labels; the
references changed (file and line); the check lines. At most 15 lines.
