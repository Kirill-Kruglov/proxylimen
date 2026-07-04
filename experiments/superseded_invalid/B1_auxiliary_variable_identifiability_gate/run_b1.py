from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from identifiability_toy import (  # noqa: E402
    SEED,
    audit_leakage,
    evaluate_predictions,
    generate_dataset,
    load_json,
    no_auxiliary_learner,
    shuffled_auxiliary_records,
    with_auxiliary_calibration_learner,
    without_anchor_records,
    write_json,
)


THIS_DIR = Path(__file__).resolve().parent
OUTPUTS = THIS_DIR / "outputs"
REPO_ROOT = THIS_DIR.parents[2]
S4_1_DECISION_PATH = (
    REPO_ROOT
    / "experiments"
    / "S"
    / "S4_tiny_boundary_accounting_replay_implementation"
    / "S4_1_decision.json"
)
EXPECTED_S4_1_DECISION = "S4.1-PASS-GATE-CHAIN-VERIFICATION-REPAIRED"


THRESHOLDS = {
    "no_aux_abs_corr_max": 0.30,
    "with_aux_corr_min": 0.90,
    "improvement_min": 0.60,
    "shuffled_aux_corr_max": 0.50,
    "no_anchor_with_aux_corr_max": 0.50,
    "random_world_corr_max": 0.30,
}


def confirm_s4_1_decision() -> dict[str, Any]:
    if not S4_1_DECISION_PATH.exists():
        return {"confirmed": False, "path": str(S4_1_DECISION_PATH), "decision": None, "error": "MISSING"}
    try:
        data = load_json(S4_1_DECISION_PATH)
    except json.JSONDecodeError:
        return {"confirmed": False, "path": str(S4_1_DECISION_PATH), "decision": None, "error": "INVALID_JSON"}
    decision = data.get("decision")
    return {
        "confirmed": decision == EXPECTED_S4_1_DECISION,
        "path": str(S4_1_DECISION_PATH),
        "decision": decision,
        "error": None if decision == EXPECTED_S4_1_DECISION else "NOT_PASS",
    }


def markdown_json(data: Any) -> str:
    return "```json\n" + json.dumps(data, indent=2, sort_keys=True) + "\n```"


