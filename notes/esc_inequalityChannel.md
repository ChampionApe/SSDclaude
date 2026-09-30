# Endogenous θ: why inequality dominates the chosen design, and what would change it (2026-09-24)

Review note for RKB and MGE. The problem: in section 7 (`sec:esc`) France's income distribution sends the
chosen design to the Bismarckian corner at every ρ, and the paper has to close on "the data cannot tell the
two apart", while figure 1 shows no inequality–design relation across the OECD. This note diagnoses the
mechanism, lists the model extensions that would change it with what each gains and costs, recommends one,
and reports a pilot of it at ρ = 1. The pilot ran from a scratch script that patches the wedge at runtime;
nothing in `python/`, `results/` or `writing/` was changed.

## 1. Diagnosis: the wedge is zeroth-order in inequality, the stakes are second-order

The paper's own stakes decomposition (`python/US/thetaStakes.py --rho 1 --country US FR UK`, LOG, at each
country's calibrated design, `full` reading; utils per unit θ_{t+1}, negative = pro-Beveridge):

| stake in a higher θ_{t+1}            | US (θ = 0.738, V = 0.48) | UK (θ = 0.560, V = 0.24) | FR (θ = 1, V = 0.26) |
|---|---|---|---|
| old, via h_t                          | +0.017 | +0.012 | +0.025 |
| old, via τ_{t+1}                      | −0.004 | −0.002 | −0.005 |
| young, re-split of their own pot      | −0.051 | −0.025 | −0.045 |
| young, aggregate (GE, R, Γ_s)         | −0.015 | −0.010 | −0.018 |
| young, size (dτ_{t+1}/dθ_{t+1} < 0)   | −0.072 | −0.056 | −0.055 |
| **total, no wedge**                   | **−0.124** | **−0.081** | **−0.098** |

V ≡ Σ_i γ_i (y_i − 1)², y_i = η_i^{1+ξ}/(X_i^ξ Γ_h), is the between-type variance of relative labour income
in the common-X calibration (US 0.483, UK 0.237, France at the US cuts 0.257).

Three things to read off it.

