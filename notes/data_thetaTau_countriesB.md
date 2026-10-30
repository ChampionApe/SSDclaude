# Scheme rules for theta and tau, countries B (ITA JPN LUX NLD NZL NOR POL PRT ESP SWE CHE GBR USA)

Brief: rebuild theta (and possibly tau) from the rules of every mandatory tier, its financing, and the minimum or
targeted pensions with their recipients; the harmonised OECD/Eurostat tables are another agent's. Collected
2026-10-30. Output: `data/oecd26_pensionSchemes_B.csv` (draft, not wired; first line is a `#` comment; 49 rows, one
per scheme; source, URL, retrieval date and confidence on every row). Raw files and their URLs:
`logs/thetaTau_raw/countriesB/` (`SOURCES.txt`); writer `python/paper/oecd26SchemesB.py` (no network). % of AW uses the
PaG 2021 country-profile AW; % of GDP uses Eurostat `nama_10_gdp` CP_MNAC or World Bank `NY.GDP.MKTP.CN`; shares
of 65+ use World Bank `SP.POP.65UP.TO`. Rules come mostly from the PaG 2021 country profiles (Wayback copies; the
oecd.org files return 410). Recipients and spending come from national administrative sources.

## By country

**ITA.** INPS earnings-related pensions, 16.2% of GDP in 2020, payroll-financed; 2020 retirees get DB+NDC pro rata
(NDC only for those who entered after 1995). The flat elements in the 2020 stock are the *integrazione al minimo*
(22.2% AW; PaG: 32% of 65+ in 2018; 3.18 mn integrated pensions and EUR 8.8 bn in 2016, a secondary source) and
the *assegno sociale* (19.8% AW, 803k = 5.8% of 65+, 0.30% GDP = 1.8% of INPS pensions). The minimum supplement
does not exist for NDC-only careers, so it disappears in steady state. Indexation is also progressive (100% of CPI
up to 3x the minimum, 40% above 9x). TFR (6.91% severance) is not a pension.

**JPN.** Two public tiers: the flat basic pension (15.1% AW for 40 years) is JPY 24.3 tn, 4.4% of GDP, 43% of the
public-pension annual amount (FY2020); the EPI earnings-related part is 5.7% of GDP, capped at about 150% AW, with a
18.3% contribution. The targeted part is small: the 2019 supplementary benefit (5.27 mn = 14.5% of 65+, about JPY
4 000/month, 0.04% GDP) and public assistance (2.8% of 65+). The flat tier is earned by contribution years, not by
earnings.

**LUX.** One general scheme with three pieces: flat increments (12.0% AW for 40 years), proportional increments
(1.8% accrual on career earnings, maximum pension 181% AW) and a minimum pension at 39.1% AW. The general scheme
spends 8.3% of GDP (2020). The global contribution rate is 24%, of which 8% employee and 8% employer, so the State pays 8% (inferred): part of
tau is general revenue.
Minimum-pension recipients: 16.4% of pensions in 2023, 19.5% in 2009 (Paperjam citing the ministry); 2020 is a gap.

**NLD.** The public tier is flat: AOW at 28.5% AW (PaG 29.2), 5.05% of GDP, financed by a 17.9% premium up to 63%
of AW plus general revenue. AIO tops up incomplete AOW for 1.45% of AOW households (0.04% GDP). The earnings link
sits in the quasi-mandatory funded occupational DB (about 90% coverage, accrual up to 1.875% on pay above a
franchise up to 201% AW). PaG's mandatory replacement rates include that tier, while SOCX public spending covers
only AOW: the clearest case of mismatch (a).

