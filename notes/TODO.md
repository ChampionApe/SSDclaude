# TODO (restructured 2026-09-11)

The one open list. Closed work is not here: it is in the session logs (`RESEARCH_LOG.md`,
`python/<module>/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`) and, for the 2026-09-08 rewrite plan and
the permanent-timing fix, in `archive/notes/todo_paperRewrite.md` and `archive/notes/todo_escPermanentTiming.md`.
`notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. C1, C2,
R1, R3, R4 and W3 closed on 2026-09-11 (`python/US/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`); C4
and W2 on 2026-09-12, W4 the same day on RKB's instruction, W2b on 2026-09-15 along with the rest of W5.
Open: W1, a wording call; W5's one remaining part, whether the paper carries a verification paragraph;
one data caveat under D1, France's voting at the UK cuts, MGE's; P1 closed 2026-09-30 with the merge into `main`; P2 below is the paper rewrite; its plan, retired on 2026-10-07, is `archive/notes/paper_presentationPlan.md`.

## Plan in progress

**P1. The size-scaled leak as the paper's endogenous design** -- closed 2026-09-30. Branch `esc-sizeLeak` (opened and executed 2026-09-24, WP1 to WP6, decisions D1 to D6 at their defaults; 7.2 rewritten 2026-09-29 with the cost as an extensive-margin loss on the tax component, `notes/esc_costLiterature.md`) was fast-forwarded into `main` at `77ba943` after both Overleaf projects were checked unchanged. The plan is restored from history to `archive/notes/plan_escSizeLeak.md` and its five live citers repointed. What stays open from it is C5 below. Diagnosis and outcome: `notes/esc_inequalityChannel.md`; finding #17.

**P2. The paper rewrite** -- branch `paper-rewrite`, opened 2026-09-30 from `main`, fast-forwarded into `main` and deleted on 2026-10-07. The 2026-09-30 plan with its five sessions and gates ran through session 4 (the appendix split and the online appendix, `notes/paper_onlineAppendix.md`); from 2026-10-06 the sections were reshaped with RKB in session instead, and the plan and the gate notes are retired to `archive/notes/` (`paper_presentationPlan.md`, `paper_gate1-3.md`). W7 was folded into it. State on 2026-10-07: sections 1–6 settled apart from final checks; section 7 restructured (root log of the date: the derivations in appendix C, the corner out of the main text, the summary table `US_ESC_Summary`). Open: the abstract, introduction and conclusion still say "inequality moves the design little" where section 7 now says the direction depends on the IES (W8a), and their rankings lack section 6's ρ ≤ 1 qualifier (W8b); the number audit of every prose number against its table (the plan's E1); RKB's read of the online appendix's exhibit texts and the publication to GitHub Pages; the Overleaf push of the restructured section 7 and appendix C; appendix C's counterpart in the technical note; a `\oa{home}` macro.

**C5. A linear (Okun) term in the leak** -- follow-up to P1, decision D3. Under a purely quadratic loss the
first unit of redistribution is free at the margin, so no electorate chooses exactly $\theta = 1$ and
France's design is a prediction the model cannot reach. A term linear in $1-\theta$ restores the corner at
the price of a second parameter, which the UK's design could pin (two targets, two parameters, France as
the prediction). Not in this draft; one sentence in `sec:esc` says so.

**C6. The CRRA design choice lets past savings shares move with the candidate design** -- opened
2026-10-02 (`notes/esc_crraDesignChoiceProblem.md`), closed 2026-10-03 with the final run. The root-in-a
layer (alg `esc:crra2D`, `LeadedCRRA2D` `designRule = 'root'`) won the pilot against the first order
condition layer (finding #19) and produced every CRRA endogenous-design row of the paper: the exact λ moved
by less than a third of a percent and the chosen designs by at most 1.3e-3 (five third decimals of the paper),
read in `archive/notes/todo_finalRun_2026-10-02.md` and item 18 of `num_esc.tex`'s checks; the paper's section 4
paragraph is rewritten. History: root log 2026-10-02 (evening) and 2026-10-03, `python/US/RESEARCH_LOG.md`.

**C7. Tax candidates compared at frozen savings shares** -- done 2026-10-02/03 (`roots1d.selectMaxFrozen`
with the equilibrium test's cell clause restricted and candidates within a cell merged, all seven solvers,
`writing/*/num_robustroot.tex`, findings #18 and #5; history in the gridsearch, US and informal logs). The
final run of 2026-10-03 found one equilibrium and no fallback at every counted state of both arms, so the
rule never bound and every published number is bitwise or within cross-process noise of the earlier one
except the CRRA design rows of C6. **Open: RKB to confirm the restatement of the equilibrium test in the
three `num_robustroot.tex` and the section 4 sentences of the paper.**

**C8. Argentina's pre-reform ε and γ₀ do not match the text** -- found 2026-10-06 (evening), closed 2026-10-07: the run
read, the paper's Argentine numbers updated (section 5, abstract, introduction, conclusion, section 4's footnote), ε = 0.21
and γ₀ = 0.47 in the calibration table, the reform's 2010 tax response 2.1 p.p. and about three quarters of the observed
rise, every count one equilibrium and no fallback. History below. Two
mismatches, both confirmed on the published ρ = 1 instance (the preview scripts and logs are in the session scratchpad
`argPreview/`; the self-check reproduced the published calibration and reform bitwise):
- *ε_pre.* `InformalSavings/model.py` `getEps` reads `auxProd(t0)[1]`, a positional index: the SECOND formal quartile
  (relative income 0.71), giving 0.29. Appendix D's formula and "the least productive formal workers", and the
  reform's own ε^U in `shockUniversal.py` (`refType = 1`, the first quartile, 0.46), say the FIRST, which gives 0.21.
  `shockUniversal.py`'s docstring speaks of "type j=2", so the second quartile may once have been deliberate.
- *γ₀.* The model counts informal households per formal household (formal shares sum to one; the budget divides by
  1+γ₀ε), so the workbook's 0.32 makes informal households 24% of all. The datum, 32%, is the share of the population
  over 65 without a pension in 2004 (Rofman and Oliveri 2012, table A1.1; not Cetrángolo and Grushka, who have no such
  figure); as a share of all households it means γ₀ = 0.32/0.68 = 0.47.
Preview at ρ = 1, log, common X (2010 reform, change against the pre-reform path; published: Δτ +1.25 p.p., Δsavings
rate −0.28 p.p. of GDP, Δworkweek −0.14 h, "almost half" of the amnesties' 1.8% of GDP): (a) first-quartile ε alone:
ε = 0.21, Δτ +1.77 p.p. (1.15% of GDP, about two thirds); (b) γ₀ = 0.47 alone: Δτ +1.45 p.p.; (c) both: ε = 0.21,
Δτ +2.08 p.p. (1.35% of GDP, about three quarters), Δsavings −0.43 p.p., Δworkweek −0.25 h; 2040 under (c): +3.53 p.p.
Every variant converges. A production fix is `getEps`'s index (by label, as `getθ` does) and the workbook's γ₀ through
Excel, then the Argentine stage (i) and (ii) with `--force`, about 4.5 h per variant on the 16-point grid, then the
paper's section 5, abstract, introduction and conclusion ("almost half") and the online appendix.
**In progress 2026-10-06 (night), RKB's decision: ε is 70% of the minimum pension, the first quartile's benefit, and
γ₀ is 32% of all households.** Done: `InformalSavings/model.py` and `informalAnalytical/model.py` `getEps` read the
type by label (`refType = 1`), `shockUniversal.py`'s docstring aligned; `data/ArgentinaTest.xlsx` heterogeneity!B2 =
0.32/0.68 = 0.4706 through Excel (formulas intact, `data/README.md` says so). The Argentine arm re-solves as a detached
chain, `logs/finalRunC8/runArg.cmd` launched 20:24 (stage (i) both variants, then stage (ii) `--all`; the marker is
`logs/finalRunC8/ARG_STATUS.txt`, START / STAGE1_DONE / DONE or FAILED; about 4.5 h). The anchor point already reads
β = 0.6495, ω = 1.4501, the preview's variant (c). **Left for the session that reads the run**: `build.py` (Argentine
tables and figures, `US`-arm untouched), `--map`, `--site` and `quarto render`; section 5's numbers (1.2 p.p., 0.8% of
GDP, "almost half", 0.3 p.p., 0.1 hours, 2.1 p.p. by 2040, the CRRA paragraph's ranges), the calibration table's reading
("γ₀ = 0.47 ... puts informal households at 32% of all households"), the abstract, the introduction and the conclusion
("almost half"); appendix D's ε formula is already the first quartile's; the technical note has no number to change;
`results/numerical/ARG_stationaryApprox_commonX.csv` if `--all` does not refresh it (section 4's footnote, 0.3 p.p.);
the preview scripts in the session scratchpad are not needed again.

**W8. The reviewer's reading of the rebuilt draft** (2026-10-03, paper-reviewer, numbers against the tables
regenerated after the final run; the stale numbers it listed were fixed the same day). Five findings that are
RKB's calls, not number fixes: (a) "inequality moves the design little" (abstract, introduction, `sec:esc`
twice, conclusion) is contradicted at ρ = 2, where France's income distribution moves the chosen design from
0.738 to 0.918 against 0.826 under acute ageing; it holds at ρ ≤ 1 (+0.034/−0.031 against +0.087/+0.078), and
section 7 argues ρ = 2 is the plausible cost. (b) The ranking "ageing, the earnings link, then inequality and
voting minor" (abstract, introduction, `sec:oecd`, conclusion) fails at ρ = 2 with θ fixed: French voting
moves the tax by 1.7 p.p., the whole earnings link by 1.5 p.p. (`US_CRRA_OtherShocks`, `US_CRRA_PensChars`).
(c) `Sections/Argentina.tex` quotes relative hours "1.18 against 1.10" and `HouseholdSurveyArg.tex` "about 8%"
with a cross-reference to `table:Arg:Calib`, which carries no relative-hours entry (correct against
`calibrationSummary.csv`): restore the entry through `python/paper` or drop the reference. (d) Introduction:
"unless propensities to vote rise sharply with income" against `prop:esc:corner`, which assumes propensities
that do not rise; the conclusion's wording is right. (e) `US_ESC_ScaleWedge`'s caption and note and
`Appendix/US.tex` say "the previous draft"/"an earlier draft" (revision history in referee-facing text; the
generator in `python/paper`), and the appendix's "the UK chose θ = 1" is in no table. (e) closed 2026-10-06: the
table now sets the two cost specifications side by side, online (OA.4.6), and the appendix paragraph is one pointer. Section 6 settled 2026-10-06 (evening): its results part states the ranking
for ρ ≤ 1 and names ρ = 2 as the exception, where French voting overtakes the earnings link; (a) and (b) stay open
for the abstract, the introduction and the conclusion.

**W7. After the appendix split** (2026-09-29, root log) -- two calls for RKB. (a) France's LIS survey year
is not stated anywhere in the draft; `sec:oecd` implies 2019. (b) `sec:esc` and the conclusion say the
UK's own λ is "within 16%" of the US one: true at ρ = 1 (7.264 vs 8.643), but at ρ = 2 it is 61% above
(2.786 vs 1.728; appendix G.2 says so). Also whether `sec:esc` gets one sentence on the UK-host results. Folded into P2 (2026-09-30): (a) is agent A4's brief, (b) is fixed in session 1 of the plan (`archive/notes/paper_presentationPlan.md` §8); the UK-host sentence is a session 1 call.

## Data tasks

**D1. France regrouped at the UK's income cuts** -- done 2026-09-22, with two caveats for MGE. The source
turned up in the old repo: `SSD/Data/calibration statistics AUG 2025.docx` carries France's LIS group
means at BOTH cuts (US percentiles, and the UK's 29.2/87.3), and its first sampling reproduces
`data/FRMain.xlsx` (shares to 6 decimals, income and hours to the cent) with one exception below. The
second sampling is now `heterogeneityUK`/`calibrationUK` in `FRMain.xlsx` (written through Excel; the
Readme sheet says where every column comes from): income 20011/37081/94604, hours 1629.38/1855.62/2194.58,
shares 0.2924/0.5807/0.1269, workweek 35.24. Caveats:
- *Voting at the UK cuts has no source.* CSES gives France's voting at the US cuts only
  (0.8097/0.8567/0.8518). The sheet carries the observed values weighted by the population overlap of the
  new groups with the old (0.8097/0.8323/0.8518), i.e. voting flat within each observed group. MGE to
  replace with CSES at the UK cuts if available; the profile is nearly flat either way.
- *A typo in France's hours, corrected 2026-09-22 on RKB's instruction.* The workbook's low-group hours
  were 1731.91, the docx says 1713.91, and the docx value is the consistent one: it makes France's average
  workweek the same at both cuts (35.240), where the workbook's gave 35.44. `data/FRMain.xlsx` sheet
  `heterogeneity` C3 now carries 1713.91 (through Excel; the Readme sheet records it). France was re-swept
  in both variants and stage (ii) re-run (`logs/frFix0922.log`): only France's hours unit moves (ω, τ,
  the savings rate and the income and voting rows are invariant to it), so what changes is the leisure and
  all-characteristics workweeks and France's own workweek, 35.44 → 35.24.
- *The UK's own regrouping at US percentiles is a linear fit, not data.* `UKMain.xlsx` sheet
  `heterogeneityUS` is Excel `FORECAST` of the three UK group means on cumulative shares. Applied to
  France it predicts a negative bottom-group income, so the method is unreliable at extreme cuts; the
  `UKUS` sweeps and `UK_ESC_Calibration`'s "US-percentile" reading rest on it. Worth a microdata
  recount if UKUS is ever printed.

**R5. The UK exercise runs** -- done 2026-09-22 (`logs/frukSweep0922.log`, `logs/ukShocks0922.log`): FRUK
swept in both variants (16/16 points each, France's ω at ρ = 1 equal to its US-cut value 1.4181, as the
aggregates do not see the grouping), `UK_shocks{,CommonX}.csv` written at ρ = 0.5, 1, 2, six UK outputs
built. The runs are wired as ordinary stage (i)/(ii) entries, so a rebuild picks them up.

**W6. The UK paragraphs** -- done 2026-09-22, drafted text for RKB: the results paragraph in
`app:US:french`, one sentence in `sec:oecd`, a footnote on the voting approximation, and the sign flip of
the income row across calibration variants noted in `app:US:vectorX`. Read them against
`Tables/UK_OtherShocks{,_vectorX}.tex`.

## Traps to remember (kept here because `README.md` points at them)

- **openpyxl drops cached formula values on save.** The Argentina workbook has formulas; after an
  openpyxl round trip pandas reads them as NaN and every steady state fails. Edit workbooks through Excel
  (COM from PowerShell works) or write literal values.
- **`PYTHONUTF8=1` for every pipeline run.** The scripts print Greek letters; under the cp1252 console
  they crash on the first print.
- **PowerShell `*>` redirection writes UTF-16.** Route python output through `cmd /c "... > log 2>&1"`.
- **A `tail -F` on a log a PowerShell script appends to makes every later `Add-Content` fail silently.**
  Poll with `grep -q` in an `until` loop instead (`notes/crossCuttingFindings.md` #14).
