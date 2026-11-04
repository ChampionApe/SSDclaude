# Overnight run of 2026-11-03: checks and readouts (checks.py)

## A. The cross-section, results/oecd26_retage/
```
   spec  turnout  layer ω rule retAge  rows  ok       LUX  nEq1  noFallback  onAnchor     ω̄   r(θ)
   none     cses      1   mean   exit    21  20 noTurnout  True        True      True 1.1425    NaN
   none     cses      1   mean   none    21  20 noTurnout  True        True      True 1.2697    NaN
   none     cses      1   mean    nra    21  20 noTurnout  True        True      True 1.1688    NaN
   none     cses      2 anchor   exit    21  20 noTurnout  True        True      True    NaN    NaN
   none     cses      2 anchor   none    21  20 noTurnout  True        True      True    NaN    NaN
   none     cses      2 anchor    nra    21  20 noTurnout  True        True      True    NaN    NaN
   none csesFlat      1   mean   exit    21  21        ok  True        True      True 1.1386    NaN
   none csesFlat      1   mean   none    21  21        ok  True        True      True 1.2910    NaN
   none csesFlat      1   mean    nra    21  21        ok  True        True      True 1.1711    NaN
   none csesFlat      2 anchor   exit    21  21        ok  True        True      True    NaN    NaN
   none csesFlat      2 anchor   none    21  21        ok  True        True      True    NaN    NaN
   none csesFlat      2 anchor    nra    21  21        ok  True        True      True    NaN    NaN
sizePiR     cses      1   mean   exit    21  20 noTurnout  True        True      True 1.1769 0.6878
sizePiR     cses      1   mean   none    21  20 noTurnout  True        True      True 1.3056 0.7354
sizePiR     cses      1   mean    nra    21  20 noTurnout  True        True      True 1.2029 0.7629
sizePiR     cses      2 anchor   exit    21  20 noTurnout  True        True      True    NaN 0.7942
sizePiR     cses      2 anchor   none    21  20 noTurnout  True        True      True    NaN 0.7945
sizePiR     cses      2 anchor    nra    21  20 noTurnout  True        True      True    NaN 0.7944
sizePiR csesFlat      1   mean   exit    21  21        ok  True        True      True 1.1715 0.6828
sizePiR csesFlat      1   mean   none    21  21        ok  True        True      True 1.3255 0.3622
sizePiR csesFlat      1   mean    nra    21  21        ok  True        True      True 1.2039 0.7218
sizePiR csesFlat      2 anchor   exit    21  21        ok  True        True      True    NaN 0.7736
sizePiR csesFlat      2 anchor   none    21  21        ok  True        True      True    NaN 0.7732
sizePiR csesFlat      2 anchor    nra    21  21        ok  True        True      True    NaN 0.7736
```

- OK   every reading present: {sizePiR, none} x {cses, csesFlat} x {layer 2, layer 1 at mean omega} x {none, exit, nra}
- OK   sizePiR cses layer 1 none: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   sizePiR cses layer 1 exit: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   sizePiR cses layer 1 nra: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   sizePiR cses layer 2 none: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   sizePiR cses layer 2 exit: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   sizePiR cses layer 2 nra: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   sizePiR csesFlat layer 1 none: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   sizePiR csesFlat layer 1 exit: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   sizePiR csesFlat layer 1 nra: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   sizePiR csesFlat layer 2 none: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   sizePiR csesFlat layer 2 exit: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   sizePiR csesFlat layer 2 nra: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   none cses layer 1 none: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   none cses layer 1 exit: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   none cses layer 1 nra: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   none cses layer 2 none: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   none cses layer 2 exit: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   none cses layer 2 nra: complete, one equilibrium, no fallback, on an ok anchor (20 ok of 21)
- OK   none csesFlat layer 1 none: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   none csesFlat layer 1 exit: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   none csesFlat layer 1 nra: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   none csesFlat layer 2 none: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   none csesFlat layer 2 exit: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   none csesFlat layer 2 nra: complete, one equilibrium, no fallback, on an ok anchor (21 ok of 21)
- OK   France's nu2020 under 'nra' is appendix F's 1.038558 (1.038558; none 1.156431, exit 0.836909)
- OK   the U.S. layer-2 row is the same under every retAge (its gap is 0) ({'none': {'ν2020': 1.3396678, 'ω': 1.2571771831158973, 'τ2020': 0.10522857142856698, 'θInForce': 0.544496000028011}, 'exit': {'ν2020': 1.3396678, 'ω': 1.2571771831158973, 'τ2020': 0.10522857142856698, 'θInForce': 0.544496000028011}, 'nra': {'ν2020': 1.3396678, 'ω': 1.2571771831158973, 'τ2020': 0.10522857142856698, 'θInForce': 0.544496000028011}})
- OK   the none cses anchor equals results/oecd26/'s (ω 1.191622 vs 1.191622)
- OK   the sizePiR cses anchor equals results/oecd26/'s (ω 1.257177 vs 1.257177)

