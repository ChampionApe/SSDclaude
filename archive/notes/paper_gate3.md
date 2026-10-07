# Gate 3 note: paper rewrite, session 3 (2026-09-30)

For RKB, then MGE. Session 3 of `notes/paper_presentationPlan.md` §8 is done: the abstract, introduction and
conclusion rewritten by the main session against the final sections 3–7, then C1's referee pass (read-only, no
priors from the notes). Gate 2's decisions are applied (G2.2: the Argentine workweek change at one decimal).
Everything is committed on `paper-rewrite` and pushed to Overleaf for this read (the dry-run pull first: the one
online difference was the branch's own newer section 5, no online edit). **Record decisions in the DECISIONS
block at the end of this file.** Session 4 reads §8 of the plan, `notes/paper_gate2.md` §3 (the out-of-scope
items for the appendices) and this file.

Checker, from the repo root, clean with no tag left: `PYTHONUTF8=1 .venv\Scripts\python.exe writing\checkPaper.py`

## 1. Word counts (checker's; the plan's method runs about 10% higher)

| Piece | Before | After | Plan §3 target |
|---|---|---|---|
| Abstract | 248 | 219, of which about 35 are the JEL and keyword lines; body about 185 | ≤ 180 |
| Introduction | 2,194 | 1,752, of which about 200 are figure 1's source footnote; body about 1,550 | 1,700 |
| Conclusion | 696 | 486 | 450 |

## 2. What to read

**Abstract.** The plan's candidate, with the sign of the design result as section 3 states it (taxes lower when
benefits are earnings-related), the Argentine result as "almost half", and the design-chosen sentence in three
short sentences.

**Introduction**, in the plan's order: (1) motivation, the two dimensions, design as a political outcome
(the duplicate sentence gone); (2) the facts, with figure 1 here: spending and the index rise as population
growth falls and rise together, neither follows the Gini, against \textcite{CondeRuizP07a1}, and the paper's
question; the sourced footnote from gate 1 (correlations 0.63 spending–index, $-0.08$ and $0.18$ with the
Gini); (3) the model in one paragraph, informal households in two sentences (platform work is now one clause of
the conclusion); (4) result 1 as what the closed form shows, not "tractability is the contribution"; (5)
Argentina as validation (1.2 p.p., 0.8% of GDP, almost half; savings 0.3 p.p. of GDP, hours 0.1) then the
ranking (8.7, 6.2, 1.2, 0.9 p.p., all checked against sections 5–6); (6) the corner as a proved result and the
cost with its three predictions, each tied to figure 1 (0.738 to 0.825 under a constant population); (7) CRRA in
three sentences (9.0 to 1.5 p.p.); (8) the literature in three blocks, see G3.1; (9) the roadmap. The old
paragraph "These results yield several contributions" is cut (its growth-and-inequality claim was not
delivered), and so is the platform-work paragraph. The `TODO-W1` tag is resolved by the rewrite: its sentence
("slower population growth raises the tax ... and makes the system more Bismarckian ...") now lives in
paragraphs (2) and (6b) in the plain register; nothing of its content was dropped (G3.2).

**Conclusion**, in the plan's order: what the paper does (two sentences); the findings in the arc's order with
the design result as the climax; two limitations (no risk, with \textcite{BergGEwp}; France's corner, with the
linear term or the formality margin as the way out) and platform work in one clause. Units fixed: savings
0.3 p.p. of GDP and hours 0.1 a week (was "0.3%"); "within 16%" qualified as the log case (plan §6.1).

**Two wording calls made without a source to lean on.** The introduction's "91% of retirees by 2010" is gone:
B3 found no source for it in the repo and section 5 says "almost universal" (Cetrángolo and Grushka;
Rofman), so the introduction says the same (G3.3). The reform is dated "from 2005", and "2005 to 2010" in the
conclusion, as section 5 has it.

## 3. C1, the referee pass

C1 read the whole draft, every table and figure, and the style guide's §3–4 only, and reported without fixing.
Its full report is condensed here into what was fixed before the push, what is your call, and what goes to
session 4.

