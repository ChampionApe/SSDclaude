# Closed form and mappings (T3: A11, #13, #22)

Package T3 of `notes/plan_reviewResponse.md`, written 2026-10-23 on `review-2026-10`. Three items: the
$J = 1$ log-HtM tax checked against Gonzalez-Eiras and Niepelt (2008, henceforth GN; `pdfs/GonzalezNiepelt2008.pdf`),
the relation between the OECD index and $\theta$, and the mapping of the cost parameter into an elasticity.
Notation is the paper's (`notes/paper_styleGuide.md` §4): $y_i \equiv \eta_i h_{t-1,i}/h_{t-1}$ relative income,
$\Gamma_h$, $\Theta_{h,t}$, $\mathcal{E}^i_{1,t}$, $\mathcal{E}^i_{2,t}$ as in appendices A and B, $\Pi_t$, $\tilde V$,
$f$, $\lambda$ as in section 7 and appendix C. Numerical runs are confirmations only; the scratch script is
`C:\Users\sxj477\AppData\Local\Temp\claude\C--Users-sxj477-Documents-GitHub-SSDclaude\f4320c70-85ef-4ec1-9a01-8a2eccd4abbe\scratchpad\scripts\check_T3.py`
(the U.S. model of `python/US` at the paper's common-$X$ calibration, $\beta = 0.7606$, $\omega = 1.4536$ from
`results/paper/usCalibrationSummary.csv`; it reproduces $\tau_{2020} = 0.1443$ and $R_{2020} = 2.443$).

## Overturned

**#22: the gap between $\lambda$ and the elasticities widens by $R_{2020} \approx 2.44$; it does not narrow.** The
brief (and decision 1 of the plan) say the review's correction "narrows the gap by $R \approx 2.4$". The review says
the opposite ("the 0.13–0.54 range shrinks and the reported multiples grow"), and the algebra of section 3 below
agrees with the review: discounting the wedge gives $\lambda \approx \varepsilon\Pi_t/R_t$, and $\Pi_t/R_t = 0.555$
at the 2020 calibration against the $\Pi_t \approx 1.34$ the paper uses, so the $\lambda$ that elasticities of
$0.1$–$0.4$ imply falls from $0.13$–$0.54$ to $0.055$–$0.22$ and every multiple in appendix C.2's comparison grows by
$2.44$: at $\rho = 1$ the calibrated $\lambda = 8.64$ is 39 to 156 times the range (the paper: 16 to 64), at
$\rho = 0.5$ 82 to 329 times (34 to 140), at $\rho = 2$ 8 to 31 times (3 to 13). The qualitative claim of section
7.2 ("by more than an order of magnitude at $\rho \leq 1$") survives and strengthens; at $\rho = 2$ "three to
thirteen times" becomes "about one order of magnitude". The direction follows from one fact: a worker at $t-1$
values a date-$t$ benefit at $1/R_t$ of its face value, so a given flat component is a smaller tax on current
earnings than its undiscounted size, and a given behavioural elasticity therefore implies a smaller loss.

Not an overturning of the brief but of appendix B as printed, confirmed here independently of T1/A5: the young's
term must carry $1 + \beta\alpha(1+\xi)/(1+\alpha\xi)$, not $1+\beta$. With the printed term the $J = 1$ tax does
not reduce to GN at $\xi = 0$ (it would put $1+\beta$ where GN have $1+\alpha\beta$) and would be $2.8\%$ rather
than $12.3\%$ at the U.S. 2020 values; the code (`base.dv1i_dτ_LOG`) has the correct term (section 1.2).

## 1. The representative-agent tax (A11)

### 1.1 Setting and the first-order condition

