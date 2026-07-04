"""Re-run B1 (auxiliary-variable identifiability) THROUGH the full gate_harness.

This is the integration test: not isolated unit tests, but the whole chain —
prereg lock -> leakage scan -> tautology pre-check -> evaluation-oracle scan ->
multi-seed run -> seed policy -> provenance-signed decision.json -> verifier.

The original ``B1_auxiliary_variable_identifiability_gate/`` is left untouched as
audit evidence; we import its learner/eval code and drive it under discipline.

Honesty expectations, stated before running (so they cannot be rationalised after):
  - the recovery signal itself should survive multi-seed (it was real);
  - BUT B1's world uses bias that counteracts group centre, so the harness should
    force ``construction_may_be_tautological: true`` — a caveat the original
    decision.json never disclosed;
  - at 1 seed the primary metric would be INSUFFICIENT_SEEDS; we run 24.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIG_B1 = HERE.parent / "B1_auxiliary_variable_identifiability_gate"
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(ORIG_B1))
sys.path.insert(0, str(REPO_ROOT))

import identifiability_toy as T  # noqa: E402  (original B1 learner/eval code)
from gate_harness import evaluation_oracle as EO  # noqa: E402
from gate_harness import leakage_scanner as LS  # noqa: E402
from gate_harness import runner as RUN  # noqa: E402
from gate_harness import seed_policy as SP  # noqa: E402
from gate_harness import tautology_check as TC  # noqa: E402
from gate_harness import verify_decision as VD  # noqa: E402

SEED_COUNT = 24
THRESHOLDS = {
    "no_aux_abs_corr_max": 0.30,
    "with_aux_corr_min": 0.90,
    "improvement_min": 0.60,
    "shuffled_aux_corr_max": 0.50,
    "no_anchor_with_aux_corr_max": 0.50,
    "random_world_corr_max": 0.30,
    "information_ratio_min": 0.50,
    "seed_count_min": SP.MIN_SEEDS_FOR_CORE_METRIC,
}

# fit/predict path the leakage scanner must clear (truth fields forbidden here)
FIT_PATH_FUNCTIONS = [
    T.no_auxiliary_learner,
    T.estimate_biases_from_anchors,
    T.with_auxiliary_calibration_learner,
    T.learner_view,
]
# only these may see ground truth
EVALUATION_ENTRYPOINTS = ["evaluate_predictions"]


def _mean(values):
    return sum(values) / len(values)


def experiment_fn():
    rows = []
    for i in range(SEED_COUNT):
        records = T.generate_dataset(random_world=False, seed=T.SEED + i)["records"]
        no_aux = T.evaluate_predictions(records, T.no_auxiliary_learner(records))
        aux = T.with_auxiliary_calibration_learner(records)
        with_aux = T.evaluate_predictions(records, aux["predictions"])
        rows.append(
            {
                "seed": T.SEED + i,
                "no_aux_abs_corr": no_aux["abs_pearson_corr"],
                "with_aux_corr": with_aux["pearson_corr"],
                "improvement": with_aux["pearson_corr"] - no_aux["abs_pearson_corr"],
            }
        )
    mean_no_aux = _mean([r["no_aux_abs_corr"] for r in rows])
    mean_with_aux = _mean([r["with_aux_corr"] for r in rows])
    mean_improvement = _mean([r["improvement"] for r in rows])

    # controls (single seed, as in the original B1)
    base = T.generate_dataset(random_world=False, seed=T.SEED)["records"]
    shuffled = T.shuffled_auxiliary_records(base)
    shuffled_eval = T.evaluate_predictions(shuffled, T.with_auxiliary_calibration_learner(shuffled)["predictions"])
    no_anchor = T.without_anchor_records(base)
    no_anchor_eval = T.evaluate_predictions(no_anchor, T.with_auxiliary_calibration_learner(no_anchor)["predictions"])
    random_world = T.generate_dataset(random_world=True, seed=T.SEED)["records"]
    random_eval = T.evaluate_predictions(random_world, T.with_auxiliary_calibration_learner(random_world)["predictions"])

    controls = {
        "shuffled_aux_corr": (shuffled_eval["pearson_corr"], shuffled_eval["pearson_corr"] <= THRESHOLDS["shuffled_aux_corr_max"]),
        "no_anchor_with_aux_corr": (no_anchor_eval["pearson_corr"], no_anchor_eval["pearson_corr"] <= THRESHOLDS["no_anchor_with_aux_corr_max"]),
        "random_world_corr": (random_eval["pearson_corr"], random_eval["pearson_corr"] <= THRESHOLDS["random_world_corr_max"]),
    }

    recovery_pass = (
        mean_no_aux <= THRESHOLDS["no_aux_abs_corr_max"]
        and mean_with_aux >= THRESHOLDS["with_aux_corr_min"]
        and mean_improvement >= THRESHOLDS["improvement_min"]
    )
    controls_pass = all(ok for _, ok in controls.values())
    raw_verdict = "PASS" if (recovery_pass and controls_pass) else "FAIL"

    seed_report = SP.enforce_seed_policy(
        [{"metric": "recovery_pearson_corr", "role": "core", "seeds": SEED_COUNT, "pass_fail": raw_verdict}]
    )
    primary_verdict = seed_report["per_metric"]["recovery_pearson_corr"]["verdict"]

    return {
        "gate": "B1_harness_rerun",
        "decision": f"B1-{primary_verdict}-AUXILIARY-IDENTIFIABILITY",
        "seed_count": SEED_COUNT,
        "primary_metric_verdict": primary_verdict,
        "recovery": {
            "mean_no_aux_abs_corr": mean_no_aux,
            "mean_with_aux_corr": mean_with_aux,
            "mean_improvement": mean_improvement,
            "recovery_pass": recovery_pass,
        },
        "controls": {k: {"value": v, "passed": ok} for k, (v, ok) in controls.items()},
        "controls_pass": controls_pass,
        "seed_policy": seed_report,
        "thresholds": THRESHOLDS,
    }


def main():
    # 1) leakage scan (raises if any truth name reaches the fit path)
    leakage = LS.assert_no_fit_path_leakage(FIT_PATH_FUNCTIONS)

    # 2) tautology pre-check on the freshly generated world, before any learner
    nav = [r for r in T.generate_dataset(random_world=False, seed=T.SEED)["records"] if not r["is_anchor"]]
    tautology = TC.tautology_precheck(
        [r["y"] for r in nav], [r["z_obj"] for r in nav], THRESHOLDS
    )

    # 3) evaluation-oracle scan of this module's eval call sites
    oracle = EO.scan_evaluation_call_sites(sys.modules[__name__], EVALUATION_ENTRYPOINTS)

    # 4) run through the runner (verifies prereg lock, writes signed decision.json)
    decision = RUN.run_gate(
        HERE,
        experiment_fn,
        leakage_report=leakage,
        tautology_report=tautology,
        evaluation_oracle_log=oracle["evaluation_oracle_log"],
    )

    # 5) independent verification of the produced decision.json
    valid, reasons = VD.verify_decision(HERE / "decision.json")

    print(json.dumps(decision, indent=2, sort_keys=True))
    print("\nleakage_scan.passed        =", leakage["passed"])
    print("evaluation_oracle.passed   =", oracle["passed"], "(hints:", oracle["evaluation_oracle_log"], ")")
    print("verify_decision            =", "VALID" if valid else f"INVALID {reasons}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
