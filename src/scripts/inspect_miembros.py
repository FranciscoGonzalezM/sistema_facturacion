from organizaciones.models import Miembro,Organizacion
from django.contrib.auth import get_user_model
User = get_user_model()
org = Organizacion.objects.filter(slug__iexact='acme').first()
print('org:', org)
qs = Miembro.objects.filter(organizacion=org)
print('miembros count:', qs.count())
for m in qs:
    print('user:', m.user.username, 'role:', m.role, 'es_propietario:', m.es_propietario)
