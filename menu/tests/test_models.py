import pytest
from django.contrib.auth.models import User
from restaurantes.models import Restaurante
from menu.models import Categoria, Plato


@pytest.mark.django_db
class TestMenuModels:
    @pytest.fixture
    def restaurante(self):
        user = User.objects.create_user(username="menuuser", password="123")
        return Restaurante.objects.create(
            usuario=user,
            nombre="Menu Test",
            slug="menu-test",
            descripcion="...",
            direccion="...",
            telefono="12345678",
            email="menu@test.com",
        )

    def test_crear_categoria(self, restaurante):
        categoria = Categoria.objects.create(
            restaurante=restaurante, nombre="Entradas", orden=1
        )
        assert categoria.nombre == "Entradas"
        assert str(categoria) == "Entradas"

    def test_crear_plato(self, restaurante):
        categoria = Categoria.objects.create(
            restaurante=restaurante, nombre="Principales"
        )
        plato = Plato.objects.create(
            categoria=categoria, nombre="Ropa Vieja", precio=15.50, disponible=True
        )
        assert plato.nombre == "Ropa Vieja"
        assert plato.precio == 15.50
        assert str(plato) == "Ropa Vieja"
