from django.urls import reverse, resolve
from core.views import home, login_view, logout_view


class TestCoreUrls:
    def test_home_url(self):
        url = reverse("home")
        assert resolve(url).func == home

    def test_login_url(self):
        url = reverse("login")
        assert resolve(url).func == login_view

    def test_logout_url(self):
        url = reverse("logout")
        assert resolve(url).func == logout_view
