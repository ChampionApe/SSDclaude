# θ variant C against the paper, ρ = 1 (2026-10-30)

Variant C (`notes/thetaTau_alternatives.md`, `data/oecd26_theta.csv`: 21 countries, U.S. θ = 0.5445) as run into
`results/oecd26_theta_C/` (`logs/thetaC/run.sh`) against the paper's `results/`, both read by the paper's own readers and
builders, C through path patches (`logs/thetaC/compare.py`, `tables.py`, `checks.py`; numbers in `compare_out.json`).
Paper = before, C = after. First pass, nothing decided. **Self-check:** from `results/` the builders `oecd26Slopes`,
`oecd26Omega`, `escCountryTable`, `escCalibrationTable`, `usukfrCalibration(US, FR)` rebuild `writing/Paper/Tables/*.tex`
byte for byte (banner aside); figures 6.1 and 7.1's ρ = 1 marks, appendix H's 17 of 25 (base 14) and review O4's r 0.59,
Spearman 0.50, RMSE 0.29 against 0.30 are reproduced exactly.

## 1. U.S. calibration (section 6), common X

`calibration/US_rhoGridCommonX.csv`, row ρ = 1 (θ: `usCalibrationSummary.csv`, C's `θ0`; s/Y: the shock csv's baseline).
Both hit τ = 10.52% and R = 2.443 (residual 4.5e-13, 2.1e-12; one candidate, no fallback).

| | θ | β | ω | X | s/Y |
|---|---|---|---|---|---|
| paper | 0.7278 | 0.6555 | 1.2309 | 4.159 | 15.30% |
| C | 0.5445 | 0.6515 | 1.1746 | 4.075 | 15.33% |
| diff | −0.1833 | −0.0040 | −0.0563 | −0.084 | +0.02 p.p. |

## 2. Section 6 counterfactuals (figure 6.1)

`shocks/US_shocksCommonX.csv`, `full` minus `Baseline` (`figuresUS.usOverview`): τ in p.p., s/Y in p.p. of GDP, workweek
in hours. **The corners are now measured from θ = 0.544, not 0.728.**

| scenario | τ paper | τ C | diff | s/Y paper | s/Y C | diff | ww paper | ww C | diff |
|---|---|---|---|---|---|---|---|---|---|
| θ = 0 | +4.34 | +3.07 | −1.27 | −1.12 | −0.79 | +0.33 | −1.73 | −1.26 | +0.47 |
| θ = 1 | −2.27 | −3.60 | −1.33 | +0.74 | +1.18 | +0.44 | +0.70 | +1.14 | +0.44 |
| θ 1 → 0 | +6.61 | +6.67 | +0.07 | −1.86 | −1.98 | −0.11 | −2.43 | −2.40 | +0.03 |
| Mild ageing | +3.99 | +3.94 | −0.05 | −0.98 | −0.97 | +0.01 | −0.29 | −0.29 | 0.00 |
| Acute ageing | +8.65 | +8.56 | −0.09 | −2.05 | −2.02 | +0.03 | −0.69 | −0.68 | 0.00 |
| French income distr. | −1.29 | −2.02 | −0.73 | +0.47 | +0.74 | +0.27 | +0.98 | +1.15 | +0.18 |
| French voting | +0.93 | +1.45 | +0.52 | −0.34 | −0.52 | −0.18 | −0.20 | −0.33 | −0.12 |
| French leisure | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | −4.03 | −4.17 | −0.14 |
| All French | −0.62 | −0.94 | −0.32 | +0.23 | +0.34 | +0.11 | −3.29 | −3.36 | −0.08 |
| France (own calibration) | +10.10 | +10.10 | 0.00 | −2.94 | −3.02 | −0.08 | −4.15 | −4.15 | 0.00 |

Section 6's "6.6 p.p. ... 1.9 p.p. of GDP ... 2.4 hours, 1.7 of them between the observed design and the Beveridgean
corner" → 6.7, 2.0, 2.4, **1.3**; "income −1.3 p.p., voting +0.9" → **−2.0, +1.5**; ageing unchanged. France keeps θ = 1.

## 3. Section 7

