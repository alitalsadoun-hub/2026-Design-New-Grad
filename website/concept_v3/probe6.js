const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();
 await p.goto('file://'+process.cwd()+'/index.html#en',{waitUntil:'networkidle'});
 console.log(await p.evaluate(()=>{const o=[];document.querySelectorAll('#shop *').forEach(e=>{if(e.scrollWidth>e.clientWidth+1&&e.clientWidth>0)o.push((e.tagName+'.'+e.className).slice(0,30)+' sw='+e.scrollWidth+' cw='+e.clientWidth+' txt='+(e.innerText||'').slice(0,30).replace(/\n/g,' '))});
  const g=document.querySelector('#best'),r=g.getBoundingClientRect();return 'best '+Math.round(r.left)+'-'+Math.round(r.right)+' cols '+getComputedStyle(g).gridTemplateColumns+'\n'+o.join('\n')}));
 await b.close()})();
