/* Dumps (1) every distinct note string with the families the page assigns to it, (2) the whole finder run:
   every combination of 1-3 note families x who-for (any/her/him), using the page's REAL code. Output: finder_runs.json */
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage();
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+process.cwd()+'/index.html#en',{waitUntil:'networkidle'});
 const data=await p.evaluate(()=>{
   const notes={};Object.values(PRODUCTS).forEach(pr=>noteItems(pr).forEach(([n])=>{notes[n]=famOf(n)}));
   const fam=FAMILIES.map(f=>f.id);const combos=[];
   const rec=(start,cur)=>{if(cur.length)combos.push([...cur]);if(cur.length===3)return;for(let i=start;i<fam.length;i++){cur.push(fam[i]);rec(i+1,cur);cur.pop()}};rec(0,[]);
   const runs=[];
   for(const c of combos)for(const who of ['any','her','him']){
     picked=c;forV=who;renderResults();
     const cards=[...document.querySelectorAll('#results .res')].map(el=>({id:el.dataset.id,name:el.querySelector('h3').innerText,tier:el.querySelector('.tier').innerText,mt:[...el.querySelectorAll('.mt')].map(e=>e.innerText),shared:[...el.querySelectorAll('.shared em')].map(e=>e.innerText)}));
     const empty=!!document.querySelector('#results .empty');
     runs.push({picked:c,who,empty,cards});
   }
   return {core:Object.fromEntries(FAMILIES.map(f=>[f.id,f.core])),notes,runs,products:Object.fromEntries(Object.values(PRODUCTS).map(pr=>[pr.id,{name:pr.name,coll:pr.collection,for:pr.for,stock:pr.stock,notes:pr.notes||null,key:pr.key||null,acc:pr.acc||null,insp:pr.insp||null}]))};
 });
 fs.writeFileSync('finder_runs.json',JSON.stringify(data));
 console.log('distinct note strings',Object.keys(data.notes).length,'| runs',data.runs.length,'| page errors',errs.length);
 await b.close();
})();
