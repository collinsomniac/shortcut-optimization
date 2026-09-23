# CourierGrid

Browser-native, MiniGrid-inspired research environment for comparing fast decision models, learned deferral and optional frontier assistance.

**Status:** environment scaffold. It is not yet a model benchmark.

## Goal

Collect the yellow key, unlock the gate, pick up the blue package and deliver it to the green dock.

The environment exposes:
- a **student observation**: local semantic view + mission + inventory + recent outcome;
- an **oracle state**: full map/state for deterministic planning, logging and training labels.

The oracle state must not be given to a student policy in fair evaluation.

## Why this environment

See [game-policy benchmark](../../docs/research/game-policy-benchmark.md). CourierGrid is designed around:
- seven bounded actions;
- phase classification;
- partial observability;
- language-conditioned goals;
- invalid-action recovery;
- explicit `frontier_assist` as a control choice;
- teacher-generated language without requiring a frontier model for every step.

## Browser API

~~~js
window.courierGrid.getObservation()
window.courierGrid.getFullState() // oracle/debug only
window.courierGrid.getAvailableActions()
window.courierGrid.step("forward")
window.courierGrid.reset()
~~~

The values are JSON-friendly so a later Run JavaScript on Webpage Shortcut can exchange state/actions.

## Run

Serve/open `index.html` through a static web server or later GitHub Pages.

Controls:
- Left / Right: turn;
- Up: forward;
- P: pickup;
- D: drop;
- T: toggle gate;
- Space: wait;
- R: reset.

Touch buttons expose the same actions.

## Policy schema

`policy-schema.json` asks for:
- phase;
- next action;
- control = act / local_replan / frontier_assist / halt;
- progress.

The controller calls a frontier model only when the local policy selects `frontier_assist` and the current budget/policy permits it.

## Training path

1. implement A*/state-machine oracle from full state;
2. generate optimal trajectories over randomized seeds/maps;
3. train action + phase from student observations;
4. add partial map memory;
5. add teacher-generated mission paraphrases/counterfactuals;
6. train `frontier_assist` from counterfactual policy regret;
7. compare SetFit, GLiClass, Laya and constrained generative baselines;
8. run one policy in browser ONNX/WebGPU;
9. later expose the same policy through a background App Intent.

The current game is deterministic and intentionally small enough that errors remain inspectable.
