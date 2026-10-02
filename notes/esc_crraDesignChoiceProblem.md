# The CRRA design choice: past savings shares move with the candidate design (2026-10-02)

Problem statement for a fresh session that designs a replacement for the CRRA solver of the endogenous design
(advance timing). Found by reading the code against the technical documentation while drafting section 4 of
the paper (`sec:numerical`). **Nothing has been run, so the size of the error is unknown.** The log results
(every headline number, at ρ = 1) are not affected; the CRRA rows of the endogenous-design results are.
The paper marks the sentence that describes this solver with `%% TODO-CRRA2D` in
`writing/Paper/Sections/Numerical.tex`; it is rewritten once the algorithm is settled.

## 1. The problem in brief

Under the advance timing the electorate at $t$ chooses $(\tau_t, \theta_{t+1})$ given the state
$(s_{t-1}, \theta_t)$ and given the distribution of past savings $D_t = \{s_{t-1,i}/s_{t-1}\}_i$. Last period's
savers chose $D_t$ against the policy they anticipated, so in equilibrium $D_t$ must be consistent with the
policy actually chosen. But the electorate cannot move it: when it compares candidate designs, every candidate
must be evaluated at the same $D_t$.

The exact CRRA solver (`LeadedCRRA2D`) evaluates the political objective at each candidate $\theta_{t+1}$ with
$D_t$ *recomputed* at that candidate's own tax and hours. Under CRRA, $D_t$ depends on both through the current
interest rate. The comparison therefore credits the electorate with a channel it does not control. The tax
first order condition in the same solver holds $D_t$ fixed correctly, so only the choice of the design is
affected. Under log preferences $D_t$ depends on the current tax alone, and the tax does not respond to the
candidate design, so the problem cannot arise there.

## 2. The economics

Notation as in the paper and `writing/US/model_esc.tex`; the model has no informal households ($\gamma_0 = 0$).

**Timing.** The design chosen at $t$, $\theta_{t+1}$, splits the benefits paid at $t+1$, i.e. those of the
current young. $\theta_t$, chosen at $t-1$, splits the benefits of current retirees.

**State and choices at $t$.** The state is $(s_{t-1}, \theta_t)$. The electorate chooses $(\tau_t, \theta_{t+1})$
given the continuation policy functions $\tau_{t+1}(s_t,\theta_{t+1})$, $h_{t+1}(s_t,\theta_{t+1})$ and
$\theta_{t+2} = \Theta_{t+1}(s_t,\theta_{t+1})$.

**The predetermined distribution.** It is the relative savings of the cohort that saved at $t-1$
(paper appendix A, eq `si_s` at vintage $t-1$; code `base.py: si_s`, line 345):
$$D_{t,i} = g_i\big(B_t, \tau_t; \theta_t\big), \qquad B_t = \beta^{\rho}\,(R_t/p)^{\rho-1}, \qquad R_t = R(s_{t-1}, h_t),$$
with the size-scaled cost $f(\theta_t,\tau_t)$ inside $g$. Every type-specific term in $g$ is proportional to
relative income $y_i$ (`auxProd` $= y_i\Gamma_h$ and `hηRatio` $= y_i$), and $\sum_i\gamma_iD_{t,i} = \sum_i\gamma_iy_i = 1$.
With a discount factor common to all types, $D$ is therefore a **one-parameter family**:
$$D_{t,i} = 1 + a_t\,(y_i - 1),$$
where the scalar $a_t$ depends on $(\tau_t, R_t)$ given $\theta_t$. Under log preferences $B_t = \beta$, so
$a_t$ depends on $\tau_t$ alone. The calibrations impose one β (`model.simpleβinv`); the redesign should confirm
that `βi` is equal across types wherever the solver runs.

