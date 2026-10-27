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

## 2026-10-09 (evening) — the online appendix rebuilt on RKB's outline (branch `oa-revision`)

RKB's outline (`notes/plan_onlineAppendix.md` §1) and the execution plan (§2, decisions D1–D6, taken as recommended)
replace the site of 2026-10-06: 20 short pages in four parts, static exhibits from the pipeline beside Observable JS
explorers. New `siteData.py` (four `data` outputs in `results/paper/Data`), six tables in `tablesOA.py` (the two leisure
calibrations of Argentina and the OECD economies, the regroupings, the two costs), `datasets.usShocksXi`/`escPathHost`,
`onlineAppendix.py` rewritten small (registry `EXHIBITS`, per-page numbers, `_variables.yml`, retired `\oa` keys
aliased), stage (ii) entries `shocksUKUS*`, `shocksXi`, `escPathHost`. 94 outputs; `test_onlineAppendix.py` 10/10, four of
them tying the datasets to figures 5.2, 6.1, 7.1 and G.1. The site reads the ESC readings against the same-reading
baseline, as the paper session's uncommitted `figuresUS`/`tablesUS` change does. On RKB's layout comments A2 no longer
shows figure 5.2, compared facets stack on one x axis, and every chart draws at its own box's width (`fitted` in
`oa.js`; OJS's `width` spans the page on a page with a `.column-page` block). Open: D5, merge, publish (plan §2.11).

## 2026-10-09 (night) — D5: 59 outputs retired; the site merged and published

The registry keeps the 35 outputs the paper inputs (15) or the site shows (20). Gone with their builders: `build._variants`
and every `_vectorX` twin (builders keep `commonX`), the shock, CRRA and ESC experiment tables, `US_ESC_Summary`,
`US_ESC_Results`, `US_ESC_ScaleWedge`, the two UK-US figures, the ρ-grid, path and ξ tables and `ESC_Path` (128 files in
`results/paper` and `writing/Paper`). Marks no longer name table rows (OECDdata's alone remain); the workbook-ξ path check
moved to `siteData.escPaths`; `build._usedIn` skips commented-out inputs; `NUM_Selection` rebuilt for the UK acute rows.
Live outputs rebuild identical but for the marks' link fields (PDFs by date). Thinner chart rows (44 px a row). Merged
(`ea52b8e`) and published (gh-pages `e3810ba`). `US_ESC_overview.marks.json` was rebuilt on the merged code without links and
stays uncommitted with the paper session's same-reading outputs. Open: TODO W13, C12.

## 2026-10-22 — pre-review pass: front matter aligned with section 7, W12 and W13 closed

On RKB's list after a full read-through. D3 stays open with a caveat in G.1 (the bound Ṽ ≥ 0.10, France at the UK's cuts
0.246) and F.3. Substantive: u''_hh ≤ 0 (section 2); proposition 2's inequality and θ results stated for equal propensities
to vote, appendix B.1 says so and gives μ_H/μ_L < (c_H/c_L)² for inequality; the CRRA-GHH utility written out (section 3);
y_i defined in 7.1. Abstract, conclusion and (minimally) the introduction now say what 7.2 finds: Summers/Harberger instead
of Okun, re-election rather than "the 2020 electorate", the design one period ahead, inequality's effect on the design
signed by the IES, the UK test without "orders as observed". Referee points in 7.2: λ's size against participation
elasticities, and the return factor λ absorbs. W12: section 6's IES reason is curvature, section 5's drops ω (W15 left; W14, `BergGEwp`'s title, is RKB's);
W13: every `\oa` key current, five pointer sentences rewritten. Editorial fixes, notation (h_{t,i}, s_{t,i}, τ^{+1}_t, k_t),
three table notes via `tables.py`/`tablesUS.py`. latexmk 61 pages, one 0.5pt overfull; checkPaper OK; test_onlineAppendix 10/10.
Committed and pushed to Overleaf and GitHub on RKB's go, for the full review.

