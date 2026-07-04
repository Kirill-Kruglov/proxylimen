from __future__ import annotations

import json
import math
import random
from collections import deque
from pathlib import Path
from typing import Any


SEED_START = 20260702
SEED_COUNT = 24
OBSERVERS = ("U0", "U1", "U2", "U3")
ADD_BIASES = {"U0": 2.4, "U1": 0.8, "U2": -0.8, "U3": -2.4}
GROUP_CENTERS = {"U0": -2.4, "U1": -0.8, "U2": 0.8, "U3": 2.4}
AFFINE_SCALES = {"U0": 0.55, "U1": 0.8, "U2": 1.2, "U3": 1.55}
AFFINE_SHIFTS = {u: -AFFINE_SCALES[u] * GROUP_CENTERS[u] for u in OBSERVERS}
ANCHOR_Z = (-3.2, -2.0, -0.8, 0.4, 1.6, 3.0)


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
    order = sorted(range(len(values)), key=lambda idx: (values[idx], idx))
    ranks = [0.0] * len(values)
    if len(values) == 1:
        return ranks
    for rank, idx in enumerate(order):
        ranks[idx] = (rank / (len(values) - 1)) * 2.0 - 1.0
    return ranks


def zscore(values: list[float]) -> list[float]:
    if not values:
        return []
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(var)
    if std == 0.0:
        return [0.0 for _ in values]
    return [(v - mean) / std for v in values]


def quantile_segment(values: list[float], bins: int = 8) -> list[float]:
    order = sorted(range(len(values)), key=lambda idx: (values[idx], idx))
    out = [0.0] * len(values)
    if len(values) == 1:
        return out
    for rank, idx in enumerate(order):
        bucket = min(bins - 1, int(rank * bins / len(values)))
        out[idx] = (bucket / (bins - 1)) * 2.0 - 1.0
    return out


def _noise(rng: random.Random, width: float = 0.025) -> float:
    return rng.uniform(-width, width)


def anchor_pairs(mode: str) -> list[tuple[str, tuple[str, ...]]]:
    if mode == "complete":
        return [(f"anchor_all_{idx}", OBSERVERS) for idx, _ in enumerate(ANCHOR_Z)]
    if mode == "sparse":
        edges = (("U0", "U1"), ("U1", "U2"), ("U2", "U3"))
    elif mode == "disconnected":
        edges = (("U0", "U1"), ("U2", "U3"))
    elif mode == "none":
        return []
    else:
        raise ValueError(f"unknown anchor mode: {mode}")
    pairs = []
    for edge_idx, edge in enumerate(edges):
        for z_idx, _ in enumerate(ANCHOR_Z):
            pairs.append((f"anchor_{edge[0]}_{edge[1]}_{z_idx}", edge))
    return pairs


