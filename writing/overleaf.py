r""" Move tex sources between this folder and Overleaf by zip -- no git sync, no API.

Two projects are known:

    note    the technical note: writing/main.tex and the three model folders it \subimports
    paper   the paper draft:    writing/Paper/

Export -- build a zip Overleaf can open (files at the zip root, main.tex among them):

    .venv\Scripts\python.exe writing\overleaf.py export paper
    .venv\Scripts\python.exe writing\overleaf.py export note  [--out some.zip]

    Writes writing/exports/<project>_<timestamp>.zip (gitignored). Before zipping, every \input,
    \include, \subimport, \includegraphics and \addbibresource in the sources is resolved against the
    files that will be in the zip, and the export REFUSES if a target is missing or matches only
    case-insensitively: Overleaf runs on Linux, so `\input{Packages}` does not find `packages.tex` there
    even though it does here. Compile artefacts (.aux, .bbl, .synctex.gz, the root main.pdf, ...) are
    never included.

Import -- bring Overleaf's "Download Source" zip back:

    .venv\Scripts\python.exe writing\overleaf.py import paper Downloads\project.zip --dry-run
    .venv\Scripts\python.exe writing\overleaf.py import paper Downloads\project.zip

    Overwrites local files whose content differs, adds files that are new, and NEVER deletes: a file
    present here but absent from the zip is only reported. Two protections, both on by default:
      * only text sources are written (.tex .bib .sty .cls .bst .txt .md); figures and other binaries
        are reported and left alone, so an older zip cannot roll back figures the pipeline has since
        rebuilt. --all writes everything.
      * a local file carrying the pipeline's `%% GENERATED` banner is never overwritten. Those tables are
        owned by python/paper/build.py; an online edit to one is reported so the change can be made at
        its source (python/paper/config.py or the builder) and rebuilt.
    --dry-run prints the plan and writes nothing. Do a dry run first.

Git sync -- the same two directions against ONE Overleaf project, through its git remote (Overleaf's
"Git" entry in the project menu; token from Account settings > Git integration, cached by the
credential manager after the first push):

    .venv\Scripts\python.exe writing\overleaf.py pull paper --url https://git.overleaf.com/<id> --dry-run
    .venv\Scripts\python.exe writing\overleaf.py push paper [--force]
    .venv\Scripts\python.exe writing\overleaf.py pull paper [--dry-run] [--all]

    A clone of the project lives in writing/exports/git-<project>/ (gitignored) and the URL is remembered
    beside it after the first use. `push` fast-forwards the clone, copies the export's file set over it --
    the same files, the same reference check -- DELETES clone files that no longer exist here, commits and
    pushes. A file that was edited online since the last push and differs from the local copy is a
    conflict: push refuses and says `pull` first (--force overwrites). On the FIRST push nothing is known
    about the online history, so every online text source that differs is treated that way: review with
    `pull --dry-run`, then `push --force` once to make Overleaf match this folder. `pull` fast-forwards
    the clone and applies the import rules above to it. Neither direction touches this repository's git
    history; commit here as usual. Run the first command from your own terminal so the credential manager
    can ask for the token.
"""
import os, re, sys, io, zipfile, argparse, datetime, json, hashlib, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
EXPORTS = os.path.join(HERE, 'exports')

# root: project root, relative to writing/. include: paths relative to root that go in the zip (a
# directory means its whole tree). main: the file Overleaf opens.
PROJECTS = {
    'note':  {'root': '.',     'main': 'main.tex',
              'include': ['main.tex', 'packages.tex', 'References.bib',
                          'informalAnalytical', 'informalSavings', 'US']},
    # The paper's Overleaf project is https://da.overleaf.com/project/6a86b4569416ca8062f0b899; its git
    # URL (Menu > Git in that project) is remembered under exports/ after the first push or pull.
    'paper': {'root': 'Paper', 'main': 'main.tex', 'include': ['.']},
}

ARTEFACT_EXT = {'.aux', '.log', '.bbl', '.blg', '.bcf', '.out', '.toc', '.lof', '.lot', '.fls',
                '.fdb_latexmk', '.synctex', '.gz', '.run.xml', '.xml', '.nav', '.snm', '.vrb',
                '.spl', '.idx', '.ilg', '.ind', '.dvi', '.ps'}
