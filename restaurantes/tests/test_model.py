import pytest
from django.contrib.auth.models import User
from restaurantes.models import Restaurante


@pytest.mark.django_db
class TestRestauranteModel:
    def test_crear_restaurante(self):
        user = User.objects.create_user(username="test", password="123")
        restaurante = Restaurante.objects.create(
            usuario=user,
            nombre="Mi Restaurante",
            slug="mi-restaurante",
            descripcion="Descripción de prueba",
            direccion="Calle Falsa 123",
            telefono="12345678",
            email="test@rest.com",
        )
        assert restaurante.nombre == "Mi Restaurante"
        assert restaurante.activo is True
        assert restaurante.qr_uuid is not None
        assert restaurante.qr_code is not None

    def test_incrementar_visitas(self):
        user = User.objects.create_user(username="test2", password="123")
        restaurante = Restaurante.objects.create(
            usuario=user,
            nombre="Otro Restaurante",
            slug="otro-restaurante",
            descripcion="...",
            direccion="...",
            telefono="12345678",
            email="test2@rest.com",
        )
        visitas_inicial = restaurante.visitas_qr
        restaurante.incrementar_visitas()
        restaurante.refresh_from_db()
        assert restaurante.visitas_qr == visitas_inicial + 1

    def test_get_qr_url(self):
        user = User.objects.create_user(username="test3", password="123")
        restaurante = Restaurante.objects.create(
            usuario=user,
            nombre="QR Test",
            slug="qr-test",
            descripcion="...",
            direccion="...",
            telefono="12345678",
            email="test3@rest.com",
        )
        assert restaurante.get_qr_url() == f"/cliente/{restaurante.qr_uuid}/"
