from django.contrib import admin
from .models import Pedido, ItemPedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ["precio_unitario", "subtotal"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        "codigo",
        "restaurante",
        "nombre_cliente",
        "mesa",
        "estado",
        "total",
        "fecha_creacion",
    ]
    list_filter = ["estado", "metodo_pago", "pagado", "restaurante", "fecha_creacion"]
    search_fields = [
        "codigo",
        "nombre_cliente",
        "telefono_cliente",
        "restaurante__nombre",
    ]
    readonly_fields = [
        "codigo",
        "total",
        "fecha_creacion",
        "fecha_confirmacion",
        "fecha_listo",
        "fecha_entregado",
    ]
    inlines = [ItemPedidoInline]

    fieldsets = (
        (
            "Información del Pedido",
            {"fields": ("codigo", "restaurante", "estado", "total")},
        ),
        (
            "Información del Cliente",
            {"fields": ("nombre_cliente", "telefono_cliente", "mesa", "notas")},
        ),
        ("Pago", {"fields": ("metodo_pago", "pagado")}),
        (
            "Fechas",
            {
                "fields": (
                    "fecha_creacion",
                    "fecha_confirmacion",
                    "fecha_listo",
                    "fecha_entregado",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "marcar_como_confirmado",
        "marcar_como_preparando",
        "marcar_como_listo",
        "marcar_como_entregado",
    ]

    def marcar_como_confirmado(self, request, queryset):
        from django.utils import timezone

        queryset.update(estado="confirmado", fecha_confirmacion=timezone.now())
        self.message_user(request, "Pedidos marcados como confirmados")

    def marcar_como_preparando(self, request, queryset):
        queryset.update(estado="preparando")
        self.message_user(request, "Pedidos marcados como preparando")

    def marcar_como_listo(self, request, queryset):
        from django.utils import timezone

        queryset.update(estado="listo", fecha_listo=timezone.now())
        self.message_user(request, "Pedidos marcados como listos")

    def marcar_como_entregado(self, request, queryset):
        from django.utils import timezone

        queryset.update(estado="entregado", fecha_entregado=timezone.now())
        self.message_user(request, "Pedidos marcados como entregados")

    marcar_como_confirmado.short_description = "Marcar seleccionados como CONFIRMADO"
    marcar_como_preparando.short_description = "Marcar seleccionados como PREPARANDO"
    marcar_como_listo.short_description = "Marcar seleccionados como LISTO"
    marcar_como_entregado.short_description = "Marcar seleccionados como ENTREGADO"
