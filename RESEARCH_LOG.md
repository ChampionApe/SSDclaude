# Research log (cross-cutting)

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_root.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-07 (evening) — the repo cut to the paper as it stands: notes, logs, tests and context

On RKB's instruction, what served the path rather than the paper left the live tree. `notes/` keeps four files (the
TODO, the style guide, the findings, `paper_costLiterature.md`); sixteen closed notes, plans and briefs went to
`archive/notes/`, four 2026-08-23 tex/bib leftovers were deleted. Every session-log entry to this date (67, six logs)
moved to `archive/sessionLogs/`, and `archive/INDEX.md` now opens with the paper's decisions by theme. Retired
diagnostics went to `archive/code/`, superseded results to `archive/results/`; `logs/` keeps `finalRun1002/` and
`finalRunC8/`. The traps moved to the root README, D1's data caveats to `data/README.md`, the `\oa{key}` rule to the
style guide; READMEs, `CLAUDE.md`, the agent definitions and code comments repointed. Tests: `US/test_createCopyFromt0.py`
archived (nothing calls the US model copies), T2's pre-split copy cut, `test_eu.py`'s FRUK check asserts the sheets
load, `paper/test_onlineAppendix.py` registered; the permanent-timing and FOC-layer checks stay (the technical note
quotes them). OA.2 and OA.3 cite appendices E and F; site republished (gh-pages `3d60368`). C9 closed: the two
`informalAnalytical` failures since C8 were a solver stopping rule, fixed in that module (its log); fast suites 24 of 24.

## 2026-10-09 (evening) — the online appendix on a branch in its own worktree

