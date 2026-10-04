/* Stable, data-driven radial tree. No random state, SVG masks, or decorative branches. */
window.TreeGeometry = (() => {
  const TAU = Math.PI * 2;
  const delta = a => Math.atan2(Math.sin(a), Math.cos(a));
  const polar = (r, a) => [r * Math.cos(a), r * Math.sin(a)];
  const point = (q, t) => {const u=1-t;return [0,1].map(i=>u*u*u*q[0][i]+3*u*u*t*q[1][i]+3*u*t*t*q[2][i]+t*t*t*q[3][i]);};
  function build(roots) {
    const nodes=[],edges=[];
    const rhythm=[1.05,.82,1.25,.92,1.13,.8,.98,1.16,.88,1.07,.94,1.2],weights=roots.map((_,i)=>rhythm[i%rhythm.length]),total=weights.reduce((a,b)=>a+b,0);let cursor=0;
    const angles=roots.map((n,i)=>{const angle=n.anchor?Math.atan2(n.anchor[1]-230,n.anchor[0]-195):-Math.PI/2+cursor/total*TAU;cursor+=weights[i];return angle});
    // Art-directed handles: radial fractions and signed fractions of each available sector.
    const poses={risk:[.34,.90,.78,.35],time:[.42,.90,.83,-.72],emotion:[.40,-.35,.82,.12],space:[.55,-.82,.87,.60],commitment:[.30,.45,.82,.92],planning:[.54,-.95,.84,-.40],growth:[.36,.92,.80,-.85],money:[.60,-.96,.84,.78]};
    const fallback=Object.values(poses);
    const root={id:'root',name:'我',depth:0,p:[0,0],radius:0,angle:0,children:roots.map(n=>n.id),kind:'root'};nodes.push(root);
    function visit(source,parent,angle,lo,hi,rootId,depth,radius){
      const n={...source,parent:parent.id,rootId,depth,angle,lo,hi,radius,p:polar(radius,angle),children:(source.children||[]).map(c=>c.id)};nodes.push(n);
      let q;
      if(depth===1){const index=roots.findIndex(r=>r.id===source.id),pose=poses[source.id]||fallback[index%fallback.length],offset=value=>value<0?value*(angle-lo):value*(hi-angle);q=[[0,0],polar(radius*pose[0],angle+offset(pose[1])),polar(radius*pose[2],angle+offset(pose[3])),n.p];}
      else{const dr=radius-parent.radius,da=delta(angle-parent.angle),r1=parent.radius+dr*.30,r2=parent.radius+dr*.73;
        // A single-child chain gets a stable, bounded S; sibling fans retain their ordered controls.
        const single=parent.children.length===1,margin=Math.max(0,Math.min(angle-lo,hi-angle)),sign=[...source.id].reduce((h,c)=>h+c.charCodeAt(0),0)%2?1:-1;
        const bend=single?sign*Math.min(margin*.28,Math.atan2(28,r2)):0;
        q=[parent.p,polar(r1,parent.angle+da*.05+bend),polar(r2,parent.angle+da*.45-bend*.8),n.p];}
      edges.push({id:parent.id+'>'+n.id,parent:parent.id,child:n.id,rootId,depth,q});
      const children=source.children||[],span=hi-lo;
      children.forEach((child,i)=>{const a=children.length===1?angle:lo+span*(i+.5)/children.length;visit(child,n,a,lo+span*i/children.length,lo+span*(i+1)/children.length,rootId,depth+1,radius+155);});
    }
    roots.forEach((n,i)=>{const a=angles[i];let left=Math.PI,right=Math.PI;angles.forEach((b,j)=>{if(i===j)return;const d=delta(b-a);if(d<0)left=Math.min(left,-d);else right=Math.min(right,d)});const radius=n.anchor?Math.hypot(n.anchor[0]-195,n.anchor[1]-230):[164,190,146,178,155,197,172,182,151,188,167,177][i%12];visit(n,root,a,a-left*.43,a+right*.43,n.id,1,radius);});
    return {nodes,edges};
  }
  function split(q,t){const mix=(a,b)=>a.map((v,i)=>v+(b[i]-v)*t),a=mix(q[0],q[1]),b=mix(q[1],q[2]),c=mix(q[2],q[3]),d=mix(a,b),e=mix(b,c),f=mix(d,e);return [[q[0],a,d,f],[f,e,c,q[3]]];}
  function trim(q,start,end){let a=0,b=1;for(let i=0;i<=100;i++){const t=i/100,p=point(q,t);if(Math.hypot(p[0]-q[0][0],p[1]-q[0][1])<start)a=t;if(Math.hypot(p[0]-q[3][0],p[1]-q[3][1])>=end)b=t;}if(a>=b)return null;const left=split(q,b)[0];return split(left,a/b)[1];}
  return {build,point,trim,delta,path:q=>`M${q[0]} C${q[1]} ${q[2]} ${q[3]}`};
})();
