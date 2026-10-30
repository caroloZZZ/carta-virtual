from django.contrib import admin
from .models import Categoria, Plato


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "restaurante", "orden", "activa"]
    list_filter = ["activa", "restaurante"]
    search_fields = ["nombre", "restaurante__nombre"]
    list_editable = ["orden", "activa"]


@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "categoria",
        "precio",
        "disponible",
        "destacado",
        "veces_pedido",
    ]
    list_filter = [
        "disponible",
        "destacado",
        "es_vegetariano",
        "es_picante",
        "categoria__restaurante",
    ]
    search_fields = ["nombre", "descripcion", "categoria__nombre"]
    list_editable = ["precio", "disponible", "destacado"]
    readonly_fields = ["veces_pedido"]

    fieldsets = (
        (
            "Información Básica",
            {"fields": ("categoria", "nombre", "descripcion", "precio", "imagen")},
        ),
        (
            "Características",
            {
                "fields": (
                    "disponible",
                    "destacado",
                    "es_vegetariano",
                    "es_picante",
                    "contiene_gluten",
                )
            },
        ),
        (
            "Información Nutricional",
            {"fields": ("calorias", "tiempo_preparacion"), "classes": ("collapse",)},
        ),
        ("Estadísticas", {"fields": ("veces_pedido",), "classes": ("collapse",)}),
    )
