from django.urls import path
from . import views

app_name = "clientes"

urlpatterns = [
    path("<uuid:qr_uuid>/", views.carta_publica, name="carta_publica"),
    path(
        "<uuid:qr_uuid>/agregar-carrito/",
        views.agregar_al_carrito,
        name="agregar_al_carrito",
    ),
    path("<uuid:qr_uuid>/carrito/", views.ver_carrito, name="ver_carrito"),
    path(
        "<uuid:qr_uuid>/crear-pedido/", views.crear_pedido_api, name="crear_pedido_api"
    ),
    path(
        "<uuid:qr_uuid>/pedido/<int:pedido_id>/",
        views.seguimiento_pedido,
        name="seguimiento_pedido",
    ),
    path(
        "<uuid:qr_uuid>/pedido/<int:pedido_id>/estado/",
        views.estado_pedido_api,
        name="estado_pedido_api",
    ),
    path("<uuid:qr_uuid>/reservar/", views.reservar_mesa, name="reservar_mesa"),
    path(
        "<uuid:qr_uuid>/reserva/<int:reserva_id>/confirmacion/",
        views.confirmacion_reserva,
        name="confirmacion_reserva",
    ),
    path("r/<slug:slug>/", views.presentacion_restaurante, name="presentacion"),
]
