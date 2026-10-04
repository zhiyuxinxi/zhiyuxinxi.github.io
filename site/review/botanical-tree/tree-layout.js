/* Stable, data-driven radial tree. No random state, SVG masks, or decorative branches. */
window.TreeGeometry = (() => {
  const TAU = Math.PI * 2;
  const delta = a => Math.atan2(Math.sin(a), Math.cos(a));
  const polar = (r, a) => [r * Math.cos(a), r * Math.sin(a)];
  const point = (q, t) => {const u=1-t;return [0,1].map(i=>u*u*u*q[0][i]+3*u*u*t*q[1][i]+3*u*t*t*q[2][i]+t*t*t*q[3][i]);};
  function build(roots) {
    const nodes=[],edges=[];
    const angles=roots.map((n,i)=>n.anchor?Math.atan2(n.anchor[1]-230,n.anchor[0]-195):-Math.PI/2+i*TAU/roots.length);
    const root={id:'root',name:'我',depth:0,p:[0,0],radius:0,angle:0,children:roots.map(n=>n.id),kind:'root'};nodes.push(root);
    function visit(source,parent,angle,lo,hi,rootId,depth,radius){
      const n={...source,parent:parent.id,rootId,depth,angle,lo,hi,radius,p:polar(radius,angle),children:(source.children||[]).map(c=>c.id)};nodes.push(n);
      let q;
      if(depth===1){const bend=Math.min(angle-lo,hi-angle)*.76*(roots.findIndex(r=>r.id===source.id)%2?1:-1);q=[[0,0],polar(radius*.31,angle+bend),polar(radius*.73,angle+bend*.48),n.p];}
      else{const dr=radius-parent.radius,da=delta(angle-parent.angle);q=[parent.p,polar(parent.radius+dr*.30,parent.angle+da*.18),polar(parent.radius+dr*.73,parent.angle+da*.80),n.p];}
      edges.push({id:parent.id+'>'+n.id,parent:parent.id,child:n.id,rootId,depth,q});
      const children=source.children||[],span=hi-lo;
      children.forEach((child,i)=>{const a=children.length===1?angle:lo+span*(i+.5)/children.length;visit(child,n,a,lo+span*i/children.length,lo+span*(i+1)/children.length,rootId,depth+1,radius+155);});
    }
    roots.forEach((n,i)=>{const a=angles[i];let left=Math.PI,right=Math.PI;angles.forEach((b,j)=>{if(i===j)return;const d=delta(b-a);if(d<0)left=Math.min(left,-d);else right=Math.min(right,d)});const radius=n.anchor?Math.hypot(n.anchor[0]-195,n.anchor[1]-230):160+(i%3-1)*5;visit(n,root,a,a-left*.43,a+right*.43,n.id,1,radius);});
    return {nodes,edges};
  }
  function split(q,t){const mix=(a,b)=>a.map((v,i)=>v+(b[i]-v)*t),a=mix(q[0],q[1]),b=mix(q[1],q[2]),c=mix(q[2],q[3]),d=mix(a,b),e=mix(b,c),f=mix(d,e);return [[q[0],a,d,f],[f,e,c,q[3]]];}
  function trim(q,start,end){let a=0,b=1;for(let i=0;i<=100;i++){const t=i/100,p=point(q,t);if(Math.hypot(p[0]-q[0][0],p[1]-q[0][1])<start)a=t;if(Math.hypot(p[0]-q[3][0],p[1]-q[3][1])>=end)b=t;}if(a>=b)return null;const left=split(q,b)[0];return split(left,a/b)[1];}
  return {build,point,trim,delta,path:q=>`M${q[0]} C${q[1]} ${q[2]} ${q[3]}`};
})();
