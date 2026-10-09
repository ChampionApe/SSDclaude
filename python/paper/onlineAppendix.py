r""" The online appendix: writing/OnlineAppendix, a Quarto book of short pages built from results/paper.

Run:   .venv\Scripts\python.exe python\paper\build.py --site      (calls build())
then:  quarto render writing\OnlineAppendix

The pages (*.qmd, listed in _quarto.yml) are written by hand: the prose, the small titles, the Observable JS cells
of the interactive figures, and an include per exhibit:
  {{< include _generated/exhibits/<id>.qmd >}}        a static figure or table, whole
  {{< include _generated/exhibits/<id>-head.qmd >}}   an interactive figure's number and caption, above its cells,
  {{< include _generated/exhibits/<id>-foot.qmd >}}   and its note and links below them.
This module writes those blocks and everything else the pages read, into _generated/: the figures (svg), the
datasets of the interactive figures and the csvs each exhibit offers (data/), the palette (style.js), the
replication map (rep-map.qmd), the version stamp and the bibliography; and writing/Paper/onlineAppendix.tex, the
paper's \oa macros from the pages' headings (`# B4. Title {#key}`) with every retired key aliased to its page.

EXHIBITS is the registry: id -> the output shown and, where neither the paper nor the output's own tex supplies
them, its caption and note (LaTeX; no number is typed in them). Exhibits are numbered per page in the order the page
includes them (Figure A2.1, Table B4.2); one the paper inputs also carries its number in the paper (main.aux).
Reads results/paper, the output map of REPLICATION.md (`build.py --map`), build.py's source, the paper's tex and
git; imports no model code and runs no builder. A missing output is reported and its block says so, never fatal.
"""
import os, re, sys, json, html, shutil, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as C
import texTable as TT

SITE = os.path.join(C.REPO, 'writing', 'OnlineAppendix')
GEN = os.path.join(SITE, '_generated')
TABLES = os.path.join(C.PAPERDIR, 'Tables')
FIGS = os.path.join(C.PAPERDIR, 'Figs')
DATA = os.path.join(C.PAPERDIR, 'Data')
MACROS = os.path.join(C.PAPERTEX, 'onlineAppendix.tex')
MAPFILE = os.path.join(C.REPO, 'REPLICATION.md')
SITE_URL = 'https://championape.github.io/SSDclaude'
REPO_URL = 'https://github.com/ChampionApe/SSDclaude'


# ---------------------------------------------------------------------------------------------------
# The registry.

class Ex:
    """ One exhibit. kind 'figure' (a static figure of results/paper/Figs), 'table' (a table of
    results/paper/Tables) or 'explorer' (an interactive figure over the dataset `output` of results/paper/Data,
    drawn by the page's OJS cells). `caption`/`note` (LaTeX) stand in where the paper or the table's tex does not
    supply them. """
    def __init__(self, kind, output, caption = None, note = None):
        self.kind, self.output, self.caption, self.note = kind, output, caption, note