**What an equilibrium at a state is.** A policy $(\hat\tau, \hat\theta')$ and a distribution $D$ such that:
- (E1) **The tax is a best response at fixed $D$:** $\hat\tau$ maximizes $W_t(\tau, \hat\theta'; D)$.
- (E2) **The design is a best response at fixed $D$:** $\hat\theta'$ maximizes $V(\theta'; D) \equiv \max_\tau W_t(\tau, \theta'; D)$ over $[0,1]$. For every candidate the tax is re-optimized *at the same $D$*.
- (E3) **Consistency:** $D = g\big(B(R(s_{t-1}, h_t(\hat\tau,\hat\theta'))), \hat\tau; \theta_t\big)$.

$h_t$ depends on the candidate $\theta'$ because current labor supply responds to the earnings link of the
benefits it earns. Since $D$ is the scalar $a_t$, (E1)–(E3) is a scalar fixed point at each state.

## 3. What the current code does

The solver is `python/US/policyESC.py`, class `LeadedCRRA2D` (lines 479–765). It is driven by
`python/US/runESCcrra.py --exact`, with settings in `python/paper/config.py`: the ESC block, `nCand2D = 41`
candidate designs, `ns2D = 150` savings nodes (`nsScan = 50` for the λ scan), and 13 nodes for $\theta_t$.
It is documented as alg `esc:crra2D` in `writing/US/num_esc.tex` (line 73 and the paragraph after it). For each
period, backwards (`solveBackward_t2D`, line 610):

1. **Savings.** For every $(\tau_t, s_{t-1}, \theta_{t+1})$ on the grid, solve for $s_t$ consistent with the
   continuation read off the $t+1$ interpolants at $(s_t, \theta_{t+1})$ (`_solveStateGrid`).
2. **The tax first order condition** $z_t$ on that grid, for each $\theta_t$ node (`_zAtθ`, line 577). $D$ is
   computed at each grid point from $(B_t(h), \tau, \theta_t)$ (lines 581–582), and the retirees' derivative
   comes from its closed form at that $D$ (`base.py: dlnc2i_dτ`, line 554). The derivative therefore holds $D$
   fixed, and $D$ is then substituted as consistent with each $\tau$. **This is correct for the tax.**
3. **The tax per candidate.** $\tau^\ast(s_{t-1}, \theta_t, \theta')$ by `roots1d.selectMaxND`: downward
   crossings and corners, ranked by the condition integrated along the tax grid.
4. **The design.** `_econAt` (line 588) evaluates $W$ at $(\tau^\ast, \theta')$ for every candidate. It
   re-solves $s_t$ and recomputes $D$ at *the candidate's* $\tau^\ast$ and $h$: `d['B'] = BG.B(s_, d['h'], tLag)`
   (via `_econCore`, line 557), then `Γs_ = BG.Γs(d['B'], τF, θtF, tLag)` and
   `si_s_ = BG.si_s(d['B'], τF, θtF, Γs_, tLag)` (lines 603–604), then $c_2$ from that $D$ (line 605). The
   design is `_argmax` over the 41 candidates (line 645), refined by a parabola through three points when interior.
5. **Hand-back.** Smooth $\tau$ along $s$ (pinned knots), retabulate at the chosen policies, and build the 2-D
   interpolants for $t-1$.

## 4. Where it goes wrong

In step 4 each candidate is evaluated at its own $D(\theta') = g\big(B(R(h(\tau^\ast(\theta'),\theta'))), \tau^\ast(\theta')\big)$.
The function maximized is $V_c(\theta') = W\big(\tau^\ast(\theta'), \theta'; D(\theta')\big)$, so
$$V_c'(\theta') = \partial_{\theta'}W\big|_D + \partial_\tau W\big|_D\,\tau^{\ast\prime}(\theta') + \partial_DW\cdot D'(\theta').$$
At an interior tax $\partial_\tau W|_D = 0$, which leaves $V_c' = \partial_{\theta'}W|_D + \partial_DW\cdot D'(\theta')$.
The correct condition (E2) is the first term alone, evaluated at the equilibrium $D$. The second term is a gain
from moving last period's savings, which the electorate cannot obtain.

