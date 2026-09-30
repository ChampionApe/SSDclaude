r""" Stage (0) for figure 1 (fig:US:OECDdata): the cross-country data behind it, and its builder.

Run:  .venv\Scripts\python.exe python\paper\oecdFigure1.py [--force]   fetch -> data/oecdFigure1{,_sources}.csv
      .venv\Scripts\python.exe python\paper\build.py --only OECDdata     the figure and oecdCorrelations.csv

`main` is the only code here that touches the network, and it skips when both csv exist; `figure` reads
the committed csv alone. One row per country: the 29 OECD members before 2000 that the introduction's
footnote lists, 2020 or the nearest year in 2018-2022 (`_nearest`), never interpolated.

Every variable is delivered in the concept the footnote names AND in the concept that reproduces the
figure the paper carries (`eps_*`, read off `writing/Paper/Figs/OECDdata.eps`). Which one the figure
plots is the gate-1 decision, made in `PLOT` and nowhere else. `data/oecdFigure1_sources.csv` sources
every column: provider, dataset id, series, vintage, years used per country, url, retrieval date.
"""
import os, io, re, sys, json, zipfile, argparse, datetime, itertools, urllib.request
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import datasets as D
from figures import plt, pe, SERIES, INK, _panel, _save

OUT     = os.path.join(C.DATA, 'oecdFigure1.csv')
SOURCES = os.path.join(C.DATA, 'oecdFigure1_sources.csv')
CORR    = os.path.join(C.PAPERDIR, 'oecdCorrelations.csv')
EPS     = os.path.join(C.PAPERTEX, 'Figs', 'OECDdata.eps')
YEAR, WINDOW, BASE = 2020, 2, 1990

# (footnote name, ISO3, ISO2), in the footnote's order.
COUNTRIES = [('Australia', 'AUS', 'AU'), ('Austria', 'AUT', 'AT'), ('Belgium', 'BEL', 'BE'),
             ('Canada', 'CAN', 'CA'), ('Czech Republic', 'CZE', 'CZ'), ('Denmark', 'DNK', 'DK'),
             ('Finland', 'FIN', 'FI'), ('France', 'FRA', 'FR'), ('Germany', 'DEU', 'DE'),
             ('Greece', 'GRC', 'GR'), ('Hungary', 'HUN', 'HU'), ('Iceland', 'ISL', 'IS'),
             ('Ireland', 'IRL', 'IE'), ('Italy', 'ITA', 'IT'), ('Japan', 'JPN', 'JP'), ('Korea', 'KOR', 'KR'),
             ('Luxembourg', 'LUX', 'LU'), ('Mexico', 'MEX', 'MX'), ('Netherlands', 'NLD', 'NL'),
             ('New Zealand', 'NZL', 'NZ'), ('Norway', 'NOR', 'NO'), ('Poland', 'POL', 'PL'),
             ('Portugal', 'PRT', 'PT'), ('Spain', 'ESP', 'ES'), ('Sweden', 'SWE', 'SE'),
             ('Switzerland', 'CHE', 'CH'), ('Turkey', 'TUR', 'TR'), ('United Kingdom', 'GBR', 'GB'),
             ('United States', 'USA', 'US')]
ISO3 = [c[1] for c in COUNTRIES]

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/124.0 Safari/537.36'}
SDMX = 'https://sdmx.oecd.org/public/rest/data/'
URL = {'socx': SDMX + 'OECD.ELS.SPD,DSD_SOCX_AGG@DF_SOCX_AGG,1.0/.A.SOCX.PT_B1GQ.ES10..TP01.'
                      '?startPeriod=2018&endPeriod=2022&format=csvfilewithlabels',
       'pop':  SDMX + 'OECD.ELS.SAE,DSD_POPULATION@DF_POP_HIST,1.0/.POP.PS._T._T.H'
                      '?startPeriod=1990&endPeriod=2020&format=csvfilewithlabels',
       'wb':   'https://api.worldbank.org/v2/country/' + ';'.join(ISO3)
               + '/indicator/SP.POP.TOTL?date=1990:2020&format=json&per_page=5000',
       'pag':  'https://stat.link/b2f0ws',
       'wiid': 'https://www.wider.unu.edu/sites/default/files/WIID/WIID-08SEP2026.xlsx',
       'wid':  'https://wid.world/bulk_download/wid_all_data.zip'}

