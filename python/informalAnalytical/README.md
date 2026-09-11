# informalAnalytical

Analytical informal-sector model: overlapping generations with `J+1` household types (type 0 =
informal/hand-to-mouth, `i>0` formal). With log preferences the politico-economic equilibrium reduces to
closed form. Derivation in `writing/informalAnalytical/`; docstrings cite tex labels by name.

This is the **ancestor module**: `US` is a copy with the informal type removed, `InformalSavings` a copy
with type 0 saving. The conventions below are shared with both, and their READMEs point here.

## Timing convention

Docs run `t=1,…,T` with `t=0` pre-determined; code has `db['t']` = `0,…,T-1`, so docs `t=0` is the `s0`
function argument, docs `t=1` is `db['t'][0]` = `Base.tFirst`, docs `t=T` is `db['t'][-1]`. Name
collisions: `db['s0']` is the baseline savings **rate** (reported; `db['KY0']` is the `β` target since
2026-08-24), `db['t0']` is the *index* of the baseline year. Code comments saying "`t=0`" mean
code-relative indexing unless stated.

## Files

| | |
|---|---|
| `base.py` | `Base`/`BaseGrid`/`BaseTime`, the equilibrium equations, one method per tex label; scalar / grid-valued / vectorised over `t` |
| `model.py` | `ModelInformalAnalytical`: db scaffolding (§0-2), EE solve (§3), steady state (§4), initial state (§5), end-to-end PEE (§6-7), calibration (§8), model copies (§9) |
| `policy.py` | `LOG`/`CRRA`: identify the policy sequence only; the model class calls `EE_*_solve`/`EE_report` with the returned `τ` |
| `test.py` | loads `data/ArgentinaTest.xlsx`; a bare `ModelInformalAnalytical()` gives NaN/inf `θ`/`κ`/`ε`, expected |
| tests | `test_ee.py`, `test_cacheParams.py`, `test_crraTerminal.py`, `test_crraBackward.py`, `test_crraPEE.py`, `test_createCopyFromt0.py`; slow: `test_calibration.py` |

## The pattern every numerical problem follows

(i) a **residual** method, cheap, raw `ndarray`; (ii) a **solve** method returning the core solution;
(iii) a shared **report** method expanding it via `base.py`. `τ`/`θ`/`ε`/`s0` are always explicit, never
read from db. Convergence goes through `_checkConverged(res.fun, tol, …)`, which checks `max|residual|`
rather than trusting scipy's `res.success`.

## Base conventions (`base.py`)

- **`cacheParams()` is opt-in and block-scoped.** Every db read is a pandas `.xs()`, per-call overhead
  that is flat in grid size; the block memoises reads (~6.5×). Not always-on because `model.py` rewrites
  db symbols during calibration. `Γh` is computed, not read from `db['Γh']`, for the same reason.
- **Evaluation cost is flat in grid size**, which is why the CRRA solve evaluates the whole Cartesian grid
  in one vectorised pass rather than refining windows per state.
- **Explicit vs db-sourced.** Primitives from db; anything solve- or policy-dependent an explicit argument.
  Known gap: `κ(ε1, t)` exists but its consumers read a cached `db['κ']`; harmless while `ε` is fixed.
- **`hRatio` vs `hηRatio`.** `hRatio = h_{t,i}/h_t`, `hηRatio = h_{t,i}η_{t,i}/h_t`; `hi` needs the
  first, `si_s`'s third term, `c2i`, `dlnc2i_dτ` the second. Was a live bug. `test_ee.py` asserts
  `∑γ_iη_i·hRatio_i = 1` and `∑γ_i·hηRatio_i = 1`.
- **`μ` attaches to a generation**: the old-generation term uses `μ_{t-1,i}`.
- **`FH_*` methods** own the terminal period's formula; where it is a special case of the general one,
  padding (`B=0`/`Γs=0`/`β=0`) is used instead of branching.
- **`BaseTime.Γh()` returns an `ndarray`**, indexed positionally. `Γs`/`B`/`si_s` report on `db['txE']`
  (length `T-1`); everything else length `T`.

## The structural result the LOG solver rests on

No term of `z_t` depends on any lag of `τ`, so `z_t = z_t(τ_t, τ_{t+1})` and the `T`-dimensional root is
triangular, solved exactly by backward recursion over scalar problems. Holds only while `θ`/`ε` are
exogenous. Three entry points: `solveVectorized` (`alg:fast`), `solveBackward` (`alg:gridsearch`, for
diagnosing the FOC), and **`solveRobust`** (vectorised, else backward then polish, else the grid solution
flagged; catches only `RuntimeError`). `solveVectorized` genuinely fails at `ω ≥ 5` on Argentina.

- `tLag` is an explicit argument resolved by `db['t'].get_loc(t)`, never `t - 1`.
- Corners and multiplicity go through `roots1d.selectMax`, not `robustRoot`'s extended grid; `maxResid`
  is restricted to periods with an interior maximum.
- Under CRRA the terminal period needs no numerical differentiation (chain rule on the LOG derivatives),
  but `B_T^i ≠ β_i` makes it state-dependent, `z_T(τ_T, s_{T-1})`; numerical derivatives start at `t<T`.
- `self.GS` holds the named political problems (`solGrids`, `stateGrids`, `gridSettings`), symmetric
  between `LOG` and `CRRA`. `stateGrids['s_']` is an override slot, not a cache.

## Model copies for shock experiments (`createCopyFromt0`)

`m.createCopyFromt0(t0)` returns an independent model with `db['t']` restricted to `>= t0` and
**renumbered from 0** (solvers index caller arrays positionally via `tFirst`), then re-solve seeded with
`m.stateAtT0(report, t0)`. `_sliceDb` (module-level, shared verbatim with `InformalSavings`) mutates db
in place, since `B`/`BG`/`BT`/`LOG`/`CRRA` alias the same dict; `db['t0']` is shifted or set to `None`;
warm-start caches are cleared. Verified: with no shock the copy reproduces the baseline's tail to
~1e-11–1e-13.

## Status

Done and verified: scaffolding and calibration (§0-2), the equilibrium blocks against the primitive
FOCs/budgets, EE solve, steady state, initial state, `LOG` (all three entry points) and `CRRA` (terminal
and `t<T`), end-to-end PEE, model copies. `steadyState_CRRA_bounds` derives the bracket from `Base.ΓsCap`
(finding #7).

**Nested-fixed-point calibration (§8)** works for LOG and near-LOG CRRA (`ρ` within ~0.02 of 1) and is
untested far from 1; its outer search has no globalisation.

## Open items

- `κ`'s db-cache staleness under an endogenous `ε`.
- The `nMax > 1` multiplicity branch is unit-tested but never triggered by a real calibration.
- No `SolveGrid`-equivalent class for `self.GS`; revisit if a third grid-search problem needs it.
- `solveBackward` does not cache nodes across window expansions (`z_t` is closed-form, so free).

Pre-cut long version: `archive/readmes/informalAnalytical_README_2026-09-11.md`.
