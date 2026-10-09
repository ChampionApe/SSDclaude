# Research log — paper

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_paper.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-07 (afternoon) — section 7 refocused on RKB's three comments

RKB on section 7: its notation differed from the paper's, it was unfocused, and the cost's explanation did not
convince. One paper-writer agent rewrote it on `archive/notes/brief_section7_2026-10-07.md` (2,738 → 1,594 words
by `checkPaper.py`): ρ = 1 in the text and the exhibits; the cost as Okun's leaky bucket, the Harberger
derivation staying in appendix C.2; calibration and test in one paragraph with `US_ESC_Country`; ageing and
inequality against figure 1 with the new `US_ESC_Results` (ρ = 1 rows, `tablesUS.escResults`) and the new path
figure `US_ESC_Path` (`figuresOA.escPathPaper`, 2020 on); voting patterns in one paragraph; the other
elasticities in one closing paragraph. Appendix C took the timing reasons and the alternative-cost footnote; both
files now write ∂f/∂x and "inherited design" (RKB: conform the section to the paper, never extend the style guide
for it). `US_ESC_Calibration`, `US_ESC_Summary` (retitled) and `US_ESC_overview` are online exhibits now
(registry captions, `esc.qmd`); the country table's note names λ instead of citing the calibration table; Okun
(1975) added to the bib. Checks: `checkPaper.py` OK, latexmk clean at 59 pages, `test_onlineAppendix.py` 6/6,
`--map` rewritten (84 outputs, 14 the paper's). Committed as `fab23cc` and pushed to Overleaf; the online
appendix published to GitHub Pages on RKB's go (`quarto publish gh-pages`), RKB reviewing the paper online. At the
wrap-up: the country table's "observed" header no longer hyphenates (`\mbox`), the cost note's §4 records the
leaky-bucket framing, and the linear term for France's corner is TODO W9, a candidate for RKB's call.

## 2026-10-08 — read-through; review items 3, 5 and 6 fixed, TFP out of section 2

A read-through of the paper and the online appendix against the tables raised six items; RKB had 3, 5 and 6 fixed
(`8a96925`, pushed to Overleaf, which was untouched since `5cc21cb`). "In force" left the exhibits: figure G.1's
lower panel, `ESC_Path` ("Pension design θ_t", as in figure 7.1), the design axes of `US_ESC_overview` and
`UKUS_ESC_French`, and five notes, which say "θ_2020, the design chosen in 1990" as section 7.2 does; docstrings and
the technical note keep it. Section 5: the savings mechanism as in proposition 1, ε in units of the average formal
benefit, the fall in the informal savings ratio as figure 5.2 prints it (ι defined in its note). Section 2 lost TFP
(one in the code and the appendices) and got the type-0 conditions right; appendix D's β_j, B^i and p, appendix E's
tense and notation (Law 24,347 dated 1994), five control spaces. Checks: `checkPaper.py` OK, latexmk clean at 60
pages, `test_onlineAppendix.py` 6/6; the site rendered locally, not republished. Open: TODO W10, D3, W11; W12, C10.

## 2026-10-09 — section 7 rewritten on RKB's outline; appendix G replaces the robustness map

RKB's outline (`notes/plan_endogenousDesign.md`) and RKB's comments on a 16-item review set the rewrite, written fresh
rather than rearranged: 7.1 the deadweight cost (the corner and the weak hours cost, Disney and Kumler et al., Summers'
implicit tax, the Harberger principle as a reasonable start rather than a microfoundation), 7.2 calibration and the
determinants on `US_ESC_overview` (acute ageing, French income, voting, leisure; mild ageing dropped). New appendix G: G.1
the UK's own cost (`UK_ESC_Calibration`, `tablesUS.ukEscCalibrationTable`) and the country test, G.2 the path figure; the
robustness map left the paper, the online appendix and the registry (84 outputs). Pushed to Overleaf (`0624e14`); RKB's
review edits pulled back (`cb01426`), the two table edits (the cost table's caption, the country table without its tax
column) now built by `tablesUS.py`, three typos fixed. `test_onlineAppendix.py` 0 failed, latexmk 61 pages; `checkPaper.py`
fails on the online edits: G.1 comments out `US_ESC_Country`, which G.1 and `CalibrationOECD.tex` still cite, and
`eq:esc:implicitTax` is defined in 7.1 and C.2. Open: those two; abstract, conclusion, `paper_costLiterature.md` §4–5; `--map`.
