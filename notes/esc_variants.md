# The cost of redistribution with a linear term: derivation and variant selection

Phase A of `notes/plan_endogenousDesign.md` §C, brief `notes/brief_escVariants_theory_2026-10-08.md`.
Labels are those of `writing/Paper/Appendix/EndogenousDesign.tex` (appendix C) and symbols those of the
paper; the one abbreviation is $g \equiv \frac{1-\alpha}{\alpha}$, which the tex block writes out. Dates:
the design $\theta_{t+1}$ is chosen at $t$; "the corner" is the Bismarckian corner $\theta_{t+1} = 1$. Every
number quoted is at $\rho = 1$, common $X$, from the runs of §3.5 and §4.4 (scripts `cornerCheck.py`,
`crossSection.py` in the session's scratchpad; nothing in the repository was changed).

## Overturned

1. **The reason given for decision C.1.2, not the decision.** The plan says a $\tau$-free linear leak
   "makes a larger system harder to put at the corner" because the young's redistributive stake is
   proportional to $\tau$. The stake is proportional to $\tau_{t+1}$, but so is the weight that multiplies
   the cost's marginal benefit (the pension is a share of order $\tau_{t+1}$ of the young's lifetime
   resources, (A.20)). Under a $\tau$-free leak the two cancel and the corner condition is independent of
   the size of the system to first order; a larger system makes the corner only slightly harder, at second
   order. Under the common scaling the cancellation leaves $\lambda_1\tau_{t+1}\tilde V \geq$ const, so the
   threshold is proportional to $1/\tau_{t+1}$: the size channel works for the corner and it is first
   order. Confirmed: raising $\omega$ by 30% moves $\tau_{2020}(1)$ from 0.134 to 0.212 and the threshold
   from 2.82 to 1.84, while $\bar\lambda_1\tau_{2020}(1)\tilde V$ moves from 0.1645 to 0.1701 (§3.5). The
   decision stands with this reason.
2. **The fallback of C.1.3 (France pins $\kappa$, the UK predicts) is infeasible under the form of C.1.1,
   and LQ pinned on the UK does not predict France's corner.** France's corner needs
   $\lambda_1 \geq \underline\lambda_1^{FR} = 2.55$ (§3.5, (A.17)); the largest $\lambda_1 = \lambda\kappa$
   compatible with the U.S. interior design is the L limit $\kappa \to \infty$, $\lambda_1^{US} = 2.26$
   (recalibrated; 2.44 at the held Q values of $(\beta,\omega)$), 13% short (4% at the held values). So no $\kappa \geq 0$ puts France at
   the corner while the U.S. re-elects 0.738, under L or LQ; France's prediction is 0.758 under L and
   0.73 to 0.76 under LQ pinned on the UK ($\kappa \approx 0.11$), against 0.749 under Q. The reason is the
   dispersion weight: France's $\tilde V$ is half the U.S. value (0.218 against 0.436) while the
   redistributive part of the stake is only a quarter of the obstacle to the corner, the rest being a
   common general-equilibrium loss that does not scale with the dispersion (§3.4). Weighting the linear
   term by the mean absolute deviation $M = \sum_i\gamma_i|y_i-1|$ (0.422 against 0.575, a ratio of 0.73
   rather than 0.50), which is the amount Okun's bucket carries, puts France's threshold at 0.77 of the
   U.S. L value and makes the France-pinned fallback feasible at $\kappa \approx 1$, with the UK then
   predicted at about 0.34. §1.4 states both weights and recommends; gate 1 is where RKB calls it.

## C.1 stands

- **C.1.1, the form.** (A.1) with Q, L and LQ nested; $A = f\theta$, $B = f(1-\theta)$; the tax
  condition's factor is $1+\ln f$ for every variant; $\theta^{\ast}$ is the data's own; separability holds;
  the marginal cost of the first unit of redistribution is $\lambda_1\tau_t\tilde V$ (§1, §2).
- **C.1.2, the $\tau$-scaling of the linear term.** Kept, for the reason in Overturned 1; the literal
  Okun leak is stated as the alternative with its cost (§1.3, §3.3).
- **C.1.3, the pinning.** $(\lambda,\kappa)$ on the U.S. and the UK, France the prediction: the map
  $\kappa \mapsto \theta^{UK}$ along the U.S.-calibrated curve is monotone decreasing, $\kappa \geq 0$ is the
  right side, the UK's own $\lambda$ at that $\kappa$ reproduces $\lambda_{US}$ by construction (§4). What
  changes is the expectation of the result (Overturned 2) and the fallback, which has no solution under
  the $\tilde V$ weight.

Two findings the later phases need, neither a decision of C.1:

- **L is knife-edge.** The costless objective $\mathcal{B}_t$ is concave but nearly flat
  ($\mathcal{B}_t'' \approx -0.07$ on all of $[0,1]$); under L the cost's marginal benefit is nearly flat in
  $\theta_{t+1}$ too, so the interior optimum is fragile. At the U.S. L parameter the UK chooses
  $\theta = 0$ (observed 0.560; 0.625 under Q), and on the U.S. every counterfactual is a corner or near
  one (acute ageing 1.000, France's income distribution 1.000, France's voting patterns 0.044; §5). L
  belongs in the paper as the limit that shows why the quadratic curvature is needed, in the one
  paragraph of W1, not on equal footing.
- **A precision item for phase C.** The recursion interpolates $\mathcal{T}_{t+1}$ linearly on the
  41-node state grid; the error is $3\times10^{-5}$ in $\tau$, but the objective moves by only
  $\mathcal{B}_t''h^2 \approx 5\times10^{-6}$ per candidate step, so the parabolic refinement of the argmax
  amplifies it: the choice made in 2020 is 0.7973 with the interpolated policy and 0.7936 with
  $\mathcal{T}_{2050}$ evaluated at the candidates ($5\times10^{-4}$ for the 1990 choice that the
  calibration targets). Evaluating the tax policy at the 121 candidates costs one `τOfθ` call per period.

## 1. The general form and its reading

**The form.**
$$
f(\theta_t,\tau_t) = \exp\Big\{-\tau_t\tilde V(1-\theta_t)\Big[\lambda_1 + \tfrac12\lambda_2(1-\theta_t)\Big]\Big\},
\qquad \tilde V \equiv \sum_i\gamma_i\frac{(y_i-1)^2}{y_i} = \sum_i\frac{\gamma_i}{y_i} - 1,
\tag{A.1}
$$
the second form of $\tilde V$ by $\sum_i\gamma_i y_i = 1$. Q is $\lambda_1 = 0$, $\lambda_2 = \lambda$; L is
$\lambda_2 = 0$, $\lambda_1 = \lambda$; LQ is $\lambda_1 = \lambda\kappa$, $\lambda_2 = \lambda$. The share
of revenue lost is, to first order in $\ln f$,
$$
1 - f = -\ln f - \tfrac12(\ln f)^2 - \dots \approx \tau_t\tilde V(1-\theta_t)\Big[\lambda_1 + \tfrac12\lambda_2(1-\theta_t)\Big],
\tag{A.2}
$$
dropping $\tfrac12(\ln f)^2$ and higher: $2\times10^{-4}$ at the U.S. observed design under Q
($\ln f = -0.019$) and $0.037$ at $\theta_t = 0$ ($\ln f = -0.272$, exact share $0.238$). The first-order
shares of the variants are $\tfrac12\lambda\tau_t\tilde V(1-\theta_t)^2$ (Q), $\lambda\tau_t\tilde V(1-\theta_t)$
(L) and $\lambda\tau_t\tilde V(1-\theta_t)[\kappa + \tfrac12(1-\theta_t)]$ (LQ).

**Properties, verified on (A.1).** (i) $f = 1$ at $\theta_t = 1$, since both terms carry $1-\theta_t$,
and $f = 1$ for every design when $\tilde V = 0$. (ii) The share lost rises with $\tau_t$:
$\partial(1-f)/\partial\tau_t = -f\ln f/\tau_t \geq 0$. (iii) The marginal cost of redistribution is
$$
\frac{\partial\ln f}{\partial\theta_t} = \tau_t\tilde V\big[\lambda_1 + \lambda_2(1-\theta_t)\big],
\qquad \frac{\partial\ln f}{\partial\theta_t}\Big|_{\theta_t = 1} = \lambda_1\tau_t\tilde V \equiv \ell_t,
\tag{A.3}
$$
zero at the corner under Q and positive under L and LQ. (iv) $\ln f$ is linear in $\tau_t$, so
$$
\frac{\partial\ln f}{\partial\tau_t} = \frac{\ln f}{\tau_t}, \qquad 1 + \tau_t\frac{\partial\ln f}{\partial\tau_t} = 1 + \ln f,
\tag{A.4}
$$
for every variant; this is the factor of `eq:esc:E2` and it needs no spec-specific code beyond
`dlnfWedge_dτ` returning $\ln f/\tau_t$.

### 1.1 The Okun reading

The flat component carries, per unit of mean past earnings, $|t_i|y_i = \Pi_t\tau_t(1-\theta_t)|y_i-1|$
to or from a retiree of type $i$ (`eq:esc:implicitTax`); counting each unit once, since what is taken
above the mean is what arrives below it, the amount carried is
$$
\tfrac12\sum_i\gamma_i y_i|t_i| = \tfrac12\Pi_t\tau_t(1-\theta_t)M, \qquad M \equiv \sum_i\gamma_i|y_i-1|.
\tag{A.5}
$$
Okun's bucket with a constant leak $\kappa_0$ per unit carried loses $\tfrac12\kappa_0\Pi_t\tau_t(1-\theta_t)M$,
which as a share of revenue $\Pi_t\tau_t$ is
$$
1 - f \approx \lambda_1^{M}(1-\theta_t)M, \qquad \lambda_1^{M} = \tfrac12\kappa_0:
\tag{A.6}
$$
independent of the size of the system and weighted by $M$, not $\tilde V$, as the brief expected. A leak
whose share per unit carried rises with the load is the Harberger term: a per-type loss $\tfrac12\varepsilon t_i^2$
on base $y_i$ sums to $\tfrac12\varepsilon\Pi_t^2\tau_t^2(1-\theta_t)^2\tilde V$, a share
$\tfrac12\varepsilon\Pi_t\tau_t(1-\theta_t)^2\tilde V$ of revenue, as C.2 has it. The two readings are one
per-type loss function $\phi(t_i) = \kappa_0|t_i| + \tfrac12\varepsilon t_i^2$ on the implicit tax, kinked at
zero and convex: the literal Okun--Harberger composite is
$$
1 - f \approx \lambda_1^{M}(1-\theta_t)M + \tfrac12\lambda_2\tau_t\tilde V(1-\theta_t)^2 .
\tag{A.7}
$$

### 1.2 The common scaling as a choice

(A.1) replaces the linear term of (A.7) by $\lambda_1\tau_t\tilde V(1-\theta_t)$: the leak per unit of
flat share is proportional to the same load, $\tau_t\tilde V$, as the quadratic one. It is a choice, not a
derivation; what it buys is (i) one dispersion statistic and one load, so that $f$ is a function of
$\tau_t\tilde V$ and $1-\theta_t$ alone and $\kappa = \lambda_1/\lambda_2$ is a pure shape parameter, (ii) the
factor $1 + \ln f$ in the tax condition for every variant, since $\ln f$ stays linear in $\tau_t$, and
(iii) the size channel at the corner: the threshold on $\lambda_1$ is proportional to $1/\tau_{t+1}$
(§3.3), which is the paper's reading of what separates France from the UK at nearly the same
dispersion.

