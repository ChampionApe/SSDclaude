# Scheme rules for theta and tau, countries A (draft, 2026-10-30)

Brief: rebuild theta (slope of relative benefit on relative earnings) and possibly tau from the actual pension rules
(every mandatory tier, its financing, minimum or targeted pensions and how many receive them). This note covers AUS AUT
BEL CAN CZE DNK FIN FRA DEU GRC HUN ISL IRL; another agent does the other 13 on the same schema, a third the
harmonised OECD/Eurostat tables. Nothing here is wired or chosen.
Output: `data/oecd26_pensionSchemes_A.csv` (49 rows, one per scheme; first line is a `#` draft comment, read with
`comment="#"`). Raw files: `logs/thetaTau_raw/countriesA/` (gitignored). Built by
`python/paper/oecd26SchemesA.py` (stage (0), no network); derived ratios carry their formula in `note`.
Conventions: % AW uses the PaG 2021 key-indicator average worker earnings (2020, national currency); recipient
shares use Eurostat `demo_pjangroup` population 65+ on 1 Jan 2021; % GDP uses Eurostat `nama_10_gdp` 2020
(CP_MNAC). Confidence: high = official statistics, medium = PaG 2021 profile or EU Pension Adequacy Report 2021
vol. II (PAR), low = secondary.

## Sources that worked, and those that did not
- PaG 2021 country profiles: oecd.org now returns 410; fetched from the Wayback Machine (2022 snapshots).
- PAR 2021 vol. II (Council doc ST-9145-2021-ADD-2): rules, recipient shares, contribution rates for the 10 EU members.
- National statistics reached: DST PEN122 (API), DSS Demographics June 2020 (data.gov.au), ESDC quarterly report
  Jan-Mar 2020, Kela open data (avoindata.suomi.fi), Statistics Iceland FEL02000/FEL02001 (PX API), DREES (fiche 08
  of 2024, fiche 25 of 2022, press release of 20/12/2021), Destatis press release 188/2021, ČSSZ open-data dumps.
- Blocked (HTTP 403 or bot check, not circumvented): SSA *Social Security Programs Throughout the World*, ISSA
  country profiles, oecd.org (PaG 2021 tables), gov.ie (DSP statistics), althingi.is, aihw.gov.au,
  publications.gc.ca PDFs. MISSOC moved to an EC page without the tables. So no row is sourced to SSA or MISSOC.

## Per country
**AUS.** Public provision is the flat, means-tested Age Pension from general revenue (27.0% AW single maximum);
67.0% of its 2.56 m recipients get the full rate (June 2020), 32.7% a part rate (income test 50%, assets test
AUD 3/fortnight per AUD 1,000). The Superannuation Guarantee (9.5% employer, funded DC, private) is the only
earnings-related tier. For theta: public benefits fall with own income (theta <= 0 on the public side); the PaG
replacement-rate ratio gets its slope from the private SG, which tau (public spending) excludes.

**AUT.** A single earnings-related DB tier (1.78% per year, ceiling 154.5% AW), payroll PAYG plus a federal transfer
of 22% of statutory spending (2.44% GDP, 2018). The Ausgleichszulage tops household income up to 27.8% AW; 8.8% of
all pensions and 6.2% of direct old-age pensions had one (Dec 2018), average EUR 313/month. A full career at 0.5 AW
(about 40% AW) is above the Richtsatz, which is why PaG's ratio misses it. AZ spending not found.

