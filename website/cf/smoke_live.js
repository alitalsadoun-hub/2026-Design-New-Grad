// Read-mostly smoke test of the LIVE site: loads the store in a browser, signs in to the dashboard, places ONE test order, checks it, cancels it (stock goes back) and deletes it.
// usage: PW='<dashboard password>' BASE=https://scentro.pages.dev node smoke_live.js
const {chromium}=require('playwright');const cp=require('child_process');const BASE=process.env.BASE||'https://scentro.pages.dev',PW=process.env.PW;
(async()=>{let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
 const b=await chromium.launch();
 const login=await fetch(BASE+'/api/admin/login',{method:'POST',headers:{'content-type':'application/json','x-admin':process.env.AT},body:JSON.stringify({password:PW})});A('live: dashboard login',login.ok);const ck=login.headers.get('set-cookie').split(';')[0];
 const ad=(p,m='GET',body)=>fetch(BASE+'/api/admin/'+p,{method:m,headers:{'content-type':'application/json',cookie:ck,'x-admin':process.env.AT},body:body&&JSON.stringify(body)}).then(r=>r.json());
 const store=(await (await fetch(BASE+'/api/store')).json());const sel=Object.values(store.products).filter(p=>p.collection==='selective')[0];const stock0=(await ad('products')).products[sel.id].stock;
 for(const [label,vp,mobile,hash] of [['desktop EN',{width:1440,height:900},false,'#en'],['mobile AR',{width:390,height:844},true,'#ar']]){
  const c=await b.newContext({viewport:vp,isMobile:mobile,hasTouch:mobile});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto(BASE+'/'+hash,{waitUntil:'networkidle'});await p.waitForTimeout(800);
  A(label+': live page runs in server mode',await p.evaluate(()=>SERVER===true));
  A(label+': all product images load',await p.evaluate(async()=>{const imgs=[...document.images].filter(i=>i.src&&i.loading!=='lazy');return imgs.every(i=>i.complete&&i.naturalWidth>0)}));
  await p.screenshot({path:`shots/live_home_${label.replace(' ','_')}.png`});A(label+': no JS errors',errs.length===0,errs.join('|'));await c.close()}
 // one real order through the API, then clean up
 const o=await fetch(BASE+'/api/order',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({cart:{[sel.id]:1},customer:{name:'SMOKE TEST',phone:'0770000000',gov:'Amman',address:'smoke test - please ignore'}})}).then(r=>r.json());
 A('live: order accepted',o.ok&&o.total===sel.price+3,JSON.stringify(o));
 let orders=(await ad('orders')).orders;A('live: order visible in dashboard',orders.some(x=>x.no===o.no));
 A('live: stock decreased',(await ad('products')).products[sel.id].stock===stock0-1);
 await ad('orders/'+o.no,'PUT',{status:'cancelled'});A('live: cancel restores stock',(await ad('products')).products[sel.id].stock===stock0);
 cp.execSync(`npx wrangler d1 execute scentro-db --remote --command="DELETE FROM orders WHERE no='${o.no}'" `,{stdio:'ignore',env:{...process.env,CLOUDFLARE_API_TOKEN:'proxy-injected',CLOUDFLARE_ACCOUNT_ID:'35b4aa5bf1b0886b5b4313e13f17441d'}});
 A('live: test order removed',!(await ad('orders')).orders.some(x=>x.no===o.no));
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
