# informalAnalytical

Analytical informal-sector model: overlapping generations with `J+1` household types (type 0 = informal/hand-to-mouth, types `i>0` = formal). With log preferences the politico-economic equilibrium reduces to closed form (no continuation policy needed). Full derivation in `writing/informalAnalytical/` (`model*.tex` = model/equilibrium definitions, `num*.tex` = numerical solution approach — tex labels like `eq:auxiliary:Gammas` are referenced throughout the code's docstrings).

## Timing convention
Docs: time runs `t=1,...,T`; `t=0` is a pre-determined state taken as given (or via a steady-state assumption), not part of the decision horizon. Code: `db['t']` defaults to `0,...,T-1`.

| Docs | Code |
|---|---|
| `t=0` (pre-determined) | the `s0` function argument (state *before* `db['t'][0]`) |
| `t=1` (first active period) | `db['t'][0]` = `Base.tFirst` |
| `t=T` (terminal period) | `db['t'][-1]` (defaults to `T-1`) |
| `t=1,...,T` (full horizon) | `db['t']` |

Two db entries share names with the above by coincidence, not relation: `db['s0']` is the savings **rate** at the baseline year, unrelated to the `s0` savings-**level** argument (it identified `β` until 2026-08-24, when `db['KY0']` — the capital-output ratio — replaced it as the target; it is now reported only); `db['t0']` is the *index* of the calibration baseline year, unrelated to `Base.tFirst`. Code comments saying "`t=0`"/"`t=T-1`" mean code's own `db['t']`-relative indexing (one less than the docs' for the same period) unless stated otherwise.

## Files
Every `test_*.py` is a standalone script: it prints one PASS/FAIL line per assertion and exits nonzero on
any failure, via the shared harness in `gridsearch/testing.py` (which also forces UTF-8 stdout — the tests
print Greek). Run them individually, or through `python/runTests.py` (`--all` to include the slow ones).

- `model.py` — `ModelInformalAnalytical`. Database (`self.db`) and parameter scaffolding (§0-2); **EE solve given a policy path** (§3); **steady state solve** (§4); **initial (pre-determined) state solve** (§5). Instantiates `self.B`/`self.BG`/`self.BT` (`base.py`) and `self.LOG`/`self.CRRA` (`policy.py`).
- `base.py` — `Base`/`BaseGrid`/`BaseTime`: the economic-equilibrium equations, each method named after its tex doc label. `Base` = scalar/single-year, `BaseGrid` = single year/grid-valued, `BaseTime` = vectorized over all `t`.
- `policy.py` — `LOG`/`CRRA`: identifies the policy sequence (politico-economic equilibrium). Scoped to *identifying `τ`* only — never solves the full economic equilibrium itself; the model class calls `EE_*_solve`/`EE_report` separately with the returned `τ`.
- `test.py` — loads `data/ArgentinaTest.xlsx` and builds `mLOG = ModelInformalAnalytical(pars=pars, **kwargs)` with the real Argentina calibration. Standard way to get a non-degenerate model instance for testing (a bare `ModelInformalAnalytical()` has identical household types, giving `NaN`/`inf` `θ`/`κ`/`ε` — expected).
- `test_cacheParams.py` — regression test for `base.py`'s parameter cache (see "Base conventions"). Imports `test.py` for the model instance. 17 checks.
- `test_crraTerminal.py` — regression test for `policy.py`'s `CRRA.solveTerminal` (see "CRRA politico-economic equilibrium — terminal period" below). Imports `test.py`. 31 checks.
- `test_ee.py` — the economic equilibrium against its *primitive* conditions: rebuilds every consumption level from the household FOCs and raw budgets (`eq:formalOpt`/`formalBudget`/`informalBudget`), plus the PAYG balance and the aggregation identities `∑γ_iη_ih_i = h` / `∑γ_i(s_i/s) = 1`. 22 checks, at `ρ=1` and `ρ=1.15`. Added 2026-08-10 after `hi`/`bi` were found wrong (see the research log) — every other test targets the FOC/policy machinery, and none of them could see that class of bug.
- `test_createCopyFromt0.py` — `_sliceDb` on synthetic db entries (restriction + 0-based renumbering, every index shape); `createCopyFromt0`'s structural consistency (`db`/`T`/`tFirst`/`x0`/`db['t0']`) on the real calibrated instance, including both `db['t0']` branches and the out-of-range `ValueError`; a behavioral round trip — with no actual shock, `mt0.solvePEE_LOG(**stateAtT0(...))` reproduces the baseline's own tail at `t0` and later; and that `LOG.solveRobust` genuinely runs on the copy (warm-start caches cleared, not stale-shaped). 31 checks.

