# B2 — Relational Order-Dimension Recovery Gate

## 0. Verdict
Decision: `B2-PASS-RELATIONAL-ORDER-DIMENSION-SIGNAL`.

Reason: Auxiliary calibration recovered the generated 2D product-order relation while no-auxiliary and broken-calibration controls failed.

## 1. Goal anchor
Immutable project goal: train an LLM / learner so that its world-model is derived, not merely generalized from internet-like data.

B2 does not train an LLM and does not use real-world data. It tests a bounded synthetic relational recovery condition.

## 2. Inputs used
- B1.1 decision artifact: `/home/master/llm_projects/ascesis/experiments/B/B1_1_auxiliary_calibration_robustness/B1_1_decision.json`
- B1.1 decision observed: `B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL`
- S4.1 decision artifact: `/home/master/llm_projects/ascesis/experiments/S/S4_tiny_boundary_accounting_replay_implementation/S4_1_decision.json`
- S4.1 decision observed: `S4.1-PASS-GATE-CHAIN-VERIFICATION-REPAIRED`

## 3. Hypothesis
If auxiliary calibration can recover more than a scalar in this toy setting, then calibrated observer-colored coordinates should recover a generated 2D product-order relation while raw no-auxiliary coordinates and broken calibration controls fail.

## 4. Synthetic relational world
Items have generated latent coordinates `(x, y)`. The generated relation is coordinate-wise product order with margin `0.035`. Each observer applies a positive coordinate-wise affine transform plus small noise. Anchors provide shared item overlaps; they do not expose true coordinates to fitting functions.

## 5. Learners
- No-auxiliary learner: uses only `obs_x` and `obs_y` as one global coordinate system.
- With-auxiliary calibration learner: uses `obs_x`, `obs_y`, `u`, and anchor overlaps to estimate affine maps into a reference observer frame, then predicts product-order relations in that calibrated frame.

## 6. Primary relation-recovery metrics
```json
{
  "chain_control_f1": 0.9991325664718084,
  "disconnected_anchor_relation_f1": 0.5858511692793421,
  "multiseed_pass_fraction": 1.0,
  "no_anchor_relation_f1": 0.5286042111196103,
  "no_aux_relation_f1": 0.4738768131916582,
  "random_relation_2d_f1": 0.2283528457169352,
  "relation_f1_improvement": 0.5226715312920849,
  "shuffled_aux_relation_f1": 0.29776635063474205,
  "sparse_anchor_relation_f1": 0.997096217234343,
  "three_d_control_2d_f1": 0.6394600533668184,
  "thresholds": {
    "chain_control_f1_min": 0.95,
    "disconnected_anchor_relation_f1_max": 0.65,
    "multiseed_pass_fraction_min": 0.8,
    "no_anchor_relation_f1_max": 0.65,
    "no_aux_relation_f1_max": 0.6,
    "random_relation_2d_f1_max": 0.6,
    "relation_f1_improvement_min": 0.3,
    "shuffled_aux_relation_f1_max": 0.65,
    "sparse_anchor_relation_f1_min": 0.85,
    "three_d_control_2d_f1_max": 0.8,
    "with_aux_relation_f1_min": 0.9
  },
  "with_aux_relation_f1": 0.9965483444837431
}
```

## 7. Toy order-dimension proxy
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

## 8. Controls
```json
{
  "controls": {
    "C1_shuffled_auxiliary": {
      "passed": true,
      "relation_f1": 0.29776635063474205
    },
    "C2_no_anchors": {
      "passed": true,
      "relation_f1": 0.5286042111196103
    },
    "C3_disconnected_anchors": {
      "passed": true,
      "relation_f1": 0.5858511692793421
    },
    "C4_random_relation": {
      "passed": true,
      "relation_f1": 0.2283528457169352
    },
    "C5_chain_control": {
      "passed": true,
      "relation_f1": 0.9991325664718084
    },
    "C6_three_d_control": {
      "passed": true,
      "relation_f1": 0.6394600533668184
    },
    "C7_leakage_audit": "see leakage_audit.json",
    "C8_static_audit": "see static_audit.json"
  },
  "passed": true,
  "sparse_anchor_relation_f1": 0.997096217234343
}
```

## 9. Leakage and static audit
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

## 10. Pass / fail analysis
- B1.1 prerequisite confirmed: `True`
- S4.1 prerequisite confirmed: `True`
- No-auxiliary recovery failed: `True`
- With-auxiliary relation recovery succeeded: `True`
- Relation improvement passed: `True`
- Toy order-dimension proxy passed: `True`
- Controls passed: `True`
- Static audit passed: `True`
- Relation label leakage detected: `False`
- Auxiliary leakage detected: `False`

## 11. What was NOT shown
- No substrate was found.
- No derived world-model was shown.
- No LLM training is allowed.
- No semantic boundary generator was implemented.
- No claim that objective/perceptual separation is generally possible.
- No claim that real-world perception can be disentangled by this toy result.
- No claim that auxiliary variables solve grounding.
- No claim that synthetic relational recovery transfers to internet-scale data.
- No claim that toy order-dimension proxy is general order-dimension recovery.
- No claim that viability coloring is truth.
- No claim that passing B2 proves the project goal.

## 12. Downstream permission
If accepted, this result permits only a B2 postmortem or a B3 relational robustness / adversarial controls specification. It does not permit LLM training, substrate claims, derivability claims, semantic boundary generator claims, real-world transfer claims, general order-dimension claims, or general disentanglement claims.

## 13. Durable result
B2 produced a bounded synthetic relational recovery signal: in this constructed toy world, auxiliary affine calibration recovered a generated 2D product-order relation and the preregistered controls did not recover above threshold.
