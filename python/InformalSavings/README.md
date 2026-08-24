# InformalSavings

Informal savings model: overlapping generations with `J+1` household types where type 0 ("informal") now
**saves** through an informal vehicle, rather than being hand-to-mouth. Informal savings earn
`R_t^0 = R_t·χ_t^R` and stay **out of the formal capital stock**. Full derivation in
`writing/informalSavings/` (`model*.tex` = model/equilibrium definitions, `num*.tex` = numerical solution
approach — tex labels like `eq:auxiliary:s0_s` are referenced throughout the code's docstrings).

## The one structural consequence that drives everything

`ι_t ≡ s_{t,0}/s_t` (the informal savings ratio, docs `eq:auxiliary:s0_s`) depends on `τ_t` through
`Θ_{s,t}`. Unlike `s_{t,i}/s_t`, which reduces to a closed-form function of `τ_{t+1}` alone, `ι_{t-1}` is
**an endogenous state of the political problem**. So:

- **The economic equilibrium is unchanged.** `Γs`, `Θh`, `Θs`, `s`, `h`, `si_s`, `κ`, `bbar` all sum over
  `i>0` only and never see `s_{t,0}`. `ι_t` is a closed-form read-off of the solved core `(s,h,Γs,B)`,
  **not** part of any root problem. `EE_LOG_solve`/`EE_CRRA_solve`/`steadyState_*` needed no change.
- **The politico-economic equilibrium changes completely.** Even under LOG there is now a state, so the
  triangular `z_t = z_t(τ_t, τ_{t+1})` structure is gone and with it the whole-path simultaneous solve.

## Timing convention
Docs: time runs `t=1,...,T`; `t=0` is a pre-determined state taken as given (or via a steady-state
assumption). Code: `db['t']` defaults to `0,...,T-1`.

| Docs | Code |
|---|---|
| `t=0` (pre-determined) | the `s0` function argument (state *before* `db['t'][0]`) |
| `t=1` (first active period) | `db['t'][0]` = `Base.tFirst` |
| `t=T` (terminal period) | `db['t'][-1]` |

Two db entries share names with the above by coincidence: `db['s0']` is the savings **rate** at the
baseline year (reported; it identified `β` until 2026-08-24, when `db['KY0']`, the capital-output ratio,
replaced it as the target); `db['t0']` is the *index* of the calibration baseline year.

## Files
Every `test_*.py` is a standalone script: it prints one PASS/FAIL line per assertion and exits nonzero on
any failure, via the shared harness in `gridsearch/testing.py` (which also forces UTF-8 stdout — the tests
print Greek). Run them individually, or through `python/runTests.py` (`--all` to include the slow ones).

- `base.py` — `Base`/`BaseGrid`/`BaseTime`: the economic-equilibrium equations, each method named after its
  tex doc label. `Base` = scalar/single-year, `BaseGrid` = single year/grid-valued, `BaseTime` = vectorized
  over all `t`.
- `model.py` — `ModelInformalSavings`. Database/parameter scaffolding (§0-2); EE solve given a policy path
  (§3); steady state (§4); initial state (§5); calibration (§8).
- `policy.py` — `LOG`/`CRRA`. Both solve the full backward recursion: `LOG` over the single state `ι_{t-1}`,
  `CRRA` over the pair `(s_{t-1}, ι_{t-1})`. See Implementation status.
- `test.py` — loads `data/ArgentinaTest.xlsx` and builds `mLOG = ModelInformalSavings(pars=pars, **kwargs)`
  with the real Argentina calibration. Standard way to get a non-degenerate instance (a bare
  `ModelInformalSavings()` has identical household types, giving `NaN`/`inf` `θ`/`κ`/`ε` — expected).
- `test_ee.py` — 36 checks at `ρ=1` and `ρ=1.15`. Rebuilds every consumption level from the **primitive**
  FOCs/budgets (`eq:formalOpt`/`informalOpt`/`formalBudget`/`informalBudget`/`governmentBudget`) and
  requires the closed forms to reproduce it, plus the PAYG balance and the aggregation identities.
- `test_peeCRRA.py` — 35 checks on `policy.py`'s `CRRA` class. The sharpest is exact rather than
  approximate: at `ρ=1` every level factor collapses to `c^0=1` and `B_T^i` to `β_i`, so
  `CRRA.solveTerminal` *is* `LOG.solveTerminal` at every state (matched to 5.6e-17, and independent of
  `s_{T-1}`). Then, at `ρ≠1`: `z_T`/`z_t` against a primitive rebuild of `W_t`, the two grid roots against
  an exact nested `brentq`, and the residuals against grid refinement — which is what separates
  "grid-limited" from "wrong".
- `test_peeLOG.py` — 52 checks on `policy.py`'s `LOG` class. Same standard as `test_ee.py`: `z_t` is
  checked against a finite difference of the political objective `W_t` **rebuilt from the primitives**
  (machine precision at `T`, ~1e-3 relative below it — see Conventions), plus `eq:zdecomposition` against
  a pointwise evaluation of the full product, the numerical `dυ_1/dτ` against the closed form that exists
  only when the continuation policy is held constant, the state fixed point's residual, and the `ε=0`
  degeneracy in which the state provably drops out.
- `test_calibration.py` — 36 checks on §8. The four target quantities against a rebuild from the solved
  path's primitives; that `_calSetPars` moves `auxProd0` but **not** `Γh` (the informal write must not leak
  into the formal aggregate); that the state grids are rebuilt per residual evaluation *and* genuinely move
  with `η0`; the outer Jacobian's step (see Conventions); the LOG convergence and all four targets; `ι_{t0}`
  in `(0,1)` and inside `𝒮_0`; and the CRRA cross-check at `ρ=1.02` with its grid-refinement pair. That
  cross-check runs at `cubic`+`smoothKnots=4`, **not** at the PEE defaults: at the defaults it fails at
  *any* outer step (the three-configuration table is in its own comment). Slow (~12 min) — four LOG
  calibrations and one CRRA.
- `test_calibrationGrid.py` — checks on §8.1's `calibratePoint`/`calibrateGrid`. Deliberately narrow:
  `gridsearch/test_continuation.py` already covers the march's logic against fake solves, so this file
  only covers what that cannot see — that the adapter installs the parameter and picks the solver, that
  that neither solver overrides scipy's outer step, that keyed grid settings leave the unnamed solver
  alone, and that a *real* calibration still hits `eq:calibration` at every point of a three-point
  grid. Slow (~45 min): three real calibrations plus a refined verification at each, and a cold CRRA
  calibration to measure what the warm start is worth.
- `calibrateRhoGrid.py` — the sweep script (not a test). Resumable: reads its own CSV back and returns
  already-solved `ρ` from it without re-solving, so a resumed march is no worse warm-started than an
  uninterrupted one — which also means a re-run under changed settings needs a **new `--out` or `--force`,
  or it will silently return the old rows**. `--out` is relative to this directory (the script `chdir`s so
  `test.py` finds `data/`). Run `--help` for options; `--interpKind` defaults to `cubic` for the reason in
  Conventions; `--smoothKnots` now defaults to 4, with `0` the way back to the adaptive smoother.
