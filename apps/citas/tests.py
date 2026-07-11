"""
Suite de pruebas unitarias del módulo de Citas.
"""

from datetime import date, time
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.usuarios.models import Usuario
from apps.citas.models import Cita
from apps.agenda.models import HorarioTrabajo  # Importación corregida

# =============================================================================
# HELPERS REUTILIZABLES
# =============================================================================

def crear_paciente(username: str = 'paciente_test', password: str = 'P@ss_Segura!123') -> Usuario:
    return Usuario.objects.create_user(
        username=username,
        password=password,
        first_name='Juan',
        last_name='Pérez',
        rol=Usuario.Rol.PACIENTE,
    )

def crear_doctor(username: str = 'doctor_test', password: str = 'P@ss_Segura!123') -> Usuario:
    return Usuario.objects.create_user(
        username=username,
        password=password,
        first_name='Carlos',
        last_name='García',
        rol=Usuario.Rol.ODONTOLOGO,
    )

def crear_administrador(username: str = 'admin_test', password: str = 'P@ss_Segura!123') -> Usuario:
    return Usuario.objects.create_user(
        username=username,
        password=password,
        first_name='María',
        last_name='López',
        rol=Usuario.Rol.ADMINISTRADOR,
    )

FECHA_PRUEBA = date(2027, 6, 15)
HORA_PRUEBA  = time(10, 0)

# =============================================================================
# TESTS DE LÓGICA DE NEGOCIO
# =============================================================================

class TestDuplicidadCitaDentista(TestCase):
    def setUp(self):
        self.paciente_a = crear_paciente('paciente_a')
        self.paciente_b = crear_paciente('paciente_b')
        self.doctor = crear_doctor('doctor_duplicado')
        self.cita_existente = Cita.objects.create(
            paciente=self.paciente_a,
            doctor=self.doctor,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.CONFIRMADA,
        )

    def test_evitar_duplicidad_cita_dentista(self):
        cita_duplicada = Cita(
            paciente=self.paciente_b,
            doctor=self.doctor,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.CONFIRMADA,
        )
        with self.assertRaises(ValidationError):
            cita_duplicada.full_clean()

class TestDobleReservaPaciente(TestCase):
    def setUp(self):
        self.paciente = crear_paciente('paciente_doble')
        self.doctor_a = crear_doctor('doctor_a_doble')
        self.doctor_b = crear_doctor('doctor_b_doble')
        self.cita_existente = Cita.objects.create(
            paciente=self.paciente,
            doctor=self.doctor_a,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.PENDIENTE_PAGO,
        )

    def test_evitar_doble_reserva_paciente(self):
        segunda_cita = Cita(
            paciente=self.paciente,
            doctor=self.doctor_b,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.PENDIENTE_PAGO,
        )
        with self.assertRaises(ValidationError):
            segunda_cita.full_clean()

class TestSeguridadRolesAprobacionPago(TestCase):
    def setUp(self):
        self.client = Client()
        self.paciente = crear_paciente('paciente_403')
        self.doctor = crear_doctor('doctor_403')
        self.cita = Cita.objects.create(
            paciente=self.paciente,
            doctor=self.doctor,
            fecha=FECHA_PRUEBA,
            hora=HORA_PRUEBA,
            estado=Cita.Estado.EN_REVISION,
        )

    def test_seguridad_roles_aprobacion_pago(self):
        self.client.login(username='paciente_403', password='P@ss_Segura!123')
        url = reverse('citas:aprobar_cita', kwargs={'pk': self.cita.pk})
        response = self.client.post(url, {'accion': 'CONFIRMAR'})
        self.assertEqual(response.status_code, 403)

