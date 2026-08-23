# Research log — `paper`

Session log for the paper pipeline. For the models it reads from, see
`python/<module>/RESEARCH_LOG.md`; for repo-structural work, the root `RESEARCH_LOG.md`.

## 2026-08-21 — the pipeline created
Creating this folder was itself structural work — a fifth `python/` folder, the first that is neither a
model nor a numerical package — so **that session is logged in the root `RESEARCH_LOG.md`**, not here.
It covers the three-stage design and why stage (iii) imports no model code, the workweek normalisation
that had been mistaken for a result, the two-route cross-check on the seed savings level (and the numpy-2
serialisation bug it caught), and the untracked-`writing/Paper` backup rule.

Entries below this point should be paper-pipeline-specific: a new output wired, a builder's formatting
convention, a change to what `config.ARG` declares.

## 2026-08-21 (cont'd) — refining the two Argentina figures

Both figures were rebuilt against what the paper actually needs to show. Model-side work (the new grid
experiment) is in `python/InformalSavings/RESEARCH_LOG.md`.

**`ARG_CRRA_LOG`: long run t0+3 → t0+1 (2100 → 2040), for legibility.** The guard against landing on or
past the terminal period is unchanged and still the binding constraint; only the default moved. Three
panels improved. **The savings-rate panel is the price**: the two series converge and cross near `ρ≈0.9`,
largest gap 0.024 p.p. on an axis spanning 0.19 p.p. The crossing is real — the savings-rate effect is
essentially at its long-run value by 2040 — but the panel no longer carries a short/long contrast, and
that is a presentation cost accepted knowingly rather than a defect. Recorded in `README.md` so the next
reader does not "fix" it.

**`ARG_LOG_FourInOne`: from a cross to a surface.** It plotted two slices through the calibrated point —
`ε` at calibrated `θ`, `θ` at calibrated `ε` — on one shared x-axis, which forced two disjoint domains
(`ε ∈ [0.02, 0.65]`, `θ ∈ [0.5, 1]`) onto one axis labelled "parameter value". Now: x is `ε`, one curve
per `θ`, the span between adjacent curves shaded, `θ` on a colourbar. The band's **width** at a given `ε`
is how much `θ` matters there, which is a statement the cross could not make at all.

*Two conventions this established, both now in `README.md`:*

- **A continuous parameter does not get the categorical pair.** `THETA_RAMP` is one hue light→dark. Its
  middle step is deliberately the existing categorical blue, so a shaded figure and a two-series figure
  read as one family rather than as two design systems; its lightest step is the ordinal contrast floor
  against a light surface, so the palest curve survives print.
- **The calibrated `θ` is drawn in ink, not as a further value of the ramp** — it is an annotation, and
  giving it a hue would send the reader to the colourbar to find it. It needs a surface-coloured halo:
  the calibrated `θ` sits in the ramp's *dark* end on three of the four panels, and bare ink on navy is
  unreadable in print. Pre- and post-reform are distinguished by marker **shape**, not by a second ink,
  so the pair survives greyscale.

**A loader that must reject a shape, not just a missing file.** `datasets.epsThetaGrid` raises unless the
csv is a complete rectangle. The figure pivots it and fills between adjacent `θ` columns, and a missing
pair becomes a NaN that `fill_between` drops **silently** — so with a resumable producer upstream, a
half-finished sweep would have rendered as a figure with holes instead of as a skipped output. Same
principle as the rest of stage (iii): an experiment that has not finished must not be able to look like
one that has, and here "has not finished" is a property of the file's shape rather than its existence.

**The cross sweep removed rather than kept as a witness.** Once the grid superseded it, the old
`epsTheta_rho1.0000.csv` had one remaining use: its rows agreed with the grid's to ~1e-16 along both
calibrated lines, which was evidence that two independently written parameter-installation paths agreed.
Tempting to keep for that reason. The user's call was to delete it, and it is the right one — a
superseded file kept beside a live one for a reason that is *not* the pipeline's own use is exactly the
shape of `notes/crossCuttingFindings.md` #8, and the check had already paid out. What it verified is
recorded here; the file is gone.

