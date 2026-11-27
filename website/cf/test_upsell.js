// Cart upsell (50% off body mist when the cart holds a perfume) + collection cards. Local server.
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8788';
const post=(p,b)=>fetch(BASE+p,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(b)}).then(async r=>({s:r.status,d:await r.json()}));
const seen=()=>{const d=new Date();localStorage.setItem('scentro_welcome',JSON.stringify(d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')))};
(async()=>{const b=await chromium.launch();let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
 const st=(await (await fetch(BASE+'/api/store')).json());const P=Object.values(st.products);const perf=P.find(p=>p.collection==='selective'),mist=P.filter(p=>p.collection==='mist');
 const cust={name:'Upsell Test',phone:'0798111111',gov:'Amman',address:'Test street 12'};
 // ---- add room sprays through the dashboard API (new collection)
 const AT=process.env.AT||'testtoken123456',PW=process.env.PW||'test-password-123';
 const lg=await fetch(BASE+'/api/admin/login',{method:'POST',headers:{'content-type':'application/json','x-admin':AT},body:JSON.stringify({password:PW})});const ck=lg.headers.get('set-cookie').split(';')[0];
 const adm=(p,m,b)=>fetch(BASE+'/api/admin/'+p,{method:m,headers:{'content-type':'application/json',cookie:ck,'x-admin':AT},body:JSON.stringify(b)}).then(r=>r.json());
 const png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';const up=await adm('upload','POST',{data:png});
 const room=[];for(const [n,st] of [['Rain Forest Room Spray',8],['Mona Rosa Room Spray',1]]){const r=await adm('products','POST',{name:n,collection:'room',for:'unisex',ml:250,price:10,stock:st,img:up.path,top:'Lemon, Green Notes',heart:'Rose',base:'Musk'});room.push(r.id)}
 A('room spray products created (collection "room")',room.every(Boolean),JSON.stringify(room));
 const st2=(await (await fetch(BASE+'/api/store')).json());A('room sprays are in the public store, no quantities',room.every(id=>st2.products[id]&&st2.products[id].collection==='room')&&!JSON.stringify(st2).includes('"stock"'));
 const o4=await post('/api/order',{cart:{[perf.id]:1,[room[0]]:3},customer:{...cust,phone:'0798111104'}});
 A('server: perfume + 3 room sprays -> half price on all three',o4.d.ok&&o4.d.discount===15,JSON.stringify(o4.d.discount));
 const o5=await post('/api/order',{cart:{[room[0]]:2},customer:{...cust,phone:'0798111105'}});A('server: room sprays alone get no discount',o5.d.ok&&o5.d.discount===0);
 const o6=await post('/api/order',{cart:{[perf.id]:1,[mist[0].id]:1,[room[0]]:1},customer:{...cust,phone:'0798111106'}});A('server: mist + room spray together, both half price',o6.d.ok&&o6.d.discount===10,JSON.stringify(o6.d.discount));
 const o7=await post('/api/order',{cart:{[perf.id]:1,[room[1]]:2},customer:{...cust,phone:'0798111107'}});A('last piece: ordering 2 when 1 is left is refused',o7.s===409);
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
 const nUp=(await p.$$('.up')).length,expUp=Object.values((await (await fetch(BASE+'/api/store')).json()).products).filter(x=>x.collection==='mist'||x.collection==='room').length;A('cart with a perfume: upsell panel appears with every body mist and room spray',!!(await p.$('.upsell'))&&nUp===expUp,nUp+' vs '+expUp);
 await p.screenshot({path:'shots/upsell_cart.png'});
 const before=await p.evaluate(()=>Object.values(cart).reduce((a,b)=>a+b,0));await p.click('.up >> nth=1 >> button');await p.waitForTimeout(400);
 A('adding from the panel puts the mist in the cart',await p.evaluate(()=>Object.values(cart).reduce((a,b)=>a+b,0))===before+1&&(await p.$('.upsell'))!==null);
 const foot=await p.innerText('#dfoot');A('a discount line shows in the summary',/Discount|−/.test(foot),foot);
 await p.click('#go');await p.waitForTimeout(300);await p.fill('input[name=n]','Upsell UI');await p.fill('input[name=p]','0798111199');await p.fill('textarea[name=a]','Test street 5, Amman');await p.click('#pl');await p.waitForTimeout(1200);
 A('order with mists goes through',/SC-\d{5}/.test(await p.innerText('#dbody')));await c.close();
 // ---- room spray in the browser
 const c3=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});await c3.addInitScript(seen);const r=await c3.newPage();const rerr=[];r.on('pageerror',e=>rerr.push(e.message));
 await r.goto(BASE+'/#en',{waitUntil:'networkidle'});await r.waitForTimeout(500);
 A('home shows the Room spray collection card',await r.evaluate(()=>!document.querySelector('#catRoom').hidden));
 A('filter chip "Room spray" exists',await r.evaluate(()=>[...document.querySelectorAll('#filters button')].some(b=>/Room spray/i.test(b.innerText))));
 await r.evaluate(()=>document.querySelector('.cat[data-col=room]').click());await r.waitForTimeout(500);const rc=await r.evaluate(()=>({v:colV,n:document.querySelectorAll('#best .card').length,names:[...document.querySelectorAll('#best .card h3')].map(h=>h.innerText).slice(0,4),rooms:Object.values(PRODUCTS).filter(p=>p.collection==='room').map(p=>p.name)}));const liveNow=Object.values((await (await fetch(BASE+'/api/store')).json()).products),roomsNow=liveNow.filter(x=>x.collection==='room').length,upNow=liveNow.filter(x=>x.collection==='mist'||x.collection==='room').length;A('room card filters to the room sprays',rc.v==='room'&&rc.n===roomsNow&&roomsNow>=1,JSON.stringify(rc)+' expected '+roomsNow);
 await r.evaluate(([a,b])=>{addCart(a);addCart(b)},[perf.id,room[0]]);await r.evaluate(()=>document.querySelector('#cartbtn').click());await r.waitForTimeout(500);
 const nU2=(await r.$$('.up')).length;A('cart upsell offers mist + room spray together',/body mist or room spray/i.test(await r.innerText('.upsell'))&&nU2===upNow,nU2+' vs '+upNow);
 await r.screenshot({path:'shots/upsell_room.png'});
 await r.evaluate(()=>{closeDrawer()});await r.waitForTimeout(300);
 A('finder never recommends a room spray',await r.evaluate(()=>{picked=['woody','sweet','fruity'];forV='any';renderResults();return ![...document.querySelectorAll('#results .res h3')].some(h=>/Room Spray/i.test(h.innerText))}));
 A('no JS errors (room spray)',rerr.length===0,rerr.join('|'));await c3.close();
 // ---- collection cards
 const c2=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await c2.addInitScript(seen);
 const q=await c2.newPage();await q.goto(BASE+'/#en',{waitUntil:'networkidle'});
 for(const col of ['niche','selective','mist']){
  const sel='.cat[data-col='+col+']';const ok=await q.$(sel);A('card "'+col+'" exists with its collection',!!ok);if(!ok)continue;await q.evaluate(s=>document.querySelector(s).click(),sel);await q.waitForTimeout(500);
  const res=await q.evaluate(c=>({v:colV,n:[...document.querySelectorAll('#best .card')].length,all:Object.keys(PRODUCTS).filter(i=>PRODUCTS[i].collection===c).length}),col);
  A('click on the '+col+' picture filters the shop to '+col+' ('+res.n+' shown)',res.v===col&&res.n>0&&res.n===Math.min(12,res.all),JSON.stringify(res));}
 A('no JS errors',errs.length===0,errs.join('|'));
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