E = Ex
EXHIBITS = {
    # A1
    'ARG_LOG_FourInOne': E('figure', 'ARG_LOG_FourInOne',
        caption = r'The equilibrium in 2010 over pension designs $(\epsilon, \theta)$, Argentina',
        note = r'Each point is an economy that has always had that design, at $\rho = 1$. The line is the calibrated '
               r'$\theta$; the markers are the pre-reform $\epsilon$ and the universal level of the reform. The '
               r'savings rate is savings relative to GDP.'),
    # A2
    'ARG_RhoGrid': E('figure', 'ARG_RhoGrid',
        caption = r'The Argentine calibration across the intertemporal elasticity',
        note = r'The parameters solved jointly with the equilibrium path at each $\rho$ of the grid, against the '
               r'same targets, and two predictions of the calibration, the savings rate and the informal savings '
               r'ratio in 2010. $\rho = 1$ is the paper\textquotesingle s calibration.'),
    'ARG_CRRA_LOG': E('figure', 'ARG_CRRA_LOG'),
    'ARG_ReformPaths': E('explorer', 'ARG_ReformPaths',
        caption = r'The reform along the path at one intertemporal elasticity',
        note = r'Levels on the pre-reform path and on the reform path, each economy calibrated at its $\rho$. The '
               r'workweek is normalised so that the pre-reform path reads the observed average workweek in 2010. '
               r'The changes printed under the panels are the two points of figure \ref{fig:ARG:EffectOfCRRA} at '
               r'the chosen $\rho$. The faint lines are $\rho = 1$, the paper\textquotesingle s calibration.'),
    # A3
    'ARG_LeisureCalibration': E('table', 'ARG_LeisureCalibration'),
    'ARG_LeisureRho': E('table', 'ARG_LeisureRho'),
    # B1
    'OECD_RhoGrid': E('figure', 'OECD_RhoGrid',
        caption = r'The calibrations of the U.S., the UK and France across the intertemporal elasticity',
        note = r'The parameters solved jointly with the equilibrium path at each $\rho$ of the grid, against the '
               r'same targets, with $\beta$ calibrated for the U.S.\ and imposed on the UK and France. $\rho = 1$ '
               r'is the paper\textquotesingle s calibration.'),
    # B2
    'OECD_Hosts': E('explorer', 'OECD_Counterfactuals',
        caption = r'What shapes pensions, savings and labor supply in the U.S.\ and the UK',
        note = r'Each bar is the change against the host\textquotesingle s own baseline at the same $\rho$, in 2020. '
               r'In the design row the full colour is $\theta = 0$ and the light tone $\theta = 1$; in the ageing '
               r'row the bar is acute ageing and the tick mild ageing. France\textquotesingle s income groups are cut '
               r'at the host\textquotesingle s income percentiles. Log preferences at $\rho = 1$, CRRA otherwise.'),
    'OECD_Regroupings': E('table', 'OECD_Regroupings'),
    'UKUS_householdheterogeneity': E('table', 'UKUS_householdheterogeneity'),
    'FRUK_householdheterogeneity': E('table', 'FRUK_householdheterogeneity'),
    'OECD_Groupings': E('explorer', 'OECD_Counterfactuals',
        caption = r'The UK at its own and at the U.S.\ income groups',
        note = r'As figure \ref{oa:OECD_Hosts}, for the UK at its own income groups, France cut at the same groups, '
               r'and for the UK regrouped at the U.S.\ income groups, France at its own (the U.S.) groups. Each '
               r'bar is the change against that economy\textquotesingle s own baseline.'),
    # B3
    'OECD_Frisch': E('explorer', 'OECD_Counterfactuals',
        caption = r'The counterfactuals of the U.S.\ across the intertemporal and the Frisch elasticity',
        note = r'As figure \ref{oa:OECD_Hosts}, for the U.S. Across $\xi$ the U.S.\ and France are recalibrated at '
               r'each value under log preferences ($\rho = 1$), the targets unchanged.'),
    # B4
    'OECD_LeisureCalibration': E('table', 'OECD_LeisureCalibration'),
    'OECD_LeisureGroups': E('table', 'OECD_LeisureGroups'),
    'OECD_LeisureRows': E('explorer', 'OECD_Counterfactuals',
        caption = r'The counterfactuals the treatment of the taste for leisure moves',
        note = r'France\textquotesingle s income distribution and leisure preferences under the common $X$ and '
               r'the vector $X_i$, each the change against the baseline of the same calibration and $\rho$. The '
               r'design, ageing and voting rows are the same under the two.'),
    # C1
    'ESC_PathsCountries': E('explorer', 'ESC_Paths',
        caption = r'The baseline path with the design chosen, by country',
        note = r'Log preferences ($\rho = 1$). Each country keeps its own calibration and demography; the cost '
               r'parameter is the U.S.\ one or the country\textquotesingle s own, as selected, and France has no own '
               r'parameter. A design chosen at one date applies from the following one. Open markers are the '
               r'observed designs.'),
    'ESC_PathsReadings': E('explorer', 'ESC_Paths',
        caption = r'The baseline path with the design chosen and with it pinned',
        note = r'Log preferences ($\rho = 1$). Pinned holds the design at the country\textquotesingle s observed '
               r'value throughout, under the same cost.'),
    # C2
    'ESC_Hosts': E('explorer', 'ESC_Counterfactuals',
        caption = r'What shapes the pension design in the U.S.\ and the UK',
        note = r'Each host at its own cost parameter. An open marker is the reading with the design pinned at the '
               r'host\textquotesingle s observed value, a filled one the reading with the design chosen; the design '
               r'is a level, the other outcomes the change against the baseline of the same reading and $\rho$, in '
               r'2020. The vertical line in the design panel is the host\textquotesingle s observed design.'),
    # C3
    'ESC_Costs': E('explorer', 'ESC_Counterfactuals',
        caption = r'The counterfactuals under the two cost specifications, U.S.',
        note = r'As figure \ref{oa:ESC_Hosts}, for the U.S.\ under the paper\textquotesingle s cost and under a cost '
               r'on the design, each calibrated at each $\rho$ (table \ref{table:OA:ESC_CostCalibration}).'),
    'ESC_CostCalibration': E('table', 'ESC_CostCalibration'),
    # C4
    'ESC_Frisch': E('explorer', 'ESC_Counterfactuals',
        caption = r'The endogenous design across the intertemporal and the Frisch elasticity, U.S.',
        note = r'As figure \ref{oa:ESC_Hosts}, for the U.S. Across $\xi$ the model is recalibrated at each value '
               r'under log preferences ($\rho = 1$), the cost parameter included; only acute ageing was run there.'),
    'ESC_PathsParameters': E('explorer', 'ESC_Paths',
        caption = r'The baseline path across the intertemporal and the Frisch elasticity, U.S.',
        note = r'The paper\textquotesingle s cost, recalibrated at each value. Under CRRA preferences the workweek with '
               r'the design pinned is not stored.'),
    # C5
    'ESC_Timing': E('table', 'ESC_Timing'),
    # D1
    'OECDdata': E('figure', 'OECDdata'),
    'OECD_Countries': E('table', 'OECD_Countries'),
    'OECD_Sources': E('table', 'OECD_Sources'),
    'OECD_Correlations': E('table', 'OECD_Correlations'),
    # D2
    'NUM_Stationary': E('table', 'NUM_Stationary'),
    'NUM_Selection': E('table', 'NUM_Selection'),
}

