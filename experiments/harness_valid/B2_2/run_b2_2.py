"""B2.2 Blind Dimension Estimation Gate — run through gate_harness.runner.

Closes the finding-#6 gap from B2.1: there, dimension classification depended on a
harness-provided truth_axes hint. Here the estimator (Kleindessner & von Luxburg
2015, E_CAP) sees ONLY the kNN adjacency — no coordinates, distances, or d_true —
so classification_success_depends_on_harness_hint must come out False.

Config (best-judgment, Option A — every tolerance is a literal Table 1 number):
worlds = the paper's exact artificial datasets; d=3 dropped (no Table 1 cell).
See PREREG.json for sources. This was chosen while the operator was away; it is
re-runnable under Option B/C if desired.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

import estimators as EST  # noqa: E402
import split_half_check as SH  # noqa: E402
import world_generator as W  # noqa: E402
from gate_harness import evaluation_oracle as EO  # noqa: E402
from gate_harness import leakage_scanner as LS  # noqa: E402
from gate_harness import runner as RUN  # noqa: E402
from gate_harness import seed_policy as SP  # noqa: E402
from gate_harness import verify_decision as VD  # noqa: E402

SEED_COUNT = 20
GATE_SEEDS = [100000 + i for i in range(SEED_COUNT)]   # disjoint from sanity 77770000 / validation 9000x
SANITY_SEED = 77770000

FORBIDDEN_EXTRA = ["d_true", "true_dimension", "true_d", "coords", "coordinates", "distances"]
FIT_PATH_FUNCTIONS = [EST.e_cap, EST.e_dp, EST.l_cap_local, EST.l_dp_local, EST._ball1, W.learner_view]

# Pre-registered cells. tolerance and expected_outcome are derived from the paper's
# Table 1 E_CAP numbers (paper_ecap), NOT from our runs.
CELLS = [
    {"key": "helix_d1_n1000",      "dist": "helix",      "n": 1000, "d_true": 1,  "tolerance": 0.5, "paper_ecap": 1.00},
    {"key": "swiss_d2_n1000",      "dist": "swiss_roll", "n": 1000, "d_true": 2,  "tolerance": 0.5, "paper_ecap": 2.14},
    {"key": "gaussian_d5_n1000",   "dist": "gaussian",   "n": 1000, "d_true": 5,  "tolerance": 1.0, "paper_ecap": 5.33},
    {"key": "sphere_d7_n1000",     "dist": "sphere",     "n": 1000, "d_true": 7,  "tolerance": 2.0, "paper_ecap": 5.88},
    {"key": "sphere_d7_n5000",     "dist": "sphere",     "n": 5000, "d_true": 7,  "tolerance": 2.0, "paper_ecap": 6.85},
    {"key": "cube_d12_n1000",      "dist": "cube",       "n": 1000, "d_true": 12, "tolerance": 3.0, "paper_ecap": 7.74},
    {"key": "cube_d12_n5000",      "dist": "cube",       "n": 5000, "d_true": 12, "tolerance": 3.0, "paper_ecap": 9.24},
]
SPLIT_HALF_MAX = 0.5           # geometric-world consistency threshold (pre-run reasonable choice)
RANDOM_CONTROL_KILL_MIN = 0.5  # control EXPECTED to exceed this; if not -> recorded finding


def _expected_outcome(cell):
    return "PASS" if abs(cell["paper_ecap"] - cell["d_true"]) <= cell["tolerance"] else "FAIL"


def _mean_std(xs):
    a = np.asarray(xs, dtype=float)
    return float(a.mean()), float(a.std())


def experiment_fn():
    per_cell = {}
    matches = 0
    for cell in CELLS:
        ecaps, edps, sh_diffs = [], [], []
        for s in GATE_SEEDS:
            w = W.generate_world(s, cell["dist"], cell["n"])
            adj = W.learner_view(w)["adjacency"]
            V = list(range(cell["n"]))
            ecaps.append(EST.e_cap(adj, V))
            edps.append(EST.e_dp(adj, V))
            sh_diffs.append(SH.split_half(adj, s + 1)["e_cap_abs_diff"])
        ecap_m, ecap_s = _mean_std(ecaps)
        edp_m, edp_s = _mean_std(edps)
        sh_m, _ = _mean_std(sh_diffs)
        within = abs(ecap_m - cell["d_true"]) <= cell["tolerance"]
        actual = "PASS" if within else "FAIL"
        expected = _expected_outcome(cell)
        ok = actual == expected
        matches += int(ok)
        per_cell[cell["key"]] = {
            "d_true": cell["d_true"], "n": cell["n"], "tolerance": cell["tolerance"],
            "e_cap_mean": ecap_m, "e_cap_std": ecap_s, "e_dp_mean": edp_m, "e_dp_std": edp_s,
            "paper_ecap": cell["paper_ecap"], "e_cap_within_tolerance": within,
            "actual_outcome": actual, "expected_outcome": expected, "matches_expected": ok,
            "split_half_mean_abs_diff": sh_m, "split_half_consistent": sh_m <= SPLIT_HALF_MAX,
            "e_dp_underestimates_vs_e_cap": edp_m < ecap_m,
        }

    # random-graph control (geometry-free) over the same seeds
    rc_ecap, rc_sh = [], []
    for s in GATE_SEEDS:
        rc = W.generate_random_graph_control(s, 1000)
        adjc = rc["learner_view"]["adjacency"]
        rc_ecap.append(EST.e_cap(adjc, list(range(1000))))
        rc_sh.append(SH.split_half(adjc, s + 1)["e_cap_abs_diff"])
    rc_ecap_m, rc_ecap_s = _mean_std(rc_ecap)
    rc_sh_m, _ = _mean_std(rc_sh)
    control_exceeds_kill = rc_sh_m > RANDOM_CONTROL_KILL_MIN
    # does the geometry-free control land inside any tested tolerance band?
    control_indistinguishable = [
        c["key"] for c in CELLS if abs(rc_ecap_m - c["d_true"]) <= c["tolerance"]
    ]

    match_fraction = matches / len(CELLS)
    seed_report = SP.enforce_seed_policy([
        {"metric": "blind_recovery_matches_paper", "role": "core", "seeds": SEED_COUNT,
         "pass_fail": "PASS" if match_fraction >= 1.0 else "FAIL"},
    ])
    verdict = seed_report["per_metric"]["blind_recovery_matches_paper"]["verdict"]

    return {
        "gate": "B2_2_blind_dimension_estimation",
        "decision": f"B2.2-{verdict}-BLIND-DIMENSION-ESTIMATION",
        "method": "Kleindessner & von Luxburg 2015 E_CAP (blind), E_DP baseline",
        "seed_count": SEED_COUNT,
        "blind_recovery_matches_paper_fraction": match_fraction,
        "per_cell": per_cell,
        "seed_policy": seed_report,
        "random_graph_control": {
            "e_cap_mean": rc_ecap_m, "e_cap_std": rc_ecap_s,
            "split_half_mean_abs_diff": rc_sh_m,
            "kill_threshold_min": RANDOM_CONTROL_KILL_MIN,
            "control_exceeded_kill_threshold": control_exceeds_kill,
            "control_within_tolerance_of_cells": control_indistinguishable,
            "finding": (
                "split-half consistency does NOT distinguish geometry: the geometry-free "
                "control is itself consistent and its E_CAP falls within the tolerance of "
                + (", ".join(control_indistinguishable) if control_indistinguishable else "no cell")
            ),
        },
        "e_dp_worse_than_e_cap_all_cells": all(v["e_dp_underestimates_vs_e_cap"] for v in per_cell.values()),
    }


def build_tautology_report(rc_ecap_mean, control_indistinguishable):
    """B2.2 substitute for the variance-ratio tautology check: if a geometry-free
    random graph produces an E_CAP inside a tested tolerance band, that cell's
    'estimate' is not distinguishable from a construction artifact."""
    return {
        "check_type": "random_graph_control_geometry_test",
        "information_ratio": None,
        "construction_may_be_tautological": bool(control_indistinguishable),
        "random_control_e_cap_mean": rc_ecap_mean,
        "cells_indistinguishable_from_control": control_indistinguishable,
        "note": "True means at least one dimension cell cannot be distinguished from a geometry-free random k-regular graph.",
    }


def main():
    # leakage scan (fit path must be blind) with the experiment's extra forbidden names
    leakage = LS.assert_no_fit_path_leakage(FIT_PATH_FUNCTIONS, forbidden_names=FORBIDDEN_EXTRA)

    # pre-compute the random control once to build the tautology report
    rc = W.generate_random_graph_control(SANITY_SEED, 1000)
    adjc = rc["learner_view"]["adjacency"]
    rc_ecap_mean = EST.e_cap(adjc, list(range(1000)))
    control_indist = [c["key"] for c in CELLS if abs(rc_ecap_mean - c["d_true"]) <= c["tolerance"]]
    tautology = build_tautology_report(rc_ecap_mean, control_indist)

    # evaluation-oracle: confirm no ground-truth hint reaches the estimators
    oracle = EO.scan_evaluation_call_sites(sys.modules[__name__], ["e_cap", "e_dp"], forbidden_names=FORBIDDEN_EXTRA)

    decision = RUN.run_gate(
        HERE, experiment_fn,
        leakage_report=leakage, tautology_report=tautology,
        evaluation_oracle_log=oracle["evaluation_oracle_log"],
    )
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
