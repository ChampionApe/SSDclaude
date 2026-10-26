# Brief C6: converged derivatives and design grids in the U.S. solvers (A6, after checkpoint 2)

Package C6 of `notes/plan_reviewResponse.md` (W16), decided at checkpoint 2 (RKB, 2026-10-24: fix before any
writing). Agent: model-coder. Branch `review-2026-10`, from commit f3a15a4. The reruns follow with paper-compute.

## 1. The CRRA tax condition's τ-derivatives (`notes/ledger_C4.md` §2, lines ~100-150)

`policy.CRRA.focParts_t` (`python/US/policy.py`) differentiates ln h_t, ln ĉ_{1,t} and ln c̃_{2,t+1} along τ with
`griddedGradient1D` at its default s = 1e-4 on 101 nodes. They are not converged:
- the path residual against converged derivatives is 0.17 / 0.37 p.p. at ρ = 0.5 / 2;
- the θ 1→0 effect moves 9.34 → 8.96 p.p. (ρ = 0.5) and 2.12 → 1.99 (ρ = 2) at the calibrated parameters (`results/numerical/US_derivativeScheme.csv`, `logs/C4/diag_tauGrid.log`).

C4 swapped in s = 0 alone, and `ModelUS.calibrate` then stalled at a residual of 2e-3 (`logs/C4/US_schemeRecal.log`).
Argentina's `_gradProfile` (`python/InformalSavings/policy.py`) uses ln(1−τ) with per-profile normalisation and
s = 0, a fix measured there.

**Task.**
- Bring that treatment, or an equivalent you can show converges, into the U.S. CRRA path. `LeadedCRRA2D` and the exact design recursion inherit `focParts_t` and must get it too.
- Show convergence: τ_2020 and the θ 1→0 gap at n = 101/201/401/801 tax nodes, against C4's 801-node spline reference.
- Show that `ModelUS.calibrate` converges at ρ = 0.5, 1 and 2 (one calibration point each, residual ≤ 1e-8 or the module's tolerance).
- LOG is not affected (closed-form path). Check that it stays bitwise.

## 2. The log design choice's anticipated-tax table (`notes/ledger_C5.md` lines ~187-194)

`LeadedLOG` reads T_{t+1}(θ) off a piecewise-linear table on its 41-node design grid (`ModelESC(nθ = 41)`). At
λ = 11.564, θ_2020 is:
- 0.7278 at 41 nodes;
- 0.7311 at 81;
- 0.7321 at 161;
- 0.7323 at 321;
- 0.7324 with T solved at each candidate.

**Task.**
- Remove the bias: solve T at each candidate where that is cheap under log (it is closed-form at given θ), or use an interpolant whose error at the calibrated design is ≤ 1e-5 in θ.
- Then measure the same error for the exact CRRA recursion's 13-node θ-state grid (`LeadedCRRA2D`) at ρ = 0.5 and 2: θ_2020 at 13 against 25 and 49 nodes.
- If that error exceeds 1e-3, raise the default and report the cost per solve.

## 3. Follow-up after the reruns: Turkey's layer-2 CSES row in the 26-country test (2026-10-25)

`python/US/runOECD26.py`, layer 2, CSES turnout, Turkey: "ValueError: The function value at x=1e-06 is NaN;
solver cannot continue". The tax reaches 1 at the lower bracket of the ω root. The row was ok at f3a15a4 and fails
deterministically on the C6 code (`logs/C6runs/oecd26.log`, `oecd26_TURretry.log`), so `US/test_oecd26.py` fails
(fast suites 28/29).

**Task.**
- Find why the C6 code produces a NaN where the f3a15a4 code did not. Suspects: `_gradProfile`'s ln(1−τ) as τ → 1,
  or `LeadedLOG.taxes_t` at candidates.
- Fix it in the model code so the condition stays finite, or so the bracket is handled as the solver handles
  bounds elsewhere. Do not widen tolerances, and do not special-case a country.
- Add a test that fails on the current code.
- Rerun Turkey's layer-2 CSES row, then `runOECD26.py` for whatever its resume logic needs (not `--force` over
  the whole test unless the fix changes other rows; if it does, say which).
- Pass `US/test_oecd26.py`, `test_gridConvergence.py` and the fast suites.
- Report whether any other result csv would move. If one does, list it; do not rerun it.

## Tests

Script style, registered in `python/runTests.py` if fast:
- each fix has a test that fails on f3a15a4's code: derivative convergence at a CRRA state, and θ_2020 at the log calibration against the per-candidate solve;
- the existing U.S. suites pass. Their reference numbers will move: update them, and list every moved reference with old → new.

## Files

May touch:
- `python/US/{policy.py, policyESC.py, modelESC.py, model.py, base.py}`;
- U.S. tests and `python/runTests.py`;
- `python/US/RESEARCH_LOG.md` and `README.md` (its open-issue bullets for these two findings).

Not `python/paper`, `results/`, `writing/`, `python/InformalSavings` (read only), `python/gridsearch` (stop and report if needed).

## Done when

- The fast suites pass.
- The report gives:
  - the convergence tables above;
  - the per-solve cost before and after (wall time of one CRRA calibration point and one exact design solve);
  - the exact list of reruns paper-compute must do (stages, drivers, flags, `--force` where needed);
  - an estimate of their wall time at 4 cores with at most 5 solver processes.
