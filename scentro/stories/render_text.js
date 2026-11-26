// usage: node render_text.js in.html out.png [width height] -> transparent PNG of the page (Arabic shaping + web fonts via Chromium)
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [inp,out,w,h]=process.argv.slice(2);const b=await chromium.launch();const p=await b.newPage({viewport:{width:+w||1080,height:+h||1920}});
await p.setContent(fs.readFileSync(inp,'utf8'),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(700);
await p.screenshot({path:out,omitBackground:true});await b.close()})()
