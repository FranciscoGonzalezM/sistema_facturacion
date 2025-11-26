from django.test import Client
from django.contrib.auth import get_user_model
from productos.models import Producto, Moneda
from categorias.models import Categoria
from proveedores.models import Proveedor
from django.conf import settings

User = get_user_model()

print('Running product creation test')

client = Client()

# Create staff user
user, created = User.objects.get_or_create(username='teststaff')
if created:
    user.set_password('staffpass')
    user.is_staff = True
    user.is_superuser = False
    user.save()
    print('Created staff user teststaff')
else:
    user.set_password('staffpass')
    user.is_staff = True
    user.save()
    print('Updated staff user teststaff password')

# Create necessary related objects
moneda, _ = Moneda.objects.get_or_create(codigo='USD', defaults={'nombre':'Dolar','simbolo':'$','cambio_a_usd':1.0,'principal':True})
cat, _ = Categoria.objects.get_or_create(nombre='General')
prov, _ = Proveedor.objects.get_or_create(nombre_empresa='Proveedor Test')

# Login
login = client.login(username='teststaff', password='staffpass')
print('Login success:', login)

# Prepare POST data for product creation
post_data = {
    'categoria': cat.id,
    'nombre': 'Producto Test',
    'precio': '9.99',
    'stock': '100',
    'moneda': moneda.id,
    'proveedor': prov.id,
    'activo': 'on',
}

# Formset management form
post_data['codigos-TOTAL_FORMS'] = '1'
post_data['codigos-INITIAL_FORMS'] = '0'
post_data['codigos-MIN_NUM_FORMS'] = '0'
post_data['codigos-MAX_NUM_FORMS'] = '1000'
# Data for one codigo
post_data['codigos-0-codigo_barra'] = '123456789012'
post_data['codigos-0-codigo_qr'] = ''

response = client.post('/productos/crear/', post_data, follow=True)
print('POST /productos/crear/ status_code:', response.status_code)

# Check created
prod = Producto.objects.filter(nombre='Producto Test').first()
if prod:
    print('Product created:', prod.id, prod.nombre, prod.precio, prod.stock)
    cods = list(prod.codigos.all())
    print('Product codes count:', len(cods))
else:
    print('Product not created. Response content excerpt:')
    print(response.content.decode()[:1000])
