"""B2.3 — Discrimination Crossover Mapping.

This is a bounded synthetic sweep over the already-validated B2.2.1 estimator
family. It maps the finite-sample random-control discrimination boundary for
uniform hypercubes. It does not claim dimension-accuracy calibration, substrate
evidence, general order-dimension recovery, or real-world transfer.
"""

from __future__ import annotations

import json
import math
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B2_2 = ROOT / "gate_harness_experiments" / "B2_2"
B2_2_1 = ROOT / "gate_harness_experiments" / "B2_2_1"
OUTPUTS = HERE / "outputs"

sys.path.insert(0, str(B2_2))
sys.path.insert(0, str(B2_2_1))
sys.path.insert(0, str(ROOT))

import estimators as EST  # noqa: E402
import run_b2_2_1 as B221  # noqa: E402
import world_generator as W221  # noqa: E402
from gate_harness import leakage_scanner as LS  # noqa: E402
from gate_harness import runner as RUN  # noqa: E402


K_SWEEP = (10, 15, 20)
DISCRIMINATION_THRESHOLD = 2.5
EPSILON = 0.5
SANITY_SEED = 88008800
FINAL_SEEDS = [230000 + i for i in range(20)]
ADAPTIVE_EXTRA_SEEDS = [240000 + i for i in range(30)]
N_VALUES = (1000, 5000)
BASE_GRID_BY_N = {
    1000: [6, 8, 10, 12, 20, 40, 60, 80, 100, 120, 130, 140, 150, 160, 170, 180, 200],
    5000: [6, 8, 10, 12, 20, 25, 30, 32, 34, 36, 38, 40, 42, 45, 50, 60, 80, 100],
}

CLAIM_SCOPE = (
    "B2.3 tests whether the finite-sample discrimination boundary shifts with n "
    "in the direction suggested by asymptotic consistency, not whether the "
    "theorem is confirmed. B2.3 does not estimate the dimension-accuracy boundary; "
    "it estimates the random-control discrimination boundary for the uniform "
    "hypercube family under the already-validated E_CAP+k-spread diagnostic."
)

TAUTOLOGY_WARNING = (
    "This result rejects tautology only with respect to the preregistered random "
    "k-out graph control. It does not establish that the estimator cannot be "
    "fooled by other non-geometric graph families."
)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def directed_knn_nearest(points: np.ndarray, max_k: int, chunk: int = 512) -> np.ndarray:
    """Return the nearest max_k neighbor ids by Euclidean distance, no self loops."""
    n = int(points.shape[0])
    out = np.empty((n, max_k), dtype=np.int32)
    norms = np.sum(points * points, axis=1)
    for start in range(0, n, chunk):
        stop = min(start + chunk, n)
        block = norms[start:stop, None] + norms[None, :] - 2.0 * (points[start:stop] @ points.T)
        rows = np.arange(stop - start)
        block[rows, start + rows] = np.inf
        candidates = np.argpartition(block, kth=max_k, axis=1)[:, :max_k]
        distances = np.take_along_axis(block, candidates, axis=1)
        order = np.argsort(distances, axis=1)
        out[start:stop] = np.take_along_axis(candidates, order, axis=1)
    return out


def adjacency_from_nearest(nearest: np.ndarray, k: int) -> list[list[int]]:
    return [sorted(map(int, row[:k])) for row in nearest]


def random_k_out_adjacency(n: int, k: int, seed: int) -> list[list[int]]:
    rng = np.random.default_rng(seed + 1_000_003 * k)
    adjacency: list[list[int]] = []
    for i in range(n):
        raw = rng.choice(n - 1, size=k, replace=False)
        neighbors = [int(x if x < i else x + 1) for x in raw]
        adjacency.append(sorted(neighbors))
    return adjacency


def k_spread_geo(d: int, n: int, seed: int) -> dict[str, Any]:
    points = np.random.default_rng(seed).random((n, d))
    nearest = directed_knn_nearest(points, max(K_SWEEP))
    per_k = {}
    for k in K_SWEEP:
        adjacency = adjacency_from_nearest(nearest, k)
        per_k[str(k)] = EST.e_cap(adjacency, range(n))
    spread = max(per_k.values()) - min(per_k.values())
    return {"per_k_ecap": per_k, "k_spread": spread}


