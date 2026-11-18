"""Builds concept_v1/index.html - SCENTRO homepage concept (EN / AR-RTL), real catalogue data from catalog_snapshot.json.
Notes/mood tags below are PLACEHOLDERS inferred from product photography; they must be verified before launch."""
import json, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = {r['id']: r for r in json.load(open('catalog_snapshot.json'))}

# id -> (short name, for, moods, notes-ish line)  moods: fresh sweet woody floral spicy
NICHE = {
    21: ('New York Night', 'her', 'sweet floral', 'Peach · Vanilla · Jasmine'),
    15: ('Exotic', 'unisex', 'spicy fresh', 'Grapefruit · Cinnamon · Amber'),
    13: ('Detox', 'unisex', 'floral sweet', 'Rose · Cherry · White flowers'),
    14: ('Rouge', 'unisex', 'sweet spicy', 'Orange · Jasmine · Moss'),
    26: ('Gumin', 'him', 'fresh woody', 'Lime · Cedar · White flowers'),
    27: ('Adria', 'unisex', 'fresh', 'Lemon · Olive leaf · Lavender'),
    23: ('Treasure', 'unisex', 'sweet spicy', 'Bergamot · Honey · Vanilla · Tobacco'),
    22: ('Midnight', 'unisex', 'woody', 'Pine · Vanilla · Wood'),
    20: ('Pera', 'him', 'spicy sweet', 'Red berries · Cinnamon · Vanilla'),
    18: ('Draco', 'unisex', 'fresh spicy', 'Lemon · Amber · Lavender'),
}
# resolve ids by name instead of trusting guesses above
byname = {}
for r in rows.values():
    m = re.match(r'MAD (.+?) (\d+) ml', r['name'])
    if m and 'Niche' in r['cat']:
        byname[m.group(1).lower()] = r
fix = {}
for pid, v in NICHE.items():
    r = byname.get(v[0].lower().replace('treasure', 'tresure'))
    if r: fix[r['id']] = v
NICHE = fix
for k, v in list(NICHE.items()):
    print(k, v[0], rows[k]['price'], rows[k]['was'])

def card(pid, extra=''):
    r = rows[pid]; n = NICHE.get(pid)
    name = n[0] if n else re.sub(r'^MAD |\s*\d+ ml.*$', '', r['name'])
    disc = f"-{round((1 - r['price'] / r['was']) * 100)}%" if r.get('was') else ''
    forw = {'her': ('For Women', 'للنساء'), 'him': ('For Men', 'للرجال'), 'unisex': ('Unisex', 'للجنسين')}[n[1]] if n else ('', '')
    return f'''<article class="card" data-for="{n[1] if n else ''}" data-moods="{n[2] if n else ''}">
  <a class="ph" href="#"><img src="img/p{pid}.webp" alt="{name}">{f'<span class="badge">{disc}</span>' if disc else ''}<button class="wish" aria-label="wishlist">♡</button></a>
  <div class="meta"><h3>{name}</h3><p class="sub"><span data-i18n="extrait">Extrait de parfum</span> · 100 ml · <span data-i18n="for_{n[1] if n else 'x'}">{forw[0]}</span></p>
  <p class="notes">{n[3] if n else ''}</p>
  <div class="row"><div class="price"><b>{r['price']}</b> <small>JOD</small>{f' <s>{r["was"]}</s>' if r.get('was') else ''}</div><button class="add" data-i18n="add">Add to cart</button></div></div></article>'''

niche_ids = [k for k in NICHE]
best = niche_ids[:8]
pk = {}
for r in rows.values():
    if r['cat'].startswith('Packages'): pk[r['id']] = r

def pkg(pid, tag_en, tag_ar):
    r = rows[pid]
    return f'''<article class="pkg"><img src="img/p{pid}.webp" alt=""><div><span class="tag" data-i18n="{tag_en}">{tag_en}</span>
<h3>{re.sub(r"\\s+", " ", r["name"])}</h3><div class="price"><b>{r["price"]}</b> <small>JOD</small> <s>{r["was"]}</s></div><button class="add" data-i18n="add">Add to cart</button></div></article>'''

html = open('template.html', encoding='utf-8').read()
html = html.replace('{{BEST}}', '\n'.join(card(i) for i in best))
html = html.replace('{{ALL_JSON}}', json.dumps({str(i): {'name': NICHE[i][0], 'for': NICHE[i][1], 'moods': NICHE[i][2].split(), 'notes': NICHE[i][3], 'price': rows[i]['price'], 'was': rows[i]['was'], 'img': f'img/p{i}.webp'} for i in NICHE}, ensure_ascii=False))
html = html.replace('{{PKGS}}', '\n'.join([pkg(98, 'pk_special', ''), pkg(93, 'pk_summer', ''), pkg(92, 'pk_sig', '')]))
open('index.html', 'w', encoding='utf-8').write(html)
print('ok', len(html))
