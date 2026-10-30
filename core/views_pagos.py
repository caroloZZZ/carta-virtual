from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
import json
import os

from pedidos.models import Pedido
from .models import Transaccion, Factura, MetodoPago, Restaurante
from .forms_pagos import PropinaForm, PagoTarjetaForm, PagoTransfermovilForm


@login_required
def lista_transacciones(request):
    """Lista todas las transacciones del restaurante"""
    restaurante = request.user.restaurante
    transacciones = Transaccion.objects.filter(pedido__restaurante=restaurante)

    # Filtros
    estado = request.GET.get("estado", "")
    metodo = request.GET.get("metodo", "")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")

    if estado:
        transacciones = transacciones.filter(estado=estado)

    if metodo:
        transacciones = transacciones.filter(metodo_pago__tipo=metodo)

    if fecha_inicio:
        transacciones = transacciones.filter(creada_en__date__gte=fecha_inicio)

    if fecha_fin:
        transacciones = transacciones.filter(creada_en__date__lte=fecha_fin)

    # Estadísticas
    hoy = timezone.now().date()
    transacciones_hoy = transacciones.filter(creada_en__date=hoy, estado="completada")
    ingresos_hoy = sum(t.monto_total for t in transacciones_hoy)

    transacciones_mes = transacciones.filter(
        creada_en__month=hoy.month, creada_en__year=hoy.year, estado="completada"
    )
    ingresos_mes = sum(t.monto_total for t in transacciones_mes)

    context = {
        "transacciones": transacciones.order_by("-creada_en"),
        "estados": Transaccion.ESTADOS,
        "metodos_pago": MetodoPago.TIPOS,
        "ingresos_hoy": ingresos_hoy,
        "ingresos_mes": ingresos_mes,
        "transacciones_hoy_count": transacciones_hoy.count(),
    }
    return render(request, "dashboard/pagos/lista_transacciones.html", context)


@login_required
def detalle_transaccion(request, transaccion_id):
    """Ver detalles de una transacción"""
    restaurante = request.user.restaurante
    transaccion = get_object_or_404(
        Transaccion, id=transaccion_id, pedido__restaurante=restaurante
    )

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "completar" and transaccion.estado == "pendiente":
            # Simular pago exitoso
            transaccion.marcar_como_completada(
                codigo_transaccion=f"SIM{transaccion.id:06d}"
            )
            messages.success(
                request, f"Transacción {transaccion.codigo_transaccion} completada"
            )

        elif accion == "reembolsar" and transaccion.estado == "completada":
            transaccion.estado = "reembolsada"
            transaccion.save()
            messages.warning(
                request, f"Transacción {transaccion.codigo_transaccion} reembolsada"
            )

        elif accion == "generar_factura" and transaccion.estado == "completada":
            # Crear factura si no existe
            if not hasattr(transaccion, "factura"):
                factura = Factura.objects.create(
                    transaccion=transaccion,
                    restaurante=restaurante,
                    cliente_nombre=transaccion.pedido.nombre_cliente,
                    cliente_telefono=transaccion.pedido.telefono_cliente,
                    subtotal=transaccion.pedido.total,
                    propina=transaccion.propina,
                    total=transaccion.monto_total,
                )
                messages.success(request, f"Factura {factura.numero_factura} generada")
            else:
                messages.info(request, "La factura ya existe")

        return redirect("detalle_transaccion", transaccion_id=transaccion.id)

    context = {
        "transaccion": transaccion,
        "factura": getattr(transaccion, "factura", None),
    }
    return render(request, "dashboard/pagos/detalle_transaccion.html", context)