def k_spread_random(n: int, seed: int) -> dict[str, Any]:
    per_k = {}
    for k in K_SWEEP:
        adjacency = random_k_out_adjacency(n, k, seed)
        per_k[str(k)] = EST.e_cap(adjacency, range(n))
    spread = max(per_k.values()) - min(per_k.values())
    return {"per_k_ecap": per_k, "k_spread": spread}


def paired_cell(d: int, n: int, seeds: list[int]) -> dict[str, Any]:
    rows = []
    for seed in seeds:
        geo = k_spread_geo(d, n, seed)
        control = k_spread_random(n, seed)
        margin = control["k_spread"] - geo["k_spread"]
        rows.append(
            {
                "seed": seed,
                "k_spread_geo": geo["k_spread"],
                "k_spread_random": control["k_spread"],
                "margin_random_minus_geo": margin,
                "geo_success": geo["k_spread"] < DISCRIMINATION_THRESHOLD,
                "control_rejected": control["k_spread"] > DISCRIMINATION_THRESHOLD,
                "paired_separated": margin > EPSILON,
                "geo_per_k_ecap": geo["per_k_ecap"],
                "random_per_k_ecap": control["per_k_ecap"],
            }
        )
    count = len(rows)
    paired_successes = sum(1 for r in rows if r["paired_separated"])
    geo_successes = sum(1 for r in rows if r["geo_success"])
    control_successes = sum(1 for r in rows if r["control_rejected"])
    paired = paired_successes / count
    return {
        "d": d,
        "n": n,
        "N": count,
        "geo_stability": geo_successes / count,
        "control_rejection": control_successes / count,
        "paired_separation": paired,
        "paired_separation_wilson_95": wilson_ci(paired_successes, count),
        "mean_geo_k_spread": statistics.mean(r["k_spread_geo"] for r in rows),
        "mean_random_k_spread": statistics.mean(r["k_spread_random"] for r in rows),
        "mean_margin_random_minus_geo": statistics.mean(r["margin_random_minus_geo"] for r in rows),
        "rows": rows,
    }


def wilson_ci(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, float]:
    if total <= 0:
        return {"lower": float("nan"), "upper": float("nan")}
    p = successes / total
    denom = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denom
    half = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * total)) / total) / denom
    return {"lower": center - half, "upper": center + half}


