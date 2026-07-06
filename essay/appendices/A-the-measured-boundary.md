# Appendix A — The Measured Boundary

This appendix carries the technical weight behind Part IV of the essay: exact
definitions, the validated regime, the control family and its mechanism, the
crossover tables with confidence intervals, the fixed-k caveat, and the stated
limits of the claim. Every number below is copied from a committed repository
artifact; [`canonical/RESULTS_CANONICAL.md`](../../canonical/RESULTS_CANONICAL.md)
is the registry that binds each value to its source file and commit, and no
statement here is permitted to be stronger than what that registry records.

---

## A.1 The estimator

The blind dimension estimator is **E_CAP** from Kleindessner & von Luxburg
(AISTATS 2015), reconstructed in
[`experiments/harness_valid/B2_2_1/PAPER_EXTRACTION.md`](../../experiments/harness_valid/B2_2_1/PAPER_EXTRACTION.md)
directly from the paper's PDF. Given only a directed kNN graph (an edge `i → j`
iff `x_j` is among the `k` nearest samples to `x_i`):

- `B_SP(i, 1)` is the radius-1 ball around vertex `i` in shortest-path distance —
  the vertex plus its `k` out-neighbors, so `|B_SP(i,1)| = k + 1` always.
- `L_CAP(i) = min_{j : i→j} |B_SP(i,1) ∩ B_SP(j,1)| / (k+1)` — the smallest
  normalized overlap between `i`'s ball and a neighbor's ball.
- In continuous space, the relative volume of the lens where two unit balls at
  unit distance overlap is `S(d) = I_{3/4}((d+1)/2, 1/2)` (regularized incomplete
  beta function), which depends injectively on `d`.
- The estimate is `E_CAP = S⁻¹(mean L_CAP)`: measure the overlap in the graph,
  invert the geometry that would have produced it.

The intuition in one line: **in low dimension, near-neighbors share most of their
neighborhoods; as dimension grows, that shared overlap dies away at a rate that
encodes the dimension.**

## A.2 What "blind" means, operationally

The learner path receives the kNN graph and nothing else. This is not a promise;
it is enforced and recorded:

- The fit path is AST-scanned for forbidden truth-names (coordinates, distances,
  generator labels, `truth_axes`, …) — the scan is static analysis of the code,
  not self-report.
- The evaluation-oracle scan checks that no ground-truth hint enters the
  evaluation call sites. The B2.2.1 decision records
  `classification_success_depends_on_harness_hint: false`
  ([`B2_2_1/decision.json`](../../experiments/harness_valid/B2_2_1/decision.json)).
- The predecessor experiment B2.1 is the honest contrast: there the 3D-control
  classification *did* depend on a harness-provided hint (`truth_axes=3`), the
  harness flagged it, and the canonical registry forbids citing it as blind
  discovery. The flag existing — and firing on my own earlier result — is what
  makes the B2.2.1 "false" meaningful.
- One interface wart, surfaced by an external read of this repository: the world
  generator's `learner_view` also exposes a `seed_id` alongside the adjacency.
  The estimator path never reads it — enforced in CI by an AST scan of every
  estimator function with the harness's own leakage scanner
  ([`scripts/check_learner_view_hygiene.py`](../../scripts/check_learner_view_hygiene.py))
  — but a stricter interface would not have exposed it at all. The signed run's
  code is preserved as it ran; the check, not a retroactive edit, carries the
  claim.

## A.3 The validated regime

B2.2.1 reproduces the paper's dimension-table behavior from the graph alone,
across 20 seeds, with every cell's expected outcome preregistered — including the
expected *failure*. From `B2_2_1/decision.json` (key `per_cell`):

