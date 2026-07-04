# B2.3 Step E — Concentration / Hubness Exploratory Diagnostic

This diagnostic reads true coordinates and is not learner-path code.
It is explanatory, not a preregistered pass/fail gate.

## Summary correlations

| n | corr(paired separation, distance CV) | corr(paired separation, hubness skew k=15) | crossover d in included B2.3 metrics |
|---:|---:|---:|---:|
| 1000 | 0.7056565007018698 | -0.560417318796962 | 130 |
| 5000 | 0.7946271079463642 | -0.8689803133236677 | 24 |

## Cell table

| n | d | source | paired separation | distance CV | hubness skew k=15 | max indegree k=15 | zero indegree fraction k=15 |
|---:|---:|---|---:|---:|---:|---:|---:|
| 1000 | 6 | core_b2_3_final_grid | 1.0 | 0.25480 | 0.25584 | 33.25 | 0.00005 |
| 1000 | 8 | core_b2_3_final_grid | 1.0 | 0.21796 | 0.60114 | 40.60 | 0.00035 |
| 1000 | 9 | dense_d_8_30_diagnostic_grid | 1.0 | 0.20437 | 0.73729 | 44.10 | 0.00050 |
| 1000 | 10 | core_b2_3_final_grid | 1.0 | 0.19350 | 0.96072 | 50.70 | 0.00095 |
| 1000 | 11 | dense_d_8_30_diagnostic_grid | 1.0 | 0.18366 | 1.09572 | 54.75 | 0.00095 |
| 1000 | 12 | core_b2_3_final_grid | 1.0 | 0.17544 | 1.18516 | 61.95 | 0.00115 |
| 1000 | 13 | dense_d_8_30_diagnostic_grid | 1.0 | 0.16852 | 1.37542 | 66.60 | 0.00145 |
| 1000 | 14 | dense_d_8_30_diagnostic_grid | 1.0 | 0.16240 | 1.52163 | 73.15 | 0.00210 |
| 1000 | 15 | dense_d_8_30_diagnostic_grid | 1.0 | 0.15634 | 1.56430 | 75.95 | 0.00255 |
| 1000 | 16 | dense_d_8_30_diagnostic_grid | 1.0 | 0.15107 | 1.70551 | 80.90 | 0.00290 |
| 1000 | 17 | dense_d_8_30_diagnostic_grid | 1.0 | 0.14644 | 1.80330 | 85.85 | 0.00305 |
| 1000 | 18 | dense_d_8_30_diagnostic_grid | 1.0 | 0.14221 | 1.82800 | 85.80 | 0.00300 |
| 1000 | 19 | dense_d_8_30_diagnostic_grid | 1.0 | 0.13831 | 2.02450 | 93.00 | 0.00420 |
| 1000 | 20 | core_b2_3_final_grid | 1.0 | 0.13459 | 1.96402 | 95.10 | 0.00420 |
| 1000 | 21 | dense_d_8_30_diagnostic_grid | 1.0 | 0.13140 | 2.21145 | 105.10 | 0.00295 |
| 1000 | 22 | dense_d_8_30_diagnostic_grid | 1.0 | 0.12818 | 2.17475 | 106.20 | 0.00500 |
| 1000 | 23 | dense_d_8_30_diagnostic_grid | 1.0 | 0.12518 | 2.16188 | 106.05 | 0.00540 |
| 1000 | 24 | dense_d_8_30_diagnostic_grid | 1.0 | 0.12234 | 2.15758 | 108.50 | 0.00515 |
| 1000 | 25 | dense_d_8_30_diagnostic_grid | 1.0 | 0.12002 | 2.30184 | 110.30 | 0.00610 |
| 1000 | 26 | dense_d_8_30_diagnostic_grid | 1.0 | 0.11743 | 2.59068 | 124.60 | 0.00570 |
| 1000 | 27 | dense_d_8_30_diagnostic_grid | 1.0 | 0.11514 | 2.26313 | 106.60 | 0.00675 |
| 1000 | 28 | dense_d_8_30_diagnostic_grid | 1.0 | 0.11327 | 2.52674 | 120.05 | 0.00680 |
| 1000 | 29 | dense_d_8_30_diagnostic_grid | 1.0 | 0.11114 | 2.66503 | 124.90 | 0.00730 |
| 1000 | 30 | dense_d_8_30_diagnostic_grid | 1.0 | 0.10927 | 2.33561 | 113.00 | 0.00705 |
| 1000 | 32 | exploratory_cross_n_focus_addition |  | 0.10557 | 2.33403 | 113.95 | 0.00780 |
| 1000 | 34 | exploratory_cross_n_focus_addition |  | 0.10244 | 2.43625 | 119.35 | 0.00755 |
| 1000 | 36 | exploratory_cross_n_focus_addition |  | 0.09931 | 2.41446 | 115.00 | 0.00840 |
| 1000 | 38 | exploratory_cross_n_focus_addition |  | 0.09683 | 2.48364 | 124.85 | 0.00835 |
| 1000 | 40 | core_b2_3_final_grid | 1.0 | 0.09416 | 2.54069 | 123.30 | 0.00855 |
| 1000 | 60 | core_b2_3_final_grid | 1.0 | 0.07670 | 2.72099 | 133.95 | 0.01545 |
| 1000 | 80 | core_b2_3_final_grid | 1.0 | 0.06636 | 2.69349 | 137.60 | 0.01795 |
| 1000 | 100 | core_b2_3_final_grid | 0.9 | 0.05929 | 2.82324 | 144.00 | 0.01900 |
| 1000 | 120 | core_b2_3_final_grid | 0.7 | 0.05405 | 2.90095 | 153.85 | 0.02310 |
| 1000 | 129 | core_b2_3_final_grid | 0.6 | 0.05213 | 2.73651 | 141.55 | 0.02400 |
| 1000 | 130 | core_b2_3_final_grid | 0.48 | 0.05184 | 2.90225 | 153.95 | 0.02475 |
| 1000 | 131 | core_b2_3_final_grid | 0.48 | 0.05176 | 2.73158 | 139.65 | 0.02335 |
| 1000 | 140 | core_b2_3_final_grid | 0.4 | 0.05005 | 2.96874 | 155.95 | 0.02275 |
| 1000 | 150 | core_b2_3_final_grid | 0.3 | 0.04830 | 2.84789 | 149.05 | 0.02610 |
| 1000 | 160 | core_b2_3_final_grid | 0.2 | 0.04684 | 2.92191 | 148.95 | 0.02555 |
| 1000 | 170 | core_b2_3_final_grid | 0.2 | 0.04538 | 2.88876 | 151.20 | 0.02650 |
| 1000 | 180 | core_b2_3_final_grid | 0.05 | 0.04407 | 2.71285 | 143.10 | 0.02790 |
| 1000 | 200 | core_b2_3_final_grid | 0.05 | 0.04176 | 2.95001 | 156.25 | 0.02615 |
| 5000 | 6 | core_b2_3_final_grid | 1.0 | 0.25510 | 0.18190 | 33.70 | 0.00005 |
| 5000 | 8 | core_b2_3_final_grid | 1.0 | 0.21808 | 0.35728 | 37.15 | 0.00022 |
| 5000 | 9 | dense_d_8_30_diagnostic_grid | 1.0 | 0.20460 | 0.46940 | 40.90 | 0.00027 |
| 5000 | 10 | core_b2_3_final_grid | 1.0 | 0.19360 | 0.59140 | 43.50 | 0.00044 |
| 5000 | 11 | dense_d_8_30_diagnostic_grid | 1.0 | 0.18389 | 0.72739 | 46.90 | 0.00067 |
| 5000 | 12 | core_b2_3_final_grid | 1.0 | 0.17557 | 0.87846 | 53.30 | 0.00087 |
| 5000 | 13 | dense_d_8_30_diagnostic_grid | 1.0 | 0.16847 | 1.00722 | 58.55 | 0.00129 |
| 5000 | 14 | dense_d_8_30_diagnostic_grid | 1.0 | 0.16208 | 1.18284 | 64.65 | 0.00174 |
| 5000 | 15 | dense_d_8_30_diagnostic_grid | 1.0 | 0.15632 | 1.32414 | 74.85 | 0.00199 |
| 5000 | 16 | dense_d_8_30_diagnostic_grid | 1.0 | 0.15117 | 1.48177 | 78.85 | 0.00256 |
| 5000 | 17 | dense_d_8_30_diagnostic_grid | 1.0 | 0.14639 | 1.63992 | 92.45 | 0.00278 |
| 5000 | 18 | dense_d_8_30_diagnostic_grid | 1.0 | 0.14223 | 1.74338 | 101.45 | 0.00312 |
| 5000 | 19 | dense_d_8_30_diagnostic_grid | 1.0 | 0.13839 | 1.87749 | 108.45 | 0.00409 |
| 5000 | 20 | core_b2_3_final_grid | 1.0 | 0.13466 | 1.93022 | 110.95 | 0.00455 |
| 5000 | 21 | dense_d_8_30_diagnostic_grid | 1.0 | 0.13130 | 2.12435 | 123.30 | 0.00526 |
| 5000 | 22 | dense_d_8_30_diagnostic_grid | 0.9 | 0.12815 | 2.14758 | 121.60 | 0.00550 |
| 5000 | 23 | dense_d_8_30_diagnostic_grid | 0.8 | 0.12524 | 2.24217 | 134.15 | 0.00595 |
| 5000 | 24 | core_b2_3_final_grid | 0.36 | 0.12256 | 2.38798 | 145.70 | 0.00669 |
| 5000 | 25 | core_b2_3_final_grid | 0.04 | 0.11997 | 2.45883 | 148.90 | 0.00756 |
| 5000 | 26 | core_b2_3_final_grid | 0.0 | 0.11759 | 2.63348 | 165.85 | 0.00700 |
| 5000 | 27 | dense_d_8_30_diagnostic_grid | 0.0 | 0.11535 | 2.64952 | 163.25 | 0.00836 |
| 5000 | 28 | dense_d_8_30_diagnostic_grid | 0.0 | 0.11328 | 2.77551 | 171.60 | 0.00902 |
| 5000 | 29 | dense_d_8_30_diagnostic_grid | 0.0 | 0.11123 | 2.96295 | 188.65 | 0.00936 |
| 5000 | 30 | core_b2_3_final_grid | 0.0 | 0.10928 | 2.76316 | 166.95 | 0.00953 |
| 5000 | 32 | core_b2_3_final_grid | 0.0 | 0.10576 | 2.82033 | 176.45 | 0.01080 |
| 5000 | 34 | core_b2_3_final_grid | 0.0 | 0.10257 | 2.99087 | 191.45 | 0.01188 |
| 5000 | 36 | core_b2_3_final_grid | 0.0 | 0.09956 | 2.95559 | 184.40 | 0.01276 |
| 5000 | 38 | core_b2_3_final_grid | 0.0 | 0.09693 | 3.02565 | 186.35 | 0.01460 |
| 5000 | 40 | core_b2_3_final_grid | 0.0 | 0.09435 | 3.27170 | 215.85 | 0.01542 |
| 5000 | 42 | core_b2_3_final_grid | 0.0 | 0.09209 | 3.17259 | 200.15 | 0.01558 |
| 5000 | 45 | core_b2_3_final_grid | 0.0 | 0.08892 | 3.59151 | 239.50 | 0.01773 |
| 5000 | 50 | core_b2_3_final_grid | 0.0 | 0.08425 | 3.43952 | 227.95 | 0.02003 |
| 5000 | 60 | core_b2_3_final_grid | 0.0 | 0.07688 | 3.50078 | 230.05 | 0.02361 |
| 5000 | 80 | core_b2_3_final_grid | 0.0 | 0.06645 | 3.69178 | 258.60 | 0.02920 |
| 5000 | 100 | core_b2_3_final_grid | 0.0 | 0.05937 | 4.10840 | 290.80 | 0.03520 |
| 5000 | 120 | exploratory_cross_n_focus_addition |  | 0.05416 | 4.03609 | 291.40 | 0.03907 |
| 5000 | 129 | exploratory_cross_n_focus_addition |  | 0.05224 | 3.94345 | 281.60 | 0.04064 |
| 5000 | 130 | exploratory_cross_n_focus_addition |  | 0.05196 | 4.07100 | 284.15 | 0.03978 |
| 5000 | 131 | exploratory_cross_n_focus_addition |  | 0.05184 | 4.35031 | 314.95 | 0.04059 |
| 5000 | 140 | exploratory_cross_n_focus_addition |  | 0.05008 | 4.14968 | 299.85 | 0.04199 |

## Interpretation guard
No substrate, theorem-confirmation, dimension-accuracy, or real-world transfer claim is made.
