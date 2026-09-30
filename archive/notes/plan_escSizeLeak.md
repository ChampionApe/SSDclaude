# Plan: the size-scaled leak as the paper's endogenous design (branch `esc-sizeLeak`, 2026-09-24)

The decision this branch executes: replace the wedge $f(\theta)=\phi+(1-\phi)\theta^{p}$ of section 7 by a
deadweight cost that scales with the redistribution the design performs and with the size of the system,
candidate B of `notes/esc_inequalityChannel.md`. Why: under the current wedge the cost is attached to the
label $\theta$ rather than to the cross-subsidy, so a compressed income distribution sends the chosen design
to the Bismarckian corner and the US wedge sends the UK there too; under B the pilot at $\rho=1$ gave an
interior income row (0.78), a first-order ageing effect (0.84 under acute ageing) and the observed
cross-country ranking UK < US < France from one parameter. The pilot is archived in
`archive/pilots/escSizeLeak_2026-09-24/`.

The plan is written so that work packages can be handed to agents in parallel. Section 3 is the dependency
graph, section 4 the handoff protocol, section 7 the decisions RKB may want to overrule (each has a
default so nothing blocks).

## 0. Basis, and what the paper should and should not claim

Sound in form, calibrated in magnitude. The flat component of a PAYG benefit levies a type-specific
implicit tax on lifetime earnings, $t_i=\tau(1-\theta)(1-1/y_i)$ up to the PAYG return factor, a subsidy for
$y_i<1$. The Harberger loss of a set of such wedges is quadratic in each of them, $\tfrac12\varepsilon\sum_i
\gamma_i y_i t_i^2$ per unit of earnings, which as a share of revenue is $\tfrac12\varepsilon\,\tau\,(1-\theta)^2
\tilde V$ with $\tilde V=\sum_i\gamma_i(y_i-1)^2/y_i$. This is the "tax component" of contributions of
Summers (1989) and Disney (2004, *Economic Policy*), whose employment effects Disney documents across the
OECD, and the mechanism by which Koethenbuerger, Poutvaara and Profeta (2008, *JPubE*) explain why more
redistributive systems are smaller, the stylised fact of Conde-Ruiz and Profeta (2007, already cited). The
form therefore has a derivation; the elasticity does not. The calibrated $\lambda$ will be of order 16 at
$\rho=1$ (the pilot's 2.05 rescaled by $1/\tau_{US}$ and $V/\tilde V$), an order of magnitude above what
labour-supply elasticities of 0.1 to 0.6 would give. The paper should say so: the leak's shape follows the
deadweight-loss logic of the tax component; its size is calibrated and stands in for administrative,
evasion and political costs of redistribution the model does not contain. That is the same position the
technical note already takes for the current wedge, now with a form that vanishes when nothing is
redistributed.

What does not change: sections 1 to 6 and every exogenous-$\theta$ result; the identification
$\theta^\ast=0.738$ (the cost is proportional, so it cancels from the replacement-rate ratio); the leaded
timing, the Markov structure, the LOG propositions (substitution, decoupling, separability, concentration)
and the numerical machinery.

## 1. Specification

$$
f(\theta_t,\tau_t)=\exp\!\Big(-\tfrac12\,\lambda\,\tau_t\,\tilde V\,(1-\theta_t)^2\Big),\qquad
\tilde V\equiv\sum_i\gamma_i\frac{(y_i-1)^2}{y_i},\qquad y_i=\frac{\eta_i^{1+\xi}/X_i^{\xi}}{\Gamma_h},
$$
with $A(\theta,\tau)=f\theta$, $B(\theta,\tau)=f(1-\theta)$, code spec name `'size'`. Conventions:

- **Same-date pairs.** $f$ takes the design and the tax of the date whose benefits it scales: $(\theta_t,
  \tau_t)$ in the benefit formula and the retirees' consumption, $(\theta_{t+1},\tau_{t+1})$ in $\Gamma_s$,
  $\Theta_h$, $s_i/s$ and the young's bracket, with $\tau_{t+1}=\mathcal T_{t+1}(\theta_{t+1})$ the
  continuation. The young at $t$ anticipate both, which is the Harberger reading.
- **$\tilde V$ with the vintage of the bracket it multiplies** (the retirees' cohort in the benefit
  formula, `lag='[t-1]'`; the young's elsewhere). Time-invariant $\eta$ makes them equal here, but the
  code keeps the vintages straight so a time-varying distribution would not silently mix them.
- **Exponential form** so $f\in(0,1]$ for every $\lambda$; $1-f\approx$ the Harberger share. The paper
  presents $1-f$ as the share of revenue lost.
- **$\lambda$ lives in the existing `wedgeP` slot** and the csv column `p`, so no schema, merge key or
  pipeline column changes; the paper prints it as $\lambda$. `phi` stays in every key as a dummy (0.5) under
  `'size'` because `pickCalib`/`escRow` filter on it; it is not used by $f$.
- **The ESC leg stays under the common-$X$ calibration** (`config.US['commonX']`), as now.

What changes in the equations, for WP1 and WP2:

| object | current | under `'size'` |
|---|---|---|
| benefits | $b_t^i=f(\theta_t)[\theta_t y_i+1-\theta_t]\bar b_t h_{t-1}$ | $f(\theta_t,\tau_t)[\cdots]$ |
| tax FOC, retirees' term $\partial\ln c_{2,t}^i/\partial\tau_t$ | $(1-\alpha)\frac{d\ln h}{d\tau}+\frac{A_0\,\mathrm{br}_i}{\sigma_i+A_0\tau_t\mathrm{br}_i}$ | numerator $\times\,(1+\tau_t\,\partial_\tau\ln f)$, $\partial_\tau\ln f=-\tfrac12\lambda\tilde V(1-\theta_t)^2$ |
| tax FOC, everything else | | unchanged: under LOG the young's terms and $d\ln h_t/d\tau_t$ do not see $f$; under CRRA the numerical $\tau$-derivatives see $f(\theta_{t+1},\tau_{t+1})$ only through the continuation, as they already do |
| sequential FOC, $A'$, $B'$ | $A'=f+\theta f'$, $B'=(1-\theta)f'-f$ | same with $\partial_\theta\ln f=\lambda\tau\tilde V(1-\theta)$; $A'+B'=f\lambda\tau\tilde V(1-\theta)\ge0$, zero at $\theta=1$ |
| leaded FOC | eq `esc:leadFOC`, `esc:leadFOCcost` | unchanged in form, $A(\theta_{t+1},\tau_{t+1})$ |
| identification | $f$ cancels from $B/A$ | unchanged |
| propositions | substitution, decoupling, separability, concentration | hold with $(\theta,\tau)$ arguments; decoupling because $\theta_{t+1},\tau_{t+1}$ still enter $\ln\Theta_{h,t}$ additively; concentration because $z_{t_0}$ carries $\partial_\tau f$ |
| calibration | $p$: design in force at 2020 $=\theta^\ast$ | $\lambda$, same residual, same nested $(\beta,\omega)$ |

## 2. Work packages

Each package lists owner lane, inputs, files it owns (nobody else edits them while it is open), acceptance
criteria and a time estimate. Estimates are working time for one agent.

### WP1. Derivation and the technical note (lane A, ½ day, independent)

Files: `writing/US/model_esc.tex`, `writing/US/num_esc.tex`, `writing/Paper/References.bib` (new entries
only). Do not touch `writing/Paper/Sections/*`.

- `model_esc.tex`: rewrite "The deadweight cost of redistributive benefits" around the implicit-tax
  derivation of section 0 and the specification of section 1; eq `esc:AB` becomes the `'size'` form with
  the old proportional and flat-only forms demoted to one sentence of history; the substitution
  proposition gains $(\theta,\tau)$ arguments and one sentence on the retirees' $\tau$-derivative; the
  identification paragraph is unchanged in substance; `esc:seqFOC` with the new $A'$, $B'$.
- `num_esc.tex`: the calibration paragraph (a $\lambda$ scan on a log grid, bracket of order $[0.5,200]$
  at $\rho=1$ and an order of magnitude lower at $\rho=2$, the same flat-at-a-corner warning); the
  verification list of section 5 below written as the note's "checks", numbers left as `\todo{}` for WP4.
- `References.bib`: Summers (1989, AER P&P, "Some simple economics of mandated benefits"), Disney (2004,
  Economic Policy 19(39), "Are contributions to public pension programmes a tax on employment?"),
  Koethenbuerger, Poutvaara and Profeta (2008, JPubE 92, "Why are more redistributive social security
  systems smaller? A median voter approach"). Verify volume and pages before committing.

Acceptance: every `\refeq:` label cited from a `.py` docstring still exists (grep the labels the code
cites: `esc:AB`, `esc:seqFOC`, `esc:leadFOC`, `esc:auxiliary*`, `esc:calibration`, `esc:permFixedPoint`);
the note compiles in the user's local setup is NOT checked here (convention: no compiling).

### WP2. Code and tests (lane B, 1 day, independent; merges first)

Files: `python/US/base.py`, `python/US/policyESC.py`, `python/US/modelESC.py`, `python/US/runESC.py`,
`python/US/runESCcrra.py`, `python/US/thetaStakes.py`, `python/US/test_esc.py`. Read first:
`python/US/README.md`, `notes/crossCuttingFindings.md` #3, #5, #7, #9, #10, #13, #15, the 2026-09-11
entry of `python/US/RESEARCH_LOG.md`, the docstring of `test_esc.py`.

- `base.py`: `fWedge(θ, τ)` with the `'size'` branch; `dlnfWedge_dτ(θ, τ)`; `wedgeA(θ, τ)`, `wedgeB(θ, τ)`;
  a memoised `Vtilde(t, lag)` from `hηRatio` and `γi` (works on `Base`, `BaseGrid` and `BaseTime`, whose
  `self(k, t)` conventions differ, and broadcasts over $t$ on `BaseTime`); every call site passes the
  $\tau$ in scope (`τ1` beside `θ1` in `Γs`, `Θh`, `si_s`, `pension`, `tildec1i`; `τ` beside `θ` in the
  benefit bracket, `c2i`, `dlnc2i_dτ`, `ΓsCap`, `BSteadyState`); `dlnc2i_dτ` multiplies `num` by
  $(1+\tau\,\partial_\tau\ln f)$. Under `None`, `'scale'` and `'flat'` the $\tau$ argument is ignored, so
  those paths stay bit-identical.
- `modelESC.py`: `'size'` in the spec registry; `getθ` needs nothing (it already treats every non-`'flat'`
  spec as proportional); `calibrateWedge` takes a spec-dependent default bracket; `setWedge` unchanged.
- `policyESC.py`: grep for direct uses of `wedgeA/wedgeB/fWedge` and pass $\tau$; the comment at the
  `~965` mark about the functions being functions of the argument stays true. `LeadedLOG.z`'s placeholders
  for $(\tau_{t+1},\theta_{t+1})$ remain placeholders: under LOG $z_t$ does not see them for any $f$
  (section 1's table), and test 3 below measures that.
- `runESC.py`, `runESCcrra.py`: `--spec size` accepted everywhere `'scale'` is; the `--bracket` default per
  spec; `stageCountry` unchanged (it already runs the US wedge on the UK, France and UK-at-US-cuts and
  calibrates the UK's own). `thetaStakes.py`'s own `fWedge` lambda gains the spec; low priority.
- `test_esc.py`, new sections, all measured on the calibrated US model at $\rho=1$: (9) `'size'` at
  $\lambda=0$ reproduces `ModelUS` bitwise; (10) `dlnc2i_dτ` under `'size'` equals a central finite
  difference of `ln c2i` at fixed `siRatio_` to 1e-8 relative; (11) test 3 (the unit-square sweep) under
  `'size'`; (12) test 4 (invariance to $s_{t-1}$) under `'size'`; (13) `Vtilde` invariant to a common
  rescaling of $X_i$ and of $\eta_i$, equal to zero when all $y_i=1$, and then $f\equiv1$; (14) `getθ`
  under `'size'` is 0.7382263650. Existing sections 1 to 8 must pass unchanged, and the calibrated
  `'scale'` $p$ at $\rho=1$ (0.4076119851) must reproduce: that is the regression gate for the untouched
  paths.

Acceptance: `python\runTests.py -k esc` fast suites pass; `python\US\test_esc.py` prints PASS on every
section; the diff touches no file outside the list. Report: the 10-line summary of section 4, plus the
measured numbers of sections 10 and 13.

### WP3. Paper pipeline (lane C, ½ day, independent; merges second)

Files: `python/paper/config.py`, `python/paper/tablesUS.py`, `python/paper/datasets.py`,
`python/paper/figuresUS.py`, `python/paper/build.py`, `python/paper/runCalibrationUS.py`,
`python/paper/runShocksUS.py`, `python/paper/README.md`. Read first `python/paper/README.md` and the
2026-09-11 and 2026-09-22 entries of `python/paper/RESEARCH_LOG.md`.

- `config.US['esc']['spec'] = 'size'`; `phi` stays 0.5 as the dummy key; a comment says why.
- `US_ESC_Calibration`: columns $\rho$, $\lambda$, $\theta^\ast$, $f(\theta^\ast)$, $f(0)$, $\tilde V$; the
  note drops "$\phi$ imposed" and states the form. `UK_ESC_Calibration` becomes `US_ESC_Country`: one row
  per economy (UK, France, UK at US cuts) with the observed design, the choice under the US $\lambda$ and
  the economy's own $\lambda$, read from `escCountry.csv` (schema already has `wedgeFrom`, `θStar`,
  `choice`, `p`). Register it in `build.py`; keep the old builder callable for the `'scale'` rows.
- The four experiment tables and `escOverview` need no change beyond the note text that names the cost;
  `datasets.escRow` already filters on `spec`.
- Stage (i)/(ii) of the US arm must pass `config`'s spec to `runESC.py`/`runESCcrra.py` and to
  `stationaryApproxESC.py`; check `runCalibrationUS.py --prepub` and `runShocksUS.py`.

Develop against the existing csvs with `spec` temporarily read as `'scale'`: the columns are the same, so
the builders can be exercised before WP4 produces `'size'` rows. Acceptance: `python\paper\build.py --only
US_ESC_Calibration US_ESC_Country US_ESC_Ageing` builds from the `'scale'` rows without error; `runTests`
fast suites pass; README updated.

### WP4. Runs (lane D, in the main checkout, after WP2 and WP3 merge)

LOG first, in the foreground, about 15 minutes:

```
set PYTHONUTF8=1
python\US\runESC.py --spec size --phi 0.5 --commonX --stage calib path shocks country
python\US\collectESCexperiments.py
python\paper\build.py --only US_ESC_Calibration US_ESC_Country US_ESC_Ageing US_ESC_IncomeDistr US_ESC_Voting US_ESC_FrenchAll US_ESC_overview
```

Read the LOG numbers against the stop conditions of section 6 before anything else starts. Then CRRA,
detached, the two $\rho$ in parallel processes (8 cores; each process is one core of numpy work most of the
time), through a `logs/*.ps1` that routes output with `cmd /c "... > log 2>&1"` (the traps in
`notes/TODO.md`):

```
python\US\runESCcrra.py --exact --rho 0.5 --spec size --phi 0.5 --commonX --stage calib path shocks --bracket L0 U0
python\US\runESCcrra.py --exact --rho 2.0 --spec size --phi 0.5 --commonX --stage calib path shocks --bracket L2 U2
```

with brackets $[\lambda_{LOG}/20,\ 3\lambda_{LOG}]$ at $\rho=2$ and $[\lambda_{LOG}/3,\ 5\lambda_{LOG}]$ at
$\rho=0.5$ (the current $p$ falls by a factor of 8 from $\rho=0.5$ to $2$). Budget per $\rho$: calibration
about 45 minutes (scan on `nsScan` 50, refine on `ns` 150), the path, then sixteen exact recursions of
about 6 minutes for the shocks and a France row: about 3 hours wall for both. Afterwards, also detached:
`python\US\stationaryApproxESC.py --commonX --spec size` (about 1 hour; only if `sec:numerical`'s
footnote keeps quoting the ESC misplacement) and `python\runTests.py --slow` (`test_escCRRA.py` about 7
minutes, `test_escTiming.py` about 75 s; both must still pass on the `'scale'` reference numbers they pin).
Then `collectESCexperiments.py` and the full `build.py`.

Poll a detached log with `grep -q` in an `until` loop, never `tail -F` (finding #14). Every csv is merge
keyed on `spec`, so `'size'` rows coexist with the `'scale'` rows and nothing is clobbered (finding #13);
a rerun of a stage resumes from the csv.

### WP5. Paper text (lane E, 1 day; drafts against LOG numbers, finalises against CRRA)

Files: `writing/Paper/Sections/EndogenousTheta.tex`, the W1 sentence and the paragraph after it in
`Introduction.tex`, the last sentence of `abstract.tex`, the last paragraph of `Conclusion.tex`, the last
paragraph of `OECD.tex`, the ESC footnote of `Numerical.tex` (only if WP4 reran the stationary check),
`Appendix/USauxiliary.tex` (`app:US:ukESC` becomes the cross-country test and inputs `US_ESC_Country`).
Register: `notes/paper_styleGuide.md`. Do not edit any `Tables/*.tex` (generated).

- "Costly redistribution, and the preferred specification": the cost paragraph around eq `esc:budget`
  with the `'size'` form, three sentences of motivation (the tax component; nothing lost when nothing is
  redistributed; the loss per unit of redistribution rises with the size of the system), the magnitude
  caveat of section 0 in one sentence, the calibration paragraph with $\lambda$ across $\rho$.
- Results: ageing (now first order, with the mechanism: a larger system makes the flat component
  costlier at the margin, on top of the political-weight channel), income distribution (interior,
  minor; the "design reversal" paragraph goes), voting, both at once (signed at $\rho=1$; state what
  happens at $\rho=2$ once known), the design path, and a new paragraph "Across countries": the UK and
  France under the US $\lambda$, the UK's own $\lambda$, read against 0.56 and 1.00, and the honest note
  that France's corner is not reached because the first unit of redistribution is free at the margin under
  a quadratic loss.
- Intro, abstract, conclusion: the sentences that currently say "a flatter income distribution moves it to
  the Bismarckian corner" and "which of the last two wins depends on the intertemporal elasticity".

Acceptance: every number in the prose traces to a `results/` csv or a generated table; no generated table
edited; RKB reads it before the Overleaf push (`writing/overleaf.py push paper`, after `pull --dry-run`).

### WP6. Docs and close (coordinator, ½ day, last)

`python/US/README.md` (Endogenous θ: `'size'` is the paper's spec, `'scale'` the previous one and the
comparison arm), `python/paper/README.md`, the three research logs (root: the decision and the
cross-country test; US: the code; paper: the pipeline), `notes/TODO.md` (close P1), `notes/
esc_inequalityChannel.md` (one line: outcome and where the numbers are), `pyenv.md` if a package changed
(it will not). Propose finding #17 for `notes/crossCuttingFindings.md` for RKB to accept or not: "A
reduced-form cost must vanish when the quantity it prices vanishes; test the specification at $V=0$."
Then merge `esc-sizeLeak` into `main` (fast-forward if main has not moved; otherwise rebase the branch
first) and push the paper to Overleaf.

## 3. Dependency graph and schedule

```
WP1 tex ─────────────────────────────────────────────┐
WP2 code+tests ──┐                                    │
WP3 pipeline ────┼─ merge B then C ─ WP4 LOG (15 min) ┼─ WP5 draft (LOG numbers) ─┐
                 │                    │               │                          ├─ WP6 close ─ merge to main
                 │                    └─ WP4 CRRA (3 h, detached, two processes) ─┴─ rebuild, WP5 final
```

Day 1: WP1, WP2, WP3 in parallel (three agents, three worktrees). Day 1 late: merge B, run the fast suites,
merge C, run WP4 LOG, check the stop conditions, start the CRRA processes and the slow tests. Day 2: WP5
against the LOG numbers while CRRA runs; rebuild when it lands; finalise WP5; WP6. Two working days with
one overnight, three agents at the peak.

## 4. Handoff protocol

**Where each lane works.** WP1, WP2, WP3 and WP5 in their own git worktree of `esc-sizeLeak` (the Agent
tool's `isolation: "worktree"`, or `git worktree add ..\SSDclaude-wpN esc-sizeLeak` by hand). WP4 in the
main checkout only: it writes `results/` and pickles, and detached runs must not live in a temporary
worktree. The coordinator merges worktree branches into `esc-sizeLeak` in the order B, C, A, E.

**The brief every agent gets** (paste, then the WP section above):

1. Read, in this order: `CLAUDE.md`; this plan's sections 0, 1 and your WP; `notes/esc_inequalityChannel.md`;
   the files your WP lists under "read first". Do not read `archive/` unless your WP points there.
2. You own the files your WP lists and no others. If the work needs a file outside the list, stop and report
   which and why; do not edit it.
3. Conventions that bind: docstrings are specs, not chronicles (`CLAUDE.md`); a `%% GENERATED` file is never
   edited by hand; every run sets `PYTHONUTF8=1`; PowerShell `*>` writes UTF-16, route through `cmd /c`;
   workbooks are edited through Excel only; a resumable csv is keyed on `spec` and `commonX`.
4. Deliverable: a commit on your worktree branch with a message that names the WP, plus a report of at most
   ten lines: what changed, what was measured (the numbers), what is open, and the exact command that
   reproduces your check. The report is what the coordinator reads; the diff is what gets merged.
5. Stop conditions: report and stop, do not work around, if a check in section 5 fails, if a stop condition
   in section 6 triggers, or if the task needs a decision listed in section 7.

**Coordinator checklist** at each merge: fast suites green on the merged tree (`python\runTests.py`, about
160 s), `git status` clean, the module README says what is true now, the log entry is at most ten lines.
Never merge a lane whose report has an unanswered "open" line that touches another lane's files.

**What to report back to RKB** at the end of WP4 LOG (the first real result): the calibrated $\lambda$, the
seven-row table of section 5's check 15, the three country rows, and whether any stop condition fired.
That is the moment to confirm the direction before the CRRA hours and the prose are spent.

## 5. Verification battery (measured, not assumed; numbers into `num_esc.tex` and the US log)

1. `'size'` at $\lambda=0$ reproduces `ModelUS` bitwise (extends test 1).
2. The `'scale'` paths are untouched: $p=0.4076119851$ at $\rho=1$, and every pinned number in
   `test_esc.py` and `test_escTiming.py` still passes.
3. $z_t$ does not see $(\tau_{t+1},\theta_{t+1})$ under `'size'` (test 3 on the unit square).
4. The leaded choice is invariant to $s_{t-1}$ under `'size'` (test 4).
5. The retirees' analytic $\tau$-derivative equals its finite difference at fixed $s_{t-1,i}/s_{t-1}$ to
   1e-8 relative.
6. $\tilde V$ invariances: common $X$ scale, $\eta$ scale, and $f\equiv1$ at $\tilde V=0$.
7. `getθ` unchanged under `'size'`.
8. The $\lambda$ scan has exactly one sign change, and the calibrated path's target drift is at the current
   tolerances ($10^{-8}$ in $\tau$, $10^{-3}$ in $R$).
9. The design path's drift 2020 to 2110 (the ageing prediction), reported next to the current 0.738 to
   0.773.
10. CRRA: the exact 2-D choice at the calibrated $\lambda$ against the path iteration, expected within 0.01 as
    now; the $\rho\to1$ continuity ratio $\text{gap}/(\rho-1)$ roughly constant.
11. The 2-D solver's candidate-grid sensitivity at the frVoting point (41 nodes settle the third decimal
    now; re-measure once).
12. Stationary-vs-date-specific misplacement of the design if `sec:numerical`'s footnote keeps it.
13. The placebo: French leisure leaves the chosen design at the baseline to the method's tolerance.
14. Invariance of the chosen design to the calibration variant is not re-measured (the ESC leg runs under
    common $X$ only), but the vector-$X$ note in `sec:esc`'s footnote must still be true: the design enters
    through relative incomes only, which both calibrations match.
15. The result table itself: chosen design, tax, savings and workweek at 2020 for baseline, mild, acute,
    frIncome, frLeisure, frVoting, frBoth, frAll at $\rho\in\{0.5,1,2\}$, pinned and chosen.
16. Cross-country: the UK, France and UK-at-US-cuts under the US $\lambda$; the UK's own $\lambda$; France's
    own (expected: no interior crossing, reported as such).

## 6. Stop conditions (report before continuing)

- S1. The LOG income row corners at $\theta=1$ under `'size'`. The pilot gave 0.78; if the in-solve
  $\tau$-feedback changes that, check $\tilde V$ against $V$ (section 7, D1) before anything else.
- S2. The country ranking is lost: the UK's choice under the US $\lambda$ above the US design, or France's
  below it. The pilot gave 0.60 and 0.77.
- S3. No sign change in a CRRA calibration scan. Widen downward once (a thin wedge at high $\rho$); if still
  none, the choice is at a corner without cost at that $\rho$, which is a result to report, not a bug.
- S4. The exact 2-D choice and the path iteration separate by more than 0.02 at the calibrated $\lambda$:
  raise the candidate grid, re-measure (check 11), then report.
- S5. Any `'scale'` regression: the previous wedge's numbers are the comparison arm and must stay
  reproducible.

## 7. Decisions for RKB, each with the default the plan assumes

- D1. **$\tilde V$ (Harberger weights, default) or $V=\sum_i\gamma_i(y_i-1)^2$ (the pilot's).** They differ by
  the $1/y_i$ weighting, i.e. a rescaling of $\lambda$ and a small change in the cross-country ordering.
  Default $\tilde V$ because it comes with the derivation.
- D2. **Keep the previous wedge as an appendix robustness** (one calibration table and the income row under
  `'scale'`, "the cost attached to the design rather than to the transfer") **or drop it.** Default: keep
  for this revision, one table, one paragraph; drop before submission.
- D3. **A second, linear (Okun) term** so that a corner at $\theta=1$ is attainable and France's design can be
  matched, calibrated on the US and the UK jointly with France as the prediction. Default: not in this
  branch; a sentence in the text and an item in the TODO.
- D4. **Where the derivation goes.** Default: one paragraph in section 7, the derivation in the technical
  note.
- D5. **The PAYG return factor $\Pi_t$ inside the leak** (it multiplies the implicit tax and carries $\nu_t$).
  Default: absorbed into $\lambda$; a footnote.
- D6. **The stationary-approximation footnote.** Default: rerun `stationaryApproxESC.py` under `'size'` so
  the footnote's ESC numbers are the paper's own; if compute is short, drop the ESC clause from the footnote.

## 8. Definition of done

`esc-sizeLeak` merged into `main` with: the fast and slow suites green; `results/esc/*` carrying `'size'`
rows at $\rho\in\{0.5,1,2\}$ (exact method) next to the `'scale'` rows; `writing/Paper` rebuilt from them
with the seven ESC outputs plus `US_ESC_Country`; section 7, the intro, abstract and conclusion updated;
the technical note updated; READMEs, logs and TODO current; the Overleaf project pushed after a dry-run
pull; this plan moved to `archive/notes/` with a pointer from the root log, per the repo's rule for closed
plans.