**The alternative's cost, for the footnote.** Under the literal leak (A.7) the share lost by the linear
term does not depend on the size of the system, so the corner is as far for a large system as for a small
one to first order and slightly farther for the large one at second order (§3.3); at the same dispersion
France and the UK would then differ only through their voting profiles and demographics, and the
cross-country ordering would rest on those alone. The tax condition's factor becomes
$1 + \tau_t\partial\ln f/\partial\tau_t = 1 - \tfrac12\lambda_2\tau_t\tilde V(1-\theta_t)^2 = 1 + \ln f + \lambda_1^{M}(1-\theta_t)M$,
only the quadratic part dissipating at the margin, because a constant share lost leaves the marginal
unit of revenue worth as much as the average one. And a second dispersion statistic enters the paper.

### 1.3 Recommendation on the scaling

Keep the $\tau_t$ in the linear term (C.1.2). The economic argument is §3.3's: the cost's marginal benefit
at the corner is $\ell_{t+1}$ times the pension's weight in lifetime resources, of order $\tau_{t+1}$,
against a stake of the same order, so only a linear term that itself scales with $\tau_{t+1}$ makes the
size of the system matter for the corner, and it does so at first order.

### 1.4 The dispersion weight of the linear term

Two weights are consistent with everything above: $\tilde V$ (C.1.1, the common load) and $M$ (the Okun
amount carried, (A.5)):
$$
\ln f = -\tau_t(1-\theta_t)\Big[\lambda_1 D + \tfrac12\lambda_2\tilde V(1-\theta_t)\Big], \qquad D \in \{\tilde V, M\}.
\tag{A.8}
$$
Both keep (A.3)--(A.4), the identification and the separability; $M = \tilde V = 0$ when all incomes are
equal. They differ only across economies: for one economy $\lambda_1 M = \lambda_1'\tilde V$ gives the same
$f$, so the U.S. calibration is the same function under either weight. The UK's $M/\tilde V$ (1.31) equals
the U.S. value (1.32), so the UK is unaffected by the choice; France's is 1.93, so France's linear term at
a common parameter is 1.47 times larger under $M$ than under $\tilde V$. That is the whole difference
between France interior (0.758 under L, 0.73 under LQ) and France at the corner (§3.5, §4.4).

Recommendation: keep $\tilde V$ as the default (C.1.1 stands), run phase C as planned, and let RKB call
the weight at gate 1 with the numbers of §3.5 and §4.4 in hand. The case for $\tilde V$: one statistic,
the paper's "load" reading, and the LQ calibration pinned on the UK is unaffected. The case for $M$: it is
the dispersion Okun's bucket actually carries, it makes France's corner reachable from the U.S.
calibration ($\underline\lambda_1^{FR} = 0.77\,\lambda_1^{US}$ under L), and it makes the France-pinned
fallback of C.1.3 feasible ($\kappa \approx 1$, the UK predicted at 0.34). Neither weight reconciles the
UK and France at one $(\lambda,\kappa)$: the UK wants a small linear term ($\kappa \approx 0.1$) and France a
large one. The code change for $M$ is a method `Mabs` beside `Vtilde` and one factor in `fWedge` and
`dlnfWedge_dτ`.

## 2. The equilibrium with the cost

Everything in C.3 uses only three facts about $f$: it multiplies both components, it depends on the
$(\theta,\tau)$ of the date whose benefits it scales, and $\ln f$ is linear in $\tau$. All three hold for
(A.1) and (A.8), so C.3 carries over verbatim:

- *The substitution.* The design enters the economic equilibrium only through
  $\frac{1-\alpha}{\alpha}\tau_{t+1}\theta_{t+1}$ and $\frac{1-\alpha}{\alpha}\tau_{t+1}(1-\theta_{t+1})$ and
  through $\theta_t$, $1-\theta_t$ in the benefits of current retirees; the cost is the substitution
  $\theta \mapsto A = f\theta$, $1-\theta \mapsto B = f(1-\theta)$ there and nowhere else. `eq:esc:auxiliary`
  is unchanged with the general $f$ in $A$ and $B$.
- *The tax condition.* `eq:esc:E2` holds with $\partial\ln f/\partial\tau_t = \ln f/\tau_t$, so the factor
  is $1 + \ln f(\theta_t,\tau_t)$ by (A.4); the sentence "since $\ln f$ is linear in $\tau_t$" is the whole
  argument and survives. Nothing else in the condition sees $f$, so $\tau_t = \mathcal{T}_t(\theta_t)$ is
  still a function of the inherited design alone.
- *Identification.* $B/A = (1-\theta_t)/\theta_t$ for every $f$ that multiplies both components;
  $\theta^{\ast} = 0.738$ whatever $(\lambda_1,\lambda_2)$.
- *The design condition.* With $\partial f/\partial\theta_{t+1} = f\tau_{t+1}\tilde V[\lambda_1 + \lambda_2(1-\theta_{t+1})]$,
  $$
  \frac{\partial A}{\partial\theta_{t+1}} + \frac{\partial B}{\partial\theta_{t+1}} = \frac{\partial f}{\partial\theta_{t+1}}
  = f\,\tau_{t+1}\tilde V\big[\lambda_1 + \lambda_2(1-\theta_{t+1})\big] \geq 0,
  \tag{A.9}
  $$
  which replaces `eq:esc:ftheta`: positive at the corner under L and LQ, where it equals
  $\ell_{t+1} = \lambda_1\tau_{t+1}\tilde V$, and zero there under Q. Under L it is constant in the design up
  to the level $f$; under LQ it falls from $\tau_{t+1}\tilde V\lambda(\kappa+1)$ at $\theta_{t+1} = 0$ to
  $\lambda\kappa\tau_{t+1}\tilde V$ at the corner.
- *Separability.* The proof of `prop:esc:separability` uses that $\Theta_{h,t}$ factors into a term in
  $\tau_t$ and a term in $(\tau_{t+1},\theta_{t+1})$, that $\tau_{t+1} = \mathcal{T}_{t+1}(\theta_{t+1})$ and
  that the continuation is state-free; none of this depends on the form of $f$. The design chosen at $t$
  maximizes $\mathcal{B}_t(\theta_{t+1})$ alone under every variant.

One thing does not carry over, and it is what §3 is about: C.3's reading that the design condition
"crosses zero in the interior" because $\partial f/\partial\theta_{t+1}$ vanishes at the corner. Under L and
LQ it does not vanish, and whether the choice is the corner is the sign of $\partial\mathcal{B}_t/\partial\theta_{t+1}$
at $\theta_{t+1} = 1$.

## 3. The corner condition at $\theta_{t+1} = 1$ under log preferences

### 3.1 The objects at the corner

