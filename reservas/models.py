from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

from restaurantes.models import Restaurante


class Reserva(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
        ("completada", "Completada"),
        ("no_show", "No Show"),
    ]

    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name="reservas"
    )
    codigo = models.CharField(max_length=10, unique=True, blank=True)

    nombre_cliente = models.CharField(max_length=100, verbose_name="Nombre del cliente")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email (opcional)")
    personas = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Número de personas",
    )

    fecha = models.DateField(verbose_name="Fecha de la reserva")
    hora = models.TimeField(verbose_name="Hora de la reserva")
    duracion = models.PositiveIntegerField(default=90, help_text="Duración en minutos")
    mesa = models.CharField(max_length=10, blank=True, verbose_name="Mesa asignada")
    notas = models.TextField(blank=True, verbose_name="Notas adicionales")

    estado = models.CharField(
        max_length=20, choices=ESTADOS, default="pendiente", verbose_name="Estado"
    )
    confirmada_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    confirmado_en = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name="Última actualización"
    )

    class Meta:
        ordering = ["-fecha", "-hora"]
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        indexes = [
            models.Index(fields=["restaurante", "fecha", "estado"]),
            models.Index(fields=["fecha", "hora"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return (
            f"{self.nombre_cliente} - {self.fecha} {self.hora} ({self.personas} pers)"
        )

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultima_reserva = Reserva.objects.order_by("-id").first()
            nuevo_numero = (ultima_reserva.id + 1) if ultima_reserva else 1
            self.codigo = f"R{nuevo_numero:06d}"
        super().save(*args, **kwargs)

    @property
    def fecha_hora_completa(self):
        return timezone.make_aware(datetime.combine(self.fecha, self.hora))

    def es_hoy(self):
        return self.fecha == timezone.now().date()

    def es_futura(self):
        return self.fecha_hora_completa > timezone.now()

    def esta_pasada(self):
        return self.fecha_hora_completa < timezone.now()

    def puede_cancelar(self):
        return self.estado in ["pendiente", "confirmada"]

    def cancelar(self):
        if self.puede_cancelar():
            self.estado = "cancelada"
            self.save()
            return True
        return False

    def confirmar(self, usuario=None):
        self.estado = "confirmada"
        if usuario:
            self.confirmada_por = usuario
        self.confirmado_en = timezone.now()
        self.save()

    def completar(self):
        self.estado = "completada"
        self.save()
