from django.contrib import admin
from categorias.models import Categoria
#from productos.models import Producto
from clientes.models import Cliente
from facturas.models import Factura, DetalleFactura

admin.site.register(Categoria)
#admin.site.register(Producto)
admin.site.register(Cliente)
#admin.site.register(Factura)
admin.site.register(DetalleFactura)


