// SCENTRO store API (Cloudflare Pages Function + D1).
// Public:  GET /api/store · POST /api/order        Admin (cookie session): /api/admin/*
// The server re-prices every order with the SAME promotions engine as the storefront; browser totals are never trusted.
import PromoEngine from '../_lib/engine.js';
import { getSetting, fee, loadRules, usesMap, publicRule, storePayload, loadProductsReal } from '../_lib/store.js';

const GOVS = ['Amman', 'Zarqa', 'Irbid', 'Aqaba', 'Balqa', 'Madaba', 'Karak', 'Jerash', 'Ajloun', 'Mafraq', "Ma'an", 'Tafilah'];
const STATUSES = ['new', 'confirmed', 'out for delivery', 'delivered', 'cancelled'];
const json = (o, status = 200, h = {}) => new Response(JSON.stringify(o), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...h } });
const bad = (msg, status = 400, extra = {}) => json({ ok: false, error: msg, ...extra }, status);
const enc = new TextEncoder();
const b64 = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64 = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
const tse = (a, b) => { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; };

async function pbkdf2(pw, saltB64) {
  const key = await crypto.subtle.importKey('raw', enc.encode(pw), 'PBKDF2', false, ['deriveBits']);
  return b64(await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: unb64(saltB64), iterations: 100000 }, key, 256));
}
async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64(await crypto.subtle.sign('HMAC', key, enc.encode(msg)));
}
async function setSetting(env, k, v) { await env.DB.prepare('INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v').bind(k, v).run(); }
async function adminCreds(env) { // a password changed from the dashboard (stored in D1) wins over the deployment secret
  const salt = await getSetting(env, 'admin_salt'), hash = await getSetting(env, 'admin_hash');
  return salt && hash ? { salt, hash } : { salt: env.ADMIN_SALT, hash: env.ADMIN_HASH };
}
const cookieOf = req => Object.fromEntries((req.headers.get('cookie') || '').split(/;\s*/).filter(Boolean).map(c => { const i = c.indexOf('='); return [c.slice(0, i), c.slice(i + 1)]; }));
async function isAdmin(req, env) {
  const c = cookieOf(req).sc_admin; if (!c || !env.SESSION_SECRET) return false;
  const [exp, sig] = c.split('.'); if (!exp || !sig || +exp < Date.now()) return false;
  const creds = await adminCreds(env);
  return tse(sig, await hmac(env.SESSION_SECRET + (creds.hash || ''), 'admin.' + exp)); // changing the password logs out old sessions
}

// ---------- public: store (never contains stock numbers; see _lib/store.js) ----------
async function store(env) { return json(await storePayload(env)); }

async function coupon(req, env, url) {
  const ip = req.headers.get('cf-connecting-ip') || 'x', now = Date.now(), code = clean(url.searchParams.get('code'), 40).toUpperCase();
  await env.DB.prepare('DELETE FROM attempts WHERE at<?').bind(now - 15 * 60e3).run();
  const n = await env.DB.prepare('SELECT COUNT(*) n FROM attempts WHERE ip=?').bind('c:' + ip).first();
  if (n.n >= 30) return bad('too_many', 429);
  const rule = code && (await loadRules(env)).find(r => r.active && r.code && r.code.trim().toUpperCase() === code);
  const okNow = rule && (!rule.start || new Date() >= new Date(rule.start)) && (!rule.end || new Date() <= new Date(rule.end + 'T23:59:59')) && (!rule.maxUses || (rule._uses || 0) < rule.maxUses);
  if (!okNow) { await env.DB.prepare('INSERT INTO attempts(ip,at) VALUES(?,?)').bind('c:' + ip, now).run(); return json({ ok: false }); }
  return json({ ok: true, rule: publicRule(rule) });
}