Section 3's model: log-GHH preferences, hand-to-mouth informal households, Markov policy. Set $\gamma_0 = 0$
(no informal households, so $\kappa = 1$ and $\overline{b}_t = \nu_t w_t h_t\tau_t/h_{t-1}$), $J = 1$ (one type of
formal household, so $y_1 = 1$, $\Gamma_h = \eta_1^{1+\xi}/X_1^{\xi}$ and $s_{t-1,1}/s_{t-1} = 1$ identically) and
$\mu_1 = 1$ (a common propensity to vote multiplies both generations' terms and cancels). The benefit is then
$b_t^1 = [\theta_t h_{t-1,1}\eta_1 + (1-\theta_t)h_{t-1}]\overline{b}_t = \nu_t w_t h_t\tau_t$ whatever $\theta_t$,
and $\epsilon$ has no household to pay. The first-order condition of appendix B.1 for an interior tax is

$$\omega\,\mathcal{E}_{2,t} + \nu_t\,\mathcal{E}_{1,t} = 0. \tag{1.1}$$

The retirees' term, (B.2) with $y_1 = 1$ and $s_{t-1,1}/s_{t-1} = 1$, so that the design drops out of the bracket
$1+\theta_t(y_1-1) = 1$, and with $\partial\ln\Theta_{h,t}/\partial\tau_t = -\xi/((1+\alpha\xi)(1-\tau_t))$ from
appendix A, is

$$\mathcal{E}_{2,t} = \frac{1-\alpha}{\alpha+(1-\alpha)\tau_t} - \frac{(1-\alpha)\,\xi}{(1+\alpha\xi)(1-\tau_t)}. \tag{1.2}$$

The first term is the benefit's share of a retiree's consumption per unit of tax (the pension is
$\frac{1-\alpha}{\alpha}\tau_t$ times the return on savings); the second is the erosion of the base, since the tax
lowers hours.

### 1.2 The young's term

Appendix B prints $\mathcal{E}^i_{1,t} = -\frac{1}{1-\tau_t}\frac{1+\xi}{1+\alpha\xi}(1+\beta)$. Derived from
appendix A's economic equilibrium it is instead the following. By the Euler equation $c_{2,t+1}^i = \beta R_{t+1}
\tilde{c}_{1,t}^i$, the young's indirect utility is $(1+\beta)\ln\tilde{c}_{1,t}^i + \beta\ln R_{t+1} + \beta\ln\beta$.
Three facts about the log-HtM equilibrium give its derivative in $\tau_t$:

1. $\tilde{c}_{1,t}^i = \frac{s_t}{1+\beta}\big[\frac{\eta_i^{1+\xi}}{X_i^{\xi}}\frac{1}{(1+\xi)\Gamma_{s,t}} +
   \frac{1-\alpha}{\alpha}\tau_{t+1}(1-\theta_{t+1})\big]$ (appendix A), whose bracket contains $\tau_{t+1}$ and
   $\theta_{t+1}$ but not $\tau_t$, and $\tau_{t+1}$ is a function of parameters and $\nu_{t+1}$ alone (proposition
   2), so $\partial\ln\tilde{c}_{1,t}^i/\partial\tau_t = \partial\ln s_t/\partial\tau_t$.
2. $s_t = \Theta_{s,t}(s_{t-1}/\nu_t)^{\alpha(1+\xi)/(1+\alpha\xi)}$ with $\Theta_{s,t} = (\Theta_{h,t}/\Gamma_h)^{(1+\xi)/\xi}
   \Gamma_{s,t}$ and $\Gamma_{s,t}$ free of $\tau_t$, so $\partial\ln s_t/\partial\tau_t = \frac{1+\xi}{\xi}
   \frac{\partial\ln\Theta_{h,t}}{\partial\tau_t} = -\frac{1+\xi}{(1+\alpha\xi)(1-\tau_t)}$ (appendix A, proof of
   proposition 1, part i).
3. $R_{t+1} = \alpha(s_t/(\nu_{t+1}h_{t+1}))^{\alpha-1}$ with $h_{t+1} = \Theta_{h,t+1}(s_t/\nu_{t+1})^{\alpha\xi/(1+\alpha\xi)}$
   and $\Theta_{h,t+1}$ free of $\tau_t$ (it depends on $\tau_{t+1}$, $\tau_{t+2}$, $\theta_{t+2}$, all state-free),
   so $\ln R_{t+1} = \text{const} + \frac{\alpha-1}{1+\alpha\xi}\ln s_t$: next period's hours respond to the capital
   stock, which damps the fall in the return from $(\alpha-1)$ to $(\alpha-1)/(1+\alpha\xi)$ per unit of $\ln s_t$.

Hence

$$\mathcal{E}_{1,t} = -\frac{(1+\beta)(1+\xi)}{(1+\alpha\xi)(1-\tau_t)} + \frac{\beta(1-\alpha)(1+\xi)}{(1+\alpha\xi)^2(1-\tau_t)}
= -\frac{1+\xi}{(1+\alpha\xi)(1-\tau_t)}\left(1 + \frac{\beta\alpha(1+\xi)}{1+\alpha\xi}\right), \tag{1.3}$$

which is the code's `dv1i_dτ_LOG` and the technical note's (PEELOG:v1i). The printed $(1+\beta)$ drops the rise in
$R_{t+1}$, the second term of (1.3); A5/T1 fix appendix B, and (1.3) is what the closed form below uses. Nothing is
type-specific in (1.3), so it holds for every $J$.

### 1.3 Solving for the tax

Write $\Psi \equiv (1+\xi)\big(1 + \frac{\alpha\beta(1+\xi)}{1+\alpha\xi}\big)$. Substituting (1.2) and (1.3) into
(1.1) and multiplying by $(1-\tau_t)(1+\alpha\xi)/(1-\alpha)$:

$$\omega\left[\frac{(1+\alpha\xi)(1-\tau_t)}{\alpha+(1-\alpha)\tau_t} - \xi\right] = \frac{\nu_t\Psi}{1-\alpha}
\quad\Longleftrightarrow\quad \frac{(1+\alpha\xi)(1-\tau_t)}{\alpha+(1-\alpha)\tau_t} = \xi + \frac{\nu_t\Psi}{\omega(1-\alpha)} \equiv Q.$$

Cross-multiplying, $(1+\alpha\xi) - Q\alpha = \tau_t[(1+\alpha\xi) + Q(1-\alpha)]$, and with $Q$ written out the
$\alpha\xi$ terms cancel in the numerator and $\alpha\xi + (1-\alpha)\xi = \xi$ in the denominator:

$$\tau_t^{\ast} = \max\left\{0,\;\frac{1 - \frac{\alpha}{1-\alpha}\frac{\nu_t}{\omega}\Psi}{1+\xi+\frac{\nu_t}{\omega}\Psi}\right\}
= \max\left\{0,\;\frac{\omega(1-\alpha) - \alpha\,\nu_t\,\Psi}{\omega(1-\alpha)(1+\xi) + (1-\alpha)\,\nu_t\,\Psi}\right\},
\qquad \Psi \equiv (1+\xi)\left(1 + \frac{\alpha\beta(1+\xi)}{1+\alpha\xi}\right). \tag{1.4}$$

The tax is a function of $\alpha$, $\beta$, $\xi$, $\omega$ and $\nu_t$: the "parameters and demographics alone" of
proposition 2, written out. The $\max$ is the non-negativity constraint; the interior root is positive iff
$\omega(1-\alpha) > \alpha\nu_t\Psi$. No step above is an approximation.

### 1.4 Properties

- **Uniqueness.** Each of the three terms of $\omega\mathcal{E}_{2,t} + \nu_t\mathcal{E}_{1,t}$ is strictly
  decreasing in $\tau_t$ on $[0,1)$ ($(1-\alpha)/(\alpha+(1-\alpha)\tau_t)$ falls, $-1/(1-\tau_t)$ falls), so
  $\mathcal{W}_t$ is strictly concave in $\tau_t$ and (1.4) is the unique maximiser, at a corner when the interior
  root is negative. This is GN's argument; for $J > 1$ the retirees' shares $s_{t-1,i}/s_{t-1}$ depend on the tax
  the old expected and the argument is T2's (A6).
- **Comparative statics.** $\tau_t^{\ast}$ rises with $\omega$ and falls with $\nu_t$ (numerator falls, denominator
  rises), with $\beta$ and with $\alpha$ (both raise $\Psi$, and $\alpha$ also raises $\alpha/(1-\alpha)$), and
  with $\xi$: $\Psi$ rises with $\xi$ since $\partial[(1+\xi)^2/(1+\alpha\xi)]/\partial\xi = (1+\xi)(2-\alpha+\alpha\xi)/(1+\alpha\xi)^2 > 0$,
  and the denominator carries $1+\xi$ besides. A more elastic labor supply lowers the equilibrium tax; at the U.S.
  values the tax at $\xi = 0$ would be $24.2\%$ against $12.3\%$ at $\xi = 0.3$ (section 1.6). GN's first four
  signs are the same; the fifth has no counterpart in GN (section 1.5).
- **Terminal period.** With a finite horizon the young at $T$ have no second period, $\beta \mapsto 0$ in (1.3),
  so $\Psi_T = 1+\xi$ and $\tau_T^{\ast} = [\omega(1-\alpha) - \alpha\nu_T(1+\xi)]/[(1+\xi)(\omega(1-\alpha)+(1-\alpha)\nu_T)]$,
  which the code's terminal period reproduces (section 1.6).
- **The Bismarckian corner for any $J$.** (1.4) is also the log-HtM tax at $\theta_t = 1$ for every income
  distribution and every profile of propensities to vote. At $\theta_t = 1$, with savings formed under that
  design, $s_{t-1,i}/s_{t-1} = y_i$ (proposition 1, part iv) and the bracket of (B.2) is $y_i$, so
  $\mathcal{E}^i_{2,t} = (1-\alpha)\partial\ln\Theta_{h,t}/\partial\tau_t + \frac{1-\alpha}{\alpha}y_i/(y_i + \frac{1-\alpha}{\alpha}\tau_t y_i)$
  is the same for every type, as is $\mathcal{E}^i_{1,t}$ by (1.3); the weights $\sum_i\gamma_i\mu_i$ then
  multiply both generations' terms and cancel from (1.1). The $\theta = 1$ counterfactual of section 6 (the light
  tone in figure 6.1) is therefore (1.4) in closed form; at the current U.S. calibration it is $12.3\%$ (section
  1.6), and C1's rerun can be checked against it at the new $(\beta,\omega)$ for free.