## B1. France's and the UK's calibrations, nra (main tree) and exit (worktree)
### FR
```
           tree      X      ρ  residual  verify      β      ω     X̄      τ     sr      h           timestamp
     nra (main) vector 0.5000    0.0000  0.0000 1.0479 2.0552    NaN 0.2062 0.1260 0.6027 2026-10-30T18:19:54
     nra (main) vector 1.0000    0.0000  0.0000 0.6515 1.3923    NaN 0.2062 0.1239 0.6022 2026-10-30T18:18:48
     nra (main) vector 2.0000    0.0000  0.0000 0.5157 1.1786    NaN 0.2062 0.1221 0.6017 2026-10-30T18:19:18
     nra (main) common 0.5000    0.0000  0.0000 1.0479 2.0552 6.5126 0.2062 0.1260 0.6595 2026-10-30T18:26:29
     nra (main) common 1.0000    0.0000  0.0000 0.6515 1.3923 6.4841 0.2062 0.1239 0.6588 2026-10-30T18:23:40
     nra (main) common 2.0000    0.0000  0.0000 0.5157 1.1786 6.4555 0.2062 0.1221 0.6582 2026-10-30T18:25:12
exit (worktree) vector 0.5000    0.0000  0.0000 1.0479 1.4514    NaN 0.2062 0.1395 0.6027 2026-11-03T22:01:49
exit (worktree) vector 1.0000    0.0000  0.0000 0.6515 1.1220    NaN 0.2062 0.1229 0.6022 2026-11-03T22:01:00
exit (worktree) vector 2.0000    0.0000  0.0000 0.5157 1.0498    NaN 0.2062 0.1102 0.6017 2026-11-03T22:01:23
exit (worktree) common 0.5000    0.0000  0.0000 1.0479 1.4514 7.9035 0.2062 0.1395 0.6896 2026-11-03T22:02:43
exit (worktree) common 1.0000    0.0000  0.0000 0.6515 1.1220 7.3256 0.2062 0.1229 0.6777 2026-11-03T22:01:53
exit (worktree) common 2.0000    0.0000  0.0000 0.5157 1.0498 6.8728 0.2062 0.1102 0.6678 2026-11-03T22:02:17
```
- OK   the exit version has FR calibrated at 3 rho in both X variants tonight, residual below 1e-6 (6 rows)
nra (main): calibration summary FR [{'ρ': 1.0, 'commonX': False, 'ν2020': 1.0385583790202264, 'ω': 1.3922987272017682, 'X': nan, 'τ': 0.2062428571428572}, {'ρ': 1.0, 'commonX': True, 'ν2020': 1.0385583790202264, 'ω': 1.3922987272017686, 'X': 6.484075060636789, 'τ': 0.2062428571428571}]
exit (worktree): calibration summary FR [{'ρ': 1.0, 'commonX': False, 'ν2020': 0.8369091718814918, 'ω': 1.1219663702423357, 'X': nan, 'τ': 0.2062428571428572}, {'ρ': 1.0, 'commonX': True, 'ν2020': 0.8369091718814918, 'ω': 1.1219663702423357, 'X': 7.32559493546188, 'τ': 0.2062428571428571}]

