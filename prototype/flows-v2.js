/* V2 flow controller. All effects remain local. No model, identity or payment API is called. */
window.V2 = (() => {
  'use strict';
  const {esc,button:B,link:L,icon} = UI;
  let C;
  const cachedDrafts = new Map(), failedDrafts = new Set();
  const uid = prefix => `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,7)}`;
  const schemas = {
    'work-choice': [
      ['options','正在比较什么','例如：继续当前岗位，或换到另一家公司。'],
      ['priorities','最在意的两件事','写出自己的优先级，例如稳定收入、能学到东西。'],
      ['limits','暂时不能忽略的条件','家庭、时间、预算，哪些是硬约束？'],
      ['unknown','决定前，还要弄清什么','写一条可以查证的信息，不急着作结论。']
    ],
    'relationships': [
      ['event','发生了哪件具体的事','尽量写可观察的事实，少用“总是”“从不”。'],
      ['need','当时，我需要什么','说说自己的感受、需要或界限。'],
      ['request','准备怎样表达一个请求','例如：下次改时间前，能否先和我确认？']
    ],
    'city-choice': [
      ['expectation','期待生活发生什么变化','先写期待，再写正在考虑的城市。'],
      ['conditions','家庭、工作与预算条件','哪些条件必须满足，哪些可以商量？'],
      ['unknown','还不了解什么','通勤、学位、实际支出、支持网络……'],
      ['experiment','怎样先验证一小步','例如：短住、实地通勤或询问真实居住者。']
    ],
    'learning': [
      ['objective','希望学习解决什么问题','把“想变好”变成具体、可讨论的目标。'],
      ['cost','能投入多少时间和精力','写真实可持续的投入，无需填理想数字。'],
      ['experiment','先用什么小实验验证','例如：试学一周，记录是否仍然感兴趣。']
    ],
    'self-space': [
      ['context','什么情况下想独处','当时发生了什么，和谁在一起？'],
      ['change','独处前后有什么不同','如实记录，也可以写“没变化”。'],
      ['support','接下来需要什么','多一点休息、一次交流，或其他支持。']
    ]
  };
  // Additional reflection prompts extend every original topic without replacing it.
  const reflectionFields = [
    ['issue','这次，想理清哪件具体的事','可从近期可逆的小选择开始；例如先独立整理再讨论，还是先讨论再动手。示例不用照写。'],
    ['evidence','有哪些亲历的事实或依据','写发生了什么、何时发生；转述或猜测请注明。这里仍是本人提供，未经外部核验。'],
    ['understanding','我目前的认识或倾向','可以写还不能决定、条件有冲突，或先补哪条信息。不必选出一个答案。']
  ];
  const topicFields = id => D.topics.find(t=>t.id===id)?.decisionScene ? schemas[id] : schemas[id] ? [[...reflectionFields[0].slice(0,2),id==='work-choice'?reflectionFields[0][2]:'从一件亲历的事开始，写下这次希望理解什么。不必把它变成选择题。'], ...schemas[id], ...reflectionFields.slice(1)] : [];
  const fieldsText = (id,fields) => topicFields(id).map(([key,label])=>`${label}\n${String(fields[key]||'').trim()||'暂未填写'}`).join('\n\n');
  const topicChanged = note => {const draft=getDraft(topicKey(note.topicId,note.id),note.fields||{});return JSON.stringify(draft)!==JSON.stringify(note.fields||{});};
  function savedVersionGuard(note,next) {
    if(!topicChanged(note))return false;
    C.show('先选择采用哪个版本',`<p>你还有未正式保存的修改。当前整理卡和后续引用仍采用第 ${note.revision||1} 版。</p><p class="small muted space-12">草稿留在本机；不会静默保存、发送或覆盖原先的小尝试。</p>`,B('回到草稿，先保存修改','topic-edit',{cls:'btn full'})+B('使用已保存版本继续',next,{cls:'btn secondary full space-12','data-id':note.id}));
    return true;
  }
  const outcomes = [
    ['not-yet','还没尝试'], ['helpful','有一点帮助'], ['no-change','没看到变化'], ['not-fit','不太适合'], ['partial','只试了一部分']
  ];
  const originalDefaults = D.defaultState.bind(D);
  D.defaultState = () => ({...originalDefaults(),schema:2,editorDrafts:{},showSampleSources:false});
  D.version='2.0.0-design';
  function normalize(raw) {
    const base = D.defaultState();
    if (!raw || typeof raw!=='object' || Array.isArray(raw) || ![1,2].includes(raw.schema)) throw Error('unsupported-storage-schema');
    const s={...base,...raw,schema:2};
    if(s.recordFilter==='体验答卷')s.recordFilter='历史练习';
    for (const key of ['sessions','reportNotes','observations','actions','memories','conversations','usage','favorites','orders']) {
      if (!Array.isArray(s[key])) throw Error(`invalid-storage-${key}`);
    }
    for (const key of ['sessions','reportNotes','observations','actions','memories','conversations','orders']) {
      if(s[key].some(x=>!x || typeof x!=='object' || typeof x.id!=='string')) throw Error(`invalid-object-${key}`);
    }
    const recordObject = v => v && typeof v==='object' && !Array.isArray(v);
    const validFields = v => recordObject(v) && Object.values(v).every(x=>typeof x==='string');
    for(const n of s.observations.filter(x=>x.kind==='topic-record')) {
      if(n.fields!==undefined&&!validFields(n.fields))throw Error('invalid-topic-fields');
      if(n.revisions!==undefined&&(!Array.isArray(n.revisions)||n.revisions.some(v=>!recordObject(v)||!Number.isInteger(v.revision)||v.revision<1||!validFields(v.fields)||typeof v.text!=='string')))throw Error('invalid-topic-revisions');
    }
    for(const a of s.actions) {
      if(a.sourceVersion!==undefined&&typeof a.sourceVersion!=='string')throw Error('invalid-action-source-version');
      if(a.sourceSnapshot!==undefined&&(!recordObject(a.sourceSnapshot)||['objectId','version','title','excerpt'].some(k=>typeof a.sourceSnapshot[k]!=='string')))throw Error('invalid-action-source-snapshot');
      if(a.reviews!==undefined&&(!Array.isArray(a.reviews)||a.reviews.some(r=>!recordObject(r)||typeof r.id!=='string'||(r.actionText!==undefined&&typeof r.actionText!=='string')||(r.actionRevision!==undefined&&(!Number.isInteger(r.actionRevision)||r.actionRevision<1)))))throw Error('invalid-action-reviews');
    }
    if(!D.themes.some(t=>t.id===s.theme)) s.theme='green';
    if(![1,2,3].includes(s.avatar)) s.avatar=1;
    if(!['original','ai'].includes(s.mode)) s.mode='original';
    if(!s.editorDrafts || typeof s.editorDrafts!=='object' || Array.isArray(s.editorDrafts)) throw Error('invalid-editor-drafts');
    s.used=Number.isFinite(s.used)?Math.max(0,Math.floor(s.used)):0;
    s.name=String(s.name||'此刻的你').slice(0,20);
    for(const x of s.sessions) {
      if(x.version!=='demo-3-v1' || !x.answers || typeof x.answers!=='object' || Array.isArray(x.answers)) throw Error('unsupported-session');
      x.index=Number.isInteger(x.index)?Math.max(0,Math.min(2,x.index)):0;
    }
    for(const c of s.conversations) {
      if(!Array.isArray(c.messages)||!Array.isArray(c.draftSources)) throw Error('invalid-conversation');
      if(c.generating || c.pendingRequest) { c.generating=false; c.interrupted=true; c.pendingRequest=null; }
    }
    for(const x of s.usage) if(x.status==='预写演示请求') x.status='窗口中断，未自动重发';
    return s;
  }
  function bind(ctx){ C=ctx; }
  function route(){return C.current().split('?')[0];}
  function params(){return Object.fromEntries(new URLSearchParams(C.current().split('?')[1]||''));}
  function getDraft(key,fallback='') { return cachedDrafts.has(key)?cachedDrafts.get(key):(C.state.editorDrafts[key]??fallback); }
  function setDraft(key,value) {
    cachedDrafts.set(key,value);
    const ok=C.commit(s=>s.editorDrafts[key]=value,'',true);
    if(ok) failedDrafts.delete(key); else failedDrafts.add(key);
    paintSaveStatus(); return ok;
  }
  function deleteDraft(s,key){delete s.editorDrafts[key];}
  function savedDraft(key){cachedDrafts.delete(key);failedDrafts.delete(key);}
  function paintSaveStatus(){
    const node=document.getElementById('editor-save-state');
    if(node){node.textContent=failedDrafts.size?'草稿尚未保存；请勿关闭页面。':'草稿已存本机 · 正式保存后进入记录';node.classList.toggle('failed',!!failedDrafts.size);}
    C.status();
  }
  function retryDrafts(){
    if(!failedDrafts.size && !App.unsavedDraft){C.toast('没有待重试的草稿。');return;}
    const all=[...failedDrafts];
    const ok=C.commit(s=>{all.forEach(k=>s.editorDrafts[k]=cachedDrafts.get(k));});
    if(ok){failedDrafts.clear();App.unsavedDraft=false;C.toast('已保存当前草稿。');paintSaveStatus();}
  }
  function journalKey(p=params()){return `journal:${p.id||p.topic||p.kind||'new'}`;}
  function topicKey(topicId,recordId=''){return `topic:${topicId}:${recordId||'new'}`;}
  function actionKey(id){return `action-review:${id}`;}
  function ownSource(note){return {id:'observation-'+note.id,kind:'self-note',objectId:note.id,version:String(note.revision||1),title:'本人记录 · '+(note.fields?.issue||note.title),excerpt:note.text,status:'valid',scope:'仅本次引用'};}
  function attachSource(src,prompt) {
    if(C.commit(s=>{const i=s.assistantSources.findIndex(x=>x.id===src.id);if(i<0)s.assistantSources.push(src);else s.assistantSources[i]=src;if(!s.assistantDraft)s.assistantDraft=prompt;})) C.nav('assistant-chat');
  }
  function context() {
    const s=C.state, rows=[];
    [...s.observations,...s.reportNotes].slice().reverse().slice(0,8).forEach(o=>rows.push(ownSource(o)));
    s.memories.filter(m=>m.status==='active').forEach(m=>rows.push({id:'memory-'+m.id,kind:'memory',objectId:m.id,version:String(m.revision||1),title:'已确认记忆',excerpt:m.text,status:'valid',scope:'本次显式选择'}));
    const item=x=>`<button class="context-item" data-action="v2-pick-context" data-id="${esc(x.id)}"><span class="grow"><strong>${esc(x.title)}</strong><small>${esc(x.excerpt.slice(0,80))}</small></span>${icon('plus')}</button>`;
    const samples=ProductContext.fixture?[D.reportSource('work'),D.reportSource('relationship')]:[];V2.contextChoices=[...rows,...samples];
    C.show('选择本次资料',`<p class="small muted">只采用你这次选中的内容。不会读取全部历史。</p><h3 class="space-24">我的记录与已确认记忆</h3>${rows.length?rows.map(item).join(''):'<p class="empty-inline">还没有个人资料。可以先写下一件具体的事。</p>'}${samples.length?'<details class="sample-context"><summary>其他资料</summary>'+samples.map(item).join('')+'</details>':''}`,B('取消选择','close-dialog',{cls:'btn secondary full'}));
  }
  function createAction(ds,isNew=false) {
    const r=route(),p=params();
    let text=isNew?'':ds.context==='relationship'?'下次想加入对话时，先回应一个具体细节。':'下次表达前，先写两个要点，观察是否更容易说清楚。';
    const note=r==='topic-workspace'?C.state.observations.find(x=>x.id===p.id&&x.topicId===p.topic):null;
    if(r==='topic-workspace'){if(!note){C.toast('先保存这份整理，再留下小尝试。');return;}if(!ds.savedConfirmed&&savedVersionGuard(note,'topic-action-saved'))return;text='';}
    const sourceId=r==='report'?D.report.id:r==='topic-workspace'?p.id||null:r==='conversation'?p.id:null;
    const sourceKind=r==='report'?'sample-report':r==='topic-workspace'?'self-note':r==='conversation'?'conversation':'self-entered';
    C.form('留下一个小尝试','什么情况下，试着做什么？',text,txt=>{
      const existing=C.state.actions.find(x=>x.status==='active'&&x.text===txt&&x.sourceId===sourceId&&(!note||x.sourceVersion===String(note.revision||1)));
      if(existing){C.nav('action-detail',{id:existing.id});C.toast('这个小尝试已经留下，直接打开原记录。');return true;}
      const a={id:uid('action'),text:txt,revision:1,status:'active',sourceId,sourceKind,...(note?{sourceVersion:String(note.revision||1),sourceSnapshot:ownSource(note)}:{}),sectionId:r==='report'?C.state.reportContext:null,reviews:[],createdAt:new Date().toISOString()};
      if(C.commit(s=>s.actions.push(a))){C.nav('action-detail',{id:a.id});C.toast('已留下。之后可以记录有帮助、没变化或还没尝试。');return true;}
      return false;
    },sourceKind==='sample-report'?'灵感来自虚构样例。你保存的是自己选择的尝试，不是个人性格结论。':'由你亲自决定。选一件成本低、可以调整的小事，并写下准备观察什么；也可以取消，不安排尝试。');
  }
  function dispatch(action,el){
    if(!C)return false;
    const ds=el?.dataset||{},id=ds.id,s=C.state,p=params();
    switch(action){
      case 'context': context();return true;
      case 'prompt': if(id==='report'){context();return true;}return false;
      case 'v2-pick-context': {const src=V2.contextChoices.find(x=>x.id===id);if(src){C.addSource(src);C.close();C.repaint();}return true;}
      case 'topic-journal': C.nav('topic-workspace',{topic:id});return true;
      case 'topic-save': {
        const topic=D.topics.find(t=>t.id===ds.topic); if(!topic)return true;
        const old=s.observations.find(x=>x.id===id&&x.topicId===topic.id),key=topicKey(topic.id,id),fields=getDraft(key,old?.fields||{});
        if(id&&!old){C.toast('原记录已不可用，请回到记录查看。');return true;}
        if(!Object.values(fields).some(v=>String(v).trim())){const error=document.getElementById('topic-error');if(error){error.hidden=false;error.textContent='至少写下一件具体的事，或一个还不知道的问题。';}const first=document.querySelector('[data-input="topic-field"]');first?.setAttribute('aria-invalid','true');first?.setAttribute('aria-describedby','topic-error');first?.focus();return true;}
        const text=fieldsText(topic.id,fields),noteId=id||uid('observation');
        if(old&&!topicChanged(old)){C.nav('topic-workspace',{topic:topic.id,id:noteId},true);C.toast('已保存版本没有变化；整理卡仍在。');return true;}
        if(C.commit(n=>{const prior=n.observations.find(x=>x.id===id);if(prior){prior.revisions=prior.revisions||[];prior.revisions.push({revision:prior.revision||1,fields:{...prior.fields},text:prior.text,createdAt:prior.updatedAt||prior.createdAt});prior.fields={...fields};prior.text=text;prior.revision=(prior.revision||1)+1;prior.updatedAt=new Date().toISOString();}else n.observations.push({id:noteId,kind:'topic-record',topicId:topic.id,title:topic.short+' · 我的整理',fields:{...fields},text,revision:1,revisions:[],createdAt:new Date().toISOString()});deleteDraft(n,key);},'整理卡已保存在本机。只整理到这里，也可以。')){savedDraft(key);C.nav('topic-workspace',{topic:topic.id,id:noteId},true);}return true;
      }
      case 'topic-edit': {C.close();const editor=document.querySelector('.record-editor');if(editor){editor.open=true;const target=editor.querySelector('textarea');target?.focus();target?.scrollIntoView({block:'center',behavior:'instant'});}return true;}
      case 'topic-to-assistant': {const note=s.observations.find(x=>x.id===id);if(note&&!savedVersionGuard(note,'topic-attach-saved'))attachSource(ownSource(note),'我整理了自己的情况，想看看还缺哪些信息。');return true;}
      case 'topic-attach-saved': {const note=s.observations.find(x=>x.id===id);if(note)attachSource(ownSource(note),'我整理了自己的情况，想看看还缺哪些信息。');return true;}
      case 'topic-action-saved':createAction({savedConfirmed:true});return true;
      case 'add-action': case 'new-action': createAction(ds,action==='new-action');return true;
      case 'review-action': C.nav('action-detail',{id});return true;
      case 'action-outcome': {const key=actionKey(id),old=getDraft(key,{});setDraft(key,{...old,outcome:ds.outcome});C.repaint();return true;}
      case 'save-action-review': {
        const key=actionKey(id),d=getDraft(key,{});if(!outcomes.some(x=>x[0]===d.outcome)){C.toast('先选择这次实际发生了什么。');document.querySelector('[data-action="action-outcome"]')?.focus();return true;}
        if(C.commit(n=>{const a=n.actions.find(x=>x.id===id);if(!a)return;a.reviews=a.reviews||[];a.reviews.push({id:uid('review'),outcome:d.outcome,text:String(d.text||'').trim(),actionText:a.text,actionRevision:a.revision||1,createdAt:new Date().toISOString()});a.status=d.outcome==='not-yet'?'active':'reviewed';deleteDraft(n,key);},d.outcome==='not-yet'?'如实记录为还没尝试，未标记完成。':'这次观察已留下，可以继续尝试或放下。')){savedDraft(key);C.repaint();}return true;
      }
      case 'cancel-action': {
        C.confirm('这次先放下？','<p>原尝试和观察会保留，也能重新开始。</p>',()=>{if(C.commit(n=>{const a=n.actions.find(x=>x.id===id);if(a)a.status='cancelled';}))C.repaint();},'先放下');return true;
      }
      case 'restart-action':if(C.commit(n=>{const a=n.actions.find(x=>x.id===id);if(a)a.status='active';},'重新放回当前尝试，已有观察仍保留。'))C.repaint();return true;
      case 'edit-action': {const a=s.actions.find(x=>x.id===id);if(a)C.form('修改小尝试','打算怎样试？',a.text,txt=>C.commit(n=>{const a=n.actions.find(x=>x.id===id);a.text=txt;a.revision=(a.revision||1)+1;}),'修改计划不删除之前的观察。');return true;}
      case 'save-journal':{
        const key=journalKey(p),old=s.observations.find(x=>x.id===id)||s.reportNotes.find(x=>x.id===id);
        const text=String(getDraft(key,old?.text||'')).trim();if(!text){C.toast('先留下一句话。');return true;}
        if(C.commit(n=>{const item=n.observations.find(x=>x.id===id)||n.reportNotes.find(x=>x.id===id);if(item){item.text=text;item.revision=(item.revision||1)+1;}else n.observations.push({id:uid('observation'),kind:'personal-note',...(p.kind?.startsWith('relationship:')&&ProductSurface.relationshipDimensions.some(d=>d[0]===p.kind.split(':')[1])&&ProductSurface.facets.some(f=>f[0]===p.kind.split(':')[2])?{relationshipDimension:p.kind.split(':')[1],relationshipFacet:p.kind.split(':')[2]}:{}),...(p.kind?.startsWith('observation:')&&ProductSurface.areas.some(a=>a[0]===p.kind.slice(12))?{observationArea:p.kind.slice(12)}:{}),...(p.kind?.startsWith('factor:')&&D.factors.some(f=>f[0]===p.kind.slice(7))?{factorId:p.kind.slice(7)}:{}),title:ds.title||'一个自己的时刻',text,revision:1,createdAt:new Date().toISOString()});deleteDraft(n,key);},'已保存记录；未发送给助理。')){savedDraft(key);C.nav('records');}return true;
      }
      case 'save-report-note':{
        const key='report:'+s.reportContext,text=String(getDraft(key,'')).trim();if(!text){C.toast('先写下自己的真实经历。');return true;}
        if(C.commit(n=>{n.reportNotes.push({id:uid('note'),kind:'self-note',title:'阅读后的本人观察',text,sourceId:D.report.id,sourceKind:'sample-report',sectionId:n.reportContext,revision:1,createdAt:new Date().toISOString()});deleteDraft(n,key);},'本人观察已保存，与虚构样例分开保留。')){savedDraft(key);C.repaint();}return true;
      }
      case 'candidate-memory': {
        const conv=s.conversations.find(c=>c.id===p.id),msg=conv?.messages.find(x=>x.id===id);
        if(msg?.sources?.some(x=>x.kind==='sample-report')){C.show('演示资料不能成为个人记忆','<p>这条回复引用了虚构人物的报告。请先写下自己的真实经历，再由你确认是否记住。</p>',L('写一条本人观察','journal',{cls:'btn full'})+B('保留对话，不建立记忆','close-dialog',{cls:'btn secondary full space-12'}));return true;}
        return false;
      }
      case 'mode': return false;
      case 'retry-drafts':retryDrafts();return true;
      case 'export-recovery':{
        C.download('jianji-recovery.json',JSON.stringify({scope:'local-recovery',warning:'明文文件，请妥善保管',corruptRaw:App.corruptRaw||null,drafts:Object.fromEntries(cachedDrafts),snapshot:App.snapshot},null,2));return true;
      }
      case 'reset-corrupt':C.confirm('清理无法读取的当前演示数据？','<p>建议先导出恢复文件。清理仅影响当前场景，不覆盖其他场景或旧版资料。</p>',()=>{try{localStorage.removeItem(App.storageKey);App.storageBlocked=false;App.corruptRaw=null;C.reset();C.nav('home',{},true);}catch(e){C.toast('清理失败，原资料仍保留。');}},'确认清理');return true;
      case 'report-jump': {const target=document.getElementById(id);if(target){target.focus({preventScroll:true});target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches||s.reduced?'instant':'smooth',block:'start'});}return true;}
      case 'quote-report':attachSource(D.reportSource(s.reportContext),'我想结合这段情境，看看自己可以观察些什么。');return true;
      case 'article-quote':{const text=document.getElementById('article-excerpt')?.textContent||'';attachSource({id:'source-article-read-traits-quote1',kind:'article',objectId:'read-traits',version:'article-demo-v1',sectionId:'quote-1',title:'阅读示例 · 高低不代表更好',excerpt:text,status:'valid',scope:'仅本次引用，不自动发送'},'我想聊聊情境和表达之间的关系。');return true;}
      default:return false;
    }
  }
  function input(e){
    const key=e.target.dataset.input,p=params();
    if(key==='journal'){setDraft(journalKey(p),e.target.value);return true;}
    if(key==='report-note'){setDraft('report:'+C.state.reportContext,e.target.value);return true;}
    if(key==='topic-field'){const k=topicKey(p.topic,p.id),found=C.state.observations.find(x=>x.id===p.id);setDraft(k,{...getDraft(k,found?.fields||{}),[e.target.dataset.field]:e.target.value});return true;}
    if(key==='action-review'){const k=actionKey(p.id);setDraft(k,{...getDraft(k,{}),text:e.target.value});return true;}
    return false;
  }
  function omitSourceText(action,reason){const copy=JSON.parse(JSON.stringify(action));if(copy.sourceSnapshot){delete copy.sourceSnapshot;copy.sourceUnavailable=reason;}return copy;}
  function actionsForExport(actions,includeNotes){return actions.map(a=>includeNotes?JSON.parse(JSON.stringify(a)):omitSourceText(a,'excluded-from-export'));}
  function forgetRecordDrafts(id){for(const key of [...cachedDrafts.keys()])if(key==='journal:'+id||key.startsWith('topic:')&&key.endsWith(':'+id)){cachedDrafts.delete(key);failedDrafts.delete(key);}}
  function reset(){cachedDrafts.clear();failedDrafts.clear();}
  const V2={bind,normalize,omitSourceText,actionsForExport,forgetRecordDrafts,schemas,reflectionFields,topicFields,topicChanged,outcomes,getDraft,journalKey,topicKey,actionKey,dispatch,input,contextChoices:[],reset,paintSaveStatus,get hasUnsaved(){return !!failedDrafts.size;},get draftStatus(){return failedDrafts.size?'草稿尚未保存；请勿关闭页面。':'草稿自动保留在本机'} };
  return V2;
})();
