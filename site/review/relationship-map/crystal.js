/* Opt-in relationship comparison; the published botanical rendering remains the default. */
(()=>{
 if(MapModel.type!=='relationships'||new URLSearchParams(location.search).get('geometry')!=='crystal')return;
 const art=RelationshipArt,NS='http://www.w3.org/2000/svg',C=[297.5,281.5],R=118,L=80;
 document.body.classList.add('crystal');document.documentElement.style.colorScheme=document.body.dataset.themeMode;
 const css=document.createElement('link');css.rel='stylesheet';css.href='crystal.css';document.head.append(css);
 const make=(tag,attrs,parent)=>{const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);parent?.append(e);return e;};
 for(const id of ['gGreen','gLit','gHi','gGlow','gWarm','gShade','gPetals','gLeaves','gJunc'])document.getElementById(id).replaceChildren();
 const green=document.getElementById('gGreen');
 art.paths.length=0;art.leaves.length=0;
 const point=(a,r)=>[C[0]+Math.cos(a)*r,C[1]+Math.sin(a)*r];
 const poly=pts=>{const s=[0];for(let i=1;i<pts.length;i++)s.push(s.at(-1)+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));return {p:pts,s,total:s.at(-1)};};
 function path(b,pts,vi,parent){const q=poly(pts),e=make('path',{d:'M'+pts.map(p=>p.join(',')).join('L'),class:vi?'crystal-twig':'crystal-spine'},green),p={b,vi,poly:q,total:q.total,main:vi===0,parent,attach:parent?.total||0,w:[1.2,1.2],gSet:[{e}],lSet:[]};b.paths.push(p);art.paths.push(p);return p;}
 for(const [i,b] of art.branches.entries()){
  b.angle=-Math.PI/2+i*Math.PI*2/art.branches.length;b.joint=point(b.angle,R);b.paths=[];b.headOffset=[0,0];b.head.replaceChildren();b.head.removeAttribute('transform');
  b.warm=b.shade=b.fillet=make('g',{});b.juncEls=[];b.budEls=[];
  const main=path(b,[point(b.angle,22),b.joint],0);
  make('path',{d:`M${b.joint[0]},${b.joint[1]-5}l5,5l-5,5l-5,-5Z`,class:'crystal-joint'},b.head);
  b.titleEl=make('text',{class:'t-title crystal-title','text-anchor':'middle'},b.head);b.titleEl.textContent=b.name;
  b.items.forEach((it,n)=>{
   const a=b.angle+(n-(b.items.length-1)/2)*Math.PI/4,end=[b.joint[0]+Math.cos(a)*L,b.joint[1]+Math.sin(a)*L];
   it.path=path(b,[b.joint,end],n+1,main);it.path.item=n;it.b=end;it.cy=end[1];
   it.g.replaceChildren();it.bul=make('g',{});
   make('path',{d:`M${end[0]},${end[1]-6}l6,6l-6,6l-6,-6Z`,class:'crystal-terminal'},it.g);
   const centered=Math.abs(end[0]-C[0])<5,left=end[0]<C[0]-5;
   it.tx=make('text',{x:centered?end[0]:end[0]+(left?-13:13),y:centered?end[1]+(end[1]<C[1]?-17:24):end[1]+5,'text-anchor':centered?'middle':left?'end':'start',class:'t-item'},it.g);it.tx.textContent=it.t;
   const box=it.tx.getBBox();it.x=[box.x,box.x+box.width];
   it.hit.setAttribute('x',Math.min(end[0]-14,box.x-5));it.hit.setAttribute('y',Math.min(end[1]-14,box.y-5));it.hit.setAttribute('width',Math.max(end[0]+14,box.x+box.width+5)-Math.min(end[0]-14,box.x-5));it.hit.setAttribute('height',Math.max(end[1]+14,box.y+box.height+5)-Math.min(end[1]-14,box.y-5));
  });
  b.vines=b.paths.map(p=>({pts:p.poly.p}));
 }
 function layout(current){for(const b of art.branches){const pos=current===b.id?[C[0]+Math.cos(b.angle)*R,Math.min(...b.paths.flatMap(p=>p.poly.p.map(q=>q[1])),...b.items.map(it=>it.g.getBBox().y))-30]:point(b.angle,232);b.titleEl.setAttribute('x',pos[0]);b.titleEl.setAttribute('y',pos[1]+(current!==b.id&&Math.abs(Math.sin(b.angle))<.1?-16:6));}}
 function bounds(b){const xs=[],ys=[];for(const p of b.paths)for(const q of p.poly.p){xs.push(q[0]);ys.push(q[1]);}for(const e of [b.head,...b.items.map(it=>it.g)]){const q=e.getBBox();xs.push(q.x,q.x+q.width);ys.push(q.y,q.y+q.height);}const x=Math.min(...xs)-14,y=Math.min(...ys)-14;return {x,y,w:Math.max(...xs)-x+14,h:Math.max(...ys)-y+14};}
 window.RelationshipGeometry={layout,bounds,parameters:{arms:art.branches.length,angle:360/art.branches.length,branchAngle:45,mainRadius:R,childLength:L,ratio:L/R}};
 layout(null);
})();
