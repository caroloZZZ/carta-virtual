import json
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from restaurantes.models import Restaurante
from menu.models import Categoria, Plato


@pytest.mark.django_db
class TestCrearPedidoAPI:
    @pytest.fixture
    def restaurante(self):
        user = User.objects.create_user(username="apiuser", password="123")
        return Restaurante.objects.create(
            usuario=user,
            nombre="Resto API",
            descripcion="...",
            direccion="...",
            telefono="12345678",
            email="api@test.com",
        )

    @pytest.fixture
    def plato(self, restaurante):
        categoria = Categoria.objects.create(
            restaurante=restaurante, nombre="Categoria API"
        )
        return Plato.objects.create(
            categoria=categoria, nombre="Plato API", precio=12.50
        )

    def test_crear_pedido_post(self, client, restaurante, plato):
        url = reverse("clientes:crear_pedido_api", args=[restaurante.qr_uuid])
        data = {
            "nombre_cliente": "Test",
            "items": [{"plato_id": plato.id, "cantidad": 2}],
        }
        response = client.post(url, json.dumps(data), content_type="application/json")
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["success"] is True
        assert "pedido_id" in res_json
