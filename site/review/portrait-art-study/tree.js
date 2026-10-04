(() => {
'use strict';
const $=s=>document.querySelector(s),NS='http://www.w3.org/2000/svg',G=TreeGeometry;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const positions = [[83,68],[185,26],[318,88],[352,222],[305,361],[181,420],[55,373],[30,218]];
  const names = ['风险兜底','时间陪伴','情绪支持','自由空间','亲密承诺','规划协商','成长认可','金钱资源'];
  const relationIds = ['risk','time','emotion','space','commitment','planning','growth','money'];
  const facetNames = ['能做到','愿投入','自己需要','边界'];
  const relations = names.map((name,i) => ({id:relationIds[i],name,p:positions[i],kind:'fixed',recorded:[2,3].includes(i),leaves:facetNames.map((name,j)=>({id:'f'+j,name,recorded:i===3&&j===2||i===2&&j===1,kind:'fixed'}))}));
  const factorNames = ['乐群','推理','情绪稳定','支配','活泼','规则意识','社交大胆','敏感','警觉','抽象','私密','忧虑','开放变化','自立','自律','紧张'];
  const codes = ['A','B','C','E','F','G','H','I','L','M','N','O','Q1','Q2','Q3','Q4'];
  // Sixteen genuine factors, each an independent branch; no invented aggregate dimensions.
  const factorAnchors=[[50,-256],[131,-209],[221,-154],[224,-63],[220,27],[195,113],[144,189],[69,255],[-39,264],[-123,214],[-187,149],[-224,65],[-228,-25],[-206,-114],[-155,-189],[-67,-254]];
  const traits=codes.map((code,i)=>({id:'group'+Math.floor(i/4)+'/'+code,shortId:code,name:code+' '+factorNames[i],p:[195+factorAnchors[i][0],230+factorAnchors[i][1]],kind:'bipolar',recorded:false,leaves:[]}));
  const personal = [
    {id:'rhythm',name:'相处节奏',p:[67,75],kind:'independent',recorded:true,leaves:[{id:'company',name:'需要陪伴',kind:'independent',recorded:true},{id:'alone',name:'需要独处',kind:'independent',recorded:true}]},
    {id:'visibility',name:'记录可见性',p:[323,158],kind:'exclusive',leaves:[{id:'private',name:'仅自己',kind:'exclusive',recorded:true},{id:'shared',name:'允许分享',kind:'exclusive',recorded:false}]},
    {id:'values',name:'在意的事',p:[267,403],kind:'fixed',leaves:[{id:'respect',name:'相互尊重',kind:'fixed'},{id:'rest',name:'休息空间',kind:'fixed'}]},
    {id:'evidence',name:'认识的进度',p:[63,338],kind:'completion',leaves:[{id:'record',name:'已有记录',kind:'completion',recorded:true},{id:'unknown',name:'信息不足',kind:'completion'}]}
  ];
const normalize=rows=>rows.map(b=>({...b,anchor:b.p,children:b.leaves.map(l=>({...l,id:b.id+'/'+l.id,shortId:l.id,children:[]}))}));
const completion=[
 {id:'original',name:'16PF原版',p:[81,68],kind:'assessment-record',leaves:[],description:'按16PF原版分类查看完成记录。当前研究页没有真实完成数据，也不生成测评分数。'},
 {id:'ai-reset',name:'AI重置版',p:[316,104],kind:'assessment-record',leaves:[],description:'AI重置版与原版分别保留记录，不默认同等效度，也不合并计算完成比例。当前无真实完成数据。'},
 {id:'single-factor',name:'单因子',p:[24,229],kind:'assessment-record',leaves:[],description:'单因子记录仅覆盖所选因子，不充作整套16PF完成结果。当前无真实完成数据。'},
 {id:'daily',name:'每日打卡',p:[350,270],kind:'assessment-record',leaves:[],description:'每日打卡按其独立入口保留记录；本页不推定连续天数、题量或完成比例。当前无真实完成数据。'},
 {id:'short-16pf',name:'简化16PF',p:[140,409],kind:'assessment-record',leaves:[],description:'简化16PF是独立分类，题数、映射和效度仍沿用原有待定状态。当前无真实完成数据。'},
 {id:'simulation',name:'模拟性格',p:[291,373],kind:'simulation-record',leaves:[],description:'模拟性格是人为设定的假设配置，不属于本人测量完成结果，不计入任何真人测评完成度。'}
];
const actual={relations:normalize(relations),traits:normalize(traits),personal:normalize(personal),completion:normalize(completion)};
function fixture(count){
  const node=(id,name,kind='explanation',children=[])=>({id,name,kind,children,recorded:kind==='completion',description:'匿名结构样本，仅验证节点说明与层级导航，不是心理维度或真实结果。'});
  return Array.from({length:count},(_,i)=>{const id='layout'+i;let children=[];
    if(i%6===1)children=[node(id+'/note','解释节点')];
    if(i%6===2)children=[node(id+'/a','A端说明','bipolar'),node(id+'/b','B端说明','bipolar')];
    if(i%6===3)children=['一','二','三'].map((n,j)=>node(id+'/n'+j,'侧面'+n,'fixed'));
    if(i%6===4){let deep=node(id+'/d6','第六层说明');for(let d=5;d>=2;d--)deep=node(id+'/d'+d,'第'+d+'层线索','explanation',d===3?[node(id+'/aside','旁侧说明'),deep]:[deep]);children=[deep];}
    if(i%6===5)children=[node(id+'/known','已有记录','completion'),node(id+'/unknown','信息不足','unknown')];
    return node(id,['固定说明','单条解释','A / B 两端','多条线索','深层线索','记录状态','补充说明'][i%7],i%6===2?'bipolar':'fixed',children);
  });
}
let count=8,tab='relations',longLabels=false,model,renderedEdges=[],visibleLayout=[],seq=0,anim=0,frame=0,returnFocus=null;
const fresh=()=>({k:1,x:0,y:0,selected:null,branch:null,leaf:null,focusDepth:0,names:false,level:1,focusCamera:null});
const views={relations:fresh(),traits:fresh(),personal:fresh(),completion:fresh()},view=()=>views[tab];
const viewport=$('#viewport'),svg=$('#branches'),layer=$('#nodes'),popover=$('#node-popover');
const reduced=()=>$('#still').checked||matchMedia('(prefers-reduced-motion: reduce)').matches;
const dims=()=>({w:viewport.clientWidth,h:viewport.clientHeight,s:tab==='relations'&&count===8?Math.min(viewport.clientWidth/390,viewport.clientHeight/720):Math.min(viewport.clientWidth/390,viewport.clientHeight/460)*.7});
const project=p=>{const d=dims(),v=view();return [d.w/2+v.x+p[0]*d.s*v.k,d.h/2+v.y+p[1]*d.s*v.k]};
const nodeBy=id=>model.nodes.find(n=>n.id===id);
function state(n){const children=model.nodes.filter(c=>c.parent===n.id);if(children.length){const recorded=children.filter(c=>c.recorded).length;return recorded?recorded===children.length?'有记录':'部分线索有记录':'未探索'}return n.recorded?'有记录':'未探索'}
function make(tag,attrs){const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));return e}
const iconPaths={
 book:'M4 3h13l3 3v15H4Z M8 7h7 M8 11h8 M8 15h6',
 shield:'M12 3 20 6v6c0 5-8 9-8 9S4 17 4 12V6Z',
 clock:'M12 7v5l4 2 M21 12a9 9 0 1 0-18 0 9 9 0 0 0 18 0',
 heart:'M12 20 4 12C-1 5 7 1 12 7c5-6 13-2 8 5Z',
 space:'M4 19v-6a8 8 0 0 1 16 0v6 M2 20h20 M12 10v5',
 link:'M9 8 7 6a4 4 0 0 0-6 6l5 5a4 4 0 0 0 6-1 M15 16l2 2a4 4 0 0 0 6-6l-5-5a4 4 0 0 0-6 1 M8 12l8 0',
 compass:'M12 3 20 20l-8-4-8 4Z M12 7v9',
 growth:'M3 20h6v-6h6V8h6 M4 5l5 5 10-8',
 coins:'M4 6c0-4 16-4 16 0s-16 4-16 0v11c0 4 16 4 16 0V6 M4 12c0 4 16 4 16 0',
 check:'M5 12l5 5L20 6',
 plus:'M12 5v14 M5 12h14',
 person:'M16 7a4 4 0 1 0-8 0 4 4 0 0 0 8 0 M4 21v-3a8 8 0 0 1 16 0v3',
 boundary:'M8 3H3v18h5 M16 3h5v18h-5 M8 12h8',
 rhythm:'M2 13h4l3-8 5 15 3-7h5',
 eye:'M2 12Q12-2 22 12Q12 26 2 12Z M15 12a3 3 0 1 0-6 0 3 3 0 0 0 6 0',
 star:'M12 2l3 7 7 3-7 3-3 7-3-7-7-3 7-3Z',
 progress:'M4 20V12 M12 20V4 M20 20V8',
 info:'M12 10v8 M12 5v1',
 unknown:'M7 7c0-6 12-6 10 1-1 3-5 3-5 7 M12 19v1'};
