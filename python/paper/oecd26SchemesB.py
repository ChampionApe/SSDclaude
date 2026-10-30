r""" Stage (0), DRAFT: scheme-by-scheme pension rules for the cross-section, countries B (ITA JPN LUX NLD
NZL NOR POL PRT ESP SWE CHE GBR USA): every mandatory tier, its financing, the minimum or targeted pensions and
their recipients. Not wired into build.py, REPLICATION.md, the tests or any calibration;
notes/data_thetaTau_countriesB.md reads it.

Run:  .venv\Scripts\python.exe -I python\paper\oecd26SchemesB.py [--force] [--out PATH]
      -> data/oecd26_pensionSchemes_B.csv (one row per scheme; first line a `#` comment, read with comment="#")

No network and no file input. The values were read by hand off the raw files in logs/thetaTau_raw/countriesB/
(retrieved 2026-10-30; their URLs in SOURCES.txt there and in each row's `url`) and sit in the rows below as
typed numbers; every percentage of AW or GDP is computed here from the amount and the denominator its `note`
names. main skips when the output exists unless --force; --out writes elsewhere, to check the committed csv
byte for byte.
"""
import os, csv, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'data', 'oecd26_pensionSchemes_B.csv')
RET = "2026-10-30"

# PaG 2021 country-profile average worker earnings (AW), national currency, 2020
AW = dict(ITA=30233, JPN=5.2e6, LUX=58040, NLD=54843, NZL=64150, NOR=627370, POL=60915,
          PRT=19478, ESP=26934, SWE=465767, CHE=87363, GBR=41807, USA=60220)
# GDP, national currency, millions: Eurostat nama_10_gdp CP_MNAC B1GQ (updated 2026-10-22); World Bank NY.GDP.MKTP.CN (lastupdated 2026-10-08)
GDP = {('ESP', 2020): 1129214.0, ('ITA', 2020): 1665979.4, ('LUX', 2020): 64499.2, ('NLD', 2020): 816463.0,
       ('POL', 2020): 2362909.0, ('PRT', 2020): 201032.7, ('SWE', 2018): 4777837.0, ('NOR', 2020): 3599226.0,
       ('CHE', 2020): 709854.6, ('GBR', 2019): 2252961.0, ('JPN', 2019): 571838000.0, ('JPN', 2020): 554074400.0,
       ('NZL', 2019): 323441.0, ('USA', 2020): 21375281.0}
POP65 = {('ITA', 2020): 13896348, ('JPN', 2019): 36253471, ('USA', 2020): 53290941, ('SWE', 2020): 2076899}  # World Bank SP.POP.65UP.TO

def paw(iso, annual):
    return round(100 * annual / AW[iso], 1)

def pgdp(iso, yr, mn):
    return round(100 * mn / GDP[(iso, yr)], 2)

PAG = "OECD Pensions at a Glance 2021 country profile"
def pagurl(ts, name):
    return f"https://web.archive.org/web/{ts}id_/https://www.oecd.org/els/public-pensions/PAG2021-country-profile-{name}.pdf"
T32 = "PaG 2021 Table 3.2 (StatLink https://stat.link/uxgr8v)"
GDPSRC = "GDP: Eurostat nama_10_gdp CP_MNAC (EU/EEA/CH) or World Bank NY.GDP.MKTP.CN (JPN NZL USA GBR)"
AWNOTE = "pctAW against PaG 2021 profile AW"

U = dict(
    ITA=pagurl("20230920204215", "Italy"), JPN=pagurl("20231204203244", "Japan"), LUX=pagurl("20231201233157", "Luxembourg"),
    NLD=pagurl("20231207105539", "Netherlands"), NZL=pagurl("20231208125756", "New-Zealand"), NOR=pagurl("20231208122227", "Norway"),
    POL=pagurl("20240517222803", "Poland"), PRT=pagurl("20231208114842", "Portugal"), ESP=pagurl("20240306190437", "Spain"),
    SWE=pagurl("20231202085132", "Sweden"), CHE=pagurl("20231201225602", "Switzerland"), GBR=pagurl("20231201221444", "United-Kingdom"),
    USA=pagurl("20231204063307", "United-States"))
INPS = "https://www.inps.it/content/dam/inps-site/pdf/dati-analisi-bilanci/rapporti-annuali/xx-rapporto-annuale/1374KEY-xx_rapporto_appendice.pdf"
SEGSOC = "https://www.seg-social.es/descarga/es/DICIEMBRE20GESTION"
MHLW_G = "https://www.mhlw.go.jp/content/000925808.pdf"
JPS_SK = "https://www.nenkin.go.jp/service/jukyu/seido/sonota-kyufu/shienkyufukin/oshirase.files/0110.pdf"
MHLW_SK = "https://www.mhlw.go.jp/content/12601000/000513054.pdf"
MHLW_PA = "https://www.mhlw.go.jp/content/12201000/000604185.pdf"
SVB = "https://zoek.officielebekendmakingen.nl/blg-981148.pdf"
AOWP = "https://zoek.officielebekendmakingen.nl/kst-35302-74.pdf"
MSD19 = "https://assets.retirement.govt.nz/public/Uploads/Retirement-Income-Policy-Review/2019-RRIP/Research-docs/MSD-Report-on-NZ-Retirement-Policies.pdf"
MSD22 = "https://assets.retirement.govt.nz/public/Uploads/Retirement-Income-Policy-Review/2022-RRIP/Description-of-New-Zealands-Current-Retirement-Income-Policies-MSD-for-2022-RRIP-.pdf"
NAV = "https://www.nav.no/_/attachment/download/ba80b626-55c1-4808-92fe-462141df3a8a:f0b2f182a09509a5b5b352c46a41e3edcb1b3ce2/Statistikknotat%20per%20desember%202020%20-%20alderspensjon%20v101.pdf"
NAV60 = "https://www.nav.no/_/attachment/download/85382651-1fb9-418f-9d04-10570a3f1b7a:3dcb9a4c68b46b92cf78444d95463a3794fd107f/2020_4kv_PST060_Alderspensjonister_med_minstepensjon._Kj%C3%B8nn_og_alder._Mnd_des_20.pdf"
REGJ = "https://www.regjeringen.no/no/dokumenter/arbeid-pensjon-og-inntekt-i-den-eldre-befolkningen/id2862999/"
ZUS = "https://www.zus.pl/documents/10182/39637/Struktura+wysoko%C5%9Bci+%C5%9Bwiadcze%C5%84+wyp%C5%82acanych+przez+ZUS+po+waloryzacji+w+marcu+2020+r.pdf/3df99481-587f-8efe-8f1f-a77871e4f8c8"
FORSAL = "https://forsal.pl/artykuly/1470186,malag-dotychczas-wyplacilismy-prawie-8-mld-zl-tzw-trzynastek-lacznie-wyplacimy-117-mld-zl.html"
SSPT = "https://sisscontent.seg-social.pt/documents/10152/113014/Seguranca_Social_em_numeros_2023_PT.pdf/628ae617-32d8-426d-ac5c-a3d39be1932d"
CFP = "https://www.cfp.pt/uploads/publicacoes_ficheiros/caixa-4-complemento-solidario-para-idosos.pdf"
UO11 = "https://www.regeringen.se/contentassets/c689564aa19c4d29bcebb1c037a2e37b/utgiftsomrade-11-ekonomisk-trygghet-vid-alderdom.pdf"
PMAR = "https://www.pensionsmyndigheten.se/content/dam/pensionsmyndigheten/blanketter---broschyrer---faktablad/publikationer/%C3%A5rsredovisningar/pensionsmyndighetens-%C3%A5rsredovisning/Pensionsmyndigheten-arsredovisning-2020.pdf"
ELS = "https://www.bfs.admin.ch/bfsstatic/dam/assets/17424585/master"
BSVT = "https://www.bsv.admin.ch/dam/de/sd-web/dP6W-ktRV5AA/Taschenstatistik_2022.pdf"
DWP = "https://assets.publishing.service.gov.uk/media/6050b444e90e075280ad694b/outturn-and-forecast-spring-statement-2021.xlsx"
RATES = "https://www.gov.uk/government/publications/benefit-and-pension-rates-2020-to-2021/benefit-and-pension-rates-2020-to-2021"
FR20 = "https://www.federalregister.gov/documents/2019/10/22/2019-22921/cost-of-living-increase-and-other-determinations-for-2020"
FR22 = "https://www.federalregister.gov/documents/2021/10/22/2021-23031/cost-of-living-increase-and-other-determinations-for-2022"
CRS = "https://www.everycrsreport.com/files/2020-02-20_IF10482_c0ff9f52d3984bbefe317c2a54e519ab7c88c40d.pdf"
LUXBT = "https://gouvernement.lu/dam-assets/documents/actualites/2022/04-avril/26-haagen-pensions/presentation-bilan-technique-2022-handout-20220422.pdf"
PAPERJAM = "https://paperjam.lu/article/complement-pension-minimum-bou"
ACLI = "https://static.acli.it/wp-content/uploads/PDF/ATLANTE-SOCIALE/4di8.pdf"
OCPI = "https://osservatoriocpi.unicatt.it/ocpi-pubblicazioni-quanto-costa-aumentare-le-pensioni-minime-a-mille-euro"

