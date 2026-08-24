# informalAnalytical

Analytical informal-sector model: overlapping generations with `J+1` household types (type 0 =
informal/hand-to-mouth, types `i>0` = formal). With log preferences the politico-economic equilibrium
reduces to closed form. Derivation in `writing/informalAnalytical/`; tex labels like
`eq:auxiliary:Gammas` are cited throughout the docstrings.

This is the **ancestor module**: `US` is a copy of it with the informal type removed, and `InformalSavings`
a copy with type 0 saving. The conventions below — the `Base`/`BaseGrid`/`BaseTime` split, the
residual/solve/report pattern, `cacheParams`, `createCopyFromt0` — are shared with both, and the other two
READMEs point here rather than restating them.

## Timing convention

Docs run `t=1,…,T` with `t=0` a pre-determined state; code has `db['t']` defaulting to `0,…,T-1`.

| Docs | Code |
|---|---|
| `t=0` (pre-determined) | the `s0` function argument (state *before* `db['t'][0]`) |
| `t=1` (first active period) | `db['t'][0]` = `Base.tFirst` |
| `t=T` (terminal) | `db['t'][-1]` |

Two db entries share names by coincidence: `db['s0']` is the savings **rate** at the baseline year (it
identified `β` until 2026-08-24, when `db['KY0']` replaced it; now reported only), unrelated to the `s0`
savings-**level** argument; and `db['t0']` is the *index* of the calibration baseline year, unrelated to
`Base.tFirst`. Code comments saying "`t=0`"/"`t=T-1`" mean code-relative indexing unless stated.

## Files

| | |
|---|---|
| `base.py` | `Base`/`BaseGrid`/`BaseTime` — the equilibrium equations, each method named after its tex label. Scalar / grid-valued / vectorized over `t` |
| `model.py` | `ModelInformalAnalytical`: db scaffolding (§0-2), EE solve given a policy (§3), steady state (§4), initial state (§5), end-to-end PEE (§6-7), calibration (§8), model copies (§9) |
| `policy.py` | `LOG`/`CRRA` — identify the policy sequence only. Never solves the full economic equilibrium; the model class calls `EE_*_solve`/`EE_report` separately with the returned `τ` |
| `test.py` | loads `data/ArgentinaTest.xlsx`. A bare `ModelInformalAnalytical()` has identical household types and gives `NaN`/`inf` `θ`/`κ`/`ε` — expected |

Test suites: `test_ee.py` (22), `test_cacheParams.py` (17), `test_crraTerminal.py` (31),
`test_crraBackward.py`, `test_crraPEE.py`, `test_createCopyFromt0.py` (31), and the slow
`test_calibration.py`. Each is a standalone script printing one PASS/FAIL line per assertion via
`gridsearch/testing.py`.

## The pattern every numerical problem follows

(i) a **residual** method — cheap, called repeatedly, raw `ndarray`; (ii) a **solve** method returning just
the core solution; (iii) a shared **report** method expanding it into downstream results via `base.py`.
`τ`/`θ`/`ε`/`s0` are always explicit, never read from db. Convergence goes through
`self._checkConverged(res.fun, tol, …)`, which checks `max|residual|` directly rather than trusting
scipy's `res.success` (inconsistent across methods).

## Base conventions (`base.py`)

- **`cacheParams()` is opt-in and block-scoped.** Every db read goes through a pandas `.xs()`, which is
  ~43% of one FOC grid evaluation and is per-*call* overhead, hence **flat in grid size** (`M=101` and
  `M=501` both ~1.8 ms). `with self.BG.cacheParams():` memoises reads for the block, ~6.5× per evaluation;
  keys are `(symbol, resolved year, lag)`, so one block covers a period *and* its lag. Deliberately not
  always-on: `model.py` rewrites whole db symbols during calibration and a surviving cache would return
  stale parameters *silently*. `Γh` is still computed rather than read from `db['Γh']` — that entry is
  only refreshed by `updateAuxPars`, so reading it would go stale mid-calibration exactly when `η_i`/`X_i`
  are being solved for.
