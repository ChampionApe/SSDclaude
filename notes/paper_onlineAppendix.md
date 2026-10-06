# The appendix split and the online appendix (2026-10-06)

Proposal for RKB (and MGE), for session 4 of the paper rewrite. It replaces the LaTeX second root (agent D1) of
`notes/paper_presentationPlan.md` §8 and makes the split of §3's appendix table concrete. Two questions: what stays
in the paper's appendix and what goes online, and what the online appendix should be. Fixed by RKB on 2026-10-06:
B.2–B.3 stay in the paper for now; the online appendix need not be a PDF and may be a website in or beside the
repository. Record decisions in the block at the end.

## 1. What there is to work with

- **The appendices**: 8,134 words (`writing/checkPaper.py`), 34 tables and 4 figures. The main text cites into
  them about 25 times; the targets are listed in §3.
- **`results/` holds more than the paper prints.** Argentina's reform at 16 values of ρ (0.5 to 2.0) with paths
  over seven periods (`shocks/universal_match_rho*`); the ε–θ surface on 27 × 14 points at ρ = 1
  (`sweeps/epsThetaGrid*`); every country's calibration on the same 16-point ρ grid (`calibration/*_rhoGrid*`);
  the chosen design and the tax along the baseline path, 1960–2170 (`esc/escPath*`); ξ at 0.2, 0.3 and 0.4
  (`esc/escXiRobustness.csv`); the timing checks (`esc/escPermanent*`, `escSequentialCRRA.csv`); the
  stationary-versus-date-specific checks behind section 4's accuracy footnote (`numerical/`, read by no output);
  and the equilibrium counts `nEqMax`, `nCandMax`, `nFallback` in every csv. The U.S. counterfactuals are stored
  at 2020 only.
- **Every robustness dimension of the headline results has already been run.** With the design given: ρ ×
  calibration variant × host (U.S., UK), twelve specifications for every counterfactual. With the design chosen:
  ρ × cost specification (size, scale), the UK as host for the French characteristics, and ξ at ρ = 1.
- **The overview figures already summarize whole table families.** `US_overview` (main text) draws every
  scenario row of the three CRRA tables, `US_ESC_overview` (main text) every row of the four endogenous-design
  tables, and `UKUS_ESC_French` the design and tax of the UK's.
- **Gate 1 kept three things out of the paper**: the drift numbers and the ξ table (G1.3), and the
  permanent-timing switch point (G1.7). The online appendix can carry them without re-opening those calls.
- **Tooling**: Quarto 1.10, pandoc 3.10 and Node 24 are installed. `ChampionApe/SSDclaude` is public on GitHub,
  and Pages is not yet enabled.

## 2. Principles for the split

1. The PDF (the paper and its appendix) carries every derivation and identifying assumption, and every number
   the main text quotes, in a table or readable from a figure. The paper can be refereed without the online
   appendix.
2. The online appendix adds depth and is not needed to complete the argument. It holds the calibration
   variants, the second host, the alternative specifications, full grids and paths, numerical checks, data and
   provenance.
3. The online appendix is a superset: it also shows every exhibit of the paper, so a reader looking up a
   number never switches documents. The derivations of A–C are not duplicated; the site links to the PDF.
4. Neither carries a hand-typed number: both are built by `python/paper` from `results/`.

## 3. The split

**Option K (recommended): keep what the main text quotes.**

| Item | Goes to | Reason |
|---|---|---|
| A economic equilibrium; B.1 proposition 2; B.4 the corner | paper | proofs, cited by sections 3, 4, 7 |
| B.2–B.3 informal savings | paper | RKB, for now |
| C terminal states | paper | cited by section 4 |
| D Argentina's calibration | paper, the survey description cut to one paragraph (about −200 words) | identification |
| D.5 vector-X (1 table) | online | the results are identical; section 5's footnote points online |
| `ARG_CRRA_LOG` figure | paper | cited by section 5 |
| E.1–E.3 household tables | paper | calibration inputs |
| E.4–E.5 regroupings (2 tables) | online | they serve the UK host and `US_ESC_Country`'s UKUS row |
| F.1 CRRA (2 tables) | paper | section 6 quotes 9.0/6.2/1.5 and 7.6–9.3 p.p. |
| F.2 vector-X (14 tables, 1 figure) | online | becomes a toggle on every exhibit |
| F.3 `US_ESC_Ageing` | paper | quoted in 7.4 |
| F.3 scale wedge (1 table) | online, as a specification comparison (W8e) | robustness, not quoted |
| G.1 `US_OtherShocks`, `US_CRRA_OtherShocks` | paper | quoted in section 6 |
| G.1 the UK as host (2 tables, 1 figure) | online | one sentence in section 6 |
| G.2 U.S. endogenous design (3 tables) | paper | quoted in 7.4 |
| G.2 the UK as host (3 tables, 1 figure) | online | one sentence in 7.4 |
| New: the robustness map (§4a) | paper, last appendix item, and the online front page | replaces the moved tables in the PDF |

