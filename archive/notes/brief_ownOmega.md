# Brief: "layer 1" becomes the model, "layer 2" becomes own ω (section 7.3, appendix G, online appendix)

Written 2026-11-07 for RKB: in section 7.3, what we call "layer 1" is simply "the model"; "layer 2" stays out of
table 5 and appears for the first time at figure 7.3, as "own ω". RKB: "I don't think layer 2 adds much, so I'd rather
keep it as a secondary thing." Every appendix and online-appendix page follows. Two agents share this brief: Part A
(builders, paper-compute) and Part B (prose, paper-writer). The names below are their interface.

No number changes anywhere. Internal names stay: the csvs `layer1.csv`/`layer2.csv`, the code's `layer` arguments,
`config` keys, file names (`OECD26_Layer1.pdf`), the tex labels (`fig:OECD26:layer1`, `app:oecd26:layer2`), the
`p.*` variables of the site and the online-appendix anchors (`#esc-oecd26-omegaUS`, ...). Only what a reader sees
changes.

## Names (the interface)

| Was | Prose | Generated labels (headers, rows, panel titles, legends) |
|---|---|---|
| layer 1, the first layer | the model | `Model` (legend entry: `model`) |
| layer 2, the second layer | the model with each country's own political weight, "own $\omega$" for short after first use | `Own $\omega$` |
| layer 1 at the mean ω | the model, at $\omega = 1.20$, the mean of the political weights that match each country's spending at its observed design | `Model` (where the ω rule must show: `Model: mean $\omega$`) |
| layer 1 at the U.S. ω (online appendix) | the model at the U.S. political weight | `Model: U.S. $\omega$` |

Before figure 7.3 the reader meets the mean weight (needed to define the model) but not own ω as a variant: "the mean
of the political weights that match each country's pension spending at its observed design (appendix G.3)" is fine;
"layer", "second layer" or "own ω" is not. Figure 6.2's note uses no layer word either (its ω, 1.17, is the mean of the
weights that reproduce each country's spending **without** the cost).

## Part A — builders (paper-compute)

Files: `python/paper/tablesOECD26.py`, `figuresOECD26.py`, `onlineAppendix.py`, `test_oecd26.py`,
`test_onlineAppendix.py` (only if it pins a changed string), `build.py` (comments only), `README.md`,
`RESEARCH_LOG.md`; `REPLICATION.md` through `build.py --map`. Nothing under `results/` except `results/paper/`
(rebuilt outputs); nothing in `writing/Paper` by hand; nothing in `writing/OnlineAppendix/*.qmd` (Part B's).

What the outputs must become (`writing/Paper` numbering):
1. **Table 5, `OECD26_Slopes`** (the paper's variant only): columns `Relation | Data | Model`; the `Layer 2`
   column is dropped. Note: "Model as in figure \ref{fig:OECD26:layer1}." (or equivalent without "layers"). The online
   appendix's slope tables (`OECD26_Slopes_cses`, `_omegaUS`, `_size`, `_29`) keep both model columns, relabelled
   `Model` and `Own $\omega$`.
2. **Figure 7.2, `OECD26_Layer1`**: legend `model`; the note describes the model only: every country at the U.S.
   $\beta$ and $\varepsilon$ and at $\omega = 1.20$, the mean of the political weights that match each country's
   spending at its observed design (appendix \ref{app:oecd26:layer2}), its cost $\lambda_{n,t}$, own CSES turnout,
   Luxembourg flat. The clause on the second layer goes.
3. **Figure 7.3, `OECD26_ThetaFit`** (and `OECD26_ThetaFitIndex`, built but not input): panel titles `Model` and
   `Own $\omega$`; legend "U.S. (anchor; on the line with own ω by construction)". The note defines own ω here, where
   it first appears: the left panel is the model of figure 7.2; the right one gives each country its own political
   weight, calibrated to its spending at its observed design (appendix \ref{app:oecd26:layer2}); the U.S. lies on the
   45° line in the right panel by construction.
4. **Figure 6.2, `OECD26_Spending`**: "at the mean of the second layer's ω, 1.17" becomes "at $\omega = 1.17$, the
   mean of the political weights that reproduce each country's spending without the cost" (or equivalent).
5. **Table 10, `OECD26_Omega`**: header `Model, own $\omega$`; note "(layer 2, figure 7.2)" becomes "(own $\omega$,
   figure \ref{fig:OECD26:thetaFit})".
6. **Table 11, `OECD26_Variants`**: row labels `Model` / `Own $\omega$`; note "Model and layers as in figure 7.2"
   becomes "The model as in figure \ref{fig:OECD26:layer1}, own $\omega$ as in figure \ref{fig:OECD26:thetaFit}."
7. **Figures G.1, G.2** (`OECD26_ThetaFitPopulation`, `OECD26_ThetaFitMeasure`): panel titles `Model` / `Own $\omega$`.
8. **Online appendix exhibits** (`onlineAppendix.py`, `tablesOECD26.OMEGACAPTION`, `_layersText`, the
   `OECD26_Layer1_*`, `OECD26_Omega_*`, `OECD26_Slopes_*` exhibits): the same names; e.g. "Layer 1 of the cross-country
   test ..." becomes "The model of the cross-country test ...", "at the mean of layer 2's ω" becomes "at the mean of the
   countries' own ω", "layer 1 at the U.S. ω" becomes "the model at the U.S. ω".

Checks before reporting (quote each verdict):
- `build.py` builds everything it built before (59 built, 0 skipped); `build.py --site` and `build.py --map` run.
- No "layer" (any case) in `writing/Paper/Tables/*.tex`, `writing/Paper/Figs/*_note.tex`, the text of every
  `OECD26_*.pdf` in `writing/Paper/Figs` and `results/paper` (extract it), or `writing/OnlineAppendix/_generated/`
  except the unrelated "design layer" of the CRRA recursion (`NUM_Selection*`).
- Numbers unchanged: each regenerated `OECD26_*` tex differs from `git show HEAD:` only in labels and wording, and
  table 5's `Model` column equals the old `Layer 1` column cell by cell.
- `test_oecd26.py`, `test_onlineAppendix.py` pass (and `python\runTests.py` if a shared module changed).
- `python/paper/README.md`: one invariant line, "layer 1/2 in code and csvs = 'the model'/'own ω' in every output".
  Module log entry, at most ten lines.
Do not compile or push the paper; Part B's writer edits the prose at the same time and the main session builds last.

## Part B — prose (paper-writer)

Files: `writing/Paper/Sections/EndogenousTheta.tex` (subsection 7.3, `sec:esc:crossSection`, only),
`writing/Paper/Appendix/OECD26.tex`, `writing/OnlineAppendix/esc-oecd26.qmd`, `esc.qmd`, `index.qmd` (the lines that
name a layer). Another writer edits `Appendix/EndogenousDesign.tex` at the same time; do not touch it. Do not edit
generated files (Part A changes them).

Section 7.3:
- The paragraph "The test has two layers. ..." becomes one description of the model: the 21 synthetic countries at
  the U.S. $\beta$ and $\varepsilon$ (with the footnote on $\varepsilon$ kept), every country at $\omega = 1.20$, the mean
  of the political weights that make the model match each country's pension spending at its observed design (appendix
  \ref{app:oecd26:layer2}), so that the countries differ only in the three dimensions of figure 1.1 and their turnout.
