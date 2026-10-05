# Checklist for the final run (opened 2026-10-02)

What changed before it: the selection among tax candidates moved from the integral of the consistent first
order condition to the equilibrium test at each candidate's own frozen savings shares
(`writing/*/num_robustroot.tex`, `roots1d.selectMaxFrozen`, `python/US/RESEARCH_LOG.md` 2026-10-02,
finding #18). Every US solver reports `nCand`, `nEq` and `fallback` per state and a `multiplicity` summary.
The quick checks (`python/US/test_frozenSelection.py`) found exactly one equilibrium at every state and no
fallback at ρ = 1, 2 and 0.5 on the baseline, in the leaded log recursion and in one period of the exact 2-D
CRRA recursion; nothing in `results/` has been re-run.

## Before the run

- [ ] Fast suites green: `python\runTests.py` (log: `logs/fastSuites_frozenSelection_1002.log`); the slow
      `US/test_escTiming.py` and `US/test_escCRRA.py` once, since they pin numbers that can move only where
      the rule binds.
- [ ] Drivers write the counts. Add `nEqMax`, `nCandMax`, `nFallback` (from `out['multiplicity']`) to the rows
      of `calibrateRhoGrid.py`, `calibrateRhoGridEU.py`, `runShocksUS.py`, `runESC.py`, `runESCcrra.py`,
      `runESCxi.py`, and to the prepub scripts `stationaryApprox*.py`. Non-key columns: the merge keys stay
      as they are (finding #13). Without this the run produces no record of whether the rule bound.
- [ ] Decide whether `LOG.solveRobust(check = True)` stays the default in the sweeps. It is what reports the
      counts under log preferences; measured cost 19 ms per solve, 1.0 s per calibration at ρ = 1.
- [ ] C6 (`notes/esc_crraDesignChoiceProblem.md`): at least the step-0 measurement before the ESC CRRA rows are
      re-run, or re-run them knowing the technical note now states the caveat (`num_esc.tex`, the
      predetermined-states paragraph).
- [ ] The informal-sector solvers (`python/informalAnalytical/policy.py`, `python/InformalSavings/policy.py`)
      still call `selectMax`; the note says so. Wire their frozen-objective callbacks (their predetermined
      states: the shares, and under CRRA the level; the ι fixed point stays a root problem) before the
      Argentine numbers are next re-run, with the same quick test pattern.

## Reading the run

- [ ] Any state with `nEq > 1` or `fallback` in any csv: list period, state and the two candidates. A run with
      none is a run in which the rule never bound; say so in `num_esc.tex`'s checks list and in the paper's
      section 4 (the uniqueness sentence, `mkvss08`, then needs only the "given the rule" qualifier).
- [ ] Row-by-row comparison of the new csvs against the committed ones. Expected: bitwise equal where
      `nEq == 1` everywhere and, under log, the gradient solve agreed with the grid selection within one cell
      (`solveRobust` returns the gradient solution untouched then); identical CRRA policy tables where
      `nEq == 1` at every state. Any difference must trace to a flagged state or to C6 work.
- [ ] `num_esc.tex` checks list: add the equilibrium count as a check item with the measured value; items
      10 and 11 (CRRA consistency, candidate grid) are untouched by the selection change.
- [ ] `REPLICATION.md` and `data/README.md`: nothing new unless csv columns are added (then name them).
- [ ] Paper (Overleaf; pull with `--dry-run` first): section 4's state paragraph says the condition is
      derived at fixed shares and the shares substituted; add that candidates are compared at frozen
      shares, and the `%% TODO-CRRA2D` paragraph waits on C6.
- [ ] Logs: name the run logs here; update the `python/US/README.md` status line.

## Plan, 2026-10-02 afternoon (RKB: implement the chosen design layer and re-run what the paper needs)

Order, each step after the one before it; the heavy runs in the background with logs under `logs/finalRun1002/`.

1. Pilot (running): `notes/brief_designChoicePilot_2026-10-02.md`; its report decides the production
   layer (root in a, or the first order condition) on solution, time and robustness.
2. Production brief (model-coder): the chosen layer becomes `LeadedCRRA2D._choose` (the earlier layer
   kept as `designRule = 'legacy'` for comparisons); `multiplicitySummary` carries the design counts;
   `solveLeaded2D`/`solvePolicies` report them; the drivers write `nEqMax`, `nCandMax`, `nFallback` (tax)
   and the design counts as non-key columns (`calibrateRhoGrid.py`, `calibrateRhoGridEU.py`,
   `runShocksUS.py`, `runESC.py`, `runESCcrra.py`, `runESCxi.py`, `stationaryApprox*.py`);
   `config.py` records the rule; `test_escCRRA.py` and `test_esc.py` re-pinned where the layer binds;
   fast suites, then `test_escTiming.py` and `test_escCRRA.py` once.
3. Informal solvers (second model-coder, may run alongside 2): `python/informalAnalytical/policy.py` and
   `python/InformalSavings/policy.py` call `selectMax`/`selectMaxND`; wire frozen-objective callbacks
   (`selectMaxFrozen[ND]`) with the shares (and under CRRA the level) frozen per candidate, the iota fixed
   point untouched; counts reported; the quick-test pattern of `test_frozenSelection.py`. Decided: the
   Argentine arm is re-run too, so that the whole paper is on one selection rule.
4. Decided: `LOG.solveRobust(check = True)` stays the default (it is what reports the counts; 1 s per
   calibration).
5. Note: `num_esc.tex` states which algorithm is production and drops the "at the time of writing"
   sentences; the three `num_robustroot.tex` drop "the informal solvers still call selectMax"; logs; TODO
   C6/C7; push the note.
6. Pipeline, US arm, `--force` throughout (a recalibration moved everything):
   `runCalibrationUS.py` (main, ~20 min) -> `runCalibrationUS.py --prepub` (exact CRRA cost at rho = 0.5
   and 2, UK own cost; hours) -> `runShocksUS.py --all` (shocks, LOG ESC legs, escShocksCRRA ~1.5 h,
   timing checks ~45 min, stationary ~1 h, escShocksCRRAUK ~1 h per rho, merges).
   Argentina arm: `runCalibration.py --force` (~3 h) -> `runShocks.py --all --force` (~1 h).
   Then `build.py`, `build.py --map`.
7. Reading the run (the list above): counts in every csv; row-by-row comparison against `git show
   HEAD:results/...`; the checks list of `num_esc.tex` with the measured values; `REPLICATION.md` /
   `data/README.md` for the new columns; the paper's section 4 sentences (Overleaf `pull --dry-run`
   first); logs named here; `python/US/README.md` status line.
8. Paper, after the build (one Overleaf round trip, `pull --dry-run` first): the prose quotes model
   numbers that the regenerated tables move (section 7.3's λ across ρ and the UK's own cost, 7.4's
   ρ = 0.5 and 2 designs, the conclusion's "within 17%", section 4's footnote and the `%% TODO-CRRA2D`
   paragraph, appendix F.3/G.2). Run `paper-reviewer` (numbers-against-tables audit) on the rebuilt
   draft, then `paper-writer` on the mismatches it lists, then push. The `%% TODO-CRRA2D` paragraph:
   each candidate design, and the tax it is paired with, valued at the inherited distribution of savings,
   closed by consistency; the flat-objective clause stays (41 to 81 candidates: at most 0.006, the pilot's
   root-layer value).

Run log, US arm: `logs/finalRun1002/runUS.cmd` launched 2026-10-02 17:21 (`US_STATUS.txt` the marker;
`US_stage1.log`, `US_stage2.log`).

## Reading the run, Argentine arm (2026-10-03, 01:15; `logs/finalRun1002/ARG_stage{1,2}.log`)

- Both stages complete (`runShocks.py --list`: every experiment present in both variants, the stationary check too).
- Counts: all 70 Argentine csvs carry `nEqMax`/`nCandMax`/`nFallback`; `nEqMax` is 1 wherever a tax was solved
  (−1 on the 32 economic-equilibrium-only files, which solve none), `nFallback` 0 everywhere, no NaN counts.
  **The rule never bound in the Argentine arm.**
- Row by row against the committed csvs (`compareResults.py`, `logs/finalRun1002/compare_0103_0120.txt`): 72
  files changed, every numeric column within 4e-12 of the committed value (cross-process noise, finding #1);
  the only other differences are the `time`/`commit`/`timestamp` metadata, the JSON vectors of
  `calibrationSummary.csv` (parsed, 1e-16) and float formatting of the keys of `epsThetaGrid_rho1.0000.csv`
  (values 3e-13). The paper's Argentine numbers do not move.

## Reading the run, US arm (2026-10-03; `logs/finalRun1002/US_stage{1,2}.log`; the session that watched it was
## stopped by accident at 08:35 and resumed by another at 08:40, the chain itself untouched)

- Stage 1 done 05:00 (nine hours: the four exact CRRA costs at 1.7–2.3 h each). Exact λ, earlier layer → root
  layer: US 18.242 → 18.267 (ρ = 0.5), 1.728 → 1.724 (ρ = 2); UK 15.089 → 15.117, 2.786 → 2.777. Each within
  a third of a percent. Scan brackets unchanged (14.6–25.1 at ρ = 0.5, 0.98–2.22 at ρ = 2).
- Counts: every US csv carries `nEqMax`/`nCandMax`/`nFallback`; the CRRA esc files add `designRule`, `Ma`,
  `nEqθMax`, `nBrθMax`, `nFallbackθ`. Wherever counted: nEq = 1, no fallback; design counts 1/1/0 at every
  row. −1 (not counted) on the US calibration grids, the EE-only files and the pinned ESC rows. **The rule
  never bound in the US arm either.** UK-host CRRA rows: pending the chain's end (re-check with the count scan).
- Row by row against the committed csvs (`compareResults.py`, `compare_0103_0600.txt` for the state at 06:00,
  the final one named below): LOG files within 1e-11 (cross-process noise, #1); the CRRA endogenous-design rows
  move by the design-layer correction: designs ≤ 1.3e-3 (French voting, ρ = 2; ≤ 4e-4 at ρ = 0.5), taxes
  ≤ 7e-5, workweek ≤ 1.2e-3 h, design path ≤ 6e-4, stationary misplacement 0.042/0.059 unchanged at the
  printed precision. Five third decimals of the paper change: acute 0.817 → 0.816 and French income 0.708 →
  0.707 at ρ = 0.5; French income 0.919 → 0.918, French voting 0.334 → 0.335, joint 0.261 → 0.262 at ρ = 2.
  Exact-vs-path gaps (item 10 of the checks): 0.031 at ρ = 0.5 French voting; 0.061 and 0.090 at ρ = 2.
- Written before the chain's end (08:50): `num_esc.tex` checks list items 8–11, 15, 17, 18 and the two status
  sentences; `REPLICATION.md` (the count columns, section 3); `python/US/README.md` status; paper section 4
  (paper-writer, `Sections/Numerical.tex`: the selection sentence and the `%% TODO-CRRA2D` paragraph).
- After the marker: `build.py`, `build.py --map`, the final `compareResults.py` log, the count scan on the UK
  file, `checkPaper.py`; then paper-reviewer (numbers against tables) → paper-writer (the five designs, the four
  λ in `EndogenousTheta.tex`/`UKvsUS.tex`, the UK designs) → Overleaf push; TODO C6/C7 closed; logs.
- Chain DONE 09:50 (13 h 53 min; the UK-host CRRA entry 1 h 29 min). UK CRRA rows: counts 1/1/0 at every chosen
  row, designs moved ≤ 3.0e-4 (ρ = 2, joint row), taxes ≤ 3.1e-5; `UK_ESC_Voting`/`UK_ESC_FrenchAll` unchanged at
  the printed precision, `UK_ESC_IncomeDistr` 0.573 → 0.574 at ρ = 0.5. Final comparison: `compare_0103_final.txt`
  (105 changed csvs, 0 new; `escPermanentCRRA.csv` aligns on no key after its label change and is read by no
  output). `build.py`: 55 built; six tables and the ESC figures changed; `build.py --map` rewritten;
  `checkPaper.py` OK. Count scan over every csv of `results/` (superseded excluded): no `nEq > 1`, no fallback,
  every `nBrθMax` 1; 1245 counted rows, 674 not counted (−1).
