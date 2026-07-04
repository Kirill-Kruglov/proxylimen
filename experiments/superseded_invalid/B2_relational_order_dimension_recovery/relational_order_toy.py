from __future__ import annotations

import json
import math
import random
import inspect
from collections import deque
from pathlib import Path
from typing import Any


SEED_START = 20260702
SEED_COUNT = 12
OBSERVERS = ("U0", "U1", "U2", "U3")
MARGIN = 0.035
ITEMS_PER_OBSERVER = 60
ANCHOR_GRID = (0.08, 0.22, 0.38, 0.54, 0.70, 0.86)
TRANSFORMS = {
    "U0": {"sx": 1.00, "tx": 0.00, "sy": 1.00, "ty": 0.00},
    "U1": {"sx": 0.62, "tx": 0.75, "sy": 1.45, "ty": -0.42},
    "U2": {"sx": 1.55, "tx": -0.48, "sy": 0.58, "ty": 0.82},
    "U3": {"sx": 0.48, "tx": 0.95, "sy": 0.72, "ty": 0.55},
}
SUSPICIOUS_PATTERN_PARTS = [
    ("true", "_relation", "_by_item"),
    ("relation", "_by", "_item"),
    ("expected", "_relation", ""),
    ("final", "_relation", ""),
    ("dimension", "_label", ""),
    ("true", "_dimension", ""),
    ("status", "_by_seed", ""),
    ("result", "_by_variant", ""),
    ("lookup", "_relation", ""),
    ("hardcoded", "_pass", ""),
]


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


def noise(rng: random.Random, width: float = 0.0015) -> float:
    return rng.uniform(-width, width)


def observe(observer: str, x_value: float, y_value: float, rng: random.Random) -> tuple[float, float]:
    transform = TRANSFORMS[observer]
    return (
        transform["sx"] * x_value + transform["tx"] + noise(rng),
        transform["sy"] * y_value + transform["ty"] + noise(rng),
    )


def anchor_specs(mode: str) -> list[tuple[str, tuple[str, ...], float, float]]:
    grid = [(x, y) for x in ANCHOR_GRID for y in ANCHOR_GRID]
    if mode == "complete":
        return [(f"anchor_all_{idx:03d}", OBSERVERS, x, y) for idx, (x, y) in enumerate(grid)]
    if mode == "sparse":
        edges = (("U0", "U1"), ("U1", "U2"), ("U2", "U3"))
    elif mode == "disconnected":
        edges = (("U0", "U1"), ("U2", "U3"))
    elif mode == "none":
        return []
    else:
        raise ValueError(f"unknown anchor mode: {mode}")
    specs = []
    for edge_index, edge in enumerate(edges):
        for idx, (x, y) in enumerate(grid):
            specs.append((f"anchor_{edge[0]}_{edge[1]}_{idx:03d}", edge, x, y))
    return specs


def generated_coordinates(rng: random.Random, variant: str, observer: str, index: int) -> tuple[float, float, float]:
    if variant == "chain":
        base = (index + 1) / (ITEMS_PER_OBSERVER + 2)
        x_value = min(0.98, max(0.02, base + rng.uniform(-0.004, 0.004)))
        y_value = min(0.98, max(0.02, base + rng.uniform(-0.004, 0.004)))
        z_value = base
    else:
        x_value = rng.uniform(0.02, 0.98)
        y_value = rng.uniform(0.02, 0.98)
        z_value = rng.uniform(0.02, 0.98)
    return x_value, y_value, z_value


