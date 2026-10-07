# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

**C9. Two `informalAnalytical` fast suites fail since C8.** `test_cacheParams.py` and `test_crraBackward.py`
stop at `LOG.solveVectorized did not converge: max|residual|=1.498e-08 > tol=1.0e-08` (scipy reports success);
they pass at the parent of `8e85632`. Diagnosed 2026-10-07 in the scratchpad, nothing changed: `optimize.root`
(`hybr`) stops on its own step tolerance (`xtol` 1.49e-8) while `model._checkConverged` gates max|z| at 1e-8, and
C8's inputs (γ₀ = 0.4706, first-quartile ε) put the quick-test model's solve just over the gate. A restart from
the solution reaches 8.9e-16 and `xtol` 1e-12 reaches 6.9e-13, τ moving by 1.2e-9 either way; `solveRobust`
already recovers through its grid fallback, so only the suites that call the vectorized solver directly fail.
Section 5's footnote holds on the current inputs: the hand-to-mouth model calibrated at ρ = 1 (β 0.671, ω 1.491),
the reform (ε 0.210 → 0.547 from 2010, rule 'match' against the first quartile, κ refreshed) raises the 2010 tax
from 10.92% to 16.38%. To close, in `python/informalAnalytical/` only, no paper or `results/` file:
(1) `policy.py`, `LOG.solveVectorized`: restart `optimize.root` once from `res.x` when the gate fails
(recommended: every solve that meets the gate today stays bitwise unchanged) or default `xtol` to 1e-12;
(2) `test_calibration.py` (slow suite): pin the footnote, the reform raising the 2010 tax on the calibrated
model; (3) `model.py`, `getEps`'s docstring: "appendix D" is now E (the same line in `InformalSavings/model.py`
is optional); (4) the module's `README.md` and `RESEARCH_LOG.md`, and this item. Checks: `python\runTests.py -k
informalAnalytical`, then `--slow -k informalAnalytical`. `US/policy.py`'s `solveVectorized` has the same
default and passes; changing it would move the published LOG csvs at ~1e-9, so it stays.

## Data tasks

**D2. Figure 5.1's data outside the pipeline.** `writing/Paper/Figs/coverageArg.eps` (beneficiaries of the
national pension system and of non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020),
table 6; neither the data nor the script is in the repository. Add `data/argentinaCoverage.csv` with a row in
`data/README.md` and a builder in `python/paper` (`REPLICATION.md` §5 lists it).