**Fixed before the push (main session's files: abstract, introduction, conclusion, section 7).**
- "Closed form": section 3 says the equilibrium conditions are solved numerically in most cases; what the
  proposition delivers is state independence. The abstract and introduction now say the tax is a function of
  parameters and demographics alone, and the abstract names the hand-to-mouth assumption.
- Section 7.3: "the UK and France ... at the U.S. income cuts, Ṽ = 0.223 and 0.218" was wrong, 0.223 is the UK
  at its own cuts (0.065 at the U.S. cuts, `US_ESC_Country`); now "the UK at its own income cuts and France at
  the U.S. percentiles".
- Section 7.3 and the conclusion: "the agreement is specific to the log case" was wrong, the UK's own cost is
  17% below the U.S. one at ρ = 0.5 (15.089 against 18.242, note to `UK_ESC_IncomeDistr`); the agreement holds
  at ρ ≤ 1 and breaks at ρ = 2.
- Three literature sentences overstated the link to us: Cremer et al.'s myopia is not "the role our propensities
  play" (our interior design rests on λ); Levy's formality margin is not one "our Argentine application turns on"
  (γ₀ is fixed); Galasso–Profeta's drift is one the model "predicts", not "quantifies" (no table carries the
  path, by G1.3). All three reworded.
- Terminology: "log-GHH preferences" throughout the three pieces; "contributive" for "contributory"; figure 1's
  index called the Bismarckian--Beveridgean index, as its footnote does, to keep "Bismarckian index" for θ.

**Your call (G3.5), the substantive ones.**
- (C1's referee point a, and its claims 1–2.) "Inequality moves the design little" and "voting patterns minor"
  hold at ρ ≤ 1. At ρ = 2, France's income distribution moves the chosen design from 0.738 to 0.919, twice acute
  ageing's move to 0.826 (`US_ESC_IncomeDistr`, `US_ESC_Ageing`), and French voting raises the tax by 1.7 p.p.
  against 1.5 p.p. for the whole design range (`US_CRRA_OtherShocks`, `US_CRRA_PensChars`); section 6 calls the
  French characteristics "visibly minor" in the overview figure. ρ = 2 is inside the range the paper argues for.
  Options: qualify the abstract and introduction ("at intertemporal elasticities of one or below"), or state the
  rankings for ρ ≤ 1 and report ρ = 2 as the documented exception with the thin-cushion mechanism 7.4 already
  gives (recommended: the second, in session 5's consistency pass; one clause in the abstract).
- (Claim 3, referee point b.) "Orders the designs as observed": at ρ = 1, and compressed (France 0.749 against the
  U.S. 0.738; UK 0.625 against 0.560). The abstract and introduction say "as observed" without the qualifier that
  7.3 gives. Recommended: "orders ... as observed, though compressed" in the introduction; the abstract as is.
- (Claim 4, referee point c.) Proposition 2's design comparative statics are proved in appendix B.1 without the
  propensities to vote, while the objective and the U.S. calibration carry μ_i, and the ε threshold is argued in
  its two limits under an unstated assumption (informal retirees poorer). The paper can answer with
  `US_PensChars` (the θ sign holds at U.S. propensities) and the footnote in section 5 for the sign of ε.
  Recommended: session 4 states the proposition's assumption (equal propensities, or μ_i in the objective and
  the proof) and the poorer-informal condition, with the appendix aligned; no change to the framing.
- The introduction's "with one exception" for CRRA leaves out Argentina at ρ = 0.5 (+0.2 against +1.2 p.p.) and
  the chosen design under French voting (0.334 at ρ = 2). Recommended: "with the exceptions section 5 to 7 name"
  or leave.
- Argentina's "2.7 million beneficiaries" against figure 2, which rises from about 2.9 to 4.9 million over
  2005–2010 (about 2.0 million); the 2.7 is from the earlier draft. Source to check (the Cetrángolo–Grushka
  figure), then the text or the figure caption says which count it is.
- Section 6's "the gap in taxes is due to France's demography, its fully Bismarckian design and the political
  weight of its old" (also G.1): the design (θ = 1 lowers the U.S. tax, `US_PensChars`) and ω_FR = 1.42 < 1.45
  both narrow the gap; only demography widens it. Recommended: "due to France's demography" alone, session 4.

**For session 4 (appendices) and session 5 (python/paper).**
- Appendix D line 20: the formula for the pre-reform ε gives 0.38 × ε^U = 0.21 with the first quartile's relative
  income, not 0.29; 0.29 comes out only with the second quartile's. This sets the size of the reform behind
  "almost half", so it is the first item to settle (RKB, with the workbook).
- Appendix D line 30: the shadow-economy formula gives 0.29 at 20% and 0.24 at 25%, not 0.30. Line 42: the
  calibration table has no hours rows; 1.18 against 1.10 is derivable only from the η_i and X_i.
- Appendix G.2 line 39: at ρ = 2 the workweek is 0.17 h above the pinned reading in the income-distribution row,
  not "up to half an hour below". Two-decimal designs and two-decimal tax gaps at `US.tex` 65, 90 and
  `UKvsUS.tex` 39, 47.
- Terminology for the consistency pass: ρ written as "the elasticity" in section 7 where the guide gives "IES",
  and "elasticity" also naming ξ and ε there; ε (`\varepsilon`) used for a behavioural elasticity in 7.2, where ε
  is the universal-pension level; "voting profile" against the guide's "voting patterns"; "pension design" in
  section 6 and the table captions against the guide's "pension characteristics" (the guide may be the stale
  side); "PEE taxes" undefined in appendix B; generated captions writing "US" and "the US design".
