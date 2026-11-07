# A microfoundation for the cost with $\tau^2$ (k = 2)

Written 2026-11-07 for `archive/notes/brief_tauPowerMicrofoundation.md`. The question: can the share of revenue lost,
$\ln f = -\tfrac12\lambda\tau^k\tilde V(1-\theta)^2$, be derived with $k = 2$ by tweaking the paper's story
(appendix C.2: Summers' tax component read as type-specific implicit taxes, Harberger's excess burden, charged
against the revenue that reaches retirees)? Notation is the paper's: $y_i$ relative earnings, $\Pi_t$ the
pay-as-you-go return factor, $R_t$ the market return, $\tilde V = \sum_i\gamma_i(y_i-1)^2/y_i$ the dispersion
of relative incomes, $\lambda$ the cost parameter, $1-f$ the share of revenue lost.

**Decided 2026-11-07 (RKB), after the comparison with the coauthor's version (section 10):** the text uses A's
accounting, the excess burden, with C's in a footnote ($3\kappa$ in place of $2\kappa$, an elasticity a third lower);
the recommendation below (C in the text) and section 6's steps are read with that change. The test run is (19) in the
coauthor's parametrisation $\lambda_{n,t} = 2\kappa\,\pi_{n,t}(1-\pi_{n,t})$, `notes/brief_convexCarrier.md`.

## Overturned (in part)

The brief's working assumption that "$k = 1$ is what the current story implies" holds under the accounting C.2
states, the Harberger triangle charged to revenue, together with a response that is linear in the wedge; it does
not hold under the literal reading of $1-f$ in section 7.1, "the share of revenue that does not reach retirees". Under
that reading a linear response erodes *no* revenue through the design, because the implicit taxes are a pure
transfer and the first-order base responses cancel (C.2's own footnote), and the first design cost is $k = 2$ (2B,
equation (13)). Second, the current story, taken at its own elasticity and with the uniform tax component it names
(Summers' tax component is the whole unvalued part, $1-\Pi/R = 0.45$ of the contribution at the U.S. values),
implies a loss of the size of the system of about $21\%$ of revenue that $f$ does not contain (1.3). Neither point
changes the $k = 1$ derivation as written; both bear on what a derivation of $k = 2$ may drop, since every
candidate below drops a size loss of the same kind and smaller.

## Summary and recommendation

**The answer.** $\tau^2$ with $(1-\theta)^2$ and $\tilde V$ cannot come from the implicit tax alone: any loss that
depends on the design and the tax only through $t_i$ ties the power of $\tau$ to one below the power of $1-\theta$
(lemma (4)), so "make the loss cubic" fails P3. One more $\tau$ has to enter from the one wedge the story names but
does not use: the uniform tax component $u\tau = (1-\Pi/R)\tau$, which every type pays and which does not depend on
the design. Under Harberger's quadratic it does not interact with the design (the interaction is the first-order
term $\sum_i\gamma_iy_it_i = 0$); under a *convex* extensive response it does, through the second-order term, and the
interaction is exactly $u\tau \times \tau^2(1-\theta)^2\tilde V$. The one tweak is therefore to replace "a common
elasticity" by "no one is at the margin at a zero wedge": the share of the base that leaves is quadratic in the
wedge, $F(T) = bT^2$, which two independent hurdles with positive densities at zero (the surplus of formality and a
cost of acting, candidate D, (16)) produce, and which is the natural case for a model whose informal technology is
strictly less productive. With that, $k = 2$ is pinned, and the three accountings of what the convexity costs give
the same form with different coefficients and carriers:

| | what the budget loses | $\lambda$ | exact? | dropped | carrier | $\varepsilon_{\mathrm{loc}}$ at the U.S. |
|---|---|---|---|---|---|---|
| A (10) | the excess burden, as C.2 | $4bu\,\Pi/R$ | to 2nd order in $r_i$ | size loss 5%, cubic $-8\%$ | $(\Pi/R)(1-\Pi/R)$, flat | 3.9 |
| B (13) | the contributions lost | $2b(\Pi/R)^2$ | exact | size loss 15% | $(\Pi/R)^2$, cv 20% | 6.4 |
| C (15) | the fiscal externality | $6bu\,\Pi/R$ | as A | as A | as A | 2.6 |