## Base conventions (`base.py`)
- **Parameter caching (`cacheParams()`).** Every db read goes through a pandas `.xs()`. Measured on the Argentina calibration that is **~43% of one FOC grid evaluation**, and it is per-*call* overhead, so it is **flat in grid size** — `M=101` and `M=501` cost the same (~1.8ms). Two derived aggregates dominate: `Γh` (~164µs) and `auxProd` (~108µs). `with self.BG.cacheParams():` memoises reads for the block; **~6.5x** per evaluation. Keys are `(symbol, resolved year, lag)`, so one block covers a period *and* its lag without either being declared, and lookups memoise lazily — a new db read in any method picks up caching automatically. Deliberately **opt-in and block-scoped, not always-on**: `model.py` rewrites whole db symbols during calibration, and a cache surviving that would return stale parameters *silently*. Outside a block every read hits db exactly as before. Nests safely (inner block reuses the outer cache; only the outermost exit clears). Wired into `LOG.solveBackward` (whole recursion) and `LOG.solveVectorized` (around the scipy call). Guarded by `test_cacheParams.py`, which checks bitwise-identical results, year non-collision, nesting, and that db writes outside a block are visible. Note `Γh` is still *computed*, not read from `db['Γh']` (same value, via `paramsFromFuncs`): `db['Γh']` is only refreshed by `updateAuxPars`, so reading it would go stale mid-calibration exactly when `ηi`/`Xi` are being solved for — caching gets the speed without that risk.
- **The flatness of evaluation cost in grid size is a design fact, not a detail**: it is why the CRRA solve evaluates the *whole* Cartesian grid in one vectorized pass rather than refining windows per state (see `gridsearch/cartesian.py`), and why the inspiration's traversal/refinement machinery is not being ported.
- **Explicit vs. db-sourced.** Primitives (`α, ξ, ν, γ, η, X, β, p, κ, Γh, ...`) are read from db via `self()`/`self.get()`. Anything solve/policy-dependent — `τ`, `θ`/`ε`, `s`/`h` and their lags/leads, discount factors `B` — is always an explicit argument, never read from db. Known gap: `κ(ε1, t)` exists as an explicit function, but its 9 consumers (`bbar`, `Γs`, `Θh`, `si_s`, `c1i`, `tildec1i`, `c2i`, `c20`, `tildec20`) still read a cached `db['κ']` — harmless while `ε`/`θ` are calibration-fixed, revisit once `policy.py` varies `ε` mid-solve.
- **`FH_*` methods (`BaseTime`, §8).** Several quantities need a genuinely different formula at the terminal period (`t=T-1`, no continuation) than for `t<T-1`. `FH_h`/`FH_c1i`/`FH_tildec1i`/`FH_dv1i_LOG`/`FH_dv10_LOG` own that stacking once. Where the terminal formula is provably a special case of the general one (feeding `B=0`/`Γs=0`/`β=0`), padding is used instead of branching — verified algebraically and numerically in each case.
- **Political weights (`ω1i`/`ω2i`/`ω10`/`ω20`, §0).** `μ` attaches to a *generation*, not a period: the old-generation term uses `μ_{t-1,i}` (their share when young), the young-generation term uses current `μ_{t,i}`.
- **`hRatio` vs `hηRatio` (§0) — keep them apart.** Two ratios differing by a factor `η_{t,i}`: `hRatio = h_{t,i}/h_t = (η_i/X_i)^ξ/Γh` (doc `eq:EE:hi`) and `hηRatio = h_{t,i}η_{t,i}/h_t = auxProd/Γh`. `hi` needs the first; `si_s`'s third term, `c2i` and `dlnc2i_dτ` need the second (the doc writes `η^{1+ξ}/X^ξ` over `Γh` in all three). Conflating them was a live bug until 2026-08-10 — `hRatio` computed the second while claiming to be the first, so `hi` returned `h_iη_i` and `bi` double-counted `η`. Reporting-only in effect (nothing else consumed them), but see the research log before touching either. Sanity checks: `∑γ_iη_i·hRatio_i = 1`, `∑γ_i·hηRatio_i = 1`; both are asserted in `test_ee.py`.
- **`BaseTime.Γh()` returns a plain `ndarray`, not a `Series`** — several formulas index it positionally without `_bcast`. Keep this in mind for any new `Base` method touching `self.Γh(t)`.

## EE solve (`model.py` §3) — style guide for numerical problems
Pattern for any numerical problem in this codebase: (i) a **residual** method (cheap, called repeatedly, raw `ndarray`), (ii) a **solve** method (returns just the core solution), (iii) a shared **report** method (expands the core solution into full downstream results via `base.py`). `τ`/`θ`/`ε`/`s0` always explicit, never read from db.
- `EE_LOG_solve`: closed-form (`ρ=1` makes `B=β` a primitive — no root-finding). Only `s_t`'s forward pass is a genuine recursion. `s0` defaults to the LOG steady state (§4) at `db['t'][0]`.
- `EE_CRRA_solve`/`EE_CRRA_residual`: root-finds the full `(Γs_t, h_t, s_t)` triple via `scipy.optimize.root`, zero Python loops (every equation just checks candidate consistency, vectorized via `self.BT`). Matches `EE_LOG_solve` exactly at `ρ=1`.
- **Terminal-period domain.** `Γs`/`B`/`si_s` report at natural length `T-1` (`db['txE']`, genuinely undefined at `T-1`); `h`/`s`/everything else stays length `T`.
- **Reporting wrap.** `_wrapVars(d)` wraps a flat `{name: ndarray}` dict at once, looking up each name's index from the class-level `_t2vars`/`_txE2vars` tuples — declared once rather than re-decided per method; a name missing from both raises `KeyError`.
- **`self.x0`** caches solver seeds by problem name (currently `'EE_CRRA'`). `update=True` on each solve method controls whether a converged solve overwrites the cache.
- **`self.ns['EE_CRRA']`** (`symMaps.SimpleSys`) replaces hardcoded `x[:nx]`-slicing for the stacked unknown vector.
- **Convergence** via `self._checkConverged(res.fun, tol, ...)` — checks `max|residual|` directly rather than trusting `scipy`'s own `res.success` (inconsistent across methods). Generic (not scipy-specific); reused across every numerical problem in this codebase.