| cell | d_true | n | E_CAP mean | paper E_CAP | outcome | expected |
|---|---:|---:|---:|---:|---|---|
| helix | 1 | 1000 | 1.00 | 1.00 | PASS | PASS |
| swiss roll | 2 | 1000 | 2.16 | 2.14 | PASS | PASS |
| gaussian | 5 | 1000 | 5.33 | 5.33 | PASS | PASS |
| sphere | 7 | 1000 | 5.88 | 5.88 | PASS | PASS |
| sphere | 7 | 5000 | 6.86 | 6.85 | PASS | PASS |
| cube | 12 | 1000 | 7.74 | 7.74 | **FAIL** | **FAIL** |
| cube | 12 | 5000 | 9.24 | 9.24 | PASS | PASS |

The `d=12, n=1000` failure is the estimator faltering exactly where its own
literature predicts, preregistered as a failure before the run. The competing
estimator E_DP was worse than E_CAP in every cell
(`e_dp_worse_than_e_cap_all_cells: true`). The supported claim is bounded:
literature-table rows up to `d ≤ 7`, with `d = 12` as boundary checks.

## A.4 The control family, and why it fools the estimator

The preregistered null is a **directed random k-out graph**: each vertex draws `k`
out-neighbors uniformly at random — no geometry at all. Its mimicry of
high-dimensional geometry is not a mystery; it is derived and verified in
[`B2_3/outputs/random_control_mechanism.json`](../../experiments/harness_valid/B2_3/outputs/random_control_mechanism.json):

For an edge `i → j`, the balls always share at least `j` itself; with high
probability the minimum over out-neighbors is *exactly* that one forced vertex,
giving `L_CAP ≈ 1/(k+1)` — which E_CAP reads as a spuriously high dimension that
**depends on k**:

| k | predicted E_CAP (if min overlap = 1) | empirical E_CAP (n=1000) |
|---:|---:|---:|
| 10 | 9.4 | 9.4 |
| 15 | 11.5 | 11.5 |
| 20 | 13.1 | 13.1 |

That k-dependence is also the tell. Real geometry's estimate moves only mildly
under a k-sweep; the random graph's estimate tracks `k` itself. The preregistered
discriminator is **k-spread** — the range of estimates across `k ∈ {10, 15, 20}` —
with a kill threshold of `2.5`. The random control's k-spread is `3.70`
(`B2_2_1/decision.json`, key `random_graph_control`); the geometric worlds in the
validated regime stay well under it (per-cell spreads `0.20`–`2.03` in A.3).

## A.5 The crossover

B2.3 asks where paired discrimination (geometric world vs. random control, same
`n`, same pipeline) collapses as `d` grows. From
[`B2_3/decision.json`](../../experiments/harness_valid/B2_3/decision.json) and
[`outputs/crossover_results.json`](../../experiments/harness_valid/B2_3/outputs/crossover_results.json):

| n | d\* (first d with paired separation ≤ 0.5) | interpolated d at 0.5 | monotone non-increasing |
|---:|---:|---:|---|
| 1000 | **130** | 129.83 | true |
| 5000 | **24** | 23.13 | true |

Selected cells with Wilson 95% intervals (N = 50 paired runs per cell):

| n | d | paired separation | Wilson 95% CI |
|---:|---:|---:|---|
| 1000 | 129 | 0.60 | [0.46, 0.72] |
| 1000 | 130 | 0.48 | [0.35, 0.61] |
| 1000 | 131 | 0.48 | [0.35, 0.61] |
| 5000 | 24 | 0.36 | [0.24, 0.50] |
| 5000 | 25 | 0.04 | [0.01, 0.13] |
| 5000 | 26 | 0.00 | [0.00, 0.07] |

Five times the data, and the discrimination boundary of this test moved from
`d ≈ 130` down to `d ≈ 24`. That is the essay's "more data made things worse" —
scoped, as it must be, to *this diagnostic against this control*.

## A.6 The mechanism diagnostic

Two candidate explanations were compared at the two crossover points
([`outputs/local_knn_mechanism_results.json`](../../experiments/harness_valid/B2_3/outputs/local_knn_mechanism_results.json)):

| metric at crossover | n=1000, d=130 | n=5000, d=24 | ratio |
|---|---:|---:|---:|
| global pairwise distance CV | 0.0518 | 0.1226 | 2.36 |
| edge-pair shared-neighbor P(>1), k=15 | 0.807 | 0.861 | **1.07** |