- **The flatness of evaluation cost in grid size is a design fact**, not a detail: it is why the CRRA
  solve evaluates the *whole* Cartesian grid in one vectorized pass rather than refining windows per state.
- **Explicit vs db-sourced.** Primitives (`α, ξ, ν, γ, η, X, β, p, κ, Γh, …`) are read from db. Anything
  solve- or policy-dependent — `τ`, `θ`/`ε`, `s`/`h` and their lags, discount factors `B` — is always an
  explicit argument. Known gap: `κ(ε1, t)` exists as an explicit function, but its nine consumers still
  read a cached `db['κ']`. Harmless while `ε`/`θ` are calibration-fixed; revisit if `policy.py` varies `ε`.
- **`hRatio` vs `hηRatio` — keep them apart.** `hRatio = h_{t,i}/h_t = (η_i/X_i)^ξ/Γh` and
  `hηRatio = h_{t,i}η_{t,i}/h_t = auxProd/Γh`. `hi` needs the first; `si_s`'s third term, `c2i` and
  `dlnc2i_dτ` need the second. Conflating them was a live bug — `hRatio` computed the second while
  claiming to be the first, so `hi` returned `h_iη_i` and `bi` double-counted `η`. Sanity checks
  (asserted in `test_ee.py`): `∑γ_iη_i·hRatio_i = 1`, `∑γ_i·hηRatio_i = 1`.
- **Political weights**: `μ` attaches to a *generation*, not a period — the old-generation term uses
  `μ_{t-1,i}`, the young-generation term current `μ_{t,i}`.
- **`FH_*` methods** own the terminal period's different formula once. Where the terminal formula is
  provably a special case of the general one, padding (`B=0`/`Γs=0`/`β=0`) is used instead of branching.
- **`BaseTime.Γh()` returns a plain `ndarray`, not a `Series`** — several formulas index it positionally.
- **Terminal-period domain.** `Γs`/`B`/`si_s` report at length `T-1` (`db['txE']`, genuinely undefined at
  the end); everything else stays length `T`. `_wrapVars` looks each name up in `_t2vars`/`_txE2vars`.

## The structural result the LOG solver rests on

**No term of `z_t` depends on any lag of `τ`.** The young terms depend on `τ_t` alone; `dv2i`'s `si_s_` is
a closed-form function of `τ_t`; only `dv20`'s `Θh` reaches forward. So `z_t = z_t(τ_t, τ_{t+1})` and the
`T`-dimensional simultaneous root is **triangular**, solving exactly by backward recursion over *scalar*
problems — which is what makes a grid search affordable and removes the initial-guess dependence. Holds
only while `θ`/`ε` are exogenous.

Hence three LOG entry points: `solveVectorized` (the whole path as one simultaneous root, `alg:fast`),
`solveBackward` (the triangular grid search, `alg:gridsearch` — accuracy capped by grid resolution, for
diagnosing the FOC rather than production), and **`solveRobust`, the practical one**: try `solveVectorized`,
else `solveBackward` → warm-started polish, else return the grid solution flagged. It catches only
`RuntimeError` (what `_checkConverged` raises) — a bare `except` would report genuine bugs as
"didn't converge". Measured: `solveVectorized` genuinely fails at `ω ≥ 5` on the Argentina calibration
(scipy reports `success=True` at `max|residual|=2.1e-08`), `solveBackward` succeeds, and `solveRobust`
polishes to ~1e-12.

Two details of the grid search that are easy to break: **`tLag` is an explicit argument, not `t - 1`**,
because `db['t']` need not be a literal integer range and `Base.Γs` has no lag-suffix mechanism for its
internal lookups — `solveBackward` resolves it via `db['t'].get_loc(t)`, position within the Index, never
arithmetic on the label. And **corners and multiplicity both go through `roots1d.selectMax`**, not
`robustRoot`'s extended grid: that exists to make corners visible to a *root*-finder, while `selectMax`
already puts `l`/`u` in the candidate set. `maxResid` is therefore restricted to periods with an interior
maximum — at a corner `z_t ≠ 0` is the correct answer, not a residual.

