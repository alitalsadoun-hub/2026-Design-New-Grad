"""Builds concept_v3/index.html (single file: storefront + promotions engine + dashboard prototype)."""
import json, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = {r['id']: r for r in json.load(open('catalog_snapshot.json'))}
niche = {k: v for k, v in json.load(open('../data/notes_niche.json')).items() if not k.startswith('_')}
sel = {k: v for k, v in json.load(open('../data/notes_selective.json')).items() if not k.startswith('_')}
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
ORDER = ['Rouge', 'Gumin', 'New York Night', 'Exotic', 'Detox', 'Adria', 'Treasure', 'Draco', 'Bruno Gold', 'Inviting', 'Prevail', 'Narcotic', 'Oud Sateen', 'Effect', 'Divine Tough', 'Marjorie']
prods = {}
def gender(nm): nm = nm.lower(); return 'her' if 'women' in nm else 'him' if ' men' in nm else 'unisex'
for name in ORDER:
    k = norm({'treasure': 'tresure'}.get(norm(name), name)); hit = None
    for r in rows.values():
        m = re.match(r'MAD (.+?) (\d+) ml', r['name'])
        if 'Niche' in r['cat'] and m and norm(m.group(1)) == k: hit = (r, m); break
    if not hit: print('NO MATCH', name); continue
    r, m = hit; n = niche[name]
    prods[str(r['id'])] = dict(id=str(r['id']), name=name, brand='mad', collection='niche', img=f"img/p{r['id']}.webp", price=r['price'], was=r.get('was'), ml=int(m.group(2)), **{'for': gender(r['name'])}, notes={x: n[x] for x in ('top', 'heart', 'base')})
for pid, s in sel.items():
    r = rows[int(pid)]
    prods[pid] = dict(id=pid, name=s['name'], brand='mad', collection='selective', img=f"img/p{pid}.webp", price=r['price'], was=r.get('was'), ml=100, **{'for': gender(r['name'])}, notes=s['notes'])
r = rows[83]; prods['83'] = dict(id='83', name='Sweet Beach Body Mist', brand='mad', collection='mist', img='img/p83.webp', price=r['price'], was=None, ml=250, **{'for': 'unisex'})
print(len(prods), 'products')
fam = json.load(open('../data/families.json'))
def pkg(pid, tag):
    r = rows[pid]
    return f'<article class="pkg"><img src="img/p{pid}.webp" alt=""><div><span class="tag" data-i18n="{tag}"></span><h3>{re.sub(chr(92)+"s+", " ", r["name"])}</h3><div class="price"><b>{r["price"]}</b> <small>JOD</small> <s>{r["was"]}</s></div><button class="add" data-i18n="add"></button></div></article>'
h = open('template.html', encoding='utf-8').read()
h = h.replace('{{ENGINE}}', open('engine.js').read()).replace('{{ADMIN}}', open('admin.js').read())
h = h.replace('{{PRODUCTS_JSON}}', json.dumps(prods, ensure_ascii=False)).replace('{{FAMILIES_JSON}}', json.dumps(fam, ensure_ascii=False))
h = h.replace('{{PKGS}}', ''.join([pkg(98, 'pk_special'), pkg(93, 'pk_summer'), pkg(92, 'pk_sig')]))
# finder helper: ensure exclusions are honoured (already in template.famOf)
open('index.html', 'w', encoding='utf-8').write(h); print('ok', len(h))
