# Social Security Design and Its Political Support

**Date**: 10/22/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper builds an OLG model with capital, households that differ in productivity and turnout, an informal sector, and probabilistic voting. It uses the model to study how two features of pension design affect the equilibrium social security tax: coverage (contributive vs. universal, $\epsilon$) and the earnings link ($\theta$). Under log-GHH preferences with hand-to-mouth informal households, the tax depends only on parameters and demographics (Proposition 2), and a more Bismarckian formula lowers it. Calibrated to Argentina, a rise in $\epsilon$ produces about three quarters of the observed spending increase. Calibrated to the U.S., UK and France, ageing ranks first among the determinants of spending and the earnings link second. When voters also choose $\theta$, costless redistribution produces the Beveridgean corner (Proposition 3). A reduced-form deadweight cost, calibrated to the U.S. design, yields interior designs that become more Bismarckian with ageing.

The paper adds a two-dimensional pension design to the tractable Markov framework of Gonzalez-Eiras–Niepelt and Song, and it keeps closed forms despite within-cohort heterogeneity and informality. Proposition 3, with its Chebyshev argument, is clean, and the documentation and online material are unusually thorough. The weak points are elsewhere. The main design results lean heavily on the aggregation rule and on a reduced-form cost calibrated to a single moment. The two empirical 'validations' do less than claimed. Several proofs and numerical claims need tightening before the conclusions about Figure 1.1 can be credited.

**The design results follow from near-utilitarian aggregation within the retired cohort**

Section 2.5 makes political responsiveness vary only by age ($\omega$) and by turnout ($\mu_j$). Within a cohort, $W_t$ is therefore a turnout-weighted utilitarian sum of log utilities. Any budget-neutral transfer toward poorer retirees raises it. Proposition 3 is then close to a restatement of concavity. The 'distinct contribution' of Proposition 2, that higher $\theta$ lowers the tax, has the same source: moving revenue toward agents with low marginal utility lowers the aggregate marginal value of revenue. This matters for how the paper positions itself against Conde-Ruiz and Profeta (2007). Their inequality prediction comes from coalition formation under majority voting, and the present aggregation rules that mechanism out by construction. Finding that the data contradict their prediction is therefore not evidence for this model's mechanism. In the probabilistic-voting tradition (Lindbeck–Weibull, Persson–Tabellini), group weights are swing-voter densities, and these are often allowed to vary with income, for example a more responsive middle class. The paper should say plainly that the Beveridgean corner and the sign of $\partial\tau/\partial\theta$ are properties of equal within-cohort responsiveness. Appendix C.1 already gives the threshold, $\mu_i/\mu_j < c^i_{2,t}/c^j_{2,t}$. A short calculation of how steep an income gradient in responsiveness $\psi_i$ (separate from turnout) must be to overturn Proposition 3 and the $\theta$ comparative static, set against available estimates, would show readers how general the results are.

**Proposition 2's comparative statics hold the predetermined savings distribution fixed and omit a needed condition**

Proposition 2 is stated for equilibrium taxes. Appendix B.1, however, signs the effects of $\theta$, inequality and $\epsilon$ 'with $s_{t-1,i}/s_{t-1}$ and $\Theta_{h,t}$ held fixed.' In Section 3, $\theta$ and $\epsilon$ are permanent parameters, so changing them also changes the current retirees' savings distribution through (13). By part iv of Proposition 1, a lower $\theta$ widens savings dispersion. By the same marginal-utility logic this probably pushes the tax further up, so the sign for $\theta$ may well survive, but the proof does not show it. For $\epsilon$, whose sign is already ambiguous through condition (B.5), the omitted channel could change the answer. The inequality result is proved for two types 'without loss of generality' and ends with 'it is now straightforward to show.' That is not an argument for $J$ types, and the mean-preserving shift in $\eta_H,\eta_L$ also moves $s_{t-1,m}/s_{t-1}$. Separately, the sign of $\partial\tau_t/\partial\nu_t$ in B.1 requires $\sum_{i>0}\gamma_i E^i_{2,t}>0$ at the optimum, a condition that does not appear in the proposition. The authors should take one of two routes. They can restate Proposition 2 as a result about the tax given the inherited distribution. Or they can extend the proof to the stationary fixed point where $s_{t-1,i}/s_{t-1}$ is consistent with $(\theta,\epsilon,\tau)$. In either case they should add the $\nu_t$ condition to the statement. A $J$-type proof for $\theta$ and inequality along the lines of the Chebyshev step in Proposition 3 looks feasible.

**Equilibrium selection, uniqueness and horizon sensitivity are not documented**

Section 4 handles the dependence of retirees' savings distribution on $\tau_t$ in two steps. It solves the tax first-order condition with that distribution held fixed, then imposes consistency. This is a fixed point between the tax and the expectations embedded in past savings, and it is a natural source of self-fulfilling multiplicity. If the old expected a higher tax, savings are more dispersed and poor retirees are poorer, which raises support for a high tax. The only evidence on uniqueness is footnote 12: exactly one candidate passes 'at every state and date of every solve that records the count.' Readers cannot tell how many solves do not record it. The appeal to the uniqueness result of Gonzalez-Eiras and Niepelt (2008) does not carry over, because their environment lacks within-cohort heterogeneity, informal savers and a design choice. The horizon is also short in model time. With thirty-year periods, $T=2200$ is six periods after 2020. The claim that finite- and infinite-horizon solutions 'agree away from $T$' needs evidence in the CRRA and informal-savings cases, where strategic effects run through the state. The revision should include:
- a table of 2020 and 2050 outcomes under several $T$ (e.g., 2140, 2200, 2290) and under the steady-state terminal condition of Appendix D;
- accuracy checks on the numerically differentiated continuation policies, such as first-order-condition residuals off the grid;
- the share of solves for which the candidate count was recorded, with the count.

