"""
Formularios del módulo de Agenda.
"""

from django import forms
from .models import HorarioTrabajo, DiaBloqueado


class HorarioTrabajoForm(forms.ModelForm):
    class Meta:
        model = HorarioTrabajo
        fields = ['dia_semana', 'hora_inicio', 'hora_fin']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin':    forms.TimeInput(attrs={'type': 'time'}),
        }


class DiaBloqueadoForm(forms.ModelForm):
    class Meta:
        model = DiaBloqueado
        fields = ['fecha', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