- **What does and does not drop out.** For $J = 1$ the tax is free of $\theta$, but the allocation is not: the
  young perceive the earnings link, so $\Theta_{h,t}$ and $\Gamma_{s,t}$ still depend on $\theta_{t+1}$ and hours
  rise and savings fall with it (section 1.6, block B). The review's "$\theta$ and $\epsilon$ drop out" is right
  for the tax only.

### 1.5 Gonzalez-Eiras and Niepelt (2008)

**Their model** (section 2, Assumption 1): two-period lives, representative agents, log utility, Cobb–Douglas with
full depreciation, $w = A(1-\alpha)(s/n)^{\alpha}$, $R = A\alpha(s/n)^{\alpha-1}$, inelastic labor, a pay-as-you-go
budget $b_t = \tau_t n_t w_t$, probabilistic voting with objective $\omega u(c_{2,t}) + n_t(u(c_{1,t}) + \beta
E_t u(c_{2,t+1}))$, Markov policies $\tau(s_{t-1}, n_t)$. Their marginal objective is
$\frac{\omega(1-\alpha)}{\alpha+(1-\alpha)\tau_t} - n_t\frac{1+\alpha\beta}{1-\tau_t}$ and the tax

$$\tau_t^{W} = \max\left\{0,\;\frac{\omega(1-\alpha) - n_t(1+\alpha\beta)\alpha}{\omega(1-\alpha) + n_t(1+\alpha\beta)(1-\alpha)}\right\} \tag{1.5}$$

(the display below their eq. (6)), unique as the limit of the finite-horizon economy, with the terminal tax
$[\omega(1-\alpha) - n_T\alpha]/[\omega(1-\alpha)+n_T(1-\alpha)]$.

**Mapping of parameters.** Their $n_t$ (young per old) is $\nu_t$; their $\omega$ (per capita weight of retirees
relative to workers) is $\omega$; $\alpha$, $\beta$ as here; their $A$ is the paper's normalisation $A = 1$ (it does
not enter the tax); their $u = \ln$ is log-GHH at $\xi = 0$, where $h_{t,i} = ((\cdot)/X_i)^{\xi} \to 1$ and labor
is inelastic; their benefit $\tau_t n_t w_t$ is $b_t^1 = \nu_t w_t h_t\tau_t$ at $h \equiv 1$; their $E_t$ over
i.i.d. demographic shocks is inert here because the tax depends on $\nu_t$ alone in both models (their
$e_t = E_t[\alpha/(\alpha+(1-\alpha)\tau_{t+1})]$ cancels from $\tau^W$ as the paper's $\tau_{t+1}$ cancels from
(1.3)). Their stochastic-ageing extension (survival probability $p$, annuitised return $R/p$, $\beta \mapsto \beta p$,
$\omega \mapsto \omega p$) is the code's $p$ (`Base.B`, `Base.ω2i`), equal to one in every calibration of the paper.

**Reduction.** At $\xi = 0$, $\Psi = 1+\alpha\beta$ and (1.4) is (1.5) term by term: numerator
$\omega(1-\alpha) - \alpha\nu_t(1+\alpha\beta)$, denominator $\omega(1-\alpha) + (1-\alpha)\nu_t(1+\alpha\beta)$. The
first-order conditions coincide as well: at $\xi = 0$, (1.2) is $\frac{1-\alpha}{\alpha+(1-\alpha)\tau_t}$ and
(1.3) is $-\frac{1+\alpha\beta}{1-\tau_t}$, and GN's decomposition of the young's term (their footnote 18,
$-n_t\frac{1+\beta e_t}{1-\tau_t} + n_t B_t$ with $B_t = \frac{\alpha(1-\alpha)\beta}{1-\tau_t}E_t\frac{1-\tau_{t+1}}{\alpha+(1-\alpha)\tau_{t+1}}$)
sums to the same $-n_t(1+\alpha\beta)/(1-\tau_t)$: the $(1+\beta)$ direct loss less the $\beta(1-\alpha)$ gain from
a higher return is the $\xi = 0$ case of (1.3). The terminal formulas coincide at $\xi = 0$ too. The paper's
heterogeneous-agent equilibrium therefore nests GN exactly.