**The Argentine exercise compares a political response with an accounting cost**

In Table 2 the 'Economic Equilibrium' column holds $\tau$ fixed. With a balanced budget, covering informal retirees is then financed by cutting formal benefits. All of the model's spending increase (2.1 p.p. of tax, 1.4% of GDP) is the endogenous political response. The 1.8% of GDP from Cetrángolo and Grushka is a different object: the fiscal cost of new beneficiaries paid at statutory minimum pensions. The 'three quarters' figure is really the share of the expansion financed by higher taxes rather than by cuts to existing pensions, and the paper presents no data on that split. Four further points need reconciling.
1. $\gamma_0=0.47$ is set from the 32% of elderly *without* a pension, yet informal retirees in the model already receive $\epsilon=0.21$ before the reform. That value is the basic pension for those with 10–30 years of contributions. If the 32% received nothing, the shock is a jump from 0 to $\epsilon^U\approx 0.55$, not from 0.21. I compute $\epsilon^U = 0.16+0.84\times 0.47\approx 0.55$ from Appendix E.2.
2. The pre-reform target is 2000–01 spending of 7.1% of GDP, but spending was 5.2% in 2005 when the amnesties began.
3. The 2008 nationalization of funded accounts (footnote 13) moved contributors and revenue into PAYG within the same window.
4. A thirty-year model period is being compared with a five-year change.
The authors should report the implied change in formal benefits in Table 2. They should redo the reform with pre-reform $\epsilon=0$ and with a 2005 spending base. The 1.8% comparison should be presented as one moment among several, not as validation.

**The cost of redistribution is a one-moment fit whose functional form builds in much of the ageing result**

$\lambda$ is exactly identified by the U.S. design in 2020, so the endogenous-design model fits the U.S. by construction. Table 4 and Appendix C.2 show that the calibrated $\lambda$ exceeds what participation and taxable-income elasticities imply by more than an order of magnitude at $\rho\le 1$. The gap is attributed to administrative, evasion and political costs. That attribution names a residual; it does not supply a mechanism. Two specification choices then shape the headline prediction that ageing makes the design more Bismarckian.
- The loss share is linear in $\tau_t$. Footnote 25 reports that this channel supplies about half of the design response to ageing.
- The PAYG return factor $\Pi_t$, which carries $\nu_t$, is absorbed into $\lambda$ (footnote 29). The paper itself notes that keeping $\Pi_t$ would make the cost grow less as the population ages.
The out-of-sample check is thin. No $\lambda$ reproduces France, and under the U.S. $\lambda$ France's chosen design (0.749) exceeds the U.S. value by only 0.011. The UK is predicted at 0.625 against an observed 0.560. The three targets are also not measured alike. The U.S. $\theta^*$ and $\tau$ include Medicare as a flat benefit, while France and the UK exclude health spending, so the calibration target and the cross-country test use differently defined designs. The revision should:
- move the ageing response under the $\Pi_t$-inclusive cost and under the design-level cost $f(\theta)=\phi+(1-\phi)\theta^p$ into the main text;
- recalibrate the U.S. without Medicare;
- add a linear term to the cost so France's corner is attainable, then check whether one parameter pair fits all three countries.

**The account of Figure 1.1 is qualitative, and the model's direct effect runs against the correlation it seeks to explain**

Figure 1.1 motivates the paper with three facts: spending and the Bismarckian index rise together, both rise as population growth falls, and neither is related to inequality. In the model, holding demography fixed, a more Bismarckian design lowers the tax (Proposition 2). Moving from $\theta=1$ to $\theta=0$ raises the tax by 6.2 p.p. at $\rho=1$. The positive cross-country correlation therefore has to come entirely from ageing moving both variables, and it has to outweigh this direct negative effect. Yet along the projected U.S. demography the chosen design moves only from 0.738 to about 0.81 (Appendix G.2). The OECD cross-section spans roughly 0.5 to 1.0. It is not shown that the model can produce the slope of the index on population growth seen in the data. The 'unrelated to inequality' claim rests on a design response whose sign flips with $\rho$ (Section 7.2). That shows the model is agnostic about the sign; it does not show the model predicts a zero correlation. The natural test is to feed the 29 countries' population growth and income distributions, or a grid spanning them, into the calibrated model with endogenous design. The paper should then report the implied regressions of spending and $\theta$ on population growth and the Gini next to the data slopes. Without this exercise, the claimed fit to Figure 1.1 remains suggestive.

**The ranking of determinants depends on the IES, and GHH is never relaxed**

