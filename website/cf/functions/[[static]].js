import { storePayload } from './_lib/store.js';
// Serves the storefront files (public/) from Workers KV, cached at the edge.
// Why KV and not Pages static assets: the sandbox that builds this site can only call the plain Cloudflare REST API, and Pages' asset-upload step needs a second credential path.
// deploy.js uploads public/ -> KV (only changed files). Product photos are served with a long browser cache.
const HEADERS = { 'x-content-type-options': 'nosniff', 'referrer-policy': 'strict-origin-when-cross-origin', 'x-frame-options': 'DENY', 'permissions-policy': 'camera=(), microphone=(), geolocation=()' };
export async function onRequest({ request, env, waitUntil }) {
  if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('Method not allowed', { status: 405 });
  if (!env.ASSETS_KV) return env.ASSETS.fetch(request); // local `wrangler pages dev`: serve public/ directly
  const url = new URL(request.url);
  // the owner's dashboard lives at a secret address (env ADMIN_TOKEN); everywhere else it simply does not exist
  if (env.ADMIN_TOKEN && url.pathname === '/manage-' + env.ADMIN_TOKEN) {
    let page = null;
    if (env.LOCAL_DEV) page = await (await env.ASSETS.fetch(new Request(url.origin + '/admin-page.html'))).text();
    else { const v = await env.ASSETS_KV.get('admin-page.html', 'text'); page = v; }
    if (!page) return new Response('Not found', { status: 404 });
    return new Response(page.replace("/*ADMIN_TOKEN*/''", () => JSON.stringify(env.ADMIN_TOKEN)), { headers: { ...HEADERS, 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex, nofollow', 'referrer-policy': 'no-referrer' } });
  }
  let key; try { key = decodeURIComponent(url.pathname).replace(/^\/+/, ''); } catch { return new Response('Bad request', { status: 400 }); }
  if (!key || key.endsWith('/')) key += 'index.html';
  if (key.includes('..') || key.startsWith('_') || key === 'admin-page.html') return new Response('Not found', { status: 404 });
  const cache = caches.default, ck = new Request(url.origin + '/' + key);
  const hit = await cache.match(ck); if (hit) return hit;
  const { value, metadata } = await env.ASSETS_KV.getWithMetadata(key, 'arrayBuffer');
  if (!value && env.LOCAL_DEV) return env.ASSETS.fetch(request); // local dev only: files not in KV come straight from public/
  if (!value) return new Response('Not found', { status: 404, headers: HEADERS });
  const html = key === 'index.html', img = key.startsWith('img/');
  let body = value;
  if (html) { // absolute URLs for social previews + the live catalogue baked in (cached for a minute)
    let boot = 'null'; try { boot = JSON.stringify(await storePayload(env)).replace(/</g, '\\u003c'); } catch (e) { /* the page fetches /api/store itself */ }
    body = new TextDecoder().decode(value).replaceAll('{{ORIGIN}}', url.origin).replace('null/*BOOT*/', () => boot);
  }
  const res = new Response(body, { headers: { ...HEADERS, 'content-type': (metadata && metadata.type) || 'application/octet-stream', 'cache-control': html ? 'public, max-age=0, must-revalidate' : img ? 'public, max-age=604800' : 'public, max-age=3600' } });
  const cached = res.clone(); cached.headers.set('cache-control', html ? 'public, max-age=60' : img ? 'public, max-age=604800' : 'public, max-age=3600');
  waitUntil(cache.put(ck, cached));
  return res;
}
