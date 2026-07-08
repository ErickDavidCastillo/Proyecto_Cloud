"""
Formularios del módulo de Citas.
"""

from django import forms
from .models import Cita


class ReservaCitaForm(forms.ModelForm):
    """
    Formulario para que el paciente reserve una cita.
    El paciente solo selecciona doctor, fecha y hora.
    El estado se asigna automáticamente en la vista.
    """

    class Meta:
        model  = Cita
        fields = ['doctor', 'fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora':  forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'doctor': 'Odontólogo',
            'fecha':  'Fecha de la cita',
            'hora':   'Hora de la cita',
        }


class SubirComprobanteForm(forms.ModelForm):
    """
    Formulario para subir el comprobante de pago.
    Solo acepta el archivo; el estado cambia en la vista.
    """

    class Meta:
        model  = Cita
        fields = ['comprobante_pago', 'fecha_transaccion']
        widgets = {
            'fecha_transaccion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'comprobante_pago':  'Archivo del comprobante (JPG/PNG/PDF)',
            'fecha_transaccion': 'Fecha y hora de la transferencia',
        }
