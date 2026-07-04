# MEMO — B-branch falsification audit & gate_harness enforcement

Factual registry. Every number is copied from a named file (path + git commit
where applicable). No rounding, no interpretation. Compiled 2026-07-02.

Branch: `gate-harness`. Harness version hash (all runs below):
`53b59235a56aba8feeacf71df8d4691e9e3814309a0c37c35c1e22ee50cbcb9f`
[source: `experiments/B/B1_harness_rerun/decision.json` and
`experiments/B/B2_harness_rerun/decision.json`, key `_harness_provenance.harness_version`].

---

## 1. What the audit found

Ten findings from the independent falsification audit of B1/B1.1/B2/B2.1
(audit report produced in-session 2026-07-02; not a committed file). Severity
table reproduced as issued, unchanged:

| # | Finding | Severity |
|---|---|---|
| 1 | Prereg + code + results in one atomic commit in every gate → pre-registration undecidable from git | CRITICAL |
| 2 | B2.1 `classify_order_proxy` thresholds introduced in the same commit as the 3D-control result they fit; no prereg file | CRITICAL |
| 3 | `leakage_audit`/`variant_oracle_audit` fields mostly hardcoded constants; B2 `static_audit` PASSed while a live `variant`→classifier leak existed | CRITICAL |
| 4 | `variant_oracle_audit.run_b2_passes_variant_to_classifier` hardcoded `False`, no call-site inspection | MODERATE |
| 5 | No-aux failure tautological by construction (`bias = −group_center`) | MODERATE |
| 6 | 3D under-dimensioning "detection" evaluation-driven via `truth_axes=3` | MODERATE |
| 7 | B2 "sparse" anchors carry more records (216) than "complete" (144) | MODERATE |
| 8 | Core B2/B2.1 metrics (classification + controls) computed on 1 seed | MODERATE |
| 9 | Thresholds loosened B1→B1.1 (0.30→0.35, 0.60→0.55, 0.90→0.85) with no justification | MINOR |
| 10 | B1 primary run used a single seed | MINOR |

---

## 2. What was built (`gate_harness/`)

| Module | Fixes | Mechanical action |
|---|---|---|
| `prereg.py` [commit c38851b] | #1, #2, #9 | Writes `PREREG.json`+`PREREG.lock` (SHA256+git-rev); `verify_prereg_lock` runs `git merge-base --is-ancestor` to require lock-rev be a strict ancestor of HEAD; raises if a threshold shared with the previous gate changed value and no rationale key is present |
| `hooks/pre-commit` [commit 48df193] | #1, #2 | On `git diff --cached`, rejects a commit staging a gate's `PREREG.*` together with that gate's `outputs/`; rejects a staged `PREREG.json` whose SHA256 ≠ the SHA in committed `PREREG.lock` |
| `leakage_scanner.py` [commit cb1dd78] | #3, #4 | `ast.walk` over each fit-path function: flags forbidden names as parameters, `ast.Name`, `ast.Attribute`, `ast.Constant` string values (dict keys), closures, referenced globals; `scan_audit_report_integrity` marks return-dict fields whose value is `ast.Constant` as `NOT_VERIFIABLE` |
| `calibration_audit.py` [commit f69ff3c] | #7 | Computes `len(anchor)/len(non_anchor)`; raises if > `max_anchor_fraction`; raises if `len(sparse) >= len(complete)` |
| `seed_policy.py` [commit 2e3f0b8] | #8 | For `role:"core"` metrics returns `INSUFFICIENT_SEEDS` when `seeds < MIN_SEEDS_FOR_CORE_METRIC` (=20) |
| `tautology_check.py` [commit 18fd674] | #5 | Computes `information_ratio = var(y)/var(z)` before any learner; raises if `information_ratio_min` absent; sets `construction_may_be_tautological` = (ratio < threshold); runs k-means(k=groups) and BIC-selected 1D GMM baselines |
| `runner.py` [commit 18cbae8, extended f2d89c4] | #1, #2, #5, #6 | Calls `verify_prereg_lock`, requires passing leakage report and tautology report, folds harness-only flags into the payload, writes `decision.json` with `_harness_provenance` |
| `verify_decision.py` [commit f2d89c4] | §1.7 | Returns INVALID if `_harness_provenance` absent, `harness_version` ≠ current `sha256(gate_harness/*.py)`, `written_by` ≠ `gate_harness.runner.run_gate`, or any required flag ≠ `True` |
| `evaluation_oracle.py` [commit 3d0c3ee] | #6 | `ast.walk` the module; at each call to a declared evaluation entrypoint, flags forbidden names passed as `ast.keyword` args or `ast.Dict` literal keys; marks `ast.Constant` values `hint_value_is_literal_constant: true` |

---

## 3. Adversarial tests (`gate_harness/tests/test_adversarial.py`)

RED = failing before the defense existed; "shown" = the failing run appears in
this session's dialog. Numbering follows the finding comments in the test file.

