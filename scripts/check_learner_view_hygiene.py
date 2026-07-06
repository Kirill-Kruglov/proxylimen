#!/usr/bin/env python3
"""Prove the estimator path never reads `seed_id` — with the harness's own knife.

An external review of this repository found an interface wart: the B2.2.1 world
generator's ``learner_view`` exposes ``seed_id`` alongside the adjacency. The
signed decision was produced under that interface, so the interface is preserved
as-is (retroactively editing the code a signed run used would falsify the record).
Instead, this check enforces the claim that actually matters: no function in the
estimator fit path references ``seed_id`` (or any other truth name) — using
``gate_harness.leakage_scanner``'s AST scan, not self-report.

    python scripts/check_learner_view_hygiene.py    # exits non-zero on any hit

Run by CI after ``scripts/verify_all.py``.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "harness_valid" / "B2_2"))

import estimators  # noqa: E402  (the B2.2/B2.2.1/B2.3 estimator fit path)
from gate_harness import leakage_scanner as LS  # noqa: E402

FORBIDDEN = frozenset({"seed_id"})  # extends BASE_FORBIDDEN_NAMES, never replaces it


def estimator_functions():
    return [
        fn for name, fn in vars(estimators).items()
        if inspect.isfunction(fn) and fn.__module__ == estimators.__name__
    ]


def main() -> int:
    fns = estimator_functions()
    if not fns:
        print("FAIL: no estimator functions found to scan")
        return 1
    report = LS.scan_fit_path(fns, forbidden_names=FORBIDDEN)
    print(f"scanned {len(fns)} estimator function(s): "
          + ", ".join(sorted(f.__name__ for f in fns)))
    if report["passed"]:
        print("OK: estimator fit path references no forbidden name "
              "(seed_id included). The learner_view wart stays inert.")
        return 0
    print("FAIL: forbidden name referenced in the estimator fit path:")
    for hit in report.get("leak_hits", []):
        print(f"  - {hit}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
