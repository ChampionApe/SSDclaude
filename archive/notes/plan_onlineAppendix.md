# Revision of online appendix

General:

* Keep sections short. Display subsections in separate pages.
* Use primarily Observable JS to interact. Simple exhibits (in javascript) to toggle between completely different figures/tables.
* Do not build the new online based on the existing structure or layout. 

## 1. Content

Open with a brief description of what the online appendix contains, mainly a map.

### A. Argentina

Short opening paragraph on what the section has.

#### A1. How pension designs shape the equilibria

The figure "The equilibrium in 2010 over pension designs (𝜖,𝜃), Argentina". Short paragraph explaining what the figure shows above the figure. Don't include common versus vector X calibration here.

#### A2. The intertemporal elasticity of substitution

Two small titles:

**Argentina calibration across the intertemporal elasticity**.
The figure "The Argentine calibration across the intertemporal elasticity". Short paragraph explaining what the figure shows above the figure. Don't include the table with numbers.

**Short- and long-run effects of the pension reform across the intertemporal elasticity**
I want to present the paper's figure "Short- and long-run effects of the pension reform as a function of 𝜌" next to a second figure: The second figure is an interactive figure with slider with ρ ∈ [0.5, 2] that shows the time paths for the same four variables in levels, one pre-reform and one post-reform curve. When we print the time paths, leave out the first and last few time periods. Short paragraph explaining what the figures show above the figures.

#### A3. Identification of X

Open with a paragraph explaining all that is identical across the two calibration strategies (common versus vector X). Emphasize that the figures below do not show the identical parts, but only highlights where things differ.

New table that compares table "Calibration, Argentina" with the two calibration variants (merge to one new table). Only keep the rows that differ. Add a short paragraph explaining the differences above the table.

New table that compares calibration parameters for the two calibration variants. Only keep the parameters that differ across variants, remember to compare common X with vector Xi. A short paragraph above that explains the differences, notably why the level of X changes across the two.

### B. Rich OECD countries with the design given

Short opening paragraph on what the section has.

#### B1. Calibration

**Calibration across the intertemporal elasticity**.
The figure "The calibrations of the U.S., the UK and France across the intertemporal elasticity". Short paragraph explaining what the figure shows above the figure. Don't include the table with numbers.

#### B2. Other countries

Two small titles:

**What shapes pensions, savings, and labor supply cross U.S. and UK.**
The figure "French characteristics in the U.S. and the UK", but slightly changed: Use the same categories as the figure from the paper (which is currently also printed in the online appendix, "The effect of various counterfactuals in the U.S."). One paragraph above explaining what the figure shows and the differences. Do not keep the table with numbers next to it.

**UK at U.S. income groups.**
First, present a (new) table comparing calibration parameters across countries. Start from the table " Calibration, the U.S., the UK and France" from the main figure, but add additional columns for UK at U.S. income groups and France at UK income groups as well. Add one paragraph above explaining the differences.

Second, add a (new) figure that shows how splitting up UK and France at different income groups (we have UK at its own and U.S. income groups, and France at UK and U.S. income groups). If we only have the solutions for ρ = 1, set up a new figure that shows the effect of the same shocks from figures above (pension design, ageing, income distr., voting, leisure) for UK at the two different income groups. Add a paragraph above explaning the results.

#### B3. Other parameters

Show the figure from B2. Other countries: **What shapes pensions, savings, and labor supply cross U.S. and UK.**, but only for the U.S., and instead add an interactive feature: If we have data for other ξ, please allow for a drop down manu where we can choose for what ξ value to plot it.

#### B4. Identification of X

Open with a paragraph explaining all that is identical across the two calibration strategies (common versus vector X). Emphasize that the figures below do not show the identical parts, but only highlights where things differ.

New table that compares table "Calibration, US" with the two calibration variants (merge to one new table). Only keep the rows that differ. Add a short paragraph explaining the differences above the table.

New table that compares calibration parameters for the two calibration variants. Only keep the parameters that differ across variants, remember to compare common X with vector Xi. A short paragraph above that explains the differences, notably why the level of X changes across the two.

