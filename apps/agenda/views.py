"""
Vistas del módulo de Agenda y Disponibilidad.
"""

from datetime import date

from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render

from apps.citas.models import Cita
from apps.usuarios.views import SoloOdontologoMixin
from .models import HorarioTrabajo, DiaBloqueado
from .forms import HorarioTrabajoForm, DiaBloqueadoForm


class MiCronogramaView(SoloOdontologoMixin, ListView):
    """Vista principal del odontólogo: muestra su horario semanal."""

    template_name = 'agenda/mi_cronograma.html'
    context_object_name = 'horarios'

    def get_queryset(self):
        return HorarioTrabajo.objects.filter(
            doctor=self.request.user
        ).order_by('dia_semana', 'hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mi Cronograma Semanal'
        context['dias_bloqueados'] = DiaBloqueado.objects.filter(
            doctor=self.request.user
        ).order_by('fecha')
        context['citas_asignadas'] = Cita.objects.filter(
            doctor=self.request.user,
            fecha__gte=date.today(),
            estado__in=[
                Cita.Estado.PENDIENTE_PAGO,
                Cita.Estado.EN_REVISION,
                Cita.Estado.CONFIRMADA,
            ],
        ).select_related('paciente').order_by('fecha', 'hora')
        context['form_horario'] = HorarioTrabajoForm()
        context['form_bloqueo'] = DiaBloqueadoForm()
        return context


class CrearHorarioView(SoloOdontologoMixin, CreateView):
    """Añade un nuevo bloque de horario al odontólogo."""

    model = HorarioTrabajo
    form_class = HorarioTrabajoForm
    success_url = reverse_lazy('agenda:mi_cronograma')
    template_name = 'agenda/mi_cronograma.html'  # Apunta al cronograma en caso de error

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        messages.success(self.request, 'Horario añadido correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Si falla, vuelve a cargar el cronograma mostrando el error en el campo."""
        context = {
            'titulo': 'Mi Cronograma Semanal',
            'horarios': HorarioTrabajo.objects.filter(doctor=self.request.user).order_by('dia_semana', 'hora_inicio'),
            'dias_bloqueados': DiaBloqueado.objects.filter(doctor=self.request.user).order_by('fecha'),
            'citas_asignadas': Cita.objects.filter(
                doctor=self.request.user,
                fecha__gte=date.today(),
                estado__in=[Cita.Estado.PENDIENTE_PAGO, Cita.Estado.EN_REVISION, Cita.Estado.CONFIRMADA]
            ).select_related('paciente').order_by('fecha', 'hora'),
            'form_horario': form,  # Este contiene los errores detectados
            'form_bloqueo': DiaBloqueadoForm(),  # Formulario de bloqueo limpio
        }
        return self.render_to_response(context)


class EliminarHorarioView(SoloOdontologoMixin, DeleteView):
    """Elimina un bloque de horario del odontólogo."""

    model = HorarioTrabajo
    success_url = reverse_lazy('agenda:mi_cronograma')

    def get_queryset(self):
        return super().get_queryset().filter(doctor=self.request.user)


class BloquearDiaView(SoloOdontologoMixin, CreateView):
    """Bloquea un día específico en la agenda del odontólogo."""

    model = DiaBloqueado
    form_class = DiaBloqueadoForm
    success_url = reverse_lazy('agenda:mi_cronograma')
    template_name = 'agenda/mi_cronograma.html'  # Apunta al cronograma en caso de error

    def form_valid(self, form):
        fecha = form.cleaned_data['fecha']
        if DiaBloqueado.objects.filter(
            doctor=self.request.user,
            fecha=fecha
        ).exists():
            form.add_error('fecha', 'Ya has bloqueado este día en tu agenda.')
            return self.form_invalid(form)
        
        form.instance.doctor = self.request.user
        messages.success(self.request, 'Día bloqueado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Si falla, vuelve a cargar el cronograma incrustando el error en el formulario."""
        context = {
            'titulo': 'Mi Cronograma Semanal',
            'horarios': HorarioTrabajo.objects.filter(doctor=self.request.user).order_by('dia_semana', 'hora_inicio'),
            'dias_bloqueados': DiaBloqueado.objects.filter(doctor=self.request.user).order_by('fecha'),
            'citas_asignadas': Cita.objects.filter(
                doctor=self.request.user,
                fecha__gte=date.today(),
                estado__in=[Cita.Estado.PENDIENTE_PAGO, Cita.Estado.EN_REVISION, Cita.Estado.CONFIRMADA]
            ).select_related('paciente').order_by('fecha', 'hora'),
            'form_horario': HorarioTrabajoForm(),  # Formulario de horario limpio
            'form_bloqueo': form,  # Este contiene el error "Ya has bloqueado este día..."
        }
        return self.render_to_response(context)