| # | Test | Reproduces | Shown RED before defense? | GREEN after (commit) |
|---|---|---|---|---|
| 1 | `test_catches_variant_branching_classifier` | #3 (`variant` branch) | No — defense (leakage_scanner) built same turn; GREEN on first adversarial run | 287b890 |
| 2 | `test_rejects_hardcoded_audit_fields` | #3 (hardcoded audit) | Yes — RED in the "3/7 GREEN" run | 287b890 |
| 3 | `test_precommit_blocks_prereg_and_outputs_together` | #1 | No — GREEN on first adversarial run | 287b890 |
| 4 | `test_precommit_blocks_locked_prereg_edit` | #2 | No — GREEN on first adversarial run | 287b890 |
| 5 | `test_tautology_check_flags_negated_bias_construction` | #5 | Yes — RED in the "3/7 GREEN" run | 287b890 |
| 6 | `test_calibration_audit_rejects_oversized_sparse_anchor_set` | #7 | Yes — RED in the "3/7 GREEN" run | 287b890 |
| 7 | `test_runner_refuses_without_valid_lock` | #1 | Yes — RED in the "3/7 GREEN" run | 287b890 |
| 8 | `test_verify_decision_rejects_missing_provenance` | §1.7 | No — GREEN on first run ("8/9 GREEN"); verifier built just prior | f2d89c4 |
| 9 | `test_evaluation_oracle_flags_literal_truth_hint` | #6 | Yes — RED (`ImportError`) in the "8/9 GREEN" run | 3d0c3ee |

Current status of all suites (this session):
`test_prereg` 2/2, `test_leakage_scanner` 7/7, `test_adversarial` 9/9.

---

## 4. Integration runs

`verify_decision` INVALID reason string (verbatim, `gate_harness/verify_decision.py:62`):
"no _harness_provenance block — decision was not produced by the runner and is
INVALID unconditionally, regardless of its numbers".

### 4A. B1 — auxiliary-variable identifiability

**Old** [`experiments/B/B1_auxiliary_variable_identifiability_gate/B1_decision.json`, added commit 9f38a14]
- verdict: `B1-PASS-AUXILIARY-IDENTIFIABILITY-SIGNAL` [key `decision`]
- seeds: no `seed_count` / `seeds` key present in file
- `construction_may_be_tautological`: field absent
- `_harness_provenance`: field absent
- `verify_decision`: INVALID — reason above

**New** [`experiments/B/B1_harness_rerun/decision.json`, added commit 8ccefba; prereg commit 93456a6]
- verdict: `B1-PASS-AUXILIARY-IDENTIFIABILITY` [key `decision`]
- `seed_count`: 24; `seed_policy.per_metric.recovery_pearson_corr.verdict`: `PASS`; `min_required`: 20
- `mean_no_aux_abs_corr`: 0.20851995111223512; `mean_with_aux_corr`: 0.9999661041760123; `mean_improvement`: 0.791446153063777
- `information_ratio`: 0.04697540404970473; `construction_may_be_tautological`: true
- `classification_success_depends_on_harness_hint`: false
- `verify_decision`: VALID

Plain language: the auxiliary-calibration scalar recovery held at 24 seeds
(`mean_with_aux_corr` 0.9999661041760123 vs `no_aux_abs_corr_max` 0.3). The world
construction makes `y` carry `information_ratio` 0.04697540404970473 of `var(z)`,
below `information_ratio_min` 0.5, so the no-auxiliary failure is flagged as
possibly an artifact of construction; the original decision omitted this field.

### 4B. B2.1 — label-free order-dimension

**Old** [`experiments/B/B2_relational_order_dimension_recovery/B2_1_decision.json`, added commit 3d454ba]
- verdict: `B2.1-PASS-LABEL-FREE-DIMENSION-PROXY-REPAIRED` [key `decision`]
- seeds: no `seed_count` / `seeds` key present in file
- `classification_success_depends_on_harness_hint`: field absent
- `_harness_provenance`: field absent
- `verify_decision`: INVALID — reason above

**New** [`experiments/B/B2_harness_rerun/decision.json`, added commit c129bd0; prereg commit bd331cd]
- verdict: `B2.1-PASS-LABEL-FREE-ORDER-DIMENSION` [key `decision`]
- `seed_count`: 24; both `seed_policy.per_metric.*.verdict`: `PASS`; `min_required`: 20
- `recovery_pass_fraction`: 1.0; `order_dimension_pass_fraction`: 1.0; `controls_pass_fraction`: 1.0
- `mean_no_aux_f1`: 0.5118956978113977; `mean_with_aux_f1`: 0.9969994875628853; `mean_sparse_f1`: 0.9965407969143273
- `information_ratio`: 0.8915238326640017; `construction_may_be_tautological`: false
- `classification_success_depends_on_harness_hint`: true; `affected_metrics`: ["truth_axes"]
- `harness_hint_warnings` (verbatim, ×2 in file): "classification success on this control depended on harness-provided ground-truth hint (truth_axes=3); this is NOT evidence of unsupervised recovery."
- leakage scan clean (`_harness_provenance.leakage_scan_verified`: true)
- `verify_decision`: VALID

