# C6 reruns (notes/brief_C6runs.md): the job table scheduler.ps1 reads, in priority order (first eligible starts first).
# Columns (tab-separated): name, class (L long / S short), deps (comma list or -), require (case-sensitive regex the log
# must contain, or -), fail (case-sensitive regex the log must not contain, or -), command. Commands are those of
# logs/C6/dry_stage1.txt and dry_stage2.txt, the prepub CRRA runs split per rho; C5's and C4's as in logs/C5, logs/C4.
import os
REPO = r'C:\Users\sxj477\Documents\GitHub\SSDclaude'
PY = REPO + r'\.venv\Scripts\python.exe'
U = REPO + r'\python\US'
G = '--lo 0.5 --hi 2.0 --step 0.1 --anchor 1.0 --n 101 --ns 150 --verify 225 --verifyN 151 --interpKind linear --smoothKnots 4'
SG = '--rho 0.5 1.0 2.0 --n 101 --ns 150 --interpKind linear --smoothKnots 4'
EX = '--ns 150 --nsScan 50 --nCand2D 41 --commonX --designRule root --Ma 5'
LAYER = '--commonX --designRule root --Ma 5'
FRSC = 'baseline acute frIncome frLeisure frVoting frBoth frAll'
SWEPT = '16 of 16 points solved'
CAL = r'\(calibrated\)'
J = []


def j(name, cls, deps, req, fail, cmd):
    J.append((name, cls, deps or '-', req or '-', fail or '-', PY + ' ' + cmd))


def sweep(name, deps, args):
    j(name, 'S', deps, SWEPT, 'Traceback', args)


