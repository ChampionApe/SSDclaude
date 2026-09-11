# Archive index

Frozen on 2026-09-11. Nothing here is read routinely: `.rgignore` keeps `archive/` out of default
searches, so a plain Grep will not see it. Read a file by path when a live note points here, or search
it explicitly (Grep with `path: archive`, or `rg --no-ignore`). Never restate archive content into a
live file; link to it.

## Session logs (verbatim, through 2026-09-11)

One line per entry: title, then `file:line`.

### RESEARCH_LOG_gridsearch.md

- 2026-08-04 — `robustRoot.py`  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:6`
- 2026-08-05 — `roots1d.py`  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:12`
- 2026-08-05 (cont'd) — ND grids, and vectorizing the crossing detection  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:28`
- 2026-08-05 (cont'd) — smoothing and gradients; `selectMax` handles NaN  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:48`
- 2026-08-10 — `griddedInterp2D`, and two traps that appear once an interpolant feeds a root-finder  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:54`
- 2026-08-11 — `selectMax` groups ragged columns by feasibility pattern  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:73`
- 2026-08-11 — `continuation.py`; `interp.py` gains kinds and NaN handling  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:88`
- 2026-08-19 — `griddedSmooth1D` gains fixed knots, because adaptive ones are a discontinuity  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:119`

### RESEARCH_LOG_informalAnalytical.md

- 2026-07-10  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:6`
- 2026-08-03  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:10`
- 2026-08-04  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:14`
- 2026-08-05 — robust LOG solve  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:23`
- 2026-08-05 (cont'd) — CRRA terminal period  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:33`
- 2026-08-05 (cont'd) — CRRA t<T recursion + solvePEE_CRRA  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:45`
- 2026-08-05 (cont'd) — usage reduction  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:54`
- 2026-08-06 — calibration (`model.py` §8)  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:60`
- 2026-08-10 — `hi`/`bi` were wrong: `hRatio` was not the ratio its name claimed  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:89`
- 2026-08-12 — `createCopyFromt0`: model copies for shock experiments  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:120`
- 2026-08-24 — the calibration's starting guess, and what it exposed  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:143`
- 2026-08-25 — num docs restructured (detail in the root log)  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:158`

### RESEARCH_LOG_InformalSavings.md

- 2026-08-10 — economic equilibrium; the numerical PEE sections written  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:6`
- 2026-08-10 (cont'd) — `policy.py` (LOG and CRRA), and the docs reconciled to it  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:26`
- 2026-08-10 (cont'd) — the path solve; two traps, one in each direction  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:49`
- 2026-08-11 — the CRRA solve ~11× faster; the calibration run for the first time  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:71`
- 2026-08-11 (cont'd) — calibration across a grid of `ρ`  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:96`
- 2026-08-12 — `createCopyFromt0`, and the second asymmetric state  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:124`
- 2026-08-12 (cont'd) — the `ρ` sweep; `ρ=0.7` resists (attribution later found wrong)  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:133`
- 2026-08-19 — `ρ=0.7` solved: a discrete choice inside a differentiated residual  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:153`
- 2026-08-19 (cont'd) — the sweep re-run; the shock across the full grid  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:163`
- 2026-08-19 (cont'd) / 2026-08-20 — the `ρ=1` boundary, and a one-row patch  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:176`
- 2026-08-21 — two experiments the paper needed, and a proxy state the control run found  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:196`
- 2026-08-21 — `sweepEpsThetaGrid.py`, and the cross sweep retired  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:218`
- 2026-08-24 — the calibration target moved to K/Y, and everything downstream was re-run  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:237`
- 2026-08-24 (cont.) — cleanup  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:271`
- 2026-08-25 — the (ε,θ) grid re-solved at the current calibration  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:280`
- 2026-08-25 — num docs restructured (detail in the root log)  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:321`
- 2026-09-08 — why β is above the US's, and what the capital share has to do with it  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:330`
- 2026-09-08 — α = 0.35: the march needed a derived bracket and a seeded anchor  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:373`
- 2026-09-08 (later) — the tax target is α-dependent; first α = 0.35 run killed and relaunched  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:395`
- 2026-09-08 (night) — every suite passes under α = 0.35, τ₀ = 0.109  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:405`

### RESEARCH_LOG_paper.md

- 2026-08-21 — the pipeline created  `archive/sessionLogs/RESEARCH_LOG_paper.md:6`
- 2026-08-21 (cont'd) — refining the two Argentina figures  `archive/sessionLogs/RESEARCH_LOG_paper.md:17`
- 2026-08-22 — the second arm: US / France / UK  `archive/sessionLogs/RESEARCH_LOG_paper.md:54`
- 2026-08-24 — the ESC leg through all three stages, and the appendix rewritten  `archive/sessionLogs/RESEARCH_LOG_paper.md:79`
- 2026-08-24 — the counterfactual convention changed under the pipeline  `archive/sessionLogs/RESEARCH_LOG_paper.md:102`
- 2026-08-24 (cont.) — stage (0), and the Argentina arm re-run end to end  `archive/sessionLogs/RESEARCH_LOG_paper.md:127`
- 2026-08-24 (cont.) — cleanup  `archive/sessionLogs/RESEARCH_LOG_paper.md:152`
- 2026-08-25 — a two-calibration sweep behind `ARG_LOG_FourInOne`, and the guards that now stop it  `archive/sessionLogs/RESEARCH_LOG_paper.md:159`
- 2026-08-25 (cont.) — the builders reconciled with hand edits to the draft  `archive/sessionLogs/RESEARCH_LOG_paper.md:192`
- 2026-08-27 — common X leads, and one builder makes both variants  `archive/sessionLogs/RESEARCH_LOG_paper.md:210`
- 2026-08-27 — three panels instead of one, and an inverted axis that was right by parity  `archive/sessionLogs/RESEARCH_LOG_paper.md:231`
- 2026-09-08 — a shared pre-reform row that was only shared in two of its three columns  `archive/sessionLogs/RESEARCH_LOG_paper.md:255`
- 2026-09-08 (later) — s/Y everywhere, changes against each ρ's baseline, and two figures redrawn  `archive/sessionLogs/RESEARCH_LOG_paper.md:286`
- 2026-09-08 (writing session) — Table 3 gets one pre-reform row and a "Change in savings rate" column  `archive/sessionLogs/RESEARCH_LOG_paper.md:316`
- 2026-09-08 (evening) — the corrected Argentina pass landed and the Argentina prose was re-read  `archive/sessionLogs/RESEARCH_LOG_paper.md:331`
- 2026-09-10 — table notes follow RKB's online edits; f(theta*) computed; tax targets in the calibration table  `archive/sessionLogs/RESEARCH_LOG_paper.md:341`
- 2026-09-11 — the leisure row leaves the paper, the ESC figure gains hours and goes 2×2, a UK wedge table  `archive/sessionLogs/RESEARCH_LOG_paper.md:357`

### RESEARCH_LOG_root.md

- 2026-07-10 — repo conventions established  `archive/sessionLogs/RESEARCH_LOG_root.md:7`
- 2026-08-05 — log cadence and docstring density  `archive/sessionLogs/RESEARCH_LOG_root.md:13`
- 2026-08-06 — the condensation template  `archive/sessionLogs/RESEARCH_LOG_root.md:20`
- 2026-08-10 — a copied bug, and the test class that would have caught it  `archive/sessionLogs/RESEARCH_LOG_root.md:26`
- 2026-08-10 (cont'd) — the docs are downstream of the code  `archive/sessionLogs/RESEARCH_LOG_root.md:42`
- 2026-08-10 (cont'd) — reuse that is silently approximation  `archive/sessionLogs/RESEARCH_LOG_root.md:62`
- 2026-08-11 — nested solves, and writing a repeated finding once  `archive/sessionLogs/RESEARCH_LOG_root.md:75`
- 2026-08-19 — a third cause for "the outer solver stalls", and a Windows output trap  `archive/sessionLogs/RESEARCH_LOG_root.md:100`
- 2026-08-19 (cont'd) — re-deriving what was built on a defect; a shock-experiment pattern  `archive/sessionLogs/RESEARCH_LOG_root.md:114`
- 2026-08-19 (cont'd) / 2026-08-20 — a fix keyed to where a defect was found  `archive/sessionLogs/RESEARCH_LOG_root.md:138`
- 2026-08-20 (cont'd) — a shared test harness and a repo-wide runner  `archive/sessionLogs/RESEARCH_LOG_root.md:164`
- 2026-08-21 — a paper pipeline, and a normalisation mistaken for a result  `archive/sessionLogs/RESEARCH_LOG_root.md:184`
- 2026-08-21 — a module documented before it was coded  `archive/sessionLogs/RESEARCH_LOG_root.md:224`
- 2026-08-22 — a second pipeline arm  `archive/sessionLogs/RESEARCH_LOG_root.md:254`
- 2026-08-24 — endogenous `θ`  `archive/sessionLogs/RESEARCH_LOG_root.md:282`
- 2026-08-24 — a calibration target's units  `archive/sessionLogs/RESEARCH_LOG_root.md:309`
- 2026-08-24 — repository cleanup  `archive/sessionLogs/RESEARCH_LOG_root.md:325`
- 2026-08-25 — a published figure built from two calibrations  `archive/sessionLogs/RESEARCH_LOG_root.md:349`
- 2026-08-25 — the num docs rebuilt as public technical notes  `archive/sessionLogs/RESEARCH_LOG_root.md:371`
- 2026-08-27 — a pinned parameter is pinned by the LAST refresh, not the last one you can see  `archive/sessionLogs/RESEARCH_LOG_root.md:406`
- 2026-09-08 — the baseline savings rate is a prediction, not a row; and a zip round trip to Overleaf  `archive/sessionLogs/RESEARCH_LOG_root.md:435`
- 2026-09-08 — the paper rebuilt as four sections, α = 0.35 launched, and two constants that were data  `archive/sessionLogs/RESEARCH_LOG_root.md:466`
- 2026-09-08 (writing) — a style guide, the numerical section, the OECD pass, and two checks that changed the record  `archive/sessionLogs/RESEARCH_LOG_root.md:498`
- 2026-09-08 (evening) — a converted datum is a stale datum: the tax target moved with α  `archive/sessionLogs/RESEARCH_LOG_root.md:555`
- 2026-09-08 (late) — Overleaf by git after all  `archive/sessionLogs/RESEARCH_LOG_root.md:572`
- 2026-09-10 — first pull from Overleaf by git; RKB's table edits moved into the builders  `archive/sessionLogs/RESEARCH_LOG_root.md:586`
- 2026-09-11 — one to-do file  `archive/sessionLogs/RESEARCH_LOG_root.md:634`

### RESEARCH_LOG_US.md

- 2026-08-21 — documentation, written before any code  `archive/sessionLogs/RESEARCH_LOG_US.md:7`
- 2026-08-21 (cont'd) — code, and the ρ sweep  `archive/sessionLogs/RESEARCH_LOG_US.md:31`
- 2026-08-22 — France/UK (`ModelFR`), the counterfactuals, and the paper pipeline  `archive/sessionLogs/RESEARCH_LOG_US.md:68`
- 2026-08-23 — endogenous `θ`: the leaded choice under a deadweight wedge  `archive/sessionLogs/RESEARCH_LOG_US.md:125`
- 2026-08-23 (cont.) — CRRA, and the permanent choice  `archive/sessionLogs/RESEARCH_LOG_US.md:170`
- 2026-08-24 — the true leaded CRRA solution (`LeadedCRRA2D`)  `archive/sessionLogs/RESEARCH_LOG_US.md:217`
- 2026-08-24 — every US counterfactual becomes a new equilibrium path, read at 2020  `archive/sessionLogs/RESEARCH_LOG_US.md:243`
- 2026-08-25 — num docs restructured (detail in the root log)  `archive/sessionLogs/RESEARCH_LOG_US.md:300`
- 2026-08-27 — the income-distribution counterfactual holds θ, and a pin that did not hold  `archive/sessionLogs/RESEARCH_LOG_US.md:310`
- 2026-08-27 — the ESC leg gains the common-X variant, and loses the flat spec  `archive/sessionLogs/RESEARCH_LOG_US.md:334`
- 2026-09-08 — a forced failure that did not fail  `archive/sessionLogs/RESEARCH_LOG_US.md:371`
- 2026-09-11 — the income-distribution shock carried France's productivity level, not just its profile  `archive/sessionLogs/RESEARCH_LOG_US.md:380`

## Findings, long form

- `findings_longform.md`: the full `notes/crossCuttingFindings.md` as of 2026-09-11, with every
  measurement and addendum. Same numbering as the live file.

## Notes

- `notes/informalSavings_results.md`: the Argentina ρ sweep, the universalisation shock, the
  decomposition, the `(ε, θ)` grid and the anchor history (2026-08-25).
- `notes/us_measurements.md`: US ρ = 1 result tables and validation against the paper (vector-X vintage).
- `notes/todo_paperRewrite.md`: the 2026-09-08 paper rewrite plan, closed; survivors in `notes/TODO.md`.
- `notes/todo_escPermanentTiming.md`: the permanent-timing fix, closed; the reruns are `notes/TODO.md`
  items 10–11.
- `notes/numAppendix_analytical_planning.md`: the 2026-08-25 inventory behind the `informalAnalytical`
  numerical notes, delivered in the 2026-08-25 restructure.
- `notes/figs_inspiration.md`: matplotlib/seaborn snippets from the prior implementation.

## README snapshots (pre-cut, 2026-09-11)

- `readmes/<module>_README_2026-09-11.md` for `root`, `US`, `InformalSavings`, `informalAnalytical`,
  `paper`, `gridsearch`: the long versions with every measurement the live READMEs now only point to.
