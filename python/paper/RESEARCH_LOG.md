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


## 2026-08-27 — common X leads, and one builder makes both variants

**Decision, from the user**: the paper leads with the common-`X` calibration and keeps vector `X_i` as an
appendix robustness set. `config.US['commonX']` names the headline; every US builder takes `commonX` and
defaults to it, and `build._variants` registers the pair. **The headline output keeps the plain name,
filename and tex `\label` the draft already cites, and the twin's carry the variant they contain** — so
flipping the flag changes what is inside the paper's tables without renaming one of them, and a file on
disk says which economy it is about. 23 outputs became 34.

`config.variantNote` puts one sentence naming the variant into *every* US table note, headline included.
The two variants share `β`, `ω`, `τ`, `R`, the savings rate and aggregate `h` exactly, so a reader
comparing two tables cannot tell them apart from the columns that did not move.

**The variants check each other, and the old form of that check was wrong about one row.** Run the same
set under both: baseline, θ, ageing and voting come back identical (≤ 5e-15 in τ and sr — block
recursivity end to end), income distribution and all-three differ (4.9e-3, 5.1e-3 in τ). The README asked
for leisure to differ *in τ* as well; it cannot. Leisure is a pure scale, so τ and the savings rate are
pinned at baseline in **both** variants (they agree to 2.3e-5) and the whole variant effect lands on
hours — 34.74 against 33.24, because `Xbar_FR/Xbar_US` is 1.520 under vector `X` and 1.761 under common
`X`. A check keyed to a quantity that cannot move reports a pass for the wrong reason.

## 2026-08-27 — three panels instead of one, and an inverted axis that was right by parity

`US_taxOverview`/`USX_taxOverview` are retired for `US_overview`: tax, savings rate and workweek as three
panels on a shared scenario axis, plus the two rows the tax figure never carried — all three French
characteristics at once, and France's own calibrated path. The layout earns itself: the tax panel's
ranking (ageing and design dominate, the French characteristics minor) is **inverted** by the workweek
panel, where leisure preferences are the largest mover and move τ not at all. That contrast is the
paper's own US-Europe hours argument, and it is invisible in three separate figures.

`US_ESC_overview` is the appendix counterpart: bar = the effect at a fixed design, open marker = the same
effect with the design chosen, both against the same baseline, so the gap between them is the design
response read along the axis rather than across a gutter. Four panels, the design itself first — where the
exogenous bars sit at zero by construction and give the scale the other three panels' gaps are read on.

**A latent bug the four-panel figure exposed.** The panels are created with `sharey=True`, so they are one
y-axis wearing several faces, and `invert_yaxis()` called per panel flips it once per call: the scenario
order reverses on an even panel count and survives on an odd one. The three-panel figure was upright
**by parity**, from the same code that put the four-panel one upside down. `_topDown` now inverts once,
outside the per-panel helper, and says why.

Also: `_panel` must be called *before* `set_yticklabels`, since its `tick_params` recolours the scenario
labels to the muted ink meant for numeric ticks; and the legend moved to figure level, because with the
France row present there is no in-panel position that is not on top of a bar.

## 2026-09-08 — a shared pre-reform row that was only shared in two of its three columns

`argentinaFuncOfRho` printed one pre-reform row (τ, savings rate, workweek from the ρ = 1 calibration)
over post-reform rows at every ρ, on the reasoning — still in the inline comment — that "τ and the savings
rate are calibration targets, so they are identical at every ρ by construction". True before the K/Y
retarget, false after it: the savings rate $s_t/Y_t$ is now $K/Y$ times the period's output growth, and
the growth term depends on how strongly households front-load against the slowing population path, i.e.
on ρ. Per ρ, own baseline vs. calibration summary vs. reform at 2010:

| ρ | own baseline | summary (ρ = 1) | reform | effect (own) | effect as printed |
|---|---|---|---|---|---|
| 0.5 | 15.34% | 14.72% | 15.27% | −0.07 | **+0.54** |
| 1.0 | 14.72% | 14.72% | 14.45% | −0.27 | −0.27 |
| 2.0 | 14.10% | 14.72% | 13.90% | −0.20 | −0.82 |

The figure (`argCrraLog`) was right all along: it differences against `savingsRatePath(ρ, 'base')`, which
equals the sweep csv's achieved `sr` at every ρ to machine precision. The table now emits a pre/post pair
per ρ (both rows commented outside `ρTable`), the pre-reform τ and workweek read from the same shock row
rather than the summary, and the note says which columns are common and why. README trap added.

**The same reasoning is wrong in `_crraTable`, and that is open.** The US identifies β by R, so its
baseline savings rate is 22.73 / 21.96 / 21.22% at ρ = 0.5 / 1 / 2 (`US_shocksCommonX.csv`, $s/(wh)$
units). The three CRRA tables print the ρ = 1 baseline once, with a note claiming the targets are hit
there — τ is, the savings rate is not. Consequences, savings effect as printed vs. against own baseline:
θ = 0 at ρ = 2, −0.60 vs +0.14 p.p.; θ = 1 at ρ = 2, −0.65 vs +0.09; mild ageing across ρ = 0.5 → 2,
−0.81 → −2.00 as printed against −1.58 → −1.26 in fact; leisure, ±0.8 as printed against exactly 0.00
(pure scale). The printed tables therefore say the savings response grows with ρ when it shrinks, and
Quant.tex's "almost linear in ρ" reading of the savings column rests on the artefact. Fix is the ESC
tables' layout — a baseline group of three rows, one per ρ — in the one shared builder, rebuilding six
files. `usOverview` and the ESC outputs were already per-ρ and need nothing.