@login_required
def configurar_metodos_pago(request):
    """Configurar métodos de pago aceptados por el restaurante"""
    restaurante = request.user.restaurante

    if request.method == "POST":
        # Actualizar métodos de pago activos
        metodos_activos = request.POST.getlist("metodos_activos")

        for tipo, _ in MetodoPago.TIPOS:
            metodo, created = MetodoPago.objects.get_or_create(
                restaurante=restaurante, tipo=tipo, defaults={"activo": False}
            )
            metodo.activo = tipo in metodos_activos

            # Configuración específica para cada método
            if tipo == "tarjeta":
                metodo.configuracion = {
                    "comision_porcentaje": float(
                        request.POST.get("comision_tarjeta", 0)
                    ),
                    "acepta_credito": "acepta_credito" in request.POST,
                    "acepta_debito": "acepta_debito" in request.POST,
                }
            elif tipo == "transferencia":
                metodo.configuracion = {
                    "banco": request.POST.get("banco", ""),
                    "cuenta": request.POST.get("cuenta", ""),
                    "titular": request.POST.get("titular", ""),
                }
            elif tipo == "qr":
                metodo.configuracion = {
                    "tipo_qr": request.POST.get("tipo_qr", "transfermovil"),
                    "telefono": request.POST.get("telefono_qr", ""),
                }

            metodo.save()

        messages.success(request, "Métodos de pago actualizados")
        return redirect("configurar_metodos_pago")

    # Obtener o crear métodos de pago para este restaurante
    metodos = MetodoPago.objects.filter(restaurante=restaurante)
    metodos_dict = {m.tipo: m for m in metodos}

    context = {
        "metodos": metodos_dict,
        "tipos_metodos": MetodoPago.TIPOS,
    }
    return render(request, "dashboard/pagos/configurar_metodos.html", context)


