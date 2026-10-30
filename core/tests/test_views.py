import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestCoreViews:
    def test_home(self, client):
        url = reverse("home")
        response = client.get(url)
        assert response.status_code == 200
        assert "core/home.html" in [t.name for t in response.templates]

    def test_login_get(self, client):
        url = reverse("login")
        response = client.get(url)
        assert response.status_code == 200
        assert "auth/login.html" in [t.name for t in response.templates]

    def test_login_post_valido(self, client):
        User.objects.create_user(username="testlogin", password="12345")
        response = client.post(
            reverse("login"), {"username": "testlogin", "password": "12345"}
        )
        assert response.status_code == 302
        assert response.url == reverse("dashboard:dashboard")
