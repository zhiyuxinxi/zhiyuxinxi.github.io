/* V3 presentation layer. Preserves the V2 record/source/request contracts.
 * No external requests, scoring, inferred personality labels, or usage analytics.
 */
window.V3 = (() => {
  'use strict';
  const {esc,icon,button:B,link:L,top,row,mark,bottleGrid,composer,empty}=UI;
  let C, previousRoute=null, chapterObserver=null, chapterScroll=null, chapterFrame=0;
  const workspaceSteps=new Map();
  const baseDefaults=D.defaultState.bind(D);
  D.defaultState=()=>({...baseDefaults(),theme:'violet',density:'balanced',workspaceMode:'overview'});
  D.version='3.0.0-design';
  D.themes.unshift({id:'violet',name:'灵感紫',desc:'鸢尾紫 · 青柠 · 奶白',colors:['#6151d6','#dcec9a','#fbf9f4']});
  const savedViews={...Views.map};
  const topicMeta={
    'work-choice':{name:'工作怎么选',title:'留下，还是换个方向？',desc:'把期待与现实放在一起。',output:'一份选择清单',color:'lime',ic:'explore'},
    relationships:{name:'需要怎么说',title:'把需要，说清楚',desc:'从一件具体的事开始。',output:'一句具体表达',color:'peach',ic:'chat'},
    'city-choice':{name:'换个城市',title:'<span class="title-phrase">哪里更适合</span><span class="title-phrase">生活？</span>',desc:'先看条件，再看向往。',output:'一份条件清单',color:'blue',ic:'home'},
    learning:{name:'为什么想学',title:'找回学习的理由',desc:'分清期待与外界的声音。',output:'一次学习实验',color:'lavender',ic:'book'},
    'self-space':{name:'留点独处',title:'一个人，刚刚好？',desc:'观察独处前后的变化。',output:'一条情境观察',color:'cream',ic:'sun'}
  };
  for(const x of DecisionScenes.items)topicMeta[x.id]={...x,output:'自己的取舍清单'};
  const section=(title,extra='')=>`<div class="section-head"><h2>${title}</h2>${extra}</div>`;
  const badge=(text,kind='')=>`<span class="v3-badge ${kind}">${text}</span>`;
  const saveState=()=>`<p class="editor-save" id="editor-save-state" role="status">${V2.draftStatus}</p>`;
  const emblem=(kind='orbit')=>`<span class="v3-art ${kind}" aria-hidden="true"><i></i><i></i><i></i><b>${icon(kind==='flower'?'sparkle':'explore')}</b></span>`;
  const title=(over,h,sub,extra='')=>`<header class="v3-title"><div><span class="eyebrow">${over}</span><h1>${h}</h1>${sub?`<p>${sub}</p>`:''}</div>${extra}</header>`;
  const noteCount=s=>s.observations.length+s.reportNotes.length;
  const activeAction=s=>s.actions.find(a=>a.status==='active');
  function home(s){return AssessmentPreview.home(s);}

  function exploreResults(s){
    const filtered=DecisionScenes.search(s.exploreSearch,s.exploreCategory);
    return `<p class="explore-result-count small muted">${s.exploreCategory==='全部'?'全部主题':esc(s.exploreCategory)} · ${filtered.length} 个问题</p><div class="v3-topic-grid decision-grid">${filtered.map(t=>`<button class="v3-topic decision-card ${t.color}" data-action="nav" data-route="topic" data-id="${t.id}"><span class="decision-layout"><span class="decision-heading"><span class="decision-symbol" aria-hidden="true">${icon(t.ic)}</span><span class="decision-category">${t.category}</span></span><span class="decision-copy"><strong class="decision-title">${t.titlePhrases.map(phrase=>`<span class="decision-title-phrase">${esc(phrase)}</span>`).join('')}</strong><span class="decision-description">${esc(t.directoryDesc||t.desc)}</span></span></span></button>`).join('')}</div>${!filtered.length?empty('没有找到这个主题','试试更短的词，如辞职、考研；也可以换个分类。',B('清空筛选','clear-filters',{cls:'btn secondary'})):''}`;
  }
  function explore(s){
    const recent=s.observations.filter(x=>x.kind==='topic-record').sort((a,b)=>(b.updatedAt||b.createdAt||'').localeCompare(a.updatedAt||a.createdAt||''))[0];
    return `${title('','最近，你在想什么？','',B('收藏','favorites',{cls:'textbtn',icon:'bookmark'}))}
    <section class="explore-intro" aria-label="探索能帮你做什么"><p>从生活与工作的纠结出发，理清在意与顾虑，多一点对自己的认识。</p></section>
    <div class="chips v3-categories" aria-label="探索类别">${['全部','工作','学业','关系','生活'].map(c=>B(c,'category',{cls:s.exploreCategory===c?'active':'','data-id':c,'aria-pressed':s.exploreCategory===c})).join('')}</div>
    <div class="explore-directory"><div class="explore-find-row">${B('找主题','toggle-topic-search',{cls:'textbtn',icon:'search','aria-expanded':!!s.exploreSearchOpen,'aria-controls':'topic-search-panel'})}</div>
    <div id="topic-search-panel" ${s.exploreSearchOpen?'':'hidden'}><div class="search-box"><label class="sr-only" for="explore-search">按标题或关键词找主题</label>${icon('search')}<input id="explore-search" data-input="explore-search" value="${esc(s.exploreSearch)}" placeholder="试试辞职、考研、搬家" maxlength="100" autocomplete="off" aria-describedby="topic-search-help">${B('','clear-search',{cls:'search-clear',icon:'close','aria-label':'清空搜索',hidden:!s.exploreSearch})}</div><p id="topic-search-help" class="small muted">在当前分类里查找标题或关键词。不用写完整问题。</p></div>
    <p id="explore-announcement" class="sr-only" role="status" aria-live="polite"></p><div id="explore-results">${exploreResults(s)}</div></div>
    ${recent?`<section class="life-entry"><h2>接着上次整理</h2><p>${esc(recent.fields?.issue||recent.title)}</p>${L('继续整理','topic-workspace',{cls:'textbtn','data-topic':recent.topicId,'data-id':recent.id,after:'arrow'})}</section>`:''}
    <details class="explore-tools"><summary>认识工具与阅读</summary><div class="plain-list">${row('单因子探索','选一个想了解的角度','single-factor','bottle')}${row('模拟性格','调整一组假设位置','personality-sandbox','explore')}${row('我的报告','回看测评结果','report','book')}${row('如何理解因子','从具体情境理解不同倾向','article','book', '',{'data-id':'read-traits'})}${row('以前的整理','找回已保存的议题和记录','records','folder')}</div></details>`;
  }
  function topic(s,p){
    const t=D.topics.find(x=>x.id===p.id);if(!t)return savedViews.topic(s,p);const m=topicMeta[t.id],note=s.observations.filter(x=>x.topicId===t.id).sort((a,b)=>(b.updatedAt||b.createdAt||'').localeCompare(a.updatedAt||a.createdAt||''))[0];
    return `${top('探索',B('','favorite',{cls:'iconbtn',icon:'bookmark','data-id':t.id,'aria-label':s.favorites.includes(t.id)?'取消收藏':'收藏这个主题','aria-pressed':s.favorites.includes(t.id)}))}
      <header class="v3-topic-intro ${m.color}">${badge(t.category+' · 自助整理')}<h1>${m.title}</h1><p>${t.desc}</p><span class="v3-intro-symbol" aria-hidden="true">${icon(m.ic)}</span></header>
      <div class="v3-facts"><span>${icon('edit','sm')}${V2.schemas[t.id].length} 个问题</span><span>${icon('pause','sm')}随时暂停</span><span>${icon('shield','sm')}不计分</span></div>
      <section class="topic-start"><h2>理清自己的取舍</h2><p>${esc(t.tip||'把具体经历、在意和待查信息分开整理。')}</p>${note?L('继续上次的整理','topic-workspace',{cls:'btn full',after:'arrow','data-topic':t.id,'data-id':note.id}):B('开始整理','topic-journal',{cls:'btn full','data-id':t.id,after:'arrow'})}${note?B('另建一份整理','topic-journal',{cls:'textbtn full','data-id':t.id}):''}</section><details class="topic-outline"><summary>这次会聊到什么<span>${V2.schemas[t.id].length} 个问题 ${icon('chevron','sm')}</span></summary>
      <ol class="v3-outline">${V2.schemas[t.id].map(([key,label,ph],i)=>`<li><span>${String(i+1).padStart(2,'0')}</span><div><strong>${label}</strong><p>${ph}</p></div></li>`).join('')}</ol></details>
      `;
  }
  function recordSummary(s,n){
    const d=n.fields||{},related=s.actions.filter(a=>a.sourceId===n.id),latest=related.slice().reverse()[0];
    const provenance=k=>k==='evidence'?'本人提供 · 未核验':k==='unknown'?'待查证':k==='understanding'?'当前认识 · 可以修正':'本人自述';
    return `<section class="record-summary" aria-label="已保存的整理卡"><div class="record-card-top">${badge('本人整理 · 第 '+(n.revision||1)+' 版','own')}<span>已存本机</span></div><h2>${esc(d.issue||n.title)}</h2><p class="record-insight-label">${d.priorities&&!d.understanding?'我在意的事':'我目前的认识'}</p><p class="record-insight">${esc(d.understanding||d.priorities||'还没有形成结论，也可以先保留这些条件。')}</p><details class="record-evidence"><summary>核对条件、依据与未知 ${icon('chevron','sm')}</summary><dl>${V2.topicFields(n.topicId).filter(([k])=>k!=='issue'&&k!=='understanding').map(([k,label])=>`<div><dt>${label}<span>${provenance(k)}</span></dt><dd class="${String(d[k]||'').trim()?'':'is-empty'}">${esc(d[k]||'暂未填写，不代表没有')}</dd></div>`).join('')}</dl></details><p class="record-boundary">这是你写下的整理，不是系统推荐或性格结论。未知和冲突可以保留。</p></section>
      <section class="record-next" aria-label="整理之后的选择"><h2>现在，按自己的需要选</h2><p>只留下认识也是一次有效整理，不必安排任务。</p><div class="record-next-actions">${B('先补信息','topic-edit',{cls:'btn secondary',icon:'edit'})}${B('选个小尝试','add-action',{cls:'btn tonal',icon:'flag'})}</div>${L('仅保存，回到我的记录','records',{cls:'textbtn full'})}${latest?L('回看这份整理的小尝试（'+related.length+'）','action-detail',{cls:'record-linked-action','data-id':latest.id,icon:'flag',after:'arrow'}):'<p class="record-no-action">还没有关联的小尝试；这份整理已经保留。</p>'}${B('带着已保存的记录问助理','topic-to-assistant',{cls:'textbtn full','data-id':n.id,icon:'chat'})}<p class="small muted">只带这份记录的已保存版本，可移除；不会自动发送。</p></section>`;
  }
  function topicWorkspace(s,p){
    const t=D.topics.find(x=>x.id===p.topic);if(!t)return savedViews['topic-workspace'](s,p);
    const found=s.observations.find(x=>x.id===p.id&&x.topicId===t.id);if(p.id&&!found)return savedViews['topic-workspace'](s,p);
    const fields=V2.topicFields(t.id),d=V2.getDraft(V2.topicKey(t.id,p.id),found?.fields||{}),key=V2.topicKey(t.id,p.id),step=Math.min(workspaceSteps.get(key)||0,fields.length-1),focus=s.workspaceMode==='focus',dirty=found&&V2.topicChanged(found);
    return `${top('返回',L('其他议题','explore',{cls:'textbtn'}))}${title(topicMeta[t.id].name+' · '+(found?'本人记录':'整理中'),found?'留住这一次的认识。':topicMeta[t.id].title,found?'条件变了，可以继续补充；旧版本仍保留。':(t.tip||'从具体经历开始，暂时不确定的地方可以留空。'))}
      <div class="record-path" aria-label="本次整理路径"><span class="${found?'':'current'}">记录情况</span>${icon('chevron','sm')}<span class="${found?'current':''}">留下认识</span>${icon('chevron','sm')}<span>按需尝试与回看</span></div>
      ${found?recordSummary(s,found):''}
      <details class="record-editor" ${!found||dirty?'open':''}><summary>${found?'继续编辑这份整理':'写下自己的情况'}<span>${found?'草稿与已存版本分开':'不必每项都填'}</span></summary>
      ${dirty?'<p class="record-draft-notice">有尚未正式保存的修改。上方整理卡与原小尝试仍保留原版本。</p>':''}
      <div class="v3-workspace-bar"><span id="v3-field-count">${fields.filter(([k])=>String(d[k]||'').trim()).length} / ${fields.length} 项已填写</span><div class="v3-segment" aria-label="整理方式">${[['overview','总览'],['focus','专注']].map(([id,l])=>B(l,'v3-workspace-mode',{cls:s.workspaceMode===id?'selected':'','data-id':id,'aria-pressed':s.workspaceMode===id})).join('')}</div></div>
      ${focus?`<nav class="v3-stepper" aria-label="整理问题">${fields.map(([k,label],i)=>B(String(i+1),'v3-step',{cls:step===i?'selected':'','data-index':i,'aria-label':label,'aria-current':step===i?'step':null})).join('')}</nav>`:''}
      <div class="topic-form v3-topic-form ${focus?'focused':''}">${fields.map(([k,label,ph],i)=>`<section ${focus&&i!==step?'hidden':''} data-step="${i}"><label class="field-label" for="topic-${k}"><span class="step-no">${String(i+1).padStart(2,'0')}</span>${label}</label><textarea id="topic-${k}" class="textarea" data-input="topic-field" data-field="${k}" maxlength="1500" placeholder="${esc(ph)}">${esc(d[k]||'')}</textarea>${k==='understanding'?'<p class="small muted">自己的倾向和推测可以写在这里；不当作已核实事实。</p>':''}</section>`).join('')}</div>
      ${focus?`<div class="v3-step-actions">${B('上一项','v3-step',{cls:'btn secondary','data-index':Math.max(0,step-1),disabled:step===0})}${step<fields.length-1?B('下一项','v3-step',{cls:'btn tonal','data-index':step+1,after:'arrow'}):B('回到总览','v3-workspace-mode',{cls:'btn tonal','data-id':'overview'})}</div>`:''}
      <p id="topic-error" class="record-field-error" role="alert" hidden></p><div class="v3-workspace-save">${saveState()}${B(found?'保存这次修改':'保存这份整理','topic-save',{cls:'btn full','data-topic':t.id,'data-id':found?.id||'',after:'check'})}</div></details>
      ${found?.revisions?.length?`<details class="record-history"><summary>以前的整理 · ${found.revisions.length} 个版本</summary>${found.revisions.slice().reverse().map(v=>`<details><summary>第 ${v.revision} 版 · 本人整理</summary><p>${esc(v.text)}</p></details>`).join('')}</details>`:''}
      ${found?L('回到我的记录','records',{cls:'textbtn full space-12'})+B('删除这份整理','delete-journal',{cls:'textbtn full space-12','data-id':found.id}):''}<p class="quiet-boundary">输入时保留本机草稿，点击保存后才成为一条记录。不会自动发送。</p>`;
  }
  function report(s,p){
    if(p.id&&p.id!==D.report.id)return savedViews.report(s,p);
    const work=s.reportContext!=='relationship',src=D.reportSource(work?'work':'relationship');
    const heads=work?['有准备，更好表达','也看看等待带来的影响','换个情境，再观察']:['熟悉之后，更愿回应','想参与时，怎样让对方知道','换个情境，再观察'];
    const bodies=work?['先理出几个要点，理由更容易讲清。','等到想好再说，对这次讨论有什么影响？','准备时间、话题熟悉度，各有什么影响？']:['和熟悉的人一起，更愿意认真交流。','如果想加入，可以观察怎样让对方知道。','人员熟悉度、话题和状态，各有什么影响？'];
    return `${top('返回',B('','nav',{cls:'iconbtn',icon:'share','data-route':'share','data-id':D.report.id,'aria-label':'预览分享图'}))}
      <div class="report-identity">${icon('book','sm')}我的报告</div>
      <header class="v3-report-cover"><span class="eyebrow">情境解读 · ${work?'工作表达':'人际相处'}</span><h1>${work?'给表达，<br>一点准备时间。':'熟悉之后，<br>慢慢打开自己。'}</h1><p>读一段经历，理解一种可能。</p><span class="v3-report-seal" aria-hidden="true">${icon('quote')}</span></header>
      <p class="v3-report-caption"></p>
      <nav class="report-chapters" aria-label="报告目录">${[['report-overview','要点'],['report-evidence','依据'],['report-personal','我的观察'],['report-action','下一步']].map(([id,n])=>B(n,'report-jump',{cls:'','data-id':id})).join('')}</nav>
      <section id="report-overview" class="report-block" tabindex="-1"><div class="v3-context-heading"><h2>先看这三个点</h2><div class="context-switch" aria-label="阅读情境">${[['work','工作'],['relationship','相处']].map(([id,l])=>B(l,'report-context',{cls:s.reportContext===id?'active':'','data-id':id,'aria-pressed':s.reportContext===id})).join('')}</div></div>
        <div class="v3-insights">${heads.map((h,i)=>`<article><span class="v3-insight-number" aria-hidden="true">${icon(['sun','leaf','explore'][i])}</span><div><h3>${h}</h3><p>${bodies[i]}</p></div></article>`).join('')}</div>
        ${B('这些解读从哪里来','report-jump',{cls:'v3-evidence-link','data-id':'report-evidence',icon:'link',after:'arrow'})}
      </section>
      <section id="report-evidence" class="report-block" tabindex="-1"><div class="row between"><h2>看见依据，再理解</h2>${badge('情境依据')}</div><blockquote class="quote"><span class="caption">生活片段</span>${src.excerpt}</blockquote><p class="body-copy">这段经历有多种可能解释。单次表现不能推导出人格分数。</p>${B('核对来源与版本','source-report',{cls:'source-row',icon:'link',after:'chevron'})}
        <details class="factor-detail"><summary><span>16 个因子角度</span><small>点开看说明</small></summary><p class="small muted">没有读数的因子保持空白。</p>${bottleGrid()}</details>
      </section>
      <section id="report-personal" class="report-block" tabindex="-1">${badge('本人观察 · 独立保存','own')}<h2 class="space-12">你的经历，哪里不同？</h2><p class="body-copy">哪里像你，哪里不像？也可以写下“要看情况”，再补充当时发生了什么。</p><label class="field-label space-16" for="report-note">我自己的真实经历</label><textarea id="report-note" class="textarea" data-input="report-note" maxlength="1500" placeholder="例如：在熟悉的小组里，我不太需要准备就能说清楚。">${esc(V2.getDraft('report:'+s.reportContext,''))}</textarea>${saveState()}${B('保存本人观察','save-report-note',{cls:'btn secondary full space-12',icon:'edit'})}${s.reportNotes.length?L('查看已保存的观察','records',{cls:'textbtn full'}):''}</section>
      <section id="report-action" class="report-block" tabindex="-1"><div class="next-step-panel v3-next"><span class="eyebrow">下次，试个小变化</span><h2>${work?'从两个要点说起':'从一个细节加入'}</h2><p>${work?'临时被问到时，先给自己一点整理时间，再说最想表达的两点。':'想参与对话时，先回应对方刚说的一个具体细节。'}</p>${B('留下这个小尝试','add-action',{cls:'btn full',icon:'flag','data-context':work?'work':'relationship'})}<small>可修改。只保存你选择的尝试，不建立性格结论。</small></div>${B('请AI帮我理解','quote-report',{cls:'btn secondary full space-16',icon:'chat'})}</section>
      `;
  }
  function assistant(s){
    const sample=s.assistantSources.some(x=>x.kind==='sample-report');
    return `
      <header class="v3-assistant-head"><div class="assistant-emblem" aria-hidden="true">${mark()}</div><div><h1>有什么，<br>想一起理清？</h1><p>从一件具体的事开始，慢慢说就好。</p></div></header>
      ${sample?'<div class="source-warning">'+icon('info','sm')+'本次含虚构样例，不作为你的个人记忆。</div>':''}
      ${composer(s.assistantDraft,s.assistantSources,s.logged)}
      <div class="v3-prompts">${B('理清最近一件事','prompt',{cls:'v3-prompt','data-id':'recent',icon:'leaf',after:'arrow'})}</div>
      <div class="v3-trust-line"><span>${icon('link','sm')}资料由你选</span><span>${icon('memory','sm')}记忆另行确认</span></div>
      <p class="demo-caption">预写演示 · 未接入模型；登录不会自动发送草稿。</p>
      <div class="assistant-quota">${B(s.logged?`演示剩余 ${Math.max(0,10-s.used)} / 10`:'登录后共享 10 次 / 天','quota',{cls:'textbtn',icon:'info'})}</div>
      ${section('接着上次聊',L('全部对话','conversations',{cls:'textbtn',after:'arrow'}))}
      ${s.conversations.length?s.conversations.slice(-3).reverse().map(c=>`<button class="history-row" data-action="nav" data-route="conversation" data-id="${c.id}">${icon('chat')}<span class="grow"><h3>${esc(c.title)}</h3><small>${c.messages.length} 条消息 · 本机</small></span>${icon('chevron','sm')}</button>`).join(''):'<div class="v3-chat-empty">'+icon('chat')+'<span>第一段对话，从你想说的开始。<small>草稿会留在本机，不必一次说完整。</small></span></div>'}
      <div class="plain-list space-16">${row('助理记住了什么','查看、修改或停用','memories','memory')}</div>`;
  }
  function me(s){
    const notes=[...s.observations,...s.reportNotes].sort((a,b)=>(b.createdAt||'').localeCompare(a.createdAt||'')),a=activeAction(s);
    return `
      <header class="v3-profile"><div class="profile-avatar"><img src="assets/person-${s.avatar}.svg" alt="我的插画形象"></div><div class="grow"><h1>${esc(s.name)}</h1><p>慢慢收集，具体的自己。</p></div>${B('','edit-name',{cls:'iconbtn',icon:'edit','aria-label':'修改称呼'})}</header>
      ${notes.length+s.actions.length+s.sessions.length?`<div class="v3-profile-stats"><button data-action="nav" data-route="records" data-filter="本人记录"><strong>${notes.length}</strong><span>本人记录 ${icon('chevron','sm')}</span></button><button data-action="nav" data-route="actions"><strong>${s.actions.length}</strong><span>小尝试 ${icon('chevron','sm')}</span></button><button data-action="nav" data-route="records" data-filter="全部答卷"><strong>${s.sessions.length}</strong><span>历史练习 ${icon('chevron','sm')}</span></button></div>`:''}
      <section class="v3-notebook"><span class="eyebrow">${notes.length?'最近留下':'从一句话开始'}</span><h2>${notes.length?esc(notes[0].title):'把今天，留一页。'}</h2><p>${notes.length?esc(notes[0].text.slice(0,100)):'哪一刻，你对自己多了一点了解？'}</p>${L(notes.length?'打开记录':'记一个自己的时刻',notes[0]?.kind==='topic-record'?'topic-workspace':'journal',{cls:'btn full',icon:'edit',...(notes.length?{'data-id':notes[0].id,...(notes[0].topicId?{'data-topic':notes[0].topicId}:{})}:{})})}</section>
      ${a?`<button class="v3-action-resume" data-action="nav" data-route="action-detail" data-id="${a.id}">${icon('flag')}<span class="grow"><strong>这件小事，还可以回看</strong><small>${esc(a.text)}</small></span>${icon('arrow','sm')}</button>`:''}
      ${section('我的资料，我来掌握')}
      <div class="v3-control-grid">${[['portrait','explore','正在认识的自己','来源与留白'],['memories','memory','助理记忆','确认与纠正'],['data','folder','我的数据','查看与导出'],['privacy','shield','隐私与引用','分开控制']].map(([r,i,h,p])=>L(`<span>${icon(i)}</span><strong>${h}</strong><small>${p}</small>`,r,{cls:'v3-control'})).join('')}</div>
      <div class="plain-list space-16">${row('账号与安全','管理账号和本机资料',s.logged?'account':'auth','user')}${row('找回全部记录','本人观察、专题与历史练习','records','clock')}${row('设置','主题、形象与阅读习惯','settings','settings')}${row('会员与使用次数','方案、规则与原订单','membership','crown')}</div>
      `;
  }
  function question(s,p){
    let h=savedViews.question(s,p);
    h=h.replace('<section class="question-main">','<section class="question-main v3-question-main">').replace('选更像平时的，不用选“更好”的。','选更像平时的那一个。没有标准答案。').replace('请选择一个选项，选中后保存到本机。','选择后保存；确认下一题前，可随时修改。');
    return h;
  }
  function journal(s,p){
    let h=savedViews.journal(s,p);if(h.includes('id="journal-text"'))h=h.replace('发生了什么？你当时怎么想？也可以只写一句。','一件事，一个反应，或一个新发现。').replace('<label class="field-label space-24" for="journal-text">我的记录</label>',`<div class="v3-writing-cue"><span>${icon('edit','sm')}留给自己的一页</span><small id="v3-char-count">0 / 4000</small></div><label class="sr-only" for="journal-text">我的记录</label>`);
    return h;
  }
  function appearance(s,p){
    const tile=t=>`<button class="v4-theme-card ${s.theme===t.id?'selected':''}" data-action="theme" data-id="${t.id}" aria-pressed="${s.theme===t.id}" style="--preview-scene:${t.tokens['scene-gradient']};--preview-paper:${t.tokens.paper};--preview-ink:${t.tokens.ink};--preview-primary:${t.tokens.primary}"><span class="v4-theme-landscape"><i></i><b></b><em></em></span><strong>${t.name}${s.theme===t.id?icon('check','sm'):''}</strong><small>${t.desc}</small></button>`;
    return `${top('返回')}${title('主题与形象','换一种风景。','主题、人物与阅读习惯，各自独立。')}
      <div class="v3-theme-preview v4-live-preview"><span>${badge(D.themes.find(t=>t.id===s.theme)?.name||'当前主题')}</span><h2>你的样子，<br>不止一种。</h2><div class="v4-person-scene" aria-hidden="true"><span></span><img src="assets/person-${s.avatar}.svg" alt=""></div></div>
      ${section('八种完整的主题风景')}<p class="small muted space-8">背景、按钮、因子瓶与阅读面板一起切换。</p><div class="v4-theme-grid">${D.themes.filter(t=>t.group==='原始主题').map(tile).join('')}</div>
      <details class="v4-candidates" ${D.themes.find(t=>t.id===s.theme)?.group==='历史候选'?'open':''}><summary>历次新增候选 · 4 套</summary><p class="small muted">独立保留 V1–V3 的新增方向，最终发行集合待确认。</p><div class="v4-theme-grid">${D.themes.filter(t=>t.group==='历史候选').map(tile).join('')}</div></details>
      ${section('阅读密度')}<div class="v3-density-options">${densityChoices(s)}</div><p class="small muted">紧凑只调整浏览间距，正文与主要触区不缩小。</p>
      <div class="switch-row"><span class="grow">减少动态<small class="muted" style="display:block">系统设置优先；保存与选中反馈仍清楚。</small></span><button class="switch ${s.reduced?'on':''}" role="switch" aria-checked="${s.reduced}" aria-label="减少动态" data-action="toggle-motion"><span></span></button></div>
      ${section('原始人物 · 三个预设')}<div class="avatar-options v4-avatar-options">${[1,2,3].map(i=>`<button class="${s.avatarFamily==='original'&&s.avatar===i?'selected':''}" data-action="avatar" data-id="${i}" data-family="original" aria-pressed="${s.avatarFamily==='original'&&s.avatar===i}"><img src="assets/original-person-${i}.webp" alt="原始人物预设 ${i}"><span>人物 ${String(i).padStart(2,'0')}</span></button>`).join('')}</div>
      ${section('更多人物')}<div class="avatar-options v4-avatar-options">${[1,2,3].map(i=>`<button class="${s.avatarFamily!=='original'&&s.avatar===i?'selected':''}" data-action="avatar" data-id="${i}" data-family="scene" aria-pressed="${s.avatarFamily!=='original'&&s.avatar===i}"><img src="assets/legacy-person-${i}.svg" alt="场景人物预设 ${i}"><span>场景 ${String(i).padStart(2,'0')}</span></button>`).join('')}</div><p class="quiet-boundary">人物与主题可以分别选择。</p>`;
  }
  function densityChoices(s){return [['balanced','舒展','留一点呼吸'],['compact','紧凑','一眼多看一点']].map(([id,l,d])=>B(`<strong>${l}</strong><small>${d}</small>`,'v3-density',{cls:'v3-density-option '+(s.density===id?'selected':''),'data-id':id,'aria-pressed':s.density===id})).join('');}
  function preferences(){const s=C.state;C.show('按你的阅读习惯',`<p class="small muted">浏览页可以紧凑一点。答题和长文仍保留阅读空间。</p><h3 class="space-16">阅读密度</h3><div class="v3-density-options">${densityChoices(s)}</div><div class="switch-row"><span class="grow">减少动态<small class="muted" style="display:block">系统减少动态优先。</small></span><button class="switch ${s.reduced?'on':''}" data-action="v3-motion" role="switch" aria-label="减少动态" aria-checked="${s.reduced}"><span></span></button></div><p class="small muted">不改文字大小，不改题目，不隐藏保存失败提示。</p>`,B('按这个方式阅读','close-dialog',{cls:'btn full'}));}
  function applyPreferences(){
    document.body.dataset.density=C.state.density==='compact'?'compact':'balanced';
    document.body.classList.toggle('reduce-motion',!!C.state.reduced);
    Ambient.setContext({quiet:C.current().split('?')[0]==='question'||AssessmentPreview.isQuiet(),reduced:C.state.reduced});
    document.querySelectorAll('[data-action="v3-density"]').forEach(b=>{const on=b.dataset.id===C.state.density;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',String(on));});
    document.querySelectorAll('[data-action="v3-motion"]').forEach(b=>{b.classList.toggle('on',C.state.reduced);b.setAttribute('aria-checked',String(C.state.reduced));});
  }
  function dispatch(action,el){
    if(AssessmentPreview.dispatch(action,el))return true;
    const ds=el?.dataset||{};
    switch(action){
      case 'v3-preferences':preferences();return true;
      case 'v3-density':if(!['balanced','compact'].includes(ds.id))return true;if(C.commit(s=>s.density=ds.id)){applyPreferences();C.toast(ds.id==='compact'?'已切换紧凑浏览；文字和点击区域保持原尺寸。':'已切换舒展浏览。');}return true;
      case 'v3-motion':if(C.commit(s=>s.reduced=!s.reduced)){applyPreferences();if(C.state.reduced)document.getAnimations().forEach(a=>a.cancel());}return true;
      case 'v3-workspace-mode':if(!['overview','focus'].includes(ds.id))return true;if(C.commit(s=>s.workspaceMode=ds.id)){const open=document.querySelector('.record-editor')?.open;C.repaint();if(open)document.querySelector('.record-editor')?.setAttribute('open','');}return true;
      case 'v3-step':{const [,q]=C.current().split('?'),p=Object.fromEntries(new URLSearchParams(q||'')),schema=V2.topicFields(p.topic);if(!schema)return true;const index=Number(ds.index);if(!Number.isInteger(index)||index<0||index>=schema.length)return true;workspaceSteps.set(V2.topicKey(p.topic,p.id),index);C.repaint();document.querySelector('.record-editor')?.setAttribute('open','');document.querySelector('.v3-topic-form section:not([hidden]) textarea')?.focus({preventScroll:true});return true;}
      default:return false;
    }
  }
  function reduced(){return matchMedia('(prefers-reduced-motion: reduce)').matches||C?.state.reduced;}
  function afterRender(){
    if(!C)return;applyPreferences();const r=C.current();document.body.dataset.route=r.split('?')[0];
    const active=previousRoute!==r;previousRoute=r;
    if(active&&!reduced()){document.querySelector('main')?.animate([{opacity:.35,transform:'translateY(7px)'},{opacity:1,transform:'translateY(0)'}],{duration:200,easing:'cubic-bezier(.2,.8,.2,1)'});}
    document.querySelectorAll('.report-chapters button').forEach(b=>b.setAttribute('aria-current',b.dataset.id==='report-overview'?'location':'false'));
    chapterObserver?.disconnect();chapterObserver=null;
    if(chapterScroll)window.removeEventListener('scroll',chapterScroll);chapterScroll=null;
    if(chapterFrame)cancelAnimationFrame(chapterFrame);chapterFrame=0;
    if(document.querySelector('.report-chapters')){
      const syncChapter=()=>{
        const bar=document.querySelector('.report-chapters'),blocks=[...document.querySelectorAll('.report-block')];if(!bar||!blocks.length)return;
        // The chapter occupying most of the unobscured reading viewport owns
        // the indicator, including centered anchors and large text layouts.
        const top=Math.max(0,bar.getBoundingClientRect().bottom),bottom=innerHeight;
        const visible=el=>{const r=el.getBoundingClientRect();return Math.max(0,Math.min(r.bottom,bottom)-Math.max(r.top,top));};
        const active=blocks.reduce((best,el)=>visible(el)>visible(best)?el:best,blocks[0]);
        bar.querySelectorAll('button').forEach(b=>b.setAttribute('aria-current',b.dataset.id===active.id?'location':'false'));
      };
      chapterScroll=()=>{if(!chapterFrame)chapterFrame=requestAnimationFrame(()=>{chapterFrame=0;syncChapter();});};
      window.addEventListener('scroll',chapterScroll,{passive:true});
      chapterObserver=new IntersectionObserver(syncChapter,{rootMargin:'-64px 0px -55% 0px',threshold:0});
      document.querySelectorAll('.report-block').forEach(el=>chapterObserver.observe(el));syncChapter();
    }
    updateCounts();AssessmentPreview.afterRender();
  }
  function updateCounts(){
    const count=document.getElementById('v3-char-count'),editor=document.getElementById('journal-text');if(count&&editor)count.textContent=editor.value.length+' / 4000';
    const fields=[...document.querySelectorAll('[data-input="topic-field"]')],c=document.getElementById('v3-field-count');if(c)c.textContent=fields.filter(t=>t.value.trim()).length+' / '+fields.length+' 项已填写';
  }
  document.addEventListener('input',e=>{if(e.target.matches('textarea'))requestAnimationFrame(updateCounts);});
  // Feedback never holds up an operation. Pointer and keyboard share the same semantics.
  document.addEventListener('click',e=>{if(reduced())return;const b=e.target.closest('button');if(!b||b.disabled)return;const id=b.dataset.id,action=b.dataset.action;
    requestAnimationFrame(()=>{const target=b.isConnected?b:document.querySelector(`[data-action="${CSS.escape(action||'')}"]${id?'[data-id="'+CSS.escape(id)+'"]':''}`);if(target?.isConnected&&['answer','favorite','action-outcome'].includes(action)){target.animate([{transform:'scale(.985)'},{transform:'scale(1.018)'},{transform:'scale(1)'}],{duration:220,easing:'cubic-bezier(.2,.8,.2,1)'});}});
  });
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',e=>{if(e.matches)document.getAnimations().forEach(a=>a.cancel());});
  Object.assign(Views.map,{home,explore,topic,'topic-workspace':topicWorkspace,report,assistant,me,question,journal,appearance});
  return {exploreResults,bind(c){C=c;AssessmentPreview.bind(c);},dispatch,afterRender,reset(){workspaceSteps.clear();previousRoute=null;},topicMeta};
})();