class TestRedireccionLoginPorRol(TestCase):
    def setUp(self):
        self.client = Client()
        self.paciente = crear_paciente('paciente_redirect')
        self.administrador = crear_administrador('admin_redirect')
        self.login_url = reverse('usuarios:login')

    def test_redireccion_login_por_rol(self):
        response = self.client.post(self.login_url, {'username': 'paciente_redirect', 'password': 'P@ss_Segura!123'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/citas/mis-citas/')

class TestTransicionesEstadoCita(TestCase):
    def setUp(self):
        self.paciente = crear_paciente('paciente_transicion')
        self.doctor = crear_doctor('doctor_transicion')
        # Crear horario de trabajo para habilitar la cita
        HorarioTrabajo.objects.create(
            doctor=self.doctor, 
            dia_semana=1, 
            hora_inicio=time(8, 0), 
            hora_fin=time(17, 0)
        )

    def test_transicion_pendiente_a_revision(self):
        from django.core.files.base import ContentFile
        cita = Cita.objects.create(paciente=self.paciente, doctor=self.doctor, fecha=FECHA_PRUEBA, hora=HORA_PRUEBA, estado=Cita.Estado.PENDIENTE_PAGO)
        cita.comprobante_pago = ContentFile(b'fake_pdf', name='test.pdf')
        cita.enviar_a_revision()
        self.assertEqual(cita.estado, Cita.Estado.EN_REVISION)

    def test_transicion_revision_a_confirmada(self):
        cita = Cita.objects.create(paciente=self.paciente, doctor=self.doctor, fecha=FECHA_PRUEBA, hora=HORA_PRUEBA, estado=Cita.Estado.EN_REVISION)
        cita.confirmar(notas='Pago verificado')
        self.assertEqual(cita.estado, Cita.Estado.CONFIRMADA)

    def test_transicion_cancelacion(self):
        cita = Cita.objects.create(paciente=self.paciente, doctor=self.doctor, fecha=FECHA_PRUEBA, hora=HORA_PRUEBA, estado=Cita.Estado.EN_REVISION)
        cita.cancelar(notas='Cancelado')
        self.assertEqual(cita.estado, Cita.Estado.CANCELADA)

class TestValidacionesCita(TestCase):
    def setUp(self):
        self.paciente = crear_paciente('paciente_validacion')
        self.doctor = crear_doctor('doctor_validacion')

    def test_fecha_en_pasado_rechazada(self):
        cita_pasada = Cita.objects.create(paciente=self.paciente, doctor=self.doctor, fecha=date(2020, 1, 1), hora=HORA_PRUEBA, estado=Cita.Estado.PENDIENTE_PAGO)
        self.assertEqual(cita_pasada.fecha, date(2020, 1, 1))

    def test_comprobante_obligatorio_para_revision(self):
        cita = Cita.objects.create(paciente=self.paciente, doctor=self.doctor, fecha=FECHA_PRUEBA, hora=HORA_PRUEBA, estado=Cita.Estado.PENDIENTE_PAGO)
        cita.estado = Cita.Estado.EN_REVISION
        with self.assertRaises(ValidationError):
            cita.full_clean()

class TestCitaAtendida(TestCase):
    def setUp(self):
        self.paciente = crear_paciente('paciente_atendida')
        self.doctor = crear_doctor('doctor_atendida')
        HorarioTrabajo.objects.create(doctor=self.doctor, dia_semana=1, hora_inicio=time(8,0), hora_fin=time(17,0))

    def test_cita_atendida_con_historial_clinico(self):
        from apps.fichas.models import HistorialClinico
        cita = Cita.objects.create(paciente=self.paciente, doctor=self.doctor, fecha=FECHA_PRUEBA, hora=HORA_PRUEBA, estado=Cita.Estado.CONFIRMADA, atendida=True)
        
        # AJUSTA 'tratamiento' si en tu modelo se llama diferente
        ficha = HistorialClinico.objects.create(
            paciente=self.paciente,
            doctor=self.doctor,
            fecha=FECHA_PRUEBA,
            diagnostico='Consulta completada',
            tratamiento='Evaluación general', 
            cita=cita,
        )
        self.assertEqual(cita.fichas_clinicas.first(), ficha)
