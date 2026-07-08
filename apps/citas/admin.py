from django.contrib import admin
from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display  = ('id', 'paciente', 'doctor', 'fecha', 'hora', 'estado', 'fecha_creacion')
    list_filter   = ('estado', 'doctor', 'fecha')
    search_fields = ('paciente__first_name', 'paciente__last_name', 'doctor__last_name')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha', '-hora')

    fieldsets = (
        ('Información principal', {
            'fields': ('paciente', 'doctor', 'fecha', 'hora', 'estado'),
        }),
        ('Comprobante de pago', {
            'fields': ('comprobante_pago', 'fecha_transaccion'),
        }),
        ('Administración', {
            'fields': ('notas_admin', 'fecha_creacion', 'fecha_actualizacion'),
        }),
    )
