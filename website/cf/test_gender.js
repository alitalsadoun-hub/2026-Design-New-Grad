// "For women / men / unisex" filter in the shop + the category block in the phone menu. Local server.
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8788';
const seen=()=>{const d=new Date();localStorage.setItem('scentro_welcome',JSON.stringify(d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')))};
(async()=>{const b=await chromium.launch();let fail=0;const A=(n,c,x='')=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
 for(const [label,hash] of [['mobile EN','#en'],['mobile AR','#ar']]){
  const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});await c.addInitScript(seen);const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto(BASE+'/'+hash,{waitUntil:'networkidle'});await p.waitForTimeout(600);
  const all=await p.evaluate(()=>Object.values(PRODUCTS).filter(x=>!soldOut(x)));
  const cnt=(col,g)=>all.filter(x=>(col==='all'||x.collection===col)&&(g==='all'||x.for===g)).length;
  // 1) shop: pick Selective -> the "for whom" chips appear
  await p.evaluate(()=>{document.querySelector('#filters [data-c=selective]').click()});await p.waitForTimeout(300);
  const chips=await p.evaluate(()=>[...document.querySelectorAll('#gfilters button')].map(b=>b.dataset.g));
  A(label+': after choosing Selective, "all / women / men / unisex" chips appear',chips.join()==='all,her,him,unisex',chips.join());
  await p.screenshot({path:`shots/gender_${label.replace(' ','_')}.png`});
  for(const g of ['her','him','unisex']){
   await p.evaluate(g=>{document.querySelector(`#gfilters [data-g=${g}]`).click()},g);await p.waitForTimeout(250);
   const r=await p.evaluate(()=>({n:Object.keys(PRODUCTS).filter(id=>colV==='all'||PRODUCTS[id].collection===colV).filter(id=>genV==='all'||PRODUCTS[id].for===genV).length,shown:document.querySelectorAll('#best .card').length,wrong:[...document.querySelectorAll('#best .card a[href^="#p-"]')].map(a=>PRODUCTS[a.getAttribute('href').slice(3)]).filter(x=>x&&x.for!==genV).length}));
   A(label+': Selective + '+g+' shows only that ('+cnt('selective',g)+' perfumes)',r.wrong===0&&r.n===cnt('selective',g)&&r.shown===Math.min(12,cnt('selective',g)),JSON.stringify(r));}
  // switching the collection keeps / resets the gender sensibly
  await p.evaluate(()=>{document.querySelector('#gfilters [data-g=him]').click()});await p.waitForTimeout(200);
  await p.evaluate(()=>{document.querySelector('#filters [data-c=mist]').click()});await p.waitForTimeout(250);
  A(label+': Body mist (all unisex) has no "for whom" row and nothing is hidden by the old choice',await p.evaluate(()=>genV==='all'&&document.querySelector('#gfilters').children.length===0&&document.querySelectorAll('#best .card').length>0));
  // 2) the phone menu
  await p.evaluate(()=>{window.scrollTo(0,0)});await p.click('#menubtn');await p.waitForTimeout(500);
  const links=await p.evaluate(()=>[...document.querySelectorAll('#mcats a')].map(a=>a.dataset.mc));
  A(label+': menu lists every collection and women / men / unisex',['col:niche','col:selective','col:mist','gen:her','gen:him','gen:unisex'].every(x=>links.includes(x)),links.join());
  await p.screenshot({path:`shots/menu_${label.replace(' ','_')}.png`});
  await p.click('#mcats a[data-mc="gen:him"]');await p.waitForTimeout(800);
  const m=await p.evaluate(()=>({open:document.querySelector('#mnav').classList.contains('on'),col:colV,gen:genV,n:document.querySelectorAll('#best .card').length,y:Math.round(document.querySelector('#shop').getBoundingClientRect().top)}));
  A(label+': menu "Men" closes the menu and shows every men\'s perfume (all collections)',!m.open&&m.col==='all'&&m.gen==='him'&&m.n===Math.min(12,cnt('all','him')),JSON.stringify(m));
  A(label+': ...and scrolls to the shop',Math.abs(m.y)<300,String(m.y));
  await p.click('#menubtn');await p.waitForTimeout(400);await p.click('#mcats a[data-mc="col:niche"]');await p.waitForTimeout(700);
  A(label+': menu "Niche" shows niche for everyone',await p.evaluate(()=>colV==='niche'&&genV==='all'&&!document.querySelector('#mnav').classList.contains('on')));
  A(label+': no JS errors',errs.length===0,errs.join('|'));await c.close()}
 console.log(fail?fail+' FAILED':'all passed');await b.close();process.exit(fail?1:0)})();
