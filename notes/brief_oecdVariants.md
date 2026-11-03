# Brief: two more readings of the cross-section on θ variant C (2026-11-02)

RKB's decisions of 2026-11-02: the paper's cross-section is θ variant C, provisionally at each country's own turnout
(`cses`). Before settling, two more readings are tested. **Exploration only**: no paper output, no file in
`writing/`, and nothing in `results/oecd26/` changes. Model: `python/US/runOECD26.py`, `python/US/oecd26.py`.

## The two readings

**1. A common ω at the sample mean (layer 1).** Today layer 1 puts every country at the U.S. anchor's ω. New key
`omegaRule`: `'anchor'` (today's layer 1, the default; rows written before the column read as `'anchor'` through
`LEGACY`) or `'mean'`: every country at ω̄ = the arithmetic mean of the layer-2 ω's at the same turnout, spec,
betaRule and θ variant (status ok, the run's countries). β and the cost parameter stay the anchor's: recalibrating
ε at ω̄ would fit it to a U.S. that spends more than the U.S. Expected: C/cses ω̄ = 1.306 over 20 countries
(median 1.248, to report, not to run). From the layer-1/layer-2 differences it should raise predicted θ by about
0.02 and spending by about 0.7 p.p. everywhere; a run far from that needs a look.

**2. A stylized turnout, `'pooled'`.** In the CSES the U.S. is the one outlier in the income gradient of turnout
(top-to-bottom ratio 1.34; 1.64 in the CPS), every other country in C's sample lies at 1.02 to 1.15, and Belgium,
with compulsory voting, at 1.08. Rule for country c (`mu1_usPct`..`mu3_usPct` of `data/oecd29.csv`):
- **USA**: its own CSES profile, as under `'cses'`. One survey for all countries; the anchor's inputs are then the
  `cses` anchor's, and it must reproduce the C/cses anchor (ω 1.257177, p 13.085633): reuse or recompute and compare.
- **Enforced compulsory voting around 2020**: AUS, BEL, LUX (TUR is outside every sample): flat, μ = (1, 1, 1).
  A constant in `oecd26.py` citing International IDEA's compulsory voting database. Greece's compulsory voting is
  not enforced: voluntary.
- **Every other country**: the mean of μ_c/μ_c,1 over the voluntary non-U.S. countries of the run's sample that have
  CSES turnout (on C's sample 18: the 20 with CSES less USA and BEL), about (1, 1.05, 1.08). Luxembourg, which has
  no CSES, enters under this reading (21 countries).

Only the ratios of μ across groups should matter (μ_j multiplies retirees and workers alike in W_t,
`writing/Paper/Sections/Model.tex`:128). Verify on one country that μ and 0.9μ give the same row to solver tolerance
before relying on it.

## Runs (θ variant C at the main run's inputs; spec sizePiR, betaRule common, ρ = 1, C's in-sample countries)
Into a new outdir `results/oecd26_explore/`, which `build.py` does not read. β and the anchor's ω seed as in the main
C run (`results/calibration/US_rhoGridCommonX.csv`); do not recompute rows already on disk at the same inputsKey
(copy or read the C/cses anchor and layer-2 rows of `results/oecd26/` as needed).
- **R1** `cses`, layer 1 at ω̄ (20 countries).
- **R2** `pooled`: anchor, layer 1 at the anchor's ω, layer 2 (21 countries).
- **R3** `pooled`, layer 1 at ω̄ of R2's layer 2.

The main C run took about 18 min per layer 1 and 24 min per layer 2 (`time` in `results/oecd26/`), so about 1.5 h
in all. Run detached, script and log in `logs/`.

## Comparison
Extend `logs/variantCompare/compare.py` (gitignored, reads `results/` only) with R1-R3 beside C/cps and C/cses:
the five slopes (data, layer 1, layer 2) and the fit metrics it already computes, plus the mean θ of model and data,
the slope of predicted θ on observed θ (the compression), and for R1 and R3 mean spending of model and data. Write
`logs/variantCompare/summary_2026-11.md` beside `summary.md`; keep the self-check (paper outputs bit for bit).

## Checks
- `runOECD26.py`'s defaults give the inputsKeys on disk (no row of `results/oecd26/` would rerun); `build.py`'s
  outputs unchanged (compare.py's self-check); `python/paper/test_oecd26.py` and `python/runTests.py` pass.
- The pooled anchor equals the cses anchor; R1's ω̄ = 1.306; every row status ok with nEqMax = 1.

## Report
The table of slopes and fit metrics for C/cps, C/cses, R1, R2, R3 with a few sentences reading it; the code
changes; an entry in `python/US/RESEARCH_LOG.md` (at most 10 lines) and the new options in `python/US/README.md`.
No commit.
