/* Read-only graph content. Every layout keeps its own hand-authored curves. */
window.MapModel=(()=>{
 const type=new URLSearchParams(location.search).get('map')||'relationships';
 const titles={relationships:'关系需求图谱',traits:'人格倾向',personal:'我的观察',completion:'认识的进度'};
 const areas=[['behavior','性格与行为'],['decisions','思考与选择'],['values','在意的事'],['assumptions','待检验的想法'],['emotions','情感与需要'],['family','家庭与边界'],['communication','沟通与互动'],['strengths','优势与代价']];
 const clone=b=>JSON.parse(JSON.stringify(b));
 function replace(b,name,items,curves){b.name=name;b.items=items;b.vines=curves;b.buds=[];b.juncs=[];b.iconPath=0;return b;}
 const item=(id,t,sub,x,y)=>({id,t,sub,b:[x,y],x:[x+16,x+88],cy:y,kind:'explanation'});
 const path=(pts,i,parent=0)=>({pts,item:i,parent,w:[1.15,.65]});
 function configure(rows){
  if(type==='traits'){
   // Letter ranges index the maintained factors, not invented higher-order dimensions.
   const designs=[
    {base:'risk',name:'A — E',leaves:[[190,70],[214,110],[236,150],[250,195]],curves:[[[110,107],[136,85],[168,65],[190,70]],[[137,160],[162,142],[190,122],[214,110]],[[173,183],[190,171],[217,157],[236,150]],[[220,195],[233,192],[243,192],[250,195]]]},
    {base:'emo',name:'F — I',leaves:[[459,105],[454,145],[462,184],[449,222]],curves:[[[425,122],[437,117],[448,108],[459,105]],[[418,153],[431,147],[444,144],[454,145]],[[401,183],[421,185],[443,185],[462,184]],[[361,213],[387,211],[419,216],[449,222]]]},
    {base:'promise',name:'L — O',leaves:[[437,375],[470,411],[493,451],[508,493]],curves:[[[368,358],[391,360],[416,369],[437,375]],[[410,390],[432,395],[451,403],[470,411]],[[427,433],[448,444],[472,449],[493,451]],[[448,463],[468,482],[489,492],[508,493]]]},
    {base:'grow',name:'Q1 — Q4',leaves:[[96,407],[112,451],[145,487],[192,516]],curves:[[[92,399],[93,403],[96,407]],[[97,463],[101,451],[112,451]],[[137,501],[140,491],[145,487]],[[197,496],[200,507],[192,516]]]}
   ];
   return designs.map((d,g)=>{const b=clone(rows.find(b=>b.id===d.base));b.id='factors-'+g;b.anchorRatio=g===2?.43:1;const main={...b.vines[0],item:undefined,deco:true};return replace(b,d.name,D.factors.slice(g*4,g*4+4).map((f,i)=>({...item(f[0],f[0]+' '+f[1],f[4]+'。具体读数以已保存的有效测评结果为准。',...d.leaves[i]),route:'factor-detail',routeId:f[0],kind:'factor'})),[main,...d.curves.map((c,i)=>path(c,i))]);});
  }
  if(type==='personal'){
   // Eight observation areas on three uneven, hand-laid climbing stems. No psychological score.
   const designs=[
    {base:'risk',name:'经历与选择',main:[[281,252],[260,230],[249,192],[248,156],[237,124],[215,105],[188,99],[166,105]],leaves:[[130,175],[170,220],[215,259]],curves:[[[177.832838,100.862804],[160,127],[145,152],[130,175]],[[248,156],[219,167],[190,193],[170,220]],[[260,230],[243,237],[226,250],[215,259]]],ids:[0,1,2]},
    {base:'emo',name:'感受与相处',main:[[327,271],[355,251],[370,222],[379,186],[400,151],[430,130],[454,122]],leaves:[[461,159],[451,204],[436,248]],curves:[[[430,130],[445,138],[455,149],[461,159]],[[379,186],[405,189],[433,197],[451,204]],[[355,251],[382,243],[409,243],[436,248]]],ids:[4,5,6]},
    {base:'grow',name:'继续理解',main:[[282,316],[276,350],[281,387],[269,426],[243,455],[209,474],[172,480]],leaves:[[181,440],[255,489]],curves:[[[243,455],[225,440],[204,434],[181,440]],[[209,474],[226,485],[243,490],[255,489]]],ids:[3,7]}
   ];
   return designs.map(d=>{const b=clone(rows.find(b=>b.id===d.base));b.id=d.name;b.anchorRatio=1;return replace(b,d.name,d.ids.map((a,i)=>({...item(areas[a][0],areas[a][1],'从具体经历看这个角度。没有记录时保持留白，不替你下结论。',...d.leaves[i]),route:'observation-area',routeId:areas[a][0],kind:'observation'})),[{pts:d.main,w:[2.5,1.1],deco:true},...d.curves.map((c,i)=>path(c,i))]);});
  }
  if(type==='completion'){
   const a=clone(rows.find(b=>b.id==='time')),b=clone(rows.find(b=>b.id==='grow')),c=clone(rows.find(b=>b.id==='free'));
   a.id='answers';b.id='observations';c.id='review';a.anchorRatio=b.anchorRatio=c.anchorRatio=1;
   replace(a,'作答',[
    {...item('answers','已保存的回答','作答进度只按真实已保存的回答统计，不代表人格特征。',329,101),route:'home'},
    {...item('unanswered','尚未回答','未作答的题目保持未知；不以零分填补。',353,150),route:'home'}
   ],[{pts:[[297,243],[292,218],[298,186],[300,153],[290,121],[270,97],[251,85]],w:[2.6,1],deco:true},path([[300,153],[311,134],[319,113],[329,101]],0),path([[298,186],[318,174],[339,160],[353,150]],1)]);
   replace(b,'本人观察',[{...item('notes','具体经历','观察记录属于本人补充，不自动变成测量读数。',155,450),route:'records'}],[{pts:[[264,300],[233,310],[201,331],[182,364],[182,394],[195,420]],w:[2.4,1],deco:true},path([[182,394],[168,410],[157,431],[155,450]],0)]);
   replace(c,'回看与修正',[{...item('review','已有结果','只有具备明确测量依据的有效结果才进入画像；未知不填零。',452,360),route:'records'},{...item('changes','改变理解','回看不同情境中的经历，允许保留不同认识。',428,414),route:'records'}],[{pts:[[328,307],[350,325],[373,350],[381,378],[384,407],[399,432]],w:[2.5,1],deco:true},path([[350,325],[389,333],[423,351],[452,360]],0),path([[381,378],[397,393],[413,407],[428,414]],1)]);
   return [a,b,c];
  }
  return rows;
 }
 function topology(art){
  // Parent identity is explicit after geometry resolution. It never comes from a visual score.
  return art.branches.map(b=>({id:b.id,kind:'fixed',coexistence:'independent',paths:b.paths.map(p=>({id:b.id+':p'+p.vi,parent:p.parent?b.id+':p'+p.parent.vi:b.id,clickable:false})),terminals:b.items.map(it=>({id:it.id,parent:b.id+':p'+it.path.vi,meaning:it.t,kind:it.kind||'fixed',clickable:true}))}));
 }
 return {type:Object.hasOwn(titles,type)?type:'relationships',title:titles[type]||titles.relationships,configure,topology};
})();
