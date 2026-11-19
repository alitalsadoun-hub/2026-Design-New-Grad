const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const url='file://'+process.cwd()+'/index.html#en';
 let c=await b.newContext({viewport:{width:1440,height:900}});let p=await c.newPage();
 await p.goto(url,{waitUntil:'networkidle'});
 await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';document.querySelector('#pk').scrollIntoView()});await p.waitForTimeout(500);
 await p.screenshot({path:'of_offers.png'});
 await p.evaluate(()=>document.querySelector('[data-offcol]').click());await p.waitForTimeout(900);
 await p.screenshot({path:'of_shop.png'});
 const ids=await p.evaluate(()=>Object.values(PRODUCTS).filter(x=>x.collection==='selective'&&x.stock>3).slice(0,2).map(x=>x.id));
 await p.evaluate(ids=>{addCart(ids[0]);addCart(ids[1]);document.querySelector('#cartbtn').click()},ids);await p.waitForTimeout(600);
 await p.screenshot({path:'of_cart.png'});
 await p.goto(url.replace('#en','#p-tf105'),{waitUntil:'load'});await p.waitForTimeout(600);
 await p.screenshot({path:'of_tf.png'});
 await b.close();
})();
