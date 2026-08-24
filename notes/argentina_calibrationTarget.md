# Argentina: the calibration target (2026-08-24)

Replaces the three notes that worked this out — `argentina_betaCalibration`, `_savingsTargetAudit` and
`_capitalOutputTarget_runbook`, at `c958031^:notes/` if the derivation is wanted.
The general lesson is `crossCuttingFindings.md` #12.

## What changed

`db['KY0'] = 3.2313` — Argentina's capital-output ratio in 2010, the calibration year (PWT 11.0, derived
by `python/paper/dataTargets.py` into `data/argentina_calibrationTargets.csv`) — replaces the savings-rate
target `db['s0'] = 0.184`. It identifies β through `Base.capitalOutputRatio` (`eq:calibration:KY`) in both
Argentina variants. Executed in full on 2026-08-24: the ρ grid, all four experiments, the tests and the
paper outputs were re-run on it.

## Why the old target was wrong

Not the denominator, and not the datum's sector coverage — **the numerator's time dimension**. A period
is 30 years with full depreciation, so the model's moment is

$$sr \;=\; \frac{s_t}{Y_t} \;=\; \frac{K_{t+1}}{Y_t},\qquad
\frac{K}{Y}\bigg|_{\text{annual}} = 30\,\frac{K_t}{Y_t} = \frac{30\alpha}{R_t},$$

a **stock over thirty years of output**. The 18.4% datum is an *annual flow* national-accounts saving
rate; thirty years of it cumulates to 5.5 years of GDP, where the stock is 3.2–3.6. The gap is the
capital that depreciates *inside* the window, which the data's gross flow replaces and a
one-purchase-per-period model does not have. The target therefore asked for about half again the capital
Argentina has, and β absorbed it — 1.212 at ρ=1, rising to 4.28 at ρ=0.5.

Three independent checks that this is the right reading:

- **The neighbouring target *was* converted.** Pension spending 7.1% of GDP ÷ (1−α) = 0.125 is exactly
  right, so the denominators were handled correctly throughout — which is why dividing `sr` by (1−α) as
  well (an early proposal) fixes the wrong thing and overshoots: its 0.105 implies K/Y = 2.33, below
  anything measured for Argentina.
- **Implied depreciation.** The model writes off `K_t` over the period: 1/30 = 3.33%/yr against the
  data's 0.1096/3.575 = 3.07%/yr.
- **The US arm says it out loud** — it targets a "30y interest" of 2.443, an unambiguously 30-year object
  and by the identity above the same object as K/Y.

## Provenance of the superseded datum

The only recorded source was one sentence in `Quant.tex` ("the private savings rate ... relative to GDP
per capita ... 18.4% from World Bank national accounts data, 1994–2007"). The workbook carried the bare
number with no series id, vintage or window. **No current-vintage World Bank series equals 18.4%** —
nearest are gross saving 17.0% of GDP / 17.7% of GNI and gross capital formation 17.9% — and Argentina's
2014 rebasing means the original vintage is not recoverable. It is also not *private* (the World Bank
publishes no private-saving series; gross saving is national) and not *net* (net national saving over the
window is 6.8% of GNI). The sector label was a reporting error, not a calibration error: households own
the entire capital stock here, so national saving is the right aggregate.

## The map from target to β (ρ = 1, LOG)

Worth keeping because re-deriving a row costs a calibration. From
`results/calibration/informalSavings_KYGrid.csv` and its savings-rate predecessor; every row converged to
|residual| ≤ 2e-11, and the 0.184 row reproduces the sweep's β = 1.211968 exactly.

| target `s0` | implied K/Y | β | ω | R (30y) | |
|---|---|---|---|---|---|
| 0.1840 | 4.01 | 1.2120 | 2.641 | 3.221 | ← superseded |
| 0.1676 | 3.66 | 1.0126 | 2.486 | 3.52 | 1980–2010 mean |
| 0.1635 | 3.58 | 0.9684 | 2.452 | 3.61 | 1994–2007 mean |
| **0.1472** | **3.23** | **0.8076** | **2.328** | **3.99** | ← **adopted** (2010) |
| 0.1300 | 2.86 | 0.6611 | 2.217 | 4.505 | |
| 0.1050 | 2.33 | 0.4831 | 2.085 | 5.546 | |

**β crosses 1 at K/Y ≈ 3.64–3.68**, which is precisely the US arm's implied ratio (30×0.3/2.443). Any
target at or below the US capital-output ratio delivers β < 1 at ρ = 1; the old one sat above it.

**Why the calibration year rather than a 30-year mean.** The tax rate, the replacement-rate ratio, the
coverage share and the household survey are all measured at or around 2010, and Argentina's K/Y moves
enough over the preceding decades (4.28 in 1990, 3.17 in 2007) that a thirty-year average describes a
different economy from the one the other targets describe. It also clears β = 1 rather than straddling it.

## What the run produced

β = 0.8076 at ρ=1 and **crosses 1 between ρ=0.8 and 0.9** rather than at ρ≈1.15 — the curve is ≈0.65× its
old self at every ρ, so the retarget shrank the β>1 region without closing it. The **ρ≈0.7 pocket is
gone** (12 evaluations, 4.5e-14, where it previously failed under four strategies).

One paper claim changed rather than just its numbers: the reform now accounts for +0.82 p.p. of GDP of
the observed 1.9% rise in pension spending — a little over two fifths, where the text said "almost the
entirety". A check that did land: τ × (1−α) = 7.12% of GDP against the 7.1% ANSES datum.

## Still open

- **β > 1 for ρ < 0.85.** A decision, not a task. Remaining options if it needs closing: target an
  Argentine 30-year real return directly (hard datum); or present rather than repair — report β^(1/30)
  (1.0064/yr at the old ρ=1) and the effective old-age weight β·p < 1, admissible in an OLG model though
  not at ρ=0.5.
- **`verifyResidual` degrades down the low-ρ tail** — 1.2e-3 at ρ=0.5, 4.9e-4 at ρ=0.6. Those rows are
  converged but not resolved.
- `writing/informalSavings/num_calibration.tex`'s *Residual* paragraph still quotes η0 = 0.326 and
  X0 = 0.408; both moved.

## If the target moves again

Order matters and the whole pass is ≈3 h of machine time.

```
.venv\Scripts\python.exe python\paper\dataTargets.py           # re-derive the datum
.venv\Scripts\python.exe python\paper\runCalibration.py        # stage (i), ~2 h
.venv\Scripts\python.exe python\paper\runShocks.py             # stage (ii), ~40 min
.venv\Scripts\python.exe python\runTests.py --all              # ~1 h
.venv\Scripts\python.exe python\paper\build.py                 # seconds
```

Two things the rebuild does not touch: `summarise()` and `tables.argentinaCalibration` name the target
column, so they change *before* the run; and the Argentina prose in `writing/Paper/Sections/Quant.tex`
(the p.p. magnitudes around line 57 and the ε/θ discussion's quoted numbers) must be re-read against the
new tables. Two starting guesses are tuned to the target and may need moving with it —
`informalAnalytical/test_calibration.py`'s β guess is the one that broke last time, walking into a region
where the path solve returns NaN τ and the steady-state `brentq` dies at its own bracket.
