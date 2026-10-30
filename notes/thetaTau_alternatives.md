# Measuring θ and τ in the OECD cross-section: three alternatives (2026-10-30)

For O5 of the 2026-10-29 review (`notes/reviewResponse_2026-10-29.md`). Data: `notes/data_thetaTau.md` (A, F) and
`data_thetaTau_countriesA.md`, `_countriesB.md`. Numbers: `logs/thetaTau_alternatives.py` (→ `logs/thetaTau_alternatives.csv`).
First pass, nothing decided.

**Common ground.** In the model $b_i = [\theta y_i + (1-\theta)\bar y]\bar b$, so $1-\theta$ is the share of spending
not linked to own earnings and θ is the slope of relative benefits on relative earnings. Tax: $\tau = S/(1-\alpha)$ with
$\alpha = 0.30$, where $S$ is pension spending in % of GDP. The rule for every alternative: **the tiers in τ are the
tiers whose design θ measures.** θ has two parts:
- the formula slope: least squares of the pension on earnings at 0.5, 1 and 2 AW, from PaG 2021 (NZ's low earner is at
  0.6 AW). The model's group 3 mean lies at 1.5–2.0 AW, so 0.5–2 AW spans its groups, while 0.5–1 AW does not;
- times $(1-s)$, with $s$ the share of spending on minimum top-ups and tested benefits that PaG's full-career worker
  never reaches. Found for ESP, FIN, ITA (assegno sociale only), HUN (≈0), JPN, SWE, CHE, USA; not yet for the rest.

## A. The public system

