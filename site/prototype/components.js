window.UI = (()=>{
 const paths={
  briefcase:'<rect x="3" y="7" width="18" height="14" rx="3"/><path d="M8 7V4h8v3M3 12c5 3 13 3 18 0M10 13v3h4v-3"/>',
  key:'<circle cx="8" cy="8" r="5"/><path d="m12 12 9 9m-5-5 3-3m-6 0 3-3"/>',
  home:'<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
  explore:'<circle cx="12" cy="12" r="9"/><path d="m16 8-3 5-5 3 3-5z"/>',
  portrait:'<rect x="4" y="2" width="16" height="20" rx="4"/><circle cx="12" cy="9" r="3"/><path d="M7 18a5 5 0 0 1 10 0"/>',
  chat:'<path d="M21 11a8 8 0 0 1-8 8H7l-5 3 1-7a9 9 0 1 1 18-4Z"/><path d="M7 9h9M7 13h6"/>',
  user:'<circle cx="12" cy="7" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
  arrow:'<path d="M4 12h16m-6-6 6 6-6 6"/>',chevron:'<path d="m9 5 7 7-7 7"/>',back:'<path d="m14 5-7 7 7 7"/>',
  close:'<path d="m6 6 12 12M6 18 18 6"/>',check:'<path d="m5 12 4 4L19 6"/>',
  sparkle:'<path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5Z"/>',
  palette:'<path d="M12 3a9 9 0 0 0 0 18h1a2.5 2.5 0 0 0 1.3-4.6 1.2 1.2 0 0 1 .6-2.3H18A4 4 0 0 0 22 10c0-4-5-7-10-7Z"/><circle cx="7" cy="10" r=".9"/><circle cx="10" cy="6.8" r=".9"/><circle cx="15" cy="7" r=".9"/>',
  bottle:'<path d="M8 3h8M9 3v5l-3 4v8a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-8l-3-4V3M7 14c3-2 6 2 10 0"/>',
  leaf:'<path d="M4 20c0-9 3-16 16-16 0 13-7 16-16 16Z"/><path d="m4 20 10-10"/>',
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1"/>',
  book:'<path d="M12 5c-3-2-6-2-10-1v15c4-1 7-1 10 1 3-2 6-2 10-1V4c-4-1-7-1-10 1Zm0 0v15"/>',
  search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',filter:'<path d="M4 7h16M7 12h10M10 17h4"/>',
  shield:'<path d="M12 2 3 6v6c0 5 9 10 9 10s9-5 9-10V6z"/><path d="m8 12 3 3 5-6"/>',
  dialogue:'<path d="M14 5H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h1v3l4-3h4a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Z"/><path d="M19 9h1a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-1v3l-4-3h-3a2 2 0 0 1-2-2"/>',
  link:'<path d="m9 8 3-3a5 5 0 1 1 7 7l-3 3M8 9l-3 3a5 5 0 0 0 7 7l3-3M8 16l8-8"/>',
  send:'<path d="m21 3-6 18-4-8-8-4 18-6Zm-10 10L21 3"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v6l4 2"/>',
  settings:'<path d="m10 2-1 3-3 1-3-1-2 4 2 3-1 3 3 2 2 3 4-1 3 2 3-2 1-3 3-2-1-4 1-3-3-2-3-2z"/><circle cx="12" cy="12" r="3"/>',
  edit:'<path d="m16 3 5 5-12 12-6 1 1-6L16 3Zm-3 3 5 5"/>',
  folder:'<path d="M3 6h6l2-3h6l4 3v14H3z"/><path d="M3 8h18"/>',
  memory:'<path d="M9 3C4 2 1 8 5 11c-5 5 1 11 5 9V4m5-1c5-1 8 5 4 8 5 5-1 11-5 9V4M6 9l4 1m4 4 5-1M7 17l3-2"/>',
  plus:'<path d="M12 4v16M4 12h16"/>',
  pause:'<path d="M8 5v14M16 5v14"/>',
  warning:'<path d="M11 3 2 19a1 1 0 0 0 1 2h18a1 1 0 0 0 1-2L13 3a1 1 0 0 0-2 0Z"/><path d="M12 8v6m0 3v.5"/>',
  download:'<path d="M12 2v13m-5-5 5 5 5-5M3 15v6h18v-6"/>',
  upload:'<path d="M12 16V3m-5 5 5-5 5 5M3 15v6h18v-6"/>',
  share:'<path d="M12 16V2m-5 5 5-5 5 5M6 11H3v11h18V11h-3"/>',
  info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v.5"/>',
  lock:'<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4m-4 5v2"/>',
  flag:'<path d="M5 22V3c5-4 9 4 15 0v10c-6 4-10-4-15 0"/>',
  crown:'<path d="m3 7 4 4 5-7 5 7 4-4-2 12H5L3 7Zm2 15h14"/>',
  card:'<rect x="2" y="4" width="20" height="16" rx="3"/><path d="M2 9h20M6 15h5"/>',
  bell:'<path d="M4 17h16l-2-4V8a6 6 0 0 0-12 0v5zM9 21h6"/>',
  help:'<circle cx="12" cy="12" r="9"/><path d="M9 8a3 3 0 1 1 5 3c-1 1-2 1-2 3m0 3v.3"/>',
  refresh:'<path d="M21 10a9 9 0 0 0-16-5L2 8m0-5v5h5M3 14a9 9 0 0 0 16 5l3-3m0 5v-5h-5"/>',
  trash:'<path d="M3 6h18M8 6V3h8v3M5 6l1 15h12l1-15M10 10v7m4-7v7"/>',
  bookmark:'<path d="M5 3h14v19l-7-5-7 5z"/>',
  wifi:'<path d="M2 7a16 16 0 0 1 20 0M5 11a11 11 0 0 1 14 0M8 15a6 6 0 0 1 8 0m-4 4v.3"/>',
  more:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  quote:'<path d="M4 11h5v8H2v-8c0-5 3-8 7-8m8 8h5v8h-7v-8c0-5 3-8 7-8"/>'
 };
 function esc(v=''){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
 function icon(name,cls=''){return `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]||paths.info}</svg>`;}
 function mark(){return '<img class="brand-mark brand-logo" src="assets/zhiyu-logo.png" alt="知遇测评标志" width="40" height="40">';}
 function attrs(obj={}){return Object.entries(obj).map(([k,v])=>v==null||(v===false&&!k.startsWith('aria-'))?'':` ${k}="${esc(typeof v==='boolean'&&k.startsWith('aria-')?String(v):v===true?'':v)}"`).join('');}
 function button(label,action,options={}){const {cls='btn',icon:ic='',after='',...a}=options;return `<button class="${cls}" data-action="${action}"${attrs(a)}>${ic?icon(ic):''}${label}${after?icon(after,'end'):''}</button>`;}
 function link(label,route,options={}){return button(label,'nav',{'data-route':route,...options});}
 function top(label,extra=''){return `<div class="topline">${button(label||'返回','back',{cls:'back',icon:'back'})}${extra}</div>`;}
 function tabs(active){return `<nav class="nav" aria-label="主导航">${[['home','home','认识'],['explore','explore','探索'],['assistant','portrait','我的画像'],['me','user','我的']].map(([id,ic,name])=>`<button data-action="tab" data-route="${id}" class="${active===id?'active':''}" ${active===id?'aria-current="page"':''}><span class="navicon">${icon(ic)}</span><span>${name}</span></button>`).join('')}</nav>`;}
 function row(title,sub,route,ic='folder',trail='',options={}){const {action='nav',...a}=options;return `<button class="list-item" data-action="${action}" data-route="${route}"${attrs(a)}><span class="list-symbol">${icon(ic,'sm')}</span><span class="grow"><span class="label">${title}</span>${sub?`<span class="sub" style="display:block">${sub}</span>`:''}</span><span class="trail">${trail}${icon('chevron','sm')}</span></button>`;}
 let bidx=0;
 function bottle(f,large=false){const [code,label,val,color]=f;const id='bottle-'+(++bidx);const y=val==null?80:76-45*val;return `<svg class="bottle-svg" viewBox="0 0 58 100" aria-hidden="true"><defs><clipPath id="${id}"><path d="M20 9h18v19c0 6 12 11 12 19v42c0 5-4 8-9 8H17c-5 0-9-3-9-8V47c0-8 11-13 11-19z"/></clipPath><linearGradient id="${id}g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="var(--${color})"/><stop offset="1" stop-color="var(--primary)"/></linearGradient></defs><path d="M20 9h18v19c0 6 12 11 12 19v42c0 5-4 8-9 8H17c-5 0-9-3-9-8V47c0-8 11-13 11-19z" fill="${val==null?'var(--unknown-fill)':'var(--surface)'}" stroke="var(--line)" stroke-width="1.3" ${val==null?'stroke-dasharray="3 3"':''}/>${val==null?'<text x="29" y="66" font-size="20" text-anchor="middle" fill="var(--muted)">?</text>':`<g clip-path="url(#${id})"><path d="M3 ${y}c17-6 33 8 55 1v55H0z" fill="url(#${id}g)"/><path d="M5 ${y+5}c17-5 33 7 51 0" stroke="#fff" stroke-opacity=".55" fill="none"/><rect x="14" y="47" width="3" height="36" rx="2" fill="#fff" opacity=".5"/></g>`}<rect x="18" y="4" width="22" height="7" rx="2.4" fill="${val==null?'var(--unknown-fill)':'var(--'+color+')'}" stroke="var(--line)" stroke-width="1"/><path d="M24 15v13" stroke="white" stroke-width="2.2" stroke-linecap="round"/></svg>`;}
 function bottleGrid(factors=D.factors){return `<div class="bottle-grid">${factors.map(f=>`<button class="bottle-tile" data-action="factor" data-id="${f[0]}" aria-label="${esc(f[0]+' '+f[1]+(f[2]===null?'，暂无依据，查看说明':'，位置仅为示意，查看说明'))}">${bottle(f)}<span class="code">${f[0]}</span><span class="name">${f[1]}</span><span class="state">${f[2]===null?'暂无依据':'位置示意'}</span></button>`).join('')}</div>`;}
 function sourceChip(src){return `<div class="source-chip">${icon('link','sm')}<div class="body"><strong>${esc(src.title)}</strong>${esc(src.excerpt.length>38?src.excerpt.slice(0,38)+'…':src.excerpt)}</div><button class="remove" data-action="remove-source" data-id="${esc(src.id)}" aria-label="移除本次引用">${icon('close','sm')}</button></div>`;}
 function portraitMap(count=0){return `<div class="portrait-map"><svg viewBox="0 0 300 195" role="img" aria-label="个人认识关系图；节点位置不表示分数。${count?'有本人观察，其余角度暂无依据。':'所有角度暂无依据，用灰色留白。'}"><path d="M150 96 69 44m81 52 83-51m-83 51L49 130m101-34 96 37m-96-37v77" stroke="var(--line)" stroke-dasharray="4 6" stroke-width="1.2"/><circle cx="150" cy="96" r="32" fill="var(--surface)" stroke="var(--line)"/><path d="M139 104c-6-11 0-23 10-21 12 3 14 15 5 22-5 4-12 4-15-1Z" stroke="var(--primary)" fill="var(--tint)" stroke-width="1.5"/>${[[69,44,'做事方式'],[233,45,'相处方式'],[49,130,'情绪情境'],[246,133,'我的选择'],[150,173,'本人观察']].map(([x,y,label],i)=>`<circle cx="${x}" cy="${y}" r="${i===4?17:18}" fill="${i===4&&count?'var(--tint)':'var(--unknown-fill)'}" stroke="${i===4&&count?'var(--primary)':'var(--line)'}"/><text x="${x}" y="${y+4}" text-anchor="middle" font-size="12">${i===4&&count?count:'?'}</text><text x="${x}" y="${y+(i===4?-25:33)}" text-anchor="middle">${label}</text>`).join('')}</svg></div>`;}
 function composer(draft,sources,logged,conversation=false){return `<div class="composer">${sources.map(sourceChip).join('')}<label class="sr-only" for="chat-draft">说说你想整理的事</label><textarea id="chat-draft" data-input="chat-draft" placeholder="从一件小事开始，也可以。" maxlength="4000">${esc(draft)}</textarea><div class="compose-foot">${button(sources.length?`已选 ${sources.length} 份资料`:'选择本次资料','context',{cls:'source-btn',icon:'plus'})}${button('发送','send',{cls:'btn send',after:'send'})}</div></div>`;}
 function empty(title,desc,action){return `<div class="entry-empty"><h3>${title}</h3><p>${desc}</p>${action||''}</div>`;}
 function sampleShare(context){return context==='relationship'?{context:'人际相处',lines:['熟悉之后，','慢慢打开自己。'],body:'回应一个细节，也是一种参与。'}:{context:'工作表达',lines:['先想清楚，','再慢慢说出来。'],body:'一段准备时间，可能让表达更从容。'};}
 return {sampleShare,esc,icon,mark,attrs,button,link,top,tabs,row,bottle,bottleGrid,sourceChip,portraitMap,composer,empty};
})();
