from django.contrib.auth import get_user_model
from organizaciones.models import Organizacion, Miembro
from django.contrib.auth.models import Group
from django.test import Client

User = get_user_model()

print('Creating organization and user...')
org, created = Organizacion.objects.get_or_create(nombre='ACME', defaults={'slug':'acme'})
if created:
    print('Organizacion created:', org)
else:
    print('Organizacion exists:', org)

user, ucreated = User.objects.get_or_create(username='tenantuser', defaults={'email':'tenant@example.com'})
if ucreated:
    user.set_password('testpass123')
    user.save()
    print('User created: tenantuser')
else:
    print('User exists: tenantuser')

# Create Miembro linking
miembro, mcreated = Miembro.objects.get_or_create(organizacion=org, user=user, defaults={'role':'owner', 'es_propietario':True})
if mcreated:
    print('Miembro created for user->org')
else:
    print('Miembro exists')

# Test login via Django test client
c = Client()
print('Attempting login via POST to /login/ ...')
resp = c.post('/login/', {'company': 'ACME', 'username': 'tenantuser', 'password': 'testpass123'}, follow=True)
print('Login response status:', resp.status_code)
print('Redirect chain:', resp.redirect_chain)

sess = c.session
print('Session keys after login:', list(sess.keys()))
print('organizacion_id in session:', sess.get('organizacion_id'))

# Try to access the organization edit page
resp2 = c.get('/organizacion/editar/')
print('/organizacion/editar/ status:', resp2.status_code)
print('Contains "Editar Organización"?', 'Editar Organización' in resp2.content.decode('utf-8'))

print('Done')
