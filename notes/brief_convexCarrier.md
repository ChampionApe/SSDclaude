# Brief: the τ² cost's cross-country carrier π(1−π) (worktree `..\SSDclaude-tauPower`, branch `exp/tauPower`)

RKB, 2026-11-07: run the test of the τ² microfoundation. Ours (`notes/tauPower_microfoundation.md`, candidate A, test
spec (19) in §7) and the coauthor's (`quadratic_cost.pdf`, repo root, untracked) are the same model: a share of revenue
lost ln f = −½ λ τ² Ṽ (1−θ)², with λ = 2κ π(1−π), π = Π/R, κ the slope of the elasticity in the wedge (ε(T) = κT).
The branch runs k = 2 with the k = 1 carrier ('sizePiR': λ_{n,t} = ε π_{n,t}). This run replaces that carrier by
λ_{n,t} = 2κ π_{n,t}(1−π_{n,t}) and reruns what the carrier changes. Main is not touched.

## The specification
- f = exp(−κ π_t(1−π_t) τ_t^k Ṽ (1−θ_t)²), k = 2 (SSD_TAUPOWER, the branch default); the p slot holds κ.
  ∂_τ ln f = −κ π(1−π) k τ^{k−1} Ṽ (1−θ)², π taken as given (as under 'sizePiR').
- π_t = Π_t/R_t exactly as 'sizePiR' dates and solves it: lag '[t-1]' π_t, lag '' π_{t+1}; the same fixed point
  (`ModelESC._ΠRFixedPoint`, `_ΠRstart`, calibrate's outer loop). Stationary uniform wedge (u = 1 − π), no cubic
  term, no size loss: the coauthor's choices, which settle §9.2 of the note.
- Expected κ at the anchor (LOG, k = 2): λ_US/(2·0.247) ≈ 84 (λ_US = 41.45, the branch's 'sizePiR' ε = 74.6). Check the
  'sizePiR' brackets (`modelESC`, `runESCcrra`, both × TAU_SCALE) contain it.
- The U.S. sections keep the constant λ ('size'): their results on the branch stand and are not rerun.

## Implementation (suggested; your call if the code argues otherwise)
- Mirror `SSD_TAUPOWER`: an env flag `SSD_CARRIER` (`convex` the branch default, `pi` the current carrier) read in
  `modelESC.py` (into db, e.g. `wedgeCarrier`) and `python/paper/config.py` (labels), used only where `Base.fWedge` and
  `Base.dlnfWedge_dτ` multiply λ by `wedgeΠR`: g(π) = π under `pi`, 2π(1−π) under `convex`. Every other 'sizePiR'
  code path (fixed point, calibration, transport to countries, csv columns `ΠR`) stays as it is.
- If the drivers' recorded settings (the 2026-11-04 settings-aware staleness) do not see the carrier, move the outputs
  the rerun must replace to `logs/convexCarrier_2026-11-07/before/` first, so the drivers rerun them; that copy is also
  the comparison against the Π/R carrier.
- Builders: the wording that prints "λ_n = ε Π_n/R_n" and the ε symbol (`tablesOECD26.py` SPEC/COSTSYMBOL/notes,
  `tablesOA.py`, `tablesUS.py`, `datasets.py`) prints "λ_{n,t} = 2κ π_{n,t}(1−π_{n,t})" and κ under `convex`.
- Tests: `pi` at k = 1 bitwise as main (`test_esc.py`, `test_oecd26.py`, `test_coreGuards.py`); under `convex` fWedge
  equals the formula at a given π and dlnfWedge_dτ a finite difference; the fast suites pass.

## The run (environment as `logs/tauPower_2026-11-06/run.sh`: PYTHONUTF8=1, SSD_TAUPOWER=2, `.venv/Scripts/python.exe`)
Rerun everything that reads the 'sizePiR' cost and nothing else; find the list from the code (grep `sizePiR`), at least:
stage (i) the LOG 'sizePiR' U.S. calibration; stage (ii) `costVariants` (the site's Π-inclusive cost, baseline and acute),
`oecd26` and `oecd26Variants` (about 2½ h last time); `c5Numbers.py` commands that read the 'sizePiR' rows; then
`build.py`, `--site`, `--map`, `quarto render` and latexmk of the paper, all in the worktree. A detached script with a
status log as on 2026-11-06 (`logs/convexCarrier_2026-11-07/`); watch it with Monitor.

## Constraints
- Worktree only. No commits, no push, no `quarto publish`, no `writing/overleaf.py`. Main's checkout is not touched
  (it is being committed and published meanwhile; the `.venv` junction is shared: install nothing).
- writing/Paper only through `build.py`. Paper prose is not edited.
- Update the worktree's `notes/tauPower_k2.md` (a short section) and its `python/US/RESEARCH_LOG.md` (≤ 10 lines).

## Report (numbers, against the branch's Π/R-carrier run and main's τ¹ where they exist)
1. κ at the anchor and λ_{US,2020}; λ_{n,2020} across the sample (min, max; expected within 2.5% of the U.S.).
2. The cross-section's fit, the model and own ω: sd, corr, RMSE (Π/R carrier: 0.202, 0.750, 0.218; own ω 0.242,
   0.796, 0.196).
3. Table 5's slopes (Π/R carrier: spending on the index 33.09/33.95, the index on growth −0.43/−0.37) and the countries
   whose predicted design moves most (the note expects Italy, Greece, Hungary, Czechia up by up to 0.1).
4. The Π-inclusive cost's U.S. numbers (`costVariants`) and the C5 entries that moved.
5. What failed or was skipped, and every file changed under python/.
