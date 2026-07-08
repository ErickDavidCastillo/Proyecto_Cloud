"""
Suite de pruebas unitarias del módulo de Citas.

Cubre los 4 tests de reglas de negocio obligatorios para el pipeline CI/CD:

1. test_evitar_duplicidad_cita_dentista
2. test_evitar_doble_reserva_paciente
3. test_seguridad_roles_aprobacion_pago
4. test_redireccion_login_por_rol
"""

from datetime import date, time

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.usuarios.models import Usuario
from apps.citas.models import Cita


# =============================================================================
# HELPERS REUTILIZABLES
# =============================================================================

def crear_paciente(username: str = 'paciente_test', password: str = 'P@ss_Segura!123') -> Usuario:
    """Crea un usuario con rol PACIENTE para pruebas."""
    return Usuario.objects.create_user(
        username=username,
        password=password,
        first_name='Juan',
        last_name='Pérez',
        rol=Usuario.Rol.PACIENTE,
    )


def crear_doctor(username: str = 'doctor_test', password: str = 'P@ss_Segura!123') -> Usuario:
    """Crea un usuario con rol ODONTOLOGO para pruebas."""
    return Usuario.objects.create_user(
        username=username,
        password=password,
        first_name='Carlos',
        last_name='García',
        rol=Usuario.Rol.ODONTOLOGO,
    )


def crear_administrador(username: str = 'admin_test', password: str = 'P@ss_Segura!123') -> Usuario:
    """Crea un usuario con rol ADMINISTRADOR para pruebas."""
    return Usuario.objects.create_user(
        username=username,
        password=password,
        first_name='María',
        last_name='López',
        rol=Usuario.Rol.ADMINISTRADOR,
    )


FECHA_PRUEBA = date(2027, 6, 15)   # Fecha futura fija para pruebas
HORA_PRUEBA  = time(10, 0)          # 10:00 AM


# =============================================================================
# TEST 1: EVITAR DUPLICIDAD DE CITA PARA EL DENTISTA
# =============================================================================

class TestDuplicidadCitaDentista(TestCase):
    """
    Valida que el sistema rechace la creación de una segunda cita CONFIRMADA
    para el mismo doctor en el mismo slot de fecha/hora.
    """

    def setUp(self):
        self.paciente_a = crear_paciente('paciente_a')
        self.paciente_b = crear_paciente('paciente_b')
        self.doctor     = crear_doctor('doctor_duplicado')

        # Crear y confirmar la primera cita
        self.cita_existente = Cita(
            paciente=self.paciente_a,
            doctor=self.doctor,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.CONFIRMADA,
        )
        # Guardamos directamente sin full_clean para simular cita ya existente
        self.cita_existente.save()

    def test_evitar_duplicidad_cita_dentista(self):
        """
        TC-001: Una segunda cita CONFIRMADA para el mismo doctor
        en el mismo slot debe lanzar ValidationError.
        """
        cita_duplicada = Cita(
            paciente=self.paciente_b,
            doctor=self.doctor,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.CONFIRMADA,
        )

        with self.assertRaises(ValidationError) as ctx:
            cita_duplicada.full_clean()

        # Verificar que el error apunta al campo correcto
        self.assertIn('hora', ctx.exception.message_dict)


# =============================================================================
# TEST 2: EVITAR DOBLE RESERVA DEL MISMO PACIENTE
# =============================================================================

class TestDobleReservaPaciente(TestCase):
    """
    Valida que un paciente no pueda tener dos citas activas en el mismo
    slot horario, aunque sean con doctores distintos.
    """

    def setUp(self):
        self.paciente = crear_paciente('paciente_doble')
        self.doctor_a = crear_doctor('doctor_a_doble')
        self.doctor_b = crear_doctor('doctor_b_doble')

        # Primera cita (activa)
        self.cita_existente = Cita(
            paciente=self.paciente,
            doctor=self.doctor_a,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.PENDIENTE_PAGO,
        )
        self.cita_existente.save()

    def test_evitar_doble_reserva_paciente(self):
        """
        TC-002: El mismo paciente NO puede reservar dos citas
        en el mismo slot con doctores distintos.
        """
        segunda_cita = Cita(
            paciente=self.paciente,
            doctor=self.doctor_b,   # Doctor diferente
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.PENDIENTE_PAGO,
        )

        with self.assertRaises(ValidationError) as ctx:
            segunda_cita.full_clean()

        self.assertIn('hora', ctx.exception.message_dict)


