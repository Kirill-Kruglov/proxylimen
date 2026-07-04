# RESULTS_CANONICAL.md — Ascesis Canonical Results Registry

This file is the canonical registry for essay claims. Any essay statement must be no stronger than the claim recorded here. Every numeric value below is copied from a named repository file with that file's last commit hash. If a requested number is not present in a committed artifact, this file says so instead of reconstructing it.

Verification baseline at time of writing: `python3 -m gate_harness.verify_decision experiments/B/B1_harness_rerun/decision.json experiments/B/B2_harness_rerun/decision.json gate_harness_experiments/B2_2_1/decision.json gate_harness_experiments/B2_3/decision.json` returns `VALID` for all four. Legacy pre-harness B1/B2.1 decisions return `INVALID` because they lack `_harness_provenance`.

## 1. Established Positive Results

### 1.1 Auxiliary Calibration Recovery

**Claim at allowed strength.** In the bounded synthetic scalar B1 world, auxiliary calibration through anchor overlaps recovers the latent scalar under the harnessed multi-seed rerun, while no-auxiliary and broken-calibration controls fail under the preregistered thresholds. This is a toy identifiability signal, not a real-world disentanglement result.

Source: `experiments/B/B1_harness_rerun/decision.json` @ `8ccefba`; prereg thresholds in `experiments/B/B1_harness_rerun/PREREG.json` @ `93456a6`.

Key values:

| quantity | value | source |
|---|---:|---|
| decision | `B1-PASS-AUXILIARY-IDENTIFIABILITY` | `decision.json` @ `8ccefba`, key `decision` |
| seed count | `24` | `decision.json` @ `8ccefba`, key `seed_count` |
| minimum core seeds | `20` | `decision.json` @ `8ccefba`, key `seed_policy.per_metric.recovery_pearson_corr.min_required` |
| mean no-aux absolute correlation | `0.20851995111223512` | `decision.json` @ `8ccefba`, key `recovery.mean_no_aux_abs_corr` |
| mean with-aux correlation | `0.9999661041760123` | `decision.json` @ `8ccefba`, key `recovery.mean_with_aux_corr` |
| mean improvement | `0.791446153063777` | `decision.json` @ `8ccefba`, key `recovery.mean_improvement` |
| shuffled auxiliary control correlation | `0.23254348554400373` | `decision.json` @ `8ccefba`, key `controls.shuffled_aux_corr.value` |
| no-anchor control correlation | `0.23254348554400373` | `decision.json` @ `8ccefba`, key `controls.no_anchor_with_aux_corr.value` |
| random-world control correlation | `0.005953949876847943` | `decision.json` @ `8ccefba`, key `controls.random_world_corr.value` |
| information ratio | `0.04697540404970473` | `decision.json` @ `8ccefba`, key `information_ratio` |
| information-ratio minimum threshold | `0.5` | `decision.json` @ `8ccefba`, key `thresholds.information_ratio_min`; also `PREREG.json` @ `93456a6` |
| construction may be tautological | `true` | `decision.json` @ `8ccefba`, key `construction_may_be_tautological` |
| harness hint dependence | `false` | `decision.json` @ `8ccefba`, key `classification_success_depends_on_harness_hint` |

Required caveat. Because `information_ratio = 0.04697540404970473` is below `information_ratio_min = 0.5`, the contrast between no-aux failure and with-aux recovery is partially guaranteed by the world construction. The B1 result therefore supports only: auxiliary calibration recovers the scalar in this bounded synthetic construction; it does not prove non-tautological information loss or general disentanglement.

B1.1 affine/sparse robustness is reported by `experiments/B/B1_1_auxiliary_calibration_robustness/B1_1_decision.json` @ `6869978` as `B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL`, with `affine_bias_robustness_passed: true`, `sparse_anchor_robustness_passed: true`, and `controls_passed: true`. That file is pre-harness and has no `_harness_provenance`; it is historical support, not a harness-valid claim.

### 1.2 Relation Recovery at Known Dimension

