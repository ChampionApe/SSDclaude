# The deadweight cost of section 7: literature, and how the paper motivates it (2026-09-29)

Review note for RKB and MGE, written with the rewrite of subsection 7.2 (`sec:esc`, "Costly redistribution,
and the preferred specification"). §1 states the specification and what it has to be motivated against;
§2 reviews the literature block by block, with what each reference does and how it relates to $f$; §3 maps
the three arguments of $f$ to the references; §4 is the strategy the paper follows. The derivation itself is
in the technical note (`writing/US/model_esc.tex`, "The deadweight cost of redistributive benefits"); the
diagnosis that led to the form is `notes/esc_inequalityChannel.md`.

## 1. The specification, and the objection it has to meet

$$
\nu_t w_t\tau_t h_t\,f(\theta_t,\tau_t)=\sum_i\gamma_i b_t^i,\qquad
f(\theta_t,\tau_t)=\exp\!\Big(-\tfrac12\lambda\,\tau_t\,\tilde V(1-\theta_t)^2\Big),\qquad
\tilde V=\sum_i\gamma_i\frac{(y_i-1)^2}{y_i}.
$$

The claim is that three things raise a loss the model does not otherwise contain: (1) the size of the
system $\tau$, (2) the dispersion of relative incomes $\tilde V$, (3) the flat share $1-\theta$. The
technical note derives $1-f$ as the Harberger loss of the type-specific implicit taxes
$t_i=\Pi\tau(1-\theta)(1-1/y_i)$ of the flat component, summed over types with bases $e_i=y_i$:
$\tfrac12\varepsilon\sum_i\gamma_i y_i t_i^2/(\Pi\tau)=\tfrac12\varepsilon\Pi\tau(1-\theta)^2\tilde V$.

**The objection.** $t_i$ is an *average* implicit tax. In the model the benefit is
$[\theta h_i\eta_i+(1-\theta)h]\bar b$, so the *marginal* benefit per unit of own earnings is $\Pi\tau\theta$
for every type, and the marginal implicit tax of the flat component, $\Pi\tau(1-\theta)$, is the same for
all $i$. That uniform marginal wedge is already in the model (it is $A\tau_{t+1}\Gamma_{s,t}$ in
$\Theta_{h,t}$; hours respond to it through $\xi$), and GHH preferences have no income effects, so the
inframarginal transfers between types distort nothing inside the model. An intensive-margin reading of
$f$ therefore double-counts, and cannot produce $\tilde V$. The motivation has to name margins the model
lacks, on which the average wedge is the relevant one.

## 2. The literature, block by block

### A. The form: quadratic losses that rise with the tax rate

- **Harberger (1964), "The Measurement of Waste", *AER P&P* 54(3):58--76.** The triangle method: a small
  tax $t$ on a base $e$ with compensated elasticity $\varepsilon$ costs $\tfrac12\varepsilon t^2e$, and the
  losses of several taxes add (up to cross effects). As a share of revenue the loss is $\tfrac12\varepsilon t$.
  *Relation.* The whole shape of $f$: quadratic in each wedge, hence in $1-\theta$ (property 3), and the loss
  per unit of revenue linear in the tax rate (property 1). $\tilde V$ is *not* from Harberger. It comes from
  the wedges fed in: type-specific wedges $\propto(1-1/y_i)$ on bases $y_i$ sum to $\tilde V$. The same
  quadratic implies a zero marginal cost of the first unit of redistribution, hence no interior choice can
  reach $\theta=1$ (France; TODO C5).
- **Okun (1975), *Equality and Efficiency: The Big Tradeoff*, Brookings.** The leaky bucket: redistribution
  loses resources in transit, and the leak rises with the amount carried. *Relation.* The plain-language
  version of $f$. The amount a flat component carries is $\propto\tau(1-\theta)\times$ dispersion, so a
  leak convex in it gives all three properties at once without committing to a margin. Also the natural
  frame for C5: Okun's leak can have a component proportional to the amount carried (a linear term).
- **Browning and Johnson (1984), "The Trade-Off between Equality and Efficiency", *JPE* 92(2):175--203.**
  Estimates, on 1976 US microdata, the marginal cost of reducing inequality with a policy whose
  distributional effects resemble the tax-transfer system. The cost is high even for modest elasticities:
  with an economy-wide uncompensated wage elasticity of 0.2, upper-quintile disposable income falls by
  \$9.51 for each dollar gained by the lower quintiles. *Relation.* A quantitative precedent for a leak that is
  large relative to the elasticities behind it, i.e. for the size of $\lambda$ as much as for its shape; and
  for convexity in the amount redistributed, (3) and, through the amount, (2). Not cited in the paper.

### B. Which part of a contribution is a wedge: the tax component

- **Summers (1989), "Some Simple Economics of Mandated Benefits", *AER P&P* 79(2):177--183.** If workers
  value what a payroll charge buys at a fraction $\alpha$ of its cost, labour supply responds only to the
  unvalued part, so the charge distorts like a tax at rate $(1-\alpha)t$ and the wage absorbs the rest.
  Social security is a leading application: the benefit link is why a contribution distorts less than an
  income tax. *Relation.* Source of the concept "tax component". In our formula the linked share is
  $\theta$, so the unvalued share is $1-\theta$; with Harberger that gives (1) and (3). It does not give
  (2): Summers's valuation is marginal and our marginal link is common to all types. And its intensive
  version is already in the model. In the paper: cited for the concept, with the statement that the model
  already contains the intensive-margin distortion.
- **Disney (2004), "Are Contributions to Public Pension Programmes a Tax on Employment?", *Economic Policy*
  19(39):268--311.** Constructs indicators of the tax component of public pension contributions (the part
  not matched by perceived benefit rights) for OECD countries over time, and estimates a cross-country panel
  of age- and gender-specific activity rates. The tax component lowers the activity rates of women; a
  larger retirement-saving component raises them; men's activity does not respond. *Relation.* The
  empirical anchor for (1) and (3) at the country level, and the one cited reference that points at the
  **participation** margin, which the model lacks. It does not speak to (2): the indicators are for
  representative workers, not across the income distribution. Not resolved from the abstract: whether his
  tax component is computed from the marginal or the lifetime-average benefit link. The paper only uses
  Disney for the participation finding, which does not depend on it.
- **Feldstein and Samwick (1992), "Social Security Rules and Marginal Tax Rates", *National Tax Journal*
  45(1):1--22.** The statutory social security tax rate is the same for all earnings up to the cap, but
  the rules linking taxes to later benefits make the *net* marginal tax (contribution minus the present
  value of the marginal benefit accrual) vary substantially across individuals, and some face much lower or
  even negative net marginal rates. *Relation.* A second route to type-specific wedges, at the *intensive*
  margin: actual redistributive formulas are non-linear. Our reading, not a result of the paper: under a
  concave formula such as the US bend points the marginal accrual is higher for low earners, so the net
  marginal tax tends to rise with earnings, the same sign pattern as $t_i$ (a tax above the mean, a subsidy
  below). Our linear
  $\theta$-formula cannot express this, so a loss in $\tilde V$ can be read as the distortion of the
  non-linear marginal wedges that the linear stylisation leaves out. A useful footnote argument if a
  referee presses on the intensive margin; not used in the draft.

### C. The margin on which the average wedge matters: participation

- **Saez (2002), "Optimal Income Transfer Programs: Intensive versus Extensive Labor Supply Responses",
  *QJE* 117(3):1039--1073.** On the extensive margin people compare being in and out of work, so what
  matters is the participation tax (the average tax on the earnings at stake), not the marginal rate. When
  responses are concentrated on the extensive margin the optimal transfer resembles the EITC, with negative
  marginal rates at the bottom. *Relation.* The reason $\tilde V$ is the right aggregator: on a participation
  margin each type's relevant wedge is its average implicit tax, which differs across types exactly as
  $t_i$ does. **Caveat against us:** Saez also shows that where participation is already taxed, lowering
  the participation tax at the bottom *reduces* the total loss. $\tilde V$ counts the subsidy to types
  below the mean as costly as the tax above it, so the symmetry is part of the reduced form, not of the
  derivation. The paper says so in a footnote.
- **Kleven and Kreiner (2006), "The Marginal Cost of Public Funds: Hours of Work versus Labor Force
  Participation", *JPubE* 90(10--11):1955--1973.** Extends the marginal cost of public funds to include
  participation. The efficiency cost of taxation then depends on participation tax rates, i.e. on average
  rates across the earnings distribution, and it is substantially larger than hours-only calculations
  suggest. *Relation.* The formal statement that a Harberger loss on a participation margin is quadratic in
  type-specific average wedges and weighted by each type's earnings, which is the $\sum_i\gamma_iy_it_i^2$
  structure behind $\tilde V$; and that hours-only accounting understates the cost, which is why a cost
  outside the model's hours margin is reasonable.
- **Immervoll, Kleven, Kreiner and Saez (2007), "Welfare Reform in European Countries: A Microsimulation
  Analysis", *Economic Journal* 117(516):1--44.** Uses EUROMOD to measure marginal and participation tax
  rates in the fifteen pre-enlargement EU countries, and a labour supply model with both margins to compare
  raising traditional welfare with introducing in-work benefits. *Relation.* Shows that participation tax
  rates are measurable and differ across the earnings distribution in the countries of our cross-country
  test (the UK and France among them). Optional.
- **Chetty, Guren, Manoli and Weber (2011), "Are Micro and Macro Labor Supply Elasticities Consistent? A
  Review of Evidence on the Intensive and Extensive Margins", *AER P&P* 101(3):471--475.** Micro and macro
  estimates agree on steady-state (Hicksian) elasticities, on both margins, while micro Frisch elasticities
  are an order of magnitude below what business-cycle models need. The steady-state values they propose are
  about 0.25 on the extensive margin and 0.3 on the intensive margin. *Relation.* The magnitude benchmark for $\lambda$ once $f$ is read
  as an extensive-margin loss (replacing the draft's "compensated labor supply elasticities of 0.1 to 0.6",
  an intensive-margin benchmark for a margin the model already has).
- **Retirement as an extensive margin.** Gruber and Wise (eds., 1999), *Social Security and Retirement around
  the World*, University of Chicago Press (NBER): the implicit tax on continued work at older ages,
  summed from the early-retirement age as the "tax force" to retire, approaches or exceeds 100 % in several
  countries, and across countries it is strikingly correlated with low labour-force participation of older
  workers. Liebman, Luttmer and Seif (2009), "Labor Supply Responses to Marginal Social Security Benefits:
  Evidence from Discontinuities", *JPubE* 93(11--12):1208--1223: using discontinuities in the US benefit
  rules, a 10 % rise in the net-of-tax share lowers the two-year retirement hazard by 2.1 p.p. (base 15 %);
  on the intensive margin the evidence is mixed, a significant hours elasticity of 0.41 but no significant
  earnings response. *Relation.* Evidence that workers respond to the tax-benefit link, most clearly on
  the extensive margin. Our two-period model has no retirement margin, so this is a further margin $f$
  stands in for. Not cited in the draft.

### D. Reporting, evasion and formality

- **Kumler, Verhoogen and Frías (2020), "Enlisting Employees in Improving Payroll-Tax Compliance: Evidence
  from Mexico", *REStat* 102(5):881--896.** Matching firms' wage reports to the social security agency with
  workers' survey wages reveals extensive under-reporting. The 1997 pension reform, which tied benefits more
  closely to reported wages for younger workers, reduced under-reporting for younger cohorts relative to
  older ones. *Relation.* Micro evidence that the unlinked share of a contribution erodes the *reported base*,
  so revenue is lost, which is the literal reading of $1-f$ ("revenue that does not reach retirees") and of
  (3). Direction for (2): the tax falls on above-mean earners, who gain most from under-reporting when
  benefits are unlinked. A bridge to the Argentine formality margin of sections 2 to 5.
- **Bergolo and Cruces (2014), "Work and Tax Evasion Incentive Effects of Social Insurance Programs: Evidence
  from an Employment-Based Benefit Extension", *JPubE* 117:211--228.** A Uruguayan reform extended health
  coverage to the dependent children of registered private-sector workers, a benefit conditional on
  registration but not on the earnings reported. Benefit-eligible registered employment rose by 1.6 p.p.
  (about 5 %), and under-reporting of salaried earnings rose by 4 p.p. in small firms. *Relation.* Stronger
  than first noted, and on both sides of the tax component: a benefit that is linked to participation
  draws workers in (the extensive margin responds to the average wedge), while a benefit that is flat in
  reported earnings invites under-reporting of those earnings, the reporting loss that $1-f$ stands for
  and that rises with the flat share, (3). The Latin American companion to Kumler et al., and a candidate
  for the paper next to them.
- **Feldstein (1999), "Tax Avoidance and the Deadweight Loss of the Income Tax", *REStat* 81(4):674--680;
  Saez, Slemrod and Giertz (2012), "The Elasticity of Taxable Income with Respect to Marginal Tax Rates: A
  Critical Review", *JEL* 50(1):3--50.** Feldstein argues that the traditional hours-based analysis greatly
  understates the deadweight loss of the income tax, because higher rates also shift compensation and
  consumption into untaxed forms; measured through the elasticity of taxable income, which collects these
  responses, the loss per dollar of revenue is more than twelve times Harberger's classic estimate, and a
  marginal dollar raised by a proportional rate increase costs nearly two dollars. Saez, Slemrod and Giertz
  review the evidence: "while there are no truly convincing estimates of the long-run elasticity, the best
  available estimates range from 0.12 to 0.40"; they set out when the ETI is a sufficient statistic for
  efficiency. *Relation.* Licence for a single elasticity that aggregates margins the model does not
  contain, i.e. for one $\lambda$, and the second magnitude benchmark. Feldstein is also the closest
  precedent for a deadweight loss an order of magnitude above what hours elasticities imply, which is where
  $\lambda$ sits at $\rho\le1$; the paper could cite him next to the magnitude sentence.

### E. The size of the system and its design

- **Conde-Ruiz and Profeta (2007), "The Redistributive Design of Social Security Systems", *Economic Journal*
  117(520):686--712.** Documents across OECD countries that Bismarckian (less redistributive) systems go
  with larger public pension spending, a smaller share of private pensions and lower income inequality
  than Beveridgean ones. Explains it by a two-dimensional vote over size and redistribution among agents
  differing in age, income and access to capital markets: with three income groups, a small Beveridgean
  system is supported by low-income agents, who gain from its redistribution, and by high-income agents
  (who have a private-saving alternative), against a middle class preferring a large earnings-related one.
  Note the inequality leg: in their data Beveridgean systems go with *higher* inequality, whereas figure 1
  of our paper shows a weak inequality-design relation; worth knowing if a referee cites them on (2). *Relation.* The stylised fact the out-of-sample test targets (the UK small and
  at 0.560, France large and at 1.000). It is the *target*, not the justification: its mechanism is
  political, not a deadweight cost. The high earners' outside option is close in spirit to the
  avoidance/opt-out reading of $f$.
- **Koethenbuerger, Poutvaara and Profeta (2008), "Why Are More Redistributive Social Security Systems
  Smaller? A Median Voter Approach", *Oxford Economic Papers* 60(2):275--292.** (The plan and the 2026-09-24
  log said *JPubE*; the bib's *OEP* is right.) Flat benefits redistribute within a generation and, with
  endogenous labour supply, carry larger efficiency costs than earnings-related ones; the median voter,
  typically middle-aged and high-income in data for eight European countries, resolves this
  efficiency-redistribution trade-off by choosing a smaller system when it is more redistributive.
  *Relation.* Motivates the *interaction* of (1) and (3): each unit of size costs more when the system is
  flat, which is $\tau(1-\theta)^2$ in $\ln f$. Two caveats. KPP's distortion is the uniform intensive
  wedge, which our model contains; and our model without $f$ goes the other way (section 6: moving from
  fully Bismarckian to fully Beveridgean *raises* the tax by 6.2 p.p., the redistributive motive of
  probabilistic voting outweighing the distortion). So $f$ amplifies a channel KPP identify rather than
  adding a new one. Whether the model *with* $f$ reproduces "more redistributive is smaller" in the
  exogenous-$\theta$ comparison has not been measured; do not claim it.
- **Casamatta, Cremer and Pestieau (2000), *Scand. J. Econ.*** Already cited for the benefit formula; no role
  in motivating the cost.

## 3. Map: property to support

| Property of $f$ | Theory | Evidence | Strength |
|---|---|---|---|
| (3) quadratic in $1-\theta$, zero at $\theta=1$ | Harberger; Summers (which part is a wedge) | Disney (participation); Kumler et al. (reporting) | strong in form; zero marginal cost at $\theta=1$ is a property to own (C5) |
| (1) loss per unit of revenue linear in $\tau$ | Harberger | Disney (the tax component's level matters); KPP / Conde-Ruiz--Profeta for the size--design link | strong |
| (2) proportional to $\tilde V$ | Saez; Kleven--Kreiner (average wedges on a participation margin); alternatively Feldstein--Samwick (non-linear marginal wedges) | direct evidence across the income distribution is thin; Kumler et al. in direction | the weakest link; symmetry is an assumption |
| one $\lambda$ for several margins | Feldstein (1999); Saez--Slemrod--Giertz | | adequate |
| magnitude of $\lambda$ | $\lambda\approx\Pi\varepsilon$, $\Pi$ of the order of $\nu_{2020}=1.34$ | $\varepsilon$ 0.1--0.4 (Chetty et al.; SSG) gives $\lambda$ 0.13--0.54 | $\lambda$ = 18.24 / 8.64 / 1.73 at $\rho$ = 0.5 / 1 / 2: roughly 30--140x, 16--65x, 3--13x |

## 4. Strategy for the paper

1. **Lead with the concept, not the formula.** The flat component is a tax (Summers's tax component); the
   cost is the deadweight loss of that tax. One sentence, two citations (Summers, Disney).
2. **Say what the model already has, and what $f$ adds.** The intensive-margin distortion of the tax
   component is in the model (the contributive share raises the return to an hour). $f$ stands for the
   margins the model lacks and on which the evidence finds the tax component to bite: participation
   (Disney) and the reporting of earnings (Kumler et al.). This removes the double-counting objection before
   it is raised.
3. **Derive $\tilde V$ from the margin.** On participation and reporting margins the relevant wedge is the
   average tax (Saez; Kleven--Kreiner); the flat component's average implicit tax differs across types; the
   Harberger triangles sum to $\tfrac12\varepsilon\tau(1-\theta)^2\tilde V$. Then list the three arguments
   of $f$ as consequences of the derivation, not as choices.
4. **Tie size to design through the literature the paper already cites.** KPP's efficiency-redistribution
   trade-off, read from the other side, and Conde-Ruiz--Profeta's fact as the target of the cross-country
   test.
5. **Own the two soft spots in footnotes, as choices with their cost.** The symmetric treatment of the
   subsidy below the mean (Saez), and the return factor absorbed into $\lambda$. The zero marginal cost at
   $\theta=1$ already has its sentence in the across-countries paragraph.
6. **Be exact about magnitude.** Shape from the theory, size from the calibration: $\lambda$ is more than an
   order of magnitude above what participation and taxable-income elasticities (0.1 to 0.4; Chetty et al.,
   Saez--Slemrod--Giertz) imply at $\rho\le1$, a few times above at $\rho=2$, and absorbs administrative,
   evasion and political costs. The $\rho=2$ proximity is a mild further argument for $\rho\in[1,2]$.
7. **Keep the paper's derivation to one paragraph** and send the rest to the technical documentation, which
   should then take the same extensive-margin framing (its "Harberger loss" paragraph still reads as a
   compensated-elasticity argument; follow-up).

## 5. Status

Subsection 7.2 rewritten along §4 on 2026-09-29 (`writing/Paper/Sections/EndogenousTheta.tex`; six
references added to `References.bib`: Harberger64a1, Saez02a1, KlevenK06a1, ChettyGMW11a1, SaezSG12a1,
KumlerVF20a1). The technical note's cost paragraph (`writing/US/model_esc.tex`) reframed the same day. Every
reference above was checked against its publisher or RePEc record on 2026-09-29; the details in §2 are
from those records, and the one point not resolved from an abstract (how Disney computes his tax
component) is flagged where it sits. Candidates for the paper if the argument needs more support:
Bergolo and Cruces (2014) next to Kumler et al., and Feldstein (1999) next to the magnitude sentence.
