# Gate 1 note: paper rewrite, session 1 (2026-09-30)

For RKB. Session 1 of `notes/paper_presentationPlan.md` §8 is done: section 7 rewritten, `writing/checkPaper.py`
built, the four agents reported. The paper was pushed to Overleaf for this read (RKB's instruction; the online copy
was checked unchanged first). Nothing is committed and nothing of the agents' is integrated: the per-file diff in
the working tree is the review object. **Record decisions in the DECISIONS block at the end of this file**, as
in the plan; session 2 reads §8 of the plan and then this file.

Files changed, all uncommitted: `writing/Paper/Sections/EndogenousTheta.tex`, `Appendix/UKvsUS.tex`,
`Appendix/PoliticoEconomicEquilibrium.tex`, `References.bib`, `Figs/OECDdata.pdf` (new, not included);
`writing/checkPaper.py`; `python/paper/build.py`, `oecdFigure1.py` (new), `README.md`, `RESEARCH_LOG.md`;
`python/US/runESCxi.py` (new), `README.md`, `RESEARCH_LOG.md`; `data/oecdFigure1.csv`, `oecdFigure1_sources.csv`;
`results/esc/escXiRobustness.csv`, `results/paper/oecdCorrelations.csv`, `results/paper/Figs/OECDdata.{pdf,png}`;
`pyenv.md`; root `RESEARCH_LOG.md`.

## 1. Section 7: what to check

- **Structure.** Four subsections: `sec:esc:corner` (7.1), `sec:esc:cost` (7.2), `sec:esc:calibration` (7.3),
  `sec:esc:results` (7.4). The "Solution" paragraph is gone; its two sentences for section 4 sit in a
  `%% TODO-B1` comment at the end of the file, for B1's brief in session 2.
