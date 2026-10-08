# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

The read-through of 2026-10-08 raised six items; 3, 5 and 6 are fixed (`8a96925`), and the introduction's timing
footnote (W11) with the cost variants. These remain, for RKB to take in turn.

**W10. The ranking of determinants at ρ = 2.** At ρ = 2 France's voting patterns raise the U.S. tax rate by
1.7 p.p. (14.43% to 16.12%, `US_CRRA_OtherShocks`) and the full swing of the design by 1.5 p.p. (θ = 1 to 0,
13.72% to 15.21%, `US_CRRA_PensChars`), so the earnings link comes second only at ρ ≤ 1. The abstract ("the
earnings link the second, and income inequality and voting patterns minor"), section 6's IES paragraph ("the
overall conclusion … holds", `OECD.tex:40`) and the conclusion ("changes only the size of the earnings-link
effect", `Conclusion.tex:5`) claim more.

**D3. The UK at the U.S. income cuts.** `UKMain.xlsx`'s `calibrationUS` regroups the UK by a linear fit
(`data/README.md`): relative incomes (0.79, 1.07, 1.45) at shares 58/18/24%. The UK's own groups, (0.50, 1.00,
2.13) at 29/58/13%, bound any exact regrouping: the top 24% average at least 1.61 and the bottom 58% at most 0.75,
so $\tilde V \geq 0.10$ against the 0.065 of `US_ESC_VariantsCountry` (appendix G.1, with the re-read design
0.543), appendix F.3 and OA.3.1. That the regrouping moves the UK's choice little holds under the quadratic cost
only (0.644 against 0.625): under the preferred linear-quadratic cost the regrouped UK chooses 0.846 against
0.560, because the regrouping's $M/\tilde V$ is 3.7 against 1.3 at the UK's own cuts and the linear term is
weighted by $M$ (2026-10-08; appendix G.1's footnote states the caveat). A recount of the survey at the U.S.
cuts, then stage (i) for `UKUS` and the ESC stages. Section 7.2 also sets the UK at its own cuts (0.223) against
France at the U.S. cuts (0.218); at the UK's cuts France is about 0.25.

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

**R6. The CRRA leg for the preferred cost at $\rho = 0.5$ and $2$.** Section 7's closing paragraph and appendix
G.3 read the quadratic cost's exact CRRA rows; the linear and linear-quadratic costs are solved at $\rho = 1$
only (W9 closed on 2026-10-08 with the variants of `notes/plan_endogenousDesign.md` §C). `runESCcrra.py` accepts
`--spec sizeLQ --kappa <κ>` (the shape held at its $\rho = 1$ value 0.1287, $\lambda$ recalibrated per $\rho$);
`config.US['esc']['bracket']['sizeLQ']` needs scan brackets per $\rho$ (from the LOG $\lambda = 5.237$ as for
`'size'`: about $[\lambda/3, 5\lambda]$ at $\rho = 0.5$ and $[\lambda/20, 3\lambda]$ at $2$) and the UK host
(`escCalibrationCRRAUK.csv`) its own; about 3 h for the two $\rho$ in parallel plus the UK host. Then
`config.US['esc']['spec'] = 'sizeLQ'` makes every $\rho$ exhibit the preferred cost's and the two-spec
configuration (`paperSpec`, `variants`) collapses. Decision 5 of the plan.

**C11. The tax policy interpolated on the design-state grid.** The leaded recursion interpolates
$\mathcal{T}_{t+1}$ linearly on the 41-node state grid; the design objective is flat, so the parabolic refinement
amplifies a $3\times10^{-5}$ error in $\tau$ into 0.004 in the 2020 choice (0.797 against 0.794 with the policy
evaluated at the candidates) and $5\times10^{-4}$ in the 1990 choice the calibration targets; near the joint
root the UK's design is uneven in $\kappa$ for the same reason ($\kappa$ uncertain by about $\pm0.005$).
Evaluating the tax policy at the 121 candidates costs one `τOfθ` call per period (`notes/esc_variants.md`, "A
precision item"). It moves every published design by up to 0.004 and breaks `test_esc.py`'s bitwise reference,
so it waits for a run that recalibrates everything (R6 is the occasion).

## Data tasks

**D2. Figure 5.1's data outside the pipeline.** `writing/Paper/Figs/coverageArg.eps` (beneficiaries of the
national pension system and of non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020),
table 6; neither the data nor the script is in the repository. Add `data/argentinaCoverage.csv` with a row in
`data/README.md` and a builder in `python/paper` (`REPLICATION.md` §5 lists it).