About 1,960 words and 23 of the 34 tables leave the PDF; with the survey cut the appendix is about 6,000 words, 11
tables and 2 figures (plan §3 aimed at about 5,000). The paper appendix then reads A–C derivations, D–E
calibration, F results for the U.S. (CRRA; French characteristics; the endogenous design), G the robustness map.
The two UK sentences in sections 6 and 7 cite the map and the online appendix; under principle 1 their bounds
("no more than 0.6 p.p.", "within 0.1 p.p.") are readable from the map, or `UK_OtherShocks` stays (O2).

Main-text pointers to retarget: `app:EPH:vectorX` (section 5's footnote), `app:US:vectorX` (section 6 and the
footnote of 7.4), `table:UK:otherShocks` (section 6), `app:US:ukESC` (7.3, 7.4 twice). Section 5 is under RKB's
Overleaf edit: retarget after that pass is pulled.

**Option S: the slim PDF appendix.** A–E and the summary figures only; every result table of F–G online, cited
there from the main text (another about 900 words and 8 tables out). Right when the target journal publishes all
appendices online anyway; option K is right when the appendix is printed with the article, since online
appendices are neither typeset nor read with the paper.

## 4. New material

**(a) For the paper's appendix: a robustness map (recommended).** One figure of small multiples, one panel per
headline result: the tax effect of θ (θ = 1 to 0), of acute ageing, of France's income distribution and of its
voting patterns; the chosen design under acute ageing, France's income distribution and its voting patterns. One
marker per specification: ρ by colour in the paper's palette, the calibration variant by marker shape, the host
by row group, and for the chosen design ξ and the cost specification. The paper's value is a reference line. It
stands in for the 23 tables in the PDF, and shows where the results hold (θ, ageing) and where they move (the
income-distribution row changes sign across variants on the UK and across hosts; at ρ = 2 French voting moves
the design to 0.335). That is the documented-exception reading C1 recommended for W8(a)–(b). Every value exists;
one builder in `figuresUS.py`.

**(b) Optional compactions for the paper**: the three household tables as one, three countries side by side; the
three CRRA tables as the one table behind figure `US_overview`.

**(c) Online only, each a builder on existing results, no run:**
- the design and the tax along the baseline path, 1960–2170, chosen against pinned, at ξ = 0.2, 0.3, 0.4;
- the timing of the choice: contemporaneous, advance, permanent, with the switch point;
- the calibration across the 16-point ρ grid for each country: β, ω, X, R, the political weight of the old that
  sections 6–7 say falls with the IES;
