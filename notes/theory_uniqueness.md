# Theory note T2: uniqueness of the log-HtM tax, and appendix C (A6, #8, #9, #11, A1)

Package T2 of `notes/plan_reviewResponse.md` (W16, branch `review-2026-10`), written 2026-10-23 by the
model-theorist agent. Inputs: the plan's T2 paragraph; `notes/paper_reviewResponse.md` (A1, A6, comments
6, 8, 9, 11, "Found while checking"); the review `coarse-output/coarse_review_22102026.md` (O1, O3,
comments 6, 8, 9, 11); the paper's sections 3, 4 and 7 and appendices A–D; the technical note's
`model_PEE.tex`, `num_robustroot.tex` (the equilibrium test) and `writing/US/model_esc.tex`;
`python/informalAnalytical/base.py`, `policy.py`, `python/US/base.py`, `policyESC.py`, `modelESC.py`;
Gonzalez-Eiras and Niepelt (2008), `pdfs/GonzalezNiepelt2008.pdf` (text extracted with `pdftotext`).
Notation is the paper's (appendix B.1 and appendix C). Equations are numbered (1), (2), ... within this
note. Nothing here is a first-order approximation unless the text says so; every result below is exact.

For the writers of W2, W3, W7 and W8: the proposed wording is in section 7 at the end. For the
computing packages: the implications for C0, C4 and C5 are in section 8.

## Overturned

One working assumption of the brief is refined, none is overturned outright.

- **The Bismarckian corner (#9).** The paper's sentence "under a purely quadratic loss no electorate
  chooses the Bismarckian corner" is false as written, as the reviewer says. The agreed replacement, "a
  purely quadratic loss can never by itself take an electorate to the Bismarckian corner", is right in
  one precise sense and wrong in another, and the wording has to say which. Right: the slope of the
  design objective at $\theta = 1$ is the same number for every value of the cost parameter, so the cost
  cannot create a local maximum at the Bismarckian corner (section 5, proposition 5). Wrong, if read
  globally: the cost lowers the objective at every design below one and leaves it unchanged at the
  corner, so where an electorate already has a local maximum at $\theta = 1$ without the cost, a large
  enough cost parameter can make that corner the global choice. The confirmation run shows both at the
  U.S. calibration: the slope at $\theta_{t+1} = 1$ is $-0.1431$ at $\lambda = 0$, $8.643$ and
  $18.267$ alike, while $\mathcal{W}_t(1) - \mathcal{W}_t(0.7)$ goes from $-0.040$ to $+0.011$ as
  $\lambda$ rises to $18.267$. France's result should be read through the local statement: if France's
  slope at the corner is negative without the cost, no finite $\lambda$ reproduces $\theta = 1$, which is
  what appendix G.1 finds; the reason is not that the cost "does not price the first unit of
  redistribution" in general. The sign of France's slope at $\theta = 1$ at $\lambda = 0$ is a one-line
  check with the French model (`ESC.objective`) that C1 or C5 can add.

Two findings go beyond the brief without contradicting it. The uniqueness theorem (section 2) extends to
the economy of section 7 with the cost, at the inherited design, by a two-region argument; and (C.9)'s
monotonicity in the tax and in the dispersion of relative incomes is not merely "plausible at an
interior tax" (reviewer, #11) but necessary: an interior equilibrium tax has $1 + \ln f > 0$ (section 4,
lemma 4).

## 1. The objects

The economy is that of proposition 2 (appendix B.1): log-GHH preferences, $J$ formal types with
relative labor incomes $y_i \equiv \eta_i^{1+\xi}/(X_i^{\xi}\Gamma_h)$, $\sum_{i>0}\gamma_i y_i = 1$,
and hand-to-mouth informal households of mass $\gamma_0 \geq 0$ with the old-age endowment of appendix
A. Write

$$a \equiv \frac{1-\alpha}{\alpha}\,\frac{1}{1+\gamma_0\epsilon}, \qquad
p_i \equiv 1+\theta_t\left(y_i-1\right), \qquad x_i \equiv \frac{s_{t-1,i}}{s_{t-1}}, \tag{1}$$

so that $p_i$ is the benefit of a formal retiree of type $i$ relative to the mean formal benefit and $x_i$
the inherited savings share. Appendix B.1 writes the first order condition for the tax at $t$ as

$$\mathcal{F}_t(\tau_t;\,x) \equiv \omega\Big[\gamma_0\mu_0\mathcal{E}^0_{2,t} + \sum_{i>0}\gamma_i\mu_i\mathcal{E}^i_{2,t}\Big]
 + \nu_t\Big[\gamma_0\mu_0\mathcal{E}^0_{1,t} + \sum_{i>0}\gamma_i\mu_i\mathcal{E}^i_{1,t}\Big] \leq 0, \tag{2}$$

with equality at an interior tax, where, from (B.1)–(B.4) and the code (`base.dv2i_dτ_LOG`,
`dv1i_dτ_LOG`, `dv10_dτ_LOG`, `dlnc20_dτ`),

$$\mathcal{E}^i_{2,t} = -\frac{(1-\alpha)\xi}{(1+\alpha\xi)(1-\tau_t)} + \frac{a\,p_i}{x_i + a\,\tau_t\,p_i}, \tag{3}$$

$$\mathcal{E}^i_{1,t} = -\frac{1+\xi}{(1+\alpha\xi)(1-\tau_t)}\left(1+\beta\frac{\alpha(1+\xi)}{1+\alpha\xi}\right), \qquad
\mathcal{E}^0_{1,t} = -\frac{\beta}{1-\tau_t}\frac{\alpha(1+\xi)^2}{(1+\alpha\xi)^2}, \tag{4}$$

$$\mathcal{E}^0_{2,t} = \frac{\partial}{\partial\tau_t}\ln\big(C_s + b^0_t(\tau_t)\big), \qquad
b^0_t(\tau_t) = C_u\,\tau_t\,(1-\tau_t)^{m}, \qquad m \equiv \frac{\xi(1-\alpha)}{1+\alpha\xi}. \tag{5}$$

In (4) the young's formal term carries the code's factor $1+\beta\alpha(1+\xi)/(1+\alpha\xi)$ rather than
the printed $(1+\beta)$ (T1/W3's correction; nothing below depends on which, since both are positive
constants). In (5), $C_s > 0$ is the endowment term of $\tilde{c}^0_{2,t}$ and $C_u > 0$ collects
$(1-\alpha)\nu_t\epsilon/(1+\gamma_0\epsilon)$ and the factor of $\Theta_{h,t}^{1-\alpha}$ that does not
depend on $\tau_t$; both are evaluated at the common power of $s_{t-1}/\nu_t$, which cancels from the
log-derivative. The form (5) uses $\Theta_{h,t} \propto (1-\tau_t)^{\xi/(1+\alpha\xi)}$, the product
structure of the labor supply function `eq:h` in appendix A, whose other factor depends on
$(\tau_{t+1},\theta_{t+1})$ and not on $\tau_t$.

**Consistent shares.** The shares in (3) are predetermined at $t$, but in a politico-economic
equilibrium the generation that holds them anticipated the tax and the design that apply to its
benefits. By (13) (part iii of proposition 1, with $B_t = \beta$),

$$x_i(\tau_t) = y_i + a\,\tau_t\,(1-\theta_t)\,\frac{y_i-1}{1+\beta}. \tag{6}$$

The equilibrium condition of section 4 and of the technical note (`num_robustroot.tex`, eq.
consistentFOC) is the zero of

