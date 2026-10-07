# Brief: section 7 and appendix C, refocused (2026-10-07)

For one paper-writer agent. The decisions are RKB's of 2026-10-07; the pipeline side (the new exhibits) is done
and built. When the work closes this brief moves to `archive/notes/`.

## 0. Files you may change

- `writing/Paper/Sections/EndogenousTheta.tex` (section 7, `sec:esc`): the main task, a rewrite.
- `writing/Paper/Appendix/EndogenousDesign.tex` (appendix C, `app:esc`): notation and vocabulary throughout,
  and what moves in from section 7 (§7 below).
- `writing/Paper/Appendix/Robustness.tex`: the figure note cites `table:US_ESC:summary`; see §6.
- `writing/Paper/Sections/Introduction.tex`, `writing/Paper/Sections/Conclusion.tex`: only the sentences
  listed in §6. `abstract.tex` is read, not changed.

Nothing else. Exemplar for voice: `Sections/OECD.tex` (section 6, as RKB settled it); the current section 7 is
the register of the section's own vocabulary but not a model of length.

## 1. What changes, and why

RKB's three comments on the section as it stands:

1. Section 7 and appendix C use notation and vocabulary of their own; they must use the paper's (§2).
2. The section is not focused. The text and its exhibits present the benchmark $\rho = 1$ only, the
   counterfactuals reduce to ageing and inequality read against figure 1, voting patterns get one sentence, the
   calibration and the cross-country test become one paragraph with one small table, and the other elasticities
   get one short closing paragraph, as sections 5 and 6 have.
3. The cost is explained as a leaky bucket, in words, with the derivation from the implicit tax demoted to
   appendix C. The specification and every number stay as they are.

Target: section 7 at 1,500 to 1,700 words (now 2,960). Appendix C may take about 150 words from the section and
must stay under 3,500 (now 3,290).

## 2. Notation and vocabulary, both files

RKB: the two files use the style of the rest of the paper, not a style of their own, and the style guide is not
changed.

- **Derivatives** as $\partial f/\partial x$: `\frac{\partial \mathcal{W}_t}{\partial \theta_t}` (or `\dfrac`)
  in display, `\partial f/\partial \theta_t` or `\frac{\partial f}{\partial \theta_t}` inline, whichever reads
  better. Never the subscript forms `\partial_{\theta}`, `\partial_{\tau}`, `f_{\theta}` (nine occurrences in
  appendix C, three in section 7). A total derivative that includes the policy response keeps
  `\frac{d \ln \Theta_{h,t}}{d \theta_{t+1}}`, as `eq:esc:leadFOC` has it.
- **The design.** $\theta_t$ is the design that applies to the benefits paid at $t$, chosen at $t-1$. Call it
  "the inherited design" where the contrast with the choice matters, and otherwise write the symbol with its
  date ("$\theta_{2020}$", "the design in 2020", "the design chosen for 2050"). $\theta_{t+1}$ is "the design
  chosen at $t$". Never "the design in force" (six occurrences across the two files and the old figure note).
  The two readings of a counterfactual are "pinned" and "chosen", or "exogenous $\theta$" and "endogenous
  $\theta$" (style guide §4).
- **The cost.** "The deadweight cost of redistribution" at first mention and in the subsection title, then
  "the cost"; "the share of revenue lost" for $1-f$; "wedge" only for $t_i$ inside appendix C.2; never
  "friction".
