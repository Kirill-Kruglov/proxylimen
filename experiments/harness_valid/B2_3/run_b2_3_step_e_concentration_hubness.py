"""B2.3 Step E exploratory concentration/hubness diagnostic.

This diagnostic intentionally reads true coordinates. It is not learner-path code,
not a core gate, and not a pass/fail test. It looks for an explanatory mechanism
behind the B2.3 paired-separation crossover by measuring:
  1. coefficient of variation of all pairwise Euclidean distances;
  2. hubness skewness of kNN in-degree distributions.
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
N_VALUES = (1000, 5000)
FOCUS_D = [20, 22, 23, 24, 25, 26, 30, 32, 34, 36, 38, 40, 120, 129, 130, 131, 140]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_b2_3_metrics() -> dict[tuple[int, int], dict[str, Any]]:
    results = json.loads((OUTPUTS / "crossover_results.json").read_text(encoding="utf-8"))
    out: dict[tuple[int, int], dict[str, Any]] = {}
    for n, cells in results["final_cells_by_n"].items():
        for cell in cells:
            out[(int(n), int(cell["d"]))] = {
                "paired_separation": cell["paired_separation"],
                "paired_separation_wilson_95": cell["paired_separation_wilson_95"],
                "mean_margin_random_minus_geo": cell["mean_margin_random_minus_geo"],
                "source": "core_b2_3_final_grid",
            }
    dense_path = OUTPUTS / "dense_d_8_30_scan.json"
    if dense_path.exists():
        dense = json.loads(dense_path.read_text(encoding="utf-8"))
        for n, cells in dense["cells_by_n"].items():
            for cell in cells:
                key = (int(n), int(cell["d"]))
                out.setdefault(
                    key,
                    {
                        "paired_separation": cell["paired_separation"],
                        "paired_separation_wilson_95": cell["paired_separation_wilson_95"],
                        "mean_margin_random_minus_geo": cell["mean_margin_random_minus_geo"],
                        "source": "dense_d_8_30_diagnostic_grid",
                    },
                )
    return out


def grid_cells() -> list[dict[str, Any]]:
    metrics = load_b2_3_metrics()
    keys = set(metrics)
    for n in N_VALUES:
        for d in FOCUS_D:
            keys.add((n, d))
    cells = []
    for n, d in sorted(keys):
        if n not in N_VALUES:
            continue
        m = metrics.get((n, d), {})
        if (n, d) in metrics:
            source = m["source"]
        elif d in FOCUS_D:
            source = "exploratory_cross_n_focus_addition"
        else:
            source = "unknown"
        cells.append({"n": n, "d": d, "grid_source": source, "b2_3_metric": m or None})
    return cells


def geometry_stats(points: np.ndarray, max_k: int = max(K_VALUES), chunk: int = 512) -> dict[str, Any]:
    n = int(points.shape[0])
    nearest = np.empty((n, max_k), dtype=np.int32)
    norms = np.sum(points * points, axis=1)
    dist_sum = 0.0
    dist_sq_sum = 0.0
    dist_count = 0
    for start in range(0, n, chunk):
        stop = min(start + chunk, n)
        sq = norms[start:stop, None] + norms[None, :] - 2.0 * (points[start:stop] @ points.T)
        np.maximum(sq, 0.0, out=sq)
        for local_i, global_i in enumerate(range(start, stop)):
            vals_sq = sq[local_i, global_i + 1 :]
            if vals_sq.size:
                dist_sum += float(np.sqrt(vals_sq).sum())
                dist_sq_sum += float(vals_sq.sum())
                dist_count += int(vals_sq.size)
        rows = np.arange(stop - start)
        sq[rows, start + rows] = np.inf
        candidates = np.argpartition(sq, kth=max_k, axis=1)[:, :max_k]
        candidate_dist = np.take_along_axis(sq, candidates, axis=1)
        order = np.argsort(candidate_dist, axis=1)
        nearest[start:stop] = np.take_along_axis(candidates, order, axis=1)
    mean_dist = dist_sum / dist_count
    variance = max(0.0, dist_sq_sum / dist_count - mean_dist * mean_dist)
    cv = math.sqrt(variance) / mean_dist if mean_dist else 0.0
    hubness = {}
    for k in K_VALUES:
        indegree = np.bincount(nearest[:, :k].ravel(), minlength=n).astype(float)
        mean = float(indegree.mean())
        std = float(indegree.std())
        skew = 0.0 if std == 0.0 else float(np.mean(((indegree - mean) / std) ** 3))
        hubness[str(k)] = {
            "mean_indegree": mean,
            "std_indegree": std,
            "skewness": skew,
            "max_indegree": int(indegree.max()),
            "zero_indegree_fraction": float(np.mean(indegree == 0.0)),
        }
    return {
        "pairwise_distance_mean": mean_dist,
        "pairwise_distance_std": math.sqrt(variance),
        "pairwise_distance_cv": cv,
        "hubness_by_k": hubness,
    }


def summarize_cell(n: int, d: int, seeds: list[int]) -> dict[str, Any]:
    rows = []
    for seed in seeds:
        points = np.random.default_rng(seed).random((n, d))
        stats = geometry_stats(points)
        rows.append({"seed": seed, **stats})
    cv_values = [r["pairwise_distance_cv"] for r in rows]
    out = {
        "n": n,
        "d": d,
        "N": len(rows),
        "mean_pairwise_distance_cv": sum(cv_values) / len(cv_values),
        "std_pairwise_distance_cv": float(np.std(cv_values)),
        "mean_pairwise_distance_mean": sum(r["pairwise_distance_mean"] for r in rows) / len(rows),
        "mean_pairwise_distance_std": sum(r["pairwise_distance_std"] for r in rows) / len(rows),
        "hubness_by_k": {},
        "rows": rows,
    }
    for k in K_VALUES:
        key = str(k)
        skews = [r["hubness_by_k"][key]["skewness"] for r in rows]
        maxes = [r["hubness_by_k"][key]["max_indegree"] for r in rows]
        zeros = [r["hubness_by_k"][key]["zero_indegree_fraction"] for r in rows]
        out["hubness_by_k"][key] = {
            "mean_skewness": sum(skews) / len(skews),
            "std_skewness": float(np.std(skews)),
            "mean_max_indegree": sum(maxes) / len(maxes),
            "mean_zero_indegree_fraction": sum(zeros) / len(zeros),
        }
    return out


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0.0 or vy == 0.0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def analyze(cells: list[dict[str, Any]]) -> dict[str, Any]:
    by_n: dict[str, Any] = {}
    for n in N_VALUES:
        subset = [c for c in cells if c["n"] == n and c.get("b2_3_metric")]
        ps = [c["b2_3_metric"]["paired_separation"] for c in subset]
        cv = [c["mean_pairwise_distance_cv"] for c in subset]
        skew = [c["hubness_by_k"][str(PRIMARY_K)]["mean_skewness"] for c in subset]
        by_n[str(n)] = {
            "pearson_paired_separation_vs_distance_cv": pearson(ps, cv),
            "pearson_paired_separation_vs_hubness_skew_k15": pearson(ps, skew),
            "cells_with_b2_3_metric": len(subset),
            "first_d_with_paired_separation_le_0_5": next((c["d"] for c in sorted(subset, key=lambda x: x["d"]) if c["b2_3_metric"]["paired_separation"] <= 0.5), None),
        }
    return by_n


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# B2.3 Step E — Concentration / Hubness Exploratory Diagnostic",
        "",
        "This diagnostic reads true coordinates and is not learner-path code.",
        "It is explanatory, not a preregistered pass/fail gate.",
        "",
        "## Summary correlations",
        "",
        "| n | corr(paired separation, distance CV) | corr(paired separation, hubness skew k=15) | crossover d in included B2.3 metrics |",
        "|---:|---:|---:|---:|",
    ]
    for n, item in payload["analysis_by_n"].items():
        lines.append(
            f"| {n} | {item['pearson_paired_separation_vs_distance_cv']} | "
            f"{item['pearson_paired_separation_vs_hubness_skew_k15']} | "
            f"{item['first_d_with_paired_separation_le_0_5']} |"
        )
    lines += [
        "",
        "## Cell table",
        "",
        "| n | d | source | paired separation | distance CV | hubness skew k=15 | max indegree k=15 | zero indegree fraction k=15 |",
        "|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for c in payload["cells"]:
        metric = c.get("b2_3_metric") or {}
        h = c["hubness_by_k"][str(PRIMARY_K)]
        ps = metric.get("paired_separation")
        lines.append(
            f"| {c['n']} | {c['d']} | {c['grid_source']} | {'' if ps is None else round(ps, 3)} | "
            f"{c['mean_pairwise_distance_cv']:.5f} | {h['mean_skewness']:.5f} | "
            f"{h['mean_max_indegree']:.2f} | {h['mean_zero_indegree_fraction']:.5f} |"
        )
    lines += [
        "",
        "## Interpretation guard",
        "No substrate, theorem-confirmation, dimension-accuracy, or real-world transfer claim is made.",
    ]
    (HERE / "B2_3_step_e_concentration_hubness_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    start = time.time()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    requested = grid_cells()
    out_cells = []
    for idx, cell in enumerate(requested, 1):
        summary = summarize_cell(cell["n"], cell["d"], SEEDS)
        merged = {**cell, **summary}
        out_cells.append(merged)
        write_json(OUTPUTS / "concentration_hubness_partial.json", {"completed": idx, "total": len(requested), "cells": out_cells})
    payload = {
        "diagnostic": "B2.3 Step E concentration/hubness exploratory diagnostic",
        "true_coordinates_used": True,
        "learner_path": False,
        "seeds": SEEDS,
        "k_values": list(K_VALUES),
        "primary_hubness_k": PRIMARY_K,
        "cells": out_cells,
        "analysis_by_n": analyze(out_cells),
        "elapsed_seconds": time.time() - start,
    }
    write_json(OUTPUTS / "concentration_hubness_results.json", payload)
    write_report(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