**Calibration** (`esc/escCalibration.csv`; paper's `sizePiR` in `escCalibrationCosts.csv`). Elast.: λ over appendix C's
0.1–0.4 × Π/R, "51 to 205 times". λ and ε fall by 45%. Section 7.2's "θ exceeds 0.5 in 23 of 29" → θ_C, 13 of 21.

| | λ | ε | U.S. Π/R | ω, β (`size`) | 1 − f(θ*) | 1 − f(0) | chosen 2050 | elast. |
|---|---|---|---|---|---|---|---|---|
| paper | 11.345 | 20.445 | 0.5549 | 1.280, 0.6549 | 1.9% | 22.9% | 0.802 | 51–204× |
| C | 6.247 | 11.260 | 0.5548 | 1.247, 0.6505 | 2.9% | 13.3% | 0.662 | 28–113× |

**Path** (`esc/escPath.csv`; G.2: "0.728 in 2020 to 0.802 in 2050 ... 0.820 from 2110 ... 16.9%, 0.3 p.p. above").

| | 1990 | 2020 | 2050 | 2080 | 2110 | τ 2110 | over pinned |
|---|---|---|---|---|---|---|---|
| paper | 0.697 | 0.728 | 0.802 | 0.819 | 0.820 | 16.85% | +0.29 p.p. |
| C | 0.498 | 0.544 | 0.662 | 0.690 | 0.692 | 16.62% | +0.42 p.p. |

**With the design chosen** (paper `esc/escExperiments.csv`, C `esc/escShocks.csv`; figure 7.1's reading, each against its
own baseline; Δθ from θ*).

| scenario | θ₂₀₂₀ paper | θ₂₀₂₀ C | Δθ paper | Δθ C | Δτ pinned paper | C | Δτ chosen paper | C |
|---|---|---|---|---|---|---|---|---|
| Mild ageing | 0.791 | 0.645 | +0.063 | **+0.100** | +3.61 | +3.40 | +3.75 | +3.60 |
| Acute ageing | 0.837 | 0.719 | +0.109 | **+0.175** | +7.83 | +7.37 | +8.25 | +7.98 |
| French income distr. | 0.749 | 0.557 | +0.021 | +0.012 | −0.68 | −1.07 | −0.68 | −1.06 |
| French voting | 0.654 | 0.446 | −0.073 | −0.098 | +0.85 | +1.26 | +0.86 | +1.25 |
| French leisure | 0.728 | 0.544 | 0.000 | 0.000 | 0.00 | 0.00 | 0.00 | 0.00 |
| All French | 0.615 | 0.356 | −0.112 | −0.189 | −0.05 | −0.06 | +0.01 | +0.02 |

Section 7.2's "7.8 p.p. rather than 8.7" → 7.4 rather than 8.6; income "lowers it by only 0.7 p.p., about half as much,
and by less than France's voting profile raises it" → 1.1, below 1.3: holds; savings fall more chosen than pinned (acute
−1.95, −1.74; paper −2.00, −1.86): holds. Not rerun: the footnotes' three-step income split and 70/30 split.

**UK and France under the U.S. λ** (`esc/escCountry.csv`, `size`; C ran no ε country stage).

| | θ observed | chosen, paper (λ 11.34) | chosen, C (λ 6.25) | own λ paper | own λ C |
|---|---|---|---|---|---|
| UK | 0.560 | 0.690 | **0.472** | 7.740 | 7.743 |
| France | 1.000 | 0.795 | 0.657 | -- | -- |

G.1's "ordered as observed, with the U.S. at 0.728 between them" → **fails**: chosen UK 0.472 < U.S. 0.544 < France 0.657,
observed U.S. 0.544 < UK 0.560. "A quarter of each under λ" → France 0.25, the UK moves away; "own λ 7.74, a third below
the U.S." → 24% **above**. **Corner slopes** (`esc/escCornerSlope.csv`): France at θ₂₀₂₀ = 1 (1990 vote) −0.0998 →
−0.0993, λ-free to 1e-7 at λ = 0, the U.S. λ, 100; `_frenchCornerFalls` passes on both. U.S. at λ = 0 −0.1371 → −0.1372.

## 4. The OECD cross-section (`sizePiR`, common β)

**26**: the paper; **21**: the paper's rows on C's 21; **C**: variant C, data side I = 1/(2 − θ_C) (spending data
identical). `anchor.csv`, `layer1.csv`, `layer2.csv` through `tablesOECD26.slopes`/`panelData`.

| anchor, paper / C | ω | ε (λ₂₀₂₀ = εΠ/R) | θ in force = observed | θ chosen 2020 |
|---|---|---|---|---|
| U.S. turnout | 1.294 / 1.269 | 20.01 (11.11) / 10.78 (5.98) | 0.735 / 0.544 | 0.795 / 0.644 |
| own turnout | 1.287 / 1.257 | 24.21 (13.44) / 13.09 (7.27) | 0.735 / 0.544 | 0.794 / 0.642 |

