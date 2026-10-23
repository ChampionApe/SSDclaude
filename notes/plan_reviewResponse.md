# Plan: the response to the AI review of 2026-10-22 (W16)

Executes the agreed actions in `notes/paper_reviewResponse.md`: A1–A14 and the detailed comments 1–25 at their
first-pass verdicts. Drafted and settled with RKB on 2026-10-23 (decisions at the end). The work runs on the branch
`review-2026-10`; the status table says where it stands.

## Principles

1. **Numbers before words.** No paper file changes until the runs it cites are done and checkpoint 2 has passed.
2. **Minimal writing.** A writing agent updates numbers and the sentences its actions name. It rewrites a
   paragraph only when the paragraph's claim changes (a sign, a ranking, an ordering) or the content is new: the
   26-country test, the cost variants in section 7 (A8), B.1's proof, the uniqueness and horizon material.
3. **Numbers at their source** (CLAUDE.md): workbooks, `python/paper/config.py`, the experiment csvs. Generated
   `.tex` files are never edited by hand.
4. **Workbooks in Excel only.** The calibration cells are formulas (`=0.101/(1-B2)`, `=39.2/49.2`). Saving with
   openpyxl drops their cached values, and pandas then reads NaN. Edit through Excel (COM works here, Excel 16)
   and check that the loader reads the new values. `python/US/model.py:149` repeats the old U.S. targets as
   defaults; update them with the workbook.
5. **Counts before reruns.** C0 lands first, so every rerun records its candidate counts (A6).
6. **Disjoint files.** One file set per writing agent; code agents work in separate modules; C3 adds files and
   touches shared ones only at its end.
7. **Each package ends green**: its tests, `build.py` (stage iii), `checkPaper`, and the `REPLICATION.md` and
   `data/README.md` rows for anything new.
8. **Checked, not trusted.** The orchestrating session reads each package's diff and reruns its checks before the
   next phase builds on it.
9. **Paper text by Opus 5.5** (RKB, 2026-10-23). Fable writes theory notes and read-only reviews only;
   paper-writer-lead now runs on Opus 5.5 by its definition and keeps its line-by-line derivation checks.

## Phases and checkpoints

- **Phase 0, setup.** Done 2026-10-23. The decisions are settled and the uncommitted work is committed on
  `review-2026-10`, which gives `python/paper/compareResults.py` its baseline. Co-authors do not edit the paper
  meanwhile.
- **Phase 1, in parallel.** T1–T3 start at once. C0 runs first, then C1, C2 and C3's code in parallel.
- **Phase 2.** C3's runs (after C1 has fixed the U.S. conventions), then C4 and C5 (after C1 and C2).
- **Checkpoint 2.** Review the findings diff (`compareResults.py`, plus each package's ledger of the numbers the
  prose cites, old and new, with file:line) and the theory outcomes. We decide which findings changed, and so which
  paragraphs open up.
- **Phase 3.** Writing (W1–W8) and the online appendix pages (W9).
- **Phase 4.** Verification (V), logs, commit. The Overleaf push and the online appendix publish happen on RKB's go.

## Code and data

**C0. Candidate counts in every solve (A6).** Today only `informalAnalytical`'s solver records them
(`policy.multiplicitySummary`), and OA D2 has them for no U.S., UK or French calibration path and for 6 of 54
`US_shocks` rows. Record nCand and nEq in every PEE solve the paper uses (Argentina, the U.S. block, ESC) and write
them to the result csvs. Done when every test suite passes and stage (iii) rebuilds byte-identical except for the
new count columns.

**C1. The U.S. block (A2, A8).**
- *U.S. workbook.* Pensions only, at figure 1.1's cash value (7.37% of GDP, `data/oecdFigure1.csv`);
  `Universal share` 0 (it is inert: `getEps`); `=39.2/49.6`.
- *UK and France.* Figure 1.1's cash values (7.84 and 14.44% of GDP, from 8.3 and 14.9). France's ν in 1990 and
  2080 set to appendix F's stated rule.
- *Medicare variant (OA).* A sheet or a switch, not a code fork: τ with Medicare and θ = (1 − 0.287)θ_P.
- *Reruns.* Stages (i) and (ii) for the U.S., UK and France; ESC with λ recalibrated; the UK and France at the new
  λ; the Π-inclusive and design-level cost variants (A8); the Medicare variant.
- *Ledger.* `notes/ledger_C1.md`.

**C2. Argentina (A7, A12, #2, #3, #4, #19, W15).**
- *#4.* At the reform date the copy rebuilds retirees' savings shares under the new ε (`policy.py`,
  `tLag = tFirst`), although they were formed under the old one. Fix it and test.
