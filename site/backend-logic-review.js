/* Read-only public architecture documents. No business API, uploads or SDKs. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const {escape: E, renderValue, bindSearch} = DevelopmentReview;
  const params = new URLSearchParams(location.hash.slice(1));
  const state = {doc: params.get('logicDoc') === 'cloud' ? 'cloud' : 'local', section: params.get('logicSection') || '', query: params.get('logicQuery') || '', status: params.get('logicStatus') || ''};
  const definitions = {
    local: {title: '本地题库与引擎', file: 'architecture-plan.json', first: 'executiveSummary', chapters: {executiveSummary:'先读：已明确与候选方向', sections:'题库交付、引擎与恢复', modeBoundaries:'六类测评模式边界', entities:'17个实体', modules:'9个职责模块', operations:'11项操作语义', flows:'8条时序与异常', acceptance:'18项待执行验收', decisions:'7组待决问题', implementationStages:'建议实施顺序', pageCoverage:'29个页面关联', sources:'出处与证据边界', meta:'方案范围与状态口径'}},
    cloud: {title: '数据与云边界', file: 'cloud-boundaries.json', first: 'summary', chapters: {summary:'先读：边界摘要', candidateBoundary:'三个条件候选', dataClasses:'11类数据与最小外发', trustLevels:'3级材料可信度', conditionalFlows:'7条条件流程', syncContract:'同步与版本约束', quotaContract:'身份、权益与额度', aiGuards:'按次AI授权边界', historyRepairs:'13项历史修补条款', errorMatrix:'20种异常与恢复', decisions:'11组待决问题', minimalModules:'6个最小职责模块', acceptance:'28项待执行验收', counterexamples:'10项反例核查', officialSources:'官方出处', nonGoals:'本轮不做什么', baseline:'基线口径', classificationLegend:'状态标签定义', validation:'源数据核查范围'}}
  };
  const labels = {
    title:'名称',local:'本机数据',steps:'步骤',expected:'预期结果',product:'产品',text:'说明',basis:'依据',store:'存储归属',fields:'字段',invariant:'不变量',owns:'负责',output:'输出',deployment:'部署边界',normal:'正常时序',exceptions:'异常分支',execution:'验收执行状态',existingAcceptanceRefs:'关联既有验收',existingDecisionIds:'关联既有待决',decisionRefs:'关联待决',blocks:'阻断范围',canProceed:'可先分析的范围',deliverables:'建议交付物',exitGate:'退出门禁',sourceIds:'出处编号',sources:'出处',supports:'支持内容',checkedAt:'核查日期',pages:'关联页面',pageIds:'关联页面',pageId:'关联页面',pageName:'页面名称',references:'关联方案条目',modeBoundaries:'模式边界',sections:'条款',entities:'实体',modules:'职责模块',operations:'操作',flows:'时序',acceptance:'待执行验收',items:'具体条款',phase:'阶段',publicSafe:'公开摘要',notAReleaseDecision:'不能替代的决定',statusLegend:'状态口径',minimumEgress:'最小按次外发',cloudRetention:'云端留存边界',excluded:'不包含',classification:'状态分类',decisionIds:'关联待决',verified:'已能核验',limits:'证据限制',minimum:'最小材料',stop:'停止条件',rules:'约束',guards:'授权与防护',historicalGapId:'历史缺口编号',implementation:'实施状态',forbidden:'禁止行为',choices:'待选方案',recommendation:'建议',newDecisionIdsCreated:'是否新增决策编号',excludes:'不负责',setup:'验收准备',mustNot:'不得发生',confirmed:'已明确',notYetApproved:'尚未批准的三个候选',readingRule:'阅读规则',referenceId:'关联编号',schema:'结构核查',businessImplementation:'业务实施',runtimeTests:'业务运行测试',officialSourceCheck:'官方资料核查边界',referencedEntries:'设计条目数',allPageRequirementDecisionIdsExist:'页面/需求/待决关联有效',requirementCount:'需求数量',acceptanceCount:'既有验收数量',decisionCount:'既有待决数量',pageCount:'页面数量',historicalRepairsCount:'历史修补数量',requirementsVersion:'需求版本',unresolved:'仍待确认',gate:'适用前提',summary:'摘要',asOf:'日期',schemaVersion:'数据格式版本',meta:'方案范围'
  };
  const cache = new Map();
  let navigate = () => {}, save = () => {}, ticket = 0, visible = 20, current = null;
  const pageNode = id => WorkbenchData.routes.find(r => r.id === id) || WorkbenchData.routes.find(r => r.route?.split('?')[0] === id);
  function pageLinks(ids) {
    return (Array.isArray(ids) ? ids : [ids]).map(id => {
      const node = pageNode(id);
      return node ? `<button class="small-button" data-logic-page="${E(node.id)}">${E(node.name)} · ${E(id)}</button>` : E(id);
    }).join(' ');
  }
  function body(value, urls) {
    return renderValue(value, {labels, link: url => urls.has(url), field: (key, value) => ['pages','pageIds','pageId'].includes(key) ? pageLinks(value) : undefined});
  }
  function documentRows(data, def) {
    return Object.keys(def.chapters).flatMap(section => {
      const entries = Array.isArray(data[section]) ? data[section] : [data[section]];
      return entries.filter(x => x !== undefined).map((entry, i) => ({section, entry, id: entry?.id || entry?.pageId || `${section}-${i+1}`, title: entry?.title || entry?.pageName || entry?.id || (typeof entry === 'string' ? entry : def.chapters[section]), status: entry?.classification || entry?.status || '', search: JSON.stringify(entry).toLowerCase()}));
    });
  }
  async function load(file) {
    if (!cache.has(file)) {
      const request = (async () => {
        const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 15000);
        try {
          const response = await fetch('handoff/backend-logic/' + file, {signal: controller.signal});
          if (!response.ok) throw Error('HTTP ' + response.status);
          return await response.json();
        } finally { clearTimeout(timeout); }
      })();
      cache.set(file, request);
      request.catch(() => cache.delete(file));
    }
    return cache.get(file);
  }
  function rows() {
    const {items, def, urls} = current, query = state.query.trim().toLowerCase();
    const matched = items.filter(r => (state.section === 'all' || r.section === state.section) && (!state.status || r.status === state.status) && (!query || (r.title + r.id + r.search + def.chapters[r.section]).toLowerCase().includes(query)));
    $('logic-count').textContent = `${matched.length} 项匹配 · 当前展示 ${Math.min(visible, matched.length)} 项；条款和验收均为只读方案。`;
    $('logic-clear').hidden = !state.query;
    $('logic-rows').innerHTML = matched.length ? matched.slice(0,visible).map(r => `<details class="dev-fold logic-item" data-logic-id="${E(r.id)}"><summary><span class="logic-item-title">${E(r.title)}</span><span class="logic-item-meta">${E(def.chapters[r.section])} · ${E(r.id)}${r.status ? ` · <b>${E(r.status)}</b>` : ''}</span></summary><div class="dev-fold-body">${body(r.entry, urls)}</div></details>`).join('') : '<p class="dev-empty">没有匹配条目。可清空搜索，或将目录、状态切换为全部。</p>';
    $('logic-more').hidden = visible >= matched.length;
    $('logic-rows').querySelectorAll('[data-logic-page]').forEach(button => button.onclick = () => navigate(button.dataset.logicPage, 'contract'));
    save();
  }
  async function render() {
    const generation = ++ticket, root = $('panel-logic'), def = definitions[state.doc];
    root.innerHTML = '<p class="dev-loading" role="status">正在载入公开方案…</p>';
    try {
      const data = await load(def.file);
      if (generation !== ticket) return;
      const items = documentRows(data, def), legend = data.meta?.statusLegend || data.classificationLegend;
      if (!def.chapters[state.section] && state.section !== 'all') state.section = def.first;
      if (!Object.keys(legend).includes(state.status)) state.status = '';
      const urls = new Set((data.sources || data.officialSources).map(s => s.url).filter(url => /^https:\/\//.test(url || '')));
      current = {items, def, urls}; visible = 20;
      const candidate = data.meta ? (data.executiveSummary.find(item => item.id === 'A-03')?.text || data.meta.notAReleaseDecision) : data.candidateBoundary.notYetApproved;
      root.innerHTML = `<div class="dev-heading"><div><p class="dev-kicker">阶段二 · 只读方案 · ${E(data.meta?.asOf || data.asOf)}</p><h3>底层逻辑方案</h3></div><button class="small-button" id="logic-return">返回当前页开发说明</button></div><p class="spec-callout">${E(data.meta?.implementationStatus || data.status)}。${E(candidate)}</p><p class="doc-lead">${E(data.meta?.scope || data.scope)}</p><div class="logic-docs" role="group" aria-label="选择方案">${Object.entries(definitions).map(([key,d])=>`<button class="small-button" data-logic-doc="${key}" aria-pressed="${key===state.doc}">${E(d.title)}</button>`).join('')}</div><h4 class="doc-section">${E(data.meta?.title || data.title)}</h4><details class="dev-fold"><summary>状态标签怎么读</summary><div class="dev-fold-body">${body(legend,urls)}</div></details><div class="dev-search"><label for="logic-query">搜索本方案的条款、实体、页面或编号</label><div><input id="logic-query" type="search" value="${E(state.query)}" placeholder="输入后搜索全部目录"><button id="logic-clear" class="small-button" aria-label="清空底层逻辑搜索">清空</button></div></div><div class="dev-filters"><label>阅读目录<select id="logic-section"><option value="all">全部目录 · ${items.length}</option>${Object.entries(def.chapters).map(([key,title])=>`<option value="${key}">${E(title)} · ${items.filter(r=>r.section===key).length}</option>`).join('')}</select></label><label>文档状态<select id="logic-status"><option value="">全部状态</option>${Object.keys(legend).map(s=>`<option>${E(s)}</option>`).join('')}</select></label></div><p id="logic-count" role="status"></p><div id="logic-rows"></div><button class="small-button" id="logic-more">再显示20项</button><p class="panel-foot">官方出处用于解释方案依据，不代表供应商、SDK或业务实现已选定。两份文档的状态原文分别保留；待执行验收没有被标成已通过。</p>`;
      $('logic-section').value = state.section; $('logic-status').value = state.status;
      $('logic-return').onclick = () => navigate(null,'contract');
      root.querySelectorAll('[data-logic-doc]').forEach(button => button.onclick = async () => {const selected=button.dataset.logicDoc;state.doc=selected;state.section=definitions[state.doc].first;state.query='';state.status='';save();await render();if(state.doc===selected)$('panel-logic').querySelector(`[data-logic-doc="${selected}"]`)?.focus();});
      bindSearch($('logic-query'), $('logic-clear'), query => {state.query=query;state.section='all';visible=20;$('logic-section').value='all';rows();});
      $('logic-section').onchange = event => {state.section=event.target.value;visible=20;rows();};
      $('logic-status').onchange = event => {state.status=event.target.value;visible=20;rows();};
      $('logic-more').onclick = () => {visible+=20;rows();};
      rows();
    } catch {
      if (generation !== ticket) return;
      root.innerHTML='<div class="dev-loading" role="status"><p>方案资料暂未载入。实际页面和已保存资料不受影响。</p><button class="small-button" id="logic-retry">重试加载方案</button></div>';
      $('logic-retry').onclick=render;
    }
  }
  window.BackendLogicReview = {render, configure(onNavigate,onSave){navigate=onNavigate;save=onSave;}, stateParams(){return {logicDoc:state.doc,logicSection:state.section,logicQuery:state.query,logicStatus:state.status};}};
})();
