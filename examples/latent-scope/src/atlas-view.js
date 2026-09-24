import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const COLORS=['#78e2c1','#b9a6ff','#f5bd77'];
export class AtlasView{
 constructor(host,atlas,onSelect){
  this.host=host;this.atlas=atlas;this.onSelect=onSelect;this.runs=[];this.selected=null;
  this.canvas=document.createElement('canvas');host.append(this.canvas);this.scene=new THREE.Scene();this.camera=new THREE.PerspectiveCamera(42,1,.1,100);this.camera.position.set(1.8,1.25,3.6);
  try{this.renderer=new THREE.WebGLRenderer({canvas:this.canvas,antialias:false,alpha:true,powerPreference:'low-power'});this.renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));}catch{this.canvas.remove();this.canvas=document.createElement('canvas');host.append(this.canvas);this.ctx=this.canvas.getContext('2d');}
  this.canvas.setAttribute('aria-label','3D activation trajectories. Drag to orbit, pinch to zoom, tap a point to inspect.');
  this.controls=new OrbitControls(this.camera,this.canvas);this.controls.enablePan=false;this.controls.minDistance=1.2;this.controls.maxDistance=12;this.controls.addEventListener('change',()=>this.invalidate());
  this.labels=atlas.anchors.map(a=>{const el=document.createElement('span');el.className='anchor-label';el.textContent=a.label;host.append(el);return el;});
  this.scene.add(new THREE.Points(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(atlas.anchors.flatMap(a=>a.position),3)),new THREE.PointsMaterial({color:'#769ab5',size:.07})));
  const axes=[];for(let i=0;i<3;i++){const a=[0,0,0],b=[0,0,0];a[i]=-1.2;b[i]=1.2;axes.push(...a,...b);}
  this.scene.add(new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(axes,3)),new THREE.LineBasicMaterial({color:'#2a4053'})));
  this.trails=new THREE.Group();this.scene.add(this.trails);this.marker=new THREE.Mesh(new THREE.SphereGeometry(.026,8,6),new THREE.MeshBasicMaterial({color:'#fff'}));this.marker.visible=false;this.scene.add(this.marker);
  let down;this.canvas.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY]});
  this.canvas.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>8)return;const b=this.canvas.getBoundingClientRect();let closest,dist=16;for(const r of this.runs)r.events.forEach((event,i)=>{const p=this.screen(event.position);if(!p.visible)return;const d=Math.hypot(p.x-e.clientX+b.left,p.y-e.clientY+b.top);if(d<dist){dist=d;closest={runId:r.id,step:i};}});if(closest)this.onSelect(closest);});
  new ResizeObserver(()=>{const b=host.getBoundingClientRect();this.width=Math.max(1,b.width);this.height=Math.max(1,b.height);this.camera.aspect=this.width/this.height;this.camera.updateProjectionMatrix();if(this.renderer)this.renderer.setSize(this.width,this.height,false);else{const d=Math.min(devicePixelRatio||1,1.5);this.canvas.width=Math.round(this.width*d);this.canvas.height=Math.round(this.height*d);this.ctx.setTransform(d,0,0,d,0,0);}this.invalidate();}).observe(host);
  document.addEventListener('visibilitychange',()=>this.invalidate());this.invalidate();
 }
 reset(){this.camera.position.set(1.8,1.25,3.6);this.controls.target.set(0,0,0);this.controls.update();this.invalidate();}
 screen(pos){const v=new THREE.Vector3(...pos).project(this.camera);return{x:(v.x+1)*this.width/2,y:(1-v.y)*this.height/2,z:v.z,visible:v.z>-1&&v.z<1&&Math.abs(v.x)<1.2&&Math.abs(v.y)<1.2};}
 setRuns(runs,selected){this.runs=runs;this.selected=selected;for(const c of [...this.trails.children]){this.trails.remove(c);c.geometry.dispose();c.material.dispose();}runs.forEach((r,i)=>{const g=new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(r.events.flatMap(e=>e.position),3)),color=COLORS[i%3];this.trails.add(new THREE.Line(g,new THREE.LineBasicMaterial({color,transparent:true,opacity:.5})));this.trails.add(new THREE.Points(g.clone(),new THREE.PointsMaterial({color,size:.035})));});const e=runs.find(r=>r.id===selected?.runId)?.events[selected?.step];this.marker.visible=!!e;if(e)this.marker.position.set(...e.position);this.invalidate();}
 invalidate(){if(this.frame)return;this.frame=requestAnimationFrame(()=>{this.frame=0;this.render();});}
 render(){if(!this.width||document.hidden)return;this.camera.updateMatrixWorld();this.labels.forEach((el,i)=>{const p=this.screen(this.atlas.anchors[i].position);el.style.display=p.visible?'block':'none';el.style.transform=`translate(${p.x}px,${p.y}px) translate(-50%,-150%)`;});if(this.renderer){this.renderer.render(this.scene,this.camera);return;}
  const ctx=this.ctx;ctx.clearRect(0,0,this.width,this.height);const line=(a,b,color)=>{const p=this.screen(a),q=this.screen(b);ctx.strokeStyle=color;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();};
  for(let i=0;i<3;i++){const a=[0,0,0],b=[0,0,0];a[i]=-1.2;b[i]=1.2;line(a,b,'#293e50');}const dots=this.atlas.anchors.map(a=>({...this.screen(a.position),color:'#769ab5',radius:4}));
  this.runs.forEach((r,i)=>r.events.forEach((e,j)=>{if(j)line(r.events[j-1].position,e.position,COLORS[i%3]+'80');const selected=this.selected?.runId===r.id&&this.selected.step===j;dots.push({...this.screen(e.position),color:selected?'#fff':COLORS[i%3],radius:selected?5:2.5});}));
  dots.sort((a,b)=>b.z-a.z).forEach(p=>{if(!p.visible)return;ctx.fillStyle=p.color;ctx.beginPath();ctx.arc(p.x,p.y,p.radius,0,Math.PI*2);ctx.fill();});
 }
}
