"""
Middleware de seguridad básico
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class SecurityMiddleware(MiddlewareMixin):
    """Middleware para headers de seguridad"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Headers de seguridad básicos
        response["X-Frame-Options"] = "DENY"
        response["X-Content-Type-Options"] = "nosniff"
        response["X-XSS-Protection"] = "1; mode=block"

        return response
