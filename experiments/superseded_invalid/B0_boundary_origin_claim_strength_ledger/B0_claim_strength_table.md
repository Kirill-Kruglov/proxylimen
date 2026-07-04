# B0 Claim Strength Table

Claim-strength levels are restricted to:
`FORM_ONLY`, `BOUNDARY_ACCOUNTING`, `TOY_REPLAY_DETERMINISTIC`,
`TOY_CONSEQUENCE_PROTOCOL`, `VIABILITY_SHIELD`,
`EXTERNAL_CONTACT_REQUIRED`, `RULE_GENERATED_CONTENT`,
`DERIVATION_EVIDENCE`, and `SUBSTRATE_CLAIM`.

## Allowed After S2

Allowed:

```text
FORM_ONLY
BOUNDARY_ACCOUNTING
TOY_REPLAY_DETERMINISTIC
TOY_CONSEQUENCE_PROTOCOL
```

Allowed only with explicit caveat:

```text
VIABILITY_SHIELD
EXTERNAL_CONTACT_REQUIRED
```

Not allowed:

```text
RULE_GENERATED_CONTENT
DERIVATION_EVIDENCE
SUBSTRATE_CLAIM
```

## Table

| claim | current tempting overclaim | allowed strength | reason | next evidence required |
| ----- | -------------------------- | ---------------- | ------ | ---------------------- |
| S0 passed anti-sophistry | S0 proves the semantic direction works | `BOUNDARY_ACCOUNTING` | S0 classified adversarial cases and blocked known sophistry modes | independent follow-up gates and consequence-bearing demonstrations |
| S1 microformalized statuses | S1 derived semantic status from logic | `BOUNDARY_ACCOUNTING`; `TOY_REPLAY_DETERMINISTIC` | S1 defined schema and rules, but fields remain externally supplied | finite field accounting plus later implementation spec |
| S2 specified finite toy model | S2 produced a semantic boundary generator | `BOUNDARY_ACCOUNTING`; `TOY_CONSEQUENCE_PROTOCOL` | S2 specified domains, rules, and toy consequence tokens | evidence that boundary force can arise without authored fields |
| S2 replay is deterministic | deterministic replay equals derived meaning | `TOY_REPLAY_DETERMINISTIC` | replay is deterministic only after human-authored fields are supplied | anti-oracle implementation and field provenance audit |
| S2 generated the semantic boundary | rules created meaningful boundaries | forbidden: `RULE_GENERATED_CONTENT` | S2 processed authored fields; it did not generate boundary force | show non-authored field generation plus consequence pressure |
| Derivational ecology is a substrate | finite toy ecology is substrate evidence | forbidden: `SUBSTRATE_CLAIM` | no learner evidence, transfer gate, or world-model derivation was shown | separate substrate / representation / learner gates |
| Protective boundary is truth | safety filter proves what is true | forbidden; caveated `VIABILITY_SHIELD` only | viability guards protect against collapse and laundering, not truth | external consequence boundary and safety/truth separation |
| Grammar boundary is semantic | well-formed derivation creates meaning | forbidden: `DERIVATION_EVIDENCE` | grammar admits form only and is blocked from semantic promotion | consequence tests and non-grammar anchors |
| Future-meaning can be preserved | future meaning is guaranteed | `BOUNDARY_ACCOUNTING`; `EXTERNAL_CONTACT_REQUIRED` | S0-S2 preserve candidates as `SUSPENDED`, not as meaningful | future object class, scope, and tested consequences |
| Liquid powder was always inside the boundary | S0 discovered liquid powder as valid | `FORM_ONLY`; `BOUNDARY_ACCOUNTING`; `EXTERNAL_CONTACT_REQUIRED` | it is preserved as future-meaning candidate, with untested outcomes | object-class and material behavior tests |
| Viability bias is necessary | safety bias is truth or sufficient | caveated `VIABILITY_SHIELD` | viability protects the learner/population but does not establish semantic truth | explicit separation from truth boundary and learner evidence |
| S3 may proceed | S3 may implement a semantic generator | `BOUNDARY_ACCOUNTING`; `TOY_REPLAY_DETERMINISTIC` | B0 permits only implementation spec for replay/accounting protocol | S3 must remain a spec and preserve boundary-origin labels |
