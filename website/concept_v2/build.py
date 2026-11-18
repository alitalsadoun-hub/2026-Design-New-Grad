"""Builds concept_v2/index.html: three design directions (A Maison / B Noir / C Atelier), notes-based finder, guest COD checkout.
Notes come from ../data/notes_niche.json (transcribed from official MAD Parfumeur descriptions) - verify before launch."""
import json, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = {r['id']: r for r in json.load(open('catalog_snapshot.json'))}
notes = {k: v for k, v in json.load(open('../data/notes_niche.json')).items() if not k.startswith('_')}
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
alias = {'treasure': 'tresure'}
ORDER = ['Rouge', 'Gumin', 'New York Night', 'Exotic', 'Detox', 'Adria', 'Treasure', 'Draco', 'Bruno Gold', 'Inviting', 'Prevail', 'Narcotic', 'Oud Sateen', 'Effect', 'Divine Tough', 'Marjorie']
prods = {}
for name in ORDER:
    k = norm(alias.get(norm(name), name)); hit = None
    for r in rows.values():
        if 'Niche' not in r['cat']: continue
        m = re.match(r'MAD (.+?) (\d+) ml', r['name'])
        if m and norm(m.group(1)) == k: hit = (r, m); break
    if not hit: print('NO MATCH', name); continue
    r, m = hit; n = notes[name]
    nm = r['name'].lower()
    prods[str(r['id'])] = dict(id=str(r['id']), name=name, img=f"img/p{r['id']}.webp", price=r['price'], was=r.get('was'), ml=int(m.group(2)),
        **{'for': 'her' if 'women' in nm else 'him' if ' men' in nm else 'unisex'}, notes={x: n[x] for x in ('top', 'heart', 'base')})
print(len(prods), 'products with notes')
fam = [
 dict(id='citrus', name='Citrus', hint='Lemon, bergamot, orange', dot='#F2C94C', kw=['lemon', 'lime', 'bergamot', 'orange', 'mandarin', 'grapefruit', 'citrus'], ex=['blossom']),
 dict(id='fruity', name='Fruity', hint='Peach, pear, apple, berries', dot='#EB8A6B', kw=['peach', 'pear', 'apple', 'raspberry', 'cherry', 'plum', 'coconut', 'fruity', 'pineapple'], ex=[]),
 dict(id='floral', name='Floral', hint='Rose, jasmine, tuberose, lily', dot='#E7A1B6', kw=['rose', 'jasmine', 'tuberose', 'ylang', 'peony', 'lily', 'orange blossom', 'magnolia', 'violet', 'heliotrope', 'marigold', 'geranium', 'orris', 'orchid'], ex=[]),
 dict(id='sweet', name='Vanilla & sweet', hint='Vanilla, tonka, honey, caramel', dot='#E8CFA0', kw=['vanilla', 'tonka', 'honey', 'caramel', 'sugar', 'praline', 'rum', 'sweet', 'cream'], ex=['orange']),
 dict(id='woody', name='Woody', hint='Sandalwood, cedar, patchouli', dot='#9A7552', kw=['sandalwood', 'cedar', 'patchouli', 'moss', 'guaiac', 'vetiver', 'wood', 'fir balsam', 'elemi'], ex=[]),
 dict(id='amber', name='Amber & musk', hint='Amber, musk, benzoin', dot='#C98A3C', kw=['amber', 'musk', 'benzoin', 'labdanum', 'powdery'], ex=[]),
 dict(id='spicy', name='Spicy', hint='Cinnamon, pepper, cardamom, saffron', dot='#C0492F', kw=['cinnamon', 'pepper', 'cardamom', 'saffron', 'nutmeg', 'anise', 'clove'], ex=[]),
 dict(id='aromatic', name='Fresh & aromatic', hint='Lavender, eucalyptus, tea, marine', dot='#7FA88A', kw=['lavender', 'eucalyptus', 'olive', 'marine', 'tea', 'mint', 'balsamic'], ex=[]),
 dict(id='oud', name='Oud & smoky', hint='Oud, tobacco, incense', dot='#5B4636', kw=['oud', 'tobacco', 'incense'], ex=[]),
]
def pkg(pid, tag):
    r = rows[pid]
    return f'<article class="pkg"><img src="img/p{pid}.webp" alt=""><div><span class="tag" data-i18n="{tag}"></span><h3>{re.sub(chr(92)+"s+", " ", r["name"])}</h3><div class="price"><b>{r["price"]}</b> <small>JOD</small> <s>{r["was"]}</s></div><button class="add" data-i18n="add"></button></div></article>'
h = open('template.html', encoding='utf-8').read()
h = h.replace('{{PRODUCTS_JSON}}', json.dumps(prods, ensure_ascii=False)).replace('{{FAMILIES_JSON}}', json.dumps(fam, ensure_ascii=False))
h = h.replace('{{PKGS}}', ''.join([pkg(98, 'pk_special'), pkg(93, 'pk_summer'), pkg(92, 'pk_sig')]))
h = h.replace("function famOf(note){const n=note.toLowerCase();return FAMILIES.filter(f=>f.kw.some(k=>n.includes(k))).map(f=>f.id)}",
              "function famOf(note){const n=note.toLowerCase();return FAMILIES.filter(f=>f.kw.some(k=>n.includes(k))&&!(f.ex||[]).some(e=>n.includes(e))).map(f=>f.id)}")
open('index.html', 'w', encoding='utf-8').write(h); print('ok')
