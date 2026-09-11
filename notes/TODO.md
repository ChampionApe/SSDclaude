# TODO (restructured 2026-09-11)

The one open list. Closed work is not here: it is in the session logs (`RESEARCH_LOG.md`,
`python/<module>/RESEARCH_LOG.md`, `python/paper/RESEARCH_LOG.md`) and, for the 2026-09-08 rewrite plan and
the permanent-timing fix, in `archive/notes/todo_paperRewrite.md` and `archive/notes/todo_escPermanentTiming.md`.
`notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing.

## Code tasks

**C1. Split the paper pipeline into a main part and a pre-publication part.** The main part is what a
routine rebuild runs (stages (i)/(ii) as today: calibrations, the exogenous-θ shocks in both variants, the
ESC leg under LOG). The pre-publication part holds heavy runs whose results move only when the model does,
run once before submission. Decided 2026-09-11: **the exact 2-D solver is the published method for the
CRRA ESC leg**, and the timing checks under LOG are **tests**, not pipeline stages. The pre-publication
part contains:
- the exact 2-D CRRA ESC solves (C2), from which stage (iii) builds every CRRA ESC output (the ρ ≠ 1 rows
  of `US_ESC_Calibration`, the four ESC counterfactual tables, `US_ESC_overview`). The path iteration may
  stay in the main part as a fast stand-in for development rebuilds, but no paper output reads it: a
  `method` column in the ESC csvs, and `config.US['esc']['exact']` = True for the published build;
- the sequential- and permanent-timing checks under CRRA (R3). Their LOG counterparts go into
  `test_esc.py`. *Sequential*: the sign of the costless `eq:esc:seqFOC` over θ ∈ [0,1] at the solved
  2020 baseline, with the actual voting weights μ_i. The paper's corner claim rests on "the numerator
  averages to zero", which ignores μ_i (US: 0.47, 0.63, 0.77, rising with income), so it is not
  established as written. No solver is needed: it is a scalar evaluation on a solved path. *Permanent*:
  `PermanentLOG` in the test, `PermanentCRRA` here (corner and fixed-point checks, reference numbers in R3);
- *(candidate)* the φ-robustness wedge calibrations at φ = 0.25 and 0.75 behind the φ footnote in
  `sec:esc`. Its 0.26 and 0.96 come from `results/esc/superseded/escCalibration.csv` and have never been
  rerun under common X; the pipeline runs φ = 0.5 only.

Also wire into the **main** part two inputs the paper uses that no stage produces today: `escCountry.csv`
(`runESC.py --stage country`, feeds `Tables/UK_ESC_Calibration.tex`) and `escPath.csv` (`--stage path`,
the 0.738 → 0.748 → 0.773 drift in `sec:esc`). Both are cheap LOG runs. Design to settle: the flag that
selects the pre-publication part on `python/paper/runShocksUS.py` (and `runCalibrationUS.py`, which runs
the wedge calibrations).

**C2. Exact solver for the US CRRA ESC leg** (the published method). The CRRA tables (ρ = 0.5, 2) come
from the path iteration today, certified against the exact 2-D recursion (`LeadedCRRA2D`) to ±0.01 in
the design. Add an `--exact`
branch to `python/US/runESCcrra.py` that runs the wedge calibration and the chosen-design readings through
`solveLeaded2D`. The driver has no 2-D branch today (it never references `ESCC2`). Narrow the p scan to
half..double the known p (0.965 / 0.090): about 8 solves per ρ for the calibration and one per chosen
reading. ~12 min per 2-D solve at ns = 150, ~3× faster at ns = 50 (the s-grid is immaterial, the 13-node
θ-state grid is not). About half a day of code; it lives in the pre-publication part (C1).

**C3. Argentina under common X.** The OECD arm leads with the common-X calibration; the Argentina arm is
vector-X only. Touches `python/InformalSavings` (calibration loader, `calibrateRhoGrid.py`),
`python/paper/runCalibration.py` / `config.ARG`, and the Argentina builders, which gain the same `commonX`
switch as the US ones (`config.variantSuffix`). Not started. **Caveat:** `calibrationη0/X0` hold only while
`h_t` is average formal hours, i.e. under `∑γ_i(η_i/X_i)^ξ = 1` (`eq:calibration:yNorm`). A common X pinned
by the workweek spends that normalisation, so the two formulas then need the factor
`Γ_h/∑γ_i(η_i/X_i)^ξ` (in `η0`, and inside the `1/ξ` power in `X0`). `test_calibration.py`'s solved-path
checks catch a miss.

**C4. US vector-X: one hours unit across countries** (for RKB; not started). Under vector X each country's
hours unit `μ = ∑γ_i y^x_i` is whatever scipy's unit-norm eigenvector gives (US 0.5593, FR 0.5590, UK
0.5770). `ModelFR` pins `h̄` by rescaling `Γ_h`, not `μ`, so `X̄_c/X̄_US` carries `μ_US/μ_c`: FR 1.0005, UK
0.969. Moot for the French leisure row, which is no longer printed. The UK `X̄` in
`USUKFRCalibration_vectorX` carries the ~3%. Fix: impose `∑γ_i y^x_i = 1` in `US.addEigenVectors`, as the
Argentina models now do. It is equilibrium-neutral, but the vector-X `X_i` and `X̄` entries move.

## Compute tasks

Order (agreed 2026-09-11): code first, then compute, then writing. R1, R3 and R4 run together as **one US
run** (main part and pre-publication part) once C1 and C2 are in; R2 follows C3. Every run waits for the
other session's Argentina job (`logs/argPipeline0911.log` ends in `DONE`): one heavy job at a time.

**R1. Re-run the US shocks and ESC stages, then rebuild.** Two code changes on 2026-09-11 make the printed US
counterfactual numbers stale: (a) the French income-distribution shock now puts France's η *profile* at
the US productivity *level* (`shocks.ηLevel`); under common X this lowers the income row's workweek by
~4% (41.97 → 40.36 hours at ρ = 1) and leaves τ, s/Y and R unchanged, while the combined rows and France's
own row do not move; (b) the French leisure shock is no longer printed but still runs. Run the main part
of `python\paper\runShocksUS.py --force` (`--list` shows what exists, `--dry` the commands), then
`build.py --no-copy`; the copy into `writing/Paper` happens with the writing tasks. The CRRA
path-iteration leg need not run: the CRRA ESC rows come from R4. The endogenous θ in the
frIncome/frBoth/frAll rows can move slightly. Then W2.

**R2. Argentina under common X** (needs C3). Full ρ-grid recalibration (~3 h) plus the shocks (~1 h):
`python\paper\runCalibration.py --force`, `runShocks.py --force`, `build.py --no-copy`. Keep the vector-X results
produced today alongside (the builders' `commonX` switch, C3): which version the paper prints is decided
once both exist (W2). Then W2.

**R3. Permanent- and sequential-timing checks** (needs the C1 check code).
- `PermanentCRRA` has never been executed (restructured: candidate solves cached in `_grid`, new `W`
  signature, `solveFixedPoint`; no test covers it). Smoke at one ρ (~4 min):
  `python\US\runESCcrra.py --stage permanent --rho 2.0 --spec scale --phi 0.5`, expect
  `θ_perm = 1.0000, corner=True` (a corner cannot tell the two pinnings apart, so this shows the code
  runs, not that the timing change works under CRRA). Then the trace (~25–30 min): `--rho 1.1 1.2 1.3 1.4
  1.5 2.0`.
- Regenerate `results/esc/escPermanent{,CRRA}.csv` (deleted as pre-timing-change vintage; at `c958031^`
  if needed): `python\US\runESC.py --stage permanent --spec scale flat --phi 0.25 0.5 0.75` (~10–15 min).
  Checks: `p` for (`scale`, φ = 0.5) must come back `0.37503226627596936`, and on every calibrated row
  `θPerm ≈ θPermIncumbent ≈ θStar`. Reference (fixed point / incumbent pinning / moving):
  p = 0.4: 0.775076 / 0.773380 / 0.9096; p = 0.375: 0.738226 / 0.738226 / 0.8694;
  p = 0.25: 0.541576 / 0.549211 / 0.652294. These LOG reference numbers are also what the `test_esc.py`
  permanent-timing test asserts (C1); nothing in `python/paper/` reads the csvs.
- Sequential: the C1 check at ρ = 0.5 and 2 (ρ = 1 is the LOG test). If the costless FOC is not negative on all of [0,1],
  "three timings, one corner" fails and the introduction, conclusion and `sec:esc` change. Then W2.

**R4. Exact solver run for the US ESC** (needs C2). 1.5–5 h. Then W2.

## Writing

**W1. Introduction**: `XXX FILL IN HERE XXX` at line 38 (the OECD-sample sentence).

**W2. Text that follows the runs** (each after its run):
- after R1: re-read the hand-written numbers in `Sections/OECD.tex` (income-distribution hours) and
  `Sections/EndogenousTheta.tex` (income-distribution and both-at-once paragraphs) against the tables;
- after R2: decide with RKB which Argentina version (vector X or common X) the paper prints, or whether
  it prints both as the OECD arm does; then the Argentina section's numbers, and the abstract,
  introduction and conclusion if a magnitude or sign moves (style guide §6). The draft already carries
  the vector-X numbers after the 2026-09-11 informal-target fix ("almost half" of the 1.8% of GDP);
  those are the baseline to compare against;
- after R3: add μ_i to the paper's `eq:esc:seqFOC` (missing against `Model.tex:128` and
  `writing/US/model_esc.tex`; this part can be done now) and replace the "averages to zero" argument with
  the measured result, in the paper and in `model_esc.tex`; back the permanent-timing sentence under CRRA;
- after R4: the CRRA numbers quoted in `sec:esc` prose against the exact-solver tables; the φ footnote
  gets current-vintage numbers once the φ runs exist (if kept in C1).

**W3. No mention of the path iteration in the paper** (after R4). The exact solver is the published
method, so the paper describes only it. Today the one place is the solution paragraph of `sec:esc`
(`Sections/EndogenousTheta.tex`, the paragraph after `\input{Tables/US_ESC_Calibration}`): the "cheaper
method that iterates on the equilibrium path", the ±0.01 / 2e-4 agreement, "the tables below use the path
iteration". Rewrite it to state that the CRRA equilibrium is solved by the exact recursion on
$(s_{t-1},\theta_t)$. Re-grep `writing/Paper` (and the table and figure notes in `python/paper/tablesUS.py`
/ `figuresUS.py`, which are generated) for "iterat", "path", "cheaper" before closing. The technical
documentation (`writing/US/num_esc.tex`) keeps the path iteration as a documented method and check.

**W4. Voting-patterns mechanism in `sec:esc`** (for RKB): "the redistributive force regains ground against
the forward-looking stake, and it is the latter that scales with ρ" reads as if higher ρ should protect
the Bismarckian design, yet the design falls most at ρ = 2 (0.285). The likely reason is the small
calibrated wedge at high ρ; decide the wording.

## Traps to remember (kept here because `README.md` points at them)

- **openpyxl drops cached formula values on save.** The Argentina workbook has formulas; after an
  openpyxl round trip pandas reads them as NaN and every steady state fails. Edit workbooks through Excel
  (COM from PowerShell works) or write literal values.
- **`PYTHONUTF8=1` for every pipeline run.** The scripts print Greek letters; under the cp1252 console
  they crash on the first print.
- **PowerShell `*>` redirection writes UTF-16.** Route python output through `cmd /c "... > log 2>&1"`.