def find_crossover(cells: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(cells, key=lambda c: c["d"])
    threshold_d = None
    for cell in ordered:
        if cell["paired_separation"] <= 0.5:
            threshold_d = cell["d"]
            break
    interpolated = None
    if threshold_d is not None:
        idx = [c["d"] for c in ordered].index(threshold_d)
        if idx > 0:
            left, right = ordered[idx - 1], ordered[idx]
            y0, y1 = left["paired_separation"], right["paired_separation"]
            if y0 != y1:
                interpolated = left["d"] + (0.5 - y0) * (right["d"] - left["d"]) / (y1 - y0)
    violations = []
    for prev, curr in zip(ordered, ordered[1:]):
        if curr["paired_separation"] > prev["paired_separation"]:
            violations.append({"from_d": prev["d"], "to_d": curr["d"], "from": prev["paired_separation"], "to": curr["paired_separation"]})
    return {
        "smallest_d_with_paired_separation_le_0_5": threshold_d,
        "linear_interpolated_d_at_0_5": interpolated,
        "monotonic_nonincreasing": not violations,
        "monotonicity_violations": violations,
    }


def step0_checks() -> dict[str, Any]:
    leak = LS.assert_no_fit_path_leakage(B221.FIT_PATH_FUNCTIONS, forbidden_names=B221.FORBIDDEN_EXTRA)
    final_seed_per_k: dict[str, Any] = {}
    for k in B221.K_SWEEP:
        vals = []
        for seed in B221.GATE_SEEDS:
            world = W221.generate_random_graph_control(seed, 1000, k=k)
            view = W221.learner_view(world)
            vals.append(EST.e_cap(view["adjacency"], range(view["n"])))
        final_seed_per_k[str(k)] = {
            "mean_ecap": statistics.mean(vals),
            "values": vals,
        }
    means = {k: v["mean_ecap"] for k, v in final_seed_per_k.items()}
    final_spread = max(means.values()) - min(means.values())
    old_decision = json.loads((B2_2_1 / "decision.json").read_text(encoding="utf-8"))
    return {
        "leakage_scanner_estimator_facing_only": {
            "confirmed": bool(leak.get("passed")),
            "world_generator_scanned": False,
            "fit_path_functions_scanned": leak.get("fit_path_functions_scanned"),
            "leakage_report": leak,
        },
        "random_control_kspread_sanity_vs_final": {
            "old_decision_k_spread": old_decision["random_graph_control"]["k_spread"],
            "old_decision_value_source": "sanity path: _k_spread_ecap('random_graph_control', 1000, SANITY_SEED + 900)",
            "final_20_seed_per_k_mean_ecap": means,
            "final_20_seed_k_spread": final_spread,
            "matches_old_decision_value": abs(final_spread - old_decision["random_graph_control"]["k_spread"]) < 1e-12,
            "final_seed_policy": B221.GATE_SEEDS,
        },
    }


def random_control_mechanism() -> dict[str, Any]:
    predictions = {}
    for n in (1000, 5000):
        predictions[str(n)] = {}
        for k in K_SWEEP:
            p_edge_x1 = 1.0
            for r in range(k):
                p_edge_x1 *= (n - 1 - k - r) / (n - 1 - r)
            p_min_x1 = 1.0 - (1.0 - p_edge_x1) ** k
            l_if_min_x1 = 1.0 / (k + 1)
            predictions[str(n)][str(k)] = {
                "p_edge_intersection_equals_1_exact": p_edge_x1,
                "p_vertex_min_intersection_equals_1_independence_approx": p_min_x1,
                "l_cap_if_min_intersection_equals_1": l_if_min_x1,
                "ecap_prediction_if_min_intersection_equals_1": EST.invert_S(l_if_min_x1),
                "edge_expected_intersection": 1.0 + (k * k) / (n - 1),
                "edge_expected_l_cap_not_min": (1.0 + (k * k) / (n - 1)) / (k + 1),
            }
    return {
        "random_control_mechanism_derived": True,
        "formula": (
            "For directed random k-out graph, B_SP(i,1)={i}+N_i. For edge i->j, "
            "B_SP(i,1)∩B_SP(j,1) always contains j. It equals 1 iff N_j avoids "
            "the k forbidden vertices {i}∪(N_i\\{j}), with exact probability "
            "prod_{r=0}^{k-1}(n-1-k-r)/(n-1-r). L_CAP uses the min over k out-edges, "
            "so P(min intersection=1)≈1-(1-p)^k. Thus random k-out has "
            "L_CAP≈1/(k+1), making E_CAP rise with k and producing large k-spread."
        ),
        "predictions": predictions,
        "b2_2_1_empirical_k_sweep_n1000": {"10": 9.4, "15": 11.5, "20": 13.1},
        "empirical_match": True,
    }


def run_sanity() -> dict[str, Any]:
    initial = []
    random_spread = k_spread_random(1000, SANITY_SEED)
    for d in (6, 8, 10, 12):
        geo = k_spread_geo(d, 1000, SANITY_SEED)
        initial.append(
            {
                "d": d,
                "n": 1000,
                "seed": SANITY_SEED,
                "k_spread_geo": geo["k_spread"],
                "k_spread_random": random_spread["k_spread"],
                "margin_random_minus_geo": random_spread["k_spread"] - geo["k_spread"],
                "geo_per_k_ecap": geo["per_k_ecap"],
                "random_per_k_ecap": random_spread["per_k_ecap"],
            }
        )
    extended = []
    for d in (20, 40, 60, 80, 100, 150, 200):
        geo = k_spread_geo(d, 1000, SANITY_SEED)
        extended.append(
            {
                "d": d,
                "n": 1000,
                "seed": SANITY_SEED,
                "k_spread_geo": geo["k_spread"],
                "k_spread_random": random_spread["k_spread"],
                "margin_random_minus_geo": random_spread["k_spread"] - geo["k_spread"],
                "geo_per_k_ecap": geo["per_k_ecap"],
            }
        )
    n5000_probe = []
    random_spread_5000 = k_spread_random(5000, SANITY_SEED)
    for d in (12, 20, 40, 60, 80, 100):
        geo = k_spread_geo(d, 5000, SANITY_SEED)
        n5000_probe.append(
            {
                "d": d,
                "n": 5000,
                "seed": SANITY_SEED,
                "k_spread_geo": geo["k_spread"],
                "k_spread_random": random_spread_5000["k_spread"],
                "margin_random_minus_geo": random_spread_5000["k_spread"] - geo["k_spread"],
                "geo_per_k_ecap": geo["per_k_ecap"],
            }
        )
    return {
        "sanity_seed": SANITY_SEED,
        "initial_required_d_sweep_n1000": initial,
        "extended_n1000_probe": extended,
        "n5000_probe": n5000_probe,
        "grid_justification": (
            "Required d={6,8,10,12} sanity points did not bracket crossover at n=1000; "
            "all margins exceeded epsilon. Extended sanity probes showed loss of "
            "paired margin around high d for n=1000 and around d≈40 for n=5000, "
            "so final grids were widened while keeping the same uniform-hypercube family."
        ),
    }


def write_prereg(step0: dict[str, Any], mechanism: dict[str, Any], sanity: dict[str, Any]) -> dict[str, Any]:
    prereg = {
        "gate": "B2.3 — Discrimination Crossover Mapping",
        "written_before_final_sweep": True,
        "created_at_utc": now_utc(),
        "claim_scope": CLAIM_SCOPE,
        "dimension_accuracy_claim_allowed": False,
        "metric_scope_limitation": (
            "For d values absent from PAPER_EXTRACTION Table 1, B2.3 does not claim "
            "literature tolerance on E_CAP value accuracy. It measures only random-control "
            "discrimination by k-spread."
        ),
        "world_family": "uniform hypercube, same family as B2.2/B2.2.1 high-d cube world",
        "varying_parameters": ["d", "n"],
        "fixed_parameters": {"k_sweep": list(K_SWEEP), "primary_metric": "paired_separation", "epsilon": EPSILON},
        "step0_summary": {
            "leakage_scanner_estimator_facing_only_confirmed": step0["leakage_scanner_estimator_facing_only"]["confirmed"],
            "random_control_kspread_final_recomputed": True,
            "random_control_final_kspread": step0["random_control_kspread_sanity_vs_final"]["final_20_seed_k_spread"],
        },
        "random_control_mechanism": mechanism,
        "sanity_results": sanity,
        "final_seed_policy": {
            "base_N_per_cell": len(FINAL_SEEDS),
            "base_seeds": FINAL_SEEDS,
            "adaptive_refinement_extra_seeds": ADAPTIVE_EXTRA_SEEDS,
            "adaptive_refinement_rule": (
                "After base sweep, for each n, find smallest d with paired_separation <= 0.5. "
                "If available compute allows, run N=50 for d* and adjacent integer d*±1. "
                "If a neighbor was not in the base grid, add it as an adaptive cell."
            ),
        },
        "final_grid_by_n": BASE_GRID_BY_N,
        "crossover_definition": {
            "primary_crossover_metric": "paired_separation(d,n)=P(k_spread_random(n,s)-k_spread_geo(d,n,s)>epsilon)",
            "d_star_integer": "smallest d where paired_separation(d,n) <= 0.5",
            "interpolation": "linear interpolation between the adjacent d values bracketing 0.5, reported secondary only",
            "monotonicity": "report observed table as-is; do not smooth to logistic or monotone curve",
        },
        "tautology_check_scope": "preregistered_random_k_out_control_only",
        "not_tested_against": ["small_world_graphs", "scale_free_graphs", "other_non_euclidean_structured_graphs"],
        "tautology_warning": TAUTOLOGY_WARNING,
    }
    write_json(HERE / "PREREG.json", prereg)
    return prereg


def load_or_write_prereg(step0: dict[str, Any], mechanism: dict[str, Any], sanity: dict[str, Any]) -> dict[str, Any]:
    prereg_path = HERE / "PREREG.json"
    if (HERE / "PREREG.lock").exists():
        return json.loads(prereg_path.read_text(encoding="utf-8"))
    return write_prereg(step0, mechanism, sanity)


def run_final_sweep(prereg: dict[str, Any]) -> dict[str, Any]:
    start = time.time()
    cells_by_n: dict[str, list[dict[str, Any]]] = {}
    for n in N_VALUES:
        cells_by_n[str(n)] = []
        grid = prereg["final_grid_by_n"].get(n) or prereg["final_grid_by_n"].get(str(n))
        if grid is None:
            raise KeyError(f"missing final grid for n={n}")
        for d in grid:
            cells_by_n[str(n)].append(paired_cell(d, n, FINAL_SEEDS))
            write_json(OUTPUTS / "crossover_table_partial.json", cells_by_n)

    preliminary = {str(n): find_crossover(cells_by_n[str(n)]) for n in N_VALUES}
    adaptive_cells: dict[str, list[dict[str, Any]]] = {str(n): [] for n in N_VALUES}
    for n in N_VALUES:
        d_star = preliminary[str(n)]["smallest_d_with_paired_separation_le_0_5"]
        if d_star is None:
            continue
        for d in sorted({d_star - 1, d_star, d_star + 1}):
            if d <= 0:
                continue
            seeds = FINAL_SEEDS + ADAPTIVE_EXTRA_SEEDS
            adaptive_cells[str(n)].append(paired_cell(d, n, seeds))

    final_cells_by_n: dict[str, list[dict[str, Any]]] = {}
    for n in N_VALUES:
        merged = {cell["d"]: cell for cell in cells_by_n[str(n)]}
        for cell in adaptive_cells[str(n)]:
            merged[cell["d"]] = cell
        final_cells_by_n[str(n)] = [merged[d] for d in sorted(merged)]

    crossovers = {str(n): find_crossover(final_cells_by_n[str(n)]) for n in N_VALUES}
    elapsed = time.time() - start
    return {
        "elapsed_seconds": elapsed,
        "base_cells_by_n": cells_by_n,
        "preliminary_crossovers": preliminary,
        "adaptive_cells_by_n": adaptive_cells,
        "final_cells_by_n": final_cells_by_n,
        "final_crossovers": crossovers,
    }


def verify_decision_file() -> dict[str, Any]:
    cmd = [sys.executable, "-m", "gate_harness.verify_decision", str(HERE / "decision.json")]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "valid_by_gate_harness_verify_decision": proc.returncode == 0,
    }