While another session drafts the paper on `main`, the online appendix is rebuilt on branch `oa-revision` in the worktree
`../SSDclaude-oa` (`.venv` a junction to the main checkout's), so neither session's commits interleave with the other's.
The only shared file is the generated `writing/Paper/onlineAppendix.tex`, which defines every key the paper cites.
Plan, decisions and status: `notes/plan_onlineAppendix.md` (untracked in the main checkout); module logs: python/paper,
python/US. Headless Chrome (`--headless=new --virtual-time-budget`) checks the OJS pages when the desktop session is
locked and the browser extension's tab is hidden.

## 2026-10-09 (night) — the online appendix merged, published, and the unused outputs retired

On RKB's go `oa-revision` went into `main` by fast-forward (`ea52b8e`). The idle paper session had uncommitted edits
in four files the branch changes: all its uncommitted work was first stored as a stash ("paper session's uncommitted
work at 58b53fb"), then three-way merged and left uncommitted on the new HEAD. `_escPairs`'s same-reading baseline
and its README line carry over; its edits to code the branch retired (`_escTable`, the old site registry) and the
retired tables' rebuilt files live only in that stash. D5 done: 94 outputs down to 35 (python/paper log). The site
was published from the clean worktree (gh-pages `e3810ba`); worktree and branch removed, run logs kept in `logs/oa`.
The plan is archived (`archive/notes/plan_onlineAppendix.md`); open: TODO W13 (the paper's pointers to the site), C12.
Bash-tool heredocs collapse a double backslash to one: edit scripts with TeX in them go through a file written by Write.

## 2026-10-23 — the AI review reconciled and the response planned

The review of 2026-10-22 (`coarse-output/`) was read critically and reconciled comment by comment with RKB:
`archive/notes/reviewResponse_2026-10/paper_reviewResponse.md` holds the agreed actions A1–A14 and the detailed comments at their first-pass
verdicts; `archive/notes/reviewResponse_2026-10/plan_reviewResponse.md` turns them into agent packages, with a checkpoint before any writing (TODO
W16). Found on the way: the U.S. design target is pension-only (39.2/49.2; PaG 2021 has 49.6) while τ includes
Medicare, against the text (decided: pensions only in all three countries, Medicare in the OA); appendix B.1 prints
the young term with 1+β; ν_t is UN WPP 2024 total population growth, not census data. An agent assembled the
29-country inputs (`data/oecd29*.csv` by `python/paper/oecd29Data.py`, `notes/data_oecd29.md`). Python run with
`-I` ignores PYTHONIOENCODING: Greek letters print with `-X utf8`.

## 2026-10-24 to 2026-10-26 — the review response carried out (W16 closed)

Phases 1–3 of the plan of 2026-10-23: code and runs C0–C7, theory notes T1–T3, the writing W1–W9 and verification V
(numbers audit, referee pass, 15 fixes, `runTests.py --all` 35/35), commits `f3a15a4`, `cd81410`, `6bb36ec`, `d5f0ef6`.
Decided with RKB on 2026-10-26: A13 as the strategic term in the OA only; France's ν at PaG 2021's retirement-age gaps
(1.5/1), rerun as C7, which moved the French leisure rows and left one design-layer fallback state, now stated; section
7.1's wording kept. The workbooks' `Readme` sheets were deleted, their content in `data/README.md`. Both Overleaf
projects pushed and the OA published from `d5f0ef6`. Everything is in `archive/notes/reviewResponse_2026-10/`
(`archive/INDEX.md`); left open: TODO C13 (the A13 split), D3, W17. Findings #20–21.

## 2026-10-27 — the paper by object (C14, R6, R7, W18–W21, V)

Decided with RKB in the morning: one laboratory, the U.S., with France and the UK as donor data plus the deep test;
section 6 ends with the 26-country test of spending at the observed designs without the cost, section 7 holds the
deep test (7.3) and the design test (7.4); the cross-section transports ε (λ_i = ε Π_i/R_i, `sizePiR`), β common with
the common-return bracket beside, both turnouts run; the UK as host retired (R7, D3 closed). Plan and ledger in
`archive/notes/byObject_2026-10/`. Checkpoint 1: ε, common β and U.S. turnout as the main variant, the inequality verdict
conditional on the turnout profile, the deep test under both transports (a third of the UK's distance and little of
France's under ε, a quarter of each under λ). Runs 3 h 19 min, every row one equilibrium; new exhibits
`OECD26_Spending`, `OECD26_Robustness`, `OECD26_Reconcile`, `USFRCalibration`; `runESC.mergeWrite` rereads csvs
round-trip exact. Overleaf pulled before the writing (RKB's abstract and introduction edits kept) and pushed after V
(numbers audit and referee pass by two reviewers, their fixes in). Symbol rule: the transported parameter is
`\varepsilon`, never the universal pension's `\epsilon` (style guide §4). Lesson: tex edits never through the Bash
tool's sed or heredocs, which mangle backslashes (a `\v` became a vertical tab); scripts written with Write instead.
Commits e14e556, 8267f10; `runTests.py --all` 35/35 in 3068 s; the online appendix published from 8267f10 (gh-pages 4281a38). Open: RKB's Overleaf review (the Conde-Ruiz sentence's new place in the
introduction, the ε letter), W17, C13, C12, D2, W14.

## 2026-10-28 — RKB's review on Overleaf (W22): table 8 out, sections 6 and 7 on synthetic countries

RKB edited on Overleaf (abstract, introduction, sections 4 and 5); pulled before every change, pushed twice. On RKB's requests:
table 8 (equilibrium counts) to the online appendix only, appendix D and section 4's footnote in words; typos; the transported
cost's country index is n (λ_{n,t}, style guide §4); section 5's Ruffo comparison and IES paragraph cut. Then the paper leans less
on the UK and France: section 6 takes the counterfactuals from France and ends with the cross-section as 26 synthetic countries
(the U.S. model with each country's demography, income distribution and design); the UK/France deep test moved from 7.3 to
appendix G.1; 7.3 is the cross-section, introducing ε, with fewer numbers; conclusion and references follow; figure 1 highlights
the U.S. and France. 82 pages (86 yesterday); commit 1f8a955, the online appendix published from it (gh-pages b2d53ad). Traps:
`build.py --list`/`--map` re-save figure PDFs that differ only in CreationDate (`git checkout` them); the Read tool cannot open
`main.pdf` ("password-protected"), `pdftoppm`/`pdftotext` can. Open: TODO W22, RKB reviews on 2026-10-29.

## 2026-10-29 — RKB's review continued (W22): read-through and decisions D1–D11

RKB's Overleaf edits pulled (abstract, sections 5–7, and the notes of tables 4 and 5 and figure 6.2, which carry the
pipeline banner and were carried into `tablesUS`, `tablesOECD26`, `figuresOECD26`). Abstract and conclusion shortened;
table 4 at two decimals (β added, then cut on RKB's call); table 5's slopes and standard errors stacked. Full read-through
by three reviewers, then RKB's decisions D1–D11 applied by three writers, one file set each (`notes/readThrough_2026-10-29.md`).
D1: λ constant for the U.S. and ε carried across countries, both explained. D2: the cross-section's U.S. is measured from
the OECD data. D3: cost parameters at two decimals everywhere. PDF links fixed (`\theHequation`; setspace before hyperref,
which had broken every footnote link). Commit `fa0335f`; Overleaf force-pushed by RKB; the online appendix published from
`fa0335f` (gh-pages `a47bb03`). Open: TODO W22 (φ_t, mkvss08, page anchors); next a coarse review round in a fresh session.

## 2026-10-29 (afternoon) — AI review round 2 (W23)

The 2026-10-22 coarse round archived (`archive/notes/reviewResponse_2026-10/coarseReview_2026-10-22/`, INDEX line). New
round on `fa0335f`: `coarse-output/coarse_review_29102026.md`, 12 overall and 19 detailed comments, major revision. Run on a
`latexpand` flattening of `writing/Paper/main.tex` (OpenRouter had no credit for PDF OCR; no Docling): the reviewer saw no
reference list and its appendix numbers are off. Two read-only checks against the draft and W16 gave first-pass verdicts:
`notes/reviewResponse_2026-10-29.md`; as a page with the reviewer's full text beside each response:
https://claude.ai/artifact/LdBZr2X8KMxShSDnFXhLcP. Main new finding: under the cost the layer-1 tax rises at the chosen
design whichever way θ moves (24–26 of 26), against section 7.3's "more Bismarckian lowers the tax". Several W16 decisions
(A8, A10, A1's intro sentence, W6's marginal loss) are not in the draft. Open: RKB's decisions in the note's last section.

## 2026-10-30 — Technical note: a data part (OECD cross-section)

Fourth part of `writing/main.tex` after the US model, `writing/data/` (`\subimport{data/}{main}`, "Data / The OECD
cross-section"; `data` added to `overleaf.py`'s note include list): inputs and sources (table), the pension tiers mapped
to θ and τ with the slope measure and s (eq:data:*), the variants paper/A/A2pt/B/C with C's rule and the data gaps
(LUX, BEL, ITA, PRT bounds), three figures by `python/paper/figuresDataNote.py` (reads `data/oecd26_theta.csv` only).
Own refsection and bibliography; 19 entries added to `writing/References.bib` (PaG 2013/2021/2025, SOCX, ESSPROS, GPS,
table 29, WPP 2024, OECD earnings, CSES, ILOSTAT, national top-up sources). tabularx breaks under the note's preamble
(even a minimal table): use tabular with p columns. Note builds: 134 pages, data part pp. 127-134, no undefined refs.

## 2026-10-30 — O5: θ re-measured, the pipeline switched to variant C (W23)

Data search for the 26 (PaG 2021 tiers, first-tier and top-up spending, SOCX programmes, ESSPROS, pension funds):
`notes/data_thetaTau*.md`. Three alternatives and the recommendation: `notes/thetaTau_alternatives.md` (page
https://claude.ai/artifact/3qiHJFtYmEXtHpoaZUNnGw). RKB chose C: θ the public-tier slope at 0.5–2 AW times (1 − s), 21
countries (U.S. 0.5445, FRA 0.8219, GBR 0.1812), `data/oecd26_theta.csv`. Test run at ρ = 1: `notes/thetaC_comparison.md`
(page https://claude.ai/artifact/PU9QdCpkCKAxUNRH3ftoxL); λ halves, the UK deep test's ordering breaks, slopes move to the
data. Pipeline on C with RKB's reduced run list (`notes/brief_pipelineThetaC.md`), commit `7694434`. Overnight run started
18:17 (`logs/overnight_2026-10-30/run.sh`, status.log; old results in `logs/results_snapshot_preC_2026-10-30/`). Open: check
the run (UK CRRA brackets the main risk), then the text pass (stale numbers listed in the brief's report), B's results.

## 2026-10-31 — The overnight run on variant C

`logs/overnight_2026-10-30/run.sh`, 18:17–02:29, every solve step OK (status.log); the build failed on NUM_Selection's
missing labels for `results/oecd26_theta_{A,A2pt,B}` (fixed in `tablesOA.SOLVEGROUPS`), rerun: 45 built, 0 skipped, site
and map written. All calibrations converged (bracket-top probes only); UK exact CRRA λ 7.57 (ρ 0.5), 1.45 (ρ 2); U.S. 13.47,
6.25, 1.41. Main outputs reproduce the C test run exactly. `OECD26_ThetaVariants`: A and B as C, A2pt as the paper's index.
Paper 80 pages, checkPaper OK, test_oecd26 12/12, test_onlineAppendix OK. Not done: quarto render of the online appendix;
the text pass (stale numbers, root log 2026-10-30); placing `OECD26_ThetaVariants` and `OECDdata_note`.

## 2026-11-02 — The OECD part on variant C at own turnout (RKB's decisions, W23)

RKB's decisions:
- Section 7 is motivated by O3: without the cost a more Bismarckian design lowers the tax, while figure 1.1's
  spending rises with the index.
- The main specification is θ variant C at each country's own (CSES) turnout: 20 countries, layer 1 at the U.S. ω.
- Design A (predicted against observed θ) is figure 7.3; design E is in the cross-section appendix, now G.
- The measures are C, A and B only. H.5 is dropped; F.3 and the old G moved to the online appendix (B6, C7).

Stylized readings, `results/oecd26_stylized`, read in `logs/variantCompare/summary_2026-11.md`:
- an average ω moves levels only;
- a pooled turnout matches own turnout on the same 20 countries.

New:
- spending at the chosen design in section 7;
- the U.S. tax against a pinned θ (hump, peak 10.5% at θ 0.58);
- C5's numbers and appendix D's U.S. checks rerun at C (`logs/c5rerun`).

Text pass on every stale number (`notes/staleNumbers_2026-11-02.md`), audited after the pass. Note for Martin:
https://claude.ai/artifact/67e2KSAyBbTksTJrZRZcuL. Checks: 80 pages, checkPaper OK, build 51/0, test_oecd26 and
test_onlineAppendix pass. Both projects are pushed to Overleaf, the paper with --force by RKB over Martin's stray online edit
(a typo plus line endings). Nothing committed.

## 2026-11-03 — Appendices B and C cut, shorter exhibit notes

RKB's Overleaf edits pulled (abstract, introduction, B.1 cut to "The design"). B.1's last three subsections rewritten
without the removed auxiliaries (a, x_i, p_i, q_i, κ_t, D(y)), on RKB's D_{t,i}; appendix C in the same register (the
cost is the substitution τ ↦ τf, so A, B and the restated equilibrium equations went; proofs shortened). Exhibit notes:
the guideline "What a note holds" in `notes/paper_styleGuide.md`; per-exhibit cuts and RKB's decisions in
`archive/notes/brief_exhibitNotes.md` (OECD26 notes point to figure 7.2 via `tablesOECD26.specText`; NUM_* details to
appendix D's prose, sourced in REPLICATION.md §5). Paper 75 pages, checkPaper OK, build 51/0, test_oecd26 14/14,
test_onlineAppendix OK. Overleaf pushed.

## 2026-11-03 (evening) — Statutory or exit-age correction of ν: both versions run overnight

RKB: the correction of ν for the retirement-age gap to the U.S. is statutory (`nra`) or effective exit age (`exit`),
to be chosen on full runs of both; the cross-section's main specification becomes own turnout with Luxembourg flat
(`csesFlat`) and layer 1 at the mean ω. Code (uncommitted): `config.US['oecd26']['retAge']` (readers select on it,
stage (ii) passes it, `runOECD26.py`'s default; `'none'`, build byte-identical) and `config.US['retAgeFR']` (France's
own ν, `testEU.load`; `'nra'` = the workbook's appendix-F column bitwise). France's exit version runs in the worktree
`logs/wt_retAgeExit/` (branch `retage-exit-2026-11`); the cross-section's readings in `results/oecd26_retage/`.
The UK added to the exit version (`config.US['retAgeUK']`, `testEU.hostNu`; gap 1.2 years): `runUK.sh` beside
`run.sh` (`logs/retAge_2026-11-03/`), checks in its `summary.md`; plan and next steps `notes/brief_retAgeChoice.md`.

## 2026-11-04 — Statutory ν; appendix G's population and data variants; the pipeline at the new main spec

RKB chose the statutory correction of ν (`nra`) as the main variant (own turnout, Luxembourg flat, layer 1 at the mean
ω); appendix G keeps the uncorrected and exit-age ν and the data variants A, B (renamed "public tier, 23 countries",
"all mandatory tiers", `config.THETANAMES`) at statutory ν; U.S. turnout, pooled turnout and A2pt retired; C6 holds
the variants in full, Luxembourg left out and layer 1 at the U.S. ω. The overnight rows merged into results/oecd26/;
A, B and the U.S.-ω reading run (`logs/variants_2026-11-04/`). Code across config, runOECD26, runShocksUS, datasets,
tablesOECD26 (variant parts ω rule, retAge, measure), figuresOECD26, build, onlineAppendix; tests 14/14, build 59/0,
online appendix OK. Text pass (sections 6, 7.3, appendix G, introduction, conclusion, abstract, C6): the variants
table also reports uncorrected ν without Luxembourg (RKB: Luxembourg alone drives that reading's poor fit, r 0.36
against 0.74 on the 20). Paper 75 pp, checkPaper OK; state in `notes/brief_retAgeChoice.md`. Overleaf pushed; uncommitted.

## 2026-11-04 (later) — Online appendix: page codes without gaps

RKB: the pages B3–B6 and C3–C7 renamed B2–B5 and C2–C6, closing the gaps the retired B2 and C2 left (headings, the
lists of the front and landing pages, link texts, code comments, `notes/TODO.md`, the site README's rule); the page
keys are unchanged, so the paper's `\oa` links stand and only `onlineAppendix.tex`'s codes moved. The front page no
longer names the authors in its opening sentence (they are printed above the title), and neither it nor part C's
landing page still advertises the dropped U.S.-turnout reading. Rebuilt, test_onlineAppendix OK, published.

## 2026-11-04 (evening) — Code and technical-note review (`notes/brief_codeDocReview.md`)

Code: four read-only reviews, then one fix pass per module (module logs of today hold the detail); triage and open
items in `notes/codeReview_triage.md`. No published number moved: writing/Paper identical (PDF dates aside); moved by
intent NUM_Selection's counts, four Source banners, REPLICATION's Reads. RKB retired Medicare/freeTheta, the unwired
ESC stages and 36 orphan results/paper files; the ξ drivers now run at C (`escXi`, `shocksXi` need a rerun);
gridsearch's cubic/pchip mask NaN as linear does (0 NaN nodes in every published ARG surface). Note: three reviews,
three writers on RKB's approval (`notes/docReview_proposals.md`): math slips fixed (labour-supply FOC in both informal
models, two distributional signs), θ from variant C, the reform state, ~16k words of log material cut; 134 -> 107 pp,
compiles clean. Fast suites 31/31. Uncommitted; the note's Overleaf push awaits RKB.

## 2026-11-04 (night) — Review follow-up: the xi rerun, replication trace, the open items

`escXi` run at C (xi 0.2/0.3/0.4; self-check at 0.3 passed; the site's xi blocks filled, NUM_Selection's ESC counts
moved). REPLICATION.md and data/README.md now trace `oecd26Theta.py` (the paper's theta) and its inputs. Fixed the
triage's open items: kappa drops (1+γ_{t,0})/(1+γ_{t+1,0}) (n_t is formal young; code and both informal notes;
bitwise), sizePiR keeps the pi solved at, pinTheta=False removed, sweeps resume only at their settings, drivers
refuse results/ without --theta, InformalSavings' objectiveFrozen anchors at the column's first feasible node (bitwise).
writing/Paper unchanged; what stays open is in `notes/codeReview_triage.md`.

## 2026-11-07 — C.2 derived step by step; layers renamed; a microfoundation of the τ² cost (W24)

RKB's three requests, four agents (briefs archived the same day, `archive/INDEX.md`). C.2 now derives the cost from the
benefit formula to f (the transfer property, the triangle, the share of revenue, both derivatives of ln f), still τ¹;
77 pp, checkPaper OK. "Layer 1" prints as the model and "layer 2" as own ω in every output (paper, appendix G, site);
table 5 without own ω, own ω first at figure 7.3; internal names unchanged; numbers cell by cell as before (python/paper
log). The τ² worktree synced (build 59/0, its `notes/tauPower_k2.md`). Fable's note `notes/tauPower_microfoundation.md`:
τ²(1−θ)² needs the uniform tax component (1−Π/R)τ and a convex extensive response (no one at the margin at a zero
wedge); carrier π(1−π), flat across countries. The coauthor's `quadratic_cost.pdf` (untracked) is the same model; RKB
chose its accounting, the excess burden (elasticity 3.9 at ρ = 1), with the fiscal externality (2.6) in a footnote
(note §10). The test with λ_{n,t} = 2κπ(1−π) runs on the worktree (`notes/brief_convexCarrier.md`).
