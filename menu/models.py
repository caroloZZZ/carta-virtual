from django.db import models
from restaurantes.models import Restaurante
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Categoria(models.Model):
    """Categorías del menú"""

    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name="categorias"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    icono = models.CharField(max_length=50, blank=True, default="fas fa-utensils")

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        unique_together = ["restaurante", "nombre"]

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    """Platos del menú"""

    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name="platos"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to="menu/platos/", blank=True, null=True)

    # Características
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    es_vegetariano = models.BooleanField(default=False)
    es_picante = models.BooleanField(default=False)
    contiene_gluten = models.BooleanField(default=False)

    # Información adicional (NUEVOS CAMPOS)
    ingredientes = models.TextField(
        blank=True, null=True, help_text="Ingredientes del plato"
    )
    preparacion = models.TextField(
        blank=True, null=True, help_text="Descripción de la preparación"
    )

    # Información nutricional (opcional)
    calorias = models.IntegerField(null=True, blank=True)
    tiempo_preparacion = models.IntegerField(default=15, help_text="Minutos")

    # Estadísticas
    veces_pedido = models.IntegerField(default=0)

    imagen_miniatura = ImageSpecField(
        source="imagen",
        processors=[ResizeToFill(300, 300)],
        format="WEBP",
        options={"quality": 80},
    )

    class Meta:
        ordering = ["categoria__orden", "nombre"]
        verbose_name = "Plato"
        verbose_name_plural = "Platos"

    def __str__(self):
        return self.nombre

    def incrementar_pedidos(self):
        """Incrementa contador de pedidos"""
        self.veces_pedido += 1
        self.save(update_fields=["veces_pedido"])

    def get_thumbnail_url(self):
        if self.imagen:
            return self.imagen_miniatura.url
        return "/static/images/placeholder.png"