# --- stage (i): the U.S. sweeps (every other run reads them)
sweep('sweep_USCX', '', rf'{U}\calibrateRhoGrid.py {G} --commonX --force')
sweep('sweep_US', '', rf'{U}\calibrateRhoGrid.py {G} --force')
sweep('sweep_USMedCX', '', rf'{U}\calibrateRhoGrid.py {G} --medicare 0.029 --commonX --force')
sweep('sweep_USMed', '', rf'{U}\calibrateRhoGrid.py {G} --medicare 0.029 --force')
# --- stage (i) prepub: the exact CRRA cost calibrations, longest first
j('calCRRA_piR05', 'L', 'sweep_USCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --stage calib --rho 0.5 --bracket 30.0 70.0 --spec sizePiR --phi 0.5 --ns 150 --nsScan 0 --nScan 3 --xtol 0.001 --nCand2D 41 --tag Costs {LAYER}')
j('calCRRA_piR2', 'L', 'sweep_USCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --stage calib --rho 2.0 --bracket 3.2 8.0 --spec sizePiR --phi 0.5 --ns 150 --nsScan 0 --nScan 3 --xtol 0.001 --nCand2D 41 --tag Costs {LAYER}')
sweep('sweep_UKCX', 'sweep_USCX', rf'{U}\calibrateRhoGridEU.py --country UK {G} --commonX --force')
j('calCRRA_size05', 'L', 'sweep_USCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --stage calib --rho 0.5 --bracket 3.855 57.82 --spec size --phi 0.5 {EX}')
j('calCRRA_size2', 'L', 'sweep_USCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --stage calib --rho 2.0 --bracket 0.5782 34.69 --spec size --phi 0.5 {EX}')
j('esc_calib_LOG', 'S', 'sweep_USCX', r'-> p=[0-9]', 'FAILED|-> p=nan', rf'{U}\runESC.py --stage calib --spec size scale --phi 0.5 --commonX')
j('calCRRA_UK05', 'L', 'sweep_UKCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --host UK --stage calib --rho 0.5 --bracket 11.5 30.0 --nScan 4 --spec size --phi 0.5 --ns 150 --nsScan 0 --nCand2D 41 {LAYER}')
j('calCRRA_UK2', 'L', 'sweep_UKCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --host UK --stage calib --rho 2.0 --bracket 1.4 5.5 --nScan 4 --spec size --phi 0.5 --ns 150 --nsScan 50 --nCand2D 41 {LAYER}')
sweep('sweep_FRCX', 'sweep_USCX', rf'{U}\calibrateRhoGridEU.py --country FR {G} --commonX --force')
sweep('sweep_FRUKCX', 'sweep_USCX', rf'{U}\calibrateRhoGridEU.py --country FR --grouping UK {G} --commonX --force')
sweep('sweep_UKUSCX', 'sweep_USCX', rf'{U}\calibrateRhoGridEU.py --country UK --grouping US {G} --commonX --force')
# --- stage (ii) main, the headline variant and the LOG ESC leg
j('shocksCommonX', 'S', 'sweep_USCX,sweep_FRCX', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --commonX')
j('esc_calib_LOG_costs', 'S', 'sweep_USCX', r'-> p=[0-9]', 'FAILED|-> p=nan', rf'{U}\runESC.py --stage calib --spec sizePiR --phi 0.5 --tag Costs --commonX')
j('escPath', 'S', 'esc_calib_LOG', '', 'FAILED|Traceback', rf'{U}\runESC.py --stage path --spec size scale --phi 0.5 --commonX')
j('escShocks', 'S', 'esc_calib_LOG,sweep_FRCX', '', 'FAILED|Traceback', rf'{U}\runESC.py --stage shocks --spec size scale --phi 0.5 --commonX')
j('escCountry', 'S', 'esc_calib_LOG,sweep_FRCX,sweep_UKCX,sweep_UKUSCX,sweep_FRUKCX', '', 'FAILED|Traceback', rf'{U}\runESC.py --stage country --spec size scale --phi 0.5 --commonX')
j('escShocksUK', 'S', 'escCountry,sweep_FRUKCX', '', 'FAILED|Traceback', rf'{U}\runESC.py --stage shocks --host UK --spec size --phi 0.5 --commonX')
j('escPathHost', 'S', 'escCountry', '', 'FAILED|Traceback', rf'{U}\runESC.py --stage pathHost --spec size --phi 0.5 --commonX')
j('escCosts', 'S', 'esc_calib_LOG_costs,sweep_FRCX', '', 'FAILED|Traceback', rf'{U}\runESC.py --stage path shocks --spec sizePiR --phi 0.5 --tag Costs --scenarios baseline mild acute --commonX')
# the LOG rows of escExperiments.csv for runESCxi.py's self-check (rewritten by the merges below); escXiRobustness.csv
# is read by the online appendix and section 7's footnote, and siteData refuses it unless it reproduces escPath.csv
j('merge_log', 'S', 'escShocks', '', 'Traceback', rf'{U}\collectESCexperiments.py')
j('escXi', 'S', 'escPath,merge_log', 'SELF-CHECK PASSED', 'FAILED|Traceback', rf'{U}\runESCxi.py')
j('calCRRA_scale05', 'L', 'sweep_USCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --stage calib --rho 0.5 --bracket 0.4146 2.488 --spec scale --phi 0.5 {EX}')
j('calCRRA_scale2', 'L', 'sweep_USCX', CAL, 'FAILED', rf'{U}\runESCcrra.py --exact --stage calib --rho 2.0 --bracket 0.0377 0.1251 --spec scale --phi 0.5 {EX} --xtol 1e-06')
# --- stage (ii) prepub: the exact CRRA design paths and counterfactuals, per rho
for r, rs in (('05', '0.5'), ('2', '2.0')):
    j(f'shkCRRA_size{r}', 'L', f'calCRRA_size{r},sweep_FRCX', '', 'FAILED|Traceback', rf'{U}\runESCcrra.py --exact --stage path shocks --rho {rs} --spec size --phi 0.5 {EX}')
j('merge_pre', 'S', 'escShocks,merge_log,shkCRRA_size05,shkCRRA_size2', '', 'Traceback', rf'{U}\collectESCexperiments.py')
for r, rs in (('05', '0.5'), ('2', '2.0')):
    j(f'c5_designCRRA{r}', 'L', f'merge_pre,shkCRRA_size{r}', '', 'Traceback', rf'{U}\c5Numbers.py designCRRA --rho {rs}')
for r, rs in (('05', '0.5'), ('2', '2.0')):
    for term, t in (('s', 'steadyState'), ('f', 'finite')):
        j(f'C4_design{r}{term}', 'L', f'shkCRRA_size{r}', 'DONE', 'Traceback', rf'{U}\runHorizon.py --stage design --rho {rs} --terminal {t}')
j('stationaryESC', 'L', 'esc_calib_LOG,calCRRA_size05,calCRRA_size2', '', 'Traceback', rf'{U}\stationaryApproxESC.py --rho 0.5 1.0 2.0 --spec size --phi 0.5 --ns 150 --nCand2D 41 --commonX')
for r, rs in (('05', '0.5'), ('2', '2.0')):
    j(f'shkCRRA_piR{r}', 'L', f'calCRRA_piR{r}', '', 'FAILED|Traceback', rf'{U}\runESCcrra.py --exact --stage path shocks --rho {rs} --spec sizePiR --phi 0.5 --tag Costs --scenarios baseline mild acute {EX}')
for r, rs in (('05', '0.5'), ('2', '2.0')):
    j(f'shkCRRA_UK{r}', 'L', f'calCRRA_UK{r},sweep_FRUKCX', '', 'FAILED|Traceback', rf'{U}\runESCcrra.py --exact --host UK --stage shocks --rho {rs} --spec size --phi 0.5 --ns 150 --nCand2D 41 --scenarios {FRSC} {LAYER}')
for r, rs in (('05', '0.5'), ('2', '2.0')):
    j(f'shkCRRA_scale{r}', 'L', f'calCRRA_scale{r},sweep_FRCX', '', 'FAILED|Traceback', rf'{U}\runESCcrra.py --exact --stage path shocks --rho {rs} --spec scale --phi 0.5 {EX}')
for r, rs in (('05', '0.5'), ('2', '2.0')):
    j(f'shkCRRA_mild{r}', 'L', f'calCRRA_size{r},calCRRA_scale{r}', '', 'FAILED|Traceback', rf'{U}\runESCcrra.py --exact --stage shocks --rho {rs} --spec size scale --phi 0.5 --tag CostsMild --scenarios mild {EX}')
# --- the rest of stage (ii) main, C5's and C4's short runs
j('oecd26', 'S', 'sweep_USCX', '', 'Traceback', rf'{U}\runOECD26.py --force')
j('C5grid', 'S', 'sweep_USCX', '', 'Traceback', rf'{U}\runShocksUS.py --commonX --rho 1.0 0.6 0.7 0.8 0.9 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 --noFrance --out {REPO}\results\numerical\C5_US_shocksRhoGridCommonX.csv')
j('shocksMedicareCommonX', 'S', 'sweep_USCX,sweep_USMedCX,sweep_FRCX', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --medicare 0.029 --commonX')
j('freeTheta', 'S', 'sweep_USCX,sweep_FRCX', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --commonX --freeTheta --family french --out {REPO}\results\shocks\US_shocks_freeTheta.csv')
j('shocksUKCommonX', 'S', 'sweep_USCX,sweep_UKCX,sweep_FRUKCX', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --host UK --commonX')
j('shocksUKUSCommonX', 'S', 'sweep_USCX,sweep_UKUSCX,sweep_FRCX', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --host UKUS --commonX')
j('shocksXi', 'S', 'shocksCommonX', '', 'Traceback', rf'{U}\runShocksXi.py')
j('C4_log', 'S', 'escPath', 'DONE', 'Traceback', rf'{U}\runHorizon.py --stage log')
j('C4_horizon', 'S', 'sweep_USCX', 'DONE', 'Traceback', rf'{U}\runHorizon.py --stage horizon')
j('C4_resjumps', 'S', 'sweep_USCX', 'DONE', 'Traceback', rf'{U}\runHorizon.py --stage residuals jumps')
j('C4_scheme', 'S', 'sweep_USCX', 'DONE', 'Traceback', rf'{U}\runHorizon.py --stage scheme')
j('escPermanent', 'S', 'sweep_USCX', '', 'FAILED|Traceback', rf'{U}\runESC.py --stage permanent --spec scale flat --phi 0.25 0.5 0.75 --commonX')
j('escPermanentCRRA', 'S', 'sweep_USCX', '', 'FAILED|Traceback', rf'{U}\runESCcrra.py --stage permanent --rho 1.1 1.2 1.3 1.4 1.5 2.0 --spec size --phi 0.5 {LAYER}')
j('escSequentialCRRA', 'S', 'sweep_USCX', '', 'FAILED|Traceback', rf'{U}\runESCcrra.py --stage sequential --rho 0.5 2.0 {LAYER}')
j('c5_selfcheck', 'S', 'shocksCommonX,esc_calib_LOG,esc_calib_LOG_costs', 'SELFCHECK OK', 'Traceback', rf'{U}\c5Numbers.py selfcheck')
j('c5_a1', 'S', 'c5_selfcheck', '', 'Traceback', rf'{U}\c5Numbers.py a1')
j('c5_a13', 'S', 'c5_selfcheck', '', 'Traceback', rf'{U}\c5Numbers.py a13')
j('c5_a9', 'S', 'c5_selfcheck,C5grid,shocksUKCommonX,shocksUKUSCommonX', '', 'Traceback', rf'{U}\c5Numbers.py a9')
j('c5_design', 'S', 'c5_selfcheck,merge_pre', '', 'Traceback', rf'{U}\c5Numbers.py design')
# --- the vector-X variant (online appendix, NUM_Selection)
for c, args in (('FR', '--country FR'), ('UK', '--country UK'), ('UKUS', '--country UK --grouping US'), ('FRUK', '--country FR --grouping UK')):
    sweep(f'sweep_{c}', 'sweep_US', rf'{U}\calibrateRhoGridEU.py {args} {G} --force')
j('shocks', 'S', 'sweep_US,sweep_FR', '', 'Traceback', rf'{U}\runShocksUS.py {SG}')
j('shocksMedicare', 'S', 'sweep_US,sweep_USMed,sweep_FR', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --medicare 0.029')
j('shocksUK', 'S', 'sweep_US,sweep_UK,sweep_FRUK', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --host UK')
j('shocksUKUS', 'S', 'sweep_US,sweep_UKUS,sweep_FR', '', 'Traceback', rf'{U}\runShocksUS.py {SG} --host UKUS')
j('stationary', 'S', 'sweep_US', '', 'Traceback', rf'{U}\stationaryApprox.py --rho 0.5 0.7 1.3 1.5 2.0 --n 101 --ns 150 --smoothKnots 4')
ALLSWEEPS = 'sweep_US,sweep_USMed,sweep_FR,sweep_UK,sweep_UKUS,sweep_FRUK,sweep_USCX,sweep_USMedCX,sweep_FRCX,sweep_UKCX,sweep_UKUSCX,sweep_FRUKCX'
j('summary', 'S', ALLSWEEPS, 'written:', 'Traceback', rf'{REPO}\python\paper\runCalibrationUS.py --summaryOnly')
# --- the three merges, last, and C5's numbers that read them
j('merge_UK', 'S', 'escShocksUK,shkCRRA_UK05,shkCRRA_UK2', '', 'Traceback', rf'{U}\collectESCexperiments.py --host UK')
j('merge', 'S', 'escShocks,merge_pre,shkCRRA_size05,shkCRRA_size2,shkCRRA_scale05,shkCRRA_scale2', '', 'Traceback', rf'{U}\collectESCexperiments.py')
j('merge_costs', 'S', 'escShocks,escCosts,shkCRRA_size05,shkCRRA_size2,shkCRRA_scale05,shkCRRA_scale2,shkCRRA_piR05,shkCRRA_piR2,shkCRRA_mild05,shkCRRA_mild2', '', 'Traceback', rf'{U}\collectESCexperiments.py --costs')
j('c5_loss', 'S', 'c5_selfcheck,merge_costs', '', 'Traceback', rf'{U}\c5Numbers.py loss')
j('c5_lambda', 'S', 'c5_selfcheck,merge_costs', '', 'Traceback', rf'{U}\c5Numbers.py lambda')
j('c5_index', 'S', 'c5_selfcheck,merge,merge_costs,escPath,escCountry', '', 'Traceback', rf'{U}\c5Numbers.py index')

names = [x[0] for x in J]
assert len(names) == len(set(names)), 'duplicate job name'
for x in J:
    for d in x[2].split(','):
        assert d == '-' or d in names, (x[0], d)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jobs.tsv')
with open(out + '.tmp', 'w', encoding = 'utf-8', newline = '\r\n') as f:
    for x in J:
        f.write('\t'.join(x) + '\n')
os.replace(out + '.tmp', out)
print(len(J), 'jobs ->', out)