**Where they differ.**

1. *Labor supply and preferences.* GN's main model has inelastic labor; their extension (section 3, Assumption
   2) has separable preferences $u(c_1) + v(x) + \beta u(c_2)$ and a second labor tax rebated to the young
   ("distortive regulation"), under which the social security tax function is unchanged, $\tau^W$ again, because
   with log consumption utility "contemporaneous social security taxes do not affect labor supply if they are the
   only taxes imposed" (income and substitution effects cancel) and anticipated benefits move hours only through
   a wealth effect. Under GHH there is no income effect: $\tau_t$ lowers hours with elasticity $\xi/(1+\alpha\xi)$
   (the Frisch elasticity damped by the rise in the wage as the capital-labor ratio rises), and $\xi$ enters the
   tax in three places that all vanish at $\xi = 0$: the base erosion in (1.2); the young's loss $(1+\xi)/(1+\alpha\xi)$
   per unit of $1/(1-\tau_t)$ instead of one, since $\tilde{c}_{1,t} \propto s_t \propto h_t^{(1+\xi)/\xi}$; and the
   return gain $(1-\alpha)(1+\xi)/(1+\alpha\xi)^2$ instead of $(1-\alpha)$. The net effect is the fall of
   $\tau_t^{\ast}$ in $\xi$ of section 1.4, which GN's extension does not have. This is also why the paper's
   calibrated $\omega$ exceeds GN's ($1.45$ against $0.92$) for a similar tax target: with $\xi = 0.3$ a
   representative-agent economy at the paper's $\alpha$, $\beta$ and $\nu_{2020}$ needs $\omega = 1.56$ to reach
   $14.4\%$.
2. *Anticipated benefits.* In GN they lower hours (wealth effect); here, for $J = 1$, the earnings link raises
   hours and lowers savings (section 1.4, last point) without touching the tax.
3. *Second instrument.* None here.
4. *Demographics.* Deterministic $\nu_t$ here; the formula is the same.
5. *Heterogeneity.* GN have none, so neither the design nor inequality can appear in (1.5); (1.4) is the
   $J = 1$ face of proposition 2, and the distance from (1.4) to the calibrated tax is what the design and
   inequality add (at the U.S. calibration, $12.3\%$ at the Bismarckian corner against $14.4\%$ observed and
   $18.5\%$ at the Beveridgean corner).

### 1.6 Numerical confirmation

`check_T3.py`, U.S. model, log, common $X$, $\beta = 0.7606$, $\omega = 1.4536$ (baseline reproduced:
$\tau_{2020} = 0.144286$, $R_{2020} = 2.4430$). (A) $\theta \equiv 1$ path: the code's tax equals (1.4) at every
date to $5\times10^{-12}$, the terminal date included with $\beta \mapsto 0$; $\tau_{2020} = 0.1228$, against
$0.1443$ at $\theta^{\ast}$ and $0.1852$ at $\theta \equiv 0$, a difference of $6.24$ p.p. between the corners,
section 6's "$6.2$ p.p." (B) Three identical types ($y_i = 1$, $\mu_i = 1$) at $\theta = 0.2$ and $0.9$: the same
tax as (1.4) to $2\times10^{-12}$ at both, while $h_{2020}$ is $0.6697$ and $0.6823$ and $s_{2020}$ $0.0461$ and
$0.0455$. (C) GN's calibration ($\alpha = 0.2815$, $\beta = 0.4469$, $\omega = 0.9176$) with $\xi = 10^{-7}$ and
$n = 1.3$, $1.375$, $1.45$: the code gives $0.144553$, $0.126185$, $0.109034$, equal to (1.5) to six digits; the
algebraic identity (1.4) at $\xi = 0$ $=$ (1.5) holds to $10^{-16}$ at 24 random parameter points. With the printed
$(1+\beta)$ in place of the bracket of (1.3), the 2020 tax at $\theta = 1$ would be $0.028$.

### 1.7 Placement and proposed wording (W3)

**Recommendation: a paragraph in appendix B.1, right after the expressions (B.2)–(B.4) and before the comparative
statics, plus a parenthetical pointer in section 3.2's sentence "policy is a function of parameters and demographics
only".** A footnote in section 3 is the losing form: it can carry (1.4) and the GN sentence but not the derivation,
the comparative statics in $\xi$ or the Bismarckian-corner remark, and a two-line formula in a footnote interrupts
the section the brief wants left alone; its only advantage, visibility, the pointer supplies. If W3 prefers the
footnote, use the second text below.

Appendix B.1 paragraph (after the displayed $\mathcal{E}$'s, with (1.3)'s corrected young term in place):

