# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

The read-through of 2026-10-08 raised six items; 3, 5 and 6 are fixed (`8a96925`). These remain, for RKB to take
in turn.

**W10. The ranking of determinants at ρ = 2.** At ρ = 2 France's voting patterns raise the U.S. tax rate by
1.7 p.p. (14.43% to 16.12%, `US_CRRA_OtherShocks`) and the full swing of the design by 1.5 p.p. (θ = 1 to 0,
13.72% to 15.21%, `US_CRRA_PensChars`), so the earnings link comes second only at ρ ≤ 1. The abstract ("the
earnings link the second, and income inequality and voting patterns minor"), section 6's IES paragraph ("the
overall conclusion … holds", `OECD.tex:40`) and the conclusion ("changes only the size of the earnings-link
effect", `Conclusion.tex:5`) claim more.

**D3. The UK at the U.S. income cuts.** `UKMain.xlsx`'s `calibrationUS` regroups the UK by a linear fit
(`data/README.md`): relative incomes (0.79, 1.07, 1.45) at shares 58/18/24%. The UK's own groups, (0.50, 1.00,
2.13) at 29/58/13%, bound any exact regrouping: the top 24% average at least 1.61 and the bottom 58% at most 0.75,
so $\tilde V \geq 0.10$ against the 0.065 of `US_ESC_Country` (table 4), section 7.2 (with the re-read design
0.543), appendix F.3 and OA.3.1. That the regrouping moves the UK's choice little probably survives. A recount of
the survey at the U.S. cuts, then stage (i) for `UKUS` and the ESC stages. Section 7.2 also sets the UK at its own
cuts (0.223) against France at the U.S. cuts (0.218); at the UK's cuts France is about 0.25.

**W11. The introduction's footnote on the timing of the choice** (`Introduction.tex:25`) narrates the research
("We also explore…", "We test…") and claims runs at other labor supply elasticities that OA.4.5 (`ESC_Timing`)
does not show: it varies ρ only.

## Candidates, not scheduled

**W12. Smaller findings of the 2026-10-08 read-through, not yet raised.** Sections 5 and 6 explain the IES in ways
a referee may ask to reconcile: in section 5 a low IES needs a larger ω and the economy responds less to ε, in
section 6 a high IES needs a lower ω and the design's effect is smaller. Appendix A keeps `\label{here1}`,
`\label{here2}` and a `\smalltitle` without its period; the abstract's opening participle dangles ("Employing an
overlapping generations model…, our analysis aligns…"); `Argentina.tex` keeps a commented-out
`\input{Tables/Argentina_funcOfRho}`.

**C10. Figure PDFs are not byte-reproducible.** `figures._save` writes the PDF without
`metadata = {'CreationDate': None}`, while the SVG drops its date, so a rebuild changes every PDF by its timestamp
alone; and `build.py --list` runs every builder in full (its comment says the loaders raise first), so on
2026-10-08 it rewrote every figure PDF. Fixing both changes each figure PDF once, the paper's copies with them
(an Overleaf push).

**W9. A linear term in the cost of redistribution (RKB's call).** Under the quadratic cost the first unit of
redistribution is free at the margin, so no electorate chooses France's corner $\theta = 1$; section 7.2's
footnote and the conclusion leave a linear term in $1-\theta$ to future work. Two parameters, the U.S. and the
UK designs as targets, France as the prediction: a derivation (appendix C.2's form and the design condition), a
`spec` in `python/US/base.py fWedge`, and the ESC calibration and experiment stages rerun, CRRA included
(`python/paper/README.md`, stage (ii) `--prepub`). `notes/paper_costLiterature.md` §2.A has the Okun framing.

## Data tasks

**D2. Figure 5.1's data outside the pipeline.** `writing/Paper/Figs/coverageArg.eps` (beneficiaries of the
national pension system and of non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020),
table 6; neither the data nor the script is in the repository. Add `data/argentinaCoverage.csv` with a row in
`data/README.md` and a builder in `python/paper` (`REPLICATION.md` §5 lists it).
