# Research log (cross-cutting)

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_root.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-02 — sections 3–4 tightened with RKB; the CRRA design solver moves a predetermined state

With RKB on `paper-rewrite`, in Overleaf round trips (push, RKB's online edits pulled back): proposition 2 now says
only that the effect of ε is ambiguous, the condition `eq:LOG:epsCondition` lives in appendix B.1, and the text
after it, the introduction's ε sentence and the conclusion's γ₀ clause give the mechanism alone; the
introduction's CRRA paragraph is cut (it misread 7.4). Section 4: the stationary footnote interprets before it
quotes (Argentina's miss is 0.24 p.p., not 0.3); the horizon footnote moved to appendix C; the state paragraph
says why first order conditions (past savings shares held fixed, then substituted) and gives the continuation
derivative and the root/corner selection in words. Reading the CRRA design solver against the code found that
`LeadedCRRA2D` recomputes s_{t-1,i}/s_{t-1} at each candidate design: log is immune, every CRRA endogenous-design
row is exposed, the size is unmeasured. `notes/esc_crraDesignChoiceProblem.md`, TODO C6, `%% TODO-CRRA2D` in section 4.

## 2026-10-01 — the introduction's last two parts settled, proposition 2's ε claim replaced

With RKB, on `paper-rewrite`: the literature block ends at "and take it to the data" (the Tabellini, Cremer-myopia
and Galasso–Profeta 2004 sentence cut, both references now uncited), the Galasso–Profeta 2002 open question opens
the design paragraph, figure 1's note is sources only, and "closed form" became "carries no state" or "a function of
parameters and demographics alone" in the introduction and sections 3 and 4 (section 3's own literature sentence
had said so). RKB's online edits to sections 2 and 3 pulled in three round trips; the infinite-horizon fixed-point
sentence now lives only in section 2. Proposition 2 checked by derivation (`notes/prop2_epsilonCheck.md`): the γ₀
threshold for the effect of ε is not a result, since the formal retirees' loss is γ₀ times the informal gain and
both sides of the FOC derivative vanish together; replaced by the pension-share condition `eq:LOG:epsCondition`,
derived in appendix B.1 with a ν qualifier, and the abstract, introduction, section 3, the section 5 footnote and
the conclusion aligned. Gate 3 decisions G3.1 and G3.5 recorded in `notes/paper_gate3.md`. Open: the proposition's
equal-μ statement (C1's point c, session 4), and section 3's "as in Argentina" rests on the hand-to-mouth variant.

## 2026-09-30 — paper rewrite session 3: the framing by one hand, C1's referee pass, pushed for gate 3

Gate 2's decisions applied (all as recommended; G2.2 puts the Argentine workweek change at one decimal). The
abstract, introduction and conclusion were rewritten by the main session against the final sections 3–7 per
`notes/paper_presentationPlan.md` §3: figure 1 in the introduction with the size–design co-movement as the
fact and the paper's question; the corner as a proved result; the cost's three predictions each tied to figure
1; A3's seven references in the literature block (G3.1 asks whether G1.4 meant none at all); `TODO-W1` resolved
by the rewrite; the conclusion's units fixed and "within 16%" qualified. 2,194 → 1,754, 696 → 495, abstract 248
→ 226 by `checkPaper.py` (its count includes the JEL lines and figure 1's footnote). C1 (`paper-reviewer`, no
notes read) returned eight framing claims, nine number mismatches, a terminology list and three referee points;
the confirmed ones in the main session's files were fixed before the push (no "closed form" claimed, section
7.3's dispersion cuts and the UK's own cost across ρ corrected, three literature links reworded), the
substantive ones (the ρ = 2 exceptions to "inequality moves the design little" and "voting minor", the
compressed ordering, proposition 2's assumptions, appendix D's ε formula) are RKB's calls in
`notes/paper_gate3.md`, session 4's entry point after §8. Pushed to Overleaf after a clean dry-run pull.

## 2026-09-30 — paper rewrite session 2: sections 2–6 cut by four writers, gate 1 follow-ups closed, pushed for gate 2

Four `paper-writer` agents (B1–B4) cut sections 4, 6, 5 and 2–3 per `notes/paper_presentationPlan.md` §3, in the
main checkout on disjoint files (worktree isolation refused again on path case; the types loaded this time):
section 3 1,435 → 1,133, 4 1,485 → 609, 5 1,646 → 1,191, 6 2,910 → 2,017 words by `checkPaper.py`, section 2
edits only. The hand-over held: section 4 carries the horizon sentence, the PEE fixed-point note, section 3's
informal-savings state paragraph and section 7's two "Solution" sentences, and nothing is said twice. The main
session closed `notes/paper_gate1.md` §6: the corner proposition stated in 7.1 (appendix B proof as prose under
a run-in heading), the ξ result as a footnote to 7.4 with the drift sentence qualitative, `tablesUS._escCells`
at three decimals with the seven ESC counterfactual tables rebuilt and 7.4 re-cut, figure 1 on `Figs/OECDdata.pdf`
with the sourced footnote. First-line review passed on all four diffs; each writer's files committed as one
commit after it, per the gate 1 merge rule. Checker clean (`TODO-W1` alone remains, session 3's). Pushed to
Overleaf; the real pull before the push reverted the nine committed section files to the stale online copy (finding #16 extended: after a clean dry run at session start, the pre-push pull is a dry run too), restored with `git checkout` and pushed again, 64 files verified in sync. The reports, six decisions for RKB (a γ₀ clause dropped from proposition 1, three
corrections in section 6 beyond a cut, two rounding calls) and the out-of-scope items for sessions 3–4 are in
`notes/paper_gate2.md`, session 3's entry point after §8.

## 2026-09-30 — paper rewrite session 1: section 7 drafted, `checkPaper.py`, four agents reported

Section 7 rewritten per `notes/paper_presentationPlan.md` §3 into four labelled subsections (`sec:esc:corner`,
`:cost`, `:calibration`, `:results`): the cross-country test and `US_ESC_Country` moved up into 7.3 (its
`\input` left appendix G.2), "within 16%" qualified as specific to ρ = 1, the mild-ageing number and the
"Solution" paragraph out (the latter parked in a `%% TODO-B1` comment for section 4), `%% TODO-PROP3` and
`\todo{xi:}`/`\todo{drift:}` placeholders in; 4,542 → 3,627 words by `writing/checkPaper.py` (new: refs, cites,
inputs, control bytes, words, todos, dashes; clean). The four agents ran in the main checkout, since the
`paper-*` types load only at startup and worktree isolation failed on path case (both in memory): A1 proved
the equal-weights corner (appendix B, `prop:esc:corner`); A2 ran ξ = 0.2/0.4 (`results/esc/escXiRobustness.csv`:
design and drift within 0.002 of ξ = 0.3); A3 added seven verified references; A4 rebuilt figure 1 from its
sources (`python/paper/oecdFigure1.py`): the EPS reproduces only under other concepts than the footnote names,
and its Ginis are WID pre-tax, not WIID; France's LIS year is 2018. Nothing integrated or committed before gate 1;
on RKB's instruction the paper was pushed to Overleaf for the gate 1 read (6 files, the online copy having
been checked unchanged first), and the four stale agent worktrees were removed. The reports and the gate 1
checklist are in `notes/paper_gate1.md`, with a DECISIONS block for RKB's calls (session 2's entry point after §8).

