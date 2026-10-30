import pytest
from django.contrib.auth.models import User
from restaurantes.models import Restaurante
from menu.models import Categoria, Plato
from pedidos.models import Pedido, ItemPedido


@pytest.mark.django_db
class TestPedidosModels:
    @pytest.fixture
    def restaurante(self):
        user = User.objects.create_user(username="pedidosuser", password="123")
        return Restaurante.objects.create(
            usuario=user,
            nombre="Resto Pedidos",
            descripcion="...",
            direccion="...",
            telefono="12345678",
            email="pedidos@test.com",
        )

    @pytest.fixture
    def plato(self, restaurante):
        categoria = Categoria.objects.create(
            restaurante=restaurante, nombre="Categoria Test"
        )
        return Plato.objects.create(
            categoria=categoria, nombre="Plato Test", precio=10.0
        )

    def test_crear_pedido(self, restaurante):
        pedido = Pedido.objects.create(
            restaurante=restaurante,
            nombre_cliente="Cliente Test",
            telefono_cliente="12345678",
            total=0,
        )
        assert pedido.codigo is not None
        assert len(pedido.codigo) == 8
        assert pedido.estado == "pendiente"

    def test_crear_item_pedido(self, restaurante, plato):
        pedido = Pedido.objects.create(
            restaurante=restaurante,
            nombre_cliente="Cliente Test",
            telefono_cliente="12345678",
            total=0,
        )
        item = ItemPedido.objects.create(
            pedido=pedido,
            plato=plato,
            cantidad=2,
            precio_unitario=plato.precio,
            subtotal=plato.precio * 2,
        )
        assert item.subtotal == 20.0
        pedido.refresh_from_db()
        assert float(pedido.total) == 20.0
