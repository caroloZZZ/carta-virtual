from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
import calendar
import json

from restaurantes.models import Restaurante
from menu.models import Categoria, Plato
from pedidos.models import Pedido, ItemPedido
from django.contrib.auth.models import User
from restaurantes.forms import RestauranteForm
from reservas.models import Reserva


# ============================================
# DASHBOARD PRINCIPAL
# ============================================
@login_required
def dashboard(request):
    restaurante = request.user.restaurante
    hoy = timezone.now().date()
    pedidos_hoy = Pedido.objects.filter(
        restaurante=restaurante, fecha_creacion__date=hoy
    ).count()
    pedidos_pendientes = Pedido.objects.filter(
        restaurante=restaurante, estado="pendiente"
    ).count()
    pedidos_recientes = Pedido.objects.filter(restaurante=restaurante).order_by(
        "-fecha_creacion"
    )[:5]
    platos_populares = (
        ItemPedido.objects.filter(pedido__restaurante=restaurante)
        .values("plato__nombre")
        .annotate(total=Sum("cantidad"))
        .order_by("-total")[:5]
    )

    return render(
        request,
        "dashboard/index.html",
        {
            "restaurante": restaurante,
            "pedidos_hoy": pedidos_hoy,
            "pedidos_pendientes": pedidos_pendientes,
            "pedidos_recientes": pedidos_recientes,
            "platos_populares": platos_populares,
        },
    )


# ============================================
# MI RESTAURANTE (PERFIL)
# ============================================
@login_required
def mi_restaurante(request):
    restaurante = request.user.restaurante
    if request.method == "POST":
        form = RestauranteForm(request.POST, request.FILES, instance=restaurante)
        if form.is_valid():
            form.save()
            messages.success(request, "Información actualizada correctamente")
            return redirect("dashboard:mi_restaurante")
    else:
        form = RestauranteForm(instance=restaurante)
    return render(
        request,
        "dashboard/mi_restaurante.html",
        {
            "restaurante": restaurante,
            "form": form,
        },
    )


# ============================================
# GESTIÓN DE MENÚ - CATEGORÍAS
# ============================================
@login_required
def lista_categorias(request):
    restaurante = request.user.restaurante
    categorias = Categoria.objects.filter(restaurante=restaurante).order_by("orden")
    return render(
        request,
        "dashboard/categorias.html",
        {
            "categorias": categorias,
            "titulo": "Categorías",
        },
    )


@login_required
def crear_categoria(request):
    if request.method == "POST":
        restaurante = request.user.restaurante
        categoria = Categoria.objects.create(
            restaurante=restaurante,
            nombre=request.POST.get("nombre"),
            descripcion=request.POST.get("descripcion", ""),
            orden=request.POST.get("orden", 0),
            icono=request.POST.get("icono", "bi-tag"),
            activa=request.POST.get("activa") == "on",
        )
        messages.success(
            request, f'Categoría "{categoria.nombre}" creada correctamente'
        )
        return redirect("dashboard:lista_categorias")
    return redirect("dashboard:lista_categorias")


@login_required
def editar_categoria(request, categoria_id):
    restaurante = request.user.restaurante
    categoria = get_object_or_404(Categoria, id=categoria_id, restaurante=restaurante)
    if request.method == "POST":
        categoria.nombre = request.POST.get("nombre", categoria.nombre)
        categoria.descripcion = request.POST.get("descripcion", categoria.descripcion)
        categoria.orden = request.POST.get("orden", categoria.orden)
        categoria.icono = request.POST.get("icono", categoria.icono)
        categoria.activa = request.POST.get("activa") == "on"
        categoria.save()
        messages.success(request, "Categoría actualizada correctamente")
        return redirect("dashboard:lista_categorias")
    return JsonResponse(
        {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "orden": categoria.orden,
            "icono": categoria.icono,
            "activa": categoria.activa,
        }
    )


@login_required
def eliminar_categoria(request, categoria_id):
    if request.method == "DELETE":
        restaurante = request.user.restaurante
        categoria = get_object_or_404(
            Categoria, id=categoria_id, restaurante=restaurante
        )
        categoria.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