**Recommendation.** A's mechanism with C's accounting (section 6 gives the six steps for C.2): the budget pays the
participation tax of every unit of base that leaves, the response is quadratic in the wedge, the pure-transfer
property kills the first-order interaction with the uniform wedge and the second-order one carries $\tau^2$. It
keeps P1–P8 to leading order (P8 improves: the subsidy below the mean *reduces* the loss, Saez's direction, as a
consequence), removes C.2's footnote that charging the loss to revenue is "a choice of reduced form", makes the
carrier $\lambda_{n,t} = 6b\,u_{n,t}(\Pi/R)_{n,t}$ flat across countries and dates (coefficient of variation $1.2\%$
over the sample, against $10\%$ for the branch's $\Pi/R$), and lowers the implied elasticity from $11.3$ to $2.6$ at
$\rho = 1$ ($6.5$–$26$ times the 0.1–0.4 range, against $28$–$113$) and to $0.57$ at $\rho = 2$. It does not close the
magnitude gap; it drops a size loss of $5\%$ of revenue (C.2 drops $21\%$) and a cubic correction of $-8\%$ at the
observed design; and it needs the responding margin to see only the pension's wedge, which is true in the model and
is the one assumption a referee can refuse (section 9). The runner-up, B, is exact and literal but concedes that
$k = 1$ was never a revenue loss, drops $15\%$, and needs a rerun with a carrier that spreads $\lambda$ twice as much
as anything run. The branch's `'sizePiR'` at $k = 2$ is the reduced form "elasticity proportional to $\tau$" with the
$k = 1$ carrier; its cross-section approximates the microfounded one within $\pm15\%$ in $\lambda_n$ (Italy, Greece,
Hungary, Czechia too low, New Zealand and Ireland slightly high); the exact run is (19), a new carrier
$\pi(1-\pi)$ in `base.fWedge`/`dlnfWedge_dτ` and the three stages. The framework (18), $F = aT + bT^2$, nests
$k = 1$ ($b = 0$) and $k = 2$ ($a = 0$) with $k$ the local power of the extensive response in the wedge; it belongs in
a footnote. Inside the model $k = 2$ is the better-founded specification; outside it, $k = 1$ is the safer default
wherever the margin is labour-force participation under an income tax.

## 1. The current story and where $\tau$ enters

**1.1 The derivation of k = 1 (appendix C.2).** Against a purely earnings-related system paying the same revenue,
$\Pi_t\tau_t$ per unit of past earnings to every type, the flat component levies on type $i$
$$t_i = \Pi_t\tau_t(1-\theta_t)\left(1-\frac1{y_i}\right) \quad\text{per unit of past earnings}, \qquad \sum_i\gamma_iy_it_i = 0. \tag{1}$$
A worker values the benefit at $1/R_t$, so the rate is $t_i/R_t$; the bases per unit of mean past earnings are $e_i = y_i$;
with a common elasticity $\varepsilon$ the Harberger loss is
$$L = \tfrac12\varepsilon\sum_i\gamma_iy_i\left(\frac{t_i}{R_t}\right)^2 = \tfrac12\varepsilon\left(\frac{\Pi_t}{R_t}\right)^2\tau_t^2(1-\theta_t)^2\tilde V, \tag{2}$$
and the revenue that pays the benefits, valued by the same worker, is $(\Pi_t/R_t)\tau_t$ per unit of mean past
earnings, so that
$$1-f \approx \frac{L}{(\Pi_t/R_t)\tau_t} = \tfrac12\,\varepsilon\,\frac{\Pi_t}{R_t}\,\tau_t\,(1-\theta_t)^2\tilde V, \qquad \lambda = \varepsilon\,\frac{\Pi_t}{R_t}. \tag{3}$$
$\tau$ enters twice in the numerator (the wedge is proportional to the benefit, hence to the tax) and once in the
denominator. Every step is a stated assumption: (a) the wedge is the average implicit tax of the flat component; (b)
the margin is one the model lacks; (c) the loss is quadratic in the wedge with a common elasticity; (d) it is charged
against the revenue that reaches retirees; (e) it is booked in the period of the benefits; (f) $\Pi/R$ carries it.

**1.2 A structural lemma: a loss that sees only the implicit tax ties the two powers.** Suppose the loss per unit of
base of type $i$ is any function $g$ of its implicit tax rate alone, $L = \sum_i\gamma_iy_i\,g(t_i/R_t)$. If $g$ is
homogeneous of degree $m+1$ (the quadratic is $m = 1$; a participation response whose density of marginal workers
behaves like a power $m$ of the wedge gives $m+1$), then
$$L = \left(\frac{\Pi_t}{R_t}\right)^{m+1}\tau_t^{m+1}(1-\theta_t)^{m+1}\sum_i\gamma_iy_i\,g\!\left(1-\frac1{y_i}\right), \qquad 1-f \propto \tau_t^{m}\,(1-\theta_t)^{m+1}. \tag{4}$$
The power of $\tau$ in the share of revenue is always one below the power of $1-\theta$: $k = 2$ with $(1-\theta)^2$
cannot come from the implicit tax alone, under any functional form on any margin. (P3 and $k = 2$ are jointly
incompatible with (4); this is why "make the loss cubic" is not an answer.) One more $\tau$ has to enter from outside
the implicit tax. There are three doors: (i) a second wedge on the same margin that scales with $\tau$, does not
depend on the design, and *interacts* with the implicit tax, which requires a loss that is not quadratic, since under
a quadratic the interaction is the first-order term $\sum_i\gamma_iy_it_i = 0$; (ii) a response coefficient
$\varepsilon$ that itself scales with $\tau$, which door (i) produces endogenously (a convex response has a local
elasticity proportional to the wedge it sits at); (iii) a denominator that does not scale with $\tau$, which has no
reading, since $1-f$ is the loss as a share of revenue by definition. Section 2 is door (i); section 3 lists what
the other doors and the wedge-only forms give.

**1.3 The wedge the story names but does not use.** Summers' tax component is the whole unvalued part of the
contribution, not only its redistributive part. Per unit of earnings a cohort that pays $\tau_{t-1}$ at $t-1$ and
receives $\Pi_t\tau_t[\theta_t + (1-\theta_t)/y_i]$ at $t$, valued at $1/R_t$, faces the total average wedge
$$T_i \equiv \tau_{t-1} - \frac{\Pi_t}{R_t}\tau_t\left[\theta_t + \frac{1-\theta_t}{y_i}\right] = \tau_t\left[u_t + r_i\right], \qquad u_t \equiv \frac{\tau_{t-1}}{\tau_t} - \frac{\Pi_t}{R_t}, \qquad r_i \equiv \frac{\Pi_t}{R_t}(1-\theta_t)\left(1-\frac1{y_i}\right) = \frac{t_i}{R_t\tau_t}. \tag{5}$$
$u_t$ is the uniform wedge: what a purely earnings-related system takes from every unit of earnings because its
return falls short of the market return (and, along a rising tax path, net of the lower rate the cohort paid). In a
stationary comparison $u = 1-\Pi/R$, which at the U.S. 2020 values ($\Pi = 1.35$, $R = 2.44$) is $0.447$: the system
keeps 45 cents of every dollar it collects. With the dates, $u_{2020} = 0.0933/0.1052 - 0.554 = 0.33$ on the U.S. path
with the design chosen, and about $0.19$ in 2050, where the tax reaches $0.153$ (`results/esc/escPath.csv`). The
derivation in C.2 can drop $u$ because, under a quadratic loss, it does not interact with the design:
$$\tfrac12\varepsilon\sum_i\gamma_iy_iT_i^2 = \tfrac12\varepsilon\tau_t^2\left[u_t^2 + 2u_t\underbrace{\textstyle\sum_i\gamma_iy_ir_i}_{=0} + \left(\frac{\Pi_t}{R_t}\right)^2(1-\theta_t)^2\tilde V\right]. \tag{6}$$
The design-dependent term is exactly (2). What C.2 leaves out is the first term, a loss of the size of the system
that does not depend on the design: as a share of revenue $\tfrac12\varepsilon u^2\tau/(\Pi/R)$, which at the paper's
own elasticity ($\varepsilon = \lambda R/\Pi = 11.3$ at $\rho = 1$) is $21\%$ of revenue at the U.S. tax rate. The
paper's $f$ therefore already prices the design and not the size, and relies on the calibration of $\omega$ to
absorb what the size costs. Every candidate below produces such a term too, and smaller; the defence is the same.

**1.4 Timing.** Under (5) the uniform wedge mixes the tax of the contribution date and that of the benefit date,
whereas $r_i$ involves $\tau_t$ alone, as in C.2. The stationary $u = 1-\Pi_t/R_t$ is used in the algebra below, with
the dated $u_t$ noted where it changes a number; in the code $u_t$ would be an aggregate of the path, taken as given
by voters and iterated to a fixed point exactly as $\Pi_t/R_t$ is under `'sizePiR'`.

## 2. Candidates

One primitive delivers $\tau^2$ with $(1-\theta)^2$ and $\tilde V$: the response of the contribution base to its
average wedge is convex, and the wedge includes the system's own tax component. The candidates differ in what
the convexity costs the budget (A, B, C) and in what produces the convexity (D).

- **A. A convex extensive response at the tax component, excess-burden accounting.** The margin responds to the
  total average wedge $T_i = \tau[(1-\Pi/R) + (\Pi/R)(1-\theta)(1-1/y_i)]$; the density of marginal participants
  vanishes at a zero wedge and rises linearly; the loss is Harberger's integral to third order. $k = 2$ to leading
  order in the dispersion; $\lambda = 4b(1-\Pi/R)(\Pi/R)$.
- **B. The contribution revenue that the eroded base no longer pays** (the literal reading of "the share of revenue
  that does not reach retirees"), same response. $k = 2$ exactly; $\lambda = 2b(\Pi/R)^2$; a linear response gives
  no design cost at all under this accounting.
- **C. The net fiscal cost of the response** (net contributions of leavers, net benefits of entrants), same
  response. As A with coefficient $6$ in place of $4$.
- **D. The primitive behind the convexity: two hurdles.** A worker leaves the system only if the wedge exceeds both
  the surplus of formality and a fixed cost of acting; two independent thresholds with positive densities at zero
  give a response quadratic in the wedge. $n$ hurdles give $k = n$: the framework that nests $k = 1$ and $k = 2$.

### 2A. Candidate A: convex extensive response, excess-burden accounting

**Mechanism.** The base of type $i$, the earnings it brings into the system (formal employment, earnings reported
to the agency), responds to its total average wedge $T_i$ of (5). A worker stays in if the surplus of being in,
$\kappa$ per unit of earnings (the productivity advantage of formal work in the model's own informal sector, access
to formal credit, the employer's side), exceeds the wedge, so the share of the base that leaves is $F(T_i)$, with
$F$ the distribution of $\kappa$. Harberger's quadratic is the case $F(T) = aT$ near zero: a positive density of
workers indifferent between in and out at a zero wedge. The candidate assumes instead that *no one is at the margin
at a zero wedge* and that the density rises linearly from it,
$$F(T) = bT^2 \quad (T \ge 0), \qquad \ell(T) \equiv \int_0^T\kappa\,dF(\kappa) = \tfrac23\,b\,T^3, \tag{7}$$
where $\ell$ is the excess burden per unit of base, the surplus the leavers give up (for a net subsidy, $T < 0$,
the entrants are workers with $\kappa \in [T,0]$, and $\ell = \tfrac23 b|T|^3$ if the density is symmetric near
zero). Everything else is as in C.2: the loss is valued by the worker and charged against the revenue that reaches
retirees, valued alike.

**Derivation.** Per unit of mean past earnings, with $T_i = \tau[u + r_i]$ from (5) and every $T_i \ge 0$,
$$L = \tfrac23 b\sum_i\gamma_iy_iT_i^3 = \tfrac23\,b\,\tau^3\Big[u^3 + 3u^2\underbrace{\textstyle\sum_i\gamma_iy_ir_i}_{=0} + 3u\Big(\frac{\Pi}{R}\Big)^2(1-\theta)^2\tilde V + \Big(\frac{\Pi}{R}\Big)^3(1-\theta)^3\tilde W_3\Big], \qquad \tilde W_3 \equiv \sum_i\gamma_i\frac{(y_i-1)^3}{y_i^2}. \tag{8}$$
The first-order interaction between the uniform wedge and the implicit tax vanishes by the pure-transfer property,
exactly as in (6); the second-order interaction does not, and it carries one power of $u\tau$ on top of the
paper's $\tau^2(1-\theta)^2\tilde V$. As a share of the revenue $(\Pi/R)\tau$,
$$1-f = \tfrac23\,b\,\tau^2\Big[\frac{u^3}{\Pi/R} + 3u\,\frac{\Pi}{R}\,(1-\theta)^2\tilde V + \Big(\frac{\Pi}{R}\Big)^2(1-\theta)^3\tilde W_3\Big]. \tag{9}$$
The middle term is the branch's specification,
$$\ln f = -\tfrac12\,\lambda\,\tau^2\,\tilde V\,(1-\theta)^2, \qquad \lambda = 4\,b\,u\,\frac{\Pi}{R} = 4b\Big(1-\frac{\Pi}{R}\Big)\frac{\Pi}{R} \ \text{(stationary)}. \tag{10}$$
$k = 2$ is pinned by (7): it is the statement that the density of marginal participants is zero at a zero wedge
and linear beyond it. It holds to second order in the implicit taxes $r_i$ (the cubic term is dropped) and under the
functional form (7); the general power is candidate D.

**Assumptions, and what is dropped.** (A1) The responding margin sees only the system's own wedge, (5): true in the
model, where the payroll tax is the only tax; see section 9 for an income tax on the same margin. (A2) The density
of the surplus of formality is zero at zero and has a positive finite slope, (7). (A3) The loss is the surplus of
the leavers, charged against revenue at the worker's valuation, as in C.2 — step (d) of 1.1 is kept, not derived.
(A4) Every type is a net contributor, $T_i \ge 0$: $(1-\theta) \le u/[(\Pi/R)(1/y_{\min}-1)]$, which at the U.S.
values ($y_{\min} = 0.507$) is $1-\theta \le 0.83$, $\theta \ge 0.17$; below it the lowest type is a net beneficiary
and (8) holds with $|T_i|^3$, so the quadratic form is an approximation at the flat end. (A5) Dropped: the
design-independent loss of the size of the system, $\tfrac23 b u^3\tau^2/(\Pi/R)$, which at the calibrated $b$
below is $5.0\%$ of revenue at the U.S. tax, at every design (C.2's own omission, 1.3, is $21\%$); and the cubic
term, which relative to the term kept is
$$\frac{(\Pi/R)(1-\theta)\tilde W_3}{3u\tilde V} = -0.081 \ \text{at}\ \theta^{\ast} = 0.544, \qquad -0.178 \ \text{at}\ \theta = 0, \tag{11}$$
at the U.S. relative incomes ($\tilde W_3 = -0.188$, $\tilde V = 0.436$). It is negative: the subsidy to types below
the mean lowers their total wedge below $u$, where a convex loss is flatter, by more than the tax above the mean
raises it. (A6) The stationary $u$; with the dated $u_{2020} = 0.33$ the coefficient $4bu\Pi/R$ is $26\%$ smaller
at the same $b$, so the calibrated $b$ is correspondingly larger (the implied elasticity is not, (12)).

**Properties.** (P1) The design-dependent part vanishes at $\theta = 1$; the dropped size loss does not, so if it
were kept the tax at the Bismarckian corner would depend on $b$. (P2) Holds: $\tilde V = \tilde W_3 = 0$ when all
incomes are equal, and the loss is then the size loss alone. (P3) Holds to leading order, and the slope of the
political objective at $\theta = 1$ does not depend on $b$ even with the cubic term kept, since
$\partial(1-\theta)^3/\partial\theta$ vanishes there too. (P4) Holds to leading order; the correction carries the third
moment $\tilde W_3$. (P5) Imposed as in C.2, not derived: the candidate says nothing about how the loss splits across
components. (P6) The tax condition's factor is $1 + \tau\,\partial\ln f/\partial\tau = 1 + 2\ln f$, positive iff
$\ln f > -\tfrac12$, a loss below $39\%$ (at $k = 1$: $63\%$); at the $k = 2$ calibration a flat benefit loses
$9.5\%$ at $\rho = 1$ and $19.8\%$ at $\rho = 0.5$. The design gain is $\partial f/\partial\theta = f\lambda\tau^2\tilde V(1-\theta)
\ge 0$, zero at $\theta = 1$; it rises with $\tau$ iff $\partial(f\tau^2)/\partial\tau = 2f\tau(1+\ln f) > 0$, i.e. iff
$\ln f > -1$, with $\tilde V$ iff $\ln f > -1$, and with $1-\theta$ iff $\ln f > -\tfrac12$: the same three
conditions as C.3 at $k = 1$, the first always met where the anticipated tax is interior since the benefit term of
the tax condition carries $1 + 2\ln f$. With the cubic term kept the gain is multiplied by $1 + (\Pi/R)(1-\theta)\tilde W_3/(2u\tilde V)$,
$0.88$ at $\theta^{\ast}$ and $0.73$ at $\theta = 0$. (P7) Holds: $f$ depends on $(\theta_t,\tau_t)$ and on path
aggregates ($u_t$, $\Pi_t/R_t$) that voters take as given, so the proof of `prop:esc:separability` goes through
verbatim, with or without the dropped terms. (P8) The symmetry is broken in Saez's direction as a consequence, not
a caveat: a subsidy below the mean reduces the loss, by (11), as long as it stays below the uniform wedge (A4);
beyond that, entrants from outside the system cost surplus again.

**Implied $\lambda_{n,t}$.** $\lambda = 4b\,u_{n,t}(\Pi/R)_{n,t}$, with $u = 1-\Pi/R$ stationary: the carrier is
$(\Pi/R)(1-\Pi/R)$, not $\Pi/R$. Across the 20 countries of the $k = 2$ cross-section (worktree
`results/oecd26/layer1.csv`, `'sizePiR'`, CSES turnout) $\Pi/R$ runs from $0.41$ (Italy, Greece) to $0.58$ (New
Zealand), a coefficient of variation of $10\%$, while $(\Pi/R)(1-\Pi/R)$ runs from $0.241$ to $0.250$, a coefficient
of variation of $1.2\%$: the carrier is flat where $\Pi/R$ is near one half, as it is everywhere in the sample, and on
the U.S. path, where $\Pi/R$ falls from $0.55$ to $0.47$ and the carrier moves from $0.2475$ to $0.249$. The branch
runs $\lambda_n \propto (\Pi/R)_n$, which lowers Italy's $\lambda$ by $26\%$ relative to the U.S. where candidate A
lowers it by $2\%$; the branch's cross-section therefore approximates candidate A's with a country-specific error in
$\lambda$ of up to $\pm15\%$, in the direction of a flatter $\lambda$ than it ran. The dated $u_{n,t}$ would add a
channel the branch does not have, the ratio of the 1990 to the 2020 tax, which varies by country (section 9).

**Magnitude.** At $\rho = 1$, $\lambda = 41.45$ gives $b = \lambda/(4u\,\Pi/R) = 41.45/0.989 = 41.9$. The local
elasticity of the base with respect to its net-of-wedge rate at a wedge $T$ is $F'(T)(1-T)/(1-F) \approx 2bT$, and at
the wedge of the average type at the observed design, $T = u\tau = 0.047$ ($\theta = 1$ for the mean type),
$$\varepsilon_{\mathrm{loc}} = 2b\,u\,\tau = \frac{\lambda\,\tau}{2\,\Pi/R} = \frac{41.45 \times 0.105}{2 \times 0.553} = 3.9, \qquad F(T) = bT^2 = 0.093, \tag{12}$$
independent of $u$ (dated or stationary). The calibration thus says that $9\%$ of the base is outside the system
because of its tax component, with a local elasticity of $3.9$ at the observed wedge and zero at a zero wedge.
Against the $0.1$–$0.4$ range of participation and taxable-income elasticities, (12) is $10$ to $39$ times too large
at $\rho = 1$, where $k = 1$ is $28$ to $113$ times ($\varepsilon = \lambda R/\Pi = 11.3$). At $\rho = 0.5$
($\lambda = 91.6$): $8.7$, at $\rho = 2$ ($\lambda = 8.94$): $0.85$, i.e. $2$ to $8.5$ times the range, where $k = 1$ is
$6$ to $25$ times. The ratio of the two implied elasticities is $\lambda_2\tau/(2\lambda_1) = 0.35$ at every $\rho$:
the convex story reads the same calibrated cost as a response that is small at small wedges and large at the
observed one, which closes about a quarter of the gap on a log scale and does not close it. In the two-hurdle
reading of candidate D, $b = 1/(2\bar\kappa\bar\phi)$, so $b = 41.9$ is two uniform hurdles with supports of about
$0.11$ of earnings each.

**Support.** Summers (1989) for the tax component, of which the uniform wedge is the larger part; Harberger
(1964) for the integral (7), of which the triangle is the first term; Saez (2002) and Kleven and Kreiner (2006)
for the average wedge on the participation margin (all in `notes/paper_costLiterature.md`). For the convexity:
Chetty (2012, *Econometrica*, "Bounds on elasticities with optimization frictions") — to verify — argues that
adjustment costs attenuate responses to small incentives, so the observed response is convex in the size of the
wedge; Kleven and Waseem (2013, *QJE*, notches) — to verify — document the mass of non-responders at small
incentives; Gelber, Jones and Sacks (2020, *AEJ: Applied*, adjustment frictions and the Social Security earnings
test) — to verify — the same for a Social Security rule specifically. For the margin's being the pension's own
wedge (A1): Kumler, Verhoogen and Frías (2020) and Bergolo and Cruces (2014), in the note, where registration and
reporting respond to the link of the contribution with the benefit; Ulyssea (2018, *AER*, informality with
heterogeneous firms) — to verify — for an extensive formality margin with a distribution of surpluses.

**Verdict.** The candidate to put in the paper. It is the smallest tweak of C.2: one assumption, (A2), replaces
"a common elasticity", and the uniform wedge the story already names does the rest; $k = 2$ is pinned, P1–P8
survive to leading order with two dropped terms of stated size; the carrier is flat across countries and dates, so
the branch's run is close to the microfounded cross-section. The price: the implied elasticity remains an order of
magnitude above the benchmarks, the quadratic form is an approximation below $\theta = 0.17$, and (A1) ties the
margin to the pension's own wedge.

### 2B. Candidate B: the contribution revenue lost

**Mechanism.** The same response (7), but what is charged to the budget is what the budget literally loses: the
contributions that the eroded base no longer pays. This is the reading of $1-f$ that section 7.1's words carry
("the share of revenue that does not reach retirees") and the margin Kumler et al. document (earnings not reported
to the agency pay no contribution).

**Derivation.** The base of type $i$ per unit of mean past earnings is $y_i[1 - F(T_i)]$. Contributions collected at
$t-1$ fall by $\tau_{t-1}\sum_i\gamma_iy_iF(T_i)$, and as a share of the contributions $\tau_{t-1}$ of the same date
(no valuation factor: both sides are in the same units),
$$1-f = \sum_i\gamma_iy_i\,F(T_i) = b\,\tau_t^2\sum_i\gamma_iy_i(u+r_i)^2 = b\,\tau_t^2\Big[u^2 + \Big(\frac{\Pi}{R}\Big)^2(1-\theta)^2\tilde V\Big], \qquad \lambda = 2b\Big(\frac{\Pi}{R}\Big)^2. \tag{13}$$
$k = 2$ is *exact* under (7) and (A4): the square of $u + r_i$ has only the vanishing cross term and $r_i^2$, so there is
no cubic correction and no approximation in the dispersion; (A4) matters because an entrant ($T_i < 0$) adds
revenue, so in general the share is $b\sum_i\gamma_iy_i\,T_i|T_i|$. Under a *linear* response the same accounting
gives $a\tau_t\sum_i\gamma_iy_iT_i = a\tau_t^2u$: a loss of the size of the system and **no design cost at all**, by
the pure-transfer property. Under this accounting $k = 1$ has no derivation; the first design cost is $k = 2$.

**Assumptions.** (A1), (A2), (A4) as in A; (A3$'$) the loss is the contributions lost, booked in the period of the
benefits as C.2's timing footnote does; (A5$'$) dropped: the size loss $b\,u^2\tau^2$, which at the calibrated $b$ is
$15\%$ of revenue at the U.S. tax — three times A's and of the order of C.2's own omission (1.3). Nothing else is
dropped.

**Properties.** As A, with three differences: (P3), (P4) hold exactly; (P8) the symmetry of the paper's quadratic
is kept exactly (a subsidy and a tax of the same size erode the base alike), so the Saez sentence of C.2 stays as a
caveat; (P1) the dropped size loss is larger. (P6), (P7) as A.

**Implied $\lambda_{n,t}$.** $\lambda = 2b(\Pi/R)^2$: the carrier is $(\Pi/R)^2$, whose coefficient of variation across
the 20 countries is $20\%$, twice the branch's $\Pi/R$ ($10\%$) and sixteen times A's; Italy's $\lambda$ would be $52\%$
of the U.S. value (branch: $72\%$; A: $98\%$). The branch's run does not test B's cross-section; a run with
`wedgeΠR` squared would. Over the U.S. path, $(\Pi/R)^2$ falls from $0.31$ to $0.22$, lowering $\lambda$ by $28\%$ by 2110
(branch: $15\%$; A: $+0.6\%$).

**Magnitude.** $b = \lambda/(2(\Pi/R)^2) = 41.45/0.612 = 67.8$; at the average type's wedge $T = 0.047$,
$\varepsilon_{\mathrm{loc}} = 2bT = 6.4$ and $F(T) = 0.15$: the gap to the $0.1$–$0.4$ range is $16$ to $64$ times
(narrower than $k = 1$, wider than A). The revenue rectangle is larger than the welfare triangle at the same
response, so a given calibrated loss needs a smaller response under B than under A: $b$ is *larger* here only
because the design term of (13) lacks A's factor $3u$; in terms of the share of the base outside the system the
two differ by the same factor.

**Support.** The literal reading of the budget; Kumler, Verhoogen and Frías (2020) and Bergolo and Cruces (2014)
(in the note) measure exactly this object, registered earnings; the convexity references of A.

**Verdict.** Runner-up. Exact, one line, and the accounting that the budget's own words suggest; but it admits that
the paper's $k = 1$ form was never a revenue loss, its omitted size loss is $15\%$ of revenue, and its carrier
$(\Pi/R)^2$ spreads $\lambda$ across countries twice as much as anything the branch has run, so adopting it costs a
full rerun whose outcome is open.

### 2C. Candidate C: the net fiscal cost

**Mechanism.** The same response (7); what is charged is the fiscal externality of the response, the object that
the participation-margin literature puts into its optimal-tax formulas (Saez 2002; Kleven and Kreiner 2006, in the
note): a leaver stops paying $\tau_{t-1}$ per unit of earnings *and* stops drawing the benefit the system owed him,
so the budget loses, in present value, the participation tax $T_i$ of (5) per unit of base that leaves; an entrant
costs $-T_i > 0$ per unit that enters. This is B with the forgone benefits credited.

**Derivation.** Per unit of mean past earnings, with every $T_i \ge 0$,
$$L^{C} = \sum_i\gamma_iy_i\,T_iF(T_i) = b\sum_i\gamma_iy_iT_i^3 = \tfrac32\,L, \tag{14}$$
with $L$ the excess burden (8): the rectangle $T\,\Delta\text{base}$ in place of the triangle under a quadratic
response. Everything in A carries over with the coefficient scaled by $\tfrac32$:
$$\lambda = 6\,b\,u\,\frac{\Pi}{R}, \qquad \text{cubic correction (11) unchanged}, \qquad \text{size loss } b\,u^3\tau^2/(\Pi/R) = 5.0\%. \tag{15}$$
Under a *linear* response the same accounting gives $a\sum_i\gamma_iy_iT_i^2$, which is (6) with $a$ in place of
$\tfrac12\varepsilon$: the paper's $k = 1$ form with twice Harberger's coefficient. C is therefore the one accounting
under which both the paper's $k = 1$ (linear response) and the convex $k = 2$ are *what the budget loses*, with step
(d) of 1.1 a consequence rather than a choice: the budget pays the fiscal externality of the response, and nobody's
utility in the model carries the leavers' surplus, which is right, since the leavers are not in the model.

**Assumptions.** (A1), (A2), (A4), (A6) as in A; (A3$''$) the present value of the forgone benefit is taken at $R$,
and the two dates are combined in the booking period as C.2 does; (A5) as A, with the size loss $5.0\%$ (the
coefficient $b$ is smaller by $\tfrac23$, the loss formula larger by $\tfrac32$).

**Properties.** Identical to A: the loss is proportional to A's at every $(\theta,\tau)$.

**Implied $\lambda_{n,t}$.** As A: $(\Pi/R)(1-\Pi/R)$, flat across countries and dates.

**Magnitude.** $b = \lambda/(6u\,\Pi/R) = 41.45/1.483 = 27.9$; $\varepsilon_{\mathrm{loc}} = 2bu\tau = \lambda\tau/(3\Pi/R) = 2.6$,
$F(T) = 0.062$: $6.5$ to $26$ times the range at $\rho = 1$ ($0.57$ at $\rho = 2$: $1.4$ to $5.7$ times). The narrowest
gap of the three accountings, because the rectangle is the largest loss per unit of response.

**Support.** Saez (2002) and Kleven and Kreiner (2006) in the note, whose participation tax rate is exactly $T_i$
and whose fiscal externality is exactly $T_i\,\Delta e_i$; Browning (1976, *JPE*, "The marginal cost of public
funds") — to verify — for the rectangle as the budget's loss.

**Verdict.** The accounting to use in the text, with A's mechanism: same algebra, same carrier, same properties,
and it removes C.2's footnote that charging the loss to revenue "is a choice of reduced form rather than a
consequence of the argument". The implied elasticity sentence improves to $2.6$. Nothing in the code changes between
A and C (the calibration absorbs the coefficient).

### 2D. Candidate D: two hurdles, and $k$ as the number of hurdles

**Mechanism.** Why would the density of the surplus of formality vanish at a zero wedge? Because leaving the system
takes more than a reason: it takes an act. Let a worker leave only if the wedge exceeds *both* the surplus of
formality $\kappa$ and a cost of acting $\phi$ (finding the informal job, learning the rule, the employer's
cooperation), the two independent and each with a positive density at zero, uniform on $[0,\bar\kappa]$ and
$[0,\bar\phi]$. Then
$$F(T) = \Pr(\kappa + \phi < T) = \frac{T^2}{2\bar\kappa\bar\phi} \quad (T \le \min\{\bar\kappa,\bar\phi\}), \qquad b = \frac1{2\bar\kappa\bar\phi}, \tag{16}$$
which is (7), and the leavers give up $\kappa + \phi$, both real, so the excess burden is $\int(\kappa+\phi)\,dF = \tfrac23 bT^3$ as
in (7). A single hurdle with a positive density at zero is Harberger ($F = aT$, $a$ the density of workers
indifferent at a zero wedge); a second hurdle with a positive density at zero convolves the two densities, and the
convolution of two positive constants near zero is a line through zero. Equivalently and without a second hurdle:
no worker is exactly indifferent to formality when the system is actuarially fair, as in the paper's own model,
where the informal technology is strictly less productive for every type.

**The framework.** With $n$ independent hurdles, each uniform near zero, $F(T) = T^n/(n!\prod_j\bar\kappa_j)$, the volume
of a simplex; more generally let the response be a power of the wedge, $F(T) = cT^m$. Then
$\ell(T) = \tfrac{m}{m+1}cT^{m+1}$, and the design-dependent term of $\sum_i\gamma_iy_i\,\ell(T_i)$ is the coefficient of
$r_i^2$ in $(u+r_i)^{m+1}$, namely $\binom{m+1}{2}u^{m-1}$, so that as a share of revenue
$$1-f \ni \tfrac12\,\lambda_m\,\tau^m\,\tilde V\,(1-\theta)^2, \qquad \lambda_m = m^2\,c\,u^{m-1}\,\frac{\Pi}{R}: \qquad k = m. \tag{17}$$
$m = 1$ is C.2 with $c = \varepsilon$ and $\lambda_1 = \varepsilon\,\Pi/R$; $m = 2$ is (10); $m = n$ for $n$ hurdles. $k$ is
therefore the local power of the extensive response in the wedge, one plus the elasticity of the participation
elasticity with respect to the wedge: $k = 2$ says the participation elasticity is proportional to the wedge it is
measured at. A mixture, $F = aT + bT^2$, gives the sum of the $k = 1$ and $k = 2$ terms (section 4). The dropped terms
at general $m$: a size loss $\propto u^{m+1}\tau^m$ and corrections of third and higher order in $r_i$.

**Assumptions and properties.** (16) adds to A only the independence of the two hurdles and the uniformity of each
near zero (any positive finite densities at zero give the same leading term); the accounting is A's or C's, and
P1–P8 are A's. The framework is exact in $k$ only when the response is a pure power; a positive density at a zero
wedge, however small, restores a $k = 1$ term that dominates at small enough taxes.

**Magnitude.** $b = 41.9$ (A) gives $\bar\kappa\bar\phi = 0.012$: two hurdles with supports of about $0.11$ of
earnings each, or, with a fraction $\pi_0$ of the base near the margin and the rest far from it, $\pi_0/(2\bar\kappa\bar\phi)$,
e.g. $\pi_0 = 0.3$ with supports of $0.06$. Under C ($b = 27.9$) the supports are $0.13$. Either way the calibration
says that the workers who can leave the system at a cost below a tenth of their earnings, and for whom formality is
worth less than a tenth of their earnings, are a sizeable band of the base; whether they are is the open empirical
question that the magnitude sentence of C.2 should state.

**Support.** Chetty (2012) — to verify — is the closest statement: with fixed adjustment costs, the response to an
incentive is attenuated when the incentive is small and the observed elasticity rises with the size of the change;
Kleven and Waseem (2013) and Gelber, Jones and Sacks (2020) — to verify — measure the frictions at notches and at the
Social Security earnings test; Ulyssea (2018) — to verify — has the extensive formality margin with a distribution of
surpluses. None of these is in `notes/paper_costLiterature.md`; all are to be checked before citation.

**Verdict.** The primitive that pins $k$, and the one sentence that C.2 needs: a worker leaves only if the wedge
exceeds both the surplus of formality and a cost of acting, so the share leaving is quadratic in the wedge; the
general power (17) goes in a footnote as the framework that nests the paper's $k = 1$.

## 3. Levers that do not deliver $\tau^2$ (counterexamples)

Each of the brief's levers (a)–(f) was tried; what follows is what each gives, so that the reader can see why
section 2 is the answer rather than one answer.

- **A power law in the implicit tax alone** (lever (c) without the uniform wedge). By (4), a loss $\propto|t_i|^{m+1}$
  gives $\tau^m(1-\theta)^{m+1}$: the cubic gives $\tau^2(1-\theta)^3\sum_i\gamma_iy_i|1-1/y_i|^3$ ($= 0.357$ at the U.S.),
  which breaks P3 and replaces $\tilde V$ (P4). $k = 2$ with $(1-\theta)^2$ is unreachable this way.
- **A fixed cost in levels** (the hurdle in consumption units rather than per unit of earnings). A worker leaves iff
  $\tau y_i(u + r_i) > \kappa$; with a uniform density the excess burden is $\tfrac12a\tau^2\sum_i\gamma_iy_i^2(u+r_i)^2
  = \tfrac12a\tau^2[u^2(1+V) + 2u(\Pi/R)(1-\theta)V + (\Pi/R)^2(1-\theta)^2V]$ with $V = \sum_i\gamma_i(y_i-1)^2$: the
  weights are $y_i^2$, so the cross term no longer vanishes. The result is $k = 1$, the variance in place of
  $\tilde V$, and a term linear in $1-\theta$ (which would let an electorate choose $\theta = 1$ exactly; a different
  specification, not this brief's).
- **A pre-existing distortion under a linear response** (an income tax $T_0$ on the same margin, lever (b)).
  $\tfrac12a\sum_i\gamma_iy_i(T_0 + T_i)^2 = \tfrac12a[T_0^2 + 2T_0u\tau + u^2\tau^2 + \tau^2(\Pi/R)^2(1-\theta)^2\tilde V]$: the design
  term is untouched, $k = 1$ whatever $T_0$. Under the convex response $T_0$ enters the cross term,
  $3(T_0 + u\tau)\,\tau^2(\Pi/R)^2(1-\theta)^2\tilde V$, a mixture of $k = 1$ (weight $T_0$) and $k = 2$ (weight $u\tau$);
  with a participation tax of $0.3$ from other taxes and $u\tau = 0.047$, the $k = 1$ part would dominate six to one.
  This is the main threat to (A1), section 9.
- **Liquidity constraints** (lever (f), the valuation). A constrained type values the benefit at $\delta_i/R$,
  $\delta_i < 1$, so its uniform wedge is $u_i = 1 - \delta_i\Pi/R$ and under a linear response the cross term is
  $-(\Pi/R)^2(1-\theta)\sum_i\gamma_i\delta_i(y_i-1)$, a term linear in $1-\theta$ times the covariance of $\delta$ with
  income; it carries $\tau^2$ only if the constraint tightens with $\tau$ (as it does by `eq:si_s`), and then as
  $\tau^2(1-\theta)$: P3 fails.
- **Optimisation frictions on the intensive margin** (hours, reporting). The gain from re-optimising to a wedge $r$
  is the triangle $\tfrac12\varepsilon_0r^2$, so the fraction that acts is $\propto r^2$ and the loss $\propto r^4$: $k = 3$
  with $(1-\theta)^4$, (4) again. Frictions deliver $k = 2$ only on the extensive margin, where the gain from acting is
  linear in the wedge, $T - \kappa$ (candidate D).
- **The denominator** (lever (d), "as a share of what"). Charging the loss against the amount the flat component
  carries, $(\Pi/R)\tau(1-\theta)\sum_{y_i>1}\gamma_i(y_i-1)$, Okun's leak per unit carried, and then the amount against
  revenue, is an identity that gives back (3): $k$ is a property of the numerator.
- **The valuation** (lever (f)). Discounting at the system's own return sets $u = 0$ and changes the carrier, not
  $k$; a valuation that falls with the size of the system (political risk) moves $u$, which under a linear response
  does not interact with the design and under the convex one only rescales $b$.
- **Heterogeneous elasticities**, $\varepsilon_i \propto y_i^{m}$: other moments in place of $\tilde V$, no $\tau$.
- **An elasticity assumed proportional to $\tau$**, $\varepsilon = \hat\varepsilon\tau$, gives $k = 2$ exactly with the
  branch's carrier $\Pi/R$: this *is* the branch's `'sizePiR'` at $k = 2$, and it is a restatement of the question.
  Its only microfoundation is the convex response, whose local elasticity is proportional to the wedge it sits at,
  $u\tau + r_i$, which is why the microfounded carrier is $u\,\Pi/R$ rather than $\Pi/R$.
- **Second-round amplification** (the loss lowers the benefit, which raises the tax component, which raises the
  loss) multiplies the $k = 1$ term by $1 + O(\tau)$: a correction, not a form.

## 4. The nesting framework

With a response that has both a positive density at a zero wedge and a positive slope, $F(T) = aT + bT^2$, the two
terms of candidate D add, and under A's accounting
$$\ln f = -\tfrac12\,\frac{\Pi}{R}\,\tilde V\,(1-\theta)^2\left[a\,\tau + 4b\,u\,\tau^2\right], \qquad (\text{C's accounting: } [2a\,\tau + 6b\,u\,\tau^2]). \tag{18}$$
$k = 1$ is $b = 0$ (Harberger: somebody is indifferent at a zero wedge); $k = 2$ is $a = 0$ (nobody is). The
specification is not a choice between two powers but a statement about the density of marginal participants at a
zero wedge, and (18) is what one would estimate if the data could: the U.S. design pins one combination,
$a\tau_{US} + 4bu\tau_{US}^2$, and a second country's own design the other. The UK is too close to the U.S. in the size
of its system ($0.112$ against $0.105$) to separate them: the two terms differ across the pair by the factor
$\tau_{UK}/\tau_{US} = 1.06$ only, whereas the worktree's own-$\lambda$ calibrations put the UK at $0.54$ of the U.S.
value at $k = 2$ and at about $0.84$ at $k = 1$, so the mix that matches both exactly is not well determined.
The separation comes from the spread of taxes in the cross-section, $0.04$ to $0.24$, which is also what prefers
$k = 2$ there; a two-parameter fit to the 20 designs is possible but would turn the cross-section from a test into a
calibration. The honest use of (18) is as the footnote that says what $k$ means and that $k = 1$ is nested, with
$k = 2$ the case the paper adopts on the stated assumption.

The tax condition under (18) carries $1 + \tau\,\partial\ln f/\partial\tau = 1 + \ln f + \ln f_2$, where $\ln f_2$ is the
$k = 2$ part: the general factor is $1 + \sum_k k\ln f_k$, which the branch's `1 + k ln f` covers only for a pure
power. The design gain $\partial f/\partial\theta = f\,\frac{\Pi}{R}\tilde V(1-\theta)[a\tau + 4bu\tau^2] \ge 0$ keeps the
monotonicity conditions of C.3 with $\ln f$ read as the whole exponent.

What the branch tests: `'sizePiR'` at $k = 2$ is (18) with $a = 0$ and the carrier $\Pi/R$ in place of
$u\,\Pi/R$; since $(\Pi/R)(1-\Pi/R)$ is flat across the sample (2A), the branch's cross-section is the microfounded
one up to country-specific errors in $\lambda$ of at most $\pm15\%$ (Italy and Greece too low, New Zealand and Ireland
too high) and a uniform scale that the calibration absorbs. It is not a test of B, whose carrier is $(\Pi/R)^2$.

## 5. Magnitude at the U.S. 2020 values

$\Pi/R = 0.553$, $u = 0.447$, $\tau = 0.105$, the wedge of the average type $T = u\tau = 0.047$; $\lambda$ from the
worktree's `escCalibration.csv` ($k = 2$) and main's ($k = 1$), log preferences unless stated.

| | $\lambda$ ($\rho = 1$) | $\lambda$ in primitives | primitive | $\varepsilon_{\mathrm{loc}} = 2bT$ | share of base out, $F(T)$ | times the 0.1–0.4 range | size loss at $\theta = 1$ (dropped) |
|---|---|---|---|---|---|---|---|
| $k = 1$, C.2 | 6.25 | $\varepsilon\,\Pi/R$ | $\varepsilon = 11.3$ | 11.3 (constant) | — | 28–113 | 21% if $u$ is priced |
| A (excess burden) | 41.45 | $4bu\,\Pi/R$ | $b = 41.9$ | 3.9 | 9.3% | 10–39 | 5.0% |
| B (contributions lost) | 41.45 | $2b(\Pi/R)^2$ | $b = 67.7$ | 6.4 | 15% | 16–64 | 15% |
| C (net fiscal cost) | 41.45 | $6bu\,\Pi/R$ | $b = 27.9$ | 2.6 | 6.2% | 6.5–26 | 5.0% |

At $\rho = 0.5$ ($\lambda = 91.6$) and $\rho = 2$ ($\lambda = 8.94$) the local elasticities scale with $\lambda$: A $8.7$ and
$0.85$, B $14.2$ and $1.4$, C $5.8$ and $0.57$; $k = 1$ at the same IES ($\lambda = 13.47$, $1.41$): $24.4$ and $2.55$.
No candidate closes the gap. C narrows it most, by the factor $\lambda_2\tau/(3\lambda_1) = 0.23$ at every IES, so that
at $\rho = 2$ the implied elasticity, $0.57$, is within a factor of $1.4$ of the top of the range (the paper's "6 to 25
times" at $\rho = 2$ becomes "1.4 to 5.7 times"), and at $\rho = 1$ "28 to 113 times" becomes "6.5 to 26 times". The
reading changes with the number: at $k = 1$ the calibrated cost is a response that is the same at every wedge; at
$k = 2$ it is a response that is zero at a zero wedge and $2.6$ at the observed one, with $6\%$ of the base outside
the system because of its tax component. The magnitude sentence of C.2 would keep its structure ("$\lambda$ also stands
in for administrative, evasion and political costs") with smaller multiples.

## 6. Recommendation, the runner-up, and $k = 1$ against $k = 2$

**Recommendation.** Candidate A's mechanism with candidate C's accounting: the extensive response is convex at
the system's own tax component, and the budget loses the fiscal externality of the response. How C.2 would derive
it, in six steps that replace "The Harberger loss" and "Specification":

1. *The wedge.* Summers' tax component is the whole unvalued part of the contribution: per unit of earnings a cohort
   pays $\tau$ and receives, valued at $1/R_t$, $(\Pi_t/R_t)\tau[\theta + (1-\theta)/y_i]$, so its average wedge is
   $T_i = \tau[u + r_i]$ of (5), the uniform wedge $u = 1-\Pi_t/R_t$ plus the implicit tax (1) in rate form.
2. *The margin.* Formality and reporting to the system, on which the average wedge is the relevant one (Saez; Kleven
   and Kreiner) and, in the model, the only wedge is the system's own, there being no other tax.
3. *The response.* A worker leaves only if the wedge exceeds both the surplus of formality and a cost of acting;
   with both positive-density at zero, the share leaving is $F(T) = bT^2$, (16): no one is at the margin at a zero
   wedge. (Harberger's quadratic loss is the case of a positive density of indifferent workers at a zero wedge.)
4. *The loss.* The budget loses the participation tax of every unit that leaves, $\sum_i\gamma_iy_iT_iF(T_i) = b\sum_i\gamma_iy_iT_i^3$, (14).
5. *The expansion.* $(u + r_i)^3 = u^3 + 3u^2r_i + 3ur_i^2 + r_i^3$; the first-order interaction vanishes because the
   implicit taxes are a pure transfer, $\sum_i\gamma_iy_ir_i = 0$; the second-order one survives and carries the uniform
   wedge: $3bu\tau^3(\Pi/R)^2(1-\theta)^2\tilde V$. As a share of the revenue $(\Pi/R)\tau$ this is
   $\tfrac12\lambda\tau^2\tilde V(1-\theta)^2$ with $\lambda = 6bu\,\Pi/R$, (15). Dropped and said: the loss of the size of the
   system, $bu^3\tau^2/(\Pi/R)$, $5\%$ of revenue at the U.S. tax and absorbed by the calibration of $\omega$; the cubic
   term, $-8\%$ of the term kept at the observed design and negative, since a subsidy below the mean lowers a wedge
   where a convex loss is flat (Saez's point is now a consequence); the stationary $u$.
6. *Specification and magnitude.* As now, with $\tau^2$, the factor $1 + 2\ln f$ in the tax condition (positive while
   the loss is below $39\%$), the carrier $u_{n,t}(\Pi/R)_{n,t}$ across countries (flat, 2A), and the sentence
   $\varepsilon_{\mathrm{loc}} = \lambda\tau/(3\Pi/R) = 2.6$ at $\rho = 1$ against $0.1$–$0.4$.

If the text keeps the excess-burden accounting instead, steps 4–5 read with $\tfrac23 b$ and $\lambda = 4bu\,\Pi/R$ and
the footnote on charging a welfare loss to the budget stays; nothing else changes, including the code.

**The runner-up's cost (B).** B is exact and one line, and it is what the budget's words say; but it concedes that
the paper's $k = 1$ was never a revenue loss (a linear response erodes no revenue through the design), it drops a
size loss of $15\%$ of revenue, three times A's, and its carrier $(\Pi/R)^2$ spreads $\lambda$ across countries with a
coefficient of variation of $20\%$, twice the branch's and sixteen times A's, so that nothing already run tests it:
adopting B means a rerun of stages (i)–(iii) with `wedgeΠR` squared, and the cross-section's fit at the end of it is
open (Italy's and Greece's $\lambda$ would fall to half the U.S. value, New Zealand's and Ireland's rise by a tenth).

**$k = 1$ against $k = 2$, both written out.** $k = 1$ rests on a linear extensive response (somebody is indifferent at
a zero wedge) and on nothing about the uniform wedge; it is robust to other taxes on the same margin; its implied
elasticity is $11$ at $\rho = 1$, $28$–$113$ times the benchmarks. $k = 2$ rests on a convex extensive response (nobody
is indifferent at a zero wedge: two hurdles, or formality strictly valued, as in the model's own informal sector), on
the responding margin's seeing only the pension's wedge (true in the model, a restriction in the world, section 9),
and on dropping a $5\%$ size loss and a $-8\%$ cubic correction; its implied elasticity is $2.6$ at $\rho = 1$ and
$0.57$ at $\rho = 2$, $6.5$–$26$ and $1.4$–$5.7$ times the benchmarks. Inside the paper's model, where the payroll tax is
the only tax and the informal technology is strictly less productive, $k = 2$ is the better-founded specification:
its one extra assumption is the one the model's own formality margin makes, and both its dropped terms are
smaller than the size loss that $k = 1$ already drops silently (1.3). Outside the model, $k = 1$ is the safer default
wherever the margin is labour-force participation under an income tax. I would adopt $k = 2$ with (18) in a footnote
and $k = 1$ as the robustness check, the mirror of the worktree note's plan.

## 7. The test

**Against $k = 1$.** The cost of a given design grows with the square of the size of the system: between 2020 and
2050 on the U.S. path the tax rises from $0.105$ to $0.153$, which raises the cost of the observed design by the
factor $2.1$ at $k = 2$ and $1.45$ at $k = 1$, so ageing ties benefits more closely to earnings (the worktree:
$0.66 \to 0.74$ against the paper's $0.66$); across countries the index responds to population growth twice as
much ($-0.43$ against $-0.22$, data $-0.44$) and the predicted designs spread twice as much (sd $0.20$ against
$0.11$, data $0.32$). These are the branch's numbers; the microfoundation adds nothing to them, it says why.

**Against the branch's plain $k = 2$.** Three differences, in decreasing order of size.
1. *The carrier.* $\lambda_{n,t} = 6b\,u_{n,t}(\Pi/R)_{n,t}$ with $u = 1-\Pi/R$, flat across the sample, against the
   branch's $\varepsilon(\Pi/R)_{n,t}$: relative to the branch, Italy's, Greece's, Hungary's and Czechia's $\lambda$ rise by a
   quarter to a third (their $\Pi/R$ is $0.41$–$0.47$ against the U.S. $0.57$), New Zealand's and Ireland's fall by a few
   percent. From the anchor's scan the design moves by about $0.5$ per unit of $\ln\lambda$, so these four would move
   by up to $+0.1$: Italy ($0.62$ predicted, $0.95$ observed) and Hungary ($0.83$, $1.00$) toward their data, Czechia
   ($0.82$, $0.34$) away, Greece ($0.82$, $0.83$) past it. The net effect on the fit is a run, not a derivation.
   With the dated $u_{n,t} = \tau_{n,t-1}/\tau_{n,t} - (\Pi/R)_{n,t}$ a new channel appears, the growth of each system
   between 1990 and 2020: a system that grew fast has a smaller uniform wedge and a smaller $\lambda$.
2. *The cubic term.* Keeping it multiplies the design gain by $1 + (\Pi/R)(1-\theta)\tilde W_3/(2u\tilde V)$, $0.88$ at
   $\theta^{\ast}$ and $0.73$ at $\theta = 0$ for the U.S., with $\tilde W_3$ country-specific and negative wherever the
   mass below the mean dominates: the gain from a more Bismarckian design is smaller at flat designs than the
   quadratic says, which pulls the Beveridgean-corner countries' predictions down. Second order; a robustness row.
3. *The size loss.* $f_0(\tau) = \exp(-bu^3\tau^2/(\Pi/R))$ in the budget at every design would change the tax
   condition (a larger system loses more whatever its design) and the tax at the Bismarckian corner. Omitted in the
   recommended specification, as C.2 omits its own; a robustness row at most.

**The run.** A new spec in `python/US/base.py`, say `'sizeConvex'`, with
$$\ln f(\theta_t,\tau_t) = -\tfrac12\,\hat\lambda\,\pi_t(1-\pi_t)\,\tau_t^2\,\tilde V\,(1-\theta_t)^2, \qquad \pi_t = \Pi_t/R_t, \qquad \lambda_{n,t} = \hat\lambda\,\pi_{n,t}(1-\pi_{n,t}), \tag{19}$$
$\hat\lambda = 6b$ calibrated to $\theta_{2020} = \theta^{\ast}$ as now, and $\partial_\tau\ln f = -\hat\lambda\pi(1-\pi)\tau\tilde V(1-\theta)^2$
(the branch's `k*τ**(k-1)` path). The carrier replaces `wedgeΠR` by $\pi(1-\pi)$ at the same dates and the same
fixed-point iteration of the $\pi$ path (`modelESC`, `_ΠRstart`); the brackets scale as the branch's (`TAU_SCALE`),
with $\hat\lambda$ about $\lambda/0.247$. Optional rows: the cubic term, which needs a memoised $\tilde W_3$ next to
`Vtilde` and enters the design search through $f$ only (the design is a grid search, so no derivative is needed),
and the size loss $f_0(\tau_t)$, which enters the tax condition through $\partial_\tau\ln f$. Stages touched: (i)
`runCalibration` (log and the two CRRA recursions), (ii) `runShocks`, the ESC country and OECD26 drivers
(`runOECD26` with the carrier), (iii) `build`; the dated $u_t$ would add a second path object, $\tau_{t-1}/\tau_t$.
Nothing in the exogenous-design stages changes. Expected cost: the branch's full run again.

## 8. Numerical confirmation

A five-second script in `python/US` (the repo's interpreter, `PYTHONUTF8=1`, `test.py`'s group shares and relative
incomes, $\gamma = (0.582, 0.176, 0.242)$, $y = (0.507, 1.000, 2.187)$, which give $\tilde V = 0.4357$, the paper's $0.436$,
and $\tilde W_3 = -0.188$), at $\Pi/R = 0.553$, $u = 0.447$, $\tau = 0.1052$, $\lambda = 41.45$, $b = 41.9$. A
confirmation of the algebra, not an argument.
1. The exact excess-burden share $\tfrac23 b\sum_i\gamma_iy_i|T_i|^3/((\Pi/R)\tau)$ equals the three terms of (9) to five
   decimals at $\theta = 0.17, 0.3, 0.544, 0.8, 1$ (e.g. $0.06893$ at $\theta^{\ast}$: size $0.04984$, quadratic $0.02078$,
   cubic $-0.00169$); the quadratic term equals the branch's $\tfrac12\lambda\tau^2\tilde V(1-\theta)^2$ at every $\theta$
   by construction. At $\theta = 0$ the lowest type is a net beneficiary ($T = -0.0097$) and the expansion misses the
   exact $|T|^3$ sum by $0.0003$ ($0.1320$ against $0.1322$). The cubic is $-8.1\%$ of the quadratic at $\theta^{\ast}$,
   $-17.8\%$ at $\theta = 0$, (11).
2. The linear-response identity (6): $\sum_i\gamma_iy_iT_i^2 - \tau^2u^2 = (\Pi/R)^2\tau^2(1-\theta)^2\tilde V$ to machine
   precision ($3.07\times10^{-4}$ both sides at $\theta^{\ast}$).
3. B at $b = 67.7$: exact share $0.1703$ = size $0.1495$ + design $0.0208$, (13).
4. Two hurdles, (16): Monte Carlo with $2\times10^6$ draws of $\kappa,\phi \sim U[0, 0.11]$ gives $F(0.047) = 0.0912$
   against $T^2/(2\cdot0.11^2) = 0.0913$; $b = 41.3$; $\varepsilon_{\mathrm{loc}} = 2bT = 3.94$, (12).
5. P6 at the $k = 2$ calibration: $f(0) = 0.905$ at $\rho = 1$, $1 + 2\ln f = 0.80 > 0$.
6. The carriers over the 20 countries of the worktree's `results/oecd26/layer1.csv` (`'sizePiR'`, CSES):
   coefficients of variation $10.3\%$ for $\Pi/R$, $1.2\%$ for $(\Pi/R)(1-\Pi/R)$, $20.5\%$ for $(\Pi/R)^2$; ranges
   $0.407$–$0.578$, $0.241$–$0.250$, $0.166$–$0.334$.

## 9. Open questions

1. **Which margin, (A1).** With an income tax's participation tax $T_0$ on the same margin, the convex response gives
   the mixture $3(T_0 + u\tau)$ in place of $3u\tau$ (section 3), a $k = 1$ term with weight $T_0$ next to the $k = 2$
   term with weight $u\tau = 0.047$. Pure $k = 2$ needs a margin on which only the pension's wedge bites: earnings
   reported to the agency (Kumler et al.), covered against uncovered employment, opting out. In the model $T_0 = 0$;
   in the text the margin named decides whether $k = 2$ is exact or a $k = 1$/$k = 2$ mix, and the derivation should
   say which. This is the one assumption a referee can refuse.
2. **The dated uniform wedge.** $u_t = \tau_{t-1}/\tau_t - \Pi_t/R_t$ is $0.33$ in 2020 and about $0.19$ in 2050 on the U.S.
   path, against the stationary $0.447$ used above; it changes $b$ (not the implied elasticity, (12)) and adds the
   growth of each system between 1990 and 2020 as a cross-country determinant of $\lambda$. Whether it helps or hurts
   the cross-section is a run; and which $\tau_{t-1}$ to use (the data's 1990 tax or the model's path) is a choice.
3. **The domain, (A4).** The expansion holds while every type is a net contributor, $\theta \ge 0.17$ at U.S. incomes;
   the Beveridgean-corner countries sit outside it, where the exact $|T_i|^3$ form prices entrants. For the U.S.
   distribution the difference at $\theta = 0$ is $0.0003$ of revenue; for a distribution with a heavier bottom it grows
   with $(1/y_{\min} - 1)^3$. The code could use the exact sum (a three-term sum over types) at no cost.
4. **Identifying the mix (18).** Not from the U.S. and the UK, whose taxes are too close; from the cross-section only
   as a calibration. The paper should state $k = 2$ as the assumption and (18) as what nests $k = 1$.
5. **Magnitude.** Still $6.5$–$26$ times the benchmarks at $\rho = 1$ under C. The hurdle supports of about a tenth of
   earnings are the number a referee could ask to see; the frictions literature (Chetty 2012; Gelber, Jones and
   Sacks 2020 — to verify) reports adjustment costs in dollars that could bound $\bar\phi$.
6. **The size loss.** Omitted as C.2 omits its own; a sentence suffices, but a run with $f_0(\tau)$ in the budget would
   show what it does to the tax's response to ageing (it makes a larger system worth less at every design).
7. **CRRA.** The derivation of $f$ is preference-free; P6's positivity holds at $\rho = 0.5$ ($f(0) = 0.80$,
   $1 + 2\ln f = 0.55$); the CRRA recursion is unchanged in form. Not rerun here.
8. **The valuation.** C values the forgone benefit at $R$ and A the wedge at $1/R$, as C.2 does; a retiree's
   marginal valuation differs from a worker's under CRRA. Inherited, not new.
9. **To verify before citing**: Chetty (2012, *Econometrica*); Kleven and Waseem (2013, *QJE*); Gelber, Jones and
   Sacks (2020, *AEJ: Applied*); Ulyssea (2018, *AER*); Browning (1976, *JPE*). None is in
   `notes/paper_costLiterature.md`; the paper's existing citations (Summers, Harberger, Saez, Kleven–Kreiner, Disney,
   Kumler et al.) carry the derivation without them.

## 10. The coauthor's version (`quadratic_cost.pdf`, repo root, untracked; read 2026-11-07)

Proposed edits to sections 7.1–7.3 and appendices B.1, C.2, C.3, G.1, written on the draft of `fa0335f` (10-29).

**The same model.** Their elasticity proportional to the wedge, $\varepsilon(T) = \kappa T$, is A's $F(T) = bT^2$ with
$\kappa = 2b$; their loss $L(T) = \int_0^T s\,\varepsilon(s)\,ds = \kappa T^3/3$ expanded to second order gives
$\lambda = 2\kappa\pi(1-\pi)$, A's $4bu\,\Pi/R$. Same caveats: another tax on the margin adds a $k = 1$ term, unequal
elasticities break the symmetry in Saez's direction, the form is local near flat designs. Checked line by line: the
expansion, the share of revenue, $\lambda$, C.3's conditions (the tax rises with size iff $\ln f > -1$, with the flat
share iff $\ln f > -\tfrac12$), B.1's $u'$ and $u''$, the magnitude $\varepsilon(\bar t) = \lambda\tau/(2\Pi/R)$.

**The accounting, decided: A in the text, C in a footnote.** The only difference is what the budget is charged with:
f, the code and every number are the same, and the implied elasticity is 3.9 under A and 2.6 under C at $\rho = 1$
(0.85 and 0.57 at $\rho = 2$). Section 6's case for C is weaker than stated: (i) section 7.1 calls the cost
*deadweight*, and C charges the whole tax a leaver avoids, of which the part the leaver keeps is a transfer; (ii) C does
not remove C.2's reduced-form footnote, since in the balanced pay-as-you-go budget the benefit a leaver no longer draws
goes to the next period's other retirees, so netting it against contributions lost a period earlier is itself a
booking choice.

**Points for their text** (in order of weight).
1. *The margin* (§9.1). "Or into the formal sector" puts the income tax on the margin: their own footnote 2 then
   gives a $k = 1$ term with weight $t^y$ against $\bar t = 0.047$, about 6 to 1 at $t^y \approx 0.3$; "the part of the wedge
   that the electorate sets" answers which taxes are chosen, not which the margin sees. Name a margin where only the
   pension's wedge moves (covered against uncovered jobs, earnings reported to the agency as in Kumler et al., opting
   out) and drop the formal sector.
2. *Section 7.1's two principles.* The second (the excess burden of a tax depends on the taxes in place) is the
   first-order term, which their C.2 shows cancels; what gives $\tau^2$ is the assumption that the response rises with
   the wedge, under which a single tax's loss is cubic, against the first principle as stated. One principle and one
   stated assumption.
3. *The remainder.* The omitted term is exactly the cubic (11): $-8\%$ at $\theta^\ast = 0.544$, $-18\%$ at $\theta = 0$.
   "[a third]" was computed at $\theta^\ast = 0.728$; at 0.544 the largest implicit tax in absolute value, the lowest
   type's subsidy, is 0.55 of $\bar t$, about a half.
   "As it is under a constant elasticity" fails below $\theta \approx 0.17$, where the lowest type's wedge is negative
   and $\kappa T < 0$ (0.0003 of revenue at U.S. incomes, §9.3).
4. *C.3's "[more] than the 39%".* Less: a flat benefit loses 19.8% at $\rho = 0.5$ under $k = 2$; the draft's sentence
   stands with 19.8% for 26.6%.
5. *$\lambda$ across countries.* Section 7.1 says unchanged, their footnotes 35 and 39 give $2\kappa\pi(1-\pi)$: one of
   the two. $\pi(1-\pi)$ is 0.241–0.250 in 2020 against the U.S. 0.247 (§8.6); the run shows whether it is visible.
6. *The edit map* follows `fa0335f`: $\theta^\ast = 0.728$, 26 countries, the deep test, appendix H, tables 12–16, table 5's
   note with $\omega = 1.29$ and $\varepsilon = 20.01$, footnotes 29–39, C.2's old paragraphs; the content carries over, the
   locations do not, and the bullet on transporting $\lambda$ against $\varepsilon$ is moot.

**Theirs is better on** the timing ($\bar t$ at $\tau_t$, defended by proposition 5's state independence, which settles
§9.2: stationary wedge), the general $L(T)$, the B.1 check, the sample argument (Mexico, Turkey, Korea out) and a full
edit list. **Ours adds** the lemma (4), the omissions measured (cubic $-8\%$, the domain $\theta \ge 0.17$, a size loss
of 5% of revenue their benchmark excludes by definition), the two-hurdle primitive (D) and a number a referee can
check: the share of the base outside the system for its tax component, $b\bar t^2$, about 9% under A (6% under C).

**Their placeholders**, at the branch's U.S. calibration: the multiples of the 0.1–0.4 benchmarks 9.9–39 at $\rho = 1$
and 2.1–8.5 at $\rho = 2$ (A); "[a third]" about a half; footnote 39's path $\Pi/R$ 0.55 to 0.47 with $\pi(1-\pi)$ 0.2475
to 0.249; footnote 35 within 2.5%. The cross-section numbers wait for the run.