// ---------- public: order ----------
const normPhone = p => { p = String(p || '').replace(/\D/g, ''); if (p.startsWith('962')) p = p.slice(3); if (p.startsWith('0')) p = p.slice(1); return p; };
const clean = (s, n) => String(s == null ? '' : s).replace(/[\u0000-\u001f\u007f<>]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, n);
async function order(req, env, ctx) {
  let b; try { b = await req.json(); } catch { return bad('Invalid request'); }
  if (b.website) return json({ ok: true, no: 'SC-00000' }); // honeypot: bots fill hidden fields
  if ((await getSetting(env, 'orders_paused')) === '1') return bad('paused', 503);
  const c = b.customer || {}, name = clean(c.name, 80), address = clean(c.address, 240), note = clean(c.note, 240), gov = GOVS.includes(c.gov) ? c.gov : null;
  const ph = normPhone(c.phone);
  if (name.length < 2) return bad('name');
  if (!/^7[789]\d{7}$/.test(ph)) return bad('phone');
  if (!gov) return bad('gov');
  if (address.length < 5) return bad('address');
  const cartIn = b.cart && typeof b.cart === 'object' ? b.cart : {}, cart = {};
  for (const [pid, q] of Object.entries(cartIn)) { const n = Math.floor(+q); if (n > 0) cart[pid] = Math.min(n, 9); }
  if (!Object.keys(cart).length || Object.keys(cart).length > 30) return bad('cart');
  // light abuse limit: 5 orders per phone per hour
  const since = new Date(Date.now() - 3600e3).toISOString();
  const recent = await env.DB.prepare('SELECT COUNT(*) n FROM orders WHERE phone=? AND at>?').bind(ph, since).first();
  if (recent.n >= 5) return bad('too_many', 429);

  const [products, rules] = await Promise.all([loadProductsReal(env), loadRules(env)]);
  const problems = [];
  for (const [pid, q] of Object.entries(cart)) { const p = products[pid]; if (!p) problems.push({ pid, reason: 'gone' }); else if (p.stock < q) problems.push({ pid, reason: 'stock' }); } // never say how many are left
  if (problems.length) { // over-ordering is the only way to probe quantities: count it and slow it down
    const ip = req.headers.get('cf-connecting-ip') || 'x', now = Date.now();
    await env.DB.prepare('DELETE FROM attempts WHERE at<?').bind(now - 15 * 60e3).run();
    const n = await env.DB.prepare('SELECT COUNT(*) n FROM attempts WHERE ip=?').bind('o:' + ip).first();
    if (n.n >= 12) return bad('too_many', 429);
    await env.DB.prepare('INSERT INTO attempts(ip,at) VALUES(?,?)').bind('o:' + ip, now).run();
    return bad('stock', 409, { problems });
  }
  const code = clean(b.code, 40);
  const q = PromoEngine.price(cart, { products, rules, code, deliveryFee: await fee(env), used: usesMap(rules) });
  // gifts must also be in stock
  for (const g of q.gifts) if (!products[g]) return bad('gift', 409, { problems: [{ pid: g, reason: 'gone' }] });
  const no = 'SC-' + (10000 + Math.floor(Math.random() * 89999));
  const at = new Date().toISOString();
  const data = { customer: { name, phone: '962' + ph, gov, address, note }, lines: q.lines.map(l => ({ pid: l.pid, name: products[l.pid].name, qty: l.qty, unit: l.unit, net: l.net })), gifts: q.gifts.map(g => ({ pid: g, name: products[g].name })), applied: q.applied.map(a => ({ id: a.id, name: a.name, amount: a.amount })), subtotal: q.subtotal, discount: q.discount, delivery: q.delivery, total: q.total, code: q.couponOk ? code : '' };
  const stmts = [env.DB.prepare('INSERT INTO orders(no,at,status,phone,data) VALUES(?,?,?,?,?)').bind(no, at, 'new', ph, JSON.stringify(data))];
  // atomic stock decrement: refuses to go below zero
  const want = { ...cart }; q.gifts.forEach(g => { want[g] = (want[g] || 0) + 1; });
  for (const [pid, n] of Object.entries(want)) stmts.push(env.DB.prepare('UPDATE products SET stock=stock-? WHERE id=? AND stock>=?').bind(n, pid, n));
  for (const a of q.applied) stmts.push(env.DB.prepare('UPDATE rules SET uses=uses+1 WHERE id=?').bind(a.id));
  const res = await env.DB.batch(stmts);
  if (res.slice(1, 1 + Object.keys(want).length).some(r => r.meta.changes === 0)) { // somebody else bought the last one in between: undo
    await env.DB.prepare('DELETE FROM orders WHERE no=?').bind(no).run();
    for (const [i, [pid, n]] of Object.entries(want).entries()) if (res[1 + i].meta.changes) await env.DB.prepare('UPDATE products SET stock=stock+? WHERE id=?').bind(n, pid).run();
    return bad('stock', 409, { problems: [] });
  }
  ctx.waitUntil(notify(env, no, at, data));
  return json({ ok: true, no, at, status: 'new', ...data, gifts: q.gifts });
}

