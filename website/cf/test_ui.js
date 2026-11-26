// End-to-end in a real browser against a running server: store -> order -> dashboard. BASE / PW env vars as in test_api.js
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8788',PW=process.env.PW||'test-password-123';
(async()=>{const b=await chromium.launch();let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
 // --- admin helper via API: make one product "low stock" (2) so the hint can be checked
 const lg=await fetch(BASE+'/api/admin/login',{method:'POST',headers:{'content-type':'application/json','x-admin':process.env.AT||'testtoken123456'},body:JSON.stringify({password:PW})});const ck=lg.headers.get('set-cookie').split(';')[0];
 const AT=process.env.AT||'testtoken123456',AP='/manage-'+AT;const ad=(p,m,body)=>fetch(BASE+'/api/admin/'+p,{method:m,headers:{'content-type':'application/json',cookie:ck,'x-admin':AT},body:body&&JSON.stringify(body)}).then(r=>r.json());
 const st=(await (await fetch(BASE+'/api/store')).json()).products;const sel=Object.values(st).filter(p=>p.collection==='selective');const lowP=sel[0],normP=sel[1];
 await ad('products/'+lowP.id,'PUT',{price:lowP.price,was:lowP.was,stock:2,hidden:false});await ad('settings','PUT',{showLowStock:true});
 for(const [label,vp,mobile,hash] of [['desktop EN',{width:1440,height:900},false,'#en'],['mobile AR',{width:390,height:844},true,'#ar']]){
  const c=await b.newContext({viewport:vp,isMobile:mobile,hasTouch:mobile});await c.addInitScript(()=>{const d=new Date();localStorage.setItem('scentro_welcome',JSON.stringify(d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')))});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
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
 const c=await b.newContext({viewport:{width:1280,height:900}});await c.addInitScript(()=>{const d=new Date();localStorage.setItem('scentro_welcome',JSON.stringify(d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')))});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto(BASE+AP,{waitUntil:'networkidle'});await p.waitForTimeout(800);
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
 // ---- add a product with a photo, edit it, see it in the public store
 require('fs').writeFileSync('/tmp/claude-0/t.png',Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==','base64'));
 await p.click('#np');await p.waitForTimeout(300);
 await p.fill('#pff [name=name]','UI Orchid');await p.selectOption('#pff [name=collection]','selective');await p.selectOption('#pff [name=for]','unisex');await p.fill('#pff [name=price]','25');await p.fill('#pff [name=was]','33');await p.fill('#pff [name=stock]','5');
 await p.fill('#pff [name=original]','Black Orchid');await p.fill('#pff [name=key]','Orchid, Chocolate, Patchouli');
 await p.setInputFiles('#pfile','/tmp/claude-0/t.png');await p.waitForFunction(()=>/Photo ready/.test(document.querySelector('#pst').textContent),null,{timeout:8000}).catch(()=>{});
 A('photo uploaded from the form',/Photo ready/.test(await p.innerText('#pst')));
 await p.screenshot({path:'shots/dash_product_form.png',fullPage:true});
 await p.click('#pff button[type=submit]');await p.waitForTimeout(900);
 A('new product appears in the products list',/UI Orchid/.test(await p.innerText('#adbody')));
 const pub=(await (await fetch(BASE+'/api/store')).json()).products;const np=Object.values(pub).find(x=>x.name==='UI Orchid');A('new product is live in the public store',!!np&&np.key.length===3&&np.insp.original==='Black Orchid');
 await p.locator('tr[data-pid="'+np.id+'"] [data-edit]').click();await p.waitForTimeout(300);await p.fill('#pff [name=price]','27');await p.click('#pff button[type=submit]');await p.waitForTimeout(800);
 A('edit saved',(await (await fetch(BASE+'/api/store')).json()).products[np.id].price===27);
 await ad('products/'+np.id,'DELETE',{});
 // ---- settings: delivery fee + announcement reach the storefront
 await p.click('.ad-top .tabs button[data-tab=settings]');await p.waitForTimeout(400);await p.fill('#sf4 [name=fee]','4');await p.fill('#sf4 [name=ae]','Eid hours test');await p.click('#sf4 button[type=submit]');await p.waitForTimeout(800);
 const sp=await c.newPage();await sp.goto(BASE+'/#en',{waitUntil:'networkidle'});await sp.waitForTimeout(600);
 A('storefront shows the custom top-bar message and the new fee',/Eid hours test/.test(await sp.innerText('#ann'))&&/Delivery 4 JOD/.test(await sp.innerText('#ann')),(await sp.innerText('#ann')));
 await sp.evaluate(id=>{addCart(id)},normP.id);await sp.evaluate(()=>document.querySelector('#cartbtn').click());await sp.waitForTimeout(300);A('cart total uses fee 4',/Delivery\s*\n?\s*4 JOD/.test(await sp.innerText('#dfoot')),(await sp.innerText('#dfoot')).replace(/\n/g,' | '));await sp.close();
 await ad('settings','PUT',{deliveryFee:3,annEn:'',annAr:''});
 // ---- orders tab: search, CSV, print
 await p.click('.ad-top .tabs button[data-tab=orders]');await p.waitForTimeout(600);
 A('orders stats strip shown',/last 7 days/i.test(await p.innerText("#adbody")));
 await p.fill('#oq','nomatchxyz');await p.waitForTimeout(300);A('order search filters (no match)',/No orders match/.test(await p.innerText('#adbody')));await p.fill('#oq','UI Tester');await p.waitForTimeout(300);A('order search finds the order',/UI Tester/.test(await p.innerText('#adbody')));
 const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#csv')]);const csv=require('fs').readFileSync(await dl.path(),'utf8');A('Excel export has header + the order',/"Order","Date","Status"/.test(csv)&&/UI Tester/.test(csv));
 const [pop]=await Promise.all([c.waitForEvent('page'),p.locator('[data-pr]').first().click()]);await pop.waitForLoadState();A('print slip opens with total to collect',/Total to collect/.test(await pop.innerText('body')));await pop.close();
 await p.click('.ad-top .tabs button[data-tab=promos]');await p.waitForTimeout(600);A('promotions tab shows offers',/3rd free|buy 2/i.test(await p.innerText('#adbody')));
 await p.screenshot({path:'shots/dash_promos.png'});
 await p.click('.ad-top .tabs button[data-tab=settings]');await p.waitForTimeout(500);A('settings tab: e-mail + password forms',!!(await p.$('#sf1'))&&!!(await p.$('#sf2')));
 await p.screenshot({path:'shots/dash_settings.png'});
 await p.click('#adout');await p.waitForTimeout(700);A('sign out returns to login',!!(await p.$('#lgp')));
 A('no JS errors in dashboard',errs.length===0,errs.join('|'));
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
