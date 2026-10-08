# Brief: the cost of redistribution with a linear term -- derivation and variant selection (phase A)

For the `model-theorist` agent. Plan: `notes/plan_endogenousDesign.md` §C (read C.1 first: the decisions
you are asked to verify or overturn). You write one file, `notes/esc_variants.md`, and nothing else.

## 1. The question

Section 7 of the paper (`writing/Paper/Sections/EndogenousTheta.tex`) lets the electorate choose the
Bismarckian index $\theta_{t+1}$ one period in advance under a deadweight cost of redistribution,
$f(\theta_t,\tau_t) = \exp\{-\tfrac12\lambda\tau_t\tilde V(1-\theta_t)^2\}$, the Harberger loss of the flat
component's implicit taxes (appendix C.2, `writing/Paper/Appendix/EndogenousDesign.tex`). Under this cost the
marginal cost of the first unit of redistribution is zero, so no electorate chooses the Bismarckian corner
$\theta = 1$, which is France's observed design. RKB wants a linear term that allows France's corner, two or
three variants of the cost presented in the paper, and the derivations for each as in appendix C.

The plan's working form (decision C.1.1) is
$$
f(\theta_t,\tau_t) = \exp\Big\{-\tau_t\tilde V\,(1-\theta_t)\big[\lambda_1 + \tfrac12\lambda_2(1-\theta_t)\big]\Big\},
\qquad \tilde V = \sum_i\gamma_i\frac{(y_i-1)^2}{y_i},
$$
with the variants Q ($\lambda_1 = 0$, the paper's), L ($\lambda_2 = 0$) and LQ (both; written
$\lambda_1 = \lambda\kappa$, $\lambda_2 = \lambda$). Your job is to derive what the paper and the code need
for the three, and to say whether this is the right form.

## 2. What to read first

- `writing/Paper/Appendix/EndogenousDesign.tex`: C.1 (the costless corner, proposition `prop:esc:corner`,
  the leaded first-order condition `eq:esc:leadFOC`), C.2 (the implicit tax, the Harberger loss, the
  specification `eq:esc:AB`, the magnitude), C.3 (the equilibrium with the cost: `eq:esc:auxiliary`,
  `eq:esc:E2`, identification, the design condition `eq:esc:ftheta`), C.4 (separability,
  `prop:esc:separability`). Your note is written against these labels.
- `writing/Paper/Sections/EndogenousTheta.tex` (how the paper reads the cost) and
  `writing/Paper/Sections/Log.tex` (the log equilibrium: `eq:s`, `eq:h`, `eq:si_s`, `eq:hi_h`, the
  political objective `eq:LOG:PolObj`, proposition `prop:LOG:PEE`).
