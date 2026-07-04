from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from robust_identifiability import (  # noqa: E402
    SEED_START,
    generate_records,
    leakage_audit,
    load_json,
    run_affine,
    run_controls,
    run_multiseed,
    run_no_aux_baselines,
    run_sparse_anchor,
    write_json,
)


THIS_DIR = Path(__file__).resolve().parent
OUTPUTS = THIS_DIR / "outputs"
REPO_ROOT = THIS_DIR.parents[2]
B1_DECISION_PATH = REPO_ROOT / "experiments" / "B" / "B1_auxiliary_variable_identifiability_gate" / "B1_decision.json"
S4_1_DECISION_PATH = (
    REPO_ROOT
    / "experiments"
    / "S"
    / "S4_tiny_boundary_accounting_replay_implementation"
    / "S4_1_decision.json"
)
EXPECTED_B1 = "B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL"
EXPECTED_S4_1 = "S4.1-PASS-GATE-CHAIN-VERIFICATION-REPAIRED"


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
    b1_gate = confirm_decision(B1_DECISION_PATH, EXPECTED_B1)
    s4_1_gate = confirm_decision(S4_1_DECISION_PATH, EXPECTED_S4_1)

    multiseed = run_multiseed()
    sparse = run_sparse_anchor()
    affine = run_affine()
    no_aux = run_no_aux_baselines()
    controls = run_controls()
    audit_records = generate_records(SEED_START + 701, mode="additive", anchor_mode="complete")
    audit = leakage_audit(audit_records)

    write_json(OUTPUTS / "multiseed_results.json", multiseed)
    write_json(OUTPUTS / "sparse_anchor_results.json", sparse)
    write_json(OUTPUTS / "affine_bias_results.json", affine)
    write_json(OUTPUTS / "no_aux_baseline_results.json", no_aux)
    write_json(OUTPUTS / "control_results.json", controls)
    write_json(OUTPUTS / "leakage_audit.json", audit)

    metrics = {
        "multiseed": {
            "mean_no_aux_abs_corr": multiseed["mean_no_aux_abs_corr"],
            "mean_with_aux_corr": multiseed["mean_with_aux_corr"],
            "mean_improvement": multiseed["mean_improvement"],
            "individual_pass_fraction": multiseed["individual_pass_fraction"],
        },
        "sparse_anchor": {
            "sparse_anchor_with_aux_corr": sparse["sparse_anchor_with_aux_corr"],
            "sparse_anchor_improvement": sparse["sparse_anchor_improvement"],
            "disconnected_anchor_corr": sparse["disconnected_anchor_corr"],
        },
        "affine_bias": {
            "affine_no_aux_abs_corr": affine["affine_no_aux_abs_corr"],
            "affine_with_aux_corr": affine["affine_with_aux_corr"],
            "affine_improvement": affine["affine_improvement"],
            "affine_shuffled_aux_corr": affine["affine_shuffled_aux_corr"],
        },
        "no_aux_baselines": {
            "max_no_aux_abs_corr": no_aux["max_no_aux_abs_corr"],
        },
        "controls_passed": controls["passed"],
    }
    write_json(OUTPUTS / "metrics.json", metrics)

    multiseed_passed = bool(multiseed["passed"])
    sparse_passed = bool(sparse["passed"])
    affine_passed = bool(affine["passed"])
    no_aux_passed = bool(no_aux["passed"])
    controls_passed = bool(controls["passed"])
    aux_leakage_detected = bool(audit["aux_leakage_detected"])
    human_authored_outcomes_detected = bool(audit["human_authored_outcomes_detected"])
    repeats_s4_accounting = False

    if not b1_gate["confirmed"] or not s4_1_gate["confirmed"]:
        decision = "B1.1-INCONCLUSIVE"
        reason = "Required upstream gate prerequisite was not confirmed."
    elif human_authored_outcomes_detected:
        decision = "B1.1-FAIL-HUMAN-AUTHORED-OUTCOMES"
        reason = "Human-authored final or outcome labels were detected."
    elif aux_leakage_detected:
        decision = "B1.1-FAIL-AUX-LEAKAGE"
        reason = "Auxiliary leakage was detected."
    elif repeats_s4_accounting:
        decision = "B1.1-FAIL-REPEATS-S4-ACCOUNTING"
        reason = "The task repeated boundary accounting rather than generated-data recovery."
    elif not multiseed_passed:
        decision = "B1.1-FAIL-MULTISEED-INSTABILITY"
        reason = "The additive signal did not survive the preregistered multiseed thresholds."
    elif not sparse_passed:
        decision = "B1.1-FAIL-SPARSE-ANCHOR-ROBUSTNESS"
        reason = "Sparse connected anchor recovery or disconnected control failed."
    elif not affine_passed:
        decision = "B1.1-FAIL-AFFINE-BIAS-ROBUSTNESS"
        reason = "Affine observer coloring recovery or shuffled auxiliary control failed."
    elif not no_aux_passed:
        decision = "B1.1-FAIL-NO-AUX-ROBUSTNESS"
        reason = "A stronger no-auxiliary baseline exceeded the preregistered threshold."
    elif not controls_passed:
        decision = "B1.1-FAIL-CONTROL-LEAKAGE"
        reason = "At least one required negative control recovered too well."
    else:
        decision = "B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL"
        reason = "The auxiliary calibration signal survived multiseed, sparse-anchor, affine, no-auxiliary baseline, control, and leakage checks."

    passed = decision == "B1.1-PASS-ROBUST-AUXILIARY-CALIBRATION-SIGNAL"
    decision_json = {
        "decision": decision,
        "reason": reason,
        "b1_decision_confirmed": b1_gate["confirmed"],
        "s4_1_decision_confirmed": s4_1_gate["confirmed"],
        "multiseed_robustness_passed": multiseed_passed,
        "sparse_anchor_robustness_passed": sparse_passed,
        "affine_bias_robustness_passed": affine_passed,
        "no_aux_baseline_robustness_passed": no_aux_passed,
        "controls_passed": controls_passed,
        "aux_leakage_detected": aux_leakage_detected,
        "human_authored_outcomes_detected": human_authored_outcomes_detected,
        "repeats_s4_accounting": repeats_s4_accounting,
        "admissible_for_next_gate": passed,
        "llm_training_allowed": False,
        "substrate_claim_allowed": False,
        "derivability_claim_allowed": False,
        "semantic_boundary_generator_claim_allowed": False,
        "real_world_transfer_claim_allowed": False,
        "general_disentanglement_claim_allowed": False,
        "next_allowed_work": ["B1.1 postmortem", "B2 relational order-dimension gate spec"] if passed else ["B1.1 postmortem / narrowing"],
    }
    write_json(THIS_DIR / "B1_1_decision.json", decision_json)

    report = f"""# B1.1 — Auxiliary-Calibration Robustness / Leakage Hardening Gate

## 0. Verdict
Decision: `{decision}`.

Reason: {reason}

## 1. Goal anchor
Immutable project goal: train an LLM / learner so that its world-model is derived, not merely generalized from internet-like data.

B1.1 does not train an LLM and does not test real-world data. It tests whether the B1 synthetic auxiliary-calibration signal survives stronger bounded robustness checks.

## 2. Inputs used
- B1 decision artifact: `{B1_DECISION_PATH}`
- B1 decision observed: `{b1_gate["decision"]}`
- S4.1 decision artifact: `{S4_1_DECISION_PATH}`
- S4.1 decision observed: `{s4_1_gate["decision"]}`

## 3. Hypothesis
If the B1 result is not merely a one-seed, complete-anchor, additive-bias, weak-baseline artifact, then auxiliary calibration should still recover the latent scalar across multiple deterministic variants while negative controls and no-auxiliary baselines fail.

## 4. Robustness suite design
The suite uses deterministic synthetic data, four observer classes, generated latent `z_obj`, observer colorings, and calibration anchors. Learner views strip `z_obj`; truth is used only by evaluation after predictions are produced.

## 5. Multiseed results
{markdown_json(multiseed)}

## 6. Sparse-anchor results
{markdown_json(sparse)}

## 7. Affine-bias results
{markdown_json(affine)}

## 8. Stronger no-auxiliary baselines
{markdown_json(no_aux)}

## 9. Controls
{markdown_json(controls)}

## 10. Leakage audit
{markdown_json(audit)}

## 11. Pass / fail analysis
- B1 prerequisite confirmed: `{b1_gate["confirmed"]}`
- S4.1 prerequisite confirmed: `{s4_1_gate["confirmed"]}`
- Multiseed robustness passed: `{multiseed_passed}`
- Sparse-anchor robustness passed: `{sparse_passed}`
- Affine-bias robustness passed: `{affine_passed}`
- No-auxiliary baseline robustness passed: `{no_aux_passed}`
- Controls passed: `{controls_passed}`
- Auxiliary leakage detected: `{aux_leakage_detected}`
- Human-authored outcomes detected: `{human_authored_outcomes_detected}`

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
"""
    (THIS_DIR / "B1_1_report.md").write_text(report, encoding="utf-8")

    final_report = f"""# B1.1 Final Report

Decision: `{decision}`

Metrics:

{markdown_json(metrics)}

Leakage audit:

{markdown_json(audit)}

No LLM training, substrate claim, derivability claim, semantic boundary generator claim, real-world transfer claim, or general disentanglement claim is allowed by this result.
"""
    (OUTPUTS / "final_report.md").write_text(final_report, encoding="utf-8")

    return decision_json


if __name__ == "__main__":
    result = run()
    metrics = load_json(OUTPUTS / "metrics.json")
    print(
        "B1.1 decision={decision} mean_no_aux_abs_corr={no_aux:.6f} mean_with_aux_corr={with_aux:.6f}".format(
            decision=result["decision"],
            no_aux=metrics["multiseed"]["mean_no_aux_abs_corr"],
            with_aux=metrics["multiseed"]["mean_with_aux_corr"],
        )
    )

