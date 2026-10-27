# Plan: the paper by object (sections 6 and 7, the OECD exercises)

Written 2026-10-27 after RKB's decisions of the same day. TODO items C14, R6, R7, W18–W21; the plan's verification
gate is V. On branch `review-2026-10` (RKB, 2026-10-27: no new branch; the Overleaf state of 2026-10-26 is `aa89dc9`).
Phase 1 started 2026-10-27.

## What was decided (RKB, 2026-10-27)

1. **The purpose.** One political process generates both the size and the design of the pension system; the test is
   their joint relation to ageing and inequality across the OECD (figure 1). Argentina is the $\epsilon$ dimension,
   a separate application with no counterpart in figure 1.
2. **By object.** Section 6 is the laboratory with the design given: the U.S. calibrated, the counterfactuals, the
   IES, and it ends with the 26-country test of *spending* at the observed designs. Section 7 is the laboratory with
   the design chosen, then the deep test on the UK and France, then the 26-country test of the *design*.
3. **The UK and France are donor data plus the deep test.** France supplies the income distribution, the voting
   profile and the taste for leisure that the U.S. counterfactuals impose; the two ageing scenarios bracket the UK's
   and France's demography. Both are calibrated only where the deep test needs them (section 7.3: the U.S. cost on
   their own calibrations, the UK's own cost, France's corner). The three-country comparison, the $\omega$ ordering
   as a result, and the UK as host (online appendix B2/C2) go.
4. **The cross-section's maintained assumptions.** The parameter transported across countries is $\epsilon$, not
   $\lambda$: $\lambda_i = \epsilon\,\Pi_{i,t}/R_{i,t}$ (the `sizePiR` cost of `python/US/modelESC.py`), since
   holding $\lambda$ fixed ties a held parameter to the regressor. $\beta$ stays common as the main case, with the
   opposite extreme reported: each country's $\beta$ set so that its 2020 return equals the U.S. one (`commonR`).
   The spending test of section 6 runs without the cost ($\lambda = 0$) at the observed designs. Turnout stays
   U.S.-for-all by default; the own-turnout variant is run beside it and decided at checkpoint 1 or later.
5. **Not reopened.** Section 7.1's cost and 7.2's U.S. laboratory stay under the paper's `size` cost: $\lambda$
   calibrated on one country absorbs $\Pi/R$, and nothing is transported there. No CRRA rerun.

## Principles

1. Numbers reach the paper through `python/paper` only; no generated `.tex` is edited; a number in prose is read
   off the cell it stands next to (style guide §3).
2. No writing before checkpoint 1: the runs decide what the paper can claim (the main specification, the inequality
   verdict, "a quarter of the distance").
3. **Overleaf first.** RKB is reviewing on Overleaf. Before phase 3 the main session pulls Overleaf
   (`writing/overleaf.py`) and the writers start from the pulled state; nothing is pushed until V passes.
4. Disjoint file sets per writer; a fix needed in another package's file is reported, not made. Only W19 edits
   `main.tex`, only W20 `References.bib`.
5. Retire, do not delete: csvs that nothing reads go to `archive/results/` with a line in `archive/INDEX.md`;
   retired `\oa` keys are aliased (style guide, the `\oa{key}` rule).
6. Every agent reports in at most 25 lines; the main session reads each diff and reruns the named tests before the
   next package starts. One module-log entry per package, at most ten lines.
7. Interpreter `.venv\Scripts\python.exe` with `PYTHONUTF8=1`; long runs in the background to `logs/<package>/`;
   finding #13 (`--force` after any recalibration), #14 (never tail an appended log).

## Phases and checkpoints

| Phase | Packages | Gate |
|---|---|---|
| 1 code | C14 (model-coder) | diff read; fast suites and `test_oecd26` (US and paper) rerun by the main session |
| 2 runs | R6 (paper-compute), then R7 (paper-compute, separable) | **Checkpoint 1** (RKB): the ledger `notes/ledger_R6.md` decides the defaults below |
| 3 writing | W18, W19 (paper-writer-lead), W20 (paper-writer), W21 (paper-compute), in parallel on disjoint files | each diff read; `checkPaper.py`; a full latexmk in `logs/W/build` |
| 4 verification | V (paper-reviewer, paper-reviewer-lead), follow-ups by W18–W20 | `runTests.py --all`; commit; Overleaf push of both projects; the online appendix published; logs; this plan and the ledger archived |