### UK
```
           tree      X      ρ  residual  verify      β      ω     X̄      τ     sr      h           timestamp
     nra (main) vector 0.5000    0.0000  0.0002 1.0479 1.2417    NaN 0.1120 0.1710 0.5939 2026-10-30T18:21:04
     nra (main) vector 1.0000    0.0000  0.0000 0.6515 1.0416    NaN 0.1119 0.1596 0.5935 2026-10-30T18:19:59
     nra (main) vector 2.0000    0.0000  0.0000 0.5157 1.0090    NaN 0.1119 0.1510 0.5929 2026-10-30T18:20:32
     nra (main) common 0.5000    0.0000  0.0002 1.0479 1.2417 7.9477 0.1119 0.1710 0.6796 2026-10-30T18:27:38
     nra (main) common 1.0000    0.0000  0.0000 0.6515 1.0416 7.6686 0.1119 0.1596 0.6740 2026-10-30T18:26:42
     nra (main) common 2.0000    0.0000  0.0000 0.5157 1.0090 7.4688 0.1119 0.1510 0.6699 2026-10-30T18:27:11
exit (worktree) vector 0.5000    0.0000  0.0001 1.0479 1.0796    NaN 0.1119 0.1782 0.5939 2026-11-03T22:22:43
exit (worktree) vector 1.0000    0.0000  0.0000 0.6515 0.9536    NaN 0.1119 0.1597 0.5935 2026-11-03T22:21:29
exit (worktree) vector 2.0000    0.0000  0.0000 0.5157 0.9623    NaN 0.1120 0.1458 0.5929 2026-11-03T22:22:03
exit (worktree) common 0.5000    0.0000  0.0001 1.0479 1.0796 8.5491 0.1119 0.1781 0.6911 2026-11-03T22:24:02
exit (worktree) common 1.0000    0.0000  0.0000 0.6515 0.9536 8.0570 0.1119 0.1597 0.6817 2026-11-03T22:22:48
exit (worktree) common 2.0000    0.0000  0.0000 0.5157 0.9623 7.6880 0.1119 0.1458 0.6744 2026-11-03T22:23:18
```
- OK   the exit version has UK calibrated at 3 rho in both X variants tonight, residual below 1e-6 (6 rows)
nra (main): calibration summary UK [{'ρ': 1.0, 'commonX': False, 'ν2020': 1.1740347147676515, 'ω': 1.0416207830422035, 'X': nan, 'τ': 0.111942857142857}, {'ρ': 1.0, 'commonX': True, 'ν2020': 1.1740347147676515, 'ω': 1.0416207830422035, 'X': 7.66859145449842, 'τ': 0.1119428571428571}]
exit (worktree): calibration summary UK [{'ρ': 1.0, 'commonX': False, 'ν2020': 1.0748490490925484, 'ω': 0.953621808695428, 'X': nan, 'τ': 0.1119428571428572}, {'ρ': 1.0, 'commonX': True, 'ν2020': 1.0748490490925484, 'ω': 0.9536218086954276, 'X': 8.056959798174182, 'τ': 0.111942857142857}]


## B2. France- and UK-dependent outputs, nra against exit
- OK   US_shocksCommonX: the rows without France or the UK agree across the trees (max |diff| 0.0e+00 over 27 rows; 0 rows in one tree only)
```
     ρ family                   scenario effect  τ_nra  τ_exit  sr_nra  sr_exit  workweek_nra  workweek_exit  ω_nra  ω_exit
0.5000 french All French characteristics     ee 0.1052  0.1052  0.2266   0.2266       35.9967        34.4241    NaN     NaN
0.5000 french All French characteristics   full 0.0863  0.0863  0.2419   0.2419       36.5013        34.9067    NaN     NaN
0.5000 french   France (own calibration)   full 0.2062  0.2062  0.1801   0.1992       35.2402        35.2402 2.0552  1.4514
0.5000 french        Income distribution     ee 0.1052  0.1052  0.2266   0.2266       40.0826        40.0826    NaN     NaN
0.5000 french        Income distribution   full 0.0813  0.0813  0.2458   0.2458       40.7837        40.7837    NaN     NaN
0.5000 french        Leisure preferences     ee 0.1052  0.1052  0.2266   0.2266       35.3772        33.8316    NaN     NaN
0.5000 french        Leisure preferences   full 0.1052  0.1052  0.2266   0.2266       35.3779        33.8324    NaN     NaN
0.5000 french                     Voting     ee 0.1052  0.1052  0.2266   0.2266       39.3927        39.3927    NaN     NaN
0.5000 french                     Voting   full 0.1103  0.1103  0.2227   0.2227       39.2498        39.2498    NaN     NaN
1.0000 french All French characteristics     ee 0.1052  0.1052  0.2190   0.2190       36.0076        35.0078    NaN     NaN
1.0000 french All French characteristics   full 0.0958  0.0958  0.2238   0.2238       36.2033        35.1980    NaN     NaN
1.0000 french   France (own calibration)   full 0.2062  0.2062  0.1770   0.1755       35.2402        35.2402 1.3923  1.1220
1.0000 french        Income distribution     ee 0.1052  0.1052  0.2190   0.2190       40.0826        40.0826    NaN     NaN
1.0000 french        Income distribution   full 0.0851  0.0851  0.2296   0.2296       40.5462        40.5462    NaN     NaN
1.0000 french        Leisure preferences     ee 0.1052  0.1052  0.2190   0.2190       35.3879        34.4053    NaN     NaN
1.0000 french        Leisure preferences   full 0.1052  0.1052  0.2190   0.2190       35.3879        34.4053    NaN     NaN
1.0000 french                     Voting     ee 0.1052  0.1052  0.2190   0.2190       39.3927        39.3927    NaN     NaN
1.0000 french                     Voting   full 0.1197  0.1197  0.2116   0.2116       39.0648        39.0648    NaN     NaN
2.0000 french All French characteristics     ee 0.1052  0.1052  0.2118   0.2118       36.0112        35.4945    NaN     NaN
2.0000 french All French characteristics   full 0.1128  0.1128  0.2095   0.2095       35.8922        35.3772    NaN     NaN
2.0000 french   France (own calibration)   full 0.2062  0.2062  0.1744   0.1575       35.2402        35.2402 1.1786  1.0498
2.0000 french        Income distribution     ee 0.1052  0.1052  0.2118   0.2118       40.0826        40.0826    NaN     NaN
2.0000 french        Income distribution   full 0.0923  0.0923  0.2157   0.2157       40.3111        40.3111    NaN     NaN
2.0000 french        Leisure preferences     ee 0.1052  0.1052  0.2118   0.2118       35.3914        34.8836    NaN     NaN
2.0000 french        Leisure preferences   full 0.1052  0.1052  0.2118   0.2118       35.3911        34.8833    NaN     NaN
2.0000 french                     Voting     ee 0.1052  0.1052  0.2118   0.2118       39.3927        39.3927    NaN     NaN
2.0000 french                     Voting   full 0.1334  0.1334  0.2035   0.2035       38.9014        38.9014    NaN     NaN
```

