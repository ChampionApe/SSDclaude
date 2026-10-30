r""" Stage (0), DRAFT: scheme-by-scheme pension rules for the cross-section, countries A (AUS AUT BEL CAN
CZE DNK FIN FRA DEU GRC HUN ISL IRL): every mandatory tier, its financing, the minimum or targeted pensions and
their recipients. Not wired into build.py, REPLICATION.md, the tests or any calibration;
notes/data_thetaTau_countriesA.md reads it.

Run:  .venv\Scripts\python.exe -I python\paper\oecd26SchemesA.py [--force] [--out PATH]
      -> data/oecd26_pensionSchemes_A.csv (one row per scheme; first line a `#` comment, read with comment="#")

No network and no file input. The values were read by hand off the raw files in logs/thetaTau_raw/countriesA/
(retrieved 2026-10-30; each row's `url` names its file's source) and sit in the rows below as typed numbers;
every percentage of AW or GDP is computed here from the amount and the denominator its `note` names. main skips
when the output exists unless --force; --out writes elsewhere, to check the committed csv byte for byte.
"""
import os, csv, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'data', 'oecd26_pensionSchemes_A.csv')
RET = '2026-10-30'
WB = 'https://web.archive.org/web/2022/https://www.oecd.org/els/public-pensions/PAG2021-country-profile-{}.pdf'
PAG = {k: WB.format(v) for k, v in dict(AUS='Australia', AUT='Austria', BEL='Belgium', CAN='Canada', CZE='Czech-Republic',
       DNK='Denmark', FIN='Finland', FRA='France', DEU='Germany', GRC='Greece', HUN='Hungary', ISL='Iceland',
       IRL='Ireland').items()}
PAR = 'https://data.consilium.europa.eu/doc/document/ST-9145-2021-ADD-2/en/pdf'
DST = 'https://api.statbank.dk/v1/data/PEN122/CSV?lang=en&YDELSESTYPE=46,47,48,49,50&ALDER1=TOT&KON=MOK&FAMTYPE=FAMIALT,ENL,PAF&ENHED=16,18,19&Tid=2020'
DSS = 'https://data.gov.au/data/dataset/cff2ae8a-55e4-47db-a66d-e177fe0ac6a0/resource/c91d7ee0-59e0-4fc9-92a9-066b840d1139/download/dss-demographics-june-2020-final.xlsx'
ESDC = 'https://www.canada.ca/en/employment-social-development/programs/pensions/pension/statistics/2020-quarterly-january-march.html'
KELA_G = 'https://avoindata.suomi.fi/data/dataset/53d56db9-475b-47e2-b862-56a1a463839a/resource/a75a1cce-6866-4c7d-9777-e3f41fe4b3af/download/data.csv'
KELA_P = 'https://avoindata.suomi.fi/data/dataset/8df7939b-6c0e-4587-9aa1-95c076e7b0a3/resource/60a6abdf-3d43-424b-8c90-07c2553e951f/download/data_2020.csv'
HAG = 'https://px.hagstofa.is/pxen/api/v1/en/Samfelag/felagsmal/lifeyristhegar/FEL02001.px ; .../FEL02000.px'
DREES08 = 'https://drees.solidarites-sante.gouv.fr/sites/default/files/2024-10/RR24%20-%20Fiche%2008%20-%20Les%20b%C3%A9n%C3%A9ficiaires%20d%E2%80%99un%20minimum%20de%20pension.pdf'
DREES25 = "https://drees.solidarites-sante.gouv.fr/sites/default/files/2022-05/25%20-%20Le%20minimum%20vieillesse%20et%20l'allocation%20suppl%C3%A9mentaire%20d'invalidit%C3%A9_0.pdf"
DREESPR = 'https://drees.solidarites-sante.gouv.fr/communique-de-presse/minimum-vieillesse-donnees-2020'
DESTATIS = 'https://www.destatis.de/DE/Presse/Pressemitteilungen/2021/04/PD21_188_228.html'
BMSGPK = 'https://de.readkong.com/page/soziale-und-finanzielle-auswirkungen-der-ausgleichszulagen-1221247'
CSSZ_N = 'https://data.cssz.cz/dump/vyplacene-duchody-dle-vyse.csv'
CSSZ_X = 'https://data.cssz.cz/dump/vydaje-na-duchody-v-cr.csv'
ES_POP = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_pjangroup (sex=T, ages 65-69..85+, 2021)'
ES_GDP = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_gdp (CP_MNAC, B1GQ, 2020; updated 2026-10-22)'

# PaG 2021 key indicators: average worker earnings (AW), national currency, 2020
AW = dict(AUS=90861, AUT=48658, BEL=47720, CAN=57292, CZE=402261, DNK=437094, FIN=45719, FRA=38188, DEU=52104,
          GRC=21139, HUN=5.0e6, ISL=9.25e6, IRL=46685)
POP65_2021 = dict(AUT=1716287, BEL=2229378, CZE=2151834, DEU=18271636, DNK=1176272, GRC=2372760, FIN=1255938,
                  FRA=13970121, HUN=1949984, IRL=744177, ISL=54359)
GDP2020 = dict(FIN=236387.0, CZE=5828318.0)  # millions of national currency


def p(x, base, nd=1):
    return round(100 * x / base, nd)


rows = []


def add(**k):
    rows.append(k)


# ---------------- AUS
add(iso3='AUS', scheme='Age Pension', tier='targeted (means-tested flat)', financing='general revenue', legislated='legislated',
    rule='flat maximum rate, indexed twice a year to max(CPI, PBLCI), couple rate floor 41.76% of male total AWE; reduced by income test or assets test, whichever gives less',
    flat_or_min_pctAW=p(24551.80, AW['AUS'], 1), min_year='2020 (Sep)', qualifying='age 66; 10 years residence, 5 continuous',
    test='income test and assets test (family home exempt)', taper='income: 50c per AUD above AUD 178/fortnight (single); assets: AUD 3/fortnight per AUD 1,000 above AUD 268,000 (single homeowner)',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none (general revenue)',
    recipients_share=p(1712309, 2556017, 1), recipients_base='Age Pension recipients on the full rate, % of all Age Pension recipients (Services Australia-paid), 30 June 2020',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes (qualifying age 66 in 2020, 67 from July 2023)',
    source='DSS Demographics June 2020 (Payment by Rate); OECD PaG 2021 country profile', url=DSS + ' ; ' + PAG['AUS'], retrieved=RET, confidence='high (DSS); medium (PaG rules)',
    note='flat max = AUD 24,551.80/yr incl. Pension and Energy Supplements / AW AUD 90,861. DSS: 2,556,017 recipients; full 1,712,309; part 835,970 (income test 496,573, assets test 339,397); zero 4,397; manual 3,341; excludes DVA-paid. PaG: 67% full, 33% part (June 2020). Share of the population of pension age not computed (no ABS denominator fetched). Spending gap.')