- Argentina: the reform at every ρ of the grid with its path; the ε–θ surface, with the reform as a move on it;
- numerical checks: stationary against date-specific policies (section 4's footnote), the equilibrium counts per
  exhibit;
- figure 1's data: the country table with sources and the correlations (`results/paper/oecdCorrelations.csv`);
- the technical documentation and `REPLICATION.md`, linked from every exhibit.

**(d) Needs a run (optional):** the U.S. counterfactuals as full paths (stage (ii) keeps 2020 only; minutes under
LOG); the model's own figure 1, the chosen design and the tax against population growth and against inequality
under the paper's cost (`esc/escFig1.csv` has it for the superseded scale cost only; a LOG run). The second is a
candidate for the paper itself, as the close of the arc.

## 5. What kind of online appendix

| Form | Interactive | Journal-ready | Cost | Verdict |
|---|---|---|---|---|
| PDF from a second LaTeX root (plan's D1) | no | yes | low | falls out of the recommendation anyway |
| Markdown pages in the GitHub repo | no: GitHub strips scripts | no | low | browsable, not interactive |
| **Quarto site on GitHub Pages, with a PDF from the same source** | yes | yes, the PDF | medium | **recommended** |
| A JavaScript dashboard (Observable, Vega) | yes | no | high | redraws the figures, a second code path that drifts from the paper's |
| An app with a server (Shiny, Streamlit) | yes | no | high | dies with the server |
| An explorable (Nicky Case tree) | yes | no | high | a teaching companion, not a reference work |
| A Claude artifact page | yes | no | low | private by default, not citable: prototyping and review only |

**The recommendation: an exhibit atlas.** Victor's "argumentative" explorable (the skill's playbook §8:
assertions backed by inspectable models, every fact and calculation visible) describes the online appendix of a
paper better than Case's pedagogical one.
- *Front door*: the robustness map. Every marker opens the exhibit behind it.
- *One page per family*: data; Argentina; the rich economies with the design given; the endogenous design;
  numerical checks; replication. Each page sets the paper's figure, as SVG, beside the tables behind it. Hover
  gives the exact value; clicking a mark pulls up its table with the row highlighted; segmented controls select
  host (U.S./UK), calibration (common X / vector Xᵢ), ρ, and θ pinned/chosen. A *diff* switch highlights the
  cells that change between two selections, so "only the income-distribution rows move between variants" is
  seen, not read. Every selection has a URL, so a single number can be linked.
- *Provenance on every exhibit*: the csv it was read from (downloadable), the builder, the stage command, the
  commit.
- *Static read*: without JavaScript every page shows its default selection. A print edition (PDF, sections
  OA.1, OA.2, …) holds every table; it is what the journal receives.

```
OA.4 Endogenous design ▸ French characteristics          Host [US|UK]  ρ [0.5|1|2|all]  [diff]
┌──────────────────────────────────────────┬───────────────────────────────────────────┐
│ the paper's figure (SVG)                  │ [Ageing | Income distr. | Voting | All]    │
│  French voting  ○──●   hover: 0.653       │  ρ    θ pinned  θ chosen   tax    ...      │
│  …                                        │  1.0  0.738     0.653 ◀    …               │
│  click a mark → its table, row lit        │                                            │
├──────────────────────────────────────────┴───────────────────────────────────────────┤
│ source: results/esc/escExperiments.csv · tablesUS.escVoting · commit · csv · paper: table n │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**Architecture, which keeps the pipeline's invariants:**
- *Tables*: the site's tables are translated from the generated `.tex` the paper inputs, by a converter for the
  builders' own vocabulary (tabularx rows, `\multicolumn`, `\tnote`, tablenotes). Paper and site cannot disagree
  on a number because they are the same file, and no builder is refactored; a test converts all 44 tables.
- *Figures*: the matplotlib builders also write SVG with each mark tagged by its key (scenario, ρ, variant,
  quantity, value); one vendored script (about 200 lines, no framework) adds tooltips and figure-to-table
  linking. One figure code path, so the site's figures are the paper's.
- *Pages*: Quarto in `writing/OnlineAppendix/`, prose in Markdown with math and citations from `References.bib`,
  generated fragments included. Provenance comes from `build.py`'s existing input tracing.
- *Build*: `build.py --site` (stage (iii): reads `results/` only, seconds), then `quarto render`; the print edition
  from the same pages.
- *Publishing*: `quarto publish gh-pages`, at RKB's go each time, from when the paper circulates; local preview
  until then, since a rendered site is far more discoverable than the public repo. At acceptance, a tagged
  release with a Zenodo DOI archives the code, the results, the site and the print edition.
- *Cross-references*: the site build writes `writing/Paper/onlineAppendix.tex` with one macro per anchor, so the
  paper writes `\oa{esc-uk}` and prints "Online Appendix OA.4.2" linked to the page; `checkPaper.py` checks the
  keys. The site reads the paper's numbers from `main.aux` when it exists, to say "table 7 of the paper".
- *A data layer*: each exhibit's values also go to JSON. A seminar deck (explorable-deck keeps every number in
  one data object) or a later explorable reads the same file, so paper, site and talk cannot disagree.
- *Rules*: no hand-typed numbers in the site's prose; the prose says what an exhibit is and how to read it, and
  the mechanisms stay in the paper.

**The two skills.** explorable-explanations is the wrong genre for an appendix: one idea per slide, a guided
path, about half the screen white, where an appendix is scanned and looked up. It is the right genre for a later
companion on the mechanism: the corner proposition with a slider for how steeply voting propensities rise with
income (the derivative of `eq:esc:seqFOC` is closed form, computable in the browser), then the cost and λ.
explorable-deck is for talks; it is Quarto too, and would read the site's data layer.

## 6. Work plan

- **A. Decisions** (below).
- **B. The paper's appendix**, one session, independent of the form: the split of §3; the robustness map's
  builder; the open items of `notes/paper_gate3.md` §3 and `notes/paper_gate2.md` §3 (C1's point c, μᵢ in the
  proposition; B.3's μ₀ where r₀ is meant; B.2's β_{t,0}; C's Γ_{t,h}; B.1's "type type"; part v's γ₀ claim;
  D's ε formula with RKB, its ξ promise and its hours sentence; E's LIS year; F.1's repeated mechanism; G.1's
  1.6 → 1.5 p.p. and "France's demography" alone; W8(e)); the main-text pointers after RKB's Overleaf pass.
- **C. A prototype**, half a day: one family, the endogenous design (`US_ESC_overview` with its four tables and
  the UK toggle), rendered locally for RKB and MGE.
- **D. The online appendix**, one to two sessions: every family, the online-only exhibits of §4c, the print
  edition, the `\oa` macros, an online-appendix column in `REPLICATION.md`, the first publish.
- **E. Optional**: the runs of §4d, the mechanism explorable, a seminar deck on the same data.

## 7. State on 2026-10-06 and hand-off to the drafting of sections 6–8

Built and merged: the appendix split (commit `a7bfcd4`), the site and print edition (`7a4c45c`, build with
`build.py --site` then `quarto render writing/OnlineAppendix`; its README), RKB's section 6 edit merged on top
(`4308629`) and pushed to Overleaf; integrated and checked the same day (every page's self-test, the paper compiled
in a scratch copy). Open on the site, none blocking: the composite "Income distr. + voting" of the two endogenous-design
figures is in no table (gate 3's open item, `python/paper`); MathJax loads from its CDN; publishing to GitHub Pages
is RKB's call. A session that drafts the main sections should know:
- **`\oa{key}`** cites the online appendix: it prints "online appendix" linked to the key's page, so the paper writes
  "the \oa{esc-uk}" (RKB, 2026-10-06: never "Online Appendix OA.4.3"; `\oanum{key}` keeps the number); the keys and
  sections are in `writing/Paper/onlineAppendix.tex` and `notes/brief_onlineAppendix_2026-10-06.md` §2.4. Never in
  a caption or heading (it is a link). `checkPaper.py` fails on an unknown key.
- **One main-text sentence is stale**: section 7's "appendix \ref{app:US:escTables} reports it as a robustness
  check" (the cost on the design is Online Appendix \oa{esc-scale}). Section 6's went when RKB cut its vector-X
  footnote; appendix E now points to \ref{app:US:vectorX}. Optional new pointers: section 5's vector-X footnote
  → \oa{arg-calibration}; 7.4's ξ footnote and drift sentence → \oa{esc-path}; section 4's accuracy footnote →
  \oa{num-stationary}, its selection sentence → \oa{num-selection}; figure 1's note → \oa{data}.
- **Open, RKB's**: C1's point c (propensities to vote in proposition 2); appendix D's pre-reform ε formula (0.21
  with the first quartile, 0.29 with the second); appendix D's claim that the 2006 sample precedes the
  amnesties' coverage increase, while section 5 dates them from 2005.
- **Done 2026-10-06 (afternoon)**, commits `753bed7` and `94865a2`, pushed: section 6's calibration states only
  its differences from Argentina's (RKB's wording) with the detail in appendix E, OA.3's opening adjusted;
  `table:US:Calib`'s lower panel of shared parameters; `fig:US:overview` with one design row in two tones, one
  ageing row (mild as a line), French leisure; every figure centred (style guide §5). The site shows the old
  overview and table until `build.py --site` and `quarto render`.
- **Done 2026-10-06 (evening)**, with RKB, sections 5 and 6: the split moved further toward option S. Online only now:
  `ARG_LOG_FourInOne` (section 5's ε–θ figure, OA.2.4), `US_PensChars` and `US_Ageing` (section 6's results part leads
  with `fig:US:overview` and points to OA.3.4–3.5 up front), appendix F.1–F.2 and appendix G whole (`Appendix/UKvsUS.tex`
  deleted; its mechanism prose, without numbers, is in `oecd.qmd` OA.3.5 and `esc.qmd` OA.4.3). The paper inputs 15 of
  the 81 exhibits; appendix F holds `US_ESC_Ageing` only and the robustness map is appendix G. Section 7's references
  into G are `\oa` pointers (`esc-us`, `esc-uk`); its prose waits for the next session. Section 6 now states the ranking
  for ρ ≤ 1 and names ρ = 2 as the exception (W8(b) there); the abstract, introduction and conclusion still carry the
  unqualified claims. **Open, RKB's, from the section 5 read**: the pre-reform ε (0.21 by appendix D's formula with the
  first quartile against the code's 0.29 with the second); γ₀ = 0.32 counted per formal household (24% of households)
  against "the share of retirees"; "2.7 million beneficiaries" against the figure's rise of about 2.0; the 2006 sample
  dated before the amnesties while section 5 dates them from 2005; appendix D's "chosen such that 2η¹h¹ = η²h² = h"
  where the workbook matches quartiles 1 and 3 (relative incomes 0.47 and 1.00); section 5's opening sentence and its
  hand-off, cut in RKB's online edit; an "All three" row in `fig:US:overview`. *Later the same evening*: the 2006
  timing and the θ-identification sentence are fixed in appendix D; the 2.7 million is Rofman and Apella's (2015)
  gross count to 2011 and is now cited as such beside the figure's net rise of about 2 million (Cetrángolo and
  Grushka 2020, table 6, which the figure note now names), the coverage reads "over 90%" in section 5 and the
  introduction, the 32% is the share of the elderly without a pension (Rofman and Oliveri), the 7.1% is the all-scheme
  total; the ε and γ₀ mismatches are confirmed and quantified, TODO C8. *The online appendix* was read by a
  paper-reviewer and revised the same evening (root and paper logs of the date); what it left open: the composite
  row's workweek marks link to no table (the table's composite also imposes France's X); the OA.3.2 comparison table
  lists every ρ as a differing row for the ρ-grid tables where the differing columns would read better; the Source
  blocks show the build step but not the stage that wrote each csv; `data/USMain_test.xlsx` and `ArgentinaTest.xlsx`
  read as scratch names; the paper's section 6 does not say that a thirty-year β above one is needed at an IES of 0.6
  or below (the online appendix's OA.2.5 and OA.3.3 now do); publishing to GitHub Pages is still RKB's call, and the
  paper's introduction now prints the address.
- **Left for sections 6–8**: TODO W8(a)/(b); the conclusion's "a higher IES changes only the size of the
  earnings-link effect" against section 6, where French voting's effect grows from 0.3 to 1.7 p.p.; section 7 at
  3,708 words against ≈ 2,800 and the conclusion at 504 against ≈ 450. Smaller: section 5 never states the equal
  propensities to vote that section 6 now cites for Argentina; style guide §5's rule that section 6 points to the
  vector-X alternative itself is stale after RKB's cut (his call); an "All three" row in `fig:US:overview`, as in
  `UKUS_French`, would show the composite section 6 discusses.
- **One Overleaf channel**: only one session pulls and pushes. A pull overwrites every local text file that
  differs from Overleaf, so commit before every pull (memory `overleaf-pull-overwrites-local`).

## DECISIONS (RKB)

Fill in below; a blank line means "as recommended".

- **O1 The split.** Option K (recommended) or option S. The target journal decides: does it print appendices
  with the article?
  RKB, 2026-10-06: the target is REStud, JPE or AEJ: Economic Policy; option K.
  RKB, 2026-10-06 (evening): further toward option S for sections 5–6: their result tables and appendices F.1–F.2
  and G go online, the sections lead with their figures and point to the online appendix up front (§7).
- **O2 The UK as host.** Wholly online, with the two sentences in sections 6 and 7 citing the map (recommended),
  or `UK_OtherShocks` kept in the paper.
  RKB, 2026-10-06: some UK results stay in the paper's appendix. Implemented as `UK_OtherShocks` and the two
  host figures `UKUS_French`, `UKUS_ESC_French` kept; the UK's CRRA and endogenous-design tables online.
- **O3 The robustness map** as the paper's last appendix item and the online front page (recommended).
  RKB:
- **O4 Online-only exhibits from existing results** (§4c; recommended: all).
  RKB:
- **O5 Runs** (§4d): the U.S. paths; the model's figure 1, and whether it goes in the paper.
  RKB:
- **O6 The form.** A Quarto site on GitHub Pages with a print edition from the same source (recommended); a site
  only; a PDF only.
  RKB, 2026-10-06: as recommended; build all of it (O8: no prototype gate). The build contract is
  `notes/brief_onlineAppendix_2026-10-06.md`.
- **O7 Where the online appendix's prose lives.** In the repo as Markdown, edited here, with MGE commenting on
  the rendered site or PDF (recommended); or LaTeX on Overleaf, converted at build.
  RKB:
- **O8 A prototype of one family before the rest** (recommended).
  RKB:
