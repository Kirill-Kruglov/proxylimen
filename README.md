# proxylimen

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Proxy* + *limen*: a proxy at the threshold.

The internet is a proxy of a proxy: text left behind by other people's models of
the world, not the world itself. `proxylimen` asks where a learner can still
recover structure from explicit, minimal contact, and where that recovery becomes
indistinguishable from a control that has no geometry at all.

> The world cannot be derived from nothing, but it may not have to be learned
> from the shadow of the internet either. There is an intermediate regime of
> calibrated derivation: contact is minimal but explicit; rules are fixed before
> outcomes; handles are named rather than smuggled; the failure boundary is
> measured rather than hidden.

## What this is

`proxylimen` is a publishable extraction from the larger Ascesis research forge:
canonical claims, reproducible experiments, a self-checking gate harness, and an
offline visual demo. The repository is organized to separate citable results from
superseded results that the instrument itself marks non-citable.

The central artifact is not just a set of numbers. It is the split between:

- [`experiments/harness_valid/`](experiments/harness_valid/) — decisions produced
  by `gate_harness.runner.run_gate` and verified by
  `gate_harness.verify_decision`.
- [`experiments/superseded_invalid/`](experiments/superseded_invalid/) — earlier
  decisions preserved as evidence that the method found and marked the author's
  own errors. Their `decision.json` files lack `_harness_provenance`, so they are
  `INVALID` by the independent verifier. See
  [`README_SUPERSEDED.md`](experiments/superseded_invalid/README_SUPERSEDED.md).

That separation is part of the thesis: a useful research instrument should not
only report successes. It should make certain author mistakes physically hard to
cite.

## The question, made testable

The experiments do not train an LLM, use internet data, or claim semantic
grounding. They ask bounded synthetic questions:

- If observations are observer-colored, can a small amount of explicit auxiliary
  calibration recover a latent scalar in a toy world?
- Can calibrated observations recover a 2D product-order relation under known or
  evaluated dimensional structure?
- Can dimension be estimated blindly from only a kNN graph, with no coordinates,
  distances, auxiliary variables, or truth hints?
- Where does a validated graph-only dimension diagnostic stop distinguishing a
  uniform-hypercube geometry from a geometry-free random k-out control?

The allowed claim strengths are recorded in
[`canonical/RESULTS_CANONICAL.md`](canonical/RESULTS_CANONICAL.md). The README is
subordinate to that file.

## Findings, at the allowed strength

- **B1 auxiliary calibration** is a bounded toy identifiability signal, not a
  general disentanglement theorem. The harnessed rerun recovers the scalar with
  auxiliary calibration, while no-auxiliary and broken-calibration controls fail;
  however `information_ratio = 0.04697540404970473` is below the preregistered
  threshold, so `construction_may_be_tautological = true`.

- **B2 relation recovery** shows high-F1 recovery of a synthetic 2D product-order
  relation under auxiliary calibration and known/evaluated structure. It is not a
  blind discovery of order dimension: the harness records
  `classification_success_depends_on_harness_hint = true` because a 3D-control
  classification depended on the evaluation hint `truth_axes=3`.

- **B2.2.1 blind dimension estimation** recovers the Kleindessner-von Luxburg
  E_CAP table behavior from the kNN graph alone for the supported literature-table
  rows up to `d <= 7`. The `d=12` rows are boundary checks, not a claim of robust
  high-dimensional recovery.

- **B2.3 discrimination crossover** maps where the already-validated E_CAP +
  k-spread diagnostic stops separating uniform-hypercube geometry from the
  preregistered random k-out control. This is a discrimination boundary, not a
  dimension-accuracy or recovery boundary. In the recorded sweep, the discrete
  crossover is `d*=130` at `n=1000` and `d*=24` at `n=5000`.

- **Random-control mimicry** is analytically explained for the preregistered
  directed random k-out graph: the mechanism gives `L_CAP ~= 1/(k+1)`, which
  drives the recorded E_CAP k-sweep `9.40`, `11.50`, `13.10` for `k=10,15,20`.

## What is enforced vs asserted

**Enforced by the harness:**

- A citable decision must contain `_harness_provenance` written by
  `gate_harness.runner.run_gate`.
- The current `gate_harness/*.py` working-tree hash must match the recorded
  `harness_version`.
- Preregistration locks, leakage scans, tautology checks, and evaluation-oracle
  checks must be recorded as true in provenance.
- Missing provenance fails closed: the verifier reports `INVALID` regardless of
  how good the numbers look.

**Asserted only with caveats:**

- The synthetic auxiliary-variable result is not evidence of general real-world
  disentanglement.
- The B2 relation result is not blind order-dimension discovery.
- The B2.3 crossover is not a proof that more data generally hurts, and it is not
  a theorem confirmation. It is a measured discrimination boundary for the stated
  uniform-hypercube family and random k-out control.
- No result here is a substrate claim, semantic-grounding claim, LLM-safety claim,
  or transfer-to-language claim.

## Reproduction

Verify the citable decisions:

```bash
for f in experiments/harness_valid/*/decision.json; do
  PYTHONPATH=. python3 -m gate_harness.verify_decision "$f"
done
```

Expected: all five print `VALID`.

Verify that superseded decisions remain non-citable:

```bash
find experiments/superseded_invalid -name '*decision*.json' -print0 \
  | xargs -0 env PYTHONPATH=. python3 -m gate_harness.verify_decision
```

Expected: each prints `INVALID` with the missing `_harness_provenance` reason.

The harness has pytest-style tests under [`gate_harness/tests/`](gate_harness/tests/):

```bash
PYTHONPATH=. python3 -m pytest gate_harness/tests -q
```

If `pytest` is unavailable, the verifier and modules can still be import-checked
with standard Python.

## Demo

Open [`demo/blind_dimension.html`](demo/blind_dimension.html) locally in a browser.
It is a single offline HTML file: no build step, no CDN, no external data. The demo
lets a reader generate a hidden high-dimensional cube, give the machine only the
kNN graph, estimate dimension blindly, then swap the world for a random k-out
control and watch k-sweep catch the artifact.

## Repository map

- [`canonical/RESULTS_CANONICAL.md`](canonical/RESULTS_CANONICAL.md) — source of
  truth for essay claims.
- [`canonical/MEMO_B_BRANCH_HARNESS.md`](canonical/MEMO_B_BRANCH_HARNESS.md) —
  audit and harness construction memo.
- [`MANIFEST.md`](MANIFEST.md) — extraction map from Ascesis into this repository.
- [`experiments/`](experiments/) — harness-valid and superseded-invalid experiment
  artifacts.
- [`gate_harness/README.md`](gate_harness/README.md) — mechanical gate discipline
  and verifier semantics.
- [`demo/blind_dimension.html`](demo/blind_dimension.html) — interactive visual
  explanation.

## License

MIT — see [`LICENSE`](LICENSE).