GBW = 365.25 / 7  # weeks per year for UK weekly rates
rows = []
def R(**k):
    k.setdefault('retrieved', RET)
    rows.append(k)

# ---------------- ITA
R(iso3='ITA', scheme='INPS earnings-related old-age pension (FPLD and other funds): DB/NDC pro rata', tier='public earnings-related (DB + NDC)',
  financing='payroll PAYG (INPS funds)', legislated='legislated',
  rule='NDC: contributions 33% of earnings capitalised at 5-yr average nominal GDP growth, annuitised with age-specific transformation coefficients (17.937 divisor = 5.575% at 67 in 2021); DB part for pre-1996 seniority (PaG: pro rata DB and NDC); pensions in payment indexed 100% of CPI up to 3x minimum, falling to 40% above 9x minimum',
  qualifying='age 67 with 20 contribution years (2020); NDC-only pensions also need pension >= 1.5x 2012 assegno sociale',
  ceiling_contrib_pctAW=paw('ITA', 103055), ceiling_benefit_pctAW=paw('ITA', 103055), contrib_rate='33% (about 1/3 employee, 2/3 employer)',
  spending_pctGDP=pgdp('ITA', 2020, 269055), spending_year=2020,
  applies_to_2020_retirees='2020 retirees are mixed DB/NDC; NDC-only for entrants after 1995 (PaG Table 3.1 panel B: DB + NDC with minimum)',
  source=f'{PAG}; INPS XX Rapporto annuale, appendice statistica, Tabella 2.6 (uscite 2020)', url=f'{U["ITA"]} ; {INPS}', confidence='medium',
  note='Ceiling: maximum earnings for benefits EUR 103 055 (new scheme, 2020). Spending = INPS "Pensioni a carico dei Fondi" EUR 269 055 mn 2020 (all INPS-paid contributory pensions, incl. public employees; table columns partly misaligned in pdftotext, value checked against labels) / Eurostat GDP. ' + AWNOTE)
R(iso3='ITA', scheme='Integrazione al trattamento minimo (minimum pension supplement)', tier='minimum pension top-up (contributory)',
  financing='INPS (split between contributions and general revenue not collected)', legislated='legislated',
  rule='tops contributory DB/mixed pensions up to the minimum EUR 515.58/month x 13 = EUR 6 702.54/yr (2020); not available for pure NDC pensions',
  flat_or_min_pctAW=paw('ITA', 6702.54), min_year=2020, qualifying='contributory pension liquidated under DB or mixed rules',
  test='income test (personal and couple income); thresholds not collected', taper='not collected',
  recipients_share='32 (PaG 2018, % of 65+); 3 181 525 integrated pensions in 2016 (INPS via ACLI)', recipients_base='PaG: population 65+; ACLI: number of pensions (not persons)',
  spending_pctGDP='', spending_year='',
  applies_to_2020_retirees='yes for DB/mixed pensions (all 2020 retirees with pre-1996 seniority); no for NDC-only careers (post-1995 entrants) -> disappears in steady state',
  source=f'{PAG}; {T32}; ACLI Atlante sociale (INPS data, 2016); OCPI Univ. Cattolica 2022', url=f'{U["ITA"]} ; https://stat.link/uxgr8v ; {ACLI} ; {OCPI}', confidence='low',
  note='GAP: no 2019-2020 official count or spending found. ACLI (secondary, read via search snippet, file not downloaded): 3 181 525 integrated pensions and EUR 8.83 bn cost in 2016 (3 856 033 in 2011). OCPI (secondary, INPS 2020 data): 2.1 mn pensioners with total pension income <= minimum, spending on minimum pensions about EUR 8.1 bn in 2020 (= 0.49% of GDP) -- a different concept (pensioners at/below the minimum, not supplements paid). PaG Table 3.2 minimum level 22.7% AW vs 22.2% computed here. ' + AWNOTE)
R(iso3='ITA', scheme='Assegno sociale / pensione sociale (social allowance)', tier='targeted (means-tested, non-contributory)',
  financing='general revenue (State, via INPS GIAS)', legislated='legislated',
  rule='EUR 459.83/month x 13 = EUR 5 977.79/yr single (2020); maggiorazione up to EUR 191.68/month at 70+ (total EUR 8 469.63/yr)',
  flat_or_min_pctAW=paw('ITA', 5977.79), min_year=2020, qualifying='age 67 (rising with life expectancy); 10 years legal residence',
  test='means test (detail not collected)', taper='not collected',
  recipients_share=round(100 * 803441 / POP65[('ITA', 2020)], 1), recipients_base='population 65+ (World Bank 2020); 803 441 pensioni/assegni sociali in force 31.12.2020',
  spending_pctGDP=pgdp('ITA', 2020, 4938), spending_year=2020, applies_to_2020_retirees='yes',
  source=f'{PAG}; INPS XX Rapporto annuale appendice, Tabella 2.6 and pension-count table (vigenti 31.12.2020)', url=f'{U["ITA"]} ; {INPS}', confidence='high',
  note='Spending EUR 4 938 mn 2020 ("Assegni sociali e pensioni sociali interamente a carico dello Stato"); = 1.8% of INPS fund pensions. With maggiorazione: ' + f'{paw("ITA", 8469.63)}% AW. PaG Table 3.2: targeted 19.8% AW, recipients 6.6% of 65+ (2018). ' + AWNOTE)
R(iso3='ITA', scheme='TFR (trattamento di fine rapporto, severance pay)', tier='mandatory deferred wage (not a pension)', financing='book reserve (employer); funded if transferred to a pension fund',
  legislated='legislated', rule='6.91% of gross salary accrued per year, revalued at 1.5% + 75% of CPI growth, paid as lump sum at end of employment',
  contrib_rate='6.91% (employer)', applies_to_2020_retirees='yes', source=PAG, url=U['ITA'], confidence='medium',
  note='Not counted as a mandatory pension by PaG; supplementary (closed collective and open) pension funds are voluntary with low enrolment and are left out.')

# ---------------- JPN
R(iso3='JPN', scheme='National Pension (Kokumin Nenkin) basic old-age pension', tier='contribution-based basic (flat)',
  financing='flat contributions (Category 1), EPI transfers and general revenue (shares not in collected sources)', legislated='legislated',
  rule='full basic pension JPY 781 700/yr (2020) for 40 contribution years, pro rata for shorter; indexed to net wages to 67, prices after',
  flat_or_min_pctAW=15.08, min_year=2020, qualifying='10 contribution years; residents 20-59 covered; Category 3 dependent spouses credited',
  spending_pctGDP=pgdp('JPN', 2020, 24.3212e6), spending_year='FY2020 (stock of annual amounts at end-March 2021)',
  recipients_share=91.8, recipients_base='PaG Table 3.2, % of 65+ (2018)', applies_to_2020_retirees='yes',
  source=f'{PAG}; MHLW Annual overview of EPI and NP FY2020 (Table 2); {T32}', url=f'{U["JPN"]} ; {MHLW_G}', confidence='high',
  note='pctAW = PaG Table 3.2 value (AW JPY 5.2 mn rounded in profile). Spending = NP total annual benefit amount JPY 243 212 oku (100 mn) at end FY2020 / WB CY2020 GDP; includes basic pensions of former employees.')
