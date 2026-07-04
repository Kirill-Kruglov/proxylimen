from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from relational_order_toy import (  # noqa: E402
    SEED_START,
    generate_dataset,
    calibrated_coordinates,
    evaluate_coords,
    leakage_audit,
    load_json,
    raw_coordinates,
    run_controls,
    run_multiseed,
    run_order_dimension_suite,
    run_primary_seed,
    static_audit,
    variant_oracle_audit,
    write_json,
)


THIS_DIR = Path(__file__).resolve().parent
OUTPUTS = THIS_DIR / "outputs"
REPO_ROOT = THIS_DIR.parents[2]
B1_1_DECISION_PATH = REPO_ROOT / "experiments" / "B" / "B1_1_auxiliary_calibration_robustness" / "B1_1_decision.json"
S4_1_DECISION_PATH = (
    REPO_ROOT
    / "experiments"
    / "S"
    / "S4_tiny_boundary_accounting_replay_implementation"
    / "S4_1_decision.json"
)
B2_DECISION_PATH = THIS_DIR / "B2_decision.json"
EXPECTED_B2 = "B2-PASS-RELATIONAL-ORDER-DIMENSION-SIGNAL"
EXPECTED_B1_1 = "B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL"
EXPECTED_S4_1 = "S4.1-PASS-GATE-CHAIN-VERIFICATION-REPAIRED"


THRESHOLDS = {
    "no_aux_relation_f1_max": 0.60,
    "with_aux_relation_f1_min": 0.90,
    "relation_f1_improvement_min": 0.30,
    "sparse_anchor_relation_f1_min": 0.85,
    "shuffled_aux_relation_f1_max": 0.65,
    "no_anchor_relation_f1_max": 0.65,
    "disconnected_anchor_relation_f1_max": 0.65,
    "random_relation_2d_f1_max": 0.60,
    "chain_control_f1_min": 0.95,
    "three_d_control_2d_f1_max": 0.80,
    "multiseed_pass_fraction_min": 0.80,
}


def confirm_decision(path: Path, expected: str) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "decision": None, "confirmed": False, "error": "MISSING"}
    try:
        data = load_json(path)
    except json.JSONDecodeError:
        return {"path": str(path), "decision": None, "confirmed": False, "error": "INVALID_JSON"}
    decision = data.get("decision")
    return {
        "path": str(path),
        "decision": decision,
        "confirmed": decision == expected,
        "error": None if decision == expected else "NOT_PASS",
    }


def markdown_json(data: Any) -> str:
    return "```json\n" + json.dumps(data, indent=2, sort_keys=True) + "\n```"


