/* SCENTRO order message - ONE format used everywhere: the e-mail to the shop, the WhatsApp text the customer sends, and the dashboard "copy" buttons.
 * Top part  = what the owner needs to understand the order (product name, what it is, quantity, prices).
 * Bottom part = a short block to copy-paste to the delivery company: name, phone, area, amount to collect INCLUDING delivery.
 * order = { no, customer:{name,phone,gov,address,note}, lines:[{name,kind,orig,qty,net}], gifts:[{name}], applied:[{name,amount}], discount, delivery, total } */
(function (root) {
  const KIND = { niche: 'نيش', selective: 'سيلكتف', mist: 'بودي ميست', room: 'سبراي غرف' };
  const GOV_AR = { 'Amman': 'عمّان', 'Zarqa': 'الزرقاء', 'Irbid': 'إربد', 'Aqaba': 'العقبة', 'Balqa': 'البلقاء', 'Balqa (Salt)': 'البلقاء (السلط)', 'Madaba': 'مادبا', 'Karak': 'الكرك', 'Jerash': 'جرش', 'Ajloun': 'عجلون', 'Mafraq': 'المفرق', "Ma'an": 'معان', 'Tafilah': 'الطفيلة' };
  const n = v => (Math.round(v * 100) / 100).toString();
  const phone = p => { const d = String(p || '').replace(/\D/g, '').replace(/^962/, ''); return '0' + d.replace(/^0/, ''); };
  const area = c => (GOV_AR[c.gov] || c.gov) + (c.address ? ' — ' + c.address : '');
  const LINE = '━━━━━━━━━━━━';
  // the part to copy for the delivery company (also used alone by the dashboard "copy for delivery" button)
  function delivery(o) {
    const c = o.customer;
    return ['الاسم: ' + c.name, 'الهاتف: ' + phone(c.phone), 'المنطقة: ' + area(c), ...(c.note ? ['ملاحظة: ' + c.note] : []), 'المبلغ شامل التوصيل: ' + n(o.total) + ' دينار'].join('\n');
  }
  function build(o, opts) {
    opts = opts || {};
    const items = o.lines.map(l => `• ${l.name}${KIND[l.kind] || l.orig ? ' (' + [KIND[l.kind], l.orig].filter(Boolean).join(' — ') + ')' : ''} × ${l.qty} — ${n(l.net)} دينار`)
      .concat((o.gifts || []).map(g => `• ${g.name} (هدية) × 1 — 0 دينار`));
    const disc = (o.applied || []).filter(a => !a.delivery && a.type !== 'gift').map(a => `${a.name} (−${n(a.amount)})`);
    return [
      (opts.greeting ? opts.greeting + '\n' : '') + '🛍 طلب جديد ' + o.no,
      '', 'الطلب:', ...items,
      ...(disc.length ? ['الخصم: ' + disc.join(' · ')] : []),
      'التوصيل: ' + n(o.delivery) + ' دينار',
      'الإجمالي شامل التوصيل: ' + n(o.total) + ' دينار (الدفع عند الاستلام)',
      '', LINE, '📦 لشركة التوصيل (انسخ من هون):', delivery(o)
    ].join('\n');
  }
  const api = { build, delivery, phone, area, KIND, GOV_AR };
  if (typeof module !== 'undefined') module.exports = api; else root.OrderText = api;
})(typeof window !== 'undefined' ? window : globalThis);
