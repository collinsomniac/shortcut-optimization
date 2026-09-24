import {AtlasView} from './atlas-view.js';
import {validateReplay} from './atlas-math.js';
const $=id=>document.getElementById(id);
let atlas,view,worker,ready=false,busy=false,runs=[],selected,follow=true,timer,liveId;
const current=()=>runs.find(r=>r.id===selected?.runId);
const status=text=>{$('status').textContent=text;};
function pause(){clearInterval(timer);timer=undefined;$('play').textContent='▶';}
function select(runId,step){selected={runId,step};render();}
function bars(host,items){host.replaceChildren(...items.map(({label,value,text})=>{const row=document.createElement('div');row.className='bar-row';const name=document.createElement('span'),track=document.createElement('span'),fill=document.createElement('i'),number=document.createElement('span');name.textContent=label;name.title=label;track.className='bar-track';fill.style.width=`${Math.max(0,Math.min(1,value))*100}%`;track.append(fill);number.textContent=text;row.append(name,track,number);return row;}));}
function render(){
 const run=current(),events=run?.events||[],e=events[selected?.step];
 $('runSelect').replaceChildren(...runs.map(r=>new Option(`${r.source==='live'?'Live':r.source==='imported'?'Imported':'Recording'} · ${r.prompt.slice(0,36)}`,r.id,false,r.id===selected?.runId)));
 $('scrub').max=Math.max(0,events.length-1);$('scrub').value=selected?.step||0;$('scrub').disabled=!events.length;$('play').disabled=!events.length;$('save').disabled=!events.length;
 $('step').textContent=events.length?`${(selected?.step||0)+1} / ${events.length}`:'0 / 0';$('sourceBadge').textContent=run?.source==='live'?'CAPTURED · WEBGPU':run?.source==='imported'?'IMPORTED TRACE':run?'RECORDED · CPU':'NO RUN';
 $('shownPrompt').textContent=run?.prompt||'Each prompt starts a fresh context.';$('reply').textContent=e?.text||'';
 $('phase').textContent=e?`${e.phase.toUpperCase()} · ${e.contextPosition} → ${e.predictedPosition}`:'WAITING';$('selectedToken').textContent=e?.token||'Waiting for captured activation';$('pointCount').textContent=`${events.length} points`;
 $('retained').textContent=e?`${(100*e.projectionRetained).toFixed(1)}%`:'—';$('firstOutput').textContent=events.length?`${(events[0].elapsedMs/1000).toFixed(2)} s`:'—';
 const duration=e?e.elapsedMs-events[0].elapsedMs:0;$('rate').textContent=duration>0?`${(selected.step*1000/duration).toFixed(1)} t/s`:'—';
 bars($('similarities'),e?atlas.anchors.map((a,i)=>({label:a.label,value:(e.similarities[i]+1)/2,text:e.similarities[i].toFixed(2)})).sort((a,b)=>b.value-a.value):[]);bars($('candidates'),(e?.candidates||[]).map(c=>({label:c.token,value:c.probability,text:`${(100*c.probability).toFixed(1)}%`})));
 view.setRuns(($('compare').checked?runs:run?[run]:[]).map(r=>({...r,events:r.id===selected?.runId?r.events.slice(0,selected.step+1):r.events})),selected);
}
function addRun(data){pause();const run={...data,id:crypto.randomUUID()};runs.push(run);if(runs.length>3)runs.shift();follow=true;select(run.id,Math.max(0,run.events.length-1));return run;}
function controls(){ $('load').hidden=!!worker;$('unload').hidden=!worker;$('prompt').disabled=!ready||busy;$('send').disabled=!ready||busy;$('stop').hidden=!busy; }
function release(){worker?.terminate();worker=undefined;ready=false;busy=false;liveId=undefined;controls();}
async function loadReplay(name){try{if(busy)return;const data=validateReplay(await(await fetch(`./atlas/replay-${name}.json`)).json(),atlas);const r=addRun({...data,source:'recorded'});select(r.id,0);status('Measured CPU recording. Play or scrub to inspect each token.');play();}catch(e){status(e.message);}}
function play(){if(timer){pause();return;}const r=current();if(!r?.events.length)return;follow=false;if(selected.step===r.events.length-1)selected.step=0;$('play').textContent='Ⅱ';render();timer=setInterval(()=>{const r=current();if(!r||selected.step>=r.events.length-1){pause();return;}select(r.id,selected.step+1);},120);}
$('load').onclick=()=>{status('Preparing WebGPU model…');worker=new Worker(new URL('./atlas-worker.js',import.meta.url),{type:'module'});controls();worker.onerror=e=>{status(`Worker failed: ${e.message}`);release();};worker.onmessage=({data:m})=>{if(m.type==='status')status(m.text);if(m.type==='ready'){ready=true;controls();status('Ready. Each generated token captures one middle-layer residual state.');}if(m.type==='error'){status(m.message);release();}if(m.type==='token'){const r=runs.find(r=>r.id===liveId);if(!r)return;r.events.push(m.event);if(follow)selected={runId:r.id,step:r.events.length-1};render();}if(m.type==='done'){busy=false;controls();if(!m.failed)status('Capture complete. Scrub, compare, or save this trace.');}};worker.postMessage({type:'load'});};
$('unload').onclick=()=>{release();status('Model released. Captured traces remain available.');};
$('form').onsubmit=e=>{e.preventDefault();const prompt=$('prompt').value.trim();if(!ready||busy||!prompt)return;const r=addRun({schemaVersion:1,source:'live',prompt,events:[],atlasVersion:atlas.version,revision:atlas.revision,hook:atlas.hook});liveId=r.id;busy=true;controls();status('Prefilling prompt…');worker.postMessage({type:'generate',prompt});};
$('stop').onclick=()=>{worker?.postMessage({type:'stop'});status('Stopping after the current token…');};
$('scrub').oninput=()=>{pause();follow=false;select(selected.runId,Number($('scrub').value));};$('play').onclick=play;
$('runSelect').onchange=()=>{pause();follow=false;const r=runs.find(r=>r.id===$('runSelect').value);select(r.id,Math.max(0,r.events.length-1));};$('compare').onchange=render;
$('follow').onclick=()=>{pause();follow=true;const r=runs.find(r=>r.id===liveId)||current();if(r)select(r.id,Math.max(0,r.events.length-1));};$('resetView').onclick=()=>view.reset();
$('chatToggle').onclick=()=>{const hidden=document.querySelector('.shell').classList.toggle('chat-hidden');$('chatToggle').textContent=hidden?'Show text':'Hide text';$('chatToggle').setAttribute('aria-expanded',String(!hidden));};
$('save').onclick=()=>{const r=current(),url=URL.createObjectURL(new Blob([JSON.stringify(r)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='latent-scope-trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
$('import').onchange=async()=>{try{const f=$('import').files[0];if(!f)return;if(busy)throw Error('Finish capture before importing.');if(f.size>5e6)throw Error('Trace exceeds 5 MB.');const r=validateReplay(JSON.parse(await f.text()),atlas);addRun({...r,source:'imported'});status('Imported trace in matching coordinates.');}catch(e){status(e.message);}finally{$('import').value='';}};
$('aboutOpen').onclick=()=>$('about').showModal();$('aboutClose').onclick=()=>$('about').close();
try{atlas=await(await fetch('./atlas/reference-atlas.json')).json();view=new AtlasView($('map'),atlas,s=>{pause();follow=false;select(s.runId,s.step);});$('atlasVersion').textContent=atlas.version;$('validation').textContent=`Calibration: 48 reference prompts; ${atlas.validation.heldoutCorrect}/${atlas.validation.heldoutCount} held-out prompt category matches. Patched-versus-original logits max difference: ${atlas.validation.logitsMaxAbsDifference}. This small test does not validate generated-token semantics or GPU parity.`;document.querySelectorAll('[data-replay]').forEach(b=>b.onclick=()=>loadReplay(b.dataset.replay));await loadReplay('ocr');}catch(e){status(`Atlas unavailable: ${e.message}`);$('load').disabled=true;}