The abstract ranks ageing first and the earnings link second as determinants of spending. Section 6, however, reports that the design effect falls from 9.0 p.p. at $\rho=0.5$ to 1.5 p.p. at $\rho=2$. At $\rho=2$ this is in the range of the inequality (1.2 p.p. at $\rho=1$) and voting (0.9 p.p., with an IES pattern reversed) effects. $\lambda$ also varies roughly tenfold across $\rho$ (Table 4). A table of every counterfactual at every $\rho$ is needed before the ranking can be asserted. Section 5 favours $\rho\in[1,2]$ because Gonzalez-Rozada and Ruffo find that savings fell. This criterion does not discriminate, because Figure 5.2 shows the savings response at $\rho<1$ is dampened, not reversed. More fundamentally, every quantitative exercise keeps GHH, which removes income effects on hours. Two channels depend on that choice: the retirees' stake in an earnings-related design (the first force in Section 7.2) and the hours responses in Figure 6.1. The evidence on pensions and labor supply points to meaningful income effects. One quantitative check would settle whether the main comparative statics are GHH artifacts. The authors could rerun the U.S. design counterfactual and the ageing-to-$\theta$ response under separable or King–Plosser–Rebelo preferences, even if closed forms are lost.

**The universal-pension dimension is never chosen politically**

The paper's stated contribution is a pension system that differs in two dimensions, coverage $\epsilon$ and the earnings link $\theta$. Yet Section 7 endogenizes only $\theta$, and the Argentine coverage expansion enters as an exogenous jump of $\epsilon$ from 0.21 to $\epsilon^U$. Section 5 calls Argentina "the case in which the design changed", but the model never asks whether its electorate would support that change. This matters for a paper about the political support of design. Within the model, the amnesties could have been a political equilibrium outcome or a departure from one, and the two readings have different implications for the 2005–2010 episode. The hand-to-mouth case looks tractable for this question. Proposition 2 already makes the tax state-free given $\epsilon$, so one can trace $W_t(\epsilon, T_t(\epsilon))$ over a grid of $\epsilon \in [0, \epsilon^U]$ at the Argentine calibration, chosen one period ahead as in Section 7. The authors should report whether the maximizer lies near 0.21, near $\epsilon^U$, or at a corner, and how the answer moves with $\gamma_0$ and the informal endowment $\chi$. Even a negative finding would tell readers which half of the two-dimensional design the political mechanism can explain.

**No closed-form special case recovers the earlier log-GHH tax**

Section 1 and Section 3.2 place Proposition 2 alongside Gonzalez-Eiras and Niepelt (2008), Song (2011) and Uchida and Ono (2024). The paper says the equilibrium tax is "a function of parameters and demographics alone", but it never writes that function down, even for the simplest case. The paper should verify that with $J=1$, $\gamma_0=0$ (so $\theta$ and $\epsilon$ drop out) and $\mu=1$, the first-order condition built from (B.2)–(B.4) reduces to the known representative-agent tax formula of Gonzalez-Eiras and Niepelt (2008). This check is cheap. It also confirms that the heterogeneous-agent extension nests the benchmark it claims to generalize. A second worked case would help readers calibrate intuition: $J=2$ types with equal $\mu$ and equal $\gamma$, and $\epsilon=0$, so that $\tau^*$ can be plotted against $\eta_H/\eta_L$ for $\theta \in \{0, 0.5, 1\}$ at the U.S. values of $\alpha$, $\xi$, $\beta$ and $\nu$. That figure would show the size of the inequality and earnings-link effects of Proposition 2 before any calibration. Readers could then judge how much of the Section 6 results comes from the mechanism and how much from calibrated $\omega$ and $X$.

**The ambiguous sign of the universal-pension effect is never shown to bite**

Proposition 2 and condition (B.5) state that a more universal pension can raise or lower the tax. The paper exhibits only the positive case, Argentina (including the hand-to-mouth check in footnote 16). An ambiguity result is informative only if both signs occur in admissible regions of the parameter space. The paper should report the two sides of (B.5) at the Argentine calibration. These are $\frac{\phi_t}{\epsilon}\sigma^0_t(1-\sigma^0_t)$ and $\sum_{i>0}\gamma_i\sigma^i_t(1-\sigma^i_t)$, together with the implied $\sigma^0_t$ and $\sigma^i_t$, so readers can see how far Argentina is from the boundary. It should also exhibit a fully specified economy where the sign flips. One option is to raise the informal old-age endowment $\chi$ until informal retirees are richer than the lowest formal type. Another is to push $\epsilon$ toward $\epsilon^U$, where $\sigma^0_t$ approaches one. A one-panel figure of $\partial\tau/\partial\epsilon$ over $(\chi, \epsilon)$ would make the abstract's conditional claim ("if informal retirees are poorer ... and the pension a comparable share") concrete. It would also tell readers whether rich-country extensions, such as platform workers mentioned in the conclusion, fall on the same side.

**CRRA policy functions and the strategic channel are never displayed**

Readers will want to see what the CRRA extension adds. The introduction states that under CRRA the state space reduces to a single aggregate state, $s_{t-1}$. It also says that once the state matters, the current tax moves future policy through the continuation function. Yet the paper never shows the policy function $\tau_t(s_{t-1})$ or the size of the strategic term $\partial\tau_{t+1}/\partial s_t \cdot ds_t/d\tau_t$. Without this, readers cannot tell whether the dynamic political-economy channel matters quantitatively or whether CRRA mainly rescales marginal utilities. That distinction bears on Section 6's claim that a higher IES "changes only the size of the earnings-link effect." The paper should plot $\tau_{2020}(s_{2019})$ at $\rho \in \{0.5, 1, 2\}$ for the U.S. calibration over a range of capital stocks. It should also decompose the 2020 tax into what a voter who ignores the state-to-policy feedback would choose and the full Markov choice. Footnote 11 already gives a related number for time-invariant policies, so the same machinery should deliver this decomposition with little extra work.

