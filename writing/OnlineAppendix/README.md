# The online appendix

A Quarto book of short pages, one per subsection, that extends the paper's sections 5–7: four parts (A Argentina,
B the rich economies with the design given, C the endogenous design, D data and computation), each a landing page
and its subsection pages. Static figures and tables come from the paper's pipeline; the interactive figures are
Observable JS cells that draw, in the reader's browser, from csv files the build writes from the same results.
Nothing is solved on the site and no number is typed in its prose. The design and its decisions (2026-10-09):
`notes/plan_onlineAppendix.md` §2. The previous site (one page per chapter, a print edition) is in git history
before branch `oa-revision`.

## Build

```
.venv\Scripts\python.exe python\paper\build.py --only <outputs>   (the exhibits and datasets, if results/ moved)
.venv\Scripts\python.exe python\paper\build.py --site           (_generated/, _variables.yml, writing/Paper/onlineAppendix.tex)
quarto render writing\OnlineAppendix                             (_book/, about a minute)
```

Preview: `quarto preview writing\OnlineAppendix`, or serve `_book/` with a static server that does not hold the folder
open (`python -m http.server --directory <path to _book>`: one started inside `_book` stops the next render from
replacing it). Reload with the cache bypassed (Ctrl+F5) after a render. A tab in a hidden or locked window does not
run the interactive cells; check them in a visible window or in headless Chrome (`chrome --headless=new
--virtual-time-budget=20000 --screenshot=<png> <url>`).

## Files

| | |
|---|---|
| `_quarto.yml` | the book: parts and pages, theme; the resources the pages fetch (`assets/oa.js`, `_generated/**`) |
| `index.qmd` | the front page: the map of A–D and how to read the figures |
| `argentina.qmd`, `oecd.qmd`, `esc.qmd`, `checks.qmd` | the four landing pages (A–D) |
| `arg-*.qmd`, `oecd-*.qmd`, `esc-*.qmd`, `data.qmd`, `numerical.qmd`, `replication.qmd` | the pages: heading `# B4. Title {#key}`, prose, an include per exhibit, the OJS cells of the interactive figures |
| `assets/oa.js` | the interactive figures (the counterfactual chart and the path chart), the controls and the view in the address; Observable Plot 0.6.16, d3 7.9.0 and Inputs 0.12.0 pinned from jsDelivr |
| `assets/theme.scss`, `assets/oa.css` | the look: serif prose, sans interface, booktabs tables, the exhibit blocks |
| `assets/header.tex` | kept for the PDF edition (not built yet) |
| `_generated/`, `_variables.yml`, `_book/`, `.quarto/` | written by the build and gitignored |

## Rules

- Each exhibit is an include of its generated block: `_generated/exhibits/<id>.qmd` (a static figure or table), or
  `<id>-head.qmd` and `<id>-foot.qmd` around an interactive figure's OJS cells. `<id>` is a key of `EXHIBITS` in
  `python/paper/onlineAppendix.py`, which names the output shown and, for an interactive figure, the dataset
  (`python/paper/siteData.py`, a `data` output of `build.py`). Exhibits are numbered per page in the order the page
  includes them (Figure B2.1); an exhibit the paper inputs also carries its number there (from `main.aux`).
- The headings are the source of the paper's `\oa{key}` macros: `build.py --site` rewrites
  `writing/Paper/onlineAppendix.tex` from them, with every key of the site before 2026-10-09 defined as an alias of
  its new page (`OLDKEYS`), and `writing/checkPaper.py` fails on a key the paper uses that is not defined. Renaming a
  heading's key breaks the paper's references to it unless the old key joins `OLDKEYS`.
- No number is typed in the prose. The paper's and the site's exhibit, section and appendix numbers come from
  `{{< var p.<label> >}}` and `{{< var x.<id> >}}` (`_variables.yml`, the label's `:` written `_`). The prose says
  what an exhibit shows and how to read it; every sign and ranking it states is checked against the dataset.
- A counterfactual chart stacks what it compares (U.S. over UK, one cost over the other) on one x axis, drawn once
  under the last. Every chart draws at the width of its own box (`fitted` in `oa.js`): OJS's `width` is `main`'s,
  which spans the page once the page holds a `.column-page` block. Only C1's and C4's path figures are page-wide.
- An interactive figure opens at the paper's reading (ρ = 1, common X, the paper's cost, the U.S.), and its
  controls keep their state in the address (`#outcome=tau&...`), each under a key unique on its page.
- `python/paper/test_onlineAppendix.py` checks the pages, keys and registry, converts every table, and ties each
  dataset to the paper's own figure (5.2, 6.1, 7.1, G.1) through that figure's marks.
- Published at `https://championape.github.io/SSDclaude` (the previous site until the next publish): GitHub Pages
  serves the `gh-pages` branch, which `quarto publish gh-pages --no-prompt --no-browser` (from this folder, after
  `build.py --site`) renders and pushes. Publish on RKB's go. Plot, d3, Inputs and MathJax load from their CDNs.
