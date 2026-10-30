# Data for measuring θ and τ consistently in the OECD cross-section (O5 of the 2026-10-29 review)

Working note. It collects and records what exists; it does not choose a measure. Sections B and later hold the
scheme-by-scheme country rules.

## A. Harmonised sources (all 26 countries)

**Files.** `data/oecd26_pensionTiers_harmonised.csv` (DRAFT, not wired into anything; long: `status, iso3, item, tier,
earnings_multiple, sex, value, unit, year, source, url, retrieved, note`; 8,485 rows, 62 items), written by
`python/paper/oecd26PensionTiers.py` (stage (0); raw files in `logs/thetaTau_raw/harmonised/`, all retrieved
2026-10-30). Every number below is a row of that csv, under the item named, with its URL. Values are as published:
no interpolation, no filling. A blank cell is no row.

### A.1 What exists, and the coverage of the 26

| item (csv) | source (id) | vintage / year | missing of the 26 |
|---|---|---|---|
| `grr_tier`: gross RR, public / mandatory private / total mandatory / voluntary / total, at 0.5, 1, 2 AW | PaG 2021 table 4.2 (StatLink uwc8nt); PaG 2025 table 4.2 (pru4oj) | rules 2020; 2024 | none; **men only** |
| `grr_mandatory`, `nrr_mandatory`: gross and net RR, mandatory, men and women | PaG 2021 tables 4.1, 4.4 (b2f0ws, cofr31); PaG 2025 (oeavq4, ic8ung) | 2020; 2024 | none |
| `rr_mandatoryVoluntary`: gross and net, mandatory and with voluntary | PaG tables 4.5 (scxdj3; f2v8nc) | 2020; 2024 | none |
| `prr_dataExplorer`: as 4.1/4.4/4.5, M and F | Data Explorer DSD_PAG@DF_PRR | 2024 only | none |
| `firstTier_value`, `firstTier_recipients`: residence basic, targeted, contributory basic, minimum (% AW; % of 65+) | PaG tables 3.2 (uxgr8v; i28xu0) | 2020; 2024 | recipients: GRC 2020 |
| `firstTier_value_figure`: the same split additively (top-up over basic) | PaG figures 3.2, 3.3 (kpoilu, k23yri; s5w1y7, 7ohtnu) | 2020; 2024 | none |
| `structure_panelA/B`: which first and second tiers exist, DB/NDC/FDC, [q] | PaG tables 3.1 (2xd6uo; mh9ruy) | 2020; 2024 | none |
| `contribRate_mandatory`, `contribCeiling`: employee/employer × public/private, effective rate at AW | PaG tables 8.1 (h4uwj7; orhufb) | 2020; 2024 | none (IRL, ESP, GBR: 2021 table 8.2, all social insurance, `contribRate_socialInsurance`) |
| `contribRate_fundedPlans`: minimum rates in (quasi-)mandatory and auto-enrolment plans | PaG figures 9.1 (8gtspo; vwcalj) | 2020; 2024 | 16 (only countries with such plans) |
| `progressivity2013`: pension Gini, earnings Gini, index 100(1 − G_pens/G_earn) | PaG 2013 table 4.19 (StatLink 888932907566) | rules 2012 | none |
| `socx_TP*`: old-age (TP11, TP111 pension, TP112 early, TP113 other cash) and survivors (TP21, TP211), public / mandatory private / voluntary private, % GDP | Data Explorer DSD_SOCX_AGG@DF_SOCX_AGG | 2019, 2020 | none |
| `socx_programme_*`: every public and mandatory-private old-age/survivors cash programme, % GDP, with this note's class | SOCX programme-level workbook SOCX2025-All-nat-cur.xlsx (webfs.oecd.org) | 2019, 2020 | none |
| `privateSpending_pag`: private spending with PaG's m/q/v label | PaG 2021 table 8.4 (kp4d5j, 2017); PaG 2025 table 8.3 (madn2r) | 2017; 2021-23 | HUN LUX NZL POL |
| `essp_pensions_*`, `essp_oldAge_*`, `essp_survivors_*`: means-tested vs not, % GDP; `essp_beneficiaries_*` | Eurostat spr_exp_pens, spr_exp_fol, spr_exp_fsu, spr_pns_ben (all schemes) | 2019, 2020 | AUS CAN GBR JPN NZL USA (not in ESSPROS; UK ends before 2019) |
| `essp_receipts`: employers', protected persons', general government (earmarked, general revenue) | Eurostat spr_rec_sumt | 2019, 2020 | as above; **all functions, not pensions** |
| `na29_*`: actual contributions (D6111, D6131), imputed (D6121), benefits (D62) by scheme type | Data Explorer DSD_NAPENS@DF_TABLE29 (national accounts table 29) | 2018-21 (EU: 2018, 2021) | AUS (NZL ends 2019) |
| `gps_benefits`, `gps_contributions`: asset-backed plans, % GDP | Data Explorer DSD_FP@DF_BC | 2019, 2020 | GRC IRL JPN NZL SWE |
| `gps_assets`; `assets_pag` (with public reserve funds); `coverage_pag` | DSD_FP@DF_PA; PaG tables 9.2 (qi2ev9; 9ku103), 9.1 (gkvjah; f31vde) | 2019-20; latest | DF_PA: AUT NOR |
| `incomeSources65`: public transfers, occupational, capital, work | PaG figures 7.1 (lqhcun; zx5sen) | 2018 or latest; per country | none |

