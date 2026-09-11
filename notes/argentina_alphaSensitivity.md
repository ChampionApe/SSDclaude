# Argentina: β, R and the savings rate as a function of α (2026-09-08)

Context: the calibrated β for Argentina (0.808 at ρ = 1) sits above the US's (0.761), and far above it for
ρ < 1. This note records what drives that and what a lower capital share does about it. Every number below
is a full recalibration at ρ = 1 on the current code (`notes/argentina_calibrationTarget.md` for the
target), with all four calibrated parameters (β, ω, η0, X0) re-solved and the residual at machine precision.
The α = 0.43 row reproduces `results/paper/calibrationSummary.csv` exactly. Produced by a scratch sweep
(session scratchpad, not committed); to reproduce, load `results/calibration/instances/rho_1.0000.pkl`,
set α through `adjPar`, call `updateAuxPars()` and then `calibrate()`.

## Why β differs from the US

The savings rule works through $B \equiv \beta^{\rho} R^{\rho-1}$, and the K/Y target pins $B$: it is
0.81 in Argentina and 0.76 in the US at every ρ on the grid (the ρ = 1 savings propensity $B/(1+B)$ is
0.447 against 0.432). The whole ρ-dependence of the gap is the conversion
$\beta = (B R^{1-\rho})^{1/\rho}$ evaluated at two different returns. With Cobb–Douglas and full
depreciation $K_t/Y_t = \alpha/R_t$, so α and the K/Y target fix R with no freedom left:
Argentina 30·0.43/3.23 = 3.99 per period (4.7%/yr) against the US's targeted 2.443 (3.0%/yr).
Predicting $\beta_{ARG}/\beta_{US}$ from the ρ = 1 ratio and the two returns alone reproduces the sweep
at every ρ (1.84 predicted vs 1.83 solved at ρ = 0.5; 0.806 vs 0.806 at ρ = 2).