R(iso3='JPN', scheme="Employees' Pension Insurance (Kosei Nenkin) earnings-related", tier='public earnings-related (DB)', financing='payroll PAYG',
  legislated='legislated', rule='0.5481% x average monthly remuneration incl. bonuses x months from April 2003 (+0.7125% excl. bonuses for months before); indexed to net wages to 67, prices after',
  qualifying='entitlement to the basic pension; 1 month of contributions', ceiling_contrib_pctAW=round(100 * 650000 * 12 / 5.2e6), ceiling_benefit_pctAW=round(100 * 650000 * 12 / 5.2e6),
  contrib_rate='18.3% (half employer)', spending_pctGDP=pgdp('JPN', 2020, 31.6866e6), spending_year='FY2020 (stock of annual amounts)', applies_to_2020_retirees='yes; specially provided pension from 63 (men)/61 (women) being phased out',
  source=f'{PAG}; MHLW Annual overview FY2020 (Table 2)', url=f'{U["JPN"]} ; {MHLW_G}', confidence='high',
  note='Ceiling JPY 650 000/month standard remuneration (= 150% of AW JPY 5.2 mn, approximate; bonus ceiling not collected). Spending JPY 316 866 oku incl. mutual-aid (Categories 2-4, 61 151 oku). Employees pension funds (contracting out) cover about 0.3% of employees; corporate DB/DC are voluntary and left out.')
R(iso3='JPN', scheme='Pension Supplementary Benefit for low-income pensioners (Nenkin seikatsusha shien kyufukin), old-age and supplementary old-age', tier='targeted top-up (income-tested, paid on top of basic pension)',
  financing='general revenue (national treasury, 100%)', legislated='legislated (from October 2019)',
  rule='JPY 5 000/month x paid-up months/480 (FY2019 base, price-indexed) + about JPY 10 800 x exempt months/480; supplementary benefit tapers for income above the threshold',
  flat_or_min_pctAW=paw('JPN', 60000), min_year=2019, qualifying='65+, basic pension recipient, whole household exempt from municipal tax',
  test='prior-year public pension + other income <= JPY 779 300 (full basic pension, FY2019); supplementary benefit up to JPY 879 300', taper='supplementary benefit decreases with income (rate not stated)',
  recipients_share=round(100 * (4394817 + 875173) / POP65[('JPN', 2019)], 1), recipients_base='population 65+ (World Bank 2019); 4 394 817 old-age + 875 173 supplementary old-age payments, first payment 13 Dec 2019',
  spending_pctGDP=pgdp('JPN', 2019, (34785.114926 + 3705.898113) * 6), spending_year='2019 (first two-month payment x 6)', applies_to_2020_retirees='yes',
  source='MHLW outline of the benefit; Japan Pension Service, first payment results (Dec 2019)', url=f'{MHLW_SK} ; {JPS_SK}', confidence='high',
  note='Average monthly old-age benefit JPY 3 962, supplementary JPY 2 118. Annualised JPY 231 bn = 0.41% of public pension annual amount. Budget target 9.7 mn recipients incl. disability/survivors. Not in PaG Table 3.2.')
R(iso3='JPN', scheme='Public assistance (Seikatsu hogo) for the elderly', tier='social assistance', financing='general revenue (not verified)', legislated='legislated',
  rule='minimum cost-of-living standard JPY 935 800/yr for a 65-69 year-old in Tokyo (from Oct 2020, excl. housing and medical aid)', flat_or_min_pctAW=paw('JPN', 935800), min_year=2020,
  qualifying='all residents after using assets, abilities and other benefits', test='income and assets (household)', taper='100%',
  recipients_share=round(100 * 2071747 * 0.491 / POP65[('JPN', 2019)], 1), recipients_base='population 65+ (World Bank 2019); 49.1% of 2 071 747 recipients aged 65+ (Nov 2019); protection rate 65+ = 2.93% (FY2017)',
  applies_to_2020_retirees='yes', source=f'{PAG}; MHLW reference material on public assistance (2020)', url=f'{U["JPN"]} ; {MHLW_PA}', confidence='high',
  note='PaG Table 3.2: targeted 18% AW, recipients 3% of 65+. Spending on elderly recipients not collected.')

# ---------------- LUX
R(iso3='LUX', scheme='General pension insurance (CNAP): proportional increments (majorations proportionnelles)', tier='public earnings-related (DB)', financing='payroll PAYG + State share, surpluses to the reserve fund (FDC)',
  legislated='legislated', rule='1.800% of total revalued career earnings (2020), +0.013 pp per year that age + contribution years exceed 94, max 2.05%; indexed to prices plus real-wage adjustment',
  qualifying='age 65 with 120 months of contributions', ceiling_benefit_pctAW=paw('LUX', 8762.81 * 12), contrib_rate='24% global rate (bilan technique); 16% paid 8% employee + 8% employer (PaG), so 8% State (inferred)',
  spending_pctGDP=pgdp('LUX', 2020, 5358), spending_year=2020, applies_to_2020_retirees='yes',
  source=f'{PAG}; Ministry of Social Security, Bilan technique du regime general 2022 (handout)', url=f'{U["LUX"]} ; {LUXBT}', confidence='high',
  note='Benefit ceiling = maximum pension EUR 8 762.81/month (25/6 of reference amount). Contribution ceiling (5x social minimum wage) not in collected sources. Spending = current expenditure of the whole general scheme EUR 5 358 mn 2020 (all benefits, 194 441 pensions, 461 345 insured). Civil-servant special schemes not covered.')
R(iso3='LUX', scheme='General pension insurance: flat increments (majorations forfaitaires) and end-of-year allowance', tier='contribution-based basic (flat)', financing='payroll PAYG + state (as above)',
  legislated='legislated', rule='EUR 513.15/month for 40 years (24.4% of reference amount EUR 2 103.07) + end-of-year allowance EUR 67.38/month, pro rata for shorter careers',
  flat_or_min_pctAW=paw('LUX', (513.15 + 67.38) * 12), min_year=2020, qualifying='pro rata per insurance year (40 years for full)', applies_to_2020_retirees='yes',
  source=f'{PAG}; {T32}', url=U['LUX'], confidence='high', note=f'Without end-of-year allowance {paw("LUX", 513.15 * 12)}% AW. PaG Table 3.2 contribution-based basic 12.0% AW, recipients 114.6% of 65+. Spending included in the row above. ' + AWNOTE)
R(iso3='LUX', scheme='Minimum pension (pension minimum personnelle, complement)', tier='minimum pension top-up (contributory)', financing='payroll PAYG + state (CNAP)', legislated='legislated',
  rule='EUR 1 892.77/month (90% of reference amount) for 40 years of contributory and non-contributory periods, pro rata down to 20 years',
  flat_or_min_pctAW=paw('LUX', 1892.77 * 12), min_year=2020, qualifying='20 years (pro rata), 40 for full', test='none (career-based top-up)',
  recipients_share='16.4 (2023); 19.5 (2009)', recipients_base='share of general-scheme pensions receiving the minimum-pension complement (36 014 pensions in 2023)',
  spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
  source=f'{PAG}; Paperjam citing Ministry of Social Security and CNAP', url=f'{U["LUX"]} ; {PAPERJAM}', confidence='low',
  note='GAP: 2019-2020 count not found (IGSS Rapport general not retrieved). Cost EUR 132.3 mn in 2023 (outside window; no 2023 GDP collected). PaG Table 3.2 minimum 39.1% AW, recipients not reported.')
R(iso3='LUX', scheme='REVIS (revenu d inclusion sociale) social assistance', tier='social assistance', financing='general revenue (not verified)', legislated='legislated',
  rule='EUR 1 502.92/month single, EUR 2 254.38 two adults (2020)', flat_or_min_pctAW=paw('LUX', 1502.92 * 12), min_year=2020, qualifying='age 25, legal residence',
  test='household means test', taper='not collected', applies_to_2020_retirees='yes', source=f'{PAG}; {T32}', url=U['LUX'], confidence='medium',
  note='PaG Table 3.2 targeted 31.1% AW; recipients 65+ not reported. ' + AWNOTE)

# ---------------- NLD
R(iso3='NLD', scheme='AOW (Algemene Ouderdomswet) state pension', tier='residence-based basic (flat)', financing='payroll tax (AOW premium); general-revenue contribution not collected', legislated='legislated',
  rule='EUR 1 230.24/month single + holiday allowance EUR 72.04 (EUR 1 302.28) in 2020, linked to net minimum wage; accrues 2% of the full value per year of residence or work in NL',
  flat_or_min_pctAW=paw('NLD', 1302.28 * 12), min_year=2020, qualifying='residence (50 years for full), AOW age 66y4m (2020)',
  ceiling_contrib_pctAW=paw('NLD', 34712), contrib_rate='17.90% AOW premium on taxable income up to EUR 34 712 (2020)',
  recipients_share=104.1, recipients_base='PaG Table 3.2, % of 65+ (2018); 3 514 736 AOW clients 2020 (SVB)',
  spending_pctGDP=pgdp('NLD', 2020, 41235), spending_year=2020, applies_to_2020_retirees='yes',
  source=f'{PAG}; SVB Jaarverslag 2020 (Kerncijfers); Tweede Kamer kst-35302-74 (AOW premium)', url=f'{U["NLD"]} ; {SVB} ; {AOWP}', confidence='high',
  note='PaG Table 3.2 residence-based basic 29.2% AW vs 28.5% computed (holiday allowance included). AOW premium rate and ceiling read from search snippet of kst-35302-74 (file not downloaded): medium. Couple EUR 1 770.76/month. ' + AWNOTE)