H.2's "ω = 1.29 and ε = 20.01, against 20.44 at the CPS groups" → 1.27, 10.78 against 11.26; its 0.728/0.735 gap goes.

**Table 5's slopes**, slope (s.e.); `targ.`: layer 2 matches spending; `cses`: own turnout, without LUX.

| | data 26 | data 21 | data C | L1 26 | L1 21 | L1 C | L2 26 | L2 21 | L2 C |
|---|---|---|---|---|---|---|---|---|---|
| spending on growth | −12.84 (3.67) | −10.89 (4.11) | −10.89 (4.11) | −16.75 (0.57) | −16.42 (0.65) | −16.12 (0.52) | targ. | targ. | targ. |
| spending on Gini | 17.80 (23.90) | 13.04 (25.40) | 13.04 (25.40) | −10.97 (18.46) | −11.75 (20.14) | −13.77 (19.60) | targ. | targ. | targ. |
| spending on index | 16.33 (3.67) | 16.79 (3.98) | 16.33 (3.91) | 42.06 (8.02) | 39.81 (8.82) | 28.87 (6.61) | 58.14 (10.35) | 54.31 (12.27) | 36.00 (8.30) |
| index on growth | −0.45 (0.16) | −0.38 (0.18) | −0.44 (0.18) | −0.23 (0.04) | −0.23 (0.04) | −0.31 (0.06) | −0.15 (0.05) | −0.12 (0.06) | −0.18 (0.09) |
| index on Gini | 0.89 (0.98) | 1.03 (1.03) | 0.88 (1.06) | −0.67 (0.29) | −0.66 (0.33) | −0.88 (0.44) | −0.24 (0.31) | −0.37 (0.32) | −0.46 (0.49) |
| cses: spending on index | 16.39 (3.75) | 16.84 (4.05) | 16.90 (3.94) | 66.59 (5.45) | 70.11 (7.05) | 52.71 (5.04) | 61.94 (6.94) | 73.42 (8.88) | 55.39 (6.75) |
| cses: index on growth | −0.62 (0.18) | −0.58 (0.21) | −0.77 (0.18) | −0.22 (0.02) | −0.21 (0.02) | −0.26 (0.02) | −0.27 (0.05) | −0.23 (0.05) | −0.30 (0.07) |
| cses: index on Gini | 0.87 (1.01) | 1.04 (1.07) | 0.80 (1.10) | 0.06 (0.23) | 0.05 (0.23) | 0.08 (0.29) | 0.40 (0.35) | 0.23 (0.32) | 0.35 (0.42) |

p, U.S. turnout (`checks.log`): index on growth, data 0.011 / 0.050 / 0.022, L2 0.005 / 0.046 / **0.052**; index on Gini,
L1 0.032 / **0.061** / 0.061. Section 7.3's "−0.23 against −0.45" → −0.31 against −0.44; "−0.67 against 0.89,
significantly" → −0.88 against 0.88, not at 5%: the sample loses it, not the measure.

**Layer 2**, the U.S. left out of counts and correlations (its design is the target).

| | cps 26 | cps 21 | cps C | cses 26 | cses 21 | cses C |
|---|---|---|---|---|---|---|
| ω range | HUN 0.95 – LUX 1.76 | same | HUN 0.95 – LUX 1.75 | HUN 0.95 – ITA 1.69 | same | HUN 0.95 – ITA 1.68 |
| predicted θ range | IRL 0.618 – FIN 0.924 | same | IRL 0.218 – FIN 0.869 | ISL 0.353 – ITA 0.831 | IRL 0.472 – ITA 0.831 | IRL 0.000 – ITA 0.710 |
| same side of the U.S. as observed | 17 / 25 | 13 / 20 | 13 / 20 | 18 / 24 | 15 / 19 | 17 / 19 |
| base rate (observed above the U.S.) | 14 / 25 | 12 / 20 | 12 / 20 | 13 / 24 | 11 / 19 | 11 / 19 |
| predicted above the U.S. | 22 | 19 | 19 | 11 | 11 | 11 |
| Pearson, Spearman (predicted, observed θ) | 0.59, 0.50 | 0.62, 0.45 | 0.50, 0.35 | 0.62, 0.68 | 0.77, 0.65 | 0.79, 0.78 |
| RMSE (of the observed mean) | 0.29 (0.30) | 0.26 (0.28) | 0.30 (0.32) | 0.25 (0.31) | 0.23 (0.29) | 0.23 (0.33) |
| layer 1: same side; Pearson, Spearman | 16; 0.35, 0.30 | 13; 0.26, 0.25 | 13; 0.17, 0.22 | 14; 0.63, 0.44 | 11; 0.57, 0.36 | 13; 0.74, 0.72 |

