(()=>{
'use strict';
const art=window.RelationshipArt,viewport=document.querySelector('#viewport'),stage=document.querySelector('#stage');
viewport.append(stage);document.querySelector('.app').remove();
const dialog=document.querySelector('#leaf-detail'),caption=document.querySelector('#map-caption');
document.querySelector('.map-header h1').textContent=MapModel.title;document.querySelector('.map-header>p').textContent=MapModel.type==='relationships'?'关系中的自己':MapModel.type==='traits'?'不同情境中的倾向':MapModel.type==='personal'?'从经历里看见自己':MapModel.type==='structure'?'中性示例 · 不代表测量结果':'记录与未知分开看';document.title='知遇测评 · '+MapModel.title;
const embedded=new URLSearchParams(location.search).has('embedded');document.body.classList.toggle('embedded',embedded);
const geometric=window.RelationshipGeometry;
const botanical=MapModel.type==='relationships'&&!geometric;document.body.classList.toggle('relationship-art',botanical);
if(botanical)document.documentElement.style.colorScheme=document.body.dataset.themeMode;
const originalState=JSON.stringify(art.branches.map(b=>b.items.map(it=>it.lit)));
let focusScale=1,current=null,cam={x:0,y:0,k:1},moved=false,returnFocus=null,frame=0,drawCount=0;
const pointer=new Map();
const geometryTopology=MapModel.geometryTopology(art),semantic=MapSemantics;
const depthLimit=()=>!current?1:semantic.research?Math.min(6,Math.max(2,2+Math.floor(Math.log(cam.k/focusScale)/Math.log(1.2)+.02))):2;
// Attach each original title/icon group to its own curved stem, not a floating label.
for(const b of art.branches){
 if(geometric)continue;
 const p=b.paths[0],anchor=art.at(p.poly,b.anchorRatio!=null?p.total*b.anchorRatio:b.id==='plan'?p.total*(botanical?.75:.48):b.id==='promise'?p.total*.43:p.total);
 if(botanical&&b.id==='money'){
  // A short continuation of the same stem gives the compact heading breathing room above its first leaf.
  const end=anchor.slice();anchor[0]-=2;anchor[1]-=24;
  b.nodeLink=document.createElementNS('http://www.w3.org/2000/svg','path');
  b.nodeLink.setAttribute('d',`M${end.join(',')}Q${end[0]-1},${end[1]-12} ${anchor.join(',')}`);
  b.nodeLink.setAttribute('fill','none');b.nodeLink.setAttribute('stroke',b.vc[0]);b.nodeLink.setAttribute('stroke-width','1.2');
  document.querySelector('#gGreen').append(b.nodeLink);
 }
 const base=({sproutT:[261.9,49.3],emo:[426.9,84.2],sun:[505.5,233.7],heart:[454.55,383.6],mount:botanical?[304.4,459.8]:[290.2,459.8],sproutG:[96.75,394.6],coins:[65.8,214.7],shield:[141.6,74.9]})[b.icon];b.headOffset=[anchor[0]-base[0],anchor[1]-base[1]];
 b.head.setAttribute('transform',`translate(${b.headOffset.join(' ')})`);
 if(botanical){
  // Replace only the old flared root segment with a tapered continuation to the smaller center.
  const start=p.poly.p[0],next=art.at(p.poly,1),dx=start[0]-297.5,dy=start[1]-281.5,d=Math.hypot(dx,dy);
  const ux=dx/d,uy=dy/d,tl=Math.hypot(next[0]-start[0],next[1]-start[1]),tx=(next[0]-start[0])/tl,ty=(next[1]-start[1])/tl;
  const inner=[297.5+ux*26,281.5+uy*26],reach=d-26,c1=[inner[0]+ux*reach/3,inner[1]+uy*reach/3],c2=[start[0]-tx*reach/3,start[1]-ty*reach/3];
  const join=p.gSet.find(s=>s.a>0).a+1,points=[];
  for(let i=0;i<=16;i++){const t=i/16,q=1-t;points.push([q*q*q*inner[0]+3*q*q*t*c1[0]+3*q*t*t*c2[0]+t*t*t*start[0],q*q*q*inner[1]+3*q*q*t*c1[1]+3*q*t*t*c2[1]+t*t*t*start[1]]);}
  for(let v=1;v<join;v++)points.push(art.at(p.poly,v));points.push(art.at(p.poly,join));
  const core=p.gSet.find(s=>s.a>0&&Number(s.e.getAttribute('stroke-opacity'))>.9),half=Number(core.e.getAttribute('stroke-width'))/2,left=[],right=[];
  for(let i=0;i<points.length;i++){
   const [x,y]=points[i],before=points[Math.max(0,i-1)],after=points[Math.min(points.length-1,i+1)],len=Math.hypot(after[0]-before[0],after[1]-before[1]),nx=-(after[1]-before[1])/len,ny=(after[0]-before[0])/len,t=i/(points.length-1),width=.65+(half-.65)*t*t*(3-2*t);
   left.push([x+nx*width,y+ny*width]);right.push([x-nx*width,y-ny*width]);
  }
  b.rootLink=document.createElementNS('http://www.w3.org/2000/svg','path');b.rootLink.setAttribute('class','root-join');
  b.rootLink.setAttribute('d','M'+[...left,...right.reverse()].map(q=>q.join(',')).join('L')+'Z');
  b.rootLink.setAttribute('fill',core.e.getAttribute('stroke'));b.rootLink.setAttribute('fill-opacity','.96');
  document.querySelector('#gGreen').prepend(b.rootLink);
  for(const segment of p.gSet)if(segment.a===0)segment.rootReplaced=true;
  // Preserve the existing shadow farther along the branch, without its old round cap around the center.
  const shadow=[];for(let v=join+8;v<=100;v+=2)shadow.push(art.at(p.poly,v));
  b.shade.setAttribute('d','M'+shadow.map(q=>q.join(',')).join('L'));

 }

}

if(botanical){
 const label=document.createElementNS('http://www.w3.org/2000/svg','text');
 label.setAttribute('class','root-label');label.setAttribute('x','297.5');label.setAttribute('y','281.5');label.textContent='我';
 document.querySelector('.orb-svg').append(label);
}
function alignHead(b){
 // Titles share an eight-unit gap and optical center with their icon. The plan group faces left into its natural clearing.
 const icon=b.iconWrap.querySelector('.ic-g').getBBox(),title=b.titleEl.getBBox();
 const x=b.id==='plan'?icon.x-8-title.width:icon.x+icon.width+8;
 b.titleEl.setAttribute('transform',`translate(${x-title.x} ${icon.y+icon.height/2-title.y-title.height/2})`);
}
const visible=(node,on)=>{node.style.display=on?'':'none';};
const hideHit=(node,on)=>{visible(node,on);node.setAttribute('tabindex',on?'0':'-1');node.setAttribute('aria-hidden',String(!on));};
function paint(){frame=0;drawCount++;stage.style.setProperty('--map-scale',cam.k);layers();if(semantic.research){for(const b of art.branches)for(const it of b.items)it.tx.style.fontSize=Math.min(14,16/cam.k)+'px';for(const n of semantic.nodes.filter(n=>n.element))n.element.querySelector('text').style.fontSize=Math.min(11,12/cam.k)+'px';}stage.style.transform=`translate(${cam.x}px,${cam.y}px) scale(${cam.k})`;document.querySelector('#zoom-level').value=Math.round(cam.k*100)+'%';}
function requestPaint(){if(!frame)frame=requestAnimationFrame(paint);}
function fit(bounds){const w=viewport.clientWidth,h=viewport.clientHeight;cam.k=Math.min((w-32)/bounds.w,(h-36)/bounds.h,2.7);cam.x=(w-bounds.w*cam.k)/2-bounds.x*cam.k;cam.y=(h-bounds.h*cam.k)/2-bounds.y*cam.k;requestPaint();}
function zoom(factor,x=viewport.clientWidth/2,y=viewport.clientHeight/2){const k=Math.min(semantic.research?8:3.5,Math.max(.35,cam.k*factor));cam.x=x-(x-cam.x)*k/cam.k;cam.y=y-(y-cam.y)*k/cam.k;cam.k=k;requestPaint();}
function layers(){
 const overview=!current,level=depthLimit();if(geometric)geometric.layout(current);stage.dataset.depth=level;stage.dataset.mode=overview?"overview":"focus";
 for(const b of art.branches){
  const chosen=b.id===current;
  visible(b.head,overview||chosen);hideHit(b.hit,overview||chosen);
  b.hit.setAttribute('aria-expanded',String(chosen));
  if(overview||chosen){if(botanical)alignHead(b);const r=b.head.getBBox();for(const [k,v] of Object.entries({x:r.x+b.headOffset[0]-5,y:r.y+b.headOffset[1]-5,width:r.width+10,height:r.height+10}))b.hit.setAttribute(k,v);}
  if(b.rootLink)visible(b.rootLink,overview||chosen);if(b.nodeLink)visible(b.nodeLink,overview||chosen);
  visible(b.warm,false);visible(b.shade,overview||chosen);visible(b.fillet,!botanical&&(overview||chosen));
  for(const j of b.juncEls)visible(j.g,false);
  for(const bd of b.budEls)visible(bd.bul,false);
  for(const p of b.paths){const on=overview?(semantic.research?p.semanticNode.depth===1:(botanical||geometric||p.main||p.vi===1)):chosen&&p.semanticNode.depth<=level;for(const s of [...p.gSet,...p.lSet])visible(s.e,on&&!s.rootReplaced);}
  for(const it of b.items){const on=chosen&&it.semanticNode.depth<=level;visible(it.g,on);hideHit(it.hit,on);it.hit.dataset.node=it.semanticNode.id;it.hit.dataset.depth=it.semanticNode.depth;if(geometric&&on){const r=it.g.getBBox(),w=Math.max(r.width+10,44/cam.k),h=Math.max(r.height+10,44/cam.k);it.hit.setAttribute('x',r.x+r.width/2-w/2);it.hit.setAttribute('y',r.y+r.height/2-h/2);it.hit.setAttribute('width',w);it.hit.setAttribute('height',h);}if(semantic.research){const y=Math.min(it.b[1]-24,it.cy-12);it.hit.setAttribute('y',y);it.hit.setAttribute('height',Math.max(it.b[1]+8,it.cy+12)-y);}}
 }
 for(const n of semantic.nodes.filter(n=>n.element))visible(n.element,n.branch===current&&n.depth<=level);
 for(const p of art.paths.filter(p=>p.stem))for(const s of p.gSet)visible(s.e,false);
 for(const [i,leaf] of art.leaves.entries()){const decorative=botanical?Boolean(leaf.host?.b):leaf.host?.main&&leaf.dist>60&&i%2===0;visible(leaf.pop.parentNode,current?leaf.host?.b?.id===current&&(!semantic.research||leaf.host.semanticNode.depth<=level):decorative);leaf.pop.parentNode.style.opacity=current||botanical?'1':'.65';}
 document.querySelector('#gPetals').style.display='none';
 if(botanical){
  // Do not leave a cropped fragment of the root button at the edge of a focused reading area.
  const root=document.querySelector('.orb'),r=Math.min(52*cam.k,44)/2,cx=cam.x+297.5*cam.k,cy=cam.y+281.5*cam.k;
  const on=overview||(cx-r>=6&&cy-r>=6&&cx+r<=viewport.clientWidth-6&&cy+r<=viewport.clientHeight-6);
  visible(root,on);root.setAttribute('tabindex',on?'0':'-1');root.setAttribute('aria-hidden',String(!on));
 }

 caption.textContent=semantic.research?(current?'结构样例 · 已展开至第 '+level+' 层 · 放大继续展开':'中性结构样例 · 深度 2 / 3 / 5 / 6，不代表心理维度'):current?art.branches.find(b=>b.id===current).name+' · 轻触叶片查看含义':MapModel.type==='relationships'?'从一条枝蔓，看看关系中在意的需要':'点击主节点，从一个角度慢慢了解自己';
}
function overview(){current=null;layers();fit(semantic.research?{x:80,y:130,w:460,h:330}:{x:25,y:5,w:545,h:553});}
function focusBranch(id){
 const b=art.branches.find(b=>b.id===id);if(!b)return;current=id;layers();
 if(geometric){fit(geometric.bounds(b));focusScale=cam.k;return;}
 if(botanical){
  // Fit the branch and its reading targets, not the root disc or the unselected map.
  const pts=b.vines.flatMap(v=>v.pts),head=b.head.getBBox(),xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);
  xs.push(head.x+b.headOffset[0],head.x+head.width+b.headOffset[0]);
  ys.push(head.y+b.headOffset[1],head.y+head.height+b.headOffset[1]);
  for(const it of b.items){const r=it.g.getBBox();xs.push(r.x,r.x+r.width);ys.push(r.y,r.y+r.height);}
  const x=Math.min(...xs)-12,y=Math.min(...ys)-12;fit({x,y,w:Math.max(...xs)-x+12,h:Math.max(...ys)-y+12});focusScale=cam.k;return;
 }
 // Other map models retain their original framing.
 const pts=b.vines.flatMap(v=>v.pts),xs=[258,337,...pts.map(p=>p[0]),b.title[0]+b.headOffset[0]-15,b.title[1]+b.headOffset[0]+14,...b.items.flatMap(it=>[it.b[0]-18,it.x[1]+10])],ys=[242,321,...pts.map(p=>p[1]),b.box[1]+b.headOffset[1]-10,b.title[2]+b.headOffset[1]+14,...b.items.map(it=>it.cy+17)];
 const x=Math.min(...xs)-12,y=Math.min(...ys)-15;fit({x,y,w:Math.max(...xs)-x+12,h:Math.max(...ys)-y+15});focusScale=cam.k;
}
function openDetail(id,index){if(current!==id)return;const b=art.branches.find(b=>b.id===id),it=b?.items[index];if(!it||it.semanticNode.depth>depthLimit())return;
 returnFocus=it.hit;
 if(embedded){parent.postMessage({type:'zhiyu-map-detail',title:it.t,description:it.sub,branch:b.name,route:it.route||(b.dimensionId?'relationship-detail':null),id:it.routeId||b.dimensionId||null},location.origin);return;}
 document.querySelector('#detail-branch').textContent=b.name;document.querySelector('#detail-title').textContent=it.t;document.querySelector('#detail-copy').textContent=it.sub+(semantic.research?' 父节点：'+semantic.by.get(it.semanticNode.parent).label+'；真实深度：'+it.semanticNode.depth+'。'+(it.semanticNode.pair?'当前状态：'+semantic.stateLabel(it.semanticNode)+'。A、B 独立记录，可同时存在，不要求总和为 100%。':''):'');dialog.showModal();document.querySelector('#close-detail').focus();}
// Keep relationship terminal leaves in the source SVG vocabulary; other models retain their approved cutout.
for(const b of art.branches)for(const it of b.items){
 if(geometric)continue;
 it.bul.style.display='none';
 if(botanical){
  if(b.id==='money'&&it.t==='现实保障')it.tx.setAttribute('transform','translate(0 -4)');
  const leaf=document.createElementNS('http://www.w3.org/2000/svg','image');
  leaf.setAttribute('class','terminal-leaf');leaf.setAttribute('aria-hidden','true');
  leaf.setAttribute('href','assets/terminal-leaf.svg');
  // Asset viewBox -14 -24 20 26 puts the stalk tip at (0,0), exactly on the path endpoint.
  leaf.setAttribute('x',it.b[0]-14);leaf.setAttribute('y',it.b[1]-24);
  leaf.setAttribute('width','20');leaf.setAttribute('height','26');
  it.g.insertBefore(leaf,it.tx);continue;
 }
 const img=document.createElementNS('http://www.w3.org/2000/svg','image');
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
let lastSize=[viewport.clientWidth,viewport.clientHeight],resizeTimer;
addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{const size=[viewport.clientWidth,viewport.clientHeight];if(size.some(v=>v<120)||size.every((v,i)=>v===lastSize[i]))return;if(current){const ratio=cam.k/focusScale,cx=(lastSize[0]/2-cam.x)/cam.k,cy=(lastSize[1]/2-cam.y)/cam.k;focusBranch(current);zoom(ratio);cam.x=size[0]/2-cx*cam.k;cam.y=size[1]/2-cy*cam.k;requestPaint();}else overview();lastSize=size;},100);});
window.MapCamera={overview,focusBranch,openDetail,geometryTopology,get topology(){return semantic.snapshot();},semantic:semantic.snapshot,inspectNode(id){const n=semantic.by.get(id);if(!n||!n.branch)return;focusBranch(n.branch);zoom(Math.pow(1.2,Math.max(0,n.depth-2)));if(n.point){cam.x=viewport.clientWidth/2-(n.point[0]+(n.type==='terminal'?45:0))*cam.k;cam.y=viewport.clientHeight/2-n.point[1]*cam.k;}requestPaint();},state:()=>({current,depth:depthLimit(),...cam,drawCount,originalState,liveState:JSON.stringify(art.branches.map(b=>b.items.map(it=>it.lit)))})};
if(botanical||geometric)document.fonts.ready.then(requestPaint);
Ambient.setContext({quiet:embedded,reduced:new URLSearchParams(location.search).has('still')});overview();
})();