**Checkpoint 1 decides** (defaults in parentheses): the cross-section's main specification (`sizePiR`, $\beta$
common, U.S. turnout); whether the deep test is reported under the same transport as the cross-section (yes, with
the `size` rows as the comparison); whether `OECD26_Layer1` moves into the main text (yes); what the abstract and
the conclusion say about inequality (written from the ledger); whether R7 runs (yes).

**Checkpoint 1, decided (RKB, 2026-10-27, "agreed as suggested").** (1) The cross-section's main variant is `sizePiR`,
$eta$ common, U.S. turnout; the inequality result is stated as conditional on the turnout profile (index on the Gini
negative and significant at the U.S. profile in layer 1 under every cost and $eta$ rule, $-0.67$ to $-0.78$; zero at own
turnout in layer 1, positive and insignificant in layer 2), with appendix H's `OECD26_Robustness` carrying own turnout.
(2) The deep test is reported under both transports in one table (`US_ESC_Country`); the text reads "a third of the
UK's distance and little of France's" under $\epsilon$ (0.33, 0.06), with the $\lambda$ shares (0.23, 0.25) beside.
(3) `OECD26_Layer1` moves into the main text (7.4). (4) R7 runs. The ledger is `notes/ledger_R6.md`.

**Overleaf pulled 2026-10-27 before phase 3** (`overleaf.py pull paper`): RKB's online edits to `abstract.tex` (the
informal-retirees qualifier cut; the closing sentences rewritten, one left unfinished, "the effect of income inequality
on the depends on"; the 26-country sentence commented out) and `Sections/Introduction.tex` (the figure-1 paragraph
rewritten without the Conde-Ruiz sentence; the figure note's pointer to the cross-section cut) are the writers' base.
Generated tables were protected and the pipeline's figures kept. Nothing is pushed until V.

## C14. The cross-section driver's variants (model-coder, Opus xhigh)

**Problem.** `python/US/runOECD26.py` runs one cost (`SPEC = 'size'`, a module constant) with $\beta$ imposed
everywhere, and `python/US/runESC.py --stage country` (the deep test) is not $\pi$-consistent under `sizePiR`. The
cross-section needs three variants beside the paper's rows, all under log preferences, and the on-disk `size` rows
must survive untouched (their keys already carry `spec`).

**Files.** `python/US/runOECD26.py`, `python/US/oecd26.py`, `python/US/runESC.py` (`stageCountry`, `wedgeReadout`),
`python/paper/datasets.py` (`_oecd26Rows`, `oecd26Anchor`, `oecd26Layer`, `escCountry`), `python/paper/config.py`
(a new `US['oecd26']`), `python/paper/runShocksUS.py` (entry `oecd26`), `python/US/test_oecd26.py`,
`python/paper/test_oecd26.py`, `python/US/README.md` (file table and invariants), `python/US/RESEARCH_LOG.md`.

**Changes.**
1. `--spec size|sizePiR|none` (default from config). `SPEC`/`PHI` become per-run values; `settings()` takes the
   bracket from `WEDGE_BRACKET[spec]`, none for `none`. Under `none` the anchor calibrates $\omega$ to $\tau_0$ and
   skips `calibrateWedge` and the design readouts (`p`, `θChosen`, `θInForce`, `fStar`, `f0` NaN; `status` 'ok'):
   a costless design choice is the corner of proposition 4 and would mislead. Under `sizePiR` the anchor calibrates
   $\lambda$ as now (`calibrateWedge(spec = 'sizePiR')`, which runs through the $\pi$-iterating solvers).
