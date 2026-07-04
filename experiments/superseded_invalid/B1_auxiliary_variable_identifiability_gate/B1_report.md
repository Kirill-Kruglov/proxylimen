# B1 — Auxiliary-Variable Identifiability Gate

## 0. Verdict
Decision: `B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL`.

Reason: No-auxiliary recovery failed, auxiliary calibration recovered the latent scalar, and controls failed as required.

## 1. Goal anchor
Immutable project goal: train an LLM / learner so that its world-model is derived, not merely generalized from internet-like data.

B1 does not train an LLM. It only tests a synthetic identifiability condition: whether objective/perceptual separation fails without an auxiliary variable and succeeds with explicit auxiliary calibration anchors.

## 2. Inputs used
- Primary task file: `experiments/B/B1_Auxiliary-Variable_Identifiability_Gate.md`
- Gate prerequisite: `/home/master/llm_projects/ascesis/experiments/S/S4_tiny_boundary_accounting_replay_implementation/S4_1_decision.json`
- S4.1 decision observed: `S4.1-PASS-GATE-CHAIN-VERIFICATION-REPAIRED`

## 3. Hypothesis
In the synthetic world `y_i,u = z_obj_i + bias_u + noise`, raw observations alone should not recover `z_obj` under the confounded observer/item allocation. Recovery should become possible when `u` and repeated anchor overlaps identify relative observer bias.

## 4. Synthetic world design
The dataset was generated with deterministic seed `20260702`. Four observer classes have different additive biases. Non-anchor item allocation is confounded: U0 mostly observes low latent items, U1 lower-mid items, U2 upper-mid items, and U3 high items. Biases counteract those latent ranges so raw `y` is not a reliable objective ordering.

Calibration anchors are repeated observations across all observer classes. Anchor records provide overlap structure only; learner fitting does not read true `z_obj`.

## 5. Learners
- `no_auxiliary_learner`: uses `y` only and emits rank-normalized raw observations.
- `with_auxiliary_calibration_learner`: uses `y`, `u`, and anchor overlaps to estimate relative observer bias, then predicts `y - estimated_bias_u`.

## 6. Primary metrics
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

## 7. Controls
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

## 8. Leakage audit
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

## 9. Pass / fail analysis
- S4.1 prerequisite confirmed: `True`
- No-auxiliary recovery failed as required: `True`
- Auxiliary recovery succeeded: `True`
- Improvement threshold passed: `True`
- Shuffled auxiliary control passed: `True`
- No-anchor control passed: `True`
- Random-world control passed: `True`
- Auxiliary leakage detected: `False`
- Human-authored outcomes detected: `False`

## 10. What was NOT shown
- No substrate was found.
- No derived world-model was shown.
- No LLM training is allowed.
- No semantic boundary generator was implemented.
- No claim that objective/perceptual separation is generally possible.
- No claim that real-world perception can be disentangled by this toy result.
- No claim that auxiliary variables solve grounding.
- No claim that synthetic identifiability transfers to internet-scale data.
- No claim that viability coloring is truth.
- No claim that passing B1 proves the project goal.

## 11. Downstream permission
If accepted, this result permits only a B1 postmortem or a B2 relational order-dimension gate specification. It does not permit LLM training, substrate claims, derivability claims, semantic boundary generator claims, or real-world transfer claims.

## 12. Durable result
B1 produced a deterministic synthetic identifiability signal: under the preregistered construction, objective latent recovery failed without the auxiliary variable and succeeded with auxiliary calibration anchors, while the preregistered controls failed to recover.
