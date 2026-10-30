import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from restaurantes.models import Restaurante
from menu.models import Categoria, Plato


@pytest.mark.django_db
class TestCartaPublica:
    @pytest.fixture
    def restaurante(self):
        user = User.objects.create_user(username="menuvendor", password="123")
        return Restaurante.objects.create(
            usuario=user,
            nombre="Resto Carta",
            descripcion="...",
            direccion="...",
            telefono="12345678",
            email="carta@test.com",
        )

    def test_carta_publica_get(self, client, restaurante):
        url = reverse("clientes:carta_publica", args=[restaurante.qr_uuid])
        response = client.get(url)
        assert response.status_code == 200
        assert "cliente/carta.html" in [t.name for t in response.templates]
