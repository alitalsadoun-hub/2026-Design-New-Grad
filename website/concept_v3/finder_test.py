"""Independent oracle for the 'find by notes' finder. Re-implements the ranking in Python from raw product data + the audited
note->family dictionary and compares it with what the PAGE really displayed for every combination (387 runs).
usage: node finder_audit.js && python3 finder_test.py"""
import json, itertools, collections, sys, re
d = json.load(open('finder_runs.json')); NF = json.load(open('../data/note_families.json')); P = d['products']
FAM = ['citrus','fruity','floral','sweet','woody','amber','spicy','aromatic','oud']
W = dict(top=.6, heart=1, base=1, key=1, acc=.8)
fam = lambda n: NF.get(n.lower().strip(), None)
def items(p):
    out = []
    for k in ('top','heart','base'):
        out += [(n, W[k]) for n in (p['notes'] or {}).get(k, [])]
    out += [(n, W['key']) for n in (p['key'] or [])] + [(n, W['acc']) for n in (p['acc'] or [])]
    return out
def items_notes(p):
    out = []
    for k in ('top','heart','base'): out += [(n, 1) for n in (p['notes'] or {}).get(k, [])]
    return out + [(n, 1) for n in (p['key'] or [])]
def ev(p, picked):
    st = collections.defaultdict(float); hits = collections.defaultdict(list)
    for n, w in items(p):
        for f in fam(n):
            if f in picked: st[f] += w; hits[f].append(n)
    cover = sum(min(1, st[f]) for f in picked); solid = sum(1 for f in picked if st[f] >= 1); light = sum(1 for f in picked if 0 < st[f] < 1)
    w = sum(wt for n_, wt in items(p) for f in fam(n_) if f in picked); total = sum(wt for _, wt in items(p)) or 1
    core = sum(1 for f in picked if any(f in fam(n_) and any(re.search(r'\b' + re.escape(c) + r'\b', n_, re.I) for c in d['core'][f]) for n_, wt in items_notes(p)))
    return dict(cover=round(cover, 2), solid=solid, light=light, hits=hits, st=st, w=round(w, 2), focus=round(100 * w / total) / 100, core=core)
def eligible(p, who): return (p['notes'] or p['key']) and p['coll'] != 'mist' and p['stock'] > 0 and (who == 'any' or p['for'] == 'unisex' or p['for'] == who)
fails = collections.Counter(); examples = {}; short = []; empty = []
def bad(kind, ctx):
    fails[kind] += 1; examples.setdefault(kind, ctx)
for r in d['runs']:
    picked, who, cards = r['picked'], r['who'], r['cards']; n = len(picked)
    pool = {i: ev(p, picked) for i, p in P.items() if eligible(p, who)}
    ranked = sorted([(i, e) for i, e in pool.items() if e['cover'] >= .6], key=lambda x: (-x[1]['cover'], -x[1]['solid'], -x[1]['core'], -x[1]['focus'], -x[1]['w']))
    key = lambda e: (e['cover'], e['solid'], e['core'], e['focus'], e['w'])
    expect = [key(e) for i, e in ranked[:3]]
    got = []
    for c in cards:
        p = P[c['id']]; e = pool.get(c['id'])
        if e is None: bad('result is ineligible (wrong gender / sold out / mist / no notes)', (picked, who, c['name'])); continue
        got.append(key(e))
        if e['cover'] < .6: bad('result has no real link to the picked families', (picked, who, c['name']))
        allnotes = {n for n, _ in items(p)}
        if not c['shared']: bad('result shows no matching notes', (picked, who, c['name']))
        low = [x.lower() for x in c['shared']]
        if len(set(low)) != len(low): bad('same note shown twice', (picked, who, c['name'], c['shared']))
        real_hits = {n_.lower() for n_, _ in items_notes(p) if set(fam(n_)) & set(picked)}
        if real_hits and any(x not in real_hits for x in low): bad('accord word shown although a real note matches', (picked, who, c['name'], c['shared']))
        if real_hits and not (set(low) & real_hits): bad('no real note shown although one matches', (picked, who, c['name'], c['shared']))
        e_real = [h for h in e['hits'].values() for h in h]
    if got != expect: bad('page top-3 differs from the true best-3 (ranking)', (picked, who, got, expect))
    if len(cards) < 3 and not r['empty']: short.append((picked, who, len(cards)))
    if r['empty'] or not cards: empty.append((picked, who))
    # a perfect (all solid) perfume exists -> it must be first
    perfect = [i for i, e in pool.items() if e['solid'] == n]
    if perfect and cards and cards[0]['id'] not in perfect: bad('a perfect match exists but is not first', (picked, who, cards[0]['name']))
print(f"runs: {len(d['runs'])}  (every 1-3 note combination x anyone/her/him)")
print('FAILURES:', dict(fails) if fails else 'none')
for k, v in examples.items(): print('  e.g.', k, v)
print(f"runs with fewer than 3 results: {len(short)}  | with NO result: {len(empty)}")
for x in short[:12]: print('   fewer:', x)
for x in empty[:12]: print('   empty:', x)
sys.exit(1 if fails else 0)
