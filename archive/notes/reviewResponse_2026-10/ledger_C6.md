# Ledger C6: the U.S. results under the converged solvers (A6)

Package C6 (reruns) of `notes/plan_reviewResponse.md` (W16), 2026-10-25, on C6's code (`notes/brief_C6.md`: the CRRA
τ-derivatives a least-squares cubic in ln(1−τ); `LeadedLOG` solves the anticipated tax at every candidate;
`LeadedCRRA2D` Catmull-Rom along θ at 13 nodes). **Old** is f3a15a4 (the C1–C5 results), **new** this run;
**paper** is the number `writing/Paper` prints at HEAD, whose text still carries the 2026-10-03 run where C1 flagged it.
Common X; changes against the baseline of the same ρ and reading. Runs: `logs/C6runs/` (`jobs.tsv` from
`gen_jobs.py`, `scheduler.log`: 80 jobs, none failed); every number below is in `logs/C6runs/ledger_numbers.txt`
(`ledger_numbers.py`); generated tables against HEAD in `logs/C6runs/compareResults.log` (67 csvs moved, no row
added or lost).

**Self-checks.** Before the runs, `runShocksUS.py --rho 1 --commonX` on the new code reproduces all 18 ρ = 1 rows of
`US_shocksCommonX.csv` exactly (τ_2020 0.1052285714, θ = 1 tax 0.0825098791; difference 0.0). After: the sweep's ρ = 1
row bitwise, the LOG λ = 11.344862735771882 equal to C6's measured value, `US_shocksXiCommonX.csv` byte-identical,
`c5Numbers.py selfcheck` OK, `runESCxi.py` self-check passed, `runHorizon.py` self-checks 2.4e-13 (log), 1.7e-14 /
1.0e-11 (design, ρ = 0.5 / 2). Under the new LOG solver θ_2020 at C1's λ = 11.564 is 0.7324; the calibration absorbs it.

## 1. Headline, old → new

| quantity | ρ = 0.5 | ρ = 1 | ρ = 2 |
|---|---|---|---|
| θ*, and θ_2020 on each calibrated path | 0.7278 → 0.7278 | 0.7278 → 0.7278 | 0.7278 → 0.7278 |
| λ, paper's cost (`size`) | 23.691 → **25.082** | 11.564 → **11.345** | 2.459 → **2.643** |
| λ, Π-inclusive (`sizePiR`) | 42.444 → 44.988 | 20.839 → 20.445 | 4.460 → 4.785 |
| p, cost on the design (`scale`) | 0.9439 → 0.9563 | 0.4146 → 0.4119 | 0.0916 → 0.0942 |
| UK's own λ (`size`) | 16.145 → 16.694 | 7.786 → 7.740 | 2.985 → 3.103 |
| 1 − f(θ*) / 1 − f(0), U.S. | 3.94 / 41.9% → **4.17** / 43.7% | 1.95 / 23.3% → 1.91 / 22.9% | 0.42 / 5.5% → 0.45 / 5.9% |
| θ 1 → 0, Δτ_2020 (p.p.) | 9.34 → **9.13** | 6.61 → 6.61 | 2.12 → **1.99** |
| acute ageing / voting, Δτ (design given) | 9.38 / 0.34 → 9.28 / 0.34 | 8.65 / 0.93 (same) | 7.87 / 1.87 → 7.68 / 1.76 |
| chosen path θ_2050 / θ_2110 | 0.784 / 0.816 → 0.799 / 0.817 | 0.802 / 0.824 → 0.802 / 0.820 | 0.785 / 0.823 → 0.802 / 0.826 |
| acute ageing Δθ_2020 (chosen) | +0.098 → +0.104 | +0.117 → +0.109 | +0.104 → +0.116 |
| French income distribution Δθ | −0.047 → **−0.019** | +0.024 → +0.021 | +0.184 → +0.182 |
| French voting Δθ | −0.044 → −0.018 | −0.074 → −0.073 | −0.339 → −0.323 |
| UK / France under the U.S. λ (ρ = 1) | | 0.698 / 0.799 → 0.690 / 0.795 | |

No sign changes and no rank changes in any of these. Two thresholds the text relies on are crossed (§3).

## 2. Section 6 and appendix F (design given)