// e-mail to the shop on every new order (hidden from customers). The Resend key is pasted in the dashboard (Settings) and kept in D1 - or set as RESEND_API_KEY.
// The order is saved either way; a mail problem never blocks an order.
async function sendMail(env, subject, text) {
  const key = (await getSetting(env, 'resend_key')) || env.RESEND_API_KEY, to = (await getSetting(env, 'notify_email')) || env.NOTIFY_EMAIL;
  if (!key) return { ok: false, error: 'No e-mail key saved yet' };
  if (!to) return { ok: false, error: 'No e-mail address saved yet' };
  const from = (await getSetting(env, 'mail_from')) || env.MAIL_FROM || 'SCENTRO Orders <onboarding@resend.dev>';
  const r = await fetch('https://api.resend.com/emails', { method: 'POST', headers: { authorization: 'Bearer ' + key, 'content-type': 'application/json' }, body: JSON.stringify({ from, to: [to], subject, text }) });
  let d = {}; try { d = await r.json(); } catch {}
  return r.ok ? { ok: true } : { ok: false, error: d.message || ('Mail service said ' + r.status) };
}
async function notify(env, no, at, d) {
  try {
    const lines = d.lines.map(l => `• ${l.name} × ${l.qty}`).concat(d.gifts.map(g => `• ${g.name} (gift)`)).join('\n');
    await sendMail(env, `New order ${no} — ${d.total} JOD`, `New SCENTRO order ${no}\n\n${lines}\n\nTotal: ${d.total} JOD (cash on delivery, delivery ${d.delivery} JOD)${d.discount ? `\nDiscount: ${d.discount} JOD` : ''}\n\n${d.customer.name}\n+${d.customer.phone}\n${d.customer.gov} — ${d.customer.address}${d.customer.note ? '\nNote: ' + d.customer.note : ''}`);
  } catch (e) { /* never block an order because of mail */ }
}

