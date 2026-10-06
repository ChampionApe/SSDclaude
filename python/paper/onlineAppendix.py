r""" The online appendix: writing/OnlineAppendix, a Quarto book of the paper's exhibits, built from results/paper.

Run:   .venv\Scripts\python.exe python\paper\onlineAppendix.py     (or build.py --site, which calls build())
then:  quarto render writing\OnlineAppendix                         (the site in _book/, and _book/OnlineAppendix.pdf)

Reads results/paper (each built table's tex; each figure's pdf, png, svg and marks.json), the output map of
REPLICATION.md (`build.py --map`), build.py's source for the builder of each output, the paper's tex (which
exhibits it inputs, its figures' captions and notes, its section titles, and its numbers from main.aux when that
file is newer than every .tex of the paper) and git. It imports no model code and runs no builder. Writes
  writing/OnlineAppendix/_generated/   one include per exhibit group (a block of HTML for the site and one of LaTeX
                                        for the print edition), the figures, the tables' print copies, the csvs
                                        offered for download, the bibliography, the version stamp
  writing/Paper/onlineAppendix.tex      the paper's \oa macros, from the chapters' OA-numbered headings

GROUPS is the registry and the order of the book's numbering. An exhibit the paper inputs is shown as the paper's
and left out of the print edition; every other one is Table or Figure OA.k, numbered in the same order in both
formats. A missing exhibit, or a figure without its svg or marks, degrades (the png; linking by table only) and is
reported, never fatal: the online-only builders may not have run yet.
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
MACROS = os.path.join(C.PAPERTEX, 'onlineAppendix.tex')
MAPFILE = os.path.join(C.REPO, 'REPLICATION.md')
SITE_URL = 'https://championape.github.io/SSDclaude'
REPO_URL = 'https://github.com/ChampionApe/SSDclaude'
TWIN = '_vectorX'                          # the variant suffix of every twin (both arms lead with common X)
VARIANT = {'commonX': ('common <i>X</i>', 'the paper\u2019s'), 'vectorX': ('vector <i>X<sub>i</sub></i>', '')}


# ---------------------------------------------------------------------------------------------------
# The registry.

class Ex:
    r""" One exhibit of a group: `name` is the headline output in build.OUTPUTS, `twin` adds its `_vectorX` twin
    under the calibration switch, `tab` names its tab, `caption`/`note` (LaTeX) stand in for a figure the paper
    does not input. `text` (LaTeX, the notes' vocabulary) is the exhibit's own paragraph: beside it on the site,
    following the tab and the calibration, and before it in the print edition; `textAlt` replaces it for the
    vector-$X_i$ twin, else the twin shows `text`. No number is typed in a text. """
    def __init__(self, kind, name, tab = '', twin = False, caption = None, note = None, text = None, textAlt = None):
        self.kind, self.name, self.tab, self.twin, self.caption, self.note = kind, name, tab, twin, caption, note
        self.text, self.textAlt = text, textAlt


def F(name, **k):
    return Ex('figure', name, **k)


def T(name, tab, **k):
    return Ex('table', name, tab, **k)


TWINNOTE = (r'The paper\textquotesingle s figure under the vector-$X_i$ calibration (Online Appendix \oa{oecd-vectorx}); '
            r'its baseline levels are the baseline rows of the tables of this section.')
IDENTICAL = (r'Under the vector-$X_i$ calibration this exhibit is identical to the common-$X$ one to the last printed '
             r'digit, as the comparison in Online Appendix \oa{oecd-vectorx} records: the calibration is block '
             r'recursive, so the aggregates the reform moves do not depend on how the taste for leisure is split across '
             r'the quartiles.')

# (anchor, chapter file stem, exhibits). The anchors are the book's headings and the paper's \oa keys.
GROUPS = [
    ('robustness', 'index', [
        F('RobustnessMap', caption = r'The paper\textquotesingle s results across specifications',
          note = r'Each marker opens the table that prints it.')]),
    ('data-countries', 'data', [
        F('OECDdata'), T('OECD_Countries', 'Countries'), T('OECD_Sources', 'Sources')]),
    ('data-correlations', 'data', [T('OECD_Correlations', 'Correlations')]),
    ('arg-calibration', 'argentina', [T('ArgentinaCalibration', 'Calibration', twin = True)]),
    ('arg-reform', 'argentina', [
        T('ArgentinaUniversal', 'The reform in 2010', twin = True, textAlt = IDENTICAL,
          text = r'Table \ref{table:Argentina:Universal}: the effect in 2010 of raising the universal pension $\epsilon$ '
                 r'to the level at which informal retirees receive the benefit of the least productive formal workers, '
                 r'unanticipated and permanent. The first row is the pre-reform economy; the second holds the tax rate '
                 r'at its pre-reform path and so isolates the response of households; the third lets the electorate '
                 r'reset the tax. Taxes rise, because the reform moves benefits toward informal retirees, who are poorer '
                 r'than formal ones and value them more at the margin, and savings and hours fall a little; with the tax '
                 r'held fixed, formal savings rise instead, since informal households now hold a claim on the system '
                 r'and save less.'),
        T('ArgentinaReformPath', 'Its path', twin = True, textAlt = IDENTICAL,
          text = r'The same reform along the path: the tax rate, the savings rate and the workweek in every model period '
                 r'from the reform year on, on the pre-reform path and on the reform path side by side. The tax response '
                 r'builds over the first periods, because informal households, now covered, save less for retirement '
                 r'and as retirees demand more taxation; section \ref{sec:argentina} quotes the response one period on.')]),
    ('arg-rho', 'argentina', [
        F('ARG_CRRA_LOG', twin = True, textAlt = IDENTICAL,
          text = r'Figure \ref{fig:ARG:EffectOfCRRA}: the effect of the reform on the tax rate, the savings rate, the '
                 r'workweek and the ratio of informal to formal savings, on impact and one period on, at every IES of the '
                 r'grid, each economy recalibrated to the same pre-reform targets. Below an IES of one the responses are '
                 r'dampened, since the young resist taxation more and the calibration needs a heavier political weight of '
                 r'the old to reproduce the observed tax rate; between one and two they stay close to the log benchmark.'),
        T('ArgentinaReformByRho', 'Every IES', twin = True, textAlt = IDENTICAL,
          text = r'The values behind the figure\textquotesingle s short-run series, one row per point of the grid: the '
                 r'post-reform tax rate, the change in the savings rate and the workweek in the reform year. The pre-reform '
                 r'row is common to every IES, because each is recalibrated to the same targets; the pre-reform savings '
                 r'rate is not a target and varies with the IES, so its column is a change.')]),
    ('arg-designs', 'argentina', [
        F('ARG_LOG_FourInOne', twin = True,
          caption = r'The equilibrium in 2010 over pension designs $(\epsilon, \theta)$, Argentina',
          note = r'The line is the calibrated $\theta$, the markers the pre-reform $\epsilon$ and the universal '
                 r'level of the reform. The savings rate is savings relative to GDP.')]),
    ('arg-rhogrid', 'argentina', [
        F('ARG_RhoGrid', twin = True, caption = r'The Argentine calibration across the intertemporal elasticity',
          note = r'The parameters solved jointly with the equilibrium path at each IES of the grid, against the same '
                 r'targets; the table of this section prints their values, and $\rho = 1$ is the paper\textquotesingle s '
                 r'calibration.'),
        T('ARG_RhoGridTable', 'Calibration by IES', twin = True)]),
    ('oecd-calibration', 'oecd', [
        T('USUKFRCalibration', 'Countries', twin = True), T('US_householdheterogeneity', 'U.S.', twin = True),
        T('FR_householdheterogeneity', 'France', twin = True), T('UK_householdheterogeneity', 'UK', twin = True),
        T('FRUK_householdheterogeneity', 'France at the UK\u2019s cuts', twin = True),
        T('UKUS_householdheterogeneity', 'The UK at U.S. cuts', twin = True)]),
    ('oecd-vectorx', 'oecd', []),
    ('oecd-rhogrid', 'oecd', [
        F('OECD_RhoGrid', twin = True,
          caption = r'The calibrations of the U.S., the UK and France across the intertemporal elasticity',
          note = r'The parameters solved jointly with the equilibrium path at each IES of the grid, against the same '
                 r'targets, with $\beta$ calibrated for the U.S. and imposed on the UK and France; the table of this '
                 r'section prints their values, and $\rho = 1$ is the paper\textquotesingle s calibration.'),
        T('OECD_RhoGridTable', 'Calibration by IES', twin = True)]),
    ('oecd-us', 'oecd', [
        F('US_overview', twin = True), T('US_PensChars', 'Pension design', twin = True),
        T('US_Ageing', 'Ageing', twin = True), T('US_OtherShocks', 'French characteristics', twin = True),
        T('US_CRRA_PensChars', 'Design by IES', twin = True), T('US_CRRA_Ageing', 'Ageing by IES', twin = True),
        T('US_CRRA_OtherShocks', 'French by IES', twin = True)]),
    ('oecd-uk', 'oecd', [
        F('UKUS_French', twin = True, caption = r'French characteristics in the U.S.\ and the UK',
          note = r'Every panel is the deviation from the host\textquotesingle s own baseline at the same $\rho$, '
                 r'whose levels are the baseline rows of the tables of this section. France\textquotesingle s income '
                 r'groups are cut at the host\textquotesingle s income percentiles. The savings rate is savings '
                 r'relative to GDP.'),
        T('UK_OtherShocks', 'French characteristics', twin = True),
        T('UK_CRRA_OtherShocks', 'French by IES', twin = True), T('UK_CRRA_PensChars', 'Design by IES', twin = True),
        T('UK_CRRA_Ageing', 'Ageing by IES', twin = True)]),
    ('esc-calibration', 'esc', [
        T('US_ESC_Calibration', 'The cost'), T('US_ESC_Country', 'The cross-country test')]),
    ('esc-us', 'esc', [
        F('US_ESC_overview'), T('US_ESC_Ageing', 'Ageing'), T('US_ESC_IncomeDistr', 'Income distribution'),
        T('US_ESC_Voting', 'Voting patterns'), T('US_ESC_FrenchAll', 'All French characteristics')]),
    ('esc-uk', 'esc', [
        F('UKUS_ESC_French',
          caption = r'Endogenous pension design under French characteristics in the U.S.\ and the UK',
          note = r'Each host at its own cost parameter. The first column is the design in force in 2020 as a level, '
                 r'the reference line at the host\textquotesingle s observed design and the muted lines at the '
                 r'corners; the second is the tax rate as a deviation from the host\textquotesingle s '
                 r'endogenous-$\theta$ baseline, whose levels are the baseline rows of the tables of this section. An '
                 r'open marker is the reading with the design pinned at the host\textquotesingle s value, a filled '
                 r'one the reading with the design chosen.'),
        T('UK_ESC_IncomeDistr', 'Income distribution'),
        T('UK_ESC_Voting', 'Voting patterns'), T('UK_ESC_FrenchAll', 'All French characteristics')]),
    ('esc-path', 'esc', [
        F('ESC_Path', caption = r'The design and the tax along the baseline path, U.S.',
          note = r'The design chosen one period in advance from the first period on, and the tax rate with the design '
                 r'chosen and with it pinned at $\theta^{\ast}$, along the baseline path at each IES and, at $\rho = 1$, '
                 r'at the Frisch elasticities $\xi = 0.2$ and $0.4$; the tables of this section print the values.'),
        T('ESC_PathTable', 'The path'), T('ESC_Xi', 'The Frisch elasticity')]),
    ('esc-timing', 'esc', [T('ESC_Timing', 'Timing of the choice')]),
    ('esc-scale', 'esc', [T('US_ESC_ScaleWedge', 'The alternative cost')]),
    ('num-stationary', 'numerical', [T('NUM_Stationary', 'Stationary policies')]),
    ('num-selection', 'numerical', [T('NUM_Selection', 'Equilibrium selection')]),
]
CHAPTERS = ['index', 'data', 'argentina', 'oecd', 'esc', 'numerical', 'replication']


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


def latexText(s):
    """ Plain text made safe for LaTeX. """
    return (s.replace('\\', r'\textbackslash{}').replace('&', r'\&').replace('%', r'\%').replace('#', r'\#')
             .replace('_', r'\_').replace('$', r'\$'))


def git(*args):
    try:
        return subprocess.run(['git', '-C', C.REPO] + list(args), capture_output = True, text = True,
                              check = True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


# ---------------------------------------------------------------------------------------------------
# What the paper says: which exhibits it inputs, its figures' captions, its section titles, its numbers.

class Paper:
    def __init__(self):
        root = C.PAPERTEX
        self.files = {}
        for d in ('Sections', 'Appendix'):
            for f in sorted(os.listdir(os.path.join(root, d))):
                if f.endswith('.tex'):
                    self.files[d + '/' + f] = uncomment(read(os.path.join(root, d, f)))
        self.uses = {}                                   # exhibit name -> [tex files]
        for rel, text in self.files.items():
            for m in re.finditer(r'\\input\s*\{Tables/([^}]+)\}', text):
                self.uses.setdefault(m.group(1).strip(), []).append(rel)
            for m in re.finditer(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{Figs/([^}.]+)(?:\.\w+)?\}', text):
                self.uses.setdefault(m.group(1).strip(), []).append(rel)
        self.sections = {}                               # label -> (title, file); also file -> first title
        self.fileTitle = {}
        for rel, text in self.files.items():
            for m in re.finditer(r'\\(section|subsection)\*?\s*\{', text):
                title, j = TT.braceArg(text, m.end() - 1)
                if m.group(1) == 'section' and rel not in self.fileTitle:
                    self.fileTitle[rel] = title
                lm = re.match(r'\s*\\label\{([^}]*)\}', text[j:j + 200])
                if lm:
                    self.sections[lm.group(1)] = (title, rel)
            for m in re.finditer(r'\\label\{(eq:[^}]*)\}', text):
                self.sections.setdefault(m.group(1), (None, rel))
        self.figures = {}                                # figure name -> {caption, label, note, file}
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
                                            'note': note.group(1).strip() if note else '', 'file': rel}
        self.numbers, self.fresh, self.eqIn = {}, False, {}
        aux = os.path.join(root, 'main.aux')
        if os.path.exists(aux):
            newest = max(os.path.getmtime(os.path.join(d, f)) for d, _, fs in os.walk(root)
                         for f in fs if f.endswith('.tex'))
            self.fresh = os.path.getmtime(aux) > newest
            if self.fresh:
                for m in re.finditer(r'\\newlabel\{([^}]*)\}\{\{([^}]*)\}', read(aux)):
                    self.numbers[m.group(1)] = m.group(2)
        if not self.fresh:
            self._count(root)
        self.bib = _bib(os.path.join(root, 'References.bib'))

    def _count(self, root):
        r""" The paper's section, appendix, table and figure numbers as LaTeX sets them, counted from main.tex's
        \input order, for when main.aux is stale: sections 1, 2, ..., appendices A, B, ... (the appendices
        environment), tables numbered through the document, figures within sections (Packages.tex's
        \numberwithin). Equations are not counted: `eqIn` holds the section each eq: label sits in. """
        state = {'sec': '', 'nsec': 0, 'napp': 0, 'sub': 0, 'tab': 0, 'fig': 0, 'env': None, 'cur': ''}

        def walk(text, appendix):
            for m in re.finditer(r'\\(section|subsection)(\*?)\s*\{|\\begin\{(table|figure)\*?\}|\\end\{(?:table|figure)\*?\}'
                                 r'|\\caption\b|\\label\{([^}]*)\}|\\input\{(Tables/[^}]*)\}', text):
                kind, star, env, label, tab = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
                if kind and not star:
                    if kind == 'section':
                        if appendix:
                            state['napp'] += 1
                            state['sec'] = chr(ord('A') + state['napp'] - 1)
                        else:
                            state['nsec'] += 1
                            state['sec'] = str(state['nsec'])
                        state['sub'], state['fig'], state['cur'] = 0, 0, state['sec']
                    else:
                        state['sub'] += 1
                        state['cur'] = '{}.{}'.format(state['sec'], state['sub'])
                elif env:
                    state['env'] = env
                elif m.group(0).startswith('\\end'):
                    state['env'] = None
                elif m.group(0) == '\\caption':
                    if state['env'] == 'table':
                        state['tab'] += 1
                        state['cur'] = str(state['tab'])
                    elif state['env'] == 'figure':
                        state['fig'] += 1
                        state['cur'] = '{}.{}'.format(state['sec'], state['fig'])
                elif label:
                    if label.startswith('eq:'):
                        self.eqIn[label] = ('appendix' if appendix else 'section', state['sec'])
                    elif label.split(':')[0] in ('sec', 'app', 'table', 'fig'):   # propositions are not counted
                        self.numbers[label] = state['cur']
                elif tab:
                    p = os.path.join(root, tab + ('' if tab.endswith('.tex') else '.tex'))
                    if os.path.exists(p):
                        walk(uncomment(read(p)), appendix)

        main = uncomment(read(os.path.join(root, 'main.tex')))
        appendix = False
        for m in re.finditer(r'\\begin\{appendices\}|\\appendix\b|\\input\{([^}]*)\}', main):
            if m.group(1) is None:
                appendix = True
                continue
            rel = m.group(1) + ('' if m.group(1).endswith('.tex') else '.tex')
            if rel.startswith(('Sections/', 'Appendix/')) and os.path.exists(os.path.join(root, rel)):
                walk(self.files.get(rel) or uncomment(read(os.path.join(root, rel))), appendix)
        self.counted = True

    def where(self, name):
        """ The paper's place for an exhibit it inputs, as a phrase ('section 7', or a title when main.aux is
        stale). """
        files = self.uses.get(name, [])
        if not files:
            return None
        rel = files[0]
        kind = 'section' if rel.startswith('Sections/') else 'appendix'
        title = self.fileTitle.get(rel, '')
        label = next((l for l, (t, f) in self.sections.items() if f == rel and t == title), None)
        if label in self.numbers:
            return '{} {}'.format(kind, self.numbers[label])
        return '{} \u201c{}\u201d'.format(kind, plain(title))


def plain(tex):
    """ A short piece of LaTeX (a title, a caption) as plain unescaped text. """
    return html.unescape(re.sub('<[^>]+>', '', TT.inline(tex or '', TT.Context())))


def _bib(path):
    """ {key: (authors' surnames, year)} from a .bib, enough for author-year citations. """
    out = {}
    if not os.path.exists(path):
        return out
    text = read(path)
    for m in re.finditer(r'@\w+\s*\{\s*([^,\s]+)\s*,', text):
        j = text.find('{', m.start())
        body, _ = TT.braceArg(text, j)
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
        self.reads, self.inputBy = {}, {}
        if os.path.exists(MAPFILE):
            text = read(MAPFILE)
            i, j = text.find('<!-- outputs:begin -->'), text.find('<!-- outputs:end -->')
            for line in text[i:j].split('\n'):
                cells = [c.strip() for c in line.split('|')]
                if len(cells) < 6 or not cells[1].startswith('`'):
                    continue
                name = cells[1].strip('`')
                self.reads[name] = re.findall(r'`([^`]+)`(?:\s*\((\d+) files\))?', cells[4])
        self.builder = {}
        src = read(os.path.join(HERE, 'build.py'))
        for m in re.finditer(r"_variants\(\s*'([^']+)',\s*([\w.]+)", src):
            self.builder[m.group(1)] = m.group(2)
            self.builder[m.group(1) + TWIN] = m.group(2) + '(commonX = False)'
        for m in re.finditer(r"'([^']+)'\s*:\s*\(\s*'(?:table|figure)'\s*,\s*([\w.]+)", src):
            self.builder.setdefault(m.group(1), m.group(2))
        self.commit = git('rev-parse', '--short', 'HEAD') or 'unknown'
        self.dirty = bool(git('status', '--porcelain', '--', 'results/paper', 'python/paper'))
        self.date = datetime.date.today().isoformat()

    def sources(self, name, texBanner = None):
        """ [(path or pattern, number of files or '')]: the traced reads, else the table's own banner. """
        if name in self.reads:
            return self.reads[name]
        if texBanner and texBanner.get('source'):
            return [(s.strip(), '') for s in texBanner['source'].split(',')]
        return []


# ---------------------------------------------------------------------------------------------------
# The exhibits.

class Asset:
    """ One output on the page: a table or a figure in one calibration variant. """
    def __init__(self, ex, name, variant, group):
        self.ex, self.name, self.variant, self.group = ex, name, variant, group
        self.kind, self.base = ex.kind, ex.name
        self.table = self.svg = self.png = self.pdf = None
        self.marks, self.ok, self.problems = [], False, []
        self.scope = 'online'
        self.number = None                             # 'OA.k' for an online exhibit
        self.anchor = ('oatab_' if self.kind == 'table' else 'oafig_') + name


def load(groups, paper, report):
    assets = []
    for anchor, chapter, exs in groups:
        for ex in exs:
            for variant, name in [('commonX', ex.name)] + ([('vectorX', ex.name + TWIN)] if ex.twin else []):
                a = Asset(ex, name, variant, anchor)
                a.chapter = chapter
                if name in paper.uses:
                    a.scope = 'paper'
                if a.kind == 'table':
                    p = os.path.join(TABLES, name + '.tex')
                    if os.path.exists(p):
                        a.tex = read(p)
                        try:
                            a.table = TT.parse(a.tex)
                            a.ok = True
                        except Exception as e:             # a table the converter cannot read is reported
                            report.append('table {} not converted: {}'.format(name, e))
                    else:
                        report.append('missing table {} ({})'.format(name, anchor))
                else:
                    for ext in ('svg', 'png', 'pdf'):
                        p = os.path.join(FIGS, name + '.' + ext)
                        setattr(a, ext, p if os.path.exists(p) else None)
                    mp = os.path.join(FIGS, name + '.marks.json')
                    if os.path.exists(mp):
                        a.marks = json.loads(read(mp)).get('marks', [])
                    a.ok = bool(a.svg or a.png)
                    if not a.ok:
                        report.append('missing figure {} ({})'.format(name, anchor))
                    elif not a.svg:
                        report.append('figure {} has no svg: png shown, no marks'.format(name))
                    elif not a.marks:
                        report.append('figure {} has no marks: not interactive'.format(name))
                assets.append(a)
    return assets


def number(assets):
    k = {'table': 0, 'figure': 0}
    for a in assets:
        if a.ok and a.scope == 'online':
            k[a.kind] += 1
            a.number = 'OA.{}'.format(k[a.kind])


# ---------------------------------------------------------------------------------------------------
# The book's headings: the OA numbers and anchors the paper's \oa macros and the cross-links use.

HEADING = re.compile(r'^(#{1,3})\s+(OA\.\d+(?:\.\d+)*)\s+(.*?)\s*\{#([A-Za-z0-9_-]+)[^}]*\}\s*$', re.M)


def headings():
    out = {}
    for ch in CHAPTERS:
        p = os.path.join(SITE, ch + '.qmd')
        if not os.path.exists(p):
            continue
        for m in HEADING.finditer(read(p)):
            out[m.group(4)] = {'number': m.group(2), 'title': m.group(3), 'page': ch + '.html',
                               'level': len(m.group(1))}
        if ch == 'index':
            out.setdefault('robustness', {'number': '', 'title': 'Robustness at a glance', 'page': 'index.html',
                                          'level': 2})
    return out


def writeMacros(heads):
    lines = [r'%% GENERATED by python/paper/onlineAppendix.py from the headings of writing/OnlineAppendix/*.qmd '
             r'-- do not edit by hand.',
             r'%% \oa{key} prints the online appendix' + "'" + r's number for a section, linked to its page:',
             r'%% "Online Appendix \oa{esc-uk}" reads "Online Appendix OA.4.3". An unknown key prints in bold, '
             r'never silently.',
             r'\providecommand{\oaurl}{' + SITE_URL + '}',
             r'\newcommand{\oadef}[3]{\expandafter\def\csname oa:#1\endcsname{\href{\oaurl/#2}{#3}}}',
             r'\newcommand{\oa}[1]{\ifcsname oa:#1\endcsname\csname oa:#1\endcsname\else\textbf{OA:#1??}\fi}',
             r'%% \oahome takes no argument, so xspace restores the space TeX drops after it ("\oahome is ...").',
             r'\RequirePackage{xspace}',
             r'\newcommand{\oahome}{\href{\oaurl}{\nolinkurl{' + SITE_URL.split('//')[1] + r'}}\xspace}']
    for key, h in heads.items():
        if not h['number']:
            continue
        target = h['page'] if h['level'] == 1 else h['page'] + r'\#' + key
        lines.append(r'\oadef{' + key + '}{' + target + '}{' + h['number'] + '}')
    return write(MACROS, '\n'.join(lines) + '\n')


# ---------------------------------------------------------------------------------------------------
# References between exhibits, the paper and the appendix.

class Refs:
    def __init__(self, assets, paper, heads):
        self.paper, self.heads = paper, heads
        self.byLabel = {}
        for a in assets:
            if a.kind == 'table' and a.table and a.table.label:
                self.byLabel[a.table.label] = a
            elif a.kind == 'figure' and a.base in paper.figures and a.name == a.base:
                lab = paper.figures[a.base].get('label')
                if lab:
                    self.byLabel[lab] = a
        self.byName = {a.name: a for a in assets}

    def href(self, a, here = None):
        page = (a.chapter if a.chapter else 'index') + '.html'
        return ('#' if here == a.chapter else page + '#') + a.anchor

    def paperText(self, label, eq, latex):
        r""" A label of the paper as words: its number when main.aux is fresh, else the title of the table, the
        figure or the section it names. `latex` gives LaTeX source (titles kept as written), else escaped HTML. """
        num = self.paper.numbers.get(label)
        if num:
            return ('equation ({}) of the paper' if eq == 'word' else '({}) of the paper' if eq
                    else '{} of the paper').format(num)
        q = (lambda s: "``" + s + "''") if latex else (lambda s: '\u201c' + html.escape(plain(s)) + '\u201d')
        a = self.byLabel.get(label)
        if a is not None and a.kind == 'table' and a.table:
            return q(a.table.caption or a.name) + ' in the paper'
        if a is not None and a.kind == 'figure':
            return q(self.paper.figures[a.base]['caption']) + ' in the paper'
        title, rel = self.paper.sections.get(label, (None, None))
        if eq:
            # no parentheses around words: "the cost of an equation in section 7 of the paper", never "of (...)"
            where = self.paper.eqIn.get(label)
            if where:
                return 'an equation in {} {} of the paper'.format(*where)
            sec = self.paper.fileTitle.get(rel, '') if rel else ''
            kind = 'appendix' if rel and rel.startswith('Appendix/') else 'section'
            return ('an equation in the paper' + ("'" if latex else '\u2019') + 's ' + kind + ' ' + q(sec)) \
                if sec else 'an equation of the paper'
        if title:
            return q(title) + ' of the paper'
        return 'the paper'

    def oaHtml(self, here):
        r""" \oa{key} as a link to the section of this appendix, and \oahome to its front page. """
        def oa(key):
            if key is None:
                return '<a href="index.html">{}</a>'.format(SITE_URL.split('//')[1])
            h = self.heads.get(key)
            if not h:
                return '<strong>OA:{}??</strong>'.format(html.escape(key))
            href = ('' if h['page'] == here + '.html' else h['page']) + ('#' + key if h['level'] > 1 else '')
            return '<a href="{}">{}</a>'.format(href or '#' + key, h['number'] or 'the front page')
        return oa

    def oaLatex(self, key):
        if key is None:
            return r'\url{' + SITE_URL + '}'
        h = self.heads.get(key)
        return h['number'] if h and h['number'] else 'OA:' + latexText(key) + '??'

    def html(self, here):
        def ref(label, eq = False):
            a = self.byLabel.get(label)
            if a is not None and a.scope == 'online' and a.number:
                return '<a href="{}">{}</a>'.format(self.href(a, here), a.number)
            text = self.paperText(label, eq, False)
            if a is not None:                              # the paper's exhibit, also shown on this site
                return '<a href="{}">{}</a>'.format(self.href(a, here), text)
            return text
        return ref

    def latex(self, label, eq = False):
        a = self.byLabel.get(label)
        if a is not None and a.scope == 'online' and a.number:
            return a.number
        return self.paperText(label, eq, True)

    def printTex(self, tex):
        return collapseRuns(TT.printTex(tex, self.latex, self.oaLatex), latex = True)

    def context(self, here):
        return TT.Context(ref = self.html(here), cite = self.cite, oa = self.oaHtml(here))

    def cite(self, keys, textual = False):
        parts = []
        for k in keys:
            names, year = self.paper.bib.get(k, ([k], ''))
            who = (names[0] if len(names) == 1 else ' and '.join(names) if len(names) == 2
                   else names[0] + ' et al.') if names else k
            parts.append('{} ({})'.format(who, year) if textual else '{} {}'.format(who, year))
        s = '; '.join(parts)
        return html.escape(s if textual else '(' + s + ')')


# ---------------------------------------------------------------------------------------------------
# Rendering.

def paperLabel(a, paper):
    """ The paper's \\label of an exhibit it inputs: the table's own, or the figure environment's. """
    if a.kind == 'table' and a.table:
        return a.table.label
    return paper.figures.get(a.base, {}).get('label') if a.name == a.base else None


def badge(a, paper):
    if a.scope == 'paper':
        num = paper.numbers.get(paperLabel(a, paper) or '')
        what = '{} {}, {}'.format(a.kind, num, paper.where(a.name)) if num else paper.where(a.name) or ''
        return '<span class="oa-badge oa-badge--paper">In the paper \u00b7 {}</span> '.format(html.escape(what))
    if a.number:
        return '<span class="oa-badge">{} {}</span> '.format('Table' if a.kind == 'table' else 'Figure', a.number)
    return ''


def provenance(a, prov):
    rows, downloads = [], []
    for path, n in prov.sources(a.name, getattr(a.table, 'banner', None) if a.table else None):
        if '*' in path or n:
            link = '{}/tree/{}/{}'.format(REPO_URL, prov.commit, os.path.dirname(path))
            rows.append('<li><code>{}</code>{} <a href="{}">folder</a></li>'.format(
                html.escape(path), ' ({} files)'.format(n) if n else '', link))
        else:
            src = os.path.join(C.REPO, path)
            dl = ''
            if os.path.exists(src) and path.endswith('.csv'):
                copy(src, os.path.join(GEN, 'data', path))
                dl = ' <a href="_generated/data/{}" download>csv</a>'.format(path)
            rows.append('<li><code>{}</code>{} <a href="{}/blob/{}/{}">on GitHub</a></li>'.format(
                html.escape(path), dl, REPO_URL, prov.commit, path))
    if a.kind == 'figure' and a.marks:
        p = os.path.join(GEN, 'data', 'marks', a.name + '.csv')
        lines = ['label,series,panel,value,text']
        for m in a.marks:
            lines.append(','.join('"{}"'.format(str(m.get(k, '')).replace('"', '""'))
                                  for k in ('label', 'series', 'panel', 'value', 'text')))
        write(p, '\n'.join(lines) + '\n')
        rows.append('<li>The values drawn: <a href="_generated/data/marks/{}.csv" download>csv</a></li>'.format(a.name))
    builder = prov.builder.get(a.name, '')
    cmd = r'.venv\Scripts\python.exe python\paper\build.py --only ' + a.name
    return ('<details class="oa-prov"><summary>Source</summary><ul>{}</ul><p>Built by <code>{}</code> from commit '
            '<code>{}</code>{}. Rebuild: <code>{}</code>; on another system substitute <code>.venv/bin/python</code></p></details>').format(
        ''.join(rows) or '<li>No traced inputs yet: run <code>build.py --map</code>.</li>',
        html.escape(builder) or 'python/paper', prov.commit,
        ' with uncommitted changes' if prov.dirty else '', html.escape(cmd))


def cleanSvg(svg, name, keep):
    """ The svg inlined: no prolog, scalable, and every id that is not a mark's prefixed with the figure's name so
    two figures on one page never share an id. """
    svg = re.sub(r'<\?xml[^>]*\?>|<!DOCTYPE[^>]*>|<!--.*?-->|<metadata>.*?</metadata>', '', svg, flags = re.S)
    ids = set(re.findall(r'\bid="([^"]+)"', svg)) - set(keep)
    pre = re.sub(r'[^A-Za-z0-9_-]', '_', name) + '-'
    if ids:
        pat = re.compile(r'(\bid="|url\(#|href="#)(' + '|'.join(re.escape(i) for i in sorted(ids, key = len,
                                                                                              reverse = True)) + r')(?=["\)])')
        svg = pat.sub(lambda m: m.group(1) + pre + m.group(2), svg)
    svg = re.sub(r'<svg\b([^>]*?)\swidth="[^"]*"', r'<svg\1', svg, count = 1)
    svg = re.sub(r'<svg\b([^>]*?)\sheight="[^"]*"', r'<svg\1', svg, count = 1)
    return svg.replace('<svg', '<svg class="oa-svgroot" role="img" focusable="false"', 1).strip()


def figureHtml(a, paper, refs, prov, here):
    ctx = refs.context(here)
    if a.base in paper.figures and a.name == a.base:
        cap, note = paper.figures[a.base]['caption'], paper.figures[a.base]['note']
    elif a.variant == 'vectorX' and a.base in paper.figures:
        cap = paper.figures[a.base]['caption'] + r', vector-$X_i$ calibration'
        note = TWINNOTE
    else:
        cap, note = a.ex.caption or a.name, a.ex.note or ''
    if a.variant == 'vectorX' and a.ex.caption and a.base not in paper.figures:
        cap = a.ex.caption + r', vector-$X_i$ calibration'
    a.captionTex, a.noteTex = cap, note
    if note and not note.lstrip().startswith(r'\textit{Note:}'):   # the paper's notes carry the label already
        note = r'\textit{Note:} ' + note                            # the print edition adds its own (groupLatex)
    if a.svg:
        body = '<div class="oa-svg">{}</div>'.format(cleanSvg(read(a.svg), a.name, [m['id'] for m in a.marks]))
    else:
        copy(a.png, os.path.join(GEN, 'figs', a.name + '.png'))
        body = '<div class="oa-img"><img src="_generated/figs/{}.png" alt="{}"></div>'.format(
            a.name, html.escape(plain(cap)))
    return ('<figure class="oa-figure" id="{}" data-name="{}" data-base="{}" data-variant="{}">'
            '<figcaption>{}{}</figcaption>{}{}{}</figure>').format(
        a.anchor, a.name, a.base, a.variant, badge(a, paper), TT.inline(cap, ctx), body,
        '<div class="oa-fignote">{}</div>'.format(collapseRuns(TT.inline(note, ctx))) if note else '',
        provenance(a, prov))


_RUN_HTML = re.compile(r' of the paper(</a>)(?=(?:, | and )<a href="[^"]*">[^<]* of the paper</a>)')
_RUN_TEX = re.compile(r' of the paper(?=(?:, | and )[\w.()]+ of the paper)')


def collapseRuns(s, latex = False):
    """ A run of the paper's references names the paper once, at its end: "tables 12, 13 and 16 of the
    paper", where each resolved on its own reads "12 of the paper, 13 of the paper and ...". """
    return _RUN_TEX.sub('', s) if latex else _RUN_HTML.sub(r'\1', s)


def tableHtml(a, paper, refs, prov, here):
    ctx = refs.context(here)
    tab = collapseRuns(a.table.html(ctx, number = badge(a, paper), tableId = a.anchor))
    return ('<div class="oa-panel" role="tabpanel" data-tab="{}" data-name="{}" data-variant="{}">'
            '<div class="oa-scroll">{}</div>{}</div>').format(a.base, a.name, a.variant, tab, provenance(a, prov))


def enrich(a, byName, report):
    """ Each mark of figure `a` as the page script reads it: where its table lives, on this page or another. """
    out, absent, rowless = [], {}, {}
    for m in a.marks:
        m = dict(m)
        t = m.get('table')
        if t:
            tgt = byName.get(t)
            if tgt is None or not tgt.ok:
                absent[t] = absent.get(t, 0) + 1
                m.pop('table', None)
            else:
                if m.get('row') and tgt.table and m['row'] not in tgt.table.keys:
                    rowless[t] = rowless.get(t, 0) + 1
                m['tab'], m['variant'] = tgt.base, tgt.variant
                if tgt.group != a.group:
                    q = 'g={}&variant={}&tab={}'.format(tgt.group, tgt.variant, tgt.base)
                    if m.get('row'):
                        q += '&row=' + m['row'].replace('@', '%40')
                    m['href'] = '{}.html?{}#{}'.format(tgt.chapter, q, tgt.group)
        out.append(m)
    for t, n in absent.items():
        report.append('{}: {} marks point to {}, which the site does not show (tooltips only)'.format(a.name, n, t))
    for t, n in rowless.items():
        report.append('{}: {} marks name rows {} does not key (table-level link)'.format(a.name, n, t))
    return out


def exhibitText(a):
    """ The registry text an asset shows: `textAlt` for the vector-X twin when given, else `text`. """
    return a.ex.textAlt if (a.variant == 'vectorX' and a.ex.textAlt) else a.ex.text


def textHtml(a, refs, here):
    t = exhibitText(a)
    if not t:
        return ''
    return '<div class="oa-text" data-kind="{}" data-tab="{}" data-variant="{}"><p>{}</p></div>'.format(
        a.kind, a.base, a.variant, collapseRuns(TT.inline(t, refs.context(here))))


def groupHtml(anchor, chapter, members, paper, refs, prov, byName, heads, report):
    figs = [a for a in members if a.kind == 'figure' and a.ok]
    tabs = [a for a in members if a.kind == 'table' and a.ok]
    textsF = ''.join(textHtml(a, refs, chapter) for a in figs)
    textsT = ''.join(textHtml(a, refs, chapter) for a in tabs)
    variants = sorted({a.variant for a in figs + tabs}, key = lambda v: v != 'commonX')
    out = ['<section class="oa-group" id="oagroup_{0}" data-group="{0}" data-variants="{1}">'.format(
        anchor, ' '.join(variants))]
    if len(variants) > 1:
        btns = ''.join('<button type="button" data-variant="{}" aria-pressed="{}">{}{}</button>'.format(
            v, 'true' if v == 'commonX' else 'false', VARIANT[v][0],
            ' <span class="oa-muted">({})</span>'.format(VARIANT[v][1]) if VARIANT[v][1] else '') for v in variants)
        out.append('<div class="oa-toolbar"><div class="oa-control" role="group" aria-label="Calibration">'
                   '<span class="oa-control-label">Calibration</span>{}</div>'.format(btns)
                   + ('<label class="oa-diff"><input type="checkbox"> Mark the cells that differ from the other '
                      'calibration</label><span class="oa-diff-status" aria-live="polite"></span>' if tabs else '')
                   + '</div>')
    # figure and tables: each text above its own kind; one kind only: the texts above the exhibits (a block of
    # their own, which the stylesheet stacks; RKB preferred this to a column beside the tables)
    layout = 'pair' if figs and tabs else ('text' if textsF or textsT else 'single')
    out.append('<div class="oa-layout oa-layout--{}">'.format(layout))
    if layout == 'text':
        out.append('<div class="oa-texts">' + textsF + textsT + '</div>')
        textsF = textsT = ''
    if figs:
        out.append('<div class="oa-figures">' + textsF + ''.join(figureHtml(a, paper, refs, prov, chapter) for a in figs)
                   + '</div>')
    if tabs:
        bases = []
        for a in tabs:
            if a.base not in bases:
                bases.append(a.base)
        label = {a.base: a.ex.tab or a.base for a in tabs}
        tablist = ''
        if len(bases) > 1:
            tablist = '<div class="oa-tabs" role="tablist">' + ''.join(
                '<button type="button" role="tab" data-tab="{}" aria-selected="{}">{}</button>'.format(
                    b, 'true' if k == 0 else 'false', html.escape(label[b])) for k, b in enumerate(bases)) + '</div>'
        out.append('<div class="oa-tables">' + textsT + tablist
                   + ''.join(tableHtml(a, paper, refs, prov, chapter) for a in tabs) + '</div>')
    out.append('</div>')
    marks = {a.name: enrich(a, byName, report) for a in figs if a.marks and a.svg}
    if marks:
        out.append('<script type="application/json" class="oa-marks">{}</script>'.format(
            json.dumps(marks, ensure_ascii = False).replace('</', '<\\/')))
    out.append('</section>')
    html_ = '\n'.join(out)
    # A note that points at the section it is shown in ("whose levels are printed in Online Appendix OA.3.4", inside
    # OA.3.4) reads "this section" here; the paper, which the note is written for, keeps the pointer.
    return re.sub(r'Online Appendix <a href="#{}">[^<]*</a>'.format(re.escape(anchor)), 'this section', html_)


def groupLatex(anchor, members, paper, refs):
    out, shown = [], []
    own = refs.heads.get(anchor, {}).get('number')

    def para(a):
        t = exhibitText(a)
        if not t:
            return ''
        t = refs.printTex(t)
        return t.replace('Online Appendix ' + own, 'this section') if own else t

    for a in members:
        if not a.ok:
            continue
        if a.scope == 'paper':
            shown.append(a)
            continue
        if para(a):
            out.append(r'\noindent ' + para(a) + r'\par\medskip')
        if a.kind == 'table':
            p = os.path.join(GEN, 'tex', a.name + '.tex')
            write(p, refs.printTex(a.tex))
            out.append(r'\setcounter{table}{' + str(int(a.number.split('.')[1]) - 1) + '}')
            out.append(r'\input{_generated/tex/' + a.name + '}')
        else:
            src = a.pdf or a.png
            ext = os.path.splitext(src)[1]
            copy(src, os.path.join(GEN, 'figs', a.name + ext))
            cap = getattr(a, 'captionTex', a.ex.caption or a.name)
            note = getattr(a, 'noteTex', a.ex.note or '')
            note, cap = refs.printTex(note), refs.printTex(cap)
            own = refs.heads.get(anchor, {}).get('number')
            if own:
                note = note.replace('Online Appendix ' + own, 'this section')
            out += [r'\begin{figure}[!htbp]', r'\centering',
                    r'\setcounter{figure}{' + str(int(a.number.split('.')[1]) - 1) + '}',
                    r'\caption{' + cap + '}',
                    r'\includegraphics[width=\linewidth]{_generated/figs/' + a.name + ext + '}']
            if note:
                out.append(r'\par\smallskip{\footnotesize\raggedright \textit{Note:} ' + note + r'\par}')
            out.append(r'\end{figure}')
    if shown:
        names = []
        for a in shown:
            if a.kind == 'table' and a.table:
                num = paper.numbers.get(a.table.label) if a.table.label else None
                name = 'table ' + num if num else "table ``" + (a.table.caption or a.name).rstrip('.') + "''"
            elif a.kind == 'figure':
                fig = paper.figures.get(a.base, {})
                num = paper.numbers.get(fig.get('label')) if fig.get('label') else None
                name = 'figure ' + num if num else "figure ``" + fig.get('caption', a.name).rstrip('.') + "''"
            else:
                continue
            try:
                where = paper.where(a.name)
            except Exception:
                where = ''
            names.append(name + (' (' + where + ')' if where else ''))
        lead = 'Beside these, the site shows the paper' if out else 'The site shows here the paper'
        head = [r'\noindent\textit{' + lead + "'" + r's ' + '; '.join(names)
                + r', which this edition does not reprint.}\par\medskip']
        for a, name in zip(shown, names):
            if para(a):                                # a text that opens with its own reference needs no lead
                lead = '' if para(a).lstrip().startswith(('Table', 'Figure')) else \
                    r'\textit{' + name[0].upper() + name[1:] + '.} '
                head.append(r'\noindent ' + lead + para(a) + r'\par\medskip')
        out[0:0] = head
    out.append(r'\FloatBarrier')
    return '\n'.join(out)


def include(html_, latex, wide = True):
    """ One exhibit group as a Quarto include: the HTML for the site, the LaTeX for the print edition. A figure
    beside its tables takes the page's width, anything else the body's and a little more. """
    # The hidden [$\cdot$] is there for pandoc, which loads MathJax only on a page whose Markdown has math; the
    # exhibits' math sits in raw HTML it does not read.
    return ('::: {.content-visible when-format="html"}\n[$\\cdot$]{.hidden}\n\n:::: {.'
            + ('column-page' if wide else 'column-body-outset') + '}\n```{=html}\n' + html_ + '\n```\n::::\n:::\n\n'
            '::: {.content-visible when-format="pdf"}\n```{=latex}\n' + latex + '\n```\n:::\n')


# ---------------------------------------------------------------------------------------------------
# Generated pages: the comparison of the two calibrations, the replication map, the version stamp.

def cellsOf(a):
    """ The body cells of a table, by row, each as (plain text, its LaTeX source). """
    ctx = TT.Context()
    return [[(re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', TT.inline(c.tex, ctx))).strip(), c.tex.strip())
             for c in r.cells] for r in a.table.body]


def blockLabels(table, cells):
    """ A readable label for each body row: its own first cell, or, where that is empty (the CRRA and endogenous-
    design tables name a block of rows once), the first label of its block, a block running between rules. """
    starts = [k for k, row in enumerate(table.body)
              if k == 0 or row.kind == 'group' or any(r in ('hline', 'midrule') for r in row.rulesBefore)]
    bounds, out = starts + [len(cells)], []
    for s, e in zip(bounds, bounds[1:]):
        lab = next((cc[0] for cc in cells[s:e] if cc and cc[0][0]), ('', ''))
        out += [c[0] if c and c[0][0] else lab for c in cells[s:e]]
    return out


def variantDiff(assets, paper, refs):
    """ For every table with a twin: how many body cells differ between the two calibrations, and in which rows. """
    by = {a.name: a for a in assets if a.kind == 'table' and a.ok}
    rows, lat = [], []
    seen = set()
    for a in assets:
        if a.kind != 'table' or not a.ok or a.variant != 'commonX' or a.name + TWIN not in by or a.name in seen:
            continue
        seen.add(a.name)
        b = by[a.name + TWIN]
        ca, cb = cellsOf(a), cellsOf(b)
        if len(ca) != len(cb):
            diff, where = None, 'different rows'
        else:
            diff, labels = 0, []
            texts = [[t for t, _ in r] for r in ca]
            for ra, rb, lab in zip(texts, [[t for t, _ in r] for r in cb], blockLabels(a.table, ca)):
                d = sum(x != y for x, y in zip(ra, rb)) + abs(len(ra) - len(rb))
                if d:
                    diff += d
                    if lab[0] and lab not in labels:
                        labels.append(lab)
        total = sum(len(r) for r in ca)
        count = '\u2013' if diff is None else '{} of {}'.format(diff, total)
        ctx = TT.Context()
        whereHtml = 'different rows' if diff is None else ', '.join(TT.inline(t, ctx) for _, t in labels) or 'none'
        whereTex = 'different rows' if diff is None else ', '.join(t for _, t in labels) or 'none'
        rows.append('<tr><td class="oa-l"><a href="{}">{}</a></td><td class="oa-c">{}</td><td class="oa-l">{}</td></tr>'
                    .format(refs.href(a, 'oecd'), TT.inline(a.table.caption or a.name, ctx), count, whereHtml))
        lat.append(r'{} & {} & {} \\'.format(a.table.caption or latexText(a.name), count.replace('\u2013', '--'),
                                                whereTex))
    h = ('<section class="oa-group" id="oagroup_oecd-vectorx" data-group="oecd-vectorx"><div class="oa-scroll">'
         '<table class="oa-table oa-table--wide"><caption>The cells that differ between the two calibrations, '
         'table by table</caption><thead><tr><th class="oa-l" scope="col">Table</th><th class="oa-c" scope="col">'
         'Cells that differ</th><th class="oa-l" scope="col">Rows in which they do</th></tr></thead><tbody>'
         + ''.join(rows) + '</tbody></table></div></section>')
    l = (r'{\footnotesize\begin{longtable}{p{6.2cm}p{2cm}p{6.2cm}}' '\n'
         r'\caption*{The cells that differ between the two calibrations, table by table}\\' '\n'
         r'\toprule Table & Cells that differ & Rows in which they do \\ \midrule \endhead' '\n'
         + '\n'.join(lat) + '\n' r'\bottomrule\end{longtable}}')
    return include(h, l)


def replicationMap(assets, paper, prov, refs):
    rows, lat = [], []
    for a in assets:
        if not a.ok:
            continue
        sec = refs.heads.get(a.group, {}).get('number', '')
        where = (('in the paper, ' + (paper.where(a.name) or '')) if a.scope == 'paper'
                 else '{} {}{}'.format('Table' if a.kind == 'table' else 'Figure', a.number, ', ' + sec if sec else ''))
        reads = ', '.join(p + (' ({} files)'.format(n) if n else '')
                          for p, n in prov.sources(a.name, getattr(a.table, 'banner', None) if a.table else None))
        rows.append('<tr><td class="oa-l"><a href="{}"><code>{}</code></a></td><td class="oa-l">{}</td>'
                    '<td class="oa-l">{}</td><td class="oa-l"><code>{}</code></td></tr>'.format(
                        refs.href(a, 'replication'), a.name, html.escape(where), html.escape(reads),
                        html.escape(prov.builder.get(a.name, ''))))
        lat.append(r'\texttt{{{}}} & {} & \texttt{{{}}} \\'.format(
            latexText(a.name).replace(r'\_', r'\_\allowbreak{}'), latexText(where), latexText(prov.builder.get(a.name, ''))))
    h = ('<section class="oa-group" id="oagroup_rep-map" data-group="rep-map"><div class="oa-scroll">'
         '<table class="oa-table oa-table--wide oa-table--map"><caption>Every exhibit, where it appears, what it reads, '
         'which builder makes it</caption><thead><tr><th class="oa-l" scope="col">Output</th><th class="oa-l" scope="col">'
         'Where</th><th class="oa-l" scope="col">Reads</th><th class="oa-l" scope="col">Builder</th></tr></thead><tbody>'
         + ''.join(rows) + '</tbody></table></div></section>')
    l = (r'{\footnotesize\begin{longtable}{p{5.2cm}p{4.4cm}p{5.4cm}}' '\n'
         r'\toprule Output & Where & Builder \\ \midrule \endhead' '\n' + '\n'.join(lat) + '\n'
         r'\bottomrule\end{longtable}}')
    return include(h, l)


def version(prov, paper):
    dirty = ' with uncommitted changes in `results/paper` or `python/paper`' if prov.dirty else ''
    nums = ('' if paper.fresh else ' The paper\u2019s section, table and figure numbers are counted from its '
            'source, as LaTeX sets them; its equations, which are not counted, are referred to by their section.')
    return ('Built on {} from commit [`{}`]({}/commit/{}){}.{}\n'.format(prov.date, prov.commit, REPO_URL, prov.commit,
                                                                       dirty, nums))


# ---------------------------------------------------------------------------------------------------

def build(verbose = True):
    report = []
    for d in ('groups', 'figs', 'tex', 'data'):
        os.makedirs(os.path.join(GEN, d), exist_ok = True)
    paper, prov, heads = Paper(), Provenance(), headings()
    assets = load(GROUPS, paper, report)
    number(assets)
    refs = Refs(assets, paper, heads)
    byName = {a.name: a for a in assets}
    for anchor, chapter, exs in GROUPS:
        members = [a for a in assets if a.group == anchor]
        if anchor == 'oecd-vectorx':
            text = variantDiff(assets, paper, refs)
        elif not any(a.ok for a in members):
            text = ('::: {.callout-note}\nThis exhibit has not been built yet: run `build.py`, then `build.py --site`.\n'
                    ':::\n')
        else:
            wide = any(a.ok and a.kind == 'figure' for a in members) and any(a.ok and a.kind == 'table' for a in members)
            text = include(groupHtml(anchor, chapter, members, paper, refs, prov, byName, heads, report),
                           groupLatex(anchor, members, paper, refs), wide)
        write(os.path.join(GEN, 'groups', anchor + '.qmd'), text)
    write(os.path.join(GEN, 'groups', 'rep-map.qmd'), replicationMap(assets, paper, prov, refs))
    write(os.path.join(GEN, 'version.qmd'), version(prov, paper))
    bib = os.path.join(C.PAPERTEX, 'References.bib')
    if os.path.exists(bib):
        copy(bib, os.path.join(GEN, 'References.bib'))
    if heads:
        writeMacros(heads)
    else:
        report.append('no OA headings found in writing/OnlineAppendix: onlineAppendix.tex left as it is')
    unknown = set()
    for a in assets:
        if a.table:
            unknown |= a.table.unknown
    if unknown:
        report.append('LaTeX outside the converter\u2019s vocabulary: ' + ', '.join(sorted(unknown)))
    shown = sum(a.ok for a in assets)
    if verbose:
        print('online appendix: {} of {} exhibits shown ({} online-only, numbered; {} the paper\u2019s), '
              'commit {}{}, paper numbers {}'.format(shown, len(assets), sum(a.ok and a.scope == 'online' for a in assets),
                                                       sum(a.ok and a.scope == 'paper' for a in assets), prov.commit,
                                                       ' (dirty)' if prov.dirty else '',
                                                       'from main.aux' if paper.fresh else 'counted from its source (main.aux stale)'))
        for line in report:
            print('  ' + line)
        print('next: quarto render ' + os.path.relpath(SITE, C.REPO))
    return {'assets': assets, 'report': report, 'paper': paper, 'heads': heads}


if __name__ == '__main__':
    build()
