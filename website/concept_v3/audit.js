/* UX/UI audit: measurable checks on the live prototype. usage: node audit.js [hash] */
const {chromium}=require('playwright');
const url='file://'+process.cwd()+'/index.html';
const lum=c=>{const a=c.map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*a[0]+.7152*a[1]+.0722*a[2]};
(async()=>{
 const b=await chromium.launch(); const out={};
 for(const [name,w,h,mobile] of [['mobile',390,844,true],['desktop',1440,900,false]]){
  const c=await b.newContext({viewport:{width:w,height:h},isMobile:mobile,hasTouch:mobile});const p=await c.newPage();
  const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text().slice(0,120))});
  const t0=Date.now();await p.goto(url+(process.argv[2]?'#'+process.argv[2]:''),{waitUntil:'load'});const loadMs=Date.now()-t0;await p.waitForTimeout(800);
  const r=await p.evaluate((DEVICE_W)=>{
    const vis=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&e.closest('#admin')===null&&e.closest('.drawer')===null};
    const res={};
    // tap targets
    res.small=[...document.querySelectorAll('a[href],button,input,select,textarea,[role=button]')].filter(vis).map(e=>{const r=e.getBoundingClientRect();return{t:(e.innerText||e.getAttribute('aria-label')||e.className||e.tagName).trim().slice(0,28),w:Math.round(r.width),h:Math.round(r.height)}}).filter(x=>x.h<44||x.w<44);
    // fonts
    const small={};document.querySelectorAll('body *').forEach(e=>{if(!vis(e))return;const own=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1);if(!own)return;const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<12){const k=(e.className||e.tagName)+' '+fs;small[k]=(small[k]||0)+1}});
    res.tiny=small;
    // contrast
    const parse=s=>{const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(',').map(Number);return{c:a.slice(0,3),a:a.length>3?a[3]:1}};
    const bgOf=e=>{if(e.closest('.dark'))return [14,12,10];let n=e;const stack=[];while(n){const p=parse(getComputedStyle(n).backgroundColor);if(p&&p.a>0){stack.push(p);if(p.a>=1)break}n=n.parentElement}let base=[255,255,255];stack.reverse().forEach(p=>{base=base.map((v,i)=>Math.round(v*(1-p.a)+p.c[i]*p.a))});return base};
    const L=c=>{const a=c.map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*a[0]+.7152*a[1]+.0722*a[2]};
    const low={};document.querySelectorAll('body *').forEach(e=>{if(!vis(e))return;if(e.closest('.cat'))return;if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1))return;const cs=getComputedStyle(e),fg=parse(cs.color);if(!fg)return;const bg=bgOf(e);const f=fg.c.map((v,i)=>Math.round(v*fg.a+bg[i]*(1-fg.a)));const l1=L(f),l2=L(bg),ratio=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);const fs=parseFloat(cs.fontSize),bold=+cs.fontWeight>=700;const need=(fs>=24||(fs>=18.66&&bold))?3:4.5;if(ratio<need){const k=(e.className||e.tagName)+'|'+cs.color+' on rgb('+bg+')';low[k]=low[k]||{ratio:+ratio.toFixed(2),need,n:0,sample:e.innerText.trim().slice(0,30)};low[k].n++}});
    res.lowContrast=Object.entries(low).map(([k,v])=>({k,...v})).sort((a,b)=>a.ratio-b.ratio);
    res.imgNoAlt=[...document.images].filter(i=>!i.hasAttribute('alt')).length;res.imgEmptyAlt=[...document.images].filter(i=>i.getAttribute('alt')==='').length;res.imgs=document.images.length;
    res.lazy=[...document.images].filter(i=>i.loading==='lazy').length;
    res.h1=[...document.querySelectorAll('h1')].filter(vis).length;res.headings=[...document.querySelectorAll('h1,h2,h3')].filter(vis).map(h=>h.tagName).join('').length;
    res.iconBtnNoLabel=[...document.querySelectorAll('button,a')].filter(vis).filter(e=>!(e.innerText||'').trim()&&!e.getAttribute('aria-label')&&!e.getAttribute('title')&&!e.querySelector('img[alt]:not([alt=""])')&&!e.closest('#mnav')).length;
    res.hrefHash=[...document.querySelectorAll('a[href="#"]')].filter(vis).length;
    res.overflowX=document.documentElement.scrollWidth>DEVICE_W+1;res.docW=document.documentElement.scrollWidth;
    res.lang=document.documentElement.lang+'/'+document.documentElement.dir;
    res.focusRing=(()=>{const s=[...document.styleSheets].flatMap(x=>{try{return[...x.cssRules]}catch{return[]}}).some(r=>r.selectorText&&r.selectorText.includes(':focus-visible'));return s})();
    res.reducedMotion=[...document.styleSheets].flatMap(x=>{try{return[...x.cssRules]}catch{return[]}}).some(r=>r.conditionText&&r.conditionText.includes('prefers-reduced-motion'));
    return res},w);
  // dead controls: click and see if anything changes
  const dead=[];
  for(const sel of ['.tools svg.ic','.menu','.card .ph','.card h3','.brand','.cat','footer li']){
    const el=await p.$(sel);if(!el||!(await el.isVisible()))continue;
    const before=await p.evaluate(()=>location.hash+'|'+document.body.className+'|'+document.querySelector('#drawer').className+'|'+document.querySelectorAll('[role=dialog],.overlay,.mnav.on,.search.on').length);
    const sy=await p.evaluate(()=>scrollY);await el.click({force:true,trial:false}).catch(()=>{});await p.waitForTimeout(250);
    const after=await p.evaluate(()=>location.hash+'|'+document.body.className+'|'+document.querySelector('#drawer').className+'|'+document.querySelectorAll('[role=dialog],.overlay,.mnav.on,.search.on').length);
    const sy2=await p.evaluate(()=>scrollY);if(before===after&&Math.abs(sy2-sy)<5)dead.push(sel);
    await p.evaluate(()=>{location.hash='';scrollTo(0,0)});
  }
  r.deadControls=dead;
  // esc closes drawer?
  await p.evaluate(()=>document.querySelector('#cartbtn').click());await p.waitForTimeout(350);await p.keyboard.press('Escape');await p.waitForTimeout(350);
  r.escClosesDrawer=!(await p.evaluate(()=>document.querySelector('#drawer').classList.contains('on')));
  r.dialogRole=await p.evaluate(()=>document.querySelector('#drawer').getAttribute('role')==='dialog');
  // add-to-cart feedback: does the cart open or offer a path to checkout?
  await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';location.hash='';scrollTo(0,0);document.querySelector('#drawer').classList.remove('on');document.querySelector('#scrim').classList.remove('on')});
  await p.evaluate(()=>document.querySelector('#best .card:nth-child(1) [data-add]').click());await p.waitForTimeout(300);
  r.addOpensCartOrCTA=await p.evaluate(()=>document.querySelector('#drawer').classList.contains('on')||!!document.querySelector('#toast a,#toast button'));
  r.loadMs=loadMs;r.errors=errs;out[name]=r;await c.close();
 }
 // finder results visible after choosing notes (mobile)
 {const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();await p.goto(url,{waitUntil:'load'});await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';document.querySelector('#finder').scrollIntoView()});await p.waitForTimeout(300);
  await p.evaluate(()=>document.querySelector('.nt:nth-child(4)').click());await p.waitForTimeout(300);
  out.mobileFinderResultsInViewport=await p.evaluate(()=>{const r=document.querySelector('#results').getBoundingClientRect();return r.top<innerHeight&&r.bottom>0});
  out.mobileFabShown=await p.evaluate(()=>document.querySelector('#fab').classList.contains('on'));out.mobileFinderResultsDistancePx=await p.evaluate(()=>Math.round(document.querySelector('#results').getBoundingClientRect().top-innerHeight));await c.close()}
 console.log(JSON.stringify(out,null,1));await b.close();
})();
