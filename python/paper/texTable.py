r""" A table built by python/paper, read back from its tex and written as HTML for the online appendix
(onlineAppendix.py), or rewritten for the appendix's print edition.

The parser covers the builders' own vocabulary and nothing wider: the BANNER lines, threeparttable with
\caption, \label and a tablenotes block, tabular or tabularx with any column spec, booktabs rules, \hline,
\cline, \cmidrule, row spacing `\\[..]`, \multicolumn, \tnote, and in text the macros of TEXTMAC, SYMBOLS and
ESCAPES; math is kept for MathJax, as pandoc writes it. A row's `% row: <key>` comment (the online appendix's
brief, 2.2) becomes its `data-row`. Lines commented out in the tex, the rows the paper hides, are dropped. A
macro outside the vocabulary is collected in Table.unknown and raises under strict=True, so a new builder
idiom shows up in the test instead of reaching the page as raw TeX.

\ref, \eqref and the citation macros are resolved by callbacks the caller passes (Context): this module knows
nothing about the paper or the appendix's numbering.
"""
import re, html

__all__ = ['Context', 'Table', 'parse', 'inline', 'printTex', 'UnknownMacro']


class UnknownMacro(ValueError):
    pass


class Context:
    r""" What `inline` needs from outside. `ref(label, eq)` returns the HTML for \ref{label}; eq is True for a
    bare \eqref and 'word' for one after "eq." or "equation", which the callback then writes itself;
    `cite(keys, textual)` the HTML for a citation; `oa(key)` the HTML for the paper's \oa{key}, and for \oahome
    when key is None. `unknown` collects macros outside the vocabulary. """
    def __init__(self, ref = None, cite = None, oa = None, strict = False):
        self.ref = ref or (lambda label, eq = False: html.escape(label))
        self.cite = cite or (lambda keys, textual = False: html.escape(', '.join(keys)))
        self.oa = oa or (lambda key: html.escape(key or 'the online appendix'))
        self.strict = strict
        self.unknown = set()


# ---------------------------------------------------------------------------------------------------
# Scanning helpers. Every scanner skips a backslash together with the character after it, so \{ \} \& \%
# and \\ never count as structure.

def commentStart(line):
    """ Index of the % that opens a comment on `line`, or None (a % preceded by an odd run of backslashes is
    a literal percent sign). """
    for m in re.finditer('%', line):
        k, j = 0, m.start() - 1
        while j >= 0 and line[j] == '\\':
            k, j = k + 1, j - 1
        if k % 2 == 0:
            return m.start()
    return None


def braceArg(text, i):
    """ (content, index after the closing brace) of the group opening at text[i] == '{'. """
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    raise ValueError('unbalanced brace group at {}: {!r}'.format(i, text[i:i + 60]))


def optArg(text, i):
    """ (content, index after) of an optional [..] argument at text[i], or (None, i). """
    if i < len(text) and text[i] == '[':
        j = text.index(']', i)
        return text[i + 1:j], j + 1
    return None, i


def topSplit(text, sep, start = 0, end = None):
    r""" Spans (s, e) of `text[start:end]` split at the top-level occurrences of `sep`, '&' or '\\\\'. """
    end = len(text) if end is None else end
    spans, depth, s, j = [], 0, start, start
    while j < end:
        c = text[j]
        if c == '\\':
            if sep == '\\\\' and j + 1 < end and text[j + 1] == '\\' and depth == 0:
                spans.append((s, j))
                s = j = j + 2
                continue
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif c == sep and depth == 0:
            spans.append((s, j))
            s = j + 1
        j += 1
    spans.append((s, end))
    return spans


# ---------------------------------------------------------------------------------------------------
# Text and math.

TEXTMAC = {'textbf': ('<strong>', '</strong>'), 'textit': ('<em>', '</em>'), 'emph': ('<em>', '</em>'),
           'textsl': ('<em>', '</em>'), 'textrm': ('', ''), 'textsf': ('', ''), 'textup': ('', ''),
           'textnormal': ('', ''), 'mbox': ('', ''), 'text': ('', ''), 'textsc': ('<span class="oa-sc">', '</span>'),
           'textsuperscript': ('<sup>', '</sup>'), 'textsubscript': ('<sub>', '</sub>'),
           'tnote': ('<sup class="oa-tnote">', '</sup>'), 'underline': ('<u>', '</u>')}
