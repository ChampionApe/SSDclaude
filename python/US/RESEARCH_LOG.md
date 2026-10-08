# Research log — US

Entries to 2026-10-07 are in `archive/sessionLogs/RESEARCH_LOG_US.md` (oldest first), indexed in
`archive/INDEX.md`. Format: one entry per session, at most ~10 lines: what changed, why, where to
look. A lesson that would recur goes to `notes/crossCuttingFindings.md` once, cited by number, not here.

## 2026-10-08 — cost variants 'sizeL', 'sizeLQ', 'sizeLQV' (briefs `notes/brief_escVariants_code{,2}_2026-10-08.md`)
- `base`: `Mabs` (M = Σγ\|y−1\|, masked, memoised as `Vtilde`); `fWedge`/`dlnfWedge_dτ`: `'sizeL'` on M, `'sizeLQ'` M on the linear term and Ṽ on the quadratic, `'sizeLQV'` Ṽ on both (κ in `db['wedgeKappa']`, its term a separate summand so κ = 0 is `'size'` bitwise). The second pass moved the linear weight from Ṽ to M at gate 1 (`notes/esc_variants.md`, Overturned 2, §1.4). `'size'` untouched: `test_esc.py`'s size lines identical.
- `modelESC`: specs, brackets, `KAPPA_SPECS`, `kappa` through the wedge dict/`setWedge`/`calibrateWedge`; `calibrateWedgeCorner` (threshold kind: scan, then bisection in log λ). A refinement after the scan now restores the bracket's left node's warm starts (`_warmStart`: `x0`, `LOG.x0`, `CRRA.x0`): under M the 'sizeL' bracket lies far below the scan's last node, the first attempt fails and leaves `LOG.x0` poisoned (`calibrateWedge` retries only on an exception, so 'size' is unchanged).
- `runESC`: `--kappa`, `--pinKappa`, `calibrateJoint` (outer `kappaRoot`; inner λ bracket narrowed from the neighbouring κ), France's threshold row, columns `kappa`/`kappaFrom`/`θPin`/`ownKind`/`Mabs`; the permanent stage refuses the new specs. `runESCcrra` accepts them (κ from the LOG row, not run); `collectESCexperiments` carries `kappa`.
- `test_escVariants.py` (new fast suite): test model M = 0.5746, Ṽ = 0.4357; 'sizeL' threshold λ = 1.948 (2.566 under Ṽ); (β, ω) do not calibrate at λ = 50 and λ = 0.5 is the θ = 0 corner, so check 7 brackets with 1.5 and 8; `calibrateJoint` is tested on stubs.
- Smoke runs (real model, `--spec sizeL --commonX --stage calib`, csvs deleted): λ = 2.2550 under Ṽ; under M λ = 1.7098 (= 2.2550·Ṽ/M, the same f), one sign change in (1.16, 2.16) between the two corners, reached only after the warm-start retry; the λ = 50 node fails to calibrate (a NaN scan node).