// ---------- admin ----------
async function login(req, env) {
  const ip = req.headers.get('cf-connecting-ip') || 'x', now = Date.now();
  await env.DB.prepare('DELETE FROM attempts WHERE at<?').bind(now - 15 * 60e3).run();
  const n = await env.DB.prepare('SELECT COUNT(*) n FROM attempts WHERE ip=?').bind(ip).first();
  if (n.n >= 8) return bad('Too many attempts. Try again in 15 minutes.', 429);
  let b; try { b = await req.json(); } catch { return bad('Invalid request'); }
  const creds = await adminCreds(env);
  const ok = creds.hash && tse(await pbkdf2(String(b.password || ''), creds.salt), creds.hash);
  if (!ok) { await env.DB.prepare('INSERT INTO attempts(ip,at) VALUES(?,?)').bind(ip, now).run(); return bad('Wrong password', 401); }
  const exp = now + 14 * 864e5, sig = await hmac(env.SESSION_SECRET + creds.hash, 'admin.' + exp);
  return json({ ok: true }, 200, { 'set-cookie': `sc_admin=${exp}.${sig}; Path=/; Max-Age=${14 * 86400}; HttpOnly; Secure; SameSite=Strict` });
}
async function admin(req, env, path) {
  if (!(await isAdmin(req, env))) return bad('Not signed in', 401);
  const m = req.method, body = async () => { try { return await req.json(); } catch { return {}; } };
  if (path === 'me') return json({ ok: true, notifyEmail: (await getSetting(env, 'notify_email')) || env.NOTIFY_EMAIL || '', mailReady: !!((await getSetting(env, 'resend_key')) || env.RESEND_API_KEY), showLowStock: (await getSetting(env, 'show_low_stock')) === '1', deliveryFee: await fee(env), paused: (await getSetting(env, 'orders_paused')) === '1', wa: (await getSetting(env, 'wa_number')) || '', annEn: (await getSetting(env, 'ann_en')) || '', annAr: (await getSetting(env, 'ann_ar')) || '' });
  if (path === 'test-mail' && m === 'POST') return json(await sendMail(env, 'SCENTRO test e-mail', 'If you can read this, new orders will reach you by e-mail.'));
  if (path === 'logout') return json({ ok: true }, 200, { 'set-cookie': 'sc_admin=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict' });
  if (path === 'products' && m === 'GET') return json({ ok: true, products: await loadProductsReal(env, { all: true }) });
  if (path === 'upload' && m === 'POST') { // product photo: the browser resizes it first; stored in KV, served from /img/u/...
    const b = await body(), mm = /^data:(image\/(webp|jpeg|png));base64,([A-Za-z0-9+/=]+)$/.exec(String(b.data || '')); if (!mm) return bad('Please choose a JPG, PNG or WebP image');
    const bytes = Uint8Array.from(atob(mm[3]), c => c.charCodeAt(0)); if (bytes.length > 1.5e6) return bad('Image is too large (max 1.5 MB after resizing)');
    const ext = mm[2] === 'jpeg' ? 'jpg' : mm[2], key = `img/u/${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}.${ext}`;
    await env.ASSETS_KV.put(key, bytes, { metadata: { type: mm[1] } }); return json({ ok: true, path: key });
  }
  if (path === 'products' && m === 'POST') {
    const b = await body(), r = cleanProduct(b); if (r.error) return bad(r.error);
    const id = 'n' + Date.now().toString(36), pos = (await env.DB.prepare('SELECT COALESCE(MIN(pos),0)-1 p FROM products').first()).p; // new items first
    await env.DB.prepare('INSERT INTO products(id,data,price,was,stock,hidden,pos) VALUES(?,?,?,?,?,?,?)').bind(id, JSON.stringify(r.data), r.price, r.was, r.stock, b.hidden ? 1 : 0, pos).run();
    return json({ ok: true, id });
  }
  if (path.startsWith('products/') && m === 'DELETE') { await env.DB.prepare('DELETE FROM products WHERE id=?').bind(path.slice(9)).run(); return json({ ok: true }); }
  if (path.startsWith('products/') && m === 'PUT' && (await peekFull(req))) {
    const id = path.slice(9), cur = await env.DB.prepare('SELECT data FROM products WHERE id=?').bind(id).first(); if (!cur) return bad('not found', 404);
    const b = await body(), r = cleanProduct(b, JSON.parse(cur.data)); if (r.error) return bad(r.error);
    await env.DB.prepare('UPDATE products SET data=?,price=?,was=?,stock=?,hidden=? WHERE id=?').bind(JSON.stringify(r.data), r.price, r.was, r.stock, b.hidden ? 1 : 0, id).run(); return json({ ok: true });
  }
  if (path.startsWith('products/') && m === 'PUT') {
    const id = path.slice(9), b = await body(), p = await env.DB.prepare('SELECT id FROM products WHERE id=?').bind(id).first(); if (!p) return bad('not found', 404);
    const stock = Math.max(0, Math.floor(+b.stock)), price = +b.price, was = b.was === '' || b.was == null ? null : +b.was;
    if (!isFinite(stock) || !(price > 0) || (was != null && !(was > 0))) return bad('invalid values');
    await env.DB.prepare('UPDATE products SET stock=?,price=?,was=?,hidden=? WHERE id=?').bind(stock, price, was, b.hidden ? 1 : 0, id).run();
    return json({ ok: true });
  }
  if (path === 'rules' && m === 'GET') return json({ ok: true, rules: (await loadRules(env)).map(r => ({ ...publicRule(r), _uses: r._uses })) });
  if (path === 'rules' && m === 'PUT') {
    const b = await body(); if (!Array.isArray(b.rules) || b.rules.length > 200) return bad('invalid');
    const cur = Object.fromEntries((await loadRules(env)).map(r => [r.id, r._uses]));
    const stmts = [env.DB.prepare('DELETE FROM rules')];
    b.rules.forEach((r, i) => { const { _uses, _new, ...x } = r; if (!x.id || !x.type) return; stmts.push(env.DB.prepare('INSERT INTO rules(id,data,uses,pos) VALUES(?,?,?,?)').bind(String(x.id), JSON.stringify(x), cur[x.id] || 0, i)); });
    await env.DB.batch(stmts); return json({ ok: true });
  }
  if (path === 'orders' && m === 'GET') {
    const rows = (await env.DB.prepare('SELECT no,at,status,data FROM orders ORDER BY id DESC LIMIT 300').all()).results;
    return json({ ok: true, orders: rows.map(r => ({ no: r.no, at: r.at, status: r.status, ...JSON.parse(r.data) })) });
  }
  if (path.startsWith('orders/') && m === 'PUT') {
    const no = path.slice(7), b = await body(); if (!STATUSES.includes(b.status)) return bad('invalid status');
    const o = await env.DB.prepare('SELECT status,data FROM orders WHERE no=?').bind(no).first(); if (!o) return bad('not found', 404);
    const stmts = [env.DB.prepare('UPDATE orders SET status=? WHERE no=?').bind(b.status, no)];
    // cancelling puts the stock back; un-cancelling takes it again (refuses if not enough)
    if (o.status !== 'cancelled' && b.status === 'cancelled') { const d = JSON.parse(o.data); [...d.lines.map(l => [l.pid, l.qty]), ...d.gifts.map(g => [g.pid, 1])].forEach(([pid, n]) => stmts.push(env.DB.prepare('UPDATE products SET stock=stock+? WHERE id=?').bind(n, pid))); }
    if (o.status === 'cancelled' && b.status !== 'cancelled') { const d = JSON.parse(o.data); [...d.lines.map(l => [l.pid, l.qty]), ...d.gifts.map(g => [g.pid, 1])].forEach(([pid, n]) => stmts.push(env.DB.prepare('UPDATE products SET stock=MAX(0,stock-?) WHERE id=?').bind(n, pid))); }
    await env.DB.batch(stmts); return json({ ok: true });
  }
  if (path === 'settings' && m === 'PUT') { const b = await body(); if (b.resendKey) { const k = clean(b.resendKey, 200); if (!/^re_[A-Za-z0-9_\-]{10,}$/.test(k)) return bad('That does not look like a Resend key (it starts with re_)'); await setSetting(env, 'resend_key', k); } if (b.showLowStock != null) await setSetting(env, 'show_low_stock', b.showLowStock ? '1' : '0');
    if (b.paused != null) await setSetting(env, 'orders_paused', b.paused ? '1' : '0');
    if (b.deliveryFee != null) { const v = parseFloat(b.deliveryFee); if (!isFinite(v) || v < 1 || v > 50) return bad('Delivery fee must be between 1 and 50 JOD (use a free-delivery offer to waive it)'); await setSetting(env, 'delivery_fee', String(v)); }
    if (b.wa != null) { const d = String(b.wa).replace(/\D/g, ''); if (d && !/^962 ?7[789]\d{7}$/.test(d)) return bad('WhatsApp number must be a Jordanian mobile, e.g. 962797906211'); await setSetting(env, 'wa_number', d); }
    if (b.annEn != null) await setSetting(env, 'ann_en', clean(b.annEn, 90));
    if (b.annAr != null) await setSetting(env, 'ann_ar', clean(b.annAr, 90)); if (b.notifyEmail != null) { const e = clean(b.notifyEmail, 120); if (e && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e)) return bad('invalid email'); await setSetting(env, 'notify_email', e); } return json({ ok: true }); }
  if (path === 'password' && m === 'PUT') {
    const b = await body(), creds = await adminCreds(env);
    if (!creds.hash || !tse(await pbkdf2(String(b.current || ''), creds.salt), creds.hash)) return bad('Current password is wrong', 401);
    if (String(b.next || '').length < 10) return bad('New password must be at least 10 characters');
    const salt = b64(crypto.getRandomValues(new Uint8Array(16)));
    await setSetting(env, 'admin_salt', salt); await setSetting(env, 'admin_hash', await pbkdf2(b.next, salt));
    return json({ ok: true }, 200, { 'set-cookie': 'sc_admin=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict' });
  }
  return bad('not found', 404);
}