$$z_t(\tau) \equiv \mathcal{F}_t\big(\tau;\,x(\tau)\big), \tag{7}$$

the first order condition evaluated at the shares consistent with the tax at which it is evaluated.
$z_t$ is not the derivative of any one function of $\tau$: the equilibrium test of the technical note
(eq. equilibriumTest) therefore asks, for each candidate $c$ (every zero of $z_t$ and the two corners),
whether $c$ maximizes the objective at its own frozen shares, $\mathcal{W}_t(\cdot\,;x(c))$. The
reviewer's worry (O3) is exactly that this fixed point between the tax and the shares can have several
solutions: a higher anticipated tax lowers the savings of poor retirees, which raises their support for
the tax.

## 2. Uniqueness of the log-HtM tax (A6)

### 2.1 Three lemmas

**Lemma 1 (the formal retirees' term at consistent shares).** For every $\theta_t \in [0,1]$, $\beta >
0$, $a > 0$ and $y_i > 0$,

$$x_i(\tau) + a\,\tau\,p_i = y_i + a\,\tau\,q_i, \qquad q_i \equiv \theta_t\,y_i + (1-\theta_t)\,\frac{\beta + y_i}{1+\beta} > 0, \tag{8}$$

so the benefit term of (3) at consistent shares, $G_i(\tau) \equiv a\,p_i/(y_i + a\,\tau\,q_i)$, is
positive, finite and strictly decreasing on $[0,1)$, and every formal retiree's consumption is positive at
every $\tau \in [0,1)$.

*Proof.* Adding (6) to $a\tau p_i$ and collecting the coefficient of $a\tau$:
$p_i + (1-\theta_t)(y_i-1)/(1+\beta) = \theta_t y_i + (1-\theta_t)\big[1 + (y_i-1)/(1+\beta)\big]
= \theta_t y_i + (1-\theta_t)(\beta+y_i)/(1+\beta)$, which is (8). Both summands of $q_i$ are
non-negative and not both zero when $y_i > 0$, so $q_i > 0$; $p_i = \theta_t y_i + 1-\theta_t > 0$ for the
same reason. The denominator $y_i + a\tau q_i$ is positive and strictly increasing in $\tau$, the numerator
is a positive constant, so $G_i$ is positive and strictly decreasing. By (C.2) with $\gamma_0 \geq 0$,
$c^i_{2,t}$ is the denominator times a positive factor, hence positive. $\square$

The economics: a higher anticipated tax does lower the savings of a type below mean income, by the
fraction $1/(1+\beta)$ of the flat part of its pension, which is what the reviewer's self-fulfilling
channel relies on. But the pension's contribution to its retirement consumption, $a\tau p_i$, grows by
more than its savings share falls, since $q_i > 0$, so the pension's share of consumption rises less than
proportionally with the tax and the marginal support $\sigma^i_t/\tau_t$ (appendix B.1's reading of
$\mathcal{E}^i_{2,t}$) still falls. Note that the share $x_i(\tau)$ itself may turn negative for a poor
type at a high anticipated tax (borrowing against the pension); the lemma does not need $x_i > 0$.

**Lemma 2 (the informal retirees' term).** If $m \leq 1$, that is $\xi(1-2\alpha) \leq 1$, then
$\mathcal{E}^0_{2,t}$ in (5) is strictly decreasing on $[0,1)$.

*Proof.* With $b \equiv b^0_t$, $\mathcal{E}^0_{2,t} = b'/(C_s+b)$ and its derivative is
$\big[b''(C_s+b) - (b')^2\big]/(C_s+b)^2$, negative wherever $b'' < 0$. Differentiating
$b = C_u\tau(1-\tau)^m$ twice, $b'' = -C_u\,m\,(1-\tau)^{m-2}\big[2 - (1+m)\tau\big]$, negative for
$\tau < 2/(1+m)$, which contains $[0,1)$ when $m \leq 1$. $\square$

The condition $\xi(1-2\alpha) \leq 1$ holds for any $\alpha \geq 1/2$ and, at $\alpha = 0.3$ or $0.35$,
for any Frisch elasticity below $2.5$ or $3.3$; the calibrations use $\xi = 0.3$. It is needed only when
$\gamma_0 > 0$ (the paper's section 7 has $\gamma_0 = 0$). Without it, $\mathcal{E}^0_{2,t}$ could rise
on $(2/(1+m),1)$; the random check of section 6 shows this does happen at $m = 2.5$.

**Lemma 3 (the young).** Each term in (4) is $-\kappa/(1-\tau_t)$ with a positive constant $\kappa$, hence
strictly decreasing on $[0,1)$ and unbounded below as $\tau_t \to 1$; so is the first term of (3).

### 2.2 The theorem

**Proposition 1 (uniqueness under log-GHH preferences with hand-to-mouth informal households).** Assume
(i) log-GHH preferences; (ii) informal households are hand-to-mouth, $\gamma_0 \geq 0$, with the old-age
endowment of appendix A; (iii) $y_i > 0$ for every formal type, $\mu_j > 0$, $\omega > 0$, $\nu_t > 0$,
and the design $\theta_t \in [0,1]$ and $\epsilon \geq 0$ that apply to the benefits paid at $t$ are
given and were anticipated by the generation that is old at $t$; (iv) if $\gamma_0 > 0$,
$\xi(1-2\alpha) \leq 1$ and the continuation $(\tau_{t+1},\theta_{t+1})$ is given, as it is in the
backward induction of a finite horizon. Then:

1. $z_t$ is continuous and strictly decreasing on $[0,1)$, finite at $\tau = 0$ and unbounded below as
   $\tau \to 1$.
2. The politico-economic equilibrium tax at $t$ exists and is unique: $\tau^{\ast}_t = 0$ if
   $z_t(0) \leq 0$, and otherwise the unique zero of $z_t$ in $(0,1)$. The corner $\tau_t \to 1$ is never
   an equilibrium.
3. Exactly one candidate passes the equilibrium test: at the shares $x(\tau^{\ast}_t)$ the objective
   $\mathcal{W}_t(\cdot\,;x(\tau^{\ast}_t))$ is strictly concave on the set of taxes at which every
   retiree's consumption is positive and attains its maximum at $\tau^{\ast}_t$; every other candidate
   fails its own test.
4. Hence the finite-horizon politico-economic equilibrium is unique for every horizon $T$, by backward
   induction from $T$. When $\gamma_0 = 0$, $z_t$ does not depend on the continuation at all, so the tax
   at every date is the same in every Markov equilibrium of definition 1, whatever the horizon.

*Proof.* Step 1. Substitute (6) into (3). By lemma 1 the formal retirees' terms at consistent shares are
$-(1-\alpha)\xi/((1+\alpha\xi)(1-\tau)) + G_i(\tau)$, each strictly decreasing (lemma 3 for the first
piece, lemma 1 for the second). The informal retirees' term (5) does not involve the formal shares and is
strictly decreasing by lemma 2; the young's terms are strictly decreasing by lemma 3. All weights
$\omega\gamma_j\mu_j$ and $\nu_t\gamma_j\mu_j$ are positive, so $z_t$, a positive combination, is
strictly decreasing. At $\tau = 0$ every term is finite ($G_i(0) = ap_i/y_i$, $\mathcal{E}^0_{2,t}(0) =
C_u/C_s$). As $\tau \to 1$ the young's terms go to $-\infty$ while $G_i$ stays bounded, so $z_t \to
-\infty$. Continuity is immediate.

Step 2. A strictly decreasing continuous function on $[0,1)$ that is finite at $0$ and unbounded below
has at most one zero, and has one in $(0,1)$ exactly when $z_t(0) > 0$. The first order condition (2)
with the Kuhn–Tucker sign holds at $\tau = 0$ iff $z_t(0) \leq 0$, and at an interior tax iff $z_t = 0$;
a corner at the upper end would need $z_t \geq 0$ there, which $z_t \to -\infty$ rules out.

Step 3. Fix any feasible vector of shares $x$ (frozen). At fixed $x_i$ the benefit term $a p_i/(x_i +
a\tau p_i)$ is strictly decreasing in $\tau$ on the set where its denominator is positive, and the other
terms of (2) do not involve $x$; so $\partial\mathcal{W}_t(\tau;x)/\partial\tau = \mathcal{F}_t(\tau;x)$
is strictly decreasing on the feasible set, and $\mathcal{W}_t(\cdot\,;x)$ is strictly concave there.
Take $x = x(\tau^{\ast}_t)$. If $\tau^{\ast}_t$ is interior, $\mathcal{F}_t(\tau^{\ast}_t;x(\tau^{\ast}_t))
= z_t(\tau^{\ast}_t) = 0$ is the unique stationary point of a strictly concave function, so
$\tau^{\ast}_t$ is its global maximizer and passes. If $\tau^{\ast}_t = 0$, $\mathcal{F}_t(0;x(0)) =
z_t(0) \leq 0$ and the objective at $x(0)$ is decreasing throughout, so the corner passes. The feasible set
is an interval whose lower end, if above zero, is a tax at which some retiree's consumption vanishes and
$\mathcal{W}_t \to -\infty$, so it never contains the maximizer; by lemma 1 the whole of $[0,1)$ is
feasible at consistent shares. Any other candidate $c$ is a corner, since $z_t$ has no other zero: the
upper corner has $\mathcal{F}_t(c;x(c)) = z_t(c) < 0$, so its own objective is decreasing at $c$ and it
fails; the lower corner passes only if $z_t(0) \leq 0$, in which case it is $\tau^{\ast}_t$.

Step 4. At $t = T$ the terminal period of appendix D changes $\mathcal{E}^i_{1,T}$ to the $\beta = 0$
form of (4) and $\Theta_{h,T}$ to the terminal formula, which is still proportional to
$(1-\tau_T)^{\xi/(1+\alpha\xi)}$; lemmas 1–3 apply unchanged, so $\tau^{\ast}_T$ is unique. For $t < T$,
given the unique continuation, steps 1–3 give a unique $\tau^{\ast}_t$; induction on $t$ gives a unique
equilibrium path. The continuation enters $z_t$ only through the level of $\Theta_{h,t}$ in (5), the
informal retirees' term (the young's terms (4) contain no policy but $\tau_t$, and the first term of (3)
is free of $(\tau_{t+1},\theta_{t+1})$ by the product structure of `eq:h`); with $\gamma_0 = 0$ that term
has zero weight and $z_t$ depends on $(\tau_t,\theta_t)$ and the parameters of $t$ alone, so the tax
at each date is determined without reference to any other date. $\square$

**What the proposition does not say.** It is uniqueness of the equilibrium tax given the design; in
section 7 the design chosen at $t$ is a separate maximization, over a grid, which the proposition does
not address. It restricts attention to Markov equilibria (definition 1), as Gonzalez-Eiras and Niepelt
(2008) do; equilibria sustained by history-dependent strategies are outside the class. With $\gamma_0 >
0$ the finite-horizon equilibrium is unique for every $T$, and the infinite-horizon Markov equilibrium is
the limit of these, the same class in which Gonzalez-Eiras and Niepelt establish uniqueness (their p.
198: "the Markov perfect equilibrium we focus on is the unique equilibrium arising in the limit of the
finite-horizon economy"; their pp. 204–205 and proposition 2(i), by backward induction from a strictly
concave last-period problem). Their model has one household per cohort, so no distribution of savings and
no fixed point between the tax and the shares; the content of proposition 1 is that this fixed point,
which their argument does not meet, has a unique solution under log-GHH preferences with hand-to-mouth
informal households.

**A remark on shares formed under another anticipated policy.** Lemma 1 needs only that the
coefficient of $\tau$ in $x_i + a\tau p_i$ be positive. If the old formed their shares under a design or
a coverage parameter other than the one in force, as in an unanticipated reform, the coefficient is
$a p_i + a^{e}(1-\theta^{e}_t)(y_i-1)/(1+\beta)$ with the anticipated values superscripted $e$; for a type
below mean income it is positive whenever $a^{e}/a < (1+\beta)\,p_i/\big((1-\theta^{e}_t)(1-y_i)\big)$,
which holds by a wide margin at the Argentine values ($a^{e}/a \approx 1.15$ for the rise of $\epsilon$
from $0.21$ to $0.55$ with $\gamma_0 = 0.47$). This matters only for the hand-to-mouth check of footnote
16; the Argentine calibration itself has informal savers and is outside the proposition.

### 2.3 The economy of section 7: the tax condition with the cost

**Proposition 2 (uniqueness with the cost, at the inherited design).** Assume log-GHH preferences, no
informal households, the cost (16) with the proportional specification (C.5) and $\lambda \geq 0$, and
a design $\theta_t$ in force at $t$ that
the generation now old anticipated. Then conclusions 1–4 of proposition 1 hold for the tax condition of
appendix C.3, with $z_t$ strictly decreasing on the set where it can vanish.

*Proof.* Write $k \equiv \tfrac12\lambda\tilde{V}(1-\theta_t)^2 \geq 0$ and $u(\tau) \equiv \tau
f(\theta_t,\tau) = \tau e^{-k\tau}$, so that $u'(\tau) = e^{-k\tau}(1-k\tau) = f\,(1+\ln f)$ and
$u''(\tau) = -k\,e^{-k\tau}(2-k\tau)$. In (C.8) the benefit term is
$\frac{1-\alpha}{\alpha}f p_i(1+\ln f)/\big(x_i + \frac{1-\alpha}{\alpha}\tau f p_i\big)$, since
$A y_i + B = f p_i$; the consistent shares are (C.7c) at $t-1$ with the tax $\tau_t$ and the design
$\theta_t$, $x_i = y_i + \frac{1-\alpha}{\alpha}u(\tau)(1-\theta_t)(y_i-1)/(1+\beta)$. With $a =
(1-\alpha)/\alpha$ and $q_i$ as in (8),

$$G^{f}_i(\tau) = \frac{a\,p_i\,u'(\tau)}{y_i + a\,q_i\,u(\tau)}. \tag{9}$$

On $k\tau \leq 1$: $u' \geq 0$ and $u'' < 0$, so the derivative of (9),
$a p_i\big[u''(y_i + aq_iu) - aq_i(u')^2\big]/(\cdot)^2$, is negative and $G^f_i$ is strictly decreasing.
On $k\tau > 1$: $u' < 0$, so $G^f_i < 0$, and since every other term of $z_t$ is negative (lemma 3; the
first term of (C.8) is $-(1-\alpha)\xi/((1+\alpha\xi)(1-\tau))$ as before, and the young's term "contains
no policy but $\tau_t$", appendix C.3), $z_t < 0$ there. Hence $z_t$ is strictly decreasing on
$[0,\min(1,1/k))$, negative on $[1/k,1)$ if $1/k < 1$, and unbounded below as $\tau \to 1$: it has at
most one zero, and the conclusions of proposition 1 follow as before. For the equilibrium test, at
frozen $x_i$ the term $a p_i u'/(x_i + a p_i u)$ has derivative $a p_i[u''(x_i + ap_iu) -
ap_i(u')^2]/(\cdot)^2 < 0$ wherever $u'' \leq 0$, that is $k\tau \leq 2$, and is negative wherever
$k\tau > 1$; so $\mathcal{F}_t(\cdot\,;x)$ is positive left of its zero and negative right of it on the
feasible set, and $\mathcal{W}_t(\cdot\,;x)$ is single-peaked. Finally, $z_t$ sees $\theta_{t+1}$ and
$\tau_{t+1}$ nowhere (appendix C.3), so conclusion 4 holds in its $\gamma_0 = 0$ form: the tax function
$\mathcal{T}_t(\theta_t)$ of appendix C.3 is single-valued. $\square$

The two regions matter at the calibration: at $\rho = 0.5$, $\lambda = 18.267$ and a flat inherited
design, $k = 3.98$ and $u'$ changes sign at $\tau = 0.25$, so a one-region monotonicity claim would be
false there, while the equilibrium tax sits at $0.054$, inside the decreasing region.

### 2.4 What does not carry over

Both quantitative extensions break the proof in identifiable places, which is why the paper has to
check them numerically (candidate counts, C0 and C4).

**CRRA preferences (hand-to-mouth or no informal households).** (a) Every term of the condition is
multiplied by a marginal-utility weight, $(c^i_{2,t})^{1-1/\rho}$ for retirees and
$(\hat{c}^i_{1,t})^{1-1/\rho}$ for the young (appendix B.3), which depend on the state $s_{t-1}$ and on
$\tau_t$; the sign of their $\tau_t$-derivative is not fixed, so the retirees' weighted term need not
fall in $\tau_t$. (b) The consistent shares carry $B_t = \beta^{\rho}R_t^{\rho-1}$ in place of $\beta$
(eq. 13 with $B_t$), and $R_t$ moves with $\tau_t$ through $h_t$; the coefficient $q_i$ of (8) becomes a
function of $\tau_t$, and for types above mean income and $\rho > 1$ the product $\tau q_i(\tau)$ can
fall at high taxes. (c) The young's terms contain the continuation $\tau_{t+1}(s_t)$ and its slope
through $ds_t/d\tau_t$, a numerically differentiated object of no fixed sign, and $\mathcal{T}_t$ has
no closed form. Lemma 3 fails with (c), lemma 1 with (a) and (b).

**Informal savers under log-GHH (the Argentine model).** The state $s_{t-1,0}/s_{t-1}$ is forward
looking (appendix B.2). Two things break. First, the labor-supply term $(1-\alpha)\,d\ln h_t/d\tau_t$ of
every retiree now carries $d\tau_{t+1}/d\tau_t = (d\tau^{+1}_t/d(s_{t,0}/s_t))\cdot d(s_{t,0}/s_t)/d\tau_t$,
the slope of the continuation policy in the state times the response of the state (part v of
proposition 1 signs the second factor, nothing signs the first), and the young's terms of appendix B.2
carry the same object; its $\tau_t$-derivative is unsigned. Second, the consistent value of the
informal share depends on $\tau_t$ through $\Theta_{s,t-1}$, which falls with the anticipated tax
(appendix A.2), so the informal retirees' own benefit term still falls in $\tau_t$ (the analogue of
lemma 1 goes through for them), but the first break is enough. The paper's statement "the rest is
checked numerically" is therefore the right one for both extensions.

## 3. The threshold under CRRA preferences (#8)

**Proposition 3.** In the setting of proposition C.1 (the design chosen with the tax, no cost, no
informal households) but with CRRA-GHH preferences, $u(c) = (c^{1-1/\rho}-1)/(1-1/\rho)$ for retirees,

$$\frac{\partial\mathcal{W}_t}{\partial\theta_t} = \omega\,K^{1-1/\rho}\,\frac{1-\alpha}{\alpha}\,\tau_t\sum_i\gamma_i\left(y_i-1\right)\mu_i D_i^{-1/\rho}, \tag{10}$$

with $K$ the common factor and $D_i$ as in (C.2), $D_i = x_i + \frac{1-\alpha}{\alpha}\tau_t p_i$. The
derivative is negative at every design at which every retiree's consumption is positive whenever, for
every pair with $y_i > y_j$,

$$\frac{\mu_i}{\mu_j} < \left(\frac{D_i}{D_j}\right)^{1/\rho} = \left(\frac{c^i_{2,t}}{c^j_{2,t}}\right)^{1/\rho}, \tag{11}$$

and the Beveridgean corner follows as in proposition C.1. The log case is $\rho = 1$.

*Proof.* The design enters only $c^i_{2,t} = K D_i$ (proof of proposition C.1, which does not use the
form of utility), and $\partial c^i_{2,t}/\partial\theta_t = K\frac{1-\alpha}{\alpha}\tau_t(y_i-1)$. With
$u'(c) = c^{-1/\rho}$, $\partial\mathcal{W}_t/\partial\theta_t = \omega\sum_i\gamma_i\mu_i
(KD_i)^{-1/\rho}K\frac{1-\alpha}{\alpha}\tau_t(y_i-1)$, which is (10). Under CRRA preferences the
inherited shares keep the form (13) with a discount term $B_t$ common to all types ($R_t$ is common), so
$D_i$ is affine in $y_i$ with slope at least one (the second step of the proof of C.1) and $D_i > D_j > 0$
when $y_i > y_j$. Chebyshev's inequality with $a_i = y_i - 1$ (mean zero) and $b_i = \mu_i D_i^{-1/\rho}$
gives $\sum_i\gamma_i a_ib_i < 0$ when $b$ is strictly decreasing wherever $a$ is strictly increasing,
which is (11). $\square$

Compared with the log threshold $\mu_i/\mu_j < c^i_{2,t}/c^j_{2,t}$, (11) is stricter at $\rho = 2$ (the
square root of the consumption ratio) and looser at $\rho = 0.5$ (its square), as the reviewer says. Two
qualifications for C.1's text. The bound binds at the design where consumption is most compressed, the
Beveridgean corner, since $D_i/D_j$ rises with $\theta_t$ for $y_i > y_j$; and (11) is sufficient, the
exact condition being the sign of the sum in (10). At the 2020 U.S. calibration with the three CPS groups
the middle group has $y = 1.000$ and drops out of (10), so the exact condition is the pairwise one: at
$\theta_t = 0$ the retirees' consumption ratio of the top to the bottom group is $3.155$ (log shares,
$\tau = 0.144$, $\alpha = 0.3$, $\beta = 0.761$, $\theta^{\ast} = 0.738$), the bound (11) is $9.96$,
$3.16$ and $1.78$ at $\rho = 0.5$, $1$ and $2$, and the observed turnout ratio is $1.61$. The margin at
$\rho = 2$ is about ten percent of the weight ratio; C5 should compute it with the CRRA shares ($B_t$
in place of $\beta$) and at the A2 calibration, where the lower tax raises the consumption ratio and so
the bound.

## 4. The conditions behind (C.9) (#11)

(C.9) is $g \equiv \partial f/\partial\theta_{t+1} = f\lambda\tau_{t+1}\tilde{V}(1-\theta_{t+1})$, and
the sentence after it claims that $g$ rises with the flat share, the dispersion of relative incomes and
the size of the system. Write $x \equiv 1-\theta_{t+1}$ and $\tau \equiv \tau_{t+1}$, so $\ln g = \ln f +
\ln\lambda + \ln\tau + \ln\tilde{V} + \ln x$ with $\ln f = -\tfrac12\lambda\tau\tilde{V}x^2$. Then

$$\frac{\partial\ln g}{\partial\tau} = \frac{1+\ln f}{\tau}, \qquad
\frac{\partial\ln g}{\partial\tilde{V}} = \frac{1+\ln f}{\tilde{V}}, \qquad
\frac{\partial\ln g}{\partial x} = \frac{1+2\ln f}{x}. \tag{12}$$

(Direct: $\partial\ln f/\partial\tau = -\tfrac12\lambda\tilde{V}x^2 = \ln f/\tau$, likewise for
$\tilde{V}$, and $\partial\ln f/\partial x = -\lambda\tau\tilde{V}x = 2\ln f/x$.) So $g$ rises with the
size of the system and with the dispersion iff $\ln f > -1$, that is $1-f < 1-e^{-1} = 63\%$, and with
the flat share iff $\ln f > -\tfrac12$, that is $1-f < 39\%$. These are partial derivatives at a given
anticipated tax; the total effect of the design on $\tau_{t+1}f$ adds $f(1+\ln f)\mathcal{T}'_{t+1}$
(reviewer #16, outside this item).

**Lemma 4 (the first two conditions at an equilibrium tax).** At any interior equilibrium tax
$\tau = \mathcal{T}_{t+1}(\theta_{t+1})$, $1 + \ln f(\theta_{t+1},\tau) > 0$.

*Proof.* By proposition 2, $z_{t+1}(\tau) = 0$ requires the retirees' benefit term (9) to be positive,
since every other term is negative; its sign is that of $u'(\tau) = f(1+\ln f)$. $\square$

Hence $g$ rises in $\tau_{t+1}$ and in $\tilde{V}$ at every design whose anticipated tax is interior,
without further conditions. The third condition is strictly stronger and is where the sentence fails:
$\ln f(\theta_{t+1},\tau_{t+1}) > -\tfrac12$ iff

$$(1-\theta_{t+1})^2\,\lambda\,\tau_{t+1}\,\tilde{V} < 1 \quad\Longleftrightarrow\quad
\theta_{t+1} > \underline{\theta} \equiv 1 - \big(\lambda\tau_{t+1}\tilde{V}\big)^{-1/2}, \tag{13}$$

a restriction only when $\lambda\tau_{t+1}\tilde{V} > 1$. At table 4's values and the 2020 tax ($\tilde{V}
= 0.436$): $\lambda\tau\tilde{V} = 1.147$, $0.543$ and $0.108$ at $\rho = 0.5$, $1$ and $2$, so
$\underline{\theta} = 0.066$ at $\rho = 0.5$ and the condition holds on all of $[0,1]$ at $\rho = 1$ and
$2$. Near the calibrated design it holds at every elasticity with room to spare: at $\theta^{\ast} =
0.738$, $(1-\theta^{\ast})^2\lambda\tau\tilde{V} = 0.079$ at $\rho = 0.5$. It fails near flat designs at
low elasticities, and more so as the system grows: at the 2110 tax of $20.9\%$, $\underline{\theta} =
0.225$ at $\rho = 0.5$. This is the sense of "near the calibrated design": the claim is local because
$1-f(0)$ exceeds $39\%$ at $\rho = 0.5$ ($43.7\%$, table 4), so that for designs flatter than
$\underline{\theta}$ the marginal gain from a more Bismarckian design falls with the flat share, the loss
already being so large that a further unit of flatness dissipates less at the margin. After the A2
recalibration the numbers change (at $\tau = 0.103$ and the current $\lambda$ the product is $0.82$ at
$\rho = 0.5$, so the condition would hold everywhere), but $\lambda$ is recalibrated with the tax and
(13) has to be re-evaluated; the writers should quote the condition and the current threshold rather than
"holds".

## 5. The Bismarckian corner (#9) and the margins the cost stands for (#6)

### 5.1 The slope at the corner does not depend on the cost parameter

Let the design be chosen one period ahead as in section 7, under the cost (16) with the specification
(C.5), log-GHH preferences and
no informal households, and let $\mathcal{B}_t(\theta_{t+1};\lambda)$ be the part of the objective that
the design moves (proposition C.2). The tax the young anticipate is $\tau_{t+1} =
\mathcal{T}_{t+1}(\theta_{t+1};\lambda)$, single-valued by proposition 2.

**Proposition 5.** $\partial\mathcal{B}_t(\theta_{t+1};\lambda)/\partial\theta_{t+1}$ at $\theta_{t+1} =
1$ is the same for every $\lambda \geq 0$, and equals its value without the cost. The same holds for
the sequential timing: $\partial\mathcal{W}_t/\partial\theta_t$ in (C.1) at $\theta_t = 1$ does not
depend on $\lambda$.

*Proof.* By appendix C.3 the design enters the economic equilibrium only through $A\tau_{t+1}$ and
$B\tau_{t+1}$ (in $\Gamma_{s,t}$, $\Theta_{h,t}$, $s_{t,i}/s_t$ and $\tilde{c}^i_{1,t}$), through
$\tau_{t+1}$ itself in $\Theta_{h,t+1}$ (and so in $R_{t+1}$), and through the continuation
$(\theta_{t+2},\tau_{t+2})$, which under log preferences enters $\ln\Theta_{h,t+1}$ additively and does
not depend on $\theta_{t+1}$ (proposition C.2), so it shifts $\mathcal{B}_t$ by a constant. Along
$\theta_{t+1}$ with $\tau_{t+1} = \mathcal{T}_{t+1}(\theta_{t+1};\lambda)$,

$$\frac{d(A\tau_{t+1})}{d\theta_{t+1}} = \tau_{t+1}\Big(f + \theta_{t+1}\frac{\partial f}{\partial\theta_{t+1}}\Big) + f\theta_{t+1}\mathcal{T}'_{t+1}, \qquad
\frac{d(B\tau_{t+1})}{d\theta_{t+1}} = \tau_{t+1}\Big((1-\theta_{t+1})\frac{\partial f}{\partial\theta_{t+1}} - f\Big) + f(1-\theta_{t+1})\mathcal{T}'_{t+1}. \tag{14}$$

At $\theta_{t+1} = 1$: $f = 1$ and $\partial f/\partial\theta_{t+1} = f\lambda\tau_{t+1}\tilde{V}(1-\theta_{t+1})
= 0$ for every $\lambda$, so (14) reduces to $\tau_{t+1} + \mathcal{T}'_{t+1}(1)$ and $-\tau_{t+1}$, the
values without the cost, provided $\mathcal{T}_{t+1}(1;\lambda)$ and $\mathcal{T}'_{t+1}(1;\lambda)$ are
$\lambda$-free. They are: the tax condition at $\theta_{t+1} = 1$ has $A = 1$, $B = 0$ and $1 + \ln f =
1$, so it is the condition without the cost and $\mathcal{T}_{t+1}(1;\lambda) = \mathcal{T}_{t+1}(1;0)$;
and $\mathcal{T}'_{t+1} = -(\partial z_{t+1}/\partial\theta)/(\partial z_{t+1}/\partial\tau)$ at
$\theta = 1$ involves $\partial A/\partial\theta = 1$, $\partial B/\partial\theta = -1$,
$\partial(1+\ln f)/\partial\theta = \lambda\tau\tilde{V}(1-\theta) = 0$ and $\partial\ln f/\partial\tau =
-\tfrac12\lambda\tilde{V}(1-\theta)^2 = 0$, all $\lambda$-free at $\theta = 1$. The levels $A = 1$, $B = 0$
at $\theta_{t+1} = 1$ are $\lambda$-free too, so every factor of the chain rule for
$\partial\mathcal{B}_t/\partial\theta_{t+1}$ at $\theta_{t+1} = 1$ is the no-cost one. For the sequential
timing, (C.1) with the cost has numerator $A'y_i + B'$ with $A' = f + \theta_t\partial f/\partial\theta_t$,
$B' = (1-\theta_t)\partial f/\partial\theta_t - f$ (technical note, eq. esc:seqFOC), which at $\theta_t =
1$ are $1$ and $-1$, and denominator $x_i + \frac{1-\alpha}{\alpha}\tau_t(Ay_i + B) = x_i +
\frac{1-\alpha}{\alpha}\tau_t y_i$, both $\lambda$-free. $\square$

**Corollary (what the cost can and cannot do at the corner).** (i) If without the cost the design
objective is strictly decreasing at $\theta = 1$, so that the Bismarckian corner is not a local
maximum, it is not one for any finite $\lambda$, and no finite cost parameter makes the electorate choose
$\theta = 1$. (ii) If the electorate chooses $\theta = 1$ at some $\lambda$, then $\theta = 1$ is a local
maximum of the design objective without the cost: the corner has to come from the political forces of
appendix C.1, the forward-looking stake of (C.3), not from the cost. (iii) The cost does change the
global comparison: it leaves $\mathcal{B}_t(1)$ unchanged (up to the constant through the continuation)
and lowers the young's benefits at every $\theta_{t+1} < 1$, so where a local maximum at the corner
exists without the cost, a large enough $\lambda$ can make it the global choice. The U.S. run of
section 6 illustrates (i) and (iii): the slope at $\theta_{t+1} = 1$ is $-0.1431$ at $\lambda = 0$,
$8.643$ and $18.267$, the objective at $\theta_{t+1} = 1$ minus that at $0.7$ is $-0.040$, $-0.013$ and
$+0.011$. France (appendix G.1) reads as a case of (i): at the U.S. $\lambda$ it chooses $0.749$ and no
$\lambda$ reproduces $1.000$, which is what (i) predicts when the slope at the corner is negative without
the cost; the sign of that slope at $\lambda = 0$ should be checked on the French model, since (ii) and
(iii) leave open the other reading, a corner that is a local maximum at every $\lambda$ and is always
beaten by an interior design.

The reviewer's example, the CRRA once-and-for-all choice at high elasticities (appendix C.1), is a case
of (ii): the corner there is a local maximum without the cost. Proposition 5 is stated for log
preferences because it uses proposition C.2; under CRRA preferences the same algebra applies to the
partial derivative at $\theta_{t+1} = 1$ holding the continuation fixed, but the continuation then
depends on $\theta_{t+1}$ through the state, and the statement would need the slope of that
dependence at the corner, which is not $\lambda$-free in general.

### 5.2 Narrowing C.2 to participation and formality (#6)

The reviewer's point is a matter of which wedge a margin responds to, and it is correct. An intensive
reporting margin, how much of a given wage to report, responds to the marginal implicit tax of the flat
component, $\Pi_t\tau_t(1-\theta_t)$, which is common to all types and does not vanish when incomes are
equal (appendix C.2, "Which margin"). The Harberger loss of such a margin with elasticity
$\varepsilon_r$ and base $\sum_i\gamma_iy_i = 1$ is $\tfrac12\varepsilon_r\Pi_t^2\tau_t^2(1-\theta_t)^2$,
or $\tfrac12\varepsilon_r\Pi_t\tau_t(1-\theta_t)^2$ as a share of revenue: quadratic in the flat share
and linear in the size of the system, like (16), but independent of $\tilde{V}$. The paper's cost cannot
represent it: $f = 1$ whenever $\tilde{V} = 0$, at every design, while the incentive to under-report is
then at its strongest at $\theta_t = 0$. The cost (16) is a cost of the average wedge $t_i$ of
(C.1)'s implicit tax, which is the right object for extensive margins only: a worker deciding whether to
bring earnings into the system, or into the formal sector, compares the earnings at stake with what they
buy (Saez 2002; Kleven and Kreiner 2006). C.2's claim should therefore be participation and formality.
The Kumler, Verhoogen and Frías evidence is evidence that the tax component matters on a margin the model
does not price; it can stay in section 7.1 as motivation for the tax component, but C.2 should not list
reporting among the margins the cost stands for. Adding a term in $(1-\theta_t)^2$ that does not scale
with the dispersion would restore the reporting margin at the price of a second parameter; A8 decided
against a second term for now, so the narrowing is the action.

## 6. Numerical confirmation (not the argument)

Two scratch scripts, in the scratchpad and not in the repository:
`C:\Users\sxj477\AppData\Local\Temp\claude\C--Users-sxj477-Documents-GitHub-SSDclaude\f4320c70-85ef-4ec1-9a01-8a2eccd4abbe\scratchpad\check_algebra.py`
(pure algebra, random parameters) and `...\scratchpad\check_us.py` (the US test model of
`python/US/test.py` at the test calibration $\rho = 1$, $\beta = 0.761$, $\omega = 1.454$, imported
read-only; 6 seconds in all).

- Lemma 1: $G_i$ strictly decreasing in 2000 random economies (in 906 of them the consistent share of
  some type turned negative on $[0,1)$; monotone regardless). Proposition 2's two regions: decreasing on
  $k\tau < 1$ and negative on $k\tau > 1$ in 2000 random economies. Lemma 2: strictly decreasing in 2000
  draws with $m \leq 1$; at $m = 2.5$ a rise appears at $\tau = 0.83$, beyond $2/(1+m) = 0.57$.
- Proposition 1 on the US model: `solvePEE_LOG` records `nEqMax` 1, `nCandMax` 3 (the two corners and
  one crossing), no multiple states, no fallback; $z_{2020}$ on 4001 nodes is strictly decreasing with
  one sign change at $\tau = 0.144$ (the solved $0.1443$), and so is $z_t$ at every non-terminal period.
  The frozen objective at $x(\tau^{\ast})$ has one local maximum on the grid, at the node nearest
  $\tau^{\ast}$.
- Proposition 2 on `ModelESC` ('size', $\lambda = 18.267$ and $8.643$): counts as above; at a flat
  inherited design, $k = 3.98$ (resp. $1.88$), $z_{2020}$ is strictly decreasing on $k\tau < 1$, negative
  on $k\tau > 1$, with one zero at $\tau = 0.054$ (resp. $0.088$); at $\theta_t = 0.738$ one zero at
  $0.124$ (resp. $0.134$).
- Proposition 3: 5000 random draws satisfying (11) all give a negative sum; a two-type case with
  $\mu_H/\mu_L$ two percent above the bound flips the sign at $\rho = 0.5$, $1$ and $2$.
- (12) against central differences agrees to six digits; the thresholds of (13) are those quoted in
  section 4.
- Proposition 5: the one-sided $O(h^2)$ slope at $\theta_{t+1} = 1$ is $-0.143145$ at $\lambda = 0$,
  $8.643$ and $18.267$, with $\mathcal{T}_{2050}(1) = 0.17579$ at all three; $\mathcal{B}_t(1) -
  \mathcal{B}_t(0.7) = -0.0396$, $-0.0134$, $+0.0112$.
- A1 (section 7.5): the critical ratio reproduces the orchestrator's scratch numbers.

## 7. Proposed wording

### 7.1 Appendix B, after the proof of proposition 2 (for W3)

> \begin{proposition}\label{prop:PEE:unique}
> Under log-GHH preferences with hand-to-mouth informal households, the politico-economic equilibrium
> tax is unique at every date: given the design and, when $\gamma_0 > 0$, the continuation policy, the
> first order condition evaluated at the savings shares consistent with each candidate tax is strictly
> decreasing in the tax, so exactly one candidate passes the equilibrium test of section
> \ref{sec:numerical}. Without informal households the tax at each date does not depend on the
> continuation, so every Markov equilibrium has the same tax path whatever the horizon. With informal
> households the condition requires $\xi(1-2\alpha) \leq 1$, and uniqueness holds for every finite horizon.
> \end{proposition}
>
> \smalltitle{Proof of proposition \ref{prop:PEE:unique}.} With $a \equiv
> \frac{1-\alpha}{\alpha}\frac{1}{1+\gamma_0\epsilon}$ and $p_i \equiv 1+\theta_t(y_i-1)$, the benefit
> term of $\mathcal{E}^i_{2,t}$ is $a p_i/(s_{t-1,i}/s_{t-1} + a\tau_tp_i)$. The generation that is old
> at $t$ anticipated $\tau_t$ and $\theta_t$, so by part iii of proposition \ref{prop:LOG:EE} its share is
> $s_{t-1,i}/s_{t-1} = y_i + a\tau_t(1-\theta_t)(y_i-1)/(1+\beta)$, and the denominator at consistent
> shares is $y_i + a\tau_t q_i$ with $q_i \equiv \theta_ty_i + (1-\theta_t)(\beta+y_i)/(1+\beta) > 0$. The
> benefit term is therefore strictly decreasing in $\tau_t$: a higher anticipated tax lowers the savings
> of a retiree below mean income, but by less than it raises the pension, so the pension's share of
> consumption rises less than proportionally with the tax. The remaining terms of the condition are
> $-\kappa/(1-\tau_t)$ with positive constants $\kappa$, strictly decreasing and unbounded below as
> $\tau_t \to 1$, except the informal retirees' term $\partial\ln(\tilde{c}^0_{2,t})/\partial\tau_t$,
> which is the log-derivative of a constant plus $\tau_t(1-\tau_t)^{m}$, $m = \xi(1-\alpha)/(1+\alpha\xi)$,
> a strictly concave function on $[0,1)$ when $m \leq 1$; its log-derivative is then strictly decreasing.
> The condition at consistent shares is thus strictly decreasing, finite at $\tau_t = 0$ and unbounded
> below as $\tau_t \to 1$: it has one zero if it is positive at zero and none otherwise, and the equilibrium
> tax is that zero or the corner $\tau_t = 0$. At the shares consistent with this tax, the condition with
> the shares held fixed is also strictly decreasing wherever every retiree's consumption is positive, so
> the political objective is strictly concave there and the tax is its maximizer: it passes the test of
> section \ref{sec:numerical}, and no other candidate does, since the upper corner has a negative
> condition at its own shares and the lower corner passes only when it is the equilibrium. The condition
> sees the continuation only through the level of $\Theta_{h,t}$ in the informal retirees' term, so without
> informal households the tax at each date is determined by that date's parameters alone; with them,
> backward induction from the terminal period of appendix \ref{app:T}, whose condition has the same form,
> gives a unique equilibrium for every finite horizon. With the cost of section \ref{sec:esc} the benefit
> term becomes $a p_i u'(\tau_t)/(y_i + a q_i u(\tau_t))$ with $u(\tau_t) \equiv \tau_t f(\theta_t,\tau_t)$,
> which is strictly decreasing where $u' \geq 0$ and negative where $u' < 0$, and the argument goes
> through at the inherited design. $\square$
>
> The proposition does not extend to CRRA preferences, where every term carries a marginal-utility weight
> that depends on the state and the tax and the young's terms carry the slope of the continuation policy
> in the state, nor to informal savers, whose savings ratio is a forward-looking state through which the
> same slope enters; in both cases the solver records the number of candidates and of equilibria at every
> state and date (appendix \ref{app:T}).

### 7.2 Section 4 (for W2)

Replace "We report the finite-horizon solution, which approximates the Markov equilibrium in the limit
of finite-horizon economies, the class in which \textcite{mkvss08} establish uniqueness." by:

> We report the finite-horizon solution. Under log-GHH preferences with hand-to-mouth informal
> households it is unique at every horizon, and without informal households the tax at each date does
> not depend on the horizon at all (proposition \ref{prop:PEE:unique} in appendix \ref{app:PEE:LOG}): at
> the savings shares consistent with each candidate tax, the first order condition is strictly
> decreasing in the tax, so one candidate passes at every date. \textcite{mkvss08} establish the same
> property for a representative household within each cohort, in the limit of finite-horizon economies;
> their argument does not meet the fixed point between the tax and the distribution of savings that
> heterogeneity creates, and it covers neither informal savers nor the design choice. Under CRRA
> preferences or with informal savers we have no proof, and the solver records at every state and date the
> number of candidates and the number that pass (appendix \ref{app:T}).

Footnote 12: "Several passing candidates would be ranked by payoff, an assumption about equilibrium
selection. Under log-GHH preferences with hand-to-mouth informal households exactly one passes by
proposition \ref{prop:PEE:unique}; in every other solve the paper uses, exactly one passed at every state
and date (appendix \ref{app:T} reports the counts)." The second sentence's number is C0's and W8's.

### 7.3 Appendix D (for W8)

> Table \ref{...} reports, for every solve the paper uses, the largest number of candidates and of
> equilibria at any state and date. The candidates always include the two corners, so their count is
> at least two; the count of equilibria is the evidence. Under log-GHH preferences with hand-to-mouth
> or no informal households it is one by proposition \ref{prop:PEE:unique}, and a larger count there
> would be a numerical failure rather than a selection; under CRRA preferences and with informal savers
> the count is what the proposition does not deliver.

### 7.4 Appendix C.1 (for W7)

After "$\mu_i/\mu_j < c_{2,t}^i/c_{2,t}^j$ whenever $y_i > y_j$, and a design other than the Beveridgean
corner requires propensities to vote that, for some pair of types and at some design, rise at least as
fast as consumption.", replace the CRRA sentence by:

> The argument also holds under CRRA-GHH preferences at every intertemporal elasticity: the design still
> enters only the consumption of current retirees, whose marginal utility is $D_i^{-1/\rho}$ times a
> factor common to all types, and relative savings keep the form of \eqref{eq:si_s} with a discount term
> $B_t$ common to all types, so $\mu_iD_i^{-1/\rho}$ takes the place of $\mu_i/D_i$ and the threshold
> becomes $\mu_i/\mu_j < (c_{2,t}^i/c_{2,t}^j)^{1/\rho}$: stricter than the log one at $\rho = 2$, the
> square root of the consumption ratio, and looser at $\rho = 0.5$, its square. The bound binds at the
> Beveridgean corner, where retirees' consumption is most compressed.

Then A1's sentence and the critical ratio (C5's number):

> The propensity to vote $\mu_i$ is the political weight of type $i$ relative to its population share,
> of which turnout is the observable part; a responsiveness to policy that differed across types, the
> density of swing voters in probabilistic voting, would multiply $\mu_i$ in the political objective and
> enter the threshold in the same place, so it is not identified apart from turnout. At the 2020 U.S.
> calibration the corner survives until the weight of the high-income group is about $\todo{C5: ratio}$
> times that of the low-income one at $\rho = 1$, against an observed turnout ratio of $1.61$, and about
> $\todo{C5: ratio}$ times at $\rho = 2$.

### 7.5 Appendix C.2 (for W7)

"Which margin", last three sentences, replace by:

> The cost therefore stands for margins the model does not contain and on which the average wedge is
> the relevant one, participation and formality: a worker who decides whether to bring earnings into the
> system, or into the formal sector, compares the earnings at stake with what they buy, so the wedge that
> matters is the average tax on those earnings \parencite{Saez02a1,KlevenK06a1}. The reporting of
> earnings is a different margin. How much of a given wage to report responds to the marginal wedge of
> the flat component, $\Pi_t\tau_t(1-\theta_t)$, which is common to all types and does not vanish when
> incomes are equal, so a loss built on it would be quadratic in the flat share and linear in the size
> of the system but independent of the dispersion of relative incomes; the cost below does not contain
> it, and we read the evidence on reporting as evidence that the tax component matters rather than as a
> margin the cost prices.

"Specification", the sentence on the corner, replace "And the marginal cost of the first unit of
redistribution is zero, ... which is why France's design has no own cost (appendix
\ref{app:escResults:calibration})." by:

> And the marginal cost of the first unit of redistribution is zero: $\partial\ln f/\partial\theta_t =
> \lambda\tau_t\tilde{V}(1-\theta_t)$ vanishes at $\theta_t = 1$, and so does its derivative with respect
> to the tax, so the marginal value of the design at the Bismarckian corner, and the tax chosen there, are
> the same with and without the cost for every value of the cost parameter. A purely quadratic loss can
> therefore never by itself create a preference for the Bismarckian corner: an electorate reaches
> $\theta = 1$ only if the corner is a local maximum of its objective without the cost, as it is for the
> once-and-for-all choice under CRRA preferences at high intertemporal elasticities (appendix
> \ref{app:esc:corner}). The cost does lower the value of every other design, so where such a local
> maximum exists it can make the corner the global choice. No value of the parameter reproduces
> France's corner (appendix \ref{app:escResults:calibration}), so its design has to come from political
> forces the model does not contain.

Section 7.1's sentence "and the cost alone cannot take an electorate to a fully Bismarckian system" can
stay with "create a preference for" in place of "take an electorate to" (W6).

### 7.6 Appendix C.3, after (C.9) (for W7)

Replace "zero at $\theta_{t+1} = 1$ and rising with the flat share, the dispersion of incomes and the
size of the system the young anticipate." by:

> zero at $\theta_{t+1} = 1$. Since $\ln f = -\frac12\lambda\tau_{t+1}\tilde{V}(1-\theta_{t+1})^2$, the
> marginal gain rises with the size of the system and with the dispersion of relative incomes if and only
> if $\ln f > -1$, which holds at every design whose anticipated tax is interior, because the tax
> condition can only hold where $1 + \ln f > 0$; and it rises with the flat share if and only if
> $\ln f > -\frac12$, that is $(1-\theta_{t+1})^2\lambda\tau_{t+1}\tilde{V} < 1$. The second condition
> holds near the calibrated design at every intertemporal elasticity, but at $\rho = 0.5$, where a flat
> benefit loses $\todo{C1: 1-f(0) at rho=0.5}$ of revenue, it fails for designs below
> $\todo{C1: 1-(lambda tau Vtilde)^(-1/2) at rho=0.5, 2020}$: there the loss is already so large that a
> further unit of flatness dissipates less at the margin.

(At the current numbers: $43.7\%$ and $\theta_{t+1} < 0.066$ at the 2020 tax.)

## 8. Implications for the computing packages

- **C0 (candidate counts).** Under log preferences with hand-to-mouth or no informal households
  (Argentina's hand-to-mouth check, the whole U.S., UK and French log block, the log design paths), the
  theorem predicts `nEq` $= 1$ at every date; a recorded `nEq` $> 1$ or a fallback there is a bug in
  the grid or the test, not an equilibrium selection. `nCand` is at least 2 (the corners) and is 3 on the
  U.S. path; the tables should report the equilibria, with the candidates beside them and a note that the
  corners are always candidates.
- **C4 (horizon).** Under log preferences with $\gamma_0 = 0$ the tax at every date is exactly
  horizon-independent (conclusion 4), and so is the design chosen at every date except $T-1$, whose
  continuation is the terminal period (proposition 5's additivity argument: the choice at $t$ sees
  $(\theta_{t+2},\tau_{t+2})$ only through an additive constant). The U.S. log rows of the horizon table
  should therefore agree to solver tolerance for every $T$ two or more periods beyond the reading date;
  anything else is a code problem. The table carries information only for CRRA and for Argentina's
  informal savers, which is where to spend the runs.
- **C5 (A1's critical ratio).** Use the exact condition, the sign of
  $\sum_i\gamma_i(y_i-1)\mu_iD_i^{-1/\rho}$ over $\theta_t \in [0,1]$, with the weights $\mu_i = y_i^{k}$
  and the first $k$ at which it turns non-negative; with the three CPS groups the middle one has $y = 1$
  and drops out, so the number coincides with the pairwise bound at $\theta_t = 0$. At the current
  calibration (log shares): the consumption ratio at $\theta_t = 0$ is $3.155$, the critical weight
  ratio $3.16$ at $\rho = 1$ (the scratch value $3.22$ came from a coarser $k$ grid), $1.78$ at $\rho = 2$
  and $9.96$ at $\rho = 0.5$, against an observed $1.61$. The $\rho = 2$ margin is thin, so compute it
  with the CRRA shares ($B_t$ in place of $\beta$) and on the A2 calibration, where the lower tax raises
  the ratio.
- **C1 / W7.** (13)'s threshold and $1-f(0)$ at $\rho = 0.5$ have to be re-read from the recalibrated
  table before W7 fills section 7.6's placeholders.

## 9. What I could not settle

- Uniqueness under CRRA preferences or with informal savers: no proof, and section 2.4 names the terms
  that block one. The candidate counts (C0) and the horizon table (C4) are the evidence the paper can
  offer; the retirees' frozen objective is concave under CRRA too when $\xi(1-2\alpha) \leq 1$ (an
  increasing concave transformation of $c^i_{2,t} \propto (1-\tau_t)^{m}(x_i + a\tau_tp_i)$, which is
  concave in $\tau_t$ for $m \leq 1$), so a multiplicity, if one appeared, would come from the young's
  terms or from the consistency map, which is where C4's residual checks should look.
- Whether the cost can turn a local maximum at $\theta = 1$ into the global choice for some
  calibration the paper reports: it does not for the U.S. or France (both have a negative slope at the
  corner without the cost), and proposition 5 says it cannot for any electorate with that property; the
  CRRA once-and-for-all case is the one place where a corner exists without the cost, and there the
  question is moot since the corner is chosen at $\lambda = 0$.
- The A1 critical ratio under CRRA with the CRRA shares, and everything at the A2 calibration: C5's
  numbers; the structure (section 3 and section 8) is settled.
