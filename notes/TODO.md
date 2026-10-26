# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

**D3. The UK at the U.S. income cuts.** `UKMain.xlsx`'s `calibrationUS` regroups the UK by a linear fit
(`data/README.md`): relative incomes (0.79, 1.07, 1.45) at shares 58/18/24%. The UK's own groups, (0.50, 1.00,
2.13) at 29/58/13%, bound any exact regrouping: the top 24% average at least 1.61 and the bottom 58% at most 0.75, so $\tilde V \geq 0.10$ (0.104) against the 0.065 of `US_ESC_Country`'s last row, read in appendix G.1 (with the re-read design 0.543), appendix F.3 and online B2. That the regrouping moves the UK's choice little probably survives. A recount of the survey at the U.S. cuts, then stage (i) for `UKUS` and the ESC stages. On RKB's call of 2026-10-22 the paper carries a caveat until then: G.1 states the bound and calls the row an approximation, F.3 says the fit understates the dispersion, and G.1's comparison of the UK at its own cuts (0.223) with France at the U.S. cuts (0.218) gives France at the UK's cuts (0.246) in parentheses. Remove the caveats when the row is recomputed.

**W16. Response to the AI review of 2026-10-22** (`coarse-output/coarse_review_22102026.md`). Phases 0–3 done;
what is left (C7's French reruns, the commit, verification, the Overleaf push) is `notes/reviewResponse_open.md`.

## Candidates, not scheduled

**W14. `BergGEwp`**, the reference the conclusion gives for the health-risk environment, carries this paper's own
title ("Social Security Design and its Political Support", working paper, 2023), as it has since the first
snapshot (`5edec9a`). RKB to confirm it is the intended reference or supply the title.

**W17. How the paper points to the online appendix** (RKB, 2026-10-26). The reader should know that every page of
the online appendix exists, without a pointer in every other sentence. On 2026-10-26, 19 of the 61 anchors in
`writing/Paper/onlineAppendix.tex` were cited (`\oa{}`, `\oanum{}`), from ten files. Some of the uncited are
subsections of cited pages, but whole pages were not reached at all, e.g. `arg-ies`, `arg-designs`, `oecd-countries`,
`oecd-parameters` (with `oecd-state`, A13's strategic term), `esc`, `checks`, `num` and `num-horizon`.
Decide the pattern, perhaps one opening or closing sentence per section ("the online appendix has further evidence
on ..."), with an inline pointer kept only where a claim rests on the page, and apply it after W16.

**C12. The online appendix's PDF edition** (RKB postponed it on 2026-10-09). The tables' tex stays in
`results/paper/Tables` and `texTable.printTex` resolves the paper's references for print; the format left
`_quarto.yml` and comes back with `pdf-engine: pdflatex` and `latex-auto-install: false` (`python/paper/README.md`,
Traps).


## Data tasks

**D2. Figure 5.1's data outside the pipeline.** `writing/Paper/Figs/coverageArg.eps` (beneficiaries of the
national pension system and of non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020),
table 6; neither the data nor the script is in the repository. Add `data/argentinaCoverage.csv` with a row in
`data/README.md` and a builder in `python/paper` (`REPLICATION.md` §5 lists it).
