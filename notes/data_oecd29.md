# Data for calibrating the log model to the 29 OECD countries

A referee asked for the model's cross-country relations (spending and the Bismarckian index against population
growth and inequality) next to figure 1's data. This note records the inputs assembled for that (written
2026-10-23): what each comes from, the checks against the U.S., UK and France workbooks, and the open decisions.
Code: `python/paper/oecd29Data.py` (stage (0), not wired; `-I`, `--force` rebuilds, `--refetch` downloads again;
raw files in `logs/oecd29_raw/`). Outputs: `data/oecd29.csv` (one row per country), `oecd29_population.csv`,
`oecd29_distribution.csv` (with the validation rows), `oecd29_sources.csv` (URL and retrieval date per column).

## 1. Workers per retiree, $\nu_t$

**Found.** $\nu_t = P(t)/P(t-30)$, total population on 1 July, UN *World Population Prospects 2024*, medium
variant, reproduces all twelve workbook values (US and UK `Worker-to-retiree`, France's `Relative cohort sizes`,
1990-2080) to 4.5e-7, the workbooks' rounding; 1960 copies 1990 and 2110 copies 2080. The paper's "census data"
is this series. WPP 2022 and 2019 miss by up to 0.05 and 0.06 at these three countries (and by up to 0.13 and
0.17 across the 29 by 2080); OECD and World Bank totals give the US 1.328, not 1.340.
- **France.** Appendix F's rule on the WPP ratio gives the workbook's $\nu$ exactly in 2020 (0.966884) and 2050
  (0.903744), but 1.0208 for 1990 (workbook 1.0263) and 0.8727 for 2080 (0.8706): gaps of 2.43 and 2.04 years
  rather than 2.5 and 2.
- **`Worker-to-retiree (census)`** is read by no loader. France's column is the UK's times 0.684707 at all five
  dates; no WPP 2024 age-band ratio reproduces the UK's (best maximum error 0.30). Not identified.
- Against figure 1's growth (OECD 2020/1990): correlation 0.997; largest gaps ISL 0.041, FRA 0.035 (the overseas
  departments enter the OECD series in 1991), KOR 0.033.

## 2. Income groups

Paper's rule: group 1 has mean half the mean, group 2 the mean ("own"); France's convention cuts at the US
shares 0.582266/0.757993 ("usPct"). Under "own" $y = (0.5, 1, y_3)$, so the shares carry the information. No
public source covers men's labour income at percentile resolution (LIS needs LISSY; WID has labour income for
France only). Candidates, at the workbooks' survey years (US 2018, UK 2006, France 2018), against the workbooks:

| candidate | US own: $\gamma_1/\gamma_3$, $\tilde V$ | UK own: $\gamma_1/\gamma_3$, $\tilde V$ | FR usPct: $y_1/y_3$, $\tilde V$ | FR at UK cuts $\tilde V$ |
|---|---|---|---|---|
| **workbooks** (CPS, BHPS w17, LIS) | .582/.242, **.436** | .292/.127, **.223** | .637/1.873, **.218** | **.245** |
| OECD earnings deciles, men full time (P10/P50/P90, two-piece lognormal) | .475/.206, .365 | .296/.129, .227 | .682/1.727, .161 | .162 |
| ILO modelled labour income, all workers, deciles | .618/.291, .468 | .536/.275, .400 | .614/1.893, .244 | .306 |
| OECD Education at a Glance, men 25-64, five bins | .545/.295, .403 | (2013) .397/.221, .292 | .604/1.839, .247 | .350 |
| OECD IDD, disposable P10/P50/P90 | .518/.298, .379 | .397/.201, .297 | (2020) .688/1.670, .149 | .177 |
| EU-SILC, disposable deciles | -- | .400/.204, .299 | .668/1.759, .176 | .216 |
| WID disposable (diinc), g-percentiles | .691/.278, .537 | .413/.102, .345 | .677/1.736, .166 | .199 |
| WID pre-tax national income (ptinc) | no group 2 | no group 2 | .466/2.256, .525 | .872 |

Mean $|\Delta\tilde V|$ over the first three targets: OECD men full time .044, EAG .044, IDD .067, ILO .079,
WID diinc .092 (over all four: .054, .059, .067, .074, .081).

