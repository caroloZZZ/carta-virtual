from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json

from .models import Notificacion


@login_required
def lista_notificaciones(request):
    """Lista de notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by(
        "-creada_en"
    )

    # Contar no leídas
    no_leidas = notificaciones.filter(leida=False).count()

    context = {
        "notificaciones": notificaciones,
        "no_leidas": no_leidas,
    }
    return render(request, "dashboard/notificaciones/lista.html", context)


@csrf_exempt
@require_POST
@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Marcar una notificación como leída"""
    try:
        notificacion = Notificacion.objects.get(
            id=notificacion_id, usuario=request.user
        )
        notificacion.marcar_como_leida()

        return JsonResponse(
            {
                "success": True,
                "notificacion_id": notificacion.id,
            }
        )
    except Notificacion.DoesNotExist:
        return JsonResponse({"success": False, "error": "Notificación no encontrada"})


@csrf_exempt
@require_POST
@login_required
def marcar_todas_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    try:
        notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False)
        count = notificaciones.count()

        notificaciones.update(leida=True, leida_en=timezone.now())

        return JsonResponse(
            {
                "success": True,
                "marcadas": count,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def api_notificaciones(request):
    """API para obtener notificaciones no leídas (para polling/AJAX)"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user, leida=False
    ).order_by("-creada_en")[:10]

    data = []
    for notif in notificaciones:
        data.append(
            {
                "id": notif.id,
                "tipo": notif.tipo,
                "titulo": notif.titulo,
                "mensaje": notif.mensaje,
                "url": notif.url,
                "creada_en": notif.creada_en.strftime("%H:%M"),
                "data": notif.data,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "notificaciones": data,
            "total": notificaciones.count(),
        }
    )
