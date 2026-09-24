# Recovery completed — 24 September 2026

The source, generated graph/atlas, recordings, projection fixture and UI were recovered/rebuilt and saved on the development branch. See [current implementation and validation](../docs/activation-atlas-implementation.md). The historical interruption notes below are retained for provenance; their missing-file checklist is superseded.

# Activation atlas development checkpoint — 2026-09-24

This is an incomplete development branch, not a deployed or device-validated feature. The workspace disconnected during browser QA. Do not merge without completing the steps below.

## Observed before interruption

- Offline ONNX capture/calibration completed with network syscalls denied by research/offline_run.py.
- 48 labeled reference prompts, 8 domain landmarks, a frozen 3-axis PCA projection over normalized 2,048-dimensional residual states.
- 15/16 held-out prompt nearest-category matches. This is a small prompt-level check, not validation of generated-token semantics or causality.
- One original-versus-instrumented logits comparison had maximum absolute difference 0.0.
- Two genuine CPU greedy-generation recordings, 48 tokens each: OCR/Markdown and vegetable cream cheese.
- Local three-entry esbuild build succeeded after implementing the interface. Four existing signal/trace tests passed. No completed browser screenshot or mobile/WebGPU inference validation.

## Runtime design

Pinned model onnx-community/Llama-3.2-1B-Instruct-ONNX at 14007543b6dc92de88daf96a9aa85d2f95ace6ef. Hook /model/layers.9/input_layernorm/output_3 is the residual after zero-based block 8, before block 9 RMSNorm. Append Gather(axis=1,index=-1) and Cast float32 to expose atlas_hidden [1,2048]. Original external q4f16 weights remain unchanged (~1.09 GB).

Transformers.js 3.8.1 worker uses a custom cache to substitute the local patched graph for the exact pinned HF graph URL. SHA256 checks bind graph to reference atlas. Wrap model.forward: project atlas_hidden, calculate top-five raw full-vocabulary softmax candidates, dispose the extra tensor, and return original outputs. Streamer associates this pending state with the next selected token. First point is end-of-prefill; earlier prompt positions are not captured. Greedy generation, max512 prompt tokens, max128 new tokens. WebGPU shader-f16 required. Worker termination releases model on errors or explicit release.

Three.js 0.180.0 viewer uses a fixed PerspectiveCamera, OrbitControls, fixed reference landmarks and token trajectories; Canvas2D perspective fallback when WebGL unavailable. Single dirty requestAnimationFrame, capped device pixel ratio1.5, at most3 runs. Selected step drives text, candidate table, similarities and visible trajectory prefix. Separate atlas.html keeps the existing WebLLM view available. No backend or new hosting service.

Reference labels are developer-labeled prompt categories, NOT SAE features, identified neurons, chain-of-thought, or causal explanations. Similarities use centered native 2,048D vectors. Three saved PCA axes and scale never refit between runs. Display retained projection energy to reveal information loss. Generated positions can lie outside calibration clusters.

## Recover local work if workspace returns

Root: /workspace/scratch/1ede383385f0/scope-work/examples/latent-scope
Model files: /workspace/scratch/1ede383385f0/atlas-research
Local files: src/atlas.js, atlas-math.js, atlas-worker.js, atlas-view.js; dist/atlas.html, atlas.css; scripts/build.mjs; .gitignore; .npmrc; package.json/package-lock.json; modified dist/index.html link.
Generated data: dist/atlas/model_q4f16.onnx (~147KB), reference-atlas.json (~521KB), replay-ocr.json and replay-recipe.json (~38KB each). These must be saved to git, unlike the 1.09GB weights, node_modules, generated JS and copied ORT WASM vendor files.

The recovered mathematical module and worker are included in this checkpoint. Other interface files were local only when the environment disconnected; their text also appears in the development conversation. Do not treat them as committed.

## Complete before merging

1. Recover/reconstruct the UI and viewer, build script, HTML/CSS, dependencies and ignore rules. npm ci must avoid onnxruntime-node CUDA postinstall (app .npmrc ignore-scripts=true was used). Copy ort-wasm-simd-threaded.jsep.mjs and .wasm to dist/vendor during build.
2. Recover/rebuild generated atlas and recordings with the pinned model and network-denied calibration wrapper. Preserve version and graph hash.
3. Add Python-to-JS projection parity fixture; malformed/version-mismatched trace checks; verify token/state alignment, custom cache graph interception and hidden tensor disposal under Transformers.js.
4. Strengthen trace schema validation and source labels (imports must not be represented as authenticated CPU recordings). Similarity bars use [-1,1], with numeric cosine explicitly labeled.
5. Complete browser QA: replay both recordings, scrub start/middle/end, overlay, select point, orbit/reset, hide/show chat, import/export. Mobile100dvh and keyboard need device checks. Current browser attempt never completed.
6. Test live WebGPU path where supported; no iPhone performance claims until reproduced. Keep failures actionable and release worker allocations.
7. Run app tests/build and repository tooling unittest gate; update source ledger, research documentation, and test report. Review patch then merge/deploy using existing GitHub Pages Actions workflow.
