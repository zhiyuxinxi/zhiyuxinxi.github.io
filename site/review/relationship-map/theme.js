// Read the generated CSS's theme names, keeping theme token ownership in the app.
const names=[...document.styleSheets].flatMap(sheet=>{try{return [...sheet.cssRules].map(r=>r.selectorText||'');}catch{return [];}}).filter(s=>s.startsWith('body.theme-')).map(s=>s.slice(11));
const requested=new URLSearchParams(location.search).get('theme');const chosen=names.includes(requested)?requested:'sunrise';
document.body.classList.add('theme-'+chosen);document.body.dataset.theme=chosen;document.body.dataset.themeMode=['nebula','amber'].includes(chosen)?'dark':'light';
