/* Explicit semantic nodes; geometric bend counts never create business levels. */
window.MapSemantics=(()=>{
 const art=RelationshipArt,research=MapModel.type==='structure',nodes=[{id:'root',parent:null,type:'root',label:research?'根':'我',depth:0,branch:null}],by=new Map(),pairs=[];
 by.set('root',nodes[0]);
 const add=n=>{if(by.has(n.id)||!by.has(n.parent))throw new Error('Invalid semantic parent or duplicate node: '+n.id);n.depth=by.get(n.parent).depth+1;nodes.push(n);by.set(n.id,n);return n;};
 for(const b of art.branches){
  if(research){
   for(const s of b.nodeSpecs){const n=add({...s,branch:b.id});const path=b.paths[s.path];path.semanticNode=n;}
   for(const it of b.items){it.semanticNode=by.get(it.nodeId);it.semanticNode.item=it;}
  }else{
   const topic=add({id:b.id,parent:'root',type:'topic',label:b.name,branch:b.id});
   for(const p of b.paths)p.semanticNode=topic;
   for(const it of b.items){const n=add({id:it.id,parent:b.id,type:'terminal',label:it.t,branch:b.id});it.semanticNode=n;n.item=it;if(it.path)it.path.semanticNode=n;}
  }
 }
 for(const n of nodes){n.children=nodes.filter(x=>x.parent===n.id).map(x=>x.id);n.clickable=n.type==='terminal'||n.type==='topic';if(n.type==='terminal'&&n.children.length)throw new Error('Terminal has children');}
 const svg=document.getElementById('gItems'),NS='http://www.w3.org/2000/svg';
 for(const n of nodes.filter(n=>n.type==='intermediate')){
  const g=document.createElementNS(NS,'g');g.classList.add('semantic-joint');g.dataset.node=n.id;g.dataset.depth=n.depth;g.setAttribute('role','img');g.setAttribute('aria-label',n.label+'，第'+n.depth+'层，中间节点');
  const circle=document.createElementNS(NS,'circle');circle.setAttribute('cx',n.point[0]);circle.setAttribute('cy',n.point[1]);circle.setAttribute('r','2.5');
  const label=document.createElementNS(NS,'text');label.setAttribute('x',n.point[0]+7);label.setAttribute('y',n.point[1]+4);label.textContent=n.label;
  g.append(circle,label);svg.append(g);n.element=g;
 }
 if(research){
  document.getElementById('wo').textContent='根';document.querySelector('#orb').setAttribute('aria-label','根：返回全图');
  document.querySelector('.detail-note').textContent='中性结构示例。层级、分枝与状态只用于验证通用显示能力，不属于心理测量结果。';
  pairs.push({id:'pair-1',members:['pair-a','pair-b'],exclusive:false,normalized:false});
  for(const id of pairs[0].members)by.get(id).state='present';
 }
 function stateLabel(n){return n.state==='present'?'有示例记录':'未知';}
 function renderStates(){for(const n of nodes.filter(n=>n.pair)){const it=n.item;it.tx.textContent=n.label+' · '+stateLabel(n);it.g.dataset.evidence=n.state;it.hit.setAttribute('aria-label',n.label+'，'+stateLabel(n)+'：查看详情');}}
 function setState(id,value){const n=by.get(id);if(!research||!n?.pair||!['present','unknown'].includes(value))return false;n.state=value;renderStates();return true;}
 function snapshot(){return {research,nodes:nodes.map(({item,element,...n})=>({...n,point:n.point?.slice(),children:n.children.slice()})),pairs:pairs.map(p=>({...p,members:p.members.slice()}))};}
 renderStates();return {research,nodes,by,pairs,setState,snapshot,stateLabel};
})();