```latex
\smalltitle{The representative-agent tax.} With a single type of formal household and no
informal households, $J = 1$ and $\gamma_0 = 0$, relative income and the relative savings
share are one, $y_1 = s_{t-1,1}/s_{t-1} = 1$, so the design drops out of
$\mathcal{E}_{2,t}^1$: both components of the benefit pay the same household. Every term of
the first order condition then falls in $\tau_t$, and its unique solution is
\begin{align}\label{eq:LOG:repAgentTax}
    \tau_t = \max\left\{0,\;\frac{\omega(1-\alpha) - \alpha\,\nu_t\,\Psi}{\omega(1-\alpha)(1+\xi)
    + (1-\alpha)\,\nu_t\,\Psi}\right\}, \qquad
    \Psi \equiv (1+\xi)\left(1 + \frac{\alpha\beta(1+\xi)}{1+\alpha\xi}\right),
\end{align}
which rises with $\omega$ and falls with $\nu_t$, $\alpha$, $\beta$ and $\xi$. With inelastic
labor, $\xi = 0$, \eqref{eq:LOG:repAgentTax} is the equilibrium tax of \textcite{mkvss08},
$\tau_t = [\omega(1-\alpha) - \nu_t(1+\alpha\beta)\alpha]/[\omega(1-\alpha) +
\nu_t(1+\alpha\beta)(1-\alpha)]$, their ratio of workers to retirees being $\nu_t$ and their
per capita weight of retirees $\omega$. The Frisch elasticity enters because GHH preferences
carry no income effect: the tax lowers hours, which erodes the base retirees draw on and
deepens the loss of the young, whereas under the separable preferences of
\textcite{mkvss08} a social security tax that is the only tax leaves hours unchanged and
their formula survives elastic labor. The same expression is the tax at the Bismarckian
corner for any income distribution and any propensities to vote: at $\theta_t = 1$ benefits
and, by part iv of proposition \ref{prop:LOG:EE}, savings are proportional to relative
income, so $\mathcal{E}_{2,t}^i$ is the same for every type and the weights cancel. At the
U.S.\ calibration of section \ref{sec:oecd} it gives \todo{CRRA: tau at theta = 1 in 2020
from C1's rerun, 12.3\% at the current calibration} in 2020.
```

Section 3.2, pointer (no new content): "... that policy is a function of parameters and demographics only
(appendix \ref{app:PEE:LOG} writes it out for a representative agent, where it is the tax of \textcite{mkvss08}
with the Frisch elasticity added), although ...".

Footnote alternative (section 3.2, at the same sentence): "\footnote{With one type of formal household and no
informal households the tax is $\tau_t = \max\{0, [\omega(1-\alpha)-\alpha\nu_t\Psi]/[\omega(1-\alpha)(1+\xi) +
(1-\alpha)\nu_t\Psi]\}$ with $\Psi \equiv (1+\xi)(1+\alpha\beta(1+\xi)/(1+\alpha\xi))$, which at $\xi = 0$ is the
tax of \textcite{mkvss08}; appendix \ref{app:PEE:LOG} derives it.}"

A6's sentence in section 4 ("their uniqueness does not carry over") should say "for a representative agent", since
section 1.4 shows it does carry over at $J = 1$ and at the Bismarckian corner; W2's file, one clause.

## 2. The OECD index and $\theta$ (#13)

### 2.1 Derivation

A retiree of type $i$ at $t$ receives $b_t^i = [\theta_t\eta_i h_{t-1,i} + (1-\theta_t)h_{t-1}]\overline{b}_t$ on
past earnings $w_{t-1}\eta_i h_{t-1,i}$. With $\gamma_0 = 0$, $\overline{b}_t = \nu_t w_t h_t\tau_t/h_{t-1}$, so the
replacement rate, benefit over own past earnings, is

$$\mathrm{RR}_i \equiv \frac{b_t^i}{w_{t-1}\eta_i h_{t-1,i}} = \frac{\overline{b}_t}{w_{t-1}}\left[\theta_t + \frac{1-\theta_t}{y_i}\right]
= \Pi_t\,\tau_t\left[\theta_t + \frac{1-\theta_t}{y_i}\right], \qquad \Pi_t \equiv \frac{\nu_t w_t h_t}{w_{t-1}h_{t-1}}, \tag{2.1}$$

section 7.1's expression. The Bismarckian–Beveridgean index of figure 1.1 is the ratio of the replacement rates at
mean and at half mean earnings, $y = 1$ and $y = 1/2$:

$$I \equiv \frac{\mathrm{RR}(y=1)}{\mathrm{RR}(y=\tfrac12)} = \frac{\theta + (1-\theta)}{\theta + 2(1-\theta)} = \frac{1}{2-\theta},
\qquad \theta = 2 - \frac{1}{I}. \tag{2.2}$$

$\Pi_t\tau_t$ cancels: the index does not see the size of the system or the demography. Under the cost of section
7, $(\theta, 1-\theta)$ become $(A, B) = (f\theta, f(1-\theta))$ and $I = (A+B)/(A+2B) = 1/(2-\theta)$ again, since
$B/(A+B) = 1-\theta$; this is the identification result of appendix C.3 in index form. The map is monotone from
$\theta \in [0,1]$ onto $I \in [1/2, 1]$, with slope

$$\frac{dI}{d\theta} = \frac{1}{(2-\theta)^2} = I^2 \in [\tfrac14, 1], \tag{2.3}$$

so a unit of $\theta$ is worth less in index units the flatter the system: $0.63$ at the U.S. design, $0.48$ at
the UK's, $1$ at the Bismarckian corner. The two scales agree only at the corners, as the review says.

### 2.2 Assumptions

(a) The benefit formula (8a): one flat and one earnings-proportional component, financed by the same gross
revenue, so that the replacement rate is affine in $1/y$. The OECD's progressive formulas (bend points, minimum
and basic pensions, ceilings) are read through their values at two earnings points only. (b) The OECD's replacement
rate is the gross pension entitlement over gross pre-retirement earnings of a full-career worker entering in 2020
at $0.5$ and $1.0$ times average worker earnings, mandatory schemes, men (`data/oecdFigure1.csv`, `bbIndex` $=$
`grr100_men/grr050_men`); the model's earnings is lifetime labor income relative to the mean of formal workers,
$y_i$, constant over time by part ii of proposition 1, and the model's mean has to be the OECD's "average worker".
(c) The two points are exactly $y = 1/2$ and $y = 1$. In the calibrations of sections 5 and 6 the income groups are
cut so that their means sit there, and the paper inverts the general ratio at the group means (technical note,
calibration:theta),

$$\theta = \frac{I/y_1 - 1/y_2}{1 - 1/y_2 - I(1 - 1/y_1)}, \tag{2.4}$$

