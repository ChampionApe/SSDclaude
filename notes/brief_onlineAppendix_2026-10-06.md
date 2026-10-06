# Brief: the appendix split and the online appendix (2026-10-06)

The shared contract of four parallel work packages. The design and its reasons are in
`notes/paper_onlineAppendix.md` (read §3–§5); this file is what the packages build against. RKB's decisions
of 2026-10-06: the online appendix is a Quarto site on GitHub Pages with a PDF print edition from the same
source; build all of it, no prototype gate; target journals REStud, JPE or AEJ: Economic Policy; the paper's
appendix keeps the split of option K **and some UK results** (below); B.2–B.3 stay in the paper.

**RKB is editing `writing/Paper/Sections/*.tex` on Overleaf while this runs. Nobody touches those files.**
Every label the sections cite stays defined (a kept section or a short stub), so no main-text edit is needed.

## 1. Ownership (agents work in the main checkout, do not commit, touch only their files)

| Package | Agent | Files |
|---|---|---|
| A exhibits in the existing pipeline | paper-compute | `python/paper/{figures,figuresUS,oecdFigure1,tables,tablesUS,build,config}.py`; outputs under `results/paper/` and their copies in `writing/Paper/{Tables,Figs}` through `build.py` |
| B online-only exhibits | paper-compute | NEW `python/paper/tablesOA.py`, `python/paper/figuresOA.py`; an appended block at the END of `python/paper/datasets.py` (A does not edit `datasets.py`) |
| S the site | fork of the main session | NEW `python/paper/onlineAppendix.py`, `python/paper/texTable.py`, `python/paper/test_onlineAppendix.py`; NEW `writing/OnlineAppendix/**`; `writing/checkPaper.py`; the generated `writing/Paper/onlineAppendix.tex` |
| P the paper's appendix | paper-writer | `writing/Paper/Appendix/*.tex`, NEW `writing/Paper/Appendix/Robustness.tex`, `writing/Paper/main.tex` |

The main session owns everything else (`README.md`s, logs, `REPLICATION.md`, `pyenv.md`, `.gitignore`, notes)
and registers B's builders in `build.py` at integration. Interpreter: `.venv\Scripts\python.exe` with
`PYTHONUTF8=1` (or `-X utf8`).

## 2. Contracts

**2.1 Figures.** `figures._save(fig, name, marks = None)` (done) writes `name`.pdf, .png, .svg and, with
`marks`, `name`.marks.json into `results/paper/Figs/`, and raises if a mark id is not exactly once in the svg.
Tag an artist with `artist.set_gid(figures.markId(name, part, ...))`; parts are ASCII (`tau`, not `τ`).
Tag every data mark a reader would ask about (a bar, a dot, a point on a line), not axes, ticks or legends.
A scatter collection carries one gid for all its points: draw taggable points as individual artists. One
mark per number. A mark is a dict:

```
{"id": "US_overview--theta0--rho2.0--tau",   # = the artist's gid
 "label": "θ = 0",                           # the row the reader sees (unicode is fine here)
 "series": "ρ = 2.0",                        # what distinguishes marks within a row, or ""
 "panel": "Equilibrium tax rate",            # the panel title, or ""
 "value": 0.8293,                            # float, in the panel's own units
 "text": "+0.8 p.p.",                        # as the paper would print it (style guide §3)
 "table": "US_CRRA_PensChars",               # build.OUTPUTS name of the table that prints it, or null
 "row": "theta0@2.0"}                        # that table's row key (2.2), or null
```

A `_vectorX` figure links to `_vectorX` tables. The PDF must look exactly as before: tags change no pixel.

**2.2 Table rows.** Every body row of a generated table ends with ` % row: <key>`, the **last** thing on its
line (several builders append `[1.25ex]`, `\hline` or `[.5em]\hline\\[-.75em]` to a row after building it;
the comment goes after all of that, or the spacing ends up inside the comment). Header rows, `\multicolumn`
block titles and rules carry no key. Keys are ASCII, unique within a table, `<block>[@<rho>][@<effect>]`:
blocks `baseline, theta0, theta1, mild, acute, income, leisure, voting, frall, france, pinned, chosen, pre`
(add others as the table needs, lowercase), ρ with one decimal (`1.0`, `1.3`), effect `full` or `ee`.
Examples: `US_PensChars` → `baseline`, `theta0@full`, `theta0@ee`; CRRA tables → `voting@2.0`; ESC tables →
`baseline@0.5`, `pinned@1.0`, `chosen@2.0`, `france@0.5`; parameter tables → the parameter (`gamma`,
`eta`, `X`, `mu`, `theta`, `omega`, `beta`, `nu`, `etaratio`); country rows → lowercase ISO3 (`aus`).
**Check (A and B):** deleting ` % row: ...` from every line of every pre-existing table reproduces the file
at `HEAD` byte for byte.

