# Stale model numbers in the prose after the switch to θ variant C (audit of 2026-11-02)

A read-only audit of the prose against the variant-C sources: the generated tables and notes in `writing/Paper`,
the marks in `results/paper/Figs/*.marks.json`, and the csvs of `results/` at thetaSource C. ρ = 1 unless a row
says otherwise. The cross-section (end of section 6, section 7.3, appendix H), Argentina and appendix G were out of
scope. Writers take numbers from the sources named here, never from this file, and recheck them once the reruns
below land.

## Sources that are still pre-C
| Source | What still reads it | Status |
|---|---|---|
| `results/numerical/US_horizon.csv`, `US_horizonDesign.csv`, `US_residuals.csv`, `US_derivativeScheme.csv` | appendix D: `NUM_Horizon` prints a chosen design of 0.728, and `NUM_Residuals`' note quotes 9.11/1.99 p.p. (figure 6.1 now gives 9.12/2.04); `TerminalStates.tex:40–48` | rerun (`runHorizon.py`, U.S. parts, at C) |
| `results/numerical/C5_*.csv` | §7.1 footnote's 70/30 split (`EndogenousTheta.tex:29`); §7.2 footnote's three-step decomposition (`:60`, whose steps sum to −0.019/+0.021/+0.182 against figure 7.1's −0.061/+0.012/+0.302); appendix C's critical turnout ratios 3.39/3.4/11.5/1.84/1.76 (`EndogenousDesign.tex:43`) and πPath 0.46 (`:70`) | rerun (`c5Numbers.py` at C) |
| `results/esc/escPermanent*.csv`, `escSequentialCRRA.csv`, `escCornerSlope.csv` | §7.1 and its footnote (the corner "at every IES", the permanent choice), `Introduction.tex:27` footnote, `EndogenousDesign.tex:43,51` | dropped by RKB on 2026-10-30: restrict the claims to the one variant-C check (the costless choice one period ahead under log preferences gives θ = 0, `escCalibration.csv` spec `none`), and add the appendix C condition once `a1` is rerun |
| Medicare (`USMedicare_rhoGridCommonX.csv`, OA `OECD_Medicare`) | `OECD.tex:2` footnote, `CalibrationOECD.tex:10` (θ 0.522 "below the UK's 0.560"; at C the comparison would flip) | dropped by RKB on 2026-10-30: drop the sentence and the pointer |

## Stale numbers (number as printed → value at C; source)
**Section 6 (`OECD.tex`)**
- **:6, footnote.** "France ... θ = 1 at any cuts" → 0.822 (`USFRCalibration`). Variant C's θ does not depend on income
  cuts, so France's groups are cut at the U.S. percentiles.
- **:26, the design corner to corner.**
  - The tax: 6.6 → 6.7 (3.070 + 3.604).
  - The savings rate: 1.9 → 2.0.
  - The hours: "1.7 of them between the observed design and the Beveridgean corner" → 1.3.
  - Source: `US_overview` marks `--theta0/--theta1--rho1.0--{tau,sr,ww}`.
- **:28, ageing.** Acute 8.7 → 8.6; mild 4.0 → 3.9.
- **:30, France's characteristics.** Income distribution 1.3 → 2.0; voting profile 0.9 → 1.5. The footnote on why θ
  is held at its U.S. value ("read off the ratio of replacement rates") no longer applies: θ is read off the benefit
  formula and does not depend on the income distribution.
- **:37, footnote.** "the 1.23 of table 6.1" → 1.17 (table `USFRCalibration`'s ω).

**Section 7.1–7.2 (`EndogenousTheta.tex`)**
- **:7** 1.7 hours → 1.3.
- **:29** θ* = 0.728 → 0.544. The cost still cancels from θ, since both fitted coefficients carry f. Name the slope
  measure, not "the ratio of replacement rates".
- **:35** "exceeds 0.5 in 23 of its 29 countries" → 13 of 21.
- **:41** pinned acute ageing 7.8 → 7.4, "rather than 8.7" → 8.6. "France's income distribution lowers it by only 0.7
  p.p. at ρ = 0.5 and 1" → 1.0 and 1.1 pinned, 1.1 and 1.1 chosen (`US_ESC_overview` marks).

**Appendices**
- **F (`CalibrationOECD.tex`)**
  - :12 η "2.54" → 2.52.
  - :18 France θ = 1 → 0.822.
  - :24 η "2.51" → 2.49; X "6.64" → 6.48, "4.16" → 4.07.
  - :32 X "7.93" → 7.67; ω "1.10" → 1.04.
  - The UK's θ "0.560" → 0.181 (F.3 leaves the paper anyway).
  - :10 "what identifies θ from the replacement rates at those two income levels": θ is now the slope of the public
    pension on earnings; the cuts set γ and η only.
- **C (`EndogenousDesign.tex`)**
  - :72 multiples of the elasticity-based λ: "51 to 205 times at ρ = 1" → 28–113; "12 to 48 times at ρ = 2" → 6–25
    (λ 6.25 and 1.41 over (0.1 to 0.4) × Π/R 0.555). "More than an order of magnitude" holds at ρ = 0.5 and 1, not
    at ρ = 2. The same claim is at `EndogenousTheta.tex:35`.
  - :97 θ* = 0.728 → 0.544.
  - :103 "a flat benefit at the 2020 tax rate loses 43.7% of revenue ... fails for designs below 0.067" → 26.6%. At
    the 2020 tax λτṼ is 0.617, 0.286 and 0.065 at ρ = 0.5, 1 and 2, so the condition holds at every design and IES.
  - :70 "France's electorate is such a case, which is why no value of λ makes it re-elect its design": under C France
    is interior (0.822), its own λ is 13.59 (`US_ESC_Country`), and no sample country is at θ = 1. Drop the example.
- **B (`PoliticoEconomicEquilibrium.tex`)** :115 "a tax of 8.3% in 2020" → 6.9% (figure 6.1's θ = 1 bar; eq.
  repAgentTax gives 0.0692).

## Claims that no longer hold
- **Rankings "at every IES"** (`OECD.tex:26,30,33`; `Conclusion.tex:5`). At ρ = 2 the voting profile moves the tax
  2.8 p.p., more than the design from corner to corner, 2.0. At ρ = 0.5 the design (9.12) and acute ageing (9.12)
  tie. Claim the ranking at ρ ≤ 1.
- **"Several times more than any other characteristic"** (`EndogenousTheta.tex:41`): with the design pinned, ageing is
  7.5×, 5.8× and 2.7× the next at ρ = 0.5, 1 and 2.
- **"The loss is a small share of revenue"** (`:35`): 6.2%, 2.9% and 0.7% at the observed design. A flat benefit
  loses 4.3–4.6 times as much.
- **The income distribution "moves the design little except at ρ = 2"; "lowers the design slightly at ρ = 0.5"**
  (`:55,60`): it now lowers θ by 0.061 at ρ = 0.5, more than twice the voting profile's 0.025. The attribution to
  "the third force" needs the decomposition rerun.
- **Introduction :24** "responds much less to other characteristics": true corner to corner (6.7 against 2.0 and
  1.5); the move from the observed design to flat benefits is only 3.1 p.p.

## Correct, keep
- **Section 6**
  - :8: 1.6 times; 0.47 to 0.77.
  - :26: 2.4 hours.
  - :28: 2.0 p.p. of GDP; less than an hour; 0.17.
  - :30: "nearly the whole gap"; "every rate at the baseline".
  - :33: 9.1 p.p. at ρ = 0.5 and 2.0 at ρ = 2.
- **Section 7**
  - :35: "close to an order of magnitude"; λ falls with the IES.
  - :41: "about half as much"; at ρ = 1 less than the voting profile.
  - :55: ageing's savings and design effects; French voting lowers θ at every ρ.
  - :60: Ṽ from 0.436 to 0.218; +0.012 at ρ = 1, +0.302 at ρ = 2.
- **Abstract** :5.
- **Introduction**
  - :27 (λ re-elects θ*; ageing raises θ and τ).
  - :29.
- **Conclusion** :7.
- **Appendix F**: R 2.443, ξ = α = 0.30, Medicare's 2.9% and τ 14.7%, 0.82, 0.47–0.77, 58%, 1.09, 2.29 vs 3.08,
  0.81–0.86, 29% vs 58%, 3.06 vs 3.08, 0.61–0.74, 1.9 times.
- **Appendix C**: 1.61, θ = 0 under log, Π/R 0.55, R 2.44, λ 0.06–0.22, 39%.
- **Appendix B**: 10.5%.
- **Appendix D**: 1960 to 2200; one candidate passing, at most three.
