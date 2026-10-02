/* V4 preservation layer. Preview communication carries route/settings metadata only. */
window.V4=(()=>{
 'use strict';
 const {esc,button:B,link:L,icon}=UI;
 let C,importCandidate=null,lastMeta='',previewAction=null;
 const previewActions=['daily','all-factors','v3-preferences','context','quota','source-report'];
 document.addEventListener('click',e=>{const action=e.target.closest('[data-action]')?.dataset.action;if(action){previewAction=previewActions.includes(action)?action:null;setTimeout(notify,0);}});
 const priorData=Views.map.data;
 Views.map.data=(s,p)=>priorData(s,p)+`<section class="v4-transfer"><h2>延续以前的记录</h2><p>V4 使用独立空间。旧版本仍保留原样；确认后可以复制有效的本机记录。</p>${B('检查旧版或导入文件','v4-import',{cls:'btn secondary full space-12',icon:'folder'})}<p class="small muted space-12">本地文件与线上站点属于不同来源，网页无法自动读取彼此的数据。可先在旧版导出，再到这里选择文件。认证和购买权益不会从文件恢复。</p></section>`;
 function meta(){return {type:'jianji-preview-state',version:4,reviewSession:new URLSearchParams(location.search).get('reviewSession'),route:C.current(),stage:AssessmentPreview.getStage(),action:document.querySelector('[role=dialog]')?previewAction:null,theme:C.state.theme,density:C.state.density,reduced:C.state.reduced,blocked:C.blocked};}
 function notify(){if(parent===window||!C)return;const m=meta(),key=JSON.stringify(m);if(key===lastMeta)return;lastMeta=key;parent.postMessage(m,location.origin==='null'?'*':location.origin);}
 function safeState(raw){
  if(!raw||typeof raw!=='object'||Array.isArray(raw))throw Error('文件内容必须是一个记录对象。');
  let x;
  if(raw.schema==='jianji-local-design-export-v1'){
   x=D.defaultState();for(const k of ['sessions','observations','reportNotes','actions','memories','conversations'])if(raw[k])x[k]=raw[k];
   if(raw.editorDrafts)x.editorDrafts=raw.editorDrafts;
  }else if([1,2].includes(raw.schema)){x=raw;}else throw Error('暂不支持这个文件格式。请使用旧版“我的数据”的导出文件。');
  if([1,2].includes(raw.schema)&&!raw.avatarFamily)x.avatarFamily='scene';
  x=V2.normalize(JSON.parse(JSON.stringify(x)));
  const walk=(v,key='',depth=0)=>{if(depth>20)throw Error('嵌套层级超出支持范围。');if(['text','title','createdAt','updatedAt'].includes(key)&&typeof v!=='string')throw Error('记录文字或日期字段格式无效。');if(typeof v==='string'){if(v.length>200000)throw Error('单个字段过长。');if((key==='id'||key.endsWith('Id'))&&v&&!/^[\w.:-]{1,180}$/.test(v))throw Error('记录标识格式无效。');return;}if(Array.isArray(v)){if(v.length>10000)throw Error('记录数量超出本原型的支持范围。');v.forEach(z=>walk(z,'',depth+1));}else if(v&&typeof v==='object'){for(const [k,z] of Object.entries(v)){if(['__proto__','constructor','prototype'].includes(k))throw Error('包含不支持的字段。');walk(z,k,depth+1);}}};walk(x);
  x.logged=false;x.used=0;x.usage=[];x.orders=[];x.assistantSources=[];x.assistantDraft='';x.plan='monthly';
  for(const c of x.conversations){c.generating=false;c.pendingRequest=null;c.interrupted=true;}
  return x;
 }
 function counts(s){return `${s.sessions.length} 份体验答卷 · ${s.observations.length+s.reportNotes.length} 条本人记录 · ${s.actions.length} 个小尝试 · ${s.conversations.length} 个历史对话`;}
 function hasRecords(s){return ['sessions','observations','reportNotes','actions','memories','conversations','orders'].some(k=>s[k]?.length)||Object.values(s.editorDrafts||{}).some(x=>JSON.stringify(x)!=='""'&&JSON.stringify(x)!=='{}');}
 function preflight(raw,label){
  try{const next=safeState(raw);importCandidate=next;C.show('确认复制有效记录',`<p>${esc(label)}</p><p class="v4-import-count">${counts(next)}</p><p class="small muted">旧空间与原文件保持不变。只复制到当前空的 V4 空间；不恢复登录、购买权益或自动发送请求。将保留记录标识、来源和可识别的主题偏好。</p>`,B('取消','close-dialog',{cls:'btn secondary'})+B('复制到当前空间','v4-import-confirm',{cls:'btn'}));}
  catch(e){importCandidate=null;C.toast('未导入：'+e.message);const n=document.getElementById('v4-import-status');if(n)n.textContent='未导入：'+e.message;}
 }
 function openImport(){
  if(hasRecords(C.state)){C.show('当前空间已有内容','<p>为避免覆盖，当前原型只支持导入到空空间。请先导出当前资料，再按明确范围清理，或在另一个独立场景中检查旧文件。合并冲突流程尚未实现。</p>');return;}
  const legacy=[];for(const v of [3,2]){const key='jianji-design-v'+v+':'+(new URLSearchParams(location.search).get('scenario')||'default');try{if(localStorage.getItem(key))legacy.push([key,'同来源 V'+v+' 空间']);}catch{}}
  C.show('检查可延续的数据',`<p>先检查格式和数量，再由你确认复制。</p>${legacy.map(([k,l])=>B(l,'v4-legacy',{cls:'btn secondary full space-12','data-id':k})).join('')}<label class="field-label space-16" for="v4-import-file">选择旧版导出的 JSON 文件</label><input id="v4-import-file" type="file" accept="application/json,.json"><p id="v4-import-status" role="status" class="small muted space-12">不上传文件；只在当前浏览器读取。上限 5 MB。</p>`,B('返回','close-dialog',{cls:'btn secondary full'}));
  document.getElementById('v4-import-file').addEventListener('change',async e=>{const f=e.target.files?.[0];if(!f)return;if(f.size>5*1024*1024){document.getElementById('v4-import-status').textContent='文件超过 5 MB，本轮未读取。';return;}try{preflight(JSON.parse(await f.text()),f.name);}catch{C.toast('JSON 无法读取。原文件与当前空间没有改动。');}});
 }
 function dispatch(action,el){
  if(action==='v4-reload-latest'){C.show('重新载入最新资料','<p>当前窗口尚未保存的更改不会自动合并。请先导出当前窗口内容。确认后将载入另一个页面已保存的最新资料。</p>',B('先返回导出','close-dialog',{cls:'btn secondary full'})+B('确认重新载入','v4-confirm-reload',{cls:'btn full space-12'}));return true;}
  if(action==='v4-confirm-reload'){location.reload();return true;}
  if(action==='v4-import'){openImport();return true;}
  if(action==='v4-legacy'){try{const key=el.dataset.id;if(!/^jianji-design-v[23]:[\w-]+$/.test(key))return true;preflight(JSON.parse(localStorage.getItem(key)),'本机旧版空间');}catch{C.toast('旧空间无法读取，未做任何覆盖。');}return true;}
  if(action==='v4-import-confirm'){
   if(!importCandidate||hasRecords(C.state)||C.blocked){C.toast('当前内容已变化，请重新检查。未覆盖现有数据。');return true;}
   if(C.replaceState(importCandidate)){importCandidate=null;C.close();C.toast('已复制有效记录。旧文件与旧空间保留，认证和购买权益未导入。');}else C.toast('保存失败，未替换当前空间；原始数据仍保留。');return true;
  }
  return false;
 }
 window.addEventListener('message',e=>{
  if(!C||e.source!==parent||parent===window||e.origin!==location.origin)return;
  const m=e.data;if(!m||m.type!=='jianji-preview-command')return;
  if(m.command==='navigate'){
   const r=String(m.route||''),[base,q]=r.split('?');if(!Object.hasOwn(Views.map,base))return;
   const p=Object.fromEntries(new URLSearchParams(q||''));if(Object.keys(p).some(k=>!['id','topic','kind','tab'].includes(k)))return;C.nav(base,p);
   previewAction=null;
   if(m.action&&previewActions.includes(m.action)&&!C.blocked){previewAction=m.action;C.dispatch(m.action,{dataset:{}});}
   if(m.stage&&['single-factor','daily-checkin','short-16pf','personality-sandbox'].includes(base)&&['config','process','result'].includes(m.stage)&&!C.blocked)C.dispatch('preview-stage',{dataset:{id:base,stage:m.stage}});
  }else if(m.command==='theme'&&D.themes.some(t=>t.id===m.value)){if(C.commit(s=>s.theme=m.value))C.repaint();}
  else if(m.command==='density'&&['balanced','compact'].includes(m.value)){if(C.commit(s=>s.density=m.value))C.repaint();}
  else if(m.command==='motion'&&typeof m.value==='boolean'){if(C.commit(s=>s.reduced=m.value))C.repaint();}
  else if(m.command==='status'){lastMeta='';notify();}
  lastMeta='';notify();
 });
 function afterRender(){
  document.body.dataset.route=C.current().split('?')[0];const t=D.themes.find(t=>t.id===C.state.theme);document.body.dataset.themeMode=t?.mode||'light';
  document.documentElement.style.colorScheme=t?.mode||'light';
  Ambient.setContext({quiet:C.current().split('?')[0]==='question'||AssessmentPreview.isQuiet(),reduced:C.state.reduced});
  document.querySelectorAll('textarea').forEach(el=>{el.style.resize='none';const grow=()=>{el.style.height='auto';el.style.height=Math.min(480,Math.max(136,el.scrollHeight+2))+'px';};el.addEventListener('input',grow);grow();});
  notify();
 }
 return {bind(c){C=c;if(parent!==window)new MutationObserver(notify).observe(document.getElementById('overlays'),{childList:true});},dispatch,afterRender,notify};
})();
