# Brief R2: numbers-against-tables audit of the endogenous-design rewrite

For the `paper-reviewer` agent (read-only). Every number in the files below is checked against the cell it
stands next to, in the paper's units and precision (`notes/paper_styleGuide.md` §3); a mismatch to the
printed precision, a wrong unit, a sign in symbols, or a number no table carries is a finding. The
sources are `writing/Paper/Tables/*.tex` (the generated tables carry a `%% Source:` banner naming the csv;
go to `results/esc/*.csv` only when a table does not print the quantity) and the figure marks
(`results/paper/Figs/*.marks.json`).

## 1. Files and their tables

- `writing/Paper/Sections/EndogenousTheta.tex`: `Tables/US_ESC_Variants.tex`, `Tables/US_ESC_Results.tex`,
  `Figs/US_ESC_Path.marks.json`, and for the closing paragraph `Tables/US_ESC_Calibration.tex`,
  `Tables/US_ESC_Summary.tex`; the figure's note.
- `writing/Paper/Appendix/EndogenousDesignDetails.tex`: `Tables/US_ESC_VariantsCountry.tex`,
  `Tables/US_ESC_VariantsShocks.tex`, `Tables/US_ESC_Calibration.tex`, `Tables/US_ESC_Summary.tex`,
  `Tables/US_ESC_Country.tex` where it is cited.
- `writing/Paper/Appendix/EndogenousDesign.tex`: the magnitude paragraph's numbers
  (`Tables/USUKFRCalibration.tex` for $\nu_{2020}$, `Tables/US_ESC_Calibration.tex` for the multiples).
- `writing/Paper/Sections/Introduction.tex`, `abstract.tex`, `Sections/Conclusion.tex`: the cost
  sentences (the ordering claim, "pinned by the U.S. and the UK", any number).
- The online appendix's texts for the new exhibits: `python/paper/onlineAppendix.py`, the group
  `esc-variants` (the `text` strings), against the same tables; and the notes of the generated tables
  `US_ESC_Variants`, `US_ESC_Results`, `US_ESC_VariantsCountry`, `US_ESC_VariantsShocks` for internal
  consistency (a parameter named in a note against the calibration csv).

## 2. Also check

- Every `\ref`, `\eqref` and `\oa{}` in the three files resolves (`writing/checkPaper.py` reports it; run
  nothing, read its last run if a log exists under `logs/`, else say it was not checked).
- The pinned and chosen tax rates quoted in section 7.3 come from the right column (pinned against
  chosen) and the right variant block.
- The designs quoted as "the corner" are printed as 1.000 or 0.000.
- Changes in p.p. are differences of the printed levels at the printed precision.

## 3. Report

Findings ranked by cost, each with `file:line`, the number as written, the cell it should match (table and
row key), and the fix. Then one line per file: "n numbers checked, m findings". At most 50 lines.
