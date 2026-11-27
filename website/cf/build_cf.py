"""Builds the Cloudflare deploy folder: public/ (storefront), functions/_lib/engine.js (shared promotions engine), seed.sql (products + starting offers).
Seeding never overwrites existing rows (stock edits are safe). Run:  python3 build_cf.py   then   npx wrangler d1 execute scentro-db --remote --file=seed.sql   and   npm run deploy"""
import json, os, re, shutil, subprocess
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.run(['python3', 'build.py'], cwd='../concept_v3', check=True)
os.makedirs('public', exist_ok=True); os.makedirs('functions/_lib', exist_ok=True)
shutil.copy('../concept_v3/index.html', 'public/index.html'); shutil.copy('../concept_v3/admin-page.html', 'public/admin-page.html'); shutil.copy('../concept_v3/engine.js', 'functions/_lib/engine.js'); shutil.copy('../concept_v3/ordertext.js', 'functions/_lib/ordertext.js')
shutil.rmtree('public/img', ignore_errors=True); shutil.copytree('../concept_v3/img', 'public/img', ignore=shutil.ignore_patterns('*.png.bak'))
open('public/_headers', 'w').write('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n/img/*\n  Cache-Control: public, max-age=31536000, immutable\n/index.html\n  Cache-Control: no-cache\n/\n  Cache-Control: no-cache\n')
# starting offers = SEED_RULES from the template (sample offers except the confirmed "buy 2 Selective, get the 3rd free")
t = open('../concept_v3/template.html', encoding='utf-8').read(); m = re.search(r'const SEED_RULES=(\[.*?\n? ?\]);\n', t, re.S)
js = "console.log(JSON.stringify(" + m.group(1).rstrip(';') + "))"
rules = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)
prods = json.load(open('../concept_v3/products_seed.json', encoding='utf-8'))
q = lambda v: "'" + str(v).replace("'", "''") + "'"
out = []
for i, (pid, p) in enumerate(prods.items()):
    d = {k: v for k, v in p.items() if k not in ('price', 'was', 'stock')}
    out.append(f"INSERT OR IGNORE INTO products(id,data,price,was,stock,hidden,pos) VALUES({q(pid)},{q(json.dumps(d, ensure_ascii=False))},{p['price']},{p['was'] if p.get('was') else 'NULL'},{p['stock']},0,{i});")
for i, r in enumerate(rules):
    out.append(f"INSERT OR IGNORE INTO rules(id,data,uses,pos) VALUES({q(r['id'])},{q(json.dumps(r, ensure_ascii=False))},0,{i});")
open('seed.sql', 'w', encoding='utf-8').write('\n'.join(out) + '\n'); print(len(prods), 'products,', len(rules), 'offers ->', 'seed.sql')