# ============================================
# GESTIÓN DE MENÚ - PLATOS
# ============================================
@login_required
def lista_platos(request):
    restaurante = request.user.restaurante
    platos = Plato.objects.filter(categoria__restaurante=restaurante).select_related(
        "categoria"
    )
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)
    return render(
        request,
        "dashboard/platos.html",
        {
            "platos": platos,
            "categorias": categorias,
            "titulo": "Platos",
        },
    )


@login_required
def crear_plato(request):
    restaurante = request.user.restaurante
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)
    if request.method == "POST":
        categoria = get_object_or_404(
            Categoria, id=request.POST.get("categoria"), restaurante=restaurante
        )
        plato = Plato.objects.create(
            categoria=categoria,
            nombre=request.POST.get("nombre"),
            descripcion=request.POST.get("descripcion", ""),
            precio=request.POST.get("precio"),
            disponible=request.POST.get("disponible") == "on",
            destacado=request.POST.get("destacado") == "on",
            es_vegetariano=request.POST.get("vegetariano") == "on",
            es_picante=request.POST.get("picante") == "on",
            contiene_gluten=request.POST.get("gluten") == "on",
            tiempo_preparacion=request.POST.get("tiempo_preparacion", 15),
            ingredientes=request.POST.get("ingredientes", ""),
            preparacion=request.POST.get("preparacion", ""),
        )
        if "imagen" in request.FILES:
            plato.imagen = request.FILES["imagen"]
            plato.save()
        messages.success(request, f'Plato "{plato.nombre}" creado correctamente')
        return redirect("dashboard:platos")
    return render(
        request,
        "dashboard/menu/crear_plato.html",
        {
            "categorias": categorias,
            "titulo": "Crear Plato",
        },
    )


@login_required
def editar_plato(request, plato_id):
    restaurante = request.user.restaurante
    plato = get_object_or_404(Plato, id=plato_id, categoria__restaurante=restaurante)
    if request.method == "POST":
        plato.categoria_id = request.POST.get("categoria", plato.categoria_id)
        plato.nombre = request.POST.get("nombre", plato.nombre)
        plato.descripcion = request.POST.get("descripcion", plato.descripcion)
        plato.precio = request.POST.get("precio", plato.precio)
        plato.tiempo_preparacion = request.POST.get(
            "tiempo_preparacion", plato.tiempo_preparacion
        )
        plato.ingredientes = request.POST.get("ingredientes", plato.ingredientes)
        plato.preparacion = request.POST.get("preparacion", plato.preparacion)
        plato.disponible = request.POST.get("disponible") == "on"
        plato.destacado = request.POST.get("destacado") == "on"
        plato.es_vegetariano = request.POST.get("vegetariano") == "on"
        plato.es_picante = request.POST.get("picante") == "on"
        plato.contiene_gluten = request.POST.get("gluten") == "on"
        if "imagen" in request.FILES:
            plato.imagen = request.FILES["imagen"]
        plato.save()
        messages.success(request, "Plato actualizado correctamente")
        return redirect("dashboard:platos")
    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)
    return render(
        request,
        "dashboard/editar_plato.html",
        {
            "plato": plato,
            "categorias": categorias,
            "titulo": "Editar Plato",
        },
    )


@login_required
def eliminar_plato(request, plato_id):
    if request.method == "DELETE":
        restaurante = request.user.restaurante
        plato = get_object_or_404(
            Plato, id=plato_id, categoria__restaurante=restaurante
        )
        plato.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


# ============================================
# GESTIÓN DE PEDIDOS
# ============================================
@login_required
def lista_pedidos(request):
    restaurante = request.user.restaurante
    pedidos = Pedido.objects.filter(restaurante=restaurante).order_by("-fecha_creacion")
    return render(
        request,
        "dashboard/lista_pedidos.html",
        {
            "pedidos": pedidos,
            "titulo": "Pedidos",
        },
    )


@login_required
def detalle_pedido(request, pedido_id):
    restaurante = request.user.restaurante
    pedido = get_object_or_404(Pedido, id=pedido_id, restaurante=restaurante)
    return render(
        request,
        "dashboard/detalle_pedido.html",
        {
            "pedido": pedido,
            "titulo": f"Pedido #{pedido.codigo}",
        },
    )


