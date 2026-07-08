"""
Formularios del módulo de usuarios.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroPacienteForm(UserCreationForm):
    """
    Formulario de registro para nuevos pacientes.
    No expone el campo 'rol' para evitar escalada de privilegios.
    """

    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'telefono', 'fecha_nacimiento',
            'password1', 'password2',
        ]
        labels = {
            'username':        'Nombre de usuario',
            'first_name':      'Nombre(s)',
            'last_name':       'Apellido(s)',
            'telefono':        'Teléfono',
            'fecha_nacimiento': 'Fecha de nacimiento',
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.rol = Usuario.Rol.PACIENTE  # Forzar rol de paciente
        if commit:
            usuario.save()
        return usuario
