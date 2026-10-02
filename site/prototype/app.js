/* Local-only interaction prototype. No authentication, AI, analytics, payment or remote requests. */
window.App=(()=>{
 'use strict';
 const {esc,icon,button:B,link:L}=UI;
 const clone=x=>JSON.parse(JSON.stringify(x));
 const scenario=new URLSearchParams(location.search).get('scenario')||'default';
 const KEY='jianji-design-v4:'+(new URLSearchParams(location.search).get('gallery')==='1'?'gallery:'+String(new URLSearchParams(location.search).get('theme'))+':':'')+scenario;
 const uid=p=>p+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,6);
 let state=D.defaultState(),route='home',params={},stack=[],scrolls={},noticeTimer,dialogCallback=null,lastFocus=null,forceSaveFailure=scenario==='save-failure';
 const busyTimers=new Map();
 let expectedRaw=undefined;
 const api={externalChange:false,storageBlocked:false,corruptRaw:null,unsavedDraft:false,pendingAnswer:null,formDrafts:{},simFactor:'A',simValue:50,getSession:id=>state.sessions.find(x=>x.id===(id||state.activeSession)),orderLabel:o=>o.payment==='refunded'?'模拟已退款':o.payment==='refunding'?'模拟退款处理中':o.payment==='paid'?(o.entitlement==='active'?'模拟已生效':'模拟已支付 · 权益待生效'):'待核验 · 演示订单'};
 const seedSession=(answers={},status='in-progress',index=0)=>({id:'session-demo-seed',mode:'original',version:'demo-3-v1',kind:'interaction-demo',answers,status,index,createdAt:'2026-10-01T09:00:00+08:00',updatedLabel:'本机演示答卷'});
 function seed(s){
  if(s==='combined'){seed('resume');seed('ongoing-action');return;}
  if(s==='mixed-records'){seed('complete');seed('topic-record');return;}
  if(['resume','question','save-failure'].includes(s)){const x=seedSession({'demo-q1':'b'},'in-progress',s==='resume'?1:0);state.sessions=[x];state.activeSession=x.id;}
  if(s==='complete'){const x=seedSession({'demo-q1':'b','demo-q2':'a','demo-q3':'c'},'completed',2);state.sessions=[x];state.activeSession=x.id;}
  if(['source-login','quota'].includes(s)){state.assistantDraft='我想知道，什么条件会让我表达得更清楚？';state.assistantSources=[D.reportSource('work')];}
  if(s==='quota'){state.logged=true;state.used=10;}
  if(s==='history'){state.logged=true;state.used=1;state.conversations=[{id:'conversation-demo-history',title:'准备时间与表达',persist:true,draft:'',draftSources:[],updatedLabel:'本机虚构历史样例',messages:[{id:'message-demo-user',role:'user',text:'我需要一点准备时间，才能把理由说明白。',sources:[],createdAt:'2026-10-01T09:00:00+08:00'},{id:'message-demo-assistant',role:'assistant',text:'这段文字是独立预写演示，不是模型判断。\n\n可以先观察两个具体条件：话题熟不熟悉，以及有没有时间整理要点。然后由你决定哪种描述更贴近自己的经历。',sources:[],requestId:'request-demo-history'}]}];}
  if(['ongoing-action','action-review'].includes(s)){state.actions=[{id:'action-demo-v2',text:'下次讨论前，先写两个要点，看看是否更容易说清楚。',status:s==='ongoing-action'?'active':'reviewed',sourceId:'report-sample-01',sourceKind:'sample-report',createdAt:'2026-10-01T09:00:00+08:00',reviews:s==='action-review'?[{id:'review-demo-v2',outcome:'no-change',text:'演示观察：列出了要点，但临时追问时仍然需要整理时间。下次想试着先确认问题。',createdAt:'2026-10-02T09:00:00+08:00'}]:[]}];}
  if(s==='topic-record'){state.observations=[{id:'topic-note-demo-v2',kind:'topic-record',topicId:'work-choice',title:'工作选择 · 我的整理（演示）',fields:{options:'演示：留在现有团队，或尝试新的岗位。',priorities:'希望保留学习空间，也看重相对稳定的安排。',limits:'需要保留家庭时间，不能只比较岗位名称。',unknown:'新岗位实际负责什么？每周投入和通勤怎样？'},text:'正在比较什么\n演示：留在现有团队，或尝试新的岗位。\n\n最在意的两件事\n希望保留学习空间，也看重相对稳定的安排。\n\n暂时不能忽略的条件\n需要保留家庭时间，不能只比较岗位名称。\n\n决定前，还要弄清什么\n新岗位实际负责什么？每周投入和通勤怎样？',revision:1,createdAt:'2026-10-01T09:00:00+08:00'}];}
  if(s==='paid-annual'){state.logged=true;state.plan='monthly';state.orders=[{id:'DEMO-ANNUAL-001',plan:'annual',planVersion:'proposal-v1',payment:'paid',entitlement:'active',returnTo:'assistant',createdAt:'2026-10-01T09:00:00+08:00'}];}
 }
 function serial(s){const out=clone(s);out.conversations=out.conversations.filter(c=>c.persist!==false).map(c=>({...c,pendingRequest:c.generating?c.requestId:null,generating:false}));return out;}
 function persist(next=state,{answer=false}={}){if(api.storageBlocked||api.externalChange)return false;try{const present=localStorage.getItem(KEY);if(expectedRaw!==undefined&&present!==expectedRaw){api.externalChange=true;renderStorageStatus();return false;}if(answer&&forceSaveFailure)throw new Error('simulated-write-failure');const raw=JSON.stringify(serial(next));localStorage.setItem(KEY,raw);expectedRaw=raw;return true;}catch(e){return false;}}
 function commit(change,msg='',quiet=false){const next=clone(state);change(next);if(persist(next)){state=next;if(msg)toast(msg);return true;}if(!quiet)toast('尚未保存成功，当前输入仍在。请导出临时内容或释放空间后重试。');return false;}
 function init(){
  const reset=new URLSearchParams(location.search).get('reset')==='1';let raw=null;
  try{if(reset)localStorage.removeItem(KEY);raw=localStorage.getItem(KEY);expectedRaw=raw;if(raw){state=V2.normalize(JSON.parse(raw));}else{seed(scenario);if(!persist())api.unsavedDraft=true;}}
  catch(e){if(raw){api.storageBlocked=true;api.corruptRaw=raw;}else api.unsavedDraft=true;}
  const requestedTheme=new URLSearchParams(location.search).get('theme');if(D.themes.some(t=>t.id===requestedTheme)&&state.theme!==requestedTheme){state.theme=requestedTheme;if(!persist())api.unsavedDraft=true;}
  const url=new URL(location.href);url.searchParams.delete('reset');if(url.searchParams.get('gallery')!=='1')url.searchParams.delete('theme');history.replaceState({jj:true,index:0},'',url.href);
  const today=new Date().toLocaleDateString('en-CA');if(!api.storageBlocked&&state.usageDay!==today){state.usageDay=today;state.used=0;persist();}
  parse();render();
  window.addEventListener('hashchange',()=>{if(api.pendingAnswer){history.replaceState(history.state,'','#question?id='+api.pendingAnswer.sessionId);toast('未保存的选择仍保留，请先重试或导出。');}parse();close();render(true);});
  window.addEventListener('storage',e=>{if(e.key===KEY&&e.newValue!==expectedRaw){api.externalChange=true;renderStorageStatus();V4.notify();}});
  window.addEventListener('beforeunload',e=>{if(api.externalChange||api.pendingAnswer||api.unsavedDraft||V2.hasUnsaved){e.preventDefault();e.returnValue='';}});
 }

 function parse(){const [r,q]=(location.hash.slice(1)||'home').split('?');route=r||'home';params=Object.fromEntries(new URLSearchParams(q||''));if(route==='question'&&!params.id&&api.getSession())params.id=state.activeSession;}
 function current(){return route+(Object.keys(params).length?'?'+new URLSearchParams(params):'');}
 function nav(r,p={},replace=false){if(api.pendingAnswer){show('先留住这次选择','<p>这次选择仍未保存。请回到答题重试，或先导出临时答案。不会悄悄丢弃你的选择。</p>',B('回到答题','close-dialog',{cls:'btn full'})+B('导出临时答案','rescue',{cls:'btn secondary full space-12'}));return;}
  scrolls[current()]=window.scrollY;const target=r+(Object.keys(p).length?'?'+new URLSearchParams(p):'');if(!replace&&target!==current())stack.push(current());if(!replace)history.pushState({jj:true,index:(history.state?.index||0)+1},'','#'+target);else history.replaceState(history.state||{jj:true,index:0},'','#'+target);parse();close();render(true);}
 function back(){
  if(api.pendingAnswer){nav('home');return;}
  if(history.state?.jj && history.state.index>0){history.back();return;}
  const root=['conversation','conversations','auth','memories'].includes(route)?'assistant':['topic','topic-workspace'].includes(route)?'explore':['action-detail','actions'].includes(route)?'me':['settings','appearance','account','data','orders','order','privacy','membership','journal','portrait'].includes(route)?'me':'home';nav(root,{},true);
 }

 function render(restore=false){document.body.className='theme-'+state.theme+(state.reduced?' reduce-motion':'');document.documentElement.style.setProperty('--font-scale',state.fontSize==='large'?'1.14':'1');
  const root=Views.isRoot(route),q=route==='question';let html=Views.render(route,state,params);if(state.avatarFamily==='original')html=html.replace(/src="assets\/person-([123])\.svg"/g,'src="assets/original-person-$1.webp"');let footer='';if(q){const x=api.getSession(params.id),question=x&&D.questions[x.index];if(x&&question){const selected=x.answers[question.id];footer=`<div class="task-footer"><div class="task-actions">${B('上一题','question-prev',{cls:'btn secondary',disabled:x.index===0})}${B(x.index===2?'检查这次作答':'下一题','question-next',{cls:'btn',after:'arrow',disabled:!selected||!!api.pendingAnswer})}</div></div>`;}}
  document.getElementById('app').innerHTML=`<div class="screen ${root?'has-tabs':''} ${q?'question-screen':''}"><main class="page" id="main-content" tabindex="-1"><div id="storage-status"></div>${html}</main>${root?UI.tabs(route):footer}</div>`;
  document.title=({home:'认识',explore:'探索',assistant:'助理',me:'我的',report:'报告样例',question:'答题体验'}[route]||'自我理解')+' · 知遇';renderStorageStatus();V3.afterRender();V4.afterRender();if(restore){window.scrollTo(0,scrolls[current()]||0);const h=document.querySelector('main h1')||document.getElementById('main-content');h?.setAttribute('tabindex','-1');h?.focus({preventScroll:true});}
 }
 function repaint(){const y=scrollY,focused=document.activeElement;const a=focused?.dataset?.action,id=focused?.dataset?.id,outcome=focused?.dataset?.outcome;render();window.scrollTo(0,y);if(a){document.querySelector('[data-action="'+CSS.escape(a)+'"]'+(id?'[data-id="'+CSS.escape(id)+'"]':'')+(outcome?'[data-outcome="'+CSS.escape(outcome)+'"]':''))?.focus({preventScroll:true});}}
 function renderStorageStatus(){
  const host=document.getElementById('storage-status');if(!host)return;
  const failed=api.unsavedDraft||V2.hasUnsaved;
  host.innerHTML=api.externalChange?`<div class="storage-alert" role="alert"><p>另一个页面已更新这份资料。当前窗口已暂停写入，避免覆盖新内容。</p><div class="alert-actions">${B('导出当前窗口内容','export-recovery',{cls:'btn secondary compact'})}${B('重新载入最新资料','v4-reload-latest',{cls:'textbtn'})}</div></div>`:api.storageBlocked?`<div class="storage-alert" role="alert"><p>本机数据暂时无法读取。原始内容未覆盖，请先导出恢复文件。</p><div class="alert-actions">${B('导出恢复文件','export-recovery',{cls:'btn secondary compact'})}${B('清理当前异常数据','reset-corrupt',{cls:'textbtn'})}</div></div>`:failed?`<div class="storage-alert" role="alert"><p>有内容尚未保存到本机。请勿关闭页面。</p><div class="alert-actions">${B('重试保存','retry-drafts',{cls:'btn secondary compact'})}${B('导出临时内容','export-recovery',{cls:'textbtn'})}</div></div>`:'';
 }
 function cancelRequest(id){const timer=busyTimers.get(id);if(timer)clearTimeout(timer);busyTimers.delete(id);}
 function cancelAll(){for(const timer of busyTimers.values())clearTimeout(timer);busyTimers.clear();}
 function toast(text){const n=document.getElementById('notice');n.textContent=text;n.className='show';clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>n.className='',4400);}
 function show(title,content,actions=''){lastFocus=document.activeElement;document.getElementById('app').inert=true;document.getElementById('overlays').innerHTML=`<div class="overlay"><section class="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title"><div class="dialog-head"><h2 id="dialog-title">${esc(title)}</h2>${B('','close-dialog',{cls:'iconbtn',icon:'close','aria-label':'关闭弹层'})}</div><div class="dialog-content">${content}</div><div class="dialog-actions">${actions||B('知道了','close-dialog',{cls:'btn full'})}</div></section></div>`;document.body.style.overflow='hidden';document.querySelector('.dialog textarea,.dialog input,.dialog button')?.focus();}
 function close(){api.factorPickerMode=null;document.getElementById('overlays').innerHTML='';document.getElementById('app').inert=false;document.body.style.overflow='';if(lastFocus?.isConnected)lastFocus.focus();dialogCallback=null;}
 function confirm(title,content,fn,label='确认'){show(title,content,B(label,'confirm-dialog',{cls:'btn full'})+B('先取消','close-dialog',{cls:'btn secondary full space-12'}));dialogCallback=fn;}
 function form(title,label,value,fn,description=''){show(title,`<p class="small muted">${description}</p><label class="field-label space-16" for="dialog-field">${label}</label><textarea id="dialog-field" class="textarea" maxlength="1500">${esc(value||'')}</textarea>`,B('保存到本机','submit-dialog',{cls:'btn full'})+B('取消','close-dialog',{cls:'btn secondary full space-12'}));dialogCallback=fn;}
 function download(name,text,type='application/json'){const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),20000);toast('已将文件交给浏览器下载；请在下载记录中确认。');}
 function currentConversation(){return route==='conversation'?state.conversations.find(c=>c.id===params.id):null;}
 function draftTarget(){return currentConversation()||{draft:state.assistantDraft,draftSources:state.assistantSources};}
 function saveDraft(value){const c=currentConversation();if(c)c.draft=value;else state.assistantDraft=value;api.unsavedDraft=!persist();renderStorageStatus();}
 function validSource(src){if(src.status!=='valid')return false;if(src.kind==='memory')return state.memories.some(m=>m.id===src.objectId&&m.status==='active'&&String(m.revision||1)===src.version);if(src.kind==='self-note')return [...state.observations,...state.reportNotes].some(n=>n.id===src.objectId&&String(n.revision||1)===src.version);return true;}
 function addSource(src){if(!validSource(src)){toast('这份资料已不可用，不会加入引用。');return;}const c=currentConversation();const sources=c?c.draftSources:state.assistantSources;const i=sources.findIndex(x=>x.id===src.id);if(i<0)sources.push(clone(src));else sources[i]=clone(src);if(!persist())api.unsavedDraft=true;renderStorageStatus();}
 function selectContext(){const activeMem=state.memories.filter(m=>m.status==='active');let rows=[D.reportSource('work'),D.reportSource('relationship')];state.observations.slice(-4).forEach(o=>rows.push({id:'observation-'+o.id,kind:'self-note',objectId:o.id,version:String(o.revision||1),title:'本人观察 · '+o.title,excerpt:o.text,status:'valid',scope:'仅本次引用'}));activeMem.forEach(m=>rows.push({id:'memory-'+m.id,kind:'memory',objectId:m.id,version:String(m.revision||1),title:'已确认记忆',excerpt:m.text,status:'valid',scope:'本次显式选择'}));api.contextChoices=rows;
  show('这次，想参考什么？','<p class="small muted">只选择与问题有关的资料。不会自动读取全部历史或把引用变成记忆。</p><div class="plain-list space-16">'+rows.map(x=>`<button class="list-item" data-action="pick-context" data-id="${esc(x.id)}"><span class="grow"><strong>${esc(x.title)}</strong><span class="sub" style="display:block">${esc(x.excerpt.slice(0,60))}…</span></span>${icon('plus')}</button>`).join('')+'</div>');}
 function beginSession(){const prior=api.getSession();if(prior?.status==='in-progress'){nav('question',{id:prior.id});return;}const x={id:uid('session'),kind:'interaction-demo',version:'demo-3-v1',mode:state.mode,status:'in-progress',index:0,answers:{},createdAt:new Date().toISOString(),updatedLabel:'本机答题体验'};if(commit(s=>{s.sessions.push(x);s.activeSession=x.id;})){nav('question',{id:x.id});}}
 function answer(choice){const x=api.getSession(params.id);if(!x||x.status==='completed')return;const q=D.questions[x.index];if(!q.options.some(o=>o[0]===choice))return;const pending={sessionId:x.id,qid:q.id,choice};const next=clone(state);const target=next.sessions.find(s=>s.id===x.id);target.answers[q.id]=choice;target.updatedAt=new Date().toISOString();if(persist(next,{answer:true})){state=next;api.pendingAnswer=null;}else api.pendingAnswer=pending;repaint();document.querySelector(`[data-action="answer"][data-id="${choice}"]`)?.focus({preventScroll:true});}
 function quota(){show('分析与聊天，共用一个额度',`<div class="card"><p>未登录：AI 功能不可调用。</p><p class="space-12">登录后的免费账户：分析 + 聊天每日合计 10 次。</p><p class="space-12">本机演示已用 ${state.used} 次，剩余 ${Math.max(0,10-state.used)} 次。</p></div><p class="small muted space-16">当前只是本机演示计数，不是可防绕过的服务端限额。真实失败、取消、重复请求的结算方式、重置时区和付费额度仍待明确。</p>`,L('查看用量明细','usage',{cls:'btn secondary full'})+B('继续原来的任务','close-dialog',{cls:'btn full space-12'}));}
 function usage(){show('本机演示用量',state.usage.length?state.usage.slice().reverse().map(x=>`<div class="record-item"><strong>${x.kind==='analysis'?'按需解析':'聊天'} · ${esc(x.status||'已返回演示')}</strong><p class="small muted">${esc(x.id)} · ${esc(x.createdAt)}</p></div>`).join(''):'<p>还没有本机演示请求记录。场景预设可能设置“剩余 0 次”，但不是实际账单。</p>');}
 function send(){const target=draftTarget();const draft=target.draft.trim();if(!draft){toast('先写下一件想整理的事。');document.querySelector('#chat-draft')?.focus();return;}if(!state.logged){state.returnAfterAuth=current();persist();nav('auth');return;}if(state.used>=10){show('今天的免费演示额度已用完','<p>你的问题和引用仍保留在原处。可以继续看已有记录，也可以先写下观察。</p><p class="small muted space-12">本轮不出售真实会员。正式产品需明确额度重置规则与购买权益。</p>',B('保留草稿，继续看看','close-dialog',{cls:'btn full'})+L('了解使用与会员规则','membership',{cls:'btn secondary full space-12'}));return;}
  let c=currentConversation();if(c?.generating){toast('演示正在返回。可先停止，不重复发送。');return;}let sources=clone(target.draftSources).filter(validSource);
  if(sources.length!==target.draftSources.length){show('有一条引用已失效','<p>停用或删除后的来源不会继续采用。先检查本次资料，再由你决定是否发送。</p>');if(c)c.draftSources=sources;else state.assistantSources=sources;persist();return;}
  const id=c?.id||uid('conversation'),requestId=uid('request'),user={id:uid('message'),role:'user',text:draft,sources:clone(sources),createdAt:new Date().toISOString()};
  const next=clone(state);if(!c){next.conversations.push({id,title:draft.slice(0,22),persist:state.chatRetention,draft:'',draftSources:[],messages:[],updatedLabel:'本机演示对话'});}const nc=next.conversations.find(x=>x.id===id);nc.messages.push(user);nc.draft='';nc.draftSources=[];nc.generating=true;nc.requestId=requestId;next.assistantDraft=c?next.assistantDraft:'';next.assistantSources=c?next.assistantSources:[];next.used++;next.usage.push({id:requestId,kind:'chat',status:'预写演示请求',createdAt:new Date().toISOString()});
  if(!persist(next)){toast('请求未发出，草稿仍保留。请先处理本机保存问题。');return;}state=next;nav('conversation',{id});busyTimers.set(requestId,setTimeout(()=>{busyTimers.delete(requestId);
   const x=state.conversations.find(x=>x.id===id);if(!x||!x.generating||x.requestId!==requestId||!state.logged)return;
   if(!sources.every(validSource)){x.generating=false;x.messages.push({id:uid('message'),role:'assistant',text:'在这次演示返回前，有资料已被删除、停用或修改。本次不再根据旧来源生成建议，也不会提出旧来源的记忆。请重新选择资料。',sources:[],status:'stopped'});const u=state.usage.find(u=>u.id===requestId);if(u)u.status='来源变化，中止演示';if(!persist())api.unsavedDraft=true;if(route==='conversation'&&params.id===id)repaint();renderStorageStatus();return;}
   const response=sources.length?'你带来的资料提供了一个具体情境，但它不能替你下结论。\n\n我们可以先把问题拆小：当时发生了什么，你最在意哪一点，有没有别的解释？从一件真实的小事开始，比急着给自己贴标签更有帮助。\n\n一个可选的小尝试：下次表达前，先写两个要点，再观察是否更容易说清楚。也可以把这条建议改成适合自己的方式。':'先把“我是不是总是这样”，换成“最近哪件事让我有这种感觉”。\n\n可以记录三个细节：当时发生了什么、你需要什么、还有哪一条信息没有弄清楚。暂时不用作人格判断。\n\n这段回复是预写演示，不是对你输入的智能分析。';
   x.messages.push({id:uid('message'),role:'assistant',text:response,sources:clone(sources),requestId});x.generating=false;state.usage.find(u=>u.id===requestId).status='已返回预写演示';if(!persist())api.unsavedDraft=true;if(route==='conversation'&&params.id===id)repaint();renderStorageStatus();
  },650));
 }
 function sourceDetails(src){show('这段内容来自哪里',`<span class="pill outline">${esc(src.kind||'演示来源')}</span><h3 class="space-16">${esc(src.title)}</h3><blockquote class="quote">${esc(src.excerpt)}</blockquote><dl class="order-facts"><dt>原对象</dt><dd>${esc(src.objectId)}</dd><dt>版本</dt><dd>${esc(src.version)}</dd><dt>片段</dt><dd>${esc(src.sectionId||'全文记录')}</dd><dt>引用范围</dt><dd>${esc(src.scope||'本次请求快照')}</dd></dl><p class="small muted">选择摘要与实际采用的来源要分开显示。本轮快照是预写演示使用的上下文，不代表真实模型已经读过。</p>`);}
 function exportPreview(){show('先确认导出范围',`<p>生成明文 JSON，不含真实认证信息。本机演示资料也可能包含你输入的文字，请妥善保存。</p><div class="plain-list space-16">${[['sessions','体验答卷与暂停进度'],['notes','本人观察、报告补充与编辑草稿'],['conversations','已保存演示对话'],['memories','记忆与小尝试'],['orders','演示订单快照']].map(([id,label])=>`<label class="export-option"><input type="checkbox" name="export-group" value="${id}" ${id==='conversations'?'':'checked'}> ${label}</label>`).join('')}</div>`,B('生成选定范围的文件','export-data',{cls:'btn full'})+B('取消','close-dialog',{cls:'btn secondary full space-12'}));}
 const specs={
 'auth-spec':['登录不是一次资料外发','真实流程：输入账号 → 验证凭据 → 告知条款与资料范围 → 识别访客空间归属 → 返回原草稿。不要代填真实密码，不自动合并访客资料，不因为登录而自动发送 AI。当前仅有本机演示身份。'],
 'context-spec':['三个独立的决定','本次引用：这一条请求携带哪些具体记录。聊天留存：对话是否保存、保存到哪里。长期记忆：哪些认识可在后续使用。三者不能捆绑授权。撤回某条来源，需要阻止新任务以及尚未返回的旧任务继续采用。'],
 'import-spec':['导入，需要先预检','正式实现：识别格式与版本 → 预览条数和来源空间 → 检查 ID 冲突 → 逐类选择保留或合并 → 事务写入 → 返回逐项结果。出错回滚，不能只提示导入成功。不从备份恢复身份令牌或购买权益。本轮未实现导入。'],
 'sync-spec':['备份不等于同步','本轮只有本机保存与文件导出。正式方案必须分别说明应用云端、用户云盘、系统备份、换机恢复的边界。离线更改的冲突要先预览；没有同步服务，不能显示“已同步”。'],
 'restore-spec':['恢复购买，不是恢复数据','真实恢复流程核验账号、渠道与原交易，再恢复已买权益；不会重新付款，也不会自动恢复本机聊天与答卷。当前没有真实购买渠道，不能执行恢复。'],
 'delete-account-spec':['删除要告诉你：删哪里','区分本机资料、应用账号、服务端副本、模型供应商留存以及已导出文件。真实流程需要身份验证、范围确认、在途任务隔离、提交记录、处理进度和失败重试。这里没有接入真实账号注销，不会伪装已删除云端数据。'],
 'recover-spec':['恢复账号的方案','真实登录方式确定后，再设计验证、限频、恢复材料、恢复后的会话失效及原资料归属。不能用本机一个按钮假称找回真实账号。'],
 'device-spec':['设备私密保护 · 候选能力','可考虑调用系统生物识别或设备凭据控制查看；不自制伪加密密码。未接入前不显示“已安全保护”。不影响应用数据导出与账号恢复规则。'],
 'demo-boundary':['本轮能力边界','可用：本机答题、暂停恢复、引用草稿、确认记忆、记录与导出、主题切换。模拟：演示登录、预写聊天、额度、订单状态。未接入：正式题源计分常模、真实账号、模型、支付退款、跨端同步、通知。'],
 'save-help':['先保留，再修复','存储失败时不清空选择，不允许把未保存标成成功。答题可重试或导出临时答案；文本草稿留在当前窗口。不要刷新或关闭未保存内容。可以先导出已有资料，再清理无关的浏览器存储。'],
 'terms-spec':['正式协议尚未替代','这是一份设计原型，不是正式隐私政策、服务条款或专业评估工具。上线前需根据实际题源许可、数据接收方、适用人群、计费规则与支持能力制定文本。'],
 'inactive-info':['停用之后会怎样','这条记忆不再出现在新的可选引用中。已经发生的对话快照仍保留原貌，但会标识来源已停用；不能让在途任务把它重新生成为有效记忆。正式服务还需传播到服务端与检索索引。'],
 'refund-info':['申请与到账，是两个状态','本机演示仅到“退款处理中”。正式流程需显示申请编号、核验结果、渠道退款状态以及对应权益处理；提交申请不等于已到账。'],
 'correct-response':['建议不符合，可以纠正','这段回复是预写内容，并不了解你的真实情况。你可以在输入框补充哪一点不适用，也可以不采用建议。原对话保留；纠正不改写正式测评分数。']
 };
 function dispatch(action,el){if(V4.dispatch(action,el)||V3.dispatch(action,el)||V2.dispatch(action,el))return;const id=el?.dataset.id,ds=el?.dataset||{};
  if(action==='nav'){if(ds.filter){const allowed=['本人记录','全部答卷','全部','体验答卷','未完成'];if(allowed.includes(ds.filter)&&!commit(s=>s.recordFilter=ds.filter))return;}if(ds.route==='usage'){close();usage();return;}const p={};['id','topic','kind','tab'].forEach(k=>{if(ds[k])p[k]=ds[k];});nav(ds.route,p);return;}
  if(action==='tab'){nav(ds.route);return;}if(action==='back'){back();return;}if(action==='close-dialog'){close();return;}
  if(action==='confirm-dialog'){const fn=dialogCallback;if(fn){close();fn();}return;}
  if(action==='submit-dialog'){const txt=document.getElementById('dialog-field')?.value.trim();if(!txt){toast('写一点内容再保存。');return;}const fn=dialogCallback;if(fn&&fn(txt)!==false){close();repaint();}return;}
  if(specs[action]){show(specs[action][0],`<p>${specs[action][1]}</p>`);return;}
  switch(action){
   case 'mode': if(commit(s=>s.mode=id))repaint();break;
   case 'start': case 'start-new': beginSession();break;
   case 'resume': {const x=api.getSession();if(x)nav('question',{id:x.id});break;}
   case 'answer':answer(id);break;
   case 'retry-save':{if(api.pendingAnswer){forceSaveFailure=false;answer(api.pendingAnswer.choice);}break;}
   case 'rescue':download('jianji-unsaved-answer.json',JSON.stringify({kind:'temporary-unsaved-answer',version:'demo-3-v1',pending:api.pendingAnswer,session:api.getSession(params.id),warning:'未保存内容；不是正式计分结果'},null,2));break;
   case 'pause':if(api.pendingAnswer){nav('home');}else confirm('停在这里，也可以','<p>已保存的答案和位置会保留在本机。下次继续同一份体验答卷，不会重新开始。</p>',()=>nav('home'),'保存位置，返回认识');break;
   case 'question-prev': case 'question-next':{const x=api.getSession(params.id);if(!x||api.pendingAnswer)return;if(action==='question-next'&&!x.answers[D.questions[x.index].id])return;if(action==='question-next'&&x.index===2){nav('review',{id:x.id});return;}const index=x.index+(action==='question-next'?1:-1);if(index<0||index>2)return;if(commit(s=>s.sessions.find(t=>t.id===x.id).index=index)){render(true);}break;}
   case 'edit-answer':{const x=api.getSession(id);if(!x||x.status==='completed')return;if(commit(s=>s.sessions.find(t=>t.id===id).index=Number(ds.index)))nav('question',{id});break;}
   case 'finish':{const x=api.getSession(id);if(x&&Object.keys(x.answers).length===3&&commit(s=>s.sessions.find(t=>t.id===id).status='completed'))nav('complete',{id});break;}
   case 'category':if(commit(s=>s.exploreCategory=id))repaint();break;
   case 'clear-search':if(!state.exploreSearch){show('从一个问题开始','<p>可以输入关键词，也可以选择工作、相处、学习或生活分类。筛选只影响当前浏览，不会更改你的记录。</p>');}else{state.exploreSearch='';persist();repaint();}break;
   case 'clear-filters':state.exploreSearch='';state.exploreCategory='全部';persist();repaint();break;
   case 'favorite':if(commit(s=>{s.favorites=s.favorites.includes(id)?s.favorites.filter(x=>x!==id):[...s.favorites,id];}))repaint();break;
   case 'favorites':show('收藏的方向',state.favorites.length?state.favorites.map(id=>{const t=D.topics.find(t=>t.id===id);return UI.row(t.title,'内容策划，正式题组未上线','topic','bookmark','',{'data-id':id});}).join(''):'<p>还没有收藏。在专题详情中可以留下感兴趣的方向。</p>');break;
   case 'daily':show('每日轻探索','<p>正式内容就绪后，按日期生成一份固定的小题组：当天重进不换题，暂停保留原选择；与完整测评分开记录。</p><p class="small muted space-16">本轮未提供获准的正式题组，不能伪造一份每日测评。现在可以先留下一句自己的观察，它不冒充测评结果。</p>',L('给今天留一句话','journal',{cls:'btn full','data-kind':'daily'})+B('先返回','close-dialog',{cls:'btn secondary full space-12'}));break;
   case 'topic-journal':nav('journal',{topic:id});break;
   case 'all-factors':case 'sim-factors':api.factorPickerMode=action;show(action==='sim-factors'?'换一个假设角度':'先了解一个因子','<p class="small muted">中文名为界面工作译名。位置均为独立示意，不是你的得分。</p>'+UI.bottleGrid());break;
   case 'factor':{const f=D.factors.find(x=>x[0]===id);if(!f){toast('这个因子不存在，不替换为其他因子。');return;}if(api.factorPickerMode==='sim-factors'){api.factorPickerMode=null;api.simFactor=id;close();repaint();return;}api.factorPickerMode=null;show(`${f[0]} · ${f[1]}`,`<div class="center"><div style="width:75px;margin:10px auto">${UI.bottle(f)}</div><h3>${esc(f[4])}</h3></div><p class="space-16">${f[2]===null?'这个角度暂无测量依据，不能用零分替代。':'瓶中水位只是独立样例的视觉位置，不代表你，也不表示优秀程度。'}</p><p class="small muted space-16">当前对象：factor:${f[0]}。正式定义、题源与计分范围待核对。本轮不从三道演示题计算这个因子。</p>`,B('用这个角度做个假设','factor-sim',{cls:'btn full','data-id':id})+B('回到刚才的位置','close-dialog',{cls:'btn secondary full space-12'}));break;}
   case 'factor-sim':api.simFactor=id;close();nav('simulation');break;
   case 'report-context':state.reportContext=id;persist();repaint();break;
   case 'source-report':sourceDetails(D.reportSource(state.reportContext));break;
   case 'quote-report':{const src=D.reportSource(state.reportContext);if(!state.assistantSources.some(x=>x.id===src.id))state.assistantSources.push(src);if(!state.assistantDraft)state.assistantDraft='我想结合这段情境，看看自己可以观察些什么。';persist();nav('assistant');break;}
   case 'article-quote':{const src={id:'source-article-read-traits-quote1',kind:'article',objectId:'read-traits',version:'article-demo-v1',sectionId:'quote-1',title:'阅读示例 · 高低不代表更好',excerpt:document.getElementById('article-excerpt').textContent,status:'valid',scope:'仅本次引用，不自动发送'};if(!state.assistantSources.some(x=>x.id===src.id))state.assistantSources.push(src);if(!state.assistantDraft)state.assistantDraft='我想聊聊“情境不同，表达也不同”这段话。';persist();nav('assistant');break;}
   case 'save-report-note':{const text=(api.formDrafts.reportNote||'').trim();if(!text){toast('先写下你自己的补充。');return;}if(commit(s=>s.reportNotes.push({id:uid('note'),title:'对报告样例的本人补充',text,sourceId:D.report.id,sectionId:s.reportContext,revision:1,createdAt:new Date().toISOString()}),'本人补充已保存在本机，不会改写测评分数。')){delete api.formDrafts.reportNote;repaint();}break;}
   case 'record-filter':state.recordFilter=id;persist();repaint();break;
   case 'theme':if(D.themes.some(t=>t.id===id)&&commit(s=>s.theme=id))repaint();break;
   case 'avatar':if([1,2,3].includes(Number(id))&&commit(s=>{s.avatar=Number(id);if(['original','scene'].includes(ds.family))s.avatarFamily=ds.family;}))repaint();break;
   case 'toggle-motion':if(commit(s=>s.reduced=!s.reduced))repaint();break;
   case 'font-size':if(commit(s=>s.fontSize=id))repaint();break;
   case 'edit-name':form('你希望怎么被称呼？','称呼',state.name,txt=>commit(s=>s.name=txt.slice(0,20)),'只是本机显示名，不是真实姓名认证。');break;
   case 'prompt':if(id==='report'){selectContext();}else{if(!state.assistantDraft)state.assistantDraft='最近有一件事，我想先说一说：';persist();repaint();document.querySelector('#chat-draft')?.focus();}break;
   case 'context':selectContext();break;
   case 'pick-context':{const src=api.contextChoices.find(s=>s.id===id);if(src){addSource(src);close();repaint();}break;}
   case 'remove-source':{const c=currentConversation();if(c)c.draftSources=c.draftSources.filter(x=>x.id!==id);else state.assistantSources=state.assistantSources.filter(x=>x.id!==id);if(!persist())api.unsavedDraft=true;repaint();break;}
   case 'quota':quota();break;
   case 'send':send();break;
   case 'demo-login':if(commit(s=>s.logged=true)){const [r,q]=(state.returnAfterAuth||'assistant').split('?');nav(r,Object.fromEntries(new URLSearchParams(q||'')),true);toast('仅启用本机演示身份。草稿尚未发送。');}break;
   case 'logout':confirm('退出演示身份？','<p>保留本机空间的答卷与草稿。停止本窗口在途演示，不自动发送。真实多账号数据隔离不在本轮运行范围。</p>',()=>{cancelAll();commit(s=>{s.logged=false;s.conversations.forEach(c=>c.generating=false);});repaint();},'退出演示');break;
   case 'stop':{const c=currentConversation();if(c){cancelRequest(c.requestId);c.generating=false;const u=state.usage.find(x=>x.id===c.requestId);if(u)u.status='已停止（演示计数保留）';persist();repaint();toast('已停止演示。原问题仍在对话中，不自动重发。');}break;}
   case 'conversation-settings':{const c=currentConversation();if(c)show('这段对话',`<p>对话编号：${esc(c.id)}</p><p class="space-12">${c.persist===false?'仅在当前窗口内展示，不写入本机持久化。':'保存在当前本机演示空间。'}</p><p class="small muted space-16">历史消息按原对象打开，不替换成新的欢迎页。删除只作用于本机这段对话，不会假称已删除服务端副本。</p>`,B('删除本机这段对话','delete-conversation',{cls:'btn secondary full','data-id':c.id})+L('查看引用与留存设置','privacy',{cls:'btn full space-12'}));break;}
   case 'delete-conversation':confirm('删除这段本机对话？','<p>这段对话及草稿将从当前演示空间移除。关联记忆会停用，不删除其他个人记录。</p>',()=>{const requestId=state.conversations.find(c=>c.id===id)?.requestId;if(commit(s=>{s.conversations=s.conversations.filter(c=>c.id!==id);s.memories.forEach(m=>{if(m.sourceId===id)m.status='inactive';});})){cancelRequest(requestId);nav('conversations');}},'删除本机对话');break;
   case 'message-source':{const c=currentConversation(),m=c?.messages.find(x=>x.id===id);if(m){const list=m.sources||[];show('这一条回复的来源快照',list.length?list.map(src=>`<h3>${esc(src.title)}</h3><blockquote class="quote">${esc(src.excerpt)}</blockquote><p class="small muted">${esc(src.objectId)} · ${esc(src.version)}${src.kind==='memory'&&!state.memories.some(m=>m.id===src.objectId&&m.status==='active')?' · 来源已停用/删除，不再供新任务采用':''}</p>`).join(''):'<p>这条预写演示没有采用额外资料。消息不会冒用当前新选择的来源。</p>');}break;}
   case 'candidate-memory':{if(!state.memoryEnabled){show('长期记忆候选尚未开启','<p>聊天记录不会自动成为记忆。开启后，仍需逐条确认。当前不会写入候选。</p>',L('查看引用与记忆设置','privacy',{cls:'btn full'})+B('先不记住','close-dialog',{cls:'btn secondary full space-12'}));return;}const c=currentConversation();const msg=c?.messages.find(m=>m.id===id);if(msg?.sources?.some(src=>!validSource(src))){show('来源已变化','<p>这条消息关联的来源已修改、停用或删除，不能再从旧来源提出有效记忆。请重新选择资料。</p>');return;}form('先确认，这是不是你的认识','可修改的候选内容','我想观察：准备时间是否影响我表达的清晰程度。',txt=>commit(s=>s.memories.push({id:uid('memory'),text:txt,status:'candidate',sourceId:c?.id,sourceMessageId:id,sourceType:'本人修改的演示候选',sourceTitle:c?.title||'本人补充',revision:1}),'仅保存为候选，尚未成为有效记忆。'),'这是预写建议，不是 AI 从你身上得出的事实。保存为候选后，还需确认采用。');break;}
   case 'confirm-memory':if(commit(s=>{const m=s.memories.find(x=>x.id===id);if(m&&m.status==='candidate')m.status='active';}))repaint();break;
   case 'deactivate-memory':if(commit(s=>{const m=s.memories.find(x=>x.id===id);if(m)m.status='inactive';s.assistantSources=s.assistantSources.filter(x=>!(x.kind==='memory'&&x.objectId===id));s.conversations.forEach(c=>c.draftSources=c.draftSources.filter(x=>!(x.kind==='memory'&&x.objectId===id)));},'已停用，不再出现在新的可选引用中。'))repaint();break;
   case 'edit-memory':{const m=state.memories.find(x=>x.id===id);if(m)form('修改这条认识','内容',m.text,txt=>commit(s=>{const x=s.memories.find(x=>x.id===id);x.text=txt;x.revision=(x.revision||1)+1;x.status='candidate';}),'修改后重新作为候选，不默默替换已生效版本。');break;}
   case 'delete-memory':confirm('删除这条记忆？','<p>从本机记忆列表删除，并移出尚未发送的引用；过去对话快照仍保留。不等于外部服务副本已删除。</p>',()=>{commit(s=>{s.memories=s.memories.filter(x=>x.id!==id);s.assistantSources=s.assistantSources.filter(x=>x.objectId!==id);s.conversations.forEach(c=>c.draftSources=c.draftSources.filter(x=>x.objectId!==id));});repaint();},'删除本机记忆');break;
   case 'add-action':case 'new-action':{const text=action==='new-action'?'':ds.context==='relationship'?'下次想加入对话时，先回应一个具体细节。':'下次表达前，先写两个要点，观察是否更容易说清楚。';form('留下一个小尝试','这次想试什么？',text,txt=>commit(s=>s.actions.push({id:uid('action'),text:txt,status:'active',sourceId:route==='report'?D.report.id:currentConversation()?.id||null,createdAt:new Date().toISOString()}),'小尝试已保存在本机。'),'不设置打卡压力。你可以修改、放下，也可以单独留下观察。');break;}
   case 'review-action':{const a=state.actions.find(x=>x.id===id);if(a)form('尝试之后，发生了什么？','我的观察',a.observation||'',txt=>commit(s=>{const t=s.actions.find(x=>x.id===id);t.observation=txt;t.status='done';}),'没做到、没变化、改变想法，都可以照实记录。');break;}
   case 'cancel-action':if(commit(s=>s.actions.find(x=>x.id===id).status='cancelled'))repaint();break;
   case 'save-journal':{const text=(api.formDrafts.journal??document.querySelector('#journal-text')?.value??'').trim();if(!text){toast('先留下一句话。');return;}if(commit(s=>{const old=s.observations.find(x=>x.id===id)||s.reportNotes.find(x=>x.id===id);if(old){old.text=text;old.revision=(old.revision||1)+1;}else s.observations.push({id:uid('observation'),title:ds.title||'一个自己的时刻',text,revision:1,createdAt:new Date().toISOString()});},'记录已保存在本机，未发送给 AI。')){delete api.formDrafts.journal;nav('records');}break;}
   case 'delete-journal':confirm('删除这条本人记录？','<p>仅删除本机这一条；不会删除其他答卷，也不改写以前的对话。已导出文件无法远程撤回。</p>',()=>{if(commit(s=>{s.observations=s.observations.filter(x=>x.id!==id);s.reportNotes=s.reportNotes.filter(x=>x.id!==id);s.assistantSources=s.assistantSources.filter(x=>x.objectId!==id);s.conversations.forEach(c=>c.draftSources=c.draftSources.filter(x=>x.objectId!==id));delete s.editorDrafts['journal:'+id];})){delete api.formDrafts.journal;nav('records');}},'删除这条记录');break;
   case 'toggle-chat-retention':if(commit(s=>s.chatRetention=!s.chatRetention))repaint();break;
   case 'toggle-memory':if(commit(s=>s.memoryEnabled=!s.memoryEnabled))repaint();break;
   case 'export-preview':exportPreview();break;
   case 'export-data':{const chosen=[...document.querySelectorAll('[name="export-group"]:checked')].map(x=>x.value);if(!chosen.length){toast('至少选择一类资料，或取消导出。');return;}const result={schema:'jianji-local-design-export-v1',exportedAt:new Date().toISOString(),scope:'local-design-only',groups:chosen,warning:'明文；不是正式报告或交易凭证'};if(chosen.includes('sessions'))result.sessions=state.sessions;if(chosen.includes('notes')){result.observations=state.observations;result.reportNotes=state.reportNotes;result.editorDrafts=state.editorDrafts;}if(chosen.includes('conversations'))result.conversations=serial(state).conversations;if(chosen.includes('memories')){result.memories=state.memories;result.actions=state.actions;}if(chosen.includes('orders'))result.orders=state.orders;download('jianji-local-export.json',JSON.stringify(result,null,2));close();break;}
   case 'clear-confirm':confirm('清理当前演示空间？','<p>只删除当前场景在这个浏览器保存的答卷、记录、聊天、演示订单和设置。不会触及其他站点、其他演示场景或外部账号。请先导出需要保留的内容。</p>',()=>{cancelAll();try{localStorage.removeItem(KEY);state=D.defaultState();V2.reset();V3.reset();api.pendingAnswer=null;api.formDrafts={};api.unsavedDraft=false;nav('home',{},true);toast('已清理当前本机演示空间。');}catch(e){toast('清理失败，没有宣称已删除。');}},'清理当前演示空间');break;
   case 'plan':state.plan=id;persist();repaint();break;
   case 'checkout-start':state.checkoutReturn='membership';persist();nav('checkout');break;
   case 'create-order':{const o={id:'DEMO-'+uid('order').toUpperCase(),plan:state.plan,planVersion:'proposal-v1',payment:'pending',entitlement:'pending',returnTo:state.checkoutReturn||'assistant',createdAt:new Date().toISOString()};if(commit(s=>s.orders.push(o)))nav('order',{id:o.id});break;}
   case 'cancel-checkout':nav(state.checkoutReturn||'membership');break;
   case 'order-paid':if(commit(s=>{const o=s.orders.find(x=>x.id===id);if(o&&o.payment==='pending')o.payment='paid';}))repaint();break;
   case 'order-active':if(commit(s=>{const o=s.orders.find(x=>x.id===id);if(o?.payment==='paid')o.entitlement='active';}))repaint();break;
   case 'refund':confirm('查看退款申请演示？','<p>将原演示订单标记为“退款处理中”，不是“已到账”。不会生成另一笔订单，不发生真实退款。</p>',()=>{commit(s=>{const o=s.orders.find(x=>x.id===id);if(o?.payment==='paid')o.payment='refunding';});repaint();},'演示提交申请');break;
   case 'order-return':{const o=state.orders.find(x=>x.id===id);if(o)nav(o.returnTo||'assistant');break;}
   case 'export-share':{const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="900" height="960" viewBox="0 0 900 960"><rect width="900" height="960" rx="40" fill="#f7f9f2"/><circle cx="770" cy="160" r="175" fill="#e4ead8"/><g fill="#263d34" font-family="system-ui,sans-serif"><text x="72" y="115" font-size="26">知遇 · 独立报告样例</text><text x="72" y="280" font-size="57">先想清楚，</text><text x="72" y="365" font-size="57">再慢慢说出来。</text><text x="72" y="500" font-size="28">一段准备时间，可能让表达更从容。</text><text x="72" y="552" font-size="28">这只是虚构情境，不是对你的个人结论。</text><path d="M72 704H828" stroke="#bbc6b4"/><text x="72" y="776" font-size="24">虚构样例 · 非个人测量</text><text x="72" y="822" font-size="24">不含姓名与本人补充</text></g></svg>`;download('jianji-sample-share.svg',svg,'image/svg+xml');break;}
   case 'design-feedback':form('记下设计反馈','页面 / 问题 / 希望发生什么','',txt=>{download('jianji-design-feedback.txt',txt,'text/plain');return true;},'生成本机文本文件，不会假称已经提交客服。');break;
   default:toast('这个动作暂未接入交互，请查看完整结构与事件契约。');console.warn('UNMAPPED_ACTION',action);
  }
 }
 document.addEventListener('click',e=>{const b=e.target.closest('[data-action]');if(b&&!b.disabled){e.preventDefault();dispatch(b.dataset.action,b);}});
 let inputTimer;
 let composing=false;document.addEventListener('compositionstart',()=>composing=true);document.addEventListener('compositionend',e=>{composing=false;e.target.dispatchEvent(new Event('input',{bubbles:true}));});
 document.addEventListener('input',e=>{if(composing||e.isComposing)return;if(V2.input(e))return;const k=e.target.dataset.input;if(!k)return;const val=e.target.value;switch(k){case 'chat-draft':saveDraft(val);break;case 'report-note':api.formDrafts.reportNote=val;break;case 'journal':api.formDrafts.journal=val;break;case 'explore-search':state.exploreSearch=val;persist();clearTimeout(inputTimer);inputTimer=setTimeout(()=>{const pos=e.target.selectionStart;repaint();const t=document.getElementById('explore-search');t?.focus();t?.setSelectionRange(pos,pos);},180);break;case 'sim-range':api.simValue=Number(val);const y=scrollY;render();document.getElementById('sim-range')?.focus({preventScroll:true});window.scrollTo(0,y);break;}});
 document.addEventListener('keydown',e=>{const dialog=document.querySelector('.dialog');if(dialog){if(e.key==='Escape'){e.preventDefault();close();}if(e.key==='Tab'){const els=[...dialog.querySelectorAll('button:not([disabled]),input,textarea,a[href]')];const f=els[0],l=els.at(-1);if(e.shiftKey&&document.activeElement===f){e.preventDefault();l?.focus();}else if(!e.shiftKey&&document.activeElement===l){e.preventDefault();f?.focus();}}return;}if(e.target.matches('[role="radio"]')&&['ArrowDown','ArrowUp','ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const options=['a','b','c'],i=options.indexOf(e.target.dataset.id),inc=['ArrowDown','ArrowRight'].includes(e.key)?1:-1;answer(options[(i+inc+3)%3]);}});
 // Read-only debugging interface enables deterministic, shipped regression tests.
 
 V4.bind({get state(){return state;},current,commit,nav,show,confirm,close,repaint,toast,download,dispatch,get blocked(){return !!(api.externalChange||api.pendingAnswer||api.unsavedDraft||V2.hasUnsaved);},get storageKey(){return KEY;},replaceState(next){if(persist(next)){state=next;V2.reset();V3.reset();render();return true;}return false;}});
 V3.bind({get state(){return state;},current,commit,nav,show,repaint,toast});
 V2.bind({get state(){return state;},current,commit,nav,show,confirm,form,repaint,toast,close,download,addSource,status:renderStorageStatus,reset(){cancelAll();state=D.defaultState();api.pendingAnswer=null;api.formDrafts={};api.unsavedDraft=false;V2.reset();V3.reset();}});
 Object.defineProperties(api,{snapshot:{get:()=>clone(serial(state))},storageKey:{get:()=>KEY},currentRoute:{get:()=>current()}});
 api.init=init;api.render=render;return api;
})();
App.init();
