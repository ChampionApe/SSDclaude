# Ledger C2: Argentina after #4, #3 and A7 (W16, 2026-10-23)

Every Argentine number the paper prints that moves with C2's reruns, old (HEAD `7b52235`, the run of 2026-10-07) and
new, the csv and row it comes from, and where `writing/Paper` prints it. Headline calibration (common $X$, $\rho = 1$)
unless a row says otherwise; 2010 is the shock csvs' first row (`t = 3`), 2040 their second (`t = 4`). Generated
tables and figures (marked *gen*) are already rebuilt by `build.py`; the rest is prose for W4 (and W1 for the front
matter). Savings and spending over GDP use GDP = formal plus informal output (#3): `datasets.savingsRatePath`
(s/(Y+Y0)) and `datasets.spendingPath` (τ(1−α)Y/(Y+Y0)), both on the shock csvs' `Y_*`, `Y0_*` columns.

Short names: `U(ρ)` = `results/shocks/universal_match_rho{ρ:.4f}_commonX.csv`, `E(ρ)` =
`results/shocks/eeOnly_match_rho{ρ:.4f}_commonX.csv`, `S` = `results/paper/calibrationSummary.csv` (the
`commonX = True` row), `G` = `results/calibration/informalSavings_rhoGridCommonX.csv`.

## 1. Calibration (table 1, section 5's calibration paragraph, appendix E.3)

| Quantity | Old | New | Source | Printed in |
|---|---|---|---|---|
| Tax target $\tau_{2010}$ | 10.9% (0.071/0.65 = 0.1092) | **11.8%** (0.1181; $y$ = 7.53% of GDP informal) | `S` τ; `config.calendar()['τ0']`; `G` `yInf`, `spendGDP` = 0.0710 at every ρ | `Sections/Argentina.tex:23` ("10.9\%, which is pension spending of 7.1\% of GDP ... divided by the labor share of formal output"); `Appendix/HouseholdSurveyArg.tex:26` ("$\tau_{2010} = 0.071/(1-\alpha) = 0.109$"); table 1's ω row (*gen*) |
| $\epsilon$ (pre-reform) | 0.21 (0.2086) | 0.21 (0.2100: β moved) | `S` ε | `Argentina.tex:21`; table 1 (*gen*) |
| $\beta$ | 0.65 | **0.67** (0.6686) | `S`, `G` ρ = 1 | table 1 (*gen*) |
| $\omega$ | 1.45 | **1.50** (1.4963) | `S`, `G` ρ = 1 | table 1 (*gen*) |
| $X$ | 1.94 | **1.92** | `S` Xi | table 1 (*gen*) |
| $\eta_0$, $X_0$ | 0.344, 0.804 | **0.340, 0.795** | `S` | table 1 (*gen*) |
| $\theta$, $\gamma_0$, $\eta_i$, relative hours 1.18 vs 1.10 | 0.84, 0.47, [0.64, 0.90, 1.14, 1.87], 1.18 | unchanged | `S` | `Argentina.tex:21,23` |
| Baseline savings rate 2010 | 14.40% (over formal output) | **13.33%** of GDP (14.41% over formal output) | `U(1)` t=3 via `savingsRatePath`; `G` `srGDP`, `sr` | table 2 (*gen*) |

## 2. The reform, $\rho = 1$ (table 2, section 5, front matter)

| Quantity | Old | New | Source | Printed in |
|---|---|---|---|---|
| Δτ 2010 | +2.08 p.p. ("2.1") | **+1.95 p.p.** (13.76% − 11.81%) | `U(1)` t=3 `τ_reform − τ_base` | `Argentina.tex:30` ("rises by 2.1 p.p."); table 2 (*gen*) |
| Δ spending 2010 | 1.35% of GDP ("1.4\%", Δτ·(1−α)) | **1.17% of GDP** (8.27% − 7.10%); 1.27% if read as Δτ·(1−α) on formal output | `spendingPath(1, 'reform') − (1, 'base')`, t=3 | `Argentina.tex:30` ("pension spending of 1.4\% of GDP") |
| Share of the 1.8% of GDP | about three quarters (75%) | **65%**, about two thirds | as above / 0.018 | `Argentina.tex:30`; `abstract.tex:6`; `Introduction.tex:23`; `Conclusion.tex:5` ("about three quarters") |
| Δ savings rate 2010, full | −0.43 p.p. ("0.4") | **−0.36 p.p.** of GDP (12.96% − 13.33%) | `U(1)` t=3, `savingsRatePath` | `Argentina.tex:30`; `Conclusion.tex:5` ("0.4 p.p.\ of GDP"); table 2 (*gen*) |
| Δ savings rate 2010, taxes fixed | +0.33 p.p. | **+0.32 p.p.** (13.64%) | `E(1)` t=3 | table 2 (*gen*); `Argentina.tex:28` (sign only) |
| Δ workweek 2010 | −0.25 h ("a quarter of an hour") | −0.24 h (42.30 against 42.54; 42.46 taxes fixed) | `U(1)`, `E(1)` t=3 `h_*` via `workweekHours` | `Argentina.tex:30`; `Conclusion.tex:5`; table 2 (*gen*) |
| Formal benefits 2010 (new column) | -- | **+1.46%** full, **−12.70%** taxes fixed | `U(1)` t=3 `d_biAvg`; `E(1)` t=3 `d_bi` | table 2 (*gen*); A7's "financed by cuts" |
| Δτ 2040 | +3.53 p.p. ("3.5") | +3.47 p.p. ("3.5") | `U(1)` t=4 | `Argentina.tex:30` |
| Δ informal savings ratio ι 2010 | −5.66 p.p. | −5.86 p.p. | `U(1)` t=3 `ι_reform − ι_base` | figure 5.2 (*gen*) |
| Tax candidates | nEqMax 1, nFallback 0 | unchanged at every ρ | `G`, `U(ρ)` `nEqMax`, `nCandMax` = 3, `nFallback` | `REPLICATION.md` §3 |

## 3. Across ρ (figure 5.2, section 5's IES paragraph)

| Quantity | Old | New | Source | Printed in |
|---|---|---|---|---|
| Δτ 2010, ρ ∈ [1, 2] | +2.08 to +2.25 p.p. ("2.1 to 2.3") | **+1.95 to +2.16** (max at ρ = 1.4) | `U(ρ)` t=3 | `Argentina.tex:49`; figure 5.2 (*gen*) |
| Δ workweek, ρ ∈ [1, 2] | −0.25 to −0.27 h ("roughly 0.25") | −0.24 to −0.27 h | `U(ρ)` t=3 | `Argentina.tex:49` |
| Δ savings rate, ρ ∈ [1, 2] | −0.43 to −0.31 ("0.4 to 0.3") | −0.37 to −0.28 p.p. of GDP | `U(ρ)` t=3 | `Argentina.tex:49` |
| Δι, ρ ∈ [1, 2] | −5.7 to −5.8 p.p. | **−5.9 to −6.1** | `U(ρ)` t=3 | `Argentina.tex:49` |
| Δτ 2040, ρ ∈ [1, 2] | +3.32 to +3.58 | +3.29 to +3.53 | `U(ρ)` t=4 | `Argentina.tex:49` ("amplified") |
| Δτ 2010 at ρ = 0.5 / 0.6 | −0.29 / +0.72 | **−0.42 / +0.53** | `U(0.5)`, `U(0.6)` t=3 | `Argentina.tex:49` ("falls slightly on impact") |
| Δ savings rate at ρ = 0.5 / 0.6 | +0.18 / −0.12 | **+0.21 / −0.06** p.p. of GDP | as above | `Argentina.tex:49` (Ruffo sentence) |
| Stationary-policy gap, Argentine calibration, lowest IES | up to 0.5 p.p. (0.49, ρ = 0.5, 1950) | **up to 0.3 p.p.** (0.28, ρ = 0.5, 2040; 0.26 in 1920) | `results/numerical/ARG_stationaryApprox_commonX.csv` `gap_pp`, ρ = 0.5, t ≤ 7 (the period before the terminal one, 2160, carries the horizon: −0.65, was −0.63) | `Numerical.tex:3` footnote; OA `NUM_Stationary` (*gen*) |

Not changed by C2 but one GDP concept short: the capital-output target (3.23) is still K over formal output (`Base.capitalOutputRatio`), against GDP = Y + Y0 elsewhere; at y = 7.5% the model's K/(Y+Y0) is 2.99. Appendix E.3's footnote discusses the direction.

## 4. New results for checkpoint 2 (no paper text yet)

**#19, the low-IES reversal.** The 2010 tax response changes sign between the grid points ρ = 0.5 (−0.42 p.p.)
and 0.6 (+0.53 p.p.), zero at ρ ≈ 0.54 by linear interpolation (`U(0.5)`, `U(0.6)` t=3). The sign is resolved by
the state grid: re-solved at nι = ns = 60 against 45, Δτ is −0.419 against −0.420 at ρ = 0.5 and +0.512 against
+0.528 at 0.6 (`results/shocks/ARG_reformRefine_commonX.csv`). The calibration itself is converged but not resolved
there (`G` `verifyResidual` 1.6e-3 at 0.5, 1.5e-3 at 0.6, the 1e-3 flag; 3.7e-3 and 1.2e-3 before), and β > 1 (1.44,
1.12). Below the threshold the savings rate rises (+0.21 p.p. at 0.5), consistent with the falling tax.

**W15, the 2010 first order condition** (`results/shocks/ARG_reformFOC_commonX.csv`, one row per ρ and group).
Each group's contribution to Δτ is its push at the pre-reform tax over minus the summed secant slope,
−push_g/Σslope (p.p.; sums to the FOC's own Δτ, 1.948 against the path's 1.950 at ρ = 1):

| Group | ρ = 0.5 | 0.6 | 1 | 2 |
|---|---|---|---|---|
| old informal, pension (where ε enters) | +4.25 | +5.42 | +8.20 | +11.78 |
| old formal, pension | −0.60 | −1.00 | −2.72 | −6.56 |
| old, labour terms | +0.14 | +0.09 | −0.06 | −0.16 |
| young formal | −0.19 | −0.25 | −0.58 | −0.94 |
| young informal | **−4.02** | −3.75 | −2.90 | −2.09 |
| total | −0.42 | +0.51 | +1.95 | +2.04 |

The young formal's share of the slope (their resistance to a higher tax) is the same at ρ = 0.5 and 1 (0.39 and
0.37); the old informal's share rises (0.51 against 0.33). What dampens and then reverses the reform at a low IES
is the push: the informal retirees' gain per unit of slope halves (+4.25 against +8.20 p.p.) while the young
informal, now covered, withdraw support by more (−4.02 against −2.90). The young formal account for −0.19 p.p.

