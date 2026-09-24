# Streaming activation atlas — development experiment

24 September 2026. Open `atlas.html` from Latent Scope. This route now instruments a real Llama 3.2 1B residual state; the original `index.html` remains the WebLLM probability instrument. Runtime remains static GitHub Pages plus the client browser. No remote inference backend, chats, or activation uploads.

## What changed and why

WebLLM's stock compiled artifact did not expose the desired tensors. The new route uses Transformers.js **3.8.1**, ONNX Runtime Web (locked dependency), Three.js **0.180.0**, and the immutable ONNX model export `onnx-community/Llama-3.2-1B-Instruct-ONNX@14007543b6dc92de88daf96a9aa85d2f95ace6ef`, `q4f16`. The original external weights are 1,089,605,632 bytes; browser peak memory exceeds that. Mobile throughput and peak memory are unknown until measured on the target device.

The patched graph adds Gather(axis=1,index=-1) and float32 Cast to `/model/layers.9/input_layernorm/output_3`, exposing `atlas_hidden [1,2048]`. This is the residual sum after block 8 (zero-based), before block 9 RMSNorm. One CPU logits parity comparison was exactly equal. No weights or normal logits path are intentionally modified. Making an intermediate tensor observable can change runtime optimization and synchronization; zero numerical difference on one prompt is not proof of zero overhead or universal parity.

A worker substitutes this small graph through the pinned runtime's custom-cache interface, verifies its SHA256 against the atlas, and downloads the original model files. The ordinary browser cache namespace is isolated from the atlas cache. Persistent cache failure remains recoverable. `model.forward` captures the activation and full-vocabulary raw top-five softmax before greedy selection; a generation streamer associates each pending state with its chosen next token. Float32 activation readback is 8 KiB per step. KV caches use the runtime's GPU-buffer output preference; projected coordinates and similarity values cross to the UI. This is indirect CPU readback, not zero-copy shader access to weights.

Each prompt starts a fresh context: max512 input tokens, max128 generated tokens. The first observation is at the end of prefill, predicting the first output token. Later observations follow the context position that predicts each subsequent token. Prompt-position activations before the endpoint are not captured. This is a dense model with no expert router.

## Fixed coordinates and honest semantics

Normalize each 2,048D activation. Subtract the fixed mean of 48 reference prompts across eight developer-labeled categories. Project onto three fixed PCA axes with deterministic signs and one saved scale. Categories use mean reference vectors. Cosine similarity is computed against centered prototypes in the original 2,048D space, not in 3D. Reference data, basis and scale are included in a version fingerprint; trace imports must match it and the model revision/hook. Nothing refits as tokens arrive or between runs.

The map's lines mean temporal succession. Positions are a lossy view of activation geometry, not one point per weight or neuron. Semantic labels are reference-defined, not SAE-discovered features. Similarity is neither probability nor causal attribution. The UI reports the fraction of each centered state's squared norm retained by the three axes.

**Observed limitation:** OCR starts nearest Software (cosine about .694, 48% retained); the recipe starts nearest Food & cooking (.595, 27% retained). Later sampled points in these recordings have roughly .09–.14 maximum cosine and only 2–4% retained. The prompt-calibrated basis poorly covers many decoding states. A weak nearest match must not be interpreted as the model secretly switching topics. The interface warns about low retention. There is no validated activation verbalizer in this build.

The next useful experiment is a larger, balanced reference corpus including decoding states, held-out prompts, format controls and matched positions. Freeze the learned map before evaluation. Compare category retrieval, neighborhood preservation, stability across paraphrases and false matches on out-of-domain prompts. Only add natural-language feature descriptions after validating an exact-model probe/SAE dictionary and its reconstruction or intervention fidelity. A prettier projection does not establish those properties.

## Interaction and resource bounds

The page fits the viewport with internal transcript/inspector scrolling, a hide-text control, orbit/pinch/reset camera, token scrubbing, up to three overlaid runs, and version-checked trace import/export. Scrubbing changes the visible trajectory prefix, selected token, full response prefix, measurements and alternatives together. Imported traces are explicitly unauthenticated. Recordings are explicitly CPU data; playback timing is a UI animation, while displayed measurements retain original capture timing.