- `retargetCalibration.py` — β (and ω, η0, X0) as a function of ONE calibration target, holding
  everything else (not a test). `--par KY0` by default; each point is a full calibration warm started
  from the previous one, ~8 s per point at ρ=1. It is what makes the target's consequence legible rather
  than asserted — `results/calibration/informalSavings_KYGrid.csv` is the β(K/Y) map behind the choice of
  reading in `notes/argentina_calibrationTarget.md`. Loads a pickled instance and fills in any 0-D
  parameter added since it was pickled, so it still runs against instances from before `KY0` existed.
- `shockUniversal.py` — the unanticipated-universalisation experiment (not a test; docs `num_shock.tex`).
  Baseline solve → `stateAtT0` → `createCopyFromt0(t0)` → new `ε` → re-solve from that state. The default
  run is `--rule match --refType 1` (`b^0 = b^1`); `--rule flat` is `ε = 1-θ`, the non-contributive
  component only, which on this calibration falls on the *other* side of the status quo, so the two
  bracket it rather than differing in degree (`ε`: 0.305 → 0.546 vs → 0.161, and every response flips
  sign). Two things it must do that a bare `ε=` argument to `solvePEE_*` would not — rewrite `db['eps']`
  **and** `db['κ']` (the `κ` staleness under "Known limitations" below is live here, not latent), and
  rebuild `db['κ[t-1]']` at the copy's first period from the *new* `ε_{t0}`, since `_sliceDb` restricts
  rather than recomputes and `b̄_{t0}` is what pays the reformed benefit to the already-old. Both are
  currently invisible (`p`/`γ0` constant, `ε^U` flat) and stop being so the moment either varies over `t`.
  `--control` runs the no-shock round trip first; the `b^0/b^j` identity is checked on the solved path
  every run.
- `shockEEOnly.py` — the same reform with **taxes held at the baseline path** (not a test). This is the
  decomposition's other half: it isolates the pure economic-equilibrium response, which for the savings
  rate runs *opposite* to the full effect (+0.72% against −0.97% at `ρ=1`), while for labour supply it is
  the same sign and about a third of the size. Cheap — taxes are exogenous, so it is one `EE_*_solve` per
  `ρ` and no policy recursion at all (well under a minute for all 16 points against ~2.5 h for
  `shockUniversal.py`). Reads the baseline `τ` path off `shockUniversal.py`'s own csv rather than
  re-solving it (`--resolveBaseline` forces the re-solve; the shortcut is bitwise exact, but **only when
  the csv is read with `float_precision='round_trip'`** — the default C parser is ~1 ulp off). Output
  mirrors `universal_*.csv` with `_reform` → `_ee`, plus `s__base`/`s__ee` (the lagged savings level,
  which no other csv carries and which `python/paper/` needs for the savings rate) and `sr_*`.
  `--control` re-runs it with `ε` unchanged and is what found the `EE_report` proxy defect under Known
  limitations; it is cheap and doubles as the CRRA warm start, so keep it on.
- `sweepEpsThetaGrid.py` — comparative statics on a full **cartesian `(ε, θ)` grid** at the calibrated
  `ρ=1` instance (not a test), behind `writing/Paper`'s `ARG_LOG_FourInOne` figure, which plots one `ε`
  curve per `θ` and shades between them. **Not a recalibration**: `β`/`ω`/`η0`/`X0` stay pinned, so the
  status-quo row reproduces the calibration exactly (τ to 5.6e-11, savings rate to 1.9e-11). ~1.1 s per
  point; the default 27×14 grid is ~5 min. `ε` is installed only through `shockUniversal.installEps`,
  never as a bare `eps=` argument — `κ_t(ε_{t+1})` is consumed through a cached `db['kappa']`, and a
  mutually inconsistent `(ε, κ)` violates no equilibrium condition, so nothing raises. **`ε` does not
  track `θ`**: `model.getEps` makes `ε` a decreasing function of `θ`, so following that chain would
  collapse the product grid onto a curve and leave no `θ`-family to plot. `solvePoint` asserts the
  `(ε, θ)` actually in `db` is the pair asked for, and both are recorded on every row. Resumable on its
  own csv, with `calibrateRhoGrid.py`'s caveat: a re-run under changed settings silently returns the old
  rows unless given a new `--out` or `--force`.
- `plotUniversalShock.py` — plots one response series (`--series`, default `d_τ`) from `shockUniversal.py`'s
  per-`ρ` CSVs against `ρ`, at a chosen number of periods after `t0` (`--period`, default 0 = impact; a
  plain positional row offset, since each CSV is already indexed on the model's own `t` starting at `t0`).
  Not a test. `results/shocks/delta_<series>_vs_rho_<rule>_t<period>.{png,pdf}`.
  **Filenames must match `universal_<rule>_rho<number>.csv` exactly, and a duplicate `ρ` raises** — see
  Conventions on superseded files. Superseded runs belong in `results/shocks/preInterpFix/`, not beside
  the live ones.
- `diagnoseLogCrraBoundary.py` — the `ρ=1` boundary diagnostic (not a test). Six selectable `--test`s:
  `limit` (the `ρ→1` limit of CRRA against LOG at fixed parameters), `refine`, `settings` (which grid
  setting carries the jump), `cal`, `path`, `shock`. `--mode common|production` is the point of it — under
  `common` both solvers get identical grid settings, isolating the *method*; under `production` each gets
  what the sweep actually hands it. Any measurement that does not hold `nι`/`interpKind` fixed across the
  boundary measures their sum and attributes it to the recursion.
- `plotBoundary.py` — overlays `--test shock`'s two modes against `ρ`, marking where the CRRA points say
  the anchor should be. `results/boundary/d_tau_t0p1_vs_rho_match.{png,pdf}`.
- `measureOuterSettings.py` — offline re-measurement of the calibration's solver settings (not a test):
  `--test jac` the outer Jacobian across finite-difference steps at converged points, `--test eps` a real
  calibration at each candidate step from a common start, `--test grid` a calibration at each inner grid
  size plus the refinement ladder at fixed parameters. Produced deviations note items 11-12; re-run it after
  any change that could alter the outer residual's smoothness.
- `measureGrids.py` — offline measurement feeding the grid rule (not a test): reachable box, occupancy,
  feasibility/`atBound`, and the anchor comparison, across pickled calibrations. `--legacy` reproduces the
  pre-2026-08-19 rule through `initGS`' override slots so the two can be compared on one code path.
- `diagnoseRho07.py` — the four diagnostics that located the residual discontinuity (not a test): Jacobian
  conditioning and column stability at converged points, a fine residual scan for jumps, and a diff of
  every discrete choice across one. Kept because the chain is worth re-running, not re-deriving.
- `test_peePath.py` — 41 checks on the path solve (`model.py` §6-7). The initial fixed point's residual and
  the fact that it is *not* the degenerate root at the top of `𝒯` (see Conventions); the walk's `τ_1`
  against the fixed point's own; the containment guards; and the docs' grid diagnostic — the simulated
  state against the exact re-solve, asserted against the state grid's spacing rather than a tolerance,
  since the question is whether the walk resolves the state to inside a cell. It does not rebuild the path
  from the primitives — the exact step is `EE_*_solve`, whose primitive checks are `test_ee.py`.
- `test_createCopyFromt0.py` — `_sliceDb` on synthetic db entries (restriction + 0-based renumbering,
  every index shape, shared verbatim with `informalAnalytical`); `createCopyFromt0`'s structural
  consistency on the real calibrated instance (`db`/`T`/`tFirst`/`x0`/`db['t0']`, both branches, the
  out-of-range `ValueError`); a behavioral round trip — with no actual shock,
  `mt0.solvePEE_LOG(**stateAtT0(...))` reproduces the baseline's own `s`/`h`/`ι` tail at `t0` and later;
  and `stateAtT0`'s `ι0` asymmetry specifically (see "Model copies for shock experiments" below) via a
  sentinel `init['ι']` that only fires at `t0 == db['t'][0]`. 36 checks.

## Informal-savings objects (`base.py`)
| Method | Doc | Note |
|---|---|---|
| `R0(s_,h,t)` / `Rlead0(s,h1,t)` | `factorPrices0` | `R·χ^R`; `Rlead0` uses `χR[t+1]` |
| `B0(s,h1,t)` | `auxiliary:B0` | collapses to primitive `β0` at `ρ=1` |
| `auxInf1(ε1,t)` / `auxInf1_(ε,t)` | `auxiliary:Ainf` | forward (`χR[t+1]`) / lagged (`χR`) pension coefficient |
| `s0_s(B0,Θs,τ1,ε1,t)` | `auxiliary:s0_s` | `ι_t` |
| `h0(s_,t)`, `c10`, `tildec10` | `informalOpt`, `EE:c0` | `c10`/`tildec10` take `(s_, s, B0, τ1, ε1)` |
| `c20`, `tildec20` | `EE:c0` | `tildec20 == c20` (informal old supply no labour) |
| `hatc10Pow`, `lnhatc10` | — | informal twins of `hatc1iPow`/`lnhatc1i`, same overflow-safe forms |
| `B0SteadyState`, `RpSteadyState` | `steadystate_CRRA:Bi` | `RpSteadyState` factored out of `BSteadyState` |
| `FH_c10`, `FH_tildec10` | `TerminalEE` | terminal collapse via `B0=0` padding |
| `lnRleadΘ(Θs,Θh1)` | `auxiliary:R` + `logsep` | `ln R_{t+1}` up to a `τ_t`-constant — why the recursion carries `Θ_{h,t+1}`, not `h_{t+1}` |
| `tildec10Θ(Θs,B0,τ1,ε1)` | `EE:c0`/`EE:sigma_ci` | `c̃_{1,t}^0`'s coefficient function (`c̃1i`'s twin is just `tildec1i(Θh,…)`) |