SYMBOLS = {'textquotesingle': "'", 'ldots': '…', 'dots': '…', 'textendash': '–', 'textemdash': '—',
           'S': '§', 'textasciitilde': '~', 'textbackslash': '\\', 'centering': '', 'raggedright': '',
           'raggedleft': '', 'footnotesize': '', 'small': '', 'normalsize': '', 'scriptsize': '', 'noindent': '',
           'arraybackslash': '', 'hfill': ' ', 'quad': ' ', 'qquad': ' ', 'newline': '<br>', 'par': ' ',
           'relax': '', 'xspace': '', 'ignorespaces': '', 'unskip': '', 'LaTeX': 'LaTeX', 'TeX': 'TeX'}
ESCAPES = {'%': '%', '&': '&amp;', '_': '_', '#': '#', '$': '$', '{': '{', '}': '}', ',': '\u2009',
           ' ': ' ', ';': ' ', ':': ' ', '!': '', '/': '', '-': '', '\\': '<br>', "'": "'", '`': '`'}
CITE = re.compile(r'(?:[Tt]extcite|[Pp]arencite|cite[tp]?|citeauthor|citeyear)s?$')


NUMERIC = re.compile(r'(?:<|>|\\leq?\s*|\\geq?\s*)?[-+]?\d[\d.,]*(?:\\%)?|\[[-+\d., ]+\]')


def _mathHtml(tex):
    """ Math for MathJax, as pandoc writes it; a bare signed number (or a bound, or a list of numbers) is set
    as text with a true minus sign, so a column of numbers keeps one typeface. """
    t = tex.strip()
    if NUMERIC.fullmatch(t):
        t = re.sub(r'\\leq?\s*', '\u2264', re.sub(r'\\geq?\s*', '\u2265', t))
        return html.escape(t.replace('\\%', '%').replace('-', '\u2212'), quote = False)
    tex = re.sub(r'\\bm\s*\{', r'\\boldsymbol{', tex)
    return '<span class="math inline">\\(' + html.escape(tex, quote = False) + '\\)</span>'


def _plain(s):
    """ A run of plain text: TeX ligatures and quotes, HTML-escaped. """
    s = html.escape(s, quote = False)
    s = s.replace('---', '\u2014').replace('--', '\u2013').replace('``', '\u201c').replace("''", '\u201d')
    s = s.replace('`', '\u2018').replace('~', '\u00a0')
    return re.sub(r'\s+', ' ', s)