### C. Endogenous design

#### C1. The path in levels

Figure plotting paths in levels for worker-per-retiree, pension design, tax rate, savings rate, and workweek. Interactive parts: Let the user choose countries to include (US, France, UK). Always keep worker-per-retiree as one of them, but let a dropdown menu choose what is plotted next to it. Add paragraph above explaining the paths for each country.

Second figure plotting the same, but only allow one country at a time and instead focus on the difference between endogenous and exogenous theta. Add paragraph explaining the paths for each country.

#### C2. Other countries

**What shapes pensions, savings, and labor supply cross U.S. and UK.**
Two figures side-by-side. The figure from the paper "The effect of various counterfactuals with the design chosen", on the left the US version on the right the corresponding UK version. One paragraph above that explains the major differences. If possible, I prefer the alternative, to repackage this as an interactive figure: We can choose between four figures in a dropdown menu (pension design, equilibrium tax rate, savings over GDP, and average workweek). When we choose one, we display the US results next to the UK results.

#### C3. Other cost specifications

Similar to "other countries", but now for US and with with different cost specifications (I think we only have two). 

#### C4. Other parameters

Similar to "other countries", but now for US and with varying ξ. If we have this for combinations of ξ and ρ and even for several countries, add these as well. We don't want to bother simulating new evidence here, however.


## 2. Execution plan (2026-10-09; replaces the site proposal of 2026-10-08)

### 2.1 How the site works

The online appendix is a Quarto *book*: a static website (HTML, CSS, JavaScript files) that GitHub Pages serves.
Nothing runs on a server and nothing is solved in the browser.

- **Pages** are `.qmd` files in `writing/OnlineAppendix/`: Markdown prose with LaTeX math, plus code cells.
  `_quarto.yml` lists them. A `part:` is a section (A, B, C, D) whose own file is a short landing page; the
  sidebar lists its subsection pages. Quarto adds the sidebar, search and previous/next links.
- **Exhibits come from the pipeline.** `build.py --site` reads `results/` and writes into `_generated/`: the
  static figures (SVG from the matplotlib builders), the tables (HTML converted from the generated `.tex`), one
  tidy csv per interactive figure, and the `\oa` macros the paper uses. A page pulls an exhibit in with
  `{{< include _generated/... >}}`.
- **Interaction is Observable JS (OJS).** An `{ojs}` cell is JavaScript that runs in the reader's browser, and
  cells are reactive: `viewof rho = Inputs.range([0.5, 2], {step: 0.1})` draws a slider, and every cell that
  uses `rho` reruns when it moves. Charts are drawn by Observable Plot from the csv
  (`FileAttachment(...).csv()`); Plot and Inputs load from a CDN, as MathJax does. A shared module
  (`assets/oa.js`) holds the two chart types of 2.5, so each page needs only a few lines of code.
- **Toggles between unrelated exhibits** (two tables, say) are Quarto tabsets (`::: {.panel-tabset}`): no
  custom code.
- **Publishing**: `quarto render`, then `quarto publish gh-pages`, on RKB's go.

### 2.2 Decisions before execution (recommendation first)

