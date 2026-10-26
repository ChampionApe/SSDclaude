# Ledger C7: France's ν at the PaG 2021 retirement-age gap

Brief `notes/brief_C7.md` (W16, RKB 2026-10-26): `data/FRMain.xlsx` `population!D` (the only sheet changed) has ν 1990–2080
= 1.098687, 1.038558, 0.967240, 0.932899 (was 1.020785, 0.966884, 0.903744, 0.872658). Old = HEAD (`logs/C7/old/`); numbers from
`logs/C7/{compare,ledger_numbers}.py`.

## 1. What reads France's ν (listed before the runs)

Stage (i): `calibration/{FR,FRUK}_rhoGrid{,CommonX}.csv`, `paper/usCalibrationSummary.csv`. Design given:
`shocks/{US,USMedicare,UK,UKUS}_shocks{,CommonX}.csv`, `US_shocks_freeTheta.csv`, `US_shocksXiCommonX.csv`,
`numerical/C5_US_shocksRhoGridCommonX.csv`. Design chosen: `esc/escShocks`, `escCountry`, `escPathHost`, `escCornerSlope`,
`escShocksUK`, `escShocksCRRA`, `escShocksCRRAUK`, merges `escExperiments{,UK}`. C5: `C5_ranking`, `C5_indexUnits`,
`C5_designDecomp{,CRRA_rho*}` (income profile only). Not the workbook: `oecd26/` (rerun without `--force`: nothing recomputed).

## 2. Runs (`logs/C7/`: `gen_jobs.py` -> `jobs.tsv`, `scheduler.log`, a log per job)

Self-check: runESC's country stage on HEAD's ν reproduces escCountry's France row bitwise (choice 0.7953757104, ω
1.3459341092; `selfcheck.log`). 37 jobs, 0 failed, 09:54–12:12 (cap 2 from 09:57, RKB): sweeps 0.21 h each, runShocksUS/Xi
and C5grid ≤0.22 h, runESC ≤0.29 h, exact CRRA (size, scale, UK host; ρ 0.5, 2; frLeisure, frAll and France's row, `--tag`
csvs folded in by `mergeTags.py`) 0.42–0.46 h each, merges and c5 a9/index/design ≤0.07 h.

## 3. What moved besides France's own rows

The brief expected the French-characteristics rows unchanged. Income and voting are: η_FR moves by one factor across
types (spread ≤2.2e-16, absorbed by `shocks.ηLevel`), μ_FR is data (`inputcheck.log`); rows ≤2e-11 (design given),
≤3e-12 (LOG ESC), C5_designDecomp ≤1.6e-11. **Leisure is not**: France's calibrated X is pinned by hours at France's
wage, which depends on its capital per worker and so on ν. The leisure row's X factor moves ×0.952/0.970/0.985 at
ρ 0.5/1/2, so the leisure and all-French rows' workweek moves +0.52/+0.32/+0.16 h, their rates ≤5e-5 (CRRA hours-unit
drift; LOG bitwise). Every other row: bitwise under common X, ≤9e-12 under vector X (#1).

## 4. French numbers, old -> new (ρ = 1, common X, unless noted)

| quantity | old | new |
|---|---|---|
| ν 2020 (table 6.1; β, τ_2020, ηH/ηL unchanged) | 0.97 | **1.04** |
| ω at ρ 0.5 / 1 / 2 | 1.965 / 1.346 / 1.152 | 2.210 / **1.446** / 1.197 |
| X (× U.S.); FRUK X | 6.90 (1.66); 6.84 | **6.64 (1.60)**; 6.58 |
| η_i; FRUK η_i | 1.10/1.56/2.53; 0.93/1.49/3.06 | 1.09/1.55/2.51; 0.92/1.47/3.03 |
| R_2020 (prediction); s/Y 2020, ρ 0.5 / 1 / 2 | 2.181/2.265/2.335; .130/.124/.119 | 2.426/2.432/2.436; .126/.124/.122 |
| France rows' sr_t0 (τ, workweek are targets), ESC LOG / CRRA 0.5 / 2 | 0.1768 / 0.1862 / 0.1695 | 0.1766 / 0.1796 / 0.1742 |
| design under the U.S. λ = 11.345 (Ṽ 0.218); own λ | 0.79538; none | 0.79527 (prints 0.795); none |
| corner slope, 1990 / 2020 electorate | −0.0927 / −0.0860 | −0.0998 / −0.0923, same at λ = 0, 11.345, 100 |
| path under U.S. λ, θ 2020/50/80/2110 | .7954/.8118/.8217/.8238 | .7953/.8125/.8227/.8249 (U.S. 2050 .8019) |
| ω order France > U.S. > UK | holds | holds at every ρ (1.446 > 1.231 > 1.103) |
| leisure Δworkweek, U.S. host, ρ 0.5/1/2 | −4.55/−4.35/−4.20 h | −4.03/−4.03/−4.04 h |
| all French Δworkweek; on the UK, leisure | −3.61/−3.61/−3.64; +1.21 | −3.08/−3.29/−3.48; +1.54 |
| NUM_Selection design-layer fallbacks | 0 | **1** (escShocksCRRA, ρ 0.5, cost on the design, frLeisure, chosen) |

Changed: USUKFRCalibration, FR_/FRUK_householdheterogeneity, NUM_Selection, OECD_Leisure*, OECD_Regroupings, figs 6.1, 7.1.

## 5. Sentences that quote a moved number or claim (not edited)

- `Sections/OECD.tex:10`: "ν_2020 = 1.34 against 0.97" -> 1.04; "1.7 times in France" -> 1.6; "highest in France, 1.35" -> 1.45.
- `Sections/OECD.tex:35`: "shortens the workweek by more than the whole gap to France's" -> by 4.03 of the 4.15-hour gap
  (97%) at ρ = 1, likewise at ρ 0.5, 2 and every ξ: no longer "more than".
- `Appendix/CalibrationOECD.tex:22`: "from 1.10 to 2.53" -> 1.09 to 2.51; "taste for leisure is 6.90" -> 6.64.
- `Appendix/TerminalStates.tex:45`: "at no state does every candidate fail the test" -> fails at one state (table note says so).
- OA `oecd-parameters.qmd:10-12`: leisure response "nearly unchanged" in ξ -> −4.14/−4.03/−3.87 h at ξ 0.2/0.3/0.4 (was −4.36/−4.35/−4.29).
- Still true: `EndogenousDesignResults.tex:11` (0.795, a quarter of the distance, 0.218, 20.6%), `CalibrationOECD.tex:36`,
  OA `oecd-ies.qmd:7-9`, `oecd-countries.qmd:15-17` (4.16 < 6.64 < 7.93), `oecd-leisure.qmd:31-33`, `esc-paths.qmd:15-17, 74-76`.
