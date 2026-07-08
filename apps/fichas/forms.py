"""Formularios del módulo de Fichas Clínicas."""

from django import forms
from .models import HistorialClinico


class HistorialClinicoForm(forms.ModelForm):
    class Meta:
        model = HistorialClinico
        fields = ['paciente', 'fecha', 'diagnostico', 'tratamiento_realizado', 'observaciones']
        widgets = {
            'fecha':               forms.DateInput(attrs={'type': 'date'}),
            'diagnostico':         forms.Textarea(attrs={'rows': 4}),
            'tratamiento_realizado': forms.Textarea(attrs={'rows': 4}),
            'observaciones':       forms.Textarea(attrs={'rows': 3}),
        }
