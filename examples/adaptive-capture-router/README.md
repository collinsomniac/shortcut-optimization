# Adaptive Capture Router

A research example for a **fast classifier + slow frontier teacher** autonomy loop.

The imagined iOS entry point is deliberately generic: a person shares text/URL/content from any app, a Shortcut/Share extension normalizes it into state, and a fast typed-decision model chooses what kind of capability should handle it. The example does not require iOS to understand the controller.

## Why this is more useful than a toy classifier

The controller asks several independent semantic questions in one batch:

- stable intent family;
- urgency;
- whether the schema itself fits;
- whether more context is needed;
- whether generation is actually necessary;
- sensitivity;
- whether the likely action crosses an external/irreversible boundary.

It then runs ordinary policy code. A frontier model is not the default controller. It appears only to **elevate the choice space**, fill a generative artifact, or reason about an ambiguous recovery.

After every executor step, a second typed-decision batch asks whether the task is complete and what recovery route is appropriate. This creates a bounded autonomous loop without granting the classifier arbitrary actions.

## Architecture

```text
Share Sheet / Shortcut / notification / onscreen context
                         │
                         ▼
                 normalize state
                         │
                         ▼
         ┌──── fast typed decision batch ────┐
         │ intent / urgency / schema fit      │
         │ context / generation / risk flags  │
         └────────────────┬───────────────────┘
                          │
                deterministic policy
             ┌────────────┼───────────────┐
             │            │               │
        safe route   ask/approve     low fit/confidence
             │                            │
             ▼                            ▼
         executor                  frontier teacher
             │                 elevate/mutate/generate
             │                            │
             │                    re-score bounded set
             └────────────┬───────────────┘
                          ▼
                       receipt
                          │
                          ▼
                  verification batch
                          │
                  stop / continue /
                 retry / elevate / ask
                          │
                    max-step boundary
```

## Files

- `decision-schema.json`: Laya-compatible `choice`, `score`, and `noul` questions.
- `demo.py`: provider-neutral bounded loop with a deterministic demo provider and optional real Laya adapter.
- `teacher-contract.md`: how a frontier model may propose new choices or generated content without directly taking authority.
- `fixtures/purchase-research.json`: a deliberately compound capture.

## Run the no-download demo

```bash
python3 examples/adaptive-capture-router/demo.py \
  examples/adaptive-capture-router/fixtures/purchase-research.json
```

The built-in deterministic provider exists only to exercise the state machine. It is **not a benchmark** and is not presented as AI.

## Run with Laya

Install Laya in an isolated environment and use the optional adapter:

```bash
pip install laya
python3 examples/adaptive-capture-router/demo.py \
  examples/adaptive-capture-router/fixtures/purchase-research.json \
  --provider laya \
  --model convaiinnovations/laya
```

The example passes the schema directly to `agent.predict(state, questions)`. Do not interpret one run as accuracy evidence. The base checkpoint is weak on Laya's own typed-decisions benchmark; a serious version of this workflow should collect data and fine-tune/calibrate a domain checkpoint.

## Choice elevation

Suppose the stable top-level classifier says `research`, but the captured item is specifically a used e-bike listing and the user wants to compare it with previously saved options.

The top-level schema should **not** permanently add every possible niche activity. Instead, the teacher can propose a temporary subordinate question:

```json
{
  "question_id": "research_subintent",
  "type": "choice",
  "criteria": {
    "compare_purchase_options": "compare a candidate purchase with saved alternatives",
    "verify_claims": "check factual claims or specifications",
    "find_missing_information": "fill important unknown facts",
    "general_research": "research without a more specific route"
  }
}
```

The fast model then chooses among those bounded options. Repeated successful elevations can later become candidates for offline schema mutation and specialist retraining.

## Policy boundary

The sample treats local draft/artifact creation as autonomously allowed, while external communication, spending, deletion, or other hard-to-reverse effects require approval. That boundary belongs in deterministic code, not in a prompt.

## Mapping to iOS later

A native version could map:

| Example component | iOS candidate |
|---|---|
| capture input | Share extension, Shortcut input, Receive What's On Screen, notification/screenshot automation |
| local classifier | Safari/ONNX prototype or native Core AI/custom runtime |
| controller | Shortcut for simple graphs; native app for richer long-lived loop |
| capability execution | App Intents / Shortcuts actions |
| local receipts/state | Shortcuts Storage, app group, app database |
| frontier teacher | Apple PCC/Foundation Models, ChatGPT/plugin service, other provider |
| approval | Shortcut prompt, App Intent confirmation, native UI |

The most compelling long-term form is probably a small native decision service exposing an App Intent such as `EvaluateDecisionSchema`, with Shortcuts remaining the user-visible orchestration layer.
