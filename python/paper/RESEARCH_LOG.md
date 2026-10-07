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
appendix is rendered but not published (on RKB's go).
