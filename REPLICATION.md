# Replication

How every table, figure and model number in *Social Security Design and Its Political Support* (Berg and
Gonzalez-Eiras, 2026) is produced from this repository, for a referee or a reader who wants to rebuild the
paper or rerun the models. The paper's source is `writing/Paper/` (`main.tex`); the technical documentation
the paper cites, with the model, its equilibria and the algorithms, is `writing/main.tex`, one folder per
model variant. Commands are written as Windows paths, as the repository uses them; on another system
substitute `.venv/bin/python` for `.venv\Scripts\python.exe`.

## 1. Environment

Python 3.14 with the packages pinned in `pyenv.md` (numpy, pandas, scipy, matplotlib, symMaps and the
repository's own `gridsearch` package). From the repository root:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install numpy pandas scipy matplotlib symMaps
.venv\Scripts\python.exe -m pip install -e python
```

## 2. Data

Every input the models and the figures read is in `data/`. `data/README.md` lists each file with its
source and vintage, the script that reads it and the part of the paper that describes it. Nothing under
`results/` is an input. Two of the files are downloaded by scripts (stage (0) below) and committed, so no
other step touches the network.

## 3. From data to results

The models are solved by the three stages of `python/paper/`, whose `README.md` is the manual; the
Argentine arm runs on `python/InformalSavings/`, the U.S., France and UK arm on `python/US/`.

| Stage | Argentina | U.S. / France / UK | Writes |
|---|---|---|---|
| (0) data | `python\paper\dataTargets.py` (Penn World Table, through FRED) | `python\paper\oecdFigure1.py` (the cross-section of figure 1) | `data/argentina_*.csv`, `data/oecdFigure1*.csv` |
| (i) calibration | `python\paper\runCalibration.py` (about 3 h) | `python\paper\runCalibrationUS.py` (about an hour; `--prepub` adds the exact CRRA cost calibrations, many hours) | `results/calibration/`, `results/paper/*Summary.csv` |
| (ii) experiments | `python\paper\runShocks.py` (about 1 h) | `python\paper\runShocksUS.py` (about an hour; `--prepub` adds the CRRA endogenous-design runs, hours) | `results/shocks/`, `results/sweeps/`, `results/esc/`, `results/oecd26/` |
| (iii) build | `python\paper\build.py` | the same | `results/paper/{Tables,Figs}`, copied into `writing/Paper/` |

Each stage is run as `.venv\Scripts\python.exe <script>` from the repository root, skips work whose output
exists, takes `--force` to redo it and `--list` to report what would run. The settings behind every
published number are recorded in `python/paper/config.py`. `results/` is committed, including one pickled
model instance per calibration point, so stage (iii) runs on the committed results without re-solving
anything, and a solved instance can be loaded directly (see `python/<model>/README.md`).

The cross-country test of section 7 (the model calibrated to the OECD cross-section of figure 1) has two stage
(0) scripts of its own, run by hand: `python\paper\oecd29Data.py` (network) and `python\paper\oecd26Sample.py`
(the sample rule, no network) write `data/oecd29*.csv` and `data/oecd26_sample.csv`. Its runs belong to stage
(ii): `runShocksUS.py`'s entry `oecd26` calls `python\US\runOECD26.py` (about 20 minutes cold) on every run, and
the script recomputes only the rows whose inputs or U.S. calibration have changed, writing `results/oecd26/`.

The U.S. stage scripts also run the online appendix's Medicare reading of the U.S. calibration
(`config.US['readings']`: `results/calibration/USMedicare_rhoGrid*.csv`, `results/shocks/USMedicare_shocks*.csv`) and
the cost variants of section 7 (`config.US['esc']['costVariants']`: `results/esc/*Costs*.csv`, merged into
`results/esc/escAgeingCosts.csv`); no output reads them yet.

Two Argentine runs are not yet driven by the stage scripts either; no output reads them yet. The pre-reform
$\epsilon = 0$ variant of the calibration and its reform, after stage (i), with the scripts' grid settings
(`--interpKind cubic --smoothKnots 4 --nι 45 --ns 45`):
`python\InformalSavings\calibrateRhoGrid.py --lo 0.5 --hi 2.0 --step 0.1 --anchor 1.0 --commonX --epsPre0 --x0 0.693156
1.663414 0.292216 0.411944` writes `results/calibration/informalSavings_rhoGridCommonXEpsPre0.csv` and
`instancesCommonXEpsPre0/`; `shockUniversal.py --epsPre0` and `shockEEOnly.py` with `--pkldir` and `--csv` on those
and `--out universal_match_rho{ρ:.4f}_commonX_epsPre0.csv` (`--baseCsv` that, `--out eeOnly_match_rho{ρ:.4f}_commonX_epsPre0.csv`)
write the reform's two files per $\rho$ into `results/shocks/`. The reform's diagnostics at the headline calibration,
`python\InformalSavings\reformDiagnostics.py --rho 0.5 0.6 1.0 2.0 --pkldir results\calibration\instancesCommonX
--refine 60 --refineRho 0.5 0.6`, write `results/shocks/ARG_reform{FOC,B5,HouseholdSavings,Refine}_commonX.csv`:
the 2010 first order condition by generation and type, both sides of condition (B.5), households' savings rates,
and the low-$\rho$ tax response on a finer state grid.

The U.S. numbers of the review response that no output reads yet are written to `results/numerical/C5_*.csv` by
`python\US\c5Numbers.py <command>` after stages (i) and (ii): `a1` (the critical turnout ratio of proposition C.1),
`a9` (the counterfactuals ranked at every $\rho$), `loss`, `lambda`, `index`, `design` (log) and `designCRRA --rho
0.5` and `--rho 2.0` (about an hour each), and `a13`. `a9` also reads the U.S. counterfactuals at the other $\rho$ of
the sweep, `python\US\runShocksUS.py --commonX --rho 1.0 0.6 0.7 0.8 0.9 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9
--noFrance --out <repo>\results\numerical\C5_US_shocksRhoGridCommonX.csv` (about 30 minutes; the path must be
absolute, since the script runs from `python\US`).

Appendix D's numerical checks (`NUM_Horizon`, `NUM_Residuals`; their counts in `NUM_Selection`) are run by hand
after stages (i) and (ii), on the calibrated results: `python\US\runHorizon.py --stage log horizon residuals jumps
scheme` (about 40 minutes) and `--stage design` (the exact CRRA recursion at four horizons, about four hours at
$\rho = 0.5$ and 2) write `results/numerical/US_{horizon,horizonDesign,residuals,jumps,derivativeScheme}.csv`;
`python\InformalSavings\runHorizon.py` (about 45 minutes) writes `results/numerical/ARG_{horizon,residuals}_commonX.csv`.
Each checks first that the paper's horizon reproduces the published solve.

Every csv written by stages (i) and (ii) carries three non-key columns from the selection among tax
candidates (the robust-root section of the technical documentation): `nEqMax` and `nCandMax`, the largest
number of equilibria and of candidates at any state of the solve, and `nFallback`, the number of states
that fell back to the integral rule; `-1` marks a row whose solver did not count (the economic-equilibrium
rows, the tax step of the exact CRRA design recursion, failed cost calibrations), a blank a row written before the
counts existed (the earlier cost on the design and the path iteration, which the exhibits do not read). The CRRA endogenous-design files (`results/esc/*CRRA*.csv`) add the
design layer's settings and counts, `designRule`, `Ma`, `nEqθMax`, `nBrθMax` and `nFallbackθ`
(`config.US['esc']`). In the runs behind the committed results (the U.S. arm on 2026-10-25, its rows that read France
on 2026-10-26, the Argentine arm on 2026-10-23/24, its $\epsilon = 0$ variant included) every count reads one equilibrium,
so no selection among equilibria was ever made, and no solve fell back except at one state of the U.S. design layer
(`escShocksCRRA.csv`, ρ = 0.5, the cost on the design, French leisure, design chosen).

## 4. From results to the paper

`python\paper\build.py` reads `results/` and writes every generated table and figure, first to
`results/paper/` and then into `writing/Paper/Tables/` and `writing/Paper/Figs/`. It imports no model code
and takes seconds. Every generated `.tex` opens with a banner naming the command that rebuilds it and the
csv it was read from:

```
%% GENERATED by python/paper/build.py from results/ -- do not edit by hand.
%% Rebuild:  .venv\Scripts\python.exe python\paper\build.py --only US_ESC_Calibration
%% Source:   results/esc/escCalibration{,CRRA}.csv
```

The online appendix shows the exhibits listed on its replication page, the paper's marked as such, each with
the files it reads, a download of them and its rebuild command; its interactive figures draw in the browser from
the `data` outputs below (`results/paper/Data/*.csv`). It is built from the same `results/paper/` files in two
steps, `python\paper\build.py --site` and `quarto render writing\OnlineAppendix` (Quarto 1.10), into
`writing/OnlineAppendix/_book/`; its README explains the layout. The paper cites its pages through `\oa{key}`
(`writing/Paper/onlineAppendix.tex`, generated).

The map below lists every registered output, the files it reads and the tex files that input it; it is
rewritten by `build.py --map`. Of the files read, `results/paper/*Summary.csv` are written by stage (i),
`results/shocks/` and `results/sweeps/` by stage (ii)'s shock scripts, `results/esc/` by its
endogenous-design scripts (`python/US/runESC*.py`), `results/oecd26/` by the cross-country driver
(`python/US/runOECD26.py`), and `data/oecdFigure1.csv` and `data/oecd26_sample.csv` by stage (0).

<!-- outputs:begin -->
51 outputs, generated by `python\paper\build.py --map` on 2026-10-26. Reads are traced at build time, `rho*` standing for the files of a rho grid. "online appendix" marks an output the paper does not input, and "online appendix only" one that is not copied into `writing/Paper` at all; the online appendix's own replication page lists the exhibits it shows.

| Output | Kind | File in `writing/Paper` | Reads | Input by |
|---|---|---|---|---|
| `ArgentinaCalibration` | table | `Tables/ArgentinaCalibration.tex` | `data/ArgentinaTest.xlsx`, `results/paper/calibrationSummary.csv` | `Sections/Argentina.tex` |
| `ArgentinaUniversal` | table | `Tables/ArgentinaUniversal.tex` | `results/calibration/informalSavings_rhoGridCommonX.csv`, `results/paper/calibrationSummary.csv`, `results/shocks/eeOnly_match_rho*_commonX.csv`, `results/shocks/universal_match_rho*_commonX.csv` | `Sections/Argentina.tex` |
| `ARG_LOG_FourInOne` | figure | `Figs/ARG_LOG_FourInOne.pdf` | `results/paper/calibrationSummary.csv`, `results/sweeps/epsThetaGrid_rho*_commonX.csv` | online appendix |
| `ARG_CRRA_LOG` | figure | `Figs/ARG_CRRA_LOG.pdf` | `results/calibration/informalSavings_rhoGridCommonX.csv`, `results/paper/calibrationSummary.csv`, `results/shocks/eeOnly_match_rho*_commonX.csv` (16 files), `results/shocks/universal_match_rho*_commonX.csv` (16 files) | `Sections/Argentina.tex` |
| `USUKFRCalibration` | table | `Tables/USUKFRCalibration.tex` | `data/USMain_test.xlsx`, `results/paper/usCalibrationSummary.csv` | `Sections/OECD.tex` |
| `US_householdheterogeneity` | table | `Tables/US_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` | `Appendix/CalibrationOECD.tex` |
| `FR_householdheterogeneity` | table | `Tables/FR_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` | `Appendix/CalibrationOECD.tex` |
| `UK_householdheterogeneity` | table | `Tables/UK_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` | `Appendix/CalibrationOECD.tex` |
| `FRUK_householdheterogeneity` | table | `Tables/FRUK_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` | `Appendix/CalibrationOECD.tex` |
| `UKUS_householdheterogeneity` | table | `Tables/UKUS_householdheterogeneity.tex` | `results/paper/usCalibrationSummary.csv` | online appendix |
| `US_overview` | figure | `Figs/US_overview.pdf` | `results/shocks/US_shocksCommonX.csv` | `Sections/OECD.tex` |
| `US_ESC_overview` | figure | `Figs/US_ESC_overview.pdf` | `results/esc/escExperiments.csv`, `results/paper/usCalibrationSummary.csv` | `Sections/EndogenousTheta.tex` |
| `US_ESC_Calibration` | table | `Tables/US_ESC_Calibration.tex` | `results/esc/escCalibration.csv`, `results/esc/escCalibrationCRRA.csv` | `Sections/EndogenousTheta.tex` |
| `UK_ESC_Calibration` | table | `Tables/UK_ESC_Calibration.tex` | `results/esc/escCalibrationCRRAUK.csv`, `results/esc/escCountry.csv` | `Appendix/EndogenousDesignResults.tex` |
| `US_ESC_Country` | table | `Tables/US_ESC_Country.tex` | `results/esc/escCornerSlope.csv`, `results/esc/escCountry.csv` | `Appendix/EndogenousDesignResults.tex` |
| `US_ESC_Path` | figure | `Figs/US_ESC_Path.pdf` | `results/esc/escCalibration.csv`, `results/esc/escCalibrationCRRA.csv`, `results/esc/escPath.csv` | `Appendix/EndogenousDesignResults.tex` |
| `OECDdata` | figure | `Figs/OECDdata.pdf` | `data/oecdFigure1.csv` | `Sections/Introduction.tex` |
| `OECD26_Layer1` | figure | `Figs/OECD26_Layer1.pdf` | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer1.csv` | `Appendix/OECD26.tex` |
| `OECD26_Slopes` | table | `Tables/OECD26_Slopes.tex` | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer1.csv`, `results/oecd26/layer2.csv` | `Sections/EndogenousTheta.tex` |
| `OECD26_Omega` | table | `Tables/OECD26_Omega.tex` | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer2.csv` | `Appendix/OECD26.tex` |
| `NUM_Horizon` | table | `Tables/NUM_Horizon.tex` | `results/numerical/ARG_horizon_commonX.csv`, `results/numerical/US_horizon.csv`, `results/numerical/US_horizonDesign.csv` | `Appendix/TerminalStates.tex` |
| `NUM_Residuals` | table | `Tables/NUM_Residuals.tex` | `results/numerical/ARG_residuals_commonX.csv`, `results/numerical/US_derivativeScheme.csv`, `results/numerical/US_residuals.csv` | `Appendix/TerminalStates.tex` |
| `NUM_Selection` | table | `Tables/NUM_Selection.tex` | `results/calibration/FR_rhoGrid.csv`, `results/calibration/FR_rhoGridCommonX.csv`, `results/calibration/UK_rhoGrid.csv`, `results/calibration/UK_rhoGridCommonX.csv`, `results/calibration/US_rhoGrid.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/calibration/informalSavings_rhoGrid.csv`, `results/calibration/informalSavings_rhoGridCommonX.csv`, `results/esc/escCalibration.csv`, `results/esc/escCalibrationCRRA.csv`, `results/esc/escCalibrationCRRAUK.csv`, `results/esc/escCountry.csv`, `results/esc/escPath.csv`, `results/esc/escPathCRRA.csv`, `results/esc/escPermanent.csv`, `results/esc/escPermanentCRRA.csv`, `results/esc/escSequentialCRRA.csv`, `results/esc/escShocks.csv`, `results/esc/escShocksCRRA.csv`, `results/esc/escShocksCRRAUK.csv`, `results/esc/escShocksUK.csv`, `results/esc/escXiRobustness.csv`, `results/numerical/ARG_horizon_commonX.csv`, `results/numerical/ARG_stationaryApprox_commonX.csv`, `results/numerical/US_ESC_stationaryApprox.csv`, `results/numerical/US_derivativeScheme.csv`, `results/numerical/US_horizon.csv`, `results/numerical/US_horizonDesign.csv`, `results/numerical/US_stationaryApprox.csv`, `results/shocks/UK_shocks.csv`, `results/shocks/UK_shocksCommonX.csv`, `results/shocks/US_shocks.csv`, `results/shocks/US_shocksCommonX.csv`, `results/shocks/eeOnly_match_rho*.csv` (16 files), `results/shocks/eeOnly_match_rho*_commonX.csv` (16 files), `results/shocks/universal_match_rho*.csv` (16 files), `results/shocks/universal_match_rho*_commonX.csv` (16 files), `results/sweeps/epsThetaGrid_rho*.csv`, `results/sweeps/epsThetaGrid_rho*_commonX.csv` | `Appendix/TerminalStates.tex` |
| `OECD_Countries` | table | online appendix only | `data/oecdFigure1.csv` | -- |
| `OECD_Sources` | table | online appendix only | `data/oecdFigure1_sources.csv` | -- |
| `OECD_Correlations` | table | online appendix only | `results/paper/oecdCorrelations.csv` | -- |
| `ARG_RhoGrid` | figure | online appendix only | `results/calibration/informalSavings_rhoGridCommonX.csv` | -- |
| `OECD_RhoGrid` | figure | online appendix only | `results/calibration/FR_rhoGridCommonX.csv`, `results/calibration/UK_rhoGridCommonX.csv`, `results/calibration/US_rhoGridCommonX.csv` | -- |
| `ESC_Timing` | table | online appendix only | `results/esc/escPermanent.csv`, `results/esc/escPermanentCRRA.csv`, `results/esc/escSequentialCRRA.csv` | -- |
| `NUM_Stationary` | table | online appendix only | `results/numerical/ARG_stationaryApprox_commonX.csv`, `results/numerical/US_ESC_stationaryApprox.csv`, `results/numerical/US_stationaryApprox.csv` | -- |
| `ARG_LeisureCalibration` | table | online appendix only | `results/paper/calibrationSummary.csv` | -- |
| `ARG_LeisureRho` | table | online appendix only | `results/calibration/informalSavings_rhoGrid.csv`, `results/calibration/informalSavings_rhoGridCommonX.csv`, `results/paper/calibrationSummary.csv` | -- |
| `OECD_Regroupings` | table | online appendix only | `results/paper/usCalibrationSummary.csv` | -- |
| `OECD_LeisureCalibration` | table | online appendix only | `results/paper/usCalibrationSummary.csv` | -- |
| `OECD_LeisureGroups` | table | online appendix only | `results/paper/usCalibrationSummary.csv` | -- |
| `ESC_CostCalibration` | table | online appendix only | `results/esc/escCalibration.csv`, `results/esc/escCalibrationCRRA.csv` | -- |
| `OECD_Medicare` | table | online appendix only | `data/USMain_test.xlsx`, `results/calibration/USMedicare_rhoGridCommonX.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/paper/usCalibrationSummary.csv` | -- |
| `US_TaxState` | figure | online appendix only | `results/numerical/C5_taxPolicyState.csv` | -- |
| `US_Strategic` | table | online appendix only | `results/numerical/C5_strategicTerm.csv` | -- |
| `NUM_HorizonPaths` | table | online appendix only | `results/numerical/ARG_horizon_commonX.csv`, `results/numerical/US_horizon.csv`, `results/numerical/US_horizonDesign.csv` | -- |
| `NUM_SelectionFiles` | table | online appendix only | `results/calibration/FR_rhoGrid.csv`, `results/calibration/FR_rhoGridCommonX.csv`, `results/calibration/UK_rhoGrid.csv`, `results/calibration/UK_rhoGridCommonX.csv`, `results/calibration/US_rhoGrid.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/calibration/informalSavings_rhoGrid.csv`, `results/calibration/informalSavings_rhoGridCommonX.csv`, `results/esc/escCalibration.csv`, `results/esc/escCalibrationCRRA.csv`, `results/esc/escCalibrationCRRAUK.csv`, `results/esc/escCountry.csv`, `results/esc/escPath.csv`, `results/esc/escPathCRRA.csv`, `results/esc/escPermanent.csv`, `results/esc/escPermanentCRRA.csv`, `results/esc/escSequentialCRRA.csv`, `results/esc/escShocks.csv`, `results/esc/escShocksCRRA.csv`, `results/esc/escShocksCRRAUK.csv`, `results/esc/escShocksUK.csv`, `results/esc/escXiRobustness.csv`, `results/numerical/ARG_horizon_commonX.csv`, `results/numerical/ARG_stationaryApprox_commonX.csv`, `results/numerical/US_ESC_stationaryApprox.csv`, `results/numerical/US_derivativeScheme.csv`, `results/numerical/US_horizon.csv`, `results/numerical/US_horizonDesign.csv`, `results/numerical/US_stationaryApprox.csv`, `results/shocks/UK_shocks.csv`, `results/shocks/UK_shocksCommonX.csv`, `results/shocks/US_shocks.csv`, `results/shocks/US_shocksCommonX.csv`, `results/shocks/eeOnly_match_rho*.csv` (16 files), `results/shocks/eeOnly_match_rho*_commonX.csv` (16 files), `results/shocks/universal_match_rho*.csv` (16 files), `results/shocks/universal_match_rho*_commonX.csv` (16 files), `results/sweeps/epsThetaGrid_rho*.csv`, `results/sweeps/epsThetaGrid_rho*_commonX.csv` | -- |
| `OECD26_Layer1_29` | figure | online appendix only | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer1.csv` | -- |
| `OECD26_Slopes_29` | table | online appendix only | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer1.csv`, `results/oecd26/layer2.csv` | -- |
| `OECD26_Omega_29` | table | online appendix only | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer2.csv` | -- |
| `OECD26_Layer1_cses` | figure | online appendix only | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer1.csv` | -- |
| `OECD26_Slopes_cses` | table | online appendix only | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer1.csv`, `results/oecd26/layer2.csv` | -- |
| `OECD26_Omega_cses` | table | online appendix only | `data/oecd26_sample.csv`, `data/oecdFigure1.csv`, `results/calibration/US_rhoGridCommonX.csv`, `results/oecd26/anchor.csv`, `results/oecd26/layer2.csv` | -- |
| `ARG_ReformPaths` | data | online appendix only | `results/calibration/informalSavings_rhoGridCommonX.csv`, `results/paper/calibrationSummary.csv`, `results/shocks/eeOnly_match_rho*_commonX.csv` (16 files), `results/shocks/universal_match_rho*_commonX.csv` (16 files) | -- |
| `OECD_Counterfactuals` | data | online appendix only | `results/paper/usCalibrationSummary.csv`, `results/shocks/UKUS_shocks.csv`, `results/shocks/UKUS_shocksCommonX.csv`, `results/shocks/UK_shocks.csv`, `results/shocks/UK_shocksCommonX.csv`, `results/shocks/USMedicare_shocks.csv`, `results/shocks/USMedicare_shocksCommonX.csv`, `results/shocks/US_shocks.csv`, `results/shocks/US_shocksCommonX.csv`, `results/shocks/US_shocksXiCommonX.csv` | -- |
| `ESC_Counterfactuals` | data | online appendix only | `results/esc/escExperiments.csv`, `results/esc/escExperimentsUK.csv`, `results/esc/escXiRobustness.csv`, `results/paper/usCalibrationSummary.csv` | -- |
| `ESC_Paths` | data | online appendix only | `results/esc/escCalibration.csv`, `results/esc/escCalibrationCRRA.csv`, `results/esc/escPath.csv`, `results/esc/escPathCRRA.csv`, `results/esc/escPathHost.csv`, `results/esc/escXiRobustness.csv`, `results/paper/usCalibrationSummary.csv` | -- |
<!-- outputs:end -->

## 5. Outside the pipeline

- **Figure 5.1** (`writing/Paper/Figs/coverageArg.eps`, beneficiaries of Argentina's national pension system and of
  non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020), table 6, which reproduces the
  Boletín Estadístico de la Seguridad Social. The data file and the script are not yet in the
  repository (TODO: add `data/argentinaCoverage.csv` with a Readme row and a builder in `python/paper`).
- **Numbers quoted from other sources** (pension spending across the OECD, the coverage and spending
  figures of the Argentine reform, replacement rates) are cited where they appear; the calibration
  appendices state every target and its source.
- **Derivations and algorithms** are in `writing/main.tex`, the technical documentation, whose equation
  labels the code's docstrings cite.

## 6. Checks

- `python\runTests.py`: the model, solver and online-appendix test suites (24 fast suites, about 7 minutes; `--all` adds
  five slow ones, about an hour).
- `python\paper\build.py --list`: every registered output is buildable from the committed results.
- `writing\checkPaper.py`: every cross-reference and citation in the paper resolves, with word counts per
  section and the list of pending items.