# =============================================================================
# TEST 3: SEGURIDAD RBAC - ACCESO 403 PARA PACIENTES EN VISTAS ADMIN
# =============================================================================

class TestSeguridadRolesAprobacionPago(TestCase):
    """
    Valida que un usuario con rol PACIENTE reciba HTTP 403 Forbidden
    al intentar acceder a la vista de aprobación de pagos (exclusiva del Admin).
    """

    def setUp(self):
        self.client    = Client()
        self.paciente  = crear_paciente('paciente_403')
        self.doctor    = crear_doctor('doctor_403')
        self.admin     = crear_administrador('admin_403')

        # Crear una cita en EN_REVISION para tener un pk válido
        self.cita = Cita.objects.create(
            paciente=self.paciente,
            doctor=self.doctor,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.EN_REVISION,
        )

    def test_seguridad_roles_aprobacion_pago(self):
        """
        TC-003: Un usuario PACIENTE que intenta hacer POST a la URL de
        aprobación del administrador debe recibir HTTP 403 Forbidden.
        """
        # Autenticar como PACIENTE
        self.client.login(username='paciente_403', password='P@ss_Segura!123')

        # Intentar acceder a la vista de aprobación de pagos (solo ADMINISTRADOR)
        url = reverse('citas:aprobar_cita', kwargs={'pk': self.cita.pk})
        response = self.client.post(url, {'accion': 'CONFIRMAR'})

        self.assertEqual(
            response.status_code, 403,
            msg=(
                f'Se esperaba HTTP 403 Forbidden para un PACIENTE en la vista de '
                f'aprobación, pero se obtuvo HTTP {response.status_code}.'
            )
        )


# =============================================================================
# TEST 4: REDIRECCIÓN DINÁMICA POR ROL TRAS EL LOGIN
# =============================================================================

class TestRedireccionLoginPorRol(TestCase):
    """
    Valida que el LoginView redirija correctamente según el rol del usuario:
    - PACIENTE       → /citas/mis-citas/
    - ADMINISTRADOR  → /dashboard/admin/
    """

    def setUp(self):
        self.client       = Client()
        self.paciente     = crear_paciente('paciente_redirect')
        self.administrador = crear_administrador('admin_redirect')
        self.login_url    = reverse('usuarios:login')

    def test_redireccion_login_por_rol(self):
        """
        TC-004a: Login de PACIENTE debe responder HTTP 302
        y redirigir a /citas/mis-citas/
        """
        response = self.client.post(self.login_url, {
            'username': 'paciente_redirect',
            'password': 'P@ss_Segura!123',
        })

        self.assertEqual(
            response.status_code, 302,
            msg=f'Se esperaba HTTP 302 tras login de PACIENTE, se obtuvo {response.status_code}.'
        )
        self.assertEqual(
            response['Location'], '/citas/mis-citas/',
            msg=(
                f'Redirección incorrecta para PACIENTE. '
                f'Esperado: /citas/mis-citas/ | Obtenido: {response["Location"]}'
            )
        )

    def test_redireccion_login_administrador(self):
        """
        TC-004b: Login de ADMINISTRADOR debe responder HTTP 302
        y redirigir a /dashboard/admin/
        """
        response = self.client.post(self.login_url, {
            'username': 'admin_redirect',
            'password': 'P@ss_Segura!123',
        })

        self.assertEqual(
            response.status_code, 302,
            msg=f'Se esperaba HTTP 302 tras login de ADMINISTRADOR, se obtuvo {response.status_code}.'
        )
        self.assertEqual(
            response['Location'], '/dashboard/admin/',
            msg=(
                f'Redirección incorrecta para ADMINISTRADOR. '
                f'Esperado: /dashboard/admin/ | Obtenido: {response["Location"]}'
            )
        )
