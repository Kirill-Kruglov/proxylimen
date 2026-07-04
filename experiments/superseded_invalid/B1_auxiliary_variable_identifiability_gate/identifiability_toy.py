from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any


SEED = 20260702
OBSERVERS = ("U0", "U1", "U2", "U3")
TRUE_BIASES = {"U0": 2.4, "U1": 0.8, "U2": -0.8, "U3": -2.4}
GROUP_CENTERS = {"U0": -2.4, "U1": -0.8, "U2": 0.8, "U3": 2.4}
ANCHOR_Z = (-3.0, -1.2, 0.0, 1.2, 3.0)


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)


def rank_normalize(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda idx: (values[idx], idx))
    ranks = [0.0] * len(values)
    if len(values) == 1:
        return [0.0]
    for rank, idx in enumerate(ordered):
        ranks[idx] = (rank / (len(values) - 1)) * 2.0 - 1.0
    return ranks


def _noise(rng: random.Random) -> float:
    return rng.uniform(-0.025, 0.025)


def generate_dataset(random_world: bool = False, seed: int = SEED) -> dict[str, Any]:
    rng = random.Random(seed + (1500 if random_world else 0))
    records: list[dict[str, Any]] = []

    for anchor_idx, z_obj in enumerate(ANCHOR_Z):
        item_id = f"anchor_{anchor_idx:02d}"
        for observer in OBSERVERS:
            if random_world:
                y_value = rng.uniform(-1.0, 1.0)
            else:
                y_value = z_obj + TRUE_BIASES[observer] + _noise(rng)
            records.append(
                {
                    "record_id": f"{item_id}_{observer}",
                    "item_id": item_id,
                    "u": observer,
                    "y": y_value,
                    "is_anchor": True,
                    "z_obj": z_obj,
                }
            )

    per_observer_count = 80
    for observer in OBSERVERS:
        center = GROUP_CENTERS[observer]
        for item_idx in range(per_observer_count):
            variation = rng.uniform(-0.7, 0.7)
            z_obj = center + variation
            item_id = f"item_{observer}_{item_idx:03d}"
            if random_world:
                y_value = rng.uniform(-1.0, 1.0)
            else:
                y_value = z_obj + TRUE_BIASES[observer] + _noise(rng)
            records.append(
                {
                    "record_id": f"{item_id}_{observer}",
                    "item_id": item_id,
                    "u": observer,
                    "y": y_value,
                    "is_anchor": False,
                    "z_obj": z_obj,
                }
            )

    manifest = {
        "seed": seed,
        "random_world": random_world,
        "record_count": len(records),
        "anchor_item_count": len(ANCHOR_Z),
        "anchor_record_count": len(ANCHOR_Z) * len(OBSERVERS),
        "heldout_non_anchor_record_count": per_observer_count * len(OBSERVERS),
        "observers": list(OBSERVERS),
        "true_biases_hidden_from_learners": TRUE_BIASES,
        "group_centers": GROUP_CENTERS,
        "formula": "y_i_u = z_obj_i + bias_u + noise",
        "learner_input_fields": ["record_id", "item_id", "u", "y", "is_anchor"],
        "truth_field_used_only_for_evaluation": "z_obj",
    }
    return {"records": records, "manifest": manifest}


def learner_view(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "record_id": record["record_id"],
            "item_id": record["item_id"],
            "u": record["u"],
            "y": record["y"],
            "is_anchor": record["is_anchor"],
        }
        for record in records
    ]


def no_auxiliary_learner(records: list[dict[str, Any]]) -> dict[str, float]:
    non_anchor = [record for record in learner_view(records) if not record["is_anchor"]]
    ranked = rank_normalize([record["y"] for record in non_anchor])
    return {record["record_id"]: estimate for record, estimate in zip(non_anchor, ranked)}


def estimate_biases_from_anchors(records: list[dict[str, Any]]) -> dict[str, float]:
    view = learner_view(records)
    anchors_by_item: dict[str, list[dict[str, Any]]] = {}
    for record in view:
        if record["is_anchor"]:
            anchors_by_item.setdefault(record["item_id"], []).append(record)

    diffs_by_u: dict[str, list[float]] = {observer: [] for observer in OBSERVERS}
    for anchor_records in anchors_by_item.values():
        observers_present = {record["u"] for record in anchor_records}
        if observers_present != set(OBSERVERS):
            continue
        item_mean = sum(record["y"] for record in anchor_records) / len(anchor_records)
        for record in anchor_records:
            diffs_by_u[record["u"]].append(record["y"] - item_mean)

    estimated: dict[str, float] = {}
    for observer in OBSERVERS:
        diffs = diffs_by_u[observer]
        estimated[observer] = sum(diffs) / len(diffs) if diffs else 0.0
    return estimated


def with_auxiliary_calibration_learner(records: list[dict[str, Any]]) -> dict[str, Any]:
    view = learner_view(records)
    estimated_biases = estimate_biases_from_anchors(records)
    predictions = {}
    for record in view:
        if not record["is_anchor"]:
            predictions[record["record_id"]] = record["y"] - estimated_biases.get(record["u"], 0.0)
    return {"predictions": predictions, "estimated_biases": estimated_biases}


def evaluate_predictions(records: list[dict[str, Any]], predictions: dict[str, float]) -> dict[str, Any]:
    truth: list[float] = []
    estimates: list[float] = []
    for record in records:
        if record["is_anchor"]:
            continue
        if record["record_id"] not in predictions:
            continue
        estimates.append(float(predictions[record["record_id"]]))
        truth.append(float(record["z_obj"]))
    corr = pearson(estimates, truth)
    return {
        "heldout_count": len(truth),
        "pearson_corr": corr,
        "abs_pearson_corr": abs(corr),
    }


def shuffled_auxiliary_records(records: list[dict[str, Any]], seed: int = SEED + 31) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    labels = [record["u"] for record in records]
    rng.shuffle(labels)
    shuffled = []
    for record, label in zip(records, labels):
        changed = dict(record)
        changed["u"] = label
        shuffled.append(changed)
    return shuffled


def without_anchor_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(record) for record in records if not record["is_anchor"]]


def audit_leakage(records: list[dict[str, Any]]) -> dict[str, Any]:
    item_ids_by_u: dict[str, set[str]] = {observer: set() for observer in OBSERVERS}
    z_values_by_u: dict[str, set[float]] = {observer: set() for observer in OBSERVERS}
    for record in records:
        item_ids_by_u[record["u"]].add(record["item_id"])
        z_values_by_u[record["u"]].add(round(float(record["z_obj"]), 12))

    unique_item_leakage = any(len(items) <= 1 for items in item_ids_by_u.values())
    exact_z_leakage = any(len(values) <= 1 for values in z_values_by_u.values())
    audit = {
        "u_uniquely_identifies_item_id": unique_item_leakage,
        "u_directly_encodes_exact_z_obj": exact_z_leakage,
        "learner_fit_reads_true_z_obj": False,
        "anchors_include_true_z_obj_labels_for_fit": False,
        "evaluation_truth_used_only_after_predictions": True,
        "human_authored_outcome_labels_used": False,
        "statistical_confounding_present_by_design": True,
        "leakage_detected": unique_item_leakage or exact_z_leakage,
    }
    return audit