@login_required
def cambiar_estado_pedido(request, pedido_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get("estado")
            restaurante = request.user.restaurante
            pedido = get_object_or_404(Pedido, id=pedido_id, restaurante=restaurante)
            pedido.estado = nuevo_estado
            if nuevo_estado == "confirmado" and not pedido.fecha_confirmacion:
                pedido.fecha_confirmacion = timezone.now()
            elif nuevo_estado == "listo" and not pedido.fecha_listo:
                pedido.fecha_listo = timezone.now()
            elif nuevo_estado == "entregado" and not pedido.fecha_entregado:
                pedido.fecha_entregado = timezone.now()
            pedido.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False}, status=405)


# ============================================
# CONFIGURACIÓN
# ============================================
@login_required
def configuracion_restaurante(request):
    restaurante = request.user.restaurante
    if request.method == "POST":
        restaurante.mostrar_precios = request.POST.get("mostrar_precios") == "on"
        restaurante.acepta_pedidos = request.POST.get("acepta_pedidos") == "on"
        restaurante.acepta_reservas = request.POST.get("acepta_reservas") == "on"
        restaurante.activo = request.POST.get("restaurante_activo") == "on"
        restaurante.save()
        messages.success(request, "Configuración actualizada")
        return redirect("dashboard:configuracion_restaurante")
    return render(
        request,
        "dashboard/configuracion.html",
        {
            "restaurante": restaurante,
            "categorias_count": Categoria.objects.filter(
                restaurante=restaurante
            ).count(),
            "platos_count": Plato.objects.filter(
                categoria__restaurante=restaurante
            ).count(),
            "destacados_count": Plato.objects.filter(
                categoria__restaurante=restaurante, destacado=True
            ).count(),
        },
    )


# ============================================
# CÓDIGO QR
# ============================================
@login_required
def ver_qr(request):
    """Muestra 2 QRs generados en backend (sin CDN). Funciona offline."""
    import qrcode
    from io import BytesIO
    import base64

    restaurante = request.user.restaurante
    url_local = f"http://{settings.LOCAL_IP}:8000{restaurante.get_qr_url()}"
    url_online = f"{settings.BASE_URL}{restaurante.get_qr_url()}"

    def _qr_b64(text):
        img = qrcode.make(text)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")

    return render(
        request,
        "dashboard/qr.html",
        {
            "restaurante": restaurante,
            "url_local": url_local,
            "url_online": url_online,
            "qr_local_b64": _qr_b64(url_local),
            "qr_online_b64": _qr_b64(url_online),
        },
    )


@login_required
def generar_qr(request):
    if request.method == "POST":
        request.user.restaurante.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


@login_required
def regenerar_qr(request):
    if request.method == "POST":
        restaurante = request.user.restaurante
        restaurante.qr_code.delete()
        restaurante.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=405)


# ============================================
# ESTADÍSTICAS
# ============================================
@login_required
def estadisticas(request):
    restaurante = request.user.restaurante
    hoy = timezone.now().date()
    semana_pasada = hoy - timedelta(days=7)
    mes_pasado = hoy - timedelta(days=30)

    pedidos_hoy = Pedido.objects.filter(
        restaurante=restaurante, fecha_creacion__date=hoy
    ).count()
    pedidos_semana = Pedido.objects.filter(
        restaurante=restaurante, fecha_creacion__date__gte=semana_pasada
    ).count()
    pedidos_mes = Pedido.objects.filter(
        restaurante=restaurante, fecha_creacion__date__gte=mes_pasado
    ).count()

    ingresos_hoy = (
        Pedido.objects.filter(
            restaurante=restaurante, fecha_creacion__date=hoy, pagado=True
        ).aggregate(total=Sum("total"))["total"]
        or 0
    )
    ingresos_semana = (
        Pedido.objects.filter(
            restaurante=restaurante,
            fecha_creacion__date__gte=semana_pasada,
            pagado=True,
        ).aggregate(total=Sum("total"))["total"]
        or 0
    )
    ingresos_mes = (
        Pedido.objects.filter(
            restaurante=restaurante, fecha_creacion__date__gte=mes_pasado, pagado=True
        ).aggregate(total=Sum("total"))["total"]
        or 0
    )

    platos_populares = (
        ItemPedido.objects.filter(pedido__restaurante=restaurante)
        .values("plato__nombre")
        .annotate(cantidad=Sum("cantidad"))
        .order_by("-cantidad")[:10]
    )

    return render(
        request,
        "dashboard/estadisticas.html",
        {
            "restaurante": restaurante,
            "pedidos_hoy": pedidos_hoy,
            "pedidos_semana": pedidos_semana,
            "pedidos_mes": pedidos_mes,
            "ingresos_hoy": ingresos_hoy,
            "ingresos_semana": ingresos_semana,
            "ingresos_mes": ingresos_mes,
            "platos_populares": platos_populares,
        },
    )