- OK   US_shocks: the rows without France or the UK agree across the trees (max |diff| 1.1e-11 over 27 rows; 0 rows in one tree only)
```
     ρ family                   scenario effect  τ_nra  τ_exit  sr_nra  sr_exit  workweek_nra  workweek_exit  ω_nra  ω_exit
0.5000 french All French characteristics     ee 0.1052  0.1052  0.2266   0.2266       36.5437        34.9472    NaN     NaN
0.5000 french All French characteristics   full 0.0773  0.0773  0.2493   0.2493       37.2893        35.6592    NaN     NaN
0.5000 french   France (own calibration)   full 0.2062  0.2062  0.1801   0.1993       35.2403        35.2406 2.0552  1.4514
0.5000 french        Income distribution     ee 0.1052  0.1052  0.2266   0.2266       40.5210        40.5210    NaN     NaN
0.5000 french        Income distribution   full 0.0729  0.0729  0.2529   0.2529       41.4797        41.4797    NaN     NaN
0.5000 french        Leisure preferences     ee 0.1052  0.1052  0.2266   0.2266       35.5261        33.9741    NaN     NaN
0.5000 french        Leisure preferences   full 0.1052  0.1052  0.2266   0.2266       35.5268        33.9749    NaN     NaN
0.5000 french                     Voting     ee 0.1052  0.1052  0.2266   0.2266       39.3927        39.3927    NaN     NaN
0.5000 french                     Voting   full 0.1103  0.1103  0.2227   0.2227       39.2498        39.2498    NaN     NaN
1.0000 french All French characteristics     ee 0.1052  0.1052  0.2190   0.2190       36.5548        35.5397    NaN     NaN
1.0000 french All French characteristics   full 0.0874  0.0874  0.2283   0.2283       36.9301        35.9047    NaN     NaN
1.0000 french   France (own calibration)   full 0.2062  0.2062  0.1770   0.1755       35.2402        35.2402 1.3923  1.1220
1.0000 french        Income distribution     ee 0.1052  0.1052  0.2190   0.2190       40.5210        40.5210    NaN     NaN
1.0000 french        Income distribution   full 0.0782  0.0782  0.2333   0.2333       41.1478        41.1478    NaN     NaN
1.0000 french        Leisure preferences     ee 0.1052  0.1052  0.2190   0.2190       35.5369        34.5502    NaN     NaN
1.0000 french        Leisure preferences   full 0.1052  0.1052  0.2190   0.2190       35.5369        34.5502    NaN     NaN
1.0000 french                     Voting     ee 0.1052  0.1052  0.2190   0.2190       39.3927        39.3927    NaN     NaN
1.0000 french                     Voting   full 0.1197  0.1197  0.2116   0.2116       39.0648        39.0648    NaN     NaN
2.0000 french All French characteristics     ee 0.1052  0.1052  0.2118   0.2118       36.5584        36.0338    NaN     NaN
2.0000 french All French characteristics   full 0.1053  0.1053  0.2117   0.2117       36.5580        36.0334    NaN     NaN
2.0000 french   France (own calibration)   full 0.2062  0.2062  0.1744   0.1575       35.2403        35.2402 1.1786  1.0498
2.0000 french        Income distribution     ee 0.1052  0.1052  0.2118   0.2118       40.5210        40.5210    NaN     NaN
2.0000 french        Income distribution   full 0.0882  0.0882  0.2169   0.2169       40.8240        40.8240    NaN     NaN
2.0000 french        Leisure preferences     ee 0.1052  0.1052  0.2118   0.2118       35.5404        35.0304    NaN     NaN
2.0000 french        Leisure preferences   full 0.1052  0.1052  0.2118   0.2118       35.5402        35.0302    NaN     NaN
2.0000 french                     Voting     ee 0.1052  0.1052  0.2118   0.2118       39.3927        39.3927    NaN     NaN
2.0000 french                     Voting   full 0.1334  0.1334  0.2035   0.2035       38.9014        38.9014    NaN     NaN
```

