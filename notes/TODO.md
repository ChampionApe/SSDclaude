# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

## Candidates, not scheduled

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