which is (2.2) when $(y_1, y_2) = (1/2, 1)$; the groups land near, not on, the points (U.S.: $0.5066$ and
$1.0005$), which is why $\theta^{\ast} = 0.738$ differs from $2 - 1/0.7967 = 0.745$. (d) Mandatory private
schemes (Australia, Denmark, the Netherlands, Sweden, Switzerland) are counted in the OECD's rates; the model reads
their earnings-related part as the Bismarckian part of a pay-as-you-go system. (e) $I < 1/2$, a benefit at half
mean earnings more than twice the benefit at the mean, would need $\theta < 0$, which the formula cannot
represent: it arises with means-tested benefits (Australia, $I = 0.4992$). $I > 1$ would need $\theta > 1$ and does
not occur in the sample.

### 2.3 The inverse in the loader (C3)

$\theta_c = \min\{1, \max\{0, 2 - 1/I_c\}\}$ with $I_c$ the country's `bbIndex`. On the 29 of `oecdFigure1.csv` the
clip binds at $0$ for Australia ($-0.003$) and Ireland (exactly $0$) and at $1$ for Austria, Finland, France,
Hungary, Italy, Spain and Turkey, six of the 26 once Turkey is dropped, as the plan says. The U.S. at the OECD
index is $0.735$ ($I = 0.7903$) and the UK $0.559$ ($I = 0.6941$; the paper's $0.560$ at the UK's own groups, which
sit at $0.5001$ and $1.0012$). Setting $\theta$ from $I$ rather than from `getθ` on the group means is right for the
cross-country exercise: (2.2) is exact under the formula and independent of the grouping, whereas (2.4) would move
$\theta$ with the percentiles chosen. For the model-against-data slopes (A14) convert the model's design back with
$I = 1/(2-\theta)$ and regress the index in both, so that the comparison is in one scale whatever the groups.

### 2.4 Design changes in index units (C5)

Exactly under (2.2),

$$\Delta I = \frac{1}{2-\theta_1} - \frac{1}{2-\theta_0} = \frac{\theta_1 - \theta_0}{(2-\theta_1)(2-\theta_0)}
\;\approx\; I_0^2\,\Delta\theta \text{ to first order.} \tag{2.5}$$

At the model's own groups the exact index is $I_m(\theta) = [\theta + (1-\theta)/y_2]/[\theta + (1-\theta)/y_1]$,
which reproduces the datum at $\theta^{\ast}$ by construction ($0.7967$ for the U.S.); for changes the two differ by
less than $0.001$ at the U.S. groups, so (2.5) is the formula to use, and it is the one C3 inverts. Current numbers
(to be redone by C5 after A2 moves $\theta^{\ast}$ to $0.728$ and the path with it): $0.738 \to 0.797$ (2050) is
$\Delta I = 0.039$; $0.738 \to 0.809$ (2110 on) is $0.047$, the review's "about $0.05$"; the UK under the U.S.
$\lambda$, $0.560 \to 0.625$, is $0.033$; the full range $\theta \in [0,1]$ is $I \in [0.5, 1]$ and the U.S. to
the Bismarckian corner is $0.21$. For reference, PaG 2021's $39.2/49.6 = 0.7903$ gives $\theta = 0.728$ by (2.4) at
the model's groups (A2's number) and $0.735$ by (2.2).

### 2.5 Numerical confirmation

`check_T3.py` block E: `getθ` on the U.S. test model equals (2.4) at $y = (0.5066, 1.0005)$ and reproduces
`RR0` $= 0.7967$ through $I_m(\theta^{\ast})$; the clip counts and the conversions above are computed there.

### 2.6 Proposed wording (W6)

Section 7.3's return to figure 1.1 (or wherever the design is first read against the figure), one sentence
block, with numbers from C5:

```latex
The index of figure \ref{fig:US:OECDdata} and the design are two scales for one object. Under
the benefit formula \eqref{eq:model:governmentBudget} a retiree's replacement rate at relative
income $y$ is $\Pi_t\tau_t[\theta + (1-\theta)/y]$, so the ratio of the replacement rates at
mean and at half mean earnings is $I = 1/(2-\theta)$, from $1/2$ at the Beveridgean corner to
$1$ at the Bismarckian one, and the size of the system and the cost cancel from it. The U.S.\
design $\theta^{\ast} = \todo{CRRA: theta*}$ is $I = \todo{CRRA: I}$ and a unit of $\theta$ is
worth $I^2$, about $0.6$, units of the index there. In index units the rise of the design
along the projected demography, from \todo{CRRA: theta 2020} to \todo{CRRA: theta 2110}, is
\todo{CRRA: dI}, against a cross-section that runs from $0.50$ to $1$.
```

The new 26-country appendix (W6): "Each country's inherited design is set from its index by $\theta = 2 - 1/I$,
the inverse of $I = 1/(2-\theta)$, and clipped to $[0,1]$: Australia and Ireland sit at the Beveridgean corner and
six countries at the Bismarckian one, which no finite cost parameter reaches (section \ref{sec:esc:cost}). The
model's designs are converted back to the index before the slopes are compared." If W5 wants appendix F to say
why $\theta^{\ast} = 0.738$ is not $2 - 1/I$, the sentence is (2.4) with the U.S. group means; that is W5's file.

## 3. The cost parameter and the elasticities (#22)

### 3.1 Definitions

