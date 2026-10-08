# R1, the referee pass on section 7, appendix C and appendix G (2026-10-08)

Read-only report of the `paper-reviewer-lead` agent, kept for the fix pass (phase R) and the appendix C
cut-back (phase W5). Line numbers are those of the files at the time of the pass. S7 =
`Sections/EndogenousTheta.tex`, C = `Appendix/EndogenousDesign.tex`, G = `Appendix/EndogenousDesignDetails.tex`.

**Checked and clean.** `eq:esc:cornerFOC` redone term by term from `eq:LOG:PolObj`, the Euler equation,
`eq:esc:auxiliary`, the young's bracket and `eq:factorPrices` (the hours term, the $-b\psi/y_i$ term, the two
return terms, $c_H$, the affine coefficient in $\ell$, the order-$\tau$ claim); the tax-response bracket from
`eq:esc:E2`; `eq:esc:ftheta`; the three properties; $M$ from `eq:esc:implicitTax` and $\tilde V$ from the
Harberger sum; the literal-leak factor; $2\lambda_1\tau$ per unit carried. Every number quoted in S7 and G
matches its table or csv at the printed precision. Style: no `---`, cross-references lowercase, footnotes
full sentences, RKB's order in 7.1, the $\rho$ paragraph says the other variants are at $\rho = 1$.

## Findings, ranked

1. **S7:18.** "an electorate chooses the corner once $\lambda_1$ exceeds a threshold that falls with the size of
   the system and rises with a flatter voting profile and a more compressed income distribution
   (proposition bismarckCorner)". The proposition delivers a *local* maximum at $\theta_{t+1} = 1$ at a given
   $\mathcal{T}'$ and $\underline\lambda_1 \propto 1/\tau$ to first order; the voting-profile and compression
   statements are the words paragraph (C:112, "at the calibrated economies"), and "chooses" needs
   $\mathcal{B}_t$ single-peaked, verified numerically in the note (§3.2) and stated nowhere in the paper.
   Fix: cite the proposition (after W5: the technical documentation) for the size channel only and
   appendix `app:esc:cost` for the other two; add one sentence that $\mathcal{B}_t$ is single-peaked at the
   three economies so the local condition decides the choice.
2. **S7:27.** "No pair of parameters that keeps the U.S. on its design reconciles the UK and France." The
   tables give two pinnings; "no pair" needs the UK's choice to fall and France's to rise monotonically in
   $\kappa$ along the U.S.-calibrated curve, which is `notes/esc_variants.md` §4.2 (A.22) and not in the paper.
   Fix: one sentence in G.1 with the monotonicity (the marginal-cost ratio
   $[\kappa + (1-\theta)]/[\kappa + (1-\theta^{\ast})]$ falls in $\kappa$ for $\theta < \theta^{\ast}$ and rises for
   $\theta > \theta^{\ast}$), or soften to "neither pinning reconciles".
3. **C:101 and C:110.** "positive if and only if $\lambda_1 > \underline\lambda_1$ ... the value of $\ell$ at
   which cornerFOC vanishes"; "The thresholds of section 7.2 solve cornerFOC with this response." With
   $\mathcal{T}'(\ell)$ substituted the slope stays affine in $\ell$ but the sign of its coefficient is not
   established (note A.20), so uniqueness of the fixed-point root is unproven; the printed thresholds
   (1.312, $\geq 9.793$) are the smallest parameter at which the *choice* is the corner
   (`calibrateWedgeCorner`), which equals the root only under single-peakedness. Fix: say the thresholds are
   computed from the choice and coincide with the root at the three economies; drop "solve".
4. **S7:56.** "The scaling by the size of the system, common to the three, is what carries the ageing
   response through the tax (`\oa{esc-scale}`)". The comparison exists for the quadratic cost only (S7:48
   says so). Fix: "shown for the quadratic cost", or drop the sentence.
5. **G:20.** "a political weight of the old close to the U.S. one (table US:Calib)". The table's $\omega$
   (1.45, 1.42) are the exogenous-$\theta$ calibration; under the linear-quadratic cost the U.S. $\omega$ is
   recalibrated to 1.53 (`escCalibration.csv`) while France's stays 1.42. Fix: cite the recalibrated value or
   drop the parenthetical.
6. **Style §4, synonyms for one object:** "the linear-quadratic cost" (tables, G, S7:16, 23, 41, 58), "the
   preferred cost" (ten uses, S7:23-54), "our preferred specification"/"the preferred one" (S7:16, 23;
   Introduction:27; Conclusion:7). Fix: the tables' name in prose, "our preferred specification" once at S7:16.
7. **Placement.** S7:18 and C:84 state the same three properties nearly verbatim; S7:27's own-value sentences
   (within 16%/41%; the France pin $\kappa = 0.629 \to 0.397$, repeated at G:6) are G.1 material per outline
   B. Fix: properties in full at S7:18 and only the display in C; in S7:27 keep the two sentences carrying
   "the UK pins a small linear term, France's corner takes about twice as large".
8. **C:112.** "The common part ... is the larger obstacle at the calibrated economies" is a numerical claim
   ($-0.110$ against $-0.043$ on the U.S., note §3.4) with no number in the paper. Fix: give the two numbers
   or drop "at the calibrated economies".
9. **Minor.** G:6 "France, at 1.94": the csv ratio is 1.93 (1.94 is the quotient of rounded cells). Table
   `US_ESC_VariantsShocks`: the "pinned" savings cells on non-baseline rows are changes against the *chosen*
   baseline under a printed pinned level of 15.54 (fixed in the builder's note on 2026-10-08: "in both
   columns"); G:18's gaps (0.3, 0.7) follow that convention.

## Three places a referee pushes hardest

(a) **Circularity of the size channel.** The $\tau$-scaling of the linear term is chosen (S7:16 footnote, C:84
footnote) so that a larger system lowers the corner threshold; S7:27 then reports "what separates the UK from
France is the size of the system" as a result, while C:84's footnote concedes that under the literal leak the
ordering would rest on demography and voting alone. Expect a demand for the literal leak's cross-country row,
or for the sentence to own the specification.
(b) **What the test tests.** The linear term exists to make France's corner reachable; the preferred
specification predicts France at 0.806 where the quadratic already ordered the designs (0.749); with $\omega$
refit per country and the UK's design spent on $\kappa$, the out-of-sample content is one ordering. Expect
"what does the second parameter buy" and "one inequality is not a test".
(c) **Magnitude and identification.** $\lambda_2$ an order of magnitude above elasticity-based values, $\lambda_1$
with no benchmark, and the one counterfactual that separates LQ from Q (France's income distribution, 0.850
against 0.772) runs through weighting the linear term by $M$ rather than $\tilde V$, a choice with no empirical
counterpart (G:6: $\tilde V$-weighted gives France 0.749). Expect a request for an external moment on the
linear term.

## Cut list for appendix C (phase W5)

Keep in C.2: :54-62 (the implicit tax; S7 cites `eq:esc:implicitTax`); :64's first five sentences (the marginal
wedge in `eq:h`, why not the hours margin, the margins and Saez/Kleven-Kreiner), cutting the Disney and
Kumler sentences, now in S7; :66-70 (Harberger, $\tilde V$), the symmetry sentence optional; :72-84:
`eq:esc:AB`, the amount carried and `eq:esc:Mabs`, `eq:esc:fGeneral` (cited by the table notes), the
first-order share and the $\Pi_t$ footnote, "Each term carries the dispersion...", "The one choice..." with its
footnote, the scale/shape and exponential sentences; compress "Three properties..." to one sentence plus the
:86 display; keep :88's last three sentences (both components alike; the flat-component alternative C.3 uses;
the design-itself cost S7 uses). Keep :114 "Magnitude" in full. Keep C.3 :117-145; :145's proposition reference
becomes the corner paragraph.

Move to `writing/US/model_esc.tex`: :90-104 (lead-in, proposition 4, proof), :106-110 (the tax response),
:148-156 (proposition 5, proof). Replace :90-112 by one paragraph in words carrying exactly what S7 cites: the
cost enters the corner condition only through $\ell = \lambda_1\tau_{t+1}M$, so $\lambda_2$ does not enter; the
slope rises in $\ell$, so the corner is a local maximum above $\underline\lambda_1 = \bar\ell/(\tau_{t+1}M)$;
$\bar\ell$ is of order one as $\tau \to 0$, so $\underline\lambda_1 \propto 1/\tau_{t+1}$; a flatter profile
raises $\bar\ell$ ($S_\mu \to \bar\mu(1+\tilde V)$); compression raises $\underline\lambda_1$ through $M$, by less
than $\tilde V$'s fall; ageing lowers it; the tax response turns positive below the threshold; the printed
thresholds are the smallest parameter at which the choice is the corner, equal to the root where
$\mathcal{B}_t$ is single-peaked, as at the three economies. Replace C.4 by :158 trimmed (the statement in
words, what section 4 uses, the CRRA caveat).

Retarget: S7:18 (both propositions), S7:27, `Numerical.tex:11`, C:84's footnote, C:145. Absence a referee would
not notice: :106-110, :70's last sentence, :64's two literature sentences, :112's decomposition clause.
