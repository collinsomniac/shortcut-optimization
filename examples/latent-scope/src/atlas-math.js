export const MODEL='onnx-community/Llama-3.2-1B-Instruct-ONNX';
export const REVISION='14007543b6dc92de88daf96a9aa85d2f95ace6ef';
export function chatText(p){return '<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+p+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n';}
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export function normalize(a){const n=Math.sqrt(dot(a,a));return Float32Array.from(a,v=>v/Math.max(n,1e-12));}
export function makeProjector(atlas){
 if(atlas.dimensions!==2048||atlas.basis.length!==3)throw Error('Incompatible atlas dimensions');
 const refs=atlas.anchors.map(a=>normalize(a.vector.map((v,i)=>v-atlas.mean[i])));
 return hidden=>{if(hidden.length!==atlas.dimensions||hidden.some(v=>!Number.isFinite(v)))throw Error('Invalid activation');
  const h=normalize(hidden),delta=Float32Array.from(h,(v,i)=>v-atlas.mean[i]),p=atlas.basis.map(row=>dot(delta,row)),unit=normalize(delta);
  return{position:p.map(v=>v/atlas.scale),similarities:refs.map(v=>dot(unit,v)),projectionRetained:Math.min(1,dot(p,p)/Math.max(1e-12,dot(delta,delta)))};
 };
}
export function topCandidates(logits,k=5){let max=-Infinity;for(const v of logits)if(v>max)max=v;let sum=0;const top=[];for(let i=0;i<logits.length;i++){sum+=Math.exp(logits[i]-max);if(top.length<k||logits[i]>logits[top.at(-1)]){top.push(i);top.sort((a,b)=>logits[b]-logits[a]);if(top.length>k)top.pop();}}return top.map(id=>({id,probability:Math.exp(logits[id]-max)/sum}));}
export function validateReplay(d,atlas){
 if(!d||d.schemaVersion!==1||d.atlasVersion!==atlas.version||d.revision!==atlas.revision||d.hook!==atlas.hook)throw Error('Trace uses a different coordinate space or schema');
 if(typeof d.prompt!=='string'||d.prompt.length>20000||!Array.isArray(d.events)||!d.events.length||d.events.length>512)throw Error('Trace needs a prompt and 1–512 events');
 const vector=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(Number.isFinite);
 let previousTime=-1,previousPosition;
 for(const [i,e] of d.events.entries()){
  if(!e||e.step!==i||e.phase!==(i===0?'prefill':'decode')||!Number.isInteger(e.contextPosition)||e.contextPosition<0||e.predictedPosition!==e.contextPosition+1||(i&&e.contextPosition!==previousPosition+1)||!Number.isInteger(e.tokenId)||e.tokenId<0||e.tokenId>=128256||typeof e.token!=='string'||typeof e.text!=='string'||e.text.length>200000||!vector(e.position,3)||!vector(e.similarities,atlas.anchors.length)||!e.similarities.every(v=>Math.abs(v)<=1.00001)||!Number.isFinite(e.projectionRetained)||e.projectionRetained<0||e.projectionRetained>1.00001||!Number.isFinite(e.elapsedMs)||e.elapsedMs<previousTime||!Array.isArray(e.candidates)||e.candidates.length>5)throw Error('Invalid trace measurements');
  let mass=0;const seen=new Set();for(const c of e.candidates){if(!c||!Number.isInteger(c.id)||c.id<0||c.id>=128256||seen.has(c.id)||typeof c.token!=='string'||!Number.isFinite(c.probability)||c.probability<0||c.probability>1)throw Error('Invalid candidate');mass+=c.probability;seen.add(c.id);}if(mass>1.00001)throw Error('Invalid candidate probability mass');
  previousTime=e.elapsedMs;previousPosition=e.contextPosition;
 }
 return d;
}
