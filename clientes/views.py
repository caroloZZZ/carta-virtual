from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
import json

from restaurantes.models import Restaurante
from menu.models import Plato
from pedidos.models import Pedido, ItemPedido
from reservas.models import Reserva


# ========== UTILIDAD ==========
def is_private_ip(ip):
    return (
        ip.startswith("10.")
        or ip.startswith("192.168.")
        or ip.startswith("172.16.")
        or ip == "127.0.0.1"
    )


# ========== CARTA PÚBLICA ==========
@never_cache
def carta_publica(request, qr_uuid):
    restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)
    restaurante.incrementar_visitas()

    categorias = (
        restaurante.categorias.filter(activa=True)
        .prefetch_related("platos")
        .order_by("orden")
    )
    for categoria in categorias:
        categoria.platos_disponibles = categoria.platos.filter(disponible=True)

    es_local = is_private_ip(request.META.get("REMOTE_ADDR", ""))

    return render(
        request,
        "cliente/carta.html",
        {
            "restaurante": restaurante,
            "categorias": categorias,
            "es_local": es_local,
        },
    )


# ========== PRESENTACIÓN POR SLUG ==========
def presentacion_restaurante(request, slug):
    """Muestra una página de bienvenida del restaurante usando el slug (nombre amigable)"""
    restaurante = get_object_or_404(Restaurante, slug=slug)
    # Puedes redirigir directamente a la carta si prefieres:
    # return redirect('clientes:carta_publica', qr_uuid=restaurante.qr_uuid)
    # O mostrar una página de presentación:
    return render(request, "cliente/presentacion.html", {"restaurante": restaurante})


# ========== CARRITO ==========
def ver_carrito(request, qr_uuid):
    restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)
    return render(request, "cliente/carrito.html", {"restaurante": restaurante})


@csrf_exempt
def agregar_al_carrito(request, qr_uuid):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Método no permitido"}, status=405
        )

    try:
        data = json.loads(request.body)
        plato_id = data.get("plato_id")
        cantidad = int(data.get("cantidad", 1))

        plato = Plato.objects.get(id=plato_id)
        restaurante = Restaurante.objects.get(qr_uuid=qr_uuid)

        if plato.categoria.restaurante != restaurante:
            return JsonResponse(
                {"success": False, "error": "Plato no disponible"}, status=400
            )

        return JsonResponse(
            {
                "success": True,
                "plato": {
                    "id": plato.id,
                    "nombre": plato.nombre,
                    "precio": str(plato.precio),
                },
                "cantidad": cantidad,
                "subtotal": str(plato.precio * cantidad),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def crear_pedido_api(request, qr_uuid):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Método no permitido"}, status=405
        )

    # Solo aceptar pedidos desde IPs locales (opcional)
    if not is_private_ip(request.META.get("REMOTE_ADDR", "")):
        return JsonResponse(
            {
                "success": False,
                "error": "Los pedidos solo están disponibles dentro del restaurante.",
            },
            status=403,
        )

    try:
        data = json.loads(request.body)
        restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)

        nombre_cliente = data.get("nombre_cliente", "").strip()
        telefono_cliente = data.get("telefono_cliente", "").strip()
        mesa = data.get("mesa", "").strip()
        notas = data.get("notas", "").strip()
        items = data.get("items", [])

        if not nombre_cliente:
            return JsonResponse(
                {"success": False, "error": "El nombre es obligatorio"}, status=400
            )
        if not items:
            return JsonResponse(
                {"success": False, "error": "El carrito está vacío"}, status=400
            )

        with transaction.atomic():
            pedido = Pedido.objects.create(
                restaurante=restaurante,
                nombre_cliente=nombre_cliente,
                telefono_cliente=telefono_cliente,
                mesa=mesa,
                notas=notas,
                estado="pendiente",
                total=0,
            )

            total = 0
            for item in items:
                plato = Plato.objects.get(
                    id=item["plato_id"],
                    categoria__restaurante=restaurante,
                    disponible=True,
                )
                cantidad = item["cantidad"]
                precio = plato.precio
                subtotal = precio * cantidad
                ItemPedido.objects.create(
                    pedido=pedido,
                    plato=plato,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal,
                )
                total += subtotal

            pedido.total = total
            pedido.save()

        return JsonResponse(
            {
                "success": True,
                "pedido_id": pedido.id,
                "codigo": pedido.codigo,
                "redirect_url": f"/cliente/{qr_uuid}/pedido/{pedido.id}/",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def seguimiento_pedido(request, qr_uuid, pedido_id):
    restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)
    pedido = get_object_or_404(Pedido, id=pedido_id, restaurante=restaurante)
    return render(
        request,
        "cliente/seguimiento_pedido.html",
        {"restaurante": restaurante, "pedido": pedido},
    )


def estado_pedido_api(request, qr_uuid, pedido_id):
    if request.method == "GET":
        restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)
        pedido = get_object_or_404(Pedido, id=pedido_id, restaurante=restaurante)

        # Formatear las fechas si existen
        fechas = {}
        if pedido.fecha_confirmacion:
            fechas["confirmado"] = pedido.fecha_confirmacion.strftime("%H:%M")
        if pedido.fecha_listo:
            fechas["listo"] = pedido.fecha_listo.strftime("%H:%M")
        if pedido.fecha_entregado:
            fechas["entregado"] = pedido.fecha_entregado.strftime("%H:%M")

        return JsonResponse(
            {
                "success": True,
                "id": pedido.id,
                "estado": pedido.estado,
                "estado_display": pedido.get_estado_display(),
                "fechas": fechas,
                "total": str(pedido.total),
            }
        )
    return JsonResponse({"success": False}, status=405)


