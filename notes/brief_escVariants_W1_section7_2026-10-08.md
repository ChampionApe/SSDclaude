# Brief W1: section 7, the endogenous pension design (`Sections/EndogenousTheta.tex`)

For the `paper-writer-lead` agent. Your file: `writing/Paper/Sections/EndogenousTheta.tex` alone. Three
other writers work at the same time: W2 on `Appendix/EndogenousDesign.tex` (appendix C), W3 on the new
`Appendix/EndogenousDesignDetails.tex` (appendix G) and `main.tex`, W4 on the introduction, abstract,
conclusion and the technical note. Interfaces are in §4 below; cite their labels, do not wait for them.

## 1. What RKB asked for

`notes/plan_endogenousDesign.md` §B is RKB's outline and is binding in its order; §C.1 lists the session's
decisions (read decisions 1 to 5 as amended at gate 1). The section presents three variants of the cost of
redistribution at $\rho = 1$ and leads with the preferred one, the linear-quadratic cost; the other two get
one paragraph. The economics is derived in `notes/esc_variants.md` (its §7 is the version under the $M$
weight, the paper's; §1-§6 the derivation and the proxies); its three or four sentences for section 7.1
are yours to adapt. Target 2,000 to 2,300 words (`checkPaper.py` counts; the current text is 1,594).

## 2. Structure, in order

**Opening paragraph** (keep the current one, adjusted): one political process delivers the size and the
shape; derivations in appendix C, details in appendix G, algorithms in the technical documentation.

**7.1 `\subsection{The deadweight cost of redistribution}\label{sec:esc:cost}`** (label kept; the
generated notes cite it).
- *Diagnosis.* Without a cost the choice is a corner (proposition `prop:esc:corner`, the U.S. timings in
  appendix C.1): the model lacks a mechanism that makes flat benefits costlier than earnings-related ones.
  Keep the current first paragraph's substance.
- *The implicit tax.* Show it: the flat component pays type $i$ $\Pi_t\tau_t[\theta_t + (1-\theta_t)/y_i]$
  per unit of past earnings against $\Pi_t\tau_t$ from an earnings-related system of the same revenue,
  so the flat component levies $t_i = \Pi_t\tau_t(1-\theta_t)(1-1/y_i)$ (display it with its label
  `eq:esc:implicitTax` cited from appendix C, or state it inline and cite), a tax above mean income, a
  subsidy below, a pure transfer in the aggregate: Summers's tax component \parencite{Summers89a1}. Then
  what the model already contains: the marginal wedge of the flat component is common to all types and
  moves hours through the Frisch elasticity (`eq:h`, the intensive margin); what it does not: an
  extensive margin, participation, formality, the reporting of earnings, on which the average wedge
  $t_i$ is what matters.
- *The literature*, one paragraph in RKB's order: (i) losses from taxation in general, the Harberger
  loss quadratic in the wedge \parencite{Harberger64a1} and Okun's leaky bucket \parencite{Okun75a1};
  (ii) the tax component as a tax on the extensive margin, \textcite{Disney04a1} on participation and
  \textcite{KumlerVF20a1} on the reporting of wages; (iii) extensive against intensive margins,
  \parencite{Saez02a1,KlevenK06a1} for the average wedge on the participation margin and
  \parencite{ChettyGMW11a1,SaezSG12a1} for the magnitudes; (iv) the size of the system and its design,
  \textcite{CondeRuizP07a1} and \textcite{KoethenbuergerPP08a1}. Every key exists in `References.bib`;
  `notes/paper_costLiterature.md` §2 says what each reference finds, use it rather than memory.
- *The specification.* The budget `eq:esc:budget` with the general $f$ (keep the display and its label;
  the form is now $f = \exp\{-\tau_t(1-\theta_t)[\lambda_1 M + \tfrac12\lambda_2\tilde V(1-\theta_t)]\}$ with
  $M \equiv \sum_i\gamma_i|y_i-1|$ beside $\tilde V$). The leaky-bucket reading: the amount the flat
  component carries is proportional to $\tau_t(1-\theta_t)M$ (appendix C.2); a leak with a constant share
  per unit carried (the linear term, weighted by the amount carried) and a share that rises with the load
  (the quadratic term, the Harberger loss, weighted by $\tilde V$), both scaled by the size of the system.
  The three variants: quadratic ($\lambda_1 = 0$, the cost of the earlier draft), linear ($\lambda_2 = 0$),
  linear-quadratic (both, written as a scale and a shape, $\lambda_1 = \lambda\kappa$, $\lambda_2 = \lambda$).
  The properties, one sentence each: nothing lost when nothing is redistributed; the share lost rises with
  the size of the system; the marginal cost of the first unit of redistribution is $\lambda_1\tau_t M$, zero
  under the quadratic cost (hence no corner) and positive otherwise, with the threshold of proposition
  `prop:esc:bismarckCorner` falling in the size of the system and rising with a flatter voting profile and
  a more compressed distribution. What carries over, in two sentences with pointers: the solution with
  $f\theta_t$ and $f(1-\theta_t)$ (`app:esc:equilibrium`), $\theta^{\ast}$ unchanged, the factor $1+\ln f$ for
  every variant, the timing one period ahead and the state independence (`prop:esc:separability`). Keep
  the current sentence on the margins the cost stands for and on $\lambda$'s magnitude (appendix C.2),
  reworded for two parameters.

**7.2 `\subsection{Calibration and a cross-country test}\label{sec:esc:calibration}`** (label kept).
Table `table:US_ESC:variants` (`Tables/US_ESC_Variants.tex`). Per variant what pins the parameters: the
quadratic and the linear on the U.S. design alone ($\theta_{2020}$, chosen in 1990, equal to $\theta^{\ast}$);
the linear-quadratic on the U.S. and the UK designs together, France the prediction. Read the table: the
parameters, the share of revenue lost at the observed design and at a flat benefit, the designs the UK and
France choose under the U.S. parameters, the own parameters (France's as a threshold). The reading the
numbers support (check it against the table): the ordering holds under every variant; the UK's design pins
a small linear term, so France is predicted interior under the preferred variant; France's corner takes a
linear term large enough to put the UK far below its design (the alternative pinning, appendix G.1); the
linear cost is knife-edge (the UK at the Beveridgean corner). One datum per parameter, so the test rests on
the economy not used. The UK at the U.S. income cuts and the $\rho \neq 1$ calibrations go to appendix G
(a pointer each).

**7.3 `\subsection{Ageing and inequality}\label{sec:esc:results}`** (label kept; the robustness map's
note cites it).
- The baseline path, figure `fig:US_ESC:path` (`Figs/US_ESC_Path.pdf`, the three variants; read the
  figure's note in the tex that W... no: the figure environment is yours, keep its form and update its note
  to name the variants): the design rises with ageing under every variant, the preferred one's numbers in
  the text; the linear one reaches the corner.
- The counterfactuals, table `table:US_ESC:results` (`Tables/US_ESC_Results.tex`, one block per variant):
  `\smalltitle{Ageing.}`, `\smalltitle{Income distribution.}`, `\smalltitle{Voting patterns.}` with the
  preferred variant's numbers and the mechanisms of the current text (the retirees' unanimity and the tax
  channel for ageing; the stakes and the cost scaling together for the income distribution; the
  redistributive force regaining ground for voting), each updated to the new numbers and to the $M$
  weight where it matters (France's income profile lowers $M$ by less than $\tilde V$).
- One paragraph on the other variants: the linear cost as the limit with no curvature, every counterfactual
  a corner, which is why the quadratic part is needed; the quadratic cost as the damped case; the
  responses ordered by the shape (`notes/esc_variants.md` §5). The rest in appendix G.2.
- One closing paragraph on the intertemporal elasticity, on the quadratic cost's numbers (the current
  closing paragraph condensed: the cost parameter falling in $\rho$, the ageing response stable, the
  inequality and voting responses not), saying the other variants are computed at $\rho = 1$, with the
  pointer to appendix G.3 and `\oa{esc-us}`.

## 3. Numbers

Every number from `writing/Paper/Tables/US_ESC_Variants.tex`, `US_ESC_Results.tex`, the figure's marks
(`results/paper/Figs/US_ESC_Path.marks.json`) or, for the appendix pointers, `US_ESC_VariantsCountry.tex`
and `US_ESC_Calibration.tex`. A number a table does not carry is `\todo{CRRA: ...}`-style, specific, and
listed in your report. Units and precision per `notes/paper_styleGuide.md` §3 (designs three decimals, tax
rates one decimal in percent, changes in p.p.).

## 4. Interfaces (labels you cite; do not define them)

Appendix C (W2): `app:esc`, `app:esc:corner`, `prop:esc:corner`, `app:esc:cost`, `eq:esc:implicitTax`,
`eq:esc:AB`, `eq:esc:fGeneral`, `prop:esc:bismarckCorner`, `app:esc:equilibrium`, `app:esc:log`,
`prop:esc:separability`. Appendix G (W3): `app:escDetails`, `app:escDetails:calibration`,
`app:escDetails:counterfactuals`, `app:escDetails:rho`. Tables and figures (generated, labels fixed):
`table:US_ESC:variants`, `table:US_ESC:results`, `fig:US_ESC:path`, `table:US_ESC:variantsCountry`,
`table:US_ESC:variantsShocks`, `table:US_ESC:calibration`, `table:US_ESC:summary`. Online appendix keys:
`esc-variants`, `esc-calibration`, `esc-us`, `esc-uk`, `esc-path`, `esc-timing`, `esc-scale`. Your own
labels: `sec:esc`, `sec:esc:cost`, `sec:esc:calibration`, `sec:esc:results`, `eq:esc:budget`.

## 5. Register and stop conditions

`notes/paper_styleGuide.md` throughout; the exemplar is the current section 7 as settled with RKB on
2026-10-07 (keep its sentences where they survive) and `Sections/OECD.tex`. No narration of the research
process; alternatives as choices with their cost, in footnotes. If `US_ESC_Variants.tex` or
`US_ESC_Results.tex` is missing or lacks a variant, stop and report; do not invent a number.