## Political-FOC objects (`base.py` §9)
| Method | Doc | Note |
|---|---|---|
| `dlnc2i_dτ(dlnh,τ,θ,si_s_)` | `PEELOG` | ported unchanged from `informalAnalytical`; closed form is **mandatory** |
| `dlnc20_dτ(dlnh,τ,ε,ι_)` | `dv20` | new: `(1-α)dlnh + A_t/(ι_+A_tτ)`, takes the state `ι_` instead of `Θh` |
| `dlnΘhTerminal_dτ`, `dv1iTerminal_dτ_LOG` | `terminalPEELOG` | terminal only; `dv1i` returns `(M,1)` to broadcast inside `FOC` |
| `v1iProfile_LOG`, `v10Profile_LOG` | `v1LOG` | `υ_1` up to an additive `τ_t`-constant, for numerical differentiation |

## Conventions and traps
- **`hRatio` vs `hηRatio` (`base.py` §0).** Two ratios differing by a factor `η_{t,i}`:
  `hRatio = h_{t,i}/h_t = (η/X)^ξ/Γh` (doc `eq:EE:hi`) and `hηRatio = h_{t,i}η_{t,i}/h_t = auxProd/Γh`.
  `hi`/`bi` need the first; `si_s`'s third term, `c2i` and `dlnc2i_dτ` need the second (the doc writes
  `η^{1+ξ}/X^ξ` over `Γh` in all three). Conflating them is a real bug that was live in both modules —
  see the 2026-08-10 research-log entries. Sanity checks: `∑γ_iη_i·hRatio_i = 1` and `∑γ_i·hηRatio_i = 1`.
- **`χ^R` carries a *period* index, not a generation index.** `R_t^0` is the return earned between `t-1`
  and `t`, so `ι_t`/`c10`/`tildec10` use `χ^R_{t+1}` (they discount `b_{t+1}^0`) while `c20`/`dv20` use
  `χ^R_t`. The docs originally wrote `χ^R_t`/`χ^R_{t-1}` in those two places — fixed 2026-08-10. Verified
  with a time-varying `χ^R`, so it is not an untested convention.
- **Reporting domains.** `Γs`/`B`/`B0`/`si_s`/`ι` report at length `T-1` (`db['txE']` — all genuinely
  undefined at `T`, where `s_T=0` makes both ratios `0/0`); everything else stays length `T`. `_wrapVars`
  looks each name up in the class-level `_t2vars`/`_txE2vars`; a name in neither raises `KeyError`.
- **Explicit vs. db-sourced.** Primitives (`α, ξ, ν, γ, η, X, β, p, κ, χR, Γh, ...`) are read from db.
  Anything solve/policy-dependent — `τ`, `θ`/`ε`, `s`/`h`, `B`/`B0`, `ι` — is always an explicit argument.
- **`initialState_solve(τ, θ, ε, t)`** now takes `ε` (it needs it for `ι_{-1}`) and returns
  `{'Γs','B','B0','si_s','ι'}`. `h_{-1}` is still computed only where needed (`EE_report`, via `hFromS`).
- **`cacheParams()`** (`base.py`) is opt-in and block-scoped, memoising db reads while a year is held
  fixed (~6.5x per evaluation, flat in grid size). Deliberately not always-on: `model.py` rewrites whole db
  symbols during calibration and a surviving cache would return stale parameters *silently*.