**Claim at allowed strength.** In the bounded synthetic relational B2 rerun, with auxiliary calibration and known evaluation structure, the 2D product-order relation is recovered at high F1. The sparse anchor repair lowered anchor volume while preserving relation-recovery quality. The order-dimension classification result is not blind: the decision explicitly records dependence on a harness-provided `truth_axes=3` hint for the 3D control.

Source: `experiments/B/B2_harness_rerun/decision.json` @ `c129bd0`; prereg/source repair in `experiments/B/B2_harness_rerun/PREREG.json` and `relational_order_toy_fixed.py` @ `bd331cd`.

Key values:

| quantity | value | source |
|---|---:|---|
| decision | `B2.1-PASS-LABEL-FREE-ORDER-DIMENSION` | `decision.json` @ `c129bd0`, key `decision` |
| seed count | `24` | `decision.json` @ `c129bd0`, key `seed_count` |
| recovery pass fraction | `1.0` | `decision.json` @ `c129bd0`, key `recovery_pass_fraction` |
| order-dimension pass fraction | `1.0` | `decision.json` @ `c129bd0`, key `order_dimension_pass_fraction` |
| controls pass fraction | `1.0` | `decision.json` @ `c129bd0`, key `controls_pass_fraction` |
| mean no-aux F1 | `0.5118956978113977` | `decision.json` @ `c129bd0`, key `mean_no_aux_f1` |
| mean with-aux F1 | `0.9969994875628853` | `decision.json` @ `c129bd0`, key `mean_with_aux_f1` |
| mean sparse-anchor F1 | `0.9965407969143273` | `decision.json` @ `c129bd0`, key `mean_sparse_f1` |
| sparse anchor fraction after repair | `0.1` | `decision.json` @ `c129bd0`, key `anchor_fraction_sparse` |
| construction may be tautological | `false` | `decision.json` @ `c129bd0`, key `construction_may_be_tautological` |
| information ratio | `0.8915238326640017` | `decision.json` @ `c129bd0`, key `information_ratio` |
| harness hint dependence | `true` | `decision.json` @ `c129bd0`, key `classification_success_depends_on_harness_hint` |

Anchor repair:

| anchor state | records / fraction | source |
|---|---:|---|
| old sparse anchor volume | `216` records, fraction `0.900` | `MEMO_B_BRANCH_HARNESS.md` @ `4718c0e`, section 5; code comment in `relational_order_toy_fixed.py` @ `bd331cd` states old sparse was `108 items / 216 records` |
| complete anchor volume | `144` records, fraction `0.600` | `MEMO_B_BRANCH_HARNESS.md` @ `4718c0e`, section 5 |
| repaired sparse anchor volume | `24` records, fraction `0.100` | `PREREG.json` @ `bd331cd`, metadata `anchor_graph`; `decision.json` @ `c129bd0`, key `anchor_fraction_sparse` |

Required warning, verbatim from `experiments/B/B2_harness_rerun/decision.json` @ `c129bd0`, key `harness_hint_warnings`:

> classification success on this control depended on harness-provided ground-truth hint (truth_axes=3); this is NOT evidence of unsupervised recovery.

Therefore the citable positive result is relation recovery at known/evaluated dimension, not blind order-dimension discovery.

### 1.3 Blind Dimension Estimation from kNN Graphs

**Claim at allowed strength.** B2.2.1 recovered dimension-table behavior from only the kNN graph, with no coordinates, distances, auxiliary variables, or harness truth hints in the learner path, for the literature-table rows up to `d <= 7`; d=12 rows are included as boundary/high-d checks. The decision is harness-valid and records `classification_success_depends_on_harness_hint: false`.

Source: `gate_harness_experiments/B2_2_1/decision.json` @ `b60683f`; formula extraction source `gate_harness_experiments/B2_2_1/PAPER_EXTRACTION.md` @ `d15a68a`.

Global values:

| quantity | value | source |
|---|---:|---|
| decision | `B2.2.1-PASS-BLIND-DIMENSION-ESTIMATION` | `decision.json` @ `b60683f`, key `decision` |
| seed count | `20` | `decision.json` @ `b60683f`, key `seed_count` |
| blind recovery matches paper fraction | `1.0` | `decision.json` @ `b60683f`, key `blind_recovery_matches_paper_fraction` |
| E_DP worse than E_CAP all cells | `true` | `decision.json` @ `b60683f`, key `e_dp_worse_than_e_cap_all_cells` |
| harness hint dependence | `false` | `decision.json` @ `b60683f`, key `classification_success_depends_on_harness_hint` |

