# Brief: appendix C.2, the derivation of the cost in more detail — paper-writer-lead

Written 2026-11-07 for RKB: "appendix C.2 should explain how we derive our cost specification in more detail; it is
okay if it repeats things from the main section". The paper stays at the current specification (τ to the power one
in $\ln f$).

## Your files

- `writing/Paper/Appendix/EndogenousDesign.tex`: subsection C.2 only (`\subsection{The deadweight cost of
  redistribution}\label{app:esc:cost}`, up to `app:esc:equilibrium`), plus the opening paragraph of the appendix if its
  one-clause description of C.2 must change. C.1, C.3 and C.4 stay as they are.

Nothing else. Another writer edits `Sections/EndogenousTheta.tex` (section 7.3) and `Appendix/OECD26.tex` at the same
time: do not touch them. If C.2's new text makes a sentence of section 7.1 redundant, leave section 7.1 alone and say
so in your report.

## Read

The style guide; the exemplar is the appendix itself (`Appendix/EndogenousDesign.tex`). Then section 7.1
(`sec:esc:cost` in `Sections/EndogenousTheta.tex`: the implicit tax `eq:esc:implicitTax`, the budget `eq:esc:budget`
and its two footnotes), the labor supply condition `eq:model:formalFOCs` (`Sections/Model.tex`), the technical note's
version of the derivation (`writing/US/model_esc.tex`, "The deadweight cost of redistributive benefits", the paragraph
"The Harberger loss" and the one after it) and `notes/paper_costLiterature.md` §1–§4 (what the derivation has to meet
and which references carry which step).

## What C.2 should do

Derive the cost step by step, so that a reader who has not read section 7.1 can follow from the benefit formula to
$f(\theta_t,\tau_t)$ and see where each argument of $f$ comes from. Repeating section 7.1 is fine. Keep the honest
framing the subsection has now: the form follows from the tax component and Harberger's principle on margins the
model lacks; it is not derived from a model of participation and formality, and its size is left to the calibration.

Suggested order (adapt if a different order reads better):

1. **The benchmark and the implicit tax.** Under no informal households a retiree of type $i$ receives
   $\nu_tw_th_t\tau_t[\theta_ty_i+1-\theta_t]$ on past earnings $w_{t-1}y_ih_{t-1}$; per unit of past earnings this is
   $\Pi_t\tau_t[\theta_t+(1-\theta_t)/y_i]$ with $\Pi_t$ the pay-as-you-go return factor; a purely earnings-related
   system paying the same revenue returns $\Pi_t\tau_t$ to every type; the difference is the implicit tax $t_i$ of
   \eqref{eq:esc:implicitTax} (cite it; restate it unnumbered if useful): a tax above mean income, a subsidy below.
   Show in one line that the implicit taxes are a pure transfer weighted by earnings, $\sum_i\gamma_iy_it_i=0$. Tie it
   to Summers' tax component (one sentence, as now).
2. **Which margin.** Keep the content of the current paragraph (average against marginal wedge; the marginal wedge of
   the flat component is common to all types and already in the model through the labor supply function `eq:h`;
   participation and formality are margins on which the average wedge matters, Saez, Kleven–Kreiner; reporting
   responds to the marginal wedge and is not priced). Tighten or expand as the new structure needs.
3. **The Harberger loss, in steps.** (a) The rate: the benefit is paid at $t$ for earnings made at $t-1$ and a worker
   values it at $1/R_t$ (point to the labor supply condition), so the wedge on a unit of earnings at $t-1$ is
   $t_i/R_t$. (b) The base of type $i$ per unit of mean past earnings is $e_i=y_i$. (c) A base that responds to its
   net-of-tax rate with elasticity $\varepsilon$ loses, under a small proportional wedge $x$, an excess burden of
   $\tfrac12\varepsilon x^2e$ to second order (Harberger); show the one-line reason (the triangle). (d) Sum over types
   and use $y_i(1-1/y_i)^2=(y_i-1)^2/y_i$ to reach
   $\tfrac12\varepsilon(\Pi_t/R_t)^2\tau_t^2(1-\theta_t)^2\tilde V$ per unit of mean past earnings, valued at $t-1$.
   (e) Valued at $t$ (times $R_t$) and divided by the revenue per unit of mean past earnings, $\Pi_t\tau_t$, this is
   the share of revenue lost, $\tfrac12\varepsilon(\Pi_t/R_t)\tau_t(1-\theta_t)^2\tilde V$. (f) Say where each argument
   comes from: quadratic in the rate, hence in $1-\theta_t$ and in $\tau_t$ in levels, linear in $\tau_t$ per unit of
   revenue; $\tilde V$ from the type-specific wedges on earnings-weighted bases. Give the key displays numbered
   equations with new labels `eq:esc:...` where the text refers back to them.
4. **Why only the excess burden, and why against revenue.** Restate the argument of the budget's first footnote in
   section 7.1 with its algebra: with a common elasticity the first-order responses of the bases of taxed and
   subsidized types cancel in revenue because $\sum_i\gamma_iy_it_i=0$; what remains is the excess burden, a welfare
   cost that subsidized types bear as taxed ones do; charging it against the revenue that reaches retirees is a choice
   of reduced form. Keep the Saez caveat on the symmetry. Do not discuss higher-order revenue terms or other powers of
   τ: whether the cost should carry τ² is a separate, open question (another agent's note), and C.2 must not anticipate it.
5. **From the share to $f$.** The exponential form, $\lambda$ in the place of $\varepsilon\Pi_t/R_t$, first-order
   equality, $f\in(0,1]$, $f=1$ at $\lambda=0$; the factor $\Pi_t/R_t$ absorbed into a constant $\lambda$ for the U.S.
   and kept in the cross-section, $\lambda_{n,t}=\varepsilon\Pi_{n,t}/R_{n,t}$ (now a footnote; it may move into the
   text). Then the properties the paper uses (the current "Specification" paragraph: both derivatives of $\ln f$ vanish
   at $\theta_t=1$, so under log preferences the slope at the Bismarckian corner and the tax there do not depend on
   $\lambda$; scaling both components alike and the identification of $\theta$; the two alternatives with their cost).
   Write the two derivatives out.
6. **Magnitude.** Keep the paragraph and its numbers.

Length: the current C.2 is about 1,000 words; up to about 2,000 is fine if every added sentence is a step of the
derivation or the reason for one.

## Numbers

Only numbers that are already in C.2 or section 7 ($\Pi_t = 1.35$, $R_t = 2.44$, $\Pi_t/R_t$ about $0.55$, from $0.55$ in
2020 to $0.47$ in 2110, $0.06$ to $0.22$, 28 to 113 times, 6 to 25 times), each checked against its source as the
current text gives it (table `table:US:CalibUSFR`, appendix `app:US`, table `table:US_ESC:calibration`). Add no new
number; if the derivation seems to need one, write `\todo{...}` and report it.

## Rules and stop conditions

- Every derivation you state is checked line by line by you; if your algebra disagrees with the current text or the
  technical note anywhere (a factor of $R_t$ or $\Pi_t$, a sign), stop at that claim, write `\todo{...}`, report it.
- Keep `app:esc:cost` and every existing label; cite with lowercase cross-references; references only through
  biblatex with keys already in `References.bib` (Harberger64a1, Summers89a1, Saez02a1, KlevenK06a1, ChettyGMW11a1,
  SaezSG12a1, Disney04a1, KumlerVF20a1, LindbeckW87a1 exist).
- Run `writing/checkPaper.py` and scan for control bytes; compile if you can (`latexmk` in `writing/Paper`), noting
  that the other writer's files may be mid-edit.
