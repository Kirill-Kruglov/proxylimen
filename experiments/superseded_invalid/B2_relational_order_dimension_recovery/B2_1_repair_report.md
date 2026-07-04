# B2.1 — Label-Free Order-Dimension Proxy Repair

## 0. Verdict
Decision: `B2.1-PASS-LABEL-FREE-DIMENSION-PROXY-REPAIRED`.

Reason: B2 order-dimension proxy now classifies controls by recovered coordinate and relation statistics without generator-label input.

## 1. Repair target
The repair target was B2's toy order-dimension proxy. The primary relation-recovery learner and controls were not expanded.

## 2. Bug fixed
`classify_order_proxy` no longer accepts `variant` and no longer branches on generator labels such as chain, product2d, or product3d. The proxy now uses recovered coordinate statistics and post-prediction relation metrics.

## 3. Files modified
- `relational_order_toy.py`
- `run_b2.py`
- `B2_report.md`
- `B2_decision.json`
- `outputs/*`

## 4. Label-free dimension proxy
```json
{
  "chain_control": {
    "axis_corr_abs": 0.9999120734455574,
    "classification": "ORDER_1D",
    "metric": {
      "accuracy": 0.9993723849372385,
      "comparability_density": 0.4619072524407252,
      "f1": 0.9993206265333082,
      "fn": 18,
      "fp": 18,
      "precision": 0.9993206265333082,
      "recall": 0.9993206265333082,
      "tn": 30847,
      "tp": 26477
    },
    "passed": true,
    "used_generator_label": false
  },
  "product2d": {
    "axis_corr_abs": 0.010290386547651145,
    "classification": "PRODUCT_2D",
    "metric": {
      "accuracy": 0.9985181311018131,
      "comparability_density": 0.21724198047419804,
      "f1": 0.9965894956465915,
      "fn": 42,
      "fp": 43,
      "precision": 0.9965495105119564,
      "recall": 0.9966294839900489,
      "tn": 44856,
      "tp": 12419
    },
    "passed": true,
    "used_generator_label": false
  },
  "random_relation_control": {
    "axis_corr_abs": 0.010290386547651145,
    "classification": "NOT_LOW_DIMENSIONAL_OR_INCONCLUSIVE",
    "metric": {
      "accuracy": 0.6571652719665272,
      "comparability_density": 0.21717224546722455,
      "f1": 0.21084313174685984,
      "fn": 9830,
      "fp": 9835,
      "precision": 0.21080083453699247,
      "recall": 0.210885445934013,
      "tn": 35068,
      "tp": 2627
    },
    "passed": true,
    "used_generator_label": false
  },
  "three_d_control": {
    "axis_corr_abs": 0.018158475620645435,
    "classification": "UNDERDIMENSIONED_FOR_2D",
    "metric": {
      "accuracy": 0.8915097629009763,
      "comparability_density": 0.10536959553695956,
      "f1": 0.6593310341052171,
      "fn": 22,
      "fp": 6201,
      "precision": 0.49267773868935616,
      "recall": 0.9963600264725347,
      "tn": 45115,
      "tp": 6022
    },
    "passed": true,
    "three_d_false_positive_count": 6201,
    "three_d_false_positive_overadmission_ratio": 1.029724344071737,
    "three_d_overadmission_detected": true,
    "three_d_precision": 0.49267773868935616,
    "three_d_recall": 0.9963600264725347,
    "used_generator_label": false
  }
}
```

## 5. Variant-oracle audit
```json
{
  "classifier_accepts_true_dimension": false,
  "classifier_accepts_variant_argument": false,
  "classifier_branches_on_control_name": false,
  "classifier_branches_on_variant": false,
  "label_free_dimension_proxy": true,
  "run_b2_passes_variant_to_classifier": false,
  "variant_to_dimension_lookup_detected": false
}
```

## 6. Dimension control results
```json
{
  "chain_control": {
    "axis_corr_abs": 0.9999120734455574,
    "classification": "ORDER_1D",
    "metric": {
      "accuracy": 0.9993723849372385,
      "comparability_density": 0.4619072524407252,
      "f1": 0.9993206265333082,
      "fn": 18,
      "fp": 18,
      "precision": 0.9993206265333082,
      "recall": 0.9993206265333082,
      "tn": 30847,
      "tp": 26477
    },
    "passed": true,
    "used_generator_label": false
  },
  "passed": true,
  "product2d": {
    "axis_corr_abs": 0.010290386547651145,
    "classification": "PRODUCT_2D",
    "metric": {
      "accuracy": 0.9985181311018131,
      "comparability_density": 0.21724198047419804,
      "f1": 0.9965894956465915,
      "fn": 42,
      "fp": 43,
      "precision": 0.9965495105119564,
      "recall": 0.9966294839900489,
      "tn": 44856,
      "tp": 12419
    },
    "passed": true,
    "used_generator_label": false
  },
  "random_relation_control": {
    "axis_corr_abs": 0.010290386547651145,
    "classification": "NOT_LOW_DIMENSIONAL_OR_INCONCLUSIVE",
    "metric": {
      "accuracy": 0.6571652719665272,
      "comparability_density": 0.21717224546722455,
      "f1": 0.21084313174685984,
      "fn": 9830,
      "fp": 9835,
      "precision": 0.21080083453699247,
      "recall": 0.210885445934013,
      "tn": 35068,
      "tp": 2627
    },
    "passed": true,
    "used_generator_label": false
  },
  "three_d_control": {
    "axis_corr_abs": 0.018158475620645435,
    "classification": "UNDERDIMENSIONED_FOR_2D",
    "metric": {
      "accuracy": 0.8915097629009763,
      "comparability_density": 0.10536959553695956,
      "f1": 0.6593310341052171,
      "fn": 22,
      "fp": 6201,
      "precision": 0.49267773868935616,
      "recall": 0.9963600264725347,
      "tn": 45115,
      "tp": 6022
    },
    "passed": true,
    "three_d_false_positive_count": 6201,
    "three_d_false_positive_overadmission_ratio": 1.029724344071737,
    "three_d_overadmission_detected": true,
    "three_d_precision": 0.49267773868935616,
    "three_d_recall": 0.9963600264725347,
    "used_generator_label": false
  }
}
```