Full per-cell table from `decision.json` @ `b60683f`, key `per_cell`:

| cell | d_true | n | E_CAP mean | paper E_CAP | tolerance | actual outcome | expected outcome | k-spread E_CAP |
|---|---:|---:|---:|---:|---:|---|---|---:|
| `helix_d1_n1000` | `1` | `1000` | `1.0` | `1.0` | `0.5` | `PASS` | `PASS` | `0.20000000000000007` |
| `swiss_d2_n1000` | `2` | `1000` | `2.160000000000001` | `2.14` | `0.5` | `PASS` | `PASS` | `0.3333333333333337` |
| `gaussian_d5_n1000` | `5` | `1000` | `5.33` | `5.33` | `1.0` | `PASS` | `PASS` | `0.6000000000000005` |
| `sphere_d7_n1000` | `7` | `1000` | `5.875000000000001` | `5.88` | `2.0` | `PASS` | `PASS` | `1.033333333333334` |
| `sphere_d7_n5000` | `7` | `5000` | `6.855000000000001` | `6.85` | `2.0` | `PASS` | `PASS` | `1.333333333333334` |
| `cube_d12_n1000` | `12` | `1000` | `7.735000000000001` | `7.74` | `3.0` | `FAIL` | `FAIL` | `1.3999999999999986` |
| `cube_d12_n5000` | `12` | `5000` | `9.24` | `9.24` | `3.0` | `PASS` | `PASS` | `2.0333333333333323` |

### 1.4 Random-Control Mimicry Mechanism

**Claim at allowed strength.** For the preregistered directed random k-out graph control used in B2.2.1/B2.3, the mechanism by which it mimics high-dimensional geometry under E_CAP+k-spread is analytically identified: for directed edge `i -> j`, `B_SP(i,1) ∩ B_SP(j,1)` always includes `j`, and with high probability the minimum over out-neighbors is exactly one shared vertex, giving `L_CAP ≈ 1/(k+1)`.

Source: `gate_harness_experiments/B2_3/decision.json` @ `fcb3fe0`, keys `random_control_mechanism_derived` and `random_control_mechanism_formula`; detailed predictions in `gate_harness_experiments/B2_3/outputs/random_control_mechanism.json` @ `fcb3fe0`.

Key values:

| k | empirical E_CAP sweep at n=1000 | prediction if min intersection = 1 | source |
|---:|---:|---:|---|
| `10` | `9.4` | `9.4` | `random_control_mechanism.json` @ `fcb3fe0` |
| `15` | `11.5` | `11.5` | `random_control_mechanism.json` @ `fcb3fe0` |
| `20` | `13.1` | `13.1` | `random_control_mechanism.json` @ `fcb3fe0` |

B2.2.1 random-control values: fixed-k E_CAP mean `11.5`, E_CAP std `0.0`, k-spread `3.6999999999999993`, kill threshold `2.5`; source `gate_harness_experiments/B2_2_1/decision.json` @ `b60683f`, key `random_graph_control`.

## 2. Established Walls / Negative Results

### 2.1 Computational Wall: General Poset Order Dimension

Claim at allowed strength: the project treats exact general order-dimension recovery as outside the toy proxy; B2/B2.1 explicitly forbid general order-dimension claims. The statement that arbitrary poset order dimension is NP-hard is external literature context, not a repository result. No committed repository artifact in this checkout contains the Yannakakis citation text; the essay must add an external bibliography entry before citing it.

Local sources for the project boundary: `experiments/B/B2_Relational_Order-Dimension_Recovery_Gate.md` @ `bfaafe7` states to implement a bounded proxy, not general exact order dimension; `experiments/B/B2_relational_order_dimension_recovery/B2_1_repair_report.md` @ `3d454ba` states no claim that B2.1 proves general order dimension.

### 2.2 Identifiability Wall: No Unsupervised Disentanglement Without Bias/Auxiliary Variables

