/* Independent design data. These three original interaction examples are NOT a psychometric test. */
window.D = {
  version:'1.0.0-design',
  report:{id:'report-sample-01',version:'illustration-v1',title:'先想清楚，再慢慢说出来',scope:'独立虚构样例，不来自三题作答'},
  questions:[
    {id:'demo-q1',title:'准备向几位同事分享一个想法，你通常会怎么开始？',options:[['a','先写下几个要点，想清楚再表达'],['b','先找一个人聊聊，让想法慢慢成形'],['c','看当天的情境，再决定怎么准备']]},
    {id:'demo-q2',title:'周末突然空出半天，你更想怎样度过？',options:[['a','留点不被打扰的时间，做自己的事'],['b','约熟悉的人见面，随意走一走'],['c','暂时不安排，到时候再看看']]},
    {id:'demo-q3',title:'一个原本安排好的计划临时改变，你通常会先做什么？',options:[['a','确认哪些条件变了，再调整安排'],['b','先试试新的方向，在过程中调整'],['c','先听听相关的人有什么想法']]}
  ],
  topics:[
    {id:'work-choice',category:'工作',color:'green',art:'paths',title:'留在熟悉的地方，还是试一条新路？',short:'工作选择',desc:'把期待、顾虑和现实条件放在一起看。',output:'一张由你填写的选择清单，而不是“最适合的职业”结论。',prompts:['我正在考虑的两个选择是什么？','我最在意什么？目前有哪些不能忽略的限制？','做决定前，还缺哪一条关键信息？']},
    {id:'relationships',category:'相处',color:'peach',art:'relations',title:'怎样把我的需要，说得更清楚？',short:'表达与相处',desc:'区分发生的事、自己的感受和希望。',output:'一句可以自己修改的表达，不推断另一个人的人格。',prompts:['最近发生了哪一件具体的事？','当时我有什么感受或需要？','我希望向对方提出怎样一个具体请求？']},
    {id:'city-choice',category:'生活',color:'blue',art:'city',title:'换一座城市，也换一种生活？',short:'城市与生活',desc:'先看生活条件，再理解自己的偏好。',output:'你在意的条件与未知，不给城市匹配百分比。',prompts:['我期待新城市带来什么变化？','家庭、工作和预算各有什么约束？','哪一项期待可以先通过短住去验证？']},
    {id:'learning',category:'学习',color:'yellow',art:'learning',title:'我为什么总想继续读书？',short:'学习与动力',desc:'分清自己的期待，与外界的声音。',output:'一份学习动机记录，不测智商或预测录取。',prompts:['我希望学习帮助我改变什么？','这种期待来自自己，还是外界的要求？','下一步最小的一次尝试是什么？']},
    {id:'self-space',category:'生活',color:'green',art:'sprout',title:'独处，是在充电还是躲开？',short:'与自己相处',desc:'看看独处前后发生了什么。',output:'具体情境中的个人观察，不作心理诊断。',prompts:['我在什么时候想一个人待着？','独处之后，我的感受有什么变化？','接下来我需要什么样的支持？']}
  ],
  factors:[
    ['A','乐群',.62,'mint','与人靠近的方式'],['B','推理',null,'blue','处理抽象问题的方式'],['C','情绪稳定',.48,'blue','面对压力时的反应'],['E','支配',.46,'peach','表达主张的方式'],
    ['F','活泼',.54,'yellow','表达活力的方式'],['G','规则意识',.7,'mint','对规则与责任的态度'],['H','社交大胆',.35,'peach','进入陌生社交的方式'],['I','敏感',.64,'blue','感受与判断的侧重'],
    ['L','警觉',.43,'yellow','理解他人意图的方式'],['M','抽象',.58,'blue','想象与现实的关注'],['N','私密',.63,'mint','向别人透露自己的方式'],['O','忧虑',null,'peach','自我担心的倾向'],
    ['Q1','开放变化',.6,'peach','面对新事物的态度'],['Q2','自立',.68,'mint','独立与共同商量的偏好'],['Q3','自律',.61,'blue','组织与安排的方式'],['Q4','紧张',.4,'yellow','内在紧迫的感受']
  ],
  themes:[
    {id:'green',name:'青屿晨光',desc:'青绿 · 杏桃 · 雾蓝',colors:['#dcead7','#d5e1f2','#f5d6c4']},
    {id:'peach',name:'杏桃晚风',desc:'杏桃 · 奶黄 · 淡紫',colors:['#f4cfb8','#e8e4c9','#e4dff1']},
    {id:'blue',name:'海盐晴空',desc:'雾蓝 · 青瓷 · 浅粉',colors:['#d4dcf5','#d6e6e2','#eedbdd']}
  ],
  defaultState(){return {schema:1,theme:'green',reduced:false,fontSize:'normal',avatar:1,name:'此刻的你',mode:'original',sessions:[],activeSession:null,reportNotes:[],observations:[],actions:[],memories:[],conversations:[],assistantDraft:'',assistantSources:[],logged:false,used:0,usage:[],usageDay:new Date().toLocaleDateString('en-CA'),favorites:[],exploreCategory:'全部',exploreSearch:'',recordFilter:'全部',plan:'annual',orders:[],chatRetention:true,memoryEnabled:false,returnAfterAuth:'assistant',reportContext:'work'};},
  reportSource(section='work'){
    const rel=section==='relationship';
    return {id:'source-'+section,kind:'sample-report',objectId:'report-sample-01',version:'illustration-v1',sectionId:section,title:'独立报告样例 · '+(rel?'相处情境':'工作情境'),excerpt:rel?'小林和熟悉的朋友在一起时很放松；多人聚会里，常常先听一会儿，再加入话题。':'小林在会前列好三个要点时，表达比较清楚；临时被问到一个新问题时，会希望先有一点整理时间。',status:'valid',scope:'仅本次引用；不自动成为长期记忆'};
  }
};
