import {build} from 'esbuild';
import {mkdir,copyFile} from 'node:fs/promises';
await build({entryPoints:['src/app.js','src/atlas.js','src/atlas-worker.js'],bundle:true,format:'esm',platform:'browser',target:'es2022',outdir:'dist',minify:true});
await mkdir('dist/vendor',{recursive:true});
for(const name of ['ort-wasm-simd-threaded.jsep.mjs','ort-wasm-simd-threaded.jsep.wasm'])await copyFile('node_modules/onnxruntime-web/dist/'+name,'dist/vendor/'+name);