- `writing/US/model_esc.tex` (the technical note's version, with the dates and vintages of $f$) and
  `notes/paper_costLiterature.md` (the literature and how the paper motivates the cost; §2.A has the
  Okun framing of a linear term).
- The code that implements the objects: `python/US/base.py` lines 168-240 (`fWedge`, `dlnfWedge_dτ`,
  `wedgeA`, `wedgeB`, `Vtilde`), `python/US/policyESC.py` lines 83-340 (`LeadedLOG`: `objective`,
  `solveBackward_t`, `_argmax`), `python/US/modelESC.py` lines 464-531 (`calibrateWedge`).

## 3. Facts to reason with (2020, common $X$, $\rho = 1$; sources in brackets)

| | U.S. | UK (own cuts) | UK (U.S. cuts) | France (U.S. cuts) |
|---|---|---|---|---|
| observed $\theta^{\ast}$ | 0.738 | 0.560 | 0.543 | 1.000 |
| tax rate $\tau_{2020}$ | 14.4% | 11.9% | 11.9% | 21.3% |
| $\tilde V$ | 0.436 | 0.223 | 0.065 | 0.218 |
| chosen under the U.S. $\lambda = 8.643$ (Q) | 0.738 | 0.625 | 0.644 | 0.749 |
| own $\lambda$ (Q) | 8.643 | 7.264 | 6.519 | none |

(`results/esc/escCountry.csv`, `results/paper/Tables/US_ESC_Country.tex`.) U.S. types: $\gamma_i$ = (0.582,
0.176, 0.242), $y_i$ = (0.507, 1.000, 2.187), so $\tilde V$ = 0.436 and the mean absolute deviation
$M = \sum_i\gamma_i|y_i - 1|$ = 0.575; $\nu_{2020}$ = 1.34. Under Q at $\rho = 1$: $f(\theta^{\ast})$ = 0.982,
$f(0)$ = 0.762; the chosen design under acute ageing 0.825, France's income distribution 0.772, France's
voting patterns 0.653 (`US_ESC_Results.tex`). The tax policy's slope in the inherited design is about
$-0.06$ per unit of $\theta$ at $\rho = 1$ without the cost (section 6: $\theta$ from 1 to 0 raises the tax
by 6.2 p.p.).

## 4. Tasks, in order

1. **The general form and its reading.** State $f$, the three variants and the first-order loss share.
   Verify and state: $f = 1$ at $\theta_t = 1$ and whenever $\tilde V = 0$; the share lost rises with
   $\tau_t$; $\partial\ln f/\partial\theta_t$ at $\theta_t = 1$ equals $\lambda_1\tau_t\tilde V$;
   $\partial\ln f/\partial\tau_t = \ln f/\tau_t$, so the tax condition's factor is $1 + \ln f$ for every
   variant. Give the Okun reading (a leak with a constant share per unit carried and a share rising with
   the load) and the Harberger reading of the quadratic part as C.2 has it. Then the $\tau$-scaling of the
   linear term (decision C.1.2): derive what a leak proportional to the amount the flat component carries
   gives as a share of revenue (I expect $\lambda_1(1-\theta_t)M$ up to a constant, independent of
   $\tau_t$, weighted by $M$ rather than $\tilde V$); state the common-scaling form as a choice, with the
   alternative's cost in one paragraph the writer can turn into a footnote. Recommend one; task 3 is the
   economic argument.
2. **The equilibrium with the cost.** Confirm that C.3 carries over verbatim for the general form: the
   substitution, the factor in `eq:esc:E2`, identification of $\theta$ (f cancels from $B/A$), the design
   condition `eq:esc:ftheta` with $\partial f/\partial\theta_{t+1} = f\tau_{t+1}\tilde V[\lambda_1 +
   \lambda_2(1-\theta_{t+1})]$, and proposition `prop:esc:separability`. Note anything that does not.
3. **The corner condition at $\theta_{t+1} = 1$ under log preferences.** By `prop:esc:separability` the
   design chosen at $t$ maximises $\mathcal{B}_t(\theta_{t+1})$ alone. Derive
   $\partial\mathcal{B}_t/\partial\theta_{t+1}$ at $\theta_{t+1} = 1$ explicitly from `eq:esc:leadFOC` with
   `eq:esc:auxiliary` (the retirees' hours term, the young's consumption and return terms, the response of
   $\tau_{t+1} = \mathcal{T}_{t+1}(\theta_{t+1})$, which you may carry as a symbol $\mathcal{T}'_{t+1}(1)$ with its
   sign and size from the facts above; the continuation design is state-free). At $\theta_{t+1} = 1$, $f = 1$,
   $A = 1$, $B = 0$, $\partial A/\partial\theta = 1 + \lambda_1\tau\tilde V$, $\partial B/\partial\theta = -1$.
   State the corner condition as $\lambda_1 \geq \bar\lambda_1$ with $\bar\lambda_1$ as explicit as the
   algebra allows (in $\tau_{t+1}$, $\tilde V$, $\alpha$, $\beta$, $\xi$, $\nu_t$, $\gamma_i$, $y_i$, $\mu_i$,
   $\mathcal{T}'_{t+1}$). Then: (a) the first-order cancellation of $\tau_{t+1}$ between the cost's marginal
   benefit and the young's redistributive stake, and the sign of what remains (does a larger system make
   the corner easier or harder to reach under the common scaling?); (b) the same condition under the
   $\tau$-free linear leak of task 1, to settle decision C.1.2; (c) how $\bar\lambda_1$ moves with the
   dispersion (the stake is a sum over types of terms like $\mu_i(y_i-1)/D_i$, not $\tilde V$, so the
   ratio is country-specific: say what France's lower dispersion and larger system do), with $\nu_t$
   (ageing) and with the voting profile $\mu_i$. If a closed form is out of reach, state the condition in
   terms of the partials and sign each. Numerical confirmation allowed and welcome: the sign of a
   one-sided finite difference of `LeadedLOG.objective` at $\theta' = 1$ on the U.S. test model
   (`python/US/test.py`'s `pars`, `kwargs`; `test_esc.py` shows `build(ModelESC, wedge)`) at a few
   $\lambda_1$ against your bound; a one-line comparison, labelled as a confirmation.
4. **Calibration and identification.** Q and L: one parameter per country on its own observed design;
   France's own parameter under L and LQ is the threshold $\underline\lambda$ of task 3 (a bound). LQ:
   $(\lambda,\kappa)$ on the U.S. and the UK designs jointly, France the prediction (decision C.1.3). Argue
   the direction: holding the U.S. first-order condition, how does the UK's chosen design under the U.S.
   parameters move as $\kappa$ rises from 0 (I expect it to fall, since the linear term lowers the marginal
   cost at the UK's lower design relative to Q while the U.S. optimum is held); is the map monotone; is
   $\kappa \geq 0$ the right side (the UK's design under Q is 0.625 > 0.560); when would the fallback
   (France pins $\kappa$, the UK predicts) be needed. Note that the UK's own $\lambda$ at the common
   $\kappa$ reproduces $\lambda_{US}$ by construction and that a corner calibration is set-valued.
5. **What to expect in the counterfactuals per variant**, one page: acute ageing ($\nu_t = 1$; the tax
   channel through $\tau$ in both terms; under L a constant marginal cost in $\theta$), France's income
   distribution (both terms scale with $\tilde V$ as the stakes do), France's voting patterns (unchanged
   mechanism), and the baseline path's drift with $\nu_t$. Qualitative, signed where you can sign it.
6. **A tex-ready block for appendix C.2 and section 7.1**, in the paper's notation and register
   (`notes/paper_styleGuide.md`; C.2's own paragraphs are the exemplar): the specification paragraph for
   the general form in place of the current one around `eq:esc:AB` (keep that label for the $(A,B)$
   definition; propose a label for the general $f$, e.g. `eq:esc:fGeneral`), a `\smalltitle{The
   Bismarckian corner.}` paragraph or a short proposition `prop:esc:bismarckCorner` with its proof, and
   three or four sentences presenting the variants for section 7.1. The writers adapt; the derivations
   are yours.

## 5. Form of the note

`notes/esc_variants.md`, Markdown with LaTeX math. Sections 1-6 as the tasks, numbered equations (`(A.1)`,
...) the writers can cite. If anything overturns C.1 (the scaling, the parametrisation, the pinning), put
it under a heading "Overturned" at the top with the reason and what to do instead; otherwise state at the
top that C.1 stands. Length as needed; three to six pages is the expectation. No narration of your own
process.