**2.3 Output names.** Existing outputs keep their names. New, all `results/paper/` only (not copied into
`writing/Paper`) unless marked *paper*:

| Name | Pkg | What |
|---|---|---|
| `RobustnessMap` (*paper*) | A | figure, §3 of this brief; `writing/Paper/Figs/RobustnessMap.pdf` |
| `ArgentinaReformByRho` + `_vectorX` | A | `Argentina_funcOfRho` with all 16 ρ rows printed; rows `pre`, `rho@0.5` … `rho@2.0` |
| `OECD_Countries`, `OECD_Sources`, `OECD_Correlations` | B | figure 1's data: one row per country (`data/oecdFigure1.csv`, the columns `oecdFigure1.PLOT` draws, with years), the sources (`data/oecdFigure1_sources.csv`), the correlations (`results/paper/oecdCorrelations.csv`) |
| `ArgentinaReformPath` + `_vectorX` | B | the reform's path at ρ = 1 by period: tax, savings over GDP, workweek, pre-reform against reform |
| `ARG_RhoGrid` (figure), `ARG_RhoGridTable` + `_vectorX` each | B | the Argentine calibration across the 16 ρ (`results/calibration/informalSavings_rhoGrid*`) |
| `OECD_RhoGrid` (figure), `OECD_RhoGridTable` + `_vectorX` each | B | the U.S., UK and France calibrations across the 16 ρ (`results/calibration/*_rhoGrid*`): β, ω, X, R, the savings rate |
| `ESC_Path` (figure), `ESC_PathTable` | B | the design and the tax along the baseline path 1960–2170, chosen against pinned (`results/esc/escPath.csv`, spec `size`; `escPathCRRA.csv` where it holds the same), with ξ = 0.2 and 0.4 (`escXiRobustness.csv`) |
| `ESC_Xi` | B | λ, the design in 2050/2080/2110, acute ageing pinned and chosen, at ξ = 0.2, 0.3, 0.4 |
| `ESC_Timing` | B | the timing checks (`escPermanent*.csv`, `escSequentialCRRA.csv`); read their meaning in `writing/US/num_esc.tex` before labelling a column |
| `NUM_Stationary` | B | stationary against date-specific policies (`results/numerical/*.csv`), the gap in p.p. by date and ρ |
| `NUM_Selection` | B | per results csv the paper's outputs read: rows, max `nEqMax`, max `nCandMax`, sum of `nFallback` |

A table builder returns the complete tex body with the `tables.BANNER` and `_xwrap`-style layout (booktabs,
threeparttable, a note); a figure builder calls `figures._save(..., marks)` and returns its paths. House style
from `figures.py`; units and precision from `notes/paper_styleGuide.md` §3. A variant twin comes from the same
builder with `commonX`, as every US builder does (`config.variantSuffix`).

**2.4 The online appendix's sections.** Book chapters and anchors, fixed (the paper's `\oa{key}` macros in
`writing/Paper/onlineAppendix.tex` use them; `\oahome` links the front page):

| File | Heading and `{#anchor}` | Exhibits (paper ones are shown too, marked as the paper's) |
|---|---|---|
| `index.qmd` | front page `#robustness` | `RobustnessMap` |
| `data.qmd` | OA.1 The cross-section of figure 1 `#data`; OA.1.1 `#data-countries`; OA.1.2 `#data-correlations` | `OECDdata`, `OECD_Countries`, `OECD_Sources`; `OECD_Correlations` |
| `argentina.qmd` | OA.2 Argentina `#arg`; OA.2.1 calibration `#arg-calibration`; OA.2.2 the reform `#arg-reform`; OA.2.3 the reform across the IES `#arg-rho`; OA.2.4 the equilibrium over designs `#arg-designs`; OA.2.5 the calibration across the IES `#arg-rhogrid` | `ArgentinaCalibration`±; `ArgentinaUniversal`±, `ArgentinaReformPath`±; `ARG_CRRA_LOG`±, `ArgentinaReformByRho`±; `ARG_LOG_FourInOne`±; `ARG_RhoGrid`±, `ARG_RhoGridTable`± |
| `oecd.qmd` | OA.3 The rich economies with the design given `#oecd`; OA.3.1 `#oecd-calibration`; OA.3.2 the vector-Xᵢ calibration `#oecd-vectorx`; OA.3.3 the calibration across the IES `#oecd-rhogrid`; OA.3.4 counterfactuals on the U.S. `#oecd-us`; OA.3.5 the UK as host `#oecd-uk` | `USUKFRCalibration`±, the five household tables±; (prose); `OECD_RhoGrid`±, `OECD_RhoGridTable`±; `US_overview`±, `US_PensChars`±, `US_Ageing`±, `US_OtherShocks`±, `US_CRRA_PensChars`±, `US_CRRA_Ageing`±, `US_CRRA_OtherShocks`±; `UKUS_French`±, `UK_OtherShocks`±, `UK_CRRA_OtherShocks`± |
| `esc.qmd` | OA.4 The endogenous pension design `#esc`; OA.4.1 `#esc-calibration`; OA.4.2 counterfactuals on the U.S. `#esc-us`; OA.4.3 the UK as host `#esc-uk`; OA.4.4 the baseline path `#esc-path`; OA.4.5 timing `#esc-timing`; OA.4.6 an alternative cost `#esc-scale` | `US_ESC_Calibration`, `US_ESC_Country`; `US_ESC_overview` + the four `US_ESC_*`; `UKUS_ESC_French` + the three `UK_ESC_*`; `ESC_Path`, `ESC_PathTable`, `ESC_Xi`; `ESC_Timing`; `US_ESC_ScaleWedge` |
| `numerical.qmd` | OA.5 Numerical checks `#num`; OA.5.1 `#num-stationary`; OA.5.2 `#num-selection` | `NUM_Stationary`; `NUM_Selection` |
| `replication.qmd` | OA.6 Replication `#rep` | the generated map |

(± = headline and `_vectorX` twin.)

## 3. The robustness map (A)

One figure, the paper's appendix H and the site's front page. Small multiples, one panel per headline result,
the change against the host's own baseline at the same ρ: with the design given, the tax rate under θ = 0
against θ = 1, acute ageing, France's income distribution, France's voting patterns (p.p.); with the design
chosen, the chosen design under acute ageing, France's income distribution, France's voting patterns (change
in θ). One marker per specification: ρ by colour (`figuresUS.RHOCOLOURS`), the calibration variant by marker
shape, the host as row groups; for the chosen design, rows for the cost specification (`size`, `scale`; U.S.
only), the UK host (`size`), and ξ = 0.2/0.4 at ρ = 1. Mark the paper's own reading (U.S., common X, ρ = 1,
cost `size`) so it stands out, and draw zero as the reference. Every value comes from the csvs the tables
read, through `datasets.py`; every marker is tagged and links to the table and row that print it. It must
read at `\linewidth` (5.91 in): size it near the measure, as the README's traps say.

## 4. The paper's appendix (P)

Exemplar of the voice: `Sections/EndogenousTheta.tex`. The order becomes A–C derivations, D–E calibration,
F the U.S., G the French characteristics on both hosts, H the robustness map.

- **A** l.181: drop the γ₀ half of "an increase (decrease) in θ (γ₀) increases s_t,0" (gate 2, G2.1), and
  write $s_{t,0}$. **B** l.32 "type type"; l.96 $\beta_{t,0}$ → $\beta$; l.138 and l.143 $\mu_0$ → $r_0$
  (the informal return factor of B.2; $\mu_0$ is a propensity to vote). **C** l.13 $\Gamma_{t,h}$ → $\Gamma_h$.
  Not yours: C1's point c (the propensities to vote in proposition 2), which is RKB's.
- **D**: the survey description to one paragraph; drop the promise of ξ between 0.20 and 0.40 and its
  footnote (no Argentine run backs it); the relative-hours sentence must not say `table:Arg:Calib` reports
  hours (it does not). D.5 becomes a stub `\subsection` keeping `\label{app:EPH:vectorX}` (section 5's
  footnote cites it): two or three sentences on what the alternative identifies, that the results are
  identical, and Online Appendix `\oa{arg-calibration}` for its calibration and `\oa{arg-rho}` for the reform
  at every ρ. The `\input` of `ArgentinaCalibration_vectorX` and the reference to `table:Argentina:funcOfRho`
  go (RKB dropped that table from section 5).
- **E**: France's LIS sample is the 2018 wave (section 6 says so). E.1–E.4 stay (E.4 carries the UK host
  that stays). E.5, the UK at U.S. percentiles, goes online: one sentence, where table
  `table:US_ESC:country`'s UKUS row is documented, `\oa{oecd-calibration}`.
- **F**: F.1 loses the sentence that repeats section 6's mechanism ("The reason for this is the one section
  ... gives ..."). F.2 becomes a stub keeping `\label{app:US:vectorX}` (sections 6 and 7 cite it): what the
  variant is, that only rows defined through η or X separately move, the income-distribution row being the
  one that does, and `\oa{oecd-vectorx}`; its 14 tables and figure go. F.3 keeps `US_ESC_Ageing` and its
  paragraph; the scale-wedge paragraph and table go, with one sentence pointing at `\oa{esc-scale}`.
- **G** (`\label{app:UKUS}`, `app:US:french`, `app:US:ukESC` all kept), the French characteristics on the U.S.
  and the UK. G.1 keeps `US_OtherShocks`, `US_CRRA_OtherShocks`, and of the UK `UK_OtherShocks` (section 6
  cites it) and figure `UKUS_French`; `UK_CRRA_OtherShocks` goes online (`\oa{oecd-uk}`); "1.6 p.p. at
  ρ = 0.5" reads 1.5 (14.43 − 12.88); the remaining tax gap is "France's demography" alone (France's θ = 1
  and ω = 1.42 < 1.45 both narrow it). G.2 keeps the three `US_ESC_*` French tables and figure
  `UKUS_ESC_French`; the three `UK_ESC_*` tables go online (`\oa{esc-uk}`). Every number left in G must be
  readable in the PDF (a kept table or figure); a number only an online table prints is cut or pointed online.
  Re-check the ρ = 2 workweek clause of G.2 against the tables. Figure notes that cite a table moving online
  cite `\oa{...}` instead.
- **H** (new, `Appendix/Robustness.tex`, `\label{app:robustness}`): a short opening (what the figure plots,
  how to read it, that the online appendix at `\oahome` is organised around it and links each marker to its
  table), then the figure environment, house layout (caption above, `\label{fig:robustness}`, threeparttable
  note), `\includegraphics[width=\linewidth]{Figs/RobustnessMap.pdf}` (built by A; the checker reports it
  missing until then).
- `main.tex`: `\input{onlineAppendix}` right after `\input{Packages.tex}`; `\input{Appendix/Robustness}` last.

## 5. The site (S)

- `python/paper/texTable.py`: generated LaTeX table → HTML, for the builders' own vocabulary (banner,
  threeparttable, `\caption`, `\label`, tabular/tabularx with any column spec incl. `|`, `!{...}`, `C{..}`,
  `\toprule/\midrule/\bottomrule/\hline/\cline`, row spacing `\\[..]`, `\multicolumn`, `\tnote`, tablenotes
  with `\item[]`/`\item[a]`, text macros `\textbf \textit \bm \%  -- \textquotesingle ~`, `$...$` kept for
  MathJax as pandoc's `<span class="math inline">\(...\)</span>`, commented-out rows dropped, `% row:` keys →
  `data-row`). `\ref`/`\eqref` resolve to an OA number or to the paper (its number from `writing/Paper/main.aux`
  when that file is newer than every `.tex` in `writing/Paper`, else a phrase that names the paper's section);
  never `??`. A test converts every table in `results/paper/Tables`.
- `python/paper/onlineAppendix.py` (`build.py --site` calls `onlineAppendix.build()`): reads only
  `results/paper/` and the repo, writes `writing/OnlineAppendix/_generated/` (one include per exhibit group:
  an HTML block with controls, the inline SVG with its marks, the tables, provenance; a LaTeX block for the
  print edition with the PDF figures and preprocessed tables, OA-numbered). An exhibit used by the paper
  (`build._usedIn()`) is shown as the paper's and left out of the print edition; an online one is numbered
  Table/Figure OA.k in the same order in both formats. Provenance: the inputs `build`'s tracing finds, the
  builder, the `--only` command, `git rev-parse --short HEAD` and whether `results/` or `python/paper` is
  dirty; the csvs copied for download. It also writes `writing/Paper/onlineAppendix.tex` from the chapters'
  headings (same format and keys as the hand-written first version) and `writing/checkPaper.py` checks every
  `\oa{}` key.
- `writing/OnlineAppendix/`: a Quarto book (HTML and one PDF, `OnlineAppendix.pdf`), chapters per 2.4 with
  `.unnumbered` headings carrying their OA numbers, short prose in the style guide's register and no
  hand-typed numbers; theme, `exhibits.js` (vendored, no framework: controls for variant/host/ρ/θ, tabs, hover
  tooltips on marks, click → table and row, a diff switch between twins, URL state; without JavaScript every
  page shows its default selection) and `exhibits.css`. `_generated/`, `_book/`, `.quarto/` are gitignored.
  Rendered locally only; publishing (`quarto publish gh-pages`) is RKB's call.

## 6. Rules for everyone

No hand-typed number anywhere: tables and figures from `results/` through `python/paper`, prose numbers
checked against the table beside them. Generated files are never hand-edited. `build.py` stays seconds and
imports no model code. Docstrings say what code does now (`CLAUDE.md`). Report in the agent type's format and
list every deviation from this brief.
