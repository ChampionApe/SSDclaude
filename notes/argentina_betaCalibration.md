# Argentina: why the calibrated β exceeds 1, and what could fix it (2026-08-24)

## The fact

`results/calibration/informalSavings_rhoGrid.csv`: β falls monotonically 4.28 → 0.65 over ρ ∈ [0.5, 2]
and crosses 1 near ρ ≈ 1.15. So β > 1 throughout the lower half of the range — including β = 1.212 at
the LOG benchmark ρ = 1 — and the empirically favored EIS values are exactly where it is worst. The US
arm at the same ρ = 1 gives β = 0.7606.

(One caveat on units before calling any of this pathological: β here is a **30-year** discount factor.
β = 1.212 annualizes to 1.0064/yr, and the old-age utility weight in the model is β·p with survival
p < 1, so the *effective* patience βp is below 1 even at the worst point of the sweep. β > 1 is
inadmissible in an infinite-horizon model, not in an OLG one. It is still worth fixing, because a
reader will not annualize before reacting.)

## Why it happens: the target's denominator

The two arms differ in what pins β. The US targets `R_{t0}` (30y interest) and merely *reports* the
savings rate; Argentina has no interest-rate datum and targets the savings rate directly:

$$sr \equiv \frac{s_t}{Y_t} = \frac{s_t}{(s_{t-1}/\nu_t)^{\alpha} h_t^{1-\alpha}} = 0.184$$

(`Base.savingsRate`, workbook `ArgentinaTest.xlsx` → Savings rate 0.184). Only the young save in this
model, out of labor income, and Argentina's capital share is high (α = 0.43, against the US's 0.30). So
hitting 18.4% of *output* requires the young to save

$$\frac{s}{w h} = \frac{s/Y}{1-\alpha} = \frac{0.184}{0.57} = 32.3\%$$

of gross labor income — half again the US arm's delivered 22.0%. In a two-period consumption-smoothing
problem the young's saving share is increasing in β with slope that flattens as β grows (log intuition:
share ≈ β/(1+β) times a policy factor), so pushing the share from ~22% to ~32% takes β from ~0.76 to
well above 1. The high ω (2.64 vs the US's 1.45) is the same target propagating through the political
block: a patient electorate needs a heavier old-age political weight to still deliver τ = 12.5%.

The past calibration the user recalls — targeting **savings / labor income** = 0.184 — imposes
s/Y = 0.184 × 0.57 = **0.105**, i.e. roughly half the saving the current target demands, which is why
it produced β well below 1. So the question is not numerical; it is *which concept the 18.4% datum
measures*. Note the paper's own reporting convention already sides with the labor-income denominator:
`shocks.srPaper` divides by (1−α) to report s/(wh) for the US tables.

## Possible fixes, ranked

1. **Re-target as savings / labor income** (s/(wh) = 0.184 ⇒ s/Y ≈ 0.105). One-line change in the
   calibration residual (divide the model moment by 1−α, or scale the target), best behind a flag so
   both variants stay runnable. Pros: restores β < 1 across the whole ρ range (the past calibration is
   the evidence); consistent with the s/(wh) convention the paper's tables already use; defensible if
   the datum is a household-saving-out-of-income concept. Cons: if the datum is national-accounts
   saving/GDP, this is a *re-interpretation*, not a fix.

2. **Audit the 18.4% datum itself.** The model's `s` is the *net new retirement saving of the young
   cohort*. A national-accounts gross saving rate (~15–18% of GDP for Argentina) includes corporate
   and government saving and consumption of fixed capital — none of which is the model's s. Stripping
   those gets the household-net concept, plausibly ~8–12% of GDP, which lands in the same place as
   fix 1 by a route that defends the number rather than the denominator. This is the intellectually
   cleanest fix but needs a data pass.

3. **Switch the target to an interest rate, as the US arm does** (target R_{t0}, report sr). Pros:
   harmonizes the two arms — one calibration logic everywhere — and R is the moment that actually
   disciplines β in this class of models. Cons: needs an Argentine 30-year real return datum, which is
   genuinely hard (sovereign risk, inflation history); whatever number is chosen will be contestable
   in a way the savings rate is not.

4. **Present rather than repair**: keep the target, report β^(1/30) (1.0064/yr at ρ=1) and the
   effective old-age weight β·p < 1, and argue admissibility in an OLG setting. Zero code, but leaves
   β > 4 at ρ = 0.5 on the table, which no annualization argument rescues (4.28^(1/30) = 1.050/yr —
   a 5%/yr *negative* rate of time preference is hard to defend).

5. **Composite target**: target the savings rate *inclusive of the capital-income channel* — e.g.
   define the moment as s/(disposable income of the young) or bring survival p into the calibration
   jointly. More structure, more moving parts; only worth it if 1–3 are rejected.

Recommendation: 1 now (cheap, reversible, evidence it works), with 2 as the follow-up that decides
whether 1 was a re-interpretation or a correction. If the FR/UK-style harmonization ever matters more
than the Argentine data constraint, 3 replaces both.

Not run: no recalibration was executed for this note (per session scope); the quantitative claims are
the sweep csv, the workbook, and arithmetic.

---

## Follow-up (same day): the audit was run — see `notes/argentina_savingsTargetAudit.md`

Fix 2 was carried out and it overturns part of what is above. In brief:

* The datum is a **World Bank gross national-accounts saving rate** — not private, not household, not
  net. No current-vintage series reproduces 18.4% exactly (nearest: gross saving 17.0–17.7% of
  GDP/GNI, gross capital formation 17.9%), and Argentina's 2014 rebasing means the original vintage
  cannot be recovered from the repo, which records no series id.
* The sector reasoning in fix 2 above ("strip corporate and government saving") does **not** apply: in
  this model households own the whole capital stock, so national saving is the right aggregate.
* The actual defect is the **time dimension**, not the denominator. With 30-year periods and full
  depreciation, the model's moment is `s_t/Y_t = K_{t+1}/Y_t`, a stock over 30 years of output —
  equivalently `(K/Y)_annual/30` times the period's capital growth. An annual flow saving rate is a
  different object, and larger, because it replaces capital that depreciates inside the window.
* This also retires **fix 1**: the τ target *was* converted into the model's denominator
  (7.1% of GDP / (1−α) = 0.125), so the denominators were handled correctly throughout; dividing sr by
  (1−α) as well would be an error, and its 0.105 implies K/Y = 2.33, below anything measured.
* Anchoring on Argentina's measured capital–output ratio (PWT 11.0: 3.58 over 1994–2007, 3.23 in 2010,
  against the calibration's implied 4.01) gives a target of **0.147–0.164** and **β = 0.81–0.97** at
  ρ=1. β crosses 1 at K/Y ≈ 3.68, which is exactly the US arm's implied ratio.

Revised recommendation: **fix 3, in capital–output form** — set the target so the implied `30α/R` matches
PWT, i.e. `s0 ≈ 0.15`. No new interest-rate datum is needed and the two arms end up on one logic.
