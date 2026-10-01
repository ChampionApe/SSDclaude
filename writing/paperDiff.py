"""
Build the paper at an old git revision and a latexdiff PDF of the changes from it to the current draft.

    python writing/paperDiff.py                  # old = merge-base of main and HEAD, new = working tree
    python writing/paperDiff.py --old 77ba943    # any git ref
    python writing/paperDiff.py --new HEAD       # compare against a commit instead of the working tree

Writes to writing/exports/paperDiff/ (gitignored, skipped by overleaf.py):
    old_<ref>.pdf             the full paper as it stood at the old revision
    diff_<ref>_to_<new>.pdf   the current draft with deletions struck out in red and additions underlined in blue
The build trees are kept under exports/paperDiff/build/ so a failed compile can be inspected (*.log).

The diff is built in a copy of the new tree, with figures that exist only in the old tree copied in, so
deleted figures still render. Generated tables are diffed as text like any other input. Needs latexdiff,
latexmk, pdflatex and biber on PATH (TeX Live).
"""
import os, sys, shutil, subprocess, argparse, tarfile, io

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PAPER = 'writing/Paper'
OUT = os.path.join(HERE, 'exports', 'paperDiff')
BUILD = os.path.join(OUT, 'build')


def git(*args):
    return subprocess.run(['git', '-C', REPO, *args], check = True, capture_output = True).stdout


def exportTree(ref, dest):
    """ writing/Paper at git ref -> dest (dest/main.tex etc.). """
    data = git('archive', '--format=tar', ref, PAPER)
    with tarfile.open(fileobj = io.BytesIO(data)) as t:
        for m in t.getmembers():
            rel = os.path.relpath(m.name, PAPER)
            if m.isfile():
                p = os.path.join(dest, rel)
                os.makedirs(os.path.dirname(p), exist_ok = True)
                with open(p, 'wb') as f:
                    f.write(t.extractfile(m).read())


def copyWorkingTree(dest):
    ignore = shutil.ignore_patterns('*.aux', '*.log', '*.bbl', '*.blg', '*.bcf', '*.out', '*.fls',
                                    '*.fdb_latexmk', '*.run.xml', '*.synctex.gz', 'main.pdf')
    shutil.copytree(os.path.join(REPO, PAPER), dest, ignore = ignore)


def addMissing(src, dest):
    """ Copy every non-.tex file in src that dest lacks (figures removed in the new draft). """
    for d, _, files in os.walk(src):
        for f in files:
            if f.endswith('.tex'):
                continue
            rel = os.path.relpath(os.path.join(d, f), src)
            p = os.path.join(dest, rel)
            if not os.path.exists(p):
                os.makedirs(os.path.dirname(p), exist_ok = True)
                shutil.copy2(os.path.join(d, f), p)


def compile(folder, main):
    r = subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', '-f', main], cwd = folder,
                       capture_output = True, text = True, errors = 'replace')
    pdf = os.path.join(folder, os.path.splitext(main)[0] + '.pdf')
    if not os.path.exists(pdf):
        sys.exit(f'compile failed, see {os.path.join(folder, os.path.splitext(main)[0] + ".log")}\n'
                 + r.stdout[-2000:])
    if r.returncode:
        print(f'  warning: latexmk reported errors in {folder} (PDF written anyway; check the .log)')
    return pdf


def safe(ref):
    return ref.replace('/', '-').replace('~', '-').replace('^', '-')


def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('--old', help = 'git ref of the old version (default: merge-base of main and HEAD)')
    p.add_argument('--new', help = 'git ref of the new version (default: the working tree)')
    p.add_argument('--no-old-pdf', action = 'store_true', help = 'skip building the full old PDF')
    a = p.parse_args()

    oldRef = a.old or git('merge-base', 'main', 'HEAD').decode().strip()
    oldTag = safe(git('rev-parse', '--short', oldRef).decode().strip())
    newTag = safe(git('rev-parse', '--short', a.new).decode().strip()) if a.new else 'working'

    if os.path.exists(BUILD):
        shutil.rmtree(BUILD)
    oldDir, newDir = os.path.join(BUILD, 'old'), os.path.join(BUILD, 'diff')
    os.makedirs(oldDir)
    print(f'old: {oldRef} ({oldTag})   new: {a.new or "working tree"}')
    exportTree(oldRef, oldDir)
    if a.new:
        os.makedirs(newDir)
        exportTree(a.new, newDir)
    else:
        copyWorkingTree(newDir)
    addMissing(oldDir, newDir)

    print('latexdiff ...')
    r = subprocess.run(['latexdiff', '--flatten', '--type=UNDERLINE', '--math-markup=coarse',
                        '--encoding=utf8', os.path.join(oldDir, 'main.tex'), os.path.join(newDir, 'main.tex')],
                       cwd = newDir, capture_output = True)
    if r.returncode:
        sys.exit('latexdiff failed:\n' + r.stderr.decode(errors = 'replace')[-2000:])
    with open(os.path.join(newDir, 'diff.tex'), 'wb') as f:
        f.write(r.stdout)

    os.makedirs(OUT, exist_ok = True)
    results = []
    print('compiling the diff ...')
    target = os.path.join(OUT, f'diff_{oldTag}_to_{newTag}.pdf')
    shutil.copy2(compile(newDir, 'diff.tex'), target)
    results.append(target)
    if not a.no_old_pdf:
        print('compiling the old version ...')
        target = os.path.join(OUT, f'old_{oldTag}.pdf')
        shutil.copy2(compile(oldDir, 'main.tex'), target)
        results.append(target)
    print('\n'.join(['written:'] + results))


if __name__ == '__main__':
    main()