function nodeIcon(n){
 if(tab==='completion')return {name:({original:'book','ai-reset':'star','single-factor':'compass',daily:'clock','short-16pf':'book',simulation:'person'})[n.id]||'info'};
 if(n.id.startsWith('layout')&&n.depth===1)return {name:'factor-code',text:n.kind==='bipolar'?'AB':String(Number(n.id.slice(6))+1).padStart(2,'0')};
 if(n.id.startsWith('layout'))return {name:n.kind==='unknown'?'unknown':n.kind==='completion'?'check':'info'};
 const roots={risk:'shield',time:'clock',emotion:'heart',space:'space',commitment:'link',planning:'compass',growth:'growth',money:'coins',rhythm:'rhythm',visibility:'eye',values:'star',evidence:'progress'};
 if(n.depth===1&&roots[n.id])return {name:roots[n.id]};
 if(tab==='traits')return {name:'factor-code',text:n.shortId||['A','F','L','Q'][Number(n.id.slice(-1))]};
 const facets={f0:'check',f1:'heart',f2:'person',f3:'boundary',company:'link',alone:'person',private:'boundary',shared:'eye',respect:'heart',rest:'space',record:'check',unknown:'unknown'};
 return {name:facets[n.shortId]||'info'};
}
function iconMarkup(n){const icon=nodeIcon(n);return `<svg class="semantic-icon" data-icon="${icon.name}" viewBox="0 0 24 24" aria-hidden="true">${icon.text?`<text x="12" y="16" text-anchor="middle">${esc(icon.text)}</text>`:`<path d="${iconPaths[icon.name]}"/>`}</svg>`;}
function rebuild(){
 const roots=tab==='relations'&&count!==8?fixture(count):actual[tab];model=tab==='relations'&&count===8?RelationArt.build(roots):G.build(roots);viewport.dataset.longSpines=String(model.composition==='long-spines');if(tab==='completion')model.nodes[0].name='测评记录';viewport.dataset.composition=tab;
 layer.innerHTML=model.nodes.map(n=>`<button class="tree-node ${n.depth===0?'root-node':''} ${n.depth>1&&!n.children.length?'leaf-node':''} depth-${n.depth} ${n.recorded?'recorded':''}" data-node="${n.id}" aria-label="${esc(n.name+'，'+state(n))}"><span class="node-medallion" aria-hidden="true">${n.depth===0?(tab==='completion'?'记录':'我'):`<span class="overview-mark">${n.depth===1&&count!==8&&tab==='relations'?String(roots.findIndex(r=>r.id===n.id)+1).padStart(2,'0'):'<i></i>'}</span>${n.depth>1&&!n.children.length?'<img class=business-leaf src=assets/leaf-node.png alt="">':iconMarkup(n)}`}</span></button><span class="tree-label" data-label="${n.id}" aria-hidden="true">${esc(n.name)}</span>`).join('');
 $('#index').innerHTML=model.nodes.filter(n=>n.depth).map(n=>`<button data-select="${n.id}" style="--depth:${n.depth}">${esc(n.name)}<small>${n.children.length?' · '+n.children.length+'个下级':' · 说明'}</small></button>`).join('');
 $('.text-index summary').textContent=`按名称查看线索 · ${roots.length}条主枝`;
 $('#fixture-banner').hidden=!(count!==8&&tab==='relations');$('#fixture-banner').textContent=`匿名拓扑样本：${count}条主枝，子树数量与深度不等，最深6层。不是新增心理维度。`;
 $('#intro').textContent=count!==8&&tab==='relations'?'匿名结构 · 点选圆点，放大逐层查看。':{relations:'点选主枝放大 · 拖动探索 · 点叶片查看线索',traits:'16个独立因子 · 点选查看，无有效结果不落点。',personal:'经历、需要与边界，各自保留。',completion:'六类入口 · 尚无真实完成数据。'}[tab];
 draw();
}
function levels(){const v=view();if(v.k<1.36)v.focusDepth=0;if(v.k>1.36)v.icons=true;if(v.k<1.24)v.icons=false;if(v.k>1.24)v.names=true;if(v.k<1.12)v.names=false;const thresholds=[0,0,1.52,1.9,2.2,2.55,2.8];let level=v.level;while(level<6&&v.k>thresholds[level+1])level++;while(level>1&&v.k<thresholds[level]-.12)level--;v.level=level;return Math.min(Math.max(...model.nodes.map(n=>n.depth)),Math.max(level,v.focusDepth));}

