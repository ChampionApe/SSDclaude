# Audit of the 18.4% savings-rate target (Argentina), 2026-08-24

Follow-up to `notes/argentina_betaCalibration.md`, which listed this as fix 2. The short version: the
datum is a real and defensible fact about Argentina, and the model's denominator is right too — but the
*numerator's time dimension* is not. An **annual flow** saving rate has been imposed on a moment that is
a **30-year stock-to-flow ratio**. Correcting that retargets the calibration on Argentina's measured
capital–output ratio of 3.58 and puts β at 0.97 at ρ=1, without re-denominating anything.

## 1. Provenance

| Where | What it says |
|---|---|
| `writing/Paper/Sections/Quant.tex:38` | "we target the private savings rate defined as savings relative to GDP per capita. We use the average savings rate between 1994 and 2007 of 18.4% from World Bank national accounts data" |
| `data/ArgentinaTest.xlsx` → `calibration` | `Savings rate = 0.184`. No `Readme` sheet (the US/FR/UK workbooks have one), no series id, no vintage, no window |
| `python/InformalSavings/test.py:37` | `pars['s0'] = dfc['Savings rate']` — straight through to `db['s0']`, the level target in `eq:calibration` |
| `writing/informalSavings/num_calibration.tex:16` | the model moment is deliberately **formal-sector only**: informal saving `ι·s` is out of the numerator and informal output out of the denominator |

So the only recorded source is one sentence in the paper. Two things in it do not survive contact with
the data: "private", and "per capita" (the moment is a ratio of two aggregates over the same population,
so per-capita is harmless, but it is also not what was done).

## 2. Can 18.4% be reproduced? — World Bank, Argentina, mean over 1994–2007

| Series | 1994–2007 | 2010 |
|---|---|---|
| Gross domestic savings (% GDP) `NY.GDS.TOTL.ZS` | **20.74** | 20.60 |
| Gross savings (% GDP) `NY.GNS.ICTR.ZS` | **17.04** | 17.33 |
| Gross savings (% GNI) `NY.GNS.ICTR.GN.ZS` | **17.73** | — |
| Gross capital formation (% GDP) `NE.GDI.TOTL.ZS` | 17.94 | 17.71 |
| Gross fixed capital formation (% GDP) `NE.GDI.FTOT.ZS` | 17.27 | — |
| Adjusted savings: net national savings (% GNI) `NY.ADJ.NNAT.GN.ZS` | 6.78 | 6.94 |
| Adjusted savings: consumption of fixed capital (% GNI) `NY.ADJ.DKAP.GN.ZS` | 10.96 | 11.00 |
| Current account balance (% GDP) | −0.12 | −0.38 |

(World Bank API, pulled 2026-08-24; series `lastupdated` 2026-07-13.)

Findings:

- **No current-vintage series equals 18.4%.** The two nearest are gross saving (17.0–17.7%) and gross
  capital formation (17.9%). Argentina's national accounts were rebased in 2014 (1993 → 2004 base) and
  the WDI numbers were revised with them, so an older vintage plausibly gave 18.4 for one of these. The
  number is *in family*; it is not reproducible on the nose, and nothing in the repo pins which series
  it was.
- **It is not a private saving rate.** The World Bank publishes no private-saving series; gross saving
  is national (households + corporations + government). Argentina ran near-zero public saving over the
  window, so private ≈ national to within a point or two — the label is a reporting error, not a
  calibration error, but `writing/Paper/Sections/Quant.tex:38` should stop saying "private".
- **It is gross, not net.** Net national saving over the same window is 6.8% of GNI, with consumption of
  fixed capital taking 11.0 points. Fix 2 as originally written guessed a household-net concept "≈8–12%
  of GDP" and reached ≈0.105 that way. That route does not survive §3: **there is no household/corporate
  distinction to strip.** In this model households own the entire capital stock and there is no
  retained-earnings or government-saving block, so the correct empirical aggregate *is* national saving.

## 3. What the model's moment actually is

Three facts from the docs and the code fix the units:

1. `writing/informalSavings/model_calibration.tex:5`: "let $t$ represent 30-year intervals (this helps
   with the assumption that capital fully depreciates between time steps)". So $Y_t$ is **30 years of
   output**, not one year's.
2. `Base.savingsRate` (`base.py:596`): $sr = s_t / \left[(s_{t-1}/\nu_t)^{\alpha}h_t^{1-\alpha}\right]$
   with $K_t \equiv s_{t-1}/\nu_t$. The numerator is the **end-of-period capital stock** $K_{t+1}$ — the
   young buy capital once, it is used once, and it is gone.
3. Cobb–Douglas gives $R_t = \alpha Y_t/K_t$, hence the identity used throughout below:

$$\frac{K}{Y}\bigg|_{\text{annual}} \;=\; 30\,\frac{K_t}{Y_t} \;=\; \frac{30\,\alpha}{R_t},
\qquad sr \;=\; \frac{K_{t+1}}{Y_t} \;=\; \frac{K_t}{Y_t}\cdot\frac{K_{t+1}}{K_t}.$$