# Keys of the site before 2026-10-09, which drafts of the paper cite: each is defined as an alias of its new page.
OLDKEYS = {'arg-calibration': 'arg-leisure', 'arg-reform': 'arg-ies', 'arg-rho': 'arg-ies', 'arg-rhogrid': 'arg-ies',
           'oecd-us': 'oecd', 'oecd-calibration': 'oecd-regroup', 'oecd-vectorx': 'oecd-leisure',
           'oecd-rhogrid': 'oecd-ies', 'oecd-uk': 'oecd-countries',
           'esc-calibration': 'esc', 'esc-us': 'esc-countries', 'esc-uk': 'esc-countries', 'esc-path': 'esc-paths',
           'esc-scale': 'esc-costs', 'data-countries': 'data', 'data-correlations': 'data',
           'num-stationary': 'num', 'num-selection': 'num'}


# ---------------------------------------------------------------------------------------------------
# Small helpers.

def read(path):
    with open(path, encoding = 'utf-8', errors = 'replace') as f:
        return f.read()


def write(path, text):
    """ Writes only when the content changed, so a rebuild leaves untouched files untouched. """
    os.makedirs(os.path.dirname(path), exist_ok = True)
    if os.path.exists(path) and read(path) == text:
        return False
    with open(path, 'w', encoding = 'utf-8', newline = '\n') as f:
        f.write(text)
    return True


def copy(src, dest):
    os.makedirs(os.path.dirname(dest), exist_ok = True)
    if not (os.path.exists(dest) and os.path.getmtime(dest) >= os.path.getmtime(src)
            and os.path.getsize(dest) == os.path.getsize(src)):
        shutil.copy2(src, dest)


def uncomment(text):
    return '\n'.join(l[:TT.commentStart(l)] if TT.commentStart(l) is not None else l for l in text.split('\n'))


