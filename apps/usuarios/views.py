"""
Vistas del módulo de autenticación y control de acceso.

Implementa:
- LoginView con redirección dinámica por rol (RBAC).
- Registro de nuevos pacientes.
- Logout seguro.
- Mixins de protección de rutas por rol (403 Forbidden).
"""

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Usuario
from .forms import RegistroPacienteForm


# =============================================================================
# VISTA DE LOGIN UNIFICADO CON REDIRECCIÓN POR ROL
# =============================================================================

class LoginRolView(LoginView):
    """
    Vista de login que sobrescribe get_success_url() para redirigir
    al panel correcto según el rol del usuario autenticado.

    Flujo:
        PACIENTE       -> /citas/mis-citas/
        ODONTOLOGO     -> /agenda/mi-cronograma/
        ADMINISTRADOR  -> /dashboard/admin/
    """

    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True  # Si ya está logueado, redirige directo

    def get_success_url(self) -> str:
        """Determina la URL de destino según el rol del usuario."""
        return self.request.user.get_dashboard_url()

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Credenciales incorrectas. Por favor, verifique su usuario y contraseña.'
        )
        return super().form_invalid(form)


# =============================================================================
# REGISTRO DE NUEVOS PACIENTES
# =============================================================================

class RegistroPacienteView(CreateView):
    """
    Permite el auto-registro de usuarios con rol PACIENTE.
    El rol se asigna automáticamente para evitar escalada de privilegios.
    """

    model = Usuario
    form_class = RegistroPacienteForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        # Forzar rol PACIENTE sin importar lo que venga del formulario
        usuario = form.save(commit=False)
        usuario.rol = Usuario.Rol.PACIENTE
        usuario.save()
        messages.success(
            self.request,
            f'¡Registro exitoso! Bienvenido/a {usuario.get_full_name()}. '
            'Por favor, inicie sesión.'
        )
        return redirect(self.success_url)


# =============================================================================
# LOGOUT SEGURO
# =============================================================================

def logout_view(request):
    """Cierra la sesión del usuario y redirige al login."""
    logout(request)
    messages.info(request, 'Ha cerrado sesión correctamente.')
    return redirect('usuarios:login')


# =============================================================================
# DASHBOARD DEL ADMINISTRADOR
# =============================================================================

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Panel de control exclusivo para Administradores.
    Devuelve HTTP 403 Forbidden si un Paciente u Odontólogo intenta acceder.
    """

    template_name = 'dashboard/admin.html'
    login_url = reverse_lazy('usuarios:login')

    def test_func(self) -> bool:
        """Solo los ADMINISTRADOR pasan el test."""
        return self.request.user.es_administrador

    def handle_no_permission(self):
        """Retorna 403 en lugar de redirigir al login cuando ya está autenticado."""
        if self.request.user.is_authenticated:
            return HttpResponseForbidden(
                '<h1>403 Prohibido</h1>'
                '<p>No tiene permisos para acceder a esta sección.</p>'
            )
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        from apps.citas.models import Cita
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Panel de Administración'
        context['citas_pendientes'] = Cita.objects.filter(
            estado=Cita.Estado.EN_REVISION
        ).select_related('paciente', 'doctor').count()
        context['citas_confirmadas_hoy'] = Cita.objects.filter(
            estado=Cita.Estado.CONFIRMADA
        ).select_related('paciente', 'doctor').count()
        return context


# =============================================================================
# MIXIN REUTILIZABLE: SOLO ADMINISTRADORES
# =============================================================================

class SoloAdministradorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin reutilizable para proteger vistas que solo pueden
    ser accedidas por usuarios con rol ADMINISTRADOR.
    Retorna HTTP 403 Forbidden ante accesos no autorizados.
    """

    login_url = reverse_lazy('usuarios:login')

    def test_func(self) -> bool:
        return self.request.user.es_administrador

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden(
                '<h1>403 Prohibido</h1>'
                '<p>Esta acción está reservada para Administradores.</p>'
            )
        return super().handle_no_permission()


# =============================================================================
# MIXIN REUTILIZABLE: SOLO ODONTÓLOGOS
# =============================================================================

class SoloOdontologoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin reutilizable para proteger vistas exclusivas de Odontólogos.
    """

    login_url = reverse_lazy('usuarios:login')

    def test_func(self) -> bool:
        return self.request.user.es_odontologo

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden(
                '<h1>403 Prohibido</h1>'
                '<p>Esta sección es exclusiva para Odontólogos.</p>'
            )
        return super().handle_no_permission()


# =============================================================================
# MIXIN REUTILIZABLE: SOLO PACIENTES
# =============================================================================

class SoloPacienteMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin reutilizable para proteger vistas exclusivas de Pacientes.
    """

    login_url = reverse_lazy('usuarios:login')

    def test_func(self) -> bool:
        return self.request.user.es_paciente

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden(
                '<h1>403 Prohibido</h1>'
                '<p>Esta sección es exclusiva para Pacientes.</p>'
            )
        return super().handle_no_permission()
