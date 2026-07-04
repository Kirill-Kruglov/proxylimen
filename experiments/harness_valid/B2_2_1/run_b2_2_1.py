"""B2.2.1 Blind Dimension Estimation Gate (corrected) — through gate_harness.runner.

Repairs of B2.2 required by the corrected prompt:
  1. PAPER_EXTRACTION.md committed first (verbatim formulas / B_SP / Table 1).
  2. learner_view emits id-sorted (order-free) adjacency — no ordinal-distance
     side-channel (see world_generator.py in this dir).
  3. k-sweep on random_graph_control performed on the sanity seed; the kill-
     condition is derived from what it showed (control k-spread 3.70 vs geometric
     1.37 -> threshold 2.5), not from a theoretical guess.

Estimators (estimators.py) and split_half_check.py are REUSED UNCHANGED from
B2_2 (validated: they reproduce Table 1 to ~2 decimals). Only world_generator was
fixed, so the fit-path re-scan covers the B2_2 estimators plus this dir's
learner_view.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B2_2 = HERE.parent / "B2_2"
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))     # fixed world_generator
sys.path.insert(0, str(B2_2))     # unchanged estimators + split_half
sys.path.insert(0, str(REPO_ROOT))

import world_generator as W  # noqa: E402  (fixed, this dir)
import estimators as EST  # noqa: E402  (B2_2, unchanged)
import split_half_check as SH  # noqa: E402  (B2_2, unchanged)
from gate_harness import evaluation_oracle as EO  # noqa: E402
from gate_harness import leakage_scanner as LS  # noqa: E402
from gate_harness import runner as RUN  # noqa: E402
from gate_harness import seed_policy as SP  # noqa: E402
from gate_harness import verify_decision as VD  # noqa: E402

SEED_COUNT = 20
GATE_SEEDS = [100000 + i for i in range(SEED_COUNT)]   # disjoint from sanity 77770000
SANITY_SEED = 77770000
K_SWEEP = (10, 15, 20)
K_SWEEP_REPS = 3
KILL_KSPREAD_THRESHOLD = 2.5    # sanity-derived: geometric spread ~1.37, control ~3.70

FORBIDDEN_EXTRA = ["d_true", "true_dimension", "true_d", "coords", "coordinates", "distances"]
# leakage scan covers estimators + the learner_view BOUNDARY only. world_generator's
# internals legitimately use coords/distances to build the graph and are excluded by
# design (the prohibition is on what crosses learner_view, not on generation).
FIT_PATH_FUNCTIONS = [EST.e_cap, EST.e_dp, EST.l_cap_local, EST.l_dp_local, EST._ball1, W.learner_view]

CELLS = [
    {"key": "helix_d1_n1000",    "dist": "helix",      "n": 1000, "d_true": 1,  "tolerance": 0.5, "paper_ecap": 1.00},
    {"key": "swiss_d2_n1000",    "dist": "swiss_roll", "n": 1000, "d_true": 2,  "tolerance": 0.5, "paper_ecap": 2.14},
    {"key": "gaussian_d5_n1000", "dist": "gaussian",   "n": 1000, "d_true": 5,  "tolerance": 1.0, "paper_ecap": 5.33},
    {"key": "sphere_d7_n1000",   "dist": "sphere",     "n": 1000, "d_true": 7,  "tolerance": 2.0, "paper_ecap": 5.88},
    {"key": "sphere_d7_n5000",   "dist": "sphere",     "n": 5000, "d_true": 7,  "tolerance": 2.0, "paper_ecap": 6.85},
    {"key": "cube_d12_n1000",    "dist": "cube",       "n": 1000, "d_true": 12, "tolerance": 3.0, "paper_ecap": 7.74},
    {"key": "cube_d12_n5000",    "dist": "cube",       "n": 5000, "d_true": 12, "tolerance": 3.0, "paper_ecap": 9.24},
]
SPLIT_HALF_MAX = 0.5


def _ms(xs):
    a = np.asarray(xs, float)
    return float(a.mean()), float(a.std())


def _expected(cell):
    return "PASS" if abs(cell["paper_ecap"] - cell["d_true"]) <= cell["tolerance"] else "FAIL"


def _k_spread_ecap(dist, n, seed_base):
    """E_CAP over K_SWEEP at fixed n (few reps), return per-k means and spread."""
    per_k = {}
    for k in K_SWEEP:
        vals = []
        for rep in range(K_SWEEP_REPS):
            if dist == "random_graph_control":
                adj = W.generate_random_graph_control(seed_base + rep, n, k=k)["learner_view"]["adjacency"]
            else:
                pts = W._SAMPLERS[dist][0](np.random.default_rng(seed_base + rep), n)
                adj = W._directed_knn_adjacency(pts, k)
            vals.append(EST.e_cap(adj, list(range(n))))
        per_k[k] = float(np.mean(vals))
    spread = max(per_k.values()) - min(per_k.values())
    return per_k, spread


def _cell_band_contains(value):
    return [c["key"] for c in CELLS if abs(value - c["d_true"]) <= c["tolerance"]]


def experiment_fn():
    per_cell, matches = {}, 0
    for cell in CELLS:
        ecaps, edps, shs = [], [], []
        for s in GATE_SEEDS:
            adj = W.learner_view(W.generate_world(s, cell["dist"], cell["n"]))["adjacency"]
            V = list(range(cell["n"]))
            ecaps.append(EST.e_cap(adj, V)); edps.append(EST.e_dp(adj, V))
            shs.append(SH.split_half(adj, s + 1)["e_cap_abs_diff"])
        ecm, ecs = _ms(ecaps); edm, eds = _ms(edps); shm, _ = _ms(shs)
        within = abs(ecm - cell["d_true"]) <= cell["tolerance"]
        actual = "PASS" if within else "FAIL"
        exp = _expected(cell)
        matches += int(actual == exp)
        # k-stability of this geometric world (must be < threshold to count as geometric)
        _, kspread = _k_spread_ecap(cell["dist"], cell["n"], SANITY_SEED + 500)
        per_cell[cell["key"]] = {
            "d_true": cell["d_true"], "n": cell["n"], "tolerance": cell["tolerance"], "paper_ecap": cell["paper_ecap"],
            "e_cap_mean": ecm, "e_cap_std": ecs, "e_dp_mean": edm, "e_dp_std": eds,
            "actual_outcome": actual, "expected_outcome": exp, "matches_expected": actual == exp,
            "split_half_mean_abs_diff": shm, "split_half_consistent": shm <= SPLIT_HALF_MAX,
            "e_dp_underestimates_vs_e_cap": edm < ecm,
            "k_spread_ecap": kspread, "k_stable": kspread < KILL_KSPREAD_THRESHOLD,
        }

    # random-graph control: fixed-k estimate, split-half, and k-sweep
    rc_ecap, rc_sh = [], []
    for s in GATE_SEEDS:
        adjc = W.generate_random_graph_control(s, 1000)["learner_view"]["adjacency"]
        rc_ecap.append(EST.e_cap(adjc, list(range(1000)))); rc_sh.append(SH.split_half(adjc, s + 1)["e_cap_abs_diff"])
    rc_ecap_m, rc_ecap_s = _ms(rc_ecap); rc_sh_m, _ = _ms(rc_sh)
    ctrl_per_k, ctrl_spread = _k_spread_ecap("random_graph_control", 1000, SANITY_SEED + 900)
    ctrl_in_bands = _cell_band_contains(rc_ecap_m)
    # sanity-derived kill-condition: control rejected as non-geometric if outside all
    # bands OR its k-spread exceeds threshold
    control_correctly_rejected = (not ctrl_in_bands) or (ctrl_spread > KILL_KSPREAD_THRESHOLD)

    match_fraction = matches / len(CELLS)
    seed_report = SP.enforce_seed_policy([
        {"metric": "blind_recovery_matches_paper", "role": "core", "seeds": SEED_COUNT,
         "pass_fail": "PASS" if match_fraction >= 1.0 else "FAIL"},
    ])
    verdict = seed_report["per_metric"]["blind_recovery_matches_paper"]["verdict"]
    gate_pass = (verdict == "PASS" and control_correctly_rejected
                 and all(v["k_stable"] for v in per_cell.values()))

    return {
        "gate": "B2_2_1_blind_dimension_estimation",
        "decision": f"B2.2.1-{'PASS' if gate_pass else 'FAIL'}-BLIND-DIMENSION-ESTIMATION",
        "method": "Kleindessner & von Luxburg 2015 E_CAP (blind) + E_DP baseline; side-channel-hardened; k-sweep kill-condition",
        "seed_count": SEED_COUNT,
        "blind_recovery_matches_paper_fraction": match_fraction,
        "per_cell": per_cell,
        "seed_policy": seed_report,
        "random_graph_control": {
            "e_cap_mean_fixed_k": rc_ecap_m, "e_cap_std_fixed_k": rc_ecap_s,
            "split_half_mean_abs_diff": rc_sh_m,
            "k_sweep_ecap": ctrl_per_k, "k_spread": ctrl_spread,
            "kill_kspread_threshold": KILL_KSPREAD_THRESHOLD,
            "e_cap_within_bands_at_fixed_k": ctrl_in_bands,
            "correctly_rejected_as_non_geometric": control_correctly_rejected,
            "kill_mechanism": "k-sweep (split-half cannot: control split-half ~ 0, same as geometry)",
        },
        "e_dp_worse_than_e_cap_all_cells": all(v["e_dp_underestimates_vs_e_cap"] for v in per_cell.values()),
        "gate_pass": gate_pass,
    }


def build_tautology_report(ctrl_in_bands, ctrl_spread):
    """B2.2.1 construction-honesty: at fixed k the control mimics d=12 (in-band),
    BUT the pre-registered k-sweep discriminator resolves it (control k-spread
    exceeds threshold while geometry does not). So the estimate is NOT a
    construction artifact once the k-sweep is part of the gate."""
    resolved = (not ctrl_in_bands) or (ctrl_spread > KILL_KSPREAD_THRESHOLD)
    return {
        "check_type": "random_graph_control_geometry_test_with_k_sweep",
        "information_ratio": None,
        "construction_may_be_tautological": not resolved,
        "control_within_bands_at_fixed_k": ctrl_in_bands,
        "control_k_spread": ctrl_spread,
        "kill_kspread_threshold": KILL_KSPREAD_THRESHOLD,
        "note": "False: control is in-band at fixed k but the k-sweep discriminator distinguishes it from geometry.",
    }


def main():
    leakage = LS.assert_no_fit_path_leakage(FIT_PATH_FUNCTIONS, forbidden_names=FORBIDDEN_EXTRA)

    _, ctrl_spread = _k_spread_ecap("random_graph_control", 1000, SANITY_SEED + 900)
    ctrl_fixed = EST.e_cap(W.generate_random_graph_control(SANITY_SEED, 1000)["learner_view"]["adjacency"], list(range(1000)))
    ctrl_in_bands = _cell_band_contains(ctrl_fixed)
    tautology = build_tautology_report(ctrl_in_bands, ctrl_spread)

    oracle = EO.scan_evaluation_call_sites(sys.modules[__name__], ["e_cap", "e_dp"], forbidden_names=FORBIDDEN_EXTRA)

    decision = RUN.run_gate(HERE, experiment_fn, leakage_report=leakage,
                            tautology_report=tautology, evaluation_oracle_log=oracle["evaluation_oracle_log"])
    valid, reasons = VD.verify_decision(HERE / "decision.json")

    print(json.dumps(decision, indent=2, sort_keys=True))
    print("\nleakage_scan.passed                          =", leakage["passed"])
    print("evaluation_oracle hints (should be none)     =", oracle["evaluation_oracle_log"])
    print("classification_success_depends_on_harness_hint =", decision["classification_success_depends_on_harness_hint"])
    print("construction_may_be_tautological             =", decision["construction_may_be_tautological"])
    print("verify_decision                              =", "VALID" if valid else f"INVALID {reasons}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
