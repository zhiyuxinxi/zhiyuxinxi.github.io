/* Review fixtures are opt-in, isolated workbench scenes. They are never personal results. */
window.ProductContext=(()=>{
 const q=new URLSearchParams(location.search),scene=q.get('scenario')||'default';
 let review=false;
 try{review=parent!==window&&q.get('preview')==='1'&&parent.location.origin===location.origin&&!!parent.WorkbenchData;}catch{}
 const fixture=review&&['resume','question','combined','save-failure','complete','mixed-records','topic-record','ongoing-action','action-review','source-login','quota','history','paid-annual','sample-report','profile-sample'].includes(scene);
 return Object.freeze({review,fixture,scene});
})();
