(() => {
  "use strict";
  const W=9,H=9;
  const DIRS=[
    {name:"north",dx:0,dy:-1,glyph:"▲"},
    {name:"east",dx:1,dy:0,glyph:"▶"},
    {name:"south",dx:0,dy:1,glyph:"▼"},
    {name:"west",dx:-1,dy:0,glyph:"◀"}
  ];
  const ACTIONS=["turn_left","turn_right","forward","pickup","drop","toggle","wait"];
  const walls=new Set();
  const k=(x,y)=>x+","+y;
  for(let x=0;x<W;x++){walls.add(k(x,0));walls.add(k(x,H-1));}
  for(let y=0;y<H;y++){walls.add(k(0,y));walls.add(k(W-1,y));}
  for(let y=1;y<H-1;y++) if(y!==4) walls.add(k(4,y));

  const initial=()=>({
    mission:"Collect the yellow key, unlock the gate, pick up the blue package, and deliver it to the green dock.",
    agent:{x:1,y:1,dir:1},
    key:{x:2,y:6,collected:false},
    gate:{x:4,y:4,locked:true,open:false},
    package:{x:6,y:2,collected:false,delivered:false},
    dock:{x:7,y:7},
    inventory:{key:false,package:false},
    stepCount:0,lastAction:null,lastResult:"reset",done:false,reward:0
  });
  let s=initial();

  const isWall=(x,y)=>walls.has(k(x,y));
  const front=()=>{const d=DIRS[s.agent.dir];return{x:s.agent.x+d.dx,y:s.agent.y+d.dy};};
  function tileAt(x,y){
    if(x<0||y<0||x>=W||y>=H)return{type:"outside"};
    if(isWall(x,y))return{type:"wall"};
    if(x===s.gate.x&&y===s.gate.y)return{type:"gate",locked:s.gate.locked,open:s.gate.open};
    if(!s.key.collected&&x===s.key.x&&y===s.key.y)return{type:"key",color:"yellow"};
    if(!s.package.collected&&!s.package.delivered&&x===s.package.x&&y===s.package.y)return{type:"package",color:"blue"};
    if(x===s.dock.x&&y===s.dock.y)return{type:"dock",color:"green"};
    return{type:"floor"};
  }
  function localView(radius=2){
    const cells=[];
    for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){
      cells.push({dx,dy,...tileAt(s.agent.x+dx,s.agent.y+dy)});
    }
    return cells;
  }
  function observation(){
    const p=front();
    return{
      mission:s.mission,direction:DIRS[s.agent.dir].name,inventory:{...s.inventory},
      local_view:localView(2),front_cell:tileAt(p.x,p.y),step_count:s.stepCount,
      last_action:s.lastAction,last_result:s.lastResult,done:s.done
    };
  }
  function fullState(){return JSON.parse(JSON.stringify({...s,walls:[...walls]}));}
  function availableActions(){return s.done?[]:[...ACTIONS];}
  function step(action){
    if(!ACTIONS.includes(action))throw new Error("Unknown action: "+action);
    if(s.done)return{observation:observation(),reward:0,done:true,info:{result:"already_done"}};
    s.stepCount++;s.lastAction=action;s.reward=-0.01;let result="ok";
    if(action==="turn_left")s.agent.dir=(s.agent.dir+3)%4;
    else if(action==="turn_right")s.agent.dir=(s.agent.dir+1)%4;
    else if(action==="forward"){
      const p=front(),blocked=isWall(p.x,p.y)||(p.x===s.gate.x&&p.y===s.gate.y&&!s.gate.open);
      if(blocked)result="blocked";else{s.agent.x=p.x;s.agent.y=p.y;}
    } else if(action==="pickup"){
      const p=front();
      if(!s.key.collected&&p.x===s.key.x&&p.y===s.key.y){
        s.key.collected=true;s.inventory.key=true;s.reward+=0.15;result="key_collected";
      } else if(!s.package.collected&&!s.package.delivered&&p.x===s.package.x&&p.y===s.package.y){
        s.package.collected=true;s.inventory.package=true;s.reward+=0.2;result="package_collected";
      } else result="nothing_to_pickup";
    } else if(action==="toggle"){
      const p=front();
      if(p.x===s.gate.x&&p.y===s.gate.y){
        if(s.gate.locked){
          if(s.inventory.key){s.gate.locked=false;s.gate.open=true;s.reward+=0.2;result="gate_unlocked";}
          else result="gate_locked_need_key";
        } else {s.gate.open=!s.gate.open;result=s.gate.open?"gate_opened":"gate_closed";}
      } else result="nothing_to_toggle";
    } else if(action==="drop"){
      const p=front();
      if(s.inventory.package&&p.x===s.dock.x&&p.y===s.dock.y){
        s.inventory.package=false;s.package.delivered=true;s.done=true;s.reward+=1;result="package_delivered";
      } else result="cannot_drop_here";
    } else if(action==="wait")result="waited";
    if(["blocked","nothing_to_pickup","nothing_to_toggle","gate_locked_need_key","cannot_drop_here"].includes(result))s.reward-=0.04;
    s.lastResult=result;render();
    return{observation:observation(),reward:s.reward,done:s.done,info:{result}};
  }
  function reset(){s=initial();render();return observation();}
  function glyph(x,y){
    if(x===s.agent.x&&y===s.agent.y)return DIRS[s.agent.dir].glyph;
    const t=tileAt(x,y);
    if(t.type==="key")return"🔑";if(t.type==="package")return"📦";if(t.type==="dock")return"🟩";
    if(t.type==="gate")return s.gate.open?"":"🚪";return"";
  }
  function render(){
    const grid=document.getElementById("grid");grid.innerHTML="";
    for(let y=0;y<H;y++)for(let x=0;x<W;x++){
      const t=tileAt(x,y),div=document.createElement("div");
      div.className="cell "+(t.type==="wall"?"wall ":"")+(t.type==="dock"?"dock ":"")+(t.type==="gate"?"gate ":"")+(t.type==="gate"&&s.gate.open?"open ":"")+(x===s.agent.x&&y===s.agent.y?"agent":"");
      div.textContent=glyph(x,y);div.title=x+","+y+": "+t.type;grid.appendChild(div);
    }
    document.getElementById("status").innerHTML=
      "<span>Step: <b>"+s.stepCount+"</b></span><span>Key: <b>"+(s.inventory.key?"yes":"no")+
      "</b></span><span>Package: <b>"+(s.inventory.package?"yes":"no")+
      "</b></span><span>Gate: <b>"+(s.gate.locked?"locked":s.gate.open?"open":"closed")+
      "</b></span><span>Last: <b>"+s.lastResult+"</b></span>";
    document.getElementById("observation").textContent=JSON.stringify(observation(),null,2);
  }
  const labels={turn_left:"↶ Left",turn_right:"↷ Right",forward:"↑ Forward",pickup:"📥 Pickup",drop:"📤 Drop",toggle:"🚪 Toggle",wait:"⏸ Wait"};
  const controls=document.getElementById("controls");
  for(const action of ACTIONS){const b=document.createElement("button");b.textContent=labels[action];b.onclick=()=>step(action);controls.appendChild(b);}
  const rb=document.createElement("button");rb.textContent="↺ Reset";rb.onclick=reset;controls.appendChild(rb);
  window.addEventListener("keydown",e=>{
    const m={ArrowLeft:"turn_left",ArrowRight:"turn_right",ArrowUp:"forward",p:"pickup",P:"pickup",d:"drop",D:"drop",t:"toggle",T:"toggle"," ":"wait",r:"reset",R:"reset"};
    const a=m[e.key];if(!a)return;e.preventDefault();a==="reset"?reset():step(a);
  });
  window.courierGrid={getObservation:observation,getFullState:fullState,getAvailableActions:availableActions,step,reset};
  render();
})();