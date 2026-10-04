(()=>{
'use strict';
const art=window.RelationshipArt,viewport=document.querySelector('#viewport'),stage=document.querySelector('#stage');
viewport.append(stage);document.querySelector('.app').remove();
const dialog=document.querySelector('#leaf-detail'),caption=document.querySelector('#map-caption');
document.querySelector('.map-header h1').textContent=MapModel.title;document.querySelector('.map-header>p').textContent=MapModel.type==='relationships'?'关系中的自己':MapModel.type==='traits'?'不同情境中的倾向':MapModel.type==='personal'?'从经历里看见自己':'记录与未知分开看';document.title='知遇测评 · '+MapModel.title;
const embedded=new URLSearchParams(location.search).has('embedded');document.body.classList.toggle('embedded',embedded);
const originalState=JSON.stringify(art.branches.map(b=>b.items.map(it=>it.lit)));
let current=null,cam={x:0,y:0,k:1},moved=false,returnFocus=null,frame=0,drawCount=0;
const pointer=new Map();
const topology=MapModel.topology(art);
// Attach each original title/icon group to its own curved stem, not a floating label.
for(const b of art.branches){
 const p=b.paths[0],anchor=art.at(p.poly,b.anchorRatio!=null?p.total*b.anchorRatio:b.id==='plan'?p.total*.48:b.id==='promise'?p.total*.43:p.total);
 const base=({sproutT:[261.9,49.3],emo:[426.9,84.2],sun:[505.5,233.7],heart:[454.55,383.6],mount:[290.2,459.8],sproutG:[96.75,394.6],coins:[65.8,214.7],shield:[141.6,74.9]})[b.icon];b.headOffset=[anchor[0]-base[0],anchor[1]-base[1]];
 b.head.setAttribute('transform',`translate(${b.headOffset.join(' ')})`);
}

const visible=(node,on)=>{node.style.display=on?'':'none';};
const hideHit=(node,on)=>{visible(node,on);node.setAttribute('tabindex',on?'0':'-1');node.setAttribute('aria-hidden',String(!on));};
function paint(){frame=0;drawCount++;stage.style.transform=`translate(${cam.x}px,${cam.y}px) scale(${cam.k})`;document.querySelector('#zoom-level').value=Math.round(cam.k*100)+'%';}
function requestPaint(){if(!frame)frame=requestAnimationFrame(paint);}
function fit(bounds){const w=viewport.clientWidth,h=viewport.clientHeight;cam.k=Math.min((w-32)/bounds.w,(h-36)/bounds.h,2.7);cam.x=(w-bounds.w*cam.k)/2-bounds.x*cam.k;cam.y=(h-bounds.h*cam.k)/2-bounds.y*cam.k;requestPaint();}
function zoom(factor,x=viewport.clientWidth/2,y=viewport.clientHeight/2){const k=Math.min(3.5,Math.max(.35,cam.k*factor));cam.x=x-(x-cam.x)*k/cam.k;cam.y=y-(y-cam.y)*k/cam.k;cam.k=k;requestPaint();}
function layers(){
 const overview=!current;stage.dataset.mode=overview?"overview":"focus";
 for(const b of art.branches){
  const chosen=b.id===current;
  visible(b.head,overview||chosen);hideHit(b.hit,overview||chosen);
  b.hit.setAttribute('aria-expanded',String(chosen));
  if(overview||chosen){const r=b.head.getBBox();for(const [k,v] of Object.entries({x:r.x+b.headOffset[0]-5,y:r.y+b.headOffset[1]-5,width:r.width+10,height:r.height+10}))b.hit.setAttribute(k,v);}
  visible(b.warm,false);visible(b.shade,overview||chosen);visible(b.fillet,overview||chosen);
  for(const j of b.juncEls)visible(j.g,false);
  for(const bd of b.budEls)visible(bd.bul,false);
  for(const p of b.paths){const on=overview?(p.main||p.vi===1):chosen;for(const s of [...p.gSet,...p.lSet])visible(s.e,on);}
  for(const it of b.items){visible(it.g,chosen);hideHit(it.hit,chosen);}
 }
 for(const p of art.paths.filter(p=>p.stem))for(const s of p.gSet)visible(s.e,false);
 for(const [i,leaf] of art.leaves.entries()){const decorative=leaf.host?.main&&leaf.dist>60&&i%2===0;visible(leaf.pop.parentNode,current?leaf.host?.b?.id===current:decorative);leaf.pop.parentNode.style.opacity=current?'1':'.65';}
 document.querySelector('#gPetals').style.display='none';
 caption.textContent=current?art.branches.find(b=>b.id===current).name+' · 轻触叶片查看含义':MapModel.type==='relationships'?'从一条枝蔓，看看关系中在意的需要':'点击主节点，从一个角度慢慢了解自己';
}
function overview(){current=null;layers();fit({x:25,y:5,w:545,h:553});}
function focusBranch(id){
 const b=art.branches.find(b=>b.id===id);if(!b)return;current=id;layers();
 // Keep the selected branch's original art coordinates and fit its full rooted extent.
 const pts=b.vines.flatMap(v=>v.pts),xs=[258,337,...pts.map(p=>p[0]),b.title[0]+b.headOffset[0]-15,b.title[1]+b.headOffset[0]+14,...b.items.flatMap(it=>[it.b[0]-18,it.x[1]+10])],ys=[242,321,...pts.map(p=>p[1]),b.box[1]+b.headOffset[1]-10,b.title[2]+b.headOffset[1]+14,...b.items.map(it=>it.cy+17)];
 const x=Math.min(...xs)-12,y=Math.min(...ys)-15;fit({x,y,w:Math.max(...xs)-x+12,h:Math.max(...ys)-y+15});
}
function openDetail(id,index){if(current!==id)return;const b=art.branches.find(b=>b.id===id),it=b?.items[index];if(!it)return;
 returnFocus=it.hit;
 if(embedded){parent.postMessage({type:'zhiyu-map-detail',title:it.t,description:it.sub,branch:b.name,route:it.route||(b.dimensionId?'relationship-detail':null),id:it.routeId||b.dimensionId||null},location.origin);return;}
 document.querySelector('#detail-branch').textContent=b.name;document.querySelector('#detail-title').textContent=it.t;document.querySelector('#detail-copy').textContent=it.sub;dialog.showModal();document.querySelector('#close-detail').focus();}
// Cutout leaf silhouettes replace terminal dots only; original branch art stays SVG.
for(const b of art.branches)for(const it of b.items){
 it.bul.style.display='none';const img=document.createElementNS('http://www.w3.org/2000/svg','image');
 img.setAttribute('href','assets/leaf-node.png');
 // Source alpha stalk tip is (25,399) in the 512×427 cutout. Rotate around that exact point.
 const width=24,height=width*427/512;
 img.setAttribute('x',-25/512*width);img.setAttribute('y',-399/427*height);
 img.setAttribute('width',width);img.setAttribute('height',height);img.setAttribute('aria-hidden','true');
 img.setAttribute('transform',`translate(${it.b.join(' ')}) rotate(-75)`);it.g.insertBefore(img,it.tx);
 // Leaf stalk sits exactly at the business path endpoint; labels stay on its right.

}
document.querySelector('#close-detail').addEventListener('click',()=>dialog.close());
dialog.addEventListener('close',()=>returnFocus?.focus({preventScroll:true}));
document.querySelector('.camera-tools').addEventListener('click',e=>{const act=e.target.closest('button')?.dataset.camera;if(!act)return;if(act==='overview')overview();else if(act==='in'||act==='out')zoom(act==='in'?1.2:1/1.2);else{cam.x+=({left:45,right:-45}[act]||0);cam.y+=({up:45,down:-45}[act]||0);requestPaint();}});
viewport.addEventListener('keydown',e=>{if(e.target!==viewport)return;const key=e.key;if(key==='+'||key==='=')zoom(1.2);else if(key==='-')zoom(1/1.2);else if(key==='Home')overview();else if(key.startsWith('Arrow')){cam.x+=({ArrowLeft:40,ArrowRight:-40}[key]||0);cam.y+=({ArrowUp:40,ArrowDown:-40}[key]||0);requestPaint();}else return;e.preventDefault();});
viewport.addEventListener('wheel',e=>{e.preventDefault();const r=viewport.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.002),e.clientX-r.left,e.clientY-r.top);},{passive:false});
viewport.addEventListener('pointerdown',e=>{if(e.button!==0)return;pointer.set(e.pointerId,{x:e.clientX,y:e.clientY});moved=false;});
viewport.addEventListener('pointermove',e=>{
 if(!pointer.has(e.pointerId))return;const old=pointer.get(e.pointerId),next={x:e.clientX,y:e.clientY},dx=next.x-old.x,dy=next.y-old.y;
 if(Math.hypot(dx,dy)>2||moved){moved=true;viewport.classList.add('dragging');viewport.setPointerCapture(e.pointerId);}
 if(pointer.size===2){const other=[...pointer.entries()].find(([id])=>id!==e.pointerId)[1];const dist=Math.hypot(old.x-other.x,old.y-other.y),nd=Math.hypot(next.x-other.x,next.y-other.y),r=viewport.getBoundingClientRect();if(dist>0)zoom(nd/dist,(old.x+other.x)/2-r.left,(old.y+other.y)/2-r.top);cam.x+=dx/2;cam.y+=dy/2;}
 else if(moved){cam.x+=dx;cam.y+=dy;}pointer.set(e.pointerId,next);if(moved)requestPaint();
});
function release(e){pointer.delete(e.pointerId);if(!pointer.size){viewport.classList.remove('dragging');setTimeout(()=>moved=false,0);}}
viewport.addEventListener('pointerup',release);viewport.addEventListener('pointercancel',release);
viewport.addEventListener('click',e=>{if(moved){e.preventDefault();e.stopImmediatePropagation();}},{capture:true});
addEventListener('resize',()=>current?focusBranch(current):overview());
window.MapCamera={overview,focusBranch,openDetail,topology,state:()=>({current,...cam,drawCount,originalState,liveState:JSON.stringify(art.branches.map(b=>b.items.map(it=>it.lit)))})};
Ambient.setContext({quiet:embedded,reduced:new URLSearchParams(location.search).has('still')});overview();
})();
