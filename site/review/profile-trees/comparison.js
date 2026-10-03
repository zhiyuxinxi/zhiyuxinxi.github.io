/* Independent visual study. Synthetic data only; deliberately no App, storage or service imports. */
(async()=>{'use strict';
let ThemeCatalog=[];try{const response=await fetch('../../handoff/themes-v4.json');if(!response.ok)throw Error('theme');ThemeCatalog=await response.json();}catch{document.querySelector('#theme').disabled=true;document.querySelector('#announcement').textContent='主题列表暂未加载，可继续查看当前方案。';}
const {esc,icon}=UI;
const branches=[
{id:'D1',short:'金钱资源',name:'金钱与资源',status:'recorded',hint:'资源怎样安排，彼此更自在？'},
{id:'D2',short:'时间陪伴',name:'时间与陪伴',status:'unexplored',hint:'相处与独处，怎样分配更合适？'},
{id:'D3',short:'规划协商',name:'规划带领与关系秩序',status:'pending',hint:'由谁规划，怎样商量和作决定？'},
{id:'D4',short:'成长认可',name:'成长与价值确认',status:'recorded',hint:'怎样支持成长，也感到被认可？'},
{id:'D5',short:'情绪支持',name:'情绪支持',status:'unexplored',hint:'需要怎样被理解，能怎样回应？'},
{id:'D7',short:'风险兜底',name:'风险兜底',status:'pending',hint:'遇到困难，期待怎样一起面对？'},
{id:'D8',short:'亲密承诺',name:'亲密节奏与承诺',status:'recorded',hint:'靠近与承诺，什么节奏适合自己？'},
{id:'D9',short:'自由空间',name:'自由与空间',status:'unexplored',hint:'亲近之余，想保留哪些自主空间？'}];
const facets=[{id:'ability',name:'能做到',question:'以现在的时间、精力和条件，我能提供什么？'},{id:'willingness',name:'愿意投入',question:'即使做得到，我愿意承担多少？'},{id:'need',name:'自己需要',question:'什么样的回应，会让我感到被支持？'},{id:'boundary',name:'边界',question:'哪些需要先商量，哪些代价不能承受？'}];
const samples={'D1:ability':{status:'recorded',text:'我能安排好日常开支，大额支出会提前讨论。'},'D3:need':{status:'pending',text:'我希望一起商量计划，但还想区分工作日与周末。'},'D4:willingness':{status:'recorded',text:'我愿意留出时间，认真听对方谈正在学习的事情。'},'D7:boundary':{status:'pending',text:'紧急支出时，我仍需要保留自己的基本生活预算。'},'D8:need':{status:'recorded',text:'我希望重要的承诺有足够时间沟通。'}};
const labels={unexplored:'未探索',recorded:'有记录',pending:'待确认'};
const schemes=[{id:'a',name:'圆形放射',subtitle:'固定方位 · 清楚主枝',note:'八个方向各自生长，回到总览仍在原位。'},{id:'b',name:'有机星簇',subtitle:'稳定分区 · 柔曲连接',note:'主枝组成疏密有致的星簇，叶子在各自分区生长。'},{id:'c',name:'花瓣轨道',subtitle:'环绕层级 · 向外拓展',note:'主枝是固定花瓣，子叶在分支内展开，不按面积计量。'}];
const state={scheme:'a',branch:null,facet:null,entry:null,draft:'',temporary:{}};
const stage=document.querySelector('#comparisons'),inspector=document.querySelector('#inspector');
const xy=(angle,r)=>[180+Math.cos(angle*Math.PI/180)*r,180+Math.sin(angle*Math.PI/180)*r];
const A=Array.from({length:8},(_,i)=>xy(-90+i*45,126));
const B=[[82,48],[278,66],[286,148],[277,284],[186,313],[73,284],[68,191],[74,122]];
const C=Array.from({length:8},(_,i)=>xy(-67.5+i*45,128));
const positions={a:A,b:B,c:C};
function branchStatus(item){return item.status==='pending'?'pending':Object.keys(state.temporary).some(k=>k.startsWith(item.id+':'))?'recorded':item.status;}
function statusMark(status){return `<i class="state-mark ${status}" aria-hidden="true"></i>`;}
function dataFor(facet){return state.temporary[state.branch+':'+facet]||samples[state.branch+':'+facet]||{status:'unexplored',text:''};}
function ornament(scheme,focus){let html='';const points=focus?[[92,85],[268,85],[268,272],[92,272]]:positions[scheme];
 if(scheme==='a'){
  html+=`<circle class="guide" cx="180" cy="180" r="${focus?120:126}"/><circle class="trunk" cx="180" cy="180" r="47"/>`;
  points.forEach(([x,y],i)=>{const dx=x-180,dy=y-180;html+=`<path class="branch" d="M${180+dx*.38} ${180+dy*.38} L${x} ${y}"/>`;[.62,.79].forEach((t,k)=>{const sign=k?1:-1;const sx=180+dx*t,sy=180+dy*t;html+=`<path class="twig" d="M${sx} ${sy} l${-dy*.11*sign} ${dx*.11*sign}"/><circle cx="${sx-dy*.11*sign}" cy="${sy+dx*.11*sign}" r="2.5" fill="var(--reading)" stroke="var(--line)"/>`;});});
 }else if(scheme==='b'){
  const hubs=focus?points:[[127,99],[234,113],[234,247],[123,232]],pairs=[[0,7],[1,2],[3,4],[5,6]];
  hubs.forEach(([hx,hy],i)=>{html+=`<path class="branch" d="M180 180 Q${hx+(i%2?20:-20)} ${180+(hy-180)*.35} ${hx} ${hy}"/>`;
   if(!focus){html+=`<circle cx="${hx}" cy="${hy}" r="4" fill="var(--surface)" stroke="var(--primary)"/>`;pairs[i].forEach(j=>{const [x,y]=points[j];html+=`<path class="branch" d="M${hx} ${hy} Q${x} ${hy} ${x} ${y}"/><path class="twig" d="M${x} ${y} q${j%2?19:-19} -17 ${j%2?26:-26} -12"/><circle cx="${x+(j%2?26:-26)}" cy="${y-12}" r="3" fill="var(--surface)" stroke="var(--line)"/>`;});}
  });html+='<circle class="trunk" cx="180" cy="180" r="43"/>';
 }else{
  html+='<circle class="guide" cx="180" cy="180" r="150"/><circle class="trunk" cx="180" cy="180" r="59"/>';
  points.forEach(([x,y],i)=>{const angle=Math.atan2(y-180,x-180),d=.24,p=(r,a)=>[180+Math.cos(a)*r,180+Math.sin(a)*r],l=p(75,angle-d),o=p(155,angle),rr=p(75,angle+d);html+=`<path class="petal" d="M${l} Q${p(164,angle-.43)} ${o} Q${p(164,angle+.43)} ${rr} Q180 180 ${l}Z"/><path class="branch" d="M${p(67,angle)} L${x} ${y}"/>`;});
 }
 return `<svg viewBox="0 0 360 360" aria-hidden="true">${html}</svg>`;
}
function node(label,index,scheme,focus){const item=focus?facets[index]:branches[index],point=focus?[[92,85],[268,85],[268,272],[92,272]][index]:positions[scheme][index],status=focus?dataFor(item.id).status:branchStatus(item),selected=focus&&state.facet===item.id;return `<button type="button" class="node ${status}" style="--x:${point[0]/3.6}%;--y:${point[1]/3.6}%" data-${focus?'facet':'branch'}="${item.id}" data-owner="${scheme}" aria-label="${focus?item.name:item.name}，${labels[status]}，${focus?'查看线索':'展开四个角度'}" aria-pressed="${!!selected}"><span class="node-symbol" aria-hidden="true">${status==='recorded'?'✓':status==='pending'?'?':''}</span><span>${esc(label)}</span></button>`;}
function renderTrees(){const focus=!!state.branch,b=branches.find(x=>x.id===state.branch);stage.innerHTML=schemes.map(s=>`<article class="scheme-card scheme-${s.id} ${state.scheme===s.id?'selected-scheme':''}" aria-labelledby="scheme-${s.id}"><header class="scheme-heading"><span class="scheme-letter">${s.id.toUpperCase()}</span><div><h2 id="scheme-${s.id}">${s.name}</h2><p>${s.subtitle}</p></div></header><div class="tree-toolbar">${focus?`<button type="button" data-overview data-owner="${s.id}">← 全部分支</button><span>${esc(b.short)} · 四个角度</span>`:'<span>关系模式 / 8条主分支</span><span>点选一个分支</span>'}</div><div class="tree" data-tree="${s.id}">${ornament(s.id,focus)}<div class="tree-center ${focus?'focus-center':''}">${focus?esc(b.short):'<img src="../../prototype/assets/original-person-1.webp" alt=""><span>我的关系线索</span>'}</div>${(focus?facets:branches).map((x,i)=>node(focus?x.name:x.short,i,s.id,focus)).join('')}</div><p class="scheme-footer">${focus?'四个角度分别保留，不合成总分。':s.note}</p></article>`).join('');}
function renderDetail(){const b=branches.find(x=>x.id===state.branch),f=facets.find(x=>x.id===state.facet),d=f?dataFor(f.id):null;
 inspector.innerHTML=!b?`<div><span class="detail-kicker">总览 · 同一份合成样本</span><h2 id="detail-title">从一个熟悉的角度开始</h2><p>选择任意主分支，三个方案会一起聚焦到同一处。下面的文字入口与图上节点完全等效。</p></div><div class="node-index" aria-label="关系维度文字入口">${branches.map(x=>`<button type="button" data-branch="${x.id}">${statusMark(branchStatus(x))}${x.short}</button>`).join('')}</div>`:`<div><span class="detail-kicker">${esc(b.name)}${f?' / '+f.name:''}</span><h2 id="detail-title" tabindex="-1">${f?f.name:b.name}</h2><p>${f?f.question:b.hint}</p>${f?`<div class="detail-status">${statusMark(d.status)}${labels[d.status]}<span>· 合成示例</span></div>`:'<p>选一个角度查看资料，不需要依次解锁。</p>'}<div class="actions"><button type="button" data-overview>返回关系总览</button></div></div><div>${f?`${d.text?`<blockquote class="detail-record"><small>一条情境记录</small>${esc(d.text)}</blockquote>`:'<p>这里还没有记录。未知只是留白，不代表能力低。</p>'}<div class="actions"><button type="button" class="primary" data-entry="record">${d.text?'补充记录示意':'记录一件事示意'}</button><button type="button" data-entry="question">看看问题示意</button></div>${renderEntry()}`:`<div class="node-index">${facets.map(x=>`<button type="button" data-facet="${x.id}">${statusMark(dataFor(x.id).status)}${x.name}</button>`).join('')}</div>`}</div>`;
}
function renderEntry(){if(!state.entry)return '';if(state.entry==='question')return `<div class="entry-demo"><h3>问题入口示意</h3><p>${facets.find(x=>x.id===state.facet).question}</p><p>回想最近一次具体情境：发生了什么？你怎样回应？下次希望有什么不同？</p><small>这里不生成测评题目，不计算分数。</small><div class="actions"><button type="button" data-close-entry>收起</button></div></div>`;return `<div class="entry-demo"><h3>记录入口示意</h3><label for="sample-note">只写虚构情境，刷新或重置后清除</label><textarea id="sample-note" maxlength="300" placeholder="例如：一次需要彼此商量的日常安排…">${esc(state.draft)}</textarea><div class="actions"><button type="button" class="primary" data-save-example>临时加入示例</button><button type="button" data-close-entry>收起</button></div><small>仅在当前页面内存，不保存到本人记录。</small></div>`;}
function announce(text){document.querySelector('#announcement').textContent=text;}
function render(){renderTrees();renderDetail();document.querySelectorAll('[data-scheme]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.scheme===state.scheme)));}
function focusNode(kind,id,owner){requestAnimationFrame(()=>{const card=stage.querySelector('.scheme-'+(owner||state.scheme));card?.querySelector(`[data-${kind}="${id}"]`)?.focus({preventScroll:true});});}
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
 if(b.dataset.scheme){state.scheme=b.dataset.scheme;renderTrees();document.querySelectorAll('[data-scheme]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));return;}
 if(b.dataset.branch){state.branch=b.dataset.branch;state.facet=null;state.entry=null;state.draft='';render();if(b.closest('.node-index'))stage.querySelector('.selected-scheme').scrollIntoView({block:'start',behavior:'instant'});focusNode('facet','ability',b.dataset.owner);announce(branches.find(x=>x.id===state.branch).name+'已展开，四个角度均可选择。');return;}
 if(b.dataset.facet){state.facet=b.dataset.facet;state.entry=null;state.draft='';render();if(matchMedia('(max-width:1000px)').matches){inspector.querySelector('#detail-title').focus({preventScroll:true});inspector.scrollIntoView({block:'start',behavior:'instant'});}else focusNode('facet',state.facet,b.dataset.owner);announce(facets.find(x=>x.id===state.facet).name+'，'+labels[dataFor(state.facet).status]);return;}
 if(b.hasAttribute('data-overview')){const previous=state.branch;state.branch=null;state.facet=null;state.entry=null;state.draft='';render();stage.querySelector('.selected-scheme').scrollIntoView({block:'start',behavior:'instant'});focusNode('branch',previous,b.dataset.owner);announce('已返回关系总览，主分支位置不变。');return;}
 if(b.dataset.entry){state.entry=b.dataset.entry;renderDetail();inspector.querySelector(state.entry==='record'?'textarea':'.entry-demo button')?.focus();return;}
 if(b.hasAttribute('data-close-entry')){const prior=state.entry;state.entry=null;renderDetail();inspector.querySelector(`[data-entry="${prior}"]`)?.focus();return;}
 if(b.hasAttribute('data-save-example')){if(!state.draft.trim()){document.querySelector('#sample-note').focus();announce('请先写一个虚构情境。');return;}state.temporary[state.branch+':'+state.facet]={status:'recorded',text:state.draft.trim()};state.draft='';state.entry=null;render();inspector.querySelector('[data-entry=record]').focus();announce('已临时加入比较示例，未写入本人资料。');return;}
 if(b.dataset.group){const note=document.querySelector('#group-note');if(b.dataset.group==='relations'){note.hidden=true;return;}note.hidden=false;note.innerHTML=b.dataset.group==='traits'?'<strong>人格倾向：应保留16个因子的各自含义。</strong><p>本轮三张图仅用关系模式的8个维度做公平比较，不将人格倾向简化成8轴。下一步可比较16分支的分层与聚焦方式。</p>':'<strong>个人画像：由本人经历逐步补充。</strong><p>此名称在本比较页替代“我的观察”。底座可长期稳定，记录叶子按实际资料变化，不用记录数量换算人格分数。</p>';note.innerHTML+='<button type="button" data-dismiss-note>继续比较关系模式</button>';return;}
 if(b.hasAttribute('data-dismiss-note')){document.querySelector('#group-note').hidden=true;document.querySelector('[data-group=relations]').focus();return;}
 if(b.id==='reset'){Object.assign(state,{branch:null,facet:null,entry:null,draft:'',temporary:{}});render();document.querySelector('#group-note').hidden=true;announce('已清除临时输入，恢复同一组合成样本。');}
});
document.addEventListener('input',e=>{if(e.target.id==='sample-note')state.draft=e.target.value;});
document.addEventListener('keydown',e=>{const n=e.target.closest('.node');if(n&&['ArrowRight','ArrowDown','ArrowLeft','ArrowUp','Home','End'].includes(e.key)){e.preventDefault();const list=[...n.closest('.tree').querySelectorAll('.node')],i=list.indexOf(n),next=e.key==='Home'?0:e.key==='End'?list.length-1:(i+(['ArrowRight','ArrowDown'].includes(e.key)?1:-1)+list.length)%list.length;list[next].focus();}if(e.key==='Escape'&&state.branch){e.preventDefault();stage.querySelector('.selected-scheme [data-overview]')?.click();}});
const theme=document.querySelector('#theme');theme.innerHTML=ThemeCatalog.map(t=>`<option value="${t.id}">${t.name}${t.group==='历史候选'?' · 历史':''}</option>`).join('');theme.value='lime';theme.addEventListener('change',()=>{const t=ThemeCatalog.find(x=>x.id===theme.value);if(!t)return;document.body.className='theme-'+t.id+(document.querySelector('#still').checked?' static':'');document.body.dataset.themeMode=t.mode;Ambient.setContext({quiet:false,reduced:document.querySelector('#still').checked});});document.querySelector('#still').addEventListener('change',e=>{document.body.classList.toggle('static',e.target.checked);Ambient.setContext({quiet:false,reduced:e.target.checked});});
window.TreeComparison={snapshot:()=>JSON.parse(JSON.stringify(state)),branches:branches.map(x=>({...x})),positions};render();Ambient.setContext({quiet:false,reduced:false});
})();