**Under CRRA the terminal period needs no numerical differentiation**: `eq:terminalPEECRRA`'s terms are
each `(consumption level)^{1-1/ρ}` times the *same* log-derivative already implemented for LOG, by the
chain rule. What is genuinely new is that `B_T^i` is no longer the primitive `β_i`, so the terminal problem
is `z_T(τ_T, s_{T-1})` — state-dependent. At `t<T`, `Θh_t` depends on the endogenous continuation
`τ_{t+1}` and there is no closed form, which is where the numerical derivatives start.

**`self.GS`** holds the named political problems, each `{'solGrids', 'stateGrids', 'gridSettings'}`, kept
symmetric between `LOG` and `CRRA` even though LOG's one problem never has a state.
`stateGrids['s_']` (CRRA only) is a settable **override slot, not an auto-populated cache** — its bounds
are data-dependent, so caching a computed default risks exactly the silent staleness `cacheParams` was
built to avoid.

## Model copies for shock experiments (`createCopyFromt0`)

Solve the baseline over the full horizon, call `m.createCopyFromt0(t0)` for an independent model whose
`db['t']` is restricted to `>= t0` and **renumbered to start at 0**, then re-solve seeded with
`m.stateAtT0(baseline_report, t0)`.

- **Renumbering, not just restriction.** `EE_*_solve`/`EE_report`/`initialState_solve` index a caller's
  `τ`/`θ`/`ε` arrays *positionally* via `self.B.tFirst`, which is only correct when `db['t']` is the native
  0-based range — so `tFirst` must come back out as `0`. `_sliceDb` (module-level, shared verbatim with
  `InformalSavings`) does restriction and shift in place for every db entry indexed wholly or partly by
  `'t'`; scalars and type-only objects pass through.
- **Mutates `db` in place, does not rebind it.** `self.B`/`self.BG`/`self.BT`/`self.LOG`/`self.CRRA` all
  share the same dict object post-`deepcopy`; replacing `db` would silently orphan that aliasing.
- **`db['t0']`** is shifted by `-t0` if the calibration year still falls inside the new horizon, else set
  to `None` rather than silently resolving to the wrong year.
- **Warm-start caches are cleared** (stale/wrong length); `GS` state grids are not time-indexed and stay.
- **State seeding is deliberately outside the copy method.** `s0` (and `ι0` in `InformalSavings`) stay
  explicit arguments to `solvePEE_*`; `stateAtT0` reads them off an already-solved baseline report.

Verified end to end: with no shock, re-solving the copy from `stateAtT0` reproduces the baseline's own tail
at `t0` and later to ~1e-11–1e-13.

## Status

Done and verified: scaffolding and simple calibration (§0-2, `θ≈0.839`, `ε≈0.284`, `κ≈1.091` on the
Argentina data); the equilibrium building blocks against the primitive FOCs/budgets; EE solve given a
policy (§3), steady state (§4), initial state (§5); `policy.py`'s `LOG` (all three entry points) and
`CRRA` (terminal *and* `t<T` backward recursion); end-to-end PEE (§6-7); model copies (§9).

**Nested-fixed-point calibration (§8) is implemented for LOG and near-LOG CRRA (`ρ` within ~0.02 of 1) and
untested far from 1** — the CRRA backward recursion and the calibration root together may need a more
robust strategy at ρ ≈ 0.5 or 2. Its outer search has no globalization, which is what made it the one
suite that broke on the 2026-08-24 change of calibration target: from its shipped β guess it walked into a
region where the path solve returns NaN τ and the steady-state `brentq` dies at its own bracket.

## Open items

- `κ`'s db-cache staleness under an endogenous `ε` (see Base conventions).
- The `nMax > 1` multiplicity branch (`roots1d.selectMax`) is unit-tested but never triggered by a real
  calibration.
- No `SolveGrid`-equivalent class for `self.GS` — deferred twice with two real problems in hand. Revisit
  if a third grid-search problem needs the same structure.
- `solveBackward` does not cache evaluated nodes across window expansions (`z_t` is closed-form, so it is
  free to recompute). Add a cache if CRRA ever makes `z` expensive here.