# The concepts the footnote names, and the ones that reproduce the published EPS. No source found
# reproduces the EPS Gini; gini_widPretax is the nearest (see the sources csv).
NAMED  = {'spending': 'pensionSpending', 'growth': 'popGrowth', 'index': 'bbIndex', 'gini': 'gini'}
AS_EPS = {'spending': 'pensionSpending_cashInKind', 'growth': 'popGrowth_wb', 'index': 'bbIndex_mean',
          'gini': 'gini_widPretax'}
EPSCOL = {'spending': 'eps_pensionSpending', 'growth': 'eps_popGrowth', 'index': 'eps_bbIndex',
          'gini': 'eps_gini'}
PLOT = NAMED                     # gate 1 (notes/paper_presentationPlan.md §8): NAMED or AS_EPS
LABEL = {'pensionSpending': 'Pension spending, % of GDP',
         'pensionSpending_cashInKind': 'Old-age spending, % of GDP',
         'popGrowth': 'Population 2020 / 1990', 'popGrowth_wb': 'Population 2020 / 1990',
         'bbIndex': 'Bismarckian index', 'bbIndex_mean': 'Bismarckian index',
         'gini': 'Gini, disposable income', 'gini_widPretax': 'Gini, pre-tax income',
         'gini_wiidMarket': 'Gini, market income'}
HIGHLIGHT = {'USA': 'US', 'GBR': 'UK', 'FRA': 'FR'}   # the economies sections 6-7 calibrate


# --- fetching (network) ----------------------------------------------------------------------------------
def _get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers = UA), timeout = 300).read()


def _nearest(s, target = YEAR, window = WINDOW):
    """ (value, year) at the year nearest `target` within +-window, ties to the earlier year; (nan, nan)
    when there is none. `s` is indexed by year and must hold one value per year. """
    s = s.dropna()
    s = s[(s.index >= target - window) & (s.index <= target + window)]
    if s.index.duplicated().any():
        raise ValueError('several values for one year: {}'.format(s[s.index.duplicated(keep = False)]))
    if s.empty:
        return np.nan, np.nan
    y = min(s.index, key = lambda t: (abs(t - target), t))
    return float(s.loc[y]), int(y)


def socx():
    """ Public old-age and survivors spending, % of GDP: in cash (C) and cash plus in kind (_T). """
    df = pd.read_csv(io.BytesIO(_get(URL['socx'])))
    out = {c: {} for c in ISO3}
    for code, col in (('C', 'pensionSpending'), ('_T', 'pensionSpending_cashInKind')):
        piv = df[df['SPENDING_TYPE'] == code].pivot(index = 'TIME_PERIOD', columns = 'REF_AREA',
                                                     values = 'OBS_VALUE')
        for c in ISO3:
            out[c][col], out[c][col + '_year'] = _nearest(piv[c]) if c in piv else (np.nan, np.nan)
    return pd.DataFrame(out).T


def population():
    """ Total population in 1990 and 2020 from the OECD and from the World Bank. """
    oecd = pd.read_csv(io.BytesIO(_get(URL['pop']))).pivot(index = 'REF_AREA', columns = 'TIME_PERIOD',
                                                           values = 'OBS_VALUE')
    wb = json.loads(_get(URL['wb']).decode())
    wbDf = pd.DataFrame([(d['countryiso3code'], int(d['date']), d['value']) for d in wb[1]],
                        columns = ['c', 'y', 'v']).pivot(index = 'c', columns = 'y', values = 'v')
    out = pd.DataFrame({'pop1990_oecd': oecd[BASE], 'pop2020_oecd': oecd[YEAR],
                        'pop1990_wb': wbDf[BASE], 'pop2020_wb': wbDf[YEAR]}).reindex(ISO3).astype(float)
    out['popGrowth'] = out['pop2020_oecd']/out['pop1990_oecd']
    out['popGrowth_wb'] = out['pop2020_wb']/out['pop1990_wb']
    return out, wb[0].get('lastupdated')


