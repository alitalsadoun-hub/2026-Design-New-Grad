/* ---- dashboard prototype: promotions · orders · brands ---- */
let adTab='promos',editing=null;
const TYPES={percent:'Percentage off',amount_cart:'Fixed amount off the cart',free_delivery:'Free delivery',bxgy:'Buy X, get Y at a discount',bundle:'Bundle price (any N for a fixed price)',tiered:'Spend more, save more',gift:'Free gift with purchase'};
const scopeLabel=s=>!s||s.type==='all'?'all products':s.type==='brand'?'brand: '+(BRANDS[s.value]||{}).name:s.type==='collection'?s.value+' collection':'product: '+((PRODUCTS[s.value]||{}).name||s.value);
function describe(r){const sc=scopeLabel(r.scope);switch(r.type){
 case'percent':return `${r.pct}% off ${sc}${r.minSpend?` · min spend ${r.minSpend} JOD`:''}`;
 case'amount_cart':return `${r.amount} JOD off the cart${r.minSpend?` over ${r.minSpend} JOD`:''}`;
 case'free_delivery':return `Delivery free${r.minSpend?` over ${r.minSpend} JOD`:' on every order'}`;
 case'bxgy':return `Buy ${r.buyQty} get ${r.getQty} at ${r.pct===100?'100% (free)':r.pct+'% off'} · ${sc}${r.repeat?' · repeats':''}`;
 case'bundle':return `Any ${r.qty} for ${r.price} JOD · ${sc}${r.repeat?' · repeats':''}`;
 case'tiered':return `Spend ${r.tiers.map(x=>x.min+'→'+x.pct+'%').join(', ')} · ${sc}`;
 case'gift':return `Free ${(PRODUCTS[r.giftId]||{}).name||'gift'} over ${r.minSpend} JOD`}return''}
function saveRules(){store.set('rules',RULES);renderAnn();renderDrawer()}
function renderAdmin(tab){adTab=tab||adTab;document.querySelectorAll('.ad-top .tabs button').forEach(b=>{b.classList.toggle('on',b.dataset.tab===adTab);b.onclick=()=>{location.hash='admin-'+b.dataset.tab}});
 const el=$('#adbody');if(adTab==='promos')el.innerHTML=promosHtml();else if(adTab==='orders')el.innerHTML=ordersHtml();else el.innerHTML=brandsHtml();
 if(adTab==='promos')bindPromos();if(adTab==='orders')bindOrders()}
function promosHtml(){const list=RULES.map(r=>{const pills=[`<span class="pill">${TYPES[r.type]}</span>`,r.code?`<span class="pill code">CODE ${r.code}</span>`:'',r.stackable?'<span class="pill">stackable</span>':'<span class="pill">best-of</span>',(r.start||r.end)?`<span class="pill">${r.start||'…'} → ${r.end||'…'}</span>`:'',r.maxUses?`<span class="pill">max ${r.maxUses} uses</span>`:'',r.active?'':'<span class="pill off">off</span>'].join('');
  return `<div class="card2"><div><div class="t">${r.name}${r.nameAr?` <span style="color:var(--mute);font-weight:400">· ${r.nameAr}</span>`:''}</div><div class="d">${describe(r)}</div><div style="margin-top:8px">${pills}</div></div><div class="acts"><button class="sw2 ${r.active?'on':''}" data-tg="${r.id}" aria-label="toggle"></button><button class="s" data-ed="${r.id}">Edit</button><button class="s del" data-del="${r.id}">Delete</button></div></div>`}).join('');
 return `<h2>Promotions</h2><p class="hint">Create discounts without touching code. They apply automatically in the cart (or with a code). Delivery is 3 JOD flat; a free-delivery promotion waives it. Prototype: stored in this browser only — the real dashboard saves to the server and re-checks every total at checkout.</p>
 <div class="btnbar"><button class="btn k" id="newp">+ New promotion</button><button class="btn o" id="resetp" style="color:var(--ink)">Reset to samples</button></div>${editing?formHtml():''}${list}`}
