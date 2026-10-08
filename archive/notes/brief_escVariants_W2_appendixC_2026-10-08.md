# Brief W2: appendix C, the derivations (`Appendix/EndogenousDesign.tex`)

For the `paper-writer-lead` agent. Your file: `writing/Paper/Appendix/EndogenousDesign.tex` alone. W1 is
rewriting section 7 at the same time and cites your labels (§3); W3 writes appendix G; W4 the technical
note. The source of every derivation is `notes/esc_variants.md`: §7 is the version under the $M$ weight,
which is the paper's (the plan `notes/plan_endogenousDesign.md` §C.1 decision 1 as amended at gate 1); §1-§6
derive it under the $\tilde V$ weight first and §6 holds the tex block §7 restates. Read §7 first, then §1-§5
for the steps, then the current appendix.

## 1. What changes, by subsection

**C.1 Costless redistribution.** Unchanged.

**C.2 The deadweight cost of redistribution.** Keep "The implicit tax", "Which margin" and "The Harberger
loss" as they are. Replace "Specification" by the note's specification paragraph under $M$: the amount
the flat component carries, $\tfrac12\Pi_t\tau_t(1-\theta_t)M$ with $M \equiv \sum_i\gamma_i|y_i-1|$ (give it
a label, `eq:esc:Mabs`, beside `eq:esc:Vtilde`), is the derivation of the linear term's weight; the
quadratic term keeps $\tilde V$ from the Harberger loss; the general form `eq:esc:fGeneral`,
$f = \exp\{-\tau_t(1-\theta_t)[\lambda_1 M + \tfrac12\lambda_2\tilde V(1-\theta_t)]\}$, with the $(A,B)$
definition keeping `eq:esc:AB`; the one choice is the $\tau_t$ in the linear term, owned in a footnote with
the literal leak's cost (a share $\lambda_1(1-\theta_t)M$ independent of the size of the system, the corner as
far for a large system as for a small one, only the quadratic part dissipating at the margin of the tax);
the three variants and the scale-and-shape writing; the properties ($f = 1$ at $\theta_t = 1$ and when
$M = \tilde V = 0$; the share lost rising in $\tau_t$; $\ln f$ linear in $\tau_t$ so the factor is $1 + \ln f$
for every variant; the first unit's marginal cost $\lambda_1\tau_t M$). Keep the two closing sentences on
the flat-only cost and on the cost on the design. Add `\smalltitle{The Bismarckian corner.}` with
proposition `prop:esc:bismarckCorner`, its proof and the two paragraphs that follow it in the note (the tax
response rising with the cost; the comparative statics: a compressed distribution raises the threshold, a
larger system lowers it in proportion to $1/\tau_{t+1}$, a flatter voting profile raises it, ageing lowers
it), in the note's wording adapted to the appendix's register. "Magnitude": keep, reworded for two
parameters ($\lambda_2$ against $\varepsilon\Pi_t$; $\lambda_1$ has no elasticity benchmark and stands for the
share of each unit carried that administrative and political costs absorb), one sentence on each.

**C.3 The equilibrium with the cost.** The substitution, `eq:esc:auxiliary`, the tax condition `eq:esc:E2`
and the identification paragraph are unchanged in substance: say once that $\partial\ln f/\partial\tau_t =
\ln f/\tau_t$ holds for every variant, so $1 + \tau_t\partial\ln f/\partial\tau_t = 1 + \ln f$ as before. "The
design condition": generalise `eq:esc:ftheta` to
$\partial f/\partial\theta_{t+1} = f\tau_{t+1}[\lambda_1 M + \lambda_2\tilde V(1-\theta_{t+1})]$, zero at the corner
under the quadratic cost and $\lambda_1\tau_{t+1}M$ otherwise, and keep the reading.

**C.4 The design choice under log preferences.** Unchanged.

## 2. Checks you owe

Every step of the proposition's proof redone against the note's (A.10)-(A.17) in the appendix's notation
(`\frac{1-\alpha}{\alpha}` written out, dated symbols, $\partial f/\partial x$); the slope affine and
increasing in $\ell_{t+1}$ with the coefficient the note gives; the order-$\tau_{t+1}$ claim. Where your
algebra and the note disagree, stop at that claim, `\todo{}` it and report. No number in this appendix
comes from a table except those already there (the 2020 $\Pi_t$ of the magnitude paragraph; the sign
check of `eq:esc:seqFOC` at the calibrated economies).

## 3. Labels

Yours, kept: `app:esc`, `app:esc:corner`, `eq:esc:seqFOC`, `prop:esc:corner`, `eq:esc:corner:c2`,
`eq:esc:leadFOC`, `app:esc:cost`, `eq:esc:implicitTax`, `eq:esc:Vtilde`, `eq:esc:AB`, `app:esc:equilibrium`,
`eq:esc:benefits`, `eq:esc:auxiliary` (and its three parts), `eq:esc:E2`, `eq:esc:ftheta`, `app:esc:log`,
`prop:esc:separability`, `eq:esc:separability`. Yours, new: `eq:esc:Mabs`, `eq:esc:fGeneral`,
`prop:esc:bismarckCorner`, `eq:esc:cornerFOC`. Section 7's: `sec:esc`, `sec:esc:cost`,
`sec:esc:calibration`, `sec:esc:results`, `eq:esc:budget`. Register and checks: `notes/paper_styleGuide.md`,
`writing/checkPaper.py`; the exemplar is the current appendix C itself. Target: the appendix grows by 500
to 800 words.