**Recommendation**: Major revision. The analytical framework is sound in its core and well executed, but the main claims go beyond what is established. The design results are largely consequences of the aggregation rule and of a reduced-form cost fitted to one moment. The Argentine comparison does not measure what it is presented as measuring. The fit to the motivating cross-country facts is asserted rather than demonstrated. Proposition 2's proof and the equilibrium-uniqueness claims also need work.

**Key revision targets**:

1. Simulate the calibrated endogenous-design model over the range of population growth and inequality in the 29-country sample, and report model-implied versus data slopes of spending and the Bismarckian index on population growth and the Gini.
2. Report how the ageing-to-design result changes when the cost keeps $\Pi_t$, when the cost is on the design itself, and when a linear term is added, and recalibrate the U.S. target without Medicare so that all three countries use the same definition of $\theta$.
3. Rework the Argentine exercise: report the implied change in formal benefits, reconcile the pre-reform $\epsilon=0.21$ with $\gamma_0$ defined as the elderly without a pension, and show results with a 2005 spending base.
4. Complete the proof of Proposition 2, either for the stationary fixed point in the savings distribution or restated conditional on it, with a $J$-type argument for $\theta$ and inequality and the $\nu_t$ condition added to the statement.
5. Document equilibrium uniqueness and horizon independence: candidate counts for all solves, results under alternative $T$ and the steady-state terminal condition, accuracy diagnostics, and a table of all counterfactuals at each $\rho$, including one non-GHH check.

**Status**: [Pending]

---

## Detailed Comments (25)

### 1. The sign of the θ effect is not settled by the marginal-utility argument

**Status**: [Pending]

**Quote**:
> marginal utility of poor households, higher _θ_ then lowers equilibrium tax rates.

**Feedback**:
This is the step behind the paper's self-described distinct contribution, and the paper's own expressions do not support it.

Start from B.1, which gives $E^i_{2,t}=(\phi_t\sigma^i_t-(1-\phi_t)(1-\sigma^i_t))/\tau_t=(\sigma^i_t-1+\phi_t)/\tau_t$. Neither $\phi_t$ nor the young's terms in (B.4) depend on $\theta$. So the sign of $\partial\tau/\partial\theta$ is the sign of $\sum_{i>0}\mu_i\gamma_i\,\partial\sigma^i_t/\partial\theta$.

Write $x_i=s_{t-1,i}/s_{t-1}$, $p_i=1+\theta(y_i-1)$ and $A=\frac{1-\alpha}{\alpha}\frac{\tau_t}{1+\gamma_0\epsilon}$, so that $\sigma^i=Ap_i/(x_i+Ap_i)$. Holding $x_i$ fixed gives
$$\partial\sigma^i/\partial\theta=A(y_i-1)x_i/(x_i+Ap_i)^2.$$
The relevant weight is therefore $x_i/c_i^2=\sigma^i(1-\sigma^i)/b^i$, not $1/c_i$. Because $x_i$ rises with income, it can outweigh the fall in $1/c_i^2$.

A concrete case:
- Equal $\mu$, two equal-mass types with $y\in\{0.5,1.5\}$, $\theta=0$, $\beta=1$, $A=1$ (roughly $\tau\approx0.43$ at $\alpha=0.3$).
- Savings from (13) give $x=\{0.25,1.75\}$ and $c=\{1.25,2.75\}$.
- The sum is $\tfrac12(-0.08+0.116)>0$, so taxes rise with $\theta$.
- At $A=0.5$ the sign turns negative.

The gap survives either convention for savings. Letting $x_i$ move with $\theta$ through (13) changes the numerator to $A(1+\kappa)(y_i-1)y_i$, which is still not common across types.

The proof also mixes conventions. The inequality step lets $x_m$ move with $\eta_m$, which is where its factor $(1-\theta)(1+\ldots)$ comes from. The $\theta$ and $\epsilon$ steps hold $x_m$ fixed.

Section 3.2 repeats the marginal-utility story. That sits awkwardly next to the $\epsilon$ explanation a few lines later, which correctly reasons through pension shares.

Requested changes:
- Add to Proposition 2 the condition $\sum_{i>0}\mu_i\gamma_i(y_i-1)x_i/(c^i_{2,t})^2<0$. For two types this is $c^H_{2,t}/c^L_{2,t}>\sqrt{x_H/x_L}$.
- Verify that the condition holds at each calibration. The Section 6 numbers suggest it does; the general statement is what needs repair.

---

### 2. Aggregate savings fall is compared with a household-level estimate

**Status**: [Pending]

**Quote**:
> average workweek by a quarter of an hour, the fall in savings in line with the estimate of

**Feedback**:
Table 2 shows that at fixed taxes the reform raises the savings rate, from 14.40% to 14.73%. The entire 0.43 p.p. fall in the 'Full effect' column therefore comes from the political tax increase.

