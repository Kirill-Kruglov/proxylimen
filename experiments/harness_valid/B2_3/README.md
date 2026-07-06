# B2.3 — Discrimination Crossover Mapping

Bounded continuation of B2.2.1.

This gate maps where the already-validated E_CAP + k-spread discrimination
diagnostic stops separating uniform-hypercube geometry from the preregistered
geometry-free random k-out graph control.

It does not test dimension-estimation accuracy for dimensions absent from the
paper extraction table. It tests only random-control discrimination under the
uniform hypercube family.

Run from repository root (paths updated for the extracted proxylimen layout;
in the ascesis forge this gate lived under `gate_harness_experiments/B2_3/`):

```bash
python3 experiments/harness_valid/B2_3/run_b2_3.py
python3 -m json.tool experiments/harness_valid/B2_3/decision.json >/dev/null
python3 -m gate_harness.verify_decision experiments/harness_valid/B2_3/decision.json
```

