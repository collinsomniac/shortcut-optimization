import {AutoModelForCausalLM,AutoTokenizer,env,InterruptableStoppingCriteria} from '@huggingface/transformers';
import {MODEL,REVISION,chatText,makeProjector,topCandidates} from './atlas-math.js';
let model,tokenizer,atlas,project,pending,loading=false,generating=false;
const stopping=new InterruptableStoppingCriteria();const emit=(type,data={})=>postMessage({type,...data});
env.allowLocalModels=false;env.backends.onnx.wasm.numThreads=1;env.backends.onnx.wasm.proxy=false;
env.backends.onnx.wasm.wasmPaths=new URL('./vendor/',import.meta.url).href;
async function load(){
 if(model||loading)return;loading=true;
 try{
  if(!navigator.gpu)throw Error('Live capture requires WebGPU. Recorded traces are available.');
  const adapter=await navigator.gpu.requestAdapter();if(!adapter?.features.has('shader-f16'))throw Error('Live capture requires WebGPU shader-f16. Recorded traces are available.');
  atlas=await(await fetch(new URL('./atlas/reference-atlas.json',import.meta.url),{cache:'no-cache'})).json();project=makeProjector(atlas);
  const graph=await(await fetch(new URL('./atlas/model_q4f16.onnx',import.meta.url),{cache:'no-cache'})).arrayBuffer();
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',graph)),x=>x.toString(16).padStart(2,'0')).join('');
  if(hash!==atlas.graphSha256)throw Error('Model graph and atlas mismatch. Refresh this page.');
  const graphURL=`https://huggingface.co/${MODEL}/resolve/${REVISION}/onnx/model_q4f16.onnx`;
  let cache;try{cache=await caches.open('latent-scope-atlas-v1');}catch{emit('status',{text:'Storage unavailable; continuing without persistent cache.'});}
  env.useBrowserCache=false;env.useCustomCache=true;
  env.customCache={
   async match(req){const url=typeof req==='string'?req:req.url;if(url===graphURL)return new Response(graph,{headers:{'Content-Type':'application/octet-stream','Content-Length':String(graph.byteLength)}});try{return await cache?.match(req);}catch{return undefined;}},
   async put(req,res){try{await cache?.put(req,res);}catch{emit('status',{text:'Cache full; next visit may download the model again.'});}}
  };
  let last=0;const progress=p=>{if(performance.now()-last>200||p.status==='ready'){last=performance.now();emit('status',{text:p.status==='progress'?`Downloading ${p.file.split('/').at(-1)} · ${Math.round(p.progress||0)}%`:`${p.status}: ${p.file||'Preparing model'}`});}};
  tokenizer=await AutoTokenizer.from_pretrained(MODEL,{revision:REVISION,progress_callback:progress});
  model=await AutoModelForCausalLM.from_pretrained(MODEL,{revision:REVISION,dtype:'q4f16',device:'webgpu',progress_callback:progress});
  const forward=model.forward.bind(model);
  model.forward=async inputs=>{const o=await forward(inputs);if(!o.atlas_hidden)throw Error('Instrumented activation output missing');const count=o.logits.dims.at(-1);pending={...project(o.atlas_hidden.data),candidates:topCandidates(o.logits.data.subarray(o.logits.data.length-count)).map(x=>({...x,token:tokenizer.decode([x.id],{skip_special_tokens:false})}))};o.atlas_hidden.dispose();delete o.atlas_hidden;return o;};
  emit('ready');
 }catch(e){if(model){await model.dispose().catch(()=>{});model=undefined;}emit('error',{message:String(e.message||e)});}finally{loading=false;}
}
async function generate(prompt){
 if(!model||generating)return;generating=true;stopping.reset();pending=undefined;let failed=false;
 try{const inputs=tokenizer(chatText(prompt),{add_special_tokens:false}),inputCount=inputs.input_ids.dims.at(-1);if(inputCount>512)throw Error('Use a shorter prompt: this experiment allows 512 input tokens.');
  const began=performance.now(),generated=[];let skip=true;
  const streamer={put(batch){if(skip){skip=false;return;}if(!pending)throw Error('Missing activation for generated token');const id=Number(batch[0][0]),step=generated.length;generated.push(id);emit('token',{event:{step,phase:step===0?'prefill':'decode',contextPosition:inputCount+step-1,predictedPosition:inputCount+step,tokenId:id,token:tokenizer.decode([id],{skip_special_tokens:false}),text:tokenizer.decode(generated,{skip_special_tokens:true}),elapsedMs:Math.round(performance.now()-began),...pending}});pending=undefined;},end(){}};
  await model.generate({...inputs,max_new_tokens:128,do_sample:false,repetition_penalty:1,eos_token_id:[128001,128008,128009],streamer,stopping_criteria:[stopping]});
 }catch(e){failed=true;emit('error',{message:String(e.message||e)});}finally{generating=false;emit('done',{failed});}
}
onmessage=e=>{const m=e.data;if(m.type==='load')load();else if(m.type==='generate')generate(m.prompt);else if(m.type==='stop')stopping.interrupt();};