R(iso3='NLD', scheme='AIO (aanvullende inkomensvoorziening ouderen)', tier='social assistance (top-up of incomplete AOW)', financing='general revenue (not verified)', legislated='legislated',
  rule='supplements AOW and other income up to the social-assistance (net AOW) level for people with incomplete residence record', qualifying='AOW age, incomplete AOW, low income and assets',
  test='income and assets (household)', taper='100%', recipients_share=round(100 * 50930 / 3514736, 2), recipients_base='AIO households (50 930) / AOW clients (3 514 736), 2020',
  spending_pctGDP=pgdp('NLD', 2020, 330), spending_year=2020, applies_to_2020_retirees='yes', source='SVB Jaarverslag 2020 (Kerncijfers)', url=SVB, confidence='high',
  note='AIO benefit expenditure EUR 330 mn 2020 (EUR 307 mn 2019); = 0.8% of AOW. Kerncijfers table rows realigned by hand (labels vs values offset in pdftotext).')
R(iso3='NLD', scheme='Occupational pension funds (industry-wide and company)', tier='quasi-mandatory private DB (collective agreements)',
  financing='funded DB (mostly career-average); DC growing', legislated='collective agreement',
  rule='career-average DB, max accrual 1.875% per year on earnings above a franchise (AOW offset) up to EUR 110 111 (2020); target ~70% of pay including AOW; indexation conditional',
  ceiling_contrib_pctAW=paw('NLD', 110111), ceiling_benefit_pctAW=paw('NLD', 110111), recipients_share='about 90 (coverage of employees)', recipients_base='employees covered (89% DB, rest DC; 2020)',
  applies_to_2020_retirees='yes', source=PAG, url=U['NLD'], confidence='medium',
  note='Contribution rates and benefit spending not collected here (pension-fund statistics are collected by the other agent).')

# ---------------- NZL
R(iso3='NZL', scheme='New Zealand Superannuation (NZS) and Veterans Pension', tier='residence-based basic (flat)', financing='general revenue', legislated='legislated',
  rule='single living alone NZD 490.73/week gross (2020/21) = NZD 25 517.96/yr; CPI-indexed with net couple rate kept between 66% and 72.5% of net average wage',
  flat_or_min_pctAW=paw('NZL', 25517.96), min_year=2020, qualifying='age 65, 10 years residence since 20 incl. 5 after 50', test='none (overseas pensions deducted)',
  contrib_rate='none (no social security contributions)', recipients_share=104.6, recipients_base='PaG Table 3.2, % of 65+ (2018); 761 508 NZS + 13 231 non-qualified partners, end-March 2019 (MSD)',
  spending_pctGDP=pgdp('NZL', 2019, 15273.021), spending_year='year ended March 2020', applies_to_2020_retirees='yes',
  source=f'{PAG}; MSD Description of current retirement income policies (2019 and 2022 RRIP), Tables 1 and 7', url=f'{U["NZL"]} ; {MSD19} ; {MSD22}', confidence='high',
  note='Spending NZD 15 273 mn before tax (+ Veterans Pension NZD 147 mn) / WB calendar-2019 GDP (fiscal-year mismatch). NZS is taxable. Brief: PaG Table 4.1 low earner for NZL is 0.6 AW.')
R(iso3='NZL', scheme='Supplementary assistance to people 65+ (Accommodation Supplement, Temporary Additional Support, Disability Allowance)', tier='targeted (income- and asset-tested supplements)',
  financing='general revenue', legislated='legislated', rule='Accommodation Supplement pays 70% of housing costs above a threshold (NZD 106/week single renter, Nov 2020) up to regional limits; Winter Energy Payment is universal for NZS recipients',
  test='income and assets', taper='not collected', recipients_share=19.2, recipients_base='% of 65+ receiving any supplementary assistance, end-March 2019 (147 853); Accommodation Supplement 5.8%, TAS 0.9%, Disability Allowance 16.9%',
  spending_pctGDP=pgdp('NZL', 2019, 362.333), spending_year='year ended March 2019', applies_to_2020_retirees='yes',
  source='MSD Description of current retirement income policies (2019 RRIP), Tables 9-11', url=MSD19, confidence='high',
  note='Spending = supplementary assistance paid to NZS recipients NZD 362.3 mn (YE March 2019) / WB CY2019 GDP; = 2.5% of NZS spending. PaG: no targeted benefit on top of a full NZS (main-benefit 65+ recipients: 5 601).')
R(iso3='NZL', scheme='KiwiSaver', tier='voluntary DC with auto-enrolment of new employees (opt-out); not mandatory', financing='funded DC + government contribution', legislated='legislated (voluntary)',
  rule='default 6% of earnings (3% employee, 3% employer); government subsidy up to NZD 521/yr; lump sum at 65', contrib_rate='6% default', recipients_share='3 026 000 members (March 2020)', recipients_base='members',
  applies_to_2020_retirees='no (small balances; 22 700 aged out in year to March 2020, average NZD 58 700)', source=PAG, url=U['NZL'], confidence='medium', note='Recorded for completeness; PaG classes it voluntary.')

# ---------------- NOR
R(iso3='NOR', scheme='Folketrygden old-age pension, old rules (ch. 19): basic pension + supplementary pension (tilleggspensjon)', tier='public earnings-related (DB points) + basic',
  financing='general NI contributions (PaG lists rates; earmarking and budget share not verified)', legislated='legislated',
  rule='basic pension plus income-related supplementary pension (tilleggspensjon), with flexible withdrawal 62-75 and life-expectancy adjustment since 2011; minimum pension level offsets supplementary pension krone for krone',
  contrib_rate='NI contribution 8.2% employee; employer 0-14.1% by region (avg 13%)', spending_pctGDP=pgdp('NOR', 2020, 241000), spending_year=2020,
  applies_to_2020_retirees='yes: cohorts born <=1953 fully, 1954-1962 partly (combined rules); PaG Table 3.1 panel B: DB + basic + targeted + FDC',
  source=f'{PAG}; NAV Statistikknotat alderspensjon des. 2020; regjeringen.no report Arbeid, pensjon og inntekt i den eldre befolkningen', url=f'{U["NOR"]} ; {NAV} ; {REGJ}', confidence='medium',
  note='Spending = all folketrygd old-age pensions NOK 241 bn 2020 (quoted in regjeringen.no report; page 403 to direct fetch, read via search snippet) / Eurostat total GDP (mainland GDP would give a higher ratio). 981 448 old-age pensioners Dec 2020, average NOK 248 000/yr. Point accrual rates and ceilings for ch. 19 not in collected sources.')
R(iso3='NOR', scheme='Folketrygden income pension, new rules (ch. 20)', tier='public earnings-related (NDC-like)', financing='as above', legislated='legislated',
  rule='18.1% of pensionable income credited up to 7.1G, revalued with wages, annuitised by cohort life-expectancy divisor; indexed to wages minus 0.75% (from 2021: average of wage and price growth)',
  ceiling_contrib_pctAW=paw('NOR', 7.1 * 100853), ceiling_benefit_pctAW=paw('NOR', 7.1 * 100853), applies_to_2020_retirees='partly (cohorts 1954-1962 pro rata); fully from cohort 1963',
  source=PAG, url=U['NOR'], confidence='medium', note='G = NOK 100 853 (2020 average); NI contributions are levied on all earnings, so contributions are uncapped while accrual stops at 7.1G (contribution ceiling left blank).')
R(iso3='NOR', scheme='Minimum pension level (minste pensjonsnivå, old rules) and guarantee pension (garantipensjon, new rules)', tier='targeted/minimum (pension-tested)', financing='general revenue (within folketrygd)', legislated='legislated',
  rule='minimum pension level single NOK 204 066 (2020 avg); guarantee pension single NOK 191 539 (full with 40 years residence, pro rata); wage-indexed adjusted for life expectancy',
  flat_or_min_pctAW=paw('NOR', 204066), min_year=2020, qualifying='residence 5 years between 16 and 66 (guarantee), 40 for full', test='pension test against earnings-related pension',
  taper='old rules 100% against supplementary pension; new rules 80% against income pension', recipients_share=round(100 * 138247 / 981448, 1), recipients_base='old-age pensioners with minimum pension, Dec 2020 (138 247 of 981 448; women 23.5%)',
  spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes (minimum pension level for old-rule cohorts; guarantee pension phases in from cohort 1954)',
  source=f'{PAG}; NAV PST060 Alderspensjonister med minstepensjon, des. 2020; NAV Statistikknotat des. 2020', url=f'{U["NOR"]} ; {NAV60} ; {NAV}', confidence='high',
  note=f'Guarantee pension {paw("NOR", 191539)}% AW (PaG Table 3.2 targeted 30.5). Residence-based basic in PaG Table 3.2: 15.4% AW, recipients 103.3% of 65+. Spending on the minimum top-up not collected. NAV notes a corrected series from Sept 2020.')
