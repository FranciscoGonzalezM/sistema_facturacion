from django.contrib.auth import get_user_model
from organizaciones.models import Organizacion, Miembro
from django.test import Client

User = get_user_model()

print('Reset/test seed login script starting...')

org, created = Organizacion.objects.get_or_create(nombre='ACME', defaults={'slug':'acme'})
if created:
    print('Organizacion created:', org)
else:
    print('Organizacion exists:', org)

user, ucreated = User.objects.get_or_create(username='tenantuser', defaults={'email':'tenant@example.com'})
if ucreated:
    user.set_password('testpass123')
    user.is_active = True
    user.save()
    print('User created: tenantuser')
else:
    # Force password to the known seed to ensure tests are consistent
    user.set_password('testpass123')
    user.is_active = True
    user.save()
    print('User existed; password reset for tenantuser')

miembro, mcreated = Miembro.objects.get_or_create(organizacion=org, user=user, defaults={'role':'owner', 'es_propietario':True})
if mcreated:
    print('Miembro created for user->org')
else:
    print('Miembro exists')

c = Client()
print('\nAttempting login WITH company (ACME)...')
resp = c.post('/login/', {'company': 'ACME', 'username': 'tenantuser', 'password': 'testpass123'}, follow=True)
print('Status:', resp.status_code)
print('Redirect chain:', resp.redirect_chain)
print('Session keys after login:', list(c.session.keys()))
print('organizacion_id in session:', c.session.get('organizacion_id'))

print('\nAttempting login WITHOUT company...')
c = Client()
resp2 = c.post('/login/', {'username': 'tenantuser', 'password': 'testpass123'}, follow=True)
print('Status:', resp2.status_code)
print('Redirect chain:', resp2.redirect_chain)
print('Session keys after login:', list(c.session.keys()))
print('organizacion_id in session (after legacy login):', c.session.get('organizacion_id'))

print('\nPassword verification check (server-side):', user.check_password('testpass123'))
print('Script finished.')
import os
import sys

cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# ensure src is on path
sys.path.insert(0, os.path.abspath(cwd))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from organizaciones.models import Organizacion, Miembro
from django.test import Client

User = get_user_model()
org, _ = Organizacion.objects.get_or_create(nombre='ACME', defaults={'slug':'acme'})
user, ucreated = User.objects.get_or_create(username='tenantuser', defaults={'email':'tenant@example.com'})
user.set_password('testpass123')
user.save()
print('User ensured and password set to testpass123')
miembro, _ = Miembro.objects.get_or_create(organizacion=org, user=user, defaults={'role':'owner','es_propietario':True})
print('Miembro ensured for org ACME and user tenantuser')

c = Client()
print('Posting to /login/ ...')
resp = c.post('/login/', {'company':'ACME','username':'tenantuser','password':'testpass123'}, follow=True)
print('Login status:', resp.status_code)
print('Redirect chain:', resp.redirect_chain)
print('Session keys:', list(c.session.keys()))
print('organizacion_id:', c.session.get('organizacion_id'))

# Also try legacy login without company
print('Posting legacy login without company ...')
resp2 = c.post('/login/', {'username':'tenantuser','password':'testpass123'}, follow=True)
print('Legacy login status:', resp2.status_code)
print('Session keys after legacy login:', list(c.session.keys()))
print('organizacion_id after legacy login:', c.session.get('organizacion_id'))
