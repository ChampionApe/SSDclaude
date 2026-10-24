# Ledger C3: the cross-country test (A14), the run of 2026-10-24

Package C3 of `notes/plan_reviewResponse.md` (A14, A3, A4), phase 2. The log model of section 7 (the `size` cost,
ρ = 1, common X) built from each OECD country's data by `python/US/oecd26.py`, at C1's pension-only U.S. calibration
(β = 0.655483 at ρ = 1 without the cost, `results/calibration/US_rhoGridCommonX.csv`). No paper text cites these
numbers yet: they are checkpoint 2's input, then W6's (end of section 7, its appendix) and W9's (online appendix).
Short names: `A` = `results/oecd26/anchor.csv`, `L1`, `L2` = `results/oecd26/layer{1,2}.csv` (rows keyed on
`turnout`, `iso3`), `F` = `data/oecdFigure1.csv`, `S` = `data/oecd26_sample.csv`. Built (cps, the 26, design chosen
in 2020): `OECD26_Layer1` (figure), `OECD26_Slopes`, `OECD26_Omega`. Run: `logs/C3/runOECD26.log`, 1089 s, fine grids.

## 1. The anchor: the U.S. at the OECD inputs

| Quantity | cps (the paper's turnout) | cses (OA) | Source |
|---|---|---|---|
| λ | **11.218** | **13.575** | `A` p |
| ω | **1.2946** | **1.2877** | `A` ω |
| θ = 2 − 1/I, I = 39.2/49.6 = 0.790 | 0.735 | 0.735 | `A` θData |
| design in force in 2020 − θ (λ's target) | 4.4e-12 | −1.6e-12 | `A` designResidual |
| design chosen in 2020 (in force in 2050) | 0.805 | 0.804 | `A` θChosen |
| τ_2020 (target 7.366% of GDP / 0.7) | 10.52% | 10.52% | `A` τ2020 |
| R_2020 (a prediction; the U.S. target is 2.443) | 2.4423 | 2.4420 | `A` R2020 |
| Ṽ at the U.S. percentiles (CPS groups: 0.436) | 0.333 | 0.333 | `A` Vtilde |
| 1 − f(θ), 1 − f(0) | 1.4%, 17.9% | 1.7%, 21.2% | `A` fStar, f0 |

C1's U.S. (`notes/ledger_C1.md`) has λ 11.564 at the CPS groups (Ṽ 0.436), θ* 0.728 and β, ω recalibrated with the
cost; the anchor's λ is 3% lower at the OECD groups (Ṽ 0.333), θ 0.735 and the no-cost β. The λ scan (12 points on
[0.5, 200]) has one sign change, between 7.62 and 13.13 (cps).

## 2. Figure 1.1's relations: slope (s.e.) [direction count]

OLS on figure 1.1's regressors (`F`: OECD population 2020/1990, WIID Gini) for data and model alike; model index
1/(2 − θ), model spending 100τ(1 − α) at the observed design. **[a/25]**: of the 25 countries other than the U.S., the
number whose value lies on the side of the U.S.'s that the data's fitted line predicts from the country's regressor
(the model's own index where the regressor is the index); in the Data column, the data's own points. Layer 2
matches spending by construction ("targeted"); spending does not depend on the design reading ("as chosen").

**cps, the 26** (`OECD26_Slopes` prints the "chosen" columns):

| Relation | Data | L1 chosen | L1 in force | L2 chosen | L2 in force |
|---|---|---|---|---|---|
| spending on growth | −12.84 (3.67) [22/25] | −16.50 (0.59) [25/25] | as chosen | targeted | targeted |
| spending on Gini | +17.80 (23.90) [7/25] | −10.20 (18.23) [6/25] | as chosen | targeted | targeted |
| spending on index | +16.33 (3.67) [17/25] | +65.97 (14.21) [22/25] | +40.18 (6.25) [23/25] | +78.07 (12.42) [19/25] | +51.14 (7.70) [21/25] |
| index on growth | −0.446 (0.162) [18/25] | −0.126 (0.025) [22/25] | −0.281 (0.036) [23/25] | −0.093 (0.041) [20/25] | −0.190 (0.059) [22/25] |
| index on Gini | +0.887 (0.978) [11/25] | −0.413 (0.172) [3/25] | −0.737 (0.330) [4/25] | −0.163 (0.242) [3/25] | −0.222 (0.378) [3/25] |

On the same side of the U.S. as the country's own datum, by variable: L1 spending 22/25, index 15/25 (chosen) and
16/25 (in force); L2 index 15/25 (chosen), 17/25 (in force).

**Signs.** Both layers and both readings have the data's sign on spending–growth (−), spending–index (+) and
index–growth (−). On the two Gini relations, flat in the data (t = 0.74 and 0.91), the model's sign is the opposite;
layer 1's index–Gini slope is significant (t = −2.4 chosen, −2.2 in force), layer 2's is not. Magnitudes: layer 1's
spending–growth slope is 1.3 times the data's; the index–growth slope is 28% (chosen) or 63% (in force) of it; the
model's spending–index slope is 2.5 to 4.8 times the data's (its designs vary much less: below).

**cses, the 25 without Luxembourg** (data slopes on the same 25; [a/24]):

| Relation | Data | L1 chosen | L1 in force | L2 chosen | L2 in force |
|---|---|---|---|---|---|
| spending on growth | −16.74 (4.00) [22/24] | −16.52 (0.54) [24/24] | as chosen | targeted | targeted |
| spending on Gini | +18.67 (24.67) [7/24] | −5.81 (16.35) [5/24] | as chosen | targeted | targeted |
| spending on index | +16.39 (3.75) [16/24] | +83.50 (8.27) [15/24] | +52.03 (4.08) [21/24] | +79.41 (6.17) [18/24] | +48.56 (4.60) [19/24] |
| index on growth | −0.620 (0.176) [18/24] | −0.162 (0.017) [15/24] | −0.288 (0.018) [21/24] | −0.191 (0.048) [16/24] | −0.352 (0.067) [17/24] |
| index on Gini | +0.875 (1.011) [11/24] | +0.103 (0.176) [14/24] | −0.012 (0.295) [8/24] | +0.362 (0.285) [13/24] | +0.424 (0.460) [12/24] |

With each country's own turnout the index–Gini slope takes the data's sign in layer 2 (+0.36, +0.42, insignificant)
and in layer 1 on the chosen reading (+0.10); which turnout profiles do it is not decomposed here. Same side of the
U.S. as the datum: L1 index 17/24 under both readings, L2 18/24 and 17/24.

**All 29 (OA, cps):** data −12.49, −6.97, +15.87, −0.328, +0.629 (spending–growth, –Gini, –index, index–growth,
–Gini); layer 1 −16.39, −24.12, +72.04 (+39.96 in force), −0.125 (−0.301), −0.341 (−0.837); layer 2 targeted,
targeted, +81.48 (+46.99), −0.086 (−0.197), −0.167 (−0.447). Only the data's spending–Gini sign moves with the
sample, as `notes/data_oecd29.md` found; it then shares the model's.

## 3. The two design readings, side by side (for the checkpoint-2 decision)

"Chosen" is θPolicy_2020 at the observed design, in force from 2050 (the brief's reading; the builders' default);
"in force" is the design in force in 2020 on the freely simulated path, chosen in 1990 (G.1's reading and λ's
target). The data's θ over the 26 has mean 0.712 and standard deviation 0.300 (0 for Australia and Ireland, 1 for six).

| Over the 26 (cps) | L1 chosen | L1 in force | L2 chosen | L2 in force |
|---|---|---|---|---|
| range of θ | 0.796 (AUS) – 0.929 (FIN) | 0.522 (LUX) – 0.924 (SWE) | 0.748 (IRL) – 0.951 (ITA) | 0.575 (IRL) – 0.937 (FIN) |
| mean, s.d. | 0.875, 0.041 | 0.824, 0.092 | 0.873, 0.052 | 0.826, 0.093 |
| index on growth (data −0.446) | −0.126 | −0.281 | −0.093 | −0.190 |
| spending on index (data +16.3) | +66.0 | +40.2 | +78.1 | +51.1 |
| the U.S. (datum 0.735) | 0.805 | 0.735 | 0.805 | 0.735 |

The in-force reading is closer to the data on every index relation and sits on the U.S. datum by construction; the
chosen reading is one period later on each country's design path (+0.07 for the U.S.). Under cses the means are 0.797/0.734 (L1)
and 0.785/0.711 (L2). G.1's two countries under layer 2: the UK 0.823 chosen, 0.802 in force (observed 0.559; C1's
G.1 at its own groups: 0.698); France 0.923, 0.902 (observed 1).

## 4. By country: the inputs, ω (layer 2) and both readings (cps; `L1`, `L2`, `S`)

| Country | ν2020 | Ṽ | spending | I | θ | ω L2 (cses) | L1 chosen / in force | L2 chosen / in force | L1 spending |
|---|---|---|---|---|---|---|---|---|---|
| Australia | 1.503 | 0.202 | 4.16 | 0.499 | 0.000 | 1.331 (1.262) | 0.796 / 0.659 | 0.801 / 0.697 | 3.83 |
| Austria | 1.162 | 0.161 | 14.35 | 1.000 | 1.000 | 1.610 (1.610) | 0.878 / 0.851 | 0.922 / 0.903 | 9.78 |
| Belgium | 1.159 | 0.104 | 11.47 | 0.643 | 0.445 | 1.459 (1.433) | 0.917 / 0.901 | 0.932 / 0.927 | 9.22 |
| Canada | 1.374 | 0.171 | 6.38 | 0.729 | 0.629 | 1.291 (1.260) | 0.826 / 0.754 | 0.826 / 0.753 | 6.42 |
| Czech Republic | 1.024 | 0.170 | 8.64 | 0.603 | 0.343 | 1.141 (1.117) | 0.898 / 0.876 | 0.872 / 0.847 | 10.73 |
| Denmark | 1.134 | 0.116 | 8.20 | 0.639 | 0.436 | 1.203 (1.171) | 0.900 / 0.896 | 0.878 / 0.872 | 9.57 |
| Finland | 1.109 | 0.094 | 12.56 | 1.000 | 1.000 | 1.411 (1.411) | 0.929 / 0.922 | 0.949 / 0.937 | 10.75 |
| France | 1.156 | 0.150 | 14.44 | 1.000 | 1.000 | 1.610 (1.610) | 0.877 / 0.851 | 0.923 / 0.902 | 9.87 |
| Germany | 1.049 | 0.148 | 11.21 | 0.892 | 0.880 | 1.247 (1.237) | 0.901 / 0.878 | 0.898 / 0.875 | 12.00 |
| Greece | 1.043 | 0.225 | 17.87 | 0.857 | 0.833 | 1.709 (1.689) | 0.893 / 0.849 | 0.924 / 0.900 | 12.22 |
| Hungary | 0.939 | 0.265 | 7.70 | 1.000 | 1.000 | 0.947 (0.947) | 0.876 / 0.871 | 0.797 / 0.773 | 14.23 |
| Iceland | 1.439 | 0.112 | 3.04 | 0.711 | 0.593 | 1.145 (1.117) | 0.872 / 0.779 | 0.823 / 0.624 | 5.37 |
| Ireland | 1.418 | 0.240 | 3.25 | 0.500 | 0.000 | 1.155 (1.096) | 0.800 / 0.722 | 0.748 / 0.575 | 4.48 |
| Italy | 1.051 | 0.134 | 17.41 | 1.000 | 1.000 | 1.688 (1.688) | 0.920 / 0.880 | 0.951 / 0.929 | 11.89 |
| Japan | 1.024 | 0.124 | 9.60 | 0.750 | 0.667 | 1.136 (1.119) | 0.926 / 0.896 | 0.902 / 0.853 | 12.21 |
| Korea (outside the 26) | 1.176 | 0.229 | 3.52 | 0.724 | 0.619 | 0.939 (0.907) | 0.876 / 0.802 | 0.800 / 0.525 | 9.43 |
| Luxembourg | 1.652 | 0.187 | 9.04 | 0.847 | 0.820 | 1.761 (--) | 0.797 / 0.522 | 0.876 / 0.835 | 2.87 |
| Mexico (outside the 26) | 1.531 | 0.163 | 4.58 | 0.756 | 0.678 | 1.310 (1.280) | 0.827 / 0.649 | 0.829 / 0.671 | 4.36 |
| Netherlands | 1.173 | 0.116 | 6.76 | 0.953 | 0.951 | 1.129 (1.125) | 0.898 / 0.873 | 0.852 / 0.822 | 9.61 |
| New Zealand | 1.492 | 0.141 | 5.14 | 0.604 | 0.344 | 1.345 (1.301) | 0.850 / 0.721 | 0.856 / 0.751 | 4.50 |
| Norway | 1.268 | 0.101 | 7.58 | 0.759 | 0.683 | 1.274 (1.252) | 0.900 / 0.875 | 0.898 / 0.873 | 7.91 |
| Poland | 1.003 | 0.240 | 11.42 | 0.962 | 0.961 | 1.203 (1.200) | 0.879 / 0.850 | 0.873 / 0.828 | 12.96 |
| Portugal | 1.038 | 0.249 | 13.62 | 0.982 | 0.981 | 1.386 (1.384) | 0.871 / 0.848 | 0.876 / 0.857 | 12.19 |
| Spain | 1.220 | 0.183 | 12.81 | 1.000 | 1.000 | 1.571 (1.571) | 0.876 / 0.822 | 0.903 / 0.875 | 8.76 |
| Sweden | 1.210 | 0.081 | 8.48 | 0.868 | 0.848 | 1.266 (1.256) | 0.927 / 0.924 | 0.925 / 0.922 | 8.95 |
| Switzerland | 1.287 | 0.127 | 6.86 | 0.831 | 0.796 | 1.240 (1.228) | 0.876 / 0.829 | 0.872 / 0.811 | 7.74 |
| Turkey (outside the 26) | 1.537 | 0.224 | 7.38 | 1.000 | 1.000 | 1.527 (1.527) | 0.829 / 0.622 | 0.872 / 0.760 | 4.01 |
| United Kingdom | 1.174 | 0.185 | 7.84 | 0.694 | 0.559 | 1.199 (1.177) | 0.849 / 0.840 | 0.823 / 0.802 | 9.26 |
| United States (anchor) | 1.340 | 0.333 | 7.37 | 0.790 | 0.735 | 1.295 (1.288) | 0.805 / 0.735 | 0.805 / 0.735 | 7.37 |

ω over the 26 runs from 0.947 (Hungary) to 1.761 (Luxembourg), the U.S. 1.295. At θ = 1 the tax is eq (1.4) of
`notes/theory_closedForm.md`, free of the income distribution and of turnout, so the six countries there have the
same ω under both turnout readings (Austria and France 1.610 at nearly the same spending and ν).

## 5. Counts and checks

- Every solved row, anchors and both layers under both readings (2 + 114): nEqMax 1, nCandMax 3, nFallback 0 (`A`,
  `L1`, `L2`). Luxembourg under cses has status `noTurnout` (no CSES election) and counts −1.
- The tax at θ ≡ 1 against eq (1.4) at each row's ω and each date's ν: largest gap 2.6e-11 over 118 rows; the τ = 0
  corner at 1960 and 1990 for Mexico and Turkey (layer 1) and Korea and Mexico (layer 2) (`closedFormGap`,
  `closedFormCorners`).
- τPolicy_2020(θ_c) against the θ-pinned path: ≤ 3.4e-11 (`τPinGap`); the design choice is state-free (spread over
  the 41 states ≤ 4.5e-12, `θStateSpread`, the log separability); no chosen design at a corner (`atBoundChosen`);
  layer 2 matches spending to 1.7e-15 (`calResidual`).
- Wall time: anchors 171 s (cps) and 127 s (cses); layers 132 + 255 s (cps) and 89 + 311 s (cses).

## 6. Decisions the plan did not make, one line each

1. β is imposed at the U.S. calibration without the cost (ρ = 1), G.1's convention, on the anchor too; R is a prediction.
2. Both design readings are written; the builders default to "chosen" (the brief's), "in force" (G.1's) by argument.
3. Data and model are regressed on figure 1.1's own regressors over the same countries; spending is 100τ(1 − α).
4. I = grr100/grr050 exactly, not the four-digit `bbIndex` (at most 4.9e-5 apart).
5. A4's rule is a stage-(0) file of its own (`python/paper/oecd26Sample.py`); countries without an ILO series stay in.
6. Common X only, h0 at the U.S. workweek everywhere (hours levels move no rate under log).
7. Under cses the anchor is recalibrated at the U.S. CSES turnout, and Luxembourg drops out of data and model alike.
8. Layer 2's ω is calibrated with the cost on at the anchor's λ and θ at θ_c (as `runESC.stageCountry`); `size` only.
