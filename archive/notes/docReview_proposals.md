# Technical note review: proposed edits (2026-11-04; brief `notes/brief_codeDocReview.md`, steps 3-4)

Three read-only reviews against the code as fixed on 2026-11-04 (D1 `writing/US`, D2 `writing/informalSavings`, D3
`writing/informalAnalytical`, `writing/data`, `main.tex`). Line numbers are the reviewers'; a writer re-derives every
math item before editing. Lead-verified: D2-7 (`model.stateAtT0` also carries s_{t0-1,i}/s_{t0-1} and h_{t0-1}). The
labour-supply FOC slip (D2-1, D3-2) was found independently in both informal models.

## D1 writing/US (25k words; aim 15-16k)
**Errors**
1. model_competitiveequilibrium:43 direction wrong: s_i/s - 1 = (r_i-1)(1 + (1-a)/a tau'(1-theta')/(1+B)): lower theta
   spreads savings (num_esc:65 has it right). Replace with the dispersion sentence.
2. model_PEE:29 "the numerator is larger for low-income retirees" false; the ratio is (benefits a larger share of
   old-age income the poorer the retiree).
3. model_setup:20,24 Y and w carry A_t, R does not; code normalises TFP to 1 (base.py:148): drop A_t, say so.
4. model_competitiveequilibrium:85 "differ except with a single type" false under variant A (hbar = h): reword.
5. model_calibration:58 mu = X^{-xi/(1+xi)} contradicts mu = sum gamma y^x (:47): write proportional or full form.
6. model_esc:33 "per contributor" -> "per member of the retiring cohort".
7. model_esc:101 E is the summand without the weight omega gamma p mu.
8. model_esc:94 retirees favour a more contributive system only at a given continuation tax.
9. model_esc:121 "every dependence on theta' arrives through ln h_t" contradicts the paragraph: "enters additively".
10-15. Notation clashes: A(theta,tau), B(theta,tau) vs TFP and B^i (-> chi^E, chi^F); v vs upsilon; z_t state vs FOC;
   mu voting shares vs hours unit (-> psi); lambda scale vs cost (-> Lambda); h_j reused (write 1/z_j^eta); in sec:ESC
   calT grid vs policy, Theta grid/policy/coefficients, calA/calB/calC, f FOC vs cost, h root fn vs hours.
16-17. num_ee:35,52 golden-section -> Brent; bracket (1e-6, min(0.75, 0.99 Gs_max)) widened upward (model.py:638-679).
18. num_calibration:18 "bit-for-bit" -> "to the calibration tolerance (1e-8)".
19. theta identification: the paper's theta is a datum (data/oecd26_theta.csv variant C, db['θ0']; RR0 unread);
   model_calibration:12-25, model_esc:2,71-75, num_calibration:16, num_esc:190 still describe the RR route as the
   calibration (0.728, France theta = 1). Open with "imposed from the design index; without it, identified from RR".
20. Stale pre-C numbers (lambda 25.08/11.35/2.64, theta* 0.728, Vtilde 0.436, ageing 0.728->0.820): remove (cuts 34-37).
21. num_esc:180 the design is pinned at the U.S. value (shocks.py:150-191), not re-derived from RR data.
22. model_esc:87, num_esc:2 under CRRA each seqFOC summand is weighted by (c2)^{1-1/rho} (modelESC.sequentialFOC).
**Inconsistencies**
23. num_peeLOG:28 describe solveRobust as run (gradient first, checked against the grid every solve, polish on miss).
24. France/UK protocol undocumented (beta imposed, 1-D root in omega, hours relative to the U.S., rescaleX so
   Gamma_h != 1 under vector X): add a five-line paragraph to sec:calibration:targets.
25. 'sizePiR' undocumented (lambda pi_t, pi_t = Pi_t/R_t taken as given, iterated to a fixed point): two sentences.
26. Code cites missing labels (fix in code): alg:fast/alg:gridsearch -> alg:LOG:fast/alg:LOG:gridsearch (US policy.py,
   model.py); eq:fast -> eq:LOG:foc (base.py:512,525); eq:w0, EE:c0 are informal-model labels (base.py).
