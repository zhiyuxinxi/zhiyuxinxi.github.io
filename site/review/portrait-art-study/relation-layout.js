/* Hand-composed relationship spines. Nodes/children retain their domain identities. */
window.RelationArt = (() => {
 const plans={
  risk:{root:[[0,0],[-24,-58],[-151,-69],[-107,-169]],stem:[[-107,-169],[-90,-210],[-164,-216],[-146,-267]],tips:[[-70,-210],[-160,-189],[-94,-255],[-170,-284]],t:[.16,.39,.64,.87]},
  time:{root:[[0,0],[48,-97],[-63,-104],[-9,-205]],stem:[[-9,-205],[32,-266],[-48,-274],[-29,-314]],tips:[[41,-246],[-45,-259],[13,-307],[-65,-320]],t:[.18,.42,.68,.90]},
  emotion:{root:[[0,0],[88,-61],[32,-119],[103,-188]],stem:[[103,-188],[137,-222],[88,-280],[142,-299]],tips:[[156,-194],[78,-243],[165,-262],[96,-321]],t:[.16,.38,.65,.86]},
  space:{root:[[0,0],[85,-10],[142,62],[112,-54]],stem:[[112,-54],[73,-140],[174,-144],[156,-18]],tips:[[92,-135],[146,-142],[169,-107],[184,-31]],t:[.17,.40,.63,.83]},
  commitment:{root:[[0,0],[72,41],[143,73],[121,153]],stem:[[121,153],[95,214],[177,224],[139,288]],tips:[[163,176],[93,239],[175,244],[111,284]],t:[.18,.40,.64,.85]},
  planning:{root:[[0,0],[20,86],[-55,141],[16,208]],stem:[[16,208],[101,279],[-7,319],[81,333]],tips:[[78,219],[1,284],[22,341],[111,322]],t:[.16,.40,.66,.86]},
  growth:{root:[[0,0],[-60,69],[-28,156],[-86,191]],stem:[[-86,191],[-149,229],[-109,285],[-153,312]],tips:[[-157,199],[-76,244],[-168,269],[-113,322]],t:[.18,.40,.65,.87]},
  money:{root:[[0,0],[-57,27],[-157,-82],[-142,-28]],stem:[[-142,-28],[-116,35],[-167,109],[-108,135]],tips:[[-172,16],[-97,61],[-169,106],[-89,113]],t:[.15,.40,.64,.87]}
 };
 function build(roots){
  const model=TreeGeometry.build(roots),byId=Object.fromEntries(model.nodes.map(n=>[n.id,n]));model.edges=[];model.composition='long-spines';model.junctions=[];
  const place=(n,p)=>{n.p=p;n.angle=Math.atan2(p[1],p[0]);n.radius=Math.hypot(...p)};
  for(const source of roots){const art=plans[source.id],n=byId[source.id];place(n,art.root[3]);n.labelP=({risk:[-65,-125],money:[-142,-69],emotion:[31,-165],commitment:[65,112],space:[139,48]})[n.id];
   model.edges.push({id:'root>'+n.id,parent:'root',child:n.id,rootId:n.id,depth:1,q:art.root,role:'main',uv:[0,.52],artWidth:[9,5.5],trim:[31,18]});
   model.edges.push({id:n.id+':carrier',parent:n.id,child:n.id,rootId:n.id,depth:1,q:art.stem,role:'carrier',uv:[.52,1],artWidth:[5.5,1.5],trim:[18,0]});
   n.children.forEach((id,i)=>{const leaf=byId[id],t=art.t[i],start=TreeGeometry.point(art.stem,t),ahead=TreeGeometry.point(art.stem,t+.002),dx=ahead[0]-start[0],dy=ahead[1]-start[1],norm=Math.hypot(dx,dy),end=art.tips[i],length=Math.hypot(end[0]-start[0],end[1]-start[1]);place(leaf,end);
    const q=[start,[start[0]+dx/norm*length*.32,start[1]+dy/norm*length*.32],[end[0]-(end[0]-start[0])*.18,end[1]-(end[1]-start[1])*.18],end];
    model.edges.push({id:n.id+'>'+id,parent:n.id,child:id,rootId:n.id,depth:2,q,role:'side-shoot',junction:n.id+':tap'+i});model.junctions.push({id:n.id+':tap'+i,p:start,edges:[n.id+':carrier',n.id+'>'+id]});
   });
  }
  return model;
 }
 return {build};
})();