# ============================================
# RESERVAS
# ============================================
@login_required
def lista_reservas(request):
    restaurante = request.user.restaurante
    fecha_str = request.GET.get("fecha", timezone.now().date().strftime("%Y-%m-%d"))
    try:
        fecha_seleccionada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except:
        fecha_seleccionada = timezone.now().date()

    reservas_dia = Reserva.objects.filter(
        restaurante=restaurante, fecha=fecha_seleccionada
    ).order_by("hora")

    inicio_semana = fecha_seleccionada - timedelta(days=fecha_seleccionada.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    reservas_semana_raw = Reserva.objects.filter(
        restaurante=restaurante, fecha__gte=inicio_semana, fecha__lte=fin_semana
    ).order_by("fecha", "hora")

    reservas_semana = {}
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        reservas_semana[dia.strftime("%A %d/%m")] = [
            r for r in reservas_semana_raw if r.fecha == dia
        ]

    año = fecha_seleccionada.year
    mes = fecha_seleccionada.month
    cal = calendar.monthcalendar(año, mes)
    primer_dia = datetime(año, mes, 1).date()
    ultimo_dia = datetime(año, mes, calendar.monthrange(año, mes)[1]).date()
    reservas_mes = (
        Reserva.objects.filter(
            restaurante=restaurante, fecha__gte=primer_dia, fecha__lte=ultimo_dia
        )
        .values("fecha")
        .annotate(total=Count("id"))
    )
    reservas_por_fecha = {r["fecha"]: r["total"] for r in reservas_mes}

    calendario_mes = []
    for semana in cal:
        semana_data = []
        for dia in semana:
            if dia == 0:
                semana_data.append({"numero": "", "reservas": 0, "fecha": None})
            else:
                fecha_dia = datetime(año, mes, dia).date()
                semana_data.append(
                    {
                        "numero": dia,
                        "reservas": reservas_por_fecha.get(fecha_dia, 0),
                        "fecha": fecha_dia,
                    }
                )
        calendario_mes.append(semana_data)

    return render(
        request,
        "dashboard/reservas.html",
        {
            "restaurante": restaurante,
            "reservas_dia": reservas_dia,
            "reservas_semana": reservas_semana,
            "calendario_mes": calendario_mes,
            "fecha_seleccionada": fecha_seleccionada,
            "hoy": timezone.now().date(),
            "titulo": "Reservas",
        },
    )


@login_required
def detalle_reserva(request, reserva_id):
    restaurante = request.user.restaurante
    reserva = get_object_or_404(Reserva, id=reserva_id, restaurante=restaurante)
    return JsonResponse(
        {
            "id": reserva.id,
            "nombre_cliente": reserva.nombre_cliente,
            "telefono": reserva.telefono,
            "email": reserva.email or "",
            "fecha": reserva.fecha.strftime("%Y-%m-%d"),
            "hora": reserva.hora.strftime("%H:%M"),
            "personas": reserva.personas,
            "mesa": reserva.mesa or "",
            "notas": reserva.notas or "",
            "estado": reserva.estado,
        }
    )


@login_required
def crear_reserva(request):
    if request.method == "POST":
        return redirect("dashboard:guardar_reserva")
    return render(
        request,
        "dashboard/crear_reserva.html",
        {
            "titulo": "Nueva Reserva",
            "fecha_hoy": timezone.now().date().strftime("%Y-%m-%d"),
            "hora_ahora": timezone.now().strftime("%H:%M"),
        },
    )


@login_required
def editar_reserva(request, reserva_id):
    restaurante = request.user.restaurante
    reserva = get_object_or_404(Reserva, id=reserva_id, restaurante=restaurante)
    if request.method == "POST":
        return redirect("dashboard:guardar_reserva")
    return render(
        request,
        "dashboard/editar_reserva.html",
        {
            "reserva": reserva,
            "titulo": f"Editar Reserva - {reserva.nombre_cliente}",
        },
    )


@login_required
def guardar_reserva(request):
    if request.method == "POST":
        restaurante = request.user.restaurante
        reserva_id = request.POST.get("reserva_id")
        nombre = request.POST.get("nombre_cliente")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email", "")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        personas = request.POST.get("personas", 2)
        mesa = request.POST.get("mesa", "")
        notas = request.POST.get("notas", "")
        estado = request.POST.get("estado", "pendiente")

        if not nombre or not telefono or not fecha or not hora:
            messages.error(
                request, "Todos los campos obligatorios deben ser completados"
            )
            return redirect("dashboard:lista_reservas")

        try:
            if reserva_id:
                reserva = get_object_or_404(
                    Reserva, id=reserva_id, restaurante=restaurante
                )
                reserva.nombre_cliente = nombre
                reserva.telefono = telefono
                reserva.email = email
                reserva.fecha = fecha
                reserva.hora = hora
                reserva.personas = personas
                reserva.mesa = mesa
                reserva.notas = notas
                reserva.estado = estado
                reserva.save()
                messages.success(request, "Reserva actualizada correctamente")
            else:
                Reserva.objects.create(
                    restaurante=restaurante,
                    nombre_cliente=nombre,
                    telefono=telefono,
                    email=email,
                    fecha=fecha,
                    hora=hora,
                    personas=personas,
                    mesa=mesa,
                    notas=notas,
                    estado=estado,
                )
                messages.success(request, "Reserva creada correctamente")
        except Exception as e:
            messages.error(request, f"Error al guardar la reserva: {str(e)}")
        return redirect("dashboard:lista_reservas")
    return redirect("dashboard:lista_reservas")


@login_required
def eliminar_reserva(request, reserva_id):
    if request.method == "DELETE":
        restaurante = request.user.restaurante
        reserva = get_object_or_404(Reserva, id=reserva_id, restaurante=restaurante)
        nombre = reserva.nombre_cliente
        reserva.delete()
        return JsonResponse(
            {"success": True, "message": f"Reserva de {nombre} eliminada"}
        )
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)


