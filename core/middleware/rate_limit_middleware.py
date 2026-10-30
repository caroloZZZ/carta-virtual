"""
Middleware para rate limiting básico
"""

import time
from django.utils.deprecation import MiddlewareMixin


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware básico para rate limiting"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Placeholder - puedes implementar rate limiting más adelante
        return self.get_response(request)
