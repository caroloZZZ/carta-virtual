from django.contrib import admin
from .models import ConfiguracionSistema, Auditoria


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ["clave", "tipo", "valor"]
    search_fields = ["clave", "descripcion"]
    list_filter = ["tipo"]


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ["usuario", "accion", "modelo", "fecha"]
    list_filter = ["accion", "modelo", "fecha"]
    search_fields = ["usuario__username", "accion", "modelo"]
    readonly_fields = [
        "usuario",
        "accion",
        "modelo",
        "objeto_id",
        "fecha",
        "detalles",
        "ip",
    ]
    date_hierarchy = "fecha"