| # | Item | Options | Recommendation |
|---|---|---|---|
| D1 | B3: the design-given counterfactuals at other ξ | (a) new code and a run: the U.S. and France recalibrated at ξ = 0.2 and 0.4 (ρ = 1), then the shocks; about half a day of code, minutes of compute. (b) drop B3 | (a): section 7 has its ξ check (C4), section 6 has none |
| D2 | C1's UK and France paths | the path stage takes no host yet: new code and a log-preference run (ρ = 1, minutes). France has no own λ (no value re-elects θ = 1) | run it; by default all three countries under the U.S. λ (the paper's cross-country test along the path), with a switch to each country's own λ (France then at θ = 1, where the cost is zero) |
| D3 | C2's UK ageing row | the endogenous design has no ageing run on the UK. Log: minutes. CRRA (exact method): roughly 1–2 h per ρ, in the background | both |
| D4 | Additions to the outline | C5 the timing of the choice (the paper cites `\oa{esc-timing}`); section D: data, numerical checks, replication (`\oa{num-selection}`, figure 1.1's data); in B4, the counterfactuals that differ between the two calibrations | all three |
| D5 | The outputs the new site no longer shows (about 50: the result tables, the vector-X twins, the old composite figures) | retire them with their builders once the site is up, or keep them | retire, at the end, on RKB's go |
| D6 | Where to work | a branch in its own worktree, merged at the end; or `main` | worktree: the paper session commits to `main` in this checkout |

Two design calls, taken unless RKB objects: B2's first figure uses C2's interactive form (outcome chosen in a
menu, the two hosts one above the other on one axis) rather than the static three-column figure, so every comparison on the site
reads the same way; and B3's and C4's ξ menu becomes "compare across ρ (ξ = 0.3) or across ξ (ρ = 1)", which
uses every run there is and shows the values side by side rather than one at a time.

### 2.3 Data

| Page | Reads | New |
|---|---|---|
| A1 | `sweeps/epsThetaGrid_rho1.0000_commonX.csv` (27 ε × 14 θ, ρ = 1) | -- |
| A2 | `calibration/informalSavings_rhoGridCommonX.csv`; `shocks/universal_match_rho*_commonX.csv` (16 ρ) | -- |
| A3 | `paper/calibrationSummary.csv`; both Argentine ρ-grid sweeps | -- |
| B1 | the three countries' ρ-grid sweeps | -- |
| B2 | `shocks/{US,UK}_shocksCommonX.csv`; `paper/usCalibrationSummary.csv` | `shocks/UKUS_shocks{,CommonX}.csv` (`runShocksUS.py --host UKUS`, agreed) |
| B3 | -- | D1 |
| B4 | as A3 for the three countries; `shocks/{US,UK}_shocks.csv` for the vector-X counterfactuals | -- |
| C1 | `esc/escPath.csv` (U.S., log, both costs); `escPathCRRA.csv` (U.S., ρ = 0.5 and 2, no pinned workweek stored) | UK and France paths (D2) |
| C2 | `esc/escExperiments.csv`, `escExperimentsUK.csv` | the UK's ageing row (D3) |
| C3 | `esc/escExperiments.csv` (both costs, all three ρ); the two cost calibrations | -- |
| C4 | `esc/escXiRobustness.csv` (ξ = 0.2, 0.3, 0.4 at ρ = 1: λ, the path, acute ageing only); `escPathCRRA.csv` | -- |
| C5, D | the built tables `ESC_Timing`, `NUM_Stationary`, `NUM_Selection`, `OECD_Countries`, `OECD_Sources`, `OECD_Correlations` | -- |

**Time windows.** Argentina 2010–2100: the reform files start in the reform year, and the calendar's dated part
ends in 2100. The U.S., the UK and France 1990–2110: 1960 is the initial period, 1990 the period whose electorate
sets the 2020 design, 2110 the last dated period; 2140 lies in the steady-state tail and 2170 is the terminal
period.

### 2.4 Site map

| Page | Key | Exhibits | Controls |
|---|---|---|---|
| Index | (home) | the map of A–D, how to read the site, version, how to cite | -- |
| A. Argentina | `arg` | landing | -- |
| A1 How pension designs shape the equilibria | `arg-designs` | `ARG_LOG_FourInOne` | -- |
| A2 The intertemporal elasticity of substitution | `arg-ies` | `ARG_RhoGrid`; the path explorer (figure 5.2 cited, not shown) | ρ slider |
| A3 Identification of X | `arg-leisure` | tables A3.1, A3.2 (new) | -- |
| B. Rich OECD countries with the design given | `oecd` | landing | -- |
| B1 Calibration | `oecd-ies` | `OECD_RhoGrid` | -- |
| B2 Other countries | `oecd-countries` | explorer U.S. vs UK; table B2.1 (new), the regroupings' household tables in tabs; explorer UK at its own vs at U.S. groups | outcome |
| B3 Other parameters | `oecd-parameters` | explorer, U.S. (D1) | outcome; compare across ρ or ξ |
| B4 Identification of X | `oecd-leisure` | tables B4.1, B4.2 (new); explorer of the rows that differ | outcome; host |
| C. Endogenous design | `esc` | landing | -- |
| C1 The path in levels | `esc-paths` | path explorer by country; chosen vs pinned for one country | countries; variable; cost parameter |
| C2 Other countries | `esc-countries` | explorer U.S. vs UK | outcome |
| C3 Other cost specifications | `esc-costs` | explorer, the paper's cost vs the cost on the design; table C3.1 (new) | outcome |
| C4 Other parameters | `esc-parameters` | explorer, U.S.; the path across ρ or ξ | outcome or variable; compare across ρ or ξ |
| C5 The timing of the choice (D4) | `esc-timing` | `ESC_Timing` | -- |
| D. Data and computation (D4) | `checks` | landing | -- |
| D1 The cross-section of figure 1.1 | `data` | `OECDdata`; countries, sources, correlations in tabs | tabs |
| D2 Numerical checks | `num` | `NUM_Stationary`, `NUM_Selection` in tabs | tabs |
| D3 Replication | `rep` | every exhibit and dataset with the files it reads, its builder and its command | -- |

Files: the landing pages keep the old chapter names (`argentina.qmd`, `oecd.qmd`, `esc.qmd`), as do D1–D3
(`data.qmd`, `numerical.qmd`, `replication.qmd`), so every address published since 2026-10-07 still opens the
right section. Every other page is a new file named after its key. A new key never reuses an old key with a
different meaning.

### 2.5 Design

**Two chart types**, each with one grammar, in `assets/oa.js`:

1. *Counterfactual explorer* (B2, B3, B4, C2, C3, C4). Rows are the counterfactuals in the paper's order:
   pension design, ageing, France's income distribution, voting patterns and leisure preferences; section C has
   no design row. Two facets, one above the other on one x axis, hold the two things compared: U.S. | UK, own groups |
   U.S. groups, common X | vector X_i, the paper's cost | the cost on the design. A menu picks the outcome (tax
   rate, savings over GDP, workweek; in C also the design θ_2020, as a level). Colour is ρ = 0.5, 1, 2, as in
   figures 6.1 and 7.1.
   - Design given: figure 6.1's grammar. Bars from zero, the design row in two tones (θ = 0, θ = 1), and ageing
     as the acute-ageing bar with a tick for mild ageing.
   - Design chosen: figure 7.1's grammar. An open marker for pinned, a filled one for chosen.
   - Hover gives the value in the paper's units. On a narrow screen the facets stack.
