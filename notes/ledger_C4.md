# Ledger C4: horizon, terminal condition, accuracy and counts (A6)

Package C4 of `notes/plan_reviewResponse.md` (W16), 2026-10-24, on the C1 (U.S., τ0 0.105229) and C2 (Argentina, τ0
0.1181) results. Drivers `python/US/runHorizon.py` and `python/InformalSavings/runHorizon.py`; csvs in
`results/numerical/`; logs `logs/C4/`. Builders `python/paper/tablesHorizon.py` (`NUM_Horizon`, `NUM_Residuals`)
and `tablesOA.numSelection` (`NUM_Selection`, now copied into `writing/Paper` too). Rates in percent, changes in
p.p.; "Δ" is the alternative horizon minus the paper's at the same date.

**Self-checks** (each run, same code path, before any other horizon): U.S. CRRA 2200 rows give the sweep's τ_2020
(0.105229, 1e-6 check); U.S. LOG and exact-CRRA design paths give `escPath.csv` / `escPathCRRA.csv` θ_2020 and
τ_2020 (6e-15; 3.6e-12 at ρ = 0.5); Argentina's 2190 rows give `universal_match_rho*_commonX.csv` τ_2010, baseline
and reform, at ρ = 0.5, 1, 2 (≤ 8.3e-17). Argentina's horizon is changed on the pickled instance (`resize`), equal to
a fresh build from the workbook at every T (0 difference).

**The steady-state terminal condition** is implemented as the infinite-horizon Markov equilibrium of an economy whose
ν stays at its last projected value: the finite horizon extended by 40 periods (to 3310 / 3300). At the paper's T
the tax policy then differs from the next period's by ≤ 1e-15 (U.S.) and ≤ 7.9e-7 (Argentina, ρ = 0.5) over the
visited states, i.e. it is stationary there. Appendix D's text gives the steady state of the economic equilibrium
(s*, Γ_s, B at a constant policy); no solver uses those formulas as a terminal period, and doing so would be new
model code.

## 1. Horizon and terminal condition

Every parameter at its calibrated value at the paper's horizon (U.S. T = 2200: 2140 is two periods shorter, 2290
three longer; Argentina T = 2190: 2130, 2280). Source rows: `US_horizon.csv` (block tax; LOG block design),
`US_horizonDesign.csv`, `ARG_horizon_commonX.csv`, key (block, preferences, ρ, terminal, tss, date).

### U.S., design given (`US_horizon.csv`, block tax)

| ρ | outcome | T 2200, 2020 | 2050 | Δ 2140, 2020 | 2050 | Δ 2290, 2020 | 2050 | Δ steady, 2020 | 2050 |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | τ (%) | 10.5229 | 16.1420 | −0.0006 | +0.0026 | −0.0001 | +0.0005 | −0.0001 | +0.0005 |
| 0.5 | s/Y (%) | 15.7840 | 14.5347 | −0.0005 | −0.0049 | −0.0001 | −0.0003 | −0.0001 | −0.0003 |
| 1 | τ (%) | 10.5229 | 15.7537 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | s/Y (%) | 15.3044 | 14.1536 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | τ (%) | 10.5229 | 15.3901 | +0.0002 | +0.0010 | −0.0000 | −0.0000 | −0.0000 | −0.0000 |
| 2 | s/Y (%) | 14.7677 | 13.7600 | −0.0002 | +0.0004 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |

ρ = 1 (LOG): τ identical (difference 0.0 in floating point) at every date to 2110 and every T, as T2's proposition
says; s/Y identical except at 2110 under T = 2140 (T − 1, whose young save for the terminal period).

### U.S., design chosen (`US_horizonDesign.csv`; ρ = 1 in `US_horizon.csv`, block design)

| ρ | outcome | T 2200, 2020 | 2050 | Δ 2140, 2020 | 2050 | Δ 2290, 2020 | 2050 | Δ steady, 2020 | 2050 |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | θ | 0.727757 | 0.784341 | −0.000007 | −0.000083 | +0.000004 | +0.000007 | +0.000004 | +0.000007 |
| 0.5 | τ (%) | 10.4941 | 15.7568 | +0.0012 | +0.0006 | +0.0001 | +0.0002 | +0.0001 | +0.0002 |
| 0.5 | s/Y (%) | 15.9642 | 14.7647 | −0.0004 | −0.0037 | −0.0001 | +0.0000 | −0.0001 | +0.0000 |
| 1 | θ | 0.727757 | 0.802079 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | τ (%) | 10.5229 | 15.4630 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | s/Y (%) | 15.3663 | 14.2525 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | θ | 0.727757 | 0.785062 | +0.000060 | +0.000085 | +0.000001 | +0.000001 | +0.000001 | +0.000001 |
| 2 | τ (%) | 10.5516 | 15.2886 | +0.0003 | +0.0010 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| 2 | s/Y (%) | 14.7803 | 13.7699 | −0.0002 | +0.0005 | −0.0000 | +0.0000 | −0.0000 | +0.0000 |

