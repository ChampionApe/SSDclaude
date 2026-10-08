# Brief: the runs for the two new cost specifications (phase C)

For the `paper-compute` agent. Plan: `notes/plan_endogenousDesign.md` §C (C.1 decisions 1-4 and 9, C.4
gate 1, C.5 schema). Read `python/US/README.md` ("Endogenous θ"), the top entry of
`python/US/RESEARCH_LOG.md` (the coder's, phase B), `python/US/runESC.py`'s docstring and
`notes/crossCuttingFindings.md` #13 and #14 before running anything. Everything is LOG at $\rho = 1$ under
the common-$X$ variant, `--commonX --phi 0.5`. Interpreter and logging as your agent definition says; logs
under `logs/escVariants/` (create it; `logs/` is gitignored).

## 1. Self-check (before anything else)

`python\US\runESC.py --spec size --phi 0.5 --commonX --stage calib --tag _selfcheck` (about 2 min) must
reproduce the committed row of `results/esc/escCalibration.csv` for `size`, `phi` 0.5, `commonX` True:
$\lambda$ = `p` = 8.64320735564998 to $10^{-6}$, $f(\theta^{\ast})$ = 0.98156, $f(0)$ = 0.76212, $\tilde V$ =
0.43565. Then delete `results/esc/escCalibration_selfcheck.csv`. If it does not reproduce, stop and report.

## 2. Backup and the untouched rows

Copy every `results/esc/*.csv` to your scratchpad directory before the runs. After the runs,
`python\paper\compareResults.py --only esc` (against HEAD) must show, for every file, only rows *added*
(the `sizeL` and `sizeLQ` rows) and new columns (`kappa`, `kappaFrom`, `θPin`, `ownKind`), with the largest
difference on the aligned `size`/`scale`/`none` rows exactly 0. Quote its output per file.

## 3. The runs, in order (each into its own log; background with `run_in_background`, polled by `grep -q`
in an `until` loop, never `tail -F`)

a. `runESC.py --spec sizeL sizeLQ --phi 0.5 --commonX --stage calib` (sizeL about 2 min; sizeLQ's joint
   calibration, `--pinKappa UK` by default, about 25 min). Read the log: for `sizeL` the scan's sign changes
   (there must be exactly one); for `sizeLQ` the outer scan over $\kappa$ and the bracket it found. Expected
   from the theorist's proxies (`notes/esc_variants.md` §4.4, $(\beta,\omega)$ held there, so second-decimal
   differences): $\kappa \approx 0.11$, $\lambda \approx 5.8$, France predicted about 0.78; $\lambda_L \approx 1.7$.
   **If the `sizeLQ` row comes back `converged = False`**, rerun
   `runESC.py --spec sizeLQ --phi 0.5 --commonX --stage calib --pinKappa FR` untagged, so that France's corner
   pins $\kappa$ and the UK becomes the prediction; say so in the report and skip step d.
b. `runESC.py --spec sizeL sizeLQ --phi 0.5 --commonX --stage path shocks country` (about 20-30 min). The
   country stage writes France's own parameter as a threshold (`ownKind = 'threshold'`) under both specs.
c. `runESC.py --spec sizeL sizeLQ --phi 0.5 --commonX --stage shocks --host UK` (about 10 min; needs the
   converged `own` UK rows of step b in `escCountry.csv`; a spec without one is skipped by the driver, say
   which).
d. `runESC.py --spec sizeLQ --phi 0.5 --commonX --pinKappa FR --tag _kappaFR --stage calib country shocks`
   (about 40 min): the alternative pinning, into `escCalibration_kappaFR.csv`, `escCountry_kappaFR.csv` and
   `escShocks_kappaFR.csv` (expected $\kappa \approx 1$, the UK predicted about 0.34). Only if step a
   converged under `--pinKappa UK`.
e. `runESC.py --spec sizeLQV --phi 0.5 --commonX --kappa <the kappa of step a's sizeLQ row> --stage calib
   country` (about 8 min): the $\tilde V$-weighted record at the same shape (its U.S. and UK rows should
   reproduce `sizeLQ`'s to the third decimal; France's differs).
f. `python\US\collectESCexperiments.py` and `python\US\collectESCexperiments.py --host UK`.
g. Step 2's comparison.

Wall-time budget 2.5 h. A stage that fails for one spec does not stop the other; report the traceback's
last lines.

## 4. Report (at most 25 lines, numbers with their csv and row)

- Per spec (`sizeL`, `sizeLQ`): $\lambda$, $\kappa$, `kappaFrom`, `θPin`, `converged`, `θStar`, `choice`,
  `τDrift`, `RDrift`, $f(\theta^{\ast})$, $f(0)$, `nEqMax`, `nFallback` (`escCalibration.csv`); the scan's sign
  changes from the log.
- Per spec, the country rows: the designs the UK, France and UKUS choose under the U.S. parameters, and the
  own values with `ownKind` (`escCountry.csv`); under `sizeLQ` the UK's own $\lambda$ against $\lambda_{US}$
  (the difference, from the driver's print).
- Per spec, the eight scenarios and France at $t_0$: `θ_t0`, `τ_t0` pinned and chosen, `sr_t0`, `ww_t0`
  (`escExperiments.csv`, $\rho = 1$); the design path by date (`escPath.csv`).
- The UK-host rows (`escExperimentsUK.csv`), the `_kappaFR` rows (calibration, country and the shocks at
  $t_0$) and the `sizeLQV` rows, in one or two lines each; every economy's `Mabs` beside its `Vtilde`.
- The checks: the self-check, the backup comparison, the sign changes, the drifts.
- The README status line and the US log entry you wrote (at most ten lines).