Claim at allowed strength: repository experiments do not establish a general theorem. B1 is a toy demonstration consistent with an auxiliary-variable identifiability need. The Locatello et al. 2019 claim is external literature context; no committed local artifact in this checkout provides the full citation. The essay must cite the external paper directly.

Local sources: `experiments/B/B1_harness_rerun/decision.json` @ `8ccefba` shows the toy auxiliary result and `construction_may_be_tautological: true`; `experiments/B/B1_1_auxiliary_calibration_robustness/B1_1_decision.json` @ `6869978` records `general_disentanglement_claim_allowed: false`.

### 2.3 Hint Dependence of B2.1 Order-Dimension Proxy

Claim at allowed strength: the harnessed B2.1 run did not establish blind dimension discovery. It established relation recovery and label-free classifier code, while the 3D-control scoring depended on `truth_axes=3` supplied at the evaluation call site.

Source: `experiments/B/B2_harness_rerun/decision.json` @ `c129bd0`: `classification_success_depends_on_harness_hint: true`, `affected_metrics: ["truth_axes"]`, and warning quoted in section 1.2. This finding is closed only for B2.2/B2.2.1 blind E_CAP dimension estimation up to the supported table rows, not for arbitrary order-dimension discovery.

### 2.4 Scale-Dependent Discrimination Collapse in B2.3

**Claim at allowed strength.** Under the uniform-hypercube family and already-validated E_CAP+k-spread diagnostic, paired discrimination against the preregistered random k-out graph control collapses at high dimension; the observed discrete-grid crossover is earlier for `n=5000` than for `n=1000`. This is a random-control discrimination boundary, not a dimension-accuracy boundary and not theorem confirmation.

Source: `gate_harness_experiments/B2_3/decision.json` @ `fcb3fe0`; full sweep `gate_harness_experiments/B2_3/outputs/crossover_results.json` @ `fcb3fe0`.

| n | d* smallest d with paired separation <= 0.5 | interpolated d at 0.5 | monotone nonincreasing | source |
|---:|---:|---:|---|---|
| `1000` | `130` | `129.83333333333334` | `true` | `decision.json` @ `fcb3fe0`, key `d_star_by_n.1000` |
| `5000` | `24` | `23.125` | `true` | `decision.json` @ `fcb3fe0`, key `d_star_by_n.5000` |

Selected crossover cells from `crossover_results.json` @ `fcb3fe0`:

| n | d | N | paired separation | Wilson 95% CI | mean margin random - geo |
|---:|---:|---:|---:|---|---:|
| `1000` | `129` | `50` | `0.6` | `[0.4618143774758936, 0.7239161026974346]` | `0.5659999999999997` |
| `1000` | `130` | `50` | `0.48` | `[0.34797135286578046, 0.6148825510995539]` | `0.5559999999999997` |
| `1000` | `131` | `50` | `0.48` | `[0.34797135286578046, 0.6148825510995539]` | `0.5519999999999998` |
| `5000` | `24` | `50` | `0.36` | `[0.24138749651846741, 0.49858983123887307]` | `0.5319999999999996` |
| `5000` | `25` | `50` | `0.04` | `[0.011038884327619805, 0.1346009068750702]` | `0.48999999999999827` |
| `5000` | `26` | `50` | `0.0` | `[6.938893903907228e-18, 0.07134759913335872]` | `0.43999999999999845` |

Mechanism diagnostic. Global distance CV does not unify the two crossover points; edge-conditioned shared-neighbor probability does. Source: `gate_harness_experiments/B2_3/outputs/local_knn_mechanism_results.json` @ `d3881b1`.

| metric at crossover | n=1000,d=130 | n=5000,d=24 | ratio n5000/n1000 | source |
|---|---:|---:|---:|---|
| global pairwise distance CV | `0.051841692593309355` | `0.1225569565723039` | `2.364061635366454` | `local_knn_mechanism_results.json` @ `d3881b1`, key `crossover_comparison.global_distance_cv` |
| relative contrast k=15 | `0.06513531836658457` | `0.20369365370949205` | `3.127238168440274` | same file, key `crossover_comparison.by_k.15.relative_contrast_kNN` |
| random-pair shared-neighbor P>1, k=15 | `0.0921825` | `0.010850000000000002` | `0.11770129905350801` | same file, key `crossover_comparison.by_k.15.random_pair_shared_neighbors_gt1` |
| edge-pair shared-neighbor P>1, k=15 | `0.8066733333333334` | `0.8609880000000001` | `1.0673316749448352` | same file, key `crossover_comparison.by_k.15.edge_pair_shared_neighbors_gt1` |