- OK   US_shocksXiCommonX: the rows without France or the UK agree across the trees (max |diff| 0.0e+00 over 27 rows; 0 rows in one tree only)
```
     ξ      ρ family                   scenario effect  τ_nra  τ_exit  ω_nra  ω_exit
0.2000 1.0000 french All French characteristics     ee 0.1052  0.1052    NaN     NaN
0.2000 1.0000 french All French characteristics   full 0.0957  0.0957    NaN     NaN
0.2000 1.0000 french   France (own calibration)   full 0.2062  0.2062 1.2131  0.9775
0.2000 1.0000 french        Income distribution     ee 0.1052  0.1052    NaN     NaN
0.2000 1.0000 french        Income distribution   full 0.0848  0.0848    NaN     NaN
0.2000 1.0000 french        Leisure preferences     ee 0.1052  0.1052    NaN     NaN
0.2000 1.0000 french        Leisure preferences   full 0.1052  0.1052    NaN     NaN
0.2000 1.0000 french                     Voting     ee 0.1052  0.1052    NaN     NaN
0.2000 1.0000 french                     Voting   full 0.1199  0.1199    NaN     NaN
0.3000 1.0000 french All French characteristics     ee 0.1052  0.1052    NaN     NaN
0.3000 1.0000 french All French characteristics   full 0.0958  0.0958    NaN     NaN
0.3000 1.0000 french   France (own calibration)   full 0.2062  0.2062 1.3923  1.1220
0.3000 1.0000 french        Income distribution     ee 0.1052  0.1052    NaN     NaN
0.3000 1.0000 french        Income distribution   full 0.0851  0.0851    NaN     NaN
0.3000 1.0000 french        Leisure preferences     ee 0.1052  0.1052    NaN     NaN
0.3000 1.0000 french        Leisure preferences   full 0.1052  0.1052    NaN     NaN
0.3000 1.0000 french                     Voting     ee 0.1052  0.1052    NaN     NaN
0.3000 1.0000 french                     Voting   full 0.1197  0.1197    NaN     NaN
0.4000 1.0000 french All French characteristics     ee 0.1052  0.1052    NaN     NaN
0.4000 1.0000 french All French characteristics   full 0.0960  0.0960    NaN     NaN
0.4000 1.0000 french   France (own calibration)   full 0.2062  0.2062 1.5945  1.2849
0.4000 1.0000 french        Income distribution     ee 0.1052  0.1052    NaN     NaN
0.4000 1.0000 french        Income distribution   full 0.0853  0.0853    NaN     NaN
0.4000 1.0000 french        Leisure preferences     ee 0.1052  0.1052    NaN     NaN
0.4000 1.0000 french        Leisure preferences   full 0.1052  0.1052    NaN     NaN
0.4000 1.0000 french                     Voting     ee 0.1052  0.1052    NaN     NaN
0.4000 1.0000 french                     Voting   full 0.1196  0.1196    NaN     NaN
```

- OK   escCountry: the rows without France or the UK agree across the trees (max |diff| 0.0e+00 over 0 rows; 0 rows in one tree only)
```
 spec country wedgeFrom   p_nra  p_exit  θStar_nra  θStar_exit  choice_nra  choice_exit  ω_nra  ω_exit  τ_nra  τ_exit
scale      FR        US  0.2914  0.2914     0.8219      0.8219      0.7576       0.7585 1.4238  1.1474 0.2062  0.2062
scale      FR       own  0.3225  0.3220     0.8219      0.8219      0.8219       0.8219 1.4272  1.1500    NaN     NaN
scale      UK        US  0.2914  0.2914     0.1812      0.1812      0.8190       0.8186 1.2664  1.1594 0.1119  0.1119
scale      UK       own  0.0528  0.0529     0.1812      0.1812      0.1812       0.1812 1.0824  0.9910    NaN     NaN
 size      FR        US  6.2470  6.2470     0.8219      0.8219      0.6450       0.6455 1.4046  1.1319 0.2062  0.2062
 size      FR       own 13.5946 13.5741     0.8219      0.8219      0.8219       0.8219 1.4193  1.1437    NaN     NaN
 size      UK        US  6.2470  6.2470     0.1812      0.1812      0.4932       0.4930 1.1582  1.0603 0.1119  0.1119
 size      UK       own  3.6278  3.6300     0.1812      0.1812      0.1812       0.1812 1.1071  1.0136    NaN     NaN
```

