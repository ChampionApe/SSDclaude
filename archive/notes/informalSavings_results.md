# InformalSavings: results

Demoted from `python/InformalSavings/README.md`. Live files are named per section; everything here is a
reading of a solved csv, not something needed to run the module.

## The ρ sweep — `results/calibration/informalSavings_rhoGrid.csv`

2026-08-24, `ρ ∈ [0.5, 2.0]` step 0.1, on the capital-output target `KY0 = 3.2313`, at
`smoothKnots=4` / `interpKind='cubic'` on both solvers, `nι=ns=45`, scipy's default outer step. One
pickled instance per point in `results/calibration/instances/`.

- **16/16 solved, first attempt, no step-halving.** `KY` = 3.2313 to 1.6e-10 and `τ` = 0.125 to 3.6e-10 at
  every point; `residual` ≤ 1.6e-10, `nRoots = 1` everywhere. ≈2 h (430–560 s/point on CRRA, 26 s at the
  LOG anchor).
- `β`/`ω` move smoothly and monotonically (`β`: 2.63 at ρ=0.5 → 0.81 at ρ=1 → 0.45 at ρ=2.0); `η0`/`X0`
  stay near-flat (0.3260–0.3263, 0.4135–0.4160). Occupancy 78–80% (`ι`) / 64–80% (`s`).
- **`β` crosses 1 between ρ=0.8 and ρ=0.9** (1.086 and 0.921), against ρ≈1.15 on the savings-rate target.
  The whole curve is ≈0.65× its old self, so the retarget shrank the β>1 region without removing it.
  `notes/argentina_calibrationTarget.md`.
- **`verifyResidual` degrades down the low-ρ tail**: ~6e-6 at ρ=1, 1.0e-4 at ρ=0.8, 4.9e-4 at ρ=0.6,
  1.2e-3 at ρ=0.5. Those bottom two rows are converged on their own 45×45 grid but **not resolved** on the
  60×60 verification grid — read them as indicative. Refining that tail is open.
- **The ρ≈0.7 pocket is gone**: 12 evaluations, 4.5e-14, where under the old target ρ ∈ [0.7, 0.775] would
  not converge at all. Whether that is the target or the different β it lands on has not been separated.

The calibrated anchor at ρ=1 is `β=0.807610, ω=2.327810, η0=0.326087, X0=0.414067` (LOG, 25 evaluations,
~26 s, `max|residual| = 1.6e-10`), pinned by `test_calibrationGrid.py`.

**History of the anchor**, since the moves are of very different kinds. The 2026-08-24 change of target is
the largest by two orders of magnitude and is not a solver-side move at all — it is a different moment.
All the earlier readings are on the savings-rate target:

| | β | ω |
|---|---|---|
| pre-2026-08-19 grid rule | 1.212188 | 2.638654 |
| after the grid retune, anchor still on the adaptive smoother | 1.211615 | 2.636787 |
| pinned knots, anchor still on **linear** interpolants | 1.210923 | 2.645212 |
| pinned knots + cubic (2026-08-20) | 1.211968 | 2.641368 |

**The 2026-08-20 interpolant move is the only entry with an independent check on it**, which is why a
*looser* residual there was not a regression: four CRRA points of a fine grid ρ ∈ {0.98,…,1.02} predicted
`β=1.211956, ω=2.641327` at ρ=1 by extrapolation onto their own gap, and the patched anchor landed on that
to 1.2e-5/4.1e-5 where the previous one missed by −1.03e-3/+3.88e-3. The earlier `1.5e-11` was the solver
converging *precisely* onto a jittering answer. That fine grid has not been re-run on the current target;
the anchor now rests on `test_calibration.py`'s cold solve agreeing with the sweep to 1e-6.

**Two results from `calibrateGrid` worth carrying.** `η0` and `X0` barely move with ρ (0.00%/0.02% spread
against 29%/22% for β/ω) — those two self-consistency conditions are nearly solved by direct substitution,
and only `(β,ω)` are genuinely identified by the data targets. And the **extrapolated warm start buys
nothing at Δρ=0.1 once the interpolants are `C¹`** — warm and cold both converge in 12 evaluations to
identical parameters, so its value is robustness at larger steps, not speed.

## The universalisation shock — `results/shocks/universal_*.csv`

LOG at ρ=1, CRRA elsewhere; all 16 ρ for `match`, ρ=1 only for `flat`. Reform at `t0`; `ε` changes only,
`θ` fixed. `b^0/b^{refType}` matches its target to ≤2.3e-16 at every `match` point, confirming
`installEps`'s `db['κ']`/`db['κ[t-1]']` rewrite stayed consistent across the grid.

**`match` (`b^0=b^1`), impact-period response relative to baseline** (`τ_0=0.125` throughout; calibrated
`ε` is 0.305 at ρ=1, universal target `ε^U=0.546`, near-flat in ρ):

