r"""Static checks on the paper draft, run by every agent before it reports and by the main session at every gate.

Run:  PYTHONUTF8=1 .venv\Scripts\python.exe writing\checkPaper.py [--root writing/Paper] [--main main.tex] [--quiet]

Fails (exit 1) on: a \ref, \eqref, \pageref, \cref, \autoref or \nameref target with no \label; a label defined
twice; an \oa{key} that onlineAppendix.tex (generated from the online appendix's headings) does not define;
a citation key missing from the .bib that \addbibresource names; an \input, \includegraphics or
\addbibresource that does not resolve; a control byte (other than tab, LF, CR) in any .tex or .bib under root,
which is what a shell heredoc leaves behind. Reports: words per prose file with the Sections/ and Appendix/
totals, every \todo and every %% TODO tag, and every paragraph with more than one '---' (style guide: at most
one). Files are found by following \input from --main; --root may be another checkout's writing/Paper (an
agent's worktree), since every path is resolved against it. Generated tables (Tables/) are checked for
references and labels but not reported on for words, todos or dashes.
"""
import os, re, sys, argparse

REF = re.compile(r'\\(?:ref|eqref|pageref|cref|Cref|autoref|nameref)\*?\{([^}]*)\}')
LABEL = re.compile(r'\\label\{([^}]*)\}')
CITE_HEAD = re.compile(r'\\(?:[Tt]extcites?|[Pp]arencites?|footcites?|autocites?|citeauthor|citeyear|citetitle|nocite|cite[tp]?)\*?')
INPUT = re.compile(r'\\(?:input|include)\{([^}]*)\}')
GRAPHICS = re.compile(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}')
BIBRES = re.compile(r'\\addbibresource\{([^}]*)\}')
BIBKEY = re.compile(r'^\s*@(?!comment|string|preamble)\w+\s*\{\s*([^,\s]+)\s*,', re.M | re.I)
COMMENT = re.compile(r'(?<!\\)%.*')
TODO_TAG = re.compile(r'%%\s*(TODO[^\n]*)')
TODO_MACRO = re.compile(r'\\todo(?:\[[^\]]*\])?\{')
ENV_DROP = re.compile(r'\\begin\{(table|figure|align\*?|equation\*?|subequations|gather\*?|algorithm)\}.*?\\end\{\1\}', re.S)
MACRO_WORD = re.compile(r'\\(?:ref|eqref|pageref|cref|Cref|autoref|nameref|[Tt]extcites?|[Pp]arencites?|cite[tp]?|citeauthor|citeyear)\*?(?:\[[^\]]*\])*\{[^}]*\}')
MACRO_DROP = re.compile(r'\\(?:label|input|include|includegraphics|setcounter|renewcommand|newcommand|vspace|hspace|smalltitle)(?:\[[^\]]*\])?\{[^}]*\}')
OADEF = re.compile(r'\\oadef\{([^}]*)\}')                              # onlineAppendix.tex, generated from the book
OAUSE = re.compile(r'\\oa\{([^}]*)\}')

def read(path):
    with open(path, encoding = 'utf-8', errors = 'replace') as f:
        return f.read()

def rel(path, root):
    return os.path.relpath(path, root).replace('\\', '/')

def braceArg(text, i):
    """Content of the brace group opening at text[i] == '{', and the index after its closing brace."""
    depth = 0
    for j in range(i, len(text)):
        if text[j] == '{': depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0: return text[i + 1:j], j + 1
    return text[i + 1:], len(text)

def citeKeys(line):
    keys = []
    for m in CITE_HEAD.finditer(line):
        j = m.end()
        while j < len(line) and line[j] == '[':                       # optional arguments, \parencite[e.g.][]{a,b}
            j = line.index(']', j) + 1 if ']' in line[j:] else len(line)
        while j < len(line) and line[j] == '{':                       # one or more key groups, \textcites{a}{b}
            arg, j = braceArg(line, j)
            keys += [k.strip() for k in arg.split(',') if k.strip()]
    return keys

def resolve(root, name, exts):
    for cand in [name] + [name + e for e in exts]:
        p = os.path.normpath(os.path.join(root, cand))
        if os.path.isfile(p): return p
    return None

def collect(root, main):
    r"""Every .tex file reachable from main by \input, in order, and the \input targets that do not resolve."""
    files, missing, queue = [], [], [os.path.normpath(os.path.join(root, main))]
    while queue:
        f = queue.pop(0)
        if f in files: continue
        files.append(f)
        for m in INPUT.finditer(COMMENT.sub('', read(f))):
            p = resolve(root, m.group(1), ['.tex'])
            queue.append(p) if p else missing.append((rel(f, root), m.group(1)))
    return files, missing

def words(text):
    t = COMMENT.sub('', text)
    t = ENV_DROP.sub(' ', t)
    t = re.sub(r'\\\[.*?\\\]', ' ', t, flags = re.S)
    t = MACRO_DROP.sub(' ', t)
    t = MACRO_WORD.sub(' X ', t)                                        # a reference or citation reads as one word
    t = re.sub(r'\$\$.*?\$\$', ' X ', t, flags = re.S)
    t = re.sub(r'\$[^$]*\$', ' X ', t)                                  # an inline symbol reads as one word
    t = re.sub(r'\\[A-Za-z]+\*?', ' ', t)                               # remaining macro names; their arguments stay
    return len([w for w in re.split(r'[\s{}\[\]]+', t) if re.search(r'[A-Za-z0-9]', w)])

def todos(text):
    out = []
    for i, line in enumerate(text.split('\n'), 1):
        for m in TODO_TAG.finditer(line):
            out.append((i, m.group(1).strip()))
        for m in TODO_MACRO.finditer(COMMENT.sub('', line)):
            out.append((i, '\\todo{' + braceArg(line, m.end() - 1)[0].strip() + '}'))
    return out