def inline(tex, ctx):
    """ A run of LaTeX text (a cell, a caption, a note) as HTML. """
    out, i, n = [], 0, len(tex)
    while i < n:
        c = tex[i]
        if c == '$':
            j = i + 1
            while j < n and not (tex[j] == '$' and tex[j - 1] != '\\'):
                j += 1
            out.append(_mathHtml(tex[i + 1:j]))
            i = j + 1
        elif c == '{':
            arg, i = braceArg(tex, i)
            out.append(inline(arg, ctx))
        elif c == '}':
            i += 1
        elif c == '\\':
            if i + 1 < n and tex[i + 1] == '(':
                j = tex.index('\\)', i + 2)
                out.append(_mathHtml(tex[i + 2:j]))
                i = j + 2
                continue
            m = re.match(r'\\([A-Za-z]+)\*?', tex[i:])
            if not m:
                sym = tex[i + 1] if i + 1 < n else ''
                if sym in ESCAPES:
                    out.append(ESCAPES[sym])
                else:
                    ctx.unknown.add('\\' + sym)
                    if ctx.strict:
                        raise UnknownMacro('\\' + sym)
                i += 2
                continue
            name, i = m.group(1), i + m.end()
            if name in ('ref', 'eqref', 'autoref', 'cref', 'Cref', 'nameref'):
                arg, i = braceArg(tex, _skipSpace(tex, i))
                eq = name == 'eqref'
                if eq:                                     # "eq.\ \eqref{x}": the callback writes the word itself
                    sofar = ''.join(out)
                    m = re.search(r'(?:eq\.|equation)[\s ]*$', sofar)
                    if m:
                        out, eq = [sofar[:m.start()]], 'word'
                out.append(ctx.ref(arg.strip(), eq))
            elif name == 'oa':
                arg, i = braceArg(tex, _skipSpace(tex, i))
                out.append(ctx.oa(arg.strip()))
            elif name == 'oahome':
                out.append(ctx.oa(None))
                i = _skipSpace(tex, i)
            elif CITE.match(name):
                j = _skipSpace(tex, i)
                while j < n and tex[j] == '[':
                    _, j = optArg(tex, j)
                arg, i = braceArg(tex, j)
                out.append(ctx.cite([k.strip() for k in arg.split(',')], name.lower().startswith('textcite')))
            elif name in TEXTMAC:
                arg, i = braceArg(tex, _skipSpace(tex, i))
                a, b = TEXTMAC[name]
                out.append(a + inline(arg, ctx) + b)
            elif name == 'url':
                arg, i = braceArg(tex, _skipSpace(tex, i))
                out.append('<a href="{0}">{0}</a>'.format(html.escape(arg)))
            elif name == 'href':
                url, i = braceArg(tex, _skipSpace(tex, i))
                arg, i = braceArg(tex, _skipSpace(tex, i))
                out.append('<a href="{}">{}</a>'.format(html.escape(url.replace('\\#', '#')), inline(arg, ctx)))
            elif name in SYMBOLS:
                out.append(SYMBOLS[name])
                i = _skipSpace(tex, i)
            else:
                ctx.unknown.add('\\' + name)
                if ctx.strict:
                    raise UnknownMacro('\\' + name)
                i = _skipSpace(tex, i)
        else:
            j = i
            while j < n and tex[j] not in '${}\\':
                j += 1
            out.append(_plain(tex[i:j]))
            i = j
    return ''.join(out)


def _skipSpace(tex, i):
    while i < len(tex) and tex[i] in ' \t\n':
        i += 1
    return i


# ---------------------------------------------------------------------------------------------------
# The table.

RULE = re.compile(r'\\(?:(cline|cmidrule)\s*(?:\([^)]*\))?\s*\{[^}]*\}'
                  r'|(toprule|midrule|bottomrule|addlinespace)(?![A-Za-z])(?:\s*\[[^\]]*\])?'
                  r'|(hline)(?![A-Za-z]))')
ALIGN = {'l': 'l', 'c': 'c', 'r': 'r', 'X': 'l', 'Y': 'c', 'p': 'l', 'm': 'l', 'b': 'l',
         'C': 'c', 'L': 'l', 'R': 'r', 'S': 'c', 'D': 'c'}


def columnAligns(spec):
    """ 'l'/'c'/'r' per column of a tabular spec; `>{\\raggedright...}X` counts as left. """
    out, i, pending = [], 0, None
    while i < len(spec):
        c = spec[i]
        if c in ' |\n':
            i += 1
        elif c in '>@<!':
            arg, i = braceArg(spec, spec.index('{', i))
            if c == '>':
                pending = ('l' if 'raggedright' in arg else 'r' if 'raggedleft' in arg
                           else 'c' if 'centering' in arg else None)
        elif c == '*':
            k, i = braceArg(spec, spec.index('{', i))
            sub, i = braceArg(spec, spec.index('{', i))
            out += columnAligns(sub) * int(k)
        elif c in ALIGN:
            out.append(pending or ALIGN[c])
            pending = None
            i += 1
            if c in 'pmbCLRSD' and i < len(spec) and spec[i] == '{':
                _, i = braceArg(spec, i)
        else:
            out.append(pending or 'c')
            pending = None
            i += 1
    return out


class Cell:
    def __init__(self, tex, span = 1, align = None):
        self.tex, self.span, self.align = tex, span, align


class Row:
    def __init__(self, cells, key, rulesBefore):
        self.cells, self.key, self.rulesBefore = cells, key, rulesBefore
        self.kind = 'body'