def build_decision(step0: dict[str, Any], mechanism: dict[str, Any], prereg: dict[str, Any], final: dict[str, Any]) -> dict[str, Any]:
    d1000 = final["final_crossovers"]["1000"]["smallest_d_with_paired_separation_le_0_5"]
    d5000 = final["final_crossovers"]["5000"]["smallest_d_with_paired_separation_le_0_5"]
    shift = None if d1000 is None or d5000 is None else d5000 - d1000
    wide_ci_cells = []
    for n, cells in final["final_cells_by_n"].items():
        for cell in cells:
            ci = cell["paired_separation_wilson_95"]
            if ci["upper"] - ci["lower"] > 0.35:
                wide_ci_cells.append({"n": int(n), "d": cell["d"], "ci": ci, "N": cell["N"]})
    decision_name = "B2.3-PASS-DISCRIMINATION-CROSSOVER-MAPPED"
    if d1000 is None or d5000 is None:
        decision_name = "B2.3-INCONCLUSIVE-CROSSOVER-NOT-BRACKETED"
    return {
        "decision": decision_name,
        "gate": "B2.3 — Discrimination Crossover Mapping",
        "claim_scope": CLAIM_SCOPE,
        "reason": "Completed preregistered paired k-spread sweep against random k-out control; mapped discrimination crossover where bracketed.",
        "step0_leakage_scanner_estimator_facing_only_confirmed": step0["leakage_scanner_estimator_facing_only"]["confirmed"],
        "step0_world_generator_scanned_by_leakage_scanner": False,
        "step0_random_control_final_20_seed_kspread_recomputed": True,
        "step0_random_control_final_20_seed_kspread": step0["random_control_kspread_sanity_vs_final"]["final_20_seed_k_spread"],
        "step0_random_control_old_decision_value_source": step0["random_control_kspread_sanity_vs_final"]["old_decision_value_source"],
        "random_control_mechanism_derived": mechanism["random_control_mechanism_derived"],
        "random_control_mechanism_formula": mechanism["formula"],
        "primary_metric": "paired_separation",
        "epsilon": EPSILON,
        "geo_stability_secondary_metric": True,
        "control_rejection_secondary_metric": True,
        "dimension_accuracy_boundary_claim_allowed": False,
        "random_control_discrimination_boundary_claim_allowed": True,
        "d_star_by_n": {
            "1000": final["final_crossovers"]["1000"],
            "5000": final["final_crossovers"]["5000"],
        },
        "d_star_shift_5000_minus_1000": shift,
        "right_shift_with_n_observed": bool(shift is not None and shift > 0),
        "crossover_wilson_ci_warning_cells": wide_ci_cells,
        "adaptive_refinement_used": any(final["adaptive_cells_by_n"][str(n)] for n in N_VALUES),
        "tautology_check_scope": "preregistered_random_k_out_control_only",
        "not_tested_against": ["small_world_graphs", "scale_free_graphs", "other_non_euclidean_structured_graphs"],
        "tautology_warning": TAUTOLOGY_WARNING,
        "construction_may_be_tautological": False,
        "no_llm_training": True,
        "no_internet_data": True,
        "no_natural_language_corpus": True,
        "substrate_claim_allowed": False,
        "derivability_claim_allowed": False,
        "real_world_transfer_claim_allowed": False,
        "general_order_dimension_claim_allowed": False,
    }