$\Pi_t \equiv \nu_t w_t h_t/(w_{t-1}h_{t-1})$, the pay-as-you-go return factor of section 7.1: by the budget with
$\gamma_0 = 0$ it equals $\overline{b}_t/(\tau_t w_{t-1})$, the benefit per unit of past earnings that a purely
earnings-related system pays per unit of contribution rate, and it is the number of workers per retiree times the
growth of labor income per worker between the contribution date and the benefit date (Aaron's condition). In a
stationary economy without productivity growth $\Pi_t = \nu_t$; on the U.S. baseline path $\Pi_{2020} = 1.355$,
$\nu_{2020} = 1.340$ times a wage-bill growth of $1.012$. $R_t = \alpha(s_{t-1}/(\nu_t h_t))^{\alpha-1}$ is the
thirty-year gross return, $2.443$ in 2020 (the target that identifies $\beta$ in table `US:Calib`; `R0` in the code). Section 7.1's wedge is
$t_i = \Pi_t\tau_t(1-\theta_t)(1-1/y_i)$ per unit of past earnings, a date-$t$ amount per unit of date-$(t-1)$
earnings, and $\tilde V = \sum_i\gamma_i(y_i-1)^2/y_i$.

### 3.2 Derivation with the lag

1. *The base.* Type $i$ brings earnings $e_i = y_i$ into the system at $t-1$, per unit of mean earnings and in
   date-$(t-1)$ goods.
2. *The rate.* Relative to the earnings-related benchmark, the flat component changes type $i$'s benefit at $t$ by
   $-t_i$ per unit of earnings. A worker at $t-1$ values a date-$t$ unit at $1/R_t$: this is how the labor supply
   condition (6a) prices the benefit, $\partial b^i_{t+1}/\partial h_{t,i}$ divided by $R_{t+1}$, and it is the
   Euler equation's marginal rate of substitution for a formal saver. Participation and taxable-income
   elasticities are defined against the net-of-tax share of earnings at the time they are made, so the implicit
   tax rate in their units is $t_i/R_t$, not $t_i$.
3. *The loss.* A proportional tax at rate $t$ on a base $e$ with elasticity $\varepsilon$ with respect to its
   net-of-tax rate costs $\frac12\varepsilon t^2 e$ to second order (Harberger). Dropped: terms of order $t^3$ and
   the first-order revenue effect of the base response, which nets to zero across types since
   $\sum_i\gamma_i y_i t_i = 0$ (#21: the triangle is excess burden, booked against revenue by choice). Per unit of
   mean past earnings, in date-$(t-1)$ goods,
   $$L = \tfrac12\varepsilon\sum_i\gamma_i\left(\frac{t_i}{R_t}\right)^2 y_i = \tfrac12\varepsilon\left(\frac{\Pi_t}{R_t}\right)^2\tau_t^2(1-\theta_t)^2\tilde V. \tag{3.1}$$
4. *Revenue.* Per unit of mean past earnings the system pays $\Pi_t\tau_t$ at $t$, which is $\Pi_t\tau_t/R_t$ in
   date-$(t-1)$ goods.
5. *The share.* Both in date-$(t-1)$ goods, or both carried to $t$ by the factor $R_t$, the ratio is the same:
   $$\frac{L}{\text{revenue}} = \tfrac12\,\varepsilon\,\frac{\Pi_t}{R_t}\,\tau_t\,(1-\theta_t)^2\,\tilde V. \tag{3.2}$$
6. *The match.* The share of revenue lost under the paper's cost is $1 - f = 1 - \exp(-\frac12\lambda\tau_t\tilde V(1-\theta_t)^2)
   = \frac12\lambda\tau_t\tilde V(1-\theta_t)^2$ to first order in the exponent (dropped: its square and higher,
   $0.0002$ at the calibrated design, where the exponent is $0.019$). Matching (3.2),
   $$\lambda \approx \varepsilon\,\frac{\Pi_t}{R_t}. \tag{3.3}$$

The paper's $\lambda \approx \varepsilon\Pi_t$ (appendix C.2, "Magnitude" and the footnote on absorbing the return
factor) is (3.3) at $R_t = 1$, that is, it treats the elasticities as if measured against the undiscounted
transfer. If workers discount future benefits more than the market, as hand-to-mouth workers do, or doubt that the
benefits will be paid, the effective rate is smaller still, so (3.3) is an upper bound on what a given elasticity
delivers. Nothing in the model's equilibrium changes: (3.3) only reinterprets the calibrated number.

### 3.3 What changes in the comparison

With $\Pi_{2020}/R_{2020} = 1.355/2.443 = 0.555$, elasticities of $0.1$ to $0.4$ imply $\lambda$ between $0.055$
and $0.222$ ($0.139$ at Chetty et al.'s $0.25$), not $0.13$ to $0.54$. The multiples of the calibrated values
(table `US_ESC:calibration`, to be recomputed by C5 at the A2 calibration; $R_{2020}$ stays at its target and $\Pi_{2020}$ will
again be close to $\nu_{2020}$, so the factor $R \approx 2.44$ is stable):

| $\rho$ | $\lambda$ | multiple at $\lambda \approx \varepsilon\Pi$ (paper) | multiple at $\lambda \approx \varepsilon\Pi/R$ |
|---|---|---|---|
| 0.5 | 18.267 | 34–135 (printed 34–140) | 82–329 |
| 1.0 | 8.643 | 16–64 | 39–156 |
| 2.0 | 1.724 | 3–13 | 8–31 |

Formula for C5: $\lambda_{\varepsilon} = \varepsilon\,\Pi_{2020}/R_{2020}$ and the multiple $\lambda R_{2020}/(\varepsilon\Pi_{2020})$
for $\varepsilon \in \{0.1, 0.4\}$, with $\Pi_{2020} = \nu_{2020}w_{2020}h_{2020}/(w_{1990}h_{1990})$ from the
baseline report (`EE_report`'s `w`, `h`) and $R_{2020}$ from the same report. Section 7.2's sentence keeps "by more
than an order of magnitude at $\rho \leq 1$" and gains "and by about one at $\rho = 2$"; the attribution to
administrative, evasion and political costs is strengthened, not weakened.

Two consequences beyond the sentence. (i) The factor the cost parameter absorbs is $\Pi_t/R_t$, not $\Pi_t$. Along
the baseline it is $0.565$ in 1990, $0.555$ in 2020, $0.513$ in 2050, $0.473$ in 2080 and $0.465$ in 2110, falling
by $16\%$ from 2020 while $\Pi_t$ alone falls by $22\%$ and $\nu_t$ by $20\%$, because $R_t$ falls with ageing too
(capital deepening). The $\Pi$-inclusive cost variant of A8/C1, if it scales the loss by $\nu_t$ or $\Pi_t$,
overstates the demographic drift of a structural cost; the Harberger-consistent factor is $\Pi_t/R_t$. Both
$\Pi_t$ and $R_t$ depend on the state ($s_{t-1}$, $h_t$), so a cost that keeps either breaks the state independence
of the log design choice (the separability proposition of appendix C.4); that is a decision for the lead, not for this note. (ii) $1 - \Pi_t/R_t
= 0.445$ in 2020 is Summers' tax component of the whole contribution even in a purely earnings-related system,
common to all types and designs, which is why it does not bear on the design and why the paper's wedge is the
redistributive part only; one clause in appendix C.2 would pre-empt a referee asking where that part went.

### 3.4 Numerical confirmation

`check_T3.py` block D, baseline path ($\theta^{\ast}$ pinned, $\lambda = 0$): $\Pi_{2020} = 1.3551$, $R_{2020} = 2.4430$,
$\Pi_{2020}/R_{2020} = 0.5547$; the implied ranges and multiples of the table above; the path of $\Pi_t/R_t$.

### 3.5 Proposed wording

Section 7.2 (W6), replacing "At every elasticity $\lambda$ lies above what participation and taxable-income
elasticities alone would imply, by more than an order of magnitude at $\rho \leq 1$, so ...":

```latex
At every elasticity $\lambda$ lies above what participation and taxable-income elasticities
alone would imply, by more than an order of magnitude at $\rho \leq 1$ and by about one at
$\rho = 2$, so the cost also stands in for administrative, evasion and political costs of
redistribution that the model does not contain (appendix \ref{app:esc:cost}).
```

Section 7.2's footnote on the ageing channel (W6): "... $\lambda$ absorbs the ratio of the pay-as-you-go return
factor to the market return, which falls as the population ages (appendix \ref{app:esc:cost}), and a cost that
kept the ratio would grow less."

Appendix C.2 (W7), the "Magnitude" paragraph and the footnote to "Specification":

```latex
\smalltitle{Magnitude.} The shape of $f$ follows from the tax component; its size does not.
The wedge \eqref{eq:esc:implicitTax} is a date-$t$ amount per unit of date-$(t-1)$ earnings,
while participation and taxable-income elasticities are measured against the net-of-tax
share of earnings at the time they are made. The rate that enters the loss is therefore the
wedge discounted at the return a worker forgoes, $t_i/R_t$, which is how the labor supply
condition \eqref{eq:model:formalFOCs} prices future benefits. Per unit of mean past earnings
the loss is then $\frac{1}{2}\varepsilon(\Pi_t/R_t)^2\tau_t^2(1-\theta_t)^2\tilde{V}$ against
revenue of $\Pi_t\tau_t/R_t$, both in date-$(t-1)$ goods, so the share of revenue lost is
$\frac{1}{2}\varepsilon\,(\Pi_t/R_t)\,\tau_t(1-\theta_t)^2\tilde{V}$ and $\lambda$ corresponds
to $\varepsilon\Pi_t/R_t$. In the U.S.\ calibration for 2020, $\Pi_t = \todo{CRRA: Pi 2020}$
and $R_t = 2.44$ (table \ref{table:US:Calib}), so participation and taxable-income
elasticities of $0.1$ to $0.4$ \parencite{ChettyGMW11a1,SaezSG12a1} correspond to $\lambda$
between about $\todo{CRRA: 0.06}$ and $\todo{CRRA: 0.22}$. The calibrated values of section
\ref{sec:esc} are \todo{CRRA: multiples at rho = 0.5, 1, 2} times that range, so $\lambda$
also stands in for administrative, evasion and political costs of redistribution that the
model does not contain. A worker who discounts future benefits more heavily than the market,
or doubts that they will be paid, faces a smaller wedge still, so the range is an upper bound
on what the elasticities alone deliver. The rest of the contribution, $1 - \Pi_t/R_t$ per unit
even in a purely earnings-related system, is a tax on every type alike and does not bear on
the design.
```

Footnote (replacing "The return factor multiplies every implicit tax alike ..."): "The factor $\Pi_t/R_t$
multiplies every implicit tax alike and so scales the loss once. It carries $\nu_t$ and would make a structural
cost parameter drift with demographics, from $\todo{CRRA: 0.56}$ in 2020 to $\todo{CRRA: 0.47}$ in 2110 along the
baseline path; we absorb it into $\lambda$, which is calibrated rather than derived."

## Formulas for C3 and C5

- **C3, loader.** $\theta_c = \min\{1,\max\{0,\,2 - 1/I_c\}\}$, $I_c$ = `bbIndex` (men). Back-conversion for the
  slopes: $I = 1/(2-\theta)$, regress $I$ in data and model alike.
- **C5, #13.** $\Delta I = (\theta_1-\theta_0)/((2-\theta_1)(2-\theta_0))$, first order $I_0^2\Delta\theta$ (2.5);
  the level $I = 1/(2-\theta)$. Headline numbers only (decision 1).
- **C5, #22.** $\lambda_{\varepsilon} = \varepsilon\Pi_{2020}/R_{2020}$, multiple $= \lambda R_{2020}/(\varepsilon\Pi_{2020})$,
  $\varepsilon \in \{0.1, 0.4\}$; $\Pi_{2020} = \nu_{2020}w_{2020}h_{2020}/(w_{1990}h_{1990})$ and $R_{2020}$ from
  the baseline report; the path $\Pi_t/R_t$ for the footnote.
- **C1/C5, a free check of the rerun.** At $\theta \equiv 1$ the log tax at every date must equal (1.4) at the
  recalibrated $(\beta, \omega)$ and the date's $\nu_t$; the U.S. shocks' $\theta = 1$ row in 2020 is (1.4) at
  $\nu_{2020}$.
