"""
Modelos del módulo de Agenda y Disponibilidad.

Define los horarios de trabajo de los odontólogos y los días bloqueados
(vacaciones, feriados, ausencias), usados para validar la disponibilidad
antes de confirmar una cita.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class HorarioTrabajo(models.Model):
    """
    Define el horario semanal de trabajo de un odontólogo.
    Cada fila representa un bloque de disponibilidad en un día de la semana.
    """

    class DiaSemana(models.IntegerChoices):
        LUNES     = 0, _('Lunes')
        MARTES    = 1, _('Martes')
        MIERCOLES = 2, _('Miércoles')
        JUEVES    = 3, _('Jueves')
        VIERNES   = 4, _('Viernes')
        SABADO    = 5, _('Sábado')
        DOMINGO   = 6, _('Domingo')

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='horarios_trabajo',
        limit_choices_to={'rol': 'ODONTOLOGO'},
        verbose_name=_('Odontólogo'),
    )
    dia_semana = models.IntegerField(
        choices=DiaSemana.choices,
        verbose_name=_('Día de la semana'),
    )
    hora_inicio = models.TimeField(verbose_name=_('Hora de inicio'))
    hora_fin    = models.TimeField(verbose_name=_('Hora de fin'))

    class Meta:
        verbose_name = _('Horario de trabajo')
        verbose_name_plural = _('Horarios de trabajo')
        unique_together = ('doctor', 'dia_semana', 'hora_inicio')
        ordering = ['dia_semana', 'hora_inicio']

    def clean(self):
        if self.hora_inicio and self.hora_fin:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError(
                    _('La hora de inicio debe ser anterior a la hora de fin.')
                )

    def __str__(self) -> str:
        return (
            f'Dr. {self.doctor.get_full_name()} | '
            f'{self.get_dia_semana_display()} '
            f'{self.hora_inicio.strftime("%H:%M")} - {self.hora_fin.strftime("%H:%M")}'
        )


class DiaBloqueado(models.Model):
    """
    Registra días específicos en que un odontólogo NO está disponible
    (feriados, vacaciones, ausencias justificadas).
    """

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dias_bloqueados',
        limit_choices_to={'rol': 'ODONTOLOGO'},
        verbose_name=_('Odontólogo'),
    )
    fecha  = models.DateField(verbose_name=_('Fecha bloqueada'))
    motivo = models.CharField(
        max_length=255,
        verbose_name=_('Motivo del bloqueo'),
        help_text=_('Ej: Vacaciones, Feriado Nacional, Ausencia médica.'),
    )

    class Meta:
        verbose_name = _('Día bloqueado')
        verbose_name_plural = _('Días bloqueados')
        unique_together = ('doctor', 'fecha')
        ordering = ['fecha']

    def __str__(self) -> str:
        return (
            f'Dr. {self.doctor.get_full_name()} | '
            f'{self.fecha.strftime("%d/%m/%Y")} — {self.motivo}'
        )
