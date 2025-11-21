"""Simple HTTP test that GETs the login form (to obtain CSRF token) and then
POSTs the tenant login to the running dev server. Prints status, redirects,
cookies and a snippet of the response body.
"""
import sys
import re
try:
    import requests
except Exception:
    print('The requests library is required. Install with: pip install requests')
    sys.exit(2)

URL = 'http://127.0.0.1:8000/login/'
DATA = {'company': 'ACME', 'username': 'tenantuser', 'password': 'testpass123'}

session = requests.Session()

print('GET login page to obtain CSRF token...')
g = session.get(URL, timeout=10)
if g.status_code != 200:
    print('GET /login/ returned', g.status_code)
    sys.exit(1)

# Try to extract CSRF token from the form
match = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', g.text)
if not match:
    # Try a looser regex
    match = re.search(r'csrfmiddlewaretoken.*?value=["\']([^"\']+)["\']', g.text, re.S)

if not match:
    print('Could not find CSRF token in login form. Aborting.')
    sys.exit(2)

csrf_token = match.group(1)
print('Found CSRF token:', csrf_token)

payload = {'csrfmiddlewaretoken': csrf_token, **DATA}
headers = {'Referer': URL}

print('POSTing login form...')
resp = session.post(URL, data=payload, headers=headers, allow_redirects=True, timeout=10)

print('\nRequest URL:', URL)
print('Status code:', resp.status_code)
print('Final URL:', resp.url)
print('History (redirects):', [(r.status_code, r.headers.get('Location')) for r in resp.history])

print('\nCookies set by server:')
for c in session.cookies:
    print(f'{c.name}={c.value}; domain={c.domain}; path={c.path}')

content = resp.text
print('\nResponse body (first 1200 chars):')
print(content[:1200])

print('\nDone')