- *#3.* One GDP concept in the spending target and in the outcome.
- *A7.* The pre-reform ε = 0 variant; formal benefits in table 2.
- *Reruns.* Stage (i) (about 3.2 h) and stage (ii).
- *A12.* Both sides of (B.5), with σ⁰ and σⁱ, at the calibration.
- *#19.* Check whether the low-IES reversal is resolved at ρ ≤ 0.6 on the grid, before the threshold is stated.
- *W15.* Decompose the 2010 first-order condition at ρ = 0.5 and 1: why the young's resistance dampens the reform
  but not the design effect.
- *#2.* The model's counterpart of Gonzalez-Rozada and Ruffo's estimate, in its units, if the household savings
  allow it.
- *Ledger.* `notes/ledger_C2.md`.

**C3. The 26 countries (A14, A3, A4); code in phase 1, runs in phase 2.**
- *Loader.* Builds the U.S. model from `data/oecd29.csv`:
  - groups at the U.S. percentiles;
  - θ = 2 − 1/I set directly, clipped to [0, 1], not `getθ` on the group means;
  - WPP ν, with 1960 = 1990 and 2110 = 2080 as in the workbooks;
  - figure 1.1's cash spending;
  - α, β, ξ and turnout (CPS) at the U.S. values.
  The sample rule (A4) lives in the data step, not in a builder.
- *Anchor.* The U.S. at these inputs, with ω and λ calibrated at log.
- *Layer 1.* The other 25 at the anchor's ω and λ, each entering 2020 with its observed design: the 2020 tax and
  the design chosen in 2020.
- *Layer 2.* Each country's ω calibrated to its spending; the design at the anchor's λ.
- *OA.* Own CSES turnout (the anchor included), and all 29.
- *Outputs.* `results/oecd26/`. Stage (iii) builders: figure 1.1's panels with the model's points and fitted lines,
  a table of slopes (data, layer 1, layer 2), and the calibrated ω's. Plus the `REPLICATION.md` and
  `data/README.md` rows.

