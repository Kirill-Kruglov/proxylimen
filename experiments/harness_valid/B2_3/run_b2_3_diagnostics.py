"""Post-B2.3 diagnostics requested before interpreting crossover shift.

Non-core/exploratory diagnostics:
- fixed-k=15 paired E_CAP separation, to test k-confound;
- S(d) numerical stability against scipy.special.betainc where available;
- dense d=8..30 paired k-spread scan for both n values.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUTS = HERE / "outputs"
sys.path.insert(0, str(ROOT / "gate_harness_experiments" / "B2_2"))
sys.path.insert(0, str(HERE))

import estimators as EST  # noqa: E402
import run_b2_3 as B23  # noqa: E402

FIXED_K = 15
FIXED_K_EPSILON = 0.5
DENSE_D = list(range(8, 31))
N_VALUES = [1000, 5000]
SEEDS = B23.FINAL_SEEDS
FIXED_K_GRID_BY_N = {
    1000: B23.BASE_GRID_BY_N[1000],
    5000: B23.BASE_GRID_BY_N[5000],
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixed_k_geo_ecap(d: int, n: int, seed: int, k: int = FIXED_K) -> float:
    points = np.random.default_rng(seed).random((n, d))
    nearest = B23.directed_knn_nearest(points, k)
    adjacency = B23.adjacency_from_nearest(nearest, k)
    return EST.e_cap(adjacency, range(n))


def fixed_k_random_ecap(n: int, seed: int, k: int = FIXED_K) -> float:
    adjacency = B23.random_k_out_adjacency(n, k, seed)
    return EST.e_cap(adjacency, range(n))


def wilson(successes: int, total: int) -> dict[str, float]:
    return B23.wilson_ci(successes, total)


def fixed_k_cell(d: int, n: int, seeds: list[int]) -> dict[str, Any]:
    rows = []
    for seed in seeds:
        geo = fixed_k_geo_ecap(d, n, seed)
        rnd = fixed_k_random_ecap(n, seed)
        margin = rnd - geo
        rows.append({
            "seed": seed,
            "ecap_geo_k15": geo,
            "ecap_random_k15": rnd,
            "margin_random_minus_geo": margin,
            "paired_separated": margin > FIXED_K_EPSILON,
        })
    successes = sum(1 for r in rows if r["paired_separated"])
    return {
        "d": d,
        "n": n,
        "N": len(rows),
        "fixed_k": FIXED_K,
        "epsilon": FIXED_K_EPSILON,
        "paired_separation_fixed_k15": successes / len(rows),
        "paired_separation_wilson_95": wilson(successes, len(rows)),
        "mean_geo_ecap_k15": sum(r["ecap_geo_k15"] for r in rows) / len(rows),
        "mean_random_ecap_k15": sum(r["ecap_random_k15"] for r in rows) / len(rows),
        "mean_margin_random_minus_geo": sum(r["margin_random_minus_geo"] for r in rows) / len(rows),
        "rows": rows,
    }


def crossover(cells: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    ordered = sorted(cells, key=lambda c: c["d"])
    threshold_d = None
    for c in ordered:
        if c[metric] <= 0.5:
            threshold_d = c["d"]
            break
    interp = None
    if threshold_d is not None:
        idx = [c["d"] for c in ordered].index(threshold_d)
        if idx > 0:
            left, right = ordered[idx - 1], ordered[idx]
            y0, y1 = left[metric], right[metric]
            if y0 != y1:
                interp = left["d"] + (0.5 - y0) * (right["d"] - left["d"]) / (y1 - y0)
    violations = []
    for a, b in zip(ordered, ordered[1:]):
        if b[metric] > a[metric]:
            violations.append({"from_d": a["d"], "to_d": b["d"], "from": a[metric], "to": b[metric]})
    return {
        "smallest_d_with_metric_le_0_5": threshold_d,
        "linear_interpolated_d_at_0_5": interp,
        "monotonic_nonincreasing": not violations,
        "monotonicity_violations": violations,
    }


def run_fixed_k_confound() -> dict[str, Any]:
    cells_by_n: dict[str, list[dict[str, Any]]] = {}
    for n in N_VALUES:
        cells = []
        for d in FIXED_K_GRID_BY_N[n]:
            cells.append(fixed_k_cell(d, n, SEEDS))
            write_json(OUTPUTS / "k_confound_fixed_k15_partial.json", cells_by_n | {str(n): cells})
        cells_by_n[str(n)] = cells
    cross = {n: crossover(cells, "paired_separation_fixed_k15") for n, cells in cells_by_n.items()}
    d1000 = cross["1000"]["smallest_d_with_metric_le_0_5"]
    d5000 = cross["5000"]["smallest_d_with_metric_le_0_5"]
    shift = None if d1000 is None or d5000 is None else d5000 - d1000
    return {
        "diagnostic_type": "non_core_exploratory_fixed_k15",
        "why_non_core": "With one fixed k, k_spread is undefined; this uses paired E_CAP gap at k=15 instead.",
        "fixed_k": FIXED_K,
        "epsilon": FIXED_K_EPSILON,
        "metric": "P(E_CAP_random(k=15,n,s)-E_CAP_geo(k=15,d,n,s)>0.5)",
        "cells_by_n": cells_by_n,
        "crossovers": cross,
        "shift_5000_minus_1000": shift,
        "left_shift_persists_under_fixed_k15": bool(shift is not None and shift < 0),
    }


def run_s_stability() -> dict[str, Any]:
    scipy_available = False
    rows = []
    try:
        from scipy import special  # type: ignore
        scipy_available = True
    except Exception as exc:  # pragma: no cover - environment dependent
        special = None
        scipy_error = repr(exc)
    else:
        scipy_error = None
    for d in [20, 50, 100, 150, 200]:
        local = EST.S(float(d))
        row = {
            "d": d,
            "continued_fraction_S": local,
            "invert_S_of_local_S": EST.invert_S(local),
        }
        if scipy_available:
            ref = float(special.betainc((d + 1.0) / 2.0, 0.5, 0.75))
            row.update({
                "scipy_special_betainc_reference": ref,
                "absolute_error": abs(local - ref),
                "relative_error": abs(local - ref) / ref if ref else 0.0,
            })
        rows.append(row)
    return {
        "scipy_available": scipy_available,
        "scipy_import_error": scipy_error,
        "rows": rows,
        "note": "invert_S uses B2.2 grid 0.5..30; large-d S values below the grid floor clamp to 30.0, but B2.3 E_CAP values remained in the observed 8..13 range.",
    }


def run_dense_scan() -> dict[str, Any]:
    cells_by_n: dict[str, list[dict[str, Any]]] = {}
    for n in N_VALUES:
        cells = []
        for d in DENSE_D:
            cells.append(B23.paired_cell(d, n, SEEDS))
            write_json(OUTPUTS / "dense_d_8_30_scan_partial.json", cells_by_n | {str(n): cells})
        cells_by_n[str(n)] = cells
    cross = {n: B23.find_crossover(cells) for n, cells in cells_by_n.items()}
    return {
        "d_range": DENSE_D,
        "metric": "paired k-spread separation, same as B2.3 core",
        "cells_by_n": cells_by_n,
        "crossovers_in_dense_range": cross,
    }


def verify_current_decision() -> dict[str, Any]:
    cmd = [sys.executable, "-m", "gate_harness.verify_decision", str(HERE / "decision.json")]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    return {"command": " ".join(cmd), "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "valid": proc.returncode == 0}


def write_report(payload: dict[str, Any]) -> None:
    fixed = payload["k_confound_fixed_k15"]
    dense = payload["dense_d_8_30_scan"]
    sstab = payload["s_function_stability"]
    lines = [
        "# B2.3 Diagnostics — Provenance, k-confound, S(d), Dense Scan",
        "",
        "## Step A — provenance fix",
        f"verify_decision valid: `{payload['step_a_verify_decision']['valid']}`",
        "",
        "## Step B — k-confound diagnostic",
        "Non-core/exploratory: fixed k=15 makes k-spread undefined, so this uses paired E_CAP gap at k=15.",
        f"d*(n=1000): `{fixed['crossovers']['1000']['smallest_d_with_metric_le_0_5']}`",
        f"d*(n=5000): `{fixed['crossovers']['5000']['smallest_d_with_metric_le_0_5']}`",
        f"shift: `{fixed['shift_5000_minus_1000']}`",
        f"left shift persists under fixed k=15: `{fixed['left_shift_persists_under_fixed_k15']}`",
        "",
        "## Step C — S(d) numerical stability",
        f"scipy available: `{sstab['scipy_available']}`",
        "| d | continued_fraction_S | scipy_reference | abs_error | rel_error | invert_S(local) |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for r in sstab["rows"]:
        lines.append(
            f"| {r['d']} | {r['continued_fraction_S']:.17g} | "
            f"{r.get('scipy_special_betainc_reference', float('nan')):.17g} | "
            f"{r.get('absolute_error', float('nan')):.3g} | "
            f"{r.get('relative_error', float('nan')):.3g} | {r['invert_S_of_local_S']} |"
        )
    lines += [
        "",
        "## Step D — dense d=8..30 scan",
        f"Dense-range crossover n=1000: `{dense['crossovers_in_dense_range']['1000']['smallest_d_with_paired_separation_le_0_5']}`",
        f"Dense-range crossover n=5000: `{dense['crossovers_in_dense_range']['5000']['smallest_d_with_paired_separation_le_0_5']}`",
        "",
        "| n | d | N | paired_separation | Wilson 95% CI | mean_margin |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for n in ["1000", "5000"]:
        for c in dense["cells_by_n"][n]:
            ci = c["paired_separation_wilson_95"]
            lines.append(f"| {n} | {c['d']} | {c['N']} | {c['paired_separation']:.3f} | [{ci['lower']:.3f}, {ci['upper']:.3f}] | {c['mean_margin_random_minus_geo']:.3f} |")
    lines += [
        "",
        "## Interpretation guard",
        "No substrate, derivability, real-world transfer, theorem-confirmation, or dimension-accuracy claim is made here.",
    ]
    (HERE / "B2_3_diagnostics_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "step_a_verify_decision": verify_current_decision(),
        "k_confound_fixed_k15": run_fixed_k_confound(),
        "s_function_stability": run_s_stability(),
        "dense_d_8_30_scan": run_dense_scan(),
    }
    write_json(OUTPUTS / "b2_3_diagnostics.json", payload)
    write_json(OUTPUTS / "k_confound_fixed_k15.json", payload["k_confound_fixed_k15"])
    write_json(OUTPUTS / "s_function_stability.json", payload["s_function_stability"])
    write_json(OUTPUTS / "dense_d_8_30_scan.json", payload["dense_d_8_30_scan"])
    write_report(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
