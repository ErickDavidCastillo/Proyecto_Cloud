"""
Vistas del módulo de Fichas Clínicas.
"""

from django.contrib.auth import get_user_model
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from apps.usuarios.views import SoloOdontologoMixin, SoloPacienteMixin
from .models import HistorialClinico
from .forms import HistorialClinicoForm

User = get_user_model()


class MiFichaView(SoloPacienteMixin, ListView):
    """El paciente ve su propio historial clínico (solo lectura)."""

    template_name = 'fichas/mi_ficha.html'
    context_object_name = 'fichas'

    def get_queryset(self):
        return HistorialClinico.objects.filter(
            paciente=self.request.user
        ).select_related('doctor').order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mi Historial Clínico'
        return context


class CrearFichaView(SoloOdontologoMixin, CreateView):
    """El odontólogo crea una nueva ficha clínica para un paciente."""

    model = HistorialClinico
    form_class = HistorialClinicoForm
    template_name = 'fichas/crear_ficha.html'
    success_url = reverse_lazy('fichas:mis_fichas_doctor')

    def get_initial(self):
        initial = super().get_initial()
        paciente_pk = self.request.GET.get('paciente')
        if paciente_pk:
            try:
                paciente = User.objects.get(pk=paciente_pk, rol='PACIENTE')
                initial['paciente'] = paciente
            except User.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        ficha = form.save(commit=False)
        ficha.doctor = self.request.user

        # Vincular la ficha con la cita (si se proporcionó) y marcar la cita como atendida
        cita_pk = self.request.GET.get('cita') or self.request.POST.get('cita')
        if cita_pk:
            try:
                from apps.citas.models import Cita
                cita = Cita.objects.get(pk=cita_pk)
                ficha.cita = cita
                # marcar atendida solo si el doctor coincide (seguridad básica)
                if cita.doctor == self.request.user:
                    cita.atendida = True
                    cita.save()
            except Exception:
                # ignorar si no existe o error de validación
                pass

        ficha.save()
        messages.success(
            self.request,
            f'Ficha clínica creada para {ficha.paciente.get_full_name()}.'
        )

        # Si la ficha fue creada desde una cita, redirigir de vuelta al cronograma
        if cita_pk:
            return redirect('agenda:mi_cronograma')

        return super().form_valid(form)


class FichasPacienteView(SoloOdontologoMixin, ListView):
    """El odontólogo ve las fichas de un paciente específico."""

    template_name = 'fichas/fichas_paciente.html'
    context_object_name = 'fichas'

    def get_queryset(self):
        return HistorialClinico.objects.filter(
            doctor=self.request.user
        ).select_related('paciente').order_by('-fecha')
