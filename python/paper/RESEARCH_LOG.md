# Research log — `paper`

Session log for the paper pipeline. Current behaviour and its traps are in this folder's `README.md`; for
the models it reads from, see `python/<module>/RESEARCH_LOG.md`; for repo-structural work, the root log.

## 2026-08-21 — the pipeline created

Creating this folder was itself structural work — a fifth `python/` folder, the first that is neither a
model nor a numerical package — so **that session is logged in the root `RESEARCH_LOG.md`**. It covers the
three-stage design and why stage (iii) imports no model code, the workweek normalisation that had been
mistaken for a result, the two-route cross-check on the seed savings level and the numpy-2 serialisation
bug it caught.

Entries below should be pipeline-specific: a new output wired, a builder's formatting convention, a change
to what `config` declares.

## 2026-08-21 (cont'd) — refining the two Argentina figures

**`ARG_CRRA_LOG`: long run t0+3 → t0+1, for legibility.** Three panels improved; **the savings-rate panel
is the price**, since the two series converge and cross near ρ≈0.9. The crossing is real — the savings-rate
effect is essentially at its long-run value by 2040 — but the panel no longer carries a short/long
contrast. A presentation cost accepted knowingly rather than a defect, recorded in the README so the next
reader does not "fix" it.

**`ARG_LOG_FourInOne`: from a cross to a surface.** It plotted two slices through the calibrated point on
one shared x-axis, which forced two disjoint domains onto one axis labelled "parameter value". Now: x is
`ε`, one curve per `θ`, the span between adjacent curves shaded. **The band's width at a given `ε` is how
much `θ` matters there**, which is a statement the cross could not make at all.

*Two conventions this established, both now in the README:* a continuous parameter does not get the
categorical pair (`THETA_RAMP` is one hue light→dark, with its middle step deliberately the categorical
blue so the two kinds of figure read as one family); and the calibrated `θ` is drawn **in ink, not as a
further value of the ramp** — it is an annotation, and giving it a hue would send the reader to the
colourbar to find it. It needs a surface-coloured halo, since the calibrated `θ` sits in the ramp's dark
end on three of four panels and bare ink on navy is unreadable in print.

**A loader that must reject a shape, not just a missing file.** `datasets.epsThetaGrid` raises unless the
csv is a complete rectangle: a missing pair becomes a NaN that `fill_between` drops **silently**, so with a
resumable producer upstream a half-finished sweep would render as a figure with holes instead of as a
skipped output. Same principle as the rest of stage (iii), except that here "has not finished" is a
property of the file's shape rather than its existence.

**The cross sweep was removed rather than kept as a witness.** Once the grid superseded it, the old csv had
one remaining use: its rows agreed with the grid's to ~1e-16 along both calibrated lines, evidence that two
independently written parameter-installation paths agreed. Tempting to keep for that. The user's call was
to delete it, and it is right — a superseded file kept beside a live one for a reason that is *not* the
pipeline's own use is exactly #8's shape, and the check had already paid out. What it verified is recorded
here; the file is gone.

*Also fixed, pre-existing:* `runShocks.py --dry` printed the Greek `--nι` and died on redirected cp1252
stdout — the repo's documented trap, in one of the few files written before `gridsearch.testing` existed to
prevent it.

## 2026-08-22 — the second arm: US / France / UK

**Why separate stage (i)/(ii) entry points rather than a `--model` flag.** The two arms delegate to
different experiment scripts with different CLIs, and **the declarations are the point of those files** — a
single entry point would have to carry both flag vocabularies and would make it harder, not easier, to read
off what the paper's numbers were produced at. Stage (iii) is shared because it is model-agnostic by
construction.

**Stage (i) is order-dependent here and is not in the Argentina arm**, so `runCalibrationUS.py` enforces
that the US sweep is complete before any European one starts rather than relying on loop order — a partial
US sweep would otherwise fail one point at a time in the middle of a march, which is the expensive way to
find out.

**The contracts were verified, not assumed.** Stages (i)/(ii) skip everything already done; stage (iii) is
idempotent and does *not* re-back-up on a second run; and with `US_shocks.csv` removed, the seven
shock-derived outputs report `BLOCKED` and write nothing while the four calibration-derived ones stay `OK`.

**Two conventions the builders must not re-apply** (README): the US shock csv already carries `sr` as
`s/(w·h)` and `workweek` already in hours, normalised against *that ρ's own* baseline. Re-deriving the
workweek in stage (iii) would be wrong twice over. This is the Argentina arm's `workweekHours` trap one
layer earlier, which is why the loaders hand the column through untouched.

