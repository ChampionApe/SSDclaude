# Brief: a microfoundation for the cost with τ² (k = 2) — model-theorist, Fable, max effort

Written 2026-11-07 for RKB's request: "think carefully if we can microfound [the τ² version] by tweaking our current
story". The deliverable is one note, `notes/tauPower_microfoundation.md`. You change no other file.

RKB's coauthor has a separate suggestion, to be compared with yours **after** your note is done. You do not know it
and should not try to guess it: find the best microfoundation(s) you can on the merits.

## Read first

Two other agents are editing `writing/Paper/Appendix/EndogenousDesign.tex` (appendix C.2) and
`writing/Paper/Sections/EndogenousTheta.tex` (section 7.3) while you work. Read the **committed** versions:
`git show HEAD:writing/Paper/Sections/EndogenousTheta.tex` (section 7.1, `sec:esc:cost`, is the cost) and
`git show HEAD:writing/Paper/Appendix/EndogenousDesign.tex` (C.2 `app:esc:cost`, C.3 `app:esc:equilibrium`, C.4
`app:esc:log`). Then:
- `writing/Paper/Sections/Model.tex` and `writing/Paper/Appendix/PoliticoEconomicEquilibrium.tex` (the household
  problem, the labor supply condition, the political objective, the tax condition under log-GHH preferences);
- the technical note's cost: `writing/US/model_esc.tex`, "The deadweight cost of redistributive benefits";
- `notes/paper_costLiterature.md` (the literature behind the cost, the objection it has to meet, and how the paper
  motivates each property; §1 and §3 are the short version);
- the code: `python/US/base.py` (`fWedge`, `dlnfWedge_dτ`, `wedgeΠR`, `Vtilde`) on main, and the k = 2 branch's
  version in the worktree `C:\Users\sxj477\Documents\GitHub\SSDclaude-tauPower` (`git -C ..\SSDclaude-tauPower diff
  python/US/base.py python/US/modelESC.py`), with its state and results in `..\SSDclaude-tauPower\notes\tauPower_k2.md`.
- Optional background, not to restate: `archive/notes/esc_inequalityChannel.md` (2026-09-24: why the design wedge gave
  way to the size-scaled cost, with the alternatives then weighed: a leak in the dispersion, a formality margin, an
  insurance motive, a contribution ceiling).

## The two specifications

The paper (k = 1), in the budget of section 7.1:
$$\nu_t w_t\tau_t h_t\, f(\theta_t,\tau_t)=\sum_i\gamma_i b_t^i,\qquad
\ln f(\theta_t,\tau_t) = -\tfrac12\,\lambda\,\tau_t^{\,k}\,\tilde V\,(1-\theta_t)^2,\qquad
\tilde V=\sum_i\gamma_i\frac{(y_i-1)^2}{y_i},$$
with $\lambda$ constant for the U.S. and $\lambda_{n,t}=\varepsilon\,\Pi_{n,t}/R_{n,t}$ in the cross-section
(section 7.3, appendix G; `'sizePiR'` in the code). The branch `exp/tauPower` sets k = 2 everywhere; the tax
condition's factor $f(1+\ln f)$ becomes $f(1+k\ln f)$.

The paper's derivation of k = 1 (C.2, and the footnote to the budget in 7.1): type $i$'s implicit tax against a purely
earnings-related system paying the same revenue is $t_i=\Pi_t\tau_t(1-\theta_t)(1-1/y_i)$ per unit of past earnings;
a worker values the benefit at $1/R_t$, so the rate is $t_i/R_t$; the bases are $e_i=y_i$; the Harberger excess
burden is $\tfrac12\varepsilon\sum_i\gamma_i y_i(t_i/R_t)^2=\tfrac12\varepsilon(\Pi_t/R_t)^2\tau_t^2(1-\theta_t)^2\tilde V$
per unit of mean past earnings, and as a share of revenue $\tfrac12\varepsilon(\Pi_t/R_t)\tau_t(1-\theta_t)^2\tilde V$.
The implicit taxes are a pure transfer, $\sum_i\gamma_iy_it_i=0$, so with a common elasticity the first-order
revenue responses cancel; the excess burden is charged against the revenue that reaches retirees "as a choice of
reduced form rather than a consequence of the argument". The ingredients of the story, each a lever you may consider
tweaking: (a) Summers' tax component, the flat component read as type-specific implicit taxes; (b) the margins the
model lacks (participation, formality, reporting), on which the average wedge is the relevant one; (c) Harberger's
principle with a common elasticity; (d) what is charged against the revenue that reaches retirees, and as a share of
what; (e) the timing (booked in the period of the benefits); (f) the factor $\Pi/R$ and how $\lambda$ is carried
across countries and dates.