*Also fixed, pre-existing:* `runShocks.py --dry` printed `GRIDFLAGS`, which carries the Greek `--nι`, and
died on redirected cp1252 stdout. The repo's documented trap, in one of the few files written before
`gridsearch.testing` existed to prevent it.

## 2026-08-22 — the second arm: US / France / UK

The pipeline now has **two model arms** sharing `config.py`, `results/` and one stage (iii). New:
`runCalibrationUS.py`, `runShocksUS.py`, `tablesUS.py`, `figuresUS.py`, a `US` spec plus `usCalendar()`
in `config.py`, US loaders in `datasets.py`, and 12 entries in `build.py`'s registry. **17 outputs build
in ~5 s.**

**Why separate stage (i)/(ii) entry points rather than a `--model` flag.** The two arms delegate to
different experiment scripts with different CLIs, and the declarations are the point of those files — a
single entry point would have to carry both flag vocabularies and would make it harder, not easier, to
read off what the paper's numbers were produced at. Stage (iii) is shared because it is model-agnostic
by construction: it reads csv and writes tex.

**Stage (i) is order-dependent here, and is not in the Argentina arm.** France and the UK impose the US
`β` at the same ρ, read out of `US_rhoGrid.csv`, which `USReference` matches exactly and refuses to
interpolate. So the US sweep must be complete over the whole grid before any European sweep starts.
`runCalibrationUS.py` enforces that rather than relying on loop order — a partial US sweep would
otherwise fail one point at a time in the middle of a march, which is the expensive way to find out.

**The contracts were verified, not assumed.** Stages (i)/(ii) skip everything already done; stage (iii)
is idempotent and does *not* re-back-up on a second run; and with `US_shocks.csv` removed, the seven
shock-derived outputs report `BLOCKED` and write nothing while the four calibration-derived ones stay
`OK`. Ten hand-written US/FR/UK tex files were preserved to `results/paper/superseded/` before takeover.

**Two conventions the builders must not re-apply.** The US shock csv already carries `sr` as `s/(w·h)`
(the paper's savings rate, which is `Base.savingsRate`'s `s/Y` divided by `(1-α)`) and `workweek` already
in hours, normalised inside the experiment script against *that ρ's own* baseline. Re-deriving the
workweek in stage (iii) from `h̄` would be wrong twice over — `h̄` has no identified level under vector
`X`, and each ρ needs its own reference. This is the Argentina arm's `workweekHours` trap, one layer
earlier, and it is why the loaders hand the column through untouched.

**The common-`X` shock run is a check as much as an output.** θ, ageing and voting must come back
*identical* to the vector-`X` run — none touches `η` or `X`, and `β`/`ω`/`h` agree across variants —
while income distribution and leisure must differ, since those two are *defined* through `η` and `X`.
Measured: ≤ 4e-15 in τ and sr for the first group; up to 7.9e-3 in τ and 1.48 hours for the second. A
common-`X` run that matched on all seven would mean the variant was not being applied.

**One bug worth naming.** `config.pct` escapes the percent sign for tex, so putting it in a matplotlib
legend rendered a literal backslash (`14.4\%`). Caught in `US_taxOverview`. Anything drawn *into* a
figure needs plain formatting; `config.pct` is for tex cells only.

### Open
- `writing/Paper/Appendix/EndogenousSystemCharacteristics.tex` — the `US_ESC_*` tables need endogenous
  `θ`, which the model does not implement yet. The only US/FR/UK paper outputs still unwired.
- The workweek column differs from the hand-written tables on full-effect rows (0.4–2.5%) while τ and the
  savings rate match exactly. Since τ and sr are hours-unit-invariant, the gap is in the conversion rather
  than the equilibrium; unattributed. See `python/US/RESEARCH_LOG.md`.