Plain language: the classifier takes no generator label and passed all 24 seeds
(`order_dimension_pass_fraction` 1.0), and cross-observer relation recovery held
(`mean_with_aux_f1` 0.9969994875628853). The 3D-control UNDERDIMENSIONED verdict
was scored against 3D truth supplied by a literal `truth_axes=3` at the evaluation
call site, so `classification_success_depends_on_harness_hint` is true: the
classifier never discovers the dimensionality from data.

---

## 5. Anchor-graph repair (finding #7)

Change: `anchor_specs` sparse/disconnected edges use `SPARSE_ANCHOR_POINTS`
(4 corners) instead of the 36-point grid
[diff commit bd331cd; `experiments/B/B2_harness_rerun/relational_order_toy_fixed.py`].

| mode | records before | fraction before | records after | fraction after |
|---|---|---|---|---|
| complete | 144 | 144/240 = 0.600 | 144 | 0.600 |
| sparse | 216 | 216/240 = 0.900 | 24 | 0.100 |
| disconnected | 144 | 144/240 = 0.600 | 16 | 0.067 |

Sources: before-numbers (216, 144) from the code comment in
`relational_order_toy_fixed.py` ("Original code reused `grid` here -> 108 items /
216 records, heavier than complete (144)"); after-numbers from
`decision.json` key `anchor_fraction_sparse` = 0.1 and `PREREG.json`
`metadata.anchor_graph` = "finding-#7-fixed: sparse=24 records (frac 0.100) vs
complete=144"; non-anchor denominator 240 = `ITEMS_PER_OBSERVER`(60) ×
`len(OBSERVERS)`(4) [`relational_order_toy_fixed.py`].

---

## 6. Sanity-seed protocol

A single seed run before the final multi-seed run to confirm the pipeline
end-to-end (recovery, classification, controls, information_ratio, oracle) without
tuning thresholds to the evaluation data.

- sanity seed: 88880000 [source: `experiments/B/B2_harness_rerun/PREREG.json`,
  `metadata.sanity_seed_disjoint` = 88880000]
- final seeds: 20260702 .. 20260932 (24 values, `SEED_START + 10*i`) [source:
  `experiments/B/B2_harness_rerun/decision.json`, key `final_seeds`]
- 88880000 is NOT a member of `final_seeds` (verified programmatically against the
  `final_seeds` list in `decision.json`).

---

## 7. Two results that must not be merged

### 7A. B1/B2/B2.1-calibration — held
Scalar/relational recovery **at a known dimension** under auxiliary calibration.
- B1: `mean_with_aux_corr` 0.9999661041760123, 24 seeds [B1 `decision.json`].
- B2.1: `mean_with_aux_f1` 0.9969994875628853; minimal-anchor `mean_sparse_f1`
  0.9965407969143273 at anchor fraction 0.100, 24 seeds [B2 `decision.json`].

### 7B. Order-dimension blind recovery — NOT resolved
Whether the dimensionality of the latent order can be recovered WITHOUT the
harness supplying the answer. In the current run the 3D control is scored with a
literal `truth_axes=3` at the evaluation call site, recorded as
`classification_success_depends_on_harness_hint` = true
[B2 `decision.json`]; the classifier never discovers the dimensionality from data.
Open question for a future B2.2: classify order-dimension without passing
`truth_axes` at any evaluation call site.

---

## 8. Technically unclosed

- `harness_version` hashes the working-tree `gate_harness/*.py`, not a git-checkout
  of the referenced commit [`gate_harness/verify_decision.py`, `harness_version()`].
  A decision cannot be verified against a different (e.g. historical) harness state.
- `construction_may_be_tautological` and `classification_success_depends_on_harness_hint`
  immutability is enforced by `runner.run_gate` rejecting an experiment that sets a
  different value; it is not a language-level constant [`gate_harness/runner.py`,
  `_require_flag_absent_or_equal`].
- Red-team tests cover findings #1–#9. Not covered by a dedicated adversarial test:
  finding #10 (single-seed B1) — covered indirectly by `seed_policy` returning
  `INSUFFICIENT_SEEDS` but no test asserts it on a 1-seed decision.
- `scan_evaluation_call_sites` detects hints passed as keyword args or dict-literal
  values; a ground-truth value threaded through a positional variable (not a literal
  or dict key) is recorded only if it matches a forbidden name as that variable's
  identifier, not by data-flow tracing [`gate_harness/evaluation_oracle.py`].
- `evaluation_oracle` was not run against the original B2 module as a committed
  regression fixture; the `truth_axes=3` detection was demonstrated in-session on
  `relational_order_toy.py:495` and on the fixed module, not asserted in a test file.
