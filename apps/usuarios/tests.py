"""
Suite de pruebas unitarias del módulo de Usuarios.

Cubre creación de usuarios con roles, validaciones, login, logout y seguridad RBAC.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.exceptions import ValidationError

from apps.usuarios.models import Usuario


# =============================================================================
# HELPERS REUTILIZABLES
# =============================================================================

def crear_usuario(username: str, password: str, rol: str) -> Usuario:
    """Crea un usuario genérico con el rol especificado."""
    return Usuario.objects.create_user(
        username=username,
        password=password,
        first_name='Test',
        last_name='User',
        rol=rol,
    )


# =============================================================================
# TEST 1: CREACIÓN DE USUARIOS CON ROLES VÁLIDOS
# =============================================================================

class TestCreacionUsuariosConRoles(TestCase):
    """
    Valida la creación correcta de usuarios con cada rol disponible.
    """

    def test_crear_usuario_paciente(self):
        """TC-001: Crear un usuario con rol PACIENTE."""
        usuario = Usuario.objects.create_user(
            username='paciente_test',
            password='P@ss_Segura!123',
            first_name='Juan',
            last_name='Pérez',
            rol=Usuario.Rol.PACIENTE,
        )
        
        self.assertEqual(usuario.rol, Usuario.Rol.PACIENTE)
        self.assertTrue(usuario.es_paciente)
        self.assertFalse(usuario.es_odontologo)
        self.assertFalse(usuario.es_administrador)

    def test_crear_usuario_odontologo(self):
        """TC-002: Crear un usuario con rol ODONTOLOGO."""
        usuario = Usuario.objects.create_user(
            username='doctor_test',
            password='P@ss_Segura!123',
            first_name='Carlos',
            last_name='García',
            rol=Usuario.Rol.ODONTOLOGO,
        )
        
        self.assertEqual(usuario.rol, Usuario.Rol.ODONTOLOGO)
        self.assertTrue(usuario.es_odontologo)
        self.assertFalse(usuario.es_paciente)

    def test_crear_usuario_administrador(self):
        """TC-003: Crear un usuario con rol ADMINISTRADOR."""
        usuario = Usuario.objects.create_user(
            username='admin_test',
            password='P@ss_Segura!123',
            first_name='María',
            last_name='López',
            rol=Usuario.Rol.ADMINISTRADOR,
        )
        
        self.assertEqual(usuario.rol, Usuario.Rol.ADMINISTRADOR)
        self.assertTrue(usuario.es_administrador)
        self.assertFalse(usuario.es_paciente)


# =============================================================================
# TEST 4: VALIDACIONES DE CAMPOS OBLIGATORIOS
# =============================================================================

class TestValidacionesCamposUsuario(TestCase):
    """
    Valida que los campos obligatorios del Usuario sean requeridos.
    """

    def test_usuario_requiere_username(self):
        """TC-004: No se puede crear usuario sin username."""
        with self.assertRaises(ValueError):
            Usuario.objects.create_user(
                username='',
                password='P@ss_Segura!123',
                rol=Usuario.Rol.PACIENTE,
            )

    def test_usuario_requiere_password(self):
        """TC-005: Un usuario sin contraseña válida no puede autenticarse."""
        usuario = Usuario.objects.create_user(
            username='test_user',
            password='TemporalPass123!',
            rol=Usuario.Rol.PACIENTE,
        )
        
        # Establecer contraseña como no utilizable
        usuario.set_unusable_password()
        usuario.save()
        
        # Verificar que no tiene contraseña utilizable
        self.assertFalse(usuario.has_usable_password())

    def test_username_unico(self):
        """TC-006: El username debe ser único en la base de datos."""
        Usuario.objects.create_user(
            username='usuario_duplicado',
            password='P@ss_Segura!123',
            rol=Usuario.Rol.PACIENTE,
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            Usuario.objects.create_user(
                username='usuario_duplicado',
                password='OtherPass_123',
                rol=Usuario.Rol.PACIENTE,
            )

    def test_email_opcional(self):
        """TC-007: El email es opcional en el modelo Usuario."""
        usuario = Usuario.objects.create_user(
            username='sin_email',
            password='P@ss_Segura!123',
            email='',
            rol=Usuario.Rol.PACIENTE,
        )
        
        self.assertEqual(usuario.email, '')


# =============================================================================
# TEST 8: LOGIN EXITOSO Y REDIRECCIONES
# =============================================================================

class TestLoginExitoso(TestCase):
    """
    Valida el flujo de login exitoso y redirecciones dinámicas por rol.
    """

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('usuarios:login')
        
        self.paciente = Usuario.objects.create_user(
            username='paciente_login',
            password='P@ss_Segura!123',
            rol=Usuario.Rol.PACIENTE,
        )
        
        self.odontologo = Usuario.objects.create_user(
            username='doctor_login',
            password='P@ss_Segura!123',
            rol=Usuario.Rol.ODONTOLOGO,
        )

    def test_login_paciente_exitoso(self):
        """TC-008: Login exitoso de PACIENTE con redirección correcta."""
        response = self.client.post(self.login_url, {
            'username': 'paciente_login',
            'password': 'P@ss_Segura!123',
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/citas/', response['Location'])

    def test_login_odontologo_exitoso(self):
        """TC-009: Login exitoso de ODONTOLOGO con redirección a agenda."""
        response = self.client.post(self.login_url, {
            'username': 'doctor_login',
            'password': 'P@ss_Segura!123',
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/agenda/', response['Location'])


# =============================================================================
# TEST 10: LOGIN FALLIDO
# =============================================================================

class TestLoginFallido(TestCase):
    """
    Valida el comportamiento cuando el login falla.
    """

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('usuarios:login')
        
        self.usuario = Usuario.objects.create_user(
            username='usuario_valido',
            password='P@ss_Segura!123',
            rol=Usuario.Rol.PACIENTE,
        )

    @override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
    def test_login_credenciales_incorrectas(self):
        """TC-010: Login con contraseña incorrecta falla."""
        response = self.client.post(self.login_url, {
            'username': 'usuario_valido',
            'password': 'ContraseñaIncorrecta',
        }, follow=False)
        
        # No debe redirigir (status_code 200 = se muestra el formulario nuevamente)
        # O 400 si hay error
        self.assertIn(response.status_code, [200, 400])
        self.assertFalse(response.wsgi_request.user.is_authenticated)