R(iso3='NOR', scheme='Mandatory occupational pension (OTP)', tier='mandatory private DC', financing='funded DC (employer)', legislated='legislated (2006)',
  rule='employer contributes at least 2% of earnings between 1G and 12G (DB allowed if at least equivalent); annuity or payout to at least 77', ceiling_contrib_pctAW=paw('NOR', 12 * 100853),
  contrib_rate='>= 2% (employer)', applies_to_2020_retirees='partly (accruals only since 2006)', source=PAG, url=U['NOR'], confidence='medium',
  note='Floor 1G = 16.1% AW. Public-sector occupational DB (SPK/KLP) and private AFP (collective agreement) are not covered here: GAP.')

# ---------------- POL
R(iso3='POL', scheme='ZUS (FUS) old-age pension, NDC with initial capital', tier='public earnings-related (NDC)', financing='payroll PAYG (FUS)', legislated='legislated',
  rule='19.52% of earnings credited to notional account (and sub-account) indexed to covered wage bill growth (>= CPI); pension = capital / life expectancy at retirement (g-value); pre-1999 rights converted to initial capital',
  qualifying='age 65 men, 60 women; no minimum years for NDC pension (25/20 years only for the minimum guarantee)', ceiling_contrib_pctAW=paw('POL', 156810), ceiling_benefit_pctAW=paw('POL', 156810),
  contrib_rate='19.52%', applies_to_2020_retirees='yes for cohorts born after 1948 (all 2020 retirees); PaG Table 3.1 panel B: DB/NDC',
  source=PAG, url=U['POL'], confidence='medium', note='Ceiling PLN 156 810 (2020), 2.5x the average base amount of the previous year (PaG). FUS old-age spending not collected (GAP). 5 907.7k ZUS old-age pensioners (March 2020).')
R(iso3='POL', scheme='OFE open pension funds (former mandatory 2nd pillar)', tier='funded DC (voluntary opt-in since 2014)', financing='funded DC', legislated='legislated',
  rule='2.92% of gross wage if the worker opted in; 51.5% of assets moved to ZUS in 2014; remaining assets moved to ZUS sub-account 10 years before retirement (slide), paid by ZUS with the NDC pension',
  contrib_rate='2.92% (of the 19.52%) if opted in', applies_to_2020_retirees='yes (via slide into ZUS sub-account)', source=PAG, url=U['POL'], confidence='medium', note='Effectively folded into the public NDC benefit at payout.')
R(iso3='POL', scheme='Guaranteed minimum old-age pension (najnizsza emerytura)', tier='minimum pension top-up (contributory)', financing='state budget', legislated='legislated',
  rule='top-up to PLN 1 200/month from 1 March 2020', flat_or_min_pctAW=paw('POL', 1200 * 12), min_year=2020, qualifying='25 contribution and non-contribution years (men), 20 (women)',
  test='none (career-based top-up)', recipients_share=round(100 * 221.0 / 5907.7, 1), recipients_base='ZUS old-age pensions paid at the minimum (221.0k) / ZUS old-age pensioners (5 907.7k), March 2020',
  applies_to_2020_retirees='yes', source=f'{PAG}; ZUS Struktura wysokosci swiadczen po waloryzacji w marcu 2020 r., Tabele 1-2', url=f'{U["POL"]} ; {ZUS}', confidence='high',
  note='529.1k ZUS benefits at the minimum in total (incl. disability 182.6k, survivors 125.5k); excludes people with international or farmer (KRUS) entitlements. Pensioners without 25/20 years get pensions below the minimum (count not collected). PaG Table 3.2: minimum 23.6% AW, recipients 1.5% of 65+ (2018). Spending not collected.')
R(iso3='POL', scheme='13th pension (dodatkowe roczne swiadczenie, trzynastka)', tier='flat annual supplement to all pensioners', financing='not collected', legislated='legislated',
  rule='flat PLN 1 200 paid in April 2020 to all ZUS and KRUS pensioners (equal to the minimum pension)', flat_or_min_pctAW=paw('POL', 1200), min_year=2020,
  recipients_share='about 9.8 mn beneficiaries (planned)', recipients_base='all pensioners (ZUS, KRUS, uniformed services)', spending_pctGDP=pgdp('POL', 2020, 11700), spending_year='2020 (planned)',
  applies_to_2020_retirees='yes', source='Minister Malag quoted by Forsal, 18.04.2020', url=FORSAL, confidence='low',
  note='Read from search snippet (file not downloaded). ZUS later reports 8.4 mn recipients and > PLN 10.5 bn paid; year attribution not verified.')

# ---------------- PRT
R(iso3='PRT', scheme='Regime Geral old-age pension (earnings-related)', tier='public earnings-related (DB)', financing='payroll PAYG (not verified)', legislated='legislated',
  rule='reference earnings (lifetime, best 40 years, CPI-revalued) x accrual 2.0-2.3% per year (higher accrual on lower earnings bands relative to IAS; 2% with <= 20 years, floor 30%) x sustainability factor (early retirement only)',
  qualifying='15 contribution years; normal age 66y5m (2020)', applies_to_2020_retirees='yes (2002 rules fully for post-2002 entrants; transitional formula for earlier entrants)',
  recipients_share='1 984 849 old-age pensioners (Regime Geral, 31.12.2020)', recipients_base='pensioners', source=f'{PAG}; Seguranca Social em Numeros 2023', url=f'{U["PRT"]} ; {SSPT}', confidence='high',
  note='Accrual by reference earnings/IAS: <=1.1 2.3%, 1.1-2 2.25%, 2-4 2.2%, 4-8 2.1%, >8 2% (IAS EUR 438.81 in 2020). Contribution rate and ceiling not in collected sources. Civil servants (CGA, closed to entrants since 2006) and farmers (RESSAA, 59 385 old-age pensioners 2020) not covered.')
R(iso3='PRT', scheme='Minimum pension (complemento social / pensao minima)', tier='minimum pension top-up (contributory)', financing='not collected', legislated='legislated',
  rule='annual minimum by contribution years (14 payments, 2020): 10-15y EUR 3 854.20, 15-20y EUR 4 043.06, 21-30y EUR 4 461.38, 31+ EUR 5 576.76; indexed with IAS',
  flat_or_min_pctAW=paw('PRT', 5576.76), min_year=2020, qualifying='eligible for a Regime Geral pension (15 years)', test='none (career-based top-up)',
  applies_to_2020_retirees='yes', source=f'{PAG}; {T32}', url=U['PRT'], confidence='medium',
  note=f'Lower tiers: {paw("PRT", 3854.20)}, {paw("PRT", 4043.06)}, {paw("PRT", 4461.38)}% AW. GAP: number of pensions with complemento social and its spending not found (Conta da Seguranca Social 2020 not retrieved); PaG Table 3.2 minimum recipients not reported.')
R(iso3='PRT', scheme='Complemento Solidario para Idosos (CSI)', tier='targeted (means-tested top-up)', financing='general revenue (non-contributory citizenship subsystem)', legislated='legislated',
  rule='pays the difference between own resources and the reference amount EUR 5 258.63/yr (2019-2020)', flat_or_min_pctAW=paw('PRT', 5258.63), min_year=2020,
  qualifying='legal retirement age, receiving an old-age/survivor/invalidity pension (or not entitled to social pension), residence', test='income incl. spouse and a share of children household income (family solidarity)', taper='100%',
  recipients_share=round(100 * 171768 / 2070387, 1), recipients_base='CSI beneficiaries with at least one payment in 2020 (171 768) / old-age pensioners 31.12.2020 (2 070 387)',
  spending_pctGDP='', spending_year='', applies_to_2020_retirees='yes',
  source=f'{PAG}; Seguranca Social em Numeros 2023; CFP Caixa 4 (2025)', url=f'{U["PRT"]} ; {SSPT} ; {CFP}', confidence='high',
  note='GAP: 2020 spending not found; CFP gives EUR 235 mn (2023) and EUR 399 mn (2024, after 2024 reform). PaG Table 3.2 targeted 27.0% AW, recipients 7.5% of 65+ (2018).')