## 2026-09-30 — the paper rewrite planned (P2); `esc-sizeLeak` merged; Opus 5.5 agent types

The whole draft read against the root log, the TODO and the style guide, and `notes/paper_presentationPlan.md`
written: diagnosis (section 7 is 28 % of a 17.5k-word main text while the framing still leads with
tractability), the recommended thesis (design shapes political support, support shapes design, the size of
the system as the link), a section-by-section recommendation with targets, what is missing (a size–design
panel in figure 1, an equal-weights corner proposition, ξ robustness for the chosen design, six references),
eleven inconsistencies, and, after RKB's decisions D1–D6, a five-session work plan with review gates (§8).
`main` fast-forwarded to `77ba943` and `paper-rewrite` opened; P1 closed with its plan restored to
`archive/notes/` and five citers repointed. Agents run on Opus 5.5 through `.claude/agents/paper-*.md`;
worktree isolation waits on `worktree.baseRef: head` in `.claude/settings.json`, RKB's to add.

## 2026-09-29 — the OECD appendix split in three; the UK as host under the chosen design

RKB's layout: old appendix E (`USauxiliary.tex`, deleted) is now `Appendix/CalibrationOECD.tex` (E, five
heterogeneity tables), `US.tex` (F: CRRA, vector X, ESC ageing + the old wedge) and `UKvsUS.tex` (G: French
characteristics on the US and the UK, pinned then chosen design). Every old label kept; `placeins` added and
`\FloatBarrier` precedes every appendix (sub)section so a heading never starts before the previous floats.
Text written around every table block, each number checked against its table or csv. New content: the UK at
its own λ under the chosen design at ρ = 0.5, 1, 2 (exact CRRA, ~5 h per ρ; module logs of the same date),
`UKUS_householdheterogeneity`, two US-vs-UK figures. RKB's calls: layout kept with three placements moved
(US CRRA French table and the US French ESC tables into G; vector X kept whole in F). Committed `e68f269`;
the paper pushed to Overleaf the same evening (17 files updated, `USauxiliary.tex` deleted there).