// De Casteljau prefix: overview and detail share exactly the same carrier path.
function curvePrefix(q,t){const mix=(a,b)=>a.map((v,i)=>v+(b[i]-v)*t),a=mix(q[0],q[1]),b=mix(q[1],q[2]),c=mix(q[2],q[3]),d=mix(a,b),e=mix(b,c);return [q[0],a,d,mix(d,e)]}
function draw(){
 frame=0;const d=dims(),v=view(),depth=levels(),scale=d.s*v.k;const bound=(Math.max(...model.nodes.map(n=>n.radius))+250)*scale;v.x=Math.max(-bound,Math.min(bound,v.x));v.y=Math.max(-bound,Math.min(bound,v.y));layer.classList.toggle('show-icons',!!v.icons);svg.setAttribute('viewBox',`0 0 ${d.w} ${d.h}`);svg.replaceChildren();
 const focusContext=model.composition==='long-spines'&&v.branch&&v.focusCamera&&v.k>1.36;
 const allowed=model.nodes.filter(n=>n.depth<=1||n.depth<=depth&&(!v.branch||n.rootId===v.branch));
 const active=[];const hitboxes=[];
 for(const n of allowed){const [x,y]=project(n.p),size=n.depth?44:66;if(x-size/2<4||x+size/2>d.w-4||y-size/2<4||y+size/2>d.h-4)continue;
  if(hitboxes.some(b=>Math.hypot(x-b.x,y-b.y)<(size+b.size)/2+3))continue;active.push(n);hitboxes.push({x,y,size,id:n.id});}
 const activeIds=new Set(active.map(n=>n.id));renderedEdges=[];
 for(const edge of model.edges){const preview=depth===1&&edge.depth===2;if(preview||!allowed.some(n=>n.id===edge.child))continue;const reveal=Math.max(0,Math.min(1,(v.k-1.05)/.31)),end=edge.role==='carrier'?((edge.rootId==='space'?.48:.62)+(1-(edge.rootId==='space'?.48:.62))*reveal):1;const q=(end<1?curvePrefix(edge.q,end):edge.q).map(project);const trimmed=G.trim(q,edge.trim?edge.trim[0]:edge.role==='side-shoot'?0:edge.parent==='root'?32:preview?18:16,edge.trim?edge.trim[1]:preview?4:16);if(!trimmed)continue;
  const child=nodeBy(edge.child),warm=child.recorded||state(child).startsWith('部分');
  if(preview){const end=q[3];svg.append(make('circle',{cx:end[0],cy:end[1],r:2.7,fill:warm?'var(--warm)':'var(--primary)',opacity:'.48','class':'preview-tip'}));}
  const samples=Array.from({length:65},(_,i)=>G.point(trimmed,i/64));renderedEdges.push({...edge,artWidth:edge.role==='carrier'?[5.5,.25+1.25*reveal]:edge.artWidth,opacity:focusContext&&edge.rootId!==v.branch?.22:1,q:trimmed,samples,warm,preview,fine:tab==='traits'});
 }
 const occupied=hitboxes.map(b=>({x:b.x-b.size/2-4,y:b.y-b.size/2-4,w:b.size+8,h:b.size+8}));visibleLayout=[];
 const overlap=(a,b)=>a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
 const blocksLine=r=>renderedEdges.some(e=>e.samples.some(p=>p[0]>r.x-8&&p[0]<r.x+r.w+8&&p[1]>r.y-8&&p[1]<r.y+r.h+8));
 const labelPriority=n=>model.composition==='long-spines'&&v.branch?(n.depth===0?-1:n.id===v.branch?0:n.rootId===v.branch?1:n.depth+2):n.depth;
 for(const n of [...model.nodes].sort((a,b)=>labelPriority(a)-labelPriority(b)||(a.id==='money'?-1:b.id==='money'?1:0))){const button=layer.querySelector(`[data-node="${n.id}"]`),label=layer.querySelector(`[data-label="${n.id}"]`),[x,y]=project(n.p),visible=activeIds.has(n.id);
  button.classList.toggle('context-node',!!focusContext&&n.depth>0&&n.rootId!==v.branch&&n.id!==v.branch);button.hidden=!visible;const actionable=n.depth===1||n.depth>1&&!n.children.length;button.disabled=!actionable;button.tabIndex=visible&&actionable?0:-1;button.setAttribute('aria-hidden',String(!visible));if(n.depth>1&&!n.children.length){const incoming=model.edges.find(e=>e.child===n.id&&e.role!=='carrier');if(incoming){const q=incoming.q;button.style.setProperty('--leaf-angle',(Math.atan2(q[3][1]-q[2][1],q[3][0]-q[2][0])*180/Math.PI+40)+'deg')}}button.style.left=x+'px';button.style.top=y+'px';button.classList.toggle('selected',v.selected===n.id);label.hidden=true;
  if(!visible)continue;visibleLayout.push({id:n.id,depth:n.depth,x,y,size:n.depth?44:66});
  if(focusContext&&n.depth===1&&n.id!==v.branch)continue;
  if(tab==='traits'&&v.k<1.3)continue;
  if(!n.depth||v.k<.86&&n.depth>1)continue;
  label.textContent=n.name+(longLabels?' · 长内容排版示例':'');label.hidden=false;if(model.composition==='long-spines'){label.style.left='0px';label.style.top='0px';label.style.width='max-content'}label.style.maxWidth=longLabels?'116px':d.w<330&&['money','space'].includes(n.id)?'28px':'100px';const w=label.offsetWidth,h=label.offsetHeight;
  const a=n.angle,ux=Math.cos(a),uy=Math.sin(a),candidates=[];if(n.labelP&&!(n.id===v.branch&&v.k>1.36)){const [lx,ly]=project(n.labelP);candidates.push({x:lx-w/2,y:ly-h/2,w,h})}
  for(const dist of [32,44,58,76,96])for(const turn of [Math.PI/2,-Math.PI/2,0,Math.PI,.7,-.7]){const tx=x+Math.cos(a+turn)*dist,ty=y+Math.sin(a+turn)*dist; candidates.push({x:tx-w/2,y:ty-h/2,w,h})}
  if(n.depth===1){const alternatives=[];for(let tx=8;tx+w<d.w-8;tx+=12)for(let ty=8;ty+h<d.h-8;ty+=12){const distance=Math.hypot(tx+w/2-x,ty+h/2-y);if(distance<120)alternatives.push({x:tx,y:ty,w,h,distance})}candidates.push(...alternatives.sort((a,b)=>a.distance-b.distance))}
  if(n.id===v.branch&&v.k>1.36)candidates.sort((a,b)=>Math.hypot(a.x+w/2-x,a.y+h/2-y)-Math.hypot(b.x+w/2-x,b.y+h/2-y));
  const rect=candidates.find(r=>r.x>=5&&r.y>=5&&r.x+w<=d.w-5&&r.y+h<=d.h-5&&!occupied.some(b=>overlap(r,b))&&!blocksLine(r));
  if(rect){label.style.left=rect.x+'px';label.style.top=rect.y+'px';occupied.push({x:rect.x-3,y:rect.y-3,w:w+6,h:h+6});}else label.hidden=true;
 }
 LineMaterial.draw(renderedEdges,d.w,d.h,v.k);
 // All visible leaves are semantic terminal nodes; no decorative foliage.
 layer.querySelectorAll('[data-node]').forEach(b=>{const item=document.querySelector(`[data-select="${b.dataset.node}"]`);if(item)item.hidden=b.hidden||b.disabled});
 $('#zoom-label').textContent=Math.round(v.k*100)+'%';$('#zoom-in').disabled=v.k>=3;$('#zoom-out').disabled=v.k<=.7;$('#fit-branch').disabled=!v.branch;$('#level').textContent=`第${depth}层 · ${active.filter(n=>n.depth).length}节点`;
 $('#detail').textContent=v.selected?`已保留「${nodeBy(v.selected)?.name||'我'}」 · 拖动探索 · 点叶片查看说明`:tab==='completion'?'记录按来源分别呈现，不合成总完成比例。':tab==='traits'?'尚无有效量表结果，16因子均保持未知。':'从一条线索开始，慢慢看见自己。';
}
function schedule(){if(!frame)frame=requestAnimationFrame(draw)}
function stop(){seq++;cancelAnimationFrame(anim);anim=0}
function moveTo(target){stop();const v=view(),from={k:v.k,x:v.x,y:v.y},token=seq,start=performance.now();target.k=Math.max(.7,Math.min(3,target.k));if(reduced()){Object.assign(v,target);draw();return}function tick(t){if(token!==seq)return;const f=Math.min(1,(t-start)/220),e=1-(1-f)**3;for(const k of ['k','x','y'])v[k]=from[k]+(target[k]-from[k])*e;draw();if(f<1)anim=requestAnimationFrame(tick)}anim=requestAnimationFrame(tick)}
function fit(){view().branch=null;view().selected=null;view().focusDepth=0;view().focusCamera=null;moveTo({k:1,x:0,y:0})}
function zoom(k,anchor){const v=view(),d=dims(),nk=Math.max(.7,Math.min(3,k)),a=anchor||[d.w/2,d.h/2],r=nk/v.k;let x=a[0]-d.w/2-(a[0]-d.w/2-v.x)*r,y=a[1]-d.h/2-(a[1]-d.h/2-v.y)*r;if(nk<1.36){v.focusDepth=0;if(v.focusCamera){x=0;y=0;v.focusCamera=null}}moveTo({k:nk,x,y})}
function focusNode(n,children=false){const d=dims(),v=view(),targets=children?n.children.map(nodeBy):[];v.branch=n.rootId||n.id;v.focusDepth=Math.min(6,n.depth+(children?1:0));const ps=[n,...targets],extent=[0,1].map(i=>[Math.min(...ps.map(n=>n.p[i])),Math.max(...ps.map(n=>n.p[i]))]),center=model.composition==='long-spines'?extent.map(a=>(a[0]+a[1])/2):ps.reduce((p,n)=>[p[0]+n.p[0]/ps.length,p[1]+n.p[1]/ps.length],[0,0]);const k=children?(model.composition==='long-spines'?Math.min(2.5,(d.w-110)/((extent[0][1]-extent[0][0])*d.s),(d.h-140)/((extent[1][1]-extent[1][0])*d.s)):1.8):1.6;v.focusCamera=true;moveTo({k,x:-center[0]*d.s*k,y:-center[1]*d.s*k})}
function description(n){
 if(tab==='completion')return `<p>${esc(n.description||'按实际测评分类分别查看；不合成总完成比例。')}</p><p>没有有效记录时保持未知，不把未知显示为0分或0%完成。</p>`;
 if(n.description)return `<p>${esc(n.description)}</p><p>${n.kind==='bipolar'?'A与B仅展示两端含义，不要求二选一。':n.kind==='unknown'?'信息不足，不推断结果或完成状态。':n.children.length?'下级线索各自保留，不合成为总分。':'这是说明节点，没有待选择或待完成的任务。'}</p>`;
 if(n.kind==='root')return '<p>不同线索共同组成画像；它们不是一个总分。</p>';
 if(n.kind==='bipolar')return n.shortId==='A'?'<p>乐群：较低与较高倾向是同一因子的两端。没有有效量表结果，暂不落点。</p>':'<p>尚无有效结果。两端名称和刻度须由对应量表支持，不借用其他因子的定义。</p>';
 const owner=nodeBy(n.rootId);
 if(owner.kind==='independent')return '<p>需要陪伴与需要独处可以同时存在，不是相反选项。</p>';
 if(owner.kind==='exclusive')return '<p>同一条记录只能有一个可见性状态。示例为“仅自己”；这里没有执行分享。</p>';
 if(owner.kind==='completion')return '<p>已有记录与信息不足可以并存。进度不代表人格高低。</p>';
 if(tab==='relations')return `<p>${n.depth===1?'能做到、愿投入、自己需要与边界四个侧面独立保留，不互斥，不相减，不合成总分。':n.id==='space/f2'?'忙碌之后，我希望留一段不被打扰的时间，也愿意约好再相处。':'这是关系中的一个独立观察角度，不代表对错或高低。'}</p>`;
 return '<p>每个因子独立保留；没有有效测量结果的地方先留白。</p>';
}
function inspect(n,source,navigate=false){const v=view();v.selected=n.id;v.branch=n.rootId||null;v.leaf=n.depth>1?n.id:null;returnFocus=source;if(navigate)focusNode(n);draw();
 const ancestors=[];let parent=nodeBy(n.parent);while(parent&&parent.depth){ancestors.unshift(parent.name);parent=nodeBy(parent.parent)}
 popover.innerHTML=`<div class="popover-head"><span>${n.depth?'第'+n.depth+'层 · '+esc(state(n)):'我的画像'}</span><button data-dismiss aria-label="关闭节点说明">×</button></div>${ancestors.length?`<p class="node-breadcrumb">${ancestors.map(esc).join(' / ')}</p>`:''}<h2>${esc(n.name)}</h2>${description(n)}${n.children.length?`<button class="open-children" data-expand-node="${n.id}">查看${n.children.length}条下级线索 ↗</button>`:''}${n.depth>1?`<button data-parent-node="${n.parent}">← 返回上级线索</button>`:''}`;
 popover.removeAttribute('style');if(innerWidth>600){const r=(source||viewport).getBoundingClientRect();popover.style.left=Math.max(12,Math.min(innerWidth-374,r.right+12))+'px';popover.style.top=Math.max(12,Math.min(innerHeight-350,r.top))+'px';popover.style.right='auto';popover.style.bottom='auto'}
 if(!popover.matches(':popover-open'))popover.showPopover();popover.querySelector('[data-dismiss]').focus({preventScroll:true});$('#announce').textContent=n.name+'，说明已打开';
}
popover.addEventListener('toggle',e=>{if(e.newState==='closed'){const target=returnFocus?.isConnected&&!returnFocus.hidden?returnFocus:viewport;target.focus({preventScroll:true})}});
function switchTab(id){stop();pointers.clear();gesture=null;if(popover.matches(':popover-open'))popover.hidePopover();tab=id;document.querySelectorAll('[data-tab]').forEach(b=>{const on=b.dataset.tab===id;b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1});$('#panel').setAttribute('aria-labelledby','tab-'+id);rebuild()}
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.tab)return switchTab(b.dataset.tab);if(b.dataset.node||b.dataset.select){const n=nodeBy(b.dataset.node||b.dataset.select);if(n.depth===1&&n.children.length){view().selected=n.id;focusNode(n,true);return}if(n.depth&& !n.children.length)return inspect(n,b);return}if(b.hasAttribute('data-dismiss'))return popover.hidePopover();if(b.dataset.parentNode){popover.hidePopover();focusNode(nodeBy(b.dataset.parentNode),true);return}if(b.dataset.expandNode){const n=nodeBy(b.dataset.expandNode);popover.hidePopover();focusNode(n,true);return}});
$('#zoom-in').onclick=()=>zoom(view().k*1.28);$('#zoom-out').onclick=()=>zoom(view().k/1.28);$('#fit').onclick=fit;$('#fit-branch').onclick=()=>{if(view().branch)focusNode(nodeBy(view().branch),true)};$('#profile-nav').onclick=fit;
$('#reset').onclick=()=>{Object.keys(views).forEach(k=>views[k]=fresh());switchTab('relations')};
$('#structure').onchange=()=>{count=+$('#structure').value;views.relations=fresh();switchTab('relations')};$('#long-labels').onchange=()=>{longLabels=$('#long-labels').checked;draw()};
const pointers=new Map();let gesture=null,moved=false,suppress=false;
const local=e=>{const r=viewport.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top]};
function snapshotGesture(){const ps=[...pointers.values()],v=view();gesture={ps,k:v.k,x:v.x,y:v.y,dist:ps.length>1?Math.hypot(ps[0][0]-ps[1][0],ps[0][1]-ps[1][1]):0}}
viewport.addEventListener('pointerdown',e=>{if(e.button!==0)return;stop();if(!pointers.size){moved=false;suppress=false}pointers.set(e.pointerId,local(e));e.target.setPointerCapture(e.pointerId);snapshotGesture()});
viewport.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId)||!gesture)return;pointers.set(e.pointerId,local(e));const ps=[...pointers.values()],v=view();if(ps.length===1){const dx=ps[0][0]-gesture.ps[0][0],dy=ps[0][1]-gesture.ps[0][1];if(Math.hypot(dx,dy)>7)moved=true;if(moved){v.x=gesture.x+dx;v.y=gesture.y+dy;v.focusCamera=null}}else{moved=true;v.focusCamera=null;const dist=Math.hypot(ps[0][0]-ps[1][0],ps[0][1]-ps[1][1]),k=Math.max(.7,Math.min(3,gesture.k*dist/gesture.dist)),d=dims(),mid=ps[0].map((x,i)=>(x+ps[1][i])/2),old=gesture.ps[0].map((x,i)=>(x+gesture.ps[1][i])/2);v.k=k;v.x=mid[0]-d.w/2-(old[0]-d.w/2-gesture.x)*k/gesture.k;v.y=mid[1]-d.h/2-(old[1]-d.h/2-gesture.y)*k/gesture.k}schedule()});
function release(e){pointers.delete(e.pointerId);if(moved)suppress=true;if(pointers.size)snapshotGesture();else gesture=null}
viewport.addEventListener('pointerup',release);viewport.addEventListener('pointercancel',release);viewport.addEventListener('click',e=>{if(suppress){e.preventDefault();e.stopPropagation();suppress=false}},true);
viewport.addEventListener('wheel',e=>{e.preventDefault();zoom(view().k*Math.exp(-e.deltaY*.002),local(e))},{passive:false});
viewport.addEventListener('keydown',e=>{if(['+','=','-','Home','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();stop();if(e.key==='+'||e.key==='=')zoom(view().k*1.28);else if(e.key==='-')zoom(view().k/1.28);else if(e.key==='Home')fit();else{const v=view();v.focusCamera=null;v.x+=e.key==='ArrowRight'?-32:e.key==='ArrowLeft'?32:0;v.y+=e.key==='ArrowDown'?-32:e.key==='ArrowUp'?32:0;draw()}}});
$('.tabs').addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const keys=['traits','relations','personal','completion'],i=keys.indexOf(tab),n=e.key==='Home'?0:e.key==='End'?3:(i+(e.key==='ArrowRight'?1:3))%4;switchTab(keys[n]);$('#tab-'+keys[n]).focus()}});
new ResizeObserver(schedule).observe(viewport);const syncMotion=()=>{if(reduced())stop();Ambient.setContext({quiet:false,reduced:$('#still').checked})};$('#still').onchange=syncMotion;matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',syncMotion);
document.body.className='theme-mint study';Ambient.setContext({quiet:false});
fetch('../../handoff/themes-v4.json').then(r=>{if(!r.ok)throw Error();return r.json()}).then(themes=>{$('#theme').insertAdjacentHTML('beforeend',themes.map(t=>`<option value="${t.id}">${esc(t.name)}</option>`).join(''));$('#theme').onchange=()=>{document.body.className=$('#theme').value==='study'?'theme-mint study':'theme-'+$('#theme').value;Ambient.setContext({quiet:false,reduced:$('#still').checked})}}).catch(()=>{$('#announce').textContent='主题目录暂不可用，当前配色仍可浏览。'});
const queryCount=+new URLSearchParams(location.search).get('structure');if([6,7,12].includes(queryCount)){count=queryCount;$('#structure').value=String(count)}rebuild();
LineMaterial.canvas.addEventListener('materials-ready',schedule);LineMaterial.load();
window.BotanicalTree={snapshot:()=>({tab,...view()}),counts:()=>({relations:8,factors:16}),structure:()=>count,layout:()=>visibleLayout,topology:()=>model,rendered:()=>renderedEdges,inspect:id=>inspect(nodeBy(id),viewport,true)};
})();
