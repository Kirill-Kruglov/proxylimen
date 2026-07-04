# B1.1 — Auxiliary-Calibration Robustness / Leakage Hardening Gate

## 0. Verdict
Decision: `B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL`.

Reason: The auxiliary calibration signal survived multiseed, sparse-anchor, affine, no-auxiliary baseline, control, and leakage checks.

## 1. Goal anchor
Immutable project goal: train an LLM / learner so that its world-model is derived, not merely generalized from internet-like data.

B1.1 does not train an LLM and does not test real-world data. It tests whether the B1 synthetic auxiliary-calibration signal survives stronger bounded robustness checks.

## 2. Inputs used
- B1 decision artifact: `/home/master/llm_projects/ascesis/experiments/B/B1_auxiliary_variable_identifiability_gate/B1_decision.json`
- B1 decision observed: `B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL`
- S4.1 decision artifact: `/home/master/llm_projects/ascesis/experiments/S/S4_tiny_boundary_accounting_replay_implementation/S4_1_decision.json`
- S4.1 decision observed: `S4.1-PASS-GATE-CHAIN-VERIFICATION-REPAIRED`

## 3. Hypothesis
If the B1 result is not merely a one-seed, complete-anchor, additive-bias, weak-baseline artifact, then auxiliary calibration should still recover the latent scalar across multiple deterministic variants while negative controls and no-auxiliary baselines fail.

## 4. Robustness suite design
The suite uses deterministic synthetic data, four observer classes, generated latent `z_obj`, observer colorings, and calibration anchors. Learner views strip `z_obj`; truth is used only by evaluation after predictions are produced.

## 5. Multiseed results
```json
{
  "individual_pass_fraction": 1.0,
  "mean_improvement": 0.788861790158433,
  "mean_no_aux_abs_corr": 0.21110462050935405,
  "mean_with_aux_corr": 0.999966410667787,
  "passed": true,
  "seed_count": 24,
  "seed_results": [
    {
      "improvement": 0.7804365604025002,
      "individual_passed": true,
      "no_aux_abs_corr": 0.21953408988753356,
      "seed": 20260702,
      "with_aux_corr": 0.9999706502900337
    },
    {
      "improvement": 0.7497660769973374,
      "individual_passed": true,
      "no_aux_abs_corr": 0.2502008806354781,
      "seed": 20260703,
      "with_aux_corr": 0.9999669576328155
    },
    {
      "improvement": 0.7016090946953527,
      "individual_passed": true,
      "no_aux_abs_corr": 0.29835889046581265,
      "seed": 20260704,
      "with_aux_corr": 0.9999679851611654
    },
    {
      "improvement": 0.8063784606789529,
      "individual_passed": true,
      "no_aux_abs_corr": 0.1935849483278691,
      "seed": 20260705,
      "with_aux_corr": 0.999963409006822
    },
    {
      "improvement": 0.8437977386070622,
      "individual_passed": true,
      "no_aux_abs_corr": 0.1561669045626288,
      "seed": 20260706,
      "with_aux_corr": 0.999964643169691
    },
    {
      "improvement": 0.8054180973331877,
      "individual_passed": true,
      "no_aux_abs_corr": 0.19455001318456358,
      "seed": 20260707,
      "with_aux_corr": 0.9999681105177513
    },
    {
      "improvement": 0.8833272979588491,
      "individual_passed": true,
      "no_aux_abs_corr": 0.11664172669196521,
      "seed": 20260708,
      "with_aux_corr": 0.9999690246508144
    },
    {
      "improvement": 0.7025576599015757,
      "individual_passed": true,
      "no_aux_abs_corr": 0.2974135600323204,
      "seed": 20260709,
      "with_aux_corr": 0.9999712199338961
    },
    {
      "improvement": 0.777898645670739,
      "individual_passed": true,
      "no_aux_abs_corr": 0.22207003444425658,
      "seed": 20260710,
      "with_aux_corr": 0.9999686801149955
    },
    {
      "improvement": 0.772087745262942,
      "individual_passed": true,
      "no_aux_abs_corr": 0.22788130570081716,
      "seed": 20260711,
      "with_aux_corr": 0.9999690509637592
    },
    {
      "improvement": 0.7742756124774067,
      "individual_passed": true,
      "no_aux_abs_corr": 0.22569435332091844,
      "seed": 20260712,
      "with_aux_corr": 0.9999699657983252
    },
    {
      "improvement": 0.7368751608584494,
      "individual_passed": true,
      "no_aux_abs_corr": 0.263092693138515,
      "seed": 20260713,
      "with_aux_corr": 0.9999678539969644
    },
    {
      "improvement": 0.8058725895162191,
      "individual_passed": true,
      "no_aux_abs_corr": 0.19407739206278435,
      "seed": 20260714,
      "with_aux_corr": 0.9999499815790034
    },
    {
      "improvement": 0.8314153053068873,
      "individual_passed": true,
      "no_aux_abs_corr": 0.16855166210025055,
      "seed": 20260715,
      "with_aux_corr": 0.9999669674071379
    },
    {
      "improvement": 0.6980750341474936,
      "individual_passed": true,
      "no_aux_abs_corr": 0.3018931314588631,
      "seed": 20260716,
      "with_aux_corr": 0.9999681656063567
    },
    {
      "improvement": 0.9232896442039455,
      "individual_passed": true,
      "no_aux_abs_corr": 0.07667378699416377,
      "seed": 20260717,
      "with_aux_corr": 0.9999634311981093
    },
    {
      "improvement": 0.8494801813570492,
      "individual_passed": true,
      "no_aux_abs_corr": 0.15047453176134368,
      "seed": 20260718,
      "with_aux_corr": 0.9999547131183929
    },
    {
      "improvement": 0.714378978655265,
      "individual_passed": true,
      "no_aux_abs_corr": 0.28558551390889597,
      "seed": 20260719,
      "with_aux_corr": 0.999964492564161
    },
    {
      "improvement": 0.7909480573632723,
      "individual_passed": true,
      "no_aux_abs_corr": 0.20901651495088888,
      "seed": 20260720,
      "with_aux_corr": 0.9999645723141612
    },
    {
      "improvement": 0.8034764370606174,
      "individual_passed": true,
      "no_aux_abs_corr": 0.1964906193599316,
      "seed": 20260721,
      "with_aux_corr": 0.9999670564205491
    },
    {
      "improvement": 0.8615868237793849,
      "individual_passed": true,
      "no_aux_abs_corr": 0.1383844068343867,
      "seed": 20260722,
      "with_aux_corr": 0.9999712306137716
    },
    {
      "improvement": 0.7246433421132652,
      "individual_passed": true,
      "no_aux_abs_corr": 0.2753251773542608,
      "seed": 20260723,
      "with_aux_corr": 0.9999685194675261
    },
    {
      "improvement": 0.7804634173194264,
      "individual_passed": true,
      "no_aux_abs_corr": 0.21950409378447508,
      "seed": 20260724,
      "with_aux_corr": 0.9999675111039015
    },
    {
      "improvement": 0.8146250021352115,
      "individual_passed": true,
      "no_aux_abs_corr": 0.18534466126157417,
      "seed": 20260725,
      "with_aux_corr": 0.9999696633967856
    }
  ]
}
```

