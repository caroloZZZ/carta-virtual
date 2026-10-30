from django.db import models
from django.utils import timezone
from restaurantes.models import Restaurante
from menu.models import Plato


class Pedido(models.Model):
    """Pedidos realizados por clientes"""

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmado", "Confirmado"),
        ("preparando", "Preparando"),
        ("listo", "Listo"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]

    METODOS_PAGO = [
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("tarjeta", "Tarjeta"),
    ]

    codigo = models.CharField(max_length=10, unique=True, blank=True)
    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name="pedidos"
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    # Información del cliente
    nombre_cliente = models.CharField(max_length=100)
    telefono_cliente = models.CharField(max_length=20, blank=True)

    notas = models.TextField(blank=True)
    mesa = models.CharField(
        max_length=10, blank=True, null=True, help_text="Número de mesa"
    )
    # Información de pago
    metodo_pago = models.CharField(
        max_length=20, choices=METODOS_PAGO, default="efectivo"
    )
    pagado = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Tiempos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_listo = models.DateTimeField(null=True, blank=True)
    fecha_entregado = models.DateTimeField(null=True, blank=True)

    @property
    def progreso(self):
        estados = ["pendiente", "confirmado", "preparando", "listo", "entregado"]
        if self.estado in estados:
            return int((estados.index(self.estado) / (len(estados) - 1)) * 100)
        return 0

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Pedido {self.codigo} - {self.restaurante}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único
            import random
            import string

            self.codigo = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )

        super().save(*args, **kwargs)

    def calcular_total(self):
        """Calcula el total sumando todos los items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save(update_fields=["total"])
        return total


class ItemPedido(models.Model):
    """Items individuales dentro de un pedido"""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

        # Actualizar total del pedido
        self.pedido.calcular_total()

        # Incrementar contador del plato
        self.plato.incrementar_pedidos()

    def __str__(self):
        return f"{self.cantidad}x {self.plato.nombre}"
