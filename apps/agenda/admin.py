from django.contrib import admin
from .models import HorarioTrabajo, DiaBloqueado


@admin.register(HorarioTrabajo)
class HorarioTrabajoAdmin(admin.ModelAdmin):
    list_display  = ('doctor', 'get_dia_semana_display', 'hora_inicio', 'hora_fin')
    list_filter   = ('doctor', 'dia_semana')
    search_fields = ('doctor__first_name', 'doctor__last_name')


@admin.register(DiaBloqueado)
class DiaBloqueadoAdmin(admin.ModelAdmin):
    list_display  = ('doctor', 'fecha', 'motivo')
    list_filter   = ('doctor',)
    search_fields = ('doctor__first_name', 'motivo')