# ========== RESERVAS ==========
def reservar_mesa(request, qr_uuid):
    restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email", "")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        personas = request.POST.get("personas", 2)
        notas = request.POST.get("notas", "")

        if not nombre or not telefono or not fecha or not hora:
            messages.error(
                request, "Todos los campos obligatorios deben ser completados."
            )
            return redirect("clientes:reservar_mesa", qr_uuid=qr_uuid)

        try:
            reserva = Reserva.objects.create(
                restaurante=restaurante,
                nombre_cliente=nombre,
                telefono=telefono,
                email=email,
                fecha=fecha,
                hora=hora,
                personas=personas,
                notas=notas,
                estado="pendiente",
            )
            messages.success(
                request,
                "¡Reserva solicitada con éxito! Te contactaremos para confirmar.",
            )
            return redirect(
                "clientes:confirmacion_reserva", qr_uuid=qr_uuid, reserva_id=reserva.id
            )
        except Exception as e:
            messages.error(request, f"Error al crear la reserva: {str(e)}")
            return redirect("clientes:reservar_mesa", qr_uuid=qr_uuid)

    hoy = timezone.now().date()
    horas_disponibles = [f"{h:02d}:00" for h in range(12, 23)]
    return render(
        request,
        "cliente/reservar.html",
        {
            "restaurante": restaurante,
            "qr_uuid": qr_uuid,
            "hoy": hoy,
            "horas_disponibles": horas_disponibles,
        },
    )


def confirmacion_reserva(request, qr_uuid, reserva_id):
    restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)
    reserva = get_object_or_404(Reserva, id=reserva_id, restaurante=restaurante)
    return render(
        request,
        "cliente/confirmacion_reserva.html",
        {
            "restaurante": restaurante,
            "reserva": reserva,
        },
    )


# ========== API PARA AUTO-ACTUALIZAR MENÚ ==========
@never_cache
def menu_version_api(request, qr_uuid):
    """Devuelve la última fecha de actualización del menú para detectar cambios."""
    from django.utils import timezone

    restaurante = get_object_or_404(Restaurante, qr_uuid=qr_uuid)

    # Buscamos la última actualización del restaurante o de algún plato
    last_update = restaurante.ultima_actualizacion
    platos = (
        Plato.objects.filter(categoria__restaurante=restaurante).order_by("-id").first()
    )

    # Si hay platos, usamos el ID del último plato o su fecha, si no, la del restaurante
    version = f"{last_update.timestamp()}_{platos.id if platos else 0}"

    return JsonResponse(
        {"version": version, "updated_at": last_update.strftime("%H:%M")}
    )
