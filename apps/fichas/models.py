"""
Modelos del módulo de Ficha Clínica.

HistorialClinico almacena el registro médico de cada visita del paciente,
incluyendo diagnóstico y tratamiento realizado por el odontólogo.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class HistorialClinico(models.Model):
    """
    Ficha clínica que el odontólogo completa tras atender al paciente.
    Representa el historial médico-dental del paciente en el consultorio.
    """

    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='historial_clinico',
        limit_choices_to={'rol': 'PACIENTE'},
        verbose_name=_('Paciente'),
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='fichas_atendidas',
        limit_choices_to={'rol': 'ODONTOLOGO'},
        verbose_name=_('Odontólogo tratante'),
    )
    fecha = models.DateField(
        verbose_name=_('Fecha de la consulta'),
        db_index=True,
    )
    diagnostico = models.TextField(
        verbose_name=_('Diagnóstico'),
        help_text=_('Descripción clínica del estado dental del paciente.'),
    )
    tratamiento_realizado = models.TextField(
        verbose_name=_('Tratamiento realizado'),
        help_text=_('Descripción del procedimiento ejecutado en la consulta.'),
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name=_('Observaciones adicionales'),
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de registro'),
    )

    class Meta:
        verbose_name = _('Historial clínico')
        verbose_name_plural = _('Historiales clínicos')
        ordering = ['-fecha']

    def __str__(self) -> str:
        return (
            f'Ficha #{self.pk} | {self.paciente.get_full_name()} | '
            f'{self.fecha.strftime("%d/%m/%Y")} | Dr. {self.doctor.get_full_name()}'
        )