2. **$\pi$-consistent readouts under `sizePiR`.** `readouts` takes `τ2020`, `spending2020`, `R2020` from the pinned
   solve (`solvePEE_LOG`, its own fixed point in $\pi$) and the free-path readouts (`θInForce`, `θChosen`,
   `τInForce`) from the leaded solve's fixed point; the order of the calls must not let one solve's $\pi$ serve the
   other. `τPinGap` stays as the diagnostic. New columns: `ΠR2020` ($\pi_{2020}$ on the pinned path) and
   `λEff2020 = p · ΠR2020`, the cost the country effectively faces (the ledger's object). `stageCountry` in
   `runESC.py` gets the same treatment (`leadedDesignAtT0` through its fixed point, not a bare `ESC.solveBackward`),
   its rows carry `ΠR` as `wedgeReadout` already does, and the docstring's "calib, path and shocks" sentence names
   `country` too.
3. `--betaRule common|commonR` (default `common`). `commonR`: layer 1 calibrates $\beta_i$ alone against
   $R_{i,2020} = $ the anchor's `R2020` (one-parameter root, $\omega$ the anchor's); layer 2 calibrates
   $(\beta_i, \omega_i)$ against $(R_{\mathrm{US}}, \tau_{0,i})$ through `ModelUS`'s two-parameter calibration
   (`_calPars = ('β', 'ω')`, both written through `adjPar`). A flag on `ModelOECD` (`betaRule`) switches
   `_calPars`, `_calSetPars` and `_calResidual`; `build` takes it. The anchor is always `common`. Under
   `sizePiR` the existing `ModelESC.calibrate` wraps the root in the $\pi$ iteration whatever `_calPars` is.
4. **Keys.** `betaRule` joins `KEYANCHOR` and `KEYLAYER` and `inputsKey`; `anchorKey`/`inputsKey` include the
   spec's bracket as now. Rows on disk without the column are read as `common` by a one-off migration in
   `mergeWrite`'s caller, so the paper's `size` rows are reused, not recomputed; the self-check of R6 confirms a
   forced recompute reproduces one of them.
