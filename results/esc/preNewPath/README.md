# Superseded: the unanticipated-shock convention (pre 2026-08-24)

Every csv here was produced under the convention `runESC.py` used before the new-path rewrite:

* counterfactuals run on `createCopyFromt0(2020)`, seeded with the baseline's own savings, i.e. an
  UNANTICIPATED permanent reform dated 2020;
* the design pinned at theta* as history through 2020 (`pinAtT0=True`), so the tables had to be read at
  t0+1 = 2050 -- 2020 was identical across the pinned and chosen readings by construction;
* the wedge `p` calibrated on `thetaPolicy_{2020}(theta*) = theta*`, the choice MADE at 2020.

The live files replace all three: new equilibrium paths (shocked parameters over the whole horizon, own
steady state), the choice binding from the first period, read at 2020, and `p` calibrated on the design
in FORCE at 2020 (`ModelESC.leadedDesignAtT0`). Under `scale`, phi = 0.5, rho = 1 that moves p from
0.40220 to 0.40761.

Kept for the record only -- nothing reads them. See `notes/crossCuttingFindings.md` #8.