- **Funds.** All public schemes: earnings-related social insurance, flat or basic pensions, minimum top-ups,
  means-tested pensions, and government-employee schemes, as in SOCX public cash, old age and survivors (today's τ).
  Funded private tiers are left out. With log preferences and no binding mandate they are private saving in the model,
  so retirement consumption from them is still in the model, through savings. Variant: take government-employee
  pensions (1–4% of GDP) out of τ, since θ is measured on private-sector rules.
- **Timing.** Spending and $s$ are in force in 2020. The formula slope is PaG's steady state for new entrants under
  2020 law; they coincide unless a reform is phasing in. The exception is the UK: 2020 retirees draw basic State
  Pension plus S2P, so θ is S2P's share of State Pension and Pension Credit spending, 0.18 (steady state: 0).
- **Gross/net.** Gross for both, as the model taxes labor income only. No public-tier net replacement rates exist by tier.

## B. All mandatory and quasi-mandatory provision

- **Funds.** A, plus legislated funded tiers (AUS SG, CHE BVG, ISL occupational funds, NOR OTP) and occupational
  tiers by collective agreement (NLD, DNK, SWE). θ comes from PaG table 4.1 (all mandatory tiers). τ adds SOCX
  mandatory private, plus SOCX voluntary private as a proxy for NLD and SWE, whose occupational tiers SOCX books as
  voluntary. τ is weak: SOCX and PaG classify tiers differently, and SOCX revised its private series by up to 40%.
- **Timing.** Mismatched where funds are immature. θ is PaG's steady state, while 2020 benefits are far below it in AUS,
  NOR and GBR (auto-enrolment pays almost nothing yet). There, B in force is close to A (GBR: θ 0.18, not 0.56).
- **Gross/net.** Gross. Conceptually B also breaks the model's PAYG budget: funded benefits earn r and transfer nothing
  between generations, so they inflate the transfer behind ω.

## C. The public system on the countries it describes

A, on the countries where one public PAYG system is the bulk of retirement provision. The rule, fixed before any
slope is seen: drop a country if funded tiers pay at least a quarter of its mandatory benefits in 2020 (`privShare`
below), or if its public pension is tested against them (θ_A < 0). Dropped: AUS, ISL, CHE, NLD and DNK; 21 remain.
SWE (0.19) and NOR (0.00 in 2020) stay. Timing and gross/net as in A.

## Implied θ and τ (τ in % of labor income; ≤: top-up spending not yet found, so an upper bound)

| | Paper θ | Paper τ | A θ, 0.5–2 AW | A θ, 0.5–1 AW | A τ | A τ, no gov. employees | B θ | B τ | private share | in C |
|---|---|---|---|---|---|---|---|---|---|---|
| AUS | 0.00 | 5.9 | <0 | <0 | 5.9 | 3.7 | 0.59 | 12.4 | 0.52 | no |
| AUT | 1.00 | 20.5 | ≤0.75 | ≤1.00 | 20.5 | 16.9 | ≤0.75 | 20.5 | 0 | yes |
| BEL | 0.44 | 16.4 | ≤0.38 | ≤0.45 | 16.4 | 16.4 | ≤0.38 | 16.4 | 0 | yes |
| CAN | 0.63 | 9.1 | 0.32 | 0.63 | 9.1 | 7.6 | 0.32 | 9.1 | 0 | yes |
| CZE | 0.34 | 12.4 | 0.34 | 0.34 | 12.4 | 12.4 | 0.34 | 12.9 | 0.04 | yes |
| DNK | 0.44 | 11.7 | <0 | <0 | 11.7 | 9.9 | 0.49 | 14.6 | 0.19 | no |
| FIN | 1.00 | 17.9 | 0.94 | 0.94 | 17.9 | 12.4 | 0.94 | 17.9 | 0 | yes |
| FRA | 1.00 | 20.6 | ≤0.85 | ≤1.00 | 20.6 | 17.3 | ≤0.85 | 20.6 | 0 | yes |
| DEU | 0.88 | 16.0 | ≤0.72 | ≤0.88 | 16.0 | 13.5 | ≤0.72 | 16.0 | 0 | yes |
| GRC | 0.83 | 25.5 | ≤0.83 | ≤0.83 | 25.5 | 21.2 | ≤0.83 | 25.6 | 0 | yes |
| HUN | 1.00 | 11.0 | 1.00 | 1.00 | 11.0 | 11.0 | 1.00 | 11.0 | 0 | yes |
| ISL | 0.59 | 4.4 | <0 | <0 | 4.4 | 4.4 | 0.81 | 12.5 | 0.65 | no |
| IRL | 0.00 | 4.6 | 0.00 | 0.00 | 4.6 | 3.2 | 0.00 | 4.6 | 0 | yes |
| ITA | 1.00 | 24.9 | ≤0.98 | ≤0.98 | 24.9 | 19.5 | ≤0.98 | 25.3 | 0.02 | yes |
| JPN | 0.67 | 13.7 | 0.66 | 0.66 | 13.7 | 12.2 | 0.66 | 14.2 | 0.03 | yes |
| LUX | 0.82 | 12.9 | ≤0.82 | ≤0.82 | 12.9 | 12.9 | ≤0.82 | 12.9 | 0 | yes |
| NLD | 0.95 | 9.7 | 0.00 | 0.00 | 9.7 | 7.5 | 0.95 | 14.3 | 0.32 | no |
| NZL | 0.34 | 7.3 | 0.00 | 0.00 | 7.3 | 7.3 | 0.00 | 7.3 | 0 | yes |
| NOR | 0.68 | 10.8 | ≤0.31 | ≤0.63 | 10.8 | 10.8 | ≤0.42 | 10.8 | 0 | yes |
| POL | 0.96 | 16.3 | ≤0.96 | ≤0.96 | 16.3 | 15.3 | ≤0.96 | 16.3 | 0 | yes |
| PRT | 0.98 | 19.4 | ≤0.96 | ≤0.98 | 19.4 | 19.4 | ≤0.96 | 19.4 | 0 | yes |
| ESP | 1.00 | 18.3 | 0.86 | 0.95 | 18.3 | 16.9 | 0.86 | 18.3 | 0 | yes |
| SWE | 0.85 | 12.1 | 0.38 | 0.78 | 12.1 | 10.6 | 1.13 | 15.0 | 0.19 | yes |
| CHE | 0.80 | 9.8 | 0.21 | 0.46 | 9.8 | 9.8 | 0.30 | 18.1 | 0.46 | no |
| GBR | 0.56 | 11.2 | 0.18 | 0.18 | 11.2 | 7.6 | 0.56 (in force 0.18) | 12.1 | 0.07 | yes |
| USA | 0.73 | 10.5 | 0.54 | 0.73 | 10.5 | 7.3 | 0.54 | 10.5 | 0 | yes |

Reading:
- **A, 0.5–2 AW.** No country is left at θ = 1 except HUN. ITA (0.98, integrazione missing) and FIN (0.94) come
  close. The θ = 0 corner gains NLD and NZL, and three countries are below the model's range (AUS, DNK, ISL).
- **C.** It removes those three and the two largest private tiers (NLD, CHE), leaving three corners: IRL and NZL at
  θ = 0, both flat public pensions, and HUN at θ = 1, whose minimum pension is negligible.
- **B.** It mostly restores the paper's index for the private-tier countries. It doubles or triples τ in AUS, CHE and ISL and raises
  it by about half in NLD and a quarter in SWE.
- **The 0.5–2 AW slope moves the U.S. from 0.73 to 0.54.** The model's sections 6–7 calibrate the U.S. at 0.728, so this
  measure cannot be used in the cross-section alone.
- **Taking government-employee pensions out of τ** cuts it by a quarter to a third in FIN, ITA, USA and GBR.

## Recommendation

**Main text: alternative C.**
- The public system on 21 countries, gross.
- θ is the 0.5–2 AW formula slope × (1 − s), with the UK in force; τ is today's SOCX public cash spending.
- θ and τ then describe the same budget, the minimum pensions enter, every corner but IRL, NZL and HUN disappears (IRL and NZL
  are genuinely flat, HUN genuinely proportional), and the selection rule is stated in data terms before any result.
- It requires the U.S. to be measured the same way in sections 6–7: θ = 0.54, which means re-calibrating ε and
  re-running the U.S. results. **Decision for RKB.** If that is too costly, the 0.5–1 AW column is the fallback. It
  keeps the U.S. at 0.73, but leaves AUT and FRA at 1 until their top-up spending is found.
- The model counterpart is the design in force in 2020, $\theta_{2020}$, as now.

**Appendix, one row each:**
1. A on all 26, θ clipped at 0: the referee's public-only index.
2. B on all 26: maximal coverage, against the paper's original concept.
3. τ without government-employee pensions, in A or C.
4. The paper's current index, for continuity.
5. Timing: PaG's steady state is the design legislated in 2020 for future retirees, so it is matched to the model's
   $\theta_{2050}$, chosen by the 2020 electorate at $\nu_{2020}$, rather than to $\theta_{2020}$. The model already
   produces it.

Net measures stay out until net earnings at 0.5, 1 and 2 AW (OECD *Taxing Wages*) and SOCX net spending are collected.

**Before any run:** top-up spending for AUT, FRA, DEU, BEL, LUX, NOR, POL, PRT and Italy's integrazione al minimo
(each "≤" cell); the two scheme csvs' builders moved into `python/paper/`; references for PaG 2021 tables 3.2, 4.1, 4.2.
