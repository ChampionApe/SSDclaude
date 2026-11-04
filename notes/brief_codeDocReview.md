# Brief: review of the code and of the technical documentation (2026-11-04)

RKB's two tasks: (1) the code: bugs, problems, and what to clean up after months of gradual change to the models; (2)
the technical documentation (`writing/main.tex` and the model folders): errors, consistency with the code, and a
register that is technical but not overly so and does not restate what reading the code makes evident. Run both
economically.

## Size
- Code: 33k lines of Python without tests (`python/US` 12.2k, `python/paper` 12.0k, `python/InformalSavings` 5.5k,
  `python/informalAnalytical` 2.3k, `python/gridsearch` 1.2k), and 8.9k lines of tests. The paper's pipeline imports
  InformalSavings, US and gridsearch, not informalAnalytical (the analytical model of the note; light pass).
- The note: 55k words in 48 files (`writing/US` 25k, `writing/informalSavings` 18k, `writing/informalAnalytical` 10k,
  `writing/data` 2k).

## Order and steps
Code first, then the note, so that the note is checked against the code as fixed.

0. **Pre-pass (lead session, no agents).** Baseline: the fast suites (`python/runTests.py`, 30/30 on 2026-11-04) and
   a build-identity snapshot of `results/paper`. Static scan with `ast` (no lint tool is installed): definitions
   never referenced, modules no stage, test or other module calls, imports unused, stale references to retired
   outputs, config keys, results folders and notes (`archive/INDEX.md` lists what retired), TODO/FIXME. Output: a lead
   list per module for the reviewers.
1. **Code review: four read-only agents in parallel**, one module each, each report at most 25 findings ranked bug,
   then risk, then cleanup, each with file:line, the evidence and a proposed fix; no edits.
   - R1 `python/US` model core (`base`, `model`, `policy`, `modelESC`, `policyESC`, `shocks`): Opus (numerics).
   - R2 `python/US` drivers (`runESC*`, `runOECD26`, `oecd26`, `testEU`, the calibration and shock drivers,
     `c5Numbers`, `runTauTheta`, `runHorizon`): Sonnet.
   - R3 `python/paper` (config, readers, builders, `build`, `onlineAppendix`, `siteData`, the stage drivers, the data
     builders): Sonnet.
   - R4 `python/InformalSavings` and `python/gridsearch`, `python/informalAnalytical` lightly: Opus for
     InformalSavings's solver, Sonnet otherwise.
2. **Triage and fixes (lead).** Verify every claimed bug before acting: an agent's finding can be wrong. Fix in one
   pass per module (`model-coder` for model code), each with its test; then the fast suites and the build-identity
   check: every paper output byte-identical (PDF dates aside) unless a fix is meant to move a number, and every moved
   number listed for RKB. Cleanups that change no output go in the same pass; anything that would change a result
   goes to RKB first.
3. **Documentation review: three read-only agents**, after step 2, each against its code: D1 `writing/US` against
   `python/US` (Opus for the derivations in `model_*.tex`), D2 `writing/informalSavings` against
   `python/InformalSavings`, D3 `writing/informalAnalytical` and `writing/data`. Each reports errors (math, notation,
   claims the code contradicts), inconsistencies with the code, and passages to cut or shorten (over-technical, or
   restating the code), as a list of proposed edits with file:line.
4. **Edits.** RKB approves the cuts; one writer per folder applies them; `writing/main.tex` compiles; the note's
   Overleaf project is pushed on RKB's go (`writing/overleaf.py push note`).

## Economy
Seven agents in all, read-only and with capped reports; Opus only where math or numerics are the object; nothing is
re-solved (the fast suites and the build-identity check stand in); the lead verifies findings instead of re-reading
whole modules. Best run from a fresh session: its context starts small, so every step costs less.
