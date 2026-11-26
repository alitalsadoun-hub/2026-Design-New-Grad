// Cart upsell (50% off body mist when the cart holds a perfume) + collection cards. Local server.
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8788';
const post=(p,b)=>fetch(BASE+p,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(b)}).then(async r=>({s:r.status,d:await r.json()}));
const seen=()=>{const d=new Date();localStorage.setItem('scentro_welcome',JSON.stringify(d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')))};
(async()=>{const b=await chromium.launch();let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
 const st=(await (await fetch(BASE+'/api/store')).json());const P=Object.values(st.products);const perf=P.find(p=>p.collection==='selective'),mist=P.filter(p=>p.collection==='mist');
 const cust={name:'Upsell Test',phone:'0798111111',gov:'Amman',address:'Test street 12'};
 // ---- server prices (same engine)
 const o1=await post('/api/order',{cart:{[perf.id]:1,[mist[0].id]:2},customer:{...cust,phone:'0798111101'}});
 A('server: perfume + 2 mists -> mists at half price',o1.d.ok&&o1.d.discount===mist[0].price,JSON.stringify([o1.d.discount,mist[0].price]));
 const o2=await post('/api/order',{cart:{[mist[0].id]:2},customer:{...cust,phone:'0798111102'}});
 A('server: mists alone get NO discount',o2.d.ok&&o2.d.discount===0,JSON.stringify(o2.d.discount));
 const o3=await post('/api/order',{cart:{[perf.id]:1,[mist[1].id]:3,[mist[2].id]:2},customer:{...cust,phone:'0798111103'}});
 A('server: every mist (5 of them, two kinds) is half price',o3.d.ok&&o3.d.discount===(mist[1].price*3+mist[2].price*2)/2,JSON.stringify(o3.d.discount));
 // ---- browser
 const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});await c.addInitScript(seen);
 const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto(BASE+'/#en',{waitUntil:'networkidle'});await p.waitForTimeout(600);
 A('home: the offer is NOT advertised (offers section, top bar)',!/body mist/i.test(await p.innerText('#ofgrid'))&&!/mist/i.test(await p.innerText('#ann')));
 await p.evaluate(id=>addCart(id),mist[0].id);await p.evaluate(()=>document.querySelector('#cartbtn').click());await p.waitForTimeout(400);
 A('cart with ONLY a body mist: no upsell panel',!(await p.$('.upsell')));
 await p.evaluate(()=>{closeDrawer&&closeDrawer()});await p.waitForTimeout(300);
 await p.evaluate(id=>addCart(id),perf.id);await p.evaluate(()=>document.querySelector('#cartbtn').click());await p.waitForTimeout(500);
 A('cart with a perfume: upsell panel appears with every mist',!!(await p.$('.upsell'))&&(await p.$$('.up')).length===mist.length,String((await p.$$('.up')).length));
 await p.screenshot({path:'shots/upsell_cart.png'});
 const before=await p.evaluate(()=>Object.values(cart).reduce((a,b)=>a+b,0));await p.click('.up >> nth=1 >> button');await p.waitForTimeout(400);
 A('adding from the panel puts the mist in the cart',await p.evaluate(()=>Object.values(cart).reduce((a,b)=>a+b,0))===before+1&&(await p.$('.upsell'))!==null);
 const foot=await p.innerText('#dfoot');A('a discount line shows in the summary',/Discount|−/.test(foot),foot);
 await p.click('#go');await p.waitForTimeout(300);await p.fill('input[name=n]','Upsell UI');await p.fill('input[name=p]','0798111199');await p.fill('textarea[name=a]','Test street 5, Amman');await p.click('#pl');await p.waitForTimeout(1200);
 A('order with mists goes through',/SC-\d{5}/.test(await p.innerText('#dbody')));await c.close();
 // ---- collection cards
 const c2=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await c2.addInitScript(seen);
 const q=await c2.newPage();await q.goto(BASE+'/#en',{waitUntil:'networkidle'});
 for(const col of ['niche','selective','mist']){
  const sel='.cat[data-col='+col+']';const ok=await q.$(sel);A('card "'+col+'" exists with its collection',!!ok);if(!ok)continue;await q.evaluate(s=>document.querySelector(s).click(),sel);await q.waitForTimeout(500);
  const res=await q.evaluate(c=>({v:colV,n:[...document.querySelectorAll('#best .card')].length,all:Object.keys(PRODUCTS).filter(i=>PRODUCTS[i].collection===c).length}),col);
  A('click on the '+col+' picture filters the shop to '+col+' ('+res.n+' shown)',res.v===col&&res.n>0&&res.n===Math.min(12,res.all),JSON.stringify(res));}
 A('no JS errors',errs.length===0,errs.join('|'));
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
