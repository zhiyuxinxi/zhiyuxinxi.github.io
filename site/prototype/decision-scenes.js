/* Public-facing scene summaries only. No source workbook, test questions or scoring rules. */
window.DecisionScenes=(()=>{
 const rows=[
 ['work-move','工作','要不要辞职换工作？','看清离职原因、外部机会和空窗承受力。','换同类工作','lime','explore','把想离开的原因，和下一份工作想得到的东西分开写。',['目前的工作发生了什么？','下一份工作最想保留或得到什么？','换工作有哪些现实顾虑？','决定前，还需要核实哪些机会？'],['写具体经历，以及已经了解到的同类岗位。','例如岗位内容、收入、团队或通勤，哪些最重要？','例如空窗收入、交接安排或家庭时间。','列出需要问清的职责、待遇、招聘要求。']],
 ['exam-retake','学业','要不要二战考研？','分清读研意愿与外部期待，看看再投入一年的条件。','再考一年','lavender','book','把想读研的理由，和对上次结果的不甘心分别写下来。',['第一次考研后，我知道了什么？','读研对我真正重要的是什么？','再投入一年需要面对哪些条件？','关于备考或读研，还缺哪些信息？'],['如实记录备考投入、结果和感受，不必只看分数。','哪些来自自己的目标，哪些来自他人的期待？','时间、经济支持、精力和其他去向分别怎样？','例如院校要求、专业方向或另一条职业路径。']],
 ['relationship-break','关系','要不要分手？','看清反复犹豫的原因、关系需要和改变空间。','关系的去留','peach','chat','先写让你犹豫的具体经历，再区分愿望与已经发生的改变。',['哪些具体经历让我反复犹豫？','我在这段关系里最需要什么？','继续或结束，各有什么顾虑？','还有什么需要想清或确认？'],['记录发生的事和你的感受，不必替对方下结论。','例如尊重、回应、边界或共同生活的期待。','哪些是现实安排，哪些是担心或舍不得？','可以是需要沟通的事，也可以是需要的支持。']],
 ['unpaid-break','工作','要不要裸辞休息？','想清休整需要、资金缓冲和回归准备。','先停下来','cream','sun','想一想休息要改变什么，再算一算可以从容停留多久。',['我为什么想现在停下来？','这段休整最想恢复或安排什么？','没有收入时，需要照顾哪些条件？','回到工作前，还要做什么准备？'],['哪些具体经历让你感到需要休整？','例如作息、照顾家人、恢复精力或探索方向。','生活开支、储备、家庭责任和支持有哪些？','还有哪些信息要查，哪些安排可以先尝试？']],
 ['city-return','生活','留在大城市，还是回老家？','对比发展机会、生活成本、归属感和家庭支持。','换座城市','blue','home','把两个地方的日常生活都具体写一天，别只比较想象。',['两个地方的现实条件分别怎样？','怎样的生活让我更有归属感？','各自有哪些不能忽略的限制？','搬迁前还需要核实什么？'],['写已知的工作机会、收入、住处和支持。','工作、朋友、家庭距离，哪些对你更重要？','比较生活成本、照护责任和通勤等实际条件。','例如岗位机会、住房支出、生活节奏。']],
 ['career-change','工作','要不要转行？','梳理可迁移能力、信息缺口和低成本尝试。','换个行业','lime','explore','先区分对当前岗位的不满，和对新行业的真实兴趣。',['我对当前与目标行业知道什么？','新方向吸引我的具体地方是什么？','转行有哪些投入和现实限制？','怎样先验证一个未知？'],['哪些来自亲历，哪些只是听说？写下已有经验。','有哪些能力可以迁移，哪些需要重新学习？','例如收入变化、学习时间或求职门槛。','可以先访谈从业者、试做项目或短期学习。']],
 ['independent-home','生活','要不要搬出去住？','分清空间需要、经济准备和家人期待。','独立生活','blue','home','把“想有自己的空间”拆成具体需要，再看看怎样满足。',['当前居住中，哪些事影响我？','我希望独立生活带来什么变化？','搬出去要承担哪些成本和责任？','行动前，还需查清或沟通什么？'],['写相处、空间、作息或通勤中的具体经历。','例如自主安排、安静时间或生活边界。','房租、生活开支、家务和家庭责任怎样安排？','例如实际预算、位置安全或家人的期待。']],
 ['first-job','工作','第一份工作，稳定还是成长？','比较收入需要、岗位匹配和成长机会。','第一份工作','cream','book','把“稳定”和“成长”拆成岗位里能核实的条件。',['正在比较的岗位具体怎样？','现阶段最重要的需要是什么？','两个选择各有什么代价？','接受之前，还要问清什么？'],['写职责、薪资、培养安排和已知的团队情况。','例如收入保障、学习机会、地点或工作节奏。','哪些条件可以接受，哪些暂时不能让步？','例如日常任务、培养方式、考核或工作时间。']]
 ];
 const titlePhrases={'work-move':['要不要辞职','换工作？'],'exam-retake':['要不要','二战考研？'],'unpaid-break':['要不要','裸辞休息？'],'city-return':['留在大城市，','还是回老家？'],'independent-home':['要不要','搬出去住？'],'first-job':['第一份工作，','稳定还是成长？']};
 const scenes=rows.map(([id,category,title,desc,name,color,ic,tip,labels,placeholders])=>({id,category,title,titlePhrases:titlePhrases[id]||[title],desc,name,color,ic,tip,short:name,art:'paths',output:'线索、取舍与待查信息',decisionScene:true,fields:labels.map((label,i)=>[['facts','priorities','concerns','unknown'][i],label,placeholders[i]])}));
 for(const x of scenes){D.topics.push(x);V2.schemas[x.id]=x.fields;}
 // Public catalog metadata only; never index answers, observations or profile data.
 const searchMeta={
  'work-move':{directoryDesc:'梳理离职原因、外部机会与空窗准备',icon:'briefcase',keywords:['工作','辞职','机会','收入'],aliases:['辞职','离职','跳槽','换工作']},
  'exam-retake':{directoryDesc:'分清读研意愿、外部期待与投入条件',icon:'book',keywords:['学业','考研','备考'],aliases:['读研','研究生','继续升学','再考一年']},
  'relationship-break':{directoryDesc:'梳理反复犹豫、相处需要与改变空间',icon:'dialogue',keywords:['关系','分手','相处','边界'],aliases:['分开','感情','恋爱']},
  'unpaid-break':{directoryDesc:'梳理休整需要、资金缓冲与回归准备',icon:'sun',keywords:['工作','裸辞','休息','储蓄'],aliases:['离职','辞职','休整','停下来']},
  'city-return':{directoryDesc:'比较机会、成本、归属与家庭支持',icon:'home',keywords:['生活','城市','成本','家庭'],aliases:['回老家','返乡','大城市','换城市']},
  'career-change':{directoryDesc:'梳理能力迁移、信息缺口与低成本尝试',icon:'explore',keywords:['工作','转行','行业','能力'],aliases:['换行业','职业转型','改行']},
  'independent-home':{directoryDesc:'分清空间需要、经济准备与家人期待',icon:'key',keywords:['生活','居住','空间','预算'],aliases:['搬家','租房','独居','独立生活']},
  'first-job':{directoryDesc:'比较收入需要、岗位匹配与成长机会',icon:'leaf',keywords:['工作','收入','成长','岗位'],aliases:['毕业','就业','找工作','应届生']}
 };
 for(const scene of scenes){const meta=searchMeta[scene.id];Object.assign(scene,{ic:meta.icon,directoryDesc:meta.directoryDesc,keywords:meta.keywords,aliases:meta.aliases})}
 const normalize=value=>String(value||'').normalize('NFKC').trim().replace(/\s+/g,' ').toLowerCase();
 function search(query='',category='全部'){
  const q=normalize(query);
  return scenes.map((item,index)=>{const title=normalize(item.title),aliases=item.aliases.map(normalize),keywords=[item.category,...item.keywords].map(normalize);
   const rank=!q?0:title===q||aliases.includes(q)?0:title.includes(q)?1:[...aliases,...keywords].some(word=>word.includes(q))?2:-1;
   return {item,index,rank};
  }).filter(x=>x.rank>=0&&(category==='全部'||x.item.category===category)).sort((a,b)=>a.rank-b.rank||a.index-b.index).map(x=>x.item);
 }
 return {items:scenes,find:id=>scenes.find(x=>x.id===id),search,normalize};
})();
