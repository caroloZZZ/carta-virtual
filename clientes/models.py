from django.db import models
from django.contrib.auth.models import User
from restaurantes.models import Restaurante


class Cliente(models.Model):
    """Información de clientes recurrentes"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # Preferencias
    restaurantes_favoritos = models.ManyToManyField(Restaurante, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