- `python/paper`: the composite scenario is "Income distr. + voting" in figures `US_ESC_overview` and
  `UKUS_ESC_French` but "All French characteristics" in the tables and 7.4, and the figure's composite omits
  France's X, so its workweek change (about +0.6 h at ρ = 1) is not the table's −4.5 h. One label and one
  definition, in session 5.

## 4. Next: session 4 (plan §8)

D1 (the online root and `overleaf.py export`) and D2 (appendices per plan §3's table), with the out-of-scope
items of `notes/paper_gate2.md` §3: the F.1 sentence to drop, G.2's 1.6 → 1.5 p.p., the two-decimal designs in
F.3 and G.2, appendix A's part v proof (G2.1), appendix D's lines 30 and 42, appendix E's France survey year
(2018). The main session takes the LIS year and the country count. MGE reads this gate alongside session 4.

## DECISIONS (RKB)

Fill in below; a blank line means "as recommended".

- **G3.1 A3's references.** Cited in the introduction's literature block (Galasso–Profeta 2002 as the survey;
  Tabellini 2000 for the coalition behind the corner; Cremer et al. 2007 with myopia named as the analogue of
  our voting weights; Galasso–Profeta 2004 for ageing and the drift toward earnings-related benefits, not for
  "designs"; Bethencourt–Galasso 2008 for Medicare; Levy 2008 for informality), and nowhere else, which is how
  the main session read G1.4 ("not here" = not in section 7). If G1.4 meant no citation at all, the sentence
  block is one paragraph to delete (recommended: keep; a design paper without these will be asked for them).
  RKB: 2026-10-01, in session: the block ends at "and take it to the data"; the Tabellini, Cremer-myopia and
  Galasso–Profeta 2004 sentence cut (both now uncited); Galasso–Profeta 2002's open question opens the design
  paragraph; Bethencourt–Galasso in section 6's Medicare footnote; Levy's footnote in section 2 cut by RKB online.
- **G3.2 `TODO-W1`.** Resolved by the rewrite as described (recommended: accept).
  RKB:
- **G3.3 Argentine coverage.** "almost universal" in the introduction and section 5; the 91% dropped
  (recommended: accept, or give the source and it goes back in both places).
  RKB:
- **G3.4 Lengths.** Abstract body about 185 against ≤ 180; the introduction on target once the footnote is
  discounted; the conclusion at 486 (recommended: stop here).
  RKB:
- **G3.5 C1's list.** Which items the main session acts on in session 4 (recommended: every number mismatch
  and terminology drift C1 confirms; the three referee points are for the reply, not the text, unless one
  names a sentence to change).
  RKB: 2026-10-01, in session: referee point c led to a re-derivation of proposition 2; the ε threshold claim is
  replaced by the pension-share condition `eq:LOG:epsCondition` (`notes/prop2_epsilonCheck.md`), the ν sign gets
  its condition in appendix B.1; the equal-μ statement of the proposition stays for session 4.
- **G3.6 MGE's read.** Push done; the line to MGE: sections 2–7 are settled at this gate, sessions 4–5 touch
  the appendices, `main.tex` (the online switch) and the technical note, so online edits to those stay
  comments until gate 5, or he says which he edits (recommended: send as is).
  RKB:
