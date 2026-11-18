const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const url='file://'+process.cwd()+'/index.html';
 const c=await b.newContext({viewport:{width:1440,height:900}});const p=await c.newPage();
 await p.goto(url+'#en',{waitUntil:'networkidle'});
 await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';document.querySelector('#shop').scrollIntoView()});
 await p.evaluate(()=>document.querySelector('#filters button[data-c=selective]').click());
 await p.waitForTimeout(700);
 await p.evaluate(()=>window.scrollBy(0,-20));
 await p.screenshot({path:'ux3_shop.png'});
 await p.evaluate(()=>{document.querySelector('#finder').scrollIntoView();});
 await p.evaluate(()=>{['sweet','spicy','oud'].forEach(id=>document.querySelector('.nt[data-f='+id+']').click())});
 await p.waitForTimeout(500);await p.screenshot({path:'ux3_finder.png'});
 // a selective product page with notes
 const id='73';
 await p.goto(url+'#p-'+id,{waitUntil:'load'});await p.waitForTimeout(500);
 await p.screenshot({path:'ux3_pdp.png'});
 await b.close();
})();
