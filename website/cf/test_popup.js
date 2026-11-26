// Welcome pop-up behaviour (needs the local server + test password). Run after test_api.js
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8788',PW=process.env.PW||'test-password-123',AT=process.env.AT||'testtoken123456';
(async()=>{const b=await chromium.launch();let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
 const lg=await fetch(BASE+'/api/admin/login',{method:'POST',headers:{'content-type':'application/json','x-admin':AT},body:JSON.stringify({password:PW})});const ck=lg.headers.get('set-cookie').split(';')[0];
 const set=o=>fetch(BASE+'/api/admin/settings',{method:'PUT',headers:{'content-type':'application/json',cookie:ck,'x-admin':AT},body:JSON.stringify(o)});
 await set({popupOn:true,popupEnd:'2099-01-01'});
 for(const [label,vp,mobile,hash] of [['desktop EN',{width:1440,height:900},false,'#en'],['mobile AR',{width:390,height:844},true,'#ar']]){
  const c=await b.newContext({viewport:vp,isMobile:mobile,hasTouch:mobile,deviceScaleFactor:2});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto(BASE+'/'+hash,{waitUntil:'networkidle'});await p.waitForSelector('#welcome.on',{timeout:5000}).catch(()=>{});
  A(label+': pop-up appears for a new visitor',await p.evaluate(()=>document.querySelector('#welcome').classList.contains('on')));
  const txt=await p.innerText('#wcard');A(label+': shows the niche price + total with delivery',/(30|٣٠)/.test(txt)&&/(33|٣٣)/.test(txt),txt.replace(/\n/g,' | '));
  A(label+': shows the Selective offer',/Selective|سيلكتف|السيلكتف|Buy 2|اشترِ/i.test(txt));
  await p.screenshot({path:`shots/popup_${label.replace(' ','_')}.png`});
  await p.keyboard.press('Escape');await p.waitForTimeout(300);A(label+': Escape closes it',!(await p.evaluate(()=>document.querySelector('#welcome').classList.contains('on'))));
  await p.reload({waitUntil:'networkidle'});await p.waitForTimeout(2200);A(label+': not shown again the same day',!(await p.evaluate(()=>document.querySelector('#welcome').classList.contains('on'))));
  A(label+': top bar carries the niche offer',/(30|٣٠)/.test(await p.innerText('#ann')));
  A(label+': no JS errors',errs.length===0,errs.join('|'));await c.close()}
 // buttons: filter + scroll
 {const c=await b.newContext({viewport:{width:1280,height:900}});const p=await c.newPage();await p.goto(BASE+'/#en',{waitUntil:'networkidle'});await p.waitForSelector('#welcome.on');
  await p.click('[data-wgo=niche]');await p.waitForTimeout(700);const only=await p.evaluate(()=>[...document.querySelectorAll('#best .card')].length>0&&colV==='niche');A('"Shop niche" closes the pop-up and filters to niche',only&&!(await p.evaluate(()=>document.querySelector('#welcome').classList.contains('on'))));
  const c2=await b.newContext({viewport:{width:1280,height:900}});const p2=await c2.newPage();await p2.goto(BASE+'/#en',{waitUntil:'networkidle'});await p2.waitForSelector('#welcome.on');await p2.click('[data-wgo=selective]');await p2.waitForTimeout(600);A('"Shop selective" filters to selective',await p2.evaluate(()=>colV==='selective'));await c.close();await c2.close()}
 // not on a product page; off; expired
 {const c=await b.newContext({viewport:{width:1280,height:900}});const p=await c.newPage();await p.goto(BASE+'/#p-27',{waitUntil:'networkidle'});await p.waitForTimeout(2200);A('not shown on a direct product link',!(await p.evaluate(()=>document.querySelector('#welcome').classList.contains('on'))));await c.close()}
 await set({popupOn:false});{const c=await b.newContext({viewport:{width:1280,height:900}});const p=await c.newPage();await p.goto(BASE+'/#en',{waitUntil:'networkidle'});await p.waitForTimeout(2200);A('switched off in the dashboard -> never shown',!(await p.evaluate(()=>document.querySelector('#welcome').classList.contains('on')))&&!/until/.test(await p.innerText('#ann')));await c.close()}
 await set({popupOn:true,popupEnd:'2020-01-01'});{const c=await b.newContext({viewport:{width:1280,height:900}});const p=await c.newPage();await p.goto(BASE+'/#en',{waitUntil:'networkidle'});await p.waitForTimeout(2200);A('after the end date -> stops by itself (pop-up and top-bar line)',!(await p.evaluate(()=>document.querySelector('#welcome').classList.contains('on')))&&!/until/.test(await p.innerText('#ann')));await c.close()}
 await set({popupOn:true,popupEnd:'2026-11-30'});
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
