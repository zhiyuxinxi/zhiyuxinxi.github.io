/* Persistent, data-free soft color field. Routes never recreate this canvas.
 * A continuous scalar field changes direction and curvature independently of
 * its 32s area envelope. Histogram quantiles keep both colors present at every
 * aspect ratio; no rotating image, outlined wave, random frame, or SVG shape. */
window.Ambient=(()=>{
 'use strict';
 const layer=document.getElementById('ambient-background'),canvas=document.getElementById('ambient-tide');
 const ctx=canvas.getContext('2d',{alpha:false});
 const preference=matchMedia('(prefers-reduced-motion: reduce)'),contrast=matchMedia('(forced-colors: active)');
 const TAU=Math.PI*2;
 let quiet=false,reduced=false,paused=true,time=0,last=0,frame=0,request=0,manual=false,colors=[],signature='';
 let values,histogram=new Uint32Array(1024),pixels;
 const rgb=h=>h.match(/[a-f\d]{2}/gi).map(n=>parseInt(n,16));
 function palette(){
  const s=getComputedStyle(document.body),next=['--field-a','--field-b'].map(k=>s.getPropertyValue(k).trim());
  if(next.some(value=>!/^#[a-f\d]{6}$/i.test(value)))return;
  if(next.join()!==signature){signature=next.join();colors=next.map(rgb);}
 }
 function resize(){
  canvas.width=144;canvas.height=Math.max(96,Math.min(400,Math.round(144*innerHeight/innerWidth)));
  values=new Float32Array(canvas.width*canvas.height);pixels=ctx.createImageData(canvas.width,canvas.height);const saved=time;if(reduced||preference.matches||contrast.matches)time=0;draw();time=saved;
 }
 function draw(){
  if(!colors.length||!pixels)return;
  const w=canvas.width,h=canvas.height,t=time;
  const angle=.95*Math.sin(TAU*t/53+.3)+1.1*Math.sin(TAU*t/79-.7);
  const dx=Math.cos(angle),dy=Math.sin(angle),area=.5+.34*Math.sin(TAU*t/32);
  let lo=Infinity,hi=-Infinity;
  for(let y=0,i=0;y<h;y++)for(let x=0;x<w;x++,i++){
   const u=x/(w-1)-.5,v=y/(h-1)-.5;
   const f=dx*u+dy*v+.16*Math.sin(3.2*u+2.4*v+TAU*t/47)+.09*Math.cos(2.8*v-2.1*u-TAU*t/61);
   values[i]=f;lo=Math.min(lo,f);hi=Math.max(hi,f);
  }
  histogram.fill(0);const range=hi-lo;
  for(const f of values)histogram[Math.min(1023,Math.floor((f-lo)/range*1023))]++;
  let count=0,bin=0;for(;bin<1023;bin++){count+=histogram[bin];if(count>=area*values.length)break;}
  const threshold=lo+(bin+.5)/1023*range,width=range*.28;
  for(let i=0;i<values.length;i++){
   const p=Math.max(0,Math.min(1,.5+(values[i]-threshold)/width));
   const blend=p*p*(3-2*p);
   for(let k=0;k<3;k++)pixels.data[4*i+k]=Math.round(colors[0][k]*(1-blend)+colors[1][k]*blend);
   pixels.data[4*i+3]=255;
  }
  ctx.putImageData(pixels,0,0);
 }
 function tick(now){
  request=0;if(paused)return;
  if(last)time+=(now-last)/1000;last=now;
  if(now-frame>=50){draw();frame=now;}
  request=requestAnimationFrame(tick);
 }
 function sync(){
  const staticMode=reduced||preference.matches||contrast.matches;
  palette();layer.dataset.quiet=String(quiet);
  layer.dataset.motion=staticMode?'reduced':quiet?'focus':document.hidden?'hidden':manual?'sample':'running';
  paused=staticMode||quiet||document.hidden||manual;
  if(request)cancelAnimationFrame(request);request=0;last=0;
  // Static rendering does not discard the live clock; re-enabling resumes it.
  if(staticMode){const saved=time;time=0;draw();time=saved;}else draw();
  if(!paused)request=requestAnimationFrame(tick);
 }
 preference.addEventListener('change',sync);contrast.addEventListener('change',sync);
 document.addEventListener('visibilitychange',sync);window.addEventListener('resize',resize);
 // Small deterministic inspection API for real-pixel evidence, no persisted data.
 const api={setContext(c){quiet=!!c.quiet;reduced=!!c.reduced;sync();},
  sample(seconds){time=Math.max(0,Number(seconds)||0);manual=true;sync();},
  resume(){manual=false;sync();},getTime(){return time;},isPaused(){return paused;}};
 palette();resize();return api;
})();