TEXT_EXT = {'.tex', '.bib', '.sty', '.cls', '.bst', '.txt', '.md'}
SKIP_DIRS = {'exports', '__pycache__', '.git'}
GENERATED = b'%% GENERATED'

REF_RE = re.compile(r'\\(input|include|subimport|import|includegraphics|addbibresource|bibliography)'
                    r'\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}(?:\s*\{([^}]*)\})?')
REF_EXT = {'input': ['.tex'], 'include': ['.tex'], 'subimport': ['.tex'], 'import': ['.tex'],
           'addbibresource': ['.bib'], 'bibliography': ['.bib'],
           'includegraphics': ['.pdf', '.png', '.jpg', '.jpeg', '.eps']}


def projectRoot(name):
    return os.path.normpath(os.path.join(HERE, PROJECTS[name]['root']))


def isArtefact(rel):
    base = os.path.basename(rel)
    ext = os.path.splitext(base)[1].lower()
    return ext in ARTEFACT_EXT or base.endswith('.synctex.gz') or base.endswith('.run.xml')


def projectFiles(name):
    """ {zip-relative path (posix): absolute path} for everything the export carries. """
    root, spec = projectRoot(name), PROJECTS[name]
    out = {}
    for inc in spec['include']:
        top = os.path.normpath(os.path.join(root, inc))
        if os.path.isfile(top):
            out[os.path.relpath(top, root).replace(os.sep, '/')] = top
            continue
        for d, dirs, files in os.walk(top):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS
                       and not (name == 'note' and os.path.join(d, x) == os.path.join(root, 'Paper'))]
            for f in files:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, root).replace(os.sep, '/')
                if isArtefact(rel) or rel == os.path.splitext(spec['main'])[0] + '.pdf':
                    continue
                if f == os.path.basename(__file__):
                    continue
                out[rel] = p
    return out


def stripComments(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit = 1)[0] for line in text.split('\n'))


def checkReferences(name, files):
    """ Resolve every file reference in the tex sources against `files` (the zip's contents), the way a
    case-sensitive filesystem would. Returns a list of problem strings. """
    exact = set(files)
    lower = {}
    for k in files:
        lower.setdefault(k.lower(), []).append(k)
    problems = []
    for rel, path in files.items():
        if not rel.endswith('.tex'):
            continue
        text = stripComments(io.open(path, encoding = 'utf-8', errors = 'replace').read())
        here = os.path.dirname(rel)
        for cmd, a, b in REF_RE.findall(text):
            if cmd in ('subimport', 'import'):
                target = a.strip() + b.strip()
            else:
                target = a.strip()
            if not target or target.startswith('#'):
                continue
            bases = {os.path.normpath(os.path.join(here, target)).replace(os.sep, '/'),
                     os.path.normpath(target).replace(os.sep, '/')}
            candidates = [c + e for c in bases for e in [''] + REF_EXT[cmd]]
            if any(c in exact for c in candidates):
                continue
            near = [lower[c.lower()][0] for c in candidates if c.lower() in lower]
            if near:
                problems.append('{}: \\{}{{{}}} matches only case-insensitively -- the file is {!r}. '
                                'Overleaf will not find it.'.format(rel, cmd, target, near[0]))
            else:
                problems.append('{}: \\{}{{{}}} -- no such file in the export.'.format(rel, cmd, target))
    return problems


def export(name, out = None):
    files = projectFiles(name)
    main = PROJECTS[name]['main']
    if main not in files:
        raise SystemExit('{} has no {} at its root'.format(name, main))
    problems = checkReferences(name, files)
    if problems:
        print('Export refused -- {} reference problem(s):'.format(len(problems)))
        for p in problems:
            print('  ' + p)
        raise SystemExit(1)
    os.makedirs(EXPORTS, exist_ok = True)
    out = out or os.path.join(EXPORTS, '{}_{}.zip'.format(
        name, datetime.datetime.now().strftime('%Y%m%d-%H%M')))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(files):
            z.write(files[rel], rel)
    print('{} files -> {}'.format(len(files), os.path.relpath(out, REPO)))
    print('Overleaf: New Project > Upload Project, and pick this zip. {} is the root document.'.format(main))
    return out


