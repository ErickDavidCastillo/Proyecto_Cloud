"""
Modelo de Cita con Máquina de Estados y manejo de comprobante de pago.

Estados del ciclo de vida de una cita:
┌─────────────────┐     sube comprobante     ┌────────────┐
│ PENDIENTE_PAGO  │ ─────────────────────── ▶ │ EN_REVISION │
└─────────────────┘                            └──────┬─────┘
                                                      │
                               ┌──────────────────────┤
                               ▼                      ▼
                         ┌──────────┐          ┌──────────┐
                         │CONFIRMADA│          │ CANCELADA│
                         └──────────┘          └──────────┘

Reglas de negocio implementadas mediante constraints de base de datos:
1. Un doctor no puede tener dos citas CONFIRMADAS en el mismo slot de tiempo.
2. Un paciente no puede tener dos citas en el mismo slot de tiempo.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Cita(models.Model):
    """
    Modelo principal del sistema. Representa el turno/cita de un paciente
    con un odontólogo. Implementa una máquina de estados mediante TextChoices.
    """

    # -------------------------------------------------------------------------
    # MÁQUINA DE ESTADOS
    # -------------------------------------------------------------------------
    class Estado(models.TextChoices):
        PENDIENTE_PAGO = 'PENDIENTE_PAGO', _('Pendiente de pago')
        EN_REVISION    = 'EN_REVISION',    _('En revisión')
        CONFIRMADA     = 'CONFIRMADA',     _('Confirmada')
        CANCELADA      = 'CANCELADA',      _('Cancelada')

    # -------------------------------------------------------------------------
    # RELACIONES
    # -------------------------------------------------------------------------
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='citas_como_paciente',
        limit_choices_to={'rol': 'PACIENTE'},
        verbose_name=_('Paciente'),
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='citas_como_doctor',
        limit_choices_to={'rol': 'ODONTOLOGO'},
        verbose_name=_('Odontólogo'),
    )

    # -------------------------------------------------------------------------
    # DATOS TEMPORALES
    # -------------------------------------------------------------------------
    fecha = models.DateField(verbose_name=_('Fecha de la cita'))
    hora  = models.TimeField(verbose_name=_('Hora de inicio'))

    # -------------------------------------------------------------------------
    # ESTADO (Máquina de estados)
    # -------------------------------------------------------------------------
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE_PAGO,
        verbose_name=_('Estado'),
        db_index=True,
    )

    # -------------------------------------------------------------------------
    # COMPROBANTE DE PAGO (FileField — almacenamiento local temporal)
    # -------------------------------------------------------------------------
    comprobante_pago = models.FileField(
        upload_to='comprobantes/',
        null=True,
        blank=True,
        verbose_name=_('Comprobante de pago'),
        help_text=_(
            'Captura/PDF de la transferencia bancaria. '
            'Máximo 5MB. Formatos: PDF, JPG, PNG.'
        ),
    )

    # -------------------------------------------------------------------------
    # AUDITORÍA
    # -------------------------------------------------------------------------
    fecha_creacion    = models.DateTimeField(auto_now_add=True, verbose_name=_('Creada el'))
    fecha_actualizacion = models.DateTimeField(auto_now=True,  verbose_name=_('Actualizada el'))
    fecha_transaccion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de transacción'),
        help_text=_('Fecha en que el paciente realizó la transferencia.'),
    )

    # Notas del administrador al aprobar/rechazar
    notas_admin = models.TextField(
        blank=True,
        verbose_name=_('Notas del administrador'),
    )

    # -------------------------------------------------------------------------
    # META
    # -------------------------------------------------------------------------
    class Meta:
        verbose_name = _('Cita')
        verbose_name_plural = _('Citas')
        ordering = ['fecha', 'hora']
        # Constraint de BD: Evita doble reserva del doctor en el mismo slot CONFIRMADO
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'fecha', 'hora'],
                condition=models.Q(estado='CONFIRMADA'),
                name='unique_cita_confirmada_doctor',
            ),
            # Constraint: Evita doble reserva del paciente en el mismo slot
            models.UniqueConstraint(
                fields=['paciente', 'fecha', 'hora'],
                condition=~models.Q(estado='CANCELADA'),
                name='unique_cita_activa_paciente',
            ),
        ]

    # -------------------------------------------------------------------------
    # VALIDACIONES A NIVEL DE MODELO
    # -------------------------------------------------------------------------
    def clean(self):
        super().clean()
        self._validar_no_duplicado_doctor()
        self._validar_no_duplicado_paciente()
        self._validar_comprobante_al_cambiar_estado()

    def _validar_no_duplicado_doctor(self):
        """
        Regla 1: El doctor NO puede tener dos citas CONFIRMADAS
        en el mismo slot (fecha + hora).
        """
        if self.estado == self.Estado.CONFIRMADA:
            existe = Cita.objects.filter(
                doctor=self.doctor,
                fecha=self.fecha,
                hora=self.hora,
                estado=self.Estado.CONFIRMADA,
            ).exclude(pk=self.pk).exists()

            if existe:
                raise ValidationError({
                    'hora': _(
                        'El Dr. %(doctor)s ya tiene una cita CONFIRMADA '
                        'el %(fecha)s a las %(hora)s.'
                    ) % {
                        'doctor': self.doctor.get_full_name(),
                        'fecha':  self.fecha.strftime('%d/%m/%Y'),
                        'hora':   self.hora.strftime('%H:%M'),
                    }
                })

    def _validar_no_duplicado_paciente(self):
        """
        Regla 2: Un paciente NO puede tener dos citas activas
        en el mismo slot horario (con distintos doctores).
        """
        estados_activos = [
            self.Estado.PENDIENTE_PAGO,
            self.Estado.EN_REVISION,
            self.Estado.CONFIRMADA,
        ]
        if self.estado in estados_activos:
            existe = Cita.objects.filter(
                paciente=self.paciente,
                fecha=self.fecha,
                hora=self.hora,
                estado__in=estados_activos,
            ).exclude(pk=self.pk).exists()

            if existe:
                raise ValidationError({
                    'hora': _(
                        'El paciente %(paciente)s ya tiene una cita activa '
                        'el %(fecha)s a las %(hora)s.'
                    ) % {
                        'paciente': self.paciente.get_full_name(),
                        'fecha':    self.fecha.strftime('%d/%m/%Y'),
                        'hora':     self.hora.strftime('%H:%M'),
                    }
                })

    def _validar_comprobante_al_cambiar_estado(self):
        """
        Regla 3: No se puede pasar a EN_REVISION sin haber subido el comprobante.
        """
        if self.estado == self.Estado.EN_REVISION and not self.comprobante_pago:
            raise ValidationError({
                'comprobante_pago': _(
                    'Debe adjuntar el comprobante de pago para enviar a revisión.'
                )
            })

    # -------------------------------------------------------------------------
    # TRANSICIONES DE ESTADO (API del modelo)
    # -------------------------------------------------------------------------
    def enviar_a_revision(self):
        """Paciente sube comprobante y solicita revisión."""
        if self.estado != self.Estado.PENDIENTE_PAGO:
            raise ValidationError(_('Solo citas PENDIENTE_PAGO pueden enviarse a revisión.'))
        self.estado = self.Estado.EN_REVISION
        self.full_clean()
        self.save()

    def confirmar(self, notas: str = ''):
        """Administrador aprueba la cita tras verificar el pago."""
        if self.estado != self.Estado.EN_REVISION:
            raise ValidationError(_('Solo citas EN_REVISION pueden ser confirmadas.'))
        self.estado = self.Estado.CONFIRMADA
        self.notas_admin = notas
        self.full_clean()
        self.save()

    def cancelar(self, notas: str = ''):
        """Administrador rechaza la cita o el paciente la cancela."""
        if self.estado == self.Estado.CANCELADA:
            raise ValidationError(_('La cita ya está cancelada.'))
        self.estado = self.Estado.CANCELADA
        self.notas_admin = notas
        self.save()

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        return (
            f'Cita #{self.pk} | {self.paciente.get_full_name()} '
            f'con Dr. {self.doctor.get_full_name()} | '
            f'{self.fecha.strftime("%d/%m/%Y")} {self.hora.strftime("%H:%M")} '
            f'[{self.get_estado_display()}]'
        )
