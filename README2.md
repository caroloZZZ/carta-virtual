# 🍽️ Carta Virtual Cuba - Sistema de Pedidos por QR

Sistema web profesional desarrollado en Django para digitalizar el menú y la gestión de pedidos de bares y restaurantes. Diseñado para funcionar en modo **Local (Offline)** mediante un Hotspot WiFi, permitiendo a los clientes ordenar escaneando un código QR sin necesidad de internet.

## 🚀 Características Principales
- **Menú Digital Interactivo:** Carta responsiva (estilo UberEats) con buscador en vivo, filtros por categoría, modal con ingredientes y preparación.
- **Carrito de Compras Inteligente:** Cálculo de totales, selección de mesa (bloqueada por QR), y validación de sesión.
- **Modo Offline (Local):** Todos los assets (CSS, JS, fuentes, imágenes) están alojados localmente. Cero dependencia de CDNs externos.
- **Dashboard Administrativo:** Gestión de pedidos en tiempo real, control de estados (Pendiente, Confirmando, Listo), gestión de menú y estadísticas.
- **Seguridad Invisible:** Límite de tiempo de sesión (90 min), límite de pedidos por sesión, validación estricta de mesas y cantidades.
- **Auto-Actualización:** El menú del cliente detecta cambios en tiempo real y sugiere recargar.

## 🛠️ Stack Tecnológico
- **Backend:** Python 3.12 / Django 6.0.2
- **Base de Datos:** SQLite (Desarrollo/Local) / PostgreSQL (Preparado para Producción)
- **Frontend:** HTML5, CSS3, Vanilla JS, Bootstrap 5 (Local)
- **Generación QR:** Librería `qrcode` de Python (Backend)

## 🔄 Flujo de Funcionamiento
1. **Admin:** Inicia el servidor local (`python manage.py runserver 0.0.0.0:8000`).
2. **Cliente:** Se conecta a la red WiFi (Hotspot) del local y escanea el QR de su mesa.
3. **Sistema:** Valida la IP local, asigna la mesa a la sesión (90 min) y muestra la carta.
4. **Pedido:** El cliente agrega platos, indica cuántas personas son y confirma.
5. **Cocina:** El pedido entra al Dashboard en estado "Pendiente". El camarero lo confirma y el cliente ve el progreso en su pantalla en tiempo real.

## 🛡️ Seguridad y Reglas de Negocio
- **Anti-Bromas:** Máximo 4 pedidos por sesión. Mesa no modificable vía URL. Límite de 20 platos por ítem.
- **Aislamiento:** Los clientes de internet (futuro modo online) podrán ver el menú, pero **no podrán hacer pedidos** (bloqueo por IP).
- **CSRF y ORM:** Protección contra inyección SQL y ataques de falsificación de peticiones.

## 🔧 Instalación y Despliegue Local
1. Clonar el repositorio.
2. Crear y activar el entorno virtual: `python -m venv venv && source venv/bin/activate`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Configurar `.env` (ver `.env.example`).
5. Aplicar migraciones: `python manage.py migrate`.
6. Crear superusuario: `python manage.py createsuperuser`.
7. Crear Hotspot (Linux): `sudo nmcli device wifi hotspot ifname wlan0 ssid "BarWifi" password "12345678"`.
8. Iniciar servidor: `python manage.py runserver 0.0.0.0:8000`.