- **Differentiate along `ln(1-τ_t)`, not `τ_t`** (`policy.py`'s `_gradProfile`). Every profile carries a
  `ln(1-τ_t)` term, so `dy/dτ` diverges like `1/(1-τ_t)` and a spline through uniform `τ` nodes cannot
  represent it: measured against the closed form available at a fixed continuation policy, a raw-`τ` fit is
  off by ~1e-2 near the top of `𝒯` and ~1e-3 in the interior, versus ~1e-15 in `x = ln(1-τ_t)`. Do not
  "simplify" this back to a direct `griddedGradient1D(τGrid, …)` call.
- **Smoothing the *derivative* hurts** (same method). `s>0` there is 3-10x worse than an interpolating
  spline — the profiles are smooth in `x`, and what is left is the piecewise-linear continuation
  interpolant's kinks, which smoothing blurs rather than removes. The doc's smoothing advice applies to
  `τ_t(ι_{t-1})` before interpolation (`solveBackward_t`'s `smooth`), which is a different object.
- **`z_t`'s accuracy at `t<T` is ~1e-3 absolute**, floored by those kinks (cubic continuation interpolation
  halves it). That is well under 1/20 of a `τ`-grid cell in the located policy, so the grid, not the
  differentiation, is what limits the solution — which is the form the tests assert it in.
- **The policy smoother's knots must be pinned (`smoothKnots`), not chosen from the data.** The default
  `None` keeps `UnivariateSpline(s=1e-5)`, whose FITPACK knot *count* is chosen from the data and so flips
  discontinuously as a parameter moves — ~3.5e-6 jumps in the calibration's outer residual, which is what
  made `ρ≈0.7` uncalibratable. `smoothKnots=m` fits fixed knots every `m`-th valid node instead, making the
  smoother a linear map of its input (hence continuous), and is ~2.4× faster. **`smoothKnots=4` is the
  default since 2026-08-19** (it was `None` until then, to reproduce pre-retune results bitwise; those are
  all superseded). Unlike `nι`/`ns`/`interpKind` — resolution choices the CRRA calibration needs and LOG
  does not — this one is about well-posedness, which is why `calibrateRhoGrid.py` keys it on `'LOG'` as
  well as `'CRRA'`: leaving the `ρ=1` anchor on the adaptive smoother would solve it under a different
  residual from every other point of the march, and the anchor's `x` seeds the whole march.
  **The flip creates an override trap**: `initGS` merges the caller's dict *over* the defaults, so passing
  `smoothKnots=None` now *disables* pinned knots rather than requesting the default. A caller threading an
  optional argument must omit the key when it has nothing to say — `calibrateRhoGrid.py` (which would have
  selected adaptive) and `diagnoseRho07.py` (which would have inherited 4 and lost its own baseline) were
  both inverted by the flip, in opposite directions. Full chain: `notes/informalSavings_resolvedIssues.md`.
- **`interpKind` and `smoothKnots` go to BOTH solvers; only the grid sizes are keyed** (2026-08-20).
  Both are well-posedness choices, not resolution ones, and keying either by solver is a bug: at
  `'linear'` the LOG solve does not converge in `nι` at all — `τ(t0)` spans 9.6e-4 across `nι ∈ [45,120]`
  with no trend against 2.2e-5 at `'cubic'` — and since `τ(t0)` is a calibration *target*, the parameters
  get fitted to one realisation of that jitter. `nι` legitimately differs (LOG 50, CRRA 45): that one **is**
  a resolution choice, and at `'cubic'` the LOG answer is already converged in it (flat to 1e-5 across
  `nι ∈ {45,60,90}`). The same rule reaches `shockUniversal.py`, which must re-solve a calibrated instance
  on the interpolant it was calibrated at. `notes/crossCuttingFindings.md` #7.
- **The state grids anchor on `min_τ ι*(τ)` and `s*(0.3)`, not on `max_τ ι*(τ)` and `s*(0)`** (2026-08-19).
  `ι*` diverges as `τ→1`, so a rule written on its maximum had no finite content and `capι` was silently
  the real bound; `s*(0)` is *perfectly anti-correlated* with the reachable set across `ρ`. Both anchors
  are now measured to be stable (`min ι*` to 0.045%, `s*(0.3)` to 1.5%), occupancy went 49–52% → 78–80%
  (`ι`), and `capι` survives as an inert backstop. `padι[0]` must not be raised further without
  re-measuring `atBound` — see deviations note item 4.
- **A superseded result file left beside the live ones is an input to anything that globs.** Three
  instances now: `shockUniversal.py`'s `--csv` default pointing at a superseded sweep; `COLUMNS` declaring
  occupancy columns `toRow` never populated; and a `universal_match_rho1.0000_preInterpFix.csv` backup
  matching `plotUniversalShock.py`'s `universal_<rule>_rho*.csv` glob, which put the pre- and post-fix
  anchors on one figure as two points at `ρ=1`. The last is the worst-behaved of the three because the
  loader reads `ρ` from the file's **own column**, so the stale row is well-formed and looks like a real
  gridpoint. Superseded runs go in a subdirectory (`results/shocks/preInterpFix/`,
  `results/calibration/instances_preInterpFix/`); readers match the filename pattern exactly and treat a
  duplicate key as an error, never as something to average or first-wins. `notes/crossCuttingFindings.md` #8.
- **Do not auto-tune the grids from a previous run.** `initGS`' state slots are override-only by design,
  and a grid learned from run *n* makes the outer residual depend on solve history — the same defect as the
  smoother's knot flips, relocated. Measure with `reachableBox`/`gridOccupancy`, retune the *rule* offline.
- **A smoothed policy must be clipped back into `[l,u]`.** A spline through a profile that is flat at a
  corner over part of the state grid undershoots it, and the reported `τ_t` goes slightly negative wherever
  many states select the lower corner. Smoothing is a denoise, not a re-optimisation.
- **A clip that manufactures a bracket also manufactures a root** (`model.py`'s `initialStatePEE`). See
  `notes/crossCuttingFindings.md` (#2) for the general trap and this module's own numbers. Do not
  "simplify" it back to a bracketed solve on `[l,u]`.
- **`τ_t` reaches `eq:stateApprox` only through `Θ_{h,t}`** (`policy.py`'s `_stateApproxSI`). `τ_{t+1}`,
  `h_{t+1}`, `B_{t+1}`, `B_{t+1}^0`, `Γ_{s,t}` and the two interpolant calls behind them are constant along
  `τ_t`, so `_iotaOfTauS` evaluates them once per distinct `(s_t,ι_t)` **pair** rather than once per
  `(τ_t,s_t,ι_t)` triple. Both hot callers pass a `(τ,s)` Cartesian product, so this is a 900× reduction in
  `report_t` (3 600 rows against 3.2M) and the difference between a 64 s and a 5.7 s CRRA solve. Exact, not
  an approximation — the argument lists are the authority, and `test_peeCRRA.py` asserts the independence
  **bitwise**. Do not fold `_stateApproxSI` back into `stateApprox_t`, and do not soften `np.unique`'s exact
  grouping to a tolerance.
- **The CRRA calibration's two settings, neither of them the PEE solve's defaults** (it was three until
  2026-08-19 — see below). Measured, with their numbers in
  `notes/informalSavings_numericalDeviations.md` rather than restated here: `interpKind='cubic'` (item 13 —
  at `'linear'` the calibration does **not converge at all** away from `ρ=1`; `'pchip'` is better in
  principle but 1400× slower in `RegularGridInterpolator`); and `nι=ns=45` set explicitly before
  `calibrate` (items 12+17; `test_peeCRRA.py`/`test_peePath.py` assert their spacing tolerances against the
  `30×30` default instead). The general diagnostics behind both are `notes/crossCuttingFindings.md` #3 and
  #4.
- **The outer finite-difference step is scipy's own, for both solvers** (`_calOuterKwargs` is empty). The
  CRRA override `options={'eps': 1e-4}` was retired 2026-08-19 (item 17): its entire content was one
  corrupted `η0` Jacobian column, which was `smoothKnots`' residual jumps being straddled at that step
  rather than a property of the CRRA residual. Re-measured at the converged `ρ=0.7`/`ρ=0.9` points, every
  column is flat to 0.01% from `1.5e-8` through `1e-4`, and all three candidate steps calibrate in the same
  evaluation count to the same parameters — with **scipy's default reaching the tightest residual**, so
  `eps=1e-3` (which the `rho07_resolved` note had recommended adopting) is marginally worse, not better.
  Items 11 and 13's documented LOG/CRRA split is retracted, not relocated.
- **`45×45` is kept, but the reason changed and is now much weaker** (item 17). It is no longer that
  `30×30` converges to a *displaced* root — that symptom does not reproduce; all of `n ∈ {30,45,60}` now
  agree to 1.5–3.8e-4 in the parameters, which is *less* than the two solver changes of 2026-08-19 moved
  the LOG anchor. What survives is that at `ρ=0.7` the `30×30` refinement rungs run 2–3× above `45×45`'s
  (at `ρ=0.9` they are indistinguishable, and at `ρ=1.02` the gap is 1.2×), and the sweep runs to
  `ρ=0.5`, further into that region. The effect grows monotonically with distance from `ρ=1`, which is the
  clearest statement of what the grid is actually buying.
  `n=60` buys nothing over 45 either way: **~1e-4 in the parameters is the outer answer's floor**, which is
  also what `calibrate`'s `tol` should be read against. `30×30` is ~4× faster (≈90 min against ≈6 h for a
  16-point sweep) and is the first thing to revisit if the sweep budget ever binds.
- **The forward walk re-solves the state transitions; it does not interpolate them** (`approximatePEE`'s
  `exact=True`). `eq:forwardSim` writes them as functions of `τ_t`, and that is meant literally. Reading
  them off `ιPolicy`/`sPolicy` instead interpolates a composition the re-solve evaluates directly, costs
  ~2 orders of magnitude (1.2e-8 vs 4.7e-6 on `ι` under LOG), and under LOG discards structural result 1
  below — that `ι_t` depends on `τ_t` alone. The interpolants are kept only for `exact=False`, which is
  what measures the difference.

## Implementation status
- **Parameter/database scaffolding, simple calibration** (§0-2): done. `χR` is a 1D parameter (default 1);
  the analytical model's `α0`/`χ` are gone.
- **EE solve given policy** (§3), **steady state** (§4), **initial state** (§5): done and verified against
  primitives (`test_ee.py`).
- **`policy.py`'s `LOG` class** (`num_peeLOG.tex`): **done and verified** (`test_peeLOG.py`).
  `solveTerminal` → `τ_T(ι_{T-1})`; `solveBackward` → `{t: report}` for the whole horizon. Each report
  carries `τPolicy`/`ΘhPolicy` (what the previous period calls) and, for `t<T`, `ιPolicy` (the state
  transition `ι_{t-1} ↦ ι_t`, used only by the path solve's `exact=False` variant) and `ιCand` (the `𝒮_0'`
  this period actually used, so the path solve re-solves on it rather than on a re-resolved default).
  Diagnostics per period: `z`, `nMax`, `atBound`, `feasible`, `nRoots`, `ιOfτ`, `outOfGrid`.
- **`policy.py`'s `CRRA` class** (`num_peeCRRA.tex`): **done and verified** (`test_peeCRRA.py`). Same two
  entry points over the state *pair* `(s_{t-1}, ι_{t-1})`, with `τPolicy`/`hPolicy`/`sPolicy`/`ιPolicy`/
  `ΓsPolicy` as 2-D interpolants (`gridsearch.griddedInterp2D`), the candidate grids (`sCand`/`ιCand`) and
  the reachable set `𝒫_t` (`eq:reachable`) recorded per period. Only `τPolicy`/`hPolicy` are called by the
  previous period; the rest serve the path solve. `solveTerminal` is deliberately usable at `ρ=1`; the
  `t<T` recursion refuses it.
- **Path solve** (§6-7, `num_peePath.tex`): **done and verified** (`test_peePath.py`). `initialStatePEE`
  pins the state entering the first period (one method, both preference cases); `approximatePEE` walks the
  policy functions forward with the transitions re-solved at the walked `τ_t`; `solvePEE_LOG`/
  `solvePEE_CRRA` then re-solve the economic equilibrium **exactly** at the resulting `τ` (CRRA
  warm-started at the simulated `Γs`/`h`/`s`). Everything reported comes from that exact step — the
  simulated path is kept only for the docs' grid diagnostic.
- **Calibration over a grid of a parameter** (§8.1): **done and verified** (`test_calibrationGrid.py`).
  `calibratePoint(value, x0, par='ρ', gridSettings, verify)` installs the parameter, picks the solver,
  calibrates, and returns one flat record (parameters, the unbounded `x`, `max|residual|`, the four
  targets, `ι(t0)`, `occupancyι`/`occupancys`, `nRoots`, `nfev`, wall time, the inner grid used).
  `calibrateGrid` marches those via `gridsearch.continuation.marchGrid`, anchored at `ρ=1` — the only
  value where the cheaper LOG solver applies and the only one needing no warm start — walking outward both
  ways. `gridSettings`/`verify` may be flat or keyed by `'LOG'`/`'CRRA'`; **keyed is normally what you
  want**, since the CRRA calibration's settings (Conventions) would otherwise move LOG off its own
  documented `nι=50`.
  Two results worth carrying. **`η0` and `X0` barely move with `ρ`** (0.00%/0.02% spread against 29%/22%
  for `β`/`ω`) — those two self-consistency conditions are nearly solved by direct substitution, and only
  `(β,ω)` are genuinely identified by the data targets. And the **extrapolated warm start buys nothing at
  `Δρ=0.1` once the interpolants are `C¹`** — warm and cold both converge in 12 evaluations to identical
  parameters, so its value is robustness at larger steps and surviving a failure, not speed.
- **Calibration** (§8): **done and verified** (`test_calibration.py`). At `smoothKnots=4` and
  `interpKind='cubic'` LOG converges from `test.py`'s starting parameters in 25 evaluations / ~26 s to
  `max|residual| = 1.6e-10`: **`β=0.807610, ω=2.327810, η0=0.326087, X0=0.414067`**, on the
  capital-output target `KY0=3.2313`. (History. The 2026-08-24 change of target is the largest move in it
  by two orders of magnitude and is not a solver-side move at all — it is a different moment: under the
  savings-rate target the anchor read `β=1.211968, ω=2.641368, η0=0.325550, X0=0.408138`. Before that,
  and all under the old target: `β=1.212188, ω=2.638654` under the pre-2026-08-19 grid rule;
  `β=1.211615, ω=2.636787` after the retune but with the anchor still on the adaptive smoother;
  `β=1.210923, ω=2.645212` with pinned knots but the anchor still on **linear** interpolants, until
  2026-08-20. `test_calibrationGrid.py` pins the current pair.)
  **The 2026-08-20 interpolant move is the only entry in that history with an independent check on it**,
  and it is the reason a looser residual there was not a regression: the four CRRA points of a fine grid
  `ρ ∈ {0.98,…,1.02}` predicted `β=1.211956, ω=2.641327` at `ρ=1` by extrapolation onto their own gap, and
  the patched anchor landed on that to 1.2e-5/4.1e-5 where the previous one missed by −1.03e-3/+3.88e-3.
  The earlier `1.5e-11` was the solver converging *precisely* onto a jittering answer — see
  `notes/informalSavings_resolvedIssues.md`. That fine grid has not been re-run on the current target;
  the anchor's standing now rests on `test_calibration.py`'s cold solve and the sweep agreeing to 1e-6.
  CRRA at `ρ=1.02`, warm-started from that, converges to `1e-12` — but **only on a refined inner grid**,
  see Conventions. Away from `ρ=1` it additionally needs `interpKind='cubic'`.
  `solvePEE_*` now also return `init` (§6's dict) so the calibration can watch its `nRoots`.
  `calibrate`'s `tol` defaults to `1e-6`, deliberately looser than the inner solves (EE `1e-8`, steady
  state `1e-11`): those are exact root problems, this one reads its targets off a grid-searched path. Do
  not relax it much further — see Conventions on the CRRA calibration grid for what a loose `tol` would
  start accepting.
- **Grid placement diagnostics** (`policy.py`'s `reachableBox`/`gridOccupancy`, `model.py`'s
  `_calOccupancy`): **done**. Pure post-processing over what the solve already stores, so free to call;
  `calibratePoint` records `occupancyι`/`occupancys` on every point, beside `verifyResidual` and asserted
  no more than it is. They measure where the grids *should* sit; they never move them (see Conventions).
- **Numerical departures from the docs are collected in `notes/informalSavings_numericalDeviations.md`**,
  with the measurements behind each. Read it before editing the `num_pee*.tex` specs.
- **Model copies for shock experiments** (`createCopyFromt0`/`stateAtT0`): **done and verified**
  (`test_createCopyFromt0.py`) — see the section above.
- **The universalisation experiment** (`shockUniversal.py`, docs `num_shock.tex`): **done**, `match` run
  across the full `ρ ∈ [0.5, 2.0]` grid (LOG at the anchor, CRRA elsewhere), `flat` still only at `ρ=1`
  (see Open, under Results). It is a script rather than a model method on purpose — the model supplies the
  copy and the state, and what "universal" means is an experiment's choice, not the model's.

### How the LOG recursion is laid out
| Step (`alg:LOG:gridsearch`) | Method | Shape |
|---|---|---|
| — | `defaultIotaGrid` / `_ιGrid` | `𝒮_0` from the padded steady-state range of `ι*(τ)` |
| `eq:zdecomposition` | `_zState` | `(M,) → (M, M_ι)`, the rank-one broadcast |
| terminal | `stateGrid_T` → `zbar_T` → `solveTerminal` → `report_T` | `(M,)`, then one `selectMax` per state |
| 1. state approximation | `stateApprox_t`/`_residualIota`/`_rootIota`/`solveStateApprox_t` | `𝒯×𝒮_0' → ι_t(τ)`, `(M,)` |
| 2. current-period objects | `stateGrid_t` | `(M,)`, `(M,ni)` |
| 3. derivatives + FOC | `_gradProfile` → `zbar_t` | `(M,)` |
| 4. selection + reporting | `solveBackward_t` → `report_t` | `selectMax` per state, then interpolants on `𝒮_0` |

No `CartesianGrid` in the terminal period or in the broadcast — only step 1 evaluates a product
(`𝒯×𝒮_0'`), which is the practical content of the two structural results below.

### How the CRRA recursion differs
Same four steps, same method names, over the state *pair*. What changes:

| | LOG | CRRA |
|---|---|---|
| carried forward | `Θ_{h,t+1}` (level isn't a function of the state) | `h_{t+1}` (`s_t` is a state, and `B_{t+1}` needs a level) |
| state roots | one, `ι_t(τ_t)`, no state in it | two, unnested exactly: `ι_t(τ_t,s_t)` then `s_t` given `s_{t-1}` (`eq:iotaOfTauS`) |
| the `ι_{t-1}` extension | rank-one (`_zState`) | a broadcast but not rank-one — `(c_{2,t}^0)^{1-1/ρ}` sees the state too (`_zStateCRRA`) |
| numerical derivatives | 2 profiles + `dlnΘh` | 3, each composing *two* interpolated surfaces |
| feasibility | 1-D over `𝒯` | 2-D over `𝒯×𝒮` (conditions 1–3), still never a function of `ι_{t-1}` |
| extra reporting | — | the reachable set `𝒫_t` (`eq:reachable`) |

## Model copies for shock experiments (`model.py`, `createCopyFromt0`)
Same mechanism as `informalAnalytical` (module-level `_sliceDb`, shared verbatim — see that module's
README for the full design: renumbering vs. restriction, in-place `db` mutation, the `db['t0']` shift/
`None` rule, warm-start cache clearing, why state seeding stays outside the copy method). One addition
here, since this module has a second state:

- **`stateAtT0(report, t0, init)` returns `{'s0', 'ι0'}`, and the two states are asymmetric.** `s_` is
  reported lagged (`report['s_'].xs(t0)` is exactly the state entering `t0`), but `ι` is reported on the
  `txE` domain as `ι_t` for `t=0..T-2` (see "Reporting domains" below) — **not** lagged. So the state
  entering `t0` is `report['ι'].xs(t0-1)`, **except** at `t0 == db['t'][0]` itself, where `t0-1` has no
  entry in the report at all. There the value is instead the model's own initial-state proxy,
  `init['ι']` — pass the `'init'` dict already returned by `solvePEE_LOG`/`solvePEE_CRRA` rather than
  recomputing it. Getting this branch wrong reads either an out-of-range index or, worse on another
  instance, a different period's `ι`; `test_createCopyFromt0.py` pins it with a sentinel `init['ι']` that
  must appear verbatim in `seed['ι0']` only at `t0 == db['t'][0]`.
- Verified end to end: with no actual shock, re-solving the copy from `stateAtT0` reproduces the
  baseline's own `s`/`h`/`ι` tail at `t0` and later.

## Results: the `ρ` sweep
**Live file: `results/calibration/informalSavings_rhoGrid.csv`** + one pickled instance per point in
`results/calibration/instances/`. The 2026-08-24 sweep over `ρ ∈ [0.5, 2.0]` at the current settings
(`smoothKnots=4` and `interpKind='cubic'` on both solvers, `nι=ns=45`, scipy's default outer step — see
Conventions), and **on the capital-output target** `KY0 = 3.2313` that replaced the savings rate that day
(`notes/argentina_calibrationTarget.md`; log in `rhoGrid_sweep_2026-08-24_KYtarget.log`).

- **16 of 16 points solved, first attempt, no step-halving.** `KY` = 3.2313 to 1.6e-10 and `τ` = 0.125 to
  3.6e-10 at every point; `residual` ≤ 1.6e-10, `nRoots=1` everywhere. ≈2 h total (430–560 s/point on
  CRRA, 26 s at the LOG anchor) — the ~75 min quoted before predates `--verify`.
- `β`/`ω` move smoothly and monotonically (`β`: 2.63 at `ρ=0.5` → 0.81 at `ρ=1` → 0.45 at `ρ=2.0`);
  `η0`/`X0` stay near-flat (0.3260–0.3263, 0.4135–0.4160), per §8.1. `occupancyι`/`occupancys`
  78–80% / 64–80%.
- **`β` crosses 1 between `ρ=0.8` and `ρ=0.9`** (1.086 and 0.921), against `ρ≈1.15` on the savings-rate
  target. The whole curve is ≈0.65× its old self at every `ρ`, so the retarget shrank the `β>1` region
  without removing it: `ρ<0.85` still calibrates to a 30-year discount factor above 1. That is a result
  about the low-EIS end, not a numerical problem — `notes/argentina_calibrationTarget.md`.
- **`verifyResidual` degrades down the low-`ρ` tail**: ~6e-6 at `ρ=1`, 1.0e-4 at `ρ=0.8`, 4.9e-4 at
  `ρ=0.6`, 1.2e-3 at `ρ=0.5`. Those bottom two rows are converged on their own 45×45 grid but **not
  resolved** on the 60×60 verification grid, and should be read as indicative. Refining the low-`ρ` tail
  (a larger `nι`/`ns` there, or a coarser `ρ` grid with a finer inner one) is open.
- **The `ρ≈0.7` pocket is gone.** Under the savings-rate target `ρ ∈ [0.7, 0.775]` would not converge and
  needed its own diagnostic (`diagnoseRho07.py`); on this target `ρ=0.7` solves in 12 function
  evaluations with a 4.5e-14 residual. Whether that is the target or the different `β` it lands on has
  not been separated.

**Superseded — read only `informalSavings_rhoGrid.csv`.** Everything below the 2026-08-24 sweep was
calibrated to the savings-rate target and is not comparable to it in any column. Also: the 2026-08-12
sweep (predates the
smoother/grid-rule fixes, failed at `ρ=0.7`), both `informalSavings_rhoGrid_fixedKnots*.csv` (predate the
`occupancy*` columns; `_retuned`'s anchor was solved on the adaptive smoother), and
`informalSavings_rhoGrid_preInterpFix.csv` + `instances_preInterpFix/` (the pre-2026-08-20 anchor). None
are comparable to the current series or to each other.

`ρ=0.7`'s failure and its fix (a library routine choosing an integer from the data inside a differentiated
residual, not grid resolution): `notes/informalSavings_resolvedIssues.md`, transferable form
`notes/crossCuttingFindings.md` #5. The `ρ=1.0→1.1` `Δτ` dip: diagnosed and fixed 2026-08-20 by the
anchor patch above — the two recursions themselves agree to **0.0016 τ-grid cells**, so it was never a
solver-transition artifact.

Open:
- A `χ^R` sensitivity sweep is not planned (deprioritized 2026-08-12) despite `χ^R=1` being a knife-edge
  rather than a neutral default; `calibrateGrid` would do it with `par='χR'`.
- `model.py`'s four-parameter outer root could be reduced to two (`η0`/`X0` finding, §8.1). Deliberately
  not done. A 2-D `(β,ω)` problem is also much better conditioned — 5.4–6.2 against 15–18 measured on the
  full system — and would make a residual *map* affordable.
- The `flat` reading of the universalisation shock (below) has only been run at `ρ=1`; extending it to the
  full grid would give the bracket at every point, not only the anchor.

## Results: the universalisation shock
LOG at `ρ=1`, CRRA elsewhere: `results/shocks/universal_match_rho{ρ}.csv` for the full `ρ ∈ [0.5, 2.0]`
grid (16 points, 2026-08-24, on the capital-output target) plus `universal_flat_rho1.0000.csv` at the
anchor only. Reform at `t0`; `ε` changes only, `θ` fixed. `b^0/b^{refType}` matches its target to
≤2.3e-16 at every `match` point, confirming `installEps`'s `db['κ']`/`db['κ[t-1]']` rewrite stayed
consistent across the whole grid.

**`match` (`b^0=b^1`), impact-period response relative to baseline** (`τ_0=0.125` throughout; the
calibrated `ε` is 0.305 at `ρ=1`, and the universal target `ε^U=0.546` is near-flat in `ρ`):

| `ρ` | `Δτ` | `Δs` | `Δι` | `Δc^{1,0}` | `Δc^{2,0}` |
|---|---|---|---|---|---|
| 0.5 | +3.12% | −0.54% | −4.73% | +2.33% | +8.34% |
| 1.0 | +11.49% | −2.09% | −7.33% | +4.11% | +12.29% |
| 1.3 | +12.10% | −2.06% | −7.94% | +4.30% | +12.65% |
| 2.0 | +11.05% | −1.62% | −8.74% | +4.35% | +12.26% |

Every response is **larger than on the superseded savings-rate target** — `Δτ` at `ρ=1` is +11.49%
against +7.22% — and in the same direction. A less patient electorate (β 1.212 → 0.808) leans harder on
the pension system when the informal block is brought into it.

**`Δc^{1,0}` and `Δc^{2,0}` at `t0` are contaminated — do not quote them.** The `EE_report` proxy-state
defect under Known limitations puts ~+5.5% of level into `c20`'s impact-period response, so the `Δc^{2,0}`
column above is roughly half artifact. `Δτ`/`Δs`/`Δι` and every column from `t0+1` on are clean.

`Δι` is monotone in `ρ` across the whole grid; `Δτ` and `Δs` are not — both rise from `ρ=0.5`, turn over
around `ρ≈1.3` (`Δs` at `ρ≈1.1`), and `Δτ` falls back to 11.05% by `ρ=2.0`. A `ρ=1`-only result could not
show that hump, since `ρ=1` sits on the near side of the peak rather than on a monotone limb. **Not yet
investigated mechanically.** The hump survived the change of target unmoved in location — it peaked at
`ρ≈1.3` on the savings-rate target too — which is evidence it is a property of the recursion rather than
of the calibration. At `t0+1` the same shape appears, peaking near `ρ≈1.5`. Plotted:
`plotUniversalShock.py --series d_τ [--period 0|1]`.

**The two readings bracket the status quo rather than differing in degree.** `match` (`b^0=b^1`) raises
`ε` 0.305 → 0.546; `flat` (`ε=1-θ`, the non-contributive component only) cuts it to 0.161. Every response
reverses sign: on impact `τ` `0.1250 → 0.1394` against `→ 0.1112`, `Δι` −7.3% against +3.3%, `Δs` −2.1%
against +2.3%, `Δc^{1,0}` +4.1% against −2.5%. Either reading alone would have looked like a result.

Two things worth knowing before reading more into it. `match` against `j=1` **is still a benefit rise**
even though it equalises type 0 to the *lowest* formal type: the calibrated `ε` is
`0.7 × (relative benefit of type j=2) × 0.535` (an early-retirement discount, `model.getEps`), so the
status quo already sits below type 1's benefit — the sign comes from the coverage rate and the discount,
not from the reference type. And under `flat` the generation already old at `t0` is almost unaffected
(`Δc^{2,0}` +0.1%) despite the 52% cut, because `κ` falls with `ε` and `b̄ ∝ 1/κ_{t-1}`; only from the
next period does `c^{2,0}` fall by ~5–6%.


## Results: the reform decomposed, and the `ε`/`θ` comparative statics
Both produced 2026-08-21 for `python/paper/`; see `RESEARCH_LOG.md` for that session.

**Economic-equilibrium-only reform** (`shockEEOnly.py`): `results/shocks/eeOnly_match_rho{ρ}.csv`, all 16
`ρ`, run with `--control`. Taxes held at the baseline path, `ε` at the universal value. At `ρ=1` the
savings rate goes `14.725% → 14.862%` against the full effect's `→ 14.446%`: **the pure equilibrium effect
is positive and the full effect negative, at every `ρ` on the grid**, so the tax response is what turns
the sign. That survived the 2026-08-24 change of target unchanged in sign and close to unchanged in size,
which is the strongest single piece of evidence that the decomposition is a property of the model rather
than of the calibration. Labour supply moves the same way in both, with the equilibrium part ≈1/3 of the total. Cheap
enough (<1 min for the grid) to re-run whenever the baseline moves.

**`(ε, θ)` grid** (`sweepEpsThetaGrid.py`): `results/sweeps/epsThetaGrid_rho1.0000.csv`, 28 `ε` × 14 `θ` =
392 points at `ρ=1` with the calibrated parameters pinned, `nRoots == 1` everywhere. Level signs: `τ` ↑ in
`ε` and ↓ in `θ`; savings rate and hours the reverse; `ι` ↓ in both. Marginal effects shrink in `ε` for
`τ`/savings/hours and grow in `θ` — **except `ι`, whose marginal effect in `ε` grows monotonically**,
contradicting `Quant.tex`'s "in all cases" (a wording fix in the paper, not a code issue).

The `ε=ε^U` row of the grid is **not** the universalisation shock and does not match it (`τ` +9.88% vs
+7.22% at `ρ=1`): the grid re-solves the whole horizon under the new `ε`, so the state entering `t0` has
itself adjusted, while the shock is unanticipated and seeds from the pre-reform state. Two different
experiments, both correct.

## The three structural results the docs derive
All now exploited. Kept here because they are what the code would silently lose if someone "simplified"
it — and one of them has already been lost once and restored (see Conventions on the forward walk):
1. **LOG: the `ι_t` fixed point is a function of `τ_t` alone** — `ι_{t-1}` appears nowhere in it
   (`eq:stateResidualLOG`), because `B^i=β_i` makes `Γ_{s,t}` a function of `τ_{t+1}` only. So the state
   approximation is 1-D over `𝒯×𝒮_0'`, not repeated per state → `solveStateApprox_t` returns `(M,)`, and
   the feasibility mask with it.
2. **LOG: `ι_{t-1}` enters `z_t` through one additive rank-one term** (`eq:zdecomposition`), so the whole
   state grid costs a broadcast. Carry `Θ_{h,t+1}(ι_t)`, **not** `h_{t+1}` — the level also depends on
   `s_t` and so is not a function of the state → `_zState` + `lnRleadΘ`, verified against a pointwise
   evaluation of the full product.
3. **CRRA: the two states unnest into two 1-D roots** — `ι_t(τ_t,s_t)` first (its residual sees neither
   predetermined state), then `s_t` given `s_{t-1}`. Exact, not an approximation (`eq:iotaOfTauS`) →
   `_iotaOfTauS` then `_rootS`, both checked against an exact nested `brentq`.

Also from the docs: `l_ι > 0` strictly (it puts `dv20`'s pole outside the grid, so no masking of the state
dimension is needed); grid searches use the interior grid `𝒯`, not the extended `𝒯̃` (the selection rule
already puts `l`/`u` in the candidate set); `dlnc2i_dτ` must stay closed-form, but `dlnc20_dτ` *may* be
gridded because `ι_{t-1}` is a grid coordinate rather than a function of `τ_t`.

## Known limitations / open items
- **`EE_report` uses proxy lagged objects at a model copy's first period, and this contaminates
  `shockUniversal.py`'s `d_c20` at `t0`** (found 2026-08-21 by `shockEEOnly.py --control`). `EE_report`
  backs its first period's lagged objects out of `initialState_solve` rather than taking them as
  arguments. On the *full* model that is right; on a **copy** built by `createCopyFromt0` it is not — the
  true `ι_{t0-1}`/`h_{t0-1}` entering `t0` are the baseline's, and `stateAtT0` already knows them.
  The shock experiments compare a baseline path solved on the full model against a reform path solved on
  a copy, so the proxy enters the *difference*: **`c20` at `t0` is off by +5.3–5.7% of level** under both
  solvers (via `ι_{t0-1}`), and `bbar` by +0.01–0.13% under CRRA only (via `h_{t0-1}`; under LOG the proxy
  `Γ_{s,t-1}` is exact, so it is 1e-17 there). `b0`/`bi` are clean — `h_{t-1}` cancels against `bbar`.
  **Everything from `t0+1` on, and every other series, is clean**, so `τ`/`s`/`h`/`ι` — and therefore the
  paper's three Argentina tables and both figures — are unaffected. What *is* affected is the
  `Δc^{2,0} = +11.31%` headline in "Results: the universalisation shock" below, which is roughly half
  artifact. The no-shock control does not catch it as a failure because `shockEEOnly.py` deliberately
  mirrors the same convention, so the EE-only and full-effect rows stay differenceable.
  **Fix**: let `EE_report` accept the lagged state instead of calling `initialState_solve` — a `model.py`
  change plus a `shockUniversal.py` re-run (~2.5 h). Not done; the consumption columns should not be
  quoted until it is.
- **`test_calibrationGrid.py`'s pinned anchor is updated but the suite has NOT been run against it**
  (2026-08-20, at the user's request). `GRIDS['LOG']` gained `interpKind` and the pin moved to
  `β=1.211968, ω=2.641368`. That pair is backed by two direct calibrations and agrees with the fine grid's
  CRRA-extrapolated prediction to 1.2e-5, but agreement with a prediction is not the suite passing. Run it
  (~45 min) before treating this as verified: `python/runTests.py -k calibrationGrid`. Everything else
  passes — the 14 fast suites and both `test_calibration.py` suites were re-run 2026-08-20 after the
  test-harness consolidation.
- **The code and the `num_*.tex` specs are reconciled as of 2026-08-19** — items 15, 16 and 17 of
  `notes/informalSavings_numericalDeviations.md` all carry their doc side as updated, so nothing there is
  currently a live deviation. The measurements behind each are in that file; if either side moves, update
  both and that file, so the numbers never have to be re-derived. Item 10 runs the other way: the doc was
  right about the forward walk and the code was changed to match it. Two items there are now *history*
  rather than specification (12, 13) and are kept only as the baseline item 17 is read against.
- ~~**The tests print Greek symbols and Windows defaults redirected stdout to cp1252**~~ — **fixed
  2026-08-20** at source: `gridsearch/testing.py` reconfigures stdout/stderr to UTF-8 on import, and every
  test file imports its `check`/`report` from there. `calibrateRhoGrid.py` still sets its own encoding.
  Any *new* script that prints Greek must do one or the other — nothing enforces it.
- **`𝒮_0'` should stay aligned with `𝒮_0`, not refined.** `ι_t` reaches `eq:stateResidual:iota` *only*
  through the continuation interpolants, so the residual has no curvature of its own and its error is
  their kinks, which sit at `𝒮_0`'s nodes. Aligning removes every straddling cell (rel. error 2.3e-7);
  refining without aligning creates them (~2e-5, and non-monotone in the node count). Refine only in whole
  multiples. The `s` root is the opposite case — `B_{t+1}(s_t,h_{t+1})`'s own nonlinearity dominates, so
  `𝒮'` is refined and geometrically spaced instead. Not symmetric, and not interchangeable.
- **`κ`'s db-cache staleness under a varying `ε` is live, not latent.** The explicit `κ(ε1, t)` exists but
  every consumer reads a cached `db['κ']`, so any code path that changes `ε` must rewrite `db['κ']` with
  it. `shockUniversal.installEps` is the one that does; it is also the pattern to copy if `policy.py` ever
  endogenizes `ε`. Nothing detects the omission — a mutually inconsistent `(ε,κ)` violates no equilibrium
  condition, since `κ` enters everywhere as a given.
- `lnRleadΘ` reads `α`/`power_h` at `t`, though both are `t+1` objects exactly. This follows `Rlead`'s own
  existing convention and is immaterial unless `α`/`ξ` vary over `t` — but the two would then disagree.
- **The code is bitwise reproducible within a process, but not across processes.** See
  `notes/crossCuttingFindings.md` (#1) — affects how any refactor here must be verified.
- `initialState_solve` returns `s` from the **CRRA** steady state in both preference cases, while
  `initialStatePEE`/`EE_LOG_solve` take `s_0` from `steadyState_LOG_solve` under LOG. At `ρ=1` the two
  agree to `steadyState_CRRA_solve`'s tolerance (1e-11) but not bitwise. Deliberate — it keeps each
  solver's `s_0` default consistent with itself — but it is why `init['s']` is not used under LOG.
- No `SolveGrid`-equivalent class for `self.GS` — same deferral as in `informalAnalytical`.