27. num_esc:51,168,170 the permanent timing survives only in the tests: delete "Both are reported", the three-timings
   sentence, escPermanent.csv.
28. num_peeCRRA:22 several crossings: the lowest is taken and the count reported.
**Cuts** (lab-notebook material: dated runs, measurements, superseded solvers)
29-33. num_esc:2, 33, 49-51, 94-104, 114-118: cut measurements and "the earlier solver/version" passages; keep the
   reasoning (e.g. the frozen state removes d_aW da/dtheta').
34. num_esc:121-148 the FOC design solver, piloted and not adopted (~1,200 words) -> one sentence.
35. num_esc:156-170 bookkeeping, dated parentheses, numbers, file names.
36. num_esc:182-201 Checks (~2,500 words) -> one line per check, values in test_esc.py / results/esc/.
37. model_esc:37 history of reduced forms and stale magnitudes -> two sentences.
38. model_esc:20,26 literature review -> three sentences, pointer to the paper.
39. num_robustroot:35,53, num_peeCRRA:47,71 history and measurements.
40. Repetitions: kappa -> p remark (keep model.tex:9), decoupling vs informal models (keep model_PEE:38), num.tex:15,
   num_peeLOG:18, num_peeCRRA:57, num_esc:8 (~400 words -> 4 sentences), model_PEE:56-61.

## D2 writing/informalSavings (18k words; aim 12.5k)
**Errors**
1. model_setup:102 labour-supply FOC: pension term must be discounted, theta' bbar'/(R'/p) (CE:9 and the savings rule do).
2. model_setup:20,24,31 A_t in Y and w only (TFP normalised, base.py:146); A_t reused for the informal pension
   coefficient (auxiliary:Ainf) and the calibration bracket (model_calibration:25, rename e.g. Lambda_t).
3. num_peeLOG:54 "ln h' differs from ln Theta_h' by a term constant in tau_t" false; true of ln R' (base.py:293-306).
4. num_ee:40,47 golden-section -> Brent; bracket (1e-6, min(0.75, 0.99 Gs_cap)) widened; cap carries Gamma_h.
5. num_calibration:44,45,58 cubic interpolants and pinned knots go to BOTH solvers (calibrateRhoGrid.py:170-178).
6. num_shock:36 "agrees to 1e-10" -> to the grid's resolution of tau (README: 1.6e-6 at rho 1).
7. num_shock:22-28 eq:shockState omits the retirees' shares s_{t0-1,i}/s_{t0-1} and h_{t0-1} (model.stateAtT0,
   verified): add them and one sentence on how the shares enter the t0 condition.
8. model_calibration:9,78 tau target is not 12.5%: tau0 from spending/GDP with GDP formal + informal (model.taxTarget,
   0.1181); check "groups j = 1, 3" against RRGroups.
9. Notation: p_t^0 vs p_{t,0}; s_{t-1}^i vs s_{t,i}; v vs upsilon; sigma_x used before defined (CE:55 vs 68).
**Inconsistencies**
10. num_peeLOG:16, num_peeCRRA:7 "align, do not refine" measured on linear interpolants; under cubic a default.
11. num_robustroot:53 fallback is selectMax over endpoints and downward crossings.
12. num_peePath:26 adjacent surviving nodes; an exact zero counts as one crossing (sign-run rule, 2026-11-04).
13. num_calibration:34 the frozen-iota starting point does not exist: starting points are the rho=1 anchor and the march.
14. num_calibration:70 rho = 1 needs "no previous solution to extrapolate from" (it does need --x0).
15. Code cites eq:calibration:etaCommonX, Xsolve (model.py:388,414,1048), eq:LOG:epsCondition (reformDiagnostics):
   not in this folder -> label the common-X display in model_calibration:91 (or retarget).
16-17. num_ee:32 "repeated from the model section" false; num_ee:23 garbled Gammas sentence.
18. num_peeCRRA:5 iota*(tau) is evaluated at the CRRA steady state.
19. model_calibration:11,13 pre-reform epsilon is computed (getEps: coverage x relative benefit x discount): say so.
**Cuts** (~4,500 words)
20. num_robustroot:19-23 extended grid (no InformalSavings code uses robustRoot). 21. num_robustroot:33,51,55 history.
22. num_robustroot:51 the three forms of the test -> ~150 words. 23. num_peeLOG:26-35 grid bounds -> ~200 words.
24. num_peeLOG:96 measurement. 25. num_peeLOG:109 smoothing -> 3 requirements; num_peeCRRA:82 -> cross-reference.
26. num_peeLOG:44,51,71,74 "state does not enter the fixed point" four times -> once.
27. num_peeCRRA:70-75 duplicates num_peeLOG:84-89. 28. num_peeCRRA:5,7 rejected anchors, measured percentages.
29. num_peeCRRA:77-85 numerical-stability bullets -> rho = 1 and the terminal identity. 30. num_peeCRRA:67 footnote.
31. num_peeCRRA:93,102 cost commentary. 32. num_peePath:36,40,42,47 -> ~1,000 of 1,570 words.
33. num_shock:19 stale epsilon percentages; :31-33 shorten. 34. num_calibration:14-18 K/Y rationale -> ~100 words.
35. num_calibration:45,70-72 refinement and retry ladder -> one paragraph. 36. num_calibration:57-60 bookkeeping.
37. model_competitiveequilibrium:45-46 dangling restart. 38. model_finitehorizon CRRA terminal: cut the aside.
39. num_robustroot:2, num.tex:5-10 preamble. 40. model.tex:5-9, model_setup:2-8 repetitions.

## D3 writing/informalAnalytical (10.3k; aim 7k), writing/data (2.2k; aim 1.7k), main.tex
**Errors**
1. data_variants:139 "the five countries above 0.25 are the five C drops" false: DNK (pi 0.19) is dropped by its
   negative A slope.
2. model_setup:108 labour-supply FOC: pension term must carry p_t/R_{t+1} (as D2-1); same in model_calibration:25.
3. model_setup:50-52 c-tilde defined with the exponent inside and applied again; define once.
4. Typos: model_setup:31 s_{t_1}; :4-5 broken p_{t,i}; :2 vs :89 sums over i and j.
5. model_PEE v vs upsilon (and upsilon vs nu_t).
6. model_PEE:17 log value: beta ln(R/p), not beta ln R.
7. data_tiers:36 alpha 0.30 (data) vs 0.43 (analytical); tau = S/(100(1-alpha)).
**Inconsistencies**
8. data_inputs:28 "the rest are drafts": variant C of oecd26_theta.csv is the paper's theta (config.US['theta']).
9. data_variants:93-97 A, A2pt, C have theta for 23 countries (AUS, DNK, ISL empty).
10. data_variants:121 five bounds (HUN missing); notes/ pointers unreadable from the note.
11. num_ee:101-108 Brent on (1e-6, min(0.75, 0.99 Gs_cap)), not golden-section with (0, 0.75).
12. num_ee:93 "repeated from the model section" false. 13. Code cites alg:fast/alg:gridsearch (informalAnalytical
   policy.py:89,96, model.py:599) -> alg:LOG:fast/alg:LOG:gridsearch (fix in code).
14. main.tex:4-8 \title duplicated. 15. main.tex abstract: "no cross-references" false (informalAnalytical points to
   the paper), the data part unmentioned, X undefined, garbled last sentence; proposed abstract in the report.
16. Edit artefacts: model_competitiveequilibrium:164-165, model_PEE:62, num_ee:84.
**Cuts**
17-19. num_robustroot:35,53,55,57,63 history, dated runs (~350 words). 20. num_peeCRRA:46 footnote (overflow trap).
21-22. num_peeCRRA:62,67-71,73,76 bookkeeping (~250 words). 23. model_calibration:30-41 normalisations (~230 words).
24. model_calibration:77-81 = num_calibration:55-59 (K/Y): once. 25. model_competitiveequilibrium:191-192 duplicate.
26. num.tex:7-13 preamble. 27. num_peeLOG:128 boundary paragraph. 28-30. data_figures:131,139,147, data_variants:121,
   data_tiers:68,74 country-by-country values the csv and figures carry (~500 words). 31-32. data_inputs:2 circular
   row reference; data_variants:82,111 repeated reason for C. 34. model_PEE:9,41,59 "see the main paper" asides.
