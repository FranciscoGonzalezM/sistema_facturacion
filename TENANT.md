Tenant (SaaS) notes

- Login flow: POST to `/login/` with fields `company`, `username`, `password`.
- `organizaciones` app: models `Organizacion` and `Miembro` store tenant and membership.
- Authentication: custom backend `organizaciones.auth_backends.TenantBackend` authenticates using company + username + password.
- Middleware `organizaciones.middleware.TenantMiddleware` populates `request.organizacion` using session or membership.
- Tenant scoping: many views now filter by `request.organizacion` and assign `organizacion` on create.

Test credentials (local development):
- Company: `ACME`
- Username: `tenantuser`
- Password: `testpass123`

Files added/changed for SaaS:
- `src/organizaciones/*` (models, admin, forms, middleware, views, urls, auth_backends, tests)
- Patched views: `src/proveedores/views.py`, `src/productos/views.py`, `src/clientes/views.py`, `src/facturas/views.py`, `src/requiza/views.py`, `src/core/views.py`
- Created `src/organizaciones/templates/organizaciones/editar.html` and `src/core/templates/base.html` (minimal base for rendering).

Next recommended steps:
- Add automated tests for tenant isolation across more endpoints (in progress).
- Audit remaining views and templates for tenant scoping and access control.
- Consider tenant routing by subdomain for production deployments.