def zipPrefix(z, main):
    """ Overleaf zips put the project at the root; some tools wrap it in one folder. Find main.tex. """
    names = [n for n in z.namelist() if not n.endswith('/')]
    hits = [n for n in names if n.endswith('/' + main) or n == main]
    if not hits:
        raise SystemExit('no {} anywhere in the zip -- is this the right project?'.format(main))
    top = min(hits, key = len)
    return top[:-len(main)]


def zipContents(zpath, main):
    """ {project-relative path: bytes} of a Download-Source zip, whatever folder it is wrapped in. """
    out = {}
    with zipfile.ZipFile(zpath) as z:
        prefix = zipPrefix(z, main)
        for n in z.namelist():
            if n.startswith(prefix) and not n.endswith('/') and '__MACOSX' not in n:
                out[n[len(prefix):]] = z.read(n)
    return out


def importZip(name, zpath, dryRun = False, allFiles = False):
    applyImport(name, zipContents(zpath, PROJECTS[name]['main']), dryRun = dryRun, allFiles = allFiles)


def applyImport(name, incoming, dryRun = False, allFiles = False):
    """ Bring `incoming` ({project-relative path: bytes}, from a zip or from the git clone) into the local
    project under the import rules of the module docstring: overwrite differing text sources, add new
    ones, never delete, never touch a `%% GENERATED` file, leave binaries alone unless allFiles. """
    root, main = projectRoot(name), PROJECTS[name]['main']
    plan = {'update': [], 'new': [], 'same': [], 'protected': [], 'binary': []}
    seen = set()
    for rel, data in incoming.items():
        if isArtefact(rel) or rel == os.path.splitext(main)[0] + '.pdf':
            continue
        seen.add(rel)
        target = os.path.join(root, rel.replace('/', os.sep))
        ext = os.path.splitext(rel)[1].lower()
        if ext not in TEXT_EXT and not allFiles:
            if not os.path.exists(target) or open(target, 'rb').read() != data:
                plan['binary'].append(rel)
            continue
        if not os.path.exists(target):
            plan['new'].append((rel, target, data))
            continue
        local = open(target, 'rb').read()
        if sameContent(local, data, rel):
            plan['same'].append(rel)
        elif local[:200].find(GENERATED) >= 0:
            plan['protected'].append(rel)
        else:
            plan['update'].append((rel, target, matchEndings(data, local)))
    onlyLocal = [rel for rel in projectFiles(name)
                 if rel not in seen and os.path.splitext(rel)[1].lower() in TEXT_EXT]

    verb = 'would write' if dryRun else 'writing'
    for rel, target, data in plan['update']:
        print('{:<12} {}'.format(verb, rel))
    for rel, target, data in plan['new']:
        print('{:<12} {}  (new)'.format(verb, rel))
    for rel in plan['protected']:
        print('{:<12} {}  -- carries the pipeline banner; edit its source and rebuild instead'
              .format('PROTECTED', rel))
    for rel in plan['binary']:
        print('{:<12} {}  -- differs, not written (pass --all to include binaries)'.format('binary', rel))
    for rel in onlyLocal:
        print('{:<12} {}  -- here but not in the zip; left in place'.format('only local', rel))
    if not dryRun:
        for rel, target, data in plan['update'] + plan['new']:
            os.makedirs(os.path.dirname(target), exist_ok = True)
            with open(target, 'wb') as f:
                f.write(data)
    print('{} updated, {} new, {} unchanged, {} protected, {} binary skipped, {} only local{}'.format(
        len(plan['update']), len(plan['new']), len(plan['same']), len(plan['protected']),
        len(plan['binary']), len(onlyLocal), '  (dry run, nothing written)' if dryRun else ''))