def pag2021():
    """ Gross replacement rates at 0.5 and 1.0 times average earnings, mandatory schemes, rules in 2020
    (Pensions at a Glance 2021, table 4.1), men and women, at the one decimal the table publishes: the
    women's figures exist only as rounded text "(59.8)", and the published figure is what was plotted. """
    raw = pd.read_excel(io.BytesIO(_get(URL['pag'])), sheet_name = 'Table 4.1', header = None)
    par = lambda v: float(re.fullmatch(r'\(([\d.]+)\)', v.strip()).group(1)) if isinstance(v, str) and v.strip() else np.nan
    rows = {}
    for o in (0, 10):                                    # the table is printed in two column blocks
        for i in range(5, raw.shape[0]):
            name, v05 = raw.iat[i, o], raw.iat[i, o + 3]
            if isinstance(name, str) and isinstance(v05, (int, float)) and pd.notna(v05):
                rows[name.strip().rstrip('*')] = {'grr050_men': round(float(v05), 1),
                                                  'grr100_men': round(float(raw.iat[i, o + 5]), 1),
                                                  'grr050_women': par(raw.iat[i, o + 4]),
                                                  'grr100_women': par(raw.iat[i, o + 6])}
    df = pd.DataFrame(rows).T.reindex([c[0] for c in COUNTRIES]).astype(float)
    df.index = ISO3
    for s in ('050', '100'):                             # "women where different"
        df['grr{}_women'.format(s)] = df['grr{}_women'.format(s)].fillna(df['grr{}_men'.format(s)])
    df['bbIndex'] = df['grr100_men']/df['grr050_men']
    df['bbIndex_women'] = df['grr100_women']/df['grr050_women']
    df['bbIndex_mean'] = (df['bbIndex'] + df['bbIndex_women'])/2
    return df


def wiid():
    """ WIID Ginis on the 0-1 scale: the observation WIID itself selects for its Companion
    (wiidcompanion = Yes; disposable income), and OECD.Stat's market income as the pre-tax reading.
    Also returns the range of every US observation for the year, for the sources note. """
    w = pd.read_excel(io.BytesIO(_get(URL['wiid'])),
                      usecols = ['id', 'c3', 'year', 'gini', 'resource_detailed', 'scale_detailed',
                                 'source_detailed', 'source_comments', 'wiidcompanion'])
    w = w[w['c3'].isin(ISO3)]
    out = {}
    for c in ISO3:
        comp = w[(w['c3'] == c) & (w['wiidcompanion'] == 'Yes')].set_index('year')
        g, y = _nearest(comp['gini'])
        r = comp.loc[y] if pd.notna(y) else None
        mkt = w[(w['c3'] == c) & (w['source_detailed'] == 'OECD.Stat') & (w['resource_detailed'] == 'Market income')
                & (w['scale_detailed'] == 'Square root')]
        # OECD IDD carries an old and a new income definition in a break year (JPN 2018): keep the new.
        mkt = mkt.sort_values('source_comments', key = lambda s: s.eq('Old series')).drop_duplicates('year')
        gm, ym = _nearest(mkt.set_index('year')['gini'])
        out[c] = {'gini': g/100, 'gini_year': y, 'gini_wiidId': np.nan if r is None else int(r['id']),
                  'gini_source': None if r is None else '{}; {}; {}'.format(
                      r['source_detailed'], r['resource_detailed'], r['scale_detailed']),
                  'gini_wiidMarket': gm/100, 'gini_wiidMarket_year': ym}
    us = w.loc[(w['c3'] == 'USA') & (w['year'] == YEAR), 'gini']/100
    return pd.DataFrame(out).T, (float(us.min()), float(us.max()))


