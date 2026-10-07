# Archive index

History of the project, kept out of the way of daily work. `.rgignore` keeps `archive/` out of default
searches, so a plain Grep will not see it: read a file by path when a live file points here, or search it
explicitly (Grep with `path: archive`, or `rg --no-ignore`). Never restate archive content into a live file;
link to it. Two cuts filled it: 2026-09-11 (the first context reset) and 2026-10-07 (the repo cut to the paper
as it stands: every session-log entry to that date, the closed notes, plans and agent briefs, retired
diagnostics and superseded results). Numbers in the archived notes are those of their date; the paper,
`results/` and the module READMEs are current.

## The paper's decisions, by theme

Where the reasoning behind each choice the paper rests on is written down.

**Argentina's calibration (section 5, appendix D)**
- The capital-output ratio (3.23 in 2010) as β's target, not the savings rate: `notes/argentina_calibrationTarget.md`
  (2026-08-24); finding #12.
- α = 0.35, the formal sector's capital share net of mixed income (Gollin), with the tax target derived from
  spending: `notes/argentina_alphaSensitivity.md` (2026-09-08).
- Common X in the main text, vector X_i as the twin: `notes/argentina_commonX_vs_vectorX.md` (2026-09-11); the
  informal targets' scaling, InformalSavings log 2026-09-11.