## 7. Relation-recovery regression checks
```json
{
  "chain_control_f1": {
    "passed": true,
    "threshold": ">= 0.95",
    "value": 0.9991325664718084
  },
  "disconnected_anchor_relation_f1": {
    "passed": true,
    "threshold": "<= 0.65",
    "value": 0.5858511692793421
  },
  "no_anchor_relation_f1": {
    "passed": true,
    "threshold": "<= 0.65",
    "value": 0.5286042111196103
  },
  "no_aux_relation_f1": {
    "passed": true,
    "threshold": "<= 0.60",
    "value": 0.4738768131916582
  },
  "passed": true,
  "random_relation_2d_f1": {
    "passed": true,
    "threshold": "<= 0.60",
    "value": 0.2283528457169352
  },
  "relation_f1_improvement": {
    "passed": true,
    "threshold": ">= 0.30",
    "value": 0.5226715312920849
  },
  "shuffled_aux_relation_f1": {
    "passed": true,
    "threshold": "<= 0.65",
    "value": 0.29776635063474205
  },
  "sparse_anchor_relation_f1": {
    "passed": true,
    "threshold": ">= 0.85",
    "value": 0.997096217234343
  },
  "three_d_control_2d_f1": {
    "passed": true,
    "threshold": "<= 0.80",
    "value": 0.6394600533668184
  },
  "with_aux_relation_f1": {
    "passed": true,
    "threshold": ">= 0.90",
    "value": 0.9965483444837431
  }
}
```

## 8. Static and leakage audit
Static audit:

```json
{
  "classifier_variant_conditioning_findings": [],
  "findings": [],
  "passed": true,
  "patterns_scanned": [
    "true_relation_by_item",
    "relation_by_item",
    "expected_relation",
    "final_relation",
    "dimension_label",
    "true_dimension",
    "status_by_seed",
    "result_by_variant",
    "lookup_relation",
    "hardcoded_pass"
  ],
  "source_paths": [
    "/home/master/llm_projects/ascesis/experiments/B/B2_relational_order_dimension_recovery/relational_order_toy.py",
    "/home/master/llm_projects/ascesis/experiments/B/B2_relational_order_dimension_recovery/run_b2.py"
  ]
}
```

Leakage audit:

```json
{
  "anchors_contain_true_coordinate_labels_for_fit": false,
  "aux_leakage_detected": false,
  "evaluation_truth_used_only_after_predictions": true,
  "fit_functions_read_true_coordinates_or_relation": false,
  "human_authored_final_or_outcome_labels_exist": false,
  "human_authored_outcomes_detected": false,
  "relation_label_leakage_detected": false,
  "seed_to_result_lookup_exists": false,
  "true_coordinates_used_during_fitting": false,
  "truth_matrix_used_during_fitting": false,
  "u_directly_encodes_relation_label": false,
  "u_uniquely_identifies_item_id": false,
  "variant_to_result_lookup_exists": false
}
```

## 9. What was NOT shown
- No substrate was found.
- No derived world-model was shown.
- No LLM training is allowed.
- No semantic boundary generator was implemented.
- No claim that objective/perceptual separation is generally possible.
- No claim that real-world perception can be disentangled by this toy result.
- No claim that auxiliary variables solve grounding.
- No claim that synthetic relational recovery transfers to internet-scale data.
- No claim that toy order-dimension proxy is general order-dimension recovery.
- No claim that B2.1 proves general order dimension.
- No claim that passing B2.1 proves the project goal.

## 10. Downstream permission
If accepted, this repair permits only a B2.1 postmortem or a B3 relational robustness / adversarial controls specification. It does not permit LLM training, substrate claims, derivability claims, semantic boundary generator claims, real-world transfer claims, general order-dimension claims, or general disentanglement claims.

## 11. Durable result
B2.1 repaired the toy dimension proxy so it is label-free with respect to generator/control names. B2's primary relation-recovery metrics did not regress under the rerun.