@login_required
def reportes_financieros(request):
    """Reportes financieros del restaurante"""
    restaurante = request.user.restaurante

    # Parámetros de fecha
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")

    # Filtrar transacciones
    transacciones = Transaccion.objects.filter(
        pedido__restaurante=restaurante, estado="completada"
    )

    if fecha_inicio:
        transacciones = transacciones.filter(completada_en__date__gte=fecha_inicio)

    if fecha_fin:
        transacciones = transacciones.filter(completada_en__date__lte=fecha_fin)

    # Estadísticas generales
    total_ingresos = sum(t.monto_total for t in transacciones)
    total_propinas = sum(t.propina for t in transacciones)
    total_comisiones = sum(t.comision for t in transacciones)

    # Ingresos por método de pago
    ingresos_por_metodo = {}
    for metodo in MetodoPago.objects.filter(restaurante=restaurante, activo=True):
        trans_metodo = transacciones.filter(metodo_pago=metodo)
        ingresos_por_metodo[metodo.get_tipo_display()] = {
            "cantidad": trans_metodo.count(),
            "total": sum(t.monto_total for t in trans_metodo),
            "comisiones": sum(t.comision for t in trans_metodo),
        }

    # Transacciones por día (para gráfico)
    import collections

    transacciones_por_dia = collections.defaultdict(lambda: {"count": 0, "total": 0})
    for t in transacciones:
        dia = t.completada_en.date().isoformat()
        transacciones_por_dia[dia]["count"] += 1
        transacciones_por_dia[dia]["total"] += float(t.monto_total)

    context = {
        "total_ingresos": total_ingresos,
        "total_propinas": total_propinas,
        "total_comisiones": total_comisiones,
        "ingresos_por_metodo": ingresos_por_metodo,
        "transacciones_por_dia": dict(transacciones_por_dia),
        "transacciones_count": transacciones.count(),
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    return render(request, "dashboard/pagos/reportes_financieros.html", context)


# VISTAS PÚBLICAS (para clientes)


@csrf_exempt
@require_POST
def procesar_pago(request, pedido_id):
    """Procesar pago de un pedido (API)"""
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        data = json.loads(request.body)

        # Verificar que el pedido no esté ya pagado
        if pedido.pagado:
            return JsonResponse({"success": False, "error": "El pedido ya fue pagado"})

        # Obtener método de pago
        metodo_tipo = data.get("metodo_pago", "efectivo")
        metodo = MetodoPago.objects.filter(
            restaurante=pedido.restaurante, tipo=metodo_tipo, activo=True
        ).first()

        if not metodo:
            return JsonResponse(
                {"success": False, "error": "Método de pago no disponible"}
            )

        # Obtener transacción existente o crear una nueva
        transaccion, created = Transaccion.objects.get_or_create(
            pedido=pedido,
            defaults={
                "metodo_pago": metodo,
                "monto": pedido.total,
                "estado": "pendiente",
            },
        )

        # Procesar propina
        propina_porcentaje = data.get("propina_porcentaje", 0)
        propina_manual = data.get("propina_manual", 0)

        if propina_manual:
            transaccion.propina = float(propina_manual)
        elif propina_porcentaje:
            transaccion.propina = float(pedido.total) * float(propina_porcentaje) / 100
            transaccion.propina_porcentaje = propina_porcentaje

        # Calcular comisión según método de pago
        if metodo.tipo == "tarjeta":
            comision_porcentaje = metodo.configuracion.get("comision_porcentaje", 2.5)
            transaccion.comision = float(pedido.total) * comision_porcentaje / 100
        else:
            transaccion.comision = 0

        # Simular procesamiento de pago (en producción se integraría con pasarela real)
        if metodo.tipo == "efectivo":
            # Pago en efectivo: marcamos como completado inmediatamente
            transaccion.marcar_como_completada(
                codigo_transaccion=f"EFE{transaccion.id:06d}"
            )
        elif metodo.tipo == "tarjeta":
            # Simular validación de tarjeta
            numero_tarjeta = data.get("numero_tarjeta", "")
            if len(numero_tarjeta.replace(" ", "")) < 16:
                return JsonResponse(
                    {"success": False, "error": "Número de tarjeta inválido"}
                )

            # Simular pago exitoso con tarjeta
            transaccion.marcar_como_completada(
                codigo_transaccion=f"TAR{transaccion.id:06d}",
                datos={"tarjeta": numero_tarjeta[-4:]},
            )
        elif metodo.tipo == "qr":
            # Simular pago con Transfermóvil/EnZona
            transaccion.marcar_como_completada(
                codigo_transaccion=f"QR{transaccion.id:06d}",
                datos={"tipo_qr": data.get("tipo_qr", "transfermovil")},
            )

        # Generar factura automáticamente
        factura = Factura.objects.create(
            transaccion=transaccion,
            restaurante=pedido.restaurante,
            cliente_nombre=pedido.nombre_cliente,
            cliente_telefono=pedido.telefono_cliente,
            subtotal=pedido.total,
            propina=transaccion.propina,
            total=transaccion.monto_total,
        )

        return JsonResponse(
            {
                "success": True,
                "transaccion_id": transaccion.id,
                "codigo_transaccion": transaccion.codigo_transaccion,
                "factura_numero": factura.numero_factura,
                "monto_total": transaccion.monto_total,
            }
        )

    except Pedido.DoesNotExist:
        return JsonResponse({"success": False, "error": "Pedido no encontrado"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def descargar_factura(request, factura_id):
    """Descargar factura en PDF"""
    factura = get_object_or_404(Factura, id=factura_id)

    # Verificar permisos (solo el restaurante o el cliente asociado)
    # En una implementación real, se verificaría que el usuario tenga acceso

    if factura.pdf and os.path.exists(factura.pdf.path):
        return FileResponse(
            factura.pdf.open(),
            as_attachment=True,
            filename=f"factura-{factura.numero_factura}.pdf",
        )
    else:
        # Generar PDF si no existe
        # Aquí implementarías la generación de PDF con ReportLab o WeasyPrint
        # Por ahora, retornamos un mensaje
        messages.error(request, "No se pudo generar la factura")
        return redirect("detalle_transaccion", transaccion_id=factura.transaccion.id)


def checkout_pago(request, pedido_id):
    """Checkout para realizar el pago"""
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Verificar que el pedido no esté ya pagado
    if pedido.pagado:
        messages.info(request, "Este pedido ya fue pagado")
        return redirect("seguimiento_pedido", pedido_id=pedido.id)

    # Obtener métodos de pago activos del restaurante
    metodos_pago = MetodoPago.objects.filter(
        restaurante=pedido.restaurante, activo=True
    )

    context = {
        "pedido": pedido,
        "metodos_pago": metodos_pago,
        "propina_form": PropinaForm(),
    }
    return render(request, "clientes/checkout_pago.html", context)
