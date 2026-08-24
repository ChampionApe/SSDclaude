# Superseded: the unanticipated-shock convention (pre 2026-08-24)

`US_shocks{,CommonX,_pinTheta}.csv` as produced before the new-path rewrite of `python/US/shocks.py`:
every counterfactual ran on `createCopyFromt0(2020)` seeded with the baseline's own savings, i.e. an
UNANTICIPATED permanent reform dated 2020. The live files instead solve a NEW EQUILIBRIUM PATH per
scenario -- the changed parameters hold over the whole 1960-2200 horizon, the economy starts from its
own steady state -- and read it at 2020.

At rho = 1 the two conventions give the SAME tau and savings rate to every printed digit (both are rate
objects independent of the inherited capital stock under LOG/Cobb-Douglas); only the workweek column
moves, because the level of hours responds to the wage and hence to k_2020. At rho != 1 tau moves too.

The live files also carry two rows these do not: all three French characteristics at once, and France's
own calibrated path.

Kept for the record only -- nothing reads them. See `notes/crossCuttingFindings.md` #8.
