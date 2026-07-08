"""URLs del módulo de Fichas Clínicas."""

from django.urls import path
from . import views

app_name = 'fichas'

urlpatterns = [
    path('mi-ficha/',     views.MiFichaView.as_view(),       name='mi_ficha'),
    path('nueva/',        views.CrearFichaView.as_view(),     name='crear_ficha'),
    path('mis-fichas/',   views.FichasPacienteView.as_view(), name='mis_fichas_doctor'),
]
