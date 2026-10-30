from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from decouple import config
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.urls import reverse


class Restaurante(models.Model):
    """Modelo principal del restaurante"""

    TIPO_RESTAURANTE = [
        ("restaurante", "Restaurante"),
        ("cafeteria", "Cafetería"),
        ("paladar", "Paladar"),
        ("bar", "Bar"),
        ("pizzeria", "Pizzería"),
    ]

    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="restaurante"
    )
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    tipo = models.CharField(
        max_length=20, choices=TIPO_RESTAURANTE, default="restaurante"
    )
    descripcion = models.TextField()
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to="restaurantes/logos/", blank=True, null=True)
    portada = models.ImageField(
        upload_to="restaurantes/portadas/", blank=True, null=True
    )

    # Configuración
    activo = models.BooleanField(default=True)
    verificado = models.BooleanField(default=False)
    mostrar_precios = models.BooleanField(default=True)
    acepta_pedidos = models.BooleanField(default=True)
    acepta_reservas = models.BooleanField(default=True)

    # QR
    qr_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    # Estadísticas
    visitas_qr = models.IntegerField(default=0)
    total_pedidos = models.IntegerField(default=0)

    # Fechas
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_registro"]
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Generar slug automáticamente si no existe
        if not self.slug:
            self.slug = slugify(self.nombre)

        # Generar código QR si no existe
        if not self.qr_code:
            base_url = config("BASE_URL", default="http://localhost:8000")
            url = f"{base_url}{reverse('clientes:carta_publica', args=[self.qr_uuid])}"
            img = qrcode.make(url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            self.qr_code.save(f"qr_{self.slug}.png", File(buffer), save=False)
        super().save(*args, **kwargs)

    def get_qr_url(self):
        """URL para acceder a la carta (relativa)"""
        return f"/cliente/{self.qr_uuid}/"

    def get_absolute_qr_url(self):
        from django.conf import settings

        base_url = settings.BASE_URL
        return f"{base_url}{self.get_qr_url()}"

    def incrementar_visitas(self):
        """Incrementa contador de visitas"""
        self.visitas_qr += 1
        self.save(update_fields=["visitas_qr"])

    def total_platos(self):
        """Retorna el total de platos del restaurante"""
        from menu.models import Plato

        return Plato.objects.filter(categoria__restaurante=self).count()

    @property
    def pedidos_pendientes(self):
        return self.pedidos.filter(estado="pendiente").count()