- **Cross-country test** closes 7.3, after the calibration table, with `US_ESC_Country` in the main text. Its
  `\input` left appendix G.2, whose opening paragraph is now a two-sentence pointer (the one edit outside the
  session's named scope; `Appendix/UKvsUS.tex`).
- **"Within 16%"** is qualified as specific to ρ = 1 with the reversal at ρ = 2 pointed at appendix G.2. The
  conclusion still says it unqualified (session 3).
- **Voice.** No dashes, no sentence about the paper's own prose, one mechanism sentence per results paragraph.
  This draft is the exemplar later writers are pointed at.
- **Numbers.** Every number in 7.3 and 7.4 stands in a table beside it, except three placeholders: the
  baseline drift (`\todo{drift: 0.809 by 2110 ...}` and the tax 20.9%, from `results/esc/escPath.csv`, no table)
  and the ξ sentence (`\todo{xi: ...}`, A2's result). Counterfactual designs are quoted at the tables' two
  decimals (0.83, 0.77, 0.65, 0.63); the style guide asks for three. The permanent timing's switch point
  ("ρ above about 1.3", `escPermanentCRRA.csv`, no table) left the text. The mild-ageing number left (D4(d)
  not taken).
- **The `%% TODO-PROP3` marker** in 7.1 is where A1's statement (§2 below) goes after sign-off.

| Part | Words before | Words after | Plan §3 target |
|---|---|---|---|
| Opening | 325 | 205 | 150 |
| 7.1 corner | 541 | 540 | 500 |
| 7.2 cost | 1,339 | 1,164 | 900 |
| 7.3 calibration and test | | 503 | 500 |
| 7.4 results | 2,337 | 1,215 | 750 |
| Section 7 | 4,542 | 3,627 | 2,800 |

Counts are `checkPaper.py`'s, about 10% below the plan's method. The excess is mechanism prose in 7.2 and the
per-counterfactual paragraphs of 7.4; a further cut drops mechanisms, not repetition (D2: no target yet).

Checker, from the repo root (clean on the whole draft at the close of session 1):
`PYTHONUTF8=1 .venv\Scripts\python.exe writing\checkPaper.py`

## 2. A1: the corner proposition (appendix B)

The Chebyshev argument of plan §4.2 holds. New last subsection of `Appendix/PoliticoEconomicEquilibrium.tex`:
`app:PEE:corner`, `prop:esc:corner`, one new equation label `eq:PEE:corner:c2` (re-displays $c_{2,t}^i$ because
appendix A's line has no label); 1,188 → 1,822 words, additions only. Stronger than asked: it holds for every
propensity-to-vote profile that does not rise with income (equal ones included), for any tax, ω, demography,
income distribution, and whatever design current retirees expected when they saved; relative savings are
$s^i_{t-1}/s_{t-1} = y_i + \frac{1-\alpha}{\alpha}\frac{\tau^e_t(1-\theta^e_t)}{1+\beta}(y_i-1)$, slope at least
one. A closing paragraph adds (a) only $\mu_i/c^i_{2,t}$ matters, so rising propensities keep the corner if they
rise proportionally less than retirees' consumption, and (b) the extension to CRRA-GHH at every ρ (weights
$\mu_i D_i^{-1/\rho}$), which goes beyond the brief's log-GHH assumption.

Sanity check (reported, not published): 2020, ρ = 1, common X, τ = 0.1443, equal μ: dW/dθ_t = −0.0671, −0.0735,
−0.0804, −0.0875, −0.0962 at θ_t = 0, 0.25, 0.5, 0.738, 1; negative on a 201-point grid at every date 1990–2170
(largest −0.0635); with the calibrated μ = (0.474, 0.629, 0.765) from −0.0398 to −0.0661; the direct formula
matches `ModelESC.sequentialFOC` to 1e-17. The calibrated weights meet the weaker condition at ρ = 1 (μ ratios
1.33, 1.61 against consumption ratios 1.63, 3.16 at θ = 0); at ρ = 2 it may fail (needs the μ ratio below the
square root of the consumption ratio, about 1.28), which is consistent with the numerical sign still being
negative there.

Statement for `%% TODO-PROP3`, A1's five lines (drop "and the intertemporal elasticity" if the CRRA paragraph
is cut):

> We prove this in proposition \ref{prop:esc:corner} (appendix \ref{app:PEE:corner}) for any propensities to
> vote that do not rise with income, equal ones included: the derivative is negative at every design and the
> design chosen with the tax is $\theta_t = 0$, whatever the tax rate, the political weight of the old, the
> demography, the income distribution and the intertemporal elasticity, and whatever design current retirees
> expected when they saved. Only propensities to vote that rise with income can overturn the corner. They do
> in the calibrations of section \ref{sec:oecd}, so there the sign is a quantitative matter.

Open: (i) keep the CRRA paragraph or not; (ii) the proof uses amsthm's `proof` environment while the appendix's
other proofs are prose under `\smalltitle`; (iii) the technical note's "Sequential" paragraph
(`writing/US/model_esc.tex`, around line 87) still says the sign can only be shown numerically and should
carry or cite the proposition (session 5's push).

## 3. A2: ξ robustness (`results/esc/escXiRobustness.csv`)

Self-check at ξ = 0.3 reproduced λ, θ*, β, ω, Ṽ, f(θ*), f(0), the path and the acute rows exactly (gap 0);
headline csvs byte-identical. θ* = 0.7382263650 and Ṽ = 0.4357 at every ξ (asserted). Wall time 7 min 36 s.
Driver `python/US/runESCxi.py`; rows keyed on `xi` and `kind` (calibration, path, acute pinned, acute chosen).

| ξ | λ | f(θ*, τ₂₀₂₀) | f(0, τ₂₀₂₀) | Design 2050 / 2080 / 2110 | Tax 2020 / 2050 / 2080 / 2110 | Acute ageing pinned τ | Acute chosen θ, τ | (β, ω, X) |
|---|---|---|---|---|---|---|---|---|
| 0.2 | 8.736 | 0.9814 | 0.7599 | 0.798 / 0.805 / 0.809 | 14.43 / 19.73 / 21.20 / 21.20 % | 22.94% | 0.8254, 23.24% | 0.662, 1.319, 16.00 |
| 0.3 | 8.643 | 0.9816 | 0.7621 | 0.797 / 0.804 / 0.809 | 14.43 / 19.48 / 20.87 / 20.88 % | 22.51% | 0.8254, 22.80% | 0.759, 1.508, 4.01 |
| 0.4 | 8.547 | 0.9818 | 0.7644 | 0.796 / 0.804 / 0.809 | 14.43 / 19.24 / 20.56 / 20.57 % | 22.11% | 0.8255, 22.39% | 0.866, 1.721, 1.89 |

Reading: once λ is recalibrated the chosen design and its drift are invariant to the Frisch elasticity to the
third decimal; only the tax level moves. One sign change in each λ scan, no corner. The interest-factor drift
of the chosen path (2.0 / 2.9 / 3.7e-3) exceeds the 1e-3 tolerance as the published ξ = 0.3 run already does.
Where it goes: a footnote to 7.4, or a small "chosen design along the baseline path" table (builder addition
in `python/paper`) that would also give the drift numbers of §1 their table.

## 4. A3: references (`writing/Paper/References.bib`, appended after `pwt`)

All seven verified (Crossref, IDEAS/RePEc, publisher pages, Library of Congress data); Biber's validator passes
the new entries; nothing cited. Keys: `Tabellini00a1`, `GalassoP02a1`, `GalassoP04a1`, `CremerDMP07a1`,
`BethencourtG08a1`, `HolzmannP06a1` (`@collection`), `Levy08a1`.

- **Tabellini (2000)**, SJE 102(3), 523–545. Contributions are wage-linked but benefits are not, so pensions
  redistribute within cohorts and are backed by the old and the poorest taxpayers; size rises with the old-age
  share and with within-cohort inequality. Qualifier for 7.1: with no commitment the poor young back the
  transfer out of weak altruism toward their parents, not for their own pension.
- **Galasso and Profeta (2002)**, EJPE 18(1), 1–29. Survey; its §4 leaves open why some systems are Beveridgean
  and others Bismarckian and why Bismarckian ones are larger, faulting one-dimensional models. The gap our
  design result fills.
- **Galasso and Profeta (2004)**, Economic Policy 19(38), 64–115. **Mismatch with the plan:** voters choose only
  the contribution rate; the design is never voted on, so "the political sustainability of designs" overstates
  it. Ageing raises the contribution rate in six countries; their §5.2 argues in words that the UK and U.S.
  systems turn more Bismarckian as high earners desert the flat benefit (following Conde-Ruiz and Profeta),
  which is the drift section 7 quantifies.
- **Cremer, De Donder, Maldonado and Pestieau (2007)**, JPubE 91(10), 2041–2061, "... when some individuals
  are myopic". **Mismatch:** the result rests on myopia. A flat system is chosen when voters are all
  far-sighted or all myopic; a less redistributive one needs a mix. Parallels the 7.1 corner, with myopia in
  the role of our income-rising voting weights.
- **Bethencourt and Galasso (2008)**, JPubE 92(3–4), 609–632. Public health care narrows the longevity gap and
  raises the poor's support for pensions; cite where the U.S. calibration adds Medicare.
- **Holzmann and Palmer (2006)**, World Bank. NDC reformers: Sweden (1994), Italy (1995), Latvia (1995), Poland
  (1998). **§4.4 mismatch:** Germany is not NDC; ch. 22 (Börsch-Supan and Wilke) says the point system was
  earnings-proportional from the start and the 1992–2004 reforms made it an "NDC look-alike". Proposed
  wording: "... and Germany's reforms of 1992–2004 made its point system an NDC look-alike"; ch. 22 can be
  added as `@incollection` if cited.
- **Levy (2008)**, Brookings. Wage-financed social security valued below its cost taxes formal jobs while
  non-contributory programmes subsidise informal ones. For section 5: a weak link between contributions and
  benefits is a tax on formality.

## 5. A4: figure 1 (`python/paper/oecdFigure1.py`, `data/oecdFigure1.csv`)

Files: `data/oecdFigure1.csv` (29 × 30, both concept sets plus the EPS marker readings) with every column
sourced in `data/oecdFigure1_sources.csv` (retrieved 2026-09-30); `results/paper/Figs/OECDdata.pdf` (2×3,
5.91 × 3.9 in: the four current panels, spending vs index top right, legend bottom right; U.S., UK, France
highlighted; `PLOT = NAMED` by default, `AS_EPS` a one-line switch), registered as `OECDdata` in `build.py`
(55 outputs); `results/paper/oecdCorrelations.csv`. The EPS and the `\includegraphics` line are untouched.

Findings:
1. All 29 countries appear in every panel; the "about 20 markers" is overlap (AUT/FRA coincide in all four).
2. The EPS reproduces point by point only under other concepts than the footnote names: spending is SOCX cash
   **plus in kind** (cash-only is up to 2.57 p.p. lower: NOR, SWE, DNK, FIN); population growth is **World
   Bank**, not OECD (France 1.192 vs 1.160, the OECD series adding the overseas departments); the index is the
   **mean of men and women**, not men (POL 0.85 vs 0.96, MEX 0.74 vs 0.76, AUS 0.49 vs 0.50).
3. The plotted Ginis are **not from WIID** (no WIID observation of any year or concept within 0.005 of the
   U.S. 0.5905 or MEX 0.7189). They track the World Inequality Database pre-tax Gini (r = 0.96), a database
   that does not archive vintages, so they cannot be reproduced exactly. Section 6's footnote that the U.S.
   has the highest Gini is wrong on the figure's own data: MEX 0.719 and TUR 0.592 are above the U.S. 0.591;
   with WIID disposable the U.S. is 0.419, again third, and France 0.321 is at the median.
4. Stop condition: the OECD Data Explorer now serves 2024 replacement rates only; the script reads the
   Pensions at a Glance 2021 StatLink table (https://stat.link/b2f0ws), the same series.
5. Years: all 2020 except the WIID market Gini (JPN 2018; CHE, DEU, DNK, FRA, TUR 2019; ISL missing);
   nothing interpolated. Old repo `SSD`: no figure data; its docx has a typo (U.S. half-mean RR 49.2 for 49.6).
6. France's LIS survey year is **2018** (`FRMain.xlsx` Readme; section 6 implies 2019). Closes W7(a).
7. Correlations, n = 29, Pearson / Spearman, sourced concepts: spending–growth −0.58 / −0.62; spending–index
   0.63 / 0.61; spending–Gini −0.08 / 0.00; index–growth −0.39 / −0.30; index–Gini 0.18 / 0.23; growth–Gini
   0.43 / 0.34. Under the EPS concepts: −0.62, 0.62, −0.29, −0.39, −0.05, 0.38. Same reading.
8. The panel's index is the raw replacement-rate ratio, not the calibrated θ (U.S. 0.79 in the figure against
   0.738 in the model).

Proposed footnote (sourced concepts, ready to paste; if the EPS concepts are kept: "public expenditure on old
age and survivors, cash and in kind", World Bank WDI population, "averaged over men and women", and the Gini
sentence waits for a fixed WID vintage):

> \footnote{The countries are Australia, Austria, Belgium, Canada, Czech Republic, Denmark, Finland, France,
> Germany, Greece, Hungary, Iceland, Ireland, Italy, Japan, Korea, Luxembourg, Mexico, Netherlands, New Zealand,
> Norway, Poland, Portugal, Spain, Sweden, Switzerland, Turkey, United Kingdom and United States; all 29 appear
> in every panel. Pension spending is public cash expenditure on old-age and survivors' pensions in percent of
> GDP (OECD Social Expenditure Database). Population growth is the ratio of the population in 2020 to that in
> 1990 (OECD historical population data), with no correction for differences in retirement age, see section
> \ref{sec:oecd}. The Bismarckian-Beveridgean index is the ratio of the gross replacement rates of mandatory
> schemes at average and at half average earnings for a man with a full career under the 2020 rules (OECD,
> \emph{Pensions at a Glance 2021}, table 4.1), see section \ref{sec:oecd}. The Gini coefficient is that of
> disposable income per capita (equivalised for New Zealand and Turkey), the observation the World Income
> Inequality Database (UNU-WIDER, version of 8 September 2026) selects for its companion series. All data are
> for 2020. Across the 29 countries pension spending correlates $-0.58$ with population growth, $0.63$ with the
> index and $-0.08$ with the Gini; the index correlates $-0.39$ with population growth and $0.18$ with the
> Gini.}

## 6. Housekeeping before session 2

- The `paper-*` agent types load only when Claude Code starts (not on `/clear`); session 1 ran the agents as
  general-purpose on the Opus alias with each type's rules in the brief. **Restart Claude Code before session
  2**, from `C:\Users\sxj477\Documents\GitHub\SSDclaude` (capitalised as git spells it): worktree isolation was
  refused because the session's lower-case path spelling differed from git's. The four stale worktrees and
  branches are removed. Both facts are in the session memory.
- `pyenv.md` and `python/paper/README.md` updated for the second network script and the 55th output.
- Session 2 (plan §8): four writers on sections 4, 6, 5 and 2–3, briefs per the §8 table; B2 also corrects
  section 6's Gini footnote per §5.3 above (G1.5), and B1 and B4 both quote the hand-over sentences (the
  `%% TODO-B1` comment at the end of section 7, section 2's horizon sentence, section 3's closing paragraph).
  Overleaf edits made during the gate 1 read come back through `pull paper` at the start of session 2.
- **Session 2 follow-ups for the main session**, from the decisions below, in `Sections/EndogenousTheta.tex`,
  `Appendix/PoliticoEconomicEquilibrium.tex`, the figure block of `Sections/Introduction.tex`, and
  `python/paper/tablesUS.py` with the tables it regenerates; the checker after each step, each step committed
  once it is clean; the agents' files untouched:
  1. G1.2: A1's five-line statement (§2) at the `%% TODO-PROP3` marker, marker dropped; the appendix B proof
     rewritten as prose under a run-in heading like the appendix's other proofs; the CRRA paragraph kept.
  2. G1.3: `\todo{xi: ...}` becomes a footnote to 7.4 with the §3 result (λ within one percent, the design in
     2110 and under acute ageing unchanged to the third decimal at ξ = 0.2 and 0.4); the two `\todo{drift: ...}`
     are resolved per RKB's choice under G1.3.
  3. G1.6: `tablesUS.py` prints θ to three decimals in `US_ESC_{Ageing,IncomeDistr,Voting,FrenchAll}` and the
     `UK_ESC_*` twins, rebuilt with `build.py --only`; 7.4's design numbers re-cut to three decimals against
     the rebuilt tables; appendices F.3 and G.2 still quote two decimals, noted for D2 (session 4).
  4. G1.5: `\includegraphics` of figure 1 pointed at `Figs/OECDdata.pdf` and its footnote replaced by the §5
     proposal; the rest of the introduction is session 3's.
  5. G1.4: the seven references stay uncited until session 3.
- **Merge rule from session 2 on.** RKB reviews on Overleaf, so after the main session's first-line review of
  the four diffs (style guide §7, cross-references, numbers against tables, the B1/B4 hand-over intact) it
  merges the worktree branches into `paper-rewrite` (disjoint files) and pushes; gate changes come back as
  edits. This replaces §8's "sign-off merges".

## DECISIONS (RKB)

Fill in below; a blank line means "as recommended".

- **G1.1 Section 7.** Structure, placement of the cross-country test, voice, numbers: accepted / changes
  wanted (which paragraphs). Length: stop at 3,627, or cut toward 2,800 (7.2 literature paragraph, 7.4
  mechanisms).
  RKB: Accept as recommended.
- **G1.2 Proposition.** Accept as written; keep the CRRA paragraph (recommended: yes); proof environment or
  prose under a run-in heading (recommended: prose, to match); the technical note carries it at session 5's
  push (recommended: yes).
  RKB: Accept as recommended.
- **G1.3 ξ result.** Footnote to 7.4, or a "chosen design along the baseline path" table with ξ rows that
  also houses the drift numbers (recommended: the table; a builder in `python/paper`).
  RKB: Footnote to 7.4. 
  The drift numbers (0.809 by 2110, tax 20.9%; no table): in the same footnote, or dropped with the drift
  sentence kept qualitative? 
  RKB: Dropped with the drift sentence kept qualitative.
- **G1.4 References.** Galasso–Profeta 2004 cited for the ageing result and the drift argument, not for
  "designs"; Cremer et al. cited with the myopia condition named; Germany sentence in A3's wording and ch. 22
  added if cited (recommended: yes to all three).
  RKB: Don't cite them here, keep them in the report.
- **G1.5 Figure 1.** Concept set: the footnote's sources (recommended) or the EPS's; the Gini series (WIID
  disposable, recommended, or a WID-like pre-tax series with the footnote saying so); replace the EPS with the
  PDF (recommended: yes) and keep the 2×3 layout with the spending–index panel (recommended: yes); the
  footnote as proposed; section 6's Gini footnote corrected (session 2, B2) and France's LIS year set to 2018
  (session 4).
  RKB: Accept as recommended.
- **G1.6 θ decimals.** The ESC counterfactual tables print three decimals (builder change in `tablesUS.py`,
  then the prose is re-cut to three) or stay at two (recommended: three).
  RKB: Accept as recommended.
- **G1.7 Permanent-timing switch point.** Stays out, or comes back with a one-line table from
  `escPermanentCRRA.csv` (recommended: stays out).
  RKB: Accept as recommended.
- **G1.8 `Appendix/UKvsUS.tex`.** The pointer paragraph in place of the country-table paragraph: accepted.
  RKB: Accept as recommended.