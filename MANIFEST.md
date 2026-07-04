# proxylimen extraction manifest

Source repository: `/home/master/llm_projects/ascesis`.
Target repository: `/home/master/llm_projects/proxylimen`.

Harness-valid means `harness.verify_decision` returned `VALID` after copying. Superseded-invalid means the copied artifact is preserved as historical evidence and is not citable as a current result.

| item | source | target | status | size_bytes |
|---|---|---|---|---:|
| `gate_harness` | `/home/master/llm_projects/ascesis/gate_harness` | `gate_harness` | tooling / verifier | 77048 |
| `canonical/RESULTS_CANONICAL.md` | `/home/master/llm_projects/ascesis/RESULTS_CANONICAL.md` | `canonical/RESULTS_CANONICAL.md` | canonical | 26463 |
| `canonical/MEMO_B_BRANCH_HARNESS.md` | `/home/master/llm_projects/ascesis/MEMO_B_BRANCH_HARNESS.md` | `canonical/MEMO_B_BRANCH_HARNESS.md` | canonical | 13148 |
| `experiments/harness_valid/B1_harness_rerun` | `/home/master/llm_projects/ascesis/experiments/B/B1_harness_rerun` | `experiments/harness_valid/B1_harness_rerun` | harness-valid | 9364 |
| `experiments/harness_valid/B2_harness_rerun` | `/home/master/llm_projects/ascesis/experiments/B/B2_harness_rerun` | `experiments/harness_valid/B2_harness_rerun` | harness-valid | 72002 |
| `experiments/harness_valid/B2_2` | `/home/master/llm_projects/ascesis/gate_harness_experiments/B2_2` | `experiments/harness_valid/B2_2` | harness-valid | 49096 |
| `experiments/harness_valid/B2_2_1` | `/home/master/llm_projects/ascesis/gate_harness_experiments/B2_2_1` | `experiments/harness_valid/B2_2_1` | harness-valid | 43538 |
| `experiments/harness_valid/B2_3` | `/home/master/llm_projects/ascesis/gate_harness_experiments/B2_3` | `experiments/harness_valid/B2_3` | harness-valid | 7840103 |
| `experiments/superseded_invalid/B0_boundary_origin_claim_strength_ledger` | `/home/master/llm_projects/ascesis/experiments/B/B0_boundary_origin_claim_strength_ledger` | `experiments/superseded_invalid/B0_boundary_origin_claim_strength_ledger` | superseded-invalid | 33584 |
| `experiments/superseded_invalid/B1_auxiliary_variable_identifiability_gate` | `/home/master/llm_projects/ascesis/experiments/B/B1_auxiliary_variable_identifiability_gate` | `experiments/superseded_invalid/B1_auxiliary_variable_identifiability_gate` | superseded-invalid | 47013 |
| `experiments/superseded_invalid/B1_1_auxiliary_calibration_robustness` | `/home/master/llm_projects/ascesis/experiments/B/B1_1_auxiliary_calibration_robustness` | `experiments/superseded_invalid/B1_1_auxiliary_calibration_robustness` | superseded-invalid | 80319 |
| `experiments/superseded_invalid/B2_relational_order_dimension_recovery` | `/home/master/llm_projects/ascesis/experiments/B/B2_relational_order_dimension_recovery` | `experiments/superseded_invalid/B2_relational_order_dimension_recovery` | superseded-invalid | 116984 |
| `experiments/superseded_invalid/README_SUPERSEDED.md` | `(generated in proxylimen)` | `experiments/superseded_invalid/README_SUPERSEDED.md` | superseded-invalid marker | 786 |
| `demo/blind_dimension.html` | `/home/master/llm_projects/ascesis/essay_demo/blind_dimension.html` | `demo/blind_dimension.html` | demo / uncommitted in source | 25874 |
| `essay/` | `(created empty)` | `essay` | empty scaffold | 0 |
| `essay/appendices/` | `(created empty)` | `essay/appendices` | empty scaffold | 0 |
| `references/` | `(created empty)` | `references` | empty scaffold | 0 |
| `.gitignore` | `(generated in proxylimen)` | `.gitignore` | repo hygiene | 51 |

Verification summary: all five `experiments/harness_valid/*/decision.json` files verified `VALID`; all copied superseded `*decision*.json` files verified `INVALID` because they lack `_harness_provenance`.
