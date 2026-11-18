const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const url='file://'+process.cwd()+'/index.html';
 let c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});let p=await c.newPage();
 await p.goto(url+'#en',{waitUntil:'networkidle'});
 await p.tap('#menubtn');await p.waitForTimeout(600);await p.screenshot({path:'ux_menu.png'});
 await p.tap('#mclose');await p.waitForTimeout(400);
 await p.tap('#searchbtn');await p.fill('#sin','vanilla');await p.waitForTimeout(400);await p.screenshot({path:'ux_search.png'});
 await p.keyboard.press('Escape');await p.waitForTimeout(300);
 // finder shortcut
 await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';document.querySelector('#finder').scrollIntoView()});
 await p.evaluate(()=>{document.querySelector('.nt:nth-child(4)').click();document.querySelector('.nt:nth-child(5)').click()});
 await p.evaluate(()=>window.scrollBy(0,330));await p.waitForTimeout(500);await p.screenshot({path:'ux_fab.png'});
 // add-to-cart feedback on a product page
 await p.goto(url+'#p-9',{waitUntil:'load'});await p.waitForTimeout(400);
 await p.evaluate(()=>document.querySelector('#sadd').click());await p.waitForTimeout(500);await p.screenshot({path:'ux_added.png'});
 // sold-out + low-stock cards on desktop catalogue
 await c.close();
 c=await b.newContext({viewport:{width:1440,height:900}});p=await c.newPage();
 await p.goto(url,{waitUntil:'networkidle'});
 await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';document.querySelector('#shop').scrollIntoView()});
 await p.waitForTimeout(600);
 await p.evaluate(()=>{for(let i=0;i<4;i++)window.scrollBy(0,1)});
 await p.screenshot({path:'ux_cards.png',clip:{x:0,y:0,width:1440,height:900}});
 await b.close();
})();