def git(*args):
    try:
        return subprocess.run(['git', '-C', C.REPO] + list(args), capture_output = True, text = True,
                              check = True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


def plain(tex):
    """ A short piece of LaTeX (a title, a caption) as plain unescaped text. """
    return html.unescape(re.sub('<[^>]+>', '', TT.inline(tex or '', TT.Context())))


# ---------------------------------------------------------------------------------------------------
# What the paper says: which exhibits it inputs, its figures' captions and notes, its numbers.

class Paper:
    def __init__(self):
        root = C.PAPERTEX
        self.files = {}
        for d in ('Sections', 'Appendix'):
            for f in sorted(os.listdir(os.path.join(root, d))):
                if f.endswith('.tex'):
                    self.files[d + '/' + f] = uncomment(read(os.path.join(root, d, f)))
        self.uses = {}                                   # output name -> [tex files that input it]
        for rel, text in self.files.items():
            for m in re.finditer(r'\\input\s*\{Tables/([^}]+)\}', text):
                self.uses.setdefault(m.group(1).strip(), []).append(rel)
            for m in re.finditer(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{Figs/([^}.]+)(?:\.\w+)?\}', text):
                self.uses.setdefault(m.group(1).strip(), []).append(rel)
        self.sections = {}                               # label -> (title, file)
        for rel, text in self.files.items():
            for m in re.finditer(r'\\(section|subsection)\*?\s*\{', text):
                title, j = TT.braceArg(text, m.end() - 1)
                lm = re.match(r'\s*\\label\{([^}]*)\}', text[j:j + 200])
                if lm:
                    self.sections[lm.group(1)] = (title, rel)
        self.figures = {}                                # figure output -> {caption, label, note}
        for rel, text in self.files.items():
            for m in re.finditer(r'\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}', text, re.S):
                body = m.group(1)
                g = re.search(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{Figs/([^}.]+)', body)
                if not g:
                    continue
                cap = re.search(r'\\caption\s*\{', body)
                lab = re.search(r'\\label\{([^}]*)\}', body)
                note = re.search(r'\\item\s*\[\]\s*(.*?)\\end\{tablenotes\}', body, re.S)
                self.figures[g.group(1)] = {'caption': TT.braceArg(body, cap.end() - 1)[0] if cap else '',
                                            'label': lab.group(1) if lab else None,
                                            'note': note.group(1).strip() if note else ''}
        self.numbers, self.fresh = {}, False
        aux = os.path.join(root, 'main.aux')
        if os.path.exists(aux):
            newest = max(os.path.getmtime(os.path.join(d, f)) for d, _, fs in os.walk(root)
                         for f in fs if f.endswith('.tex'))
            self.fresh = os.path.getmtime(aux) > newest
            for m in re.finditer(r'\\newlabel\{([^}]*)\}\{\{([^}]*)\}', read(aux)):
                self.numbers[m.group(1)] = m.group(2)
        self.bib = _bib(os.path.join(root, 'References.bib'))

    def label(self, name, table):
        """ The paper's label of an output it inputs: the table's own, or the figure environment's. """
        if table is not None:
            return table.label
        return self.figures.get(name, {}).get('label')


def _bib(path):
    """ {key: (authors' surnames, year)} from a .bib, enough for author-year citations. """
    out = {}
    if not os.path.exists(path):
        return out
    text = read(path)
    for m in re.finditer(r'@\w+\s*\{\s*([^,\s]+)\s*,', text):
        body, _ = TT.braceArg(text, text.find('{', m.start()))
        a = re.search(r'author\s*=\s*[{"](.*?)[}"]\s*,\s*\n', body, re.S)
        y = re.search(r'(?:year|date)\s*=\s*[{"]?(\d{4})', body)
        names = []
        if a:
            for person in re.split(r'\s+and\s+', a.group(1).replace('\n', ' ')):
                person = person.strip().strip('{}')
                names.append(person.split(',')[0].strip() if ',' in person else person.split()[-1])
        out[m.group(1)] = (names, y.group(1) if y else 'n.d.')
    return out


# ---------------------------------------------------------------------------------------------------
# Provenance: what an output reads (REPLICATION.md's map), which builder makes it (build.py), the commit.

class Provenance:
    def __init__(self):
        self.reads = {}
        if os.path.exists(MAPFILE):
            text = read(MAPFILE)
            i, j = text.find('<!-- outputs:begin -->'), text.find('<!-- outputs:end -->')
            for line in text[i:j].split('\n'):
                cells = [c.strip() for c in line.split('|')]
                if len(cells) >= 6 and cells[1].startswith('`'):
                    self.reads[cells[1].strip('`')] = re.findall(r'`([^`]+)`(?:\s*\((\d+) files\))?', cells[4])
        self.builder = {}
        src = read(os.path.join(HERE, 'build.py'))
        for m in re.finditer(r"_variants\(\s*'([^']+)',\s*([\w.]+)", src):
            self.builder[m.group(1)] = m.group(2)
        for m in re.finditer(r"'([^']+)'\s*:\s*\(\s*'(?:table|figure|data)'\s*,\s*([\w.]+)", src):
            self.builder.setdefault(m.group(1), m.group(2))
        self.commit = git('rev-parse', '--short', 'HEAD') or 'unknown'
        self.dirty = bool(git('status', '--porcelain', '--', 'results', 'python/paper'))
        self.date = datetime.date.today().isoformat()


# ---------------------------------------------------------------------------------------------------
# The pages: their headings (the \oa keys and the page codes) and the exhibits they include, in order.

HEADING = re.compile(r'^(#{1,2})\s+(?:([A-D]\d?)\.\s+)?(.*?)\s*\{#([A-Za-z0-9_-]+)[^}]*\}\s*$', re.M)
INCLUDE = re.compile(r'\{\{<\s*include\s+_generated/exhibits/([A-Za-z0-9_]+?)(-head)?\.qmd\s*>\}\}')


def pageFiles():
    """ The book's pages in the order of _quarto.yml. """
    return re.findall(r'^\s*-\s*(?:part:\s*)?([\w-]+\.qmd)\s*$', read(os.path.join(SITE, '_quarto.yml')), re.M)


def pages():
    """ [{file, page, code, title, key, keys, exhibits}] per page: `keys` {key: (target, code)} of every heading
    with an anchor, `exhibits` the ids the page includes, in order. """
    out = []
    for f in pageFiles():
        text = read(os.path.join(SITE, f))
        page = f[:-4] + '.html'
        heads = list(HEADING.finditer(text))
        top = next((h for h in heads if len(h.group(1)) == 1), None)
        code = top.group(2) if top else None
        keys = {h.group(4): (page if len(h.group(1)) == 1 else page + '#' + h.group(4), code) for h in heads}
        ids = []
        for m in INCLUDE.finditer(text):
            if m.group(1) not in ids:
                ids.append(m.group(1))
        out.append({'file': f, 'page': page, 'code': code, 'title': top.group(3) if top else '',
                    'key': top.group(4) if top else None, 'keys': keys, 'exhibits': ids})
    return out


def writeMacros(pgs):
    keys = {}
    for p in pgs:
        keys.update({k: v for k, v in p['keys'].items() if v[1]})
    lines = [r'%% GENERATED by python/paper/onlineAppendix.py from the headings of writing/OnlineAppendix/*.qmd '
             r'-- do not edit by hand.',
             r'%% \oa{key} prints "online appendix", linked to the key' + "'" + r's page: "in the \oa{esc-paths}" reads '
             r'"in the online appendix"; \oanum{esc-paths} prints its section, "C1". An unknown key prints in bold.',
             r'\providecommand{\oaurl}{' + SITE_URL + '}',
             r'\newcommand{\oadef}[3]{\expandafter\def\csname oa:#1\endcsname{\href{\oaurl/#2}{online appendix}}'
             r'\expandafter\def\csname oanum:#1\endcsname{\href{\oaurl/#2}{#3}}}',
             r'\newcommand{\oa}[1]{\ifcsname oa:#1\endcsname\csname oa:#1\endcsname\else\textbf{OA:#1??}\fi}',
             r'\newcommand{\oanum}[1]{\ifcsname oanum:#1\endcsname\csname oanum:#1\endcsname\else\textbf{OA:#1??}\fi}',
             r'%% \oahome takes no argument, so xspace restores the space TeX drops after it ("\oahome is ...").',
             r'\RequirePackage{xspace}',
             r'\newcommand{\oahome}{\href{\oaurl}{\nolinkurl{' + SITE_URL.split('//')[1] + r'}}\xspace}']
    for key, (target, code) in keys.items():
        lines.append(r'\oadef{' + key + '}{' + target.replace('#', r'\#') + '}{' + code + '}')
    lines.append(r'%% Retired keys (the site before 2026-10-09), defined as their new pages.')
    for old, new in OLDKEYS.items():
        if new in keys and old not in keys:
            target, code = keys[new]
            lines.append(r'\oadef{' + old + '}{' + target.replace('#', r'\#') + '}{' + code + '}')
    return write(MACROS, '\n'.join(lines) + '\n')


# ---------------------------------------------------------------------------------------------------
# References from captions and notes: to the site's exhibits (\ref{oa:<id>}, a table's own label), to the
# paper (its numbers from main.aux), to the site's pages (\oa) and to the literature.

def anchor(i):
    return 'ex-' + i


class Refs:
    def __init__(self, paper, pgs, numbers, labels):
        self.paper, self.numbers, self.labels = paper, numbers, labels      # numbers: id -> (word, number, page)
        self.keys = {}
        for p in pgs:
            self.keys.update(p['keys'])

    def _exhibit(self, i, here):
        word, num, page = self.numbers[i]
        return '<a href="{}#{}">{}</a>'.format('' if page == here else page, anchor(i), num)

    def ref(self, here):
        def f(label, eq = False):
            if label.startswith('oa:') and label[3:] in self.numbers:
                return self._exhibit(label[3:], here)
            if label in self.labels and self.labels[label] in self.numbers:
                return self._exhibit(self.labels[label], here)
            num = self.paper.numbers.get(label)
            if num:
                if eq:
                    return ('equation ({}) of the paper' if eq == 'word' else '({}) of the paper').format(num)
                return '{} of the paper'.format(num)
            title = self.paper.sections.get(label, (None, None))[0]
            return '\u201c{}\u201d of the paper'.format(html.escape(plain(title))) if title else 'the paper'
        return f

    def oa(self, here):
        def f(key):
            if key is None:
                return '<a href="index.html">{}</a>'.format(SITE_URL.split('//')[1])
            target, code = self.keys.get(OLDKEYS.get(key, key), (None, None))
            if not target:
                return '<strong>OA:{}??</strong>'.format(html.escape(key))
            href = target[len(here):] if target.startswith(here + '#') else target
            return '<a href="{}">{}</a>'.format(href, code or 'the front page')
        return f

    def cite(self, keys, textual = False):
        parts = []
        for k in keys:
            names, year = self.paper.bib.get(k, ([k], ''))
            who = (names[0] if len(names) == 1 else ' and '.join(names) if len(names) == 2 else names[0] + ' et al.')
            parts.append('{} ({})'.format(who, year) if textual else '{} {}'.format(who, year))
        s = '; '.join(parts)
        return html.escape(s if textual else '(' + s + ')')

    def context(self, here):
        return TT.Context(ref = self.ref(here), cite = self.cite, oa = self.oa(here))


# ---------------------------------------------------------------------------------------------------
# The blocks.

def paperBadge(name, table, paper):
    """ ' Table 3 in the paper' for an output the paper inputs, '' otherwise. """
    if name not in paper.uses:
        return ''
    num = paper.numbers.get(paper.label(name, table) or '')
    what = ('Table' if table is not None else 'Figure') + (' ' + num if num else '')
    return ' <span class="oa-badge">{} in the paper</span>'.format(html.escape(what))


def links(ex, prov, files):
    """ The exhibit's foot: its data as csv and, folded, where it comes from. `files`: (label, path under
    _generated/data) pairs. """
    data = ' \u00b7 '.join('<a href="_generated/data/{}" download>{}</a>'.format(p, html.escape(l)) for l, p in files)
    reads = prov.reads.get(ex.output, [])
    src = ''.join('<li><code>{}</code>{}</li>'.format(html.escape(p), ' ({} files)'.format(n) if n else '')
                  for p, n in reads) or '<li>Not traced yet: run <code>build.py --map</code>.</li>'
    cmd = r'.venv\Scripts\python.exe python\paper\build.py --only ' + ex.output
    return ('<div class="oa-links">{}<details class="oa-source"><summary>Source</summary><p>Reads:</p><ul>{}</ul>'
            '<p>Built by <code>{}</code> (<a href="{}/tree/{}/python/paper">python/paper</a>) at commit <code>{}</code>{}. '
            'Rebuild: <code>{}</code>, then <code>build.py --site</code>.</p></details></div>').format(
        ('Data: ' + data + ' \u00b7 ') if data else '', src, html.escape(prov.builder.get(ex.output, 'python/paper')),
        REPO_URL, prov.commit, prov.commit, ' with uncommitted changes' if prov.dirty else '', html.escape(cmd))


def dataFiles(ex, prov):
    """ The csvs an exhibit offers, copied under _generated/data: an explorer's dataset; a static exhibit's traced
    inputs that are single csv files. """
    out = []
    if ex.kind == 'explorer':
        src = os.path.join(DATA, ex.output + '.csv')
        if os.path.exists(src):
            copy(src, os.path.join(GEN, 'data', ex.output + '.csv'))
            out.append(('the figure\u2019s data (csv)', ex.output + '.csv'))
        return out
    for path, n in prov.reads.get(ex.output, []):
        src = os.path.join(C.REPO, path)
        if not n and '*' not in path and path.endswith('.csv') and os.path.exists(src):
            copy(src, os.path.join(GEN, 'data', path))
            out.append((os.path.basename(path), path.replace('\\', '/')))
    return out


def block(i, ex, num, paper, refs, prov, here, report):
    """ {'whole': html} for a static exhibit, {'head': html, 'foot': html} for an explorer. """
    word, n, _ = num
    ctx = refs.context(here)
    number = '<span class="oa-num">{} {}.</span> '.format(word.capitalize(), n)
    files = dataFiles(ex, prov)
    if ex.kind == 'table':
        p = os.path.join(TABLES, ex.output + '.tex')
        if not os.path.exists(p):
            report.append('missing table {}'.format(ex.output))
            return {'whole': '<p class="oa-missing">Table {} has not been built yet.</p>'.format(n)}
        t = TT.parse(read(p))
        body = t.html(ctx, number = number, tableId = anchor(i)).replace(
            '</caption>', paperBadge(ex.output, t, paper) + '</caption>', 1)
        report.extend('{}: LaTeX outside the converter\u2019s vocabulary: {}'.format(ex.output, u) for u in sorted(t.unknown))
        return {'whole': '<div class="oa-exhibit oa-tablebox"><div class="oa-scroll">{}</div>{}</div>'.format(
            body, links(ex, prov, files))}
    if ex.kind == 'figure':
        fig = paper.figures.get(ex.output) if ex.output in paper.uses else None
        cap, note = (fig['caption'], fig['note']) if fig else (ex.caption or ex.output, ex.note or '')
        svg = os.path.join(FIGS, ex.output + '.svg')
        if not os.path.exists(svg):
            report.append('missing figure {}'.format(ex.output))
            return {'whole': '<p class="oa-missing">Figure {} has not been built yet.</p>'.format(n)}
        copy(svg, os.path.join(GEN, 'figs', ex.output + '.svg'))
        note = re.sub(r'^\\textit\{Note:\}\s*', '', note.strip())
        return {'whole': ('<div class="oa-exhibit oa-figure" id="{}"><div class="oa-caption">{}{}{}</div>'
                          '<img src="_generated/figs/{}.svg" alt="{}">{}{}</div>').format(
            anchor(i), number, TT.inline(cap, ctx), paperBadge(ex.output, None, paper), ex.output,
            html.escape(plain(cap)), '<div class="oa-note"><em>Note:</em> {}</div>'.format(TT.inline(note, ctx))
            if note else '', links(ex, prov, files))}
    if not os.path.exists(os.path.join(DATA, ex.output + '.csv')):
        report.append('missing dataset {} for {}'.format(ex.output, i))
    head = '<div class="oa-caption" id="{}">{}{}</div>'.format(anchor(i), number, TT.inline(ex.caption or i, ctx))
    foot = (('<div class="oa-note"><em>Note:</em> {}</div>'.format(TT.inline(ex.note, ctx)) if ex.note else '')
            + links(ex, prov, files))
    return {'head': head, 'foot': foot}


_RUN = re.compile(r' of the paper(?=(?:, | and )[\w.]+ of the paper)')


def collapseRuns(s):
    """ A run of the paper's references names the paper once, at its end: "tables 5, 6 and 7 of the paper", where
    each resolved on its own reads "5 of the paper, 6 of the paper and ...". """
    return _RUN.sub('', s)


def include(htmlText):
    """ A block as a Quarto include: raw HTML for the site. The hidden math span is there for pandoc, which
    loads MathJax only on a page whose Markdown has math. """
    return '[$\\cdot$]{.hidden}\n\n```{=html}\n' + collapseRuns(htmlText) + '\n```\n'


# ---------------------------------------------------------------------------------------------------
# The replication map, the palette, the version stamp.

def replicationMap(pgs, numbers, prov):
    rows = []
    for p in pgs:
        for i in p['exhibits']:
            if i not in numbers:
                continue
            ex, (word, n, page) = EXHIBITS[i], numbers[i]
            reads = ', '.join(path + (' ({} files)'.format(k) if k else '') for path, k in prov.reads.get(ex.output, []))
            rows.append('<tr><td class="oa-l"><a href="{}#{}">{} {}</a></td><td class="oa-l"><code>{}</code></td>'
                        '<td class="oa-l"><code>{}</code></td><td class="oa-l">{}</td></tr>'.format(
                            page, anchor(i), word.capitalize(), n, ex.output,
                            html.escape(prov.builder.get(ex.output, '')), html.escape(reads) or '\u2013'))
    return include('<div class="oa-scroll"><table class="oa-table oa-table--map"><caption>Every exhibit, the output '
                   'that holds it, the builder that makes it and what it reads</caption><thead><tr>'
                   '<th class="oa-l" scope="col">Exhibit</th><th class="oa-l" scope="col">Output</th>'
                   '<th class="oa-l" scope="col">Builder</th><th class="oa-l" scope="col">Reads</th></tr></thead><tbody>'
                   + ''.join(rows) + '</tbody></table></div>')


def styleJs():
    """ The palette of the paper's figures (figures.py), for assets/oa.js: one source for both. """
    import figures as F
    style = {'series': list(F.SERIES), 'ink': dict(F.INK), 'rhoColours': [F.SERIES[0], F.SERIES[1], F.INK['secondary']]}
    return ('// GENERATED by python/paper/onlineAppendix.py from python/paper/figures.py -- do not edit by hand.\n'
            'export const STYLE = ' + json.dumps(style, indent = 1) + ';\n')


def variables(paper, numbers):
    r""" _variables.yml, for the prose's {{< var >}}: p.<label> the paper's number of a figure, table, section or
    appendix (main.aux; the label's ':' as '_'), x.<id> a site exhibit's number. """
    key = lambda s: re.sub(r'[^A-Za-z0-9]', '_', s)
    lines = ['# GENERATED by python/paper/onlineAppendix.py -- do not edit by hand.', 'p:']
    for lab, num in sorted(paper.numbers.items()):
        if lab.split(':')[0] in ('fig', 'table', 'sec', 'app') and '@' not in lab:
            lines.append('  {}: "{}"'.format(key(lab), num))
    lines.append('x:')
    for i, (word, n, _) in sorted(numbers.items()):
        lines.append('  {}: "{}"'.format(key(i), n))
    return '\n'.join(lines) + '\n'


def version(prov, paper):
    dirty = ' with uncommitted changes in `results` or `python/paper`' if prov.dirty else ''
    nums = '' if paper.fresh else ' The paper\u2019s numbers are those of its last compilation.'
    return 'Built on {} from commit [`{}`]({}/commit/{}){}.{}\n'.format(prov.date, prov.commit, REPO_URL, prov.commit,
                                                                       dirty, nums)


# ---------------------------------------------------------------------------------------------------

def build(verbose = True):
    report = []
    for d in ('exhibits', 'figs', 'data'):
        os.makedirs(os.path.join(GEN, d), exist_ok = True)
    paper, prov, pgs = Paper(), Provenance(), pages()
    numbers, labels, seen = {}, {}, set()
    for p in pgs:
        k = {'figure': 0, 'table': 0}
        for i in p['exhibits']:
            if i not in EXHIBITS:
                report.append('{} includes {}, which the registry does not hold'.format(p['file'], i))
                continue
            if i in seen:
                report.append('{} is included on more than one page'.format(i))
            seen.add(i)
            word = 'table' if EXHIBITS[i].kind == 'table' else 'figure'
            k[word] += 1
            numbers[i] = (word, '{}.{}'.format(p['code'], k[word]) if p['code'] else str(k[word]), p['page'])
            if word == 'table':
                tp = os.path.join(TABLES, EXHIBITS[i].output + '.tex')
                if os.path.exists(tp):
                    lab = TT.parse(read(tp)).label
                    if lab:
                        labels[lab] = i
            elif EXHIBITS[i].output in paper.figures and paper.figures[EXHIBITS[i].output]['label']:
                labels[paper.figures[EXHIBITS[i].output]['label']] = i
    unused = sorted(set(EXHIBITS) - seen)
    if unused:
        report.append('registered but on no page: ' + ', '.join(unused))
    refs = Refs(paper, pgs, numbers, labels)
    for p in pgs:
        for i in p['exhibits']:
            if i not in EXHIBITS:
                continue
            b = block(i, EXHIBITS[i], numbers[i], paper, refs, prov, p['page'], report)
            for part, text in b.items():
                write(os.path.join(GEN, 'exhibits', i + ('' if part == 'whole' else '-' + part) + '.qmd'), include(text))
    write(os.path.join(GEN, 'rep-map.qmd'), replicationMap(pgs, numbers, prov))
    write(os.path.join(GEN, 'style.js'), styleJs())
    write(os.path.join(GEN, 'version.qmd'), version(prov, paper))
    write(os.path.join(SITE, '_variables.yml'), variables(paper, numbers))
    bib = os.path.join(C.PAPERTEX, 'References.bib')
    if os.path.exists(bib):
        copy(bib, os.path.join(GEN, 'References.bib'))
    writeMacros(pgs)
    if verbose:
        print('online appendix: {} pages, {} exhibits ({} interactive), commit {}{}, paper numbers {}'.format(
            len(pgs), len(numbers), sum(EXHIBITS[i].kind == 'explorer' for i in numbers), prov.commit,
            ' (dirty)' if prov.dirty else '', 'from main.aux' if paper.fresh else 'from a main.aux older than the tex'))
        for line in report:
            print('  ' + line)
        print('next: quarto render ' + os.path.relpath(SITE, C.REPO))
    return {'pages': pgs, 'numbers': numbers, 'report': report}


if __name__ == '__main__':
    build()