By `prop:esc:separability` the choice at $t$ maximizes $\mathcal{B}_t$, and by `eq:esc:leadFOC`
$$
\frac{\partial\mathcal{B}_t}{\partial\theta_{t+1}} = \sum_i\gamma_i\mu_i\Big[\omega(1-\alpha)\frac{d\ln\Theta_{h,t}}{d\theta_{t+1}}
+ \nu_t\Big((1+\beta)\frac{d\ln\tilde c_{1,t}^i}{d\theta_{t+1}} + \beta\frac{d\ln R_{t+1}}{d\theta_{t+1}}\Big)\Big],
\tag{A.10}
$$
with the weights of `eq:LOG:PolObj` (time-invariant $\gamma_i$, $\mu_i$; $p = 1$), each total derivative
carrying $\tau_{t+1} = \mathcal{T}_{t+1}(\theta_{t+1})$. Write $\tau_{t+1} \equiv \mathcal{T}_{t+1}(1)$ and
$\mathcal{T}'_{t+1} \equiv \mathcal{T}'_{t+1}(1)$ for the tax and its slope at the corner, and
$$
g \equiv \frac{1-\alpha}{\alpha}, \quad b \equiv \frac{\beta}{1+\beta}, \quad
\psi_{t+1} \equiv \frac{g\tau_{t+1}}{1+g\tau_{t+1}}, \quad
\Lambda_{t+1} \equiv \frac{b\psi_{t+1}}{1+\xi-b\psi_{t+1}}, \quad
\chi_{t+1} \equiv \ell_{t+1} + \frac{\mathcal{T}'_{t+1}}{\tau_{t+1}},
\tag{A.11}
$$
where $b\psi_{t+1}$ is the present value of the anticipated pension relative to the lifetime surplus of a
young household at the Bismarckian design and $\frac{\xi}{1+\alpha\xi}\Lambda_{t+1}$ the elasticity of
$\Theta_{h,t}$ to the earnings-related return $A\tau_{t+1}\Gamma_{s,t}$ there. At $\theta_{t+1} = 1$: $f = 1$,
$A = 1$, $B = 0$, $\partial f/\partial\tau_{t+1} = f\ln f/\tau_{t+1} = 0$, and
$$
\frac{dA}{d\theta_{t+1}} = 1 + \ell_{t+1}, \qquad \frac{dB}{d\theta_{t+1}} = -1, \qquad
\frac{d\ln(A\tau_{t+1})}{d\theta_{t+1}} = 1 + \chi_{t+1}:
\tag{A.12}
$$
the cost and the tax response enter the young's earnings-related return through one number, the
proportional change of $A\tau_{t+1}$ at the corner, and $\lambda_2$ does not enter at all.

*The ingredients* (`eq:esc:auxiliary` with $B_{t+1} = \beta$; $\mathcal{T}'_{t+1}$ held as a symbol):
$$
\Gamma_{s,t} = \frac{\Gamma_h\,b}{(1+\xi)\big[1 + g\tau_{t+1}\big(A + \tfrac{B}{1+\beta}\big)\big]}
\;\Rightarrow\;
\frac{d\ln\Gamma_{s,t}}{d\theta_{t+1}}\Big|_{1} = -\psi_{t+1}\Big[(1+\ell_{t+1}) - \frac{1}{1+\beta} + \frac{\mathcal{T}'_{t+1}}{\tau_{t+1}}\Big]
= -\psi_{t+1}\big(b + \chi_{t+1}\big),
\tag{A.13}
$$
$$
\ln\Theta_{h,t} = \text{const} + \frac{\xi}{1+\alpha\xi}\Big[\ln(1-\tau_t) - \ln\big(\Gamma_h - gA\tau_{t+1}\Gamma_{s,t}\big)\Big]
\;\Rightarrow\;
H_{t+1} \equiv \frac{d\ln\Theta_{h,t}}{d\theta_{t+1}}\Big|_{1} = \frac{\xi}{1+\alpha\xi}\Lambda_{t+1}\Big[1 - b\psi_{t+1} + (1-\psi_{t+1})\chi_{t+1}\Big],
\tag{A.14}
$$
using $gA\tau_{t+1}\Gamma_{s,t}/\Gamma_h = b\psi_{t+1}/(1+\xi)$ at the corner and
$d\ln(A\tau_{t+1}\Gamma_{s,t}) = (1+\chi_{t+1}) - \psi_{t+1}(b+\chi_{t+1})$. The young's consumption is
$\tilde c_{1,t}^i = \frac{(h_t/\Gamma_h)^{(1+\xi)/\xi}}{1+\beta}\big[\frac{y_i\Gamma_h}{1+\xi} + g\tau_{t+1}B\,\Gamma_{s,t}\big]$
(appendix B's $\tilde c_{1,t}^i$ with $s_t$ eliminated), so at the corner, where the bracket is $y_i\Gamma_h/(1+\xi)$,
$$
\frac{d\ln\tilde c_{1,t}^i}{d\theta_{t+1}}\Big|_{1} = \frac{1+\xi}{\xi}H_{t+1} - \frac{b\psi_{t+1}}{y_i}:
\tag{A.15}
$$
the only type-specific term of (A.10) is the loss of the flat benefit, $dB = -1$, which is a larger share of
a poorer type's surplus. The return is $\ln R_{t+1} = \text{const} - \frac{1-\alpha}{1+\alpha\xi}\ln(s_t/\nu_{t+1}) + (1-\alpha)\ln\Theta_{h,t+1}$,
with $\ln s_t = \frac{1+\xi}{\xi}\ln h_t + \ln\Gamma_{s,t}$ and $\Theta_{h,t+1}$ seeing $\theta_{t+1}$ only
through $(1-\tau_{t+1})^{\xi/(1+\alpha\xi)}$, since the continuation design is state-free:
$$
\frac{d\ln R_{t+1}}{d\theta_{t+1}}\Big|_{1} = -\frac{1-\alpha}{1+\alpha\xi}\Big[\frac{1+\xi}{\xi}H_{t+1} - \psi_{t+1}(b+\chi_{t+1})\Big]
- \frac{(1-\alpha)\xi}{1+\alpha\xi}\frac{\mathcal{T}'_{t+1}}{1-\tau_{t+1}}.
\tag{A.16}
$$
Retirees' consumption carries $\theta_{t+1}$ only through $(1-\alpha)\ln h_t$.

### 3.2 The derivative and the bound

Collecting (A.13)--(A.16) in (A.10), with $\bar\mu \equiv \sum_i\gamma_i\mu_i$ and
$S_\mu \equiv \sum_i\gamma_i\mu_i/y_i$,
$$
\frac{\partial\mathcal{B}_t}{\partial\theta_{t+1}}\Big|_{\theta_{t+1}=1}
= \underbrace{\bar\mu\,c_H\,H_{t+1}}_{\text{hours}}
+ \underbrace{\bar\mu\nu_t\beta\frac{1-\alpha}{1+\alpha\xi}\psi_{t+1}\big(b+\chi_{t+1}\big)}_{\text{return, through } s_t}
- \underbrace{\bar\mu\nu_t\beta\frac{(1-\alpha)\xi}{1+\alpha\xi}\frac{\mathcal{T}'_{t+1}}{1-\tau_{t+1}}}_{\text{return, through } h_{t+1}}
- \underbrace{\nu_t\beta\psi_{t+1}S_\mu}_{\text{the flat benefit}},
\tag{A.17}
$$
$$
c_H \equiv \omega(1-\alpha) + \nu_t\frac{1+\xi}{\xi}\,\frac{1+\alpha\xi+\alpha\beta(1+\xi)}{1+\alpha\xi}.
$$
The hours term is the retirees' unanimous gain and the young's common gain from a higher earnings-related
return; it is positive whenever $1 - b\psi_{t+1} + (1-\psi_{t+1})\chi_{t+1} > 0$. The savings term is
positive when $b + \chi_{t+1} > 0$ (a higher earnings-related return lowers savings, which raises the
return). The $h_{t+1}$ term has the sign of $-\mathcal{T}'_{t+1}$. The last term is the loss of the flat
benefit, weighted by $1/y_i$: with equal propensities $S_\mu = \bar\mu(1+\tilde V)$ by (A.1), so it splits
into a common part $\nu_t\beta\psi_{t+1}\bar\mu$ and a redistributive part $\nu_t\beta\psi_{t+1}\bar\mu\tilde V$,
and with the U.S. profile $S_\mu/\bar\mu = 1.294$ against $1+\tilde V = 1.436$.

At fixed $\mathcal{T}'_{t+1}$ the derivative is affine in $\ell_{t+1}$ with a positive coefficient,
$$
\frac{\partial\mathcal{B}_t}{\partial\theta_{t+1}}\Big|_{1} = \Phi_0(\mathcal{T}'_{t+1}) + \ell_{t+1}\Phi_1, \qquad
\Phi_1 = \bar\mu\Big[c_H\frac{\xi}{1+\alpha\xi}\Lambda_{t+1}(1-\psi_{t+1}) + \nu_t\beta\frac{1-\alpha}{1+\alpha\xi}\psi_{t+1}\Big] > 0,
\tag{A.18}
$$
and the Bismarckian corner is a local maximum of $\mathcal{B}_t$ if and only if
$$
\lambda_1 \geq \underline\lambda_1 \equiv \frac{-\Phi_0(\mathcal{T}'_{t+1})}{\tau_{t+1}\tilde V\,\Phi_1}
\quad\Longleftrightarrow\quad
\ell_{t+1} \geq \bar\ell \equiv \frac{-\Phi_0}{\Phi_1},
\tag{A.19}
$$
a bound on $\lambda_1$ alone: the same under L and LQ, whatever $\lambda_2$. Normalized by
$\bar\mu\nu_t\beta\psi_{t+1}$, with $\hat c_H \equiv c_H/(\nu_t\beta)$,
$$
\bar\ell = \frac{\dfrac{S_\mu}{\bar\mu} - \mathcal{F}}{\hat\Phi_1}, \quad
\hat\Phi_1 = \hat c_H\frac{\xi}{1+\alpha\xi}\frac{b(1-\psi_{t+1})}{1+\xi-b\psi_{t+1}} + \frac{1-\alpha}{1+\alpha\xi}, \quad
\mathcal{F} = \hat c_H\frac{\xi}{1+\alpha\xi}\frac{b}{1+\xi-b\psi_{t+1}}\Big(1 - b\psi_{t+1} + (1-\psi_{t+1})\frac{\mathcal{T}'_{t+1}}{\tau_{t+1}}\Big)
+ \frac{1-\alpha}{1+\alpha\xi}\Big(b + \frac{\mathcal{T}'_{t+1}}{\tau_{t+1}}\Big) - \frac{(1-\alpha)\xi}{1+\alpha\xi}\frac{\mathcal{T}'_{t+1}}{\psi_{t+1}(1-\tau_{t+1})},
\tag{A.19$'$}
$$
where $\mathcal{F}$ is the forward-looking gain per unit of the stake. The condition is necessary; it is
sufficient when $\mathcal{B}_t$ is single-peaked, which holds on the three calibrated economies (§3.5:
the choice is the corner at $1.1\,\underline\lambda_1$ and interior at $0.9\,\underline\lambda_1$ under L and
under LQ with $\lambda_2 = \lambda_Q$). What (A.19) drops: nothing; it is exact at fixed $\mathcal{T}'_{t+1}$.

**The tax response.** $\mathcal{T}'_{t+1}$ is not free of $\lambda_1$. At the corner the tax condition
$z_{t+1}(\tau,\theta) = 0$ of `eq:esc:E2` has, from $N_i = [Ay_i+B](1+\ln f)$ and
$D_i = s_{t,i}/s_t + g\tau[Ay_i+B]$ with $s_{t,i}/s_t = y_i + g\tau B(y_i-1)/(1+\beta)$,
$\partial N_i/\partial\theta = (1+2\ell)y_i - 1$ and $\partial D_i/\partial\theta = g\tau[b(y_i-1) + \ell y_i]$, so
$$
\frac{\partial z_{t+1}}{\partial\theta_{t+1}}\Big|_{1} = \frac{\omega g}{(1+g\tau_{t+1})^2}\Big[-\Big(1+\frac{g\tau_{t+1}}{1+\beta}\Big)\big(S_\mu - \bar\mu\big) + \ell_{t+1}(2+g\tau_{t+1})\bar\mu\Big],
\qquad
\mathcal{T}'_{t+1} = -\frac{\partial z_{t+1}/\partial\theta_{t+1}}{\partial z_{t+1}/\partial\tau_{t+1}} = \mathcal{T}'_{0}\Big(1 - \frac{\ell_{t+1}}{\ell^{0}}\Big),
\tag{A.20}
$$
$$
\ell^{0} \equiv \frac{\big(1+\frac{g\tau_{t+1}}{1+\beta}\big)\big(S_\mu/\bar\mu - 1\big)}{2+g\tau_{t+1}},
$$
with $\partial z/\partial\tau < 0$ at a stable interior tax and $\mathcal{T}'_0 < 0$ the costless slope
(the redistributive force of `prop:LOG:PEE`: a more Bismarckian design lowers retirees' support for the
tax). The cost enters with the factor $2$: once through the level $A$ and once through the marginal
factor $1+\ln f$, whose slope at the corner is $\ell_{t+1}$. The tax response therefore turns positive at
$\ell_{t+1} = \ell^{0}$ (0.150 for the U.S., below $\bar\ell = 0.1645$): at the threshold a more Bismarckian
design already raises the tax, because the dissipation it saves raises what the marginal contribution is
worth to retirees. (A.20) is linear in $\ell_{t+1}$ and confirmed numerically to the slope
($\mathcal{T}'_{2020}(1) = -0.090, +0.009, +0.190, +0.401$ at $\ell = 0, 0.165, 0.467, 0.816$). Substituting
(A.20) in (A.18) keeps the derivative affine in $\ell_{t+1}$, with coefficient
$\Phi_1 + (\mathcal{T}'_0/\ell^{0})\big[\bar\mu\nu_t\beta\frac{(1-\alpha)\xi}{(1+\alpha\xi)(1-\tau_{t+1})} - \Phi_1/\tau_{t+1}\big]$;
the numerical bound of §3.5 solves this fixed point.

### 3.3 The first-order cancellation of $\tau_{t+1}$, and the two scalings

As $\tau_{t+1} \to 0$ at fixed $\mathcal{T}'_{t+1}/\tau_{t+1}$ (the proportional tax response, an elasticity
that stays finite as the system shrinks through $\omega$), $\psi_{t+1} = g\tau_{t+1} + O(\tau^2)$ and
$\Lambda_{t+1} = \frac{b g\tau_{t+1}}{1+\xi} + O(\tau^2)$, so every term of (A.17) is of order $\tau_{t+1}$:
$$
\Phi_0 = \tau_{t+1}\phi_0 + O(\tau_{t+1}^2), \qquad \Phi_1 = \tau_{t+1}\phi_1 + O(\tau_{t+1}^2), \qquad
\bar\ell = -\frac{\phi_0}{\phi_1} + O(\tau_{t+1}).
\tag{A.21}
$$
This is the cancellation: the stake is proportional to $\tau_{t+1}$ and so is the weight of the pension in
the young's lifetime resources, which multiplies the cost's marginal benefit $\ell_{t+1}$. What remains is
a condition on $\ell_{t+1}$, the marginal share saved by the first unit of design, of order one. Hence:

- *Common scaling* (A.1): $\ell_{t+1} = \lambda_1\tau_{t+1}\tilde V$, so
  $\underline\lambda_1 = \bar\ell/(\tau_{t+1}\tilde V)$ with $\bar\ell$ independent of $\tau_{t+1}$ to first
  order: a larger system makes the corner easier, and the effect is first order, $\underline\lambda_1 \propto 1/\tau_{t+1}$.
- *$\tau$-free leak* (A.7): $\ell_{t+1} = \lambda_1^{M}M$, so $\underline\lambda_1^{M} = \bar\ell/M$,
  independent of the size of the system to first order. At second order both $\hat\Phi_1$ and
  $\mathcal{F}$ in (A.19$'$) fall as $\psi_{t+1}$ rises (the factors $\frac{1-\psi}{1+\xi-b\psi}$ and
  $\frac{1-b\psi}{1+\xi-b\psi}$), so $\bar\ell$ rises slightly with $\tau_{t+1}$: a larger system makes the
  corner slightly harder, which is the direction the plan expected, but at second order only.

The decision C.1.2 is therefore right and its reason is the first-order statement: the two scalings differ
by the factor $\tau_{t+1}\tilde V/M$ in the threshold, and only the common one lets the size of the system
separate France ($\tau = 0.213$) from the UK ($0.119$) at nearly the same dispersion. Confirmed in §3.5 by
the $\omega$ probe: $\bar\ell$ moves by 3% when $\tau_{2020}(1)$ moves by 58%.

### 3.4 Comparative statics of the threshold

Read off (A.19$'$), at fixed $\mathcal{T}'_{t+1}/\tau_{t+1}$:

- *Dispersion.* $\tilde V$ enters the threshold in two places: the redistributive part of the stake,
  $S_\mu/\bar\mu - 1$ ($= \tilde V$ with equal propensities), and the conversion $\underline\lambda_1 = \bar\ell/(\tau_{t+1}\tilde V)$.
  The common part of the obstacle, $1 - \mathcal{F}$, does not scale with the dispersion, and it is the
  larger part: on the U.S. at Q the stake is $-0.188$ of which the redistributive part is $-0.043$, and the
  common part net of the hours and return gains is $-0.110$ (§3.5). So
  $\underline\lambda_1\tau_{t+1} = \frac{1}{\hat\Phi_1}\big[1 + \frac{1-\mathcal{F}}{\tilde V}\big]$ with equal
  propensities: compressing the distribution *raises* the threshold, since the cost's marginal benefit
  falls one for one with $\tilde V$ while most of the obstacle stays. This is what France's lower
  dispersion does, and why the weight of the linear term matters for France (Overturned 2): under $M$ the
  conversion is $\bar\ell/(\tau_{t+1}M)$ and $M$ falls by a quarter from the U.S. to France where
  $\tilde V$ halves.
- *Size.* $\underline\lambda_1 \propto 1/\tau_{t+1}$ (first order), plus the second-order rise of
  $\bar\ell$ in $\psi_{t+1}$. France's larger system lowers its threshold by the factor
  $0.134/0.213 = 0.63$ relative to the U.S.; its lower dispersion raises it by $2.0$ ($\tilde V$) or $1.36$
  ($M$); its stake per unit, $\bar\ell$, is $0.72$ of the U.S. value (the older population, $\nu_{1990} = 1.03$
  against $1.41$, raises the retirees' weight in the hours term, and the flat profile with a lower
  $\tilde V$ gives $S_\mu/\bar\mu = 1.21$ against $1.29$). Net: $0.72 \times 0.63 \times 2.0 = 0.90$ under
  $\tilde V$ (France's threshold 10% below the U.S. threshold, but above the U.S. L value, which is 0.80 of
  the U.S. threshold), $0.72 \times 0.63 \times 1.36 = 0.62$ under $M$.
- *Ageing.* A lower $\nu_t$ raises $\hat c_H = \frac{\omega(1-\alpha)}{\nu_t\beta} + \dots$ and with it
  both $\mathcal{F}$ and $\hat\Phi_1$: the corner is easier (retirees are unanimous for it). The tax
  channel adds: ageing raises $\tau_{t+1}$ and lowers $\underline\lambda_1$ through the conversion. On the
  U.S. between the 1990 choice ($\nu_{1990} = 1.41$, $\tau_{2020}(1) = 0.134$) and the 2020 choice
  ($1.34$, $0.187$) the threshold falls from 2.82 to 2.11 with $\bar\ell$ nearly constant (0.1645, 0.172).
- *Voting profile.* $\mu_i$ enters only through $S_\mu/\bar\mu$, the voting-weighted harmonic mean of
  relative income. A profile rising with income lowers it (the U.S.: 1.294 against 1.436 with equal
  propensities), a flat one restores $1+\tilde V$: France's voting patterns raise the threshold, by the
  share $(S_\mu/\bar\mu - 1)/(S_\mu/\bar\mu - \mathcal{F})$ of the obstacle that is redistributive, about a
  quarter.

### 3.5 Numerical confirmation

Scripts in the session's scratchpad (`cornerCheck.py`, `crossSection.py`), interpreter `.venv`, about
four minutes each. The general $f$ of (A.1) is monkey-patched onto `base.Base.fWedge` and
`dlnfWedge_dτ`, so the check is of the algebra against `LeadedLOG.objective` and does not depend on the
coder's in-progress specs; at $\lambda_1 = 0$ the patch reproduces `'size'` (design in force at 2020:
0.7382). Models: `ModelESC` on `test.py`'s workbook, common $X$, $\rho = 1$, $(\beta,\omega)$ seeded from
`results/calibration/US_rhoGridCommonX.csv` and recalibrated at $\lambda_Q = 8.643$; France and the UK
through `testEU.load` and `ModelESC`+`ModelFR`, calibrated at $\lambda_Q$ ($\omega = 1.418$ and $1.217$,
choices under the U.S. parameter 0.7489 and 0.6246, as `results/esc/escCountry.csv`). The objective is
evaluated on the 121 candidates with $\mathcal{T}_{t+1}$ solved at each candidate (`τOfθ`, polished); the
derivative at the corner by a one-sided second-order difference ($h = 10^{-3}$); $\mathcal{T}'_{t+1}(1)$ the
same way on the tax policy.

*(A.17) against the finite difference*, choice at 1990 for 2020, relative difference below
$5\times10^{-6}$ at every point:

| economy | $(\lambda_1,\lambda_2)$ | analytic | finite diff. | hours | return $s_t$ | return $h_{t+1}$ | flat benefit | $\mathcal{T}'_{2020}(1)$ | choice |
|---|---|---|---|---|---|---|---|---|---|
| U.S. | (0, 8.64) Q | $-0.1524$ | $-0.1524$ | $+0.061$ | $-0.038$ | $+0.012$ | $-0.188$ | $-0.090$ | 0.738 |
| U.S. | (3, 0) | $+0.0097$ | $+0.0097$ | $+0.177$ | $+0.022$ | $-0.002$ | $-0.188$ | $+0.015$ | 1 |
| U.S. | (8, 0) | $+0.2798$ | $+0.2798$ | $+0.371$ | $+0.123$ | $-0.026$ | $-0.188$ | $+0.190$ | 1 |
| U.S. | (8, 8.64) | $+0.2798$ | $+0.2798$ | same | same | same | same | same | 1 |
| France | (0, 8.64) Q | $-0.1065$ | $-0.1065$ | $+0.164$ | $-0.022$ | $+0.010$ | $-0.259$ | $-0.063$ | 0.748 |
| UK | (0, 8.64) Q | $-0.0894$ | $-0.0894$ | $+0.061$ | $-0.022$ | $+0.007$ | $-0.136$ | $-0.057$ | 0.624 |

The $\lambda_2$ rows coincide with the L rows at the corner, as (A.12) says. The "hours" column is
$(1-\alpha)\omega\bar\mu H_{t+1} + \nu_t\bar\mu(1+\beta)\frac{1+\xi}{\xi}H_{t+1}$ and the "return $s_t$" column
$-\nu_t\bar\mu\beta\frac{1-\alpha}{1+\alpha\xi}\big[\frac{1+\xi}{\xi}H_{t+1} - \psi_{t+1}(b+\chi_{t+1})\big]$, the
script's grouping; their sum is the first two terms of (A.17). The U.S. 2020 choice at Q is 0.7936 here
against 0.7973 in `escPath.csv` (the interpolation item in the preamble).

*The threshold (A.19) with (A.20) solved as a fixed point*, and the choice on either side of it:

| economy ($t \to t+1$) | $\tau_{t+1}(1)$ | $\nu_t$ | $\tilde V$ | $M$ | $S_\mu/\bar\mu$ | $\psi$ | $\Lambda$ | $\underline\lambda_1$ | $\bar\ell$ | $\bar\ell/M$ | choice at $0.9\underline\lambda_1$, L / LQ | at $1.1\underline\lambda_1$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U.S. 1990 $\to$ 2020 | 0.1339 | 1.405 | 0.436 | 0.575 | 1.294 | 0.238 | 0.086 | **2.821** | 0.1645 | 0.286 | 0.809 / 0.973 | 1 / 1 |
| U.S. 2020 $\to$ 2050 | 0.1869 | 1.340 | 0.436 | 0.575 | 1.294 | 0.304 | 0.112 | 2.113 | 0.172 | 0.299 | 0.831 / 0.979 | 1 / 1 |
| U.S., $\omega \times 1.3$ | 0.2123 | 1.405 | 0.436 | 0.575 | 1.294 | | | 1.839 | 0.170 | | | |
| France 1990 $\to$ 2020 | 0.2129 | 1.026 | 0.218 | 0.422 | 1.208 | 0.332 | 0.124 | **2.548** | 0.1184 | 0.280 | 0.790 / 0.974 | 1 / 1 |
| UK 1990 $\to$ 2020 | 0.1092 | 1.092 | 0.223 | 0.292 | 1.187 | 0.203 | 0.072 | **4.143** | 0.1009 | 0.346 | 0.753 / 0.960 | 1 / 1 |

LQ in the last two columns is at $\lambda_2 = \lambda_Q$. $\mathcal{T}'_{2020}(1)$ at the threshold is
$+0.009$ (U.S.), $+0.007$ (France), $+0.004$ (UK): the tax response has just turned positive, as (A.20)
predicts ($\ell^{0} = 0.150$ for the U.S.).

*The U.S. L value and the cross-section under L* (`crossSection.py`): $\lambda_1^{US} = 2.441$ at the
Q-calibrated $(\beta,\omega)$ and $2.256$ with $(\beta,\omega)$ recalibrated at each trial
($\beta = 0.756$, $\omega = 1.565$; the share lost at the observed design is 3.7% against 1.8% under Q).
At $\lambda_1 = 2.256$: France chooses 0.7575 under the $\tilde V$ weight and the corner under the $M$
weight; the UK chooses $\theta = 0$ under both. France's own threshold is $2.548 = 1.13\,\lambda_1^{US}$
($\tilde V$) or $1.738 = 0.77\,\lambda_1^{US}$ ($M$); the UK's own L value is $3.42 = 1.52\,\lambda_1^{US}$,
its corner threshold 4.14.

## 4. Calibration and identification

### 4.1 Q and L: one parameter per economy

Q: the U.S. $\lambda$ on $\theta_{2020} = \theta^{\ast}$ (the design in force in 2020, chosen in 1990), the
UK's own $\lambda$ likewise, France none. L: the same two, and France's own parameter is the threshold
$\underline\lambda_1^{FR}$ of (A.19): any $\lambda_1 \geq \underline\lambda_1^{FR}$ re-elects the corner, so
the calibration is set-valued, $[\underline\lambda_1^{FR},\infty)$, and the number to report is the bound.
Under LQ at a given $\kappa$ the same set is $\lambda \geq \underline\lambda_1^{FR}/\kappa$. The residual
of `calibrateWedge` is flat at a corner, so the threshold has to be found on the sign of the corner
derivative or on the smallest $\lambda_1$ at which the grid argmax is 1 (the coder's `calibrateWedgeCorner`),
not on a root of the residual.

### 4.2 LQ: $(\lambda,\kappa)$ on two designs

Along the U.S.-calibrated curve $\lambda_{US}(\kappa)$ the first-order condition at $\theta^{US}$ holds,
which to first order pins the marginal cost there,
$\lambda_{US}(\kappa)\,[\kappa + (1-\theta^{US})] \approx \lambda_Q(1-\theta^{US})$. The marginal cost at any
other design, relative to its value at the U.S. design, is then
$$
\frac{\partial\ln f/\partial\theta\,\big|_{\theta}}{\partial\ln f/\partial\theta\,\big|_{\theta^{US}}} = \frac{\kappa + (1-\theta)}{\kappa + (1-\theta^{US})},
\tag{A.22}
$$
which for $\theta < \theta^{US}$ falls monotonically from $\frac{1-\theta}{1-\theta^{US}} > 1$ at $\kappa = 0$
to 1 as $\kappa \to \infty$, and for $\theta > \theta^{US}$ rises from below 1 to 1. So, holding the U.S.
condition, raising $\kappa$ lowers the UK's chosen design and raises France's, both monotonically and both
toward the data. The UK under Q chooses 0.625 above its 0.560, so $\kappa \geq 0$ is the right side; the map
is monotone, so the root is unique if it exists; it exists if the L limit ($\kappa \to \infty$,
$\lambda\kappa \to \lambda_1^{US}$) puts the UK below 0.560, which it does (the UK chooses 0 there). What
(A.22) drops: the level $f$ (lower under a larger $\kappa$; the share lost at the U.S. design is 1.8% at
$\kappa = 0$, 2.3% at $\kappa = 0.11$, 3.7% in the L limit) and the response of $\mathcal{T}_{t+1}$ to the
spec; neither changes the direction.

The UK's own $\lambda$ at the common $\kappa$ reproduces $\lambda_{US}(\kappa)$ by construction, since
the UK's design is what pinned $\kappa$. The fallback (France pins $\kappa$) is needed when no
$\kappa \geq 0$ puts the UK on its design, which is not the case; it would be *usable* only if some
$\kappa$ puts France at the corner, that is $\lambda_{US}(\kappa)\,\kappa \geq \underline\lambda_1^{FR}$, which
fails under the $\tilde V$ weight because $\lambda_{US}(\kappa)\kappa$ is capped at $\lambda_1^{US} < \underline\lambda_1^{FR}$,
and holds under the $M$ weight from $\kappa \approx 1$ on.

### 4.3 What to expect

France's chosen design sits within 0.01 of the U.S. design under Q (0.749 against 0.738), so by (A.22)
the split between the linear and the quadratic term barely moves its marginal cost at the margin: along
the U.S.-calibrated curve France moves from 0.748 ($\kappa = 0$) to 0.763 ($0.25$), 0.776 ($0.5$), 0.797
($1$), 0.823 ($2$), 0.852 ($4$), while the UK falls from 0.625 to 0.552, 0.493, 0.404, 0.287, 0.162. The
UK's design pins a small $\kappa$ (about 0.11) and France stays where Q had it. France's corner needs
$\lambda\kappa \geq \underline\lambda_1^{FR}$, a large linear term, which the UK's design rules out.

### 4.4 Numerical confirmation (proxy)

`crossSection.py`, $(\beta,\omega)$ held rather than recalibrated at each $(\lambda,\kappa)$ (the U.S. at
its L calibration, $\beta = 0.756$, $\omega = 1.565$; France and the UK at their Q calibrations), exact tax
policy at the candidates; the paper's procedure recalibrates and the numbers will differ in the second
decimal. Joint calibration on the U.S. (0.738) and the UK (0.560):
$\kappa = 0.112$, $\lambda = 5.75$ ($\lambda\kappa = 0.645$); France predicted 0.733 under the
$\tilde V$ weight and 0.775 under $M$ (same U.S. and UK numbers to 0.001). Along the curve:
$\kappa = 1$, $\lambda = 1.76$: the UK 0.339, France 0.739 ($\tilde V$) and 1.000 ($M$); $\kappa = 4$,
$\lambda = 0.527$: the UK 0.059, France 0.748 and 1.000. The $\kappa$ sweep of §4.3 (U.S. $\lambda(\kappa)$
at the Q calibration): $\lambda = 8.66, 4.59, 3.12, 1.90, 1.07, 0.57$ at $\kappa = 0, 0.25, 0.5, 1, 2, 4$,
so $\lambda\kappa$ rises to 2.28 at $\kappa = 4$ and tends to $\lambda_1^{US}$.

## 5. The counterfactuals per variant

The response of the chosen design to a shock is $d\theta/dx = -\mathcal{B}_{\theta x}/\mathcal{B}_{\theta\theta}$.
The cost contributes to $\mathcal{B}_{\theta\theta}$ through the slope of its marginal benefit in the
design, $-\lambda_2\tau_{t+1}\tilde V \times$ (the pension's weight) under Q and LQ and nothing under L
(A.9), on top of the costless curvature, which is weak ($\mathcal{B}_t'' \approx -0.07$ on $[0,1]$ at the
U.S. calibration, no sign change). Every response is therefore larger under L than under Q, LQ in between
in proportion to $\kappa$, and under L a shock that raises $\ell_{t+1}$ above $\bar\ell$ sends the choice to
the corner.

- *Acute ageing* ($\nu_t = 1$). Both channels of Q (the retirees' weight; the tax, which raises the
  marginal benefit through $\tau_{t+1}$ in every variant, (A.9)) are present under L and LQ. Under L the
  marginal benefit does not fall as the design rises, so the response is not damped: on the U.S. L
  calibration the tax at the corner rises from 0.134 to about 0.21, $\ell_{t+1}$ by 57%, past the threshold,
  and the choice is the corner (proxy: Q 0.833, L 1.000, at the L calibration's $(\beta,\omega)$; the
  paper's Q number is 0.825). Under LQ at $\kappa \approx 0.1$ expect a response a little above Q's
  (0.738 $\to$ about 0.83 to 0.85).
- *France's income distribution* (lower $\tilde V$). Both terms of the cost scale with $\tilde V$, as
  does the redistributive part of the stake; the common part and the forward-looking gains do not. Under
  Q the design rises a little (0.772) because the forward-looking stake gains ground. Under L the same
  mechanism with no damping sends the choice to the corner (proxy 1.000; under LQ at $\kappa = 0.22$,
  0.815). Signed: up, more under L.
- *France's voting patterns* (flat $\mu_i$). $S_\mu/\bar\mu$ rises toward $1+\tilde V$; the redistributive
  force of `prop:esc:corner` regains ground; the design falls (Q 0.653). Under L the fall is to the
  Beveridgean corner or next to it (proxy 0.044; LQ at $\kappa = 0.22$: 0.632). Combined with France's
  income distribution: Q 0.627, L 0.000, LQ 0.599. Signed: down, more under L.
- *The baseline drift* with $\nu_t$ from 1.34 to 1.07. Under Q the design rises from 0.738 to 0.809 by
  2110. Under L the drift is larger and reaches the corner within one or two periods (the threshold falls
  from 2.82 to 2.11 between the 1990 and the 2020 choice while $\lambda_1^{US} = 2.26$ is fixed), so the
  tax path then carries no further design response. Under LQ at $\kappa \approx 0.1$ a drift somewhat above
  Q's, interior.

Under every variant the share of revenue lost at the observed design rises with the linear term
(1.8%, 2.3%, 3.7% at $\kappa = 0$, $0.11$, $\infty$), so the tax that the cost makes "worth less at the
margin" (section 7.2's reading) is worth less still under L, and the pinned tax responses move accordingly.

## 6. A tex-ready block for appendix C.2 and section 7.1

The writers adapt; `eq:esc:AB` keeps its label for the $(A,B)$ definition, the general $f$ takes
`eq:esc:fGeneral`, the corner proposition `prop:esc:bismarckCorner`. Register as C.2's paragraphs.

```latex
\smalltitle{Specification.} The exponential form $f(\theta_t,\tau_t)$ of \eqref{eq:esc:budget} scales both components of the benefit alike,
\begin{align}\label{eq:esc:AB}
    A(\theta_t,\tau_t) = f(\theta_t,\tau_t)\,\theta_t, \qquad B(\theta_t,\tau_t) = f(\theta_t,\tau_t)\,(1-\theta_t),
\end{align}
so that the surviving share of revenue is $A+B = f \in (0,1]$. We let the leak have a part proportional to the amount carried and a part rising with it,
\begin{align}\label{eq:esc:fGeneral}
    f(\theta_t,\tau_t) = \exp\Big\{-\tau_t\tilde{V}\,(1-\theta_t)\Big[\lambda_1 + \tfrac{1}{2}\lambda_2\,(1-\theta_t)\Big]\Big\},
\end{align}
so that $1-f$ is, to first order, $\lambda_1\tau_t\tilde{V}(1-\theta_t) + \tfrac{1}{2}\lambda_2\tau_t\tilde{V}(1-\theta_t)^2$: the second term is the Harberger share with $\lambda_2$ in the place of $\varepsilon\Pi_t$,\footnote{The return factor multiplies every implicit tax alike and so scales the loss once. It carries $\nu_t$ and would make a structural cost parameter drift with demographics; we absorb it into the cost parameters, which are calibrated rather than derived.} the first a constant share of every unit the flat component carries, scaled by the same load $\tau_t\tilde{V}$.\footnote{A leak proportional to the amount carried, Okun's bucket read literally, loses a share $\lambda_1(1-\theta_t)\sum_i\gamma_i|y_i-1|$ of revenue, independent of the size of the system: the corner would then be as far for a large system as for a small one, and only the quadratic part would dissipate at the margin of the tax. We scale the linear term with $\tau_t\tilde{V}$ like the quadratic one, so that one load governs both and the size of the system lowers the cost parameter at which the Bismarckian corner is reached, in proportion to $1/\tau_{t+1}$ (proposition \ref{prop:esc:bismarckCorner}).} The quadratic cost of section \ref{sec:esc:cost} is $\lambda_1 = 0$; a purely linear leak is $\lambda_2 = 0$; we write the general case as a scale and a shape, $\lambda_1 = \lambda\kappa$ and $\lambda_2 = \lambda$. The exponential keeps $f$ positive for every parameter and every size of system, and nests the model without the cost at $\lambda = 0$. Three properties hold for every variant. Nothing is lost when nothing is redistributed, $f = 1$ at $\theta_t = 1$ and for every design when $\tilde{V} = 0$. The loss per unit of redistribution rises with the size of the system, through $\tau_t$, and since $\ln f$ is linear in $\tau_t$ the marginal contribution is worth $1 + \ln f$ of its revenue to a retiree whatever the variant (appendix \ref{app:esc:equilibrium}). And the marginal cost of the first unit of redistribution is
\begin{align*}
    \frac{\partial \ln f}{\partial \theta_t}\Big|_{\theta_t = 1} = \lambda_1\tau_t\tilde{V},
\end{align*}
zero under the quadratic cost, under which no electorate chooses the Bismarckian corner, and positive under the two with a linear term, which is what lets an electorate choose it. Scaling both components alike is a choice. A cost on the flat component alone delivers the same endpoints and differs in the interior, but it loses the separate identification of $\theta$ and the cost parameters (appendix \ref{app:esc:equilibrium}). A cost on the design itself rather than on the transfer it performs, $f(\theta) = \phi + (1-\phi)\theta^{p}$, stays in place when a compressed income distribution removes the redistributive stakes; the \oa{esc-scale} reports it.

\smalltitle{The Bismarckian corner.} With the design chosen one period in advance under log preferences the choice maximizes $\mathcal{B}_t(\theta_{t+1})$ alone (proposition \ref{prop:esc:separability}), and at $\theta_{t+1} = 1$ the cost enters its slope through one number, the marginal share saved by the first unit of design, $\ell_{t+1} \equiv \lambda_1\tau_{t+1}\tilde{V}$, where $\tau_{t+1} = \mathcal{T}_{t+1}(1)$ is the tax the young anticipate at the Bismarckian design.
\begin{proposition}\label{prop:esc:bismarckCorner}
Assume log-GHH preferences, no informal households, a time-invariant distribution of types, and let the design be chosen one period in advance under the cost \eqref{eq:esc:fGeneral}. Write $\psi_{t+1} \equiv \frac{\frac{1-\alpha}{\alpha}\tau_{t+1}}{1+\frac{1-\alpha}{\alpha}\tau_{t+1}}$, $b \equiv \frac{\beta}{1+\beta}$, $\Lambda_{t+1} \equiv \frac{b\psi_{t+1}}{1+\xi-b\psi_{t+1}}$, $\bar{\mu} \equiv \sum_i\gamma_i\mu_i$, $S_{\mu} \equiv \sum_i\gamma_i\mu_i/y_i$, and let $\mathcal{T}'_{t+1}$ be the slope of the equilibrium tax function in the inherited design at $\theta_{t+1} = 1$. Then
\begin{align}\label{eq:esc:cornerFOC}
    \frac{\partial \mathcal{B}_t}{\partial \theta_{t+1}}\Big|_{\theta_{t+1} = 1}
    = \bar{\mu}\,c_{H}\,H_{t+1}
    + \bar{\mu}\nu_t\beta\,\frac{1-\alpha}{1+\alpha\xi}\,\psi_{t+1}\Big(b + \ell_{t+1} + \frac{\mathcal{T}'_{t+1}}{\tau_{t+1}}\Big)
    - \bar{\mu}\nu_t\beta\,\frac{(1-\alpha)\xi}{1+\alpha\xi}\,\frac{\mathcal{T}'_{t+1}}{1-\tau_{t+1}}
    - \nu_t\beta\,\psi_{t+1}S_{\mu},
\end{align}
with $H_{t+1} = \frac{\xi}{1+\alpha\xi}\Lambda_{t+1}\big[1 - b\psi_{t+1} + (1-\psi_{t+1})\big(\ell_{t+1} + \mathcal{T}'_{t+1}/\tau_{t+1}\big)\big]$ and $c_{H} = \omega(1-\alpha) + \nu_t\frac{1+\xi}{\xi}\frac{1+\alpha\xi+\alpha\beta(1+\xi)}{1+\alpha\xi}$. At a given $\mathcal{T}'_{t+1}$ the slope is affine and increasing in $\ell_{t+1}$, so the Bismarckian corner is a local maximum of $\mathcal{B}_t$ if and only if $\lambda_1 \geq \underline{\lambda}_1$, with $\underline{\lambda}_1\,\tau_{t+1}\tilde{V}$ the value of $\ell_{t+1}$ at which \eqref{eq:esc:cornerFOC} vanishes; $\lambda_2$ does not enter. As $\tau_{t+1} \to 0$ at a given $\mathcal{T}'_{t+1}/\tau_{t+1}$ every term of \eqref{eq:esc:cornerFOC} is of order $\tau_{t+1}$, so $\underline{\lambda}_1\tau_{t+1}\tilde{V}$ is independent of the size of the system to first order and $\underline{\lambda}_1$ is proportional to $1/\tau_{t+1}$.
\end{proposition}

\smalltitle{Proof of proposition \ref{prop:esc:bismarckCorner}.} By \eqref{eq:esc:leadFOC} the slope of $\mathcal{B}_t$ is $\sum_i\gamma_i\mu_i[\omega(1-\alpha)\,d\ln\Theta_{h,t} + \nu_t((1+\beta)\,d\ln\tilde{c}_{1,t}^i + \beta\,d\ln R_{t+1})]/d\theta_{t+1}$, each derivative carrying $\tau_{t+1} = \mathcal{T}_{t+1}(\theta_{t+1})$. At $\theta_{t+1} = 1$, $f = 1$, $A = 1$, $B = 0$ and $\partial f/\partial\tau_{t+1} = f\ln f/\tau_{t+1} = 0$, so by \eqref{eq:esc:fGeneral} $dA/d\theta_{t+1} = 1 + \ell_{t+1}$ and $dB/d\theta_{t+1} = -1$, whatever $\lambda_2$. From \eqref{eq:esc:auxiliary:Gammas}, $\Gamma_{s,t} = \Gamma_h b/\big((1+\xi)[1 + \frac{1-\alpha}{\alpha}\tau_{t+1}(A + \frac{B}{1+\beta})]\big)$, so $d\ln\Gamma_{s,t}/d\theta_{t+1} = -\psi_{t+1}(b + \ell_{t+1} + \mathcal{T}'_{t+1}/\tau_{t+1})$; from \eqref{eq:esc:auxiliary:Thetah}, in which $\frac{1-\alpha}{\alpha}A\tau_{t+1}\Gamma_{s,t}/\Gamma_h = b\psi_{t+1}/(1+\xi)$ at the corner, $d\ln\Theta_{h,t}/d\theta_{t+1} = \frac{\xi}{1+\alpha\xi}\Lambda_{t+1}\,d\ln(A\tau_{t+1}\Gamma_{s,t})/d\theta_{t+1} = H_{t+1}$. The young's consumption is $\tilde{c}_{1,t}^i = \frac{(h_t/\Gamma_h)^{(1+\xi)/\xi}}{1+\beta}\big[\frac{y_i\Gamma_h}{1+\xi} + \frac{1-\alpha}{\alpha}\tau_{t+1}B\,\Gamma_{s,t}\big]$ (appendix \ref{app:EE:CRRA} with $s_t$ eliminated by \eqref{eq:s}), whose bracket at the corner is $y_i\Gamma_h/(1+\xi)$, so $d\ln\tilde{c}_{1,t}^i/d\theta_{t+1} = \frac{1+\xi}{\xi}H_{t+1} - b\psi_{t+1}/y_i$: the only type-specific term is the loss of the flat benefit, a larger share of a poorer type's surplus. The return satisfies $\ln R_{t+1} = \text{const} - \frac{1-\alpha}{1+\alpha\xi}\ln(s_t/\nu_{t+1}) + (1-\alpha)\ln\Theta_{h,t+1}$ with $\ln s_t = \frac{1+\xi}{\xi}\ln h_t + \ln\Gamma_{s,t}$, and $\Theta_{h,t+1}$ depends on $\theta_{t+1}$ only through $(1-\tau_{t+1})^{\xi/(1+\alpha\xi)}$, the continuation design being state-free (proposition \ref{prop:esc:separability}); hence $d\ln R_{t+1}/d\theta_{t+1} = -\frac{1-\alpha}{1+\alpha\xi}[\frac{1+\xi}{\xi}H_{t+1} - \psi_{t+1}(b + \ell_{t+1} + \mathcal{T}'_{t+1}/\tau_{t+1})] - \frac{(1-\alpha)\xi}{1+\alpha\xi}\mathcal{T}'_{t+1}/(1-\tau_{t+1})$. Retirees see $\theta_{t+1}$ only through $(1-\alpha)\ln h_t$. Summing with the weights of \eqref{eq:LOG:PolObj} gives \eqref{eq:esc:cornerFOC}; $\ell_{t+1}$ enters linearly through $H_{t+1}$ and the savings term, with the coefficient $\bar{\mu}[c_H\frac{\xi}{1+\alpha\xi}\Lambda_{t+1}(1-\psi_{t+1}) + \nu_t\beta\frac{1-\alpha}{1+\alpha\xi}\psi_{t+1}] > 0$. As $\tau_{t+1} \to 0$, $\psi_{t+1}$ and $\Lambda_{t+1}$ are of order $\tau_{t+1}$ and so is every term, which gives the last claim.

The tax response is itself a function of the cost: at the corner the retirees' term of the tax condition \eqref{eq:esc:E2} has slope $\frac{\omega\frac{1-\alpha}{\alpha}}{(1+\frac{1-\alpha}{\alpha}\tau_{t+1})^2}\big[-(1+\frac{\frac{1-\alpha}{\alpha}\tau_{t+1}}{1+\beta})(S_{\mu}-\bar{\mu}) + \ell_{t+1}(2+\frac{1-\alpha}{\alpha}\tau_{t+1})\bar{\mu}\big]$ in the design, the cost entering once through $A$ and once through the factor $1 + \ln f$, so $\mathcal{T}'_{t+1}$ rises linearly with $\ell_{t+1}$ from the negative slope of proposition \ref{prop:LOG:PEE} and is positive at the threshold: a more Bismarckian design then raises the tax, since the dissipation it saves raises what the marginal contribution is worth to retirees. The threshold of section \ref{sec:esc:calibration} solves \eqref{eq:esc:cornerFOC} with this response. With equal propensities to vote $S_{\mu} = \bar{\mu}(1+\tilde{V})$, so the loss of the flat benefit splits into a part common to all types and a redistributive part proportional to $\tilde{V}$; the common part, net of the gains in hours and returns, is the larger obstacle at the calibrated economies, and it does not scale with the dispersion, which is why a compressed income distribution raises the threshold while a larger system lowers it.
```

For section 7.1, after the paragraph that reads the cost (three to four sentences):

```latex
The quadratic loss has a property that the data reject: the marginal cost of the first unit of redistribution is zero, so no electorate chooses the Bismarckian corner, which is France's observed design. We therefore let the leak have a constant part as well, a share of every unit the flat component carries, and compare three variants of the cost: the quadratic one, a purely linear one, and the two together, written as a scale $\lambda$ and a shape $\kappa$, $1 - f \approx \lambda\tau_t\tilde{V}(1-\theta_t)[\kappa + \tfrac{1}{2}(1-\theta_t)]$ (appendix \ref{app:esc:cost}). The linear part prices the first unit of redistribution at $\lambda\kappa\tau_t\tilde{V}$, and an electorate chooses the Bismarckian corner once this exceeds a threshold that falls with the size of the system and rises with a flatter voting profile and a more compressed income distribution (proposition \ref{prop:esc:bismarckCorner}). The variants share the solution of appendix \ref{app:esc:equilibrium}, the identification of $\theta^{\ast}$ and the factor by which a larger system is worth less to a retiree at the margin; they differ in how the marginal cost falls as the design becomes more earnings-related, and so in how far a shock moves the chosen design.
```

## 7. Under the $M$ weight

Gate 1 adopted the $M$ weight on the linear term (§1.4); the $\tilde V$-weighted linear-quadratic form
stays in the code as `'sizeLQV'`. §1 to §6 are left as written and this section restates what changes.
Numbers are from `mWeight.py` (scratchpad, four minutes), the form (A.28) patched onto `base.Base` as
before, $(\beta,\omega)$ held at the Q calibration unless said; (A.17) with $\ell_{t+1} = \lambda_1\tau_{t+1}M$
agrees with the finite difference of the objective to $10^{-6}$ relative on the three economies.

### 7.1 The form

$$
f(\theta_t,\tau_t) = \exp\Big\{-\tau_t(1-\theta_t)\Big[\lambda_1 M + \tfrac12\lambda_2\tilde V(1-\theta_t)\Big]\Big\},
\qquad M \equiv \sum_i\gamma_i|y_i-1|, \qquad \tilde V \equiv \sum_i\gamma_i\frac{(y_i-1)^2}{y_i},
\tag{A.28}
$$
$M$ the mean absolute deviation of relative income, which by (A.5) is the amount the flat component
carries per unit of $\tfrac12\Pi_t\tau_t(1-\theta_t)$. To first order in $\ln f$,
$$
1 - f \approx \lambda_1\tau_t M(1-\theta_t) + \tfrac12\lambda_2\tau_t\tilde V(1-\theta_t)^2,
\tag{A.29}
$$
dropping $\tfrac12(\ln f)^2$ as in (A.2). Scale and shape: $\lambda_1 = \lambda\kappa$, $\lambda_2 = \lambda$,
so $\ln f = -\lambda\tau_t(1-\theta_t)[\kappa M + \tfrac12\tilde V(1-\theta_t)]$; $\kappa = 0$ is Q and
$\lambda_2 = 0$ is L. $\kappa$ now multiplies $M$: for one economy the two weights give the same $f$ at
$\kappa^{M}M = \kappa^{\tilde V}\tilde V$, so on the U.S. $\kappa^{M} = 0.758\,\kappa^{\tilde V}$ at the same
$\lambda$, and every U.S.-only number of §3.5 and §5 is a relabelling. Properties: (i) $f = 1$ at
$\theta_t = 1$, and $f = 1$ for every design when all incomes are equal, since $M$ and $\tilde V$ vanish
together, exactly when every $y_i = 1$. (ii) $\partial(1-f)/\partial\tau_t = -f\ln f/\tau_t \geq 0$. (iii)
$$
\frac{\partial\ln f}{\partial\theta_t} = \tau_t\big[\lambda_1 M + \lambda_2\tilde V(1-\theta_t)\big], \qquad
\frac{\partial\ln f}{\partial\theta_t}\Big|_{\theta_t = 1} = \lambda_1\tau_t M \equiv \ell_t .
\tag{A.30}
$$
(iv) $\ln f$ is linear in $\tau_t$, so $\partial\ln f/\partial\tau_t = \ln f/\tau_t$ and the factor of
`eq:esc:E2` is $1 + \ln f$, as (A.4). §2 carries over unchanged; (A.9) reads
$\partial f/\partial\theta_{t+1} = f\tau_{t+1}[\lambda_1 M + \lambda_2\tilde V(1-\theta_{t+1})]$.

### 7.2 The corner proposition and its comparative statics under $M$

(A.10)--(A.19) hold verbatim with $\ell_{t+1} = \lambda_1\tau_{t+1}M$: the derivative (A.17) sees the cost
only through $\ell_{t+1}$, the marginal share saved by the first unit of design, and the weight only fixes
what $\ell_{t+1}$ is in terms of $\lambda_1$. The bound $\bar\ell = -\Phi_0/\Phi_1$ of (A.19) is therefore
the same number as under $\tilde V$ (0.1645 for the U.S. 1990 choice, 0.1184 for France, 0.1009 for the
UK), and the threshold on the parameter is
$$
\underline\lambda_1^{M} = \frac{\bar\ell}{\tau_{t+1}M} = \underline\lambda_1^{\tilde V}\,\frac{\tilde V}{M}.
\tag{A.31}
$$
The tax response (A.20) is unchanged in $\ell_{t+1}$: the slope of the factor $1 + \ln f$ at the corner is
$\ell_{t+1}$ whatever the weight, so $\mathcal{T}'_{t+1} = \mathcal{T}'_0(1 - \ell_{t+1}/\ell^{0})$ with the same
$\ell^{0}$ and the same sign change (0.150 on the U.S., below $\bar\ell$). The first-order cancellation
of §3.3 is unchanged: the condition is on $\ell_{t+1}$, of order one, so $\underline\lambda_1^{M} \propto 1/\tau_{t+1}$
under (A.28), and the $\tau$-free leak (A.6) remains the size-neutral alternative.

*Comparative statics.* With equal propensities (A.19$'$) becomes
$$
\underline\lambda_1^{M}\,\tau_{t+1} = \frac{1}{\hat\Phi_1}\Big[\frac{\tilde V}{M} + \frac{1-\mathcal{F}}{M}\Big]:
\tag{A.32}
$$
the redistributive part of the stake enters in the ratio $\tilde V/M$ (0.76 for the U.S. and the UK, 0.52
for France: $\tilde V$ weights a unit carried by $|y_i-1|/y_i$ and falls faster than $M$ when the
distribution is compressed) and the common part in $1/M$ (1.74, 3.43, 2.37). What changes relative to
§3.4 is the conversion alone: France's $M/\tilde V$ is 1.93 against 1.32 for the U.S. and 1.31 for the UK,
so France's lower dispersion raises its threshold by the factor $1.36$ instead of $2.0$ and the
decomposition of §3.4 reads $0.72 \times 0.63 \times 1.36 = 0.62$. France's threshold is 0.62 of the U.S.
threshold and 0.77 of the U.S. L value, inside the range in which the U.S. is interior; the UK's ratios
move by 1%. Ageing, the voting profile and the size channel read as in §3.4.

*The numbers that change* (the $\tilde V$ column from §3.5 and §4.4; the UK-pinned LQ under $\tilde V$ was
computed with the U.S. at its L calibration, the $M$ column at the Q calibration):

| | $\tilde V$ weight | $M$ weight |
|---|---|---|
| threshold $\underline\lambda_1$, U.S. 1990 $\to$ 2020 ($\bar\ell = 0.1645$) | 2.821 | 2.139 |
| threshold, U.S. 2020 $\to$ 2050 ($\bar\ell = 0.172$) | 2.113 | 1.602 |
| threshold, U.S. at $\omega \times 1.3$ ($\bar\ell = 0.170$) | 1.839 | 1.394 |
| threshold, France ($\bar\ell = 0.1184$) | 2.548 | 1.318 |
| threshold, UK ($\bar\ell = 0.1009$) | 4.143 | 3.170 |
| U.S. L value, held / recalibrated ($\beta = 0.756$, $\omega = 1.565$; the same $f$) | 2.441 / 2.256 | 1.851 / 1.710 |
| France's threshold / U.S. L value | 1.13 | 0.77 |
| UK's threshold / U.S. L value | 1.84 | 1.85 |
| UK's own L value / U.S. L value | 1.52 | 1.53 |
| France under L at the U.S. L value | 0.758 | 1.000 (corner) |
| UK under L at the U.S. L value | 0.000 | 0.000 |
| U.S.-calibrated LQ curve, $\kappa$ in own units: UK / France | $\kappa^{\tilde V} = 0.25$: 0.552 / 0.763; $0.5$: 0.493 / 0.776; $1$: 0.404 / 0.797 | $\kappa^{M} = 0.1$: 0.583 / 0.806; $0.25$: 0.530 / 0.883; $0.5$: 0.458 / 0.990; $0.75$: 0.401 / 1.000; $1$: 0.354 / 1.000 |
| UK-pinned LQ: $\kappa$, $\lambda$, $\lambda\kappa$ | 0.112, 5.75, 0.645 | 0.162, 4.92, 0.799 |
| France predicted there; share lost at $\theta^{\ast}$ | 0.733; 2.3% | 0.839; 2.7% |
| France-pinned LQ: $\kappa$, $\lambda$, $\lambda\kappa$ | none | 0.517, 2.53, 1.310 |
| UK predicted there; share lost at $\theta^{\ast}$ | -- | 0.453; 3.3% |
| U.S. counterfactuals under Q / L at the L calibration: acute ageing | 0.833 / 1.000 | 0.833 / 1.000 |
| France's income distribution ($M = 0.422$, $\tilde V = 0.218$ on the shocked U.S.) | 0.782 / 1.000 | 0.782 / 1.000 |
| France's voting patterns | 0.676 / 0.044 | 0.676 / 0.044 |
| both | 0.653 / 0.000 | 0.653 / 0.740 |

Read: under $M$ the U.S.-calibrated L cost puts France at the corner (its threshold is 0.77 of the U.S.
value) and the UK at $\theta = 0$, as under $\tilde V$; the UK-pinned LQ now predicts France at 0.84 rather
than at Q's number; the France-pinned fallback of C.1.3 is feasible at $\kappa^{M} \approx 0.5$ with the UK
predicted at 0.45 (§1.4's "$\kappa \approx 1$, the UK at 0.34" is the same point in $\tilde V$ units of
$\kappa$ on the curve of §4.4). Along the curve France rises steeply with $\kappa$ under $M$ because its
linear term at a common parameter is 1.47 times the one $\tilde V$ gives. The counterfactuals on the U.S.
are a relabelling except where the shock changes the income distribution: under L the combination of
France's income distribution and voting patterns stays interior (0.74) because $M$ falls by a quarter where
$\tilde V$ halves. The precision item of the preamble and the knife-edge character of L are unchanged.

### 7.3 A tex-ready block under $M$

Replaces §6 for the writers; labels as there.

```latex
\smalltitle{Specification.} The exponential form $f(\theta_t,\tau_t)$ of \eqref{eq:esc:budget} scales both components of the benefit alike,
\begin{align}\label{eq:esc:AB}
    A(\theta_t,\tau_t) = f(\theta_t,\tau_t)\,\theta_t, \qquad B(\theta_t,\tau_t) = f(\theta_t,\tau_t)\,(1-\theta_t),
\end{align}
so that the surviving share of revenue is $A+B = f \in (0,1]$. We let the leak have the two parts of Okun's bucket, a constant share of every unit the flat component carries and a share that rises with the load. Per unit of mean past earnings the flat component carries $\tfrac{1}{2}\Pi_t\tau_t(1-\theta_t)M$, with $M \equiv \sum_i\gamma_i|y_i-1|$ the implicit taxes \eqref{eq:esc:implicitTax} summed over the earnings they fall on, so the first part loses a share proportional to $(1-\theta_t)M$ of revenue; the second is the Harberger loss above, a share proportional to $\tau_t(1-\theta_t)^2\tilde{V}$. We write
\begin{align}\label{eq:esc:fGeneral}
    f(\theta_t,\tau_t) = \exp\Big\{-\tau_t\,(1-\theta_t)\Big[\lambda_1 M + \tfrac{1}{2}\lambda_2\,\tilde{V}\,(1-\theta_t)\Big]\Big\},
\end{align}
so that $1-f$ is, to first order, $\lambda_1\tau_t M(1-\theta_t) + \tfrac{1}{2}\lambda_2\tau_t\tilde{V}(1-\theta_t)^2$, with $\lambda_2$ in the place of $\varepsilon\Pi_t$.\footnote{The return factor multiplies every implicit tax alike and so scales the loss once. It carries $\nu_t$ and would make a structural cost parameter drift with demographics; we absorb it into the cost parameters, which are calibrated rather than derived.} Each term carries its own dispersion: a leak proportional to the amount carried counts every unit alike, and its weight is the amount, $M$; a loss quadratic in each type's wedge counts a unit carried by the wedge it travels under, $|y_i-1|/y_i$, so that a given transfer counts for more against a smaller income, which is $\tilde{V}$. The one choice in \eqref{eq:esc:fGeneral} is the factor $\tau_t$ on the linear term. A constant share of the amount carried is, as a share of revenue, independent of the size of the system; we let it rise with the size of the system as the quadratic share does.\footnote{Under the literal leak, $1 - f \approx \lambda_1(1-\theta_t)M + \tfrac{1}{2}\lambda_2\tau_t\tilde{V}(1-\theta_t)^2$, the cost parameter at which an electorate chooses the Bismarckian corner is independent of the size of the system to first order, and only the quadratic part dissipates at the margin of the tax, so that the factor of appendix \ref{app:esc:equilibrium} becomes $1 + \ln f + \lambda_1(1-\theta_t)M$. With the factor $\tau_t$ that parameter is proportional to $1/\tau_{t+1}$ (proposition \ref{prop:esc:bismarckCorner}), which is what lets the size of the system separate France from the UK at nearly the same dispersion, and one factor $1+\ln f$ serves every variant.} The quadratic cost of section \ref{sec:esc:cost} is $\lambda_1 = 0$; a purely linear leak is $\lambda_2 = 0$; we write the general case as a scale and a shape, $\lambda_1 = \lambda\kappa$ and $\lambda_2 = \lambda$. The exponential keeps $f$ positive for every parameter and every size of system, and nests the model without the cost at $\lambda = 0$. Three properties hold for every variant. Nothing is lost when nothing is redistributed, $f = 1$ at $\theta_t = 1$ and for every design when all incomes are equal, where $M$ and $\tilde{V}$ vanish together. The loss per unit of redistribution rises with the size of the system, through $\tau_t$, and since $\ln f$ is linear in $\tau_t$ the marginal contribution is worth $1 + \ln f$ of its revenue to a retiree whatever the variant (appendix \ref{app:esc:equilibrium}). And the marginal cost of the first unit of redistribution is
\begin{align*}
    \frac{\partial \ln f}{\partial \theta_t}\Big|_{\theta_t = 1} = \lambda_1\tau_t M,
\end{align*}
zero under the quadratic cost, under which no electorate chooses the Bismarckian corner, and positive under the two with a linear term, which is what lets an electorate choose it. Scaling both components alike is a choice. A cost on the flat component alone delivers the same endpoints and differs in the interior, but it loses the separate identification of $\theta$ and the cost parameters (appendix \ref{app:esc:equilibrium}). A cost on the design itself rather than on the transfer it performs, $f(\theta) = \phi + (1-\phi)\theta^{p}$, stays in place when a compressed income distribution removes the redistributive stakes; the \oa{esc-scale} reports it.

\smalltitle{The Bismarckian corner.} With the design chosen one period in advance under log preferences the choice maximizes $\mathcal{B}_t(\theta_{t+1})$ alone (proposition \ref{prop:esc:separability}), and at $\theta_{t+1} = 1$ the cost enters its slope through one number, the marginal share saved by the first unit of design, $\ell_{t+1} \equiv \lambda_1\tau_{t+1}M$, where $\tau_{t+1} = \mathcal{T}_{t+1}(1)$ is the tax the young anticipate at the Bismarckian design.
\begin{proposition}\label{prop:esc:bismarckCorner}
Assume log-GHH preferences, no informal households, a time-invariant distribution of types, and let the design be chosen one period in advance under the cost \eqref{eq:esc:fGeneral}. Write $\psi_{t+1} \equiv \frac{\frac{1-\alpha}{\alpha}\tau_{t+1}}{1+\frac{1-\alpha}{\alpha}\tau_{t+1}}$, $b \equiv \frac{\beta}{1+\beta}$, $\Lambda_{t+1} \equiv \frac{b\psi_{t+1}}{1+\xi-b\psi_{t+1}}$, $\bar{\mu} \equiv \sum_i\gamma_i\mu_i$, $S_{\mu} \equiv \sum_i\gamma_i\mu_i/y_i$, and let $\mathcal{T}'_{t+1}$ be the slope of the equilibrium tax function in the inherited design at $\theta_{t+1} = 1$. Then
\begin{align}\label{eq:esc:cornerFOC}
    \frac{\partial \mathcal{B}_t}{\partial \theta_{t+1}}\Big|_{\theta_{t+1} = 1}
    = \bar{\mu}\,c_{H}\,H_{t+1}
    + \bar{\mu}\nu_t\beta\,\frac{1-\alpha}{1+\alpha\xi}\,\psi_{t+1}\Big(b + \ell_{t+1} + \frac{\mathcal{T}'_{t+1}}{\tau_{t+1}}\Big)
    - \bar{\mu}\nu_t\beta\,\frac{(1-\alpha)\xi}{1+\alpha\xi}\,\frac{\mathcal{T}'_{t+1}}{1-\tau_{t+1}}
    - \nu_t\beta\,\psi_{t+1}S_{\mu},
\end{align}
with $H_{t+1} = \frac{\xi}{1+\alpha\xi}\Lambda_{t+1}\big[1 - b\psi_{t+1} + (1-\psi_{t+1})\big(\ell_{t+1} + \mathcal{T}'_{t+1}/\tau_{t+1}\big)\big]$ and $c_{H} = \omega(1-\alpha) + \nu_t\frac{1+\xi}{\xi}\frac{1+\alpha\xi+\alpha\beta(1+\xi)}{1+\alpha\xi}$. At a given $\mathcal{T}'_{t+1}$ the slope is affine and increasing in $\ell_{t+1}$, so the Bismarckian corner is a local maximum of $\mathcal{B}_t$ if and only if $\lambda_1 \geq \underline{\lambda}_1$, with $\underline{\lambda}_1\,\tau_{t+1}M$ the value of $\ell_{t+1}$ at which \eqref{eq:esc:cornerFOC} vanishes; $\lambda_2$ does not enter. As $\tau_{t+1} \to 0$ at a given $\mathcal{T}'_{t+1}/\tau_{t+1}$ every term of \eqref{eq:esc:cornerFOC} is of order $\tau_{t+1}$, so $\underline{\lambda}_1\tau_{t+1}M$ is independent of the size of the system to first order and $\underline{\lambda}_1$ is proportional to $1/\tau_{t+1}$.
\end{proposition}

\smalltitle{Proof of proposition \ref{prop:esc:bismarckCorner}.} By \eqref{eq:esc:leadFOC} the slope of $\mathcal{B}_t$ is $\sum_i\gamma_i\mu_i[\omega(1-\alpha)\,d\ln\Theta_{h,t} + \nu_t((1+\beta)\,d\ln\tilde{c}_{1,t}^i + \beta\,d\ln R_{t+1})]/d\theta_{t+1}$, each derivative carrying $\tau_{t+1} = \mathcal{T}_{t+1}(\theta_{t+1})$. At $\theta_{t+1} = 1$, $f = 1$, $A = 1$, $B = 0$ and $\partial f/\partial\tau_{t+1} = f\ln f/\tau_{t+1} = 0$, so by \eqref{eq:esc:fGeneral} $dA/d\theta_{t+1} = 1 + \ell_{t+1}$ and $dB/d\theta_{t+1} = -1$, whatever $\lambda_2$. From \eqref{eq:esc:auxiliary:Gammas}, $\Gamma_{s,t} = \Gamma_h b/\big((1+\xi)[1 + \frac{1-\alpha}{\alpha}\tau_{t+1}(A + \frac{B}{1+\beta})]\big)$, so $d\ln\Gamma_{s,t}/d\theta_{t+1} = -\psi_{t+1}(b + \ell_{t+1} + \mathcal{T}'_{t+1}/\tau_{t+1})$; from \eqref{eq:esc:auxiliary:Thetah}, in which $\frac{1-\alpha}{\alpha}A\tau_{t+1}\Gamma_{s,t}/\Gamma_h = b\psi_{t+1}/(1+\xi)$ at the corner, $d\ln\Theta_{h,t}/d\theta_{t+1} = \frac{\xi}{1+\alpha\xi}\Lambda_{t+1}\,d\ln(A\tau_{t+1}\Gamma_{s,t})/d\theta_{t+1} = H_{t+1}$. The young's consumption is $\tilde{c}_{1,t}^i = \frac{(h_t/\Gamma_h)^{(1+\xi)/\xi}}{1+\beta}\big[\frac{y_i\Gamma_h}{1+\xi} + \frac{1-\alpha}{\alpha}\tau_{t+1}B\,\Gamma_{s,t}\big]$ (appendix \ref{app:EE:CRRA} with $s_t$ eliminated by \eqref{eq:s}), whose bracket at the corner is $y_i\Gamma_h/(1+\xi)$, so $d\ln\tilde{c}_{1,t}^i/d\theta_{t+1} = \frac{1+\xi}{\xi}H_{t+1} - b\psi_{t+1}/y_i$: the only type-specific term is the loss of the flat benefit, a larger share of a poorer type's surplus. The return satisfies $\ln R_{t+1} = \text{const} - \frac{1-\alpha}{1+\alpha\xi}\ln(s_t/\nu_{t+1}) + (1-\alpha)\ln\Theta_{h,t+1}$ with $\ln s_t = \frac{1+\xi}{\xi}\ln h_t + \ln\Gamma_{s,t}$, and $\Theta_{h,t+1}$ depends on $\theta_{t+1}$ only through $(1-\tau_{t+1})^{\xi/(1+\alpha\xi)}$, the continuation design being state-free (proposition \ref{prop:esc:separability}); hence $d\ln R_{t+1}/d\theta_{t+1} = -\frac{1-\alpha}{1+\alpha\xi}[\frac{1+\xi}{\xi}H_{t+1} - \psi_{t+1}(b + \ell_{t+1} + \mathcal{T}'_{t+1}/\tau_{t+1})] - \frac{(1-\alpha)\xi}{1+\alpha\xi}\mathcal{T}'_{t+1}/(1-\tau_{t+1})$. Retirees see $\theta_{t+1}$ only through $(1-\alpha)\ln h_t$. Summing with the weights of \eqref{eq:LOG:PolObj} gives \eqref{eq:esc:cornerFOC}; $\ell_{t+1}$ enters linearly through $H_{t+1}$ and the savings term, with the coefficient $\bar{\mu}[c_H\frac{\xi}{1+\alpha\xi}\Lambda_{t+1}(1-\psi_{t+1}) + \nu_t\beta\frac{1-\alpha}{1+\alpha\xi}\psi_{t+1}] > 0$. As $\tau_{t+1} \to 0$, $\psi_{t+1}$ and $\Lambda_{t+1}$ are of order $\tau_{t+1}$ and so is every term, which gives the last claim.

The tax response is itself a function of the cost: at the corner the retirees' term of the tax condition \eqref{eq:esc:E2} has slope $\frac{\omega\frac{1-\alpha}{\alpha}}{(1+\frac{1-\alpha}{\alpha}\tau_{t+1})^2}\big[-(1+\frac{\frac{1-\alpha}{\alpha}\tau_{t+1}}{1+\beta})(S_{\mu}-\bar{\mu}) + \ell_{t+1}(2+\frac{1-\alpha}{\alpha}\tau_{t+1})\bar{\mu}\big]$ in the design, the cost entering once through $A$ and once through the factor $1 + \ln f$, so $\mathcal{T}'_{t+1}$ rises linearly with $\ell_{t+1}$ from the negative slope of proposition \ref{prop:LOG:PEE} and is positive at the threshold: a more Bismarckian design then raises the tax, since the dissipation it saves raises what the marginal contribution is worth to retirees. The threshold of section \ref{sec:esc:calibration} solves \eqref{eq:esc:cornerFOC} with this response. With equal propensities to vote $S_{\mu} = \bar{\mu}(1+\tilde{V})$, so the loss of the flat benefit splits into a part common to all types and a redistributive part proportional to $\tilde{V}$; the common part, net of the gains in hours and returns, is the larger obstacle at the calibrated economies and does not scale with the dispersion. The threshold is this obstacle in units of the first unit's saving, $\underline{\lambda}_1 = \bar{\ell}/(\tau_{t+1}M)$: a larger system lowers it in proportion, and a compressed income distribution raises it, by less than the fall in $\tilde{V}$ would suggest, since the amount carried, $M$, falls more slowly than the Harberger dispersion.
```

For section 7.1, after the paragraph that reads the cost:

```latex
The quadratic loss has a property that the data reject: the marginal cost of the first unit of redistribution is zero, so no electorate chooses the Bismarckian corner, which is France's observed design. We therefore let the leak have a constant part as well, a share of every unit the flat component carries, which is $\tau_t(1-\theta_t)M$ per unit of revenue with $M$ the mean absolute deviation of relative incomes, and compare three variants of the cost: the quadratic one, a purely linear one, and the two together, written as a scale $\lambda$ and a shape $\kappa$, $1 - f \approx \lambda\tau_t(1-\theta_t)[\kappa M + \tfrac{1}{2}\tilde{V}(1-\theta_t)]$ (appendix \ref{app:esc:cost}). The linear part prices the first unit of redistribution at $\lambda\kappa\tau_t M$, and an electorate chooses the Bismarckian corner once this exceeds a threshold that falls with the size of the system and rises with a flatter voting profile and a more compressed income distribution (proposition \ref{prop:esc:bismarckCorner}). The variants share the solution of appendix \ref{app:esc:equilibrium}, the identification of $\theta^{\ast}$ and the factor by which a larger system is worth less to a retiree at the margin; they differ in how the marginal cost falls as the design becomes more earnings-related, and so in how far a shock moves the chosen design.
```
