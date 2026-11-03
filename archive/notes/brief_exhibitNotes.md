# Brief: shorter notes under tables and figures (2026-11-03)

Guideline: `notes/paper_styleGuide.md`, "What a note holds". A note says what is shown, the units, the
sample, the source and the conventions. Results, interpretation and restated specifications go to the
text, a table or the online appendix. These are guidelines: an exhibit that needs more keeps it.

Status: DONE 2026-11-03, archived. RKB's decisions: (8) Gini slopes dropped; (15) the 2020-tax check moved
to appendix D's text (with the spline details and the stationarity gap; sources in REPLICATION.md §5); (20)
RMSEs dropped; (11)-(13) the later notes point to figure 7.2. Variant copies (`_cps` etc., online appendix)
keep the full specification sentence (`tablesOECD26.specText`). Figure 7.2's note, the anchor, came out
longer than drafted (~90 words) because it also defines layer 2.
Generated notes are edited in their builder (column "where"), then `build.py --only <name>`;
`test_oecd26.py` may check note text and has to follow.

## Shared blocks (the OECD cross-section)

Six OECD26 notes repeat four blocks: (a) "20 countries (without Luxembourg, which has no CSES
survey)"; (b) "The model's index is 1/(2-θ) of the design in force in 2020, chosen in 1990, and its
spending τ(1-α) in 2020 on the path of the design it chooses"; (c) "Layer 1: every country at the U.S.
β = 0.65, ω = 1.26 and ε = 13.09, each at its cost λ_{n,t} = ε Π_{n,t}/R_{n,t}; layer 2: ω calibrated
to each country's spending at its observed design"; (d) "Turnout: each country's own propensities to
vote by income group, from the CSES". Section 7.3 (lines 64-66) defines (a), (c), (d) and λ_{n,t}.

Proposal: figure 7.2 (`OECD26_Layer1`, the first exhibit of 7.3) keeps (b) and a short (c). Every later
OECD26 note says "Model and layers as in figure 7.2" and states only what differs. Builder:
`tablesOECD26.py` (`turnoutNote`, the layer sentence near l. 307, `_sampleNote` near l. 282) and
`figuresOECD26.py`.

## Per exhibit (paper order; words = current note)