class _RemoteFile(io.RawIOBase):
    """ Seekable read-only view of a remote file through HTTP range requests, so zipfile can pull single
    members of the WID bulk archive (~0.9 GB) without downloading the whole of it. """
    def __init__(self, url):
        self.url, self.pos = url, 0
        h = urllib.request.urlopen(urllib.request.Request(url, method = 'HEAD', headers = UA), timeout = 60)
        self.size, self.modified = int(h.headers['Content-Length']), h.headers.get('Last-Modified')

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos

    def seek(self, off, whence = 0):
        self.pos = (off, self.pos + off, self.size + off)[whence]
        return self.pos

    def readinto(self, b):
        n = min(len(b), self.size - self.pos)
        if n <= 0:
            return 0
        r = urllib.request.urlopen(urllib.request.Request(self.url, headers = dict(
            UA, Range = 'bytes={}-{}'.format(self.pos, self.pos + n - 1))), timeout = 300)
        if r.status != 206:                  # a server ignoring Range would stream the whole archive
            raise IOError('{} ignored the range request (HTTP {})'.format(self.url, r.status))
        data = r.read()
        b[:len(data)] = data
        self.pos += len(data)
        return len(data)


def wid():
    """ WID pre-tax national income Gini (gptincj992: equal-split adults, 20+), 2020 or nearest. """
    f = _RemoteFile(URL['wid'])
    z = zipfile.ZipFile(io.BufferedReader(f, buffer_size = 1 << 20))
    out = {}
    for _, c3, c2 in COUNTRIES:
        with z.open('WID_data_{}.csv'.format(c2)) as fh:
            d = pd.read_csv(fh, sep = ';', usecols = ['variable', 'percentile', 'year', 'value'])
        s = d[(d['variable'] == 'gptincj992') & (d['percentile'] == 'p0p100')].set_index('year')['value']
        out[c3] = dict(zip(('gini_widPretax', 'gini_widPretax_year'), _nearest(s)))
        print('  WID {} {:.4f}'.format(c2, out[c3]['gini_widPretax']), flush = True)
    return pd.DataFrame(out).T, f.modified


# --- the published figure (a local file) -------------------------------------------------------------------
def epsReadings(path = EPS):
    """ The four variables as the Stata EPS plots them: each marker centre mapped through its panel's axis
    ticks (resolution ~1e-4 of the axis unit). Stata writes markers in dataset order, which is ISO3
    alphabetical here; that assignment matches SOCX, the World Bank and PaG 2021 to their rounding for
    all 29 countries, which is how it was identified. Panels: spending|growth, spending|Gini,
    index|growth, index|Gini. """
    panels, tick = [], None
    for s in (l.strip() for l in open(path, encoding = 'latin-1')):
        m = re.match(r'(\d+) (\d+) (\d+) (\d+) 0 0 Srect$', s)
        if m:
            panels.append({'box': tuple(map(int, m.groups())), 'pts': [], 'x': [], 'y': []})
            continue
        if not panels:
            continue
        p = panels[-1]
        if (m := re.match(r'(\d+) (\d+) \d+ 0 1 Scc$', s)):
            p['pts'].append((int(m[1]), int(m[2])))
        elif (m := re.match(r'(\d+) (\d+) (\d+) (\d+) Sln$', s)):
            a, b, c, d = map(int, m.groups())
            x0, y0 = p['box'][:2]
            tick = ('y', b) if (b == d and a == x0 and c < a) else ('x', a) if (a == c and b == y0 and d < b) else None
        elif tick and (m := re.match(r'\((-?[\d.]+)\) Stxtl$', s)):
            p[tick[0]].append((tick[1], float(m[1])))
            tick = None

    def axis(p, k, j):
        a, b = np.polyfit(*zip(*p[k]), 1)
        return a*np.array([q[j] for q in p['pts']], float) + b

    if len(panels) != 4 or any(len(p['pts']) != len(ISO3) for p in panels):
        raise ValueError('{}: expected 4 panels of {} markers'.format(path, len(ISO3)))
    return pd.DataFrame({'eps_pensionSpending': axis(panels[0], 'y', 1), 'eps_popGrowth': axis(panels[0], 'x', 0),
                         'eps_gini': axis(panels[1], 'x', 0), 'eps_bbIndex': axis(panels[2], 'y', 1)},
                        index = sorted(ISO3)).reindex(ISO3).round(4)


