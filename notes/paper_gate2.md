# Gate 2 note: paper rewrite, session 2 (2026-09-30)

For RKB. Session 2 of `notes/paper_presentationPlan.md` §8 is done: the four writers B1–B4 cut sections 2–6, the
main session closed the gate 1 follow-ups of `notes/paper_gate1.md` §6, everything passed the first-line review
(style guide §7, cross-references, numbers against tables, the B1/B4 hand-over) and is committed on `paper-rewrite`
per file, and the paper is pushed to Overleaf for this read; the online copy was unchanged (a real pull before
the push reverted the nine committed section files to the stale online copy, finding #16; restored from the
branch and pushed again, all 64 files verified in sync by a dry-run pull). A gate change comes back as an edit
on the branch. **Record decisions in the DECISIONS block at the end of this file.**

The writers ran in the main checkout with disjoint files (worktree isolation refused again: the session's path
spells `Github`, git's `GitHub`; see the memory note). The checker is clean on the whole draft; two tags remain,
`TODO-W1` in the introduction (session 3) and none of this session's.

Checker, from the repo root: `PYTHONUTF8=1 .venv\Scripts\python.exe writing\checkPaper.py`

## 1. Word counts (checker's, about 10% below the plan's method)

| Section | Before | After | Plan §3 target (×0.9) |
|---|---|---|---|
| 2 Model (B4) | 1,040 | 1,049 | edits only |
| 3 Log-GHH (B4) | 1,435 | 1,133 | 1,300 (1,170) |
| 4 Numerical (B1) | 1,485 | 609 | 600 (540; for this file the plan's count was only 3% above the checker's, so 609 is about 630 by the plan's method) |
| 5 Argentina (B3) | 1,646 | 1,191 | 1,300 (1,170) |
| 6 OECD (B2) | 2,910 | 2,017 | 2,300 (2,070) |
| 7 Endogenous design (main) | 3,627 | 3,703 | 2,800; the increase is the proposition statement and the ξ footnote |

## 2. What to read, section by section

**Section 2 (B4).** Edits only: the horizon sentence and the fixed-point note after the PEE definition are gone
(section 4 carries them); the "analytical/numerical model" naming is gone, section 3 names the two cases; informal
prices are stated once in 2.2 as calibrated ($w^0_t$ the formal wage at the same capital stock without the pension
system, $R^0_t = r_0 R_t$ with $r_0 = 1$, informal savings outside the capital stock), which agrees with section
5's "same return on savings". Section 2 now closes with a hand-off to section 3.

**Section 3 (B4).** Opening corrected (log-GHH is the benchmark of sections 5–7, CRRA the robustness). Both
propositions and every label kept; the closing paragraph on the informal savings state is gone (section 4 has it).
New after proposition 2: inequality is the between-type dispersion of relative labor income, the $\tilde V$ of
section 7, not the Gini of figure 1. **One change to a proposition statement, for your call (G2.1):** part v of
proposition 1 said the effect of $\gamma_0$ on informal savings is ambiguous, while the appendix A proof signs it;
B4's own derivation gives $\epsilon/(1+\gamma_0\epsilon) - \partial \ln s_t/\partial\gamma_0$, unsigned, and the
clause is dropped from the proposition. The proof in appendix A (session 4, D2) still carries the signed claim.
γ̄₀ for Argentina is not stated: appendix B says the threshold has no closed form and `results/` has no
hand-to-mouth sweep.

**Section 4 (B1).** Four paragraphs, no run-in headings: (1) why the policy function is date-specific, the
literature in one sentence, the three cases, backward induction from $T$ (the two initialisations of the old
"Identifying policy functions" paragraph and section 2's horizon sentence and fixed-point note folded in), with
the accuracy footnote at two sentences (0.2 p.p. U.S., 0.3 p.p. Argentina, the design by up to 0.053 and 0.059
against responses of 0.030 to 0.477, all checked against `results/numerical/*_stationaryApprox.csv` and the
ESC tables) and the horizon footnote; (2) the state is at most two scalars, with section 3's informal-savings
state paragraph absorbed here (the ratio written as $s_{t-1,0}/s_{t-1}$, its forward-looking dependence on the
current tax kept, `app:EE:CRRA` and `app:PEE:LOG_s0` kept), the FOC on a tax grid with corners and interior
roots ranked by the reconstructed objective, no displayed candidate set; (3) path and calibration as a nested
fixed point, targets left to sections 5–6; (4) section 7's two "Solution" sentences, then the hand-off. Gone to
the technical documentation: the candidate set, the CRRA fixed-point paragraph, the calibration target list,
and the steady-state-comparison and terminal-period numbers (0.2/1.4 p.p.; 3–11, under 0.7, under 0.1 p.p.),
which live only in `results/numerical` and the module logs. One audit flag (G2.6): the Argentine 0.3 p.p. is an
upper bound on a largest gap of 0.240, as the old footnote had it. If you want the plan's 540: the uniqueness
sentence (−24), the population clause of the horizon footnote (−13), the "holds past savings fixed" clause
(−8), the counterfactual-response comparison in the accuracy footnote (−8), in that order.

**Section 5 (B3).** Opening reframed as the one observed change of design, tested before the counterfactuals.
Calibration in two paragraphs; the ξ ∈ [0.2, 0.4] promise is cut. The reform paragraph kept (1.25 p.p. now
1.2 p.p.). The ε–θ paragraph halved. CRRA in one paragraph; `fig:ARG:EffectOfCRRA` is at the end of appendix D,
label unchanged, pointed at once. The "ρ ∈ [1,2] more plausible" sentence stays for section 7's cross-reference.
The informal-savings "16%" left (no table carries it). Rounding call for the number audit (G2.2): the workweek
change is 0.143 hours in the csv and the text says "about 0.15" to match the table's printed levels.

**Section 6 (B2).** Opening to one paragraph (platform work gone); calibration cut by a third with the vector-X
paragraph as the section's one footnote to `app:US:vectorX`; the two counterfactual tables and paragraphs kept;
French characteristics one paragraph; CRRA one paragraph with the mechanism once; interpretation shorter; the
closing returns to figure 1 and hands off to `sec:esc` and `sec:esc:corner`. The two commented-out blocks are
deleted (`Prescotta1`, `Alesinaa1`, `Blancharda1` are now cited nowhere). The Gini footnote reads: on the
disposable-income Gini of figure 1 the U.S. is 0.42, third of 29 after Mexico and Turkey; France 0.32, the median
(two decimals because the figure's axis is at two). **Three corrections beyond a cut, for your call (G2.3):**
(a) the overview-figure paragraph said pension design "barely registers in hours", but on the figure it is the
largest mover of hours (1.9 hours at ρ = 1), rewritten; (b) the figure note cites each ρ's own baseline rows;
(c) the closing claim that a higher θ "dampens the effects of ageing" is dropped: no table shows it and section
7 finds the chosen design adds a little to the tax response to ageing.

**Section 7 (main session, the §6 follow-ups).** G1.2: the five-line statement of proposition 3 in 7.1 with the
marker gone, merged with the sentence that followed; B2's check narrowed "the calibrations of section 6" to "the
U.S. calibration" (France's propensities 0.810, 0.857, 0.852 are not monotone). The appendix B proof is prose under
`\smalltitle{Proof of proposition ...}` like appendix A's; the CRRA paragraph kept. G1.3: the ξ result is a
footnote to 7.4 (λ = 8.736 and 8.547 at ξ = 0.2 and 0.4 against 8.643, about one percent; the design in 2110 and
under acute ageing unchanged to the third decimal; the tax level moves by about 0.3 p.p. by 2110, all from
`results/esc/escXiRobustness.csv`); the drift sentence is qualitative, both drift placeholders gone. G1.6:
`tablesUS._escCells` prints θ to three decimals, the seven `US_ESC_*`/`UK_ESC_*` counterfactual tables rebuilt with
`build.py --only`, and 7.4 re-cut against them (0.825, 0.817, 0.826; 0.772, 0.708, 0.919; 0.653, 0.687, 0.334;
0.627, 0.667, 0.261). G1.5: figure 1 reads `Figs/OECDdata.pdf`; its footnote is gate 1's proposal, the five
correlations checked against `results/paper/oecdCorrelations.csv`.

## 3. Items the writers found in files outside their scope (nothing edited)

For session 3 (framing):
- Conclusion: "labor supply of about 0.3%" should be about 0.15 hours a week (B3).
- Introduction: "91% of retirees by 2010" has no source in the repo; section 5 says "almost universal" (B3).
- Section 7.4, "Income distribution", repeats the $\tilde V$-versus-Gini point that section 3 now makes; could
  refer back (B4). Optional.

For session 4 (appendices, D2):
- `Appendix/US.tex` line 6 (F.1): drop "The reason for this is the one section \ref{sec:oecd} gives: a higher
  elasticity lowers the young's resistance to taxation, ... counts for less." Section 6 now gives it once (B2).
- `Appendix/UKvsUS.tex` line 8: "1.6 p.p. at ρ = 0.5" should read 1.5 (unrounded 1.5455) (B2).
- Appendices F.3 (`US.tex` line 90) and G.2 (`UKvsUS.tex` lines 39, 47) quote designs at two decimals against
  tables that now print three (G1.6).
- `Appendix/EconomicEquilibrium.tex`, proof of part v: "an increase (decrease) in θ (γ₀) increases $s_{t,0}$"
  signs the γ₀ effect that G2.1 drops from the proposition; fix or drop (B4). Optional: line 75 could say
  "with $r_0 = 1$ (section 2)".
- Appendix D: line 30 still promises ξ between 0.20 and 0.40 as robustness; line 42 says `table:Arg:Calib`
  reports relative hours against the survey, which it does not; its opening could mention the CRRA figure now at
  its end (B3). Appendix E's France paragraph has no survey year (2018 LIS, now in section 6) (B2).

For RKB (a possible calibration mismatch, text unchanged, B3): section 2 counts informal households per formal
household (formal types sum to one; the average benefit is divided by $1+\gamma_0\epsilon$), so $\gamma_0 = 0.32$
is about 24% of the population, while section 5 and appendix D describe it as the 32% share of retirees on the
basic pension, which would be $\gamma_0 \approx 0.47$.

Minor, `python/paper`: `ARG_CRRA_LOG.pdf` draws a title inside the image that repeats the tex caption
(`figures.argCrraLog`) (B3).

## 4. Next: session 3 (plan §8)

Abstract, introduction and conclusion by the main session against the final sections 3–7, with A3's references
(G1.4: uncited until then) and A4's figure and footnote (in place); `TODO-W1` resolves there; then C1, the
referee pass. Gate 3 pushes to Overleaf for MGE.

## DECISIONS (RKB)

Fill in below; a blank line means "as recommended".

- **G2.1 Proposition 1, part v.** The γ₀ clause dropped (recommended: accept; appendix A's proof aligned in
  session 4).
  RKB:
- **G2.2 Rounding of the Argentine workweek change.** "about 0.15 hours" against the 0.143 in the csv
  (recommended: keep, it matches the table's printed levels; the style guide's one decimal would give 0.1).
  RKB:
- **G2.3 Section 6's three corrections.** (a) hours and pension design; (b) the figure note; (c) the "θ dampens
  ageing" claim dropped (recommended: accept all three).
  RKB:
- **G2.4 Sections 2–6 as cut.** Accept, or name the paragraphs to revisit.
  RKB:
- **G2.5 Section 7 at 3,703 words.** Stop here (recommended), or cut 7.2/7.4 toward 2,800 in session 5.
  RKB:
- **G2.6 Section 4's accuracy footnote.** "0.3 p.p. in Argentina" as an upper bound on 0.240 (recommended:
  keep as the bound the old text stated; strict rounding would say 0.2), and 609 words or the four cuts to 540
  (recommended: stop at 609).
  RKB:
