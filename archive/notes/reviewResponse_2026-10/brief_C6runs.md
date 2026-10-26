# Brief C6 runs: the U.S. results under the converged solvers (A6, after checkpoint 2)

Package C6 (reruns) of `notes/plan_reviewResponse.md` (W16). Agent: paper-compute. Branch `review-2026-10`; the
C6 code is in the working tree, uncommitted (`notes/brief_C6.md`, `python/US/RESEARCH_LOG.md` 2026-10-24):
- CRRA τ-derivatives: a least-squares cubic in ln(1−τ), knots 0.04 apart (`policy.CRRA._gradProfile`);
- `LeadedLOG` solves the anticipated tax at every candidate;
- `LeadedCRRA2D` interpolates Catmull-Rom along θ at 13 nodes.

Every U.S. CRRA number and every endogenous-design number moves. LOG tax paths at given θ do not.

## Rules

- At most **5 solver processes** at once on this machine (4 cores, 8 threads). Set `OMP_NUM_THREADS=1` and
  `MKL_NUM_THREADS=1` in every process. Run detached with logs in `logs/C6runs/`.
- Use `.venv\Scripts\python.exe` (anaconda's python lacks `symMaps`).
- Do not edit model code (`python/US/{policy,policyESC,modelESC,model,base}.py`). If a run fails or a
  calibration does not converge, stop that chain and report; do not change tolerances or brackets beyond what
  the driver's own flags allow, and report any bracket you widen.
- Never hand-edit `writing/Paper`; it changes only through `python/paper/build.py`.

## Runs (the exact commands are in `logs/C6/dry_stage1.txt` and `logs/C6/dry_stage2.txt`)

1. **Stage (i), main and prepub**: `python/paper/runCalibrationUS.py --force` with `--commonX` as the stage's
   registry uses it, then `--prepub --force`. Equivalently, the 21 commands of `dry_stage1.txt`. The two
   sizePiR exact calibrations (~13.5 h each) are the longest chain: start them as soon as the main calibrations
   they read are written.
2. **Stage (ii)**: `runShocksUS.py --force`, then `--prepub --force` (`dry_stage2.txt`), with each step after the
   calibration it reads. Then `python/US/runOECD26.py --force`, run directly, and the three
   `collectESCexperiments.py` merges last.
3. **C5's unwired runs** (`notes/ledger_C5.md`; the commands are in `logs/C5/`):
   - the U.S. ρ grid 0.6–1.9 by `runShocksUS.py --out .../C5_US_shocksRhoGridCommonX.csv`;
   - `python/US/c5Numbers.py selfcheck` first (it must reproduce the new csvs), then `a1 a9 loss lambda index
     design a13`, and `designCRRA --rho 0.5` and `--rho 2` (~2.5 h each).
4. **C4's runs** (`notes/ledger_C4.md`; the commands are in `logs/C4/`):
   - `python/US/runHorizon.py` at the stages C4 ran, including `--stage residuals scheme` (its reference is now
     the production derivative on 801 nodes) and `design` (~5 h);
   - re-derive `results/numerical/US_derivativeScheme.csv` if C4's script wrote it.
5. **Stage (iii)**: `python/paper/build.py`, `--site`, `--map`, then `writing/checkPaper.py`. Run
   `python/paper/compareResults.py` against HEAD to list what moved.
6. **Tests**: refresh `P_CRRA2` in `python/US/test_escCRRA.py` from the new csv (old → new in the ledger), then run
   `python/runTests.py` (fast suites) and `python/US/test_escCRRA.py`.

## Ledger

Write `notes/ledger_C6.md` in the format of `notes/ledger_C1.md`. Give old (f3a15a4) → new for:
- θ* and θ_2020 (log, and CRRA at ρ = 0.5 and 2), and λ for each spec (size, scale, sizePiR) and each ρ;
- the design effect θ 1→0 at ρ = 0.5, 1, 2;
- the headline counterfactuals of figure 6.1 (U.S., UK, UK at U.S. groups);
- the ESC experiments (path, ageing under the three costs, UK host, country);
- the 26-country slopes (`OECD26_*`);
- C5's numbers: A1, A9's ranking and any rank that flips, #22, the design decomposition, X1/X2 under CRRA, A13;
- C4's horizon, residual and scheme tables.

For each number that the paper states (in `writing/Paper` at HEAD), cite the file and line, say whether the
claim still holds, and flag every sign change, rank change or crossing of a threshold the text relies on.
Ledgers C1–C5 note claims that move: recheck those against the new numbers.

## Done when

- every run above has finished, or its failure is reported with the log;
- `build.py` builds every output, `checkPaper` is OK, and the fast suites and `test_escCRRA` pass;
- `notes/ledger_C6.md` is complete;
- the report gives the ledger's headline table, every flagged claim, and the wall time used.
