## A. Endogenous choice formulation -- derive and and compute

### A1. Variant selection

* We want to present model results with different versions of the endogenous design. Think carefully about 2-3 variants to include in the paper. They could be variants of our preferred specification. Our specified variant (unless we discover something much better): Similar to our current version, only with a linear term that allows us to calibrate France with the corner.
* For each variant, add the formal derivation (as in the current appendix C).
* Make sure that no variant introduces big changes to the code base; we should be able to use the same solution methods only pass slightly different functional forms.

### A2. Code and compute

For each variant of the endogenous pension design from above, but only for ρ = 1, do the following:

* Define new model variants in python.
* Calibrate US, France, and UK model (with US income groups) with endogenous choice. If the variant does not permit the French version, drop this.
* Experiment 1: Take US calibration of λ and apply in France + UK models.
* Experiment 2: Ageing, income distribution, and French voting patterns in the U.S. model. Compare results with exogenous theta versus endogenous, and across variants.

For our preferred specification, calibrate U.S. with endogenous design and carry out experiments from 2. This is the basis for comparing.

## B. Outline for the endogenous pension design section

Short opening paragraph.

### The deadweight cost of redistribution

* **First paragraph**. Why the model from previous sections does not allow for an interior solution. The diagnosis: The model misses a mechanism that makes flat, redistributive benefits more costly than earnings-related ones.
* **Second part.** What reasons does the literature find that can explain that flat benefits are most costly, beyond what our model already holds? Ingredients this part should hold (not sure of the best ordering, yet).
    1. The implicit tax: Explain and show the implicit tax from flat benefits. The idea follows Summers (1989). Explain that our model already holds an intensive margin response in labor supply to changes in pension design and rates, but no extensive margin.
    2. Literature paragraph: (i) Taxes associated with losses from generalized taxation (Harberger loss, Okun's leaky bucket). (ii) Evidence confirming "flat benefits as an implied tax" also associated with external margin losses e.g. from participation/underreporting of wages (Disney 2004, Kumler et al. 2020). (iii) Extensive versus intensive margin losses associated with taxes (Saez 2002, Kleven and Kreiner 2006, Chetty et al. 2011, Saez et al. 2012). (iv) The size of the system's design (Conde-Ruiz and Profeta 2007, Koethenbuerger et al. 2008).
    3. Present variants from task A1.

### Results 
* **Third part.** If it is meaningful, compare briefly how calibration parameters compare across variants. Also, if meaningful, compare how calibration across countries vary, e.g. relying on results from **Experiment 2** from task A2. Review this critically and delegate the rest of the material to a subsection G.1. (appendix G dedicated to additional details on the endogenous design section). In my view, we may want to skip this entire part of just make it a paragraph in the fourth part, decide when materials are in.
* **Fourth part.** Present results from experiment 2 of task A2. The most important results come here. Appendix G.2 should have what does not come in the main section. We can think about either leading with the preferred specification in a figure, and only spend a paragraph on other variants. Or we can include the other variants on more equal footing. I lean towards the first option, but decide when results are in.
* **Fifth part.** The role of ρ. Probably keep this to one paragraph and leave the rest for appendix G.3.

---

## C. Execution plan (written 2026-10-08 by the session; RKB's sketch above is the brief)

Everything below is executed autonomously; RKB reviews the result. Decisions taken by the session are
listed in C.1 so they can be reversed; the phases in C.2 run in the order given, the agents in C.3, the
gates in C.4. Briefs for the agents are `notes/brief_escVariants_*_2026-10-08.md`; the theorist's note is
`notes/esc_variants.md`. When the work closes, this plan and the briefs move to `archive/notes/`.

### C.1 Decisions (RKB to confirm or reverse)

1. **The three variants.** One general form, the loss share to first order
   $1-f \approx \tau_t\tilde V(1-\theta_t)\left[\lambda_1 + \tfrac12\lambda_2(1-\theta_t)\right]$, with
   $f = \exp\{-\tau_t\tilde V(1-\theta_t)[\lambda_1 + \tfrac12\lambda_2(1-\theta_t)]\}$:
   - **Q** (quadratic; the current paper): $\lambda_1 = 0$. Code spec `'size'`, untouched.
   - **L** (linear; Okun's leak proper, a constant share of every unit carried): $\lambda_2 = 0$. Spec `'sizeL'`.
   - **LQ** (linear-quadratic; the preferred one): both. Parametrised as a scale and a shape,
     $\lambda_1 = \lambda\kappa$, $\lambda_2 = \lambda$, so $\ln f = -\lambda\tau\tilde V(1-\theta)[\kappa + \tfrac12(1-\theta)]$;
     $\kappa = 0$ is Q. Spec `'sizeLQ'`, $\kappa$ in `db['wedgeKappa']`.
   All three are proportional ($A = f\theta$, $B = f(1-\theta)$), so $\theta^{\ast}$ stays the data's own and
   the tax condition's factor is still $1 + \ln f$ ($\ln f$ linear in $\tau$). The marginal cost of the first
   unit of redistribution is positive under L and LQ, which is what lets an electorate choose the
   Bismarckian corner.
   **Amended after phase A (gate 1, 2026-10-08):** the linear term is weighted by the amount the flat
   component carries, $M \equiv \sum_i\gamma_i|y_i-1|$ (`notes/esc_variants.md` (A.5), (A.8)), the quadratic
   term by $\tilde V$ as before:
   $\ln f = -\tau_t(1-\theta_t)\big[\lambda_1 M + \tfrac12\lambda_2\tilde V(1-\theta_t)\big]$. Each term carries
   the weight its own derivation gives (Okun's leak on the amount carried; Harberger's loss on the squared
   wedges). The U.S. and the UK have the same $M/\tilde V$ (1.32, 1.31), so their calibrations are the same
   function under either weight; France's is 1.93, so its linear term at a common parameter is 1.47 times
   larger under $M$, which is the difference between France interior under every variant ($\tilde V$: the
   U.S. design caps $\lambda_1$ at 2.26 against France's threshold 2.55) and France's corner reachable
   ($M$). The $\tilde V$-weighted LQ stays in the code as `'sizeLQV'` for the record.
2. **The linear term scales with $\tau\tilde V$ like the quadratic one**, rather than as Okun's proportional
   leak would literally have it (a loss linear in the amount carried is, as a share of revenue, independent
   of $\tau$ and weighted by $\sum_i\gamma_i|y_i-1|$). Reason: in the corner condition at $\theta = 1$ the
   redistributive stake of the young is to first order proportional to $\tau$, so a $\tau$-free linear leak
   makes a larger system *harder* to put at the corner, against the cross-section (France, the largest
   system, is the corner); with the common scaling the size channel works for the corner, which is the
   paper's existing reading of what separates France from the UK. The theorist verifies this (phase A) and
   the paper owns the choice in a footnote with the alternative's cost. If the theorist overturns it, the
   code change is one line in `fWedge` and the plan proceeds with the alternative.
3. **Calibration.** Q and L: one parameter per country on its own design (the U.S. $\lambda$; the UK's own;
   France's own under L is the *threshold* $\underline\lambda$ at which its choice reaches the corner, a
   bound rather than a point). LQ: $(\lambda, \kappa)$ jointly on two designs, the U.S. (0.738) and the UK
   (0.560) at the UK's own income cuts, France the out-of-sample prediction (what section 7.2's footnote and
   TODO W9 proposed). Fallback if no $\kappa \geq 0$ puts the UK on its design: pin $\kappa$ by France's corner
   (the smallest $\kappa$ at which France chooses $\theta = 1$ under $\lambda_{US}(\kappa)$) and the UK becomes
   the prediction. The other pinning is run as a robustness row either way (`--tag _kappaFR`).
   **Expectation after phase A:** the UK pins a small linear term ($\kappa \approx 0.11$) and France is then
   predicted interior (about 0.78 under the $M$ weight, 0.73 under $\tilde V$); France's corner pins
   $\kappa \approx 1$, at which the UK is predicted at about 0.34. Neither weight reconciles the UK and
   France at one $(\lambda,\kappa)$; the ordering holds under every pinning. The paper's row is the UK
   pin; the France pin is appendix G.1's "what France's corner takes" row. L is knife-edge (the UK at
   $\theta = 0$, every U.S. counterfactual a corner) and is presented as the limit, in one paragraph.
4. **The UK of the paper stays at its own income cuts** (as section 7.2 has it; TODO D3's caveat on the
   U.S.-cuts regrouping). RKB's sketch says "UK model (with US income groups)": the UK at the U.S.
   percentiles is computed for every variant and printed in appendix G.1, not in the main text. Reverse by
   swapping the two in `tablesUS.escVariants` if RKB prefers the U.S. cuts.
5. **$\rho \neq 1$ only under Q**, as RKB's sketch says (the existing exact CRRA rows). Section 7's closing
   paragraph on $\rho$ therefore reads the quadratic cost's numbers and says so; appendix G.3 holds the
   $\rho$ exhibits. The CRRA leg for LQ at $\rho = 0.5, 2$ (about 3 h, two $\rho$ in parallel, plus the UK
   host) is *prepared* (the drivers accept the new specs, the commands and brackets go into TODO R6) and not
   run; running it would let `config.US['esc']['spec']` become `'sizeLQ'` throughout.
6. **Appendix G becomes "Endogenous design: additional results"** (G.1 calibration across variants and
   countries, G.2 counterfactuals across variants, G.3 the role of $\rho$); the robustness map moves to a
   new appendix H (`Appendix/Robustness.tex` unchanged, one `\input` line added in `main.tex`).
7. **Config carries two specs until decision 5 is revisited**: `US['esc']['spec'] = 'size'` drives every
   $\rho$-dependent exhibit; `US['esc']['paperSpec'] = 'sizeLQ'` and `US['esc']['variants']` drive the
   $\rho = 1$ variant exhibits. Builders say which they read.
8. **Version control.** Local commits at the end of phases B, C+D and W+R, staged by path; no push to
   GitHub, no Overleaf push, no site publish. RKB pushes after review (the Overleaf sequence in
   `notes/`'s memory: dry-run, pull, `push paper --force`).
9. **The UK as host** (`--host UK`, the online appendix's OA.4.3) is rerun for L and LQ at the UK's own
   parameter; cheap under LOG.

### C.2 Phases

**Phase A, derivation (model-theorist, Fable max; parallel with B).** Brief
`notes/brief_escVariants_theory_2026-10-08.md`. Deliverable `notes/esc_variants.md`: the general form and
its reading (Okun's leak with a constant and a rising part; Harberger for the quadratic); what each
variant changes in appendix C's equilibrium (nothing beyond the substitution; the factor $1+\ln f$;
identification); the design condition and the **corner condition at $\theta = 1$ under log preferences**,
derived explicitly (the young's terms, the retirees' hours term, the tax response), stated as a bound on
$\lambda_1$, with the first-order cancellation of $\tau$ and the comparative statics in $\tau$, $\tilde V$,
$\nu$, $\mu$; the calibration strategy and the identification of $(\lambda,\kappa)$; the predicted
direction of the UK's design as $\kappa$ rises and of France's corner; what each variant should do to the
three counterfactuals; a tex-ready derivation block for appendix C.2 in the paper's notation; and, at the
top, anything that overturns C.1. Numerics only to confirm an algebraic result.

**Phase B, code (model-coder, Opus xhigh; parallel with A).** Brief
`notes/brief_escVariants_code_2026-10-08.md`. `base.py` (`fWedge`, `dlnfWedge_dτ`, the two specs),
`modelESC.py` (`wedge` with `kappa`, `WEDGE_SPECS`, `WEDGE_BRACKET`, `calibrateWedgeCorner`),
`runESC.py` (`--spec` choices, `--kappa`, `--pinKappa`, the joint calibration `calibrateJoint`,
`stageCalib`/`stageCountry` branches, the new columns), `runESCcrra.py` (accepts the specs; no run),
`collectESCexperiments.py` (`kappa`), a new fast suite `test_escVariants.py` registered in `runTests.py`,
README status and US log. `'size'` bitwise unchanged (the suite's calibrated-$\lambda$ line is the reference).

**Phase C, runs (paper-compute, Opus xhigh; after B).** Brief
`notes/brief_escVariants_runs_2026-10-08.md`. Self-check (`--spec size --stage calib` into a tagged csv
reproduces $\lambda = 8.643207$); `runESC.py --spec sizeL sizeLQ --phi 0.5 --commonX --stage calib path
shocks country`; `--host UK` shocks for both; the `_kappaFR` alternative; `collectESCexperiments.py` for
both hosts; `compareResults.py` to show the `'size'`/`'scale'` rows untouched. Report every number with
its csv row and the checks (one sign change per scan, `targetDrift`, the UK's own $\lambda$ under LQ
reproducing $\lambda_{US}$).

**Gate 1 (session).** Read the numbers; settle the exhibit layout of section 7 and appendix G (RKB's
"decide when materials are in"); confirm or apply the fallback of decision 3; write the builder brief.

**Phase D, pipeline (paper-compute, Opus xhigh; after gate 1).** Brief
`notes/brief_escVariants_pipeline_2026-10-08.md`. `config.py` (`paperSpec`, `variants`, labels),
`datasets.py` (the new columns), `tablesUS.py` (`escVariants` -> `US_ESC_Variants`, `escResults`
generalised across variants, `escVariantsCountry` and `escVariantsShocks` for appendix G),
`figuresOA.escPathPaper` (the three variants' paths), `build.py` registry and `--map`,
`onlineAppendix.py` and `esc.qmd` (a section `esc-variants`), the robustness map's variant rows if that is
a data change; `test_onlineAppendix.py` and `build.py` clean.

**Phase W, writing (after D; four writers in parallel, disjoint files).**
- W1 section 7 (`Sections/EndogenousTheta.tex`): paper-writer-lead, Fable max. RKB's outline B, about
  2,000 words, the preferred specification leading, the other variants in one paragraph, the $\rho$
  paragraph on the quadratic cost's numbers.
- W2 appendix C (`Appendix/EndogenousDesign.tex`): paper-writer-lead, Fable max. C.2 for the general form
  and the three variants from `notes/esc_variants.md`, the corner condition, C.3's design condition
  generalised; C.1 and C.4 untouched unless a label moves.
- W3 appendix G and `main.tex` (`Appendix/EndogenousDesignDetails.tex` new; `Appendix/Robustness.tex`
  becomes H): paper-writer, Opus max.
- W4 the introduction's and conclusion's cost sentences, the abstract's clause, the technical note
  (`writing/US/model_esc.tex` specification paragraph, `num_esc.tex` calibration subsection) and
  `notes/paper_costLiterature.md` §4-5: paper-writer, Opus max.

**Phase R, review (after W).** R1 referee pass on section 7, appendices C and G: paper-reviewer-lead, Fable
max (claims delivered, derivations, style conformity). R2 numbers-against-tables audit of section 7,
appendix G, the introduction, the conclusion and the online appendix texts: paper-reviewer, Opus max. The
session applies the fixes, runs `checkPaper.py`, latexmk, `build.py --map`, `build.py --site` and the
quarto render (not published), writes the logs (paper, US, root), closes TODO W9, adds R6, indexes the
briefs in `archive/INDEX.md`, commits.

### C.3 Agents

| Phase | Role | Agent type | Model, effort |
|---|---|---|---|
| A | derivation and variant selection | `model-theorist` (new) | Fable, max |
| B | the specs in the code | `model-coder` | Opus, xhigh |
| C | the runs | `paper-compute` | Opus, xhigh |
| D | the builders | `paper-compute` | Opus, xhigh |
| W1, W2 | section 7, appendix C | `paper-writer-lead` (new) | Fable, max |
| W3, W4 | appendix G, the rest | `paper-writer` | Opus, max |
| R1 | referee pass | `paper-reviewer-lead` (new) | Fable, max |
| R2 | numbers audit | `paper-reviewer` | Opus, max |

The three new types are `.claude/agents/{model-theorist,paper-writer-lead,paper-reviewer-lead}.md`,
pinned to `claude-fable-5-1` at max; if the Agent tool has not loaded them, the same brief goes to a
`general-purpose` agent with `model: "fable"` and the type's rules pasted in. Fable where a wrong turn is
expensive to detect later (the economics, the paper's main section, the referee read); Opus where the
brief is complete and the checks are mechanical.

### C.4 Gates and stop conditions

- Gate 0 (before A and B): the agent types are available; the working tree is clean apart from this note.
- Gate 1 (after C): the LQ joint calibration converged with $\kappa \geq 0$ and the scans show one sign
  change; otherwise the fallback of decision 3. France's prediction under LQ is read here, whatever it is.
- Gate 2 (after D): `build.py --list` builds every registered output, `test_onlineAppendix.py` passes, the
  `'size'` outputs are byte-identical apart from figure timestamps.
- Gate 3 (after W): `checkPaper.py` clean, latexmk clean, no `\todo` left that a table could fill.
- A stop: a phase's agent reports a check it could not pass (the self-check, a non-converged joint
  calibration under both pinnings, a suite failure in `'size'`). The session then reads the report and
  decides; nothing downstream starts.

### C.5 Data schema the phases share (fixed here so D can be briefed before C ends)

`results/esc/escCalibration.csv` gains `kappa` (NaN except `sizeLQ`), `kappaFrom` (`UK`, `FR` or NaN) and
`θPin` (the pinning country's design at the joint solution); `escCountry.csv` gains `kappa` and `ownKind`
(`interior`, `threshold`, NaN), a threshold row carrying the bound in `p` with `θStar = choice = 1`;
`escPath.csv`, `escShocks.csv`, `escShocksUK.csv` and `escExperiments{,UK}.csv` gain `kappa`. Keys are
unchanged (`spec`, `phi` = 0.5 dummy, `commonX`, ...). The `_kappaFR` alternative lives in tagged csvs.
After gate 1: every row written by `wedgeReadout` also carries `Mabs` (the economy's $M$ at $t_0$), and the
specs are `'sizeL'`, `'sizeLQ'` ($M$ on the linear term, the paper's) and `'sizeLQV'` ($\tilde V$ on both, the
record), with $\lambda_1 = \lambda\kappa$ under `'sizeLQ'`/`'sizeLQV'` and $\lambda_1 = \lambda$ under `'sizeL'`.

### C.6 Open items raised by phase A, not taken up here

- The leaded recursion interpolates the tax policy linearly on the 41-node state grid; because the design
  objective is flat, the parabolic refinement amplifies the $3\times10^{-5}$ error in $\tau$ into 0.004 in
  the 2020 choice (0.797 against 0.794 with the policy evaluated at the candidates) and $5\times10^{-4}$ in
  the 1990 choice the calibration targets. Evaluating the tax policy at the candidates costs one `τOfθ` call
  per period (`notes/esc_variants.md`, "A precision item"). Not changed in this plan, so that the published
  quadratic rows stay bitwise; TODO C11.
