from django.contrib import admin
from .models import HistorialClinico


@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'paciente', 'doctor', 'fecha', 'fecha_registro')
    list_filter   = ('doctor', 'fecha')
    search_fields = ('paciente__first_name', 'paciente__last_name', 'diagnostico')
    readonly_fields = ('fecha_registro',)
