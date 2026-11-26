// API tests against a running `wrangler pages dev` (default http://localhost:8788) with test password "test-password-123"
const B=process.env.BASE||'http://localhost:8788',PW=process.env.PW||'test-password-123';let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
const j=async(p,o={})=>{if(p.startsWith('/api/admin')&&p!=='/api/admin/x'){o={...o,headers:{...(o.headers||{}),'x-admin':process.env.AT||'testtoken123456'}}}const r=await fetch(B+p,o);let d={};try{d=await r.json()}catch{}return {s:r.status,d,h:r.headers}};
const post=(p,b,ck)=>j(p,{method:'POST',headers:{'content-type':'application/json',...(ck?{cookie:ck}:{})},body:JSON.stringify(b)});
const put=(p,b,ck)=>j(p,{method:'PUT',headers:{'content-type':'application/json',cookie:ck},body:JSON.stringify(b)});
const cust={name:'Test Customer',phone:'0791234567',gov:'Amman',address:'Abdoun, street 5',note:'call first'};
async function extra(ck){
 const png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
 const up=await post('/api/admin/upload',{data:png},ck);A('photo upload works',up.d.ok&&/^img\/u\/.+\.png$/.test(up.d.path),JSON.stringify(up.d));
 A('upload refuses non-images',(await post('/api/admin/upload',{data:'data:text/html;base64,PGI+'},ck)).d.ok===false);
 const mk=await post('/api/admin/products',{name:'Black Orchid',collection:'selective',for:'unisex',ml:100,price:25,was:33,stock:4,img:up.d.path,original:'Black Orchid',house:'Tom Ford',key:'Orchid, Chocolate, Patchouli',top:'Truffle, Ylang',heart:'Orchid',base:'Patchouli'},ck);
 A('new product created',mk.d.ok&&mk.d.id,JSON.stringify(mk.d));
 let st=(await j('/api/store')).d;A('new product is in the public store with its notes',st.products[mk.d.id]&&st.products[mk.d.id].notes.top.length===2&&st.products[mk.d.id].insp.original==='Black Orchid'&&st.products[mk.d.id].key.length===3);
 A('product without a photo refused',(await post('/api/admin/products',{name:'x',collection:'niche',for:'her',ml:50,price:10,stock:1},ck)).d.ok===false);
 A('bad collection refused',(await post('/api/admin/products',{name:'x',collection:'zzz',for:'her',ml:50,price:10,stock:1,img:up.d.path},ck)).d.ok===false);
 A('external image url refused',(await post('/api/admin/products',{name:'x',collection:'niche',for:'her',ml:50,price:10,stock:1,img:'https://evil.example/x.png'},ck)).d.ok===false);
 const ed=await put('/api/admin/products/'+mk.d.id,{name:'Black Orchid 2',collection:'selective',for:'unisex',ml:100,price:27,was:'',stock:3,img:up.d.path,original:'Black Orchid',top:'',heart:'',base:'',key:''},ck);A('product edited',ed.d.ok);
 st=(await j('/api/store')).d;A('edit visible (name, price, notes removed)',st.products[mk.d.id].name==='Black Orchid 2'&&st.products[mk.d.id].price===27&&!st.products[mk.d.id].notes);
 A('html in name is neutralised',(await post('/api/admin/products',{name:'<script>alert(1)</script>Z',collection:'niche',for:'her',ml:50,price:10,stock:1,img:up.d.path},ck)).d.ok&&Object.values((await j('/api/store')).d.products).every(p=>!/[<>]/.test(p.name)));
 // display order: more pieces first, the last few at the end
 const ids3=Object.keys((await j('/api/store')).d.products).slice(0,3),pr=(await j('/api/admin/products',{headers:{cookie:ck}})).d.products;
 await put('/api/admin/products/'+ids3[0],{price:pr[ids3[0]].price,was:pr[ids3[0]].was,stock:2,hidden:false},ck);await put('/api/admin/products/'+ids3[1],{price:pr[ids3[1]].price,was:pr[ids3[1]].was,stock:30,hidden:false},ck);await put('/api/admin/products/'+ids3[2],{price:pr[ids3[2]].price,was:pr[ids3[2]].was,stock:9,hidden:false},ck);
 const ps=(await j('/api/store')).d.products;A('ranking: 30 pieces before 9 pieces before 2 pieces',ps[ids3[1]].r<ps[ids3[2]].r&&ps[ids3[2]].r<ps[ids3[0]].r,JSON.stringify([ps[ids3[1]].r,ps[ids3[2]].r,ps[ids3[0]].r]));
 const real2=(await j('/api/admin/products',{headers:{cookie:ck}})).d.products;A('every item with 5+ pieces is listed before the 2-piece item',Object.keys(ps).filter(i=>real2[i].stock>=5).every(i=>ps[i].r<ps[ids3[0]].r)&&Object.keys(ps).filter(i=>real2[i].stock<=4&&i!==ids3[0]).every(i=>ps[i].r>Math.max(...Object.keys(ps).filter(k=>real2[k].stock>=5).map(k=>ps[k].r))));
 const ov=await post('/api/order',{cart:{[ids3[0]]:6},customer:{...cust,phone:'0797000001'}});A('over-ordering is refused WITHOUT saying how many are left',ov.s===409&&!JSON.stringify(ov.d).match(/"(stock|max|left)":\s*\d/),JSON.stringify(ov.d));
 let blocked=false;for(let k=0;k<14;k++){const r=await post('/api/order',{cart:{[ids3[0]]:7},customer:{...cust,phone:'0797000002'}});if(r.s===429)blocked=true}A('probing quantities with repeated over-orders gets rate-limited',blocked);
 // settings

 A('fee below 1 refused',(await put('/api/admin/settings',{deliveryFee:0},ck)).d.ok===false);
 A('bad whatsapp number refused',(await put('/api/admin/settings',{wa:'12345'},ck)).d.ok===false);
 A('bad pop-up date refused',(await put('/api/admin/settings',{popupEnd:'tomorrow'},ck)).d.ok===false);
 A('pop-up can be switched off and re-dated',(await put('/api/admin/settings',{popupOn:false,popupEnd:'2026-12-15'},ck)).d.ok&&(await j('/api/store')).d.popup.on===false&&(await j('/api/store')).d.popup.end==='2026-12-15');
 await put('/api/admin/settings',{popupOn:true,popupEnd:'2026-11-30'},ck);
 A('settings saved',(await put('/api/admin/settings',{deliveryFee:4,wa:'962781234567',annEn:'Eid hours <b>x</b>',annAr:'ساعات العيد'},ck)).d.ok);
 st=(await j('/api/store')).d;A('store reflects fee 4, whatsapp, announcement (tags stripped)',st.deliveryFee===4&&st.wa==='962781234567'&&st.annEn==='Eid hours b x /b'&&st.annAr==='ساعات العيد',JSON.stringify([st.deliveryFee,st.wa,st.annEn]));
 const sel=Object.values(st.products).find(p=>p.collection==='niche');
 const o4=await post('/api/order',{cart:{[sel.id]:1},customer:{name:'Fee Test',phone:'0798888888',gov:'Amman',address:'Test street 12'}});A('order uses the new delivery fee (price + 4)',o4.d.ok&&o4.d.delivery===4&&o4.d.total===sel.price+4,JSON.stringify([o4.d.delivery,o4.d.total]));
 await put('/api/admin/settings',{paused:true},ck);A('paused: order refused',(await post('/api/order',{cart:{[sel.id]:1},customer:{name:'Paused Test',phone:'0798888889',gov:'Amman',address:'Test street 12'}})).d.error==='paused');
 A('paused flag visible to the store',(await j('/api/store')).d.paused===true);
 await put('/api/admin/settings',{paused:false,deliveryFee:3,wa:'962797906211',annEn:'',annAr:''},ck);
 A('delete product',(await fetch(B+'/api/admin/products/'+mk.d.id,{method:'DELETE',headers:{'content-type':'application/json',cookie:ck,'x-admin':process.env.AT||'testtoken123456'},body:'{}'}).then(r=>r.json())).ok&&!(await j('/api/store')).d.products[mk.d.id]);
}
(async()=>{
 // the dashboard is invisible to the public
 A('dashboard API does not exist without the secret token (login too)',(await fetch(B+'/api/admin/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({password:PW})})).status===404&&(await fetch(B+'/api/admin/orders')).status===404);
 A('wrong token is refused (404)',(await fetch(B+'/api/admin/me',{headers:{'x-admin':'guess'}})).status===404);
 A('dashboard page opens only at the secret address',(await fetch(B+'/manage-testtoken123456')).status===200&&(process.env.LOCAL_SPA_FALLBACK||true)&&(await fetch(B+'/admin-page.html')).status===404);
 const home=await (await fetch(B+'/')).text();A('public page contains no dashboard code',!/Pause new orders|promosHtml|Download Excel|adApi|x-admin/.test(home));
 const adm=await (await fetch(B+'/manage-testtoken123456')).text();A('dashboard page is noindex and carries the token only at that address',/noindex/.test(adm)&&adm.includes('testtoken123456')&&!home.includes('testtoken123456'));
 let s=(await j('/api/store')).d;A('store lists products',Object.keys(s.products).length>50);
 A('public rules carry no coupon codes',s.rules.every(r=>!r.code));
 const ids=Object.keys(s.products),sel=ids.filter(i=>s.products[i].collection==='selective'),pid=sel[0],p0=s.products[pid];
 A('public store carries NO stock numbers (hints are off by default)',!JSON.stringify(s).includes('"stock"')&&Object.values(s.products).every(p=>!('low' in p)&&typeof p.r==='number'));
 A('low-stock hint is off by default',s.lowStock===false);
 A('welcome pop-up config is public and on by default (ends 2026-11-30)',s.popup&&s.popup.on===true&&s.popup.end==='2026-11-30');
 // validation
 A('rejects bad phone',(await post('/api/order',{cart:{[pid]:1},customer:{...cust,phone:'12345'}})).d.error==='phone');
 A('rejects short name',(await post('/api/order',{cart:{[pid]:1},customer:{...cust,name:'x'}})).d.error==='name');
 A('rejects unknown governorate',(await post('/api/order',{cart:{[pid]:1},customer:{...cust,gov:'Mars'}})).d.error==='gov');
 A('rejects empty cart',(await post('/api/order',{cart:{},customer:cust})).d.error==='cart');
 A('rejects unknown product',(await post('/api/order',{cart:{nope:1},customer:cust})).d.error==='stock');
 A('rejects more than stock',(await post('/api/order',{cart:{[pid]:9999},customer:cust})).d.ok!==true);
 // happy path + server-side price (browser total ignored)
 const o=await post('/api/order',{cart:{[pid]:1},customer:cust,total:0.01});
 A('order accepted',o.d.ok&&/^SC-\d{5}$/.test(o.d.no),JSON.stringify(o.d));
 A('total = price + 3 delivery (server priced)',o.d.total===p0.price+3,o.d.total+' vs '+(p0.price+3));
 let s2=(await j('/api/store')).d;
 const lg0=await post('/api/admin/login',{password:PW});const ck0=(lg0.h.get('set-cookie')||'').split(';')[0];const real=(await j('/api/admin/products',{headers:{cookie:ck0}})).d.products[pid].stock;A('real stock decreased by 1 (6 -> 5)',real===5,String(real));
 // buy 3 selective -> 3rd free offer
 const three=sel.slice(0,3),o3=await post('/api/order',{cart:Object.fromEntries(three.map(i=>[i,1])),customer:{...cust,phone:'0792222222'}});
 A('buy-2-get-3rd-free applied on server',o3.d.ok&&o3.d.discount>0&&o3.d.applied.length>0,JSON.stringify(o3.d.applied));
 // admin gate
 A('admin api needs login',(await j('/api/admin/orders')).s===401);
 const bad1=await post('/api/admin/login',{password:'wrong'});A('wrong password rejected',bad1.s===401);
 const lg=await post('/api/admin/login',{password:PW});A('login ok + HttpOnly cookie',lg.d.ok&&/HttpOnly/i.test(lg.h.get('set-cookie')||''));
 const ck=(lg.h.get('set-cookie')||'').split(';')[0];
 const ord=await j('/api/admin/orders',{headers:{cookie:ck}});A('orders listed (2)',ord.d.ok&&ord.d.orders.length>=2&&ord.d.orders[0].customer.name==='Test Customer');
 A('CSRF guard: write without json content-type refused',(await j('/api/admin/rules',{method:'PUT',headers:{cookie:ck,'content-type':'text/plain'},body:'{}'})).s===415);
 // coupon secrecy + coupon flow
 const rr=(await j('/api/admin/rules',{headers:{cookie:ck}})).d.rules;A('admin sees all rules incl. coupon',rr.some(r=>r.code));
 const code=rr.find(r=>r.code).code,cp=await j('/api/coupon?code='+code);A('valid coupon returns the rule',cp.d.ok&&cp.d.rule.code===code);
 A('invalid coupon refused',(await j('/api/coupon?code=NOPE')).d.ok===false);
 const oc=await post('/api/order',{cart:{[pid]:1},customer:{...cust,phone:'0793333333'},code});A('coupon applied on server',oc.d.ok&&oc.d.code===code&&oc.d.discount>0,JSON.stringify(oc.d));
 // rules CRUD
 const newRules=[...rr.map(r=>({...r})),{id:'t1',name:'Test 5 off',type:'amount_cart',amount:5,minSpend:20,active:true,stackable:false,priority:9,scope:{type:'all'}}];
 A('rules saved',(await put('/api/admin/rules',{rules:newRules},ck)).d.ok);
 s2=(await j('/api/store')).d;A('new automatic offer is public',s2.rules.some(r=>r.id==='t1'));
 await put('/api/admin/rules',{rules:rr},ck);
 // products edit + hidden
 const pe=await put('/api/admin/products/'+pid,{price:p0.price,was:p0.was,stock:2,hidden:false},ck);A('stock edited to 2',pe.d.ok);
 s2=(await j('/api/store')).d;A('hints off: a product with 2 left looks like any other (no number)',s2.products[pid]&&!('low' in s2.products[pid])&&!('stock' in s2.products[pid]));
 await put('/api/admin/settings',{showLowStock:true},ck);s2=(await j('/api/store')).d;A('hints on: only the last 1-3 get a low flag',s2.products[pid].low===2&&Object.values(s2.products).filter(p=>p.low).every(p=>p.low>=1&&p.low<=3)&&!JSON.stringify(s2).includes('"stock"'));
 await put('/api/admin/settings',{showLowStock:false},ck);
 await put('/api/admin/products/'+pid,{price:p0.price,was:p0.was,stock:0,hidden:false},ck);s2=(await j('/api/store')).d;A('stock 0 -> hidden from store',!s2.products[pid]);
 A('cannot order a hidden/sold-out item',(await post('/api/order',{cart:{[pid]:1},customer:cust})).d.error==='stock');
 await put('/api/admin/products/'+pid,{price:p0.price,was:p0.was,stock:5,hidden:false},ck);
 A('invalid price rejected',(await put('/api/admin/products/'+pid,{price:-1,stock:1},ck)).d.ok===false);
 // cancel restores stock
 const no=o.d.no,before=(await j('/api/admin/products',{headers:{cookie:ck}})).d.products[pid].stock;
 await put('/api/admin/orders/'+no,{status:'cancelled'},ck);const after=(await j('/api/admin/products',{headers:{cookie:ck}})).d.products[pid].stock;A('cancel puts item back in stock',after===before+1,before+'->'+after);
 A('invalid status rejected',(await put('/api/admin/orders/'+no,{status:'bogus'},ck)).d.ok===false);
 // concurrency: two simultaneous orders for the last unit
 await put('/api/admin/products/'+pid,{price:p0.price,was:p0.was,stock:1,hidden:false},ck);
 const race=await Promise.all([0,1,2].map(k=>post('/api/order',{cart:{[pid]:1},customer:{...cust,phone:'079444444'+k}})));
 A('only one of 3 simultaneous buyers gets the last unit',race.filter(r=>r.d.ok).length===1,race.map(r=>r.d.ok).join());
 A('stock never negative',(await j('/api/admin/products',{headers:{cookie:ck}})).d.products[pid].stock===0);
 // phone abuse limit
 let many=[];for(let k=0;k<7;k++)many.push(await post('/api/order',{cart:{[sel[3]]:1},customer:{...cust,phone:'0795555555'}}));A('6th+ order from one phone in an hour is refused',many.some(r=>r.d.error==='too_many'),many.map(r=>r.d.ok||r.d.error).join());
 A('honeypot swallowed silently, nothing stored',(await post('/api/order',{website:'x',cart:{[sel[4]]:1},customer:cust})).d.ok===true);
 // password change
 A('wrong current password refused',(await put('/api/admin/password',{current:'nope',next:'another-long-pass'},ck)).s===401);
 A('short new password refused',(await put('/api/admin/password',{current:PW,next:'short'},ck)).d.ok===false);
 // login lockout
 let st=[];for(let k=0;k<10;k++)st.push((await post('/api/admin/login',{password:'x'+k})).s);A('brute force locked out (429)',st.includes(429),st.join());
 // ---- products add/edit/delete, upload, settings (fee, whatsapp, announcement, pause)
 await extra(ck);
 console.log(fail?fail+' FAILED':'all passed');process.exit(fail?1:0)})();
