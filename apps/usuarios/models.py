"""
Modelo de Usuario personalizado con sistema de roles (RBAC).
Hereda de AbstractUser para mantener compatibilidad total con
el sistema de autenticación nativo de Django.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Usuario(AbstractUser):
    """
    Usuario personalizado del sistema de Consultorio Dental.

    Extiende AbstractUser añadiendo el campo 'rol' que determina
    los permisos y la interfaz que verá cada usuario tras el login.
    """

    class Rol(models.TextChoices):
        PACIENTE      = 'PACIENTE',      _('Paciente')
        ODONTOLOGO    = 'ODONTOLOGO',    _('Odontólogo')
        ADMINISTRADOR = 'ADMINISTRADOR', _('Administrador')

    rol = models.CharField(
        max_length=15,
        choices=Rol.choices,
        default=Rol.PACIENTE,
        verbose_name=_('Rol del usuario'),
        help_text=_('Determina los permisos y el panel de control asignado.'),
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono de contacto'),
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de nacimiento'),
    )

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['last_name', 'first_name']

    def __str__(self) -> str:
        return f'{self.get_full_name()} ({self.get_rol_display()})'

    # ------------------------------------------------------------------
    # Helpers de rol (evitan comparaciones de string en toda la app)
    # ------------------------------------------------------------------
    @property
    def es_paciente(self) -> bool:
        return self.rol == self.Rol.PACIENTE

    @property
    def es_odontologo(self) -> bool:
        return self.rol == self.Rol.ODONTOLOGO

    @property
    def es_administrador(self) -> bool:
        return self.rol == self.Rol.ADMINISTRADOR

    def get_dashboard_url(self) -> str:
        """Retorna la URL de inicio según el rol del usuario."""
        if self.es_paciente:
            return '/citas/mis-citas/'
        if self.es_odontologo:
            return '/agenda/mi-cronograma/'
        return '/dashboard/admin/'