R(iso3='PRT', scheme='Pensao social de velhice (non-contributory social pension)', tier='targeted (non-contributory)', financing='non-contributory regime (financing not collected)', legislated='legislated',
  rule='means-tested flat social pension (amount not collected)', test='income <= 40% IAS single, 60% couple (CFP)', recipients_share='26 153 old-age pensioners in the non-contributory and equivalent regimes (31.12.2020)',
  recipients_base='pensioners', applies_to_2020_retirees='yes', source='Seguranca Social em Numeros 2023; CFP Caixa 4', url=f'{SSPT} ; {CFP}', confidence='medium', note='Amount and spending not collected.')

# ---------------- ESP
R(iso3='ESP', scheme='Contributory retirement pension (Seguridad Social: Regimen General, RETA)', tier='public earnings-related (DB)', financing='payroll PAYG (Seguridad Social)', legislated='legislated',
  rule='50% of the regulatory base after 15 years rising to 100% after 37 (0.19%/0.18% per month); base = last 23 years of earnings (2020, 25 from 2022), price-revalued except last 2; 14 payments; max pension EUR 2 683.34/month',
  qualifying='15 contribution years; age 65y10m (65 with 38.5 years) in 2020', ceiling_contrib_pctAW=paw('ESP', 48841.2), ceiling_benefit_pctAW=paw('ESP', 2683.34 * 14),
  spending_pctGDP=pgdp('ESP', 2020, 131922.49385), spending_year=2020, applies_to_2020_retirees='yes (2011 reform phasing in to 2027)',
  source=f'{PAG}; Boletin Informativo de la Seguridad Social, Gestion economica, diciembre 2020 (obligaciones reconocidas, agregado del sistema)', url=f'{U["ESP"]} ; {SEGSOC}', confidence='high',
  note='Spending = contributory pensions EUR 131 922 mn 2020, all classes (retirement, survivors, permanent incapacity), excl. complementos a minimos; Clases Pasivas (civil servants, state budget) not included. Contribution rate not in collected sources.')
R(iso3='ESP', scheme='Complementos a minimos (minimum pension supplements)', tier='minimum pension top-up (means-tested)', financing='general revenue (classified non-contributory in the Social Security budget since 2014)', legislated='legislated',
  rule='tops contributory pensions to the minimum: EUR 683.5/month single, EUR 843.4 with dependent spouse, 14 payments (2020, age 65+)',
  flat_or_min_pctAW=paw('ESP', 683.5 * 14), min_year=2020, qualifying='entitled to a contributory pension; residence in Spain', test='income test (limit not collected)', taper='not collected',
  recipients_share=22.5, recipients_base='retirement pensions with complemento (1 323 839) / all retirement pensions, Dec 2020; all classes 2 288 079 = 23.99%',
  spending_pctGDP=pgdp('ESP', 2020, 6955.00527), spending_year=2020, applies_to_2020_retirees='yes',
  source=f'{PAG}; Boletin Informativo de la Seguridad Social, Gestion economica, diciembre 2020, II.8.1-II.8.2', url=f'{U["ESP"]} ; {SEGSOC}', confidence='high',
  note='Spending EUR 6 955 mn 2020 (all classes; retirement EUR 4 131 mn = 0.37% GDP); = 5.3% of contributory pension spending. INSS budget execution gives EUR 6 880 mn. PaG Table 3.2: minimum 35.5% AW, recipients 25% of 65+ (2018).')
R(iso3='ESP', scheme='Pension no contributiva de jubilacion (PNC)', tier='targeted (means-tested, non-contributory)', financing='non-contributory pensions budget (IMSERSO)', legislated='legislated',
  rule='flat means-tested pension (amount not collected)', qualifying='not collected', test='not collected', spending_pctGDP=pgdp('ESP', 2020, 2437.43028), spending_year=2020,
  recipients_share=2.85, recipients_base='PaG Table 3.2, % of 65+ (2018)', applies_to_2020_retirees='yes',
  source=f'Boletin Informativo de la Seguridad Social, diciembre 2020 (pensiones no contributivas); {T32}', url=f'{SEGSOC} ; https://stat.link/uxgr8v', confidence='medium',
  note='Spending EUR 2 437 mn includes disability PNC (no split collected). PaG Table 3.2 targeted 20.4% AW.')

# ---------------- SWE
R(iso3='SWE', scheme='Inkomstpension (NDC)', tier='public earnings-related (NDC)', financing='payroll PAYG with buffer fund', legislated='legislated',
  rule='16% of pensionable income credited (14.88% of gross), indexed to average earnings, annuitised with cohort life-expectancy divisor and 1.6% norm; balancing mechanism',
  qualifying='withdrawal from 62 (2020)', ceiling_contrib_pctAW=paw('SWE', 538700), ceiling_benefit_pctAW=paw('SWE', 538700), contrib_rate='18.5% of pensionable income in total (17.21% of gross), of which 16% NDC',
  applies_to_2020_retirees='yes for cohorts born 1954+; cohorts 1938-1953 partly ATP/tillaggspension (PaG Table 3.1 panel B: DB/NDC + FDC + basic + targeted)',
  source=PAG, url=U['SWE'], confidence='medium', note='Ceiling SEK 501 000 pensionable (= SEK 538 700 gross, 2020); PaG text says "just over 111%" of AW, 115.7% with the profile AW. Floor SEK 20 008. Employer contributions above the ceiling are a tax. Spending not collected (GAP).')
R(iso3='SWE', scheme='Premiepension (FDC)', tier='mandatory funded DC (public)', financing='funded DC', legislated='legislated',
  rule='2.5% of pensionable income (2.33% of gross) to individual accounts with fund choice; annuity (fixed or variable)', contrib_rate='2.5% of pensionable income', applies_to_2020_retirees='yes (phasing in; payouts +28.1% 2019-20)',
  source=f'{PAG}; Pensionsmyndigheten Arsredovisning 2020', url=f'{U["SWE"]} ; {PMAR}', confidence='medium', note='Payout amounts are in images in the annual report; not extracted.')
R(iso3='SWE', scheme='Garantipension (guarantee pension)', tier='targeted (pension-tested top-up)', financing='general revenue (state budget, UO11 1:1)', legislated='legislated',
  rule='full SEK 103 161/yr single born after 1938 (2020), 40 years residence for full; price-indexed', flat_or_min_pctAW=paw('SWE', 103161), min_year=2020,
  qualifying='age 65, 3 years residence (40 for full)', test='earnings-related (income) pension only', taper='100% on first SEK 59 598 of earnings-related pension, 48% above; exhausted at SEK 150 348',
  recipients_share='44 (women), 13 (men) in 2018; forecast 720 000 in 2020 = ' + str(round(100 * 720000 / POP65[('SWE', 2020)], 1)) + '% of 65+',
  recipients_base='old-age pensioners with any guarantee pension (2018); forecast count / World Bank 65+ population 2020',
  spending_pctGDP=pgdp('SWE', 2018, 13142.095), spending_year=2018, applies_to_2020_retirees='yes',
  source=f'{PAG}; Prop. 2019/20:1 Utgiftsomrade 11 (Tabell 2.8, diagram 2.1); Pensionsmyndigheten Arsredovisning 2020', url=f'{U["SWE"]} ; {UO11} ; {PMAR}', confidence='high',
  note='Spending = outcome 2018 SEK 13 142 mn / Eurostat 2018 GDP. 2020: annual report says outlay was SEK 555 mn (3.7%) below the appropriation (implies about SEK 14.4 bn, not stated directly); payouts +9.2% 2019-20. PaG Table 3.2 targeted 22.2% AW, recipients 35% of 65+.')
R(iso3='SWE', scheme='Bostadstillagg (housing supplement for pensioners) and aldreforsorjningsstod (maintenance support)', tier='targeted (means-tested)', financing='general revenue', legislated='legislated',
  rule='housing supplement covers housing costs up to SEK 7 000/month (2020), reduced by 62% of income; maintenance support tops up for short residence', test='income and assets', taper='62% (housing supplement, 2020)',
  applies_to_2020_retirees='yes', source=f'{PAG}; Pensionsmyndigheten Arsredovisning 2020', url=f'{U["SWE"]} ; {PMAR}', confidence='medium',
  note='Recipients and outcome spending not extracted (tables are images). Budget proposals for 2021: housing supplement SEK 10.2 bn, maintenance support SEK 1.19 bn (Pensionsmyndigheten Budgetunderlag 2021-2023 del 1, https://www.pensionsmyndigheten.se/content/dam/pensionsmyndigheten/blanketter---broschyrer---faktablad/publikationer/anslagsbelastning-och-prognos/2020/Budgetunderlag%202021-2023%20del%201%20februari.pdf; file not kept).')
