# Proposition 2 at the fixed point of tax and savings shares (T1)

Package T1 of `notes/plan_reviewResponse.md` (A5, detailed comments #1 and #10 of the review of 2026-10-22).
Written 2026-10-23 by the model-theorist (Fable), read-only against `writing/Paper/Sections/Log.tex`,
`writing/Paper/Appendix/PoliticoEconomicEquilibrium.tex` (B.1), `writing/Paper/Appendix/EconomicEquilibrium.tex`,
`writing/informalAnalytical/model_PEE.tex` and `python/informalAnalytical/base.py`. Notation is the paper's
(`notes/paper_styleGuide.md` §4); parameters are constant over time as in section 3. The code's vintage-$(t-1)$
parameters and its $p_{t-1}/\kappa_{t-1}$ in place of $1/(1+\gamma_0\epsilon)$ generalize this and change nothing below.
The intended reader is the writer of W3 (paper-writer-lead); parts (a) and (b) at the end are for them.

## Overturned

- **The fallback of decision 5 is not available.** Decision 5 says that if the inequality step fails at consistent
  shares, Proposition 2 states inequality at the inherited distribution. At the inherited distribution a
  mean-preserving spread of incomes leaves the tax unchanged when $\theta = 0$ and *lowers* it when $\theta > 0$ and
  $s_{t-1,i}/(c_{2,t}^i)^2$ falls with income, as it does at both calibrations (§2, remark R5, equation (27)). The
  inequality result is a result about the savings distribution: it exists only at the fixed point. The fallback is
  also not needed, since the inequality step at consistent shares holds for $J$ types (§2).
- Nothing else in the brief is overturned. The $\theta$ step holds at the fixed point as the scratch check of
  2026-10-23 found, but under a condition the brief did not state: the weight $y_i/(c_{2,t}^i)^2$ must fall with
  income, which holds whenever no formal type borrows against its pension, (18)–(19). Without it a counterexample
  exists (remark R4).

## Recommendation (decision 5)

State both $\theta$ and inequality at the fixed point, where retirees' savings shares are consistent with the tax
and the design they anticipated; state $\epsilon$ at the inherited distribution. The losing form, both results at
the inherited distribution, would cost both results: the $\theta$ effect is then ambiguous (the review's two-type
example, remark R1, (20)), and the inequality effect is zero or of the wrong sign (R5, (27)). The fixed point is
also the right object for the proposition's claim, which compares equilibrium taxes across economies that differ
in a parameter, so that retirees saved knowing the design; the inherited distribution is the right object for an
unanticipated reform, which is how $\epsilon$ enters the paper (Argentina, after C2 fixes #4).

## 0. Objects and the first-order condition

Formal types $i = 1,\dots,J$ with masses $\gamma_i$, $\sum_{i>0}\gamma_i = 1$; informal type 0, hand-to-mouth, mass
$\gamma_0$. Define

$$y_i \equiv \frac{\eta_i^{1+\xi}}{X_i^{\xi}}\frac{1}{\Gamma_h} = \frac{\eta_i h_{t-1,i}}{h_{t-1}}, \qquad \sum_{i>0}\gamma_i y_i = 1, \tag{1}$$

the relative labor income of type $i$ (proposition 1, part ii; independent of policy),

$$a_t \equiv \frac{1-\alpha}{\alpha}\frac{\tau_t}{1+\gamma_0\epsilon} = \frac{h_{t-1}\overline{b}_t}{R_t s_{t-1}}, \tag{2}$$

the average formal pension relative to the average capital income of formal retirees (the ratio of the wage bill to
capital income is $(1-\alpha)/\alpha$ under Cobb–Douglas, so $a_t$ does not depend on $\nu_t$ or on the state), and

$$p_i \equiv 1 + \theta\,(y_i - 1) = \frac{b_t^i}{h_{t-1}\overline{b}_t}, \tag{3}$$

type $i$'s pension relative to the average formal pension, from (8a). Write $x_i \equiv s_{t-1,i}/s_{t-1}$ for the
inherited savings share. Appendix A's consumption function for formal retirees is then

$$c_{2,t}^i = R_t s_{t-1}\,D_i, \qquad D_i \equiv x_i + a_t\,p_i, \tag{4}$$

since $R_t s_{t-1} = \alpha\nu_t h_t^{1-\alpha}(s_{t-1}/\nu_t)^{\alpha}$. The pension's share of consumption and the
marginal revenue of the tax relative to its base are, as in B.1,

$$\sigma_t^i \equiv \frac{b_t^i}{c_{2,t}^i} = \frac{a_t p_i}{D_i}, \qquad \sigma_t^0 \equiv \frac{b_t^0}{\tilde{c}_{2,t}^0}, \qquad
\phi_t \equiv 1 + (1-\alpha)\tau_t\frac{\partial\ln\Theta_{h,t}}{\partial\tau_t} = 1 - \frac{(1-\alpha)\xi}{1+\alpha\xi}\frac{\tau_t}{1-\tau_t}. \tag{5}$$

$\phi_t > 0$ if and only if $\tau_t < \bar{\tau} \equiv (1+\alpha\xi)/(1+\xi)$, the revenue-maximizing rate (revenue is
proportional to $\tau_t(1-\tau_t)^{(1-\alpha)\xi/(1+\alpha\xi)}$); $\bar{\tau} = 0.85$ at the Argentine and $0.84$ at the
U.S. values of $\alpha$ and $\xi$. The marginal supports of B.1, (B.1)–(B.2), read

$$\mathcal{E}_{2,t}^i = \frac{\phi_t - 1 + \sigma_t^i}{\tau_t}, \qquad \mathcal{E}_{2,t}^0 = \frac{\phi_t\,\sigma_t^0}{\tau_t}, \tag{6}$$

and the young's, (B.3)–(B.4) with the correction of §5,

$$\mathcal{E}_{1,t}^i = -\frac{1}{1-\tau_t}\frac{1+\xi}{1+\alpha\xi}\left(1+\beta\frac{\alpha(1+\xi)}{1+\alpha\xi}\right), \qquad
\mathcal{E}_{1,t}^0 = -\frac{\beta}{1-\tau_t}\frac{\alpha(1+\xi)^2}{(1+\alpha\xi)^2}. \tag{7}$$

Neither (7) nor $\phi_t$ depends on $\theta$, $\epsilon$, $\nu_t$ or the $y_i$. With propensities to vote $\mu_j$ (those of
the retirees' own cohort for the old), the first-order condition for an interior tax is

$$\mathcal{F}_t \equiv \omega\Big[\gamma_0\mu_0\,\mathcal{E}_{2,t}^0 + \sum_{i>0}\gamma_i\mu_i\,\mathcal{E}_{2,t}^i\Big]
+ \nu_t\Big[\gamma_0\mu_0\,\mathcal{E}_{1,t}^0 + \sum_{i>0}\gamma_i\mu_i\,\mathcal{E}_{1,t}^i\Big] = 0. \tag{8}$$

**Consistent shares.** Proposition 1, part iii (equation (13) of the draft), one period back and with $B = \beta$,
gives the shares generation $t-1$ chose when it anticipated the tax $\tau_t$ and the design $\theta$ for its
retirement. In equilibrium the anticipated and the realized policy coincide, so

$$x_i(\tau_t,\theta) = y_i + \frac{a_t(1-\theta)}{1+\beta}\,(y_i - 1). \tag{9}$$

Poorer types save less than their income share because the flat part of the pension substitutes for savings
(part iv). Substituting (9) and (3) in (4),

$$D_i = y_i + \frac{a_t(1-\theta)}{1+\beta}(y_i-1) + a_t + a_t\theta(y_i - 1) = 1 + a_t + (1 + a_t\psi)(y_i - 1), \qquad
\psi \equiv \theta + \frac{1-\theta}{1+\beta} = \frac{1+\beta\theta}{1+\beta}\in\Big[\tfrac{1}{1+\beta},1\Big]. \tag{10}$$

Equivalently $D_i = (1+a_t\psi)\,y_i + a_t(1-\psi)$ with $a_t(1-\psi) = a_t\beta(1-\theta)/(1+\beta)$: retirement
consumption is affine in relative income, with slope above one and an intercept equal to the consumption of a
hypothetical retiree without labor income, the flat pension net of the fraction $1/(1+\beta)$ borrowed against it
when young. Two facts are used throughout: $D_i$ increases in $y_i$ (slope $1+a_t\psi > 0$) and in $a_t$ (slope
$1-\psi+\psi y_i > 0$).

**The fixed point and the sign of a comparative static.** Let $G_t(\tau_t;\pi)$ denote $\mathcal{F}_t$ with
$x_i = x_i(\tau_t,\theta)$ from (9), for a parameter $\pi$. The equilibrium tax solves $G_t(\tau_t;\pi) = 0$: it is a
fixed point between the tax and the expectations embedded in past savings, and it is what `policy.LOG.stateGrid`
evaluates (the shares are rebuilt at every candidate tax, at the vintage $t-1$ parameters). By the implicit
function theorem $d\tau_t/d\pi = -(\partial G_t/\partial\pi)/(\partial G_t/\partial\tau_t)$, so the sign of a comparative
static is the sign of $\partial G_t/\partial\pi$ once $\partial G_t/\partial\tau_t < 0$.

**Lemma 1 (monotonicity at consistent shares).** Assume every formal type's consistent savings are nonnegative,
$x_i \geq 0$. On $0 < \tau_t < \bar{\tau}$ every term of $G_t$ is strictly decreasing in $\tau_t$: (i) the young's terms
(7) are a negative constant over $1-\tau_t$; (ii) in (6), $(\phi_t - 1)/\tau_t = -\frac{(1-\alpha)\xi}{1+\alpha\xi}\frac{1}{1-\tau_t}$
falls, and $\sigma_t^i/\tau_t = \frac{1-\alpha}{\alpha(1+\gamma_0\epsilon)}\,p_i/D_i$ falls because $D_i$ rises with
$a_t \propto \tau_t$ by (10); (iii) $\mathcal{E}_{2,t}^0 = \phi_t\cdot\frac{b_t^0/\tau_t}{e_t + b_t^0}$ with $e_t$ the
endowment (independent of $\tau_t$) and $b_t^0$ proportional to revenue, which rises on $(0,\bar{\tau})$ while
$b_t^0/\tau_t$ falls; $\phi_t$ is positive and falling. For $\tau_t \geq \bar{\tau}$, $\phi_t \leq 0$ and, since
$\sigma_t^i < 1$ when $x_i > 0$, every term of $G_t$ is negative. Hence an interior equilibrium has $\phi_t > 0$, is the
unique root of $G_t$ in $(0,1)$, and $\partial G_t/\partial\tau_t < 0$ there. (T2's note owns uniqueness; B.1 needs the
lemma only for the sign, and currently asserts it in one clause before (B.5).)

## 1. The earnings link $\theta$ at the fixed point

**Scope.** $\theta$ enters $G_t$ (a) through $p_i$ and $x_i$, the design in force at $t$, which pays the current
retirees and which they anticipated, and (b) through $\Theta_{h,t}$, which depends on the design the current young
anticipate for their own pension, $\theta_{t+1}$ in the paper's section 7 timing (appendix A, equation for
$\Theta_{h,t}$, via $\theta\tau_{t+1}\Gamma_{s,t}$). Channel (b) reaches only $\mathcal{E}_{2,t}^0$: for a formal retiree
$b_t^i$ and $R_t s_{t-1,i}$ both scale with $h_t^{1-\alpha}$, so $\sigma_t^i$ is independent of hours, while the informal
retiree's endowment does not move with $h_t$. The result below is for (a); remark R3 gives (b).

**Derivation.** At consistent shares, from (3) and (9),

$$\frac{\partial D_i}{\partial\theta} = \frac{\partial x_i}{\partial\theta} + a_t(y_i - 1) = -\frac{a_t(y_i-1)}{1+\beta} + a_t(y_i-1) = \frac{\beta}{1+\beta}\,a_t(y_i - 1), \tag{11}$$

so

$$\frac{\partial\sigma_t^i}{\partial\theta} = \frac{a_t(y_i-1)D_i - a_tp_i\,\partial D_i/\partial\theta}{D_i^2}
= \frac{a_t(y_i-1)}{D_i^2}\Big[x_i + a_tp_i - \frac{\beta}{1+\beta}a_tp_i\Big] = \frac{a_t(y_i-1)}{D_i^2}\Big[x_i + \frac{a_tp_i}{1+\beta}\Big],$$

and, substituting (9) and (3), $x_i + \frac{a_tp_i}{1+\beta} = y_i + \frac{a_t}{1+\beta}\big[(1-\theta)(y_i-1) + 1 + \theta(y_i-1)\big] = y_i\big(1+\frac{a_t}{1+\beta}\big)$. Hence

$$\frac{\partial\sigma_t^i}{\partial\theta}\Big|_{x_i = x_i(\tau_t,\theta)} = a_t\left(1+\frac{a_t}{1+\beta}\right)\frac{y_i\,(y_i-1)}{D_i^2}. \tag{12}$$

Since (7), $\phi_t$ and $\mathcal{E}_{2,t}^0$ do not depend on the design in force,

$$\frac{\partial G_t}{\partial\theta} = \frac{\omega\,a_t}{\tau_t}\left(1+\frac{a_t}{1+\beta}\right)\sum_{i>0}\gamma_i\,\mu_i\,\frac{y_i}{D_i^2}\,(y_i - 1). \tag{13}$$

The weight is $y_i/D_i^2 \propto y_i/(c_{2,t}^i)^2$: what the brief and A5 call "weight $y_i/c_i^2$". With
$w_i \equiv \mu_i y_i/D_i^2$ and $\sum_i\gamma_i(y_i - 1) = 0$, the identity appendix C uses for proposition 3 gives

$$\sum_{i>0}\gamma_i\,w_i\,(y_i - 1) = \sum_{i,j}\gamma_i\gamma_j\,w_i\,(y_i - y_j) = \frac{1}{2}\sum_{i,j}\gamma_i\gamma_j\,(w_i - w_j)(y_i - y_j), \tag{14}$$

which is negative when $w$ and $y$ are oppositely ordered across types, strictly when incomes differ (Chebyshev's sum
inequality). Therefore $\partial G_t/\partial\theta < 0$, and by Lemma 1 $\partial\tau_t/\partial\theta < 0$, under

$$\text{(C$\theta$)}\qquad \mu_i\,\frac{y_i}{(c_{2,t}^i)^2}\ \text{ is decreasing in income across the formal types.} \tag{15}$$

**Equal propensities.** $w(y) = y/D(y)^2$ with $D$ affine, so

$$\frac{d\ln w}{dy} = \frac{1}{y} - \frac{2(1+a_t\psi)}{D(y)} = \frac{a_t(1-\psi) - (1+a_t\psi)\,y}{y\,D(y)}, \tag{16}$$

negative if and only if $y > y^*$. $w$ rises on $(0,y^*)$ and falls beyond, so (15) holds for every distribution whose
lowest income exceeds

$$y^* \equiv \frac{a_t(1-\psi)}{1+a_t\psi} = \frac{a_t\,\beta\,(1-\theta)}{1+\beta+a_t(1+\beta\theta)}. \tag{17}$$

Three equivalent or sufficient forms, all from $D_i > 2a_t(1-\psi)$:

$$\frac{\partial\ln c_{2,t}^i}{\partial\ln y_i} = \frac{(1+a_t\psi)\,y_i}{D_i} > \frac{1}{2}\quad\Longleftrightarrow\quad
c_{2,t}^i > \frac{2\beta}{1+\beta}\,(1-\theta)\,h_{t-1}\overline{b}_t \quad\text{for every } i>0, \tag{18}$$

that is, every formal retiree consumes more than $2\beta/(1+\beta)$ times the flat pension (twice the consumption of
the hypothetical retiree without labor income), and

$$s_{t-1,i} \geq 0 \text{ for every } i > 0 \quad\Longrightarrow\quad (18), \tag{19}$$

because then $D_i \geq a_tp_i \geq a_t(1-\theta) > \frac{2\beta}{1+\beta}a_t(1-\theta)$ for $\beta < 1$. (19) is the condition
to put in the proposition: no formal type borrows against its pension. At consistent shares $s_{t-1,i} \geq 0$ iff
$y_i \geq a_t(1-\theta)/(1+\beta+a_t(1-\theta))$: 0.017 at the Argentine hand-to-mouth calibration, 0.16 at the
U.S. values with $\theta = 0$ and $\tau_t = 0.144$, 0.05 at $\theta = 0.738$. The lowest incomes are 0.46 and 0.51.

**Unequal propensities.** For two adjacent types (15) is $\mu_H/\mu_L < \frac{y_L}{y_H}\big(c_{2,t}^H/c_{2,t}^L\big)^2$,
tighter than the inequality condition of §2 by the factor $y_L/y_H$ and close to C.1's corner threshold
$c_{2,t}^H/c_{2,t}^L$ because retirement consumption is nearly proportional to income (the elasticity in (18) is
0.95–0.99 at the calibrations). At the U.S. groups with CPS turnout the bounds are 1.87 and 2.12 against observed
ratios 1.33 and 1.22 (§7).

**Remarks.**

- R1 (*the inherited distribution*). Holding $x_i$ fixed, as B.1 does now, $\partial\sigma_t^i/\partial\theta = a_t(y_i-1)\,x_i/D_i^2$
  and the weight is $x_i/(c_{2,t}^i)^2$, which need not fall with income: $x_i$ rises with $y_i$ faster than $y_i$
  does when $\theta < 1$ (by (9)). The review's example ($y \in \{0.5,1.5\}$, equal masses, $\theta = 0$, $\beta = 1$,
  $a_t = 1$) gives

  $$\textstyle\sum_i\gamma_i\,x_i(y_i-1)/D_i^2 = +0.018 \quad\text{but}\quad \sum_i\gamma_i\,y_i(y_i-1)/D_i^2 = -0.030, \tag{20}$$

  so a surprise change in the design in force has an ambiguous effect while the anticipated one does not. This is
  comment #1's point, and the reason the current B.1 proof does not establish the proposition.
- R2 (*the Bismarckian corner*). At $\theta = 1$, $\psi = 1$ and $D_i = (1+a_t)y_i$, so with equal propensities

  $$\frac{\partial G_t}{\partial\theta}\Big|_{\theta=1} = -\frac{\omega\,a_t}{\tau_t}\left(1+\frac{a_t}{1+\beta}\right)\frac{\tilde{V}}{(1+a_t)^2}, \qquad \tilde{V} = \sum_i\gamma_i\frac{(y_i-1)^2}{y_i} = \sum_i\gamma_i\frac{1}{y_i} - 1, \tag{21}$$

  the dispersion of relative incomes of section 7 (equation (16) of the draft). Checked numerically to 2e-5.
- R3 (*a permanent change in $\theta$ with a universal pension*). Channel (b) adds

  $$\frac{\partial\mathcal{E}_{2,t}^0}{\partial\theta_{t+1}} = \mathcal{E}_{2,t}^0\,(1-\sigma_t^0)\,(1-\alpha)\,\frac{\partial\ln\Theta_{h,t}}{\partial\theta_{t+1}} \geq 0, \tag{22}$$

  since hours rise with the anticipated earnings link (proposition 1, part i): a more Bismarckian design raises the
  tax base and so the universal pension relative to the informal endowment. It is zero when $\gamma_0\epsilon = 0$ (the
  U.S., UK and French calibrations) and is $0.0087$ against $-0.554$ for (13) at the Argentine hand-to-mouth
  calibration, 1.6% of the direct effect and of the opposite sign. A permanent change also moves $\tau_{t+1}$, which
  enters $z_t$ through $\Theta_{h,t}$ in the same term only (the backward recursion of `num_peeLOG.tex`); the clean
  statement is therefore for the design in force given the continuation, exact without a universal pension.
- R4 (*where (18) fails*). With $a_t = 1$, $\beta = 1$, $\theta = 0$ ($y^* = 1/3$) and equal masses at $y \in \{0.02, 1.98\}$,
  the poorer type has $x_L = -0.47$, consumes 0.53 against a flat pension of 1 and has $\sigma_L = 1.9$; the sum in
  (13) is $+0.046$ and the tax rises with $\theta$. The type's support is almost independent of $\theta$ because a retiree
  without labor income has both pension and consumption proportional to $1-\theta$. The condition is therefore
  needed, but it fails only with heavy borrowing against the flat pension at a tax rate near 0.4.

## 2. Income inequality for $J$ types at consistent shares

**The transfer.** B.1's mean-preserving transfer raises $\eta_H$ and lowers $\eta_L$ with
$\partial\eta_L/\partial\eta_H = -\gamma_H(\eta_H/X_H)^{\xi}/[\gamma_L(\eta_L/X_L)^{\xi}]$, which keeps $\Gamma_h$ (and so average
hours and savings) fixed. Since $dy_m = (1+\xi)\frac{\eta_m^{\xi}}{X_m^{\xi}\Gamma_h}d\eta_m$, it leaves every other $y_j$
unchanged and satisfies $\gamma_H\,dy_H + \gamma_L\,dy_L = 0$: a mean-preserving transfer of relative income from a
poorer to a richer type, with $y_H > y_L$ the only requirement (neither needs to straddle the mean). It reaches
$G_t$ only through the formal retirees' shares: (7) is scale-free, $\phi_t$ and $a_t$ do not involve the $y_i$, and
$\mathcal{E}_{2,t}^0$ depends on them only through $\Gamma_h$, which is held fixed.

**Convexity.** By (3) and (10), at consistent shares the pension's share is a ratio of affine functions of $y$,

$$\sigma(y) = \frac{a_t\,[1+\theta(y-1)]}{1 + a_t + (1+a_t\psi)(y-1)} = \frac{a_t\theta\,y + a_t(1-\theta)}{(1+a_t\psi)\,y + a_t(1-\psi)}. \tag{23}$$

Its derivative has the constant numerator $a_t\theta\cdot a_t(1-\psi) - a_t(1-\theta)(1+a_t\psi) = a_t[\theta(1+a_t) - 1 - a_t\psi]$,
and with $\psi = (1+\beta\theta)/(1+\beta)$, $\theta(1+a_t) - 1 - a_t\psi = (\theta-1) + a_t\theta - \frac{a_t(1+\beta\theta)}{1+\beta} = -(1-\theta)\big(1+\frac{a_t}{1+\beta}\big)$, so

$$\sigma'(y) = -\frac{a_t(1-\theta)\left(1+\frac{a_t}{1+\beta}\right)}{D(y)^2} \leq 0, \qquad
\sigma''(y) = \frac{2\,(1+a_t\psi)\,a_t(1-\theta)\left(1+\frac{a_t}{1+\beta}\right)}{D(y)^3} > 0 \ \text{ for } \theta < 1. \tag{24}$$

The pension's share of consumption falls with income and is strictly convex in it; at $\theta = 1$ it is the constant
$a_t/(1+a_t)$. ($\sigma'(y_m)\,dy_m/d\eta_m$ is exactly B.1's printed $\partial\mathcal{E}_{2,t}^m/\partial\eta_m$ times $\tau_t$, so
the existing display is right.)

**The $J$-type result.** Using $\gamma_L\,dy_L = -\gamma_H\,dy_H$,

$$\frac{\partial G_t}{\partial\eta_H} = \frac{\omega}{\tau_t}\,\gamma_H\frac{dy_H}{d\eta_H}\Big[\mu_H\,\sigma'(y_H) - \mu_L\,\sigma'(y_L)\Big]
= \frac{\omega}{\tau_t}\,\gamma_H\frac{dy_H}{d\eta_H}\,a_t(1-\theta)\left(1+\frac{a_t}{1+\beta}\right)\left[\frac{\mu_L}{D_L^2} - \frac{\mu_H}{D_H^2}\right]. \tag{25}$$

With equal propensities the bracket is positive because $D_H > D_L$ (10), so every transfer from a poorer to a richer
type raises the tax; this is B.1's "straightforward" step made explicit, and it needs no condition beyond
$\theta < 1$. For $J$ types, any mean-preserving spread that is a sequence of such transfers, and more generally any
change in the distribution of relative incomes that raises $\sum_i\gamma_i\varphi(y_i)$ for every convex $\varphi$,
raises $\sum_i\gamma_i\sigma(y_i)$ by (24) and so the tax. With unequal propensities the condition is

$$\text{(CI)}\qquad \mu_H/\mu_L < \big(c_{2,t}^H/c_{2,t}^L\big)^2 \ \text{ for the types involved, i.e. } \mu_i/(c_{2,t}^i)^2 \text{ decreasing in income,} \tag{26}$$

which is what B.1 already states for two types.

**Remark R5 (*the inherited distribution*).** Holding $x_i$ fixed, $\partial\sigma_t^i/\partial y_i = a_t\theta\,x_i/D_i^2$ and the
transfer changes the retirees' aggregate support by

$$\frac{\omega}{\tau_t}\,a_t\theta\,\gamma_H\,dy_H\left[\frac{x_H}{D_H^2} - \frac{x_L}{D_L^2}\right], \tag{27}$$

zero at $\theta = 0$ and negative whenever $x_i/D_i^2$ falls with income, as at both calibrations (1.48, 0.99, 0.73,
0.39 for Argentina). The result in the proposition is carried entirely by the shares' response (9): poorer types
save less relative to their income, so a spread lowers their retirement consumption relative to richer types' and
raises the pension's share of it.

## 3. The condition for $\nu_t$

$\nu_t$ enters $G_t$ in two places. First, the weight on the young in (8). Second, the universal pension:
$b_t^0 = \frac{(1-\alpha)\nu_t\epsilon\tau_t}{1+\gamma_0\epsilon}\Theta_{h,t}^{1-\alpha}(s_{t-1}/\nu_t)^{\alpha(1+\xi)/(1+\alpha\xi)}$ and the
endowment $e_t \propto (s_{t-1}/\nu_t)^{\alpha(1+\xi)/(1+\alpha\xi)}$ carry the same power of capital per worker, so
$\sigma_t^0 = b_t^0/(e_t + b_t^0)$ depends on $\nu_t$ only through the factor $\nu_t$ in $b_t^0$ (more contributors per
informal retiree), and

$$\frac{\partial\sigma_t^0}{\partial\nu_t} = \frac{\sigma_t^0(1-\sigma_t^0)}{\nu_t}, \qquad \frac{\partial\mathcal{E}_{2,t}^0}{\partial\nu_t} = \mathcal{E}_{2,t}^0\,\frac{1-\sigma_t^0}{\nu_t}. \tag{28}$$

Nothing else moves: $a_t$ and the $x_i$ do not involve $\nu_t$, so $\sigma_t^i$ does not (formal pensions and capital
income both scale with $\nu_t$); $\phi_t$, $\Theta_{h,t}$ and (7) do not. Hence

$$\frac{\partial G_t}{\partial\nu_t} = \frac{\omega}{\nu_t}\,\gamma_0\mu_0\,\mathcal{E}_{2,t}^0(1-\sigma_t^0) + \Big[\gamma_0\mu_0\,\mathcal{E}_{1,t}^0 + \sum_{i>0}\gamma_i\mu_i\,\mathcal{E}_{1,t}^i\Big], \tag{29}$$

and substituting the first-order condition (8) for the bracket,

$$\frac{\partial G_t}{\partial\nu_t} = -\frac{\omega}{\nu_t}\Big[\gamma_0\mu_0\,\mathcal{E}_{2,t}^0\,\sigma_t^0 + \sum_{i>0}\gamma_i\mu_i\,\mathcal{E}_{2,t}^i\Big], \tag{30}$$

which is B.1's expression with the propensities in. Taxes fall with $\nu_t$ if and only if the bracket is positive
at the equilibrium. Its first term is positive ($\phi_t > 0$ by Lemma 1), so the sufficient condition the proposition
should carry is

$$\text{(C$\nu$)}\qquad \sum_{i>0}\gamma_i\mu_i\,\mathcal{E}_{2,t}^i > 0 \quad\Longleftrightarrow\quad
\frac{\sum_{i>0}\gamma_i\mu_i\,\sigma_t^i}{\sum_{i>0}\gamma_i\mu_i} > 1 - \phi_t = \frac{(1-\alpha)\xi}{1+\alpha\xi}\frac{\tau_t}{1-\tau_t}, \tag{31}$$

by (6): the (propensity-weighted) average share of the pension in formal retirees' consumption exceeds the
elasticity of the tax base with respect to the tax rate. What it requires: without a universal pension
($\gamma_0\epsilon = 0$) it follows from (8) itself, since the young's terms are negative; with one it can fail only if the
tax is sustained by informal retirees against formal ones, that is, if $\omega\gamma_0\mu_0\mathcal{E}_{2,t}^0(1-\sigma_t^0)$
exceeds the young's resistance $\nu_t|\gamma_0\mu_0\mathcal{E}_{1,t}^0 + \sum_i\gamma_i\mu_i\mathcal{E}_{1,t}^i|$, the equivalent
form of (30)'s bracket being negative. At the Argentine hand-to-mouth calibration the average share is 0.163 against
$1-\phi_t = 0.022$, and every type's $\sigma_t^i$ exceeds $1-\phi_t$. For $\omega$, $\partial G_t/\partial\omega$ is the retirees'
total, which equals $-\nu_t[\dots]/\omega > 0$ at an interior equilibrium; at the corner $\tau_t = 0$ neither $\omega$ nor
$\nu_t$ has an effect. Both hold for any propensities.

## 4. The condition for $\epsilon$ at the inherited distribution

B.1's derivation holds $x_i$ and $\Theta_{h,t}$ fixed: it signs the effect of the universal pension in force at $t$ on
the tax of that period when the current retirees did not anticipate it and the young's anticipated $\epsilon_{t+1}$
is unchanged. That is the Argentine reform period (once C2's #4 fix leaves the shares at their pre-reform values),
so the paper's use of (B.5) and its statement should carry this qualifier. With propensities, since
$\partial\ln b_t^0/\partial\epsilon = 1/[\epsilon(1+\gamma_0\epsilon)]$, $\partial\ln b_t^i/\partial\epsilon = -\gamma_0/(1+\gamma_0\epsilon)$,
$\partial\sigma_t^j/\partial\ln b_t^j = \sigma_t^j(1-\sigma_t^j)$ when the rest of consumption does not move, and
$\partial\mathcal{E}_{2,t}^0/\partial\sigma_t^0 = \phi_t/\tau_t$, $\partial\mathcal{E}_{2,t}^i/\partial\sigma_t^i = 1/\tau_t$ by (6),

$$\frac{\partial G_t}{\partial\epsilon}\Big|_{x_i,\,\Theta_{h,t}} = \frac{\omega\,\gamma_0}{\tau_t(1+\gamma_0\epsilon)}\left[\frac{\phi_t}{\epsilon}\,\mu_0\,\sigma_t^0(1-\sigma_t^0) - \sum_{i>0}\gamma_i\mu_i\,\sigma_t^i(1-\sigma_t^i)\right], \tag{32}$$

(B.5) with $\mu_j = 1$. Comment #10: with $\sigma_t^0 = \sigma_t^i = \sigma$ for all $i$ and $\mu_j = 1$ the bracket is positive
iff $\phi_t/\epsilon > 1$; at equal shares $c_{2,t}^0/\overline{c}_{2,t} = b_t^0/(h_{t-1}\overline{b}_t) = \epsilon$, so "poorer" is
$\epsilon < 1$ and the condition is $\epsilon < \phi_t$. The sentence after (B.5) should read: the condition holds when
informal retirees are poorer than formal ones by more than the marginal-revenue factor, $c_{2,t}^0/\overline{c}_{2,t} < \phi_t$
at equal pension shares, and the pension is a comparable share of their consumption. $\phi_t = 0.978$ at the Argentine
hand-to-mouth calibration; the abstract's and conclusion's wording ("poorer ... and a comparable share") can stand with
"by more than the marginal revenue of the tax" if the writer wants the exact statement there too.

**Remark R6 (*the fixed point*).** Two terms are added if the shares and hours are consistent with the new $\epsilon$.
(a) Shares: by (10), $\partial D_i/\partial a_t = 1-\psi+\psi y_i$ and $D_i - a_t(1-\psi+\psi y_i) = y_i$, so
$\partial\sigma_t^i/\partial a_t = p_iy_i/D_i^2$ and with $\partial a_t/\partial\epsilon = -a_t\gamma_0/(1+\gamma_0\epsilon)$

$$\frac{\partial\sigma_t^i}{\partial\epsilon}\Big|_{x_i = x_i(\epsilon)} = -\frac{\gamma_0}{1+\gamma_0\epsilon}\,\sigma_t^i\,\frac{y_i}{D_i}
\quad\text{in place of}\quad -\frac{\gamma_0}{1+\gamma_0\epsilon}\,\sigma_t^i\,\frac{x_i}{D_i} = -\frac{\gamma_0}{1+\gamma_0\epsilon}\,\sigma_t^i(1-\sigma_t^i), \tag{33}$$

so the right-hand side of (B.5) becomes $\sum_i\gamma_i\mu_i\sigma_t^iy_i/D_i$: poorer types, with $y_i > x_i$ by (9),
lose more support. (b) Hours: $\partial\mathcal{E}_{2,t}^0/\partial\epsilon_{t+1} = \mathcal{E}_{2,t}^0(1-\sigma_t^0)(1-\alpha)\,\partial\ln\Theta_{h,t}/\partial\epsilon_{t+1} < 0$
(hours fall with the anticipated $\epsilon$, proposition 1). At the Argentine hand-to-mouth calibration (a) moves the
right-hand side from 0.1359 to 0.1367 against a left-hand side of 0.525, and (b) is 0.1% of (32). Neither changes the
sign, but the fixed-point statement is not clean, which is a second reason to state $\epsilon$ at the inherited
distribution.

## 5. B.1's displays: the young term, the stray $\tau_t$

**The young term.** By the Euler equation, $\upsilon_{1,t}^i = (1+\beta)\ln\tilde{c}_{1,t}^i + \beta\ln R_{t+1} + \beta\ln\beta$.
Appendix A: $\tilde{c}_{1,t}^i = \frac{s_t}{1+\beta}(\dots)$ with the bracket free of $\tau_t$, $s_t = \Theta_{s,t}(s_{t-1}/\nu_t)^{\alpha(1+\xi)/(1+\alpha\xi)}$
and $\partial\ln\Theta_{s,t}/\partial\tau_t = \frac{1+\xi}{\xi}\partial\ln\Theta_{h,t}/\partial\tau_t = -\frac{1+\xi}{1+\alpha\xi}\frac{1}{1-\tau_t}$
($\Gamma_{s,t}$ does not depend on $\tau_t$); and $R_{t+1} = \alpha\Theta_{h,t+1}^{1-\alpha}(s_t/\nu_{t+1})^{-(1-\alpha)/(1+\alpha\xi)}$,
where $\Theta_{h,t+1}$ does not depend on $\tau_t$ (no strategic effects under log-HtM), so

$$\frac{\partial\ln R_{t+1}}{\partial\tau_t} = -\frac{1-\alpha}{1+\alpha\xi}\frac{\partial\ln s_t}{\partial\tau_t} = \frac{(1-\alpha)(1+\xi)}{(1+\alpha\xi)^2}\frac{1}{1-\tau_t} > 0. \tag{34}$$

Adding up, $\mathcal{E}_{1,t}^i = -\frac{1+\xi}{1+\alpha\xi}\frac{1}{1-\tau_t}\big[1+\beta - \beta\frac{1-\alpha}{1+\alpha\xi}\big]$, and
$1 - \frac{1-\alpha}{1+\alpha\xi} = \frac{\alpha(1+\xi)}{1+\alpha\xi}$ gives (7). The code (`base.py`, `dv1i_dτ_LOG`) and the
technical note (`model_PEE.tex`, eq. PEELOG) are right; the printed (B.4) drops the rise in $R_{t+1}$ that a lower
$s_t$ brings, (34), and so overstates the young's opposition by the factor $(1+\beta)/(1+\beta\frac{\alpha(1+\xi)}{1+\alpha\xi})$:
1.31 at the Argentine hand-to-mouth values ($\alpha = 0.35$, $\xi = 0.3$, $\beta = 0.67$), 1.38 at the U.S. values
($\alpha = 0.3$, $\beta = 0.76$). No numerical result changes, since every solve uses the code's form; (B.4) is the only
place in the paper with the slip (B.2's and appendix C's decompositions keep $\beta\,d\ln R_{t+1}$ separate). The
informal young's term, (B.3), is confirmed: $\tilde{c}_{1,t}^0$ does not depend on $\tau_t$ and both parts of
$\tilde{c}_{2,t+1}^0$ scale with $s_t^{\alpha(1+\xi)/(1+\alpha\xi)}$.

**The stray $\tau_t$.** Since $\mathcal{E}_{2,t}^m = (\phi_t - 1 + \sigma_t^m)/\tau_t$, the fixed-share derivative is
$\partial\mathcal{E}_{2,t}^m/\partial\theta = \frac{1}{\tau_t}\,a_t(y_m-1)x_m/D_m^2 = \frac{1-\alpha}{\alpha}\frac{1}{1+\gamma_0\epsilon}\frac{(y_m-1)\,x_m}{D_m^2}$;
the printed line has $\frac{1-\alpha}{\alpha}\frac{\tau_t}{1+\gamma_0\epsilon}$, a common factor $\tau_t$ too many. In the
rewritten proof the display is replaced by (12), so nothing needs correcting in place. The printed
$\partial\mathcal{E}_{2,t}^m/\partial\eta_m$ is right (§2).

**For T3 (the $J = 1$ closed form).** With $J = 1$ and $\gamma_0 = 0$: $y_1 = x_1 = p_1 = 1$, $D_1 = 1+a_t$,
$\sigma_t^1/\tau_t = \frac{1-\alpha}{\alpha+(1-\alpha)\tau_t}$, and (8) with (6)–(7), multiplied by $1-\tau_t$, is
$\omega\big[\frac{(1-\alpha)(1-\tau_t)}{\alpha+(1-\alpha)\tau_t} - \frac{(1-\alpha)\xi}{1+\alpha\xi}\big] = \nu_t\frac{1+\xi}{1+\alpha\xi}\big(1+\beta\frac{\alpha(1+\xi)}{1+\alpha\xi}\big)$,
so with $K \equiv \frac{\nu_t}{\omega}\frac{1+\xi}{1+\alpha\xi}\big(1+\beta\frac{\alpha(1+\xi)}{1+\alpha\xi}\big) + \frac{(1-\alpha)\xi}{1+\alpha\xi}$,

$$\tau_t = \frac{1-\alpha-\alpha K}{(1-\alpha)(1+K)}, \tag{35}$$

positive iff $K < (1-\alpha)/\alpha$. It must be built from (7), not from the printed $(1+\beta)$, before it is compared with
Gonzalez-Eiras and Niepelt (2008). Not checked against their formula here.

## 6. The fallback (task 6)

Not needed: §2 holds at consistent shares with no condition beyond $\theta < 1$ for equal propensities. The
proposition's wording for the case that holds is in part (a).

## 7. Numerical confirmation (of the algebra, not an argument)

Argentine hand-to-mouth log model (`python/informalAnalytical/test.py`'s `pars`/`kwargs`, `calibrate(preferences='LOG')`,
5 s: $\beta = 0.671$, $\omega = 1.49$, $\theta = 0.839$, $\epsilon = 0.210$, $\gamma_0 = 0.471$, $\tau_{2010} = 0.109$,
$y = (0.46, 0.71, 0.97, 1.85)$, equal masses and propensities). The consistent shares (9) equal the solved path's
$s_{t-1,i}/s_{t-1}$ to 3e-16. Central finite differences of the code's marginal supports in $\theta$ (shares rebuilt),
$\nu_t$ (through the database), $\epsilon$ (shares and $\Theta_{h,t}$ frozen, $\kappa$ rebuilt) and of
$(1+\beta)\ln\tilde{c}_{1,t}^i + \beta\ln R_{t+1}$ in $\tau_t$ match (12), (29), (32) and (7) to 1e-10 or better; (22) and
(21) to 1e-6 and 2e-5. Conditions at this point: $y^* = 0.010$ against $y_{\min} = 0.46$, $x_{\min} = 0.45 > 0$;
$y_i/D_i^2 = (1.51, 0.99, 0.73, 0.39)$, decreasing; $\partial G_t/\partial\theta = -0.554$ (the hours channel $+0.009$);
average $\sigma_t^i = 0.163$ against $1-\phi_t = 0.022$; (B.5): $0.525 > 0.136$ ($\sigma_t^0 = 0.130$, $\phi_t/\epsilon = 4.66$).
Whole-path solves (`LOG.solveVectorized`): $\tau_{2010} = 0.1127$, $0.1092$, $0.1057$ at $\theta - 0.05$, $\theta$, $\theta + 0.05$;
the transfer of §2 between the two lowest types with $d\eta_H = 0.01$ ($\Gamma_h$ constant to 2e-5) raises
$\tau_{2010}$ by 0.12 p.p. U.S. groups (`python/US/test.py`, CPS incomes $y = (0.51, 1.00, 2.19)$, turnout
$\mu = (0.47, 0.63, 0.77)$, $\theta = 0.738$, $\beta = 0.76$, $\tau_t = 0.144$ and $0.103$, no solve): $\mu_iy_i/D_i^2$ and
$\mu_i/D_i^2$ are decreasing at both taxes and at $\theta \in \{0, 0.738, 1\}$; the adjacent bounds of (15) are 1.87 and
2.12 at $\tau_t = 0.144$ (1.89 and 2.13 at 0.103) against turnout ratios 1.33 and 1.22; the bounds of (26) are 3.7 and
4.6; C.1's corner bounds $c_{2,t}^H/c_{2,t}^L$ are 1.92 and 2.15. Scripts in the session scratchpad only.

## (a) Proposed statement of Proposition 2

Minimal rewording of the current text; changes in brackets are the clauses to add or replace.

> In politico-economic equilibrium with hand-to-mouth informal households, all consumption functions are
> log-separable in the endogenous state variables, making policy only a function of parameters, including system
> characteristics and demographics. Politico-economic equilibrium taxes are increasing in $\omega$ and decreasing in
> $\nu_t$ [whenever the aggregate marginal support of formal retirees for the tax is positive at the equilibrium, as
> it is without a universal pension]. With equal propensities to vote[, and with retirees' savings consistent with
> the tax and the design they anticipated,] they are increasing in income inequality and[, if no formal type borrows
> against its pension,] decreasing in $\theta$. The effect of [an unanticipated change in] $\epsilon$ is ambiguous and
> depends on the pension's share of consumption of informal and formal retirees.

Notes for the writer. (i) The $\nu_t$ clause is the sufficient condition (31); the exact one, (30)'s bracket, is for
B.1. The alternative wording "unless the tax is sustained by informal retirees against formal ones" is B.1's current
phrase and also fine. (ii) "Income inequality" means a mean-preserving spread of relative labor incomes $y_i$, any
transfer from a poorer to a richer type at constant $\Gamma_h$ (§2); B.1 should say so once. (iii) The $\theta$ result is
for the design that pays the current retirees, which they anticipated when they saved; a footnote or a B.1 remark
can add that a permanent change also moves the hours of the young through the design they anticipate, a channel that
works through the universal pension alone, is absent in the U.S., UK and French calibrations and is 2% of the direct
effect at the Argentine one (R3). (iv) "No formal type borrows against its pension" is (19); the weaker exact
condition (18) stays in B.1. (v) The general conditions with unequal propensities, (15) and (26), replace B.1's
current sentence "for income inequality the condition is $\mu_H/\mu_L < (c_{2,t}^H/c_{2,t}^L)^2$", which is right but
covers inequality only.

## (b) Proposed outline of B.1's rewritten proof

1. *States.* Keep the current first two paragraphs (no endogenous state; the shares are a function of parameters and
   the current tax). Then define (1)–(3), (5), write the consumption function as (4), and the first-order condition
   as (8) with propensities, noting that (B.1)–(B.4) are (6)–(7) and that (B.4) now carries $1+\beta\alpha(1+\xi)/(1+\alpha\xi)$
   (one sentence: the rise in $R_{t+1}$ as savings fall partly compensates the young). Introduce the consistent shares
   (9) and the affine $D_i$ (10) with the two monotonicity facts.
2. *The sign rule.* One paragraph: at consistent shares every term of the condition falls in $\tau_t$ below the
   revenue-maximizing rate $\bar{\tau}$ and the condition is negative above it (Lemma 1, cross-referenced to the
   uniqueness result T2 adds to this appendix), so each comparative static has the sign of the partial derivative of
   the condition. This replaces the clause "At an interior equilibrium $\mathcal{F}_t$ is decreasing in $\tau_t$" before
   (B.5).
3. *$\omega$ and $\nu_t$.* Keep the current text, with the propensities in the sums, (28)–(30), and state the condition
   (31) in both forms (shares against the base elasticity; sustained by informal retirees), with "always met without
   a universal pension".
4. *Income inequality.* The transfer as now, then (23)–(24): the pension's share is decreasing and convex in relative
   income because the flat part substitutes for savings; (25) for the pair, the sentence extending it to $J$ types
   by repeated transfers (or the convex order), and (26) for unequal propensities. One sentence on R5: with the
   shares held fixed the effect is zero at $\theta = 0$, so the result rests on the savings response.
5. *$\theta$.* (11)–(13), the Chebyshev identity (14) in the form appendix C uses, condition (15), and for equal
   propensities (16)–(19) with the words "every formal retiree consumes more than $2\beta/(1+\beta)$ times the flat
   pension, which holds whenever no type borrows against its pension". Two sentences for R1 (at the inherited
   distribution the weight is $x_i/(c_{2,t}^i)^2$ and the sign is open, comment #1's example) and R3 (the hours
   channel of a permanent change). Optionally R2, which ties the effect at the Bismarckian corner to $\tilde{V}$.
6. *$\epsilon$.* Keep the derivation and (B.5), with the propensities, stating up front that it holds the inherited
   shares and $\Theta_{h,t}$ fixed (the reform period), and fix the sentence after (B.5) as in §4 (comment #10). One
   sentence for R6, that the fixed point adds (33) and the hours term without changing the sign at the calibration.

## Cross-package notes

- **C2 (A12).** The two sides of (B.5) as printed are the right objects for the reform period, with the shares at
  their inherited values (after #4's fix). Report $\phi_t/\epsilon$ alongside, since it carries the $\phi_t$ of comment #10.
  (B.5) is derived for hand-to-mouth informal households; if A12 is evaluated on the informal-savings calibration, say
  so, because there the informal retiree also holds capital and the share enters differently. Hand-to-mouth reference
  values from this note: 0.525 against 0.136.
- **T2.** Lemma 1 is the uniqueness argument in its sign-only form, with $\bar{\tau} = (1+\alpha\xi)/(1+\xi)$ and the
  qualifier $x_i \geq 0$; the two notes should use the same words for it.
- **T3.** The $J = 1$ closed form must start from (7); (35) is what (6)–(8) give at $J = 1$, $\gamma_0 = 0$.
- **No numerical result changes.** The slip in (B.4) is in the appendix's display only; the code has (7).
