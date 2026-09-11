# Planning: technical notes / numerical appendix for the analytical model

Session working note (2026-08-25). Exhaustive inventory of candidate content for the
`informalAnalytical` numerical documentation, followed by a recommendation for what the
public-facing technical notes should keep. Sources: `writing/informalAnalytical/num*.tex`,
`python/informalAnalytical/README.md`, `python/gridsearch/README.md`.

## A. Exhaustive list of candidate items

### 1. Problem formulation and state-space reduction
1. Solving the political problem through its **first-order condition as a root problem** rather
   than maximising the objective directly — the device that keeps the distribution of past
   savings out of the state space (`num_robustroot` intro).
2. The reduction itself: `s_{t-1,i}/s_{t-1}` is a closed-form function of `τ_t` at the previous
   period's parameter vintage, so no distributional state is ever carried.
3. **LOG triangularity**: no term of `z_t` depends on any lag of `τ`, so `z_t = z_t(τ_t, τ_{t+1})`,
   `z_T = z_T(τ_T)` — the T-dimensional simultaneous root is triangular and solves exactly by
   backward recursion over *scalar* problems; removes initial-guess dependence. Holds only while
   `θ`, `ε` are exogenous.
4. **CRRA**: `s_{t-1}` returns as a state; terminal problem is `z_T(τ_T, s_{T-1})`; all marginal
   indirect utilities take the form (level)^{1−1/ρ} × (log-derivative), so the log-derivatives are
   shared with the LOG implementation by the chain rule and the terminal period needs no numerical
   differentiation at all.

### 2. Bounded-root reparameterization (robustRoot)
5. The auxiliary problem `h(z,τ) = z − |z|·g(τ)`: lets an unconstrained gradient-based solver
   search all of ℝ while `f` is only ever evaluated on `[l,u]`; boundary solutions identified at
   `τ̃ = 1 + 1/a₁` and `τ̃ = −1/a₀` even when `f` has no interior root.
6. The **extended grid**: outer nodes at `l − 1/a₀ − δ` and `u + 1/a₁ + δ`. A corner solution is
   encoded as an *exact zero* at an outer node, invisible to a pure sign-change test; the `δ`
   offset restores a sign change in the outer cell, and linear interpolation there returns the
   corner exactly. `a₀, a₁` serve double duty (penalty slopes and node placement) and must be kept
   consistent.

### 3. Grid-search selection machinery
7. **Boundary behaviour**: `z_t → −∞` as `τ_t → 1` via the `1/(1−τ_t)` factor; evaluate on
   `[l,u]` with `u < 1` strictly; `z_t(u) < 0` is a calibration property, checked not assumed. The
   real difficulties are lower-corner detection and multiplicity, not existence.
8. **Roots vs maxima**: an upward crossing of `z_t` is a local *minimum* of the objective — only
   downward crossings are admissible candidates.
9. **Objective recovery on the same grid**: `V̂_t = ∫ ẑ_t` — the cumulative trapezoid of the *same*
   piecewise-linear interpolant used to locate crossings, hence exact for that interpolant.
   Candidate set `{l, u} ∪ {downward crossings}`; the argmax rule resolves corners and
   multiplicity under one criterion. Accuracy demanded: only ranking well-separated candidates.
10. **Exact-zero handling** in crossing detection (sign-run rule, `tol = 0` default) — required
    because robustRoot encodes corners as identical zeros.
11. The three LOG entry points: `solveVectorized` (simultaneous root), `solveBackward` (triangular
    grid search, diagnostic-grade accuracy), `solveRobust` (try fast → grid → warm-started polish,
    flagged if unpolished). Catches only the convergence `RuntimeError`, never a bare except.
12. **Do not trust `res.success`**: scipy reported `success=True` at `max|residual| = 2.1e−8`
    while genuinely failed at `ω ≥ 5`; convergence is checked on `max|residual|` directly.
13. Grid-search implementation facts: evaluation cost is **flat in grid size** (per-call overhead
    dominates), which is why the whole Cartesian grid is evaluated in one vectorized pass rather
    than refining windows per state; `tLag` explicit (position in the index, not label
    arithmetic); residual reporting restricted to interior maxima — at a corner `z ≠ 0` is the
    correct answer.

### 4. CRRA machinery
14. Grids `S` (predetermined states, solved *at*) vs `S′` (candidates, searched *over*); bounds
    from steady-state dynamics (`s*(τ)` decreasing, `u_s = 1.25·s*(0)`); the state-grid override
    slot is settable, not an auto-populated cache (silent-staleness rationale).
15. The economic equilibrium at `t < T` as a **fixed point in `s_t`**: residual
    `R_t(τ_t, s_t; s_{t-1}) = Θ_{s,t}(τ_t,s_t)(s_{t-1}/ν_t)^{α(1+ξ)/(1+αξ)} − s_t`; a genuine
    root problem (continuation policies), not a maximisation.
16. **The broadcast trick ("two-dimensional, not three")**: nothing in the forward pass depends on
    `s_{t-1}`; it enters only through an explicit scalar factor, so the expensive evaluation is on
    `T̃ × S′` once and every `s_{t-1} ∈ S` follows by broadcast.
17. **Feasibility mask** over `T̃ × S`: the root need not lie inside `S′`; require ≥ 2 feasible
    `τ_t` per state; mask cells individually rather than assuming a contiguous feasible interval.