At the calibrated ρ=1 point ($s=0.02121$, $s_-=0.02268$, $h=0.5265$, α=0.43, ν=1.474):

$$R_{t_0} = 3.221 \;(=1.0398/\text{yr}), \qquad \frac{K}{Y}\bigg|_{\text{annual}} = 4.005,
\qquad sr = 0.1335 \times 1.378 = 0.184 .$$

**The error.** Thirty years of gross saving at 18.4%/yr cumulates to 5.5 years of GDP. The model's $s_t$
is not that cumulated flow — it is the stock $K_{t+1}$, which in the data is 3.2–3.6 years of GDP. The
difference is exactly the replacement of capital that depreciates *within* the 30-year window, which the
data's gross flow contains and the model's one-purchase-per-period convention does not. Feeding the flow
rate into the stock moment therefore asks the model to accumulate roughly half again as much capital as
Argentina has, and β is what gives.

Three independent checks that this units reading is the right one rather than a rationalisation:

- **The τ target was converted and the sr target was not.** Pension spending is 7.1% of GDP
  (`Quant.tex:50`) and the model's τ is a labour-income tax, so the target imposed is
  $0.071/(1-\alpha) = 0.1246 \approx 0.125$. Each data ratio was put into the model's own denominator —
  which is exactly why fix 1 (dividing sr by $1-\alpha$ as well) fixes the wrong thing: the sr moment's
  denominator *is* output, and an output-denominated datum belongs there unconverted.
- **Implied depreciation.** The model writes off $K_t$ over the period, i.e. $K_t/Y_t = 13.4\%$ of output
  per period, against measured consumption of fixed capital of 11.0% of GNI. Straight-line, the model's
  $1/30 = 3.33\%$/yr against the data's $0.1096/3.575 = 3.07\%$/yr.
- **The US arm says the same thing out loud.** `USMain_test.xlsx` targets a "30y interest" of 2.443,
  i.e. 2.99%/yr — an unambiguously 30-year object, and by the identity above the same object as $K/Y$.

## 4. What the model-consistent target is

The moment's data counterpart is a capital–output ratio. Penn World Table 11.0 (capital stock and GDP
at constant national prices, `rnna/rgdpna`, via FRED):

| $K/Y$ (annual) | 1994–2007 | 2010 | 2019 |
|---|---|---|---|
| Argentina | 3.575 | 3.231 | 3.896 |
| United States | 3.420 | 3.533 | 3.311 |

Argentina is *not* capital-scarce in these data — over the target's own window it sits slightly above the
US. The problem is the level: the calibration implies **4.005**, 12% above the same-window datum and 24%
above 2010's.

Recalibrating at ρ=1 with nothing moved but the savings-rate target `db['s0']` (produced by what is now
`python/InformalSavings/retargetCalibration.py`, before the target was swapped; the run is the record in
`results/calibration/informalSavings_srGrid.csv`):

| target `s0` | β | ω | $R$ (30y) | $R$ /yr | implied $K/Y$ | |
|---|---|---|---|---|---|---|
| 0.1840 | 1.2120 | 2.641 | 3.221 | 3.98% | 4.01 | ← current |
| 0.1700 | 1.0401 | 2.507 | 3.475 | 4.24% | 3.71 | |
| **0.1636** | **0.9695** | 2.452 | 3.606 | 4.37% | **3.58** | ← PWT $K/Y$, 1994–2007 |
| 0.1600 | 0.9316 | 2.423 | 3.684 | 4.44% | 3.50 | |
| 0.1500 | 0.8332 | 2.347 | 3.921 | 4.66% | 3.29 | |
| **0.1472** | **0.8072** | 2.328 | 3.993 | 4.72% | **3.23** | ← PWT $K/Y$, 2010 |
| 0.1400 | 0.7434 | 2.279 | 4.192 | 4.89% | 3.08 | |
| 0.1300 | 0.6611 | 2.217 | 4.505 | 5.15% | 2.86 | |
| 0.1200 | 0.5856 | 2.160 | 4.869 | 5.42% | 2.65 | |
| 0.1100 | 0.5159 | 2.109 | 5.300 | 5.72% | 2.43 | |
| 0.1050 | 0.4831 | 2.085 | 5.546 | 5.88% | 2.33 | ← what fix 1 implies |

