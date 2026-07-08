"""URLs del módulo de Agenda."""

from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('mi-cronograma/',          views.MiCronogramaView.as_view(),    name='mi_cronograma'),
    path('horario/nuevo/',          views.CrearHorarioView.as_view(),     name='crear_horario'),
    path('horario/<int:pk>/eliminar/', views.EliminarHorarioView.as_view(), name='eliminar_horario'),
    path('bloquear-dia/',           views.BloquearDiaView.as_view(),      name='bloquear_dia'),
]