## 2026-09-29 — section 7.2 rewritten: the cost as a loss on margins the model lacks

The derivation of $f$ used the flat component's *average* implicit tax, but the model already contains its
*marginal* wedge, which is common to all types (through $\Theta_h$, with GHH ruling out income effects), so
a compensated-elasticity reading double-counted and could not produce $\tilde V$. Subsection 7.2 now reads
$f$ as the Harberger loss of the tax component on participation and reporting margins, where the average
wedge matters; it also covers the advance-timing conditions and why only that timing; calibration and
solution moved to open 7.3. Six references added (all checked online), and `model_esc.tex`/`num_esc.tex`
reframed alike; both Overleaf projects pushed. Literature and strategy: `notes/esc_costLiterature.md`.
`notes/plan_escSizeLeak.md` was deleted from the working tree during the session (not moved) and committed
as deleted on RKB's instruction; it is in history at `264cbd7`, and five live pointers to it remain.

## 2026-09-25 — `esc-sizeLeak` closed out and on Overleaf for review; the merge waits for MGE

WP4's CRRA leg finished (S4 diagnosed, exact numbers kept by RKB), WP6 committed, finding #17 accepted. The
paper (`6a86b4…`) and, for the first time through `writing/overleaf.py`, the technical note (`6a4b74…`) were
pushed from the branch; before the note's forced first push every online file was checked against this
repo's history (all 46 were old committed versions). That push exposed a defect: a file renamed only in case
(`Packages.tex` there, `packages.tex` here) would have been deleted on Overleaf; `push` now carries such a
rename (`caseRenames`, tested against a local bare remote) and `CLAUDE.md` names both projects. The merge
into `main` waits for RKB's discussion with MGE (`notes/TODO.md` P1).

## 2026-09-24 — the size-scaled leak replaces the design wedge (branch `esc-sizeLeak`, P1)

Section 7's cost $f(\theta)=\phi+(1-\phi)\theta^p$ attached the deadweight loss to the design label, so a
compressed income distribution cornered the French income row and the US wedge cornered the UK
(`notes/esc_inequalityChannel.md`). Replaced by $f(\theta,\tau)=\exp(-\tfrac12\lambda\tau\tilde V(1-\theta)^2)$,
the Harberger loss of the flat component's implicit taxes (Summers 1989, Disney 2004; Koethenbuerger, Poutvaara
and Profeta 2008), derived in `writing/US/model_esc.tex`; $\theta^\ast = 0.738$ unchanged. Six work packages in
parallel worktrees per `notes/plan_escSizeLeak.md`, D1 to D6 at their defaults. $\lambda$ = 18.24, 8.64, 1.73 at
$\rho$ = 0.5, 1, 2; every counterfactual interior; the joint French row less Bismarckian at every $\rho$; one US
$\lambda$ puts the UK at 0.625 and France at 0.749 (observed 0.560, 1.000), the UK's own $\lambda$ within 16 % of
the US's. The previous wedge stays as `US_ESC_ScaleWedge` (D2). S4 fired: the path-iteration cross-check
separates from the published exact solver by up to 0.09 on the French voting rows at $\rho$ = 2, not by the
candidate grid; check 8's $R$ drift (2.9e-3 LOG, 6.6e-3 at $\rho$ 0.5) exceeds its 1e-3 tolerance. Merge into `main` and the Overleaf push wait for RKB's
read of section 7 (`notes/TODO.md` P1). Per-arm detail in the US and paper logs of the same date.

## 2026-09-22 — the UK exercise, France's hours corrected, and the paper's tables moved to appendix E

Martin's 2026-09-18 Overleaf pass pulled (layout to 12pt/1in/one-and-a-half spacing; his hand edit to the
Argentina calibration note made at its source in `tables.py`). The French-characteristics exercise now runs
on the UK as host: `runShocksUS.py --host UK|UKUS`, France regrouped at the UK's cuts (`FRUK`), six new paper
outputs (45 wired), `app:US:french`. The data came from the old repo's
`SSD/Data/calibration statistics AUG 2025.docx`, which also exposed a transposed digit in France's low-group
hours (1731.91 → 1713.91, corrected on RKB's instruction; France's workweek 35.44 → 35.24, nothing else
moves) and that the UK's own US-percentile regrouping is an Excel linear fit, not data. Paper: tables 7–8
and the four ESC tables to appendix E, now *Rich OECD countries*; the advance and costly first-order
conditions written out; the permanent paragraph cut. Open for MGE: France's voting at the UK cuts
(`notes/TODO.md` D1). Per-arm detail in the US and paper logs of the same date.

