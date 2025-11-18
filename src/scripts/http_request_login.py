"""Simple HTTP test that posts to /login/ on the local dev server.
Prints status, redirects, cookies and a snippet of the response body.
"""
import sys
try:
    import requests
except Exception:
    print('The requests library is required. Install with: pip install requests')
    sys.exit(2)

URL = 'http://127.0.0.1:8000/login/'
DATA = {'company': 'ACME', 'username': 'tenantuser', 'password': 'testpass123'}

session = requests.Session()
resp = session.post(URL, data=DATA, allow_redirects=True, timeout=10)

print('Request URL:', URL)
print('Status code:', resp.status_code)
print('Final URL:', resp.url)
print('History (redirects):', [(r.status_code, r.headers.get('Location')) for r in resp.history])
print('\nResponse headers:')
for k, v in resp.headers.items():
    print(f'{k}: {v}')

print('\nCookies set by server:')
for c in session.cookies:
    print(f'{c.name}={c.value}; domain={c.domain}; path={c.path}')

content = resp.text
print('\nResponse body (first 1000 chars):')
print(content[:1000])

if 'organizacion_id' in session.cookies.get_dict():
    print('\norganizacion_id cookie present in client cookies (unexpected - session stores org id server-side)')

print('\nDone')