2. *Path explorer* (A2, C1, C4). Model periods are markers joined by lines on a calendar-year axis, with a
   vertical rule at the reform year (2010) or the calibration year (2020).
   - A2: four panels (tax rate, savings over GDP, workweek, informal savings ratio), pre-reform in grey and
     reform in blue. The ρ slider has the paper's ρ = 1 marked, and that path stays as a faint reference when
     another ρ is chosen. A readout under the slider gives the 2010 and 2040 changes at that ρ, which are the
     two points of figure 5.2 there, so the paper's figure and the explorer read together.
   - C1: workers per retiree on the left, the variable chosen in the menu on the right.

**Conventions across the site**
- **Defaults** are the paper's reading: ρ = 1, common X, the paper's cost, the U.S. A control's default is
  labelled "(the paper's)".
- **Colours** carry one meaning everywhere. ρ uses the paper's three colours; countries use `OECD_RhoGrid`'s
  colours and markers; pinned and chosen are open and filled markers. The palette is written once, from
  `figures.py` (`SERIES`, `INK`), into `_generated/style.json`, which the charts and the CSS both read.
- **Each page** has a title, a paragraph of at most about 120 words above each exhibit, the exhibit and a short
  note. Exhibits are numbered per page (Figure A2.1, Table B4.2). An exhibit that is the paper's carries
  "Figure 5.2 in the paper", with the number read from `main.aux`.
