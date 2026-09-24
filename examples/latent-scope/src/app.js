import * as webllm from "@mlc-ai/web-llm";
import { decodeChoice, TOP_LIMIT } from "./signal.js";
import { startTrace, recordToken } from "./trace.js";

const MODEL = "Llama-3.2-1B-Instruct-q4f16_1-MLC";
const HISTORY = 64, CANDIDATES = 8, MAX_TOP_LOGPROBS = TOP_LIMIT;
const $ = id => document.getElementById(id);
const canvas = $("gl");
const gpuState = $("gpuState"), loadBtn = $("loadBtn"), loadPanel = $("loadPanel");
const prompt = $("prompt"), sendBtn = $("sendBtn"), stopBtn = $("stopBtn");
const signal = new Float32Array(HISTORY * CANDIDATES * 4);
const conversation = [];
let engine, busy = false, stopRequested = false, total = 0;
let latestTrace;
let gl, program, texture, uniforms, vao, dirty = true;

const vertex = `#version 300 es
in vec2 position;
void main(){gl_Position=vec4(position,0.,1.);}
`;
const fragment = `#version 300 es
precision highp float;
precision highp sampler2D;
uniform vec2 resolution;
uniform float count;
uniform float selection;
uniform sampler2D dataTex;
out vec4 fragColor;
void main(){
 vec2 uv=gl_FragCoord.xy/resolution;
 float x=floor(uv.x*64.), y=floor((1.-uv.y)*8.);
 float p=texelFetch(dataTex,ivec2(int(x),int(y)),0).r;
 vec2 q=fract(vec2(uv.x*64.,uv.y*8.));
 float edge=smoothstep(.01,.12,min(min(q.x,1.-q.x),min(q.y,1.-q.y)));
 vec3 background=vec3(.025,.075,.11);
 vec3 color=mix(background,vec3(.06,.29,.37),edge*.45);
 float intensity=pow(clamp(p,0.,1.),.56);
 color+=vec3(.20,.72,.57)*intensity*edge;
 if(count>0. && abs(x-selection)<.5){
   color+=vec3(.17,.30,.26)*(1.-smoothstep(.025,.11,min(q.x,1.-q.x)));
 }
 fragColor=vec4(color,1.);
}`;

