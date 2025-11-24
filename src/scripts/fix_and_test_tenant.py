from django.contrib.auth import get_user_model
from organizaciones.models import Organizacion, Miembro
from django.test import Client
from django.db import IntegrityError

User = get_user_model()

def ensure_org():
    org = Organizacion.objects.filter(slug__iexact='acme').first() or Organizacion.objects.filter(nombre__iexact='ACME').first()
    if org:
        print('Organizacion exists:', org)
        return org
    try:
        org = Organizacion.objects.create(nombre='ACME', slug='acme')
        print('Organizacion created:', org)
        return org
    except IntegrityError:
        org = Organizacion.objects.filter(slug__iexact='acme').first()
        print('Organizacion found after IntegrityError:', org)
        return org

def ensure_user():
    user, created = User.objects.get_or_create(username='tenantuser', defaults={'email':'tenant@example.com'})
    if created:
        user.set_password('testpass123')
        user.save()
        print('User created: tenantuser')
    else:
        # Ensure password is set to known value for testing
        user.set_password('testpass123')
        user.save()
        print('User exists, password reset: tenantuser')
    return user

def ensure_cajero(org):
    # create a cashier user for testing
    cajero_user, created = User.objects.get_or_create(username='cajero1', defaults={'email':'cajero1@example.com'})
    if created:
        cajero_user.set_password('cajero123')
        cajero_user.save()
        print('Cajero user created: cajero1')
    else:
        cajero_user.set_password('cajero123')
        cajero_user.save()
        print('Cajero user exists, password reset: cajero1')

    miembro, mcreated = Miembro.objects.get_or_create(organizacion=org, user=cajero_user, defaults={'role':'cajero', 'es_propietario':False})
    if mcreated:
        print('Miembro cajero created for cajero1')
    else:
        print('Miembro cajero exists for cajero1')
    return cajero_user

def ensure_miembro(org, user):
    miembro, mcreated = Miembro.objects.get_or_create(organizacion=org, user=user, defaults={'role':'owner', 'es_propietario':True})
    if mcreated:
        print('Miembro created for user->org')
    else:
        print('Miembro exists')
    return miembro

def test_login_and_pages():
    c = Client()
    print('Attempting login via POST to /login/ ...')
    resp = c.post('/login/', {'company': 'ACME', 'username': 'tenantuser', 'password': 'testpass123'}, follow=True)
    print('Login response status:', resp.status_code)
    print('Redirect chain:', resp.redirect_chain)
    sess = c.session
    print('Session keys after login:', list(sess.keys()))
    print('organizacion_id in session:', sess.get('organizacion_id'))

    # Access billing page
    resp2 = c.get('/facturas/nueva/')
    print('/facturas/nueva/ status:', resp2.status_code)
    if resp2.status_code != 200:
        print('facturas/nueva content (truncated):')
        print(resp2.content.decode('utf-8')[:1000])

    # Access dashboard
    resp3 = c.get('/dashboard/mi-dashboard/')
    print('/dashboard/mi-dashboard/ status:', resp3.status_code)

    # Access organizacion edit
    resp4 = c.get('/organizacion/editar/')
    print('/organizacion/editar/ status:', resp4.status_code)

if __name__ == '__main__':
    org = ensure_org()
    user = ensure_user()
    miembro = ensure_miembro(org, user)
    cajero = ensure_cajero(org)
    test_login_and_pages()
