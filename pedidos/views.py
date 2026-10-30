from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from .models import Pedido, ItemPedido
from menu.models import Plato
from restaurantes.models import Restaurante


@login_required
def lista_pedidos(request):
    """Lista de pedidos del restaurante"""
    restaurante = request.user.restaurante
    pedidos = Pedido.objects.filter(restaurante=restaurante).order_by("-fecha_creacion")

    context = {
        "pedidos": pedidos,
        "titulo": "Pedidos",
    }
    return render(request, "dashboard/pedidos.html", context)


@login_required
def detalle_pedido(request, pedido_id):
    """Detalle de un pedido específico"""
    pedido = get_object_or_404(
        Pedido, id=pedido_id, restaurante=request.user.restaurante
    )

    context = {
        "pedido": pedido,
        "titulo": f"Pedido {pedido.codigo}",
    }
    return render(request, "dashboard/detalle_pedido.html", context)


def crear_pedido_api(request):
    """API para crear pedido desde el carrito"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Implementar creación de pedido
            return JsonResponse({"success": True, "pedido_id": 1})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False})
