from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from restaurantes.models import Restaurante


class Auditoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    modelo = models.CharField(max_length=50)
    objeto_id = models.IntegerField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        if self.usuario:
            return f"{self.usuario} - {self.accion} - {self.fecha}"
        return f"Sistema - {self.accion} - {self.fecha}"


class ConfiguracionSistema(models.Model):
    clave = models.CharField(max_length=50, unique=True)
    valor = models.TextField()
    tipo = models.CharField(
        max_length=20,
        choices=[
            ("texto", "Texto"),
            ("numero", "Número"),
            ("booleano", "Booleano"),
            ("json", "JSON"),
        ],
    )
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.clave


class Notificacion(models.Model):
    TIPOS = [
        ("reserva_nueva", "Nueva Reserva"),
        ("reserva_confirmada", "Reserva Confirmada"),
        ("reserva_cancelada", "Reserva Cancelada"),
        ("pedido_nuevo", "Nuevo Pedido"),
        ("pedido_listo", "Pedido Listo"),
        ("sistema", "Mensaje del Sistema"),
    ]

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notificaciones"
    )
    tipo = models.CharField(max_length=30, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    leida = models.BooleanField(default=False)
    url = models.CharField(max_length=200, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    leida_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creada_en"]
        indexes = [
            models.Index(fields=["usuario", "leida"]),
            models.Index(fields=["creada_en"]),
        ]

    def __str__(self):
        return f"{self.tipo}: {self.titulo}"

    def marcar_como_leida(self):
        self.leida = True
        self.leida_en = timezone.now()
        self.save()

    @classmethod
    def crear_notificacion(cls, usuario, tipo, titulo, mensaje, url="", data=None):
        return cls.objects.create(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            url=url,
            data=data or {},
        )


class PlantillaEmail(models.Model):
    nombre = models.CharField(max_length=100)
    asunto = models.CharField(max_length=200)
    contenido = models.TextField()
    variables = models.JSONField(
        default=list, help_text="Lista de variables disponibles"
    )

    class Meta:
        verbose_name = "Plantilla de Email"
        verbose_name_plural = "Plantillas de Email"

    def __str__(self):
        return self.nombre


class Backup(models.Model):
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to="backups/")
    tamano = models.BigIntegerField(default=0)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ("completo", "Completo"),
            ("base_datos", "Base de Datos"),
            ("media", "Archivos Media"),
        ],
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if self.archivo:
            self.tamano = self.archivo.size
        super().save(*args, **kwargs)


class MetodoPago(models.Model):
    TIPOS = [
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta de Crédito/Débito"),
        ("transferencia", "Transferencia Bancaria"),
        ("enlinea", "Pago en Línea"),
        ("qr", "Pago QR"),
    ]

    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name="metodos_pago"
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    activo = models.BooleanField(default=True)
    configuracion = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ["restaurante", "tipo"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.restaurante}"


class Transaccion(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("completada", "Completada"),
        ("fallida", "Fallida"),
        ("reembolsada", "Reembolsada"),
    ]

    pedido = models.OneToOneField(
        "pedidos.Pedido", on_delete=models.CASCADE, related_name="transaccion"
    )
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    comision = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    codigo_transaccion = models.CharField(max_length=100, blank=True)
    datos_transaccion = models.JSONField(default=dict, blank=True)
    propina = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    propina_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    creada_en = models.DateTimeField(auto_now_add=True)
    completada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creada_en"]

    def __str__(self):
        return f"Transacción {self.codigo_transaccion or self.id} - {self.estado}"

    @property
    def monto_total(self):
        return self.monto + self.propina

    def marcar_como_completada(self, codigo_transaccion="", datos=None):
        self.estado = "completada"
        self.codigo_transaccion = codigo_transaccion or self.codigo_transaccion
        self.datos_transaccion = datos or self.datos_transaccion
        self.completada_en = timezone.now()
        self.save()
        self.pedido.pagado = True
        self.pedido.save()


class Factura(models.Model):
    transaccion = models.OneToOneField(
        Transaccion, on_delete=models.CASCADE, related_name="factura"
    )
    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name="facturas"
    )
    cliente_nombre = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20, blank=True)
    cliente_email = models.EmailField(blank=True)
    numero_factura = models.CharField(max_length=20, unique=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    propina = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cai = models.CharField(max_length=50, blank=True)
    rtn = models.CharField(max_length=20, blank=True)
    fecha_limite_emision = models.DateField(blank=True, null=True)
    pdf = models.FileField(upload_to="facturas/pdf/", blank=True, null=True)
    xml = models.FileField(upload_to="facturas/xml/", blank=True, null=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    anulada = models.BooleanField(default=False)
    anulada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creada_en"]

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente_nombre}"

    def save(self, *args, **kwargs):
        if not self.numero_factura:
            ultima_factura = Factura.objects.order_by("-id").first()
            nuevo_numero = (ultima_factura.id + 1) if ultima_factura else 1
            self.numero_factura = f"F001-001-{nuevo_numero:06d}"
        super().save(*args, **kwargs)