## Steady state solve (`model.py` §4, docs §2.1)
Steady state = fixed point `s_t=s_{t-1}=s*` under constant `(τ,θ)`, evaluated at `Base.tFirst`'s parameters. Supplies the default `s0` for `EE_LOG_solve`/`EE_CRRA_solve`.
- `steadyState_LOG_solve`: closed-form (`B^i=β_i`).
- `steadyState_CRRA_solve`/`_residual`: `Γs` root-found via `scipy.optimize.brentq` (bounded scalar, `(0,0.75)` default per the doc) — a self-consistency check (`Γs == self.B.Γs(self.B.BSteadyState(Γs,...), ...)`), same style as `EE_CRRA_residual`.
- `Base.sSteadyState`/`Base.BSteadyState` (`base.py` §8) hold the closed forms; `sSteadyState` is written generally via `Θs` so it serves both LOG and CRRA.
- `steadyState_report` returns `{'Γs','B','s','h','Θs'}`, shared by both solvers.

## Initial (pre-determined) state solve (`model.py` §5, docs' `t=0`)
Identifies the state of the generation already old at `db['t'][0]` (docs' `t=0`), under the docs' own stated fallback ("the pre-defined state we take as given, or identify using some steady state assumption").
- **Key realization**: `Γ_{s,-1}` needs the policy this generation faces *when old* — `τ_0`/`θ_0`/`B_0^i` — which, since `t=0` is `db['t'][0]`, are simply `τ[db['t'][0]]`/`θ[db['t'][0]]`: actual given data, not an assumption. Only `Γs`'s *other* inputs (`α,ξ,γ,p,κ,η,X`, this generation's own labour-market conditions at period `-1`) are unavoidably proxied with `db['t'][0]`'s values, since no data exists for period `-1` itself.
- `initialState_solve(τ, θ, t)` — **no `s0`**. Returns `{'Γs','B','si_s'}` via `steadyState_CRRA_solve` (collapses to the LOG closed-form `βi` at `ρ=1`, so one method serves both preference cases) plus the existing `si_s` formula. None of these three depend on the savings level.
- `h_{-1}` is the one quantity that *does* need the actual `s0` — computed only where needed (`EE_report`) via the new `Base.hFromS` (inverse of `sFromH`, `h = Γh·(s/Γs)^{ξ/(1+ξ)}`), not bundled into `initialState_solve`.
- Consequence for LOG: since `B^i=β_i` is a pure primitive there (never a function of `s`/`h`), *nothing* in `policy.py`'s LOG FOC solve depends on `s0` at all — matching the docs' "no endogenous states" result (§PEELOG). `policy.py`'s `stateVectorized`/`solveVectorized` take no `s0` argument accordingly.

## Political first-order condition (`base.py` §9, docs `eq:fast`/§PEELOG/§terminalPEELOG)
Naming convention (settled before CRRA arrives): methods combining already-computed `dv/dτ` terms are preference-agnostic, no suffix (`FOC`); methods computing the `dv/dτ` terms themselves are preference-specific, suffixed (`_LOG` — CRRA's counterparts will be genuinely different code, e.g. numerical derivatives, not a different-suffix overload).
- `Base.FOC(dv1i, dv10, dv2i, dv20, t)` — the single, preference-agnostic combiner: `z_t` from the young/old marginal utilities via the political weights and population shares (old-generation term uses `γ[t-1]`, young uses current `γ` — matches the doc, not a typo).
- `Base.dv1i_dτ_LOG`/`dv10_dτ_LOG` — young generations' marginal utilities, single closed-form terms. `β`/`β0` explicit (mirrors `B` always being explicit elsewhere).
- `BaseTime.FH_dv1i_LOG`/`FH_dv10_LOG` — terminal stacking via zeroing `β`'s terminal entry (the doc's terminal formulas = general ones with `β_{T-1,j}=0`).
- `Base.dlnΘh_dτ_LOG`/`dv2i_dτ_LOG`/`dv20_dτ_LOG` — old generations' marginal utilities. Literally the same formula at every `t` (doc calls the terminal expression a "replica"), so no `FH_*` wrapper needed.

## LOG politico-economic equilibrium solve (`policy.py`'s `LOG` class, docs `alg:fast`)
"Gradient-based roots for the politico-economic equilibrium with log preferences" — no fallback, presumes the FOC is well-behaved. Solves the whole tax path `τ_0..τ_{T-1}` as one simultaneous vector unknown via the bounded-root reparameterization (`gridsearch.robustRoot`), split into three stages:
- `stateVectorized(τtilde, θ, ε, l, u)` — unbounded candidate `τ̃` → dict of every economic object the FOC needs (bounded `τ`, `Γs`, `Θh` with terminal substitution, the shifted `si_s_` ratio). No `s0`.
- `focVectorized(d)` — that dict → `z_t`, via the `_LOG` marginal utilities combined through `Base.FOC`.
- `reportVectorized(res, l, u, tol)` — a converged `scipy.optimize.root` result → just the bounded tax vector `τ` plus solver diagnostics (`maxResid`/`success`/`message`). No `EE_LOG_solve`/`EE_report` call — the model class does that separately once it has `τ`.
- `solveVectorized(θ, ε, x0, l, u, a0, a1, tol, update, **kwargs)` — orchestrator: builds the bounded residual, calls `scipy.optimize.root`, reports. `x0` defaults to a cached `self.x0['vectorized']`, falling back to the constant `db['τ0']` path.