The generic story ("distances concentrate in high dimension") does not unify the
two collapse points — its value differs by 2.4× between them. The local story
does: the probability that an actual *edge* of the graph carries shared structure
beyond the single forced overlap is nearly identical (≈0.8) at both crossovers.
The estimator dies when its edges run out of surplus local overlap — when *near*
stops meaning *geometry* and starts meaning *echo*.

## A.7 The fixed-k caveat (load-bearing)

An exploratory diagnostic held `k = 15` fixed instead of sweeping it
([`outputs/b2_3_diagnostics.json`](../../experiments/harness_valid/B2_3/outputs/b2_3_diagnostics.json),
key `k_confound_fixed_k15`): under a fixed-k paired E_CAP gap, `n = 1000` showed
**no crossover through `d = 200`**, while `n = 5000` crossed at `d = 38`.

So the inward shift of the boundary is established for the preregistered
k-spread diagnostic; it is **not** established as stable under fixed k. The
canonical registry states this must not be claimed otherwise, and the essay's
Part IV points here. The honest mechanism statement is correspondingly weaker:
local edge-conditioned overlap aligns the two observed core crossover points
better than the global explanation does — no more than that.

## A.8 What this licenses, and what it does not

Verbatim scope warning from `B2_3/decision.json`:

> This result rejects tautology only with respect to the preregistered random
> k-out graph control. It does not establish that the estimator cannot be fooled
> by other non-geometric graph families.

Explicitly untested (`not_tested_against`): small-world graphs, scale-free
graphs, other non-Euclidean structured graphs.

And the limits that matter for the essay's argument:

- **No information-theoretic lower bound was proven.** Nothing here shows the
  geometric/random distinction has left the data past the crossover — only that
  this validated channel stops extracting it. A different statistic might
  separate these families farther out.
- **The boundary is a property of the ensemble** — world family, observation
  model (kNN graph), diagnostic (E_CAP + k-spread), control family, and decision
  rule together — not a demonstrated property of "contact" in the abstract.
- **All of it is one forge.** Designer, experimenter, and interpreter are the
  same author with the same AI partners; the harness makes self-deception harder,
  not impossible. Independent replication is invited and would outweigh any
  further internal check.

## A.9 External references

- M. Kleindessner, U. von Luxburg. *Dimensionality estimation without distances.*
  AISTATS 2015, PMLR vol. 38, pp. 471–479.
  [proceedings.mlr.press/v38/kleindessner15.html](https://proceedings.mlr.press/v38/kleindessner15.html)
- F. Locatello, S. Bauer, M. Lucic, G. Rätsch, S. Gelly, B. Schölkopf,
  O. Bachem. *Challenging Common Assumptions in the Unsupervised Learning of
  Disentangled Representations.* ICML 2019, PMLR vol. 97, pp. 4114–4124.
  [proceedings.mlr.press/v97/locatello19a.html](https://proceedings.mlr.press/v97/locatello19a.html)
  — the identifiability theorem referenced in Part II.
- M. Yannakakis. *The complexity of the partial order dimension problem.*
  SIAM Journal on Algebraic and Discrete Methods, 3(3):351–358, 1982.
  [doi:10.1137/0603036](https://doi.org/10.1137/0603036) — the anchor for the
  essay's "computational wall": already deciding whether a partial order has
  dimension at most three is NP-complete.

## A.10 Where every number lives

Every value above appears in
[`canonical/RESULTS_CANONICAL.md`](../../canonical/RESULTS_CANONICAL.md) with the
source file, JSON key, and commit hash recorded next to it. The decisions that
carry these numbers are harness-signed; `gate_harness.verify_decision` accepts
all five under `experiments/harness_valid/` and rejects every superseded
pre-harness decision — which you can re-run yourself from the repository root:

```bash
for f in experiments/harness_valid/*/decision.json; do
  PYTHONPATH=. python3 -m gate_harness.verify_decision "$f"
done
```
