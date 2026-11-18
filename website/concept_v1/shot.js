const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const jobs=[['desk_en',1440,900,false,''],['desk_ar',1440,900,false,'#ar'],['mob_en',390,844,true,''],['mob_ar',390,844,true,'#ar']];
 for(const [n,w,h,m,hash] of jobs){
  const c=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,isMobile:m,hasTouch:m});const p=await c.newPage();
  await p.goto('file://'+process.cwd()+'/index.html'+hash,{waitUntil:'networkidle'});await p.waitForTimeout(1200);
  await p.screenshot({path:'shot_'+n+'.png',fullPage:true});await c.close();}
 await b.close();})();