function sel(name,opts,val){return `<select name="${name}">${opts.map(([v,l])=>`<option value="${v}" ${String(v)===String(val)?'selected':''}>${l}</option>`).join('')}</select>`}
function scopeVals(type){return type==='brand'?Object.entries(BRANDS).map(([k,v])=>[k,v.name]):type==='collection'?[['niche','Niche'],['selective','Selective']]:type==='product'?Object.values(PRODUCTS).map(p=>[p.id,p.name]):[]}
function formHtml(){const r=editing,sc=r.scope||{type:'all'};
 const f=(l,n,v,ty='text',ph='')=>`<div><label>${l}</label><input name="${n}" type="${ty}" value="${v==null?'':v}" placeholder="${ph}"></div>`;
 let typeFields='';
 if(r.type==='percent')typeFields=f('Discount %','pct',r.pct,'number')+f('Minimum spend (JOD, optional)','minSpend',r.minSpend,'number');
 if(r.type==='amount_cart')typeFields=f('Amount off (JOD)','amount',r.amount,'number')+f('Minimum spend (JOD)','minSpend',r.minSpend,'number');
 if(r.type==='free_delivery')typeFields=f('Minimum spend (JOD, blank = always free)','minSpend',r.minSpend,'number');
 if(r.type==='bxgy')typeFields=f('Customer buys (qty)','buyQty',r.buyQty,'number')+f('Gets (qty)','getQty',r.getQty,'number')+f('Discount on those (%, 100 = free)','pct',r.pct,'number')+`<div class="chk"><input type="checkbox" name="repeat" ${r.repeat?'checked':''}> Repeat for every set in the cart</div>`;
 if(r.type==='bundle')typeFields=f('Items in the bundle','qty',r.qty,'number')+f('Bundle price (JOD)','price',r.price,'number')+`<div class="chk"><input type="checkbox" name="repeat" ${r.repeat?'checked':''}> Repeat for every set in the cart</div>`;
 if(r.type==='tiered')typeFields=`<div class="full">${f('Tiers — "spend:percent", comma separated','tiers',(r.tiers||[]).map(x=>x.min+':'+x.pct).join(', '),'text','80:5, 120:10')}</div>`;
 if(r.type==='gift')typeFields=f('Minimum spend (JOD)','minSpend',r.minSpend,'number')+`<div><label>Gift product</label>${sel('giftId',Object.values(PRODUCTS).map(p=>[p.id,p.name]),r.giftId)}</div>`;
 const noScope=['free_delivery','amount_cart','gift'].includes(r.type);
 return `<form class="form" id="pf"><h3>${r._new?'New promotion':'Edit promotion'}</h3>
  ${f('Name (shown to customers)','name',r.name)}${f('Arabic name (optional)','nameAr',r.nameAr)}
  <div><label>Type</label>${sel('type',Object.entries(TYPES),r.type)}</div>
  ${noScope?'<div></div>':`<div><label>Applies to</label>${sel('scopeType',[['all','All products'],['brand','A brand'],['collection','A collection'],['product','One product']],sc.type)}</div>`}
  ${noScope||sc.type==='all'?'':`<div><label>Which</label>${sel('scopeValue',scopeVals(sc.type),sc.value)}</div>`}
  ${typeFields}
  ${f('Headline shown to customers (EN, optional)','headline',r.headline)}${f('Headline (AR, optional)','headlineAr',r.headlineAr)}${f('Second line (EN, optional)','sub',r.sub)}${f('Second line (AR, optional)','subAr',r.subAr)}
  ${f('Coupon code (leave empty = automatic)','code',r.code,'text','e.g. RAMADAN15')}${f('Max total uses (optional)','maxUses',r.maxUses,'number')}
  ${f('Starts (optional)','start',r.start,'date')}${f('Ends (optional)','end',r.end,'date')}
  <div class="chk"><input type="checkbox" name="stackable" ${r.stackable?'checked':''}> Can combine with other promotions</div><div class="chk"><input type="checkbox" name="active" ${r.active?'checked':''}> Active</div>
  <div class="note">Rules that cannot combine compete: the customer automatically gets the single most generous one. Combinable rules stack in priority order.</div>
  <div class="full btnbar"><button class="btn k" type="submit">Save promotion</button><button class="btn o" type="button" id="cancelp" style="color:var(--ink)">Cancel</button></div></form>`}
