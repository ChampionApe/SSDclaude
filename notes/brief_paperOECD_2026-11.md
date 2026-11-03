# Brief: the paper's cross-section on C at own turnout, the predicted-design figures, and the moves to the online appendix (2026-11-02)

RKB's decisions of 2026-11-02 (root log to come):
- **D1.** Section 7 is motivated by review point O3. Without the cost a more Bismarckian design lowers the tax
  (proposition LOG:PEE; −6.6 p.p. corner to corner in figure 6.1), while in figure 1.1 spending rises with the
  index. Section 7 resolves this: under the cost the tax is hump-shaped in θ, and ageing raises both τ and θ.
- **D2.** The main specification is θ variant C, each country's own turnout (CSES), layer 1 at the U.S. anchor's ω.
  The stylized readings go to appendix H as robustness: layer 1 at the average ω, and the pooled turnout (U.S. own,
  AUS/BEL/LUX flat, the rest the voluntary average). They are in `results/oecd26_explore/`, with the reading in
  `logs/variantCompare/summary_2026-11.md` and `python/US/README.md`.
- **D3.** Two predicted-against-observed design figures: design A in section 7.3 and design E in appendix H. Index
  versions of both are built for RKB's discussion and not input in the paper.
- **D5.** Robustness of the measure: C, A and B only, in appendix H. The old index and A2pt leave the paper.
- **D6.** Appendix H.5 (measured twice) is dropped. Appendix F.3 (the UK's calibration) and appendix G (G.1, the UK
  and France calibrated in full; G.2, the design along the baseline path) move to the online appendix.

Scope: `python/paper`, `config.py`, the stage (ii) declarations, `onlineAppendix.py`, and page stubs in
`writing/OnlineAppendix`. Writers do the prose later. Never hand-edit a generated `.tex` in `writing/Paper`.

## Tasks
**T1. Main specification.** Set `config.US['oecd26']['turnout']` = `'cses'`. Every cross-section output follows:
figure 6.2 (`OECD26_Spending`, no cost), figure 7.2 (`OECD26_Layer1`), table 5 (`OECD26_Slopes`), `OECD26_Omega`,
and the online-appendix exhibits that take the default.
- Generated notes and captions must give the sample (20 countries; Luxembourg has no CSES survey), the turnout and
  the anchor's values (C/cses: β 0.651, ω 1.257, ε 13.086).
