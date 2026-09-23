# Game-policy benchmark: CourierGrid

Reviewed 2026-09-23. This document proposes a browser-native benchmark for fast typed-decision models. It is an architecture/curriculum specification, not a measured result.

## Why a game?

A game gives the project something ordinary workflow corpora do not:
- thousands of cheap, repeatable sequential decisions;
- exact state/action/reward logs;
- controllable novelty and difficulty;
- known success/failure;
- deterministic or algorithmic teacher policies where available;
- counterfactual replay;
- a clean way to price optional frontier-model escalation in both latency and reward.

The research question is not "can an LLM play a game?" It is:

> Can a small decision model own the hot control loop, learn when to defer, and use a frontier model only when its expected improvement is worth the latency?

## Why not DOOM first?

DOOM is a compelling demonstration of fast inference, but it entangles perception, continuous visual change, partial observability, aiming and long-horizon control. A first benchmark should make policy quality and routing errors legible.

## Candidate environments

| Environment | Actions/state | Strength for this research | Weakness |
|---|---|---|---|
| 2048 | 4 actions; complete deterministic board | excellent imitation/distillation and planning baseline | little semantic structure; no interesting dynamic choice schema |
| LunarLander | 4 discrete actions; 8 numeric state variables | excellent latency/control benchmark; established Gymnasium environment | typed language-oriented encoders are a somewhat unnatural fit |
| MiniGrid/BabyAI | 7 discrete actions; local symbolic image + direction + textual mission | compositional goals, phase structure, partial observability, natural-language mission, configurable difficulty | Python reference environment rather than browser-native |
| BrowserGym/MiniWoB | dynamic web actions and realistic browser tasks | directly relevant to later web agents | action space and UI complexity are too high for the first System-One benchmark |
| **CourierGrid** | MiniGrid-inspired browser environment with explicit semantic API | designed around typed decision schemas, optional defer, browser/iPhone execution and oracle logging | new environment; external benchmark comparability must come through MiniGrid/LunarLander baselines |