**BEL.** Earnings-related DB (60%/75% of revalued career earnings over 45 years) with three floors: a credited
earnings floor per year (54.1% AW; it binds at 0.5 AW, so PaG's ratio probably already reflects it), a minimum pension after 30
years (32.5% AW; about 1 in 5 women and 1 in 20 men, 2013) and GRAPA (29.0% AW, 4.9% of pensioners, 2018).
Occupational pensions are voluntary but reach 75% of workers through sector plans (median contributions 1-6%).

**CAN.** Three public tiers: OAS flat residence pension (12.9% AW, general revenue, 15% clawback), GIS income-tested
top-up (19.2% AW; 32.3% of OAS pensioners, 2.08 m), and CPP/QPP earnings-related to the YMPE (102.5% AW; 5.25% + 5.25%).
From ESDC's monthly amounts, OAS pension CAD 3.72 bn and GIS CAD 1.07 bn a month against 2019-20 forecasts of OAS
programme CAD 56.2 bn, CPP 50.1 bn, QPP 15.6 bn, so OAS+GIS are 46% of the three (derived).
2020 retirees get the base CPP (25%); the enhancement accrues from 2019.

**CZE.** One public PAYG pension with a flat basic amount (10.4% AW, all pensioners) plus a progressive percentage
amount (1.5% a year of earnings counted 100% to 44% of the average wage, 26% to 400%). Contribution 28% (6.5 + 21.5).
Old-age pensions cost 7.06% of GDP in 2020 (ČSSZ). The legal minimum (12.7% AW) binds rarely: 0.82% of old-age
pensions are below CZK 5,000 (an upper bound). Theta follows from the formula; no means-tested tier for pensioners.

**DNK.** Public folkepension = basic amount (17.6% AW, residence, earnings-tested at 30%) + pension supplement
(19.6% AW single, 30.9% taper on all non-public income); 57.5% of the 1.10 m recipients get the full supplement,
29.2% a reduced one, 10.5% none (Jan 2020). ATP is a statutory funded flat contribution (DKK 3,408/yr, 0.78% AW);
quasi-mandatory occupational DC (10-18% by collective agreement) covers about 90% of employees; coverage grew from the
mid-1980s, so 2020 retirees have short occupational careers. Public theta is about zero or negative; the slope sits in the private tier.

**FIN.** Statutory earnings-related pensions (TyEL 24.4%, no ceiling, partly funded, run by private insurers)
dominate. Kela's national pension (17.4% AW, 50% pension test) reaches 35.6% of people 65+ and cost
0.63% of GDP in 2020; the guarantee pension (21.9% AW, 100% test) reaches 3.6% of 65+ (0.11% GDP, all ages).

**FRA.** Two mandatory earnings-related tiers: CNAV (50% of the 25 best years, to the PSS 107.7% AW) and
AGIRC-ARRCO points (to 8 PSS; 24.5% of obligatory-scheme pensions, 2018). Minimum pensions are frequent: 37% of
retirees living in France get a minimum (MiCo, minimum garanti, PMR) at end 2020, but only 18% of new CNAV pensions
(2020-21) since the 2012 tightening, a large flow-stock gap. ASPA/ASV (28.4% AW) reaches 4.5% of 65+ (635,300).

**DEU.** A single earnings-related points system (18.6%, ceiling 158.9% AW). Grundsicherung im Alter, needs-based
(about 18.7% AW), reaches 3.1% of 65+ (564,110, Dec 2020). The Grundrente starts in 2021 (not a 2020 rule; about
1.3 m expected). Civil servants (15% of older people's pension income): 8.8% on the 35% minimum (2020).

**GRC.** Since Law 4387/2016 every main pension = a flat national pension (EUR 384, 21.8% AW, State budget,
conditional on 15+ years of insurance and residence) + a contributory DB part (0.77%-2.55% accrual, ceiling
369% AW) + a mandatory PAYG auxiliary (DB to 2014, NDC since). The national pension is a fixed (1 - theta)
component of nearly every new pension; its spending and the treatment of pre-2016 pensions were not found.

**HUN.** One mandatory public earnings-related DB on net earnings (43% at 15 years to 80% at 40, progressive
reduction at the top; 10% employee + 15.5% unified employer tax). The minimum pension (HUF 28,500, 6.8% AW,
frozen since 2008) is "very rare" (PaG); 92% of those above pension age get an old-age benefit (2019). Theta is
close to 1; the means-tested old-age allowance is small and unquantified.

**ISL.** TR basic pension (33.3% AW, 45% taper on all income including occupational pensions) plus a household
supplement (8.4% AW, 11.9% taper), from general revenue; mandatory funded occupational pensions (15.5%). In Dec 2020
TR reached 56% of 67-69, 79% of 70-74 and 84% of 75+; only 1,277 people 67+ got TR alone. Public theta is negative
(TR falls with occupational income); the earnings slope sits in the funded tier.

**IRL.** Flat contributory State Pension (27.7% AW, PRSI 15.05% via the Social Insurance Fund with an Exchequer
subvention) and the means-tested non-contributory pension (26.4% AW, general revenue); 82% / 18% of their 526,078
recipients (2019). No mandatory private tier in 2020. Public theta is about zero; PaG's ratio (59.4 vs 29.7 at 0.5
and 1.0 AW) is exactly the flat-rate signature.

## What does not reproduce, or conflicts
- BEL benefit ceiling for 2019 wages: PaG EUR 59,615.88, PAR EUR 58,446.94.
- ISL: PaG's withdrawal threshold "ISK 300 000 million or equivalent to 31% of AW" is inconsistent; ISK 300,000/yr
  is 3.2% AW. Hagstofa FEL02001 mislabels its third payment category (FEL02000 calls it "occupational only").
- DNK occupational coverage: the PaG profile says both about 90% and about 85%.
- FRA MiCo and ASPA amounts in PaG are 2021 values; DREES gives end-2020 ASPA EUR 10,838/yr (used).
- DEU: Destatis's Grundsicherung rate uses the population above the age threshold; 3.1% here is of all 65+.
- CZE: ČSSZ's "old-age pensions total" (1.81 m) excludes pensions paid together with a survivor's pension.

## Gaps
- Spending of the minimum/targeted schemes: AUT AZ, BEL minimum pension and GRAPA, DNK supplement, FRA MiCo and
  ASPA, DEU Grundsicherung, GRC national pension, IRL SPC/SPNC, ISL TR, AUS Age Pension (DSS annual report not
  fetched). FIN and CZE found; CAN in CAD only (no GDP fetched). The ESSPROS means-tested split (other agent) may fill these.
- Recipient shares missing or old: HUN minimum pension and old-age allowance, GRC national pension, DNK ældrecheck,
  ISL household supplement, BEL (2013 and 2018 values), AUT (2018), IRL (2019), AUS share of the age-eligible
  population (no ABS denominator).
- Contribution rates not in the fetched sources: AUT, BEL, GRC employee/employer split; contribution ceilings for
  BEL, CZE, HUN, IRL; GIS and SPNC tapers.
- Financing statements not verified in a budget source: CAN OAS/GIS general revenue, CPP partial funding, BEL GRAPA,
  ISL TR, AUT AZ federal reimbursement.
- SSA SSPTW and MISSOC not used (blocked or moved), so the medium-confidence cross-check rests on PaG and PAR alone.
