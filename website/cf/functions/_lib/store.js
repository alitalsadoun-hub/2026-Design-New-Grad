// Shared server code: settings, rules, products and the PUBLIC store payload.
// PRIVACY RULE: the public payload NEVER contains stock numbers. A product is either present (in stock) or absent (sold out / switched off).
// Browsers only ever learn two things about quantity: (1) an optional `low` (1-3) when the owner turned on "Only N left", (2) a relative display rank `r`
// so that perfumes with more pieces are listed first. Real quantities exist only on the server and in the password-protected dashboard.
const DEFAULT_FEE = 3;
export async function getSetting(env, k) { const r = await env.DB.prepare('SELECT v FROM settings WHERE k=?').bind(k).first(); return r ? r.v : null; }
export async function fee(env) { const v = parseFloat(await getSetting(env, 'delivery_fee')); return isFinite(v) && v >= 1 && v <= 50 ? Math.round(v * 100) / 100 : DEFAULT_FEE; }
export async function loadRules(env) {
  return (await env.DB.prepare('SELECT id,data,uses FROM rules ORDER BY pos,id').all()).results.map(r => ({ ...JSON.parse(r.data), id: r.id, _uses: r.uses }));
}
export const usesMap = rules => Object.fromEntries(rules.map(r => [r.id, r._uses || 0]));
export const publicRule = r => { const { _uses, ...x } = r; return x; };
// real quantities: used by the order check and the admin dashboard only, never sent to the storefront
export async function loadProductsReal(env, { all = false } = {}) {
  const rows = (await env.DB.prepare('SELECT id,data,price,was,stock,hidden,pos FROM products ORDER BY pos,id').all()).results;
  const out = {};
  for (const r of rows) { if (!all && (r.hidden || r.stock <= 0)) continue; out[r.id] = { ...JSON.parse(r.data), id: r.id, price: r.price, was: r.was, stock: r.stock, hidden: !!r.hidden }; }
  return out;
}
export async function popupCfg(env) { const on = await getSetting(env, 'popup_on'), end = await getSetting(env, 'popup_end'); return { on: on !== '0', end: /^\d{4}-\d{2}-\d{2}$/.test(end || '') ? end : '2026-11-30' }; }
export async function storePayload(env) {
  const rows = (await env.DB.prepare('SELECT id,data,price,was,stock,hidden,pos FROM products ORDER BY pos,id').all()).results;
  const hints = (await getSetting(env, 'show_low_stock')) === '1';
  const live = rows.filter(r => !r.hidden && r.stock > 0);
  // display order: plenty in stock first (more pieces = earlier); the last few pieces (1-4) always at the end
  const score = r => (r.stock >= 5 ? r.stock : r.stock - 100);
  const ordered = [...live].sort((a, b) => score(b) - score(a) || a.pos - b.pos);
  const products = {};
  ordered.forEach((r, i) => { const p = { ...JSON.parse(r.data), id: r.id, price: r.price, was: r.was, r: i }; if (hints && r.stock <= 3) p.low = r.stock; products[r.id] = p; });
  // coupon codes are secrets: only automatic (code-less) active offers are public; a code is checked on the server (GET /api/coupon)
  const pub = (await loadRules(env)).filter(r => r.active && !r.code);
  return { ok: true, products, rules: pub.map(publicRule), uses: usesMap(pub), deliveryFee: await fee(env), lowStock: hints, paused: (await getSetting(env, 'orders_paused')) === '1', wa: (await getSetting(env, 'wa_number')) || '', annEn: (await getSetting(env, 'ann_en')) || '', annAr: (await getSetting(env, 'ann_ar')) || '', popup: await popupCfg(env) };
}
