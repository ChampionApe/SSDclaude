# Endogenous θ: the paper's counterfactuals across ρ (2026-08-24)

The paper's experiment set (acute ageing, French income distribution, leisure preferences, voting) run
on the **leaded-choice** model at ρ ∈ {0.5, 1, 2}, both wedge specs, φ = 0.5, with the wedge `p`
calibrated per (ρ, spec) so the electorate re-elects the observed design in 2020
(`results/esc/escCalibrationCRRA.csv`; ρ=1 is LOG). Each scenario reported twice: θ **pinned** at the
calibrated design (the paper's exogenous-θ reading) and θ **chosen** (the leaded choice binding from
t0, so θ_{t0+1} is the first design it can move). Long table: `results/esc/escExperiments.csv`;
producers: `runESC.py` (LOG), `runESCcrra.py --stage shocks` (CRRA), merged by
`collectESCexperiments.py`. ρ=1 solves are exact policy functions (LOG); ρ≠1 use the path iteration,
certified against the 2-D solver (`num_esc.tex` alg:esc:crra2D) to ±0.01 in θ, 2e-4 in τ.

## The chosen design θ_{t0+1} (spec = scale; baseline θ* = 0.738 at every ρ)

| Scenario | ρ=0.5 | ρ=1 | ρ=2 | pinned θ (all ρ) |
|---|---|---|---|---|
| baseline | 0.741 | 0.738 | 0.739 | 0.738 |
| acute ageing | 0.774 | 0.775 | 0.815 | 0.738 |
| French income distribution | **1.000** | **1.000** | **1.000** | 0.495 |
| French leisure | 0.741 | 0.738 | 0.739 | 0.738 |
| French voting | 0.664 | 0.536 | **0.281** | 0.738 |
| income + voting | 1.000 | 1.000 | 0.692 | 0.495 |

Under spec = flat (θ* and p jointly identified, so the baseline design itself moves with ρ:
0.691/0.716/0.733) the same shape holds with everything less extreme: frIncome 0.877/0.905/1.000,
frVoting 0.665/0.628/0.458, frBoth 0.849/0.828/0.716, acute 0.702/0.726/0.764.

## What the table says

1. **Acute ageing moves the design Bismarckian at every EIS**, and more strongly the higher ρ
   (+0.04 at ρ=0.5, +0.08 at ρ=2 under scale). The endogenous design slightly *damps* the tax response
   (τ_{t0+1} 0.2389 chosen vs 0.2402 pinned at ρ=0.5): part of the fiscal adjustment happens through
   design rather than size.

2. **The French income distribution corners the chosen design at θ = 1 at every ρ under scale.** The
   data-implied design for French inequality is θ* = 0.495; the model's electorate un-does the
   flattening entirely. The design response also erases most of the savings-rate gain the pinned
   reading shows (sr_{t0+1} 0.208 chosen vs 0.242 pinned at ρ=0.5) and pulls the tax back up
   (0.189 vs 0.171). This is the counterfactual version of the fig-1.1 finding that the model ties θ
   far more tightly to inequality than the cross-section does.

3. **Voting is the one experiment whose strength is sharply ρ-dependent.** France's flat voting
   profile pushes Beveridgean: −0.07 at ρ=0.5, −0.20 at ρ=1, −0.46 at ρ=2 (scale). Consequently the
   **income+voting net effect flips sign territory across the EIS range**: cornered at θ=1 for ρ ≤ 1,
   interior (0.69 scale / 0.72 flat) at ρ=2 — the two French characteristics pull in opposite
   directions and which one wins is an EIS question. That is the sharpest new fact in this table:
   whether "French characteristics" raise or lower the Bismarckian index in the model depends on a
   preference parameter the cross-section cannot pin.

4. **Leisure preferences leave the design untouched at every ρ** (chosen θ within 1e-3 of baseline) —
   the CRRA counterpart of the LOG scale-invariance argument: a pure scale on X moves nothing the
   political trade-off cares about. A useful placebo: the machinery does not manufacture design
   responses where the theory says there are none.

Mild ageing exists at ρ=1 only (the session's scope was the acute row); add
`--scenarios baseline mild ...` to the CRRA driver to fill it if wanted.
