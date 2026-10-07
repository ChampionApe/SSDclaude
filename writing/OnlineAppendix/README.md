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

Preview: `quarto preview writing\OnlineAppendix`, or serve `_book/` with any static server. After a render, reload
the page with the cache bypassed (Ctrl+F5): the browser keeps `assets/exhibits.js` and `.css`, which carry no
version, and a plain reload can show the previous build's layout or behaviour. The paper's table
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
- A sentence that only makes sense on the site (point at, click, the browser's address, the sidebar's download)
  is wrapped in `[...]{.content-visible when-format="html"}` (a `:::` div for a paragraph); the print edition has
  its own reading guide in `index.qmd` under `when-format="pdf"`.
- An exhibit's own paragraph is the registry's `text` (the notes' LaTeX vocabulary, no typed number): on the site it
  sits above the exhibit (above the tabs when the group has tables) and follows the tab and the calibration switch;
  in the print edition it precedes the exhibit, and the paper's own exhibits keep it
  after the stand-in line. `textAlt` replaces it for the vector-$X_i$ twin (the Argentine twins say "identical").
  Since 2026-10-06 OA.2.2 and OA.2.3 carry texts; the other groups are to be written.
- An exhibit the paper no longer inputs needs a `caption` and a `note` in the registry (its tex no longer supplies
  them); the site adds the "Note:" label to a registry note, the print edition adds its own. A note that points at
  the section it is shown in ("Online Appendix OA.3.4" inside OA.3.4) renders as "this section" in both editions;
  the paper keeps the pointer.
- Published at `https://championape.github.io/SSDclaude` since 2026-10-07: GitHub Pages serves the root of the
  `gh-pages` branch, which `quarto publish gh-pages --no-prompt --no-browser` (run from this folder, after
  `build.py --site`) renders and pushes; the branch holds the rendered site only and is never edited by hand.
  Publish on RKB's go, after the paper's compile so the stand-in lines carry the paper's current numbers. MathJax
  loads from its CDN, so an offline archive would need it vendored.