An estimate of the amnesty's effect on saving that compares eligible with ineligible households would difference out an economy-wide tax change. That is how such estimates are usually identified, and the authors should state how Gonzalez-Rozada and Ruffo identify theirs. If it is of that kind, the matching model object is the saving response of newly covered informal households. Figure 5.2 reports this as a 5.7–5.8 p.p. fall in the informal savings ratio. The aggregate savings-to-GDP ratio is the wrong object.

This matters for two reasons:
- Matching the aggregate number says little about the political channel the comparison is meant to support.
- The same comparison is later used to select $\rho\in[1,2]$.

State their estimate in its own units and for its own population, and compare it with the model response for that group.

---

### 3. Spending-to-tax conversion assumes GDP equals formal output

**Status**: [Pending]

**Quote**:
> rate of 10.9%, which is pension spending of 7.1% of GDP before the 2001 crisis divided by

**Feedback**:
The arithmetic is right: $7.1/0.65=10.9\%$, and $2.1\times0.65\approx1.4\%$ of GDP. Both steps, though, treat national-accounts GDP as formal output. Appendix E.3 itself argues that measured GDP includes informal mixed income. That argument is how the paper justifies lowering $\alpha$ to 0.35.

If a share $y$ of GDP is informal, the tax target becomes $0.071/(0.65(1-y))$. The model's tax rise then converts to $2.1\times0.65\times(1-y)$ of GDP. Using the paper's own range:
- At $y=0.05$ (the survey estimate), the target is about 11.5%, and the rise is about 1.30% of GDP, or 72% of 1.8%.
- At $y=0.2$ (shadow-economy estimates), the rise is about 1.09%, or 61% of 1.8%.

The 'three quarters' headline depends on this choice. The savings rate 'relative to GDP' in Table 2 has the same ambiguity. Say which GDP concept the model and the data denominators use. Rescale the 10.9% target, and with it $\omega$, if they differ.

---

### 4. Which savings distribution is used at the date of the surprise reform?

**Status**: [Pending]

**Quote**:
> Table 2 reports the effect in 2010 of an unanticipated and permanent rise

**Feedback**:
Section 4 reduces the state space by replacing the inherited savings distribution with 'the one consistent distribution for each candidate tax'. That is valid on an equilibrium path. At an unanticipated change in $\epsilon$ it is not.

Retirees in the reform period saved expecting pre-reform benefits. Their distribution, and especially $s_{t-1,0}/s_{t-1}$, is therefore predetermined at its pre-reform value. Making it consistent with the post-reform tax would credit informal retirees with savings decisions they never made. That moves exactly the marginal-utility weights that drive the 2.1 p.p. response.

State which distribution enters the 2010 tax condition in Table 2. If it is the post-reform-consistent one, report the result with the inherited pre-reform distribution, and apply the consistency step only from the next period on.

---

### 5. The two forces described cannot by themselves flip the inequality effect on the design

**Status**: [Pending]

**Quote**:
> calibrated cost parameter is largest (table 4), and the first at high elasticities, where the

**Feedback**:
A stylized local check suggests the stated mechanism does not produce the reported sign pattern.

Take retirees with log utility over $\theta y_i+1-\theta$. The marginal redistributive gain of flattening at $\theta=1$ is $\sum_i\gamma_i/y_i-1$. Because $\sum_i\gamma_i y_i=1$, this equals $\tilde V$ exactly. The marginal cost in (16), $\lambda\tau\tilde V(1-\theta)$, is also proportional to $\tilde V$.

So halving $\tilde V$ from 0.436 to 0.218 scales the first and second forces down together. Their balance stays put. The only change is that the labor-supply stake, which the text says is independent of dispersion, gains relative weight. That pushes toward Bismarck at every $\rho$.

The level of $\lambda$ cannot explain the Beveridgean move at $\rho=0.5$. At an interior optimum, marginal cost equals marginal gain net of the labor stake whatever $\lambda$ is.

Something else produces the flip. Candidates include:
- curvature away from $\theta=1$ under CRRA, where the gain is no longer proportional to $\tilde V$;
- type-specific turnout weights;
- price effects.

Naming the term matters because the paper uses this sign pattern to argue that inequality and design are unrelated.

---

### 6. The reporting margin calls for a marginal wedge, which the cost omits

**Status**: [Pending]

**Quote**:
> participation, formality and the reporting of earnings, on which the average wedge is the

**Feedback**:
The participation argument is sound. A worker deciding whether to enter the formal system compares total earnings with what they buy, so the average wedge $t_i$ in (15) is the right object.

Under-reporting of wages (Kumler et al., one of the two pieces of evidence cited) is an intensive choice: how much to report. One more reported peso raises the benefit by $\Pi_t\tau_t\theta_t$. The marginal wedge $\Pi_t\tau_t(1-\theta_t)$ is therefore common across types and does not vanish when incomes are equal.

At $\theta=0$ with equal incomes, the incentive to under-report is strongest, yet $\tilde V=0$ and $f=1$. Appendix C.2 says the marginal wedge is already in the model through hours. That is a different margin, governed by the Frisch elasticity, not by a reporting elasticity.

Narrow the claim to participation and formality. Alternatively, add a term in $(1-\theta_t)^2$ that does not scale with dispersion and check what it does to the calibrated $\lambda$ and the ageing response.

---

### 7. The small loss at the observed design is mechanical; the marginal loss is not small

**Status**: [Pending]

**Quote**:
> at the calibrated design, the loss amounts to a relatively small share of revenue, no more