class Table:
    r""" A parsed table. `head` and `body` are lists of Row; `notes` a list of (marker, tex); `banner` the
    BANNER's fields ('source', 'rebuild'); `keys` the row keys in order. """

    def __init__(self, tex, strict = False):
        self.tex = tex
        self.unknown = set()
        text, ends, self.banner = _clean(tex)
        self.text = text
        self.caption = _macroArg(text, 'caption')
        self.label = _macroArg(text, 'label')
        m = re.search(r'\\begin\{(tabularx|tabular\*?|longtable)\}', text)
        if not m:
            raise ValueError('no tabular in table')
        env, j = m.group(1), m.end()
        if env.startswith('tabularx') or env == 'tabular*':
            _, j = braceArg(text, text.index('{', j))              # the width
        spec, j = braceArg(text, text.index('{', j))
        self.aligns = columnAligns(spec)
        k = text.index('\\end{' + env + '}', j)
        self.rows = _rows(text, j, k, ends)
        self.ncols = max(len(self.aligns), max((sum(c.span for c in r.cells) for r in self.rows), default = 0))
        self.aligns += ['c'] * (self.ncols - len(self.aligns))
        heads = _headCount(self.rows)
        self.head, self.body = self.rows[:heads], self.rows[heads:]
        for r in self.head:
            r.kind = 'head'
        for r in self.body:
            if len(r.cells) == 1 and r.cells[0].span >= self.ncols:
                r.kind = 'group'
        self.notes = _notes(text)
        self.keys = [r.key for r in self.body if r.key]
        if len(set(self.keys)) != len(self.keys):
            raise ValueError('duplicate row keys in {}: {}'.format(self.label, self.keys))
        self.strict = strict

    def html(self, ctx, number = '', tableId = None, attrs = ''):
        r""" The table as one HTML fragment: <table> with the caption, then the notes. `number` is the HTML
        placed before the caption (the online appendix's numbering); `attrs` extra attributes for <table>. """
        out = ['<table class="oa-table"{}{}>'.format(' id="{}"'.format(tableId) if tableId else '', attrs)]
        cap = inline(self.caption or '', ctx)
        out.append('<caption>{}{}</caption>'.format(number, cap))
        if self.head:
            out.append('<thead>')
            for r in self.head:
                out.append(self._tr(r, ctx, 'th'))
            out.append('</thead>')
        out.append('<tbody>')
        for k, r in enumerate(self.body):
            out.append(self._tr(r, ctx, 'td', first = k == 0))
        out.append('</tbody></table>')
        if self.notes:
            out.append('<div class="oa-notes">')
            for marker, t in self.notes:
                mk = '<span class="oa-note-mark">{}</span> '.format(inline(marker, ctx)) if marker else ''
                out.append('<p>{}{}</p>'.format(mk, inline(t, ctx)))
            out.append('</div>')
        self.unknown |= ctx.unknown
        return '\n'.join(out)

    def _tr(self, row, ctx, tag, first = False):
        cls = []
        if row.kind == 'group':
            cls.append('oa-grouprow')
        if not first and row.kind != 'head' and any(r in ('hline', 'midrule') for r in row.rulesBefore):
            cls.append('oa-sep')
        attrs = ''.join([' class="{}"'.format(' '.join(cls)) if cls else '',
                         ' data-row="{}"'.format(html.escape(row.key)) if row.key else ''])
        cells, col = [], 0
        for c in row.cells:
            align = c.align or (self.aligns[col] if col < len(self.aligns) else 'c')
            t = tag if row.kind != 'group' else 'th'
            span = ' colspan="{}"'.format(c.span) if c.span > 1 else ''
            scope = ' scope="col"' if tag == 'th' and row.kind == 'head' else ''
            cells.append('<{0} class="oa-{1}"{2}{3}>{4}</{0}>'.format(t, align, span, scope, inline(c.tex, ctx)))
            col += c.span
        return '<tr{}>{}</tr>'.format(attrs, ''.join(cells))