**NZL.** NZ Super is flat and universal (39.8% AW, 4.7% of GDP, tax-financed, no contributions); supplementary
assistance reaches 19.2% of 65+ (mostly the Disability Allowance; the Accommodation Supplement reaches 5.8%) for
0.11% of GDP. KiwiSaver is voluntary with auto-enrolment. With a flat benefit the replacement rate falls in
proportion to earnings, so PaG's 0.6 AW low earner gives a ratio of 0.60, not the 0.5 a flat benefit gives with
0.5 AW (figure 1's bbIndex 0.6039).

**NOR.** 2020 retirees are mostly on the old rules (born 1953 or earlier; 1954-62 pro rata): a basic pension plus
a points-based supplementary pension, topped to a minimum pension level of 32.5% AW. 14.1% of old-age pensioners are
on it (23.5% of women, Dec 2020). The new rules are an NDC-like income pension (18.1% up to 7.1G = 114% AW) and a
guarantee pension at 30.5% AW, tapered 80%. Old-age spending was NOK 241 bn (6.7% of total GDP), financed through general
NI contributions (8.2% employee, up to 14.1% employer; earmarking not verified). The mandatory OTP (2% of 1G-12G) is small. Public-sector
occupational DB and AFP are not covered.

**POL.** NDC with initial capital (19.52% up to 257% AW), so the earnings link is strict. The flat elements are the
minimum guarantee (23.6% AW, 25/20 years; 221k = 3.7% of ZUS old-age pensioners in March 2020; PaG 1.5% of 65+) and
the 13th pension (PLN 1 200 = 2% AW per year to all pensioners, about PLN 11.7 bn = 0.5% GDP planned for 2020, a
press source). Pensioners without 25/20 years get less than the minimum. KRUS (farmers, largely
budget-financed) is not covered.

**PRT.** The Regime Geral DB has a progressive accrual (2.3% for reference earnings up to 1.1 IAS, falling to 2.0%
above 8 IAS). Minimum pensions by contribution years run from 19.8% to 28.6% AW; CSI (27.0% AW) reaches 171.8k =
8.3% of old-age pensioners (2020); 26k non-contributory social pensions. The number and cost of minimum-pension
top-ups are the main gap (PaG does not report them either).

**ESP.** One contributory DB (11.7% of GDP 2020) with a contribution ceiling of 181% AW and a maximum pension of
139.5% AW. *Complementos a minimos* reach 22.5% of retirement pensions (24.0% of all contributory pensions) and cost
EUR 6.96 bn (0.62% GDP, 5.3% of contributory spending), booked as non-contributory since 2014. The minimum is 35.5% AW. PNC
pensions add 0.22% GDP. PaG's replacement rates are equal at 0.5 and 1.0 AW (theta = 1), even though a quarter of
pensions are topped up to the minimum.

**SWE.** NDC 16% + FDC 2.5% up to 116% AW (strict link; PaG text says "just over 111%"). The guarantee pension
(22.2% AW, 100% taper on the first 13% AW of income pension, 48% above) reached 44% of female and 13% of male
pensioners in 2018 and cost SEK 13.1 bn (0.28% GDP). Housing supplement (62% taper) on top. Quasi-mandatory
occupational DC (>90% coverage) pays 4.5% below the public ceiling and 30% above it, which restores the earnings
link above 7.5 IBA. Cohorts born 1938-53 still have ATP rights (PaG Table 3.1 panel B).

**CHE.** AHV benefits are compressed between 16.3% and 32.6% AW (maximum reached at 97.7% AW); AHV spending is
6.5% of GDP, financed by payroll, a federal contribution and VAT. EL reaches 12.7% of old-age pensioners and costs
CHF 3.17 bn (0.45% GDP; it raises the AHV pension sum by 8.3%). Mandatory BVG credits run on coordinated pay
(24.4%-97.7% AW) and pay CHF 31.5 bn in pensions (4.4% GDP) plus CHF 10.9 bn in lump sums. PaG's mandatory
replacement rates mix in BVG.

**GBR.** For 2020 retirees: the new State Pension (21.9% AW, flat), whose transitional starting amount carries
pre-2016 additional-pension rights, plus Pension Credit (21.7% AW). The 2019/20 stock is a basic SP (16.8% AW,
2.96% GDP) plus SERPS/S2P (0.81%) plus nSP (0.48%). The earnings-related parts (S2P, GRB, protected payments) are
about 21% of State Pension spending (GBP 98.8 bn, 4.4% GDP). Pension Credit goes to 12.4% of the State Pension
caseload (0.22% GDP). In steady state: flat nSP plus auto-enrolment DC (8% of band earnings).

**USA.** The PIA is 90/32/15 with bend points at 20.7% and 124.8% of AWI 2020 (19.1% and 115.3% of the OECD AW,
22.1% and 133.1% of AWI 2018, the index that sets them); the taxable maximum is 247.5% of AWI 2020 (228.7% of the
OECD AW). SSI 65+: 2.3 mn (4.3% of 65+, counting disabled recipients who aged in; PaG says 2.2%), FBR 15.6% AW,
0.06% GDP.

## Does not reproduce PaG 2021 Table 3.2 (its values in brackets)
ITA minimum 22.2% AW (22.7); NLD AOW 28.5% (29.2); CHE EL recipients 12.7% (stored as 0.127); USA SSI 4.3% of 65+
(2.2%, apparently the aged category only); SWE ceiling 115.7% AW (profile text "just over 111%").

## Gaps
- ITA: 2019-20 count and cost of *integrazione al minimo* (INPS Osservatorio pensioni / GIAS accounts); DB formula.
- LUX: 2020 minimum-pension count and cost (IGSS *Rapport general*); contribution ceiling; civil-servant schemes.
- PRT: count and cost of *complemento social*; CSI spending 2020 (*Conta da Seguranca Social 2020*); social-pension
  amount; contribution rate; CGA.
- POL: FUS old-age spending; KRUS; pensions below the minimum; 13th-pension outturn (ZUS/KRUS).
- NOR: cost of the minimum top-up; old-rule parameters; public-sector occupational DB and AFP.
- SWE: 2020 guarantee-pension outturn and recipients (annual-report tables are images); NDC/FDC/ATP spending;
  agreements other than ITP1.
- CHE: AHV contribution rate and its uncapped base (not in the collected sources).
- GBR: S2P accrual bands and contracting-out; the 2020/21 auto-enrolment band.
- USA: OASI spending and the payroll rate, SSI by eligibility category: ssa.gov refuses automated access
  (Akamai), and no workaround was attempted.
- JPN: spending on public assistance for the elderly; bonus ceiling; the general-revenue share of the basic pension.
- ESP: complemento income limit; PNC amount and count; Clases Pasivas (civil servants).
- NLD: occupational contribution rates and benefits (pension-fund statistics: other agent).
- Cross-checks not done: SSA *SSPTW* (blocked), MISSOC 2020 (no export found), EU Pension Adequacy Report 2021
  vol. II (the Council PDF download is cut off after 2-5 MB).