**A12, condition (B.5)** (`results/shocks/ARG_reformB5_commonX.csv`, rows `pre`/`post`; γ_i = 1/4). At ρ = 1 before
the reform: ε = 0.210, φ = 0.976, σ⁰ = 0.122, σⁱ = 0.196, 0.177, 0.167, 0.155; left side (φ/ε)σ⁰(1−σ⁰) = 0.498
against Σγ_iσⁱ(1−σⁱ) = 0.143 (3.5 times). At ε^U = 0.546: σ⁰ = 0.270, 0.350 against 0.145. In this model the informal
retirees' coefficient is 1 rather than φ (their savings income moves with h_t, as formal retirees' does): 0.511
(`lhsSavings`). At ρ = 0.5 and 2 the log condition on the CRRA calibrations reads 0.475/0.141 and 0.508/0.144.

**#2, Gonzalez-Rozada and Ruffo's counterpart** (`results/shocks/ARG_reformHouseholdSavings_commonX.csv`). Savings
of the young over disposable labour income in 2010, informal against the formal average, ρ = 1: 27.3% and 25.1%
before; 21.8% and 25.0% after (22.7% and 25.7% with the tax fixed). Difference-in-differences −5.4 p.p. (−5.2 with
the tax fixed); −4.9 at ρ = 0.5, −5.4 at ρ = 2. The household response is negative at every ρ, the aggregate one
only above ρ ≈ 0.58 (+0.21 p.p. at 0.5, −0.06 at 0.6). The estimate itself (value, sample, whether the treated are pre-retirement households) is not
in the repository (no copy of IDB-WP-629; `notes/paper_reviewResponse.md` records "difference-in-differences,
households"), so the comparison of magnitudes is open.

## 5. A7, the pre-reform ε = 0 variant

`G0` = `results/calibration/informalSavings_rhoGridCommonXEpsPre0.csv`, `U0(ρ)`/`E0(ρ)` =
`results/shocks/{universal,eeOnly}_match_rho{ρ:.4f}_commonX_epsPre0.csv` (2010 = `t = 3`). Same targets (τ 11.81%,
K/Y 3.23); γ₀ now counts informal retirees without any pension, and the reform raises ε from 0 to ε^U = 0.546.

| Quantity, ρ = 1 | Headline (ε = 0.21) | ε = 0 | Source |
|---|---|---|---|
| β, ω | 0.669, 1.496 | 0.693, 1.663 | `G0` ρ = 1 |
| Δτ 2010 / 2040 | +1.95 / +3.47 p.p. | **+4.20 / +7.17 p.p.** | `U0(1)` t=3, 4 |
| Δ spending 2010 | 1.17% of GDP (65% of 1.8%) | **2.52% of GDP (140%)** | `U0(1)` t=3, τ(1−α)Y/(Y+Y0) |
| Δ savings rate, full / taxes fixed | −0.36 / +0.32 p.p. | −0.88 / +0.55 p.p. of GDP | `U0(1)`, `E0(1)` t=3 |
| Δ workweek | −0.24 h | −0.50 h | `U0(1)` t=3 |
| Δι | −5.86 p.p. | −9.61 p.p. | `U0(1)` t=3 |
| Formal benefits, full / taxes fixed | +1.46% / −12.70% | +7.02% / −20.63% | `U0(1)` `d_biAvg`, `E0(1)` `d_bi` |

Across ρ the variant's tax response is +3.75 to +4.32 p.p. for ρ ∈ [1, 2] and changes sign between ρ = 0.5 (−3.85)
and 0.6 (+0.71), as the headline's; at ρ = 0.5 the savings rate rises 1.11 p.p. Every point one equilibrium, no
fallback; the variant's own calibration is resolved down to ρ = 0.5 (`G0` `verifyResidual` ≤ 8.1e-4). The ρ = 1
no-shock control reproduces the baseline tail to 9.8e-7 in τ (`logs/C2runs/B_universalEpsPre0rho1.log`).
