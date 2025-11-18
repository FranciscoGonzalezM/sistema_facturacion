from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Organizacion, Miembro


class TenantBackend(ModelBackend):
    """Authenticate using company (organizacion nombre/slug) + username + password.

    Falls back to default behaviour if `company` is not provided.
    """

    def authenticate(self, request, company=None, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if company:
            # Try to find organization by name or slug (case-insensitive)
            org = Organizacion.objects.filter(nombre__iexact=company).first()
            if not org:
                org = Organizacion.objects.filter(slug__iexact=company).first()

            # If org wasn't found, fall back to default backend (allow system/global users)
            if not org:
                return super().authenticate(request, username=username, password=password, **kwargs)

            try:
                member = Miembro.objects.select_related('user').get(organizacion=org, user__username=username)
            except Miembro.DoesNotExist:
                # If the user is not a member of the organization, allow the default backend
                # to try to authenticate (useful for staff/superusers or legacy accounts)
                return super().authenticate(request, username=username, password=password, **kwargs)

            user = member.user
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            return None

        # No company provided, fallback to default ModelBackend
        return super().authenticate(request, username=username, password=password, **kwargs)