Three.js uses WebGL with a Canvas2D perspective fallback. Drawing is invalidation-driven, stops when hidden, and caps pixel ratio at1.5. Geometry is bounded to3×128 live steps (imports allow512 each); it is rebuilt on updates, not an unbounded particle simulation. Model loading and generation run off the UI thread. Release terminates the worker; errors also terminate it, preventing failed-generation cache allocations from accumulating. Reopening the original WebLLM view unloads this page rather than keeping two model runtimes resident.

## Reproduction

Build the browser app with `npm ci`, `node --test test/*.test.js`, `npm run build`. App `.npmrc` disables install scripts to avoid optional onnxruntime-node CUDA downloads; esbuild's platform package remains usable. Build copies the matching ORT JSEP module and WASM to `dist/vendor`. Generated bundles/vendor are not committed. The instrumented graph, atlas, fixture and recordings are committed.

To rebuild data, download config.json, tokenizer.json, tokenizer_config.json, onnx/model_q4f16.onnx and onnx/model_q4f16.onnx_data from the immutable model revision into one local directory. Install `onnx`, `onnxruntime`, `tokenizers`, `numpy`. Run:

```sh
python research/offline_run.py research/build_atlas.py --source /absolute/model-directory --out dist/atlas
```

The Linux wrapper denies socket syscalls before importing the inference runtime and verifies the denial. No model downloads occur during calibration. Preserve shipped data to preserve exact coordinates; recalibration produces a version tied to its numeric contents.

`research/validate_runtime.mjs` checks four actual Transformers.js CPU steps against the Python recording. Put the patched graph and original external weights in the model directory's `onnx/` folder. Invoke `python research/offline_run.py research/run_js_validation.py /absolute/model-directory/`. The runner disables V8 native Float16Array for the ORT Node1.21 native binding on Node24; without that flag this native-only test fails on its float16 input type. This flag is not a browser workaround and does not validate WebGPU.

## Validation record

- Linux CPU calibration: 48 references; 15/16 held-out prompt category matches. Small development set, not general semantic accuracy.
- One patched-vs-original CPU logits comparison: max absolute difference0.
- Two real48-token greedy recordings with per-token state alignment.
- Transformers.js3.8.1 / ORT Node CPU:4 forward calls,4 aligned tokens `[8586,596,264,4382]`; maximum projected-coordinate difference vs Python `8.304918025503483e-8`.
- App:9 tests passed, including independent Python/JS activation projection, graph checksum, schema/coordinate rejection and probability mass. Build passed.
- Repository tooling:7 unittest tests passed from repo root.
- Browser/mobile checks are recorded separately below when completed. Localhost preview was inaccessible from the cloud browser (`ERR_BLOCKED_BY_CLIENT`); this was a preview-network limitation, not an application result.
- Live WebGPU on iPhone17 Pro Max remains unverified. No frame-rate, throughput or battery claim is made.

## Sources and attribution

See the [source ledger](../../../docs/research/source-ledger.md), section “Latent Scope activation atlas”. Model materials retain [Llama3.2 license](../dist/atlas/LICENSE.txt), use policy and notice; application code follows the repository license. Built with Llama.

### Published browser check

GitHub Pages Actions installation,9 tests, build and deployment succeeded. Cloud Chrome reproduced OCR/recipe playback, first/middle/end scrubbing, trace switching, hide/show, and export/reimport of a48-event trace. Export's browser automation event timed out, but the downloaded JSON was present and independently validated, then successfully reimported. Live-load capability detection reports missing shader-f16 and restores the load control in this browser. WebGL is disabled here; the perspective Canvas2D fallback rendered the real coordinates. GPU rendering and actual iPhone inference are not validated by these checks.

A390×660 iframe viewport had equal client/scroll dimensions (390×660), with no page overflow. This is responsive-layout simulation, not Safari/device emulation. `atlas-layout-check.html` provides430×850,390×660 and760×390 cases. Visible landmark overlap prompted deterministic screen-space label separation and a closer default camera, with no change to data coordinates. A cached old bundle delayed that fix during verification; the build now versions JS/CSS/worker URLs and revalidates graph/atlas fetches.
