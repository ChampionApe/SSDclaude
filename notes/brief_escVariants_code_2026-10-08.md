# Brief: two new cost specifications in the US module (phase B)

For the `model-coder` agent. Plan: `notes/plan_endogenousDesign.md` §C (C.1 decisions 1-3, C.5 schema).
Read `python/US/README.md` (section "Endogenous θ"), `python/US/RESEARCH_LOG.md`, `notes/crossCuttingFindings.md`
(#9, #10, #13, #17 apply), `writing/US/model_esc.tex` (the specification, Eq `esc:AB`), and the files below.

## 1. The problem

The deadweight cost $f(\theta_t,\tau_t) = \exp\{-\tfrac12\lambda\tau_t\tilde V(1-\theta_t)^2\}$ (spec `'size'`,
`Base.fWedge`) has a zero marginal cost at $\theta = 1$, so the Bismarckian corner is never chosen and France
has no own calibration. Two specs are added, both proportional ($A = f\theta$, $B = f(1-\theta)$) and with
$\ln f$ linear in $\tau$:

| spec | $f(\theta,\tau)$ | parameters | $\partial\ln f/\partial\tau$ |
|---|---|---|---|
| `'size'` (unchanged, bitwise) | $\exp\{-\tfrac12\lambda\tau\tilde V(1-\theta)^2\}$ | $\lambda$ = `db['wedgeP']` | $-\tfrac12\lambda\tilde V(1-\theta)^2$ |
| `'sizeL'` | $\exp\{-\lambda\tau\tilde V(1-\theta)\}$ | $\lambda$ = `db['wedgeP']` | $-\lambda\tilde V(1-\theta)$ |
| `'sizeLQ'` | $\exp\{-\lambda\tau\tilde V(1-\theta)[\kappa + \tfrac12(1-\theta)]\}$ | $\lambda$ = `db['wedgeP']`, $\kappa$ = `db['wedgeKappa']` | $-\lambda\tilde V(1-\theta)[\kappa + \tfrac12(1-\theta)]$ |

$\tilde V$ is `Base.Vtilde` with the same vintage rules as now. `'sizeLQ'` at $\kappa = 0$ is `'size'`;
`'sizeL'` and `'sizeLQ'` at $\lambda = 0$ are the no-wedge model. Under both new specs
$\partial\ln f/\partial\theta|_{\theta=1} = \lambda\tau\tilde V\cdot(1$ or $\kappa) > 0$, so the leaded choice
can be the corner $\theta = 1$; `LeadedBase._argmax` already returns a corner as a corner.

Three calibration kinds are needed on top of the existing `calibrateWedge` (a scan for a sign change of
"design at $t_0$ minus $\theta^{\ast}$", then brentq):

- **interior** (exists): $\lambda$ such that the design in force at $t_0$ is $\theta^{\ast}$, at a fixed $\kappa$.
- **threshold** (new, `ModelESC.calibrateWedgeCorner`): the smallest $\lambda$ at which the design in force
  at $t_0$ is the corner $\theta = 1$. France's own parameter under `'sizeL'` and `'sizeLQ'`.
- **joint** (new, `runESC.calibrateJoint`): under `'sizeLQ'`, $(\lambda,\kappa)$ such that the U.S. design is
  $\theta^{\ast}_{US}$ and a second economy's design is its own observed one, nested: for each $\kappa$ the
  inner `calibrateWedge` gives $\lambda_{US}(\kappa)$; the outer root in $\kappa$ is on the second economy's
  design under $(\lambda_{US}(\kappa),\kappa)$ minus its $\theta^{\ast}$ (`--pinKappa UK`, the UK at its own
  cuts, default) or, with `--pinKappa FR`, the smallest $\kappa$ at which France's design is the corner
  (bisection on the corner indicator, as the threshold kind).

## 2. Files and functions

**`python/US/base.py`** (`fWedge`, `dlnfWedge_dτ`, the comment block of section 2b). Keep the `'size'`
expression verbatim so it stays bitwise; add the two branches; `wedgeA`/`wedgeB` already give $f\theta$ and
$f(1-\theta)$ for every spec but `None`/`'flat'` and need no change beyond the docstring. Read $\kappa$ from
`self.db['wedgeKappa']` only under `'sizeLQ'`.

**`python/US/modelESC.py`.** `WEDGE_SPECS` += the two; `WEDGE_BRACKET['sizeL'] = (0.05, 50.)`,
`['sizeLQ'] = (0.05, 200.)` (under L the marginal cost at $\theta^{\ast}$ is $\lambda\tau\tilde V$ against
$\lambda\tau\tilde V(1-\theta^{\ast})$ under Q, so $\lambda_L \approx 0.26\,\lambda_Q \approx 2.3$ at
$\rho = 1$; under LQ $\lambda \approx 8.64\cdot0.262/(\kappa+0.262)$); `_defaultWedge` gains `'kappa': 0.0`;
`initPars` writes `wedgeKappa`; the `wedge` property returns it; `setWedge(kappa = ...)`. The module
docstring's spec list. New method:

```
calibrateWedgeCorner(self, spec, phi = 0.5, kappa = None, bracket = None, nScan = 10, calKwargs = None,
                     tol = 1e-3, preferences = 'LOG', verbose = True)
```
Scan `bracket` (default `WEDGE_BRACKET[spec]`) on a log grid; at each $\lambda$ call `wedgeResidual` (which
recalibrates $(\beta,\omega)$ and leaves `db` at that point) and record the design at $t_0$
(`residual + θ*`); the corner indicator is `design >= 1 - 1e-6`. Locate the first scan interval whose left
point is interior and right point the corner; bisect in $\log\lambda$ to relative precision `tol`. Return
`{'p': threshold, 'converged', 'scan', 'θ': 1.0, 'residual': 0.0, 'choiceBelow': the design at the last
interior point, 'wedge', 'message'}`, the model left at the threshold. No corner in the bracket, or the
corner already at its left end: `converged = False` with the message saying which.

**`python/US/runESC.py`.** `--spec` choices `('scale', 'flat', 'size', 'sizeL', 'sizeLQ')`; `--kappa`
(float, default None: run `'sizeLQ'` at a fixed $\kappa$, calibrating $\lambda$ only, `kappaFrom = 'fixed'`);
`--pinKappa` (`'UK'` default, `'FR'`). Wedge dicts carry `'kappa'` everywhere a model is built (`buildUS`,
`buildEU`); `pickCalib`'s callers read `kappa` off the row (NaN -> 0.0). New columns per C.5 of the plan:
`escCalibration.csv` `kappa`, `kappaFrom`, `θPin`; `escCountry.csv` `kappa`, `ownKind`; `escPath.csv`,
`escShocks*.csv` `kappa`. Keys unchanged. Branches:

- `stageCalib`: for `'sizeLQ'` without `--kappa`, `calibrateJoint(pin, ...)`: outer scan over
  $\kappa \in \{0, 0.25, 0.5, 1, 2, 4\}$, inner `calibrateWedge('sizeLQ', kappa = κ)` on the U.S. (narrow the
  inner bracket from the previous $\kappa$'s $\lambda$ once one exists), the pinned economy built as in
  `stageCountry`'s U.S.-wedge branch (`buildEU` + `calibrate` + `ESC.solveBackward` + `leadedDesignAtT0`);
  the first sign change of (its design $- \theta^{\ast}$) then brentq in $\kappa$ with `xtol = 1e-3`; under
  `'FR'` the indicator and bisection instead. No sign change (or France's corner unreachable at every
  $\kappa$ scanned): write the row with `converged = False` and the scan printed, and continue. The row
  carries the U.S. readouts as the other rows do plus `kappa`, `kappaFrom`, `θPin` (the pinned economy's
  design at the solution).
- `stageCountry`, the `'own'` branch under `'sizeL'`/`'sizeLQ'`: France -> `calibrateWedgeCorner`
  (`ownKind = 'threshold'`, `p` the bound, `θStar = choice = 1.0`); the UK and UKUS -> `calibrateWedge` at the
  row's $\kappa$ (`ownKind = 'interior'`). Under `'sizeLQ'` the pinning economy's own $\lambda$ should
  reproduce $\lambda_{US}$: print the difference, do not assert.
- `stagePath`, `stageShocks`, `stageFig1`, `stagePermanent`: pass $\kappa$ through; the permanent stage may
  simply refuse the new specs with a message if its calibration path needs more than the wedge dict.

**`python/US/runESCcrra.py`.** Accept the two specs (`--spec` choices, `--kappa` defaulting to the LOG
calibration row's `kappa` for the spec, `BRACKET_CRRA` entries scaled from `'size'`'s by $0.26$ for
`'sizeL'`) so the exact CRRA leg can be run later; no run now.

**`python/US/collectESCexperiments.py`.** `COLUMNS` += `'kappa'`.

**`python/US/test_escVariants.py`** (new fast suite, under three minutes, registered in `python/runTests.py`
after `test_esc.py`; `gridsearch/testing.py`'s `check`/`report`; the test model and `build(ModelESC, wedge)`
as `test_esc.py` uses them). Checks, each a line that fails without the change:
1. `'sizeL'` and `'sizeLQ'` at $\lambda = 0$: `fWedge` $\equiv 1$, `wedgeA` $= \theta$, `wedgeB` $= 1-\theta$,
   `dlnfWedge_dτ` $= 0$ on a grid of $(\theta,\tau)$.
2. `'sizeLQ'` at $\kappa = 0$ equals `'size'` bitwise in `fWedge` and `dlnfWedge_dτ` on the grid.
3. `dlnfWedge_dτ` $= \ln f/\tau$ (identity) and equals a central finite difference of $\ln$ `fWedge` in
   $\tau$ to $10^{-8}$, both specs.
4. $f = 1$ at $\theta = 1$ for every $\tau$, and $f = 1$ for every $(\theta,\tau)$ when $\tilde V = 0$
   (the degenerate distribution of `test_esc.py` S13), both specs (finding #17).
5. $\partial\ln f/\partial\theta$ at $\theta = 1$ by finite difference equals $\lambda\tau\tilde V$ (`'sizeL'`)
   and $\lambda\tau\tilde V\kappa$ (`'sizeLQ'`).
6. `dlnc2i_dτ` under both specs equals its central finite difference at fixed $s_{t-1,i}/s_{t-1}$
   (as `test_esc.py` S10).
7. The corner is reached: under `'sizeL'` at $\lambda = 50$ the design at $t_0$ is exactly 1.0, at
   $\lambda = 0.5$ interior; `calibrateWedgeCorner` returns a threshold between them with `converged`, the
   design just below it interior and above 0.9, and `db['wedgeP']` at the threshold.
8. `calibrateWedge('sizeLQ', kappa = 0.25)` on the test model converges with one sign change in the scan
   and a $\lambda$ below the test model's `'size'` $\lambda$ (`test_esc.py` prints it; a narrow bracket and
   `nScan = 6` keep this under a minute).

**Docs.** `python/US/README.md`: the spec list in "Endogenous θ" and the three calibration kinds, the status
lines; `python/US/RESEARCH_LOG.md`: one entry (at most ten lines). Docstrings cite `Eq esc:AB` and
`esc:Vtilde` as now; the general form's label in the paper will be `eq:esc:fGeneral` (the theorist's note
`notes/esc_variants.md` may rename it; cite `esc:AB` if it has not appeared).

## 3. Reference numbers and checks

- Before the change, run `test_esc.py` and record its calibrated-`'size'` line ($\lambda$ on the test model,
  vector $X$) and the `US_ESC` numbers it prints; after the change the same lines bitwise.
- `python\runTests.py` (the fast suites) all pass; quote the totals.
- One smoke run of the driver on the real model, `runESC.py --spec sizeL --phi 0.5 --commonX --stage calib
  --tag _smoke` (about 2 min), then delete `results/esc/escCalibration_smoke.csv`; quote the $\lambda$ it
  found and the scan's sign changes. Nothing else under `results/` is written.

## 4. Report

As the agent definition says: files and functions, the verdict lines verbatim, the suite totals, the
reference numbers before and after, the smoke run's line, what the brief asked that you did not do and why,
the log entry.
