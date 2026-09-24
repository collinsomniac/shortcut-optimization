import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {AutoModelForCausalLM,AutoTokenizer,env} from '@huggingface/transformers';
import {makeProjector,topCandidates,chatText} from '../src/atlas-math.js';
env.allowRemoteModels=false;env.useFSCache=false;
const root=process.argv[2],atlas=JSON.parse(await readFile('dist/atlas/reference-atlas.json')),replay=JSON.parse(await readFile('dist/atlas/replay-ocr.json'));
process.chdir(root+'onnx');
const tokenizer=await AutoTokenizer.from_pretrained(root,{local_files_only:true});
const model=await AutoModelForCausalLM.from_pretrained(root,{local_files_only:true,dtype:'q4f16',device:'cpu',session_options:{intraOpNumThreads:4}});
const project=makeProjector(atlas),forward=model.forward.bind(model);let pending,skip=true,events=[],calls=0;
model.forward=async inputs=>{const out=await forward(inputs);assert.equal(out.atlas_hidden.data.length,2048);pending={...project(out.atlas_hidden.data),top:topCandidates(out.logits.data.subarray(out.logits.data.length-out.logits.dims.at(-1)))};out.atlas_hidden.dispose();delete out.atlas_hidden;calls++;return out;};
const streamer={put(batch){if(skip){skip=false;return;}assert.ok(pending);const id=Number(batch[0][0]);assert.equal(id,pending.top[0].id);events.push({id,...pending});pending=undefined;},end(){}};
await model.generate({...tokenizer(chatText(replay.prompt),{add_special_tokens:false}),max_new_tokens:4,do_sample:false,repetition_penalty:1,eos_token_id:[128001,128008,128009],streamer});
assert.equal(calls,4);assert.equal(events.length,4);let maxDelta=0;
for(let i=0;i<4;i++){assert.equal(events[i].id,replay.events[i].tokenId);for(let j=0;j<3;j++)maxDelta=Math.max(maxDelta,Math.abs(events[i].position[j]-replay.events[i].position[j]));}
assert.ok(maxDelta<0.005,`CPU runtime version drift ${maxDelta}`);
console.log(JSON.stringify({runtime:'Transformers.js 3.8.1 / ORT Node CPU',calls,alignedTokens:events.map(e=>e.id),maxPositionDifferenceFromPython:maxDelta}));await model.dispose();
