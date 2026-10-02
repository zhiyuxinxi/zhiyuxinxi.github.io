/* One background instance lives outside #app. Rendering a route never rebuilds
 * its SVG, restarts its clock, or changes its color/opacity. No personal data. */
window.Ambient=(()=>{
 'use strict';
 const layer=document.getElementById('ambient-background'),svg=document.getElementById('ambient-tide');
 const preference=matchMedia('(prefers-reduced-motion: reduce)'),contrast=matchMedia('(forced-colors: active)');
 const CYCLE=16,BALANCED=CYCLE/2;
 let started=false,quiet=false,reduced=false,wasReduced=false;
 function sync(){
  const staticMode=reduced||preference.matches||contrast.matches;
  if(!started){svg.pauseAnimations();document.getElementById('tide-motion').beginElement();document.getElementById('tide-direction').beginElement();started=true;}
  layer.dataset.quiet=String(quiet);
  layer.dataset.motion=staticMode?'reduced':quiet?'focus':document.hidden?'hidden':'running';
  if(staticMode){svg.pauseAnimations();if(!wasReduced)svg.setCurrentTime(BALANCED);}
  else if(quiet||document.hidden)svg.pauseAnimations();
  else svg.unpauseAnimations();
  wasReduced=staticMode;
 }
 preference.addEventListener('change',sync);contrast.addEventListener('change',sync);
 document.addEventListener('visibilitychange',sync);
 return {setContext(context){quiet=!!context.quiet;reduced=!!context.reduced;sync();}};
})();