add(iso3='AUS', scheme='Superannuation Guarantee', tier='mandatory private DC', financing='funded DC', legislated='legislated',
    rule='employer contribution to a private (mostly DC) fund; 9.5% of ordinary time earnings 2014-2021, +0.5 pp a year from July 2021 to 12% in July 2025; lump sum (51.6% of 2019-20 benefit payments) or income stream',
    flat_or_min_pctAW='', min_year='', qualifying='employees earning at least AUD 450 a month; access from preservation age 55-60',
    test='none', taper='', ceiling_contrib_pctAW=p(57090 * 4, AW['AUS'], 1), ceiling_benefit_pctAW='', contrib_rate='9.5 (employer)',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='',
    applies_to_2020_retirees='partly: SG began 1992, so 2020 retirees have at most 28 years of contributions at rates up to 9.5%',
    source='OECD PaG 2021 country profile', url=PAG['AUS'], retrieved=RET, confidence='medium',
    note='ceiling = maximum super contribution base AUD 57,090 per quarter (2020-21) x 4 / AW. Not public: SOCX public spending excludes it.')

# ---------------- AUT
add(iso3='AUT', scheme='Statutory pension insurance (ASVG/GSVG/BSVG, pension account)', tier='public earnings-related DB', financing='payroll PAYG plus federal budget transfer', legislated='legislated',
    rule='1.78% of each year\'s gross earnings credited to the pension account, valorised with wage growth; 80% after 45 years; 14 payments; pensions in payment indexed roughly to CPI',
    flat_or_min_pctAW='', min_year='', qualifying='180 months of contributions, 84 of them from employment; age 65 men, 60 women (rising 2024-2033)',
    test='none', taper='', ceiling_contrib_pctAW=p(75180, AW['AUT'], 1), ceiling_benefit_pctAW=p(75180, AW['AUT'], 1), contrib_rate='',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='',
    applies_to_2020_retirees='partly: account rule is the long-run formula; 2020 retirees are under transitional arrangements from the pre-2004 best-15-years, 2% accrual rules (PAR)',
    source='OECD PaG 2021; EU Pension Adequacy Report 2021 vol. II (Austria)', url=PAG['AUT'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='ceiling EUR 75,180/yr = EUR 5,370/month x 14. Federal budget share 2018: EUR 9.37 bn = 2.44% of GDP = 22% of statutory pension spending (PAR). Contribution rate not in the fetched sources (gap).')
add(iso3='AUT', scheme='Ausgleichszulage (equalisation supplement)', tier='minimum (pension- and income-tested top-up)', financing='general revenue (federal budget reimburses the insurers; seen in search results citing the Rechnungshof, not fetched)', legislated='legislated',
    rule='tops household income up to the reference rate (Richtsatz) EUR 966.65/month single, EUR 1,472.00 couple, 14 payments; 2020 bonus: single with 30 (40) contribution years at least EUR 1,080 (1,315)',
    flat_or_min_pctAW=p(966.65 * 14, AW['AUT'], 1), min_year='2020', qualifying='entitled to a statutory pension; habitual residence in Austria',
    test='gross pension plus other income of the household', taper='100% (differential)', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='',
    recipients_share=8.8, recipients_base='pensions with an Ausgleichszulage, % of all pensions in payment, December 2018 (6.2% of direct old-age pensions)',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
    source='PAR 2021 vol. II (citing Hauptverband 2019, p. 66); OECD PaG 2021; BMSGPK 2021 evaluation (hosted on readkong)', url=PAR + ' ; ' + PAG['AUT'] + ' ; ' + BMSGPK, retrieved=RET,
    confidence='medium (shares, 2018); low (stock counts via a secondary host)',
    note='Richtsatz x 14 / AW = 27.8%; 40-year bonus EUR 1,315 x 14 = 37.8% AW. Average supplement EUR 313/month (2018, PAR). Stock 205,306 in Dec 2019 and 198,749 in Jan 2020 (BMSGPK). The 2020 bonus cost EUR 51.0 m (BMSGPK). Total AZ spending 2019-2020 not found (gap). Year differs from target: 2018.')
add(iso3='AUT', scheme='Sozialhilfe / Mindestsicherung', tier='social assistance (not old-age specific)', financing='general revenue (Länder)', legislated='legislated',
    rule='means-tested minimum income EUR 917.35/month single, EUR 1,376.02 couple, 12 payments; own resources above EUR 4,586.75 used first; Sozialhilfe-Grundsatzgesetz in force since June 2019',
    flat_or_min_pctAW=p(917.35 * 12, AW['AUT'], 1), min_year='2020', qualifying='residence; no other resources', test='income and assets', taper='100%',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='', recipients_share='', recipients_base='', spending_pctGDP='', spending_year='',
    applies_to_2020_retirees='yes', source='OECD PaG 2021', url=PAG['AUT'], retrieved=RET, confidence='medium', note='Old people with a pension right get the Ausgleichszulage instead; recipients 65+ not found (gap).')
add(iso3='AUT', scheme='Abfertigung neu (severance pay fund)', tier='mandatory funded DC (severance; optional annuity)', financing='funded DC', legislated='legislated',
    rule='employer pays 1.53% of monthly gross pay into a staff provision fund; withdrawable on termination or kept until retirement',
    flat_or_min_pctAW='', min_year='', qualifying='employees since 2003', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='1.53 (employer)',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='partly (introduced 2003)',
    source='PAR 2021 vol. II (Austria)', url=PAR, retrieved=RET, confidence='medium', note='Mostly taken as a lump sum; not modelled by PaG.')

# ---------------- BEL
add(iso3='BEL', scheme='Employee pension (régime salarié / werknemersstelsel)', tier='public earnings-related DB', financing='payroll PAYG plus general taxes', legislated='legislated',
    rule='per career year: capped gross earnings revalued with prices x 60% (single) or 75% (household rate) / 45; indexed to the health index plus discretionary welfare adjustments',
    flat_or_min_pctAW='', min_year='', qualifying='no minimum period; full career 45 years; age 65 (66 in 2025, 67 in 2030)',
    test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW=p(59615.88, AW['BEL'], 1), contrib_rate='',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
    source='OECD PaG 2021; PAR 2021 vol. II (Belgium)', url=PAG['BEL'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='Benefit ceiling: PaG gives EUR 59,615.88 for 2019 wages (124.9% AW); PAR gives EUR 58,446.94 for 2019 (122.5% AW). Contribution rate and any contribution ceiling not in the fetched sources (gap). Self-employed scheme: same structure with a correction coefficient on net business income.')
add(iso3='BEL', scheme='Minimum pension (gewaarborgd minimumpensioen / pension minimum garantie)', tier='minimum (career-tested)', financing='payroll PAYG plus general taxes', legislated='legislated',
    rule='if higher than the earnings-related pension: EUR 15,500/yr from March 2020 (single rate), 25% higher at the household rate; pro rata career/45',
    flat_or_min_pctAW=p(15500, AW['BEL'], 1), min_year='2020 (from March)', qualifying='at least 2/3 of a full career (30 years) as employee or self-employed',
    test='none (career test only)', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='',
    recipients_share='', recipients_base='about 1 in 5 women and 1 in 20 men received a minimum pension, 2013',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
    source='OECD PaG 2021; PAR 2021 vol. II (citing Commissie Pensioenhervorming 2020-2040, 2014)', url=PAG['BEL'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='PAR states EUR 1,291.69/month gross (2020) for a 45-year career = EUR 15,500/yr. No share for 2019-2020 found (gap); year differs from target: 2013.')
add(iso3='BEL', scheme='Minimum right per career year (droit minimum par année de carrière)', tier='minimum (earnings floor in accrual)', financing='payroll PAYG plus general taxes', legislated='legislated',
    rule='a year\'s earnings below EUR 25,833.78 (from March 2020) are counted at that amount, unless the total pension exceeds EUR 16,434.94 (60% rate) or EUR 20,543.69 (75%)',
    flat_or_min_pctAW=p(25833.78, AW['BEL'], 1), min_year='2020 (from March)', qualifying='at least 1/3 of a full career (15 years) as employee',
    test='total pension ceiling', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='', recipients_share='', recipients_base='',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='OECD PaG 2021; PAR 2021 vol. II', url=PAG['BEL'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='flat_or_min_pctAW is the earnings floor credited per year (54.1% AW), not a benefit; its value in benefit terms is 60%/45 of that per year. Recipients gap.')
add(iso3='BEL', scheme='GRAPA / IGO (income guarantee for the elderly)', tier='targeted means-tested', financing='general revenue', legislated='legislated',
    rule='tops resources up to EUR 13,852.92/yr living alone, EUR 9,235.32 sharing a household (from March 2020); 90% of pension income counted; indexed to the health index',
    flat_or_min_pctAW=p(13852.92, AW['BEL'], 1), min_year='2020 (from March)', qualifying='age 65; residence',
    test='household resources; only 90% of pension income counted', taper='90% on pension income (100% on other means)', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='',
    recipients_share=4.9, recipients_base='pension recipients receiving the means-tested top-up, % of pension recipients, 2018',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='OECD PaG 2021; PAR 2021 vol. II (citing Coene 2020)', url=PAG['BEL'] + ' ; ' + PAR, retrieved=RET,
    confidence='medium', note='PAR gives the 2020 threshold as EUR 1,154.41/month (x12 = 13,852.92). Year differs from target: 2018. Spending gap. Financing by general revenue stated as social assistance, not verified in a budget source.')
add(iso3='BEL', scheme='Civil servants\' pension', tier='public DB (deferred pay)', financing='general taxes', legislated='legislated',
    rule='1/60 per year of the average wage of the last 10 career years; at most 75% of it and EUR 6,801.90/month gross (2020); follows public pay (perequation)',
    flat_or_min_pctAW='', min_year='', qualifying='statutory civil servants', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW=p(6801.90 * 12, AW['BEL'], 1),
    contrib_rate='', recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='PAR 2021 vol. II (Belgium)', url=PAR, retrieved=RET,
    confidence='medium', note='benefit cap EUR 6,801.90 x 12 / AW.')
add(iso3='BEL', scheme='Occupational pensions (second pillar)', tier='voluntary occupational, broad coverage by sector agreements', financing='funded (DC with guaranteed return, some DB)', legislated='collective agreement / employer',
    rule='organiser (employer or sector) sets the plan; legal minimum guaranteed return 1.75% since 2016; statutory plus occupational capped at 80% gross replacement',
    flat_or_min_pctAW='', min_year='', qualifying='membership compulsory once the plan exists', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='',
    contrib_rate='PaG modelling median: 1.3 (low earner), 3.3 (average), 6.1 (high earner)', recipients_share=75, recipients_base='employees and self-employed with an occupational pension, start of 2019',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='partly (accrual, payout linked to statutory pension since 2016)',
    source='PAR 2021 vol. II; OECD PaG 2021', url=PAR + ' ; ' + PAG['BEL'], retrieved=RET, confidence='medium', note='Recorded because coverage is broad through sector agreements; legally voluntary.')

# ---------------- CAN
add(iso3='CAN', scheme='Old Age Security (OAS) pension', tier='basic residence-based', financing='general revenue', legislated='legislated',
    rule='flat CAD 7,364.19 (2020), price-indexed; 1/40 per year of residence after 18; clawed back through the tax system',
    flat_or_min_pctAW=p(7364.19, AW['CAN'], 1), min_year='2020', qualifying='age 65; 40 years residence after 18 for full, at least 10 for partial',
    test='individual net income (clawback)', taper='15% of net income above CAD 79,054 (2020)', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share='', recipients_base='6,424,855 OAS pension benefits paid (month reported in the Jan-Mar 2020 quarterly report)',
    spending_pctGDP='', spending_year='2019-20', applies_to_2020_retirees='yes', source='OECD PaG 2021; ESDC quarterly report Jan-Mar 2020', url=PAG['CAN'] + ' ; ' + ESDC, retrieved=RET,
    confidence='high (ESDC); medium (PaG)', note='Clawback threshold = 138% AW. OAS amount paid CAD 3,724.3 m in the month. ESDC forecast 2019-20 expenditure OAS programme (OAS+GIS+Allowances) CAD 56.2 bn; % GDP not computed (no GDP fetched). General-revenue financing not stated in the fetched sources.')
add(iso3='CAN', scheme='Guaranteed Income Supplement (GIS)', tier='targeted income-tested', financing='general revenue', legislated='legislated',
    rule='monthly top-up for OAS pensioners with low income; maximum CAD 916.38/month single (Jan-Mar 2020), price-indexed; first CAD 5,000 of earnings exempt plus 50% of the next CAD 10,000',
    flat_or_min_pctAW=p(916.38 * 12, AW['CAN'], 1), min_year='2020 (Q1)', qualifying='OAS pensioner; income below CAD 18,600 (single, excluding OAS)',
    test='income other than OAS', taper='gap (not in the fetched sources)', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share=p(2077605, 6424855, 1), recipients_base='GIS benefits (2,077,605), % of OAS pension benefits (6,424,855), as reported in the Jan-Mar 2020 quarterly report',
    spending_pctGDP='', spending_year='2019-20', applies_to_2020_retirees='yes', source='ESDC quarterly report Jan-Mar 2020; OECD PaG 2021', url=ESDC + ' ; ' + PAG['CAN'], retrieved=RET,
    confidence='high', note='GIS paid CAD 1,070.0 m in the month (x12 = CAD 12.8 bn/yr, derived). OAS + GIS maximum single = (613.53+916.38) x 12 = 32.0% AW. PaG quotes OAS+GIS max CAD 17,757.63 for 2018.')
add(iso3='CAN', scheme='Allowance and Allowance for the Survivor', tier='targeted income-tested (ages 60-64)', financing='general revenue', legislated='legislated',
    rule='for low-income spouses/partners of GIS recipients and survivors aged 60-64; max CAD 1,165.16 and 1,388.92/month', flat_or_min_pctAW='', min_year='2020 (Q1)',
    qualifying='age 60-64; residence', test='couple income', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share='', recipients_base='72,254 benefits', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='ESDC quarterly report Jan-Mar 2020', url=ESDC, retrieved=RET,
    confidence='high', note='CAD 42.1 m paid in the month.')
add(iso3='CAN', scheme='Canada Pension Plan / Quebec Pension Plan', tier='public earnings-related DB', financing='payroll contributions (partially funded)', legislated='legislated',
    rule='25% of average YMPE-capped earnings (40 years, 17% drop-out; QPP 15%), revalued with wages, price-indexed; enhancement raises it to 33.33% and the ceiling by 14% (phase-in of contributions 2019-2025, full benefits 2065)',
    flat_or_min_pctAW='', min_year='', qualifying='contributions on earnings between CAD 3,500 and the YMPE; age 65 (60-70 with adjustment)',
    test='none', taper='', ceiling_contrib_pctAW=p(58700, AW['CAN'], 1), ceiling_benefit_pctAW=p(58700, AW['CAN'], 1),
    contrib_rate='CPP 5.25 employee + 5.25 employer (4.95 base + 0.30 enhancement); QPP 5.7 + 5.7; self-employed 10.5 / 11.4', recipients_share='', recipients_base='CPP retirement 5,361,695; QPP 1,932,625 benefits',
    spending_pctGDP='', spending_year='2019-20', applies_to_2020_retirees='partly: 2020 retirees get essentially the base 25% formula; enhancement accrues only from 2019',
    source='OECD PaG 2021; ESDC quarterly report Jan-Mar 2020', url=PAG['CAN'] + ' ; ' + ESDC, retrieved=RET, confidence='high',
    note='YMPE CAD 58,700 (2020). ESDC forecast 2019-20 expenditure: CPP CAD 50.1 bn, QPP 15.6 bn. "Partially funded" (CPP Investments) is not stated in the fetched sources. Occupational plans cover 37.5% of workers (2018, PaG): voluntary, not recorded as a row.')

# ---------------- CZE
add(iso3='CZE', scheme='Basic amount (základní výměra)', tier='basic flat (within the public PAYG pension)', financing='payroll PAYG', legislated='legislated',
    rule='flat 10% of the legislated average wage: CZK 3,490/month in 2020, paid with every old-age pension', flat_or_min_pctAW=p(41880, AW['CZE'], 1), min_year='2020',
    qualifying='entitlement to the pension: 35 years coverage (30 without credits), or 20 (15) years at 5 years above pension age', test='none', taper='',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='28 (whole pension insurance: 6.5 employee + 21.5 employer)',
    recipients_share=100, recipients_base='all old-age pensioners', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
    source='OECD PaG 2021; PAR 2021 vol. II (Czechia)', url=PAG['CZE'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='CZK 41,880/yr / AW CZK 402,261. Share of the basic amount in old-age pension spending not computed (needs the count of all old-age pensions incl. those paid with survivor\'s pensions).')
add(iso3='CZE', scheme='Percentage amount (procentní výměra)', tier='public earnings-related DB, progressive', financing='payroll PAYG', legislated='legislated',
    rule='1.5% per insured year of the reduced calculation base: personal average earnings counted 100% up to 44% of the legislated average wage, 26% between 44% and 400%, 0 above; indexed by prices plus half of real wage growth',
    flat_or_min_pctAW='', min_year='', qualifying='as basic amount', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='400 (of the legislated average wage)',
    contrib_rate='28 (6.5 employee + 21.5 employer)', recipients_share='', recipients_base='', spending_pctGDP=p(411284.6, GDP2020['CZE'], 2), spending_year='2020',
    applies_to_2020_retirees='yes; earnings measure covers years since 1986, extending toward lifetime',
    source='OECD PaG 2021; PAR 2021 vol. II; ČSSZ open data (vydaje-na-duchody-v-cr); Eurostat nama_10_gdp', url=PAG['CZE'] + ' ; ' + PAR + ' ; ' + CSSZ_X + ' ; ' + ES_GDP, retrieved=RET,
    confidence='high (spending); medium (rules)', note='spending = all old-age pensions (basic + percentage amount) CZK 411,284.6 m / GDP 2020 CZK 5,828,318 m; all pensions CZK 507,630.9 m = 8.71% GDP. Contribution ceiling not in fetched sources (gap).')
add(iso3='CZE', scheme='Minimum pension (minimum percentage amount)', tier='minimum', financing='payroll PAYG', legislated='legislated',
    rule='percentage amount at least CZK 770/month, so the minimum newly granted pension is CZK 4,260 (3,490 + 770)', flat_or_min_pctAW=p(4260 * 12, AW['CZE'], 1), min_year='2020',
    qualifying='entitlement to an old-age pension', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='',
    recipients_share=p(14904, 1811211, 2), recipients_base='old-age pensions below CZK 5,000/month, % of old-age pensions paid alone (not with a survivor\'s pension), Dec 2020; upper bound (band also holds partial pensions)',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='ČSSZ open data (vyplacene-duchody-dle-vyse); OECD PaG 2021', url=CSSZ_N + ' ; ' + PAG['CZE'], retrieved=RET,
    confidence='medium', note='14,904 of 1,811,211 pensions in the 1-4,999 CZK band.')
add(iso3='CZE', scheme='Living minimum (social assistance)', tier='social assistance', financing='general revenue', legislated='legislated',
    rule='living minimum CZK 3,860/month for an individual', flat_or_min_pctAW=p(3860 * 12, AW['CZE'], 1), min_year='2020', qualifying='residence', test='income', taper='',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='', recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
    source='OECD PaG 2021', url=PAG['CZE'], retrieved=RET, confidence='medium', note='Recipients 65+ gap. Voluntary personal pension schemes cover >50% of the population 0-65 but <1% of pensioners\' income (PAR); the funded opt-out pillar ran 2013-2015 only.')

# ---------------- DNK
add(iso3='DNK', scheme='Folkepension, basic amount (grundbeløb)', tier='basic residence-based', financing='general revenue', legislated='legislated',
    rule='DKK 77,028/yr (2020), wage-indexed (two-year lag); 40 years residence 15-pension age for full, pro rata otherwise',
    flat_or_min_pctAW=p(77028, AW['DNK'], 1), min_year='2020', qualifying='residence; pension age 66 (67 in 2022, 68 in 2030)',
    test='individual earnings from work', taper='30% of work income above DKK 336,900', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share=94.8, recipients_base='folkepension recipients (1,095,524), per mille of the same population group /10, January 2020',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='Statistics Denmark PEN122; OECD PaG 2021', url=DST + ' ; ' + PAG['DNK'], retrieved=RET,
    confidence='high', note='Average folkepension paid in January 2020: DKK 10,432/month. Earnings-test threshold = 77% AW. Spending gap.')
add(iso3='DNK', scheme='Folkepension, pension supplement (pensionstillæg)', tier='targeted means-tested', financing='general revenue', legislated='legislated',
    rule='full DKK 85,464/yr single, DKK 42,912 married/cohabiting; tested against all personal income except public pensions (ATP and occupational pensions count); work income up to DKK 122,004 disregarded',
    flat_or_min_pctAW=p(85464, AW['DNK'], 1), min_year='2020', qualifying='folkepension recipient', test='personal (couple) income excluding public pensions',
    taper='30.9% above DKK 88,700 (single); 16% of couple income above DKK 177,700 if both pensioners; 32% if partner not a pensioner',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share=p(630234, 1095524, 1), recipients_base='folkepension recipients with the full supplement, % of all folkepension recipients, January 2020 (reduced supplement 29.2%, none 10.5%, fractional pension 2.8%)',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='Statistics Denmark PEN122; OECD PaG 2021', url=DST + ' ; ' + PAG['DNK'], retrieved=RET,
    confidence='high', note='Counts: full 630,234; reduced 319,584; none 115,496; fractional 30,210 (classes exclude fractional pensions). Basic + full supplement single = 37.2% AW.')
add(iso3='DNK', scheme='Ældrecheck (supplementary pension benefit)', tier='targeted means-tested', financing='general revenue', legislated='legislated',
    rule='DKK 18,000/yr paid once a year to the poorest pensioners; liquid assets at most DKK 89,800', flat_or_min_pctAW=p(18000, AW['DNK'], 1), min_year='2020',
    qualifying='folkepension recipient', test='income and liquid assets', taper='gap', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='OECD PaG 2021', url=PAG['DNK'], retrieved=RET, confidence='medium',
    note='Recipients gap (Ældre Sagen, from a 30% sample of the DST pension register, reports 21% of folkepension recipients with ældrecheck and full supplement in 2020: secondary, not used).')
add(iso3='DNK', scheme='ATP (Labour Market Supplementary Pension)', tier='statutory funded (guaranteed deferred annuity)', financing='funded DC', legislated='legislated',
    rule='flat contribution by hours worked, DKK 3,408/yr for a full-time employee (2/3 employer, 1/3 employee); 80% buys guaranteed nominal annuity rights, 20% to reserves; bonuses when sound',
    flat_or_min_pctAW='', min_year='', qualifying='almost all employees and benefit recipients', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='',
    contrib_rate=f'flat DKK 3,408/yr ({p(3408, AW["DNK"], 2)}% of AW)', recipients_share=90, recipients_base='pensioners receiving an ATP payment, 2016',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='OECD PaG 2021; PAR 2021 vol. II (Denmark)', url=PAG['DNK'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='Contribution-proportional, so theta-like slope on hours, not on earnings. Year differs from target: 2016.')
add(iso3='DNK', scheme='Occupational pensions (labour market pensions)', tier='quasi-mandatory occupational DC', financing='funded DC', legislated='collective agreement',
    rule='contributions set by collective agreement, mostly life annuities; no intra- or intergenerational transfers', flat_or_min_pctAW='', min_year='',
    qualifying='employees under a collective agreement; all public sector workers', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='',
    contrib_rate='10-18 (PaG; PaG models 12); 12-18 (PAR)', recipients_share=90, recipients_base='employed workforce covered (PaG; the same text also gives about 85%)',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='partly: blue-collar schemes formed from the mid-1980s, so 2020 retirees have short occupational careers',
    source='OECD PaG 2021; PAR 2021 vol. II', url=PAG['DNK'] + ' ; ' + PAR, retrieved=RET, confidence='medium', note='Private; outside SOCX public cash spending.')

# ---------------- FIN
add(iso3='FIN', scheme='Earnings-related pensions (TyEL and other acts)', tier='statutory earnings-related DB, privately administered', financing='partially funded DB (private sector); PAYG (public sector)', legislated='legislated',
    rule='1.5% of annual earnings (1.7% at ages 53-62 in 2017-2025); valorisation 80% wages/20% prices; life-expectancy coefficient; in payment 20% wages/80% prices',
    flat_or_min_pctAW='', min_year='', qualifying='no waiting period; accrual from age 17', test='none', taper='', ceiling_contrib_pctAW='none', ceiling_benefit_pctAW='none',
    contrib_rate='24.4 (TyEL average 2020; employer 16.95, employee the rest)', recipients_share='', recipients_base='', spending_pctGDP='', spending_year='',
    applies_to_2020_retirees='partly: years 2005-2016 accrued at 1.5% (18-52), 1.9% (53-62), 4.5% (63-67)',
    source='OECD PaG 2021; PAR 2021 vol. II (Finland)', url=PAG['FIN'] + ' ; ' + PAR, retrieved=RET, confidence='medium', note='TyEL covers about 65% of the employed. Spending gap (ETK yearbook not fetched).')
add(iso3='FIN', scheme='National pension (kansaneläke)', tier='basic, pension-tested', financing='general revenue (Kela)', legislated='legislated',
    rule='full EUR 662.86/month single (2020), price-indexed; reduced by 50% of other pension income above EUR 56.04/month; nil above EUR 1,368.21 (single) / 1,226.13',
    flat_or_min_pctAW=p(662.86 * 12, AW['FIN'], 1), min_year='2020', qualifying='age 65; 40 years adult residence for full, pro rata',
    test='earnings-related and foreign pension income', taper='50%', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share=p(446885, POP65_2021['FIN'], 1), recipients_base='recipients aged 65+ of the national old-age pension, Dec 2020 (446,885), % of population 65+ on 1 Jan 2021 (Eurostat)',
    spending_pctGDP=p(1493.1, GDP2020['FIN'], 2), spending_year='2020', applies_to_2020_retirees='yes',
    source='Kela open data (pension benefits 2020); Eurostat demo_pjangroup, nama_10_gdp; OECD PaG 2021', url=KELA_P + ' ; ' + ES_POP + ' ; ' + ES_GDP + ' ; ' + PAG['FIN'], retrieved=RET,
    confidence='high', note='spending = old-age national pension paid 2020 (sum of monthly payments) EUR 1,493.1 m / GDP EUR 236,387 m; all Kela pensions EUR 2,228.9 m (0.94% GDP). All-age old-age national pension recipients 455,040.')
add(iso3='FIN', scheme='Guarantee pension (takuueläke)', tier='minimum, pension-tested', financing='general revenue (Kela)', legislated='legislated',
    rule='tops total pension income up to EUR 834.52/month; same for singles and couples', flat_or_min_pctAW=p(834.52 * 12, AW['FIN'], 1), min_year='2020',
    qualifying='resident in Finland receiving an old-age or disability pension', test='all pension income', taper='100%', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share=p(45077, POP65_2021['FIN'], 1), recipients_base='guarantee pension recipients aged 65+ (45,077), Dec 2020, % of population 65+ on 1 Jan 2021',
    spending_pctGDP=p(255.6, GDP2020['FIN'], 2), spending_year='2020', applies_to_2020_retirees='yes', source='Kela open data (guarantee pension); Eurostat; OECD PaG 2021',
    url=KELA_G + ' ; ' + ES_POP + ' ; ' + ES_GDP + ' ; ' + PAG['FIN'], retrieved=RET, confidence='high',
    note='All ages: 113,967 recipients Dec 2020 (most qualify through the national pension), EUR 255.6 m paid in 2020; the spending ratio covers all ages.')

# ---------------- FRA
add(iso3='FRA', scheme='Régime général (CNAV) and aligned schemes', tier='public earnings-related DB', financing='payroll PAYG', legislated='legislated',
    rule='50% x average of the 25 best years (price-revalued, capped at the PSS) x quarters/required quarters; décote 1.25% per missing quarter (max 25%); price-indexed',
    flat_or_min_pctAW='', min_year='', qualifying='full rate: 167 quarters (cohort 1958) from age 62, or age 67', test='none', taper='',
    ceiling_contrib_pctAW=p(41136, AW['FRA'], 1), ceiling_benefit_pctAW=p(41136, AW['FRA'], 1), contrib_rate='6.90 employee + 8.55 employer below the PSS; plus 0.40 + 1.90 on total pay (no rights)',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes (required quarters rising to 172 for cohorts from 1973)',
    source='OECD PaG 2021; PAR 2021 vol. II (France)', url=PAG['FRA'] + ' ; ' + PAR, retrieved=RET, confidence='medium', note='PSS EUR 41,136/yr (2020) = EUR 3,428/month. Spending gap.')
add(iso3='FRA', scheme='Minimum contributif (MiCo)', tier='minimum within the earnings-related scheme, pension-tested since 2012', financing='payroll PAYG', legislated='legislated',
    rule='base pension raised to EUR 7,746.02/yr (2021) for a full career, EUR 8,464.28 with at least 120 quarters contributed; pro rata to quarters; capped so that all own pensions stay below EUR 1,203.35/month (2021)',
    flat_or_min_pctAW=p(7746.02, AW['FRA'], 1), min_year='2021', qualifying='full-rate pension (by duration or age 67); all pensions claimed (subsidiarity)',
    test='total own direct pensions, all schemes', taper='100% above the ceiling (écrêtement)', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='',
    recipients_share=37, recipients_base='retirees with a direct right living in France receiving a minimum pension in any basic scheme (MiCo, minimum garanti, PMR), end 2020: 5.8 m, 4.0 m in their main scheme',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes, under post-2012 rules: 18% of new régime général pensions in 2020 and 2021 were raised to the MiCo (over 40% before 2012)',
    source='DREES, Les retraités et les retraites 2024, fiche 08 (EIR 2020, EACR); OECD PaG 2021', url=DREES08 + ' ; ' + PAG['FRA'], retrieved=RET, confidence='high',
    note='MiCo 2021 amount / 2020 AW = 20.3%; majoré 22.2%; ceiling 37.8% AW. Cohort 1953: 25% receive a minimum (34% women, 15% men). Spending gap. Amounts are 2021 (PaG) because PaG reports 2021 values.')
add(iso3='FRA', scheme='AGIRC-ARRCO', tier='mandatory occupational points', financing='payroll PAYG', legislated='collective agreement (affiliation compulsory by law)',
    rule='points = contributions / purchase price (EUR 17.3982 in 2020); pension = points x point value (EUR 1.2714 in 2020); uprating agreed by the social partners',
    flat_or_min_pctAW='', min_year='', qualifying='private and agricultural employees', test='none', taper='', ceiling_contrib_pctAW=p(329088, AW['FRA'], 1), ceiling_benefit_pctAW=p(329088, AW['FRA'], 1),
    contrib_rate='6.2 below the PSS, 17 between 1 and 8 PSS (rates generating points, PaG)', recipients_share='', recipients_base='',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes (AGIRC and ARRCO merged 2019)', source='OECD PaG 2021; PAR 2021 vol. II', url=PAG['FRA'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='Occupational schemes paid 24.5% of all pension entitlements of the obligatory schemes in 2018 (PAR). Public in SOCX (mandatory social security).')
add(iso3='FRA', scheme='Civil servants (SRE, CNRACL) incl. minimum garanti', tier='public DB', financing='employer and employee contributions, State budget', legislated='legislated',
    rule='75% of the salary of the last 6 months for a full career; minimum garanti pro rata to service', flat_or_min_pctAW='', min_year='',
    qualifying='civil servants', test='minimum garanti: no all-scheme ceiling yet (decree not issued)', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='',
    recipients_share='', recipients_base='minimum garanti paid to 4% of new State civil retirees and 25% of new CNRACL retirees, 2022',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='DREES 2024 fiche 08; PAR 2021 vol. II', url=DREES08 + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='Year differs from target: 2022 (flow). Financing details not in the fetched sources.')
add(iso3='FRA', scheme='ASPA / ASV (minimum vieillesse)', tier='targeted means-tested', financing='general revenue via the Fonds de solidarité vieillesse', legislated='legislated',
    rule='differential allowance up to EUR 903/month single (10,838/yr), EUR 1,402 couple, end 2020',
    flat_or_min_pctAW=p(10838, AW['FRA'], 1), min_year='2020 (end)', qualifying='age 65 (62 if unfit for work); residence', test='household resources', taper='100% (differential)',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share=p(635300, POP65_2021['FRA'], 1), recipients_base='ASPA + ASV recipients (635,300), end 2020, % of population 65+ on 1 Jan 2021 (Eurostat)',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='DREES press release 20/12/2021; DREES Les retraités et les retraites 2022, fiche 25; Eurostat',
    url=DREESPR + ' ; ' + DREES25 + ' ; ' + ES_POP, retrieved=RET, confidence='high',
    note='Average amounts end 2020: ASV EUR 419/month, ASPA EUR 476/month (DREES). Total spending gap. PaG gives 2021 ASPA EUR 10,881.75 single.')

# ---------------- DEU
add(iso3='DEU', scheme='Gesetzliche Rentenversicherung (statutory pension insurance)', tier='public earnings-related points', financing='payroll PAYG plus federal subsidy', legislated='legislated',
    rule='one point per year at the average earnings of contributors (EUR 40,551 in 2020); pension = points x pension value (EUR 410.28/yr, 2018); value indexed to gross wages with contribution and sustainability factors',
    flat_or_min_pctAW='', min_year='', qualifying='5 years of contributions; age 65 and 9-10 months (67 for cohorts from 1964)', test='none', taper='',
    ceiling_contrib_pctAW=p(82800, AW['DEU'], 1), ceiling_benefit_pctAW=p(82800, AW['DEU'], 1), contrib_rate='18.6 (9.3 employee + 9.3 employer)',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
    source='OECD PaG 2021; PAR 2021 vol. II (Germany)', url=PAG['DEU'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='Ceiling EUR 82,800 (West, 2020) = 158.9% of PaG AW, 204% of the contributors\' average earnings. Federal subsidy size not in the fetched sources. PAR: SPI pensions are 73% of older people\'s pension income, civil servants\' 15%.')
add(iso3='DEU', scheme='Grundrente (basic pension supplement)', tier='minimum top-up, income-tested', financing='general revenue', legislated='legislated',
    rule='points of low-earning years doubled up to 0.8 per year for at most 35 years (only months with at least 0.025 points); full if income <= EUR 1,250 single / 1,950 couple, reduced 60% above, nil above 1,600 / 2,300',
    flat_or_min_pctAW='', min_year='', qualifying='at least 33 years of compulsory contributions', test='income (incl. pensions, rent)', taper='60%',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='', recipients_share='', recipients_base='about 1.3 million expected in the first year, 70% women (PAR)',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='no: in force from January 2021 (then for stock and flow)',
    source='OECD PaG 2021; PAR 2021 vol. II', url=PAG['DEU'] + ' ; ' + PAR, retrieved=RET, confidence='medium', note='Not part of the 2020 rules.')
add(iso3='DEU', scheme='Grundsicherung im Alter (SGB XII ch. 4)', tier='social assistance for the old', financing='general revenue', legislated='legislated',
    rule='needs-based differential benefit (standard needs plus housing); average need EUR 9,732 per capita in 2019', flat_or_min_pctAW=p(9732, AW['DEU'], 1), min_year='2019',
    qualifying='at or above the age threshold (65 years 9 months in Dec 2020); residence', test='household income and assets', taper='100%',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share=p(564110, POP65_2021['DEU'], 1), recipients_base='recipients at or above the age threshold (564,110), Dec 2020, % of population 65+ on 1 Jan 2021 (Eurostat)',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='Destatis press release 188 of 14 April 2021; Eurostat; OECD PaG 2021', url=DESTATIS + ' ; ' + ES_POP + ' ; ' + PAG['DEU'], retrieved=RET,
    confidence='high', note='Dec 2019: 561,969. Destatis\'s own rate uses the population above the threshold, not 65+ (3.2% for 2020 per Statista, not verified). Spending gap.')
add(iso3='DEU', scheme='Beamtenversorgung (civil servants)', tier='public DB', financing='general revenue', legislated='legislated',
    rule='minimum pension (Mindestversorgung) 35% of pensionable pay after at least 5 years of service', flat_or_min_pctAW='', min_year='', qualifying='civil servants',
    test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none', recipients_share=8.8, recipients_base='civil servants receiving the minimum pension, 2020',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='PAR 2021 vol. II (Germany)', url=PAR, retrieved=RET, confidence='medium',
    note='Accrual rule not in the fetched sources. Occupational and Riester pensions are voluntary (not recorded).')

# ---------------- GRC
add(iso3='GRC', scheme='National pension (εθνική σύνταξη)', tier='basic, residence- and contribution-conditioned', financing='general revenue (State budget)', legislated='legislated (Law 4387/2016)',
    rule='EUR 384/month for 20 years of insurance and 40 years of residence; -2% per year below 20 (EUR 345.60 at 15); -1/40 per missing residence year; -6% per year if claimed at 62-67 with under 40 years',
    flat_or_min_pctAW=p(384 * 12, AW['GRC'], 1), min_year='2020', qualifying='15 years insurance and 15 years residence; age 67 (62 with 40 years)', test='none', taper='',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none', recipients_share='', recipients_base='',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes for pensions under Law 4387/2016 (from 2016-2017); older pensions were recalculated (details not in the fetched sources)',
    source='OECD PaG 2021; PAR 2021 vol. II (Greece)', url=PAG['GRC'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='384 x 12 / AW EUR 21,139 (assumes 12 payments). Recipients and spending gap (HELIOS/e-EFKA reports not fetched; HELIOS Sept 2020: 201,998 persons with disability main pensions = 8.1% of pensioners).')
add(iso3='GRC', scheme='Contributory (main) pension, e-EFKA', tier='public earnings-related DB', financing='payroll PAYG', legislated='legislated',
    rule='accrual 0.77% a year up to 15 years, rising to 2.55% for years 36-40, 0.5% beyond 40; pensionable earnings since 2002, CPI-valorised until 2024 then wages',
    flat_or_min_pctAW='', min_year='', qualifying='15 years (4,500 days); age 67, or 62 with 40 years', test='none', taper='',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW=p(6500 * 12, AW['GRC'], 1), contrib_rate='20 (regular rate cited for the self-employed, PaG); employee/employer split not in fetched sources',
    recipients_share='', recipients_base='', spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes (accrual rates for years 31-40 raised retroactively from Oct 2019)',
    source='OECD PaG 2021; PAR 2021 vol. II', url=PAG['GRC'] + ' ; ' + PAR, retrieved=RET, confidence='medium', note='Ceiling EUR 6,500/month x 12 / AW.')
add(iso3='GRC', scheme='Auxiliary (supplementary) pension (ex-ETEAEP, in e-EFKA)', tier='mandatory public supplementary', financing='PAYG (DB to 2014, NDC from 2015)', legislated='legislated',
    rule='0.45% of pensionable earnings per year of insurance up to 2014; NDC for insurance from 2015 (fully NDC for those first insured after 2014)', flat_or_min_pctAW='', min_year='',
    qualifying='same as the main pension', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='', recipients_share='', recipients_base='',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='partly: 2020 retirees get mostly the DB part', source='OECD PaG 2021; PAR 2021 vol. II', url=PAG['GRC'] + ' ; ' + PAR, retrieved=RET,
    confidence='medium', note='Not modelled by PaG. Self-employed not mandatorily covered. Also an NDC lump-sum benefit for some groups (PAR).')
add(iso3='GRC', scheme='Social solidarity allowance for uninsured elderly', tier='targeted means-tested', financing='general revenue', legislated='legislated',
    rule='allowance for uninsured persons over 67 not covered by a pension scheme, subject to conditions', flat_or_min_pctAW='', min_year='', qualifying='age 67+; uninsured; residence',
    test='means (conditions not detailed in the fetched sources)', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none', recipients_share='', recipients_base='',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='PAR 2021 vol. II (Greece)', url=PAR, retrieved=RET, confidence='medium', note='Amount and recipients gap.')

# ---------------- HUN
add(iso3='HUN', scheme='Old-age pension (öregségi nyugdíj)', tier='public earnings-related DB', financing='payroll PAYG', legislated='legislated',
    rule='43% of average valorised net earnings since 1988 for 15 years, +2%/yr for years 16-25, +1% for 26-36, +1.5% for 37-40, +2% beyond (80% at 40 years); progressive reduction of high earnings; CPI-indexed; 13th month phased in from 2021',
    flat_or_min_pctAW='', min_year='', qualifying='20 years service (15 for a partial pension); age 64.5 in 2020', test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='',
    contrib_rate='10 employee pension contribution + 15.5 employer social contribution tax (from July 2020; unified, not earmarked)',
    recipients_share=92, recipients_base='population above the standard retirement age receiving old-age benefits, January 2019',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='OECD PaG 2021; PAR 2021 vol. II (Hungary)', url=PAG['HUN'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='Earnings base is net of employee contributions and tax. PaG describes a single mandatory public tier; the former mandatory private pillar is not covered in the fetched sources. Year differs from target: 2019 (share).')
add(iso3='HUN', scheme='Minimum pension', tier='minimum', financing='payroll PAYG', legislated='legislated',
    rule='HUF 28,500/month, unchanged since January 2008', flat_or_min_pctAW=p(28500 * 12, AW['HUN'], 1), min_year='2020', qualifying='at least 20 years of service',
    test='none', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='', recipients_share='', recipients_base='"very rare" (PaG); not quantified',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='OECD PaG 2021', url=PAG['HUN'], retrieved=RET, confidence='medium',
    note='AW from PaG is rounded (HUF 5.0 million), so the % AW is approximate.')
add(iso3='HUN', scheme='Old-age allowance (időskorúak járadéka)', tier='social assistance for the old', financing='general revenue', legislated='legislated',
    rule='means-tested allowance for people at the standard retirement age without a sufficient pension', flat_or_min_pctAW='', min_year='', qualifying='standard retirement age',
    test='income', taper='', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none', recipients_share='', recipients_base='', spending_pctGDP='', spending_year='',
    applies_to_2020_retirees='yes', source='OECD PaG 2021', url=PAG['HUN'], retrieved=RET, confidence='medium', note='Amount and recipients gap.')

# ---------------- ISL
add(iso3='ISL', scheme='TR old-age pension (ellilífeyrir)', tier='basic, income-tested', financing='general revenue', legislated='legislated',
    rule='full ISK 3,081,468/yr (2020), 40 years residence 16-67 for full, pro rata (minimum 3); reduced by 45% of income above ISK 300,000/yr',
    flat_or_min_pctAW=p(3081468, AW['ISL'], 1), min_year='2020', qualifying='age 67; residence', test='income from all sources incl. occupational pensions (labour and capital)',
    taper='45%', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none',
    recipients_share='56.1 (age 67-69), 78.7 (70-74), 84.3 (75+)', recipients_base='old-age pension beneficiaries receiving TR (TR only or TR plus occupational), % of the age group, Dec 2020',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='Statistics Iceland FEL02000/FEL02001; OECD PaG 2021', url=HAG + ' ; ' + PAG['ISL'], retrieved=RET,
    confidence='high (Hagstofa); medium (PaG)',
    note='Counts 67+: TR only 1,277; TR + occupational 36,655; occupational only 10,131 (FEL02001 labels this third category wrongly as personal allowances; FEL02000 labels it occupational only). PaG text: withdrawal above "ISK 300 000 million or equivalent to 31% of AW" is inconsistent; ISK 300,000/yr = 3.2% AW. Financing: general revenue not stated in fetched sources. Spending gap.')
add(iso3='ISL', scheme='Household / pension supplement (heimilisuppbót)', tier='targeted income-tested', financing='general revenue', legislated='legislated',
    rule='max ISK 778,668/yr for a single person, withdrawn above ISK 300,000', flat_or_min_pctAW=p(778668, AW['ISL'], 1), min_year='2020', qualifying='TR pensioner living alone',
    test='income', taper='11.9%', ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none', recipients_share='', recipients_base='', spending_pctGDP='', spending_year='',
    applies_to_2020_retirees='yes', source='OECD PaG 2021', url=PAG['ISL'], retrieved=RET, confidence='medium', note='Recipients gap.')
add(iso3='ISL', scheme='Occupational pension funds (lífeyrissjóðir)', tier='mandatory occupational', financing='funded (DB/DC by fund)', legislated='legislated (terms by collective agreements)',
    rule='membership compulsory for workers aged 16-70; fund rules set benefits', flat_or_min_pctAW='', min_year='', qualifying='all working people', test='none', taper='',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='15.5 (4 employee + 11.5 employer)',
    recipients_share='96.0 (age 70-74), 96.5 (75+)', recipients_base='population receiving an occupational pension (alone or with TR), % of age group, Dec 2020',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='partly: the 15.5% rate is recent; earlier rates not in fetched sources',
    source='OECD PaG 2021; Statistics Iceland FEL02000', url=PAG['ISL'] + ' ; ' + HAG, retrieved=RET, confidence='medium', note='70-74: 76.7 both + 19.3 occupational only; 75+: 81.5 + 15.0. Private; outside SOCX public spending.')

# ---------------- IRL
add(iso3='IRL', scheme='State Pension (Contributory)', tier='basic contributory flat', financing='PRSI payroll PAYG through the Social Insurance Fund, Exchequer subvention for shortfalls', legislated='legislated',
    rule='flat EUR 248.30/week (2020), +EUR 10 at 80+, +EUR 14 living alone; reduced for incomplete records (yearly average, or total contributions approach with 40 years for full)',
    flat_or_min_pctAW=p(248.30 * 52, AW['IRL'], 1), min_year='2020', qualifying='age 66; at least 520 paid weekly contributions', test='none (no earnings test)', taper='',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='15.05 PRSI (4 employee + 11.05 employer), not earmarked to pensions',
    recipients_share=82, recipients_base='SPC recipients, % of SPC + SPNC recipients (526,078), 2019',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes (age 66 kept; rise to 67 repealed in late 2020)', source='OECD PaG 2021; PAR 2021 vol. II (Ireland)', url=PAG['IRL'] + ' ; ' + PAR, retrieved=RET,
    confidence='medium', note='Spending gap (DSP statistics on gov.ie not reachable). Year differs from target: 2019.')
add(iso3='IRL', scheme='State Pension (Non-Contributory)', tier='targeted means-tested', financing='general revenue', legislated='legislated',
    rule='max EUR 237/week single; means test with EUR 30 disregard and EUR 200 earnings disregard; capital above EUR 20,000 (excl. home) assessed by formula',
    flat_or_min_pctAW=p(237 * 52, AW['IRL'], 1), min_year='2020', qualifying='age 66; means', test='income and capital (excluding the home)', taper='gap (formula not in the fetched sources)',
    ceiling_contrib_pctAW='', ceiling_benefit_pctAW='', contrib_rate='none', recipients_share=18, recipients_base='SPNC recipients, % of SPC + SPNC recipients (526,078), 2019',
    spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes', source='OECD PaG 2021; PAR 2021 vol. II', url=PAG['IRL'] + ' ; ' + PAR, retrieved=RET, confidence='medium',
    note='18% = 100 - 82 (PAR). A parliamentary answer reported in search results gives 95,465 SPNC recipients at end 2020 (not verified). No mandatory private tier in 2020; occupational coverage just over half of employees (voluntary).')

COLS = ['iso3', 'scheme', 'tier', 'financing', 'legislated', 'rule', 'flat_or_min_pctAW', 'min_year', 'qualifying', 'test', 'taper',
        'ceiling_contrib_pctAW', 'ceiling_benefit_pctAW', 'contrib_rate', 'recipients_share', 'recipients_base', 'spending_pctGDP', 'spending_year',
        'applies_to_2020_retirees', 'source', 'url', 'retrieved', 'confidence', 'note']


def write(path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        f.write('# DRAFT, not wired into any stage (2026-10-30). Scheme rules for 13 OECD countries (set A). AW = PaG 2021 average worker earnings, 2020. Raw files: logs/thetaTau_raw/countriesA/. Read with comment="#".\n')
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            assert set(r) == set(COLS), set(COLS) ^ set(r)
            w.writerow(r)
    return len(rows)


def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--force', action = 'store_true', help = 'rebuild the csv even if it exists')
    p.add_argument('--out', default = None, help = 'write here instead of data/ (implies --force)')
    a = p.parse_args()
    out = os.path.abspath(a.out or OUT)
    if os.path.exists(out) and not (a.force or a.out):
        print('up to date: {} (--force to rebuild)'.format(out))
        return
    print(write(out), 'rows ->', out)


if __name__ == '__main__':
    main()
