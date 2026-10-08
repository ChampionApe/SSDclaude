# Research log — US

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_US.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-08 — runs of the cost variants (brief `notes/brief_escVariants_runs_2026-10-08.md`, logs `logs/escVariants/`)
- Self-check `--spec size --stage calib --tag _selfcheck` reproduced λ = 8.64320735564998 and the `none` row bitwise. After the runs every committed row of `results/esc/` is unchanged (`compareResults.py --only esc`: 0); read with `float_precision='round_trip'` the merge's read-write cycle moves old cells by ≤1 ulp in the text, which pandas' default parser (the pipeline's) does not see.
- `'sizeL'` λ = 1.7098, one sign change in (1.16, 2.16), corner to corner (knife-edge); the UK chooses 0 under it, its own λ 2.414; France's threshold 1.312; the path is at 1 from 2050.
- `'sizeLQ'` pinned on the UK: κ = 0.1287, λ = 5.2366 (κ scan: one sign change in (0, 0.25)); France predicted 0.806; the UK's own λ − λ_US = 2e-6. Near the root the UK design is steep and uneven in κ (0.567 at 0.125, 0.554 at 0.134): the precision item TODO C11 sets κ to about ±0.005.
- `_kappaFR` (France pins κ): κ = 0.629, λ = 2.068, the UK predicted 0.397; France jumps from 0.995 to the corner between κ 0.628 and 0.629.
- `'sizeLQV'` run at κ_Ṽ = κ·M_US/Ṽ_US = 0.1698, not the brief's literal κ (M units), so the U.S. cost is the same function: λ = 5.2366 again; the UK chooses 0.566, France 0.749.
- Steps b, c and e split by spec or stage to run in parallel on disjoint csvs. Every new row: one equilibrium, no fallback.

## 2026-10-08 — cost variants 'sizeL', 'sizeLQ', 'sizeLQV' (briefs `notes/brief_escVariants_code{,2}_2026-10-08.md`)
- `base`: `Mabs` (M = Σγ\|y−1\|, masked, memoised as `Vtilde`); `fWedge`/`dlnfWedge_dτ`: `'sizeL'` on M, `'sizeLQ'` M on the linear term and Ṽ on the quadratic, `'sizeLQV'` Ṽ on both (κ in `db['wedgeKappa']`, its term a separate summand so κ = 0 is `'size'` bitwise). The second pass moved the linear weight from Ṽ to M at gate 1 (`notes/esc_variants.md`, Overturned 2, §1.4). `'size'` untouched: `test_esc.py`'s size lines identical.
- `modelESC`: specs, brackets, `KAPPA_SPECS`, `kappa` through the wedge dict/`setWedge`/`calibrateWedge`; `calibrateWedgeCorner` (threshold kind: scan, then bisection in log λ). A refinement after the scan now restores the bracket's left node's warm starts (`_warmStart`: `x0`, `LOG.x0`, `CRRA.x0`): under M the 'sizeL' bracket lies far below the scan's last node, the first attempt fails and leaves `LOG.x0` poisoned (`calibrateWedge` retries only on an exception, so 'size' is unchanged).
- `runESC`: `--kappa`, `--pinKappa`, `calibrateJoint` (outer `kappaRoot`; inner λ bracket narrowed from the neighbouring κ), France's threshold row, columns `kappa`/`kappaFrom`/`θPin`/`ownKind`/`Mabs`; the permanent stage refuses the new specs. `runESCcrra` accepts them (κ from the LOG row, not run); `collectESCexperiments` carries `kappa`.
- `test_escVariants.py` (new fast suite): test model M = 0.5746, Ṽ = 0.4357; 'sizeL' threshold λ = 1.948 (2.566 under Ṽ); (β, ω) do not calibrate at λ = 50 and λ = 0.5 is the θ = 0 corner, so check 7 brackets with 1.5 and 8; `calibrateJoint` is tested on stubs.
- Smoke runs (real model, `--spec sizeL --commonX --stage calib`, csvs deleted): λ = 2.2550 under Ṽ; under M λ = 1.7098 (= 2.2550·Ṽ/M, the same f), one sign change in (1.16, 2.16) between the two corners, reached only after the warm-start retry; the λ = 50 node fails to calibrate (a NaN scan node).