def _clean(tex):
    """ (the tex without banner and comments, [(offset of each line's end, its row key)], banner fields). """
    out, ends, banner, pos = [], [], {}, 0
    for line in tex.split('\n'):
        if line.startswith('%%'):
            m = re.match(r'%%\s*(\w+):\s*(.*)$', line)
            if m:
                banner[m.group(1).lower()] = m.group(2).strip()
            continue
        key, i = None, commentStart(line)
        if i is not None:
            m = re.match(r'%\s*row:\s*(\S+)', line[i:])
            key = m.group(1) if m else None
            line = line[:i]
        out.append(line)
        pos += len(line)
        ends.append((pos, key))
        pos += 1
    return '\n'.join(out), ends, banner


def _macroArg(text, name):
    m = re.search(r'\\' + name + r'\s*\{', text)
    return braceArg(text, m.end() - 1)[0] if m else None


def _rows(text, start, end, ends):
    rows, pending, first = [], [], True
    for s, e in topSplit(text, '\\\\', start, end):
        if not first:
            _, s = optArg(text, s)                                   # \\[1ex]: the spacing of the row above
        first = False
        seg = text[s:e]
        content, before, after, pos = [], [], [], 0
        for m in RULE.finditer(seg):
            piece = seg[pos:m.start()]
            if piece.strip():
                content.append((s + pos, s + m.start()))
            (after if content else before).append(next(g for g in m.groups() if g))
            pos = m.end()
        if seg[pos:].strip():
            content.append((s + pos, e))
        if not content:
            pending += before
            continue
        cs, ce = content[0][0], content[-1][1]
        body = text[cs:ce]
        last = cs + len(body.rstrip())
        key = _keyAt(ends, last)
        cells = []
        for a, b in topSplit(text, '&', cs, ce):
            cells.append(_cell(text[a:b].strip()))
        rows.append(Row(cells, key, pending + before))
        pending = after
    if pending and rows:
        rows[-1].rulesAfter = pending
    return rows


def _keyAt(ends, offset):
    """ The row key of the line the offset lies on. """
    for e, key in ends:
        if offset <= e:
            return key
    return None


def _cell(tex):
    m = re.match(r'\\multicolumn\s*\{', tex)
    if not m:
        return Cell(tex)
    k, j = braceArg(tex, m.end() - 1)
    spec, j = braceArg(tex, _skipSpace(tex, j))
    content, j = braceArg(tex, _skipSpace(tex, j))
    al = next((ALIGN[ch] for ch in spec if ch in 'lcr'), 'c')
    return Cell(content + tex[j:], int(k), al)


def _headCount(rows):
    for k, r in enumerate(rows):
        if k and 'midrule' in r.rulesBefore:
            return k
    if not any('midrule' in r.rulesBefore for r in rows):
        for k, r in enumerate(rows):
            if k and 'hline' in r.rulesBefore and k < len(rows):
                return k
    return 0


def _notes(text):
    m = re.search(r'\\begin\{tablenotes\}', text)
    if not m:
        return []
    j = m.end()
    _, j = optArg(text, j)
    k = text.index('\\end{tablenotes}', j)
    body = re.sub(r'\\(footnotesize|small|scriptsize)\b', '', text[j:k])
    items = []
    for part in re.split(r'\\item\b', body)[1:]:
        part = part.lstrip()
        marker, p = optArg(part, 0)
        items.append((marker or '', part[p:].strip()))
    return items


def parse(tex, strict = False):
    return Table(tex, strict)


# ---------------------------------------------------------------------------------------------------
# The print edition.

def printTex(tex, ref, oa = None):
    r""" The tex with every \ref and \eqref replaced by `ref(label, eq)`, and every \oa{key} by `oa(key)` (\oahome
    by `oa(None)`), all plain LaTeX text, so the print edition never shows an unresolved reference to a label
    or a macro that only the paper defines. """
    tex = re.sub(r'(?:eq\.\\?\s*~?|equation\s+)\\eqref\s*\{([^}]*)\}', lambda m: ref(m.group(1).strip(), 'word'), tex)
    tex = re.sub(r'\\(ref|eqref)\s*\{([^}]*)\}', lambda m: ref(m.group(2).strip(), m.group(1) == 'eqref'), tex)
    if oa is not None:
        tex = re.sub(r'\\oa\s*\{([^}]*)\}', lambda m: oa(m.group(1).strip()), tex)
        tex = re.sub(r'\\oahome\b', lambda m: oa(None), tex)
    return tex
