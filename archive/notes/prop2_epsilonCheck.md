# Proposition 2, the effect of ε: the threshold claim and its replacement (2026-10-01)

Working note for the paper's `prop:LOG:PEE` (section 3) and its proof (appendix B.1). RKB asked for a
check of the proposition's claims, in particular that the effect of ε on the tax switches sign at a
threshold share of informal households γ̄₀. Verdict: ω, inequality and θ hold (θ with equal propensities
to vote; the appendix's θ derivative drops a same-sign term from the savings shares' own dependence on
θ); ν holds under one condition now stated in B.1; the γ₀ threshold is not established and not true in
general. The paper now carries the exact condition, `eq:LOG:epsCondition`.

## The argument

The young's terms of the first order condition do not depend on ε, so the sign of dτ/dε is the sign of
the retirees' block's derivative. With σʲ = bʲ/c₂ʲ the pension's share of retiree j's consumption and
φ = 1 + (1−α)τ ∂ln Θ_h/∂τ the marginal revenue factor, retiree support is E⁰ = φσ⁰/τ and
Eⁱ = (σⁱ − (1−φ))/τ, so ε acts only through the shares. A share responds to a proportional change in the
benefit by σ(1−σ); a unit of ε raises b⁰ by 1/(ε(1+γ₀ε)) and lowers every bⁱ by γ₀/(1+γ₀ε) in proportion.
Hence

    ∂z/∂ε = ω γ₀ / (τ(1+γ₀ε)) · [ (φ/ε) σ⁰(1−σ⁰) − Σᵢ γᵢ σⁱ(1−σⁱ) ].

γ₀ multiplies the whole expression: the formal retirees' loss is γ₀ times the informal per-head gain, so
the old limit argument ("γ₀ ≈ 0 makes the formal loss dominate") fails; both sides vanish together.
σ(1−σ) is zero for a retiree with no pension and for one living on the pension alone (log utility: a
higher ε raises their consumption and marginal benefit in the same proportion). 1/ε is the asymmetry of
the transfer. The equivalent form in levels is φ e⁰/(c̃₂⁰)² against Σ γᵢ(1+θ[yᵢ−1]) R s_{t−1,i}/(c₂ⁱ)².

## The numerical check (hand-to-mouth log model, `python/informalAnalytical`, Argentine workbook)

Run only to confirm the derivative against the code's exact FOC; the argument above is the proof. The
analytical model was calibrated with `calibrate('LOG')` (β 0.671, ω 1.486, η₀ 0.288, X₀ 0.376 at ρ = 1;
θ 0.839, ε 0.292, γ₀ 0.32). Holding those fixed:
- γ₀ sweep 0.02 to 5: dτ/dε > 0 at every point (2010 and 2130); ∂z/∂ε by group at the fixed τ path:
  young exactly 0, old informal +, old formal −, both proportional to γ₀ (per unit γ₀ at γ₀ = 0.02:
  +8.3 against −2.3).
- ε sweep 0.05 to 1 at γ₀ = 0.32: positive throughout, falling as the informal pension share rises.
- χ sweep (scale of informal retirees' endowment) at γ₀ = 0.32: positive from χ = 0.1 (pension share 0.90)
  to χ = 2, negative only at χ = 4, where informal retirees are richer than three of four formal types.
- At the calibration the pension shares are 0.17 (informal) and 0.15–0.18 (formal); the condition holds by
  a factor of about 3.5, which is φ/ε ≈ 3.4 with equal shares.
The scripts lived in the session scratchpad and are not kept; the sweep is ~60 lines on
`ModelInformalAnalytical.solvePEE_LOG` with `db['eps']`/`db['κ']` overridden together (κ is read from db).

## Open

- The proposition's inequality and θ claims assume equal propensities to vote (C1, gate 3); the ε condition
  is stated the same way, with μⱼ multiplying each term otherwise.
- Section 3 says the condition holds "as in the calibration to Argentina"; the paper's Argentine model has
  informal savers, so the claim rests on the hand-to-mouth variant of section 5's footnote.