## 2026-10-24 — C4 of the review response (A6): appendix D's tables
New `tablesHorizon.py`: `NUM_Horizon` (the calibration year and one period later at T ± periods and under the
steady-state terminal condition, U.S. design given and chosen, Argentina with its reform) and `NUM_Residuals` (the tax
rule's first-order-condition residuals off the grid, as solved and against converged τ-derivatives), both copied
into `writing/Paper` for appendix D, not input yet. `NUM_Selection` leaves `ONLINE_ONLY` (appendix D's counts table too)
and gains the columns no selection (−1) and not recorded (blank) and a note naming every counted exception from the
data (`datasets.countExceptions`; today the one design-layer fallback). New readers `datasets.horizon`, `residuals`,
`derivativeScheme`; `selectionCsvs` adds the horizon csvs. Inputs from `python/{US,InformalSavings}/runHorizon.py`
(not wired; `REPLICATION.md` §3). Numbers and the open U.S. τ-derivative issue: `archive/notes/reviewResponse_2026-10/ledger_C4.md`.

## 2026-10-25 — W9 of the review response: the online appendix pages, appendix D's layouts
New site pages B5 (`oecd-medicare`: `OECD_Medicare`, host `USMedicare` in `OECD_Counterfactuals`) and C6 (`esc-oecd26`:
the cross-country test on all 29 and at CSES turnout, six `OECD26_*_29`/`_cses` outputs), sections `oecd-state` (A13,
`US_TaxState` from `C5_taxPolicyState.csv`) and `num-horizon` (`NUM_HorizonPaths`); 50 outputs, 40 exhibits. The paper's
`OECD26_*` now read the design in force in 2020 (checkpoint 2; `tablesOECD26.PAPER`). Appendix D's tables fit the
page: `NUM_Selection` groups the files by solve (file by file in `NUM_SelectionFiles`), `NUM_Horizon` short headers;
`ArgentinaUniversal`, `OECD26_Omega` within the measure; `NUM_Residuals`' note describes C6's least-squares cubic in
ln(1−τ) (`config.US['gridSettings']['gradKnotSpacing']`); `US_ESC_Country`'s France note gives the log-corner reason.
Eight stale OA sentences fixed against the datasets (ω ranking, θ = 1 corner, France vs U.S. path, cost on the design a
third, timing). Not done: A13's myopic/Markov split (needs a model function). Checks: test_onlineAppendix 10/10, test_oecd26 5/5.

## 2026-10-27 — R6: the cross-section's variants run, their builders (branch `review-2026-10`, `notes/plan_byObject.md`)
Runs (`logs/R6/`, 3 h 19 min): `runOECD26.py` none, sizePiR (anchor, both layers), size and sizePiR under commonR,
cps and cses; `runESC.py --stage country --spec sizePiR --tag Costs` -> `escCountryCosts.csv` (stage (ii)'s
`escCountryCosts`). Every row nEqMax 1, nFallback 0; the paper's size rows unchanged to 1e-15 (relative). Anchor ε 20.014
(λEff 11.108); layer 1 index on growth −0.23, on the Gini −0.67 (0.29); under ε the deep test closes 0.33 of the UK's
distance and 0.06 of France's. New outputs `OECD26_Spending` (with its generated note), `OECD26_Robustness`,
`OECD26_Reconcile`, `USFRCalibration`, `OECD26_*_size`; `US_ESC_Country` over λ and ε without UKUS; `StaleInput`.
README cut to 98 lines (pre-cut in `archive/readmes/`). Ledger `notes/ledger_R6.md`. build 58/58, paper test_oecd26
13/13, test_onlineAppendix 10/10; US test_oecd26 53/55: M's "other rows unchanged" at 6.5e-13 > 1e-13, from
`runESC.mergeWrite` rereading with pandas 3's default parser (16 decimals).

## 2026-10-27 — R7: the UK as a second host economy retired (branch `review-2026-10`, `notes/plan_byObject.md`)
RKB's decision: the UK is donor data and the deep test. Gone: stage (i)'s `FRUK`/`UKUS` sweeps, stage (ii)'s `shocksUK*`,
`shocksUKUS*`, `escShocksUK`, `escShocksCRRAUK`, `escExperimentsUK`, `config.US['ukHost']`, `extraSweeps`, `esc['uk']['scenarios']`;
`--host` of `runShocksUS.py`, `runESC.py`, `collectESCexperiments.py`, `--grouping` and `testEU`'s regrouped sheets; the UKUS row
of `runESC.stageCountry` (old rows stay in `escCountry.csv`, unprinted); `runESCcrra.py --host UK` runs `--stage calib` only.
Builders `FRUK_`/`UKUS_householdheterogeneity`, `OECD_Regroupings`, site pages B2/C2 and exhibits retired (keys aliased to
`oecd`/`esc`). csvs, pickles, last builds: `archive/results/ukHost_2026-10/`; pages `archive/code/OnlineAppendix/`.
`NUM_Selection`: experiments 4 -> 2 files, endogenous design 14 -> 12 (tax) and 5 -> 4 (design); maxima, fallback unchanged.
build 55/55 (`US_ESC_Country` identical), `--map`, `--site` (20 pages, 38 exhibits), test_onlineAppendix 10/10, fast suites
29/29 (1067 s), test_eu 23/23, test_esc 90/90. Logs `logs/R7/`. TODO D3 closes.

## 2026-10-27 — W21: the online appendix, the replication map, the READMEs (branch `review-2026-10`, `notes/plan_byObject.md`)
The transported cost parameter prints as `\varepsilon` (appendix C.2's Harberger elasticity) in every builder and site note
(`tablesUS.COSTSYMBOL`, `tablesOECD26`, `onlineAppendix.OECD26LAYER1`); `\epsilon` stays the universal pension. `US_ESC_Country`
gains each economy's Π/R of 2020 under the U.S. ε (UK 0.529, France 0.432, `escCountryCosts.csv`) and in its note the U.S. 0.555,
checked so that ε·Π/R is the U.S. λ (1e-3). Notes point to appendix F for the UK and France (`OECD26_Reconcile`, `UK_ESC_Calibration`),
section 7.4 (`OECD26_Spending`); `NUM_SelectionFiles` names the unprinted regrouped-UK row. Page C6 by variant (the paper's, λ,
β rule, own turnout, 29; new keys `esc-oecd26-paper`, `-beta`, none retired); the codes keep the B2/C2 gaps. `REPLICATION.md` §3
and `data/README.md` follow; the stale `FRUK_`/`UKUS_householdheterogeneity` copies removed from `writing/Paper`. build 55/55 (paper
inputs 24), `--map`, `--site`, test_onlineAppendix 10/10, test_oecd26 13/13, checkPaper OK; `logs/W21/`. The site's paper numbers
wait for a fresh `writing/Paper/main.aux` (2026-10-26's lacks `sec:esc:deepTest`): rerun `--site` after V's latexmk.
Addendum: `selectionCsvs` covers `escCalibrationCosts`, `escCountryCosts` and `results/oecd26` (a new group, Luxembourg's `noTurnout` rows uncounted); `NUM_Selection` endogenous design 14/313/164, cross-country 3/586/576, maxima unchanged, no prose number moves.
