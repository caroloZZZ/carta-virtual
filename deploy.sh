#!/bin/bash

# Script de deploy para Carta Virtual Cuba

set -e  # Detener en caso de error

echo "🚀 Iniciando deploy de Carta Virtual Cuba..."

# Variables
PROJECT_DIR="/var/www/carta_virtual_cuba"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/tuusuario/carta_virtual_cuba.git"
BRANCH="main"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de logging
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# 1. Actualizar código
echo "📥 Actualizando código desde GitHub..."
cd $PROJECT_DIR
git pull origin $BRANCH || log_error "Error al actualizar código"

# 2. Activar entorno virtual
echo "🐍 Activando entorno virtual..."
source $VENV_DIR/bin/activate || log_error "Error activando entorno virtual"

# 3. Instalar/actualizar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt || log_error "Error instalando dependencias"

# 4. Aplicar migraciones
echo "🔄 Aplicando migraciones..."
python manage.py migrate --settings=config.settings_prod || log_error "Error en migraciones"

# 5. Colectar archivos estáticos
echo "📁 Colectando archivos estáticos..."
python manage.py collectstatic --noinput --settings=config.settings_prod || log_error "Error colectando estáticos"

# 6. Verificar permisos
echo "🔒 Verificando permisos..."
chmod -R 755 $PROJECT_DIR
chown -R www-data:www-data $PROJECT_DIR/media
chown -R www-data:www-data $PROJECT_DIR/staticfiles

# 7. Reiniciar servicios
echo "🔄 Reiniciando servicios..."
sudo systemctl restart gunicorn || log_error "Error reiniciando Gunicorn"
sudo systemctl restart nginx || log_error "Error reiniciando Nginx"

# 8. Verificar estado
echo "🔍 Verificando estado del servicio..."
sleep 2
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

log_success "🚀 Deploy completado exitosamente!"
echo ""
echo "📊 Accesos:"
echo "   🌐 URL pública: https://tudominio.com"
echo "   🔧 Panel admin: https://tudominio.com/admin"
echo "   📱 Carta QR: https://tudominio.com/cliente/<uuid>/"
echo ""
echo "📈 Monitoreo:"
echo "   📊 Logs: tail -f $PROJECT_DIR/logs/django.log"
echo "   📈 Métricas: sudo systemctl status gunicorn"
