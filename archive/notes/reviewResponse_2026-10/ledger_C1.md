# Ledger C1: the U.S. block, the UK, France and section 7 at the pension-only calibration

Package C1 of `notes/plan_reviewResponse.md` (A2, A8), 2026-10-23. Every number the prose of
`Sections/{OECD,EndogenousTheta,Introduction,Conclusion}.tex`, `abstract.tex` and
`Appendix/{CalibrationOECD,EndogenousDesign,EndogenousDesignResults}.tex` cites from these blocks, at HEAD (old)
and after the reruns (new), with file:line, and whether the claim changes (sign, ranking, ordering). Generated
tables are not copied here: `python/paper/compareResults.py` compares them. Common X, the headline variant.
Changes are against the baseline of the same ρ (and, in section 7, of the same reading). Runs: `logs/C1/`.

## Section 6 and appendix F (design given)

| file:line | quantity | old | new | claim |
|---|---|---|---|---|
| OECD.tex:8, CalibrationOECD.tex:8 | Medicare in U.S. spending and in θ | yes | no (pensions only; Medicare is the OA reading) | **changes** (A2's rewrite) |
| OECD.tex:10 | ν2020 U.S. / France | 1.34 / 0.97 | 1.34 / 0.97 | holds |
| OECD.tex:10 | η_H/η_L U.S. / France | 3.08 / 2.29 | 3.08 / 2.29 | holds |
| OECD.tex:10 | mean X: U.S., UK, France ("roughly twice the U.S. in the UK and France") | 4.03, 8.26, 7.27 (×2.05, ×1.80) | 4.16, 7.93, 6.90 (×1.91, ×1.66) | weaker for France |
| OECD.tex:10 | ω U.S., France, UK ("nearly the same in the U.S. and France, lower in the UK") | 1.45, 1.42, 1.16 | 1.23, 1.35, 1.10 | **changes**: France 9% above the U.S. |
| CalibrationOECD.tex:10 | U.S. η low–high | 0.82–2.52 | 0.82–2.54 | holds |
| CalibrationOECD.tex:22 | France η low–high; X France vs U.S. | 1.12–2.56; 7.27 vs 4.03 | 1.10–2.53; 6.90 vs 4.16 | holds |
| CalibrationOECD.tex:30, :36 | UK 29% vs 58%, 3.06 vs 3.08, voting 0.61–0.74; France at UK cuts 3.3 | same | same (data) | holds |
| OECD.tex:29 | θ: 1 → 0, Δτ at ρ = 1 | +6.2 p.p. | +6.6 p.p. (8.25% → 14.86%) | holds |
| OECD.tex:29 | θ: 1 → 0, Δ s/Y at ρ = 1 | −1.6 p.p. | −1.9 p.p. | holds |
| OECD.tex:29 | θ↑ lowers savings with τ fixed (ee), raises them in full | ee +0.55 / full −1.57 (θ1→θ0) | ee +0.42 / full −1.87 | holds |
| OECD.tex:29 | hours: tax response ≥ direct effect (θ = 0, ρ = 1) | full −1.87 h, ee −0.86 h | full −1.73 h, ee −0.66 h | holds |
| OECD.tex:31 | acute / mild ageing Δτ, ρ = 1 | +8.7 / +4.0 p.p. | +8.7 / +4.0 p.p. (8.65 / 3.99) | holds |
| OECD.tex:31 | acute ageing Δ s/Y, ρ = 1; hours | −2.1 p.p.; −0.7 h | −2.0 p.p. (−2.05); −0.7 h (−0.69) | holds |
| OECD.tex:35 | France's income distribution / voting, Δτ at ρ = 1 | −1.2 / +0.9 p.p. | −1.3 / +0.9 p.p. (−1.29 / +0.93) | holds |
| OECD.tex:35 | leisure row shortens the workweek by more than the gap to France (4.15 h) | −5.02 h | −4.35 h | holds (narrowly) |
| OECD.tex:35 | France's income distribution raises the UK's tax (UK host, ρ = 1) | +0.29 p.p. | +0.29 p.p. | holds |
| OECD.tex:37, EndogenousTheta.tex:7 | hours at the Beveridgean corner, ρ = 1 ("about two hours") | −1.87 h | −1.73 h | holds ("about 1.7") |
| OECD.tex:37 | ageing moves hours less than France's income distribution, every ρ | 0.71/0.73/0.68 vs 1.14/0.96/0.82 | 0.70/0.69/0.70 vs 1.17/0.98/0.84 | holds |
| OECD.tex:40 | θ: 1 → 0, Δτ at ρ = 0.5 / 2 | +9.0 / +1.5 p.p. | +9.3 / +2.1 p.p. | holds |
| OECD.tex:40 | effects larger at low ρ, French voting the exception | voting 0.33/0.89/1.69 | voting 0.34/0.93/1.87 | holds |
| abstract:6, Conclusion:5 (A9) | ranking at ρ = 2: voting vs design effect | voting 1.69 > design 1.48 | design 2.12 > voting 1.87 | **changes**: the earnings link is second at every ρ |
| OECD.tex:48 | ageing vs income distribution ("several times less") | 8.68 vs 1.22 | 8.65 vs 1.29 | holds |
| Conclusion:5 | "a higher IES changes only the size of the earnings-link effect" | design 9.0/6.2/1.5 | design 9.3/6.6/2.1; voting rises 0.34→1.87 | as before (A9 fixes the wording) |

## Section 7 and appendices C, G (design chosen)

| file:line | quantity | old | new | claim |
|---|---|---|---|---|
| EndogenousTheta.tex:29, EndogenousDesign.tex:97 | θ* | 0.738 | 0.728 | number |
| EndogenousTheta.tex:35 | λ at ρ = 0.5 / 1 / 2 (falls in ρ, "roughly an order of magnitude") | 18.27 / 8.64 / 1.72 (×10.6) | 23.69 / 11.56 / 2.46 (×9.6) | holds |
| EndogenousTheta.tex:35 | 1 − f(θ*) "no more than 4%"; 1 − f(0) | 3.9 / 1.8 / 0.4%; 43.7 / 23.8 / 5.3% | 3.9 / 1.9 / 0.4%; 41.9 / 23.3 / 5.5% | holds (3.94% at ρ = 0.5) |
| EndogenousTheta.tex:35 | λ above the elasticity range "by more than an order of magnitude at ρ ≤ 1" (λ ≈ εΠ, 0.13–0.54) | 8.64/0.54 = 16× | 11.56/0.54 = 21× | holds (C5 redoes with Π/R) |
| EndogenousTheta.tex:35, Introduction:27 | the U.S. λ "accounts for much of the UK's distance" | UK 0.625 vs 0.560 obs., U.S. 0.738: 63% | UK 0.698 vs 0.560 obs., U.S. 0.728: 18% | **changes** |
| EndogenousTheta.tex:35 | "none of France's" | France 0.749 (U.S. +0.011) | France 0.799 (U.S. +0.072), 26% of the distance | **changes** |
| EndogenousTheta.tex:41 | pinned acute ageing Δτ at ρ = 1 vs design-given 8.7 | 8.1 p.p. | 7.8 p.p. | holds |
| EndogenousTheta.tex:55 | chosen acute crowds out savings more than pinned (s/Y, p.p.), "in particular for low ρ" | 0.5: −2.28 vs −1.97; 1: −2.04 vs −1.94; 2: −1.81 vs −1.77 | 0.5: −2.18 vs −1.84; 1: −2.01 vs −1.85; 2: −1.81 vs −1.77 | holds |
| EndogenousTheta.tex:55, :62, abstract:6, Conclusion:7 | ageing raises θ at every ρ (acute, chosen) | +0.078 / +0.087 / +0.088 | +0.098 / +0.117 / +0.104 | holds |
| EndogenousTheta.tex:55 | French voting lowers θ (chosen) | −0.051 / −0.085 / −0.403 | −0.044 / −0.074 / −0.339 | holds |
| EndogenousTheta.tex:57 | cost on the design (`scale`): acute raises θ "only to 0.778"; size channel "about half" | 0.778; (0.087−0.040)/0.087 = 54% | 0.771; (0.117−0.043)/0.117 = 63% | "about two thirds" |
| EndogenousTheta.tex:59 | Ṽ U.S. / France | 0.436 / 0.218 | 0.436 / 0.218 | holds |
| EndogenousTheta.tex:55, :59 | income distribution moves θ (chosen): down at ρ = 0.5, up slightly at 1, up much at 2 | −0.031 / +0.033 / +0.180 | −0.047 / +0.024 / +0.184 | holds |
| EndogenousDesignResults.tex:6 | UK λ vs U.S.: −17% (0.5), −16% (1), +61% (2) | 15.12, 7.26, 2.78 | 16.15 (−32%), 7.79 (−33%), 2.99 (+21%) | **changes** (a third below at ρ ≤ 1, a fifth above at 2) |
| EndogenousDesignResults.tex:6 | UK 1 − f(θ*) "as the U.S."; 1 − f(0) UK vs U.S. (ρ = 1) | 1.8% / 1.8%; 9.2% vs 23.8% | 1.9% / 1.9%; 9.3% vs 23.3% | holds |
| EndogenousDesignResults.tex:6 | "the UK's system is smaller, 11.9% against 14.4%" | 11.9% < 14.4% | 11.2% > 10.5% | **flips** (A2) |
| EndogenousDesignResults.tex:6 | UK ω without / with the cost (ρ = 1) | 1.16 → 1.21 | 1.10 → 1.15 | holds |
| EndogenousDesignResults.tex:11, Conclusion:7 | λ = 8.643 imposed: UK chooses / France chooses; order UK < U.S. < FR | 0.625 / 0.749; holds | 0.698 / 0.799; holds | order holds |
| EndogenousDesignResults.tex:11 | France 21.3% vs UK 11.9% ("almost twice") | ×1.80 | 20.6% vs 11.2%, ×1.84 | holds |
| EndogenousDesignResults.tex:11 | regrouped UK: θ 0.543, Ṽ 0.065, chooses 0.644, own λ 6.519 | as listed | 0.543, 0.065, 0.702, 7.047 | numbers |
| Conclusion:7 | UK's own λ "within 17% of the U.S. at IES ≤ 1, though not at two" | 16–17%; +61% | 32–33%; +21% | **changes** |
| EndogenousDesignResults.tex:15 | path θ 2020 → 2050 → 2110 on | 0.738 → 0.797 → 0.809 | 0.728 → 0.802 → 0.824 | holds |
| EndogenousDesignResults.tex:15 | τ 2020 → 2110; above the pinned path | 14.4% → 20.9%; +0.2 p.p. | 10.5% → 16.9%; +0.3 p.p. | holds |
| EndogenousDesignResults.tex:15 (fn) | ξ = 0.2/0.4: λ ±1%, τ 2110 ±0.3 p.p., θ 2110 and acute θ "same to the third decimal" | as stated | λ 11.634/11.492 (±0.6%); τ ±0.3 p.p.; θ 2110 0.825/0.824/0.824, acute 0.846/0.845/0.842 | third-decimal claim **weakens** (within 0.004) |
| EndogenousDesign.tex:43 | costless sequential FOC negative at every date, ρ = 0.5, 1, 2 | yes | yes (escSequentialCRRA, test_esc at ρ = 1) | holds |
| EndogenousDesign.tex:72 | λ multiples of 0.13–0.54 (λ ≈ εΠ): >10× at ρ ≤ 1, 3–13× at ρ = 2 | 16–64× (ρ = 1); 3–13× | 21–86× (ρ = 1); 5–18× (ρ = 2) | numbers (C5 redoes with Π/R) |

## The θ = 1 tax (T3's closed form)

`notes/theory_closedForm.md` (1.4) at the recalibrated (β, ω) = (0.655483, 1.230860) and each ν_t equals the code's
log tax on the θ ≡ 1 path to 6.3e-13 at every date (terminal date with β → 0). The 2020 value is **8.25%** (12.3% at
HEAD), against 10.52% at θ* and 14.86% at θ = 0. Π_2020/R_2020 = 1.3547/2.4430 = 0.5545 (0.5547 at HEAD).

## A8: the ageing response under three costs (θ chosen, changes at 2020 against the baseline of the same reading)

| ρ | cost | λ or p | mild Δθ | acute Δθ | 2050 / 2110 θ on the baseline path |
|---|---|---|---|---|---|
| 0.5 | paper's (`size`) | 23.691 | +0.033 | +0.098 | 0.784 / 0.816 |
| 0.5 | Π-inclusive (`sizePiR`) | 42.444 | +0.027 | +0.062 | 0.764 / 0.767 |
| 0.5 | on the design (`scale`) | 0.9439 | +0.011 | +0.019 | 0.730 / 0.743 |
| 1 | paper's (`size`) | 11.564 | +0.070 | +0.117 | 0.802 / 0.824 |
| 1 | Π-inclusive (`sizePiR`) | 20.839 | +0.048 | +0.074 | 0.797 / 0.798 |
| 1 | on the design (`scale`) | 0.4146 | +0.020 | +0.043 | 0.737 / 0.753 |
| 2 | paper's (`size`) | 2.4593 | +0.033 | +0.104 | 0.785 / 0.823 |
| 2 | Π-inclusive (`sizePiR`) | 4.4598 | +0.026 | +0.086 | 0.756 / 0.761 |
| 2 | on the design (`scale`) | 0.0916 | +0.021 | +0.066 | 0.744 / 0.758 |

Every cost keeps the sign: ageing raises θ at every ρ, mild and acute, and the order is the paper's > Π-inclusive
> on the design at every ρ. The Π-inclusive cost keeps 64% (ρ = 0.5), 63% (1) and 82% (2) of the paper's acute
response, and 36–73% of its long-run drift (2020 → 2110: +0.039 / +0.070 / +0.034 against +0.088 / +0.096 /
+0.095); π_2020 = Π/R = 0.558 / 0.555 / 0.553, and λ_ΠR·π_2020 is within 0.2% of the paper's λ at every ρ. `results/esc/escAgeingCosts.csv` (rows: spec, ρ, scenario, θpinned; columns dθ_t0, dτ_t0, ...). The section
7 footnote's claim ("a cost that kept the factor would grow less") holds; the "about half" of the size channel
(EndogenousTheta.tex:57) is now 63% at ρ = 1 (`scale` 0.771 against `size` 0.845).

## The Medicare reading (online appendix)

m = 2.9/(7.366 + 2.9) = 0.2825; τ0 = 0.146657; θ* = (1 − m)·0.7278 = 0.5222 (A2's 0.519 was on the 7.2 base). At
ρ = 1: θ 1 → 0 +6.3 p.p., acute +8.6, mild +4.0, France's income −2.0, voting +1.5
(`results/shocks/USMedicare_shocksCommonX.csv`).

## Online appendix and checks

- `ESC_Timing`: the costless permanent choice under CRRA is θ = 1 at every ρ ≥ 1.1 (HEAD: θ = 0 up to ρ = 1.3,
  θ = 1 from 1.4); under log it stays θ = 0. The costless sequential FOC is negative at every date (ρ = 0.5, 2).
- The permanent timing's own calibrated `scale` p is 0.383 (0.375); the comparison cost's exact p is 0.944 / 0.0916
  at ρ = 0.5 / 2 (0.935 / 0.0855).
- Counts: one equilibrium and no fallback at every counted state of every C1 csv, except one state of the design
  layer (`escShocksCRRA.csv`, ρ = 2, `size`, all French characteristics, chosen: `nFallbackθ` 1).
