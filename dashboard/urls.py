from django.urls import path
from . import views
from .views import lista_categorias

app_name = "dashboard"

urlpatterns = [
    # Dashboard principal
    path("", views.dashboard, name="dashboard"),
    # Mi Restaurante (PERFIL)
    path("mi-restaurante/", views.mi_restaurante, name="mi_restaurante"),
    # Gestión de menú - CATEGORÍAS
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categorias/crear/", views.crear_categoria, name="crear_categoria"),
    path(
        "categorias/editar/<int:categoria_id>/",
        views.editar_categoria,
        name="editar_categoria",
    ),
    path(
        "categorias/eliminar/<int:categoria_id>/",
        views.eliminar_categoria,
        name="eliminar_categoria",
    ),
    # Gestión de menú - PLATOS
    path("platos/", views.lista_platos, name="platos"),
    path("platos/crear/", views.crear_plato, name="crear_plato"),
    path("platos/editar/<int:plato_id>/", views.editar_plato, name="editar_plato"),
    path(
        "platos/eliminar/<int:plato_id>/", views.eliminar_plato, name="eliminar_plato"
    ),
    # Gestión de pedidos
    path("pedidos/", views.lista_pedidos, name="lista_pedidos"),
    path("pedidos/<int:pedido_id>/", views.detalle_pedido, name="detalle_pedido"),
    path(
        "pedidos/<int:pedido_id>/cambiar-estado/",
        views.cambiar_estado_pedido,
        name="cambiar_estado_pedido",
    ),
    # Configuración
    path(
        "configuracion/",
        views.configuracion_restaurante,
        name="configuracion_restaurante",
    ),
    # QR
    path("qr/", views.ver_qr, name="ver_qr"),
    path("qr/generar/", views.generar_qr, name="generar_qr"),
    path("qr/regenerar/", views.regenerar_qr, name="regenerar_qr"),
    # Estadísticas
    path("estadisticas/", views.estadisticas, name="estadisticas"),
    # RESERVAS
    path("reservas/", views.lista_reservas, name="lista_reservas"),
    path("reservas/crear/", views.crear_reserva, name="crear_reserva"),
    path("reservas/guardar/", views.guardar_reserva, name="guardar_reserva"),
    path("reservas/<int:reserva_id>/", views.detalle_reserva, name="detalle_reserva"),
    path(
        "reservas/<int:reserva_id>/editar/", views.editar_reserva, name="editar_reserva"
    ),
    path(
        "reservas/<int:reserva_id>/eliminar/",
        views.eliminar_reserva,
        name="eliminar_reserva",
    ),
    path(
        "reservas/<int:reserva_id>/cambiar-estado/",
        views.cambiar_estado_reserva,
        name="cambiar_estado_reserva",
    ),
    # Clientes
    path("clientes/", views.lista_clientes, name="clientes"),  # ¡OJO: name='clientes'!
    path("clientes/<int:cliente_id>/", views.detalle_cliente, name="detalle_cliente"),
    # Notificaciones
    path("notificaciones/", views.lista_notificaciones, name="notificaciones"),
    path(
        "notificaciones/marcar-leidas/",
        views.marcar_notificaciones_leidas,
        name="marcar_notificaciones_leidas",
    ),
    # Reportes
    path("reportes/exportar-pedidos/", views.exportar_pedidos, name="exportar_pedidos"),
    path(
        "reportes/exportar-clientes/", views.exportar_clientes, name="exportar_clientes"
    ),
    path(
        "reportes/exportar-estadisticas/",
        views.exportar_estadisticas,
        name="exportar_estadisticas",
    ),
]
