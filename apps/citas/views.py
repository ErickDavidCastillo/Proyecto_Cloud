"""
Vistas del módulo de Citas y Turnos.

Implementa el flujo completo del paciente:
  1. Ver lista de mis citas.
  2. Reservar nueva cita (crea en PENDIENTE_PAGO).
  3. Subir comprobante de pago (pasa a EN_REVISION).

Y el flujo del Administrador:
  4. Ver citas EN_REVISION.
  5. Aprobar o Rechazar citas (CONFIRMADA / CANCELADA).
"""

from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError

from apps.usuarios.views import SoloPacienteMixin, SoloAdministradorMixin
from .models import Cita
from .forms import ReservaCitaForm, SubirComprobanteForm


# =============================================================================
# VISTAS DEL PACIENTE
# =============================================================================

class MisCitasView(SoloPacienteMixin, ListView):
    """Lista de citas del paciente autenticado."""

    template_name = 'citas/mis_citas.html'
    context_object_name = 'citas'

    def get_queryset(self):
        return Cita.objects.filter(
            paciente=self.request.user
        ).select_related('doctor').order_by('-fecha', '-hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mis Citas'
        return context


class ReservarCitaView(SoloPacienteMixin, CreateView):
    """El paciente reserva una nueva cita (estado inicial: PENDIENTE_PAGO)."""

    model = Cita
    form_class = ReservaCitaForm
    template_name = 'citas/reservar_cita.html'
    success_url = reverse_lazy('citas:mis_citas')

    def post(self, request, *args, **kwargs):
        """Asigna el paciente actual a la instancia del formulario ANTES de su validación."""
        self.object = None
        form = self.get_form()
        form.instance.paciente = request.user  # 🔥 AQUÍ CORREGIMOS EL ERROR
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        cita = form.save(commit=False)
        cita.paciente = self.request.user
        cita.estado = Cita.Estado.PENDIENTE_PAGO
        try:
            cita.full_clean()
            cita.save()
            messages.success(
                self.request,
                '✅ Cita reservada correctamente. '
                'Por favor, suba su comprobante de pago para continuar.'
            )
            return redirect('citas:subir_comprobante', pk=cita.pk)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class SubirComprobanteView(SoloPacienteMixin, UpdateView):
    """El paciente sube el comprobante de transferencia y pasa a EN_REVISION."""

    model = Cita
    form_class = SubirComprobanteForm
    template_name = 'citas/subir_comprobante.html'
    success_url = reverse_lazy('citas:mis_citas')

    def get_queryset(self):
        # El paciente solo puede editar SUS citas
        return Cita.objects.filter(
            paciente=self.request.user,
            estado=Cita.Estado.PENDIENTE_PAGO,
        )

    def form_valid(self, form):
        cita = form.save(commit=False)
        try:
            cita.enviar_a_revision()
            messages.success(
                self.request,
                '📤 Comprobante enviado. Su cita está en revisión. '
                'El administrador la confirmará pronto.'
            )
        except ValidationError as e:
            messages.error(self.request, str(e))
        return redirect(self.success_url)


# =============================================================================
# VISTAS DEL ADMINISTRADOR
# =============================================================================

class CitasPendientesReviewView(SoloAdministradorMixin, ListView):
    """Lista de citas EN_REVISION esperando aprobación del administrador."""

    template_name = 'citas/admin_revision.html'
    context_object_name = 'citas'

    def get_queryset(self):
        return Cita.objects.filter(
            estado=Cita.Estado.EN_REVISION
        ).select_related('paciente', 'doctor').order_by('fecha', 'hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Citas en Revisión'
        return context


class AprobarCitaView(SoloAdministradorMixin, DetailView):
    """
    Vista de aprobación/rechazo de citas por el Administrador.
    GET:  Muestra el detalle de la cita y el comprobante.
    POST: Confirma o Cancela la cita según el parámetro 'accion'.

    SEGURIDAD: SoloAdministradorMixin retorna HTTP 403 Forbidden
    si un PACIENTE u ODONTOLOGO intenta acceder.
    """

    model = Cita
    template_name = 'citas/admin_aprobar.html'
    context_object_name = 'cita'

    def get_queryset(self):
        return Cita.objects.filter(
            estado=Cita.Estado.EN_REVISION
        ).select_related('paciente', 'doctor')

    def post(self, request, *args, **kwargs):
        cita   = self.get_object()
        accion = request.POST.get('accion', '')
        notas  = request.POST.get('notas', '')

        if accion == 'CONFIRMAR':
            try:
                cita.confirmar(notas=notas)
                messages.success(
                    request,
                    f'✅ Cita #{cita.pk} de {cita.paciente.get_full_name()} CONFIRMADA.'
                )
            except ValidationError as e:
                messages.error(request, str(e))

        elif accion == 'CANCELAR':
            try:
                cita.cancelar(notas=notas)
                messages.warning(
                    request,
                    f'❌ Cita #{cita.pk} de {cita.paciente.get_full_name()} CANCELADA.'
                )
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Acción no válida.')

        return redirect('citas:citas_revision')