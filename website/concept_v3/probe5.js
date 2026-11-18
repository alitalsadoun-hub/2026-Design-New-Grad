const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();
 await p.goto('file://'+process.cwd()+'/index.html#en',{waitUntil:'networkidle'});
 console.log(await p.evaluate(()=>{const out=[];const kids=[...document.querySelectorAll('body > *, #home > *, #main > *, #store > *, #shop *')];
  const base=document.documentElement.scrollWidth;out.push('base '+base);
  kids.forEach(k=>{const d=k.style.display;k.style.display='none';const w=document.documentElement.scrollWidth;k.style.display=d;if(w!==base)out.push((k.tagName+'#'+k.id+'.'+k.className).slice(0,40)+' -> '+w)});return out.join('\n')}));
 await b.close()})();
