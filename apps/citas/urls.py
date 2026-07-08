"""URLs del módulo de Citas."""

from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    # Paciente
    path('mis-citas/',                     views.MisCitasView.as_view(),          name='mis_citas'),
    path('reservar/',                      views.ReservarCitaView.as_view(),       name='reservar_cita'),
    path('<int:pk>/subir-comprobante/',    views.SubirComprobanteView.as_view(),   name='subir_comprobante'),

    # Administrador
    path('revision/',                      views.CitasPendientesReviewView.as_view(), name='citas_revision'),
    path('<int:pk>/aprobar/',              views.AprobarCitaView.as_view(),        name='aprobar_cita'),
]
