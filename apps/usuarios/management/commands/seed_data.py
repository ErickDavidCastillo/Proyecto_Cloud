from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario
from apps.agenda.models import HorarioTrabajo
from datetime import time


class Command(BaseCommand):
    help = 'Semilla de datos iniciales para desarrollo local (Admin, Odontologo y Paciente)'

    def handle(self, *args, **options):
        self.stdout.write('=== Iniciando Sembrado de Usuarios ===')

        # 1. Crear Administrador
        admin, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'DentalCare',
                'email': 'admin@dentalcare.com',
                'rol': Usuario.Rol.ADMINISTRADOR,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('clave_admin_123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('[OK] Creado Administrador: admin / clave_admin_123'))
        else:
            self.stdout.write('[INFO] Administrador ya existe.')

        # 2. Crear Odontólogo
        dentista, created = Usuario.objects.get_or_create(
            username='odontologo',
            defaults={
                'first_name': 'Carlos',
                'last_name': 'Mendoza',
                'email': 'carlos@dentalcare.com',
                'rol': Usuario.Rol.ODONTOLOGO
            }
        )
        if created:
            dentista.set_password('clave_odontologo_123')
            dentista.save()
            self.stdout.write(self.style.SUCCESS('[OK] Creado Odontologo: odontologo / clave_odontologo_123'))

            # Crear un par de horarios de prueba para el odontólogo
            HorarioTrabajo.objects.get_or_create(
                doctor=dentista,
                dia_semana=0,  # Lunes
                hora_inicio=time(9, 0),
                hora_fin=time(13, 0)
            )
            HorarioTrabajo.objects.get_or_create(
                doctor=dentista,
                dia_semana=2,  # Miércoles
                hora_inicio=time(14, 0),
                hora_fin=time(18, 0)
            )
            self.stdout.write(self.style.SUCCESS('     Horarios semanales agregados al Odontologo.'))
        else:
            self.stdout.write('[INFO] Odontologo ya existe.')

        # 3. Crear Paciente
        paciente, created = Usuario.objects.get_or_create(
            username='paciente',
            defaults={
                'first_name': 'Pedro',
                'last_name': 'Perez',
                'email': 'pedro@gmail.com',
                'rol': Usuario.Rol.PACIENTE
            }
        )
        if created:
            paciente.set_password('clave_paciente_123')
            paciente.save()
            self.stdout.write(self.style.SUCCESS('[OK] Creado Paciente: paciente / clave_paciente_123'))
        else:
            self.stdout.write('[INFO] Paciente ya existe.')

        self.stdout.write(self.style.SUCCESS('=== Sembrado finalizado correctamente ==='))
