from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from reservas.models import Reserva
from pedidos.models import Pedido
from django.db.models import F
from core.models import Notificacion


@receiver(post_save, sender=Reserva)
def crear_notificacion_reserva(sender, instance, created, **kwargs):
    """Crear notificación cuando se hace una nueva reserva"""
    if created:
        Notificacion.crear_notificacion(
            usuario=instance.restaurante.usuario,
            tipo="reserva_nueva",
            titulo="¡Nueva Reserva!",
            mensaje=f"{instance.nombre_cliente} ha reservado para {instance.fecha} a las {instance.hora}",
            url=f"/dashboard/reservas/{instance.id}/",
            data={
                "reserva_id": instance.id,
                "codigo": instance.codigo,
                "cliente": instance.nombre_cliente,
                "fecha": instance.fecha.isoformat(),
                "hora": instance.hora.strftime("%H:%M"),
            },
        )


@receiver(post_save, sender=Pedido)
def crear_notificacion_pedido(sender, instance, created, **kwargs):
    """Crear notificación cuando se hace un nuevo pedido"""
    if created:
        Notificacion.crear_notificacion(
            usuario=instance.restaurante.usuario,
            tipo="pedido_nuevo",
            titulo="¡Nuevo Pedido!",
            mensaje=f"Pedido {instance.codigo} - ${instance.total}",
            url=f"/dashboard/pedidos/{instance.id}/",
            data={
                "pedido_id": instance.id,
                "codigo": instance.codigo,
                "total": float(instance.total),
                "estado": instance.estado,
            },
        )

    # Notificar cambio de estado a "listo"
    # Necesitamos verificar si el estado cambió
    if instance.pk:
        try:
            old_instance = Pedido.objects.get(pk=instance.pk)
            if old_instance.estado != "listo" and instance.estado == "listo":
                Notificacion.crear_notificacion(
                    usuario=instance.restaurante.usuario,
                    tipo="pedido_listo",
                    titulo="¡Pedido Listo!",
                    mensaje=f"El pedido {instance.codigo} está listo para servir",
                    url=f"/dashboard/pedidos/{instance.id}/",
                    data={
                        "pedido_id": instance.id,
                        "codigo": instance.codigo,
                        "mesa": instance.mesa,
                    },
                )
        except Pedido.DoesNotExist:
            pass


@receiver(post_save, sender=Reserva)
def notificar_cambio_estado_reserva(sender, instance, **kwargs):
    """Notificar cambios de estado en reservas"""
    if instance.pk:
        try:
            old_instance = Reserva.objects.get(pk=instance.pk)
            if old_instance.estado != instance.estado:
                if instance.estado == "confirmada":
                    Notificacion.crear_notificacion(
                        usuario=instance.restaurante.usuario,
                        tipo="reserva_confirmada",
                        titulo="Reserva Confirmada",
                        mensaje=f"Has confirmado la reserva {instance.codigo}",
                        url=f"/dashboard/reservas/{instance.id}/",
                        data={
                            "reserva_id": instance.id,
                            "codigo": instance.codigo,
                            "cliente": instance.nombre_cliente,
                        },
                    )
                elif instance.estado == "cancelada":
                    Notificacion.crear_notificacion(
                        usuario=instance.restaurante.usuario,
                        tipo="reserva_cancelada",
                        titulo="Reserva Cancelada",
                        mensaje=f"Se ha cancelado la reserva {instance.codigo}",
                        url=f"/dashboard/reservas/{instance.id}/",
                        data={
                            "reserva_id": instance.id,
                            "codigo": instance.codigo,
                            "cliente": instance.nombre_cliente,
                        },
                    )
        except Reserva.DoesNotExist:
            pass
