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

## 2026-10-28 — W22: the builders follow RKB's review (branch `review-2026-10`)
`NUM_Selection` joins `ONLINE_ONLY`: appendix D states the counts in words and page D2 keeps both count tables; its copy left
`writing/Paper`. The transported cost's country index prints as n (`λ_n = ε Π_{n,2020}/R_{n,2020}`) in the notes of `tablesOECD26`,
`tablesUS` and `onlineAppendix`, with `test_oecd26`'s assertion; `NUM_Residuals` spells "centers"; `OECD26_Spending`'s note calls
the model section 6's synthetic countries; `oecdFigure1.HIGHLIGHT` is the U.S. and France (legend "calibrated in section 6"), which
`OECD_Countries` bolds. README counts: paper inputs 23, online-only 31. test_oecd26 13/13, test_onlineAppendix 10/10, `--map`,
`--site`; commit 1f8a955, the site published from it.

## 2026-10-30 — the pipeline on θ variant C, reduced run list (`notes/brief_pipelineThetaC.md`, RKB's two rounds)
`config.US['theta']` = 'C', ρ grid 0.5/1/2, ρStationary 0.5/2; every U.S. arm command carries `--theta C --main`; outputs count
only at that thetaSource and every reader filters on it (`config.atTheta`, `datasets._readUS`). Dropped from the declarations:
PHIROBUST, Medicare, freeTheta, escCountryCosts, the timing checks, the comparison/Π-inclusive costs under CRRA, the `size` and
`commonR` cross-sections; escCosts is acute ageing; new entry `oecd26Variants` (A, A2pt, B), `--keepGoing`, `--exclude`, stage (i)
`--lanes`; the UK's exact brackets rescaled (smoke λ 3.628). `--list`'s 0/N for always-run entries fixed (`status`). Builders: the
cross-section's data side and figure 1.1 on C's 21 (`OECDdata_note.tex`), new `OECD26_ThetaVariants` ('paper' reproduces table 5),
`US_ESC_Country` on λ with France's own λ; 11 outputs removed, 10 site exhibits `RETIRED`. test_oecd26 12/12, test_onlineAppendix
10/10, fast suites 30/30. Overnight: `logs/overnight_2026-10-30/run.sh` (not run); `--map` is its step 5.

## 2026-10-31 — The cross-section under every θ measure, compared outside the paper (`logs/variantCompare/`, gitignored)
`logs/variantCompare/compare.py` reads results/ only and calls `tablesOECD26.slopes`/`panelData` for paper, A, A2pt, B, C × cps, cses
(sizePiR, common β). It writes figure 7.2's layout per combination (layers 1 and 2, PNGs on common axes), `slopes.csv`, `fit.csv` (|z| against
the data s.e., sign and 95%-interval counts, θ-prediction correlations/RMSE/same side of the U.S., mean ranks fixed in advance) and `summary.md`.
Self-check: OECD26_Slopes, OECD26_ThetaVariants and the OECD26_Layer1 pdf all reproduce bit for bit. Reading: turnout matters more than the measure.
cps fits the slopes best (C ≈ A ≈ B), cses predicts θ best (C ≈ A; layer-2 r 0.79 against 0.50 for C/cps), and spending-on-index is too steep
in every combination (z 3 to 17). C is A without CHE and NLD. Dropping LUX under cses steepens the data's index-on-growth slope (−0.44 → −0.77).

## 2026-11-02 — Section 7 at own turnout, the design figures, F.3/G to the site (`notes/brief_paperOECD_2026-11.md`)
`config.US['oecd26']`: turnout 'cses' (20 countries), `spendingReading` 'chosen' (section 7's spending 100 τInForce (1−α), both
layers; section 6 stays observed), thetaVariants A, B (A2pt off the declarations), `stylized`; `US['tauTheta']`. Notes give sample,
turnout and anchor (β 0.65, ω 1.26, ε 13.09); OECD26_Layer1 writes its note. New: OECD26_ThetaFit, _ThetaFitGrid (+Index, built,
not input; `tablesOECD26.thetaFit`), OECD26_Stylized, US_ESC_TauTheta; stage (ii) `oecd26Stylized` (results/oecd26_explore moved to
results/oecd26_stylized: every row reused, identical) and `escTauTheta` (`python/US/runTauTheta.py`, 27 s; self-check 5e-14).
ONLINE_ONLY: OECD_Calibration (appendix F's USUKFRCalibration is now the U.S. and France, `table:US:Calib`), UK_householdheterogeneity,
UK_ESC_Calibration, US_ESC_Country, US_ESC_Path; pages B6 `oecd-uk`, C7 `esc-countries`, C1/C3 sections; the site shows a figure's
generated note. NUM_Selection: A2pt out, stylized and escTauTheta in. build 52/52, `--map`, `--site` (22 pages, 34 exhibits),
test_oecd26 14/14, test_onlineAppendix 11/11, fast suites 30/30, checkPaper OK. Logs `logs/paperOECD_2026-11/`.
Follow-up (same day, after the writers' pass): OECD26_ThetaFit's note adds the standard deviations of predicted θ (0.10, 0.16)
against observed (0.33), `thetaFit`'s `sdModel`/`sdData`; θ is defined once, `config.THETADEF` (earnings-linked share c/(a+c) of
the least-squares line, times one minus the top-up share), in OECDdata's and OECD26_Omega's notes and the calibration table's cell;
`USUKFRCalibration` unregistered, its copies deleted. `--map` not rerun: NUM_Horizon raises while results/numerical is being rerun.
The pooled turnout's compulsory-voting countries are oecd26.COMPULSORY within the measure's sample (`datasets.compulsoryVoting`, read with ast): Belgium and Luxembourg under C.
Closing (main session): datasets.horizon('US')/residuals('US')/derivativeScheme/taxPolicyState/strategicTerm read through
`_readUS` (the rerun csvs carry thetaSource C); full build 51/0, `--map`, `--site`; date-only PDF rewrites of --map restored (README trap).

## 2026-11-04 — code review pass P3 (`notes/codeReview_triage.md`, paper module)

Guards, no output change: `compareResults` keys +15 and repeated keys compared in file order and counted, not dropped; `build.py`
skips `StaleInput` like `MissingInput` (`--list`: BLOCKED) and `--map` clears the cached workbook reads (`config.clearCaches`), so 20
rows of REPLICATION's map gained their workbook or csv; last-wins readers (`rhoGrid`, `usSweep`, `usShockRow`, `escRow`, `escCountry`)
raise on a repeated key; `usAlpha` raises, cached; the overview figures raise on a missing headline row; `siteData` checks are NaN-safe
and its skips print; OECD26_Variants' paper rows raise, OECD26_Omega checks layer 2's data columns, OECD_Correlations the csv against
the figure's data (`oecdFigure1.figureCorrelations`); typed prose numbers now come from config/data or assert it (`paperWording`).
Moved on purpose: NUM_Selection(Files) count `US_shocksXiCommonX.csv` and `escXiRobustness.csv` (Experiments 2 -> 3 files, 108 -> 162 rows,
60 -> 90 counted; Endogenous design 12 -> 13 files, rows unchanged: the xi csv has no row at θ C); the `_thetaA/B` banners name
`results/oecd26_theta_<V>/`. 36 orphan files of retired builders `git rm`ed from results/paper; dead defs and imports out (`spendingPath`
stays: REPLICATION §3 cites it); Argentina's commands carry `--commonX`. Checks: tests 2/2 (16 + 11), build 59/0, `--map`, `--site`, quarto OK.
