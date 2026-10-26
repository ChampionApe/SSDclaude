# Brief C7: France's ν at the PaG 2021 retirement-age gap (W16, RKB 2026-10-26)

**Change (done by RKB in Excel, do not touch the workbook).** `data/FRMain.xlsx` `population!D3:D6` apply
appendix F's rule ν(30−g)/(30+νg) with g = 1.5 (1990, 2020) and 1 (2050, 2080) instead of 2.5, 2.5, 2, 2:
France's men's normal retirement age is 64.5 against the U.S. 66 now and 66 against 67 in future (OECD *Pensions
at a Glance 2021*, fig. 3.7). ν = 1.098687, 1.038558, 0.967240, 0.932899 (was 1.020785, 0.966884, 0.903744,
0.872658); they equal the `wpp2024_nraAdj` rows of `data/oecd29_population.csv`. `testEU.load('FR')` already
reads them.

**Task (paper-compute).** Rerun everything that reads France's ν, rebuild, test. Nothing else changes: the
U.S. and UK calibrations, the U.S. counterfactuals with French characteristics (incomes, leisure, voting, not
demography) and the 26-country test (unadjusted WPP for every country) must come out bitwise or to solver
tolerance unchanged; check that rather than assume it.

1. List first (in the ledger) every csv under `results/` that a France or FRUK model writes, from
   `REPLICATION.md`, `python/paper/README.md`, `python/US/README.md` and the drivers (`testEU` callers:
   `calibrateRhoGridEU.py`, `runShocksUS.py`, `runESC.py`, `runShocksXi.py`, `python/paper/runCalibration*.py`,
   `runShocks*.py`; `runESCcrra.py` and `python/US/c5Numbers.py` design X3 if they build France). Include the
   UK-host runs that use France at the UK's cuts (`heterogeneityUK`; same population sheet).
2. Rerun them in pipeline order, stage (i) then (ii) then the ESC stages (`runESC.py --spec size --phi 0.5
   --commonX --stage country pathHost corner`, and the CRRA/UK-host France rows where they exist), with the
   same options the existing rows were written with (read them off the csv columns and logs in `logs/`).
   Detached runs go in `logs/C7/`. Merge-writing drivers keep other rows; do not delete csvs.
3. `python/paper/build.py` (all), `--site` generation (`onlineAppendix.py`), `--map`; `writing/checkPaper.py`;
   `python/US/test_eu.py`, `test_esc.py`, `test_counts.py`, `test_oecd26.py`, `python/paper/test_onlineAppendix.py`.
   A test that pins an old French number: update the pinned value only if the change is the ν change, and say so.
4. Ledger `archive/notes/reviewResponse_2026-10/ledger_C7.md` (≤ 60 lines): files rerun with timings; old → new for every French number the
   paper or online appendix prints in prose or a generated table (France's ω and β, 2020 tax, the France
   reference rows, the design chosen under the U.S. λ (0.795), the own-λ row (still none?), the corner slope
   (still negative and λ-free?), France's design path, FRUK rows, section 6's ω ordering France > U.S. > UK);
   then every sentence of `writing/Paper` and `writing/OnlineAppendix/*.qmd` that quotes a number that moved
   (file:line, old, new). Do not edit `writing/Paper` or the qmd prose; generated tables are rebuilt only.

Do not commit. Do not push to Overleaf.