- **Under every exhibit**: Data (csv) and Source (the results files, the builder, the commit). The csvs have
  readable column names with units.
- **No number typed in the prose**, as now. Optional: a few numbers in the prose, computed by the build into
  `_variables.yml` and written `{{< var a2.tax2010 >}}`.
- **Shareable views**: an explorer's state goes in the address (`#rho=1.4&outcome=tau`), so a link opens the
  same view.
- **A new look**, not the current theme: a light academic page, body text at most about 70 characters wide,
  explorers at page width.

### 2.6 Page by page

What each paragraph covers; every sign and ranking is checked against the csv when it is drafted.

- **Index.** One paragraph: what the appendix is, and that every number is built from the replication package.
  The map as four cards (A–D), each listing its pages with one line. How to read the site: defaults, hover,
  data, badges. Version and how to cite.
- **A, B, C, D landings.** One paragraph on what the section adds to the paper (with the paper's sections and
  appendices it extends), then the map of its pages.
- **A1.** Each point is an economy that has always had that design (ε, θ). The calibrated θ is the line; the
  pre-reform and universal ε are the markers. The paragraph says how the tax rate, savings, hours and the
  informal savings ratio move with ε and θ. Static figure.
- **A2.** Small title 1: `ARG_RhoGrid` and a paragraph: what the calibration absorbs as the IES rises, and that
  an IES of 0.6 or below needs a thirty-year β above one. Small title 2: the path explorer (figure 5.2 is cited,
  not shown), and a paragraph on how the levels of the two paths differ across ρ and why the changes of figure 5.2 follow.
  New dataset `ARG_ReformPaths`.
- **A3.**
  - Opening paragraph: what is identical under the two calibrations (β, ω, the tax rate, savings, every result
    of section 5 at every ρ), and why. The productivity distribution reaches the aggregates only through
    Σγ_iη_i^{1+ξ}/X_i^ξ, which both normalise to one. The tables show only what differs.
  - Table A3.1: the rows of table 1 that differ: X against X_i with their targets, η_i, η_0, X_0.
  - Table A3.2: the parameters solved with the path that differ, at ρ = 0.5, 1, 2: X, η_0, X_0. The X_i are
    data, the same at every ρ.
  - Paragraph on the level of X. Under the common X, X is the unit of hours, pinned by the observed formal
    workweek. Under vector X_i relative hours are data and the unit is a normalisation (Σγ_i y^x_i = 1), so
    the level has no data counterpart; the technical documentation's variants A and B give the argument.
- **B1.** `OECD_RhoGrid` and a paragraph.
- **B2.**
  - Small title 1: the U.S. | UK explorer (five rows, three ρ) and a paragraph on the differences between the
    hosts, row by row. France is cut at the host's income groups.
  - Small title 2: table B2.1, table 3's parameters for the U.S., the UK at its own and at U.S. groups, and
    France at U.S. and at UK groups. Tabs hold the two regroupings' household tables
    (`UKUS_householdheterogeneity`, `FRUK_householdheterogeneity`). The paragraph says what regrouping changes
    (the θ read at other cuts, ω, the productivity spread), and that the UK at U.S. groups is a linear fit of
    the UK's group means, not a recount of the survey (TODO D3).
  - Then the explorer UK at its own groups | at U.S. groups, France at the matching groups, and a paragraph.
- **B3** (D1). The explorer for the U.S. alone, comparing across ρ (ξ = 0.3) or across ξ (ρ = 1), and a
  paragraph.
- **B4.** As A3, for the three countries.
  - Table B4.1: the rows of table 3 that differ (X, η_H/η_L).
  - Table B4.2: X_i and η_i by income group.
  - Added (D4): the counterfactuals the choice of calibration moves. These are France's income distribution and
    leisure preferences, compared common X | vector X_i on each host; on the UK the income-distribution row
    changes sign.
