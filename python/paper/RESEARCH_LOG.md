# Research log — paper

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_paper.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-09-24 — the pipeline reads the `'size'` cost spec (WP3); `US_ESC_Country`, `US_ESC_ScaleWedge`, WP5

`config.US['esc']`: `spec = 'size'`, `comparisonSpec = 'scale'`, per-(spec, ρ) `bracket` through
`config.escBracket` (set from the LOG λ: [2.88, 43.2] at ρ 0.5, [0.432, 25.9] at ρ 2), `phi` a dummy key.
`datasets.escWedge` reads `fStar`/`f0`/`Vtilde` with the `'scale'` fallback; `escCountry(spec=)`. `tablesUS`:
`US_ESC_Calibration` prints λ, f(θ*), f(0), Ṽ; new `escCountryTable` (`US_ESC_Country`, in place of
`UK_ESC_Calibration`, now deleted) and `escScaleWedge` (D2); 46 outputs. Stage (i) calibrates both specs under
LOG and the paper's under CRRA, one command per ρ with its bracket, φ-robustness only for a spec whose f reads
φ; stage (ii)'s LOG entries run `--spec size scale`. WP5 rewrote `sec:esc`, the intro, abstract, conclusion,
`app:US:ukESC` (the cross-country test) and `app:US:escTables` (the previous wedge's paragraph);
`notes/paper_styleGuide.md` gained the cost vocabulary. Rebuilt with `'size'` rows at ρ ∈ {0.5, 1, 2}
(`logs/escSizeLog0924.log`, `escSizeCrra0924.log`); the stationary footnote's ESC numbers are 0.053 (LOG) and 0.059 (CRRA), from 0.005 and 0.016.

## 2026-09-22 — the UK arm, the leisure row back, and eight tables moved to appendix E

`config.US['ukHost']`, `usShockCsv`, `usHasSheets`; `datasets.usShocks(host=)`; `tablesUS._otherShocks`
(host-generic, leisure row printed again), `ukOtherShocks`, `ukCrraOtherShocks`, `frukHouseholdHeterogeneity`;
six registrations in `build.py`; stage (i) skips a regrouping without sheets and the summary tolerates a
missing sweep; stage (ii) entries `shocksUK`/`shocksUKCommonX` carry a `requires` guard. In the draft:
`US_OtherShocks`, `US_CRRA_PensChars` and the four `US_ESC_*` tables are `\input` from appendix E
(`app:US:french`, `app:US:CRRA`, `app:US:escTables`), the UK twins from `app:US:vectorX`. After France's
hours correction every France-dependent output was rebuilt (stage (ii) main with `--force`, then the exact
CRRA ESC leg): only the hours unit moves, so the leisure and all-characteristics workweeks and France's own
row change (35.44 → 35.24), the vector-X income row by 0.03 p.p., and no design or tax. Prose refreshed:
the U.S. leisure sentence (5.0 hours), the UK paragraph and its footnote on the voting approximation.

## 2026-09-15 — the tables and figures stop announcing themselves

A presentation pass on RKB's list, all at source. `config.variantNote` is empty under common X and keyed
on `commonX` rather than on which variant leads, so 16 headline tables dropped the "Common-$X$
calibration" sentence. `tables.notesBlock` sets a single note as a flush-left paragraph; the list form
survives only for `US_Ageing`, whose a/b markers are keyed to cells. `ArgentinaUniversal` prints savings
as levels. `USUKFRCalibration` was rebuilt twice, ending as parameter, three values between hairline
rules, then the identifying phrase — `\addlinespace` had to go, a per-row `\vrule` breaking at the gap.
The US figures were drawn 10.6in wide into a 5.91in measure, so 9pt type arrived at 5pt: both are
narrower with larger type, and their baseline note moved to a `\tablenotes` citing the table that holds
the levels. `tablesUS.ESCANCHOR` — table 10 carries the shared ESC note, 11–13 point at it; the ESC
tables take `_xwrap(width=\textwidth)`.

## 2026-09-12 (night) — stationary vs date-specific policies: the check behind sec:numerical's literature paragraph

RKB's claim: the numerical literature computes stationary policy functions and applies them to non-stationary
settings, a steady-state approximation, whereas we compute the date-specific sequence. Checked against the
cited papers (`pdfs/`, gitignored): Song (2011) and Forni (2005) are stationary environments solved by
Chebyshev projection; Gonzalez-Eiras–Niepelt (2008) is exact along the transition under log; none runs a
transition through a stationary function. The opening paragraph of `Sections/Numerical.tex` now states the
claim about the object (stationary function = right object only in a stationary environment; along a
transition it holds the continuation at its stationary form; empty under log without informal savers) and
a footnote quotes what the approximation costs in our models, measured by three new scripts (US taxes,
Argentina, endogenous θ; `results/numerical/`, module logs). Pipeline: `runShocksUS.py --prepub` gained
`stationary`/`stationaryESC`; `runShocks.py` gained a `--prepub` part (`stationary`, headline variant only,
`headline: True`); `config.NUMDIR`, `config.US['ρStationary']`. The horizon footnote was corrected (four
constant periods after the last projection, not five). Open: TODO W5.

## 2026-09-12 (evening) — paper prose: the identification argument stated once, W4 reworded

Three prose passes on RKB's instruction, no pipeline change. (i) `sec:oecd` now cites section 5's
identification paragraph instead of repeating it, keeping only what is specific to its arm -- that the
French income-distribution counterfactual (and the composite containing it) is defined through eta and X
separately, which is why every table is repeated under the vector-X variant. It had also still named the
French leisure row, not printed since 2026-09-11. (ii) W4: the voting paragraph keeps its mechanism
sentence but drops "it is the latter that scales with rho", which explained the rho-profile of the
*response* with an argument that points the wrong way; it now says the profile follows from the
calibration, the wedge costing about 1.3% of raised funds at rho = 2 against roughly 12% at rho = 0.5
(`US_ESC_Calibration`), so the interior choice sits on a thin cushion at high rho. (iii) W1's
introduction sentence follows, naming income and political participation as the two dimensions pulling
against each other; it keeps its `%% TODO-W1` tag.

Provenance, established from the Overleaf clone's history and recorded in `notes/TODO.md`: the W1
sentence fills a placeholder MGE left in his 2026-09-10 online edit (the same edit that widened the
sample to the 29 pre-2000 OECD members); W4's paragraph is drafted text throughout, self-flagged, and
MGE's edit left it byte-identical. Open: W1 and W2b.

## 2026-09-12 — Argentina leads with common X (W2); vector-X outputs rebuilt after C4

`config.ARG['commonX'] = True`, so both arms now print the common-X calibration. Argentina's ten outputs
rebuilt: the headline `ArgentinaCalibration` is X = 1.94 against the 42.5-hour formal workweek with
eta_i = [0.64, 0.90, 1.14, 1.87], eta_0 = 0.344, X_0 = 0.804, and relative formal hours as a prediction;
the `_vectorX` twin is the old table. No counterfactual number moves (R2 measured <= 4e-12), so
`ArgentinaUniversal`, `Argentina_funcOfRho` and the two figures are byte-identical to the vector-X ones.
Paper text: the identification paragraph of `Sections/Argentina.tex` rewritten with a footnote naming the
alternative, and a new appendix subsection `app:EPH:vectorX` in `HouseholdSurveyArg.tex` carrying the
twin table.

C4's rebuild (`python/US/RESEARCH_LOG.md`, same date): every US counterfactual table is unchanged --
headline and vector-X alike, including the French income row -- because the shocked models rescale with
the baseline and the workweek is reported as a ratio. What moved is exactly the three tables that print
eta_i/X_i/X-bar: the vector-X X-bar ratios lose the hours-unit artefact (UK/US 1.716 -> 1.773, FR/US
1.514 -> 1.519) and the vector-X X_i now sit on an O(1) scale, which is why `tablesUS` prints X and X_i
to two decimals instead of one. Only France's own-path rows move numerically, in levels alone
(h by 5.1e-4, tau to 1e-8), since its lambda carries the target.

## 2026-09-11 — Argentina rebuilt after the informal-target fix

Stages (i)–(iii) re-run for Argentina (`InformalSavings` log, same date, for the fix). `anchorGuess`
retuned; `ArgentinaCalibration` prints `η_i`/`X_i` to two decimals (the rescaled `X_i` are 0.74–1.24).
Only the five Argentina outputs were copied into `writing/Paper` (`build.py --only`): a US ESC run was in
flight. Prose updated to the new numbers in `Argentina.tex`, and the headline "a third" became "almost
half" in the abstract, introduction and conclusion. This is the vector-X Argentina; TODO W2 still decides
it against common X.

## 2026-09-11 — US pipeline split into a main and a pre-publication part; exact CRRA ESC leg

`runShocksUS.py` / `runCalibrationUS.py` entries carry `part` (main | prepub | both); `--prepub`, `--all`.
Main: exogenous shocks, LOG ESC leg (+ new `escPath`, `escCountry` entries). Prepub: exact CRRA wedge
(`runESCcrra.py --exact`, ~45 min per ρ), φ = 0.25/0.75 wedge runs, the R3 timing checks, the exact CRRA
path+shocks (~5 min per chosen reading). `config.US['esc']`: `exact` = True, `ns2D`, `nsScan`, `nCand2D` = 41,
`ρPermanentCRRA`; `datasets.escMethod` filters CRRA rows by method, never falling back. The merge entry now
always runs (a stale-but-present `escExperiments.csv` blocked the first build). Full run 13:36–16:53
(`logs/runUsPipeline0911.ps1`; its log froze, finding #14): income row workweek 41.97 → 40.36 at ρ = 1 with
τ/s/Y unchanged, LOG ESC rows unchanged except French workweeks, CRRA ESC rows now exact (acute 0.821,
voting 0.259, both 0.494 at ρ = 2). US outputs copied; `sec:esc` prose updated (W2, W3), W1 drafted.

## 2026-09-11 (evening) — Argentina variant twins (C3), R2 launched

`config.ARG['commonX']` (False: vector X stays the headline), `argSweepCsv/argInstanceDir/argShockTemplate/
argEpsThetaCsv`, `variantSuffix/Caption/Note(commonX, arm)`. `runCalibration.py --commonX` sweeps the second
variant and the summary carries one row per variant (`commonX` column); `runShocks.py --commonX` runs every
experiment per variant through the scripts' `--pkldir/--out/--csv/--baseCsv`. Loaders and the five Argentina
builders take `commonX`; `build._variants(..., arm='ARG')` registers the `_commonX` twins. R2 ran detached
(`logs/runArgCommonX0911.ps1`, 1.8 h, every stage exit 0, 39 outputs, 22 fast suites): every common-X shock
csv and the ε×θ grid equal the vector-X ones to ≤ 4e-12, so W2's decision is about the calibration table and
its description, not the numbers. The `runShocks.py` docstring's 2.5 h estimate for `universal` is stale (13 min).
Comparison and recommendation (common X for the main text): `notes/argentina_commonX_vs_vectorX.md`.
