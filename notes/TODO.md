# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

**W22. RKB's review of the draft** (2026-10-28 and 29; commits `1f8a955`, `fa0335f`, root log). Done: RKB's Overleaf edits,
the read-through and RKB's decisions D1–D11 (`notes/readThrough_2026-10-29.md`). Overleaf, the online appendix and GitHub
match `fa0335f`. Left for RKB: appendix B's φ_t = 0.971 is the solver's value with the strategic term, while B.1's formula
gives 0.972 (add a clause, or switch to the formula); section 6 sets the 4.0 p.p. rise in the tax rate against mkvss08's 3.6 p.p.
rise in spending (model spending is τ(1−α), about 2.8 p.p. of GDP; their measure can't be checked from the repo); the 35
duplicate page anchors from restarting the appendix pages at 1 (fix: number them A1, A2, …); the ε letter and the
Conde-Ruiz sentence's place (W20).

**W23. The AI review of 2026-10-29** (`coarse-output/coarse_review_29102026.md`; the 2026-10-22 round archived).
First-pass verdicts and the questions for RKB: `notes/reviewResponse_2026-10-29.md` (as a page with the reviewer's text:
https://claude.ai/artifact/LdBZr2X8KMxShSDnFXhLcP). O5 decided 2026-10-30: θ variant C is the paper's measure, pipeline
switched (commit `7694434`), overnight run done 2026-10-31 (all OK, results committed). 2026-11-02: RKB's decisions
on the OECD part applied and the text pass on every stale number done (root log 2026-11-02; its briefs and audit archived
2026-11-04 in `archive/notes/`). 2026-11-03/04: RKB's decisions on the cross-section applied (statutory ν, own turnout
with Luxembourg flat, layer 1 at the mean ω, appendix G's population and data variants), with the text pass, the Overleaf
push and the online appendix (`archive/notes/brief_retAgeChoice.md`). Left for RKB:
- Review the changes of 2026-11-02 (committed in `d4a55bc`; the cross-section's parts rewritten on 2026-11-04), among them:
  - own turnout throughout the cross-section, section 6's spending test included;
  - spending at the chosen design in section 7;
  - the hump paragraph and figure 7.3;
  - the softened inequality claims in the abstract, introduction and conclusion;
  - the cross-section appendix, now G;
  - the online appendix pages B5 and C6.
- Overleaf: the note and the paper are pushed (2026-11-02). The paper went with `--force` over Martin's online edit, a stray "i c"
  in `Sections/OECD.tex` plus line endings.
- Option F, figure 7.3 in index units, is built (`OECD26_ThetaFitIndex`) but not input;
  to decide with Martin.
- Online-appendix leftovers of the runs dropped on 2026-10-30:
  - B4 (Medicare), C2's first section and C4 (timing) still include RETIRED exhibits and stale prose;
  - C3's ξ statements have no ξ ≠ 0.3 rows behind them;
  - `OECD_Sources` documents the old index;
  - the style guide's §4 and `data/README.md` still cite the old appendix letters and "the deep test".
- Then the rest of "For RKB" in the review response.

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


**C15. `US_stationaryApprox.csv` has no `commonX` column** (code review of 2026-11-04,
`archive/notes/codeReview_triage.md`). A `stationaryApprox --vectorX` run on part of the grid keeps the common-X rows
of that part next to the new ones, with nothing to tell them apart. Add the column and key the merge on it before the
first vector-X run.

## Data tasks

**D2. Figure 5.1's data outside the pipeline.** `writing/Paper/Figs/coverageArg.eps` (beneficiaries of the
national pension system and of non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020),
table 6; neither the data nor the script is in the repository. Add `data/argentinaCoverage.csv` with a row in
`data/README.md` and a builder in `python/paper` (`REPLICATION.md` §5 lists it).