`LOG` keeps its own `self.x0` cache, separate from `self.m.x0` (`model.py`'s `EE_*` cache), and copies `self.ni`/`self.T` locally at `__init__` — reduces coupling to the model instance. Still shared via `self.m`: `leadSym` and `_checkConverged` (generic utilities, designed for exactly this reuse) and `initialState_solve` (shared economic-equilibrium machinery, not "solving the full PEE").

## Robust LOG solve — backward grid search (`policy.py`'s `LOG.solveBackward`, docs `alg:gridsearch`)
Rests on a structural property of `eq:fast` that `solveVectorized` doesn't exploit: **no term of `z_t` depends on any lag of `τ`**. The young terms depend on `τ_t` alone; `dv2i`'s `si_s_` is a closed-form function of `τ_t`; only `dv20`'s `Θh` reaches forward. Hence `z_t = z_t(τ_t, τ_{t+1})` and `z_{T-1} = z_{T-1}(τ_{T-1})`. The `T`-dimensional simultaneous root is therefore **triangular** and solves exactly by backward recursion over *scalar* problems — which is what makes a grid search affordable and removes the initial-guess dependence entirely. (Holds only while `θ`/`ε` are exogenous.)
- `stateGrid(τ, t, θ, tLag, terminal, τ1, θ1)` / `focGrid(d, t, θ, ε, terminal)` — single-period counterparts of `stateVectorized`/`focVectorized`, via `self.BG` (`BaseGrid`: db params sliced to one year, arguments grid-valued). `Γ_{s,t}` is a *scalar* here (depends on `τ_{t+1}`, not the candidate `τ_t`); `Γ_{s,t-1}` inside `si_s_` is what's grid-valued. Terminal handled by passing `β=β0=0`, exactly as `FH_dv1i_LOG` does.
- **`tLag` is an explicit argument, not `t - 1`**: `db['t']` need not be a literal integer range (a generic pandas `Index` — dates, a non-contiguous calibration horizon — must still work), and `Base.Γs` has no lag-suffix mechanism for its own internal lookups (unlike `dv2i_dτ_LOG` etc., which read pre-shifted `'x[t-1]'` symbols), so evaluating it at the previous period's primitives genuinely needs that period's own label passed as `t`. `solveBackward` resolves `tLag` once per period via `db['t'].get_loc(t)` — position *within the Index*, never arithmetic on the label's value — so it works for any ordered index.
- **No `initialState_solve` call** at `tFirst`: `Base.__call__` clamps the year to `tFirst`, which reproduces that method's proxy exactly, and under LOG its `Γs` root-find collapses to `B^i=β_i` anyway (it's also scalar-only, so it couldn't be evaluated over a grid).
- **Corners and multiplicity** both resolved by `gridsearch.roots1d.selectMax` (`eq:candidates`). Deliberately **not** using `robustRoot`'s extended grid: that exists to make corners visible to a *root*-finder, and `selectMax` already puts `l`/`u` in the candidate set alongside interior maxima.
- `maxResid` is restricted to periods with an *interior* maximum — at a corner `z_t ≠ 0` is the correct answer, not a residual. No `_checkConverged` call: a grid search doesn't converge or fail, it resolves to grid resolution. Polish via `solveRobust`.
- Refinement window `Δl`/`Δu` (`_gridSettings`, symmetric by default) with doubling-on-the-binding-side expansion. Kept as two settings so a monotone path can be solved asymmetrically. Evaluated nodes are *not* cached on expansion — `z_t` is closed-form; that changes for CRRA.
- **Loops over the values of `db['t']`** (matching `inspiration/policyLog.py`'s `solveGSLoop`), not `range(self.T)`. `τ_{t+1}`/`θ_{t+1}` never need label arithmetic — the loop visits periods newest-to-oldest, so "the next period's solution" is just what the previous iteration produced, carried forward. `θ`/`ε`/the solved `τ` stay plain ndarrays positionally aligned with `db['t']` (the same convention `EE_LOG_solve`/`solveVectorized` already use for these three); only the label→position lookup (`db['t'].get_loc(t)`, for `tLag` and for indexing into those arrays) touches the Index itself.

`solveRobust(θ, ε, ...)` is the practical entry point: try `solveVectorized`, else `solveBackward` → warm-started `solveVectorized` polish, else return the grid solution flagged. Catches only `RuntimeError` (what `_checkConverged` raises) — a bare `except` would report genuine bugs as "didn't converge".

**Verified**: `solveVectorized` genuinely fails at `ω ≥ 5` on the Argentina calibration (scipy reports `success=True` with `max|residual|=2.1e-08`); `solveBackward` succeeds, and `solveRobust` polishes to `~1e-12`. `solveBackward` agrees with `solveVectorized` to `1.3e-05` at `n=101` and `5.0e-08` at `n=2001`, and the terminal period matches an independent `brentq`.

## PEE solve, end to end (`model.py` §6)
`solvePEE_LOG(θ=None, ε=None, s0=None, solver='Robust', **kwargs)` is the thin top-level orchestrator: `θ`/`ε` default to `db['θ']`/`db['eps']` if `None`; solves `τ` via `self.LOG.solve<solver>` (no `s0` needed there); `s0` (if `None`) is then resolved via the LOG steady state at the *solved* `τ[db['t'][0]]` — the same default `EE_LOG_solve` itself uses, resolved once here so it's consistent across `EE_LOG_solve` and `EE_report`. Returns `{'policy','sol','report'}`. `kwargs` pass through to the chosen solve.
- `solver='Robust'` (default) — same cost and same answer as `'Vectorized'` whenever the gradient solve works, plus a fallback when it doesn't, so it's strictly the better default.
- `'Vectorized'` — `alg:fast` alone, fails loudly. `'Backward'` — `alg:gridsearch` alone, accuracy capped by grid resolution; for diagnosing the FOC, not production.

## Named grid-problem structure (`self.GS`, `policy.py`'s `LOG.initGS`/`CRRA.initGS`)
Both `LOG` and `CRRA` hold `self.GS`, a dict of named political problems, each `{'solGrids': {...}, 'stateGrids': {...} or None, 'gridSettings': {...}}` — organized like the inspiration's `SolveGrid` dicts (one entry per problem, split into the variables actually solved for vs. the predetermined variables the solution is a function of), but **deliberately without that class's solver machinery yet** (each entry is a plain dict, not an object with its own `.solve()` — see RESEARCH_LOG's "groundwork" entry for why a `SolveGrid`-equivalent class was evaluated and deferred). Kept symmetric between `LOG` and `CRRA` on purpose, even though `LOG`'s one problem (`'PEE'`) never has a state (its FOC is independent of the savings level — see the `LOG` class docstring): `CRRA.initGS` extends the same `'PEE'` entry with the state grid its problem actually has (`{'s_': None}`), rather than inventing a separate name, so the terminal solve and the eventual `t<T` recursion share one place to look.
- **No more `self.grid`/`self.gridSettings` top-level attributes** — both lived only inside the single named problem `'PEE'` anyway, so once `self.GS` existed, the separate attributes were pure redundancy. `gridSettings` now lives *per problem* (`self.GS['PEE']['gridSettings']`), which is what lets a future second named problem (e.g. a `t<T` `'stateApprox'` entry) use different `l`/`u`/`n`/`Δl`/`Δu` without the two fighting over one shared attribute. `LOG.__init__`'s `grid` constructor argument still overrides these defaults exactly as before — it's forwarded through `initGS` into `'PEE'['gridSettings']` rather than assigned directly.
- **`solGrids['τ']`** is built in `initGS` from that same `gridSettings` (`np.linspace(l, u, n)`) — the τ-grid `LOG`'s backward solve (`solveBackward_t`) and `CRRA`'s terminal solve both read from `self.GS['PEE']['solGrids']['τ']`.
- **`stateGrids['s_']` (`CRRA` only) is a settable *override slot*, not an auto-populated cache.** Its bounds are data-dependent (`defaultSGrid` needs `θ`, only known at solve time) — caching a computed default here would risk the exact kind of silent staleness `cacheParams()` was built to avoid (a later solve with a different `θ` silently reusing the wrong grid). Starts `None`; `CRRA.solveTerminal` computes a fresh `defaultSGrid` per call when it's unset, and never writes the result back. Set `self.GS['PEE']['stateGrids']['s_']` explicitly to fix one grid across many solves — the eventual `t<T` recursion's use case, where every period should share the same state grid.

## CRRA politico-economic equilibrium — terminal period (`policy.py`'s `CRRA` class, docs §PEE/`eq:terminalPEECRRA`)
`CRRA(LOG)` — inherits `LOG`'s `__init__`/`self.grid`/`gridSettings` unchanged; overrides only `initGS` (see "Named grid-problem structure" above).
- **Structural finding**: docs `eq:terminalPEECRRA`'s terms are not new formulas — each is `(consumption level)^{1-1/ρ}` times the *same* log-derivative already implemented for LOG (`dv1i_dτ_LOG`/`dv2i_dτ_LOG`/`dv20_dτ_LOG`, which compute `dln(c)/dτ`), by the CRRA chain rule. So the terminal period needs **no numerical differentiation** — unlike `t<T`, where `Θh_t` depends on the endogenous continuation `τ_{t+1}` and has no closed form for `dτ_t`.
- **What's genuinely new**: `B_T^i` is no longer the primitive `β_i` — it's `Base.B(s_{T-1}, h_T, tLag)`, so the terminal problem is `z_T(τ_T, s_{T-1})`, a state-dependent scalar, not LOG's pure scalar.
- `stateGrid_T(τ, s_, θ, ε, t, tLag)` — closed-form terminal economic objects over grids of candidate `τ_T` and state `s_ = s_{T-1}`. Mirrors `LOG.stateGrid`'s `tLag` convention exactly: `Θh`/`h`/`tc1i`/`c2i`/`tc20` all use `t` (terminal's own primitives, with base.py's own internal `[t-1]` shifts where the doc's formulas need it); only `Bi`/`Γs_`/`si_s_` need `tLag` passed explicitly (the same three quantities, same reason, as `LOG.stateGrid`'s `βi_`/`Γs_`/`si_s_`).
- `focGrid_T(d, θ, ε, t)` — combines into `z_T` via the `c^{1-1/ρ}`-weighted `_LOG` terms, through the same preference-agnostic `Base.FOC`. The informal young's term is `0` identically regardless of `ρ` (written directly, not routed through a weighted call with nothing to weight).
- `defaultSGrid(θ, t, n=50)` — bounds from the doc's own suggestion: small positive lower bound (`s_{T-1}=0` makes `Rlead`/`Bi`/`si_s` undefined), `u_s = 1.25×s*(τ=0)` via the existing `steadyState_CRRA_solve`.
- `solveTerminal(θ, ε, t, tol)` — reads its grids from `self.GS['PEE']` (see "Named grid-problem structure" above): `τ` always from `solGrids['τ']`; `s_` from `stateGrids['s_']` if a caller has fixed one, else a fresh `defaultSGrid(θ, t)` per call. Builds a `gridsearch.CartesianGrid(τ=τGrid, s_=sGrid)`, evaluates `stateGrid_T`/`focGrid_T` **once, vectorized over the whole product** (no per-state loop, no refinement — the cost-is-flat-in-grid-size finding above is what licenses this), then `roots1d.selectMaxND` — exactly `LOG`'s terminal corner/multiplicity handling, applied once per state. No `self.x0`/warm start needed: closed-form, self-starting at every state simultaneously. Hands the solved `(sGrid, τ)` path to `report_T` and returns its full solution dict plus `'nMax'`/`'atBound'` diagnostics.
- `report_T(sGrid, τ, θ, ε, t, tLag)` — expands a solved `τ(s_{T-1})` into the full terminal solution dict, **evaluated along the solved path rather than the whole grid**: `stateGrid_T` makes no assumption about where its `τ` argument came from, only that it matches `s_`'s shape, so this is `stateGrid_T` called a second time with `(N,)`-length solved values instead of the `(M·N,)`-length search grid — no new economic content needed, and no `funcOfτGrid_T`/`funcOfτ_i` split like the inspiration's (its `funcOfτGrid_T` was already written generically enough to serve both, which is exactly what `stateGrid_T` does here too). Also builds `τPolicy`/`hPolicy` — the "local functions τ_t(s_{t-1})/h_t(s_{t-1}), evaluable along the PEE path" the `t<T` recursion needs (matching the inspiration's `solp['τPolicy']`/`solp['hPolicy']`) — via `gridsearch.griddedInterp1D`, which **extrapolates rather than clamps**: a `t<T` candidate continuation state need not land on `sGrid`'s own nodes. `'τ'`/`'h'` come back wrapped as `pd.Series` indexed by `sGrid`; everything else (`Θh`, `Bi`, `Γs_`, `si_s_`, `tc1i`, `c2i`, `tc20`) stays a raw ndarray, matching `stateGrid_T`'s own convention.
- **Delegated to `gridsearch`, not implemented in `policy.py`**: the interpolation `report_T` needs (`griddedInterp1D`) lives in the new `gridsearch/interp.py` — model-agnostic, like `robustRoot`/`roots1d`/`cartesian`. The `t<T` recursion's other numerical needs from the inspiration (smoothing a solved policy before interpolating; numerically differentiating along a grid axis, since `t<T`'s FOC has no closed form) belong there too when built — deliberately not built yet, since the terminal period doesn't call them (see `gridsearch/README.md`'s Implementation status).
- **Verified, not just tested**: at `ρ=1`, `Base.B`'s `ρ_c=1` collapses `Bi` to `β_i` regardless of `(s_,h)` and every `c^{1-1/ρ}` weight collapses to `c^0=1` — so `solveTerminal`'s `τ(s_)` is then *exactly* (bitwise, not grid-tolerance) `LOG.solveBackward_t(terminal=True)`'s answer, state-independent, at every `s_`. `test_crraTerminal.py` checks this plus genuine state-dependence at `ρ≠1`, the full report dict's contents, `τPolicy`/`hPolicy`'s node-exactness/linear-interpolation/extrapolation, and that `report_T` re-run on its own output reproduces it exactly.

## CRRA politico-economic equilibrium — t<T backward recursion (docs alg:CRRA:grid)
- **The economic equilibrium at each t<T is a fixed point in `s_t`** (docs `eq:stateResidual`), not closed-form: a candidate `s_t` determines `τ_{t+1}(s_t)`/`h_{t+1}(s_t)` via the next period's interpolants, hence `Θ_{s,t}`, and `s_t` is an equilibrium iff `Θ_{s,t}·(s_{t-1}/ν)^σ` returns that same `s_t`. Genuinely a **root** problem (`roots1d.allRoots`), not the maximisation the political FOC needs.
- **The fixed point is 2D, not 3D**: nothing in the forward pass depends on `s_{t-1}` — only the residual's explicit `(s_{t-1}/ν)^σ` factor does — so the expensive part (`stateApprox_t`) is evaluated once over `(τ,s)` and every `s_{t-1}` follows by broadcasting (`solveStateApprox_t`).
- **Exactly three log-derivatives are numerical** (`d ln h_t`, `d ln ĉ_{1,t}^i`, `d ln c̃_{2,t+1}^0`, via `gridsearch.griddedGradient1D`); `dln(c_{2,t}^i)/dτ_t` must stay closed-form (`base.py`'s `dlnc2i_dτ`) — a grid derivative would fold `s_{t-1,i}/s_{t-1}`'s own grid-variation into the FOC, which is a correctness bug, not an approximation (docs §PEE footnote).
- **`ĉ_{1,t}^i` is never materialized as a level** — `base.py`'s `hatc1iPow`/`lnhatc1i` carry `(1+B)·c̃^p` and `ln(1+B)/p + ln(c̃)` instead of the literal `(1+B)^{1/(1-1/ρ)}·c̃`, which overflows float64 as `ρ→1` (verified: at `ρ=1.001` the literal form hits `inf` in 12/12 test entries; the safe forms match it to machine precision wherever it doesn't overflow).
- **Infeasibility is first-class**: `roots1d.selectMax` now maximises each state over its own feasible (NaN-masked) sub-grid rather than requiring a fully-feasible column.
- `report_t` builds `sPolicy`/`ΓsPolicy` alongside `τPolicy`/`hPolicy` (no new economic content — the data was already computed); these feed `CRRA.approximatePEE`.
- **Verified**: FOC residual at the selected `τ` is `~1e-17` (machine precision) at every interior selection; `ρ=1` is refused with a message pointing at `LOG` (checked before, not after, `hatc1i`'s division). `test_crraBackward.py`.

## PEE solve, end to end — CRRA (`model.py`'s `solvePEE_CRRA`)
- **`s0` needs a genuine fixed-point search** (`steadyStatePEE_CRRA`, searching over `τ` not `s` — clean bounds), unlike `solvePEE_LOG`'s plug-in: CRRA's `τ_{tFirst}=τPolicy_{tFirst}(s0)` depends on the very state being determined, so "solve τ, then read off `τ[tFirst]`" is circular here.
- **`CRRA.approximatePEE`** forward-simulates the tax path by walking `τPolicy`/`sPolicy` from `s0` — no new state-transition machinery, since `report_t` already has the equilibrium `s_t`/`h_t`/`Γ_{s,t}` at every grid node.
- **The forward-simulated path is never trusted directly** — `solvePEE_CRRA` re-solves `EE_CRRA_solve` exactly given the simulated `τ` path (mirrors `LOG.solveRobust`'s "grid locates the branch, an exact step polishes it"), optionally warm-started from the forward-simulated `(Γs,h,s)` (`warmStart=True`, scoped to this call only).
- **Verified**: the fixed point round-trips exactly; `warmStart=True/False` converge to the same equilibrium (`~5e-12` apart — solver noise, not a different answer); `ρ=1.02` CRRA lands within `0.0015` of `ρ=1` LOG despite sharing no code path. `test_crraPEE.py`.

## Calibration (`model.py` §8, docs §calibration/eq:calibration)
Nested fixed point: `calibrate` root-finds `(β, ω, η0, X0)` (unbounded log/logit reparameterization,
positivity only — β is **not** capped at 1, since `simpleβ` sets `βj=β·p_j`, the actual discount factor,
and this model's calibration has landed either side of 1 depending on the target) against four targets at
`db['t0']` — **capital-output ratio**, tax rate, and `η0`/`X0` self-consistency (`base.py`'s
`capitalOutputRatio`/`calibrationη0`/`calibrationX0`, plus `ΘhFromH` to recover `Θ_{h,t0}` from a solved
path regardless of LOG/CRRA/terminal origin). The residual is formed once, in `_calResidual`: `K/Y`
relative and `τ` level, since `K/Y ≈ 3.2` against `τ = 0.125`.

**The target changed on 2026-08-24**: `db['KY0'] = 3.2313` (Argentina's 2010 capital-output ratio, PWT
11.0 via `python/paper/dataTargets.py`) replaced the savings rate `db['s0'] = 0.184`, in this variant as
in `InformalSavings`. `notes/argentina_savingsTargetAudit.md` is the argument; the savings rate is still
computed and reported. This variant calibrates to `β = 0.844, ω = 2.197` at `ρ=1` — above `InformalSavings`'
0.808, as it must be, since hand-to-mouth informal households leave the formal block to hold the whole
capital stock.

**`test.py`'s `β`/`ω` are a starting point, not a calibration**, and they had to move with the target: from
`β=0.6` the outer search walks into a region where the whole-path policy solve returns a NaN `τ` and the
steady-state `brentq` then fails at its own lower bracket. Every start in `[0.7, 1.0]` converges to the
same root, so the guess is now `β=0.85, ω=2.2`. Worth knowing as a limitation of this variant: its outer
search has no globalization, so a start far from the root fails outright rather than converging slowly —
`InformalSavings` took the same change of target from the same `β=0.6` guess without complaint. Each residual evaluation is
a full `solvePEE_LOG`/`solvePEE_CRRA` solve via `calibration_report`. `preferences` defaults to `'LOG'` iff
`ρ=1`. On failure db is restored to its pre-call state (never left holding a trial point); `_calSetPars`'s
db rewrites happen strictly outside any `cacheParams()` block, so the two don't interact.
Converges in ~4s / 36 PEE solves on Argentina (LOG); CRRA at `ρ=0.98/1.02` (warm-started) lands within
~1–3% of the LOG parameters. See `test_calibration.py` and the 2026-08-06 research-log entry (incl. two
faster variants that were tried and reverted — one cost more than the 4-D root, the other broke scipy's
finite-difference Jacobian by mutating parameters inside the residual).

## Model copies for shock experiments (`model.py` §9, `createCopyFromt0`)
For an "unexpected shock at `t0`" experiment: solve the baseline PEE over the full horizon, call
`m.createCopyFromt0(t0)` to get an independent model whose `db['t']` is restricted to `>= t0` and
**renumbered to start at 0**, then re-solve on the copy seeded with `m.stateAtT0(baseline_report, t0)`.

- **Renumbering, not just restriction.** `EE_LOG_solve`/`EE_CRRA_solve`/`EE_report`/`initialState_solve`
  index a caller's `τ`/`θ`/`ε` arrays *positionally* via `self.B.tFirst`, which is only correct when
  `db['t']` is the native 0-based range a fresh instance builds — so `tFirst` must come back out as `0` on
  the copy. `_sliceDb` (module-level helper, shared with `InformalSavings`) does both the restriction and
  the shift, in place, for every db entry indexed wholly or via one level by `'t'` (plain `Index`,
  `MultiIndex`, `Series`/`DataFrame` and their `[t±1]` siblings) — scalars and type-only (`j`/`i`/`u`)
  objects pass through untouched.
- **Mutates `db` in place, does not rebind it.** `createCopyFromt0` relies on `self.B`/`self.BG`/`self.BT`/
  `self.LOG`/`self.CRRA` all sharing the same dict object post-`deepcopy`; replacing `db` with a fresh dict
  would silently orphan that aliasing.
- **`db['t0']`** (the calibration-baseline-year position — unrelated to this method's `t0` argument) is
  shifted by `-t0` if the calibration year still falls inside the new horizon, else set to `None` rather
  than silently resolving to the wrong year. Recalibrating a copy needs a caller-supplied `db['t0']`.
- **Warm-start caches** (`x0`, `LOG.x0`, `CRRA.x0`) are cleared (stale/wrong length for the new horizon);
  `LOG.GS`/`CRRA.GS` (state-space grids, not time-indexed) are left as-is.
- **State seeding is deliberately not done inside `createCopyFromt0`.** `s0` (and, in `InformalSavings`,
  `ι0`) stay explicit arguments to `solvePEE_LOG`/`solvePEE_CRRA` on the copy, exactly as for any other
  instance — `stateAtT0(report, t0)` is the helper that reads them off an already-solved baseline report.
- Verified end to end (`test_createCopyFromt0.py`): with no actual shock, re-solving the copy from
  `stateAtT0` reproduces the baseline's own tail at `t0` and later to ~1e-11–1e-13.

## Implementation status
- **Parameter/database scaffolding** (§0-2): done.
- **Simple calibration** (§2): eigenvector step for `ηi`/`Xi`/`θ`/`ε`, real values against `test.py`'s
  Argentina data (`θ≈0.839`, `ε≈0.284`, `κ≈1.091`).
- **Economic equilibrium building blocks** (`base.py`): complete, and verified against the primitive
  FOCs/budgets by `test_ee.py` (added 2026-08-10, which is when `hi`/`bi` were found and fixed).
- **EE solve given policy** (§3), **steady state solve** (§4), **initial state solve** (§5): complete and tested.
- **Politico-economic equilibrium** (`policy.py`): `LOG` (`solveVectorized`/`solveBackward`/`solveRobust`) and `CRRA` (terminal period **and** `t<T` backward recursion, `solveBackward`) both implemented and verified — see the sections above.
- **End-to-end PEE solve** (`model.py` §6-7): `solvePEE_LOG` and `solvePEE_CRRA` both implemented and tested.
- **Nested-fixed-point calibration** (§8): implemented for LOG and near-LOG CRRA (`ρ` within ~0.02 of 1);
  untested at `ρ` far from 1 (see Known limitations).
- **Model copies for shock experiments** (§9, `createCopyFromt0`/`stateAtT0`): implemented and verified —
  see the section above.
- **`gridsearch`**: `robustRoot`, `roots1d` (incl. NaN/infeasibility handling), `cartesian`, `interp` (incl. `griddedSmooth1D`/`griddedGradient1D`) — all implemented and unit-tested.

## Known limitations / open items
- `κ`'s db-cache staleness under endogenous `ε` (see "Base conventions") — revisit when `policy.py` needs it.
- Calibration untested at `ρ` far from 1 (~0.5, ~2) — the CRRA backward recursion + calibration root
  together may need a more robust solve strategy there.
- The `nMax > 1` multiplicity branch (`roots1d.selectMax`) is unit-tested but never triggered by a real calibration.
- No `SolveGrid`-equivalent class built yet for `self.GS` — deferred twice now with two real problems (terminal, `t<T`) in hand; revisit if a third grid-search problem (e.g. a different model variant) needs the same structure.
- `solveBackward` does not cache evaluated nodes across window expansions (`z_t` is closed-form, so it's free to recompute). Add a cache when CRRA makes `z` expensive.
