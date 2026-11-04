# The cross-section's new main specification and appendix G's variants (2026-11-03/04)

RKB's decisions:
- 2026-11-03: ν is corrected for each country's retirement-age gap to the U.S. (appendix F's rule, `oecd26.retAgeNu`);
  the cross-section's main specification becomes own (CSES) turnout with Luxembourg flat (`csesFlat`) and layer 1 at
  the mean layer-2 ω (`omegaRule mean`). Both corrections were run in full overnight (`logs/retAge_2026-11-03/`,
  pages "Statutory or exit age?" and "Statutory and exit exhibits" on claude.ai).
- 2026-11-04: the **statutory** correction (`nra`) is the main variant. France and the UK stay as the main tree's
  results are (FRMain.xlsx's appendix-F column; the UK's gap is 0); the exit-age version is a record only, not
  adopted (`archive/results/retAgeExit_2026-11/`).
- Appendix G keeps two **population variants**, ν uncorrected (`none`) and exit-age corrected (`exit`), and two **data
  variants**, the measures A and B renamed, run at the statutory correction only. Names (`config.THETANAMES`): C
  "public tier" (the paper's), A "public tier, 23 countries", B "all mandatory tiers". `OECD26_Variants` (two panels)
  replaces table 11; `OECD26_ThetaFitPopulation` and `OECD26_ThetaFitMeasure` (3 x 2, the paper's row included)
  replace figure G.1; table 12 (`OECD26_Stylized`) is gone.
- U.S. turnout is dropped from the paper and the online appendix (section 7.3's inequality paragraph goes with it);
  pooled turnout and A2pt are retired.
- Online appendix C6: the paper's specification; the four variants in full (figure 7.2 and table 10 each); Luxembourg
  left out (statutory, 20 countries); layer 1 at the U.S. ω (statutory, csesFlat); the countries outside the test.

## State (2026-11-04)
- Rows: the overnight rows merged from results/oecd26_retage/ into results/oecd26/ (runOECD26._write; the 748 old rows
  unchanged); layer 1 at the U.S. ω (statutory) and the data variants A, B (statutory, csesFlat, mean ω) run
  (`logs/variants_2026-11-04/`): every reading complete, one equilibrium, no fallback, on its anchor.
- Code: config, runOECD26 (csesFlat and mean allowed into results/oecd26/), runShocksUS, datasets, tablesOECD26,
  figuresOECD26, build, tablesOA, onlineAppendix, test_oecd26 (14/14); READMEs, REPLICATION.md (map regenerated).
- Build 59/0; online appendix 22 pages, 43 exhibits, test OK; paper 75 pages, checkPaper OK, Overleaf pushed.
- Readings worth the text: under "all mandatory tiers" layer 1's fit drops (r 0.37, RMSE above the mean's), Iceland
  predicted at 0.168 against 0.813; Luxembourg flattens the data's slope of the index on population growth (-0.44
  against -0.77 on the 20).

## Closed 2026-11-04
1. Text pass: sections 6 and 7.3, appendix G (G.4 rewritten for the variants), introduction, conclusion, abstract, C6.
   RKB's addition: OECD26_Variants reports the uncorrected ν without Luxembourg, and G.4 says Luxembourg alone drives
   that reading's fit (r 0.36 with it, 0.74 without, between the exit age's 0.69 and the statutory age's 0.76 on the
   same 20). checkPaper OK.
2. Overleaf pushed (22 files updated, the 6 retired exhibits deleted); committed and pushed to GitHub; the online
   appendix rebuilt and published to GitHub Pages from the cleanup's commit.
3. Cleanup: results/oecd26_retage/ deleted (merged into results/oecd26/); results/oecd26_stylized/,
   results/oecd26_theta_A2pt/ and results/oecd26_theta_C/ moved to archive/results/; the exit-age worktree and its
   branch deleted after its results, checks and paper went to archive/results/retAgeExit_2026-11/; this brief and the
   cross-section's earlier briefs moved to archive/notes/ (archive/INDEX.md).
