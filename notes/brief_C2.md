# Brief C2: Argentina's model fixes (#4, #3, A7's switch)

Package C2, code part, of `notes/plan_reviewResponse.md` (W16). Agent: model-coder. Branch `review-2026-10`.
The runs (stage (i), about 3.2 h, and stage (ii)), A12, #19, W15 and #2 follow with paper-compute; this
brief is the code only. Read the review's detailed comments 3 and 4 and overall comment O4
(`coarse-output/coarse_review_22102026.md`, lines 148-181 and 39-42), and `notes/paper_reviewResponse.md`
(A7, comments 3 and 4).

## 1. #4: the savings distribution at the date of the surprise reform (a bug; fix and test)

The reform (`python/InformalSavings/shockUniversal.py`) re-solves the politico-economic equilibrium on the
copy built by `createCopyFromt0` (`model.py`), seeded with the state `(s_{t0-1}, ι_{t0-1})` read off the
baseline path. In the copy's first period the generation old at t0 enters with savings shares
(`si_s`, `Γs` at vintage `tLag`; `policy.py`, `stateGrid_t`/`stateGrid_T`, `objectiveFrozen`, the line
`tLag = tIdx[pos - 1] if pos > 0 else self.B.tFirst`) that are rebuilt from the copy's own parameters,
i.e. under the NEW ε, although these retirees saved under the old one. Their shares, in particular
`ι_{t0-1} = s_{t0-1,0}/s_{t0-1}` and the formal shares `s_{t0-1,i}/s_{t0-1}`, are predetermined at their
pre-reform values. Fix: in the reform period, the old generation's shares and every vintage-`t0-1` object
of the copy are those of the baseline (old ε, and whatever else the baseline used at t0-1); the consistency
step with the new system applies from t0+1 on. Check first exactly which objects at vintage t0-1 depend on
ε (κ, Γs, si_s, ι; README "Known limitations" and the `installEps` notes in `shockUniversal.py` name the
ones already handled) and whether `ι_{t0-1}` itself is already taken from the baseline path, so that the fix
is only what is wrong. Under CRRA the same holds for `s_{t-1}`'s distribution.

Test (`test_createCopyFromt0.py` or a new `test_reformVintage.py`): the copy's vintage-t0-1 shares equal the
baseline path's at t0-1 to machine precision when ε changes, and the test fails on the unchanged code.
Reference: the 2010 tax response of the headline reform (`rule='match'`, `refType=1`) at ρ = 1, common X,
before and after the fix (it is expected to move; report both, and the 2010 savings rate).

## 2. #3: one GDP concept in the spending target and in the outcome

Today `db['τ0'] = spending/(1-α)` with spending = 0.071 of GDP (`test.py`, workbook `data/ArgentinaTest.xlsx`),
and the paper converts the model's tax response back to GDP with the same `(1-α)`. Both steps treat GDP as
formal output, while appendix E.3 argues that measured GDP includes informal mixed income (which is how the
paper justifies α = 0.35). First establish, from `writing/informalSavings/` and the code, what output and
GDP are in the model (does the informal type produce? how is the savings rate "relative to GDP" in table 2
computed, `datasets`/`shockUniversal` readouts?). Then make one concept consistent across the target, the
calibrated ω and every reported "% of GDP" or "relative to GDP" number: GDP = formal output plus the informal
type's output where the model has it, with the informal share `y` the model's own at the calibration if
that is computable inside the calibration loop, else a named parameter `y` in the workbook/db (not a
literal), set to the model's informal share at the current calibration and documented. Report: the concept
chosen and why, `y`, the new τ target (the review's arithmetic: 0.071/(0.65(1-y))), and which readouts
change. Do NOT rerun the calibration; a single-ρ check of the target computation is enough. If the model has
no informal output in GDP at all and the right concept is unclear, stop after the investigation and report
the options instead of choosing.

## 3. A7: the switches for the reform's variants

- A pre-reform ε = 0 calibration variant: γ₀ then counts the elderly without a pension. A switch on the
  model (a constructor or db argument, and a `--epsPre0` flag on `calibrateRhoGrid.py` and
  `shockUniversal.py` with its own csv and instance names, as `commonX` does), not a code fork.
- Table 2's formal benefits: the shock csv rows carry the change in formal benefits (`b_t^i`, per type and
  the average formal pension) in 2010, so that the table can report it (+3.4% in 2010 in the review's check).
  Add the readout columns in `shockUniversal.py`; the table builder is not yours.

## Files

May touch: `python/InformalSavings/*.py` (model, base, policy, shockUniversal, calibrateRhoGrid, test.py,
tests), `python/runTests.py` to register fast tests, `python/InformalSavings/RESEARCH_LOG.md`, its `README.md`.
Not `python/US`, `python/paper`, `python/gridsearch`, `data/` (the workbook: if #3 needs a workbook cell,
report the cell and its formula; workbooks are edited in Excel only, plan principle 4), `results/`, `writing/`.

## Done when

The fast suites pass (`python\runTests.py`), the module's PEE suites pass (`test_peeLOG.py`, `test_peeCRRA.py`,
`test_peePath.py`, `test_createCopyFromt0.py`), the new tests fail without the change and pass with it, and the
report gives the reference numbers before and after, #3's investigation and decision, and the exact commands
paper-compute will run for stage (i)/(ii) and the ε = 0 variant.
