"""
Middleware que verifica el estado del restaurante del usuario autenticado.

Reglas:
- Rutas públicas (login, logout, registro, admin de Django, estáticos,
  media y cliente): se dejan pasar sin verificar.
- Usuario NO autenticado: se deja pasar (las vistas usan @login_required).
- Usuario autenticado sin restaurante:
    - Si es superuser → se le manda a crear el restaurante en el admin.
    - Si es usuario normal → se le manda al registro.
- Usuario con restaurante inactivo → se le manda al home.
- Usuario con restaurante activo → se expone request.restaurante
  para que las vistas lo usen sin volver a consultarlo.
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


PUBLIC_PREFIXES = (
    "/login/",
    "/logout/",
    "/registro/",
    "/admin/",
    "/static/",
    "/media/",
    "/cliente/",
)


class RestauranteMiddleware(MiddlewareMixin):
    """Verifica y expone el restaurante del usuario autenticado."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Home y rutas públicas: nunca se tocan
        if request.path == "/" or request.path.startswith(PUBLIC_PREFIXES):
            return None

        # Usuarios anónimos: @login_required se encarga
        if not request.user.is_authenticated:
            return None

        restaurante = getattr(request.user, "restaurante", None)

        # Usuario autenticado SIN restaurante
        if restaurante is None:
            if request.user.is_superuser:
                messages.info(
                    request,
                    "Aún no tienes un restaurante. Crea uno para acceder al panel.",
                )
                return redirect("/admin/restaurantes/restaurante/add/")

            messages.warning(
                request, "Completa el registro de tu restaurante para continuar."
            )
            return redirect("registro")

        # Restaurante inactivo
        if not restaurante.activo:
            messages.error(
                request,
                "Tu restaurante está inactivo. Contacta con el administrador.",
            )
            return redirect("home")

        # Todo bien: exponerlo a las vistas
        request.restaurante = restaurante
        return None