@login_required
def cambiar_estado_reserva(request, reserva_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get("estado")
            restaurante = request.user.restaurante
            reserva = get_object_or_404(Reserva, id=reserva_id, restaurante=restaurante)
            reserva.estado = nuevo_estado
            reserva.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False}, status=405)


# ============================================
# CLIENTES
# ============================================
@login_required
def lista_clientes(request):
    restaurante = request.user.restaurante
    clientes_data = (
        Pedido.objects.filter(restaurante=restaurante)
        .values("nombre_cliente")
        .annotate(total_pedidos=Count("id"), total_gastado=Sum("total"))
        .order_by("-total_gastado")
    )
    return render(
        request,
        "dashboard/clientes.html",
        {
            "clientes": clientes_data,
            "titulo": "Clientes",
        },
    )


@login_required
def detalle_cliente(request, cliente_id):
    return JsonResponse({"success": True})


# ============================================
# NOTIFICACIONES
# ============================================
@login_required
def lista_notificaciones(request):
    return render(
        request,
        "dashboard/notificaciones.html",
        {
            "notificaciones": [],
            "no_leidas_count": 0,
        },
    )


@login_required
def marcar_notificaciones_leidas(request):
    return JsonResponse({"success": True})


# ============================================
# EXPORTACIONES
# ============================================
@login_required
def exportar_pedidos(request):
    messages.success(request, "Exportación iniciada")
    return redirect("dashboard:lista_pedidos")


@login_required
def exportar_clientes(request):
    messages.success(request, "Exportación iniciada")
    return redirect("dashboard:clientes")


@login_required
def exportar_estadisticas(request):
    messages.success(request, "Exportación iniciada")
    return redirect("dashboard:estadisticas")


# ============================================
# GESTIÓN DE MENÚ (VISTA PRINCIPAL)
# ============================================
@login_required
def gestion_menu(request):
    restaurante = request.user.restaurante
    categorias = Categoria.objects.filter(restaurante=restaurante)
    platos = Plato.objects.filter(categoria__restaurante=restaurante)
    return render(
        request,
        "dashboard/menu/gestion_menu.html",
        {
            "categorias": categorias,
            "platos": platos,
            "titulo": "Gestión de Menú",
        },
    )