5. **Readers.** `datasets._oecd26Rows(layer, turnout, spec, betaRule)` filters on `C.US['oecd26']` by default;
   `oecd26Anchor` tolerates a `none` anchor without `p`; `oecd26Layer` keeps the staleness checks (#13).
   `datasets.escCountry(spec)` finds the `sizePiR` rows where the tagged csvs of `config.US['esc']['costVariants']`
   put them. `config.US['oecd26'] = {'spec': 'sizePiR', 'betaRule': 'common', 'turnout': 'cps', 'reading':
   'inForce', 'spendingSpec': 'none', 'variants': [...]}` is the one place the paper's variant lives;
   `tablesOECD26.PAPER` reads it. The stage (ii) entry `oecd26` runs every variant of the list (cheap when rows
   are current).
6. **Builder plumbing** (the new exhibits are R6's): `tablesOECD26` and `figuresOECD26` take `spec` and `betaRule`
   beside `turnout`, `sample`, `reading`; `PAPER` comes from `config.US['oecd26']`; `suffix` and `variantCaption`
   extend to the two new dimensions (`_size`, `_commonR`); `build.py`'s registrations of the existing `OECD26_*`
   outputs are unchanged in name and read the paper's variant.

**Checks that must pass.**
- `python/US/test_oecd26.py`, coarse grid, one country each: under `none`, $\tau_{2020}$ at a country with
  $\theta_c = 1$ (FRA, AUT) equals `closedFormTax` to 1e-8 (eq (1.4) holds at $\theta = 1$ under any cost or none);
  under `commonR`, layer 1's `R2020` equals the anchor's to 1e-8 and layer 2's two residuals vanish; under
  `sizePiR`, the row's `ΠRgap` is below `ΠR_TOL` and `λEff2020 = p · ΠR2020`; a forced recompute of GBR under
  `size`/`common`/`cps` reproduces the on-disk row's `τ2020` and `θInForce` to 1e-10 (the migration).
- `python/paper/test_oecd26.py`: synthetic csvs holding both specs and both $\beta$ rules; the readers select the
  configured variant and never mix; `OECD26_Slopes` at a non-default variant carries the variant in its suffix.
- `python/runTests.py` fast suites; `test_oecd26Anchor.py` (slow): the `size` anchor's $\lambda$ unchanged at the
  2026-10-03 inputs.

**Report.** The diff by file; the test counts; the wall time of one `sizePiR` layer row and one `commonR` row on
the fine grid (R6's budget); the README lines and the log entry.

## R6. The runs, the builders and the ledger (paper-compute, Opus xhigh)

**Self-check first.** (i) A forced recompute of GBR, layer 1, `size`/`common`/`cps`, reproduces `results/oecd26/
layer1.csv`'s row to 1e-10 in `τ2020` and `θInForce` (C14's test M does this; its reference: `τ2020`
0.1323514088148834, `θInForce` 0.8365989778825912). (ii) `results/esc/escCalibrationCosts.csv`'s LOG `sizePiR` row
is at the current U.S. calibration: checked 2026-10-27, $\theta^*$ 0.727757, $\beta$ 0.654670, $\omega$ 1.279637,
$\lambda_{\mathrm{sizePiR}}$ 20.444896 at $\Pi/R$ 0.554912 (so $\lambda\,\Pi/R$ = 11.35, the paper's $\lambda$); no
rerun needed. C14's timings on the fine grid (GBR): a `sizePiR` row 43–48 s, a `commonR` row 9 s; the `sizePiR` +
`commonR` cell is unmeasured. Until the configured spec's rows exist, `build.py` reports the three registered
`OECD26_*` outputs as `MissingInput`: expected before run a.

**Runs** (background, `logs/R6/`, budget 12 h wall time; measure the first country of each and extrapolate before
launching the rest):
- a. `runOECD26.py --spec sizePiR --stage anchor layer1 layer2 --turnout cps cses`
- b. `runOECD26.py --spec none --stage anchor layer1 --turnout cps cses` (layer 2 only if time allows: the no-cost
  $\omega$'s)
- c. `runOECD26.py --spec size --betaRule commonR --stage layer1 layer2 --turnout cps cses`
- d. `runOECD26.py --spec sizePiR --betaRule commonR --stage layer1 layer2 --turnout cps` (then `cses`)
- e. `runESC.py --stage country --spec sizePiR --phi 0.5 --commonX --tag Costs` (the deep test under $\epsilon$:
  the U.S. parameter on the UK and France at their own calibrations, the UK's own parameter). `escCornerSlope`
  needs no rerun: at $\theta = 1$ the cost vanishes under every proportional spec.
- Every run: `nEqMax = 1`, `nFallback = 0` on every row, or the row is reported.
- The variants merge into the same three csvs (`mergeWrite`), so runs a–d go one after another in one script, never
  two at once; e writes its own tagged csv and may run beside them. Expected order of cost: b minutes, a and c a
  few hours each, d the expensive one (a two-parameter root inside the $\pi$ loop per country): launch d last,
  from the first country's timing, and drop its `cses` half if the budget does not hold.

**Builders** (`python/paper`, `--map` and `test_onlineAppendix` after; the `spec`/`betaRule` plumbing is C14's):
- New `OECD26_Spending` (figure, section 6): two panels, spending on growth and on the Gini, data and layer 1 at
  `spendingSpec`; the slopes and standard errors in the note. Copied to `writing/Paper`.
- `OECD26_Layer1`, `OECD26_Slopes`, `OECD26_Omega` at the main variant (names unchanged). `OECD26_Slopes` keeps
  the five rows; W19 decides which it prints in the text.
- New `OECD26_Robustness` (table, appendix H): the index-on-growth, index-on-Gini and spending-on-index slopes of
  both layers under spec {size, sizePiR} × $\beta$ rule {common, commonR} × turnout {cps, cses}, the data's slopes
  on top; a cell whose rows are missing prints `--`, never a stale value.
- New `OECD26_Reconcile` (table, appendix H): the U.S., the UK and France measured both ways: $\theta^*$,
  $\tilde V$, $\nu_{2020}$, $\omega$, and the design chosen under the U.S. parameter (the deep test's row from
  `escCountry`, the cross-section's layer 2); reads `usCalibrationSummary.csv`, `escCountry*.csv`, the
  `oecd26` csvs.
- `US_ESC_Country`: the UKUS row dropped (R7), the `sizePiR` rows added with a spec column (one table).
- `usukfrCalibration(countries)`: new output `USFRCalibration` (the U.S. and France, section 6); the three-country
  table stays registered for appendix F.
- Online-appendix variants: `OECD26_*_29`, `_cses` at the main variant, plus `_size` (the $\lambda$ transport)
  for page C6.

**Ledger `notes/ledger_R6.md`** (checkpoint 1's input): every slope of every variant in one table (data, layer 1,
layer 2); the anchors ($\lambda$ or $\epsilon$, $\omega$, `R2020`) per spec and turnout; the deep test under both
transports (the UK's and France's chosen designs, the UK's own parameter, the share of each distance the U.S.
parameter closes); the reconcile rows; the counts; and the list of paper sentences the main variant's numbers change
(abstract, introduction, 7.2's "a quarter", 7.3, the conclusion), old value → new value with file:line.

## R7. Retire the UK as host (paper-compute, Opus xhigh; separable, after R6)

The UK as a second laboratory lives only in the online appendix (B2, C2) and its pipeline arm; with the UK a donor
plus the deep test it goes. Keep: the UK's own cost across $\rho$ (`escCalibrationCRRAUK.csv`, stage (i)
`--prepub`), the LOG `own` rows of `escCountry*.csv`, `escPathHost.csv` (page C1 by country).
- Pipeline: drop the `FRUK` and `UKUS` sweeps (`runCalibrationUS.py`), the entries `shocksUK*`, `shocksUKUS*`,
  `escShocksUK`, `escShocksCRRAUK`, `escExperimentsUK` (`runShocksUS.py`), `collectESCexperiments.py --host UK`,
  the `('UK', 'US')` regrouping in `runESC.stageCountry`, `config.US['ukHost']` and `esc['uk']['scenarios']`
  (keep `esc['uk']['bracket']`, `nsScan`, `nScan` for the UK's own calibration).
- Builders and site: retire `FRUK_householdheterogeneity`, `UKUS_householdheterogeneity`; `siteData.OECDHOSTS` →
  `('US', 'USMedicare')`, `escCounterfactuals` hosts → `('US',)`; `onlineAppendix.py` exhibits `OECD_Hosts`, the
  regroup exhibits, `ESC_Hosts` retired with their keys aliased; pages `oecd-countries.qmd` and `esc-countries.qmd`
  retired (W21 writes the pages; R7 removes the exhibits and keeps the build green).
- Results to `archive/results/ukHost_2026-10/` with an `archive/INDEX.md` line: `UK_shocks*.csv`,
  `UKUS_shocks*.csv`, `FRUK_rhoGrid*.csv`, `UKUS_rhoGrid*.csv`, `escShocksUK.csv`, `escShocksCRRAUK.csv`,
  `escExperimentsUK.csv`. The UKUS rows of `escCountry.csv` stay on disk; the builder filters them.
- Tests: `test_eu.py`'s FRUK/UKUS checks and any UK-host reference in `test_esc.py`; `runTests.py` notes.
- Data: the `calibrationUS` sheet of `UKMain.xlsx` and the UK-cut sheets of `FRMain.xlsx` become unused: a line in
  `data/README.md`, the sheets untouched. TODO D3 closes with this package.
- `REPLICATION.md` rows through `--map`; `python/paper/README.md` and `python/US/README.md` lines.
- Interfaces: W18 cuts the UK-host sentence of section 6 and appendix F.4; W21 the pages.

## W18. Section 6 and appendix F (paper-writer-lead, Opus max)

Files: `Sections/OECD.tex`, `Appendix/CalibrationOECD.tex`. Exemplar `Sections/EndogenousTheta.tex`; the style
guide; `notes/ledger_R6.md`; the current text and every table and figure it cites.

Section 6, in order:
1. Opening paragraph: the U.S. is the laboratory; France and the UK supply the counterfactual characteristics
   (France's income distribution, voting profile and taste for leisure; the two ageing scenarios bracketing the
   two countries' demography); the design is given; the deep test and the design test are section 7's. The
   sentence "three rich OECD economies that differ markedly" goes; the informality footnote stays.
2. Calibration: the U.S. (table `USFRCalibration`), France's characteristics in one paragraph with the numbers the
   counterfactuals use; appendix F for the household data of the three countries and the UK's calibration. The
   $\omega$ ordering as a finding goes (the deep test reports the UK's and France's $\omega$ where it needs them).
3. Determinants (figure 6.1): text unchanged except the "three economies" phrasing and, with R7, the UK-host
   sentence ("With the UK as the host economy ...") and its appendix pointer.
4. The IES: unchanged.
5. New `\smalltitle{The OECD cross-section: spending.}`: the 26 countries at their observed designs, no cost,
   U.S. $\beta$ and $\omega$, each with its own demography and income distribution; figure `OECD26_Spending`; the
   slopes against the data's; spending unrelated to the Gini in model and data; one sentence on what is held common,
   pointing to section 7.4's ledger; the closing paragraph: the design pattern of figure 1 needs the design chosen.
   Replaces the current closing paragraph ("We now return to figure ...").
Appendix F: an opening sentence on the roles (the U.S. calibrated; the UK's and France's data serve section 6's
counterfactuals and section 7.3's deep test); with R7, F.4 (France at the UK's groups) and the regrouping sentence
in F.3 go; the retirement-age correction of France's $\nu$ stays and is the number section 7.3 and appendix H's
reconcile table refer to.
Target: section 6 about its current length; appendix F shorter by F.4. New labels from the builders only.

## W19. Section 7, appendices G and H, main.tex (paper-writer-lead, Opus max)

Files: `Sections/EndogenousTheta.tex`, `Appendix/EndogenousDesignResults.tex`, `Appendix/OECD26.tex`, `main.tex`.
- 7.1 unchanged. 7.2: the paragraph ending "accounts for about a quarter of the distance ..." becomes a pointer to
  7.3.
- New 7.3 `\subsection{The UK and France}` (the deep test): their calibrations (appendix F), the U.S. parameter on
  each (table `US_ESC_Country` moved from G.1 into the text, with the $\epsilon$ transport beside the $\lambda$
  transport and the main one named per checkpoint 1), the UK's own parameter (G.1's table across $\rho$ stays in
  G), France's corner (appendix C.2), the share of each distance closed, and the UK as the case that shows what the
  broad test's held parameters do (own cost, own turnout, the transport).
- New 7.4 `\subsection{The OECD cross-section: the design}`: the ledger of what varies (the $\nu$ path, the income
  distribution, the inherited design) and what is held (a hand-written tabular without numbers is allowed: parameter,
  nature, treatment); what the test is, a conditional one: the slopes are what demography and the income
  distribution alone produce at a common cost of redistribution and common preferences; layers 1 and 2; figure
  `OECD26_Layer1` in the text if checkpoint 1 says so; table `OECD26_Slopes` printing the index rows and
  spending-on-index (the spending rows are section 6's); the results and the verdict from the ledger; one paragraph
  on the robustness of appendix H (the $\lambda$ transport, common returns, own turnout, 29 countries).
- Appendix G: G.1 keeps the UK's calibration across $\rho$ and loses the UKUS row and the regrouping paragraph (R7);
  G.2 unchanged.
- Appendix H: data unchanged; the anchor under the main spec ($\epsilon$ and $\omega$); layer 2; table
  `OECD26_Robustness` with a paragraph; table `OECD26_Reconcile` with a paragraph on the two measurements of the
  three countries (France's $\nu$ 1.04 against 1.16 with and without the retirement-age correction, $\tilde V$,
  $\omega$) and what each moves.
- `main.tex` only if an appendix is added or renamed.
Interfaces: section 6's spending subsection (W18) is cross-referenced, not repeated; the framing is W20's.

## W20. Abstract, introduction, conclusion (paper-writer, Opus max)

Files: `abstract.tex`, `Sections/Introduction.tex`, `Sections/Conclusion.tex`, `References.bib` (only if needed).
The framing: one calibrated economy with France and the UK as the source of its counterfactuals and as the deep
test, the 26 countries as the broad test; the design given then chosen, each with its laboratory and its test; the
cross-section's verdict and "a quarter of the distance" from the ledger under the main variant; the maintained
assumptions in one clause; the Conde-Ruiz and Profeta sentence consistent with the new inequality result; the road
map paragraph. Minimal writing: the paragraphs whose claims change.

## W21. The online appendix, the replication map, the READMEs (paper-compute, Opus xhigh)

Files: `writing/OnlineAppendix/*.qmd`, `python/paper/onlineAppendix.py`, `REPLICATION.md` (§3 commands, §4 by
`--map`, §5), `data/README.md`, `python/US/README.md`, `python/paper/README.md`, `python/paper/RESEARCH_LOG.md`.
Page C6 restructured around the variants (the transport, the $\beta$ rule, turnout, the 29); B2 and C2 retired
with R7 (their keys aliased to C1/C6 or the deep test); the paper's `\oa` keys all defined (`test_onlineAppendix`);
`build.py --site`; the site published only after V. W17's pattern (one pointer per section) is not applied here;
no new scattered pointers.

## V. Verification

- paper-reviewer (Opus max): numbers-against-tables audit of the abstract, introduction, sections 6 and 7,
  appendices F, G, H and the conclusion; every old value named in the ledger gone.
- paper-reviewer-lead (Fable max): referee pass of section 6's spending subsection, 7.3, 7.4 and appendix H: is the
  conditional reading of the test stated and honoured; do the deep test and the broad test tell one story; is any
  claim made that an exhibit does not carry.
- Follow-ups to W18–W20; latexmk in `logs/V/build` (page count, no undefined references); `checkPaper.py`;
  `runTests.py --all`; commit on the branch; `writing/overleaf.py` push of both projects; the online appendix
  published; entries in the root, US and paper logs; this plan and `ledger_R6.md` to
  `archive/notes/byObject_2026-10/` with an `archive/INDEX.md` line; TODO updated (W18–W21, C14, R6, R7, D3 closed).

## Agents

| Package | Agent | Model, effort | Runs after |
|---|---|---|---|
| C14 | model-coder | Opus 5.5, xhigh | — |
| R6 | paper-compute | Opus 5.5, xhigh | C14 |
| R7 | paper-compute | Opus 5.5, xhigh | R6 (shares `python/paper` files) |
| W18, W19 | paper-writer-lead | Opus 5.5, max | checkpoint 1, the Overleaf pull |
| W20 | paper-writer | Opus 5.5, max | checkpoint 1, the Overleaf pull |
| W21 | paper-compute | Opus 5.5, xhigh | checkpoint 1; its page text after W19's labels |
| V | paper-reviewer, paper-reviewer-lead | Opus 5.5 max; Fable 5.1 max | W18–W21 |

## Status

| Package | State |
|---|---|
| plan | written 2026-10-27 |
| C14 | done 2026-10-27 (diff read by the main session; gate rerun in `logs/C14/gate/gate.log`: US `test_oecd26` 45/45, paper `test_oecd26` 9/9, fast suites 29/29 in 806 s, `test_oecd26Anchor` 5/5). Not committed. Stale notes fixed by the main session: `python/paper/README.md`'s cross-country bullet, `runTests.py`'s `test_oecd26` note. Fine-grid row times (GBR): `sizePiR` 43–48 s, `commonR` 9 s |
| R6 | done 2026-10-27 (runs 13:57–17:16, every row nEqMax 1 and nFallback 0; builders and ledger in; diff read by the main session; gate `logs/R6/gate/gate.log`: build 58/58, paper `test_oecd26` 13/13, `test_onlineAppendix` 10/10, US `test_oecd26` 55/55 after the main session's fix of `runESC.mergeWrite` (csv reread round-trip exact), fast suites 29/29 in 843 s). Stale line fixed by the main session: `python/US/README.md`'s status. Not committed |
| checkpoint 1 | decided 2026-10-27, see above. RKB, 18:05: "continue through it all", i.e. V, the commit on the branch, the Overleaf push and the site publish without a further go; RKB reviews on Overleaf tomorrow |
| R7 | done 2026-10-27 19:00 (diff read by the main session; fast suites 29/29 in its own run; D3 closed) |
| W18–W21 | W18, W19, W20 done 2026-10-27 18:10–18:35 (diffs read by the main session; section 6 2051 words, 7.3 new, 7.4 and H enlarged, G shortened; the transported cost parameter written as varepsilon, appendix C symbol, by the main session in 7.3/7.4/H, the pipeline follows in W21; appendix C pointer to 7.3 fixed). W21 after R7 |
| V | reviewers launched 18:50 on the writers state (paper-reviewer numbers audit, paper-reviewer-lead referee pass); latexmk in logs/W/build |