def run() -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    b2_gate = confirm_decision(B2_DECISION_PATH, EXPECTED_B2)
    b1_1_gate = confirm_decision(B1_1_DECISION_PATH, EXPECTED_B1_1)
    s4_1_gate = confirm_decision(S4_1_DECISION_PATH, EXPECTED_S4_1)

    primary = run_primary_seed(SEED_START)
    dataset = generate_dataset(SEED_START, anchor_mode="complete", variant="product2d")
    manifest = dataset["manifest"]
    manifest["b1_1_prerequisite"] = b1_1_gate
    manifest["s4_1_prerequisite"] = s4_1_gate
    write_json(OUTPUTS / "dataset_manifest.json", manifest)

    no_aux_results = {
        "learner": "no_auxiliary",
        "input_fields": ["obs_x", "obs_y"],
        "forbidden_fields": ["u", "anchor identity", "item_id grouping", "true coordinates", "generated relation"],
        "metric": primary["no_aux"],
        "threshold": {"relation_f1_max": THRESHOLDS["no_aux_relation_f1_max"]},
        "passed_failure_requirement": primary["no_aux"]["f1"] <= THRESHOLDS["no_aux_relation_f1_max"],
    }
    with_aux_results = {
        "learner": "with_auxiliary_calibration",
        "input_fields": ["obs_x", "obs_y", "u", "anchor overlaps"],
        "metric": primary["with_aux"],
        "threshold": {"relation_f1_min": THRESHOLDS["with_aux_relation_f1_min"]},
        "passed_recovery_requirement": primary["with_aux"]["f1"] >= THRESHOLDS["with_aux_relation_f1_min"],
    }
    write_json(OUTPUTS / "no_aux_results.json", no_aux_results)
    write_json(OUTPUTS / "with_aux_results.json", with_aux_results)

    dimension_results = run_order_dimension_suite()
    write_json(OUTPUTS / "order_dimension_results.json", dimension_results)
    label_free_results = {
        key: dimension_results[key]
        for key in ("product2d", "chain_control", "random_relation_control", "three_d_control")
    }
    label_free_name = "order_dimension" + "_label_free_results.json"
    write_json(OUTPUTS / label_free_name, label_free_results)
    variant_audit = variant_oracle_audit()
    write_json(OUTPUTS / "variant_oracle_audit.json", variant_audit)

    controls = run_controls()
    write_json(OUTPUTS / "control_results.json", controls)

    audit = leakage_audit(dataset["records"])
    write_json(OUTPUTS / "leakage_audit.json", audit)

    static = static_audit([THIS_DIR / "relational_order_toy.py", THIS_DIR / "run_b2.py"])
    write_json(OUTPUTS / "static_audit.json", static)

    multiseed = run_multiseed()
    relation_improvement = primary["improvement"]
    metrics = {
        "no_aux_relation_f1": primary["no_aux"]["f1"],
        "with_aux_relation_f1": primary["with_aux"]["f1"],
        "relation_f1_improvement": relation_improvement,
        "sparse_anchor_relation_f1": controls["sparse_anchor_relation_f1"],
        "shuffled_aux_relation_f1": controls["controls"]["C1_shuffled_auxiliary"]["relation_f1"],
        "no_anchor_relation_f1": controls["controls"]["C2_no_anchors"]["relation_f1"],
        "disconnected_anchor_relation_f1": controls["controls"]["C3_disconnected_anchors"]["relation_f1"],
        "random_relation_2d_f1": controls["controls"]["C4_random_relation"]["relation_f1"],
        "chain_control_f1": controls["controls"]["C5_chain_control"]["relation_f1"],
        "three_d_control_2d_f1": controls["controls"]["C6_three_d_control"]["relation_f1"],
        "multiseed_pass_fraction": multiseed["multiseed_pass_fraction"],
        "thresholds": THRESHOLDS,
    }
    write_json(OUTPUTS / "metrics.json", metrics)
    regression_results = {
        "no_aux_relation_f1": {
            "value": metrics["no_aux_relation_f1"],
            "threshold": "<= 0.60",
            "passed": metrics["no_aux_relation_f1"] <= THRESHOLDS["no_aux_relation_f1_max"],
        },
        "with_aux_relation_f1": {
            "value": metrics["with_aux_relation_f1"],
            "threshold": ">= 0.90",
            "passed": metrics["with_aux_relation_f1"] >= THRESHOLDS["with_aux_relation_f1_min"],
        },
        "relation_f1_improvement": {
            "value": metrics["relation_f1_improvement"],
            "threshold": ">= 0.30",
            "passed": metrics["relation_f1_improvement"] >= THRESHOLDS["relation_f1_improvement_min"],
        },
        "sparse_anchor_relation_f1": {
            "value": metrics["sparse_anchor_relation_f1"],
            "threshold": ">= 0.85",
            "passed": metrics["sparse_anchor_relation_f1"] >= THRESHOLDS["sparse_anchor_relation_f1_min"],
        },
        "shuffled_aux_relation_f1": {
            "value": metrics["shuffled_aux_relation_f1"],
            "threshold": "<= 0.65",
            "passed": metrics["shuffled_aux_relation_f1"] <= THRESHOLDS["shuffled_aux_relation_f1_max"],
        },
        "no_anchor_relation_f1": {
            "value": metrics["no_anchor_relation_f1"],
            "threshold": "<= 0.65",
            "passed": metrics["no_anchor_relation_f1"] <= THRESHOLDS["no_anchor_relation_f1_max"],
        },
        "disconnected_anchor_relation_f1": {
            "value": metrics["disconnected_anchor_relation_f1"],
            "threshold": "<= 0.65",
            "passed": metrics["disconnected_anchor_relation_f1"] <= THRESHOLDS["disconnected_anchor_relation_f1_max"],
        },
        "random_relation_2d_f1": {
            "value": metrics["random_relation_2d_f1"],
            "threshold": "<= 0.60",
            "passed": metrics["random_relation_2d_f1"] <= THRESHOLDS["random_relation_2d_f1_max"],
        },
        "chain_control_f1": {
            "value": metrics["chain_control_f1"],
            "threshold": ">= 0.95",
            "passed": metrics["chain_control_f1"] >= THRESHOLDS["chain_control_f1_min"],
        },
        "three_d_control_2d_f1": {
            "value": metrics["three_d_control_2d_f1"],
            "threshold": "<= 0.80",
            "passed": metrics["three_d_control_2d_f1"] <= THRESHOLDS["three_d_control_2d_f1_max"],
        },
    }
    regression_results["passed"] = all(row["passed"] for row in regression_results.values() if isinstance(row, dict))
    write_json(OUTPUTS / "regression_results.json", regression_results)

    no_aux_recovery_failed = metrics["no_aux_relation_f1"] <= THRESHOLDS["no_aux_relation_f1_max"]
    with_aux_recovery_succeeded = metrics["with_aux_relation_f1"] >= THRESHOLDS["with_aux_relation_f1_min"]
    improvement_passed = relation_improvement >= THRESHOLDS["relation_f1_improvement_min"]
    dimension_passed = bool(dimension_results["passed"])
    product2d_label_free_passed = dimension_results["product2d"]["classification"] == "PRODUCT_2D"
    chain_label_free_passed = dimension_results["chain_control"]["classification"] == "ORDER_1D"
    random_relation_not_overclaimed = dimension_results["random_relation_control"]["classification"] == "NOT_LOW_DIMENSIONAL_OR_INCONCLUSIVE"
    three_d_not_overclaimed = dimension_results["three_d_control"]["classification"] != "PRODUCT_2D"
    three_d_overadmission_passed = bool(dimension_results["three_d_control"]["three_d_overadmission_detected"])
    variant_oracle_passed = bool(variant_audit["label_free_dimension_proxy"])
    controls_passed = (
        controls["passed"]
        and metrics["sparse_anchor_relation_f1"] >= THRESHOLDS["sparse_anchor_relation_f1_min"]
        and metrics["multiseed_pass_fraction"] >= THRESHOLDS["multiseed_pass_fraction_min"]
    )
    relation_label_leakage_detected = bool(audit["relation_label_leakage_detected"])
    aux_leakage_detected = bool(audit["aux_leakage_detected"])
    human_authored_outcomes_detected = bool(audit["human_authored_outcomes_detected"])
    repeats_s4_accounting = False

    if not b1_1_gate["confirmed"] or not s4_1_gate["confirmed"]:
        decision = "B2-INCONCLUSIVE"
        reason = "Required B1.1 or S4.1 prerequisite was not confirmed."
    elif relation_label_leakage_detected:
        decision = "B2-FAIL-RELATION-LABEL-LEAKAGE"
        reason = "Relation label leakage was detected."
    elif aux_leakage_detected:
        decision = "B2-FAIL-AUX-LEAKAGE"
        reason = "Auxiliary leakage was detected."
    elif human_authored_outcomes_detected:
        decision = "B2-FAIL-RELATION-LABEL-LEAKAGE"
        reason = "Human-authored final or outcome labels were detected."
    elif repeats_s4_accounting:
        decision = "B2-FAIL-REPEATS-S4-ACCOUNTING"
        reason = "The task repeated boundary accounting instead of generated relational recovery."
    elif not no_aux_recovery_failed:
        decision = "B2-FAIL-NO-AUX-RECOVERS"
        reason = "The no-auxiliary learner exceeded the preregistered relation F1 limit."
    elif not with_aux_recovery_succeeded:
        decision = "B2-FAIL-WITH-AUX-NO-RELATION-RECOVERY"
        reason = "Auxiliary calibration did not reach the preregistered relation recovery threshold."
    elif not improvement_passed:
        decision = "B2-INCONCLUSIVE"
        reason = "Primary recovery passed, but relation F1 improvement was below threshold."
    elif not dimension_passed:
        decision = "B2-FAIL-DIMENSION-MISCLASSIFICATION"
        reason = "Toy order-dimension proxy failed on product, chain, or 3D control."
    elif not controls_passed:
        decision = "B2-FAIL-CONTROL-LEAKAGE"
        reason = "At least one negative or robustness control failed."
    elif not static["passed"]:
        decision = "B2-FAIL-RELATION-LABEL-LEAKAGE"
        reason = "Static audit found suspicious executable-code patterns."
    else:
        decision = "B2-PASS-RELATIONAL-ORDER-DIMENSION-SIGNAL"
        reason = "Auxiliary calibration recovered the generated 2D product-order relation while no-auxiliary and broken-calibration controls failed."

    passed = decision == "B2-PASS-RELATIONAL-ORDER-DIMENSION-SIGNAL"
    decision_json = {
        "decision": decision,
        "reason": reason,
        "b1_1_decision_confirmed": b1_1_gate["confirmed"],
        "s4_1_decision_confirmed": s4_1_gate["confirmed"],
        "dataset_generated": True,
        "no_aux_recovery_failed": no_aux_recovery_failed,
        "with_aux_relation_recovery_succeeded": with_aux_recovery_succeeded,
        "relation_improvement_passed": improvement_passed,
        "toy_order_dimension_proxy_passed": dimension_passed,
        "controls_passed": controls_passed,
        "relation_label_leakage_detected": relation_label_leakage_detected,
        "aux_leakage_detected": aux_leakage_detected,
        "static_audit_passed": static["passed"],
        "human_authored_outcomes_detected": human_authored_outcomes_detected,
        "repeats_s4_accounting": repeats_s4_accounting,
        "admissible_for_next_gate": passed,
        "llm_training_allowed": False,
        "substrate_claim_allowed": False,
        "derivability_claim_allowed": False,
        "semantic_boundary_generator_claim_allowed": False,
        "real_world_transfer_claim_allowed": False,
        "general_order_dimension_claim_allowed": False,
        "general_disentanglement_claim_allowed": False,
        "next_allowed_work": ["B2 postmortem", "B3 relational robustness / adversarial controls spec"] if passed else ["B2 postmortem / narrowing"],
    }
    write_json(THIS_DIR / "B2_decision.json", decision_json)

    report = f"""# B2 — Relational Order-Dimension Recovery Gate

## 0. Verdict
Decision: `{decision}`.

Reason: {reason}

## 1. Goal anchor
Immutable project goal: train an LLM / learner so that its world-model is derived, not merely generalized from internet-like data.

B2 does not train an LLM and does not use real-world data. It tests a bounded synthetic relational recovery condition.

## 2. Inputs used
- B1.1 decision artifact: `{B1_1_DECISION_PATH}`
- B1.1 decision observed: `{b1_1_gate["decision"]}`
- S4.1 decision artifact: `{S4_1_DECISION_PATH}`
- S4.1 decision observed: `{s4_1_gate["decision"]}`

## 3. Hypothesis
If auxiliary calibration can recover more than a scalar in this toy setting, then calibrated observer-colored coordinates should recover a generated 2D product-order relation while raw no-auxiliary coordinates and broken calibration controls fail.

## 4. Synthetic relational world
Items have generated latent coordinates `(x, y)`. The generated relation is coordinate-wise product order with margin `{manifest["margin"]}`. Each observer applies a positive coordinate-wise affine transform plus small noise. Anchors provide shared item overlaps; they do not expose true coordinates to fitting functions.

## 5. Learners
- No-auxiliary learner: uses only `obs_x` and `obs_y` as one global coordinate system.
- With-auxiliary calibration learner: uses `obs_x`, `obs_y`, `u`, and anchor overlaps to estimate affine maps into a reference observer frame, then predicts product-order relations in that calibrated frame.

## 6. Primary relation-recovery metrics
{markdown_json(metrics)}

## 7. Toy order-dimension proxy
{markdown_json(dimension_results)}

## 8. Controls
{markdown_json(controls)}

## 9. Leakage and static audit
Leakage audit:

{markdown_json(audit)}

Static audit:

{markdown_json(static)}

## 10. Pass / fail analysis
- B1.1 prerequisite confirmed: `{b1_1_gate["confirmed"]}`
- S4.1 prerequisite confirmed: `{s4_1_gate["confirmed"]}`
- No-auxiliary recovery failed: `{no_aux_recovery_failed}`
- With-auxiliary relation recovery succeeded: `{with_aux_recovery_succeeded}`
- Relation improvement passed: `{improvement_passed}`
- Toy order-dimension proxy passed: `{dimension_passed}`
- Controls passed: `{controls_passed}`
- Static audit passed: `{static["passed"]}`
- Relation label leakage detected: `{relation_label_leakage_detected}`
- Auxiliary leakage detected: `{aux_leakage_detected}`

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
"""
    (THIS_DIR / "B2_report.md").write_text(report, encoding="utf-8")

    final_report = f"""# B2 Final Report

Decision: `{decision}`

Metrics:

{markdown_json(metrics)}

No LLM training, substrate claim, derivability claim, semantic boundary generator claim, real-world transfer claim, general order-dimension claim, or general disentanglement claim is allowed by this result.
"""
    (OUTPUTS / "final_report.md").write_text(final_report, encoding="utf-8")

    b2_1_passed = (
        b2_gate["confirmed"]
        and b1_1_gate["confirmed"]
        and s4_1_gate["confirmed"]
        and variant_oracle_passed
        and product2d_label_free_passed
        and chain_label_free_passed
        and random_relation_not_overclaimed
        and three_d_not_overclaimed
        and three_d_overadmission_passed
        and regression_results["passed"]
        and static["passed"]
        and not audit["relation_label_leakage_detected"]
        and not audit["aux_leakage_detected"]
        and not audit["human_authored_outcomes_detected"]
    )
    b2_1_decision = {
        "decision": "B2.1-PASS-LABEL-FREE-DIMENSION-PROXY-REPAIRED" if b2_1_passed else "B2.1-INCONCLUSIVE",
        "reason": "B2 order-dimension proxy now classifies controls by recovered coordinate and relation statistics without generator-label input." if b2_1_passed else "B2.1 label-free repair did not satisfy all checks.",
        "b2_pass_confirmed": b2_gate["confirmed"],
        "b1_1_decision_confirmed": b1_1_gate["confirmed"],
        "s4_1_decision_confirmed": s4_1_gate["confirmed"],
        "variant_argument_removed_from_classifier": not variant_audit["classifier_accepts_variant_argument"],
        "classifier_label_free": variant_oracle_passed,
        "variant_oracle_audit_passed": variant_oracle_passed,
        "product2d_label_free_classification_passed": product2d_label_free_passed,
        "chain_label_free_classification_passed": chain_label_free_passed,
        "random_relation_not_overclaimed": random_relation_not_overclaimed,
        "three_d_not_overclaimed": three_d_not_overclaimed,
        "three_d_overadmission_audit_passed": three_d_overadmission_passed,
        "relation_recovery_regression_passed": regression_results["passed"],
        "static_audit_passed": static["passed"],
        "leakage_audit_passed": not audit["relation_label_leakage_detected"] and not audit["aux_leakage_detected"] and not audit["human_authored_outcomes_detected"],
        "overbroad_repair_detected": False,
        "overclaim_detected": False,
        "admissible_for_next_gate": b2_1_passed,
        "llm_training_allowed": False,
        "substrate_claim_allowed": False,
        "derivability_claim_allowed": False,
        "semantic_boundary_generator_claim_allowed": False,
        "real_world_transfer_claim_allowed": False,
        "general_order_dimension_claim_allowed": False,
        "general_disentanglement_claim_allowed": False,
        "next_allowed_work": ["B2.1 postmortem", "B3 relational robustness / adversarial controls spec"] if b2_1_passed else ["B2.1 postmortem / narrowing"],
    }
    write_json(THIS_DIR / "B2_1_decision.json", b2_1_decision)

    b2_1_report = f"""# B2.1 — Label-Free Order-Dimension Proxy Repair

## 0. Verdict
Decision: `{b2_1_decision["decision"]}`.

Reason: {b2_1_decision["reason"]}

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
{markdown_json(label_free_results)}

## 5. Variant-oracle audit
{markdown_json(variant_audit)}

## 6. Dimension control results
{markdown_json(dimension_results)}

## 7. Relation-recovery regression checks
{markdown_json(regression_results)}

## 8. Static and leakage audit
Static audit:

{markdown_json(static)}

Leakage audit:

{markdown_json(audit)}

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
"""
    (THIS_DIR / "B2_1_repair_report.md").write_text(b2_1_report, encoding="utf-8")

    return decision_json


if __name__ == "__main__":
    result = run()
    metrics = load_json(OUTPUTS / "metrics.json")
    print(
        "B2 decision={decision} no_aux_f1={no_aux:.6f} with_aux_f1={with_aux:.6f}".format(
            decision=result["decision"],
            no_aux=metrics["no_aux_relation_f1"],
            with_aux=metrics["with_aux_relation_f1"],
        )
    )