**Feedback**:
Table 4 satisfies $-\ln f(\theta^*)=(1-\theta^*)^2[-\ln f(0)]$ with $(1-0.738)^2=0.0686$. At $\rho=1$, $0.272\times0.0686=0.0187$, which is the reported 1.8%. The same check reproduces 3.9% and 0.4%. The low level therefore follows from the quadratic form and from $\theta^*$ being near one. It says little about how hard the cost bites, because the calibration pins down the marginal cost.

The marginal cost is large at low elasticities:
- At $\rho=0.5$, lowering $\theta$ by 0.1 raises the loss from 3.9% to $1-e^{-0.131\times0.5745}\approx7.3\%$ of revenue.
- At $\rho=2$ the same move takes it only from 0.4% to about 0.7%.

Report the marginal figures alongside the levels so readers can judge the strength of the calibrated cost.

---

### 8. Turnout threshold for the corner depends on the IES

**Status**: [Pending]

**Quote**:
> preferences at every intertemporal elasticity: the design still enters only the consumption

**Feedback**:
The CRRA extension is correct, but the threshold changes with it.

Under CRRA, $c^i_{2,t}=KD_i$ with $K$ common to all types. The Chebyshev weights become $b_i=\mu_iD_i^{-1/\rho}$. These are ordered opposite to $y_i$ if and only if $\mu_i/\mu_j<(c^i_{2,t}/c^j_{2,t})^{1/\rho}$.

The condition stated just before, that turnout rises 'by proportionally less than consumption', is therefore the log case only. Compared with log preferences:
- At $\rho=2$ the bound is the square root of the consumption ratio, which is stricter.
- At $\rho=0.5$ it is the square, which is looser.

This matters because U.S. turnout rises with income in the calibration and Section 7 reports results at $\rho=2$. Add the $\rho$-dependent threshold after 'takes the place of $\mu_i/D_i$'.

---

### 9. A zero marginal cost at θ=1 does not rule out the Bismarckian corner

**Status**: [Pending]

**Quote**:
> electorate chooses the Bismarckian corner, which is why France’s design has no own cost

**Feedback**:
The derivative is right: $\partial\ln f/\partial\theta_t=\lambda\tau_t\tilde V(1-\theta_t)$, which vanishes at $\theta_t=1$. What follows is narrower than the sentence says. The cost can never push an electorate to $\theta=1$. An electorate that already prefers the corner without the cost still chooses it.

The paper's own Appendix C.1 has such a case. Under CRRA with a once-and-for-all choice, the electorate picks $\theta=1$ at high intertemporal elasticities.

Rewrite as 'a purely quadratic loss can never by itself take an electorate to the Bismarckian corner'. That is also the reading the France result needs: at $\theta=1$, $f=1$ and $\lambda$ has no bite, so France's corner has to come from political forces.

---

### 10. Verbal reading of (B.5) drops the factor $\phi_t$

**Status**: [Pending]

**Quote**:
> holds when informal retirees are poorer than formal ones and the pension is a comparable

**Feedback**:
(B.5) itself checks out. The verbal summary does not quite follow from it.

Set $\sigma^0=\sigma^i=\sigma$ and use $\sum_{i>0}\gamma_i=1$. The condition reduces to $\phi_t/\epsilon>1$. With equal shares, $c^0_{2,t}/\bar c_{2,t}=b^0_t/\bar b_t=\epsilon$, so 'poorer' only means $\epsilon<1$. On the band $\phi_t<\epsilon<1$, informal retirees are poorer and hold a comparable share, yet taxes fall with $\epsilon$.

The band is narrow. At the Argentine values ($\alpha=0.35$, $\xi=0.3$, $\tau=0.109$), $\phi_t\approx0.98$. It is still a gap in a statement that appears in the abstract and the conclusion. Rewrite as 'poorer than formal ones by more than the marginal-revenue factor, $c^0_{2,t}/c^i_{2,t}<\phi_t$, at comparable pension shares'.

---

### 11. Monotonicity in (C.9) needs conditions, and one fails at the calibration

**Status**: [Pending]

**Quote**:
> rising with the flat share, the dispersion of incomes and the size of

**Feedback**:
Let $g=f\lambda\tilde V\tau x$ with $x=1-\theta_{t+1}$ and $\ln f=-\tfrac12\lambda\tilde V\tau x^2$. Differentiating:
$$\partial g/\partial\tau=\lambda\tilde Vxf(1+\ln f),\qquad \partial g/\partial\tilde V=\lambda\tau xf(1+\ln f),\qquad \partial g/\partial x=\lambda\tilde V\tau f(1+2\ln f).$$

The conditions behave differently:
- The first two need $\ln f>-1$. This plausibly holds at any interior tax, since the same factor multiplies the retirees' benefit term in (C.8).
- Monotonicity in the flat share needs $\ln f>-\tfrac12$, which is strictly stronger.

The second condition fails inside the paper's own calibration. At $\rho=0.5$, Table 4 gives $1-f(0)=43.7\%$ at the 2020 tax, so $\ln f(0)=-0.575$. Near flat designs, the marginal gain from a more Bismarckian design then falls with the flat share.

State both conditions after (C.9), and qualify the sentence accordingly.

---

### 12. $b_t$ is a pension rate, not the average formal pension

**Status**: [Pending]

