// Deploys the store to Cloudflare Pages with nothing but the plain REST API + one API token:
//   1) public/ files  -> Workers KV (only files that changed since the last deploy)      2) functions/ (API + static server) -> Pages deployment
// (wrangler's `pages deploy` needs a second, JWT-authenticated upload path that the build sandbox's proxy cannot pass. On a normal computer `npm run deploy` works as well.)
// usage: node deploy.js [branch]
const fs = require('fs'), path = require('path'), cp = require('child_process'), crypto = require('crypto');
const ACCOUNT = process.env.CLOUDFLARE_ACCOUNT_ID || '35b4aa5bf1b0886b5b4313e13f17441d', PROJECT = 'scentro', NS = '1af332dd9587474aa6df92add99f14f1', BRANCH = process.argv[2] || 'main';
const API = `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT}`;
const TYPES = { html: 'text/html; charset=utf-8', js: 'application/javascript', css: 'text/css', json: 'application/json', webp: 'image/webp', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', svg: 'image/svg+xml', ico: 'image/x-icon', txt: 'text/plain' };
const curl = (args, input) => { const r = cp.spawnSync('curl', ['-s', '-m', '300', ...args], { encoding: 'utf8', input, maxBuffer: 1 << 27 }); try { return JSON.parse(r.stdout); } catch { return { success: false, errors: [r.stdout.slice(0, 300) + r.stderr.slice(0, 200)] }; } };
const files = []; (function walk(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f), s = fs.statSync(p); if (s.isDirectory()) walk(p); else files.push(p); } })('public');
const items = files.map(p => { const key = path.relative('public', p).split(path.sep).join('/'), buf = fs.readFileSync(p); return { key, buf, type: TYPES[path.extname(p).slice(1).toLowerCase()] || 'application/octet-stream', hash: crypto.createHash('sha256').update(buf).digest('hex').slice(0, 20) }; }).filter(i => !i.key.startsWith('_'));
// which files changed? (hashes of the previous deploy are kept in KV under the reserved key "_hashes")
const prevRaw = cp.spawnSync('curl', ['-s', '-m', '60', `${API}/storage/kv/namespaces/${NS}/values/_hashes`], { encoding: 'utf8' }).stdout; let prev = {}; try { prev = JSON.parse(prevRaw); if (!prev || prev.success === false) prev = {}; } catch { prev = {}; }
const todo = items.filter(i => prev[i.key] !== i.hash); const now = Object.fromEntries(items.map(i => [i.key, i.hash]));
for (let i = 0; i < todo.length; i += 40) {
  const batch = todo.slice(i, i + 40).map(x => ({ key: x.key, value: x.buf.toString('base64'), base64: true, metadata: { type: x.type } }));
  const d = curl(['-X', 'PUT', `${API}/storage/kv/namespaces/${NS}/bulk`, '-H', 'Content-Type: application/json', '--data-binary', '@-'], JSON.stringify(batch));
  if (!d.success) { console.log('KV upload failed', JSON.stringify(d.errors)); process.exit(1); }
}
const dh = curl(['-X', 'PUT', `${API}/storage/kv/namespaces/${NS}/values/_hashes`, '-H', 'Content-Type: application/json', '--data-binary', '@-'], JSON.stringify(now)); // note: raw body = JSON text
if (dh.success === false) { console.log('could not save hashes', JSON.stringify(dh.errors)); }
console.log('KV: uploaded', todo.length, 'of', items.length, 'files');
// functions bundle
const out = '/tmp/claude-0/fb'; fs.mkdirSync(out, { recursive: true });
cp.execSync(`npx wrangler pages functions build functions --outdir=${out} --output-routes-path=${out}/routes.json`, { stdio: 'ignore' });
fs.writeFileSync(`${out}/routes.json`, JSON.stringify({ version: 1, include: ['/*'], exclude: [] }));
fs.writeFileSync(`${out}/manifest.json`, '{}');
const d = curl(['-X', 'POST', `${API}/pages/projects/${PROJECT}/deployments`, '-F', `manifest=<${out}/manifest.json`, '-F', `branch=${BRANCH}`, '-F', `_routes.json=@${out}/routes.json;filename=_routes.json`, '-F', `_worker.js=@${out}/index.js;filename=_worker.js`]);
if (!d.success) { console.log('deploy FAILED', JSON.stringify(d.errors)); process.exit(1); }
console.log('deployed ->', d.result.url, '| id', d.result.id);
