import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from restaurantes.models import Restaurante


@pytest.mark.django_db
class TestRegistroRestaurante:
    def test_registro_get(self, client):
        url = reverse("registro")
        response = client.get(url)
        assert response.status_code == 200
        assert "auth/register.html" in [t.name for t in response.templates]

    def test_registro_post_valido(self, client):
        url = reverse("registro")
        data = {
            "username": "nuevorest",
            "email": "nuevo@rest.com",
            "password1": "Compleja123!",
            "password2": "Compleja123!",
            "nombre": "Mi Nuevo Restaurante",
            "tipo": "restaurante",
            "telefono": "55123456",
            "email": "contacto@nuevorest.com",
            "direccion": "Avenida Principal 456",
            "descripcion": "Un lugar acogedor",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse("dashboard:dashboard")
        assert User.objects.filter(username="nuevorest").exists()
        assert Restaurante.objects.filter(nombre="Mi Nuevo Restaurante").exists()
