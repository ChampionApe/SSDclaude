r""" Checks of the online appendix's generator (onlineAppendix.py) and table converter (texTable.py).

Run:  .venv\Scripts\python.exe python\paper\test_onlineAppendix.py      (pytest collects the same test_ functions)

Reads results/paper, writing/Paper and writing/OnlineAppendix; writes nothing (the generator itself is not run).
"""
import os, re, sys, glob, html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as C
import texTable as TT
import onlineAppendix as OA

TABLES = sorted(glob.glob(os.path.join(C.PAPERDIR, 'Tables', '*.tex')))


def test_every_table_converts():
    r""" Every built table parses in strict mode (no macro outside the converter's vocabulary), every body row
    fills the table's width, its row keys are unique and are exactly its `% row:` comments, and the HTML carries
    no TeX outside math. """
    assert TABLES, 'no built tables in results/paper/Tables'
    for f in TABLES:
        name = os.path.basename(f)[:-4]
        tex = OA.read(f)
        t = TT.parse(tex)
        h = t.html(TT.Context(strict = True))
        for r in t.body:
            if r.kind != 'group':
                assert sum(c.span for c in r.cells) == t.ncols, (name, [c.tex for c in r.cells])
        live = [l for l in tex.split('\n') if not l.lstrip().startswith('%')]
        assert len(t.keys) == sum('% row:' in l for l in live), name
        outside = re.sub(r'<span class="math inline">.*?</span>', '', h)
        assert not re.search(r'\\[A-Za-z]+', html.unescape(re.sub('<[^>]+>', '', outside))), name


def test_print_copy_resolves_every_reference():
    r""" The print edition's copy of a table holds no \ref, \eqref or \oa: each became text. """
    for f in TABLES:
        out = TT.printTex(OA.read(f), lambda label, eq = False: 'X', lambda key: 'OA.0')
        assert not re.search(r'\\(ref|eqref|oa)\s*\{', out), os.path.basename(f)


def test_converter_vocabulary():
    ctx = TT.Context(strict = True)
    assert TT.inline(r'$-0.09$ p.p.', ctx) == '\u22120.09 p.p.'
    assert TT.inline(r'France\textquotesingle s', ctx) == "France's"
    assert '\\(\\boldsymbol{\\theta}\\)' in TT.inline(r'$\bm{\theta}$', ctx)
    assert TT.inline(r'1960--2020', ctx) == '1960\u20132020'
    refs = TT.Context(ref = lambda label, eq = False: '[{}|{}]'.format(label, eq))
    assert TT.inline(r'eq.\ \eqref{eq:x}', refs) == '[eq:x|word]'
    assert TT.inline(r'of \eqref{eq:x}', refs) == 'of [eq:x|True]'
    try:
        TT.inline(r'\unknownmacro{a}', ctx)
        raise AssertionError('strict mode let an unknown macro through')
    except TT.UnknownMacro:
        pass


def test_headings_give_every_key_once():
    r""" The book's OA headings define each anchor once, with the numbering the paper's macros use. """
    heads = OA.headings()
    numbered = {k: h for k, h in heads.items() if h['number']}
    assert len(numbered) >= 26, sorted(numbered)
    numbers = [h['number'] for h in numbered.values()]
    assert len(set(numbers)) == len(numbers), numbers
    for anchor, chapter, _ in OA.GROUPS:
        assert anchor in heads, 'group {} has no heading in {}.qmd'.format(anchor, chapter)
        assert heads[anchor]['page'] == chapter + '.html', anchor


def test_paper_macros_cover_the_paper():
    r""" writing/Paper/onlineAppendix.tex defines every \oa key the paper uses. """
    defined = set(re.findall(r'\\oadef\{([^}]*)\}', OA.read(OA.MACROS)))
    for d in ('Sections', 'Appendix'):
        for f in glob.glob(os.path.join(C.PAPERTEX, d, '*.tex')):
            for k in re.findall(r'\\oa\{([^}]*)\}', OA.uncomment(OA.read(f))):
                assert k in defined, (os.path.basename(f), k)


def test_registry_names_are_outputs():
    r""" Every exhibit of the registry is an output build.py registers, so `--only` rebuilds it. """
    src = OA.read(os.path.join(HERE, 'build.py'))
    names = set(re.findall(r"_variants\(\s*'([^']+)'", src)) | set(re.findall(r"'([^']+)'\s*:\s*\(\s*'(?:table|figure)'", src))
    for _, _, exs in OA.GROUPS:
        for ex in exs:
            assert ex.name in names, ex.name


if __name__ == '__main__':
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print('ok    ' + name)
            except AssertionError as e:
                fails += 1
                print('FAIL  {}: {}'.format(name, e))
    print('{} failed'.format(fails))
    sys.exit(1 if fails else 0)
