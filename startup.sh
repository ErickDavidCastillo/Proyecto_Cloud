#!/bin/bash
# =============================================================================
# startup.sh — Script de arranque para Azure App Service (Linux, Python 3.12)
# =============================================================================
# Este script se configura en la sección "Startup Command" del App Service.
# Ejecuta las migraciones del ORM de forma no-interactiva ANTES de levantar
# el servidor Gunicorn, garantizando que la base de datos esté actualizada
# con cada nuevo despliegue.
#
# IMPORTANTE: Gunicorn debe escuchar en el puerto 8000 (requerido por Azure).
# =============================================================================

set -e  # Detener ejecución ante cualquier error no controlado

echo "============================================================"
echo " Consultorio Dental — Arranque del servidor de producción"
echo " Fecha: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "============================================================"

# -----------------------------------------------------------------------------
# 1. APLICAR MIGRACIONES DEL ORM (no-interactivo)
# -----------------------------------------------------------------------------
echo ""
echo "=== [1/3] Aplicando Migraciones del ORM ==="
python manage.py migrate --noinput
echo "    ✅ Migraciones aplicadas correctamente."

# -----------------------------------------------------------------------------
# 2. RECOLECTAR ARCHIVOS ESTÁTICOS (WhiteNoise los sirve desde STATIC_ROOT)
# -----------------------------------------------------------------------------
echo ""
echo "=== [2/3] Recolectando Archivos Estáticos ==="
python manage.py collectstatic --noinput --clear
echo "    ✅ Archivos estáticos recolectados."

# -----------------------------------------------------------------------------
# 3. INICIAR SERVIDOR GUNICORN
# -----------------------------------------------------------------------------
echo ""
echo "=== [3/3] Iniciando Gunicorn en puerto 8000 ==="
echo "    Workers: $(( 2 * $(nproc) + 1 ))"

gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers $(( 2 * $(nproc) + 1 )) \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info \
    --preload