- **C1.** The path explorer (countries, variable, cost parameter), with the observed designs marked in 2020.
  Second, one country at a time, chosen (solid) against pinned (dashed). A paragraph per country. New dataset
  `ESC_Paths`.
- **C2.** The U.S. | UK explorer (θ_2020, tax rate, savings, workweek) and a paragraph on the major differences.
  New dataset `ESC_Counterfactuals`.
- **C3.** The explorer, the paper's cost | the cost on the design (U.S.). Table C3.1: the two calibrations per ρ
  (λ; φ and p; the share of revenue lost at θ* and at θ = 0). The paragraph: what the cost on the design keeps
  that the paper's drops, and where that shows (acute ageing, France's income distribution); the paper's
  section 7 and appendix C.2 cite this page.
- **C4.**
  - The explorer for the U.S., compared across ρ (ξ = 0.3, every row) or across ξ (ρ = 1). Across ξ only acute
    ageing was run, and the figure says so.
  - The path across ρ or ξ. The pinned workweek is stored only at ρ = 1.
- **C5.** `ESC_Timing` and a paragraph.
- **D1–D3.** As in 2.4.

### 2.7 Code

- **`python/paper/siteData.py`** (new): one function per explorer dataset, reading through `datasets.py` only.
  Writes tidy csvs to `results/paper/Data/`. Registered in `build.py` as kind `data`, `ONLINE_ONLY`, so `--map`
  traces their reads and `--list` reports them.
- **`tablesOA.py`**: A3.1, A3.2, B2.1, B4.1, B4.2 and C3.1 as generated `.tex`. They also serve the PDF later.
- **`onlineAppendix.py`**, rewritten small. It writes:
  - one exhibit block per static exhibit (`_generated/exhibits/<name>.qmd`: caption, badge, image or HTML
    table, note, Data and Source links);
  - copies of the datasets and `style.json`;
  - `onlineAppendix.tex` from the page headings, with the old keys as aliases;
  - the version stamp.

  It keeps `texTable.py`, the `Paper` reader (`main.aux`, which exhibits the paper inputs) and the provenance.
  It drops `GROUPS`, the figure-to-table links, the calibration switch, the marking of differing cells and
  `exhibits.js`.
- **`writing/OnlineAppendix/`**: a new `_quarto.yml` (parts), the pages, `assets/oa.js`, `assets/theme.scss`
  and `assets/oa.css`. The old chapter bodies and assets go; they stay in the git history.
- **Model side**, only for the runs decided:
  - `runShocksUS.py --host UKUS`, registered in `python/paper/runShocksUS.py` (both variants);
  - `runESC.py`'s path stage for the UK and France at a given λ;
  - `'acute'` added to the UK's endogenous-design scenarios;
  - D1's ξ option for the design-given calibration and shocks, as `runESCxi.buildUSxi` does it.

  Each comes with a check that it reproduces the rows on disk (the U.S. host, the workbook ξ) and a test.
- **Tests** (`test_onlineAppendix.py`):
  - page keys are unique and every old key is aliased;
  - every include and dataset exists, with its columns, and has no missing values where the results have them;
  - the explorer data at the paper's reading equals the paper's exhibits (figures 5.2, 6.1, 7.1, G.1);
  - `checkPaper.py` is clean.

### 2.8 With the paper session

- **The paper keeps compiling.** The regenerated `onlineAppendix.tex` defines the eleven keys the paper uses as
  aliases of the new pages:

  | Old key | New key |
  |---|---|
  | `arg-calibration` | `arg-leisure` |
  | `oecd-us` | `oecd` |
  | `oecd-vectorx` | `oecd-leisure` |
  | `oecd-rhogrid` | `oecd-ies` |
  | `oecd-calibration`, `oecd-uk` | `oecd-countries` |
  | `esc-path` | `esc-paths` |
  | `esc-scale` | `esc-costs` |
  | `num-selection` | `num` |
  | `arg`, `esc-timing` | unchanged |
