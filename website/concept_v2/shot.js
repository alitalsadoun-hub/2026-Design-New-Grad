const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
 const jobs=process.argv.slice(2).map(a=>a.split(':'));
 for(const [name,hash,w,h,full] of jobs){const m=+w<600;
  const c=await b.newContext({viewport:{width:+w,height:+h},deviceScaleFactor:1,isMobile:m,hasTouch:m});const p=await c.newPage();
  p.on('pageerror',e=>console.log('PAGEERR',name,e.message));
  await p.goto('file://'+process.cwd()+'/index.html#'+hash,{waitUntil:'networkidle'});await p.waitForTimeout(1200);
  await p.screenshot({path:'shot_'+name+'.png',fullPage:full==='1'});await c.close();}
 await b.close();})();