There is a second difference. For a candidate other than the chosen one, $\tau^\ast(\theta')$ is the tax
consistent with that candidate's own $D$, not the best response at the equilibrium $D$. At the selected design
(E3) does hold, so the bias is in *which* design is selected, not in the internal consistency of the reported
path.

**Why log is immune.** $B_t = \beta$, so $D$ depends on $\tau_t$ alone. And $z_t$ does not depend on
$\theta_{t+1}$ (decoupling; num_esc check 3 measures the tax policy as exactly constant along $\theta_{t+1}$),
so $\tau^\ast$, and with it $D$, is the same for every candidate: $D' = 0$.

**Why CRRA is not.** $D$ depends on $R_t$ through $B_t$ when $\rho \neq 1$. $R_t$ depends on $h_t$, and $h_t$
on $\theta'$. The tax also responds to $\theta'$ under CRRA; the documentation says so itself in the paragraph
on pinned periods after alg `esc:crra2D`.

**The documentation states the opposite.** `writing/US/num_esc.tex` line 8, *Evaluating the objective does not
relax the discipline on predetermined states*, says: "Under the leaded timing the discipline is automatic: the
candidate $\theta_{t+1}$ does not appear in [the ratio] at vintage $t-1$, so no channel exists through which the
sweep could move the ratio." That is true of the formula's arguments but not of its inputs under CRRA. The
paragraph is corrected together with the fix.

**Size: not measured.** $D'(\theta')$ runs through $d\ln B_t/d\theta' = (\rho-1)(1-\alpha)\,d\ln h_t/d\theta'$
and through $\tau^{\ast\prime}(\theta')$, both small. $\partial_DW$ is a transfer of savings between rich and
poor retirees ($\sum_i\gamma_i\,dD_{t,i} = 0$), valued at their marginal utilities and propensities to vote.
The term is small, but the objective is very flat at the interior choice. At the French-voting counterfactual
at ρ = 2 it differs by $10^{-5}$ between designs 0.27 and 0.29 (num_esc.tex, paragraph after alg
`esc:crra2D`), so a tilt of that size moves the chosen design by hundredths. The interest-rate part enters
through $\rho - 1$, so the sign may differ between ρ = 0.5 and ρ = 2. The correction vanishes as ρ → 1.

## 5. The same class of problem elsewhere

- **The path iteration** (`LeadedCRRA`, line 322; the cross-check, the `method = 'path'` rows). `W` (line 363)
  reads $c_2$ from each candidate's own re-solved *path*. The whole path is re-solved per candidate (`solvePath`,
  line 379), so both $D_t$ and the level $s_{t-1}$ move with the candidate, because savers before $t$
  anticipate it. It shares the problem and adds a second one. Part of its disagreement with the exact recursion
  (num_esc check 10: 0.031 to 0.091 at ρ = 0.5 and 2) may come from this, not only from holding
  $\theta_{t+2}$ fixed as the documentation reads it.
- **The permanent timing under CRRA** (`PermanentCRRA`, line 897). It pins $D$ at a fixed point
  (`solveFixedPoint`, line 994), as it should. But `W` (line 962) takes the level of past savings from each
  candidate's own path (`cache['s_']`), so the same problem applies to the aggregate state. It bears only on
  section 7.1's qualitative claim that the permanent CRRA choice is the corner θ = 1 at a high IES.
- **Ranking several tax roots** (every solver; `writing/informalSavings/num_robustroot.tex`,
  `roots1d.selectMaxND`). Candidates are ranked by the condition integrated along the tax grid, while $D$ moves
  with $\tau$ along it. Each located root is right, since it satisfies the fixed-$D$ condition at its own
  consistent $D$. Only the comparison between two roots, or between a root and a corner, compares objects at
  different $D$. Lower priority; first check how often the paper's runs have more than one candidate.

## 6. What depends on it

All the CRRA endogenous-design rows (`method = 'exact'`) in `results/esc/escExperiments.csv`,
`escCalibrationCRRA.csv` and `escCalibrationCRRAUK.csv`, and everything built from them:
- **Tables and figures:** the ρ = 0.5 and 2 rows of `US_ESC_Calibration` (λ = 18.242 and 1.728, and the
  revenue losses), `US_ESC_Ageing`, `US_ESC_IncomeDistr`, `US_ESC_Voting` and `US_ESC_FrenchAll`; the UK tables
  of appendix G.2 at ρ ≠ 1; the ρ ≠ 1 markers of figure `US_ESC_overview`.
- **Numerical checks:** `results/numerical/US_ESC_stationaryApprox.csv` at ρ = 0.5 and 2, behind section 4's
  footnote ("misplaces the design by up to 0.059").