function shader(type, source) {
  const s = gl.createShader(type); gl.shaderSource(s, source); gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
  return s;
}
function initGraphics() {
  gl = canvas.getContext("webgl2", {antialias:false, alpha:false, powerPreference:"low-power"});
  if (!gl) { $("liveLabel").textContent = "WEBGL2 UNAVAILABLE"; return; }
  program=gl.createProgram();
  gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));
  gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  vao=gl.createVertexArray(); gl.bindVertexArray(vao);
  const buffer=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
  const loc=gl.getAttribLocation(program,"position"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
  texture=gl.createTexture(); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D,texture);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,HISTORY,CANDIDATES,0,gl.RGBA,gl.FLOAT,signal);
  uniforms=Object.fromEntries(["resolution","count","selection","dataTex"].map(n=>[n,gl.getUniformLocation(program,n)]));
  gl.uniform1i(uniforms.dataTex,0);
  dirty=true;requestAnimationFrame(render);
}
function render(t) {
  if (!gl) return;
  const rect=canvas.getBoundingClientRect(), dpr=Math.min(devicePixelRatio||1,2);
  const w=Math.max(1,Math.round(rect.width*dpr)),h=Math.max(1,Math.round(rect.height*dpr));
  if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);dirty=true;}
  if(document.hidden||!dirty){requestAnimationFrame(render);return;}
  dirty=false;
  gl.useProgram(program);gl.bindVertexArray(vao);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);
  gl.uniform2f(uniforms.resolution,w,h);
  gl.uniform1f(uniforms.count,Math.min(total,HISTORY));gl.uniform1f(uniforms.selection,Math.max(0,selectedStep()));
  gl.drawArrays(gl.TRIANGLES,0,6);requestAnimationFrame(render);
}
function upload(rows) {
  // Columns are chronological. On overflow, evict oldest once per token.
  for(let y=0;y<CANDIDATES;y++){
    for(let x=0;x<HISTORY;x++){
      const base=(y*HISTORY+x)*4;
      signal[base]=rows[x]?.[y]??0;
    }
  }
  if(gl){gl.bindTexture(gl.TEXTURE_2D,texture);gl.texSubImage2D(gl.TEXTURE_2D,0,0,0,HISTORY,CANDIDATES,gl.RGBA,gl.FLOAT,signal);}
  dirty=true;
}
const rows=[];
const observations=[];
let pinnedStep=-1;
function selectedStep(){return pinnedStep<0?observations.length-1:Math.min(pinnedStep,observations.length-1);}
function refreshSelection(){
  const index=selectedStep(), item=observations[index], slider=$("stepSlider");
  $("stepControls").hidden=!item;
  if(!item)return;
  slider.max=String(observations.length-1);slider.value=String(index);
  const choice=item.choice;
  showCandidates(choice);
  $("tokenValue").textContent=JSON.stringify(item.token).slice(0,30);
  $("probValue").textContent=(choice.chosen.probability*100).toFixed(1)+"%";
  $("entropyValue").textContent=choice.entropy.toFixed(2)+" bits*";
  $("stepLabel").textContent="STEP "+item.number+" · "+Math.round(item.elapsedMs)+" ms"+(pinnedStep<0?" · LIVE":" · PINNED");
  $("followBtn").hidden=pinnedStep<0;
  dirty=true;
}
function consume(log,elapsedMs) {
  const choice=decodeChoice(log);if(!choice)return;
  rows.push(choice.row);observations.push({choice,token:log.token||"",elapsedMs,number:total+1});
  if(rows.length>HISTORY){rows.shift();observations.shift();if(pinnedStep>=0)pinnedStep=Math.max(0,pinnedStep-1);}
  total++;upload(rows);refreshSelection();
  $("frameLabel").textContent=total+" TOKEN"+(total===1?"":"S");
  $("liveLabel").textContent="LIVE / DECODE";
}
function showCandidates(choice){
  const items=[choice.chosen,...choice.alternatives];
  while(items.length<6)items.push({token:"",probability:0});
  items.push({token:"All other tokens",probability:choice.remaining,other:true});
  const panel=$("candidateInspector");
  panel.replaceChildren(...items.map((x,i)=>{
    const row=document.createElement("div");row.className="candidate-row"+(i===0?" chosen":"")+(x.other?" other":"");
    const meter=document.createElement("span");meter.className="meter";meter.style.width=(x.probability*100).toFixed(2)+"%";
    const label=document.createElement("span");label.className="choice-token";
    label.textContent=i===0?"CHOSEN  "+JSON.stringify(x.token):x.other?x.token:x.token?JSON.stringify(x.token):"—";
    const value=document.createElement("strong");value.className="choice-value";
    value.textContent=(x.probability*100).toFixed(1)+"%";
    row.append(meter,label,value);return row;
  }));
}
function message(role,text) {
  const item=document.createElement("div");item.className="message "+role;
  const who=document.createElement("span");who.className="who";who.textContent=role==="user"?"YOU":"MODEL";
  const p=document.createElement("p");p.textContent=text;
  item.append(who,p);$("messages").append(item);$("messages").scrollTop=$("messages").scrollHeight;return p;
}
function setBusy(value) {
  busy=value;prompt.disabled=value||!engine;sendBtn.disabled=value||!engine;
  stopBtn.hidden=!value;$("composeHint").textContent=value?"Generating locally":"Enter to send · Shift+Enter for a new line";
}
async function load() {
  if(engine)return;
  if(!navigator.gpu){$("loadStatus").textContent="WebGPU is unavailable in this browser. Try a current browser with WebGPU enabled.";return;}
  loadBtn.disabled=true;$("progress").hidden=false;$("loadStatus").textContent="Starting model download…";
  try {
    engine=await webllm.CreateMLCEngine(MODEL,{initProgressCallback:p=>{
      $("loadStatus").textContent=p.text||"Loading…";
      if(Number.isFinite(p.progress))$("progressBar").style.width=Math.max(0,Math.min(100,p.progress*100))+"%";
    }});
    loadPanel.hidden=true;prompt.disabled=false;sendBtn.disabled=false;
    $("composeHint").textContent="Enter to send · Shift+Enter for a new line";
    $("liveLabel").textContent="MODEL READY";prompt.focus();
  }catch(e){
    engine=undefined;loadBtn.disabled=false;
    $("loadStatus").textContent="Load failed: "+String(e?.message||e);
    console.error(e);
  }
}
async function send(event) {
  event.preventDefault();if(!engine||busy)return;
  const input=prompt.value.trim();if(!input)return;
  pinnedStep=-1;
  $("inputPreview").textContent=input.slice(0,80);
  $("prefillValue").textContent="Waiting for first output";
  $("outputPreview").textContent="Decoding…";
  prompt.value="";const userBubble=message("user",input);
  conversation.push({role:"user",content:input});
  const settings={top_logprobs:MAX_TOP_LOGPROBS,max_tokens:256,temperature:.8,frequency_penalty:.1};
  const trace=startTrace({model:MODEL,prompt:input,messages:conversation,settings,startedAt:new Date().toISOString()});
  latestTrace=trace;$("downloadTrace").disabled=true;
  const began=performance.now();
  const target=message("assistant","");
  setBusy(true);stopRequested=false;
  let output="", n=0, firstTokenAt=0;
  try {
    const stream=await engine.chat.completions.create({
      messages:conversation,stream:true,logprobs:true,...settings
    });
    for await(const chunk of stream){
      const choice=chunk.choices?.[0],delta=choice?.delta?.content||"";
      output+=delta;target.textContent=output;$("messages").scrollTop=$("messages").scrollHeight;
      if(delta){
        $("outputPreview").textContent=output.slice(-80);
        if(!firstTokenAt){
          firstTokenAt=performance.now();
          $("prefillValue").textContent=Math.round(firstTokenAt-began)+" ms to first output*";
        }
      }
      const entries=choice?.logprobs?.content||[];
      for(const entry of entries){
        if(!firstTokenAt){
          firstTokenAt=performance.now();
          $("prefillValue").textContent=Math.round(firstTokenAt-began)+" ms to first output*";
        }
        const elapsedMs=performance.now()-began;
        recordToken(trace,entry,elapsedMs);
        consume(entry,elapsedMs);n++;
      }
      if(n>1)$("rateValue").textContent=((n-1)/Math.max(.001,(performance.now()-firstTokenAt)/1000)).toFixed(1)+" tok/s";
      if(stopRequested)break;
    }
    conversation.push({role:"assistant",content:output});
    trace.status=stopRequested?"stopped":"completed";
    if(!output)target.textContent=stopRequested?"Stopped.":"No text returned.";
  }catch(e){
    trace.status="error";trace.error=String(e?.message||e);
    if(output){conversation.push({role:"assistant",content:output});}
    else{
      // The request failed before decoding; allow the same prompt to be retried.
      conversation.pop();userBubble.parentElement.remove();prompt.value=input;
    }
    target.textContent=output+(output?"\n":"")+"Generation error: "+String(e?.message||e);
    if(!output)$("outputPreview").textContent="Generation failed";
    console.error(e);
  }finally{
    trace.output=output;trace.durationMs=Math.round(performance.now()-began);
    $("downloadTrace").disabled=false;
    setBusy(false);$("liveLabel").textContent=total?"PAUSED / LAST STATE":"MODEL READY";
  }
}
$("stepSlider").addEventListener("input",event=>{pinnedStep=Number(event.target.value);refreshSelection();});
$("followBtn").addEventListener("click",()=>{pinnedStep=-1;refreshSelection();});
canvas.addEventListener("pointerdown",event=>{
  if(!observations.length)return;
  const bounds=canvas.getBoundingClientRect();
  const column=Math.max(0,Math.min(HISTORY-1,Math.floor((event.clientX-bounds.left)/bounds.width*HISTORY)));
  if(column>=observations.length)return;
  pinnedStep=column;refreshSelection();
});
document.querySelectorAll("[data-prompt]").forEach(button=>button.addEventListener("click",()=>{
  prompt.value=button.dataset.prompt;prompt.focus();
}));
const chatToggle=$("chatToggle");
chatToggle.addEventListener("click",()=>{
  const collapsed=$("console").classList.toggle("collapsed");
  $("workspace").classList.toggle("chat-minimized",collapsed);
  chatToggle.textContent=collapsed?"Show chat ↓":"Focus diagram ↑";
  chatToggle.setAttribute("aria-expanded",String(!collapsed));
  dirty=true;
});
document.addEventListener("visibilitychange",()=>{dirty=true;});
canvas.addEventListener("webglcontextlost",event=>{
  event.preventDefault();gl=null;$("liveLabel").textContent="GRAPHICS PAUSED";
});
canvas.addEventListener("webglcontextrestored",()=>{
  try{initGraphics();$("liveLabel").textContent=total?"PAUSED / LAST STATE":"MODEL READY";}
  catch(error){$("liveLabel").textContent="SHADER ERROR";console.error(error);}
});
loadBtn.addEventListener("click",load);
$("chatForm").addEventListener("submit",send);
prompt.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();$("chatForm").requestSubmit();}});
stopBtn.addEventListener("click",()=>{stopRequested=true;Promise.resolve(engine?.interruptGenerate?.()).catch(console.error);});
$("downloadTrace").addEventListener("click",()=>{
  if(!latestTrace||busy)return;
  const blob=new Blob([JSON.stringify(latestTrace,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob),link=document.createElement("a");
  link.href=url;link.download="latent-scope-trace-"+latestTrace.startedAt.replace(/[:.]/g,"-")+".json";
  document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
});
if(navigator.gpu){gpuState.textContent="WEBGPU AVAILABLE";gpuState.classList.add("good");}
else{gpuState.textContent="WEBGPU UNAVAILABLE";gpuState.classList.add("bad");loadBtn.disabled=true;}
try{initGraphics();}catch(e){$("liveLabel").textContent="SHADER ERROR";console.error(e);}
