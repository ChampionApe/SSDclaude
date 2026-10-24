# Ledger C5: smaller numbers for the review response (A1, A9, #7, #22, #13, #5, A13)

Package C5 of `notes/plan_reviewResponse.md`, 2026-10-24, at the pension-only U.S. calibration of C1 (common X).
Driver `python/US/c5Numbers.py` (one subcommand per item), the U.S. counterfactuals at the other ρ of the sweep by
`python/US/runShocksUS.py --out`; csvs `results/numerical/C5_*.csv`; logs `logs/C5/`. Self-check before the runs
(`c5Numbers.py selfcheck`): τ_2020 at ρ = 1 and the θ = 1 counterfactual tax reproduce `US_shocksCommonX.csv`
(0.1052285714, 0.0825098791; 4e-17), and at λ = 11.563954 the recalibrated (β, ω) and θ_2020 reproduce
`escCalibration.csv` (0.654862, 1.280689, 0.72775680). Paper lines are `writing/Paper` at HEAD.

## A1: the critical turnout-weight ratio (C.1's timing)

`C5_criticalTurnout.csv` (one row per ρ and date; `tax` = calibrated, or `theta0` for 2020 at the θ = 0
counterfactual's tax). The sign of Σ γ_i μ_i (y_i − 1) D_i^{−1/ρ} over θ_t ∈ [0, 1] at the solved equilibrium,
D_i with the CRRA shares (B_t in place of β) formed under θ*; weights μ_i = y_i^k (T2's family) or μ_i = (μ_i^CPS)^m.
The middle group has y = 1.0005, so both families give the pairwise bound (D_H/D_L)^{1/ρ} at θ_t = 0 to 2e-4.

| ρ | c_H/c_L at θ = 0, 2020 | critical μ_H/μ_L, 2020 | lowest over 2020–2170 | at the θ = 0 tax (2020) | observed (CPS) |
|---|---|---|---|---|---|
| 0.5 | 3.387 | **11.47** (k = 1.67) | 9.04 (2170) | 9.05 | 1.61 |
| 1 | 3.387 | **3.39** (k = 0.83) | 3.05 (2080 on) | 3.10 | 1.61 |
| 2 | 3.388 | **1.84** (k = 0.42) | 1.75 (2080 on) | 1.82 | 1.61 |

At observed turnout the sum is negative at every θ_t, date and ρ (`negativeEverywhere`; and
`ModelESC.sequentialFOC` agrees in sign). The corner survives until the high-income group's weight is 3.4 times the
low-income one's at ρ = 1 (twice the observed 1.61), 11.5 times at ρ = 0.5 and 1.84 times at ρ = 2: at ρ = 2 the
margin is 14% in 2020 and 9% from 2080, as the larger system compresses retirement consumption. T2's 3.16/1.78 were
at τ = 0.144; the lower pension-only tax raises the consumption ratio (3.16 → 3.39) and the bounds.
Paper: `Appendix/EndogenousDesign.tex:41` (threshold in log; the CRRA sentence has no ρ-dependent bound),
`:43` ("negative over the whole interval, at every date of the projection and at ρ = 0.5, 1 and 2"),
`Sections/Introduction.tex:25` ("unless propensities to vote rise sharply with income"), `Sections/EndogenousTheta.tex:5`.
**Holds**; the numbers for T2's C.1 placeholders are 3.4 (ρ = 1) and 1.84 (ρ = 2).

## A9: every counterfactual at every ρ (the ranking)

`C5_ranking.csv` (rows: host, ρ, ageing scenario used for the rank, effect; `dτ_pp` = full-effect change in the 2020
tax, p.p.; `rank` among ageing, design θ: 1 → 0, income distribution, voting, leisure). U.S. host from
`US_shocksCommonX.csv` (ρ = 0.5, 1, 2) and the new `C5_US_shocksRhoGridCommonX.csv` (ρ = 0.6–1.9, 0.1 apart; its
ρ = 1 rows reproduce the published ones exactly); UK and UK-at-U.S.-percentiles hosts from `UK_shocksCommonX.csv`,
`UKUS_shocksCommonX.csv`.

| U.S., ρ | acute | mild | design 1→0 | income | voting | leisure |
|---|---|---|---|---|---|---|
| 0.5 | **9.38** | 4.34 | **9.34** | −1.65 | 0.34 | 0.00 |
| 0.7 | 9.08 | 4.22 | 8.38 | −1.54 | 0.61 | 0.00 |
| 1.0 | 8.65 | 3.99 | 6.61 | −1.29 | 0.93 | 0.00 |
| 1.5 | 8.28 | 3.91 | 4.38 | −1.09 | 1.45 | 0.00 |
| 2.0 | 7.87 | 3.74 | 2.12 | −0.88 | 1.87 | 0.00 |

- U.S.: acute ageing first and the earnings link second at every ρ of the grid; at ρ = 0.5 the two tie (9.38
  against 9.34). Voting overtakes income distribution from ρ = 1.3; the earnings link stays above voting up to 2.0
  (2.12 > 1.87), but the gap closes by about 0.5 p.p. per 0.1 of ρ there (0.77 at 1.9, 0.25 at 2.0), so the two
  cross just above ρ = 2. With mild ageing in place of acute, the earnings link is first up to ρ = 1.6 and mild
  ageing first from 1.7.
- UK host (own cuts): the earnings link is first at ρ = 0.5 (6.31 against acute ageing's 5.05), second at 1 (4.55
  against 4.73) and 2. UK at U.S. percentiles: France's income distribution (1.83, 1.60) exceeds the earnings link
  (1.46, 0.47) at ρ = 1 and 2, so the link is third.
Paper: `abstract.tex:6` and `Sections/Conclusion.tex:5` ("ageing ... the main determinant ..., the earnings link the
second, and income inequality and voting patterns minor", "In the model calibrated to the U.S., France and the
UK"), `Sections/OECD.tex:29` (design and ageing the main determinants), `:40` ("robust across different ρ"),
`Sections/Introduction.tex:23`. **Holds for the U.S. at every ρ (tie at 0.5); changes for the UK hosts**: the
"U.S., France and the UK" sentence is true only with acute ageing on the U.S. host; on the UK host the earnings
link leads at ρ = 0.5, and at U.S. percentiles it is third at ρ ≥ 1. C1's A9 finding stands (design 2.12 > voting
1.87 at ρ = 2).

## #7: the marginal loss at the observed design

`C5_marginalLoss.csv` (rows: ρ, spec, Δθ, taxHeld). Share of revenue lost, 1 − f, at θ* and θ* − 0.1, the 2020
tax held at 0.1052 (the review's convention); `dLoss_dθ_atθStar` the slope.

| ρ | λ | 1 − f(θ*) | 1 − f(θ* − 0.05) | 1 − f(θ* − 0.1) | 1 − f(θ* − 0.2) | −d(1 − f)/dθ at θ* (per 0.1) |
|---|---|---|---|---|---|---|
| 0.5 | 23.69 | 3.9% | 5.5% | **7.2%** | 11.4% | 2.8 p.p. |
| 1 | 11.56 | 1.9% | 2.7% | **3.6%** (3.5% with T_2020 re-solved) | 5.7% | 1.4 p.p. |
| 2 | 2.46 | 0.4% | 0.6% | **0.8%** | 1.2% | 0.3 p.p. |

The Π-inclusive cost gives the same shares (λ_ΠR·π = λ to 0.2%). Paper: `Sections/EndogenousTheta.tex:35` ("no more
than 4%"). **Holds** as a level; the marginal figures are new (review: 3.9% → 7.3% at ρ = 0.5, now 7.2%).

## #22: λ against the elasticities, λ ≈ εΠ/R

`C5_lambdaElasticity.csv` (one row per ρ). Π_2020 and R_2020 on each ρ's no-cost baseline (θ* pinned):
Π = 1.359 / 1.355 / 1.350, R = 2.443, π = Π/R = 0.556 / 0.555 / 0.552 (the Π-inclusive runs' own π: 0.558 / 0.555 /
0.553). Elasticities 0.1–0.4 (Chetty et al. 2011; Saez, Slemrod and Giertz 2012) give λ = 0.055–0.222 (paper:
0.13–0.54 from λ ≈ εΠ).

| ρ | λ (paper's cost) | implied ε = λR/Π | ε under the paper's λ ≈ εΠ | Π-inclusive λ (= implied ε) | multiples of 0.1–0.4, λ ≈ εΠ/R | paper's mapping |
|---|---|---|---|---|---|---|
| 0.5 | 23.69 | 42.6 | 17.4 | 42.4 | **106–426** | 44–174 |
| 1 | 11.56 | 20.9 | 8.5 | 20.8 | **52–209** | 21–85 |
| 2 | 2.46 | 4.45 | 1.82 | 4.46 | **11–45** | 5–18 |

The gap to the elasticities widens by R/1 = 2.44 (T3 confirmed; decision 1's "narrows" is wrong). π falls from 0.555
(2020) to 0.464 (2110) at ρ = 1 (`πPath`). Paper: `Sections/EndogenousTheta.tex:35` ("by more than an order of
magnitude at ρ ≤ 1"), `Appendix/EndogenousDesign.tex:70` (footnote: the return factor absorbed into λ), `:72`
("0.13 and 0.54 ... more than an order of magnitude above at ρ ≤ 1, three to thirteen times above it at ρ = 2").
**Changes in the direction of the claim**: "more than an order of magnitude" now holds at every ρ (11× at ρ = 2);
"three to thirteen times" becomes 11–45 times, and 0.13–0.54 becomes 0.06–0.22.

## #13: headline design changes in index units, I = 1/(2 − θ)

`C5_indexUnits.csv` (rows: item, ρ; θ0 → θ1, I0 → I1, ΔI exact and I0²Δθ). θ* = 0.7278 is I = 0.786 (figure 1.1's
U.S. index 0.790, θ = 0.735 by 2 − 1/I; the difference is the model's groups, T3 §2.2).

| change (θ chosen, 2020, against the chosen baseline) | ρ = 0.5 | ρ = 1 | ρ = 2 |
|---|---|---|---|
| design path 2020 → 2050 / → 2110 (Δθ) | +0.057 / +0.088 | +0.074 / +0.097 | +0.057 / +0.095 |
| same in index units | **+0.037 / +0.059** | **+0.049 / +0.065** | **+0.037 / +0.063** |
| acute ageing Δθ → ΔI | +0.098 → **+0.065** | +0.117 → **+0.080** | +0.104 → **+0.070** |
| mild ageing Δθ → ΔI | +0.033 → +0.021 | +0.070 → +0.046 | +0.033 → +0.021 |
| French income distribution | −0.047 → −0.028 | +0.024 → +0.015 | +0.184 → +0.133 |
| French voting | −0.044 → −0.026 | −0.074 → −0.043 | −0.339 → −0.165 |
| all French characteristics | −0.070 → −0.041 | −0.104 → −0.059 | −0.414 → −0.193 |

Corners: θ 1 → 0 is I 1 → 0.5; the U.S. to the Bismarckian corner +0.214, to the Beveridgean −0.286; figure 1.1's
29 countries span I = 0.50–1.00. Appendix G.1 at ρ = 1: the UK under the U.S. λ chooses 0.698 (I 0.768) against
its observed 0.560 (I 0.694) and the U.S. 0.786: in index units the U.S. λ covers 19% of the UK's distance (18% in
θ). France chooses 0.799 (I 0.833) against 1. Paper: `Sections/Introduction.tex:5` (the index defined as the ratio
of replacement rates), `:19` and `Sections/EndogenousTheta.tex:2` (θ called "the Bismarckian index"),
`Appendix/EndogenousDesignResults.tex:15` (path 0.738 → 0.797 → 0.809), `Sections/EndogenousTheta.tex:62`,
`Sections/OECD.tex:48`. **Numbers** (no claim changes sign); the review's "about 0.05 on the index" for the path
is now 0.065, against a cross-section spanning 0.5.

## #5: the design condition's response to inequality

France's income distribution on the U.S., θ chosen (figure 7.1's row: θ_2020 −0.047 / +0.024 / +0.184). Two pieces.

**The design's response split by what the cost sees** (`C5_designDecomp.csv` kind `choice` at ρ = 1;
`C5_designDecompCRRA_rho0.5.csv`, `_rho2.csv`, exact 2-D recursion; every count one equilibrium, no fallback). The
Π-inclusive slot of the cost is set to a fixed π_t so that the loss share keeps the U.S. size of the system,
π_t = τ^US_t/τ_t (X1), or the U.S. size and dispersion, times Ṽ_US/Ṽ_FR (X2); iterated until π_t τ_t matches
(log: to 1e-10; CRRA two passes, gaps 0.06%/1.1% at ρ = 0.5 and 0.04%/0.2% at ρ = 2). Sequential split of
Δθ_2020 against the U.S. 0.7278:

| ρ | response | gains side (X2 − U.S.) | cost's dispersion (X1 − X2) | cost's size, the τ channel (France − X1) | without the τ channel (X1 − U.S.) |
|---|---|---|---|---|---|
| 0.5 | −0.047 | +0.111 | −0.119 | **−0.039** | −0.008 |
| 1 | +0.024 | +0.149 | −0.104 | **−0.021** | +0.045 |
| 2 | +0.184 | +0.207 | −0.020 | **−0.002** | +0.186 |

The 2020 tax falls 7.2 / 6.3 / 4.3% under France's distribution (free paths), and with a loss share linear in τ
every unit of redistribution gets cheaper: the τ channel is Beveridgean at every ρ, strongest where λ is largest,
and supplies 83% of the ρ = 0.5 response. **It is not the whole story**: with the loss share held at the U.S. size the
response at ρ = 0.5 is still Beveridgean (−0.008), because the cost's dispersion force (flat benefits cheaper, Ṽ
halved) outweighs the gains side there (−0.119 against +0.111), and not at ρ = 1 or 2. The review's stylised
argument (the redistributive gain and the cost both ∝ Ṽ, so only the labor stake gains weight) holds at θ = 1 under
log; at the calibrated design the two dispersion forces do not scale together, the cost's being the stronger at low
ρ, which is the paper's own account. The order matters: the cost's dispersion alone on the U.S. (X3, ρ = 1) moves
θ_2020 to 0.547 (−0.181).

**The design condition under log** (`C5_designDecomp.csv` kind `foc`, ρ = 1): dW_1990/dθ_2020 at the U.S. choice
with the anticipated tax function solved at every candidate (θ̂ = 0.7324, where it is zero), by route, ×10³:

| route | U.S. | France's distribution | change |
|---|---|---|---|
| design at given loss share and tax | −27.95 | −10.66 | +17.29 |
| … retirees' labor stake / young's hours | +8.39 / +94.38 | +8.02 / +90.16 | −0.37 / −4.22 |
| … young's pension and earnings / young's R_{t+1} | −133.25 / +2.53 | −111.25 / +2.40 | +22.01 / −0.13 |
| loss share's dependence on the design (eq:esc:ftheta) | +19.72 | +8.65 | −11.08 |
| anticipated tax's response T'_{2020}(θ) | +8.23 | +6.69 | −1.54 |
| total | 0 | **+4.67** | +4.67 |

On the design route the flat pension's pull (the young's bracket) shrinks by 17% and the hours stake by 4% (the
lower tax); the cost route shrinks by 56% (Ṽ halved, τ lower). The anticipated tax's response, which the paper's
account does not name, supplies 29% of what balances the design route at the U.S. choice (8.23 of 27.95).

Paper: `Sections/EndogenousTheta.tex:59` (two forces; "the second force is strongest at low elasticities, where the
calibrated cost parameter is largest, and the first at high elasticities"), `:55`, `:62`, `abstract.tex:6`,
`Sections/Conclusion.tex:7`, `Sections/Introduction.tex:27`. **Holds, with a third force to add**: the two named
forces order as the paragraph says (dispersion −0.119 / −0.104 / −0.020, gains +0.111 / +0.149 / +0.207), and the
fall in the tax with a cost linear in τ adds a Beveridgean push (−0.039 / −0.021 / −0.002) that the paragraph omits
and that carries most of the ρ = 0.5 response. The responses and the experiments come from the same solvers as
figure 7.1 (log: the 41-node table below; CRRA: the exact recursion), so the split is internally consistent. No FOC
split under CRRA (the 2-D layer values designs at frozen shares; the experiments stand in).

## A13 (online appendix): τ_2020 against inherited capital

`C5_taxPolicyState.csv` (rows: ρ, s_2019 relative to the equilibrium s*_2019). The 2020 policy function of the
design-given CRRA equilibrium: at ρ = 0.5 the tax falls with inherited capital (11.4% at half s*, 10.0% at 1.5 s*;
elasticity −0.13 at s*), at ρ = 2 it rises (10.1% to 10.7%; +0.05); under log it is flat at 10.52%. **Not done: the
split into the choice of a voter who ignores the state-to-policy feedback and the Markov choice.** It needs a
period solve with the continuation's policy response frozen while h_{t+1} keeps its economic response to s_t, which
no solver function offers (`policy.CRRA.stateApprox_t` reads τ_{t+1} and h_{t+1} off one continuation); a model
function would have to change, so it is left for W9 to decide.

## Found on the way

- **The log design choice carries a grid error of 0.005.** `LeadedLOG` reads the anticipated tax function
  T_{t+1}(θ) off a piecewise-linear table on its 41-node design grid (`ModelESC(nθ = 41)`); near θ* the table's
  slope is 0.0053 against the solved 0.0084, and the flat design objective moves its argmax by a fifth of a cell.
  At λ = 11.564, θ_2020 is 0.7278 (41 nodes), 0.7311 (81), 0.7321 (161), 0.7323 (321) and 0.7324 with T solved at
  every candidate; France's income distribution moves it by +0.0236, +0.0215, +0.0212, +0.0213, +0.0213
  (`C5_designDecomp.csv`, kind `grid`). The calibration absorbs the level (λ would be about 2% lower on a converged
  grid, dθ/d ln λ ≈ 0.22); responses move by ≤ 0.0025. Finding #19's mechanism in the log solver. The exact CRRA
  recursion interpolates its continuation along a 13-node θ-state grid in the same way and was not measured here.
  For checkpoint 2.