- Remove any text that assumes U.S. turnout.
- Check: no-cost spending on growth at cses is −12.15 (1.15) in the model against −15.39 (4.90) in the data (on
  ν2020; figure 1.1's population-growth regressor gives slightly different values).

**T2. Spending at the chosen design in section 7's test.** Today figure 7.2 and table 5 set spending at the
observed design (`τ2020`) against the chosen design's index (`θInForce`) (review O3).
- Add a switch read by `tablesOECD26`/`figuresOECD26`, e.g. config `'spendingReading'`: `'observed'` | `'chosen'`.
- Section 7's outputs use `'chosen'`, i.e. 100·`τInForce`·(1−α), in both layers. Figure 6.2 stays at the observed design.
- Layer 2's ω matches spending at the observed design, so its spending cells are no longer "targeted". Print them,
  and say in the note that layer 2's ω matches each country's spending at its observed design.
- Expected at C/cses: spending on the index 54.58 (5.34) in layer 1 and 56.33 (6.52) in layer 2.

**T3. Design A and E figures.** The reference implementation is `scatter()` and `multiples()` in
`C:\Users\sxj477\AppData\Local\Temp\claude\C--Users-sxj477-Documents-GitHub-SSDclaude\4d783720-9d09-4e77-8130-668e1608478d\scratchpad\thetaFigs\make.py`.
RKB approved its look, so keep it, in the house style of `figures.py`.
- **`OECD26_ThetaFit`** (section 7.3): predicted `θInForce` against observed `θData`, two panels (layer 1 | layer 2),
  main specification. Draw the 45° line, the fitted line over the non-U.S. countries, the U.S. marked as the anchor,
  and ISO labels. Report r and RMSE, with the RMSE of predicting the sample mean beside it, leaving out the U.S.
- **`OECD26_ThetaFitGrid`** (appendix H): the same without labels on common axes. Rows: U.S. turnout (21), own turnout
  (20), pooled turnout (21, from T4). Columns: layer 1 | layer 2.
- **Index versions** of both, with 1/(2 − θ) on both axes and the statistics in index units. Build them; don't input them.
- Give both figures marks and a generated note with their statistics, as `OECD26_Spending` has, so the prose can
  cite them. Expected: C/cses r 0.74/0.79, RMSE 0.27/0.23 against 0.33; C/cps r 0.17/0.50; pooled on 21 countries
  r 0.35/0.78; in index units, C/cses r 0.70/0.76.

**T4. The stylized runs into the pipeline.** Register R1–R3 (`logs/oecdVariants/run.sh`) as a stage (ii) entry so
the paper can cite them.
- Use a folder name fit for the paper, e.g. `results/oecd26_stylized/`. Move the csvs only if their keys let every
  row be reused without a solve; otherwise keep `results/oecd26_explore/`.
- Add a small table, **`OECD26_Stylized`**, for appendix H. Rows: C at own turnout, own turnout with average ω, pooled
  turnout, pooled with average ω. Columns: n, the index relations' slopes (L1/L2), the θ correlation (L1/L2), and the
  mean θ and spending, model against data. Add a line on own against pooled turnout on the same 20 countries.

**T5. `OECD26_ThetaVariants`.** Rows C (first, marked as the paper's), A and B, at U.S. and own turnout as now.
- Drop `'paper'` and A2pt from the table and from `config['thetaVariants']`. A2pt's results stay on disk, but its
  runs leave the declarations.
- The table replaces the stale `OECD26_Robustness` in appendix H.

**T6. F.3, G and H.5 leave the paper.**
- **ONLINE_ONLY:** `UK_householdheterogeneity`, `UK_ESC_Calibration`, `US_ESC_Country` and `US_ESC_Path`, with their
  `EXHIBITS`.
- **`USUKFRCalibration`:** the paper's appendix F keeps the U.S. and France under the same label, `table:US:Calib`. The
  three-country version goes ONLINE_ONLY.
- **Page stubs**, following `writing/OnlineAppendix/README.md`: a heading, the exhibit includes and an empty prose
  slot. Add each to `_quarto.yml`, its part's landing page and `index.qmd`:
  - **B6 `oecd-uk`** "The UK": the three-country calibration table and `UK_householdheterogeneity`.
  - **C7 `esc-countries`** "The UK and France calibrated in full": `UK_ESC_Calibration` and `US_ESC_Country`.
  - **`US_ESC_Path`** joins C1 `esc-paths`.
- Then run `build.py --site`, so `writing/Paper/onlineAppendix.tex` defines `\oa{oecd-uk}` and `\oa{esc-countries}`.
- `OECD26_Reconcile` and `OECD26_Robustness` are no longer built, and their stale copies in `writing/Paper/Tables`
  stay. I delete them after the writers remove the `\input` lines.

**T7. The tax against a pinned design** (O3's picture). Take the U.S. at ρ = 1 under log preferences, in the
paper's calibration with the cost (table `US_ESC_Calibration`) and in the one without it (section 6).
- Pin θ on the whole path at 0, 0.1, …, 1, plus θ* = 0.5445, and record τ_2020 and spending. Use runESC's pinned
  machinery.
- Expected: without the cost τ falls in θ (−6.6 p.p. corner to corner); with the cost, a hump.
- Outputs: a csv in `results/esc/` from a stage (ii) entry, and an ONLINE_ONLY figure (e.g. `US_ESC_TauTheta`) on C7
  `esc-countries` or C3 `esc-costs` (your choice). Its note gives the peak θ, τ at the peak and at both corners, with
  and without the cost.
- If this would run longer than an hour, stop and report instead.

## Checks
- `build.py` builds every output; `--map` updates `REPLICATION.md`.
- `test_oecd26.py`, `test_onlineAppendix.py` (adapted), the fast suites of `python/runTests.py`, `writing/checkPaper.py`
  and `build.py --site` all pass.
- `python/paper/README.md`, the config comments and the module log are updated. No commit.

## Report
- every new or changed output, with its label, and the `\input` lines the writers must add, swap or remove;
- the numbers the prose will quote, from the generated notes: section 6's and 7's slopes at cses, the anchor, T3's
  statistics, T4's table and T7's peak;
- the page keys and their exhibit ids;
- anything that deviated from the expected values above.