- **What this session touches in `writing/Paper`**: only the generated `onlineAppendix.tex`. It does not
  compile the paper, and it builds with `--only` so nothing is copied into `writing/Paper`.
- **Handed over, as a list for that session:**
  - the key map;
  - the sentences the new site no longer supports:
    - section 6's footnote and figure 6.1's note: the tables of numbers leave, and the data downloads replace
      them;
    - appendix E's "the reform at every ρ under both": A3 says it is identical;
    - appendix G's note on figure G.1, "the paths from the first period": C1 starts in 1990.

### 2.9 Phases

0. RKB's decisions D1–D6.
1. **Spike**, in a scratch book, about an hour. It tests a part page, an OJS cell that imports `assets/oa.js`,
   Plot's tooltips in the paper's palette, the view in the address and a tabset, all checked in Chrome with the
   console open. It fixes the components' interface.
2. **Runs**: D1–D3 and the UKUS shocks. They run in the background while phases 3 and 4 proceed.
3. **Data and tables**: `siteData.py`, the new tables, their registration, `--map`.
4. **Skeleton**: `_quarto.yml`, the index, the landing pages, the generator, `oa.js`, the theme; first render.
5. **Pages**, A, B, C, D in that order: exhibits first, then the paragraphs. A paper-writer agent per section
   can draft them, briefed with the style guide and the no-typed-number rule.
