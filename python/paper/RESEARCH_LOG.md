# Research log — paper

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_paper.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

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
