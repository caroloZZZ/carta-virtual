from django.contrib import admin
from .models import Restaurante


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "usuario",
        "tipo",
        "activo",
        "verificado",
        "fecha_registro",
    ]
    list_filter = ["tipo", "activo", "verificado", "fecha_registro"]
    search_fields = ["nombre", "usuario__username", "email", "telefono"]
    readonly_fields = ["qr_uuid", "qr_code", "fecha_registro", "ultima_actualizacion"]
    fieldsets = (
        (
            "Información Básica",
            {"fields": ("usuario", "nombre", "slug", "tipo", "descripcion")},
        ),
        ("Contacto", {"fields": ("direccion", "telefono", "email")}),
        ("Imágenes", {"fields": ("logo", "portada")}),
        (
            "Configuración",
            {
                "fields": (
                    "activo",
                    "verificado",
                    "mostrar_precios",
                    "acepta_pedidos",
                    "acepta_reservas",
                )
            },
        ),
        ("QR", {"fields": ("qr_uuid", "qr_code")}),
        ("Estadísticas", {"fields": ("visitas_qr", "total_pedidos")}),
        (
            "Fechas",
            {
                "fields": ("fecha_registro", "ultima_actualizacion"),
                "classes": ("collapse",),
            },
        ),
    )
