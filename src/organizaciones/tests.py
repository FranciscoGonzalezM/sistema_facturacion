from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from organizaciones.models import Organizacion, Miembro
from clientes.models import Cliente
from productos.models import Producto


class TenantIsolationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Org A
        self.org_a = Organizacion.objects.create(nombre='OrgA', slug='orga')
        self.user_a = User.objects.create_user(username='usera', password='passA')
        Miembro.objects.create(organizacion=self.org_a, user=self.user_a, role='owner', es_propietario=True)

        # Org B
        self.org_b = Organizacion.objects.create(nombre='OrgB', slug='orgb')
        self.user_b = User.objects.create_user(username='userb', password='passB')
        Miembro.objects.create(organizacion=self.org_b, user=self.user_b, role='owner', es_propietario=True)

        # Create a cliente for each org
        self.cliente_a = Cliente.objects.create(nombre='Cliente A', organizacion=self.org_a)
        self.cliente_b = Cliente.objects.create(nombre='Cliente B', organizacion=self.org_b)

        # Create required related objects for Producto
        from categorias.models import Categoria
        from productos.models import Moneda
        categoria = Categoria.objects.create(nombre='General')
        moneda = Moneda.objects.create(codigo='USD', nombre='Dolar', simbolo='$', cambio_a_usd=1)

        # Create a producto for each org
        self.producto_a = Producto.objects.create(nombre='Producto A', organizacion=self.org_a, precio=0, activo=True, stock=10, categoria=categoria, moneda=moneda)
        self.producto_b = Producto.objects.create(nombre='Producto B', organizacion=self.org_b, precio=0, activo=True, stock=10, categoria=categoria, moneda=moneda)

    def login(self, company, username, password):
        c = Client()
        resp = c.post('/login/', {'company': company, 'username': username, 'password': password}, follow=True)
        return c, resp

    def test_clientes_isolation(self):
        c, resp = self.login('OrgA', 'usera', 'passA')
        response = c.get('/clientes/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Cliente A', content)
        self.assertNotIn('Cliente B', content)

    def test_productos_isolation(self):
        c, resp = self.login('OrgB', 'userb', 'passB')
        response = c.get('/')  # homepage/redirects to dashboard which may list counts
        self.assertEqual(response.status_code, 302)  # redirect to login or dashboard
        # Query products list directly
        response = c.get('/productos/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Producto B', content)
        self.assertNotIn('Producto A', content)
