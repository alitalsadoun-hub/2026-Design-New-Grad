const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();let fail=0;const A=(n,c)=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n)};
 const url='file://'+process.cwd()+'/index.html#en';
 for(const [label,vp,mobile] of [['desktop',{width:1440,height:900},false],['mobile',{width:390,height:844},true]]){
  const c=await b.newContext({viewport:vp,isMobile:mobile,hasTouch:mobile});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto(url,{waitUntil:'networkidle'});
  await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto'});
  // 1) product page -> browser back restores the exact scroll position
  await p.evaluate(()=>window.scrollTo(0,document.querySelector('#shop').offsetTop+300));await p.waitForTimeout(300);
  const y0=await p.evaluate(()=>scrollY);
  await p.evaluate(()=>document.querySelector('#best .card h3 a').click());await p.waitForTimeout(500);
  A(label+': product page opened',await p.evaluate(()=>document.body.classList.contains('ispdp')));
  await p.goBack();await p.waitForTimeout(700);
  const y1=await p.evaluate(()=>scrollY);
  A(label+': back returns to the list at the same scroll ('+y0+' -> '+y1+')',!await p.evaluate(()=>document.body.classList.contains('ispdp'))&&Math.abs(y1-y0)<80);
  // 2) on-page Back button
  await p.evaluate(()=>document.querySelector('#best .card h3 a').click());await p.waitForTimeout(500);
  await p.evaluate(()=>document.querySelector('#pback').click());await p.waitForTimeout(700);
  A(label+': Back button on product page works',!await p.evaluate(()=>document.body.classList.contains('ispdp'))&&Math.abs(await p.evaluate(()=>scrollY)-y0)<80);
  // 3) cart: back closes it, page stays
  await p.evaluate(()=>document.querySelector('#cartbtn').click());await p.waitForTimeout(400);
  A(label+': cart opened',await p.evaluate(()=>document.querySelector('#drawer').classList.contains('on')));
  await p.goBack();await p.waitForTimeout(500);
  A(label+': back closes the cart (page unchanged)',!await p.evaluate(()=>document.querySelector('#drawer').classList.contains('on'))&&!await p.evaluate(()=>document.body.classList.contains('ispdp')));
  // 4) cart closed with the x button leaves no stuck state
  await p.evaluate(()=>document.querySelector('#cartbtn').click());await p.waitForTimeout(300);await p.evaluate(()=>document.querySelector('#dclose').click());await p.waitForTimeout(500);
  A(label+': x button closes the cart',!await p.evaluate(()=>document.querySelector('#drawer').classList.contains('on')));
  // 5) search
  await p.evaluate(()=>document.querySelector('#searchbtn').click());await p.waitForTimeout(300);
  await p.goBack();await p.waitForTimeout(400);
  A(label+': back closes search',!await p.evaluate(()=>document.querySelector('#search').classList.contains('on')));
  // 6) mobile menu
  if(mobile){await p.evaluate(()=>document.querySelector('#menubtn').click());await p.waitForTimeout(400);await p.goBack();await p.waitForTimeout(400);
   A(label+': back closes the menu',!await p.evaluate(()=>document.querySelector('#mnav').classList.contains('on')));}
  // 7) direct entry on a product page: Back goes to the shop section
  await p.goto(url.replace('#en','#p-9'),{waitUntil:'load'});await p.waitForTimeout(500);
  await p.evaluate(()=>document.querySelector('#pback').click());await p.waitForTimeout(700);
  A(label+': direct product link -> Back goes to the shop',!await p.evaluate(()=>document.body.classList.contains('ispdp')));
  A(label+': no JS errors',errs.length===0);
  await c.close();
 }
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
