# Brief: the paper pipeline for the cost variants (phase D)

For the `paper-compute` agent, in the builder role. Plan: `notes/plan_endogenousDesign.md` §C (C.1
decisions 4-7, C.4 gate 2, C.5 schema). Read `python/paper/README.md` in full, the top entries of
`python/paper/RESEARCH_LOG.md` and `python/US/RESEARCH_LOG.md` (phases B and C), `notes/paper_styleGuide.md`
§5 (tables, notes, labels, `\oa{key}`), and the builders you extend: `python/paper/tablesUS.py` (the ESC
block from `ESCANCHOR` on: `_escTable`, `escSummary`, `escResults`, `escCalibrationTable`,
`escCountryTable`, `escScaleWedge`), `figuresOA.escPathPaper`, `datasets.py`'s ESC readers, `build.py`'s
registry and `ONLINE_ONLY`, `onlineAppendix.py`'s `SECTIONS` (the `esc-*` groups) and
`writing/OnlineAppendix/esc.qmd`. You write under `python/paper/`, `results/paper/` (through `build.py`),
`writing/OnlineAppendix/esc.qmd` and `writing/Paper/onlineAppendix.tex` (through `build.py --site`); you do
not hand-edit anything else under `writing/`.

## 1. What the paper needs

Section 7 is being rewritten around three cost specifications at $\rho = 1$ (the plan's C.1.1): the
quadratic cost `'size'` (the current paper's), the linear `'sizeL'` and the linear-quadratic `'sizeLQ'`
(preferred). The general form is $\ln f = -\tau(1-\theta)[\lambda_1 M + \tfrac12\lambda_2\tilde V(1-\theta)]$
with $M = \sum_i\gamma_i|y_i-1|$ the amount the flat component carries and $\tilde V$ the Harberger
dispersion (the plan's C.1.1 as amended at gate 1); the csvs store $\lambda$ in `p` and, for `'sizeLQ'`,
$\kappa$ in `kappa`, with $\lambda_1 = \lambda\kappa$, $\lambda_2 = \lambda$; under `'sizeL'` $\lambda_1 = \lambda$,
$\lambda_2 = 0$; under `'size'` $\lambda_1 = 0$, $\lambda_2 = \lambda$. Every readout row carries `Vtilde` and
`Mabs`. The paper prints $\lambda_1$ and $\lambda_2$ (and names $\kappa$ only where the joint calibration is
described). A fourth spec `'sizeLQV'` ($\tilde V$ on both terms) exists for the record: it is not a paper
variant and no builder prints it except one row of `US_ESC_VariantsCountry`'s note or last block (France's
design under it). `results/esc/*.csv` carry the rows after phase C; the schema is the plan's C.5. The
$\rho \neq 1$ rows exist for `'size'` only and stay as they are.

### Config (`python/paper/config.py`, `US['esc']`)

- `'spec'` stays `'size'`: it drives every $\rho$-dependent exhibit (the exact CRRA rows exist for it alone).
- New `'paperSpec': 'sizeLQ'` and `'variants': [('sizeLQ', 'linear-quadratic'), ('sizeL', 'linear'),
  ('size', 'quadratic')]` in the paper's order, with a comment saying which builders read which and that
  the split ends when the CRRA leg is run for the preferred spec (TODO R6).
- A helper `escParams(rec, spec)` (in `datasets.py` or `config.py`) returning `{'λ1', 'λ2', 'κ'}` from a
  calibration or country row.

### Builders (labels fixed here; the writers cite them)

| output | kind | label | where | what |
|---|---|---|---|---|
| `US_ESC_Variants` | table | `table:US_ESC:variants` | section 7 | one row per variant, paper order: $\lambda_1$, $\lambda_2$, $f(\theta^{\ast})$, $f(0)$ (U.S., 2020), the design the UK and France choose under the U.S. parameters, the UK's own $\lambda$ and France's own (the threshold, printed as $\geq$ with a note; `--` where there is none). Note: which design(s) pin the parameters per variant (one for `'size'` and `'sizeL'`, the U.S. and the UK for `'sizeLQ'` with $\kappa$ = its value, France the prediction; or the fallback if `kappaFrom = 'FR'`), $\tilde V$ and the tax rates by reference to `table:US:Calib`/section 6, the UK at its own cuts. Row keys `size|sizeL|sizeLQ`. |
| `US_ESC_Results` | table | `table:US_ESC:results` (kept) | section 7 | `RESULTSROWS` (baseline, acute, frIncome, frVoting) by variant: one three-column block per variant in paper order ($\theta$ chosen, tax pinned, tax chosen), `escSummary`'s layout with variants in place of $\rho$. Note as now, naming the preferred variant's parameters and pointing at `table:US_ESC:variants` and `\oa{esc-variants}`; row keys unchanged. |
| `US_ESC_Path` | figure | `fig:US_ESC:path` (kept) | section 7 | `escPathPaper` with the three variants' chosen paths in the design and tax panels (preferred solid with markers, the other two thinner dashed/dotted in the secondary colours of `figures`), pinned at $\theta^{\ast}$ as now, the $\nu$ panel unchanged; the legend names the variants. Marks for the preferred variant as now; the others' marks may be omitted if `_save`'s one-artist rule makes them awkward. |
| `US_ESC_VariantsCountry` | table | `table:US_ESC:variantsCountry` | appendix G.1 | per variant (block) × economy (UK, France, UK at U.S. cuts): observed $\theta^{\ast}$, tax rate, $\tilde V$, $M$, chosen under the U.S. parameters, own value and kind; a last block for the alternative pinning of `'sizeLQ'` on the U.S. and France (`escCalibration_kappaFR.csv`, `escCountry_kappaFR.csv`: its $\lambda_1$, $\lambda_2$, the UK's and France's designs) when the files exist, else that block is omitted and the note says so; France's design under `'sizeLQV'` in the note. |
| `US_ESC_VariantsShocks` | table | `table:US_ESC:variantsShocks` | appendix G.2 | per variant (block) × scenario (baseline, mild, acute, frIncome, frVoting, frBoth, frAll, France): $\theta$ chosen, tax pinned/chosen, savings rate pinned/chosen (level on the baseline rows, change in p.p. of GDP on the others, as `_escTable`), workweek pinned/chosen. `\footnotesize`, `\textwidth`. |
| `UK_ESC_VariantsShocks` | table | `table:UK_ESC:variantsShocks` | online (`ONLINE_ONLY`) | the same on the UK as host from `escExperimentsUK.csv` (`frIncome`, `frVoting`, `frBoth`, `frAll`, baseline, France), per variant with a converged UK own parameter. |

`US_ESC_Calibration` and `US_ESC_Summary` (the quadratic cost across $\rho$) will be input by appendix G.3:
make their notes self-contained for the paper (no `\ref` to a figure that is online-only; `US_ESC_Summary`'s
note cites `fig:US_ESC:overview`, which must become `\oa{esc-us}`), and let `_costSentence` say "the
quadratic cost". `US_ESC_Country` and `US_ESC_ScaleWedge` stay as they are (online).

### Registry, online appendix, map

- `build.py`: register the new outputs (`UK_ESC_VariantsShocks` in `ONLINE_ONLY`), then
  `build.py --only <each>` and `build.py --list`; `build.py --map` at the end (then `git checkout` the
  figure PDFs that differ by their timestamp alone, README trap).
- `onlineAppendix.py`: a new group `('esc-variants', 'esc', [...])` after `esc-calibration` holding
  `US_ESC_Variants`, `US_ESC_VariantsCountry`, `US_ESC_VariantsShocks`, `UK_ESC_VariantsShocks`, each with a
  `text` in the registry's register (one or two sentences reading the exhibit; numbers only where they
  carry the reading); `esc.qmd` gets the matching section `## OA.4.x The cost specifications {#esc-variants}`
  (renumber the later ones); `build.py --site` so `writing/Paper/onlineAppendix.tex` defines
  `\oa{esc-variants}`; `test_onlineAppendix.py` passes. Do not render or publish the site.
- `figuresUS.robustnessMap`: if its row registry takes a new row as data (a host/spec/row-label entry
  reading `escExperiments.csv`), add the two variants at $\rho = 1$ to the chosen-design panels as a
  "cost specification" row group; if it needs more than that, leave it and say so.
- `REPLICATION.md`: the hand-written parts need no change if the map regenerates; check the count line.

## 2. Checks

- `build.py --only` for every registered ESC output succeeds; the `%% Source:` banners name the csvs read.
- The `'size'` cells of every rebuilt table are unchanged against `git show HEAD:` (diff the `.tex`;
  the only differences are the rows and notes this brief changes).
- `python\paper\test_onlineAppendix.py` and the fast suites of `python\runTests.py` that touch `paper/`.
- `python\paper\build.py --list` reports every output buildable.
- `PYTHONUTF8=1 .venv\Scripts\python.exe writing\checkPaper.py` still passes (the paper has not been
  rewritten yet, so nothing inputs the new tables; a dangling label would show here).

## 3. Report (at most 25 lines)

The outputs built with their labels and the csv rows they read; the config keys added; what the
robustness map got; the `'size'`-cell diff; the test lines; the README and paper-log entries you wrote; what
you could not do and why. Nothing under `writing/Paper/Sections` or `Appendix` is yours.
