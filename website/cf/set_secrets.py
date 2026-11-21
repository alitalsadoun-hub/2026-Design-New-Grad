"""Sets the production secrets on the Cloudflare Pages project (never prints them, never writes them to disk).
usage: PW='<dashboard password>' NOTIFY='<order e-mail>' python3 set_secrets.py
Secrets: ADMIN_SALT / ADMIN_HASH (PBKDF2-SHA256, 100k iterations - the password itself is NOT stored), SESSION_SECRET (random).
The API token is injected by the sandbox proxy; locally use your own CLOUDFLARE_API_TOKEN."""
import os, json, base64, hashlib, secrets, subprocess, sys
A = os.environ.get('CF_ACCOUNT', '35b4aa5bf1b0886b5b4313e13f17441d'); D1 = '656f4268-c6d4-488b-80c6-91330adba758'
pw = os.environ['PW']; notify = os.environ.get('NOTIFY', '')
b = lambda x: base64.urlsafe_b64encode(x).rstrip(b'=').decode()
salt = secrets.token_bytes(16)
env = {'ADMIN_SALT': {'type': 'secret_text', 'value': b(salt)},
       'ADMIN_HASH': {'type': 'secret_text', 'value': b(hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, 100000, 32))},
       'SESSION_SECRET': {'type': 'secret_text', 'value': b(secrets.token_bytes(32))}}
if notify: env['NOTIFY_EMAIL'] = {'type': 'plain_text', 'value': notify}
body = {'deployment_configs': {'production': {'env_vars': env, 'd1_databases': {'DB': {'id': D1}}, 'compatibility_date': '2026-11-01'},
                               'preview': {'env_vars': env, 'd1_databases': {'DB': {'id': D1}}, 'compatibility_date': '2026-11-01'}}}
r = subprocess.run(['curl', '-s', '-m', '40', '-X', 'PATCH', f'https://api.cloudflare.com/client/v4/accounts/{A}/pages/projects/scentro', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                   input=json.dumps(body), capture_output=True, text=True)
d = json.loads(r.stdout); print('success:', d.get('success'), d.get('errors'))
sys.exit(0 if d.get('success') else 1)
