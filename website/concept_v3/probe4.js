const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();
 await p.goto('file://'+process.cwd()+'/index.html#en',{waitUntil:'networkidle'});
 console.log(await p.evaluate(()=>{const o=[];const W=390;document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);if(r.width>0&&r.right>W+1&&!e.closest('.drawer,.mnav,.scrim')&&cs.position!=='fixed')o.push((e.tagName+'.'+e.className).slice(0,40)+' right='+Math.round(r.right)+' pos='+cs.position+' in='+(e.closest('.drawer')?'drawer':e.closest('.mnav')?'mnav':e.closest('.toast')?'toast':e.closest('#admin')?'admin':e.closest('.search')?'search':'-'))});return 'docW '+document.documentElement.scrollWidth+'\n'+o.slice(0,12).join('\n')}));
 await b.close()})();