**Not published, so not collected.** No PaG table gives RRs at 0.75 or 1.5 AW (2021 and 2025 tables: 0.5, 1, 2 only), nor
the tier split for women. The country profiles (oe.cd/pag) were not reached: oecd.org answers scripted requests with a
Cloudflare challenge (403), so their charts by earnings are unchecked. ESSPROS publishes scheme-level expenditure and
receipts only as "All schemes": the scheme codelist (SPSCHEME) exists, the public tables carry no scheme rows. The
progressivity index is in PaG 2013; PaG 2015, 2021 and 2025 do not have it (2017, 2019, 2023 not checked). The OECD
Global Pension Statistics flows have no mandatory/voluntary dimension (only occupational/personal, DB/DC, vehicle).

### A.2 Definitions that matter

- PaG "mandatory public" includes NDC and funded DC run by the state (SWE premium pension, LVA, NOR) and FIN's
  privately managed earnings-related scheme (table 8.1's note: national accounts define it as public). "Mandatory
  private" includes quasi-mandatory collective-agreement schemes ([q] in table 3.1: NLD, DNK, SWE, ISL) and the UK's
  auto-enrolment (27.4% at all three multiples in 2020).
- Table 3.2's "targeted" column is not one concept: for NOR and ISR (and CAN in 2021) it is the total first tier
  including the basic amount; for DNK, ISL (and CAN in 2025) it is the top-up only. Figures 3.2/3.3 give the additive
  split. Its recipients can exceed 100% of the 65+ (recipients under 65 or abroad).
- SOCX voluntary private (ES30) is published only as cash plus in kind (`socx_*_cashInKind`); public and mandatory
  private by cash. SOCX classifies by who pays and whether it is legislated, not by the PaG tiers.
- Programme classes (`tier` = source:class) are this collection's reading of the SOCX title, not a SOCX field:
  govEmployees, meansTested, targetedPensionTested (FIN KEL and SWE guarantee pension, which SOCX labels
  non-means-tested), basic, earningsRelated, other (veterans, injury, care allowances). Old-age programmes sum to
  SOCX's TP111+TP113 to 0.005 p.p. of GDP everywhere but CHE (0.05 short, 2019).

### A.3 Facts for θ

Index I = RR(1)/RR(0.5) from table 4.2, men; θ = 2 − 1/I is the current mapping. Private share = mandatory private
over total mandatory RR at 1 AW. Recipients from table 3.2 (2020), progressivity from PaG 2013 (OECD distribution).

| | I mandatory 2020 | I public 2020 | I public 2024 | private share at 1 AW 2020 | first-tier recipients, % of 65+ (2020) | progressivity 2013 |
|---|---|---|---|---|---|---|
| AUS | 0.499 | 0.000 | 0.320 | 1.00 | targeted 63 | 72 |
| ISL | 0.711 | 0.000 | 0.019 | 1.00 | basic 67 | 17 |
| DNK | 0.640 | 0.395 | 0.405 | 0.63 | basic 103 | 57 |
| NLD | 0.954 | 0.500 | 0.500 | 0.58 | basic 104 | 4 |
| GBR | 0.694 | 0.500 | 0.500 | 0.56 | contrib. basic 105, targeted 16 | 85 |
| CHE | 0.831 | 0.662 | 0.659 | 0.50 | targeted 0.13 (2024: 12.8) | 67 |
| SWE | 0.868 | 0.836 | 0.989 | 0.22 | targeted 35 | −13 |
| NOR | 0.760 | 0.729 | 0.752 | 0.14 | basic 103 | 45 |
| NZL | 0.603 | 0.603 | 0.610 | 0 | basic 105 | 100 |
| AUT / FIN / FRA | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 | 0 | min 10 / targeted 38 / min 38 | 28 / 4 / 31 |
| HUN / ITA / ESP | 1 / 1 / 1 | 1 / 1 / 1 | 0.965 / 1 / 0.998 | 0 | min 0.6 / min 32 / min 25 | 0 / 1 / 24 |

- AUS and ISL have no public pension at all for a full-career average earner (RR 0 at 1 AW: the Age Pension and
  ISL's national pension are means-tested against the funded pension), so a public-only I is 0 and 2 − 1/I has no value.
- NZL's "0.5" column is a low earner at 0.60 AW (2021) and 0.61 AW (2025 pdf; the 2025 StatLink note says 0.63).
  NZ Super is flat, and the published ratios are exactly 0.603 and 0.610, i.e. a flat benefit read at 0.603 and 0.610
  AW. Read at 0.5, the same flat benefit gives I = 0.5 (θ = 0); the current mapping gives θ = 0.34.
- In the six θ = 1 countries the minimum pensions exist and are large in value (AUT 28%, ESP 36%, ITA 23%, FRA 20%
  of AW; FIN's national pension 22%), and in FRA, FIN, ITA, ESP a quarter to two-fifths of the 65+ receive one (2020),
  but the full-career worker at 0.5 AW never qualifies. PaG 2013's index, which integrates over a whole earnings
  distribution, is 24-31 for AUT, FRA, ESP but about 0-4 for FIN, HUN, ITA. Recipients fell sharply by 2024 in ITA
  (32 → 14) and ESP (25 → 12) and rose in BEL (33 → 41); PRT's minimum has recipients only in 2025 (30): the
  definitions changed between editions. CHE's 2020 targeted recipients, 0.127, against 12.8 in 2025, look like a
  fraction printed as a percentage.
- PaG 2013's index is on mandatory schemes too (NLD 4 includes its occupational DB).

### A.4 Facts for τ (SOCX 2019, % of GDP; programmes from the programme-level file)

| | public old-age+surv. cash | mand. private | vol. private | of public: gov. employees | of public: means-tested + targeted | asset-backed benefits / contributions (DF_BC) | assets |
|---|---|---|---|---|---|---|---|
| AUS | 4.28 | 5.05 | – | 1.56 | 2.52 | 5.77 / 6.69 | 136 |
| ISL | 2.88 | 4.51 | – | 0 | 2.86 | 5.29 / 9.88 | 173 |
| CHE | 6.55 | 5.38 | – | 0.03 | 0.11 | 5.24 / 8.24 (occ.) | 155 |
| DNK | 8.15 | 1.98 | 0.38 | 1.30 | 6.13 | 5.72 / 8.04 (occ.) | 221 |
| NLD | 6.37 | – | 3.08 | 1.51 | 0.04 | 3.87 / 4.27 | 190 |
| GBR | 7.51 | 0.62 | 2.49 | 2.52 | 0.23 | 2.84 / 2.69 | 107 |
| SWE | 8.08 | – | 1.89 | 1.07 | 0.26 | not published | 100 |
| NOR | 7.02 | – | 1.05 | 0 | 0.23 | 1.28 / 2.94 | 12 (PaG 9.2, 2020) |
| USA | 7.04 | – | 5.55 | 2.24 | 0.03 | 6.56 / 4.94 (occ.) | 150 |

- **Government-employee pensions are inside SOCX public spending**, 1-4% of GDP: FIN 3.86, ITA 3.75, GRC 3.06,
  AUT 2.55, GBR 2.52, FRA 2.31 (central-government schemes only; local ones are inside "other schemes"), USA 2.24
  (federal and state/local, largely funded), DEU 1.77, AUS 1.56, NLD 1.51 (ABP), DNK 1.30. They are employers'
  pensions for their own staff, not PAYG transfers by the formula the model gives.
- **SOCX and PaG disagree on what is mandatory.** SOCX has no mandatory-private row for NLD, SWE, NOR: their
  occupational schemes are voluntary private (ES30), and NLD's ABP is public. PaG labels the same spending q (NLD
  3.74), q/m (SWE 1.97), v/m (NOR 0.94) and counts them as mandatory private in its RRs. The UK's auto-enrolment is
  mandatory private in PaG table 4.2 but voluntary in SOCX; SOCX's UK mandatory private (0.62) is the legacy
  contracted-out Guaranteed Minimum Pension.
- **SOCX revised the private series.** PaG 2021 table 8.4 printed 2017 values from an older SOCX vintage: NLD q 5.57,
  SWE q/m 3.10, GBR v 4.58, CAN v 5.47. The current DF_SOCX_AGG gives 3.22, 1.98, 2.23, 4.44 for 2017.
- **Funded tiers are immature**: contributions exceed benefits in ISL (9.9 vs 5.3), CHE, DNK, NOR (2.9 vs 1.3; OTP
  from 2006) and AUS (6.7 vs 5.8). The UK's total (2.84 vs 2.69) is dominated by legacy DB, so AE's immaturity
  does not show there. SWE, JPN, NZL, IRL, GRC: no flows in DF_BC.
- **ESSPROS old-age pensions include the occupational funds** where they are social protection: NLD 8.78 vs SOCX
  public TP111 6.08; CHE 8.83 vs 5.90. DNK's whole folkepension is means-tested in ESSPROS (6.14 of 9.90); SWE's
  guarantee pension is not flagged means-tested (no MT row); FIN's national pension counts as non-means-tested.
- **Payroll vs budget.** Table 29, social security schemes (S13PS), actual contributions (D6111 + D6131) over
  pension benefits (D62), 2018: AUT 0.82, BEL 0.92, CAN 1.09, CHE 0.79, CZE 1.08, DEU 0.85, ESP 0.83, FIN 0.79,
  FRA 0.72, GRC 0.51, HUN 0.89, IRL 1.12, ITA 0.70, LUX 0.77, NLD 0.66 (AOW), NOR 0.72, POL 0.75, PRT 1.05, SWE 0.84,
  GBR 1.30 (NI also funds other benefits). Unusable: USA (household contributions recorded as 0: 0.44), ISL
  (contributions set equal to benefits), DNK (0.20: ATP only). Tax-financed basic and means-tested pensions (AUS
  Age Pension, NZ Super, DNK folkepension) are outside table 29 by construction. The ratios are computed here
  from the csv rows, not published. ESSPROS receipts (all functions, 2020) put general-government financing at
  78% in DNK, 62% IRL, 58% NOR, 53% ITA and SWE, 51% FIN, 26% CHE and CZE, 30% NLD; FRA 45%, of which 29% earmarked
  taxes (CSG).

### A.5 Smaller surprises

- PaG 2021 figure 3.3's subtitle says 2018; its values are table 3.2's 2020 values.
- Table 8.1 omits IRL, ESP, GBR (no pension-specific contribution); table 8.2's rates cover all social insurance.
- UK SOCX "flat rate retirement pension" (4.59) includes the earnings-related additional State Pension; IRL's
  "Dept of Social Protection" line (0.29), classed means-tested here, is not described further in SOCX.
- Minimum-income benefits for the elderly sit in old-age "other cash" (TP113), not TP111: FRA's ASPA (0.15), the UK's
  Pension Credit (0.23), the US SSI for the aged (0.03), DEU's old-age social assistance (0.07).

## F. First-pass θ measures (2026-10-30; `logs/thetaTau_measures.py`, run with the repo root as argument)

Not a choice, a comparison. Public 2pt: 2 − 1/I on table 4.2's public tier (NZ read at 0.6 AW). Public 3pt: least-squares
slope of the public pension on earnings at 0.5, 1, 2 AW, θ = c/(a+c). 1 − P/100: PaG 2013 progressivity index, national
distribution, **mandatory incl. private, 2012 rules**. SOCX: 1 − (basic + means-tested + targeted)/(public old-age cash
less government employees), 2019; blind to flat parts inside one programme (IRL, CZE, GBR's S2P), so a check only.

| | paper | public 2pt | public 3pt | 1−P/100 | SOCX |
|---|---|---|---|---|---|
| θ = 1 in paper: AUT FRA ESP | 1 | 1 | 0.75 0.85 0.90 | 0.72 0.70 0.76 | 0.98 0.98 0.94 |
| θ = 1 in paper: FIN HUN ITA | 1 | 1 | 1 | 0.98 1.00 0.99 | 0.93 0.98 0.96 |
| private tier: NLD GBR NZL | 0.95 0.56 0.34 | 0 | 0 | 0.96 0.15 0.00 | ~0 |
| means-tested vs private: AUS DNK ISL | 0 0.44 0.59 | <0 | −1.33 −0.33 −1.33 | 0.28 0.43 – | 0.05 0.10 0.00 |
| CHE SWE NOR | 0.80 0.85 0.68 | 0.49 0.80 0.63 | 0.22 0.40 0.31 | 0.32 1.19 0.56 | 0.98 0.96 0.64 |
| USA | 0.73 | 0.73 | 0.55 | 0.57 | 0.99 |

Government-employee pensions inside SOCX public spending (τ's target), % GDP 2019: FIN 3.78, ITA 3.18, GRC 2.61,
GBR 2.50, AUT 2.30, USA 2.24, FRA 2.07; θ is measured on private-sector rules. Gaps that bear on the six θ = 1
countries: ITA's integrazione al minimo (2016 count only), PRT's top-up, AUT/FRA/HUN top-up spending.

## G. Top-up spending (2026-10-30; `data/oecd26_topups.csv`, written by `python/paper/oecd26Topups.py`, which prints s)

s = 2020 spending on the top-ups and tested benefits that PaG 2021's full-career worker at 0.5 AW does not reach,
over SOCX public old-age and survivors cash (TP01, τ's S), both in millions of national currency. "Reached" compares
PaG's public pension at 0.5 AW (table 4.2, men) with the benefit's 2020 level (table 3.2), both in % of AW. Raw files:
`logs/thetaTau_raw/topups/`; every typed value is checked against its file's text. Nothing interpolated.

| | in s, 2020 (millions NC) | s | inside SOCX old age | conf. | alternatives, caveats |
|---|---|---|---|---|---|
| ITA | integrazione al minimo 7,024 + maggiorazioni sociali on IVS pensions 1,505 + assegno/pensione sociale with its maggiorazioni 4,849 + importo aggiuntivo 82 | 0.046 | part: integrazione, maggiorazioni paid with the INPS pensions (no line of their own); assegno yes [380.10.1.1.1.15] | medium | upper bound: integrazioni include invalidity pensions (no split found). Table 5.6's 2020 maggiorazioni (2,633) add civil-invalidity ones: 0.050. Quattordicesima (1,403) is reached (limit 2 × minimum, 45.4% AW) and left out; with it 0.051 |
| FRA | minima de pension 8,530 (MiCo, Miga, PMR, CD; 6,005,400 beneficiaries) + minimum vieillesse 3,530 (635,300) | 0.036 | yes: minima inside the pension programmes; ASPA/ASV in TP113 [250.10.1.1.3.2-3] | high | without the civil-service Miga (1,590): 0.031; CNAV MiCo (6,100) + minimum vieillesse: 0.029; EIR's minimum vieillesse 3,810 (= SOCX's 0.165% of GDP): 0.037 |
| AUT | Ausgleichszulage on old-age and survivors pensions 861.3 (SOCX lines) | 0.016 | part: invalidity AZ (183.8) is incapacity | high | all AZ, federal reimbursement 1,052.2 (2019: 979.8): 0.019. SOCX's three lines sum to 1,045.2 |
| DEU | SOCX old-age "Other cash benefits (Social assistance)" 1,810.7 [276.10.1.1.3.5] | 0.005 | part | high | Grundsicherung im Alter, age part ≈ 3,300 (press, via a government answer): 0.009; all of SGB XII ch. 4 with reduced earning capacity, net 7,561.7 (2019: 6,868.5): 0.020. SOCX spreads ch. 4 over old age, incapacity [276.10.3.1.5.19] and other social policy areas [276.10.9.1.1.1] |
| BEL | GRAPA/IGO 729.2 (SOCX) | ≥ 0.014 | yes [56.10.1.1.1.15] | high | lower bound: minimum-pension supplement not found. 2019: Court of Audit 593.7, SOCX 605.9 |
| PRT | complementos sociais 1,927 + CSI 212 (171,768 recipients) + pensões sociais 118 | 0.082 | part: complementos inside the pension programmes, invalidity part in incapacity; CSI [620.10.1.1.3.14] and social pensions yes | high | upper bound: complementos include invalidity. Without them 0.012. CGA not covered. 2019: 1,910, 216, 121 |
| NOR | none | 0 | part (inside basic and supplementary pension) | | reached: 0.5 AW pension 27.1% AW below the guarantee level 30.5%, and RR 54.1 at 0.5 AW against 39.4 at 1, so it is in the slope. 138,200 minimum pensioners (December 2020); spending not found |
| POL | dopłata to the minimum pension 180.8 (2021, nearest year; new-system pensions only) | 0.001 | part | low | reached with 2020 values (minimum 23.6% AW above the 15.9% AW pension), not in PaG's projection (RR 31.8 at 0.5 AW, 30.6 at 1): if "reached" rules, s = 0. Old-system top-ups unpublished; 221,000 old-age pensions at the minimum (March 2020) |
| LUX | none found | gap | part (inside the old-age pension) | | 16.4% of pensions had the complement in 2023, 19.5% in 2009 (ministry, press) |
| HUN | minimum top-up ≤ 4,068 (0.61% of 65+ × HUF 28,500 × 12) + SOCX means-tested old-age cash 6,115 | ≤ 0.003 | part; yes | low | confirms negligible: the minimum is 6.8% AW, the 0.5 AW pension 31.2% |

- **Not reached, by thin margins:** BEL minimum pension 32.5% AW against 33.7%; FRA ASPA 28.4 against 30.1; DEU Grundsicherung
  19.3 against 23.2. FRA's MiCo majoré (EUR 702.54, 22.1% AW) tops up the CNAV pension alone, which PaG does not publish:
  50% of a 0.5 AW reference wage is 25.0% AW, less once PaG's price revaluation of past wages lowers the reference wage.
- **Reproduces / does not.** ITA: the assegno sociale is 0.29% of GDP with its maggiorazioni (4,849) and 0.29% without (4,803),
  so the 0.30 found earlier stands to rounding; it equals SOCX's means-tested line. The X report revises 2020's integrazioni to
  7,030.1. AUT: SOCX's AZ lines match the federal reimbursement within 1%; BEL: SOCX's GRAPA is 2% above the Court of
  Audit's 2019 figure. DEU: PaG table 3.2 prints 0.5% of 65+ on Grundsicherung; Destatis 3.1% (564,110).
- **Gaps:** BEL minimum-pension supplement (SFP reports not reached); LUX 2019-20 (IGSS pages 404); NOR spending
  (regjeringen.no 403); POL 2019-20 and old-system top-ups; PRT complemento counts and the invalidity split; ITA integrazioni
  by pension category; DEU age split from an official source; FRA 2019 levels (DREES's www host serves a bot check; the
  2020 files came from the Wayback Machine); AUT recipients from the Dachverband (2020: 198,378 from the press).
