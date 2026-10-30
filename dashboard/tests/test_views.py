import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from restaurantes.models import Restaurante


@pytest.mark.django_db
class TestDashboardViews:
    @pytest.fixture
    def user_restaurante(self):
        user = User.objects.create_user(username="dashuser", password="123")
        Restaurante.objects.create(
            usuario=user,
            nombre="Dash Resto",
            slug="dash-resto",
            descripcion="...",
            direccion="...",
            telefono="12345678",
            email="dash@test.com",
        )
        return user

    def test_dashboard_sin_login(self, client):
        url = reverse("dashboard:dashboard")
        response = client.get(url)
        assert response.status_code == 302  # redirige a login
        assert "/login/" in response.url

    def test_dashboard_con_login(self, client, user_restaurante):
        client.force_login(user_restaurante)
        url = reverse("dashboard:dashboard")
        response = client.get(url)
        assert response.status_code == 200
        assert "dashboard/index.html" in [t.name for t in response.templates]