// ---------- product validation (add / edit from the dashboard) ----------
const list = (v, n = 12) => (Array.isArray(v) ? v : String(v || '').split(/[,،\n]/)).map(x => clean(x, 40)).filter(Boolean).slice(0, n);
function cleanProduct(b, old = {}) {
  const name = clean(b.name, 60), coll = ['niche', 'selective', 'mist'].includes(b.collection) ? b.collection : null, who = ['her', 'him', 'unisex'].includes(b.for) ? b.for : null;
  const ml = Math.floor(+b.ml), price = +b.price, was = b.was === '' || b.was == null ? null : +b.was, stock = Math.max(0, Math.floor(+b.stock || 0));
  if (name.length < 1) return { error: 'Name is required' }; if (!coll) return { error: 'Choose a collection' }; if (!who) return { error: 'Choose who it is for' };
  if (!(ml > 0 && ml < 2000)) return { error: 'Size in ml is required' }; if (!(price > 0 && price < 10000)) return { error: 'Price is required' }; if (was != null && !(was > 0)) return { error: 'Price before discount is not valid' };
  const img = String(b.img || old.img || ''); if (!/^img\/[A-Za-z0-9_\-\/]+\.(webp|jpg|png)$/.test(img)) return { error: 'Please add a product photo' };
  const d = { ...old, brand: old.brand || 'mad', collection: coll, img, for: who, name, ml };
  const top = list(b.top), heart = list(b.heart), base = list(b.base);
  if (top.length || heart.length || base.length) d.notes = { top, heart, base }; else delete d.notes;
  const key = list(b.key, 6); if (key.length) d.key = key; else delete d.key;
  if (b.acc !== undefined) { const acc = list(b.acc, 10); if (acc.length) d.acc = acc; else delete d.acc; } // scent character words (optional)
  const house = clean(b.house, 60), orig = clean(b.original, 60); if (orig) d.insp = { house, original: orig, confirmed: true }; else delete d.insp;
  delete d.placeholder; return { data: d, price, was, stock };
}
// a PUT that edits the whole product (has a name) vs the quick price/stock row save
async function peekFull(req) { try { const b = await req.clone().json(); return typeof b.name === 'string'; } catch { return false; } }

export async function onRequest({ request, env, params, waitUntil }) {
  const path = (Array.isArray(params.path) ? params.path : [params.path]).join('/'), m = request.method;
  try {
    if (path === 'store' && m === 'GET') return await store(env);
    if (path === 'coupon' && m === 'GET') return await coupon(request, env, new URL(request.url));
    if (path === 'order' && m === 'POST') return await order(request, env, { waitUntil });
    if (path === 'admin/login' && m === 'POST') return await login(request, env);
    if (path.startsWith('admin/')) {
      if (m !== 'GET' && !(request.headers.get('content-type') || '').includes('application/json')) return bad('bad content type', 415); // CSRF guard on top of SameSite
      return await admin(request, env, path.slice(6));
    }
    return bad('not found', 404);
  } catch (e) { return bad('server error', 500); }
}
