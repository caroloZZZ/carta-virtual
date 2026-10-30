#!/usr/bin/env python
import os
import sys
import django
import subprocess
import socket


def check_django():
    print("\n🔍 Verificando Django...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
    django.setup()
    print("✅ Django OK")


def check_models():
    from restaurantes.models import Restaurante
    from menu.models import Categoria, Plato
    from pedidos.models import Pedido

    print("\n📦 Modelos:")
    rest_count = Restaurante.objects.count()
    print(f"   Restaurantes: {rest_count}")
    if rest_count == 0:
        print("   ⚠️  No hay restaurantes. Crea uno.")
    else:
        for r in Restaurante.objects.all():
            print(f"      - {r.nombre} (activo: {r.activo})")
    print(f"   Categorías: {Categoria.objects.count()}")
    print(f"   Platos: {Plato.objects.count()}")
    print(f"   Pedidos: {Pedido.objects.count()}")


def check_urls():
    from django.urls import reverse
    from restaurantes.models import Restaurante

    print("\n🔗 URLs:")
    try:
        rest = Restaurante.objects.filter(activo=True).first()
        if rest:
            url_carta = reverse("clientes:carta_publica", args=[rest.qr_uuid])
            print(f"   Carta pública: {url_carta} ✅")
        else:
            print("   ⚠️  No hay restaurante activo para generar URL.")
        print(f"   Dashboard: {reverse('dashboard:dashboard')} ✅")
        print(f"   Admin: {reverse('admin:index')} ✅")
    except Exception as e:
        print(f"❌ Error en URLs: {e}")


def check_services():
    print("\n🌐 Servicios:")
    for service in ["carta_virtual", "nginx"]:
        result = subprocess.run(
            ["systemctl", "is-active", service], capture_output=True, text=True
        )
        status = result.stdout.strip()
        print(f"   {service}: {'✅ activo' if status == 'active' else '❌ inactivo'}")


def check_env():
    print("\n📝 Variables de entorno:")
    for var in ["DEBUG", "ALLOWED_HOSTS", "BASE_URL", "DB_NAME"]:
        value = os.environ.get(var, "No definida")
        print(f"   {var}: {value}")


def check_port():
    print("\n🔌 Puerto 80:")
    result = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True)
    if ":80" in result.stdout:
        print("   ✅ Puerto 80 escuchando")
    else:
        print("   ❌ Puerto 80 no escucha")


def check_public_ip():
    print("\n🌍 IP Pública:")
    try:
        ip = subprocess.check_output(["curl", "-s", "ifconfig.me"]).decode().strip()
        print(f"   IP actual: {ip}")
        # Probar si el dominio resuelve a esa IP
        domain = "tubaarestaurant.duckdns.org"
        resolved = socket.gethostbyname(domain)
        if resolved == ip:
            print(f"   ✅ {domain} resuelve a la IP correcta")
        else:
            print(f"   ❌ {domain} resuelve a {resolved} (debería ser {ip})")
    except:
        print("   ❌ No se pudo obtener IP pública")


def main():
    print("=" * 50)
    print("   VERIFICACIÓN CARTA VIRTUAL CUBA")
    print("=" * 50)
    check_django()
    check_models()
    check_urls()
    check_services()
    check_env()
    check_port()
    check_public_ip()
    print("\n" + "=" * 50)
    print("   VERIFICACIÓN COMPLETADA")
    print("=" * 50)


if __name__ == "__main__":
    main()
