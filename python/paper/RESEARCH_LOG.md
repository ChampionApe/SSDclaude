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

## 2026-10-08 (afternoon) — the cost variants through stage (iii) (phase D, `notes/brief_escVariants_pipeline_2026-10-08.md`)

`config.US['esc']` gains `paperSpec = 'sizeLQ'` and `variants` (linear-quadratic, linear, quadratic); `spec` stays `'size'`
for every rho-dependent exhibit until TODO R6. `datasets.escParams` (lambda_1, lambda_2, kappa from `p`, `kappa`),
`escEconomies` (theta*, tau, Vtilde, M per economy), `tag` for the `_kappaFR` csvs. New outputs: `US_ESC_Variants`,
`US_ESC_VariantsCountry`, `US_ESC_VariantsShocks`, `UK_ESC_VariantsShocks` (online only); `US_ESC_Results` one block per
variant, `US_ESC_Path` the three chosen paths, `ESC_PathTable` two variant blocks (the path marks link there). Notes of
`US_ESC_Calibration`/`_Summary` self-contained ("the quadratic cost", no online-only figure). Group `esc-variants` (OA.4.2,
later sections renumbered). The robustness map is unchanged: a variant row needs a new kind in `_mapChosen`. Checks: the
quadratic cells of every ESC table equal HEAD's; 88 outputs build; `test_onlineAppendix.py` 6/6; `checkPaper.py` OK.

## 2026-10-08 (afternoon, evening) — section 7 rewritten on the cost with a linear term

RKB's sketch (`notes/plan_endogenousDesign.md` §A-B) executed autonomously by eleven agents on Fable and Opus
(§C the plan, the decisions in §C.1, the status and RKB's calls at its head). Three costs at ρ = 1, one general
form ln f = -τ(1-θ)[λ₁M + ½λ₂Ṽ(1-θ)] with M = Σγ_i|y_i-1| the amount the flat component carries (adopted at gate
1 over a common Ṽ weight, under which the U.S. design caps λ₁ below France's corner threshold under every
variant): the quadratic (the earlier draft's), the linear (knife-edge: the UK at θ = 0, France at its corner,
every U.S. counterfactual a corner) and the linear-quadratic (λ, κ) pinned on the U.S. and UK designs (κ =
0.129, λ = 5.237; France predicted 0.806; pinned on France instead, κ = 0.629 and the UK at 0.397). The paper:
section 7 on RKB's outline (3,029 words; the implicit tax, the literature in four blocks, the cost as the
ingredients the literature supplies, US_ESC_Variants, US_ESC_Path and US_ESC_Results across the variants, the
inequality finding against figure 1: under the linear-quadratic cost France's income distribution moves the
design to 0.850, nearly as far as ageing), appendix C (the general form, the corner stated in words, the
propositions moved to the technical note; 3,655 words), appendix G new (G.1 calibration across variants and
countries, G.2 the counterfactuals, G.3 the role of ρ; the robustness map is appendix H), the abstract,
introduction and conclusion aligned, the technical note's specification, calibration kinds and the two
propositions. Pipeline: `config.US['esc']` paperSpec and variants beside spec (until R6), six new outputs, the
online appendix's `esc-variants` group (OA.4.2), 88 outputs mapped, site rendered locally, not published.
Reviews: the referee pass (`archive/notes/review_escVariants_R1_2026-10-08.md`, nine findings applied, three
pushes for RKB) and the numbers audit (R2, twelve items applied; no numeric mismatch beyond a rounded ratio).
Checks: checkPaper OK, latexmk clean (69 pages), test_onlineAppendix OK, the fast suites 25 of 25. Commits
428412e to the wrap-up, local; appendix C pushed to Overleaf at RKB's request at eefb460; the paper tree at bef83fa pushed on RKB's request
(14 files, no online edit found by the dry-run pull).
