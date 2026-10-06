# The online appendix

A Quarto book that holds every table and figure of the paper's pipeline (81 exhibits), the paper's own
marked as such, beside the tables that print their numbers: hover a mark for its value, click it for its
table and row, switch the calibration variant, host or ρ, mark the cells two variants differ in. The same
pages render as a PDF print edition (`_book/OnlineAppendix.pdf`), which holds every exhibit the paper does not,
numbered Table/Figure OA.k as on the site. Design and decisions: `notes/paper_onlineAppendix.md`.

## Build

```
.venv\Scripts\python.exe python\paper\build.py           (the exhibits, if results/ moved)
.venv\Scripts\python.exe python\paper\build.py --site    (_generated/ and writing/Paper/onlineAppendix.tex)
quarto render writing\OnlineAppendix                      (_book/: the site and the PDF, about 45 s)
```

Preview: `quarto preview writing\OnlineAppendix`, or serve `_book/` with any static server. The paper's table
and equation numbers come from `writing/Paper/main.aux` when it is newer than every `.tex` of the paper, and are
counted from the source otherwise (equations then named by their section); compile the paper first for exact
numbers.

## Files

| | |
|---|---|
| `_quarto.yml` | the book: chapters, theme, the PDF engine (`pdflatex`, no automatic LaTeX installs) |
| `index.qmd`, `data.qmd`, `argentina.qmd`, `oecd.qmd`, `esc.qmd`, `numerical.qmd`, `replication.qmd` | the chapters: headings `OA.n.m Title {#anchor .unnumbered}` and short prose; the exhibits come in through `{{< include _generated/... >}}` |
| `assets/` | `exhibits.js` (controls, tooltips, linking, diff, URL state; vendored, no framework), `exhibits.css`, `theme.scss`, `header.tex` (the print edition's table packages), `scripts.html` |
| `_generated/`, `_book/`, `.quarto/` | written by the build and gitignored |

## Rules

- The headings are the source of the paper's `\oa{key}` macros: `build.py --site` rewrites
  `writing/Paper/onlineAppendix.tex` from them, and `writing/checkPaper.py` fails on a key the paper uses that
  no heading defines. Renumbering a section therefore renumbers the paper's references; renaming an anchor
  breaks them.
- No number is typed in the prose: every number is in an exhibit built from `results/`. The prose says what an
  exhibit is and how to read it; mechanisms stay in the paper.
- Which group shows which exhibit is the registry in `python/paper/onlineAppendix.py`; an exhibit the paper
  inputs is detected from the paper's tex, never declared.
- Publishing is RKB's call: the site is meant for `https://championape.github.io/SSDclaude`
  (`quarto publish gh-pages`; GitHub Pages is not enabled yet). MathJax loads from its CDN, so an offline
  archive would need it vendored.
