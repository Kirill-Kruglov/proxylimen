#!/usr/bin/env python3
"""Reproduce the citability split, and fail if it ever breaks.

Every decision under ``experiments/harness_valid/`` must verify VALID; every
decision under ``experiments/superseded_invalid/`` must verify INVALID (they lack
``_harness_provenance``). That split is the project's central claim — a method
that marks the author's own pre-harness errors non-citable — so it is checked on
every push, not just asserted in prose.

    python scripts/verify_all.py    # exits non-zero on any mismatch
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gate_harness.verify_decision import verify_decision  # noqa: E402

VALID_DIR = ROOT / "experiments" / "harness_valid"
SUPERSEDED_DIR = ROOT / "experiments" / "superseded_invalid"


def gate_decisions(base: Path) -> list[Path]:
    """Top-level gate decisions only (e.g. B2_3/decision.json, B0_decision.json).

    Excludes nested artifacts like outputs/verify_decision.json, which are logs,
    not gate decisions.
    """
    return sorted(p for p in base.glob("*/*.json") if "decision" in p.name.lower())


def main() -> int:
    failures: list[str] = []

    print("expect VALID  (experiments/harness_valid):")
    valid = gate_decisions(VALID_DIR)
    for p in valid:
        ok, reasons = verify_decision(p)
        print(f"  {'VALID  ' if ok else 'INVALID'}  {p.relative_to(ROOT)}")
        if not ok:
            failures.append(f"{p.relative_to(ROOT)}: expected VALID; {reasons}")

    print("\nexpect INVALID (experiments/superseded_invalid):")
    superseded = gate_decisions(SUPERSEDED_DIR)
    for p in superseded:
        ok, _ = verify_decision(p)
        print(f"  {'VALID  ' if ok else 'INVALID'}  {p.relative_to(ROOT)}")
        if ok:
            failures.append(f"{p.relative_to(ROOT)}: expected INVALID, verified VALID")

    print(f"\n{len(valid)} harness-valid, {len(superseded)} superseded checked.")
    if not valid or not superseded:
        print("FAIL: expected to find decisions in both trees")
        return 1
    if failures:
        print(f"FAIL: {len(failures)} mismatch(es):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("OK: the citability split holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