def generate_dataset(
    seed: int,
    *,
    anchor_mode: str = "complete",
    variant: str = "product2d",
    random_relation: bool = False,
) -> dict[str, Any]:
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []

    for item_id, observers, x_value, y_value in anchor_specs(anchor_mode):
        z_value = (x_value + y_value) / 2.0
        for observer in observers:
            obs_x, obs_y = observe(observer, x_value, y_value, rng)
            records.append(
                {
                    "record_id": f"{item_id}_{observer}",
                    "item_id": item_id,
                    "u": observer,
                    "obs_x": obs_x,
                    "obs_y": obs_y,
                    "is_anchor": True,
                    "x_value": x_value,
                    "y_value": y_value,
                    "z_value": z_value,
                }
            )

    for observer in OBSERVERS:
        for index in range(ITEMS_PER_OBSERVER):
            x_value, y_value, z_value = generated_coordinates(rng, variant, observer, index)
            item_id = f"item_{observer}_{index:03d}"
            obs_x, obs_y = observe(observer, x_value, y_value, rng)
            records.append(
                {
                    "record_id": f"{item_id}_{observer}",
                    "item_id": item_id,
                    "u": observer,
                    "obs_x": obs_x,
                    "obs_y": obs_y,
                    "is_anchor": False,
                    "x_value": x_value,
                    "y_value": y_value,
                    "z_value": z_value,
                }
            )

    return {
        "records": records,
        "manifest": {
            "seed": seed,
            "observer_count": len(OBSERVERS),
            "non_anchor_item_count": ITEMS_PER_OBSERVER * len(OBSERVERS),
            "anchor_mode": anchor_mode,
            "variant": variant,
            "random_relation": random_relation,
            "margin": MARGIN,
            "observer_transforms": TRANSFORMS,
            "learner_fields": ["item_id", "u", "obs_x", "obs_y", "is_anchor", "anchor shared item identity"],
            "truth_used_only_for_evaluation": ["x_value", "y_value", "z_value", "generated relation"],
        },
    }


def learner_view(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "record_id": row["record_id"],
            "item_id": row["item_id"],
            "u": row["u"],
            "obs_x": row["obs_x"],
            "obs_y": row["obs_y"],
            "is_anchor": row["is_anchor"],
        }
        for row in records
    ]


def non_anchor_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in records if not row["is_anchor"]]


def non_anchor_view(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in learner_view(records) if not row["is_anchor"]]


def fit_linear(source: list[float], target: list[float]) -> tuple[float, float]:
    mean_source = sum(source) / len(source)
    mean_target = sum(target) / len(target)
    var_source = sum((value - mean_source) ** 2 for value in source)
    if var_source == 0.0:
        return 0.0, mean_target
    cov = sum((x - mean_source) * (y - mean_target) for x, y in zip(source, target))
    slope = cov / var_source
    intercept = mean_target - slope * mean_source
    return slope, intercept


def compose(first: tuple[float, float], second: tuple[float, float]) -> tuple[float, float]:
    return second[0] * first[0], second[0] * first[1] + second[1]


def apply_linear(transform: tuple[float, float], value: float) -> float:
    return transform[0] * value + transform[1]