| `ρ` | `Δτ` | `Δs` | `Δι` | `Δc^{1,0}` | `Δc^{2,0}` |
|---|---|---|---|---|---|
| 0.5 | +3.12% | −0.54% | −4.73% | +2.33% | +8.34% |
| 1.0 | +11.49% | −2.09% | −7.33% | +4.11% | +12.29% |
| 1.3 | +12.10% | −2.06% | −7.94% | +4.30% | +12.65% |
| 2.0 | +11.05% | −1.62% | −8.74% | +4.35% | +12.26% |

Every response is **larger than on the superseded savings-rate target** (`Δτ` at ρ=1 is +11.49% against
+7.22%) and in the same direction: a less patient electorate leans harder on the pension system when the
informal block is brought into it.

> **`Δc^{1,0}` and `Δc^{2,0}` at `t0` are contaminated — do not quote them.** The `EE_report` proxy-state
> defect (README, Open items) puts ~+5.5% of level into `c20`'s impact response, so that column is roughly
> half artifact. `Δτ`/`Δs`/`Δι` and everything from `t0+1` on are clean.

`Δι` is monotone in ρ across the whole grid; `Δτ` and `Δs` are **not** — both rise from ρ=0.5, turn over
around ρ≈1.3 (`Δs` at ρ≈1.1), and `Δτ` falls back to 11.05% by ρ=2.0. A ρ=1-only result could not show
that hump, since ρ=1 sits on the near side of the peak. **Not investigated mechanically.** It survived the
change of target unmoved in location, which is evidence it is a property of the recursion rather than of
the calibration. At `t0+1` the same shape appears, peaking near ρ≈1.5.

**The two readings bracket the status quo rather than differing in degree.** `match` raises `ε` 0.305 →
0.546; `flat` (`ε = 1-θ`, the non-contributive component only) cuts it to 0.161, and every response
reverses sign: on impact τ `0.1250 → 0.1394` against `→ 0.1112`, `Δι` −7.3% against +3.3%, `Δs` −2.1%
against +2.3%, `Δc^{1,0}` +4.1% against −2.5%. Either reading alone would have looked like a result.

Two things before reading more into it. `match` against `j=1` **is still a benefit rise** even though it
equalises type 0 to the *lowest* formal type: the calibrated `ε` is `0.7 × (relative benefit of j=2) ×
0.535` (an early-retirement discount), so the status quo already sits below type 1's benefit — the sign
comes from the coverage rate and the discount, not from the reference type. And under `flat` the
generation already old at `t0` is almost unaffected (`Δc^{2,0}` +0.1%) despite the 52% cut, because `κ`
falls with `ε` and `b̄ ∝ 1/κ_{t-1}`; only from the next period does `c^{2,0}` fall by ~5–6%.

## The reform decomposed — `results/shocks/eeOnly_match_rho*.csv`

Taxes held at the baseline path, `ε` at the universal value, all 16 ρ, run with `--control`. At ρ=1 the
savings rate goes 14.725% → 14.862% against the full effect's → 14.446%: **the pure equilibrium effect is
positive and the full effect negative, at every ρ on the grid**, so the tax response is what turns the
sign. That survived the change of target unchanged in sign and close to unchanged in size — the strongest
single piece of evidence that the decomposition is a property of the model rather than of the calibration.
Labour supply moves the same way in both, with the equilibrium part ≈1/3 of the total. Under a minute for
the whole grid, so re-run it whenever the baseline moves.

## The `(ε, θ)` comparative statics — `results/sweeps/epsThetaGrid_rho1.0000.csv`

27 `ε` × 14 `θ` = 378 points at ρ=1 with the calibrated parameters pinned, `nRoots == 1` everywhere. Level
signs: `τ` ↑ in `ε` and ↓ in `θ`; savings rate and hours the reverse; `ι` ↓ in both. Marginal effects
shrink in `ε` for `τ`/savings/hours and grow in `θ` — **except `ι`, whose marginal effect in `ε` grows
monotonically** (0.036 → 0.108 across the grid at the calibrated `θ`, monotone in 11 of 14 `θ` columns).
That used to contradict `Quant.tex`'s "in all cases"; the paragraph was rewritten on 2026-08-25 and no
longer makes the claim, so this is a property of the surface rather than an outstanding discrepancy.

**The `ε=ε^U` row is not the universalisation shock** and does not match it (τ +15.10% vs +11.49% at ρ=1):
the grid re-solves the whole horizon under the new `ε`, so the state entering `t0` has itself adjusted,
while the shock is unanticipated and seeds from the pre-reform state. Two different experiments, both
correct.

**These figures are from the 2026-08-25 re-solve.** The `392`-point grid this section previously described
was the two-calibration file — 28 `ε` columns because the pre-retarget calibrated `ε` was still in it, its
numbers a mix of two parameter sets. A note that records a corrupted artefact's *shape* as a fact is how
that state stayed invisible; `crossCuttingFindings.md` #13.
