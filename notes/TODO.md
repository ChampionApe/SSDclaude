# TODO (restructured 2026-09-11)

The one open list. Closed work is not here: it is in the session logs (`RESEARCH_LOG.md`,
`python/<module>/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`) and, for the 2026-09-08 rewrite plan and
the permanent-timing fix, in `archive/notes/todo_paperRewrite.md` and `archive/notes/todo_escPermanentTiming.md`.
`notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing. C1, C2, R1, R3, R4
and W3 closed on 2026-09-11 (`python/US/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`); C4 and W2 on
2026-09-12. Open: W1, W2b, W4, all three RKB's wording calls.

## Code tasks

**C3. Argentina under common X** — done 2026-09-11 (`python/InformalSavings/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`); R2 runs it.

**C4. US vector-X: one hours unit across countries** — done 2026-09-12. `US.addEigenVectors` now scales
both eigenvectors to γ·y = 1, so the hours unit μ = ∑γ_i y^x_i is 1 in every country rather than whatever
scipy's unit-norm eigenvector gave (US 0.5593, FR 0.5590, UK 0.5770), and `X̄_c/X̄_US` no longer carries
μ_US/μ_c. Equilibrium-neutral (it is the eq (hoursUnit) rescaling, which moves only h̄ and h_i); the
vector-X η_i, X_i and X̄ entries move. Docs, `test_ee.py`'s h̄-vs-h check and the vector-X sweeps followed
(`python/US/RESEARCH_LOG.md`, `logs/usVectorX0912.log`).

## Compute tasks

**R2. Argentina under common X** — done 2026-09-11 evening (`logs/argCommonX*0911.log`, 1.8 h; all stages
exit 0, 39 outputs built, 22 fast suites pass). Every common-X shock csv and the ε×θ grid equal the vector-X
ones to ≤ 4e-12 at every ρ, and the sweeps agree in β, ω, K/Y, τ, ι to 4e-12: the two versions print the same
counterfactual tables and figures and differ only in `ArgentinaCalibration{,_commonX}` (η_i, X vs X_i, η_0,
X_0, the relative-hours prediction). Copied into `writing/Paper` on 2026-09-12 as the headline (W2).

## Writing

**W1. Introduction**: the OECD-sample sentence at `Sections/Introduction.tex` line 38 is drafted under a
`%% TODO-W1` tag (2026-09-11); RKB to confirm or rewrite, then drop the tag.

**W2. Text that follows R2** — decided 2026-09-12: the paper prints **common X** in both arms
(`config.ARG['commonX'] = True`). The Argentina identification paragraph was rewritten (one X pinned by the
42.5-hour formal workweek, relative formal hours a prediction), the vector-X calibration table moved to a
new appendix subsection `app:EPH:vectorX`, and the ten Argentina outputs were rebuilt. No counterfactual
number moved, so the draft's magnitudes stand. The OECD section now cites section 5's identification
paragraph instead of repeating it, and keeps only the part specific to its own arm.

**W2b. The permanent corner under CRRA** (for RKB). `results/esc/escPermanentCRRA.csv` (2026-09-11): with no
wedge the permanent choice is the corner θ = 0 for ρ ≤ 1.3 and θ = 1 for ρ ≥ 1.4 (W gaps of 0.002–0.02).
`Sections/EndogenousTheta.tex` now says so in the permanent paragraph and qualifies the section opening,
under a `%% TODO-W2` tag; confirm the wording and check the introduction/conclusion do not promise
"the Beveridgean corner" for every timing.

**W4. Voting-patterns mechanism in `sec:esc`** (for RKB): "the redistributive force regains ground against
the forward-looking stake, and it is the latter that scales with ρ" reads as if higher ρ should protect
the Bismarckian design, yet the design falls most at ρ = 2 (0.259 under the exact solver). The likely
reason is the small calibrated wedge at high ρ; decide the wording.

## Traps to remember (kept here because `README.md` points at them)

- **openpyxl drops cached formula values on save.** The Argentina workbook has formulas; after an
  openpyxl round trip pandas reads them as NaN and every steady state fails. Edit workbooks through Excel
  (COM from PowerShell works) or write literal values.
- **`PYTHONUTF8=1` for every pipeline run.** The scripts print Greek letters; under the cp1252 console
  they crash on the first print.
- **PowerShell `*>` redirection writes UTF-16.** Route python output through `cmd /c "... > log 2>&1"`.
- **A `tail -F` on a log a PowerShell script appends to makes every later `Add-Content` fail silently.**
  Poll with `grep -q` in an `until` loop instead (`notes/crossCuttingFindings.md` #14).