- OK   the UK's own exact CRRA cost: the rows without France or the UK agree across the trees (max |diff| 0.0e+00 over 0 rows; 0 rows in one tree only)
```
     ρ spec host  p_nra  p_exit  θStar_nra  θStar_exit  β_nra  β_exit  ω_nra  ω_exit  residual_nra  residual_exit
0.5000 size   UK 7.5664  7.5130     0.1812      0.1812 1.0479  1.0479 1.4150  1.2282       -0.0000         0.0000
2.0000 size   UK 1.4550  1.4674     0.1812      0.1812 0.5157  0.5157 1.0344  0.9867        0.0000         0.0000
```

- OK   escPathHost: the rows without France or the UK agree across the trees (max |diff| 0.0e+00 over 0 rows; 0 rows in one tree only)
```
spec country wedgeFrom  date  ν_nra  ν_exit  θ_nra  θ_exit  τ_nra  τ_exit
size      FR        US  1960 1.0987  0.8803 0.8219  0.8219 0.1896  0.1913
size      FR        US  1990 1.0987  0.8803 0.6224  0.6254 0.1922  0.1938
size      FR        US  2020 1.0386  0.8369 0.6450  0.6455 0.2082  0.2082
size      FR        US  2050 0.9672  0.7609 0.6742  0.6814 0.2286  0.2355
size      FR        US  2080 0.9329  0.7367 0.6916  0.6995 0.2390  0.2448
size      FR        US  2110 0.9329  0.7367 0.6952  0.7028 0.2390  0.2448
size      FR        US  2140 0.9329  0.7367 0.6952  0.7028 0.2390  0.2448
size      FR        US  2170 0.9329  0.7367 0.6952  0.7028 0.2390  0.2448
size      FR       own  1960 1.0987  0.8803 0.8219  0.8219 0.1899  0.1915
size      FR       own  1990 1.0987  0.8803 0.8097  0.8110 0.1898  0.1915
size      FR       own  2020 1.0386  0.8369 0.8219  0.8219 0.2062  0.2062
size      FR       own  2050 0.9672  0.7609 0.8372  0.8408 0.2270  0.2340
size      FR       own  2080 0.9329  0.7367 0.8462  0.8501 0.2375  0.2434
size      FR       own  2110 0.9329  0.7367 0.8480  0.8517 0.2375  0.2434
size      FR       own  2140 0.9329  0.7367 0.8480  0.8517 0.2375  0.2434
size      FR       own  2170 0.9329  0.7367 0.8480  0.8517 0.2375  0.2434
size      UK        US  1960 1.0919  1.0029 0.1812  0.1812 0.1284  0.1277
size      UK        US  1990 1.0919  1.0029 0.5536  0.5510 0.1371  0.1362
size      UK        US  2020 1.1740  1.0748 0.4932  0.4930 0.1173  0.1173
size      UK        US  2050 1.1210  1.0285 0.5283  0.5266 0.1298  0.1292
size      UK        US  2080 1.0060  0.9270 0.6033  0.5995 0.1600  0.1582
size      UK        US  2110 1.0060  0.9270 0.6115  0.6074 0.1600  0.1582
size      UK        US  2140 1.0060  0.9270 0.6115  0.6074 0.1600  0.1582
size      UK        US  2170 1.0060  0.9270 0.6115  0.6074 0.1600  0.1582
size      UK       own  1960 1.0919  1.0029 0.1812  0.1812 0.1301  0.1293
size      UK       own  1990 1.0919  1.0029 0.2759  0.2722 0.1307  0.1299
size      UK       own  2020 1.1740  1.0748 0.1812  0.1812 0.1119  0.1119
size      UK       own  2050 1.1210  1.0285 0.2359  0.2337 0.1238  0.1233
size      UK       own  2080 1.0060  0.9270 0.3553  0.3495 0.1528  0.1510
size      UK       own  2110 1.0060  0.9270 0.3681  0.3618 0.1528  0.1510
size      UK       own  2140 1.0060  0.9270 0.3681  0.3618 0.1528  0.1510
size      UK       own  2170 1.0060  0.9270 0.3681  0.3618 0.1528  0.1510
```