| # | Exhibit | Where | Words | Proposal | Removed content goes to |
|---|---|---|---|---|---|
| 1 | Fig. 1.1 `fig:US:OECDdata` | hand, `Sections/Introduction.tex` | 56 | Rewrite (below): define the four series and name the sources, instead of "various OECD databases ... several other sources" and two pointers. About the same length, more informative. Add the missing "\textit{Note:}". | -- |
| 2 | Fig. `fig:Arg` | hand, `Argentina.tex` | 32 | Keep. | -- |
| 3 | Tab. `table:Arg:Calib` | `tables.py` | 8 | Keep; "The baseline is $\rho = 1$." | -- |
| 4 | Tab. `table:Argentina:Universal` | `tables.py` | 79 | Cut the reform's definition, which section 5 gives; keep the scenario labels and units (below). | section 5 already |
| 5 | Fig. `fig:ARG:EffectOfCRRA` | hand, `Argentina.tex` | 46 | Keep. | -- |
| 6 | Tab. `table:US:CalibUSFR` | `tablesUS.py` | 48 | Keep. | -- |
| 7 | Fig. `fig:US:overview` | hand, `OECD.tex` | 51 | Keep. | -- |
| 8 | Fig. `fig:OECD26:spending` | `figuresOECD26.py` | 93 | Drop the four slopes and standard errors (results). Keep sample, model spending, calibration, turnout (below). | Population-growth slopes are already in section 6 (l. 39). The Gini slopes, 14.79 (26.28) and -11.98 (13.11), go into that sentence if wanted. |
| 9 | Tab. `table:US_ESC:calibration` | `tablesUS.py` | 52 | Keep. | -- |
| 10 | Fig. `fig:US_ESC:overview` | hand, `EndogenousTheta.tex` | 13 | Keep. | -- |
| 11 | Fig. 7.2 `fig:OECD26:layer1` | `figuresOECD26.py` | 116 | Anchor of the shared blocks, shortened (below). | -- |
| 12 | Tab. `table:OECD26:slopes` | `tablesOECD26.py` | 116 | Conventions, sample and a pointer (below). | figure 7.2's note; section 7.3 |
| 13 | Fig. `fig:OECD26:thetaFit` | `figuresOECD26.py` | 168 | Drop the r, RMSE and SD statistics: section 7.3 (l. 86) quotes every one. Keep markers and lines (below). | section 7.3 already |
| 14 | Tab. `table:T:Horizon` | `tablesHorizon.py` | 218 | Keep the column definitions, units and the cost. The steady-state construction (40 extra periods, the 1.1e-6) goes to appendix D's text; the log-preference sentence is already there (l. 40). | appendix D text |
| 15 | Tab. `table:T:Residuals` | `tablesHorizon.py` | 228 | Keep what a cell is, the three evaluation sets and the two column blocks. The spline details and the check of the 2020 tax (10.52%, 9.13 against 9.12 p.p.) go to appendix D's text, or to the online appendix's numerical section. | appendix D text / OA |
| 16-17 | Household heterogeneity, U.S. and France | `tablesUS.py` | 0 | Keep. | -- |
| 18 | Tab. `table:OECD26:omega` | `tablesOECD26.py` | 160 | Keep the column definitions (the table's job). Shorten the θ definition to a pointer to appendix G.1, and drop (c) and (d) for a pointer (below). | appendix G.1 already |
| 19 | Tab. `table:OECD26:thetaVariants` | `tablesOECD26.py` | 172 | Keep the variant counts and the two turnout readings; drop (b) and (c) for a pointer (below). | figure 7.2's note |
| 20 | Fig. `fig:OECD26:thetaFitGrid` | `figuresOECD26.py` | 274 | Drop the anchors' ω and ε per reading, and the nine statistics. Keep the three readings and the markers (below). | ε = 10.78 at U.S. turnout is in G.2 text (l. 13). Correlations: U.S. turnout in 7.3 (l. 101), pooled in `table:OECD26:stylized`. RMSEs at U.S. and pooled turnout appear nowhere else: drop, or add to the OA. |
| 21 | Tab. `table:OECD26:stylized` | `tablesOECD26.py` | 226 | Keep the column conventions and the row definitions; the pooled reading is defined once, in G (l. 41), and here only named; drop (b), (c) for a pointer (below). | appendix G text already |

## Proposed note texts

(1) Fig. 1.1. \textit{Note:} 21 OECD countries, selected as in appendix \ref{app:oecd26}. Pension
spending is public cash spending on old age and survivors in 2020, in \% of GDP; population growth is
the population of 2020 relative to 1990; the Gini is that of disposable income. The Bismarckian index
is $I = 1/(2-\theta)$, with $\theta$ the earnings-linked share of the public pension net of minimum
top-ups and tested benefits. Sources: OECD (SOCX, \textit{Pensions at a Glance 2021}, population
statistics), World Bank WDI and UNU-WIDER WIID. [~65 words]

(4) \textit{Note:} The reform of section \ref{sec:argentina}, $\rho = 1$. Economic equilibrium: the
new $\epsilon$ with taxes as in the baseline; full effect: taxes set in politico-economic equilibrium.
The savings rate is savings relative to GDP, formal plus informal output; formal benefits are the change
in the benefit of every formal retiree against the baseline. [~50]

(8) \textit{Note:} 20 countries; Luxembourg has no CSES survey of turnout. The model's spending is
$\tau(1-\alpha)$ in 2020 at the observed design, every country at the U.S.\ $\beta = 0.65$ and
$\omega = 1.19$, without the cost, and at its own CSES propensities to vote. The lines are least-squares
fits. [~50]

(11) Fig. 7.2. \textit{Note:} 20 countries, as in figure \ref{fig:OECD26:spending}. The model's index
is $1/(2-\theta)$ of the design chosen in 1990 for 2020, its spending $\tau(1-\alpha)$ in 2020 on that
path, in the first layer of section \ref{sec:esc:crossSection}. The lines are least-squares fits, with
the slopes of table \ref{table:OECD26:slopes}. [~50]

(12) \textit{Note:} Least-squares slopes, standard errors in parentheses, 20 countries. Model and
layers as in figure \ref{fig:OECD26:layer1} and section \ref{sec:esc:crossSection}. [~25]

(13) \textit{Note:} The model's design for 2020, chosen in 1990, against the observed one, in both
layers (figure \ref{fig:OECD26:layer1}). The U.S.\ is the anchor and lies on the $45^{\circ}$ line by
construction; the solid line is the least-squares fit over the other 19 countries. [~45]

(14) \textit{Note:} The first two columns are levels at the paper's horizon, $T = 2200$ in the U.S.\
and $2190$ in Argentina; the others are changes against them at the same date, with the backward
induction started two periods earlier, three periods later, or from the steady state of appendix
\ref{app:T}. Tax and savings rates in percent, their changes in percentage points, the design in units
of $\theta$. The design is chosen one period ahead at the calibrated cost; in Argentina the universal
pension is that of section \ref{sec:argentina}, as a change against the baseline of the same horizon.
[~95]

(15) \textit{Note:} Each cell is the largest (or 99th percentile) absolute difference, in percentage
points of the tax rate, between the root of the first order condition at a state and the policy
function there, over the periods of the paper's horizon: at the states the equilibrium path visits, at
the cell centers of the state grid within the range the path visits (padded by a fifth), and at all
cell centers. The first four columns evaluate the condition as the solver does, the last four with its
derivatives in the tax converged. Log preferences in the U.S.\ have no state. [~90]

(18) \textit{Note:} 20 countries. $\nu_{2020}$, workers per retiree; $\tilde V$, the dispersion of
relative incomes at the U.S.\ income percentiles; spending in \% of GDP; $\theta$ and $I = 1/(2-\theta)$
as in appendix \ref{app:oecd26:data}. $\omega$ is calibrated to spending at the observed design (the
second layer); the last two columns are the model's design for 2020, chosen in 1990, and its index.
$^{\ast}$The anchor, where $\omega$ and $\varepsilon$ are calibrated. [~65]

(19) \textit{Note:} Least-squares slopes, standard errors in parentheses. Each measure of $\theta$
(appendix \ref{app:oecd26:data}) is its own cross-section, the data and the model calibrated to it, on
its countries at U.S.\ and at own turnout: C 21/20, A 23/22, B 26/25. U.S.\ turnout: the CPS
propensities to vote in every country; own turnout: each country's CSES propensities, the anchor
recalibrated at its own. Model and layers as in figure \ref{fig:OECD26:layer1}. $^{\ast}$The paper's
measure; at own turnout, table \ref{table:OECD26:slopes}. [~80]

(20) \textit{Note:} As figure \ref{fig:OECD26:thetaFit}, under three readings of the propensities to
vote: U.S.\ (CPS) in every country, each country's own (CSES, the paper's), and pooled (appendix
\ref{app:oecd26}). Each anchor is calibrated at its own reading. The U.S.\ is open; the solid lines
are least-squares fits over the other countries, 21, 20 and 21. [~55]

(21) \textit{Note:} The test of table \ref{table:OECD26:slopes} under the two readings of appendix
\ref{app:oecd26}: every country at the mean of the second layer's $\omega$ (1.31 at own and 1.33 at
pooled turnout, against the anchor's 1.26), and pooled turnout. Slopes: least squares, standard errors
in parentheses, the U.S.\ included; correlations and means: without the U.S. Spending in \% of GDP.
Model and layers as in figure \ref{fig:OECD26:layer1}. $^{\ast}$The paper's specification. [~75]

## Open for RKB

- (8): put the Gini slopes in the text, or drop them?
- (15): the 2020-tax check, to appendix D's text or to the OA?
- (20): drop the RMSEs at U.S. and pooled turnout, or report them in the OA?
- (11)-(13): is pointing back to figure 7.2 enough for a reader who opens the appendix tables first?
  The alternative repeats (c) in one clause per note.