def dashParagraphs(text):
    out, start, buf = [], 1, []
    lines = COMMENT.sub('', text).split('\n') + ['']
    for i, line in enumerate(lines, 1):
        if line.strip():
            if not buf: start = i
            buf.append(line)
        elif buf:
            n = '\n'.join(buf).count('---')
            if n > 1: out.append((start, n))
            buf = []
    return out

def controlBytes(path):
    hits, line, col = [], 1, 0
    for b in open(path, 'rb').read():
        col += 1
        if b == 10: line, col = line + 1, 0
        elif (b < 32 and b not in (9, 13)) or b == 127: hits.append((line, col, b))
    return hits

def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--root', default = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Paper'))
    p.add_argument('--main', default = 'main.tex')
    p.add_argument('--quiet', action = 'store_true', help = 'failures and totals only')
    a = p.parse_args()
    root = os.path.abspath(a.root)
    files, missingInputs = collect(root, a.main)
    prose = lambda f: not rel(f, root).startswith('Tables/') and rel(f, root) not in ('main.tex', 'Packages.tex')
    labels, refs, cites, graphics, bibs, oaKeys, oaUses = {}, [], [], [], [], set(), []
    for f in files:
        r = rel(f, root)
        for i, line in enumerate(read(f).split('\n'), 1):
            line = COMMENT.sub('', line)
            for m in LABEL.finditer(line): labels.setdefault(m.group(1).strip(), []).append((r, i))
            for m in REF.finditer(line): refs += [(r, i, k.strip()) for k in m.group(1).split(',')]
            oaKeys |= {m.group(1).strip() for m in OADEF.finditer(line)}
            oaUses += [(r, i, m.group(1).strip()) for m in OAUSE.finditer(line)]
            cites += [(r, i, k) for k in citeKeys(line)]
            graphics += [(r, i, m.group(1)) for m in GRAPHICS.finditer(line)]
            bibs += [m.group(1) for m in BIBRES.finditer(line)]
    fails = 0
    missingRefs = [(r, i, k) for r, i, k in refs if k not in labels]
    dupLabels = {k: v for k, v in labels.items() if len(v) > 1}
    print('== refs: {} missing, {} duplicate labels ({} labels, {} references)'.format(len(missingRefs), len(dupLabels), len(labels), len(refs)))
    for r, i, k in missingRefs: print('  {}:{}  {}'.format(r, i, k))
    for k, v in dupLabels.items(): print('  {}  defined at {}'.format(k, ', '.join('{}:{}'.format(*x) for x in v)))
    fails += len(missingRefs) + len(dupLabels)
    missingOa = [(r, i, k) for r, i, k in oaUses if k not in oaKeys]
    print('== online appendix: {} \\oa keys missing ({} keys defined, {} uses)'.format(len(missingOa), len(oaKeys), len(oaUses)))
    for r, i, k in missingOa: print('  {}:{}  \\oa{{{}}}'.format(r, i, k))
    fails += len(missingOa)
    keys = set()
    for b in bibs:
        path = resolve(root, b, ['.bib'])
        if path: keys |= set(BIBKEY.findall(read(path)))
        else: missingInputs.append(('Packages.tex', b))
    missingCites = [(r, i, k) for r, i, k in cites if k not in keys]
    print('== cites: {} missing ({} keys in {}, {} citations)'.format(len(missingCites), len(keys), ', '.join(bibs) or 'no .bib', len(cites)))
    for r, i, k in missingCites: print('  {}:{}  {}'.format(r, i, k))
    fails += len(missingCites)
    missingGraphics = [(r, i, g) for r, i, g in graphics if not resolve(root, g, ['.pdf', '.eps', '.png', '.jpg'])]
    print('== inputs: {} missing ({} files followed, {} graphics)'.format(len(missingInputs) + len(missingGraphics), len(files), len(graphics)))
    for r, g in missingInputs: print('  {}  \\input{{{}}}'.format(r, g))
    for r, i, g in missingGraphics: print('  {}:{}  \\includegraphics{{{}}}'.format(r, i, g))
    fails += len(missingInputs) + len(missingGraphics)
    scanned = [os.path.join(d, n) for d, _, ns in os.walk(root) for n in ns if n.endswith(('.tex', '.bib'))]
    hits = [(rel(f, root), l, c, b) for f in scanned for l, c, b in controlBytes(f)]
    print('== bytes: {} control bytes in {} files'.format(len(hits), len(scanned)))
    for r, l, c, b in hits[:50]: print('  {}:{}:{}  0x{:02x}'.format(r, l, c, b))
    fails += len(hits)
    if not a.quiet:
        counts = [(rel(f, root), words(read(f))) for f in files if prose(f)]
        print('== words')
        for r, n in counts: print('  {:<48} {:>6}'.format(r, n))
        for part in ('Sections/', 'Appendix/'):
            print('  {:<48} {:>6}'.format(part + 'total', sum(n for r, n in counts if r.startswith(part))))
        items = [(rel(f, root), i, t) for f in files if prose(f) for i, t in todos(read(f))]
        print('== todo: {}'.format(len(items)))
        for r, i, t in items: print('  {}:{}  {}'.format(r, i, t[:140]))
        dashes = [(rel(f, root), i, n) for f in files if prose(f) for i, n in dashParagraphs(read(f))]
        print('== dashes: {} paragraphs with more than one ---'.format(len(dashes)))
        for r, i, n in dashes: print('  {}:{}  {}'.format(r, i, n))
    print('== {}'.format('FAIL' if fails else 'OK'))
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