The residual 6% at ρ = 1 is the higher required propensity: Argentina's savings must be 29.5% of net
formal wages to sustain its K/Y, against 25.7% in the US, because the labour share is 0.57 rather than
0.70. Pension crowd-out works the other way (Argentina's PAYG return relative to R is lower) and is
second order.

## α at the measured K/Y = 3.23

| α | β | ω | η0 | X0 | savings rate $s_t/Y_t$ | ι | R per period | R per year |
|---|---|---|---|---|---|---|---|---|
| **0.43** | **0.808** | **2.328** | 0.326 | 0.414 | **14.72%** | 0.365 | 3.99 | 4.72% |
| 0.40 | 0.754 | 2.025 | 0.326 | 0.413 | 14.62% | 0.367 | 3.71 | 4.47% |
| 0.35 | 0.686 | 1.616 | 0.325 | 0.410 | 14.44% | 0.372 | 3.25 | 4.01% |
| 0.30 | 0.642 | 1.295 | 0.325 | 0.407 | 14.27% | 0.378 | 2.79 | 3.47% |

τ = 12.50% and K/Y = 3.2313 are hit exactly in every row. The savings rate is $K_{t+1}/Y_t$, which is
K/Y times the period's output growth; it falls slightly with α because the baseline transition changes,
not because anything targets it. Bold is the published calibration.

Three readings:

- **β falls with α at ρ = 1.** A smaller capital share makes the same capital stock a smaller multiple
  of net wages, so less patience is needed to hold it. The lower R raises pension wealth, which pushes
  the other way, but the labour-share effect dominates.
- **ω falls with α too**, from 2.33 to a range that brackets the US's 1.45 (France 1.42, UK 1.16). A
  lower α brings Argentina's calibration in line with the rich economies on both parameters at once.
- **η0, X0 and ι barely move.** The informal side of the calibration is insensitive to α.

### Projection over ρ ∈ [1, 2]

Using the invariance of $B$ (it drifts by 1% across the grid), $\beta(\rho) = (B R^{1-\rho})^{1/\rho}$
with $B$ = the ρ = 1 β from the table:

| ρ | α = 0.43 | α = 0.40 | α = 0.35 | α = 0.30 | US |
|---|---|---|---|---|---|
| 1.0 | 0.81 | 0.75 | 0.69 | 0.64 | 0.76 |
| 1.2 | 0.66 | 0.63 | 0.60 | 0.58 | 0.68 |
| 1.5 | 0.55 | 0.53 | 0.53 | 0.53 | 0.62 |
| 2.0 | 0.45 | 0.45 | 0.46 | 0.48 | 0.56 |

The α = 0.43 column reproduces the solved grid to within 0.002. For ρ > 1 the lower R *raises* β, and by
ρ = 2 the two effects cancel. Argentina is already below the US for ρ ≥ 1.2 at the current α; any α at or
below 0.40 puts it below at ρ = 1 as well. Below ρ ≈ 0.85 β exceeds 1 at every α considered — as it does
for the US below ρ ≈ 0.7 — and that tail is not treated as a calibration problem.

## Why a lower α is defensible

In the model α is the capital share of *formal* output: informal households produce with a separate
linear technology, outside $Y_t$ and $K_t$. National accounts book the output of unincorporated household
enterprises — where most informal work sits — as *mixed income*, which a share computed as one minus the
wage bill over GDP counts entirely as capital income. That is Gollin (2002), and it is why unadjusted
labour shares are low precisely where self-employment is large. The paper uses Gollin's adjustments 2 and
3 for the US, France and the UK but takes Argentina's 0.43 from Frankema (2010), a reconstruction of
1870–2000, so the two arms are not treated symmetrically in the one economy where the correction matters
most. Two things to check in Frankema: whether the series imputes labour income to the self-employed, and
what it does after 2000, since the calibration year is 2010.

Magnitude: if a share $y$ of GDP is informal mixed income currently sitting in the 0.43, the formal
capital share is $(0.43 - y)/(1 - y)$. The EPH survey puts informal earnings near 5% of GDP (0.40);
shadow-economy estimates for Argentina run to 20–25% (0.29–0.30).

## Caveat: the same logic applied to K/Y pushes back

The Penn World Table's stock is economy-wide and the informal sector is labour-intensive, so a
formal-only capital-output ratio is *higher* than 3.23 by roughly $(1-k_{inf})/(1-y_{inf})$. A higher
K/Y target raises the required savings out of formal wages, and that raises β faster than the lower R
lowers it:

| α | K/Y | β | ω | savings rate | R per period | R per year |
|---|---|---|---|---|---|---|
| 0.43 | 3.23 | 0.808 | 2.328 | 14.72% | 3.99 | 4.72% |
| 0.35 | 3.23 | 0.686 | 1.616 | 14.44% | 3.25 | 4.01% |
| 0.35 | 3.61 | 0.824 | 1.684 | 16.20% | 2.91 | 3.62% |
| 0.30 | 3.61 | 0.765 | 1.339 | 16.00% | 2.49 | 3.09% |
| 0.35 | 4.00 | 0.989 | 1.765 | 18.02% | 2.63 | 3.27% |

So a fully consistent formal-sector calibration is not obviously a lower β. The α correction has a data
basis (Gollin) and restores symmetry with the paper's own US treatment; the K/Y correction needs an
informal capital share no source measures, and PWT's stock also includes housing, which cuts the other
way. Recommendation: correct α, keep K/Y at the measured 3.23, and say in the calibration section that
the share is the formal-sector one net of mixed income, on the same footing as the Gollin adjustments.

## Status

**Adopted 2026-09-08: α = 0.35, K/Y kept at 3.23 — and the tax target moves with α.** Every table above
was computed at τ₀ = 0.125, which is the spending share 7.1% of GDP converted at α = 0.43
(0.071/0.57). The target is τ₀ = 0.071/(1−α), so at α = 0.35 it is 0.1092, and the workbook now carries
the spending share with τ₀ derived. Recalibrated at ρ = 1:

| α | τ₀ | β | ω | η0 | X0 | savings rate | R/yr |
|---|---|---|---|---|---|---|---|
| 0.43 | 0.1246 | 0.808 | 2.328 | 0.326 | 0.414 | 14.72% | 4.72% |
| 0.35 | 0.1250 (stale) | 0.686 | 1.616 | 0.325 | 0.410 | 14.44% | 4.01% |
| **0.35** | **0.1092** | **0.651** | **1.527** | 0.331 | 0.413 | 14.41% | 4.01% |

The extra fall in β is the tax channel: a lower τ raises disposable income and shrinks the PAYG claim that
crowds out private saving, so less patience sustains the same K/Y; R is untouched. ω lands inside the
rich-economy range (1.16–1.45 there). Two other things the pass needed: the CRRA steady-state bracket
derived from α (`crossCuttingFindings.md` #7) and the anchor seeded (`config.ARG['anchorGuess']`).

## If α moves

The full pass is the one in `notes/argentina_calibrationTarget.md` (≈3 h): `dataTargets.py` is not
involved, but the workbook's *Capital income share* cell is the source, then `runCalibration.py --force`,
`runShocks.py --force`, the tests and `build.py`. The Argentina prose in `writing/Paper/Sections/Argentina.tex`
(the Frankema sentence and the p.p. magnitudes) must be re-read against the new tables.
