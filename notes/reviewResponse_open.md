# Review response (W16): what is still open

The response to the AI review of 2026-10-22 (`coarse-output/coarse_review_22102026.md`) on branch
`review-2026-10`. Its history is in `archive/notes/reviewResponse_2026-10/`: the plan with the package status table
(`plan_reviewResponse.md`), the tracker of the agreed actions A1–A14 and comments 1–25 (`paper_reviewResponse.md`),
the theory notes T1–T3, the ledgers C1–C6 (old → new for every number the prose cites) and the briefs. Read them
only for the reasoning behind a choice; this file is the state.

**Done.** Phases 0–3: candidate counts (C0), the U.S. pension-only calibration and Medicare reading (C1), Argentina
(C2), the 26-country test (C3), horizon and residuals (C4), the smaller numbers (C5), the converged U.S. solvers
(C6), theory notes T1–T3, the writing W1–W9. Committed through `cd81410` (phases 1–2 and C6); phase 3 and
everything below are in the working tree.

## Decided with RKB, 2026-10-26

- Abstract's "ageing is the main determinant of U.S. pension spending" and footnote 11's "modest" (design gap
  0.074) kept as written.
- Proposition 2: "decreasing in θ, given the continuation policy when there is a universal pension".
- Section 5's Gonzalez-Rozada and Ruffo sentence written from the paper (`pdfs/gonzalezrozada_ruffo2016.pdf`,
  IDB-WP-629: savings levels, 2–4% per ten points of treatment probability, at every age); E.3 dates the tax
  target; `data/README.md` has EPH 2006 H2 and WPP 2024.
- A13: the strategic term instead of the myopic/Markov split, OA table `US_Strategic` on `oecd-state`
  (`c5Numbers.py strategic`), nothing in the paper.
- France's corner slope in the pipeline (`runESC.py --stage corner`, `escCornerSlope.csv`, checked by the
  `US_ESC_Country` builder and `test_esc` S17).
- C.2: the common-wedge sentence cut; the implicit tax is "the redistributive part" of Summers' tax component.
- France's ν at the PaG 2021 retirement-age gaps (1.5, 1): `FRMain.xlsx` edited by RKB; appendix F rewritten.

## Open, in order

1. **C7, France's reruns** (running at 2 solvers; `notes/brief_C7.md`, ledger `notes/ledger_C7.md`, runs in
   `logs/C7/`). Then the French numbers that moved, in the paper and the OA prose (paper-writer on Opus 5.5),
   brought to RKB before any commit. Done 2026-10-26, with the five fallback passages; the workbooks' `Readme`
   sheets deleted (their content is in `data/README.md` and appendix F).
2. **Commit** phase 3 and the 2026-10-26 changes, on RKB's go.
3. **V**, on RKB's go:
   - builds and tests: `build.py`, `checkPaper`, latexmk, `test_onlineAppendix`, `runTests.py`;
   - a numbers-against-tables audit of the whole paper (paper-reviewer), and a referee pass over sections 3 and
     7 and appendices B–D against each review comment (paper-reviewer-lead);
   - documentation: `REPLICATION.md` maps the informal-retiree spending 1.053/1.968% (computed in prose from the
     shock csvs) and lists `c5Numbers.py strategic`; `data/README.md`'s Argentina ν row (1920/1950 copy 1980,
     2100 copies 2070); the technical note's stale numbers (num_esc:49/51 permanent timing against
     `test_escTiming` 0.753/0.870, the flat-only variant and path iteration dated 2026-10-03, model_calibration:25
     "0.738 against 0.745"); `NUM_Residuals`' note still says "smoothing spline" (`tablesHorizon.py`);
     `data/oecd29_sources.csv` still says "appendix F's 63.5" (stage (0) rerun, network); `python/US/README.md`
     is 209 lines against the ~100 budget.
4. **Overleaf** push of both projects and the OA publish, on RKB's go.
5. **Wrap-up**: TODO W16 removed, a root `RESEARCH_LOG.md` entry, this file and C7's brief and ledger archived
   with a line in `archive/INDEX.md`.

## For RKB, not blocking

- The 26-country test: both Gini relations take the opposite sign to the data's (flat there); the paper says so.
- λ is 12–205 times what participation and taxable-income elasticities imply; the paper reads it as standing
  in for other costs.
- Section 7.1's "the part that buys nothing distorts like a tax" measures against an earnings-related benchmark
  that itself returns Π < R; C.2 now says "redistributive part", 7.1 does not.
- Deferred: the A13 split (a new model function), D3's recount, W17 (pointers to the OA).
