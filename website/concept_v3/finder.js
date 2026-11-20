/* SCENTRO "find by notes": ranking core (pure, no DOM) - used by the page and by finder_test.js.
 *
 * Every perfume is reduced to evidence items [note, weight]:
 *   heart / base notes = 1.0 · top notes = 0.6 · key notes of the original = 1.0 · accords (community-voted character) = 0.8
 * A note belongs to one or more scent families via the audited dictionary (data/note_families.json).
 * For every family the customer picked we add up the evidence:  strength >= 1  -> "solid",  0 < strength < 1 -> "light".
 * cover = sum over picked families of min(1, strength).  A perfume is only offered if cover >= 0.6 (some real link),
 * and ranked by cover, then number of solid families, then HEADLINE notes (e.g. a real Oud note for 'Oud & smoky'), then FOCUS (share of the perfume's evidence that belongs to the picked families), then total evidence.
 */
(function (root) {
  const W = { top: 0.6, heart: 1, base: 1, key: 1, acc: 0.8 };
  function items(p) {
    const out = [];
    if (p.notes) { p.notes.top.forEach(n => out.push([n, W.top, 'n'])); p.notes.heart.forEach(n => out.push([n, W.heart, 'n'])); p.notes.base.forEach(n => out.push([n, W.base, 'n'])); }
    if (p.key) p.key.forEach(n => out.push([n, W.key, 'n']));
    if (p.acc) p.acc.forEach(n => out.push([n, W.acc, 'a']));   // 'a' = accord (character word), not a real note
    return out;
  }
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const hasCore = (note, words) => (words || []).some(w => new RegExp('\\b' + esc(w) + '\\b', 'i').test(note));
  function evaluate(p, picked, famOf, core) {
    const st = {}, hits = {}; let w = 0;
    items(p).forEach(([note, wt, src]) => famOf(note).forEach(f => { if (picked.includes(f)) { st[f] = (st[f] || 0) + wt; (hits[f] = hits[f] || []).push({ n: note, w: wt, s: src }); w += wt; } }));
    const cover = picked.reduce((a, f) => a + Math.min(1, st[f] || 0), 0);
    const solid = picked.filter(f => (st[f] || 0) >= 1).length;
    const light = picked.filter(f => (st[f] || 0) > 0 && st[f] < 1).length;
    const total = items(p).reduce((a, [, wt]) => a + wt, 0) || 1;
    // headline note of the family (the ones named on the tile, e.g. Oud for 'Oud & smoky') present as a REAL note
    const coreHits = picked.filter(f => items(p).some(([n, , s]) => s !== 'a' && famOf(n).includes(f) && hasCore(n, (core || {})[f]))).length;
    return { p, st, hits, coreHits, cover: Math.round(cover * 100) / 100, solid, light, w: Math.round(w * 100) / 100, focus: Math.round(100 * w / total) / 100 };
  }
  function rank(products, picked, famOf, limit, core) {
    return products.map(p => evaluate(p, picked, famOf, core)).filter(x => x.cover >= 0.6)
      .sort((a, b) => b.cover - a.cover || b.solid - a.solid || b.coreHits - a.coreHits || b.focus - a.focus || b.w - a.w || String(a.p.name).localeCompare(String(b.p.name))).slice(0, limit || 3);
  }
  function tier(x, n) { const r = x.cover / n; return (r >= 0.999 && x.light === 0) ? 'best' : r >= 0.6 ? 'close' : 'part'; }
  const api = { rank, evaluate, tier, items, W };
  if (typeof module !== 'undefined') module.exports = api; else root.FinderCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