# --- the csv pair ------------------------------------------------------------------------------------------
def _years(s, target = YEAR):
    """ '2020 (29 of 29)', or with the exceptions: '2020 (22 of 29); 2019: CHE, DEU; none in 2018-2022: ISL'. """
    s = pd.to_numeric(s.reindex(ISO3))
    parts = ['{} ({} of {})'.format(target, int((s == target).sum()), len(s))]
    for y in sorted(set(s.dropna()) - {target}):
        parts.append('{}: {}'.format(int(y), ', '.join(s.index[s == y])))
    if s.isna().any():
        parts.append('none in {}-{}: {}'.format(target - WINDOW, target + WINDOW, ', '.join(s.index[s.isna()])))
    return '; '.join(parts)


def _gaps(df, col, ref, tol):
    """ 'POL 0.962 vs 0.848, MEX ...': the countries where `col` misses `ref` by more than `tol`. """
    if df[ref].isna().all():
        return 'EPS not read'
    d = (df[col] - df[ref]).abs().sort_values(ascending = False)
    return ', '.join('{} {:.3f} vs {:.3f}'.format(c, df.at[c, col], df.at[c, ref]) for c in d.index[d > tol]) or 'none'


def sources(df, retrieved, wbUpdated, usRange, widModified):
    """ One row per data column (or group of columns sharing a source). """
    inKind = (df['pensionSpending_cashInKind'] - df['pensionSpending']).sort_values(ascending = False)
    w = df[['gini_widPretax', 'eps_gini']].astype(float).dropna()
    wd = (w['gini_widPretax'] - w['eps_gini']).abs()
    socxDs = 'Social Expenditure Database, OECD.ELS.SPD:DSD_SOCX_AGG@DF_SOCX_AGG(1.0)'
    rows = [
        ('pensionSpending', 'OECD', socxDs, 'public (ES10), old age and survivors (TP01), in cash (C), % of GDP',
         'Data Explorer', _years(df['pensionSpending_year']), URL['socx'],
         "The OECD's 'pension spending': cash expenditure on old-age and survivors pensions (Pensions at a "
         'Glance measure PEP to its rounding). Misses the EPS by up to {:.2f} p.p.'.format(
             (df['pensionSpending'] - df['eps_pensionSpending']).abs().max())),
        ('pensionSpending_cashInKind', 'OECD', socxDs, 'as pensionSpending, cash plus in kind (_T)',
         'Data Explorer', _years(df['pensionSpending_cashInKind_year']), URL['socx'],
         'Reproduces eps_pensionSpending (max |diff| {:.3f}). The in-kind part is services to the elderly '
         '(care, home help), largest in {}.'.format(
             (df['pensionSpending_cashInKind'] - df['eps_pensionSpending']).abs().max(),
             ', '.join('{} {:.2f}'.format(c, v) for c, v in inKind.head(4).items()))),
        ('pop1990_oecd, pop2020_oecd, popGrowth', 'OECD',
         'Historical population data, OECD.ELS.SAE:DSD_POPULATION@DF_POP_HIST(1.0)',
         'POP, persons, both sexes, all ages, historical; popGrowth = pop2020/pop1990', 'Data Explorer',
         '1990 and 2020 (29 of 29)', URL['pop'],
         'France: the series adds the overseas departments from 1991, so its ratio ({:.3f}) is not on a '
         'constant territory (World Bank {:.3f}). Misses the EPS: {}.'.format(
             df.at['FRA', 'popGrowth'], df.at['FRA', 'popGrowth_wb'], _gaps(df, 'popGrowth', 'eps_popGrowth', 5e-4))),
        ('pop1990_wb, pop2020_wb, popGrowth_wb', 'World Bank', 'World Development Indicators',
         'SP.POP.TOTL; popGrowth_wb = pop2020/pop1990', 'API lastupdated ' + str(wbUpdated), '1990 and 2020 (29 of 29)',
         URL['wb'], 'Reproduces eps_popGrowth except {} (an earlier WDI estimate of the 2020 population).'.format(
             _gaps(df, 'popGrowth_wb', 'eps_popGrowth', 5e-4))),
        ('grr050_men, grr100_men, grr050_women, grr100_women', 'OECD', 'Pensions at a Glance 2021, table 4.1',
         'gross pension replacement rate at 0.5 and 1.0 times average earnings, mandatory schemes, % of '
         'individual earnings, one decimal as published; women = men where the table gives none',
         'StatLink xlsx "Version 1 - Last updated: 08-Dec-2021"', 'pension rules in 2020 (29 of 29)', URL['pag'],
         'The OECD Data Explorer dataflows DSD_PAG@DF_PRR and DSD_PAG@DF_PAG now hold only 2024 (Pensions at '
         'a Glance 2025); the publication StatLink still serves the 2020 vintage.'),
        ('bbIndex', 'derived', 'Pensions at a Glance 2021, table 4.1', 'grr100_men / grr050_men', '',
         '2020 (29 of 29)', URL['pag'], 'Men: the table headline and the concept of section 6. Misses the EPS: '
         + _gaps(df, 'bbIndex', 'eps_bbIndex', 5e-4) + '.'),
        ('bbIndex_women', 'derived', 'Pensions at a Glance 2021, table 4.1', 'grr100_women / grr050_women', '',
         '2020 (29 of 29)', URL['pag'], ''),
        ('bbIndex_mean', 'derived', 'Pensions at a Glance 2021, table 4.1', '(bbIndex + bbIndex_women) / 2', '',
         '2020 (29 of 29)', URL['pag'], 'Reproduces eps_bbIndex (max |diff| {:.4f}).'.format(
             (df['bbIndex_mean'] - df['eps_bbIndex']).abs().max())),
        ('gini, gini_year, gini_wiidId, gini_source', 'UNU-WIDER',
         'World Income Inequality Database (WIID), version 8 September 2026, doi 10.35188/UNU-WIDER/WIID-080926',
         'the observation WIID flags for its Companion (wiidcompanion = Yes): disposable income, persons, per '
         'capita except where gini_source says otherwise; 0-1 scale', 'version 8 Sep 2026', _years(df['gini_year']),
         URL['wiid'], 'gini_wiidId is the WIID row id. The EPS Gini is not a WIID series: every WIID US value for '
         '{} lies in {:.3f}-{:.3f}, the EPS plots {:.4f}.'.format(YEAR, usRange[0], usRange[1], df.at['USA', 'eps_gini'])),
        ('gini_wiidMarket, gini_wiidMarket_year', 'UNU-WIDER', 'WIID, version 8 September 2026',
         'source OECD.Stat (Income Distribution Database), market income, square-root scale, persons; 0-1 scale',
         'version 8 Sep 2026', _years(df['gini_wiidMarket_year']), URL['wiid'],
         'Before taxes and transfers; retirees without market income count at zero.'),
        ('gini_widPretax, gini_widPretax_year', 'World Inequality Lab', 'World Inequality Database (WID), bulk download',
         'gptincj992, p0p100: Gini of pre-tax national income, equal-split adults (20+)',
         'Last-Modified ' + str(widModified), _years(df['gini_widPretax_year']), URL['wid'],
         'EPS not read' if w.empty else
         'Nearest to eps_gini (correlation {:.2f}, mean |diff| {:.3f}, max {:.3f} {}) but not equal to it: '
         'WID revises back years at each update.'.format(w.corr().iloc[0, 1], wd.mean(), wd.max(), wd.idxmax())),
        ('eps_pensionSpending, eps_popGrowth, eps_bbIndex, eps_gini', 'read off the paper',
         'writing/Paper/Figs/OECDdata.eps (Stata; in the repo since 2026-08-23)',
         'marker centres mapped through the axis ticks; markers in ISO3 order', '', 'as plotted',
         'writing/Paper/Figs/OECDdata.eps', 'Resolution about 1e-4 of each axis unit. All 29 countries are '
                                             'plotted in all four panels.')]
    out = pd.DataFrame(rows, columns = ['column', 'provider', 'dataset', 'series', 'vintage', 'years', 'url', 'note'])
    out.insert(6, 'retrieved', [retrieved if r[1] not in ('derived', 'read off the paper') else '' for r in rows])
    return out