## 2026-09-15 — the draft says common X by saying nothing, and a pull no longer needs --force

W2b closed: the permanent corner flips to θ = 1 for ρ ≥ 1.4, so the introduction promises a corner rather
than a *fully Beveridgean* system "under every timing", and the conclusion dropped "too attractive" for the
claim that holds at all three timings. Common X became the paper's silent default — nothing in the main
text names it, each arm points at its vector-X appendix once — and the Argentina calibration was cut from
two pages to four paragraphs, the detail moving to appendix D, now *Calibration — Argentina*. Three
plain-text references went through biblatex, and `app:recursive`, a `\ref` aimed at an online appendix,
became a `\parencite`. Tooling: `writing/overleaf.py pull` now records what it took, so a pull → edit →
push round trip is an ordinary push instead of demanding `--force`. Per-arm detail in
`python/paper/RESEARCH_LOG.md`, the lesson in finding #16; `notes/TODO.md` holds W1 and a trimmed W5.

## 2026-09-12 — one hours-unit convention, and common X in both arms

Two conventions that were per-model became repo-wide. (i) The US models now impose the second
normalisation the Argentina models already did, `sum gamma_i y^x_i = 1` in `addEigenVectors` (TODO C4), so
the hours unit is 1 in every calibration rather than whatever scipy's unit-norm eigenvector returned. It
is the eq (hoursUnit) rescaling, hence equilibrium-neutral: the re-swept vector-X grids reproduce beta,
omega, R, tau, the savings rate and aggregate h to <= 1.6e-13, and the mu_c/mu_US that ModelFR's Gamma_h
rescaling hid in X-bar_c/X-bar_US now sits in lambda. (ii) `config.ARG['commonX'] = True` (TODO W2), so
both arms print one leisure parameter pinned by an observed workweek and treat relative hours as a
prediction; the vector-X calibration table moved to an appendix in each arm. Spending the hours-unit
normalisation made `h̄` and `h` coincide and broke a test asserting they differ, which is finding #15.
Per-arm detail in the US and paper logs of the same date; `notes/TODO.md` now holds two open items, W1
and W2b, both RKB's wording calls.

## 2026-09-11 — context reset

The repo's markdown context had grown to ~400 KB. All six session logs, `notes/archive/`, the 2026-08-25
numerical-appendix planning note and `paper/figs_inspiration.md` moved to a root `archive/` (`git mv`),
with `archive/INDEX.md` listing every log entry by date and title. `.rgignore` keeps `archive/` out of
default searches. `notes/crossCuttingFindings.md` was cut to statement/tell/habit per finding, same
numbers (long form with measurements: `archive/findings_longform.md`); the six READMEs were cut to
orientation, each under ~100 lines, with the pre-cut versions in `archive/readmes/`. `CLAUDE.md` now
carries the size caps. Live paths cited from code (`crossCuttingFindings`, the three InformalSavings
notes, `TODO.md`) did not move; two code comments citing the old root log were repointed. The archived
logs sit in `archive/sessionLogs/`, not `archive/logs/`: `.gitignore`'s `logs/` rule matches any directory
of that name, which both untracks it and hides it from ripgrep.

## 2026-09-11 — the agent plan executed: exact CRRA ESC solver, two-part pipeline, variant twins in both arms

`notes/plan_2026-09-11.md` (deleted at the end of the day, per its own rule) ran end to end: C1, C2, R1, R3,
R4, W1–W3, then C3 and R2. Structural: (i) the US stages (i)/(ii) have a `main` and a `--prepub` part, and
the exact 2-D recursion is the published CRRA ESC method with a `method` column keyed into every CRRA csv
(`python/paper/RESEARCH_LOG.md`); (ii) both arms now carry two calibration variants with headline/twin
outputs (`config.US['commonX']` = True, `config.ARG['commonX']` = False) — for Argentina the variants print
identical results and differ only in the calibration table (`notes/argentina_commonX_vs_vectorX.md`,
decision W2); (iii) finding #14 (a `tail -F` on a pipeline log breaks the ps1's own `Add-Content`). Per-model
detail in the three module logs of the same date; open items for RKB in `notes/TODO.md` (W1, W2, W2b, W4, C4).
