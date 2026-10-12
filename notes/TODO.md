# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

**D3. The UK at the U.S. income cuts.** `UKMain.xlsx`'s `calibrationUS` regroups the UK by a linear fit
(`data/README.md`): relative incomes (0.79, 1.07, 1.45) at shares 58/18/24%. The UK's own groups, (0.50, 1.00,
2.13) at 29/58/13%, bound any exact regrouping: the top 24% average at least 1.61 and the bottom 58% at most 0.75, so $\tilde V \geq 0.10$ against the 0.065 of `US_ESC_Country` (table 4), section 7.2 (with the re-read design 0.543), appendix F.3 and OA.3.1. That the regrouping moves the UK's choice little probably survives. A recount of the survey at the U.S. cuts, then stage (i) for `UKUS` and the ESC stages. Section 7.2 also sets the UK at its own cuts (0.223) against France at the U.S. cuts (0.218); at the UK's cuts France is about 0.25.

## Candidates, not scheduled

**W12. Smaller findings of the 2026-10-08 read-through, not yet raised.** Sections 5 and 6 explain the IES in ways
a referee may ask to reconcile: in section 5 a low IES needs a larger ω and the economy responds less to ε, in
section 6 a high IES needs a lower ω and the design's effect is smaller. Appendix A keeps `\label{here1}`,
`\label{here2}` and a `\smalltitle` without its period; the abstract's opening participle dangles ("Employing an
overlapping generations model…, our analysis aligns…"); `Argentina.tex` keeps a commented-out
`\input{Tables/Argentina_funcOfRho}`, whose table was retired on 2026-10-09.

**W13. The paper's pointers to the online appendix**, rebuilt and published on 2026-10-09
(`archive/notes/plan_onlineAppendix.md`). Every `\oa` key resolves, the retired ones as aliases
(`onlineAppendix.OLDKEYS`; `oecd-us` is now `oecd`, `arg-calibration` `arg-leisure`, `esc-path` `esc-paths`). Four
sentences describe the old site: section 6's footnote ("holds every table behind the figures of this section",
`OECD.tex:4`) and figure 6.1's note ("Full tables with results are printed in the", `OECD.tex:23`), where each
figure now offers its data as csv instead; appendix E's "the reform at every $\rho$ under both, are reported"
(`HouseholdSurveyArg.tex:39`), where A3 shows the calibration under both and says the reform is identical; and
figure G.1's note, "the paths from the first period" (`EndogenousDesignResults.tex:24`), where C1 starts in 1990.
The site also has results the paper may cite: the UK's acute ageing with the design chosen (C2), the UK's and
France's design paths (C1), and section 6's ranking at $\xi = 0.2$ and $0.4$ (B3).

**C12. The online appendix's PDF edition** (RKB postponed it on 2026-10-09). The tables' tex stays in
`results/paper/Tables` and `texTable.printTex` resolves the paper's references for print; the format left
`_quarto.yml` and comes back with `pdf-engine: pdflatex` and `latex-auto-install: false` (`python/paper/README.md`,
Traps).


## Data tasks

**D2. Figure 5.1's data outside the pipeline.** `writing/Paper/Figs/coverageArg.eps` (beneficiaries of the
national pension system and of non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020),
table 6; neither the data nor the script is in the repository. Add `data/argentinaCoverage.csv` with a row in
`data/README.md` and a builder in `python/paper` (`REPLICATION.md` §5 lists it).
