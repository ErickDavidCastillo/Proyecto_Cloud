# 🦷 DentalCare Pro — Sistema de Gestión de Citas y Turnos

Sistema web para **Consultorio Dental** desarrollado con **Django 4.2 + Python 3.12**, listo para despliegue en **Azure App Service (Linux, plan F1 gratuito)** con pipeline CI/CD en GitHub Actions.

---

## 📁 Estructura del Proyecto

```
proyecto_final/
├── .github/
│   └── workflows/
│       └── azure-deploy.yml       # Pipeline CI/CD
├── apps/
│   ├── usuarios/                  # Modelo AbstractUser + RBAC + Login
│   │   ├── models.py              # Usuario con campo 'rol'
│   │   ├── views.py               # LoginRolView + Mixins 403
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── dashboard_urls.py
│   ├── agenda/                    # HorarioTrabajo + DiaBloqueado
│   ├── citas/                     # Cita (Máquina de estados) + tests.py
│   └── fichas/                    # HistorialClinico
├── config/
│   ├── settings.py                # Configuración segura (python-decouple)
│   ├── urls.py
│   └── wsgi.py
├── static/
│   ├── css/main.css               # Sistema de diseño premium
│   └── js/main.js
├── templates/
│   ├── base.html
│   ├── usuarios/ (login, registro)
│   ├── citas/ (mis_citas, reservar, comprobante, admin)
│   └── dashboard/ (admin.html)
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore
├── manage.py
├── requirements.txt
└── startup.sh                     # Script de arranque para Azure
```

---

## 🚀 Instalación Local

### 1. Clonar e instalar dependencias
```bash
git clone <tu-repositorio>
cd proyecto_final
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus valores reales
```

### 3. Aplicar migraciones y crear superusuario
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

Acceder en: `http://localhost:8000/auth/login/`

---

## 🧪 Ejecutar Tests Unitarios

```bash
python manage.py test apps.citas --verbosity=2
```

### Tests incluidos:
| Test | Descripción |
|------|-------------|
| `test_evitar_duplicidad_cita_dentista` | Bloquea doble cita CONFIRMADA del mismo doctor en el mismo slot |
| `test_evitar_doble_reserva_paciente` | Bloquea doble reserva del mismo paciente en el mismo horario |
| `test_seguridad_roles_aprobacion_pago` | Verifica HTTP 403 para PACIENTE en vista de aprobación |
| `test_redireccion_login_por_rol` | Valida HTTP 302 y URL de redirección por rol |

---

## 🔐 Sistema de Roles (RBAC)

| Rol | URL de inicio | Permisos |
|-----|---------------|----------|
| `PACIENTE` | `/citas/mis-citas/` | Ver/reservar citas, subir comprobante, ver ficha clínica |
| `ODONTOLOGO` | `/agenda/mi-cronograma/` | Gestionar horario, crear fichas clínicas |
| `ADMINISTRADOR` | `/dashboard/admin/` | Aprobar/rechazar citas, gestión completa |

---

## 📊 Máquina de Estados de la Cita

```
PENDIENTE_PAGO  →  EN_REVISION  →  CONFIRMADA
                                →  CANCELADA
```

---

## ☁️ Despliegue en Azure App Service

### Secrets de GitHub necesarios:
| Secret | Descripción |
|--------|-------------|
| `AZURE_CREDENTIALS` | JSON del Service Principal de Azure |
| `AZURE_WEBAPP_NAME` | Nombre del App Service |

### Variables de entorno en Azure Portal:
Configure en **App Service → Configuration → Application settings**:
- `SECRET_KEY`
- `DEBUG` = `False`
- `ALLOWED_HOSTS` = `tu-app.azurewebsites.net`
- `DB_HOSTNAME`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

### Startup Command en Azure Portal:
```
bash startup.sh
```

---

## 📦 Stack Tecnológico

- **Backend**: Python 3.12 + Django 4.2 LTS
- **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Servidor**: Gunicorn 22.0
- **Archivos estáticos**: WhiteNoise 6.7
- **Configuración**: python-decouple 3.8
- **CI/CD**: GitHub Actions
- **Cloud**: Azure App Service F1 (gratuito)
