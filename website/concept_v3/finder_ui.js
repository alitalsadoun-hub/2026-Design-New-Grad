const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();let fail=0;const A=(n,c)=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n)};
 const url='file://'+process.cwd()+'/index.html';
 for(const [label,vp,mobile,hash] of [['desktop EN',{width:1440,height:900},false,'#en'],['mobile AR',{width:390,height:844},true,'#ar']]){
  const c=await b.newContext({viewport:vp,isMobile:mobile,hasTouch:mobile});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto(url+hash,{waitUntil:'networkidle'});
  const click=async s=>p.evaluate(s=>document.querySelector(s).click(),s);
  const names=()=>p.evaluate(()=>[...document.querySelectorAll('#results .res h3')].map(e=>e.innerText));
  A(label+': before any pick, an invitation (not results) is shown',await p.evaluate(()=>!!document.querySelector('#results .empty')&&!document.querySelector('#results .res')));
  await click('.nt[data-f=sweet]');await click('.nt[data-f=spicy]');await click('.nt[data-f=oud]');
  A(label+': 3 results after 3 picks',(await p.$$('#results .res')).length===3);
  A(label+': a 4th note cannot be picked (tile disabled)',await p.evaluate(()=>document.querySelector('.nt[data-f=woody]').disabled));
  A(label+': counter shows 3 / 3',/3 \/ 3/.test(await p.innerText('#cnt'))||/3 \/ 3/.test((await p.innerText('#cnt')).replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d))));
  const top=await names();
  await click('.nt[data-f=oud]');
  const after=await names();
  A(label+': un-picking updates the results ('+top.join(',')+' -> '+after.join(',')+')',JSON.stringify(top)!==JSON.stringify(after));
  await click('.nt[data-f=oud]');await click('#forChips .chip[data-v=her]');
  const g=await p.evaluate(()=>[...document.querySelectorAll('#results .res')].map(e=>PRODUCTS[e.dataset.id].for));
  A(label+': "for her" shows only women/unisex ('+g.join(',')+')',g.length>0&&g.every(x=>x==='her'||x==='unisex'));
  await click('#forChips .chip[data-v=him]');
  const g2=await p.evaluate(()=>[...document.querySelectorAll('#results .res')].map(e=>PRODUCTS[e.dataset.id].for));
  A(label+': "for him" shows only men/unisex ('+g2.join(',')+')',g2.length>0&&g2.every(x=>x==='him'||x==='unisex'));
  A(label+': honest disclaimer present',(await p.innerText('#honest')).length>80);
  A(label+': every card links to a product page and has an Add button',await p.evaluate(()=>[...document.querySelectorAll('#results .res')].every(e=>e.querySelector('a[href^="#p-"]')&&e.querySelector('[data-add]'))));
  await click('#results .res [data-add]');await p.waitForTimeout(300);
  A(label+': adding from a result puts it in the cart',await p.evaluate(()=>Object.keys(cart).length===1));
  if(label.includes('AR'))A(label+': Arabic wording for strength',/قوي في/.test(await p.innerText('#results')));
  A(label+': no JS errors',errs.length===0);
  await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';document.querySelector('#finder').scrollIntoView()});await p.waitForTimeout(300);
  await p.screenshot({path:'finder_'+label.replace(' ','_')+'.png'});
  await c.close();
 }
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