- OK   escShocks (LOG): the rows without France or the UK agree across the trees (max |diff| 1.4e-14 over 14 rows; 0 rows in one tree only)
```
 spec  scenario  θpinned  θ_t0_nra  θ_t0_exit  θ_t1_nra  θ_t1_exit  τ_t0_nra  τ_t0_exit  ww_t0_nra  ww_t0_exit
scale     frAll    False    0.7140     0.7140    0.7163     0.7163    0.0957     0.0957    36.2911     35.2834
scale     frAll     True    0.5445     0.5445    0.5445     0.5445    0.0953     0.0953    36.1775     35.1729
scale    frBoth    False    0.7140     0.7140    0.7163     0.7163    0.0957     0.0957    40.4376     40.4376
scale    frBoth     True    0.5445     0.5445    0.5445     0.5445    0.0953     0.0953    40.3110     40.3110
scale  frIncome    False    1.0000     1.0000    1.0000     1.0000    0.0912     0.0912    40.7833     40.7833
scale  frIncome     True    0.5445     0.5445    0.5445     0.5445    0.0839     0.0839    40.5665     40.5665
scale frLeisure    False    0.5445     0.5445    0.5552     0.5552    0.1052     0.1052    35.3623     34.3804
scale frLeisure     True    0.5445     0.5445    0.5445     0.5445    0.1052     0.1052    35.3534     34.3717
scale  frVoting    False    0.3937     0.3937    0.3988     0.3988    0.1240     0.1240    38.8673     38.8673
scale  frVoting     True    0.5445     0.5445    0.5445     0.5445    0.1205     0.1205    39.0520     39.0520
 size     frAll    False    0.3558     0.3558    0.5221     0.5221    0.1054     0.1054    35.9753     34.9764
 size     frAll     True    0.5445     0.5445    0.5445     0.5445    0.1046     0.1046    36.0013     35.0016
 size    frBoth    False    0.3558     0.3558    0.5221     0.5221    0.1054     0.1054    40.0862     40.0862
 size    frBoth     True    0.5445     0.5445    0.5445     0.5445    0.1046     0.1046    40.1151     40.1151
 size  frIncome    False    0.5568     0.5568    0.6908     0.6908    0.0946     0.0946    40.4792     40.4792
 size  frIncome     True    0.5445     0.5445    0.5445     0.5445    0.0946     0.0946    40.3439     40.3439
 size frLeisure    False    0.5445     0.5445    0.6617     0.6617    0.1052     0.1052    35.4594     34.4748
 size frLeisure     True    0.5445     0.5445    0.5445     0.5445    0.1052     0.1052    35.3530     34.3713
 size  frVoting    False    0.4461     0.4461    0.5664     0.5664    0.1177     0.1177    39.1469     39.1469
 size  frVoting     True    0.5445     0.5445    0.5445     0.5445    0.1179     0.1179    39.1098     39.1098
```

- OK   escShocksCRRA (exact): the rows without France or the UK agree across the trees (max |diff| 8.8e-14 over 10 rows; 0 rows in one tree only)
```
     ρ spec  scenario  θpinned  θ_t0_nra  θ_t0_exit  θ_t1_nra  θ_t1_exit  τ_t0_nra  τ_t0_exit
0.5000 size     frAll    False    0.4253     0.4253    0.5792     0.5792    0.0990     0.0990
0.5000 size     frAll     True    0.5445     0.5445    0.5445     0.5445    0.0992     0.0992
0.5000 size    frBoth    False    0.4254     0.4254    0.5792     0.5792    0.0990     0.0990
0.5000 size    frBoth     True    0.5445     0.5445    0.5445     0.5445    0.0992     0.0992
0.5000 size  frIncome    False    0.4834     0.4834    0.6312     0.6312    0.0948     0.0948
0.5000 size  frIncome     True    0.5445     0.5445    0.5445     0.5445    0.0951     0.0951
0.5000 size frLeisure    False    0.5445     0.5445    0.6541     0.6541    0.1053     0.1053
0.5000 size frLeisure     True    0.5445     0.5445    0.5445     0.5445    0.1052     0.1052
0.5000 size  frVoting    False    0.5190     0.5190    0.6295     0.6295    0.1090     0.1090
0.5000 size  frVoting     True    0.5445     0.5445    0.5445     0.5445    0.1094     0.1094
2.0000 size     frAll    False    0.0000     0.0000    0.1685     0.1685    0.1211     0.1211
2.0000 size     frAll     True    0.5445     0.5445    0.5445     0.5445    0.1157     0.1157
2.0000 size    frBoth    False    0.0000     0.0000    0.1685     0.1685    0.1211     0.1211
2.0000 size    frBoth     True    0.5445     0.5445    0.5445     0.5445    0.1157     0.1157
2.0000 size  frIncome    False    0.8461     0.8461    0.8932     0.8932    0.0995     0.0995
2.0000 size  frIncome     True    0.5445     0.5445    0.5445     0.5445    0.0959     0.0959
2.0000 size frLeisure    False    0.5445     0.5445    0.6632     0.6632    0.1060     0.1060
2.0000 size frLeisure     True    0.5445     0.5445    0.5445     0.5445    0.1052     0.1052
2.0000 size  frVoting    False    0.0852     0.0852    0.2440     0.2440    0.1380     0.1380
2.0000 size  frVoting     True    0.5445     0.5445    0.5445     0.5445    0.1318     0.1318
```