6. **Checks**:
   - the tests;
   - a reviewer pass of the prose against the data;
   - a browser pass over every page and control (Chrome, console clean);
   - READMEs (online appendix, `python/paper`), `REPLICATION.md` (section 4's text and the map), the logs.
7. **Close**: retire the unused outputs (D5); publish on RKB's go.

Later: the PDF edition. Each explorer's default view becomes a static figure, and the tables go in as they are.
The site is designed for it now and it is built later.

### 2.10 Optional improvements, not in the outline

- **A1 as an explorer**: a θ slider highlights one curve, with the grid's others in grey and the reform's two ε
  marked.
- **A2**: a switch adds the reform with the tax held at its pre-reform path (table 2's second row; the files
  exist).
- **C3**: the design along the path under both costs (the data exists).
- **Numbers in the prose** through `{{< var >}}` (2.5).

### 2.11 Status (2026-10-09, evening)

**Closed 2026-10-09.** On RKB's go the branch was merged into `main` by fast-forward (`ea52b8e`, the paper
session's uncommitted work carried over, a copy in the stash), the site published (`gh-pages` `e3810ba`), and D5
done: the 59 outputs neither the paper nor the site uses retired with their builders, both groups below included.
What stays open is in `notes/TODO.md`: W13 (the paper's pointers to the site) and C12 (the PDF edition).

**Where the work is.** Branch `oa-revision` in the worktree `C:\Users\sxj477\Documents\GitHub\SSDclaude-oa` (D6), not
merged into `main` and not published. Render it with `quarto render writing\OnlineAppendix` there and serve
`_book` (the worktree's README says how).

**Built.** Every page of 2.4 (20), the four datasets and six tables of 2.7, the new generator and the chart module.
Decided along the way:
- Time windows as 2.3.
- B2's figure uses the explorer form, and B3/C4 compare across ρ or across ξ.
- C1 defaults to the U.S. cost parameter for all countries. Under "own", France is shown with its design pinned
  at 1, where the cost is zero.
- Exhibits are numbered per page. Paper numbers in prose come through `{{< var p.<label> >}}`.

The runs D1–D3 and the UKUS shocks are done. Each left every published row unchanged:
- **D1.** ξ = 0.3 reproduces `US_shocksCommonX.csv` to 7e-12.
- **D3.** The UK's acute ageing under the chosen design ran in LOG and in exact CRRA, about 7 minutes per ρ. Under
  it the UK's chosen design rises from 0.560 to between 0.656 and 0.672.

**RKB's comments on the layout** (`2026-10-09`, the commit after `20554ca`): figure 5.2 is no longer shown on A2; the
two facets of B2.1, B2.2, B4.1, C2.1 and C3.1 are stacked on one x axis; the counterfactual charts sit in the text
column (B3.1 and C4.1 were off-centre), and every chart draws at the width of its own box.

**Prose review.** An agent checked every claim against the datasets and tables; its 17 findings (six claims the data
contradicted, among them B2's ranking at ρ = 2 and three dates in C1) are fixed in `20554ca`.

**Checks.**
- `test_onlineAppendix.py`: 10 of 10. Each dataset equals the paper's figures 5.2, 6.1, 7.1 and G.1 at their marks.
- `US/test_esc.py`: 85 of 85.
- `checkPaper.py` finds no missing `\oa` key (53 defined). Its FAIL is the one already in the paper log.
- Every page was rendered in headless Chrome, at its defaults and at non-default views opened from the address.

**For the paper session** (nothing in `writing/Paper` was touched except the generated `onlineAppendix.tex`, and
only on the branch):
- **The paper keeps compiling.** Every key it cites is defined: the retired ones as aliases of their new pages
  (`OLDKEYS` in `python/paper/onlineAppendix.py`).
- **Pointing at the new keys**, when convenient:

  | Old key | New key |
  |---|---|
  | `arg-calibration` | `arg-leisure` |
  | `oecd-us` | `oecd` |
  | `oecd-vectorx` | `oecd-leisure` |
  | `oecd-rhogrid` | `oecd-ies` |
  | `oecd-calibration` | `oecd-regroup` |
  | `oecd-uk` | `oecd-countries` |
  | `esc-path` | `esc-paths` |
  | `esc-scale` | `esc-costs` |
  | `num-selection` | `num` |
- **Sentences the new site no longer supports:**
  - section 6's footnote ("holds every table behind the figures of this section") and figure 6.1's note ("Full
    tables with results are printed in the online appendix"): the tables leave, and each figure's data download
    replaces them;
  - appendix E's "and the reform at every ρ under both, are reported in the online appendix": A3 says it is
    identical;
  - appendix G's note to figure G.1 ("the paths from the first period"): C1 runs from 1990.
- **New results the paper may want:**
  - the UK's acute ageing under the chosen design (C2);
  - the design paths of the UK and France (C1);
  - section 6's ranking at ξ = 0.2 and 0.4: ageing and the design first at every ξ (B3).
- **One convention to keep aligned.** The site reads every endogenous-design counterfactual against the baseline
  of the same reading, pinned against pinned and chosen against chosen. That is the paper session's uncommitted
  change to `figuresUS`/`tablesUS`, which this branch does not carry.

**Open, RKB's.**
- **D5, in two groups.**
  - Safe to retire, since neither the site nor the paper uses them: every `_vectorX` twin (A3 and B4
    read the calibration summaries directly); `US_PensChars`,
    `US_Ageing`, `US_OtherShocks` and their CRRA tables; `UK_OtherShocks` and the UK CRRA tables;
    `ArgentinaReformPath`, `ArgentinaReformByRho`, `ARG_RhoGridTable`, `OECD_RhoGridTable`, `ESC_Path`,
    `ESC_PathTable`, `ESC_Xi`; `UKUS_French`.
  - To decide with the paper session, which is editing them: `US_ESC_Ageing`, `US_ESC_IncomeDistr`, `US_ESC_Voting`,
    `US_ESC_FrenchAll`, `US_ESC_Summary`, `US_ESC_Results`, `US_ESC_Country` (commented out in G.1),
    `US_ESC_ScaleWedge`, the three `UK_ESC_*` tables, `UKUS_ESC_French`, `Argentina_funcOfRho`.
- **Merge and publish.** Merge `oa-revision` into `main` once the paper session has committed; the expected
  conflicts are `python/paper/onlineAppendix.py` (the branch's version wins), `REPLICATION.md` and the READMEs.
  Then `build.py --site`, `quarto render` and `quarto publish gh-pages`.
- **The PDF edition** (later): the tables' tex is kept, and `texTable.printTex` still resolves references for print.