1. **The two large pro-Beveridge stakes are both redistributive.** The re-split is by construction (to
   leading order ∝ Σγ_iμ_i(y_i−1)²). The size channel is the young anticipating that a more Bismarckian
   design lowers next period's tax, which is *their* pension; dτ_{t+1}/dθ_{t+1} < 0 is proposition 2's
   mechanism (retirees' marginal-utility dispersion) and is likewise second-order in the spread. The
   pro-Bismarck stakes (the old through h_t, and the wedge) do not scale with the spread at all.
2. **The current wedge f(θ) = φ + (1−φ)θ^p burns 1−f(θ) of revenue at a design θ whatever the income
   distribution.** At V = 0 the two designs pay identical benefits (θy_i + 1−θ = 1 for every i), so a
   flat component redistributes nothing, yet θ = 0 would still burn half the revenue. The cost is attached
   to the label, not to the redistribution the label performs. Compress the distribution and the stakes
   fall roughly ∝ V while the cost does not: the corner at θ = 1 is arithmetic, not political economy.
3. **"Inequality" in the model is V, and V depends on the group cuts as much as on the country.** The
   UK's η_H/η_L (3.06) equals the US's (3.08), but its V is half, because its groups are 29/58/13 rather
   than 58/18/24. That is why the US wedge imposed on the UK returns θ = 1 against the observed 0.56
   (`results/esc/escCountry.csv`): the same arithmetic as the French-income row. Any inequality–design
   statement the paper makes is a statement about V, which figure 1's Gini does not measure.

## 2. Candidates

| | extension | what it does to the inequality channel | gain | loss / cost |
|---|---|---|---|---|
| A | **Leak proportional to the redistribution performed**: 1−f = ½λV(1−θ)² (exponential form keeps f > 0). Proportional, so f still cancels from the replacement-rate ratio and θ* = 0.738 stands; λ calibrated as p is now. | Stakes and cost scale together, so the design is invariant to a compression of the distribution to leading order; what survives is the first-order covariance of voting weights with income and the two zeroth-order channels. | Removes the corner and the group-cut fragility; nothing is lost at V = 0, which is the natural leaky bucket; no new proposition (the A/B substitution, decoupling and separability results hold verbatim); one `spec` in `Base.fWedge`, the pipeline reruns as is. | Still a reduced form; a referee can say the scaling was chosen. The rebuttal is that the *current* form is the odd one (burns revenue when nothing is redistributed) and that the cross-country prediction (calibrate on the US, predict the UK and France) is the test. Ageing → Bismarckian stays a political-weight effect, not strengthened. The voting row stays ρ-fragile at ρ = 2 (the objective is flat there; a wedge property, not this wedge's). |
| B | **A plus size**: 1−f = ½λτV(1−θ)², the Harberger form — the loss is quadratic in the implicit tax τ(1−θ)(1−1/y_i) the flat component puts on each type, summed and divided by revenue. | As A, and the design now responds to the size of the system: a bigger system makes the flat component costlier at the margin. | A cost-based ageing → Bismarckian channel on top of the weight channel; a positive size–design relation, which is the stylised fact behind figure 1 and in Conde-Ruiz & Profeta (2007) and Koethenbuerger, Poutvaara & Profeta (2008); the observed ranking UK (11.9 %, 0.56) < US (14.4 %, 0.74) < France (21.3 %, 1.00) becomes a prediction from one parameter. | f depends on τ_t: the tax FOC picks up ∂f/∂τ, the substitution proposition becomes A(θ,τ), B(θ,τ), the old's closed-form derivative in z_t is extended; decoupling survives under LOG. A day or two of code plus the CRRA reruns. Builds in what it shows, so it must be presented as a specification whose test is out of sample. |
| C | **Structural cost: a latent formality/evasion margin** (the Argentine model's own margin, activated in the rich-country model). High types can leave the tax base when the flat component's implicit tax on them rises. | Endogenous leak, ∝ the cross-subsidy (hence V) and ∝ τ: B with a microfoundation. | Referee-proof answer to "what is the cost"; ties sections 5 and 7 together. | Weeks: a distribution of outside options per type (unidentified for the rich countries), an extensive margin inside the political FOC, informal savings as a state (the CRRA recursion goes to three dimensions), and sections 2–6 change unless the margin is switched on in section 7 only. The follow-up paper, not this draft. |
| D | **Insurance motive**: idiosyncratic risk realised after the design vote, so the flat component is insurance (Casamatta–Cremer–Pestieau; Conde-Ruiz–Profeta). | Interior design without any wedge; inequality matters less because everyone values the flat part ex ante. | The cleanest economics. | Breaks the deterministic GHH-log tractability (closed forms, state-space collapse, propositions 1–2, the whole numerical apparatus); explicitly outside the paper's scope (the conclusion says so; `BergGEwp` is the sequel). |
| E | **Non-labour old-age resources** e_i (housing, bequests, other transfers), less dispersed than earnings. | Lowers the retirees' marginal-utility dispersion, i.e. the level of the redistributive stake. | Cheap (an endowment term as in the analytical model); realistic. | Rescales V-like objects but does not change the shape of the trade-off, so compression still corners under a V-independent wedge; and it weakens the inequality → τ results of sections 3 and 6, which read well and should not be reopened. Not a fix. |
| F | **Constitutional choice** of θ (utilitarian or steady-state objective) with τ by probabilistic voting. | Separates rules from policy. | Realistic in that designs are sticky and taxes are not. | Gives up the paper's single political objective; with equal weights the redistributive stake is *stronger*, so a wedge is still needed. No. |
| G | **Contribution ceiling / opt-out** for high earners (multi-pillar realism). | Bounds the cross-subsidy a flat benefit can extract. | Matches how Beveridgean systems work; the identification from replacement rates at half-mean and mean income is untouched if the ceiling sits above mean income. | A new policy dimension whose level has to be chosen or calibrated, with no natural datum. Medium cost, uncertain payoff; a footnote at most. |
| H | **No model change**: report the corner and confront figure 1 with the joint income + voting experiment, which is what the cross-section moves together. | None. | Free; the paper already has the joint row. | A corner makes every sensitivity check on that row vacuous (`notes/crossCuttingFindings.md` #10), the joint row's sign depends on ρ, and the paper's novel section ends on "the data cannot tell the two apart". |

## 3. Recommendation

Do A now and aim for B. A is a three-line change to the wedge and the existing calibration and experiment
pipeline reruns unchanged; it turns the French-income corner into an ordinary interior response and makes
the wedge's cross-country prediction meaningful. B is the version that also delivers the size–design
relation that figure 1 and the literature show, at the cost of a τ inside f and a day or two of derivation
and code. C is the microfoundation to promise in the conclusion and to build in the follow-up. D is a
different paper. Whichever of A or B is adopted, the discipline that replaces "we chose the scaling" is the
out-of-sample test already half-built in `runESC.stageCountry`: calibrate λ on the US, then let the UK and
France choose under the US λ and compare with 0.56 and 1.00. Under the current wedge that test fails (both
go to θ = 1).

## 4. Pilot at ρ = 1 (LOG), common-X calibration

A scratch script (session scratchpad, `pilotQuadWedge.py`) patches `Base.fWedge` at runtime with two specs
and otherwise uses the paper's own machinery: `calibrateWedge` (design in force in 2020 = 0.738, (β, ω)
recalibrated at every trial λ), `leadedNewPath` for the counterfactuals (new equilibrium path, own steady
state, the choice binding from the first period, read at 2020) and `buildEU` + `leadedDesignAtT0` for the
countries.

    quad      f(θ) = exp(−½ λ V (1−θ)²)
    quadSize  the same with λ·τ̄_s/τ̄_US, τ̄_s the scenario's or country's tax with the design pinned:
              an OUTER scaling standing in for a τ inside f (candidate B proper)

Calibration: λ = 2.054 (residual 5e-10; the scan is monotone, from the θ = 0 corner at λ ≤ 0.34 to θ → 1 at
λ ≥ 20). At the US V, f(0.738) = 0.967, i.e. 3.3 % of revenue lost at the observed design against 5.8 %
under the paper's wedge, and f(0) = 0.61 against φ = 0.5. A LOG wedge calibration takes 82 s, a leaded
solve 3 s.

**The chosen design in 2020** (paper column: `results/esc/escExperiments.csv`, ρ = 1):

| scenario | V | paper's wedge | quad | quadSize (scale) |
|---|---|---|---|---|
| baseline | 0.483 | 0.738 | 0.738 | 0.738 (1.00) |
| mild ageing | 0.483 | 0.752 | 0.747 | 0.797 (1.28) |
| acute ageing | 0.483 | 0.778 | 0.752 | **0.837** (1.61) |
| French income distribution | 0.261 | **1.000** | **0.791** | **0.776** (0.94) |
| French leisure (placebo) | 0.483 | 0.738 | 0.738 | 0.738 (1.00) |
| French voting | 0.483 | 0.533 | 0.647 | 0.661 (1.06) |
| income + voting | 0.261 | 0.972 | 0.652 | 0.650 (0.99) |
| baseline path 2050 / 2080 / 2110 | | 0.748 / 0.768 / 0.773 | 0.744 / 0.749 / 0.750 | not run |

Under quad the French-income row's tax is 13.58 % with the design chosen against 13.59 % pinned (paper:
13.80 % against 13.16 %), so the "design reversal" paragraph of `sec:esc` would go.

**The UK and France under the US λ** (observed design in brackets; `escCountry.csv` for the paper column):

| | paper's wedge (US p) | quad | quadSize (scale) |
|---|---|---|---|
| UK [0.560] | 1.000 | 0.672 | **0.602** (0.82) |
| France [1.000] | 1.000 | 0.675 | **0.772** (1.48) |
| UK at US cuts [0.543], V = 0.073 | 1.000 | 0.698 | 0.640 (0.82) |

The UK's own calibrated wedge, relative to the US's: p = 0.185 against 0.408 under the paper's form (a
factor 2.2), λ = 1.50 against 2.05 under quad (1.4), λ = 1.82 against 2.05 under quadSize (1.1). One
technology of redistribution comes within 11 % of rationalising both designs under the size-scaled form.

Reading.

1. **The corner is gone.** France's income distribution moves the design by +0.05 (quad) or +0.04
   (quadSize), the same order as ageing, and the income row's tax and savings read as in the pinned
   reading.
2. **The voting effect halves** (−0.09 against −0.21) and the joint experiment has a sign at ρ = 1: French
   characteristics make the design *less* Bismarckian (0.65), the flatter voting profile outweighing the
   compressed distribution. Under the paper's wedge the joint row is 0.972 at ρ = 1 and 0.494 at ρ = 2.
3. **The size scaling is what makes ageing a first-order determinant of the design** (+0.10 under acute
   ageing, against +0.04 in the paper and +0.01 under quad alone) **and what orders the countries**: one λ
   calibrated on the US puts the UK at 0.60 and France at 0.77, the observed ranking, where the paper's
   wedge sends both to θ = 1 and quad alone puts France below the US.
4. **Not covered by the pilot**: ρ ≠ 1 (the exact 2-D CRRA runs, ~45 min per ρ for the calibration alone);
   a τ inside f instead of the outer scaling; and France's corner. Under a purely quadratic leak the first
   unit of redistribution is free at the margin, so no electorate chooses exactly θ = 1; a linear (Okun)
   term restores that possibility at the price of a second parameter, which the UK's design could pin
   (two targets, two parameters, France as the prediction).

## 5. Status

Candidate B adopted on 2026-09-24 as the branch `esc-sizeLeak`; the execution plan, with the derivation
behind the form, the work packages and the stop conditions, is `archive/notes/plan_escSizeLeak.md`. The pilot's
script, result csvs and log are in `archive/pilots/escSizeLeak_2026-09-24/`.

Outcome (2026-09-24, the branch executed with $\tilde V$ in place of $V$ and $\tau$ inside $f$): at $\rho = 1$
one $\lambda = 8.64$ calibrated on the US gives the French income row 0.772 (interior), acute ageing 0.825,
French voting 0.653, income + voting 0.627, and the ranking UK 0.625 < US 0.738 < France 0.749 under the
US $\lambda$, with the UK's own $\lambda$ within 16 % of the US's. Numbers: `results/esc/*.csv` rows
`spec = size`, the paper's `Tables/US_ESC_*.tex`; the CRRA rows and the write-up are logged in
`python/US/RESEARCH_LOG.md` and `python/paper/RESEARCH_LOG.md` of the same date.

## 6. What adopting A (or B) touches

- `python/US/base.py` `fWedge`: one new `spec` (A), or a τ argument through `wedgeA`/`wedgeB` and the
  old's derivative in `policy.py` (B). `modelESC.getθ` needs nothing: both are proportional.
- `python/US/runESC.py`, `runESCcrra.py`: the `--spec` list; `--bracket` for λ (its scale differs from p's).
- `python/paper/config.py`, `tablesUS.py`: `US_ESC_Calibration` prints λ (and f(0)) instead of p, φ.
- `writing/US/model_esc.tex`: the cost paragraph and eq `esc:AB`; `num_esc.tex`: the calibration bracket.
- `writing/Paper/Sections/EndogenousTheta.tex`: `eq:esc:budget` and the paragraph after it, the results
  subsection (income distribution, both at once), the intro's W1 sentence, the abstract's and the
  conclusion's last sentences on inequality and the design.