18. **Which derivatives may be taken on the grid**: `d ln(c₂ᵢ)/dτ` *must* come from its closed
    form — a grid derivative would include the predetermined `s_{t-1,i}/s_{t-1}` channel, which is
    wrong, not imprecise. `d ln(c̃₂⁰)/dτ` may go either way (closed form used). Numerical:
    `h_t`, `ĉ₁ᵢ`, `c̃₂⁰_{t+1}`. The LOG and CRRA closed forms share one formula via
    `∂ln(Θ_h)/∂τ = d ln(h)/dτ` at fixed `s_{t-1}`.
19. **The `ĉ₁ᵢ` absorption and the ρ → 1 overflow trap**: `(1+B)^{1/(1−1/ρ)}` is never formed as a
    level; the two safe identities avoid an exponent that diverges (already 1001 at ρ = 1.001).
20. Light smoothing of the selected `τ_t(s_{t-1})` before interpolation (kinks inherited from
    interpolated continuation policies).
21. Shared `gridsearch` facts the recursion and calibration lean on: fixed-knot smoothing
    (`LSQUnivariateSpline`) so the smoother is a *linear map* of the data — an adaptive knot count
    is an integer that flips and puts discontinuities inside a residual that gets differentiated;
    interpolants extrapolate rather than clamp; NaN survives the non-linear interpolation kinds
    (fill-and-mask, never "simplified" away).

### 5. Economic equilibrium, steady state, initial state
22. LOG EE: fully closed-form forward pass (Γ_s → Θ_h → Θ_s → iterate `s_t`), no root finding.
23. CRRA EE: square nonlinear system in `(Γ_s, h, s)` vectors.
24. Steady state: LOG closed form; CRRA reduced to a *bounded scalar* search in `Γ_s` with a
    derived bracket `Γ_s ∈ (0, B/((1+B)(1+ξ)))` → golden-section on `(0, 0.75)`.
25. Initial state `s₀` defaulting to the steady state at first-period parameters.

### 6. Calibration
26. Nested fixed point: inner full-PEE solve; outer root over `(β, ω, η₀, X₀)`; auxiliary
    parameters (`ε` from `β`, `κ` from `ε`) refreshed inside the loop.
27. The K/Y target and the `n_yr = 30` factor (stock vs thirty years of flow); the savings rate
    reported but not targeted (it is `K_{t0+1}/Y_{t0}`, not an annual NA savings rate).
28. Known limitations: outer search has no globalization; tested for LOG and near-LOG CRRA only.

### 7. Model copies / shock experiments
29. `createCopyFromt0`: renumbering (not just restricting) `db['t']` because callers index
    positionally; in-place db mutation (aliasing across B/BG/BT/LOG/CRRA); `t0` shifted or set to
    `None`; warm-start caches cleared; state seeding kept outside the copy; verified tail
    reproduction at ~1e−11–1e−13.

### 8. Conventions and infrastructure (repo-internal)
30. Timing conventions (docs `t = 1..T` vs code `0..T−1`; the two `s0`s; the two `t0`s).
31. `cacheParams` block-scoped memoisation (per-call `.xs()` overhead, ~6.5× speedup, deliberate
    opt-in against silent staleness); explicit-vs-db-sourced argument convention.
32. `hRatio` vs `hηRatio` distinction and its sanity checks; political weights attaching to
    generations; `FH_*` padding-vs-branching; terminal-domain lengths (`T−1` vs `T`).
33. The residual/solve/report pattern; the PASS/FAIL test harness; test suite inventory.

## B. Recommendation for the public technical notes

**Keep, as the spine of the appendix (the methodological contributions):**

1. *State-space reduction* — items 1–4 as one section: FOC-as-root formulation, the closed-form
   `s_{t-1,i}/s_{t-1}` reduction that keeps the savings distribution out of the state space, LOG
   triangularity, and the CRRA (level)×(log-derivative) structure that reuses the LOG derivatives.
2. *Robust bounded grid search* — items 5–10 as one section: the reparameterization, the
   extended-grid corner encoding (with the exact-zero point), and the
   selection-by-objective-integration rule on the same grid. This is the "corners and gradients on
   one grid" innovation and deserves the fullest treatment.
3. *The CRRA broadcast structure* — items 15–16: the fixed point in `s_t` and why it costs a 2-D
   evaluation plus a broadcast, tied to the flat-in-grid-size cost fact (13) in one sentence.

**Keep, as a short "gotchas" list (correctness, not performance):**

- Which derivatives must be closed-form (18) — the one error that is *wrong, not imprecise*.
- The ρ → 1 overflow identities (19).
- Corner = exact zero, so sign-change tests are insufficient (6/10).
- Upward crossings are minima (8).
- Check `max|residual|`, not the solver's success flag (12).
- Fixed-knot smoothing wherever the output is later differentiated (21) — one paragraph, with a
  pointer to the InformalSavings notes for the full account.

**Compress to a sentence or two each:** EE/steady-state/initial-state (22–25) and calibration
(26–27) — state the structure and the target, skip the procedural detail.

**Leave out of the public notes** (keep in READMEs / research logs): items 11 (entry-point
taxonomy beyond naming `solveRobust` as the default), 13's timing measurements, 20's tuning
advice, 28–33 — verification measurements, performance internals, repo conventions, copy
mechanics, test inventories. These are for maintainers, not readers, and the repo being public
means the curious reader can still find them where they live.
