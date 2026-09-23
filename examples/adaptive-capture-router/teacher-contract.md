# Frontier teacher contract

The teacher is powerful but deliberately **not authoritative**. It may propose semantics; it does not directly execute arbitrary actions.

## Allowed operations

### 1. `elevate_choices`

Use when a stable parent label is correct but too coarse.

Input:

```json
{
  "operation": "elevate_choices",
  "request_id": "...",
  "parent_choice": "research",
  "state_excerpt": {},
  "existing_children": {},
  "constraints": {
    "max_new_choices": 4,
    "labels_must_be_mutually_distinguishable": true,
    "no_side_effects": true
  }
}
```

Output:

```json
{
  "question": {
    "id": "research_subintent",
    "type": "choice",
    "instructions": "Which research operation best matches the user's outcome?",
    "criteria": {
      "compare_purchase_options": "compare a candidate purchase with saved alternatives",
      "verify_claims": "check claims, specifications, authenticity, or compatibility",
      "find_missing_information": "identify and obtain decisive missing facts",
      "general_research": "research without a better specific category"
    }
  },
  "novelty_note": "The state includes a candidate purchase and saved alternatives."
}
```

The controller validates the shape, label count and allowed parent, then asks the fast classifier to score the new question.

### 2. `generate_artifact`

Use when the classifier says an operation genuinely requires generative text/code.

The teacher gets a narrow output schema and cannot choose the side effect. Example: generate a draft message, but the deterministic controller separately decides whether sending it requires user approval.

### 3. `request_context`

Propose the smallest missing field that would discriminate between current choices. The user or an authorized capability supplies the field.

### 4. `schema_review` — offline only

Analyze accumulated difficult cases and propose durable split/merge/rename/add changes. Any durable change invalidates previous calibration assumptions and should create a new schema/model version.

## Teacher data-generation roles

A frontier model is especially valuable offline for:

- generating balanced cases per label;
- counterfactual pairs where one state edit flips one question;
- hard negatives near decision boundaries;
- multilingual/noisy paraphrases;
- probability/soft-label suggestions;
- critiquing overlapping criteria;
- generating new cases from student errors;
- generating candidate labels for human review.

Use multiple teachers or human review for a held-out subset when possible. Teacher agreement is not ground truth.

## Feedback record

Every escalated case can become a training candidate:

```json
{
  "schema_version": "0.1",
  "state_hash": "...",
  "fast_model": {
    "model_id": "...",
    "distribution": {},
    "confidence": 0.0
  },
  "trigger": "low_margin",
  "teacher": {
    "provider": "...",
    "proposal": {}
  },
  "human_or_postcondition_outcome": {},
  "eligible_for_training": true
}
```

Do not store sensitive raw state when a redacted semantic record is sufficient.
