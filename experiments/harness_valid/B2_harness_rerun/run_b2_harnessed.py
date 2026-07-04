"""Re-run B2 / B2.1 (relational order-dimension) THROUGH the full gate_harness.

Uses the finding-#7-fixed anchor graph (relational_order_toy_fixed). Original
B2 dir left untouched as audit evidence. Final seeds are disjoint from the sanity
seed (88880000) used earlier to confirm the pipeline.

Honesty expectations, stated before running:
  - recovery and the LABEL-FREE order-dimension classifier should PASS over seeds
    (the B2.1 repair removed the variant argument; that part was real);
  - BUT the 3D control's UNDERDIMENSIONED verdict is scored against 3D truth via a
    harness-provided ``truth_axes=3`` hint (finding #6). The evaluation oracle will
    catch it and the decision.json MUST carry
    ``classification_success_depends_on_harness_hint: true`` — disclosing that the
    3D "detection" is evaluation-driven, not unsupervised recovery.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

import relational_order_toy_fixed as B2  # noqa: E402
from gate_harness import calibration_audit as CA  # noqa: E402
from gate_harness import evaluation_oracle as EO  # noqa: E402
from gate_harness import leakage_scanner as LS  # noqa: E402
from gate_harness import runner as RUN  # noqa: E402
from gate_harness import seed_policy as SP  # noqa: E402
from gate_harness import tautology_check as TC  # noqa: E402
from gate_harness import verify_decision as VD  # noqa: E402

SEED_COUNT = 24
FINAL_SEEDS = [B2.SEED_START + 10 * i for i in range(SEED_COUNT)]  # disjoint from sanity 88880000

TH = {
    "no_aux_relation_f1_max": 0.60,
    "with_aux_relation_f1_min": 0.90,
    "relation_f1_improvement_min": 0.30,
    "sparse_anchor_relation_f1_min": 0.85,
    "recovery_pass_fraction_min": 0.80,
    "order_dimension_pass_fraction_min": 0.80,
    "controls_pass_fraction_min": 0.80,
    "information_ratio_min": 0.50,
    "max_anchor_fraction_sparse": 0.15,
    "seed_count_min": SP.MIN_SEEDS_FOR_CORE_METRIC,
}

# Label-free fit/classify path — the leakage scanner must clear these of truth names.
FIT_PATH_FUNCTIONS = [
    B2.classify_order_proxy,
    B2.calibrated_coordinates,
    B2.complete_transforms,
    B2.sparse_transforms,
    B2.relation_from_coords,
    B2.raw_coordinates,
    B2.learner_view,
]
EVALUATION_ENTRYPOINTS = ["evaluate_coords"]


def _mean(xs):
    return sum(xs) / len(xs)


def _anchor_records(mode):
    return [(iid, o) for iid, obs, x, y in B2.anchor_specs(mode) for o in obs]


def experiment_fn():
    rec_rows, cls_rows, ctrl_rows = [], [], []
    for seed in FINAL_SEEDS:
        prim = B2.run_primary_seed(seed, anchor_mode="complete")
        sparse = B2.generate_dataset(seed, anchor_mode="sparse", variant="product2d")
        sparse_f1 = B2.evaluate_coords(sparse["records"], B2.calibrated_coordinates(sparse["records"], "sparse"))["f1"]
        recovery_ok = (
            prim["no_aux"]["f1"] <= TH["no_aux_relation_f1_max"]
            and prim["with_aux"]["f1"] >= TH["with_aux_relation_f1_min"]
            and prim["improvement"] >= TH["relation_f1_improvement_min"]
            and sparse_f1 >= TH["sparse_anchor_relation_f1_min"]
        )
        rec_rows.append({"seed": seed, "no_aux_f1": prim["no_aux"]["f1"], "with_aux_f1": prim["with_aux"]["f1"],
                         "sparse_f1": sparse_f1, "passed": recovery_ok})
        cls_rows.append({"seed": seed, "passed": B2.run_order_dimension_suite(seed)["passed"]})
        ctrl_rows.append({"seed": seed, "passed": B2.run_controls(seed)["passed"]})

    rec_frac = _mean([1.0 if r["passed"] else 0.0 for r in rec_rows])
    cls_frac = _mean([1.0 if r["passed"] else 0.0 for r in cls_rows])
    ctrl_frac = _mean([1.0 if r["passed"] else 0.0 for r in ctrl_rows])

    raw_pass = (
        rec_frac >= TH["recovery_pass_fraction_min"]
        and cls_frac >= TH["order_dimension_pass_fraction_min"]
        and ctrl_frac >= TH["controls_pass_fraction_min"]
    )
    seed_report = SP.enforce_seed_policy([
        {"metric": "recovery_relation_f1", "role": "core", "seeds": SEED_COUNT, "pass_fail": "PASS" if rec_frac >= TH["recovery_pass_fraction_min"] else "FAIL"},
        {"metric": "order_dimension_classification", "role": "core", "seeds": SEED_COUNT, "pass_fail": "PASS" if cls_frac >= TH["order_dimension_pass_fraction_min"] else "FAIL"},
    ])
    verdicts = {m: v["verdict"] for m, v in seed_report["per_metric"].items()}
    overall = "PASS" if (raw_pass and all(v == "PASS" for v in verdicts.values())) else "FAIL_OR_INSUFFICIENT"

    return {
        "gate": "B2_harness_rerun",
        "decision": f"B2.1-{overall}-LABEL-FREE-ORDER-DIMENSION",
        "seed_count": SEED_COUNT,
        "final_seeds": FINAL_SEEDS,
        "recovery_pass_fraction": rec_frac,
        "order_dimension_pass_fraction": cls_frac,
        "controls_pass_fraction": ctrl_frac,
        "mean_no_aux_f1": _mean([r["no_aux_f1"] for r in rec_rows]),
        "mean_with_aux_f1": _mean([r["with_aux_f1"] for r in rec_rows]),
        "mean_sparse_f1": _mean([r["sparse_f1"] for r in rec_rows]),
        "seed_policy": seed_report,
        "per_metric_verdicts": verdicts,
        "anchor_fraction_sparse": len(_anchor_records("sparse")) / (B2.ITEMS_PER_OBSERVER * len(B2.OBSERVERS)),
        "thresholds": TH,
    }


def main():
    # calibration audit (finding #7) — before any learner
    CA.assert_sparse_not_heavier_than_complete(_anchor_records("sparse"), _anchor_records("complete"))
    CA.assert_minimal_calibration(_anchor_records("sparse"), [0] * (B2.ITEMS_PER_OBSERVER * len(B2.OBSERVERS)),
                                  max_anchor_fraction=TH["max_anchor_fraction_sparse"])

    # leakage scan of the label-free fit/classify path
    leakage = LS.assert_no_fit_path_leakage(FIT_PATH_FUNCTIONS)

    # tautology pre-check (scalar projection of the relational world)
    nav = [r for r in B2.generate_dataset(FINAL_SEEDS[0], anchor_mode="complete", variant="product2d")["records"] if not r["is_anchor"]]
    tautology = TC.tautology_precheck([(r["obs_x"] + r["obs_y"]) / 2 for r in nav], [r["z_value"] for r in nav], TH)

    # evaluation-oracle scan (finding #6) — catches truth_axes=3 hints
    oracle = EO.scan_evaluation_call_sites(B2, EVALUATION_ENTRYPOINTS)

    decision = RUN.run_gate(
        HERE,
        experiment_fn,
        leakage_report=leakage,
        tautology_report=tautology,
        evaluation_oracle_log=oracle["evaluation_oracle_log"],
    )
    valid, reasons = VD.verify_decision(HERE / "decision.json")

    print(json.dumps(decision, indent=2, sort_keys=True))
    print("\nleakage_scan.passed      =", leakage["passed"])
    print("evaluation_oracle hints  =", [(e["hint_name"], e["hint_value"]) for e in oracle["evaluation_oracle_log"]])
    print("verify_decision          =", "VALID" if valid else f"INVALID {reasons}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