- The pre-reform ε from the first formal quartile (the minimum pension's type) and γ₀ = 32% of all households
  (TODO C8): root log 2026-10-06 (late evening, night) and 2026-10-07; InformalSavings log 2026-10-06 (night).

**The rich economies (section 6, appendix E)**
- Common X for the U.S., France and the UK: `notes/us_commonX_vs_vectorX.md` (2026-09-10); one hours unit
  across countries, US log 2026-09-12; finding #15.
- France's hours corrected, France regrouped at the UK's cuts, the UK as host: root log 2026-09-22 (the data
  caveats are live in `data/README.md`).
- Every counterfactual a new equilibrium path read at 2020: US log 2026-08-24.

**The endogenous design (section 7, appendix C)**
- Why the design wedge gave way to the size-scaled cost, with the alternatives weighed (a leak in the
  dispersion, a formality margin, an insurance motive, a contribution ceiling): `notes/esc_inequalityChannel.md`
  (2026-09-24); the execution plan `notes/plan_escSizeLeak.md`; the pilots `pilots/escSizeLeak_2026-09-24/` and
  `pilots/escSizeLeak_S4_2026-09-25/`; finding #17. The literature behind the cost is live:
  `notes/paper_costLiterature.md`.
- The counterfactuals across ρ under the earlier proportional cost: `notes/esc_experiments_acrossRho.md`
  (2026-08-27).
- The exact 2-D CRRA recursion as the published method: US log 2026-08-24 and 2026-09-11.
- The CRRA design chosen at frozen savings shares (TODO C6): the problem `notes/esc_crraDesignChoiceProblem.md`,
  the briefs `notes/brief_designChoicePilot_2026-10-02.md` and `notes/brief_designChoiceProduction_2026-10-02.md`,
  the pilot's report `pilots/designChoice_2026-10-02/report.txt`, its driver `code/US/pilotDesignChoice.py`;
  finding #19.
- Frisch robustness (ξ = 0.2, 0.3, 0.4): US log 2026-09-30.
- The stakes decomposition that showed the leaded choice needs a cost: `code/US/thetaStakes.py`,
  `results/diagnostics/thetaStakes.csv`; US log 2026-08-23.

**The numerical method (section 4, the technical note)**
- Tax candidates tested and ranked at frozen shares (TODO C7), and the equilibrium test's one-cell clause:
  `notes/brief_informalFrozenSelection_2026-10-02.md`, `notes/brief_equilibriumTestCell_2026-10-02.md`; the
  gridsearch, US and informal logs of 2026-10-02; finding #18.
- The final run and its reading, one equilibrium and no fallback at every counted state:
  `notes/todo_finalRun_2026-10-02.md`; the run logs `logs/finalRun1002/` and `logs/finalRunC8/` (gitignored,
  kept when `logs/` was pruned on 2026-10-07).
- Stationary against date-specific policy functions (section 4's footnote): root, paper and module logs of
  2026-09-12.
- `InformalSavings`' departures from the `num_*.tex` specs, with the measurement behind each live setting:
  `notes/informalSavings_numericalDeviations.md`; the ρ ≈ 0.7 pocket and the ρ = 1 boundary:
  `notes/informalSavings_resolvedIssues.md`, the diagnostics in `code/InformalSavings/`; the Argentine results
  of 2026-08-25: `notes/informalSavings_results.md`.

**The paper and the online appendix**
- Proposition 2's effect of ε, checked by derivation: `notes/prop2_epsilonCheck.md` (2026-10-01).
- The 2026-09-08 rewrite plan `notes/todo_paperRewrite.md`; the 2026-09-30 presentation plan and its gates,
  `notes/paper_presentationPlan.md` and `notes/paper_gate1.md` to `paper_gate3.md` (retired 2026-10-07).
- The appendix split and the online appendix (options, form, decisions O1 to O8, the open items as of
  2026-10-07): `notes/paper_onlineAppendix.md`; the build contract `notes/brief_onlineAppendix_2026-10-06.md`.
- Figure 1 rebuilt from its sources: paper log 2026-09-30.

## Session logs

`sessionLogs/RESEARCH_LOG_<log>.md`, one per live log, oldest first: verbatim through 2026-09-11, then a heading
`# Entries 2026-09-11 to 2026-10-07` and the entries moved on 2026-10-07. Run logs under `logs/` that the
entries cite were deleted on 2026-10-07, except `logs/finalRun1002/` and `logs/finalRunC8/`. One line per
entry: title, then `file:line`.

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
- 2026-09-11 — the agent plan executed: exact CRRA ESC solver, two-part pipeline, variant twins in both arms  `archive/sessionLogs/RESEARCH_LOG_root.md:662`
- 2026-09-11 — context reset  `archive/sessionLogs/RESEARCH_LOG_root.md:673`
- 2026-09-12 — one hours-unit convention, and common X in both arms  `archive/sessionLogs/RESEARCH_LOG_root.md:686`
- 2026-09-15 — the draft says common X by saying nothing, and a pull no longer needs --force  `archive/sessionLogs/RESEARCH_LOG_root.md:700`
- 2026-09-22 — the UK exercise, France's hours corrected, and the paper's tables moved to appendix E  `archive/sessionLogs/RESEARCH_LOG_root.md:712`
- 2026-09-24 — the size-scaled leak replaces the design wedge (branch `esc-sizeLeak`, P1)  `archive/sessionLogs/RESEARCH_LOG_root.md:725`
- 2026-09-25 — `esc-sizeLeak` closed out and on Overleaf for review; the merge waits for MGE  `archive/sessionLogs/RESEARCH_LOG_root.md:740`
- 2026-09-29 — section 7.2 rewritten: the cost as a loss on margins the model lacks  `archive/sessionLogs/RESEARCH_LOG_root.md:750`
- 2026-09-29 — the OECD appendix split in three; the UK as host under the chosen design  `archive/sessionLogs/RESEARCH_LOG_root.md:762`
- 2026-09-30 — the paper rewrite planned (P2); `esc-sizeLeak` merged; Opus 5.5 agent types  `archive/sessionLogs/RESEARCH_LOG_root.md:774`
- 2026-09-30 — paper rewrite session 1: section 7 drafted, `checkPaper.py`, four agents reported  `archive/sessionLogs/RESEARCH_LOG_root.md:786`
- 2026-09-30 — paper rewrite session 2: sections 2–6 cut by four writers, gate 1 follow-ups closed, pushed for gate 2  `archive/sessionLogs/RESEARCH_LOG_root.md:803`
- 2026-09-30 — paper rewrite session 3: the framing by one hand, C1's referee pass, pushed for gate 3  `archive/sessionLogs/RESEARCH_LOG_root.md:819`
- 2026-10-01 — the introduction's last two parts settled, proposition 2's ε claim replaced  `archive/sessionLogs/RESEARCH_LOG_root.md:835`
- 2026-10-02 — sections 3–4 tightened with RKB; the CRRA design solver moves a predetermined state  `archive/sessionLogs/RESEARCH_LOG_root.md:849`
- 2026-10-02 (later) — the selection rule of the technical note rebuilt at frozen predetermined states  `archive/sessionLogs/RESEARCH_LOG_root.md:861`
- 2026-10-02 (evening) — the CRRA design layer decided by pilot and made production; both pipeline arms restarted  `archive/sessionLogs/RESEARCH_LOG_root.md:873`
- 2026-10-03 — the final run read, the paper rebuilt on it, both Overleaf projects pushed  `archive/sessionLogs/RESEARCH_LOG_root.md:885`
- 2026-10-06 — session 4: the appendix split and the online appendix as a Quarto site with a print edition  `archive/sessionLogs/RESEARCH_LOG_root.md:898`
- 2026-10-06 (afternoon) — section 6's calibration as Argentina's with exceptions; fig:US:overview redrawn  `archive/sessionLogs/RESEARCH_LOG_root.md:909`
- 2026-10-06 (evening) — sections 5 and 6 with RKB: section 6's results lead with its figure; tables 4–5, F.1–F.2 and G online  `archive/sessionLogs/RESEARCH_LOG_root.md:920`
- 2026-10-06 (late evening) — section 5's sources and calibration items; the online appendix read and revised  `archive/sessionLogs/RESEARCH_LOG_root.md:933`
- 2026-10-06 (night) — C8 decided: ε from the first quartile, γ₀ = 32% of all households; the Argentine arm re-solving  `archive/sessionLogs/RESEARCH_LOG_root.md:948`
- 2026-10-07 — the C8 run read: the paper's Argentine numbers on ε = 0.21 and γ₀ = 0.47  `archive/sessionLogs/RESEARCH_LOG_root.md:959`
- 2026-10-07 (afternoon) — section 7 restructured: appendix C carries its derivations, the corner leaves the main text, one summary table  `archive/sessionLogs/RESEARCH_LOG_root.md:972`

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
- 2026-09-11 (evening) — Argentina variant twins (C3), R2 launched  `archive/sessionLogs/RESEARCH_LOG_paper.md:404`
- 2026-09-11 — US pipeline split into a main and a pre-publication part; exact CRRA ESC leg  `archive/sessionLogs/RESEARCH_LOG_paper.md:416`
- 2026-09-11 — Argentina rebuilt after the informal-target fix  `archive/sessionLogs/RESEARCH_LOG_paper.md:428`
- 2026-09-12 — Argentina leads with common X (W2); vector-X outputs rebuilt after C4  `archive/sessionLogs/RESEARCH_LOG_paper.md:437`
- 2026-09-12 (evening) — paper prose: the identification argument stated once, W4 reworded  `archive/sessionLogs/RESEARCH_LOG_paper.md:456`
- 2026-09-12 (night) — stationary vs date-specific policies: the check behind sec:numerical's literature paragraph  `archive/sessionLogs/RESEARCH_LOG_paper.md:475`
- 2026-09-15 — the tables and figures stop announcing themselves  `archive/sessionLogs/RESEARCH_LOG_paper.md:490`
- 2026-09-22 — the UK arm, the leisure row back, and eight tables moved to appendix E  `archive/sessionLogs/RESEARCH_LOG_paper.md:503`
- 2026-09-24 — the pipeline reads the `'size'` cost spec (WP3); `US_ESC_Country`, `US_ESC_ScaleWedge`, WP5  `archive/sessionLogs/RESEARCH_LOG_paper.md:516`
- 2026-09-29 — the UK under the chosen design; 54 outputs  `archive/sessionLogs/RESEARCH_LOG_paper.md:529`
- 2026-09-30 — figure 1 rebuilt from its sources (paper rewrite, agent A4); 55 outputs  `archive/sessionLogs/RESEARCH_LOG_paper.md:538`
- 2026-10-06 — row keys, tagged marks, the robustness map (online appendix, package A); 62 outputs  `archive/sessionLogs/RESEARCH_LOG_paper.md:549`
- 2026-10-06 — the online appendix's own exhibits (package B): `tablesOA.py`, `figuresOA.py`, 19 outputs  `archive/sessionLogs/RESEARCH_LOG_paper.md:560`
- 2026-10-06 — the online appendix built and integrated (package S and the main session); 81 outputs  `archive/sessionLogs/RESEARCH_LOG_paper.md:571`
- 2026-10-06 (afternoon) — the calibration table's shared panel; the overview figure's merged rows  `archive/sessionLogs/RESEARCH_LOG_paper.md:582`
- 2026-10-06 (late evening) — the online appendix after a reader's review; captions say "the U.S."  `archive/sessionLogs/RESEARCH_LOG_paper.md:594`
- 2026-10-07 — `US_ESC_Summary`: section 7's table of the endogenous design across counterfactuals  `archive/sessionLogs/RESEARCH_LOG_paper.md:608`
- 2026-10-07 (afternoon) — the online appendix's exhibit texts  `archive/sessionLogs/RESEARCH_LOG_paper.md:616`

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
- 2026-09-11 — Exact CRRA ESC solver published; timing checks as tests and stages  `archive/sessionLogs/RESEARCH_LOG_US.md:424`
- 2026-09-12 — one hours unit across countries (C4)  `archive/sessionLogs/RESEARCH_LOG_US.md:437`
- 2026-09-12 (night) — stationary vs date-specific policy functions (prepub check)  `archive/sessionLogs/RESEARCH_LOG_US.md:450`
- 2026-09-22 — a UK host for the French-characteristics shocks  `archive/sessionLogs/RESEARCH_LOG_US.md:465`
- 2026-09-24 — the `'size'` wedge f(θ, τ) (WP2 and WP4 of `archive/notes/plan_escSizeLeak.md`)  `archive/sessionLogs/RESEARCH_LOG_US.md:478`
- 2026-09-29 — the UK as ESC host (`--host UK`)  `archive/sessionLogs/RESEARCH_LOG_US.md:491`
- 2026-09-30 — Frisch-elasticity robustness of the endogenous design (`runESCxi.py`)  `archive/sessionLogs/RESEARCH_LOG_US.md:501`
- 2026-10-02 — the CRRA design choice moves a predetermined state (found by reading, nothing run)  `archive/sessionLogs/RESEARCH_LOG_US.md:511`
- 2026-10-02 (later) — tax candidates tested and ranked at frozen savings shares (C7)  `archive/sessionLogs/RESEARCH_LOG_US.md:520`
- 2026-10-02 (pilot) — the two frozen-state design layers for the CRRA leaded choice, measured (C6)  `archive/sessionLogs/RESEARCH_LOG_US.md:537`
- 2026-10-02 (production) — the root layer is LeadedCRRA2D's design layer (C6)  `archive/sessionLogs/RESEARCH_LOG_US.md:543`
- 2026-10-02 (evening) — the equilibrium test's cell clause, and two edge cases of the frozen objective  `archive/sessionLogs/RESEARCH_LOG_US.md:550`
- 2026-10-03 — the final run's US arm read (C6 closed)  `archive/sessionLogs/RESEARCH_LOG_US.md:560`

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
- 2026-09-11 (evening) — common-X calibration variant (TODO C3)  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:418`
- 2026-09-11 — the informal targets were mis-scaled; recalibrated  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:430`
- 2026-09-12 — stationary vs date-specific policy functions (prepub check)  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:442`
- 2026-10-02 — tax candidates tested and ranked at frozen savings shares (finding #18)  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:456`
- 2026-10-06 (night) — the pre-reform ε read from the first quartile, γ₀ = 32% of all households (TODO C8)  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:468`
- 2026-10-07 — the C8 run read  `archive/sessionLogs/RESEARCH_LOG_InformalSavings.md:480`

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
- 2026-09-11 — informal targets: hours normalisation and formal-mean denominators  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:170`
- 2026-10-02 — tax candidates tested and ranked at frozen savings shares (finding #18)  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:177`
- 2026-10-06 (night) — `getEps` reads the first quartile by label (TODO C8)  `archive/sessionLogs/RESEARCH_LOG_informalAnalytical.md:189`

### RESEARCH_LOG_gridsearch.md

- 2026-08-04 — `robustRoot.py`  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:6`
- 2026-08-05 — `roots1d.py`  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:12`
- 2026-08-05 (cont'd) — ND grids, and vectorizing the crossing detection  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:28`
- 2026-08-05 (cont'd) — smoothing and gradients; `selectMax` handles NaN  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:48`
- 2026-08-10 — `griddedInterp2D`, and two traps that appear once an interpolant feeds a root-finder  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:54`
- 2026-08-11 — `selectMax` groups ragged columns by feasibility pattern  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:73`
- 2026-08-11 — `continuation.py`; `interp.py` gains kinds and NaN handling  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:88`
- 2026-08-19 — `griddedSmooth1D` gains fixed knots, because adaptive ones are a discontinuity  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:119`
- 2026-10-02 — selection among tax candidates at frozen predetermined states  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:146`
- 2026-10-02 (evening) — the equilibrium test's one-cell form restricted, candidates within a cell merged  `archive/sessionLogs/RESEARCH_LOG_gridsearch.md:159`

## Notes

`notes/`, one line each. Archived 2026-09-11:
- `informalSavings_results.md`: the Argentina ρ sweep, the universalisation shock, the decomposition, the
  `(ε, θ)` grid and the anchor history (2026-08-25).
- `us_measurements.md`: US ρ = 1 result tables and validation against the paper (vector-X vintage).
- `todo_paperRewrite.md`: the 2026-09-08 paper rewrite plan, closed.
- `todo_escPermanentTiming.md`: the permanent-timing fix, closed.
- `numAppendix_analytical_planning.md`: the 2026-08-25 inventory behind the `informalAnalytical` numerical notes.
- `figs_inspiration.md`: matplotlib/seaborn snippets from the prior implementation.

Archived 2026-09-30 and 2026-10-07 (plans and checklists):
- `plan_escSizeLeak.md`: the size-scaled cost's execution plan (derivation, work packages WP1 to WP6, stop
  conditions, checks), branch `esc-sizeLeak`, 2026-09-24; cited by `python/US/test_esc.py`.
- `paper_presentationPlan.md`: the 2026-09-30 plan of the paper rewrite (diagnosis, decisions D1 to D6, five
  sessions with review gates), retired 2026-10-07.
- `paper_gate1.md`, `paper_gate2.md`, `paper_gate3.md`: the gate notes of sessions 1 to 3 of that plan (agent
  reports condensed, RKB's decisions in each DECISIONS block).
- `todo_finalRun_2026-10-02.md`: the checklist and reading of the final pipeline run of 2026-10-03.

Archived 2026-10-07 (the cut to the paper as it stands):
- `argentina_calibrationTarget.md`, `argentina_alphaSensitivity.md`, `argentina_commonX_vs_vectorX.md`,
  `us_commonX_vs_vectorX.md`, `esc_experiments_acrossRho.md`, `esc_inequalityChannel.md`,
  `esc_crraDesignChoiceProblem.md`, `prop2_epsilonCheck.md`: the decision notes of the themes above.
- `informalSavings_numericalDeviations.md`: where `InformalSavings` departs from the `num_*.tex` specs and the
  measurement behind each setting; read before editing those specs (`python/InformalSavings/README.md`).
- `informalSavings_resolvedIssues.md`: the ρ ≈ 0.7 pocket and the ρ = 1 boundary, with the measurements behind
  the live smoother, grid and interpolant settings; cited from code.
- `paper_onlineAppendix.md`, `brief_onlineAppendix_2026-10-06.md`: the online appendix's design and build
  contract (output names, mark and row-key formats, sections and anchors); cited from `tablesOA.py`, `figuresOA.py`.
- `brief_designChoicePilot_2026-10-02.md`, `brief_designChoiceProduction_2026-10-02.md`,
  `brief_equilibriumTestCell_2026-10-02.md`, `brief_informalFrozenSelection_2026-10-02.md`: the `model-coder`
  briefs of 2026-10-02 (their test and measurement labels T1 to T11 and M1 to M8 are the ones the code uses).

## Code

Retired scripts, moved 2026-10-07; not runnable from here (they import their module by path):
- `code/InformalSavings/`: `diagnoseRho07.py` (the ρ ≈ 0.7 pocket, tests 1 to 4), `diagnoseLogCrraBoundary.py`
  and `plotBoundary.py` (the ρ = 1 boundary, `--mode common|production`), `measureGrids.py` (the occupancy
  behind the state-grid anchors), `measureOuterSettings.py` (the outer finite-difference step),
  `plotUniversalShock.py` (the first universalisation figure), `retargetCalibration.py` (the K/Y retarget sweep).
- `code/US/`: `thetaStakes.py` (who gains from a marginal change in θ_{t+1}), `pilotDesignChoice.py` (the
  design-layer pilot's driver, items M1 to M8), `test_createCopyFromt0.py` (the suite of `ModelUS`'s model
  copies, which nothing has called since the counterfactuals became full-horizon paths and `thetaStakes.py`
  retired).

## Results

Outputs no builder reads, moved from `results/` on 2026-10-07 (same relative paths):
- `results/esc/superseded/`: the endogenous design under the earlier `'scale'` wedge, vector-X runs of 2026-09-08.
- `results/esc/escFig1.csv`: the model's own figure 1 (design and tax against ν and inequality), earlier wedge.
- `results/sweeps/superseded/`: the ε–θ grid at ρ = 1 before the K/Y retarget.
- `results/diagnostics/thetaStakes.csv`, `results/calibration/informalSavings_KYGrid.csv`: the outputs of the two
  retired scripts above.

## Findings, long form

- `findings_longform.md`: the full `notes/crossCuttingFindings.md` as of 2026-09-11 (findings 1 to 15), with
  every measurement and addendum. Same numbering as the live file.

## README snapshots (pre-cut, 2026-09-11)

- `readmes/<module>_README_2026-09-11.md` for `root`, `US`, `InformalSavings`, `informalAnalytical`,
  `paper`, `gridsearch`: the long versions with every measurement the live READMEs now only point to.

## Pilots

- 2026-09-24 — the transfer-scaled and size-scaled leak, run from a scratch script that patches
  `Base.fWedge` at runtime (nothing in `python/` changed): `pilots/escSizeLeak_2026-09-24/`
  (`pilotQuadWedge.py`, `pilotUKown.py`, the two result csvs, the json and the log). Quoted in
  `notes/esc_inequalityChannel.md` section 4; the branch `esc-sizeLeak` implemented it
  (`notes/plan_escSizeLeak.md`).
- 2026-09-25 — stop condition S4 of that plan, the two diagnostics at ρ = 2 under `'size'`:
  `pilots/escSizeLeak_S4_2026-09-25/` (the exact 2-D choice at 81 candidates, and the path iteration at the
  exact λ with its planted calibration row; launchers and run logs). Quoted in `writing/US/num_esc.tex`'s
  checks and the 2026-09-24 entry of the US log.
- 2026-10-02 — the two frozen-state design layers for the CRRA leaded choice: `pilots/designChoice_2026-10-02/report.txt`,
  the M1 to M6 tables of `code/US/pilotDesignChoice.py --report` (the per-run csv and npz files were not kept).