The design in force in 2020 (chosen in 1990) is the calibration target at every T (θ* = 0.727757); the cost λ (23.69,
2.459) and (β, ω, X) recalibrated with the cost on at 2200 are held at every horizon. ρ = 1 (LOG, λ 11.564): θ and τ
identical at every date to 2110 and every T. Exact recursion at ns = 150, 41 candidate designs; one equilibrium
and no fallback in the design layer of every row (the tax step is the root layer's, −1).

### Argentina (`ARG_horizon_commonX.csv`; reform = the universal pension, change against the baseline of the same T)

| ρ | outcome | T 2190, 2010 | 2040 | Δ 2130, 2010 | 2040 | Δ 2280, 2010 | 2040 | Δ steady, 2010 | 2040 |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | τ (%) | 11.8121 | 20.1113 | −0.0047 | +0.0283 | −0.0005 | −0.0014 | −0.0031 | −0.0055 |
| 0.5 | s/GDP (%) | 13.8316 | 12.3315 | −0.0030 | −0.0110 | +0.0003 | +0.0002 | +0.0015 | +0.0014 |
| 0.5 | reform Δτ (p.p.) | −0.4199 | +1.7532 | +0.0296 | −0.0156 | +0.0012 | −0.0041 | +0.0045 | −0.0010 |
| 0.5 | reform Δs/GDP (p.p.) | +0.2108 | −0.0584 | −0.0038 | −0.0039 | +0.0003 | +0.0034 | −0.0008 | +0.0024 |
| 1 | τ (%) | 11.8121 | 19.7547 | −0.0003 | −0.0032 | −0.0000 | −0.0000 | −0.0000 | −0.0000 |
| 1 | s/GDP (%) | 13.3272 | 11.5642 | +0.0004 | −0.0006 | +0.0000 | −0.0000 | +0.0000 | −0.0000 |
| 1 | reform Δτ (p.p.) | +1.9500 | +3.4694 | −0.0083 | +0.0208 | +0.0000 | −0.0004 | +0.0000 | −0.0004 |
| 1 | reform Δs/GDP (p.p.) | −0.3642 | −0.4309 | −0.0010 | −0.0022 | +0.0000 | −0.0005 | +0.0000 | −0.0005 |
| 2 | τ (%) | 11.8121 | 18.7960 | +0.0011 | −0.0017 | +0.0000 | −0.0001 | +0.0000 | −0.0001 |
| 2 | s/GDP (%) | 12.7766 | 10.9321 | +0.0001 | −0.0002 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| 2 | reform Δτ (p.p.) | +2.0328 | +3.2896 | −0.0061 | −0.0079 | −0.0005 | −0.0008 | −0.0005 | −0.0009 |
| 2 | reform Δs/GDP (p.p.) | −0.2775 | −0.2530 | +0.0014 | −0.0012 | +0.0001 | +0.0002 | +0.0001 | +0.0002 |

The informal savings ratio ι moves ≤ 2.2e-4 (ρ = 0.5, 2040, T = 2130), ≤ 5e-6 elsewhere. At ρ = 0.5 the 2280 and
steady-state rows differ by up to 0.003 p.p. in τ_2010, which is the grid resolution of that tail (C2: the no-shock
control reproduces τ_2010 to 3.3e-5 there), not a trend.

**Answer.** The calibration year is horizon-robust: from the paper's T to two periods shorter, three longer or the
steady-state terminal condition, the 2020 U.S. tax moves ≤ 0.0006 p.p. and the 2010 Argentine tax ≤ 0.005 p.p.; the
reform's 2010 response ≤ 0.03 p.p. (ρ = 0.5, T = 2130); the chosen design in force in 2020 ≤ 6e-5 (ρ = 2, T =
2140) and in 2050 ≤ 9e-5, with the tax under the chosen design ≤ 0.0012 p.p. Against the steady state
alone (the paper's T versus the infinite horizon) every difference at the calibration year is ≤ 0.005 p.p. One
period later the largest move is 0.028 p.p. (Argentina, ρ = 0.5, τ_2040, T = 2130). Counts: one equilibrium and
no fallback in every horizon row (U.S. tax rule and design layer, Argentina).

**Sentences.** `Numerical.tex:3` "For a large T the two agree away from T": the paper's T and the steady-state
terminal condition agree to ≤ 0.005 p.p. at the calibration year (table above, NUM_Horizon). `TerminalStates.tex:2`
(the reported horizons 2200 / 2190): unchanged, now with the evidence. A6's planned appendix D table ("2020 and 2050
outcomes at T = 2140, 2200, 2290 and under the steady-state terminal condition, for CRRA and informal savings"):
`NUM_Horizon`. T2's prediction for the U.S. LOG rows ("agree to solver tolerance for every T two or more periods
beyond the reading date"): confirmed, exactly.

## 2. First-order-condition residuals off the grid

|τ_FOC(x) − τ̂(x)|, p.p. of the tax, pooled over the periods of the paper's horizon: the root of the period's first
order condition at an off-grid state x (the period's own selection rerun without smoothing, against the solved
continuation) against the policy function there. "As solved": the condition as the solver evaluates it; "converged":
with converged τ-derivatives (U.S.: interpolating spline on 801 tax nodes; Argentina: its own interpolating spline
in ln(1−τ) on 401). `US_residuals.csv`, `ARG_residuals_commonX.csv`, rows `date = all`.

| model | ρ | state grid | path, as solved | visited cells max / p99 | all cells max | path, converged | visited cells max, converged |
|---|---|---|---|---|---|---|---|
| U.S. CRRA | 0.5 | 150 | 3.2e-4 | 0.0064 / 0.0052 | 0.36 | 0.17 | 0.17 |
| U.S. CRRA | 2 | 150 | 1.9e-4 | 0.0011 / 3.5e-4 | 0.72 | 0.37 | 0.38 |
| U.S. CRRA | 0.5 | 50 | 0.056 | 0.12 / 0.11 | 1.9 | 0.21 | 0.38 |
| U.S. CRRA | 2 | 50 | 0.069 | 0.091 / 0.064 | 3.6 | 0.42 | 0.51 |
| Argentina CRRA | 0.5 | 45×45 | 0.0064 | 0.22 / 0.14 | 0.35 | 0.0098 | 0.23 |
| Argentina LOG | 1 | 45 | 0.0012 | 0.0023 / 0.0021 | 0.0028 | 0.0024 | 0.0046 |
| Argentina CRRA | 2 | 45×45 | 0.0082 | 0.014 / 0.011 | 0.014 | 0.014 | 0.029 |

- **As solved** the policy functions are accurate where the path goes: ≤ 3.2e-4 p.p. (U.S., 150 nodes) and ≤ 0.008
  p.p. (Argentina) on the path. Large values sit at states the path never visits (the U.S. grid's edges, up to 0.72
  p.p.; Argentina at ρ = 0.5 in 1920–2010, where the separable 2-D smoothing departs up to 0.35 p.p. from the raw
  selection at nodes as much as at cells). U.S. log preferences have no state: no residual.
- **C1's jumps at ns = 50.** A scan of τ_2020 over ω ± 0.1% (41 points, β fixed; `US_jumps.csv`) shows isolated
  jumps of 2.0e-4 (ρ = 0.5) and 2.3e-4 (ρ = 2) in τ, against a median second difference of 7e-8 and 2e-7: a
  discrete selection change (finding #5). At 150 nodes the largest is 1.2e-8. The residuals see them: at 50 nodes
  the path residual is 5.6e-4 and 6.9e-4 in τ, larger than the jumps; at 150 nodes 3.2e-6 and 1.9e-6, and no jumps.
- **The U.S. τ-derivatives are not converged.** Against converged derivatives the U.S. residual on the path is
  0.17 p.p. (ρ = 0.5) and 0.37 p.p. (ρ = 2), uniform across states: a bias of the condition, not of the
  interpolation. `CRRA.focParts_t` differentiates ln h_t, ln ĉ_{1,t} and ln c̃_{2,t+1} along τ with
  `griddedGradient1D` at its default s = 1e-4 (an absolute residual bound, adaptive knots) on 101 nodes;
  `InformalSavings`' `_gradProfile` differentiates in ln(1−τ), normalised, with s = 0, a fix measured there and not
  carried to the U.S. module (finding #7). The 2020 root at the path state (ρ = 0.5): 0.10523 with the solver's
  scheme at n = 101, 0.10485 / 0.10462 / 0.10451 at n = 201 / 401 / 1601; with s = 0: 0.10469 at 101, 0.10455 at
  1601 (`logs/C4/diag_tauGrid.log`). Whole solves at the calibrated parameters (`US_derivativeScheme.csv`):

| ρ | scheme | τ_2020 baseline | τ_2050 baseline | τ_2020 θ = 0 | τ_2020 θ = 1 | θ 1 → 0, Δτ_2020 (p.p.) |
|---|---|---|---|---|---|---|
| 0.5 | published (n 101, s 1e-4) | 10.523 | 16.142 | 16.439 | 7.101 | +9.34 |
| 0.5 | converged (n 801, s 0) | 10.734 | 15.626 | 16.299 | 7.339 | +8.96 |
| 2 | published | 10.523 | 15.390 | 11.779 | 9.658 | +2.12 |
| 2 | converged | 10.497 | 15.041 | 11.606 | 9.617 | +1.99 |

  A recalibration would absorb the 2020 level (β, ω re-fitted to τ0); the counterfactuals would move by about this
  much. A recalibration under the derivatives as swapped in here (s = 0 along τ) does not converge: `ModelUS.calibrate`'s
  root stalls at a residual of 2e-3 at ρ = 0.5 (`logs/C4/US_schemeRecal.log`), so the fix is `_gradProfile`'s whole
  treatment (ln(1−τ), per-profile normalisation), not s = 0 alone. Not fixed here: it is a change to
  `python/US/policy.py` (and the exact design recursion, `LeadedCRRA2D`, inherits the same `focParts_t`), then C1's
  CRRA reruns.

**Sentences.** A6's "first-order-condition residuals off the grid" (W8): on the path the policy functions solve
their first order condition to 3e-4 p.p. (U.S.) and 0.008 p.p. (Argentina) of the tax as solved; the converged
columns of `NUM_Residuals` are what a referee would read as the residual, and for the U.S. they say 0.17–0.37 p.p.
until the derivative scheme is fixed. Section 6 `OECD.tex:40` (θ: 1 → 0, Δτ +9.3 / +2.1 p.p. at ρ = 0.5 / 2) and the
A9 ranking at ρ = 2 (design 2.12 against voting 1.87, `ledger_C1.md`) rest on the published scheme.

## 3. Candidate counts (`NUM_Selection`)

Per csv the rows, counted rows, rows with −1 (the solve selects nothing at that layer), rows with blanks (written
before the counts existed), and over counted rows the largest number of equilibria, of candidates, and the fallbacks.
`datasets.countSummary`/`countExceptions`; the table's note is built from them.

- **Every counted row: one equilibrium at every state and period.** Candidates at most 3 (the two corners and one
  crossing) in the tax rule, one bracket in the design layer.
- **One fallback**: the design layer of `escShocksCRRA.csv`, ρ = 2, the paper's cost, all French characteristics,
  design chosen, exact recursion (one state).
- **No selection (−1), tax rule**: the economic-equilibrium rows (`eeOnly_*`: 112 + 112; `US_shocks*`, `UK_shocks*`:
  24 each); the exact CRRA recursion with the design chosen, whose tax step is selected inside the design layer
  (`escCalibrationCRRA` 4, `escCalibrationCRRAUK` 2, `escShocksCRRA` 27, `escShocksCRRAUK` 14, `escPathCRRA` 32,
  `US_ESC_stationaryApprox` 18, `US_horizonDesign` all its rows); failed cost calibrations (`escCountry.csv` 3:
  France under both costs, the regrouped UK under the cost on the design).
- **No selection, design layer**: the pinned-design rows (`escShocksCRRA` 32, `escShocksCRRAUK` 16) and the LOG rows of
  `US_ESC_stationaryApprox` (9).
- **Not recorded (blank)**: the earlier cost on the design (`scale`, method blank) and the path iteration
  (`method = path`) in `escCalibrationCRRA` (4), `escShocksCRRA` (60), `escPathCRRA` (16): the cross-check the
  exhibits do not read, not rerun by C1, so stale as well as uncounted.
- New rows: `US_horizon` 96, `US_horizonDesign`, `ARG_horizon_commonX` 84, `US_derivativeScheme` 24, all one
  equilibrium, no fallback.

**Sentences.** `Numerical.tex:7` footnote ("exactly one passes at every state and date of every solve that records
the count"): true for the equilibria; the one design-layer state where none passed is a fallback and must be named
(T2's §7.2 footnote text for W2 needs "except one state of the design layer, where none passed"). T2's §7.3 appendix D
paragraph (for W8): "the largest number of candidates and of equilibria at any state and date" is `NUM_Selection`;
"its count is at least two" holds for the tax rule (3), not for the design layer, whose candidates are brackets (1).

## 4. Open for checkpoint 2

1. The U.S. CRRA τ-derivative scheme (section 2): a model-code fix in `python/US/policy.py` (`focParts_t`, as
   `InformalSavings._gradProfile`), then C1's CRRA sweeps, shocks and exact ESC reruns. Until then the converged
   columns of `NUM_Residuals` show 0.17–0.37 p.p.
2. The steady-state terminal condition is the infinite-horizon limit (40 appended periods), not appendix D's
   closed-form steady state as a terminal period; W8 should describe it so.
3. `NUM_Selection` is now copied into `writing/Paper` (appendix D) and keeps its `table:OA:` label.