- **Text:** section 7.3 (λ across ρ, the UK's own cost 17% below the U.S. one at ρ = 0.5 and well above it at
  ρ = 2); section 7.4 (every ρ = 0.5 and ρ = 2 design: 0.817/0.826, 0.708/0.919, 0.687/0.334, 0.667/0.261; the
  thin-cushion argument; French voting's half hour at ρ = 2); the conclusion's "within 17% … though not at two";
  section 4's last paragraph.
- **Not affected:** every log number (ρ = 1), the CRRA results with the design given (sections 5 and 6), and
  the costless corner of section 7.1. A corner survives a small tilt unless the objective is flat at the bound;
  confirm this for the CRRA advance timing.

## 7. Structure a new algorithm can use

1. **$D$ is one scalar.** With a common discount factor $D_{t,i} = 1 + a_t(y_i - 1)$, so the equilibrium at
   each state is a scalar fixed point in $a_t$. At a fixed $a$, the best responses (E1) and (E2) are well
   defined; (E3) is one equation.
2. **Constructions to weigh, not prescribed:**
   - (a) *Per-state fixed-point iteration.* For a trial $a$, compute $V(\theta'; a)$ on the candidate grid with
     the tax re-optimized at fixed $a$ (the fixed-$D$ condition, with no substitution). Take $\hat\theta'(a)$,
     update $a$ from (E3), and iterate. `PermanentLOG/PermanentCRRA.solveFixedPoint` is the template: a best
     response, with convergence reported rather than assumed. Cost: the number of iterations times the current
     cost per period.
   - (b) *Tabulate over $a$.* Evaluate on $(\tau, s, \theta_t, \theta', a)$, obtain $\hat\theta'(s,\theta_t,a)$
     and $\hat\tau$, then solve (E3) for $a$ as a one-dimensional *root*. The informal-savings state fixed point
     in `writing/informalSavings/num_peeLOG.tex` works this way: a root problem, not a maximization. This adds
     one grid dimension to the expensive part, but the range of $a$ is narrow.
   - (c) *Joint first order conditions in $(\tau, \theta')$ at fixed $D$, then substitute $D$.* This is section
     4's approach extended to two choices. It is the cheapest, but it gives up the direct evaluation that makes
     corners visible (num_esc.tex, *Why a grid and not a first order condition*), so corners in $\theta'$ would
     need the selection rule of `num_robustroot.tex` in two dimensions.
3. **Existence and multiplicity.** The fixed point at a state need not be unique: savers who expect a more
   Bismarckian design save in a way that can make it attractive. The redesign must say how it detects several
   fixed points and which one it reports. This is the same selection question as the tax-root ranking in §5.
4. **Checks the new solver should pass:**
   - (i) As ρ → 1, it converges to the log solver at a first-order rate (the existing continuity test), and
     the correction vanishes.
   - (ii) At the solved equilibrium, holding its $D$ fixed, no candidate design beats the chosen one (a one-shot
     deviation check).
   - (iii) With the design pinned everywhere, it reproduces the CRRA taxes with the design given (existing check,
     $\max|\Delta\tau| = 3.2\times10^{-5}$).
   - (iv) The old and new results compared row by row, to report the size of the correction.
   - (v) The candidate-grid sensitivity re-measured: today 41 against 81 candidates moves the choice by up to
     0.006 at ρ = 2. Locating the maximum from a fixed-$D$ derivative rather than a parabola through grid values
     may resolve the flat objective better.

## 8. Pointers

- **Code:** `python/US/policyESC.py` (`LeadedBase._argmax` line 67, `LeadedCRRA` 322, `LeadedCRRA2D` 479,
  `PermanentCRRA` 897); `python/US/base.py` (`Γs` 277, `B` 336, `si_s` 345, `c2i` 400, `dlnc2i_dτ` 554);
  `python/US/runESCcrra.py` (`--exact`, `--nCand2D`); `python/paper/runCalibrationUS.py` and `runShocksUS.py`
  (the stage entries); `python/paper/config.py` (the ESC block); `python/US/test_escCRRA.py`.
- **Documentation:** `writing/US/num_esc.tex` (line 8; alg `esc:crraPath`; alg `esc:crra2D` at line 73 and the
  paragraph after it; checks 10–11 at lines 130–131); `writing/US/model_esc.tex` (prop `esc:separability`; the
  permanent-timing paragraph on pinning the ratio); `writing/informalSavings/num_robustroot.tex`.
- **Paper:** `Sections/Numerical.tex` (`%% TODO-CRRA2D`), `Sections/EndogenousTheta.tex` 7.3–7.4,
  `Appendix/US.tex` F.3, `Appendix/UKvsUS.tex` G.2.
