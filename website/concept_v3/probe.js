const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const url='file://'+process.cwd()+'/index.html';
 // desktop: search + Esc on cart
 let c=await b.newContext({viewport:{width:1440,height:900}});let p=await c.newPage();
 await p.goto(url,{waitUntil:'load'});
 await p.click('#searchbtn');await p.waitForTimeout(300);
 console.log('desktop: search opens:',await p.evaluate(()=>document.querySelector('#search').classList.contains('on')));
 await p.fill('#sin','vanilla');await p.waitForTimeout(200);
 console.log('search "vanilla" results:',await p.evaluate(()=>document.querySelectorAll('#sres a').length));
 await p.keyboard.press('Escape');await p.waitForTimeout(200);
 console.log('Esc closes search:',!(await p.evaluate(()=>document.querySelector('#search').classList.contains('on'))));
 await p.click('#cartbtn');await p.waitForTimeout(400);
 console.log('cart opens:',await p.evaluate(()=>document.querySelector('#drawer').classList.contains('on')),'| focus in drawer:',await p.evaluate(()=>document.activeElement.id));
 await p.keyboard.press('Escape');await p.waitForTimeout(400);
 console.log('Esc closes cart:',!(await p.evaluate(()=>document.querySelector('#drawer').classList.contains('on'))));
 console.log('unlabelled buttons/links:',await p.evaluate(()=>[...document.querySelectorAll('button,a')].filter(e=>e.getBoundingClientRect().width>0&&!(e.innerText||'').trim()&&!e.getAttribute('aria-label')).map(e=>e.outerHTML.slice(0,90))));
 await c.close();
 // mobile: menu
 c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});p=await c.newPage();
 await p.goto(url,{waitUntil:'load'});
 await p.tap('#menubtn');await p.waitForTimeout(500);
 console.log('mobile: menu opens:',await p.evaluate(()=>document.querySelector('#mnav').classList.contains('on')));
 await p.tap('#mnav nav a:nth-child(2)');await p.waitForTimeout(500);
 console.log('menu closes after choosing:',!(await p.evaluate(()=>document.querySelector('#mnav').classList.contains('on'))),'| scrolled to shop:',await p.evaluate(()=>scrollY>500));
 await c.close();await b.close();
})();