## 2026-09-08 (later) — s/Y everywhere, changes against each ρ's baseline, and two figures redrawn

**The savings-rate convention is one unit now.** The US tables and figures read `srOverY` (= s/Y) from
the shock csv instead of `sr` (= s/(wh)); the ESC csvs carry only s/(wh) and `datasets.escSavingsOverY`
converts by the exact `(1-α)`, with α read from `usCalibrationSummary.csv` and cross-checked against the
workbook (`datasets.usAlpha`). US baselines in s/Y: 15.91 / 15.37 / 14.85% at ρ = 0.5 / 1 / 2.

**Every counterfactual row prints the savings rate as a change against that ρ's own baseline**
(`config.pp`, `tables.SRNOTE`), which closes the morning's open defect in the three `US_CRRA_*` tables:
they now carry a baseline group of three rows and difference per ρ. The check that the differencing is
right is the leisure row, `0.00 p.p.` at every ρ in both variants (raw +0.0047 / 0.0000 / −0.0001). The
sign flips the morning's entry predicted are now on the page: θ = 0 at ρ = 2 is +0.10 p.p., θ = 1 is
+0.06, mild ageing shrinks −1.10 → −0.88 across ρ. A scripted cell-by-cell check of every changed table
against the csv: 0 mismatches. The ESC tables difference against the *endogenous* baseline (the printed
row, and what the figure differences against), so their exogenous leisure rows show the 0.01–0.02 p.p.
gap between the two baselines; switching them to the pinned baseline is a one-line change in `_escTable`.

**Figures.** `US_overview` drops the all-three and France rows and its savings panel is s/Y.
`US_ESC_overview` is a dumbbell chart — open marker at the pinned reading, filled at the chosen one, one
connector per (scenario, ρ), design panel as a level with every pinned marker at 0.738 by construction.
Two alternatives were drawn and kept as pngs in the session scratchpad: a single-panel "chosen θ against
ρ" line chart (the clearest statement of the design response; worth adding as a companion figure) and a
5×3 small-multiples grid (too small at `\linewidth`). `frAll` is dropped from the ESC figure since by
scale invariance it duplicates `frBoth` in everything the figure shows.

**Pipeline.** `config.ARG['anchorGuess']` is forwarded to the Argentina sweep as `--x0`. `build.py --list`
raises (not `MissingInput`) on `seedSavings`' agreement guard while the Argentina csvs are of mixed
vintage — expected during the re-run, and the guard working as intended. The Argentina builders were
verified on the committed α = 0.43 csvs in a scratch tree; their new numbers arrive with the re-run.

## 2026-09-08 (writing session) — Table 3 gets one pre-reform row and a "Change in savings rate" column

`argentinaFuncOfRho` no longer prints a pre-reform row per ρ. RKB's reading: the two things that are
common across ρ by construction (τ is a target, the workweek a normalisation) belong in one shared row,
and the pre-reform savings level, which is a prediction that varies with ρ, is simply not printed (`--`)
rather than printed per ρ. Every post-reform row still differences against its own ρ's baseline path, so
the p.p. changes are unchanged; the column header now says "Change in savings rate". The builder raises
if the pre-reform τ is not common across ρ — a spread would mean a calibration point missed its target,
and a single row must not hide that. The three `US_CRRA_*` tables keep their per-ρ baseline rows (their
baseline savings level is part of what they show). README's convention bullet updated.

Also this session: the rebuilt US/UK/FR tables and the three US figures were copied from `results/paper`
into `writing/Paper` by hand (`cp`), since the draft copies predated the s/Y convention and the Argentina
pipeline — which the copy stage would otherwise wait for — never touches them.

## 2026-09-08 (evening) — the corrected Argentina pass landed and the Argentina prose was re-read

`build.py` with the copy at 19:10: the draft's Argentina tables had still been the α = 0.43 vintage.
Then every `TODO-ARG035` marker was resolved against the new tables (`notes/todo_paperRewrite.md` item 2
records what each paragraph now says). Two things the numbers forced beyond a find-and-replace: the
reform paragraph claimed higher labour supply where both table rows show lower hours (fixed, with the
taxes-fixed mechanism), and the four-in-one figure's 1.6 p.p. move along the calibrated θ is the
always-had-it comparison, which sits next to the 1.7 p.p. long-run effect rather than the 1.0 p.p.
impact effect — the text now says so instead of quoting one number beside the other.

## 2026-09-10 — table notes follow RKB's online edits; f(theta*) computed; tax targets in the calibration table

RKB edited eight generated tables on Overleaf; the pull refused them (banner) and the edits went into
the builders. `config.variantNote(commonX, full = False)`: every US table now points at the calibration
table's note ("Common-X calibration: see the note to Table X", label via `variantSuffix` so the vector-X
twins point at their own), and only `usukfrCalibration` passes `full = True`. Notes shortened as online
(ageing, the CRRA tables, other shocks, the ESC calibration, the Argentina universal table); every US
note now opens with `\textit{Note:}` like the Argentina ones; `\cref` replaced by `Table~\ref` in the
two notes that had it. Kept against the online version on RKB's instruction: `tablenotes`, and no `\ \ `
spacing in header cells. `escCalibrationTable` gained a fourth column f(theta*) = phi + (1-phi) theta*^p
computed from the csv (0.873 / 0.942 / 0.987; RKB had typed 0.986 for the last, the value is 0.9865).
`usukfrCalibration`'s omega row prints the tax targets from `τ0` in the summary csv as
`$\tau^{US} = 14.4\%$, ...`. Verified by a normalised diff of the rebuilt tables against the online
copies: only the intended differences remain. `config.py` carried two literal 0x08 bytes where `\bar h`
and `\beta` should be (heredoc damage); fixed.
