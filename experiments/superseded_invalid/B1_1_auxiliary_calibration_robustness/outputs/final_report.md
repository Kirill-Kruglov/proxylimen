# B1.1 Final Report

Decision: `B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL`

Metrics:

```json
{
  "affine_bias": {
    "affine_improvement": 0.8031909984767123,
    "affine_no_aux_abs_corr": 0.196738031634565,
    "affine_shuffled_aux_corr": 0.18820233703438402,
    "affine_with_aux_corr": 0.9999290301112772
  },
  "controls_passed": true,
  "multiseed": {
    "individual_pass_fraction": 1.0,
    "mean_improvement": 0.788861790158433,
    "mean_no_aux_abs_corr": 0.21110462050935405,
    "mean_with_aux_corr": 0.999966410667787
  },
  "no_aux_baselines": {
    "max_no_aux_abs_corr": 0.31253299890661973
  },
  "sparse_anchor": {
    "disconnected_anchor_corr": 0.1607473760914764,
    "sparse_anchor_improvement": 0.8388748088900052,
    "sparse_anchor_with_aux_corr": 0.9999649333239292
  }
}
```

Leakage audit:

```json
{
  "anchors_contain_true_z_obj_labels_for_fit": false,
  "aux_leakage_detected": false,
  "fit_functions_read_z_obj": false,
  "human_authored_final_or_outcome_labels_exist": false,
  "human_authored_outcomes_detected": false,
  "seed_to_result_lookup_exists": false,
  "true_z_obj_used_only_after_predictions": true,
  "u_directly_encodes_exact_z_obj": false,
  "u_uniquely_identifies_item_id": false,
  "variant_to_result_lookup_exists": false
}
```

No LLM training, substrate claim, derivability claim, semantic boundary generator claim, real-world transfer claim, or general disentanglement claim is allowed by this result.