**Recommended: the OECD earnings database, men, full-time employees** (`OECD.ELS.SAE:DSD_EARNINGS@DEC_I`,
P50/P10 and P90/P50), through a two-piece lognormal, 2019 or nearest (2018 for CHE, ISL, POL, TUR). It is the
paper's sex, one consistent series, 29 of 29, and defined under both conventions everywhere. It reproduces the
UK's BHPS grouping (shares within .006, $\tilde V$ +.004) but, being full-time only, misses part-year and part-time
men and understates the CPS and LIS dispersion ($\tilde V$ -.071 US, -.058 France; France's bottom 29% earn .575
of the mean, not .508). Under "own", compressed countries get small bottom groups: SWE .023, ITA and NOR .054,
FIN .059, DNK .074, BEL .083. **Alternative: ILO** (in the file for all 29): right for the US and France but both
sexes, so female part-time inflates it (UK +.177); at decile resolution "own" has no group 2 for GBR and JPN;
KOR and NZL are imputed. EAG is the right population but breaks in levels across countries (GBR 2019, FRA 2020,
BEL 2021, HUN 2019, NOR 2016; no ISL; JPN 2012 only), so it validates only. 2019 rather than 2020: earnings ratios
jump in 2020-21 for ESP, IRL, ITA. Across the 29, $\tilde V$ (usPct) runs .081 (SWE) to .333 (USA); its
correlation with figure 1's Gini is .44.

## 3. Spending and replacement rates (checked, not refetched)

`oecdFigure1.csv` is complete for the 29: spending (cash, and cash plus in kind), replacement rates at 0.5 and
1.0 of average earnings for men and women, the index. Two differences with the workbooks: their spending is
SOCX cash plus in kind for the UK (8.3 against 8.27) and France (14.9 against 14.88), not figure 1's cash concept
(7.84, 14.44), and 10.1% for the US (7.2 pensions plus 2.9 Medicare; SOCX 7.37 cash, 7.43 with in kind). The US
replacement-rate ratio is 39.2/49.2 = .797 in the workbook against 39.2/49.6 = .790 in PaG 2021 (UK and France match).

## 4. Secondary inputs

- **Voting.** CSES modules 5 and 6 and the IMD, all plain HTTP. Turnout in the main election by household-income
  quintile ("not registered" counts as not voting), one election per country nearest 2020 within 2015-22 with
  at least 30 respondents per quintile: 28 of 29 (Luxembourg never in the CSES); ESP 2008 and PRT 2009 fall
  outside (PRT 2019 has 23 respondents in Q5, on fixed brackets). `mu1-3` average the weighted quintiles over
  each group's percentile range. That rule, on CSES France 2007 unweighted at the US cuts, gives France's workbook
  values to 4e-4: the paper's French source is module 3. The UK's are not reproduced (closest: 2005, weighted,
  0.032). For the US (CPS in the workbook: .474/.629/.765) the CSES 2020 gives .641/.823/.860. Self-reported
  turnout is too high (US .76 weighted against about .67), so the gradient is more reliable than the level.
  OECD WISE has no turnout by income; the ESS needs a login.
- **Normal retirement age**, PaG 2021 figure 3.7 (StatLink 2cvxya), current (retiring 2020) and future (entering
  2020), by sex, 29 of 29. France 64.5 and 66 against the US 66 and 67, not appendix F's 63.5 and a gap of 2;
  Turkey 52 for men now; future ages indexed to life expectancy reach 74 (DNK), 71 (ITA), 69 (NLD).
- **PWT 11.0** labour share and K/Y (rnna/rgdpna and cn/cgdpo), 2019-20, 29 of 29. **OECD hours** actually worked
  per worker, 29 of 29 (the OECD warns levels are not comparable; Mexico 2,247 against PWT's 1,639).
- **Informality** (SDG 8.3.1) 24 of 29, none for AUS, CAN, JPN, NZL, USA: MEX 56% (2020, series break),
  TUR 31%, KOR 29%, GBR 20% (2018), CZE 17%. **Old-age pension coverage** (SDG 1.3.1) 29 of 29: below 90% only
  in AUS 74, ISL 82, POL 84 and ESP 88; MEX 100 (non-contributory). EU series break in 2021.

## 5. Decisions needed

1. Distribution source: the recommended OECD men full-time, or ILO. Then whether the US, UK and France keep their
   microdata groupings (mixed concepts across the 29) or take the public source too.
2. Year 2019 (used, pre-pandemic) or 2020.
3. "Own" cuts everywhere, or the US percentiles for the countries with $\theta = 1$ (AUT, FIN, FRA, HUN, ITA, ESP,
   TUR), as for France; under "own" the Nordic countries, Italy and Belgium have bottom groups of 2-8%.
4. $\nu$: plain WPP 2024 (as the US and UK); the age adjustment for France only, as now; or for every country
   (`wpp2024_nraAdj`, which moves TUR, DNK and ITA by 0.3 to 1.1). Also France's 1990 and 2080 workbook values,
   which do not follow the stated rule.
5. Spending concept for the 29 (figure 1's cash, or cash plus in kind as in the UK and France workbooks).
6. Voting: weighted or unweighted CSES, the election for PRT and ESP, and the US from CPS or CSES.
7. Mexico and Turkey: informal employment of 56% and 31%. Keep them, flag them, or drop them.
