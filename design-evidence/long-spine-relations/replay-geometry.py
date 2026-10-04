from pathlib import Path
import json,math
p=Path(__file__).resolve().parent;m=json.loads((p/'geometry-model.json').read_text());es=m['edges']
def pt(q,t):return [(1-t)**3*q[0][i]+3*(1-t)**2*t*q[1][i]+3*(1-t)*t*t*q[2][i]+t**3*q[3][i] for i in [0,1]]
def cross(a,b,c,d):
 if max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]) or max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1]):return None
 ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-c[0],d[1]-c[1];den=ux*vy-uy*vx
 if abs(den)<1e-10:return None
 wx,wy=c[0]-a[0],c[1]-a[1];t=(wx*vy-wy*vx)/den;u=(wx*uy-wy*ux)/den
 return [a[0]+t*ux,a[1]+t*uy] if 0<t<1 and 0<u<1 else None
samples={e['id']:[pt(e['q'],i/200) for i in range(201)] for e in es};hits=[];joins=[]
for i,e in enumerate(es):
 for f in es[i+1:]:
  common=[a for a in [e['q'][0],e['q'][3]] for b in [f['q'][0],f['q'][3]] if math.dist(a,b)<1e-8]
  common += [j['p'] for j in m['junctions'] if e['id'] in j['edges'] and f['id'] in j['edges']]
  for a,b in zip(samples[e['id']],samples[e['id']][1:]):
   for c,d in zip(samples[f['id']],samples[f['id']][1:]):
    v=cross(a,b,c,d)
    if v:
     if any(math.dist(v,x)<.05 for x in common):joins.append([e['id'],f['id'],v])
     else:hits.append([e['id'],f['id'],v])
r={'segments':len(es),'samplingPerCurve':200,'crossings':hits,'declaredJunctionContacts':len(joins),'junctionToleranceWorldUnits':.05};(p/'geometry.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
