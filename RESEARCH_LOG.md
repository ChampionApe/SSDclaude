# Research log (cross-cutting)

Entries before 2026-09-11 are in `archive/sessionLogs/RESEARCH_LOG_root.md`, indexed in `archive/INDEX.md`.
Format: one entry per session, at most ~10 lines: what changed, why, where to look. A lesson that would
recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

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
separates from the published exact solver by up to 0.09 on the French voting rows at $ho$ = 2, not by the
candidate grid; check 8's $R$ drift (2.9e-3 LOG, 6.6e-3 at $ho$ 0.5) exceeds its 1e-3 tolerance. Merge into `main` and the Overleaf push wait for RKB's
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