**One bug worth naming.** `config.pct` escapes the percent for tex, so putting it in a matplotlib legend
rendered a literal backslash. Anything drawn *into* a figure needs plain formatting.

## 2026-08-24 — the ESC leg through all three stages, and the appendix rewritten

The endogenous-θ appendix was the last unwired corner of `writing/Paper`. Stage (i) gained a
**per-(ρ, spec)** check of the wedge calibrations rather than a per-file one, because a CRRA calibration
costs ~25–30 min and the check being cheap is what lets the stage keep its "re-run costs seconds" property.
Stage (ii) gained the two shock entries plus the merge, listed last so a `--force` rebuilds it after its
producers. Stage (iii) gained five builders sharing one `_escTable`.

**The ESC drivers now merge into their csvs instead of overwriting.** Without this, stage (i)'s "re-run
exactly the missing (ρ, spec)" would clobber every other row in the file — the failure mode that produced
this session's tagged-file workaround in the first place.

**A trap for the record**: appending python to a file through a quoted bash heredoc halved every `\` in the
tex-emitting builders. Raw strings ending in what became a single backslash are a syntax error, and worse,
`\hline` silently becomes something that still parses. Don't emit tex-bearing python via heredoc.

**The appendix itself** was rewritten from the working-notes draft into a short paper section: the four
variants, the one-corner lesson (kept as the single retained derivation), why the preferred spec is leaded
+ proportional cost, the calibration table, a solution paragraph, and the four experiments at
ρ ∈ {0.5, 1, 2} with the income+voting combination in text. Everything else is deferred to the online
technical documentation in `writing/`, referenced in a footnote — which formalizes what those docs are for.
All numbers in the text were checked against the built tables.

## 2026-08-24 — the counterfactual convention changed under the pipeline

`python/US` switched every US counterfactual to a new equilibrium path read at 2020. Three things followed
here.

**Stage (iii) reads t0 for the ESC tables now, not t0+1**, and the "identical by construction at 2020" note
is gone — it was true only while the design was pinned as history through 2020. The main-text and appendix
legs are finally on the same dating.

**Every ESC calibration point had to be recomputed, not just the experiments.** The wedge target moved one
period back with the reporting, so `escCalibration{,CRRA}.csv` are new files, not new rows. **A stale `p`
is no longer merely old — it answers a different question.**

**Two new rows and one new table.** `frAll` and France's own calibrated path. The France row is not a
counterfactual on the US model — France brings its own `ω` — and its workweek is `ModelFR`'s calibration
target rather than a prediction, which every note that prints it now says.

**Two string bugs fixed in `tablesUS.py`, both silently wrong in the shipped tex.** `r'...France''s...'` is
not an escaped apostrophe — Python splits it into a raw part and a *non-raw* part, so the apostrophe
vanished and the `\theta` that followed became a literal tab. And `\n` inside a raw string is a
backslash-n, so one `\item` separator rendered literally. **The same trap bit again the same day** in
`Quant.tex` and both `model_calibration.tex` files, where "Argentina''s" silently became "Argentinas" —
caught by re-reading the rendered line rather than by any check. Worth treating adjacent-literal
concatenation inside `r'...'` as a repo-wide hazard.

## 2026-08-24 (cont.) — stage (0), and the Argentina arm re-run end to end

**`dataTargets.py` is a new stage (0), and the only part of the pipeline that touches the network.** It
writes to `data/`, not `results/` — the target is a calibration *input*, on the same footing as the
workbook. It exists because that number is a reading of an external series at a chosen year rather than
something anyone typed: the derivation has to be reproducible, and the record has to carry the window, the
source and the retrieval date. It writes **both** readings every run and names only one
`capitalOutputRatio`, so the choice that was made is visible next to the one that was not — the two are 13%
apart and they straddle `β = 1`.

**`tables.argentinaCalibration`'s `β` row** now reads "Capital--output ratio of $3.23$" where it read
"Private savings rate of $18.4\%$" — a label that was wrong on the concept, the sector *and* the
denominator even for the old number. That edit and `summarise()`'s were made **before** the re-run rather
than after, since on the old csvs they break the build.

**`datasets.seedSavings` needed nothing**, which is worth recording as a design paying off: it inverts eq
(calibration) at `t0` but reads the *achieved* savings rate off the sweep csv instead of assuming the
target's 0.184. A version that had hard-coded the target would have failed silently against a calibration
that no longer targets it.

**Two notes for the next person driving this pipeline.** `--force` is not optional on either expensive
stage — every experiment script is resumable on its own csv and will hand back the old rows without a word.
And a bare `build.py` rebuilds *both* arms, so it publishes whatever in-progress work is in the tree along
with the numbers you meant to publish; `--only` when that is not wanted.

## 2026-08-24 (cont.) — cleanup

The README lost its narrative sections to this log and to `notes/`, and gained a corrected claim: it said
`writing/Paper` is not tracked by git, which is false (42 files are). That mattered, because it was the
stated reason `results/paper/superseded/` had to be preserved indefinitely. The originals are in git at
`bfba998:results/paper/superseded/` and the directory is gone from the working tree.

## 2026-08-25 — a two-calibration sweep behind `ARG_LOG_FourInOne`, and the guards that now stop it

**The figure was wrong on the page and had been since the retarget.** `results/sweeps/epsThetaGrid` is
resumable on `(eps, theta)`, so the 2026-08-24 K/Y re-run *added* the new calibrated `eps` column and kept
everything else: 378 of 392 rows were bit-identical to the pre-retarget file, `time` column included. The
figure showed one column of the current economy inside a surface of the old one — a 3.7 p.p. notch in the
savings-rate panel, and the whole workweek panel rescaled against an `hRef` that belonged only to the
fresh column. Generalised as `crossCuttingFindings.md` #13; the archived file is
`results/sweeps/superseded/epsThetaGrid_rho1.0000_preKYretarget.csv`.

**Neither existing guard could have caught it, and that is the transferable part.** The rectangle check
asks "is this finished", and staleness *adds a column* rather than leaving a hole — 28x14 is as
rectangular as 27x14. The real tell was semantic: **two rows flagged `statusQuo`**, since the pinned
calibrated point is inserted and the old one is never removed. `datasets.epsThetaGrid` now requires
exactly one, **and** requires it to match `calibrationSummary` — the second check is the one that matters,
because a *wholly* stale csv has exactly one `statusQuo` row and would pass the first. Tested against all
four states (fresh, mixed, wholly stale, truncated).

**`--force` was documentation, not behaviour.** It only ever defeated `runShocks.py`'s own skip; it was
never appended to the child command. So the 2026-08-24 entry's "`--force` is not optional on either
expensive stage" was unactionable — and also overstated: `sweepEpsThetaGrid.py` is the **only** one of the
seven children across both arms that resumes from its own csv. The two Argentina shock scripts and
`runShocksUS.py` `to_csv` outright; the ESC drivers `mergeWrite`, which replaces the keys the run produced.
It is now declared per entry (`'force': ['--force']`) rather than assumed universal, since a flag the child
does not parse would crash argparse.

**A flag that reads as compliance but does nothing is worse than no flag.** Anyone who had followed the
written advice would still have received the stale csv, and would have had more confidence in it.

**Cost correction: the sweep is ~15 min, not ~5.** 378 points at ~2.4 s each. The old ~0.65 s/point came
from the pre-retarget calibration's own `time` column, so the estimate was stale in the same way the rows
were — a measurement inherited across the change that invalidated it.

## 2026-08-25 (cont.) — the builders reconciled with hand edits to the draft

Three tables in `writing/Paper` had been edited by hand; 17 others differed only in line endings. Diffing
`results/paper/Tables/` against `writing/Paper/Tables/` isolates that in one pass and is the right tool
here — `git status` cannot separate a content edit from a CRLF rewrite.

The changes were pushed back to their sources, not to the tex: `config.ARG['ρTable']` `[0.8, 1.0, 2.0]` ->
`[0.5, 1.0, 2.0]` (now equal to `US['ρTable']`, so both arms show the same three points), and two shortened
note strings in `tables.py`/`tablesUS.py`. The `ArgentinaCalibration` note lost its residual, which
orphaned `_sci` — removed, no other caller.

**Verification against git, not against the rebuilt file.** After rebuilding, `writing/Paper` necessarily
matches `results/paper` because build.py just copied it there; the question is whether it matches what the
*user wrote*. The blob hashes were unchanged (`8060794`, `01c05af`), so the builders reproduce the hand
edits byte for byte. Full rebuild: 23 built, 0 skipped, nothing backed up to `superseded/` — correct, since
all three carried the `%% GENERATED` banner and so were recognised as build.py's own output.
