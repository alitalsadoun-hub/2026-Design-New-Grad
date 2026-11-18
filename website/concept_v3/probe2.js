const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();
 await p.goto('file://'+process.cwd()+'/index.html#en',{waitUntil:'networkidle'});
 await p.tap('#menubtn');await p.waitForTimeout(600);
 console.log(await p.evaluate(()=>{
  const r=s=>{const e=document.querySelector(s);const x=e.getBoundingClientRect();return s+' '+Math.round(x.left)+','+Math.round(x.top)+' '+Math.round(x.width)+'x'+Math.round(x.height)};
  return [r('#mnav'),r('#mnav .top'),r('#mclose'),r('#mnav nav'),'innerWidth '+innerWidth,'docW '+document.documentElement.scrollWidth,'scrollX '+scrollX,'vv '+(visualViewport?visualViewport.width+'@'+visualViewport.scale:''),getComputedStyle(document.querySelector('#mnav')).transform].join('\n')}));
 await b.close();
})();