**Corners and movers.** Data: eight corners in the paper's 26 (AUS, IRL at 0; AUT, FIN, FRA, HUN, ITA, ESP at 1), C's 21
IRL at 0, NZL 0.003, HUN 0.997; model: none but IRL (C, layer 2, own turnout, exactly 0). Every predicted design falls
(layer 2, cps: FIN −0.055 to IRL −0.400; mean 0.834 → 0.707, observed 0.750 → 0.605): IRL 0.618 → 0.218, NZL 0.760 →
0.584, CAN 0.768 → 0.600, HUN 0.765 → 0.601, GBR 0.791 → 0.649; layer 1 LUX 0.528 → 0.187. Observed most: SWE 0.848 →
0.383, NZL 0.344 → 0.003, GBR 0.559 → 0.181, NOR 0.683 → 0.313. H.3's UK "0.791, above the U.S. at 0.735" → 0.649 above
0.544 (observed 0.181), still an exception; France "0.879, about half of the way to its corner" → 0.790 (obs. 0.822).

## 5. Main differences

1. **The cost halves**: λ 11.34 → 6.25, ε 20.44 → 11.26 (anchor 20.01 → 10.78); ω 1.231 → 1.175 without it; the observed
   design loses 2.9% of revenue (1.9%), a flat benefit 13.3% (22.9%).
2. **Section 6's corner bar is re-split**: 1 → 0 still +6.7 p.p., but θ = 0 adds 3.1 (4.3) and θ = 1 takes 3.6 (2.3); the
   workweek at θ = 0 falls 1.3 h, not 1.7. Income and voting move τ by half again (−2.0, +1.5 p.p.).
3. **The design responds more**: acute +0.175 (+0.109), mild +0.100 (+0.063), voting −0.098 (−0.073); path to 0.692 (0.820).
4. **The UK deep test breaks**: the UK chooses 0.472 (0.690) against its 0.560, now above the U.S.'s 0.544; its own λ is 24%
   above the U.S. one, not a third below. France 0.657 (0.795), a quarter of the way, as before.
5. **The slopes move towards the data** (same 21): index on growth L1 −0.23 → −0.31, L2 −0.12 → −0.18 (data −0.38 → −0.44);
   spending on index L1 39.8 → 28.9, L2 54.3 → 36.0 (data 16.3). The 26 → 21 sample alone costs index–Gini L1 (p 0.061).
6. **Validation worse at U.S. turnout, better at own**: layer 2 13 of 20 against a base of 12, r 0.62 → 0.50, Spearman 0.45
   → 0.35 (19 of 20 above the U.S.); own turnout 17 of 19 against 11, r 0.77 → 0.79, Spearman 0.65 → 0.78.

**Flags.**
- No failed or unconverged row. The logs' inner-solve failures are the scans' top nodes (p = 200, `size`; 400, `sizePiR`,
  both anchors), 30–37 times the root, whose sign changes lie at 4.4–7.6 and 8.8–15.2: no root at a bracket edge. Final rows
  `converged`, residuals ≤ 5e-11, one candidate, no fallback; layer rows `ok` (LUX `noTurnout`, cses), ΠRgap ≤ 1e-10.
  `sizePiR`'s τDrift −2.4e-6 (paper −8e-7) and RDrift 0.004 (0.003) are larger but small.
- **Measurement mismatch in the deep test**: the U.S. at C's 0.544, the UK and France at their workbooks' 0.560 and 1.000
  (C: 0.181, 0.822). At 0.822 France is interior, so G.1's corner argument may not carry over; section 6's France row and
  French counterfactuals keep θ_FR = 1 too. IRL's model corner is invisible to `atBoundChosen` (2020 choice only).
- Not run under C: the spending test without the cost (`none`; figure 6.2, "ω 1.26"), the ε country stage, CRRA, appendix
  H's `size`/`commonR` variants, `OECD26_Reconcile`. C's rows say `commit` cea6613, but the `--theta` code is uncommitted.
