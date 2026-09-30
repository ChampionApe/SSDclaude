# TODO (restructured 2026-09-11)

The one open list. Closed work is not here: it is in the session logs (`RESEARCH_LOG.md`,
`python/<module>/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`) and, for the 2026-09-08 rewrite plan and
the permanent-timing fix, in `archive/notes/todo_paperRewrite.md` and `archive/notes/todo_escPermanentTiming.md`.
`notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. C1, C2,
R1, R3, R4 and W3 closed on 2026-09-11 (`python/US/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`); C4
and W2 on 2026-09-12, W4 the same day on RKB's instruction, W2b on 2026-09-15 along with the rest of W5.
Open: W1, a wording call; W5's one remaining part, whether the paper carries a verification paragraph;
one data caveat under D1, France's voting at the UK cuts, MGE's; P1 closed 2026-09-30 with the merge into `main`; P2 below is the paper rewrite, whose plan is `notes/paper_presentationPlan.md`.

## Plan in progress

**P1. The size-scaled leak as the paper's endogenous design** -- closed 2026-09-30. Branch `esc-sizeLeak` (opened and executed 2026-09-24, WP1 to WP6, decisions D1 to D6 at their defaults; 7.2 rewritten 2026-09-29 with the cost as an extensive-margin loss on the tax component, `notes/esc_costLiterature.md`) was fast-forwarded into `main` at `77ba943` after both Overleaf projects were checked unchanged. The plan is restored from history to `archive/notes/plan_escSizeLeak.md` and its five live citers repointed. What stays open from it is C5 below. Diagnosis and outcome: `notes/esc_inequalityChannel.md`; finding #17.

**P2. The paper rewrite** -- branch `paper-rewrite`, opened 2026-09-30 from `main`. Diagnosis, the thesis, the section-by-section recommendation, RKB's decisions D1 to D6 and the five-session work plan with its review gates are all in `notes/paper_presentationPlan.md` (§8 is the entry point for a fresh session). Agents run on Opus 5.5 through `.claude/agents/paper-*.md`. W7 is folded into it: (a) is agent A4's brief, (b) is fixed in session 1.

**C5. A linear (Okun) term in the leak** -- follow-up to P1, decision D3. Under a purely quadratic loss the
first unit of redistribution is free at the margin, so no electorate chooses exactly $\theta = 1$ and
France's design is a prediction the model cannot reach. A term linear in $1-\theta$ restores the corner at
the price of a second parameter, which the UK's design could pin (two targets, two parameters, France as
the prediction). Not in this draft; one sentence in `sec:esc` says so.

**W7. After the appendix split** (2026-09-29, root log) -- two calls for RKB. (a) France's LIS survey year
is not stated anywhere in the draft; `sec:oecd` implies 2019. (b) `sec:esc` and the conclusion say the
UK's own λ is "within 16%" of the US one: true at ρ = 1 (7.264 vs 8.643), but at ρ = 2 it is 61% above
(2.786 vs 1.728; appendix G.2 says so). Also whether `sec:esc` gets one sentence on the UK-host results. Folded into P2 (2026-09-30): (a) is agent A4's brief, (b) is fixed in session 1 of `notes/paper_presentationPlan.md` §8; the UK-host sentence is a session 1 call.

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