R(iso3='SWE', scheme='Quasi-mandatory occupational pensions (ITP1 white-collar; also SAF-LO, AKAP-KL/KAP-KL, PA16)', tier='quasi-mandatory private DC (collective agreements)', financing='funded DC (ITP1); older ITP2 DB',
  legislated='collective agreement', rule='ITP1: 4.5% of salary up to 7.5 income base amounts (SEK 501 000, 2020), 30% above', ceiling_contrib_pctAW='', contrib_rate='4.5% / 30% above 7.5 IBA (ITP1)',
  recipients_share='> 90 (coverage of employees)', recipients_base='employees', applies_to_2020_retirees='partly (ITP1 for born 1979+; 2020 retirees mostly in older DB plans)',
  source=PAG, url=U['SWE'], confidence='medium', note=f'7.5 IBA = {paw("SWE", 501000)}% AW (contribution rate jumps above it). Other agreements and spending not collected (GAP).')

# ---------------- CHE
R(iso3='CHE', scheme='AHV/AVS old-age and survivors insurance (1st pillar)', tier='public earnings-related (DB, capped, with minimum)', financing='payroll PAYG + federal contribution + VAT', legislated='legislated',
  rule='full pension (44/43 years) between CHF 14 220 and CHF 28 440/yr (2020) depending on average lifetime earnings, maximum reached at CHF 85 320; couples capped at 150% of single max; indexed 50% prices/50% wages every 2 years',
  flat_or_min_pctAW=paw('CHE', 14220), min_year=2020, qualifying='age 65 men, 64 women; full career 44/43 years', ceiling_benefit_pctAW=paw('CHE', 85320),
  spending_pctGDP=pgdp('CHE', 2020, 45977), spending_year=2020, applies_to_2020_retirees='yes',
  source=f'{PAG}; BSV Taschenstatistik Sozialversicherungen 2022 (AHV Betriebsrechnung)', url=f'{U["CHE"]} ; {BSVT}', confidence='high',
  note=f'Maximum pension {paw("CHE", 28440)}% AW. Spending = AHV Ausgaben CHF 45 977 mn 2020 (old-age and survivors; matches 25.1% of CHF 182 bn). AHV contribution rate and absence of a contribution ceiling are not in the collected sources (GAP). PaG Table 3.2: minimum 16.3% AW.')
R(iso3='CHE', scheme='Ergaenzungsleistungen (EL/PC) zur AHV (supplementary benefits)', tier='targeted (means-tested)', financing='general revenue (Confederation about 30%, cantons the rest)', legislated='legislated',
  rule='pays recognised expenses minus counted income; recognised living needs CHF 19 450/yr single at home + rent up to CHF 13 200 (2020) + health and disability costs',
  flat_or_min_pctAW=paw('CHE', 19450), min_year=2020, qualifying='AHV/IV pension entitlement, residence', test='income and assets', taper='100% (gap-filling)',
  recipients_share=12.7, recipients_base='old-age pensioners in Switzerland receiving EL (218 900 EL zur AV, Dec 2020)', spending_pctGDP=pgdp('CHE', 2020, 3167.6), spending_year=2020,
  applies_to_2020_retirees='yes', source='BSV, Statistik der Ergaenzungsleistungen zur AHV und IV 2020, T1 and T4', url=ELS, confidence='high',
  note='EL zur AHV CHF 3 167.6 mn 2020 (total EL CHF 5 367.9 mn); EL raise the AHV pension sum by 8.3% (BSV). About 40% of EL spending is care-home related. PaG Table 3.2 lists CHE targeted recipients as 0.127 -- apparently 12.7% stored as a fraction.')
R(iso3='CHE', scheme='Mandatory occupational pension (BVG/LPP, 2nd pillar)', tier='mandatory private (DC with legislated credits, minimum interest and conversion rate: implicitly DB per PaG)', financing='funded', legislated='legislated (1985)',
  rule='age credits 7/10/15/18% of coordinated salary (gross minus CHF 24 885, max CHF 60 435) at ages 25-34/35-44/45-54/55-65; minimum interest 1.00%; conversion rate 6.8%; >= 1/4 as lump sum; most funds pay above the mandatory minimum',
  qualifying='earnings >= CHF 21 330 (2020)', ceiling_contrib_pctAW=paw('CHE', 85320), contrib_rate='7-18% of coordinated salary by age (employer >= half)',
  spending_pctGDP=pgdp('CHE', 2020, 31515), spending_year=2020, applies_to_2020_retirees='yes', source=f'{PAG}; BSV Taschenstatistik 2022 (BV Betriebsrechnung)', url=f'{U["CHE"]} ; {BSVT}', confidence='medium',
  note=f'Entry threshold {paw("CHE", 21330)}% AW; coordination deduction {paw("CHE", 24885)}% AW; insured salary capped at CHF 85 320. Spending = BV pensions CHF 31 515 mn 2020 (old-age, survivor, disability; incl. extra-mandatory) + lump sums CHF 10 949 mn ({pgdp("CHE", 2020, 10949)}% GDP); 842 357 BV old-age pensions 2020. Column values realigned by hand from pdftotext.')

# ---------------- GBR (design for 2020 retirees and stock vs steady state)
R(iso3='GBR', scheme='basic State Pension (SPa before 6 April 2016)', tier='contribution-based basic (flat)', financing='payroll PAYG, National Insurance (not verified)', legislated='legislated',
  rule='Category A GBP 134.25/week (2020/21) for 30 qualifying years (SPa 2010-2016), pro rata from 1 year', flat_or_min_pctAW=paw('GBR', 134.25 * GBW), min_year=2020,
  qualifying='30 NI qualifying years for full (paid, treated as paid or credited)', recipients_share=round(100 * 11224 / 12556, 1), recipients_base='share of State Pension caseload with basic SP (11 224k of 12 556k), 2019/20',
  spending_pctGDP=pgdp('GBR', 2019, 66792.952), spending_year='2019/20', applies_to_2020_retirees='no (stock only; closed to people reaching SPa from April 2016)',
  source=f'{PAG}; DWP benefit expenditure and caseload tables, Spring Statement 2021 (State_Pension); gov.uk Benefit and pension rates 2020 to 2021', url=f'{U["GBR"]} ; {DWP} ; {RATES}', confidence='high',
  note='Spending GBP 66 793 mn / WB calendar-2019 GDP (fiscal-year mismatch). Category D non-contributory GBP 80.45/week, 58k cases, GBP 119 mn. Graduated Retirement Benefit GBP 2 040 mn (9 813k cases, small amounts).')
R(iso3='GBR', scheme='Additional State Pension: SERPS / State Second Pension (S2P) (SPa before 6 April 2016)', tier='public earnings-related (DB), with contracting-out', financing='payroll PAYG, National Insurance (not verified)', legislated='legislated',
  rule='earnings-related additional pension (accrual bands not collected); maximum additional pension GBP 179.41/week (2020/21); contracted-out members accrued in occupational schemes instead',
  ceiling_benefit_pctAW=paw('GBR', 179.41 * GBW), recipients_share=round(100 * 9238 / 12556, 1), recipients_base='share of State Pension caseload with S2P/SERPS (9 238k), 2019/20',
  spending_pctGDP=pgdp('GBR', 2019, 18329.088), spending_year='2019/20', applies_to_2020_retirees='no (stock); for 2020 retirees pre-2016 additional-pension rights enter the nSP starting amount (row below)',
  source=f'{PAG}; DWP Spring Statement 2021 tables; gov.uk rates 2020-21', url=f'{U["GBR"]} ; {DWP} ; {RATES}', confidence='medium',
  note='Accrual bands (LET, UAP) and contracted-out deduction rules not in collected sources (GAP). The ceiling given is the maximum additional pension, not an earnings ceiling.')