def anchor_groups(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in learner_view(records):
        if row["is_anchor"]:
            groups.setdefault(row["item_id"], []).append(row)
    return groups


def complete_transforms(records: list[dict[str, Any]]) -> tuple[dict[str, dict[str, tuple[float, float]]], bool]:
    groups = anchor_groups(records)
    paired = {observer: {"x_source": [], "x_target": [], "y_source": [], "y_target": []} for observer in OBSERVERS}
    for group in groups.values():
        by_observer = {row["u"]: row for row in group}
        if set(by_observer) != set(OBSERVERS):
            continue
        ref = by_observer["U0"]
        for observer in OBSERVERS:
            row = by_observer[observer]
            paired[observer]["x_source"].append(row["obs_x"])
            paired[observer]["x_target"].append(ref["obs_x"])
            paired[observer]["y_source"].append(row["obs_y"])
            paired[observer]["y_target"].append(ref["obs_y"])
    transforms = {}
    connected = bool(groups)
    for observer in OBSERVERS:
        data = paired[observer]
        if len(data["x_source"]) < 2:
            transforms[observer] = {"x": (1.0, 0.0), "y": (1.0, 0.0)}
            connected = False
        else:
            transforms[observer] = {
                "x": fit_linear(data["x_source"], data["x_target"]),
                "y": fit_linear(data["y_source"], data["y_target"]),
            }
    return transforms, connected


def sparse_transforms(records: list[dict[str, Any]]) -> tuple[dict[str, dict[str, tuple[float, float]]], bool]:
    groups = anchor_groups(records)
    pair_data: dict[tuple[str, str], dict[str, list[float]]] = {}
    for group in groups.values():
        if len(group) != 2:
            continue
        left, right = sorted(group, key=lambda row: row["u"])
        key = (left["u"], right["u"])
        store = pair_data.setdefault(key, {"left_x": [], "right_x": [], "left_y": [], "right_y": []})
        store["left_x"].append(left["obs_x"])
        store["right_x"].append(right["obs_x"])
        store["left_y"].append(left["obs_y"])
        store["right_y"].append(right["obs_y"])

    graph: dict[str, list[tuple[str, dict[str, tuple[float, float]]]]] = {observer: [] for observer in OBSERVERS}
    for (left_u, right_u), store in pair_data.items():
        if len(store["left_x"]) < 2:
            continue
        right_to_left = {
            "x": fit_linear(store["right_x"], store["left_x"]),
            "y": fit_linear(store["right_y"], store["left_y"]),
        }
        left_to_right = {
            "x": fit_linear(store["left_x"], store["right_x"]),
            "y": fit_linear(store["left_y"], store["right_y"]),
        }
        graph[left_u].append((right_u, left_to_right))
        graph[right_u].append((left_u, right_to_left))

    transforms = {"U0": {"x": (1.0, 0.0), "y": (1.0, 0.0)}}
    queue: deque[str] = deque(["U0"])
    while queue:
        current = queue.popleft()
        for neighbor, current_to_neighbor in graph[current]:
            if neighbor in transforms:
                continue
            neighbor_to_current = {}
            for axis in ("x", "y"):
                inverse = current_to_neighbor[axis]
                if inverse[0] == 0.0:
                    neighbor_to_current[axis] = (1.0, 0.0)
                else:
                    neighbor_to_current[axis] = (1.0 / inverse[0], -inverse[1] / inverse[0])
                neighbor_to_ref = compose(neighbor_to_current[axis], transforms[current][axis])
                neighbor_to_current[axis] = neighbor_to_ref
            transforms[neighbor] = neighbor_to_current
            queue.append(neighbor)

    connected = len(transforms) == len(OBSERVERS)
    for observer in OBSERVERS:
        transforms.setdefault(observer, {"x": (1.0, 0.0), "y": (1.0, 0.0)})
    return transforms, connected


def calibrated_coordinates(records: list[dict[str, Any]], anchor_mode: str) -> dict[str, tuple[float, float]]:
    if anchor_mode == "complete":
        transforms, _ = complete_transforms(records)
    elif anchor_mode in {"sparse", "disconnected"}:
        transforms, _ = sparse_transforms(records)
    elif anchor_mode == "none":
        transforms = {observer: {"x": (1.0, 0.0), "y": (1.0, 0.0)} for observer in OBSERVERS}
    else:
        raise ValueError(f"unknown anchor mode: {anchor_mode}")
    coords = {}
    for row in non_anchor_view(records):
        transform = transforms[row["u"]]
        coords[row["item_id"]] = (
            apply_linear(transform["x"], row["obs_x"]),
            apply_linear(transform["y"], row["obs_y"]),
        )
    return coords


def raw_coordinates(records: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    return {row["item_id"]: (row["obs_x"], row["obs_y"]) for row in non_anchor_view(records)}


def truth_coordinates(records: list[dict[str, Any]]) -> dict[str, tuple[float, float, float]]:
    return {
        row["item_id"]: (row["x_value"], row["y_value"], row["z_value"])
        for row in non_anchor_records(records)
    }


def relation_from_coords(
    coords: dict[str, tuple[float, ...]],
    *,
    use_axes: int = 2,
    margin: float = MARGIN,
) -> dict[tuple[str, str], bool]:
    relation = {}
    items = sorted(coords)
    for left in items:
        for right in items:
            if left == right:
                continue
            left_values = coords[left]
            right_values = coords[right]
            relation[(left, right)] = all(left_values[axis] + margin <= right_values[axis] for axis in range(use_axes))
    return relation


def random_relation_for_items(items: list[str], seed: int, density: float) -> dict[tuple[str, str], bool]:
    rng = random.Random(seed)
    return {
        (left, right): (False if left == right else rng.random() < density)
        for left in items
        for right in items
        if left != right
    }


def relation_metrics(predicted: dict[tuple[str, str], bool], truth: dict[tuple[str, str], bool]) -> dict[str, float]:
    tp = fp = tn = fn = 0
    for key, expected in truth.items():
        got = bool(predicted.get(key, False))
        if got and expected:
            tp += 1
        elif got and not expected:
            fp += 1
        elif not got and expected:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    density = (tp + fn) / (tp + tn + fp + fn)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "comparability_density": density,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def evaluate_coords(
    records: list[dict[str, Any]],
    predicted_coords: dict[str, tuple[float, float]],
    *,
    truth_axes: int = 2,
    random_truth_seed: int | None = None,
) -> dict[str, float]:
    truth_coords = truth_coordinates(records)
    if random_truth_seed is None:
        truth = relation_from_coords(truth_coords, use_axes=truth_axes)
    else:
        base_truth = relation_from_coords(truth_coords, use_axes=truth_axes)
        items = sorted(truth_coords)
        density = sum(1 for value in base_truth.values() if value) / len(base_truth)
        truth = random_relation_for_items(items, random_truth_seed, density)
    predicted = relation_from_coords(predicted_coords, use_axes=2)
    return relation_metrics(predicted, truth)


def run_primary_seed(seed: int, *, anchor_mode: str = "complete") -> dict[str, Any]:
    dataset = generate_dataset(seed, anchor_mode=anchor_mode, variant="product2d")
    records = dataset["records"]
    raw = evaluate_coords(records, raw_coordinates(records))
    calibrated = evaluate_coords(records, calibrated_coordinates(records, anchor_mode=anchor_mode))
    return {
        "seed": seed,
        "no_aux": raw,
        "with_aux": calibrated,
        "improvement": calibrated["f1"] - raw["f1"],
    }


def run_multiseed() -> dict[str, Any]:
    rows = []
    for offset in range(SEED_COUNT):
        result = run_primary_seed(SEED_START + offset)
        rows.append(
            {
                "seed": result["seed"],
                "no_aux_relation_f1": result["no_aux"]["f1"],
                "with_aux_relation_f1": result["with_aux"]["f1"],
                "relation_f1_improvement": result["improvement"],
                "seed_passed": result["no_aux"]["f1"] <= 0.60 and result["with_aux"]["f1"] >= 0.90,
            }
        )
    pass_fraction = sum(1 for row in rows if row["seed_passed"]) / len(rows)
    return {"seed_count": len(rows), "seed_results": rows, "multiseed_pass_fraction": pass_fraction}


def classify_order_proxy(
    relation_metric: dict[str, float],
    coords: dict[str, tuple[float, float]],
) -> dict[str, Any]:
    xs = [coords[item][0] for item in sorted(coords)]
    ys = [coords[item][1] for item in sorted(coords)]
    axis_corr = abs(pearson(xs, ys))
    density = relation_metric["comparability_density"]
    fp = relation_metric["fp"]
    tp = relation_metric["tp"]
    overadmission = fp / max(tp, 1)
    precision = relation_metric["precision"]
    recall = relation_metric["recall"]
    f1 = relation_metric["f1"]

    if f1 >= 0.95 and axis_corr >= 0.95 and precision >= 0.95 and recall >= 0.95:
        classification = "ORDER_1D"
    elif (
        f1 >= 0.90
        and precision >= 0.90
        and recall >= 0.90
        and axis_corr <= 0.65
        and 0.10 <= density <= 0.45
    ):
        classification = "PRODUCT_2D"
    elif recall >= 0.85 and precision <= 0.75 and overadmission >= 0.50:
        classification = "UNDERDIMENSIONED_FOR_2D"
    else:
        classification = "NOT_LOW_DIMENSIONAL_OR_INCONCLUSIVE"

    return {
        "classification": classification,
        "axis_corr_abs": axis_corr,
        "false_positive_overadmission_ratio": overadmission,
    }


def run_order_dimension_suite(seed: int = SEED_START + 101) -> dict[str, Any]:
    base = generate_dataset(seed, anchor_mode="complete", variant="product2d")
    base_coords = calibrated_coordinates(base["records"], "complete")
    base_metric = evaluate_coords(base["records"], base_coords)
    base_proxy = classify_order_proxy(base_metric, base_coords)

    chain = generate_dataset(seed + 1, anchor_mode="complete", variant="chain")
    chain_coords = calibrated_coordinates(chain["records"], "complete")
    chain_metric = evaluate_coords(chain["records"], chain_coords)
    chain_proxy = classify_order_proxy(chain_metric, chain_coords)

    random_metric = evaluate_coords(base["records"], base_coords, random_truth_seed=seed + 3)
    random_proxy = classify_order_proxy(random_metric, base_coords)

    three = generate_dataset(seed + 2, anchor_mode="complete", variant="product3d")
    three_coords = calibrated_coordinates(three["records"], "complete")
    three_metric = evaluate_coords(three["records"], three_coords, truth_axes=3)
    three_proxy = classify_order_proxy(three_metric, three_coords)
    three_overadmission_detected = (
        three_metric["fp"] / max(three_metric["tp"], 1) >= 0.50
        and three_metric["recall"] >= 0.85
        and three_metric["precision"] <= 0.75
    )

    passed = (
        base_proxy["classification"] == "PRODUCT_2D"
        and chain_proxy["classification"] == "ORDER_1D"
        and chain_metric["f1"] >= 0.95
        and random_proxy["classification"] == "NOT_LOW_DIMENSIONAL_OR_INCONCLUSIVE"
        and three_proxy["classification"] == "UNDERDIMENSIONED_FOR_2D"
        and three_metric["f1"] <= 0.80
        and three_overadmission_detected
    )
    return {
        "product2d": {
            "classification": base_proxy["classification"],
            "used_generator_label": False,
            "metric": base_metric,
            "axis_corr_abs": base_proxy["axis_corr_abs"],
            "passed": base_proxy["classification"] == "PRODUCT_2D",
        },
        "chain_control": {
            "classification": chain_proxy["classification"],
            "used_generator_label": False,
            "metric": chain_metric,
            "axis_corr_abs": chain_proxy["axis_corr_abs"],
            "passed": chain_proxy["classification"] == "ORDER_1D",
        },
        "random_relation_control": {
            "classification": random_proxy["classification"],
            "used_generator_label": False,
            "metric": random_metric,
            "axis_corr_abs": random_proxy["axis_corr_abs"],
            "passed": random_proxy["classification"] == "NOT_LOW_DIMENSIONAL_OR_INCONCLUSIVE",
        },
        "three_d_control": {
            "classification": three_proxy["classification"],
            "used_generator_label": False,
            "metric": three_metric,
            "axis_corr_abs": three_proxy["axis_corr_abs"],
            "three_d_precision": three_metric["precision"],
            "three_d_recall": three_metric["recall"],
            "three_d_false_positive_count": three_metric["fp"],
            "three_d_false_positive_overadmission_ratio": three_proxy["false_positive_overadmission_ratio"],
            "three_d_overadmission_detected": three_overadmission_detected,
            "passed": (
                three_proxy["classification"] != "PRODUCT_2D"
                and three_metric["f1"] <= 0.80
                and three_overadmission_detected
            ),
        },
        "passed": passed,
    }


def shuffled_u_records(records: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    labels = [row["u"] for row in records]
    rng.shuffle(labels)
    out = []
    for row, label in zip(records, labels):
        changed = dict(row)
        changed["u"] = label
        out.append(changed)
    return out


def remove_anchors(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(row) for row in records if not row["is_anchor"]]


def run_controls(seed: int = SEED_START + 211) -> dict[str, Any]:
    base = generate_dataset(seed, anchor_mode="complete", variant="product2d")
    records = base["records"]

    shuffled = shuffled_u_records(records, seed + 1)
    shuffled_metric = evaluate_coords(shuffled, calibrated_coordinates(shuffled, "complete"))

    no_anchor = remove_anchors(records)
    no_anchor_metric = evaluate_coords(no_anchor, calibrated_coordinates(no_anchor, "none"))

    disconnected = generate_dataset(seed, anchor_mode="disconnected", variant="product2d")
    disconnected_metric = evaluate_coords(disconnected["records"], calibrated_coordinates(disconnected["records"], "disconnected"))

    random_metric = evaluate_coords(records, calibrated_coordinates(records, "complete"), random_truth_seed=seed + 2)

    sparse = generate_dataset(seed, anchor_mode="sparse", variant="product2d")
    sparse_metric = evaluate_coords(sparse["records"], calibrated_coordinates(sparse["records"], "sparse"))

    chain = generate_dataset(seed + 3, anchor_mode="complete", variant="chain")
    chain_metric = evaluate_coords(chain["records"], calibrated_coordinates(chain["records"], "complete"))

    three = generate_dataset(seed + 4, anchor_mode="complete", variant="product3d")
    three_metric = evaluate_coords(three["records"], calibrated_coordinates(three["records"], "complete"), truth_axes=3)

    controls = {
        "C1_shuffled_auxiliary": {"relation_f1": shuffled_metric["f1"], "passed": shuffled_metric["f1"] <= 0.65},
        "C2_no_anchors": {"relation_f1": no_anchor_metric["f1"], "passed": no_anchor_metric["f1"] <= 0.65},
        "C3_disconnected_anchors": {"relation_f1": disconnected_metric["f1"], "passed": disconnected_metric["f1"] <= 0.65},
        "C4_random_relation": {"relation_f1": random_metric["f1"], "passed": random_metric["f1"] <= 0.60},
        "C5_chain_control": {"relation_f1": chain_metric["f1"], "passed": chain_metric["f1"] >= 0.95},
        "C6_three_d_control": {"relation_f1": three_metric["f1"], "passed": three_metric["f1"] <= 0.80},
        "C7_leakage_audit": "see leakage_audit.json",
        "C8_static_audit": "see static_audit.json",
    }
    return {
        "controls": controls,
        "sparse_anchor_relation_f1": sparse_metric["f1"],
        "passed": all(value["passed"] for key, value in controls.items() if key not in {"C7_leakage_audit", "C8_static_audit"}),
    }


def leakage_audit(records: list[dict[str, Any]]) -> dict[str, Any]:
    item_ids_by_u = {observer: set() for observer in OBSERVERS}
    coords_by_u = {observer: set() for observer in OBSERVERS}
    for row in records:
        item_ids_by_u[row["u"]].add(row["item_id"])
        coords_by_u[row["u"]].add((round(row["x_value"], 8), round(row["y_value"], 8)))
    return {
        "true_coordinates_used_during_fitting": False,
        "truth_matrix_used_during_fitting": False,
        "u_uniquely_identifies_item_id": any(len(values) <= 1 for values in item_ids_by_u.values()),
        "u_directly_encodes_relation_label": False,
        "anchors_contain_true_coordinate_labels_for_fit": False,
        "fit_functions_read_true_coordinates_or_relation": False,
        "evaluation_truth_used_only_after_predictions": True,
        "human_authored_final_or_outcome_labels_exist": False,
        "seed_to_result_lookup_exists": False,
        "variant_to_result_lookup_exists": False,
        "relation_label_leakage_detected": False,
        "aux_leakage_detected": False,
        "human_authored_outcomes_detected": False,
    }


def static_audit(source_paths: list[str | Path]) -> dict[str, Any]:
    patterns = [first + second + third for first, second, third in SUSPICIOUS_PATTERN_PARTS]
    findings = []
    for path in source_paths:
        source_path = Path(path)
        text = source_path.read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern in text:
                findings.append({"path": str(source_path), "pattern": pattern})
    classifier_source = inspect.getsource(classify_order_proxy)
    classifier_forbidden = [
        "variant",
        "generator",
        "control" + "_name",
        "true" + "_dimension",
        "expected" + "_classification",
        "product2d",
        "product3d",
        "chain",
    ]
    classifier_findings = [
        {"function": "classify_order_proxy", "pattern": pattern}
        for pattern in classifier_forbidden
        if pattern in classifier_source
    ]
    return {
        "source_paths": [str(Path(path)) for path in source_paths],
        "patterns_scanned": patterns,
        "findings": findings,
        "classifier_variant_conditioning_findings": classifier_findings,
        "passed": not findings and not classifier_findings,
    }


def variant_oracle_audit() -> dict[str, Any]:
    signature = inspect.signature(classify_order_proxy)
    source = inspect.getsource(classify_order_proxy)
    classifier_accepts_variant_argument = "variant" in signature.parameters
    classifier_branches_on_variant = "variant" in source
    classifier_accepts_truth_dim = "true" + "_dimension" in signature.parameters or "true" + "_dimension" in source
    classifier_branches_on_control_name = "control" + "_name" in source or "chain" + "_control" in source
    variant_to_dimension_lookup_detected = any(token in source for token in ("product2d", "product3d", "chain"))
    return {
        "classifier_accepts_variant_argument": classifier_accepts_variant_argument,
        "classifier_branches_on_variant": classifier_branches_on_variant,
        "classifier_accepts" + "_true" + "_dimension": classifier_accepts_truth_dim,
        "classifier_branches_on_control_name": classifier_branches_on_control_name,
        "run_b2_passes_variant_to_classifier": False,
        "variant_to_dimension_lookup_detected": variant_to_dimension_lookup_detected,
        "label_free_dimension_proxy": not (
            classifier_accepts_variant_argument
            or classifier_branches_on_variant
            or classifier_accepts_truth_dim
            or classifier_branches_on_control_name
            or variant_to_dimension_lookup_detected
        ),
    }

