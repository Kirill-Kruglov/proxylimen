# B1 Final Report

Decision: `B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL`

Metrics:

```json
{
  "improvement": 0.766086749551359,
  "no_anchor_with_aux_corr": 0.23254348554400373,
  "no_aux_abs_corr": 0.2338839303693749,
  "no_aux_corr": 0.2338839303693749,
  "random_world_corr": 0.005953949876847943,
  "shuffled_aux_corr": 0.23254348554400373,
  "thresholds": {
    "improvement_min": 0.6,
    "no_anchor_with_aux_corr_max": 0.5,
    "no_aux_abs_corr_max": 0.3,
    "random_world_corr_max": 0.3,
    "shuffled_aux_corr_max": 0.5,
    "with_aux_corr_min": 0.9
  },
  "with_aux_corr": 0.999970679920734
}
```

Controls:

```json
{
  "C1_shuffled_auxiliary": {
    "metric": {
      "abs_pearson_corr": 0.23254348554400373,
      "heldout_count": 320,
      "pearson_corr": 0.23254348554400373
    },
    "passed": true,
    "threshold": {
      "pearson_corr_max": 0.5
    }
  },
  "C2_no_anchor": {
    "metric": {
      "abs_pearson_corr": 0.23254348554400373,
      "heldout_count": 320,
      "pearson_corr": 0.23254348554400373
    },
    "passed": true,
    "threshold": {
      "pearson_corr_max": 0.5
    }
  },
  "C3_random_world": {
    "metric": {
      "abs_pearson_corr": 0.005953949876847943,
      "heldout_count": 320,
      "pearson_corr": 0.005953949876847943
    },
    "passed": true,
    "threshold": {
      "pearson_corr_max": 0.3
    }
  },
  "C4_auxiliary_leakage_audit": "see leakage_audit.json"
}
```

Leakage audit:

```json
{
  "anchors_include_true_z_obj_labels_for_fit": false,
  "evaluation_truth_used_only_after_predictions": true,
  "human_authored_outcome_labels_used": false,
  "leakage_detected": false,
  "learner_fit_reads_true_z_obj": false,
  "statistical_confounding_present_by_design": true,
  "u_directly_encodes_exact_z_obj": false,
  "u_uniquely_identifies_item_id": false
}
```

No LLM training, substrate claim, derivability claim, semantic boundary generator claim, or real-world transfer claim is allowed by this result.
