from .models import Organizacion, Miembro


class TenantMiddleware:
    """Attach `organizacion` to request based on session or authenticated user.

    Priority: should run after AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organizacion = None
        # First try session
        org_id = request.session.get('organizacion_id')
        if org_id:
            try:
                request.organizacion = Organizacion.objects.filter(id=org_id).first()
            except Exception:
                request.organizacion = None

        # If not set and user is authenticated, try to get from Miembro
        if not request.organizacion and getattr(request, 'user', None) and request.user.is_authenticated:
            miembro = request.user.organizaciones.select_related('organizacion').first()
            if miembro:
                request.organizacion = miembro.organizacion

        return self.get_response(request)
