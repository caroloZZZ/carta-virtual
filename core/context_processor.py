from pedidos.models import Pedido, ItemPedido
from reservas.models import Reserva  # Cambiado de pedidos.models a reservas.models
from menu.models import Categoria, Plato
from restaurantes.models import Restaurante
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


def global_context(request):
    """Context processor para pasar variables globales a todas las plantillas"""
    context = {}

    if request.user.is_authenticated:
        try:
            restaurante = request.user.restaurante
            # Notificaciones no leídas
            from core.models import Notificacion

            context["notificaciones_no_leidas"] = Notificacion.objects.filter(
                usuario=request.user, leida=False
            ).count()

            # Pedidos pendientes hoy (para el badge)
            hoy = timezone.now().date()
            context["pedidos_hoy"] = Pedido.objects.filter(
                restaurante=restaurante,
                fecha_creacion__date=hoy,
                estado__in=["pendiente", "confirmado", "preparando"],
            ).count()

            # Reservas pendientes hoy
            context["reservas_hoy"] = Reserva.objects.filter(
                restaurante=restaurante, fecha=hoy, estado="pendiente"
            ).count()

        except:
            pass

    return context
