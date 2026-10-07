# TODO

The one open list. Closed work is not kept here: it is in the session logs and, by theme, in
`archive/INDEX.md`. `notes/paper_styleGuide.md` is the register every new paragraph follows.

Items are labelled so they can cite each other: `C` code, `R` compute runs, `W` writing, `D` data. The labels
used up to 2026-10-07 (C1–C8, R1–R5, W1–W8, D1, P1–P2) are taken, and code and the archived logs still cite
some of them; new items continue the numbering.

## Plan in progress

**C9. Two `informalAnalytical` fast suites fail since C8.** `test_cacheParams.py` and `test_crraBackward.py`
stop at `LOG.solveVectorized did not converge: max|residual|=1.498e-08 > tol=1.0e-08` (scipy reports success).
They pass (33 of 33 for the first) at the parent of `8e85632` and fail from it on: the shared workbook's γ₀ =
0.4706 and the first-quartile ε moved the quick-test model's LOG solve just past its tolerance. No table or
figure reads this module, but section 3's propositions, the technical note's first chapter and section 5's
footnote ("the tax also rises when informal households are hand-to-mouth", last computed before C8's inputs)
rest on it. Decide between the tolerance and the test model's inputs, recheck that footnote, then rerun
`python\runTests.py` (22 of 24 pass on 2026-10-07).

## Data tasks

**D2. Figure 5.1's data outside the pipeline.** `writing/Paper/Figs/coverageArg.eps` (beneficiaries of the
national pension system and of non-contributive old-age pensions) is drawn from Cetrángolo and Grushka (2020),
table 6; neither the data nor the script is in the repository. Add `data/argentinaCoverage.csv` with a row in
`data/README.md` and a builder in `python/paper` (`REPLICATION.md` §5 lists it).