**Quote**:
> sures how Bismarckian are the benefits of formal workers, and _bt_ is the average formal

**Feedback**:
Sum (8a) over $i>0$ with $\sum_{i>0}\gamma_i=1$. This gives $\theta h_{t-1}b_t+(1-\theta)h_{t-1}b_t=h_{t-1}b_t$. The average formal pension is therefore $h_{t-1}b_t$, and $b_t$ is benefit per unit of past average effective labor. This is what the label 'average pension rate' at (8c) suggests, and the two descriptions in the same section disagree. Relabel $b_t$ at its definition.

---

### 13. The model's θ and the OECD index in Figure 1.1 are different scales

**Status**: [Pending]

**Quote**:
> earnings-related one, the weight of the second being the Bismarckian index, and informal

**Feedback**:
The introduction defines the Bismarckian index as the ratio of replacement rates at mean and half-mean earnings. Under (8a) with incomes at exactly 1 and 0.5, that ratio is $I=1/(2-\theta)$. It coincides with $\theta$ only at the corners.

The calibration handles this correctly: Appendix E.2 inverts the replacement-rate ratio using model incomes. The text, however, calls $\theta$ 'the Bismarckian index', and Figure 1.1's axis is $I$. The difference matters when model results are read against the figure:
- U.S. $\theta^*=0.738$ corresponds to $I\approx0.79$.
- The UK's 0.56 corresponds to $I\approx0.69$.
- The projected rise in $\theta$ from 0.738 to 0.809 is only about 0.05 on the index scale.

State the mapping. Express model design changes in index units wherever they are compared with the OECD cross-section.

---

### 14. Leisure counterfactual is ranked first but absent from Figure 6.1

**Status**: [Pending]

**Quote**:
> The workweek panel ranks the determinants differently. France’s leisure preferences

**Feedback**:
The text lists five rows: design, population growth, income distribution, leisure preferences and voting. Figure 6.1 shows four, and the leisure row is missing. Yet leisure is the effect the paragraph ranks first for hours.

Its size is also unlikely to fit the plotted axis. With rates unchanged, rescaling $X$ from 4.03 to 7.27 at $\xi=0.3$ multiplies hours by $(4.03/7.27)^{0.3}\approx0.84$, a fall of about 16%. The hours axis stops at $-4$.

Add the row, or report the number in the note.

---

### 15. Informal prices are indexed to the zero-tax formal wage, which linearity does not imply

**Status**: [Pending]

**Quote**:
> For informal households, we assume that informal wages are proportional to formal

**Feedback**:
Section 2.2 says informal prices are proportional to formal factor prices because the informal technology is linear. Linearity alone gives constant marginal products, not indexation.

Appendix A states the actual assumption: the informal wage is tied to the formal wage 'absent taxes'. Its formula depends only on $s_{t-1}/\nu_t$, not on $\tau_t$ or $h_t$. This is a substantive modelling choice. It cuts the channel through which the payroll tax, via formal hours, would move informal incomes and the informal retirees' endowment ($\chi$). That channel feeds directly into (B.1) and (B.5).

Reword Section 2.2 to state the indexation assumption. Note briefly what it rules out.

---

### 16. Verbal sign arguments for the design hold at a fixed anticipated tax

**Status**: [Pending]

**Quote**:
> With it, a more Bismarckian design also raises the total the young will receive, since it

**Feedback**:
The paper sets $\tau_{t+1}=T_{t+1}(\theta_{t+1})$, and (C.3) is a total derivative. Two of the verbal arguments drop that response.

The young's benefits scale with $\tau_{t+1}f$. The total derivative is
$$\tau_{t+1}\partial f/\partial\theta_{t+1}+f(1+\ln f)T'_{t+1},$$
but (C.9) keeps only the first term.

The retirees' stake in Appendix C.1 runs through the earnings-linked return, which scales with $\tau_{t+1}\theta_{t+1}$. Its total derivative is $\tau_{t+1}+\theta_{t+1}T'_{t+1}$. Without the cost, Proposition 2 says $T'<0$. So 'retirees favour a more earnings-related system' requires the anticipated tax to respond to $\theta_{t+1}$ with elasticity below one in absolute value.

Both claims probably hold at the calibration. Add 'at a given anticipated tax', and confirm numerically that the interior design survives with the $T'$ terms included.

---

### 17. Timing of the design choice is described inconsistently

**Status**: [Pending]

**Quote**:
> in advance or choosing a permanent structure. We test the variants numerically varying parameters like

**Feedback**:
Footnote 3 lists 'choosing the design one period in advance' as a variant. Section 7 adopts it as the baseline, and Proposition 3 covers the contemporaneous timing.

Section 7.1 also cites the once-and-for-all choice as a robustness case. Two paragraphs later it rules that timing out because it 'would require a commitment that the Markov equilibria of section 2 rule out'.

Finally, 'still ends at a corner' does not say which corner. Appendix C.1 reports the Bismarckian corner for the permanent choice under CRRA at high IES.

State the baseline timing once, flag the permanent choice as an exercise outside the equilibrium concept, and name the corner each time.

---

### 18. Mild-ageing benchmark compares a level shift with a projected transition

**Status**: [Pending]

**Quote**:
> projection of Gonzalez-Eiras and Niepelt (2008).

