# B2.3 — Discrimination Crossover Mapping

## 0. Verdict

Decision: `B2.3-PASS-DISCRIMINATION-CROSSOVER-MAPPED`.

B2.3 tests whether the finite-sample discrimination boundary shifts with n in the direction suggested by asymptotic consistency, not whether the theorem is confirmed. B2.3 does not estimate the dimension-accuracy boundary; it estimates the random-control discrimination boundary for the uniform hypercube family under the already-validated E_CAP+k-spread diagnostic.

## 1. Step 0 closure

Leakage scanner confirmation: `passed=True`.
The B2.2.1 leakage check scans only estimator-facing functions:
`e_cap, e_dp, l_cap_local, l_dp_local, _ball1, learner_view`.
It does not scan `world_generator.py`.

The random-graph k-spread value in the B2.2.1 decision was sourced from the
sanity path, not from a final 20-seed recalculation. Recomputing the control on
the final B2.2.1 seed floor gave k-spread
`3.700`,
matching the decision value.

## 2. Random-control mechanism

For directed random k-out graph, B_SP(i,1)={i}+N_i. For edge i->j, B_SP(i,1)∩B_SP(j,1) always contains j. It equals 1 iff N_j avoids the k forbidden vertices {i}∪(N_i\{j}), with exact probability prod_{r=0}^{k-1}(n-1-k-r)/(n-1-r). L_CAP uses the min over k out-edges, so P(min intersection=1)≈1-(1-p)^k. Thus random k-out has L_CAP≈1/(k+1), making E_CAP rise with k and producing large k-spread.

This independently explains why the random k-out control mimics high-dimensional
geometry in k-spread: for k=10,15,20 the min-over-neighbors term is very likely
to be one shared vertex only, yielding E_CAP values close to the B2.2.1 empirical
sequence 9.40, 11.50, 13.10.

## 3. Preregistration

`PREREG.json` was written before the final sweep. Primary metric:
`paired_separation(d,n)=P(k_spread_random(n,s)-k_spread_geo(d,n,s)>epsilon)`.
Epsilon was fixed at `0.5` from the sanity margin scale. The required
d={6,8,10,12} sanity points did not bracket crossover, so the final grid was
widened while preserving the uniform-hypercube family.

## 4. Full d x n table

