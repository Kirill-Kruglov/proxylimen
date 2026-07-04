"""B2.3 exploratory local-kNN diagnostic.

Explains why the global pairwise-distance CV at crossover differs between
n=1000 and n=5000. This script intentionally reads true coordinates; it is not
learner-path code, not a gate, and does not modify B2.3 decision artifacts.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUTS = HERE / "outputs"
sys.path.insert(0, str(HERE))
import run_b2_3 as B23  # noqa: E402

K_VALUES = (10, 15, 20)
PRIMARY_K = 15
SEEDS = B23.FINAL_SEEDS
PAIR_SAMPLE_SIZE = 20_000
GRID = {
    1000: [120, 129, 130, 131, 140],
    5000: [22, 23, 24, 25, 26],
}
CROSSOVER_D = {1000: 130, 5000: 24}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def nearest_with_distances(points: np.ndarray, max_rank: int, chunk: int = 512) -> tuple[np.ndarray, np.ndarray]:
    n = int(points.shape[0])
    nearest = np.empty((n, max_rank), dtype=np.int32)
    distances = np.empty((n, max_rank), dtype=np.float64)
    norms = np.sum(points * points, axis=1)
    for start in range(0, n, chunk):
        stop = min(start + chunk, n)
        sq = norms[start:stop, None] + norms[None, :] - 2.0 * (points[start:stop] @ points.T)
        np.maximum(sq, 0.0, out=sq)
        rows = np.arange(stop - start)
        sq[rows, start + rows] = np.inf
        candidates = np.argpartition(sq, kth=max_rank, axis=1)[:, :max_rank]
        candidate_sq = np.take_along_axis(sq, candidates, axis=1)
        order = np.argsort(candidate_sq, axis=1)
        sorted_candidates = np.take_along_axis(candidates, order, axis=1)
        sorted_sq = np.take_along_axis(candidate_sq, order, axis=1)
        nearest[start:stop] = sorted_candidates
        distances[start:stop] = np.sqrt(sorted_sq)
    return nearest, distances


def ball_sets(nearest: np.ndarray, k: int) -> list[set[int]]:
    return [set((i, *map(int, nearest[i, :k]))) for i in range(nearest.shape[0])]


def random_pair_shared_probability(balls: list[set[int]], seed: int, samples: int) -> float:
    n = len(balls)
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(samples):
        i = int(rng.integers(0, n))
        j = int(rng.integers(0, n - 1))
        if j >= i:
            j += 1
        if len(balls[i] & balls[j]) > 1:
            hits += 1
    return hits / samples


def edge_pair_shared_probability(nearest: np.ndarray, balls: list[set[int]], k: int) -> float:
    hits = 0
    total = nearest.shape[0] * k
    for i in range(nearest.shape[0]):
        bi = balls[i]
        for j in nearest[i, :k]:
            if len(bi & balls[int(j)]) > 1:
                hits += 1
    return hits / total


def global_pairwise_cv(points: np.ndarray, chunk: int = 512) -> float:
    n = int(points.shape[0])
    norms = np.sum(points * points, axis=1)
    total = 0.0
    total_sq = 0.0
    count = 0
    for start in range(0, n, chunk):
        stop = min(start + chunk, n)
        sq = norms[start:stop, None] + norms[None, :] - 2.0 * (points[start:stop] @ points.T)
        np.maximum(sq, 0.0, out=sq)
        for local_i, global_i in enumerate(range(start, stop)):
            vals_sq = sq[local_i, global_i + 1 :]
            if vals_sq.size:
                total += float(np.sqrt(vals_sq).sum())
                total_sq += float(vals_sq.sum())
                count += int(vals_sq.size)
    mean = total / count
    var = max(0.0, total_sq / count - mean * mean)
    return math.sqrt(var) / mean


def seed_metrics(n: int, d: int, seed: int) -> dict[str, Any]:
    points = np.random.default_rng(seed).random((n, d))
    nearest, distances = nearest_with_distances(points, max(K_VALUES) + 1)
    out: dict[str, Any] = {
        "seed": seed,
        "global_pairwise_distance_cv": global_pairwise_cv(points),
        "by_k": {},
    }
    first_mean = float(distances[:, 0].mean())
    for k in K_VALUES:
        kth_plus_one_mean = float(distances[:, k].mean())
        balls = ball_sets(nearest, k)
        out["by_k"][str(k)] = {
            "mean_dist_to_1st_neighbor": first_mean,
            "mean_dist_to_k_plus_1_neighbor": kth_plus_one_mean,
            "relative_contrast_kNN": (kth_plus_one_mean - first_mean) / first_mean,
            "random_pair_shared_neighbors_gt1": random_pair_shared_probability(
                balls, seed + 9_000_001 * k, PAIR_SAMPLE_SIZE
            ),
            "edge_pair_shared_neighbors_gt1": edge_pair_shared_probability(nearest, balls, k),
        }
    return out


def summarize_cell(n: int, d: int) -> dict[str, Any]:
    rows = [seed_metrics(n, d, seed) for seed in SEEDS]
    out: dict[str, Any] = {
        "n": n,
        "d": d,
        "N": len(rows),
        "global_pairwise_distance_cv_mean": float(np.mean([r["global_pairwise_distance_cv"] for r in rows])),
        "global_pairwise_distance_cv_std": float(np.std([r["global_pairwise_distance_cv"] for r in rows])),
        "by_k": {},
        "rows": rows,
    }
    for k in K_VALUES:
        key = str(k)
        out["by_k"][key] = {}
        for metric in [
            "mean_dist_to_1st_neighbor",
            "mean_dist_to_k_plus_1_neighbor",
            "relative_contrast_kNN",
            "random_pair_shared_neighbors_gt1",
            "edge_pair_shared_neighbors_gt1",
        ]:
            vals = [r["by_k"][key][metric] for r in rows]
            out["by_k"][key][metric + "_mean"] = float(np.mean(vals))
            out["by_k"][key][metric + "_std"] = float(np.std(vals))
    return out


def ratio(a: float, b: float) -> float:
    return a / b if b else float("inf")


def build_comparison(cells: list[dict[str, Any]]) -> dict[str, Any]:
    by_key = {(c["n"], c["d"]): c for c in cells}
    c1000 = by_key[(1000, CROSSOVER_D[1000])]
    c5000 = by_key[(5000, CROSSOVER_D[5000])]
    comparison = {
        "crossover_points": {
            "n1000": {"n": 1000, "d": CROSSOVER_D[1000]},
            "n5000": {"n": 5000, "d": CROSSOVER_D[5000]},
        },
        "global_distance_cv": {
            "n1000": c1000["global_pairwise_distance_cv_mean"],
            "n5000": c5000["global_pairwise_distance_cv_mean"],
            "ratio_n5000_over_n1000": ratio(c5000["global_pairwise_distance_cv_mean"], c1000["global_pairwise_distance_cv_mean"]),
        },
        "by_k": {},
    }
    for k in K_VALUES:
        key = str(k)
        comparison["by_k"][key] = {}
        for metric in [
            "relative_contrast_kNN",
            "random_pair_shared_neighbors_gt1",
            "edge_pair_shared_neighbors_gt1",
        ]:
            m = metric + "_mean"
            a = c1000["by_k"][key][m]
            b = c5000["by_k"][key][m]
            comparison["by_k"][key][metric] = {
                "n1000": a,
                "n5000": b,
                "ratio_n5000_over_n1000": ratio(b, a),
                "unifies_within_20_percent": 0.8 <= ratio(b, a) <= 1.2,
            }
    return comparison


def write_report(payload: dict[str, Any]) -> None:
    comp = payload["crossover_comparison"]
    lines = [
        "# B2.3 Local kNN Mechanism Diagnostic",
        "",
        "Exploratory diagnostic only. True coordinates are used outside learner path.",
        "Core B2.3 decision artifacts are not modified.",
        "",
        "## Metric at crossover",
        "",
        "| metric | n=1000,d=130 | n=5000,d=24 | ratio n5000/n1000 | within 1.0±0.2? |",
        "|---|---:|---:|---:|---:|",
        f"| global pairwise distance CV | {comp['global_distance_cv']['n1000']:.6f} | {comp['global_distance_cv']['n5000']:.6f} | {comp['global_distance_cv']['ratio_n5000_over_n1000']:.3f} | false |",
    ]
    for k in K_VALUES:
        for metric, label in [
            ("relative_contrast_kNN", f"relative contrast k={k}"),
            ("random_pair_shared_neighbors_gt1", f"random-pair shared-neighbor P>1 k={k}"),
            ("edge_pair_shared_neighbors_gt1", f"edge-pair shared-neighbor P>1 k={k}"),
        ]:
            item = comp["by_k"][str(k)][metric]
            lines.append(
                f"| {label} | {item['n1000']:.6f} | {item['n5000']:.6f} | "
                f"{item['ratio_n5000_over_n1000']:.3f} | {str(item['unifies_within_20_percent']).lower()} |"
            )
    primary = comp["by_k"][str(PRIMARY_K)]
    candidates = [
        ("relative contrast k=15", primary["relative_contrast_kNN"]),
        ("random-pair shared-neighbor P>1 k=15", primary["random_pair_shared_neighbors_gt1"]),
        ("edge-pair shared-neighbor P>1 k=15", primary["edge_pair_shared_neighbors_gt1"]),
    ]
    unified = [name for name, item in candidates if item["unifies_within_20_percent"]]
    if unified:
        conclusion = "The local metric that best unifies the two crossover points is: " + ", ".join(unified) + "."
    else:
        conclusion = "None of the tested k=15 local metrics unified the two crossover points within ratio 1.0±0.2."
    lines += [
        "",
        "## Cell table, k=15",
        "",
        "| n | d | global CV | relative contrast k=15 | random-pair shared P>1 | edge-pair shared P>1 |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for c in payload["cells"]:
        k = c["by_k"][str(PRIMARY_K)]
        lines.append(
            f"| {c['n']} | {c['d']} | {c['global_pairwise_distance_cv_mean']:.6f} | "
            f"{k['relative_contrast_kNN_mean']:.6f} | "
            f"{k['random_pair_shared_neighbors_gt1_mean']:.6f} | "
            f"{k['edge_pair_shared_neighbors_gt1_mean']:.6f} |"
        )
    lines += ["", "## One-paragraph conclusion", "", conclusion]
    (HERE / "B2_3_local_knn_mechanism_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    start = time.time()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    cells = []
    total = sum(len(v) for v in GRID.values())
    done = 0
    for n, ds in GRID.items():
        for d in ds:
            done += 1
            cell = summarize_cell(n, d)
            cells.append(cell)
            write_json(OUTPUTS / "local_knn_mechanism_partial.json", {"completed": done, "total": total, "cells": cells})
    payload = {
        "diagnostic": "B2.3 local kNN mechanism exploratory diagnostic",
        "true_coordinates_used": True,
        "learner_path": False,
        "grid": GRID,
        "seeds": SEEDS,
        "k_values": K_VALUES,
        "primary_k": PRIMARY_K,
        "pair_sample_size_per_seed": PAIR_SAMPLE_SIZE,
        "cells": cells,
        "crossover_comparison": build_comparison(cells),
        "elapsed_seconds": time.time() - start,
    }
    write_json(OUTPUTS / "local_knn_mechanism_results.json", payload)
    write_report(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