Fixed-k caveat. The exploratory fixed-`k=15` diagnostic did **not** establish the same left-shift as the core k-spread result: for fixed-k paired E_CAP gap, `n=1000` had no crossover through `d=200`, while `n=5000` crossed at `d=38`; source `gate_harness_experiments/B2_3/outputs/b2_3_diagnostics.json` @ `fcb3fe0`, key `k_confound_fixed_k15`. Therefore the canonical claim must not say that the left-shift is stable under fixed k. The established mechanism statement is weaker: local edge-conditioned overlap aligns the two observed core crossover points better than global CV.

Scope warning, verbatim from `gate_harness_experiments/B2_3/decision.json` @ `fcb3fe0`:

> This result rejects tautology only with respect to the preregistered random k-out graph control. It does not establish that the estimator cannot be fooled by other non-geometric graph families.

`not_tested_against` in the same file: `small_world_graphs`, `scale_free_graphs`, `other_non_euclidean_structured_graphs`.

## 3. Methodological Result: `gate_harness`

### 3.1 Chronology and Effect of the Audit

Source: `MEMO_B_BRANCH_HARNESS.md` @ `4718c0e`.

Audit summary recorded there: `10` findings, `3` CRITICAL findings. The three CRITICAL findings were: atomic prereg+results commits, B2.1 thresholds introduced in the result commit, and hardcoded leakage/static-audit fields that let a live variant-branching leak pass.

Harness modules and functions recorded in `MEMO_B_BRANCH_HARNESS.md` @ `4718c0e`:

| module | role |
|---|---|
| `gate_harness/prereg.py` | two-phase `PREREG.json` + `PREREG.lock` with SHA and strict-ancestor git rev |
| `gate_harness/hooks/pre-commit` | blocks staging prereg with outputs and locked-prereg SHA mismatch |
| `gate_harness/leakage_scanner.py` | AST fit-path and audit-integrity leakage scan |
| `gate_harness/calibration_audit.py` | anchor-volume assertions |
| `gate_harness/seed_policy.py` | multi-seed enforcement for core metrics |
| `gate_harness/tautology_check.py` | information-ratio tautology pre-check |
| `gate_harness/runner.py` | fail-closed run path and harness-only flags |
| `gate_harness/verify_decision.py` | standalone decision provenance verifier |
| `gate_harness/evaluation_oracle.py` | harness hint detection |

Re-run changes:

| old artifact | old status | new artifact | new status / flipped fields |
|---|---|---|---|
| `experiments/B/B1_auxiliary_variable_identifiability_gate/B1_decision.json` @ `9f38a14` | `INVALID`, no `_harness_provenance` | `experiments/B/B1_harness_rerun/decision.json` @ `8ccefba` | `VALID`; `construction_may_be_tautological` changed from absent to `true`; `information_ratio` changed from absent to `0.04697540404970473`; `seed_count` changed from absent to `24` |
| `experiments/B/B2_relational_order_dimension_recovery/B2_1_decision.json` @ `3d454ba` | `INVALID`, no `_harness_provenance` | `experiments/B/B2_harness_rerun/decision.json` @ `c129bd0` | `VALID`; `classification_success_depends_on_harness_hint` changed from absent to `true`; `affected_metrics` added as `["truth_axes"]`; sparse anchor fraction recorded as `0.1` |

Old decision invalid reason, verbatim from `gate_harness/verify_decision.py` @ `f2d89c4` and `MEMO_B_BRANCH_HARNESS.md` @ `4718c0e`:

> no _harness_provenance block — decision was not produced by the runner and is INVALID unconditionally, regardless of its numbers

### 3.2 Independent-Agent Discipline

