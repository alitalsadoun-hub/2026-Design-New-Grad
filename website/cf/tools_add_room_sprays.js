// Adds the MAD Room Spray 250 ml collection to the LIVE store through the dashboard API (idempotent: skips names that already exist).
// usage: BASE=https://scentrojo.com AT=<secret address token> PW=<dashboard password> node tools_add_room_sprays.js
const fs=require('fs'),path=require('path');const BASE=process.env.BASE,AT=process.env.AT,PW=process.env.PW;const D=path.join(__dirname,'..','data');
(async()=>{const cfg=JSON.parse(fs.readFileSync(path.join(D,'room_sprays.json'),'utf8'));
 const lg=await fetch(BASE+'/api/admin/login',{method:'POST',headers:{'content-type':'application/json','x-admin':AT},body:JSON.stringify({password:PW})});const ck=lg.headers.get('set-cookie').split(';')[0];
 const api=(p,m,b)=>fetch(BASE+'/api/admin/'+p,{method:m||'GET',headers:{'content-type':'application/json',cookie:ck,'x-admin':AT},body:b&&JSON.stringify(b)}).then(r=>r.json());
 const have=Object.values((await api('products')).products).map(p=>p.name);
 for(const p of cfg.products){if(have.includes(p.name)){console.log('exists',p.name);continue}
  const data='data:image/webp;base64,'+fs.readFileSync(path.join(D,'room_sprays',p.file+'.webp')).toString('base64');const up=await api('upload','POST',{data});if(!up.ok){console.log('upload failed',p.name,up);continue}
  const r=await api('products','POST',{name:p.name,collection:'room',for:'unisex',ml:cfg.ml,price:cfg.price,stock:p.stock,img:up.path,top:p.top,heart:p.heart,base:p.base});console.log(r.ok?'added':'FAILED',p.name,r.id||r.error)}
 const rules=(await api('rules')).rules;if(!rules.some(r=>r.id==='room50')){const room={id:'room50',name:'Room spray at half price',nameAr:'سبراي غرف بنصف السعر',type:'percent',pct:50,scope:{type:'collection',value:'room'},requires:[{type:'collection',value:'niche'},{type:'collection',value:'selective'}],quiet:true,active:true,stackable:true,priority:1};
  const r=await api('rules','PUT',{rules:[room,...rules.map(x=>{const y={...x};delete y._uses;return y})]});console.log('rule room50',r.ok?'added':'FAILED')}else console.log('rule room50 exists')})()
