from django import template
from organizaciones.models import Organizacion, Miembro

register = template.Library()


@register.simple_tag(takes_context=True)
def is_org_role(context, roles):
    """Return True if current user is staff or has one of the roles in the current organisation.

    Usage: {% if is_org_role 'owner,admin' %} ... {% endif %}
    """
    request = context.get('request')
    if not request:
        return False
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return False

    # staff always allowed
    if getattr(user, 'is_staff', False):
        return True

    # determine organisation from request (middleware sets request.organizacion)
    org = getattr(request, 'organizacion', None)
    if not org:
        org_id = request.session.get('organizacion_id')
        if org_id:
            try:
                org = Organizacion.objects.filter(id=org_id).first()
            except Exception:
                org = None

    if not org:
        return False

    wanted = [r.strip() for r in roles.split(',') if r.strip()]
    try:
        return Miembro.objects.filter(organizacion=org, user=user, role__in=wanted).exists()
    except Exception:
        return False
