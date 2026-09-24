# Latent Scope: browser model flow

A static, client-side instrument for a 1B parameter Llama model. WebLLM performs prefill and generation in WebGPU; a WebGL2 canvas renders a small rolling texture of next-token probabilities. The diagram maps the prompt, model architecture, returned candidate distribution, and decoded reply onto one screen. Green stages display input or runtime-returned measurements. Blue stages are **architecture only**; they do not claim to expose weights or internal activations.

## New: activation atlas

Open `atlas.html` for the experimental streaming 3D map of actual middle-layer activations. Start with the two recorded CPU traces, or load the separate ONNX/WebGPU model. Coordinates are frozen across runs; labels are reference-prompt categories, not causal features. See [implementation, measurements and limitations](docs/activation-atlas-implementation.md). Live iPhone validation remains pending.

## Run locally

```sh
npm ci
npm run build
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000/` in a WebGPU/WebGL2 browser, load the model, and send a prompt. For GitHub Pages, this example lives at `examples/latent-scope/` and the included GitHub Actions workflow builds `dist/` under the project subpath `/latent-scope/`. The repo owner must enable Pages with **GitHub Actions** as its source for deployment. The model files download separately and can be evicted from browser cache; the static host serves the app, not inference.

Use the token range control or tap a column of the signal grid to inspect the chosen output token and its up-to-five returned alternatives. **Live** returns to the newest step. The current window holds 64 steps; the export preserves the latest full run and includes the conversation text. The table shows one-token choices, not complete branched answers. The first-output duration includes prompt processing, queueing, and sampling; it is not a layer-by-layer prefill measurement. Output speed starts at first content or token log probabilities and excludes most prompt processing.

The lower conversation panel stays within the same viewport on mobile and can be minimized with **Focus diagram**. It is the only element that scrolls internally. The main page does not scroll. During generation the shader uploads an 8 KiB float texture per emitted token; it draws on data changes or resize and caps display pixel ratio at 2. When the app is hidden, no draw is issued. An offline named-tensor probe is documented separately in [`research/README.md`](research/README.md) and is not wired to the browser.

## What is measured

The output distribution comes from WebLLM `logprobs: true, top_logprobs: 5`. The sampled token may be outside the five returned candidates; it is still shown. The remainder is the probability mass not represented by the sampled token and distinct returned alternatives. *Entropy is normalized within returned top candidates only. High confidence does not establish correctness or causal feature attribution. No browser API in this app reveals hidden neurons, per-layer tensors, expert routing, or weights.

See [the visual/adapter design](docs/visual-and-adapter-design.md) for the annotated screenshot, Laya research, and boundary between a token generator and a typed decision model. The broader [interpretability roadmap](docs/interpretability-roadmap.md) tracks activation capture and causal validation.

## Checks

`node --test test/*.test.js` checks sampled token handling and trace data. `npm run build` bundles the app. This revision still needs a run on the owner's iPhone to check the keyboard, model cache, range input, and responsiveness in Safari/Chrome. No Laya browser model has been loaded by this app.
