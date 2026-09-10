# TODO — the paper rewrite (opened 2026-09-08)

The plan agreed with RKB on 2026-09-08, and where each piece stands. Four items: (1) Argentina at
α = 0.35, (2) one savings-rate convention reported as changes, (3) the two overview figures, (4) the main
text rebuilt as four sections. Fresh sessions own the writing; this note is their entry point, and
`notes/paper_styleGuide.md` (2026-09-08) is the register and conventions every new paragraph follows.

## Done this session

- **(1) launched.** Workbook `Capital income share` = 0.35 (set through Excel, see trap below). The chain
  `runCalibration.py --force` → `runShocks.py --force` runs detached, then a watcher runs
  `runTests.py --all` and `build.py --no-copy`. Progress in `logs/argPipeline.log` (one line per stage
  with exit code), detail in `logs/argCalibration.log`, `argShocks.log`, `argTests.log`, `argBuild.log`.
  Two code changes were needed to make it run: the derived CRRA steady-state bracket in both Argentina
  modules, and `--x0`/`config.ARG['anchorGuess']` (`crossCuttingFindings.md` #7).
- **(2) done for stage (iii).** Every table prints savings over GDP; counterfactual rows are changes
  against that ρ's own baseline, with the level in the baseline row and the note saying so. The US
  numbers are rebuilt in `results/paper/Tables`; the Argentina builders are verified on the old csvs and
  will produce the new numbers once (1) lands. The US/UK/FR tables and US figures were copied into
  `writing/Paper` by hand later the same day (OECD session); the Argentina ones arrive with the build.
  `Argentina_funcOfRho` was reformatted again on RKB's request: one shared pre-reform row, savings `--`,
  header "Change in savings rate" (`python/paper/RESEARCH_LOG.md`).
- **(3) done.** `US_overview` (and `_vectorX`) without the all-three and France rows, savings panel in
  s/Y. `US_ESC_overview` is now a dumbbell chart (open = θ pinned, filled = θ chosen, per scenario and
  ρ). Two alternatives were drawn and not adopted: a single-panel "chosen θ against ρ" line chart (a
  strong companion figure if wanted, ~20 lines in `figuresUS.py`) and a 5×3 small-multiples grid.
- **(4) restructured, not rewritten.** `Sections/Quant.tex` is gone; `main.tex` inputs
  `Numerical`, `Argentina`, `OECD`, `EndogenousTheta` in that order. The ESC appendix moved into the main
  text as `sec:esc`; the empty numerical appendix was dropped and every `app:numeric` reference points at
  `sec:numerical`. Introduction: roadmap paragraph rewritten, the "to be endogenous" placeholder replaced
  with a paragraph describing the deadweight-cost mechanism and the results. Conclusion: a closing
  paragraph on endogenous design. Contradictions with the tables fixed in the OECD section (savings
  magnitudes now in p.p. of GDP; the red "we do not endogenize" paragraph now forwards to `sec:esc`).

## Resolved 2026-09-08: the tax target is α-dependent, and is now derived

The paper's tax target comes from pension spending of 7.1% of GDP, and spending over formal output is
τ(1−α), so τ₀ = 0.071/(1−α): 12.46% at α = 0.43 (the old literal 0.125), 10.92% at α = 0.35. The first
α = 0.35 run calibrated ω to the stale 0.125 and was killed at ρ = 1.5. **The workbook now carries
`Pension spending` = 0.071 instead of `Pension tax`, and both Argentina loaders (`test.py` in
`InformalSavings` and `informalAnalytical`) and `config.calendar()` derive τ₀ from it and the capital
share** (finding #9: a datum the model also derives is derived, not typed). Effect on the ρ = 1
calibration at α = 0.35: β 0.686 → 0.651, ω 1.616 → 1.527, η0/X0 and the savings rate essentially
unchanged, R unchanged (it is α/(K/Y)). Lower τ raises disposable income and shrinks the PAYG crowd-out,
so less patience sustains the same K/Y. `config.ARG['anchorGuess']` is the new row. Relaunched 2026-09-08
~11:30. Every "% of GDP" conversion in the Argentina prose uses the factor 0.65 from now on.

Also noticed: the workbook's `Savings rate` cell reads 0.165 where it read 0.184 this morning — changed
by someone else this day. It is reported, not targeted (`db['s0']`), so nothing solved depends on it, but
whoever changed it should say why in the log.

## Landed 2026-09-08 19:10: the corrected Argentina pass

Calibration 16/16 (0 failed, residuals ≤ 1.4e-11, `verifyResidual` 1.0e-3 at ρ = 0.5 as before), shocks
exit 0, `build.py` run WITH the copy at 19:10 — `writing/Paper` now carries the α = 0.35, τ₀ = 0.109
Argentina tables and both figures (the draft copies had been the α = 0.43 vintage). Headline at ρ = 1:
β = 0.651, ω = 1.527, ε = 0.290, θ = 0.839; the reform raises τ 10.92% → 11.91% (+0.99 p.p., i.e.
0.99 × 0.65 = 0.64% of GDP, about a third of the observed 1.9%), savings −0.20 p.p. of GDP, workweek
−0.12 h; EE-only savings +0.18 p.p. Across ρ: +0.13 p.p. of tax at ρ = 0.5 (savings 0.00), +0.96 at
ρ = 2 (savings −0.14). β crosses one between ρ = 0.6 and 0.7 (0.903 / 1.082), as
$\beta(\rho) = (B R^{1-\rho})^{1/\rho}$ predicts; the sweep is `results/calibration/informalSavings_rhoGrid.csv`.

## Open, in order

1. ~~**Tests.**~~ Done 2026-09-08 20:30: `runTests.py --all` 25/26 with the expected anchor failure;
   anchor re-pinned to β = 0.651367, ω = 1.526699 and the grid suite re-run alone, pass. All 26 suites
   pass under α = 0.35, τ₀ = 0.109. (The 8604 s wall time was CPU contention from outside the repo, not a
   defect — `python/InformalSavings/RESEARCH_LOG.md`.)
2. ~~**Argentina section session.**~~ Done 2026-09-08 19:30: every `TODO-ARG035` marker resolved against
   the rebuilt tables (abstract, introduction, `Sections/Argentina.tex`, conclusion). The tax target is
   now stated as $0.071/(1-\alpha) = 0.109$ in the calibration prose; the reform paragraph reads
   1.0 p.p. / 0.6% of GDP / about a third of the 1.9% / savings −0.2 p.p. of GDP / hours −0.1 /
   informal savings −13%, plus the long-run 1.7 p.p. by 2040 with its mechanism (newly covered
   households retire with less private savings). The four-in-one figure paragraph now says its 1.6 p.p.
   move is the always-had-it comparison, close to the long-run effect and not the impact one. The CRRA
   paragraph quotes the ρ = 0.5 dampening (0.1 p.p., savings 0.00) and the flat 1.0 / 1.7 p.p. and
   0.2 → 0.1 p.p. savings over ρ ∈ [1, 2]. The "higher labor supply" sentence in the reform paragraph
   was wrong in both vintages (hours fall in both rows) and now reads lower, with the EE-only mechanism.
   `num_calibration.tex` no longer quotes η0/X0 (checked). Two checks on Frankema (2010) remain for RKB:
   whether the series imputes labour income to the self-employed, and what it does after 2000.
3. ~~**Numerical-methods session.**~~ Done 2026-09-08: `Sections/Numerical.tex` written as a compact
   section (six run-in headings, two displayed equations, the generic nested-fixed-point calibration and
   the ρ march; targets stay in the application sections). Agreed with RKB: no methodological
   contribution is claimed; the endogenous-θ solution stays in `sec:esc` with one forwarding sentence
   here. Literature sentence corrected the same day after RKB's check: the numerical PEE literature
   computes a *stationary* policy function as a fixed point (Krusell--Ríos-Rull 1999 by LQ approximation,
   Song 2011 by Chebyshev projection for CRRA; Gonzalez-Eiras--Niepelt 2008 closed form, CRRA only
   footnoted), not backward induction on a grid. The section now says we compute a sequence of
   date-specific policy functions by backward induction, that this is the finite-horizon-limit
   equilibrium in which GN 2008 prove uniqueness, that the terminal condition selects it where a
   stationary fixed point can be multiple (Forni 2005), and that the demographic transition enters
   directly. Framed as a difference, not a contribution. `KrusellRR99a1` added to `References.bib`.
   One loose end: the introduction's `\parencite{...}{e.g.}` is invalid biblatex syntax (see
   `notes/paper_styleGuide.md` §5).
4. ~~**OECD session.**~~ Done 2026-09-08. The rebuilt US/FR/UK tables and the three US figures were
   copied from `results/paper` into `writing/Paper` (the draft copies still had savings as levels over
   labour income); every number in `Sections/OECD.tex` was re-read against them. Changes: the CRRA
   robustness now sits under its own `\smalltitle` and precedes a closing `Interpretation` block (stylised
   model, hours gap, the OECD cross-section and the hand-off to `sec:esc`); the duplicated IES paragraph
   is a cross-reference to the Argentina section; a sentence in the savings convention was added before
   the first counterfactual; "order of magnitude smaller" for inequality vs ageing softened to "several
   times" (the ratio is 3–7 depending on the ageing scenario); dashes and meta-commentary removed; two
   typos. `Appendix/USauxiliary.tex`: the vector-X paragraph said France's income distribution was a
   *smaller* change under vector X while quoting a *larger* tax effect; fixed to "larger".
   **Still open for the introduction pass:** three `XXX` markers in the Conde-Ruiz paragraph; the claim
   that leisure preferences "fully explain the observed differences labor supply" should read that they
   somewhat overshoot the gap (section text: 6.2 hours against an observed 4).
   **Endogenous-θ session** remains: mostly rearrangement and register; the ESC tables were also
   refreshed by the copy above.
5. ~~**Docs that still describe the old world.**~~ Checked 2026-09-08: the US technical notes already
   define the savings rate over GDP (`model_competitiveequilibrium.tex`) and `num_esc.tex` does not
   state a unit. Nothing to change.

## Traps met this session

- **openpyxl drops cached formula values on save.** The Argentina workbook has formulas (`=0.678/0.803`
  for the replacement rate, three population cells); after an openpyxl round trip pandas reads them as
  NaN, so θ, ε and ν were NaN and every steady state failed. Edit workbooks through Excel (COM from
  PowerShell works) or write literal values.
- **`PYTHONUTF8=1` for every pipeline run.** The scripts print `ι`; under the cp1252 console they crash
  on the first print.
- **PowerShell `*>` redirection writes UTF-16.** Route python output through `cmd /c "... > log 2>&1"`.

## Open, added 2026-09-10

Two larger items agreed with RKB, both for the final version of the paper rather than the next build.

6. **Argentina with common X.** The OECD arm leads with the common-X calibration (one leisure parameter
   across income groups, its level pinned by the observed workweek, relative hours a prediction); the
   Argentina arm is still vector-X only. Solve the Argentina model under common X as well, so the two
   arms rest on the same calibration convention. This touches `python/InformalSavings` (the calibration
   loader, `calibrateRhoGrid.py`), `python/paper/runCalibration.py`/`config.ARG`, and the Argentina
   builders, which would gain the same `commonX` variant switch as the US ones (`config.variantSuffix`).
   Not started; budget a full recalibration of the rho grid (~3 h) plus the shocks (~1 h).

7. **Re-run the CRRA ESC leg with the exact solver.** The CRRA tables (rho = 0.5, 2) come from the path
   iteration, certified against the exact two-dimensional recursion (`LeadedCRRA2D`) to +-0.01 in the
   design. For the final version, run the wedge calibration and the chosen-design readings through
   `solveLeaded2D` instead, so the paragraph in `sec:esc` can say the tables are the exact solution and
   drop the path-iteration caveat. Timings (2026-09-10 assessment): ~12 min per 2-D solve at ns = 150,
   ~3x faster at ns = 50 (the s-grid is immaterial, the 13-node theta-state grid is not); with the scan
   for p narrowed to half..double the known p (0.965 / 0.090), about 8 solves per rho for the calibration
   and one per chosen reading. **Make it opt-in, not part of the default pipeline**: a `--exact` switch
   on `python/US/runESCcrra.py` routing the calibration residual and the shocks stage through the 2-D
   solver, a `method` column in `escCalibrationCRRA.csv`/`escExperiments.csv` so the two vintages cannot
   be confused, and `config.US['esc']['exact']` (default False) telling `runCalibrationUS.py`/
   `runShocksUS.py` which vintage stage (iii) should read. Nothing about the LOG point changes.
   The driver has no 2-D branch today (`runESCcrra.py` never references `ESCC2`), so this is half a day of
   code plus 1.5-5 h of compute depending on the grid.

Smaller loose ends from the 2026-09-10 session:

- Introduction: `XXX FILL IN HERE` in the OECD-sample sentence; the leisure-preferences claim should say
  "somewhat overshoots" the hours gap (6.2 hours against 4).
- Two checks on Frankema (2010) remain RKB's (see item 2 above).
- `notes/todo_escPermanentTiming.md`: `PermanentCRRA` has never been executed. Only matters if the
  permanent-timing sentence in `sec:esc` is to be backed under CRRA.
- The composite French shocks (income + voting, all three): RKB is inclined to cut them from the ESC leg
  but the section's closing paragraphs rest on income + voting; decision deferred.
