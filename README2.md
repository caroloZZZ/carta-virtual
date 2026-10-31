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





""estos son los pasas especificos paara usarlo desde tu pc :""
--- INICIO README ---

# 🍽️ Carta Virtual Cuba - Sistema de Pedidos Locales

¡Hola! Bienvenido al proyecto **Carta Virtual Cuba**. Este es un sistema profesional desarrollado en **Django** para digitalizar el menú y la gestión de pedidos de bares y restaurantes. 

El sistema está diseñado principalmente para funcionar en **Modo Local (Offline)**, es decir, el servidor corre en la PC del bar, emite una red WiFi (Hotspot) y los clientes escanean un código QR para ver el menú y ordenar desde sus mesas sin necesidad de internet.

---

## 🛠️ Requisitos Previos
Antes de ejecutar el proyecto, asegúrate de tener instalado en tu PC (Linux/Ubuntu recomendado):
*   **Python 3.10+** (`sudo apt install python3 python3-venv python3-pip`)
*   **Git** (`sudo apt install git`)

# estos comandos en la consola

python3 -m venv venv
source venv/bin/activate

# lueego instalar las dependencias con  
pip install -r requirements.txt
---

## 🚀 Instalación y Ejecución (Paso a Paso)

Sigue estos comandos exactos en tu terminal para tener el sistema funcionando en menos de 5 minutos.

### 1. Clonar el repositorio
```bash
git clone https://github.com/caroloZZZ/carta-virtual.git
cd carta-virtual]

# estas son las variables del entorno tuyo es decir datos de salida y entrada de el internet q usara el proyecto aqui estan los mios pero si necesitas conseguir los tuyos con este comando ves la ip  , hay q ponerla fija en la maquina q se correra el proyecto


ip -4 addr show 


cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=clave-secreta-super-segura-para-desarrollo-local-123456
ALLOWED_HOSTS=localhost,127.0.0.1,10.42.0.1
BASE_URL=http://10.42.0.1:8000
LOCAL_IP=10.42.0.1
DB_NAME=admin_restaurant
DB_USER=admin_restaurant_user
DB_PASSWORD=AdminRest123!
DB_HOST=localhost
DB_PORT=5432
EOF


# hacer las migraciones de los datos 
python manage.py migrate
#crear super usuario admin
python manage.py createsuperuser

# iniciar el serve 
python manage.py runserver 0.0.0.0:8000


