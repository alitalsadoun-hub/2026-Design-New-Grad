"""Builds concept_v3/index.html (single file: storefront + promotions engine + dashboard prototype).
All 81 catalogue products (niche, selective, body mist) are included; notes are optional and only shown where verified."""
import json, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = {r['id']: r for r in json.load(open('catalog_snapshot.json'))}
niche = {k: v for k, v in json.load(open('../data/notes_niche.json')).items() if not k.startswith('_')}
sel = {k: v for k, v in json.load(open('../data/notes_selective.json')).items() if not k.startswith('_')}
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
nkey = {norm({'Treasure': 'Tresure'}.get(k, k)): k for k in niche}          # catalogue spells it "Tresure"
def gender(nm): nm = nm.lower(); return 'her' if 'women' in nm else 'him' if re.search(r"\bmen", nm) else 'unisex'
prods = {}
order = sorted(rows.values(), key=lambda r: (0 if 'Niche' in r['cat'] else 1 if 'Selective' in r['cat'] else 2, -r['id']))
PREFERRED = ['Rouge', 'Gumin', 'New York Night', 'Exotic', 'Detox', 'Adria', 'Treasure', 'Draco']
def rank(r):
    m = re.match(r'MAD (.+?) (\d+) ml', r['name']); nm = norm(m.group(1)) if m else ''
    for i, p in enumerate(PREFERRED):
        if norm({'Treasure': 'Tresure'}.get(p, p)) == nm: return i
    return 99
order.sort(key=lambda r: (0 if 'Niche' in r['cat'] else 1 if 'Selective' in r['cat'] else 2, rank(r) if 'Niche' in r['cat'] else 0))
for r in order:
    if r['cat'].startswith('Packages'): continue
    pid = str(r['id']); coll = 'niche' if 'Niche' in r['cat'] else 'selective' if 'Selective' in r['cat'] else 'mist'
    base = dict(id=pid, brand='mad', collection=coll, img=f"img/p{pid}.webp", price=r['price'], was=r.get('was'), stock=int(r['stock'] or 0), **{'for': gender(r['name'])})
    if coll == 'niche':
        m = re.match(r'MAD (.+?) (\d+) ml', r['name']); nm = m.group(1); k = nkey.get(norm(nm))
        base.update(name=niche_name if False else (k or nm.title().replace("'S", "'s")), ml=int(m.group(2)))
        if k: base['notes'] = {x: niche[k][x] for x in ('top', 'heart', 'base')}
    elif coll == 'selective':
        m = re.search(r'MAD (\w+) Selective', r['name']); base.update(name=m.group(1), ml=100)
        if pid in sel: base['notes'] = sel[pid]['notes']
    else:
        base.update(name=re.sub(r'^MAD | Body Mist 250 ml$', '', r['name']).strip() + ' Body Mist', ml=250)
    prods[pid] = base
withn = sum(1 for p in prods.values() if 'notes' in p)
print(len(prods), 'products |', withn, 'with notes |', sum(1 for p in prods.values() if p['collection']=='niche'), 'niche,', sum(1 for p in prods.values() if p['collection']=='selective'), 'selective')
fam = json.load(open('../data/families.json'))
def pkg(pid, tag):
    r = rows[pid]
    return f'<article class="pkg"><img src="img/p{pid}.webp" alt="" loading="lazy"><div><span class="tag" data-i18n="{tag}"></span><h3>{re.sub(chr(92)+"s+", " ", r["name"])}</h3><div class="price"><b>{r["price"]}</b> <small>JOD</small> <s>{r["was"]}</s></div><button class="add" data-i18n="add"></button></div></article>'
h = open('template.html', encoding='utf-8').read()
h = h.replace('{{ENGINE}}', open('engine.js').read()).replace('{{ADMIN}}', open('admin.js').read())
h = h.replace('{{PRODUCTS_JSON}}', json.dumps(prods, ensure_ascii=False)).replace('{{FAMILIES_JSON}}', json.dumps(fam, ensure_ascii=False))
h = h.replace('{{PKGS}}', ''.join([pkg(98, 'pk_special'), pkg(93, 'pk_summer'), pkg(92, 'pk_sig')]))
open('index.html', 'w', encoding='utf-8').write(h); print('ok', len(h))
