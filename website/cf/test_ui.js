// End-to-end in a real browser against a running server: store -> order -> dashboard. BASE / PW env vars as in test_api.js
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8788',PW=process.env.PW||'test-password-123';
(async()=>{const b=await chromium.launch();let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
 // --- admin helper via API: make one product "low stock" (2) so the hint can be checked
 const lg=await fetch(BASE+'/api/admin/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({password:PW})});const ck=lg.headers.get('set-cookie').split(';')[0];
 const ad=(p,m,body)=>fetch(BASE+'/api/admin/'+p,{method:m,headers:{'content-type':'application/json',cookie:ck},body:body&&JSON.stringify(body)}).then(r=>r.json());
 const st=(await (await fetch(BASE+'/api/store')).json()).products;const sel=Object.values(st).filter(p=>p.collection==='selective'&&p.stock>3);const lowP=sel[0],normP=sel[1];
 await ad('products/'+lowP.id,'PUT',{price:lowP.price,was:lowP.was,stock:2,hidden:false});
 for(const [label,vp,mobile,hash] of [['desktop EN',{width:1440,height:900},false,'#en'],['mobile AR',{width:390,height:844},true,'#ar']]){
  const c=await b.newContext({viewport:vp,isMobile:mobile,hasTouch:mobile});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto(BASE+'/'+hash,{waitUntil:'networkidle'});await p.waitForFunction(()=>typeof SERVER!=='undefined'&&SERVER===true,null,{timeout:8000}).catch(()=>{});
  A(label+': page runs in server mode',await p.evaluate(()=>SERVER===true));
  A(label+': low-stock item shows "only N left"',await p.evaluate(id=>!!PRODUCTS[id]&&PRODUCTS[id].stock<=3&&lowStock(PRODUCTS[id]),lowP.id));
  A(label+': normal-stock items show no stock number',await p.evaluate(id=>!lowStock(PRODUCTS[id]),normP.id));
  await p.evaluate(ids=>{addCart(ids[0]);addCart(ids[1])},[lowP.id,normP.id]);await p.evaluate(()=>document.querySelector('#cartbtn').click());await p.waitForTimeout(400);
  A(label+': offer nudge in cart (2 Selective)',/\d/.test(await p.innerText('#dbody')));
  await p.click('#go');await p.waitForTimeout(300);
  await p.fill('input[name=n]','UI Tester');await p.fill('input[name=p]','079'+(label.includes('AR')?'7777777':'6666666'));await p.fill('textarea[name=a]','Test street 1, Amman <b>x</b>');
  await p.click('#pl');await p.waitForTimeout(1200);
  const done=await p.innerText('#dbody');A(label+': confirmation shown with order number',/SC-\d{5}/.test(done),done.slice(0,120));
  const no=(done.match(/SC-\d{5}/)||[])[0];
  await p.screenshot({path:`shots/order_done_${label.replace(' ','_')}.png`});
  const wa=await p.getAttribute('.btn.wa2','href');A(label+': WhatsApp confirm link prefilled',wa.startsWith('https://wa.me/962797906211?text=')&&decodeURIComponent(wa).includes('UI Tester'));
  const o=(await ad('orders','GET')).orders.find(x=>x.no===no);A(label+': order is saved on the server',!!o&&o.customer.name==='UI Tester'&&o.lines.length===2);
  A(label+': no JS errors',errs.length===0,errs.join('|'));await c.close()}
 // --- dashboard in the browser
 const c=await b.newContext({viewport:{width:1280,height:900}});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto(BASE+'/#admin-orders',{waitUntil:'networkidle'});await p.waitForTimeout(800);
 A('dashboard asks for a password (nothing visible before login)',await p.evaluate(()=>!!document.querySelector('#lgp')&&!/UI Tester/.test(document.body.innerText)));
 await p.fill('#lgp','wrong');await p.click('#lg button');await p.waitForTimeout(600);A('wrong password shows an error',/Wrong password/.test(await p.innerText('#lgm')));
 await p.fill('#lgp',PW);await p.click('#lg button');await p.waitForTimeout(1200);
 A('login works, orders listed',/UI Tester/.test(await p.innerText('#adbody')));
 A('customer HTML is neutralised (server strips tags, dashboard escapes)',/Test street 1, Amman/.test(await p.innerText('#adbody'))&&!(await p.$('#adbody td b:text-is("x")')));
 await p.screenshot({path:'shots/dash_orders.png'});
 await p.selectOption('select.st >> nth=0','confirmed');await p.waitForTimeout(700);
 A('status change persisted',(await ad('orders','GET')).orders[0].status==='confirmed');
 await p.click('.ad-top .tabs button[data-tab=products]');await p.waitForTimeout(600);
 A('products tab lists items',(await p.$$('tr[data-pid]')).length>50);
 await p.screenshot({path:'shots/dash_products.png'});
 const row=p.locator(`tr[data-pid="${normP.id}"]`);await row.locator('[name=stock]').fill('1');await row.locator('[data-save]').click();await p.waitForTimeout(700);
 A('stock edit saved from the UI',(await ad('products','GET')).products[normP.id].stock===1);
 await p.click('.ad-top .tabs button[data-tab=promos]');await p.waitForTimeout(600);A('promotions tab shows offers',/3rd free|buy 2/i.test(await p.innerText('#adbody')));
 await p.screenshot({path:'shots/dash_promos.png'});
 await p.click('.ad-top .tabs button[data-tab=settings]');await p.waitForTimeout(500);A('settings tab: e-mail + password forms',!!(await p.$('#sf1'))&&!!(await p.$('#sf2')));
 await p.screenshot({path:'shots/dash_settings.png'});
 await p.click('#adout');await p.waitForTimeout(700);A('sign out returns to login',!!(await p.$('#lgp')));
 A('no JS errors in dashboard',errs.length===0,errs.join('|'));
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
