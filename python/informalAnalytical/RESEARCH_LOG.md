# Research log — informalAnalytical

Model-specific session log. Structure/design conventions live in this folder's `README.md` (check there
first — this log is for history and open decisions, not current state).

## 2026-07-10
- Migrated `model.py`/`base.py` from the old private `pyDbs` API to public `symMaps`.
- Implemented `base.py`'s factor-price/labour-supply/pension-benefit/§auxiliary building blocks.

## 2026-08-03
- Implemented remaining `base.py` building blocks (`si_s`, formal/informal consumption) and `model.py` §3
  (`EE_LOG_solve`/`EE_CRRA_solve`/`EE_report`). `test.py` runs end to end against the Argentina data.

## 2026-08-04
- Fixed a μ-timing bug: political weights attach to a *generation*, not a period (README's "Political
  weights").
- Implemented the steady state solve (§4) and the initial pre-determined state solve (§5) — the latter
  removed `s0` from `policy.py`'s LOG solve entirely (LOG's `Γs`/`Θh`/`si_s` never depend on savings level).
- Added `gridsearch.robustRoot` and `policy.py`'s `LOG.solveVectorized` (`alg:fast`).
- Renamed `Base.t0` → `Base.tFirst` (was colliding in name only with `db['t0']`, the calibration-year index).
- Added `model.py` §6, `solvePEE_LOG`.

## 2026-08-05 — robust LOG solve
- Built the backward grid-search LOG solve (`alg:gridsearch`). Key structural result: no term of `z_t`
  depends on a lag of `τ`, so the `T`-dim simultaneous root is triangular and solves by backward scalar
  recursion (`policy.py`'s `solveBackward`).
- Two bugs fixed: `roots1d` dropped zeros at the first/last grid node (exactly where corners land);
  `solveBackward`/`stateGrid` assumed `db['t']` is a literal integer range (`tLag = t-1` by arithmetic) —
  fixed to resolve via `db['t'].get_loc(t)`, works for any ordered Index.
- `alg:fast` genuinely fails at `ω≥5` on this calibration (scipy reports false success); `solveRobust`'s
  fallback is load-bearing, not hypothetical insurance.

## 2026-08-05 (cont'd) — CRRA terminal period
- Implemented the CRRA terminal-period PEE solve (`policy.py`'s `CRRA.solveTerminal` etc.) plus the
  `gridsearch` machinery it needed (`CartesianGrid`, vectorized `roots1d`, `griddedInterp1D`) and
  `base.py`'s `cacheParams()`.
- Key finding: the terminal FOC needs no numerical differentiation — each term is `(consumption)^{1-1/ρ}`
  times the same log-derivative already built for LOG.
- Profiling: one FOC grid evaluation costs ~1.8ms flat in grid size (~43% pandas `.xs()` overhead) — this
  is why `cacheParams()` exists (6.5x/eval) and why CRRA evaluates the whole grid at once rather than
  refining a window.
- Deferred porting the inspiration's `SolveGrid` class; adopted the lighter `self.GS` dict instead (see
  README's "Named grid-problem structure").

## 2026-08-05 (cont'd) — CRRA t<T recursion + solvePEE_CRRA
- Implemented the `t<T` backward recursion. The fixed point is 2D not 3D: `Θ_{s,t}` doesn't depend on
  `s_{t-1}`, only the residual's `(s_{t-1}/ν)^σ` factor does.
- Bug (caught by a user question, not testing): `hatc1i`'s literal `(1+B)^{1/(1-1/ρ)}` overflows float64
  as `ρ→1` — fixed by carrying `(1+B)·c̃^p` in log space instead (`hatc1iPow`/`lnhatc1i`), never
  materializing the level.
- `roots1d.selectMax` extended for NaN/infeasibility masking (a `(τ,s_)` cell can leave the state grid).
- `steadyStatePEE_CRRA` needed because CRRA's `τ[tFirst]` depends circularly on `s0` (unlike LOG).

## 2026-08-05 (cont'd) — usage reduction
- Swept `base.py`/`policy.py`/`model.py` docstrings down to equation refs/shape conventions/genuine
  gotchas; recorded the convention in root `CLAUDE.md`. Verified behavior-neutral (full suite unchanged).
- Saved feedback memories: write test checks directly into the real test file (no throwaway-then-promote
  step); prefer `Grep`+narrow `Read` over re-reading whole files.

## 2026-08-06 — calibration (`model.py` §8)
- Implemented the nested-fixed-point calibration: one 4-D root over `(β,ω,η0,X0)` against
  `eq:calibration`'s four targets (savings rate, tax rate, and η0/X0 self-consistency), each residual
  evaluation a full PEE solve. `base.py` §10 (`savingsRate`/`calibrationη0`/`calibrationX0`) plus
  `ΘhFromH` (inverse of `Base.h`, recovers Θh from a solved path regardless of LOG/CRRA/terminal origin).
- **Bug caught before shipping, not after**: `_calBounds` originally capped `β∈(0,1)`, on the assumption
  β is a discount factor. It isn't — `simpleβ` sets `βj=β·p_j`, so `β·p_j` is the discount factor, not β
  itself — and the Argentina savings-rate target needs `β≈1.18`. The cap made `scipy.optimize.root` stall
  ("not making good progress") rather than fail loudly. Fixed to positivity-only bounds; guarded by
  `test_calibration.py`. Also noted: `test.py`'s `pars` never sets `'pj'`, so `p_j=1` throughout on the
  current data — real survival-rate data would make this distinction load-bearing.
- Converges in ~4s / 36 PEE solves on Argentina (LOG), residual `~1e-10`; the two CRRA points (ρ=0.98/1.02,
  warm-started) land within ~1–3% of the LOG parameters.
- Explored and reverted two variants: (i) a 2-D search over `(β,ω)` with `η0/X0` converged to
  self-consistency by an inner successive-substitution loop each evaluation — worked but cost *more*
  than the 4-D root (the inner loop needs ~13 passes/evaluation); (ii) a 2-D search with `η0/X0` updated
  once per outer evaluation and folded into the residual directly — broke `scipy`'s finite-difference
  Jacobian, since mutating `η0/X0` inside the residual makes it depend on call history rather than being a
  pure function of `x` (measured spurious Jacobian entries of order 100+). If a faster/robust-at-extreme-ρ
  calibration is needed later, revisit as: freeze `η0/X0` for the whole root solve, refresh only between
  solves — not implemented, since the accuracy/speed tradeoff wasn't judged worth it yet.
- Verified `_calSetPars`'s db rewrites don't interact with `cacheParams()`: every cache block lives inside
  `policy.py`'s solve methods, which run strictly after `_calSetPars` finishes writing, so no write ever
  lands inside a live block (checked directly, not just by inspection, in `test_calibration.py`).

**Next**: `ρ` far from 1 (~0.5, ~2) is untested — the CRRA backward recursion + calibration root together
may need a more robust solve strategy there (see "Known limitations" in README).