Committed evidence for a general claim about two independent agents named Claude Code and Codex is not present as a primary artifact in this repository. The committed evidence supports a narrower claim: the B2.3 standalone result was explicitly marked non-citable before the harness-signed rerun.

Source: `gate_harness_experiments/B2_3/B2_3_report.md` @ `fcb3fe0` contains the statement:

> This B2.3 artifact is not harness-signed because the current harness requires a strict two-commit preregistration lock before `run_gate` will write a citable decision. The local decision is therefore JSON-valid and reproducible, but not valid by the existing `verify_decision` provenance checker.

The later signed B2.3 decision is `VALID`; source `gate_harness_experiments/B2_3/decision.json` @ `fcb3fe0` plus `verify_decision` output recorded in `gate_harness_experiments/B2_3/outputs/verify_decision.json` @ `fcb3fe0`.

### 3.3 Honest Limits of the Harness

Source: `MEMO_B_BRANCH_HARNESS.md` @ `4718c0e`, section 8; implementation sources `gate_harness/verify_decision.py` @ `f2d89c4` and `gate_harness/runner.py` @ `f2d89c4`.

Limits:

| limit | exact status |
|---|---|
| working-tree hashing | `harness_version` hashes current working-tree `gate_harness/*.py`, not a git checkout of the historical commit |
| runner-level immutability | harness-only flags are protected by `runner.run_gate`; this is not a language-level constant |
| adversary model | committed harness catches represented audit bugs; it is not proof against arbitrary malicious code or non-declared fit paths |
| evaluation-oracle data flow | detects explicit forbidden names/literal hints at call sites; not full data-flow tracing |

## 4. What Is Not Established

### 4.1 No Transfer to Semantic Claims, Language, or LLMs

No B-branch result establishes semantic grounding, language behavior, LLM training validity, substrate discovery, derivability, or real-world transfer. Explicit false/forbidden fields appear in pre-harness B1.1/B2/B2.1 files and B2.3; e.g. `gate_harness_experiments/B2_3/decision.json` @ `fcb3fe0` has `substrate_claim_allowed: false`, `derivability_claim_allowed: false`, `real_world_transfer_claim_allowed: false`, `general_order_dimension_claim_allowed: false`, `no_llm_training: true`, `no_internet_data: true`, and `no_natural_language_corpus: true`.

### 4.2 Other Distributions and Other Non-Geometric Graph Families

Not tested. `gate_harness_experiments/B2_3/decision.json` @ `fcb3fe0`, key `not_tested_against`, lists: `small_world_graphs`, `scale_free_graphs`, `other_non_euclidean_structured_graphs`. The B2.3 world-family claim is limited to the uniform hypercube family under E_CAP+k-spread.

### 4.3 No Closed Formula for d*(n,k)

B2.3 reduced the observed collapse mechanism to local edge-conditioned kNN overlap better than global CV, but did not produce a closed predictive formula for `d*(n,k)`. Source: `gate_harness_experiments/B2_3/outputs/local_knn_mechanism_results.json` @ `d3881b1` gives ratios at observed crossover points; it is diagnostic, not a preregistered formula-fitting gate.

### 4.4 Truth / Viability / Rule Trilemma Not Proven as a Theorem

The trilemma is a conceptual framing used by the S/B branch, not a theorem established by the B-gate results. `experiments/B/B0_boundary_origin_claim_strength_ledger/B0_decision.json` @ `d3fde5b` allows only bounded next work and keeps `substrate_claim_allowed: false`, `derivability_claim_allowed: false`, and `implementation_allowed: false`. Toy consistency across B1/B2/B2.2/B2.3 does not prove the general trilemma.

## 5. Chronological Gate Table