**Feedback**:
Each counterfactual in Section 6 is an economy that 'has always had' the changed characteristic. The mild-ageing 4.0 p.p. is therefore a cross-economy gap in 2020 between two transitions, since the baseline already carries its own projected decline.

Gonzalez-Eiras and Niepelt's 3.6 p.p. is a within-economy change as $\nu$ falls from 1.38 to 1.23. Footnote 20 matches the size of the decline (0.17 against 0.15). The two numbers still measure different things, so their closeness is not a validation. Present it as a comparison of demographic magnitudes only.

---

### 19. At low IES the tax response reverses sign, which is more than dampening

**Status**: [Pending]

**Quote**:
> and at the lowest values of the IES the tax rate even falls slightly on impact. The reason

**Feedback**:
A tax that falls on impact reverses the main result. It is also the only place the paper exhibits the negative side of the ambiguous universal-pension effect, so it deserves more than a clause.

The stated mechanism, that the young resist taxation more, explains a lower tax level rather than a different response to $\epsilon$. A lower IES also steepens the marginal utility of poorer informal retirees, which works the other way.

The passage also leaves the savings response unexplained. In Table 2, savings rise when taxes are held fixed. If the tax falls, savings should rise too, unless the fixed-tax response changes sign.

Report:
- the $\rho$ at which the tax response turns negative;
- the direction of the savings response there;
- which term of the tax condition dominates below that threshold.

---

### 20. The loss is booked a period after the behaviour it proxies

**Status**: [Pending]

**Quote**:
> benefits of the current young. A design chosen together with the tax would only re-split

**Feedback**:
Participation and reporting responses happen when the young work, at $t$. They erode the base that pays current retirees.

In the model, the loss from $(\theta_{t+1},\tau_{t+1})$ instead reduces the young's own benefits at $t+1$. This puts the cost on the cohort that chooses the design, weighted by their electoral weight. Under the alternative timing, current retirees would bear it.

The allocation matters for the second channel behind the ageing result, the higher tax raising the loss. Justify booking the loss at $t+1$, or report the chosen design when the loss falls on period-$t$ revenue.

---

### 21. A Harberger triangle is excess burden, not lost revenue

**Status**: [Pending]

**Quote**:
> the loss a tax causes rises with the square of its rate (Harberger 1964). Applied to the

**Feedback**:
Appendix C.2 notes that $\sum_i\gamma_iy_it_i=0$. With a common elasticity, the first-order base responses of taxed and subsidized types therefore net to zero in revenue. The quadratic term measures excess burden, a welfare cost that subsidized types incur as well.

Charging it against the revenue that reaches retirees is a modelling choice. It is defensible as a reduced form, but it does not follow from Harberger. Say that the cost is a revenue-equivalent excess burden. Explain why the first-order base effect is set aside.

---

### 22. Elasticity-to-λ mapping ignores the one-period lag

**Status**: [Pending]

**Quote**:
> follows from the tax component; its size does not.

**Feedback**:
The wedge $t_i$ is a date-$t$ amount per unit of date-$(t-1)$ earnings. The cited elasticities refer to the net-of-tax rate at the time earnings are made, so the rate entering the Harberger formula should be $t_i/R_t$.

Redoing the algebra, the loss share becomes $\tfrac12(\varepsilon\Pi_t/R_t)\tau_t(1-\theta_t)^2\tilde V$. That implies $\lambda\approx\varepsilon\Pi_t/R_t$, not $\varepsilon\Pi_t$.

With $R_t>\Pi_t$ over thirty years, the 0.13–0.54 range shrinks and the reported multiples grow. This strengthens the paper's point, but the figures should be recomputed at the calibrated 2020 $R_t$.

---

### 23. France's voting channel moves the design away from its observed position

**Status**: [Pending]

**Quote**:
> design more Bismarckian at every intertemporal elasticity of substitution, France’s flatter

**Feedback**:
France is fully Bismarckian in the data, yet its flatter voting profile makes the chosen design less Bismarckian. Under the U.S. cost, France ends up at 0.749, only 0.011 above the U.S. (Table 10).

The conclusion lists the voting effect among the model's findings without noting that this country-specific channel runs against the data for the one country it is drawn from. Say so explicitly.

---

### 24. Inequality result attributed to Gonzalez-Eiras and Niepelt (2008)

**Status**: [Pending]

**Quote**:
> effects and taxes increase with the political power of retirees, income inequality and

**Feedback**:
Gonzalez-Eiras and Niepelt (2008) have a representative household within each cohort, so they cannot deliver an inequality comparative static. Section 3.2 itself credits only Song (2011) with that result.

The same sentence also says the log-GHH equilibrium has 'no strategic effects'. Footnote 2 and Section 4 show this fails once informal households save.

Restrict the inequality attribution to Song, and add the hand-to-mouth qualifier.

---

### 25. State what $\gamma_0$ and $\nu_t$ are measured against

**Status**: [Pending]

**Quote**:
> The ratio of workers to retirees in period

**Feedback**:
Section 2.1 sets $\sum_{j>0}\gamma_j=1$ and calls $\gamma_0$ 'the share' of informal households. Table 1 and Appendix E.2 instead treat it as informal households per formal household ($0.32/0.68=0.47$).

The budget (8) only balances if $\nu_t$ is formal workers per formal retiree. Section 2.1 says only 'workers to retirees'.

State both definitions in Section 2.1 so the aggregation in (1) and (8) can be checked directly.

---
