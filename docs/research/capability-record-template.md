# Capability record template

Copy this structure for a capability that may become part of the future harness. Delete fields that truly do not apply; use `unknown` rather than inventing values.

## Identity

- **Semantic ID:** `group.capability`
- **Human purpose:**
- **Layer:** workflow / app / context / state / decision / model / web / file / script-shell / transport / verification / other
- **Status:** research lead / documented candidate / later experiment / implemented / deprecated

## Contract

- **Inputs:** types, required/optional fields, size/context limits
- **Outputs:** types and status/error variants
- **Side effects:** none / local state / app data / network / communication / destructive / other
- **Idempotent or reversible?:**
- **Permissions / user interaction:**

## Candidate implementations

| Provider/action/runtime | Preconditions | Advantages | Boundaries | Evidence |
|---|---|---|---|---|
| | | | | |

## Evidence

- **Primary source(s):**
- **Maintainer/implementation source(s):**
- **Independent/community source(s):**
- **Evidence label(s):** documented / artifact-inspected / reproduced / reported / hypothesis / unknown
- **Reviewed date/version:**

## Composition

- **Natural upstream capabilities:**
- **Natural downstream capabilities:**
- **Representative use cases:**
- **Fallback/escalation path:**

## Risk and portability

- **Data leaving device:**
- **Secret handling:**
- **Required app/account/device:**
- **Failure if provider unavailable:**
- **Distribution/share concerns:**

## Research questions

-

## Eventual experiment

- **Hypothesis:**
- **Fixture/input:**
- **Success metrics:**
- **Important negative/control case:**

Do not mark an experiment result here until a dated record exists under `experiments/`.