R(iso3='GBR', scheme='new State Pension (SPa from 6 April 2016), incl. transitional starting amount and protected payment', tier='contribution-based basic (flat), with transitional earnings-related element', financing='payroll PAYG, National Insurance (not verified)', legislated='legislated',
  rule='full rate GBP 175.20/week (2020/21) with 35 qualifying years, min 10; transitional: the pre-2016 NI record (incl. additional pension) sets a starting amount (PaG); amounts above the full rate are paid as a protected payment (DWP tables), uprated 1.7% in 2020 (gov.uk rates)',
  flat_or_min_pctAW=paw('GBR', 175.20 * GBW), min_year=2020, qualifying='10 years minimum, 35 for full', recipients_share=round(100 * 1305 / 12556, 1), recipients_base='share of State Pension caseload on nSP (1 305k), 2019/20; 366k with protected payments',
  spending_pctGDP=pgdp('GBR', 2019, 10447.129 + 418.359), spending_year='2019/20', applies_to_2020_retirees='yes (this is the rule for 2020 retirees; steady state = flat nSP + auto-enrolment)',
  source=f'{PAG}; DWP Spring Statement 2021 tables; gov.uk rates 2020-21', url=f'{U["GBR"]} ; {DWP} ; {RATES}', confidence='high',
  note='nSP GBP 10 447 mn + protected payments GBP 418 mn. Starting-amount formula (old vs new rules, contracted-out deduction) not in collected sources (GAP). PaG Table 3.2 contribution-based basic 16.7% AW (= bSP), recipients 104.8% of 65+.')
R(iso3='GBR', scheme='Pension Credit: Guarantee Credit', tier='targeted (means-tested)', financing='general revenue (not verified)', legislated='legislated',
  rule='tops income up to the standard minimum guarantee GBP 173.75/week single, GBP 265.20 couple (2020/21), plus additions (severe disability, carers, housing costs)',
  flat_or_min_pctAW=paw('GBR', 173.75 * GBW), min_year=2020, qualifying='Pension Credit qualifying age (66 from Oct 2020)', test='income and capital', taper='100%',
  recipients_share=round(100 * 1563 / 12556, 1), recipients_base='Pension Credit caseload (1 563k, of which 1 309k receive Guarantee Credit) / State Pension caseload (12 556k), 2019/20',
  spending_pctGDP=pgdp('GBR', 2019, 4668.3985), spending_year='2019/20', applies_to_2020_retirees='yes',
  source='DWP Spring Statement 2021 tables (Pension_Credit); gov.uk rates 2020-21', url=f'{DWP} ; {RATES}', confidence='high',
  note='Total Pension Credit GBP 5 061 mn (0.22% GDP) = 5.1% of State Pension spending; caseload 2018/19 1 654k. PaG Table 3.2 targeted 21.6% AW, recipients 15.9% of 65+ (2018).')
R(iso3='GBR', scheme='Pension Credit: Savings Credit', tier='targeted (rewards modest savings)', financing='general revenue (not verified)', legislated='legislated',
  rule='GBP 0.60 per GBP 1 of income above the threshold up to a maximum, withdrawn at 40% above the minimum guarantee (2021/22 parameters in PaG: threshold GBP 153.70, max GBP 14.04/week single)',
  test='income', taper='+60% build-up, -40% withdrawal', recipients_share=round(100 * (533 + 254) / 12556, 1), recipients_base='Savings Credit cases (533k with GC + 254k only) / State Pension caseload, 2019/20',
  spending_pctGDP=pgdp('GBR', 2019, 392.4883), spending_year='2019/20', applies_to_2020_retirees='no (closed to people reaching SPa from April 2016)',
  source=f'{PAG}; DWP Spring Statement 2021 tables', url=f'{U["GBR"]} ; {DWP}', confidence='high', note='Savings Credit GBP 392 mn.')
R(iso3='GBR', scheme='Workplace pension automatic enrolment (NEST and other qualifying schemes)', tier='quasi-mandatory private DC (auto-enrolment, opt-out)', financing='funded DC', legislated='legislated (opt-out)',
  rule='minimum 8% of qualifying earnings (from April 2019; 5% in 2018/19) for workers 22 to SPa earning over GBP 10 000; band GBP 6 032-46 350 (2018/19)',
  ceiling_contrib_pctAW=paw('GBR', 46350), contrib_rate='8% of band earnings (employer >= 3%)', applies_to_2020_retirees='no (rolled out 2012-2018; steady-state tier)',
  source=PAG, url=U['GBR'], confidence='medium', note=f'Lower band limit {paw("GBR", 6032)}% AW (2018/19 band; 2020/21 band not collected). Older contracted-out occupational DB schemes not covered (GAP).')

# ---------------- USA
R(iso3='USA', scheme='OASI (Social Security old-age insurance), PIA formula', tier='public earnings-related (DB, progressive)', financing='payroll PAYG (trust fund)', legislated='legislated',
  rule='PIA = 90% of AIME up to USD 960 + 32% to USD 5 785 + 15% above (2020 bend points); AIME = 35 highest wage-indexed years; price-indexed after 62; 50% spousal addition',
  qualifying='10 years of contributions; NRA 66y8m for cohort 62 in 2020', ceiling_contrib_pctAW=paw('USA', 137700), ceiling_benefit_pctAW=paw('USA', 137700), contrib_rate='',
  applies_to_2020_retirees='yes', source=f'{PAG}; Federal Register 84 FR 56515 (2019-22921) and 86 FR 58715 (2021-23031)', url=f'{U["USA"]} ; {FR20} ; {FR22}', confidence='high',
  note=('Bend points (annual USD 11 520, 69 420) and taxable max USD 137 700 as % of: OECD AW USD 60 220 -> ' + f'{paw("USA", 11520)}, {paw("USA", 69420)}, {paw("USA", 137700)}; '
        f'AWI 2020 USD 55 628.60 -> {round(100*11520/55628.60,1)}, {round(100*69420/55628.60,1)}, {round(100*137700/55628.60,1)}; '
        f'AWI 2018 USD 52 145.80 (index used to set 2020 values) -> {round(100*11520/52145.80,1)}, {round(100*69420/52145.80,1)}, {round(100*137700/52145.80,1)}. '
        'Payroll contribution rate and OASI spending not in collected sources: ssa.gov blocked automated access (GAP; SOCX from the other agent). Special minimum PIA not covered.'))
R(iso3='USA', scheme='Supplemental Security Income (SSI), aged', tier='targeted (means-tested)', financing='federal public assistance, not Social Security (CRS); optional state supplements', legislated='legislated',
  rule='federal benefit rate USD 783/month individual, USD 1 175 couple (2020); price-indexed', flat_or_min_pctAW=paw('USA', 783 * 12), min_year=2020, qualifying='aged 65+ (or blind/disabled), citizen or qualified alien, US residence',
  test='income and resources (USD 2 000 single / 3 000 couple)', taper='100% after USD 20 general and USD 65 + 1/2 earned-income disregards',
  recipients_share=round(100 * 2.3e6 / POP65[('USA', 2020)], 1), recipients_base='SSI recipients aged 65+ (2.3 mn, Jan 2020; includes former disabled recipients who aged in) / World Bank 65+ population 2020',
  spending_pctGDP=pgdp('USA', 2020, 1071 * 12), spending_year='2020 (Jan 2020 monthly x 12)', applies_to_2020_retirees='yes',
  source=f'{PAG}; CRS In Focus IF10482 (Feb 2020, citing SSA Monthly Statistical Snapshot Jan 2020); Federal Register 2019-22921', url=f'{U["USA"]} ; {CRS} ; {FR20}', confidence='medium',
  note=f'FBR = {round(100*783*12/55628.60,1)}% of AWI 2020. Average payment to 65+ USD 466/month (total USD 1 071 mn/month). PaG Table 3.2 targeted 15.6% AW, recipients 2.2% of 65+ (2018), apparently the aged-eligibility category only. State supplements excluded.')

COLS = ['iso3', 'scheme', 'tier', 'financing', 'legislated', 'rule', 'flat_or_min_pctAW', 'min_year', 'qualifying', 'test', 'taper', 'ceiling_contrib_pctAW',
        'ceiling_benefit_pctAW', 'contrib_rate', 'recipients_share', 'recipients_base', 'spending_pctGDP', 'spending_year', 'applies_to_2020_retirees', 'source', 'url',
        'retrieved', 'confidence', 'note']


def write(path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        f.write('# DRAFT, not wired into python/paper: scheme rules for ITA JPN LUX NLD NZL NOR POL PRT ESP SWE CHE GBR USA, hand-collected 2026-10-30; see notes/data_thetaTau_countriesB.md. '
                'pctAW against PaG 2021 profile AW; pctGDP against Eurostat nama_10_gdp CP_MNAC or World Bank NY.GDP.MKTP.CN. Read with pandas.read_csv(..., comment="#").\n')
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator='\n')
        w.writeheader()
        for r in rows:
            assert set(r) <= set(COLS), set(r) - set(COLS)
            w.writerow({c: r.get(c, '') for c in COLS})
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
