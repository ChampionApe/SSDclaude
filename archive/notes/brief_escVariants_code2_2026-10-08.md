# Brief: the linear term's weight, second coder pass (phase B, gate 1 amendment)

For the `model-coder` agent, after `notes/brief_escVariants_code_2026-10-08.md` was implemented (the top
entry of `python/US/RESEARCH_LOG.md`). Plan: `notes/plan_endogenousDesign.md` §C.1 decision 1 (the
amendment) and §C.5. The reason is in `notes/esc_variants.md`, "Overturned" item 2 and §1.4: weighting the
linear term by $M = \sum_i\gamma_i|y_i-1|$ instead of $\tilde V$ leaves the U.S. and UK calibrations
unchanged and brings France's corner within reach of the U.S. calibration.

## 1. The change

| spec | $\ln f(\theta,\tau)$ | $\partial\ln f/\partial\tau$ |
|---|---|---|
| `'size'` (unchanged, bitwise) | $-\tfrac12\lambda\tau\tilde V(1-\theta)^2$ | as now |
| `'sizeL'` (now $M$) | $-\lambda\tau M(1-\theta)$ | $-\lambda M(1-\theta)$ |
| `'sizeLQ'` (now $M$ on the linear term; the paper's) | $-\lambda\tau(1-\theta)\big[\kappa M + \tfrac12\tilde V(1-\theta)\big]$ | $-\lambda(1-\theta)[\kappa M + \tfrac12\tilde V(1-\theta)]$ |
| `'sizeLQV'` (new name for what `'sizeLQ'` is now; the record) | $-\lambda\tau\tilde V(1-\theta)\big[\kappa + \tfrac12(1-\theta)\big]$ | as implemented |

with $M$ a new `Base.Mabs(t, lag)` beside `Vtilde`: $\sum_i\gamma_i|y_i-1|$, $y_i$ = `hηRatio`, zero-mass
slots masked before the product, memoised, the same vintage rules (`lag`). $M = 0$ when $\tilde V = 0$; $M$
is invariant to the two normalisations as $\tilde V$ is. Under `'sizeLQ'` at $\kappa = 0$ the result is
`'size'` bitwise (the $\kappa$ term is a separate summand, as you implemented it).

## 2. Files

- `python/US/base.py`: `Mabs`; the three branches of `fWedge` and `dlnfWedge_dτ`; the section 2b comment
  (one line per spec, the weight named).
- `python/US/modelESC.py`: `WEDGE_SPECS` and `WEDGE_BRACKET` (`'sizeLQV'` as `'sizeLQ'`'s; `'sizeL'`'s
  bracket unchanged: $\lambda_L$ under $M$ is $0.76\,\lambda_L$ under $\tilde V$ for the U.S.); the module
  docstring's spec list.
- `python/US/runESC.py` and `runESCcrra.py`: `--spec` choices += `'sizeLQV'`; `calibrateJoint` and
  `stageCountry` treat `'sizeLQV'` as `'sizeLQ'`; `wedgeReadout` writes `Mabs` (every row that carries
  `Vtilde`). Under `--pinKappa FR` the bisection in $\kappa$ now has a solution (§4.4 of the note:
  $\kappa \approx 1$); make sure the outer scan's upper end (4) is above it and that the indicator is the
  corner at $t_0$ on France's freely simulated path, as the threshold kind defines it.
- `python/US/test_escVariants.py`: update checks 1-8 for the weights (check 5: $\lambda\tau M$ under
  `'sizeL'`, $\lambda\tau M\kappa$ under `'sizeLQ'`, $\lambda\tau\tilde V\kappa$ under `'sizeLQV'`); add: `Mabs`
  equals its definition on the test model and is invariant to a common rescaling of $X_i$ and of $\eta_i$,
  and is 0 for the degenerate distribution; `'sizeLQ'` and `'sizeLQV'` differ by the factor $M/\tilde V$ in
  the linear term of $\ln f$ (check it on the grid); the test model's $M$ printed beside its $\tilde V$.
- README (the spec table of "Endogenous θ") and the US log entry (extend yours, at most ten lines in all).

## 3. Checks

`test_esc.py`'s calibrated-size line bitwise as before (`lambda=8.643207 residual=1.4e-08`); the fast
suites; one smoke run `runESC.py --spec sizeL --phi 0.5 --commonX --stage calib --tag _smoke` (expect
$\lambda_L$ near $0.76\times2.255 \approx 1.7$), then delete the tagged csv. Report as before, at most 15 lines.
