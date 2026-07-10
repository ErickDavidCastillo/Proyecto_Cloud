# 🚀 Guía de Despliegue a Producción (Azure App Service)

## Configuración Completada

Este proyecto está totalmente configurado para desplegarse en Azure App Service con las siguientes características:

### ✅ Paquetes Instalados

- **gunicorn** (22.0.0): Servidor WSGI para producción
- **whitenoise** (6.7.0): Servir archivos estáticos eficientemente
- **django-decouple** (2.1): Gestión segura de variables de entorno
- **psycopg2-binary** (2.9.9): Driver PostgreSQL

Todos los paquetes están listados en `requirements.txt`.

### ✅ Configuración de Django (`config/settings.py`)

#### 1. **SECRET_KEY y DEBUG desde Variables de Entorno**
```python
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```
- En producción, `DEBUG` debe ser `False`
- `SECRET_KEY` se lee desde la variable de entorno (nunca en texto plano)

#### 2. **ALLOWED_HOSTS Dinámico**
```python
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv()
)
```
- Separar múltiples hosts con comas (sin espacios)
- Ejemplo para Azure: `localhost,127.0.0.1,mi-app.azurewebsites.net`

#### 3. **Bases de Datos Dinámicas**
```python
if DB_HOSTNAME:
    # PostgreSQL en producción
    DATABASES = { 'default': { 'ENGINE': 'django.db.backends.postgresql', ... } }
else:
    # SQLite en desarrollo local
    DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', ... } }
```

#### 4. **WhiteNoise Configurado**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Aquí
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 5. **Seguridad en Producción**
- HTTPS forzado (`SECURE_SSL_REDIRECT`)
- HSTS habilitado
- Cookies seguras (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)

---

## 📋 Pasos para Desplegar en Azure

### 1. Crear Archivo `.env` en Azure App Service

En Azure Portal → App Service → Configuration → Application settings, agregar:

```env
SECRET_KEY=<clave-segura-generada>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,mi-app.azurewebsites.net
DB_HOSTNAME=mi-servidor.postgres.database.azure.com
DB_NAME=dental_db
DB_USER=usuario_postgresql
DB_PASSWORD=<contraseña-super-segura>
DB_PORT=5432
```

**Generar SECRET_KEY seguro:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Configurar Startup Command en Azure App Service

En Azure Portal → App Service → Configuration → Startup command:

```bash
bash startup.sh
```

O directamente:
```bash
sh ./startup.sh
```

### 3. Desplegar Código

```bash
# Clonar repositorio
git clone https://github.com/ErickDavidCastillo/Proyecto_Cloud.git
cd Proyecto_Cloud

# Push a Azure (si usas Azure DevOps o Git directo)
git push azure main
```

### 4. Verificar Logs

```bash
# En Azure Portal → App Service → Log stream
# O desde terminal local:
az webapp log tail --name <nombre-app> --resource-group <resource-group>
```

---

## 🗄️ Base de Datos PostgreSQL en Azure

### Obtener Credenciales
1. Ir a Azure Portal → Azure Database for PostgreSQL
2. En "Connection strings", copiar la información
3. Configurar en variables de entorno de App Service

### Estructura Esperada
- **db_hostname**: `servidor.postgres.database.azure.com`
- **db_user**: `usuario@servidor` (incluye nombre del servidor)
- **db_password**: Contraseña de 12+ caracteres
- **db_name**: Nombre de la base de datos

---

## 📦 Estructura de Archivos en Producción

```
proyecto_final/
├── manage.py
├── config/
│   ├── settings.py          ← Configuración (lee desde env)
│   ├── wsgi.py              ← Punto de entrada para Gunicorn
│   └── urls.py
├── apps/
│   ├── usuarios/
│   ├── citas/
│   ├── agenda/
│   └── fichas/
├── templates/
├── static/                   ← Archivos estáticos
├── staticfiles/              ← WhiteNoise los comprime aquí
├── media/                    ← Comprobantes de pago (subidos)
├── startup.sh               ← Script de arranque (Azure App Service)
├── requirements.txt         ← Dependencias Python
├── .env                     ← Variables de entorno (NO HACER COMMIT)
├── .env.example             ← Template de .env (HACER COMMIT)
└── README.md
```

---

## 🔧 Comandos Útiles

### Desarrollo Local
```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Recolectar estáticos
python manage.py collectstatic --noinput

# Servidor de desarrollo
python manage.py runserver
```

### Producción Local (Simular Azure)
```bash
.\venv\Scripts\Activate.ps1

# Ejecutar el startup.sh (si usas WSL o bash)
bash startup.sh

# O ejecutar Gunicorn directamente
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## ⚠️ Checklist Pre-Despliegue

- [ ] `DEBUG=False` en el archivo `.env` de Azure
- [ ] `SECRET_KEY` es único y seguro (no reutilizar)
- [ ] `ALLOWED_HOSTS` incluye el dominio de Azure
- [ ] PostgreSQL está configurado y accesible desde App Service
- [ ] Variables de entorno están en Azure App Service (no en `.env`)
- [ ] `requirements.txt` está actualizado (`pip freeze > requirements.txt`)
- [ ] Migraciones están aplicadas (`python manage.py migrate`)
- [ ] Estáticos están compilados (`python manage.py collectstatic`)
- [ ] Tests pasan correctamente (`python manage.py test`)
- [ ] No hay archivos `.env` o secretos en el repositorio
- [ ] `.gitignore` excluye `.env`, `__pycache__`, `venv/`, `*.pyc`

---

## 🐛 Troubleshooting

### Error: "Missing staticfiles manifest"
```bash
python manage.py collectstatic --noinput --clear
```

### Error: "connection refused" a PostgreSQL
- Verificar que PostgreSQL está en la misma región
- Permitir acceso desde Azure App Service en el firewall de BD
- Verificar credenciales en variables de entorno

### Error: "No such table: usuarios_usuario"
```bash
python manage.py migrate --noinput
```

### Error: "ALLOWED_HOSTS configuration error"
- Verificar que `ALLOWED_HOSTS` incluye el dominio de Azure
- Reiniciar la aplicación en Azure Portal

---

## 📚 Referencias

- [Django en Azure App Service](https://learn.microsoft.com/es-es/azure/app-service/quickstart-python)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [django-decouple](https://github.com/Henriquel1702/django-decouple)

---

**Última actualización**: 2026-07-10
