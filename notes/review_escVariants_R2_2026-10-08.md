# R2, the numbers audit of the endogenous-design rewrite (2026-10-08)

Read-only report of the `paper-reviewer` role (a `general-purpose` agent on Opus at max), kept for the
record; the prose items went to the fix pass, items 7 (online text), 8, 10 (online text), 11 and 12 to the
builder. Line numbers are those of the files at the time of the audit.

In the three main files every $\theta$, tax level, p.p. change, share lost and parameter matched its cell at
the printed precision; section 7.3's tax rates come from the right column and block; every corner is
printed 1.000 or 0.000; no sign in symbols in prose. Item 5 is the only literal numeric mismatch.

1. **The composite claim.** Introduction:27, Conclusion:7 and section 7:54 say the two French
   characteristics together "match" the cross-section's weak relation; the LQ cells are frincome 0.850
   (+0.112), frvoting 0.622 ($-0.116$), frboth 0.641 ($-0.097$): the pair does not offset, it moves the design
   84% as far as voting alone and 71% as far as acute ageing. Fix: quote 0.641 and say what it is; drop
   "match".
2. **abstract:6** "a deadweight cost of flat benefits" -> "of redistribution" (style guide §4).
3. **Section 7:27** "the size of the system, 11.9% against 21.3%, as in figure 1": the figure plots spending
   (7.8%, 14.4% of GDP); the rates are table `US:Calib`'s. Cite the table.
4. **Introduction:27** "France's fully Bismarckian design would need a larger constant share than the UK's
   design allows" is false for the linear cost (UK own 2.414 against France's threshold 1.312) and true for
   the linear-quadratic (1.260 against 0.674). Qualify.
5. **Appendix G:6** "France, at 1.94" -> 1.93 (0.42228/0.21838); the UK's ratio at one precision (1.307).
6. **Section 7:48** "22.3% against 14.4%" is the pinned reading (chosen 22.7%): name it.
7. **Section 7:32** "after which the tax path carries no further design response": the chosen-minus-pinned
   tax gap under the linear cost grows from +0.81 p.p. (2050) to +1.01 (2080 on); "the design no longer
   moves". The online text's "a little above" under every specification is wrong for the linear cost.
8. **`US_ESC_Results`' note** sends readers to `\oa{esc-variants}` and `\oa{esc-us}` for tables now in the
   paper (G.2, G.3): `\ref` them.
9. **Section 7:23** the shares lost are $1-f$ from `table:US_ESC:variants` itself: cite the table.
10. **Units.** G:18 "about half a point" -> "0.5 p.p. of GDP"; the online texts "within a tenth of a point",
    "within half a point" -> p.p.
11. **`US_ESC_VariantsCountry`'s note** sources $\theta^{\ast}$ to `US:Calib`, which lacks the regrouped UK's
    0.543.
12. **`US_ESC_Path.marks.json`** carries the LQ series only; the quadratic 0.809 and the linear corner trace
    to `ESC_PathTable` rows alone.

Cross-references: the last compile (71 pages) has no undefined reference; every `\oa` key used is a group.
Outside the brief: the compile leaves the 40 hyperref footnote anchors unresolved (`Hfootnote.1-40`), a
pre-existing condition of the preamble, so every footnote link is dead.

Per file: section 7, 102 numbers checked, 7 findings; appendix G, 74 and 2; appendix C (magnitude, $\theta^{\ast}$),
8 and 0; introduction, 9 claims and 2; abstract, 4 and 1; conclusion, 9 and 1; the online texts, 18 and 2;
the four new tables' notes, 16 parameters and claims against the csvs, all matching, 2 findings.