# ---------------------------------------------------------------------------------------------------
# Git sync. The clone under exports/ is the only thing that talks to Overleaf; this repository's own
# history is never involved (no subtree, no second remote here), which is what keeps a push from
# Overleaf's point of view a plain fast-forward and keeps a co-author's edit from landing in this
# repository unreviewed -- `pull` goes through the import rules like a zip does.
# ---------------------------------------------------------------------------------------------------
def cloneDir(name):
    return os.path.join(EXPORTS, 'git-' + name)


def urlFile(name):
    return os.path.join(EXPORTS, 'git-' + name + '.url')


def pushedFile(name):
    return os.path.join(EXPORTS, 'git-' + name + '.pushed.json')


def git(clone, *args, check = True, capture = False):
    r = subprocess.run(['git', '-C', clone] + list(args), text = True,
                       capture_output = capture, encoding = 'utf-8')
    if check and r.returncode:
        raise SystemExit('git {} failed ({})'.format(' '.join(args), r.returncode)
                         + ('\n' + (r.stderr or '') if capture else ''))
    return r


def ensureClone(name, url = None):
    """ Clone on first use, fast-forward afterwards. Returns the clone directory. """
    clone = cloneDir(name)
    if url:
        os.makedirs(EXPORTS, exist_ok = True)
        with open(urlFile(name), 'w', encoding = 'utf-8') as f:
            f.write(url.strip() + '\n')
    elif os.path.exists(urlFile(name)):
        url = open(urlFile(name), encoding = 'utf-8').read().strip()
    else:
        raise SystemExit('no remote known for {}: pass --url <the project\'s git URL> once'.format(name))
    if not os.path.isdir(os.path.join(clone, '.git')):
        os.makedirs(EXPORTS, exist_ok = True)
        # Line endings pass through untouched: with autocrlf the checkout would turn every LF file
        # into CRLF and a byte comparison would report the whole project as changed on every pull.
        r = subprocess.run(['git', 'clone', '-c', 'core.autocrlf=false', url, clone], text = True)
        if r.returncode:
            raise SystemExit('git clone failed -- is Git enabled on the project, and is the token cached?')
        git(clone, 'config', 'core.autocrlf', 'false')
    else:
        git(clone, 'pull', '--ff-only', '--quiet')
    return clone


def isText(rel):
    return os.path.splitext(rel)[1].lower() in TEXT_EXT


def norm(data, rel):
    """ Bytes to compare: text sources with line endings normalised, everything else as is. Overleaf's
    editor saves LF and this repository holds both, so an ending difference is not an edit. """
    return data.replace(b'\r\n', b'\n') if isText(rel) else data


def sameContent(a, b, rel):
    return norm(a, rel) == norm(b, rel)


def matchEndings(data, like):
    """ Give `data` the line-ending style of `like` (the local file being overwritten). """
    if b'\r\n' in like and b'\r\n' not in data:
        return data.replace(b'\n', b'\r\n')
    if b'\r\n' not in like and b'\r\n' in data:
        return data.replace(b'\r\n', b'\n')
    return data


def cloneFiles(clone):
    """ {project-relative path (posix): absolute path} of the clone's working tree, artefacts excluded. """
    out = {}
    for d, dirs, files in os.walk(clone):
        dirs[:] = [x for x in dirs if x != '.git']
        for f in files:
            p = os.path.join(d, f)
            rel = os.path.relpath(p, clone).replace(os.sep, '/')
            if not isArtefact(rel):
                out[rel] = p
    return out


def sha(path, rel = None):
    """ Content hash for the push bookkeeping; line-ending-blind for text sources (see norm). """
    data = open(path, 'rb').read()
    return hashlib.sha1(norm(data, rel if rel is not None else path)).hexdigest()


def push(name, url = None, force = False, message = None):
    files = projectFiles(name)
    problems = checkReferences(name, files)
    if problems:
        print('Push refused -- {} reference problem(s):'.format(len(problems)))
        for p in problems:
            print('  ' + p)
        raise SystemExit(1)
    clone = ensureClone(name, url)
    online = cloneFiles(clone)
    first = not os.path.exists(pushedFile(name))
    pushed = {} if first else json.load(open(pushedFile(name)))
    # A file edited online since the last push, and not identical to what is here now, is a conflict.
    # On the FIRST push nothing is known about the online history, so every online text source that
    # differs from (or is absent from) the export counts: review it with `pull --dry-run`, then --force.
    differs = lambda rel, p: rel not in files or sha(files[rel], rel) != sha(p, rel)
    conflicts = [rel for rel, p in online.items()
                 if differs(rel, p) and ((rel in pushed and sha(p, rel) != pushed[rel]) or
                                         (first and isText(rel)))]
    if conflicts and not force:
        print('Push refused -- {} and different here:'.format(
            'first push, and Overleaf has text sources that are not in the export'
            if first else 'edited on Overleaf since the last push'))
        for rel in conflicts:
            print('  ' + rel)
        print('Run `pull {} --dry-run` to review (it applies the import rules), then `push {} --force` '
              'to make Overleaf match this folder.'.format(name, name))
        raise SystemExit(1)
    changed, removed = [], []
    for rel, src in sorted(files.items()):
        dst = os.path.join(clone, rel.replace('/', os.sep))
        if not os.path.exists(dst) or sha(dst, rel) != sha(src, rel):
            os.makedirs(os.path.dirname(dst), exist_ok = True)
            shutil.copyfile(src, dst)
            changed.append(rel)
    for rel, p in online.items():
        if rel not in files:
            os.remove(p)
            removed.append(rel)
    for rel in changed:
        print('{:<12} {}'.format('update', rel))
    for rel in removed:
        print('{:<12} {}'.format('delete', rel))
    if not changed and not removed:
        print('nothing to push: Overleaf already matches the {} export'.format(name))
        return
    git(clone, 'add', '-A')
    head = subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'], text = True,
                          capture_output = True).stdout.strip()
    git(clone, 'commit', '--quiet', '-m', message or 'sync from SSDclaude {} {}'.format(
        head, datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
    git(clone, 'push', '--quiet')
    with open(pushedFile(name), 'w', encoding = 'utf-8') as f:
        json.dump({rel: sha(p, rel) for rel, p in cloneFiles(clone).items()}, f, indent = 1)
    print('{} updated, {} deleted -> pushed to Overleaf'.format(len(changed), len(removed)))


def pull(name, url = None, dryRun = False, allFiles = False):
    clone = ensureClone(name, url)
    incoming = {rel: open(p, 'rb').read() for rel, p in cloneFiles(clone).items()}
    applyImport(name, incoming, dryRun = dryRun, allFiles = allFiles)


def main():
    p = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest = 'cmd', required = True)
    e = sub.add_parser('export'); e.add_argument('project', choices = PROJECTS)
    e.add_argument('--out', help = 'zip path (default writing/exports/<project>_<timestamp>.zip)')
    i = sub.add_parser('import'); i.add_argument('project', choices = PROJECTS)
    i.add_argument('zip'); i.add_argument('--dry-run', action = 'store_true')
    i.add_argument('--all', action = 'store_true', help = 'also write non-text files (figures etc.)')
    ps = sub.add_parser('push'); ps.add_argument('project', choices = PROJECTS)
    ps.add_argument('--url', help = "the Overleaf project's git URL; remembered after the first push")
    ps.add_argument('--force', action = 'store_true', help = 'overwrite files edited online since the last push')
    ps.add_argument('-m', '--message', help = 'commit message on the Overleaf side')
    pl = sub.add_parser('pull'); pl.add_argument('project', choices = PROJECTS)
    pl.add_argument('--url', help = "the Overleaf project's git URL; remembered after the first use")
    pl.add_argument('--dry-run', action = 'store_true')
    pl.add_argument('--all', action = 'store_true', help = 'also write non-text files (figures etc.)')
    a = p.parse_args()
    if a.cmd == 'export':
        export(a.project, a.out)
    elif a.cmd == 'import':
        importZip(a.project, a.zip, dryRun = a.dry_run, allFiles = a.all)
    elif a.cmd == 'push':
        push(a.project, url = a.url, force = a.force, message = a.message)
    else:
        pull(a.project, url = a.url, dryRun = a.dry_run, allFiles = a.all)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding = 'utf-8')
    main()
