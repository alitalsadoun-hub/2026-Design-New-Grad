const O=require('./ordertext.js');let fail=0;const A=(n,c,x)=>{if(!c)fail++;console.log(c?'ok  ':'FAIL',n,c?'':x)};
const o={no:'SC-12345',customer:{name:'علي أحمد',phone:'962791234567',gov:'Balqa (Salt)',address:'السلط، شارع الخندق',note:'اتصل قبل الوصول'},
 lines:[{name:'P102',kind:'selective',orig:'1 Million Lucky',qty:1,net:25},{name:'Daydream Body Mist',kind:'mist',qty:2,net:10}],gifts:[],applied:[{name:'Body mist at half price',amount:10,type:'percent'}],discount:10,delivery:3,total:38};
const full=O.build(o,{greeting:'مرحباً سنترو 👋'}),del=O.delivery(o),parts=full.split('📦 لشركة التوصيل');
A('top part names every product with what it is, quantity and price',/P102 \(سيلكتف — 1 Million Lucky\) × 1 — 25 دينار/.test(parts[0])&&/Daydream Body Mist \(بودي ميست\) × 2 — 10 دينار/.test(parts[0]),parts[0]);
A('top part shows discount, delivery and total incl. delivery',/الخصم: Body mist at half price \(−10\)/.test(parts[0])&&/التوصيل: 3 دينار/.test(parts[0])&&/الإجمالي شامل التوصيل: 38 دينار/.test(parts[0]));
A('delivery block: name, local phone, area, amount incl. delivery',/الاسم: علي أحمد/.test(del)&&/الهاتف: 0791234567/.test(del)&&/المنطقة: البلقاء \(السلط\) — السلط/.test(del)&&/المبلغ شامل التوصيل: 38 دينار/.test(del),del);
A('delivery block has NO product names or codes (the company does not need them)',!/P102|Body Mist|Million/.test(del),del);
A('delivery block is the tail of the full message, ready to copy',full.endsWith(del)&&full.includes('انسخ من هون'));
A('greeting is first',full.startsWith('مرحباً سنترو'));
A('no note -> no note line',!/ملاحظة/.test(O.delivery({...o,customer:{...o.customer,note:''}})));
A('+962 / 962 / 0 phone forms all become 07XXXXXXXX',['962791234567','+962791234567','0791234567','791234567'].every(p=>O.phone(p)==='0791234567'));
A('gift line',/\(هدية\)/.test(O.build({...o,gifts:[{name:'Sun Kiss Body Mist'}]})));
console.log(fail?fail+' FAILED':'all passed');process.exit(fail?1:0)
