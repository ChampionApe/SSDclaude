# Ledger R6: the cross-section's variants, the deep test under ε, the builders

Package R6 of `notes/plan_byObject.md`, 2026-10-27, branch `review-2026-10` (C14 uncommitted beneath). Checkpoint 1's
input. Every number below is read off the csv named beside it; `results/oecd26/*.csv` rows are keyed on (turnout,
spec, phi 0.5, commonX True, betaRule[, iso3]). Logs: `logs/R6/`. Numbers assembled by `logs/R6/ledger_numbers.py`
and `logs/R6/paper_numbers.py` (read-only on `results/`).

## 1. Self-checks

| check | result | where |
|---|---|---|
| (i) `python/US/test_oecd26.py` | 45/45 pass. Test M: a forced recompute of GBR, layer 1, `size`/`common`/`cps` gives τ2020 0.1323514088148834 and θInForce 0.8365989778825912, \|Δ\| 0.0e+00 and 0.0e+00 against the row on disk; the other rows' max relative change 2.8e-16 (temporary copy) | `logs/R6/selfcheck_test_oecd26.log`; `results/oecd26/layer1.csv` (cps, size, 0.5, True, common, GBR) |
| (ii) the LOG `sizePiR` calibration, quoted, not rerun | ε (`p`) 20.444896, ΠR 0.554912 (ε·ΠR = 11.345, the paper's λ 11.344863), θ* 0.727757, β 0.654670, ω 1.279637, nEqMax 1, nFallback 0, converged; the `none` row β 0.655483, ω 1.230860 | `results/esc/escCalibrationCosts.csv` (sizePiR, 0.5, True); (none, NaN, True) |
| (iii) the legacy rows after every run (migration) | anchor 2, layer1 58, layer2 58 rows of `logs/R6/before/` all present; max \|Δ\| over the numeric columns 4.4e-16 (relative ≤ 1.0e-15, from `runESC.mergeWrite` rereading the csv with pandas' default parser before rewriting, see (iv)); no NaN or string mismatch; columns added: `betaRule` ('common' on every legacy row) and the new variants' `ΠR2020`, `ΠRgap`, `λEff2020`, `βAnchor`, `RTarget` (NaN on the legacy rows) | `logs/R6/compare_before.py`, `logs/R6/compare_before.log` |
| (iv) `python/US/test_oecd26.py` again, after the runs | 53/55. P passes for every spec × β rule (each row against its anchor, one equilibrium, no fallback). M's two "the other rows unchanged" checks fail at a relative change of 6.5e-13 (> 1e-13), GBR's τ2020 and θInForce again \|Δ\| 0.0: M's rewrite of the layer files goes through `runESC.mergeWrite`, which rereads the csv with pandas 3.0.3's default parser, and that parser keeps 16 digits after the decimal point (τPinGap 0.0001488994842999969 of the sizePiR/commonR/cses KOR row reads 0.0001488994842999). The rows a run writes last are at full precision until the next rewrite truncates them; nothing printed moves. Fix (not R6's file): `float_precision = 'round_trip'` in `mergeWrite` (`python/US/runESC.py:88`) | `logs/R6/test_US_oecd26_after.log` |

## 2. The anchors (results/oecd26/anchor.csv, key turnout, spec, phi 0.5, commonX True, betaRule common)

| spec | turnout | p (λ or ε) | ΠR2020 | λEff2020 = p·ΠR2020 | ω | β | R2020 | τ2020 | θData | θInForce | θChosen | status | nEqMax | nFallback | time (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | cps | -- | -- | -- | 1.258709 | 0.655483 | 2.4432 | 0.1052 | 0.7347 | -- | -- | ok | 1 | 0 | 8 |
| none | cses | -- | -- | -- | 1.244636 | 0.655483 | 2.4432 | 0.1052 | 0.7347 | -- | -- | ok | 1 | 0 | 8 |
| size | cps | 11.108624 | -- | -- | 1.294281 | 0.655483 | 2.4423 | 0.1052 | 0.7347 | 0.734694 | 0.8089 | ok | 1 | 0 | 317 |
| size | cses | 13.443497 | -- | -- | 1.287315 | 0.655483 | 2.4421 | 0.1052 | 0.7347 | 0.734694 | 0.8080 | ok | 1 | 0 | 284 |
| sizePiR | cps | 20.013665 | 0.555031 | 11.1082 | 1.294280 | 0.655483 | 2.4419 | 0.1052 | 0.7347 | 0.734694 | 0.7946 | ok | 1 | 0 | 1876 |
| sizePiR | cses | 24.214871 | 0.555146 | 13.4428 | 1.287313 | 0.655483 | 2.4416 | 0.1052 | 0.7347 | 0.734694 | 0.7938 | ok | 1 | 0 | 1057 |

## 3. Every slope of every variant (slope (s.e.); tablesOECD26.slopes on results/oecd26, sample 26, design in force in 2020)

The paper's variant is `sizePiR common cps`. Index on the Gini, where a verdict can flip: layer 1 negative and significant (|t| > 2) at U.S. turnout under every cost and β rule (−0.67 to −0.78), layer 2 not significant (−0.04 to −0.24); at own turnout layer 1 near zero (−0.04 to 0.09) and layer 2 positive, not significant (0.40 to 0.62), the data's sign. Spending on the Gini is negative in layer 1 in every variant against the data's positive, neither significant. Spending on growth and on the index keep the data's sign in every variant, significantly; the index on growth is negative everywhere, significantly except in layer 2 under ε with common R, −0.10 (0.06).

| relation | data cps (26) | data cses (25) | size common cps L1 | size common cps L2 | size commonR cps L1 | size commonR cps L2 | sizePiR common cps L1 | sizePiR common cps L2 | sizePiR commonR cps L1 | sizePiR commonR cps L2 | size common cses L1 | size common cses L2 | size commonR cses L1 | size commonR cses L2 | sizePiR common cses L1 | sizePiR common cses L2 | sizePiR commonR cses L1 | sizePiR commonR cses L2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| spending on growth | -12.84 (3.67) | -16.74 (4.00) | -16.49 (0.59) | targeted | -17.80 (0.53) | targeted | -16.75 (0.57) | targeted | -18.08 (0.48) | targeted | -16.49 (0.53) | targeted | -17.74 (0.52) | targeted | -16.87 (0.49) | targeted | -18.16 (0.43) | targeted |
| spending on gini | 17.80 (23.90) | 18.67 (24.67) | -10.25 (18.21) | targeted | -12.48 (19.53) | targeted | -10.97 (18.46) | targeted | -13.92 (19.75) | targeted | -5.86 (16.33) | targeted | -7.20 (17.51) | targeted | -6.81 (16.65) | targeted | -8.94 (17.84) | targeted |
| spending on index | 16.33 (3.67) | 16.39 (3.75) | 39.84 (6.25) | 51.27 (7.36) | 39.23 (6.13) | 50.89 (7.39) | 42.06 (8.02) | 58.14 (10.35) | 41.85 (8.76) | 50.47 (8.83) | 51.41 (4.00) | 48.55 (4.55) | 52.68 (4.18) | 48.52 (4.53) | 66.59 (5.45) | 61.94 (6.94) | 76.18 (7.18) | 56.20 (5.29) |
| index on growth | -0.45 (0.16) | -0.62 (0.18) | -0.28 (0.04) | -0.19 (0.06) | -0.31 (0.04) | -0.19 (0.06) | -0.23 (0.04) | -0.15 (0.05) | -0.23 (0.04) | -0.10 (0.06) | -0.29 (0.02) | -0.35 (0.07) | -0.30 (0.02) | -0.35 (0.07) | -0.22 (0.02) | -0.27 (0.05) | -0.20 (0.02) | -0.23 (0.07) |
| index on gini | 0.89 (0.98) | 0.87 (1.01) | -0.73 (0.33) | -0.19 (0.38) | -0.78 (0.37) | -0.19 (0.39) | -0.67 (0.29) | -0.24 (0.31) | -0.67 (0.30) | -0.04 (0.36) | -0.02 (0.30) | 0.42 (0.46) | -0.04 (0.31) | 0.42 (0.46) | 0.06 (0.23) | 0.40 (0.35) | 0.09 (0.21) | 0.62 (0.38) |

No cost (`none`, spending at the observed designs; `tablesOECD26.spendingSlopes`, layer 1):

| relation | data cps | none cps L1 | data cses | none cses L1 |
|---|---|---|---|---|
| spending on growth | -12.84 (3.67) | -14.90 (0.73) | -16.74 (4.00) | -13.05 (1.27) |
| spending on gini | 17.80 (23.90) | -15.65 (16.47) | 18.67 (24.67) | -11.93 (13.91) |

## 4. The deep test under both transports

θ*_US = 0.727757 (results/paper/usCalibrationSummary.csv, US, commonX True; the θStar of both cost calibrations). Share closed = (chosen − θ*_US)/(θ observed − θ*_US).

| country | θ observed | transport | U.S. parameter | ΠR (2020) | chosen | share closed | own parameter | own ΠR | ω (U.S. param) | nEqMax | nFallback | csv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UK | 0.559746 | size | 11.344863 | -- | 0.689672 | 0.227 | 7.739948 | -- | 1.166025 | 1.0 | 0.0 | results/esc/escCountry.csv |
| FR | 1.000000 | size | 11.344863 | -- | 0.795269 | 0.248 | none (not converged) | -- | 1.445707 | 1.0 | 0.0 | results/esc/escCountry.csv |
| UKUS | 0.542703 | size | 11.344863 | -- | 0.699360 | 0.153 | 7.120690 | -- | 1.183785 | 1.0 | 0.0 | results/esc/escCountry.csv |
| UK | 0.559746 | sizePiR | 20.444896 | 0.529273 | 0.672824 | 0.327 | 14.655035 | 0.528121 | 1.162993 | 1 | 0 | results/esc/escCountryCosts.csv |
| FR | 1.000000 | sizePiR | 20.444896 | 0.431610 | 0.743112 | 0.056 | none (not converged) | -- | 1.445707 | 1 | 0 | results/esc/escCountryCosts.csv |
| UKUS | 0.542703 | sizePiR | 20.444896 | 0.527096 | 0.683185 | 0.241 | 13.519042 | 0.526715 | 1.182746 | 1 | 0 | results/esc/escCountryCosts.csv |

The cross-section on the same two countries (layer 1 and layer 2, β rule common; θInForce; share against the anchor's observed U.S. design θData_USA):

| spec | turnout | anchor θData_USA | GBR θData | GBR L1 | GBR L2 | GBR share L1/L2 | FRA θData | FRA L1 | FRA L2 | FRA share L1/L2 |
|---|---|---|---|---|---|---|---|---|---|---|
| size | cps | 0.7347 | 0.5592 | 0.8366 | 0.8046 | -0.581 / -0.398 | 1.0000 | 0.8509 | 0.9035 | 0.438 / 0.636 |
| size | cses | 0.7347 | 0.5592 | 0.7707 | 0.7228 | -0.205 / 0.068 | 1.0000 | 0.7519 | 0.8283 | 0.065 / 0.353 |
| sizePiR | cps | 0.7347 | 0.5592 | 0.8169 | 0.7913 | -0.468 / -0.322 | 1.0000 | 0.8382 | 0.8788 | 0.390 / 0.543 |
| sizePiR | cses | 0.7347 | 0.5592 | 0.7434 | 0.7062 | -0.049 / 0.162 | 1.0000 | 0.7307 | 0.7843 | -0.015 / 0.187 |

Under ε each country faces λ_i = ε·ΠR_i: UK 10.821, FR 8.824 (the U.S. 11.345 at its calibration). The UK's own ε 14.655 is λ 7.740 at its ΠR 0.528, its own λ under `size` (7.739948): the UK's own calibration is one economy under both, and what differs is the U.S. parameter it faces, λ 11.345 against ε·ΠR_UK 10.821. The UK at U.S. income groups (`UKUS`) stays in both csvs and is no longer printed (R7).

## 5. The reconcile rows (`results/paper/Tables/OECD26_Reconcile.tex`, `% row:` keys)

Deep test: `results/paper/usCalibrationSummary.csv` (θ, ν2020, ω without the cost; US/UK/FR, commonX True), `results/esc/escCalibration{,Costs}.csv` (the U.S.: Ṽ, ω, θ* as its chosen design), `results/esc/escCountry{,Costs}.csv` (UK, FR, wedgeFrom US: Ṽ, ω, choice). Cross-section: `results/oecd26/anchor.csv` (USA) and `layer2.csv` (GBR, FRA), turnout cps, β rule common, under none, size and sizePiR; θInForce as the chosen design.

| key | quantity | deep U.S. | deep UK | deep France | cross U.S. | cross UK | cross France |
|---|---|---|---|---|---|---|---|
| `theta` | θ observed | 0.728 | 0.560 | 1.000 | 0.735 | 0.559 | 1.000 |
| `vtilde` | Ṽ | 0.436 | 0.223 | 0.218 | 0.333 | 0.185 | 0.150 |
| `nu` | ν2020 | 1.34 | 1.17 | 1.04 | 1.34 | 1.17 | 1.16 |
| `omega_none` | ω, no cost | 1.231 | 1.103 | 1.446 | 1.259 | 1.145 | 1.610 |
| `omega_size` | ω, U.S. λ | 1.280 | 1.166 | 1.446 | 1.294 | 1.198 | 1.610 |
| `chosen_size` | θ chosen, U.S. λ | 0.728 | 0.690 | 0.795 | 0.735 | 0.805 | 0.903 |
| `omega_sizePiR` | ω, U.S. ε | 1.280 | 1.163 | 1.446 | 1.294 | 1.196 | 1.610 |
| `chosen_sizePiR` | θ chosen, U.S. ε | 0.728 | 0.673 | 0.743 | 0.735 | 0.791 | 0.879 |

What differs between the two measurements: the U.S. design 0.728 (CPS groups) against 0.735 (OECD deciles); Ṽ lower in the OECD series for all three; France's ν2020 1.04 (with PaG 2021's retirement-age correction) against 1.16 (plain WPP ratio); France's ω 1.446 against 1.610 at every cost, the UK's 1.103 against 1.145 without the cost.

## 6. Counts (every row of results/oecd26/*.csv)

| file | spec | betaRule | turnout | status | rows | nEqMax values | nFallback values | rows outside (1, 0) |
|---|---|---|---|---|---|---|---|---|
| anchor | none | common | cps | ok | 1 | [1] | [0] | none |
| anchor | none | common | cses | ok | 1 | [1] | [0] | none |
| anchor | size | common | cps | ok | 1 | [1] | [0] | none |
| anchor | size | common | cses | ok | 1 | [1] | [0] | none |
| anchor | sizePiR | common | cps | ok | 1 | [1] | [0] | none |
| anchor | sizePiR | common | cses | ok | 1 | [1] | [0] | none |
| layer1 | none | common | cps | ok | 29 | [1] | [0] | none |
| layer1 | none | common | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer1 | none | common | cses | ok | 28 | [1] | [0] | none |
| layer1 | size | common | cps | ok | 29 | [1] | [0] | none |
| layer1 | size | common | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer1 | size | common | cses | ok | 28 | [1] | [0] | none |
| layer1 | size | commonR | cps | ok | 29 | [1] | [0] | none |
| layer1 | size | commonR | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer1 | size | commonR | cses | ok | 28 | [1] | [0] | none |
| layer1 | sizePiR | common | cps | ok | 29 | [1] | [0] | none |
| layer1 | sizePiR | common | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer1 | sizePiR | common | cses | ok | 28 | [1] | [0] | none |
| layer1 | sizePiR | commonR | cps | ok | 29 | [1] | [0] | none |
| layer1 | sizePiR | commonR | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer1 | sizePiR | commonR | cses | ok | 28 | [1] | [0] | none |
| layer2 | none | common | cps | ok | 29 | [1] | [0] | none |
| layer2 | none | common | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer2 | none | common | cses | ok | 28 | [1] | [0] | none |
| layer2 | size | common | cps | ok | 29 | [1] | [0] | none |
| layer2 | size | common | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer2 | size | common | cses | ok | 28 | [1] | [0] | none |
| layer2 | size | commonR | cps | ok | 29 | [1] | [0] | none |
| layer2 | size | commonR | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer2 | size | commonR | cses | ok | 28 | [1] | [0] | none |
| layer2 | sizePiR | common | cps | ok | 29 | [1] | [0] | none |
| layer2 | sizePiR | common | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer2 | sizePiR | common | cses | ok | 28 | [1] | [0] | none |
| layer2 | sizePiR | commonR | cps | ok | 29 | [1] | [0] | none |
| layer2 | sizePiR | commonR | cses | noTurnout | 1 | [-1] | [-1] | n/a |
| layer2 | sizePiR | commonR | cses | ok | 28 | [1] | [0] | none |

Every row of every variant: nEqMax 1, nFallback 0; the `noTurnout` rows are Luxembourg under cses (−1 by construction). Run e: every row of `results/esc/escCountryCosts.csv` nEqMax 1, nFallback 0, France's `own` row unconverged (−1), as under `size`.

## 7. Wall times

| run | command (`.venv\Scripts\python.exe`, `PYTHONUTF8=1`) | wall time | log |
|---|---|---|---|
| b | `python\US\runOECD26.py --spec none --stage anchor layer1 --turnout cps cses` (GBR probe, then all) | 35 + 57 s | `logs/R6/runs.log` (the step logs of b were overwritten by a broken log path, fixed before a) |
| b, layer 2 | `... --spec none --stage layer2 --turnout cps cses` | 104 s | `logs/R6/b_layer2.log` |
| a | `... --spec sizePiR --stage anchor layer1 layer2 --turnout cps cses` (GBR probe, then all) | 3147 + 3274 s (the anchors 1876 s cps, 1057 s cses); a first probe killed after 3.6 min, before any write | `logs/R6/a_probe.log`, `a.log` |
| c | `... --spec size --betaRule commonR --stage layer1 layer2 --turnout cps cses` | 44 + 870 s | `logs/R6/c_probe.log`, `c.log` |
| d, cps | `... --spec sizePiR --betaRule commonR --stage layer1 layer2 --turnout cps` | 86 + 1946 s | `logs/R6/d_probe.log`, `d_cps.log` |
| d, cses | `... --turnout cses` | 93 + 1974 s | `logs/R6/d_cses_probe.log`, `d_cses.log` |
| e | `python\US\runESC.py --stage country --spec sizePiR --phi 0.5 --commonX --tag Costs` (beside b and a) | 3413 s | `logs/R6/e.log`, `e_times.log` |

All runs: 13:57 to 17:16, 3 h 19 min of the 12 h budget; a to d one after another, e beside them. Nothing skipped: d's cses half and b's layer 2 ran within the budget.

Row times (sum of the csv `time` column, s):

| file | spec | betaRule | turnout | rows | sum | mean | max |
|---|---|---|---|---|---|---|---|
| anchor | none | common | cps | 1 | 8 | 8.4 | 8.4 |
| anchor | none | common | cses | 1 | 8 | 7.7 | 7.7 |
| anchor | size | common | cps | 1 | 317 | 316.6 | 316.6 |
| anchor | size | common | cses | 1 | 284 | 284.1 | 284.1 |
| anchor | sizePiR | common | cps | 1 | 1876 | 1875.7 | 1875.7 |
| anchor | sizePiR | common | cses | 1 | 1057 | 1057.3 | 1057.3 |
| layer1 | none | common | cps | 29 | 21 | 0.7 | 2.1 |
| layer1 | none | common | cses | 28 | 19 | 0.7 | 1.6 |
| layer1 | size | common | cps | 29 | 305 | 10.5 | 12.1 |
| layer1 | size | common | cses | 28 | 278 | 9.9 | 11.1 |
| layer1 | size | commonR | cps | 29 | 220 | 7.6 | 9.7 |
| layer1 | size | commonR | cses | 28 | 216 | 7.7 | 9.3 |
| layer1 | sizePiR | common | cps | 29 | 800 | 27.6 | 56.5 |
| layer1 | sizePiR | common | cses | 28 | 736 | 26.3 | 42.6 |
| layer1 | sizePiR | commonR | cps | 29 | 1006 | 34.7 | 58.6 |
| layer1 | sizePiR | commonR | cses | 28 | 1004 | 35.8 | 60.6 |
| layer2 | none | common | cps | 29 | 48 | 1.7 | 2.1 |
| layer2 | none | common | cses | 28 | 46 | 1.6 | 1.9 |
| layer2 | size | common | cps | 29 | 450 | 15.5 | 17.3 |
| layer2 | size | common | cses | 28 | 427 | 15.2 | 17.2 |
| layer2 | size | commonR | cps | 29 | 234 | 8.1 | 10.0 |
| layer2 | size | commonR | cses | 28 | 227 | 8.1 | 11.2 |
| layer2 | sizePiR | common | cps | 29 | 946 | 32.6 | 63.1 |
| layer2 | sizePiR | common | cses | 28 | 985 | 35.2 | 53.9 |
| layer2 | sizePiR | commonR | cps | 29 | 1017 | 35.1 | 69.7 |
| layer2 | sizePiR | commonR | cses | 28 | 1055 | 37.7 | 59.9 |

## 8. Paper sentences the main variant changes

Read at commit `aa89dc9` plus the working tree (`writing/Paper` unchanged there), read-only. Main variant: `sizePiR`,
β common, cps, the design in force in 2020; deep test under ε from `results/esc/escCountryCosts.csv`. "Holds" means
the number or verdict survives at the paper's rounding. Generated tables and notes (`OECD26_*`, `US_ESC_Country`)
change by the build and are not listed. `paper_numbers.py` reproduces every old value below from the `size` rows.

| file:line | sentence (abridged) | old → new | source (csv, row) |
|---|---|---|---|
| `abstract.tex:6` | "the model has pension spending and the earnings link rise together as population growth falls, as the data do, but it also relates the earnings link to inequality, which the data do not" | holds: L1 spending on growth −16.75 (0.57), index on growth −0.23 (0.04), index on Gini −0.67 (0.29), t = −2.3 | `results/oecd26/layer1.csv` (cps, sizePiR, common) |
| `Sections/Introduction.tex:27` | "it accounts for about a quarter of the distance of each from the U.S. design" | λ: 0.23 (UK), 0.25 (France) → ε: 0.33 (UK), 0.06 (France). **Verdict flips for France** ("a quarter of each" fails under ε) | `escCountry.csv` / `escCountryCosts.csv` (UK, FR; wedgeFrom US) |
| `Sections/Introduction.tex:27` | "though no value of it reproduces France's fully Bismarckian one" | holds under ε (no sign change in the scan; France's `own` row not converged) | `escCountryCosts.csv` (FR, own) |
| `Sections/Introduction.tex:27` | "reproduces the signs of the relations among pension spending, the index and population growth, with a weaker response of the index to population growth than in the data. Unlike the data, however, it ties more Beveridgean designs to higher inequality" | holds: index on growth −0.28 → −0.23 against −0.45 (weaker still); index on Gini −0.73 (0.33) → −0.67 (0.29), significant | `layer1.csv` (cps, sizePiR, common) |
| `Sections/Conclusion.tex:7` | "The U.S. cost parameter accounts for about a quarter of the distance of the UK and of France from the U.S. design" | 0.23 / 0.25 → 0.33 / 0.06. **Flips for France** | as above |
| `Sections/Conclusion.tex:7` | "the UK's own parameter is a third below the U.S. value at elasticities of one or below and a sixth above it at two" | at ρ = 1: λ 7.740 vs 11.345 (−32%) → ε 14.655 vs 20.445 (−28%, "a quarter below" rather than "a third"); ρ ≠ 1 not computed under ε | `escCountryCosts.csv` (UK, own; UK, US) |
| `Sections/Conclusion.tex:7` | "reproduces the first pattern in sign, though the earnings link responds less to population growth than in the data, and it leaves spending unrelated to inequality. Unlike the data, however, it ties more Beveridgean designs to higher inequality" | holds: spending on Gini −10.25 (18.21) → −10.97 (18.46); index on Gini −0.67 (0.29) | `layer1.csv` (cps, sizePiR, common) |
| `Sections/EndogenousTheta.tex:35` | "The parameter calibrated on the U.S. accounts for about a quarter of the distance from the U.S. design to the UK's and to France's" | 0.23 / 0.25 → 0.33 / 0.06 (the plan turns this into a pointer to 7.3) | `escCountryCosts.csv` |
| `Sections/EndogenousTheta.tex:69` | "the design that the calibration of λ targets" | λ → ε (the anchor's `p` is ε under `sizePiR`) | `anchor.csv` (cps, sizePiR) |
| `Sections/EndogenousTheta.tex:69` (footnote) | "0.809 for the U.S. at the data of the test against 0.802 on its baseline path" | 0.809 → 0.795 (anchor θChosen); the baseline path under ε has 0.788 in 2050 (against 0.802 under λ) | `anchor.csv` (cps, sizePiR) θChosen; `escPathCosts.csv` (sizePiR, pos 3) |
| `Sections/EndogenousTheta.tex:69` (footnote) | "its index falls with population growth at less than a third of the slope in the data, −0.13 against −0.45" | −0.13 → −0.09 against −0.45 ("about a fifth") | `tablesOECD26.slopes(reading = 'chosen', spec = 'sizePiR')` on `layer1.csv` |
| `Sections/EndogenousTheta.tex:71` | "Spending falls with population growth, at a slope 1.3 times that of the data" | 1.28 → 1.30: holds | `layer1.csv` (cps, sizePiR, common) |
| `Sections/EndogenousTheta.tex:71` | "and so does the index, less steeply, −0.28 against −0.45" | −0.28 → −0.23 | idem |
| `Sections/EndogenousTheta.tex:71` | "Its slope is 2.4 times that of the data" | 2.44 → 2.58 ("2.6 times") | idem (spending on index 42.06 (8.02) against 16.33 (3.67)) |
| `Sections/EndogenousTheta.tex:71` | "On the index they run from 0.672 to 0.928" | 0.672 (LUX) – 0.928 (SWE) → 0.680 (LUX) – 0.922 (SWE) | idem, `indexInForce` |
| `Sections/EndogenousTheta.tex:75` | "the index falls with it, −0.73 against 0.89 in the data, and significantly" | −0.73 (0.33) → −0.67 (0.29), t −2.2 → −2.3: holds | idem |
| `Sections/EndogenousTheta.tex:75` | "the second layer ... the index still falls with population growth, while its relation with the Gini is no longer significant" | holds: L2 index on growth −0.19 (0.06) → −0.15 (0.05), on Gini −0.19 (0.38) → −0.24 (0.31) | `layer2.csv` (cps, sizePiR, common) |
| `Appendix/OECD26.tex:3` | "Every economy is solved under log preferences with the cost of section ...; exactly one candidate tax passes at every state and date of every solve" | holds for every new row (section 6); the cost is now λ_i = ε Π_i/R_i (wording) | all `results/oecd26` rows |
| `Appendix/OECD26.tex:11` | "we calibrate ω to the U.S. tax rate and λ ..., which gives ω = 1.294 and λ = 11.109, against 11.345 at the CPS groups" | ω 1.294 holds (1.294280); λ 11.109 → ε 20.014 (λEff2020 = ε·Π/R 11.108), against ε 20.445 at the CPS groups | `anchor.csv` (cps, sizePiR); `escCalibrationCosts.csv` (sizePiR) |
| `Appendix/OECD26.tex:26` | "each country keeps the U.S. β and λ" | λ → ε | — |
| `Appendix/OECD26.tex:26` | "The weight of the old runs from 0.947 in Hungary to 1.761 in Luxembourg, against 1.294 in the U.S." | 0.947 (HUN) – 1.761 (LUX) → 0.947 (HUN) – 1.758 (LUX); U.S. 1.294 | `layer2.csv` (cps, sizePiR, common) ω |
| `Appendix/OECD26.tex:26` | "The predicted designs run from 0.570 in Ireland to 0.937 in Finland" | → 0.618 (IRL) – 0.924 (FIN) | idem θInForce |
| `Appendix/OECD26.tex:26` | "For 17 of the 25 countries the predicted design lies on the same side of the U.S. design as the observed one" | 17 → 17: holds (exceptions unchanged: BEL, CAN, CZE, DNK, GBR, JPN, NZL, NOR) | idem |
| `Appendix/OECD26.tex:26` | "The UK ... is predicted at 0.805, above the U.S." | 0.805 → 0.791 (still above 0.735) | idem (GBR) |
| `Appendix/OECD26.tex:26` | "with ... the CSES ... the UK is predicted at 0.723, below the U.S." | 0.723 → 0.706 (still below) | `layer2.csv` (cses, sizePiR, common, GBR) |
| `Appendix/OECD26.tex:26` | "France is predicted at 0.903, short of its corner" | 0.903 → 0.879 | `layer2.csv` (cps, sizePiR, common, FRA) |
| `Appendix/EndogenousDesignResults.tex:11` | "takes λ = 11.345 from the U.S. The UK's electorate then chooses 0.690 ..., and France's chooses 0.795" (if G.1/7.3 report the deep test under ε) | λ 11.345 → ε 20.445; UK 0.690 → 0.673; France 0.795 → 0.743 | `escCountryCosts.csv` (UK, FR; US) |
| `Appendix/EndogenousDesignResults.tex:11` | "so the three designs are ordered as observed, with the U.S. at 0.728 between them" | holds under ε: 0.673 < 0.728 < 0.743 | idem |
| `Appendix/EndogenousDesignResults.tex:11` | "the parameter accounts for about a quarter of the distance from the U.S. design to each of the other two" | 0.23 / 0.25 → 0.33 / 0.06. **Flips for France** | idem |
| `Appendix/EndogenousDesignResults.tex:11` | "Under one parameter, each unit of redistribution therefore costs France nearly twice as much as the UK" | under λ: τ ratio 0.206/0.112 = 1.84; under ε the cost per unit scales with τ·Π/R: (0.206 × 0.432)/(0.112 × 0.529) = 1.50 ("half as much again") | `escCountryCosts.csv` (UK, FR; US) τ, ΠR |
| `Appendix/EndogenousDesignResults.tex:6` | "The UK's parameter lies below the U.S. one ... by 32% at ρ = 1" (the UK's own calibration, table `UK_ESC_Calibration`, under λ) | under ε at ρ = 1: 28% below; ρ = 0.5 and 2 not computed under ε | `escCountryCosts.csv` (UK, own) |

Not in the paper today, for the writers: section 6's spending test (`OECD26_Spending`, no cost) gives spending on
population growth −14.90 (0.73) against the data's −12.84 (3.67), and on the Gini −15.65 (16.47) against 17.80 (23.90),
neither significant on the Gini; `results/oecd26/layer1.csv` (cps, none, common).
