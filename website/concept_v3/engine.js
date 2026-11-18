/* SCENTRO promotions engine (pure functions, no DOM).  Same code will run on the server at checkout (never trust the browser's totals).
 *
 * rule = { id, name, type, active, code?, start?, end?, stackable, priority, maxUses?, scope:{type:'all|brand|collection|product',value}, ...params }
 * types:
 *   percent        pct, minSpend          % off the items in scope
 *   amount_cart    amount, minSpend       fixed JOD off the cart
 *   free_delivery  minSpend               delivery fee waived
 *   bxgy           buyQty, getQty, pct, repeat   buy N, get M of the cheapest at pct% off (100 = free)
 *   bundle         qty, price, repeat     any `qty` items in scope for a fixed price
 *   tiered         tiers:[{min,pct}]      spend more, save more
 *   gift           minSpend, giftId       free gift product above a spend
 */
(function (root) {
  const r2 = n => Math.round(n * 100) / 100;
  const inScope = (p, s) => !s || s.type === 'all' || (s.type === 'brand' && p.brand === s.value) || (s.type === 'collection' && p.collection === s.value) || (s.type === 'product' && String(p.id) === String(s.value));
  const live = (rule, now, code, used) => {
    if (!rule.active) return false;
    if (rule.start && now < new Date(rule.start)) return false;
    if (rule.end && now > new Date(rule.end + 'T23:59:59')) return false;
    if (rule.code && (!code || code.trim().toUpperCase() !== rule.code.trim().toUpperCase())) return false;
    if (rule.maxUses && (used[rule.id] || 0) >= rule.maxUses) return false;
    return true;
  };
  // each unit: {pid, price, disc}; helpers work on the remaining price (price - disc)
  const rem = u => u.price - u.disc;
  function applyRule(rule, st) {
    const units = st.units, sc = u => inScope(st.products[u.pid], rule.scope);
    let amount = 0, delivery = null, gift = null;
    const spend = list => list.reduce((a, u) => a + rem(u), 0);
    const take = (u, d) => { d = Math.min(d, rem(u)); u.disc += d; amount += d; };
    switch (rule.type) {
      case 'percent': { const L = units.filter(sc); if (spend(L) >= (rule.minSpend || 0)) L.forEach(u => take(u, rem(u) * rule.pct / 100)); break; }
      case 'amount_cart': { const t = spend(units); if (t >= (rule.minSpend || 0) && t > 0) { const d = Math.min(rule.amount, t); units.forEach(u => take(u, d * rem(u) / t)); } break; }
      case 'free_delivery': { if (spend(units) >= (rule.minSpend || 0)) delivery = 0; break; }
      case 'bxgy': {
        const L = units.filter(sc).sort((a, b) => rem(b) - rem(a)), size = rule.buyQty + rule.getQty;
        for (let i = 0; i + size <= L.length; i += size) {
          L.slice(i + rule.buyQty, i + size).forEach(u => take(u, rem(u) * rule.pct / 100));
          if (!rule.repeat) break;
        }
        break;
      }
      case 'bundle': {
        const L = units.filter(sc).sort((a, b) => rem(b) - rem(a));
        for (let i = 0; i + rule.qty <= L.length; i += rule.qty) {
          const g = L.slice(i, i + rule.qty), tot = spend(g);
          if (tot > rule.price) g.forEach(u => take(u, (tot - rule.price) * rem(u) / tot));
          if (!rule.repeat) break;
        }
        break;
      }
      case 'tiered': {
        const L = units.filter(sc), t = spend(L), tier = [...rule.tiers].sort((a, b) => b.min - a.min).find(x => t >= x.min);
        if (tier) L.forEach(u => take(u, rem(u) * tier.pct / 100));
        break;
      }
      case 'gift': { if (spend(units) >= (rule.minSpend || 0) && st.products[rule.giftId]) gift = rule.giftId; break; }
    }
    return { amount: r2(amount), delivery, gift };
  }
  function nudge(rule, st, subtotal) {
    const need = (min) => Math.max(0, r2(min - subtotal));
    if (rule.type === 'free_delivery' && st.delivery !== 0 && need(rule.minSpend) > 0) return { rule: rule.id, kind: 'free_delivery', need: need(rule.minSpend), target: rule.minSpend };
    if (rule.type === 'gift' && !st.gifts.includes(rule.giftId) && need(rule.minSpend) > 0) return { rule: rule.id, kind: 'gift', need: need(rule.minSpend), target: rule.minSpend, giftId: rule.giftId };
    if (rule.type === 'tiered') { const next = [...rule.tiers].sort((a, b) => a.min - b.min).find(x => x.min > subtotal); if (next) return { rule: rule.id, kind: 'tier', need: need(next.min), target: next.min, pct: next.pct }; }
    return null;
  }
  /* price(cart, ctx) -> {lines,gifts,applied,subtotal,discount,delivery,deliveryFee,total,nudges,couponOk}
     cart: {pid: qty}; ctx: {products, rules, code, now, deliveryFee, used} */
  function price(cart, ctx) {
    const now = ctx.now || new Date(), used = ctx.used || {}, fee = ctx.deliveryFee == null ? 3 : ctx.deliveryFee;
    const units = [];
    Object.entries(cart).forEach(([pid, q]) => { for (let i = 0; i < q; i++) units.push({ pid, price: ctx.products[pid].price, disc: 0 }); });
    const subtotal = r2(units.reduce((a, u) => a + u.price, 0));
    const st = { units, products: ctx.products, delivery: fee, gifts: [] };
    const applied = [];
    const eligible = ctx.rules.filter(r => live(r, now, ctx.code, used));
    const couponOk = !!(ctx.code && ctx.rules.some(r => r.code && r.code.trim().toUpperCase() === ctx.code.trim().toUpperCase() && live(r, now, ctx.code, used)));
    // 1) exclusive rules: only the single most generous one applies
    const excl = eligible.filter(r => !r.stackable && r.type !== 'free_delivery' && r.type !== 'gift');
    let best = null;
    excl.forEach(r => { const sim = { ...st, units: units.map(u => ({ ...u })) }; const res = applyRule(r, sim); if (res.amount > (best ? best.amount : 0)) best = { r, amount: res.amount }; });
    const order = [...(best ? [best.r] : []), ...eligible.filter(r => r.stackable && r.type !== 'free_delivery' && r.type !== 'gift').sort((a, b) => (a.priority || 0) - (b.priority || 0))];
    order.forEach(r => { const res = applyRule(r, st); if (res.amount > 0) applied.push({ id: r.id, name: r.name, amount: res.amount, type: r.type }); });
    // 2) delivery + gifts are judged on the discounted subtotal
    const after = r2(units.reduce((a, u) => a + rem(u), 0));
    eligible.filter(r => r.type === 'free_delivery' || r.type === 'gift').forEach(r => {
      const res = applyRule(r, st);
      if (res.delivery === 0) { st.delivery = 0; applied.push({ id: r.id, name: r.name, amount: fee, type: r.type, delivery: true }); }
      if (res.gift) { st.gifts.push(res.gift); applied.push({ id: r.id, name: r.name, amount: ctx.products[res.gift].price, type: 'gift', gift: res.gift }); }
    });
    const lines = Object.entries(cart).map(([pid, q]) => { const mine = units.filter(u => u.pid === pid); const d = r2(mine.reduce((a, u) => a + u.disc, 0)); return { pid, qty: q, unit: ctx.products[pid].price, gross: r2(ctx.products[pid].price * q), discount: d, net: r2(ctx.products[pid].price * q - d) }; });
    const nudges = eligible.concat(ctx.rules.filter(r => r.active && !live(r, now, ctx.code, used) && !r.code && false)).map(r => nudge(r, st, after)).filter(Boolean);
    const discount = r2(subtotal - after), delivery = Object.keys(cart).length ? st.delivery : 0;
    return { lines, gifts: st.gifts, applied, subtotal, discount, delivery, deliveryFee: fee, total: r2(after + delivery), nudges, couponOk };
  }
  const api = { price, inScope, r2 };
  if (typeof module !== 'undefined') module.exports = api; else root.PromoEngine = api;
})(typeof window !== 'undefined' ? window : globalThis);