def collect():
    retrieved = datetime.date.today().isoformat()
    print('fetching OECD SOCX, OECD and World Bank population, PaG 2021, WIID ...', flush = True)
    sp = socx()
    pop, wbUpdated = population()
    pag = pag2021()
    wi, usRange = wiid()
    print('fetching WID (29 members of the bulk archive, ~130 MB) ...', flush = True)
    wd, widModified = wid()
    df = pd.concat([sp, pop, pag, wi, wd], axis = 1).reindex(ISO3)
    df = df.apply(lambda s: s if s.name == 'gini_source' else pd.to_numeric(s))
    for col in df.columns:                  # counts and years as integers, NaN kept (never zero-filled)
        if col.endswith('_year') or col.startswith(('pop1990', 'pop2020')) or col == 'gini_wiidId':
            df[col] = df[col].round().astype('Int64')
    if os.path.exists(EPS):
        df = df.join(epsReadings())
    else:
        print('  {} not found: eps_* columns left empty'.format(os.path.relpath(EPS, C.REPO)))
        for c in EPSCOL.values():
            df[c] = np.nan
    df.insert(0, 'country', [c[0] for c in COUNTRIES])
    df.index.name = 'iso3'
    return df, sources(df, retrieved, wbUpdated, usRange, widModified)


