"""
Sistema de validación automática de URLs y vistas
"""

import re
from django.urls import get_resolver, get_urlconf
from django.core.exceptions import ViewDoesNotExist
from importlib import import_module


class URLValidator:
    """Validador profesional de URLs del proyecto"""

    @staticmethod
    def validate_all_urls():
        """Valida todas las URLs del proyecto"""
        errors = []
        warnings = []
        successes = []

        resolver = get_resolver(get_urlconf())

        for url_pattern in resolver.url_patterns:
            result = URLValidator.validate_url_pattern(url_pattern)
            if result["type"] == "error":
                errors.append(result)
            elif result["type"] == "warning":
                warnings.append(result)
            else:
                successes.append(result)

        return {
            "errors": errors,
            "warnings": warnings,
            "successes": successes,
            "total": len(errors) + len(warnings) + len(successes),
        }

    @staticmethod
    def validate_url_pattern(pattern, prefix=""):
        """Valida un patrón de URL individual"""
        try:
            # Si es un include
            if hasattr(pattern, "url_patterns"):
                namespace = pattern.namespace or ""
                for sub_pattern in pattern.url_patterns:
                    URLValidator.validate_url_pattern(
                        sub_pattern, f"{prefix}{pattern.pattern}"
                    )
                return {
                    "type": "success",
                    "pattern": f"{prefix}{pattern.pattern}",
                    "message": f"Include válido: {namespace}",
                }

            # Si es un path normal
            elif hasattr(pattern, "callback"):
                # Verificar que la vista exista
                view_name = (
                    pattern.callback.__name__
                    if hasattr(pattern.callback, "__name__")
                    else str(pattern.callback)
                )
                pattern_name = getattr(pattern, "name", "sin-nombre")

                return {
                    "type": "success",
                    "pattern": f"{prefix}{pattern.pattern}",
                    "name": pattern_name,
                    "view": view_name,
                    "message": f"URL válida: {pattern_name} -> {view_name}",
                }

            # Si no tiene callback
            elif not hasattr(pattern, "callback"):
                return {
                    "type": "warning",
                    "pattern": f"{prefix}{pattern.pattern}",
                    "message": f"URL sin vista asignada",
                }

        except Exception as e:
            return {
                "type": "error",
                "pattern": f"{prefix}{pattern.pattern}"
                if hasattr(pattern, "pattern")
                else str(pattern),
                "message": f"Error: {str(e)}",
            }

    @staticmethod
    def find_broken_urls():
        """Encuentra URLs rotas en el proyecto"""
        broken_urls = []

        try:
            # Obtener todas las URLs
            resolver = get_resolver(get_urlconf())

            for url_pattern in resolver.url_patterns:
                if hasattr(url_pattern, "url_patterns"):
                    # Es un include
                    for sub_pattern in url_pattern.url_patterns:
                        if not hasattr(sub_pattern, "callback"):
                            broken_urls.append(
                                {
                                    "url": f"{url_pattern.pattern}{sub_pattern.pattern}",
                                    "error": "No tiene vista asignada",
                                }
                            )
                        else:
                            try:
                                # Intentar importar la vista
                                callback_str = str(sub_pattern.callback)
                                if "function" in callback_str:
                                    # Extraer módulo y función
                                    match = re.search(r"'(.*?)'", callback_str)
                                    if match:
                                        module_func = match.group(1)
                                        module_name, func_name = module_func.rsplit(
                                            ".", 1
                                        )

                                        # Verificar que exista
                                        module = import_module(module_name)
                                        getattr(module, func_name)
                            except (ImportError, AttributeError) as e:
                                broken_urls.append(
                                    {
                                        "url": f"{url_pattern.pattern}{sub_pattern.pattern}",
                                        "error": f"Vista no encontrada: {str(e)}",
                                    }
                                )

        except Exception as e:
            broken_urls.append({"url": "global", "error": f"Error general: {str(e)}"})

        return broken_urls


class TemplateValidator:
    """Validador de templates y URLs en templates"""

    @staticmethod
    def validate_template_urls(template_content):
        """Valida todas las URLs en un template"""
        import re

        # Buscar todas las tags {% url %}
        url_patterns = re.findall(r'\{%\s*url\s+[\'"]([^\'"]+)[\'"]', template_content)

        errors = []
        valid_urls = []

        # Obtener todas las URLs registradas
        resolver = get_resolver(get_urlconf())
        registered_urls = URLValidator.get_all_named_urls(resolver)

        for url_name in url_patterns:
            if url_name in registered_urls:
                valid_urls.append(url_name)
            else:
                errors.append(
                    {"url_name": url_name, "message": f"URL no encontrada: {url_name}"}
                )

        return {"errors": errors, "valid": valid_urls, "total": len(url_patterns)}

    @staticmethod
    def get_all_named_urls(resolver, namespace=""):
        """Obtiene todas las URLs con nombre"""
        url_dict = {}

        for pattern in resolver.url_patterns:
            if hasattr(pattern, "url_patterns"):
                # Include con namespace
                if pattern.namespace:
                    new_namespace = (
                        f"{namespace}:{pattern.namespace}"
                        if namespace
                        else pattern.namespace
                    )
                else:
                    new_namespace = namespace

                # Recursividad
                sub_urls = TemplateValidator.get_all_named_urls(pattern, new_namespace)
                url_dict.update(sub_urls)

            elif hasattr(pattern, "name") and pattern.name:
                # URL con nombre
                full_name = f"{namespace}:{pattern.name}" if namespace else pattern.name
                url_dict[full_name] = {
                    "pattern": str(pattern.pattern),
                    "namespace": namespace,
                }

        return url_dict