## 6. Sparse-anchor results
```json
{
  "disconnected_anchor_corr": 0.1607473760914764,
  "disconnected_anchor_graph_connected": false,
  "no_aux_abs_corr": 0.161090124433924,
  "passed": true,
  "seed": 20260803,
  "sparse_anchor_graph_connected": true,
  "sparse_anchor_improvement": 0.8388748088900052,
  "sparse_anchor_with_aux_corr": 0.9999649333239292
}
```

## 7. Affine-bias results
```json
{
  "affine_improvement": 0.8031909984767123,
  "affine_no_aux_abs_corr": 0.196738031634565,
  "affine_shuffled_aux_corr": 0.18820233703438402,
  "affine_with_aux_corr": 0.9999290301112772,
  "passed": true,
  "seed": 20260913,
  "transforms_to_U0_scale": {
    "U0": [
      1.0,
      0.0
    ],
    "U1": [
      0.6938098235044614,
      0.8658541592833564
    ],
    "U2": [
      0.4588038752754258,
      1.7555494573084367
    ],
    "U3": [
      0.35502779754972125,
      2.632944730134988
    ]
  }
}
```

## 8. Stronger no-auxiliary baselines
```json
{
  "baseline_results": {
    "NO_AUX_GLOBAL_STANDARDIZE": {
      "abs_pearson_corr": 0.31253299890661973,
      "heldout_count": 320,
      "pearson_corr": 0.31253299890661973
    },
    "NO_AUX_QUANTILE_SEGMENT": {
      "abs_pearson_corr": 0.3064511926284344,
      "heldout_count": 320,
      "pearson_corr": 0.3064511926284344
    },
    "NO_AUX_RAW_RANK": {
      "abs_pearson_corr": 0.30799841410283424,
      "heldout_count": 320,
      "pearson_corr": 0.30799841410283424
    }
  },
  "max_no_aux_abs_corr": 0.31253299890661973,
  "passed": true
}
```

## 9. Controls
```json
{
  "controls": {
    "C1_shuffled_auxiliary": {
      "corr": 0.03774241829592382,
      "passed": true
    },
    "C2_no_anchors": {
      "corr": 0.15895900362362353,
      "passed": true
    },
    "C3_disconnected_anchors": {
      "anchor_graph_connected": false,
      "corr": 0.15895900362362353,
      "passed": true
    },
    "C4_random_world": {
      "corr": -0.2657645862573657,
      "passed": true
    },
    "C5_leakage_audit": "see leakage_audit.json"
  },
  "passed": true
}
```

## 10. Leakage audit
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

## 11. Pass / fail analysis
- B1 prerequisite confirmed: `True`
- S4.1 prerequisite confirmed: `True`
- Multiseed robustness passed: `True`
- Sparse-anchor robustness passed: `True`
- Affine-bias robustness passed: `True`
- No-auxiliary baseline robustness passed: `True`
- Controls passed: `True`
- Auxiliary leakage detected: `False`
- Human-authored outcomes detected: `False`

## 12. What was NOT shown
- No substrate was found.
- No derived world-model was shown.
- No LLM training is allowed.
- No semantic boundary generator was implemented.
- No claim that objective/perceptual separation is generally possible.
- No claim that real-world perception can be disentangled by this toy result.
- No claim that auxiliary variables solve grounding.
- No claim that synthetic identifiability transfers to internet-scale data.
- No claim that viability coloring is truth.
- No claim that passing B1.1 proves the project goal.
- No claim that affine/sparse-anchor toy robustness proves real-world robustness.

## 13. Downstream permission
If accepted, this result permits only a B1.1 postmortem or a B2 relational order-dimension gate specification. It does not permit LLM training, substrate claims, derivability claims, semantic boundary generator claims, real-world transfer claims, or general disentanglement claims.

## 14. Durable result
B1.1 produced a bounded synthetic robustness signal: in this toy construction, auxiliary calibration remained useful under the preregistered robustness checks, and the negative controls did not recover above their thresholds.
