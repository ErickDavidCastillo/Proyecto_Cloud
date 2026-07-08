"""
Configuración del panel de administración de Django para el módulo usuarios.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado que muestra el rol en la lista y formularios."""

    list_display  = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active')
    list_filter   = ('rol', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('last_name', 'first_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Información del Consultorio', {
            'fields': ('rol', 'telefono', 'fecha_nacimiento'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Consultorio', {
            'fields': ('rol', 'telefono', 'fecha_nacimiento'),
        }),
    )