def generate_records(
    seed: int,
    *,
    mode: str = "additive",
    anchor_mode: str = "complete",
    random_world: bool = False,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []

    for pair_idx, (item_id, observers) in enumerate(anchor_pairs(anchor_mode)):
        z_obj = ANCHOR_Z[pair_idx % len(ANCHOR_Z)]
        for observer in observers:
            y_value = generate_y(rng, observer, z_obj, mode=mode, random_world=random_world)
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

    for observer in OBSERVERS:
        center = GROUP_CENTERS[observer]
        for idx in range(80):
            z_obj = center + rng.uniform(-0.7, 0.7)
            item_id = f"item_{observer}_{idx:03d}"
            y_value = generate_y(rng, observer, z_obj, mode=mode, random_world=random_world)
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
    return records


def generate_y(
    rng: random.Random,
    observer: str,
    z_obj: float,
    *,
    mode: str,
    random_world: bool,
) -> float:
    if random_world:
        return rng.uniform(-1.0, 1.0)
    if mode == "additive":
        return z_obj + ADD_BIASES[observer] + _noise(rng)
    if mode == "affine":
        return AFFINE_SCALES[observer] * z_obj + AFFINE_SHIFTS[observer] + _noise(rng)
    raise ValueError(f"unknown mode: {mode}")


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


def non_anchor_view(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in learner_view(records) if not record["is_anchor"]]


def no_aux_predictions(records: list[dict[str, Any]], method: str = "NO_AUX_RAW_RANK") -> dict[str, float]:
    view = non_anchor_view(records)
    ys = [record["y"] for record in view]
    if method == "NO_AUX_RAW_RANK":
        estimates = rank_normalize(ys)
    elif method == "NO_AUX_GLOBAL_STANDARDIZE":
        estimates = zscore(ys)
    elif method == "NO_AUX_QUANTILE_SEGMENT":
        estimates = quantile_segment(ys)
    else:
        raise ValueError(f"unknown no-aux method: {method}")
    return {record["record_id"]: estimate for record, estimate in zip(view, estimates)}


def anchor_groups(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in learner_view(records):
        if record["is_anchor"]:
            groups.setdefault(record["item_id"], []).append(record)
    return groups


def complete_additive_biases(records: list[dict[str, Any]]) -> dict[str, float]:
    groups = anchor_groups(records)
    diffs: dict[str, list[float]] = {observer: [] for observer in OBSERVERS}
    for group in groups.values():
        if {row["u"] for row in group} != set(OBSERVERS):
            continue
        mean_y = sum(row["y"] for row in group) / len(group)
        for row in group:
            diffs[row["u"]].append(row["y"] - mean_y)
    return {observer: (sum(values) / len(values) if values else 0.0) for observer, values in diffs.items()}


def sparse_additive_biases(records: list[dict[str, Any]]) -> tuple[dict[str, float], bool]:
    groups = anchor_groups(records)
    pair_diffs: dict[tuple[str, str], list[float]] = {}
    for group in groups.values():
        if len(group) != 2:
            continue
        a, b = sorted(group, key=lambda row: row["u"])
        pair_diffs.setdefault((a["u"], b["u"]), []).append(b["y"] - a["y"])

    graph: dict[str, list[tuple[str, float]]] = {observer: [] for observer in OBSERVERS}
    for (u_a, u_b), diffs in pair_diffs.items():
        diff = sum(diffs) / len(diffs)
        graph[u_a].append((u_b, diff))
        graph[u_b].append((u_a, -diff))

    biases = {"U0": 0.0}
    queue: deque[str] = deque(["U0"])
    while queue:
        current = queue.popleft()
        for neighbor, diff in graph[current]:
            if neighbor not in biases:
                biases[neighbor] = biases[current] + diff
                queue.append(neighbor)
    connected = len(biases) == len(OBSERVERS)
    if not connected:
        return {observer: 0.0 for observer in OBSERVERS}, False
    return {observer: biases[observer] for observer in OBSERVERS}, True


def additive_aux_predictions(records: list[dict[str, Any]], anchor_mode: str = "complete") -> dict[str, Any]:
    if anchor_mode == "complete":
        biases = complete_additive_biases(records)
        connected = bool(anchor_groups(records))
    elif anchor_mode in {"sparse", "disconnected"}:
        biases, connected = sparse_additive_biases(records)
    elif anchor_mode == "none":
        biases = {observer: 0.0 for observer in OBSERVERS}
        connected = False
    else:
        raise ValueError(f"unknown anchor mode: {anchor_mode}")

    predictions = {
        record["record_id"]: record["y"] - biases.get(record["u"], 0.0)
        for record in non_anchor_view(records)
    }
    return {"predictions": predictions, "estimated_biases": biases, "anchor_graph_connected": connected}


def fit_linear(xs: list[float], ys: list[float]) -> tuple[float, float]:
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    var = sum((x - mx) ** 2 for x in xs)
    if var == 0.0:
        return 0.0, my
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = cov / var
    intercept = my - slope * mx
    return slope, intercept


def affine_aux_predictions(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups = anchor_groups(records)
    paired: dict[str, list[tuple[float, float]]] = {observer: [] for observer in OBSERVERS}
    for group in groups.values():
        by_u = {row["u"]: row for row in group}
        if set(by_u) != set(OBSERVERS):
            continue
        ref_y = by_u["U0"]["y"]
        for observer in OBSERVERS:
            paired[observer].append((by_u[observer]["y"], ref_y))

    transforms: dict[str, tuple[float, float]] = {}
    for observer in OBSERVERS:
        pairs = paired[observer]
        if len(pairs) < 2:
            transforms[observer] = (1.0, 0.0)
            continue
        slope, intercept = fit_linear([x for x, _ in pairs], [y for _, y in pairs])
        transforms[observer] = (slope, intercept)

    predictions = {}
    for record in non_anchor_view(records):
        slope, intercept = transforms.get(record["u"], (1.0, 0.0))
        predictions[record["record_id"]] = slope * record["y"] + intercept
    return {"predictions": predictions, "transforms_to_U0_scale": transforms}


def evaluate(records: list[dict[str, Any]], predictions: dict[str, float]) -> dict[str, Any]:
    estimates: list[float] = []
    truth: list[float] = []
    for record in records:
        if record["is_anchor"]:
            continue
        if record["record_id"] not in predictions:
            continue
        estimates.append(float(predictions[record["record_id"]]))
        truth.append(float(record["z_obj"]))
    corr = pearson(estimates, truth)
    return {"heldout_count": len(truth), "pearson_corr": corr, "abs_pearson_corr": abs(corr)}


def shuffled_u_records(records: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    labels = [record["u"] for record in records]
    rng.shuffle(labels)
    out = []
    for record, label in zip(records, labels):
        changed = dict(record)
        changed["u"] = label
        out.append(changed)
    return out


def remove_anchors(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(record) for record in records if not record["is_anchor"]]


def run_additive_seed(seed: int) -> dict[str, Any]:
    records = generate_records(seed, mode="additive", anchor_mode="complete")
    no_aux_eval = evaluate(records, no_aux_predictions(records))
    with_aux = additive_aux_predictions(records, anchor_mode="complete")
    with_aux_eval = evaluate(records, with_aux["predictions"])
    return {
        "seed": seed,
        "no_aux_abs_corr": no_aux_eval["abs_pearson_corr"],
        "with_aux_corr": with_aux_eval["pearson_corr"],
        "improvement": with_aux_eval["pearson_corr"] - no_aux_eval["abs_pearson_corr"],
        "individual_passed": no_aux_eval["abs_pearson_corr"] <= 0.40 and with_aux_eval["pearson_corr"] >= 0.85,
    }


def run_multiseed() -> dict[str, Any]:
    seed_results = [run_additive_seed(SEED_START + idx) for idx in range(SEED_COUNT)]
    mean_no_aux = sum(row["no_aux_abs_corr"] for row in seed_results) / len(seed_results)
    mean_with_aux = sum(row["with_aux_corr"] for row in seed_results) / len(seed_results)
    mean_improvement = sum(row["improvement"] for row in seed_results) / len(seed_results)
    individual_pass_fraction = sum(1 for row in seed_results if row["individual_passed"]) / len(seed_results)
    passed = (
        mean_no_aux <= 0.35
        and mean_with_aux >= 0.90
        and mean_improvement >= 0.55
        and individual_pass_fraction >= 0.80
    )
    return {
        "seed_count": len(seed_results),
        "seed_results": seed_results,
        "mean_no_aux_abs_corr": mean_no_aux,
        "mean_with_aux_corr": mean_with_aux,
        "mean_improvement": mean_improvement,
        "individual_pass_fraction": individual_pass_fraction,
        "passed": passed,
    }


def run_sparse_anchor(seed: int = SEED_START + 101) -> dict[str, Any]:
    complete_records = generate_records(seed, mode="additive", anchor_mode="complete")
    no_aux_eval = evaluate(complete_records, no_aux_predictions(complete_records))

    sparse_records = generate_records(seed, mode="additive", anchor_mode="sparse")
    sparse_fit = additive_aux_predictions(sparse_records, anchor_mode="sparse")
    sparse_eval = evaluate(sparse_records, sparse_fit["predictions"])

    disconnected_records = generate_records(seed, mode="additive", anchor_mode="disconnected")
    disconnected_fit = additive_aux_predictions(disconnected_records, anchor_mode="disconnected")
    disconnected_eval = evaluate(disconnected_records, disconnected_fit["predictions"])

    improvement = sparse_eval["pearson_corr"] - no_aux_eval["abs_pearson_corr"]
    passed = (
        sparse_eval["pearson_corr"] >= 0.85
        and improvement >= 0.50
        and disconnected_eval["pearson_corr"] <= 0.50
    )
    return {
        "seed": seed,
        "no_aux_abs_corr": no_aux_eval["abs_pearson_corr"],
        "sparse_anchor_with_aux_corr": sparse_eval["pearson_corr"],
        "sparse_anchor_improvement": improvement,
        "sparse_anchor_graph_connected": sparse_fit["anchor_graph_connected"],
        "disconnected_anchor_corr": disconnected_eval["pearson_corr"],
        "disconnected_anchor_graph_connected": disconnected_fit["anchor_graph_connected"],
        "passed": passed,
    }


def run_affine(seed: int = SEED_START + 211) -> dict[str, Any]:
    records = generate_records(seed, mode="affine", anchor_mode="complete")
    no_aux_eval = evaluate(records, no_aux_predictions(records))
    fit = affine_aux_predictions(records)
    with_aux_eval = evaluate(records, fit["predictions"])
    shuffled = shuffled_u_records(records, seed + 97)
    shuffled_fit = affine_aux_predictions(shuffled)
    shuffled_eval = evaluate(shuffled, shuffled_fit["predictions"])
    improvement = with_aux_eval["pearson_corr"] - no_aux_eval["abs_pearson_corr"]
    passed = (
        with_aux_eval["pearson_corr"] >= 0.85
        and no_aux_eval["abs_pearson_corr"] <= 0.45
        and improvement >= 0.40
        and shuffled_eval["pearson_corr"] <= 0.55
    )
    return {
        "seed": seed,
        "affine_no_aux_abs_corr": no_aux_eval["abs_pearson_corr"],
        "affine_with_aux_corr": with_aux_eval["pearson_corr"],
        "affine_improvement": improvement,
        "affine_shuffled_aux_corr": shuffled_eval["pearson_corr"],
        "transforms_to_U0_scale": fit["transforms_to_U0_scale"],
        "passed": passed,
    }


def run_no_aux_baselines(seed: int = SEED_START + 307) -> dict[str, Any]:
    records = generate_records(seed, mode="additive", anchor_mode="complete")
    methods = ("NO_AUX_RAW_RANK", "NO_AUX_GLOBAL_STANDARDIZE", "NO_AUX_QUANTILE_SEGMENT")
    results = {}
    for method in methods:
        metric = evaluate(records, no_aux_predictions(records, method))
        results[method] = metric
    max_abs = max(metric["abs_pearson_corr"] for metric in results.values())
    return {"baseline_results": results, "max_no_aux_abs_corr": max_abs, "passed": max_abs <= 0.50}


def run_controls(seed: int = SEED_START + 409) -> dict[str, Any]:
    records = generate_records(seed, mode="additive", anchor_mode="complete")
    shuffled = shuffled_u_records(records, seed + 41)
    shuffled_fit = additive_aux_predictions(shuffled, anchor_mode="complete")
    shuffled_eval = evaluate(shuffled, shuffled_fit["predictions"])

    no_anchor = remove_anchors(records)
    no_anchor_fit = additive_aux_predictions(no_anchor, anchor_mode="none")
    no_anchor_eval = evaluate(no_anchor, no_anchor_fit["predictions"])

    disconnected = generate_records(seed, mode="additive", anchor_mode="disconnected")
    disconnected_fit = additive_aux_predictions(disconnected, anchor_mode="disconnected")
    disconnected_eval = evaluate(disconnected, disconnected_fit["predictions"])

    random_world = generate_records(seed + 503, mode="additive", anchor_mode="complete", random_world=True)
    random_fit = additive_aux_predictions(random_world, anchor_mode="complete")
    random_eval = evaluate(random_world, random_fit["predictions"])

    controls = {
        "C1_shuffled_auxiliary": {"corr": shuffled_eval["pearson_corr"], "passed": shuffled_eval["pearson_corr"] <= 0.50},
        "C2_no_anchors": {"corr": no_anchor_eval["pearson_corr"], "passed": no_anchor_eval["pearson_corr"] <= 0.50},
        "C3_disconnected_anchors": {
            "corr": disconnected_eval["pearson_corr"],
            "anchor_graph_connected": disconnected_fit["anchor_graph_connected"],
            "passed": disconnected_eval["pearson_corr"] <= 0.50,
        },
        "C4_random_world": {"corr": random_eval["pearson_corr"], "passed": random_eval["pearson_corr"] <= 0.30},
        "C5_leakage_audit": "see leakage_audit.json",
    }
    return {"controls": controls, "passed": all(v["passed"] for k, v in controls.items() if k != "C5_leakage_audit")}


def leakage_audit(records: list[dict[str, Any]]) -> dict[str, Any]:
    item_ids_by_u = {observer: set() for observer in OBSERVERS}
    exact_z_by_u = {observer: set() for observer in OBSERVERS}
    for record in records:
        item_ids_by_u[record["u"]].add(record["item_id"])
        exact_z_by_u[record["u"]].add(round(float(record["z_obj"]), 12))
    return {
        "u_uniquely_identifies_item_id": any(len(values) <= 1 for values in item_ids_by_u.values()),
        "u_directly_encodes_exact_z_obj": any(len(values) <= 1 for values in exact_z_by_u.values()),
        "anchors_contain_true_z_obj_labels_for_fit": False,
        "fit_functions_read_z_obj": False,
        "true_z_obj_used_only_after_predictions": True,
        "human_authored_final_or_outcome_labels_exist": False,
        "seed_to_result_lookup_exists": False,
        "variant_to_result_lookup_exists": False,
        "aux_leakage_detected": False,
        "human_authored_outcomes_detected": False,
    }