Primary references:
- [MiniGrid](https://minigrid.farama.org/)
- [MiniGrid GoToObject](https://minigrid.farama.org/environments/minigrid/GoToObjectEnv/)
- [Gymnasium LunarLander](https://gymnasium.farama.org/environments/box2d/lunar_lander/)
- [BrowserGym](https://github.com/ServiceNow/BrowserGym)

## CourierGrid concept

The browser example in [examples/courier-grid](../../examples/courier-grid/) uses a small grid world:

1. locate and collect a key;
2. navigate to a locked gate;
3. unlock it;
4. locate and collect a package;
5. deliver the package to a dock;
6. recover from invalid actions or unexpected state.

The hot action vocabulary remains bounded:

`turn_left`, `turn_right`, `forward`, `pickup`, `drop`, `toggle`, `wait`.

The environment also exposes a **semantic observation** rather than forcing screenshot perception immediately: mission text, direction, inventory, nearby cells, previous action result, step count, and optional memory. A later benchmark can progressively remove privileged structure and add pixels/OCR/vision.

This follows MiniGrid's useful separation of a textual mission from a local grid observation. MiniGrid's canonical action space is also seven discrete actions, which makes external policy baselines easier to interpret.

## Hierarchical policy schema

A useful fast policy should answer several questions from one state:

~~~json
{
  "phase": {
    "type": "choice",
    "criteria": {
      "explore": "...",
      "get_key": "...",
      "open_gate": "...",
      "get_package": "...",
      "deliver": "...",
      "recover": "..."
    }
  },
  "action": {
    "type": "choice",
    "criteria": {
      "turn_left": "...",
      "turn_right": "...",
      "forward": "...",
      "pickup": "...",
      "drop": "...",
      "toggle": "...",
      "wait": "..."
    }
  },
  "control": {
    "type": "choice",
    "criteria": {
      "act": "execute the selected local action",
      "local_replan": "recompute a bounded local subgoal without a frontier call",
      "frontier_assist": "pay for slow semantic/planning assistance",
      "halt": "stop because the state is unsafe or contradictory"
    }
  }
}
~~~

The key idea is that **frontier escalation is a learned action**, not a mandatory verifier after every step.

## Training the defer/escalate action

This connects directly to established **selective classification / learning-to-defer** research. Madras, Pitassi and Zemel's [Learning to Defer](https://papers.neurips.cc/paper_files/paper/2018/hash/09d37c08f7b129e96277388757530c72-Abstract.html) explicitly gives a model a PASS/defer option to an external decision-maker. [FrugalGPT](https://arxiv.org/abs/2305.05176) similarly formalizes learned model cascades under cost constraints, while early-exit networks study adaptive computation based on input difficulty.

For this benchmark, do not hand-label every uncertain state as "escalate." Generate a counterfactual training target:

~~~text
V_fast(s)       = expected episode return if the local policy continues
V_assisted(s)   = expected return after one frontier/teacher intervention
C_frontier      = normalized latency/cost penalty

target(frontier_assist) if:
    V_assisted(s) - V_fast(s) > lambda * C_frontier
~~~

This turns escalation into an expected-value decision rather than a confidence superstition.

A simpler first approximation can train on:
- local-policy errors versus oracle action;
- low top-1/top-2 margin;
- high entropy;
- OOD/novel state;
- repeated invalid actions;
- phase/action contradiction;
- stalled progress.

But confidence and calibration should be separate from the learned defer policy. A calibrated classifier can be confident and still know that a particular state class is strategically difficult.

## Teacher hierarchy

Not every teacher signal should come from a frontier LLM.

### Algorithmic oracle first

For deterministic grid navigation, shortest-path/A* planning can generate cleaner action labels than an LLM. Use the oracle for:
- shortest legal paths;
- action labels;
- optimal/near-optimal episode reward;
- exact counterfactual regret for wrong actions;
- success/failure verification.

### Frontier model where semantics matter

Use the frontier teacher for:
- diverse mission paraphrases;
- new compositional mission templates;
- phase/subgoal ontology proposals;
- curriculum generation;
- adversarial or semantically ambiguous cases;
- explaining why a current schema lacks a useful choice;
- temporary **choice elevation** when the stable policy vocabulary is insufficient;
- reviewing clusters of policy failures for durable schema mutation.

This preserves high-quality deterministic labels while using the expensive model for the work it actually does better.

## Curriculum

1. **Action semantics** — full state, no partial observability.
2. **Navigation** — random start/goal; shortest-path imitation.
3. **Object interaction** — key, gate and package; phase + action jointly.
4. **Partial observation + memory** — student sees local view only.
5. **Language variation** — mission paraphrases and unseen combinations.
6. **Perturbation** — blocked routes, missing items, state changes after planning.
7. **Optional frontier assist** — assistance has an explicit latency/cost penalty.
8. **Teacher removal / budget shift** — evaluate at 0%, 1%, 5%, 10% and unlimited teacher-call budgets.

## Model comparison matrix

Run the same environment and splits through:

1. deterministic oracle;
2. SetFit/tiny embedding specialist;
3. GLiClass edge/base;
4. Laya base;
5. task-fine-tuned Laya;
6. hybrid GLiClass → Laya;
7. small constrained generative LM;
8. frontier model;
9. learned-defer hybrid.

## Metrics

### Policy
- success rate;
- cumulative reward;
- excess steps over oracle;
- invalid-action rate;
- phase accuracy;
- next-action accuracy;
- recovery success.

### Selective/autonomy
- autonomous coverage;
- success at autonomous coverage;
- frontier-call rate;
- escalation precision: calls that materially improve return;
- escalation recall: helpful-assistance states that are escalated;
- unnecessary frontier calls;
- teacher-induced regressions.

### Systems
- warm and cold decision latency;
- p50/p95 action latency;
- decisions/sec;
- browser memory;
- later iPhone battery/thermal impact;
- full episode wall-clock time;
- latency-weighted reward.

A useful objective is:

~~~text
utility =
    episode_reward
  - alpha * local_inference_ms
  - beta  * frontier_calls
  - gamma * frontier_latency_ms
~~~

Report a Pareto curve rather than treating one arbitrary weighting as universal.

## Why this helps Shortcuts research

CourierGrid exposes its state and actions through a stable JavaScript API. That lets us test three boundaries against the same environment:

1. **page-local loop** — ONNX/WebGPU classifier runs inside the game page;
2. **Safari Shortcut step** — Run JavaScript on Webpage retrieves state and applies/returns one bounded action;
3. **native App Intent policy** — Shortcut invokes a background native classifier.

The page-local loop is the only one intended for high-frequency play. Shortcut routes are integration benchmarks, not a recommendation to use the Shortcuts engine as a 10–60 Hz game loop.