Why the question matters: at k = 2 the cross-section fits markedly better (worktree note): predicted designs sd 0.202
against 0.11 at k = 1 (data 0.32), correlation 0.750 against 0.72, RMSE 0.218 against 0.26; table 5's slope of the
index on population growth −0.43 against −0.22 (data −0.44), of spending on the index 33.1 against 64.9 (data 16.3).
The calibrated cost parameter is λ = 41.45 under log preferences (k = 1: 6.25). RKB is deciding whether k = 2 becomes
the main specification, and a microfoundation is what the text would need.

## The question

Can the τ² form be derived by tweaking the current story, so that k = 2 is a consequence of stated assumptions
rather than a choice? Concretely:

1. **Candidates.** At least three genuinely different mechanisms that deliver a share of revenue lost proportional to
   $\tau_t^2\tilde V(1-\theta_t)^2$, each derived in the paper's notation from stated primitives to the form of $\ln f$.
   Say for each whether τ² is exact, holds to a stated order in the wedges, or holds under a functional form (and
   which), and whether k is pinned at 2 or is a parameter of the mechanism (a framework that nests k = 1 and k = 2 is
   worth having in its own right).
2. **The properties the paper uses.** For each candidate, check, or say what breaks and whether it matters:
   (P1) no loss at θ = 1; (P2) no loss when all incomes are equal; (P3) quadratic in $1-\theta$, so that under log
   preferences the slope of the political objective at the Bismarckian corner and the tax chosen there do not depend
   on λ (C.2, "Specification"); (P4) proportional to $\tilde V$; (P5) both components of the benefit scaled alike, so
   that θ stays identified from the earnings-linked share (C.3); (P6) the tax condition's factor $1+k\ln f$ positive
   wherever the tax is interior, and the design gain $\partial f/\partial\theta$ with the monotonicity conditions of C.3
   restated for k = 2; (P7) the separability of C.4 (proposition `prop:esc:separability`); (P8) the symmetry caveat
   (the subsidy below the mean counted as a loss, C.2's Saez sentence): does the candidate keep it, remove it, or
   change its sign?
3. **What the candidate implies beyond k.** The exact coefficient on $\tau^2\tilde V(1-\theta)^2$ in terms of
   primitives; how $\lambda_{n,t}$ should then be carried across countries and dates (is it still $\varepsilon\Pi/R$,
   or $(\Pi/R)^2$, or something else?); any design-independent loss of the size of the system the mechanism also
   produces, and whether leaving it out is defensible; any change to the timing argument. Compare with what the
   branch actually runs (`'sizePiR'`: $\ln f=-\tfrac12\varepsilon(\Pi/R)\tau^2\tilde V(1-\theta)^2$) and say whether the
   branch's numbers already test the microfounded specification or what exactly a run would have to change.
4. **Magnitude.** The primitive (an elasticity or its analogue) that the calibrated k = 2 parameters imply under each
   candidate, at the U.S. 2020 values ($\Pi = 1.35$, $R = 2.44$, $\tau = 0.105$; the calibrated values are in the
   worktree's `results/esc/escCalibration.csv`, `escCountry.csv` and `results/oecd26/anchor.csv`), against the
   0.1–0.4 range of participation and taxable-income elasticities that C.2 uses for k = 1 (where λ is 28–113 times what
   those elasticities imply at ρ = 1). Does any candidate close or widen that gap?
5. **Support.** The literature each candidate can lean on, from `notes/paper_costLiterature.md` and your own knowledge.
   You have no web access: mark every reference not already in that note as "to verify".
6. **Recommendation.** The candidate you would put in the paper, with a sketch (a paragraph of mathematics and
   reasoning, not paper prose) of how C.2 would derive it, and the cost of the runner-up in one paragraph. Say also,
   plainly, whether k = 1 or k = 2 is the better-founded specification once both stories are written out, and why.
7. **The test.** For the recommended candidate, what would distinguish it from k = 1 (and from the plain k = 2 of the
   branch) in the model's predictions, and the precise specification of any run needed: the formula of $\ln f$, of
   $\lambda_{n,t}$, and which stages of the pipeline it touches.

## Rules for this note

- Lead with the analytical argument; a numerical computation (under ten minutes, the repo's interpreter with
  `PYTHONUTF8=1`) is a confirmation of the algebra and is labelled as one.
- Where a step rests on an approximation, say what is dropped and its order relative to what is kept.
- Use the paper's notation and vocabulary (`notes/paper_styleGuide.md` §4: "the cost parameter", "the share of revenue
  lost", "the dispersion of relative incomes", "the size of the system").
- Anything that overturns a premise of this brief (for example, that k = 1 is what the current story implies) goes at
  the top under "Overturned".
- Write the note with the Write tool. Structure: Summary and recommendation (half a page); the current story and where
  τ enters; one section per candidate (mechanism, derivation, assumptions, properties P1–P8, implied λ, magnitude,
  support, verdict); a nesting framework if you have one; the test; open questions.

## Report (at most 20 lines)

The note's path; the recommendation; each candidate in one line with its verdict and the equation number in the note;
what you confirmed numerically and how; what you could not settle.
