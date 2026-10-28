# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

**W22. RKB's review of the draft on Overleaf** (started 2026-10-28, RKB continues on 2026-10-29). Done on 2026-10-28
(commit `1f8a955`, root log): table 8 to the online appendix, typos, the country index n, section 5's cuts, sections 6 and 7
rebuilt around 26 synthetic countries with the UK and France moved to appendix G.1, figure 1 highlighting the U.S. and France;
Overleaf and the online appendix match the commit. Points left for RKB: the transported cost parameter is written ε
(`\varepsilon`), distinct from the universal pension ϵ, and a different letter is RKB's call; the introduction's timing footnote
calls the one-period-ahead timing "alternative", although section 7 uses it; section 4 gives the horizon as $T = 2200$, Argentina's
being 2190; the Conde-Ruiz sentence's place in the introduction (W20). Small: `US_ESC_Country`'s header row overruns by 8pt;
`review-2026-10` is not on GitHub, so the online appendix's footer link to its commit is dead.

## Candidates, not scheduled

**C13. A13's myopic/Markov split** (review response, deferred by RKB on 2026-10-26). The online appendix reports
the strategic term instead (`c5Numbers.py strategic`, table `US_Strategic`); the split itself needs a new model
function that solves the tax with the continuation policy held fixed.

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