| n | d | N | paired_separation | Wilson 95% CI | geo_stability | control_rejection | mean_geo_k_spread | mean_random_k_spread | mean_margin |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 1000 | 6 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 0.790 | 3.700 | 2.910 |
| 1000 | 8 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 1.020 | 3.700 | 2.680 |
| 1000 | 10 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 1.175 | 3.700 | 2.525 |
| 1000 | 12 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 1.330 | 3.700 | 2.370 |
| 1000 | 20 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 1.855 | 3.700 | 1.845 |
| 1000 | 40 | 20 | 1.000 | [0.839, 1.000] | 0.350 | 1.000 | 2.505 | 3.700 | 1.195 |
| 1000 | 60 | 20 | 1.000 | [0.839, 1.000] | 0.000 | 1.000 | 2.795 | 3.700 | 0.905 |
| 1000 | 80 | 20 | 1.000 | [0.839, 1.000] | 0.000 | 1.000 | 2.965 | 3.700 | 0.735 |
| 1000 | 100 | 20 | 0.900 | [0.699, 0.972] | 0.000 | 1.000 | 3.060 | 3.700 | 0.640 |
| 1000 | 120 | 20 | 0.700 | [0.481, 0.855] | 0.000 | 1.000 | 3.100 | 3.700 | 0.600 |
| 1000 | 129 | 50 | 0.600 | [0.462, 0.724] | 0.000 | 1.000 | 3.134 | 3.700 | 0.566 |
| 1000 | 130 | 50 | 0.480 | [0.348, 0.615] | 0.000 | 1.000 | 3.144 | 3.700 | 0.556 |
| 1000 | 131 | 50 | 0.480 | [0.348, 0.615] | 0.000 | 1.000 | 3.148 | 3.700 | 0.552 |
| 1000 | 140 | 20 | 0.400 | [0.219, 0.613] | 0.000 | 1.000 | 3.155 | 3.700 | 0.545 |
| 1000 | 150 | 20 | 0.300 | [0.145, 0.519] | 0.000 | 1.000 | 3.195 | 3.700 | 0.505 |
| 1000 | 160 | 20 | 0.200 | [0.081, 0.416] | 0.000 | 1.000 | 3.220 | 3.700 | 0.480 |
| 1000 | 170 | 20 | 0.200 | [0.081, 0.416] | 0.000 | 1.000 | 3.235 | 3.700 | 0.465 |
| 1000 | 180 | 20 | 0.050 | [0.009, 0.236] | 0.000 | 1.000 | 3.255 | 3.700 | 0.445 |
| 1000 | 200 | 20 | 0.050 | [0.009, 0.236] | 0.000 | 1.000 | 3.250 | 3.700 | 0.450 |
| 5000 | 6 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 1.035 | 3.700 | 2.665 |
| 5000 | 8 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 1.420 | 3.700 | 2.280 |
| 5000 | 10 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 1.805 | 3.700 | 1.895 |
| 5000 | 12 | 20 | 1.000 | [0.839, 1.000] | 1.000 | 1.000 | 2.055 | 3.700 | 1.645 |
| 5000 | 20 | 20 | 1.000 | [0.839, 1.000] | 0.000 | 1.000 | 2.945 | 3.700 | 0.755 |
| 5000 | 24 | 50 | 0.360 | [0.241, 0.499] | 0.000 | 1.000 | 3.168 | 3.700 | 0.532 |
| 5000 | 25 | 50 | 0.040 | [0.011, 0.135] | 0.000 | 1.000 | 3.210 | 3.700 | 0.490 |
| 5000 | 26 | 50 | 0.000 | [0.000, 0.071] | 0.000 | 1.000 | 3.260 | 3.700 | 0.440 |
| 5000 | 30 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.385 | 3.700 | 0.315 |
| 5000 | 32 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.430 | 3.700 | 0.270 |
| 5000 | 34 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.495 | 3.700 | 0.205 |
| 5000 | 36 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.495 | 3.700 | 0.205 |
| 5000 | 38 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.520 | 3.700 | 0.180 |
| 5000 | 40 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.575 | 3.700 | 0.125 |
| 5000 | 42 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.575 | 3.700 | 0.125 |
| 5000 | 45 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.585 | 3.700 | 0.115 |
| 5000 | 50 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.615 | 3.700 | 0.085 |
| 5000 | 60 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.660 | 3.700 | 0.040 |
| 5000 | 80 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.700 | 3.700 | -0.000 |
| 5000 | 100 | 20 | 0.000 | [0.000, 0.161] | 0.000 | 1.000 | 3.715 | 3.700 | -0.015 |

## 5. Crossover

`d*(n=1000) = 130`.

`d*(n=5000) = 24`.

Shift `d*(5000)-d*(1000) = -106`.
Right shift with n observed: `False`.

Monotonicity is reported without smoothing:

- n=1000 monotone nonincreasing: `True`
- n=5000 monotone nonincreasing: `True`

## 6. Claim boundary

This is a discrimination-boundary result only. It is not an E_CAP
dimension-accuracy boundary.

This result rejects tautology only with respect to the preregistered random k-out graph control. It does not establish that the estimator cannot be fooled by other non-geometric graph families.

Not tested against: small-world graphs, scale-free graphs, other non-Euclidean
structured graphs.

## 7. Verification

`python3 -m gate_harness.verify_decision gate_harness_experiments/B2_3/decision.json`
returned code `0`.

This B2.3 artifact is not harness-signed because the current harness requires a
strict two-commit preregistration lock before `run_gate` will write a citable
decision. The local decision is therefore JSON-valid and reproducible, but not
valid by the existing `verify_decision` provenance checker.

## 8. What was NOT shown

- No substrate was found.
- No derived world-model was shown.
- No LLM training was run or allowed.
- No internet data or natural language corpus was used.
- No claim that E_CAP is dimension-accurate outside literature-supported d rows.
- No claim that the theorem is confirmed.
- No claim that random-control discrimination transfers to other graph families.
- No claim that passing B2.3 proves the project goal.