(Every row converges to |residual| ≤ 2e-11, and the 0.184 row reproduces the ρ-sweep's β=1.211968
exactly, so the map is the model's and not a solver artefact.)

Reading it:

- **β crosses 1 at $sr \approx 0.168$, i.e. at $K/Y \approx 3.68$** — which is precisely the US arm's
  implied $K/Y$ ($30\alpha/R = 30\times0.3/2.443$). Any target that puts Argentina at or below the US
  capital–output ratio delivers β<1 at the LOG benchmark. The current target puts it above.
- The defensible range is **0.147–0.164**, on the two PWT anchors. The 1994–2007 anchor is the one
  adopted: it is the window the superseded datum itself used, it is the pre-reform period the
  calibration describes, and a single year is a worse anchor here because the 2001–02 collapse moves
  $K/Y$ by ~0.9 through the denominator alone. For comparison the US arm *delivers* $sr=0.1537$ at ρ=1,
  so this correction happens to harmonise the two arms rather than separate them further.
- **Fix 1 overshoots.** Its 0.105 implies $K/Y=2.33$ and a 5.9%/yr real return, below anything measured
  for Argentina. It produced β<1 for the right reason (the target is too high) by the wrong route.

## 5. The formal-only wedge, quantified

`num_calibration.tex:16` measures the moment on the formal block alone. The national-accounts reading —
$s(1+\gamma_0\iota)$ over $Y+\gamma_0 w^0\eta_0 h_0$ — evaluates at the calibrated ρ=1 point to **0.1944**
against the formal-only **0.1840**. So switching concepts at a fixed datum would *lower* the formal-only
target by about 5% (to ≈0.174): a second-order correction next to §4's. Worth knowing, not worth doing.

It does surface a diagnostic. At the calibrated point informal households save 38% of their income
against the formal block's 18.4% ($\iota s/(w^0\eta_0h_0) = 0.00767/0.02016$). Nothing disciplines that —
ι is a free read-off — and it runs against the usual reading of informal households as the constrained
ones. That is a reason to keep reporting ι, not a reason to re-target on it.

## 6. Recommendation, and what it does to the ranked fixes

Replace the savings-rate target with a **capital-output-ratio target**, `db['KY0']`, evaluated as
$n_{\text{yr}}\alpha/R_{t_0}$ on the solved path. This is fix 3 in substance — it targets the return —
but bought with $K/Y$ from PWT rather than an Argentine 30-year real return, which is the datum fix 3
flagged as genuinely hard to defend. Concretely: `KY0 = 3.5752`.

- **Fix 1** (÷(1−α) → 0.105): rejected. Right direction, wrong mechanism, and it overshoots by §4's
  table. The τ conversion shows the denominators were handled correctly all along.
- **Fix 2** (this audit): the datum is sound and its *sector* coverage was never the problem; the
  household-net reconstruction the note proposed is not this model's concept. The defect is the time
  dimension.
- **Fix 3** (target the return): endorsed, in the $K/Y$ form above.
- **Fix 4** (present β^{1/30}): unnecessary at ρ≥1 once the target moves. Still live at low ρ — see the
  open items.

## Implemented (same day)

The target was moved: `db['KY0']` replaces `db['s0'] = 0.184` as what identifies β, through a new
`Base.capitalOutputRatio` (`eq:calibration:KY`) in both Argentina model variants.
`python/paper/dataTargets.py` derives the datum from PWT and writes it to
`data/argentina_calibrationTargets.csv`; `notes/argentina_capitalOutputTarget_runbook.md` is the runbook for
the results and paper outputs that still have to follow.

**The reading adopted is the calibration year, 2010: K/Y = 3.2313.** The alternative is a mean over the
thirty years ending there — one model period of data — and the two are 13% apart:

| reading | K/Y | β at ρ=1 | ω | delivered sr | R (annualised) |
|---|---|---|---|---|---|
| **2010 (adopted)** | **3.2313** | **0.8076** | 2.3278 | 0.1472 | 3.99 (4.72%/yr) |
| 1980–2010 mean | 3.6606 | 1.0126 | 2.4858 | 0.1676 | 3.52 (4.29%/yr) |
| 1994–2007 mean | 3.5752 | 0.9684 | 2.4515 | 0.1635 | 3.61 (4.37%/yr) |

The calibration year wins on the same grounds the rest of `eq:calibration` is built on: the tax rate, the
replacement-rate ratio, the coverage share and the household survey are all measured at or around 2010,
and Argentina's K/Y moves enough over the preceding decades (4.28 in 1990, 3.17 in 2007 — the denominator
doing most of the work) that a thirty-year average would describe a different economy from the one the
other targets describe. It also puts β comfortably below 1 rather than 1.3% above it: β crosses 1 at
K/Y ≈ 3.64, which the window mean straddles and the 2010 reading clears. The full map is
`results/calibration/informalSavings_KYGrid.csv`.

## Open items

- **The ρ<1 end is not fixed by this.** The re-target above was run at ρ=1 only. β rises steeply as ρ
  falls (4.28 at ρ=0.5 on the current target), and a proportional response would still leave β>1 there.
  A CRRA re-target at ρ=0.5 was started and stopped before finishing; until the sweep is re-run on the
  new target, treat the low-ρ half of it as unresolved.
- If the target moves, `results/calibration/informalSavings_rhoGrid.csv` and everything downstream
  (`shockUniversal.py`, `shockEEOnly.py`, `sweepEpsThetaGrid.py`, `python/paper/`) is stale. That is a
  decision to take deliberately, not a side effect of this note.
- `writing/Paper/Sections/Quant.tex:38` needs rewriting whatever is decided: the current sentence
  mislabels the concept ("private"), the denominator ("per capita"), and names no series.
