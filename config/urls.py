"""
URLs principales del proyecto - Consultorio Dental.
Enruta hacia los módulos de autenticación, citas, agenda, fichas y dashboard.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Módulo de autenticación (login, logout, registro)
    path('auth/', include('apps.usuarios.urls', namespace='usuarios')),

    # Módulo de citas y turnos
    path('citas/', include('apps.citas.urls', namespace='citas')),

    # Módulo de agenda y disponibilidad
    path('agenda/', include('apps.agenda.urls', namespace='agenda')),

    # Módulo de fichas clínicas
    path('fichas/', include('apps.fichas.urls', namespace='fichas')),

    # Dashboard del administrador
    path('dashboard/', include('apps.usuarios.dashboard_urls', namespace='dashboard')),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)