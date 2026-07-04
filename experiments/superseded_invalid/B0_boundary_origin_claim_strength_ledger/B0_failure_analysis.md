# B0 Failure Analysis

## B0-FAIL-HUMAN-AUTHORED-BOUNDARY-AS-DERIVED

Result:
Not triggered.

Reason:
B0 explicitly classifies S2 scopes, assumptions, outcomes, tests, extension
paths, and case replay fields as `HUMAN_AUTHORED_BOUNDARY` unless another
source is separately identified. S2 is downgraded to accounting / replay.

Residual risk:
Future S3 work could accidentally hide authored fields inside defaults. S3, if
allowed later, must expose provenance for every field.

## B0-FAIL-PROTECTIVE-BOUNDARY-AS-TRUTH

Result:
Not triggered.

Reason:
Goodhart guards, danger statuses, and CL viability constraints are classified
as `VIABILITY_BOUNDARY`. They support only caveated `VIABILITY_SHIELD`, not
truth.

Residual risk:
Protective rejection can feel like truth rejection. Reports must keep those
separate.

## B0-FAIL-GRAMMAR-BOUNDARY-AS-SEMANTIC

Result:
Not triggered.

Reason:
Derivation traces and primitives are classified as `FORM_BOUNDARY`. They allow
`FORM_ONLY` and sometimes `POETIC`, but not semantic content or derivation
evidence.

Residual risk:
Any future Sanskrit / derivational layer must remain form lineage unless it is
connected to consequence pressure.

## B0-FAIL-RULE-BOUNDARY-NONCONTENTFUL

Result:
Not triggered as a failure because rule boundaries are downgraded.

Reason:
T1-T9 are classified as `RULE_GENERATED_BOUNDARY` that process fields. B0 does
not claim rule-generated content. Rule boundaries are allowed only as
deterministic toy replay unless consequence pressure is present.

Residual risk:
If a future report claims the rules generate meaning by themselves, this
failure mode becomes active.

## B0-FAIL-EXTERNAL-BOUNDARY-UNAVAILABLE

Result:
Not triggered.

Reason:
B0 states that external contact is required for truth strength beyond toy
protocols. It does not claim that such contact has been achieved or safely
exposed.

Residual risk:
The project cannot move from toy status to real semantic strength without an
external-contact route and transfer gate.

## B0-INCONCLUSIVE

Result:
Not selected.

Reason:
Boundary sources can be separated enough for a safe next specification step
once S2 is reinterpreted conservatively.

## HALT-GOAL-DRIFT

Result:
Not triggered.

Reason:
B0 did not plan S3, implement code, run experiments, rename the framework, or
turn into Sanskrit worship or a philosophical essay. It produced a ledger,
claim-strength table, trilemma map, S2 reinterpretation, and decision.

## Pass Condition Check

| condition | result |
|---|---|
| Boundary taxonomy applied to all required targets | pass |
| Boundary law preserved | pass |
| S2 not overclaimed as boundary generator | pass |
| Human-authored fields not treated as derived | pass |
| Protective / viability boundary not treated as truth | pass |
| Grammar / derivation boundary not treated as semantic | pass |
| Rule-generated boundary not called meaningful without consequence pressure | pass |
| Claim-strength levels downgraded where needed | pass |
| S3 allowed only as boundary-accounting / replay-protocol implementation spec | pass |
| No implementation, experiment, training, substrate, derivability, or grounding claim | pass |
