# Endogenous θ: the paper's counterfactuals across ρ (rerun 2026-08-27)

The paper's experiment set run on the **leaded-choice** model at ρ ∈ {0.5, 1, 2}, φ = 0.5, under the
**proportional** cost (`spec = 'scale'`) and the **common-X** calibration — the two things this rerun
changed, along with holding `θ` at the US design in the exogenous rows. The wedge `p` is calibrated per ρ
so the electorate re-elects the observed design in 2020 (`results/esc/escCalibration{,CRRA}.csv`; ρ=1 is
LOG). Each scenario is reported twice: θ **pinned** at the US design (the exogenous-θ reading) and θ
**chosen**, with the choice binding from the first period so `θ_{t0}` is itself an outcome. Long table:
`results/esc/escExperiments.csv`; producers `runESC.py` (LOG) and `runESCcrra.py --stage shocks` (CRRA),
merged by `collectESCexperiments.py`. ρ≠1 uses the path iteration, certified against the 2-D solver to
±0.01 in θ and 2e-4 in τ.

The calibrated cost: **p = 0.965 / 0.408 / 0.090** at ρ = 0.5 / 1 / 2, and θ* = 0.738 at all three,
because under the proportional cost `f` cancels from the replacement-rate ratio.

## The chosen design θ_{t0} (pinned θ = 0.738 in every row)

| Scenario | ρ=0.5 | ρ=1 | ρ=2 |
|---|---|---|---|
| baseline | 0.737 | 0.738 | 0.739 |
| acute ageing | 0.766 | 0.778 | **0.846** |
| French income distribution | **1.000** | **1.000** | **1.000** |
| French leisure | 0.738 | 0.738 | 0.739 |
| French voting | 0.662 | 0.533 | **0.285** |
| income + voting | 1.000 | 0.972 | 0.508 |
| all three French | 1.000 | 0.972 | 0.508 |

Along the baseline demographic path at ρ=1 the design drifts 0.738 (2020) → 0.748 (2050) → 0.768 (2080)
→ 0.773 (2110 on), tracking the projected fall in ν and flattening when it does (`escPath.csv`).

## What the table says

1. **Acute ageing moves the design Bismarckian at every EIS**, and more strongly the higher ρ — the same
   ordering as the calibrated cost itself, since a higher elasticity strengthens the young's
   forward-looking stake and less friction is needed to hold the choice off the corner.
2. **French inequality corners the design at θ = 1 everywhere.** Under a compressed distribution there is
   little left for a flat benefit to redistribute and the cost of trying is unchanged. This is the result
   most in tension with the cross-section, which shows no clear inequality–design relation.
3. **French voting drives it Beveridgean, and this is where ρ matters most** — 0.662 → 0.285 across the
   range. More relative weight on the poor restores the redistributive force against the forward-looking
   stake, and it is the latter that scales with ρ.
4. **The two together have no sign.** They pull opposite ways and which wins is an EIS question: the
   corner at ρ=0.5, essentially the corner at ρ=1, and 0.508 — well below the US 0.738 — at ρ=2. Whether
   "French characteristics" raise or lower the Bismarckian index is not identified by anything in this
   calibration.
5. **Leisure is the placebo and it passes.** A pure `rescaleX` moves hours and nothing else; the chosen
   design reproduces the baseline's to within 6e-4, which is a bound on the method rather than an effect.

## Three invariances, measured rather than assumed

**The chosen design is invariant to the calibration variant.** Comparing the LOG runs under vector `X`
and common `X` scenario by scenario: baseline, mild, acute, voting and leisure agree to **≤ 1.2e-12 in θ
and 1.2e-14 in τ**, in the chosen reading as well as the pinned one. So does the calibrated `p`, bit for
bit (0.964818 / 0.407612 / 0.090068). Only the scenarios that *swap* `η` differ — under vector `X` the
swap holds `X_i` fixed so `y^η` is not proportional to either country's `z^η`, under common `X` it is —
and `frIncome` hides even that by cornering, so it shows up only on `frBoth`/`frAll` (0.972 against
1.000). A corner masking a real difference is finding #10's shape.

**The chosen design is also invariant to what the exogenous rows are pinned at.** Every number in the
table above reproduces the 2026-08-24 run exactly, which was taken under vector `X` *and* with the
exogenous rows re-deriving θ from `RR0`. Only the exogenous rows moved. That is what makes the current
pairing worth having: both readings now start from θ = 0.738, so the gap between them is the political
response to the changed characteristic and nothing else — where previously the `frIncome` comparison
bundled a design change (0.738 → 0.495) into it.

**`frAll` and `frBoth` differ only by a scale.** Adding French leisure to the pair leaves design and tax
identical and moves only hours (42.46 → 35.19 at ρ=0.5), the scale invariance holding through the
endogenous-θ layer under CRRA.

## What the design response does to the reported outcomes

Small for ageing, decisive for inequality:

| ρ=1, at 2020 | τ pinned | τ chosen | savings pinned | savings chosen |
|---|---|---|---|---|
| baseline | 14.43% | 14.43% | 21.99% | 21.97% |
| acute ageing | 23.25% | 23.19% | 18.99% | 18.94% |
| French income distr. | 13.16% | 13.80% | 22.63% | 21.84% |
| French voting | 15.35% | 15.93% | 21.53% | 21.66% |

For ageing the endogenous design moves τ by at most 0.13 p.p. on a response of eight to ten, and not even
with a consistent sign (it shaves at ρ ≤ 1 and adds 0.05 p.p. at ρ = 2). For inequality it reverses the
reading: taxes come back up toward baseline, and the savings gain the pinned row shows (+0.6 p.p.) is not
reduced but erased (−0.1 p.p. against baseline). Under the wedge, equilibrium taxes are *increasing* in θ
under the French distribution, so a more Bismarckian design and a larger system arrive together.
