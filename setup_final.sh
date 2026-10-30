#!/bin/bash

# ==================================================
# SCRIPT DE CONFIGURACIÓN FINAL - CARTA VIRTUAL CUBA
# ==================================================

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   CONFIGURANDO CARTA VIRTUAL CUBA     ${NC}"
echo -e "${GREEN}========================================${NC}"

# ==================================================
# VARIABLES (CÁMBIALAS SÓLO SI SON DIFERENTES)
# ==================================================
PROJECT_DIR="/home/srwizard/admin-bar-rest/admin-restaurant"
VENV_DIR="/home/srwizard/admin-bar-rest/venv"
DOMAIN="tubaarestaurant.duckdns.org"
LOCAL_IP="192.168.44.162"
DB_NAME="carta_virtual_prod"
DB_USER="carta_user"
DB_PASS="contraseña_segura"   # Cámbiala si quieres
# ==================================================

# Verificar que estamos en el directorio correcto
cd $PROJECT_DIR || { echo -e "${RED}❌ No se puede acceder a $PROJECT_DIR${NC}"; exit 1; }

# ==================================================
# 1. Crear/actualizar archivo .env
# ==================================================
echo -e "\n${YELLOW}📝 Configurando archivo .env...${NC}"
cat > .env <<EOF
DEBUG=False
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=localhost,127.0.0.1,$LOCAL_IP,$DOMAIN
BASE_URL=http://$DOMAIN
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_HOST=localhost
DB_PORT=5432
EOF
echo -e "${GREEN}✅ .env actualizado${NC}"

# ==================================================
# 2. Crear servicio de Gunicorn
# ==================================================
echo -e "\n${YELLOW}🛠️  Configurando servicio Gunicorn...${NC}"
sudo bash -c "cat > /etc/systemd/system/carta_virtual.service <<EOF
[Unit]
Description=Carta Virtual Gunicorn Service
After=network.target

[Service]
User=srwizard
Group=srwizard
WorkingDirectory=$PROJECT_DIR
Environment=\"PATH=$VENV_DIR/bin\"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable carta_virtual
sudo systemctl restart carta_virtual
echo -e "${GREEN}✅ Servicio Gunicorn configurado y reiniciado${NC}"

# ==================================================
# 3. Configurar Nginx
# ==================================================
echo -e "\n${YELLOW}🌐 Configurando Nginx...${NC}"
sudo bash -c "cat > /etc/nginx/sites-available/carta_virtual <<EOF
server {
    listen 80;
    server_name $DOMAIN $LOCAL_IP localhost;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF"

# Habilitar sitio si no está
if [ ! -f /etc/nginx/sites-enabled/carta_virtual ]; then
    sudo ln -s /etc/nginx/sites-available/carta_virtual /etc/nginx/sites-enabled/
fi

sudo nginx -t && sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx configurado${NC}"

# ==================================================
# 4. Recolectar estáticos y comprimir
# ==================================================
echo -e "\n${YELLOW}📦 Recolectando estáticos y comprimiendo...${NC}"
source $VENV_DIR/bin/activate
python manage.py collectstatic --noinput --settings=config.settings.production
python manage.py compress --settings=config.settings.production
echo -e "${GREEN}✅ Estáticos listos${NC}"

# ==================================================
# 5. Verificar servicios
# ==================================================
echo -e "\n${YELLOW}🔍 Verificando servicios...${NC}"
sleep 3
if systemctl is-active --quiet carta_virtual; then
    echo -e "${GREEN}✅ Gunicorn activo${NC}"
else
    echo -e "${RED}❌ Gunicorn no está activo. Revisa: sudo journalctl -u carta_virtual -f${NC}"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx activo${NC}"
else
    echo -e "${RED}❌ Nginx no está activo. Revisa: sudo systemctl status nginx${NC}"
fi

# ==================================================
# 6. Preguntar si crear restaurante de prueba
# ==================================================
echo -e "\n${YELLOW}🍽️  ¿Quieres crear un restaurante de prueba ahora? (s/n)${NC}"
read -r crear
if [[ "$crear" == "s" || "$crear" == "S" ]]; then
    echo -e "${YELLOW}Ejecutando script para crear restaurante...${NC}"
    python manage.py shell <<EOF
from restaurantes.models import Restaurante
from django.contrib.auth.models import User

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@local.com', 'admin123')
    print("✅ Superusuario 'admin' creado (contraseña: admin123)")

# Crear restaurante si no hay ninguno
if Restaurante.objects.count() == 0:
    admin = User.objects.get(username='admin')
    Restaurante.objects.create(
        usuario=admin,
        nombre='Mi Restaurante de Prueba',
        descripcion='Restaurante creado automáticamente',
        direccion='Dirección de prueba',
        telefono='12345678',
        email='restaurante@local.com',
        activo=True
    )
    print("✅ Restaurante de prueba creado")
else:
    print("ℹ️ Ya existen restaurantes")
EOF
    echo -e "${GREEN}✅ Proceso completado.${NC}"
fi

# ==================================================
# 7. Mostrar resumen
# ==================================================
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}   CONFIGURACIÓN FINALIZADA            ${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "🔹 Acceso local: http://$LOCAL_IP/"
echo -e "🔹 Acceso internet: http://$DOMAIN/"
echo -e "🔹 Panel admin: http://$LOCAL_IP/admin/ (usuario: admin, pass: admin123 si lo creaste)"
echo -e "🔹 Dashboard restaurante: http://$LOCAL_IP/dashboard/"
echo -e "\n${YELLOW}⚠️  Recuerda:${NC}"
echo -e "  - Si quieres acceso desde internet, configura el reenvío de puertos en tu router (puerto 80 -> $LOCAL_IP)."
echo -e "  - Para mantener DuckDNS actualizado, ejecuta: crontab -e y añade:"
echo -e "    */5 * * * * /home/srwizard/duckdns/duck.sh >/dev/null 2>&1"
echo -e "${GREEN}========================================${NC}"