# --- stage (iii): the figure and the correlations, from the committed csv only -------------------------------
def correlations(df):
    """ Pairwise Pearson and Spearman correlations of the four variables, pairwise complete, per concept set. """
    from scipy import stats
    rows = []
    for variant, cols in (('named', NAMED), ('asEPS', AS_EPS), ('epsReadings', EPSCOL)):
        for a, b in itertools.combinations(('spending', 'growth', 'index', 'gini'), 2):
            x, y = df[cols[a]].astype(float), df[cols[b]].astype(float)
            ok = x.notna() & y.notna()
            pr, sr = stats.pearsonr(x[ok], y[ok]), stats.spearmanr(x[ok], y[ok])
            rows.append({'variant': variant, 'x': cols[a], 'y': cols[b], 'n': int(ok.sum()),
                         'pearson': round(float(pr[0]), 3), 'pearson_p': round(float(pr[1]), 4),
                         'spearman': round(float(sr[0]), 3), 'spearman_p': round(float(sr[1]), 4)})
    return pd.DataFrame(rows)


# Label positions around a marker: offset in points, alignment. Tried in this order; the first of the best wins.
_SPOTS = [((3, 2), 'left', 'bottom'), ((-3, 2), 'right', 'bottom'), ((3, -2), 'left', 'top'),
          ((-3, -2), 'right', 'top'), ((4, 0), 'left', 'center'), ((-4, 0), 'right', 'center')]


def _labels(ax, x, y, size = 6.5):
    """ Name the HIGHLIGHT countries, each at the spot around its marker whose text box stays inside the
    axes and farthest from every other marker and label. Needs the final layout (draw first). """
    px = ax.figure.dpi/72                                           # pixels per point
    pts = list(ax.transData.transform(np.column_stack([x, y])))
    box = ax.get_window_extent()
    for iso, lab in HIGHLIGHT.items():
        if iso not in x.index:
            continue
        i = x.index.get_loc(iso)
        w, h = 0.65*size*len(lab)*px, size*px                       # the label's rough extent
        def score(spot):
            (ox, oy), ha, va = spot
            x0 = pts[i][0] + ox*px - (w if ha == 'right' else 0)
            y0 = pts[i][1] + oy*px - {'top': h, 'center': h/2, 'bottom': 0}[va]
            if x0 < box.x0 or x0 + w > box.x1 or y0 < box.y0 or y0 + h > box.y1:
                return -np.inf
            return min(np.hypot(max(x0 - p[0], 0, p[0] - x0 - w), max(y0 - p[1], 0, p[1] - y0 - h))
                       for j, p in enumerate(pts) if j != i)
        (ox, oy), ha, va = max(_SPOTS, key = score)
        ax.annotate(lab, (x[iso], y[iso]), xytext = (ox, oy), textcoords = 'offset points', ha = ha, va = va,
                    fontsize = size, color = INK['primary'], zorder = 5,
                    path_effects = [pe.withStroke(linewidth = 2, foreground = '#fcfcfb')])
        pts.append(pts[i] + np.array([ox*px + (w/2 if ha == 'left' else -w/2), oy*px]))   # later labels avoid it