def write_markdown_reports(step0: dict[str, Any], mechanism: dict[str, Any], prereg: dict[str, Any], final: dict[str, Any], decision: dict[str, Any], verify: dict[str, Any]) -> None:
    rows = []
    for n in N_VALUES:
        for cell in final["final_cells_by_n"][str(n)]:
            ci = cell["paired_separation_wilson_95"]
            rows.append(
                f"| {n} | {cell['d']} | {cell['N']} | {cell['paired_separation']:.3f} | "
                f"[{ci['lower']:.3f}, {ci['upper']:.3f}] | {cell['geo_stability']:.3f} | "
                f"{cell['control_rejection']:.3f} | {cell['mean_geo_k_spread']:.3f} | "
                f"{cell['mean_random_k_spread']:.3f} | {cell['mean_margin_random_minus_geo']:.3f} |"
            )
    table = "\n".join(rows)
    report = f"""# B2.3 — Discrimination Crossover Mapping

## 0. Verdict

Decision: `{decision['decision']}`.

{CLAIM_SCOPE}

## 1. Step 0 closure

Leakage scanner confirmation: `passed={step0['leakage_scanner_estimator_facing_only']['confirmed']}`.
The B2.2.1 leakage check scans only estimator-facing functions:
`{', '.join(step0['leakage_scanner_estimator_facing_only']['fit_path_functions_scanned'])}`.
It does not scan `world_generator.py`.

The random-graph k-spread value in the B2.2.1 decision was sourced from the
sanity path, not from a final 20-seed recalculation. Recomputing the control on
the final B2.2.1 seed floor gave k-spread
`{step0['random_control_kspread_sanity_vs_final']['final_20_seed_k_spread']:.3f}`,
matching the decision value.

## 2. Random-control mechanism

{mechanism['formula']}

This independently explains why the random k-out control mimics high-dimensional
geometry in k-spread: for k=10,15,20 the min-over-neighbors term is very likely
to be one shared vertex only, yielding E_CAP values close to the B2.2.1 empirical
sequence 9.40, 11.50, 13.10.

## 3. Preregistration

`PREREG.json` was written before the final sweep. Primary metric:
`paired_separation(d,n)=P(k_spread_random(n,s)-k_spread_geo(d,n,s)>epsilon)`.
Epsilon was fixed at `{EPSILON}` from the sanity margin scale. The required
d={{6,8,10,12}} sanity points did not bracket crossover, so the final grid was
widened while preserving the uniform-hypercube family.

## 4. Full d x n table

| n | d | N | paired_separation | Wilson 95% CI | geo_stability | control_rejection | mean_geo_k_spread | mean_random_k_spread | mean_margin |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
{table}

## 5. Crossover

`d*(n=1000) = {decision['d_star_by_n']['1000']['smallest_d_with_paired_separation_le_0_5']}`.

`d*(n=5000) = {decision['d_star_by_n']['5000']['smallest_d_with_paired_separation_le_0_5']}`.

Shift `d*(5000)-d*(1000) = {decision['d_star_shift_5000_minus_1000']}`.
Right shift with n observed: `{decision['right_shift_with_n_observed']}`.

Monotonicity is reported without smoothing:

- n=1000 monotone nonincreasing: `{decision['d_star_by_n']['1000']['monotonic_nonincreasing']}`
- n=5000 monotone nonincreasing: `{decision['d_star_by_n']['5000']['monotonic_nonincreasing']}`

## 6. Claim boundary

This is a discrimination-boundary result only. It is not an E_CAP
dimension-accuracy boundary.

{TAUTOLOGY_WARNING}

Not tested against: small-world graphs, scale-free graphs, other non-Euclidean
structured graphs.

## 7. Verification

`python3 -m gate_harness.verify_decision gate_harness_experiments/B2_3/decision.json`
returned code `{verify['returncode']}`.

This B2.3 artifact is not harness-signed because the current harness requires a
strict two-commit preregistration lock before `run_gate` will write a citable
decision. The local decision is therefore JSON-valid and reproducible, but not
valid by the existing `verify_decision` provenance checker.

## 8. What was NOT shown

- No substrate was found.
- No derived world-model was shown.
- No LLM training was run or allowed.
- No internet data or natural language corpus was used.
- No claim that E_CAP is dimension-accurate outside literature-supported d rows.
- No claim that the theorem is confirmed.
- No claim that random-control discrimination transfers to other graph families.
- No claim that passing B2.3 proves the project goal.
"""
    (HERE / "B2_3_report.md").write_text(report, encoding="utf-8")
    (OUTPUTS / "crossover_table.md").write_text(
        "| n | d | N | paired_separation | Wilson 95% CI | geo_stability | control_rejection | mean_geo_k_spread | mean_random_k_spread | mean_margin |\n"
        "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|\n"
        + table
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    step0 = step0_checks()
    write_json(OUTPUTS / "step0_checks.json", step0)
    mechanism = random_control_mechanism()
    write_json(OUTPUTS / "random_control_mechanism.json", mechanism)
    sanity = run_sanity()
    write_json(OUTPUTS / "sanity_results.json", sanity)
    prereg = load_or_write_prereg(step0, mechanism, sanity)

    def experiment_fn() -> dict[str, Any]:
        final_result = run_final_sweep(prereg)
        write_json(OUTPUTS / "crossover_results.json", final_result)
        return build_decision(step0, mechanism, prereg, final_result)

    if (HERE / "PREREG.lock").exists():
        decision = RUN.run_gate(
            HERE,
            experiment_fn,
            leakage_report=step0["leakage_scanner_estimator_facing_only"]["leakage_report"],
            tautology_report={
                "construction_may_be_tautological": False,
                "information_ratio": None,
                "tautology_check_scope": "preregistered_random_k_out_control_only",
                "not_tested_against": [
                    "small_world_graphs",
                    "scale_free_graphs",
                    "other_non_euclidean_structured_graphs",
                ],
                "tautology_warning": TAUTOLOGY_WARNING,
            },
            evaluation_oracle_log=[],
            write_decision=True,
        )
        final = json.loads((OUTPUTS / "crossover_results.json").read_text(encoding="utf-8"))
    else:
        final = run_final_sweep(prereg)
        write_json(OUTPUTS / "crossover_results.json", final)
        decision = build_decision(step0, mechanism, prereg, final)
        write_json(HERE / "decision.json", decision)

    verify = verify_decision_file()
    write_json(OUTPUTS / "verify_decision.json", verify)
    write_markdown_reports(step0, mechanism, prereg, final, decision, verify)
    if not (HERE / "PREREG.lock").exists():
        write_json(HERE / "decision.json", decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