- **The $\theta$ dimension** is "more Bismarckian", "more earnings-related", "flat". Never "contributive"
  (section 7's ageing paragraph and appendix C's one-period-ahead paragraph both have "a more contributive
  system"); contributive is the $\epsilon$ dimension.
- **The design function.** Drop the symbol $\Theta_{t_0-1}(\cdot)$ of `eq:esc:calibration`: it clashes with
  the labor-supply coefficient $\Theta_{h,t}$. State the calibration condition in words, or as
  $\theta_{2020} = \theta^{\ast}$ with the sentence saying that $\theta_{2020}$ is the design chosen in 1990 on
  the equilibrium path. The label `eq:esc:calibration` may go if nothing cites it.
- Everything else per `notes/paper_styleGuide.md`.

## 3. Section 7: structure, contents, length

Keep the labels `sec:esc`, `sec:esc:cost`, `sec:esc:calibration`, `sec:esc:results`, `eq:esc:budget`.

**Lead** (one paragraph, about 90 words). As now: $\theta$ calibrated so far while the tax is chosen; this
section lets the electorate choose the design with the same objective, in the model without informal
households, so one process delivers size and shape; derivations in appendix C, algorithms in the technical
documentation. Drop "The section presents the results under different model specifications".

**7.1 The deadweight cost of redistribution** (`sec:esc:cost`; three paragraphs, about 520 words).

- P1, the corner (about 110 words, the current paragraph tightened): without a cost the choice is a corner;
  the flat component is a pure transfer within the retired cohort and an electorate that weighs retirees by
  marginal utility wants all of it; proposition `prop:esc:corner` (appendix `app:esc:corner`); propensities to
  vote that rise with income could overturn it, and at the U.S. calibration do not, whichever of the three
  timings is used. An interior design requires flat benefits to be costlier than earnings-related ones.
- P2, the cost: §5 verbatim, with `eq:esc:budget` as now.
- P3, what the cost stands for and what it changes (about 180 words). The model contains the hours response to
  the flat component, the common marginal wedge, through the Frisch elasticity; the cost stands for what the
  model does not contain, the participation, formality and reporting margins on which the evidence finds the
  unlinked part of contributions to matter (\textcite{Summers89a1}, \textcite{Disney04a1},
  \textcite{KumlerVF20a1}), and the administrative and political costs of redistribution. $\lambda$ is
  calibrated rather than derived, is larger than labor-supply elasticities alone would give (appendix
  `app:esc:cost`), and its discipline is the cross-country test of section 7.2. Then what it changes: the
  solution of sections 2 to 4 is intact (the substitution of $A = f\theta$ and $B = f(1-\theta)$, appendix
  `app:esc:equilibrium`); the cost is proportional and cancels from the replacement-rate ratio, so
  $\theta^{\ast} = 0.738$ is unchanged; the tax condition gains one factor, a larger system is worth less to a
  retiree at the margin than the revenue it collects; and an interior choice becomes possible because a more
  Bismarckian design also raises the total the young will receive. Timing in two sentences: the design is chosen
  one period in advance, the Markov timing in which it moves labor supply and savings before it binds and the
  way benefit formulas are legislated; under log preferences the choice depends on neither the inherited design
  nor savings (proposition `prop:esc:separability`), so each date's choice is a one-dimensional search. The
  present footnote on the alternative specifications (a cost on the flat component only; a cost on the design,
  `\oa{esc-scale}`) moves to appendix C.2 (§7).

**7.2 Calibration and a cross-country test** (`sec:esc:calibration`; one paragraph of about 230 words, then
`\input{Tables/US_ESC_Country}`).

$\lambda$ is identified separately from the design by requiring that the design chosen for 2020 on the
equilibrium path, with the choice binding from the first period, is the observed one, with $(\beta,\omega)$
recalibrated at every trial value; the calibration pins 2020 only, every later design is a prediction. At
$\rho = 1$, $\lambda = 8.643$; the observed design loses 1.8% of revenue at the 2020 size of the system and a flat
system of the same size would lose 24% (the full calibration across $\rho$ is in `\oa{esc-calibration}`). The
test: one datum calibrates the cost, so the UK and France test the specification, not its fit. Under the U.S.
parameter the UK (observed 0.560, tax 11.9%) chooses 0.625 and France (observed 1.000, tax 21.3%) chooses 0.749,
the U.S. re-electing 0.738 by construction. Say it plainly: the ordering is the observed one, but France's chosen
design is only 0.011 above the U.S. one, so the weight of the test is the UK, whose own cost, $\lambda = 7.264$,
is within 16% of the U.S. value, and whose regrouping at the U.S. income percentiles (observed design re-read as
0.543, $\tilde V$ 0.065) moves the choice only to 0.644. What separates the UK from France is the size of the
system, at nearly the same dispersion of relative incomes (0.223 and 0.218, about half the U.S. 0.436), the
relation of figure 1. France's corner is out of reach under a quadratic cost, where the first unit of
redistribution is free at the margin; keep the footnote on the linear term as future work.

**7.3 Ageing and inequality** (`sec:esc:results`; about 600 words: lead, the figure, the table, three run-in
paragraphs, a close).

- Lead (about 150 words). The counterfactuals of section 6 with the design chosen: each a separate equilibrium
  path read in 2020, read twice, pinned at the U.S. value and chosen, both under the cost, so the distance is
  the political response. Then the baseline path, figure `fig:US_ESC:path`: the calibration pins 2020 only;
  along the projected demographic path the chosen design rises from 0.738 in 2020 to 0.797 in 2050 and 0.809
  from 2110, tracking the fall in workers per retiree from 1.34 to 1.07 and flattening when it flattens, while the
  tax rate rises from 14.4% to 20.9% and lies 0.2 p.p. above the path with the design pinned, since a more
  Bismarckian system dissipates less and is worth more to the electorate at the margin. Keep the Frisch footnote
  ($\xi = 0.2$ and $0.4$: $\lambda$ within about one percent, the 2110 design unchanged to the third decimal, the
  acute-ageing design within one unit, the 2110 tax about 0.3 p.p. either way) here, and the pointer to
  `\oa{esc-path}` for the full path from 1960 and the other elasticities. The pre-2020 path is not discussed.
- The figure environment, written by you per the style guide (caption above, `[!htb]`, `\par` after the
  graphic, `threeparttable` note in `\footnotesize`): `Figs/US_ESC_Path.pdf`, `\label{fig:US_ESC:path}`,
  caption of the kind "The design and the tax along the baseline path". Note: three panels at $\rho = 1$ from
  2020 on, workers per retiree, the design chosen against $\theta^{\ast}$ pinned, the tax rate with the design
  chosen and pinned; the values and the path from the first period are in the `\oa{esc-path}`.
- `\input{Tables/US_ESC_Results}`.
- `\smalltitle{Ageing.}` (about 150 words). Acute ageing, $\nu_t = 1$ throughout, raises the chosen design from
  0.738 to 0.825. Two mechanisms: a scarcer young generation raises the political weight of retirees, who are
  unanimous for a more earnings-related system since it raises the labor supply on which their benefits are
  levied (appendix `app:esc:corner`); and the tax that ageing calls for makes the flat component costlier at the
  margin, since the loss is proportional to $\tau_t$: the tax rises from 14.4% to 22.8%, so the loss per unit
  of redistribution rises by more than half. This second channel supplies about half the response: under a cost
  without the size scaling the design rises only to 0.778 (`\oa{esc-scale}`). The tax and savings responses are
  those of the pinned reading: the chosen design adds 0.3 p.p. to a pinned tax response of 8.1 p.p., which is a
  little below section 6's 8.7 p.p. because with the cost a larger system is worth less to retirees at the
  margin.
- `\smalltitle{Income distribution.}` (about 150 words). The model's inequality is the dispersion of relative
  labor income across the three groups, $\tilde V$, not the Gini of figure 1. Pinned, France's flatter
  distribution lowers the tax from 14.4% to 13.8%, less than section 6's 1.2 p.p., because a compressed
  distribution also lowers $\tilde V$ and the share of revenue the flat component loses. Chosen, the design moves
  to 0.772, interior and close to the observed one: the cost is proportional to the same dispersion as the
  redistribution a flat benefit performs, so compressing the distribution lowers the redistributive stakes and
  the cost of carrying them together, and the young's forward-looking stake in earnings-related benefits, which
  does not scale with the dispersion, gains a little ground. The design response leaves the tax where the
  pinned reading puts it.
- `\smalltitle{Voting patterns.}` (one or two sentences, about 60 words). France's much flatter voting
  profile moves the design the other way, to 0.653, by as much as ageing: when the poor carry more voting
  weight the redistributive force of proposition `prop:esc:corner` regains ground against the forward-looking
  stake. The tax is 15.3% in both readings. With France's income distribution and voting patterns together the
  voting patterns prevail, 0.627, and on the UK as host the same (`\oa{esc-us}`, `\oa{esc-uk}`).
- Close (about 100 words). The two forces that figure 1 motivates come out as the data do: ageing moves the
  chosen design a long way toward earnings-related benefits and the size of the system with it; inequality
  moves the design little; the pattern of the cross-section, where spending and the Bismarckian index rise
  together as population growth falls and neither follows the Gini coefficient.

**`\smalltitle{The effect of the intertemporal elasticity of substitution.}`** (one paragraph, about 140
words, no exhibit). The calibrated cost falls from $\lambda = 18.267$ at $\rho = 0.5$ to $1.724$ at $\rho = 2$, a
factor of about ten, because a higher elasticity strengthens the forward-looking channels, so less cost holds the
choice away from the Beveridgean corner; at $\rho = 2$ the cost is closest to what estimated elasticities imply
(appendix `app:esc:cost`), which adds to the case of section 5 for $\rho \in [1, 2]$. The ageing response is
stable across elasticities (0.816 and 0.826 at $\rho = 0.5$ and $2$). At $\rho = 2$ the observed design loses
only 0.4% of revenue, so the interior choice rests on a thin cushion: there France's income distribution moves
the design to 0.918 and its voting patterns to 0.335, against 0.707 and 0.687 at $\rho = 0.5$, so the inequality
response has no stable direction across elasticities, which is the sense in which the model ties the design to
ageing and not to inequality. The UK's own cost is within 17% of the U.S. one at $\rho \le 1$ and well above it
at $\rho = 2$. Tables in `\oa{esc-calibration}`, `\oa{esc-us}` and `\oa{esc-uk}`.

## 4. Exhibits

Input in section 7: `Tables/US_ESC_Country` (7.2), `Figs/US_ESC_Path.pdf` with `\label{fig:US_ESC:path}` and
`Tables/US_ESC_Results` (7.3). Remove the inputs of `Tables/US_ESC_Calibration` and `Tables/US_ESC_Summary` and
the figure environment of `Figs/US_ESC_overview.pdf`: these are the online appendix's now. Labels you may cite:
`table:US_ESC:country`, `table:US_ESC:results`, `fig:US_ESC:path`, `fig:US:OECDdata`, `table:US:Calib`; keys
`\oa{esc-calibration}`, `\oa{esc-us}`, `\oa{esc-uk}`, `\oa{esc-path}`, `\oa{esc-timing}`, `\oa{esc-scale}`.
Never cite `table:US_ESC:calibration`, `table:US_ESC:summary` or `fig:US_ESC:overview`: they are no longer in
the paper and `writing/checkPaper.py` will fail on them.

## 5. The cost paragraph (P2 of 7.1), to be used as written

The flat component redistributes within the retired cohort. Relative to an earnings-related benefit paying the
same revenue, it takes from retirees whose past earnings were above the mean and gives to those below it, a pure
transfer in the aggregate. We assume that the transfer is costly, in the sense of Okun's leaky bucket
\parencite{Okun75a1}: part of what the flat component carries does not arrive, and the part lost rises with the
amount carried. The amount carried to or from a retiree of type $i$, per unit of past earnings, is proportional
to $\tau_t(1-\theta_t)(1-1/y_i)$, where $y_i$ is the labor income of type $i$ relative to the mean: it rises with
the size of the system, with the flat share of benefits and with the distance of the type's income from the
mean. A loss on each type's earnings that is quadratic in this amount, as the deadweight loss of a tax is
quadratic in its rate \parencite{Harberger64a1}, summed over types and taken out of revenue, gives the budget

```
\begin{align}\label{eq:esc:budget}
    \nu_t w_t\tau_th_t\, f(\theta_t,\tau_t) &= \sum_i \gamma_i b_t^i, \\
    f(\theta_t,\tau_t) &= \exp\!\left(-\tfrac{1}{2}\,\lambda\,\tau_t\,\tilde{V}\,(1-\theta_t)^2\right), \qquad \tilde{V} \equiv \sum_i\gamma_i\frac{(y_i-1)^2}{y_i}, \nonumber
\end{align}
```

where $1-f$ is the share of revenue lost, $\lambda \geq 0$ is the cost parameter and $\tilde{V}$ is the
dispersion of relative incomes, in which a given transfer counts for more against a smaller income (appendix
\ref{app:esc:cost} derives the form from the implicit tax of the flat component).\footnote{The exponential form
keeps $f$ positive at every size of the system and nests the model without the cost at $\lambda = 0$; to first
order $1-f$ is the quadratic loss.} Nothing is lost when nothing is redistributed: $f = 1$ at $\theta_t = 1$
and, for every design, when all incomes are equal, where a flat and an earnings-related benefit pay the same to
everyone. And because the loss is quadratic in the amount carried while revenue is linear in it, the share lost
rises with the size of the system, so a larger system is costlier to keep redistributive, the
efficiency--redistribution trade-off by which \textcite{KoethenbuergerPP08a1} account for the finding of
\textcite{CondeRuizP07a1} that more redistributive systems are smaller, read from the other side.

(`Okun75a1` is in `References.bib`.)

## 6. Sentences elsewhere

- `Appendix/Robustness.tex`, the figure note: "Table \ref{table:US_ESC:summary} prints the designs chosen for
  the U.S.\ under a common $X$ with the cost of section \ref{sec:esc:cost}" becomes the same sentence with
  `table:US_ESC:results` and "at $\rho = 1$"; the other elasticities are in the online appendix sections it
  already names.
- `Sections/Introduction.tex`, the paragraph "An interior design requires flat benefits to be more expensive
  ...": its second sentence describes the cost as "read as the tax component of contributions". Rewrite that
  one sentence to the leaky bucket: a cost of the redistribution the flat component performs, whose leak rises
  with the amount carried, so that the share of revenue lost is quadratic in the flat share of benefits,
  proportional to the dispersion of incomes and rising with the size of the system. The rest of the paragraph
  stands.
- `Sections/Conclusion.tex`: nothing has to change; "a deadweight cost of redistribution that rises with the size
  of the system" and the sentence on the UK's own cost still hold. Change nothing there unless a claim you
  write in section 7 contradicts it.
- `abstract.tex`: read it; it still holds. Do not change it.

## 7. Appendix C

- §2 throughout: derivatives, "inherited design" or dated symbols, no "in force", no "contributive", "wedge"
  only in C.2.
- C.1 (`app:esc:corner`): the proposition and proof stay. The paragraph on the one-period-ahead timing gains
  the reasons section 7 drops: the choice keeps the Markov structure, it is the timing in which the design moves
  labor supply and savings before it binds (a design chosen with the tax moves no decision; a design chosen
  once and for all requires a commitment the paper's equilibria do not have), and it mirrors how reforms of
  benefit formulas are legislated, applying to future benefits and leaving benefits in payment untouched.
- C.2 (`app:esc:cost`): the derivation stays as it is, it is the foundation of the shape. The "Specification"
  paragraph absorbs the section's footnote on the alternatives: a cost on the flat component alone delivers the
  same endpoints, differs in the interior and loses the separate identification of $\theta$ and $\lambda$; a cost
  on the design itself, $f(\theta) = \phi + (1-\phi)\theta^{p}$, stays in place when a compressed distribution
  removes the redistributive stakes, and `\oa{esc-scale}` reports it. The "Magnitude" paragraph stays; section
  7's footnote on magnitude is cut in favour of a reference to it.
- No new propositions, no number changes, no change to the equations' content.

## 8. Numbers you may quote, and where each is printed

| Number | Source |
|---|---|
| $\theta^{\ast} = 0.738$; $\lambda = 8.643$ at $\rho = 1$; 1.8% and 24% of revenue lost ($f = 0.982$, $0.762$); $\tilde V = 0.436$ | `results/paper/Tables/US_ESC_Calibration.tex` (online), row $\rho = 1$; the $\lambda$ also in the note of `Tables/US_ESC_Results.tex` |
| $\lambda = 18.267$ and $1.724$ at $\rho = 0.5$ and $2$; 3.9% and 0.4% lost at the observed design, 44% and 5% at a flat one | the same table, the other rows |
| UK 0.560 observed, 11.9%, 0.625 chosen, own $\lambda = 7.264$, $\tilde V = 0.223$; France 1.000, 21.3%, 0.749, $\tilde V = 0.218$; UK at U.S. groups 0.543, 0.644, own 6.519, $\tilde V = 0.065$ | `Tables/US_ESC_Country.tex` |
| within 16% (7.264 against 8.643); within 17% at $\rho = 0.5$ (15.117 against 18.267); well above at $\rho = 2$ (2.777 against 1.724) | the country table; `results/esc/escCalibrationCRRAUK.csv`, printed in `\oa{esc-uk}` |
| baseline 0.738, 14.43% both readings; acute 0.825, 22.51% pinned, 22.80% chosen; income distribution 0.772, 13.78%, 13.80%; voting 0.653, 15.27%, 15.26% | `Tables/US_ESC_Results.tex` |
| composite 0.627, 14.40%, 14.44%; at $\rho = 0.5$ and $2$: acute 0.816, 0.826; income 0.707, 0.918; voting 0.687, 0.335 | `results/paper/Tables/US_ESC_Summary.tex` (online) |
| acute ageing without the size scaling: 0.778 at $\rho = 1$ | `results/paper/Tables/US_ESC_ScaleWedge.tex` (online), row "the design", $\rho = 1$ |
| path: design 0.738 (2020), 0.797 (2050), 0.804 (2080), 0.809 (2110 on); tax chosen 14.43%, 19.48%, 20.87%, 20.88%; pinned 14.43%, 19.33%, 20.67%, 20.67%; workers per retiree 1.34, 1.12, 1.07 | `results/paper/Tables/ESC_PathTable.tex` (online), block $\rho = 1$; $\nu_t$ from `results/esc/escPath.csv` |
| Frisch: $\lambda$ 8.736, 8.643, 8.547 at $\xi = 0.2, 0.3, 0.4$; 2110 design 0.809 at all three; acute-ageing design chosen 0.825, 0.825, 0.826 | `results/paper/Tables/ESC_Xi.tex` (online) |
| Frisch: the 2110 tax with the design chosen 21.2%, 20.9%, 20.6% at $\xi = 0.2, 0.3, 0.4$ | `results/paper/Tables/ESC_PathTable.tex` (online), rows `y2110xi0.2@1.0`, `y2110@1.0`, `y2110xi0.4@1.0` |
| section 6's responses with the design given: ageing 8.7 p.p., France's income distribution $-1.2$ p.p., France's voting patterns 0.9 p.p. | `Sections/OECD.tex` |

Style guide §3 for units and precision: taxes to one decimal in prose, designs to three decimals.

## 9. Stop conditions

- A number you need that none of the sources in §8 prints: write `\todo{...}` and report it; do not derive it.
- A label or key outside §4 that you would need: stop and report.
- Do not edit a generated file, rename a label, or touch `notes/paper_styleGuide.md`.

## 10. Checks before the report

`writing/checkPaper.py` with the repo's interpreter (`PYTHONUTF8=1 .venv\Scripts\python.exe writing\checkPaper.py`),
no control bytes in your files, the style guide's §6 checklist, every number against §8.