### C5_designDecomp.csv
```
  kind      ρ                                        case experiment  route                       piece  value_nra  value_exit  θ2020_nra  θ2020_exit  θ2020FR_nra  θ2020FR_exit
choice 1.0000            FR (pi = 1, reproduces frIncome)         FR    NaN                         NaN        NaN         NaN     0.5568      0.5568          NaN           NaN
choice 1.0000 FR, cost at the U.S. size (pi = tau^US/tau)         X1    NaN                         NaN        NaN         NaN     0.5959      0.5959          NaN           NaN
choice 1.0000    FR, cost at the U.S. size and dispersion         X2    NaN                         NaN        NaN         NaN     0.7835      0.7835          NaN           NaN
choice 1.0000   FR, tax function solved at each candidate   FRexactT    NaN                         NaN        NaN         NaN     0.5568      0.5568          NaN           NaN
choice 1.0000                                        U.S.         US    NaN                         NaN        NaN         NaN     0.5445      0.5445          NaN           NaN
choice 1.0000         U.S., cost at the French dispersion         X3    NaN                         NaN        NaN         NaN     0.2668      0.2668          NaN           NaN
choice 1.0000   US, tax function solved at each candidate   USexactT    NaN                         NaN        NaN         NaN     0.5445      0.5445          NaN           NaN
   foc 1.0000                                          FR        NaN   cost                           W     0.0074      0.0074        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN   cost            old: labor stake     0.0002      0.0002        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN   cost              young: R_{t+1}     0.0024      0.0024        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN   cost                young: hours     0.0025      0.0025        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN   cost young: pension and earnings     0.0024      0.0024        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN design                           W    -0.0099     -0.0099        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN design            old: labor stake     0.0076      0.0076        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN design              young: R_{t+1}     0.0022      0.0022        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN design                young: hours     0.0877      0.0877        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN design young: pension and earnings    -0.1074     -0.1074        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN    tax                           W     0.0039      0.0039        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN    tax            old: labor stake     0.0001      0.0001        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN    tax              young: R_{t+1}     0.0010      0.0010        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN    tax                young: hours     0.0014      0.0014        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN    tax young: pension and earnings     0.0013      0.0013        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN  total                           W     0.0015      0.0015        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN  total            old: labor stake     0.0080      0.0080        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN  total              young: R_{t+1}     0.0056      0.0056        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN  total                young: hours     0.0916      0.0916        NaN         NaN          NaN           NaN
   foc 1.0000                                          FR        NaN  total young: pension and earnings    -0.1037     -0.1037        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN   cost                           W     0.0184      0.0184        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN   cost            old: labor stake     0.0005      0.0005        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN   cost              young: R_{t+1}     0.0057      0.0057        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN   cost                young: hours     0.0059      0.0059        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN   cost young: pension and earnings     0.0063      0.0063        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN design                           W    -0.0267     -0.0267        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN design            old: labor stake     0.0082      0.0082        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN design              young: R_{t+1}     0.0024      0.0024        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN design                young: hours     0.0946      0.0946        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN design young: pension and earnings    -0.1319     -0.1319        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN    tax                           W     0.0083      0.0083        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN    tax            old: labor stake     0.0003      0.0003        NaN         NaN          NaN           NaN
   foc 1.0000                                          US        NaN    tax              young: R_{t+1}     0.0020      0.0020        NaN         NaN          NaN           NaN
```

### C5_designDecompCRRA_rho0.5.csv
```
  kind      ρ                                        case experiment  θ2020_nra  θ2020_exit
choice 0.5000 FR, cost at the U.S. size (pi = tau^US/tau)         X1     0.5284      0.5284
choice 0.5000    FR, cost at the U.S. size and dispersion         X2     0.7441      0.7429
```

### C5_designDecompCRRA_rho2.csv
```
  kind      ρ                                        case experiment  θ2020_nra  θ2020_exit
choice 2.0000 FR, cost at the U.S. size (pi = tau^US/tau)         X1     0.8535      0.8535
choice 2.0000    FR, cost at the U.S. size and dispersion         X2     0.9154      0.9154
```


All checks passed.