- Figure 7.2 and table 5 paragraph: the model beside the data; "the slopes of both layers" and "The second layer keeps
  these signs and magnitudes." go; the Luxembourg footnote's "first layer" becomes "the model".
- Figure 7.3 paragraph: own ω enters here, in a sentence or two (each country's own political weight, calibrated so
  that the model matches its pension spending at its observed design, appendix G.3), then the fit of both: correlation
  0.72 and 0.77, RMSE 0.26 and 0.24, standard deviation 0.11 and 0.16 against 0.32. If the slopes with own ω are
  mentioned, one clause pointing to table \ref{table:OECD26:variants} (its starred rows) or appendix G.3, no more:
  own ω is secondary.
- "Neither spending nor the index is related to the Gini in either layer" becomes "in the model" (table 5); own ω at
  most a clause.
- No "layer" anywhere in section 7.3. The section's opening paragraph and 7.1–7.2 are not yours.

Appendix G: every "layer" goes, by the names above. G.2's "Every country takes these values of β and ε in both layers
of the test; in the first it takes the mean of the second layer's political weights" becomes one sentence on the model.
G.3 (`app:oecd26:layer2`, title may stay "Each country's political weight") opens by defining own ω; its last sentence
cites table 5 for own ω's slopes, which table 5 no longer has: point to table \ref{table:OECD26:variants} (the
starred rows of panel A) instead. G.4: "the second layer" becomes "with own ω", "the first layer" becomes "the model".
The opening paragraph's online-appendix sentence: "with every country in the model at the U.S. political weight".

Online appendix pages: the same names in `esc-oecd26.qmd` (its heading "Layer 1 at the U.S. political weight" becomes
"The model at the U.S. political weight", anchor unchanged), `esc.qmd` line 17 and `index.qmd` line 45. Keep the
pages' register (they mirror the paper's).

Checks: every number you keep is checked against `Tables/OECD26_Slopes.tex`, `OECD26_Variants.tex`,
`OECD26_Omega.tex` and the figure notes (the old `Layer 1` column is the model, `Layer 2` is own ω);
`grep -n -i layer` over your files returns nothing in the paper's files and nothing reader-facing in the pages;
`writing/checkPaper.py` passes. Do not compile the PDF or push; the main session builds last.