Every ρ = 1 number is unchanged to the last digit (LOG), so C1's rows for `OECD.tex:10–35` and `:48` stand.

| file:line | quantity | paper | old | new | claim |
|---|---|---|---|---|---|
| OECD.tex:37 | ageing moves hours less than France's income distribution, every ρ | – | 0.70/0.69/0.70 vs 1.17/0.98/0.84 | 0.66/0.69/0.66 vs 1.15/0.98/0.83 | holds |
| OECD.tex:40 | θ 1 → 0, Δτ at ρ = 0.5 / 2 | +9.0 / +1.5 | +9.34 / +2.12 | **+9.13 / +1.99** | number |
| OECD.tex:40 | effects larger at low ρ, French voting the exception | – | voting 0.34/0.93/1.87 | voting 0.34/0.93/1.76; acute 9.28/8.65/7.68; income −1.58/−1.29/−0.82 | holds |
| abstract:6, Conclusion:5, Introduction:23 | ageing first, earnings link second (U.S.) | – | ρ = 2: design 2.12 > voting 1.87 | 1.99 > 1.76 (gap 0.23); ρ = 0.5: acute 9.28 > design 9.13 (gap 0.15, was 0.04) | holds at every ρ of the grid; no rank changes (`C5_ranking.csv`) |
| abstract:6, Conclusion:5 (C5 A9) | UK hosts | – | UK: link first at ρ = 0.5; UKUS: link third at ρ ≥ 1 | UK 6.18 vs 4.98 at ρ = 0.5; UKUS 1.46/0.44 vs income 1.83/1.53 | as C5 (changes for the UK hosts) |
| Conclusion:5 | a higher IES changes only the size of the earnings-link effect | – | voting 0.34 → 1.87 | voting 0.34 → 1.76 | as C1 |

## 3. Section 7 and appendices C, G (design chosen)

| file:line | quantity | paper | old | new | claim |
|---|---|---|---|---|---|
| EndogenousTheta.tex:35 | λ falls in ρ, "roughly an order of magnitude" | 18.27/8.64/1.72 | 23.69/11.56/2.46 (×9.6) | 25.08/11.34/2.64 (×9.5) | holds |
| EndogenousTheta.tex:35 | 1 − f(θ*) "no more than 4%" | 3.9/1.8/0.4% | 3.94/1.95/0.42% | **4.17**/1.91/0.45% | **crosses the threshold at ρ = 0.5** (US_ESC_Calibration now prints 4.2%) |
| EndogenousTheta.tex:35 | λ above the elasticities "by more than an order of magnitude at ρ ≤ 1" | 16× | 44–174× / 21–85× (λ ≈ εΠ) | 46–185× / 21–84× | holds |
| EndogenousTheta.tex:35, Introduction:27, Conclusion:7 | the U.S. λ accounts for "much of the UK's distance" | 63% | 18% | 23% (UK 0.690, observed 0.560, U.S. 0.728) | as C1 (changes) |
| EndogenousTheta.tex:35 | "none of France's" | +0.011 | +0.072 (26%) | +0.068 (25%) | as C1 (changes) |
| EndogenousTheta.tex:41 | pinned acute ageing Δτ at ρ = 1 (vs 8.7 design given) | 8.1 | 7.81 | 7.83 | holds |
| EndogenousTheta.tex:55 | chosen acute crowds out savings more than pinned, "in particular for low ρ" (s/Y, p.p.) | – | −2.18 vs −1.84; −2.01 vs −1.85; −1.81 vs −1.77 | −2.15 vs −1.79; −2.00 vs −1.86; −1.80 vs −1.76 | holds |
| EndogenousTheta.tex:55, :62, abstract:6, Conclusion:7, Introduction:27 | ageing raises θ at every ρ (acute, chosen) | +0.078/+0.087/+0.088 | +0.098/+0.117/+0.104 | +0.104/+0.109/+0.116 | holds |
| EndogenousTheta.tex:55, Conclusion:7 | French voting lowers θ | −0.051/−0.085/−0.403 | −0.044/−0.074/−0.339 | −0.018/−0.073/−0.323 | holds (ρ = 0.5 response 60% smaller) |
| EndogenousTheta.tex:55, :59, abstract:6, Conclusion:7, Introduction:27 | income distribution: down slightly at ρ = 0.5, up slightly at 1, up much at 2 | −0.031/+0.033/+0.180 | −0.047/+0.024/+0.184 | **−0.019**/+0.021/+0.182 | holds (ρ = 0.5 sign kept, size 40% of old) |
| EndogenousTheta.tex:57 | cost on the design: acute raises θ "only to 0.778"; size channel "about half" | 0.778; 54% | 0.771; 63% | 0.762; 68% | number; "about two thirds" |
| EndogenousTheta.tex:57 fn | a cost that kept Π/R would grow less | – | 64/63/82% of the acute response | 71/68/70% | holds |
| EndogenousTheta.tex:59 | Ṽ 0.436 → 0.218 | 0.436/0.218 | same | same | holds |
| EndogenousDesignResults.tex:6 | UK λ against the U.S.: −17% / −16% / +61% | −17/−16/+61% | −32/−33/+21% | −33/−32/+17% | as C1 (changes) |
| Conclusion:7 | UK's own λ "within 17% of the U.S. at IES of one or below, though not at two" | – | 32–33%; 21% | 32–33%; **17.4%** | **inverts**: now about 17% at ρ = 2 and a third off at ρ ≤ 1 |
| EndogenousDesignResults.tex:6 | UK 1 − f(θ*) "as the U.S."; 1 − f(0) UK vs U.S. (ρ = 1) | 1.8 / 1.8%; 9.2 vs 23.8% | 1.87 / 1.95%; 9.3 vs 23.3% | 1.86 / 1.91%; 9.2 vs 22.9% | holds |
| EndogenousDesignResults.tex:6 | UK ω without / with the cost (ρ = 1) | 1.16 → 1.21 | 1.10 → 1.15 | 1.10 → 1.15 | as C1 |
| EndogenousDesignResults.tex:11, Conclusion:7 | U.S. λ imposed: UK / France choose; order UK < U.S. < France | 0.625 / 0.749 | 0.698 / 0.799 | 0.690 / 0.795 | order holds |
| EndogenousDesignResults.tex:11 | λ imposed; regrouped UK chooses, own λ | 8.643; 0.644, 6.519 | 11.564; 0.702, 7.047 | 11.345; 0.699, 7.121 | numbers |
| EndogenousDesignResults.tex:15 | path θ 2020 → 2050 → 2110 (ρ = 1) | 0.738 → 0.797 → 0.809 | 0.728 → 0.802 → 0.824 | 0.728 → 0.802 → 0.820 | holds |
| EndogenousDesignResults.tex:15 | τ 2020 → 2110; above the pinned path | 14.4 → 20.9%; +0.2 | 10.5 → 16.9%; +0.32 | 10.5 → 16.9%; +0.29 | holds |
| EndogenousDesignResults.tex:15 fn | ξ = 0.2 / 0.4: λ ±1%, τ_2110 ±0.3 p.p., θ_2110 and acute θ "same to the third decimal" | – | λ ±0.6%; θ_2110 0.825/0.824/0.824; acute 0.846/0.845/0.842 | λ 11.413/11.276 (±0.6%); τ_2110 17.14/16.85/16.58; θ_2110 0.821/0.820/0.819; acute 0.838/0.837/0.836 | third-decimal claim still fails (spread 0.002, was 0.004) |
| EndogenousDesign.tex:43 | costless sequential FOC negative at every date, ρ = 0.5, 1, 2 | – | yes | yes (max −0.75 / −0.0015 at ρ = 0.5 / 2) | holds |
| EndogenousDesign.tex:72 | λ ≈ εΠ: >10× at ρ ≤ 1; "three to thirteen times" at ρ = 2 | 3–13× | 5–18× | 4.9–20× (with Π/R: 12–48×) | number (as C5) |
| ESC_Timing (OA) | costless permanent choice θ = 1 at every ρ ≥ 1.1 | – | yes | yes | holds |

## 4. Ageing under the three costs (C1's A8 table)

| ρ | cost | λ or p | mild Δθ | acute Δθ | 2050 / 2110 θ, baseline path |
|---|---|---|---|---|---|
| 0.5 | paper's | 23.691 → 25.082 | +0.033 → +0.061 | +0.098 → +0.104 | 0.784 / 0.816 → 0.799 / 0.817 |
| 0.5 | Π-inclusive | 42.444 → 44.988 | +0.027 → +0.045 | +0.062 → +0.074 | 0.764 / 0.767 → 0.791 / 0.792 |
| 0.5 | on the design | 0.9439 → 0.9563 | +0.011 → +0.007 | +0.019 → +0.022 | 0.730 / 0.743 → 0.728 / 0.744 |
| 1 | paper's | 11.564 → 11.345 | +0.070 → +0.064 | +0.117 → +0.109 | 0.802 / 0.824 → 0.802 / 0.820 |
| 1 | Π-inclusive | 20.839 → 20.445 | +0.048 → +0.045 | +0.074 → +0.074 | 0.797 / 0.798 → 0.788 / 0.791 |
| 1 | on the design | 0.4146 → 0.4119 | +0.020 → +0.013 | +0.043 → +0.035 | 0.737 / 0.753 → 0.734 / 0.753 |
| 2 | paper's | 2.459 → 2.643 | +0.033 → +0.067 | +0.104 → +0.116 | 0.785 / 0.823 → 0.802 / 0.826 |
| 2 | Π-inclusive | 4.460 → 4.785 | +0.026 → +0.047 | +0.086 → +0.082 | 0.756 / 0.761 → 0.782 / 0.796 |
| 2 | on the design | 0.0916 → 0.0942 | +0.021 → +0.032 | +0.066 → +0.077 | 0.744 / 0.758 → 0.746 / 0.786 |