| gate / artifact | question | verdict | key number | status |
|---|---|---|---|---|
| B1 original, `experiments/B/B1_auxiliary_variable_identifiability_gate/B1_decision.json` @ `9f38a14` | Does auxiliary variable allow scalar recovery in synthetic world? | `B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL` | no `_harness_provenance` | superseded / INVALID |
| B1.1 original, `experiments/B/B1_1_auxiliary_calibration_robustness/B1_1_decision.json` @ `6869978` | Is B1 robust to multiseed/sparse/affine controls? | `B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL` | `affine_bias_robustness_passed: true` | historical / pre-harness |
| B2 original, `experiments/B/B2_relational_order_dimension_recovery/B2_decision.json` @ `b52da24` | Can 2D product-order relation be recovered? | `B2-PASS-RELATIONAL-ORDER-DIMENSION-SIGNAL` | `toy_order_dimension_proxy_passed: true` | superseded / pre-harness |
| B2.1 original, `experiments/B/B2_relational_order_dimension_recovery/B2_1_decision.json` @ `3d454ba` | Was variant-label order proxy repaired? | `B2.1-PASS-LABEL-FREE-DIMENSION-PROXY-REPAIRED` | no `_harness_provenance` | superseded / INVALID |
| B1 harness rerun, `experiments/B/B1_harness_rerun/decision.json` @ `8ccefba` | Does scalar auxiliary recovery survive harness discipline? | `B1-PASS-AUXILIARY-IDENTIFIABILITY` | `mean_with_aux_corr = 0.9999661041760123`; `construction_may_be_tautological = true` | harness-valid |
| B2 harness rerun, `experiments/B/B2_harness_rerun/decision.json` @ `c129bd0` | Does relation recovery survive harness discipline and anchor repair? | `B2.1-PASS-LABEL-FREE-ORDER-DIMENSION` | `mean_with_aux_f1 = 0.9969994875628853`; `classification_success_depends_on_harness_hint = true` | harness-valid with hint caveat |
| B2.2, `gate_harness_experiments/B2_2/decision.json` @ `d0df33d` | Can dimension be estimated blindly from kNN graph? | `B2.2-PASS-BLIND-DIMENSION-ESTIMATION` | `blind_recovery_matches_paper_fraction = 1.0` | harness-valid but superseded by B2.2.1 |
| B2.2.1, `gate_harness_experiments/B2_2_1/decision.json` @ `b60683f` | Side-channel-hardened blind E_CAP dimension estimation plus random-control k-sweep | `B2.2.1-PASS-BLIND-DIMENSION-ESTIMATION` | random-control `k_spread = 3.6999999999999993`; `classification_success_depends_on_harness_hint = false` | harness-valid |
| B2.3 prereg/code, `gate_harness_experiments/B2_3/PREREG.json` @ `1b35bad` | Preregister discrimination crossover mapping | prereg/code only | primary metric `paired_separation`; epsilon `0.5` | prereg phase |
| B2.3 signed run, `gate_harness_experiments/B2_3/decision.json` @ `fcb3fe0` | Where does random-control discrimination collapse? | `B2.3-PASS-DISCRIMINATION-CROSSOVER-MAPPED` | `d*(1000)=130`; `d*(5000)=24`; shift `-106` | harness-valid |
| B2.3 diagnostics A-D, `gate_harness_experiments/B2_3/outputs/b2_3_diagnostics.json` @ `fcb3fe0` | Check provenance, fixed-k, S(d), dense d=8..30 | exploratory diagnostics | fixed-k: `n=1000` no crossover to `d=200`, `n=5000` d*=38; dense scan `n=5000` d*=24 | informal / explanatory |
| B2.3 concentration/hubness, `gate_harness_experiments/B2_3/outputs/concentration_hubness_results.json` @ `fd68fe1` | Do global CV and hubness correlate with collapse? | exploratory diagnostic | corr(paired separation, CV): `0.7056565007018698` at n=1000, `0.7946271079463642` at n=5000 | informal / explanatory |
| B2.3 local kNN mechanism, `gate_harness_experiments/B2_3/outputs/local_knn_mechanism_results.json` @ `d3881b1` | Does a local kNN statistic unify crossover? | exploratory diagnostic | edge-pair shared-neighbor ratio at k=15: `1.0673316749448352`; global CV ratio `2.364061635366454` | informal / explanatory |

## Source Discipline

A number may be cited in the essay only if it appears above with a path and commit hash, or if the essay adds a new source entry here first. Literature claims without committed local source, including Yannakakis/order-dimension complexity and Locatello-style disentanglement impossibility, require external bibliography entries in the essay and must not be presented as repository results.
