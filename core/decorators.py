"""
Decoradores de autorización basados en el restaurante del usuario.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


def restaurante_required(view_func):
    """
    Exige que el usuario esté autenticado y tenga un restaurante activo.
    Si no tiene restaurante → lo manda al registro.
    Si el restaurante está inactivo → lo manda al home.
    """

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        restaurante = getattr(request.user, "restaurante", None)

        if restaurante is None:
            if request.user.is_superuser:
                messages.info(
                    request,
                    "Aún no tienes un restaurante. Crea uno para acceder al panel.",
                )
                return redirect("/admin/restaurantes/restaurante/add/")

            messages.error(request, "Debes completar el registro de tu restaurante.")
            return redirect("registro")

        if not restaurante.activo:
            messages.error(
                request, "Tu restaurante está inactivo. Contacta al administrador."
            )
            return redirect("home")

        # Exponerlo también por comodidad
        request.restaurante = restaurante
        return view_func(request, *args, **kwargs)

    return _wrapped_view