Every cost keeps the sign, and the order paper's > Π-inclusive > on the design holds at every ρ, mild and acute. The
Π-inclusive cost keeps 71 / 68 / 70% of the paper's acute response (was 64 / 63 / 82%); π_2020 = 0.557 / 0.555 / 0.553
and λ_ΠR·π_2020 is within 0.1% of λ. The CRRA mild responses roughly double (13-node linear θ grid, finding #19).
`results/esc/escAgeingCosts.csv`.

## 5. Section 4 and appendix D (C4's tables)

- `Numerical.tex:3` fn, "misplaces the design by up to 0.059": the largest gap in `NUM_Stationary` is 0.074 (0.074 at
  f3a15a4; ρ = 1, 2 in 2050). The tax gap, "roughly 0.2 p.p.", is ≤ 0.24 p.p. Number stale since C1.
- `Numerical.tex:7` fn, exactly one candidate passes at every state of every counted solve: C4's one design-layer
  fallback (`escShocksCRRA`, ρ = 2, all French characteristics) is gone. `NUM_Selection` reports no fallback, so the
  footnote holds as written and T2's planned "except one state" clause is no longer needed.
- `Numerical.tex:3`, "for a large T the two agree away from T"; `NUM_Horizon`. Design given, Δτ_2020 at T = 2140 / 2290 /
  steady state: ρ = 0.5 +0.003 / **+0.011 / +0.027 p.p.** (C4: ≤ 0.0006), ρ = 2 −0.005 / −0.001 / 0.000. τ_2050 within
  0.028. Design chosen: θ_2020 within 1.4e-4 (steady state, ρ = 0.5; C4 6e-5), τ_2020 within 0.005 p.p. The ρ = 0.5
  steady state's policy is stationary to 2.3e-7 (C4: 1e-15). The sentence holds to 0.03 p.p.; C4's "≤ 0.0006 p.p." and
  "≤ 0.005 p.p. against the steady state" no longer hold for the U.S. at ρ = 0.5.
- `NUM_Residuals` (p.p., ns = 150, ρ = 0.5 / 2). As solved on the path: 5.3e-4 / 8.8e-4 (was 3.2e-4 / 1.9e-4).
  Visited cells: 0.0024 / 0.0023. Against converged derivatives: **0.0028 / 0.0013** (was 0.17 / 0.37). At ns = 50:
  0.050 / 0.0065, against 0.056 / 0.069 before. The note generated by `tablesHorizon.py` still says the U.S. solver
  "differentiates along the tax with a smoothing spline". That is stale after C6; the builder text was not changed here.
- `US_jumps.csv`: ns = 50 now shows no isolated jumps. The largest second difference of τ_2020 over ω is 1.8e-6 / 2.1e-7,
  against 2.0e-4 / 2.3e-4; C1's ns = 50 jump is gone.
- `US_derivativeScheme.csv` (101 vs 801 tax nodes): τ_2020 10.523 vs 10.522% (ρ = 0.5) and 10.523 vs 10.517% (ρ = 2). The
  θ 1 → 0 gap is 9.127 vs 9.115 and 1.988 vs 1.990 p.p.

## 6. C5's numbers

- **A1** (`EndogenousDesign.tex:41, :43`, `Introduction:25`): critical μ_H/μ_L 11.47 / 3.39 / 1.84 (was 11.47 / 3.39 / 1.84),
  lowest over dates 9.06 / 3.05 / 1.76; negative everywhere at observed turnout. Holds.
- **A9**: no rank flips on any host at any ρ (U.S. grid 0.5–2.0, UK, UKUS); see §2.
- **#7**: 1 − f(θ* − 0.1), tax held: 7.66 / 3.54 / 0.84% (7.25 / 3.61 / 0.78).
- **#22**: multiples of ε = 0.1–0.4 under λ ≈ εΠ/R: 113–451 / 51–205 / 12–48 (106–426 / 52–209 / 11–45). "More than an
  order of magnitude" holds at every ρ.
- **#13** (index units, I = 1/(2 − θ)): acute ΔI +0.070 / +0.074 / +0.079 (+0.065 / +0.080 / +0.070); path 2020 → 2110 ΔI
  +0.059 / +0.062 / +0.066. The UK under the U.S. λ covers 25% of its distance in index units (23% in θ; was 19% / 18%).
- **#5**, the design's response to France's income distribution, sequential split:

| ρ | response | gains side (X2 − U.S.) | cost's dispersion (X1 − X2) | τ channel (France − X1) | without the τ channel (X1 − U.S.) |
|---|---|---|---|---|---|
| 0.5 | −0.047 → −0.019 | +0.111 → +0.128 | −0.119 → −0.130 | −0.039 → −0.017 | −0.008 → −0.002 |
| 1 | +0.024 → +0.021 | +0.149 → +0.149 | −0.104 → −0.113 | −0.021 → −0.015 | +0.045 → +0.036 |
| 2 | +0.184 → +0.182 | +0.207 → +0.216 | −0.020 → −0.031 | −0.002 → −0.003 | +0.186 → +0.185 |

  `EndogenousTheta.tex:59`'s two forces still order as stated (dispersion −0.130 / −0.113 / −0.031, gains +0.128 /
  +0.149 / +0.216). At ρ = 0.5 the dispersion force outweighs the gains by 0.002 only, and the τ channel now carries
  89% of the response. Under log the solver's θ_2020 equals the per-candidate maximiser and is identical at nθ =
  41–321 (C5's grid error closed). The FOC routes at the U.S. choice (×10³): design −27.92, cost +19.69, tax +8.23.
  France's total is +4.58 (+4.67).
- **A13**: τ_2020 at 0.5 / 1.5 s*: 11.41 / 9.98% at ρ = 0.5 (elasticity −0.129) and 10.17 / 10.72% at ρ = 2 (+0.047).

## 7. The 26-country test (`OECD26_*`, no sentence in the paper cites them)

The anchor's λ is 11.218 → 11.109 (cps) and 13.575 → 13.444 (cses); ω 1.2946 → 1.2943. In `OECD26_Slopes`, layer 1: spending on
growth −16.50 → −16.49, on the Gini −10.20 → −10.25, on the index 65.97 → 65.35; index on growth −0.13 → −0.13, on the
Gini −0.41 → −0.41. Layer 2: spending on the index 78.07 → 76.45, index on growth −0.09 → −0.09, on the Gini −0.16 → −0.14.
No sign changes. **Failed row**: layer 2 under CSES turnout, Turkey: `ValueError: The function value at x=1e-06 is NaN`.
The tax reaches 1 at the ω root's lower bracket (`base.py:564`, `:573` divide by zero). It is deterministic: a retry in a
scratch copy fails the same way (`logs/C6runs/oecd26_TURretry.log`). It was ok at f3a15a4. The registered outputs read the
CPS reading and build; `test_oecd26.py`'s P check fails on this row, and so would the CSES layer-2 variants.
