from django.contrib import admin
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        "nombre_cliente",
        "telefono",
        "fecha",
        "hora",
        "personas",
        "estado",
        "restaurante",
    ]
    list_filter = ["estado", "fecha", "restaurante"]
    search_fields = ["nombre_cliente", "telefono", "mesa"]
    date_hierarchy = "fecha"
    ordering = ["-fecha", "hora"]

    fieldsets = (
        ("Datos del Cliente", {"fields": ("nombre_cliente", "telefono", "email")}),
        (
            "Datos de la Reserva",
            {"fields": ("restaurante", "fecha", "hora", "personas", "mesa")},
        ),
        ("Estado y Notas", {"fields": ("estado", "notas")}),
    )