function newRule(){return{id:'r'+Date.now(),_new:true,name:'',nameAr:'',type:'percent',pct:10,minSpend:0,active:true,stackable:false,priority:RULES.length+1,scope:{type:'all'}}}
function bindPromos(){
 $('#newp').onclick=()=>{editing=newRule();renderAdmin()};$('#resetp').onclick=()=>{if(confirm('Replace all promotions with the sample set?')){RULES=JSON.parse(JSON.stringify(SEED_RULES));saveRules();editing=null;renderAdmin()}};
 document.querySelectorAll('[data-tg]').forEach(b=>b.onclick=()=>{const r=RULES.find(x=>x.id===b.dataset.tg);r.active=!r.active;saveRules();renderAdmin()});
 document.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{if(confirm('Delete this promotion?')){RULES=RULES.filter(x=>x.id!==b.dataset.del);saveRules();renderAdmin()}});
 document.querySelectorAll('[data-ed]').forEach(b=>b.onclick=()=>{editing=JSON.parse(JSON.stringify(RULES.find(x=>x.id===b.dataset.ed)));renderAdmin()});
 const fm=$('#pf');if(!fm)return;
 const reread=()=>{const d=new FormData(fm),n=k=>d.get(k)===''||d.get(k)==null?undefined:+d.get(k);
  const r={...editing,name:d.get('name'),nameAr:d.get('nameAr'),headline:d.get('headline')||undefined,headlineAr:d.get('headlineAr')||undefined,sub:d.get('sub')||undefined,subAr:d.get('subAr')||undefined,type:d.get('type'),code:(d.get('code')||'').trim()||undefined,maxUses:n('maxUses'),start:d.get('start')||undefined,end:d.get('end')||undefined,stackable:fm.stackable.checked,active:fm.active.checked};
  const st=d.get('scopeType');r.scope=st&&st!=='all'?{type:st,value:d.get('scopeValue')||(scopeVals(st)[0]||[])[0]}:{type:'all'};
  ['pct','minSpend','amount','buyQty','getQty','qty','price'].forEach(k=>{if(d.has(k))r[k]=n(k)});if(fm.repeat)r.repeat=fm.repeat.checked;if(d.has('giftId'))r.giftId=d.get('giftId');
  if(d.has('tiers'))r.tiers=d.get('tiers').split(',').map(s=>s.trim().split(':').map(Number)).filter(a=>a[0]>0&&a[1]>0).map(a=>({min:a[0],pct:a[1]}));return r};
 fm.type.onchange=()=>{const r=reread();const defaults={percent:{pct:10},amount_cart:{amount:5,minSpend:40},free_delivery:{minSpend:60},bxgy:{buyQty:1,getQty:1,pct:50,repeat:true},bundle:{qty:2,price:40,repeat:true},tiered:{tiers:[{min:80,pct:5},{min:120,pct:10}]},gift:{minSpend:100,giftId:'83'}};editing={...r,...defaults[r.type]};renderAdmin()};
 if(fm.scopeType)fm.scopeType.onchange=()=>{const r=reread();editing=r;renderAdmin()};
 $('#cancelp').onclick=()=>{editing=null;renderAdmin()};
 fm.onsubmit=e=>{e.preventDefault();const r=reread();if(!r.name){fm.name.focus();return}delete r._new;const i=RULES.findIndex(x=>x.id===r.id);if(i>=0)RULES[i]=r;else RULES.push(r);saveRules();editing=null;renderAdmin()}}
function ordersHtml(){const os=store.get('orders',[]);if(!os.length)return `<h2>Orders</h2><p class="hint">Every order placed on the store is saved here first, so nothing depends on the customer pressing “send” in WhatsApp. Place a test order on the store to see it appear.</p><div class="empty2">No orders yet.</div>`;
 return `<h2>Orders</h2><p class="hint">Saved on the server in the real build, with an instant e-mail to the shop. “WhatsApp” opens a chat with the customer, message ready.</p><table class="t"><tr><th>Order</th><th>Customer</th><th>Items</th><th>Total</th><th>Status</th></tr>${os.map((o,i)=>`<tr><td><b>${o.no}</b><br><small>${new Date(o.at).toLocaleString()}</small></td><td>${o.customer.name}<br><small>${o.customer.phone}<br>${o.customer.gov} — ${o.customer.address}</small><br><a class="wal" target="_blank" href="${waLink(o.customer.phone,`Hello ${o.customer.name}, this is SCENTRO about your order ${o.no}. We are confirming your details and delivery time.`)}">WhatsApp customer</a></td>
 <td>${o.lines.map(l=>`${PRODUCTS[l.pid].name} × ${l.qty}`).join('<br>')}${o.gifts.map(g=>`<br>${PRODUCTS[g].name} <small>(gift)</small>`).join('')}${o.applied.length?`<br><small style="color:#2F6B3C">${o.applied.map(a=>a.name).join(' · ')}</small>`:''}</td><td><b>${o.total} JOD</b><br><small>delivery ${o.delivery} · cash on delivery</small></td>
 <td><select class="st" data-st="${i}">${['new','confirmed','out for delivery','delivered','cancelled'].map(s=>`<option ${s===o.status?'selected':''}>${s}</option>`).join('')}</select></td></tr>`).join('')}</table>`}
function bindOrders(){document.querySelectorAll('[data-st]').forEach(s=>s.onchange=()=>{const os=store.get('orders',[]);os[+s.dataset.st].status=s.value;store.set('orders',os)})}
function brandsHtml(){const n=b=>Object.values(PRODUCTS).filter(p=>p.brand===b).length;return `<h2>Brands</h2><p class="hint">Scentro is the store; each brand is a record. Products, notes and promotions can target a brand. A Scentro-own label can be added the same way later.</p>
 ${Object.entries(BRANDS).map(([k,b])=>`<div class="card2"><div style="display:flex;gap:14px;align-items:center"><img src="${b.logo}" style="width:48px;height:48px;border-radius:50%" alt=""><div><div class="t">${b.name}</div><div class="d">${n(k)} products in this demo · 96 in the live catalogue</div></div></div><span class="pill">active</span></div>`).join('')}
 <div class="empty2" style="margin-top:12px">+ Add brand — name, logo, description (built in the real dashboard)</div>`}
