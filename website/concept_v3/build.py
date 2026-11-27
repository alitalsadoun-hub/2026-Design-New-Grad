"""Builds concept_v3/index.html (single file: storefront + promotions engine + dashboard prototype).
All 81 catalogue products (niche, selective, body mist) are included; notes are optional and only shown where verified."""
import json, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = {r['id']: r for r in json.load(open('catalog_snapshot.json'))}
niche = {k: v for k, v in json.load(open('../data/notes_niche.json')).items() if not k.startswith('_')}
sel = {k: v for k, v in json.load(open('../data/notes_selective.json')).items() if not k.startswith('_')}
mistn = {k: v for k, v in json.load(open('../data/notes_mist.json')).items() if not k.startswith('_')}
perc = {k: v for k, v in json.load(open('../data/perceived_niche.json')).items() if not k.startswith('_')}
nins = json.load(open('../data/niche_inspired.json'))
catsel = json.load(open('../data/selective_catalogue.json'))
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
    if r['cat'].startswith('Packages') or int(r['stock'] or 0) <= 0: continue
    pid = str(r['id']); coll = 'niche' if 'Niche' in r['cat'] else 'selective' if 'Selective' in r['cat'] else 'mist'
    base = dict(id=pid, brand='mad', collection=coll, img=f"img/p{pid}.webp", price=r['price'], was=r.get('was'), stock=int(r['stock'] or 0), **{'for': gender(r['name'])})
    if coll == 'niche':
        m = re.match(r'MAD (.+?) (\d+) ml', r['name']); nm = m.group(1); k = nkey.get(norm(nm))
        base.update(name=niche_name if False else (k or nm.title().replace("'S", "'s")), ml=int(m.group(2)))
        if k: base['notes'] = {x: niche[k][x] for x in ('top', 'heart', 'base')}
        if k in perc and perc[k]['acc']: base['acc'] = perc[k]['acc']
        if k in nins:
            base['insp'] = {'house': nins[k]['house'], 'original': nins[k]['original'], 'confirmed': True}
            if 'key' in nins[k]: base['key'] = nins[k]['key']
    elif coll == 'selective':
        m = re.search(r'MAD (\w+) Selective', r['name']); base.update(name=m.group(1), ml=100)
        if pid in catsel:
            c = catsel[pid]; ok = 'confirm' not in c['original']; orig = re.sub(r'\s*\(.*?\)', '', c['original']).strip() if ok else ''
            base['insp'] = {'house': c['house'], 'original': orig, 'confirmed': ok}
            if c.get('notes'): base['notes'] = c['notes']; base['origNotes'] = True
            elif c['key']: base['key'] = c['key']; base['acc'] = c['accords']
            elif pid in sel: base['notes'] = sel[pid]['notes']
        elif pid in sel: base['notes'] = sel[pid]['notes']
    else:
        mn = re.sub(r'^MAD | Body Mist 250 ml$', '', r['name']).strip().title(); base.update(name=mn + ' Body Mist', ml=250)
        if mn in mistn: base['notes'] = {x: mistn[mn][x] for x in ('top', 'heart', 'base')}
    prods[pid] = base
for x in json.load(open('../data/new_products_draft.json')):
    pid = 'tf' + x['code'][1:]
    prods[pid] = dict(id=pid, name=x['code'], brand='mad', collection='selective', img=x['image'], price=x['price'], was=x['was'], stock=x['stock'], ml=100, **{'for': x['gender']},
                      insp={'house': x['house'], 'original': x['original'], 'confirmed': True}, key=x['key'], acc=x['accords'], placeholder=True)
withn = sum(1 for p in prods.values() if 'notes' in p or 'key' in p)
print(len(prods), 'products |', withn, 'with notes |', sum(1 for p in prods.values() if p['collection']=='niche'), 'niche,', sum(1 for p in prods.values() if p['collection']=='selective'), 'selective')
fam = json.load(open('../data/families.json'))
NF = json.load(open('../data/note_families.json'))
def _notes(p):
    s = set()
    for k in ('top', 'heart', 'base'):
        s.update((p.get('notes') or {}).get(k, []))
    s.update(p.get('key') or []); s.update(p.get('acc') or []); return s
missing = sorted({n for p in prods.values() for n in _notes(p) if n.lower().strip() not in NF})
assert not missing, 'notes without a scent family in data/note_families.json: %s' % missing
h = open('template.html', encoding='utf-8').read()
h = h.replace('{{ENGINE}}', open('engine.js').read()).replace('{{ORDERTEXT}}', open('ordertext.js').read())
h = h.replace('{{FINDER}}', open('finder.js').read()).replace('{{NOTE_FAM_JSON}}', json.dumps(NF, ensure_ascii=False))
# quantities are private: the static page carries no real stock (9 = per-item cart cap); the live catalogue comes from the server
pub = {k: {**v, 'stock': 9} for k, v in prods.items()}
h = h.replace('{{PRODUCTS_JSON}}', json.dumps(pub, ensure_ascii=False)).replace('{{FAMILIES_JSON}}', json.dumps(fam, ensure_ascii=False))

# two builds: the PUBLIC page has no dashboard code at all; the PRIVATE one is served only at the owner's secret address (see cf/functions/[[static]].js)
STUB = "let ADM={swapped:false},adTab='promos';function renderAdmin(){}function renderAnn0(){}"
pub_h = h.replace('{{ADMIN}}', STUB); pub_h = re.sub(r'<!--ADMIN_BEGIN-->.*?<!--ADMIN_END-->', '', pub_h, flags=re.S)
adm_h = h.replace('{{ADMIN}}', open('admin.js').read()).replace('/*ADMIN_MODE*/false', 'true')
adm_h = adm_h.replace('<title>SCENTRO — Niche & Selective Perfumes · عطور سنترو</title>', '<title>SCENTRO Dashboard</title><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer">')
adm_h = re.sub(r'<meta property="og:[^>]*>|<meta name="twitter:[^>]*>|<meta name="description"[^>]*>', '', adm_h)
open('index.html', 'w', encoding='utf-8').write(pub_h); open('admin-page.html', 'w', encoding='utf-8').write(adm_h); print('ok public', len(pub_h), '| admin', len(adm_h))
json.dump(prods, open('products_seed.json', 'w', encoding='utf-8'), ensure_ascii=False)
