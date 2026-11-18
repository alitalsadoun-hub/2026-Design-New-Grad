const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();
 await p.goto('file://'+process.cwd()+'/index.html#en',{waitUntil:'networkidle'});
 console.log(await p.evaluate(()=>{
  const out=[];const W=document.documentElement.clientWidth;
  document.querySelectorAll('body *').forEach(e=>{if(e.closest('.drawer,.mnav,.search,#admin,.toast'))return;const r=e.getBoundingClientRect();if(r.width>0&&r.right>W+2){out.push((e.tagName+'.'+e.className).slice(0,50)+' right='+Math.round(r.right)+' w='+Math.round(r.width))}});
  return 'clientWidth '+W+'\n'+out.slice(0,14).join('\n')}));
 await b.close();
})();