**C4. Horizon and accuracy (A6); after C1 and C2.**
- *Horizon.* T at three horizons around the baseline (U.S. 2140, 2200, 2290; Argentina's equivalents) and under
  appendix D's steady-state terminal condition. Run at ρ = 0.5, 1, 2 for the U.S. under CRRA and Argentina's
  informal savings. Outcomes at the calibration year and one period later.
- *Accuracy.* First-order-condition residuals at off-grid states.
- *Counts.* The candidate-count table from C0's records.
- *Output.* A csv and a table builder for appendix D.

**C5. Smaller numbers (A1, A9, A13, #5, #7, #13, #22); after C1.**
- *A1.* The critical turnout-weight ratio at the new U.S. calibration (C.1's timing), as a script with a csv.
- *A9.* Every counterfactual at every ρ, for the ranking.
- *#7.* The marginal loss at the observed design for Δθ = −0.1, at ρ = 0.5, 1, 2.
- *#22.* λ against the elasticities, with λ ≈ εΠ/R.
- *#13.* The headline design changes in index units.
- *#5.* Decompose the design condition's response to inequality. Is the channel the fall in τ, with a cost linear
  in τ?
- *A13 (OA, low priority).* τ₂₀₂₀ against inherited capital at ρ = 0.5, 1, 2, and the myopic/Markov split.

## Theory (model-theorist agents, notes only, from phase 1)

**T1. Proposition 2 (A5, #1, #10), in `notes/theory_prop2.md`.**
- θ at the stationary fixed point (weight $y_i/c_i^2$; checked).
- Inequality for J types by pairwise transfers at consistent shares (still to derive).
- The ν condition.
- ε at the inherited distribution.
- B.1's young term and its stray $\tau_t$.
- The fallback of decision 5, if the inequality step fails.

**T2. Uniqueness and appendix C (A6, #8, #9, #11), in `notes/theory_uniqueness.md`.**
- The log-HtM uniqueness proof.
- The CRRA threshold $(c_i/c_j)^{1/\rho}$.
- The conditions for (C.9)'s monotonicity near the calibrated design.
- The Bismarckian-corner argument for C.2.

**T3. Closed form and mappings (A11, #13, #22), in `notes/theory_closedForm.md`.**
- The J = 1 log-HtM tax, checked against Gonzalez-Eiras and Niepelt (2008), `pdfs/GonzalezNiepelt2008.pdf`.
- $I = 1/(2-\theta)$.
- λ ≈ εΠ/R.

## Writing (phase 3; one file set per agent)

| | Files | Agent | Actions |
|---|---|---|---|
| W1 | abstract, Introduction, Conclusion | paper-writer | A1 (Conde-Ruiz and Profeta), A9, #24, the 26-country result in a sentence each, the conclusion's "changes only the size" |
| W2 | Model, Numerical | paper-writer | #12, #15, #25; A6's sentence and footnote 12 |
| W3 | Log, appendix B | paper-writer-lead | A5 (Proposition 2 changed slightly, B.1's proof rewritten), A6's uniqueness proof, A11, A12, #10 |
| W4 | Argentina, appendix E | paper-writer | A7, A10, #2, #3, #4, #19, W15 |
| W5 | OECD, appendix F | paper-writer | A2, #18, #23, ν from WPP 2024 (not "census data"), France's ν |
| W6 | EndogenousTheta, appendix G, new appendix for the 26 | paper-writer-lead | A8, A14 (new subsection at the end of section 7; layer 2 and the data in the appendix), #5, #7, #13, #16, #17, #20, #21, #22 |
| W7 | appendix C | paper-writer-lead | A1 (C.1), #6, #8, #9, #11, #22 |
| W8 | appendix D | paper-writer | A6: counts, horizon table, residuals |
| W9 | online appendix pages | paper-compute | Medicare variant, all 29 and own turnout, A13, horizon detail |

Each writer gets its actions, the ledgers, the theory notes and `notes/paper_styleGuide.md`.

## Verification (V)

- Builds and tests: stage (iii), `checkPaper`, latexmk, `test_onlineAppendix`.
- Review: a numbers-against-tables audit of the whole paper, and a referee pass over sections 3 and 7 and
  appendices B–D against the review (each comment and the action taken).
- Documentation: `REPLICATION.md` (`build.py --map`), `data/README.md`, the module READMEs, the research logs.
- Wrap-up: update TODO W16 and D3; archive this plan and the tracker, each with a line in `archive/INDEX.md`.

## Agents

The defaults are the definitions in `.claude/agents/`. The two packages raised to max get `effort: "max"`.

| Package | Agent | Model, effort |
|---|---|---|
| T1, T2, T3 (in parallel) | model-theorist | Fable, max |
| C0 | model-coder | Opus, xhigh |
| C1 | paper-data (the workbooks, in Excel), then paper-compute (the rest) | Opus, xhigh |
| C2 | model-coder (#4, #3, the ε = 0 switch), then paper-compute (runs, A12, #19, W15, #2) | Opus: max for the fixes, xhigh for the runs |
| C3 | paper-compute | Opus, max |
| C4, C5, W9 | paper-compute | Opus, xhigh |
| W1, W2, W4, W5, W8 | paper-writer | Opus, max |
| W3, W6, W7 | paper-writer-lead | Opus, max |
| V | paper-reviewer (the audit), paper-reviewer-lead (the referee pass) | Opus, max; Fable, max |

About 22 agents in all. model-coder works from a brief file under `notes/` (`brief_C0.md`, `brief_C2.md`) written
from this plan. Every other prompt carries:
- the package's paragraph from this plan and its tracker labels;
- the files it may touch and its done-when;
- the report wanted: what changed (file:line), the checks run and their results, open issues, and the ledger for
  code packages.

## Status

| Package | State |
|---|---|
| Phase 0 | done 2026-10-23 |
| T1, T2, T3, C0 | ready |
| C1, C2, C3 (code) | after C0 |
| C3 (runs), C4, C5 | after C1; C4 also after C2 |
| Checkpoint 2 | after phase 2 |
| W1–W9 | after checkpoint 2 |
| V | after phase 3 |

A session that resumes this work reads this file (this table first), the tracker and `notes/paper_styleGuide.md`.
It launches what is ready and updates the table as packages finish.

## Decisions (settled with RKB, 2026-10-23)

1. Comments 1–25 at their first-pass verdicts. W15 goes with #19; #13's index units are for the headline numbers
   only. Known consequences:
   - #4 is a bug, and fixing it moves Argentina's numbers.
   - #3 may change Argentina's target.
   - #2 and #19 may change section 5's case for ρ.
   - #5 may change section 7.2's account of inequality and the design.
   - #22 narrows the gap between λ and the elasticities by R ≈ 2.4.
2. The 26-country test as A14: the end of section 7, an appendix, and the OA.
3. Figure 1.1's cash spending in the three main calibrations too.
4. λ keeps "political" among the costs it stands for.
5. If inequality at the fixed point fails for J types, Proposition 2 states inequality at the inherited
   distribution and θ at the fixed point.
6. D3's recount (Understanding Society) comes later; G.1's caveat stays.
7. Gonzalez-Eiras and Niepelt (2008) is in `pdfs/GonzalezNiepelt2008.pdf`.
8. The work runs on `review-2026-10`; co-authors do not edit the paper until phase 4.