def run() -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    s4_1 = confirm_s4_1_decision()

    dataset = generate_dataset(random_world=False, seed=SEED)
    records = dataset["records"]
    manifest = dict(dataset["manifest"])
    manifest["s4_1_prerequisite"] = s4_1
    write_json(OUTPUTS / "dataset_manifest.json", manifest)

    no_aux_predictions = no_auxiliary_learner(records)
    no_aux_eval = evaluate_predictions(records, no_aux_predictions)
    no_aux_results = {
        "learner": "no_auxiliary_learner",
        "input_fields": ["y"],
        "metric": no_aux_eval,
        "threshold": {"abs_pearson_corr_max": THRESHOLDS["no_aux_abs_corr_max"]},
        "passes_failure_requirement": no_aux_eval["abs_pearson_corr"] <= THRESHOLDS["no_aux_abs_corr_max"],
    }
    write_json(OUTPUTS / "no_aux_results.json", no_aux_results)

    with_aux_fit = with_auxiliary_calibration_learner(records)
    with_aux_eval = evaluate_predictions(records, with_aux_fit["predictions"])
    with_aux_results = {
        "learner": "with_auxiliary_calibration_learner",
        "input_fields": ["y", "u", "anchor overlaps"],
        "estimated_biases": with_aux_fit["estimated_biases"],
        "metric": with_aux_eval,
        "threshold": {"pearson_corr_min": THRESHOLDS["with_aux_corr_min"]},
        "passes_recovery_requirement": with_aux_eval["pearson_corr"] >= THRESHOLDS["with_aux_corr_min"],
    }
    write_json(OUTPUTS / "with_aux_results.json", with_aux_results)

    shuffled_records = shuffled_auxiliary_records(records)
    shuffled_fit = with_auxiliary_calibration_learner(shuffled_records)
    shuffled_eval = evaluate_predictions(shuffled_records, shuffled_fit["predictions"])

    no_anchor_records = without_anchor_records(records)
    no_anchor_fit = with_auxiliary_calibration_learner(no_anchor_records)
    no_anchor_eval = evaluate_predictions(no_anchor_records, no_anchor_fit["predictions"])

    random_world = generate_dataset(random_world=True, seed=SEED)
    random_fit = with_auxiliary_calibration_learner(random_world["records"])
    random_eval = evaluate_predictions(random_world["records"], random_fit["predictions"])

    controls = {
        "C1_shuffled_auxiliary": {
            "metric": shuffled_eval,
            "threshold": {"pearson_corr_max": THRESHOLDS["shuffled_aux_corr_max"]},
            "passed": shuffled_eval["pearson_corr"] <= THRESHOLDS["shuffled_aux_corr_max"],
        },
        "C2_no_anchor": {
            "metric": no_anchor_eval,
            "threshold": {"pearson_corr_max": THRESHOLDS["no_anchor_with_aux_corr_max"]},
            "passed": no_anchor_eval["pearson_corr"] <= THRESHOLDS["no_anchor_with_aux_corr_max"],
        },
        "C3_random_world": {
            "metric": random_eval,
            "threshold": {"pearson_corr_max": THRESHOLDS["random_world_corr_max"]},
            "passed": random_eval["pearson_corr"] <= THRESHOLDS["random_world_corr_max"],
        },
        "C4_auxiliary_leakage_audit": "see leakage_audit.json",
    }
    write_json(OUTPUTS / "control_results.json", controls)

    improvement = with_aux_eval["pearson_corr"] - no_aux_eval["abs_pearson_corr"]
    metrics = {
        "no_aux_corr": no_aux_eval["pearson_corr"],
        "no_aux_abs_corr": no_aux_eval["abs_pearson_corr"],
        "with_aux_corr": with_aux_eval["pearson_corr"],
        "improvement": improvement,
        "shuffled_aux_corr": shuffled_eval["pearson_corr"],
        "no_anchor_with_aux_corr": no_anchor_eval["pearson_corr"],
        "random_world_corr": random_eval["pearson_corr"],
        "thresholds": THRESHOLDS,
    }
    write_json(OUTPUTS / "metrics.json", metrics)

    leakage = audit_leakage(records)
    write_json(OUTPUTS / "leakage_audit.json", leakage)

    no_aux_recovery_failed = no_aux_eval["abs_pearson_corr"] <= THRESHOLDS["no_aux_abs_corr_max"]
    with_aux_recovery_succeeded = with_aux_eval["pearson_corr"] >= THRESHOLDS["with_aux_corr_min"]
    improvement_threshold_passed = improvement >= THRESHOLDS["improvement_min"]
    shuffled_aux_control_passed = controls["C1_shuffled_auxiliary"]["passed"]
    no_anchor_control_passed = controls["C2_no_anchor"]["passed"]
    random_world_control_passed = controls["C3_random_world"]["passed"]
    aux_leakage_detected = bool(leakage["leakage_detected"])
    human_authored_outcomes_detected = bool(leakage["human_authored_outcome_labels_used"])
    repeats_s4_accounting = False

    if not s4_1["confirmed"]:
        decision = "B1-INCONCLUSIVE"
        reason = "S4.1 prerequisite was not confirmed."
    elif human_authored_outcomes_detected:
        decision = "B1-FAIL-HUMAN-AUTHORED-OUTCOMES"
        reason = "Human-authored outcome labels were detected."
    elif aux_leakage_detected:
        decision = "B1-FAIL-AUX-LEAKAGE"
        reason = "Auxiliary leakage was detected."
    elif not no_aux_recovery_failed:
        decision = "B1-FAIL-NO-AUX-RECOVERS"
        reason = "The no-auxiliary learner exceeded the preregistered correlation limit."
    elif not with_aux_recovery_succeeded:
        decision = "B1-FAIL-WITH-AUX-NO-RECOVERY"
        reason = "The auxiliary calibration learner did not reach the preregistered correlation threshold."
    elif not (shuffled_aux_control_passed and no_anchor_control_passed and random_world_control_passed):
        decision = "B1-FAIL-CONTROL-LEAKAGE"
        reason = "At least one negative control exceeded its preregistered threshold."
    elif not improvement_threshold_passed:
        decision = "B1-INCONCLUSIVE"
        reason = "Primary recovery passed, but the improvement threshold did not."
    elif repeats_s4_accounting:
        decision = "B1-FAIL-REPEATS-S4-ACCOUNTING"
        reason = "The task repeated accounting instead of synthetic recovery."
    else:
        decision = "B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL"
        reason = "No-auxiliary recovery failed, auxiliary calibration recovered the latent scalar, and controls failed as required."

    passed = decision == "B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL"
    decision_json = {
        "decision": decision,
        "reason": reason,
        "s4_1_decision_confirmed": s4_1["confirmed"],
        "dataset_generated": True,
        "no_aux_recovery_failed": no_aux_recovery_failed,
        "with_aux_recovery_succeeded": with_aux_recovery_succeeded,
        "improvement_threshold_passed": improvement_threshold_passed,
        "shuffled_aux_control_passed": shuffled_aux_control_passed,
        "no_anchor_control_passed": no_anchor_control_passed,
        "random_world_control_passed": random_world_control_passed,
        "aux_leakage_detected": aux_leakage_detected,
        "human_authored_outcomes_detected": human_authored_outcomes_detected,
        "repeats_s4_accounting": repeats_s4_accounting,
        "admissible_for_next_gate": passed,
        "llm_training_allowed": False,
        "substrate_claim_allowed": False,
        "derivability_claim_allowed": False,
        "semantic_boundary_generator_claim_allowed": False,
        "real_world_transfer_claim_allowed": False,
        "next_allowed_work": ["B1 postmortem", "B2 relational order-dimension gate spec"] if passed else ["B1 postmortem / narrowing"],
    }
    write_json(THIS_DIR / "B1_decision.json", decision_json)

    final_report = f"""# B1 Final Report

Decision: `{decision}`

Metrics:

{markdown_json(metrics)}

Controls:

{markdown_json(controls)}

Leakage audit:

{markdown_json(leakage)}

No LLM training, substrate claim, derivability claim, semantic boundary generator claim, or real-world transfer claim is allowed by this result.
"""
    (OUTPUTS / "final_report.md").write_text(final_report, encoding="utf-8")

    b1_report = f"""# B1 — Auxiliary-Variable Identifiability Gate

## 0. Verdict
Decision: `{decision}`.

Reason: {reason}

## 1. Goal anchor
Immutable project goal: train an LLM / learner so that its world-model is derived, not merely generalized from internet-like data.

B1 does not train an LLM. It only tests a synthetic identifiability condition: whether objective/perceptual separation fails without an auxiliary variable and succeeds with explicit auxiliary calibration anchors.

## 2. Inputs used
- Primary task file: `experiments/B/B1_Auxiliary-Variable_Identifiability_Gate.md`
- Gate prerequisite: `{S4_1_DECISION_PATH}`
- S4.1 decision observed: `{s4_1["decision"]}`

## 3. Hypothesis
In the synthetic world `y_i,u = z_obj_i + bias_u + noise`, raw observations alone should not recover `z_obj` under the confounded observer/item allocation. Recovery should become possible when `u` and repeated anchor overlaps identify relative observer bias.

## 4. Synthetic world design
The dataset was generated with deterministic seed `{SEED}`. Four observer classes have different additive biases. Non-anchor item allocation is confounded: U0 mostly observes low latent items, U1 lower-mid items, U2 upper-mid items, and U3 high items. Biases counteract those latent ranges so raw `y` is not a reliable objective ordering.

Calibration anchors are repeated observations across all observer classes. Anchor records provide overlap structure only; learner fitting does not read true `z_obj`.

## 5. Learners
- `no_auxiliary_learner`: uses `y` only and emits rank-normalized raw observations.
- `with_auxiliary_calibration_learner`: uses `y`, `u`, and anchor overlaps to estimate relative observer bias, then predicts `y - estimated_bias_u`.

## 6. Primary metrics
{markdown_json(metrics)}

## 7. Controls
{markdown_json(controls)}

## 8. Leakage audit
{markdown_json(leakage)}

## 9. Pass / fail analysis
- S4.1 prerequisite confirmed: `{s4_1["confirmed"]}`
- No-auxiliary recovery failed as required: `{no_aux_recovery_failed}`
- Auxiliary recovery succeeded: `{with_aux_recovery_succeeded}`
- Improvement threshold passed: `{improvement_threshold_passed}`
- Shuffled auxiliary control passed: `{shuffled_aux_control_passed}`
- No-anchor control passed: `{no_anchor_control_passed}`
- Random-world control passed: `{random_world_control_passed}`
- Auxiliary leakage detected: `{aux_leakage_detected}`
- Human-authored outcomes detected: `{human_authored_outcomes_detected}`

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
"""
    (THIS_DIR / "B1_report.md").write_text(b1_report, encoding="utf-8")

    return decision_json


if __name__ == "__main__":
    result = run()
    print(
        "B1 decision={decision} no_aux_abs_corr={no_aux:.6f} with_aux_corr={with_aux:.6f}".format(
            decision=result["decision"],
            no_aux=load_json(OUTPUTS / "metrics.json")["no_aux_abs_corr"],
            with_aux=load_json(OUTPUTS / "metrics.json")["with_aux_corr"],
        )
    )