def figure(plot = None):
    r""" Figure \ref{fig:US:OECDdata}, 2x3: rows are spending and the Bismarckian index, columns population
    growth and the Gini; the third column holds spending against the index (the size-design relation of
    sec:esc) above the legend. Equal panels keep one aspect ratio, so slopes compare across panels.
    Also writes results/paper/oecdCorrelations.csv. """
    plot = PLOT if plot is None else plot
    df = pd.read_csv(D._need(OUT), index_col = 'iso3')
    os.makedirs(C.PAPERDIR, exist_ok = True)
    correlations(df).to_csv(CORR, index = False)

    fig, axes = plt.subplots(2, 3, figsize = (5.91, 3.9), constrained_layout = True)
    cells = [(0, 0, 'growth', 'spending'), (0, 1, 'gini', 'spending'), (0, 2, 'index', 'spending'),
             (1, 0, 'growth', 'index'), (1, 1, 'gini', 'index')]
    hi = df.index.isin(list(HIGHLIGHT))
    ns, points = set(), []
    for r, c, xv, yv in cells:
        ax = axes[r, c]
        _panel(ax, '', '', titlesize = 8, labelsize = 7)
        x, y = df[plot[xv]].astype(float), df[plot[yv]].astype(float)
        ok = x.notna() & y.notna()
        ns.add(int(ok.sum()))
        points.append((ax, x[ok], y[ok]))
        for mask, colour, z in ((ok & ~hi, SERIES[0], 3), (ok & hi, SERIES[1], 4)):
            ax.plot(x[mask], y[mask], linestyle = 'none', marker = 'o', markersize = 4.2, color = colour,
                    markeredgecolor = '#fcfcfb', markeredgewidth = 0.6, zorder = z)
        if c == 0:
            ax.set_ylabel(LABEL[plot[yv]], color = INK['secondary'], fontsize = 7.5)
        if r == 1 or c == 2:
            ax.set_xlabel(LABEL[plot[xv]], color = INK['secondary'], fontsize = 7.5)
        if yv == 'spending':
            ax.set_ylim(0, max(20, float(y.max()) + 1))
        if yv == 'index':
            ax.set_ylim(0.44, 1.07)
        if xv == 'index':
            ax.set_xlim(0.44, 1.07)
    fig.canvas.draw()                          # fixes the layout, so the label placement sees final axes
    for ax, x, y in points:
        _labels(ax, x, y)

    dot = lambda colour: plt.Line2D([], [], linestyle = 'none', marker = 'o', markersize = 4.2, color = colour,
                                    markeredgecolor = '#fcfcfb', markeredgewidth = 0.6)
    axes[1, 2].axis('off')
    leg = axes[1, 2].legend([dot(SERIES[0]), dot(SERIES[1])],
                            ['OECD members before 2000', 'calibrated in the paper:\nU.S., UK, France'],
                            loc = 'center', frameon = False, fontsize = 7, labelcolor = INK['secondary'],
                            title = ('{} countries in every panel'.format(ns.pop()) if len(ns) == 1
                                     else 'countries per panel: see the footnote'), title_fontsize = 7)
    leg.get_title().set_color(INK['secondary'])
    return _save(fig, 'OECDdata') + [CORR]


def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--force', action = 'store_true', help = 'refetch even if the outputs exist')
    a = p.parse_args()
    if os.path.exists(OUT) and os.path.exists(SOURCES) and not a.force:
        print('up to date: {} (--force to refetch)'.format(os.path.relpath(OUT, C.REPO)))
        return
    df, src = collect()
    df.round(4).to_csv(OUT)
    src.to_csv(SOURCES, index = False)
    print('{}: {} countries, {} columns; sources in {}'.format(
        os.path.relpath(OUT, C.REPO), len(df), df.shape[1], os.path.relpath(SOURCES, C.REPO)))
    for k in NAMED:
        print('  max |diff| against the EPS  {:<16} {:.4f}   {:<27} {:.4f}'.format(
            NAMED[k], (df[NAMED[k]] - df[EPSCOL[k]]).abs().max(),
            AS_EPS[k], (df[AS_EPS[k]] - df[EPSCOL[k]]).abs().max()))


if __name__ == '__main__':
    main()
